# Essential Commands

## Setup

```bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
git init
git clone https://github.com/user/repo.git
```

## Daily Workflow

```bash
git status
git add file.txt
git add .
git commit -m "feat: add feature"
git commit -am "fix: quick fix"
git push
git pull --rebase
```

## Viewing Changes

```bash
git diff                    # unstaged changes
git diff --staged           # staged changes
git log --oneline -10       # recent commits
git log --graph --all       # visual history
git show commit-hash        # specific commit
git blame file.txt          # who changed each line
```

## Staging

```bash
git add -p                  # interactive staging (partial files)
git restore --staged file   # unstage
git restore file            # discard changes
git reset                   # unstage all
```

## Stashing

```bash
git stash                   # save work temporarily
git stash -m "wip: feature" # with message
git stash list              # see stashes
git stash pop               # apply and remove
git stash apply             # apply and keep
git stash drop              # remove without applying
```

## Tags

```bash
git tag                     # list tags
git tag v1.0.0              # lightweight tag
git tag -a v1.0.0 -m "msg"  # annotated tag
git push origin v1.0.0      # push single tag
git push --tags             # push all tags
git tag -d v1.0.0           # delete local
git push origin --delete v1.0.0  # delete remote
```

## Remote Operations

```bash
git remote -v               # list remotes
git remote add origin URL   # add remote
git fetch origin            # download without merge
git push -u origin branch   # push and track
git push --force-with-lease # safe force push
```

## Undoing

```bash
git reset --soft HEAD~1     # undo commit, keep changes staged
git reset --mixed HEAD~1    # undo commit, keep changes unstaged
git reset --hard HEAD~1     # undo commit, discard changes
git revert commit-hash      # create undo commit
git checkout -- file        # discard file changes (old)
git restore file            # discard file changes (new)
```

## Cherry-pick

```bash
git cherry-pick commit-hash     # apply specific commit
git cherry-pick -n commit-hash  # apply without committing
git cherry-pick --abort         # cancel in progress
```

## Clean

```bash
git clean -n                # preview what will be deleted
git clean -f                # delete untracked files
git clean -fd               # delete untracked files and dirs
git clean -fdx              # also delete ignored files
```

## Submodules

```bash
git submodule add URL path  # add submodule
git submodule update --init # initialize after clone
git clone --recurse-submodules URL  # clone with submodules
git submodule update --remote       # update to latest
```

## Aliases (add to ~/.gitconfig)

```ini
[alias]
    st = status
    co = checkout
    br = branch
    ci = commit
    lg = log --oneline --graph --all
    amend = commit --amend --no-edit
    unstage = reset HEAD --
```
