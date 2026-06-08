# Knowledge Gap Detector Skill

## Overview

知识盲区发现器，主动识别用户的知识缺口，帮助发现"你不知道你不知道"的内容。通过分析已有知识、领域图谱、论文引用网络等方式，推断用户可能忽略的重要概念和技术方向。

## Core Capabilities

### 1. 知识盲区识别
- 基于领域知识图谱分析缺口
- 识别相关但未探索的方向
- 发现跨学科交叉点

### 2. 学习优先级排序
- 评估盲区的重要性和紧迫性
- 推荐学习顺序
- 估计补齐所需时间

### 3. 个性化推荐
- 基于用户已有知识背景
- 考虑学习目标和工作需求
- 生成定制化学习建议

## CLI Usage

### 分析知识盲区
```bash
# 分析某领域的知识盲区
bun run skills/knowledge-gap-detector/scripts/detect.ts --domain "Natural Language Processing" --known "transformer,attention,BERT"

# 从用户知识档案分析
bun run skills/knowledge-gap-detector/scripts/detect.ts --profile ./my-knowledge.json

# 输出盲区报告
bun run skills/knowledge-gap-detector/scripts/detect.ts --domain "Machine Learning" --output gap-report.md
```

## API Usage

### 基础用法
```typescript
import KnowledgeGapDetector from './scripts/detect';

const detector = new KnowledgeGapDetector();
await detector.initialize();

// 检测知识盲区
const gaps = await detector.detect({
  domain: 'Natural Language Processing',
  knownConcepts: ['transformer', 'attention', 'BERT', 'GPT'],
  targetLevel: 'advanced'
});

console.log(gaps);
// {
//   criticalGaps: [...],
//   recommendedGaps: [...],
//   optionalGaps: [...],
//   crossDisciplinary: [...],
//   emergingTopics: [...]
// }
```

### 高级用法
```typescript
// 从知识档案分析
const gaps = await detector.detectFromProfile({
  profilePath: './knowledge-profile.json',
  domain: 'Machine Learning'
});

// 分析学习路径缺口
const pathGaps = await detector.analyzeLearningPath({
  currentPath: ['Python', 'NumPy', 'Pandas'],
  targetRole: 'Machine Learning Engineer'
});

// 发现跨学科机会
const crossGaps = await detector.discoverCrossDisciplinary({
  primaryDomain: 'NLP',
  relatedDomains: ['Computer Vision', 'Speech Recognition']
});
```

## Output Format

### GapReport 类型
```typescript
interface GapReport {
  domain: string;
  analysisDate: string;
  summary: {
    totalGaps: number;
    criticalCount: number;
    recommendedCount: number;
    optionalCount: number;
  };
  criticalGaps: KnowledgeGap[];      // 必须补齐的关键缺口
  recommendedGaps: KnowledgeGap[];   // 建议学习的内容
  optionalGaps: KnowledgeGap[];      // 可选的扩展内容
  crossDisciplinary: KnowledgeGap[]; // 跨学科交叉点
  emergingTopics: KnowledgeGap[];    // 新兴主题
  suggestedOrder: string[];          // 建议学习顺序
  estimatedEffort: {
    critical: string;                // 补齐关键缺口所需时间
    recommended: string;             // 建议学习所需时间
  };
}

interface KnowledgeGap {
  concept: string;
  category: 'critical' | 'recommended' | 'optional' | 'cross-disciplinary' | 'emerging';
  reason: string;                    // 为什么这是盲区
  importance: 1 | 2 | 3 | 4 | 5;     // 重要性等级
  prerequisites: string[];           // 前置知识
  relatedKnown: string[];            // 相关已知知识
  resources: LearningResource[];
  estimatedTime: string;
  impactIfLearned: string;           // 学会后的影响
}
```

## Detection Methods

### 方法一：领域图谱分析
```typescript
// 基于领域标准知识图谱检测缺口
const gaps = await detector.detectByGraph({
  domain: 'Deep Learning',
  knownConcepts: ['neural network', 'backpropagation'],
  graphSource: 'standard' // 使用标准知识图谱
});
```

### 方法二：引用网络分析
```typescript
// 基于论文引用网络发现盲区
const gaps = await detector.detectByCitations({
  knownPapers: ['Attention Is All You Need', 'BERT'],
  domain: 'NLP'
});
```

### 方法三：从业者技能对比
```typescript
// 对比行业从业者常见技能
const gaps = await detector.detectByRole({
  currentSkills: ['Python', 'TensorFlow'],
  targetRole: 'ML Engineer',
  level: 'senior'
});
```

## Integration Examples

### 与概念学习器结合
```typescript
import KnowledgeGapDetector from '../knowledge-gap-detector/scripts/detect';
import ConceptLearner from '../concept-learner/scripts/learn';

async function fillKnowledgeGaps(domain: string, known: string[]) {
  const detector = new KnowledgeGapDetector();
  const learner = new ConceptLearner();

  await Promise.all([detector.initialize(), learner.initialize()]);

  // 检测盲区
  const gaps = await detector.detect({ domain, knownConcepts: known });

  // 生成盲区学习卡片
  const cards = await Promise.all(
    gaps.criticalGaps.slice(0, 3).map(gap => 
      learner.learn(gap.concept)
    )
  );

  return { gaps, cards };
}
```

## Best Practices

1. **定期检测**: 每月或每季度进行一次盲区检测
2. **聚焦关键缺口**: 优先补齐critical类型的盲区
3. **结合实践**: 学完概念后尝试项目应用
4. **记录成长**: 保存检测报告，追踪知识增长
5. **保持开放**: 接受可能出乎意料的盲区建议

## Troubleshooting

### 问题：检测结果太多
- 缩小领域范围
- 提高targetLevel精度
- 添加更多已知概念

### 问题：建议不够相关
- 提供更详细的已知知识列表
- 指定具体的工作/学习目标
- 更新领域选择

### 问题：优先级不合理
- 手动调整category
- 结合个人目标重新评估
- 参考同行经验

## File Structure

```
skills/knowledge-gap-detector/
├── skill.md           # 本说明文档
├── scripts/
│   ├── detect.ts      # 核心检测脚本
│   ├── types.ts       # 类型定义
│   └── domain-graphs/ # 领域知识图谱
└── examples/
    ├── basic.ts       # 基础用法示例
    └── advanced.ts    # 高级用法示例
```
