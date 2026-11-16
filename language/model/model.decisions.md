**MODEL-1. State design in the language's terms alone, factored into selectable semantic layers and holding publication and source identity apart from concrete notation.**
*Stated by* [kernel.meaning alone], [graph.abstract publication] and [kernel.layered principles].
*Because* common structural, publication, contract and representation meanings can then serve different sources without imposing files, [rich.standard view]s or publication on every one.
*Because* publication identity, [graph.version] selection and source integrity are meanings a consumer relies on rather than file syntax.
*Accepting* every design rule standing abstract, with principles applying only where their terms are selected and breaches placed by whatever reads a concrete form.
*Rejected* a second native ontology; one monolithic requirement set; and publication terms reduced to one manifest or [graph.lock] syntax.
*Formerly* the renderer's NAME-3, in part.

**MODEL-2. Hold every package in five types, each with one job, package, module, interface, item and decision, and let a package play a [graph.role].**
*Stated by* package, module, interface, item, decision, [graph.role] and [profile.framework rules].
*Because* each answers a question a program's units already answer: a library what is published and trusted, a unit of compilation what is hidden, its declarations apart what may be relied on, a declaration what is stated; the decision is the one the language adds, since code never kept its why.
*Because* an interface of its own shows what may be relied on apart from any [kernel.body], and lets several [kernel.body]s stand behind one, each checked against what none of them wrote.
*Because* a package's bounds differ in kind from a module's: packages depend on one another and never nest, and [graph.version]s and trust live with them, while modules nest within one and see one another by [kernel.sight].
*Because* decisions kept apart from items keep their IDs out of every interface, items being named and referred to by name, which reads and refers as code does, while an ID is mechanical and hard to read.
*Because* within a package every [kernel.reference] changes with what it names, so an item needs no name that outlives a rename, while a decision is cited from places its package cannot update, whose citations must keep landing.
*Because* library, framework and system are each a [graph.role], needing no type of their own.
*Accepting* five words to learn, each a familiar one; and that a rename changes every [kernel.reference] to what it renames.
*Rejected* one type, every unit a module, which makes every rule say which job it means; three, with no package and decisions as items, which leaves [graph.version]s and trust nowhere but a root and puts the why among an interface's names; a programming language's set, where a [kernel.body] defines its own surface; connectors and ports, a style rather than a type; interfaces alone, every [kernel.body] generated, which leaves a module's own choices nowhere to live; and names and IDs alike for every design item, two identities, one of which nobody reads.

**MODEL-3.** *Superseded by* MODEL-44

**MODEL-4. Draw a module around one secret, kept behind the interfaces it provides or implements.**
*Stated by* module.
*Because* decomposing by the choices likely to change is what makes a unit a module to engineers, and a definition built on the secret holds whatever models read it.
*Because* a module then bounds an edit's reach: an edit to its [kernel.body] reaches nothing outside it, and an edit to an interface reaches exactly the modules whose [kernel.reference]s land in it and those implementing it, alone or through an interface including it, so the edits by which a system evolves stay closed.
*Rejected* fitting one session as part of the definition, a bound that moves with each model and differs between them, left as a recommendation for review to judge; a file, which lets how files lie on disk draw the design; a keeper's scope, which freezes an organisation chart into the package; a page about a topic, drawn around no secret; and a chunk cut to fit a session, which scatters every change to one concern.

**MODEL-5. State a [rich.full interface] apart from every [kernel.body], holding all its users notice, and bound implementing and inclusion by declared [kernel.sight].**
*Stated by* [rich.full interface], module, [kernel.body], [kernel.implementable] and [kernel.includable].
*Because* users then read what they may rely on alone, while several bodies or a regenerated one are checked against what none of them wrote.
*Because* promises and freedoms keep an implementation's unnoticed choices from becoming public commitments, and an interface belongs to no one implementation.
*Because* inclusion cannot hand users what the providing module's [kernel.sight] withholds.
*Accepting* contract and body statements serving different purposes, larger interfaces with smaller bodies, and native surfaces whose fidelity is explicitly partial.
*Rejected* public items marked within a [kernel.body]; native symbols treated as the whole contract; and a permanent duplicate header for every native interface.

**MODEL-6. Require profile-declared abstract [kernel.sight], retain the current nested policy as canonical Quoll [kernel.sight], and narrow every task's inputs within that legal bound.**
*Stated by* [kernel.sight], [graph.package sight], [profile.canonical sight], [profile.canonical names] and [profile.bounded inputs].
*Because* structural resolution needs a declared sight without prescribing sibling, ancestor, export or native visibility rules.
*Because* the current canonical policy hides bodies and decisions, composes parts and siblings without facade boilerplate, and has no observed coupling problem that justifies rewriting it.
*Because* legal visibility exceeds useful task context, so every generating or reviewing task must receive only the interfaces, bodies, decisions and dependencies it needs.
*Accepting* that canonical modules may legally see more than a task needs, and that native visibility and review may give only partial agent-boundary enforcement whose limits are declared.
*Revisit* canonical visibility if a real package demonstrates leakage, excessive coupling or a needed control.
*Rejected* parent-mediated narrow sight, package-wide non-private sight, and compiler visibility treated as a complete bound on agent reading.

**MODEL-7.** *Superseded by* MODEL-29

**MODEL-8. Name no kind of material beside the five types, a [rich.full interface] being what is required of whatever implements it.**
*Stated by* [rich.full interface] and [kernel.body].
*Because* position already says what a kind would: an interface faces its users, so the root's interfaces are what is required of the whole system, and a [kernel.body] is a design; a kind on top would classify the same statements twice.
*Because* the core then names no domain and stays small.
*Accepting* that nothing says requirement, so a newcomer learns from the definition that the root's interfaces are the system's requirements; and that a requirement no one interface holds is a rule of the root's interfaces or of its private one.
*Rejected* distinct kinds in the core, requirements, specifications, designs and guides, naming software's notions where position tells them apart; requirements stated apart from the root's own interfaces, which restate them; and a guide people write taken as an input to generation, which would rest the code on generated prose.

**MODEL-9.** *Superseded by* MODEL-30

**MODEL-10. Read a module's [kernel.uses] off its [kernel.reference]s, each landing within its [kernel.sight], and an interface's on nothing that implements it or [kernel.uses] it.**
*Stated by* [kernel.uses], [kernel.resolved] and [kernel.independent].
*Because* a list of [kernel.uses] beside the [kernel.reference]s would state twice what they say, two copies needing a check to stay equal.
*Because* a word escapes what a [kernel.reference] keeps: speaking of a module in words is resting on it unseen, so [kernel.sight] binds every mention, and whether a module stands alone is a fact of its [kernel.reference]s, stated nowhere else.
*Because* an interface stands apart from what implements it, so speaking of an implementation ties it to one, and of a user to one user, while its own items say all a rule needs.
*Because* a decision's reasons name what its module sees, so a choice argued from a parent's perspective is the parent's.
*Accepting* that a decision's reasons cannot name its module's users, even where they are why, and speak of what it provides instead.
*Revisit* a word for whatever implements an interface, when a rule must speak of that as a whole.
*Rejected* words left free while [kernel.sight] binds [kernel.reference]s alone; a declared list of [kernel.uses], a second copy of the [kernel.reference]s; and a module binding at design what serves each interface it [kernel.uses], which only generation needs and is a [generation.assembly]'s.

**MODEL-11. Resolve every [kernel.reference] by one rule for internal and external readers, with [kernel.sight] only authorizing authorship, contextual shortest-unambiguous forms and explicit public [graph.exposure] paths across package bounds.**
*Stated by* [kernel.reference], [graph.exposure], [graph.public reference], [profile.canonical reference], [kernel.resolved], [profile.canonical resolved], [graph.dependency] and [graph.package names].
*Because* what a name denotes stays fixed wherever it is read, while [kernel.sight] separately determines what an author may write and a task may receive.
*Because* shortest unambiguous forms remain contextual, so shared resolution requires neither universally longest paths nor facade precedence; ambiguity fails instead.
*Because* a [kernel.pair]'s halves are one item seen twice, and a [graph.dependency]'s leaf gives a readable default local name with aliases for collisions.
*Because* an explicit public alias and its target's private [kernel.structural path] identify one interface through distinct references without exposing that structure or traversing a [graph.dependency]'s private [kernel.module tree]; a package name is not a removable prefix, and a local structural reference and package-qualified public path each retain one target for every reader.
*Because* an exact published address preserves a target's meaning while coordinated workspace members can revise at-head references together, and independent renames supply no basis for inferring logical identity.
*Because* profile-declared native structured references resolved against explicit [graph.dependency]s enter closed change, while unmarked prose cannot create a hidden formal relation.
*Accepting* qualification or aliases where public names collide, explicit errors for ambiguous short forms, upgrades revisiting broken or redirected references, and full-fidelity profiles flagging suspected references in free prose for review.
*Rejected* module-context target selection, separate internal and external reference languages, facade or module-first precedence, a removable package-qualification prefix, inferred public paths through private modules, IDs resolving across modules, durable IDs for every item, inferred identity across independent renames, native storage paths or symbols as the common public address, unmarked prose as a formal [kernel.reference], and mandatory full Package URLs at every use.

**MODEL-12. Let a module, the root among them, provide one [kernel.default interface], which it implements wherever it has a [kernel.body], its items named through the module's name and it as `default` alone.**
*Stated by* [kernel.default interface], [profile.canonical reference] and [kernel.defaults].
*Because* a module's main interface is then named briefly where it is used, through the module's name, while the module stays the namespace.
*Because* a module's name then names the module alone, within it as anywhere, and `default` names its [kernel.default interface] alike in every module, so no rename changes what a local structural [kernel.reference] rests on, and each item of it has one local structural spelling.
*Because* a module with no [kernel.body] has nothing that could keep a promise.
*Because* the root bears its package's name, so its [kernel.default interface] has the same local structural and explicitly exposed public treatment as any module's, without becoming public merely by existing.
*Accepting* a name reserved, `default`; a [kernel.default interface] whose name in a local structural [kernel.reference] is not the one it bears; legal public aliases continuing to its items without changing that structural rule; and a module implementing its [kernel.default interface] without saying so.
*Rejected* no interface named for its module, the stutter avoided by never wanting it; a module's name standing for both it and its [kernel.default interface], which lets a rename change unseen what [kernel.reference]s rest on; the [kernel.default interface] named through the name it bears, or its items after `default`, as local [kernel.structural path]s that spell one thing two ways; a mark for modules or for [kernel.default interface]s, syntax only one of them needs; and a root with no [kernel.default interface], whose main interface would be reached with its package's name twice.

**MODEL-13. Pair an item of a module's [kernel.body] with the item of its name in an interface the module states it is with, any item of an implemented interface free to stay unpaired.**
*Stated by* [kernel.pair], [kernel.body] and [kernel.paired].
*Because* the interface says what and the [kernel.body] says how, read side by side, with nothing restated that could drift.
*Because* a [kernel.pair] is then stated rather than a coincidence of names, so a misspelt one is found, where by name alone it passed as the [kernel.body]'s own and left the interface's unpaired.
*Because* many promises need no how beyond the [kernel.body]'s other items, so pairing each would restate them.
*Because* a promise may be kept in another [kernel.view] than its own, as a rule by an action.
*Accepting* that nothing marks a promise forgotten; and a [kernel.body]'s own items barred from the names of an implemented interface's items.
*Rejected* pairing by name alone; a qualified name on every paired item, which repeats what it is with on every line and spells one item two ways; each promise restated beside its how, kept equal by a check; prose beside the items, derived text nobody keeps; every item paired, which would restate what needs no how; and the items kept without a [kernel.pair] listed, a list that drifts as the interface grows.
*Formerly* the renderer's NAME-2, in part.

**MODEL-14. In canonical Quoll, name every package, module and interface by a lowercase ASCII identifier, and no item with a `.`; impose that spelling on no [profile.native profile].**
*Stated by* [profile.identifiers].
*Because* these names then stand unchanged in reference paths, addresses and generated target identifiers, with no case or Unicode-normalization ambiguity.
*Because* [profile.native profile]s map names their ecosystems already own rather than inheriting a concrete Quoll spelling rule.
*Because* an item's name keeps spaces, capitals and any script, excluding only the path separator.
*Accepting* no capitals or other script in canonical package, module or interface names.
*Rejected* Unicode identifiers and hyphenated local names in canonical Quoll; and lowercase ASCII imposed as a universal native naming rule.

**MODEL-15. Keep a question open as an item promising only what it states as settled until a decision of its module answers it.**
*Stated by* [rich.open question].
*Because* a question shapes the work before it is answered: a writer told that a search may come keeps what it writes open to one, where one never told commits to whatever is simplest.
*Because* the question then reaches exactly its readers, by [kernel.sight], as any item does, placed where they look.
*Because* an answer is then a decision like any other.
*Because* a form designed before its first use is designed blind, so a question waits for that use, while a package silent on what it has settled of the question would be inconsistent with it.
*Accepting* an item that promises nothing of what it keeps open until it is answered.
*Rejected* no way to keep a question, under which one reaches a writer only as prose in a decision, or not at all; questions marked as undecided or as delegated, the second marking the default; a question that stops the work, where it should shape it; and what a writer does with a [rich.open question] stated here, a rule writers keep across a package's history rather than what a package means.

**MODEL-16. Let a [rich.label] bind nothing, any reader taking it as context.**
*Stated by* [rich.label].
*Because* the language's rules then stand where they are stated, in items, so a [rich.label] obliges nothing its item does not already say.
*Because* a [rich.label] cannot be kept from agents, which read it as any reader does, so it binds nothing while anyone may take it as context.
*Accepting* that an agent treating a [rich.label] as an instruction errs.
*Rejected* marks with meanings the language gives, kinds by another name; and [rich.label]s for people alone, which agents read anyway.

**MODEL-17. Hold a decision's why in its [kernel.field]s, each under the language's word for it.**
*Stated by* decision and [kernel.field].
*Because* a decision a writer took alone is then marked so, by the writer's role.
*Because* a superseded decision points to its successor, and one that moved names its former ID.

**MODEL-18. Let an action do only what its statement and the rules on it state.**
*Stated by* [rich.stated effects].
*Because* a [rich.full interface] states everything its users notice through it, so an effect its statements omit is one the action does not have, said once for every package.
*Rejected* each interface listing what its actions leave alone, a list without end; and an effect left for a [kernel.body] to decide, which its users would notice unstated.

**MODEL-19. Name in each package the [graph.edition] it is written in, a [graph.version] of the language's definition, the definition's own [graph.edition] being its own [graph.version], and keep canonical Quoll source in `language` as the bootstrap [profile.canonical profile], satisfying [profile.profile semantics] by default for pure and mixed packages.**
*Stated by* [graph.edition], [profile.canonical profile] and [profile.canonical parity].
*Because* a reader of any package then finds what the language's terms mean one step away, with the definition kept in one place.
*Because* a [graph.edition] is needed once the language changes under packages written in it.
*Because* the first reader of any Quoll text is an agent, which needs no reader of its own, so reading the definition with the reader generated from it is the fixed-point test self-hosting compilers run.
*Because* the definition is then the first package to use each term it adds, and a [graph.edition] has one meaning.
*Because* keeping the canonical representation join in the definition avoids a two-package bootstrap and profile/edition discovery cycle, while semantic parity gives external [profile.native profile]s the same contract without requiring package symmetry.
*Accepting* that a newcomer meets terms defined in their own terms; that a reader for one [graph.edition] is generated again, never reused, for one that changes how packages are written; and the intentional package asymmetry, with later extraction possible only when a real consumer settles bootstrap and profile selection.
*Rejected* a glossary in every package, a copy that drifts; the terms on a rendered page alone, while engineers read files; the definition written in the [graph.edition] before its own, which keeps it behind its own terms; and the [graph.edition] as one more [graph.dependency], while it decides how the rest is read; a separate canonical-source profile package before its bootstrap and discovery joins exist; canonical source owned by a toolchain; and target-specific dialects for co-located Quoll.

**MODEL-20.** *Superseded by* MODEL-27

**MODEL-27. Keep a narrow, unnamed workspace for maintenance and coordinated [graph.release], never a package's semantic context, and let explicit, profile-supported substitution use member working trees for the same external [graph.dependency] declarations.**
*Stated by* workspace, [graph.dependency] and [graph.self-contained].
*Because* a fetched package must remain independently readable and publishable without its originating workspace, so no workspace decision, inherited [graph.version], hidden path rewrite or workspace-only [graph.dependency] identity may become part of its meaning.
*Because* the workspace still standardizes discovery and [graph.release] coordination for packages maintained together, and its decisions can record membership and [graph.release] rationale over package wholes and public surfaces without entering package [kernel.sight].
*Because* one versioned Package URL declaration serves both an outside consumer and local development: explicit member declarations and workspace membership let supported tooling resolve the same identity to a working tree at head, without a path form or publication rewrite.
*Accepting* that local at-head checks can differ from checks against declared [graph.release]s, so coordinated [graph.release]s recheck the exact tagged set; that local substitution needs no [graph.lock] entry for the member's content; that profiles may withhold substitution support; and that workspace decisions cannot impose coding rules inside member packages.
*Rejected* moving workspaces out of the core, which discards a useful interoperability format rather than only the unwanted coupling; arbitrary workspace decisions or a fixed policy interface in package [kernel.sight], which creates hidden context or an inheritance mechanism before consumers; workspace decisions binding member packages' meaning, which makes unpublished context part of that meaning; hidden or workspace-internal path dependencies, which point nowhere or silently change meaning when a package is fetched alone; and requiring a [graph.release] before every cross-package development change.

**MODEL-21. Keep the concrete [generation.assembly], [generation.target map], [generation.resources], [generation.tests] and [generation.trace link] forms open until the first derived-target implementation or profile needs each.**
*Stated by* [generation.assembly form], [generation.target map form], [generation.resources], [generation.tests] and [generation.trace link form].
*Because* their abstract semantics now serve generation and realization consumers, while concrete grammars and schemas designed before those consumers would be blind.
*Accepting* one common [generation.target map] form whose native locators remain profile-interpreted, and profile-specific concrete trace notation over common link meanings.
*Rejected* their forms designed now; their semantics left out of the definition; [generation.resources] defined in full now; and a different map grammar per profile.

**MODEL-22. Give a package a [generation.assembly] exactly where it declares derived [kernel.target]s, and a [generation.target map] for its derived [kernel.unit]s alone.**
*Stated by* [generation.assembly] and [generation.target map].
*Because* intended targets and bindings belong to authoritative source before realization, while actual native units and realization state belong to the target afterward; neither record can mirror or replace the other.
*Because* a canonical native package with no derived [kernel.unit]s has nothing for either record to state, and an ephemeral [kernel.derived view] needs its temporary map only until [generation.view closure].
*Accepting* separate source and target lifecycles, target-top maps auditable without the source checkout, and ephemeral maps surviving only in work history.
*Rejected* a [generation.assembly] in every package, empty wherever there is nothing to assemble; source-side maps mirroring native structure; scattered per-file provenance without a target-level record; and mapping canonical native units as though derived.

**MODEL-23. Give each package its ecosystem's canonical Package URL identity apart from every [graph.source locator], retain `pkg:quoll` and direct Git distribution for canonical Quoll source, and leave native metadata and distribution authoritative.**
*Stated by* [graph.package id], [graph.source locator], [graph.distribution] and [graph.dependency].
*Because* standardized ecosystem identities are globally namespaced and stable across hosting moves; canonical Quoll retains its mandatory trust domain and user-defined namespace, while a native package needs no second Quoll identity.
*Because* location-based addition can discover canonical Quoll identity from fetched source before any identity resolver exists, and later identity-based [graph.resolution] or mirrors can use the same declarations without migration.
*Because* native manifests and requirements already own their ecosystems' metadata, while canonical direct source fetching needs no transformation or central publication service; a selected commit and package content digest provide per-consumer integrity without being mistaken for publisher authentication, global first-seen consistency or availability.
*Accepting* heterogeneous canonical Package URL types, the Quoll Package URL type convention and eventual registration, validation that fetched source has the expected identity, no built-in identity resolver initially, and the initial absence of publisher authenticity, global first-seen consistency and a central availability guarantee; later signatures or transparency infrastructure can bind the same identity, [graph.source locator], [graph.version], commit and content digest without changing content identity.
*Rejected* a Quoll-only graph or Quoll metadata mirrors for native packages; a SPIFFE or custom URI, which adds no package semantics or duplicates an existing package-identifier standard; a hosting path as identity, which makes a hosting move an identity change; flat names or a vanity identity with no trust domain for canonical Quoll, which retain ambiguity; a mandatory registry or transparency service before its separate guarantees are operated; mandatory publisher signatures before key establishment, rotation and revocation are designed; and publication transformation of canonical Quoll source, which would make fetched source differ from its published package.

**MODEL-24. Under canonical Quoll source rules, take [graph.release] [graph.version]s from root or path-qualified Git tags and development [graph.version]s from three canonical pseudo-version forms, publishing coordinated package tags in [graph.dependency] order without imposing those rules on native ecosystems.**
*Stated by* [graph.version] and [graph.release].
*Because* a canonical Quoll [graph.release] tag alone determines the [graph.release] [graph.version], eliminating drift with a self-declared field: the selected tag spells the selected semantic release [graph.version] canonically, stable or prerelease, with `vX.Y.Z` the stable form; a root package uses that selected tag without a synthetic prefix or coordination of below-root packages, while a below-root package prefixes it with its package path, preserving independent cadences without probing.
*Because* the nearest valid ancestor tag for a release supplies the base, whose prerelease or stable form selects the no-base, prerelease-base or stable-release-base derivation and preserves semantic-version ordering around ancestor [graph.release]s, and validating that tag, the UTC timestamp and revision of 12 lowercase hexadecimal characters against Git history gives independent resolvers one canonical development PURL; this ordering belongs to the spelling, not to a particular selection algorithm.
*Because* coordinated canonical Quoll [graph.release]s can share one [graph.version] and commit through several package tags, and [graph.dependency]-ordered publication keeps every visible dependent's same-release dependencies available while leaving partial publication recoverable.
*Accepting* the full three-form grammar and ancestor-tag, timestamp and revision validation, several tags for a coordinated [graph.release], untagged workspace checks before those tags exist, no selected [graph.version] for a copied tree without Git history or a [graph.resolution] record, and native [graph.version] and publication mechanics remaining native.
*Rejected* a manifest [graph.version] or base manifest [graph.version] for canonical Quoll, which duplicates authority and cannot distinguish untagged snapshots; one simplified pseudo-version form, which loses base-ordering information; tool-specific spellings, which destroy canonical identity; root tags coordinating below-root [graph.release]s; arbitrary literal tags; mandatory atomic publication; arbitrary publication order; and canonical Git tags or pseudo-versions imposed on native ecosystems.

**MODEL-25. Under canonical Quoll source rules, declare dependencies as exact or stable-only partial Package URL [graph.selector]s, resolve the newest satisfying graph within each major [graph.version], advance development branches only by explicit branch update, and use the PURL leaf as the default local name, leaving native requirement and resolution rules native.**
*Stated by* [graph.selector], [graph.dependency], [graph.resolution] and [graph.lock].
*Because* canonical exact and partial [graph.selector]s express exact [graph.release]s and compatible update requirements without a general range language: a compatibility series is one major, partial [graph.selector]s match stable [graph.release]s alone, and any prerelease or development pseudo-version must be named exactly.
*Because* canonical newest-satisfying [graph.resolution] obtains available fixes on fresh [graph.resolution] and explicit stable updates, intersects compatible requirements instead of duplicating them, makes disjoint [graph.selector]s within one major fail, and allows incompatible majors to coexist while the committed root [graph.lock] keeps ordinary checks stable.
*Because* an ordinary stable update cannot silently replace an exact development snapshot; an explicit update of its branch resolves that branch anew and changes both pseudo-version and [graph.lock], while a commit-pinned selection changes only through an explicit different [graph.selector].
*Because* the canonical leaf is the least redundant common local name, and aliases outside the [graph.dependency] list distinguish same-leaf dependencies or simultaneous [graph.version]s without making [graph.version] updates rewrite ordinary aliases.
*Accepting* backtracking and conflict diagnostics, potentially breaking explicit updates, multiple [graph.version]s across incompatible majors, exact development pseudo-[graph.version]s remaining locked until their explicit branch or [graph.selector] update, and profile-specific native requirement and selection forms.
*Rejected* exact [graph.version]s only for canonical Quoll, which rejects compatible graphs or maximizes duplicates; exact minimums with minimal selection, whose lock-free determinism is redundant and whose older selections are not otherwise preferable; general comparator ranges before a canonical consumer needs them; prereleases admitted by partial [graph.selector]s, which lets an ordinary stable update replace development content implicitly; mandatory local names in the canonical manifest; [graph.source locator]s in canonical declarations; and canonical selectors or selection algorithms imposed on native ecosystems.

**MODEL-26. Under canonical Quoll source rules, give each root package one committed full-graph [graph.lock], whose selected [graph.version], selected commit and package content digest alone govern that consumer's exact sources and integrity, without replacing native locks.**
*Stated by* [graph.lock] and [graph.resolution].
*Because* committing a canonical root's complete graph makes ordinary checks reproducible independently of later publication, while explicit updates alone change selected [graph.version]s and content.
*Because* canonical consumers resolve from [graph.dependency] manifests and unify compatible requirements instead of recursively inheriting each [graph.dependency]'s independent subgraph; canonical [graph.dependency] [graph.lock]s remain useful [graph.source locator] hints without competing authority.
*Because* the full commit ties a canonical [graph.resolution] to one Git revision and the package content digest verifies exactly the extracted package from any mirror or cache, so moved tags, corrupted delivery and changed caches fail rather than replacing reviewed content.
*Accepting* lockfile merge conflicts, transitive entries duplicated across independent roots, source-hint extraction from canonical [graph.dependency] [graph.lock]s, a checking mode that fails rather than updating implicitly, and native lock formats and precedence remaining native; the content digest supplies integrity, not publisher authenticity.
*Rejected* one canonical workspace [graph.lock], which leaves a fetched package without its own [graph.resolution] and duplicates local membership; recursive authority of a canonical [graph.dependency]'s [graph.lock], which prevents consumer-level reconciliation; competing canonical workspace and package [graph.lock]s, which need precedence policy; tag and commit alone, which ties verification to Git storage and the whole repository; content digest as [graph.version], which sacrifices meaningful ordering and compatibility; and a canonical Quoll lock replacing native lock authority.

**MODEL-28. Factor the existing model into a [kernel.structural kernel], independent [graph.package graph] and [rich.rich contract] layers, and concrete [profile.representation profile]s, attaching principles by their terms.**
*Stated by* [kernel.layer], [kernel.structural kernel], [graph.package graph], [rich.rich contract], [profile.representation profile] and [kernel.layered principles].
*Because* native packages and non-code documents need the same structural identity, [kernel.reference]s, implementation, decisions and change closure without sharing publication, [rich.standard view]s or notation.
*Because* independent outer layers let native packages add graph semantics and documents add [rich.rich contract]s without forcing either through an unrelated full-Quoll layer.
*Accepting* substantial model reorganization and explicit placement of every item and principle, with full Quoll retaining its current obligations.
*Rejected* a separate native-document ontology, deferring the factoring for each [kernel.semantic profile] to infer, and a kernel containing nearly the whole model.

**MODEL-29. Declare versioned profile- or framework-defined [kernel.view]s over the common kernel, retaining Structure, Flow and Rules in canonical full Quoll and keeping decisions outside every [kernel.view].**
*Stated by* [kernel.view], item, [rich.standard view], [rich.direction], decision and [profile.framework rules].
*Because* [kernel.reference]s, decisions, [kernel.provenance] and change closure do not depend on the [rich.standard view]s, while domain statements still need explicit kinds and shared versioned semantics.
*Because* generic tooling can preserve structural operations for an unknown [kernel.view], leaving richer checks to its [kernel.semantic profile].
*Accepting* opaque generic handling of unknown statements, profile-specific checks, and no immediate domain-view design here.
*Revisit* a new canonical [kernel.view] only after deliberate evaluation against real consumers.
*Rejected* three [kernel.view]s for every [kernel.semantic profile], anonymous or viewless items, unversioned per-package inventions, and decisions as a fourth [kernel.view].

**MODEL-30. Assign authority per maintained fact and [kernel.unit], distinguish generation from source and target, keep provenance distinct from the five design relations and from [rich.conformance evidence], preserve delegated target decisions through localized change, and give separate generated [graph.native publication]s separate native identities without independent design authority.**
*Stated by* [kernel.unit], [kernel.source], [kernel.target], [kernel.generation activity], [kernel.provenance], [kernel.derived view], [graph.native publication], [generation.target map], [generation.localized generation], [kernel.single authority] and [kernel.provenanced].
*Because* agents may generate canonical or derived states, while packages mix canonical Quoll, canonical native and derived [kernel.unit]s without separate package modes or a synchronized two-way mirror.
*Because* separate [graph.native publication]s may be derived targets of one logical design under separate native Package URL identities and publication mechanics, retain delegated target-local decisions and evolve incrementally without becoming independent realizations or authorities for source facts.
*Because* a [kernel.derived view] may guide an accepted source change without authenticating itself or surviving as a second current implementation.
*Accepting* explicit per-[kernel.unit] authority and [kernel.provenance], bounded target-local choices, no guarantee that extraction is faithful or complete, and no partial-realization claim from a package-level provenance pointer whose mappings do not cover those [kernel.unit]s.
*Rejected* five design relations alone with [kernel.provenance] left implicit; [kernel.generation activity] synonymous with [kernel.target], [kernel.generation activity] limited to Quoll-to-native production, universal two-way synchronization, one publication identity across every native ecosystem, independent native authorities for the same source facts, [kernel.provenance] treated as [graph.dependency], independent realization or proof of conformance, every target choice copied upstream, whole regeneration after every source change, and missing source promises settled silently in the target.

**MODEL-31. Implement one abstract [profile.profile semantics] contract for native and mixed sources, composing [rich.semantic surface]s from native and supplemental artifacts with explicit [profile.profile fidelity] and one home for each contract fact.**
*Stated by* [kernel.semantic profile], [profile.representation profile], [profile.profile semantics], [profile.profile fidelity], [profile.profile identity], [profile.canonical profile], [profile.native profile], [rich.semantic surface], [rich.fidelity], [rich.surface fidelity] and [profile.contract placement].
*Because* common-graph participation and closed change need one minimum interpretation owned by the language rather than a replaceable toolchain, and a shared [profile.native profile] package can keep it through a module implementing that interface through target-specific statements and decisions rather than software methods.
*Because* native declarations already state some contractual facts, while co-located canonical Quoll, decisions, schemas and other artifacts can supply only those missing without a permanent mirror.
*Because* native-only systems need no separate Quoll surface, while independently owned or multiply realized contracts need an abstract Quoll package.
*Because* mappings, discovery, ecosystem conventions and fidelity limits belong to profiles rather than a fixed core metadata protocol, and unsupported obligations must remain visible rather than counting as full fidelity.
*Accepting* initially partial surfaces and guarantees, versioned profile-specific declarations, explicit additional profile-specific principles that do not weaken shared ones, and later contract extraction when its lifecycle becomes independent.
*Rejected* native symbols as the whole interface, mandatory full Quoll mirrors, project-specific mappings with no named profile boundary, a toolchain-owned profile API, independent principle sets per target language, tests or fixtures treated as the complete contract, and target-specific Quoll dialects.

**MODEL-32. Reuse implementing for native realization, keep dependency distinct from generated-from, binding and tracing roles and from provenance, use directional versioned [generation.trace link]s with optional derived indexes, and require target-appropriate evidence rather than inferring conformance from a relation.**
*Stated by* [rich.conformance evidence], [graph.dependency alone], [generation.trace link], [generation.trace index] and [generation.trace validity].
*Because* implementing already states that a module keeps an interface's promises, while dependency grants sight, provenance records generation, and binding and tracing declarations retain their own roles.
*Because* the realizing side already knows which public contract it implements or checks, so directional references let independent realizations avoid editing the specification while a derived index serves cross-cutting queries.
*Because* one semantic link vocabulary and canonical default support closed change and reusable tooling, while [profile.native profile]s need idiomatic concrete notation without changing reference or role meaning.
*Accepting* profile-specific realization mappings and trace notation, broken links revisited on upgrades, optional indexes, and no uniform evidence format or universal durable item identity.
*Revisit* durable IDs or rename metadata only for selected externally cited anchors where versioned public addresses and workspace-at-head updates cannot preserve a required citation.
*Rejected* new package-level realizes or conforms relations; realization, generated-from, binding, tracing or conformance inferred from dependency, provenance or link presence; specification-owned realization lists; traceability by naming or duplicated text; one mandatory concrete token for every native language; and unconstrained per-profile link meanings.

**MODEL-33. Keep one decision collection per module across representations, use Stated by references and unit authority provisionally to distinguish contract and delegated implementation choices, and migrate ephemeral-view intent to canonical modules at [generation.view closure].**
*Stated by* decision, [kernel.field], [kernel.decision authority], [graph.decision separation] and [generation.view closure].
*Because* module locality keeps reasons beside what changes without parallel Quoll and native documentation trees or a package-wide decision corpus.
*Because* an external source and its derived target have separate homes and authority, not merely different representations.
*Because* an ephemeral view serves a change rather than becoming a second current source, while accepted choices, rejected alternatives and unresolved questions must remain durable beside the surviving canonical items.
*Accepting* profile-specific decision notation, reference retargeting and decision moves with preserved IDs and history, minimal supplemental Quoll only where no surviving item can carry accepted intent, and later module splits where ownership or lifecycles genuinely differ.
*Revisit* the provisional authority distinction when [profile.native profile] or ephemeral-closure work supplies a better reference mechanism, without reopening module-local ownership by default.
*Rejected* parallel decision collections by representation or level, one package-wide collection, permanent [kernel.derived view]s retained as current packages, and realized native code retained without its accepted rationale or [rich.open question]s.

**MODEL-34. Own native contract and body changes as [profile.semantic delta]s rather than physical files, declaring whether each profile's classification is mechanical, inferred or partial.**
*Stated by* [profile.semantic delta] and [profile.semantic ownership].
*Because* the interface/body boundary is semantic even where a native artifact combines them, and public choices need independent contract review.
*Because* bounded semantic contexts let implementation roles retain body freedom without silently settling externally visible questions.
*Accepting* combined native diffs with semantic classification and additional review where separation is inferred or partial.
*Rejected* mandatory physical separation of contracts and bodies, and whole-file ownership that removes independent contract review.

**MODEL-35. Serve each semantic consumer group through kernel, graph, rich, profile and generation interfaces with no joint default, keeping one model module and one decision collection.**
*Stated by* [kernel.structural kernel], [graph.package graph], [rich.rich contract], [profile.representation profile], [generation.assembly], [generation.projection], [generation.realization], [generation.target map], [generation.view closure], [generation.trace link] and [graph.exposure].
*Because* kernel-only documents, graph consumers, rich-layer users, profile implementers and [profile.generation backend]s have disjoint reading needs, while the design ontology still forms one coherent module secret.
*Because* explicit root-reachable [graph.exposure]s publish the five interfaces at their natural public paths without a named facade, a same-named facade and module, or a flat aggregate alias that recreates whole-model usage.
*Accepting* qualified internal cross-interface references, deliberate migration of whole-model dependents and facade references, and explicit maintenance of five public exposures with no default.
*Rejected* a joint default or flat aggregate facade for compatibility, splitting the model module and its decision collection by layer, and retaining one monolithic interface.

**MODEL-36. Mark a native package as quollified and graph-discoverable through a minimal `package.quoll.toml` overlay carrying only cross-profile identity, edition, co-located canonical source, decision and applicable provenance facts, leaving its concrete schema open.**
*Stated by* [graph.native overlay] and [graph.native overlay form].
*Because* one discovery marker admits native and generated packages to the common graph without replacing their native manifests or duplicating metadata their ecosystems already own.
*Because* [kernel.semantic profile] identity and version, model [graph.edition], co-located canonical statements and decisions, and applicable [kernel.provenance] are cross-profile facts a native manifest cannot be assumed to carry.
*Accepting* profile-specific concrete fields, sidecar locations and additional schema; native Package URLs in the overlay; and no inherited canonical Quoll module-list, [graph.lock], Git pseudo-version or Markdown-file requirements.
*Rejected* a complete Quoll metadata mirror, which creates competing metadata and resolution authorities; and no common overlay, which loses reliable discovery and scatters the cross-profile declarations.

**MODEL-37. Resolve each ecosystem's subgraph under its own resolver and committed [graph.lock], and join exact native states, source revisions and content digests to exact Quoll selections and cross-profile [graph.dependency] edges in a consuming root's [graph.mixed graph] without re-resolving them.**
*Stated by* [graph.resolution], [graph.lock], [graph.mixed graph], [graph.federated exactness] and [graph.mixed graph form].
*Because* one common graph can join exact subgraph states without owning their selection algorithms, preserving each ecosystem's authority while making a mixed change reproducible and auditable.
*Because* a design-time Quoll contract [graph.dependency] need not supply a runtime native artifact, while a runtime native [graph.dependency] must remain published and resolved in its own ecosystem.
*Accepting* a [graph.mixed graph] record whose concrete form waits for a mixed profile, exact states repeated from native locks without duplicated resolution authority, and explicit failure where no reproducible cross-ecosystem selection is available.
*Rejected* one universal Quoll resolver and [graph.lock], which creates a second incompatible resolution authority; and disconnected ecosystem graphs with unversioned prose or local paths, which prevents exact reconstruction and mechanical closed change.

**MODEL-38. Keep [profile.native profile]s, [profile.profile adapter]s, one profile-neutral [profile.generation backend] and [profile.target support] as external capabilities, with shared profiles preferably versioned Quoll packages and first project-local profiles remaining structured decisions, orchestrate generation through composed adapters, and provide a complete [generation.generated only] abstraction with source-mapped diagnostics.**
*Stated by* [profile.native profile], [profile.profile identity], [profile.profile adapter], [profile.generation backend], [profile.target support], [profile.external roles], [generation.backend orchestration] and [generation.generated only].
*Because* interpretation, operational access, generation and runtime support answer different questions and evolve independently, so the core stays target-language independent even where one distribution carries several capabilities.
*Because* a shared profile has versioned semantic promises and decisions that suit a Quoll package, while a first project-specific profile needs no premature independent package or universal tool plug-in.
*Accepting* a workflow using only the capabilities it needs, several coordinated packages implementing one backend, adapters living with their profiles, [kernel.provenance] recording profile and adapter versions, substantial [profile.target support] machinery, explicit unsupported diagnostics, and no mandatory separate product for any role.
*Rejected* profiles, backends or [profile.target support] registries built into `language`; unnamed tool configuration without a versioned or decision-recorded profile; conflating interpretation, generation and runtime support into one concept; a separate complete backend for every target; one monolith without adapters; native observation alone as a [generation.generated only] workflow; and routine human native debugging or editing.

**MODEL-39. Declare each target's [profile.target binding] in [generation.assembly], realize an abstract interface through one reusable binding per target owned by [profile.target support], and have the [profile.generation backend] select it deterministically and record it in [kernel.provenance], without artificial packages for platform built-ins.**
*Stated by* [generation.assembly], [profile.target binding], [profile.binding selection], [graph.dependency alone] and [rich.conformance evidence].
*Because* the existing implementing relation carries the realization, while one shared binding per target keeps semantic adaptation out of every generated consumer and remains distinct from an ordinary [graph.dependency].
*Because* native facilities can be used directly only where they keep the interface's promises, with adaptation and target-owned conformance tests covering their semantic differences.
*Accepting* targets needing shims, design-time Quoll [graph.dependency]s that produce no runtime Quoll package [graph.dependency], and concrete registry and build syntax remaining open.
*Rejected* artificial quollified packages and overlays for every built-in, consumer-local inferred mappings, and a new realization or conformance relation beside implementing.

**MODEL-40. Derive a bounded canonical-Quoll [generation.projection] at an exact base, retaining source identity and authority and making mechanical, inferred, omitted and lossy information explicit.**
*Stated by* [generation.projection].
*Because* a scoped design context reduces reading without becoming a permanent mirror, while exact provenance and visible fidelity let review distinguish extracted facts from agent inference and known omissions.
*Accepting* profile-dependent fidelity, explicit uncertainty and review findings, broader scope after closed-change analysis, and no byte-for-byte reconstruction of the base.
*Rejected* a complete permanent mirror treated as a second source, and an unprovenanced agent summary with no exact base or distinction between extraction and inference.

**MODEL-41. Realize accepted deltas through coherent tickets and per-[kernel.unit] mappings with explicit ordering, partial state, conflicts, conformance and semantic rebasing, using package states, diffs, decisions coordinated through workspaces and provenance rather than a first-class change package.**
*Stated by* [generation.realization] and [generation.realization closure].
*Because* per-unit provenance and work tracking represent incremental delivery honestly without claiming that a package-level source pointer or an accepted proposal proves completion.
*Because* a changed base can change the delta's meaning, so references, contracts and decisions must be revisited rather than text patches replayed; direct, ephemeral and cross-package changes share this obligation.
*Accepting* tracker-held ordering and deferral, repeated conformance runs, possible re-projection, manual escalation of semantic conflicts, and no universal ticket or realization-status format.
*Revisit* a first-class change artifact only when a real native or mixed cross-package feature cannot coherently represent its ordering, partial realization, conflicts or rebasing through package states, diffs, decisions coordinated through workspaces, tickets and per-unit provenance.
*Rejected* atomic whole-proposal realization alone, untracked implementation from a design document, representation-local closure with silent cross-representation gaps, full mechanical closure as a precondition for partial profiles, a change package introduced before such a failure, and independent package changes where coordination is required.

**MODEL-42. Settle native contracts before bodies and generate against declared source-to-unit mappings, with one-to-one mapping common and source bodies and pairs constraining native bodies only to their stated depth.**
*Stated by* [generation.contract first].
*Because* target contract review catches surface mistakes before implementation, while persistent per-unit provenance bounds localized change and preserves the distinction between source promises and delegated implementation choices.
*Accepting* declared one-to-many and many-to-one mappings, partial or inferred mappings marked for review, and non-byte-reproducible native output.
*Rejected* whole-package prose-to-code regeneration without contract review or per-unit mappings, and independent native bodies that ignore source body depth or settle missing source promises silently.

**MODEL-43. Make a [kernel.module tree] the composition and history holder for one module and all its parts, and let a package contain exactly one and extend it with publication, [graph.version]s, trust and [graph.dependency] semantics without a second tree, history or decision ID space.**
*Stated by* [kernel.module tree], package and [kernel.layered principles].
*Because* a standalone tree's modules and decisions need one design and history holder without publication, while a package adds its own semantics to that same tree.
*Because* attaching principles to the holder whose terms they use lets kernel-only documents share them without acquiring publication semantics, leaving genuinely publication- and edition-specific obligations to the graph layer.
*Accepting* a composition and history holder that adds no material type or parallel decision collection, with graph packages extending rather than duplicating it.
*Rejected* each module as the whole tree's holder, which fragments history and decision IDs; mandatory packages for standalone trees; and a second tree, history or decision ID space in a package.

**MODEL-44. Make the root the package itself, publish only explicit root-reachable [graph.exposure]s of whole interfaces, close every supplied public [kernel.reference] through exposed items or public [graph.dependency]s, and distinguish local [kernel.structural path]s from package-qualified public paths.**
*Stated by* package, [graph.exposure], [kernel.structural path], interface, [graph.public reference], [graph.public closure], [graph.package names], [profile.public unit], [profile.public reading], [profile.canonical reference] and [profile.canonical resolved].
*Because* canonical structural identity and public accessibility answer different questions, and an explicit alias keeps a public contract stable while the private hierarchy changes without copying the target.
*Because* the interface is already the public contract boundary, so exposing it exposes all its items coherently and admits no module-target, item-target, same-unit-private or declaration-only exception.
*Because* a local structural reference and a package-qualified public path answer different naming needs, and keeping them distinct gives each complete spelling one target for every reader without a removable package prefix or module-first precedence.
*Because* root reachability distinguishes an intermediate re-export needed for [kernel.sight] from a deliberately published path, while one exposed interface may have several unique aliases and a [kernel.default interface]'s items remain continuable through every legal alias.
*Because* `includes` states unchanged whole-interface composition, whose included items are direct items of the including interface with no nested path or public alias.
*Because* a complete [graph.public closure] lets a reader resolve every supplied [kernel.reference] from identified public [kernel.source] [kernel.unit]s and public [graph.dependency] metadata alone, without private author context and without requiring native units to be files.
*Accepting* explicit exposure declarations and intermediate re-exports, unique declared paths including every legal continuation to an exposed [kernel.default interface]'s items, explicit exposure of a root [kernel.default interface] where its public contracts require it, [graph.public closure] checks over declaration units as well as contracts, unit identity and dependency metadata from adapters, and migration away from flat facades.
*Rejected* the former facade/inclusion publication model, which republished included interfaces through root facades and used facade or module-first precedence between a facade and a same-named structural module; public [kernel.structural path]s by default; module or individual-item exposure; same-unit-private and declaration-only closure exceptions; treating package qualification as a removable prefix; a central exposure manifest apart from the declarations needed for [kernel.sight]; one facade header per exposure; and renaming `includes` to `extends` or `composes`.
