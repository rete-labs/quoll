**MODEL-1. Say what a [package] means in the language's terms alone, holding nothing of how it is written.**
*Stated by* [meaning alone].
*Because* the part of the language every other part reads is then the most abstract and the one least changed: a change in how a [package] is written or stored, to a format of the language's own say, leaves every term here as it stands.
*Because* whoever reads the language's terms, every other part and the agents' prompts among them, then rests on the terms rather than on their storage, and what they read depends on nothing.
*Accepting* every rule here standing abstract, a breach of it found and placed by whatever reads how a [package] is written.
*Rejected* each term saying where it is written, which moves the terms with every change of storage; each thing handed over with how it was written, which sets the writing among what the terms provide; each written form saying what it means, which mixes meaning into what is read off one text alone; a tie kept here to each text as written and to where each thing stands in it, of which what a [package] means needs nothing.
*Formerly* the renderer's NAME-3, in part.

**MODEL-2. Hold every [package] in five types, each with one job, [package], [module], [interface], [item] and [decision], and let a [package] play a [role].**
*Stated by* [package], [module], [interface], [item], [decision], [role] and [framework rules].
*Because* each answers a question a program's units already answer: a library what is published and trusted, a unit of compilation what is hidden, its declarations apart what may be relied on, a declaration what is stated; the [decision] is the one the language adds, since code never kept its why.
*Because* an [interface] of its own shows what may be relied on apart from any [body], and lets several [body]s stand behind one, each checked against what none of them wrote.
*Because* a [package]'s bounds differ in kind from a [module]'s: [package]s depend on one another and never nest, and [version]s and trust live with them, while [module]s nest within one and see one another by [sight].
*Because* [decision]s kept apart from [item]s keep their IDs out of every [interface], [item]s being named and referred to by name, which reads and refers as code does, while an ID is mechanical and hard to read.
*Because* within a [package] every [reference] changes with what it names, so an [item] needs no name that outlives a rename, while a [decision] is cited from places its [package] cannot update, as tickets, commits, reviews and code, whose citations must keep landing, without doubt as to which [decision] they mean.
*Because* library, framework and system are each a [role], needing no type of their own.
*Accepting* five words to learn, each a familiar one; and that a rename changes every [reference] to what it renames.
*Rejected* one type, every unit a [module], which makes every rule say which job it means; three, with no [package] and [decision]s as [item]s, which leaves [version]s and trust nowhere but a root and puts the why among an [interface]'s names; a programming language's set, where a [body] defines its own surface; connectors and ports, a style rather than a type; [interface]s alone, every [body] generated, which leaves a [module]'s own choices nowhere to live; the kinds and rules a framework may declare, stated here, which nothing yet designs; IDs for everything, mechanical where people read; names and IDs alike, two identities, one of which nobody reads; [decision]s cited by title, which changes as what was decided is refined, so citations from outside rot.

**MODEL-3. Make the root the [package] itself, and the [interface]s it provides the [package]'s surface.**
*Stated by* [package].
*Because* a root named apart from its [package] would be a second thing bearing the [package]'s name.
*Because* the surface is then designed for the [package]'s users, apart from how its [module]s are cut, so they may be split, merged or moved with the surface as it stands.
*Because* one mechanism, inclusion, then serves every level, the surface included, so a part implementing an [interface] of the root keeps it as stated once.
*Because* an [interface] none of its [module]s implements is abstract, as [package] has it, by a fact the [package] already shows, needing no mark.
*Accepting* that an inclusion ties the surface to a part's [interface], so a part's change can reach the surface unseen until a published surface is compared with every inclusion expanded.
*Rejected* [item]s re-exported one by one at the root, which leaves the surface read by traversal and changed by edits deep inside; a place for public [interface]s apart from the tree, a second place for what the root already holds; the surface stated in full at the root, which made the part serving it restate nearly all of it; a surface rendered by tooling, which nobody reviews or versions; a mark for an abstract [interface], a state the facts already give.

**MODEL-4. Draw a [module] around one secret, kept behind the [interface]s it provides or implements.**
*Stated by* [module].
*Because* decomposing by the choices likely to change is what makes a unit a [module] to engineers, and a definition built on the secret holds whatever models read it.
*Because* a [module] then bounds an edit's reach: an edit to its [body] reaches nothing outside it, and an edit to an [interface] reaches exactly the [module]s whose [reference]s land in it and those implementing it, alone or through an [interface] including it, so the edits by which a system evolves stay closed.
*Rejected* fitting one session as part of the definition, a bound that moves with each model and differs between them, left as a recommendation for review to judge; a file, which lets how files lie on disk draw the design; a keeper's scope, which freezes an organisation chart into the [package]; a page about a topic, drawn around no secret; a chunk cut to fit a session, which scatters every change to one concern.

**MODEL-5. State an [interface], holding all its users notice, apart from every [body], let a [module] implement one only where it may see it or its parent provides it, and let an [interface] include only what its [module] sees.**
*Stated by* [interface], [module], [body], [implementable] and [includable].
*Because* whoever relies on a [module] then reads what it may rely on alone, with no projection between, and several [body]s, or a regenerated one, are checked against what none of them wrote.
*Because* a [module]'s users meet it through its [interface]s alone, so whatever they notice is said where they read it, and a [body] says only how; what an agent writing a [body] decides alone is then noticed by nobody outside its [module].
*Because* a freedom stated keeps an [interface] from promising more than it means, while its users learn what they may not rely on, since what users can observe they come to rely on.
*Because* nothing then makes an [interface] belong to what implements it, so a [module] provides [interface]s for others to implement as readily as for itself, a parent among them providing what its parts implement.
*Because* an [interface] including one its [module] cannot see would hand its users, through it, what [sight] keeps from them, a part's [interface] hidden outside its parent or another subtree's private one.
*Accepting* that a [module] offering anything is stated twice over, what it offers and how it keeps it, as C's declarations and definitions are; and larger [interface]s with smaller [body]s.
*Rejected* public [item]s marked within a [module], under which a [body] defines its own surface and a reader sees it only through a projection; both forms allowed, two ways to write one thing; separate [interface]s only where several implement, beside marked [item]s, a second mechanism; a [body] deciding what users notice, or what they notice but may not rely on, which lets an agent's choice become what users rely on, kept by nobody.

**MODEL-6. Let a [module] see, as nested scopes do, the [interface]s of its parts, its siblings and its ancestors' siblings, every private [interface] above it and each it implements, a part's staying hidden outside its parent.**
*Stated by* [sight] and [unique names].
*Because* a [module]'s [body] and [decision]s are then hidden from every side, its parent composing it through its [interface]s alone, so the root can be discussed with every part's details set aside.
*Because* a [module] then reaches its siblings and its ancestors' siblings as a nested unit of a program reaches what encloses it, with no inclusion along the way, while a part's [interface]s, hidden outside its parent, keep each subtree's inside its own.
*Because* an ancestor then binds its whole subtree by a private [interface], as [sight] has it, with no ceremony, and what a [module] must read stays a rule.
*Because* an [interface]'s reach is then fixed by where its [module] stands and whether it is private, so no [item] carries a mark of visibility.
*Because* every [dependency] stands outside the tree, so any [module] may rest on its surface, as any unit of a program may on a library.
*Accepting* that a subtree's root no longer lists what its subtree takes from outside, so an ancestor's change reaches deep [module]s directly; that a middle parent cannot narrow what its parts see of an ancestor's private [interface]; and that deep [module]s see [item]s meant for direct parts.
*Rejected* flat [module]s, which leave a choice spanning several no home but the root; a child seeing its parent's [body], which couples every part to its parent's most volatile text; visibility marked per [item]; a part's [interface]s reaching outside its parent, which lets a [module] rest on what that parent never offered; [item]s carried down level by level, which made [interface]s of nothing but re-exports; a path opening one subtree, which nothing needs yet; fixed levels, one depth forced on every system.

**MODEL-7. State every [item] in one of three [view]s, its kind the [view]'s, and a rule with its [direction].**
*Stated by* [view], [item], [direction] and [decision].
*Because* the three are what a program states one level down, types, functions and assertions, so an engineer reads them as a program one level up; and any system has parts, behaviour over time and what must always hold, so they name no domain.
*Because* each [view] holds one kind, so an [item]'s kind is never in doubt, and an [interface] and the [body] implementing it share one outline, checked [view] by [view].
*Because* a rule's [direction] is what substitution turns on, as design by contract has it; and an assumption is a rule required of the world, needing no kind of its own.
*Because* a [decision] explains [item]s of any [view], so as a [view] of its own it would state the what twice.
*Accepting* that a statement may sit between [view]s, as a protocol is both actions and rules, and is placed by judgement; and that a [module] with no behaviour states no Flow.
*Revisit* if a [package] needs a [view] none of the three can hold.
*Rejected* no [view]s, a free list where practice found three places; [view]s each [package] declares, a reader's map changing with every one; [decision]s as a fourth [view]; an architecture framework's viewpoints, which name a domain; no kinds, under which a guarantee cannot be told from a reliance; kinds beside the [view]s, as term, contract, assumption, future and hole, a second classification; a future [item], which no [module] keeps now, a future being the reason for a present rule; a hole [item], which marks what is the default already.

**MODEL-8. Name no kind of material beside the five types, an [interface] being what is required of whatever implements it.**
*Stated by* [interface] and [body].
*Because* position already says what a kind would: an [interface] faces its users, so the root's [interface]s are what is required of the whole system, and a [body] is a design; a kind on top would classify the same statements twice.
*Because* the core then names no domain and stays small.
*Accepting* that nothing says requirement, so a newcomer learns from the definition that the root's [interface]s are the system's requirements; and that a requirement no one [interface] holds is a rule of the root's [interface]s or of its private one.
*Rejected* distinct kinds in the core, requirements, specifications, designs and guides, naming software's notions where position tells them apart; requirements stated apart, as [interface]s the root implements, which restate its own; a guide people write taken as an input to generation, which would rest the code on generated prose.

**MODEL-9. Relate the types by five relations alone, each stated once: [uses], implementing, including, containing and depending.**
*Stated by* [uses], [module], [interface] and [dependency].
*Because* an [interface] is then built from others without restating them, and inclusion serves every level, since a parent may provide what a part implements.
*Because* implementing and including oblige otherwise than [uses] does, so each is told apart by rule.
*Because* inheritance among [interface]s amounts to inclusion with additions, and overriding an included promise would state against it.
*Because* [package]s depend on one another as Cargo's crates do, each a [dependency] of its dependent.
*Accepting* no refinement of an included promise yet.
*Revisit* refinement, ensuring more or requiring less of an included [item], when a [module] needs to strengthen a promise it includes.
*Rejected* one relation, [uses], the rest in prose, while an agent must tell them apart by rule; satisfying and verifying, which name a domain's kinds; refinement now, a need nobody has met.

**MODEL-10. Read a [module]'s [uses] off its [reference]s, each landing within its [sight], and an [interface]'s on nothing that implements it or [uses] it.**
*Stated by* [uses], [resolved] and [independent].
*Because* a list of [uses] beside the [reference]s would state twice what they say, two copies needing a check to stay equal.
*Because* a word escapes what a [reference] keeps: speaking of a [module] in words is resting on it unseen, so [sight] binds every mention, and whether a [module] stands alone is a fact of its [reference]s, stated nowhere else.
*Because* an [interface] stands apart from what implements it, so speaking of an implementation ties it to one, and of a user to one user, while its own [item]s say all a rule needs.
*Because* a [decision]'s reasons name what its [module] sees, so a choice argued from a parent's view is the parent's.
*Accepting* that a [decision]'s reasons cannot name its [module]'s users, even where they are why, and speak of what it provides instead.
*Revisit* a word for whatever implements an [interface], when a rule must speak of that as a whole.
*Rejected* words left free while [sight] binds [reference]s alone, the hole through which a [module] spoke of what it could not see; a declared list of [uses], a second copy of the [reference]s; a [module] binding at design what serves each [interface] it [uses], which only generation needs and is a [build]'s.

**MODEL-11. Name everything through its [module], alike from anywhere in its [package], a [module]'s own things alone within it, and a [decision] by its ID within its [module] alone.**
*Stated by* [reference], [resolved] and [unique names].
*Because* each [item] then has one spelling from anywhere in its [package], so a move in the tree changes no [reference], and a part and a sibling are spelt alike.
*Because* a [module]'s own things are then named alone in its own statements, a clash between two of them being its own to make and to see the moment it is made.
*Because* a [pair]'s two halves are one [item] seen twice, what and how, so a name alone rests on both, while a path through the [interface] names the promise alone; the how alone means nothing apart from its promise, and has no name of its own.
*Because* [decision]s are seen as [sight] has it, so their IDs need name nothing beyond it.
*Accepting* that a [reference] does not show where its target stands in the tree; that an [item] is spelt one way within its [package] and another from outside; and that a name alone naming two things must be written in full.
*Rejected* one namespace for the whole [package], which couples the names of unrelated [module]s; a path spelt from where the referrer stands, which changes with every move; a [module]'s own [interface]s brought into its statements by a declaration that declares nothing; IDs resolving across [module]s, which rests one [module]'s reasons on another's.

**MODEL-12. Let a [module], the root among them, provide one [default interface], which it implements wherever it has a [body], its [item]s named through the [module]'s name and it as `default` alone.**
*Stated by* [default interface], [reference] and [defaults].
*Because* a [module]'s main [interface] is then named briefly where it is used, through the [module]'s name, while the [module] stays the namespace, as JavaScript's default export is.
*Because* a [module]'s name then names the [module] alone, within it as anywhere, and `default` names its [default interface] alike in every [module], so no rename changes what a [reference] rests on, and each [item] of it has one spelling.
*Because* a [module] with no [body] has nothing that could keep a promise.
*Because* the root bears its [package]'s name, so its [default interface] is reached through that name as any [module]'s is.
*Because* the one clash this allows, a name both an [item] of the [default interface] and another [interface], is the [module]'s own to make, seen where it is made.
*Accepting* a name reserved, `default`; a [default interface] whose name in a [reference] is not the one it bears; and a [module] implementing its [default interface] without saying so.
*Rejected* no [interface] named for its [module], the stutter avoided by never wanting it; the [module]'s name skipped, one namespace for the [package]; one fixed name for every main [interface], read in every [reference] and saying nothing; a [module]'s name standing for both it and its [default interface], which let a rename change unseen what [reference]s rest on; the [default interface] named through the name it bears, or its [item]s after `default`, which spell one thing two ways; a mark for [module]s or for [default interface]s, syntax only one of them needs; a [default interface] chosen by a declaration, a second way to say it, or by being a [module]'s only [interface], which breaks every [reference] when it gains a second; a [default interface] a [module] with a [body] leaves unimplemented, whose [item]s its name would reach with nothing keeping them; every [default interface] implemented, a [module] with no [body] among them, which would keep its promises with nothing to keep them; a root with no [default interface], whose main [interface] would be reached with its [package]'s name twice.

**MODEL-13. Pair an [item] of a [module]'s [body] with the [item] of its name in an [interface] the [module] states it is with, any [item] of an implemented [interface] free to stay unpaired.**
*Stated by* [pair], [body] and [paired].
*Because* the [interface] says what and the [body] says how, read side by side, with nothing restated that could drift.
*Because* a [pair] is then stated rather than a coincidence of names, so a misspelt one is found, where by name alone it passed as the [body]'s own and left the [interface]'s unpaired.
*Because* many promises need no how beyond the [body]'s other [item]s, so pairing each would restate them.
*Because* a promise may be kept in another [view] than its own, as a rule by an action.
*Accepting* that nothing marks a promise forgotten; and a [body]'s own [item]s barred from the names of an implemented [interface]'s [item]s.
*Rejected* pairing by name alone; a qualified name on every paired [item], which repeats what it is with on every line and spells one [item] two ways; each promise restated beside its how, kept equal by a check; prose beside the [item]s, derived text nobody keeps; every [item] paired, which restates what needs no how; the [item]s kept without a [pair] listed, a list that drifts as the [interface] grows.
*Formerly* the renderer's NAME-2, in part.

**MODEL-14. Name every [package], [module] and [interface] by a lowercase ASCII identifier, and no [item] with a `.`.**
*Stated by* [identifiers].
*Because* such a name stands unchanged wherever a [package] is stored or generated, as a step of a [reference]'s path, in an address and as an identifier in every target's code, with nothing converted.
*Because* lowercase ASCII leaves no two names that any form of storage could take for one, as names differing in case are on a case-insensitive file system, and names differing in Unicode's normalization on one that normalizes.
*Because* a dependent's [reference] spells a [package]'s name as it spells any other step.
*Because* an [item]'s name stands nowhere but in [reference]s, so it keeps spaces, capitals and any script, holding no `.` alone, where a path's steps part.
*Accepting* no capitals and no other script in the name of a [package], a [module] or an [interface].
*Rejected* any name but one holding `.`, which keeps every other trouble; Unicode identifiers, which keep case and normalization; `-` joining words, which most targets' code must convert.

**MODEL-15. Keep a question open as an [item] promising only what it states as settled until a [decision] of its [module] answers it.**
*Stated by* [open question].
*Because* a question shapes the work before it is answered: a writer told that a search may come keeps what it writes open to one, where one never told commits to whatever is simplest.
*Because* the question then reaches exactly its readers, by [sight], as any [item] does, placed where they look.
*Because* an answer is then a [decision] like any other.
*Because* a form designed before its first use is designed blind, so a question waits for that use, while a [package] silent on what it has settled of the question would be inconsistent with it.
*Accepting* an [item] that promises nothing of what it keeps open until it is answered.
*Rejected* no way to keep a question, under which one reaches a writer only as prose in a [decision], or not at all; questions marked as undecided or as delegated, the second marking the default; a question that stops the work, where it should shape it; what a writer does with an open question, and with what is left unstated, stated here, a rule writers keep across a [package]'s history rather than what a [package] means.

**MODEL-16. Let a [label] bind nothing, any reader taking it as context.**
*Stated by* [label].
*Because* the language's rules then stand where they are stated, in [item]s, so a [label] obliges nothing its [item] does not already say.
*Because* a [label] cannot be kept from agents, which read it as any reader does, so it binds nothing while anyone may take it as context.
*Accepting* that an agent treating a [label] as an instruction errs.
*Rejected* marks with meanings the language gives, kinds by another name; [label]s for people alone, which agents read anyway.

**MODEL-17. Hold a [decision]'s why in its [field]s, each under the language's word for it.**
*Stated by* [decision] and [field].
*Because* a [decision] a writer took alone is then marked so, by the writer's role.
*Because* a superseded [decision] points to its successor, and one that moved names its former ID.

**MODEL-18. Let an action do only what its statement and the rules on it state.**
*Stated by* [stated effects].
*Because* an [interface] states everything its users notice through it, so an effect its statements omit is one the action does not have, said once for every [package].
*Rejected* each [interface] listing what its actions leave alone, a list without end; an effect left for a [body] to decide, which its users would notice unstated.

**MODEL-19. Name in each [package] the [edition] it is written in, a [version] of the language's definition, the definition's own [edition] being its own [version].**
*Stated by* [edition].
*Because* a reader of any [package] then finds what the language's terms mean one step away, as a Rust crate, a script's first line or a JSON document's schema says it, with the definition kept in one place.
*Because* an [edition] is needed once the language changes under [package]s written in it.
*Because* the first reader of any Quoll text is an agent, which needs no reader of its own, so the regress that makes a compiler build itself with its previous release does not arise, and reading the definition with the reader generated from it is the fixed-point test self-hosting compilers run.
*Because* the definition is then the first [package] to use each term it adds, and an [edition] has one meaning.
*Accepting* that a newcomer meets terms defined in their own terms; and that a reader for one [edition] is generated again, never reused, for one that changes how [package]s are written.
*Rejected* a glossary in every [package], a copy that drifts; the terms on a rendered page alone, while engineers read files; the definition written in the [edition] before its own, which keeps it behind its own terms; a kernel defined by hand outside the language, a second form checked by none of its rules; no [edition] for the definition, its reading fixed by nothing; the [edition] as one more [dependency], while it decides how the rest is read.

**MODEL-20. Keep the [package]s maintained together in one [project], at head, holding the [decision]s that bind several of them.**
*Stated by* [project], [dependency] and [project scope].
*Because* a [project] draws the line between what lives at head and what is pinned by [version], as a Cargo workspace does.
*Because* [decision]s binding several [package]s then have a home, and an edit across them stays closed, re-checking every dependent in one change.
*Because* [sight] then stays as it is, every shared term an [interface] of a [package] the others depend on.
*Accepting* a sixth type, a unit of maintenance beside the unit of publication; [package]s of one [project] written in different [edition]s; and a [project]'s [decision]s whose reach waits.
*Rejected* none, under which [package]s kept together would depend on one another by [version] before any is published, and their shared [decision]s have no home; [package]s nesting, which blurs a bound of publication; a [package] no other depends on standing for the [project], whose [decision]s cannot bind what it depends on; a list of [package]s for assembly alone, which leaves their [decision]s homeless; what a [project]'s [decision]s see and name designed now.

**MODEL-21. Keep a [package]'s [build], its [resources] and its [tests] open until a [package] needs each.**
*Stated by* [build], [resources] and [tests].
*Because* no [package] written in the language yet needs them.
*Rejected* their forms designed now; their forms left out of the definition; the [resources] defined in full now.

**MODEL-22. Give a [package] a [build] exactly where it has a target.**
*Stated by* [build].
*Because* a [package] with no target has nothing for a [build] to state, so it holds none rather than an empty one.
*Rejected* a [build] in every [package], empty wherever there is nothing to assemble.
