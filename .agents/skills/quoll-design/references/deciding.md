# Deciding

How the orchestrator takes a design decision with the person, and records it. Everything here lives in the ticket's working file, `.quoll-wip/<issue>-<topic>/decisions.md`, until a `write` ticket records the verdicts into a package.

## The working file

One file that grows: each axis is one block, from its question to its options and lean to its verdict. The person may edit it too: edit it in place, never rewrite it whole, and keep every paragraph on one line. Chat carries pointers to it and argument about it, never a copy of it.

It opens with a counter, kept current, as `12 axes: 4 in progress, 5 open, 3 closed.`, and holds four sections, in this order:

- `## Inputs`: what the person gives that is not yet an axis, findings among it, each a paragraph opening with its ID, as `**IN-1. Short name.**`, followed by your reading and where it lands.
- `## In progress`: the axes being decided now, each written whole with its options and lean, for the person's verdicts.
- `## Open`: the axes still to decide, each by its question alone.
- `## Closed`: the axes ratified, each keeping everything it held, its verdict beneath.

The last three are an axis's statuses, and an axis moves as its status changes: a set brought into progress moves under In progress; a ratified one moves under Closed; one reopened, because a verdict it rested on flipped, goes back under In progress where it is decided in the same pass, or under Open where it waits. A reopened axis keeps its whole block, its old verdict included, with a line saying what reopened it, wherever it moves.

An axis's ID is a letter and a number, `A1`, `A2`, `B1`, the axes of one topic sharing a letter, so that one can be inserted, split, moved or closed without renumbering the rest; an ID is never reused.

## An axis

An axis is one thing the design leaves unsettled. It exists where something is asserted without warrant, or is silent where something must be settled; it is admitted where a competent person could reasonably choose otherwise **and** the choice changes the result. An item the person raises that this rule would reject means the rule is too narrow: widen it.

Write each axis whole when it is brought into progress:

```
**A1. Short name.** The question: what must be settled, and why it is open.

Options:
- (i) ← **The lean, in a few words.** What it is, enough to judge it.
- (ii) **Another.** ...

Criterion: the test that separates the options.

Lean: (i).
*Because* the reasons a reader needs to accept it.
*Accepting* what it costs.
*Rejected* (ii), with the reason it lost.
```

- **The criterion** is usually the hard part; once it is right, the pick is often plain. Name a dependency on another axis where one exists.
- **Name the claims a lean rests on**: a fact about the world, as that a tool behaves some way or a file exists, is stated with how it was checked, or as "from knowledge, not checked".
- **Prior art and examples** only where the person asks, or where an axis clearly benefits, as a notation or a mechanism with known precedent; if unsure, ask. An example is a few lines, never the implementation itself.
- **Keep it short**: leave out a rejection that a *Because* already answers, or that nobody would propose again.
- **Every consumer the design defers** gets the one property it needs from what is decided now, so that an incompatibility surfaces while it can still open an axis.

## What goes in progress

Decide a set of axes at a time, brought into progress together: the axes the others depend on, with those closely related to them; three to six, so that a pass is neither starved nor swamped. The next set is chosen in the light of what was ratified. Do not bring options and leans for every axis at once, even in a hurry: a verdict in one set can repurpose another, and the rework costs more than the rounds saved.

## Verdicts

The person rules. Record the verdict on its axis, below its lean, keeping everything the axis held, and move the axis under Closed:

```
→ (i). Ratified on 2026-10-29. The person's words, where they gave reasons.
```

- An amendment at ratification is recorded beneath it, in the person's words.
- **A verdict that flips** sweeps the closed axes: walk them for decisions that rested on the old pick, and reopen those that no longer hold. Each amended axis gets a line saying what amended it.
- A verdict whose reach goes past the ticket, binding other packages or later work, is said to be so when it is recorded.

## Into a package

A `write` ticket's architect records ratified verdicts into a package's decisions files, as the definition's grammar writes an entry and its principles' `lifetime` keeps one; whether an entry was ever committed, which `lifetime` turns on, `git log -S'<ID>'` tells. How an entry is compacted from its verdict is in [`architect.md`](architect.md).
