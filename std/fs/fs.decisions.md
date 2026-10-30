**FS-1. Offer a small surface over native [path]s, whole files and directories, omitting streams, metadata, copying, moving and watching.**
*Stated by* [construct], [render], [join], [extract], [list], [inspect], [read], [write] and [remove].
*Because* [path] handling, inspection and removal complete the basic use and lifecycle of files and directories, while each omitted facility introduces requirements beyond that coherent core.
*Accepting* that later consumers will require additions to the surface.
*Rejected* listing, reading and writing alone, which leaves callers unable to [inspect] or [remove] what they handle; and a broad surface including the omitted facilities, whose distinct semantics have no stated requirements.

**FS-2. Hold [path]s opaquely in native operating-system form, with native-text conversion and joining and extraction by [name].**
*Stated by* [path], [name], [construct], [render], [join] and [extract].
*Because* a native [path] can represent whatever its operating system accepts, and operations over individual [name]s keep host separators and [path] syntax out of callers.
*Accepting* that [path] values and their textual forms differ between operating systems.
*Rejected* one portable [path] syntax, whose mapping could exclude valid native places; and bare text [path]s, which would make every caller handle native syntax and conversion [failure]s.

**FS-3. [read] and [write] file [content] as bytes alone.**
*Stated by* [content], [read] and [write].
*Because* complete bytes preserve text and non-text files alike without loss, alteration or an encoding choice that consumers have not specified.
*Accepting* that consumers must obtain encoded bytes elsewhere before writing text.
*Rejected* text alone, which cannot faithfully handle arbitrary files and imposes an encoding; and separate byte and text operations, which duplicate surface and require an encoding decision before a consumer does.

**FS-4. Return every operating-system and native-text conversion [failure] explicitly through [fs].**
*Stated by* [failure] and [completion].
*Because* callers can handle unsuccessful outcomes without knowing a target's exception or error mechanism, and no conversion is hidden by lossy replacement.
*Accepting* that a reader must consult the Rules view as well as each Flow item for an action's unsuccessful outcome, and that [fs] defines its own [failure] notion.
*Rejected* target-specific [failure] mechanisms outside this surface, which prevent portable handling; a generic result abstraction, which would introduce a general facility and another module without a present requirement; and repeating the [failure] alternative in every action, which duplicates one promise and invites drift.

**FS-5. Report symbolic links in listing, follow them for inspection, reading and writing, and [remove] links themselves.**
*Stated by* [kind], [list], [inspect], [read], [write] and [remove].
*Because* callers can distinguish a link from its target for safe traversal, while ordinary file operations retain native behavior and removal stays confined to the named tree.
*Accepting* that writing through a link changes its target, so replacing the link itself requires removing it first.
*Rejected* hiding links, which denies callers information needed for safe traversal; and never following links, which denies useful ordinary file behavior and departs from native operations.

**FS-6. Replace whole files and create missing parent directories on writing, without promising atomic replacement.**
*Stated by* [write].
*Because* one whole-file operation can establish its parent directories and replace [content] without introducing temporary-file and replacement semantics.
*Accepting* that a [failure] can leave a partial result, so callers requiring crash safety or concurrent readers cannot rely on this operation alone.
*Rejected* requiring existing parent directories, which leaves no way to create them through this surface; and atomic replacement, which requires stronger guarantees and does not compose with following symbolic links.

**FS-7. Remove files, symbolic links and whole directory trees through one recursive operation, never following links.**
*Stated by* [remove].
*Because* recursive removal is the basic counterpart to creating a tree, and leaving links unfollowed confines its effect to the tree named.
*Accepting* that removal is destructive and not transactional, so a caller must supply the intended [path] and handle partial [failure].
*Rejected* removing only files and empty directories, which makes every tree-owning caller implement traversal and link safety; and separate single and recursive operations, which expose two operations for one lifecycle need.

**FS-8. List native-order [entry]s with [path], [name] or conversion [failure], and [kind], and [inspect] [kind] alone.**
*Stated by* [entry], [list] and [inspect].
*Because* [path], [name] and [kind] support reading and descending into [entry]s, an unconvertible [name] leaves the [entry] usable by [path], and consumers can impose their own order where needed.
*Accepting* that deterministic output requires the consumer to sort, and that no size, timestamps or permissions are exposed.
*Rejected* guaranteed [name] sorting, which imposes an ordering cost and requires an order for unconvertible [name]s; and [name]s with existence-only inspection, which cannot support safe recursive traversal or distinguish a missing [path] from other inspection [failure]s.

**FS-9. Provide [default] through each target language's standard library, adapting it only where needed to keep [default]'s promises.**
*Stated by* [delegation].
*Because* target standard libraries already provide native file-system operations, leaving only their differences from [default]'s promises to adapt.
*Accepting* that each target may require different adaptation.
*Rejected* an independent file-system implementation, which duplicates facilities the target already supplies; and no body, which would leave [default] abstract.
