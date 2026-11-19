+++
"module lead" = true
+++
The language definition's design ontology, with this [interface] its [structural kernel]: [unit] authority, [module tree]s, [interface]s and [body]s, [item]s and [decision]s, [reference]s, [sight], implementation and change closure.

## Structure

```
  layer                   a named, independently selectable part of the language's meaning, resting
                          only on its own terms and those of the layers it names as below it; a
                          principle attaches to the layer whose terms it uses, rather than to every
                          layer together
  semantic profile        a versioned interpretation of artifacts in the terms of one or more
                          [layer]s, stating the limits of that interpretation and supplying every
                          declaration the selected layers require; it changes none of their meanings
  view                    a [semantic profile]'s versioned declaration of a place for statements:
                          their kinds, statement and responsibility semantics, naming rules and
                          intended readers; generic tooling may treat statements of an unknown
                          [view] as opaque while still resolving their structural relations, richer
                          checks belonging to the [semantic profile]
  structural kernel       the [layer] sufficient for a standalone [module tree], its [interface]s
                          and [body]s, [reference]s and implementation, durable [decision]s, [unit]
                          authority and change closure; it requires no publication, standard
                          contract outline or concrete notation

  unit                    one separately identifiable part of a design, for which authority and
                          derivation may be stated; authority belongs to each maintained fact, not
                          to a whole representation by default
  source                  an [unit] insofar as it is canonical for the maintained facts it owns,
                          whether a person or an agent writes it and whether it has an
                          implementation output; each such fact has one [source]
  target                  an [unit] insofar as it is derived from authoritative [source]s and is not
                          independently authoritative for their facts; it is canonical only for
                          choices explicitly delegated to it, and may be changed incrementally
                          within those bounds without becoming a second [source]
  generation activity     every local agent-authored modification of an [unit], whether canonical or
                          derived; the activity alone makes no [unit] a [source] or a [target]
  provenance              the authoritative [source] [unit]s of a [target] and the mapping between
                          their [unit]s, sufficient to revisit the [target] when a [source] changes;
                          this is neither an ordinary use relation nor a claim of independent
                          implementation, and its concrete record belongs to an outer [layer]
  derived view            a scoped [target] projection of [source] [unit]s in declared [view]s,
                          supporting a proposal and its realization without becoming a second
                          current implementation [source]; it is non-authoritative at extraction,
                          while an accepted design delta may direct a change to the [source]

  item                    a name and a statement standing in one declared [view], of one of the
                          kinds that [view] declares; a decisions-only supplement has no [item]s,
                          and no concrete [item] stands outside every [view]
  interface               what others may rely on: its name; what it offers; whether it is private;
                          the [interface]s it includes whole, each [item] of theirs a direct [item]
                          of its own, none changed, with no nested [interface] path or alias
                          created; and its [item]s, [view] by [view]; it stands apart from all that
                          implements it
  decision                why [item]s are as they are, its holder's or those of what it binds, in no
                          [view] and never an [interface]'s: under its ID, which names it alone, its
                          statement, the choice it makes; its holder holds one collection for all
                          its [decision]s, whatever representation states what they explain
  field                   a part of a [decision] under one of the language's words for it: Stated
                          by, the [item]s whose own statements enact what it decided, not every
                          [item] its reasons or implementation use, with no [item] losing its
                          [decision] or plain-definition owner by omission; the named [item]s'
                          [unit] authority provisionally distinguishes contract choices from
                          delegated implementation choices without forming a permanent taxonomy;
                          Because, its reasons; Accepting, its costs; Revisit, where it is
                          provisional, what would call for it to be taken again; Rejected, each
                          option it rejected, with its reason, a scope its holder leaves out among
                          them; Superseded by, its successor, a [decision] its holder holds;
                          Formerly, the ID it bore in another [module], in its own tree or another,
                          before it moved, naming nothing; and Taken by, the role of the writer who
                          took it alone, where people left it open

  module                  the unit of hiding, keeping one secret, a choice likely to change, behind
                          the [interface]s it provides or implements: its name; what it is for, and
                          its secret; its parent, a [module], but for the root of its tree, which
                          has none, and its parts, the [module]s whose parent it is; the
                          [interface]s it provides, whether it implements them or not; the
                          [interface]s it implements; and its [decision]s
  module tree             one [module] and all its parts, considered as one design and history: the
                          composition and history holder in which their [decision] IDs remain
                          stable, adding no material type and no [decision] collection beside those
                          of its [module]s; it may stand alone or be contained by an outer [layer]
  structural path         the canonical internal path identifying a [module], [interface] or [item]
                          by its place in its [module tree], private by default and independent of
                          every alias to the same target
  body                    a [module]'s own [item]s, [view] by [view], which no other [module] sees,
                          saying how it keeps the [interface]s it implements
  default interface       the one [interface] a [module] may provide as its own face, which the
                          [module] implements where it has a [body], and does not where it has none
  pair                    an [item] of a [module]'s [body] that the [module] states is with an
                          [interface], together with that [interface]'s [item] of its name, which
                          the [body]'s one carries out, saying how it is kept, in whatever [view]
                          each stands; a [module] may leave any [item] of an [interface] it
                          implements unpaired, keeping it all the same

  sight                   the legal upper bound on what a [module] may read and name, declared by
                          its [semantic profile] and containing its own [body] and [decision]s; the
                          inputs to a particular task contain only what that task needs within this
                          bound, including all of it where that is what the task needs
  reference               a name, or a path of names each naming something within the one before,
                          standing in an [item], in a [decision], or in what a [module] or an
                          [interface] is said to be for or to offer, and resting on what it lands
                          on: an [item], a [pair]'s two halves, an [interface], a [module], a
                          [decision], or nothing, where nothing it could name bears its name; its
                          [semantic profile] supplies one resolution rule for every reader, with
                          contextual shortest unambiguous forms and [sight] authorizing a reference
                          rather than selecting its target
  uses                    the [interface]s, other than those it provides, that a [module]'s
                          [reference]s land on through its [sight], or on an [item] of: what a
                          [module] [uses], read off its [reference]s and [sight] alone, so that one
                          whose [reference]s land in none through [sight] stands alone
```

## Rules

```
  ensures:
    meaning alone         what these [item]s state of a design rests on nothing of how it is written
                          or stored: no file, no text as written and no place in either is part of
                          it, so that it stays as stated whatever form its writing takes

    layered principles    a principle attaches to each [layer] whose [item]s supply its terms, and a
                          [semantic profile] accepts the principles of the layers it selects rather
                          than one monolithic requirement set
  requires:
    resolved              every [reference] lands on what it names, one thing or a [pair]'s two
                          halves, under the same rule for an internal or external reader; its
                          shortest unambiguous form is contextual, every ambiguity fails rather than
                          being settled by storage or precedence, and [sight] only authorizes what
                          its author may write, never selecting a different target
    independent           no [reference] standing in an [interface] lands on a [module]'s [body], an
                          [item] of one or a [decision], nor on a [module] that implements it or
                          [uses] it

    implementable         a [module] implements only an [interface] it would see were it to
                          implement none, or one its parent provides
    includable            an [interface] includes only [interface]s within the [sight] of the
                          [module] that provides it
    paired                every [pair] is with an [interface] its [module] implements, holding an
                          [item] named as the [pair]'s half in its [module]'s [body]; and no [item]
                          of a [body] outside every [pair] bears the name of an [item] of an
                          [interface] its [module] implements

    unique names          no two [item]s of one [interface], those it includes among them, share a
                          name, nor two [item]s of one [body] but in [pair]s with different
                          [interface]s; nor two [interface]s one [module] provides; nor two
                          [module]s of one tree; nor an [interface] a [module] provides and one of
                          its parts
    defaults              no [module], [interface] or [item] bears the name `default`, which names a
                          [module]'s [default interface] alone; and no name is both an [item] of a
                          [module]'s [default interface] and another [interface] it provides

    single authority      every maintained fact has exactly one [source]; a [target] never becomes
                          independently authoritative for a [source]'s facts through generation,
                          publication or incremental patching, while its delegated choices persist
                          and later [generation activity] reads them; a choice that becomes
                          externally visible requires an explicit change to its authoritative
                          contract
    provenanced           every [target] carries [provenance] to its exact [source] [unit]s and
                          their [unit] mappings; a [derived view] is non-authoritative at
                          extraction, an accepted design delta may direct a change to the [source],
                          completing that change leaves the designated canonical artifacts and
                          preserved [decision]s authoritative
    decision authority    a [module] has one [decision] collection across every representation it
                          contains; Stated by references and [unit] authority distinguish shared
                          contract choices from delegated implementation choices provisionally, and
                          choices with different ownership or lifecycles call for separate [module]s
                          rather than parallel collections
```
