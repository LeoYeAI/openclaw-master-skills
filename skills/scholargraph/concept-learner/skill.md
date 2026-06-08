# Concept Learner Skill

## Overview

概念快速学习器，帮助用户在遇到陌生知识概念时，快速构建完整的知识框架。自动整合定义、历史、核心原理、应用场景、相关概念等信息，生成结构化的学习卡片。

## Core Capabilities

### 1. 概念框架构建
- 自动提取概念定义与解释
- 识别核心组成要素
- 梳理发展历史与演进
- 发现实际应用场景

### 2. 知识关联
- 自动识别相关概念
- 区分前置知识与后续知识
- 构建概念关系网络

### 3. 学习路径生成
- 从入门到精通的学习建议
- 推荐学习资源（论文、教程、课程）
- 估计学习时间与难度

## CLI Usage

### 快速学习
```bash
# 使用CLI快速学习概念
bun run skills/concept-learner/scripts/learn.ts "Transformer"

# 指定学习深度
bun run skills/concept-learner/scripts/learn.ts "Attention Mechanism" --depth advanced

# 输出到文件
bun run skills/concept-learner/scripts/learn.ts "BERT" --output concept-card.md
```

## API Usage

### 基础用法
```typescript
import ConceptLearner from './scripts/learn';

const learner = new ConceptLearner();
await learner.initialize();

// 学习一个概念
const conceptCard = await learner.learn('Transformer');

console.log(conceptCard);
// {
//   concept: 'Transformer',
//   definition: '...',
//   coreComponents: [...],
//   history: {...},
//   applications: [...],
//   relatedConcepts: [...],
//   learningPath: [...],
//   resources: [...]
// }
```

### 高级用法
```typescript
// 深度学习模式
const deepDive = await learner.learn('Large Language Model', {
  depth: 'advanced',
  includePapers: true,
  includeCode: true,
  language: 'zh-CN'
});

// 对比学习两个概念
const comparison = await learner.compare('RNN', 'Transformer');

// 学习路径规划
const path = await learner.planLearningPath('Natural Language Processing', {
  currentLevel: 'beginner',
  targetLevel: 'advanced',
  timeCommitment: '10 hours/week'
});
```

## Output Format

### ConceptCard 类型
```typescript
interface ConceptCard {
  concept: string;
  definition: string;
  shortExplanation: string;    // 一句话解释
  coreComponents: {
    name: string;
    description: string;
    importance: 'high' | 'medium' | 'low';
  }[];
  history: {
    origin: string;            // 起源时间与背景
    keyDevelopments: {
      year: string;
      event: string;
      significance: string;
    }[];
    currentStatus: string;     // 当前状态
  };
  applications: {
    domain: string;
    examples: string[];
    impact: string;
  }[];
  relatedConcepts: {
    concept: string;
    relationship: 'prerequisite' | 'related' | 'derived' | 'alternative';
    briefExplanation: string;
  }[];
  learningPath: {
    stage: string;
    concepts: string[];
    estimatedTime: string;
    resources: string[];
  }[];
  resources: {
    type: 'paper' | 'tutorial' | 'course' | 'book' | 'code';
    title: string;
    url?: string;
    description: string;
    difficulty: 'beginner' | 'intermediate' | 'advanced';
  }[];
  keyPapers?: Paper[];
  codeExamples?: CodeExample[];
}
```

## Integration Examples

### 与文献检索结合
```typescript
import ConceptLearner from './scripts/learn';
import LiteratureSearch from '../literature-search/scripts/search';

async function deepLearnConcept(concept: string) {
  const learner = new ConceptLearner();
  const searcher = new LiteratureSearch();
  
  await Promise.all([learner.initialize(), searcher.initialize()]);
  
  // 获取概念卡片
  const card = await learner.learn(concept, { includePapers: true });
  
  // 补充最新论文
  const papers = await searcher.search(concept, {
    limit: 5,
    sortBy: 'date'
  });
  
  return {
    ...card,
    recentPapers: papers.results
  };
}
```

## Best Practices

1. **明确学习目标**: 指定depth参数控制详细程度
2. **结合实践**: 设置includeCode获取代码示例
3. **循序渐进**: 先学前置概念再学目标概念
4. **多维度学习**: 结合论文、教程、代码多种资源
5. **定期复习**: 保存概念卡片，定期回顾

## Troubleshooting

### 问题：概念解释不够详细
- 使用depth: 'advanced'
- 设置includePapers: true

### 问题：相关概念太多
- 使用importance过滤
- 专注于prerequisite关系

### 问题：学习路径不适合
- 指定currentLevel和targetLevel
- 调整timeCommitment

## File Structure

```
skills/concept-learner/
├── skill.md           # 本说明文档
├── scripts/
│   ├── learn.ts       # 核心学习脚本
│   └── types.ts       # 类型定义
└── examples/
    ├── basic.ts       # 基础用法示例
    └── advanced.ts    # 高级用法示例
```
