"""List sites resting on items and decisions changed between two package copies.

Usage: ref_sites.py OLD_DIR NEW_DIR. Both directories are v0.4 package states.
References are matched textually, without sight or resolution checks.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from quollcheck import Decision, Module, Package, SourceFile, load_package  # noqa: E402


@dataclass(frozen=True)
class Change:
    module_path: str
    module_name: str
    stem: str | None
    item: str
    how: str
    impl: str | None = None

    @property
    def default(self) -> bool:
        return self.stem == self.module_name


def normalized(text: str) -> str:
    return " ".join(text.split())


def interface_stem(source: SourceFile) -> str:
    name = Path(source.path).name
    if name.endswith(".private.h.md"):
        return name[: -len(".private.h.md")]
    return name[: -len(".h.md")]


def interfaces(module: Module | None) -> dict[str, SourceFile]:
    if module is None:
        return {}
    result: dict[str, SourceFile] = {}
    for source in sorted(module.files, key=lambda file: file.path):
        if source.kind in {"header", "private header"}:
            result[interface_stem(source)] = source
    return result


def interface_identity(module: Module, relation: str) -> tuple[str, str] | None:
    stem = module.name if relation == "default" else relation
    if stem in interfaces(module):
        return module.path, stem
    return None


def resolved_interface(
    package: Package, module: Module | None, relation: str
) -> tuple[str, str] | None:
    relation = relation.strip().strip("\"'")
    if module is not None and ("." not in relation or relation == "default"):
        local = interface_identity(module, relation)
        if local is not None:
            return local
    parts = relation.split(".")
    candidates: list[tuple[str, str]] = []
    root_candidate: tuple[str, str] | None = None
    for target in package.modules:
        if len(parts) == 1:
            identity = interface_identity(target, "default") if target.name == relation else None
            if target.path == "":
                root_candidate = interface_identity(target, relation)
        else:
            qualifiers = {target.name, target.path.replace("/", ".")}
            if target.path == "":
                qualifiers.add(package.name)
            identity = (
                interface_identity(target, parts[-1])
                if ".".join(parts[:-1]) in qualifiers
                else None
            )
        if identity is not None:
            candidates.append(identity)
    if root_candidate is not None:
        return root_candidate
    unique = list(dict.fromkeys(candidates))
    return unique[0] if len(unique) == 1 else None


def relation_identity(
    package: Package, module: Module | None, relation: str | None
) -> str | None:
    if relation is None:
        return None
    resolved = resolved_interface(package, module, relation)
    if resolved is None:
        return f"relation:{relation}"
    path, stem = resolved
    return f"interface:{path}:{stem}"


def items(
    source: SourceFile | None, package: Package, module: Module | None
) -> dict[tuple[str, str | None, int], str]:
    if source is None:
        return {}
    result: dict[tuple[str, str | None, int], str] = {}
    occurrences: dict[tuple[str, str | None], int] = {}
    for item in source.items:
        identity = (item.name, relation_identity(package, module, item.impl))
        occurrence = occurrences.get(identity, 0)
        occurrences[identity] = occurrence + 1
        result[(*identity, occurrence)] = normalized(item.statements)
    return result


def module_name(old: Module | None, new: Module | None) -> str:
    return (new or old).name  # type: ignore[union-attr]


def item_changes(old: Package, new: Package) -> list[Change]:
    changes: list[Change] = []
    old_modules = old.module_map
    new_modules = new.module_map
    for path in sorted(set(old_modules) | set(new_modules)):
        old_module = old_modules.get(path)
        new_module = new_modules.get(path)
        name = module_name(old_module, new_module)
        old_interfaces = interfaces(old_module)
        new_interfaces = interfaces(new_module)
        targets: list[tuple[str | None, SourceFile | None, SourceFile | None]] = [
            (
                stem,
                old_interfaces.get(stem),
                new_interfaces.get(stem),
            )
            for stem in sorted(set(old_interfaces) | set(new_interfaces))
        ]
        targets.append(
            (
                None,
                old_module.body if old_module else None,
                new_module.body if new_module else None,
            )
        )
        for stem, old_source, new_source in targets:
            old_items = items(old_source, old, old_module)
            new_items = items(new_source, new, new_module)
            keys = sorted(
                set(old_items) | set(new_items),
                key=lambda key: (key[0], key[1] or "", key[2]),
            )
            for item, impl, occurrence in keys:
                key = (item, impl, occurrence)
                if key not in new_items:
                    how = "gone"
                elif key not in old_items:
                    how = "new"
                elif old_items[key] != new_items[key]:
                    how = "changed"
                else:
                    continue
                changes.append(Change(path, name, stem, item, how, impl))
    return changes


def markdown_sources(package: Package) -> list[SourceFile]:
    files = {
        source.path: source
        for module in package.modules
        for source in module.files
        if source.path.endswith(".md")
    }
    return [files[path] for path in sorted(files)]


def historical_lines(source: SourceFile) -> set[int]:
    lines: set[int] = set()
    for decision in source.decisions:
        if decision.active:
            continue
        end = max(decision.line, decision.end_line)
        lines.update(range(decision.line, end + 1))
    return lines


def mask_code_spans(text: str) -> str:
    return re.sub(
        r"`[^`\n]*`",
        lambda match: " " * len(match.group(0)),
        text,
    )


def spellings(change: Change, inside: bool) -> set[str]:
    stem = change.stem
    item = change.item
    name = change.module_name
    default = change.default
    outside = set() if stem is None else (
        {f"{name}.{item}"} if default else {f"{name}.{stem}.{item}"}
    )
    if stem is not None and not default and change.module_path == "":
        outside.add(f"{stem}.{item}")
    if not inside:
        return outside
    local = {item}
    if stem and not default:
        local.add(f"{stem}.{item}")
    if default:
        local.add(f"default.{item}")
    return local | outside


def print_reference_sites(change: Change, new: Package) -> None:
    stem = change.stem
    if stem:
        suffix = "" if change.default else f".{stem}"
        print(f"## {change.module_name}{suffix}.{change.item} ({change.how})")
    else:
        print(f"## {change.module_name} body: {change.item} ({change.how})")
    if change.how == "new":
        return
    for source in markdown_sources(new):
        module = next(
            (module for module in new.modules if source in module.files),
            None,
        )
        if module is None:
            continue
        wanted = spellings(change, module.path == change.module_path)
        if not wanted:
            continue
        history = historical_lines(source)
        seen: set[int] = set()
        for match in re.finditer(
            r"\[([^\]\n]+(?:\n *[^\]\n]+)*)\](?!\()",
            mask_code_spans(source.text),
        ):
            if normalized(match.group(1)) not in wanted:
                continue
            line = source.text.count("\n", 0, match.start()) + 1
            if line in history or line in seen:
                continue
            seen.add(line)
            text = source.text.splitlines()[line - 1].strip()[:160]
            print(f"  {source.path}:{line}: {text}")


def decisions(module: Module | None) -> dict[str, Decision]:
    if module is None or module.decisions is None:
        return {}
    return {decision.id: decision for decision in module.decisions.decisions}


def decision_key(identifier: str) -> tuple[str, int, str]:
    prefix, separator, number = identifier.rpartition("-")
    if separator and number.isdigit():
        return prefix, int(number), identifier
    return identifier, 0, identifier


def decision_changes(old: Package, new: Package) -> list[tuple[str, str]]:
    changes: list[tuple[str, str]] = []
    old_modules = old.module_map
    new_modules = new.module_map
    for path in sorted(set(old_modules) | set(new_modules)):
        old_decisions = decisions(old_modules.get(path))
        new_decisions = decisions(new_modules.get(path))
        for identifier in sorted(old_decisions, key=decision_key):
            previous = old_decisions[identifier]
            current = new_decisions.get(identifier)
            if not previous.active:
                continue
            if current is not None and not current.active:
                # Gaining a successor retires the entry; it is not a current edit.
                continue
            if current is None:
                changes.append((identifier, "gone"))
            elif normalized(previous.text) != normalized(current.text):
                changes.append((identifier, "changed"))
    return changes


def print_decision_sites(identifier: str, how: str, new: Package) -> None:
    print(f"## {identifier} ({how})")
    pattern = re.compile(r"(?<![A-Za-z0-9-])" + re.escape(identifier) + r"(?![0-9-])")
    for source in markdown_sources(new):
        history = historical_lines(source)
        for line_number, line in enumerate(source.text.splitlines(), 1):
            if line_number in history or line.startswith(f"**{identifier}. "):
                continue
            if pattern.search(line):
                print(f"  {source.path}:{line_number}: {line.strip()[:160]}")


def relation_values(front: dict, key: str) -> list[str]:
    value = front.get(key)
    if isinstance(value, list):
        return [entry for entry in value if isinstance(entry, str)]
    return []


def relation_matches(value: str, change: Change, inside: bool) -> bool:
    value = value.strip().strip("\"'")
    local = {change.stem or ""}
    if change.default:
        local.add("default")
    outside = (
        {change.module_name, f"{change.module_name}.default"}
        if change.default
        else {f"{change.module_name}.{change.stem}"}
    )
    if change.stem is not None and not change.default and change.module_path == "":
        outside.add(change.stem)
    return value in outside or (inside and value in local)


def front_relation_line(source: SourceFile, key: str) -> int:
    pattern = re.compile(rf"^\s*{re.escape(key)}\s*=", re.MULTILINE)
    match = pattern.search(source.text)
    if match is None:
        return 1
    return source.text.count("\n", 0, match.start()) + 1


def print_relation_sites(change: Change, new: Package) -> None:
    if change.how == "new" or change.stem is None:
        return
    sites: list[str] = []
    for module in new.modules:
        for source in module.files:
            if not source.path.endswith(".md"):
                continue
            inside = module.path == change.module_path
            for key in ("includes", "implements"):
                values = relation_values(source.front, key)
                if any(relation_matches(value, change, inside) for value in values):
                    line_number = front_relation_line(source, key)
                    line = source.text.splitlines()[line_number - 1].strip()[:160]
                    sites.append(f"  {source.path}:{line_number}: {line}")
            for match in re.finditer(
                r"^\s*impl\s+\[([^\]]+)\]\s*:\s*$",
                source.text,
                re.MULTILINE,
            ):
                if relation_matches(match.group(1), change, inside):
                    line_number = source.text.count("\n", 0, match.start()) + 1
                    sites.append(
                        f"  {source.path}:{line_number}: {match.group(0).strip()[:160]}"
                    )
    if change.default:
        module = new.module_map.get(change.module_path)
        if module and module.body:
            sites.append(
                f"  {module.body.path}: the body of [{change.module_name}], implementing its default"
            )
    if sites:
        suffix = "" if change.default else f".{change.stem}"
        print(f"## {change.module_name}{suffix}.{change.item} (relations)")
        for site in dict.fromkeys(sites):
            print(site)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="List textual sites resting on changes between two package copies."
    )
    result.add_argument("old", metavar="OLD_DIR", help="old v0.4 package copy")
    result.add_argument("new", metavar="NEW_DIR", help="current v0.4 package copy")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if not Path(args.old).is_dir() or not Path(args.new).is_dir():
        parser().error("OLD_DIR and NEW_DIR must be package directories")
    try:
        old = load_package(args.old)
        new = load_package(args.new)
    except (OSError, ValueError) as error:
        print(f"ref_sites.py: {error}", file=sys.stderr)
        return 2
    untrusted = False
    for label, package in (("OLD_DIR", old), ("NEW_DIR", new)):
        for finding in package.findings:
            print(f"{label}: {finding}", file=sys.stderr)
            untrusted = True
    if untrusted:
        return 2
    changes = item_changes(old, new)
    for change in changes:
        print_reference_sites(change, new)
    for identifier, how in decision_changes(old, new):
        print_decision_sites(identifier, how, new)
    for change in changes:
        print_relation_sites(change, new)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
