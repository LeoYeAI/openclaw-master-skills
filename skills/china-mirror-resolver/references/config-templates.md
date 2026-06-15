# Configuration Templates

> Detailed configuration templates for each tool. Referenced by SKILL.md Section 5.
> Replace `<MIRROR_URL>` with validated source, `<MIRROR_HOST>` with its hostname.

---

## pip

Config file: `%APPDATA%\pip\pip.ini` (Win) / `~/.pip/pip.conf` (macOS/Linux)

```ini
[global]
index-url = <MIRROR_URL>
trusted-host = <MIRROR_HOST>
```

Or via CLI: `pip config set global.index-url <MIRROR_URL>`

> **Security note**: `trusted-host` disables SSL verification for that host.
> Only use for known institutional mirrors with HTTPS. Prefer mirrors with
> valid certificates that don't require `trusted-host`.

---

## npm / yarn / pnpm

```bash
# npm
npm config set registry <MIRROR_URL>

# yarn v1
yarn config set registry <MIRROR_URL>

# yarn v2+ (Berry)
yarn config set npmRegistryServer <MIRROR_URL>

# pnpm
pnpm config set registry <MIRROR_URL>
```

---

## conda

Config file: `~/.condarc` (all platforms)

```yaml
channels:
  - <MIRROR_BASE>/anaconda/pkgs/main
  - <MIRROR_BASE>/anaconda/pkgs/free
  - <MIRROR_BASE>/anaconda/cloud/conda-forge
  - defaults
show_channel_urls: true
```

---

## Docker

Config file locations:
- Linux: `/etc/docker/daemon.json`
- macOS: `~/.docker/daemon.json` (or Docker Desktop → Settings → Docker Engine)
- Windows: `%USERPROFILE%\.docker\daemon.json` (or Docker Desktop → Settings → Docker Engine)

**IMPORTANT: Merge, don't overwrite.** Read existing daemon.json first, then
add/update only the `registry-mirrors` field. Example merge logic:

```bash
# Linux / macOS — safe merge with jq
DAEMON_JSON="/etc/docker/daemon.json"
MIRRORS='["https://docker.1ms.run","https://docker.xuanyuan.me"]'

if [ -f "$DAEMON_JSON" ]; then
    # Merge: preserve existing fields, update registry-mirrors
    sudo cp "$DAEMON_JSON" "${DAEMON_JSON}.bak"
    jq --argjson mirrors "$MIRRORS" '. + {"registry-mirrors": $mirrors}' "$DAEMON_JSON" | sudo tee "${DAEMON_JSON}.tmp" > /dev/null
    sudo mv "${DAEMON_JSON}.tmp" "$DAEMON_JSON"
else
    echo "{\"registry-mirrors\": $MIRRORS}" | sudo tee "$DAEMON_JSON" > /dev/null
fi
sudo systemctl daemon-reload && sudo systemctl restart docker
```

```powershell
# Windows PowerShell — safe merge
$daemonJson = "$env:USERPROFILE\.docker\daemon.json"
$mirrors = @("https://docker.1ms.run", "https://docker.xuanyuan.me")

if (Test-Path $daemonJson) {
    Copy-Item $daemonJson "$daemonJson.bak"
    $config = Get-Content $daemonJson -Raw | ConvertFrom-Json
} else {
    $config = [PSCustomObject]@{}
}
$config | Add-Member -NotePropertyName "registry-mirrors" -NotePropertyValue $mirrors -Force
$config | ConvertTo-Json -Depth 10 | Set-Content $daemonJson -Encoding UTF8
Write-Host "Restart Docker Desktop to apply changes."
```

---

## Go

```bash
go env -w GOPROXY=<MIRROR_URL>,direct
go env -w GOSUMDB=sum.golang.google.cn
```

---

## Rust (cargo)

Config file: `~/.cargo/config.toml` (Linux/macOS) / `%USERPROFILE%\.cargo\config.toml` (Win)

```toml
[source.crates-io]
replace-with = "mirror"

[source.mirror]
registry = "<MIRROR_URL>"
```

## Rust (rustup)

```bash
# Linux / macOS — add to ~/.bashrc or ~/.zshrc
export RUSTUP_DIST_SERVER=<RUSTUP_MIRROR>
export RUSTUP_UPDATE_ROOT=<RUSTUP_MIRROR>/rustup
```

```powershell
# Windows — set persistent environment variable
[System.Environment]::SetEnvironmentVariable("RUSTUP_DIST_SERVER", "<RUSTUP_MIRROR>", "User")
[System.Environment]::SetEnvironmentVariable("RUSTUP_UPDATE_ROOT", "<RUSTUP_MIRROR>/rustup", "User")
```

---

## Maven

Config file: `~/.m2/settings.xml` (Linux/macOS) / `C:\Users\<user>\.m2\settings.xml` (Win)

```xml
<settings>
  <mirrors>
    <mirror>
      <id>china-mirror</id>
      <mirrorOf>central</mirrorOf>
      <url><MIRROR_URL></url>
    </mirror>
  </mirrors>
</settings>
```

---

## Gradle

### Groovy DSL (`build.gradle` or `~/.gradle/init.gradle`)

```groovy
allprojects {
    repositories {
        maven { url '<MIRROR_URL>' }
        mavenCentral()
    }
}
```

### Kotlin DSL (`build.gradle.kts` or `~/.gradle/init.gradle.kts`)

```kotlin
allprojects {
    repositories {
        maven(url = "<MIRROR_URL>")
        mavenCentral()
    }
}
```

---

## Homebrew (macOS / Linuxbrew)

Add to `~/.zshrc` or `~/.bash_profile`:

```bash
export HOMEBREW_BREW_GIT_REMOTE="<MIRROR_BASE>/git/homebrew/brew.git"
export HOMEBREW_CORE_GIT_REMOTE="<MIRROR_BASE>/git/homebrew/homebrew-core.git"
export HOMEBREW_BOTTLE_DOMAIN="<MIRROR_BASE>/homebrew-bottles"
```

---

## apt (Debian / Ubuntu)

Edit `/etc/apt/sources.list`: replace `archive.ubuntu.com` and `security.ubuntu.com`
with `<MIRROR_HOST>`, then run `sudo apt update`.

Example for Ubuntu 22.04:
```
deb https://<MIRROR_HOST>/ubuntu/ jammy main restricted universe multiverse
deb https://<MIRROR_HOST>/ubuntu/ jammy-updates main restricted universe multiverse
deb https://<MIRROR_HOST>/ubuntu/ jammy-security main restricted universe multiverse
```

---

## yum / dnf (CentOS / RHEL / Fedora)

```bash
# 1. Backup
sudo cp -r /etc/yum.repos.d /etc/yum.repos.d.bak

# 2. Replace mirror (CentOS example)
# Option A: Use sed (verify result before applying)
sudo sed -i.bak 's|mirrorlist=|#mirrorlist=|g' /etc/yum.repos.d/CentOS-*.repo
sudo sed -i 's|#baseurl=http://mirror.centos.org|baseurl=https://<MIRROR_HOST>|g' /etc/yum.repos.d/CentOS-*.repo

# Option B: Download provider's pre-made repo file (safer)
# e.g., Aliyun: curl -o /etc/yum.repos.d/CentOS-Base.repo https://mirrors.aliyun.com/repo/Centos-7.repo

# 3. Rebuild cache
sudo yum makecache
```

> **Caution**: Always verify sed results with `cat /etc/yum.repos.d/CentOS-*.repo`
> before running `yum makecache`. If the regex matched incorrectly, restore from backup.

---

## GitHub Accelerator

Prepend accelerator prefix to the clone URL:

```bash
git clone <ACCEL_PREFIX>https://github.com/<owner>/<repo>.git
# Example:
git clone https://ghfast.top/https://github.com/torvalds/linux.git
```

---

## Hugging Face

```bash
# Linux / macOS — add to ~/.bashrc or ~/.zshrc
export HF_ENDPOINT=<MIRROR_URL>
```

```powershell
# Windows PowerShell — session only
$env:HF_ENDPOINT = "<MIRROR_URL>"

# Windows — persistent
[System.Environment]::SetEnvironmentVariable("HF_ENDPOINT", "<MIRROR_URL>", "User")
```
