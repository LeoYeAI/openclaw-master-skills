# add-newcli-provider

[中文](#中文) | [English](#english)

---

## 中文

### 用最低的成本在 OpenClaw 中使用 Claude、GPT 和 Gemini

[NewCLI (FoxCode)](https://code.newcli.com) 是一个多模型代理服务，通过统一账户同时提供 Anthropic Claude、OpenAI GPT、Google Gemini 三大模型家族的访问能力。本 Skill 让你一键将 NewCLI 接入 OpenClaw，立刻获得 30+ 个模型的访问。

### 为什么选 NewCLI？

- **全家桶** — 一个 API Key 同时用 Claude、GPT、Gemini，不用分别注册
- **便宜** — 包月制/低价代理，不按 token 计费，适合高频使用场景
- **兼容** — 完全兼容 Anthropic / OpenAI / Google 原生 API 格式
- **丰富** — Claude Opus、GPT-5.3、Gemini 3 Pro，旗舰模型全覆盖

### 这个 Skill 做了什么？

一个完整的 OpenClaw 多 provider 配置指南，包含：

- 三个 Provider 的注册与模型定义（Claude / GPT / Gemini）
- 别名配置（聊天中用 `/model claude-opus`、`/model gpt53`、`/model gemini3pro` 快速切换）
- Fallback 链优化（每个 provider 一个最轻量模型，精简高效）
- API 可用性测试方法（三种不同的测试命令）
- 验证与排障流程（踩过的坑都写进去了）

### 支持的模型

#### Claude 系列（`newcli` provider）
| 别名 | 模型 | 适用场景 |
|------|------|----------|
| `claude-opus` | Claude Opus 4.6 | 复杂推理、长文写作、代码生成 |
| `claude-haiku` | Claude Haiku 4.5 | 轻量对话、快速响应 |

#### GPT 系列（`newcli-codex` provider）
| 别名 | 模型 | 适用场景 |
|------|------|----------|
| `gpt53` | GPT-5.3 Codex | 最新旗舰、代码生成 |
| `gpt52` | GPT-5.2 | 通用对话 |
| `gpt51mini` | GPT-5.1 Codex Mini | 轻量快速 |
| `gpt51max` | GPT-5.1 Codex Max | 增强推理 |
| ...  | 共 9 个模型 | 详见 SKILL.md |

#### Gemini 系列（`newcli-gemini` provider）
| 别名 | 模型 | 适用场景 |
|------|------|----------|
| `gemini3pro` | Gemini 3 Pro | 最新旗舰、深度推理（1M context） |
| `gemini3flash` | Gemini 3 Flash | 快速响应 |
| `gemini25pro` | Gemini 2.5 Pro | 上代旗舰 |
| `gemini25lite` | Gemini 2.5 Flash Lite | 最轻量 |
| ... | 共 8 个文本 + 30 个生图模型 | 详见 SKILL.md |

> 实际可用模型以你的 NewCLI 账户为准。

### 三个 Provider 的技术差异

| Provider | API 协议 | Base URL | 认证方式 |
|----------|----------|----------|----------|
| `newcli` | `anthropic-messages` | `/claude` | `x-api-key` |
| `newcli-codex` | `openai-completions` | `/codex/v1` | Bearer token |
| `newcli-gemini` | `google-generative-ai` | `/gemini/v1beta` | `x-goog-api-key` |

同一个 API Key，三种不同的协议和端点——这就是为什么需要配置三个 provider。

### 使用方法

将此 skill 目录放入 OpenClaw 的 skills 目录，对你的 agent 说「配 newcli」、「加 Claude」、「加 GPT」、「加 Gemini」或「接入 fox 源」即可。

### 注册 NewCLI

**使用我的邀请链接注册：**
https://foxcode.rjj.cc/auth/register?aff=7WTAV8R

---

## English

### Use Claude, GPT, and Gemini on OpenClaw at a Fraction of the Cost

[NewCLI (FoxCode)](https://code.newcli.com) is a multi-model proxy service that provides unified access to Anthropic Claude, OpenAI GPT, and Google Gemini through a single account and API key. This Skill lets you integrate all three model families into OpenClaw with minimal effort.

### Why NewCLI?

- **All-in-one** — One API key for Claude, GPT, and Gemini, no separate signups needed
- **Affordable** — Flat-rate / low-cost proxy pricing instead of per-token billing
- **Compatible** — Fully compatible with Anthropic / OpenAI / Google native API formats
- **Comprehensive** — Claude Opus, GPT-5.3, Gemini 3 Pro — all flagship models included

### What Does This Skill Do?

A complete OpenClaw multi-provider configuration guide, covering:

- Three Provider setups (Claude / GPT / Gemini) with model definitions
- Alias configuration (`/model claude-opus`, `/model gpt53`, `/model gemini3pro`)
- Optimized fallback chain (one lightweight model per provider)
- API availability testing (three different test commands for three protocols)
- Validation and troubleshooting (battle-tested in production)

### Supported Models

#### Claude (`newcli` provider)
| Alias | Model | Best For |
|-------|-------|----------|
| `claude-opus` | Claude Opus 4.6 | Complex reasoning, writing, coding |
| `claude-haiku` | Claude Haiku 4.5 | Lightweight, fast responses |

#### GPT (`newcli-codex` provider)
| Alias | Model | Best For |
|-------|-------|----------|
| `gpt53` | GPT-5.3 Codex | Latest flagship, code generation |
| `gpt51mini` | GPT-5.1 Codex Mini | Lightweight, fast |
| ... | 9 models total | See SKILL.md for full list |

#### Gemini (`newcli-gemini` provider)
| Alias | Model | Best For |
|-------|-------|----------|
| `gemini3pro` | Gemini 3 Pro | Latest flagship, reasoning (1M context) |
| `gemini3flash` | Gemini 3 Flash | Fast responses |
| `gemini25lite` | Gemini 2.5 Flash Lite | Lightest weight |
| ... | 8 text + 30 image models | See SKILL.md for full list |

> Actual availability depends on your NewCLI account.

### Quick Start

Place this skill directory in your OpenClaw skills folder and tell your agent to "configure newcli", "add Claude", "add GPT", or "add Gemini".

### Sign Up for NewCLI

**Register with my referral link:**
https://foxcode.rjj.cc/auth/register?aff=7WTAV8R

---

## 变更记录

| 日期 | 版本 | 变更内容 | 变更人 |
|------|------|----------|--------|
| 2026-02-08 | v1.0 | 创建 README（仅 Claude） | jooey (via Claude Code) |
| 2026-02-08 | v2.0 | 重写为三模型家族完整指南 | ConfigBot (via OpenClaw with Opus 4.6) |

## License

MIT
