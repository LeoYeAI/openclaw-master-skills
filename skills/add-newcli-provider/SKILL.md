---
name: add-newcli-provider
description: 为 OpenClaw 配置 code.newcli.com 作为模型源，包含四个 provider：newcli（Claude 主线路）、newcli-aws（Claude AWS 特价线路，消耗 1/24）、newcli-codex（GPT 系列）、newcli-gemini（Gemini 系列）。适用于需要接入 Claude 或 GPT 模型的场景。包含 provider 注册、模型定义、别名配置、fallback 链接入和验证的完整流程。当管理员说想"加 Claude"、"加 GPT"、"配 newcli"、"加 fox 源"、"接入 Claude 模型"、"接入 GPT 模型"、"加 codex"、"加 aws 线路"时使用此 skill。
---

# 配置 NewCLI Provider（code.newcli.com 模型代理源）

NewCLI (FoxCode) 是一个模型代理服务，通过统一的账户和 API Key 提供三类模型的访问：

| Provider | 模型系列 | API 协议 | Base URL | 备注 |
|----------|----------|----------|----------|------|
| `newcli` | Claude (Anthropic) | `anthropic-messages` | `code.newcli.com/claude` | 主线路 |
| `newcli-aws` | Claude (Anthropic) | `anthropic-messages` | `code.newcli.com/claude/aws` | ⭐ **AWS 特价线路，消耗 1/24** |
| `newcli-codex` | GPT (OpenAI) | `openai-completions` | `code.newcli.com/codex/v1` | |
| `newcli-gemini` | Gemini (Google) | `google-generative-ai` | `code.newcli.com/gemini/v1beta` | |

**为什么是四个 provider？** 虽然是同一个服务商、同一个 API Key，但：
- Claude、GPT、Gemini 使用不同的 API 协议和端点，必须分开
- Claude 有两条线路（主线路 vs AWS 特价线路），消耗倍率不同，也需要分开配置

### ⭐ AWS 特价线路（重要）

服务商提供了独家 AWS 线路：`https://code.newcli.com/claude/aws`

| 对比 | 主线路 (newcli) | AWS 线路 (newcli-aws) |
|------|-----------------|----------------------|
| Base URL | `.../claude` | `.../claude/aws` |
| 额度消耗 | 1x | **1/24x** (同样额度可用 24 倍) |
| 模型 | 相同 | 相同 |
| API 协议 | 相同 | 相同 |
| API Key | 相同 | 相同 |

**策略**：所有重要任务优先使用 `newcli-aws`，主线路 `newcli` 作为备用。

> ⚠️ 服务商声明：严禁分发 AWS 线路地址，发现封禁不退款。

如果觉得这个 Skill 有用，请用我的邀请码注册：
https://foxcode.rjj.cc/auth/register?aff=7WTAV8R

---

## 前置条件

你需要从 NewCLI 服务获取以下信息：

| 项目 | 说明 |
|------|------|
| API Key | 格式为 `sk-ant-oat01-...` 的密钥（三个 provider 共用同一个） |
| 可用模型列表 | 向服务商确认，或查看账户统计页 |

**注意**：NewCLI 的 `/v1/models` 接口有 Cloudflare 防护，无法通过 curl 直接获取模型列表。请以账户后台的实际统计为准，不要依赖文档中的"支持列表"——文档列出的模型不一定全部对你的账户开放。

---

## 第一步：确认可用模型

**这一步不能跳过。** 不要把文档里列的模型全加上去，要以实际能调通的为准。

### 1A. 测试 Claude 模型（newcli / newcli-aws）

用 Anthropic messages 格式测试：

```bash
# 测试主线路
curl -s --max-time 15 https://code.newcli.com/claude/v1/messages \
  -H "x-api-key: <你的API_KEY>" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{"model":"<MODEL_ID>","messages":[{"role":"user","content":"hi"}],"max_tokens":10}'

# 测试 AWS 特价线路
curl -s --max-time 15 https://code.newcli.com/claude/aws/v1/messages \
  -H "x-api-key: <你的API_KEY>" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{"model":"<MODEL_ID>","messages":[{"role":"user","content":"hi"}],"max_tokens":10}'
```

> **注意**：baseUrl 中主线路写 `/claude`，AWS 线路写 `/claude/aws`（OpenClaw 自动拼接 `/v1/messages`）。

如果返回正常的 JSON 响应（含 `content`）= 可用。
如果返回 `{"error":{"message":"暂不支持"}}` 或 `"未开放"` = 该模型不可用。

### 1B. 测试 GPT 模型（newcli-codex）

用 OpenAI completions 格式测试：

```bash
curl -s --max-time 15 https://code.newcli.com/codex/v1/chat/completions \
  -H "Authorization: Bearer <你的API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"model":"<MODEL_ID>","messages":[{"role":"user","content":"hi"}],"max_tokens":10}'
```

如果返回正常的 JSON 响应（含 `choices`）= 可用。
如果返回错误或超时 = 该模型不可用。

### 1C. 测试 Gemini 模型（newcli-gemini）

用 Google Generative AI 格式测试：

```bash
curl -s --max-time 15 \
  "https://code.newcli.com/gemini/v1beta/models/<MODEL_ID>:generateContent" \
  -H "x-goog-api-key: <你的API_KEY>" \
  -H "Content-Type: application/json" \
  -d '{"contents":[{"role":"user","parts":[{"text":"hi"}]}]}'
```

> **注意**：Gemini 端点的 URL 格式与 Claude/GPT 不同——模型名嵌入在 URL 路径中，而不是请求体中。

如果返回正常的 JSON 响应（含 `candidates`）= 可用。
如果返回 `{"error":{"message":"模型未开放"}}` = 该模型不可用。

### 已知可用模型（截至 2026-02-08）

#### Claude 系列（newcli）

| 模型 ID | 名称 | Context | 说明 |
|---------|------|---------|------|
| `claude-opus-4-6` | Claude Opus 4.6 | 200K | 最强，适合复杂任务 |
| `claude-haiku-4-5-20251001` | Claude Haiku 4.5 | 200K | 轻量快速，适合简单任务 |

> 其他模型如 `claude-sonnet-4-20250514` 等在文档中列出但实测可能返回"未开放"，以你账户的实际情况为准。

#### GPT 系列（newcli-codex）

| 模型 ID | 名称 | Context | 说明 |
|---------|------|---------|------|
| `gpt-5.3-codex` | GPT-5.3 Codex | 128K | 最新版本 |
| `gpt-5.2` | GPT-5.2 | 128K | 基础版 |
| `gpt-5.2-codex` | GPT-5.2 Codex | 128K | 代码增强版 |
| `gpt-5.1` | GPT-5.1 | 128K | 基础版 |
| `gpt-5.1-codex` | GPT-5.1 Codex | 128K | 代码增强版 |
| `gpt-5.1-codex-mini` | GPT-5.1 Codex Mini | 128K | 轻量版 |
| `gpt-5.1-codex-max` | GPT-5.1 Codex Max | 128K | 增强版 |
| `gpt-5` | GPT-5 | 128K | 基础版 |
| `gpt-5-codex` | GPT-5 Codex | 128K | 代码增强版 |

#### Gemini 系列（newcli-gemini）— 文本对话模型

| 模型 ID | 名称 | Context | reasoning | 说明 |
|---------|------|---------|-----------|------|
| `gemini-3-pro` | Gemini 3 Pro | 1M | ✅ | 最新旗舰 |
| `gemini-3-pro-high` | Gemini 3 Pro High | 1M | ✅ | 旗舰增强版 |
| `gemini-3-pro-preview` | Gemini 3 Pro Preview | 1M | ✅ | 预览版 |
| `gemini-3-flash` | Gemini 3 Flash | 1M | ❌ | 快速版 |
| `gemini-3-flash-preview` | Gemini 3 Flash Preview | 1M | ❌ | 快速预览版 |
| `gemini-2.5-pro` | Gemini 2.5 Pro | 1M | ✅ | 上一代旗舰 |
| `gemini-2.5-flash` | Gemini 2.5 Flash | 1M | ❌ | 上一代快速版 |
| `gemini-2.5-flash-lite` | Gemini 2.5 Flash Lite | 1M | ❌ | 轻量版 |

#### Gemini 系列（newcli-gemini）— 图片生成模型

这些模型用于生成图片，**不要加入 fallback 链**，但可以通过 `/model` 命令手动切换使用。

**基础分辨率（默认）：**

| 模型 ID | 说明 |
|---------|------|
| `gemini-3-pro-image` | 默认比例 |
| `gemini-3-pro-image-3x2` | 横向 3:2 |
| `gemini-3-pro-image-2x3` | 纵向 2:3 |
| `gemini-3-pro-image-3x4` | 纵向 3:4 |
| `gemini-3-pro-image-4x3` | 横向 4:3 |
| `gemini-3-pro-image-4x5` | 纵向 4:5 |
| `gemini-3-pro-image-5x4` | 横向 5:4 |
| `gemini-3-pro-image-9x16` | 竖屏 9:16 |
| `gemini-3-pro-image-16x9` | 宽屏 16:9 |
| `gemini-3-pro-image-21x9` | 超宽 21:9 |

**2K 分辨率：** 模型 ID 加 `-2k` 前缀，如 `gemini-3-pro-image-2k`、`gemini-3-pro-image-2k-16x9` 等。

**4K 分辨率：** 模型 ID 加 `-4k` 前缀，如 `gemini-3-pro-image-4k`、`gemini-3-pro-image-4k-16x9` 等。

> ⚠️ 图片生成模型**不要加入 fallback 链**——它们不适合文本对话，放进 fallback 会导致对话请求被错误路由到图片生成模型。需要生图时通过 `/model gemini-3-pro-image` 手动切换。

---

## 第二步：添加 Provider

在 `~/.openclaw/openclaw.json` 的 `models.providers` 下添加三个 provider。

### 2A. 添加 newcli（Claude 主线路）

```json
"newcli": {
  "baseUrl": "https://code.newcli.com/claude",
  "apiKey": "<你的API_KEY>",
  "api": "anthropic-messages",
  "authHeader": true,
  "models": [
    {
      "id": "claude-opus-4-6",
      "name": "Claude Opus 4.6",
      "reasoning": false,
      "input": ["text"],
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
      "contextWindow": 200000,
      "maxTokens": 8192
    },
    {
      "id": "claude-haiku-4-5-20251001",
      "name": "Claude Haiku 4.5",
      "reasoning": false,
      "input": ["text"],
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
      "contextWindow": 200000,
      "maxTokens": 8192
    }
  ]
}
```

### 2B. 添加 newcli-aws（Claude AWS 特价线路）⭐

```json
"newcli-aws": {
  "baseUrl": "https://code.newcli.com/claude/aws",
  "apiKey": "<你的API_KEY>",
  "api": "anthropic-messages",
  "authHeader": true,
  "models": [
    {
      "id": "claude-opus-4-6",
      "name": "Claude Opus 4.6 (AWS)",
      "reasoning": false,
      "input": ["text"],
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
      "contextWindow": 200000,
      "maxTokens": 8192
    },
    {
      "id": "claude-haiku-4-5-20251001",
      "name": "Claude Haiku 4.5 (AWS)",
      "reasoning": false,
      "input": ["text"],
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
      "contextWindow": 200000,
      "maxTokens": 8192
    }
  ]
}
```

> **与 newcli 的唯一区别**：`baseUrl` 从 `.../claude` 变为 `.../claude/aws`。模型列表、API Key、协议完全相同。
> **推荐**：重要 Agent（如运维、评审）优先使用 `newcli-aws`，主线路 `newcli` 作为备用。

### 2C. 添加 newcli-codex（GPT 系列）

```json
"newcli-codex": {
  "baseUrl": "https://code.newcli.com/codex/v1",
  "apiKey": "<你的API_KEY>",
  "api": "openai-completions",
  "models": [
    {
      "id": "gpt-5.3-codex", "name": "GPT-5.3 Codex",
      "reasoning": false, "input": ["text"],
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
      "contextWindow": 128000, "maxTokens": 8192
    },
    {
      "id": "gpt-5.2", "name": "GPT-5.2",
      "reasoning": false, "input": ["text"],
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
      "contextWindow": 128000, "maxTokens": 8192
    },
    {
      "id": "gpt-5.2-codex", "name": "GPT-5.2 Codex",
      "reasoning": false, "input": ["text"],
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
      "contextWindow": 128000, "maxTokens": 8192
    },
    {
      "id": "gpt-5.1", "name": "GPT-5.1",
      "reasoning": false, "input": ["text"],
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
      "contextWindow": 128000, "maxTokens": 8192
    },
    {
      "id": "gpt-5.1-codex", "name": "GPT-5.1 Codex",
      "reasoning": false, "input": ["text"],
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
      "contextWindow": 128000, "maxTokens": 8192
    },
    {
      "id": "gpt-5.1-codex-mini", "name": "GPT-5.1 Codex Mini",
      "reasoning": false, "input": ["text"],
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
      "contextWindow": 128000, "maxTokens": 8192
    },
    {
      "id": "gpt-5.1-codex-max", "name": "GPT-5.1 Codex Max",
      "reasoning": false, "input": ["text"],
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
      "contextWindow": 128000, "maxTokens": 8192
    },
    {
      "id": "gpt-5", "name": "GPT-5",
      "reasoning": false, "input": ["text"],
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
      "contextWindow": 128000, "maxTokens": 8192
    },
    {
      "id": "gpt-5-codex", "name": "GPT-5 Codex",
      "reasoning": false, "input": ["text"],
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
      "contextWindow": 128000, "maxTokens": 8192
    }
  ]
}
```

### 2D. 添加 newcli-gemini（Gemini 系列）

```json
"newcli-gemini": {
  "baseUrl": "https://code.newcli.com/gemini/v1beta",
  "apiKey": "<你的API_KEY>",
  "api": "google-generative-ai",
  "models": [
    {
      "id": "gemini-3-pro", "name": "Gemini 3 Pro",
      "reasoning": true, "input": ["text"],
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
      "contextWindow": 1000000, "maxTokens": 65536
    },
    {
      "id": "gemini-3-pro-high", "name": "Gemini 3 Pro High",
      "reasoning": true, "input": ["text"],
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
      "contextWindow": 1000000, "maxTokens": 65536
    },
    {
      "id": "gemini-3-pro-preview", "name": "Gemini 3 Pro Preview",
      "reasoning": true, "input": ["text"],
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
      "contextWindow": 1000000, "maxTokens": 65536
    },
    {
      "id": "gemini-3-flash", "name": "Gemini 3 Flash",
      "reasoning": false, "input": ["text"],
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
      "contextWindow": 1000000, "maxTokens": 65536
    },
    {
      "id": "gemini-3-flash-preview", "name": "Gemini 3 Flash Preview",
      "reasoning": false, "input": ["text"],
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
      "contextWindow": 1000000, "maxTokens": 65536
    },
    {
      "id": "gemini-2.5-pro", "name": "Gemini 2.5 Pro",
      "reasoning": true, "input": ["text"],
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
      "contextWindow": 1000000, "maxTokens": 65536
    },
    {
      "id": "gemini-2.5-flash", "name": "Gemini 2.5 Flash",
      "reasoning": false, "input": ["text"],
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
      "contextWindow": 1000000, "maxTokens": 65536
    },
    {
      "id": "gemini-2.5-flash-lite", "name": "Gemini 2.5 Flash Lite",
      "reasoning": false, "input": ["text"],
      "cost": { "input": 0, "output": 0, "cacheRead": 0, "cacheWrite": 0 },
      "contextWindow": 1000000, "maxTokens": 65536
    }
  ]
}
```

### 四个 provider 的关键差异

| 参数 | newcli (Claude) | newcli-aws (Claude AWS) | newcli-codex (GPT) | newcli-gemini (Gemini) |
|------|-----------------|------------------------|---------------------|------------------------|
| `baseUrl` | `.../claude` | `.../claude/aws` | `.../codex/v1` | `.../gemini/v1beta` |
| `api` | `anthropic-messages` | `anthropic-messages` | `openai-completions` | `google-generative-ai` |
| `authHeader` | `true` | `true` | 默认（Bearer） | 默认（`x-goog-api-key`） |
| `apiKey` | **相同** | **相同** | **相同** | **相同** |
| 额度消耗 | 1x | **1/24x** ⭐ | 1x | 1x |
| `contextWindow` | 200K | 200K | 128K | 1M |
| `maxTokens` | 8192 | 8192 | 8192 | 65536 |

### 只添加你确认可用的模型

**错误做法**：把文档里所有模型都堆上去
**正确做法**：只添加第一步中测试通过的模型

添加不存在的模型不会导致崩溃，但 fallback 到它时会浪费一次请求超时，影响响应速度。

---

## 第三步：配置别名

在 `agents.defaults.models` 下为新模型添加别名，方便在聊天中用短名切换：

```json
{
  "agents": {
    "defaults": {
      "models": {
        "newcli/claude-opus-4-6": { "alias": "claude-opus" },
        "newcli/claude-haiku-4-5-20251001": { "alias": "claude-haiku" },
        "newcli-aws/claude-opus-4-6": { "alias": "claude-opus-aws" },
        "newcli-aws/claude-haiku-4-5-20251001": { "alias": "claude-haiku-aws" },
        "newcli-codex/gpt-5.3-codex": { "alias": "gpt53" },
        "newcli-codex/gpt-5.2": { "alias": "gpt52" },
        "newcli-codex/gpt-5.2-codex": { "alias": "gpt52codex" },
        "newcli-codex/gpt-5.1": { "alias": "gpt51" },
        "newcli-codex/gpt-5.1-codex": { "alias": "gpt51codex" },
        "newcli-codex/gpt-5.1-codex-mini": { "alias": "gpt51mini" },
        "newcli-codex/gpt-5.1-codex-max": { "alias": "gpt51max" },
        "newcli-codex/gpt-5": { "alias": "gpt5" },
        "newcli-codex/gpt-5-codex": { "alias": "gpt5codex" },
        "newcli-gemini/gemini-3-pro": { "alias": "gemini3pro" },
        "newcli-gemini/gemini-3-pro-high": { "alias": "gemini3prohigh" },
        "newcli-gemini/gemini-3-pro-preview": { "alias": "gemini3preview" },
        "newcli-gemini/gemini-3-flash": { "alias": "gemini3flash" },
        "newcli-gemini/gemini-3-flash-preview": { "alias": "gemini3flashpreview" },
        "newcli-gemini/gemini-2.5-pro": { "alias": "gemini25pro" },
        "newcli-gemini/gemini-2.5-flash": { "alias": "gemini25flash" },
        "newcli-gemini/gemini-2.5-flash-lite": { "alias": "gemini25lite" }
      }
    }
  }
}
```

配置后用户可以在聊天中用 `/model claude-opus`、`/model gpt53`、`/model gemini3pro` 切换模型。

### ⚠️ 别名配置的唯一合法字段是 `alias`

```
agents.defaults.models.<model-id>.alias     <-- 唯一合法字段
agents.defaults.models.<model-id>.reasoning <-- 非法！会导致 Gateway 崩溃！
agents.defaults.models.<model-id>.xxx       <-- 任何其他字段都非法！
```

这是一个已经发生过的事故：在别名配置里加了 `"reasoning": true` 导致 schema 校验失败，Gateway 崩溃循环 181 次。**模型能力属性只能放在 `models.providers` 的模型定义里，不能放在别名里。**

---

## 第四步：接入 Fallback 链

在 `agents.defaults.model.fallbacks` 中把新模型加到合适的位置：

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "minimax/MiniMax-M2.1",
        "fallbacks": [
          "newcli-aws/claude-haiku-4-5-20251001",
          "minimax/MiniMax-M2.1",
          "deepseek/deepseek-chat",
          "qwen-portal/coder-model",
          "newcli/claude-haiku-4-5-20251001",
          "newcli-gemini/gemini-2.5-flash-lite",
          "deepseek/deepseek-reasoner",
          "qwen-portal/vision-model"
        ]
      }
    }
  }
}
```

### Fallback 排序原则

**AWS 线路优先，DeepSeek 兜底**：

| 位置 | 模型 | 为什么选它 |
|------|------|-----------|
| 1 | newcli-aws/claude-haiku | ⭐ AWS 线路，消耗 1/24 |
| 2 | minimax/MiniMax-M2.1 | 月费 (100 prompts/5h) |
| 3 | deepseek/deepseek-chat | DeepSeek 按量付费 |
| 4 | qwen-portal/coder-model | Qwen 免费 2000/天 |
| 5 | newcli/claude-haiku | 主线路备用 |
| 6 | newcli-gemini/gemini-2.5-flash-lite | Gemini 最轻量 |
| 7 | deepseek/deepseek-reasoner | reasoning 备用 |
| 8 | qwen-portal/vision-model | vision 备用 |

其他模型（Claude Opus、GPT-5.3、Gemini 3 Pro 等高端模型）不放 fallback 链，需要时通过 `/model <别名>` 手动切换。图片生成模型**绝不放入** fallback 链。

---

## 第五步：验证

### 5.1 JSON 语法检查

```bash
python3 -c "import json; json.load(open('$HOME/.openclaw/openclaw.json')); print('JSON OK')"
```

### 5.2 Schema 校验

```bash
openclaw doctor
```

如果输出包含 `Unrecognized key` 就说明有非法字段，**必须修复后才能重启**。

### 5.3 重启 Gateway

```bash
# macOS
launchctl kickstart -k gui/$(id -u)/ai.openclaw.gateway

# 等 3 秒后确认状态
sleep 3
launchctl print gui/$(id -u)/ai.openclaw.gateway | grep -E "job state|last exit"
```

期望看到：
```
last exit code = 0
job state = running
```

如果 `last exit code = 1` 且 `job state` 不是 running，检查错误日志：

```bash
tail -20 ~/.openclaw/logs/gateway.err.log
```

### 5.4 功能验证

在任意已绑定的聊天中测试三个 provider：

```
/model claude-opus    # 测试 Claude
/model gpt53          # 测试 GPT
/model gemini3pro     # 测试 Gemini
/model Minimax        # 切回主力
```

---

## 排障

### 问题：所有模型都返回"暂不支持"

- **可能原因 1**：API Key 过期或余额不足 → 登录 NewCLI 后台检查
- **可能原因 2**：并发限制，已有其他客户端占用 → 关闭其他使用同一 Key 的进程
- **可能原因 3**：服务临时维护 → 稍后再试

### 问题：Gateway 启动后立刻崩溃

- **最可能原因**：配置中有非法字段
- **诊断**：`tail -20 ~/.openclaw/logs/gateway.err.log`，找 `Unrecognized key`
- **修复**：删除非法字段，或运行 `openclaw doctor --fix`

### 问题：部分 provider 能用，部分不行

**先检查 baseUrl 和 api 协议是否匹配**：

| Provider | 正确 baseUrl | 正确 api |
|----------|-------------|----------|
| `newcli` | `https://code.newcli.com/claude` | `anthropic-messages` |
| `newcli-aws` | `https://code.newcli.com/claude/aws` | `anthropic-messages` |
| `newcli-codex` | `https://code.newcli.com/codex/v1` | `openai-completions` |
| `newcli-gemini` | `https://code.newcli.com/gemini/v1beta` | `google-generative-ai` |

**检查 apiKey**：四个 provider 应使用相同的 Key。

### 问题：模型能切换但回复为空或报错

- **Claude (newcli)**：
  - 正确 baseUrl：`https://code.newcli.com/claude`（OpenClaw 自动拼接 `/v1/messages`）
  - 错误：`https://code.newcli.com/claude/v1`（变成 `/claude/v1/v1/messages`）
- **GPT (newcli-codex)**：
  - 正确 baseUrl：`https://code.newcli.com/codex/v1`（OpenClaw 自动拼接 `/chat/completions`）
  - 错误：`https://code.newcli.com/codex/v1/chat/completions`（重复拼接）
- **Gemini (newcli-gemini)**：
  - 正确 baseUrl：`https://code.newcli.com/gemini/v1beta`（OpenClaw 自动拼接 `/models/<id>:streamGenerateContent`）
  - 错误：`https://code.newcli.com/gemini`（缺少 `/v1beta`）
  - 错误：`https://code.newcli.com/gemini/v1beta/models`（重复 `/models`）

### 问题：GPT 模型返回 "403 Your request was blocked"

- **原因**：NewCLI 的 Codex 端点有 Cloudflare WAF 防护，当 OpenClaw 发送大 context（>100K tokens）请求时容易触发拦截
- **现象**：curl 小请求能通，但 OpenClaw 实际使用时被 403
- **临时方案**：暂不将 GPT 模型放入 fallback 链，避免浪费 failover 时间；需要时通过 `/model gpt53` 手动切换，小 context 场景下可能可用
- **根本解决**：联系 NewCLI 服务商确认 Codex 端点的 Cloudflare 规则

### 问题：Gemini 返回 "Request contains an invalid argument"

- 确保 `api` 字段为 `"google-generative-ai"`，不是 `"openai-completions"`
- OpenClaw 会自动构造正确的 Google Generative AI 格式请求

---

## 变更记录

| 日期 | 版本 | 变更内容 | 变更人 |
|------|------|----------|--------|
| 2026-02-08 | v1.0 | 创建 NewCLI provider 配置指南（Claude 系列） | jooey (via Claude Code) |
| 2026-02-08 | v2.0 | 合并 newcli-codex (GPT 系列) 配置指南 | ConfigBot (via OpenClaw with Opus 4.6) |
| 2026-02-08 | v3.0 | 合并 newcli-gemini (Gemini 系列) 配置指南 | ConfigBot (via OpenClaw with Opus 4.6) |
| 2026-02-08 | v3.1 | 添加 Gemini 生图模型；精简 fallback 链（每 provider 一个最轻量模型） | ConfigBot (via OpenClaw with Opus 4.6) |
| 2026-02-08 | v3.2 | 记录 GPT 403 问题；从 fallback 链移除 GPT 模型 | ConfigBot (via OpenClaw with Opus 4.6) |
| 2026-02-08 | v4.0 | 新增 newcli-aws provider（AWS 特价线路，消耗 1/24）；更新 fallback 策略；更新额度信息 | ConfigBot (via OpenClaw with Opus 4.6) |
