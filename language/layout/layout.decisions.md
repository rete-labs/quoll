+++
prelude = []
+++
**LAYOUT-1. Lay a [package] out as one directory, with the directories below its top, and say each canonical [source file]'s kind in its name.**
*Stated by* [package], [manifest], [modules], [lock], [assembly], [header], [private header], [body], [decisions] and [source file].
*Because* a name says what a [source file] is, as `.h` and `.c` do in C, so a person browsing a directory or a row of tabs sees each one's kind without opening it.
*Because* each [source file] then has one kind, read whole, its history the history of one thing.
*Because* the [body] and the [decisions] stand apart, so rewriting a [body] whole never touches the [decisions].
*Accepting* that the [package]'s top holds [source file]s of several kinds side by side, told apart by suffix alone; and a directory and a few files however little it holds.
*Rejected* a fixed name per kind in every directory, whose files share their names everywhere and are not told apart in tabs; one file per directory with a section per kind, from which one kind is read only by cutting it out of a file holding others; [header]s apart with the [body] and the [decisions] in one file, which rewriting the [body] would touch; any file holding any number of kinds, many ways to store one thing; a directory's files beside its siblings', as Rust's `foo.rs` beside `foo/`, which scatters them among others'; a file in every directory stating each of its files' kinds, with the suffixes as well, which states each kind twice and needs a check to keep the two equal; kinds declared in each file's front matter, learnt only by opening every file; a default arrangement that a file in a directory overrides, two ways to learn a file's kind; and any other way to lay a [package] out, each one a second way for every reader and tool to learn.

**LAYOUT-2.** *Superseded by* LAYOUT-18

**LAYOUT-18. Use `package.quoll.toml` for the canonical [package]'s public [manifest] and a quollified native [package]'s [native overlay], keeping their grammars apart.**
*Stated by* [manifest] and [native overlay].
*Because* the canonical [manifest] is the one public [source file] standing for its [package], while the same name at a native [package]'s top supplies the common discovery marker without making that overlay a canonical metadata mirror.
*Accepting* a word given to one canonical file kind, a compound suffix that marks both its format and its ownership, and a [native overlay] whose concrete schema waits for its first profile.
*Rejected* a map, which reads as a generic type rather than one [package]'s file; a name after the file itself, which says only where it is; a card, a word nobody gives a file; a Markdown shell for wholly structured canonical metadata; a complete canonical metadata mirror beside every native manifest, which creates two authorities; and no common [native overlay], which loses reliable discovery.

**LAYOUT-3. Say what a [package] is on disk in the language's own notation, and leave how a tool finds it to the tool.**
*Stated by* [path].
*Because* every tool that reads a [package] relies on what this part states, so it holds no one tool's choices, while how a tool reads the disk changes with the tool and the operating system, and nobody writing a [package] relies on it.
*Because* the language then depends on no file-system library, and a [package] reads alike on every system.
*Rejected* stating, beside the [package], how a tool lists directories, what it does with a link, in what order it hands things over, and what it reports when the disk fails it, which binds every tool to one tool's choices and tells a writer nothing a writer relies on; and the file system's own [path]s, which differ from one system to the next.

**LAYOUT-4. Tell each [source file]'s kind by its name and [path], reading no file.**
*Stated by* [kind by name].
*Because* a kind read off a name is seen at a glance, by a person in a directory's listing and by any tool, which reads no file to learn it.
*Because* a [source file] then counts wherever it stands, so one standing where it should not is found rather than missed.
*Rejected* every file read to learn its kind, which reads what nothing uses; and only the directories some file names, which needs that file read first and leaves a [source file] standing outside them unseen.
*Formerly* the renderer's FILE-25, its part the language's.

**LAYOUT-5. Leave out of a [package] everything whose name opens with `.`, with all it holds.**
*Stated by* [package].
*Because* the [package] then holds what its writers keep, while what tools and systems keep beside it, as a repository's `.git`, stays out.
*Accepting* that a file its writer names with a leading `.` is never part of a [package].
*Rejected* taking in everything found, which takes a repository's `.git` into the [package].
*Formerly* the renderer's FILE-10.

**LAYOUT-6. Stand each fixed file and the [assembly] at the top of the [package] or [workspace] it describes.**
*Stated by* [top only].
*Because* each name then makes one [source file] of the unit whose top holds it, so no second [manifest], [modules], [lock], [assembly] or [workspace] file stands below that top.
*Rejected* finding fixed files by their names anywhere, which makes a second [manifest] of one below the top.
*Formerly* the renderer's FILE-11.

**LAYOUT-7. Match a name against the language's names for its kinds exactly, case included.**
*Stated by* [exact case].
*Because* each kind is then said by the one way the language writes it, on every operating system alike.
*Accepting* that on a disk that ignores case, a [manifest] misspelt in case is no [source file].
*Rejected* ignoring case, under which one directory could hold two [manifest]s.
*Formerly* the renderer's FILE-19.

**LAYOUT-8. Read a name ending in `.private.h.md` as a [private header]'s.**
*Stated by* [private suffix].
*Because* `.private.h.md` is a suffix of the language's own, so a file bearing it is read by it, as its writer marked it, and every file so marked is found as a [private header].
*Rejected* reading `foo.private.h.md` as a [header] whose [stem] is `foo.private`, which drops the language's own suffix silently, the file read as of another kind than its writer marked.
*Formerly* the renderer's FILE-20.

**LAYOUT-10. Keep the [tests]' kind of [source file] open until a [package] needs it.**
*Stated by* [tests].
*Accepting* a kind of [source file] still to come, which [kind by name] tells apart, so that whoever must not read the [tests] can be kept from them by rule.
*Rejected* their kind, names and place designed now.

**LAYOUT-11.** *Superseded by* LAYOUT-19

**LAYOUT-19. Keep a [workspace] unnamed, with each member [package] in a directory of its own.**
*Stated by* [workspace].
*Because* each [package]'s top is then one, and every file below it belongs to that [package] alone, while the [workspace]'s own directory is all the identity the maintenance unit needs.
*Because* a [workspace] publishes nothing and nothing within a [package] needs to name it as a value.
*Accepting* an explicit membership list and fixed [workspace] files, without a second naming scheme for the group.
*Rejected* [package]s within one another's directories, under which one file would stand in two [package]s; a model-level [workspace] name before anything consumes one; and leaving the maintenance unit's fixed files open, which prevents deterministic discovery.

**LAYOUT-12. Hold an [assembly] at an authoritative source [package]'s top exactly where it declares derived targets, leaving its concrete form open.**
*Stated by* [assembly], [assembly form] and [assembly targets].
*Because* the source declaration names intended [assembly], distinct from the generation agents perform, the native toolchain's compilation and the generated target's realization map, so no file kind conflates those activities or authorities.
*Because* a canonical native [package] with no derived units has no declaration to make and must not acquire an empty file.
*Accepting* that a [package] gains its [assembly] with its first derived target, and that the concrete filename and grammar wait for the first derived-target implementation.
*Rejected* `build`, which conflates declaration, agent work and native tooling; `generate` or `generation`, which names the activity rather than its input declaration; and a mandatory [assembly] for a canonical native [package] with no derived units.

**LAYOUT-14. Name each [body] and [decisions] below the top after the directory holding it, and hold one of each at most.**
*Stated by* [stem] and [one each].
*Because* a [body] or a [decisions] opened alone, or among others in tabs, then shows by its name which directory it stands in, and the files of directories named apart are never named alike.
*Because* a free [stem] names nothing its directory does not, and lets the two disagree.
*Because* at the [package]'s top the directory is freely named, as [package] has it, so its name can fix no [stem] there.
*Because* a directory holding one of each keeps every [source file] whole and read whole, while what grows too large is divided into directories, never into files, where its [path] shows it.
*Accepting* a [stem] that changes whenever its directory is renamed, and a check that it does.
*Revisit* custom locations, when a [package] needs them.
*Rejected* a free [stem], a second name for what the directory names; a fixed [stem] in every directory, as `body.md`, whose files are not told apart in tabs; several [body]s or [decisions] in one directory, a directory divided into files; and custom locations, a [source file] standing elsewhere than its [stem] names, a second way for every reader and tool to learn.

**LAYOUT-15. Hold a [manifest] in every canonical Quoll source [package].**
*Stated by* [one manifest].
*Because* the [manifest] is the public file by which a canonical [package]'s top is known, so every canonical Quoll source [package] holds the one file that stands for it; a native [package]'s overlay is not this canonical [manifest].

**LAYOUT-16. Separate canonical public [package] metadata, private membership, dependency resolutions and [workspace] membership into fixed files, using the `.quoll.toml` suffix for structured metadata, with [workspace decisions] optional where no workspace-level rationale exists, and keep those rules within the canonical Quoll source profile.**
*Stated by* [modules], [lock], [workspace manifest], [workspace decisions], [one modules], [one lock], [workspace files] and [profile scope].
*Because* fixed names let people and tools discover each canonical unit and each kind of statement without searching arbitrary directories, while separate public and private files keep internal structure out of the published surface.
*Because* the compound suffix leaves the artifact kind first, marks Quoll ownership unmistakably beside another ecosystem's metadata, and remains an ordinary structured-data suffix for generic tools.
*Because* [workspace decisions] keep the established entry file kind rather than giving a structured [manifest] two unrelated grammars, and the file appears with the first workspace-level rationale instead of being kept empty.
*Because* a native [package] retains its own manifest, resolution, lock and release/source metadata authorities rather than inheriting the canonical [modules], Quoll [lock], pseudo-version or Markdown file rules.
*Accepting* longer filenames, a membership file that is metadata rather than a readable [package] overview, a committed [lock] for every canonical root [package], no empty [workspace decisions] file where none has anything to record, and native [package]s without canonical metadata files.
*Rejected* generic structured filenames that blend into a mixed directory; a `quoll.` prefix or hyphenated abbreviation, which trade readable kind names for grouping or brevity; one [manifest] mixing public and private material; a [workspace] [lock] competing with each [package]'s own resolution; one [workspace] file mixing membership with entries; a mandatory empty [workspace decisions] file, which adds ceremony without a statement; and imposing the canonical metadata, lock or Markdown rules on every native [package], which creates a second authority and pre-empts its profile.

**LAYOUT-17. Hash exactly the selected canonical Quoll source [package]'s portable regular files with Go `dirhash.Hash1` and a SHA-256 multihash, rejecting content that cannot restore consistently across supported systems.**
*Stated by* [content hash].
*Because* the canonical [package] is the publication unit for this profile, so hashing its own [path]s and raw blob bytes verifies the same delivered text from a mirror or extracted cache independently of repository history, neighboring content and archive metadata.
*Because* the established summary algorithm specifies each file digest, two spaces, the UTF-8 `/` [path] and a newline before the outer SHA-256 digest, while the community [multihash specification](https://github.com/multiformats/multihash) assigns `0x12` to SHA-256 and uses `0x20` for the 32-byte digest length, without replacing the summary serialization.
*Because* raw bytes and portable [path]s avoid line-ending, filter and separator differences, while rejecting executable and special modes, symlinks, gitlinks, case collisions and Windows-reserved names prevents a tree that hashes on one system but cannot restore safely on another.
*Accepting* rejection of non-portable canonical [package]s at resolution, independent implementations checked against shared test vectors, and native [package]s retaining their own release and source metadata rather than inheriting this digest rule.
*Rejected* preserving executable or symlink metadata, which creates platform differences without a demonstrated text-source consumer; NAR, Git tree objects, canonical TAR and a custom binary serialization, each retaining unwanted metadata, requiring new normalization or inventing a format without an interoperability advantage; hashing the whole repository or an archive; and imposing this canonical content digest on every native [package].

**LAYOUT-20. Keep one common [target map] at a generated target [package]'s top for its derived units, leaving its concrete filename and grammar open.**
*Stated by* [target map] and [map when derived].
*Because* intended [assembly] and actual realization have different homes and lifecycles: the authoritative source declares targets before they exist, while each generated target records its own derived units afterward.
*Because* one canonical metadata kind shared by every profile keeps the realization record common without imposing the canonical Quoll source profile's file rules on native [package]s.
*Accepting* that the concrete filename and grammar wait for the first derived-target implementation, and that a mixed [package]'s map covers its derived units alone.
*Rejected* a complete map only in the authoritative source, which makes it mirror target structure and leaves the generated target without its own realization record; scattered per-file annotations, which lose the coherent target-level record; per-profile map grammars, which fragment one common record; and requiring either an [assembly] or a [target map] of a canonical native [package] with no derived units.
