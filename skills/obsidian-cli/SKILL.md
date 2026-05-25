---
name: obsidian-cli
description: Skill for the official Obsidian CLI (v1.12+). Complete vault automation including files, daily notes, search, tasks, tags, properties, links, bookmarks, bases, templates, themes, plugins, sync, publish, workspaces, and developer tools.
version: 2.0.0
author: adolago
tags:
  - obsidian
  - cli
  - notes
  - automation
  - vault
triggers:
  - obsidian
  - vault
  - daily note
  - obsidian cli
---

# Obsidian CLI (Official, v1.12+)

The official Obsidian CLI connects to a running Obsidian instance via IPC.
Requires Obsidian 1.12+ with CLI enabled in Settings > General.

## Prerequisites

- **Obsidian 1.12+** installed and running
- CLI enabled: Settings > General > Enable CLI
- The `obsidian` binary must be in your PATH

**Important**: Obsidian must be running for CLI commands to work. The CLI communicates
with the running instance via IPC.

### Platform Notes

- **macOS/Windows**: The Obsidian installer typically places the CLI binary in PATH automatically.
- **Linux**: You may need a wrapper script to avoid Electron flag injection that breaks CLI arg parsing. Ensure your wrapper is in PATH before the system `obsidian` binary. If running as a service, ensure `PrivateTmp=false` for IPC to work.

## Complete Command Reference

### Basics

```bash
obsidian version                            # Show Obsidian version
obsidian help                               # List all available commands
obsidian vault                              # Show vault info (name, path, files, size)
obsidian vault info=name                    # Just vault name
obsidian vault info=path                    # Just vault path
obsidian reload                             # Reload the vault
obsidian restart                            # Restart the app
```

### Daily Notes

```bash
obsidian daily                              # Open today's daily note
obsidian daily silent                       # Open without focusing
obsidian daily:read                         # Read daily note contents
obsidian daily:append content="- [ ] Task"  # Append to daily note
obsidian daily:prepend content="# Header"   # Prepend to daily note
obsidian daily paneType=tab                 # Open in new tab (tab|split|window)
```

### Files

```bash
obsidian read file=Recipe                   # Read by name (wikilink resolution)
obsidian read path="Work/notes.md"          # Read by exact path
obsidian file file=Recipe                   # Show file info (path, size, dates)
obsidian create name=Note content="Hello"   # Create a new note
obsidian create name=Note template=Travel   # Create from template
obsidian create path="Work/note.md" content="text"  # Create at exact path
obsidian create name=Note overwrite         # Overwrite if exists
obsidian create name=Note silent newtab     # Create silently in new tab
obsidian open file=Recipe                   # Open in Obsidian
obsidian open file=Recipe newtab            # Open in new tab
obsidian delete file=Old                    # Delete (to trash)
obsidian delete file=Old permanent          # Delete permanently
obsidian move file=Old to="Archive/Old.md"  # Move/rename (include .md in target)
obsidian append file=Log content="Entry"    # Append to file
obsidian append file=Log content="text" inline  # Append inline (no newline)
obsidian prepend file=Log content="Header"  # Prepend to file
obsidian unique name="Meeting" content="notes"  # Create note with unique timestamp
obsidian wordcount file=Note                # Word and character count
obsidian wordcount file=Note words          # Words only
obsidian wordcount file=Note characters     # Characters only
obsidian random                             # Open a random note
obsidian random:read                        # Read a random note
obsidian random folder="Work"               # Random note from folder
obsidian recents                            # List recently opened files
obsidian recents total                      # Count of recent files
```

### Search

```bash
obsidian search query="meeting notes"               # Search vault
obsidian search query="TODO" matches                 # Show match context
obsidian search query="project" path="Work" limit=10 # Scoped search
obsidian search query="test" format=json             # JSON output
obsidian search query="Bug" case                     # Case-sensitive search
obsidian search query="error" total                  # Count matches only
obsidian search:open query="TODO"                    # Open search view in Obsidian
```

### Tasks

```bash
obsidian tasks daily                        # Tasks from daily note
obsidian tasks daily todo                   # Incomplete daily tasks
obsidian tasks daily done                   # Completed daily tasks
obsidian tasks all todo                     # All incomplete tasks in vault
obsidian tasks file=Recipe done             # Completed tasks in file
obsidian tasks verbose                      # Tasks with file paths + line numbers
obsidian tasks total                        # Count of tasks
obsidian tasks status="/"                   # Tasks with custom status character
obsidian task daily line=3 toggle           # Toggle task completion
obsidian task daily line=3 done             # Mark task done
obsidian task daily line=3 todo             # Mark task incomplete
obsidian task ref="Work/todo.md:5" toggle   # Toggle by file:line reference
obsidian task daily line=3 status="/"       # Set custom status
```

### Tags & Properties

```bash
# Tags
obsidian tags all counts                    # All tags with counts
obsidian tags all counts sort=count         # Sorted by frequency
obsidian tags file=Note                     # Tags in specific file
obsidian tags total                         # Total tag count
obsidian tag name=project verbose           # Tag details with file list
obsidian tag name=project total             # Count of files with tag

# Properties (frontmatter)
obsidian properties all counts              # All properties with counts
obsidian properties all counts sort=count   # Sorted by frequency
obsidian properties file=Note               # Properties of specific file
obsidian properties name=status             # Files with specific property
obsidian properties format=yaml             # YAML output
obsidian properties format=tsv              # TSV output
obsidian property:read name=status file=Note       # Read a property value
obsidian property:set name=status value=done file=Note  # Set a property
obsidian property:set name=due value="2026-03-01" type=date file=Note  # Set with type
obsidian property:remove name=status file=Note     # Remove a property

# Aliases
obsidian aliases                            # List all aliases in vault
obsidian aliases all                        # Include files without aliases
obsidian aliases file=Note                  # Aliases for specific file
obsidian aliases total                      # Count of aliases
obsidian aliases verbose                    # With file paths
```

### Links & Structure

```bash
obsidian backlinks file=Note                # Files linking to Note
obsidian backlinks file=Note counts         # With link counts
obsidian backlinks file=Note total          # Count of backlinks
obsidian links file=Note                    # Outgoing links from Note
obsidian links file=Note total              # Count of outgoing links
obsidian orphans                            # Files with no incoming links
obsidian orphans total                      # Count of orphans
obsidian orphans all                        # Include non-markdown files
obsidian deadends                           # Files with no outgoing links
obsidian deadends total                     # Count of deadends
obsidian unresolved                         # Broken/unresolved links
obsidian unresolved total                   # Count of unresolved
obsidian unresolved counts                  # With reference counts
obsidian unresolved verbose                 # With source file details
obsidian outline file=Note                  # Headings tree
obsidian outline file=Note format=md        # Headings as markdown
obsidian outline file=Note total            # Count of headings
```

### Vault Info

```bash
obsidian files total                        # File count
obsidian files folder="Work" ext=md         # Filter by folder and extension
obsidian folders                            # List all folders
obsidian folders total                      # Folder count
obsidian folders folder="Work"              # Subfolders of path
obsidian folder path="Work" info=size       # Folder size in bytes
obsidian folder path="Work" info=files      # File count in folder
obsidian folder path="Work" info=folders    # Subfolder count
```

### Bookmarks

```bash
obsidian bookmarks                          # List all bookmarks
obsidian bookmarks total                    # Count of bookmarks
obsidian bookmarks verbose                  # With details
obsidian bookmark file="Work/note.md"       # Bookmark a file
obsidian bookmark file="note.md" subpath="#heading"  # Bookmark a heading
obsidian bookmark folder="Work"             # Bookmark a folder
obsidian bookmark search="TODO"             # Bookmark a search query
obsidian bookmark url="https://example.com" title="Example"  # Bookmark a URL
```

### Bases (Database Views)

```bash
obsidian bases                              # List all base files
obsidian base:views                         # List views in current base
obsidian base:query file=MyBase             # Query base, default format
obsidian base:query file=MyBase format=json # JSON output
obsidian base:query file=MyBase format=csv  # CSV output
obsidian base:query file=MyBase format=tsv  # TSV output
obsidian base:query file=MyBase format=md   # Markdown table
obsidian base:query file=MyBase format=paths  # Just file paths
obsidian base:query file=MyBase view="View Name"  # Query specific view
obsidian base:create name="New Item"        # Create item in current base view
obsidian base:create content="text" silent  # Create silently
```

### Templates

```bash
obsidian templates                          # List available templates
obsidian templates total                    # Count of templates
obsidian template:read name=Daily           # Read template content
obsidian template:read name=Daily resolve   # Read with variables resolved
obsidian template:read name=Daily resolve title="My Note"  # Resolve with title
obsidian template:insert name=Daily         # Insert template into active file
```

### Commands & Hotkeys

```bash
obsidian commands                           # List all command IDs
obsidian commands filter="editor"           # Filter by prefix
obsidian command id=app:open-settings       # Execute a command
obsidian hotkeys                            # List assigned hotkeys
obsidian hotkeys all                        # Include unassigned
obsidian hotkeys total                      # Count of hotkeys
obsidian hotkeys verbose                    # With command details
obsidian hotkey id=app:open-settings        # Hotkey for specific command
obsidian hotkey id=app:open-settings verbose # With full details
```

### Tabs & Workspaces

```bash
# Tabs
obsidian tabs                               # List open tabs
obsidian tabs ids                           # With tab IDs
obsidian tab:open                           # Open new empty tab
obsidian tab:open file="Work/note.md"       # Open file in new tab
obsidian tab:open group=2                   # Open in specific tab group

# Workspaces
obsidian workspaces                         # List saved workspaces
obsidian workspaces total                   # Count of workspaces
obsidian workspace                          # Show current workspace tree
obsidian workspace ids                      # With element IDs
obsidian workspace:save name="coding"       # Save current layout
obsidian workspace:load name="coding"       # Load saved workspace
obsidian workspace:delete name="old"        # Delete saved workspace
```

### History & Diff (File Recovery)

```bash
obsidian history file=Note                  # List version history for file
obsidian history:list                       # List all files with history
obsidian history:read file=Note             # Read latest history version
obsidian history:read file=Note version=3   # Read specific version
obsidian history:restore file=Note version=3  # Restore a version
obsidian history:open file=Note             # Open file recovery UI
obsidian diff file=Note                     # List/diff local versions
obsidian diff file=Note from=1 to=3         # Diff between versions
obsidian diff file=Note filter=local        # Local versions only
obsidian diff file=Note filter=sync         # Sync versions only
```

### Sync (Obsidian Sync)

```bash
obsidian sync:status                        # Show sync status
obsidian sync on                            # Resume sync
obsidian sync off                           # Pause sync
obsidian sync:history file=Note             # Sync version history
obsidian sync:history file=Note total       # Count of sync versions
obsidian sync:read file=Note version=2      # Read a sync version
obsidian sync:restore file=Note version=2   # Restore a sync version
obsidian sync:deleted                       # List files deleted in sync
obsidian sync:deleted total                 # Count of deleted files
obsidian sync:open file=Note               # Open sync history UI
```

### Publish (Obsidian Publish)

```bash
obsidian publish:site                       # Show publish site info
obsidian publish:status                     # List all publish changes
obsidian publish:status new                 # New files to publish
obsidian publish:status changed             # Changed files
obsidian publish:status deleted             # Deleted files
obsidian publish:status total               # Count of changes
obsidian publish:list                       # List published files
obsidian publish:list total                 # Count of published files
obsidian publish:add file=Note              # Publish a file
obsidian publish:add changed                # Publish all changed files
obsidian publish:remove file=Note           # Unpublish a file
obsidian publish:open file=Note             # Open on published site
```

### Themes & CSS Snippets

```bash
# Themes
obsidian theme                              # Show active theme
obsidian theme name="Minimal"               # Get theme info
obsidian themes                             # List installed themes
obsidian themes versions                    # With version numbers
obsidian theme:set name="Minimal"           # Set active theme
obsidian theme:install name="Minimal"       # Install community theme
obsidian theme:install name="Minimal" enable  # Install and activate
obsidian theme:uninstall name="Minimal"     # Uninstall theme

# CSS Snippets
obsidian snippets                           # List installed snippets
obsidian snippets:enabled                   # List enabled snippets
obsidian snippet:enable name="custom"       # Enable a snippet
obsidian snippet:disable name="custom"      # Disable a snippet
```

### Plugins

```bash
obsidian plugins                            # List all installed
obsidian plugins filter=core                # Core plugins only
obsidian plugins filter=community           # Community plugins only
obsidian plugins versions                   # With version numbers
obsidian plugins:enabled                    # List enabled plugins
obsidian plugins:enabled filter=community versions  # Enabled community with versions
obsidian plugins:restrict                   # Check restricted mode status
obsidian plugins:restrict on                # Enable restricted mode
obsidian plugins:restrict off               # Disable restricted mode
obsidian plugin id=dataview                 # Get plugin info
obsidian plugin:enable id=dataview          # Enable plugin
obsidian plugin:disable id=dataview         # Disable plugin
obsidian plugin:install id=dataview         # Install community plugin
obsidian plugin:install id=dataview enable  # Install and enable
obsidian plugin:uninstall id=dataview       # Uninstall community plugin
obsidian plugin:reload id=my-plugin         # Reload plugin (dev)
```

### Web Viewer

```bash
obsidian web url="https://example.com"      # Open URL in web viewer
obsidian web url="https://example.com" newtab  # Open in new tab
```

### Developer Tools

```bash
# JavaScript evaluation
obsidian eval code="app.vault.getFiles().length"  # Run JS in Obsidian context

# Screenshots
obsidian dev:screenshot                     # Screenshot to default path
obsidian dev:screenshot path=screenshot.png # Screenshot to file

# DevTools
obsidian devtools                           # Toggle Electron devtools

# Console & Errors (requires dev:debug on)
obsidian dev:debug on                       # Attach CDP debugger (required for console)
obsidian dev:debug off                      # Detach debugger
obsidian dev:console                        # Show captured console messages
obsidian dev:console limit=10               # Last 10 messages
obsidian dev:console level=error            # Filter by level (log|warn|error|info|debug)
obsidian dev:console clear                  # Clear captured messages
obsidian dev:errors                         # Show captured JS errors
obsidian dev:errors clear                   # Clear errors

# DOM inspection
obsidian dev:dom selector=".workspace"      # Query DOM elements
obsidian dev:dom selector=".nav-file" total # Count matching elements
obsidian dev:dom selector=".nav-file" text  # Get text content
obsidian dev:dom selector=".nav-file" inner # Get innerHTML
obsidian dev:dom selector=".nav-file" all   # All matches
obsidian dev:dom selector="h1" attr=class   # Get attribute
obsidian dev:dom selector="h1" css=color    # Get CSS property

# CSS inspection
obsidian dev:css selector=".workspace"      # Inspect CSS with source locations
obsidian dev:css selector=".workspace" prop=background  # Specific property

# Chrome DevTools Protocol
obsidian dev:cdp method="Page.getLayoutMetrics"  # Raw CDP command
obsidian dev:cdp method="Runtime.evaluate" params='{"expression":"1+1"}'

# Mobile emulation
obsidian dev:mobile on                      # Enable mobile emulation
obsidian dev:mobile off                     # Disable mobile emulation
```

### Multi-Vault

```bash
obsidian vaults                             # List known vaults
obsidian vaults verbose                     # With paths
obsidian vaults total                       # Count of vaults
obsidian vault=Notes daily                  # Target specific vault
obsidian vault=Notes search query="test"    # Search in specific vault
```

## Parameter Syntax

- `param=value` for parameters (quote spaces: `content="Hello world"`)
- Bare words for flags: `obsidian tasks daily todo verbose`
- Multiline: use `\n` for newline, `\t` for tab
- `file=<name>` resolves like wikilinks (name only, no path/extension needed)
- `path=<path>` requires exact path from vault root
- `vault=<name>` must be the FIRST parameter to target a specific vault

## Targeting Vaults

- If CWD is inside a vault, that vault is used
- Otherwise, the active vault is used
- Use `vault=<name>` as FIRST parameter to target a specific vault

## Troubleshooting

- **"Cannot connect"**: Ensure Obsidian is running and CLI is enabled in Settings > General.
- **"Command not found"**: Ensure the `obsidian` binary is in your PATH.
- **Linux IPC issues**: If running headless or as a service, ensure the IPC socket is accessible (no `PrivateTmp`, correct user context).
- **Electron flag conflicts (Linux)**: Use a wrapper script that omits electron-flags.conf for CLI invocations.

## Notes

- CLI connects to running Obsidian via IPC singleton lock
- For non-interactive use (scripts/cron), ensure Obsidian is running first
- `move` requires the full target path including `.md` extension
- `folders` can be slow on large vaults (19k+ files)
- `dev:console` requires `dev:debug on` to be run first
