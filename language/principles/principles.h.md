What every [model.kernel.module tree] keeps across its history and its writers, and what review judges of it, for whoever writes one, person or agent, and for any tool or reviewer that checks one: [information hiding], the root, read on a [model.kernel.module tree]'s relations, each reading a rule, whose breach is a fact about it, or a judgement, whose breach is an opinion, naming the [sign] that points review at a candidate; and beside them, rules and judgements of its items and decisions, and of how its writers take and record their choices.

## Structure

```
  information hiding  the root of every principle here: a module's
                      interfaces say only what others need of it, so that its users
                      may stay clueless about all they leave unsaid, and the edits by which a
                      [model.kernel.module tree] evolves stay closed

  sign                what review reads off a [model.kernel.module tree] and its history,
                      as which of its items change together, that points it at a
                      candidate breach of a rule whose breach is an opinion, a judgement,
                      rather than a fact: itself no breach; where a judgement names none,
                      or the history a [sign] reads is not yet written, review judges without one
```

## Rules

```
  ensures:
    applicability         [model.kernel.layered principles] attaches each principle here by the
                           [model.kernel.layer]s and workflow whose terms it uses, their composition
                           where it uses several, rather than by its representation; each applicable
                           principle keeps one statement across
                           [model.kernel.semantic profile]s, whose [model.profile.profile fidelity]
                           declares each applicable guarantee, with additional principles owned by a
                           [model.profile.representation profile]; neither applicability nor a
                           guarantee class decides whether a principle is required or recommended,
                           or whether checking it is mechanical

    terms only             these items speak of a [model.kernel.module tree] in the
                           terms of the module providing item alone, its modules, interfaces,
                           items, decisions and its history, never of
                           how it is written or stored, nor of who writes it or how review is run
  requires:
    single responsibility  [information hiding] read on what changes together: a
                           module answers to one reason to change, what changes
                           together for one reason standing together and what changes for different
                           reasons apart; a judgement, its [sign] co-change: items
                           that change together across modules, or apart within one
    open closed            [information hiding] read on how change arrives: a feature arrives as
                           what is added, a new module, as one implementing an
                           interface already stated or one keeping a requirement the
                           root takes on, rather than as edits across modules already
                           standing, and an interface grows by gaining
                           items; a judgement, its [sign] one feature's change touching many modules
    substitution           [information hiding] read on implementing: a module
                           implementing a [model.rich.full interface] states nothing against it,
                           requiring of its users and of the world no more than the
                           [model.rich.full interface] requires, and ensuring no less than it
                           ensures, so that any module implementing it may stand in
                           for another; a breach is found over the whole [model.kernel.body], no
                           [model.kernel.pair] proving it kept, by review and, once they are
                           designed, by the [model.generation.tests]
    interface segregation  [information hiding] read on what users rely on: an
                           interface serves one group of users, and one whose users
                           rest on disjoint parts of it is split; a judgement, its [sign] disjoint
                           use: modules whose [model.kernel.reference]s land on
                           disjoint parts of one interface
    dependency inversion   [information hiding] read on which way resting points: policy rests on no
                           mechanism, and the interfaces most rested on are those
                           stating least of any mechanism and change least, so that what changes
                           often rests on what changes seldom; between an interface
                           and what implements it or [model.kernel.uses] it, the way resting points
                           is [model.kernel.independent]'s rule, and how stability is stated waits;
                           the rest a judgement, its [sign] churn: a module resting
                           on an interface that changes more often than the module itself
    no cycle               [information hiding] read on where cycles form: no
                           interface rests on itself, one resting on each
                           interface it includes, on each its
                           [model.kernel.reference]s land on, or on an item of, and
                           on all that each of those rests on, so that an edit to an
                           interface reaches what rests on it along paths that end
    link locality          [information hiding] read on how items refer: a
                           [model.kernel.reference] goes from the less stable toward the more
                           stable; [model.profile.canonical sight] holds that by default, with
                           [model.kernel.independent], and between interfaces it is
                           [dependency inversion]'s

    bounded reading      [information hiding] read on what a writer reads:
                           [model.profile.bounded inputs] binds whatever representation holds the
                           module, while native visibility bounds compiled dependents
                           rather than an agent able to read beyond it; a
                           [model.kernel.semantic profile] relying on native visibility
                           and review alone claims no full enforcement, and
                           [model.profile.profile fidelity] states how completely this bound is kept
    session fit            a module fits one agent's session: one holding its
                           [model.kernel.body], its decisions, the
                           interfaces it provides and implements, those it
                           [model.kernel.uses] and those its parts provide, never their
                           [model.kernel.body]s, can do the work the module needs,
                           as reviewing, implementing or amending it, the root fitting as a leaf
                           does; a judgement, its [sign] that work outgrowing one session, which
                           points review at splitting the module
    several faces          a module providing several interfaces is
                           better with no [model.kernel.default interface] among them; a judgement
    needed pairs           a [model.kernel.body] [model.kernel.pair]s an item of an
                           interface its module implements only where
                           how it is kept needs saying beyond the [model.kernel.body]'s other
                           items; a judgement

    acyclic definitions    no item rests on itself through the items
                           its [model.kernel.reference]s land on and theirs in turn, but by naming
                           itself, as a tree's node holds nodes, so that some order of reading meets
                           each item after all it rests on: a relation between two
                           items is stated by one of them, and a family of
                           items by naming its members, none of which names it;
                           neither a [model.kernel.view]'s written item order nor
                           its blank lines state a relation: the order may group what a reader needs
                           together rather than putting each definition before its uses, and blank
                           lines separate visual groups alone
    no restating           no statement restates what an item states: it
                           [model.kernel.reference]s the item, and may build on an
                           item through a [model.kernel.reference] to it, a
                           decision's own statement aside; a decision
                           holds only what its [model.kernel.field]s hold, Stated by among them;
                           what holds of a [model.kernel.module tree], across items
                           or within one, is an item's to state, never a
                           decision's alone; and no two decisions state one choice
    own scope              each lead, item statement and decision statement states its own subject
                           positively: its meaning, promise or obligation, with the relationships
                           and prohibitions that bound that subject, rather than inventories of its
                           current environment or concerns owned elsewhere; an unresolved matter
                           stays stated as such, and each decision field serves its own purpose
    edition terms          where a package names a [model.graph.edition], no
                           statement restates what that [model.graph.edition] states: the
                           package writes in that [model.graph.edition]'s terms
    stated items           every item is named under Stated by of some
                           decision, or is a plain definition needing none; a
                           judgement, its [sign] an item that no Stated by names

    lifetime               a decision's ID is fixed when it is first written,
                           and no other decision of its [model.kernel.module tree]
                           ever bears it; until it is committed to its [model.kernel.module tree]'s
                           history it may be withdrawn, leaving nothing in its place, and once
                           committed it is never withdrawn, only superseded or moved; a superseded
                           one keeps only its ID and Superseded by pointer, its former prose left to
                           its history and its former choice among its successor's Rejected options;
                           one moving to another module leaves its own, committed or
                           not, for a successor there, as [model.kernel.field]'s Formerly has it
    labels kept            an agent writing a [model.kernel.module tree] keeps every
                           [model.rich.label] people gave an item or a
                           decision, and gives none of its own
    english                a [model.kernel.module tree] is better stated in English,
                           the language's own words being English, though it may be stated in any
                           natural language, or several; a judgement
    unstated choices       whoever writes a [model.kernel.module tree]'s items and
                           decisions decides what those it writes from leave
                           unstated, within all they state, recording each choice it so takes alone
                           as a decision under Taken by, for people to review
    answerable             a writer takes no choice that some answer to a
                           [model.rich.open question] would force undone: where one choice keeps
                           every answer possible it takes that one, and where none does it decides
                           provisionally, recording its decision under Taken by and
                           naming under Revisit the [model.rich.open question] it rests on, so that
                           answering the question finds every decision resting on it;
                           whether a choice keeps every answer possible is review's to judge, the
                           rule otherwise a fact
    body depth             a [model.kernel.body] says, of how its module keeps the
                           [model.rich.full interface]s it implements, all later
                           [model.kernel.generation activity] of its implementation must not change:
                           whatever anyone outside the module would notice came out
                           otherwise, what it leaves for a later run or [model.graph.release] to
                           read among it; the implementation decides alone what later
                           [model.kernel.generation activity] may change unnoticed, as its data
                           structures, algorithms, libraries and idioms, with
                           [model.kernel.single authority] fixing what a
                           [model.kernel.target] owns among those choices; whether anyone
                           would notice is review's to judge, the rule otherwise a fact
    reported questions     a writer meeting a question that what it writes from leaves open, and
                           that would be noticed outside what it writes, reports it against what
                           left it open and settles it provisionally until that answers it: a
                           [model.kernel.body]'s writer, meeting one that users would notice through
                           a [model.rich.full interface], against it, recording its choice as a
                           decision under Taken by, naming under Revisit the question
                           it reported; and a writer of an implementation, meeting one its
                           [model.kernel.body] should have settled, against the
                           [model.kernel.body], recording no choice for it in the
                           [model.kernel.module tree]; whether a question would be noticed is
                           review's to judge, the rule otherwise a fact

    closed change          a writer changing what an item states revisits each place
                           where a [model.kernel.reference] landing on it stands, each
                           [model.kernel.pair] whose half it is, each module
                           implementing an interface that holds it, as its own or by
                           inclusion, and each [model.kernel.target] [model.kernel.unit] whose
                           [model.kernel.provenance] maps its [model.kernel.source]
                           [model.kernel.unit]: the union of current dependents across
                           [model.kernel.source] and [model.kernel.target] [model.kernel.unit]s in
                           every representation, whether what it revisits restated the
                           item or only relied on it, and amends each that no longer
                           holds, revisiting in turn those of each amended item,
                           until a round amends nothing; a [model.kernel.derived view] adds
                           proposal-local dependents for its proposal's closure alone, never another
                           current graph; where a [model.kernel.semantic profile] supplies these
                           relations mechanically, finding every such place is mechanical; where its
                           mappings are inferred or partial, each inferred or unresolved
                           dependent is an explicit review obligation and uncertain finding, never
                           silent success;
                           and where discovery of a [model.kernel.reference], [model.kernel.pair],
                           implementing relation or [model.kernel.provenance] is unsupported, the
                           unresolved scope is an explicit review obligation and uncertain finding,
                           never silent success, with no claim of mechanical or complete closure;
                           whether one still holds is review's to judge, the rule otherwise a fact

    present futures        a future a [model.kernel.module tree] is shaped for, an undecided one
                           aside, which is a [model.rich.open question], stands as a present
                           item, most often a rule its module
                           ensures, its reason the future, in the decision that keeps it
    futures restrained     a future stands as [present futures] has it only where its arrival, left
                           unwritten, would change or remove what stands rather than add to it; a
                           judgement
```
