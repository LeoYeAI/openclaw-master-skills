# AI 技术与 SaaS 厂商数据来源指南

## 概述

本文档提供针对 **AI 技术产品**和 **SaaS 厂商**的关键数据来源，帮助快速定位产品发布、市场活动、客户案例、招投标、生态活动、战略合作、投资并购等信息。

---

## AI 技术产品数据来源

### 官方渠道

| 数据类型 | 来源 | URL 示例 |
|---------|------|---------|
| **产品官网** | 厂商官网 | `https://www.anthropic.com/`、`https://openai.com/` |
| **技术博客** | 官方技术博客 | `https://www.anthropic.com/research`、`https://openai.com/blog` |
| **产品更新** | 更新日志、发布公告 | 官网产品页面、博客发布 |
| **技术文档** | API 文档、开发指南 | `https://docs.anthropic.com/`、`https://platform.openai.com/docs` |
| **GitHub** | 开源项目、代码库 | `https://github.com/anthropics`、`https://github.com/openai` |

### 社区与生态

| 数据类型 | 来源 | 搜索方法 |
|---------|------|---------|
| **开发者社区** | Discord、论坛、Reddit | `site:discord.com "AI agent"`、`site:reddit.com/r/LocalLLaMA` |
| **技术讨论** | Hacker News、Twitter/X | `site:news.ycombinator.com "MCP protocol"` |
| **技术评测** | YouTube、技术媒体 | `AI agent 技术评测`、`Claude vs GPT 对比` |
| **开源项目** | GitHub Trending、Awesome 列表 | `site:github.com "AI agent" stars:>1000` |

### 行业媒体

| 数据类型 | 来源 | URL 示例 |
|---------|------|---------|
| **AI 行业媒体** | 机器之心、新智元、量子位 | `https://www.jiqizhixin.com/` |
| **国际媒体** | The Verge、TechCrunch、VentureBeat | `https://techcrunch.com/category/artificial-intelligence/` |
| **研究报告** | ARK Invest、a16z、红杉资本 | `https://www.ark-invest.com/research` |

---

## SaaS 厂商数据来源

### 1. 产品发布与技术演进

| 数据类型 | 来源 | 搜索方法 |
|---------|------|---------|
| **产品发布会** | 官网活动页面、直播 | `site:kingdee.com "发布会"`、`site:yonyou.com "新品发布"` |
| **版本更新** | 官网产品页面、更新日志 | `site:kingdee.com "产品更新"`、`site:sap.com "release notes"` |
| **技术博客** | 官方技术博客、CTO 分享 | `site:kingdee.com "技术博客"`、`site:sap.com "technology blog"` |
| **技术大会** | 开发者大会、技术峰会 | `site:kingdee.com "开发者大会"`、`site:sap.com "SAPPHIRE"` |

**快速搜索示例**：
```
web_search(query="金蝶 云星空 最新版本 2024", max_results=5)
web_search(query="用友 BIP 产品发布会 2024", max_results=5)
web_search(query="SAP S/4HANA release 2024", max_results=5)
```

---

### 2. 市场活动与品牌建设

| 数据类型 | 来源 | 搜索方法 |
|---------|------|---------|
| **市场活动** | 官网新闻、活动报道 | `site:kingdee.com "活动"`、`site:yonyou.com "市场活动"` |
| **品牌传播** | 广告投放、媒体报道 | `金蝶 品牌营销 2024`、`用友 品牌传播` |
| **内容营销** | 白皮书、行业报告 | `site:kingdee.com filetype:pdf`、`site:yonyou.com 白皮书` |
| **奖项荣誉** | 行业奖项、认证 | `金蝶 获奖 2024`、`用友 行业奖项` |

**快速搜索示例**：
```
web_search(query="金蝶 市场活动 2024", max_results=5)
web_search(query="用友 行业奖项 2024", max_results=5)
web_fetch(url="https://www.sap.com/about/awards.html")
```

---

### 3. 客户案例与行业覆盖

| 数据类型 | 来源 | 搜索方法 |
|---------|------|---------|
| **标杆客户** | 官网案例、客户故事 | `site:kingdee.com "客户案例"`、`site:yonyou.com "成功案例"` |
| **行业解决方案** | 行业页面、解决方案手册 | `site:kingdee.com "行业解决方案"`、`site:sap.com/industries` |
| **客户成功** | 客户证言、案例研究 | `金蝶 客户成功案例`、`用友 客户故事` |
| **客户结构** | 财报、分析师报告 | `site:kingdee.com "年报"`、`site:sap.com "annual report"` |

**快速搜索示例**：
```
web_search(query="金蝶 标杆客户 案例 2024", max_results=5)
web_search(query="用友 行业解决方案 制造业", max_results=5)
web_fetch(url="https://www.sap.com/customers/index.html")
```

---

### 4. 招投标与政企市场

| 数据类型 | 来源 | URL 示例 |
|---------|------|---------|
| **政府采购网** | 中央政府采购网、各省采购网 | `http://www.ccgp.gov.cn/` |
| **招投标平台** | 中国招标投标公共服务平台 | `http://www.cebpubservice.com/` |
| **企业招标** | 企业官网招标公告 | `site:kingdee.com "中标"`、`site:yonyou.com "中标公告"` |
| **政企客户** | 官网案例、新闻公告 | `金蝶 政企客户 中标`、`用友 央企 案例` |

**快速搜索示例**：
```
web_search(query="site:ccgp.gov.cn 金蝶 中标 2024", max_results=5)
web_search(query="site:cebpubservice.com 用友 招投标", max_results=5)
web_search(query="金蝶 央企 ERP 中标 2024", max_results=5)
```

**招投标信息提取重点**：
- 中标金额
- 项目名称
- 客户类型（政府/央企/国企）
- 项目范围（实施/运维/定制开发）
- 竞争对手

---

### 5. 生态活动与合作伙伴

| 数据类型 | 来源 | 搜索方法 |
|---------|------|---------|
| **生态大会** | 官网活动页面、新闻 | `site:kingdee.com "生态大会"`、`site:yonyou.com "伙伴大会"` |
| **合作伙伴** | 合作伙伴页面 | `site:kingdee.com "合作伙伴"`、`site:sap.com/partners` |
| **ISV 生态** | ISV 列表、应用市场 | `金蝶 ISV 伙伴`、`SAP App Center` |
| **开发者社区** | 开发者平台、论坛 | `site:kingdee.com "开发者社区"`、`site:sap.com/developers` |

**快速搜索示例**：
```
web_search(query="金蝶 生态大会 2024", max_results=5)
web_search(query="用友 合作伙伴 生态", max_results=5)
web_fetch(url="https://partner.sap.com/")
```

---

### 6. 战略合作与投资并购

| 数据类型 | 来源 | 搜索方法 |
|---------|------|---------|
| **战略合作** | 新闻公告、联合发布 | `金蝶 战略合作 2024`、`用友 战略联盟` |
| **投资并购** | 财报、投资公告 | `site:kingdee.com "投资"`、`site:sap.com "acquisition"` |
| **组织调整** | 新闻、内部邮件泄露 | `金蝶 组织架构调整`、`用友 高管变动` |
| **国际化** | 海外官网、扩张新闻 | `site:kingdee.com "国际化"`、`site:sap.com "China strategy"` |

**快速搜索示例**：
```
web_search(query="金蝶 战略合作 投资 2024", max_results=5)
web_search(query="用友 并购 2024", max_results=5)
web_search(query="SAP acquisition 2024", max_results=5)
```

---

## AI 大模型厂商数据来源

### 国际领先厂商

| 厂商 | 官方来源 | 关键信息 |
|------|---------|---------|
| **Anthropic** | `https://www.anthropic.com/` | Claude 产品更新、API 文档、研究报告 |
| **Google** | `https://ai.google/`、`https://cloud.google.com/vertex-ai` | Gemini 产品、Vertex AI 平台、技术博客 |
| **OpenAI** | `https://openai.com/`、`https://platform.openai.com/` | GPT 产品、API 文档、研究论文 |
| **Microsoft** | `https://azure.microsoft.com/en-us/products/cognitive-services` | Azure OpenAI、Copilot 产品、技术文档 |
| **Meta** | `https://llama.meta.com/`、`https://github.com/facebookresearch` | Llama 开源模型、研究论文、社区 |

**快速搜索示例**：
```
web_search(query="Claude 3.5 Sonnet release 2024", max_results=5)
web_search(query="Gemini 2.0 features capabilities", max_results=5)
web_search(query="OpenAI Sora release date", max_results=5)
web_fetch(url="https://www.anthropic.com/research")
```

### 国内领先厂商

| 厂商 | 官方来源 | 关键信息 |
|------|---------|---------|
| **DeepSeek** | `https://www.deepseek.com/`、`https://github.com/deepseek-ai` | DeepSeek 模型、开源代码、技术论文 |
| **豆包** | `https://www.doubao.com/`、`https://www.volcengine.com/` | 豆包产品、火山引擎、企业服务 |
| **智谱 AI** | `https://www.zhipuai.cn/`、`https://github.com/THUDM` | GLM 模型、ChatGLM、开发者平台 |
| **百度** | `https://yiyan.baidu.com/`、`https://cloud.baidu.com/` | 文心一言、百度智能云、行业解决方案 |
| **阿里** | `https://tongyi.aliyun.com/`、`https://www.aliyun.com/` | 通义千问、阿里云、企业服务 |
| **腾讯** | `https://hunyuan.tencent.com/`、`https://cloud.tencent.com/` | 混元大模型、腾讯云、企业服务 |

**快速搜索示例**：
```
web_search(query="DeepSeek V2 开源 性能评测", max_results=5)
web_search(query="豆包大模型 字节跳动 应用场景", max_results=5)
web_search(query="智谱 GLM-4 最新发布 2024", max_results=5)
web_fetch(url="https://www.deepseek.com/")
```

---

## AI 工具产品数据来源

### 文生图工具

| 工具名称 | 官方来源 | 关键信息 |
|---------|---------|---------|
| **Midjourney** | `https://www.midjourney.com/` | 产品更新、Discord 社区、定价信息 |
| **DALL-E** | `https://openai.com/dall-e-3` | OpenAI 整合、API 文档、功能特性 |
| **Stable Diffusion** | `https://stability.ai/`、`https://github.com/Stability-AI` | 开源模型、技术文档、社区生态 |
| **Nano Banana** | 官网（待确认） | 产品功能、定价、用户评价 |
| **豆包生图** | `https://www.doubao.com/` | 与豆包整合、中文优化、使用教程 |

**快速搜索示例**：
```
web_search(query="Midjourney v6 features 2024", max_results=5)
web_search(query="Stable Diffusion 3 vs DALL-E 3 comparison", max_results=5)
web_search(query="豆包生图 功能 使用教程", max_results=5)
web_search(query="Nano Banana AI 生图工具", max_results=5)
```

### 文生 PPT 工具

| 工具名称 | 官方来源 | 关键信息 |
|---------|---------|---------|
| **豆包 PPT** | `https://www.doubao.com/` | 豆包生态整合、功能特性、使用教程 |
| **Gamma** | `https://gamma.app/` | 产品功能、模板库、定价信息 |
| **Beautiful.ai** | `https://www.beautiful.ai/` | 企业模板、协作功能、定价 |
| **Tome** | `https://tome.app/` | 叙事驱动、多模态、团队协作 |

**快速搜索示例**：
```
web_search(query="豆包 PPT 功能 使用教程", max_results=5)
web_search(query="Gamma vs Beautiful.ai vs Tome comparison", max_results=5)
web_fetch(url="https://gamma.app/")
```

### 文生视频工具

| 工具名称 | 官方来源 | 关键信息 |
|---------|---------|---------|
| **即梦** | `https://jimeng.jianying.com/` | 字节跳动产品、功能特性、定价 |
| **可灵** | 快手官网（待确认） | 快手生态、生成能力、应用场景 |
| **Runway** | `https://runwayml.com/` | 专业工具、Gen-2、API 文档 |
| **Pika** | `https://pika.art/` | Pika Labs 产品、功能更新 |
| **Sora** | `https://openai.com/sora` | OpenAI 产品、技术特性、发布时间 |

**快速搜索示例**：
```
web_search(query="即梦 AI 视频生成 功能评测", max_results=5)
web_search(query="可灵 AI 快手 视频生成", max_results=5)
web_search(query="Runway Gen-2 vs Pika comparison", max_results=5)
web_search(query="OpenAI Sora release date features", max_results=5)
```

---

## AI Agent / MCP / Skill / OpenClaw 专项来源

### AI Agent 产品

| 产品/项目 | 官方来源 | 关键信息 |
|----------|---------|---------|
| **Claude (Anthropic)** | `https://www.anthropic.com/` | 产品更新、技术博客、API 文档 |
| **AutoGPT** | `https://github.com/Significant-Gravitas/AutoGPT` | GitHub Stars/Forks/Issues、开发活跃度 |
| **LangChain** | `https://www.langchain.com/` | 产品路线图、应用案例、开发者生态 |
| **CrewAI** | `https://www.crewai.com/` | 功能介绍、用例、社区 |

**快速搜索示例**：
```
web_search(query="AI agent frameworks 2024 comparison", max_results=5)
web_search(query="LangChain vs CrewAI features", max_results=5)
web_fetch(url="https://github.com/Significant-Gravitas/AutoGPT")
```

---

### MCP（模型上下文协议）

| 数据类型 | 来源 | 搜索方法 |
|---------|------|---------|
| **官方规范** | GitHub、官方文档 | `site:github.com "MCP protocol"` |
| **生态工具** | MCP 工具列表 | `MCP servers list`、`MCP integrations` |
| **社区讨论** | Discord、Reddit、HN | `site:reddit.com "MCP protocol"` |

**快速搜索示例**：
```
web_search(query="MCP protocol model context protocol", max_results=5)
web_search(query="MCP servers integrations 2024", max_results=5)
```

---

### Skill 技能系统

| 数据类型 | 来源 | 搜索方法 |
|---------|------|---------|
| **技能市场** | 平台技能商店 | `OpenAI GPT Store`、`Claude Skills` |
| **开发者文档** | 技能开发指南 | `skill development guide`、`custom skills` |
| **技能生态** | 技能排行榜、热门技能 | `top skills 2024`、`skill marketplace` |

---

### OpenClaw 开源项目

| 数据类型 | 来源 | 搜索方法 |
|---------|------|---------|
| **GitHub 项目** | GitHub、Gitee | `site:github.com "OpenClaw"` |
| **社区活跃度** | GitHub Insights | Stars/Forks/Issues/PRs/Contributors |
| **商业应用** | 公司官网、案例 | `OpenClaw commercial use`、`OpenClaw enterprise` |

---

## 数据收集优先级

### P0（必须收集）

- **产品发布**：最近 1 年内的重大版本更新
- **客户案例**：标杆客户案例（至少 5 个）
- **市场活动**：重要市场活动（发布会、峰会）
- **招投标**：近期重大招投标中标信息
- **战略合作**：重要战略合作协议

### P1（重要收集）

- **技术演进**：技术路线图、架构演进
- **生态活动**：生态大会、开发者大会
- **投资并购**：近期投资并购事件
- **行业覆盖**：行业解决方案、行业客户

### P2（可选收集）

- **品牌传播**：品牌营销活动
- **内容营销**：白皮书、行业报告
- **奖项荣誉**：行业奖项、认证
- **组织调整**：高管变动、组织调整

---

## 时间过滤建议

| 数据类型 | 推荐时间范围 | 说明 |
|---------|-------------|------|
| **产品发布** | 近 6 月 | 获取最新产品动态 |
| **市场活动** | 近 3 月 | 获取最新市场动态 |
| **客户案例** | 近 1 年 | 获取最新客户案例 |
| **招投标** | 近 1 年 | 获取近期招投标信息 |
| **战略合作** | 近 1 年 | 获取近期战略合作 |
| **投资并购** | 近 2 年 | 获取近期投资并购 |

---

## 数据质量控制

### 验证原则

1. **多源验证**：关键信息至少从 2 个来源验证
2. **官方优先**：优先使用官方来源（官网、财报、公告）
3. **时效性**：标注数据发布时间，过期数据需重新验证
4. **可信度标注**：
   - **高可信度**：官方公告、财报、政府采购网
   - **中可信度**：行业媒体、分析师报告
   - **低可信度**：社交媒体、非官方报道

---

## 快速搜索模板

### SaaS 厂商综合搜索

```markdown
# 金蝶综合信息搜索
web_search(query="金蝶 最新产品发布 2024", max_results=5)
web_search(query="金蝶 客户案例 标杆客户 2024", max_results=5)
web_search(query="site:ccgp.gov.cn 金蝶 中标 2024", max_results=5)
web_search(query="金蝶 生态大会 合作伙伴 2024", max_results=5)
web_search(query="金蝶 战略合作 投资 并购 2024", max_results=5)
```

### AI Agent 产品搜索

```markdown
# LangChain 产品分析搜索
web_search(query="LangChain latest release 2024", max_results=5)
web_search(query="LangChain vs AutoGPT comparison", max_results=5)
web_fetch(url="https://github.com/langchain-ai/langchain")
web_search(query="LangChain customer case studies", max_results=5)
```

---

## 总结

本文档提供了 AI 技术产品和 SaaS 厂商的全面数据来源指南，涵盖：

- ✅ 产品发布与技术演进
- ✅ 市场活动与品牌建设
- ✅ 客户案例与行业覆盖
- ✅ 招投标与政企市场
- ✅ 生态活动与合作伙伴
- ✅ 战略合作与投资并购

使用本指南可以快速定位关键信息，提高数据收集效率。
