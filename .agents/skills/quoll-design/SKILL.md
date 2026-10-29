---
name: quoll-design
description: Work a ticket of the Quoll repository with a person, as the orchestrator - take design decisions as axes with options and a lean, record only what the person ratifies, and run the agents that write a package's headers and bodies. Use for any issue labelled decide or write, and for any change to a Quoll package.
---

# Quoll design

You are the **orchestrator**. You work one ticket with one **person**, who rules on every design decision, and you run other agents in **roles**, each in a fresh context, on prompts you write. You take no design decision yourself: you bring each to the person, and you carry out what the person ratifies. The language is [the definition](../../../language/package.md); this skill holds the practice around it and restates none of it.

Read [`AGENTS.md`](../../../AGENTS.md) first: its conventions bind everything here.

## Taking a ticket

1. Read the issue whole, with `gh issue view <n> --comments`, and every design it links. Restate its scope to yourself: what it asks, and what its requirements are. Where the scope is unclear, ask the person; never infer it from what is missing.
2. Open its working directory, `.quoll-wip/<issue>-<topic>/`, and, unless it is `decide`, its branch, `<type>/<issue>/<description>`.
3. Read what of the definition the ticket touches, and the package it works on, as it stands. Establish what exists and what is only designed: a decision resting on a module or a file that does not exist yet is a mistake this prevents.
4. Work it by its label:
   - `decide`: a pass of decisions, below, writing into no package. It closes once every axis it opened is ratified, with no commit: tell the person, who closes the issue. Its `decisions.md` stays in its working directory for the `write` ticket that records it.
   - `write`: decide what the ticket leaves open, then write the package by the roles, below. Where the ticket rests on a `decide` ticket, extract that ticket's verdicts from its working `decisions.md`, and ask the person where it is absent.
   - `generate` and `release`: not covered by this skill yet. Say so to the person and stop.

## Deciding

Every design decision is the person's. Run it as [`references/deciding.md`](references/deciding.md) has it: each unsettled thing becomes an **axis** in the ticket's `decisions.md`, under Open by its question; a set at a time is brought into progress, each written whole with its options, a criterion and your lean, the axes the others depend on first; and the person's verdict closes each.

- **Nothing is recorded around an axis not yet closed.** A decision met while writing a header, a body or an entry stops that writing: bring the axis, its options and your lean to the person, at the top of your message, and resume only once it is ratified.
- **Only what is designed is recorded.** Where a verdict settles a principle but not its terms or its form, it enters a package as one `open:` item, worded with the person, and nothing of it is designed further.
- A question that a ratified verdict already settles is yours to answer: record your answer, and tell the person, who may overrule it.

## Writing a package

A package is written in two stages, each by roles you run.

**Headers.** The **architect** writes the headers, the private headers, the manifest and the decisions files from the ratified decisions, as [`references/architect.md`](references/architect.md) has it. A **header reviewer**, fresh, reviews what it wrote, as [`references/header-review.md`](references/header-review.md) has it. Findings go back to the architect, round by round, until the headers are settled. What the architect or the reviewer raises that needs a decision goes to the person, as an axis.

**Bodies.** Once the headers a module's body implements are settled, a pair writes the body: a **body writer**, as [`references/body-writer.md`](references/body-writer.md) has it, and a **body reviewer**, fresh, as [`references/body-review.md`](references/body-review.md) has it. A question the headers leave open goes back to the architect and the person as a finding against the header, the body settling it provisionally meanwhile. The choices the headers leave to the body are the writer's, as the principles' `unstated choices` has it; once a pair settles, list its entries *Taken by* the writer to the person, who may let each stand or open an axis on it.

**Rounds.**
- Run the checks after every round, before any review: an architect counting widths and order by hand misses some.
- A round whose findings are all minor goes back to its writer with no new review, the checks standing in; a blocking finding, or a change in a package's shape, gets a review.
- Two rounds of a pair at most; what stays open after them goes to the person. The passes closed change asks for, below, belong to the round that caused them, and are not counted.

**Closed change.** Whenever a round changes what an item or an entry states, the principles' `closed change` asks that every site resting on it be revisited. Before the round, copy the package into the working directory; after it, run `ref_sites.py <copy> <package>` and send the sites it lists to the writer, who revisits each and amends what no longer holds. Copy again and repeat until a pass amends nothing. The script matches references by their text, as its docstring says; a site it cannot see is the writer's to find.

## Prompts for the roles

You write each role's prompt yourself, and run it by whatever your agent has for running another agent in a fresh context: a subagent, a separate session, or a headless run of an agent's command line. Every prompt carries:

- **the role** and its one goal, and its reference file from `references/`, which it reads first;
- **what it reads**: every file by its path, those its reference file says it always reads among them, and that it reads no other, naming in its report any other it needs;
- **what it writes**, and that it changes no other file;
- **what it reports** at its end, as its reference file says.

An agent reads only what its prompt names, and searching long records costs it: extract what it needs into one inputs file in the working directory, with `extract.py`. Keep out of its inputs any verdict it must not design further, and give it the `open:` wording instead.

Save every prompt as sent, in the working directory's `prompts/`, one file per prompt, noting the agent and model that ran it. Where your agent keeps a transcript of a role's run, check that it read only what its prompt named, and report any other read.

A role is fresh for each task and continued through that task's rounds. Where your agent cannot continue one, start a fresh one for the next round, giving it the previous round's findings and answers as files. An agent cannot be continued from another session: a pair interrupted there is rerun fresh, and you tell the person.

**The ticket is leave for the roles its process names and their rounds.** Another role, a third round, or any agent beyond them is asked of the person first.

## Checks

The checks are this skill's `scripts/`, each run with `python3 -I` from the repository's top, as `python3 -I .agents/skills/quoll-design/scripts/check_blocks.py std`. Each prints what it finds, for you or a reviewer to judge.

- `check_blocks.py <package dir>`: every view block's groups, items and widths.
- `check_bare.py <package dir>`: every bare use of a name some reference uses, each a missing reference, a use beyond sight, or the word in another sense.
- `check_part.py <header> <decisions> <MNEMONIC> name=<header> ...`: one module's references, its items' order, and its entries' *Stated by*; for a module with a body, concatenate its header and body into one file first.
- `ref_sites.py <old copy> <package dir>`: the sites resting on what changed between two copies of a package.
- `extract.py <out> <title> <record>:<ID>,<ID> ...`: blocks of a record by their IDs, whole, into one inputs file.

## Closing a ticket

Nothing is pushed before the ticket's final review settles: the repository is public, and a push publishes.

1. Commit on the ticket's branch as `AGENTS.md` says, the body ending with `Closes #<issue>`. Each round of fixes after a review is a commit of its own, so that the reviewer sees what changed since its last round as well as the whole.
2. Write the pull request's body to the working directory's `pr.md`: what changed; which decisions were recorded, by their entries' IDs; the roles run, their rounds, and the agent and model of each; and **what this guidance left unanswered**, each question you had to ask the person or guess. It quotes nothing of the working directory, which is private.
3. Ask the person for the final review: a fresh reviewer, run by the person, reviews the branch as [`references/ticket-review.md`](references/ticket-review.md) has it, and writes its findings to the working directory's `review.md`. Answer each beneath it, fixed or why not, the fixes in a new commit.
4. Once the person says the review is settled, squash the branch's commits into one, its message the first's, amended where the fixes changed what it says, as the last step before the push, and check that `git diff <last reviewed commit>` is empty; then the person pushes the branch and opens the pull request with `pr.md`, or asks you to. The person merges.

If a session ends before the ticket closes, write `handoff.md` in the working directory: where the ticket stands, what is next, and what to read first.
