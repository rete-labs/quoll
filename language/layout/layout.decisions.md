**LAYOUT-1. Lay a [package] out as one directory, with the directories below its top, and say each [source file]'s kind in its name.**
*Stated by* [package], [manifest], [build], [header], [private header], [body], [decisions] and [source file].
*Because* a name says what a [source file] is, as `.h` and `.c` do in C, so a person browsing a directory or a row of tabs sees each one's kind without opening it.
*Because* each [source file] then has one kind, read whole, its history the history of one thing.
*Because* the [body] and the [decisions] stand apart, so rewriting a [body] whole never touches the [decisions].
*Accepting* that the [package]'s top holds [source file]s of several kinds side by side, told apart by suffix alone; and a directory and a few files however little it holds.
*Rejected* a fixed name per kind in every directory, whose files share their names everywhere and are not told apart in tabs; one file per directory with a section per kind, from which one kind is read only by cutting it out of a file holding others; [header]s apart with the [body] and the [decisions] in one file, which rewriting the [body] would touch; any file holding any number of kinds, many ways to store one thing; a directory's files beside its siblings', as Rust's `foo.rs` beside `foo/`, which scatters them among others'; a file in every directory stating each of its files' kinds, with the suffixes as well, which states each kind twice and needs a check to keep the two equal; kinds declared in each file's front matter, learnt only by opening every file; a default arrangement that a file in a directory overrides, two ways to learn a file's kind; and any other way to lay a [package] out, each one a second way for every reader and tool to learn.

**LAYOUT-2. Call `package.md` the [package]'s [manifest].**
*Stated by* [manifest].
*Because* it is the one [source file] standing for its [package], as Cargo's `Cargo.toml` and npm's `package.json` stand for theirs, so the word is the one engineers already give such a file.
*Accepting* a word given to one file alone, at the top.
*Rejected* a map, which reads as a generic type rather than one [package]'s file; a name after the file itself, which says only where it is; and a card, a word nobody gives a file.

**LAYOUT-3. Say what a [package] is on disk in the language's own notation, and leave how a tool finds it to the tool.**
*Stated by* [path].
*Because* every tool that reads a [package] relies on what [layout] states, so it holds no one tool's choices, while how a tool reads the disk changes with the tool and the operating system, and nobody writing a [package] relies on it.
*Because* the language then depends on no file-system library, and a [package] reads alike on every system.
*Rejected* stating, beside the [package], how a tool lists directories, what it does with a link, in what order it hands things over, and what it reports when the disk fails it, which binds every tool to one tool's choices and tells a writer nothing a writer relies on; and the file system's own paths, which differ from one system to the next.

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

**LAYOUT-6. Stand the [manifest] and the [build] at the [package]'s top alone.**
*Stated by* [top only].
*Because* each name then makes one [source file] of the [package], so no second [manifest] stands below a top.
*Rejected* finding them by their name anywhere, which makes a second [manifest] of one below the top.
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
*Rejected* reading `foo.private.h.md` as a [header] whose stem is `foo.private`, which drops the language's own suffix silently, the file read as of another kind than its writer marked.
*Formerly* the renderer's FILE-20.

**LAYOUT-10. Keep the [tests]' kind of [source file] open until a [package] needs it.**
*Stated by* [tests].
*Accepting* a kind of [source file] still to come, which [kind by name] tells apart, so that whoever must not read the [tests] can be kept from them by rule.
*Rejected* their kind, names and place designed now.

**LAYOUT-11. Stand each [package] of a [project] in a directory of its own, and keep the [project]'s own files open until a [project] needs them.**
*Stated by* [project] and [project files].
*Because* each [package]'s top is then one, and every file below it belongs to that [package] alone.
*Because* no [package] yet stands in a [project] with a second.
*Rejected* [package]s within one another's directories, under which one file would stand in two [package]s; and the [project]'s own files designed now.

**LAYOUT-12. Hold a [build] at a [package]'s top, or none.**
*Stated by* [build].
*Because* no name or [path] says whether a [package] should hold one, and no [package] must then hold a file it has no use for.
*Accepting* that a [package] gains its [build] when it first needs one.

**LAYOUT-14. Name each [body] and [decisions] below the top after the directory holding it, and hold one of each at most.**
*Stated by* [stem] and [one each].
*Because* a [body] or a [decisions] opened alone, or among others in tabs, then shows by its name which directory it stands in, and the files of directories named apart are never named alike.
*Because* a free stem names nothing its directory does not, and lets the two disagree.
*Because* at the [package]'s top the directory is freely named, as [package] has it, so its name can fix no stem there.
*Because* a directory holding one of each keeps every [source file] whole and read whole, while what grows too large is divided into directories, never into files, where its [path] shows it.
*Accepting* a stem that changes whenever its directory is renamed, and a check that it does.
*Revisit* custom locations, when a [package] needs them.
*Rejected* a free stem, a second name for what the directory names; a fixed stem in every directory, as `body.md`, whose files are not told apart in tabs; several [body]s or [decisions] in one directory, a directory divided into files; and custom locations, a [source file] standing elsewhere than its stem names, a second way for every reader and tool to learn.

**LAYOUT-15. Hold a [manifest] in every [package].**
*Stated by* [one manifest].
*Because* the [manifest] is the file by which a [package]'s top is known, as `Cargo.toml` is a crate's, so every [package] holds the one file that stands for it.
