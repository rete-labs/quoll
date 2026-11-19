+++
prelude = []
+++
**GRAM-1.** *Superseded by* GRAM-30

**GRAM-30. Write the canonical public [manifest] as structured identity, edition, description and dependency [selector]s.**
*Stated by* [manifest], [package id] and [selector].
*Because* every fact a tool reads or edits then has one exact structured representation, while a renderer can derive the [layout.package] title and edition link instead of maintaining a second reading face.
*Because* a Package URL already has an optional version position, so one [selector] carries the canonical identity and requirement without separate identity and version fields, while the final segment supplies the default local name.
*Because* the three canonical pseudo-version forms preserve semantic-version ordering with no base, a prerelease base or a stable release base, using one UTC timestamp and 12 lowercase hexadecimal revision characters across tools; exact [selector]s also admit other prereleases, while generalized major and major.minor partial [selector]s remain stable-only.
*Because* release authority belongs to the release rather than a self-declared [manifest] version, and source locations and resolved content belong to the [lock], so a hosting move or mirror does not rewrite the [layout.package]'s public identity.
*Accepting* the full three-form pseudo-version grammar and exact prerelease admission, with no comparator or range grammar added for partial [selector]s; a structured [manifest] with no Markdown title or [lead], dependency-list uniqueness by unversioned [package id] within one major compatibility series, permitting distinct major series of one [package id], and no inline alias field.
*Rejected* a Markdown [manifest] or front-matter shell, which leaves tool-read facts in presentation markup; a separate [layout.package] name or self-version, which duplicates another authority; a vanity [package id] with no trust domain, which loses global namespacing; a mapping from local names or object entries with separate identity and version, which repeats defaults without adding meaning; [source locator]s in the [manifest], which couple identity to hosting; a public-face list, which duplicates the root [layout.header]s; a membership list, which publishes internal structure and duplicates [modules]; and comparator or range [selector]s, which add grammar before a consumer needs it.

**GRAM-2. Write the [assembly] as [view]s alone.**
*Stated by* [assembly].
*Because* a [layout.assembly] states things, a flow and rules, so one syntax writes every Markdown design file.
*Accepting* [view]s in a [layout.source file] that holds assembly rather than design.
*Revisit* the open [layout.assembly form] at the first derived-target implementation.
*Rejected* headings of its own, which the language would define for one kind of [layout.source file]; and assembly keys in a [front].
*Formerly* the renderer's SYN-2.

**GRAM-3. Open a group of statements once.**
*Stated by* [opener], [view block], [grouped] and [colon].
*Because* it says each [opener] once, where the eye lands first, as a caption does, and keeps one [view block] per [view].
*Because* an [opener] stays a word and a [colon], so the three read as syntax rather than as part of a statement's prose, and nothing is learned but where they stand.
*Because* `ensures` and `requires` are words developers already know, from design by contract.
*Because* an `impl` line shows, in a [layout.body]'s [view block], which [item]s stand under what its [reference] names, with no [view block] or name more for them.
*Because* what an `impl` line's [reference] names rests on more than its [layout.source file]'s text, so the line is an [opener] wherever it is written as one (GRAM-20).
*Because* a missed `:` then costs its own line, the group under it standing as written, where taken as an [item] the line would take the whole group as its statement (GRAM-8).
*Accepting* a level of indentation more in every [view block] of Rules, an [opener] that is no [item], and two [opener] lines over a group that stands under an `impl` line as well as one of the others; and a second shape that is an [opener], always against [colon], so that an [item] named `ensures`, `requires` or `open` cannot stand with its name alone over its statement.
*Revisit* the `impl` line's form as [layout.body]s carrying out several [layout.header]s are written.
*Rejected* each statement opening with its own [opener]'s word, which repeats one word down a [view block]; a heading per [opener], splitting a [view] into several fenced blocks; `ensures:` taken where none is written, which hides what a substitution turns on, whether a rule is kept or relied on; a bare [reference] as an [opener], `[bar]:`, which reads as a link definition; a fenced block for each [layout.header] a [layout.body] carries out, which splits a [view] into several; an `impl` line an [opener] only where its [reference] names what the [layout.body] implements, which the line's text cannot show; a line missing its `:` taken as an [item], or as nothing of the language's, either losing the group under it; the [opener]s' words kept from every name, which takes `open` from writers; plainer words, as `guarantees` and `assumes`, which developers know less well than the words of design by contract.
*Formerly* the renderer's SYN-3.

**GRAM-4. Mark every [reference] with brackets, and nothing else with them.**
*Stated by* [reference], [used] and [no definitions].
*Because* [markdown]'s own forms then mean what they say: a bracketed name is [markdown]'s form of a link waiting for its target, and a code span is code, [literal] text, as engineers already write file names and commands.
*Because* every bracket in Markdown prose is a [reference], so a misspelt one is found, and nothing in [literal] text is ever taken for one.
*Because* brackets delimit a name with spaces, where a sigil would not know where it ends.
*Because* a name that is a verb is used as one, as `[foo]s each`, while the name within the brackets stays as defined, so no [reference] needs English's endings to be resolved.
*Because* a link definition would make [markdown] render each bracketed span of its name as a link.
*Accepting* a [reference] shown as bracketed text wherever [markdown] is rendered as it stands; a form of [markdown] no [layout.source file] may write, as [no definitions] has it; endings read as English and checked by nobody; and unbracketed names in structured values whose own [construct] defines them.
*Rejected* backticks for [reference]s and [literal]s alike, told apart by scope, which lets a misspelt [reference] pass as a [literal]; [literal]s marked by double backticks or a letter, which show as single backticks or a stray letter wherever [markdown] is rendered; a call form, formal punctuation; plurals and possessives alone after the bracket, which bends a sentence around a verb; and the inflected form within the brackets, which asks every resolution for English's endings.
*Formerly* the renderer's SYN-4.

**GRAM-5. Open each [layout.header], [layout.private header] and [layout.body] with a [lead], a whole paragraph however many lines it runs over.**
*Stated by* [lead].
*Because* a [layout.source file]'s opening paragraph is what a reader meets first, in an editor as on a site, and it is [markdown] with [reference]s, as the rest of the [layout.source file] is.
*Because* a [front] keeps to relations, aliases, edition-prelude selection and the module-lead declaration, outside the prose they serve.
*Because* every [layout.body] is then read alike, its [lead] read off its [own text] wherever the [layout.body] stands (GRAM-20).
*Because* a [lead] an editor wraps is still the paragraph the language means.
*Accepting* a paragraph the language places between the [front] and the first [view].
*Rejected* descriptions in a membership file alone, which leaves every [layout.header] undescribed; a description in a [front]; a heading of its own over it; an [item] named as the [layout.source file] it opens, which repeats a name in every [reference] to it; and the [layout.body] at the [layout.package]'s top written with no [lead], which its text alone cannot show.
*Formerly* the renderer's SYN-5 and SYN-17.

**GRAM-6.** *Superseded by* GRAM-31

**GRAM-31. Write every canonical Markdown design file as [view]s over [item] lines within [markdown], with plain ATX headings alone and wholly structured canonical metadata in [toml] instead.**
*Stated by* [markdown], [construct], [section], [view], [view block], [written] and [no empty view].
*Because* a Markdown design file then reads as written wherever that flavour is shown, its tables, task boxes and links among it, and the language's [construct]s stand apart from [markdown]'s own forms, each defined beside it.
*Because* one plain ATX heading form gives prose and [section] boundaries the same syntax, and treating every other form as ordinary text keeps canonical reading within that one grammar.
*Because* the language extends Markdown already, by its [reference]s, and grows by an [item].
*Because* [item]s then read as code does, one level above a programming language, in the fenced block engineers like to read: names in a [column] the eye runs down, a statement starting where the eye lands, with no markup on the line, and a long statement one visual unit.
*Because* headings give the [view block]s what bulk text lacks, a way to navigate, while the [layout.source file] renders in an editor, on a code host and in review tools alike.
*Because* a [view block] is still written by rule, as formal as any list.
*Because* a [layout.header] and a [layout.body] then share one outline, so a reader of one knows where to look in the other.
*Because* a [view] with nothing to hold states nothing, so none is written to keep an outline full.
*Accepting* [column]s kept aligned on every edit, which agents do readily and a formatter can restore; links not clickable within a [view block]; a [view block] shown in monospace on a code host; canonical [markdown] narrower than unrestricted GFM, with a Markdown host allowed to render Setext or another noncanonical ATX form as a heading while Quoll treats the same lines as ordinary text; and pure structured files outside this Markdown form.
*Revisit* the concrete syntax in a dedicated design pass informed by native and document profiles, with canonical Markdown retained meanwhile and no migration scheduled.
*Rejected* CommonMark alone, which reads a table as a paragraph; the complete GFM ATX form, which retains compatibility spellings with no canonical use; the language's [construct]s found line by line over the whole text, which reads a heading or a bracket within a fenced block otherwise than every renderer does; a [markdown] list, a bold name and its statement on each line, which reads as a document's prose where engineers read code; columns of text alone, with no headings to navigate; a programming language's syntax, statements quoted within braces, formal punctuation that reads as code with strings in it; prose within structured data for design [view]s, the least readable of all; a [markdown] shell for wholly structured metadata, which misstates the file's format; an Illustrations [section] beside the [view]s, which nothing used; and an empty [view] written over an empty fenced block.
*Formerly* the renderer's SYN-7.

**GRAM-7. Write no [reference] in [literal] text, and let one run over the lines of an [item] or a paragraph.**
*Stated by* [literal] and [reference].
*Because* backticks mark [literal]s, as the `impl [bar]:` that shows how an [opener] is written, and a diagram's notation, a node in brackets, names nothing in scope; as [reference]s, both would be names nobody wrote.
*Because* a [view block] is fenced but is the language's own, so its brackets stay [reference]s, while another fenced block is another language's text.
*Because* a [reference] an editor wraps over two lines is still one.
*Accepting* that a misspelt [reference] within a code span passes as text.
*Rejected* every bracketed span a [reference], code included, which forbids the language's [layout.source file]s to show their own syntax; an escape, `\[`, for a [literal] bracket, which every writer must remember in prose and code alike.
*Formerly* the renderer's SYN-8.

**GRAM-8. Tell a [view block]'s lines apart by indentation, a group's first line setting where its [item]s start.**
*Stated by* [view block] and [item].
*Because* indentation already says which [item]s a group holds, so it says where the group ends as well: one rule, the one [markdown]'s lists and Python's blocks follow.
*Because* the [item]s outside every group can then stand where they read best, beside the ones they serve.
*Because* one step more indented then has one meaning however wide a writer makes the step, and a [view block] whose names stand alone over their statements reads as written.
*Because* a tab has no [width] the language fixes, so a line opening with one has no indentation to compare.
*Accepting* an [item]'s group resting on its indentation alone.
*Rejected* a group ending only at the next [opener] line or at the [view block]'s end, which pushes the [item]s outside every group before the first; an [opener] for those [item]s, a word which needs none, as one of the others; a blank line ending a group, a meaning a reader cannot see in a long [view]; and a step fixed at two spaces, which turns a group indented by four into lines part of no [construct].
*Formerly* the renderer's SYN-9.

**GRAM-9.** *Superseded by* GRAM-32

**GRAM-32. Write every canonical Quoll-owned structured file and [front] in [toml], declaring explicit renames in `aliases` and prefix-grouped path stripping in `use`.**
*Stated by* [toml], [front], [workspace manifest], [modules] and [canonical toml].
*Because* explicit scalar types and a simple table model give tools an exact edit boundary without implicit conversions, anchors or a custom configuration language, while short [manifest]s and aliases remain comfortable to read and write.
*Because* one structured syntax serves pure [manifest]s, membership, [lock]s and [front] matter, and `+++` keeps that [front] matter distinct from the Markdown it precedes.
*Because* a [workspace manifest] names an edition for the [layout.workspace]'s own files while member [manifest]s name their own, giving [layout.workspace decisions] deterministic grammar and history without making a member's meaning depend on its originating [layout.workspace].
*Because* one `aliases` mapping handles explicit PURL and qualified-name renames where [reference]s are used, with Package URL versus qualified-[reference] syntax telling the target kinds apart; an unversioned target follows ordinary version updates, while a [selector] target distinguishes simultaneously visible versions.
*Because* a quoted `use` key states a complete abstract prefix once and its TOML string array states exactly the desired relative continuations, retaining each continuation's final segment as its local name without wildcard or brace-expansion syntax.
*Because* a [layout.decisions] or [layout.workspace decisions] uses the same [reference]s, so its [front] admits the same `prelude`, `aliases` and `use` forms and no implementation, inclusion or module-lead declaration.
*Because* the boolean `"module lead" = true` marks the owning [layout.header] where no [layout.body] or default [layout.header] supplies the [lead], without making that [layout.header] a default or moving its [lead] into membership metadata.
*Accepting* a TOML parser dependency, arrays of tables in generated [lock]s, explicit quoting, two target grammars in the rename table, quoted prefix keys and relative-continuation validation in grouped declarations, alias-only fronts apart from edition selection in [layout.decisions] and [layout.workspace decisions], qualified-name targets within the declaring file's sight including same-package internal [model.kernel.item]s, whose resolution and public exposure remain the source join's to check, and one front-matter boolean whose cardinality is the source join's to check.
*Rejected* YAML, whose broader grammar and implicit typing need restriction and careful canonicalization; JSON, whose hand-facing forms are more verbose and comment-free; splitting TOML and JSON by file kind, which doubles parsers and serializers; comment-enabled JSON variants, whose implementations vary; separate PURL and qualified-name rename mappings, which add structure without expressive power; a flat `use` string array, which repeats each shared prefix; brace groups inside reference strings, which add an expansion parser and escaping diagnostics; package-global aliases, which turn a local [reference] convenience into global naming policy; and descriptions in [modules], which duplicate the owning [lead]s and drift.
*Formerly* the renderer's SYN-15 and SYN-27.

**GRAM-10. Write an active [layout.decisions] [entry] with its `*Stated by*` first, naming [item]s alone, an active [layout.workspace decisions] [entry] with its rationale directly and no `*Stated by*`, and a superseded [entry] as one titleless line holding only its ID and successor pointer.**
*Stated by* [entry] and [stated].
*Because* an active [layout.decisions] [entry] then [reference]s the [item]s that state it, so that a reader finds where it is stated.
*Because* the [workspace manifest] holds no [item]s, so an active [layout.workspace decisions] [entry] carries its workspace-level rationale directly rather than naming a member [layout.package]'s [item] as its own statement.
*Because* a line under a word, `*Taken by*` among them, is found by its opening, whatever lines an active [entry] holds.
*Because* a superseded [entry] states no current [item]s or choice, so its ID and `*Superseded by*` pointer stand alone on one titleless line.
*Accepting* a line under a word wrapped over two lines, its second taken as what was decided.
*Rejected* requiring `*Stated by*` of a [layout.workspace decisions] [entry], which gives workspace-level membership and coordinated-publication rationale no valid stating [item] of its own.
*Formerly* the renderer's SYN-16, in part.

**GRAM-12.** *Superseded by* GRAM-33

**GRAM-33. Write every example with made-up names, allowing domains reserved for examples.**
*Stated by* [examples].
*Because* a made-up name reads as one wherever programming is written, so an example is never taken for a [reference] to something real, and none goes stale when the [layout.package] renames what it would have shown.
*Because* [literal] text holds no [reference] (GRAM-7), so a real name within it escapes every resolution of [reference]s, while a made-up one stays an example wherever it stands.
*Accepting* a set of made-up names rather than four fixed names, and reserved example domains such as `acme.example` where an example needs a domain.
*Rejected* real names in examples, which go stale unseen when what they name is renamed; names the language reserves, except domains reserved for examples, which would take names from every [layout.package]; and a real [reference] in place of an example, which shows it as its link, never as it is written.

**GRAM-13. Keep a [view block]'s lines within 100 [column]s.**
*Stated by* [width].
*Because* 100 is the line length common formatters and widely followed style guides keep, so a [view block] reads as the code its readers write.
*Because* a [view block]'s writer wraps each statement at its [column], which no editor's soft wrap keeps, so a [view block] needs a [width] of its own.
*Accepting* [view block]s wrapped at two [width]s, until each is next rewritten.
*Revisit* when the language lets a [layout.package] set its own [width], as a formatter's line length is a repository's own setting.
*Rejected* 92, one [column] more than the widest line in the language's first sketch, a number with no reason; 80, which would rewrap nearly every [view block]; and no limit, under which a long line wraps to the margin in an editor and scrolls sideways on a page.

**GRAM-14. Start a [view block]'s statements in one [column], and take a [construct] written against a writer's rule as the [construct] it reads as.**
*Stated by* [column] and [slips].
*Because* a breach of a rule [slips] names is a slip in what its writer wrote, where a line part of no [construct] says nothing this part states.
*Because* one [column] lets a reader run down a [view block]'s names and its statements apart.
*Rejected* the [column] as part of what makes an [item], which turns a statement one space off into lines part of no [construct].

**GRAM-15. Head a [section] as the language names it, once, and let every [entry] stand under any heading of an [entry] file.**
*Stated by* [section] and [written].
*Because* the [view] kept is the first, which nothing after it changes, and a second would split one [view]'s [item]s over two fenced blocks.
*Because* a [view]'s [section] then holds its [view block] alone, so no prose, table or second fenced block beside it states what its [item]s do not.
*Because* a heading in an [entry] file then costs its own line, and leaves every [entry] and [reference] under it as written.
*Accepting* a line part of no [construct] for each heading a writer groups [entry]s under.
*Revisit* when a [layout.package]'s [layout.decisions] need grouping.
*Rejected* every line under such a heading part of no [construct], which loses a whole [entry] file's [entry]s to one heading; and a heading grouping [entry]s as a [construct] of its own, which no [entry] file needs, its [entry]s standing in the order taken.
*Formerly* the renderer's SYN-23.

**GRAM-16. Mark an [item] or an [entry] with free [label]s at the end of its last line, each word running to the next space.**
*Stated by* [label].
*Because* it is what code already gives people, as a task marker in a comment or a [label] on an issue: a free word costs nothing to learn, and one search finds every [item] it marks.
*Because* a [label] at the end of what it marks is found in the [layout.source file], where engineers read, while a `#` within a sentence stays the text it is.
*Because* a [label] is then the word its writer wrote, as `#foo-bar` is, whatever its characters.
*Accepting* that free [label]s drift into a vocabulary of their own, which a team may settle by convention.
*Rejected* none in the [layout.source file]s, marks on a rendered page alone, while engineers read files; [label]s listed in a [manifest], a mark away from what it marks; any `#` word a [label], wherever it stands, which turns a number in a sentence into one; and a word of letters alone, which cuts `#foo-bar` short.
*Formerly* the renderer's SYN-25, in part.

**GRAM-17. Write an ID as a mnemonic of ASCII letters, digits and hyphens, a hyphen and ASCII digits, and take a bare one of its [entry] file's own mnemonic as a [reference] where nothing joins it to what stands beside it.**
*Stated by* [entry] and [reference].
*Because* an [entry] citing another of its [entry] file is then checked to cite one that exists, a misspelt ID being a [reference] that lands on nothing rather than text.
*Because* an ID is distinct enough to need no brackets, its [entry] file's own mnemonic telling it from text of its shape, as `UTF-8`.
*Because* an ID then holds no space, full stop or asterisk, so where it ends in an [entry]'s first line is never in doubt, and a mnemonic with a segment of its own is still an ID.
*Because* an ID whose number opens a longer one, or which ends or opens a longer ID, is never taken out of it, while one followed by `'s` or a full stop still is a [reference].
*Accepting* that another [entry] file's ID, cited in an [entry], stays text.
*Rejected* IDs as plain text, under which a citation of one that does not exist goes unseen; IDs in brackets, spending them where no name in scope is meant; a mnemonic of capital letters alone, which is narrower than what writers write; and any match of an ID's characters, which takes one out of a longer ID.
*Formerly* the renderer's SYN-16 in part, SYN-26 and SYN-28.

**GRAM-19. Name the language's [construct]s as one family, [construct], below its members.**
*Stated by* [construct].
*Because* this part uses the word itself, so it defines it, its members listed beside their own [item]s and kept in step as one is added.
*Because* a family is then an [item] like any other, a thing that is one of several, as an enum is in a programming language, so the language needs nothing new for it.
*Because* [written] then makes a line outside every member a fault.
*Rejected* the word left plain, read by inference; a name for the family declared in the [front] of each [layout.source file] using it, which leaves it undefined for whoever reads that [layout.source file]'s [layout.header]; the family defined by whatever reads the [construct]s as its own [item] stating it is one of this part's, a second list kept in step by hand; and the members spelt out wherever the family is meant.

**GRAM-20. Read every [construct] off one [layout.source file]'s [own text], apart from what it means; let only a rule for writers rest on the [layout.package].**
*Stated by* [own text].
*Because* whoever writes a [layout.source file], person or agent, relies on how it is written, so it is stated where writers read it, apart from what a [layout.source file] means, which is another thing, read from many [layout.source file]s at once.
*Because* a [layout.source file]'s form then rests on its text alone, so any tool reads one [layout.source file] by it, and a fault of meaning is found as what it is rather than as a line malformed.
*Because* a rule for writers asks what a writer, who sees the [layout.package], can keep, while what a [layout.source file] holds stays readable without it.
*Because* whatever reads for meaning then uses this part and is never used by it, so the two are stated in order.
*Rejected* how a [layout.source file] is written left to whatever reads it, hidden from those who write; form and meaning in one [layout.header], which whoever needs either must take whole; and a [construct] resting on more than one [layout.source file]'s text, as whether a [layout.body] stands at the [layout.package]'s top, which one [layout.source file]'s text cannot show.

**GRAM-22. Open each [item] with its name and each [entry] with its ID, the IDs of one [entry] file sharing a mnemonic no other uses.**
*Stated by* [item], [entry] and [unique].
*Because* a bare ID is then read within its own [entry] file alone, its mnemonic showing which that is (GRAM-17).
*Formerly* the renderer's SYN-16, in part.

**GRAM-25.** *Superseded by* GRAM-37

**GRAM-37.** *Superseded by* GRAM-38

**GRAM-38. Write every use of a name in scope as a [reference], with the optional `prelude` of each [layout.source file] in a [model.graph.package] or [model.graph.workspace] selecting its own edition's fixed bindings.**
*Stated by* [reference], [front], [used] and [stated].
*Because* one visibly bracketed spelling then serves every intended reference to a model [model.kernel.item], while the same words in another sense remain ordinary English and no separate lexical family or inflection rules acquire hidden model meaning.
*Because* one optional list-valued key expresses the edition selection in the file where its [reference]s stand, without a second package-level reading input or inheritance chain; grammar recognizes its form but holds no model targets or fixed name list.
*Because* package and [layout.workspace decisions] use the same per-file selection and fixed bindings, removing the former special workspace exception; a [model.graph.workspace] names an edition for its own files and no member [model.graph.package] inherits it.
*Accepting* heavier punctuation in prose, per-file default, disabled and selective declarations in package and [layout.workspace files] alike, removal of the core-word construct and its special capitalization and inflection handling, and no canonical syntax imposed on native representations.
*Rejected* the six bare core words, which give ordinary English hidden model meaning; retaining bare and bracketed canonical spellings together, which preserves a lasting style split; a broader extensible lexical vocabulary, which expands the special namespace before concrete consumers justify it; grammar-owned model targets, which collapse own-text reading into semantic resolution; the former no-edition, no-prelude workspace exception, which leaves durable workspace notation without an explicit authority and preserves a second rule; using a workspace edition as a member default, which violates package self-containment; and reinterpreting an existing edition's spelling in place, which makes already written source nondeterministic.

**GRAM-26. Keep how [layout.tests] are written open until a [layout.package] has some.**
*Stated by* [tests].
*Because* no [layout.package] yet has [layout.tests].
*Rejected* their form designed now; and their form left out of the definition.

**GRAM-28. Give each [item] of a [layout.source file] a name of its own, but under `impl` lines of a [layout.body] whose [reference]s differ.**
*Stated by* [one name].
*Because* a name standing alone then names one [item] of its [layout.source file], wherever it is written there.
*Because* a [layout.body] carrying out two [layout.header]s that each hold an [item] of one name holds an [item] for each, each written bare under its own `impl` line; whether two differing [reference]s name different things is the meaning's (GRAM-20).
*Accepting* that two [item]s of one [layout.body] may share a name, told apart by the `impl` line each stands under.
*Rejected* two [item]s of one name under `impl` lines with the same [reference], as in two [view]s, which would make two [item]s carry out one.

**GRAM-29. Write the canonical root's full direct-and-transitive resolution as exact [lock] entries, with [layout.content hash]es, canonical [release tag]s and one or more resolved Git sources written by [source locator]s.**
*Stated by* [lock], [release tag] and [source locator].
*Because* the exact selected [selector], full commit and [layout.package] hash fix what the root checked, while the [source locator] and matched tag or requested committish explain how to find the same source again.
*Because* the last `@` parts location from request, and the explicit `.git` repository boundary or either GitHub owner-and-repository shorthand, host-qualified or hostless, makes the following [layout.package] path unambiguous; the examples show the same nested [layout.package] path at a branch and at a release, the hostless form equivalent to the host-qualified one.
*Because* a [release tag] gives the selected stable or prerelease semantic version one canonical spelling, alone at the repository root or prefixed by the below-root [layout.package] path; release and development entries share one shape apart from this release-only tag, and mirrors can differ in [source locator] and commit without changing the expected [layout.package] hash.
*Because* `1220` followed by 64 lowercase hexadecimal digits writes the SHA-256 multihash's algorithm and length around the outer dirhash digest, not a replacement for the specified summary serialization.
*Accepting* verbose arrays of tables, transitive entries repeated across independent root [lock]s, and no [lock] entry for a workspace-local working tree substituted at head.
*Rejected* direct entries alone recursively governed by dependency [lock]s, which prevents consumer-level reconciliation; partial [selector]s in a [lock], which leaves the selected graph unfixed; a hash in the public [manifest], which mixes resolution into declaration; machine-specific [layout.workspace] [layout.path]s in a [lock]; an unmarked repository boundary or general host probing, which makes the [layout.package] path uncertain; an untyped tag string, which admits inconsistent or non-release values; [literal] as the tag's type, which confuses Markdown text with structured tag syntax; and a tag on a development source, which has no matched [release tag] to record.

**GRAM-34. Leave native and cross-profile declarations, [native overlay]s and structured [native link]s open.**
*Stated by* [native form], [native overlay] and [native link].
*Because* native ecosystems retain their own requirement grammars and resolvers, while canonical [manifest], [selector] and [lock] forms supply no native or mixed concrete carrier before a profile needs one.
*Because* what structured native comments or annotations carry and mean belongs with the semantic joins that define them, so their concrete tokens and placement stay open here without transferring those meanings into grammar.
*Accepting* profile-specific concrete carriers, with no common native comment token, overlay schema or mixed-record syntax stated before their owning semantic joins settle one.
*Revisit* these open forms when their owning semantic joins settle their concrete carriers and meanings.
*Rejected* stretching canonical [package id], [selector], [manifest], [source locator] or [lock] grammars into native rules; one mandatory comment token across native languages; per-profile changes to what structured [native link]s mean; and concrete native or mixed forms without a profile consumer.

**GRAM-35. Leave the common [target map]'s concrete grammar open until the first derived-target implementation.**
*Stated by* [target map].
*Because* actual realization has one common record across profiles, while neither its concrete fields nor native locators have a consumer before that implementation.
*Accepting* one shared form whose concrete grammar waits for the first derived-target implementation.
*Revisit* the open form at the first derived-target implementation.
*Rejected* per-profile [target map] grammars; treating [assembly] as the realization record; and designing native locator schemas in canonical grammar.

**GRAM-36. Declare exposed names and paths in an `exposes` table in an existing [layout.header] or [layout.private header].**
*Stated by* [front].
*Because* an exposure belongs to the existing [model.kernel.module] whose sight covers its target, so its declaration needs no additional [layout.source file] or duplicated contract.
*Because* one TOML mapping gives each exposed name or dotted path one exact target spelling, using the existing [reference] form and quoted dotted keys rather than another path grammar.
*Accepting* intermediate declarations in [layout.private header]s and several paths for one target; an exposure creating no [model.kernel.module], [model.kernel.interface] or [model.kernel.item]; no `exposes` key in a [layout.body], [layout.decisions] or [layout.workspace decisions]; the existing `includes`, `implements`, `prelude`, `use`, `aliases` and module-lead forms keeping their own contexts, with `includes` neither renamed nor made an exposure declaration; and target resolution, path uniqueness, sibling-name uniqueness and root reachability remaining outside this grammar.
*Rejected* one facade [layout.header] per exposure, which creates a second contract and competes with a same-named [model.kernel.module]; and a central [model.graph.package] exposure manifest, which separates an exposure from the [model.kernel.module] sight that authorizes it.
