# china-mirror-resolver

> **Self-healing China mirror source resolver for AI agents.**
> Automatically discovers, validates, and configures the best available mirror sources for development tools in mainland China.

[中文](#中文说明) | [English](#english)

---

## English

### What is this?

An Agent Skill that helps AI coding assistants (Claude Code, StepFun, Cursor, Windsurf, etc.) resolve slow/failed package downloads in mainland China by automatically switching to domestic mirror sources.

### Key Design

Unlike traditional mirror lists that go stale, this skill teaches the agent a **self-healing workflow**:

1. **Diagnose** — Identify the failing tool from error messages
2. **Try baseline** — Test known stable mirrors (university/cloud provider mirrors)
3. **Search if needed** — If baselines fail, search the web for current alternatives
4. **Validate** — HTTP reachability + tool-specific verification before applying
5. **Configure** — Backup → write config → verify
6. **Degrade gracefully** — Works offline with baseline table only (no search needed)

### Supported Tools

pip, npm, yarn, pnpm, conda, Docker, Go, Rust (cargo/rustup), Maven, Gradle, Homebrew, apt, yum/dnf, GitHub accelerator, Hugging Face

### Installation

**Method 1 — One-click install via URL (Recommended)**

Simply paste this repository URL into your AI agent's chat:

```
https://github.com/The-Ladder-of-Rrogress/china-mirror-resolver
```

Agents that support skill installation from URLs (e.g. Claude Code, StepFun) will automatically download and activate the skill.

**Method 2 — Manual install**

Copy the `china-mirror-resolver/` folder to your agent's skill directory:

| Agent | Skill Directory |
|---|---|
| Claude Code | `~/.claude/skills/` |
| StepFun (小跃) | `~/.stepfun/skills/` |

For Cursor/Windsurf, see [Cross-Agent Usage](#cross-agent-usage).

### Validation Scripts

```bash
# Linux / macOS — test all mirrors
bash scripts/validate.sh

# Test specific tool only
bash scripts/validate.sh pip

# Machine-readable JSON output
bash scripts/validate.sh all --json

# Windows PowerShell
powershell -ExecutionPolicy Bypass -File scripts/validate.ps1
powershell -ExecutionPolicy Bypass -File scripts/validate.ps1 -Tool docker
powershell -ExecutionPolicy Bypass -File scripts/validate.ps1 -Json
```

### Cross-Agent Usage

This skill follows the [Agent Skills open standard](https://agentskills.io/specification). To adapt for other platforms:

| Platform | How to use |
|---|---|
| **Cursor** | Copy SKILL.md content into `.cursor/rules/china-mirror-resolver.mdc`, set activation to "Agent Requested" |
| **Windsurf** | Copy SKILL.md content into `.windsurf/rules/china-mirror-resolver.md`, set activation to "Always On" or "Auto" |
| **Gemini** | Package as tar.gz and upload via API |
| **Other LLM agents** | Include SKILL.md content in system prompt or knowledge base |

### Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on reporting dead sources, adding new mirrors, and submitting PRs.

### License

MIT — see [LICENSE](LICENSE)

---

## 中文说明

### 这是什么？

一个 AI Agent 技能，帮助 AI 编程助手（Claude Code、小跃、Cursor、Windsurf 等）自动解决中国大陆环境下包管理器下载慢/超时的问题。

### 核心设计

不硬编码 URL，而是教会 Agent 一套**自愈式工作流**：诊断 → 尝试基准源 → 失效则搜索替代 → 验证 → 配置 → 无搜索能力时降级为仅用基准源表。

### 支持工具

pip、npm、yarn、pnpm、conda、Docker、Go、Rust、Maven、Gradle、Homebrew、apt、yum/dnf、GitHub 加速、Hugging Face

### 安装

**方式一 — 一键安装（推荐）**

将本仓库 URL 直接发送给你的 AI Agent 即可自动安装：

```
https://github.com/The-Ladder-of-Rrogress/china-mirror-resolver
```

支持 URL 安装技能的 Agent（如 Claude Code、小跃）会自动下载并激活。

**方式二 — 手动安装**

将 `china-mirror-resolver/` 文件夹复制到 Agent 的技能目录即可。

### 验证

```bash
bash scripts/validate.sh          # Linux/macOS 全量测试
bash scripts/validate.sh docker   # 仅测试 Docker
```

```powershell
powershell -File scripts/validate.ps1            # Windows 全量测试
powershell -File scripts/validate.ps1 -Tool pip  # 仅测试 pip
```

### 许可证

MIT
