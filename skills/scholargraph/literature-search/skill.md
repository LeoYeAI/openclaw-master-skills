# Literature Search Skill

## Overview

文献检索引擎，提供多源学术文献搜索与聚合能力。支持arXiv、Semantic Scholar、以及通用网络搜索，帮助用户快速找到相关领域的高质量文献资源。

## Core Capabilities

### 1. 查询扩展 (Query Expansion) ⭐ 新功能
- **智能理解**: 分析模糊的研究兴趣，识别核心主题
- **关键词生成**: 生成核心词、同义词、缩写、相关术语、应用领域
- **交互式对话**: 通过多轮对话逐步明确研究方向
- **结构化输出**: 提供确认信息、关键词列表、追问建议

### 2. 多源检索
- **arXiv**: 预印本论文检索，获取最新研究动态
- **Semantic Scholar**: 学术搜索，获取引用关系和论文质量指标
- **OpenAlex**: 250M+ 开放学术数据，全面覆盖
- **PubMed**: 生物医学文献数据库
- **CrossRef**: DOI 元数据检索
- **DBLP**: 计算机科学文献
- **CORE**: 开放获取全文（需 API Key）
- **IEEE Xplore**: 工程技术文献（需 API Key）
- **Google Scholar**: 通过 SerpAPI（需 API Key）
- **Unpaywall**: OA PDF 解析器（需邮箱）
- **Web Search**: 扩展检索，覆盖更多资源

### 3. PDF 下载 ⭐ 核心功能
- **多策略解析**: 直接 URL → Unpaywall → OpenAlex OA → CORE
- **开放获取优先**: 自动查找 OA 版本 PDF
- **并发下载**: 支持批量下载（默认 3 并发）
- **智能验证**: PDF 格式验证、文件大小检查
- **元数据索引**: 自动维护 metadata.json 索引
- **支持的源**: arXiv (100%)、OpenAlex (OA)、CORE (OA)、Semantic Scholar (部分)

### 4. 智能排序
- 按引用数排序
- 按发布时间排序
- 按相关性排序

### 5. 信息提取
- 论文标题、作者、摘要
- 发布时间、期刊/会议
- 引用数、影响力指标

## CLI Usage

### 查询扩展
```bash
# 单次模式 - 快速扩展查询
lit expand "我想做 AI 相关的研究"

# 保存结果到文件
lit expand "Transformer 在 NLP 中的应用" --output keywords.md

# 交互式模式 - 多轮对话明确方向
lit expand "机器学习" --interactive
```

### 基础检索
```bash
# 基础搜索
lit search "transformer attention mechanism" --limit 20

# 指定领域（自动选择最佳数据源）
lit search "CRISPR gene editing" --domain biomedical

# 指定数据源
lit search "deep learning" --source semantic_scholar,arxiv --sort citations

# 搜索并下载 PDF
lit search "attention is all you need" --download --limit 3
```

### PDF 下载
```bash
# 专门的下载命令（默认 5 篇）
lit download "transformer" --limit 5

# 指定输出目录
lit download "attention mechanism" --output ./papers --limit 10

# 指定数据源（优先选择有 PDF 的源）
lit download "BERT" --source arxiv,openalex --limit 3

# 下载结果会保存到指定目录，并生成 metadata.json 索引
```

### 使用脚本
```bash
# 运行文献检索脚本
bun run skills/literature-search/scripts/search.ts "attention mechanism"

# 指定数据源
bun run skills/literature-search/scripts/search.ts "transformer" --source arxiv

# 限制结果数量
bun run skills/literature-search/scripts/search.ts "GPT" --limit 20
```

## API Usage

### 查询扩展
```typescript
import QueryExpander from './scripts/query-expander';

const expander = new QueryExpander();
await expander.initialize();

// 单次扩展
const result = await expander.expandQuery('我想做 AI 相关的研究');
console.log(expander.formatResult(result));

// 交互式扩展
const conversationHistory = [];
const result2 = await expander.interactiveExpand(
  '深度学习',
  conversationHistory
);
```

### 简单搜索
```typescript
import LiteratureSearch from './scripts/search';
import { PdfDownloader } from './scripts/pdf-downloader';

const searcher = new LiteratureSearch();
await searcher.initialize();

// 搜索文献
const results = await searcher.search("transformer attention", {
  sources: ['arxiv', 'semantic_scholar'],
  limit: 10,
  sortBy: 'relevance'
});

console.log(results);

// 下载 PDF
const downloader = new PdfDownloader(
  { outputDir: './papers' },
  searcher.getRegistry()
);
const downloads = await downloader.downloadResults(results.results);
console.log(`Downloaded ${downloads.length} PDFs`);
```

### 高级搜索
```typescript
// 带过滤条件的搜索
const filtered = await searcher.search("machine learning", {
  sources: ['arxiv'],
  limit: 20,
  filters: {
    yearRange: [2022, 2024],
    categories: ['cs.LG', 'cs.AI'],
    minCitations: 10
  },
  sortBy: 'citations'
});

// 按作者搜索
const byAuthor = await searcher.searchByAuthor("Yann LeCun", {
  limit: 15,
  sortBy: 'date'
});
```

### PDF 下载 API
```typescript
import { PdfDownloader } from './scripts/pdf-downloader';
import type { PdfDownloadOptions } from './scripts/types';

// 创建下载器
const options: PdfDownloadOptions = {
  outputDir: './downloads/pdfs',  // 输出目录
  maxFileSize: 50 * 1024 * 1024,  // 最大文件大小 (50MB)
  skipExisting: true,              // 跳过已存在文件
  concurrency: 3,                  // 并发数
  namingStrategy: 'title'          // 命名策略: 'title' | 'doi' | 'id'
};

const downloader = new PdfDownloader(options, searcher.getRegistry());

// 下载搜索结果
const downloads = await downloader.downloadResults(results.results);

// 下载结果
downloads.forEach(dl => {
  console.log(`Downloaded: ${dl.title}`);
  console.log(`  Path: ${dl.filePath}`);
  console.log(`  Size: ${(dl.size / 1024).toFixed(1)} KB`);
});
```

## Output Format

### QueryExpansionResult 类型
```typescript
interface QueryExpansionResult {
  confirmation: {
    coreTheme?: string;          // 核心主题
    subField?: string;           // 子领域
    applicationScenario?: string; // 应用场景
    timeRange?: string;          // 时间范围
    preferredSources?: string;   // 偏好来源
  };
  keywords: Array<{
    term: string;                // 关键词
    description: string;         // 描述
    type: 'core' | 'synonym' | 'abbreviation' | 'related' | 'application';
  }>;
  followUpQuestions?: string[];  // 追问问题
  needsMoreInfo: boolean;        // 是否需要更多信息
}
```

### SearchResult 类型
```typescript
interface SearchResult {
  id: string;              // 论文唯一标识
  title: string;           // 标题
  authors: string[];       // 作者列表
  abstract: string;        // 摘要
  publishDate: string;     // 发布日期
  source: string;          // 数据源
  url: string;             // 论文链接
  pdfUrl?: string;         // PDF链接
  citations?: number;      // 引用数
  venue?: string;          // 期刊/会议
  keywords?: string[];     // 关键词
  doi?: string;            // DOI
  openAccess?: boolean;    // 是否开放获取
}
```

### PdfDownloadOptions 类型
```typescript
interface PdfDownloadOptions {
  outputDir?: string;           // 输出目录 (默认: ./downloads/pdfs)
  maxFileSize?: number;         // 最大文件大小 (默认: 50MB)
  skipExisting?: boolean;       // 跳过已存在文件 (默认: true)
  concurrency?: number;         // 并发下载数 (默认: 3)
  namingStrategy?: 'title' | 'doi' | 'id';  // 文件命名策略 (默认: title)
}
```

### PdfDownloadResult 类型
```typescript
interface PdfDownloadResult {
  filePath: string;        // 文件路径
  title: string;           // 论文标题
  source: string;          // 数据源
  size: number;            // 文件大小（字节）
  doi?: string;            // DOI
}
```

## Integration Examples

### 查询扩展 + 文献检索工作流
```typescript
import QueryExpander from './scripts/query-expander';
import LiteratureSearch from './scripts/search';

async function expandAndSearch(vagueQuery: string) {
  // 1. 扩展查询
  const expander = new QueryExpander();
  await expander.initialize();
  const expansion = await expander.expandQuery(vagueQuery);

  console.log('生成的关键词:', expansion.keywords.map(k => k.term));

  // 2. 使用生成的关键词搜索
  const searcher = new LiteratureSearch();
  await searcher.initialize();

  const allResults = [];
  for (const keyword of expansion.keywords.slice(0, 3)) {
    const results = await searcher.search(keyword.term, { limit: 5 });
    allResults.push(...results);
  }

  return { expansion, results: allResults };
}

// 使用示例
const result = await expandAndSearch('我想研究大语言模型');
```

### 与AI分析结合
```typescript
import LiteratureSearch from './scripts/search';
import ZAI from 'z-ai-web-dev-sdk';

async function searchAndAnalyze(query: string) {
  const searcher = new LiteratureSearch();
  await searcher.initialize();

  // 搜索文献
  const results = await searcher.search(query, { limit: 5 });

  // 使用AI分析结果
  const zai = await ZAI.create();
  const summary = await zai.chat.completions.create({
    messages: [{
      role: 'user',
      content: `分析以下文献搜索结果，总结研究趋势:\n${JSON.stringify(results, null, 2)}`
    }]
  });

  return { results, analysis: summary.choices[0].message.content };
}
```

### 完整的 PDF 下载工作流
```typescript
import LiteratureSearch from './scripts/search';
import { PdfDownloader } from './scripts/pdf-downloader';
import { readFileSync } from 'fs';
import { join } from 'path';

async function downloadAndIndex(query: string, outputDir: string = './papers') {
  // 1. 搜索文献（优先选择有 PDF 的源）
  const searcher = new LiteratureSearch();
  await searcher.initialize();

  const results = await searcher.search(query, {
    sources: ['arxiv', 'openalex', 'core'],  // 高 PDF 可用率的源
    limit: 20,
    sortBy: 'citations'
  });

  console.log(`Found ${results.totalResults} papers`);

  // 2. 下载 PDF
  const downloader = new PdfDownloader(
    {
      outputDir,
      skipExisting: true,
      concurrency: 3,
      namingStrategy: 'title'
    },
    searcher.getRegistry()
  );

  const downloads = await downloader.downloadResults(results.results);
  console.log(`Downloaded ${downloads.length} PDFs`);

  // 3. 读取元数据索引
  const metadataPath = join(outputDir, 'metadata.json');
  const metadata = JSON.parse(readFileSync(metadataPath, 'utf-8'));

  // 4. 生成下载报告
  console.log('\n=== Download Report ===');
  metadata.files.forEach((file: any, i: number) => {
    console.log(`${i + 1}. ${file.title}`);
    console.log(`   Authors: ${file.authors.join(', ')}`);
    console.log(`   Source: ${file.source}`);
    console.log(`   File: ${file.filePath}`);
    console.log(`   Downloaded: ${file.downloadedAt}`);
    console.log('');
  });

  return { results, downloads, metadata };
}

// 使用示例
await downloadAndIndex('transformer attention mechanism', './papers/transformers');
```

## Best Practices

1. **使用查询扩展**: 对于模糊的研究兴趣，先用 `expand` 命令生成具体关键词
2. **明确检索词**: 使用具体的技术术语而非模糊概念
3. **组合数据源**: 不同数据源覆盖不同范围的文献
4. **合理排序**: 根据目的选择排序方式 (引用数/时间/相关性)
5. **缓存结果**: 避免重复检索相同内容
6. **定期更新**: 关注新发表论文，保持知识更新
7. **交互式模式**: 不确定研究方向时使用 `--interactive` 模式

### PDF 下载最佳实践
8. **优先选择 OA 源**: arXiv、OpenAlex、CORE 提供更高的 PDF 可用率
9. **合理设置并发**: 默认 3 并发，避免触发 API 限流
10. **检查 metadata.json**: 下载后检查索引文件，了解下载详情
11. **仅下载 OA 论文**: 本工具仅支持开放获取论文，尊重版权
12. **配置 Unpaywall**: 设置 `UNPAYWALL_EMAIL` 环境变量提高 PDF 解析成功率
13. **文件命名策略**: 使用 `title` 策略便于浏览，使用 `doi` 策略避免重名

## Troubleshooting

### 问题：检索结果太少
- 尝试扩大检索词范围
- 增加数据源数量
- 检查拼写是否正确

### 问题：结果质量不高
- 使用引用数排序
- 添加时间过滤
- 指定高质量期刊/会议

### 问题：API限制
- 实现请求缓存
- 使用合理的请求间隔
- 合并相似请求

### 问题：PDF 下载失败
- **无 PDF URL**: 论文可能不是开放获取，尝试其他数据源
- **下载超时**: 检查网络连接，降低并发数
- **文件过大**: 调整 `maxFileSize` 参数
- **格式验证失败**: 下载的可能不是真实 PDF，检查 URL 有效性
- **Unpaywall 无结果**: 确保设置了 `UNPAYWALL_EMAIL` 环境变量

### 问题：PDF 可用率低
- **优先使用 arXiv**: 100% PDF 可用率
- **启用 Unpaywall**: 设置邮箱后可解析更多 DOI
- **使用 OpenAlex**: 提供大量 OA 论文 PDF
- **避免付费源**: IEEE、部分 PubMed 论文需要订阅

## File Structure

```
skills/literature-search/
├── skill.md              # 本说明文档
├── scripts/
│   ├── search.ts         # 核心搜索脚本
│   ├── query-expander.ts # 查询扩展脚本 ⭐ 新增
│   ├── pdf-downloader.ts # PDF 下载模块 ⭐ 核心功能
│   ├── search-strategy.ts # 互补搜索策略
│   ├── types.ts          # 类型定义
│   └── adapters/         # 搜索源适配器
│       ├── base.ts       # 适配器基类
│       ├── registry.ts   # 适配器注册表
│       ├── arxiv-adapter.ts
│       ├── semantic-scholar-adapter.ts
│       ├── openalex-adapter.ts
│       ├── pubmed-adapter.ts
│       ├── crossref-adapter.ts
│       ├── dblp-adapter.ts
│       ├── ieee-adapter.ts
│       ├── core-adapter.ts
│       ├── unpaywall-adapter.ts
│       ├── google-scholar-adapter.ts
│       └── web-adapter.ts
└── examples/
    ├── basic.ts          # 基础用法示例
    └── advanced.ts       # 高级用法示例
```

## Related Documentation

- [QUERY_EXPANSION.md](../../QUERY_EXPANSION.md) - 查询扩展功能详细文档
