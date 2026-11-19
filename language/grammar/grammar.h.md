+++
prelude = []
+++
How a canonical Quoll [layout.source file] is written, for whoever writes one, person or agent, and for any tool that reads one: the [markdown] or [toml] it is written in, and the language's [construct]s within it and, a [front], before it, each read as [own text] has it; its [native form], [native overlay], [native link], [target map] and [tests] remain open.

## Structure

```
  markdown            in canonical Quoll, GitHub Flavored Markdown, its specification's version
                      0.29-gfm, in which a [layout.source file]'s prose and design statements are
                      written; a line, a blank line, a paragraph, a fenced block, a code span, a
                      link, a list and a task box are as that specification has them, while a
                      heading is only its plain ATX form: at column zero, one to six `#` characters,
                      one ASCII space, then nonempty text with no leading or trailing whitespace and
                      no whitespace-delimited closing `#` sequence; only this form has heading
                      meaning in canonical Quoll
  toml                in canonical Quoll, TOML, in which a [layout.manifest], [layout.modules],
                      [layout.lock], [layout.workspace manifest] and metadata preceding a
                      [layout.header]'s, [layout.private header]'s, [layout.body]'s,
                      [layout.decisions]' or [layout.workspace decisions]' text are written

  item                a name and its statement: its first line holds the name, running to its first
                      two spaces or to the line's end, then the statement; each later line more
                      indented than the first continues it, the blank lines between them included
  entry               a paragraph of a [layout.decisions] or [layout.workspace decisions], its ID a
                      mnemonic, an ASCII letter then ASCII letters, digits and hyphens, then a
                      hyphen and a number, ASCII digits after the ID's last hyphen; an active one
                      opens with `**`, its ID, a full stop and a space, holds its statement on that
                      line and ends that line with `**`, each later line opening with one of the
                      words `*Stated by*`, `*Because*`, `*Accepting*`, `*Revisit*`, `*Rejected*`,
                      `*Formerly*` or `*Taken by*` is a line under that word, the rest of the line
                      its text, and its other lines, in their order, are what was decided; a
                      superseded one is one line opening with `**`, its ID and `.**`, followed by
                      ` *Superseded by* ` and its successor's ID, with no other text or line
  label               a word written after a `#` that follows a space, every character after its `#`
                      to the next space or the line's end, in the run of such words that ends an
                      [item]'s or an [entry]'s last line: a part of that [item] or [entry], and none
                      of its statement or of what was decided; any other `#` word is text
  reference           a name or a dotted path in square brackets, as `[foo.bar.baz]`, within one
                      [item], one line of an [entry] or one other paragraph, or else on one line; in
                      a [layout.workspace decisions], the first name may be an unversioned
                      [package id], whose own full stops stay within it, a full stop after it
                      starting the following path; letters following its closing bracket inflect the
                      name, as `[baz]s`, the [reference] being the bracketed name alone; a bracket
                      followed at once by a parenthesis opens a link, which is no [reference]; and,
                      in a [layout.decisions] or [layout.workspace decisions], an ID written bare
                      whose mnemonic is that of its own [entry]s, whether or not one of its [entry]s
                      holds it, outside square brackets, with neither a letter, a digit nor a hyphen
                      just before it nor a digit or a hyphen just after it, but where it opens its
                      own [entry], an ID of another mnemonic being text
  package id          in canonical Quoll, an unversioned Package URL of the form
                      `pkg:quoll/<trust-domain>/<arbitrary-path>/<pkg-name>`: the trust domain is
                      mandatory, the remaining namespace path is user-defined, and the final segment
                      is the [layout.package]'s name
  selector            in canonical Quoll, a [package id] followed in the Package URL's version
                      position by an exact semantic version, stable or prerelease; an exact
                      canonical development pseudo-version in no-base
                      `v0.0.0-<timestamp>-<revision>`, prerelease-base
                      `vX.Y.Z-pre.0.<timestamp>-<revision>` or release-base
                      `vX.Y.(Z+1)-0.<timestamp>-<revision>` form, with a UTC `yyyymmddhhmmss`
                      timestamp and 12 lowercase hexadecimal revision characters; or a partial
                      stable-release selector `v<major>` or `v<major>.<minor>`
  release tag         in canonical Quoll, a TOML string writing a selected semantic release
                      version's canonical stable or prerelease spelling, `vX.Y.Z` being the stable
                      form: at the repository root, that spelling alone, as `v0.4.0`; below it, the
                      repository-relative [layout.package] path followed by `/` and that spelling,
                      as `std/v0.4.0` and `std/v0.5.0-beta.1`
  source locator      in canonical Quoll, a string `<location>@<request>`, parted at its last `@`:
                      the request is an exact [selector]'s version or a nonempty branch or commit;
                      the location is either an HTTP or HTTPS URL whose first segment ending in
                      `.git` closes the repository path, followed by any [layout.package] path, or
                      GitHub shorthand, host-qualified `github.com/<owner>/<repository>` or hostless
                      `<owner>/<repository>`, each followed by any [layout.package] path, the
                      host-qualified form optionally taking an HTTP or HTTPS scheme; a
                      [layout.package] path is slash-separated and repository-relative, empty at the
                      repository root, and the whole string holds no whitespace, as
                      `https://acme.example/team/widgets.git/packages/core@main`, whose repository
                      ends at `widgets.git`, [layout.package] path is `packages/core` and request is
                      `main`; `github.com/acme/widgets/packages/core@v1.2.0`, whose repository is
                      `github.com/acme/widgets`, with the same [layout.package] path and request
                      `v1.2.0`; and `acme/widgets/packages/core@v1.2.0`, whose first two segments
                      name the same GitHub repository, with the same [layout.package] path and
                      request

  front               the lines from a `+++` line a [layout.header], a [layout.private header], a
                      [layout.body], a [layout.decisions] or a [layout.workspace decisions] opens
                      with to the next `+++` line: [toml], no part of its [markdown] text, which is
                      the lines after them, so that they hold no heading, [reference] or [label]; a
                      TOML mapping whose keys are the language's, `implements`, in a [layout.body],
                      and `includes`, in a [layout.header] or a [layout.private header], each
                      holding a TOML list of names; `exposes`, in a [layout.header] or
                      [layout.private header], a table whose every key is an exposed name or dotted
                      path and whose every value is a TOML string holding its target's [reference]
                      spelling, without brackets; in canonical Quoll, `prelude`, in a
                      [layout.header], [layout.private header], [layout.body], [layout.decisions] or
                      [layout.workspace decisions], holding a TOML list of strings; `use`, in any of
                      those, a table whose keys are strings and whose values are TOML lists of
                      strings; `aliases`, in the same files, a table whose values are strings; and
                      `"module lead"`, in a [layout.header] or [layout.private header], holding the
                      boolean `true`; in a [layout.decisions] or [layout.workspace decisions],
                      `prelude`, `use` and `aliases` alone are keys the language names there; each
                      name in `implements` or `includes`, each `exposes` key and the content of each
                      `exposes` value are written as a [reference]'s bracketed name is, without its
                      brackets, a dotted `exposes` key quoted whole as one TOML key, as
                      `archy = "hier.archy"` and `"foo.bar" = "hier.foo.bar"`; each `use` key is
                      such a qualified name, quoted whole, and each string in its value writes an
                      explicit relative continuation as a [reference]'s bracketed name is written;
                      each `aliases` value is a [package id], a [selector], or such a qualified
                      name; a key the language does not name there, or one it names whose value is
                      not of that form, is no part of the [front], nor are the lines of its value;
                      and where the opening `+++` line has no closing one, or the lines between the
                      two are no TOML mapping, the [layout.source file] has no [front], those lines
                      part of its [markdown] text
  lead                one paragraph, its text however many lines it runs over, where a
                      [layout.source file] of its kind holds one: in a [layout.header], a
                      [layout.private header] or a [layout.body], the one it opens with, nothing but
                      its [front] and blank lines before it
  section             the lines from a second-level [markdown] heading to the next [markdown]
                      heading of the first or second level, or to the text's end, whose heading's
                      text is exactly `Structure`, `Flow` or `Rules` in a [layout.header], a
                      [layout.private header], a [layout.body] or a [layout.assembly], and is the
                      first so headed in its [layout.source file], its piece its heading's text, and
                      its lines other than its heading, blank lines and its first fenced block
                      writing nothing of the language's; outside a [layout.decisions] and
                      [layout.workspace decisions], any other second-level [markdown] heading, a
                      second so headed among them, opens none, its line and the lines under it, to
                      the next [markdown] heading of the first or second level, writing nothing of
                      the language's; and in a [layout.decisions] or [layout.workspace decisions] a
                      [markdown] heading's line alone writes nothing, every [entry] under it
                      standing as any other
  opener              a line holding only `ensures:`, `requires:` or `open:`, or, in a
                      [layout.body], `impl`, a space, a [reference] and `:`; a line holding one of
                      these without its `:` is that [opener] still
  view block          a fenced block whose lines are told apart by their indentation, the spaces
                      each opens with: each starts an [item], continues one, is an [opener], or is
                      blank, and one opening with a tab is none of these; its [opener]s stand at its
                      least indentation, and a run of them stacks, an `impl` line first and one
                      other at most, and opens a group, which runs to the first line other than a
                      blank one indented as they are, or to the block's end, its [item]s starting at
                      the indentation of its first line other than a blank one; outside every group,
                      its [item]s start at its least indentation; and a line less indented than its
                      group's [item]s but more than its [opener]s, or one holding an [opener]'s
                      words where none may stand, is none of these
  literal             text taken as written: a code span, a fenced block other than a [view block],
                      and a task box, `[ ]` or `[x]` opening a line of a list; within a
                      [view block], where [markdown] finds no code span, one runs from a run of
                      backticks to the next run as long on its line; such text holds no [reference]
                      and no [label]
  view                a [section] headed `Structure`, `Flow` or `Rules`, its pieces which of the
                      three it is and its [view block], the [section]'s first fenced block

  manifest            in canonical Quoll, the [toml] of a [layout.manifest]: a mapping holding
                      exactly `id`, a [package id]; `edition`, a quoted version of the language's
                      definition; `description`, a quoted short statement of what the
                      [layout.package] is for; and `dependencies`, a list of [selector]s, unique by
                      their unversioned [package id] within one major compatibility series, so
                      distinct major series of one [package id] may coexist
  workspace manifest  in canonical Quoll, the [toml] of a [layout.workspace manifest]: a mapping
                      holding exactly `packages`, a list of workspace-relative [layout.path]s,
                      `edition`, a quoted version of the language's definition fixing the grammar
                      and source meaning of the [layout.workspace]'s own files, and `description`, a
                      quoted short statement of what the [layout.workspace] maintains
  modules             in canonical Quoll, the [toml] of a [layout.modules]: a mapping holding
                      exactly `modules`, a list of package-relative [layout.path]s
  lock                in canonical Quoll, the [toml] of a [layout.lock]: an array of `dependencies`
                      tables covering the root's direct and transitive graph, each holding `id`, an
                      exact selected [selector], and `hash`, the selected tree's
                      [layout.content hash], written as `1220` followed by 64 lowercase hexadecimal
                      digest digits, with a `sources` array of tables each holding `locator`, a
                      [source locator], and `commit`, the full resolved Git commit; a release source
                      also holds `tag`, a [release tag], while a development source holds exactly
                      `locator` and `commit`; several sources may be mirrors, sharing the expected
                      hash and carrying their own [source locator] and commit where histories differ
  assembly            the text of a [layout.assembly], its pieces its [view]s

  construct           a part of a [layout.source file] the language writes, within [markdown] or
                      [toml] or, a [front], before [markdown], one of: a [front], a [section], a
                      [lead], a [view], a [view block], an [item], an [opener], a [label], a
                      [reference], an [entry], a [package id], a [selector], a [release tag], a
                      [source locator], a [manifest], a [workspace manifest], a [modules], a [lock]
                      or an [assembly]; its pieces, the things a statement here names as its, as an
                      [item]'s name and statement and the [label]s that end it

  open:
    native form        native manifests, requirement grammars, resolvers and locks stay with their
                       ecosystems; the concrete declaration connecting native and canonical Quoll
                       source, any mixed-source or generation-provenance record included, and its
                       cross-profile meaning wait for the native semantic joins that own them
    native overlay     the concrete grammar of a [layout.native overlay] waits for the first native
                       source profile implementing that overlay
    native link        the concrete tokens and placement of structured native comments or
                       annotations, and what they carry and mean, wait for the native semantic joins
                       that own them
    target map         one concrete grammar of the common [layout.target map] waits for the first
                       derived-target implementation
    tests              how a [layout.source file] of [layout.tests] is written, its cases among it,
                       which waits for the first [layout.package] with [layout.tests]
```

## Rules

```
  requires:
    written         a [layout.source file] holds nothing but what these [item]s write, and
                    [markdown] within its [lead] and its [entry]s
    no definitions  a [layout.source file] writes no link definition, as
                    `[foo]: https://foo.example/`

    used            every use of a name in scope, in the sense of what it names, in [markdown] text,
                    is a [reference], but an [item]'s own name where the [item] is defined; a name
                    in a [front] or another [toml] value is written as that value's [construct] has
                    it; the name's word in another sense is text
    examples        an example of how a [layout.source file] is written, in [literal] text, names
                    nothing its [layout.package] defines and copies no statement of that
                    [layout.package], taking made-up names, as `foo`, `bar`, `baz` and `qux`

    width           no line of a [view block] passes 100 [column]s
    column          the statements of one [view block] start in one [column]

    grouped         every [item] of a Rules [view] stands in a group of `ensures:`, `requires:` or
                    `open:`, and a group of `open:` may stand in any [view]
    colon           an [opener] ends in its `:`
    no empty view   a [view] holds at least one [item]
    one name        no two [item]s of one [layout.source file] share a name, but two in a
                    [layout.body] under `impl` lines whose [reference]s differ

    unique          the IDs of one [layout.decisions] or [layout.workspace decisions] share a
                    mnemonic no other uses
    stated          in a [layout.decisions], every active [entry]'s line after its first is its line
                    under `*Stated by*`, holding [reference]s alone, each naming an [item], joined
                    by commas and `and`; an active [entry] of a [layout.workspace decisions] instead
                    carries its rationale directly in its statement and later lines, with no
                    `*Stated by*` line; a superseded [entry] instead holds only its one-line
                    `*Superseded by*` pointer, naming its successor

    canonical toml  every scalar in [toml] is quoted explicitly where its kind has a quoted form,
                    arrays of [package id]s, [selector]s and [layout.path]s stay short, and [lock]
                    entries and their sources use arrays of tables

  ensures:
    own text        every [construct] is read off one [layout.source file]'s [own text], never what
                    it means, while a rule for writers, as [used], [examples] and [unique], may rest
                    on the [layout.package] and on what its writer means
    slips           a [construct] written against [width], [grouped], [column], [no empty view] or
                    [stated] is still the [construct] it reads as
```
