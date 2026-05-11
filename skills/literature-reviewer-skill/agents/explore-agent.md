# Explore Agent 模板

用于在特定学术数据库执行文献检索的Agent。通过浏览器自动化访问数据库检索页面。

---

## Agent 信息

| 属性 | 值 |
|------|-----|
| **名称** | Explore Agent |
| **类型** | Task Agent |
| **用途** | 文献搜索（浏览器自动化） |

---

## 任务描述

在指定的学术数据库中搜索与给定主题相关的文献，返回结构化的文献元数据列表。

**执行方式**：使用 `browser_navigate` 和 `browser_fill_form` 等工具访问数据库网页，提取文献信息。

---

## 输入格式

```yaml
query:
  keywords_zh: ["深度学习", "神经网络"]  # 中文关键词
  keywords_en: ["deep learning", "neural network"]  # 英文关键词
  search_expression_cnki: "SU=('深度学习'+'神经网络')*('医学图像')"
  search_expression_wos: "TS=((deep learning OR neural network) AND medical imaging)"
  
database: "cnki"  # 目标数据库：cnki, wos, sciencedirect, pubmed

filters:
  year_range: [2020, 2025]  # 年份范围
  max_results: 50  # 最大结果数

session_id: "20240115_dl_survey"
```

### 支持的数据库

| 数据库 | 标识符 | 访问方式 |
|--------|--------|----------|
| CNKI 中国知网 | `cnki` | 浏览器自动化 |
| Web of Science | `wos` | 浏览器自动化 |
| ScienceDirect | `sciencedirect` | 浏览器自动化 |
| PubMed | `pubmed` | 浏览器自动化 |

---

## 执行步骤

### Step 1: 访问数据库检索页面

根据目标数据库访问对应的检索页面：

**CNKI**:
```
https://kns.cnki.net/kns8/AdvSearch?classid=YSTT4HG0
```

**Web of Science**:
```
https://www.webofscience.com/wos/woscc/advanced-search
```

**ScienceDirect**:
```
https://www.sciencedirect.com/search
```

**PubMed**:
```
https://pubmed.ncbi.nlm.nih.gov/advanced/
```

### Step 2: 执行检索

1. 在检索页面填充检索式
2. 设置筛选条件（年份、文献类型等）
3. 执行搜索
4. 等待结果加载

### Step 3: 提取文献信息

从搜索结果页面提取以下信息：
- 标题
- 作者
- 期刊/会议名称
- 年份
- 卷期页
- DOI
- 摘要（如有）

**提取示例**（使用 browser_evaluate）：
```javascript
// 提取CNKI搜索结果
const papers = [];
const items = document.querySelectorAll('.result-table-list tbody tr');
items.forEach(item => {
  const title = item.querySelector('.title a')?.textContent?.trim();
  const authors = item.querySelector('.author')?.textContent?.trim().split(';');
  const journal = item.querySelector('.source')?.textContent?.trim();
  const year = item.querySelector('.date')?.textContent?.trim();
  papers.push({ title, authors, journal, year });
});
return papers;
```

### Step 4: 格式化输出

将提取的信息格式化为标准结构：

```json
{
  "id": "C1",
  "source_db": "cnki",
  "title": "文献标题",
  "authors": ["作者1", "作者2"],
  "journal": "期刊名称",
  "year": 2023,
  "volume": "46",
  "issue": "5",
  "pages": "100-110",
  "doi": "10.xxxx",
  "abstract": "摘要内容...",
  "url": "原文链接"
}
```

---

## 输出格式

```json
{
  "agent": "explore",
  "database": "cnki",
  "session_id": "20240115_dl_survey",
  "timestamp": "2024-01-15T10:30:00Z",
  "query": "SU=('深度学习'+'神经网络')*('医学图像')",
  "total_found": 1250,
  "returned": 50,
  "results": [
    {
      "id": "C1",
      "source_db": "cnki",
      "title": "基于深度学习的医学图像诊断研究",
      "authors": ["张三", "李四", "王五"],
      "journal": "计算机学报",
      "year": 2023,
      "volume": "46",
      "issue": "5",
      "pages": "1023-1035",
      "doi": "10.xxxx",
      "abstract": "本文研究了...",
      "url": "https://kns.cnki.net/..."
    }
  ]
}
```

---

## 注意事项

1. **验证码处理**
   - 如遇到验证码，暂停执行
   - 提示用户手动完成验证
   - 验证完成后继续

2. **结果限制**
   - 每数据库最多提取50-100条结果
   - 按相关度或发表时间排序
   - 优先选择近5-10年文献

3. **数据完整性**
   - 尽可能获取完整元数据
   - DOI和摘要为可选，但尽量获取
   - 记录来源URL以便追溯

4. **错误处理**
   - 网络超时：重试3次
   - 页面结构变化：记录错误，尝试备用选择器
   - 访问受限：记录警告，跳过该数据库
