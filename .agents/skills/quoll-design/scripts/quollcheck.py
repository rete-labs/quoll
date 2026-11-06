"""Temporary structured checks for Quoll v0.4 packages.

This module deliberately stops at source discovery, structured validation, and
portable content hashing.  Reference resolution and semantic checks build on
these data classes elsewhere.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import re
import stat
import tomllib
from typing import Iterable, Iterator


@dataclass(frozen=True, order=True)
class Finding:
    """One diagnostic; its ordering and equality intentionally ignore line."""

    rule: str
    severity: str
    path: str
    subject: str
    detail: str
    line: int = field(default=0, compare=False)

    def __post_init__(self) -> None:
        if self.severity not in {"error", "review"}:
            raise ValueError("finding severity must be 'error' or 'review'")

    @property
    def key(self) -> tuple[str, str, str, str, str]:
        return (self.rule, self.severity, self.path, self.subject, self.detail)

    @property
    def sort_key(self) -> tuple[str, str, str, str, str]:
        return self.key

    def __str__(self) -> str:
        location = self.path or "<package>"
        if self.line:
            location += f":{self.line}"
        subject = f" {self.subject}" if self.subject else ""
        return f"{location}: {self.severity} {self.rule}{subject}: {self.detail}"


@dataclass
class Item:
    name: str
    statements: str = ""
    direction: str | None = None
    impl: str | None = None
    line: int = 0
    end_line: int = 0
    view: str = ""

    @property
    def statement(self) -> str:
        return self.statements

    @property
    def implements(self) -> str | None:
        return self.impl


@dataclass
class Decision:
    id: str
    title: str = ""
    fields: dict[str, str] = field(default_factory=dict)
    line: int = 0
    end_line: int = 0
    active: bool = True
    successor: str | None = None
    text: str = ""

    @property
    def superseded_by(self) -> str | None:
        return self.successor


@dataclass
class SourceFile:
    path: str
    kind: str
    text: str = ""
    module: str = ""
    front: dict = field(default_factory=dict)
    items: list[Item] = field(default_factory=list)
    decisions: list[Decision] = field(default_factory=list)
    content: str = ""

    @property
    def references(self) -> list[str]:
        return extract_refs(self.content or self.text)


@dataclass
class Module:
    path: str
    name: str
    files: list[SourceFile] = field(default_factory=list)

    def _first(self, *kinds: str) -> SourceFile | None:
        return next((source for source in self.files if source.kind in kinds), None)

    @property
    def header(self) -> SourceFile | None:
        return self._first("header")

    @property
    def private_header(self) -> SourceFile | None:
        return self._first("private header")

    @property
    def body(self) -> SourceFile | None:
        return self._first("body")

    @property
    def decisions(self) -> SourceFile | None:
        return self._first("decisions")

    @property
    def sources(self) -> list[SourceFile]:
        return self.files


@dataclass(frozen=True)
class Selector:
    raw: str
    id: str
    version: str
    kind: str
    major: int
    minor: int | None = None
    patch: int | None = None
    prerelease: tuple[str, ...] = ()
    build: tuple[str, ...] = ()
    timestamp: str | None = None
    revision: str | None = None

    @property
    def unversioned_id(self) -> str:
        return self.id

    @property
    def exact(self) -> bool:
        return self.kind != "partial"

    @property
    def partial(self) -> bool:
        return self.kind == "partial"

    @property
    def development(self) -> bool:
        return self.kind == "development"

    @property
    def release(self) -> bool:
        return self.kind in {"stable", "prerelease"}

    @property
    def series(self) -> tuple[str, int]:
        return (self.id, self.major)

    def __str__(self) -> str:
        return self.raw


@dataclass
class Package:
    root: Path
    name: str
    id: str = ""
    edition: str = ""
    description: str = ""
    dependencies: list[Selector] = field(default_factory=list)
    modules: list[Module] = field(default_factory=list)
    manifest: dict | None = None
    membership: dict | None = None
    lock: dict | None = None
    findings: list[Finding] = field(default_factory=list)
    _parse_findings: list[Finding] = field(default_factory=list, repr=False)

    @property
    def files(self) -> list[SourceFile]:
        return [source for module in self.modules for source in module.files]

    @property
    def module_map(self) -> dict[str, Module]:
        return {module.path: module for module in self.modules}


@dataclass(frozen=True)
class FileRecord:
    path: str
    data: bytes
    mode: int = 0o100644
    kind: str = "file"

    @property
    def raw(self) -> bytes:
        return self.data

    @property
    def content(self) -> bytes:
        return self.data


@dataclass(frozen=True)
class Locator:
    raw: str
    repository: str
    package_path: str
    request: str


_NUMBER = r"0|[1-9][0-9]*"
_SEMVER_RE = re.compile(
    rf"^v(?P<major>{_NUMBER})\.(?P<minor>{_NUMBER})\.(?P<patch>{_NUMBER})"
    r"(?:-(?P<pre>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+(?P<build>[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
_PARTIAL_RE = re.compile(rf"^v(?P<major>{_NUMBER})(?:\.(?P<minor>{_NUMBER}))?$")
_NO_BASE_RE = re.compile(
    rf"^v0\.0\.0-(?P<timestamp>[0-9]{{14}})-(?P<revision>[0-9a-f]{{12}})$"
)
_PRERELEASE_BASE_RE = re.compile(
    rf"^v(?P<major>{_NUMBER})\.(?P<minor>{_NUMBER})\.(?P<patch>{_NUMBER})"
    r"-pre\.0\.(?P<timestamp>[0-9]{14})-(?P<revision>[0-9a-f]{12})$"
)
_RELEASE_BASE_RE = re.compile(
    rf"^v(?P<major>{_NUMBER})\.(?P<minor>{_NUMBER})\.(?P<patch>{_NUMBER})"
    r"-0\.(?P<timestamp>[0-9]{14})-(?P<revision>[0-9a-f]{12})$"
)
_PACKAGE_NAME_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


def _validate_package_id(value: str) -> str:
    if not isinstance(value, str) or not value.startswith("pkg:quoll/"):
        raise ValueError("package ID must be an unversioned pkg:quoll PURL")
    if any(character in value for character in "@?#\\"):
        raise ValueError("package ID contains an invalid PURL character")
    segments = value[len("pkg:quoll/") :].split("/")
    if len(segments) < 2 or any(not segment for segment in segments):
        raise ValueError("package ID needs a trust domain and a package name")
    if any(segment in {".", ".."} for segment in segments):
        raise ValueError("package ID contains a noncanonical path segment")
    if not _PACKAGE_NAME_RE.fullmatch(segments[-1]):
        raise ValueError("package name must be lowercase and PURL-compatible")
    return value


def _valid_prerelease(parts: tuple[str, ...]) -> bool:
    return all(
        not part.isdigit() or part == "0" or not part.startswith("0")
        for part in parts
    )


def _development_selector(
    raw: str, package_id: str, version: str, match: re.Match[str]
) -> Selector:
    timestamp = match.group("timestamp")
    try:
        datetime.strptime(timestamp, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
    except ValueError as error:
        raise ValueError("development selector has an invalid UTC timestamp") from error
    groups = match.groupdict()
    major = int(groups.get("major") or 0)
    minor = int(groups["minor"]) if groups.get("minor") is not None else 0
    patch = int(groups["patch"]) if groups.get("patch") is not None else 0
    return Selector(
        raw=raw,
        id=package_id,
        version=version,
        kind="development",
        major=major,
        minor=minor,
        patch=patch,
        prerelease=tuple(version.split("-", 1)[1].split(".")),
        timestamp=timestamp,
        revision=match.group("revision"),
    )


def parse_selector(value: str) -> Selector:
    """Parse an exact, development, or partial Quoll package selector."""

    if not isinstance(value, str) or "@" not in value:
        raise ValueError("selector must contain a package ID and @version")
    package_id, version = value.rsplit("@", 1)
    _validate_package_id(package_id)

    for pattern in (_NO_BASE_RE, _PRERELEASE_BASE_RE, _RELEASE_BASE_RE):
        match = pattern.fullmatch(version)
        if match:
            return _development_selector(value, package_id, version, match)

    # Any member of a pseudo-version family must not fall back to an ordinary
    # prerelease when its timestamp or revision has the wrong shape or length.
    core = rf"v(?:{_NUMBER})\.(?:{_NUMBER})\.(?:{_NUMBER})"
    pseudo_shaped = (
        re.match(r"^v0\.0\.0-[^-]*-", version)
        or re.match(rf"^{core}-pre\.0\.[^-]*-", version)
        or re.match(rf"^{core}-0\.[^-]*-", version)
    )
    if pseudo_shaped:
        raise ValueError("malformed canonical development pseudo-version")

    partial = _PARTIAL_RE.fullmatch(version)
    if partial:
        minor = partial.group("minor")
        return Selector(
            raw=value,
            id=package_id,
            version=version,
            kind="partial",
            major=int(partial.group("major")),
            minor=int(minor) if minor is not None else None,
        )

    exact = _SEMVER_RE.fullmatch(version)
    if not exact:
        raise ValueError("selector version is not an exact or partial semantic version")
    prerelease = tuple((exact.group("pre") or "").split(".")) if exact.group("pre") else ()
    if not _valid_prerelease(prerelease):
        raise ValueError("numeric prerelease identifiers must not have leading zeroes")
    return Selector(
        raw=value,
        id=package_id,
        version=version,
        kind="prerelease" if prerelease else "stable",
        major=int(exact.group("major")),
        minor=int(exact.group("minor")),
        patch=int(exact.group("patch")),
        prerelease=prerelease,
        build=tuple((exact.group("build") or "").split(".")) if exact.group("build") else (),
    )


def _toml_line(error: tomllib.TOMLDecodeError) -> int:
    match = re.search(r"\bat line ([0-9]+)", str(error))
    return int(match.group(1)) if match else 0


def _read_toml(package: Package, filename: str) -> dict | None:
    path = package.root / filename
    try:
        with path.open("rb") as stream:
            return tomllib.load(stream)
    except FileNotFoundError:
        return None
    except (OSError, UnicodeDecodeError) as error:
        package._parse_findings.append(
            Finding("toml.read", "error", filename, filename, str(error))
        )
    except tomllib.TOMLDecodeError as error:
        package._parse_findings.append(
            Finding("toml.syntax", "error", filename, filename, str(error), _toml_line(error))
        )
    return None


def _classify_file(path: str) -> str | None:
    name = path.rsplit("/", 1)[-1]
    top = "/" not in path
    if top and name == "package.quoll.toml":
        return "manifest"
    if top and name == "modules.quoll.toml":
        return "modules"
    if top and name == "package.lock.quoll.toml":
        return "lock"
    if top and name == "build.md":
        return "build"
    if name.endswith(".private.h.md"):
        return "private header"
    if name.endswith(".h.md"):
        return "header"
    if name.endswith(".body.md"):
        return "body"
    if name.endswith(".decisions.md"):
        return "decisions"
    return None


def _valid_module_path(path: str) -> bool:
    if not isinstance(path, str) or not path or path.startswith("/") or "\\" in path:
        return False
    return all(segment not in {"", ".", ".."} for segment in path.split("/"))


def _source_text(package: Package, path: str) -> str:
    try:
        return (package.root / path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        package._parse_findings.append(
            Finding("source.read", "error", path, path, str(error))
        )
        return ""


def _parse_front(
    package: Package, source: SourceFile, lines: list[str]
) -> list[str]:
    if source.kind not in {"header", "private header", "body"}:
        return lines
    if not lines or lines[0].rstrip("\r\n") != "+++":
        return lines
    closing = next(
        (index for index in range(1, len(lines)) if lines[index].rstrip("\r\n") == "+++"),
        None,
    )
    if closing is None:
        package._parse_findings.append(
            Finding("front.unclosed", "error", source.path, source.path, "front matter has no closing +++", 1)
        )
        return lines
    text = "".join(lines[1:closing])
    try:
        source.front = tomllib.loads(text)
    except tomllib.TOMLDecodeError as error:
        package._parse_findings.append(
            Finding("front.toml", "error", source.path, source.path, str(error), 1 + _toml_line(error))
        )
        source.front = {}
        return lines
    return ["\n"] * (closing + 1) + lines[closing + 1 :]


def _validate_front(package: Package, source: SourceFile) -> None:
    if not source.front:
        return
    allowed = {"aliases"}
    if source.kind == "body":
        allowed.add("implements")
    else:
        allowed.update({"includes", "module lead"})
    for key, value in source.front.items():
        if key not in allowed:
            package._parse_findings.append(
                Finding("front.keys", "error", source.path, key, "key is not allowed in this file kind")
            )
        elif key in {"implements", "includes"} and (
            not isinstance(value, list) or any(not isinstance(name, str) or not name for name in value)
        ):
            package._parse_findings.append(
                Finding("front.type", "error", source.path, key, "value must be a list of names")
            )
        elif key == "module lead" and value is not True:
            package._parse_findings.append(
                Finding("front.type", "error", source.path, key, "value must be true")
            )
        elif key == "aliases":
            if not isinstance(value, dict) or any(
                not isinstance(alias, str) or not isinstance(target, str) or not target
                for alias, target in value.items()
            ):
                package._parse_findings.append(
                    Finding("front.type", "error", source.path, key, "value must be a string table")
                )
            else:
                for alias, target in value.items():
                    if target.startswith("pkg:"):
                        try:
                            if "@" in target:
                                parse_selector(target.split("#", 1)[0])
                            else:
                                _validate_package_id(target.split("#", 1)[0])
                        except ValueError as error:
                            package._parse_findings.append(
                                Finding("front.alias", "error", source.path, alias, str(error))
                            )


def _opener(content: str) -> tuple[str | None, str | None] | None:
    match = re.fullmatch(r"(ensures|requires|open):?", content.strip())
    if match:
        return match.group(1), None
    match = re.fullmatch(r"impl\s+\[([^\]]+)\]:?", content.strip())
    if match:
        return None, match.group(1)
    return None


def _item_start(content: str) -> tuple[str, str]:
    parts = re.split(r"[ ]{2,}", content.strip(), maxsplit=1)
    if len(parts) == 1:
        return parts[0], ""
    return parts[0].strip(), parts[1].strip()


def _parse_view(lines: list[str], start: int, end: int) -> list[Item]:
    candidates = [
        (index, len(lines[index]) - len(lines[index].lstrip(" ")))
        for index in range(start, end)
        if lines[index].strip() and not lines[index].lstrip(" ").startswith("\t")
    ]
    if not candidates:
        return []
    base = min(indent for _, indent in candidates)
    items: list[Item] = []
    current: Item | None = None
    item_indent = base
    grouped = False
    pending_group = False
    direction: str | None = None
    impl: str | None = None

    for index in range(start, end):
        raw = lines[index]
        if not raw.strip() or raw.lstrip(" ").startswith("\t"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        content = raw[indent:].strip()
        opening = _opener(content)

        if indent == base and opening:
            new_direction, new_impl = opening
            if not grouped or not pending_group:
                direction, impl = None, None
            if new_direction is not None:
                direction = new_direction
            if new_impl is not None:
                impl = new_impl
            grouped = True
            pending_group = True
            current = None
            continue

        if grouped and indent == base:
            grouped = False
            pending_group = False
            direction = None
            impl = None
            item_indent = base
            current = None

        if pending_group:
            if indent <= base:
                continue
            item_indent = indent
            pending_group = False

        if indent == item_indent:
            name, statement = _item_start(content)
            current = Item(
                name=name,
                statements=statement,
                direction=direction,
                impl=impl,
                line=index + 1,
                end_line=index + 1,
            )
            items.append(current)
        elif current is not None and indent > item_indent:
            current.statements = " ".join(
                part for part in (current.statements, content) if part
            )
            current.end_line = index + 1
    return items


def _fence_marker(line: str) -> str | None:
    match = re.match(r"^\s*(`{3,}|~{3,})", line)
    return match.group(1) if match else None


def _is_fence_close(line: str, marker: str) -> bool:
    return bool(
        re.fullmatch(rf"\s*{re.escape(marker[0])}{{{len(marker)},}}\s*", line)
    )


def _parse_views(source: SourceFile, lines: list[str]) -> None:
    for piece in ("Structure", "Flow", "Rules"):
        heading = next(
            (index for index, line in enumerate(lines) if re.match(rf"^##\s+{piece}\s*$", line)),
            None,
        )
        if heading is None:
            continue
        section_end = next(
            (
                index
                for index in range(heading + 1, len(lines))
                if re.match(r"^#{1,2}\s+", lines[index])
            ),
            len(lines),
        )
        opening = next(
            (
                (index, marker)
                for index in range(heading + 1, section_end)
                if (marker := _fence_marker(lines[index])) is not None
            ),
            None,
        )
        if opening is None:
            continue
        opening_index, marker = opening
        closing = next(
            (
                index
                for index in range(opening_index + 1, section_end)
                if _is_fence_close(lines[index], marker)
            ),
            section_end,
        )
        source.items.extend(
            Item(
                name=item.name,
                statements=item.statements,
                direction=item.direction,
                impl=item.impl,
                line=item.line,
                end_line=item.end_line,
                view=piece,
            )
            for item in _parse_view(lines, opening_index + 1, closing)
        )


def _parse_decisions(source: SourceFile, lines: list[str]) -> None:
    current: Decision | None = None
    last_field: str | None = None
    for index, line in enumerate(lines):
        entry = re.match(r"^\s*\*\*([^\s*.]+)\.\s+(.+?)\*\*\s*$", line)
        if entry:
            current = Decision(
                id=entry.group(1),
                title=entry.group(2).strip(),
                line=index + 1,
                end_line=index + 1,
            )
            source.decisions.append(current)
            last_field = None
            continue
        if current is None:
            continue
        if not line.strip():
            current = None
            last_field = None
            continue
        current.end_line = index + 1
        field_match = re.match(r"^\s*\*([^*\n]+)\*[ \t]+(.*?)\s*$", line)
        if field_match:
            key = field_match.group(1).strip()
            value = field_match.group(2).strip()
            current.fields[key] = value
            last_field = key
        elif last_field:
            current.fields[last_field] += " " + line.strip()
        if current.fields:
            superseded = next(
                (value for key, value in current.fields.items() if key.lower() == "superseded by"),
                None,
            )
            if superseded is not None:
                current.active = False
                reference = re.search(r"\[([^\]]+)\]", superseded)
                current.successor = (reference.group(1) if reference else superseded.split()[0]).strip("`*_ .")
    for decision in source.decisions:
        decision.text = "".join(lines[decision.line - 1 : decision.end_line])


def _parse_source(package: Package, source: SourceFile) -> None:
    lines = source.text.splitlines(keepends=True)
    lines = _parse_front(package, source, lines)
    _validate_front(package, source)
    source.content = "".join(lines)
    if source.kind == "decisions":
        _parse_decisions(source, lines)
    elif source.kind in {"header", "private header", "body", "build"}:
        _parse_views(source, lines)


def _add_module(package: Package, path: str, name: str) -> Module:
    module = Module(path=path, name=name)
    directory = package.root / path if path else package.root
    try:
        entries = sorted(directory.iterdir(), key=lambda entry: entry.name)
    except OSError as error:
        package._parse_findings.append(
            Finding("module.read", "error", path, path or ".", str(error))
        )
        entries = []
    for entry in entries:
        if entry.name.startswith(".") or not entry.is_file():
            continue
        relative = f"{path}/{entry.name}" if path else entry.name
        kind = _classify_file(relative)
        if kind is None:
            continue
        source = SourceFile(
            path=relative,
            kind=kind,
            text=_source_text(package, relative),
            module=path,
        )
        module.files.append(source)
        _parse_source(package, source)
    package.modules.append(module)
    return module


def _discover_modules(package: Package, member_paths: list[str]) -> None:
    _add_module(package, "", package.name)
    for path in member_paths:
        if path == "":
            continue
        _add_module(package, path, path.rsplit("/", 1)[-1])

    # Source outside a listed module is still parsed and checked: placing it in
    # a synthetic module keeps a bad reference from disappearing with the
    # placement error itself.
    loaded = {source.path for source in package.files}
    unlisted: dict[str, list[str]] = {}
    for directory, dirnames, filenames in os.walk(package.root):
        dirnames[:] = sorted(name for name in dirnames if not name.startswith("."))
        for filename in sorted(filenames):
            if filename.startswith("."):
                continue
            path = Path(directory, filename).relative_to(package.root).as_posix()
            if path in loaded or _classify_file(path) is None:
                continue
            unlisted.setdefault(path.rsplit("/", 1)[0] if "/" in path else "", []).append(path)
    for module_path, paths in sorted(unlisted.items()):
        module = Module(path=module_path, name=module_path.rsplit("/", 1)[-1])
        for path in paths:
            package._parse_findings.append(
                Finding(
                    "source.placement",
                    "error",
                    path,
                    path,
                    "source file is outside every listed module directory",
                )
            )
            source = SourceFile(
                path=path,
                kind=_classify_file(path) or "file",
                text=_source_text(package, path),
                module=module_path,
            )
            module.files.append(source)
            _parse_source(package, source)
        package.modules.append(module)


def _error(findings: list[Finding], rule: str, path: str, subject: str, detail: str) -> None:
    findings.append(Finding(rule, "error", path, subject, detail))


def _exact_keys(
    findings: list[Finding], data: dict, expected: set[str], path: str, subject: str
) -> None:
    for key in sorted(expected - set(data)):
        _error(findings, f"{subject}.keys", path, key, "required key is missing")
    for key in sorted(set(data) - expected):
        _error(findings, f"{subject}.keys", path, key, "key is not allowed")


def _string_list(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(item, str) for item in value)


def _validate_manifest(package: Package, findings: list[Finding]) -> None:
    path = "package.quoll.toml"
    data = package.manifest
    if data is None:
        return
    _exact_keys(findings, data, {"id", "edition", "description", "dependencies"}, path, "manifest")
    for key in ("id", "edition", "description"):
        if key in data and not isinstance(data[key], str):
            _error(findings, "manifest.type", path, key, "value must be a string")
    if "dependencies" in data and not _string_list(data["dependencies"]):
        _error(findings, "manifest.type", path, "dependencies", "value must be a list of selectors")
    package_id = data.get("id")
    if isinstance(package_id, str):
        try:
            _validate_package_id(package_id)
        except ValueError as error:
            _error(findings, "manifest.id", path, "id", str(error))
    edition = data.get("edition")
    if isinstance(edition, str) and not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", edition):
        _error(findings, "manifest.edition", path, "edition", "edition must be a quoted X.Y.Z version")
    selectors: list[Selector] = []
    dependencies = data.get("dependencies", [])
    if isinstance(dependencies, list):
        for index, raw in enumerate(dependencies):
            if not isinstance(raw, str):
                continue
            try:
                selectors.append(parse_selector(raw))
            except ValueError as error:
                _error(findings, "manifest.selector", path, f"dependencies[{index}]", str(error))
    seen: dict[tuple[str, int], Selector] = {}
    for selector in selectors:
        if selector.series in seen:
            _error(
                findings,
                "manifest.duplicate",
                path,
                selector.id,
                f"multiple selectors for major series v{selector.major}",
            )
        else:
            seen[selector.series] = selector
    package.dependencies = selectors


def _validate_membership(package: Package, findings: list[Finding]) -> None:
    path = "modules.quoll.toml"
    data = package.membership
    if data is None:
        return
    _exact_keys(findings, data, {"modules"}, path, "modules")
    modules = data.get("modules")
    if not _string_list(modules):
        _error(findings, "modules.type", path, "modules", "value must be a list of paths")
        return
    seen: set[str] = set()
    for index, member in enumerate(modules):
        subject = f"modules[{index}]"
        if not _valid_module_path(member):
            _error(findings, "modules.path", path, subject, "path must be canonical and package-relative")
        if member in seen:
            _error(findings, "modules.duplicate", path, subject, "module path is listed more than once")
        seen.add(member)


def parse_locator(value: str) -> Locator:
    """Parse a source locator without accessing its repository."""

    if not isinstance(value, str) or "@" not in value or any(c.isspace() for c in value):
        raise ValueError("locator must be repository[/package-path]@request")
    location, request = value.rsplit("@", 1)
    if not request or any(character in request for character in "/?#\\"):
        raise ValueError("locator request must be a nonempty version or committish")
    if any(character in location for character in "?#\\"):
        raise ValueError("locator repository or package path contains an invalid character")
    scheme = ""
    rest = location
    scheme_match = re.match(r"^(https?)://(.+)$", location)
    if scheme_match:
        scheme = scheme_match.group(1) + "://"
        rest = scheme_match.group(2)
    elif "://" in location:
        raise ValueError("locator scheme must be HTTP or HTTPS")
    segments = rest.split("/")
    if len(segments) < 3 or any(not segment for segment in segments):
        raise ValueError("locator repository path is incomplete")
    host = segments[0]
    if ":" in host or host.startswith("-"):
        raise ValueError("locator host is invalid")
    git_indices = [index for index, segment in enumerate(segments) if segment.endswith(".git")]
    if git_indices:
        boundary = git_indices[0]
        if boundary < 1:
            raise ValueError("invalid .git repository boundary")
        repository_segments = segments[: boundary + 1]
        package_segments = segments[boundary + 1 :]
    else:
        if host.lower() != "github.com" or len(segments) < 3:
            raise ValueError("shorthand locator must be github.com/owner/repository")
        repository_segments = segments[:3]
        package_segments = segments[3:]
    if any(segment in {".", ".."} for segment in package_segments):
        raise ValueError("locator package path is not canonical")
    package_path = "/".join(package_segments)
    repository = scheme + "/".join(repository_segments)
    return Locator(value, repository, package_path, request)


def _validate_lock(package: Package, findings: list[Finding]) -> None:
    path = "package.lock.quoll.toml"
    data = package.lock
    if data is None:
        return
    _exact_keys(findings, data, {"dependencies"}, path, "lock")
    dependencies = data.get("dependencies")
    if not isinstance(dependencies, list) or any(not isinstance(entry, dict) for entry in dependencies):
        _error(findings, "lock.type", path, "dependencies", "value must be an array of tables")
        return
    for index, entry in enumerate(dependencies):
        subject = f"dependencies[{index}]"
        _exact_keys(findings, entry, {"id", "hash", "sources"}, path, subject)
        selector: Selector | None = None
        raw_id = entry.get("id")
        if not isinstance(raw_id, str):
            _error(findings, "lock.type", path, f"{subject}.id", "value must be an exact selector")
        else:
            try:
                selector = parse_selector(raw_id)
                if not selector.exact:
                    _error(findings, "lock.selector", path, f"{subject}.id", "partial selector is not allowed in a lock")
            except ValueError as error:
                _error(findings, "lock.selector", path, f"{subject}.id", str(error))
        digest = entry.get("hash")
        if not isinstance(digest, str) or not re.fullmatch(r"1220[0-9a-f]{64}", digest):
            _error(findings, "lock.hash", path, f"{subject}.hash", "hash must be 1220 plus 64 lowercase hexadecimal digits")
        sources = entry.get("sources")
        if not isinstance(sources, list) or any(not isinstance(source, dict) for source in sources):
            _error(findings, "lock.type", path, f"{subject}.sources", "value must be an array of tables")
            continue
        if not sources:
            _error(findings, "lock.sources", path, f"{subject}.sources", "at least one source is required")
        for source_index, source in enumerate(sources):
            source_subject = f"{subject}.sources[{source_index}]"
            expected = {"locator", "commit"} | ({"tag"} if selector and selector.release else set())
            _exact_keys(findings, source, expected, path, source_subject)
            commit = source.get("commit")
            if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
                _error(findings, "lock.commit", path, f"{source_subject}.commit", "commit must be 40 lowercase hexadecimal characters")
            raw_locator = source.get("locator")
            locator: Locator | None = None
            if not isinstance(raw_locator, str):
                _error(findings, "lock.type", path, f"{source_subject}.locator", "value must be a string")
            else:
                try:
                    locator = parse_locator(raw_locator)
                except ValueError as error:
                    _error(findings, "lock.locator", path, f"{source_subject}.locator", str(error))
            tag = source.get("tag")
            if selector and selector.development and "tag" in source:
                _error(findings, "lock.tag", path, f"{source_subject}.tag", "development sources must not have a tag")
            if selector and selector.release:
                expected_tag = selector.version
                if locator and locator.package_path:
                    expected_tag = f"{locator.package_path}/{selector.version}"
                if not isinstance(tag, str) or tag != expected_tag:
                    _error(findings, "lock.tag", path, f"{source_subject}.tag", f"release tag must be {expected_tag}")


def validate_structured(package: Package) -> list[Finding]:
    """Return all structured findings for an already discovered package."""

    findings = list(package._parse_findings)
    for filename, rule in (
        ("package.quoll.toml", "manifest.required"),
        ("modules.quoll.toml", "modules.required"),
        ("package.lock.quoll.toml", "lock.required"),
    ):
        if not (package.root / filename).is_file():
            _error(findings, rule, filename, filename, "required v0.4 file is missing")
    _validate_manifest(package, findings)
    _validate_membership(package, findings)
    _validate_lock(package, findings)
    return sorted(findings)


def load_package(root: str | os.PathLike[str], baseline: bool = False) -> Package:
    """Discover and structurally validate a current or earlier v0.4 package."""

    root_path = Path(root)
    package = Package(root=root_path, name=root_path.name)
    package.manifest = _read_toml(package, "package.quoll.toml")
    package.membership = _read_toml(package, "modules.quoll.toml")
    package.lock = _read_toml(package, "package.lock.quoll.toml")
    if package.manifest and isinstance(package.manifest.get("id"), str):
        package.id = package.manifest["id"]
        try:
            package.name = package.id.rsplit("/", 1)[-1]
        except IndexError:
            pass
    members: list[str] = []
    if package.membership and isinstance(package.membership.get("modules"), list):
        members = [
            path
            for path in package.membership["modules"]
            if isinstance(path, str) and _valid_module_path(path)
        ]
    _discover_modules(package, list(dict.fromkeys(members)))
    package.findings = validate_structured(package)
    return package


def discover_package(root: str | os.PathLike[str], baseline: bool = False) -> Package:
    """Public discovery entry point; parsing errors remain package findings."""

    return load_package(root, baseline=baseline)


def structured_findings(
    root: str | os.PathLike[str] | Package, baseline: bool = False
) -> list[Finding]:
    if isinstance(root, Package):
        return validate_structured(root)
    return load_package(root, baseline=baseline).findings


def _mask_code_spans(text: str) -> str:
    characters = list(text)
    index = 0
    while index < len(text):
        if text[index] != "`":
            index += 1
            continue
        run = len(text[index:]) - len(text[index:].lstrip("`"))
        delimiter = "`" * run
        closing = text.find(delimiter, index + run)
        if closing < 0:
            index += run
            continue
        for position in range(index, closing + run):
            if characters[position] != "\n":
                characters[position] = " "
        index = closing + run
    return "".join(characters)


def _mask_literals(text: str) -> str:
    """Blank code and literal fences while retaining newlines and view blocks."""

    lines = text.splitlines(keepends=True)
    output = list(lines)
    fence: str | None = None
    fence_is_view = False
    section: str | None = None
    section_had_fence = False
    for index, line in enumerate(lines):
        heading = re.match(r"^##\s+(Structure|Flow|Rules)\s*$", line)
        if heading and fence is None:
            section = heading.group(1)
            section_had_fence = False
        elif re.match(r"^#{1,2}\s+", line) and fence is None:
            section = None
            section_had_fence = False
        marker = _fence_marker(line)
        if marker is not None:
            if fence is None:
                fence = marker
                fence_is_view = bool(section and not section_had_fence)
                if section:
                    section_had_fence = True
                output[index] = "\n" if line.endswith("\n") else ""
                continue
            if _is_fence_close(line, fence):
                fence = None
                output[index] = "\n" if line.endswith("\n") else ""
                continue
            if not fence_is_view:
                output[index] = "\n" if line.endswith("\n") else ""
                continue
        if fence is not None and not fence_is_view:
            output[index] = "\n" if line.endswith("\n") else ""
        elif re.match(r"^\s*(?:[-*+]|\d+[.)])\s+\[[ xX]\]", line):
            output[index] = re.sub(r"\[[ xX]\]", "   ", line, count=1)
    return _mask_code_spans("".join(output))


def extract_refs(text: str | SourceFile, with_lines: bool = False):
    """Extract bracketed names, excluding code spans and literal fenced blocks."""

    if isinstance(text, SourceFile):
        text = text.content or text.text
    masked = _mask_literals(text)
    references = []
    for match in re.finditer(r"\[([^\[\]\n]+)\](?!\()", masked):
        name = match.group(1).strip()
        if not name:
            continue
        if with_lines:
            references.append((name, masked.count("\n", 0, match.start()) + 1))
        else:
            references.append(name)
    return references


# The semantic checker is deliberately self-contained.  It consumes the parsed
# source above and never resolves or loads dependencies itself.
@dataclass(eq=False)
class _SemanticInterface:
    package: Package
    module: Module
    source: SourceFile
    name: str
    default: bool
    includes: list["_SemanticInterface"] = field(default_factory=list)

    @property
    def public(self) -> bool:
        return self.source.kind == "header"

    @property
    def root_public(self) -> bool:
        return self.public and self.module.path == ""


@dataclass(eq=False)
class _SemanticTarget:
    kind: str
    package: Package
    name: str
    module: Module | None = None
    interface: _SemanticInterface | None = None
    item: Item | None = None
    decision: Decision | None = None
    source: SourceFile | None = None
    dependency: Selector | None = None


@dataclass
class _SemanticSite:
    source: SourceFile
    module: Module
    reference: str
    line: int
    context: str
    owner: _SemanticInterface | None = None
    in_item: bool = False


@dataclass
class _SemanticResolution:
    targets: list[_SemanticTarget] = field(default_factory=list)
    status: str = "ok"
    detail: str = ""


@dataclass
class _SemanticAlias:
    name: str
    value: str
    source: SourceFile
    purl: bool
    selectors: list[Selector] = field(default_factory=list)


_SEMANTIC_IDENTIFIER = re.compile(r"^[a-z][a-z0-9_]*$")


def _semantic_stem(source: SourceFile) -> str:
    name = source.path.rsplit("/", 1)[-1]
    for suffix in (".private.h.md", ".h.md"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def _semantic_unique(targets: Iterable[_SemanticTarget]) -> list[_SemanticTarget]:
    result: list[_SemanticTarget] = []
    seen: set[int] = set()
    for target in targets:
        if id(target) not in seen:
            seen.add(id(target))
            result.append(target)
    return result


class _SemanticModel:
    def __init__(self, package: Package) -> None:
        self.package = package
        self.interfaces: list[_SemanticInterface] = []
        self.by_source: dict[str, _SemanticInterface] = {}
        self.by_module: dict[str, list[_SemanticInterface]] = {}
        self.modules = {module.path: _SemanticTarget("module", package, module.name, module=module) for module in package.modules}
        self.body_items: dict[str, list[_SemanticTarget]] = {}
        self.decisions: dict[str, list[_SemanticTarget]] = {}
        self.item_targets: dict[tuple[int, int], _SemanticTarget] = {}
        self.implemented: dict[str, set[_SemanticInterface]] = {module.path: set() for module in package.modules}
        self.pair_targets: dict[tuple[str, int], list[_SemanticTarget]] = {}
        self.pair_interfaces: dict[tuple[str, int], _SemanticInterface] = {}
        self.dependency_targets: dict[int, _SemanticTarget] = {}
        for module in package.modules:
            for source in module.files:
                if source.kind in {"header", "private header"}:
                    name = _semantic_stem(source)
                    interface = _SemanticInterface(
                        package,
                        module,
                        source,
                        name,
                        source.kind == "header" and name == module.name,
                    )
                    self.interfaces.append(interface)
                    self.by_source[source.path] = interface
                    self.by_module.setdefault(module.path, []).append(interface)
                elif source.kind == "body":
                    self.body_items[module.path] = [
                        _SemanticTarget(
                            "body-item",
                            package,
                            item.name,
                            module=module,
                            item=item,
                            source=source,
                        )
                        for item in source.items
                    ]
                elif source.kind == "decisions":
                    self.decisions[module.path] = [
                        _SemanticTarget(
                            "decision",
                            package,
                            decision.id,
                            module=module,
                            decision=decision,
                            source=source,
                        )
                        for decision in source.decisions
                    ]
            body = module.body
            default = self.default_interface(module)
            if body is not None and default is not None:
                self.implemented[module.path].add(default)
        for selector in package.dependencies:
            self.dependency_targets[id(selector)] = _SemanticTarget(
                "dependency",
                package,
                selector.id.rsplit("/", 1)[-1],
                dependency=selector,
            )

    def default_interface(self, module: Module) -> _SemanticInterface | None:
        return next((interface for interface in self.by_module.get(module.path, []) if interface.default), None)

    def item_target(self, interface: _SemanticInterface, item: Item) -> _SemanticTarget:
        key = (id(interface), id(item))
        if key not in self.item_targets:
            self.item_targets[key] = _SemanticTarget(
                "item",
                interface.package,
                item.name,
                module=interface.module,
                interface=interface,
                item=item,
                source=interface.source,
            )
        return self.item_targets[key]

    def interface_items(self, interface: _SemanticInterface) -> list[_SemanticTarget]:
        result: list[_SemanticTarget] = []
        seen_interfaces: set[int] = set()

        def visit(current: _SemanticInterface) -> None:
            if id(current) in seen_interfaces:
                return
            seen_interfaces.add(id(current))
            result.extend(self.item_target(current, item) for item in current.source.items)
            for included in current.includes:
                visit(included)

        visit(interface)
        return result

    def root_interfaces(self, package: Package | None = None) -> list[_SemanticInterface]:
        return [interface for interface in self.interfaces if interface.root_public]


class _SemanticResolver:
    def __init__(
        self,
        checker: "_SemanticChecker",
        source: SourceFile,
        module: Module,
        context: str,
        owner: _SemanticInterface | None,
    ) -> None:
        self.checker = checker
        self.model = checker.model
        self.source = source
        self.module = module
        self.context = context
        self.owner = owner
        raw_aliases = source.front.get("aliases", {})
        self.aliases: dict[str, _SemanticAlias] = {}
        if isinstance(raw_aliases, dict):
            for name, value in raw_aliases.items():
                if isinstance(name, str) and isinstance(value, str):
                    self.aliases[name] = _SemanticAlias(name, value, source, value.startswith("pkg:"))

    def resolve(
        self,
        reference: str,
        *,
        include_implemented: bool = True,
        allow_parent: bool = False,
        relation: bool = False,
        alias_stack: tuple[str, ...] = (),
    ) -> _SemanticResolution:
        parts = [part.strip() for part in reference.split(".")]
        if not reference or any(not part for part in parts):
            return _SemanticResolution(status="form", detail="reference has an empty name segment")
        if parts[0] in self.aliases:
            base = self._resolve_alias(parts[0], alias_stack)
            if base.status != "ok":
                return base
            if len(base.targets) != 1:
                return _SemanticResolution(status="ambiguous", detail="alias does not identify one target")
            return self._continue(base.targets[0], parts[1:])
        rooted = self._resolve_root_facade_or_module(parts)
        if rooted is not None:
            return rooted
        candidates = self._first_candidates(parts, include_implemented, allow_parent)
        visible = [target for target in candidates if self._visible(target, include_implemented, allow_parent)]
        if candidates and not visible:
            return _SemanticResolution(status="sight", detail="target exists but is outside the module's sight")
        candidates = _semantic_unique(visible)
        if not candidates:
            if self.context == "interface" and not relation and len(parts) == 1:
                forbidden = [
                    *self.model.body_items.get(self.module.path, []),
                    *self.model.decisions.get(self.module.path, []),
                ]
                matches = [target for target in forbidden if target.name == parts[0]]
                if len(matches) == 1:
                    return _SemanticResolution(matches)
                if matches:
                    return _SemanticResolution(status="ambiguous", detail="name has multiple forbidden local targets")
            return _SemanticResolution(status="unresolved", detail="no target bears this name")
        if len(candidates) > 1:
            return _SemanticResolution(status="ambiguous", detail="name identifies multiple targets at one precedence")
        target = candidates[0]
        if len(parts) == 1 and target.kind == "body-item" and target.source is not None and target.item is not None:
            pair = self.model.pair_targets.get((target.source.path, id(target.item)), [])
            return _SemanticResolution([target, *pair])
        return self._continue(target, parts[1:])

    def _resolve_root_facade_or_module(self, parts: list[str]) -> _SemanticResolution | None:
        if self.module.path != "" or len(parts) < 2 or parts[1] == "default":
            return None
        facades = [
            interface
            for interface in self.model.root_interfaces()
            if not interface.default and interface.name == parts[0]
        ]
        modules = [
            target
            for target in self.model.modules.values()
            if target.module is not None and target.module.path != "" and target.name == parts[0]
        ]
        if len(facades) != 1 or len(modules) != 1:
            return None
        facade = self._continue(self._interface_target(facades[0]), parts[1:])
        module = self._continue(modules[0], parts[1:])
        if facade.status == "ok":
            return facade
        if module.status == "ok":
            return module
        if module.status == "sight" and facade.status == "unresolved":
            return module
        return facade

    def _first_candidates(
        self,
        parts: list[str],
        include_implemented: bool,
        allow_parent: bool,
    ) -> list[_SemanticTarget]:
        name = parts[0]
        root_default_path = self.module.path == "" and len(parts) > 1 and parts[1] == "default"
        own_interfaces = self.model.by_module.get(self.module.path, [])
        if self.context == "interface":
            items = [
                target
                for interface in own_interfaces
                for target in self.model.interface_items(interface)
                if target.name == name
            ]
            if items:
                return items
        elif self.context in {"body", "decision"}:
            items = [target for target in self.model.body_items.get(self.module.path, []) if target.name == name]
            if items:
                return items
            interface_items = [
                target
                for interface in own_interfaces
                for target in self.model.interface_items(interface)
                if target.name == name
            ]
            if interface_items:
                return interface_items
        interfaces = [
            self._interface_target(interface)
            for interface in own_interfaces
            if (interface.default and name == "default")
            or (not interface.default and interface.name == name and not root_default_path)
        ]
        if interfaces:
            return interfaces
        if self.context == "decision":
            decisions = [target for target in self.model.decisions.get(self.module.path, []) if target.name == name]
            if decisions:
                return decisions
        modules = [
            target
            for target in self.model.modules.values()
            if target.name == name
            or (target.module is not None and target.module.path == "" and self.model.package.name == name)
        ]
        facades = [] if root_default_path else [
            self._interface_target(interface)
            for interface in self.model.root_interfaces()
            if not interface.default and interface.name == name
        ]
        dependencies = [
            self.model.dependency_targets[id(selector)]
            for selector in self.model.package.dependencies
            if selector.id.rsplit("/", 1)[-1] == name
        ]
        return [*facades, *modules, *dependencies]

    def _interface_target(self, interface: _SemanticInterface) -> _SemanticTarget:
        return _SemanticTarget(
            "interface",
            interface.package,
            interface.name,
            module=interface.module,
            interface=interface,
            source=interface.source,
        )

    def _visible(self, target: _SemanticTarget, include_implemented: bool, allow_parent: bool) -> bool:
        if target.package is not self.model.package:
            return True
        if target.kind == "dependency":
            return True
        if target.kind in {"body-item", "decision"}:
            return target.module is self.module
        if target.kind == "item":
            return target.interface is not None and self._interface_visible(
                target.interface, include_implemented, allow_parent
            )
        if target.kind == "interface":
            return target.interface is not None and self._interface_visible(
                target.interface, include_implemented, allow_parent
            )
        if target.kind == "module":
            other = target.module
            if other is None:
                return False
            if other is self.module or self._is_part(other, self.module) or self._is_sibling(other, self.module):
                return True
            return any(
                interface.module is other and self._interface_visible(interface, include_implemented, allow_parent)
                for interface in self.model.by_module.get(other.path, [])
            )
        return False

    @staticmethod
    def _parent_path(path: str) -> str:
        return path.rsplit("/", 1)[0] if "/" in path else ""

    def _is_part(self, candidate: Module, module: Module) -> bool:
        prefix = f"{module.path}/" if module.path else ""
        return candidate.path.startswith(prefix) and candidate.path != module.path and "/" not in candidate.path[len(prefix) :]

    def _is_sibling(self, candidate: Module, module: Module) -> bool:
        return candidate is not module and self._parent_path(candidate.path) == self._parent_path(module.path) and bool(candidate.path)

    def _interface_visible(
        self,
        interface: _SemanticInterface,
        include_implemented: bool,
        allow_parent: bool,
    ) -> bool:
        other = interface.module
        if other is self.module:
            return True
        if include_implemented and interface in self.model.implemented.get(self.module.path, set()):
            return True
        if allow_parent and other.path == self._parent_path(self.module.path):
            return True
        ancestors: list[str] = []
        path = self.module.path
        while path:
            path = self._parent_path(path)
            ancestors.append(path)
        if not interface.public:
            return other.path in ancestors
        if self._is_part(other, self.module) or self._is_sibling(other, self.module):
            return True
        return any(
            self._is_sibling(other, self.model.modules[ancestor].module)  # type: ignore[union-attr]
            for ancestor in ancestors
            if ancestor in self.model.modules
        )

    def _continue(self, target: _SemanticTarget, rest: list[str]) -> _SemanticResolution:
        if not rest:
            return _SemanticResolution([target])
        if target.kind == "module":
            return self._module_continuation(target, rest, dependency=False)
        if target.kind == "dependency":
            return self._dependency_continuation(target, rest)
        if target.kind == "interface" and target.interface is not None:
            matches = [
                candidate
                for candidate in self.model.interface_items(target.interface)
                if candidate.name == rest[0]
            ]
            matches = _semantic_unique(matches)
            if not matches:
                return _SemanticResolution(status="unresolved", detail="interface has no item with this name")
            if len(rest) > 1:
                return _SemanticResolution(status="form", detail="no segment may follow an item")
            if len(matches) > 1:
                return _SemanticResolution(status="ambiguous", detail="included interfaces give this item more than one meaning")
            return _SemanticResolution(matches)
        if target.kind in {"item", "body-item", "decision"}:
            return _SemanticResolution(status="form", detail="no segment may follow this target")
        return _SemanticResolution(status="unresolved", detail="target cannot be continued")

    def _module_continuation(
        self,
        target: _SemanticTarget,
        rest: list[str],
        *,
        dependency: bool,
    ) -> _SemanticResolution:
        module = target.module
        if module is None:
            return _SemanticResolution(status="unresolved", detail="dependency has no loaded root")
        model = self.checker.models.get(id(target.package), self.model)
        if rest[0] == "default":
            if len(rest) > 1:
                return _SemanticResolution(status="form", detail="no segment may follow a module's default")
            candidates = [
                interface
                for interface in model.by_module.get(module.path, [])
                if interface.default and (not dependency or interface.root_public)
            ]
        else:
            candidates = [
                interface
                for interface in model.by_module.get(module.path, [])
                if not interface.default and interface.name == rest[0] and (not dependency or interface.root_public)
            ]
            default = model.default_interface(module)
            if default is not None and (not dependency or default.root_public):
                items = _semantic_unique(item for item in model.interface_items(default) if item.name == rest[0])
                if items:
                    if len(rest) > 1:
                        return _SemanticResolution(status="form", detail="no segment may follow an item")
                    if candidates or len(items) > 1:
                        detail = "name is both an interface and a default item" if candidates else "default path names multiple included items"
                        return _SemanticResolution(status="ambiguous", detail=detail)
                    return _SemanticResolution(items)
        targets = [self._interface_target_for(model, interface) for interface in candidates]
        if not dependency:
            visible = [candidate for candidate in targets if self._visible(candidate, True, False)]
            if targets and not visible:
                return _SemanticResolution(status="sight", detail="interface is private at this point")
            targets = visible
        targets = _semantic_unique(targets)
        if not targets:
            return _SemanticResolution(status="unresolved", detail="module has no interface or default item with this name")
        if len(targets) > 1:
            return _SemanticResolution(status="ambiguous", detail="module path has multiple targets")
        return self._continue(targets[0], rest[1:])

    def _interface_target_for(self, model: _SemanticModel, interface: _SemanticInterface) -> _SemanticTarget:
        return _SemanticTarget(
            "interface",
            interface.package,
            interface.name,
            module=interface.module,
            interface=interface,
            source=interface.source,
        )

    def _dependency_continuation(self, target: _SemanticTarget, rest: list[str]) -> _SemanticResolution:
        supplied = self.checker.supplied_for(target.dependency)
        if supplied is None:
            if target.dependency is not None and any(
                package.id != target.dependency.id
                and package.name == target.dependency.id.rsplit("/", 1)[-1]
                for package in self.checker.dependencies
            ):
                return _SemanticResolution(
                    status="wrong-dependency",
                    detail="supplied package ID does not match the declared dependency",
                )
            if rest[0] == "default" and len(rest) > 1:
                return _SemanticResolution(status="form", detail="no segment may follow a dependency's default")
            return _SemanticResolution(status="unavailable", detail="dependency surface is not supplied")
        model = self.checker.models[id(supplied)]
        root = next((module for module in supplied.modules if module.path == ""), None)
        if root is None:
            return _SemanticResolution(status="unresolved", detail="dependency has no root module")
        external = _SemanticTarget("module", supplied, root.name, module=root)
        return self._module_continuation(external, rest, dependency=True)

    def _resolve_alias(self, name: str, stack: tuple[str, ...]) -> _SemanticResolution:
        alias = self.aliases[name]
        if name in stack:
            return _SemanticResolution(status="alias-cycle", detail=" -> ".join((*stack, name)))
        if alias.purl:
            selectors = self.checker.alias_selectors(alias)
            alias.selectors = selectors
            if not selectors:
                return _SemanticResolution(status="unresolved", detail="alias Package URL matches no manifest dependency")
            if len(selectors) > 1:
                return _SemanticResolution(status="ambiguous", detail="unqualified alias selects several manifest dependencies")
            return _SemanticResolution([self.model.dependency_targets[id(selectors[0])]])
        base = self.resolve(alias.value, alias_stack=(*stack, name))
        if base.status in {"unavailable", "alias-cycle"}:
            return base
        if base.status != "ok":
            return base
        if len(base.targets) != 1 or base.targets[0].kind not in {"interface", "item"}:
            return _SemanticResolution(status="form", detail="qualified alias must name one dependency interface or item")
        if base.targets[0].package is self.model.package:
            return _SemanticResolution(status="form", detail="qualified alias target is not reached through a dependency")
        return base


class _SemanticChecker:
    def __init__(self, package: Package, dependency_packages: Iterable[Package]) -> None:
        self.package = package
        self.dependencies = list(dependency_packages)
        self.models: dict[int, _SemanticModel] = {id(package): _SemanticModel(package)}
        self.model = self.models[id(package)]
        for dependency in self.dependencies:
            prepared = _SemanticChecker(dependency, ())
            prepared._resolve_implements()
            prepared._resolve_includes()
            self.models[id(dependency)] = prepared.model
        self.findings: list[Finding] = []
        self.resolved_sites: list[tuple[_SemanticSite, _SemanticResolution]] = []
        self.used_modules: dict[str, set[str]] = {module.path: set() for module in package.modules}
        self.used_interfaces: dict[str, set[_SemanticInterface]] = {module.path: set() for module in package.modules}
        self.resolvers: dict[str, _SemanticResolver] = {}

    def error(self, rule: str, source: SourceFile | str, subject: str, detail: str, line: int = 0) -> None:
        self.findings.append(Finding(rule, "error", source if isinstance(source, str) else source.path, subject, detail, line))

    def resolver_for(self, source: SourceFile, module: Module) -> _SemanticResolver:
        owner = self.model.by_source.get(source.path)
        context = "interface" if owner is not None else "decision" if source.kind == "decisions" else "body"
        key = source.path
        if key not in self.resolvers:
            self.resolvers[key] = _SemanticResolver(self, source, module, context, owner)
        return self.resolvers[key]

    def supplied_for(self, selector: Selector | None) -> Package | None:
        if selector is None:
            return None
        candidates = [package for package in self.dependencies if package.id == selector.id]
        return candidates[0] if len(candidates) == 1 else None

    def alias_selectors(self, alias: _SemanticAlias) -> list[Selector]:
        raw = alias.value.split("#", 1)[0]
        if "@" not in raw:
            return [selector for selector in self.package.dependencies if selector.id == raw]
        try:
            selected = parse_selector(raw)
        except ValueError:
            return []
        result = []
        for selector in self.package.dependencies:
            if selector.id != selected.id or selector.major != selected.major:
                continue
            if selected.partial and selector.kind != "stable":
                continue
            if selected.minor is not None and selector.minor is not None and selected.minor != selector.minor:
                continue
            if selected.patch is not None and selector.patch is not None and selected.patch != selector.patch:
                continue
            if selected.exact and selector.exact and selected.version != selector.version:
                continue
            result.append(selector)
        return result

    def run(self) -> list[Finding]:
        self._check_names_and_leads()
        self._resolve_implements()
        self._resolve_includes()
        self._resolve_impl_items()
        self._check_body_unique_names()
        self._check_aliases()
        self._resolve_sites()
        self._check_decision_statements()
        self._check_definitions()
        self._compute_uses()
        self._check_cycles()
        self._check_complete_uses()
        self._check_structural_joins()
        self._check_public_closure()
        self._check_independent_modules()
        existing = {finding.key for finding in self.package.findings}
        return sorted(
            {finding for finding in self.findings if finding.key not in existing},
            key=lambda finding: finding.sort_key,
        )

    def _check_names_and_leads(self) -> None:
        if not _SEMANTIC_IDENTIFIER.fullmatch(self.package.name):
            self.error("semantic.identifiers", self.package.name, self.package.name, "package name is not a lowercase ASCII identifier")
        for module in self.package.modules:
            if not _SEMANTIC_IDENTIFIER.fullmatch(module.name):
                self.error("semantic.identifiers", module.path or self.package.name, module.name, "module name is not a lowercase ASCII identifier")
            headers = [source for source in module.files if source.kind in {"header", "private header"}]
            named = [source for source in headers if _semantic_stem(source) != module.name or source.kind != "header"]
            marked = [source for source in named if source.front.get("module lead") is True]
            default = self.model.default_interface(module)
            if len(marked) > 1:
                self.error("semantic.one-module-lead", module.path or self.package.name, module.name, "more than one named interface is marked module lead")
            if module.body is None and default is None and len(marked) != 1:
                self.error("semantic.one-module-lead", module.path or self.package.name, module.name, "a module without a body or default header needs exactly one named module lead")
            seen_interfaces: dict[str, list[_SemanticInterface]] = {}
            for interface in self.model.by_module.get(module.path, []):
                seen_interfaces.setdefault(interface.name, []).append(interface)
                if not _SEMANTIC_IDENTIFIER.fullmatch(interface.name) or interface.name == "default":
                    self.error("semantic.identifiers" if interface.name != "default" else "semantic.defaults", interface.source, interface.name, "interface name is reserved or is not a lowercase ASCII identifier")
                item_names: dict[str, list[Item]] = {}
                for item in interface.source.items:
                    item_names.setdefault(item.name, []).append(item)
                    if "." in item.name or item.name == "default":
                        self.error("semantic.defaults" if item.name == "default" else "semantic.identifiers", interface.source, item.name, "item name contains a dot or is reserved", item.line)
                for name, items in item_names.items():
                    if len(items) > 1:
                        self.error("semantic.unique-names", interface.source, name, "interface declares an item name more than once", items[1].line)
                if interface.default:
                    for other in self.model.by_module.get(module.path, []):
                        if other is not interface and any(item.name == other.name for item in interface.source.items):
                            self.error("semantic.defaults", interface.source, other.name, "default item name collides with another provided interface")
            for name, interfaces in seen_interfaces.items():
                if len(interfaces) > 1:
                    self.error("semantic.unique-names", interfaces[1].source, name, "module provides this interface name more than once")
            if module.body is not None:
                for item in module.body.items:
                    if "." in item.name or item.name == "default":
                        self.error("semantic.defaults" if item.name == "default" else "semantic.identifiers", module.body, item.name, "item name contains a dot or is reserved", item.line)

    def _resolve_implements(self) -> None:
        for module in self.package.modules:
            body = module.body
            if body is None:
                continue
            resolver = self.resolver_for(body, module)
            for reference in body.front.get("implements", []):
                if not isinstance(reference, str):
                    continue
                resolution = resolver.resolve(reference, include_implemented=False, allow_parent=True, relation=True)
                interface = self._one_interface(resolution)
                if interface is None:
                    self.error("semantic.implementable", body, reference, resolution.detail or "implements relation does not name one visible interface")
                else:
                    self.model.implemented[module.path].add(interface)

    def _resolve_includes(self) -> None:
        for interface in self.model.interfaces:
            resolver = self.resolver_for(interface.source, interface.module)
            for reference in interface.source.front.get("includes", []):
                if not isinstance(reference, str):
                    continue
                resolution = resolver.resolve(reference, relation=True)
                included = self._one_interface(resolution)
                if included is None:
                    self.error("semantic.includable", interface.source, reference, resolution.detail or "includes relation does not name one visible interface")
                else:
                    interface.includes.append(included)

    def _resolve_impl_items(self) -> None:
        for module in self.package.modules:
            body = module.body
            if body is None:
                continue
            resolver = self.resolver_for(body, module)
            implemented = self.model.implemented[module.path]
            implemented_items: dict[str, list[_SemanticTarget]] = {}
            for interface in implemented:
                for target in self.model.interface_items(interface):
                    implemented_items.setdefault(target.name, []).append(target)
            for item in body.items:
                if item.impl is None:
                    if item.name in implemented_items:
                        self.error("semantic.paired", body, item.name, "unpaired body item bears an implemented interface item's name", item.line)
                    continue
                resolution = resolver.resolve(item.impl, relation=True)
                interface = self._one_interface(resolution)
                if interface is None or interface not in implemented:
                    self.error("semantic.relations", body, item.impl, "impl relation does not name an interface this module implements", item.line)
                    continue
                self.model.pair_interfaces[(body.path, id(item))] = interface
                matches = [target for target in self.model.interface_items(interface) if target.name == item.name]
                if len(matches) != 1:
                    self.error("semantic.paired", body, item.name, "pair has no unique same-named interface item", item.line)
                else:
                    self.model.pair_targets[(body.path, id(item))] = matches

    def _check_body_unique_names(self) -> None:
        for module in self.package.modules:
            body = module.body
            if body is None:
                continue
            groups: dict[str, list[Item]] = {}
            for item in body.items:
                groups.setdefault(item.name, []).append(item)
            for name, items in groups.items():
                if len(items) < 2:
                    continue
                interfaces = [
                    self.model.pair_interfaces.get((body.path, id(item)))
                    for item in items
                ]
                distinct_pairs = all(interface is not None for interface in interfaces) and len({id(interface) for interface in interfaces}) == len(items)
                if not distinct_pairs:
                    self.error("semantic.unique-names", body, name, "body declares an item name more than once for one interface", items[1].line)

    @staticmethod
    def _one_interface(resolution: _SemanticResolution) -> _SemanticInterface | None:
        if resolution.status == "ok" and len(resolution.targets) == 1:
            return resolution.targets[0].interface if resolution.targets[0].kind == "interface" else None
        return None

    def _check_aliases(self) -> None:
        for source in self.package.files:
            if not isinstance(source.front.get("aliases"), dict):
                continue
            module = self.package.module_map[source.module]
            resolver = self.resolver_for(source, module)
            local_names = self._local_names(resolver)
            for alias in resolver.aliases.values():
                if not _SEMANTIC_IDENTIFIER.fullmatch(alias.name):
                    self.error("semantic.alias-unique", source, alias.name, "alias is not a lowercase ASCII identifier")
                if alias.name in local_names:
                    self.error("semantic.alias-unique", source, alias.name, "alias collides with a visible dependency or local reference name")
                resolution = resolver._resolve_alias(alias.name, ())
                if resolution.status == "alias-cycle":
                    self.error("semantic.alias-cycle", source, alias.name, resolution.detail)
                elif resolution.status == "ambiguous":
                    self.error("semantic.alias-ambiguous", source, alias.name, resolution.detail)
                elif resolution.status in {"unresolved", "form", "sight", "wrong-dependency"}:
                    self.error("semantic.alias-target", source, alias.name, resolution.detail)

    def _local_names(self, resolver: _SemanticResolver) -> set[str]:
        names = {selector.id.rsplit("/", 1)[-1] for selector in self.package.dependencies}
        for interface in self.model.by_module.get(resolver.module.path, []):
            names.add("default" if interface.default else interface.name)
            names.update(target.name for target in self.model.interface_items(interface))
        if resolver.context in {"body", "decision"}:
            names.update(target.name for target in self.model.body_items.get(resolver.module.path, []))
        if resolver.context == "decision":
            names.update(target.name for target in self.model.decisions.get(resolver.module.path, []))
        for target in self.model.modules.values():
            if resolver._visible(target, True, False):
                names.add(target.name)
                if target.module is not None and target.module.path == "":
                    names.add(self.package.name)
        for interface in self.model.root_interfaces():
            if not interface.default and resolver._visible(resolver._interface_target(interface), True, False):
                names.add(interface.name)
        return names

    def _decision_file_mnemonic(self, source: SourceFile) -> str | None:
        mnemonics: set[str] = set()
        for decision in source.decisions:
            match = re.fullmatch(r"([A-Za-z][A-Za-z0-9-]*)-[0-9]+", decision.id)
            if match:
                mnemonics.add(match.group(1))
        return mnemonics.pop() if len(mnemonics) == 1 else None

    @staticmethod
    def _bare_decision_refs(
        source: SourceFile, decision: Decision, mnemonic: str
    ) -> list[tuple[str, int]]:
        lines = _mask_literals(source.content).splitlines(keepends=True)
        text = "".join(lines[decision.line - 1 : decision.end_line])
        opening = re.match(r"\s*\*\*" + re.escape(decision.id) + r"(?=\.)", text)
        if opening:
            text = " " * opening.end() + text[opening.end() :]
        kept_lines: list[str] = []
        in_formerly = False
        for line in text.splitlines(keepends=True):
            field = re.match(r"^\s*\*([^*\n]+)\*[ \t]+", line)
            if field:
                in_formerly = field.group(1).strip().casefold() == "formerly"
            kept_lines.append(
                "".join("\n" if character == "\n" else " " for character in line)
                if in_formerly
                else line
            )
        text = "".join(kept_lines)
        text = re.sub(r"\[[^\[\]\n]+\]", lambda match: " " * len(match.group(0)), text)
        pattern = re.compile(
            rf"(?<![A-Za-z0-9-]){re.escape(mnemonic)}-[0-9]+(?![0-9-])"
        )
        return [
            (match.group(0), decision.line + text.count("\n", 0, match.start()))
            for match in pattern.finditer(text)
        ]

    def _sites(self) -> list[_SemanticSite]:
        sites: list[_SemanticSite] = []
        for module in self.package.modules:
            for source in module.files:
                if source.kind not in {"header", "private header", "body", "decisions"}:
                    continue
                owner = self.model.by_source.get(source.path)
                context = "interface" if owner is not None else "decision" if source.kind == "decisions" else "body"
                ranges: list[tuple[int, int, int]] = []
                if source.kind == "decisions":
                    ranges = [(decision.line, decision.end_line, decision.line - 1) for decision in source.decisions if decision.active]
                else:
                    ranges = [(1, len(source.content.splitlines()), 0)]
                lines = source.content.splitlines(keepends=True)
                for start, end, offset in ranges:
                    text = "".join(lines[start - 1 : end])
                    relation_lines = {
                        start + index
                        for index, line in enumerate(text.splitlines())
                        if re.match(r"^\s*impl\s+\[[^\]]+\]\s*:?\s*$", line)
                    }
                    for reference, line in extract_refs(text, with_lines=True):
                        physical = line + offset
                        if physical in relation_lines:
                            continue
                        in_item = any(item.line <= physical <= item.end_line for item in source.items)
                        sites.append(_SemanticSite(source, module, reference, physical, context, owner, in_item))
                if source.kind == "decisions":
                    mnemonic = self._decision_file_mnemonic(source)
                    if mnemonic is not None:
                        for decision in source.decisions:
                            if not decision.active:
                                continue
                            for reference, physical in self._bare_decision_refs(source, decision, mnemonic):
                                sites.append(
                                    _SemanticSite(source, module, reference, physical, context, owner)
                                )
        return sites

    def _resolve_sites(self) -> None:
        for site in self._sites():
            resolver = self.resolver_for(site.source, site.module)
            resolution = resolver.resolve(site.reference)
            if resolution.status == "unresolved":
                hidden = self._hidden_dependency(site.reference)
                if hidden:
                    self.error("semantic.dependency", site.source, site.reference, "reference uses a supplied package that is not a declared dependency", site.line)
                else:
                    self.error("semantic.resolved", site.source, site.reference, resolution.detail, site.line)
                continue
            if resolution.status == "ambiguous":
                self.error("semantic.ambiguous", site.source, site.reference, resolution.detail, site.line)
                continue
            if resolution.status == "sight":
                self.error("semantic.sight", site.source, site.reference, resolution.detail, site.line)
                continue
            if resolution.status == "form":
                self.error("semantic.reference-form", site.source, site.reference, resolution.detail, site.line)
                continue
            if resolution.status == "wrong-dependency":
                self.error("semantic.dependency", site.source, site.reference, resolution.detail, site.line)
                continue
            if resolution.status != "ok":
                continue
            self.resolved_sites.append((site, resolution))
            if site.context == "interface" and any(target.kind in {"body-item", "decision"} for target in resolution.targets):
                self.error("semantic.independent", site.source, site.reference, "interface reference lands on a body item or decision", site.line)

    def _hidden_dependency(self, reference: str) -> bool:
        parts = reference.split(".")
        declared = {selector.id for selector in self.package.dependencies}
        for dependency in self.dependencies:
            if dependency.id in declared or dependency.name != parts[0]:
                continue
            model = self.models[id(dependency)]
            root = next((module for module in dependency.modules if module.path == ""), None)
            if len(parts) == 1:
                return True
            if root is None:
                continue
            resolver = next(iter(self.resolvers.values()), None)
            if resolver is None:
                continue
            target = _SemanticTarget("module", dependency, root.name, module=root)
            resolution = resolver._module_continuation(target, parts[1:], dependency=True)
            if resolution.status == "ok":
                return True
        return False

    def _check_decision_statements(self) -> None:
        reference_pattern = re.compile(r"\[[^\[\]\n]+\](?!\()")
        for module in self.package.modules:
            for source in module.files:
                if source.kind != "decisions":
                    continue
                resolver = self.resolver_for(source, module)
                for decision in source.decisions:
                    if not decision.active:
                        continue
                    fields = list(decision.fields.items())
                    if not fields or fields[0][0] != "Stated by":
                        self.error(
                            "semantic.stated-by-form",
                            source,
                            decision.id,
                            "active decision's first field must be Stated by",
                            decision.line,
                        )
                        continue
                    stated_by = fields[0][1]
                    references = extract_refs(stated_by)
                    shape = reference_pattern.sub("\x00", stated_by.strip())
                    if not references or not re.fullmatch(
                        r"\x00(?:(?:\s*,\s*(?:and\s+)?|\s+and\s+)\x00)*\.?",
                        shape,
                    ):
                        self.error(
                            "semantic.stated-by-form",
                            source,
                            decision.id,
                            "Stated by must hold item references with only permitted joining punctuation and words",
                            decision.line,
                        )
                    for reference in references:
                        resolution = resolver.resolve(reference)
                        if resolution.status != "ok" or not any(
                            target.kind in {"item", "body-item"}
                            for target in resolution.targets
                        ):
                            self.error(
                                "semantic.stated-by-target",
                                source,
                                decision.id,
                                f"Stated by reference [{reference}] does not land on one item",
                                decision.line,
                            )

    def _check_definitions(self) -> None:
        nodes: dict[tuple[str, int], tuple[SourceFile, Item]] = {}
        graph: dict[tuple[str, int], set[tuple[str, int]]] = {}
        for module in self.package.modules:
            for source in module.files:
                for item in source.items:
                    node = (source.path, id(item))
                    nodes[node] = (source, item)
                    graph[node] = set()
        for site, resolution in self.resolved_sites:
            origin = next(
                (
                    item
                    for item in site.source.items
                    if item.line <= site.line <= item.end_line
                ),
                None,
            )
            if origin is None:
                continue
            origin_node = (site.source.path, id(origin))
            for target in resolution.targets:
                if (
                    target.kind not in {"item", "body-item"}
                    or target.source is None
                    or target.item is None
                ):
                    continue
                target_node = (target.source.path, id(target.item))
                if target_node not in graph:
                    continue
                graph[origin_node].add(target_node)
                if (
                    origin.view == "Structure"
                    and target.source is site.source
                    and target.item.line > origin.line
                ):
                    self.error(
                        "semantic.definition-order",
                        site.source,
                        origin.name,
                        f"Structure item refers to later item {target.item.name}",
                        site.line,
                    )

        counter = 0
        indices: dict[tuple[str, int], int] = {}
        low: dict[tuple[str, int], int] = {}
        stack: list[tuple[str, int]] = []
        on_stack: set[tuple[str, int]] = set()

        def visit(node: tuple[str, int]) -> None:
            nonlocal counter
            indices[node] = low[node] = counter
            counter += 1
            stack.append(node)
            on_stack.add(node)
            for other in graph[node]:
                if other not in indices:
                    visit(other)
                    low[node] = min(low[node], low[other])
                elif other in on_stack:
                    low[node] = min(low[node], indices[other])
            if low[node] != indices[node]:
                return
            component: list[tuple[str, int]] = []
            while True:
                other = stack.pop()
                on_stack.remove(other)
                component.append(other)
                if other == node:
                    break
            if len(component) > 1:
                for member in component:
                    source, item = nodes[member]
                    self.error(
                        "semantic.definition-cycle",
                        source,
                        item.name,
                        "item definitions form a reference cycle",
                        item.line,
                    )

        for node in graph:
            if node not in indices:
                visit(node)

    def _compute_uses(self) -> None:
        for site, resolution in self.resolved_sites:
            for target in resolution.targets:
                interface = target.interface if target.kind in {"interface", "item"} else None
                if interface is None or interface.package is not self.package:
                    continue
                if interface.module is site.module:
                    continue
                self.used_modules[site.module.path].add(interface.module.path)
                self.used_interfaces[site.module.path].add(interface)

    def _check_cycles(self) -> None:
        include_graph = {interface: set(interface.includes) for interface in self.model.interfaces}
        reference_graph = {interface: set() for interface in self.model.interfaces}
        for site, resolution in self.resolved_sites:
            if site.owner is None:
                continue
            for target in resolution.targets:
                if target.interface is not None:
                    reference_graph[site.owner].add(target.interface)
        combined_graph = {
            interface: include_graph[interface] | reference_graph[interface]
            for interface in self.model.interfaces
        }
        include_cycles = self._cycle_nodes(include_graph, include_self=True)
        for interface in self._cycle_nodes(combined_graph, include_self=True):
            if interface in include_cycles:
                self.error("semantic.includes-cycle", interface.source, interface.name, "interface inclusion forms a cycle")
            else:
                self.error("semantic.interface-cycle", interface.source, interface.name, "interface inclusion and references form a cycle")
        for interface in self.model.interfaces:
            groups: dict[str, list[_SemanticTarget]] = {}
            for target in self.model.interface_items(interface):
                groups.setdefault(target.name, []).append(target)
            for name, targets in groups.items():
                if len(_semantic_unique(targets)) > 1:
                    self.error("semantic.unique-names", interface.source, name, "included interfaces expose colliding item names")

    @staticmethod
    def _cycle_nodes(
        graph: dict[_SemanticInterface, set[_SemanticInterface]],
        *,
        include_self: bool,
    ) -> set[_SemanticInterface]:
        index = 0
        indices: dict[_SemanticInterface, int] = {}
        low: dict[_SemanticInterface, int] = {}
        stack: list[_SemanticInterface] = []
        on_stack: set[_SemanticInterface] = set()
        result: set[_SemanticInterface] = set()

        def visit(node: _SemanticInterface) -> None:
            nonlocal index
            indices[node] = low[node] = index
            index += 1
            stack.append(node)
            on_stack.add(node)
            for other in graph.get(node, set()):
                if other not in indices:
                    visit(other)
                    low[node] = min(low[node], low[other])
                elif other in on_stack:
                    low[node] = min(low[node], indices[other])
            if low[node] == indices[node]:
                component: list[_SemanticInterface] = []
                while True:
                    other = stack.pop()
                    on_stack.remove(other)
                    component.append(other)
                    if other is node:
                        break
                if len(component) > 1:
                    result.update(component)
                elif include_self and node in graph.get(node, set()):
                    result.add(node)

        for node in graph:
            if node not in indices:
                visit(node)
        return result

    def _check_complete_uses(self) -> None:
        root = next((module for module in self.package.modules if module.path == ""), None)
        if root is None or root.body is None:
            return
        declarations: dict[str, tuple[Item, set[str]]] = {}
        ambiguous: set[str] = set()
        for item in root.body.items:
            parsed = self._parse_complete_use(item)
            if parsed is None:
                continue
            subject, expected = parsed
            if subject in declarations:
                ambiguous.add(subject)
            else:
                declarations[subject] = (item, expected)
        for subject in ambiguous:
            declarations.pop(subject, None)
        for subject, (item, expected) in declarations.items():
            actual = self.used_modules.get(subject, set())
            if actual != expected:
                missing = sorted(expected - actual)
                unexpected = sorted(actual - expected)
                details = []
                if missing:
                    details.append("missing " + ", ".join(missing))
                if unexpected:
                    details.append("undeclared " + ", ".join(unexpected))
                self.error("semantic.uses", root.body, subject or self.package.name, "; ".join(details) or "use declaration differs from resolved references", item.line)

    def _parse_complete_use(self, item: Item) -> tuple[str, set[str]] | None:
        text = item.statements.strip()
        references = extract_refs(text)
        if references.count("model.uses") != 1:
            return None
        uses_index = references.index("model.uses")
        if uses_index < 1 or not references[uses_index - 1].endswith(".default"):
            return None
        subject_name = references[uses_index - 1][: -len(".default")]
        subject = self._direct_default_module(subject_name)
        if subject is None:
            return None
        trailing = references[uses_index + 1 :]
        if trailing == ["model.interface"]:
            if not re.search(r"\bno\s+\[model\.interface\]", text):
                return None
            return subject, set()
        if (
            not text.endswith("alone")
            or len(trailing) < 3
            or trailing[:2] != ["model.interface", "model.module"]
        ):
            return None
        expected_names = [reference[: -len(".default")] for reference in trailing[2:] if reference.endswith(".default")]
        if len(expected_names) != len(trailing) - 2 or len(expected_names) != len(set(expected_names)):
            return None
        expected: set[str] = set()
        for name in expected_names:
            module = self._direct_default_module(name)
            if module is None:
                return None
            expected.add(module)
        return subject, expected

    def _direct_default_module(self, name: str) -> str | None:
        root = next((module for module in self.package.modules if module.path == ""), None)
        if root is None:
            return None
        for module in self.package.modules:
            if module.name == name and self._is_direct_part(module, root) and self.model.default_interface(module) is not None:
                return module.path
        return None

    @staticmethod
    def _is_direct_part(module: Module, root: Module) -> bool:
        prefix = f"{root.path}/" if root.path else ""
        return module.path.startswith(prefix) and module.path != root.path and "/" not in module.path[len(prefix) :]

    def _check_structural_joins(self) -> None:
        defaults: dict[str, _SemanticInterface] = {}
        for name in ("model", "grammar", "source"):
            module = next((module for module in self.package.modules if module.name == name), None)
            default = self.model.default_interface(module) if module is not None else None
            if default is None:
                return
            defaults[name] = default
        model_items = {item.name for item in defaults["model"].source.items}
        grammar_items = {item.name for item in defaults["grammar"].source.items}
        for item in defaults["source"].source.items:
            if item.name not in model_items or item.name not in grammar_items:
                continue
            references = set(extract_refs(item.statements))
            required = {f"model.{item.name}", f"grammar.{item.name}"}
            missing = sorted(required - references)
            if missing:
                self.error(
                    "semantic.join",
                    defaults["source"].source,
                    item.name,
                    "same-named source item does not reference " + " and ".join(missing),
                    item.line,
                )

    def _check_public_closure(self) -> None:
        facades = self.model.root_interfaces()
        if not facades:
            return
        exposed: set[tuple[str, int, str]] = set()
        for facade in facades:
            for target in self.model.interface_items(facade):
                if target.source is not None and target.item is not None:
                    exposed.add((target.source.path, id(target.item), target.name))
        selected: dict[tuple[str, int, str], tuple[_SemanticSite, _SemanticResolution]] = {}
        resolved_by_site = {(site.source.path, site.line, site.reference): resolution for site, resolution in self.resolved_sites}
        for site, resolution in self.resolved_sites:
            if site.owner is None:
                continue
            is_facade_source = site.owner in facades and site.source is site.owner.source
            is_included_item = site.in_item and any(site.owner in self._included_closure(facade) for facade in facades)
            if is_facade_source or is_included_item:
                selected[(site.source.path, site.line, site.reference)] = (site, resolution)
        for site, resolution in selected.values():
            if all(self._public_target(target, exposed) for target in resolution.targets):
                continue
            if any(target.kind == "body-item" for target in resolution.targets) and any(self._public_target(target, exposed) for target in resolution.targets):
                continue
            self.error("semantic.public-closure", site.source, site.reference, "public facade reference escapes the exposed item surface", site.line)

    def _included_closure(self, facade: _SemanticInterface) -> set[_SemanticInterface]:
        result: set[_SemanticInterface] = set()

        def visit(interface: _SemanticInterface) -> None:
            for included in interface.includes:
                if included not in result:
                    result.add(included)
                    visit(included)

        visit(facade)
        return result

    def _public_target(self, target: _SemanticTarget, exposed: set[tuple[str, int, str]]) -> bool:
        if target.kind != "item" or target.item is None or target.source is None or target.interface is None:
            return False
        if target.package is not self.package:
            model = self.models[id(target.package)]
            return any(
                exposed_target.item is target.item
                for facade in model.root_interfaces()
                for exposed_target in model.interface_items(facade)
            )
        return (target.source.path, id(target.item), target.name) in exposed

    def _check_independent_modules(self) -> None:
        for site, resolution in self.resolved_sites:
            if site.owner is None:
                continue
            for target in resolution.targets:
                if target.kind != "module" or target.module is None:
                    continue
                if site.owner in self.model.implemented.get(target.module.path, set()) or site.owner in self.used_interfaces.get(target.module.path, set()):
                    self.error("semantic.independent", site.source, site.reference, "interface references a module that implements or uses it", site.line)


def semantic_findings(package: Package, dependency_packages: Iterable[Package] = ()) -> list[Finding]:
    """Return local semantic findings; supplied dependencies are never loaded here."""

    return _SemanticChecker(package, dependency_packages).run()


@dataclass(frozen=True)
class _DecisionLocation:
    module: Module
    source: SourceFile
    decision: Decision


@dataclass(frozen=True)
class _ItemLocation:
    module: Module
    source: SourceFile
    item: Item


def _decision_locations(package: Package) -> list[_DecisionLocation]:
    return [
        _DecisionLocation(module, source, decision)
        for module in package.modules
        for source in module.files
        if source.kind == "decisions"
        for decision in source.decisions
    ]


def _item_locations(package: Package) -> list[_ItemLocation]:
    return [
        _ItemLocation(module, source, item)
        for module in package.modules
        for source in module.files
        for item in source.items
    ]


def _decision_field(decision: Decision, name: str) -> str | None:
    return next(
        (value for key, value in decision.fields.items() if key.casefold() == name.casefold()),
        None,
    )


def _canonical_decision(text: str, *, without_successor: bool = False) -> str:
    kept: list[str] = []
    skipping = False
    for line in text.splitlines():
        field_match = re.match(r"^\s*\*([^*\n]+)\*[ \t]+", line)
        if field_match:
            skipping = without_successor and field_match.group(1).strip().casefold() == "superseded by"
        elif re.match(r"^\s*\*\*[^\s*.]+\.\s+", line):
            skipping = False
        if not skipping:
            kept.append(line)
    return " ".join(" ".join(kept).split())


def _decision_index(
    package: Package,
) -> dict[tuple[str, str], list[_DecisionLocation]]:
    index: dict[tuple[str, str], list[_DecisionLocation]] = {}
    for location in _decision_locations(package):
        key = (location.module.path, location.decision.id)
        index.setdefault(key, []).append(location)
    return index


def _lifetime_finding(
    findings: list[Finding],
    rule: str,
    location: _DecisionLocation,
    detail: str,
    severity: str = "error",
) -> None:
    findings.append(
        Finding(rule, severity, location.source.path, location.decision.id, detail, location.decision.line)
    )


def _successor_cycles(
    index: dict[tuple[str, str], list[_DecisionLocation]]
) -> set[tuple[str, str]]:
    graph: dict[tuple[str, str], set[tuple[str, str]]] = {key: set() for key in index}
    for key, locations in index.items():
        module_path, decision_id = key
        for location in locations:
            successor = location.decision.successor
            if successor is not None and successor != decision_id:
                target = (module_path, successor)
                if target in index:
                    graph[key].add(target)

    counter = 0
    indices: dict[tuple[str, str], int] = {}
    low: dict[tuple[str, str], int] = {}
    stack: list[tuple[str, str]] = []
    on_stack: set[tuple[str, str]] = set()
    cycles: set[tuple[str, str]] = set()

    def visit(node: tuple[str, str]) -> None:
        nonlocal counter
        indices[node] = low[node] = counter
        counter += 1
        stack.append(node)
        on_stack.add(node)
        for other in graph[node]:
            if other not in indices:
                visit(other)
                low[node] = min(low[node], low[other])
            elif other in on_stack:
                low[node] = min(low[node], indices[other])
        if low[node] == indices[node]:
            component: list[tuple[str, str]] = []
            while True:
                other = stack.pop()
                on_stack.remove(other)
                component.append(other)
                if other == node:
                    break
            if len(component) > 1:
                cycles.update(component)

    for node in graph:
        if node not in indices:
            visit(node)
    return cycles


def _decision_history_matches(old: Decision, current: Decision) -> bool:
    unchanged = _canonical_decision(old.text) == _canonical_decision(current.text)
    gained_successor = (
        old.successor is None
        and current.successor is not None
        and _canonical_decision(old.text)
        == _canonical_decision(current.text, without_successor=True)
    )
    return unchanged or gained_successor


def _committed_predecessor(
    previous: list[_DecisionLocation], location: _DecisionLocation
) -> _DecisionLocation:
    if len(previous) == 1:
        return previous[0]
    return next(
        (
            candidate
            for candidate in previous
            if _decision_history_matches(candidate.decision, location.decision)
        ),
        previous[0],
    )


def decision_lifetime_findings(
    package: Package, baseline: Package | None = None, review: bool = False
) -> list[Finding]:
    """Check committed decision persistence and all current successor links."""

    findings: list[Finding] = []
    current = _decision_index(package)
    committed = _decision_index(baseline) if baseline is not None else {}
    baseline_ids = {decision_id for _, decision_id in committed}

    global_current: dict[str, list[_DecisionLocation]] = {}
    for location in _decision_locations(package):
        global_current.setdefault(location.decision.id, []).append(location)
    for decision_id, locations in global_current.items():
        if len(locations) < 2:
            continue
        first = locations[0]
        _lifetime_finding(
            findings,
            "lifetime.duplicate-id",
            first,
            "decision ID is not unique; occurrences: "
            + ", ".join(f"{location.source.path}:{location.decision.line}" for location in locations),
        )

    for key, locations in current.items():
        module_path, decision_id = key
        for location in locations:
            decision = location.decision
            successor = decision.successor
            if successor is not None:
                if successor == decision_id:
                    _lifetime_finding(
                        findings,
                        "lifetime.successor-self",
                        location,
                        "successor differs from its predecessor",
                    )
                elif (module_path, successor) not in current:
                    _lifetime_finding(
                        findings,
                        "lifetime.successor-missing",
                        location,
                        f"successor {successor} does not exist in the same module",
                    )

            previous_locations = committed.get(key)
            if baseline is None:
                continue
            if previous_locations is None:
                if successor is not None and successor != decision_id and successor in baseline_ids:
                    _lifetime_finding(
                        findings,
                        "lifetime.successor-stale",
                        location,
                        f"successor {successor} was already committed and is not fresh",
                    )
                continue

            old = _committed_predecessor(previous_locations, location).decision
            if not _decision_history_matches(old, decision):
                altered_history = successor is not None or old.successor is not None
                if altered_history or review:
                    _lifetime_finding(
                        findings,
                        "lifetime.in-place-replacement",
                        location,
                        (
                            "historical entry text changed despite supersession"
                            if altered_history
                            else "committed entry text changed without supersession; review for possible choice replacement"
                        ),
                        "error" if altered_history else "review",
                    )
            if old.successor is not None and successor != old.successor:
                _lifetime_finding(
                    findings,
                    "lifetime.successor-changed",
                    location,
                    "committed successor link was changed or removed",
                )
            elif old.successor is None and successor is not None and successor != decision_id:
                if successor in baseline_ids:
                    _lifetime_finding(
                        findings,
                        "lifetime.successor-stale",
                        location,
                        f"successor {successor} was already committed and is not fresh",
                    )

    if baseline is not None:
        for key, previous_locations in committed.items():
            if key in current:
                continue
            for previous in previous_locations:
                findings.append(
                    Finding(
                        "lifetime.withdrawn",
                        "error",
                        previous.source.path,
                        previous.decision.id,
                        "committed decision ID does not persist in the same module",
                        previous.decision.line,
                    )
                )

    for key in _successor_cycles(current):
        for location in current[key]:
            _lifetime_finding(
                findings,
                "lifetime.successor-cycle",
                location,
                "successor links form a cycle",
            )
    return _sorted_findings(findings)


_NEGATIVE_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"\b(?:does|do)\s+not\s+(?:contain|include|hold|list|provide|comprise|consist\s+of)\b",
        r"\b(?:contains?|includes?|holds?|lists?|provides?)\s+(?:no|none|nothing)\b",
        r"\b(?:must|shall|may)\s+(?:not|never)\s+(?:contain|include|hold|list|provide)\b",
        r"\b(?:excluding|except(?:ing)?|other\s+than)\b",
        r"\bwithout\s+(?:any\s+)?[\w-]+",
    )
)
_PROSE_CORE_WORDS = {"structure", "flow", "rules", "open", "ensures", "requires", "impl", "default"}


def _negative_material(text: str) -> bool:
    return any(pattern.search(text) for pattern in _NEGATIVE_PATTERNS)


def _stated_by_decisions(
    package: Package, item_location: _ItemLocation
) -> list[_DecisionLocation]:
    checker = _SemanticChecker(package, ())
    checker._resolve_includes()
    associations: list[_DecisionLocation] = []
    for location in _decision_locations(package):
        decision = location.decision
        if not decision.active:
            continue
        stated_by = _decision_field(decision, "Stated by")
        if stated_by is None:
            continue
        resolver = checker.resolver_for(location.source, location.module)
        for reference in extract_refs(stated_by):
            if "." not in reference and location.module.path != item_location.module.path:
                continue
            resolution = resolver.resolve(reference)
            if resolution.status != "ok":
                continue
            if any(
                target.item is item_location.item and target.module is item_location.module
                for target in resolution.targets
            ):
                associations.append(location)
                break
    return associations


def _rejected_associations(
    package: Package, item_location: _ItemLocation
) -> dict[tuple[str, str], str]:
    result: dict[tuple[str, str], str] = {}
    for location in _stated_by_decisions(package, item_location):
        rejected = _decision_field(location.decision, "Rejected")
        if rejected is not None:
            result[(location.module.path, location.decision.id)] = " ".join(rejected.split())
    return result


def _negative_definition_findings(package: Package) -> list[Finding]:
    findings: list[Finding] = []
    for location in _item_locations(package):
        item = location.item
        if item.view != "Structure" or not _negative_material(item.statements):
            continue
        associations = _stated_by_decisions(package, location)
        if associations:
            evidence = "; ".join(
                f"{associated.decision.id}: "
                + (
                    "Rejected present"
                    if _decision_field(associated.decision, "Rejected") is not None
                    else "no Rejected field"
                )
                for associated in associations
            )
        else:
            evidence = "no active Stated by decision"
        findings.append(
            Finding(
                "prose.negative-definition",
                "review",
                location.source.path,
                item.name,
                "negative or exclusion inventory; " + evidence,
                item.line,
            )
        )
    return findings


def _preservation_findings(package: Package, baseline: Package) -> list[Finding]:
    current_items = {
        (location.source.path, location.item.name): location
        for location in _item_locations(package)
        if location.item.view == "Structure"
    }
    findings: list[Finding] = []
    for old in _item_locations(baseline):
        if old.item.view != "Structure" or not _negative_material(old.item.statements):
            continue
        current = current_items.get((old.source.path, old.item.name))
        if current is None or _negative_material(current.item.statements):
            continue
        before = _rejected_associations(baseline, old)
        after = _rejected_associations(package, current)
        unchanged = sorted(
            decision_id
            for (module_path, decision_id), rejected in before.items()
            if after.get((module_path, decision_id)) == rejected
        )
        if not unchanged:
            continue
        findings.append(
            Finding(
                "prose.rejected-preservation",
                "review",
                current.source.path,
                current.item.name,
                "negative material disappeared while Rejected text remained unchanged for "
                + ", ".join(unchanged)
                + "; verify the alternatives were preserved",
                current.item.line,
            )
        )
    return findings


def _blank_match(match: re.Match[str]) -> str:
    return "".join("\n" if character == "\n" else " " for character in match.group(0))


def _mask_prose(text: str) -> str:
    masked = _mask_literals(text)
    masked = re.sub(r"!?\[[^\]\n]*\]\([^\)\n]*\)", _blank_match, masked)
    masked = re.sub(r"<(?:https?://|mailto:)[^>\n]+>", _blank_match, masked)
    return re.sub(r"\[[^\[\]\n]+\](?!\()", _blank_match, masked)


def _ambiguous_english_use(text: str, match: re.Match[str]) -> bool:
    preceding = re.search(r"([A-Za-z]+)\s*$", text[: match.start()])
    if preceding is not None and preceding.group(1).casefold() in {"own", "one"}:
        return True
    return re.match(r"(?:own|one)(?:\s|-)", match.group(0), re.IGNORECASE) is not None


def _definition_spans(source: SourceFile) -> list[tuple[int, int]]:
    lines = _mask_prose(source.content).splitlines(keepends=True)
    offsets: list[int] = []
    offset = 0
    for line in lines:
        offsets.append(offset)
        offset += len(line)
    spans: list[tuple[int, int]] = []
    for item in source.items:
        if not (1 <= item.line <= len(lines)):
            continue
        line = lines[item.line - 1]
        match = re.search(rf"(?<![\w-]){re.escape(item.name)}(?![\w-])", line)
        if match is not None:
            start = offsets[item.line - 1] + match.start()
            spans.append((start, start + (match.end() - match.start())))
    return spans


def _prose_regions(source: SourceFile) -> list[tuple[str, int]]:
    if source.kind != "decisions":
        return [(source.content, 1)]
    lines = source.content.splitlines(keepends=True)
    return [
        ("".join(lines[decision.line - 1 : decision.end_line]), decision.line)
        for decision in source.decisions
        if decision.active
    ]


def _word_forms(word: str) -> list[str]:
    if word.endswith("y") and len(word) > 1 and word[-2].casefold() not in "aeiou":
        plural = word[:-1] + "ies"
    elif word.casefold().endswith(("s", "x", "z", "ch", "sh")):
        plural = word + "es"
    else:
        plural = word + "s"
    forms = {
        word,
        plural,
        word + "'s",
        word + "’s",
        plural + "'s",
        plural + "’s",
        plural + "'",
        plural + "’",
    }
    return sorted(forms, key=len, reverse=True)


@dataclass(frozen=True)
class _BareCandidate:
    start: int
    end: int
    finding: Finding


def _bare_candidates(package: Package, review: bool) -> list[Finding]:
    names = {location.item.name for location in _item_locations(package)}
    compounds = [name for name in names if re.split(r"[ -]+", name.strip()) and len(re.split(r"[ -]+", name.strip())) > 1]
    singles = [
        name
        for name in names
        if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", name) and name.casefold() not in _PROSE_CORE_WORDS
    ]
    findings: list[Finding] = []
    for source in package.files:
        if source.kind not in {"header", "private header", "body", "decisions"}:
            continue
        definitions = _definition_spans(source)
        for region, base_line in _prose_regions(source):
            masked = _mask_prose(region)
            candidates: list[_BareCandidate] = []
            for name in compounds:
                words = re.split(r"[ -]+", name.strip())
                final_forms = _word_forms(words[-1])
                expression = r"[ -]".join(
                    [*(re.escape(word) for word in words[:-1]), "(?:" + "|".join(map(re.escape, final_forms)) + ")"]
                )
                pattern = re.compile(rf"(?<![\w-]){expression}(?![\w-])")
                for match in pattern.finditer(masked):
                    if _ambiguous_english_use(masked, match):
                        continue
                    if any(start < match.end() and match.start() < end for start, end in definitions):
                        continue
                    line = base_line + masked.count("\n", 0, match.start())
                    candidates.append(
                        _BareCandidate(
                            match.start(),
                            match.end(),
                            Finding(
                                "prose.bare-compound",
                                "error",
                                source.path,
                                name,
                                f"bare multiword item name; write [{name}] when this use names the item",
                                line,
                            ),
                        )
                    )
            if review:
                for name in singles:
                    expression = "(?:" + "|".join(map(re.escape, _word_forms(name))) + ")"
                    pattern = re.compile(rf"(?<![\w-]){expression}(?![\w-])")
                    for match in pattern.finditer(masked):
                        if _ambiguous_english_use(masked, match):
                            continue
                        if any(start < match.end() and match.start() < end for start, end in definitions):
                            continue
                        line = base_line + masked.count("\n", 0, match.start())
                        candidates.append(
                            _BareCandidate(
                                match.start(),
                                match.end(),
                                Finding(
                                    "prose.bare-word",
                                    "review",
                                    source.path,
                                    name,
                                    f"ambiguous bare item name; write [{name}] if this use names the item",
                                    line,
                                ),
                            )
                        )
            occupied: list[tuple[int, int]] = []
            for candidate in sorted(candidates, key=lambda candidate: (candidate.start, -(candidate.end - candidate.start), candidate.finding.key)):
                if any(start < candidate.end and candidate.start < end for start, end in occupied):
                    continue
                occupied.append((candidate.start, candidate.end))
                findings.append(candidate.finding)
    grouped: dict[tuple[str, str, str, str], list[Finding]] = {}
    for finding in findings:
        key = (finding.rule, finding.path, finding.subject, finding.detail)
        grouped.setdefault(key, []).append(finding)
    result: list[Finding] = []
    for (rule, path, subject, detail), occurrences in grouped.items():
        result.append(
            Finding(
                rule,
                occurrences[0].severity,
                path,
                subject,
                f"{detail}; occurrence count {len(occurrences)}",
                min(finding.line for finding in occurrences),
            )
        )
    return result


def _sorted_findings(findings: Iterable[Finding]) -> list[Finding]:
    unique: dict[tuple[str, str, str, str, str], Finding] = {}
    for finding in findings:
        previous = unique.get(finding.key)
        if previous is None or (finding.line and (not previous.line or finding.line < previous.line)):
            unique[finding.key] = finding
    severity = {"error": 0, "review": 1}
    return sorted(unique.values(), key=lambda finding: (severity[finding.severity], finding.sort_key))


def prose_findings(
    package: Package, baseline: Package | None = None, review: bool = False
) -> list[Finding]:
    """Check high-confidence bare compounds and bounded definition-style reviews."""

    findings = _bare_candidates(package, review)
    findings.extend(_negative_definition_findings(package))
    if baseline is not None:
        findings.extend(_preservation_findings(package, baseline))
    return _sorted_findings(findings)


def check_package(
    package: Package,
    baseline: Package | None = None,
    dependency_packages: Iterable[Package] = (),
    review: bool = False,
) -> list[Finding]:
    """Aggregate current checks, suppressing only exact committed finding keys."""

    dependencies = tuple(dependency_packages)
    current = [
        *structured_findings(package),
        *semantic_findings(package, dependencies),
        *prose_findings(package, baseline=baseline, review=review),
    ]
    if baseline is not None:
        committed = [
            *structured_findings(baseline),
            *semantic_findings(baseline, dependencies),
            *prose_findings(baseline, review=review),
        ]
        committed_keys = {finding.key for finding in committed}
        current = [finding for finding in current if finding.key not in committed_keys]
    current.extend(decision_lifetime_findings(package, baseline, review=review))
    if not review:
        current = [finding for finding in current if finding.severity == "error"]
    return _sorted_findings(current)


_WINDOWS_RESERVED = {"CON", "PRN", "AUX", "NUL"} | {
    f"{prefix}{number}" for prefix in ("COM", "LPT") for number in range(1, 10)
}
_WINDOWS_BAD = set('<>:"\\|?*')


def _validate_hash_path(path: str) -> str:
    if not isinstance(path, str) or not path or path.startswith("/"):
        raise ValueError("content path must be nonempty and package-relative")
    if "\\" in path or "\x00" in path:
        raise ValueError(f"noncanonical content path: {path!r}")
    try:
        path.encode("utf-8")
    except UnicodeEncodeError as error:
        raise ValueError("content path must be valid UTF-8") from error
    for component in path.split("/"):
        if component in {"", ".", ".."}:
            raise ValueError(f"noncanonical content path: {path!r}")
        if component.endswith((".", " ")):
            raise ValueError(f"Windows-incompatible trailing dot or space: {path!r}")
        if any(ord(character) < 32 or character in _WINDOWS_BAD for character in component):
            raise ValueError(f"Windows-incompatible content path: {path!r}")
        if component.split(".", 1)[0].upper() in _WINDOWS_RESERVED:
            raise ValueError(f"Windows-reserved content path: {path!r}")
    return path


def _validate_mode(mode: int, path: str) -> None:
    if not isinstance(mode, int) or not stat.S_ISREG(mode):
        raise ValueError(f"non-regular content file: {path}")
    if mode & 0o111:
        raise ValueError(f"executable content file: {path}")
    if mode & 0o7000:
        raise ValueError(f"special-mode content file: {path}")


def content_hash(records: Iterable[FileRecord]) -> str:
    """Return Go dirhash.Hash1 encoded as a SHA-256 multihash."""

    rows: list[tuple[bytes, str, bytes]] = []
    folded: dict[str, str] = {}
    for record in records:
        path = _validate_hash_path(record.path)
        _validate_mode(record.mode, path)
        collision = path.casefold()
        if collision in folded:
            raise ValueError(f"case-insensitive content path collision: {folded[collision]!r} and {path!r}")
        folded[collision] = path
        if not isinstance(record.data, bytes):
            raise ValueError(f"content bytes must be bytes: {path}")
        rows.append((path.encode("utf-8"), path, record.data))
    rows.sort(key=lambda row: row[0])
    summary = b"".join(
        hashlib.sha256(data).hexdigest().encode("ascii")
        + b"  "
        + path.encode("utf-8")
        + b"\n"
        for _, path, data in rows
    )
    return "1220" + hashlib.sha256(summary).hexdigest()


def _directory_records(root: Path, directory: Path, prefix: str = "") -> Iterator[FileRecord]:
    try:
        entries = list(os.scandir(directory))
    except OSError as error:
        raise ValueError(f"cannot scan content directory {directory}: {error}") from error
    for entry in sorted(entries, key=lambda item: item.name):
        if entry.name.startswith("."):
            continue
        path = f"{prefix}/{entry.name}" if prefix else entry.name
        mode = entry.stat(follow_symlinks=False).st_mode
        if stat.S_ISLNK(mode):
            raise ValueError(f"symlink content file: {path}")
        if stat.S_ISDIR(mode):
            yield from _directory_records(root, Path(entry.path), path)
            continue
        if not stat.S_ISREG(mode):
            raise ValueError(f"non-regular content file: {path}")
        try:
            data = Path(entry.path).read_bytes()
        except OSError as error:
            raise ValueError(f"cannot read content file {path}: {error}") from error
        yield FileRecord(path, data, mode, _classify_file(path) or "file")


def hash_directory(root: str | os.PathLike[str]) -> str:
    """Hash real files below root, omitting every dot-named file or directory."""

    root_path = Path(root)
    mode = root_path.lstat().st_mode
    if stat.S_ISLNK(mode) or not stat.S_ISDIR(mode):
        raise ValueError("content root must be a real directory")
    return content_hash(_directory_records(root_path, root_path))
