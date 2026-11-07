How a [package] lies on disk, for whoever writes one and for any tool that reads one: its [source file]s, the kind of each, as [kind by name] tells it; the [content hash] that identifies its delivered source; and the [workspace] that may hold [package]s.

## Structure

```
  package              a directory, freely named, and every directory below it, with the files
                       standing in each; anything whose name opens with `.` is left out, with
                       all it holds
  workspace            an unnamed directory holding [package]s, each in a directory below its
                       top, none within another's; its directory alone identifies it
  path                 where a directory stands in a [package] or [workspace]: the names of
                       the directories leading to it from that top, in order, joined by `/`,
                       as `foo/bar`, the top's own being empty; the same on every system, and
                       never a file system's own [path], which a tool maps it onto; a file stands
                       at the [path] of the directory holding it
  manifest             the public file named `package.quoll.toml` at the [package]'s top
  modules              the private file named `modules.quoll.toml` at the [package]'s top,
                       listing the [path] of each member directory
  lock                 the file named `package.lock.quoll.toml` at the [package]'s top, holding
                       the exact source graph resolved for that [package]
  build                the file named `build.md` at the [package]'s top, where the [package] has one
  header               a file of the [package] named `<stem>.h.md`
  private header       a file of the [package] named `<stem>.private.h.md`
  body                 a file of the [package] named `<stem>.body.md`
  decisions            a file of the [package] named `<stem>.decisions.md`
  workspace manifest   the file named `workspace.quoll.toml` at the [workspace]'s top
  workspace decisions  the file named `workspace.decisions.md` at the [workspace]'s top, where
                       the [workspace] has workspace-level rationale to record, absent where it
                       has none
  source file          a file of one of the language's kinds, which its name and its [path]
                       make it: the [manifest], the [modules], the [lock], the [build], a
                       [header], a [private header], a [body], [decisions], the
                       [workspace manifest] or the [workspace decisions]
  content hash         Go `dirhash.Hash1` with a SHA-256 multihash over the portable regular files
                       below a [package]'s [path] at a resolved commit: sort the package-relative
                       UTF-8 regular-file [path]s, each formed from the containing directory's
                       [path] followed by `/` and the file's name, or from the file's name
                       alone at the [package]'s top; hash each file's raw Git blob bytes with
                       SHA-256, append the lowercase hexadecimal digest, two spaces, that
                       complete regular-file [path] and a newline, then hash the complete
                       summary with SHA-256 and encode the raw outer digest under the community
                       [multihash specification](https://github.com/multiformats/multihash)
                       as `0x12 0x20`, the SHA-256 code and 32-byte digest length, followed
                       by its 32 bytes; executable and other special modes, symlinks
                       and Git submodule gitlinks are rejected, as are case-insensitive
                       [path] collisions and Windows-reserved [path]s; content has no
                       line-ending or smudge-filter conversion, empty directories and `.git`
                       metadata are absent, and files outside the [package]'s [path],
                       including [workspace] files and other [package]s, are excluded
  open:
    tests              the [tests]' files are of a kind of [source file] not yet given: their
                       names, and where they stand, wait for the first [package] with [tests]
```

## Rules

```
  ensures:
    kind by name     which kind a [source file] is comes from its name and its [path] alone,
                     never from what it holds
    exact case       a name makes a [source file] of a kind only where it is one of the fixed
                     names the fixed files above give, or ends in `.h.md`, `.private.h.md`,
                     `.body.md` or `.decisions.md`, character for character, case included
    private suffix   a name ending in `.private.h.md` makes a [private header], never a [header]
    top only         the fixed names of the [manifest], [modules], [lock] and [build] make
                     those kinds at the [package]'s top alone, and those of the
                     [workspace manifest] and [workspace decisions] at the [workspace]'s top
                     alone; below that top they are of no kind
  requires:
    one manifest     every [package] holds a [manifest]
    one modules      every [package] holds a [modules]
    one lock         every [package] holds a [lock]
    workspace files  every [workspace] holds a [workspace manifest], and holds
                     [workspace decisions] exactly where it has workspace-level rationale to record
    one each         no directory of the [package], its top included, holds more than one
                     [body], nor more than one [decisions]
    stem             below the [package]'s top, a [body]'s and a [decisions]' [stem] is the name
                     of the directory holding it, the last step of its [path], as
                     `foo/bar/bar.body.md`; one with another [stem] is still of its kind, its
                     [stem] breaking this rule; at the [package]'s top, this rule fixes no [stem]
```
