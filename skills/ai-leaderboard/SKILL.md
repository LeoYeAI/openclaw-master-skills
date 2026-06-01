---
name: AI Rankings Leaderboard
display_name: AI Rankings Leaderboard / AI 排行榜
description: Comprehensive AI leaderboard for LLM models and AI applications. Query model rankings, model IDs, and pricing from OpenRouter, Artificial Analysis, and Pinchbench. Trigger words include "AI rankings", "LLM leaderboard", "model comparison", "AI apps ranking", "best AI models", "model benchmark", "free models", "免费模型", "OpenRouter model ID", "OpenRouter 模型", "Artificial Analysis", "artificial analysis", "AI 智力指数", "intelligence index", "coding index", "coding排行榜", "agentic index", "agentic排行榜", "模型速度排行", "模型价格对比", "model ID for", "OpenRouter model parameter".
version: 1.20.1
cli_dependencies:
  - agent-browser
---

# AI Rankings Leaderboard Skill

## Description

A comprehensive skill for querying AI model and application rankings from multiple authoritative sources. Get the latest insights on LLM performance, popularity, pricing, and value metrics.

## Data Sources

| Source | URL | Focus |
|--------|-----|-------|
| **Artificial Analysis** | https://artificialanalysis.ai/ | Intelligence Index, Speed, Price benchmarks |
| LLM Leaderboard | https://artificialanalysis.ai/leaderboards/models | Model comparison (100+ models) |
| LLM API Providers | https://artificialanalysis.ai/leaderboards/providers | API Provider comparison (500+ endpoints) |
| Image & Video Leaderboards | https://artificialanalysis.ai/ (Image & Video section) | Image/Video model ELO rankings |
| OpenRouter Rankings | https://openrouter.ai/rankings | Model usage & popularity |
| OpenRouter Apps | https://openrouter.ai/apps | AI applications ranking |
| OpenRouter Models | https://openrouter.ai/models | All available models with pricing |
| OpenRouter Free Models | https://openrouter.ai/models?q=free | Free models only |
| Pinchbench | https://pinchbench.com/ | Model benchmark (Success Rate, Speed, Cost, Value) |

## Features

### 1. Artificial Analysis LLM Leaderboard

**Intelligence Index (智力指数)**
- **Artificial Analysis Intelligence Index v4.0**: Comprehensive model intelligence score
- **10 evaluation dimensions**: Multiple independent assessment criteria
- **Frontier Models**: Top intelligence models (Gemini 3.1 Pro, GPT-5.4, Claude Opus 4.6, etc.)
- **Reasoning Models**: Identifies models with reasoning capabilities

**Artificial Analysis Coding Index** (编程能力指数)
- URL: https://artificialanalysis.ai/?intelligence=coding-index
- 评估模型在编程任务上的表现
- 综合多个代码评测基准

**Artificial Analysis Agentic Index** (智能体能力指数)
- URL: https://artificialanalysis.ai/?intelligence=agentic-index
- 评估模型的自主智能体能力
- 包括工具使用、多步骤推理、任务完成等

**Performance Metrics**
| Metric | Description |
|--------|-------------|
| Intelligence Index | Overall model intelligence score (higher is better) |
| Speed | Output tokens per second (tokens/s) |
| Blended Price | Combined USD per million tokens (3:1 input/output ratio) |
| Input Price | Price per million input tokens (USD) |
| Output Price | Price per million output tokens (USD) |
| Latency (TTFT) | Time to First Token in seconds |
| Context Window | Maximum context length supported |

**Model Comparison Table Columns**
| Column | Description |
|--------|-------------|
| Features | Model features (reasoning badge, etc.) |
| Model | Model name with logo |
| Context Window | Max context length |
| Creator | Provider/Company |
| Intelligence Index | AI intelligence score |
| Blended USD/1M Tokens | Combined input/output price |
| Median Tokens/s | Median output speed |
| Latency First Chunk (s) | Time to first token |
| Further Analysis | Link to detailed analysis |

**Filters Available**
| Filter | Options |
|--------|---------|
| Frontier Models | On/Off |
| Open Weights | On/Off (开源权重模型) |
| Size Class | Small, Medium, Large, etc. |
| Reasoning | On/Off (推理模型筛选) |
| Model Status | Current, Preview, Discontinued |

### 2. Artificial Analysis LLM API Providers Leaderboard

**Comparison of 500+ AI Model Endpoints**

| Column | Description |
|--------|-------------|
| API Provider | Provider name (Cerebras, Groq, Fireworks, etc.) |
| Model | Model name |
| Context Window | Max context length |
| License | Model license |
| Intelligence Index | Model intelligence score |
| Blended USD/1M Tokens | Combined price |
| Median Tokens/s | Output speed |
| Median First Chunk (s) | Latency (TTFT) |
| Total Response (s) | End-to-end response time |
| Reasoning Time (s) | Reasoning model computation time |
| End-to-End Response Time | Full request-response cycle |

**Key Providers**
- Cerebras
- Eigen AI
- Fireworks
- SambaNova
- Together.ai
- Hyperbolic
- Nebius Fast
- Google Vertex
- Groq
- Azure OpenAI
- AWS Bedrock
- OpenAI Direct
- Anthropic Direct
- And 10+ more...

### 3. Artificial Analysis Image & Video Leaderboards

**Text-to-Image Leaderboard**
- ELO scores from blind preference votes
- 95% confidence intervals displayed
- Top models: GPT Image 1.5, Imagen 4 Ultra, Gemini Image models, etc.

**Video Leaderboards**
| Category | Description |
|----------|-------------|
| Text to Video (with Audio) | Text generates video with sound |
| Text to Video (without Audio) | Text generates silent video |
| Image to Video (with Audio) | Image + text generates video with sound |
| Image to Video (without Audio) | Image + text generates silent video |
| Image Editing | Edit existing images with AI |

**Evaluation Method**
- ELO scoring system (blind preference voting)
- 95% confidence intervals
- Real user preference data

### 4. OpenRouter Model Rankings
- **LLM Leaderboard**: Overall model usage rankings
- **Market Share**: Market share by model provider
- **Categories**: Rankings by use case
- **Languages**: Natural language support rankings
- **Programming**: Programming language support
- **Context Length**: Long context handling
- **Tool Calls**: Tool calling capabilities
- **Images**: Image processing volume

### 5. OpenRouter App Rankings
- **Most Popular**: Top apps by token usage
- **Trending**: Fastest growing apps this week
- **Categories**: Coding Agents, Productivity, Creative, Entertainment

### 6. OpenRouter Model Catalog
- **All Models**: Complete list of available models on OpenRouter
- **Free Models**: Models with $0 pricing (free to use)
- **Model ID**: The exact `model` parameter to use when calling OpenRouter API
- **Pricing Info**: Input/output token pricing

### 7. Pinchbench Benchmarks
- **Success Rate**: Task completion success percentage
- **Speed**: Response time performance
- **Cost**: Cost per run analysis
- **Value**: Price-performance ratio

## Trigger Keywords

### General AI Rankings
- "AI rankings" / "AI 排行榜"
- "LLM leaderboard" / "LLM 排行"
- "model comparison" / "模型对比"
- "best AI models" / "最好的 AI 模型"
- "AI apps ranking" / "AI 应用排行"
- "model benchmark" / "模型评测"

### Artificial Analysis Specific
- "Artificial Analysis" / "artificialanalysis"
- "AI intelligence index" / "AI 智力指数"
- "intelligence index" / "智力指数"
- "模型速度排行" / "speed ranking"
- "模型价格对比" / "price comparison"
- "fastest models" / "最快模型"
- "cheapest models" / "最便宜模型"
- "tokens per second" / "t/s" / "tokens/s"
- "latency" / "TTFT" / "首 token 延迟"
- "Artificial Analysis Intelligence Index"
- "AAII" / "AA Intelligence"
- "API providers" / "API 提供商"
- "LLM providers" / "LLM 提供商"
- "Cerebras" / "Groq" / "Fireworks"
- "open weights" / "开源权重"
- "reasoning models" / "推理模型"
- "elo score" / "ELO 评分"
- "image arena" / "图生图"
- "text to image" / "文生图"
- "text to video" / "文生视频"
- "image to video" / "图生视频"

### OpenRouter Specific
- "free models" / "免费模型" / "free AI models"
- "OpenRouter models" / "OpenRouter 免费模型"
- "OpenRouter rankings" / "OpenRouter 排行"
- "Pinchbench"
- "OpenRouter model ID" / "OpenRouter 模型 ID"
- "查找 OpenRouter" / "OpenRouter 上的模型"
- "model ID for [模型名]" / "[模型名] model ID"
- "OpenRouter 上 [模型名]" / "OpenRouter [模型名] 模型"
- "OpenRouter model parameter"
- "调用量排行" / "使用量排行" / "top models" / "top 模型"
- "OpenRouter 调用量" / "OpenRouter 使用量"

## Runtime Tools

This skill requires:
- `execute_command`: Execute shell commands and scripts
- `use_skill`: Load browser-automation skill for JavaScript-rendered pages
- `web_fetch`: Fallback for simple HTTP requests

## Installation

**Required CLI Dependency**: `agent-browser`

The `agent-browser` CLI must be installed before using this skill. Install via:

```bash
npm install -g agent-browser
# or
npx agent-browser --version
```

This skill calls `agent-browser` via subprocess with hardcoded argument arrays (no shell injection risk).

**Note on browser eval**: The `agent-browser eval` command executes `document.body.innerText` or similar DOM queries on the remote page to extract rendered content. This is standard web scraping behavior for JavaScript-rendered pages and is limited to reading page content only.

## Browser Automation Support

For JavaScript-rendered pages (OpenRouter Rankings, Artificial Analysis), this skill uses browser automation:

1. **Load browser-automation skill first**:
   ```
   use_skill("browser-automation")
   ```

2. **Navigate to rankings page**:
   ```bash
   agent-browser open "https://artificialanalysis.ai/leaderboards/models"
   agent-browser wait --load networkidle
   agent-browser eval "document.body.innerText"
   ```

3. **Key pages requiring browser**:
   - `https://artificialanalysis.ai/leaderboards/models` - LLM comparison (100+ models)
   - `https://artificialanalysis.ai/leaderboards/providers` - API providers (500+ endpoints)
   - `https://artificialanalysis.ai/` - Image & Video leaderboards
   - `https://openrouter.ai/rankings` - Model usage rankings (JS rendered)
   - `https://openrouter.ai/apps` - App rankings (JS rendered)

### Artificial Analysis Page Structure

**LLM Leaderboard Page** (`/leaderboards/models`):
```
LLM Leaderboard - Comparison of over 100 AI models
├── HIGHLIGHTS section
│   ├── Intelligence: Gemini 3.1 Pro Preview, GPT-5.4 (xhigh)
│   ├── Speed: Mercury 2 (943 t/s), NVIDIA Nemotron 3 Super (462 t/s)
│   └── Price: Gemma 3n E4B (cheapest)
├── Filters:
│   ├── Frontier Models | Open Weights | Size Class | Reasoning | Model Status
├── Comparison table columns:
│   ├── Features | Model | Context Window | Creator
│   ├── Intelligence Index | Blended USD/1M | Median Tokens/s | Latency
│   └── Further Analysis
└── Key definitions (expandable)
    ├── Context window
    ├── Output Speed (tokens/s)
    ├── Latency (Time to First Token)
    ├── Price (3:1 blended)
    ├── Output Price
    └── Input Price
```

**LLM API Providers Page** (`/leaderboards/providers`):
```
LLM API Providers Leaderboard - 500+ endpoints
├── Filters (same as LLM Leaderboard)
├── Comparison table columns:
│   ├── API Provider | Model | Context Window | License
│   ├── Intelligence Index | Blended USD/1M | Median Tokens/s
│   ├── Median First Chunk (s) | Total Response (s) | Reasoning Time (s)
│   └── Further Analysis
└── 24+ Providers: Cerebras, Groq, Fireworks, SambaNova, etc.
```

**Image & Video Leaderboards** (on homepage):
```
Image & Video Leaderboards
├── Tabs:
│   ├── Text to Image (ELO scores, 95% CI)
│   ├── Image Editing
│   ├── Text to Video (with Audio)
│   ├── Text to Video (without Audio)
│   ├── Image to Video (with Audio)
│   └── Image to Video (without Audio)
└── Top models with ELO rankings
```

### OpenRouter Page Structure (Reminder)

**OpenRouter Rankings Page** (`/rankings`):
```
https://openrouter.ai/rankings
├── Top Models (chart header)
├── LLM Leaderboard ← THIS is the usage ranking (parse this!)
│   ├── 1. MiniMax M2.5 (1.75T tokens)
│   ├── 2. Step 3.5 Flash (1.34T tokens)
│   └── [Show more] button
├── Market Share (different metric - don't mix!)
└── ...
```

## Usage Examples

### Query Artificial Analysis Intelligence Index
```
User: "What are the top models on Artificial Analysis Intelligence Index?"
-> Fetches Artificial Analysis LLM Leaderboard and displays top models by intelligence
```

### Query Model Speed Rankings
```
User: "Which AI models are the fastest in terms of output speed?"
-> Fetches Artificial Analysis data and lists models by tokens/second
```

### Query API Providers
```
User: "Compare LLM API providers like Cerebras and Groq"
-> Fetches Artificial Analysis Providers Leaderboard and compares speed/price
```

### Query Image/Video Models
```
User: "What are the best text-to-image models?"
-> Fetches Artificial Analysis Image Arena leaderboard with ELO scores
```

### Query Model Rankings (OpenRouter)
```
User: "What are the top 10 AI models right now?"
-> Fetches OpenRouter rankings and displays top models with usage stats
```

### Query Free Models
```
User: "What free models are available on OpenRouter?"
-> Fetches https://openrouter.ai/models?q=free and lists all free models with their model IDs
```

### Get Model ID for API Calls
```
User: "What's the model ID for GPT-4o on OpenRouter?"
-> Fetches https://openrouter.ai/models and returns the exact model parameter to use
```

### Compare Model Performance
```
User: "Compare GPT-4 and Claude on Pinchbench"
-> Fetches Pinchbench data and compares success rate, speed, cost
```

## Output Format

### Artificial Analysis Intelligence Index
```
==================================================
    Artificial Analysis Intelligence Index
==================================================

Top 10 Models by Intelligence:

| Rank | Model | Intelligence | Speed (t/s) | Price ($/M) |
|------|-------|--------------|-------------|-------------|
| 1 | Gemini 3.1 Pro Preview | 57 | ~50 | $1.25 |
| 2 | GPT-5.4 (xhigh) | 57 | ~60 | $15.00 |
| 3 | Claude Opus 4.6 (max) | 53 | ~80 | $18.00 |
| 4 | Claude Sonnet 4.6 (max) | 52 | ~85 | $4.50 |
| 5 | GLM-5 | 50 | ~45 | $0.50 |
...

Fastest Models: Mercury 2 (943 t/s), NVIDIA Nemotron 3 Super (462 t/s)
Best Price: Gemma 3n E4B, Granite 4.0 H Small

Data Source: Artificial Analysis (artificialanalysis.ai)
==================================================
```

### API Providers Comparison
```
==================================================
    LLM API Providers Leaderboard
==================================================

| Provider | Model | Speed (t/s) | Price ($/M) | Latency (s) |
|----------|-------|-------------|-------------|-------------|
| Cerebras | Llama 3.1 70B | 2143 | $0.12 | 0.08 |
| Groq | Llama 3.1 70B | 943 | $0.59 | 0.15 |
| Fireworks | Llama 3.1 70B | 562 | $0.90 | 0.22 |
...

Data Source: Artificial Analysis Providers
==================================================
```

### Image Arena (ELO Rankings)
```
==================================================
    Text-to-Image Leaderboard (ELO)
==================================================

| Rank | Model | ELO Score | 95% CI |
|------|-------|-----------|--------|
| 1 | GPT Image 1.5 (high) | 1342 | ±12 |
| 2 | Imagen 4 Ultra | 1289 | ±15 |
| 3 | Gemini 3.1 Flash Image | 1245 | ±18 |
...

Data Source: Artificial Analysis Image Arena
==================================================
```

### OpenRouter Model Rankings
```
==================================================
    AI Model Rankings (OpenRouter)
==================================================

Top 10 Models by Usage:

| Rank | Model | Provider | Tokens | Growth |
|------|-------|----------|--------|--------|
| 1 | MiniMax M2.5 | minimax | 1.75T | +15% |
| 2 | Step 3.5 Flash | step | 1.34T | +22% |
...

Data Source: OpenRouter (Weekly Rankings)
==================================================
```

### Free Models List
```
==================================================
    Free Models on OpenRouter
==================================================

| Model Name | Model ID (for API) | Context |
|------------|-------------------|---------|
| GPT-4o Mini | openai/gpt-4o-mini | 128K |
| Llama 3.3 70B | meta-llama/llama-3.3-70b-instruct | 128K |
| DeepSeek V3 | deepseek/deepseek-chat | 64K |
...

💡 Usage: Set model parameter to the Model ID value
   Example: model="openai/gpt-4o-mini"

Data Source: OpenRouter Models
==================================================
```

## Execution Instructions

### Method 1: Browser Automation for Rankings (Recommended)

Artificial Analysis and OpenRouter rankings pages require JavaScript rendering:

```bash
# Step 1: Load browser-automation skill (REQUIRED)
use_skill("browser-automation")

# Step 2: Navigate to Artificial Analysis LLM Leaderboard
agent-browser open "https://artificialanalysis.ai/leaderboards/models"
agent-browser wait --load networkidle

# Step 3: Wait for content to load, then extract
agent-browser wait 3000
agent-browser eval "document.body.innerText"

# Step 4: Close browser when done
agent-browser close
```

### Method 2: Python Script for OpenRouter Model Catalog

Use the `query_leaderboard.py` script to fetch model data via OpenRouter API (no JavaScript needed):

```bash
# List free models
python3 "${SKILL_DIR}/query_leaderboard.py --free"

# Search models by name
python3 "${SKILL_DIR}/query_leaderboard.py -s glm"
python3 "${SKILL_DIR}/query_leaderboard.py -s gpt"

# Get specific model info
python3 "${SKILL_DIR}/query_leaderboard.py --id openai/gpt-4o"

# List all models with limit
python3 "${SKILL_DIR}/query_leaderboard.py --all --limit 50"
```

### Method 3: Web Fetch (Fallback)

When browser/Python is not available, use `web_fetch`:

1. **For Artificial Analysis**: Fetch `https://artificialanalysis.ai/leaderboards/models`
2. **For OpenRouter model catalog**: Use OpenRouter API `https://openrouter.ai/api/v1/models`
3. **For benchmarks**: Fetch `https://pinchbench.com/`

**Note**: Rankings pages require JavaScript rendering - use browser automation (Method 1).

## Notes

- Data is updated regularly (Artificial Analysis, OpenRouter weekly, Pinchbench near real-time)
- Artificial Analysis Intelligence Index is based on 10 independent evaluations
- ELO scores are from blind preference voting with 95% confidence intervals
- Pinchbench disclaimer: "For entertainment purposes only, should not be relied upon for critical decisions"
- Rankings reflect actual usage data from millions of users
- Free models have $0.00 pricing on OpenRouter
- **Model ID format**: Use the exact string (e.g., `openai/gpt-4o-mini`) as the `model` parameter in API calls

## Artificial Analysis API Patterns

Based on observed page structure, Artificial Analysis provides:
- **Model comparison data**: https://artificialanalysis.ai/leaderboards/models
- **Provider comparison**: https://artificialanalysis.ai/leaderboards/providers
- **Image/Video arenas**: Embedded on homepage with tab navigation
- **Model-specific provider data**: `/models/{model-id}/providers` endpoint pattern

**Example model providers API**:
```
/models/gpt-oss-120b/providers
/models/gemini-3-1-pro-preview/providers
/models/claude-opus-4-6-adaptive/providers
```

## OpenRouter API Usage

When calling OpenRouter API (for chat completions), use the Model ID. Note: This skill's scripts (fetch_rankings.py, query_leaderboard.py) only read public leaderboard data and do NOT require API authentication.

```bash
curl https://openrouter.ai/api/v1/chat/completions \
  -H "Authorization: Bearer $OPENROUTER_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "openai/gpt-4o-mini",  # <- Model ID from this skill
    "messages": [{"role": "user", "content": "Hello"}]
  }'
```

