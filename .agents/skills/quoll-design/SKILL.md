---
name: quoll-design
description: Work a ticket of the Quoll repository with a person, as the orchestrator - take design decisions as axes with options and a lean, record only what the person ratifies, and run the agents that write a package's headers and bodies. Use for any issue labelled write, and for any change to a Quoll package.
---

# Quoll design

You are the **orchestrator**. You work one ticket with one **person**, who rules on every design decision, and you run other agents in **roles**, each in a fresh context, on prompts you write. You take no design decision yourself: you bring each to the person, and you carry out what the person ratifies. The language is [the definition](../../../language/language.h.md); this skill holds the practice around it and restates none of it.

Read [`AGENTS.md`](../../../AGENTS.md) first: its conventions bind everything here.

## Taking a ticket

1. Read the issue whole, with `gh issue view <n> --comments`, and every design it links. Restate its scope to yourself: what it asks, and what its requirements are. Where the scope is unclear, ask the person; never infer it from what is missing.
2. Open its working directory, `.quoll-wip/<issue>-<topic>/`, and its branch, `<type>/<issue>/<description>`, from the start.
3. Read what of the definition the ticket touches, and the package it works on, as it stands. Establish what exists and what is only designed: a decision resting on a module or a file that does not exist yet is a mistake this prevents.
4. Work it by its label:
   - `write`: decide and write one package change. Take what the ticket leaves open through the deciding pass below, then write its final package by the roles below, reopening a verdict with the person whenever the writing or review tests it. Its working `decisions.md` stays local; its final source and component decisions are committed together.
   - `generate`: not covered by this skill yet. Say so to the person and stop.
   - `release`: publish the release as [`references/release.md`](references/release.md) has it.

## Deciding

Every design decision is the person's. Run it as [`references/deciding.md`](references/deciding.md) has it: each unsettled thing becomes an **axis** in the ticket's `decisions.md`, under Open by its question; a set at a time is brought into progress, each written whole with its options, a criterion and your lean, the axes the others depend on first; and the person's verdict closes each.

- **Nothing is recorded around an axis not yet closed.** A decision met while writing a header, a body or an entry stops that writing: bring the axis, its options and your lean to the person, at the top of your message, and resume only once it is ratified.
- **Only what is designed is recorded.** Where a verdict settles a principle but not its terms or its form, it enters a package as one `open:` item, worded with the person, and nothing of it is designed further.
- A question that a ratified verdict already settles is yours to answer: record your answer, and tell the person, who may overrule it.

## Writing a package

A package is written in two stages, each by roles you run.

**Plan the change and its consumers.** Before implementation, record a short working plan naming the target change, the contracts and items it touches, and every declared consumer its work must serve. Have the consistency architect identify consumers and missing joins from the public contracts; do not make an implementation writer discover them by reading the whole package. Split a large change into coherent, reviewable chunks, each with its target, declared consumers, permitted inputs, dependencies, and checks. A chunk must leave its own target and declared consumers consistent; later chunks and the whole-package consistency pass must not depend on an unstated interface or an undocumented binding. Keep the chunks independent where their inputs allow it, and sequence them where one consumes another's settled contract.

**Consistency architecture is not implementation architecture.** The architect and header reviewer are consistency roles: they may see the package and all public contracts needed to judge its shape, references, decision lifetime, and consumers. A body writer is an implementation role: it receives only its target contract, the interfaces that contract implements or uses, and the declared consumers its work must serve. Its reviewer receives the same bounded context. Never give an implementation writer unrelated interfaces merely to make whole-package consistency easier; that remains the consistency roles' work.

**Headers.** The **architect** writes the headers, the private headers, the manifest and the decisions files from the ratified decisions, as [`references/architect.md`](references/architect.md) has it. A **header reviewer**, fresh, reviews what it wrote, as [`references/header-review.md`](references/header-review.md) has it. Findings go back to the architect, round by round, until the headers are settled. What the architect or the reviewer raises that needs a decision goes to the person, as an axis.

**Bodies.** Once the headers a module's body implements are settled, a pair writes the body: a **body writer**, as [`references/body-writer.md`](references/body-writer.md) has it, and a **body reviewer**, fresh, as [`references/body-review.md`](references/body-review.md) has it. A question the headers leave open goes back to the architect and the person as a finding against the header, the body settling it provisionally meanwhile. The choices the headers leave to the body are the writer's, as the principles' `unstated choices` has it; once a pair settles, list its entries *Taken by* the writer to the person, who may let each stand or open an axis on it.

**Rounds.**
- Capture a ticket baseline before the first edit and a round baseline before each round. Run the named checks after every round, before any review, using the round baseline for diff-scoped diagnostics; keep the ticket baseline for the final review.
- Freeze the round's package, role inputs, prompts, and check output in the working directory, and launch review against that frozen set. Settle newer decisions in parallel in the working record, without changing the frozen inputs. The next writer round receives both the review findings and every newer ratified verdict, explicitly distinguished from the frozen round's inputs.
- Review the changed items and their declared dependents first, then the chunk, and only then the whole package for consistency. A whole-package check is not leave to give an implementation role unrelated source.
- A round whose findings are all minor goes back to its writer with no new review, the checks standing in; a blocking finding, or a change in a package's shape, gets a review.
- When a role runs as a background agent, launch it once, end the turn without polling it, and resume on its completion notification. Do not launch a duplicate because its result is not immediate. If another role is independent, launch it on the next turn immediately rather than waiting for that notification: independent roles run concurrently. Wait for completion only when the next role depends on the previous result, as a writer's reviewer depends on the writer's round.
- Two rounds of a pair at most; what stays open after them goes to the person. The passes closed change asks for, below, belong to the round that caused them, and are not counted.

**Decision lifetime and closed change, every round.** Every round that writes source or decisions explicitly checks both and records the result, including when there is nothing to change. For each entry added, amended, moved, superseded, or restored, use its committed history to apply the principles' `lifetime`; do not leave this to final review. A superseded entry is a titleless pointer-only stub retaining its stable ID and only `*Superseded by* NEW-ID`, with no `*Stated by*` or other active-decision fields; its active successor carries the superseded alternative under `*Rejected*`, and the old prose remains in Git history. Whenever a round changes what an item or an active entry states, revisit every site resting on it before settling the round. Converting a full superseded entry to its pointer-only stub is valid history migration, not a changed active choice, and triggers no closed-change pass by itself; changing the successor's active choice does. Use the round baseline as the old copy, run `python3 -I .agents/skills/quoll-design/scripts/ref_sites.py <round baseline> <package>`, and send its sites together with the plan's declared consumers to the writer, who revisits each and amends what no longer holds. Copy again and repeat until a pass amends nothing. The script matches references by their text, as its docstring says; a site it cannot see is the writer's to find. Superseded historical entries are neither current edits nor sites requiring amendment, and restored history is not by itself a source defect.

## Prompts for the roles

You write each role's prompt yourself, and run it by whatever your agent has for running another agent in a fresh context: a subagent, a separate session, or a headless run of an agent's command line. Every prompt carries:

- **the role** and its one goal, and its reference file from `references/`, which it reads first;
- **the target change or chunk** and its declared consumers, with the boundaries of its review or writing task;
- **what it reads**: every file by its path, those its reference file says it always reads among them, and that it reads no other, naming in its report any other it needs;
- **what it writes**, and that it changes no other file;
- **the checks to run**, with exact current, baseline, dependency, and output paths;
- **what it reports** at its end, as its reference file says, including decision-lifetime and closed-change results and documented non-findings.

An agent reads only what its prompt names, and searching long records costs it: extract what it needs into one inputs file in the working directory, with `extract.py`. Keep out of its inputs any verdict it must not design further, and give it the `open:` wording instead. Preserve independence through context as well as freshness: if a role must remain independent or bounded, do not show the generating agent unrelated interfaces, review chatter, or other material its task does not require.

A role that needs an unlisted dependency or a missing join must stop the affected work and escalate the precise binding to the orchestrator, not read another file silently and not invent the binding. The orchestrator decides whether to supply the context, add an explicit join to the plan, or assign the join to another role, and then gives the writer the resulting input. A locator binding joining the model, grammar, and source is an example of a join the orchestrator may assign explicitly; no writer is expected to reconstruct it from unrelated interfaces.

Save every prompt as sent, in the working directory's `prompts/`, one file per prompt, noting the agent and model that ran it. Where your agent keeps a transcript of a role's run, check that it read only what its prompt named, and report any other read.

A role is fresh for each task and continued through that task's rounds. Where your agent cannot continue one, start a fresh one for the next round, giving it the previous round's findings and answers as files. An agent cannot be continued from another session: a pair interrupted there is rerun fresh, and you tell the person.

**The ticket is leave for the roles its process names and their rounds.** Another role, a third round, or any agent beyond them is asked of the person first.

## Checks

The checks are this skill's `scripts/`, each run with `python3 -I` from the repository's top. Package commands support v0.4 source only. Default semantic output is high-confidence and, with a baseline, diff-filtered; it is not a broad lexical gate. Each prints what it finds, for you or a reviewer to judge. Materialize only declared dependencies as checker inputs; a missing dependency or join follows the escalation rule above rather than improvised resolution.

- `check_blocks.py <package dir>` remains the view-block check: every block's groups, items and widths.
- `check_package.py CURRENT [--base BASELINE] [--dependency DEPENDENCY ...] [--review]` checks a whole v0.4 package and accepts only an earlier v0.4 package state as a baseline. Dependencies are materialized semantic inputs, not resolution. Use `--base <round baseline>` for each round's high-confidence diff-scoped run and `--base <ticket baseline>` for final review; omit it only for an intentional full-current check. Full current: `python3 -I .agents/skills/quoll-design/scripts/check_package.py std`; base-filtered: `python3 -I .agents/skills/quoll-design/scripts/check_package.py std --base .quoll-wip/<issue>-<topic>/before`; review: `python3 -I .agents/skills/quoll-design/scripts/check_package.py std --review`.
- `check_bare.py CURRENT [--base BASELINE] [--review]` retains only the targeted bare-compound errors, adding bare-word reviews in review mode: `python3 -I .agents/skills/quoll-design/scripts/check_bare.py std --review`. The `own`/`one` ambiguity guard can suppress a genuine lexical use; no general NLP is intended.
- `check_part.py` is a migration shim only, not a role command. Remove it once `check_package.py` covers every check for which a caller still uses the shim and all callers and guidance have migrated. Manual interface-name arguments and header/body concatenation are obsolete; never reconstruct the shim's inputs by hand.
- `ref_sites.py <old copy> <package dir>` lists the sites resting on what changed between two copies of a package: `python3 -I .agents/skills/quoll-design/scripts/ref_sites.py .quoll-wip/<issue>-<topic>/before std`.
- `extract.py <out> <title> <record>:<ID>,<ID> ...` extracts blocks of a record by their IDs, whole, into one inputs file.

Use review-mode output for a named investigation, not as a broad lexical-advisory gate. Promote only findings supported by the current source and the task's scope. Document a rejected diagnostic as a non-finding with its reason, including a pre-existing baseline state, restored history, valid full-to-pointer history migration, a known checker limitation, or a word used in another sense; none becomes a source defect by default.

Run all four test suites with `python3 -I -m unittest discover -s .agents/skills/quoll-design/tests -p 'test_*.py'`.

## Closing a ticket

Nothing is pushed before the ticket's final review settles: the repository is public, and a push publishes.

1. Commit the package's final source and its component decisions together on the ticket's branch as `AGENTS.md` says, the body ending with `Closes #<issue>`. The working `decisions.md` and any throwaway Quoll stay uncommitted. Each round of fixes after a review is a commit of its own, so that the reviewer sees what changed since its last round as well as the whole.
2. Write the pull request's body to the working directory's `pr.md`: what changed; which decisions were recorded, by their entries' IDs; the roles run, their rounds, and the agent and model of each; and **what this guidance left unanswered**, each question you had to ask the person or guess. It quotes nothing of the working directory, which is private.
3. Ask the person for the final review: a fresh reviewer, run by the person, reviews the branch as [`references/ticket-review.md`](references/ticket-review.md) has it, and writes its findings to the working directory's `review.md`. Answer each beneath it, fixed or why not, the fixes in a new commit. A finding that reopens a verdict goes back to the person as an axis; record the amended verdict in the working record and carry it into the final source and its component decisions together.
4. Once the person says the review is settled, squash the branch's commits into one, its message the first's, amended where the fixes changed what it says, as the last step before the push, and check that `git diff <last reviewed commit>` is empty; then the person pushes the branch and opens the pull request with `pr.md`, or asks you to. The person merges.

If a session ends before the ticket closes, write `handoff.md` in the working directory: where the ticket stands, what is next, and what to read first.
