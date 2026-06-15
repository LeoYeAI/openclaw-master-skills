# Linux Patcher - Setup Guide

Complete setup instructions for getting the Linux Patcher skill running securely.

## ⚠️ Important Disclaimers

**Distribution Support:**
- ✅ **Ubuntu** - Fully tested end-to-end
- ⚠️ **Untested but supported:** Amazon Linux, Debian, RHEL, AlmaLinux, CentOS, Rocky Linux, SUSE
- Update commands for untested distributions are based on official documentation
- **Always test in a non-production environment first**
- Verify updates manually after first run

**Security Notice:**
- This skill requires passwordless sudo access
- This skill uses SSH key authentication
- Review all security implications before deployment
- Follow principle of least privilege

## Prerequisites Checklist

Before starting, ensure you have:
- [ ] OpenClaw installed and running
- [ ] SSH client installed on OpenClaw host
- [ ] `jq` and `curl` installed (for PatchMon integration)
- [ ] Root/sudo access on all target hosts
- [ ] **PatchMon installed** (required to check which hosts need updating)
  - **Important:** PatchMon does NOT need to be on the same server as OpenClaw
  - Install on any server accessible via HTTPS from your OpenClaw host
  - Download: https://github.com/PatchMon/PatchMon
  - Docs: https://docs.patchmon.net

## Setup Steps

### Step 1: Install the Skill

```bash
# Option A: Install from file
openclaw skill install linux-patcher.skill

# Option B: Install from ClawHub
clawhub install linux-patcher

# Verify installation
ls -la ~/.openclaw/workspace/skills/linux-patcher
```

### Step 2: Configure SSH Key Authentication

**On OpenClaw host (control machine):**

```bash
# Generate SSH key if you don't have one
ssh-keygen -t ed25519 -C "openclaw-patching" -f ~/.ssh/id_openclaw

# Copy public key to each target host
ssh-copy-id -i ~/.ssh/id_openclaw.pub admin@targethost.example.com

# Test SSH access (should not prompt for password)
ssh -i ~/.ssh/id_openclaw admin@targethost.example.com echo "SSH OK"
```

**Configure SSH config for convenience:**

```bash
# Edit ~/.ssh/config
cat >> ~/.ssh/config << 'EOF'

# Linux Patcher hosts
Host webserver
    HostName webserver.example.com
    User admin
    IdentityFile ~/.ssh/id_openclaw

Host database
    HostName database.example.com
    User admin
    IdentityFile ~/.ssh/id_openclaw
EOF

# Test with hostname alias
ssh webserver echo "Alias works"
```

### Step 3: Configure Passwordless Sudo (CRITICAL SECURITY STEP)

**⚠️ Security Warning:**
Passwordless sudo is required for automation but poses security risks. We configure it with **minimal permissions** - only for specific commands needed for patching.

**On each target host, run as root or with sudo:**

#### For Ubuntu/Debian Systems:

```bash
# Create sudoers file with restricted permissions
cat > /etc/sudoers.d/linux-patcher << 'EOF'
# Linux Patcher - Restricted sudo access
# Only allows specific commands needed for patching
# Replace 'admin' with your SSH username

# Package management only
admin ALL=(ALL) NOPASSWD: /usr/bin/apt update
admin ALL=(ALL) NOPASSWD: /usr/bin/apt upgrade
admin ALL=(ALL) NOPASSWD: /usr/bin/apt autoremove
admin ALL=(ALL) NOPASSWD: /usr/bin/apt-get update
admin ALL=(ALL) NOPASSWD: /usr/bin/apt-get upgrade
admin ALL=(ALL) NOPASSWD: /usr/bin/apt-get autoremove

# Docker management only (if using Docker updates)
admin ALL=(ALL) NOPASSWD: /usr/bin/docker system prune
admin ALL=(ALL) NOPASSWD: /usr/bin/docker pull *
admin ALL=(ALL) NOPASSWD: /usr/bin/docker compose pull
admin ALL=(ALL) NOPASSWD: /usr/bin/docker compose up
admin ALL=(ALL) NOPASSWD: /usr/bin/docker images
EOF

# Set correct permissions (CRITICAL)
chmod 0440 /etc/sudoers.d/linux-patcher

# Verify syntax
visudo -c -f /etc/sudoers.d/linux-patcher
```

#### For RHEL/CentOS/Rocky/Alma/Amazon Linux:

```bash
# Create sudoers file with restricted permissions
cat > /etc/sudoers.d/linux-patcher << 'EOF'
# Linux Patcher - Restricted sudo access

# Package management (yum)
admin ALL=(ALL) NOPASSWD: /usr/bin/yum check-update
admin ALL=(ALL) NOPASSWD: /usr/bin/yum update
admin ALL=(ALL) NOPASSWD: /usr/bin/yum autoremove

# Package management (dnf - for RHEL 8+, Rocky, Alma)
admin ALL=(ALL) NOPASSWD: /usr/bin/dnf check-update
admin ALL=(ALL) NOPASSWD: /usr/bin/dnf update
admin ALL=(ALL) NOPASSWD: /usr/bin/dnf autoremove

# Docker management
admin ALL=(ALL) NOPASSWD: /usr/bin/docker system prune
admin ALL=(ALL) NOPASSWD: /usr/bin/docker pull *
admin ALL=(ALL) NOPASSWD: /usr/bin/docker compose pull
admin ALL=(ALL) NOPASSWD: /usr/bin/docker compose up
admin ALL=(ALL) NOPASSWD: /usr/bin/docker images
EOF

chmod 0440 /etc/sudoers.d/linux-patcher
visudo -c -f /etc/sudoers.d/linux-patcher
```

#### For SUSE/OpenSUSE:

```bash
# Create sudoers file with restricted permissions
cat > /etc/sudoers.d/linux-patcher << 'EOF'
# Linux Patcher - Restricted sudo access

# Package management
admin ALL=(ALL) NOPASSWD: /usr/bin/zypper refresh
admin ALL=(ALL) NOPASSWD: /usr/bin/zypper update
admin ALL=(ALL) NOPASSWD: /usr/bin/zypper packages
admin ALL=(ALL) NOPASSWD: /usr/bin/zypper remove

# Docker management
admin ALL=(ALL) NOPASSWD: /usr/bin/docker system prune
admin ALL=(ALL) NOPASSWD: /usr/bin/docker pull *
admin ALL=(ALL) NOPASSWD: /usr/bin/docker compose pull
admin ALL=(ALL) NOPASSWD: /usr/bin/docker compose up
admin ALL=(ALL) NOPASSWD: /usr/bin/docker images
EOF

chmod 0440 /etc/sudoers.d/linux-patcher
visudo -c -f /etc/sudoers.d/linux-patcher
```

**Test sudo access:**

```bash
# From OpenClaw host, test sudo without password prompt
ssh admin@targethost sudo apt update  # Should run without password
ssh admin@targethost sudo reboot       # Should ask for password (not allowed)
```

### Step 4: Configure PatchMon Credentials (Optional but Recommended)

```bash
# Copy template
cp ~/.openclaw/workspace/skills/linux-patcher/scripts/patchmon-credentials.example.conf \
   ~/.patchmon-credentials.conf

# Edit with your credentials
nano ~/.patchmon-credentials.conf
```

**Set the following values:**

```bash
PATCHMON_URL=https://patchmon.example.com  # Your PatchMon server URL
PATCHMON_USERNAME=your-username             # Your PatchMon username
PATCHMON_PASSWORD=your-secure-password      # Your PatchMon password
```

**Secure the credentials file:**

```bash
chmod 600 ~/.patchmon-credentials.conf
```

**Test PatchMon connectivity:**

```bash
cd ~/.openclaw/workspace/skills/linux-patcher
scripts/patchmon-query.sh
```

### Step 5: Test the Setup

#### Test 1: Host-Only Update (Dry-Run)

```bash
cd ~/.openclaw/workspace/skills/linux-patcher

# Test on one host first
DRY_RUN=true scripts/patch-host-only.sh admin@webserver.example.com
```

#### Test 2: Full Update (Dry-Run with Docker)

```bash
# Test with Docker path auto-detection
DRY_RUN=true scripts/patch-host-full.sh admin@webserver.example.com

# Or specify Docker path
DRY_RUN=true scripts/patch-host-full.sh admin@webserver.example.com /opt/docker
```

#### Test 3: Automatic Mode (Dry-Run via PatchMon)

```bash
# Queries PatchMon, detects hosts, but doesn't apply changes
scripts/patch-auto.sh --dry-run
```

#### Test 4: Apply Real Updates (Single Host)

```bash
# Remove DRY_RUN flag to actually apply updates
scripts/patch-host-only.sh admin@webserver.example.com
```

### Step 6: Verify Results

After first real update:

1. **SSH into the updated host:**
   ```bash
   ssh admin@webserver.example.com
   ```

2. **Check update logs:**
   ```bash
   # Ubuntu/Debian
   tail -100 /var/log/apt/history.log
   
   # RHEL/CentOS
   tail -100 /var/log/yum.log  # or dnf.log
   
   # SUSE
   tail -100 /var/log/zypper.log
   ```

3. **Verify Docker containers (if applicable):**
   ```bash
   docker ps
   docker compose ps
   docker logs container-name
   ```

4. **Check for reboot requirement:**
   ```bash
   # Ubuntu/Debian
   [ -f /var/run/reboot-required ] && echo "Reboot needed" || echo "No reboot needed"
   
   # Any distro - check kernel
   uname -r  # Running kernel
   ls -t /boot/vmlinuz-* | head -n1  # Latest installed
   ```

## Security Best Practices

### 1. Principle of Least Privilege

✅ **DO:**
- Create separate user for patching (e.g., `patchbot`)
- Grant sudo only for specific commands
- Use sudoers.d files (easier to manage)
- Set file permissions to 0440

❌ **DON'T:**
- Use `NOPASSWD: ALL` (grants too much access)
- Share SSH keys between users
- Run patches as root directly

### 2. SSH Key Protection

✅ **DO:**
- Use passphrase-protected SSH keys when possible
- Store keys with permissions 0600
- Use dedicated keys for automation
- Rotate keys periodically
- Use SSH agent for passphrase management

❌ **DON'T:**
- Share private keys
- Store keys in version control
- Use the same key for multiple purposes

### 3. PatchMon Credentials

✅ **DO:**
- Store credentials in `~/.patchmon-credentials.conf` with 0600 permissions
- Use strong, unique password
- Rotate passwords regularly
- Use HTTPS for PatchMon URL

❌ **DON'T:**
- Hardcode credentials in scripts
- Share credentials file
- Use weak passwords
- Access PatchMon over HTTP

### 4. Network Security

✅ **DO:**
- Use firewall rules to restrict SSH access
- Use VPN for remote patching
- Enable SSH key-only authentication
- Disable password authentication for SSH

❌ **DON'T:**
- Expose SSH to public internet without restrictions
- Use default SSH port without firewall
- Allow password authentication

### 5. Audit and Monitoring

✅ **DO:**
- Review `/var/log/auth.log` regularly
- Monitor sudo usage
- Enable PatchMon agents for tracking
- Set up alerts for failed updates
- Keep update logs

❌ **DON'T:**
- Ignore failed login attempts
- Skip log reviews
- Disable auditing

## Troubleshooting Setup

### Issue: SSH Key Authentication Not Working

**Symptoms:**
- Password prompts appear
- "Permission denied (publickey)" errors

**Solutions:**
```bash
# 1. Verify key is added to target host
ssh admin@target "cat ~/.ssh/authorized_keys"

# 2. Check SSH key permissions
ls -la ~/.ssh/id_openclaw
chmod 600 ~/.ssh/id_openclaw  # Fix if needed

# 3. Check target host SSH config
ssh admin@target "grep -E '(PubkeyAuthentication|PasswordAuthentication)' /etc/ssh/sshd_config"

# 4. Enable SSH debugging
ssh -vvv admin@target
```

### Issue: Sudo Still Asking for Password

**Symptoms:**
- "sudo: a password is required" errors
- Updates fail with permission denied

**Solutions:**
```bash
# 1. Verify sudoers file exists and is valid
ssh admin@target "sudo visudo -c -f /etc/sudoers.d/linux-patcher"

# 2. Check file permissions
ssh admin@target "ls -la /etc/sudoers.d/linux-patcher"
# Should be: -r--r----- root root

# 3. Test specific command
ssh admin@target "sudo apt update"  # Should not prompt

# 4. Check sudo logs for errors
ssh admin@target "sudo grep sudo /var/log/auth.log | tail -20"
```

### Issue: PatchMon Connection Failed

**Symptoms:**
- "Failed to authenticate with PatchMon"
- Connection timeout errors

**Solutions:**
```bash
# 1. Test PatchMon connectivity
curl -k https://patchmon.example.com/api/health

# 2. Verify credentials
cat ~/.patchmon-credentials.conf

# 3. Test authentication manually
curl -k -X POST https://patchmon.example.com/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"user","password":"pass"}'

# 4. Check firewall rules
telnet patchmon.example.com 443
```

### Issue: Docker Detection Fails

**Symptoms:**
- "Docker Compose not found"
- Auto-detection fails

**Solutions:**
```bash
# 1. Verify Docker is installed
ssh admin@target "command -v docker"

# 2. Check Docker Compose file exists
ssh admin@target "find /home /opt /srv -name docker-compose.yml 2>/dev/null"

# 3. Specify path manually
scripts/patch-host-full.sh admin@target /full/path/to/docker

# 4. Check permissions
ssh admin@target "ls -la /path/to/docker/docker-compose.yml"
```

## Next Steps

After successful setup:

1. **Schedule automated updates:**
   ```bash
   cron add --name "Nightly Patching" \
     --schedule "0 2 * * *" \
     --task "cd ~/.openclaw/workspace/skills/linux-patcher && scripts/patch-auto.sh"
   ```

2. **Set up notifications:**
   - Configure PatchMon alerts
   - Add Telegram/Discord webhooks
   - Monitor cron job logs

3. **Document your infrastructure:**
   - Create host inventory
   - Note Docker paths
   - Track update schedules

4. **Test disaster recovery:**
   - Practice rolling back updates
   - Document manual procedures
   - Test backup restoration

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review skill logs
3. Test each component individually
4. Read SKILL.md for detailed documentation
5. Ask OpenClaw: "Help me troubleshoot linux-patcher skill"
