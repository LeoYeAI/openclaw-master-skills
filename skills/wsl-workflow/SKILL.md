---
name: wsl-workflow
description: "Use when working inside WSL (Windows Subsystem for Linux). Path translation, Windows interop, clipboard, port forwarding, and filesystem quirks."
version: 1.0.0
author: Papi
license: MIT
metadata:
  hermes:
    tags: [wsl, windows, linux, filesystem, interop]
    related_skills: []
---

# WSL Workflow

## Overview

Everything you need to navigate the WSL/Windows boundary. Path translation, running Windows binaries, clipboard access, port forwarding, filesystem performance, and the quirks that bite you when you forget you're in a compatibility layer.

## When to Use

- User references Windows paths (C:\, Desktop, Documents, Downloads)
- Need to access or modify files on the Windows host from WSL
- Need to run a Windows .exe from within WSL
- Clipboard operations between WSL and Windows
- Port forwarding or networking between WSL and Windows
- Performance issues with filesystem operations in WSL

Don't use for:
- Pure Linux tasks that never touch Windows — just use standard Linux commands
- Docker Desktop WSL2 backend issues (use docker-ops skill instead)

## Path Translation

| Windows Path | WSL Path |
|---|---|
| `C:\Users\Name\Desktop\file.txt` | `/mnt/c/Users/Name/Desktop/file.txt` |
| `D:\Projects\app` | `/mnt/d/Projects/app` |
| `\\wsl$\Ubuntu\home\user\file` | `/home/user/file` (access from Windows) |
| `\\wsl.localhost\Ubuntu\home\user` | `/home/user/file` (Windows 11+) |

### Discovering the Windows Username

```bash
ls /mnt/c/Users/ | grep -v -E 'Public|Default|All Users|Default User|desktop.ini'
```

### Quick Path Helpers

```bash
# Windows Desktop from WSL
DESKTOP="/mnt/c/Users/$(ls /mnt/c/Users/ | grep -v -E 'Public|Default|All Users|Default User|desktop.ini' | head -1)/Desktop"

# Windows Downloads
DOWNLOADS="/mnt/c/Users/$(ls /mnt/c/Users/ | grep -v -E 'Public|Default|All Users|Default User|desktop.ini' | head -1)/Downloads"
```

## Running Windows Executables from WSL

WSL2 can run .exe files directly:

```bash
# Open a file with the default Windows app
/mnt/c/Windows/System32/cmd.exe /c start "" "/mnt/c/Users/Name/file.pdf"

# Use explorer.exe to open current directory in Windows Explorer
explorer.exe .

# Open a URL in Windows default browser
/mnt/c/Windows/System32/cmd.exe /c start "" "https://example.com"

# Run PowerShell
powershell.exe -Command "Get-Process"

# Run cmd
cmd.exe /c "dir C:\\"

# Use Windows Python
/mnt/c/Users/Name/AppData/Local/Programs/Python/python.exe script.py
```

## Clipboard Operations

```bash
# Copy to Windows clipboard
echo "hello" | clip.exe

# Pipe Windows clipboard to WSL
powershell.exe -Command "Get-Clipboard" | tail -n +1

# Copy file contents to clipboard
cat file.txt | clip.exe

# Alternative: use xclip if installed (works with X forwarding)
echo "hello" | xclip -selection clipboard
```

## Port Forwarding & Networking

WSL2 uses a virtual network adapter. Key points:

```bash
# Get the WSL2 IP address
ip addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}'

# Get the Windows host IP from within WSL
cat /etc/resolv.conf | grep nameserver | awk '{print $2}'

# Access a WSL server from Windows
# Usually auto-forwarded: localhost:PORT on Windows → WSL
# If not working, try:
WIN_IP=$(cat /etc/resolv.conf | grep nameserver | awk '{print $2}')
# Then access via $WIN_IP:PORT from Windows

# Mirror mode (Windows 11 22H2+): add to ~/.wslconfig
# [wsl2]
# networkingMode=mirrored
```

## Filesystem Performance

**Critical rule:** Cross-filesystem access (Windows files from WSL, or WSL files from Windows) is 3-5x slower than native.

### Best Practices

1. **Work in the Linux filesystem** (`/home/user/`) for projects, git repos, node_modules, builds
2. **Access Windows files** (`/mnt/c/`) only when you need to read/write Windows-side files
3. **Never run `npm install` or `git clone` inside `/mnt/c/`** — it will be painfully slow
4. **If you must work on Windows files**, consider cloning/copying to Linux fs first

```bash
# BAD: Slow
cd /mnt/c/Users/Name/project && npm install

# GOOD: Fast
cp -r /mnt/c/Users/Name/project ~/project && cd ~/project && npm install
```

### WSL2 Filesystem Tuning

Add to `/etc/wsl.conf`:
```ini
[automount]
enabled = true
options = "metadata,umask=22,fmask=11"

[interop]
enabled = true
appendWindowsPath = true
```

The `metadata` option enables Linux permissions on Windows files.

## Common WSL Commands

```bash
# Check WSL version
wsl.exe --version

# List distros
wsl.exe --list --verbose

# Restart WSL (from PowerShell)
wsl.exe --shutdown

# Open specific distro
wsl.exe -d Ubuntu

# Convert WSL1 to WSL2
wsl.exe --set-version Ubuntu 2

# Update WSL kernel
wsl.exe --update
```

## Environment Variables Between Worlds

```bash
# Access Windows env vars from WSL
# WSLENV allows sharing specific vars
# Format: VAR_NAME/l where l = path translation, u = value only
# Set in Windows: setx WSLENV "PATH/l:HOME/u"

# Read a Windows env var from WSL
powershell.exe -Command "Write-Output \$env:VARIABLE_NAME" | tr -d '\r'
```

## Common Pitfalls

1. **Line endings.** Windows files may have CRLF. Run `sed -i 's/\r$//' file.sh` before executing scripts copied from Windows.

2. **Permissions on /mnt/c/.** Without `metadata` mount option, all files show 777. Add `metadata` to automount options in `/etc/wsl.conf` and restart WSL.

3. **Slow git status on /mnt/c/.** Add to `.gitconfig`: `git config --global core.fsmonitor true` and `git config --global core.untrackedCache true`.

4. **Symlinks across filesystems.** NTFS symlinks and Linux symlinks are not interchangeable. Windows may need Developer Mode to create symlinks.

5. **DNS resolution fails.** If `/etc/resolv.conf` gets overwritten: `echo -e "[network]\ngenerateResolvConf = false" | sudo tee /etc/wsl.conf` then manually set nameserver in `/etc/resolv.conf`.

6. **Memory consumption.** WSL2 defaults to 50% of RAM. Limit it in `C:\Users\Name\.wslconfig`:
   ```ini
   [wsl2]
   memory=8GB
   swap=4GB
   ```

7. **Firewall blocking WSL networking.** Windows Defender may block WSL2 traffic. Allow the WSL subnet in Windows Firewall.

8. **grep/find on /mnt/c/ is extremely slow on large repos.** A repo that scans in 2s on Linux FS can take 30s+ on /mnt/c/. For bulk operations (security scans, code search), copy to Linux fs first: `cp -r /mnt/c/Users/name/repo ~/scan-target && cd ~/scan-target`. See wsl-workflow skill for full details.

9. **jq not installed by default.** Many CLI tools and skills assume jq for JSON parsing. On this system it's not available. Use `python3 -c "import json, urllib.request; ..."` as a universal fallback.

8. **Missing CLI tools (jq, curl flags, etc.).** WSL minimal installs often lack `jq`, `htop`, and other common tools. `sudo apt install` may fail if you don't have sudo access. **Fallback:** use Python's built-in `urllib` and `json` modules instead of `jq` for API parsing:
   ```bash
   python3 -c "
   import urllib.request, json
   data = json.loads(urllib.request.urlopen('https://api.example.com/data').read())
   for item in data[:5]:
       print(item['title'])
   "
   ```
   Python is always available on WSL and handles JSON natively.

9. **Hermes approval settings block external API calls.** By default, `approvals.mode: manual` prompts for every external network request. Routine API calls (weather, news, etc.) get tedious. Switch to smart mode:
   ```bash
   hermes config set approvals.mode smart
   ```
   This auto-approves low-risk calls (curl to public APIs) but still prompts on destructive commands.

## Verification Checklist

- [ ] Path correctly translated (Windows → WSL or vice versa)
- [ ] Cross-filesystem performance considered (work in Linux fs when possible)
- [ ] Line endings handled (CRLF → LF for scripts)
- [ ] Clipboard operations tested
- [ ] Port accessibility confirmed from both sides
