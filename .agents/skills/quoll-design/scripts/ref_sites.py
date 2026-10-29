"""List every site resting on what changed between two copies of a package.

usage: ref_sites.py OLD_DIR NEW_DIR
OLD_DIR and NEW_DIR are two copies of one package's directory. Copy the package before a round of changes, and run
this from the copy to the package after it. The modules are the root, whose files stand at the package's top, and
each path the manifest lists under Modules, nested ones included, each named by its path's last step; each header of
a module, `<stem>.h.md` or `<stem>.private.h.md` in its directory, is one of its interfaces, the one whose stem is the
module's name its default. Lists:
- for every item of an interface or a body changed or gone, each line in NEW_DIR holding a reference landing on it:
  `item`, `interface.item` or `default.item` within its own module's files, and `module.item`, for its default's
  items, or `module.interface.item` from anywhere;
- for every decision entry changed or gone, each line citing its ID;
- for every item changed in an interface, each place relating to that interface: a front's `includes` or
  `implements`, an `impl` line, and the body of a module implementing its default.
Its limits: a reference is matched by its text alone, with no check of sight, so two modules sharing a name are both
matched; and an item is matched by its name, so a reference spanning two lines of a view block is found only where
its brackets hold the whole name.
"""
import re, sys, os, glob

def items(path):
    out = {}
    if not os.path.exists(path): return out
    t = open(path, encoding='utf-8').read()
    for b in re.findall(r'^```\n(.*?)^```', t, re.S | re.M):
        lines = [l for l in b.split('\n') if l.strip()]
        if not lines: continue
        least = min(len(l) - len(l.lstrip(' ')) for l in lines)
        grp, ii, cur = None, None, None
        for l in lines:
            ind = len(l) - len(l.lstrip(' ')); body = l.strip()
            if re.fullmatch(r'(ensures|requires|open):|impl \[[^\]]+\]:', body):
                grp, ii, cur = ind, None, None; continue
            if grp is not None and ind <= grp: grp, ii = None, None
            if ii is None: ii = ind if grp is not None else least
            if ind == ii:
                m = re.match(r'(\S(?:.*?\S)?)  +(.*)', body) or re.match(r'(\S.*)', body)
                cur = m.group(1); out[cur] = (m.group(2) if m.lastindex == 2 else '')
            elif cur: out[cur] += ' ' + body
    return out

def root_name(root):
    """The package's name: the first heading of its manifest, package.md."""
    for line in open(os.path.join(root, 'package.md'), encoding='utf-8'):
        if line.startswith('# '): return line[2:].strip()
    sys.exit(f'{root}/package.md: no first-level heading naming the package')

def manifest_paths(root):
    """The module paths the manifest lists: the item names of its Modules section's first fenced block."""
    t = open(os.path.join(root, 'package.md'), encoding='utf-8').read()
    m = re.search(r'^## Modules[ \t]*\n.*?^```[^\n]*\n(.*?)^```', t, re.S | re.M)
    if not m: return []
    lines = [l for l in m.group(1).split('\n') if l.strip()]
    least = min(len(l) - len(l.lstrip(' ')) for l in lines)
    return [l.split()[0] for l in lines if len(l) - len(l.lstrip(' ')) == least]

def modules(root):
    """Each module, keyed by its path ('' for the root): its name, its directory, its interfaces' headers by stem,
    and its body."""
    mods = {}
    for path in [''] + manifest_paths(root):
        name = path.rstrip('/').split('/')[-1] if path else ROOT
        d = os.path.join(root, path)
        heads = {}
        for h in sorted(glob.glob(os.path.join(d, '*.h.md'))):
            stem = os.path.basename(h)[:-len('.h.md')]
            heads[stem[:-len('.private')] if stem.endswith('.private') else stem] = h
        mods[path] = (name, d, heads, os.path.join(d, f'{name}.body.md'))
    return mods

def files_of(mods, path):
    """A module's own files: the Markdown files of its directory, its nested modules' directories aside."""
    return sorted(glob.glob(os.path.join(mods[path][1], '*.md')))

old, new = sys.argv[1], sys.argv[2]
ROOT = root_name(new)
mods = modules(new)
oldpath = lambda p: os.path.join(old, os.path.relpath(p, new))

# Items: (module path, interface stem or None for the body, item name, how).
changed = []
for path, (name, d, heads, body) in mods.items():
    for stem, p in list(heads.items()) + [(None, body)]:
        o, n = items(oldpath(p)), items(p)
        for it, stmt in o.items():
            if it not in n: changed.append((path, stem, it, 'gone'))
            elif ' '.join(n[it].split()) != ' '.join(stmt.split()): changed.append((path, stem, it, 'changed'))
        for it in n:
            if it not in o: changed.append((path, stem, it, 'new'))

def spellings(path, stem, it, inside):
    name = mods[path][0]
    default = stem == name
    outside = set() if stem is None else ({f'{name}.{it}'} if default else {f'{name}.{stem}.{it}'})
    if inside:
        return {it} | ({f'{stem}.{it}'} if stem and not default else set()) | ({f'default.{it}'} if default else set()) | outside
    return outside

blank_code = lambda t: re.sub(r'`[^`\n]*`', lambda x: ' ' * len(x.group()), t)
for path, stem, it, how in changed:
    name = mods[path][0]
    print(f'## {name}{"." + stem if stem and stem != name else ""}.{it} ({how})' if stem else f'## {name} body: {it} ({how})')
    if how == 'new': continue
    for p2 in mods:
        want = spellings(path, stem, it, p2 == path)
        if not want: continue
        for f in files_of(mods, p2):
            text = open(f, encoding='utf-8').read(); lines = text.split('\n'); seen = set()
            for m in re.finditer(r'\[([^\]\n]+(?:\n *[^\]\n]+)*)\](?!\()', blank_code(text)):
                if ' '.join(m.group(1).split()) in want:
                    i = text.count('\n', 0, m.start()) + 1
                    if i in seen: continue
                    seen.add(i); print(f'  {os.path.relpath(f, new)}:{i}: {lines[i-1].strip()[:160]}')

# Decisions: an entry whose text changed, or is gone; its sites are every other line citing its ID.
def entries(p):
    out = {}
    if not os.path.exists(p): return out
    for e in re.split(r'\n(?=\*\*[A-Z][A-Za-z0-9-]*-\d+\. )', open(p, encoding='utf-8').read()):
        m = re.match(r'\*\*([A-Z][A-Za-z0-9-]*-\d+)\. ', e)
        if m: out[m.group(1)] = ' '.join(e.split())
    return out
allfiles = [f for p2 in mods for f in files_of(mods, p2)]
for path, (name, d, heads, body) in mods.items():
    dec = os.path.join(d, f'{name}.decisions.md')
    o, n = entries(oldpath(dec)), entries(dec)
    for i in sorted(o, key=lambda x: int(x.rsplit('-', 1)[1])):
        how = 'gone' if i not in n else ('changed' if n[i] != o[i] else None)
        if not how: continue
        print(f'## {i} ({how})')
        for f in allfiles:
            for k, line in enumerate(open(f, encoding='utf-8'), 1):
                if re.search(r'(?<![A-Za-z0-9-])' + re.escape(i) + r'(?![0-9-])', line) and not line.startswith(f'**{i}. '):
                    print(f'  {os.path.relpath(f, new)}:{k}: {line.strip()[:160]}')

# Relations: for an item changed in an interface, the places relating to that interface: a front's `includes` or
# `implements`, an `impl` line, and the body of a module implementing its default.
for path, stem, it, how in changed:
    if how == 'new' or stem is None: continue
    name, d, heads, body = mods[path]
    default = stem == name
    inside = {stem} | ({'default'} if default else set())
    outside = {name} if default else {f'{name}.{stem}'}
    sites = []
    for p2 in mods:
        for f in files_of(mods, p2):
            for k, line in enumerate(open(f, encoding='utf-8'), 1):
                found = re.findall(r'^\s*(?:includes|implements):\s*\[?([^\]\n]*)\]?', line) + re.findall(r'^\s*impl \[([^\]]+)\]:', line) + re.findall(r'^\s*-\s+(\S+)\s*$', line)
                for g in found:
                    for x in [y.strip().strip('"\'') for y in g.split(',') if y.strip()]:
                        if (p2 == path and x in inside) or x in outside:
                            sites.append(f'  {os.path.relpath(f, new)}:{k}: {line.strip()[:160]}')
    if default and os.path.exists(body):
        sites.append(f'  {os.path.relpath(body, new)}: the body of [{name}], implementing its default')
    if sites:
        print(f'## {name}{"" if default else "." + stem}.{it} (relations)')
        for x in dict.fromkeys(sites): print(x)
