# 分析模型索引

本目录包含所有分析模型的独立文件，按需加载以节省 Token。

---

## 模型列表

### 战略与环境分析（5个）

| 模型名称 | 文件路径 | 适用场景 |
|---------|---------|---------|
| SWOT 分析 | `strategic/swot.md` | 品牌评估、竞争定位、战略规划 |
| PESTEL 分析 | `strategic/pestel.md` | 宏观环境扫描、市场进入评估 |
| 波特五力模型 | `strategic/porter-five-forces.md` | 行业竞争格局、进入壁垒评估 |
| VRIO 分析 | `strategic/vrio.md` | 核心能力评估、资源优势分析 |
| 波特钻石模型 | `strategic/porter-diamond.md` | 国家/区域竞争优势分析 |

### 市场与增长分析（6个）

| 模型名称 | 文件路径 | 适用场景 |
|---------|---------|---------|
| STP 分析 | `market/stp.md` | 市场细分、目标市场选择、品牌定位 |
| BCG 矩阵 | `market/bcg-matrix.md` | 产品组合管理、资源配置决策 |
| 安索夫矩阵 | `market/ansoff-matrix.md` | 增长战略选择 |
| TAM-SAM-SOM | `market/tam-sam-som.md` | 市场规模测算、机会量化 |
| 产品生命周期 (PLC) | `market/product-lifecycle.md` | 产品战略制定、市场节奏判断 |
| 技术采用生命周期 | `market/technology-adoption.md` | 新兴技术/品类渗透分析 |

### 竞争与战略定位分析（6个）

| 模型名称 | 文件路径 | 适用场景 |
|---------|---------|---------|
| 商业模式画布 | `competitive/business-model-canvas.md` | 商业模式设计、竞争分析、企业诊断 |
| 竞品对比矩阵 | `competitive/competitor-matrix.md` | 竞争分析、产品定位、战略规划 |
| 价值链分析 | `competitive/value-chain.md` | 成本优势来源、差异化机会识别 |
| 蓝海战略 | `competitive/blue-ocean.md` | 差异化创新、新市场空间开拓 |
| 战略群组图 | `competitive/strategic-groups.md` | 竞争格局可视化、市场空白识别 |
| Benchmarking | `competitive/benchmarking.md` | 竞品差距分析、最佳实践识别 |

### 消费者与行为分析（5个）

| 模型名称 | 文件路径 | 适用场景 |
|---------|---------|---------|
| 消费者决策旅程 | `consumer/decision-journey.md` | 消费者行为路径、触点优化 |
| AARRR 漏斗 | `consumer/aarrr-funnel.md` | 用户增长分析、转化优化 |
| RFM 模型 | `consumer/rfm-model.md` | 客户价值分层、精准营销 |
| JTBD | `consumer/jtbd.md` | 需求洞察、产品创新方向 |
| 马斯洛需求层次 | `consumer/maslow-hierarchy.md` | 消费心理分析、产品价值主张 |

### 财务与估值分析（4个）

| 模型名称 | 文件路径 | 适用场景 |
|---------|---------|---------|
| 杜邦分析 | `financial/dupont-analysis.md` | 盈利能力拆解、财务健康诊断 |
| DCF 估值 | `financial/dcf-valuation.md` | 企业/项目估值 |
| 可比公司分析 | `financial/comparable-analysis.md` | 相对估值、同行基准分析 |
| EVA | `financial/eva.md` | 价值创造能力评估 |

### 行业与供应链分析（3个）

| 模型名称 | 文件路径 | 适用场景 |
|---------|---------|---------|
| 行业价值链 | `industry/industry-value-chain.md` | 行业结构理解、利润分配分析 |
| Gartner 技术成熟度曲线 | `industry/gartner-hype-cycle.md` | 新兴技术成熟度评估 |
| GE-麦肯锡矩阵 | `industry/ge-mckinsey-matrix.md` | 业务组合排序、投资决策 |

---

## 模型总览

| 分类 | 数量 | 目录 |
|------|------|------|
| 战略与环境分析 | 5 | `strategic/` |
| 市场与增长分析 | 6 | `market/` |
| 竞争与战略定位分析 | 6 | `competitive/` |
| 消费者与行为分析 | 5 | `consumer/` |
| 财务与估值分析 | 4 | `financial/` |
| 行业与供应链分析 | 3 | `industry/` |
| **总计** | **29** | - |

---

## 框架组合建议

### 按研究领域组合

| 研究领域 | 推荐模型组合 |
|---------|-------------|
| **行业分析** | PESTEL + 波特五力 + 行业价值链 |
| **企业竞争分析** | 商业模式画布 + 竞品矩阵 + SWOT |
| **产品竞争分析** | 竞品矩阵 + 商业模式画布 + SWOT |
| **市场进入分析** | PESTEL + 波特五力 + TAM-SAM-SOM |
| **品牌战略分析** | SWOT + 蓝海战略 + STP |
| **消费者洞察** | RFM + 决策旅程 + JTBD |
| **投资尽调** | 波特五力 + 杜邦分析 + DCF |

---

## 使用方式

### 1. 根据主题推断领域

```markdown
# 阶段 0：推断分析领域
根据主题关键词加载对应的领域文档：
- 行业分析 → domains/industry-analysis.md
- 企业分析 → domains/company-analysis.md
- 产品分析 → domains/product-analysis.md
```

### 2. 根据领域选择模型

```markdown
# 阶段 1：选择分析模型
从 domains 文档中读取推荐模型组合，然后按需加载：
- 只加载实际使用的模型文件
- 不加载未使用的模型文件
- 每次研究最多使用 2-4 个模型
```

### 3. Token 节省策略

| 策略 | 说明 |
|------|------|
| **按需加载** | 只加载实际使用的模型文件 |
| **领域优先** | 先加载领域文档，再根据推荐加载模型 |
| **最大 4 个模型** | 每次研究最多使用 4 个模型，避免堆砌 |

---

## 单个模型 Token 估算

| 模型类型 | 平均行数 | Token 估算 |
|---------|---------|-----------|
| 所有模型 | ~60-80 行 | ~500-700 tokens |
| 加载 3 个模型 | ~200 行 | ~1,500-2,000 tokens |
| 加载 4 个模型 | ~280 行 | ~2,000-2,800 tokens |

**对比原文件**：
- 原 `analysis-frameworks.md`：709 行 ≈ ~18,000 tokens
- 按需加载 3 个模型：~1,700 tokens
- **节省约 90%**

---

## 更新记录

- **v1.0.0** (2026-03-18): 初始版本，创建 29 个独立模型文件
