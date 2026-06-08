# 查询扩展功能 (Query Expansion)

## 概述

查询扩展功能可以将用户模糊的研究兴趣转化为具体的搜索关键词，帮助用户更有效地进行文献检索。

## 功能特点

### 1. 智能理解
- 分析用户的模糊输入
- 识别核心主题和研究方向
- 理解应用场景和研究目的

### 2. 关键词生成
生成多种类型的关键词：
- **核心词** 🎯：用户提到的核心概念
- **同义词** 🔄：常见的替换词
- **缩写** 📝：全称和缩写
- **相关术语** 🔗：上下游技术、工具、框架
- **应用领域** 💡：具体应用场景

### 3. 交互式模式
- 支持多轮对话
- 通过提问逐步明确研究方向
- 最多 5 轮对话

## 使用方法

### 单次模式

```bash
# 基础用法
lit expand "我想做 AI 相关的研究"

# 保存结果到文件
lit expand "Transformer 在 NLP 中的应用" --output keywords.md
```

### 交互式模式

```bash
# 启动交互式对话
lit expand "机器学习" --interactive

# 系统会通过多轮对话帮助你明确研究方向
```

## 输出示例

### 示例 1: 模糊查询

**输入：** "我想做 AI 相关的研究"

**输出：**
```
📋 确认信息：
- 核心主题：人工智能（范围较广）

🔍 建议关键词：
1. 🎯 Artificial Intelligence - AI 总览
2. 🎯 Machine Learning - 机器学习基础
3. 🎯 Deep Learning - 深度学习
4. 🔗 Neural Networks - 神经网络
5. 🔗 Transformer - Transformer 架构
6. 💡 Large Language Model - 大语言模型
7. 💡 Computer Vision - 计算机视觉
8. 📝 NLP - 自然语言处理
9. 🔗 Reinforcement Learning - 强化学习
10. 💡 Generative AI - 生成式 AI

❓ 追问：
1. 你更偏向于 AI 的哪个具体方向？（如：生成内容、图像识别、强化学习等）
2. 是为了写论文、找创新点，还是为了工程应用？
```

### 示例 2: 具体查询

**输入：** "Transformer 在 NLP 中的应用"

**输出：**
```
📋 确认信息：
- 核心主题：Transformer 架构
- 子领域：自然语言处理
- 应用场景：NLP 应用研究

🔍 建议关键词：
1. 🎯 Transformer - 核心架构
2. 🎯 Natural Language Processing - 自然语言处理
3. 📝 NLP - 自然语言处理缩写
4. 🔗 BERT - 双向编码器表示
5. 🔗 GPT - 生成式预训练
6. 🔗 Attention Mechanism - 注意力机制
7. 💡 Machine Translation - 机器翻译
8. 💡 Text Generation - 文本生成
9. 💡 Question Answering - 问答系统
10. 🔗 Pre-training - 预训练模型
```

## 工作流程

### 阶段 1：理解需求
系统会分析以下信息：
1. **核心主题**：具体想研究什么？
2. **子领域/方向**：更具体的角度？
3. **应用场景**：研究目的是什么？
4. **时间范围**：需要多新的论文？
5. **偏好来源**：对某些期刊/会议有偏好吗？

### 阶段 2：生成关键词
根据理解的需求，生成多个可执行的搜索关键词。

### 阶段 3：后续搜索
使用生成的关键词进行文献检索：
```bash
lit search "Transformer"
lit search "BERT"
lit search "Attention Mechanism"
```

## 交互式模式示例

```bash
$ lit expand "机器学习" --interactive

🔍 查询扩展 - 交互式模式

我会通过几个问题来帮助你明确研究方向并生成搜索关键词。

💬 第 1 轮对话

📋 确认信息：
- 核心主题：机器学习

🔍 建议关键词：
1. 🎯 Machine Learning - 机器学习
2. 🔗 Supervised Learning - 监督学习
3. 🔗 Unsupervised Learning - 无监督学习
...

❓ 追问：
1. 你更关注机器学习的哪个方向？（监督学习、无监督学习、强化学习等）
2. 是理论研究还是实际应用？

请回答上述问题（输入 "skip" 跳过，"done" 完成）：
> 我想研究深度学习在图像识别中的应用

💬 第 2 轮对话

📋 确认信息：
- 核心主题：深度学习
- 子领域：图像识别
- 应用场景：计算机视觉应用

🔍 建议关键词：
1. 🎯 Deep Learning - 深度学习
2. 🎯 Image Recognition - 图像识别
3. 🎯 Computer Vision - 计算机视觉
4. 🔗 CNN - 卷积神经网络
5. 🔗 ResNet - 残差网络
...

✅ 查询扩展完成！
```

## 编程 API

```typescript
import QueryExpander from './literature-search/scripts/query-expander';

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

## 返回数据结构

```typescript
interface QueryExpansionResult {
  confirmation: {
    coreTheme?: string;
    subField?: string;
    applicationScenario?: string;
    timeRange?: string;
    preferredSources?: string;
  };
  keywords: Array<{
    term: string;
    description: string;
    type: 'core' | 'synonym' | 'abbreviation' | 'related' | 'application';
  }>;
  followUpQuestions?: string[];
  needsMoreInfo: boolean;
}
```

## 最佳实践

1. **从模糊到具体**：先用模糊的查询开始，根据建议逐步细化
2. **使用交互式模式**：对于不确定的研究方向，使用 `--interactive` 模式
3. **保存结果**：使用 `--output` 保存关键词列表，方便后续使用
4. **组合使用**：将生成的关键词与 `search` 命令结合使用

## 示例工作流

```bash
# 1. 扩展查询
lit expand "我想研究大语言模型" --output llm-keywords.md

# 2. 查看生成的关键词
cat llm-keywords.md

# 3. 使用关键词搜索
lit search "Large Language Model" --limit 20
lit search "GPT" --limit 20
lit search "Transformer" --limit 20

# 4. 学习相关概念
lit learn "Large Language Model" --depth advanced --papers
```

## 注意事项

- 需要配置 AI 提供商（AI_PROVIDER 环境变量）
- 交互式模式最多支持 5 轮对话
- 生成的关键词数量通常在 5-15 个之间
- 建议使用英文关键词进行文献检索

---

*功能版本: 1.0.0*
*最后更新: 2026-03-02*
