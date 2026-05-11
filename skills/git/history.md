# History Traps

## Reset

- `git reset --hard` loses uncommitted changes PERMANENTLY — no undo
- `--hard` vs `--soft` vs `--mixed` — each moves different things
- Reset of pushed commit = history diverges — you need force push
- Reset with untracked files = untracked survive — can surprise you

## Revert

- Revert creates NEW commit — doesn't delete the original
- Revert of merge commit needs `-m 1` or `-m 2` — without it, error
- Revert of revert = re-applies changes — confusing history
- Revert of old commit can conflict with later commits

## Amend

- `--amend` changes SHA — amended commit is DIFFERENT commit
- Amend of pushed commit = same problems as rebase
- `--amend` without staging = only changes message
- Accidental amend on wrong commit = use reflog to recover

## Reflog

- Reflog is LOCAL — doesn't sync with remote
- Reflog expires (default 90 days) — old commits lost
- `git gc` can clean unreachable commits before expiration
- Reflog of deleted branch is in HEAD reflog, not branch reflog

## Cherry-pick

- Cherry-pick creates new commit with different SHA
- Cherry-picking then merging = duplicate commits in history
- Cherry-pick of merge commit needs `-m` flag
- Conflicts in cherry-pick = resolve same as rebase

## Blame

- `git blame` shows last change, not original author
- Blame ignores whitespace changes with `-w`
- `git log -p filename` shows full history of changes
- Blame on moved code: use `git log --follow` for renamed files
