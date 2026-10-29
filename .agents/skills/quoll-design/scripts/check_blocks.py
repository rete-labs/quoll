"""Check the view blocks of a package's files.

Usage: python3 -I check_blocks.py <package dir>
A line holding only an opener opens a group: `ensures:`, `requires:` or `open:`, or,
in a body, `impl [interface]:`. Opener lines stack at one indentation, at most one
`impl` line and one other, the `impl` line first. Items are the least indented
lines outside a group and the lines one step more indented inside one, a group
ending at the first line indented as its openers are; every item's
name is followed by two spaces. Also reports lines over 100 columns, an opener left
at the start of a statement, a rule outside any group, and a rule whose group has
no direction.
"""
import re
import sys
from pathlib import Path

DIRECTIONS = {"ensures:", "requires:", "open:"}
IMPL = re.compile(r"^impl \[[^\]]+\]:$")
root = Path(sys.argv[1])
bad = 0


def report(path, no, what):
    global bad
    print(f"{path.relative_to(root)}:{no}: {what}")
    bad += 1


def is_opener(text):
    return text in DIRECTIONS or bool(IMPL.match(text))


def check_block(path, heading, block):
    body = [(n, l) for n, l in block if l.strip()]
    least = min(len(l) - len(l.lstrip(" ")) for _, l in body)
    run, group, after_run = [], None, False
    for n, l in body:
        indent, text = len(l) - len(l.lstrip(" ")), l.strip()
        if len(l) > 100:
            report(path, n, f"{len(l)} columns")
        if indent == least and is_opener(text):
            if not after_run:
                run = []
            run.append(text)
            kinds = ["impl" if IMPL.match(t) else "direction" for t in run]
            if kinds[-1] == "impl" and not path.name.endswith(".body.md"):
                report(path, n, "an impl line outside a body")
            if kinds.count("impl") > 1 or kinds.count("direction") > 1:
                report(path, n, "two openers of one kind over a group")
            if kinds[-1] == "impl" and "direction" in kinds[:-1]:
                report(path, n, "an impl line under another opener")
            group, after_run = None, True
            continue
        is_item = False
        if indent == least:
            run, group, is_item = [], None, True
            if heading == "Rules":
                report(path, n, "a rule outside any group")
        elif group is None and after_run:
            group, is_item = indent, True
        elif group is not None and indent == group:
            is_item = True
        after_run = False
        if is_item:
            if heading == "Rules" and run and not any(t in DIRECTIONS for t in run):
                report(path, n, "a rule whose group has no direction")
            rest = l[indent:]
            m = re.search(r"  +", rest)
            if not m:
                report(path, n, f"no two spaces after the name: {rest[:40]!r}")
            elif rest[m.end():].split(" ", 1)[0] in DIRECTIONS:
                report(path, n, "an opener left at the start of a statement")


for path in sorted(root.rglob("*.md")):
    lines = path.read_text(encoding="utf-8").split("\n")
    heading, in_block, block = None, False, []
    for no, line in enumerate(lines, 1):
        if line.startswith("## ") and not in_block:
            heading = line[3:].strip()
        if line.startswith("```"):
            if in_block and block:
                check_block(path, heading, block)
            block, in_block = [], not in_block
            continue
        if in_block:
            block.append((no, line))
print("problems:", bad)
