# 高级功能使用指南

本文档介绍新增的高级 CLI 命令。

## 新增命令

### 1. 概念对比 (compare concepts)

对比两个概念的相似点、差异点和使用场景。

**用法**:
```bash
lit compare concepts <概念1> <概念2> [--output <文件>]
```

**示例**:
```bash
# 对比 CNN 和 RNN
lit compare concepts CNN RNN --output cnn-vs-rnn.md

# 对比 Transformer 和 LSTM（输出到控制台）
lit compare concepts Transformer LSTM
```

**输出内容**:
- 相似点
- 差异点
- 使用场景（何时优先使用哪个概念）

---

### 2. 论文对比 (compare papers)

对比多篇论文的共同主题、主要差异和综合分析。

**用法**:
```bash
lit compare papers <URL1> <URL2> [<URL3>...] [--output <文件>]
```

**示例**:
```bash
# 对比两篇论文
lit compare papers \
  "https://www.semanticscholar.org/paper/83b90f4a0ae4cc214eb3cc140ccfef9cd99fac05" \
  "https://www.semanticscholar.org/paper/1f2a20a6efaf83214861dddae4a38a83ae18fe32" \
  --output paper-comparison.md
```

**输出内容**:
- 对比论文列表
- 共同主题
- 主要差异
- 综合分析

---

### 3. 批判性分析 (critique)

对论文进行批判性分析，识别优点、缺点、研究空白和改进建议。

**用法**:
```bash
lit critique <论文URL> [--focus <关注领域>] [--output <文件>]
```

**参数**:
- `--focus`: 重点关注的领域（逗号分隔），如 "scalability,efficiency"

**示例**:
```bash
# 批判性分析论文，关注可扩展性和效率
lit critique "https://arxiv.org/abs/2301.07001" \
  --focus "scalability,efficiency" \
  --output critique.md

# 不指定关注领域
lit critique "https://www.semanticscholar.org/paper/xxx"
```

**输出内容**:
- 论文信息
- 关注领域（如果指定）
- 优点
- 缺点
- 研究空白
- 改进建议
- 总体评价

---

### 4. 学习路径 (path)

查找从一个概念到另一个概念的学习路径。

**用法**:
```bash
lit path <起始概念> <目标概念> [--concepts <中间概念列表>] [--output <文件>]
```

**参数**:
- `--concepts`: 可选的中间概念列表（逗号分隔）

**示例**:
```bash
# 查找从机器学习到深度学习的路径
lit path "Machine Learning" "Deep Learning" \
  --concepts "Neural Networks,Backpropagation" \
  --output ml-to-dl-path.md

# 不指定中间概念
lit path "Beginner" "Expert"
```

**输出内容**:
- 推荐学习路径（按顺序）
- Mermaid 图表可视化
- 学习建议

---

## 完整示例

### 示例 1: 对比深度学习架构

```bash
# 对比 CNN 和 RNN
AI_PROVIDER=openai lit compare concepts CNN RNN --output cnn-vs-rnn.md

# 对比 Transformer 和 LSTM
AI_PROVIDER=openai lit compare concepts Transformer LSTM
```

### 示例 2: 分析论文质量

```bash
# 批判性分析论文
AI_PROVIDER=deepseek lit critique \
  "https://arxiv.org/abs/2301.07001" \
  --focus "novelty,reproducibility,scalability" \
  --output critique.md
```

### 示例 3: 规划学习路径

```bash
# 从基础到高级的学习路径
AI_PROVIDER=zhipu lit path "Linear Regression" "Deep Reinforcement Learning" \
  --concepts "Neural Networks,CNN,RNN,Q-Learning" \
  --output learning-path.md
```

### 示例 4: 对比相关论文

```bash
# 对比同一领域的多篇论文
AI_PROVIDER=openai lit compare papers \
  "https://www.semanticscholar.org/paper/paper1" \
  "https://www.semanticscholar.org/paper/paper2" \
  "https://www.semanticscholar.org/paper/paper3" \
  --output papers-comparison.md
```

---

## 注意事项

1. **API 限制**: 这些功能需要调用 AI API，请确保已配置有效的 API 密钥
2. **速率限制**: Semantic Scholar API 有速率限制，如遇到 429 错误，请稍后重试
3. **输出格式**: 所有命令都支持 `--output` 参数保存为 Markdown 文件，或直接输出到控制台

---

*文档生成时间: 2026-02-28*
