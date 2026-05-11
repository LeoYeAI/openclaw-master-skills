# Advanced Operations

## Interactive Rebase

```bash
git rebase -i HEAD~5        # edit last 5 commits
git rebase -i main          # edit all since diverging from main
```

Commands in editor:
- `pick` = keep as-is
- `reword` = edit message
- `squash` = merge into previous, keep message
- `fixup` = merge into previous, discard message
- `drop` = remove commit

```bash
git rebase --continue       # after resolving conflicts
git rebase --abort          # cancel and restore
git rebase --skip           # skip problematic commit
```

## Bisect (Find Bug)

```bash
git bisect start
git bisect bad              # current has bug
git bisect good v1.0.0      # known good version

# Git checks out middle commit. Test, then:
git bisect good             # no bug here
git bisect bad              # bug here
# Repeat until found

git bisect reset            # done, return to branch
```

Automated bisect:
```bash
git bisect start HEAD v1.0.0
git bisect run ./test-script.sh   # exit 0 = good, 1 = bad
```

## Worktree (Parallel Work)

```bash
git worktree add ../hotfix hotfix-branch   # new dir with branch
git worktree add ../feature -b new-feature # create new branch
git worktree list                          # show all worktrees
git worktree remove ../hotfix              # clean up
```

Use cases:
- Review PR while keeping current work
- Run tests on main while developing
- Compare behavior between versions

## Reflog (Recovery)

```bash
git reflog                  # all HEAD movements
git reflog show branch      # specific branch history
```

Recovery patterns:
```bash
# After bad rebase
git reflog
git reset --hard HEAD@{5}   # go back 5 reflog entries

# Recover deleted branch
git reflog
git branch recovered commit-hash

# Recover dropped stash
git fsck --unreachable | grep commit
```

## Sparse Checkout (Large Repos)

```bash
git sparse-checkout init --cone
git sparse-checkout set packages/my-app packages/shared
git sparse-checkout add packages/another
git sparse-checkout disable         # checkout everything again
```

Clone with sparse:
```bash
git clone --filter=blob:none --sparse URL
cd repo
git sparse-checkout set path/to/need
```

## Subtree vs Submodule

**Subtree** (copies code into repo):
```bash
git subtree add --prefix=lib/shared URL main --squash
git subtree pull --prefix=lib/shared URL main --squash
git subtree push --prefix=lib/shared URL main
```

**Submodule** (pointer to commit):
```bash
git submodule add URL path
git submodule update --init --recursive
git submodule update --remote
```

Choose subtree for: simpler workflow, infrequent updates
Choose submodule for: large deps, independent release cycles

## Merge vs Rebase

**Merge** (preserves history):
```bash
git checkout main
git merge feature           # creates merge commit
git merge --no-ff feature   # always create merge commit
```

**Rebase** (linear history):
```bash
git checkout feature
git rebase main             # replay commits on top of main
git checkout main
git merge feature           # fast-forward
```

Rule: Rebase local unpublished commits. Never rebase published branches.

## Conflict Resolution Tools

```bash
git mergetool               # launch configured tool
git checkout --ours file    # take current branch version
git checkout --theirs file  # take incoming version
```

See all versions:
```bash
git show :1:file            # common ancestor
git show :2:file            # ours
git show :3:file            # theirs
```

## Rerere (Remember Resolution)

```bash
git config --global rerere.enabled true   # remember conflict resolutions
git rerere forget file                    # forget bad resolution
```
