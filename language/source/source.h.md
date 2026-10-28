Where each thing of a [model.package] is written, for whoever writes one, person or agent, and for any tool that reads one: which [layout.source file] and which [grammar.construct] of it writes each, the [place] it stands at, the checks that rest on more than one part, and the [problem]s, each at its [place]; what a [model.package] means, how its files lie and how their text is written are not stated here.

## Structure

```
  place              where something stands in a [layout.package]: a file, by its
                     [layout.path] and its name, and, where it is written within the file,
                     the line it opens on; or, where it stands in no file, a directory, by
                     its [layout.path]
  package            where a [model.package] is written: a [layout.package], its [place] its
                     [layout.manifest]; its name the [grammar.manifest]'s name, however its
                     top's directory is named; its [model.version] the [grammar.manifest]'s
                     version; and its [model.edition] the [model.version] the
                     [grammar.manifest]'s edition names, of the language's definition its
                     link opens
  module             where a [model.module] is written: the root at the [layout.package]'s
                     top, its name the [model.package]'s, and what it is for, and its secret,
                     the [grammar.manifest]'s [grammar.lead], with any [grammar.lead] its
                     [layout.body] holds, its [place] where the [grammar.manifest]'s name is
                     written; and each other at the directory an [grammar.item] of the
                     [grammar.manifest] names by its [layout.path], where it stands one step
                     below another [model.module]'s directory, the root's being the top, that
                     [model.module] its parent; its name the [layout.path]'s last step; what
                     it is for, and its secret, the [grammar.item]'s statement and its
                     [layout.body]'s [grammar.lead]; and its [place] where the [grammar.item]
                     is written
  relation name      a name of a [grammar.front], or the [grammar.reference] of an `impl`
                     [grammar.opener], which is no [model.reference] but names what one spelt
                     as it is would land on, standing in the [model.interface] its
                     [layout.header] or [layout.private header] writes, or in the
                     [model.body] its [layout.body] writes; its [place] where it is written
  interface          where a [model.interface] is written: a [layout.header] or a
                     [layout.private header], its [place], in the directory of the
                     [model.module] that provides it; its name the file's stem; private where
                     it is a [layout.private header]; what it offers its [grammar.lead]; the
                     [model.interface]s it includes those the [relation name]s of its
                     [grammar.front]'s `includes` name; and its [model.item]s those of its
                     [grammar.view]s
  default interface  where a [model.default interface] is written: the [layout.header] in its
                     [model.module]'s directory whose stem is that [model.module]'s name, the
                     root's among them, named as the [model.package]
  item               where a [model.item] is written: an [grammar.item] of a [grammar.view] of
                     a [layout.source file] writing a [model.interface] or a [model.body], its
                     [place] where it is written; its name and its statement the
                     [grammar.item]'s; its [model.view] its [grammar.view]'s; its
                     [model.label]s the [grammar.label]s that end it; and, of the
                     [grammar.opener]s over its group, `ensures:` or `requires:` its
                     [model.direction], where it is a rule, and `open:` making it an
                     [model.open question]
  body               where a [model.body] is written: the [layout.body] in its
                     [model.module]'s directory, its [place], its [model.item]s those of its
                     [grammar.view]s; the [model.interface]s its [model.module] implements
                     being its [model.default interface], where it provides one, and those the
                     [relation name]s of its [grammar.front]'s `implements` name; and, where
                     that directory holds no [layout.body], no [model.body], its
                     [model.module] implementing nothing
  pair               where a [model.pair] is written: an [grammar.item] of a [layout.body]
                     under an `impl` [grammar.opener], its [place] where it is written, which
                     writes the [model.item] its [model.module] states is with the
                     [model.interface] the [grammar.opener]'s [relation name] names
  decision           where a [model.decision] is written: an [grammar.entry] of the
                     [layout.decisions] in its [model.module]'s directory, its [place] where
                     it is written; its ID the [grammar.entry]'s; its statement the
                     [grammar.entry]'s, with what was decided after it; each of its
                     [model.field]s the lines under the word of that [model.field]'s name;
                     and its [model.label]s the [grammar.label]s that end it
  reference          where a [model.reference] is written: a [grammar.reference] within what
                     writes an [model.item] or a [model.decision], or what a [model.module]
                     is said to be for or an [model.interface] to offer, as [item],
                     [decision], [module] and [interface] have it, standing in that, its
                     [place] where it is written; its names the [grammar.reference]'s
                     bracketed name, parted at each `.`, or the ID that a bare one writes
  core word          what a [grammar.core word] writes: the [model.item] of [model] its word
                     names, as the [model.edition] its [model.package] is written in defines
                     it, and no [model.reference]
  problem            what the language counts as wrong in a [layout.package], whoever finds
                     it: a `requires:` rule of [layout], [grammar], [model] or these
                     [model.item]s, broken, at the [place] of each thing that breaks it, that
                     of a thing of the [model.package] where these [model.item]s write it;
                     what was written still read as written, as [grammar.slips] reads a slip;
                     and no rule of [principles], whose breach is of another kind, review's
                     and a checker's
```

## Rules

```
  ensures:
    join alone  these [model.item]s state no meaning [model] does not, no file [layout] does
                not and no [grammar.construct] [grammar] does not: each says where a thing of
                a [model.package] is written, or, where the parts meet, what is wrong
  requires:
    listed      every [grammar.item] of the [grammar.manifest] writes a [model.module], as
                [module] has it
    placed      every [layout.source file] stands in the directory of a [model.module]
    top stem    at the [layout.package]'s top, a [layout.body]'s and a [layout.decisions]'
                stem is the [model.package]'s name
    root lead   the [layout.body] at the [layout.package]'s top holds no [grammar.lead]
    relations   every [relation name] names a [model.interface], and that of an `impl`
                [grammar.opener] one its [model.module] implements
```
