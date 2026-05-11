---
name: git-essentials
description: Essential Git commands and workflows for version control, branching, and collaboration.
homepage: https://git-scm.com/
metadata: {"clawdbot":{"emoji":"🌳","requires":{"bins":["git"]}}}
---

# Git Essentials

Essential Git commands for version control and collaboration.

## Initial Setup

```bash
# Configure user
git config --global user.name "Your Name"
git config --global user.email "your@email.com"

# Initialize repository
git init

# Clone repository
git clone https://github.com/user/repo.git
git clone https://github.com/user/repo.git custom-name
```

## Basic Workflow

### Staging and committing
```bash
# Check status
git status

# Add files to staging
git add file.txt
git add .
git add -A  # All changes including deletions

# Commit changes
git commit -m "Commit message"

# Add and commit in one step
git commit -am "Message"

# Amend last commit
git commit --amend -m "New message"
git commit --amend --no-edit  # Keep message
```

### Viewing changes
```bash
# Show unstaged changes
git diff

# Show staged changes
git diff --staged

# Show changes in specific file
git diff file.txt

# Show changes between commits
git diff commit1 commit2
```

## Branching & Merging

### Branch management
```bash
# List branches
git branch
git branch -a  # Include remote branches

# Create branch
git branch feature-name

# Switch branch
git checkout feature-name
git switch feature-name  # Modern alternative

# Create and switch
git checkout -b feature-name
git switch -c feature-name

# Delete branch
git branch -d branch-name
git branch -D branch-name  # Force delete

# Rename branch
git branch -m old-name new-name
```

### Merging
```bash
# Merge branch into current
git merge feature-name

# Merge with no fast-forward
git merge --no-ff feature-name

# Abort merge
git merge --abort

# Show merge conflicts
git diff --name-only --diff-filter=U
```

## Remote Operations

### Managing remotes
```bash
# List remotes
git remote -v

# Add remote
git remote add origin https://github.com/user/repo.git

# Change remote URL
git remote set-url origin https://github.com/user/new-repo.git

# Remove remote
git remote remove origin
```

### Syncing with remote
```bash
# Fetch from remote
git fetch origin

# Pull changes (fetch + merge)
git pull

# Pull with rebase
git pull --rebase

# Push changes
git push

# Push new branch
git push -u origin branch-name

# Force push (careful!)
git push --force-with-lease
```

## History & Logs

### Viewing history
```bash
# Show commit history
git log

# One line per commit
git log --oneline

# With graph
git log --graph --oneline --all

# Last N commits
git log -5

# Commits by author
git log --author="Name"

# Commits in date range
git log --since="2 weeks ago"
git log --until="2024-01-01"

# File history
git log -- file.txt
```

### Searching history
```bash
# Search commit messages
git log --grep="bug fix"

# Search code changes
git log -S "function_name"

# Show who changed each line
git blame file.txt

# Find commit that introduced bug
git bisect start
git bisect bad
git bisect good commit-hash
```

## Undoing Changes

### Working directory
```bash
# Discard changes in file
git restore file.txt
git checkout -- file.txt  # Old way

# Discard all changes
git restore .
```

### Staging area
```bash
# Unstage file
git restore --staged file.txt
git reset HEAD file.txt  # Old way

# Unstage all
git reset
```

### Commits
```bash
# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1

# Revert commit (create new commit)
git revert commit-hash

# Reset to specific commit
git reset --hard commit-hash
```

## Stashing

```bash
# Stash changes
git stash

# Stash with message
git stash save "Work in progress"

# List stashes
git stash list

# Apply latest stash
git stash apply

# Apply and remove stash
git stash pop

# Apply specific stash
git stash apply stash@{2}

# Delete stash
git stash drop stash@{0}

# Clear all stashes
git stash clear
```

## Rebasing

```bash
# Rebase current branch
git rebase main

# Interactive rebase (last 3 commits)
git rebase -i HEAD~3

# Continue after resolving conflicts
git rebase --continue

# Skip current commit
git rebase --skip

# Abort rebase
git rebase --abort
```

## Tags

```bash
# List tags
git tag

# Create lightweight tag
git tag v1.0.0

# Create annotated tag
git tag -a v1.0.0 -m "Version 1.0.0"

# Tag specific commit
git tag v1.0.0 commit-hash

# Push tag
git push origin v1.0.0

# Push all tags
git push --tags

# Delete tag
git tag -d v1.0.0
git push origin --delete v1.0.0
```

## Advanced Operations

### Cherry-pick
```bash
# Apply specific commit
git cherry-pick commit-hash

# Cherry-pick without committing
git cherry-pick -n commit-hash
```

### Submodules
```bash
# Add submodule
git submodule add https://github.com/user/repo.git path/

# Initialize submodules
git submodule init

# Update submodules
git submodule update

# Clone with submodules
git clone --recursive https://github.com/user/repo.git
```

### Clean
```bash
# Preview files to be deleted
git clean -n

# Delete untracked files
git clean -f

# Delete untracked files and directories
git clean -fd

# Include ignored files
git clean -fdx
```

## Common Workflows

**Feature branch workflow:**
```bash
git checkout -b feature/new-feature
# Make changes
git add .
git commit -m "Add new feature"
git push -u origin feature/new-feature
# Create PR, then after merge:
git checkout main
git pull
git branch -d feature/new-feature
```

**Hotfix workflow:**
```bash
git checkout main
git pull
git checkout -b hotfix/critical-bug
# Fix bug
git commit -am "Fix critical bug"
git push -u origin hotfix/critical-bug
# After merge:
git checkout main && git pull
```

**Syncing fork:**
```bash
git remote add upstream https://github.com/original/repo.git
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

## Useful Aliases

Add to `~/.gitconfig`:
```ini
[alias]
    st = status
    co = checkout
    br = branch
    ci = commit
    unstage = reset HEAD --
    last = log -1 HEAD
    visual = log --graph --oneline --all
    amend = commit --amend --no-edit
```

## Tips

- Commit often, perfect later (interactive rebase)
- Write meaningful commit messages
- Use `.gitignore` for files to exclude
- Never force push to shared branches
- Pull before starting work
- Use feature branches, not main
- Rebase feature branches before merging
- Use `--force-with-lease` instead of `--force`

## Common Issues

**Undo accidental commit:**
```bash
git reset --soft HEAD~1
```

**Recover deleted branch:**
```bash
git reflog
git checkout -b branch-name <commit-hash>
```

**Fix wrong commit message:**
```bash
git commit --amend -m "Correct message"
```

**Resolve merge conflicts:**
```bash
# Edit files to resolve conflicts
git add resolved-files
git commit  # Or git merge --continue
```

## Documentation

Official docs: https://git-scm.com/doc
Pro Git book: https://git-scm.com/book
Visual Git guide: https://marklodato.github.io/visual-git-guide/
