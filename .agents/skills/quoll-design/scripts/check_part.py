"""Check one module of a package: its references land, its items are in order, and its entries' Stated by.

usage: check_part.py <header> <decisions> <MNEMONIC> [name=<header of an interface it uses> ...]
Every reference in the header and the decisions must land on one of the header's own items, an entry ID of
MNEMONIC, or `name.item` of an interface named on the command line, `name` being written as the module's
references write it: `fs` for a module's default interface, `fs.reader` for another of its interfaces. Items of the first view may use only items
above them. Every entry's first line under its heading must be its Stated by, references alone, each landing on
an item. Prints the items no Stated by names, for a reviewer to judge, and entries run together in one paragraph.
To check a module with a body, concatenate its header and body into one file first and pass that as <header>.
"""
import re, sys

def items(t):
    out = []
    for vi, b in enumerate(re.findall(r'^```\n(.*?)^```', t, re.S | re.M)):
        lines = [l for l in b.split('\n') if l.strip()]
        least = min(len(l) - len(l.lstrip(' ')) for l in lines)
        item_ind, grp, cur = least, None, None
        for l in lines:
            ind = len(l) - len(l.lstrip(' ')); body = l.strip()
            if re.fullmatch(r'(ensures|requires|open):|impl \[[^\]]+\]:', body):
                grp, item_ind, cur = ind, None, None; continue
            if grp is not None and ind <= grp:
                grp, item_ind = None, least
            if item_ind is None:
                item_ind = ind
            if ind == item_ind:
                m = re.match(r'(\S(?:.*?\S)?)  +(.*)', body) or re.match(r'(\S.*)', body)
                cur = [m.group(1), vi, m.group(2) if m.lastindex == 2 else '']; out.append(cur)
            elif cur:
                cur[2] += ' ' + body
    return out

hdr, dec, mn = sys.argv[1:4]
others = dict(a.split('=', 1) for a in sys.argv[4:])
h = open(hdr, encoding='utf-8').read(); d = open(dec, encoding='utf-8').read()
own = items(h); names = [i[0] for i in own]
other = {k: [i[0] for i in items(open(v, encoding='utf-8').read())] for k, v in others.items()}
strip = lambda t: re.sub(r'`[^`\n]*`', '', t)
refs = set(re.findall(r'\[([^\]]+)\](?!\()', strip(h))) | set(re.findall(r'\[([^\]]+)\](?!\()', strip(d)))
bad = []
def lands(r):
    """r is an item of the header, an interface named on the command line, or an item of one."""
    if r in names or r in other: return True
    return any(r.startswith(k + '.') and r[len(k) + 1:] in other[k] for k in other)
for r in sorted(refs):
    if re.fullmatch(mn + r'-\d+', r) or lands(r): continue
    bad.append(r)
print('items:', ', '.join(names))
print('unresolved:', bad or 'none')
seen = set()
for n, vi, txt in [i for i in own if i[1] == 0]:
    later = [u for u in set(re.findall(r'\[([^\]]+)\]', strip(txt))) - {n} if '.' not in u and u not in seen and u not in other]
    if later: print('uses an item below it:', n, '->', later)
    seen.add(n)
print('acyclic check done')

# Stated by: the first field of every entry, references alone with joining words.
stated = set()
for e in re.split(r'\n(?=\*\*' + mn + r'-\d+\. )', d):
    m = re.match(r'\*\*(' + mn + r'-\d+)\.', e)
    if not m: continue
    lines = [l for l in e.split('\n')[1:] if l.strip()]
    if not lines or not lines[0].startswith('*Stated by* '):
        print('no Stated by first:', m.group(1)); continue
    refs = re.findall(r'\[([^\]]+)\]', lines[0]); stated |= set(refs)
    rest = re.sub(r'\[[^\]]+\]', '', lines[0][len('*Stated by* '):])
    if re.sub(r'\b(and|by|for|what|waits|the)\b|[,;.\s]', '', rest):
        print('Stated by holds more than references:', m.group(1), repr(rest.strip()[:80]))
# Stated by names items alone: every reference in it lands on an item of this part or another's.
for e in re.split(r'\n(?=\*\*' + mn + r'-\d+\. )', d):
    m = re.match(r'\*\*(' + mn + r'-\d+)\.', e)
    if not m: continue
    first = [l for l in e.split('\n')[1:] if l.strip()][:1]
    if not first or not first[0].startswith('*Stated by* '): continue
    for r in re.findall(r'\[([^\]]+)\]', first[0]):
        if r in names or (r not in other and lands(r)): continue
        print('Stated by names no item:', m.group(1), '[' + r + ']')
print('items no Stated by names, for the reviewer:', [n for n in names if n not in stated] or 'none')
joined = [p.split('\n')[0][:30] for p in d.split('\n\n') if len(re.findall(r'^\*\*' + mn + r'-\d+\.', p, re.M)) > 1]
print('entries run together in one paragraph:', joined or 'none')
