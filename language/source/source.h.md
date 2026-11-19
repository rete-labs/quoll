+++
prelude = []
+++
Where each thing of a canonical Quoll source [model.graph.package] or [model.graph.workspace] is written, for whoever writes one, person or agent, and for any tool that reads one: which [layout.source file] and which [grammar.construct] of it writes each, the [place] it stands at, the checks that rest on more than one part, and the [problem]s, each at its [place]; how [language.layout], [language.grammar] and these joins supply the [model.profile.canonical profile]'s concrete representation; and which other representation joins remain open.

## Structure

```
  place               where something stands in a [layout.package] or [layout.workspace]: a file, by
                      its [layout.path] and its name, and, where it is written within the file, the
                      line it opens on; or, where it stands in no file, a directory, by its
                      [layout.path]

  package             where a canonical Quoll source [model.graph.package] is written: a
                      [layout.package], its [place] its [layout.manifest]; its
                      [model.graph.package id] the [grammar.manifest]'s `id`, however its top's
                      directory is named; its name that identity's final segment; its
                      [model.graph.edition] the [model.graph.version] the [grammar.manifest]'s
                      `edition` names; its [model.graph.dependency]s the [grammar.manifest]'s
                      `dependencies`; and its selected [model.graph.version] and exact source the
                      [model.graph.release] or [model.graph.resolution] that selected it
  workspace           where a canonical Quoll source [model.graph.workspace] is written: a
                      [layout.workspace], its [place] its [layout.workspace manifest]; its
                      [model.graph.edition] the [model.graph.version] the
                      [grammar.workspace manifest]'s `edition` names, fixing the grammar and source
                      meaning of the [layout.workspace]'s own files and no member's; its member
                      [model.graph.package]s those at the workspace-relative [layout.path]s in the
                      [grammar.workspace manifest]'s `packages`, each naming its own mandatory
                      [model.graph.edition] and inheriting none of the [layout.workspace]'s; its
                      [model.kernel.decision]s those of its [layout.workspace decisions] where that
                      file stands, none where absent
  assembly            where a [model.generation.assembly] is written under the
                      [model.profile.canonical profile]: the [layout.assembly] at its authoritative
                      source [model.graph.package]'s top, its [place] where it is written and its
                      text the [grammar.assembly]; the [layout.assembly form] and
                      [model.generation.assembly form] remain open at the first derived-target
                      implementation

  module              where a [model.kernel.module] is written: the root at the [layout.package]'s
                      top, its name the [model.graph.package]'s, what it is for and its secret the
                      [grammar.manifest]'s `description`, its [place] the [layout.manifest]; and
                      each other at the directory a package-relative [layout.path] in the
                      [grammar.modules]' `modules` names, where it stands one step below another
                      [model.kernel.module]'s directory, the root's being the top, that
                      [model.kernel.module] its parent; its name the [layout.path]'s last step; what
                      it is for and its secret its [layout.body]'s [grammar.lead] or, where it has
                      no [model.kernel.body], the [grammar.lead] of the [layout.header] whose
                      [layout.stem] is its name or, where it has no such default [layout.header], of
                      the named [layout.header] or [layout.private header] whose [grammar.front]
                      holds `"module lead" = true`; and its [place] where its [layout.path] is
                      written
  interface           where a [model.kernel.interface] is written: a [layout.header] or a
                      [layout.private header], its [place], in the directory of the
                      [model.kernel.module] that provides it; its name the file's [layout.stem];
                      private where it is a [layout.private header]; what it offers its
                      [grammar.lead]; the [model.kernel.interface]s it includes those the
                      [relation name]s of its [grammar.front]'s `includes` name; and its
                      [model.kernel.item]s those of its [grammar.view]s together with each included
                      [model.kernel.interface]'s, all direct as [model.kernel.interface] has them,
                      inclusion creating no nested [model.kernel.interface] path or
                      [model.graph.exposure]
  default interface   where a [model.kernel.default interface] is written: the [layout.header] in
                      its [model.kernel.module]'s directory whose [layout.stem] is that
                      [model.kernel.module]'s name, the root's among them, named as the
                      [model.graph.package]
  item                where a [model.kernel.item] is written: a [grammar.item] of a [grammar.view]
                      of a [layout.source file] writing a [model.kernel.interface] or a
                      [model.kernel.body], its [place] where it is written; its name and its
                      statement the [grammar.item]'s; its [model.kernel.view] its [grammar.view]'s;
                      its [model.rich.label]s the [grammar.label]s that end it; and, of the
                      [grammar.opener]s over its group, `ensures:` or `requires:` its
                      [model.rich.direction], where it is a rule, and `open:` making it a
                      [model.rich.open question]
  body                where a [model.kernel.body] is written: the [layout.body] in its
                      [model.kernel.module]'s directory, its [place], its [model.kernel.item]s those
                      of its [grammar.view]s; the [model.kernel.interface]s its
                      [model.kernel.module] implements being its [model.kernel.default interface],
                      where it provides one, and those the [relation name]s of its [grammar.front]'s
                      `implements` name; and, where that directory holds no [layout.body], no
                      [model.kernel.body], its [model.kernel.module] implementing nothing
  pair                where a [model.kernel.pair] is written: a [grammar.item] of a [layout.body]
                      under an `impl` [grammar.opener], its [place] where it is written, which
                      writes the [model.kernel.item] its [model.kernel.module] states is with the
                      [model.kernel.interface] the [grammar.opener]'s [relation name] names
  decision            where a [model.kernel.decision] is written: a [grammar.entry] of the
                      [layout.decisions] in its [model.kernel.module]'s directory, its [place] where
                      it is written; its ID the [grammar.entry]'s; its statement the
                      [grammar.entry]'s, with what was decided after it; each of its
                      [model.kernel.field]s the lines under the word of that [model.kernel.field]'s
                      name; and its [model.rich.label]s the [grammar.label]s that end it
  workspace decision  where a [model.graph.workspace]'s [model.kernel.decision] is written: a
                      [grammar.entry] of the [layout.workspace decisions], its [place] where it is
                      written and its ID, statement, [model.kernel.field]s and [model.rich.label]s
                      read as [decision] has them; an active one carries its rationale directly,
                      with no `*Stated by*` [model.kernel.field]; it may name member
                      [model.graph.package]s and targets of their root-reachable
                      [model.graph.exposure]s directly or through an [alias], and no
                      [model.kernel.module] of a member sees it
  exposure            where a [model.graph.exposure] is written: one mapping of a [grammar.front]'s
                      `exposes` table in a [layout.header] or [layout.private header], its [place]
                      where it is written; the [model.kernel.module] in whose directory that file
                      stands declares it, its key a name or path at that [model.kernel.module], and
                      its value naming one whole target [model.kernel.interface], never a
                      [model.kernel.module] or an individual [model.kernel.item], resolved under the
                      [model.profile.canonical reference] rule in that file, an explicit or derived
                      [alias] or included [edition alias] supplying spelling alone; it denotes that
                      same [model.kernel.interface], every [model.kernel.item] of it publicly
                      readable through it, and creates no [layout.header], [layout.private header],
                      [model.kernel.module], [model.kernel.interface] or [model.kernel.item]; only
                      one reached from the [model.graph.package] root by a chain of
                      [model.graph.exposure]s is root-reachable and forms part of its external
                      surface, every other being intermediate, and inclusion alone declares no
                      [model.graph.exposure]

  relation name       a name in an `implements` or `includes` list of a [grammar.front], or the
                      [grammar.reference] of an `impl` [grammar.opener], which is no
                      [model.profile.canonical reference] but names what one spelt as it is would
                      land on, standing in the [model.kernel.interface] its [layout.header] or
                      [layout.private header] writes, or in the [model.kernel.body] its
                      [layout.body] writes; its [place] where it is written
  alias               a local name declared by one value of a [grammar.front]'s `aliases` table or
                      derived from one mapping of its `use` table: an `aliases` Package URL value
                      names a [model.graph.dependency], and a qualified-reference value names a
                      [model.kernel.module], [model.kernel.interface] or [model.kernel.item] within
                      the declaring file's [model.kernel.sight], a same-package internal one
                      included or, in [layout.workspace decisions], a member [model.graph.package]
                      or the target of one of its root-reachable [model.graph.exposure]s under the
                      [model.graph.workspace]'s existing sight; a `use` key is one complete abstract
                      prefix reference and each string in its array is an explicit relative
                      continuation, resolved together by the [model.profile.canonical reference]
                      rule in the declaring file, with the continuation's final segment as the local
                      name and no [alias] for the prefix itself; array order has no meaning, and
                      duplicate continuations or competing derived names fail explicitly; every
                      explicit or derived [alias] is visible only in the [layout.header],
                      [layout.private header], [layout.body], [layout.decisions] or
                      [layout.workspace decisions] declaring it and changes spelling alone, never
                      its target's identity, sight or public availability, declaring no
                      [model.graph.exposure]; an unversioned Package URL follows
                      [model.graph.version] updates, and a versioned or partial-selector value
                      distinguishes simultaneously visible [model.graph.version]s; its [place] where
                      it is written

  edition alias       one of seven fixed terminal bindings supplied by the [model.graph.edition] a
                      [model.graph.package] or [model.graph.workspace] names: `workspace` to
                      `model.graph.workspace`, `package` to `model.graph.package`, `module` to
                      `model.kernel.module`, `interface` to `model.kernel.interface`, `item` to
                      `model.kernel.item`, `decision` to `model.kernel.decision`, and `uses` to
                      `model.kernel.uses`; an omitted `prelude` includes all seven, `prelude = []`
                      includes none, and a nonempty list includes exactly the fixed names it holds,
                      with unknown or duplicate names rejected; the selection belongs to one
                      [layout.header], [layout.private header], [layout.body], [layout.decisions] or
                      [layout.workspace decisions] alone and is never inherited, with the same rules
                      in package and [layout.workspace files]; an included spelling is reserved for
                      its fixed target and cannot be shadowed, an excluded spelling keeps its
                      ordinary local meaning, and no dotted continuation follows the fixed
                      [model.kernel.item] target; that target is read under the named
                      [model.graph.edition]'s authority, adding no ordinary
                      [model.graph.dependency], [model.kernel.sight], [model.graph.exposure],
                      [model.kernel.uses] or [model.graph.public closure] edge;
                      [model.profile.native profile]s retain ownership of their concrete notation

  reference           where a [model.profile.canonical reference] is written: a [grammar.reference]
                      within what writes a [model.kernel.item] or a [model.kernel.decision], or what
                      a [model.kernel.module] is said to be for or a [model.kernel.interface] to
                      offer, as [item], [decision], [module] and [interface] have it, standing in
                      that, its [place] where it is written; its names the [grammar.reference]'s
                      bracketed name, parted at each `.`, or the ID that a bare one writes; where
                      its first segment names an included [edition alias], that binding supplies its
                      fixed target, no later segment may follow, and the included spelling takes
                      precedence over ordinary local lookup; an excluded [edition alias] supplies no
                      binding; a local [model.kernel.structural path] and a package-qualified public
                      path are distinct complete references, neither expanding into the other by
                      removing a [model.graph.package] prefix, each identifying exactly one target
                      for every reader; the shortest unambiguous local, default and
                      [model.graph.dependency] forms remain, ambiguity fails rather than
                      module-first or facade precedence selecting a target, and [model.kernel.sight]
                      authorizes rather than selects one; where its first segment names an explicit
                      or derived [alias] of the same file, that [alias] supplies what the
                      [model.profile.canonical reference] rests on: with no later segment, the
                      [alias]'s [model.graph.dependency], member [model.graph.package],
                      [model.kernel.module], [model.kernel.interface] or [model.kernel.item] itself;
                      after a [model.graph.dependency] or member [model.graph.package] [alias],
                      later segments follow only [model.graph.exposure]s reachable from its root, as
                      [model.profile.canonical reference] has them; after a [model.kernel.module]
                      [alias], later segments follow the [model.profile.canonical reference] rule
                      for that [model.kernel.module], its provided [model.kernel.interface]s and
                      targets through [model.graph.exposure]s included; after a
                      [model.kernel.interface] [alias], a later segment names one of its
                      [model.kernel.item]s; and no later segment follows a [model.kernel.item]
                      [alias]; every explicit or derived [alias] target and continuation remains
                      within the declaring file's existing [model.kernel.sight]; an [alias]'s
                      qualified-reference value or a `use` prefix resolves by these same rules in
                      its declaring file, same-package [model.kernel.module],
                      [model.kernel.interface] and [model.kernel.item] names included, its first
                      segment another [alias], an included [edition alias] or an existing
                      unambiguous name there; in a [grammar.entry] of [layout.workspace decisions],
                      where no [alias] or included [edition alias] supplies the first segment, a
                      leading [grammar.package id] equal to a member's unversioned
                      [model.graph.package id] is one first segment, its full stops included, only a
                      full stop after it parting the continuation; that segment or a member leaf
                      unambiguous among the [model.graph.workspace]'s members names the member
                      [model.graph.package], and later segments follow only [model.graph.exposure]s
                      reachable from its root, as [model.profile.canonical reference] has them;
                      elsewhere, where no [alias] supplies the first segment, a package-qualified
                      public path begins with the current [model.graph.package]'s name or an
                      unambiguous default leaf of a [model.graph.dependency], and later segments
                      follow only [model.graph.exposure]s reachable from that
                      [model.graph.package]'s root, continuing through the exposed
                      [model.kernel.interface] to any of its [model.kernel.item]s, one of an exposed
                      [model.kernel.default interface] under every legal [model.graph.exposure] path
                      included; no public path traverses its private [model.kernel.module tree]
  source locator      where a canonical Quoll source [model.graph.source locator] is written: a
                      [grammar.source locator] in the `locator` of a source table of the
                      [grammar.lock], its [place] where it is written
  release tag         where a canonical Quoll source [model.graph.release]'s selected tag is
                      written: the [grammar.release tag] in the `tag` of a source table of the
                      [grammar.lock], its [place] where it is written
  package hash        where a canonical Quoll source [model.graph.resolution]'s selected-tree
                      content digest is written: the `hash` of a [model.graph.dependency] table of
                      the [grammar.lock], computed as the [layout.content hash] of the selected
                      [layout.package] tree
  lock                where a canonical Quoll source [model.graph.lock] is written: the
                      [layout.lock] beside its root [layout.manifest], its entries the
                      [grammar.lock]'s direct and transitive `dependencies` and their `sources`; it
                      is committed for the root's own checks, while a [model.graph.dependency]'s
                      [layout.lock] supplies only [model.graph.source locator] hints to a consumer
                      resolving its own [model.graph.lock]

  problem             what the language counts as wrong in a canonical Quoll source [layout.package]
                      or [layout.workspace], whoever finds it: a `requires:` rule of the
                      [model.kernel.module]s providing [layout.source file], [grammar.construct] or
                      [model.kernel.item], or of these [model.kernel.item]s, broken, at the [place]
                      of each thing that breaks it, that of a thing of the [model.graph.package]
                      where these [model.kernel.item]s write it; what was written still read as
                      written, as [grammar.slips] reads a slip; and no rule of review's practice,
                      whose breach is of another kind, review's and a checker's

  open:
    open joins        the concrete joins of [model.profile.native profile] artifacts,
                      [model.graph.native overlay]s, [model.graph.mixed graph] records,
                      [model.generation.target map]s, native [model.generation.trace link]s and
                      additional [model.kernel.view]s wait for the owning
                      [model.profile.native profile], [model.profile.framework rules] or first
                      derived-target implementation
```

## Rules

```
  ensures:
    join alone       these [model.kernel.item]s state no meaning the [model.kernel.module] providing
                     [model.kernel.item] does not, no file the [model.kernel.module] providing
                     [layout.source file] does not and no [grammar.construct] the
                     [model.kernel.module] providing [grammar.construct] does not: each says where a
                     thing of a canonical Quoll source [model.graph.package] or
                     [model.graph.workspace] is written, how the existing representation joins
                     satisfy the [model.profile.canonical profile]'s contract or, where the parts
                     meet, what is wrong
    canonical join   the [model.profile.canonical profile]'s concrete [model.kernel.sight],
                     notation, storage and representation joins are supplied by
                     [model.profile.canonical sight], [model.profile.canonical reference],
                     [layout.source file], [grammar.construct] and these [model.kernel.item]s
                     together, through their existing relations; this satisfies
                     [model.profile.profile semantics], declaring every settled mapping mechanical
                     under [model.profile.profile fidelity] and every join [open joins] leaves open
                     unsupported here rather than inferred, and requires no separate
                     [model.graph.package], [model.kernel.module], [model.kernel.body] or
                     [model.profile.profile adapter]

  requires:
    listed           every [layout.path] of the [grammar.modules] writes one [model.kernel.module],
                     every non-root [model.kernel.module] is listed exactly once, and no
                     [layout.path] is listed for the root
    placed           every [layout.source file] of a [layout.package] stands in the directory of a
                     [model.kernel.module], and the [layout.workspace manifest] and any
                     [layout.workspace decisions] stand at their [model.graph.workspace]'s top
    top stem         at the [layout.package]'s top, a [layout.body]'s and a [layout.decisions]'
                     [layout.stem] is the [model.graph.package]'s name
    root lead        the [layout.body] at the [layout.package]'s top holds no [grammar.lead]
    one module lead  at most one named [layout.header] or [layout.private header] of a
                     [model.kernel.module] holds `"module lead" = true` in its [grammar.front];
                     where the [model.kernel.module] has neither a [layout.body] nor a
                     [layout.header] whose [layout.stem] is its name, exactly one named
                     [layout.header] or [layout.private header] bears that declaration and supplies
                     the [model.kernel.module]'s purpose and secret

    relations        every [relation name] names a [model.kernel.interface], and that of an `impl`
                     [grammar.opener] one its [model.kernel.module] implements

    public surface   every declared [exposure] path identifies exactly one whole
                     [model.kernel.interface], though one [model.kernel.interface] may have several
                     [exposure] paths; at declaration time, every legal continuation of an
                     [exposure] path to a [model.kernel.item] of its exposed
                     [model.kernel.interface], one of a [model.kernel.default interface] under every
                     legal [exposure] path included, identifies exactly one [model.kernel.item], no
                     module-first or facade precedence resolving a collision; only root-reachable
                     [exposure]s form the [model.graph.package]'s external surface, no
                     [layout.header] or `includes` relation adding one implicitly;
                     [model.graph.public closure] follows those [exposure]s and every ordinary
                     [grammar.reference] in their exposed contracts or a supplied declaration
                     [model.kernel.unit] recursively, same-package references and
                     [model.kernel.reference]s of directly included [model.kernel.item]s among them,
                     with no further include or [model.kernel.uses] declaration; every such ordinary
                     [grammar.reference] lands on a [model.kernel.item] of a root-reachable exposed
                     [model.kernel.interface] of the same [model.graph.package] or on a
                     [model.graph.dependency]'s public [model.graph.package] surface, while one
                     resolved through an included [edition alias] lands on its fixed target under
                     the named [model.graph.edition]'s authority and adds no closure edge; no
                     same-unit-private or declaration-only exception admits another ordinary target;
                     a private or unexposed same-package target cannot satisfy closure, a
                     [model.graph.dependency] target must belong to that [model.graph.package]'s
                     surface, and an explicit or derived [alias] changes spelling alone, adding
                     neither [model.kernel.sight] nor an [exposure]; under
                     [model.profile.public reading], each canonical [model.profile.public unit] is
                     supplied as the identified [layout.source file] writing it, its [place] its
                     locator and its own [grammar.front] preserved, together with the
                     [model.graph.package]'s named [model.graph.edition] and public
                     [model.graph.dependency] declarations, so every [grammar.reference] resolves
                     from that collection and the named [model.graph.edition] alone; a
                     [model.profile.native profile]'s mappings and its
                     [model.profile.profile adapter] supply its non-file
                     [model.profile.public unit]s and locators
    default leaves   every [model.graph.dependency]'s unversioned [model.graph.package id] leaf is
                     available as a default local name throughout the depending [layout.package],
                     without a declaration

    alias scope      an explicit or derived [alias] applies only to its own [layout.header],
                     [layout.private header], [layout.body], [layout.decisions] or
                     [layout.workspace decisions], never to a sibling file or by
                     [model.kernel.module], [model.graph.package] or [model.graph.workspace]
                     inheritance; every target is already visible there, and the [alias] adds no
                     sight or public availability; an unversioned [alias] is ambiguous where several
                     selected [model.graph.version]s of its [model.graph.package id] are visible,
                     requiring a selector-qualified [alias]
    alias unique     an explicit or derived [alias] collides with no included [edition alias], no
                     other visible [model.graph.dependency] or [model.graph.workspace] member
                     [model.graph.package] name, no other explicit or derived [alias], and no local
                     name in its file's [model.profile.canonical reference] namespace; a declaration
                     using an included [edition alias]'s spelling fails whether its target is the
                     same or different, while a package-owned defining name may coexist without
                     shadowing that included spelling; where two visible [model.graph.dependency]s
                     share a leaf, the ambiguous default does not resolve in that file and each used
                     [model.graph.dependency] needs a distinct [alias]
    alias acyclic    resolving an [alias]'s qualified target or a `use` prefix through other
                     [alias]s never returns to an [alias] already being followed, independently of
                     declaration order; such a cycle is a [problem] at each [alias] in it
```
