# The final review of a ticket

You review the change that closes a ticket, fresh, before it is pushed: the repository is public, so a push publishes it, and your review decides whether it may be. You read it as its readers will, with the issue, the branch and the repository, and nothing of the conversation that made it.

## You read

- the issue, with `gh issue view <n> --comments`, and every design it links;
- the change, with `git diff main..<branch>`, and every file it adds or changes, as it stands on the branch; from your second round on, also the commits since the last one you reviewed, each round's fixes being a commit of its own;
- the ticket baseline and the frozen round check and review summaries your prompt names, including their decision-lifetime, closed-change, and non-finding records, without treating those summaries as evidence you need not verify;
- the draft of its pull request's body, `pr.md` in the ticket's working directory, `.quoll-wip/<issue>-<topic>/`;
- [`AGENTS.md`](../../../../AGENTS.md), this skill, and [`writing.md`](writing.md);
- the definition's parts the change touches;
- what the person gives you to tell what is private: notes, a list, or an agent's memory.

## You check, in this order

1. **Leaks**: every line of the change and of `pr.md`, for anything private to the project's people or business: a name of a person other than a contributor's public handle, of a company, a client or a partner; a deal, money, a business stage or plan; a private project, document or path; an ID or the content of the private working records under `.quoll-wip/`; and a rule whose wording gives away a private incident it came from. Judge implied leaks as well as named ones.
2. **The ticket**: each of the issue's requirements, one by one, met, partly met, or not; and nothing done that it does not ask.
3. **The changed items and their consumers**: inspect the target changes and every declared dependent before reviewing whole-package consistency; each necessary consumer was revisited, and no unrelated change was introduced to make a chunk pass.
4. **The checks**: run `check_package.py` for each changed v0.4 package with `--base <ticket baseline>` and the declared materialized dependencies, and run `check_blocks.py` for its view blocks. Run `check_bare.py` or a review-mode pass only for a named targeted question, never as a broad lexical-advisory gate. Do not use `check_part.py`, manual interface-name arguments, or header/body concatenation. Judge high-confidence diff-scoped output against the current source; an intentional full-current `check_package.py` run may supplement, but does not replace, the baseline comparison.
5. **The language**: every file changed follows the definition, its grammar above all; every reference lands; the definition is linked, never restated.
6. **Its decisions and their lifetime**: the active entries `pr.md` names are well formed, consistent with the items that state them and with each other; each superseded entry is a titleless pointer-only stub retaining its stable ID and only `*Superseded by* NEW-ID`, with no heading, `*Stated by*`, reasons, or other active-decision fields, and its active successor carries the superseded alternative under `*Rejected*`; old prose remains in Git history; each added, amended, moved, superseded, or restored entry follows `lifetime` from its committed history; every relevant round recorded decision-lifetime and closed-change results and revisited dependents before final review; converting a full superseded entry to its pointer-only stub is valid history migration rather than a changed active choice, while changing the successor's active choice is a closed change; the final source and its component decisions are committed together, with no working `decisions.md` or throwaway Quoll among them.
7. **The conventions** of `AGENTS.md`: the branch, the commit messages, no agent's trailer, Markdown unwrapped.
8. **Its report**: `pr.md` says the roles run, their rounds, the agent and model of each, and what the guidance left unanswered.

A diagnostic is not automatically a finding. Record a rejected line as a non-finding with its reason where it is a pre-existing baseline state, restored history, valid full-to-pointer history migration, a known checker limitation, a word used in another sense, or outside the ticket's scope; require independent current-source evidence before making one a source defect.

## You write

Your findings to `review.md` in the ticket's working directory, numbered `FN<issue>-<n>`, as `FN2-1`: one per finding, each with its place, what is wrong, which check it fails, a suggested fix, and *blocking* or *minor*; any leak is *blocking*. Under a separate `Non-findings` heading, record each rejected diagnostic with its reason. Change no other file, push nothing, and post nothing.

## You report

The number of findings, blocking and minor, a sentence on each blocking one, the number of documented non-findings, and whether the branch may be pushed once they are answered.
