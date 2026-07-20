# 深度研究方法论

## 概述

当需要深度背景研究、学术研究或复杂主题全面分析时，采用深度研究方法。

---

## 适用场景

- 学术研究或论文写作
- 复杂主题的全面分析
- 需要多源验证的关键数据
- 新兴领域或技术的研究
- 竞争情报深度调查

---

## 工作流程

### Step 1：规划研究问题

将研究主题拆解为 3-5 个子问题：

```
主题: "AI 对医疗行业的影响"
├── 子问题1: AI 在医疗领域的主要应用是什么？
├── 子问题2: 有哪些临床结果已被验证？
├── 子问题3: 监管挑战有哪些？
├── 子问题4: 哪些公司处于领先地位？
└── 子问题5: 市场规模和增长轨迹如何？
```

**拆解原则**：
- 每个子问题应该是独立可回答的
- 子问题之间应该有逻辑关联
- 所有子问题回答完后应该能完整回答主问题

---

### Step 2：执行多源搜索

为每个子问题生成 2-3 个搜索查询，使用不同的关键词变体：

```markdown
# 子问题1：AI 在医疗领域的应用
web_fetch(url="https://www.google.com/search?q=AI+applications+healthcare+2024")
web_fetch(url="https://www.google.com/search?q=artificial+intelligence+medical+use+cases")
web_fetch(url="https://www.baidu.com/s?wd=人工智能+医疗应用+2024")

# 子问题2：临床结果
web_fetch(url="https://www.google.com/search?q=AI+healthcare+clinical+outcomes+study")
web_fetch(url="https://www.google.com/search?q=filetype:pdf+AI+medical+clinical+trial")

# ... 继续其他子问题
```

**搜索策略**：
- 每个子问题使用 2-3 个不同的关键词变体
- 混合使用网页搜索和新闻搜索
- 目标：15-30 个独特来源
- 优先级：学术、官方、可信新闻 > 博客 > 论坛

---

### Step 3：深度阅读关键来源

对于最有价值的 URL，使用 `web_fetch` 获取完整内容：

```markdown
# 获取完整网页内容
web_fetch(url="https://example.com/detailed-report")
```

**策略**：
- 深度阅读 3-5 个关键来源
- 不要只依赖搜索摘要
- 寻找数据、图表、原始引用

---

### Step 4：整合与交叉验证

对收集的信息进行：

#### 交叉验证

如果只有一个来源提到某个观点，标记为"未验证"。

**验证标准**：
- **高可信度**：3+ 个独立来源验证
- **中可信度**：2 个独立来源验证
- **低可信度**：1 个来源，需标注"未验证"

#### 时效性检查

优先过去 12 个月的来源。

| 数据类型 | 可接受的时间范围 |
|---------|------------------|
| 市场规模 | 最近 1-3 年 |
| 增长趋势 | 最近 3-5 年 |
| 政策法规 | 最近 6 个月 |
| 新闻热点 | 最近 1 周 |

#### 可信度评估

标注来源类型：

| 来源类型 | 可信度等级 |
|---------|-----------|
| 学术期刊（peer-reviewed） | 最高 |
| 政府统计、官方报告 | 高 |
| 上市公司财报 | 高 |
| 行业报告（咨询公司） | 中高 |
| 主流新闻媒体 | 中 |
| 专业博客 | 中低 |
| 个人博客、论坛 | 低 |

---

## 深度研究示例

### 示例：AI 在医疗领域的应用研究

#### Step 1：规划研究问题

```
主题: "AI 在医疗领域的应用现状与发展趋势"
├── 子问题1: AI 在医疗领域的主要应用场景有哪些？
├── 子问题2: 这些应用的成熟度如何？
├── 子问题3: 有哪些临床验证的成功案例？
└── 子问题4: 面临的主要挑战是什么？
```

#### Step 2：执行多源搜索

```markdown
# 子问题1：主要应用场景
web_fetch(url="https://www.google.com/search?q=AI+healthcare+applications+2024")
web_fetch(url="https://www.google.com/search?q=artificial+intelligence+medical+diagnosis")
web_fetch(url="https://www.baidu.com/s?wd=人工智能+医疗应用场景")

# 子问题2：应用成熟度
web_fetch(url="https://www.google.com/search?q=AI+healthcare+maturity+adoption+rate")
web_fetch(url="https://www.google.com/search?q=AI+medical+FDA+approval+list")

# 子问题3：临床验证案例
web_fetch(url="https://www.google.com/search?q=AI+healthcare+clinical+validation+study")
web_fetch(url="https://www.google.com/search?q=filetype:pdf+AI+medical+clinical+trial")

# 子问题4：主要挑战
web_fetch(url="https://www.google.com/search?q=AI+healthcare+challenges+regulation")
web_fetch(url="https://www.google.com/search?q=AI+medical+ethics+privacy+concerns")
```

#### Step 3：深度阅读关键来源

```markdown
# 深度阅读 3-5 个关键报告
web_fetch(url="https://www.example.com/ai-healthcare-report-2024")
web_fetch(url="https://www.example.com/clinical-validation-study")
web_fetch(url="https://www.example.com/regulatory-guidelines")
```

#### Step 4：整合与验证

```json
{
  "findings": {
    "application_scenes": {
      "diagnosis_imaging": {
        "maturity": "成熟应用",
        "clinical_validation": "3+ 研究",
        "sources": ["来源1", "来源2", "来源3"],
        "confidence": "high"
      },
      "drug_discovery": {
        "maturity": "早期阶段",
        "clinical_validation": "1 研究",
        "sources": ["来源1"],
        "confidence": "low"
      }
    }
  }
}
```

---

## 研究输出格式

### 研究摘要

```markdown
# [研究主题] 深度研究报告

## 研究概述
- 研究主题
- 子问题列表
- 研究方法

## 主要发现

### 子问题1：[标题]
- **核心发现**：...
- **支持证据**：
  - 证据1（来源A, 来源B）
  - 证据2（来源C）
- **可信度**：high/medium/low

### 子问题2：[标题]
...

## 来源评估
- 总来源数：XX
- 高可信度来源：XX
- 验证通过的关键发现：XX

## 研究局限
- 数据缺口
- 验证不足的发现
```

---

## 最佳实践

### 1. 避免单一来源依赖

**错误做法**：
- 只依赖一个来源得出结论
- 未验证就引用

**正确做法**：
- 每个关键发现至少 2 个来源
- 标注来源可信度
- 未验证的发现明确标注

### 2. 及时更新信息

**错误做法**：
- 使用 5 年前的数据
- 忽略最新发展

**正确做法**：
- 优先过去 12 个月的信息
- 标注信息时间范围
- 必要时更新研究

### 3. 保持客观中立

**错误做法**：
- 只搜索支持自己观点的信息
- 忽略反面证据

**正确做法**：
- 全面搜索
- 包含不同观点
- 客观呈现争议

### 4. 记录研究过程

**错误做法**：
- 不记录搜索关键词
- 不保存来源 URL

**正确做法**：
- 记录所有搜索查询
- 保存所有来源 URL
- 方便后续验证和更新
