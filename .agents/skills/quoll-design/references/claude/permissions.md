# Claude Code tool permissions

This reference applies only to Claude Code. The rest of `quoll-design` is agent-agnostic. For other agents, users configure tool permissions in their own harness; neither role prompts nor this guidance grants permissions there.

Claude Code permissions are a safety measure against unintended actions, not a security boundary against a malicious agent. An allowed script can execute arbitrary code with the user's authority, and an allowed command prefix can admit options that were not anticipated. Use OS-level sandboxing where filesystem or network containment is required.

## Where rules live

- `~/.claude/settings.json` holds personal rules for every project. Use it for repository-independent authoring and inspection.
- `.claude/settings.json` holds shared rules for one repository and is committed. Use it for the project's known development commands; the main agent and subagents inherit these rules.
- `.claude/settings.local.json` holds personal rules for one repository and is not committed. Use it for a finite task's exact commands or personal additions.
- `claude --settings <file>` supplies rules to a new CLI session; it does not change an existing VSCode conversation.

Claude Code merges allow rules across settings files. Deny and ask rules retain precedence over allow rules, including approvals returned by hooks. Narrow allow rules resolve before the auto-mode classifier unless `autoMode.classifyAllShell` is enabled. Settings-file edits are watched and normally reloaded without a restart.

The `.claude` directory is protected. In auto mode, an agent's write to a settings file routes to the classifier, so a person applies a proposed settings batch in the editor rather than having the agent activate it. The VSCode Permissions interface is another way to add rules.

## Recommended global authoring rules

This closed set covers ordinary local authoring, branch creation and switching, reset/history operations, current-branch publication, issue/PR authorship and editing, and common read-only GitHub inspection. Issue and PR editing includes milestone assignment. It deliberately excludes releases, closures, milestone creation or editing, broad `gh api`, and arbitrary interpreters. Native rules also apply to subagents; their role instructions still govern whether they should attempt an authoring action.

```json
{
  "permissions": {
    "allow": [
      "Bash(git add *)",
      "Bash(git commit *)",
      "Bash(git switch *)",
      "Bash(git reset *)",
      "Bash(git push)",
      "Bash(git push origin HEAD)",
      "Bash(git push -u origin HEAD)",
      "Bash(gh issue create *)",
      "Bash(gh issue edit *)",
      "Bash(gh pr create *)",
      "Bash(gh pr edit *)",
      "Bash(gh issue list *)",
      "Bash(gh issue view *)",
      "Bash(gh pr list *)",
      "Bash(gh pr view *)",
      "Bash(gh pr diff *)",
      "Bash(gh pr checks *)",
      "Bash(gh release list *)",
      "Bash(gh release view *)",
      "Bash(gh repo view *)"
    ]
  }
}
```

Ordinary publication uses only the three exact forms `git push`, `git push origin HEAD`, and `git push -u origin HEAD`. Other remotes, refs, tag pushes, and option-bearing pushes use the normal permission path or an exact task-local rule. Commit amend and `git switch *` are intentionally allowed as routine local authoring; the agent inspects the worktree first, asks about uncommitted work, and never silently force-switches or discards changes. These permissions do not provide a security boundary against destructive switch options.

Commit amend, `git switch *`, and `git reset *` are intentionally allowed as routine local authoring. The agent inspects the worktree first, asks about uncommitted work, and never silently force-switches, hard-resets, or otherwise discards changes. These permissions do not provide a security boundary against destructive options; an agent can also rewrite files directly. The safeguard is the agent-agnostic worktree guidance and the person's review, not a classifier.

The closing workflow still uses `git reset --soft <commit-before-ticket>` for its squash because that is the correct operation, not because other reset modes have a separate permission guard. Broad `git checkout *` is not included: use `git switch` for branch operations, because checkout also addresses and overwrites paths.

Merge these entries with existing settings; never replace an existing allow or ask array wholesale. Add no blanket `Bash(git *)`, `Bash(gh *)`, `Bash(python*)`, or `Bash(gh api *)` rule.

## Project development commands

Commit a closed inventory of the commands the repository's actual workflow uses. Prefer an exact script path or named test/build command with a trailing wildcard for its documented arguments and output redirection. Do not infer a standing rule from a one-off historical invocation, and do not allow a bare interpreter, package runner, migration shim, or temporary codemod.

For example, a repository-specific rule has this form:

```json
"Bash(python3 -I path/to/check.py package *)"
```

The trailing wildcard also matches the command without further arguments. Claude Code checks every part of a compound command separately, so the prefix does not approve an appended unrelated command. File writes and redirections still follow the applicable path rules.

Use `.claude/settings.local.json` for a command needed only for the current task. If an invocation does not match a rule, it follows the normal classifier or prompt path; add it deliberately rather than broadening an existing rule.

## Exact batches for management tasks

For a finite management task, draft fully literal commands and exact `Bash(...)` rules with no wildcard. The person reviews and applies the batch to `.claude/settings.local.json`; applying it is the approval. The agent then executes only those commands verbatim. A changed parameter or quoting is a different command and needs another rule.

A `*` anywhere in a Bash rule is a wildcard, including inside shell quotes. If a command contains one, do not describe the rule as exact: rewrite the command to avoid it or use the ordinary approval path.

See [the release workflow](../release.md) for preflight, the completed/missing action record, interruption, retry, and cleanup. Provider-specific classifier setup is separate, including [the Kimi under Claude Code note](kimi.md).
