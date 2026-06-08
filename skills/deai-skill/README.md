# AI文本去味技能 (de-ai-fy-text)

## 项目简介

`de-ai-fy-text` 是一个专业的AI文本去味处理技能，用于去除AI生成文本中的典型AI特征，使文本看起来更加自然、接近人类写作风格。该技能支持中文和英文两种语言，提供多种处理风格，适用于各种文本处理场景。

## 核心功能

### 1. AI特征检测
- 自动识别文本中的AI生成痕迹
- 检测过于完美的语法和句式结构
- 识别常见的AI模式化表达
- 计算文本的AI特征分数

### 2. 文本人性化处理
- 句式多样化处理，打破单一句式模式
- 词汇替换，去除过于正式的词汇
- 添加口语化表达，增强自然感
- 增加个性化元素和不确定性表达

### 3. 中英文双语言支持
- **中文处理**：成语使用优化、标点符号调整、语气词增加
- **英文处理**：正式词汇替换、句式结构变化、俚语适度引入

### 4. 多种处理风格
- **自然风格**：平衡处理，保持专业性的同时增强自然感
- **口语风格**：大幅度口语化，适用于日常交流场景
- **正式风格**：保留专业性，仅做轻度调整

## 项目结构

```
.
├── SKILL.md              # 技能说明文档
├── README.md             # 项目说明文档（本文件）
├── deai_skill.py         # 核心实现代码
├── rules.json            # 规则配置文件
├── example_usage.py      # 使用示例
└── test_deai.py          # 单元测试
```

## 安装

### 环境要求

- Python 3.6 或更高版本

### 安装依赖

```bash
pip install jieba
```

`jieba` 是可选依赖，安装后可以提升中文文本处理效果。如果不安装，技能仍然可以运行，但某些功能可能会受影响。

## 快速开始

### Python API使用

```python
from deai_skill import DeAIProcessor

# 创建处理器实例
processor = DeAIProcessor()

# 处理中文文本
chinese_text = "综上所述，我们可以看出人工智能技术正在改变我们的生活方式。"
humanized_text = processor.process(chinese_text, language='zh')[0]
print(humanized_text)

# 处理英文文本
english_text = "In conclusion, it is important to note that artificial intelligence technology is transforming our way of life."
humanized_text = processor.process(english_text, language='en')[0]
print(humanized_text)
```

### 指定处理风格

```python
# 自然风格
result = processor.process(text, language='zh', style='natural')

# 口语风格
result = processor.process(text, language='zh', style='casual')

# 正式风格
result = processor.process(text, language='zh', style='formal')
```

### 命令行使用

```bash
# 处理单个文件
python deai_skill.py --input input.txt --output output.txt --language zh

# 批量处理目录
python deai_skill.py --input_dir ./texts --output_dir ./humanized --language en

# 指定风格
python deai_skill.py --input input.txt --output output.txt --language zh --style casual

# 直接处理文本
python deai_skill.py --text "综上所述，这是一个重要的结论。" --language zh

# 仅检测AI特征
python deai_skill.py --input input.txt --language zh --detect
```

### 批量处理

```python
texts = [
    "这一技术方案具有显著的优势和潜在的应用价值。",
    "通过深入分析，我们可以看出这种方法的有效性。",
    "需要注意的是，在实际应用中可能会遇到一些挑战。"
]

results = processor.batch_process(texts, language='zh')
for original, (humanized, features) in zip(texts, results):
    print(f"原文: {original}")
    print(f"处理后: {humanized}")
    print(f"AI分数: {features['ai_score']:.2f}\n")
```

## 配置说明

技能使用 `rules.json` 配置文件来定义转换规则和特征词列表。您可以根据需要自定义配置：

### 配置结构

```json
{
  "chinese_ai_features": {
    "transition_words": ["综上所述", "值得注意的是", ...],
    "formal_words": ["具有", "表现出", ...],
    "idioms": ["举足轻重", "息息相关", ...]
  },
  "english_ai_features": {
    "transition_words": ["furthermore", "moreover", ...],
    "formal_words": ["possess", "exhibit", ...],
    "idioms": ["play a crucial role", "of great importance", ...]
  },
  "conversion_rules": {
    "zh": {
      "transition_replacements": {...},
      "formal_word_replacements": {...}
    },
    "en": {
      "transition_replacements": {...},
      "formal_word_replacements": {...}
    }
  },
  "colloquial_expressions": {
    "zh": {
      "endings": ["吧", "呢", "啊", ...],
      "fillers": ["你知道", "那个", "其实", ...],
      "uncertainties": ["好像", "大概", "可能", ...]
    },
    "en": {
      "endings": [", right?", ", isn't it?", ...],
      "fillers": ["you know", "I mean", "like", ...],
      "uncertainties": ["sort of", "kind of", "maybe", ...]
    }
  }
}
```

### 自定义配置

您可以编辑 `rules.json` 文件来：

1. 添加新的AI特征词
2. 修改词汇替换规则
3. 调整口语化表达
4. 添加新的句式转换模式

## 示例

### 中文文本处理

**输入：**
```
综上所述，通过深入分析可以看出，人工智能技术在教育领域的应用具有巨大的潜力和广阔的前景。我们应该认识到，这一技术能够为学生提供个性化学习体验，同时也需要关注其可能带来的挑战。
```

**输出（自然风格）：**
```
总的来说吧，从分析中能看出来，AI技术在教育这块确实挺有潜力，前景也不错。它能给学生提供个性化的学习体验啊，不过咱们也得注意可能会遇到的一些问题。
```

### 英文文本处理

**输入：**
```
In conclusion, after thorough analysis, it becomes evident that artificial intelligence technology possesses immense potential and promising prospects in the field of education. We should recognize that this technology can provide personalized learning experiences for students, while also paying attention to potential challenges that may arise.
```

**输出（自然风格）：**
```
Overall, looking at the analysis, AI technology clearly has huge potential in education. It can give students personalized learning experiences, but we also need to be aware of the challenges that might come up.
```

## 测试

运行单元测试：

```bash
python test_deai.py
```

运行使用示例：

```bash
python example_usage.py
```

## API 参考

### DeAIProcessor

主要处理类，提供文本去AI味的核心功能。

#### 方法

##### `__init__(config_path: str = "rules.json")`
初始化处理器。

##### `process(text: str, language: str = 'zh', style: str = 'natural', detect_only: bool = False) -> Tuple[str, Optional[Dict]]`
处理文本，去除AI特征。

**参数：**
- `text`: 待处理文本
- `language`: 语言类型 ('zh' 或 'en')
- `style`: 处理风格 ('natural', 'casual', 'formal')
- `detect_only`: 是否只检测不处理

**返回：**
- (处理后的文本, AI特征信息)

##### `batch_process(texts: List[str], language: str = 'zh', style: str = 'natural') -> List[Tuple[str, Dict]]`
批量处理文本。

**参数：**
- `texts`: 文本列表
- `language`: 语言类型
- `style`: 处理风格

**返回：**
- 处理结果列表，每个元素为(处理后的文本, AI特征信息)

##### `get_ai_score(text: str, language: str = 'zh') -> float`
获取文本的AI特征分数。

**参数：**
- `text`: 待检测文本
- `language`: 语言类型

**返回：**
- AI特征分数 (0-1)

### AITextDetector

AI文本特征检测器，用于识别文本中的AI特征。

#### 方法

##### `detect_ai_features(text: str, language: str = 'zh') -> Dict`
检测文本中的AI特征。

**返回：**
- 包含AI特征信息的字典：
  - `ai_score`: 综合AI分数
  - `ai_phrases`: 检测到的AI特征词
  - `sentence_similarity`: 句式相似度
  - `formal_word_count`: 正式词汇数量

### TextHumanizer

文本人性化处理器，提供文本转换和重写功能。

#### 方法

##### `humanize_text(text: str, language: str = 'zh', style: str = 'natural') -> str`
人性化处理文本。

**参数：**
- `text`: 待处理文本
- `language`: 语言类型 ('zh' 或 'en')
- `style`: 处理风格 ('natural', 'casual', 'formal')

**返回：**
- 处理后的文本

## 使用建议

1. **文本长度**：对于长文本，建议分段处理以获得更好的效果
2. **批量处理**：批量处理时，每批建议不超过100条文本
3. **风格选择**：
   - 专业文档：使用 `formal` 风格
   - 社交媒体：使用 `casual` 风格
   - 一般内容：使用 `natural` 风格
4. **人工检查**：建议在处理后进行人工检查，确保语义准确无误

## 注意事项

1. 本技能主要针对AI生成文本的特征进行优化，不适用于文本纠错或润色
2. 处理效果取决于文本的初始质量，过于结构化的文本可能需要多次处理
3. 英文处理效果可能略逊于中文，因为规则主要针对中文AI文本特征优化

## 版本历史

- **v1.0.0** (2026-03-01)
  - 初始版本发布
  - 支持中英文文本处理
  - 实现基础的去AI化功能
  - 提供命令行和Python API两种使用方式

## 技术支持

如有问题或建议，请提交issue或联系开发团队。

## 许可证

MIT License

---

**开发者**: OpenClaw Team
**最后更新**: 2026-03-01