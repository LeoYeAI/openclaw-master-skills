---
name: file-search
description: "Fast file-name and content search using `fd` and `rg` (ripgrep)."
metadata:
  {
    "openclaw":
      {
        "emoji": "🔍",
        "requires": { "bins": ["fd", "rg"] },
        "install":
          [
            {
              "id": "dnf-fd",
              "kind": "dnf",
              "package": "fd-find",
              "bins": ["fd"],
              "label": "Install fd-find (dnf)",
            },
            {
              "id": "dnf-rg",
              "kind": "dnf",
              "package": "ripgrep",
              "bins": ["rg"],
              "label": "Install ripgrep (dnf)",
            },
          ],
      },
  }
---

# File Search Skill

Fast file-name and content search using `fd` and `rg` (ripgrep).

## Find Files by Name

Search for files matching a pattern:

```bash
fd "\.rs$" /home/xrx/projects
```

Find files by exact name:

```bash
fd -g "Cargo.toml" /home/xrx/projects
```

## Search File Contents

Search for a regex pattern across files:

```bash
rg "TODO|FIXME" /home/xrx/projects
```

Search with context lines:

```bash
rg -C 3 "fn main" /home/xrx/projects --type rust
```

## Install

```bash
sudo dnf install fd-find ripgrep
```
