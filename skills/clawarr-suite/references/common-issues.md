# Common Issues & Troubleshooting

Comprehensive guide to diagnosing and fixing common *arr stack problems.

## Table of Contents
- [Import Issues](#import-issues)
- [Docker & Container Issues](#docker--container-issues)
- [Path Mapping Problems](#path-mapping-problems)
- [Download Client Issues](#download-client-issues)
- [Permission Problems](#permission-problems)
- [Network & Connectivity](#network--connectivity)
- [Performance Issues](#performance-issues)

---

## Import Issues

### "No files eligible for import"

**Symptoms:**
- Download completes successfully
- Radarr/Sonarr can't see files
- Queue shows "No files found eligible for import"

**Causes & Solutions:**

#### 1. Stale Docker Mounts
**Cause:** Container started before host volumes mounted (common after host reboot)

**Diagnosis:**
```bash
# Check container vs host uptime
docker inspect radarr | grep StartedAt
uptime  # Compare
```

**Fix:**
```bash
docker restart radarr sonarr lidarr
```

Container was holding reference to old (empty) mount point. Restart picks up current mounts.

#### 2. Path Mapping Mismatch
**Cause:** Download client reports different path than Radarr expects

**Example scenario:**
- Download client reports: `/data/torrents/complete/MovieName/`
- Radarr expects: `/downloads/complete/MovieName/`

**Diagnosis:**
```bash
# Check what download client reports
curl -H "X-Api-Key: $KEY" http://host:7878/api/v3/downloadclient | jq

# Check queue for actual path
curl -H "X-Api-Key: $KEY" http://host:7878/api/v3/queue | jq '.records[].outputPath'
```

**Fix:** Settings → Download Clients → Remote Path Mappings
- Add mapping:
  - Remote Path: `/data/torrents/`
  - Local Path: `/downloads/`

#### 3. Wrong Category/Directory
**Cause:** Download client put file in unexpected location

**Diagnosis:**
```bash
# Check download client category config
# In qBittorrent: Tools → Options → Downloads → Category

# Check what Radarr expects
curl -H "X-Api-Key: $KEY" http://host:7878/api/v3/downloadclient | jq
```

**Fix:**
- Ensure download client category matches Radarr configuration
- Or update Radarr's download client category setting

#### 4. Permissions
**Cause:** Radarr user can't read download directory

**Diagnosis:**
```bash
# Exec into container
docker exec -it radarr bash

# Try to list files
ls -la /downloads/complete/

# Check ownership
ls -lnd /downloads/complete/
```

**Fix:**
```bash
# Option 1: Fix permissions on host
sudo chown -R 1000:1000 /path/to/downloads  # Match container user

# Option 2: Add Radarr user to download group
# In docker-compose.yml:
services:
  radarr:
    user: 1000:1000  # Match download client user
```

#### 5. Incomplete Download
**Cause:** Files still extracting or incomplete

**Diagnosis:**
```bash
# Check queue status
curl -H "X-Api-Key: $KEY" http://host:7878/api/v3/queue | jq '.records[] | {title, status}'
```

**Fix:** Wait for extraction to complete, or check download client for errors

---

## Docker & Container Issues

### Container Won't Start

**Diagnosis:**
```bash
docker logs radarr

# Check port conflicts
docker ps | grep 7878
netstat -an | grep 7878
```

**Common causes:**
- Port already in use
- Permission denied on config directory
- Invalid volume mounts

**Fix:**
```bash
# Change port in docker-compose.yml
ports:
  - "7879:7878"  # Use different external port

# Fix config permissions
sudo chown -R 1000:1000 /path/to/appdata/radarr
```

### Container Constantly Restarting

**Diagnosis:**
```bash
docker logs radarr --tail 100

# Check restart count
docker inspect radarr | grep RestartCount
```

**Common causes:**
- Database corruption
- Out of memory
- Invalid configuration

**Fix:**
```bash
# Database repair
docker exec radarr sqlite3 /config/radarr.db "PRAGMA integrity_check;"

# If corrupted, restore from backup
cd /path/to/appdata/radarr/Backups/scheduled
# Copy most recent .zip, extract radarr.db
```

### Stale Mounts After Host Reboot

**Symptoms:**
- Services worked before reboot
- After reboot, can't see media/downloads

**Fix:**
```bash
# Restart all containers to pick up new mounts
docker restart radarr sonarr lidarr readarr prowlarr bazarr

# Or restart entire compose stack
cd /path/to/docker-compose
docker-compose restart
```

---

## Path Mapping Problems

### Understanding Remote Path Mappings

Remote path mappings translate paths between different systems or containers.

**When needed:**
- Download client on different machine
- Download client in different container with different volume mounts
- Network shares with different mount points

**Example Docker setup:**

Download client (qBittorrent):
```yaml
volumes:
  - /mnt/storage/torrents:/data
```
Reports completed downloads at: `/data/complete/MovieName/`

Radarr:
```yaml
volumes:
  - /mnt/storage/torrents:/downloads
```
Expects downloads at: `/downloads/complete/MovieName/`

**Solution:** Add remote path mapping:
- Remote Path: `/data`
- Local Path: `/downloads`

### Diagnosing Path Issues

```bash
# Get download client config
curl -H "X-Api-Key: $KEY" http://host:7878/api/v3/downloadclient | jq

# Check what paths queue shows
curl -H "X-Api-Key: $KEY" http://host:7878/api/v3/queue | jq '.records[] | {title, outputPath, downloadClient}'

# Exec into both containers and compare
docker exec -it radarr ls -la /downloads
docker exec -it qbittorrent ls -la /data
```

### Testing Path Mappings

```bash
# Trigger manual import to test
curl -X POST http://host:7878/api/v3/command \
  -H "X-Api-Key: $KEY" \
  -d '{"name":"DownloadedMoviesScan"}'

# Check logs for path resolution
docker logs radarr --tail 50 | grep -i path
```

---

## Download Client Issues

### Can't Connect to Download Client

**Diagnosis:**
```bash
# Test connectivity from Radarr container
docker exec -it radarr curl http://qbittorrent:8080

# Check download client credentials
curl -H "X-Api-Key: $KEY" http://host:7878/api/v3/downloadclient | jq
```

**Fix:**
- Verify host/IP is correct
- Check port accessibility
- Confirm credentials
- Test connection in Settings → Download Clients → Test

### Downloads Not Starting

**Diagnosis:**
```bash
# Check indexer health
curl -H "X-Api-Key: $PROWLARR_KEY" http://host:9696/api/v1/indexer | jq '.[] | {name, enable, priority}'

# Check download client queue limit
curl -H "X-Api-Key: $KEY" http://host:7878/api/v3/downloadclient | jq '.[] | {name, protocol, priority}'
```

**Common causes:**
- Indexers down or rate limited
- Download client queue full
- No suitable releases found

**Fix:**
- Test indexers in Prowlarr
- Adjust quality profile if no releases match
- Increase download client queue limit

### Category Mismatch

**Symptom:** Downloads complete but Radarr doesn't see them

**Diagnosis:**
```bash
# Check Radarr's expected category
curl -H "X-Api-Key: $KEY" http://host:7878/api/v3/downloadclient | jq '.[] | {name, category}'

# Check download client's actual category
# In qBittorrent web UI: Right click torrent → Category
```

**Fix:**
- Set matching category in download client settings
- Or update Radarr's download client category setting
- For qBittorrent: Tools → Options → Downloads → Default Save Path per category

---

## Permission Problems

### Understanding Container Users

Most *arr containers run as user `abc` (UID 1000, GID 1000) by default.

**Check container user:**
```bash
docker exec -it radarr id
# Should show: uid=1000(abc) gid=1000(abc)
```

### Permission Denied Errors

**Diagnosis:**
```bash
# Check file ownership on host
ls -lnd /mnt/media/movies
ls -lnd /mnt/downloads

# Check from inside container
docker exec -it radarr ls -la /movies
docker exec -it radarr ls -la /downloads
```

**Fix:**
```bash
# Option 1: Match host ownership to container user
sudo chown -R 1000:1000 /mnt/media
sudo chown -R 1000:1000 /mnt/downloads

# Option 2: Set PUID/PGID in docker-compose.yml
services:
  radarr:
    environment:
      - PUID=1000
      - PGID=1000

# Option 3: Use umask for new files
services:
  radarr:
    environment:
      - UMASK=002  # New files: rw-rw-r--
```

### Permission Best Practices

1. **Single user for all media apps:**
   ```yaml
   # docker-compose.yml
   x-common: &common
     environment:
       - PUID=1000
       - PGID=1000
   
   services:
     radarr:
       <<: *common
     sonarr:
       <<: *common
     qbittorrent:
       <<: *common
   ```

2. **Proper directory ownership:**
   ```bash
   sudo chown -R 1000:1000 /mnt/media
   sudo chown -R 1000:1000 /mnt/downloads
   sudo chmod -R 775 /mnt/media
   sudo chmod -R 775 /mnt/downloads
   ```

3. **Test with manual file:**
   ```bash
   # Create test file as container user
   docker exec -it radarr touch /movies/test.txt
   
   # Check on host
   ls -la /mnt/media/movies/test.txt
   ```

---

## Network & Connectivity

### Can't Access Web UI

**Diagnosis:**
```bash
# Check container is running
docker ps | grep radarr

# Check port binding
docker port radarr

# Test from host
curl http://localhost:7878/api/v3/system/status

# Test from network
curl http://192.168.1.100:7878/api/v3/system/status
```

**Fix:**
```bash
# Firewall on host
sudo ufw allow 7878

# Or use host networking
services:
  radarr:
    network_mode: host
```

### API Key Not Working

**Diagnosis:**
```bash
# Get correct API key
docker exec radarr cat /config/config.xml | grep ApiKey

# Or use /initialize.js endpoint
curl http://host:7878/initialize.js | grep apiKey
```

**Fix:**
- Copy exact key from config.xml
- Regenerate key in Settings → General → Security → API Key → Regenerate

### Connection Timeouts

**Diagnosis:**
```bash
# Check container network
docker exec -it radarr ping 8.8.8.8
docker exec -it radarr curl https://api.themoviedb.org

# Check DNS
docker exec -it radarr nslookup api.themoviedb.org
```

**Fix:**
```bash
# Set DNS in docker-compose.yml
services:
  radarr:
    dns:
      - 8.8.8.8
      - 8.8.4.4
```

---

## Performance Issues

### Slow Search/Import

**Diagnosis:**
```bash
# Check system resources
docker stats radarr

# Check database size
docker exec radarr ls -lh /config/*.db

# Check logs for slow queries
docker logs radarr | grep -i slow
```

**Fix:**
```bash
# Optimize database
docker exec radarr sqlite3 /config/radarr.db "VACUUM;"

# Reduce history retention
# Settings → General → History Cleanup → 30 days

# Disable unused metadata consumers
# Settings → Metadata → Disable unused
```

### High CPU/Memory Usage

**Diagnosis:**
```bash
docker stats --no-stream radarr

# Check for runaway processes
docker exec radarr ps aux
```

**Fix:**
```bash
# Set memory limits in docker-compose.yml
services:
  radarr:
    mem_limit: 1g
    memswap_limit: 1g

# Restart container
docker restart radarr
```

### Database Corruption

**Symptoms:**
- Crashes on startup
- Missing data
- Errors in logs about database

**Fix:**
```bash
# Stop container
docker stop radarr

# Backup current database
cp /path/to/appdata/radarr/radarr.db /path/to/backup/

# Try repair
docker run --rm -v /path/to/appdata/radarr:/config \
  ghcr.io/linuxserver/radarr \
  sqlite3 /config/radarr.db "PRAGMA integrity_check;"

# If failed, restore from backup
cd /path/to/appdata/radarr/Backups/scheduled
unzip radarr_backup_*.zip
cp radarr.db ../../

# Start container
docker start radarr
```

---

## Quick Diagnostic Checklist

When encountering issues, run through:

1. **Check container health:**
   ```bash
   docker ps | grep -E "(radarr|sonarr)"
   docker logs radarr --tail 50
   ```

2. **Check connectivity:**
   ```bash
   curl http://host:7878/api/v3/health -H "X-Api-Key: $KEY"
   ```

3. **Check paths:**
   ```bash
   docker exec -it radarr ls -la /downloads
   docker exec -it radarr ls -la /movies
   ```

4. **Check permissions:**
   ```bash
   docker exec -it radarr id
   ls -lnd /mnt/media/movies
   ```

5. **Check disk space:**
   ```bash
   df -h /mnt/media
   df -h /mnt/downloads
   ```

6. **Check queue:**
   ```bash
   curl -H "X-Api-Key: $KEY" http://host:7878/api/v3/queue | jq
   ```

7. **Run diagnostics script:**
   ```bash
   scripts/diagnose.sh
   ```

---

## Getting Help

When asking for help, provide:

1. Container logs:
   ```bash
   docker logs radarr --tail 100 > radarr.log
   ```

2. System info:
   ```bash
   curl -H "X-Api-Key: $KEY" http://host:7878/api/v3/system/status
   ```

3. Queue status:
   ```bash
   curl -H "X-Api-Key: $KEY" http://host:7878/api/v3/queue
   ```

4. Docker compose configuration (redact passwords)

5. Description of exact error message and when it occurs
