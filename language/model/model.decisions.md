**MODEL-1. Say what a [package] means in the language's terms alone, holding its design apart from how it is written while stating publication and source identity abstractly.**
*Stated by* [meaning alone].
*Because* the part of the language every other part reads is then the most abstract and the one least changed: a change in how a [package] is written or stored leaves its [module]s, [interface]s and statements as they stand.
*Because* publication identity, [version] selection and source integrity are meanings a consumer relies on rather than file syntax, so they belong here while their concrete encodings remain with writing and storage.
*Accepting* every design rule here standing abstract, a breach of it found and placed by whatever reads how a [package] is written.
*Rejected* each design term saying where it is written, which moves the terms with every change of storage; and publication terms reduced to one manifest or [lock] syntax, which would make identity change with representation.
*Formerly* the renderer's NAME-3, in part.

**MODEL-2. Hold every [package] in five types, each with one job, [package], [module], [interface], [item] and [decision], and let a [package] play a [role].**
*Stated by* [package], [module], [interface], [item], [decision], [role] and [framework rules].
*Because* each answers a question a program's units already answer: a library what is published and trusted, a unit of compilation what is hidden, its declarations apart what may be relied on, a declaration what is stated; the [decision] is the one the language adds, since code never kept its why.
*Because* an [interface] of its own shows what may be relied on apart from any [body], and lets several [body]s stand behind one, each checked against what none of them wrote.
*Because* a [package]'s bounds differ in kind from a [module]'s: [package]s depend on one another and never nest, and [version]s and trust live with them, while [module]s nest within one and see one another by [sight].
*Because* [decision]s kept apart from [item]s keep their IDs out of every [interface], [item]s being named and referred to by name, which reads and refers as code does, while an ID is mechanical and hard to read.
*Because* within a [package] every [reference] changes with what it names, so an [item] needs no name that outlives a rename, while a [decision] is cited from places its [package] cannot update, whose citations must keep landing.
*Because* library, framework and system are each a [role], needing no type of their own.
*Accepting* five words to learn, each a familiar one; and that a rename changes every [reference] to what it renames.
*Rejected* one type, every unit a [module], which makes every rule say which job it means; three, with no [package] and [decision]s as [item]s, which leaves [version]s and trust nowhere but a root and puts the why among an [interface]'s names; a programming language's set, where a [body] defines its own surface; connectors and ports, a style rather than a type; [interface]s alone, every [body] generated, which leaves a [module]'s own choices nowhere to live; and names and IDs alike for every design [item], two identities, one of which nobody reads.

**MODEL-3. Make the root the [package] itself, and the public [interface]s it provides the [package]'s surface, with arbitrary facade names independent of internal [module] names.**
*Stated by* [package], [reference], [unique names] and [public closure].
*Because* a root named apart from its [package] would be a second thing bearing the [package]'s name.
*Because* the surface is then designed for the [package]'s users, apart from how its [module]s are cut, so they may be split, merged or moved with the surface as it stands.
*Because* inclusion republishes an internal [interface] whole without copying its statements, and separate public-interface and internal-module namespaces let a facade bear the natural name without exposing or colliding with the internal [module].
*Because* public [reference] paths resolve only through root [interface]s, with interface-first [reference] resolution in the root, so a same-name facade creates neither an ambiguous external path nor a back door into internal structure.
*Because* inclusion expands a public promise together with every [reference] it carries, so [public closure] recursively requires each target to remain available through a public root [interface] or a [dependency]'s surface; author-side [sight] alone cannot prove that a dependent can resolve it.
*Accepting* that an inclusion ties the surface to a part's [interface], so a part's change can reach the surface unseen until a published surface is compared with every inclusion expanded; recursive closure checks over included [interface]s and their opening paragraphs; and that public [reference]s in the root prefer the facade over a same-name internal [module], with no additional include or [uses] declaration.
*Rejected* [item]s re-exported one by one at the root, which leaves the surface read by traversal and changed by edits deep inside; public facade names forced to differ from internal [module] names, which invents synonyms for collision avoidance alone; exposing internal [module] trees directly, which abolishes the publication boundary; explicit public-interface dependency declarations and transitive re-export of every referenced [item], each duplicating facts or public names the surface already owns; and a surface rendered by tooling, which nobody reviews or versions.

**MODEL-4. Draw a [module] around one secret, kept behind the [interface]s it provides or implements.**
*Stated by* [module].
*Because* decomposing by the choices likely to change is what makes a unit a [module] to engineers, and a definition built on the secret holds whatever models read it.
*Because* a [module] then bounds an edit's reach: an edit to its [body] reaches nothing outside it, and an edit to an [interface] reaches exactly the [module]s whose [reference]s land in it and those implementing it, alone or through an [interface] including it, so the edits by which a system evolves stay closed.
*Rejected* fitting one session as part of the definition, a bound that moves with each model and differs between them, left as a recommendation for review to judge; a file, which lets how files lie on disk draw the design; a keeper's scope, which freezes an organisation chart into the [package]; a page about a topic, drawn around no secret; and a chunk cut to fit a session, which scatters every change to one concern.

**MODEL-5. State an [interface], holding all its users notice, apart from every [body], let a [module] implement one only where it may see it or its parent provides it, and let an [interface] include only what its [module] sees.**
*Stated by* [interface], [module], [body], [implementable] and [includable].
*Because* whoever relies on a [module] then reads what it may rely on alone, with no projection between, and several [body]s, or a regenerated one, are checked against what none of them wrote.
*Because* a [module]'s users meet it through its [interface]s alone, so whatever they notice is said where they read it, and a [body] says only how; what an agent writing a [body] decides alone is then noticed by nobody outside its [module].
*Because* a freedom stated keeps an [interface] from promising more than it means, while its users learn what they may not rely on, since what users can observe they come to rely on.
*Because* nothing then makes an [interface] belong to what implements it, so a [module] provides [interface]s for others to implement as readily as for itself, a parent among them providing what its parts implement.
*Because* an [interface] including one its [module] cannot see would hand its users, through it, what [sight] keeps from them.
*Accepting* that a [module] offering anything is stated twice over, what it offers and how it keeps it; and larger [interface]s with smaller [body]s.
*Rejected* public [item]s marked within a [module], under which a [body] defines its own surface and a reader sees it only through a projection; both forms allowed, two ways to write one thing; and a [body] deciding what users notice, which lets an agent's choice become what users rely on, kept by nobody.

**MODEL-6. Let a [module] see, as nested scopes do, the [interface]s of its parts, its siblings and its ancestors' siblings, every private [interface] above it and each it implements, a part's staying hidden outside its parent.**
*Stated by* [sight] and [unique names].
*Because* a [module]'s [body] and [decision]s are then hidden from every side, its parent composing it through its [interface]s alone, so the root can be discussed with every part's details set aside.
*Because* a [module] then reaches its siblings and its ancestors' siblings as a nested unit of a program reaches what encloses it, while a part's [interface]s, hidden outside its parent, keep each subtree's inside its own.
*Because* an ancestor then binds its whole subtree by a private [interface], as [sight] has it, with no ceremony, and what a [module] must read stays a rule.
*Because* an [interface]'s reach is then fixed by where its [module] stands and whether it is private, so no [item] carries a mark of visibility.
*Because* every [dependency] stands outside the tree, so any [module] may rest on its surface, as any unit of a program may on a library.
*Accepting* that a subtree's root no longer lists what its subtree takes from outside; that a middle parent cannot narrow what its parts see of an ancestor's private [interface]; and that deep [module]s see [item]s meant for direct parts.
*Rejected* flat [module]s, which leave a choice spanning several no home but the root; a child seeing its parent's [body], which couples every part to its parent's most volatile text; visibility marked per [item]; and a path opening one subtree, which nothing needs yet.

**MODEL-7. State every [item] in one of three [view]s, its kind the [view]'s, and a rule with its [direction].**
*Stated by* [view], [item], [direction] and [decision].
*Because* the three are what a program states one level down, types, functions and assertions, so an engineer reads them as a program one level up; and any system has parts, behaviour over time and what must always hold, so they name no domain.
*Because* each [view] holds one kind, so an [item]'s kind is never in doubt, and an [interface] and the [body] implementing it share one outline, checked [view] by [view].
*Because* a rule's [direction] is what substitution turns on, as design by contract has it; and an assumption is a rule required of the world, needing no kind of its own.
*Because* a [decision] explains [item]s of any [view], so as a [view] of its own it would state the what twice.
*Accepting* that a statement may sit between [view]s, as a protocol is both actions and rules, and is placed by judgement; and that a [module] with no behaviour states no Flow.
*Revisit* if a [package] needs a [view] none of the three can hold.
*Rejected* no [view]s, a free list where practice found three places; [view]s each [package] declares, a reader's map changing with every one; [decision]s as a fourth [view]; an architecture framework's viewpoints, which name a domain; no kinds, under which a guarantee cannot be told from a reliance; and kinds beside the [view]s, as term, contract, assumption, future and hole, a second classification.

**MODEL-8. Name no kind of material beside the five types, an [interface] being what is required of whatever implements it.**
*Stated by* [interface] and [body].
*Because* position already says what a kind would: an [interface] faces its users, so the root's [interface]s are what is required of the whole system, and a [body] is a design; a kind on top would classify the same statements twice.
*Because* the core then names no domain and stays small.
*Accepting* that nothing says requirement, so a newcomer learns from the definition that the root's [interface]s are the system's requirements; and that a requirement no one [interface] holds is a rule of the root's [interface]s or of its private one.
*Rejected* distinct kinds in the core, requirements, specifications, designs and guides, naming software's notions where position tells them apart; requirements stated apart from the root's own [interface]s, which restate them; and a guide people write taken as an input to generation, which would rest the code on generated prose.

**MODEL-9. Relate the types by five relations alone, each stated once: [uses], implementing, including, containing and depending.**
*Stated by* [uses], [module], [interface] and [dependency].
*Because* an [interface] is then built from others without restating them, and inclusion serves every level, since a parent may provide what a part implements.
*Because* implementing and including oblige otherwise than [uses] does, so each is told apart by rule.
*Because* inheritance among [interface]s amounts to inclusion with additions, and overriding an included promise would state against it.
*Because* [package]s depend on one another as [package] managers' units do, each a [dependency] of its dependent, whether selected externally or substituted at head by a [workspace].
*Accepting* no refinement of an included promise yet.
*Revisit* refinement, ensuring more or requiring less of an included [item], when a [module] needs to strengthen a promise it includes.
*Rejected* one relation, [uses], the rest in prose, while an agent must tell them apart by rule; satisfying and verifying, which name a domain's kinds; and refinement now, a need nobody has met.

**MODEL-10. Read a [module]'s [uses] off its [reference]s, each landing within its [sight], and an [interface]'s on nothing that implements it or [uses] it.**
*Stated by* [uses], [resolved] and [independent].
*Because* a list of [uses] beside the [reference]s would state twice what they say, two copies needing a check to stay equal.
*Because* a word escapes what a [reference] keeps: speaking of a [module] in words is resting on it unseen, so [sight] binds every mention, and whether a [module] stands alone is a fact of its [reference]s, stated nowhere else.
*Because* an [interface] stands apart from what implements it, so speaking of an implementation ties it to one, and of a user to one user, while its own [item]s say all a rule needs.
*Because* a [decision]'s reasons name what its [module] sees, so a choice argued from a parent's perspective is the parent's.
*Accepting* that a [decision]'s reasons cannot name its [module]'s users, even where they are why, and speak of what it provides instead.
*Revisit* a word for whatever implements an [interface], when a rule must speak of that as a whole.
*Rejected* words left free while [sight] binds [reference]s alone; a declared list of [uses], a second copy of the [reference]s; and a [module] binding at design what serves each [interface] it [uses], which only generation needs and is a [build]'s.

**MODEL-11. Name everything through its [module], alike from anywhere in its [package], a [module]'s own things alone within it, a [decision] by its ID within its [module] alone, and a [dependency] only through its public surface.**
*Stated by* [reference], [resolved] and [unique names].
*Because* each [item] then has one spelling from anywhere in its [package], so a move in the tree changes no [reference], and a part and a sibling are spelt alike.
*Because* a [module]'s own things are then named alone in its own statements, a clash between two of them being its own to make and to see the moment it is made.
*Because* a [pair]'s two halves are one [item] seen twice, what and how, so a name alone rests on both, while a path through the [interface] names the promise alone.
*Because* a [dependency]'s leaf gives the common local name without repetition, while explicit aliases distinguish same-leaf dependencies or simultaneously visible [version]s and collisions fail rather than shadow.
*Because* a public path follows root [interface]s alone, never the [dependency]'s internal [module] tree, and interface-first [reference] resolution within the root makes a same-name facade's public path unambiguous.
*Accepting* that a [reference] does not show where its target stands in the tree; that an [item] is spelt one way within its [package] and another from outside; and that an ambiguous default local name must be written through an alias.
*Rejected* one namespace for the whole [package], which couples the names of unrelated [module]s; a path spelt from where the referrer stands, which changes with every move; IDs resolving across [module]s, which rests one [module]'s reasons on another's; mandatory full Package URLs at every use, which sacrifices readable [reference]s; and inferred public paths through internal [module]s.

**MODEL-12. Let a [module], the root among them, provide one [default interface], which it implements wherever it has a [body], its [item]s named through the [module]'s name and it as `default` alone.**
*Stated by* [default interface], [reference] and [defaults].
*Because* a [module]'s main [interface] is then named briefly where it is used, through the [module]'s name, while the [module] stays the namespace.
*Because* a [module]'s name then names the [module] alone, within it as anywhere, and `default` names its [default interface] alike in every [module], so no rename changes what a [reference] rests on, and each [item] of it has one spelling.
*Because* a [module] with no [body] has nothing that could keep a promise.
*Because* the root bears its [package]'s name, so its [default interface] is reached through that name as any [module]'s is.
*Accepting* a name reserved, `default`; a [default interface] whose name in a [reference] is not the one it bears; and a [module] implementing its [default interface] without saying so.
*Rejected* no [interface] named for its [module], the stutter avoided by never wanting it; a [module]'s name standing for both it and its [default interface], which lets a rename change unseen what [reference]s rest on; the [default interface] named through the name it bears, or its [item]s after `default`, which spell one thing two ways; a mark for [module]s or for [default interface]s, syntax only one of them needs; and a root with no [default interface], whose main [interface] would be reached with its [package]'s name twice.

**MODEL-13. Pair an [item] of a [module]'s [body] with the [item] of its name in an [interface] the [module] states it is with, any [item] of an implemented [interface] free to stay unpaired.**
*Stated by* [pair], [body] and [paired].
*Because* the [interface] says what and the [body] says how, read side by side, with nothing restated that could drift.
*Because* a [pair] is then stated rather than a coincidence of names, so a misspelt one is found, where by name alone it passed as the [body]'s own and left the [interface]'s unpaired.
*Because* many promises need no how beyond the [body]'s other [item]s, so pairing each would restate them.
*Because* a promise may be kept in another [view] than its own, as a rule by an action.
*Accepting* that nothing marks a promise forgotten; and a [body]'s own [item]s barred from the names of an implemented [interface]'s [item]s.
*Rejected* pairing by name alone; a qualified name on every paired [item], which repeats what it is with on every line and spells one [item] two ways; each promise restated beside its how, kept equal by a check; prose beside the [item]s, derived text nobody keeps; every [item] paired, which would restate what needs no how; and the [item]s kept without a [pair] listed, a list that drifts as the [interface] grows.
*Formerly* the renderer's NAME-2, in part.

**MODEL-14. Name every [package], [module] and [interface] by a lowercase ASCII identifier, and no [item] with a `.`.**
*Stated by* [identifiers].
*Because* such a name stands unchanged wherever a [package] is stored or generated, as a step of a [reference]'s path, in an address and as an identifier in every target's code, with nothing converted.
*Because* lowercase ASCII leaves no two names that any form of storage could take for one, as names differing in case on a case-insensitive file system or in Unicode normalization on one that normalizes.
*Because* a dependent's [reference] spells the final segment of the [package id] as it spells any other step, while the namespace path remains free to its owner.
*Because* an [item]'s name stands nowhere but in [reference]s, so it keeps spaces, capitals and any script, holding no `.` alone, where a path's steps part.
*Accepting* no capitals and no other script in the name of a [package], a [module] or an [interface].
*Rejected* any name but one holding `.`, which keeps every other trouble; Unicode identifiers, which keep case and normalization; and `-` joining words in a local [package] name, which most targets' code must convert.

**MODEL-15. Keep a question open as an [item] promising only what it states as settled until a [decision] of its [module] answers it.**
*Stated by* [open question].
*Because* a question shapes the work before it is answered: a writer told that a search may come keeps what it writes open to one, where one never told commits to whatever is simplest.
*Because* the question then reaches exactly its readers, by [sight], as any [item] does, placed where they look.
*Because* an answer is then a [decision] like any other.
*Because* a form designed before its first use is designed blind, so a question waits for that use, while a [package] silent on what it has settled of the question would be inconsistent with it.
*Accepting* an [item] that promises nothing of what it keeps open until it is answered.
*Rejected* no way to keep a question, under which one reaches a writer only as prose in a [decision], or not at all; questions marked as undecided or as delegated, the second marking the default; a question that stops the work, where it should shape it; and what a writer does with an [open question] stated here, a rule writers keep across a [package]'s history rather than what a [package] means.

**MODEL-16. Let a [label] bind nothing, any reader taking it as context.**
*Stated by* [label].
*Because* the language's rules then stand where they are stated, in [item]s, so a [label] obliges nothing its [item] does not already say.
*Because* a [label] cannot be kept from agents, which read it as any reader does, so it binds nothing while anyone may take it as context.
*Accepting* that an agent treating a [label] as an instruction errs.
*Rejected* marks with meanings the language gives, kinds by another name; and [label]s for people alone, which agents read anyway.

**MODEL-17. Hold a [decision]'s why in its [field]s, each under the language's word for it.**
*Stated by* [decision] and [field].
*Because* a [decision] a writer took alone is then marked so, by the writer's role.
*Because* a superseded [decision] points to its successor, and one that moved names its former ID.

**MODEL-18. Let an action do only what its statement and the rules on it state.**
*Stated by* [stated effects].
*Because* an [interface] states everything its users notice through it, so an effect its statements omit is one the action does not have, said once for every [package].
*Rejected* each [interface] listing what its actions leave alone, a list without end; and an effect left for a [body] to decide, which its users would notice unstated.

**MODEL-19. Name in each [package] the [edition] it is written in, a [version] of the language's definition, the definition's own [edition] being its own [version].**
*Stated by* [edition].
*Because* a reader of any [package] then finds what the language's terms mean one step away, with the definition kept in one place.
*Because* an [edition] is needed once the language changes under [package]s written in it.
*Because* the first reader of any Quoll text is an agent, which needs no reader of its own, so reading the definition with the reader generated from it is the fixed-point test self-hosting compilers run.
*Because* the definition is then the first [package] to use each term it adds, and an [edition] has one meaning.
*Accepting* that a newcomer meets terms defined in their own terms; and that a reader for one [edition] is generated again, never reused, for one that changes how [package]s are written.
*Rejected* a glossary in every [package], a copy that drifts; the terms on a rendered page alone, while engineers read files; the definition written in the [edition] before its own, which keeps it behind its own terms; and the [edition] as one more [dependency], while it decides how the rest is read.

**MODEL-20. Keep the [package]s maintained together in one [project], at head, holding the [decision]s that bind several of them.**
*Stated by* [project], [dependency] and [project scope].
*Because* a [project] draws the line between what lives at head and what is pinned by [version], as a Cargo workspace does.
*Because* [decision]s binding several [package]s then have a home, and an edit across them stays closed, re-checking every dependent in one change.
*Because* [sight] then stays as it is, every shared term an [interface] of a [package] the others depend on.
*Accepting* a sixth type, a unit of maintenance beside the unit of publication; [package]s of one [project] written in different [edition]s; and a [project]'s [decision]s whose reach waits.
*Rejected* none, under which [package]s kept together would depend on one another by [version] before any is published, and their shared [decision]s have no home; [package]s nesting, which blurs a bound of publication; a [package] no other depends on standing for the [project], whose [decision]s cannot bind what it depends on; a list of [package]s for assembly alone, which leaves their [decision]s homeless; what a [project]'s [decision]s see and name designed now.
*Superseded by* MODEL-27.

**MODEL-27. Keep a narrow, unnamed [workspace] for maintenance and coordinated [release], never a [package]'s semantic context, and let it substitute member working trees for the same external [dependency] declarations.**
*Stated by* [workspace], [dependency] and [self-contained].
*Because* a fetched [package] must remain independently readable and publishable without its originating [workspace], so no [workspace] [decision], inherited [version] or [workspace]-only [dependency] identity may become part of its meaning.
*Because* the [workspace] still standardizes discovery and [release] coordination for [package]s maintained together, and its [decision]s can record membership and [release] rationale over [package] wholes and public surfaces without entering [package] [sight].
*Because* one versioned Package URL declaration serves both an outside consumer and local development: member manifests and [workspace] membership let tooling resolve the same identity to a working tree at head, without a path form or publication rewrite.
*Accepting* that local at-head checks can differ from checks against declared [release]s, so coordinated [release]s recheck the exact tagged set; that local substitution needs no [lock] entry for the member's content; and that [workspace] [decision]s cannot impose coding rules inside member [package]s.
*Rejected* moving [workspace]s out of the core, which discards a useful interoperability format rather than only the unwanted coupling; arbitrary [workspace] [decision]s or a fixed policy [interface] in [package] [sight], which creates hidden context or an inheritance mechanism before consumers; [workspace]-internal path dependencies, which point nowhere when a [package] is fetched alone; and requiring a [release] before every cross-[package] development change.

**MODEL-21. Keep a [package]'s [build], its [resources] and its [tests] open until a [package] needs each.**
*Stated by* [build], [resources] and [tests].
*Because* no [package] written in the language yet needs them.
*Rejected* their forms designed now; their forms left out of the definition; and the [resources] defined in full now.

**MODEL-22. Give a [package] a [build] exactly where it has a target.**
*Stated by* [build].
*Because* a [package] with no target has nothing for a [build] to state, so it holds none rather than an empty one.
*Rejected* a [build] in every [package], empty wherever there is nothing to assemble.

**MODEL-23. Give each [package] a canonical Package URL identity apart from every [source locator], and distribute its source directly from Git without requiring a central service or publisher signature.**
*Stated by* [package id], [source locator] and [distribution].
*Because* a standardized [package] identifier with a mandatory trust domain and user-defined namespace is globally namespaced and stable across hosting moves, while its ecosystem type gives it [package] rather than workload or location semantics.
*Because* location-based addition can discover that identity from fetched source before any identity resolver exists, and later identity-based [resolution] or mirrors can use the same declarations without migration.
*Because* direct source fetching needs no transformation or central publication service, while a selected commit and [package] hash provide per-consumer integrity without being mistaken for publisher authentication, global first-seen consistency or availability.
*Accepting* a Quoll Package URL type convention and eventual registration, validation that fetched source has the expected identity, no built-in identity resolver initially, and the initial absence of publisher authenticity; later signatures or transparency infrastructure can bind the same identity, locator, [version], commit and hash without changing content identity.
*Rejected* a SPIFFE or custom URI, which adds no [package] semantics or duplicates an existing [package]-identifier standard; a hosting path as identity, which makes a hosting move an identity change; flat names, which retain ambiguity; a mandatory registry or transparency service before its separate guarantees are operated; and mandatory publisher signatures before key establishment, rotation and revocation are designed.

**MODEL-24. Take [release] [version]s from root or path-qualified Git tags and development [version]s from three canonical pseudo-version forms, publishing coordinated [package] tags in [dependency] order.**
*Stated by* [version] and [release].
*Because* a [release] tag alone determines the [release] [version], eliminating drift with a self-declared field: the selected tag spells the selected semantic release [version] canonically, stable or prerelease, with `vX.Y.Z` the stable form; a root [package] uses that selected tag without a synthetic prefix or coordination of below-root [package]s, while a below-root [package] prefixes it with its [package] path, preserving independent cadences without probing.
*Because* the nearest valid ancestor release tag supplies the base, whose prerelease or stable form selects the no-base, prerelease-base or stable-release-base derivation and preserves semantic-version ordering around ancestor [release]s, and validating that tag, the UTC timestamp and 12-character revision against Git history gives independent resolvers one canonical development PURL; this ordering belongs to the spelling, not to a particular selection algorithm.
*Because* coordinated [release]s can share one [version] and commit through several [package] tags, and [dependency]-ordered publication keeps every visible dependent's same-release dependencies available while leaving partial publication recoverable.
*Accepting* the full three-form grammar and ancestor-tag, timestamp and revision validation, several tags for a coordinated [release], untagged [workspace] checks before those tags exist, and no selected [version] for a copied tree without Git history or a [resolution] record.
*Rejected* a manifest [version] or base manifest [version], which duplicates authority and cannot distinguish untagged snapshots; one simplified pseudo-version form, which loses base-ordering information; tool-specific spellings, which destroy canonical identity; root tags coordinating below-root [release]s; arbitrary literal tags; mandatory atomic publication; and arbitrary publication order.

**MODEL-25. Declare dependencies as exact or stable-only partial Package URL [selector]s, resolve the newest satisfying graph within each major [version], advance development branches only by explicit branch update, and use the PURL leaf as the default local name.**
*Stated by* [selector], [dependency], [resolution] and [lock].
*Because* exact and partial [selector]s express exact [release]s and compatible update requirements without a general range language: a compatibility series is one major, partial [selector]s match stable [release]s alone, and any prerelease or development pseudo-version must be named exactly.
*Because* newest-satisfying [resolution] obtains available fixes on fresh [resolution] and explicit stable updates, intersects compatible requirements instead of duplicating them, makes disjoint [selector]s within one major fail, and allows incompatible majors to coexist while the committed root [lock] keeps ordinary checks stable.
*Because* an ordinary stable update cannot silently replace an exact development snapshot; an explicit update of its branch resolves that branch anew and changes both pseudo-version and [lock], while a commit-pinned selection changes only through an explicit different [selector].
*Because* the canonical leaf is the least redundant common local name, and aliases outside the [dependency] list distinguish same-leaf dependencies or simultaneous [version]s without making [version] updates rewrite ordinary aliases.
*Accepting* backtracking and conflict diagnostics, potentially breaking explicit updates, multiple [version]s across incompatible majors, and exact development pseudo-[version]s remaining locked until their explicit branch or [selector] update.
*Rejected* exact [version]s only, which rejects compatible graphs or maximizes duplicates; exact minimums with minimal selection, whose lock-free determinism is redundant and whose older selections are not otherwise preferable; general comparator ranges before a consumer needs them; prereleases admitted by partial [selector]s, which lets an ordinary stable update replace development content implicitly; mandatory local names in the manifest; and [source locator]s in declarations.

**MODEL-26. Give each root [package] one committed full-graph [lock], whose selected [version], selected commit and [package] hash alone govern that consumer's exact sources and integrity.**
*Stated by* [lock] and [resolution].
*Because* committing the root's complete graph makes ordinary checks reproducible independently of later publication, while explicit updates alone change selected [version]s and content.
*Because* consumers resolve from [dependency] manifests and unify compatible requirements instead of recursively inheriting each [dependency]'s independent subgraph; [dependency] [lock]s remain useful source-locator hints without competing authority.
*Because* the full commit ties a [resolution] to one Git revision and the [package] hash verifies exactly the extracted [package] from any mirror or cache, so moved tags, corrupted delivery and changed caches fail rather than replacing reviewed content.
*Accepting* lockfile merge conflicts, transitive entries duplicated across independent roots, source-hint extraction from [dependency] [lock]s, and a checking mode that fails rather than updating implicitly; the hash supplies integrity, not publisher authenticity.
*Rejected* one [workspace] [lock], which leaves a fetched [package] without its own [resolution] and duplicates local membership; recursive authority of a [dependency]'s [lock], which prevents consumer-level reconciliation; competing [workspace] and [package] [lock]s, which need precedence policy; tag and commit alone, which ties verification to Git storage and the whole repository; and content hash as [version], which sacrifices meaningful ordering and compatibility.
