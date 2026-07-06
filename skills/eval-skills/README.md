<div align="center">

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://capsule-render.vercel.app/api?type=waving&color=0:6366f1,100:06b6d4&height=200&section=header&text=eval-skills&fontSize=72&fontColor=ffffff&fontAlignY=38&desc=L1%20Evaluation%20Framework%20for%20AI%20Agent%20Skills&descAlignY=60&descSize=18&animation=fadeIn"/>
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:6366f1,100:06b6d4&height=200&section=header&text=eval-skills&fontSize=72&fontColor=ffffff&fontAlignY=38&desc=L1%20Evaluation%20Framework%20for%20AI%20Agent%20Skills&descAlignY=60&descSize=18&animation=fadeIn" alt="eval-skills banner" width="100%"/>
</picture>

<br/>

[![License: MIT](https://img.shields.io/badge/License-MIT-6366f1?style=for-the-badge&logo=opensourceinitiative&logoColor=white)](LICENSE)&nbsp;
[![Version](https://img.shields.io/badge/version-0.1.0-06b6d4?style=for-the-badge&logo=semver&logoColor=white)](CHANGELOG.md)&nbsp;
[![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178c6?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)&nbsp;
[![Node.js >= 18](https://img.shields.io/badge/Node.js-%E2%89%A518-339933?style=for-the-badge&logo=nodedotjs&logoColor=white)](https://nodejs.org/)&nbsp;
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-ff6b6b?style=for-the-badge&logo=git&logoColor=white)](#-contributing)

<br/>

[![GitHub stars](https://img.shields.io/github/stars/isLinXu/eval-skills?style=social)](https://github.com/isLinXu/eval-skills/stargazers)&nbsp;
[![GitHub forks](https://img.shields.io/github/forks/isLinXu/eval-skills?style=social)](https://github.com/isLinXu/eval-skills/network/members)&nbsp;
[![GitHub issues](https://img.shields.io/github/issues/isLinXu/eval-skills?style=social)](https://github.com/isLinXu/eval-skills/issues)

<br/>

> **The Missing Quality Gate for AI Agent Skills.**
>
> Framework-agnostic **L1 (atomic skill-unit) evaluation** for MCP, OpenClaw, Claude Code, and any JSON-RPC-compatible AI skill — featuring sandboxed execution, multi-dimensional scoring, regression diffing, and CI/CD integration.

<br/>

[**🚀 Quick Start**](#-quick-start) · [**📦 Installation**](#-installation) · [**✨ Features**](#-key-features) · [**🏗️ Architecture**](#%EF%B8%8F-system-architecture) · [**📚 References**](#-references)

</div>

---

## 🔥 Why eval-skills?

The AI skill ecosystem has exploded with **11,000+ registered tools**, yet the average quality score remains alarmingly low at **44.7 / 100** *(SkillsIndex, Feb 2026)*.

Low-quality skills lead to:
*   **3–5× LLM token overconsumption** due to retry loops.
*   **Degraded agent reliability** and user trust.
*   **Supply-chain security risks** from unverified code execution.

**No existing tool evaluates skills at the atomic unit level (L1).** `eval-skills` fills this critical gap.

<table>
<tr>
<td width="50%">

### ❌ Without eval-skills
```diff
- No unit tests for individual skills
- Unclear quality before deployment
- No regression detection on updates
- Unsafe execution of 3rd-party code
```

</td>
<td width="50%">

### ✅ With eval-skills
```diff
+ Automated L1 skill unit evaluation
+ CompositeScore across 4 dimensions
+ DiffReport to catch regressions
+ 3-layer sandboxed execution
```

</td>
</tr>
</table>

### Evaluation Scope

| Level | Scope | Tools |
|:-----:|-------|-------|
| **L3** System | End-to-end agent tasks | WebArena · SWE-bench · OSWorld |
| **L2** Trajectory | Multi-turn tool-use | ToolSandbox · ToolGym · AgentBench |
| **L1** Skill Unit | **Single-skill correctness, latency, security** | **eval-skills** ⭐ |

> 📖 *A survey of 120 LLM-agent evaluation frameworks identifies L1 granularity as a primary open problem — Yehudai et al., arXiv:2503.16416*

---

## ✨ Key Features

- **🛡️ Multi-Layer Sandbox**: Securely execute untrusted skills using Process or Docker isolation.
- **📊 Comprehensive Metrics**: Evaluate Correctness, Latency, Error Rate, and Consistency.
- **🔌 Universal Adapters**: Support for HTTP, Subprocess (JSON-RPC), and MCP protocols.
- **📉 Regression Detection**: Compare evaluation snapshots to prevent quality drift.
- **🤖 CI/CD Ready**: Machine-readable reports (JSON, CSV) and exit codes for automated pipelines.

---

## 📦 Installation

### 1. Install as a Claude Code Skill
Ideal for conversational evaluation within your agent workflow.

```bash
# Global (all projects)
git clone https://github.com/isLinXu/eval-skills.git ~/.claude/skills/eval-skills

# Project-level (current repo only)
git clone https://github.com/isLinXu/eval-skills.git .claude/skills/eval-skills
```

### 2. Install as an OpenClaw Skill
For integration with the OpenClaw ecosystem.

```bash
# From ClawHub registry
clawhub install eval-skills

# Manual install
git clone https://github.com/isLinXu/eval-skills.git ~/.openclaw/skills/eval-skills
```

### 3. Install from Source (Standalone CLI)
Best for CI/CD pipelines, local development, and advanced usage.

```bash
git clone https://github.com/isLinXu/eval-skills.git
cd eval-skills
pnpm install && pnpm build

# Link globally (optional)
pnpm link --global
```

> **Prerequisites:** Node.js >= 18, pnpm >= 8. Optional: Python >= 3.8, Docker >= 24.

---

## 🚀 Quick Start

### 1. Evaluate a Single Skill
Run a specific benchmark against a skill.

```bash
eval-skills eval --skill calculator --benchmark coding-easy
```

### 2. Evaluate All Skills (Quality Gate)
Run a comprehensive check on all discovered skills, enforcing a quality threshold.

```bash
eval-skills eval --all \
  --benchmark skill-quality \
  --min-completion 0.8 \
  --exit-on-fail \
  --format json markdown
```

### 3. Detect Regressions
Compare two evaluation reports to identify performance drops.

```bash
eval-skills report diff ./reports/baseline.json ./reports/current.json
```

### 4. Programmatic API
Integrate evaluation logic directly into your TypeScript/Node.js applications.

```typescript
import { EvaluationEngine, SandboxFactory, SubprocessAdapter } from "@eval-skills/core";

const sandbox = SandboxFactory.create({ runtime: "auto" });
const adapter = new SubprocessAdapter({ sandbox, skillDirectory: "./skills/calculator" });
const engine  = new EvaluationEngine({ adapter });

const result = await engine.evaluate({
  skillId: "calculator",
  benchmarkId: "coding-easy",
  concurrency: 4,
});

console.log(`CompositeScore: ${result.compositeScore.toFixed(3)}`);
```

---

## 📖 Documentation

Dive deeper into our guides to master skill evaluation:

- [**⚡️ Quick Start Guide**](docs/guides/quickstart.md): Get up and running in minutes.
- [**🛠️ Create Your First Skill**](docs/guides/create-skill.md): Learn how to scaffold, build, and evaluate a new skill.
- [**🎯 Custom Benchmarks**](docs/guides/custom-benchmark.md): Define your own evaluation scenarios and metrics.
- [**🔄 CI/CD Integration**](docs/guides/ci-cd-integration.md): Automate skill quality gates in your pipeline.

---

## 🏗️ System Architecture

![Architecture Diagram](https://github.com/user-attachments/assets/4764919f-91ef-4b3a-9c6d-09e3af064e8a)

### Core Components

- **Adapters**: Unified interface (`BaseAdapter.invoke()`) for different skill protocols.
- **Sandbox**: 3-layer defense (Executor, Process, Docker) against malicious code.
- **Scorers**: Pluggable evaluation logic (`exact_match`, `contains`, `json_schema`, `llm_judge`).
- **Reporters**: Output generators for various formats (JSON, Markdown, HTML).

---

## 📂 Project Structure

This project is organized as a monorepo:

```
eval-skills/
├── packages/
│   ├── cli/          # Command-line interface
│   ├── core/         # Core evaluation engine, adapters, and logic
│   └── web/          # Web dashboard (Work in Progress)
├── benchmarks/       # Standard benchmark definitions
├── examples/         # Example skills and configurations
├── scripts/          # Maintenance and utility scripts
└── skills/           # Internal skills for testing
```

---

## 📊 Benchmarks & Scoring

### Built-in Benchmarks

| ID | Domain | Tasks | Scoring Method |
|:---|:-------|------:|:---------------|
| `coding-easy` | Coding | 20 | `exact_match` |
| `skill-quality` | Tool Use | 5 | `contains` + `json_schema` |
| `web-search-basic` | Web | 8 | `contains` + `json_schema` |

### Composite Score Formula

The **CompositeScore** aggregates multiple dimensions to provide a holistic view of skill quality:

$$ \text{CompositeScore} = w_1 \cdot \text{CR} + w_2 \cdot (1 - \text{LN}) + w_3 \cdot (1 - \text{ER}) + w_4 \cdot \text{CS} $$

| Dimension | Metric | Default Weight |
|-----------|--------|:--------------:|
| **Completion Rate (CR)** | `passed / total` | **0.50** |
| **Latency Norm (LN)** | `min(p95ms / targetMs, 1.0)` | **0.20** |
| **Error Rate (ER)** | `errors / total` | **0.30** |
| **Consistency (CS)** | `1 − CV(scores)` | 0.00 |

---

## �️ Security Sandbox

We implement a **Defense-in-Depth** strategy to safely execute untrusted skills:

| Layer | Runtime | Key Protections |
|:-----:|---------|-----------------|
| **0** | **SandboxExecutor** | Executable allow-list, injection detection, output capping (10MB). |
| **1** | **ProcessSandbox** | Hard timeouts, SIGKILL, memory ulimits, path validation. (Default) |
| **2** | **DockerSandbox** | Full isolation: cgroup limits, network restrictions, seccomp profiles. (Production) |

---

## 🗺️ Roadmap

| Phase | Status | Highlights |
|-------|:------:|------------|
| **Phase 1 — Core** | ✅ | CLI, HTTP/Subprocess adapters, Process/Docker sandboxes, basic benchmarks. |
| **Phase 2 — Ecosystem** | 🚧 | MCPAdapter, LangChain adapter, Web Dashboard, `llm_judge` calibration. |
| **Phase 3 — Research** | 🔭 | Auto-benchmark synthesis, adversarial generation, async eval, 1k+ skill dataset. |

---

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

1.  Clone the repository:
    ```bash
    git clone https://github.com/isLinXu/eval-skills.git
    cd eval-skills
    ```
2.  Install dependencies:
    ```bash
    pnpm install
    ```
3.  Run tests:
    ```bash
    pnpm test
    ```

We follow [Conventional Commits](https://www.conventionalcommits.org/).

---

## 📚 References

<details>
<summary><b>Expand to see all 21 references</b></summary>

| # | Citation |
|:-:|---------|
| 1 | Liu et al. (2024). **ToolACE**: *Winning the Points of LLM Function Calling*. arXiv:2409.00920 |
| 2 | Lu et al. (2025). **ToolSandbox**: *A Stateful, Conversational, Interactive Evaluation Benchmark for LLM Tool-Use*. NAACL 2025 |
| 3 | Yehudai et al. (2025). **Survey on Evaluation of LLM-Based Agents**. arXiv:2503.16416 |
| 4 | Patil et al. (2026). **SoK: Agentic Skills — Beyond Tool Use in LLM Agents**. arXiv:2602.20867 |
| 5 | (2026). **SkillsBench**: *Benchmarking How Well Agent Skills Work Across Diverse Tasks*. arXiv:2602.12670 |
| 6 | (2026). **MCP-Atlas**: *A Large-Scale Benchmark for Tool-Use Competency with Real MCP Servers*. arXiv:2602.00933 |
| 7 | (2025). **HammerBench**: *Fine-Grained Function-Calling Evaluation*. ACL 2025 |
| 8 | Bangalore et al. (2025). **NESTFUL**: *Evaluating LLMs on Nested Sequences of API Calls*. EMNLP 2025 |
| 9 | (2025). **AsyncTool**: *Evaluating Asynchronous Function Calling under Multi-Task Scenarios* |
| 10 | (2026). **ReliabilityBench**: *Evaluating LLM Agent Reliability Under Production Stress*. arXiv:2601.06112 |
| 11 | (2026). **ToolGym**: *An Open-World Tool-Using Environment for Scalable Agent Testing*. arXiv:2601.06328 |
| 12 | Bhatia et al. (2025). *Testing Practices in Open-Source AI Agent Frameworks*. arXiv:2509.19185 |
| 13 | (2025). *Function Calling in LLMs: Industrial Practices and Future Directions*. ACM 2025 |
| 14 | (2024). *Benchmarks and Metrics for Code Generation: A Critical Review*. arXiv:2406.12655 |
| 15 | (2025). *Benchmarking AI Models in Software Engineering*. arXiv:2503.05860 |
| 16 | (2024). **ToolNet**: *Connecting LLMs with Massive Tools via Tool Graph*. arXiv:2403.00839 |
| 17 | Wu et al. (2024). **ToolPlanner**. EMNLP 2024 |
| 18 | (2026). *Learning to Rewrite Tool Descriptions for Reliable LLM-Agent Tool Use*. arXiv:2602.20426 |
| 19 | SkillsIndex (2026). *State of AI Agent Tools — February 2026* |
| 20 | IBM Research (2024). *EvalAssist: Using LLMs as Judges for AI Evaluation*. arXiv:2410.10934 |
| 21 | (2025). *LLM Evaluation in 2025: Smarter Metrics That Separate Hype from Trust*. TechRxiv |

</details>

---

<div align="center">

<picture>
  <img src="https://capsule-render.vercel.app/api?type=waving&color=0:06b6d4,100:6366f1&height=100&section=footer" alt="footer" width="100%"/>
</picture>

**eval-skills** is MIT-licensed open-source software.

[⬆ Back to top](#)

</div>
