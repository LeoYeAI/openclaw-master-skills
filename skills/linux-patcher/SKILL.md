---
name: linux-patcher
description: Automated Linux server patching and Docker container updates. Use when the user asks to update, patch, or upgrade Linux servers, apply security updates, update Docker containers, check for system updates, or manage server maintenance across multiple hosts. Supports Ubuntu, Debian, RHEL, AlmaLinux, Rocky Linux, CentOS, Amazon Linux, and SUSE. Includes PatchMon integration for automatic host detection and intelligent Docker handling.
---

# Linux Patcher

Automate Linux server patching and Docker container updates across multiple hosts via SSH.

## ⚠️ Important Disclaimers

### Distribution Support Status

**Fully Tested:**
- ✅ **Ubuntu** - Tested end-to-end with real infrastructure

**Supported but Untested:**
- ⚠️ **Debian GNU/Linux** - Commands based on official documentation
- ⚠️ **Amazon Linux** - Supports both AL2 (yum) and AL2023 (dnf)
- ⚠️ **RHEL (Red Hat Enterprise Linux)** - Supports RHEL 7 (yum) and 8+ (dnf)
- ⚠️ **AlmaLinux** - RHEL-compatible, uses dnf
- ⚠️ **Rocky Linux** - RHEL-compatible, uses dnf
- ⚠️ **CentOS** - Supports CentOS 7 (yum) and 8+ (dnf)
- ⚠️ **SUSE/OpenSUSE** - Uses zypper package manager

**Testing Recommendation:**
Always test untested distributions in a non-production environment first. The script will warn you when running on untested distributions.

### Security Notice

This skill requires:
- **Passwordless sudo access** - Configured with restricted permissions
- **SSH key authentication** - No passwords stored or transmitted
- **PatchMon credentials** - Stored securely in user's home directory

**Read `SETUP.md` for complete security configuration guide.**

## Quick Start

### Automated (Recommended)

**Patch all hosts from PatchMon** (automatic detection):
```bash
scripts/patch-auto.sh
```

**Skip Docker updates** (packages only):
```bash
scripts/patch-auto.sh --skip-docker
```

**Preview changes** (dry-run):
```bash
scripts/patch-auto.sh --dry-run
```

### Manual (Alternative)

**Single host - packages only**:
```bash
scripts/patch-host-only.sh user@hostname
```

**Single host - full update**:
```bash
scripts/patch-host-full.sh user@hostname /path/to/docker/compose
```

**Multiple hosts from config**:
```bash
scripts/patch-multiple.sh config-file.conf
```

## Features

- **PatchMon integration** - Automatically detects hosts needing updates
- **Smart Docker detection** - Auto-detects Docker and Compose paths
- **Selective updates** - Skip Docker updates with `--skip-docker` flag
- **Passwordless sudo required** - Configure with `visudo` or `/etc/sudoers.d/` files
- **SSH key authentication** - No password prompts
- **Parallel execution** - Update multiple hosts simultaneously
- **Dry-run mode** - Preview changes without applying
- **Manual override** - Run updates on specific hosts without PatchMon

## Configuration

### Option 1: Automatic via PatchMon (Recommended)

Configure PatchMon credentials for automatic host detection:

```bash
cp scripts/patchmon-credentials.example.conf ~/.patchmon-credentials.conf
nano ~/.patchmon-credentials.conf
```

Set your credentials:
```bash
PATCHMON_URL=https://patchmon.example.com
PATCHMON_USERNAME=your-username
PATCHMON_PASSWORD=your-password
```

Then simply run:
```bash
scripts/patch-auto.sh
```

The script will:
1. Query PatchMon for hosts needing updates
2. Auto-detect Docker on each host
3. Apply appropriate updates (host-only or full)

### Option 2: Single Host (Quick Manual)

Run scripts directly with command-line arguments (no config file needed).

### Option 3: Multiple Hosts (Manual Config)

Create a config file based on `scripts/patch-hosts-config.example.sh`:

```bash
cp scripts/patch-hosts-config.example.sh my-servers.conf
nano my-servers.conf
```

Example config:
```bash
# Host definitions: hostname,ssh_user,docker_path
HOSTS=(
  "webserver.example.com,ubuntu,/opt/docker"
  "database.example.com,root,/home/admin/compose"
  "monitor.example.com,docker,/srv/monitoring"
)

# Update mode: "host-only" or "full"
UPDATE_MODE="full"

# Dry run mode (set to "false" to apply changes)
DRY_RUN="true"
```

Then run:
```bash
scripts/patch-multiple.sh my-servers.conf
```

## Prerequisites

### Required on Control Machine (where OpenClaw runs)

- [ ] **OpenClaw** installed and running
- [ ] **SSH client** installed (`ssh` command available)
- [ ] **Bash** 4.0 or higher
- [ ] **curl** installed (for PatchMon API)
- [ ] **jq** installed (for JSON parsing)
- [ ] **PatchMon** installed (required to check which hosts need updating)
  - Does NOT need to be on the OpenClaw host
  - Can be installed on any server accessible via HTTPS
  - Download: https://github.com/PatchMon/PatchMon

**Install missing tools:**
```bash
# Ubuntu/Debian
sudo apt install curl jq

# RHEL/CentOS/Rocky/Alma
sudo dnf install curl jq

# macOS
brew install curl jq
```

### Required on Target Hosts

- [ ] **SSH server** running and accessible
- [ ] **SSH key authentication** configured (passwordless login)
- [ ] **Passwordless sudo** configured for patching commands (see SETUP.md)
- [ ] **Docker** installed (optional, only for full updates)
- [ ] **Docker Compose** installed (optional, only for full updates)
- [ ] **PatchMon agent** installed and reporting (optional but recommended)

### PatchMon Setup (Required for Automatic Mode)

**PatchMon is required to automatically detect which hosts need patching.**

**Important:** PatchMon does NOT need to be installed on the same server as OpenClaw. Install PatchMon on a separate server (can be any server on your network), and OpenClaw will query it via API.

**Download PatchMon:**
- **GitHub:** https://github.com/PatchMon/PatchMon
- **Documentation:** https://docs.patchmon.net

**What you need:**
- [ ] PatchMon server installed on ANY accessible server (not necessarily the OpenClaw host)
- [ ] PatchMon agents installed on all target hosts you want to patch
- [ ] PatchMon API credentials (username/password)
- [ ] Network connectivity from OpenClaw host to PatchMon server (HTTPS)

**Architecture:**
```
┌─────────────────┐      HTTPS API      ┌─────────────────┐
│ OpenClaw Host   │ ──────────────────> │ PatchMon Server │
│ (this machine)  │    Query updates    │ (separate host) │
└─────────────────┘                     └─────────────────┘
                                                  │
                                                  │ Reports
                                                  ▼
                                         ┌─────────────────┐
                                         │ Target Hosts    │
                                         │ (with agents)   │
                                         └─────────────────┘
```

**Quick Start:**
1. Install PatchMon server on a separate server (see GitHub repo)
2. Install PatchMon agents on all hosts you want to patch
3. Configure OpenClaw to access PatchMon API:

```bash
cp scripts/patchmon-credentials.example.conf ~/.patchmon-credentials.conf
nano ~/.patchmon-credentials.conf  # Set PatchMon server URL
chmod 600 ~/.patchmon-credentials.conf
```

**Detailed setup:**
See `references/patchmon-setup.md` for complete installation guide.

**Can I use this skill without PatchMon?**
Yes! You can use manual mode to target specific hosts without PatchMon. However, automatic detection of hosts needing updates requires PatchMon.

### On Target Hosts

**Required:**
- SSH server running
- Passwordless sudo for the SSH user (for `apt` and `docker` commands)
- PatchMon agent installed and reporting (for automatic mode)

**For full updates:**
- Docker and Docker Compose installed
- Docker Compose files exist at specified paths

### Configure Passwordless Sudo

On each target host, create `/etc/sudoers.d/patches`:

```bash
# For Ubuntu/Debian systems
username ALL=(ALL) NOPASSWD: /usr/bin/apt, /usr/bin/docker

# For RHEL/CentOS systems
username ALL=(ALL) NOPASSWD: /usr/bin/yum, /usr/bin/docker, /usr/bin/dnf
```

Replace `username` with your SSH user. Test with `sudo -l` to verify.

## Update Modes

### Host-Only Updates

Updates system packages only:
- Run `apt update && apt upgrade` (or `yum update` on RHEL)
- Remove unused packages (`apt autoremove`)
- **Does NOT** touch Docker containers

**When to use:**
- Hosts without Docker
- Security patches only
- Minimal downtime required

### Full Updates

Complete update cycle:
- Update system packages
- Clean Docker cache (`docker system prune`)
- Pull latest Docker images
- Recreate containers with new images
- **Causes brief service interruption**

**When to use:**
- Docker-based infrastructure
- Regular maintenance windows
- Application updates available

## Workflow

### Automatic Workflow (patch-auto.sh)

1. **Query PatchMon** - Fetch hosts needing updates via API
2. **For each host:**
   - SSH into host
   - Check if Docker is installed
   - Auto-detect Docker Compose path (if not specified)
   - Apply host-only OR full update based on Docker detection
3. **Report results** - Summary of successful/failed updates

### Host-Only Update Process

1. SSH into target host
2. Run `sudo apt update`
3. Run `sudo apt -y upgrade`
4. Run `sudo apt -y autoremove`
5. Report results

### Full Update Process

1. SSH into target host
2. Run `sudo apt update && upgrade && autoremove`
3. Navigate to Docker Compose directory
4. Run `sudo docker system prune -af` (cleanup)
5. Pull all Docker images listed in compose file
6. Run `sudo docker compose pull`
7. Run `sudo docker compose up -d` (recreate containers)
8. Report results

### Docker Detection Logic

When using automatic mode:
- **Docker installed + compose file found** → Full update
- **Docker installed + no compose file** → Host-only update
- **Docker not installed** → Host-only update
- **--skip-docker flag set** → Host-only update (ignores Docker)

## Docker Path Auto-Detection

When Docker path is not specified, the script checks these locations:

1. `/home/$USER/Docker/docker-compose.yml`
2. `/opt/docker/docker-compose.yml`
3. `/srv/docker/docker-compose.yml`
4. `$HOME/Docker/docker-compose.yml`
5. Current directory

**Override auto-detection:**
```bash
scripts/patch-host-full.sh user@host /custom/path
```

## Examples

### Example 1: Automatic update via PatchMon (recommended)
```bash
# First time: configure credentials
cp scripts/patchmon-credentials.example.conf ~/.patchmon-credentials.conf
nano ~/.patchmon-credentials.conf

# Run automatic updates
scripts/patch-auto.sh
```

### Example 2: Automatic with dry-run
```bash
# Preview what would be updated
scripts/patch-auto.sh --dry-run

# Review output, then apply
scripts/patch-auto.sh
```

### Example 3: Skip Docker updates
```bash
# Update packages only, even if Docker is detected
scripts/patch-auto.sh --skip-docker
```

### Example 4: Manual single host, packages only
```bash
scripts/patch-host-only.sh admin@webserver.example.com
```

### Example 5: Manual single host, full update with custom Docker path
```bash
scripts/patch-host-full.sh docker@app.example.com /home/docker/production
```

### Example 6: Manual multiple hosts from config
```bash
scripts/patch-multiple.sh production-servers.conf
```

### Example 7: Via OpenClaw chat
Simply ask OpenClaw:
- "Update my servers"
- "Patch all hosts that need updates"
- "Update packages only, skip Docker"

OpenClaw will use the automatic mode and report results.

## Troubleshooting

### PatchMon Integration Issues

#### "PatchMon credentials not found"
- Create credentials file: `cp scripts/patchmon-credentials.example.conf ~/.patchmon-credentials.conf`
- Edit with your PatchMon URL and credentials
- Or set `PATCHMON_CONFIG` environment variable to custom location

#### "Failed to authenticate with PatchMon"
- Verify PatchMon URL is correct (without trailing slash)
- Check username and password
- Ensure PatchMon server is accessible: `curl -k https://patchmon.example.com/api/health`
- Check firewall rules

#### "No hosts need updates" but PatchMon shows updates available
- Verify PatchMon agents are running on target hosts: `systemctl status patchmon-agent`
- Check agent reporting intervals: `/etc/patchmon/config.yml`
- Force agent update: `patchmon-agent report`

### System Update Issues

#### "Permission denied" on apt/docker commands
- Configure passwordless sudo (see Prerequisites section)
- Test with: `ssh user@host sudo apt update`

#### "Connection refused"
- Verify SSH access: `ssh user@host echo OK`
- Check SSH keys are configured
- Verify hostname resolution

#### Docker Compose not found
- Specify full path: `scripts/patch-host-full.sh user@host /full/path`
- Or install Docker Compose on target host
- Auto-detection searches: `/home/user/Docker`, `/opt/docker`, `/srv/docker`

#### Containers fail to start after update
- Check logs: `ssh user@host "docker logs container-name"`
- Manually inspect: `ssh user@host "cd /docker/path && docker compose logs"`
- Rollback if needed: `ssh user@host "cd /docker/path && docker compose down && docker compose up -d"`

## PatchMon Integration (Optional)

For dashboard monitoring and scheduled patching, see `references/patchmon-setup.md`.

PatchMon provides:
- Web dashboard for update status
- Per-host package tracking
- Security update highlighting
- Update history

## Security Considerations

- **Passwordless sudo** is required for automation
  - Limit to specific commands (`apt`, `docker` only)
  - Use `/etc/sudoers.d/` files (easier to manage)
- **SSH keys** should be protected
  - Use passphrase-protected keys when possible
  - Restrict key permissions: `chmod 600 ~/.ssh/id_rsa`
- **Review updates** before applying in production
  - Use dry-run mode first
  - Test on staging environment
- **Schedule updates** during maintenance windows
  - Use OpenClaw cron jobs for automation
  - Coordinate with team for Docker updates (brief downtime)

## Best Practices

1. **Test first** - Run dry-run mode before applying changes
2. **Stagger updates** - Don't update all hosts simultaneously (avoid full outage)
3. **Monitor logs** - Check output for errors after updates
4. **Backup configs** - Keep Docker Compose files in version control
5. **Schedule wisely** - Update during low-traffic windows
6. **Document paths** - Maintain config files for infrastructure
7. **Reboot when needed** - Kernel updates require reboots (not automated)

## Reboot Management

The scripts do NOT automatically reboot hosts. After updates:

1. Check if reboot required: `ssh user@host "[ -f /var/run/reboot-required ] && echo YES || echo NO"`
2. Schedule manual reboots during maintenance windows
3. Use PatchMon dashboard to track reboot requirements

## Integration with OpenClaw

### Run Updates on Schedule

Create a cron job for automatic nightly patching:

```bash
cron add --name "Nightly Server Patching" \
  --schedule "0 2 * * *" \
  --task "cd ~/.openclaw/workspace/skills/linux-patcher && scripts/patch-auto.sh"
```

Or packages-only mode:

```bash
cron add --name "Nightly Package Updates" \
  --schedule "0 2 * * *" \
  --task "cd ~/.openclaw/workspace/skills/linux-patcher && scripts/patch-auto.sh --skip-docker"
```

### Run Updates via Chat

Simply ask OpenClaw natural language commands:

**Full updates (packages + Docker containers):**
- "Update my servers" ← **Includes Docker by default**
- "Patch all hosts that need updates"
- "Update all my infrastructure"

**Packages only (exclude Docker):**
- "Update my servers, excluding docker"
- "Update packages only, skip Docker"
- "Patch hosts without touching containers"

**Query status:**
- "What servers need patching?"
- "Show me hosts that need updates"

**What happens automatically:**

When you say **"Update my servers"**:
1. ✅ Queries PatchMon for hosts needing updates
2. ✅ Detects Docker on each host
3. ✅ Updates system packages
4. ✅ **Pulls Docker images and recreates containers** (if Docker detected)
5. ✅ Reports results with success/failure count

When you say **"Update my servers, excluding docker"**:
1. ✅ Queries PatchMon for hosts needing updates
2. ✅ Updates system packages only
3. ❌ Skips all Docker operations (containers keep running)
4. ✅ Reports results

**Important:** Docker updates are **included by default** for maximum automation. Use "excluding docker" to skip container updates.

### Manual Override (Specific Hosts)

Target individual hosts without querying PatchMon:
- "Update webserver.example.com"
- "Patch database.example.com packages only"
- "Update app.example.com with Docker"

OpenClaw will use the manual scripts for targeted updates.

## Documentation Files

This skill includes comprehensive documentation:

- **SKILL.md** (this file) - Overview and usage guide
- **SETUP.md** - Complete setup instructions with security best practices
- **WORKFLOWS.md** - Visual workflow diagrams for all modes
- **references/patchmon-setup.md** - PatchMon installation and integration

**First time setup?** Read `SETUP.md` first - it provides step-by-step instructions for secure configuration.

**Want to understand the flow?** Check `WORKFLOWS.md` for visual diagrams of how the skill operates.

## Supported Linux Distributions

| Distribution | Package Manager | Tested | Status |
|--------------|-----------------|--------|--------|
| Ubuntu | apt | ✅ Yes | Fully supported |
| Debian | apt | ⚠️ No | Supported (untested) |
| Amazon Linux 2 | yum | ⚠️ No | Supported (untested) |
| Amazon Linux 2023 | dnf | ⚠️ No | Supported (untested) |
| RHEL 7 | yum | ⚠️ No | Supported (untested) |
| RHEL 8+ | dnf | ⚠️ No | Supported (untested) |
| AlmaLinux | dnf | ⚠️ No | Supported (untested) |
| Rocky Linux | dnf | ⚠️ No | Supported (untested) |
| CentOS 7 | yum | ⚠️ No | Supported (untested) |
| CentOS 8+ | dnf | ⚠️ No | Supported (untested) |
| SUSE/OpenSUSE | zypper | ⚠️ No | Supported (untested) |

The skill automatically detects the distribution and selects the appropriate package manager.
