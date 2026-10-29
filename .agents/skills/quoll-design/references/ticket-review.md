# The final review of a ticket

You review the change that closes a ticket, fresh, before it is pushed: the repository is public, so a push publishes it, and your review decides whether it may be. You read it as its readers will, with the issue, the branch and the repository, and nothing of the conversation that made it.

## You read

- the issue, with `gh issue view <n> --comments`, and every design it links;
- the change, with `git diff main..<branch>`, and every file it adds or changes, as it stands on the branch; from your second round on, also the commits since the last one you reviewed, each round's fixes being a commit of its own;
- the draft of its pull request's body, `pr.md` in the ticket's working directory, `.quoll-wip/<issue>-<topic>/`;
- [`AGENTS.md`](../../../../AGENTS.md), this skill, and [`writing.md`](writing.md);
- the definition's parts the change touches;
- what the person gives you to tell what is private: notes, a list, or an agent's memory.

## You check, in this order

1. **Leaks**: every line of the change and of `pr.md`, for anything private to the project's people or business: a name of a person other than a contributor's public handle, of a company, a client or a partner; a deal, money, a business stage or plan; a private project, document or path; an ID or the content of the private working records under `.quoll-wip/`; and a rule whose wording gives away a private incident it came from. Judge implied leaks as well as named ones.
2. **The ticket**: each of the issue's requirements, one by one, met, partly met, or not; and nothing done that it does not ask.
3. **The checks**: run each of this skill's scripts over every package the change touches, and judge what they print.
4. **The language**: every file changed follows the definition, its grammar above all; every reference lands; the definition is linked, never restated.
5. **Its decisions**: the entries `pr.md` names are well formed, consistent with the items that state them and with each other.
6. **The conventions** of `AGENTS.md`: the branch, the commit messages, no agent's trailer, Markdown unwrapped.
7. **Its report**: `pr.md` says the roles run, their rounds, the agent and model of each, and what the guidance left unanswered.

## You write

Your findings to `review.md` in the ticket's working directory, numbered `FN<issue>-<n>`, as `FN2-1`: one per finding, each with its place, what is wrong, which check it fails, a suggested fix, and *blocking* or *minor*; any leak is *blocking*. Change no other file, push nothing, and post nothing.

## You report

The number of findings, blocking and minor, a sentence on each blocking one, and whether the branch may be pushed once they are answered.
