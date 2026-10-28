How a [layout.source file] is written, for whoever writes one, person or agent, and for any tool that reads one: the [markdown] it is written in, and the language's [construct]s within it and, a [front], before it, each read as [own text] has it; what a [layout.source file] means is not stated here.

## Structure

```
  markdown        GitHub Flavored Markdown, its specification's version 0.29-gfm, in which a
                  [layout.source file]'s text is written; a line, a blank line, a paragraph, a
                  heading, a fenced block, a code span, a link, a list and a task box are as
                  that specification has them
  item            a name and its statement: its first line holds the name, running to its
                  first two spaces or to the line's end, then the statement; each later line
                  more indented than the first continues it, the blank lines between them
                  included
  entry           a paragraph of a [layout.decisions] whose first line opens with `**`, its ID, a
                  full stop and a space, holds its statement and ends with `**`; its ID a
                  mnemonic, an ASCII letter then ASCII letters, digits and hyphens, then a hyphen
                  and a number, ASCII digits after the ID's last hyphen; each later line opening
                  with one of the words `*Stated by*`, `*Because*`, `*Accepting*`, `*Revisit*`,
                  `*Rejected*`, `*Superseded by*`, `*Formerly*` or `*Taken by*`, is a line under
                  that word, the rest of the line its text; and its other lines, in their order,
                  are what was decided
  label           a word written after a `#` that follows a space, every character after its `#`
                  to the next space or the line's end, in the run of such words that ends an
                  [item]'s or an [entry]'s last line: a part of that [item] or [entry], and none
                  of its statement or of what was decided; any other `#` word is text
  reference       a name or a dotted path in square brackets, as `[foo.bar.baz]`, within one
                  [item], one line of an [entry] or one other paragraph, or else on one line;
                  letters following its closing bracket inflect the name, as `[baz]s`, the
                  [reference] being the bracketed name alone; a bracket followed at once by a
                  parenthesis opens a link, which is no [reference]; and, in a
                  [layout.decisions], an ID written bare whose mnemonic is that of its own
                  [entry]s, whether or not one of its [entry]s holds it, outside square
                  brackets, with neither a letter, a digit nor a hyphen just before it nor a
                  digit or a hyphen just after it, but where it opens its own [entry], an ID
                  of another mnemonic being text
  core word       one of the words `project`, `package`, `module`, `interface`, `item` and
                  `decision`, written bare as a whole word in text alone, an [item]'s
                  statement, an [entry]'s lines or a paragraph, and never an [item]'s name
                  where the [item] is defined, a heading the language names, a [label] or a
                  link's destination; the word followed by `s`, `'s` or `s'`, its plural or
                  possessive, as `modules`, is the word, and so is any of these forms with a
                  capital where it opens a sentence, while any other word opening with one is
                  text; a bracketed span is a [reference], never a [core word]
  front           the lines from a `---` line a [layout.header], a [layout.private header] or
                  a [layout.body] opens with to the next `---` line: YAML, no part of its
                  [markdown] text, which is the lines after them, so that they hold no heading,
                  [reference], [label] or [core word]; a YAML mapping whose keys are the
                  language's, `implements`, in a [layout.body], and `includes`, in a
                  [layout.header] or a [layout.private header], each holding a YAML list of
                  names, however YAML writes it; each name its scalar's content, its quotes and
                  escapes resolved, before YAML gives it a type, written as a [reference]'s
                  bracketed name is, without its brackets; a key the language does not name
                  there, or one it names whose value is no list of scalars, is no part of the
                  [front], nor are the lines of its value; and where the opening `---` line has
                  no closing one, or the lines between the two are no YAML mapping, the
                  [layout.source file] has no [front], those lines part of its [markdown] text
  lead            one paragraph, its text however many lines it runs over, where a
                  [layout.source file] of its kind holds one: in a [layout.header], a
                  [layout.private header] or a [layout.body], the one it opens with, nothing
                  but its [front] and blank lines before it
  section         the lines from a second-level heading to the next heading of the first or
                  second level, or to the text's end, whose heading reads `Structure`, `Flow` or
                  `Rules` in a [layout.header], a [layout.private header], a [layout.body] or a
                  [layout.build], or `Modules` in a [layout.manifest], and is the first so
                  headed in its [layout.source file], its piece its heading's text, and its
                  lines other than its heading, blank lines and its first fenced block writing
                  nothing of the language's; outside a [layout.decisions], any other
                  second-level heading, a second so headed among them, opens none, its line
                  and the lines under it, to the next heading of the first or second level,
                  writing nothing of the language's; and in a [layout.decisions] a heading's
                  line alone writes nothing, every [entry] under it standing as any other
  opener          a line holding only `ensures:`, `requires:` or `open:`, or, in a [layout.body],
                  `impl`, a space, a [reference] and `:`; a line holding one of these without its
                  `:` is that [opener] still
  view block      a fenced block whose lines are told apart by their indentation, the spaces each
                  opens with: each starts an [item], continues one, is an [opener], or is blank,
                  and one opening with a tab is none of these; its [opener]s stand at its least
                  indentation, and a run of them stacks, an `impl` line first and one other at
                  most, and opens a group, which runs to the first line other than a blank one
                  indented as they are, or to the block's end, its [item]s starting at the
                  indentation of its first line other than a blank one; outside every group,
                  its [item]s start at its least indentation; and a line less indented than its
                  group's [item]s but more than its [opener]s, or one holding an [opener]'s words
                  where none may stand, is none of these
  literal         text taken as written: a code span, a fenced block other than a [view block],
                  and a task box, `[ ]` or `[x]` opening a line of a list; within a [view block],
                  where [markdown] finds no code span, one runs from a run of backticks to the
                  next run as long on its line; such text holds no [reference], no [core word]
                  and no [label]
  view            a [section] headed `Structure`, `Flow` or `Rules`, its pieces which of the three
                  it is and its [view block], the [section]'s first fenced block
  manifest        the text of a [layout.manifest], its pieces its [layout.package]'s name, its
                  version, its link's destination, its edition, its [lead], and its [item]s,
                  each a [layout.path] and a statement: its one first-level heading, the name;
                  the paragraph after it, one line, `Version`, a space, the version, which holds
                  no space, `, written in `, a link to the language's definition whose text's
                  last word is the edition, and a full stop; its [lead], the paragraph after
                  that; and its [section] `Modules`, whose first fenced block is a [view block]
                  holding no [opener], each [item] of it named by a [layout.path]
  build           the text of a [layout.build], its pieces its [view]s
  construct       a part of a [layout.source file] the language writes, within [markdown] or, a
                  [front], before it, one of: a [front], a [section], a [lead], a [view], a
                  [view block], an [item], an [opener], a [label], a [reference], an [entry], a
                  [manifest], a [build] or a [core word]; its pieces, the things a statement
                  here names as its, as an [item]'s name and statement and the [label]s that
                  end it
  open:
    dependencies  a [manifest] holds its [layout.package]'s dependencies; how it writes them
                  waits for a [layout.package] that has some
    tests         how a [layout.source file] of [layout.tests] is written, its cases among it,
                  which waits for the first [layout.package] with [layout.tests]
```

## Rules

```
  requires:
    written         a [layout.source file] holds nothing but what these [item]s write, and
                    [markdown] within its [lead] and its [entry]s
    width           no line of a [view block] passes 100 columns
    used            every use of a name in scope, in the sense of what it names, everywhere in
                    every [layout.source file] alike, is a [reference], but an [item]'s own
                    name where the [item] is defined, a name in a [front], and a [core word];
                    the name's word in another sense is text
    own terms       in the language's own [layout.package], no [core word] stands: each use of
                    its word in text is a [reference]
    no definitions  a [layout.source file] writes no link definition, as
                    `[foo]: https://foo.example/`
    grouped         every [item] of a Rules [view] stands in a group of `ensures:`, `requires:` or
                    `open:`, and a group of `open:` may stand in any [view]
    column          the statements of one [view block] start in one column
    colon           an [opener] ends in its `:`
    no empty view   a [view] holds at least one [item]
    one name        no two [item]s of one [layout.source file] share a name, but two in a
                    [layout.body] under `impl` lines whose [reference]s differ
    examples        an example of how a [layout.source file] is written, in [literal] text,
                    names nothing its [layout.package] defines and copies none of the
                    [layout.package]'s own text, taking made-up names, as `foo`, `bar`, `baz`
                    and `qux`
    unique          the IDs of one [layout.decisions] share a mnemonic no other uses
    stated          every [entry]'s line after its first is its line under `*Stated by*`, holding
                    [reference]s alone, each naming an [item], joined by commas and `and`
  ensures:
    own text        every [construct] is read off one [layout.source file]'s own text, never what
                    it means, while a rule for writers, as [used], [own terms], [examples] and
                    [unique], may rest on the [layout.package] and on what its writer means
    slips           a [construct] written against [width], [grouped], [column], [no empty view]
                    or [stated] is still the [construct] it reads as
```
