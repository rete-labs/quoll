# Quoll

This repository holds Quoll, a language for the source of a system, and the packages written in it. What the language is, who writes and reads it, and what it aims at is stated by the language itself, in [`language/quoll.h.md`](language/quoll.h.md); the whole definition is [`language/`](language/package.md), written in Quoll. It is the one reference for the language: read the parts your work needs, and never restate them anywhere else.

Every directory at the repository's top holding a `package.md` is a package, written in Quoll; together they form one project, released at one version, tagged `vX.Y.Z`.

## Working here

Work arrives as GitHub issues on `rete-labs/quoll`. For any issue, and for any change to a package, follow the skill [`quoll-design`](.agents/skills/quoll-design/SKILL.md): it says how a ticket is worked with a person, how a design decision is taken and recorded, and which roles write a package. An agent that does not load skills from `.agents/skills/` reads that file directly.

An issue's label says what it ends with:

- `write`: one package change, decided and written with a person, ending in its final source and component decisions committed together.
- `generate`: targets, generated from a package's source, or straight from decisions where none exists yet.
- `release`: a version tagged, and what it holds published.

## Conventions every change keeps

- **English**, in every file, commit, issue and pull request.
- **Markdown is never hard-wrapped**: a paragraph, a list item or a table row is one line, however long. The language's view blocks are the exception, written as its grammar has them.
- **Git** follows Florete's [git workflow](https://florete.tech/docs/contributing/workflows/git-workflow), [issue tracking](https://florete.tech/docs/contributing/workflows/issue-tracking) and [commit messages](https://florete.tech/docs/contributing/workflows/commit-messages): a branch `<type>/<issue>/<description>` per issue that changes the repository, and one pull request closing it, merged by rebase as one commit, whose message is a Conventional Commit naming the issue, as `feat(std): add the fs module (#3)`. A scope names the package a change lands in; a change to this guidance is `build(authoring)`.
- **No agent's trailer**: no `Co-Authored-By`, `Assisted-By` or "generated with" line in a commit or a pull request.
- **Working files** go in `.quoll-wip/`, which git ignores, a ticket's in `.quoll-wip/<issue>-<topic>/`; never in `/tmp`, which may be lost, and never committed.
- **Nothing private** enters this public repository or its issues: no business context, no client, no person's name but a contributor's own. Material given to you privately, prior art among it, informs your work and is never copied into a file or a post.
- **An issue or a comment is concise**: what to do and only what doing it needs, its requirements as results anyone can observe, and links to the designs it rests on; it copies none of them, restates no decision it carries out, prescribes no solution, and cites nothing private.
- **A post that turned wrong before anyone read it**, an issue's body or a comment, is edited in place rather than corrected by another post; fetch its live text first, and add a comment instead where someone has replied.
- **Nothing is pushed before a ticket's final review settles**, since a push publishes; the skill says how a ticket closes.
