Generation and realization over the lower semantic layers: source [assembly], bounded [projection], ticketed [realization], the actual [target map], derived-[view closure] and directional [trace link]s, with [resources], [tests] and [generated only] diagnostics.

## Structure

```
  assembly              an authoritative [kernel.source] [package]'s declaration of its intended
                        derived [kernel.target]s: per target and configuration, which [module]s and
                        [interface]s participate, which implementations or [profile.target binding]s
                        serve them, and which target [profile.representation profile] and
                        [profile.generation backend] choices apply; it mirrors no generated native
                        [kernel.unit], and a [package] has one exactly where it declares derived
                        [kernel.target]s; an ephemeral [kernel.derived view] likewise has an
                        [assembly] only where it declares [kernel.target]s of its own;
                        [kernel.generation activity] is the agents' work from this declaration,
                        while native compilation, testing and packaging remain native tooling
  projection            derivation of a bounded [kernel.derived view] in canonical Quoll under the
                        [profile.canonical profile] at an exact base [graph.version] or immutable
                        resolved state: the [profile.generation backend] and
                        [profile.profile adapter]s select the [module]s, public [interface]s,
                        [kernel.body]s, [decision]s and [graph.dependency] context needed for a
                        proposed change; each projected [kernel.unit] retains its [kernel.source]
                        identity and authority, and its mechanical, agent-inferred, omitted and
                        lossy information is explicit; surviving Quoll facts are referenced rather
                        than duplicated where practical, fidelity may be partial, and reconstruction
                        of the base byte-for-byte is neither required nor evidence of semantic
                        fidelity
  realization           implementation of an accepted design delta as coherent implementation
                        tickets and per-[kernel.unit] source-to-target mappings: each ticket
                        realizes a coherent part and runs its required conformance and closed-change
                        checks; work tracking records ordering and completed, deferred and
                        conflicted [kernel.unit]s, while current [kernel.provenance] records only
                        what has actually been realized; a rebase compares the proposal's exact base
                        with the new canonical state, revisits affected [kernel.reference]s and
                        [decision]s, and regenerates or revises the remaining delta rather than
                        blindly replaying text patches; direct and ephemeral workflows follow these
                        same rules, and a change spanning [package]s uses their states and diffs,
                        coordinated [workspace] [decision]s, tickets and per-[kernel.unit]
                        [kernel.provenance], with no first-class change [package]

  target map            the persistent realization record at a [kernel.target] [package]'s top, in
                        one common canonical-Quoll metadata form shared by every
                        [profile.representation profile]: its exact [kernel.source] state, native
                        [kernel.unit]s and contracts, source-to-[kernel.unit] [kernel.provenance],
                        authority, [realization] state and references to target-local [decision]
                        collections; [kernel.provenance] records the
                        [profile.representation profile] and [profile.profile adapter] versions;
                        native locators remain profile-interpreted inside this common structure,
                        which records actual realization rather than owning [kernel.source]
                        semantics or [graph.dependency] resolution; a mixed [package] maps its
                        derived [kernel.unit]s alone, a canonical native [package] with no derived
                        [kernel.unit]s carries none, and an ephemeral [kernel.derived view] may
                        carry this base and [realization] mapping temporarily, retiring it with the
                        view
  view closure          completion of a [projection] and its [realization]: accepted [decision]s
                        move to the [module]s owning surviving canonical [kernel.unit]s, retaining
                        IDs and move history and retargeting their references to surviving [item]s;
                        rejected alternatives survive in those [decision]s, and
                        [rich.open question]s return to their owning canonical [item]s or the work
                        tracker; only the minimal co-located canonical Quoll contract or
                        decision-bearing [item] needed to carry an accepted choice is added where no
                        surviving [item] can carry it; the [kernel.derived view], its derived-only
                        links and its temporary [target map] leave the current
                        [graph.package graph], its exact base and proposal remaining in work history
                        rather than becoming hidden semantic context

  trace link            a directional, versioned [graph.public reference] from a native realization,
                        test or [decision] to the public Quoll requirement or [interface] [item] it
                        implements, checks or traces, with an explicit role and the existing
                        implementing relation used where it already carries that meaning; canonical
                        Quoll [item]s, [decision]s, [graph.native overlay]s and [kernel.provenance]
                        carry the same roles through ordinary references; the specification does not
                        enumerate its realizations; one canonical default structured native-comment
                        or annotation form carries the role and reference, and a
                        [profile.native profile] may specialize its concrete spelling only by
                        declaring the mapping, preserving reference and role meaning, and letting
                        its [profile.profile adapter] resolve and check it; no native comment
                        creates an undeclared [graph.dependency]
  trace index           an optional derived aggregation of [trace link]s for cross-cutting queries
                        and external tooling, never a second authority for them and never required
                        of the specification
  open:
    assembly form       the concrete grammar, filename and configuration notation of an [assembly],
                        which wait for the first derived-target implementation
    target map form     the concrete common grammar, filename and schema of a [target map], shared
                        by every [profile.representation profile] and waiting for the first
                        derived-target implementation; per-[profile.representation profile] map
                        grammars are not alternatives

    resources           exact statements in a [kernel.target]'s own form, each named by an
                        [interface], which [kernel.generation activity] takes as input; how and
                        where they are written waits on the parts that write them
    tests               a [package]'s [tests], written in Quoll, their cases checking what users
                        notice through a [module]'s [rich.full interface]s, and every one of the
                        [resources], with the fixtures only they use; what else they state waits

    trace link form     the exact canonical-default role spellings, native tokens and placement of a
                        [trace link], which wait for the first [profile.native profile] and
                        [profile.profile adapter] needing them
```

## Rules

```
  requires:
    generated only         the [profile.generation backend] and [profile.target support] together
                           provide [assembly] and [profile.binding selection], native contracts and
                           bodies, [resources], [tests], target-framework integration,
                           [kernel.provenance], conformance, localized updates and diagnostics
                           mapped to authoritative Quoll [item]s and source places; people need not
                           routinely read or edit native code, and native failures or escape hatches
                           return as reported source questions rather than an independent native
                           design workflow

    backend orchestration  one profile-neutral [profile.generation backend] in authoring composes
                           the [profile.profile adapter]s needed for canonical and derived
                           [kernel.unit]s and orchestrates authority, [kernel.provenance], closed
                           change, incremental selection, [decision] preservation,
                           [rich.conformance evidence] and diagnostics across base and proposed
                           states
    contract first         the target architect and reviewer settle native contracts before
                           implementation agents write native bodies; one-to-one
                           module-to-native-unit mapping is common and every grouping or splitting
                           is declared, while each [kernel.body] [item] and [kernel.pair] constrains
                           its native body only to the depth the [kernel.source] states, leaving
                           remaining choices to persistent target-local [decision]s
    localized generation   later [kernel.generation activity] reads persistent target-local
                           [decision]s and the [target map], patching or regenerating only affected
                           [kernel.unit]s and preserving unrelated bodies and [decision]s; a missing
                           [kernel.source] promise returns as a question reported against that
                           [kernel.source] rather than becoming a silent target choice, and a
                           target-local choice becoming externally visible requires an explicit
                           source-contract change
    realization closure    closed change revisits the union of Quoll, native and generated
                           dependents through the available references, implementing relations and
                           [target map]; mechanical mappings support mechanical closure, while
                           inferred or partial mappings produce explicit review obligations and
                           uncertain findings rather than silent success, and conformance is checked
                           against [kernel.source] promises rather than textual similarity to a
                           proposal

    trace validity         every [trace link] participates in closed change and version upgrades,
                           whose broken or changed targets are revisited; neither a link nor a
                           [trace index] supplies [rich.conformance evidence], and
                           [profile.native profile]s may vary concrete notation alone, never the
                           common reference or role meaning
```
