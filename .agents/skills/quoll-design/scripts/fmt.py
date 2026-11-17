"""Format statement lines in canonical Quoll view blocks.

Usage: python3 -I fmt.py <package dir>

Only Structure, Flow and Rules views in ATX-headed sections are changed. Item names, their opening
prefixes, statement text, openers, blank lines and everything outside those
views stay as written. Statements are greedily wrapped to 100 columns, with
continuations aligned to the statement's first column.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))

from quollcheck import _fence_marker, _is_fence_close, _opener  # noqa: E402

WIDTH = 100


@dataclass
class _Item:
    indent: int
    lines: list[int] = field(default_factory=list)


def _content(line: str) -> str:
    return line.rstrip("\r\n")


def _ending(line: str) -> str:
    return line[len(_content(line)) :]


def _atx_heading(line: str) -> tuple[int, str] | None:
    match = re.match(r"^ {0,3}(#{1,6})(?:[ \t]+(.*)|[ \t]*)$", line)
    if match is None:
        return None
    content = (match.group(2) or "").strip(" \t")
    content = re.sub(r"[ \t]+#+[ \t]*$", "", content).strip(" \t")
    return len(match.group(1)), content


def _view_spans(lines: list[str]) -> list[tuple[int, int]]:
    """Return content bounds for views, with ATX heading and fence boundaries."""
    spans = []
    fence: str | None = None
    view_start: int | None = None
    section: str | None = None
    section_had_fence = False
    seen_sections: set[str] = set()

    for index, line in enumerate(lines):
        raw = _content(line)
        if fence is not None:
            if _is_fence_close(raw, fence):
                if view_start is not None:
                    spans.append((view_start, index))
                    view_start = None
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
                section_had_fence = True

    if view_start is not None:
        spans.append((view_start, len(lines)))
    return spans


def _items(lines: list[str], start: int, end: int) -> list[_Item]:
    candidates = [
        len(_content(lines[index])) - len(_content(lines[index]).lstrip(" "))
        for index in range(start, end)
        if _content(lines[index]).strip()
        and not _content(lines[index]).lstrip(" ").startswith("\t")
    ]
    if not candidates:
        return []

    base = min(candidates)
    items: list[_Item] = []
    current: _Item | None = None
    item_indent = base
    grouped = False
    pending_group = False

    for index in range(start, end):
        raw = _content(lines[index])
        if not raw.strip() or raw.lstrip(" ").startswith("\t"):
            if current is not None:
                current.lines.append(index)
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        opening = _opener(raw[indent:])

        if indent == base and opening:
            if not grouped or not pending_group:
                item_indent = base
            grouped = True
            pending_group = True
            current = None
            continue

        if grouped and indent == base:
            grouped = False
            pending_group = False
            item_indent = base
            current = None

        if pending_group:
            if indent <= base:
                current = None
                continue
            item_indent = indent
            pending_group = False

        if indent == item_indent:
            current = _Item(indent, [index])
            items.append(current)
        elif current is not None and indent > item_indent:
            current.lines.append(index)
        else:
            current = None
    return items


def _backtick_run_end(text: str, start: int) -> int:
    end = start + 1
    while end < len(text) and text[end] == "`":
        end += 1
    return end


def _code_span_end(text: str, start: int) -> int | None:
    run_end = _backtick_run_end(text, start)
    marker = text[start:run_end]
    search = run_end
    while (closing := text.find(marker, search)) != -1:
        after = closing + len(marker)
        if (
            text[closing - 1] != "`"
            and (after == len(text) or text[after] != "`")
        ):
            return after
        search = closing
        while search < len(text) and text[search] == "`":
            search += 1
    return None


def _bracket_end(text: str, start: int) -> int | None:
    depth = 0
    index = start
    while index < len(text):
        if text[index] == "\\":
            index += 2
            continue
        if text[index] == "`":
            run_end = _backtick_run_end(text, index)
            index = _code_span_end(text, index) or run_end
            continue
        if text[index] == "[":
            depth += 1
        elif text[index] == "]":
            depth -= 1
            if depth == 0:
                return index + 1
        index += 1
    return None


def _inline_link_end(text: str, opening: int) -> int | None:
    depth = 0
    angle = False
    quote: str | None = None
    index = opening
    while index < len(text):
        character = text[index]
        if character == "\\":
            index += 2
            continue
        if quote is not None:
            if character == quote:
                quote = None
        elif angle:
            if character == ">":
                angle = False
        elif character == "<":
            angle = True
        elif character in {'"', "'"} and index > opening and text[index - 1].isspace():
            quote = character
        elif character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
            if depth == 0:
                return index + 1
        index += 1
    return None


def _chunks(statement: str) -> list[str]:
    """Split at single spaces outside code spans and bracketed constructs."""
    chunks = []
    start = 0
    index = 0
    while index < len(statement):
        if statement[index] == "`":
            run_end = _backtick_run_end(statement, index)
            index = _code_span_end(statement, index) or run_end
            continue
        if statement[index] == "[":
            closing = _bracket_end(statement, index)
            if closing is not None:
                index = closing
                if index < len(statement) and statement[index] == "(":
                    index = _inline_link_end(statement, index) or index
                continue
        if (
            statement[index] == " "
            and (index == 0 or statement[index - 1] != " ")
            and (index + 1 == len(statement) or statement[index + 1] != " ")
        ):
            chunks.append(statement[start:index])
            start = index + 1
        index += 1
    chunks.append(statement[start:])
    return chunks


def _wrap(statement: str, prefix: str) -> list[str]:
    continuation = " " * len(prefix)
    available = WIDTH - len(prefix)
    wrapped: list[str] = []
    current = ""
    for chunk in _chunks(statement):
        if not current:
            current = chunk
        elif len(current) + 1 + len(chunk) <= available:
            current += " " + chunk
        else:
            wrapped.append(current)
            current = chunk
    if current:
        wrapped.append(current)
    return [prefix + wrapped[0], *(continuation + line for line in wrapped[1:])]


def _format_run(lines: list[str], indices: list[int], prefix: str, statement: str) -> None:
    if not statement:
        return
    replacement = _wrap(statement, prefix)
    endings = [_ending(lines[index]) for index in indices]
    final_ending = endings[-1]
    first_ending = endings[0]
    replacement = [
        line + (final_ending if index == len(replacement) - 1 else first_ending)
        for index, line in enumerate(replacement)
    ]
    lines[indices[0] : indices[-1] + 1] = replacement


def _format_item(lines: list[str], item: _Item) -> None:
    first_index = item.lines[0]
    first = _content(lines[first_index])
    separator = re.search(r" {2,}", first[item.indent :])
    fragments = {}
    item_lines = item.lines
    if separator is not None:
        statement_start = item.indent + separator.end()
        prefix = first[:statement_start]
        fragments[first_index] = first[statement_start:].strip()
    else:
        statement_start = next(
            (
                len(_content(lines[index])) - len(_content(lines[index]).lstrip(" "))
                for index in item.lines[1:]
                if _content(lines[index]).strip()
                and not _content(lines[index]).lstrip(" ").startswith("\t")
            ),
            0,
        )
        if not statement_start:
            return
        prefix = " " * statement_start
        item_lines = item.lines[1:]

    runs: list[list[int]] = []
    for index in item_lines:
        raw = _content(lines[index])
        if not raw.strip() or raw.lstrip(" ").startswith("\t"):
            runs.append([])
            continue
        if not runs or not runs[-1]:
            runs.append([index])
        else:
            runs[-1].append(index)
        if index != first_index:
            fragments[index] = raw.strip()

    for run in reversed([run for run in runs if run]):
        run_prefix = prefix if run[0] == first_index else " " * statement_start
        statement = " ".join(fragment for index in run if (fragment := fragments[index]))
        _format_run(lines, run, run_prefix, statement)


def format_text(text: str) -> str:
    lines = text.splitlines(keepends=True)
    for start, end in reversed(_view_spans(lines)):
        for item in reversed(_items(lines, start, end)):
            _format_item(lines, item)
    return "".join(lines)


def main(arguments: list[str]) -> int:
    if len(arguments) != 1:
        print("usage: fmt.py <package dir>", file=sys.stderr)
        return 2
    root = Path(arguments[0])
    if not root.is_dir():
        print(f"fmt.py: not a directory: {root}", file=sys.stderr)
        return 2

    changed = 0
    for path in sorted(root.rglob("*.md")):
        relative = path.relative_to(root)
        if any(part.startswith(".") for part in relative.parts):
            continue
        if not path.name.endswith((".h.md", ".body.md")):
            continue
        original = path.read_bytes().decode("utf-8")
        formatted = format_text(original)
        if formatted != original:
            path.write_bytes(formatted.encode("utf-8"))
            changed += 1
            print(relative)
    print(f"formatted: {changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
