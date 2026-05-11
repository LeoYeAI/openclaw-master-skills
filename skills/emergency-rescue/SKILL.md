---
name: emergency-rescue
description: Recover from developer disasters. Use when someone force-pushed to main, leaked credentials in git, ran out of disk space, killed the wrong process, corrupted a database, broke a deploy, locked themselves out of SSH, lost commits after a bad rebase, or hit any other "oh no" moment that needs immediate, calm, step-by-step recovery.
metadata: {"clawdbot":{"emoji":"🚨","requires":{"anyBins":["git","bash"]},"os":["linux","darwin","win32"]}}
---

# Emergency Rescue Kit

Step-by-step recovery procedures for the worst moments in a developer's day. Every section follows the same pattern: **diagnose → fix → verify**. Commands are non-destructive by default. Destructive steps are flagged.

When something has gone wrong, find your situation below and follow the steps in order.

## When to Use

- Someone force-pushed to main and overwrote history
- Credentials were committed to a public repository
- A rebase or reset destroyed commits you need
- Disk is full and nothing works
- A process is consuming all memory or won't die
- A database migration failed halfway through
- A deploy needs to be rolled back immediately
- SSH access is locked out
- SSL certificates expired in production
- You don't know what went wrong, but it's broken

---

## Git Disasters

### Force-pushed to main (or any shared branch)

Someone ran `git push --force` and overwrote remote history.

```bash
# DIAGNOSE: Check the reflog on any machine that had the old state
git reflog show origin/main
# Look for the last known-good commit hash

# FIX (if you have the old state locally):
git push origin <good-commit-hash>:main --force-with-lease
# --force-with-lease is safer than --force: it fails if remote changed again

# FIX (if you DON'T have the old state locally):
# GitHub/GitLab retain force-pushed refs temporarily

# GitHub: check the "push" event in the audit log or use the API
gh api repos/{owner}/{repo}/events --jq '.[] | select(.type=="PushEvent") | .payload.before'

# GitLab: check the reflog on the server (admin access needed)
# Or restore from any CI runner or team member's local clone

# VERIFY:
git log --oneline -10 origin/main
# Confirm the history looks correct
```

### Lost commits after rebase or reset --hard

You ran `git rebase` or `git reset --hard` and commits disappeared.

```bash
# DIAGNOSE: Your commits are NOT gone. Git keeps everything for 30+ days.
git reflog
# Find the commit hash from BEFORE the rebase/reset
# Look for entries like "rebase (start)" or "reset: moving to"

# FIX: Reset back to the pre-disaster state
git reset --hard <commit-hash-before-disaster>

# FIX (alternative): Cherry-pick specific lost commits
git cherry-pick <lost-commit-hash>

# FIX (if reflog is empty — rare, usually means different repo):
git fsck --lost-found
# Look in .git/lost-found/commit/ for dangling commits
ls .git/lost-found/commit/
git show <hash>  # Inspect each one

# VERIFY:
git log --oneline -10
# Your commits should be back
```

### Committed to the wrong branch

You made commits on `main` that should be on a feature branch.

```bash
# DIAGNOSE: Check where you are and what you committed
git log --oneline -5
git branch

# FIX: Create the feature branch at current position, then reset main
git branch feature-branch          # Create branch pointing at current commit
git reset --hard HEAD~<N>          # Move main back N commits (⚠️ destructive)
git checkout feature-branch        # Switch to the new branch

# FIX (safer alternative using cherry-pick):
git checkout -b feature-branch     # Create and switch to new branch
git checkout main
git reset --hard origin/main       # Reset main to remote state
# Your commits are safely on feature-branch

# VERIFY:
git log --oneline main -5
git log --oneline feature-branch -5
```

### Merge gone wrong (conflicts everywhere, wrong result)

A merge produced a bad result and you want to start over.

```bash
# FIX (merge not yet committed — still in conflict state):
git merge --abort

# FIX (merge was committed but not pushed):
git reset --hard HEAD~1

# FIX (merge was already pushed): Create a revert commit
git revert -m 1 <merge-commit-hash>
# -m 1 means "keep the first parent" (your branch before merge)
git push

# VERIFY:
git log --oneline --graph -10
git diff HEAD~1  # Review what changed
```

### Corrupted git repository

Git commands fail with "bad object", "corrupt", or "broken link" errors.

```bash
# DIAGNOSE: Check repository integrity
git fsck --full

# FIX (if remote is intact — most common):
# Save any uncommitted work first
cp -r . ../repo-backup

# Re-clone and restore local work
cd ..
git clone <remote-url> repo-fresh
cp -r repo-backup/path/to/uncommitted/files repo-fresh/

# FIX (repair without re-cloning):
# Remove corrupt objects and fetch them again
git fsck --full 2>&1 | grep "corrupt\|missing" | awk '{print $NF}'
# For each corrupt object:
rm .git/objects/<first-2-chars>/<remaining-hash>
git fetch origin  # Re-download from remote

# VERIFY:
git fsck --full  # Should report no errors
git log --oneline -5
```

---

## Credential Leaks

### Secret committed to git (API key, password, token)

A credential is in the git history. Every second counts — automated scrapers monitor public GitHub repos for leaked keys.

```bash
# STEP 1: REVOKE THE CREDENTIAL IMMEDIATELY
# Do this FIRST, before cleaning git history.
# The credential is already compromised the moment it was pushed publicly.

# AWS keys:
aws iam delete-access-key --access-key-id AKIAXXXXXXXXXXXXXXXX --user-name <user>
# Then create a new key pair

# GitHub tokens:
# Go to github.com → Settings → Developer settings → Tokens → Revoke

# Database passwords:
# Change the password in the database immediately
# ALTER USER myuser WITH PASSWORD 'new-secure-password';

# Generic API tokens:
# Revoke in the provider's dashboard, generate new ones

# STEP 2: Remove from current branch
git rm --cached <file-with-secret>    # If the whole file is secret
# OR edit the file to remove the secret, then:
git add <file>

# STEP 3: Add to .gitignore
echo ".env" >> .gitignore
echo "credentials.json" >> .gitignore
git add .gitignore

# STEP 4: Remove from git history (⚠️ rewrites history)
# Option A: git-filter-repo (recommended, install with pip install git-filter-repo)
git filter-repo --path <file-with-secret> --invert-paths

# Option B: BFG Repo Cleaner (faster for large repos)
# Download from https://rtyley.github.io/bfg-repo-cleaner/
java -jar bfg.jar --delete-files <filename> .
git reflog expire --expire=now --all
git gc --prune=now --aggressive

# STEP 5: Force push the cleaned history
git push origin --force --all
git push origin --force --tags

# STEP 6: Notify all collaborators to re-clone
# Their local copies still have the secret in reflog

# VERIFY:
git log --all -p -S '<the-secret-string>' --diff-filter=A
# Should return nothing
```

### .env file pushed to public repo

```bash
# STEP 1: Revoke ALL credentials in that .env file. All of them. Now.

# STEP 2: Remove and ignore
git rm --cached .env
echo ".env" >> .gitignore
git add .gitignore
git commit -m "Remove .env from tracking"

# STEP 3: Remove from history (see credential removal above)
git filter-repo --path .env --invert-paths

# STEP 4: Check what was exposed
# List every variable that was in the .env:
git show HEAD~1:.env 2>/dev/null || git log --all -p -- .env | head -50
# Rotate every single value.

# PREVENTION: Add a pre-commit hook
cat > .git/hooks/pre-commit << 'HOOK'
#!/bin/bash
if git diff --cached --name-only | grep -qE '\.env$|\.env\.local$|credentials'; then
    echo "ERROR: Attempting to commit potential secrets file"
    echo "Files: $(git diff --cached --name-only | grep -E '\.env|credentials')"
    exit 1
fi
HOOK
chmod +x .git/hooks/pre-commit
```

### Secret visible in CI/CD logs

```bash
# STEP 1: Revoke the credential immediately

# STEP 2: Delete the CI run/logs if possible
# GitHub Actions:
gh run delete <run-id>
# Or: Settings → Actions → delete specific run

# STEP 3: Fix the pipeline
# Never echo secrets. Mask them:
# GitHub Actions: echo "::add-mask::$MY_SECRET"
# GitLab CI: variables are masked if marked as "Masked" in settings

# STEP 4: Audit what was exposed
# Check the log output for patterns like:
# AKIAXXXXXXXXX (AWS)
# ghp_XXXXXXXXX (GitHub)
# sk-XXXXXXXXXXX (OpenAI/Stripe)
# Any connection strings with passwords
```

---

## Disk Full Emergencies

### System or container disk is full

Nothing works — builds fail, logs can't write, services crash.

```bash
# DIAGNOSE: What's using space?
df -h                          # Which filesystem is full?
du -sh /* 2>/dev/null | sort -rh | head -20    # Biggest top-level dirs
du -sh /var/log/* | sort -rh | head -10        # Log bloat?

# QUICK WINS (safe to run immediately):

# 1. Docker cleanup (often the #1 cause)
docker system df               # See Docker disk usage
docker system prune -a -f      # Remove all unused images, containers, networks
docker volume prune -f          # Remove unused volumes
docker builder prune -a -f      # Remove build cache
# ⚠️ This removes ALL unused Docker data. Safe if you can re-pull/rebuild.

# 2. Package manager caches
# npm
npm cache clean --force
rm -rf ~/.npm/_cacache

# pip
pip cache purge

# apt
sudo apt-get clean
sudo apt-get autoremove -y

# brew
brew cleanup --prune=all

# 3. Log rotation (immediate)
# Truncate (not delete) large log files to free space instantly
sudo truncate -s 0 /var/log/syslog
sudo truncate -s 0 /var/log/journal/*/*.journal  # systemd journals
find /var/log -name "*.log" -size +100M -exec truncate -s 0 {} \;
# Truncate preserves the file handle so services don't break

# 4. Old build artifacts
find . -name "node_modules" -type d -prune -exec rm -rf {} + 2>/dev/null
find . -name ".next" -type d -exec rm -rf {} + 2>/dev/null
find . -name "dist" -type d -exec rm -rf {} + 2>/dev/null
find /tmp -type f -mtime +7 -delete 2>/dev/null

# 5. Find the actual culprit
find / -xdev -type f -size +100M -exec ls -lh {} \; 2>/dev/null | sort -k5 -rh | head -20
# Shows files over 100MB, sorted by size

# VERIFY:
df -h  # Check free space increased
```

### Docker-specific disk full

```bash
# DIAGNOSE:
docker system df -v

# Common culprits:
# 1. Dangling images from builds
docker image prune -f

# 2. Stopped containers accumulating
docker container prune -f

# 3. Build cache (often the biggest)
docker builder prune -a -f

# 4. Volumes from old containers
docker volume ls -qf dangling=true
docker volume prune -f

# NUCLEAR OPTION (⚠️ removes EVERYTHING):
docker system prune -a --volumes -f
# You will need to re-pull all images and recreate all volumes

# VERIFY:
docker system df
df -h
```

---

## Process Emergencies

### Port already in use

```bash
# DIAGNOSE: What's using the port?
# Linux:
lsof -i :8080
ss -tlnp | grep 8080
# macOS:
lsof -i :8080
# Windows:
netstat -ano | findstr :8080

# FIX: Kill the process
kill $(lsof -t -i :8080)           # Graceful
kill -9 $(lsof -t -i :8080)       # Force (if graceful didn't work)

# FIX (Windows):
# Find PID from netstat output, then:
taskkill /PID <pid> /F

# FIX (if it's a leftover Docker container):
docker ps | grep 8080
docker stop <container-id>

# VERIFY:
lsof -i :8080  # Should return nothing
```

### Process won't die

```bash
# DIAGNOSE:
ps aux | grep <process-name>
# Note the PID

# ESCALATION LADDER:
kill <pid>                # SIGTERM (graceful shutdown)
sleep 5
kill -9 <pid>             # SIGKILL (cannot be caught, immediate death)

# If SIGKILL doesn't work, it's a zombie or kernel-stuck process:
# Check if zombie:
ps aux | grep <pid>
# State "Z" = zombie. The parent must reap it:
kill -SIGCHLD $(ps -o ppid= -p <pid>)
# Or kill the parent process

# If truly stuck in kernel (state "D"):
# Only a reboot will fix it. The process is stuck in an I/O syscall.

# MASS CLEANUP: Kill all processes matching a name
pkill -f <pattern>          # Graceful
pkill -9 -f <pattern>      # Force
```

### Out of memory (OOM killed)

```bash
# DIAGNOSE: Was your process OOM-killed?
dmesg | grep -i "oom\|killed process" | tail -20
journalctl -k | grep -i "oom\|killed" | tail -20

# Check what's using memory right now:
ps aux --sort=-%mem | head -20        # Top memory consumers
free -h                                 # System memory overview

# FIX: Free memory immediately
# 1. Kill the biggest consumer (if safe to do so)
kill $(ps aux --sort=-%mem | awk 'NR==2{print $2}')

# 2. Drop filesystem caches (safe, no data loss)
sync && echo 3 | sudo tee /proc/sys/vm/drop_caches

# 3. Disable swap thrashing (if swap is full)
sudo swapoff -a && sudo swapon -a

# PREVENT: Set memory limits
# Docker:
docker run --memory=512m --memory-swap=1g myapp

# Systemd service:
# Add to [Service] section:
# MemoryMax=512M
# MemoryHigh=400M

# Node.js:
node --max-old-space-size=512 app.js

# VERIFY:
free -h
ps aux --sort=-%mem | head -5
```

---

## Database Emergencies

### Failed migration (partially applied)

```bash
# DIAGNOSE: What state is the database in?
# Check which migrations have run:

# Rails:
rails db:migrate:status

# Django:
python manage.py showmigrations

# Knex/Node:
npx knex migrate:status

# Prisma:
npx prisma migrate status

# Raw SQL — check migration table:
# PostgreSQL/MySQL:
SELECT * FROM schema_migrations ORDER BY version DESC LIMIT 10;
# Or: SELECT * FROM _migrations ORDER BY id DESC LIMIT 10;

# FIX: Roll back the failed migration
# Most frameworks track migration state. Roll back to last good state:

# Rails:
rails db:rollback STEP=1

# Django:
python manage.py migrate <app_name> <previous_migration_number>

# Knex:
npx knex migrate:rollback

# FIX (manual): If the framework is confused about state:
# 1. Check what the migration actually did
# 2. Manually undo partial changes
# 3. Delete the migration record from the migrations table
# 4. Fix the migration code
# 5. Re-run

# VERIFY:
# Run the migration again and confirm it applies cleanly
# Check the affected tables/columns exist correctly
```

### Accidentally dropped a table or database

```bash
# PostgreSQL:
# If you have WAL archiving / point-in-time recovery configured:
pg_restore -d mydb /backups/latest.dump -t dropped_table

# If no backup exists, check if the transaction is still open:
# (Only works if you haven't committed yet)
# Just run ROLLBACK; in your SQL session.

# MySQL:
# If binary logging is enabled:
mysqlbinlog /var/log/mysql/mysql-bin.000001 \
  --start-datetime="2026-02-03 10:00:00" \
  --stop-datetime="2026-02-03 10:30:00" > recovery.sql
# Review recovery.sql, then apply

# SQLite:
# If the file still exists, it's fine — SQLite DROP TABLE is within the file
# Restore from backup:
cp /backups/db.sqlite3 ./db.sqlite3

# PREVENTION: Always run destructive SQL in a transaction
BEGIN;
DROP TABLE users;  -- oops
ROLLBACK;          -- saved
```

### Database locked / deadlocked

```bash
# PostgreSQL:
-- Find blocking queries
SELECT pid, usename, state, query, wait_event_type, query_start
FROM pg_stat_activity
WHERE state != 'idle'
ORDER BY query_start;

-- Find locks
SELECT blocked_locks.pid AS blocked_pid,
       blocking_locks.pid AS blocking_pid,
       blocked_activity.query AS blocked_query,
       blocking_activity.query AS blocking_query
FROM pg_catalog.pg_locks blocked_locks
JOIN pg_catalog.pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_catalog.pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
JOIN pg_catalog.pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;

-- Kill blocking query
SELECT pg_terminate_backend(<blocking_pid>);

# MySQL:
SHOW PROCESSLIST;
SHOW ENGINE INNODB STATUS\G  -- Look for "LATEST DETECTED DEADLOCK"
KILL <process_id>;

# SQLite:
# SQLite uses file-level locking. Common fix:
# 1. Find and close all connections
# 2. Check for .db-journal or .db-wal files (active transactions)
# 3. If stuck: cp database.db database-fixed.db && mv database-fixed.db database.db
# This forces SQLite to release the lock by creating a fresh file handle

# VERIFY:
# Run a simple query to confirm database is responsive
SELECT 1;
```

### Connection pool exhausted

```bash
# DIAGNOSE:
# Error messages like: "too many connections", "connection pool exhausted",
# "FATAL: remaining connection slots are reserved for superuser"

# PostgreSQL — check connection count:
SELECT count(*), state FROM pg_stat_activity GROUP BY state;
SELECT max_conn, used, max_conn - used AS available
FROM (SELECT count(*) AS used FROM pg_stat_activity) t,
     (SELECT setting::int AS max_conn FROM pg_settings WHERE name='max_connections') m;

# FIX: Kill idle connections
-- Terminate idle connections older than 5 minutes
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE state = 'idle'
AND query_start < now() - interval '5 minutes';

# FIX: Increase max connections (requires restart)
# postgresql.conf:
# max_connections = 200  (default is 100)

# BETTER FIX: Use a connection pooler
# PgBouncer or pgcat in front of PostgreSQL
# Application-level: set pool size to match your needs
# Node.js (pg): { max: 20 }
# Python (SQLAlchemy): pool_size=20, max_overflow=10
# Go (database/sql): db.SetMaxOpenConns(20)

# VERIFY:
SELECT count(*) FROM pg_stat_activity;
# Should be well below max_connections
```

---

## Deploy Emergencies

### Quick rollback

```bash
# Git-based deploys:
git log --oneline -5 origin/main
git revert HEAD                    # Create a revert commit
git push origin main               # Deploy the revert
# Revert is safer than reset because it preserves history

# Docker/container deploys:
# Roll back to previous image tag
docker pull myapp:previous-tag
docker stop myapp-current
docker run -d --name myapp myapp:previous-tag

# Kubernetes:
kubectl rollout undo deployment/myapp
kubectl rollout status deployment/myapp    # Watch rollback progress

# Heroku:
heroku releases
heroku rollback v<previous-version>

# AWS ECS:
aws ecs update-service --cluster mycluster --service myservice \
  --task-definition myapp:<previous-revision>

# VERIFY:
# Hit the health check endpoint
curl -s -o /dev/null -w "%{http_code}" https://myapp.example.com/health
# Should return 200
```

### Container won't start

```bash
# DIAGNOSE: Why did it fail?
docker logs <container-id> --tail 100
docker inspect <container-id> | grep -A5 "State"

# Common causes and fixes:

# 1. "exec format error" — wrong platform (built for arm64, running on amd64)
docker build --platform linux/amd64 -t myapp .

# 2. "permission denied" — file not executable or wrong user
# In Dockerfile:
RUN chmod +x /app/entrypoint.sh
# Or: USER root before the command, then drop back

# 3. "port already allocated" — another container or process on that port
docker ps -a | grep <port>
docker stop <conflicting-container>

# 4. "no such file or directory" — entrypoint or CMD path is wrong
docker run -it --entrypoint sh myapp  # Get a shell to debug
ls -la /app/                           # Check what's actually there

# 5. Healthcheck failing → container keeps restarting
docker inspect <container-id> --format='{{json .State.Health}}'
# Temporarily disable healthcheck to get logs:
docker run --no-healthcheck myapp

# 6. Out of memory — container OOM killed
docker inspect <container-id> --format='{{.State.OOMKilled}}'
# If true: docker run --memory=1g myapp

# VERIFY:
docker ps  # Container should show "Up" status
docker logs <container-id> --tail 5  # No errors
```

### SSL certificate expired

```bash
# DIAGNOSE: Check certificate expiry
echo | openssl s_client -connect mysite.com:443 -servername mysite.com 2>/dev/null | \
  openssl x509 -noout -dates
# notAfter shows expiry date

# FIX (Let's Encrypt — most common):
sudo certbot renew --force-renewal
sudo systemctl reload nginx   # or: sudo systemctl reload apache2

# FIX (manual certificate):
# 1. Get new certificate from your CA
# 2. Replace files:
sudo cp new-cert.pem /etc/ssl/certs/mysite.pem
sudo cp new-key.pem /etc/ssl/private/mysite.key
# 3. Reload web server
sudo nginx -t && sudo systemctl reload nginx

# FIX (AWS ACM):
# ACM auto-renews if DNS validation is configured.
# If email validation: check the admin email for renewal link
# If stuck: request a new certificate in ACM and update the load balancer

# PREVENTION: Auto-renewal with monitoring
# Cron job to check expiry and alert:
echo '0 9 * * 1 echo | openssl s_client -connect mysite.com:443 2>/dev/null | openssl x509 -checkend 604800 -noout || echo "CERT EXPIRES WITHIN 7 DAYS" | mail -s "SSL ALERT" admin@example.com' | crontab -

# VERIFY:
curl -sI https://mysite.com | head -5
# Should return HTTP/2 200, not certificate errors
```

---

## Access Emergencies

### SSH locked out

```bash
# DIAGNOSE: Why can't you connect?
ssh -vvv user@host  # Verbose output shows where it fails

# Common causes:

# 1. Key not accepted — wrong key, permissions, or authorized_keys issue
ssh -i ~/.ssh/specific_key user@host  # Try explicit key
chmod 600 ~/.ssh/id_rsa               # Fix key permissions
chmod 700 ~/.ssh                       # Fix .ssh dir permissions

# 2. "Connection refused" — sshd not running or firewall blocking
# If you have console access (cloud provider's web console):
sudo systemctl start sshd
sudo systemctl status sshd

# 3. Firewall blocking port 22
# Cloud console:
sudo ufw allow 22/tcp       # Ubuntu
sudo firewall-cmd --add-service=ssh --permanent && sudo firewall-cmd --reload  # CentOS

# 4. Changed SSH port and forgot
# Try common alternate ports:
ssh -p 2222 user@host
ssh -p 22222 user@host
# Or check from console: grep -i port /etc/ssh/sshd_config

# 5. IP changed / DNS stale
ping hostname    # Verify IP resolution
ssh user@<direct-ip>  # Try IP instead of hostname

# 6. Locked out after too many attempts (fail2ban)
# From console:
sudo fail2ban-client set sshd unbanip <your-ip>
# Or wait for the ban to expire (usually 10 min)

# CLOUD PROVIDER ESCAPE HATCHES:
# AWS: EC2 → Instance → Connect → Session Manager (no SSH needed)
# GCP: Compute → VM instances → SSH (browser-based)
# Azure: VM → Serial console
# DigitalOcean: Droplet → Access → Console

# VERIFY:
ssh user@host echo "connection works"
```

### Lost sudo access

```bash
# If you have physical/console access:
# 1. Boot into single-user/recovery mode
#    - Reboot, hold Shift (GRUB), select "recovery mode"
#    - Or add init=/bin/bash to kernel command line

# 2. Remount filesystem read-write
mount -o remount,rw /

# 3. Fix sudo access
usermod -aG sudo <username>    # Debian/Ubuntu
usermod -aG wheel <username>   # CentOS/RHEL
# Or edit directly:
visudo
# Add: username ALL=(ALL:ALL) ALL

# 4. Reboot normally
reboot

# If you have another sudo/root user:
su - other-admin
sudo usermod -aG sudo <locked-user>

# CLOUD: Use the provider's console or reset the instance
# AWS: Create an AMI, launch new instance, mount old root volume, fix
```

---

## Network Emergencies

### Nothing connects (total network failure)

```bash
# DIAGNOSE: Isolate the layer
# 1. Is the network interface up?
ip addr show         # or: ifconfig
ping 127.0.0.1       # Loopback works?

# 2. Can you reach the gateway?
ip route | grep default
ping <gateway-ip>

# 3. Can you reach the internet by IP?
ping 8.8.8.8          # Google DNS
ping 1.1.1.1          # Cloudflare DNS

# 4. Is DNS working?
nslookup google.com
dig google.com

# DECISION TREE:
# ping 127.0.0.1 fails      → network stack broken, restart networking
# ping gateway fails         → local network issue (cable, wifi, DHCP)
# ping 8.8.8.8 fails        → routing/firewall issue
# ping 8.8.8.8 works but    → DNS issue
#   nslookup fails

# FIX: DNS broken
echo "nameserver 8.8.8.8" | sudo tee /etc/resolv.conf
# Or: sudo systemd-resolve --flush-caches

# FIX: Interface down
sudo ip link set eth0 up
sudo dhclient eth0        # Request new DHCP lease

# FIX: Restart networking entirely
sudo systemctl restart NetworkManager    # Desktop Linux
sudo systemctl restart networking        # Server
sudo systemctl restart systemd-networkd  # Systemd-based

# Docker: Container can't reach the internet
docker run --rm alpine ping 8.8.8.8  # Test from container
# If fails:
sudo systemctl restart docker    # Often fixes Docker networking
# Or: docker network prune
```

### DNS not propagating after change

```bash
# DIAGNOSE: Check what different DNS servers see
dig @8.8.8.8 mysite.com        # Google
dig @1.1.1.1 mysite.com        # Cloudflare
dig @ns1.yourdns.com mysite.com # Authoritative nameserver

# Check TTL (time remaining before caches expire):
dig mysite.com | grep -i ttl

# REALITY CHECK:
# DNS propagation takes time. TTL controls this.
# TTL 300 = 5 minutes. TTL 86400 = 24 hours.
# You cannot speed this up. You can only wait.

# FIX: If authoritative nameserver has wrong records
# Update the record at your DNS provider (Cloudflare, Route53, etc.)
# Then flush your local cache:
# macOS:
sudo dscacheutil -flushcache && sudo killall -HUP mDNSResponder
# Linux:
sudo systemd-resolve --flush-caches
# Windows:
ipconfig /flushdns

# WORKAROUND: While waiting for propagation
# Add to /etc/hosts for immediate local effect:
echo "93.184.216.34 mysite.com" | sudo tee -a /etc/hosts
# Remove this after propagation completes!

# VERIFY:
dig +short mysite.com  # Should show new IP/record
```

---

## File Emergencies

### Accidentally deleted files (not in git)

```bash
# DIAGNOSE: Are the files recoverable?

# If the process still has the file open:
lsof | grep deleted
# Then recover from /proc:
cp /proc/<pid>/fd/<fd-number> /path/to/restored-file

# If recently deleted on ext4 (Linux):
# Install extundelete or testdisk
sudo extundelete /dev/sda1 --restore-file path/to/file
# Or use testdisk interactively for a better UI

# macOS:
# Check Trash first: ~/.Trash/
# Time Machine: tmutil restore /path/to/file

# PREVENTION:
# Use trash-cli instead of rm:
# npm install -g trash-cli
# trash file.txt  (moves to trash instead of permanent delete)
# Or alias: alias rm='echo "Use trash instead"; false'
```

### Wrong permissions applied recursively

```bash
# "I ran chmod -R 777 /" or "chmod -R 000 /important/dir"

# FIX: Common default permissions
# For a web project:
find /path -type d -exec chmod 755 {} \;  # Directories: rwxr-xr-x
find /path -type f -exec chmod 644 {} \;  # Files: rw-r--r--
find /path -name "*.sh" -exec chmod 755 {} \;  # Scripts: executable

# For SSH:
chmod 700 ~/.ssh
chmod 600 ~/.ssh/id_rsa
chmod 644 ~/.ssh/id_rsa.pub
chmod 600 ~/.ssh/authorized_keys
chmod 644 ~/.ssh/config

# For a system directory (⚠️ serious — may need rescue boot):
# If /etc permissions are broken:
# Boot from live USB, mount the drive, fix permissions
# Reference: dpkg --verify (Debian) or rpm -Va (RHEL) to compare against package defaults

# VERIFY:
ls -la /path/to/fixed/directory
```

---

## The Universal Diagnostic

When you don't know what's wrong, run this sequence:

```bash
#!/bin/bash
# emergency-diagnostic.sh — Quick system health check

echo "=== DISK ==="
df -h | grep -E '^/|Filesystem'

echo -e "\n=== MEMORY ==="
free -h

echo -e "\n=== CPU / LOAD ==="
uptime

echo -e "\n=== TOP PROCESSES (by CPU) ==="
ps aux --sort=-%cpu | head -6

echo -e "\n=== TOP PROCESSES (by MEM) ==="
ps aux --sort=-%mem | head -6

echo -e "\n=== NETWORK ==="
ping -c 1 -W 2 8.8.8.8 > /dev/null 2>&1 && echo "Internet: OK" || echo "Internet: UNREACHABLE"
ping -c 1 -W 2 $(ip route | awk '/default/{print $3}') > /dev/null 2>&1 && echo "Gateway: OK" || echo "Gateway: UNREACHABLE"

echo -e "\n=== RECENT ERRORS ==="
journalctl -p err --since "1 hour ago" --no-pager | tail -20 2>/dev/null || \
  dmesg | tail -20

echo -e "\n=== DOCKER (if running) ==="
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || echo "Docker not running"
docker system df 2>/dev/null || true

echo -e "\n=== LISTENING PORTS ==="
ss -tlnp 2>/dev/null | head -15 || netstat -tlnp 2>/dev/null | head -15

echo -e "\n=== FAILED SERVICES ==="
systemctl --failed 2>/dev/null || true
```

Run it, read the output, then jump to the relevant section above.

## Tips

- **Revoke credentials before cleaning git history.** The moment a secret is pushed publicly, automated scrapers have it within minutes. Cleaning the history is important but secondary to revocation.
- **`git reflog` is your undo button.** It records every HEAD movement for 30+ days. Lost commits, bad rebases, accidental resets — the reflog has the recovery hash. Learn to read it before you need it.
- **Truncate log files, don't delete them.** `truncate -s 0 file.log` frees disk space instantly while keeping the file handle open. Deleting a log file that a process has open won't free space until the process restarts.
- **`--force-with-lease` instead of `--force`.** Always. It fails if someone else has pushed, preventing you from overwriting their work on top of your recovery.
- **Every recovery operation should end with verification.** Run the diagnostic command, check the output, confirm the fix worked. Don't assume — confirm.
- **Docker is the #1 disk space thief on developer machines.** `docker system prune -a` is almost always safe on development machines and can recover tens of gigabytes.
- **Database emergencies: wrap destructive operations in transactions.** `BEGIN; DROP TABLE users; ROLLBACK;` costs nothing and saves everything. Make it muscle memory.
- **When SSH is locked out, every cloud provider has a console escape hatch.** AWS Session Manager, GCP browser SSH, Azure Serial Console. Know where yours is *before* you need it.
- **The order matters: diagnose → fix → verify.** Skipping diagnosis leads to wrong fixes. Skipping verification leads to false confidence. Follow the sequence every time.
- **Keep this skill installed.** You won't need it most days. The day you do need it, you'll need it immediately.
