What a [package] means, for whoever writes one, person or agent, and for any tool that reads one: its [module]s, the [interface]s they provide and implement, their [body]s and [decision]s, where each [reference] lands, and the [project] that may hold it, each in the language's terms alone; how a [package] is written, and which of its writing states what, is not stated here.

## Structure

```
  view               one of the three a statement of the language stands in: Structure, for
                     what something is made of and speaks of; Flow, for how it acts over time;
                     and Rules, for what holds throughout
  item               a name and a statement standing in a [view], of the one kind its [view]
                     holds: in Structure a thing, a noun, as a part, a term or a piece of data;
                     in Flow an action, a verb, as a step, an operation, a sequence or a
                     lifecycle; and in Rules a rule, a predicate that holds throughout
  interface          what others may rely on, and what they may not, and so a requirement on
                     whatever implements it: its name; what it offers; whether it is private;
                     the [interface]s it includes whole, each [item] of theirs one of its own,
                     none changed; and its [item]s, [view] by [view], stating everything its
                     users notice through it, each as a promise they may rely on or a freedom
                     they may not; it stands apart from all that implements it
  decision           why [item]s are as they are, its holder's or those of what it binds, in
                     no [view] and never an [interface]'s: under its ID, which names it alone,
                     its statement, the choice it makes
  module             the unit of hiding, keeping one secret, a choice likely to change, behind
                     the [interface]s it provides or implements: its name; what it is for, and
                     its secret; its parent, a [module], but for the root of its tree, which has
                     none, and its parts, the [module]s whose parent it is; the [interface]s it
                     provides, whether it implements them or not; the [interface]s it
                     implements, keeping every promise of each; and its [decision]s
  body               a [module]'s own [item]s, [view] by [view], which no other [module] sees,
                     saying how it keeps the [interface]s it implements
  direction          a rule's, saying who keeps it: ensures, that whatever holds it makes it
                     true, each [module] that implements the [interface] it stands in, or the
                     [module] whose [body] holds it; or requires, that whatever holds it relies
                     on it being true, of its users or of the world; and a rule speaking of
                     its own [interface]'s [item]s is kept by them as written
  field              a part of a [decision] under one of the language's words for it: Stated
                     by, the [item]s that state what it decided; Because, its reasons;
                     Accepting, its costs; Revisit, where it is provisional, what would call
                     for it to be taken again; Rejected, each option it rejected, with its
                     reason, a scope its holder leaves out among them; Superseded by, its
                     successor, a [decision] its holder holds; Formerly, the ID it bore in
                     another [module], in its own tree or another, before it moved, naming
                     nothing; and Taken by, the role of the writer who took it alone, where
                     people left it open
  open question      an [item] that, in place of its [view]'s kind, states a question people
                     keep open, an open future among them: it promises what it states as
                     settled and nothing of what it keeps open, bears no [direction], and
                     stays open until a [decision] of the [module] whose [body] holds it, or
                     which provides the [interface] it stands in, answers it, when it is an
                     ordinary [item]
  label              a free word an [item] or a [decision] bears, its writer's choice: it binds
                     nothing, no rule or check resting on it, while a reader, person or agent,
                     may take it as context
  package            the unit of publication, versioning and trust: its name; its [module]s,
                     one tree, whose root is the [package] itself, bearing its name and saying
                     what it is for and what it hides; and its surface, the [interface]s its
                     root provides, private ones aside, which alone cross its bounds; it never
                     stands within another [package]; and an [interface] none of its [module]s
                     implements is abstract by that alone
  version            a [package]'s, under which it is published and others depend on it: with
                     its name, what tells it, as published, from every other state of it
  edition            the language's definition at one [version], itself a [package], which a
                     [package] names as the one it is written in, fixing what the language's
                     terms mean in it; the definition is written in the [edition] that is its
                     own [version]
  project            the unit of maintenance: [package]s kept at head together; it lends
                     nothing and publishes nothing, and holds [decision]s of its own
  dependency         another [package] that a [package] depends on: by its name and a
                     [version], under a local name where its own would clash; or, where both
                     stand in one [project], at head, with no [version]
  role               what a [package] is to the [package]s around it: a library, a [package]
                     others depend on; a framework, a library whose abstract [interface]s its
                     users implement, and which owns the flow that calls them; and a system, a
                     [package] no other depends on
  default interface  the one [interface] a [module] may provide as its own face, which the
                     [module] implements where it has a [body], and does not where it has none
  pair               an [item] of a [module]'s [body] that the [module] states is with an
                     [interface], together with that [interface]'s [item] of its name, which
                     the [body]'s one carries out, saying how it is kept, in whatever [view]
                     each stands; a [module] may leave any [item] of an [interface] it
                     implements unpaired, keeping it all the same
  sight              what a [module] sees: its [body]; its [decision]s, which no other [module]
                     sees; the [interface]s it provides, private ones among them; those its
                     parts, its siblings and its ancestors' siblings provide, private ones
                     aside, a part's staying hidden outside its parent; every private
                     [interface] an ancestor of it provides, which so reaches every [module]
                     below its own; each [interface] it implements; the surface of each
                     [dependency] of its [package]; and, as wholes, itself, its parts, its
                     siblings, and each [module] or [package] providing one of these
  reference          a name, or a path of names each naming something within the one before,
                     standing in an [item], in a [decision], or in what a [module] or an
                     [interface] is said to be for or to offer: its [module]'s, the one it is
                     said of, or whose [body] or [decision] it stands in, or which provides
                     the [interface] it stands in; resting on what it lands on: an [item], a
                     [pair]'s two halves, an [interface], a [module], a [decision], a
                     [package], or nothing, where nothing it could name bears its name; a name
                     alone naming, first, an [item] of the [interface] it stands in or of
                     another its [module] provides, or, from its [module]'s [body] and
                     [decision]s, an [item] of its [body], both halves where it is a [pair]'s;
                     an [interface] its [module] provides, its [default interface] as
                     `default` alone, never by the name it bears; within a [decision] of a
                     [module], another of its [decision]s by its ID; and else a [module], the
                     root among them by the [package]'s name, an [interface] the root provides,
                     or a [dependency], by its local name; after a [module], a name naming an
                     [interface] it provides, its [default interface] as `default`, never by
                     the name it bears, or an [item] of its [default interface]; after an
                     [interface], an [item] of it, of a [pair] its half alone, though after a
                     [module] and `default` none, its [item]s being named after the [module]
                     alone; and after a [dependency], an [interface] of its surface, its
                     root's [default interface] as `default`, never by the name it bears, or
                     an [item] of that [default interface], and after a [dependency] and
                     `default` none
  uses               the [interface]s, other than those it provides, that a [module]'s
                     [reference]s land on, or on an [item] of: what a [module] [uses], read
                     off its [reference]s alone, so that one whose [reference]s land in none
                     stands alone
  open:
    build            a [package]'s assembly, apart from its design, which never binds: a
                     [build] says, per configuration, which [module], of this [package] or
                     another, serves each [interface] a [module] [uses], and what is generated
                     from which [module]s; it is declarative, agents doing its work, then each
                     target's own tooling; a [package] has one exactly where it has a target;
                     what a configuration and a binding are, and how a [build] names its
                     targets, wait
    framework rules  what a framework, as [role] has it, declares over the [module]s that
                     implement its [interface]s, as kinds and rules they keep, waits
    project scope    a [project]'s [decision]s bind several of its [package]s; what they see
                     and what they name wait
    resources        exact statements in a target's own form, each named by an [interface],
                     which generation takes as input; how and where they are written waits on
                     the parts that write them
    tests            a [package]'s [tests], written in Quoll, their cases checking what users
                     notice through a [module]'s [interface]s, and every one of the
                     [resources], with the fixtures only they use; what else they state waits
```

## Rules

```
  ensures:
    meaning alone     what these [item]s state of a [package] rests on nothing of how it is
                      written or stored: no file, no text as written and no place in either is
                      part of it, so that it stays as stated whatever form its writing takes
    stated effects    an action does nothing its statement and the rules on it do not state, so
                      that one whose statement names no effect has none
  requires:
    resolved          every [reference] lands on what it names, one thing or a [pair]'s two
                      halves, within its [module]'s [sight]
    independent       no [reference] standing in an [interface] lands on a [module]'s [body], an
                      [item] of one or a [decision], nor on a [module] that implements it or
                      [uses] it
    implementable     a [module] implements only an [interface] it would see were it to
                      implement none, or one its parent provides
    includable        an [interface] includes only [interface]s within the [sight] of the
                      [module] that provides it
    paired            every [pair] is with an [interface] its [module] implements, holding an
                      [item] named as the [pair]'s half in its [module]'s [body]; and no [item]
                      of a [body] outside every [pair] bears the name of an [item] of an
                      [interface] its [module] implements
    identifiers       the [package]'s name, and every [module]'s and every [interface]'s, is a
                      lowercase ASCII identifier: a lowercase letter, then lowercase letters,
                      digits and `_`; and an [item]'s name holds no `.`
    unique names      no two [item]s of one [interface], those it includes among them, share a
                      name, nor two [item]s of one [body] but in [pair]s with different
                      [interface]s; nor two [interface]s one [module] provides; nor two of what
                      a [package] names at large, its [module]s, the [interface]s its root
                      provides, its [default interface] aside, which no [reference] names by
                      the name it bears, and its [dependency]s; nor two private [interface]s
                      that ancestors of one [module] provide
    defaults          no [module], [interface] or [item] bears the name `default`, which names a
                      [module]'s [default interface] alone; and no name is both an [item] of a
                      [module]'s [default interface] and another [interface] it provides
```
