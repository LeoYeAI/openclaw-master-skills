# Conflict Traps

## Detection

- Binary file conflict = git can't show diff — choose complete version
- "Both modified" vs "both added" conflict — different resolution expected
- Renamed + modified file = git may not detect rename — false conflict
- Whitespace-only conflicts hidden if diff ignores whitespace

## Resolution

- Markers `<<<<<<<` forgotten in code = compiles but code is broken
- Resolve "accept theirs" but needed "accept ours" = hard to undo
- Merge commit with badly resolved conflict = bug introduced silently
- `git checkout --ours` during rebase = inverted semantics vs merge

## During Rebase

- Each commit can have different conflicts — resolve N times, not 1
- Skip commit during rebase = commit lost without clear warning
- `--continue` without resolving everything = error, no partial merge
- Abort rebase after several commits = back to start, work lost

## Tool Issues

- External merge tool may not save = git thinks you resolved but file unchanged
- Merge tool that deletes markers but doesn't combine code = silently wrong
- `git mergetool` generates `.orig` backups that can be committed by mistake
- Three-way merge tools: "local/remote/base" confusing during rebase (inverted)

## Prevention

- Pull frequently to avoid large divergences
- Small, focused commits = smaller conflicts
- Communicate with team about which files you're editing
- Use `git diff main` before merging to preview conflicts
