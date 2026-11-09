# Publishing a release

Work a `release` ticket with the person. A release without source changes needs no source pull request and no independent release reviewer.

## Select and approve

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
3. Read the selected manifests' `dependencies` and order dependencies before dependents where applicable. Inspect every package's existing local tag, remote tag and host release before creating anything:
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
4. Show the person the exact full commit, every literal tag and title, and every complete paragraph. Obtain explicit approval before any push.

## Publish

Work through the packages in dependency order, creating only missing pieces.

1. Create a local annotated tag with the approved paragraph and commit only when no exact remote tag already stands; reuse an exact fetched tag rather than recreating it:
   ```sh
   git tag -a --cleanup=verbatim -m "$paragraph" "$tag" "$commit"
   ```
2. Push a missing remote tag exactly, without force:
   ```sh
   git push "$remote" "refs/tags/$tag"
   ```
3. Create a missing host release from the tag:
   ```sh
   gh release create "$tag" --repo "$repository" --verify-tag --target "$commit" --title "$title" --notes-from-tag
   ```
   Add `--prerelease` to that command only when the canonical version has a prerelease suffix. Add no Latest policy or other metadata.
4. On retry, repeat the inspection and continue only with missing pieces; exact existing pieces stand, and any mismatch stops for the person.

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
3. Only after every package verifies, close the release issue:
   ```sh
   gh issue close "$issue" --repo "$repository"
   ```
   Close the milestone only when no open issues remain in it.
