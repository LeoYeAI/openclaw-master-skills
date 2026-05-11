# Branching Traps

## Branch Creation

- `git checkout -b feature` from wrong branch = incorrect base
- `git branch feature` without checkout = you stay on previous branch — commits go there
- Branch name with spaces fails silently in some tools
- `/` in branch name (feature/x) = some systems see it as directory

## Switching

- `git checkout branch` with uncommitted changes = they may go to new branch — confusing
- `git switch` is safer but `-f` loses changes without warning
- Auto stash doesn't exist — tracked changes are blocking, untracked get mixed
- Checkout of branch with different submodule = submodule stays in previous state

## Merge

- Fast-forward merge doesn't create merge commit — linear history but no context
- `--no-ff` always creates merge commit — useful for features, noise for fixes
- Merge of long branch = mega merge commit hard to review/revert
- Branch deleted after merge = orphan commits if no tag

## Rebase

- Rebase of published branch = different history = others must `--force` pull
- Bad interactive rebase can lose commits — use reflog to recover
- Conflicts in rebase: resolve EACH commit, not just once
- Rebase changes SHAs — CI/CD references to old commits broken

## Remote Tracking

- `git push -u origin feature` needed first time — without `-u` it doesn't track
- Remote branch deleted doesn't delete local tracking — `git fetch --prune` to clean
- `git pull` without upstream configured = error — `git branch --set-upstream-to`
- Remote rename doesn't update tracking branches — reconfigure manually

## Naming Conventions

- Same branch in two remotes (origin/main, upstream/main) = confusion
- Branch name case-insensitive on Mac/Windows, sensitive on Linux — CI bugs
- Branch named same as tag = ambiguity in some commands
