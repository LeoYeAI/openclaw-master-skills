# Setup Guide

Step-by-step setup instructions for ClawARR Suite across common platforms.

## Table of Contents
- [Docker Compose](#docker-compose)
- [Unraid](#unraid)
- [Synology DSM](#synology-dsm)
- [Bare Metal](#bare-metal)
- [First-Time Configuration](#first-time-configuration)

---

## Docker Compose

Recommended setup using docker-compose for maximum flexibility and portability.

### Prerequisites

```bash
# Install Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Verify
docker --version
docker-compose --version
```

### Directory Structure

```bash
mkdir -p /mnt/storage/{media,downloads,appdata}
cd /mnt/storage

# Media structure
mkdir -p media/{movies,tv,music,books}

# Download structure
mkdir -p downloads/{movies,tv,music,books}

# Appdata for configs
mkdir -p appdata/{radarr,sonarr,lidarr,readarr,prowlarr,bazarr,overseerr,plex,tautulli,qbittorrent}
```

### docker-compose.yml

Create `/opt/media-stack/docker-compose.yml`:

```yaml
version: "3.8"

x-common: &common
  restart: unless-stopped
  environment:
    - PUID=1000
    - PGID=1000
    - TZ=America/Chicago

services:
  radarr:
    <<: *common
    image: lscr.io/linuxserver/radarr:latest
    container_name: radarr
    volumes:
      - /mnt/storage/appdata/radarr:/config
      - /mnt/storage/media/movies:/movies
      - /mnt/storage/downloads:/downloads
    ports:
      - "7878:7878"

  sonarr:
    <<: *common
    image: lscr.io/linuxserver/sonarr:latest
    container_name: sonarr
    volumes:
      - /mnt/storage/appdata/sonarr:/config
      - /mnt/storage/media/tv:/tv
      - /mnt/storage/downloads:/downloads
    ports:
      - "8989:8989"

  lidarr:
    <<: *common
    image: lscr.io/linuxserver/lidarr:latest
    container_name: lidarr
    volumes:
      - /mnt/storage/appdata/lidarr:/config
      - /mnt/storage/media/music:/music
      - /mnt/storage/downloads:/downloads
    ports:
      - "8686:8686"

  readarr:
    <<: *common
    image: lscr.io/linuxserver/readarr:develop
    container_name: readarr
    volumes:
      - /mnt/storage/appdata/readarr:/config
      - /mnt/storage/media/books:/books
      - /mnt/storage/downloads:/downloads
    ports:
      - "8787:8787"

  prowlarr:
    <<: *common
    image: lscr.io/linuxserver/prowlarr:latest
    container_name: prowlarr
    volumes:
      - /mnt/storage/appdata/prowlarr:/config
    ports:
      - "9696:9696"

  bazarr:
    <<: *common
    image: lscr.io/linuxserver/bazarr:latest
    container_name: bazarr
    volumes:
      - /mnt/storage/appdata/bazarr:/config
      - /mnt/storage/media/movies:/movies
      - /mnt/storage/media/tv:/tv
    ports:
      - "6767:6767"

  overseerr:
    <<: *common
    image: lscr.io/linuxserver/overseerr:latest
    container_name: overseerr
    volumes:
      - /mnt/storage/appdata/overseerr:/config
    ports:
      - "5055:5055"

  qbittorrent:
    <<: *common
    image: lscr.io/linuxserver/qbittorrent:latest
    container_name: qbittorrent
    volumes:
      - /mnt/storage/appdata/qbittorrent:/config
      - /mnt/storage/downloads:/downloads
    ports:
      - "8080:8080"
      - "6881:6881"
      - "6881:6881/udp"

  plex:
    <<: *common
    image: lscr.io/linuxserver/plex:latest
    container_name: plex
    network_mode: host
    volumes:
      - /mnt/storage/appdata/plex:/config
      - /mnt/storage/media:/media
    environment:
      - VERSION=docker
      - PLEX_CLAIM=claim-xxxxxxxxxxxx  # Get from plex.tv/claim

  tautulli:
    <<: *common
    image: lscr.io/linuxserver/tautulli:latest
    container_name: tautulli
    volumes:
      - /mnt/storage/appdata/tautulli:/config
    ports:
      - "8181:8181"
```

### Start Stack

```bash
cd /opt/media-stack
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f radarr
```

### Set Permissions

```bash
sudo chown -R 1000:1000 /mnt/storage
sudo chmod -R 775 /mnt/storage
```

---

## Unraid

Unraid users can use Community Applications (CA) for easy installation.

### Install Apps via Community Applications

1. Open Unraid web UI → Apps
2. Search and install each app:
   - **Radarr** (by binhex or linuxserver)
   - **Sonarr** (by binhex or linuxserver)
   - **Lidarr** (by linuxserver)
   - **Readarr** (by linuxserver)
   - **Prowlarr** (by linuxserver)
   - **Bazarr** (by linuxserver)
   - **Overseerr** (by linuxserver)
   - **qBittorrent** (by binhex)
   - **Plex** (official)
   - **Tautulli** (by linuxserver)

### Recommended Paths

Configure each container with consistent paths:

**Storage:**
- Media: `/mnt/user/media/`
  - Movies: `/mnt/user/media/movies/`
  - TV: `/mnt/user/media/tv/`
  - Music: `/mnt/user/media/music/`
  - Books: `/mnt/user/media/books/`
- Downloads: `/mnt/user/downloads/`
- Appdata: `/mnt/user/appdata/<appname>/`

**Container paths (map to above):**
- `/movies` → `/mnt/user/media/movies`
- `/tv` → `/mnt/user/media/tv`
- `/music` → `/mnt/user/media/music`
- `/books` → `/mnt/user/media/books`
- `/downloads` → `/mnt/user/downloads`

### User/Group Settings

Set consistent PUID/PGID across all containers:
- PUID: `99` (default Unraid nobody user)
- PGID: `100` (default Unraid users group)

### Network

Use bridge networking for all except Plex:
- **Most apps:** Bridge mode
- **Plex:** Host mode (for discovery)

---

## Synology DSM

Run *arr stack on Synology NAS using Docker.

### Enable Docker

1. Package Center → Search "Docker"
2. Install "Container Manager" (Docker)

### Create Folders

File Station → Create structure:
```
/volume1/docker/
  ├── radarr/
  ├── sonarr/
  ├── lidarr/
  ├── prowlarr/
  ├── overseerr/
  └── ...

/volume1/media/
  ├── movies/
  ├── tv/
  ├── music/
  └── books/

/volume1/downloads/
```

### Import Compose File

1. Container Manager → Project → Create
2. Project name: `media-stack`
3. Paste docker-compose.yml (see Docker Compose section above)
4. Adjust paths:
   - `/mnt/storage` → `/volume1`
   - PUID/PGID: Use your Synology user ID (usually 1026+)

Find your UID:
```bash
# SSH into Synology
ssh admin@synology-ip

# Get UID
id
```

### Network Configuration

1. Control Panel → Network → Network Interface
2. Note your NAS IP (e.g., 192.168.1.100)
3. Access apps via `http://192.168.1.100:<port>`

### Firewall Rules

Control Panel → Security → Firewall → Edit Rules → Create:
- Ports: 7878, 8989, 8686, 8787, 9696, 6767, 5055, 8080, 32400, 8181
- Source IP: Your local network (192.168.1.0/24)

---

## Bare Metal

Install directly on Linux server without containers.

### System Requirements

- Ubuntu 20.04+ or Debian 11+
- 2GB RAM minimum (4GB recommended)
- 20GB storage for apps
- Separate storage for media

### Install Dependencies

```bash
sudo apt update
sudo apt install -y curl wget sqlite3 mediainfo
```

### Install Radarr

```bash
# Add repository
sudo apt install -y gnupg
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 0xA236C58F409091A18ACA53CBEBFF6B99D9B78493
echo "deb https://radarr.servarr.com/apt/ubuntu focal main" | sudo tee /etc/apt/sources.list.d/radarr.list

# Install
sudo apt update
sudo apt install radarr

# Enable service
sudo systemctl enable --now radarr

# Access at http://localhost:7878
```

### Install Sonarr

```bash
sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 0x2009837CBFFD68F45BC180471F4F90DE2A9B4BF8
echo "deb https://apt.sonarr.tv/ubuntu focal main" | sudo tee /etc/apt/sources.list.d/sonarr.list
sudo apt update
sudo apt install sonarr
sudo systemctl enable --now sonarr
```

### Install Others

**Lidarr:**
```bash
curl -s https://lidarr.audio/install.sh | sudo bash
sudo systemctl enable --now lidarr
```

**Prowlarr:**
```bash
wget https://github.com/Prowlarr/Prowlarr/releases/download/v1.15.0.4308/Prowlarr.master.1.15.0.4308.linux-core-x64.tar.gz
tar -xvzf Prowlarr*.tar.gz -C /opt/
sudo chown -R $USER:$USER /opt/Prowlarr

# Create systemd service
sudo tee /etc/systemd/system/prowlarr.service > /dev/null <<EOF
[Unit]
Description=Prowlarr
After=network.target

[Service]
Type=simple
User=$USER
ExecStart=/opt/Prowlarr/Prowlarr -nobrowser -data=/home/$USER/.config/Prowlarr
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now prowlarr
```

### User Permissions

```bash
# Create media user
sudo useradd -r -s /bin/false media

# Set ownership
sudo chown -R media:media /mnt/media
sudo chown -R media:media /mnt/downloads

# Add your user to media group
sudo usermod -aG media $USER
```

---

## First-Time Configuration

After installation on any platform:

### 1. Get API Keys

Use ClawARR discovery:
```bash
export CLAWARR_HOST=192.168.1.100
scripts/discover.sh $CLAWARR_HOST
```

Get API keys via `/initialize.js`:
```bash
# Radarr
curl -s http://192.168.1.100:7878/initialize.js | grep -o "apiKey: '[^']*'" | cut -d"'" -f2

# Sonarr
curl -s http://192.168.1.100:8989/initialize.js | grep -o "apiKey: '[^']*'" | cut -d"'" -f2

# Repeat for Lidarr (8686), Readarr (8787), Prowlarr (9696)
```

Or get from config files:
```bash
# Docker
docker exec radarr cat /config/config.xml | grep ApiKey

# Unraid
cat /mnt/user/appdata/radarr/config.xml | grep ApiKey

# Synology
cat /volume1/docker/radarr/config.xml | grep ApiKey

# Bare metal
cat ~/.config/Radarr/config.xml | grep ApiKey
```

### 2. Configure Prowlarr (Indexers)

1. Open Prowlarr web UI (http://host:9696)
2. Settings → General → Copy API Key
3. Indexers → Add Indexer → Search for indexers
4. Add public indexers or configure private trackers
5. Apps → Add Application:
   - Type: Radarr
   - Prowlarr Server: http://localhost:9696
   - Radarr Server: http://radarr:7878 (Docker) or http://localhost:7878
   - API Key: (Radarr API key)
   - Sync Level: Full Sync
6. Repeat for Sonarr, Lidarr, Readarr

### 3. Configure Download Client

**qBittorrent:**
1. Open qBittorrent (http://host:8080)
2. Default login: admin/adminadmin (change immediately!)
3. Tools → Options:
   - Downloads → Default Save Path: `/downloads` (Docker) or full path
   - Downloads → Category: Create categories for movies, tv, music, books
   - Web UI → Enable authentication

**Add to Radarr:**
1. Settings → Download Clients → Add → qBittorrent
2. Host: `qbittorrent` (Docker) or `localhost`
3. Port: 8080
4. Username/Password: (qBittorrent credentials)
5. Category: `movies`
6. Test → Save

Repeat for Sonarr (category: `tv`), Lidarr (category: `music`), etc.

### 4. Configure Quality Profiles

**Radarr:**
1. Settings → Profiles → Add
2. Name: "HD"
   - Allowed: Bluray-1080p, WEB-1080p
   - Upgrade Until: Bluray-1080p
3. Name: "4K"
   - Allowed: Bluray-2160p, WEB-2160p

**Sonarr:**
1. Settings → Profiles → Add
2. Name: "HD-1080p"
   - Allowed: HDTV-1080p, WEB-1080p, Bluray-1080p
   - Upgrade Until: Bluray-1080p

### 5. Add Root Folders

**Radarr:**
- Settings → Media Management → Root Folders → Add Root Folder
- Path: `/movies` (Docker) or `/mnt/media/movies` (full path)

**Sonarr:**
- Path: `/tv` or `/mnt/media/tv`

**Lidarr:**
- Path: `/music` or `/mnt/media/music`

### 6. Configure Plex

1. Open Plex (http://host:32400/web)
2. Sign in with Plex account
3. Add Libraries:
   - Movies → `/media/movies` (Docker) or `/mnt/storage/media/movies`
   - TV Shows → `/media/tv`
   - Music → `/media/music`

Get Plex token for API:
1. Play any item in Plex web
2. Click ⋮ → Get Info → View XML
3. URL contains: `X-Plex-Token=xxxxxxxxxxxx`
4. Save this token

### 7. Configure Overseerr

1. Open Overseerr (http://host:5055)
2. Sign in with Plex
3. Settings → Plex:
   - Server: Select your Plex server
   - Libraries: Select Movies & TV Shows
4. Settings → Services:
   - Add Radarr:
     - Default: Yes
     - Server: http://radarr:7878 (Docker) or http://localhost:7878
     - API Key: (Radarr key)
     - Root Folder: /movies
     - Quality Profile: HD
   - Add Sonarr:
     - Server: http://sonarr:8989
     - API Key: (Sonarr key)
     - Root Folder: /tv
     - Quality Profile: HD-1080p

### 8. Test with ClawARR

```bash
# Set environment
export CLAWARR_HOST=192.168.1.100
export RADARR_KEY=xxxx
export SONARR_KEY=yyyy
export OVERSEERR_KEY=zzzz

# Check status
scripts/status.sh

# Search
scripts/search.sh "dune" movie

# Check queue
scripts/queue.sh
```

### 9. Store Configuration

Create `.env` file:
```bash
# ~/.clawarr.env
CLAWARR_HOST=192.168.1.100
SONARR_KEY=abc123...
RADARR_KEY=def456...
LIDARR_KEY=ghi789...
READARR_KEY=jkl012...
PROWLARR_KEY=mno345...
BAZARR_KEY=pqr678...
OVERSEERR_KEY=stu901...
PLEX_TOKEN=vwx234...
TAUTULLI_KEY=yz567...
```

Source before using scripts:
```bash
source ~/.clawarr.env
scripts/status.sh
```

---

## Troubleshooting Setup

### Services Not Starting

**Check logs:**
```bash
# Docker
docker logs radarr

# Bare metal
sudo journalctl -u radarr -f
```

### Can't Access Web UI

**Check firewall:**
```bash
# Ubuntu/Debian
sudo ufw status
sudo ufw allow 7878

# Check if port is listening
sudo netstat -tlnp | grep 7878
```

### Permission Errors

**Docker:**
```bash
sudo chown -R 1000:1000 /mnt/storage
```

**Bare metal:**
```bash
sudo chown -R media:media /mnt/media
sudo chmod -R 775 /mnt/media
```

### Import Not Working

See [Common Issues](common-issues.md) for detailed troubleshooting.

---

## Next Steps

After setup:
1. ✅ Run `scripts/diagnose.sh` to verify everything
2. ✅ Test adding content via Overseerr
3. ✅ Monitor first download to ensure import works
4. ✅ Set up Bazarr for subtitles
5. ✅ Configure Tautulli for Plex stats

Enjoy your fully automated media stack! 🎬📺🎵
