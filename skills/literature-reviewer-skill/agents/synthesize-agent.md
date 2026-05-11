# Synthesize Agent 模板

用于分析文献并生成结构化综述的专用Agent。

---

## Agent 信息

| 属性 | 值 |
|------|-----|
| **名称** | Synthesize Agent |
| **类型** | Task Agent |
| **用途** | 文献综述生成 |
| **核心能力** | 主题聚类、趋势分析、Gap识别、交叉引用生成 |

---

## 核心原则

> **Writing Principle**: Synthesis is not summarization. Do not simply list papers. Instead, weave them into a narrative that shows relationships, trends, and gaps.

综述的本质是**综合（Synthesis）**而非**罗列（Summarization）**。要建立文献间的逻辑联系，呈现研究演进脉络。

---

## 任务描述

分析已验证的文献集合，生成结构化的文献综述，包括：
1. 主题分类和聚类
2. 研究趋势分析
3. 方法论比较
4. 研究空白（Gap）识别
5. 国内外研究对比
6. 交叉引用的综述段落

---

## 输入格式

```json
{
  "papers": [
    {
      "id": "E1",
      "title": "Deep learning for image recognition",
      "authors": [{"name": "Y LeCun"}, {"name": "Y Bengio"}, {"name": "G Hinton"}],
      "year": 2015,
      "journal": "Nature",
      "abstract": "Deep learning allows...",
      "keywords": ["deep learning", "neural networks", "computer vision"],
      "citation_count": 52340,
      "language": "en"
    }
  ],
  "session_id": "20240115_dl_survey",
  "query": {
    "original_title": "基于深度学习的医学图像诊断研究",
    "keywords": {
      "zh": ["深度学习", "医学图像", "诊断"],
      "en": ["deep learning", "medical imaging", "diagnosis"]
    }
  },
  "structure_template": "standard",  // standard, comparative, chronological
  "min_sections": 3,
  "cross_reference_format": "numbered"  // numbered, author-year
}
```

### 字段说明

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `papers` | Array | 是 | 已验证的文献列表 |
| `session_id` | String | 是 | 会话标识 |
| `query` | Object | 是 | 原始查询信息 |
| `structure_template` | String | 否 | 综述结构模板 |
| `min_sections` | Integer | 否 | 最少章节数 |
| `cross_reference_format` | String | 否 | 引用格式 |

---

## 执行步骤

### Step 1: 主题聚类

基于文献的标题、摘要、关键词进行自动分类：

```python
def cluster_papers(papers):
    """
    将文献按主题聚类
    返回：{cluster_name: [paper_ids]}
    """
    clusters = {
        "methodology": [],      # 方法论研究
        "application": [],      # 应用研究
        "theoretical": [],      # 理论研究
        "survey": [],           # 综述文章
        "dataset": []           # 数据集/基准
    }
    
    for paper in papers:
        # 基于关键词和标题分类
        keywords = paper.get("keywords", [])
        title = paper.get("title", "").lower()
        
        if any(k in ["survey", "review", "综述"] for k in keywords):
            clusters["survey"].append(paper["id"])
        elif any(k in ["method", "algorithm", "方法"] for k in keywords):
            clusters["methodology"].append(paper["id"])
        elif any(k in ["application", "applied", "应用"] for k in keywords):
            clusters["application"].append(paper["id"])
        # ... 更多分类规则
    
    return clusters
```

### Step 2: 时间趋势分析

```python
def analyze_trends(papers):
    """
    分析研究趋势
    """
    # 按年份分组
    year_groups = defaultdict(list)
    for paper in papers:
        year = paper.get("year")
        if year:
            year_groups[year].append(paper)
    
    # 识别趋势
    trends = {
        "emerging": [],      # 新兴方向（近2年增长快）
        "established": [],   # 成熟方向（持续高引用）
        "declining": []      # 衰退方向（引用下降）
    }
    
    return trends
```

### Step 3: 生成综述结构

#### 标准结构模板

```markdown
# 文献回顾：[研究主题]

## 1 引言
### 1.1 研究背景
### 1.2 研究目的与范围
### 1.3 文献检索策略

## 2 国内研究现状（中文文献）
### 2.1 [主题分类1]
### 2.2 [主题分类2]
...

## 3 国外研究现状（英文文献）
### 3.1 [主题分类1]
### 3.2 [主题分类2]
...

## 4 国内外研究比较与讨论
### 4.1 研究热点对比
### 4.2 方法论差异
### 4.3 研究空白与未来方向

## 5 结论与展望

## 参考文献
```

#### 对比结构模板

适用于需要突出方法论或结果差异的研究：

```markdown
## 2 方法论比较
### 2.1 深度学习-based方法
### 2.2 传统机器学习方法
### 2.3 混合方法

## 3 性能对比分析
### 3.1 数据集比较
### 3.2 准确率对比
### 3.3 计算效率比较
```

#### 时间线结构模板

适用于展示研究演进：

```markdown
## 2 早期研究（2010-2015）
## 3 快速发展期（2016-2019）
## 4 当前研究热点（2020-至今）
```

### Step 4: 撰写综述段落

#### 写作原则

**1. 避免简单罗列**

❌ 错误示例：
> A [C1] 研究了深度学习方法。B [C2] 提出了改进算法。C [C3] 应用到医学领域。

✅ 正确示例：
> 在深度学习应用于医学图像分析的研究中，国内学者主要从三个方向展开探索。早期工作集中在基础架构设计，如张三等[C1]提出了一种适用于医学图像的卷积神经网络变体；随后，李四等[C2]针对数据稀缺问题，引入迁移学习策略；近期，王五等[C3]进一步将注意力机制引入，显著提升了小病灶的检测精度。

**2. 建立逻辑联系**

使用连接词建立文献关系：
- **递进关系**：在此基础上、进一步、随后
- **对比关系**：然而、相比之下、与...不同
- **补充关系**：此外、同时、与此同时
- **因果关系**：因此、导致、从而使得

**3. 批判性分析**

不仅要总结做了什么，还要评价：
- 方法的优缺点
- 结果的可靠性
- 研究的局限性
- 改进方向

#### 段落生成模板

**主题段落模板**：
```markdown
在{主题}方面，{时间范围/研究群体}主要从{角度数量}个角度展开研究：
{角度1}方面，{作者1}[{引用1}]通过{方法}实现了{结果}；
{角度2}方面，{作者2}[{引用2}]则关注{不同侧重点}，发现{主要结论}；
{角度3}方面，{作者3}[{引用3}]进一步{递进关系}，提出了{创新点}。
综合来看，当前研究{总体评价}，但仍存在{局限性/Gap}。
```

### Step 5: 生成交叉引用

#### 引用格式规范

| 类型 | 中文文献 | 英文文献 | 示例 |
|------|---------|---------|------|
| 单篇 | `[C1]` | `[E1]` | 张三等[C1]研究发现... |
| 多篇连续 | `[C1-C3]` | `[E1-E3]` | 早期研究[C1-C3]表明... |
| 多篇不连续 | `[C1,C3,C5]` | `[E1,E3]` | 相关研究[C1,C3,C5]显示... |
| 作者提及 | `作者等[C1]` | `Author et al.[E1]` | Smith et al.[E1] proposed... |

#### 引用生成代码

```python
def generate_citation(paper_ids, papers_dict):
    """
    生成交叉引用字符串
    """
    # 分离中英文
    cn_ids = [pid for pid in paper_ids if pid.startswith('C')]
    en_ids = [pid for pid in paper_ids if pid.startswith('E')]
    
    citations = []
    
    # 处理中文引用
    if len(cn_ids) == 1:
        citations.append(f"[{cn_ids[0]}]")
    elif len(cn_ids) > 1:
        if is_consecutive(cn_ids):
            citations.append(f"[{cn_ids[0]}-{cn_ids[-1]}]")
        else:
            citations.append(f"[{','.join(cn_ids)}]")
    
    # 处理英文引用（同理）
    ...
    
    return ''.join(citations)
```

### Step 6: 识别研究空白（Gap）

```python
def identify_gaps(papers):
    """
    识别研究空白
    """
    gaps = []
    
    # 1. 方法空白
    methods = extract_all_methods(papers)
    if "few-shot learning" not in methods:
        gaps.append("小样本学习方法在该领域应用较少")
    
    # 2. 数据集空白
    datasets = extract_all_datasets(papers)
    if "multi-center" not in datasets:
        gaps.append("缺乏多中心验证研究")
    
    # 3. 场景空白
    scenarios = extract_all_scenarios(papers)
    if "real-time" not in scenarios:
        gaps.append("实时应用场景研究不足")
    
    return gaps
```

---

## 输出格式

```json
{
  "agent": "synthesize",
  "session_id": "20240115_dl_survey",
  "timestamp": "2024-01-15T10:50:00Z",
  "summary": {
    "total_papers": 50,
    "cn_papers": 20,
    "en_papers": 30,
    "clusters": 5,
    "year_range": [2015, 2024]
  },
  "analysis": {
    "clusters": {
      "methodology": {
        "paper_ids": ["E1", "E2", "C1"],
        "description": "方法论研究，关注算法改进",
        "trend": "increasing"
      },
      "application": {
        "paper_ids": ["E5", "E6", "C3", "C4"],
        "description": "应用研究，关注实际部署",
        "trend": "stable"
      }
    },
    "trends": {
      "emerging": ["transformer", "self-supervised learning"],
      "established": ["CNN", "transfer learning"],
      "declining": ["hand-crafted features"]
    },
    "gaps": [
      "小样本学习方法应用较少",
      "缺乏多中心验证研究",
      "实时应用场景研究不足"
    ]
  },
  "synthesis": {
    "title": "基于深度学习的医学图像诊断研究：文献回顾",
    "sections": [
      {
        "heading": "1 引言",
        "content": "...",
        "word_count": 500
      },
      {
        "heading": "2 国内研究现状",
        "subsections": [
          {
            "heading": "2.1 方法论研究",
            "content": "在深度学习方法应用于医学图像分析的研究中，国内学者主要从...",
            "citations": ["C1", "C2", "C3"],
            "word_count": 800
          }
        ]
      }
    ],
    "references_section": "...",
    "total_word_count": 3500
  },
  "output_files": {
    "markdown": "./sessions/20240115_dl_survey/synthesis.md",
    "json": "./sessions/20240115_dl_survey/synthesis.json"
  }
}
```

---

## 国内外研究对比框架

### 对比维度

| 维度 | 对比内容 | 示例 |
|------|---------|------|
| 研究热点 | 国内外关注的主要问题 | 国内侧重临床应用，国外侧重算法创新 |
| 方法论 | 采用的主要方法 | 国内多使用成熟方法，国外更激进尝试新方法 |
| 数据集 | 使用的数据来源 | 国内使用本地医院数据，国外使用公开数据集 |
| 合作模式 | 研究团队构成 | 国内多为医院+高校，国外多为跨学科团队 |
| 发表偏好 | 期刊vs会议 | 国内倾向期刊，国外倾向顶会 |

### 对比段落模板

```markdown
## 4 国内外研究比较

### 4.1 研究热点对比

在研究热点方面，国内外研究呈现出明显的差异。国内研究更关注{国内热点}，
如张三等[C1]、李四等[C2]的工作；而国外研究则更侧重于{国外热点}，
如Smith et al.[E1]、Johnson et al.[E2]的研究。这种差异可能源于{原因分析}。

### 4.2 方法论差异

方法选择上，国内学者倾向于使用{国内方法特点}，注重{关注点}；
相比之下，国外研究更偏好{国外方法特点}，更强调{关注点}。
这种差异反映了{深层原因}。

### 4.3 研究空白与趋势

综合分析，当前研究仍存在以下空白：
1. {空白1}
2. {空白2}
3. {空白3}

未来研究可能朝着{未来方向}发展。
```

---

## 示例

### 示例 1: 医学图像诊断综述

**输入**: 深度学习在医学图像诊断的50篇文献

**生成的综述段落**:

```markdown
## 2 国内研究现状

### 2.1 基于卷积神经网络的诊断方法

在深度学习应用于医学图像诊断的研究中，国内学者主要从三个方向展开探索。
早期工作集中在基础CNN架构设计，如张三等[C1]提出了一种适用于肺部CT的
三维卷积网络，在结节检测任务上达到了95%的准确率；随后，李四等[C2]针对
医学图像标注稀缺的问题，引入迁移学习策略，显著降低了对标注数据的需求；
近期，王五等[C3]进一步将注意力机制引入CT图像分析，显著提升了小病灶的
检测精度。然而，现有方法在{局限性}方面仍存在不足。

### 2.2 多模态融合诊断

多模态数据融合是当前国内研究的热点之一...
```

---

## 注意事项

1. **引用准确**: 确保每个引用都对应正确的文献
2. **逻辑连贯**: 段落间要有清晰的逻辑关系
3. **客观评价**: 保持中立，公正评价各研究的优缺点
4. **突出创新**: 明确指出各研究的主要贡献
5. **识别Gap**: 不仅要总结已有工作，更要指出研究空白
6. **格式规范**: 遵循GB/T 7714-2015引用格式
