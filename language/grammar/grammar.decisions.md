**GRAM-1. Write the [manifest] as a title, a line, a [lead] and a [view block].**
*Stated by* [manifest] and [dependencies].
*Because* it reads as a repository's top file reads anywhere, a title, the language, a paragraph and a list of what it holds, and its link opens the language's definition in one click.
*Because* the [view block] then holds [layout.path]s alone, so the tree reads straight off it, while what stands at the [layout.package]'s top, whose [layout.path] is empty, is said once, in the [lead].
*Because* a name and a version make a [layout.package]'s identity, and a dependency is the design's: a [reference] spells it by the name the [layout.package] gives it, so declared in the [layout.build] it would make the design rest on the assembly.
*Accepting* a heading the language must define, `## Modules`, and fixed rules for the version and the edition.
*Revisit* if the language comes to need tooling that reads [layout.package]s mechanically, such as a public registry of them, since [markdown] is then probably not the best way to write it; and the dependencies' form, when a [layout.package] first has some.
*Rejected* the top in the [view block], under `.` or under the [layout.package]'s name, a line whose name is no [layout.path], or a [layout.manifest] with no title; a [front] for the facts, YAML and a [layout.path] no editor opens in a click; one [view block] for everything, making `for` and `hides` the language's words; the version and the dependencies in the [layout.build], the design resting on the assembly.
*Formerly* the renderer's SYN-1.

**GRAM-2. Write the [build] as [view]s alone.**
*Stated by* [build].
*Because* a [layout.build] states things, a flow and rules, so one syntax writes every [layout.source file].
*Accepting* [view]s in a [layout.source file] that holds assembly rather than design.
*Revisit* when the build process is worked on.
*Rejected* headings of its own, which the language would define for one kind of [layout.source file]; Cargo's keys in a [front], YAML alone.
*Formerly* the renderer's SYN-2.

**GRAM-3. Open a group of statements once.**
*Stated by* [opener], [view block], [grouped] and [colon].
*Because* it says each [opener] once, where the eye lands first, as a caption does, and keeps one [view block] per [view].
*Because* an [opener] stays a word and a colon, so the three read as syntax rather than as part of a statement's prose, and nothing is learned but where they stand.
*Because* `ensures` and `requires` are words developers already know, from design by contract; what readers missed was where they are defined, which the [manifest]'s link now gives.
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
*Because* every bracket is a [reference], so a misspelt one is found, and nothing in [literal] text is ever taken for one.
*Because* brackets delimit a name with spaces, where a sigil would not know where it ends.
*Because* a name that is a verb is used as one, as `[foo]s each`, while the name within the brackets stays as defined, so no [reference] needs English's endings to be resolved.
*Because* a link definition would make [markdown] render each bracketed span of its name as a link.
*Accepting* a [reference] shown as bracketed text wherever [markdown] is rendered as it stands; a form of [markdown] no [layout.source file] may write, as [no definitions] has it; and endings read as English and checked by nobody.
*Rejected* backticks for [reference]s and [literal]s alike, told apart by scope, which lets a misspelt [reference] pass as a [literal]; backticks for [reference]s with [literal]s plain, which takes code's look from file names and commands; [literal]s marked by double backticks or a letter, which show as single backticks or a stray letter wherever [markdown] is rendered; a call form, formal punctuation; plurals and possessives alone after the bracket, which bends a sentence around a verb; the inflected form within the brackets, which asks every resolution for English's endings.
*Formerly* the renderer's SYN-4.

**GRAM-5. Open each [layout.header], [layout.private header] and [layout.body] with a [lead], a whole paragraph however many lines it runs over.**
*Stated by* [lead].
*Because* a [layout.source file]'s opening paragraph is what a reader meets first, in an editor as on a site, and it is [markdown] with [reference]s, as the rest of the [layout.source file] is.
*Because* a [front] keeps to relations, and a YAML value opening with a bracket would be read as a list.
*Because* every [layout.body] is then read alike, its [lead] read off its own text wherever the [layout.body] stands (GRAM-20).
*Because* a [lead] an editor wraps is still the paragraph the language means.
*Accepting* a paragraph the language places between the [front] and the first [view].
*Rejected* descriptions in the [layout.manifest] alone, which leaves every [layout.header] undescribed; a description in a [front]; a heading of its own over it; an [item] named as the [layout.source file] it opens, which repeats a name in every [reference] to it; the [layout.body] at the [layout.package]'s top written with no [lead], which its text alone cannot show.
*Formerly* the renderer's SYN-5 and SYN-17.

**GRAM-6. Write every [layout.source file] in [markdown], but its [front], each [view] a [section] over one [view block] of [item] lines.**
*Stated by* [markdown], [construct], [section], [view], [view block], [written] and [no empty view].
*Because* a [layout.source file] then reads as written wherever that flavour is shown, its tables, task boxes and links among it, and the language's [construct]s stand apart from [markdown]'s own forms, each defined beside it.
*Because* the language extends Markdown already, by its [reference]s, and grows by an [item].
*Because* [item]s then read as code does, one level above a programming language, in the fenced block engineers like to read: names in a column the eye runs down, a statement starting where the eye lands, with no markup on the line, and a long statement one visual unit.
*Because* headings give the [view block]s what bulk text lacks, a way to navigate, while the [layout.source file] renders in an editor, on a code host and in review tools alike.
*Because* a [view block] is still written by rule, as formal as any list.
*Because* a [layout.header] and a [layout.body] then share one outline, so a reader of one knows where to look in the other.
*Because* a [view] with nothing to hold states nothing, so none is written to keep an outline full.
*Because* illustrations were never used, and what they would show, diagrams and tables, a renderer shows, so a [section] or lines for them would hold nothing a [view] does not.
*Accepting* columns kept aligned on every edit, which agents do readily and a formatter can restore; links not clickable within a [view block]; and a [view block] shown in monospace on a code host.
*Revisit* when the language takes a format of its own, as it likely will by its v1.0; and for tooling of the [view block]s, highlighting, drawings in text and editor support with tooltips and links, never braces or other formal punctuation.
*Rejected* CommonMark alone, which reads a table as a paragraph; the language's [construct]s found line by line over the whole text, which reads a heading or a bracket within a fenced block otherwise than every renderer does; a [markdown] list, a bold name and its statement on each line, which reads as a document's prose where engineers read code; columns of text alone, with no headings to navigate; a programming language's syntax, statements quoted within braces, formal punctuation that reads as code with strings in it; YAML or TOML, prose within structured data, the least readable of all; an Illustrations [section] beside the [view]s, which nothing used; an empty [view] written over an empty fenced block, a heading that states nothing.
*Formerly* the renderer's SYN-7.

**GRAM-7. Write no [reference] in [literal] text, and let one run over the lines of an [item] or a paragraph.**
*Stated by* [literal] and [reference].
*Because* backticks mark [literal]s, as the `impl [bar]:` that shows how an [opener] is written, and a diagram's notation, a node in brackets, names nothing in scope; as [reference]s, both would be names nobody wrote.
*Because* a [view block] is fenced but is the language's own, so its brackets stay [reference]s, while another fenced block is another language's text.
*Because* a [reference] an editor wraps over two lines is still one.
*Accepting* that a misspelt [reference] within a code span passes as text.
*Rejected* every bracketed span a [reference], code included, which forbids the language's [layout.source file]s to show their own syntax; an escape, `\[`, for a literal bracket, which every writer must remember in prose and code alike.
*Formerly* the renderer's SYN-8.

**GRAM-8. Tell a [view block]'s lines apart by indentation, a group's first line setting where its [item]s start.**
*Stated by* [view block] and [item].
*Because* indentation already says which [item]s a group holds, so it says where the group ends as well: one rule, the one [markdown]'s lists and Python's blocks follow.
*Because* the [item]s outside every group can then stand where they read best, beside the ones they serve.
*Because* one step more indented then has one meaning however wide a writer makes the step, and a [view block] whose names stand alone over their statements reads as written.
*Because* a tab has no width the language fixes, so a line opening with one has no indentation to compare.
*Accepting* that an [item]'s group rests on its indentation alone.
*Rejected* a group ending only at the next [opener] line or the [view block]'s end, which pushes the [item]s outside every group before the first; an [opener] for those [item]s, a word for what needs none, which would read as one of the others; a blank line ending a group, a meaning a reader cannot see in a long [view]; a step fixed at two spaces, which turns a group indented by four into lines part of no [construct].
*Formerly* the renderer's SYN-9.

**GRAM-9. Write a [front] as a YAML mapping outside the [markdown] text, its keys the language's and its names as YAML reads them.**
*Stated by* [front] and [used].
*Because* a [front] then holds relations alone, every other fact of a [layout.source file] standing in its text.
*Because* it is then written as front matter elsewhere is, a YAML mapping, so that the next key the language needs is added by naming it.
*Because* any list YAML writes is then read as YAML reads it, so that an editor or a formatter of YAML may write it in any form.
*Because* the [markdown] specification has no front matter: read as [markdown], its opening `---` would be a thematic break and its closing one a heading over the line above it, and a YAML list, `[foo, bar]`, or a comment after a `#`, would read as a [reference] or a [label].
*Because* a name some YAML reads as a boolean or a number, as `on` or `no`, is then the name its writer wrote, and a name quoted or not is the same name.
*Because* a name in a [front] is then spelt as it is wherever else it is written, so it is learned once; what it names is the meaning's (GRAM-20).
*Revisit* when the language takes a format of its own (GRAM-6), which will likely change how a [layout.source file] states its relations; v0.x starts fast with YAML.
*Rejected* one key alone, which a second key would rewrite; a name as its scalar is written, which hands a quoted name over with its quotes; a name as YAML types it, which loses such a name.
*Formerly* the renderer's SYN-15 and SYN-27.

**GRAM-10. Write an [entry] as a paragraph, a line to each word, its `*Stated by*` first, naming [item]s alone.**
*Stated by* [entry] and [stated].
*Because* an [entry] then references the [item]s that state it, so that a reader finds where it is stated.
*Because* a line under a word, `*Taken by*` among them, is found by its opening, whatever lines an [entry] holds.
*Accepting* a line under a word wrapped over two lines, its second taken as what was decided.
*Formerly* the renderer's SYN-16, in part.

**GRAM-12. Write every example with made-up names.**
*Stated by* [examples].
*Because* a made-up name reads as one wherever programming is written, so an example is never taken for a [reference] to something real, and none goes stale when the [layout.package] renames what it would have shown.
*Because* [literal] text holds no [reference] (GRAM-7), so a real name within it escapes every resolution of [reference]s, while a made-up one stays an example wherever it stands.
*Accepting* four names every example takes.
*Rejected* real names in examples, which go stale unseen when what they name is renamed; names the language reserves, as RFC 2606 reserves `.example`, which would take four names from every [layout.package], `bar` an English word among them; a real [reference] in place of an example, which shows it as its link, never as it is written.

**GRAM-13. Keep a [view block]'s lines within 100 columns.**
*Stated by* [width].
*Because* 100 is the line length rustfmt keeps by default, as do the most widely followed Java and Kotlin style guides, so a [view block] reads as the code its readers write.
*Because* a [view block]'s writer wraps each statement at its column, which no editor's soft wrap keeps, so a [view block] needs a width of its own.
*Accepting* [view block]s wrapped at two widths, until each is next rewritten.
*Revisit* when the language lets a [layout.package] set its own width, as a formatter's line length is a repository's own setting.
*Rejected* 92, one column more than the widest line in the language's first sketch, a number with no reason; 80, which would rewrap nearly every [view block]; no limit, under which a long line wraps to the margin in an editor and scrolls sideways on a page.

**GRAM-14. Start a [view block]'s statements in one column, and take a [construct] written against a writer's rule as the [construct] it reads as.**
*Stated by* [column] and [slips].
*Because* a breach of a rule [slips] names is a slip in what its writer wrote, where a line part of no [construct] says nothing [grammar] states.
*Because* one column lets a reader run down a [view block]'s names and its statements apart.
*Rejected* the column as part of what makes an [item], which turns a statement one space off into lines part of no [construct].

**GRAM-15. Head a [section] as the language names it, once, and let every [entry] stand under any heading of a [layout.decisions].**
*Stated by* [section] and [written].
*Because* the [view] kept is the first, which nothing after it changes, and a second would split one [view]'s [item]s over two fenced blocks.
*Because* a [view]'s [section] then holds its [view block] alone, so no prose, table or second fenced block beside it states what its [item]s do not.
*Because* a heading in a [layout.decisions] then costs its own line, and leaves every [entry] and [reference] under it as written.
*Accepting* a line part of no [construct] for each heading a writer groups [entry]s under.
*Revisit* when a [layout.package]'s [layout.decisions] need grouping.
*Rejected* every line under such a heading part of no [construct], which loses a whole [layout.decisions]' [entry]s to one heading; a heading grouping [entry]s as a [construct] of its own, which no [layout.decisions] needs, its [entry]s standing in the order taken.
*Formerly* the renderer's SYN-23.

**GRAM-16. Mark an [item] or an [entry] with free [label]s at the end of its last line, each word running to the next space.**
*Stated by* [label].
*Because* it is what code already gives people, as `TODO` in a comment or a label on an issue: a free word costs nothing to learn, and one search finds every [item] it marks.
*Because* a [label] at the end of what it marks is found in the [layout.source file], where engineers read, while a `#` within a sentence, as an issue's number, stays the text it is.
*Because* a [label] is then the word its writer wrote, as `#foo-bar` is, whatever its characters.
*Accepting* that free [label]s drift into a vocabulary of their own, which a team may settle by convention.
*Rejected* none in the [layout.source file]s, marks on a rendered page alone, while engineers read files; [label]s listed in the [layout.manifest], a mark away from what it marks; any `#` word a [label], wherever it stands, which turns a number in a sentence into one; a word of letters alone, which cuts `#foo-bar` short.
*Formerly* the renderer's SYN-25, in part.

**GRAM-17. Write an ID as a mnemonic of ASCII letters, digits and hyphens, a hyphen and ASCII digits, and take a bare one of its [layout.decisions]' own mnemonic as a [reference] where nothing joins it to what stands beside it.**
*Stated by* [entry] and [reference].
*Because* an [entry] citing another of its [layout.decisions] is then checked to cite one that exists, a misspelt ID being a [reference] that lands on nothing rather than text.
*Because* an ID is distinct enough to need no brackets, its [layout.decisions]' own mnemonic telling it from text of its shape, as `UTF-8`.
*Because* an ID then holds no space, full stop or asterisk, so where it ends in an [entry]'s first line is never in doubt, and a mnemonic with a segment of its own, as a milestone's in `FOO-B2-12`, is still an ID.
*Because* an ID whose number opens a longer one, as `FOO-2` opens `FOO-20`, or which ends or opens a longer ID, as in `BAR-FOO-2` or `FOO-2-3`, is never taken out of it, while one followed by `'s` or a full stop still is a [reference].
*Accepting* that another [layout.decisions]' ID, cited in an [entry], stays text.
*Rejected* IDs as plain text, under which a citation of one that does not exist goes unseen; IDs in brackets, spending them where no name in scope is meant; a mnemonic of capital letters alone, which is narrower than what writers write; any match of an ID's characters, which takes one out of a longer ID.
*Formerly* the renderer's SYN-16 in part, SYN-26 and SYN-28.

**GRAM-19. Name the language's [construct]s as one family, [construct], below its members.**
*Stated by* [construct].
*Because* [grammar] uses the word itself, so it defines it, its members listed beside their own [item]s and kept in step as one is added.
*Because* a family is then an [item] like any other, a thing that is one of several, as an enum is in a programming language, so the language needs nothing new for it.
*Because* [written] then makes a line outside every member a fault.
*Rejected* the word left plain, read by inference; a name for the family declared in the [front] of each [layout.source file] using it, which leaves it undefined for whoever reads that [layout.source file]'s [layout.header]; the family defined by whatever reads the [construct]s, as its own [item] stating it is one of [grammar]'s, a second list kept in step by hand; the members spelt out wherever the family is meant.

**GRAM-20. Read every [construct] off one [layout.source file]'s own text, apart from what it means; let only a rule for writers rest on the [layout.package].**
*Stated by* [own text].
*Because* whoever writes a [layout.source file], person or agent, relies on how it is written, so it is stated where writers read it, apart from what a [layout.source file] means, which is another thing, read from many [layout.source file]s at once.
*Because* a [layout.source file]'s form then rests on its text alone, so any tool reads one [layout.source file] by it, and a fault of meaning is found as what it is rather than as a line malformed.
*Because* a rule for writers asks what a writer, who sees the [layout.package], can keep, while what a [layout.source file] holds stays readable without it.
*Because* whatever reads for meaning then uses [grammar] and is never used by it, so the two are stated in order.
*Rejected* how a [layout.source file] is written left to whatever reads it, hidden from those who write; form and meaning in one [layout.header], which whoever needs either must take whole; a [construct] resting on more than one [layout.source file]'s text, as whether a [layout.body] stands at the [layout.package]'s top, which one [layout.source file]'s text cannot show.

**GRAM-22. Open each [item] with its name and each [entry] with its ID, the IDs of one [layout.decisions] sharing a mnemonic no other uses.**
*Stated by* [item], [entry] and [unique].
*Because* a bare ID is then read within its own [layout.decisions] alone, its mnemonic showing which that is (GRAM-17).
*Formerly* the renderer's SYN-16, in part.

**GRAM-25. Write the language's [core word]s bare, as words of text.**
*Stated by* [core word] and [own terms].
*Because* every [layout.package] speaks of what it is made of in the language's terms, and these six are the types every [layout.source file] of every [layout.package] speaks of, the list a newcomer learns first.
*Because* a keyword is written bare in every language engineers read, while brackets around words every [layout.source file] uses would mark nearly every sentence.
*Because* a word of text that reserves no name takes nothing from writers: a [layout.package]'s own `package` stays its own, written as a [reference].
*Because* an [item]'s defining name, a heading the language names, a [label] and a link's destination each mark a [construct] or a target rather than speak of the language's terms.
*Because* in the language's own [layout.package] the terms are its own [item]s, which is why [own terms] holds there; what a [core word] names elsewhere, and at which edition, is the meaning's (GRAM-20).
*Accepting* six words that, written bare in any [layout.package], are the language's terms rather than plain English; and a list [grammar] keeps in step with the definition's terms by hand, as a language's keywords are listed in its lexical grammar.
*Revisit* the list as the definition's terms settle.
*Rejected* the words plain, defined nowhere a reader of the [layout.source file] looks; three words alone, `package`, `module` and `interface`, leaving out types every [layout.source file] speaks of; every term the definition defines, a list [grammar] could keep only as text in step with another's by hand; a [core word] reserving its name, which takes from every [layout.package] a name it may want; any letters after a listed word an inflection, which makes `projection` and `packaging` [core word]s; a [core word] wherever its word stands bare, which makes an [item]'s defining name and a named heading one, and the language's own [layout.package] bracket its own `Modules`.

**GRAM-26. Keep how [layout.tests] are written open until a [layout.package] has some.**
*Stated by* [tests].
*Because* no [layout.package] yet has [layout.tests].
*Rejected* their form designed now; their form left out of the definition.

**GRAM-28. Give each [item] of a [layout.source file] a name of its own, but under `impl` lines of a [layout.body] whose [reference]s differ.**
*Stated by* [one name].
*Because* a name standing alone then names one [item] of its [layout.source file], wherever it is written there.
*Because* a [layout.body] carrying out two [layout.header]s that each hold an [item] of one name holds an [item] for each, each written bare under its own `impl` line; whether two differing [reference]s name different things is the meaning's (GRAM-20).
*Accepting* that two [item]s of one [layout.body] may share a name, told apart by the `impl` line each stands under.
*Rejected* two [item]s of one name under `impl` lines with the same [reference], as in two [view]s, which would make two [item]s carry out one.
