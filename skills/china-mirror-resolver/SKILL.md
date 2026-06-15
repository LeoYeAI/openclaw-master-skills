---
name: china-mirror-resolver
description: >
  Self-healing China mirror source resolver. Automatically discovers, validates,
  and configures domestic mirror sources for pip/npm/yarn/pnpm/conda/Docker/Go/
  Rust/Maven/Gradle/Homebrew/apt/yum/GitHub/HuggingFace when downloads are slow
  or timing out in mainland China. Trigger keywords: "换源", "镜像源", "下载慢",
  "超时", "timeout", "mirror", "registry", "proxy", "connection refused",
  "SSL error", "443", "ETIMEDOUT", "CondaHTTPError", "pip install failed".
version: 2.1.0
license: MIT
homepage: https://github.com/The-Ladder-of-Rrogress/china-mirror-resolver
compatibility: >
  Requires terminal/shell access and internet connectivity.
  Works on Windows (PowerShell), macOS (bash/zsh), and Linux (bash).
  Designed for Claude Code, StepFun, and similar agentic coding assistants.
  Adaptable to Cursor (.mdc rules) and Windsurf (.md rules) — see Section 9.
  Agents without web search capability can still use baseline sources (Section 2).
metadata:
  author: community
  category: devtools
  region: china-mainland
  last-verified: "2026-03-08"
  clawdbot:
    emoji: "🪞"
    files: ["scripts/*", "references/*"]
allowed-tools: WebSearch WebFetch terminal file-read file-write
---

# China Mirror Resolver

> Mirror URLs break frequently. This skill teaches the agent a **self-healing
> workflow**: discover → validate → configure the best available source.
> A baseline table provides offline fallback; web search enables self-repair.

---

## Execution Flow

```
User error / request
      │
      ▼
 1. Identify tool type (Section 1)
      │
      ▼
 2. Detect current source config
      │
      ▼
 3. Try ALL baseline sources for that tool (Section 2)
    Validate each with Section 4 thresholds (< 3s = good, 3–10s = acceptable)
      ├─ At least one source < 10s → pick fastest → go to step 6
      └─ All sources > 10s or failed ↓
      ▼
 4. [IF search capable] Search for latest sources (Section 3)
      ├─ Found candidates → go to step 5
      └─ No candidates found → report to user with baseline table as reference
    [IF no search] Report baseline failure to user, suggest manual URL
      │
      ▼
 5. Validate ALL candidates (Section 4), pick fastest passing one
      ├─ At least one passes → go to step 6
      └─ All fail → report failure to user, suggest checking network/proxy
      │
      ▼
 6. Backup original config → write new config → verify with test command
      │
      ▼
 7. Confirm result to user (show old source → new source, response time)
```

> **Graceful degradation**: If the agent has no web search capability, skip
> step 4 and use only the baseline table. The skill remains functional with
> reduced self-healing ability.

> **Speed selection**: When multiple sources pass validation, always select
> the one with the lowest response time. Test all candidates, not just the first.

---

## 1. Diagnostic Table

Match error keywords to identify the tool, then check current config:

| Error keywords | Tool | Detect current source |
|---|---|---|
| `pip` / `PyPI` / `setup.py` / `No matching distribution` | pip | `pip config get global.index-url` |
| `npm ERR` / `FETCH_ERROR` | npm | `npm config get registry` |
| `yarn` / `ESOCKETTIMEDOUT` | yarn | `yarn config get registry` (v1) / `yarn config get npmRegistryServer` (v2+) |
| `pnpm` / `ERR_PNPM` | pnpm | `pnpm config get registry` |
| `conda` / `CondaHTTPError` / `PackagesNotFoundError` | conda | `conda config --show channels` |
| `docker` / `pull` / `manifest` / `toomanyrequests` | Docker | Linux/macOS: `docker info \| grep -A5 "Registry Mirrors"` / Win: Docker Desktop → Settings → Docker Engine |
| `go: downloading` / `GOPROXY` / `dial tcp` | Go | `go env GOPROXY` |
| `cargo` / `crates.io` / `Blocking waiting` | Rust (cargo) | check `~/.cargo/config.toml` (Linux/macOS) or `%USERPROFILE%\.cargo\config.toml` (Win) |
| `rustup` / `could not download` | Rust (rustup) | `echo $RUSTUP_DIST_SERVER` / `$env:RUSTUP_DIST_SERVER` |
| `maven` / `pom.xml` / `BUILD FAILURE` / `Could not resolve` | Maven | check `~/.m2/settings.xml` or `C:\Users\<user>\.m2\settings.xml` |
| `gradle` / `Could not resolve` / `build.gradle` | Gradle | check `build.gradle` / `build.gradle.kts` or `~/.gradle/init.gradle` |
| `brew` / `Homebrew` / `Fetching` | Homebrew | `echo $HOMEBREW_BOTTLE_DOMAIN` |
| `apt` / `dpkg` / `E: Failed to fetch` | apt (Debian/Ubuntu) | check `/etc/apt/sources.list` |
| `yum` / `dnf` / `Cannot find a valid baseurl` | yum/dnf (CentOS/RHEL/Fedora) | check `/etc/yum.repos.d/` |
| `git clone` / `github.com` / `RPC failed` | GitHub accelerator | N/A |
| `huggingface` / `hf_hub` / `ConnectionError` | Hugging Face | `echo $HF_ENDPOINT` / `$env:HF_ENDPOINT` |

---

## 2. Baseline Sources

> High-stability institutional mirrors. Try these first. If all fail or are
> too slow (> 10s), proceed to Section 3 (search).
> Agents without search capability stop here.

### pip
| Provider | URL |
|---|---|
| Tsinghua TUNA | `https://pypi.tuna.tsinghua.edu.cn/simple` |
| Aliyun | `https://mirrors.aliyun.com/pypi/simple/` |
| USTC | `https://pypi.mirrors.ustc.edu.cn/simple/` |
| Tencent | `https://mirrors.cloud.tencent.com/pypi/simple/` |

### npm / yarn / pnpm
| Provider | URL |
|---|---|
| npmmirror | `https://registry.npmmirror.com` |
| Huawei | `https://repo.huaweicloud.com/repository/npm/` |

### conda
| Provider | URL |
|---|---|
| Tsinghua TUNA | `https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main` |
| USTC | `https://mirrors.ustc.edu.cn/anaconda/pkgs/main` |
| Aliyun | `https://mirrors.aliyun.com/anaconda/pkgs/main` |

### Docker
| Provider | URL |
|---|---|
| 1ms.run | `https://docker.1ms.run` |
| xuanyuan.me | `https://docker.xuanyuan.me` |
| DaoCloud | `https://docker.m.daocloud.io` |
| linkedbus | `https://docker.linkedbus.com` |

### Go
| Provider | URL |
|---|---|
| goproxy.cn | `https://goproxy.cn` |
| goproxy.io | `https://goproxy.io` |

### Rust
| Provider | cargo registry | rustup server |
|---|---|---|
| USTC | `sparse+https://mirrors.ustc.edu.cn/crates.io-index/` | `https://mirrors.ustc.edu.cn/rustup` |
| Tsinghua TUNA | `sparse+https://mirrors.tuna.tsinghua.edu.cn/crates.io-index/` | `https://mirrors.tuna.tsinghua.edu.cn/rustup` |
| RsProxy.cn | `sparse+https://rsproxy.cn/crates.io-index/` | `https://rsproxy.cn/rustup` |

### Maven / Gradle
| Provider | URL |
|---|---|
| Aliyun Public | `https://maven.aliyun.com/repository/public` |
| Aliyun Google | `https://maven.aliyun.com/repository/google` |
| Huawei | `https://repo.huaweicloud.com/repository/maven` |

### Homebrew (macOS / Linuxbrew)
| Provider | HOMEBREW_BOTTLE_DOMAIN |
|---|---|
| Tsinghua TUNA | `https://mirrors.tuna.tsinghua.edu.cn/homebrew-bottles` |
| USTC | `https://mirrors.ustc.edu.cn/homebrew-bottles` |

### apt (Debian / Ubuntu)
| Provider | Base URL |
|---|---|
| Tsinghua TUNA | `https://mirrors.tuna.tsinghua.edu.cn` |
| Aliyun | `https://mirrors.aliyun.com` |
| USTC | `https://mirrors.ustc.edu.cn` |

### yum / dnf (CentOS / RHEL / Fedora)
| Provider | Base URL |
|---|---|
| Tsinghua TUNA | `https://mirrors.tuna.tsinghua.edu.cn` |
| Aliyun | `https://mirrors.aliyun.com` |
| USTC | `https://mirrors.ustc.edu.cn` |

### GitHub Accelerator
| Provider | Prefix URL |
|---|---|
| ghfast.top | `https://ghfast.top/` |
| gh-proxy.com | `https://gh-proxy.com/` |
| ghp.ci | `https://ghp.ci/` |

### Hugging Face
| Provider | HF_ENDPOINT |
|---|---|
| hf-mirror.com | `https://hf-mirror.com` |

---

## 3. Search Strategy

> **Capability gate**: This section requires web search. If the agent lacks
> search capability, skip to Section 5 using only baseline sources.

### 3.1 Search Query Templates

Replace `<YEAR>` with current year. Use the agent's available search mechanism.
Provide both Chinese and English queries for better coverage:

| Tool | Chinese query | English query |
|---|---|---|
| pip | `pip 国内镜像源 <YEAR> 可用` | `pip china mirror source <YEAR> working` |
| npm | `npm 国内镜像 registry <YEAR>` | `npm china registry mirror <YEAR>` |
| conda | `conda 国内镜像源 channels <YEAR>` | `conda china mirror channel <YEAR>` |
| Docker | `docker 镜像加速源 <YEAR> 可用` | `docker registry mirror china <YEAR> working` |
| Go | `GOPROXY 国内代理 <YEAR>` | `GOPROXY china proxy <YEAR>` |
| Rust | `cargo crates 国内镜像 <YEAR>` | `cargo crates china mirror <YEAR>` |
| Maven | `maven 国内镜像 仓库地址 <YEAR>` | `maven china mirror repository <YEAR>` |
| Homebrew | `homebrew 国内镜像 <YEAR>` | `homebrew china mirror <YEAR>` |
| apt | `ubuntu apt 国内源 <YEAR>` | `ubuntu apt china mirror <YEAR>` |
| yum/dnf | `centos yum 国内镜像源 <YEAR>` | `centos yum china mirror <YEAR>` |
| GitHub | `github 加速 代理 镜像站 <YEAR>` | `github proxy accelerator china <YEAR>` |
| HuggingFace | `huggingface 国内镜像 下载加速 <YEAR>` | `huggingface china mirror download <YEAR>` |

### 3.2 Source Credibility

Prioritize results in this order:

1. Official mirror site docs (mirrors.tuna.tsinghua.edu.cn/help, developer.aliyun.com/mirror)
2. Mirror provider's own site/README (goproxy.cn, npmmirror.com)
3. Recent posts (< 3 months) from reputable tech communities
4. GitHub repos with > 100 stars that aggregate mirror lists

Reject: undated articles, posts > 6 months old, zero-reply forum threads, unverifiable personal blogs.

### 3.3 Candidate Extraction Rules

Extracted URLs must:
- Use HTTPS protocol
- Belong to known institutions (.edu.cn, major cloud vendors, well-known OSS orgs) OR be cross-referenced in 2+ independent articles
- Come from articles published within the last 6 months

> **Security warning**: Never use mirror sources from unknown individuals or
> unverifiable personal servers. Malicious mirrors can inject tampered packages.
> Especially for Docker and pip, only use sources from recognized institutions.

---

## 4. Validation

**Every candidate must pass validation before being written to config.**

### 4.1 Universal HTTP Check

```bash
# Linux / macOS
start=$(date +%s%N 2>/dev/null || perl -MTime::HiRes=time -e 'printf "%d\n",time()*1e9')
code=$(curl -o /dev/null -s -w "%{http_code}" --max-time 10 "<URL>")
end=$(date +%s%N 2>/dev/null || perl -MTime::HiRes=time -e 'printf "%d\n",time()*1e9')
echo "HTTP $code | $(( (end - start) / 1000000 ))ms"
```

```powershell
# Windows PowerShell
$sw = [System.Diagnostics.Stopwatch]::StartNew()
try { $r = Invoke-WebRequest -Uri "<URL>" -TimeoutSec 10 -UseBasicParsing -ErrorAction Stop
  $sw.Stop(); "OK: HTTP $($r.StatusCode) | $($sw.ElapsedMilliseconds)ms"
} catch { $sw.Stop(); "FAIL: $_" }
```

### 4.2 Tool-Specific Validation

| Tool | Command / Check | Success Criteria |
|---|---|---|
| pip | `pip install --dry-run requests -i <URL> --trusted-host <HOST>` | `Would install` or `already satisfied` |
| npm | `npm view lodash version --registry <URL>` | Returns version number |
| yarn v1 | `yarn info lodash version --registry <URL>` | Returns version number |
| pnpm | `pnpm view lodash version --registry <URL>` | Returns version number |
| conda | `conda search numpy -c <URL> --override-channels` | Returns package list |
| Docker | HTTP GET `<URL>/v2/` | HTTP 401 (auth required = service alive) |
| Go | HTTP GET `<URL>/github.com/gin-gonic/gin/@v/list` | Returns version list |
| Rust | HTTP GET the sparse index URL | HTTP 200 |
| Maven | HTTP GET `<URL>/org/apache/commons/commons-lang3/maven-metadata.xml` | Returns XML content |
| HuggingFace | HTTP GET `<URL>/api/models?limit=1` | Returns JSON |

### 4.3 Acceptance Criteria

| Response Time | Rating | Action |
|---|---|---|
| < 3000ms | Excellent | Use this source |
| 3000–10000ms | Acceptable | Use if no faster alternative found |
| > 10000ms or timeout | Unusable | Try next candidate |

**Selection rule**: Test ALL available candidates (baseline + search-discovered),
then select the one with the lowest response time that passes validation.

### 4.4 Batch Validation Scripts

Pre-built scripts in `scripts/`:
- `scripts/validate.sh` — Linux / macOS (bash). Supports `--json` flag for machine-readable output.
- `scripts/validate.ps1` — Windows (PowerShell)

```bash
bash scripts/validate.sh              # test all, colored output
bash scripts/validate.sh pip           # test pip only
bash scripts/validate.sh all --json    # machine-readable JSON output
```

### 4.5 Security Notes on Validation

> **`trusted-host` warning**: Using `--trusted-host` with pip disables SSL
> certificate verification for that host. This is a security trade-off.
> Only use it when the mirror is a known institution (e.g., .edu.cn, major
> cloud vendor) and the connection is within a trusted network.
> Prefer mirrors that have valid SSL certificates and do not require `trusted-host`.

---

## 5. Configuration

### Core Principles

1. **Backup first** — Always backup the original config file before modifying
2. **Merge, don't overwrite** — For JSON configs (Docker daemon.json), read existing content and merge new fields. Never blindly overwrite the entire file
3. **Permanent config** — Write to config files, not just CLI flags
4. **Verify after write** — Run a test command to confirm the new source works

> Detailed configuration templates for each tool are in
> [`references/config-templates.md`](references/config-templates.md).
> Below is a quick reference of the key commands.

### Quick Reference

**pip**: `pip config set global.index-url <URL>`

**npm**: `npm config set registry <URL>`

**yarn v1**: `yarn config set registry <URL>`

**yarn v2+**: `yarn config set npmRegistryServer <URL>`

**pnpm**: `pnpm config set registry <URL>`

**conda**: `conda config --add channels <URL> && conda config --set show_channel_urls yes`

**Docker**: Read existing `daemon.json`, add/update `registry-mirrors` array, write back, restart Docker. See `references/config-templates.md` for merge logic.

**Go**: `go env -w GOPROXY=<URL>,direct && go env -w GOSUMDB=sum.golang.google.cn`

**Rust (cargo)**: Write `[source.crates-io]` + `[source.mirror]` to `~/.cargo/config.toml`

**Rust (rustup)**: Set `RUSTUP_DIST_SERVER` and `RUSTUP_UPDATE_ROOT` env vars

**Maven**: Add `<mirror>` block to `~/.m2/settings.xml`

**Gradle (Groovy)**: Add `maven { url '<URL>' }` to `repositories` block

**Gradle (Kotlin)**: Add `maven(url = "<URL>")` to `repositories` block

**Homebrew**: Set `HOMEBREW_BREW_GIT_REMOTE`, `HOMEBREW_CORE_GIT_REMOTE`, `HOMEBREW_BOTTLE_DOMAIN` env vars

**apt**: Replace `archive.ubuntu.com` with mirror host in `/etc/apt/sources.list`, then `sudo apt update`

**yum/dnf**: Backup `/etc/yum.repos.d/`, replace `baseurl` in repo files, then `sudo yum makecache`

**GitHub**: Prepend accelerator prefix: `git clone <PREFIX>https://github.com/<owner>/<repo>.git`

**HuggingFace**: Set `HF_ENDPOINT=<URL>` env var

---

## 6. Restore Official Sources

| Tool | Restore Command |
|---|---|
| pip | `pip config unset global.index-url` |
| npm | `npm config set registry https://registry.npmjs.org` |
| yarn v1 | `yarn config set registry https://registry.yarnpkg.com` |
| yarn v2+ | `yarn config set npmRegistryServer https://registry.yarnpkg.com` |
| pnpm | `pnpm config set registry https://registry.npmjs.org` |
| conda | `conda config --remove-key channels` |
| Go | `go env -w GOPROXY=https://proxy.golang.org,direct` |
| Docker | Remove `registry-mirrors` from daemon.json (keep other fields), restart |
| Rust (cargo) | Remove `[source.*]` sections from config.toml |
| Rust (rustup) | `unset RUSTUP_DIST_SERVER RUSTUP_UPDATE_ROOT` |
| Maven | Remove `<mirror>` block from settings.xml |
| Homebrew | `unset HOMEBREW_BREW_GIT_REMOTE HOMEBREW_CORE_GIT_REMOTE HOMEBREW_BOTTLE_DOMAIN` |
| apt | Restore `/etc/apt/sources.list` from backup, `sudo apt update` |
| yum/dnf | Restore `/etc/yum.repos.d/` from backup, `sudo yum makecache` |
| HuggingFace | `unset HF_ENDPOINT` |

---

## 7. Notes

- **Docker & GitHub accelerators** have the highest churn rate — always validate before configuring
- If the user has an enterprise Nexus/Artifactory, prefer that over public mirrors
- WSL 1 and WSL 2 have different network stacks; WSL 2 has its own IP and needs separate Docker/apt config
- If `HTTP_PROXY` / `HTTPS_PROXY` env vars are set, some tools may bypass mirrors and go through the proxy instead
- On ARM architectures (Apple Silicon, ARM Linux), verify that the mirror hosts packages for your architecture
- When multiple Python/Node versions coexist (pyenv, nvm, conda envs), config may need to target specific environments rather than global settings
- Use `scripts/validate.sh` or `scripts/validate.ps1` for periodic health checks

---

## 8. Known Unstable Sources

> This section is informational. Always validate before use rather than
> relying solely on this list, which may itself become outdated.

| Source | Status (2026-03) | Notes |
|---|---|---|
| `pypi.douban.com` (pip) | Dead | Connection reset |
| `ghproxy.cc` (GitHub) | Dead | SSL certificate untrusted |
| `mirrors.aliyun.com/goproxy/` (Go) | Unstable | Homepage 404, module downloads intermittent |

---

## 9. Cross-Agent Adaptation

### Capability Requirements

| Capability | Required? | Used in | If absent |
|---|---|---|---|
| Terminal/shell | **Required** | Steps 2, 4, 5, 6 | Cannot function |
| File read/write | **Required** | Steps 5, 6 | Cannot write config |
| Web search | Optional | Step 4 | Use baseline table only (Section 2) |
| Web fetch | Optional | Step 4 | Use `curl` / `Invoke-WebRequest` via terminal |

### Platform Adaptation

**Claude Code / StepFun**: Native support. Place folder in `~/.claude/skills/` or `~/.stepfun/skills/`.

**Cursor**: Create `.cursor/rules/china-mirror-resolver.mdc` with this content:
```
---
description: Resolve slow package downloads in China by switching to domestic mirrors. Triggers on: timeout, mirror, 换源, 镜像源, 下载慢
globs:
alwaysApply: false
---

[Paste the content of this SKILL.md here, excluding the YAML frontmatter]
```

**Windsurf**: Create `.windsurf/rules/china-mirror-resolver.md` with this content:
```
---
trigger: auto
---

[Paste the content of this SKILL.md here, excluding the YAML frontmatter]
```

**Generic LLM (no skill system)**: Include Section 2 (baseline table) and Section 5 (config quick reference) in the system prompt. Skip Section 3 (search) if the LLM has no search tool.
