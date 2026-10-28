What every [model.package] keeps across its history and its writers, and what review judges of it, for whoever writes one, person or agent, and for any tool or reviewer that checks one: [information hiding], the root, read on a [model.package]'s relations, each reading a rule, whose breach is a fact about it, or a judgement, whose breach is an opinion, naming the [sign] that points review at a candidate; and beside them, rules and judgements of its [model.item]s and [model.decision]s, and of how its writers take and record their choices; what a [model.package] means is not stated here, nor who writes it or how review is run.

## Structure

```
  information hiding  the root of every principle here: a [model.module]'s [model.interface]s
                      say only what others need of it, so that its users may stay clueless
                      about all they leave unsaid, and the edits by which a [model.package]
                      evolves stay closed
  sign                what review reads off a [model.package] and its history, as which of its
                      [model.item]s change together, that points it at a candidate breach of a
                      rule whose breach is an opinion, a judgement, rather than a fact: itself
                      no breach; where a judgement names none, or the history a [sign] reads is not
                      yet written, review judges without one
```

## Rules

```
  ensures:
    terms only             these [model.item]s speak of a [model.package] in [model]'s terms alone,
                           its [model.module]s, [model.interface]s, [model.item]s, [model.decision]s
                           and its history, never of how it is written or stored, nor of who
                           writes it or how review is run
  requires:
    single responsibility  [information hiding] read on what changes together: a [model.module]
                           answers to one reason to change, what changes together for one reason
                           standing together and what changes for different reasons apart; a
                           judgement, its [sign] co-change: [model.item]s that change together
                           across [model.module]s, or apart within one
    open closed            [information hiding] read on how change arrives: a feature arrives as
                           what is added, a new [model.module], as one implementing an
                           [model.interface] already stated or one keeping a requirement the root
                           takes on, rather than as edits across [model.module]s already standing,
                           and an [model.interface] grows by gaining [model.item]s; a judgement,
                           its [sign] one feature's change touching many [model.module]s
    substitution           [information hiding] read on implementing: a [model.module] implementing
                           an [model.interface] states nothing against it, requiring of its users
                           and of the world no more than the [model.interface] requires, and
                           ensuring no less than it ensures, so that any [model.module]
                           implementing it may stand in for another; a breach is found over the
                           whole [model.body], no [model.pair] proving it kept, by review and,
                           once they are designed, by the [model.tests]
    interface segregation  [information hiding] read on what users rely on: an [model.interface]
                           serves one group of users, and one whose users rest on disjoint parts
                           of it is split; a judgement, its [sign] disjoint use: [model.module]s
                           whose [model.reference]s land on disjoint parts of one [model.interface]
    dependency inversion   [information hiding] read on which way resting points: policy rests on
                           no mechanism, and the [model.interface]s most rested on are those stating
                           least of any mechanism and change least, so that what changes often
                           rests on what changes seldom; between an [model.interface] and what
                           implements it or [model.uses] it, the way resting points is
                           [model.independent]'s rule, and how stability is stated waits; the rest
                           a judgement, its [sign] churn: a [model.module] resting on an
                           [model.interface] that changes more often than the [model.module] itself
    no cycle               [information hiding] read on where cycles form: no [model.interface]
                           rests on itself, one resting on each [model.interface] it includes, on
                           each its [model.reference]s land on, or on an [model.item] of, and on
                           all that each of those rests on, so that an edit to an [model.interface]
                           reaches what rests on it along paths that end
    link locality          [information hiding] read on how [model.item]s refer: a [model.reference]
                           goes from the less stable toward the more stable; [model.sight] holds
                           that by default, with [model.independent], and between [model.interface]s
                           it is [dependency inversion]'s
    session fit            a [model.module] fits one agent's session: one holding its [model.body],
                           its [model.decision]s, the [model.interface]s it provides and
                           implements, those it [model.uses] and those its parts provide, never
                           their [model.body]s, can do the work the [model.module] needs, as
                           reviewing, implementing or amending it, the root fitting as a leaf
                           does; a judgement, its [sign] that work outgrowing one session, which
                           points review at splitting the [model.module]
    several faces          a [model.module] providing several [model.interface]s is better with no
                           [model.default interface] among them; a judgement
    needed pairs           a [model.body] pairs an [model.item] of an [model.interface] its
                           [model.module] implements only where how it is kept needs saying beyond
                           the [model.body]'s other [model.item]s; a judgement
    acyclic definitions    no [model.item] rests on itself through the [model.item]s its
                           [model.reference]s land on and theirs in turn, but by naming itself, as
                           a tree's node holds nodes, so that some order of reading meets each
                           [model.item] after all it rests on: a relation between two [model.item]s
                           is stated by one of them, and a family of [model.item]s by naming its
                           members, none of which names it
    no restating           no statement restates what a [model.item] states, or what the
                           [model.edition] its [model.package] is written in states: it
                           references the [model.item], or writes in that [model.edition]'s
                           terms, and may build on an [model.item] through a [model.reference]
                           to it, a [model.decision]'s own statement aside; a [model.decision]
                           holds only what its [model.field]s hold, Stated by among them; what
                           holds of a [model.package], across [model.item]s or within one, is an
                           [model.item]'s to state, never a [model.decision]'s alone; and no two
                           [model.decision]s state one choice
    stated items           every [model.item] is named under Stated by of some [model.decision], or
                           is a plain definition needing none; a judgement, its [sign] an
                           [model.item] that no Stated by names
    lifetime               a [model.decision]'s ID is fixed when it is first written, and no other
                           [model.decision] of its [model.package] ever bears it; until it is
                           committed to its [model.package]'s history it may be withdrawn, leaving
                           nothing in its place, and once committed it is never withdrawn, only
                           superseded or moved; one moving to another [model.module] leaves its
                           own, committed or not, for a successor there, as [model.field]'s
                           Formerly has it
    labels kept            an agent writing a [model.package] keeps every [model.label] people gave
                           an [model.item] or a [model.decision], and gives none of its own
    english                a [model.package] is better stated in English, the language's own
                           words being English, though it may be stated in any natural
                           language, or several; a judgement
    unstated choices       whoever writes a [model.package]'s [model.item]s and [model.decision]s
                           decides what those it writes from leave unstated, within all they
                           state, recording each choice it so takes alone as a [model.decision]
                           under Taken by, for people to review
    answerable             a writer takes no choice that some answer to an [model.open question]
                           would force undone: where one choice keeps every answer possible it
                           takes that one, and where none does it decides provisionally, recording
                           its [model.decision] under Taken by and naming under Revisit the
                           [model.open question] it rests on, so that answering the question finds
                           every [model.decision] resting on it; whether a choice keeps every
                           answer possible is review's to judge, the rule otherwise a fact
    body depth             a [model.body] says, of how its [model.module] keeps the
                           [model.interface]s it implements, all a regeneration of its code must
                           not change: whatever anyone outside the [model.module] would notice came
                           out otherwise, what it leaves for a later run or release to read among
                           it; the code decides alone what a regeneration may change unnoticed, as
                           its data structures, algorithms, libraries and idioms; whether anyone
                           would notice is review's to judge, the rule otherwise a fact, and how
                           code is made from a [model.body] waits
    reported questions     a writer meeting a question that what it writes from leaves open, and
                           that would be noticed outside what it writes, reports it against what
                           left it open and settles it provisionally until that answers it: a
                           [model.body]'s writer, meeting one that users would notice through an
                           [model.interface], against it, recording its choice as a [model.decision]
                           under Taken by, naming under Revisit the question it reported; and a
                           writer of code, meeting one its [model.body] should have settled,
                           against the [model.body], writing nothing into the [model.package];
                           whether a question would be noticed is review's to judge, the rule
                           otherwise a fact
    closed change          a writer changing what a [model.item] states revisits each place
                           where a [model.reference] landing on it stands, each [model.pair]
                           whose half it is, and each [model.module] implementing an
                           [model.interface] that holds it, as its own or by inclusion, whether
                           what it revisits restated the [model.item] or only relied on it, and
                           amends each that no longer holds, revisiting in turn those of each
                           amended [model.item], until a round amends nothing; finding every
                           such place is mechanical, and whether one still holds is review's to
                           judge, the rule otherwise a fact
    present futures        a future a [model.package] is shaped for, an undecided one aside, which
                           is an [model.open question], stands as a present [model.item], most often
                           a rule its [model.module] ensures, its reason the future, in the
                           [model.decision] that keeps it
    futures restrained     a future stands as [present futures] has it only where its arrival, left
                           unwritten, would change or remove what stands rather than add to it; a
                           judgement
```
