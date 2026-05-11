# Domain: Hardware Resources

> Deep reference for Domain 1 in SKILL.md.
> Load this file when running L3 analysis or when SKILL.md thresholds need clarification.
>
> **Input:** `DATA.env`
> **Output:** status (✅/⚠️/❌) + score (0–100) + findings + fix hints
> If `DATA.env = null`: status = ⚠️, score = 50, finding = "Could not collect environment data."

---

## Analysis Checklist

### 1. Memory Usage

Extract: `DATA.env.memory.total_mb`, `DATA.env.memory.available_mb`
Calculate: `used_pct = (total_mb - available_mb) / total_mb * 100`

| used_pct | Status | Score Impact | Qualitative |
|----------|--------|-------------|-------------|
| < 70% | ✅ | 0 | Healthy headroom |
| 70–85% | ⚠️ | -15 | Moderate pressure |
| > 85% | ❌ | -35 | Critical — risk of OOM kills |

**Risk:** High memory pressure causes agent task failures, OOM kills, and log file corruption.
**Fix:** Identify heavy processes: `top -o MEM` / `ps aux --sort=-%mem | head -10`

---

### 2. Disk Usage

Extract: `DATA.env.disk.total_gb`, `DATA.env.disk.available_gb`
Calculate: `used_pct = (total_gb - available_gb) / total_gb * 100`

| used_pct | Status | Score Impact | Qualitative |
|----------|--------|-------------|-------------|
| < 80% | ✅ | 0 | Adequate space |
| 80–90% | ⚠️ | -15 | Space running low |
| > 90% | ❌ | -30 | Critical — log rotation and skill installs will fail |

**Risk:** Full disk prevents log rotation, snapshot saves, skill installation, memory writes.
**Fix:** `du -sh $OPENCLAW_HOME/*` to identify large directories; prune old snapshots.

---

### 3. CPU Load

Extract: `DATA.env.cpu.load_avg_1m`, `DATA.env.cpu.cores`
Calculate: `load_per_core = load_avg_1m / cores`

| load_per_core | Status | Score Impact | Qualitative |
|---------------|--------|-------------|-------------|
| < 0.7 | ✅ | 0 | Normal operation |
| 0.7–1.0 | ⚠️ | -10 | Elevated — agent responses may slow |
| > 1.0 | ❌ | -25 | Overloaded — tasks will queue and timeout |

**Risk:** Sustained high CPU causes agent timeout failures and degraded response quality.
**Fix:** `top` or `htop` to identify runaway processes.

---

### 4. Node.js Version

Extract: `DATA.env.versions.node` (format: `vXX.XX.XX`)

| Version | Status | Score Impact | Note |
|---------|--------|-------------|------|
| ≥ 18.0.0 | ✅ | 0 | LTS supported |
| 16.x | ⚠️ | -20 | EOL since Sep 2023 |
| < 16 | ❌ | -40 | Unsupported — OpenClaw will not run |

**Fix (darwin):** `brew install node` or `nvm install --lts`
**Fix (linux):** `curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo bash -`

---

### 5. OS Compatibility

Extract: `DATA.env.system.platform`

| Platform | Status | Score Impact |
|----------|--------|-------------|
| `darwin` | ✅ | 0 |
| `linux` | ✅ | 0 |
| `win32` | ⚠️ | -10 |
| other | ❌ | -30 |

---

## Scoring

```
Base score: 100
Apply all score impacts (cumulative).
Floor: 0. Ceiling: 100.
```

| Score Range | Status |
|-------------|--------|
| ≥ 80 | ✅ |
| 60–79 | ⚠️ |
| < 60 | ❌ |

---

## Output Format

Produce in REPORT_LANG (domain label and summary translated; metrics and commands in English):

```
[Hardware Resources — translated domain label] [STATUS] — Score: XX/100
[One-sentence summary in REPORT_LANG]

Memory:  XX.X GB used / XX.X GB total (XX%)   [STATUS]
Disk:    XX.X GB used / XX.X GB total (XX%)   [STATUS]
CPU:     load XX.XX / X cores = XX.X per core [STATUS]
Node.js: vXX.XX.XX                            [STATUS]
OS:      [platform] [arch]                    [STATUS]

[If any ⚠️/❌ — Findings label in REPORT_LANG:]
- [Evidence citing DATA.env field and actual value]

[Fix Hints label in REPORT_LANG:]
- [Specific command, with rollback where applicable]
```
