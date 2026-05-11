<div align="center">

# 🔨 AutoForge

### *Stop vibing. Start converging.*

**Iterative optimization loops for AI agent skills, code, docs & entire repos.**

Mathematical convergence · Multi-model cross-validation · Live Unicode reporting

[![MIT License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-skill-brightgreen.svg)](https://openclaw.ai)
[![ClawHub](https://img.shields.io/badge/ClawHub-autoforge-8B5CF6.svg)](https://clawhub.com/skills/autoforge)

</div>

---

Most "self-improving agent" approaches boil down to *"reflect on your output."*
That's a vibe check, not optimization. AutoForge is different.

|  | Typical "Reflect" | AutoForge |
|---|---|---|
| **When to stop** | "Looks good to me" | 3× 100% pass, 5× retained, or 3× discard |
| **Progress** | Chat history | TSV with pass rates & diffs per iteration |
| **Validation** | Same model checks itself | Multi-model cross-validation |
| **Reporting** | Final summary | Live Unicode bars after every iteration |
| **Modes** | One generic loop | 4 specialized modes |
| **Track record** | Demo | 50+ iterations across 6 production skills |

---

## 🏗️ Architecture

### Core Loop

```
                         ┌─────────────────────┐
                         │  Define target +     │
                         │  evals               │
                         └─────────┬───────────┘
                                   │
                                   ▼
                         ┌─────────────────────┐
                         │  Baseline scan       │
                         └─────────┬───────────┘
                                   │
                    ┌──────────────┘
                    │
                    ▼
           ┌───────────────┐     proposed     ┌───────────────┐
       ┌──▶│   Optimizer   │────────────────▶│   Validator   │
       │   │  (Claude Opus)│                  │    (GPT-5)    │
       │   └───────────────┘                  └───────┬───────┘
       │                                              │
       │                              ┌───────────────┴───────────────┐
       │                              │                               │
       │                              ▼                               ▼
       │                     ┌─────────────┐                 ┌─────────────┐
       │                     │ ✅ improved  │                 │ ❌ discarded │
       │                     └──────┬──────┘                 └──────┬──────┘
       │                            │                               │
       │                            └───────────┬─────────────┬─────┘
       │                                        ▼             │
       │                               ┌─────────────┐       │
       │                               │  Log to TSV  │       │
       │                               │  + report.sh │       │
       │                               └──────┬──────┘       │
       │                                      │              │
       │                                      ▼              │
       │                              ┌──────────────┐       │
       │          No                  │  Converged?  │       │
       └──────────────────────────────┤              │       │
                                      └──────┬───────┘       │
                                             │               │
                         ┌───────────────────┼───────────────┐
                         │                   │               │
                         ▼                   ▼               ▼
                  ┌─────────────┐   ┌──────────────┐  ┌───────────┐
                  │ 3× 100% ✅  │   │ 5× retained  │  │ 3× discard│
                  │   Deploy!   │   │  Converged   │  │   Stop ⚠️  │
                  └─────────────┘   └──────────────┘  └───────────┘
```

### Multi-Model Validation

```
  Iter 1 (Optimizer)          Iter 2 (Validator)         Iter 3 (Optimizer)
  ─────────────────           ──────────────────         ─────────────────

  ┌──────────────┐            ┌──────────────┐           ┌──────────────┐
  │ Claude Opus  │            │    GPT-5     │           │ Claude Opus  │
  │              │            │              │           │              │
  │ Analyze      │            │ Blind review │           │ Fix findings │
  │ Find issues  │            │ of output    │           │ from GPT-5   │
  │ Write fixes  │            │ (no context) │           │              │
  └──────┬───────┘            └──────┬───────┘           └──────┬───────┘
         │                           │                          │
         ▼                           ▼                          ▼
  pass_rate: 62%              pass_rate: 78%              pass_rate: 95%
  status: improved            status: improved            status: improved

         └────── TSV ──────────────── TSV ──────────────── TSV ──────┘

  Different model validates → no "grading your own homework" blind spot
```

### Project Mode — Three Phases

```
  Phase 1                    Phase 2                      Phase 3
  SCAN & PLAN                CROSS-FILE ANALYSIS          ITERATIVE FIX LOOP
  ─────────────              ───────────────────          ──────────────────

  ┌──────────────┐           ┌──────────────────┐         ┌──────────────┐
  │ Walk repo    │           │ README ↔ CLI     │    ┌───▶│ Surgical fix │
  │ tree         │           │ Dockerfile ↔ deps│    │    │ across files │
  │              │──────────▶│ CI ↔ scripts     │───▶│    └──────┬───────┘
  │ Build file   │           │ .env ↔ code refs │    │           │
  │ priority map │           │ imports ↔ reqs   │    │           ▼
  └──────────────┘           │ .gitignore ↔ out │    │    ┌──────────────┐
                             └──────────────────┘    │    │ Validate     │
                                                     │    │ consistency  │
                                                     │    └──────┬───────┘
                                                     │           │
                                                     │     Not   │  Done?
                                                     └─── yet ◀──┘
```

---

## 🚀 Quick Start

**Install**

```bash
# Via ClawHub
clawhub install autoforge

# Or clone
git clone https://github.com/akrimm702/autoforge.git
cp -r autoforge ~/.openclaw/workspace/skills/autoforge
```

**Configure reporting** *(optional)*

```bash
export AF_CHANNEL="telegram"        # telegram | discord | slack
export AF_CHAT_ID="-100XXXXXXXXXX"  # chat/group ID
export AF_TOPIC_ID="1234"           # thread ID (optional)
```

No env vars? Reports print to stdout with ANSI colors.

**Tell your agent**

```
Start autoforge mode: prompt for the coding-agent skill.
Evals: PTY handling correct? Workspace protection enforced? Clear structure?
```

The agent reads the skill, runs the loop, tracks everything in TSV, reports live, and stops when convergence math says it's done.

---

## 🔧 Four Modes

### `prompt` — Mental Simulation

Simulates 5 realistic scenarios per iteration, evaluates Yes/No against defined evals, calculates pass rate mathematically. No code execution.

**Best for:** SKILL.md files, prompt engineering, documentation, briefing templates.

### `code` — Real Execution

Runs code in a sandbox, measures exit codes, stdout, stderr, runtime. Evaluates against concrete test criteria.

**Best for:** Shell scripts, Python tools, data pipelines, build systems.

### `audit` — CLI Testing

Tests documented commands against actual CLI behavior (`--help`, read-only). Catches docs-vs-reality drift. Two variants: Simple (2 iterations) or Deep (iterative with multi-model).

**Best for:** Verifying skill documentation matches real CLI behavior.

### `project` — Whole Repository ⭐

Scans an entire repo, builds a file-map with priorities, runs **cross-file consistency checks**, and iteratively fixes issues across multiple files.

**Best for:** README ↔ CLI drift, Dockerfile ↔ dependency mismatches, CI ↔ project structure gaps.

Cross-file checks include:

- README documents what the CLI actually does
- Dockerfile installs the right dependency versions
- CI workflows reference correct paths and scripts
- `.env.example` covers all env vars used in code
- Every import has a matching dependency declaration
- `.gitignore` excludes build artifacts and secrets

---

## 📊 Live Reporting

After each iteration, `report.sh` sends live updates:

```
📊 AutoForge: coding-agent

📍 Iter 1   █████████░░░░░░░░░░░  45%
✅ Iter 2   ████████████░░░░░░░░  62%
✅ Iter 3   ███████████████░░░░░  78%
✅ Iter 4   █████████████████░░░  85%
✅ Iter 5   ██████████████████░░  90%
✅ Iter 6   ██████████████████░░  92%
✅ Iter 7   ██████████████████░░  92%
✅ Iter 8   ███████████████████░  95%
✅ Iter 9   ███████████████████░  95%
✅ Iter 10  ████████████████████  100%

──────────────────────
Iterations: 10  ✅ Keep: 10  ❌ Discard: 0
🏆 Best pass rate: 100% (Iter 10)

✅ Loop converged — improvement found
```

Every iteration is tracked in TSV:

```
iteration  prompt_version_summary       pass_rate  change_description              status
1          Baseline                     45%        Original SKILL.md baseline      baseline
2          Add missing subcommands      62%        16 Codex subcommands added      improved
3          Fix approval flags           78%        Scoped flags by context         improved
...
10         Validation pass              100%       All checks green                improved
```

---

## 📐 Convergence Rules

No vibes. No "looks good." Mathematical stop conditions:

| Condition | Rule | Purpose |
|-----------|------|---------|
| ⬇️ Minimum iters | Must reach N before any stop | Prevents premature convergence |
| 🛑 Max 30 iters | Hard safety cap | Cost protection |
| ❌ 3× discard streak | Stop + analyze | Detects structural problems |
| ✅ 3× 100% pass | Confirmed perfect | After minimum reached |
| ➡️ 5× retained streak | Fully converged | No further improvement possible |

**Validator noise detection:** In multi-model setups, validators can produce false positives. AutoForge recognizes config/path confusion, inverted checks, normal English flagged as forbidden references, and over-counting. After all real fixes, if >3 discards stem from non-reproducible complaints → declare convergence.

---

## 🔀 Multi-Model Cross-Validation

For complex audits, split optimizer and validator across different models:

| Role | Example Models | Task |
|------|---------------|------|
| **Optimizer** | Claude Opus, GPT-4.1 | Finds issues, writes fixes |
| **Validator** | GPT-5, Gemini | Checks against ground truth independently |

The validator doesn't see the optimizer's reasoning — just the output. This prevents the "same model validates its own work" blind spot.

---

## 🏆 Real-World Results

*Production runs, not demos.*

**coding-agent SKILL.md** — 553 lines rewritten across 10 iterations. 16 Codex subcommands + 40 Claude CLI flags documented. 45% → 100%. Discovered `--yolo` was never a real flag.

**ACP Router** — 90% → 100% in 9 iterations. Agent coverage doubled from 6 to 12 harnesses. Thread spawn recovery policy written from scratch.

**Sub-Agents Documentation** — 70% → 100% in 14 iterations with multi-model validation. 6 real bugs found in upstream docs. Identified 4 categories of validator false positives.

**backup.sh** — Added rsync support, validation checks, restore-test. Code mode with sandboxed test runs. 3 iterations to stable, 2 more to polish.

**AutoForge on itself 🤯** — Self-forged in project mode: 67% → 100% in 8 iterations. Fixed 2 script bugs, cleaned config/doc inconsistencies across 7 files.

---

## 🗂️ Directory Structure

```
autoforge/
├── SKILL.md                ← OpenClaw skill definition
├── README.md               ← You are here
├── LICENSE                 ← MIT
├── .gitignore
├── scripts/
│   ├── report.sh           ← Live reporting (channel or stdout)
│   └── visualize.py        ← PNG progress chart generator
├── references/
│   ├── eval-examples.md    ← 200+ pre-built evals by category
│   └── ml-mode.md          ← ML training integration guide
├── examples/
│   ├── demo-results.tsv    ← Sample iteration data
│   └── example-config.json ← Reference template
└── results/                ← Your run data (gitignored)
    └── .gitkeep
```

---

## ⚙️ Configuration

AutoForge is configured entirely via environment variables. No config file needed.

| Variable | Default | Description |
|----------|---------|-------------|
| `AF_CHANNEL` | `telegram` | Report delivery channel |
| `AF_CHAT_ID` | *(none)* | Chat/group ID. Unset = stdout |
| `AF_TOPIC_ID` | *(none)* | Thread/topic ID |

| Flag | Behavior |
|------|----------|
| `--dry-run` *(default)* | Only TSV + proposed files. Target unchanged. |
| `--live` | Overwrites target. Auto-backup to `results/backups/`. |
| `--resume` | Continue from existing TSV. |

---

## 🤝 Contributing

1. Fork → feature branch → PR
2. Run `shellcheck scripts/report.sh` and `python3 -m py_compile scripts/visualize.py`
3. Include real-world results from your own runs if possible

**Good contributions:** new eval templates, additional channel support, bug fixes with repro steps, production run case studies.

---

## License

MIT — see [LICENSE](LICENSE).

---

<div align="center">

Built by [Alexander Krimm](https://github.com/akrimm702).

Battle-tested across **50+ iterations** on **6 production skills**.

*Stop reflecting. Start forging.* 🔨

</div>
