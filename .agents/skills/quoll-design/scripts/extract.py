"""Extract axis blocks by ID from a decisions record into one inputs file.

usage: extract.py OUT TITLE SRC:ID,ID,... [SRC:ID,...]
A block runs from a line opening `**ID. ` to the next line opening another `**<ID>. `, as `**A2. ` or `**IN-3. `,
or a heading, outside fenced blocks.
"""
import re, sys

out, title, specs = sys.argv[1], sys.argv[2], sys.argv[3:]
head = re.compile(r'^\*\*[A-Z][A-Za-z0-9-]*\. |^#')
parts = [f"# {title}\n\nExtracted verbatim by the orchestrator from the records named below; each block is whole, from its heading to the next.\n"]
for spec in specs:
    src, ids = spec.split(':', 1)
    lines = open(src, encoding='utf-8').read().split('\n')
    parts.append(f"\n## From `{src.split('quoll/', 1)[-1]}`\n")
    for i in ids.split(','):
        starts = [n for n, l in enumerate(lines) if l.startswith(f"**{i}. ")]
        if len(starts) != 1:
            sys.exit(f"{i}: {len(starts)} blocks in {src}")
        n = starts[0]; m = n + 1; fence = None
        while m < len(lines):
            f = re.match(r'^(`{3,}|~{3,})', lines[m])
            if f and (fence is None or f.group(1)[0] == fence[0] and len(f.group(1)) >= len(fence)):
                fence = None if fence else f.group(1)
            elif fence is None and head.match(lines[m]):
                break
            m += 1
        parts.append('\n'.join(lines[n:m]).rstrip('\n') + '\n')
open(out, 'w', encoding='utf-8').write('\n'.join(parts))
print(out, sum(len(p) for p in parts))
