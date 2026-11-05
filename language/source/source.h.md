Where each thing of a [model.package] is written, for whoever writes one, person or agent, and for any tool that reads one: which [layout.source file] and which [grammar.construct] of it writes each, the [place] it stands at, the checks that rest on more than one part, and the [problem]s, each at its [place]; what a [model.package] means, how its files lie and how their text is written are not stated here.

## Structure

```
  place               where something stands in a [layout.package] or [layout.workspace]: a
                      file, by its [layout.path] and its name, and, where it is written within
                      the file, the line it opens on; or, where it stands in no file, a
                      directory, by its [layout.path]
  package             where a [model.package] is written: a [layout.package], its [place] its
                      [layout.manifest]; its [model.package id] the [grammar.manifest]'s `id`,
                      however its top's directory is named; its name that identity's final
                      segment; its [model.edition] the [model.version] the [grammar.manifest]'s
                      `edition` names; its [model.dependency]s the [grammar.manifest]'s
                      `dependencies`; and its selected [model.version] and exact source the
                      [model.release] or [model.resolution] that selected it, never a `version`
                      field of its own
  workspace           where a [model.workspace] is written: a [layout.workspace], its [place]
                      its [layout.workspace manifest], and its member [model.package]s those at
                      the workspace-relative [layout.path]s in the
                      [grammar.workspace manifest]'s `packages`
  module              where a [model.module] is written: the root at the [layout.package]'s
                      top, its name the [model.package]'s, what it is for and its secret the
                      [grammar.manifest]'s `description`, its [place] the [layout.manifest];
                      and each other at the directory a package-relative [layout.path] in the
                      [grammar.modules]' `modules` names, where it stands one step below another
                      [model.module]'s directory, the root's being the top, that [model.module]
                      its parent; its name the [layout.path]'s last step; what it is for and its
                      secret its [layout.body]'s [grammar.lead] or, where it has no [model.body],
                      the [grammar.lead] of the [layout.header] whose stem is its name or, where
                      it has no such default [layout.header], of the named [layout.header] or
                      [layout.private header] whose [grammar.front] holds `"module lead" = true`;
                      and its [place] where its [layout.path] is written
  relation name       a name of a [grammar.front], or the [grammar.reference] of an `impl`
                      [grammar.opener], which is no [model.reference] but names what one spelt
                      as it is would land on, standing in the [model.interface] its
                      [layout.header] or [layout.private header] writes, or in the
                      [model.body] its [layout.body] writes; its [place] where it is written
  alias               a local name declared by one value of a [grammar.front]'s `aliases` table:
                      a Package URL value names a [model.dependency], and a qualified-reference
                      value names a public [model.interface] or [model.item] reached through
                      one; the [alias] is visible only in the [layout.header],
                      [layout.private header] or [layout.body] declaring it, an unversioned
                      Package URL follows [model.version] updates, and a versioned or
                      partial-selector value distinguishes simultaneously visible
                      [model.version]s; its [place] where it is written
  interface           where a [model.interface] is written: a [layout.header] or a
                      [layout.private header], its [place], in the directory of the
                      [model.module] that provides it; its name the file's stem; private where
                      it is a [layout.private header]; what it offers its [grammar.lead]; the
                      [model.interface]s it includes those the [relation name]s of its
                      [grammar.front]'s `includes` name; and its [model.item]s those of its
                      [grammar.view]s
  default interface   where a [model.default interface] is written: the [layout.header] in its
                      [model.module]'s directory whose stem is that [model.module]'s name, the
                      root's among them, named as the [model.package]
  item                where a [model.item] is written: an [grammar.item] of a [grammar.view] of
                      a [layout.source file] writing a [model.interface] or a [model.body], its
                      [place] where it is written; its name and its statement the
                      [grammar.item]'s; its [model.view] its [grammar.view]'s; its
                      [model.label]s the [grammar.label]s that end it; and, of the
                      [grammar.opener]s over its group, `ensures:` or `requires:` its
                      [model.direction], where it is a rule, and `open:` making it an
                      [model.open question]
  body                where a [model.body] is written: the [layout.body] in its
                      [model.module]'s directory, its [place], its [model.item]s those of its
                      [grammar.view]s; the [model.interface]s its [model.module] implements
                      being its [model.default interface], where it provides one, and those the
                      [relation name]s of its [grammar.front]'s `implements` name; and, where
                      that directory holds no [layout.body], no [model.body], its
                      [model.module] implementing nothing
  pair                where a [model.pair] is written: an [grammar.item] of a [layout.body]
                      under an `impl` [grammar.opener], its [place] where it is written, which
                      writes the [model.item] its [model.module] states is with the
                      [model.interface] the [grammar.opener]'s [relation name] names
  decision            where a [model.decision] is written: an [grammar.entry] of the
                      [layout.decisions] in its [model.module]'s directory, its [place] where
                      it is written; its ID the [grammar.entry]'s; its statement the
                      [grammar.entry]'s, with what was decided after it; each of its
                      [model.field]s the lines under the word of that [model.field]'s name;
                      and its [model.label]s the [grammar.label]s that end it
  workspace decision  where a [model.workspace]'s [model.decision] is written: an
                      [grammar.entry] of the [layout.workspace decisions], its [place] where it
                      is written and its ID, statement, [model.field]s and [model.label]s read
                      as [decision] has them; it may name member [model.package]s and their
                      public [model.interface]s, and no [model.module] of a member sees it
  reference           where a [model.reference] is written: a [grammar.reference] within what
                      writes a [model.item] or a [model.decision], or what a [model.module]
                      is said to be for or a [model.interface] to offer, as [item],
                      [decision], [module] and [interface] have it, standing in that, its
                      [place] where it is written; its names the [grammar.reference]'s
                      bracketed name, parted at each `.`, or the ID that a bare one writes;
                      where its first segment names an [alias] of the same file, that [alias]
                      supplies what the [model.reference] rests on: with no later segment, the
                      [alias]'s [model.dependency], public [model.interface] or public
                      [model.item] itself; after a [model.dependency] [alias], later segments
                      follow only [model.interface]s provided by its root; after a public
                      [model.interface] [alias], a later segment names one of its
                      [model.item]s; and no later segment follows an [model.item] [alias];
                      an [alias]'s qualified-reference value resolves by these same rules in
                      its declaring file, its first segment another [alias] or an unambiguous
                      default leaf; where no [alias] supplies the first segment, a
                      [model.dependency] [model.reference]'s first segment is an unambiguous
                      default leaf, and the rest follows only [model.interface]s provided by
                      the [model.dependency]'s root
  core word           what a [grammar.core word] writes: its word's [model.item] in the
                      [model.module] providing [model.item], as the [model.edition] its
                      [model.package] is written in defines it, and no [model.reference]
  package hash        where a [model.resolution]'s selected-tree hash is written: the `hash` of a
                      dependency table of the [grammar.lock], computed as the
                      [layout.content hash] of the selected [layout.package] tree
  lock                where a [model.lock] is written: the [layout.lock] beside its root
                      [layout.manifest], its entries the [grammar.lock]'s direct and transitive
                      `dependencies` and their `sources`; it is committed for the root's own
                      checks, while a [model.dependency]'s [layout.lock] supplies only
                      source-locator hints to a consumer resolving its own [model.lock]
  problem             what the language counts as wrong in a [layout.package] or
                      [layout.workspace], whoever finds it: a `requires:` rule of the
                      [model.module]s providing [layout.source file], [grammar.construct] or
                      [model.item], or of these [model.item]s, broken, at the [place] of each
                      thing that breaks it, that of a thing of the [model.package] where these
                      [model.item]s write it; what was written still read as written, as
                      [grammar.slips] reads a slip; and no rule of review's practice, whose
                      breach is of another kind, review's and a checker's
```

## Rules

```
  ensures:
    join alone       these [model.item]s state no meaning the [model.module] providing
                     [model.item] does not, no file the [model.module] providing
                     [layout.source file] does not and no [grammar.construct] the [model.module]
                     providing [grammar.construct] does not: each says where a thing of a
                     [model.package] or [model.workspace] is written, or, where the parts meet,
                     what is wrong
  requires:
    listed           every [layout.path] of the [grammar.modules] writes one [model.module],
                     every non-root [model.module] is listed exactly once, and no [layout.path]
                     is listed for the root
    placed           every [layout.source file] of a [layout.package] stands in the directory
                     of a [model.module], and the [layout.workspace manifest] and
                     [layout.workspace decisions] stand at their [model.workspace]'s top
    top stem         at the [layout.package]'s top, a [layout.body]'s and a [layout.decisions]'
                     stem is the [model.package]'s name
    root lead        the [layout.body] at the [layout.package]'s top holds no [grammar.lead]
    one module lead  at most one named [layout.header] or [layout.private header] of a
                     [model.module] holds `"module lead" = true` in its [grammar.front]; where
                     the [model.module] has neither a [layout.body] nor a [layout.header] whose
                     stem is its name, exactly one named [layout.header] or [layout.private header]
                     bears that declaration and supplies the [model.module]'s purpose and secret
    relations        every [relation name] names a [model.interface], and that of an `impl`
                     [grammar.opener] one its [model.module] implements
    public surface   every public [layout.header] at the [layout.package]'s top writes one of
                     the [model.package]'s public [model.interface]s, every
                     [layout.private header] there a private one, and no [layout.manifest] or
                     membership list duplicates them; [model.public closure] is checked over
                     these [layout.header]s and every [grammar.reference] their inclusions bring in
                     recursively, with no further include or [model.uses] declaration
    default leaves   every [model.dependency]'s unversioned [model.package id] leaf is available
                     as a default local name throughout the depending [layout.package], without
                     a declaration
    alias scope      an [alias] applies only to its own file, never to a sibling [layout.header],
                     [layout.body] or [layout.private header]; every target is visible there, and
                     an unversioned [alias] is ambiguous where several selected [model.version]s
                     of its [model.package id] are visible, requiring a selector-qualified [alias]
    alias acyclic    resolving an [alias]'s qualified target through other [alias]s never returns
                     to an [alias] already being followed; such a cycle is a [problem] at each
                     [alias] in it
    alias unique     an [alias] collides with no other visible [model.dependency] name, no other
                     [alias], and no local name in its file's [model.reference] namespace; where two
                     visible [model.dependency]s share a leaf, the ambiguous default does not
                     resolve in that file and each used [model.dependency] needs a distinct [alias]
```
