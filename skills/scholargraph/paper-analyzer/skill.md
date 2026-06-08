# Paper Analyzer Skill

## Overview

论文深度分析器，提供论文的智能阅读、理解和总结能力。支持PDF解析、关键点提取、方法论分析、实验结果解读、引用关系梳理等功能，帮助用户快速掌握论文精髓。

## Core Capabilities

### 1. 智能阅读
- 自动提取论文结构
- 识别关键章节
- 生成章节摘要

### 2. 深度分析
- 方法学分析
- 实验设计评估
- 创新点识别
- 局限性分析

### 3. 知识关联
- 引用关系分析
- 相关工作梳理
- 概念关系映射

## CLI Usage

### 分析论文
```bash
# 从URL分析论文
bun run skills/paper-analyzer/scripts/analyze.ts --url "https://arxiv.org/abs/2301.07001"

# 从本地PDF分析
bun run skills/paper-analyzer/scripts/analyze.ts --file ./paper.pdf

# 生成分析报告
bun run skills/paper-analyzer/scripts/analyze.ts --url "https://arxiv.org/abs/2301.07001" --output analysis.md
```

### 批量分析
```bash
# 批量分析多篇论文
bun run skills/paper-analyzer/scripts/batch.ts --input papers.txt --output reports/
```

## API Usage

### 基础用法
```typescript
import PaperAnalyzer from './scripts/analyze';

const analyzer = new PaperAnalyzer();
await analyzer.initialize();

// 分析论文
const analysis = await analyzer.analyze({
  url: 'https://arxiv.org/abs/2301.07001'
});

console.log(analysis);
// {
//   title: '...',
//   authors: [...],
//   abstract: '...',
//   keyPoints: [...],
//   methodology: {...},
//   experiments: {...},
//   conclusions: [...],
//   citations: [...],
//   limitations: [...],
//   futureWork: [...]
// }
```

### 高级用法
```typescript
// 深度分析
const deepAnalysis = await analyzer.analyze({
  url: 'https://arxiv.org/abs/2301.07001',
  depth: 'deep',
  includeCitations: true,
  includeRelatedWork: true
});

// 比较分析
const comparison = await analyzer.compare([
  'https://arxiv.org/abs/2301.07001',
  'https://arxiv.org/abs/2301.07002'
]);

// 提取方法论
const methodology = await analyzer.extractMethodology({
  url: 'https://arxiv.org/abs/2301.07001'
});

// 生成批判性分析
const critique = await analyzer.critique({
  url: 'https://arxiv.org/abs/2301.07001',
  focusAreas: ['methodology', 'experiments', 'conclusions']
});
```

## Output Format

### PaperAnalysis 类型
```typescript
interface PaperAnalysis {
  metadata: PaperMetadata;
  abstract: string;
  summary: string;              // 整体摘要
  keyPoints: KeyPoint[];        // 关键要点
  methodology: MethodologyAnalysis;
  experiments: ExperimentAnalysis;
  contributions: Contribution[];
  limitations: Limitation[];
  futureWork: string[];
  citations: {
    key: string;                // 关键引用
    count: number;              // 引用数
    recent: string[];           // 近期引用
  };
  relatedWork: RelatedWork[];
  reproducibility: {
    score: number;              // 可复现性评分 0-100
    codeAvailable: boolean;
    datasetAvailable: boolean;
    detailsAvailable: boolean;
    notes: string;
  };
  recommendations: {
    forResearchers: string[];   // 对研究者的建议
    forPractitioners: string[]; // 对实践者的建议
  };
}

interface PaperMetadata {
  title: string;
  authors: string[];
  venue?: string;
  year: string;
  doi?: string;
  arxivId?: string;
  url: string;
  keywords: string[];
}

interface KeyPoint {
  point: string;
  importance: 'critical' | 'important' | 'supporting';
  location: string;             // 在论文中的位置
  explanation: string;
}

interface MethodologyAnalysis {
  overview: string;
  approach: string;
  novelty: string;
  assumptions: string[];
  strengths: string[];
  weaknesses: string[];
}

interface ExperimentAnalysis {
  datasets: string[];
  metrics: string[];
  baselines: string[];
  mainResults: string;
  ablations: string[];
  analysis: string;
}

interface Contribution {
  description: string;
  type: 'methodological' | 'empirical' | 'theoretical' | 'dataset' | 'tool';
  significance: 'major' | 'moderate' | 'minor';
}

interface Limitation {
  description: string;
  impact: 'high' | 'medium' | 'low';
  potentialSolution?: string;
}

interface RelatedWork {
  category: string;
  papers: string[];
  comparison: string;
}
```

## Analysis Modes

### 快速分析
```typescript
const quick = await analyzer.analyze({
  url: '...',
  mode: 'quick'
});
// 返回：标题、摘要、关键点、主要结论
```

### 标准分析
```typescript
const standard = await analyzer.analyze({
  url: '...',
  mode: 'standard'
});
// 返回：完整的结构化分析
```

### 深度分析
```typescript
const deep = await analyzer.analyze({
  url: '...',
  mode: 'deep',
  includeCitations: true,
  includeRelatedWork: true
});
// 返回：包括引用分析、相关工作、批判性分析
```

## Integration Examples

### 与文献检索结合
```typescript
import PaperAnalyzer from './scripts/analyze';
import LiteratureSearch from '../literature-search/scripts/search';

async function searchAndAnalyze(query: string) {
  const searcher = new LiteratureSearch();
  const analyzer = new PaperAnalyzer();

  await Promise.all([searcher.initialize(), analyzer.initialize()]);

  // 搜索论文
  const results = await searcher.search(query, { limit: 5 });

  // 分析每篇论文
  const analyses = await Promise.all(
    results.results.map(r => analyzer.analyze({ url: r.url }))
  );

  return { papers: results.results, analyses };
}
```

### 与概念学习器结合
```typescript
import PaperAnalyzer from './scripts/analyze';
import ConceptLearner from '../concept-learner/scripts/learn';

async function extractAndLearnConcepts(paperUrl: string) {
  const analyzer = new PaperAnalyzer();
  const learner = new ConceptLearner();

  await Promise.all([analyzer.initialize(), learner.initialize()]);

  // 分析论文
  const analysis = await analyzer.analyze({ url: paperUrl });

  // 提取关键概念
  const concepts = analysis.keyPoints
    .filter(k => k.importance === 'critical')
    .map(k => k.point);

  // 学习每个概念
  const cards = await Promise.all(
    concepts.slice(0, 3).map(c => learner.learn(c))
  );

  return { analysis, conceptCards: cards };
}
```

## Best Practices

1. **选择合适的分析模式**: 快速浏览用quick，深入学习用standard/deep
2. **关注关键贡献**: 优先理解论文的主要贡献点
3. **结合引用分析**: 了解论文的学术背景
4. **注意局限性**: 批判性思考论文的限制
5. **记录笔记**: 将分析结果保存为笔记

## Troubleshooting

### 问题：无法解析PDF
- 确认URL可访问
- 尝试使用其他来源链接
- 检查PDF格式是否标准

### 问题：分析结果不完整
- 使用深度分析模式
- 指定focusAreas参数
- 检查网络连接

### 问题：语言识别错误
- 手动指定论文语言
- 使用PDF文本提取后分析

## File Structure

```
skills/paper-analyzer/
├── skill.md           # 本说明文档
├── scripts/
│   ├── analyze.ts     # 核心分析脚本
│   ├── types.ts       # 类型定义
│   └── pdf-parser.ts  # PDF解析工具
└── examples/
    ├── basic.ts       # 基础用法示例
    └── advanced.ts    # 高级用法示例
```
