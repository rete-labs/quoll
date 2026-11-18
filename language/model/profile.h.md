Concrete representation over the lower semantic layers: the abstract [profile semantics] contract and [profile fidelity], [representation profile]s, canonical bootstrap parity and native visibility and references, external realization roles and [target binding]s, [profile identity], [semantic delta]s and [framework rules].

## Structure

```
  representation profile  a [kernel.layer] over any selection of lower layers, giving a
                          [kernel.semantic profile]'s concrete visibility policy, notation, storage
                          and representation joins without changing their meanings; it may add
                          explicit optional or required profile-specific principles, including
                          generation and coding styles, without restating or weakening shared ones
  canonical profile       the [representation profile] for canonical Quoll, kept in `language` as
                          the bootstrap profile and available by default to pure and mixed
                          quollified packages; canonical full Quoll retains the
                          [rich.standard view]s, while co-located Quoll statements always use this
                          [kernel.semantic profile], never a target-specific dialect, and may select
                          only the [kernel.structural kernel] or add the [rich.rich contract] layer
                          independently of any native [kernel.semantic profile] beside them
  native profile          a [representation profile] interpreting native artifacts through the
                          common terms, owning native module and visibility mappings,
                          [graph.exposure] mappings, public-contract discovery, semantic conventions
                          and ecosystem-specific [graph.dependency] metadata, and declaring the
                          limits of each; it may combine native artifacts and co-located canonical
                          Quoll statements, and a native-only system needs no separate Quoll surface

  canonical sight         the current nested [graph.package sight] of canonical Quoll: a module sees
                          its [kernel.body]; its decisions, which no other module sees; the
                          interfaces it provides, private ones among them; those its parts, its
                          siblings and its ancestors' siblings provide, private ones aside, a part's
                          staying hidden outside its parent; every private interface an ancestor of
                          it provides, which so reaches every module below its own; and each
                          interface it implements
  canonical reference     a [kernel.reference] in canonical Quoll, resolved by one rule for internal
                          and external readers: a local structural reference follows a
                          [kernel.structural path], while a [graph.public reference] follows
                          root-reachable [graph.exposure]s from a package's name; the package name
                          is not a removable qualification prefix, neither path expands into the
                          other, every complete spelling identifies one target for every reader, and
                          no module-first precedence selects a target; within `std`, for example,
                          `[fs]` names the structural module and `[fs.path]` an item of its
                          [kernel.default interface], while `[std.fs]` names the interface the root
                          explicitly exposes and `[std.fs.path]` an item of that interface; a
                          shortest unambiguous local form remains contextual, while
                          [canonical sight] authorizes what an author may write and never selects
                          another target; it is read in the context of its module, the one it is
                          said of, or whose [kernel.body] or decision it stands in, or which
                          provides the interface it stands in; or of its workspace, the one whose
                          decision it stands in: a name alone naming, where unambiguous, an item of
                          the interface it stands in or of another its module provides, or, from its
                          module's [kernel.body] and decisions, an item of its [kernel.body], both
                          halves where it is a [kernel.pair]'s; an interface its module provides,
                          its [kernel.default interface] as `default` alone, never by the name it
                          bears; within a decision of a module, another of its decisions by its ID;
                          and else a module, an interface the root provides, or a
                          [graph.dependency], by its local name; within a decision of a workspace, a
                          name alone instead names a member package by its unversioned
                          [graph.package id] or by its name, the final segment of that
                          [graph.package id], where unambiguous among members; after a module, a
                          name naming an interface it provides, its [kernel.default interface] as
                          `default`, never by the name it bears, or an item of its
                          [kernel.default interface]; after an interface, an item of it, of a
                          [kernel.pair] its half alone, though after a module and `default` none,
                          its items being named after the module alone; and after a package's name,
                          a [graph.dependency] or a member package named from a workspace decision,
                          a path following only [graph.exposure]s reachable from its root and
                          continuing through the exposed interface to any of its items, including
                          one of an exposed [kernel.default interface] under every legal alias; no
                          public path traverses its private [kernel.module tree]

  semantic delta          the interface, [kernel.body], decision and other [kernel.unit]s a change
                          affects, as classified by a [kernel.semantic profile] independently of how
                          artifacts divide or combine them; the [kernel.semantic profile] declares
                          whether that classification is mechanical, inferred or partial, so
                          physical co-location never by itself joins contract and body ownership

  public unit             one identified [kernel.source] [kernel.unit] supplied for reading a public
                          surface, with its content and a locator under its
                          [representation profile]; a canonical [public unit] is its corresponding
                          file, while a native one need not be a file
  profile adapter         optional external operational access to artifacts under a
                          [representation profile]: observing, checking, extracting or modifying
                          them, or supplying target-specific operational guidance and tooling; the
                          [representation profile] retains ownership of the semantic mapping
  generation backend      one profile-neutral external capability in authoring, composing
                          [profile adapter]s to read authoritative [kernel.source]s and produce or
                          update canonical and derived [kernel.unit]s under
                          [representation profile]s; several coordinated packages may implement it

  target support          external reusable native libraries and build/runtime facilities used by
                          generated [kernel.target]s, whether quollified and generated or
                          independently authored; the umbrella need not denote the framework
                          [graph.role]
  target binding          a reusable realization for one target, supplied by [target support]: a
                          module implementing an abstract interface, using native facilities
                          directly where they keep its promises and adapting semantic differences
                          otherwise; a platform built-in needs no artificial native package or
                          [graph.native overlay], and the binding is no ordinary [graph.dependency]
                          or per-consumer inference
  open:
    profile identity      a [kernel.semantic profile] participating in a package has an identity and
                          [graph.version] under which its mappings and declarations are selected; a
                          shared [native profile] is preferably a versioned package with a module
                          implementing this interface through target-specific statements and
                          decisions rather than mandatory software methods, while a first
                          project-local profile may remain structured decisions; how a package
                          declares that identity and its metadata waits

    framework rules       what a framework, as [graph.role] has it, declares over the modules that
                          implement its interfaces, as kinds and rules they keep, and any versioned
                          [kernel.view]s it declares with their kinds, statement and responsibility
                          semantics, naming rules and intended readers, waits
```

## Rules

```
  requires:
    profile semantics     every [representation profile] states how its representation exposes
                          modules, public interfaces, [kernel.body]s, decisions and
                          [kernel.reference]s; where its selected layers include the
                          [graph.package graph], it also states [graph.exposure]s, [public unit]
                          identity and locators, [graph.dependency]s and how native
                          [graph.package id] and [graph.native publication] metadata are read, and
                          where they include the [rich.rich contract], it declares [rich.fidelity];
                          toolchains and [profile adapter]s may consume or implement profile
                          operations but do not own this semantic interface
    profile fidelity      each [representation profile] declares which mappings and guarantees are
                          mechanical, agent-inferred and reviewed, partial or unsupported; an
                          unsupported obligation prevents any claim of full [rich.fidelity], and
                          [rich.conformance evidence] never completes a [rich.semantic surface] by
                          itself
    contract placement    co-located canonical Quoll statements share the native package's lifecycle
                          and close its [rich.fidelity] gaps, while a separate abstract Quoll
                          package holds a contract with independent ownership, publication or
                          evolution, or several realizations; no fact is maintained in both homes

    public reading        a public reader or its [profile adapter] starts from a package's
                          root-reachable [graph.exposure]s and follows those [graph.exposure]s and
                          the [kernel.reference]s of exposed contracts to collect the complete
                          [graph.public closure] as [public unit]s with unit identity, locators and
                          public [graph.dependency] declarations; every [kernel.reference] in the
                          collection resolves through the shared rules from this collection alone,
                          landing on an item of a root-reachable exposed interface or a public
                          [graph.dependency]'s surface, with no same-unit-private or
                          declaration-only exception and without private modules, [kernel.body]s,
                          decisions or author-only [kernel.sight]; an unstructured filename list is
                          only canonical-Quoll shorthand where it still supplies that identity and
                          metadata
    canonical parity      the [canonical profile] satisfies [profile semantics] through its existing
                          representation join, without becoming a toolchain plug-in or requiring a
                          separate package; no lower-layer or [native profile] rule depends on
                          canonical Quoll notation
    canonical resolved    every [canonical reference] resolves by its stated rules, with
                          [canonical sight] authorizing authorship and never selecting a target;
                          every [kernel.reference] in a public contract or supplied declaration
                          [kernel.unit] resolves from its [graph.public closure] without private
                          author context or a same-unit-private or declaration-only exception,
                          including one in a workspace decision resolved within member packages and
                          their public surfaces alone; a colliding or ambiguous local
                          [graph.dependency] name is resolved by an explicit alias rather than
                          shadowing
    canonical names       no two private interfaces that ancestors of one module provide share a
                          name under [canonical sight]
    identifiers           in canonical Quoll, the package's name, and every module's and every
                          interface's, is a lowercase ASCII identifier: a lowercase letter, then
                          lowercase letters, digits and `_`; and an item's name holds no `.`

    external roles        no [native profile], [profile adapter], [generation backend] or
                          [target support] is a built-in module of `language` or a mandatory
                          separate product; a workflow uses only the capabilities it needs, and one
                          distribution may carry several
    binding selection     a [generation backend] deterministically selects the registered default or
                          an explicitly configured [target binding] and records the selection in the
                          generated [kernel.target]'s [kernel.provenance]; [target support] owns the
                          implementation and its conformance tests, and no consumer infers its own
                          mapping

    bounded inputs        legal [kernel.sight] is only an upper bound: every generating or reviewing
                          task receives only the interfaces, [kernel.body]s, decisions and
                          [graph.dependency] context it needs; native visibility and review may
                          provide partial enforcement, whose limits the [kernel.semantic profile]
                          declares rather than claiming repository access is bounded by compiler
                          visibility alone
    semantic ownership    contract and cross-module choices belong to contract review and
                          [kernel.body] choices to implementation review even where one native
                          artifact holds both; a [semantic delta], not file ownership, bounds each
                          review, and a question visible outside the module returns to the contract
                          owner and person
```
