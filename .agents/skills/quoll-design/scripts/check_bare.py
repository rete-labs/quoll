"""For every name a reference uses, list its bare uses across the package.

Usage: python3 -I check_bare.py <package dir>
A name that some reference uses, met bare elsewhere, is either a reference
left unmarked, a use beyond the module's sight, or the word in another sense:
each line is for a reviewer to judge. Plurals and possessives count. Prints file:line, the name, and
whether the name is in the writing component's own scope.
"""
import re
import sys
from pathlib import Path

root = Path(sys.argv[1])
files = sorted(root.rglob("*.md"))


def blank_literal_fences(text):
    """A fenced block other than a view's, the first under its view's heading, is
    literal text and holds no reference; its lines are blanked, their count kept."""
    out, heading, in_fence, keep, seen = [], None, False, False, False
    for line in text.split("\n"):
        if not in_fence and line.startswith("## "):
            heading, seen = line[3:].strip(), False
        if line.startswith("```"):
            if not in_fence:
                keep = heading in ("Structure", "Flow", "Rules") and not seen
                seen = True
            in_fence = not in_fence
            out.append(line)
            continue
        out.append(line if not in_fence or keep else "")
    return "\n".join(out)


def strip(text):
    text = blank_literal_fences(text)
    text = re.sub(r"\A---\n.*?\n---\n", lambda m: "\n" * m.group(0).count("\n"), text, flags=re.S)
    text = re.sub(r"`[^`\n]*`", lambda m: " " * len(m.group(0)), text)
    text = re.sub(r"\[[^\]\n]*\](\([^)\n]*\))?", lambda m: " " * len(m.group(0)), text)
    return text


names = set()
for f in files:
    t = f.read_text(encoding="utf-8")
    t = re.sub(r"\A---\n.*?\n---\n", "", t, flags=re.S)
    t = re.sub(r"`[^`\n]*`", "", t)
    for m in re.finditer(r"\[([^\]\n]+)\](?!\()", t):
        ref = m.group(1)
        names.add(ref.split(".")[-1])
        if "." not in ref:
            names.add(ref)

own = {}
for f in files:
    d = f.parent
    if d not in own:
        s = set()
        for h in d.glob("*.h.md"):
            for line in h.read_text(encoding="utf-8").split("\n"):
                m = re.match(r"^ {2,4}(\S(?:\S| (?! ))*)  ", line)
                if m:
                    s.add(m.group(1))
        own[d] = s

for f in files:
    text = strip(f.read_text(encoding="utf-8"))
    for no, line in enumerate(text.split("\n"), 1):
        defined = re.match(r"^ {2,4}(\S(?:\S| (?! ))*)  ", line)
        for n in sorted(names, key=len, reverse=True):
            for m in re.finditer(rf"(?<![\w-]){re.escape(n)}(s|'s|')?(?![\w-])", line):
                if defined and m.start() == defined.start(1):
                    continue
                scope = "own" if n in own.get(f.parent, ()) else "elsewhere"
                ctx = line[max(0, m.start() - 30): m.end() + 20].strip()
                print(f"{f.relative_to(root)}:{no}\t{n}\t{scope}\t…{ctx}…")
