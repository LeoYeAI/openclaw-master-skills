# AI 大模型厂商分析框架

## 适用场景

当研究主题涉及**AI 大模型厂商**（Anthropic、Google、OpenAI、DeepSeek、豆包、智谱 AI 等）时使用本框架。

---

## 厂商列表

### 国际领先厂商

| 厂商 | 核心产品 | 关键分析点 |
|------|---------|-----------|
| **Anthropic** | Claude 3、Claude 3.5 | AI 安全研究、宪法 AI、企业级应用、API 生态 |
| **Google** | Gemini、Bard、Vertex AI | 多模态能力、企业集成、云生态、搜索整合 |
| **OpenAI** | GPT-4、ChatGPT、DALL-E、Sora | 技术领先性、应用生态、商业化路径、API 服务 |
| **Microsoft** | Copilot、Azure OpenAI | 企业办公集成、云服务整合、Bing 搜索、Office 365 |
| **Meta** | Llama 系列（开源） | 开源策略、社区生态、社交媒体整合 |
| **Amazon** | Bedrock、Titan | 云服务整合、多模型支持、企业应用 |

### 国内领先厂商

| 厂商 | 核心产品 | 关键分析点 |
|------|---------|-----------|
| **DeepSeek** | DeepSeek-V2、DeepSeek Coder | 开源大模型、代码能力、成本优势、社区生态 |
| **豆包** | 豆包大模型、云雀 | 字节生态整合、短视频应用、To C 产品矩阵、AI 工具（PPT、生图） |
| **智谱 AI** | GLM-4、ChatGLM | 清华技术背景、开源社区、企业服务、金融行业应用 |
| **百度** | 文心一言（ERNIE） | 搜索整合、知识图谱、企业服务、自动驾驶应用 |
| **阿里** | 通义千问、通义万象 | 电商生态整合、云计算服务、企业级应用 |
| **腾讯** | 混元大模型 | 社交生态整合、游戏应用、企业微信、云计算 |

---

## 核心分析维度

| 维度 | 关键指标 | 数据来源 |
|------|---------|---------|
| **技术能力** | 参数规模、性能基准（MMLU、HumanEval）、多模态能力 | 技术论文、评测榜单、官方发布 |
| **产品矩阵** | To C 产品、To B 产品、API 服务、行业解决方案 | 官网、产品页面、开发者文档 |
| **应用生态** | 应用数量、开发者数量、API 调用量、合作伙伴 | 开发者平台、应用商店、合作伙伴页面 |
| **商业模式** | 订阅制、按量计费、API 定价、企业定制 | 官网定价、财报、销售材料 |
| **市场表现** | 用户数量、市场份额、收入规模、增长率 | 财报、行业报告、第三方数据 |

---

## 数据收集优先级

| 数据类型 | 具体内容 | 优先级 |
|---------|---------|--------|
| **产品发布** | 最新版本、功能更新、技术路线图 | P0 |
| **技术评测** | 性能基准、第三方评测、对比测试 | P0 |
| **商业模式** | 定价策略、订阅模式、API 价格 | P0 |
| **应用生态** | 开发者数量、应用数量、合作伙伴 | P1 |
| **市场表现** | 用户数量、收入、市场份额 | P1 |

---

## 官方数据来源

### 国际厂商

| 厂商 | 官网 | 开发者平台 |
|------|------|-----------|
| Anthropic | `https://www.anthropic.com/` | `https://docs.anthropic.com/` |
| Google | `https://ai.google/` | `https://cloud.google.com/vertex-ai` |
| OpenAI | `https://openai.com/` | `https://platform.openai.com/` |
| Microsoft | - | `https://azure.microsoft.com/en-us/products/cognitive-services` |
| Meta | `https://llama.meta.com/` | `https://github.com/facebookresearch` |

### 国内厂商

| 厂商 | 官网 | 开发者平台 |
|------|------|-----------|
| DeepSeek | `https://www.deepseek.com/` | `https://github.com/deepseek-ai` |
| 豆包 | `https://www.doubao.com/` | `https://www.volcengine.com/` |
| 智谱 AI | `https://www.zhipuai.cn/` | `https://github.com/THUDM` |
| 百度 | `https://yiyan.baidu.com/` | `https://cloud.baidu.com/` |
| 阿里 | `https://tongyi.aliyun.com/` | `https://www.aliyun.com/` |
| 腾讯 | `https://hunyuan.tencent.com/` | `https://cloud.tencent.com/` |

---

## 快速搜索模板

```markdown
# 技术能力搜索
web_search(query="{厂商名} {产品名} 性能评测 benchmark 2024", max_results=5)

# 产品发布搜索
web_search(query="{厂商名} {产品名} release update 2024", max_results=5)

# 商业模式搜索
web_search(query="{厂商名} API 定价 订阅模式", max_results=5)

# 应用生态搜索
web_search(query="{厂商名} 开发者生态 合作伙伴", max_results=5)
```

---

## 分析示例

**分析 DeepSeek**：

```markdown
# 技术能力
web_search(query="DeepSeek V2 性能评测 benchmark 2024", max_results=5)
web_fetch(url="https://www.deepseek.com/")
web_fetch(url="https://github.com/deepseek-ai")

# 产品矩阵
web_search(query="DeepSeek 产品矩阵 应用场景", max_results=5)

# 商业模式
web_search(query="DeepSeek API 定价 开源策略", max_results=5)
```
