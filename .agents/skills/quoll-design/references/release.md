# Publishing a release

Work a `release` ticket with the person. A release without source changes needs no source pull request and no independent release reviewer. For Claude Code, use [the Claude Code permissions guidance](claude/permissions.md) for the exact local approval batch; no executor or custom hook is needed. For other agents, the person configures equivalent exact-command permissions in that harness; this workflow does not prescribe its settings files, and role prompts grant no permissions.

## Select, inspect, and approve

1. Confirm that all source changes are merged. Select the exact full release commit and package scope from the issue and workspace decisions. Set the Git remote, GitHub repository and release issue:
   ```sh
   remote=origin
   repository=rete-labs/quoll
   issue='<release-issue-number>'
   commit='<exact-full-release-commit>'
   ```
2. For each selected package, set its repository-relative package path and canonical semantic version, then derive its literal tag and package-version title:
   ```sh
   package=language
   version=v0.4.0
   tag="$package/$version"
   title="${package##*/} $version"
   paragraph='<one plain-text paragraph of semantic package changes>'
   ```
   Write its `paragraph` as exactly one plain-text paragraph of semantic package changes: no title duplication, commit list, Markdown structure, links, cross-references or coordination metadata. Do not create a notes file or release TOML.
3. Preflight local CLI compatibility before drafting the write batch:
   ```sh
   git --version
   gh --version
   gh release create --help
   gh issue close --help
   gh api --help
   ```
   Confirm that the installed versions support every planned command and flag. Milestone operations use `gh api`; do not assume that a `gh milestone` command exists.
4. Read the selected manifests' `dependencies` and order dependencies before dependents where applicable. Inspect every package's existing local tag, remote tag and host release before creating anything:
   ```sh
   git tag --list "$tag"
   git ls-remote --tags "$remote" "refs/tags/$tag" "refs/tags/$tag^{}"
   gh release view "$tag" --repo "$repository" --json tagName,targetCommitish,name,body,isPrerelease,isDraft
   ```
   A not-found result is expected for a new piece. If the remote tag exists but the local tag does not, fetch exactly that tag into the same local ref, without force or unrelated tags:
   ```sh
   git fetch --no-tags "$remote" "refs/tags/$tag:refs/tags/$tag"
   ```
   For every existing local tag, including one just fetched, use `git show --no-patch "$tag"` to inspect its type, full target and complete message, and `git rev-parse "$tag" "$tag^{}"` to read its object and peeled IDs. Compare every existing piece with the intended annotated tag, full commit, paragraph, title and prerelease state; an existing host release must also have `isDraft` equal to false. Compare local and remote tag object IDs and peeled commits so that a different remote object stops the release even when a local tag already exists. Skip only exact matches; any mismatch stops for the person. Never move, edit, delete, overwrite or automatically repair existing state.
5. Inspect the release issue and its milestone. Read the milestone number from the issue and query its current state and open-issue count:
   ```sh
   gh issue view "$issue" --repo "$repository" --json number,state,title,milestone
   gh api "repos/$repository/milestones/$milestone"
   ```
   The milestone is closed only after the release issue and every other issue in it are closed. An absent milestone needs no closure action.
6. In the ticket's working directory, write `actions.md`: every write action by a stable name, its fully literal command, and its status as missing, completed, mismatched, failed, or unknown after interruption. Derive missing actions from the inspection above. Record read-only verification separately; it does not depend on write approval.
7. Draft the write commands in dependency order, using the forms below with every placeholder replaced by its approved literal value:
   ```sh
   git tag -a --cleanup=verbatim -m '<paragraph>' '<tag>' '<commit>'
   git push '<remote>' 'refs/tags/<tag>'
   gh release create '<tag>' --repo '<repository>' --verify-tag --target '<commit>' --title '<title>' --notes-from-tag
   gh issue close '<issue>' --repo '<repository>'
   gh api --method PATCH 'repos/<repository>/milestones/<milestone>' -f state=closed
   ```
   Add `--prerelease` to a host-release command only when the canonical version has a prerelease suffix. Add no Latest policy or other metadata. Do not execute the closure commands at this stage; their conditions are checked below.
8. For Claude Code, draft one exact local allow rule for each literal write command as `Bash(<literal-command>)`, with no wildcard. Show the person the exact full commit, every literal tag and title, every complete paragraph, the ordered write commands, and the corresponding rule batch. The person reviews and merges the batch into `.claude/settings.local.json` in the editor, preserving existing entries, and saves it. Applying the batch is the explicit approval; the agent does not edit the protected settings file in auto mode. Under another harness, the person applies the equivalent reviewed commands through that harness's own permission mechanism.
9. Execute each command exactly as approved: no variables, changed quoting, added flags, or substituted parameters. A `*` anywhere in a rule is a wildcard, even inside shell quotes, so a command containing one must be rewritten without it or left to the ordinary approval path. Any changed command requires a new exact rule. Deny and ask rules still take precedence, and no approval is cached across a different command.

## Publish and record

Work through the packages in dependency order, creating only missing pieces.

1. Confirm that the exact command is marked missing in `actions.md`, run it, and record its result. Never run an action already completed or one whose current state mismatches the approved target.
2. Create a local annotated tag with the approved paragraph and commit only when no exact remote tag already stands; reuse an exact fetched tag rather than recreating it. Push a missing remote tag exactly, without force. Create a missing host release from the tag. The approved literal commands above are the only write forms used.
3. After each command, update its status and the observed result in `actions.md`. A failed or interrupted command is not assumed to have had no effect: mark it failed or unknown, stop the sequence, and reinspect before doing anything else.
4. If the classifier is unavailable for an unapproved write, that write remains unexecuted. Stop and present the consolidated exact-rule batch or one retry point; do not retry each subaction into repeated stalls. An explicit denial stops the affected action: do not rename, rewrite, or reach it by another route.
5. On retry, repeat every inspection and update `actions.md` with completed and missing pieces. Exact existing pieces stand; any mismatch stops for the person. Run only missing commands whose unchanged exact rules remain in local settings. If the intended action changed, draft its new rule and obtain another batch approval. Remove the task's exact rules from local settings when the release is complete; the person applies that cleanup.

## Verify and close

1. Verify each remote tag object and its peeled full commit:
   ```sh
   git ls-remote --tags "$remote" "refs/tags/$tag" "refs/tags/$tag^{}"
   ```
   Compare the tag object with `git rev-parse "$tag"` and the peeled ref with the approved full commit.
2. Verify each host release:
   ```sh
   gh release view "$tag" --repo "$repository" --json tagName,targetCommitish,name,body,isPrerelease,isDraft
   ```
   Check the literal tag, full target, title and body against the approved values; `isPrerelease` must reflect only the version's prerelease suffix, and `isDraft` must be false.
3. Only after every package verifies, run the approved literal issue-closure command. Verify that the issue is closed and inspect the milestone again:
   ```sh
   gh issue view "$issue" --repo "$repository" --json number,state,milestone
   gh api "repos/$repository/milestones/$milestone"
   ```
4. Close the milestone only when its current `open_issues` is zero and its state is open. Run the approved literal `gh api --method PATCH ... -f state=closed` command, then query the milestone again and record `state=closed`. If issues remain open, leave the milestone open and stop for the person.
5. Record every completed and remaining action in `actions.md`, perform the final read-only verification independently of the now-finished write approvals, and ask the person to remove the task's exact local rules.
