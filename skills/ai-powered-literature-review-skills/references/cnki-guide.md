# CNKI 文献检索指南

本文档提供 CNKI（中国知网）高级检索的详细操作指南，支持 Claude Code 自动化检索。

---

## 高级检索页面

**URL**: `https://kns.cnki.net/kns/AdvSearch?classid=7NS01R8M`

---

## 字段类型代码

| 代码 | 含义 | 使用场景 |
|------|------|---------|
| SU | 主题 | 广泛检索（推荐） |
| TI | 篇名 | 精确匹配标题 |
| KY | 关键词 | 主题相关 |
| TKA | 篇关摘 | 篇名+关键词+摘要（最全面） |
| AB | 摘要 | 摘要内容检索 |
| AU | 作者 | 查找特定作者 |
| JN | 期刊 | 限定期刊范围 |
| RF | 参考文献 | 引用检索 |
| YE | 年 | 特定年份 |

---

## 来源类别

| 代码 | 含义 | 说明 |
|------|------|------|
| CSSCI | 中文社会科学引文索引 | 人文社科权威 |
| hx | 北大核心期刊 | 各学科核心期刊 |
| CSCD | 中国科学引文数据库 | 自然科学权威 |
| SCI | SCI 来源期刊 | 国际期刊 |
| EI | EI 来源期刊 | 工程索引 |

---

## 检索策略示例

### 示例 1：单一主题检索

```javascript
const query = "深度学习";
const fieldType = "SU";  // 主题
const sourceTypes = ["CSSCI", "hx"];  // CSSCI + 北大核心
const startYear = "2020";
const endYear = "2025";
```

### 示例 2：多关键词组合（AND）

```javascript
const query = "深度学习";
const fieldType = "SU";
const query2 = "图像识别";
const fieldType2 = "SU";
const rowLogic = "AND";
const sourceTypes = ["CSSCI", "hx"];
```

### 示例 3：多关键词组合（OR）

```javascript
const query = "人工智能";
const fieldType = "SU";
const query2 = "机器学习";
const fieldType2 = "SU";
const rowLogic = "OR";
```

---

## 执行检索的 JavaScript 代码

以下代码用于在 CNKI 高级检索页面执行自动化检索：

```javascript
async () => {
  const query = "KEYWORDS";
  const fieldType = "SU";
  const query2 = "";
  const fieldType2 = "KY";
  const rowLogic = "AND";
  const sourceTypes = ["CSSCI", "hx"];
  const startYear = "2020";
  const endYear = "2025";
  const author = "";
  const journal = "";

  // 等待页面加载
  await new Promise((r, j) => {
    let n = 0;
    const c = () => { 
      if (document.querySelector('#txt_1_value1')) r(); 
      else if (n++ > 30) j('timeout'); 
      else setTimeout(c, 500); 
    };
    c();
  });

  // 检查验证码
  const cap = document.querySelector('#tcaptcha_transform_dy');
  if (cap && cap.getBoundingClientRect().top >= 0) return { error: 'captcha' };

  // 获取所有可见的 select 元素
  const selects = Array.from(document.querySelectorAll('select')).filter(s => s.offsetParent !== null);

  // 设置来源类别
  if (sourceTypes.length > 0) {
    const gjAll = document.querySelector('#gjAll');
    if (gjAll && gjAll.checked) gjAll.click();
    for (const st of sourceTypes) {
      const cb = document.querySelector('#' + st);
      if (cb && !cb.checked) cb.click();
    }
  }

  // 设置第一个查询
  selects[0].value = fieldType;
  selects[0].dispatchEvent(new Event('change', { bubbles: true }));
  const input = document.querySelector('#txt_1_value1');
  input.value = query;
  input.dispatchEvent(new Event('input', { bubbles: true }));

  // 设置第二个查询（如果有）
  if (query2) {
    selects[5].value = rowLogic;
    selects[5].dispatchEvent(new Event('change', { bubbles: true }));
    selects[6].value = fieldType2;
    selects[6].dispatchEvent(new Event('change', { bubbles: true }));
    const input2 = document.querySelector('#txt_2_value1');
    input2.value = query2;
    input2.dispatchEvent(new Event('input', { bubbles: true }));
  }

  // 设置作者
  if (author) {
    const auInput = document.querySelector('#au_1_value1');
    if (auInput) { 
      auInput.value = author; 
      auInput.dispatchEvent(new Event('input', { bubbles: true })); 
    }
  }

  // 设置期刊
  if (journal) {
    const magInput = document.querySelector('#magazine_value1');
    if (magInput) { 
      magInput.value = journal; 
      magInput.dispatchEvent(new Event('input', { bubbles: true })); 
    }
  }

  // 设置年份范围
  if (startYear) { 
    selects[14].value = startYear; 
    selects[14].dispatchEvent(new Event('change', { bubbles: true })); 
  }
  if (endYear) { 
    selects[15].value = endYear; 
    selects[15].dispatchEvent(new Event('change', { bubbles: true })); 
  }

  // 点击搜索按钮
  document.querySelector('div.search')?.click();

  // 等待结果加载
  await new Promise((r, j) => {
    let n = 0;
    const c = () => {
      if (document.body.innerText.includes('条结果')) r();
      else if (n++ > 40) j('timeout');
      else setTimeout(c, 500);
    };
    setTimeout(c, 2000);
  });

  // 再次检查验证码
  const cap2 = document.querySelector('#tcaptcha_transform_dy');
  if (cap2 && cap2.getBoundingClientRect().top >= 0) return { error: 'captcha' };

  // 提取结果
  const rows = document.querySelectorAll('.result-table-list tbody tr');
  const checkboxes = document.querySelectorAll('.result-table-list tbody input.cbItem');
  const results = Array.from(rows).map((row, i) => {
    const titleLink = row.querySelector('td.name a.fz14');
    const authors = Array.from(row.querySelectorAll('td.author a.KnowledgeNetLink') || []).map(a => a.innerText?.trim());
    const journal = row.querySelector('td.source a')?.innerText?.trim() || '';
    const date = row.querySelector('td.date')?.innerText?.trim() || '';
    const citations = row.querySelector('td.quote')?.innerText?.trim() || '';
    return {
      n: i + 1,
      title: titleLink?.innerText?.trim() || '',
      href: titleLink?.href || '',
      exportId: checkboxes[i]?.value || '',
      authors: authors.join('; '),
      journal,
      date,
      citations
    };
  });

  return {
    query, fieldType, query2, fieldType2, rowLogic,
    sourceTypes, startYear, endYear, author, journal,
    total: document.querySelector('.pagerTitleCell')?.innerText?.match(/([\d,]+)/)?.[1] || '0',
    page: document.querySelector('.countPageMark')?.innerText || '1/1',
    results
  };
}
```

---

## 结果提取选择器

| 元素 | 选择器 | 说明 |
|------|--------|------|
| 标题 | `td.name a.fz14` | 文献标题链接 |
| 作者 | `td.author a.KnowledgeNetLink` | 作者列表 |
| 期刊 | `td.source a` | 期刊名称 |
| 日期 | `td.date` | 发表日期 |
| 被引次数 | `td.quote` | 被引用次数 |
| 下载次数 | `td.download` | 下载次数 |
| 复选框 | `input.cbItem` | 用于批量导出 |

---

## 验证码处理

CNKI 在频繁访问时会触发腾讯云滑块验证码。

### 检测验证码

```javascript
const cap = document.querySelector('#tcaptcha_transform_dy');
if (cap && cap.getBoundingClientRect().top >= 0) {
  return { error: 'captcha', message: '请手动完成验证码' };
}
```

### 处理流程

1. **检测**：执行脚本前检查验证码元素
2. **暂停**：如果发现验证码，暂停自动化流程
3. **提示**：通知用户手动完成验证码
4. **继续**：用户确认后继续执行

### 规避策略

- 降低检索频率
- 使用较长的间隔时间
- 避免短时间内大量请求

---

## 期刊影响因子查询

### 查询页面

CNKI 提供期刊影响因子查询功能：

**URL**: `https://navi.cnki.net/knavi/journals/index`

### 影响因子类型

| 类型 | 说明 |
|------|------|
| 复合影响因子 | 综合考虑期刊被引用情况 |
| 综合影响因子 | 基础研究类期刊指标 |

### JavaScript 查询代码

```javascript
// 在期刊导航页面查询影响因子
async function getJournalMetrics(journalName) {
  // 搜索期刊
  const searchInput = document.querySelector('#search_journals');
  searchInput.value = journalName;
  searchInput.dispatchEvent(new Event('input', { bubbles: true }));
  
  // 点击搜索
  document.querySelector('.search-btn')?.click();
  
  // 等待结果
  await new Promise(r => setTimeout(r, 2000));
  
  // 提取影响因子
  const impactFactor = document.querySelector('.impact-factor')?.innerText;
  const quartile = document.querySelector('.quartile')?.innerText;
  
  return { impactFactor, quartile };
}
```

---

## Zotero 导出

### 方法一：使用 CNKI 导出功能

1. 在搜索结果页勾选需要导出的文献
2. 点击 "导出/参考文献"
3. 选择 "Zotero"
4. 复制导出的文本
5. 在 Zotero 中通过 "从剪贴板导入"

### 方法二：使用 Zotero Connector

1. 安装 Zotero Connector 浏览器插件
2. 在 CNKI 文献详情页
3. 点击 Zotero 图标保存文献

### 方法三：批量导入（通过 DOI）

```python
# 提取 CNKI 文献的 DOI，使用 Zotero 的 DOI 导入功能
import pyperclip

 dois = [paper['doi'] for paper in papers if paper.get('doi')]
pyperclip.copy('\n'.join(dois))
# 然后在 Zotero 中：文件 → 通过标识符添加条目
```

---

## 批量下载策略

### 限制说明

- CNKI 对批量下载有限制
- 需要登录账号
- 部分文献需要购买权限

### 批量下载代码

```javascript
// 批量下载前50篇文献的PDF
async function batchDownload(results) {
  for (let i = 0; i < Math.min(results.length, 50); i++) {
    const result = results[i];
    
    // 打开详情页
    window.open(result.href, '_blank');
    
    // 等待下载按钮可点击
    await new Promise(r => setTimeout(r, 3000));
    
    // 点击下载（需要在详情页执行）
    document.querySelector('.btn-download')?.click();
    
    // 间隔5秒，避免触发限制
    await new Promise(r => setTimeout(r, 5000));
  }
}
```

### 分批导出建议

- 每批最多 50 篇
- 批次间隔 10-30 秒
- 使用 CAJ 格式（通常更小）

---

## 常见问题

### Q: 检索结果为空？

A: 检查：
- 关键词是否正确
- 字段选择是否合适
- 年份范围是否合理
- 来源类别是否冲突

### Q: 验证码频繁出现？

A: 建议：
- 降低检索频率
- 使用更长的等待间隔
- 分时段进行检索

### Q: 无法下载PDF？

A: 可能原因：
- 未登录账号
- 无下载权限
- 文献为 CAJ 格式
- 浏览器设置问题

---

## 参考链接

- CNKI 高级检索: https://kns.cnki.net/kns/AdvSearch
- CNKI 期刊导航: https://navi.cnki.net
- CNKI 帮助中心: https://www.cnki.net/gycnki/gycnki.htm
