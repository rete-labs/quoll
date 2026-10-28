How a [package] lies on disk, for whoever writes one and for any tool that reads one: its [source file]s, the kind of each, as [kind by name] tells it; and the [project] that may hold [package]s.

## Structure

```
  package           a directory, freely named, and every directory below it, with the files
                    standing in each; anything whose name opens with `.` is left out, with all
                    it holds
  path              where a directory stands in a [package]: the names of the directories
                    leading to it from the [package]'s top, in order, joined by `/`, as
                    `foo/bar`, the top's own being empty; the same on every system, and never
                    a file system's own path, which a tool maps it onto; a file stands at the
                    [path] of the directory holding it
  manifest          the file named `package.md` at the [package]'s top
  build             the file named `build.md` at the [package]'s top, where the [package] has
                    one
  header            a file of the [package] named `<stem>.h.md`
  private header    a file of the [package] named `<stem>.private.h.md`
  body              a file of the [package] named `<stem>.body.md`
  decisions         a file of the [package] named `<stem>.decisions.md`
  source file       a file of one of the language's six kinds, which its name and its [path]
                    make it: the [manifest], the [build], a [header], a [private header], a
                    [body] or [decisions]
  project           a directory holding [package]s, each in a directory below its top, none
                    within another's
  open:
    tests           the [tests]' files are of a kind of [source file] not yet given: their
                    names, and where they stand, wait for the first [package] with [tests]
    project files   the [project]'s own files, their names and their form, wait for a
                    [project] with a second [package]
```

## Rules

```
  ensures:
    kind by name    which kind a [source file] is comes from its name and its [path] alone,
                    never from what it holds
    exact case      a name makes a [source file] of a kind only where it is `package.md` or
                    `build.md`, or ends in `.h.md`, `.private.h.md`, `.body.md` or
                    `.decisions.md`, character for character, case included
    private suffix  a name ending in `.private.h.md` makes a [private header], never a [header]
    top only        `package.md` and `build.md` make the [manifest] and the [build] at the
                    [package]'s top alone, and below it are of no kind
  requires:
    one manifest    every [package] holds a [manifest]
    one each        no directory of the [package], its top included, holds more than one
                    [body], nor more than one [decisions]
    stem            below the [package]'s top, a [body]'s and a [decisions]' stem is the name
                    of the directory holding it, the last step of its [path], as
                    `foo/bar/bar.body.md`; one with another stem is still of its kind, its
                    stem breaking this rule; at the [package]'s top, this rule fixes no stem
```
