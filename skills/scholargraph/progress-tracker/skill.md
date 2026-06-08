# Progress Tracker Skill

## Overview

进展追踪器，实时监控领域新动态，帮助用户持续跟进最新研究进展。支持关键词监控、学者追踪、会议论文追踪等多种监控模式，并生成定期摘要报告。

## Core Capabilities

### 1. 多维度监控
- 关键词监控：追踪特定研究主题
- 学者追踪：关注特定学者的最新工作
- 会议追踪：监控顶级会议论文
- 机构追踪：关注特定研究机构

### 2. 智能过滤
- 按重要性筛选
- 去重与聚合
- 相关性评分

### 3. 定期报告
- 日报/周报/月报
- 领域进展摘要
- 重点论文推荐

## CLI Usage

### 添加监控
```bash
# 添加关键词监控
bun run skills/progress-tracker/scripts/track.ts add keyword "large language model" --frequency daily

# 添加学者监控
bun run skills/progress-tracker/scripts/track.ts add author "Yann LeCun" --frequency weekly

# 添加会议监控
bun run skills/progress-tracker/scripts/track.ts add conference "NeurIPS" --year 2024
```

### 生成报告
```bash
# 生成日报
bun run skills/progress-tracker/scripts/track.ts report --type daily --output daily-report.md

# 生成周报
bun run skills/progress-tracker/scripts/track.ts report --type weekly --output weekly-report.md

# 特定领域报告
bun run skills/progress-tracker/scripts/track.ts report --topic "transformer"
```

## API Usage

### 基础用法
```typescript
import ProgressTracker from './scripts/track';

const tracker = new ProgressTracker();
await tracker.initialize();

// 添加监控项
await tracker.addWatch({
  type: 'keyword',
  value: 'large language model',
  frequency: 'daily'
});

// 获取最新进展
const updates = await tracker.getUpdates({
  since: '2024-01-01',
  limit: 20
});

console.log(updates);
```

### 高级用法
```typescript
// 批量添加监控
await tracker.addWatches([
  { type: 'keyword', value: 'attention mechanism', frequency: 'daily' },
  { type: 'keyword', value: 'transformer', frequency: 'daily' },
  { type: 'author', value: 'Geoffrey Hinton', frequency: 'weekly' }
]);

// 生成进度报告
const report = await tracker.generateReport({
  type: 'weekly',
  includeSummaries: true,
  highlightImportant: true
});

// 获取趋势分析
const trends = await tracker.analyzeTrends({
  topic: 'large language models',
  timeframe: 'month'
});
```

## Output Format

### ProgressReport 类型
```typescript
interface ProgressReport {
  reportType: 'daily' | 'weekly' | 'monthly';
  period: {
    start: string;
    end: string;
  };
  summary: {
    totalPapers: number;
    highlightedPapers: number;
    newKeywords: string[];
    trendingTopics: string[];
  };
  papers: PaperUpdate[];
  trending: TrendingTopic[];
  recommendations: PaperRecommendation[];
}

interface PaperUpdate {
  title: string;
  authors: string[];
  publishDate: string;
  source: string;
  url: string;
  abstract?: string;
  keywords: string[];
  matchedWatches: string[];  // 匹配的监控项
  relevanceScore: number;    // 相关性评分 0-1
  importance: 'high' | 'medium' | 'low';
  summary?: string;          // AI生成的摘要
}

interface TrendingTopic {
  topic: string;
  paperCount: number;
  changePercent: number;     // 相比上期变化
  keyPapers: string[];
}

interface PaperRecommendation {
  paper: PaperUpdate;
  reason: string;            // 推荐理由
  priority: number;
}
```

## Watch Configuration

### 监控配置文件 (watch-config.json)
```json
{
  "watches": [
    {
      "id": "watch_001",
      "type": "keyword",
      "value": "large language model",
      "frequency": "daily",
      "filters": {
        "minCitations": 0,
        "sources": ["arxiv", "semantic_scholar"],
        "categories": ["cs.CL", "cs.AI"]
      },
      "active": true,
      "createdAt": "2024-01-01"
    },
    {
      "id": "watch_002",
      "type": "author",
      "value": "Yann LeCun",
      "frequency": "weekly",
      "active": true
    }
  ],
  "settings": {
    "maxResultsPerWatch": 20,
    "enableNotifications": false,
    "reportSchedule": {
      "daily": "09:00",
      "weekly": "Monday 09:00",
      "monthly": "1st 09:00"
    }
  }
}
```

## Integration Examples

### 与文献检索结合
```typescript
import ProgressTracker from './scripts/track';
import LiteratureSearch from '../literature-search/scripts/search';

async function getComprehensiveUpdates(topic: string) {
  const tracker = new ProgressTracker();
  const searcher = new LiteratureSearch();

  await Promise.all([tracker.initialize(), searcher.initialize()]);

  // 添加监控
  await tracker.addWatch({
    type: 'keyword',
    value: topic,
    frequency: 'daily'
  });

  // 获取更新
  const updates = await tracker.getUpdates({ limit: 10 });

  // 补充搜索
  const searchResults = await searcher.search(topic, { limit: 5, sortBy: 'date' });

  return {
    trackedUpdates: updates,
    additionalSearch: searchResults
  };
}
```

## Best Practices

1. **合理设置监控频率**: 避免过于频繁的监控
2. **精细化关键词**: 使用具体的技术术语
3. **定期清理监控**: 删除不再关注的监控项
4. **结合报告**: 定期查看生成的报告
5. **标记重要论文**: 对重要发现进行标记和笔记

## Troubleshooting

### 问题：结果太多
- 增加过滤条件
- 提高相关性阈值
- 减少监控关键词

### 问题：错过重要论文
- 扩大关键词范围
- 增加学者监控
- 检查过滤条件

### 问题：重复结果
- 启用去重功能
- 调整监控间隔

## File Structure

```
skills/progress-tracker/
├── skill.md           # 本说明文档
├── scripts/
│   ├── track.ts       # 核心追踪脚本
│   ├── types.ts       # 类型定义
│   └── config.ts      # 配置管理
└── examples/
    ├── basic.ts       # 基础用法示例
    └── advanced.ts    # 高级用法示例
```
