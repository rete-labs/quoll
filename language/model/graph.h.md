Publication and trust over the [kernel.structural kernel]: heterogeneous [package] identity, [version]s, [dependency]s, federated [resolution], [workspace]s, public surfaces and [native publication]s.

## Structure

```
  package id              a globally namespaced, location-independent Package URL under the
                          canonical rules of the ecosystem whose published unit it identifies,
                          unversioned and stable across hosting, mirror and repository-directory
                          moves: a Quoll-authored published unit retains ecosystem type `quoll`,
                          with a mandatory trust domain, a user-defined hierarchical namespace path
                          and a final segment supplying its name; a native published unit uses its
                          ecosystem's canonical Package URL type and identity, never a second Quoll
                          identity
  package                 the unit of publication, versioning and trust, and a composition of
                          [kernel.source] and [kernel.target] [kernel.unit]s in any combination
                          rather than a separate mode for each workflow: its [package id] and name;
                          exactly one [kernel.module tree], whose root is the [package] itself,
                          bearing its name and saying what it is for and what it hides; and its
                          surface, the public paths reachable from that root, which alone cross its
                          bounds; the [package] extends that same [kernel.module tree] with
                          publication, versioning, trust and dependency semantics, creating no
                          second tree, design history or decision ID space; a [package] never stands
                          within another [package]; and an interface none of its modules implements
                          is abstract by that alone
  exposure                an explicit alias declared by an existing module, mapping a name or path
                          it exposes to a whole interface within its [kernel.sight], never to a
                          module or an individual item: every item of the exposed interface, one
                          included whole among them, is publicly readable through it; the alias
                          identifies the same interface rather than copying it or creating a header,
                          module or item, and leaves its [kernel.structural path] unchanged and
                          private by default; an intermediate [exposure] may re-export a deeper
                          interface to its parent, becoming externally public only where a chain of
                          [exposure]s reaches the [package] root; one interface may have several
                          [exposure] paths, while every declared [exposure] path, public or
                          intermediate, identifies exactly one target

  version                 a [package]'s, under which it is published and others depend on it: with
                          its [package id], what tells it, as published, from every other state of
                          it, under its ecosystem's rules; the canonical Quoll source rules take a
                          semantic tag for a release as alone determining a release [version] and
                          derive a canonical pseudo-version from a development request for a branch
                          or commit: the nearest valid ancestor tag for a release supplies the base,
                          whose prerelease or stable form selects the derivation: with no valid
                          ancestor tag for a release, `v0.0.0-<timestamp>-<revision>`; from
                          prerelease base `vX.Y.Z-pre`, `vX.Y.Z-pre.0.<timestamp>-<revision>`; and
                          from stable release base `vX.Y.Z`, `vX.Y.(Z+1)-0.<timestamp>-<revision>`;
                          the base ancestor tag, UTC `yyyymmddhhmmss` timestamp and revision of 12
                          lowercase hexadecimal characters are validated against Git history,
                          semantic-version precedence orders the snapshot against its base and other
                          snapshots, and its selected commit and content digest fix exact content; a
                          copied tree's selected [version], where one exists, comes from the tag for
                          a release or development selection recorded for it; these Git and
                          pseudo-version rules bind no native ecosystem
  selector                a requirement for a [package], interpreted under its own ecosystem's
                          rules; canonical Quoll source rules use a [package id] together with an
                          exact stable, prerelease or development [version], or a partial
                          stable-release [version] written `v<major>` or `v<major>.<minor>`: an
                          exact [selector] requires that [version], including any prerelease, while
                          a partial [selector] matches stable release [version]s alone; a
                          compatibility series is one major [version], and [selector]s carry
                          requirements, not selected identity; native requirement forms remain
                          native and inherit none of these canonical Quoll rules
  source locator          the location of one selection of a [package id], whose identity stays
                          independent of it, under the ecosystem's rules; canonical Quoll source
                          rules use a Git repository, a [package] path within it and a requested
                          [version] or committish, the [package] path published as part of the
                          source location and tag prefix for a release, so moving it changes the
                          source location rather than the [package id]
  distribution            delivery of a [package]'s content under its ecosystem's publication and
                          integrity rules; canonical Quoll source rules fetch source directly as
                          written from Git: a [source locator] finds the source; a selected commit
                          and [package] content digest verify its integrity independently of a
                          mutable tag or one hosting location; a mirror or cache must deliver the
                          same [package] content digest

  workspace               the unnamed unit of maintenance and publication coordination: [package]s
                          kept at head together, each independently readable and fetchable; it
                          coordinates publication of its members rather than publishing itself, and
                          holds decisions over workspace-level membership and coordinated
                          publication choices, which may name member [package]s as wholes and their
                          public surfaces and bind those choices alone
  dependency              another [package] that a [package] depends on, declared by a [selector] in
                          the ecosystem metadata that remains authoritative for it; a native
                          manifest owns native requirements and no overlay duplicates them; the
                          declaration is the same for an external consumer and a [workspace] member,
                          and only explicit, [kernel.semantic profile]-supported [workspace] tooling
                          may substitute the member's local working tree at head, never a hidden
                          path rewrite or workspace-local context in a fetched [package]; under
                          canonical Quoll source rules its default local name is the final segment
                          of its unversioned [package id], with an explicit alias where needed; a
                          design-time Quoll contract [dependency] is distinct from a runtime native
                          [dependency], which must be published and resolved in the native
                          ecosystem; development between [package]s outside one [workspace] uses
                          their ecosystems' published or exact source states
  release                 publication of one [package] at one [version] under its ecosystem's
                          mechanics; under canonical Quoll source rules its selected tag for a
                          release is the canonical spelling of the selected semantic release
                          [version], stable or prerelease, `vX.Y.Z` being the stable form; below a
                          repository's root, the literal tag is the [source locator]'s [package]
                          path followed by `/` and that selected tag for a release, while at the
                          root it is the selected tag for a release alone, with no synthetic prefix
                          and no coordination of below-root [package]s by that root tag; a
                          coordinated commit may declare member [version]s before their tags exist,
                          with [workspace] substitution checking it at head; coordinated [release]s
                          place one such tag per [package] at that commit, may share a [version],
                          and publish each [dependency] before its dependents so no published
                          dependent lacks a same-release [dependency] and a tag-level check can
                          resolve externally; an interrupted coordinated publication leaves already
                          published [package]s valid and the remainder retryable; these tag rules
                          bind no native ecosystem
  resolution              selection of exact source for a [dependency] within its ecosystem's own
                          subgraph, whose resolver remains authoritative, the common graph requiring
                          no common resolver; under canonical Quoll source rules all [selector]s for
                          one major [version] are intersected, partial [selector]s match stable
                          release [version]s alone and any prerelease must be named exactly, the
                          newest satisfying stable release [version] is preferred with backtracking
                          on conflicts, disjoint [selector]s within one major fail, and incompatible
                          majors may coexist; the selected versioned [package id], each
                          [source locator], the matched literal tag for a [release], the full Git
                          commit and the [package] content digest are recorded, a development
                          selection having its requested branch or commit and pseudo-version but no
                          tag; a changed tag or changed delivered content fails verification rather
                          than silently replacing the selection
  lock                    the exact full direct-and-transitive subgraph selected for one root
                          [package] under its ecosystem's authority, committed as that ecosystem
                          requires and authoritative within that subgraph; under canonical Quoll
                          source rules it governs the root's own checks and takes precedence over
                          fresh selection until an explicit update; ordinary checking fails rather
                          than silently changing it when manifests require another graph, an
                          explicit stable graph update re-resolves stable [selector]s and changes
                          only the [lock], never advancing an exact development selection, while an
                          explicit update of a development branch resolves that branch anew and
                          changes both its pseudo-version and [lock]; a commit-pinned development
                          selection changes only through an explicit different [selector], and
                          editing a direct [selector] re-resolves the [lock]; when the [package]
                          becomes a [dependency], its manifest joins the consumer's graph and the
                          consumer resolves and locks that graph anew, the [dependency]'s own [lock]
                          supplying [source locator] hints alone while the consumer's [lock] governs
                          [version], commit and content digest; none of these canonical Quoll update
                          or precedence rules governs a native [lock]
  mixed graph             the exact outcome for one consuming root across ecosystems, joining exact
                          native [lock] states, source revisions and content digests to exact Quoll
                          selections and cross-profile [dependency] edges; it records outcomes
                          rather than re-resolving any subgraph, and an unavailable reproducible
                          cross-ecosystem selection fails explicitly

  edition                 the language's definition at one [version], itself a [package], which a
                          [package] names as the one it is written in, fixing what the language's
                          terms mean in it; the definition is written in the [edition] that is its
                          own [version]
  role                    what a [package] is to the [package]s around it: a library, a [package]
                          others depend on; a framework, a library whose abstract interfaces its
                          users implement, and which owns the flow that calls them; and a system, a
                          [package] no other depends on
  package sight           the [kernel.sight] of a module in a [package], adding the surface of each
                          [dependency] and, as wholes, each module or [package] providing something
                          visible; no [workspace] decision enters it
  public reference        a [kernel.reference] using a [package]-qualified public path, within the
                          same [package] or crossing its bound, or standing in a [workspace]
                          decision: it names a [package] by its canonical [package id] and lands
                          only on it as a whole or on an interface exposed from its root, or an item
                          of one, through that public path, never on a private
                          [kernel.structural path]; its complete public spelling has one target for
                          every reader and is distinct from a local structural reference, not that
                          reference with a removable [package] prefix; a published address includes
                          the exact [version] or immutable resolved state, readable local aliases
                          may shorten its source spelling, and [workspace] members at head may
                          update their references atomically; an upgrade revisits renamed or changed
                          targets, with no universal item IDs and no inferred logical identity
                          across independent renames; a native structured comment, documentation or
                          annotation may carry such a [kernel.reference] only where its
                          [kernel.semantic profile] declares the form and its adapter resolves it
                          against an explicit [dependency], including it in [kernel.uses] and closed
                          change; unmarked prose is no formal [kernel.reference], and a
                          [kernel.semantic profile] claiming full reference fidelity flags suspected
                          references in it for review rather than silently ignoring them

  native overlay          the presence of `package.quoll.toml` on a native [package], marking it as
                          quollified and discoverable for common-graph participation; it carries the
                          native [package id], [kernel.semantic profile] identity and version,
                          [edition], references to any co-located canonical Quoll items and
                          structured decisions, and [kernel.provenance] where the [package] is a
                          [kernel.target]; the native manifest remains authoritative for native
                          name, [version], requirements, [resolution] and [lock], and the overlay
                          declares only cross-profile facts the native ecosystem cannot carry,
                          duplicating no native metadata and imposing no mandatory canonical Quoll
                          module-list, [lock], Git pseudo-version or Markdown-file rules
  native publication      a [package] with the identity, versioning and publication mechanics its
                          ecosystem requires; separate generated [native publication]s of one
                          authoritative logical design have separate [package id]s and [release]
                          mechanics while remaining [kernel.target]s, not independent realizations
                          or second design authorities; each may be quollified and carry exact
                          [kernel.provenance] and source-to-target [kernel.unit] mappings, which are
                          no ordinary [dependency] and prove no conformance; a package-level
                          [kernel.provenance] pointer claims no realization of [kernel.unit]s it
                          does not map

  package graph           the [kernel.layer] over the [kernel.structural kernel] for heterogeneous
                          [package] publication and trust, [package id]s and [version]s,
                          [dependency]s, federated [resolution] and exact [mixed graph]s,
                          [workspace]s, [kernel.semantic profile] identity, [exposure]s and public
                          surfaces, [native overlay]s, publication-level [kernel.provenance] and
                          [public reference]s
  open:
    native overlay form   the concrete fields, sidecar locations and full schema of a
                          [native overlay], which wait for the first [kernel.semantic profile]
                          needing them

    mixed graph form      the concrete record of a [mixed graph], which waits for the first mixed
                          [kernel.semantic profile] needing it
```

## Rules

```
  ensures:
    abstract publication  [package id], [version], [distribution] and [resolution] state publication
                          and source identity without prescribing a file syntax
  requires:
    self-contained        a [package]'s meaning and [dependency] declarations rest on its own
                          source, its [edition] and its [dependency]s' public surfaces alone, never
                          on its originating [workspace], an inherited [version], a workspace-local
                          path or a publication transformation; at-head substitution is explicit and
                          changes no fetched [package]'s declarations or meaning
    public closure        every [kernel.reference] in a root-reachable [exposure]'s contract or a
                          supplied declaration [kernel.unit], including one brought in directly by
                          interface inclusion, lands on an item of a root-reachable exposed
                          interface of the same [package] or on a [dependency]'s public surface; no
                          same-unit-private or declaration-only exception admits another target;
                          closure follows [exposure]s and the [kernel.reference]s of exposed
                          contracts recursively, while inclusion alone creates no public alias and
                          no private target is exposed implicitly; [kernel.sight] governs what its
                          author may write, while this closure governs what a dependent can resolve,
                          and is checked from the [kernel.reference]s and public surface alone
    package names         no declared [exposure] path, public or intermediate, identifies two
                          targets, though one target may have several [exposure] paths; every legal
                          continuation of an [exposure] path to an item of its exposed interface,
                          including an item of a [kernel.default interface] under every legal alias,
                          identifies exactly one item; a named interface and a sibling module may
                          not share a name, and no facade or module-first precedence resolves a
                          collision; a [dependency]'s local names are unique wherever they resolve
                          without an explicit alias

    dependency alone      a [dependency] makes a surface visible and never itself claims
                          implementing, generated-from, binding, tracing, conformance or
                          [kernel.provenance]; the realizing side names the versioned interface it
                          implements, the specification does not enumerate its realizations, a
                          design-time Quoll contract [dependency] supplies no runtime native
                          artifact, and no relation itself establishes that the implementation keeps
                          it
    federated exactness   each ecosystem's resolver and committed [lock] alone govern its subgraph;
                          a consuming root's [mixed graph] joins their exact states to exact Quoll
                          selections and cross-profile [dependency] edges without re-resolving them,
                          and fails where no reproducible cross-ecosystem selection is available

    decision separation   an external [kernel.source] [package] and its derived [kernel.target]
                          [package] keep their own decisions in their own [package]s, the
                          [kernel.target]'s canonical only for choices delegated to it
```
