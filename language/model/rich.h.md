Rich contracts over the [kernel.structural kernel]: [standard view]s, [direction], [open question]s, [label]s, [full interface]s, [conformance evidence], [semantic surface]s and [fidelity].

## Structure

```
  standard view           one of the three [kernel.view]s retained by canonical full Quoll:
                          Structure, for what something is made of and speaks of, its [item] a thing
                          or noun; Flow, for how it acts over time, its [item] an action or verb;
                          and Rules, for what holds throughout, its [item] a rule or predicate
  direction               a rule's, saying who keeps it: ensures, that whatever holds it makes it
                          true, each [module] that implements the [interface] it stands in, or the
                          [module] whose [kernel.body] holds it; or requires, that whatever holds it
                          relies on it being true, of its users or of the world; and a rule speaking
                          of its own [interface]'s [item]s is kept by them as written
  open question           an [item] that, in place of its [kernel.view]'s kind, states a question
                          people keep open, an open future among them: it promises what it states as
                          settled and nothing of what it keeps open, bears no [direction], and stays
                          open until a [decision] of the [module] whose [kernel.body] holds it, or
                          which provides the [interface] it stands in, answers it, when it is an
                          ordinary [item]
  label                   a free word an [item] or a [decision] bears, its writer's choice: it binds
                          nothing, no rule or check resting on it, while a reader, person or agent,
                          may take it as context

  full interface          an [interface] whose [item]s state everything its users notice through it,
                          each as a promise they may rely on or a freedom they may not; an
                          implementation states nothing against it, requiring no more and ensuring
                          no less, so that any implementation keeping it may stand in for another
  conformance evidence    evidence that a [module] keeps a [full interface] it implements, supplied
                          by target-appropriate tests, checks and review; neither the implementing
                          claim nor [kernel.provenance] supplies this evidence, and no uniform
                          evidence form or new relation is required

  semantic surface        the [interface] a [kernel.semantic profile] exposes from all artifacts
                          that deliberately state it: native declarations, types and documentation,
                          co-located supplemental statements, structured [decision]s, schemas or
                          other contract artifacts; supplemental statements close only actual gaps,
                          each fact has one home, and tests, fixtures and reviews supply
                          [conformance evidence] rather than silently becoming the complete contract
  fidelity                what a [kernel.semantic profile]'s discovered [semantic surface] actually
                          states of its [interface], and every gap in it: native artifacts alone
                          claim only the semantics they state, mixed artifacts add only what closes
                          a declared gap, and public-surface discovery and [fidelity] are versioned
                          with the [kernel.semantic profile]

  rich contract           the [kernel.layer] directly over the [kernel.structural kernel] for
                          [full interface]s, [standard view]s, [direction] and substitution,
                          [open question]s, [label]s, [conformance evidence], [semantic surface]s
                          and [fidelity]; it requires no publication or concrete notation
```

## Rules

```
  ensures:
    stated effects        an action does nothing its statement and the rules on it do not state, so
                          that one whose statement names no effect has none
  requires:
    surface fidelity      every [semantic surface] declares its [fidelity] and gaps, versioned with
                          its [kernel.semantic profile]; a native-only surface claims no promise its
                          artifacts do not state, and no permanent mirror of every native
                          [interface] is required
```
