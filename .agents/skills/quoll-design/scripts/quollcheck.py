"""Structured and semantic checks for current Quoll 0.6.0 packages.

Baselines are same-edition trees used only for diff and decision-lifetime checks.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from datetime import datetime, timezone
import hashlib
import os
from pathlib import Path
import re
import stat
import tomllib
from typing import Iterable, Iterator


CURRENT_EDITION = "0.6.0"
LANGUAGE_PACKAGE_ID = "pkg:quoll/rete-labs.ru/quoll/language"
EDITION_FINDING_RULES = {"manifest.edition", "workspace.edition"}
EDITION_PRELUDE = {
    "workspace": "model.graph.workspace",
    "package": "model.graph.package",
    "module": "model.kernel.module",
    "interface": "model.kernel.interface",
    "item": "model.kernel.item",
    "decision": "model.kernel.decision",
    "uses": "model.kernel.uses",
}


@dataclass(frozen=True, order=True)
class Finding:
    """One diagnostic; its ordering and equality intentionally ignore line."""

    rule: str
    severity: str
    path: str
    subject: str
    detail: str
    line: int = field(default=0, compare=False)
    package_id: str = ""

    def __post_init__(self) -> None:
        if self.severity not in {"error", "review"}:
            raise ValueError("finding severity must be 'error' or 'review'")

    @property
    def key(self) -> tuple[str, str, str, str, str, str]:
        return (
            self.rule,
            self.severity,
            self.path,
            self.subject,
            self.detail,
            self.package_id,
        )

    @property
    def sort_key(self) -> tuple[str, str, str, str, str, str]:
        return self.key

    def __str__(self) -> str:
        location = self.path or "<package>"
        if self.package_id:
            location = f"{self.package_id}::{location}"
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
    workspace: dict | None = None
    lock: dict | None = None
    workspace_members: list[Package] = field(default_factory=list, repr=False)
    related_decisions: list[tuple[Module, SourceFile]] = field(default_factory=list, repr=False)
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
    if top and name == "workspace.decisions.md":
        return "workspace decisions"
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
    if source.kind not in {"header", "private header", "body", "decisions", "workspace decisions"}:
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


def _valid_exposure_spelling(value: object) -> bool:
    if not isinstance(value, str) or not value or value != value.strip():
        return False
    if any(character in value for character in "[]\r\n"):
        return False
    parts = value.split(".")
    return all(part and part == part.strip() for part in parts)


def _toml_assignment_key(line: str) -> str | None:
    """Return the raw TOML key before an assignment's unquoted equals sign."""

    quote: str | None = None
    escaped = False
    for index, character in enumerate(line):
        if quote == '"':
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == quote:
                quote = None
        elif quote == "'":
            if character == quote:
                quote = None
        elif character in {'"', "'"}:
            quote = character
        elif character == "=":
            return line[:index]
    return None


def _toml_declares_key(raw_key: str, key: str) -> bool:
    """Decode bare, dotted, literal and escaped basic keys with the TOML parser."""

    try:
        parsed = tomllib.loads(f"{raw_key} = 0")
    except tomllib.TOMLDecodeError:
        return False
    return key in parsed


def _front_mapping_line(source: SourceFile, key: str) -> int:
    """Locate a decoded key only in the actual exposes table or inline table."""

    in_exposes = False
    for number, line in enumerate(source.text.splitlines(), 1):
        stripped = line.strip()
        if stripped == "+++":
            if number > 1:
                break
            continue
        if stripped.startswith("["):
            try:
                table = tomllib.loads(stripped)
            except tomllib.TOMLDecodeError:
                in_exposes = False
            else:
                nested = table.get("exposes")
                in_exposes = table == {"exposes": {}}
                if (
                    not in_exposes
                    and set(table) == {"exposes"}
                    and isinstance(nested, dict)
                    and key in nested
                ):
                    return number
            continue
        raw_key = _toml_assignment_key(line)
        if raw_key is None:
            continue
        if in_exposes and _toml_declares_key(raw_key, key):
            return number
        try:
            parsed = tomllib.loads(line)
        except tomllib.TOMLDecodeError:
            continue
        inline = parsed.get("exposes")
        if isinstance(inline, dict) and key in inline:
            return number
    return 0


def _validate_front(package: Package, source: SourceFile) -> None:
    if not source.front:
        return
    allowed = {"aliases", "use", "prelude"}
    if source.kind == "body":
        allowed.add("implements")
    elif source.kind in {"header", "private header"}:
        allowed.update({"includes", "exposes", "module lead"})
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
        elif key == "prelude":
            if not isinstance(value, list) or any(not isinstance(name, str) for name in value):
                package._parse_findings.append(
                    Finding("front.type", "error", source.path, key, "value must be a TOML string array")
                )
                continue
            seen: set[str] = set()
            for name in value:
                if name not in EDITION_PRELUDE:
                    package._parse_findings.append(
                        Finding("front.prelude", "error", source.path, name, "unknown edition prelude alias")
                    )
                if name in seen:
                    package._parse_findings.append(
                        Finding("front.prelude", "error", source.path, name, "duplicate edition prelude alias")
                    )
                seen.add(name)
        elif key == "use":
            if not isinstance(value, dict):
                package._parse_findings.append(
                    Finding("front.type", "error", source.path, key, "value must be a table of string arrays")
                )
                continue
            for prefix, continuations in value.items():
                if not _valid_exposure_spelling(prefix):
                    package._parse_findings.append(
                        Finding("front.use", "error", source.path, str(prefix), "use prefix is not a nonempty abstract reference")
                    )
                if not isinstance(continuations, list) or any(
                    not isinstance(continuation, str) for continuation in continuations
                ):
                    package._parse_findings.append(
                        Finding("front.type", "error", source.path, str(prefix), "use value must be a TOML string array")
                    )
                    continue
                seen_continuations: set[str] = set()
                for continuation in continuations:
                    if (
                        not _valid_exposure_spelling(continuation)
                        or continuation.startswith("pkg:")
                    ):
                        package._parse_findings.append(
                            Finding("front.use", "error", source.path, continuation, "use continuation is not a nonempty relative reference")
                        )
                    if continuation in seen_continuations:
                        package._parse_findings.append(
                            Finding("front.use", "error", source.path, continuation, "duplicate use continuation")
                        )
                    seen_continuations.add(continuation)
        elif key == "exposes":
            if not isinstance(value, dict):
                package._parse_findings.append(
                    Finding("front.type", "error", source.path, key, "value must be a table of string targets")
                )
            else:
                for exposed, target in value.items():
                    line = _front_mapping_line(source, exposed)
                    if not _valid_exposure_spelling(exposed):
                        package._parse_findings.append(
                            Finding("front.exposure", "error", source.path, str(exposed), "exposed path is not a reference spelling without brackets", line)
                        )
                    if not isinstance(target, str):
                        detail = (
                            "dotted exposure keys must be quoted wholly as one TOML key"
                            if isinstance(target, dict)
                            else "exposure target must be a TOML string"
                        )
                        package._parse_findings.append(
                            Finding("front.type", "error", source.path, str(exposed), detail, line)
                        )
                    elif not _valid_exposure_spelling(target):
                        package._parse_findings.append(
                            Finding("front.exposure", "error", source.path, str(exposed), "target is not a reference spelling without brackets", line)
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
                    if target.startswith("pkg:") and source.kind != "workspace decisions":
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
    match = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
    return match.group(1) if match else None


def _is_fence_close(line: str, marker: str) -> bool:
    raw = line.rstrip("\r\n")
    return bool(
        re.fullmatch(rf" {{0,3}}{re.escape(marker[0])}{{{len(marker)},}}[ \t]*", raw)
    )


def _atx_heading(line: str) -> tuple[int, str] | None:
    """Return a canonical plain ATX heading's level and text."""

    raw = line.rstrip("\r\n")
    match = re.fullmatch(r"(#{1,6}) (.+)", raw)
    if match is None:
        return None
    text = match.group(2)
    if text != text.strip() or re.search(r"(?:^|[ \t])#+$", text):
        return None
    return len(match.group(1)), text


def _view_blocks(lines: list[str]) -> list[tuple[str, int, int]]:
    """Return each first named section's first fence content bounds."""

    blocks: list[tuple[str, int, int]] = []
    fence: str | None = None
    view_start: int | None = None
    view_section: str | None = None
    section: str | None = None
    section_had_fence = False
    seen_sections: set[str] = set()

    for index, line in enumerate(lines):
        raw = line.rstrip("\r\n")
        if fence is not None:
            if _is_fence_close(raw, fence):
                if view_start is not None and view_section is not None:
                    blocks.append((view_section, view_start, index))
                    view_start = None
                    view_section = None
                fence = None
            continue

        heading = _atx_heading(raw)
        if heading is not None:
            level, text = heading
            if level <= 2:
                section = None
                section_had_fence = False
                if level == 2 and text in {"Structure", "Flow", "Rules"} and text not in seen_sections:
                    section = text
                    seen_sections.add(text)
            continue

        marker = _fence_marker(raw)
        if marker is not None:
            fence = marker
            if section is not None and not section_had_fence:
                view_start = index + 1
                view_section = section
                section_had_fence = True

    if view_start is not None and view_section is not None:
        blocks.append((view_section, view_start, len(lines)))
    return blocks


def _parse_views(source: SourceFile, lines: list[str]) -> None:
    blocks = _view_blocks(lines)
    for piece in ("Structure", "Flow", "Rules"):
        for view_piece, start, end in blocks:
            if view_piece != piece:
                continue
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
                for item in _parse_view(lines, start, end)
            )


_ONE_LINE_POINTER_STUB = re.compile(
    r"^\s*\*\*([^\s*.]+)\.\*\*[ \t]+\*Superseded by\*[ \t]+([^\s*.]+)\s*$",
    re.IGNORECASE,
)


def _parse_decisions(source: SourceFile, lines: list[str]) -> None:
    current: Decision | None = None
    last_field: str | None = None
    for index, line in enumerate(lines):
        stub = _ONE_LINE_POINTER_STUB.fullmatch(line)
        if stub:
            successor = stub.group(2)
            source.decisions.append(
                Decision(
                    id=stub.group(1),
                    fields={"Superseded by": successor},
                    line=index + 1,
                    end_line=index + 1,
                    active=False,
                    successor=successor,
                )
            )
            current = None
            last_field = None
            continue
        entry = re.match(r"^\s*\*\*([^\s*.]+)\.(?:\s+(.+?))?\s*\*\*\s*$", line)
        if entry:
            current = Decision(
                id=entry.group(1),
                title=(entry.group(2) or "").strip(),
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
    if source.kind in {"decisions", "workspace decisions"}:
        _parse_decisions(source, lines)
    elif source.kind in {"header", "private header", "body"}:
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


def _baseline_copy_root(package: Package, candidate: Path) -> bool:
    """Recognize a nested copy of the baseline package, not another package."""

    try:
        return all(
            (package.root / filename).read_bytes() == (candidate / filename).read_bytes()
            for filename in ("package.quoll.toml", "modules.quoll.toml")
        )
    except OSError:
        return False


def _discover_modules(package: Package, member_paths: list[str], baseline: bool = False) -> None:
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
    workspace_roots = set()
    if package.workspace is not None:
        workspace_roots = {
            path
            for path in package.workspace.get("packages", [])
            if isinstance(path, str)
            and _valid_module_path(path)
            and (package.root / path / "package.quoll.toml").is_file()
        }
    for directory, dirnames, filenames in os.walk(package.root):
        dirnames[:] = sorted(name for name in dirnames if not name.startswith("."))
        relative_directory = Path(directory).relative_to(package.root)
        dirnames[:] = [
            name
            for name in dirnames
            if (relative_directory / name).as_posix() not in workspace_roots
            and not (
                baseline
                and _baseline_copy_root(package, Path(directory) / name)
            )
        ]
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
    if len(segments) < 2 or any(not segment for segment in segments):
        raise ValueError("locator repository path is incomplete")
    host = segments[0]
    if ":" in host or host.startswith("-"):
        raise ValueError("locator host is invalid")
    hostless_github = not scheme and "." not in host and host.lower() != "github.com"
    git_indices = [index for index, segment in enumerate(segments) if segment.endswith(".git")]
    if hostless_github:
        repository_segments = ["github.com", *segments[:2]]
        package_segments = segments[2:]
    elif git_indices:
        boundary = git_indices[0]
        if boundary < 1:
            raise ValueError("invalid .git repository boundary")
        repository_segments = segments[: boundary + 1]
        package_segments = segments[boundary + 1 :]
    else:
        if host.lower() != "github.com" or len(segments) < 3:
            raise ValueError("shorthand locator must be [github.com/]owner/repository")
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


def _validate_workspace(package: Package, findings: list[Finding]) -> None:
    path = "workspace.quoll.toml"
    data = package.workspace
    if data is None:
        return
    _exact_keys(findings, data, {"packages", "edition", "description"}, path, "workspace")
    if "description" in data and not isinstance(data["description"], str):
        _error(findings, "workspace.type", path, "description", "value must be a string")
    edition = data.get("edition")
    if "edition" in data and not isinstance(edition, str):
        _error(findings, "workspace.type", path, "edition", "value must be a string")
    if edition != CURRENT_EDITION:
        _error(findings, "workspace.edition", path, "edition", "every current and baseline workspace requires exactly 0.6.0")
    packages = data.get("packages")
    if not _string_list(packages):
        _error(findings, "workspace.type", path, "packages", "value must be a list of workspace-relative paths")
        return
    seen: set[str] = set()
    for index, member in enumerate(packages):
        subject = f"packages[{index}]"
        if not _valid_module_path(member):
            _error(findings, "workspace.path", path, subject, "member path must be canonical and workspace-relative")
        if member in seen:
            _error(findings, "workspace.duplicate", path, subject, "member path is listed more than once")
        seen.add(member)


def validate_structured(package: Package) -> list[Finding]:
    """Return all structured findings for an already discovered package."""

    findings = list(package._parse_findings)
    if package.manifest is None and package.workspace is not None:
        _validate_workspace(package, findings)
        return _sorted_findings(findings)
    for filename, rule in (
        ("package.quoll.toml", "manifest.required"),
        ("modules.quoll.toml", "modules.required"),
        ("package.lock.quoll.toml", "lock.required"),
    ):
        if not (package.root / filename).is_file():
            _error(findings, rule, filename, filename, "required package file is missing")
    _validate_manifest(package, findings)
    _validate_membership(package, findings)
    _validate_lock(package, findings)
    if package.workspace is not None:
        _validate_workspace(package, findings)
    return _sorted_findings(findings)


def _load_related_decisions(package: Package) -> None:
    """Load only the decision collection of a workspace declaring this package."""

    if package.workspace is not None:
        return
    package_root = package.root.resolve()
    for ancestor in package.root.parents:
        manifest_path = ancestor / "workspace.quoll.toml"
        if not manifest_path.is_file():
            continue
        try:
            with manifest_path.open("rb") as stream:
                workspace = tomllib.load(stream)
        except (OSError, UnicodeDecodeError, tomllib.TOMLDecodeError):
            continue
        members = workspace.get("packages", [])
        if not isinstance(members, list) or not any(
            isinstance(member, str)
            and _valid_module_path(member)
            and (ancestor / member).resolve() == package_root
            for member in members
        ):
            continue
        if workspace.get("edition") != CURRENT_EDITION:
            package._parse_findings.append(
                Finding(
                    "workspace.edition",
                    "error",
                    str(manifest_path),
                    "edition",
                    "related workspace decisions require workspace edition 0.6.0 before front parsing",
                )
            )
            return
        decision_path = ancestor / "workspace.decisions.md"
        try:
            text = decision_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            return
        source = SourceFile(
            path=str(decision_path),
            kind="workspace decisions",
            text=text,
            module="<workspace>",
        )
        lines = _parse_front(package, source, text.splitlines(keepends=True))
        _validate_front(package, source)
        source.content = "".join(lines)
        _parse_decisions(source, lines)
        package.related_decisions.append(
            (Module(path="<workspace>", name="workspace", files=[source]), source)
        )
        return


def _edition_role_valid(package: Package, baseline: bool, workspace_only: bool) -> bool:
    """Validate the package or workspace edition before source/front discovery."""

    data = package.workspace if workspace_only else package.manifest
    edition = data.get("edition") if data else None
    if edition == CURRENT_EDITION:
        return True
    path = "workspace.quoll.toml" if workspace_only else "package.quoll.toml"
    rule = "workspace.edition" if workspace_only else "manifest.edition"
    role = "baseline" if baseline else "current"
    if not isinstance(edition, str):
        detail = f"a quoted edition 0.6.0 is required for every {role} package or workspace"
    elif not re.fullmatch(r"[0-9]+\.[0-9]+\.[0-9]+", edition):
        detail = f"edition is malformed; every {role} package or workspace requires exactly 0.6.0"
    else:
        detail = f"unsupported {role} edition {edition}; only 0.6.0 is supported"
    package._parse_findings.append(
        Finding(rule, "error", path, "edition", detail)
    )
    return False


def load_package(root: str | os.PathLike[str], baseline: bool = False) -> Package:
    """Discover a current 0.6.0 package or an explicit verification baseline."""

    root_path = Path(root)
    package = Package(root=root_path, name=root_path.name)
    package.manifest = _read_toml(package, "package.quoll.toml")
    package.workspace = _read_toml(package, "workspace.quoll.toml")
    workspace_only = package.manifest is None and (root_path / "workspace.quoll.toml").is_file()
    if package.manifest and isinstance(package.manifest.get("id"), str):
        package.id = package.manifest["id"]
        package.name = package.id.rsplit("/", 1)[-1]
    if package.manifest and isinstance(package.manifest.get("edition"), str):
        package.edition = package.manifest["edition"]
    elif workspace_only and package.workspace and isinstance(package.workspace.get("edition"), str):
        package.edition = package.workspace["edition"]
    if not _edition_role_valid(package, baseline, workspace_only):
        package.findings = validate_structured(package)
        return package

    package.membership = _read_toml(package, "modules.quoll.toml")
    package.lock = _read_toml(package, "package.lock.quoll.toml")
    if workspace_only and package.workspace and isinstance(package.workspace.get("packages"), list):
        for member_path in package.workspace["packages"]:
            if isinstance(member_path, str) and _valid_module_path(member_path):
                package.workspace_members.append(
                    load_package(root_path / member_path, baseline=baseline)
                )
    members: list[str] = []
    if package.membership and isinstance(package.membership.get("modules"), list):
        members = [
            path
            for path in package.membership["modules"]
            if isinstance(path, str) and _valid_module_path(path)
        ]
    _discover_modules(package, list(dict.fromkeys(members)), baseline=baseline)
    if not workspace_only:
        _load_related_decisions(package)
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
    seen_sections: set[str] = set()
    for index, line in enumerate(lines):
        heading = _atx_heading(line)
        if heading is not None and fence is None:
            level, text = heading
            if level <= 2:
                section = None
                section_had_fence = False
                if level == 2 and text in {"Structure", "Flow", "Rules"} and text not in seen_sections:
                    section = text
                    seen_sections.add(text)
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
    external: bool = False
    exposure: _SemanticExposure | None = None
    exposure_chain: tuple[_SemanticExposure, ...] = ()


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
    edition: bool = False


@dataclass
class _SemanticAlias:
    name: str
    value: str
    source: SourceFile
    purl: bool
    selectors: list[Selector] = field(default_factory=list)
    derived: bool = False
    prelude: bool = False


@dataclass(eq=False)
class _SemanticExposure:
    module: Module
    source: SourceFile
    key: tuple[str, ...]
    value: str
    line: int
    resolution: _SemanticResolution | None = None
    dependencies: set["_SemanticExposure"] = field(default_factory=set)

    @property
    def name(self) -> str:
        return ".".join(self.key)

    @property
    def target(self) -> _SemanticTarget | None:
        if self.resolution is None or self.resolution.status != "ok" or len(self.resolution.targets) != 1:
            return None
        return self.resolution.targets[0]


@dataclass(frozen=True)
class PublicUnit:
    """One self-contained canonical source file needed by an external reader."""

    identity: str
    path: str
    locator: str
    package_id: str
    dependencies: tuple[str, ...] = ()
    exposures: tuple[str, ...] = ()
    edition: str = CURRENT_EDITION
    text: str = ""


@dataclass(frozen=True)
class PublicModule:
    """An exposed module's identity and directory place, without its contents."""

    identity: str
    path: str
    locator: str
    package_id: str
    name: str


@dataclass(frozen=True)
class PublicReading:
    """A deterministic, bounded canonical public-reader input."""

    units: tuple[PublicUnit, ...]
    dependencies: tuple[str, ...]
    modules: tuple[PublicModule, ...] = ()

    @property
    def paths(self) -> tuple[str, ...]:
        return tuple(unit.path for unit in self.units)

    @property
    def identities(self) -> tuple[str, ...]:
        return tuple(unit.identity for unit in self.units)


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
        self.exposures: list[_SemanticExposure] = []
        self.exposures_by_module: dict[str, list[_SemanticExposure]] = {}
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
        for module in package.modules:
            for source in module.files:
                if source.kind not in {"header", "private header"}:
                    continue
                raw_exposures = source.front.get("exposes", {})
                if not isinstance(raw_exposures, dict):
                    continue
                for key, value in raw_exposures.items():
                    if not _valid_exposure_spelling(key) or not _valid_exposure_spelling(value):
                        continue
                    exposure = _SemanticExposure(
                        module,
                        source,
                        tuple(key.split(".")),
                        value,
                        _front_mapping_line(source, key),
                    )
                    self.exposures.append(exposure)
                    self.exposures_by_module.setdefault(module.path, []).append(exposure)

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

    def root_exposures(self) -> list[_SemanticExposure]:
        return [
            exposure
            for exposure in self.exposures
            if exposure.module.path == "" and exposure.target is not None
        ]

    def reachable_exposures(
        self,
        roots: Iterable[_SemanticExposure] | None = None,
    ) -> list[_SemanticExposure]:
        result: list[_SemanticExposure] = []
        pending = list(self.root_exposures() if roots is None else roots)
        seen: set[_SemanticExposure] = set()
        while pending:
            exposure = pending.pop()
            if exposure in seen:
                continue
            seen.add(exposure)
            result.append(exposure)
            pending.extend(exposure.dependencies)
            target = exposure.target
            if target is not None and target.package is self.package and target.kind == "module" and target.module is not None:
                pending.extend(
                    candidate
                    for candidate in self.exposures_by_module.get(target.module.path, [])
                    if candidate.target is not None
                )
        return result

    def public_interfaces(self) -> list[_SemanticInterface]:
        return _semantic_unique(
            exposure.target.interface
            for exposure in self.root_exposures()
            if exposure.target is not None
            and exposure.target.kind == "interface"
            and exposure.target.interface is not None
        )

    def public_item_paths(self) -> list[tuple[_SemanticTarget, str]]:
        result: list[tuple[_SemanticTarget, str]] = []
        for exposure in self.root_exposures():
            target = exposure.target
            if (
                target is None
                or target.kind != "interface"
                or target.interface is None
            ):
                continue
            result.extend(
                (item, f"{exposure.name}.{item.name}")
                for item in self.interface_items(target.interface)
            )
        return result

    def public_items(self) -> list[_SemanticTarget]:
        return _semantic_unique(target for target, _path in self.public_item_paths())


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
        self.alias_declarations: list[_SemanticAlias] = []
        self.prelude_names: set[str] = set()
        if self.model.package.edition == CURRENT_EDITION:
            selected = source.front.get("prelude", list(EDITION_PRELUDE))
            if isinstance(selected, list):
                self.prelude_names = {
                    name for name in selected if isinstance(name, str) and name in EDITION_PRELUDE
                }
            for name in sorted(self.prelude_names):
                self.aliases[name] = _SemanticAlias(
                    name, EDITION_PRELUDE[name], source, False, prelude=True
                )
        declarations: list[_SemanticAlias] = []
        if isinstance(raw_aliases, dict):
            for name, value in raw_aliases.items():
                if isinstance(name, str) and isinstance(value, str):
                    purl = value.startswith("pkg:") and context != "workspace decision"
                    declarations.append(_SemanticAlias(name, value, source, purl))
        raw_use = source.front.get("use", {})
        if isinstance(raw_use, dict):
            for prefix, continuations in raw_use.items():
                if not isinstance(prefix, str) or not isinstance(continuations, list):
                    continue
                for continuation in continuations:
                    if not isinstance(continuation, str) or not continuation:
                        continue
                    local = continuation.rsplit(".", 1)[-1]
                    declarations.append(
                        _SemanticAlias(
                            local,
                            f"{prefix}.{continuation}",
                            source,
                            False,
                            derived=True,
                        )
                    )
        self.alias_declarations = declarations
        for alias in declarations:
            # An included edition spelling stays reserved even when a collision
            # is also diagnosed; duplicate user declarations are never order-dependent.
            if alias.name not in self.aliases:
                self.aliases[alias.name] = alias

    def _reference_parts(self, reference: str) -> list[str]:
        if self.context == "workspace decision" and reference.startswith("pkg:quoll/"):
            for member in self.checker.workspace_members:
                if reference == member.id:
                    return [member.id]
                if reference.startswith(member.id + "."):
                    rest = reference[len(member.id) + 1 :]
                    return [member.id, *rest.split(".")]
        return reference.split(".")

    def resolve(
        self,
        reference: str,
        *,
        include_implemented: bool = True,
        allow_parent: bool = False,
        relation: bool = False,
        alias_stack: tuple[str, ...] = (),
    ) -> _SemanticResolution:
        parts = [part.strip() for part in self._reference_parts(reference)]
        if (
            self.context == "workspace decision"
            or not parts
            or parts[0] in self.aliases
            or any(not part for part in parts)
        ):
            return self._resolve_structural(
                reference,
                include_implemented=include_implemented,
                allow_parent=allow_parent,
                relation=relation,
                alias_stack=alias_stack,
            )
        if len(parts) > 1 and parts[0] == self.model.package.name:
            root = next(
                (module for module in self.model.package.modules if module.path == ""),
                None,
            )
            if root is None:
                return _SemanticResolution(
                    status="unresolved", detail="package has no root module"
                )
            public = self._exposure_continuation(root, parts[1:], external=True)
            matching_dependencies = [
                self.model.dependency_targets[id(selector)]
                for selector in self.model.package.dependencies
                if selector.id.rsplit("/", 1)[-1] == self.model.package.name
            ]
            if matching_dependencies:
                return self._merge(
                    public,
                    *(
                        self._dependency_continuation(dependency, parts[1:])
                        for dependency in matching_dependencies
                    ),
                )
            return public
        return self._resolve_structural(
            reference,
            include_implemented=include_implemented,
            allow_parent=allow_parent,
            relation=relation,
            alias_stack=alias_stack,
        )

    def _resolve_structural(
        self,
        reference: str,
        *,
        include_implemented: bool = True,
        allow_parent: bool = False,
        relation: bool = False,
        alias_stack: tuple[str, ...] = (),
    ) -> _SemanticResolution:
        parts = [part.strip() for part in self._reference_parts(reference)]
        if not reference or any(not part for part in parts):
            return _SemanticResolution(status="form", detail="reference has an empty name segment")
        if parts[0] in self.aliases:
            base = self._resolve_alias(parts[0], alias_stack)
            if base.status != "ok":
                return base
            if len(base.targets) != 1:
                return _SemanticResolution(status="ambiguous", detail="alias does not identify one target")
            return self._continue(base.targets[0], parts[1:], edition=base.edition)
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

    def _first_candidates(
        self,
        parts: list[str],
        include_implemented: bool,
        allow_parent: bool,
    ) -> list[_SemanticTarget]:
        name = parts[0]
        if self.context == "workspace decision":
            members = []
            for member in self.checker.workspace_members:
                if name not in {member.name, member.id}:
                    continue
                root = next((module for module in member.modules if module.path == ""), None)
                if root is not None:
                    members.append(_SemanticTarget("member", member, member.name, module=root))
            return members
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
        dependencies = [
            self.model.dependency_targets[id(selector)]
            for selector in self.model.package.dependencies
            if selector.id.rsplit("/", 1)[-1] == name
        ]
        return [*modules, *dependencies]

    def _merge(self, *resolutions: _SemanticResolution) -> _SemanticResolution:
        successful_resolutions = [resolution for resolution in resolutions if resolution.status == "ok"]
        if len(successful_resolutions) == 1:
            return successful_resolutions[0]
        successful: list[_SemanticTarget] = []
        seen: set[tuple] = set()
        for resolution in successful_resolutions:
            for target in resolution.targets:
                key = self.checker._target_key(target)
                if key not in seen:
                    seen.add(key)
                    successful.append(target)
        if len(successful) == 1:
            return _SemanticResolution(successful)
        if len(successful) > 1:
            return _SemanticResolution(status="ambiguous", detail="name identifies multiple targets without precedence")
        for status in ("ambiguous", "alias-cycle", "exposure-cycle", "sight", "wrong-dependency", "form", "unavailable"):
            match = next((resolution for resolution in resolutions if resolution.status == status), None)
            if match is not None:
                return match
        return next(
            (resolution for resolution in resolutions if resolution.status == "unresolved"),
            _SemanticResolution(status="unresolved", detail="no target bears this name"),
        )

    def _exposure_continuation(
        self,
        module: Module,
        parts: list[str],
        *,
        external: bool,
        model: "_SemanticModel | None" = None,
    ) -> _SemanticResolution:
        model = model or self.model
        exposures = [
            exposure
            for exposure in model.exposures_by_module.get(module.path, [])
            if len(exposure.key) <= len(parts) and tuple(parts[: len(exposure.key)]) == exposure.key
        ]
        if not exposures:
            return _SemanticResolution(status="unresolved", detail="no exposure bears this path")
        resolutions: list[_SemanticResolution] = []
        for exposure in exposures:
            resolution = self.checker._resolve_exposure(exposure)
            if self.checker._exposure_resolving and self.checker._exposure_resolving[-1] is not exposure:
                self.checker._exposure_resolving[-1].dependencies.add(exposure)
            if resolution.status != "ok" or len(resolution.targets) != 1:
                resolutions.append(resolution)
                continue
            target = resolution.targets[0]
            provenance = (
                exposure
                if target.package is model.package
                else target.exposure or exposure
            )
            target = replace(
                target,
                external=target.external or external,
                exposure=provenance,
                exposure_chain=(exposure, *target.exposure_chain),
            )
            if not external and module is self.module and not self._visible(target, True, False):
                resolutions.append(
                    _SemanticResolution(status="sight", detail="exposure target is outside the author's sight")
                )
                continue
            rest = parts[len(exposure.key) :]
            if external and rest and target.kind == "module":
                resolutions.append(self._module_continuation(target, rest, dependency=True))
                continue
            continued = self._continue(target, rest)
            if continued.status == "ok":
                continued = _SemanticResolution(
                    [
                        replace(
                            candidate,
                            external=candidate.external or external,
                            exposure=provenance,
                            exposure_chain=target.exposure_chain,
                        )
                        for candidate in continued.targets
                    ]
                )
            resolutions.append(continued)
        return self._merge(*resolutions)

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
        if target.kind == "member":
            return self.context == "workspace decision" and any(
                target.package is member for member in self.checker.workspace_members
            )
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

    def _continue(
        self,
        target: _SemanticTarget,
        rest: list[str],
        *,
        edition: bool = False,
    ) -> _SemanticResolution:
        if not rest:
            return _SemanticResolution([target], edition=edition)
        if target.kind == "module":
            return self._module_continuation(target, rest, dependency=target.external)
        if target.kind == "dependency":
            return self._dependency_continuation(target, rest)
        if target.kind == "member":
            return self._module_continuation(target, rest, dependency=True)
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
        if target.kind in {"item", "body-item", "decision", "edition-item"}:
            return _SemanticResolution(status="form", detail="no segment may follow this target", edition=edition)
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
        if dependency:
            return self._exposure_continuation(
                module, rest, external=True, model=model
            )
        if rest[0] == "default" and len(rest) > 1:
            return _SemanticResolution(
                status="form", detail="no segment may follow a module's default"
            )
        exposed = self._exposure_continuation(module, rest, external=False, model=model)
        if rest[0] == "default":
            candidates = [
                interface
                for interface in model.by_module.get(module.path, [])
                if interface.default
            ]
        else:
            candidates = [
                interface
                for interface in model.by_module.get(module.path, [])
                if not interface.default and interface.name == rest[0]
            ]
            default = model.default_interface(module)
            if default is not None:
                items = _semantic_unique(item for item in model.interface_items(default) if item.name == rest[0])
                if items:
                    if len(rest) > 1:
                        structural = _SemanticResolution(status="form", detail="no segment may follow an item")
                        return self._merge(structural, exposed)
                    if candidates or len(items) > 1:
                        structural = _SemanticResolution(
                            status="ambiguous",
                            detail="name is both an interface and a default item" if candidates else "default path names multiple included items",
                        )
                        return self._merge(structural, exposed)
                    return self._merge(_SemanticResolution(items), exposed)
        targets = [self._interface_target_for(model, interface) for interface in candidates]
        visible = [candidate for candidate in targets if self._visible(candidate, True, False)]
        if targets and not visible:
            structural = _SemanticResolution(status="sight", detail="interface is private at this point")
            return self._merge(structural, exposed)
        targets = _semantic_unique(visible)
        if not targets:
            structural = _SemanticResolution(status="unresolved", detail="module has no interface or default item with this name")
            return self._merge(structural, exposed)
        if len(targets) > 1:
            structural = _SemanticResolution(status="ambiguous", detail="module path has multiple targets")
            return self._merge(structural, exposed)
        return self._merge(self._continue(targets[0], rest[1:]), exposed)

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
        if supplied is not None and id(supplied) in self.checker._preparing:
            return _SemanticResolution(
                status="unavailable",
                detail="dependency preparation is cyclic",
            )
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
            return _SemanticResolution(status="unavailable", detail="dependency surface is not supplied")
        model = self.checker.models[id(supplied)]
        root = next((module for module in supplied.modules if module.path == ""), None)
        if root is None:
            return _SemanticResolution(status="unresolved", detail="dependency has no root module")
        external = _SemanticTarget("module", supplied, root.name, module=root, external=True)
        return self._module_continuation(external, rest, dependency=True)

    def _resolve_prelude_alias(self, alias: _SemanticAlias) -> _SemanticResolution:
        interface_name = "graph" if alias.name in {"workspace", "package"} else "kernel"

        def canonical(model: _SemanticModel) -> list[_SemanticTarget]:
            return [
                model.item_target(interface, item)
                for interface in model.interfaces
                if interface.module.path == "model" and interface.name == interface_name
                for item in interface.source.items
                if item.name == alias.name
            ]

        local = (
            _semantic_unique(canonical(self.model))
            if self.model.package.id == LANGUAGE_PACKAGE_ID
            else []
        )
        if len(local) == 1:
            return _SemanticResolution(local, edition=True)
        if len(local) > 1:
            return _SemanticResolution(status="ambiguous", detail="edition alias has multiple local target items")
        foreign = _semantic_unique(
            target
            for model in self.checker.models.values()
            if model is not self.model and model.package.id == LANGUAGE_PACKAGE_ID
            for target in canonical(model)
        )
        if len(foreign) == 1:
            return _SemanticResolution(foreign, edition=True)
        if len(foreign) > 1:
            return _SemanticResolution(status="ambiguous", detail="edition alias has multiple target items")
        return _SemanticResolution(
            [_SemanticTarget("edition-item", self.model.package, alias.name, external=True)],
            edition=True,
        )

    def _resolve_alias(self, name: str, stack: tuple[str, ...]) -> _SemanticResolution:
        alias = self.aliases[name]
        if name in stack:
            return _SemanticResolution(status="alias-cycle", detail=" -> ".join((*stack, name)))
        if alias.prelude:
            return self._resolve_prelude_alias(alias)
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
        if self.context == "workspace decision":
            allowed = {"member", "module", "interface", "item", "edition-item"}
        elif self.context == "interface":
            allowed = {"module", "interface", "item", "edition-item"}
        else:
            allowed = {"module", "interface", "item", "body-item", "edition-item"}
        if len(base.targets) != 1 or base.targets[0].kind not in allowed:
            return _SemanticResolution(status="form", detail="qualified alias must name one visible module, interface or item")
        return base


class _SemanticChecker:
    def __init__(
        self,
        package: Package,
        dependency_packages: Iterable[Package],
        _prepared: dict[int, "_SemanticChecker"] | None = None,
        _preparing: set[int] | None = None,
    ) -> None:
        self.package = package
        self.dependencies = list(dependency_packages)
        self.models: dict[int, _SemanticModel] = {id(package): _SemanticModel(package)}
        self.model = self.models[id(package)]
        self._exposure_resolving: list[_SemanticExposure] = []
        self._exposure_cycles: set[_SemanticExposure] = set()
        prepared = {} if _prepared is None else _prepared
        preparing = set() if _preparing is None else _preparing
        self._preparing = preparing
        prepared[id(package)] = self
        preparing.add(id(package))
        for dependency in self.dependencies:
            if id(dependency) in prepared:
                self.models[id(dependency)] = prepared[id(dependency)].model
                continue
            supplied = [
                candidate
                for candidate in self.dependencies
                if candidate is not dependency
            ]
            prepared_dependency = _SemanticChecker(
                dependency, supplied, prepared, preparing
            )
            self.models[id(dependency)] = prepared_dependency.model
            prepared_dependency._resolve_implements()
            prepared_dependency._resolve_includes()
            prepared_dependency._resolve_exposures()
        preparing.discard(id(package))
        self.workspace_members = package.workspace_members
        for member in self.workspace_members:
            prepared = _SemanticChecker(member, ())
            prepared._resolve_implements()
            prepared._resolve_includes()
            prepared._resolve_exposures()
            self.models[id(member)] = prepared.model
        self.findings: list[Finding] = []
        self.resolved_sites: list[tuple[_SemanticSite, _SemanticResolution]] = []
        self.unavailable_sites: list[tuple[_SemanticSite, _SemanticResolution]] = []
        self.include_targets: dict[
            tuple[_SemanticInterface, _SemanticInterface], _SemanticTarget
        ] = {}
        self.used_modules: dict[str, set[str]] = {module.path: set() for module in package.modules}
        self.used_interfaces: dict[str, set[_SemanticInterface]] = {module.path: set() for module in package.modules}
        self.declared_uses: dict[str, set[str]] = {}
        self.resolvers: dict[str, _SemanticResolver] = {}

    def error(self, rule: str, source: SourceFile | str, subject: str, detail: str, line: int = 0) -> None:
        self.findings.append(Finding(rule, "error", source if isinstance(source, str) else source.path, subject, detail, line))

    def resolver_for(self, source: SourceFile, module: Module) -> _SemanticResolver:
        owner = self.model.by_source.get(source.path)
        context = (
            "interface"
            if owner is not None
            else "workspace decision"
            if source.kind == "workspace decisions"
            else "decision"
            if source.kind == "decisions"
            else "body"
        )
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

    def run(self, *, check_public_closure: bool = True) -> list[Finding]:
        self._check_names_and_leads()
        self._resolve_implements()
        self._resolve_includes()
        self._check_exposure_names()
        self._resolve_exposures()
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
        if check_public_closure:
            self._check_public_closure()
        self._check_independent_modules()
        existing = {finding.key for finding in self.package.findings}
        return sorted(
            {finding for finding in self.findings if finding.key not in existing},
            key=lambda finding: finding.sort_key,
        )

    def _check_names_and_leads(self) -> None:
        if self.package.workspace is None and not _SEMANTIC_IDENTIFIER.fullmatch(self.package.name):
            self.error("semantic.identifiers", self.package.name, self.package.name, "package name is not a lowercase ASCII identifier")
        for module in self.package.modules:
            if self.package.workspace is not None and module.path == "":
                continue
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
                children = [
                    child
                    for child in self.package.modules
                    if child.path and self._parent_module_path(child.path) == module.path and child.name == name
                ]
                if children and any(not interface.default for interface in interfaces):
                    interface = next(interface for interface in interfaces if not interface.default)
                    self.error("semantic.unique-names", interface.source, name, "named interface collides with a sibling module")
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
                    if len(resolution.targets) == 1:
                        self.include_targets[(interface, included)] = resolution.targets[0]

    def _check_exposure_names(self) -> None:
        for module in self.package.modules:
            declared: dict[tuple[str, ...], list[_SemanticExposure]] = {}
            for exposure in self.model.exposures_by_module.get(module.path, []):
                declared.setdefault(exposure.key, []).append(exposure)
            for exposures in declared.values():
                if len(exposures) > 1:
                    for exposure in exposures[1:]:
                        self.error(
                            "semantic.exposure-unique",
                            exposure.source,
                            exposure.name,
                            "exposure path is declared more than once by one module",
                            exposure.line,
                        )

    def _resolve_exposure(self, exposure: _SemanticExposure) -> _SemanticResolution:
        if exposure.resolution is not None:
            return exposure.resolution
        if exposure in self._exposure_resolving:
            start = self._exposure_resolving.index(exposure)
            self._exposure_cycles.update(self._exposure_resolving[start:])
            return _SemanticResolution(status="exposure-cycle", detail="exposure declarations form a cycle")
        self._exposure_resolving.append(exposure)
        try:
            resolver = self.resolver_for(exposure.source, exposure.module)
            resolution = resolver.resolve(exposure.value)
            if resolution.status == "ok":
                if len(resolution.targets) != 1 or resolution.targets[0].kind != "interface":
                    resolution = _SemanticResolution(
                        status="form",
                        detail="exposure target must be one whole interface",
                    )
            exposure.resolution = resolution
            if resolution.status == "ok":
                self._exposure_cycles.discard(exposure)
            return resolution
        finally:
            self._exposure_resolving.pop()

    def _resolve_exposures(self) -> None:
        for exposure in self.model.exposures:
            self._resolve_exposure(exposure)
        for exposure in self.model.exposures:
            resolution = exposure.resolution
            if resolution is None:
                continue
            if exposure in self._exposure_cycles:
                self.error(
                    "semantic.exposure-cycle",
                    exposure.source,
                    exposure.name,
                    resolution.detail or "exposure declarations form a cycle",
                    exposure.line,
                )
                continue
            if resolution.status != "ok":
                self.error(
                    "semantic.exposure-target",
                    exposure.source,
                    exposure.value,
                    resolution.detail or "exposure does not resolve to one visible whole interface",
                    exposure.line,
                )
                continue
        self._check_composed_exposure_paths()

    def _check_composed_exposure_paths(self) -> None:
        paths: dict[tuple[int, str, str], list[tuple[_SemanticExposure, _SemanticTarget, Package]]] = {}

        def visit(
            model: _SemanticModel,
            module: Module,
            prefix: str,
            stack: frozenset[tuple[int, str]],
            namespace: Package,
            namespace_root: str,
        ) -> None:
            marker = (id(model.package), module.path)
            if marker in stack:
                return
            next_stack = stack | {marker}
            for exposure in model.exposures_by_module.get(module.path, []):
                target = exposure.target
                if target is None:
                    continue
                path = f"{prefix}.{exposure.name}" if prefix else exposure.name
                paths.setdefault((id(namespace), namespace_root, path), []).append(
                    (exposure, target, model.package)
                )
                if target.kind == "module" and target.module is not None:
                    target_model = self.models.get(id(target.package), model)
                    visit(
                        target_model,
                        target.module,
                        path,
                        next_stack,
                        namespace,
                        namespace_root,
                    )
                elif target.kind == "interface" and target.interface is not None:
                    for item in model.interface_items(target.interface):
                        item_path = f"{path}.{item.name}"
                        paths.setdefault((id(namespace), namespace_root, item_path), []).append(
                            (exposure, item, model.package)
                        )

        for model in self.models.values():
            for module in model.package.modules:
                visit(model, module, "", frozenset(), model.package, module.path)
        for (_package_id, _namespace_root, path), declarations in paths.items():
            distinct = {self._target_key(target) for _, target, _ in declarations}
            if len(distinct) < 2:
                continue
            for exposure, _target, owner in declarations:
                if owner is not self.package:
                    continue
                self.error(
                    "semantic.exposure-unique",
                    exposure.source,
                    exposure.name,
                    f"composed exposure path {path} identifies multiple targets",
                    exposure.line,
                )

    @staticmethod
    def _same_target(left: _SemanticTarget, right: _SemanticTarget) -> bool:
        return _SemanticChecker._target_key(left) == _SemanticChecker._target_key(right)

    @staticmethod
    def _target_key(target: _SemanticTarget) -> tuple:
        return (
            id(target.package),
            target.kind,
            target.module.path if target.module is not None else None,
            target.interface.source.path if target.interface is not None else None,
            id(target.item) if target.item is not None else None,
            target.decision.id if target.decision is not None else None,
            target.dependency.raw if target.dependency is not None else None,
        )

    @staticmethod
    def _parent_module_path(path: str) -> str:
        return path.rsplit("/", 1)[0] if "/" in path else ""

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
            if source.kind not in {"header", "private header", "body", "decisions", "workspace decisions"}:
                continue
            module = self.package.module_map[source.module]
            resolver = self.resolver_for(source, module)
            declarations = resolver.alias_declarations
            if not declarations:
                continue
            local_names = self._local_names(resolver)
            counts = {
                name: sum(alias.name == name for alias in declarations)
                for name in {alias.name for alias in declarations}
            }
            for alias in declarations:
                if not alias.derived and not _SEMANTIC_IDENTIFIER.fullmatch(alias.name):
                    self.error("semantic.alias-unique", source, alias.name, "rename alias is not a lowercase ASCII identifier")
                if counts[alias.name] > 1:
                    self.error("semantic.alias-unique", source, alias.name, "explicit and derived aliases declare the same local name more than once")
                if alias.name in resolver.prelude_names:
                    self.error("semantic.alias-unique", source, alias.name, "alias collides with an included edition prelude spelling")
                if alias.name in local_names:
                    self.error("semantic.alias-unique", source, alias.name, "alias collides with a visible dependency or local reference name")
                if resolver.aliases.get(alias.name) is not alias:
                    continue
                resolution = resolver._resolve_alias(alias.name, ())
                if resolution.status == "alias-cycle":
                    path = resolution.detail.split(" -> ")
                    repeated = path[-1]
                    participants = path[path.index(repeated) : -1] if repeated in path[:-1] else []
                    if alias.name in participants:
                        self.error("semantic.alias-cycle", source, alias.name, resolution.detail)
                elif resolution.status == "ambiguous":
                    self.error("semantic.alias-ambiguous", source, alias.name, resolution.detail)
                elif resolution.status in {"unresolved", "form", "sight", "wrong-dependency"}:
                    self.error("semantic.alias-target", source, alias.name, resolution.detail)

    def _local_names(self, resolver: _SemanticResolver) -> set[str]:
        if resolver.context == "workspace decision":
            return {member.name for member in self.workspace_members}
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
        for exposure in self.model.exposures_by_module.get(resolver.module.path, []):
            names.add(exposure.key[0])
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
                if source.kind not in {"header", "private header", "body", "decisions", "workspace decisions"}:
                    continue
                owner = self.model.by_source.get(source.path)
                context = (
                    "interface"
                    if owner is not None
                    else "workspace decision"
                    if source.kind == "workspace decisions"
                    else "decision"
                    if source.kind == "decisions"
                    else "body"
                )
                ranges: list[tuple[int, int, int]] = []
                if source.kind in {"decisions", "workspace decisions"}:
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
                if source.kind in {"decisions", "workspace decisions"}:
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
            if resolution.status == "unavailable":
                self.unavailable_sites.append((site, resolution))
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

    def _decision_item_references(self, text: str) -> tuple[list[tuple[str, bool]], str]:
        """Return bracketed item references and their joining punctuation."""

        references = [(reference, False) for reference in extract_refs(text)]
        shape = re.sub(r"\[[^\[\]\n]+\](?!\()", "\x00", text.strip())
        return references, shape

    def _resolve_decision_reference(
        self,
        resolver: _SemanticResolver,
        reference: str,
        *,
        bare: bool,
    ) -> _SemanticResolution:
        return resolver.resolve(reference)

    def _check_decision_statements(self) -> None:
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
                    references, shape = self._decision_item_references(stated_by)
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
                    for reference, bare in references:
                        resolution = self._resolve_decision_reference(
                            resolver, reference, bare=bare
                        )
                        if resolution.status != "ok" or not any(
                            target.kind in {"item", "body-item", "edition-item"}
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
            if resolution.edition:
                continue
            for target in resolution.targets:
                interface = target.interface if target.kind in {"interface", "item"} else None
                if interface is None or interface.package is not self.package:
                    continue
                if interface.module is site.module:
                    continue
                self.used_modules[site.module.path].add(interface.module.path)
                self.used_interfaces[site.module.path].add(interface)

    def _interface_graphs(
        self,
    ) -> tuple[
        dict[_SemanticInterface, set[_SemanticInterface]],
        dict[_SemanticInterface, set[_SemanticInterface]],
    ]:
        include_graph = {interface: set(interface.includes) for interface in self.model.interfaces}
        reference_graph = {interface: set() for interface in self.model.interfaces}
        for site, resolution in self.resolved_sites:
            if site.owner is None:
                continue
            for target in resolution.targets:
                if target.interface is None:
                    continue
                # An item naming another item on its own interface is not an
                # interface dependency.  Explicit interface self-references and
                # inclusion edges remain in the graph and are still diagnosed.
                if target.kind == "item" and target.interface is site.owner:
                    continue
                reference_graph[site.owner].add(target.interface)
        return include_graph, reference_graph

    def _check_cycles(self) -> None:
        include_graph, reference_graph = self._interface_graphs()
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
        resolver = self.resolver_for(root.body, root)
        for item in root.body.items:
            parsed = self._parse_complete_use(item, resolver)
            if parsed is None:
                continue
            subject, expected = parsed
            if subject in declarations:
                ambiguous.add(subject)
            else:
                declarations[subject] = (item, expected)
        for subject in ambiguous:
            declarations.pop(subject, None)
        self.declared_uses = {
            subject: expected for subject, (_, expected) in declarations.items()
        }
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

    @staticmethod
    def _edition_contract_item(target: _SemanticTarget, name: str) -> bool:
        if target.kind == "edition-item":
            return target.name == name
        return (
            target.kind == "item"
            and target.item is not None
            and target.item.name == name
            and target.interface is not None
            and target.interface.module.name == "model"
        )

    def _contract_reference(
        self, resolver: _SemanticResolver, reference: str, name: str
    ) -> bool:
        resolution = resolver.resolve(reference)
        return resolution.status == "ok" and any(
            self._edition_contract_item(target, name) for target in resolution.targets
        )

    def _parse_complete_use(
        self, item: Item, resolver: _SemanticResolver
    ) -> tuple[str, set[str]] | None:
        text = item.statements.strip()
        references = extract_refs(text)
        uses_indices = [
            index
            for index, reference in enumerate(references)
            if self._contract_reference(resolver, reference, "uses")
        ]
        if len(uses_indices) != 1:
            return None
        uses_index = uses_indices[0]
        if uses_index < 1 or not references[uses_index - 1].endswith(".default"):
            return None
        subject_name = references[uses_index - 1][: -len(".default")]
        subject = self._direct_default_module(subject_name)
        if subject is None:
            return None
        trailing = references[uses_index + 1 :]
        if len(trailing) == 1 and self._contract_reference(resolver, trailing[0], "interface"):
            if not re.search(rf"\bno\s+\[{re.escape(trailing[0])}\]", text):
                return None
            return subject, set()
        if (
            not text.endswith("alone")
            or len(trailing) < 3
            or not self._contract_reference(resolver, trailing[0], "interface")
            or not self._contract_reference(resolver, trailing[1], "module")
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

    def _available_public_targets(self, model: _SemanticModel) -> set[tuple]:
        available: set[tuple] = set()
        for exposure in model.reachable_exposures():
            target = exposure.target
            if (
                target is None
                or target.kind != "interface"
                or target.interface is None
            ):
                continue
            available.add(self._target_key(target))
            available.update(
                self._target_key(item)
                for item in model.interface_items(target.interface)
            )
        return available

    def _target_available(self, target: _SemanticTarget, available: set[tuple]) -> bool:
        if target.kind == "edition-item":
            return True
        if target.kind == "dependency":
            return target.dependency in self.package.dependencies
        if target.kind == "member":
            return any(target.package is member for member in self.workspace_members)
        if target.kind not in {"module", "interface", "item"}:
            return False
        if target.kind == "module":
            return target.module is not None and target.module.path == ""
        model = self.models.get(id(target.package))
        if model is None:
            return False
        return self._target_key(target) in self._available_public_targets(model)

    @staticmethod
    def _exposure_descriptor(exposure: _SemanticExposure) -> tuple:
        return (
            exposure.module.path,
            exposure.source.path,
            exposure.key,
            exposure.value,
        )

    def _exposure_scope_for_target(self, target: _SemanticTarget) -> list[_SemanticExposure]:
        """Return only root chains and descendants needed for one foreign target."""

        exposures = {
            self._exposure_descriptor(exposure): exposure
            for exposure in self.model.reachable_exposures()
        }
        goals: list[_SemanticExposure] = []
        if target.exposure is not None:
            goal = exposures.get(self._exposure_descriptor(target.exposure))
            if goal is not None:
                goals.append(goal)
        if not goals:
            direct = [
                exposure
                for exposure in exposures.values()
                if exposure.target is not None
                and self._same_target(exposure.target, target)
            ]
            goals.extend(direct)
        if not goals and target.kind == "item":
            for exposure in exposures.values():
                exposed = exposure.target
                if exposed is None or exposed.kind != "interface" or exposed.interface is None:
                    continue
                if any(self._same_target(item, target) for item in self.model.interface_items(exposed.interface)):
                    goals.append(exposure)

        related: set[_SemanticExposure] = set()

        def collect_ancestors(
            exposure: _SemanticExposure,
            stack: frozenset[_SemanticExposure],
        ) -> bool:
            if exposure in goals:
                related.add(exposure)
                return True
            if exposure in stack:
                return False
            children = list(exposure.dependencies)
            exposed = exposure.target
            if (
                exposed is not None
                and exposed.package is self.package
                and exposed.kind == "module"
                and exposed.module is not None
            ):
                children.extend(
                    candidate
                    for candidate in self.model.exposures_by_module.get(exposed.module.path, [])
                    if candidate.target is not None
                )
            found = False
            for child in children:
                if collect_ancestors(child, stack | {exposure}):
                    found = True
            if found:
                related.add(exposure)
            return found

        for root in self.model.root_exposures():
            collect_ancestors(root, frozenset())
        scope = set(related)
        for goal in goals:
            scope.update(self.model.reachable_exposures([goal]))
        return [
            exposure
            for exposure in self.model.reachable_exposures()
            if exposure in scope
        ]

    def _compute_public_closure(
        self,
        exposure_scope: Iterable[_SemanticExposure] | None = None,
    ) -> tuple[dict[tuple[str, int, str], tuple[_SemanticSite, _SemanticResolution]], PublicReading]:
        sources: dict[str, SourceFile] = {}
        contract_sources: set[str] = set()
        module_paths: set[str] = set()
        foreign_units: dict[tuple[str, str], PublicUnit] = {}
        foreign_modules: dict[tuple[str, str], PublicModule] = {}
        foreign_checkers: dict[int, _SemanticChecker] = {}
        foreign_readings: dict[tuple, PublicReading] = {}
        selected_exposures: list[_SemanticExposure] = []
        selected_exposure_set: set[_SemanticExposure] = set()

        def add_module(path: str) -> None:
            while path:
                module_paths.add(path)
                path = self._parent_module_path(path)

        def merge_foreign(
            target: _SemanticTarget,
            through: _SemanticExposure | None = None,
        ) -> None:
            if through is None and target.exposure_chain:
                for exposure in target.exposure_chain:
                    merge_foreign(target, exposure)
                return
            if through is None:
                package = target.package
            else:
                owner = next(
                    (
                        model
                        for model in self.models.values()
                        if through in model.exposures
                    ),
                    None,
                )
                if owner is None:
                    return
                package = owner.package
                target = replace(target, exposure=through)
            if id(package) not in foreign_checkers:
                supplied = [
                    candidate for candidate in self.dependencies if candidate is not package
                ]
                checker = _SemanticChecker(package, supplied)
                checker.run(check_public_closure=False)
                foreign_checkers[id(package)] = checker
            checker = foreign_checkers[id(package)]
            scope = checker._exposure_scope_for_target(target)
            if not scope:
                return
            key = (
                id(package),
                tuple(sorted(self._exposure_descriptor(exposure) for exposure in scope)),
            )
            if key not in foreign_readings:
                _selected, foreign_readings[key] = checker._compute_public_closure(scope)
            reading = foreign_readings[key]
            for unit in reading.units:
                key = (unit.package_id, unit.path)
                previous = foreign_units.get(key)
                if previous is not None:
                    unit = replace(
                        previous,
                        dependencies=tuple(
                            sorted(set(previous.dependencies) | set(unit.dependencies))
                        ),
                        exposures=tuple(
                            sorted(set(previous.exposures) | set(unit.exposures))
                        ),
                    )
                foreign_units[key] = unit
            for module in reading.modules:
                foreign_modules[(module.package_id, module.path)] = module

        def add_source(source: SourceFile, *, contract: bool = True) -> None:
            if source.path not in sources:
                sources[source.path] = source
                add_module(source.module)
            if not contract or source.path in contract_sources:
                return
            contract_sources.add(source.path)
            owner = self.model.by_source.get(source.path)
            if owner is None:
                return
            pending = list(owner.includes)
            seen: set[_SemanticInterface] = set()
            while pending:
                included = pending.pop()
                if included in seen:
                    continue
                seen.add(included)
                if included.package is self.package:
                    add_source(included.source)
                    pending.extend(included.includes)
                    continue
                target = self.include_targets.get((owner, included))
                if target is None:
                    target = _SemanticTarget(
                        "interface",
                        included.package,
                        included.name,
                        module=included.module,
                        interface=included,
                        source=included.source,
                        external=True,
                    )
                merge_foreign(target)

        def add_exposure(exposure: _SemanticExposure) -> None:
            if exposure in selected_exposure_set:
                return
            selected_exposure_set.add(exposure)
            selected_exposures.append(exposure)
            add_source(exposure.source, contract=False)
            target = exposure.target
            if target is None:
                return
            if target.package is not self.package:
                if self._target_available(target, set()):
                    merge_foreign(target)
                return
            if target.source is not None:
                add_source(target.source)

        initial_exposures = (
            self.model.reachable_exposures()
            if exposure_scope is None
            else list(exposure_scope)
        )
        for exposure in initial_exposures:
            if any(source is exposure.source for source in self.package.files):
                add_exposure(exposure)
            elif exposure.target is not None and self._target_available(exposure.target, set()):
                merge_foreign(exposure.target)

        available = self._available_public_targets(self.model)
        selected: dict[tuple[str, int, str], tuple[_SemanticSite, _SemanticResolution]] = {}
        changed = True
        while changed:
            changed = False
            before = len(sources)
            for site, resolution in self.resolved_sites:
                if site.source.path not in sources:
                    continue
                key = (site.source.path, site.line, site.reference)
                selected[key] = (site, resolution)
                if resolution.edition:
                    continue
                for target in resolution.targets:
                    if not self._target_available(target, available):
                        continue
                    if target.package is not self.package:
                        if target.kind not in {"dependency", "member"}:
                            merge_foreign(target)
                        continue
                    for needed in self._exposure_scope_for_target(target):
                        add_exposure(needed)
                    if target.source is not None:
                        add_source(target.source)
                    if target.kind == "module" and target.module is not None:
                        add_module(target.module.path)
            changed = len(sources) != before

        own_dependencies = tuple(sorted(selector.raw for selector in self.package.dependencies))
        own_units = [
            PublicUnit(
                identity=f"{self.package.id}:source:{path}",
                path=path,
                locator=f"{self.package.id}:source:{path}",
                package_id=self.package.id,
                dependencies=own_dependencies,
                exposures=tuple(
                    sorted(
                        exposure.name
                        for exposure in selected_exposures
                        if exposure.source.path == path
                    )
                ),
                edition=self.package.edition,
                text=sources[path].text,
            )
            for path in sources
        ]
        own_modules = [
            PublicModule(
                identity=f"{self.package.id}:module:{path}",
                path=path,
                locator=f"{self.package.id}:module:{path}",
                package_id=self.package.id,
                name=path.rsplit("/", 1)[-1],
            )
            for path in module_paths
        ]
        units = sorted(
            [*own_units, *foreign_units.values()],
            key=lambda unit: (unit.package_id, unit.path),
        )
        modules = sorted(
            [*own_modules, *foreign_modules.values()],
            key=lambda module: (module.package_id, module.path),
        )
        reading = PublicReading(
            units=tuple(units),
            dependencies=own_dependencies,
            modules=tuple(modules),
        )
        return selected, reading

    def _check_public_closure(self) -> None:
        selected, self.public_reading = self._compute_public_closure()
        available = self._available_public_targets(self.model)
        for site, resolution in selected.values():
            if resolution.edition:
                continue
            if all(self._target_available(target, available) for target in resolution.targets):
                continue
            self.error(
                "semantic.public-closure",
                site.source,
                site.reference,
                "public reading reference does not resolve from the supplied units and public dependencies",
                site.line,
            )

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
    """Return package-owned local and supplied-dependency semantic findings."""

    dependencies = tuple(dependency_packages)

    def owned_run(
        current: Package, supplied: tuple[Package, ...]
    ) -> list[Finding]:
        return [
            replace(finding, package_id=current.id)
            for finding in _SemanticChecker(current, supplied).run()
        ]

    findings = owned_run(package, dependencies)
    for dependency in dependencies:
        supplied = tuple(candidate for candidate in dependencies if candidate is not dependency)
        findings.extend(owned_run(dependency, supplied))
    return _sorted_findings(findings)


def public_reading(
    package: Package,
    dependency_packages: Iterable[Package] = (),
) -> PublicReading:
    """Collect identified canonical public units and public dependency metadata."""

    supplied = tuple(dependency_packages)
    unsupported = [candidate for candidate in (package, *supplied) if candidate.edition != CURRENT_EDITION]
    if unsupported:
        raise ValueError("public reading requires current edition 0.6.0 for every supplied package")
    checker = _SemanticChecker(package, supplied)
    checker.run()
    return checker.public_reading


@dataclass(frozen=True, order=True)
class ResolvedTargetSite:
    """One mechanically resolved dependent site and its stable target identity."""

    target: str
    path: str
    line: int
    reference: str
    context: str


@dataclass(frozen=True)
class DependentSiteEvidence:
    sites: tuple[ResolvedTargetSite, ...]
    complete: bool
    limits: tuple[str, ...] = ()


def _resolved_target_identity(target: _SemanticTarget) -> str:
    if target.kind == "edition-item":
        return f"edition:{CURRENT_EDITION}:{EDITION_PRELUDE[target.name]}"
    package = target.package.id or target.package.name
    if target.kind == "item" and target.interface is not None and target.item is not None:
        return f"{package}:item:{target.interface.module.path}:{target.interface.name}:{target.item.name}"
    if target.kind == "interface" and target.interface is not None:
        return f"{package}:interface:{target.interface.module.path}:{target.interface.name}"
    if target.kind == "module" and target.module is not None:
        return f"{package}:module:{target.module.path}"
    if target.kind == "member":
        return f"{package}:package:"
    if target.kind == "dependency" and target.dependency is not None:
        return f"{package}:dependency:{target.dependency.raw}"
    if target.kind == "body-item" and target.module is not None and target.item is not None:
        return f"{package}:body-item:{target.module.path}:{target.item.name}"
    if target.kind == "decision" and target.module is not None and target.decision is not None:
        return f"{package}:decision:{target.module.path}:{target.decision.id}"
    return f"{package}:{target.kind}:{target.name}"


def dependent_site_evidence(
    package: Package,
    dependency_packages: Iterable[Package] = (),
) -> DependentSiteEvidence:
    """Return resolved prose and relation sites; textual search remains supplemental."""

    checker = _SemanticChecker(package, dependency_packages)
    findings = checker.run()
    records: list[ResolvedTargetSite] = []
    limits: list[str] = []

    def add(site: _SemanticSite, resolution: _SemanticResolution) -> None:
        if resolution.status == "unavailable":
            limits.append(
                f"unavailable dependency surface omits {site.context} site {site.source.path}:{site.reference}"
            )
            return
        if resolution.status != "ok":
            return
        for target in resolution.targets:
            records.append(
                ResolvedTargetSite(
                    _resolved_target_identity(target),
                    site.source.path,
                    site.line,
                    site.reference,
                    site.context,
                )
            )

    for site, resolution in checker.resolved_sites:
        add(site, resolution)
    for site, resolution in checker.unavailable_sites:
        add(site, resolution)
    for module in package.modules:
        body = module.body
        if body is not None:
            resolver = checker.resolver_for(body, module)
            for reference in body.front.get("implements", []):
                if isinstance(reference, str):
                    add(
                        _SemanticSite(body, module, reference, 1, "implements"),
                        resolver.resolve(reference, include_implemented=False, allow_parent=True, relation=True),
                    )
            for item in body.items:
                if item.impl is not None:
                    add(
                        _SemanticSite(body, module, item.impl, item.line, "impl"),
                        resolver.resolve(item.impl, relation=True),
                    )
        for source in module.files:
            owner = checker.model.by_source.get(source.path)
            if owner is not None:
                resolver = checker.resolver_for(source, module)
                for reference in source.front.get("includes", []):
                    if isinstance(reference, str):
                        add(
                            _SemanticSite(source, module, reference, 1, "includes"),
                            resolver.resolve(reference, relation=True),
                        )
    for module in package.modules:
        for source in module.files:
            if source.kind not in {"header", "private header", "body", "decisions", "workspace decisions"}:
                continue
            resolver = checker.resolver_for(source, module)
            for alias in resolver.alias_declarations:
                resolution = resolver._resolve_alias(alias.name, ())
                if resolution.status == "unavailable":
                    limits.append(
                        f"unavailable dependency surface omits binding {source.path}:{alias.name}"
                    )
    for exposure in checker.model.exposures:
        resolution = checker._resolve_exposure(exposure)
        add(
            _SemanticSite(exposure.source, exposure.module, exposure.value, exposure.line, "exposes"),
            resolution,
        )

    if package.related_decisions and package.workspace is None:
        limits.append("related workspace decisions require evidence collection from the workspace root")
    if any(finding.rule.startswith("front.") for finding in package.findings):
        limits.append("malformed or absent front bindings may omit dependent sites")
    incomplete_rules = {
        "semantic.resolved",
        "semantic.ambiguous",
        "semantic.sight",
        "semantic.reference-form",
        "semantic.alias-target",
        "semantic.alias-ambiguous",
        "semantic.alias-cycle",
        "semantic.exposure-target",
        "semantic.exposure-cycle",
        "semantic.implementable",
        "semantic.includable",
        "semantic.relations",
    }
    if any(finding.rule in incomplete_rules for finding in findings):
        limits.append("sites with unresolved or invalid references are absent from mechanical evidence")
    return DependentSiteEvidence(
        sites=tuple(sorted(set(records))),
        complete=not limits,
        limits=tuple(dict.fromkeys(limits)),
    )


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
    locations = [
        _DecisionLocation(module, source, decision)
        for module in package.modules
        for source in module.files
        if source.kind in {"decisions", "workspace decisions"}
        for decision in source.decisions
    ]
    locations.extend(
        _DecisionLocation(module, source, decision)
        for module, source in package.related_decisions
        for decision in source.decisions
    )
    return locations


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


def _successor_locations(
    index: dict[tuple[str, str], list[_DecisionLocation]],
    location: _DecisionLocation,
    successor: str,
) -> list[_DecisionLocation]:
    """Resolve locally first; a pointer-only move may cross collection bounds."""

    local = index.get((location.module.path, successor), [])
    if local or not _pointer_only_stub(location.decision):
        return local
    return [
        candidate
        for locations in index.values()
        for candidate in locations
        if candidate.decision.id == successor
    ]


def _successor_cycles(
    index: dict[tuple[str, str], list[_DecisionLocation]]
) -> set[tuple[str, str]]:
    graph: dict[tuple[str, str], set[tuple[str, str]]] = {key: set() for key in index}
    for key, locations in index.items():
        _module_path, decision_id = key
        for location in locations:
            successor = location.decision.successor
            if successor is not None and successor != decision_id:
                targets = _successor_locations(index, location, successor)
                if len(targets) == 1:
                    target = targets[0]
                    graph[key].add((target.module.path, successor))

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


def _pointer_only_stub(decision: Decision) -> bool:
    if decision.active or decision.successor is None:
        return False
    fields = {key.casefold() for key in decision.fields}
    lines = [line.strip() for line in decision.text.splitlines() if line.strip()]
    one_line = len(lines) == 1 and _ONE_LINE_POINTER_STUB.fullmatch(lines[0]) is not None
    two_lines = (
        len(lines) == 2
        and re.match(r"^\*Superseded by\*[ \t]+", lines[1], re.IGNORECASE) is not None
    )
    return (
        decision.title in {"", "Superseded."}
        and fields == {"superseded by"}
        and (one_line or two_lines)
    )


def _decision_history_matches(old: Decision, current: Decision) -> bool:
    if _pointer_only_stub(current):
        # Pointer-only stubs carry no active choice whose text can be replaced.
        # A dependent pointer may migrate to the successor of its former target.
        if _pointer_only_stub(old):
            return True
        # B10 permits committed prose to leave the active file for Git history.
        # Remaining successor checks enforce existence, freshness and cycles.
        return old.successor is None or old.successor == current.successor
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


def _dependent_pointer_migration(
    index: dict[tuple[str, str], list[_DecisionLocation]],
    location: _DecisionLocation,
    old: Decision,
    current: Decision,
) -> bool:
    """Accept only migration to the active end of the former successor's chain."""

    if (
        not _pointer_only_stub(old)
        or not _pointer_only_stub(current)
        or old.successor is None
        or current.successor is None
    ):
        return False
    seen = {current.id}
    successor = old.successor
    followed_supersession = False
    while True:
        locations = _successor_locations(index, location, successor)
        if len(locations) != 1:
            return False
        location = locations[0]
        candidate = location.decision
        if candidate.active:
            return followed_supersession and current.successor == candidate.id
        if not _pointer_only_stub(candidate) or candidate.successor is None:
            return False
        if candidate.id in seen:
            return False
        seen.add(candidate.id)
        followed_supersession = True
        successor = candidate.successor


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
                elif not _successor_locations(current, location, successor):
                    _lifetime_finding(
                        findings,
                        "lifetime.successor-missing",
                        location,
                        f"successor {successor} does not exist in a visible decision collection",
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
            pointer_migration = _dependent_pointer_migration(
                current, location, old, decision
            )
            if old.successor is not None and successor != old.successor:
                if not pointer_migration:
                    _lifetime_finding(
                        findings,
                        "lifetime.successor-changed",
                        location,
                        "committed successor link was changed or removed",
                    )
                elif successor in baseline_ids:
                    _lifetime_finding(
                        findings,
                        "lifetime.successor-stale",
                        location,
                        f"successor {successor} was already committed and is not fresh",
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
        references, _shape = checker._decision_item_references(stated_by)
        for reference, bare in references:
            if (
                not bare
                and "." not in reference
                and reference not in resolver.aliases
                and location.module.path != item_location.module.path
            ):
                continue
            resolution = checker._resolve_decision_reference(
                resolver, reference, bare=bare
            )
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
    if source.kind not in {"decisions", "workspace decisions"}:
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


def _graph_reaches(
    graph: dict[_SemanticInterface, set[_SemanticInterface]],
    start: _SemanticInterface,
    goal: _SemanticInterface,
) -> bool:
    pending = [start]
    seen: set[_SemanticInterface] = set()
    while pending:
        current = pending.pop()
        if current is goal:
            return True
        if current in seen:
            continue
        seen.add(current)
        pending.extend(graph.get(current, set()))
    return False


def _module_dependency_reaches(
    used_modules: dict[str, set[str]], start: str, goal: str
) -> bool:
    pending = [start]
    seen: set[str] = set()
    while pending:
        current = pending.pop()
        if current == goal:
            return True
        if current in seen:
            continue
        seen.add(current)
        pending.extend(used_modules.get(current, set()))
    return False


def _item_reference(
    checker: _SemanticChecker,
    source: SourceFile,
    compound: str,
    reference_graph: dict[_SemanticInterface, set[_SemanticInterface]],
) -> str | None:
    """Return a visible reference spelling that preserves dependency direction."""

    module = checker.package.module_map[source.module]
    resolver = checker.resolver_for(source, module)
    owner = checker.model.by_source.get(source.path)
    declared_uses = checker.declared_uses.get(module.path)
    references = [compound]
    if source.kind == "workspace decisions":
        for member in checker.workspace_members:
            model = checker.models[id(member)]
            for target, public_path in model.public_item_paths():
                if target.name != compound:
                    continue
                references.append(f"{member.name}.{public_path}")
                references.append(f"{member.id}.{public_path}")
    for interface in checker.model.interfaces:
        if interface.module is module or not any(
            item.name == compound for item in interface.source.items
        ):
            continue
        if interface.module.path == "":
            prefix = checker.package.name if interface.default else interface.name
        else:
            prefix = interface.module.name
            if not interface.default:
                prefix += f".{interface.name}"
        references.append(f"{prefix}.{compound}")

    candidates = dict.fromkeys(references)
    ordered = sorted(candidates) if source.kind == "workspace decisions" else candidates
    for reference in ordered:
        resolution = resolver.resolve(reference)
        if resolution.status != "ok":
            continue
        targets = [
            target
            for target in resolution.targets
            if target.kind in {"item", "body-item"}
        ]
        if not targets:
            continue
        if source.kind == "workspace decisions":
            return reference
        if any(
            target.kind == "item"
            and target.interface is not None
            and target.interface.module is not module
            and (
                _module_dependency_reaches(
                    checker.used_modules, target.interface.module.path, module.path
                )
                or (
                    declared_uses is not None
                    and target.interface.module.path not in declared_uses
                )
            )
            for target in targets
        ):
            continue
        if owner is not None and any(
            target.kind == "item"
            and target.interface is not None
            and target.interface is not owner
            and _graph_reaches(reference_graph, target.interface, owner)
            for target in targets
        ):
            continue
        return reference
    return None


def _bare_candidates(package: Package, review: bool) -> list[Finding]:
    checker = _SemanticChecker(package, ())
    checker.run()
    _, reference_graph = checker._interface_graphs()
    names = {location.item.name for location in _item_locations(package)}
    for member in package.workspace_members:
        model = checker.models[id(member)]
        names.update(target.name for target in model.public_items())
    compounds = [name for name in names if re.split(r"[ -]+", name.strip()) and len(re.split(r"[ -]+", name.strip())) > 1]
    excluded_words = _PROSE_CORE_WORDS
    singles = [
        name
        for name in names
        if re.fullmatch(r"[A-Za-z][A-Za-z0-9_]*", name) and name.casefold() not in excluded_words
    ]
    findings: list[Finding] = []
    for source in package.files:
        if source.kind not in {"header", "private header", "body", "decisions", "workspace decisions"}:
            continue
        definitions = _definition_spans(source)
        for region, base_line in _prose_regions(source):
            masked = _mask_prose(region)
            candidates: list[_BareCandidate] = []
            for name in compounds:
                reference = _item_reference(checker, source, name, reference_graph)
                if reference is None:
                    continue
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
                                f"bare multiword item name; write [{reference}] when this use names the item",
                                line,
                            ),
                        )
                    )
            if review:
                for name in singles:
                    suggestion = name
                    if source.kind == "workspace decisions":
                        suggestion = _item_reference(checker, source, name, reference_graph) or name
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
                                    f"ambiguous bare item name; write [{suggestion}] if this use names the item",
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
    unique: dict[tuple[str, str, str, str, str, str], Finding] = {}
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
    baseline_dependency_packages: Iterable[Package] | None = None,
) -> list[Finding]:
    """Aggregate current checks, suppressing only exact committed finding keys."""

    dependencies = tuple(dependency_packages)
    baseline_dependencies = (
        dependencies
        if baseline_dependency_packages is None
        else tuple(baseline_dependency_packages)
    )
    current = [
        *structured_findings(package),
        *(
            replace(finding, package_id=dependency.id)
            for dependency in dependencies
            for finding in structured_findings(dependency)
        ),
        *semantic_findings(package, dependencies),
        *prose_findings(package, baseline=baseline, review=review),
    ]
    if baseline is not None:
        committed = [
            *structured_findings(baseline),
            *(
                replace(finding, package_id=dependency.id)
                for dependency in baseline_dependencies
                for finding in structured_findings(dependency)
            ),
            *semantic_findings(baseline, baseline_dependencies),
            *prose_findings(baseline, review=review),
        ]
        committed_keys = {finding.key for finding in committed}
        current = [
            finding
            for finding in current
            if finding.rule in EDITION_FINDING_RULES or finding.key not in committed_keys
        ]
        current.extend(
            replace(finding, package_id=baseline.id)
            for finding in baseline.findings
            if finding.rule in EDITION_FINDING_RULES
        )
    current.extend(decision_lifetime_findings(package, baseline, review=review))
    if not review:
        current = [finding for finding in current if finding.severity == "error"]
    return _sorted_findings(current)


def check_workspace(
    package: Package,
    baseline: Package | None = None,
    review: bool = False,
) -> list[Finding]:
    """Check current members independently together with workspace decisions."""

    findings = list(check_package(package, baseline, review=review))
    baseline_members = {
        member.id: member for member in (baseline.workspace_members if baseline else [])
    }
    for member in package.workspace_members:
        findings.extend(
            check_package(
                member,
                baseline_members.get(member.id),
                review=review,
            )
        )
    return _sorted_findings(findings)


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
    """Return Go dirhash.Hash1 as a SHA-256 multihash.

    The leading ``1220`` is the hexadecimal form of the multihash prefix
    ``0x12 0x20`` (SHA-256, 32 bytes), defined by the community specification at
    https://github.com/multiformats/multihash.
    """

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
