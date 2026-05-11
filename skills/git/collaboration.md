# Collaboration Traps

## Push/Pull

- `git pull` = fetch + merge — can create unexpected merge commits
- `git pull --rebase` avoids merge commits but can have conflicts
- Push rejected for non-fast-forward ≠ you need force — pull first
- `--force` overwrites others' history — `--force-with-lease` is safer

## Force Push

- `--force` ignores others' changes — coworkers' commits lost
- `--force-with-lease` fails if remote changed — safer but not foolproof
- Force push to main/master = broken CI/CD references, failed deploys
- Branch protection on GitHub/GitLab prevents force push — always configure

## Remote Branches

- `git fetch` doesn't update working directory — only refs
- Branch tracking doesn't update automatically if remote renames
- `origin` is convention, not requirement — other remotes can exist
- `git remote prune origin` cleans refs but not local branches

## Code Review

- Push during review = new commits not necessarily reviewed
- Force push during review = diff changes, comments may become obsolete
- Approve before CI complete = bugs merged
- Squash merge loses individual commit history

## Team Coordination

- Multiple people on same branch = constant conflicts
- No branch naming convention = chaos in long-running projects
- Forgetting to pull before starting work = divergent history
- Rebasing shared branch without warning = teammates' work broken
