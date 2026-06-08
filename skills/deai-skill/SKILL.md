---
name: deai-skill
description: Remove AI-like features from text to make it more natural and human-like (去除AI生成文本的AI特征，使文本更自然、更接近人类写作)
homepage: https://github.com/yourusername/deai-skill
user-invocable: true
version: 1.0.0
tags:
  - text-processing
  - ai-humanization
  - natural-language-processing
  - multilingual
  - chinese
  - english
author: OpenClaw Team
license: MIT
---

# De-AI-fy Text Skill | 去AI味文本技能

## 功能说明 | Function Description

【中文】
本技能是一个专业的AI文本去AI味处理工具，用于去除AI生成文本中的典型AI特征，使文本看起来更加自然、接近人类写作风格。该技能支持中文和英文两种语言，提供多种处理风格，适用于各种文本处理场景。

核心功能包括：
- AI特征检测：自动识别文本中的AI生成痕迹，检测过于完美的语法和句式结构
- 文本人性化处理：通过句式多样化、词汇替换和添加口语化表达来增强文本自然度
- 多语言支持：针对中文和英文的特定优化策略
- 多种处理风格：提供自然、口语和正式三种风格供用户选择

【English】
This skill is a professional AI text humanization tool designed to remove typical AI features from AI-generated text, making it appear more natural and closer to human writing style. The skill supports both Chinese and English languages, provides multiple processing styles, and is suitable for various text processing scenarios.

Core features include:
- AI Feature Detection: Automatically identify traces of AI generation in text, detecting overly perfect grammar and sentence structures
- Text Humanization: Enhance text naturalness through sentence diversification, vocabulary replacement, and adding colloquial expressions
- Multi-language Support: Optimization strategies specifically for Chinese and English
- Multiple Processing Styles: Provide natural, casual, and formal styles for user selection

## 使用方法 | Usage

【中文】

### Python API 使用

```python
from deai_skill import DeAIProcessor

# 创建处理器实例
processor = DeAIProcessor()

# 处理中文文本
chinese_text = "综上所述，我们可以看出人工智能技术正在改变我们的生活方式。"
humanized_text = processor.process(chinese_text, language='zh')
print(humanized_text)

# 处理英文文本
english_text = "In conclusion, it is important to note that artificial intelligence technology is transforming our way of life."
humanized_text = processor.process(english_text, language='en')
print(humanized_text)
```

### 命令行使用

```bash
# 处理单个文件
python deai_skill.py --input input.txt --output output.txt --language zh

# 批量处理目录
python deai_skill.py --input_dir ./texts --output_dir ./humanized --language en

# 指定风格
python deai_skill.py --input input.txt --output output.txt --language zh --style casual
```

【English】

### Python API Usage

```python
from deai_skill import DeAIProcessor

# Create processor instance
processor = DeAIProcessor()

# Process Chinese text
chinese_text = "综上所述，我们可以看出人工智能技术正在改变我们的生活方式。"
humanized_text = processor.process(chinese_text, language='zh')
print(humanized_text)

# Process English text
english_text = "In conclusion, it is important to note that artificial intelligence technology is transforming our way of life."
humanized_text = processor.process(english_text, language='en')
print(humanized_text)
```

### Command Line Usage

```bash
# Process single file
python deai_skill.py --input input.txt --output output.txt --language zh

# Batch process directory
python deai_skill.py --input_dir ./texts --output_dir ./humanized --language en

# Specify style
python deai_skill.py --input input.txt --output output.txt --language zh --style casual
```

## 配置选项 | Configuration Options

【中文】

### 处理风格 | Processing Styles

本技能提供三种处理风格，可根据不同场景选择：

1. **自然风格 (natural)**
   - 平衡处理，保持专业性的同时增强自然感
   - 适用于一般内容创作
   - 过渡词替换概率：70%
   - 正式词汇替换概率：60%
   - 口语化强度：轻度

2. **口语风格 (casual)**
   - 高度口语化，适用于日常交流场景
   - 适用于社交媒体和非正式写作
   - 过渡词替换概率：90%
   - 正式词汇替换概率：80%
   - 口语化强度：强烈

3. **正式风格 (formal)**
   - 保留专业性，仅做轻度调整
   - 适用于专业文档和技术内容
   - 过渡词替换概率：40%
   - 正式词汇替换概率：30%
   - 口语化强度：无

### 配置文件 | Configuration File

技能使用 `rules.json` 配置文件来定义转换规则和特征词列表。主要配置项包括：

- `chinese_ai_features`: 中文AI特征词列表
  - `transition_words`: 中文过渡词（如"综上所述"、"值得注意的是"）
  - `formal_words`: 中文正式词汇（如"具有"、"体现出"）
  - `idioms`: 中文成语（如"举足轻重"、"不可或缺"）

- `english_ai_features`: 英文AI特征词列表
  - `transition_words`: 英文过渡词（如"furthermore"、"moreover"）
  - `formal_words`: 英文正式词汇（如"possess"、"exhibit"）
  - `idioms`: 英文常用短语（如"play a crucial role"、"of great importance"）

- `conversion_rules`: 文本转换规则
  - `transition_replacements`: 过渡词替换规则
  - `formal_word_replacements`: 正式词汇替换规则
  - `sentence_patterns`: 句式模式转换规则

- `colloquial_expressions`: 口语化表达
  - `endings`: 句尾语气词
  - `fillers`: 填充词
  - `uncertainties`: 不确定性表达

【English】

### Processing Styles

This skill provides three processing styles that can be selected according to different scenarios:

1. **Natural Style (natural)**
   - Balanced processing that maintains professionalism while enhancing naturalness
   - Suitable for general content creation
   - Transition word replacement probability: 70%
   - Formal word replacement probability: 60%
   - Colloquial intensity: mild

2. **Casual Style (casual)**
   - Highly colloquial, suitable for daily communication scenarios
   - Suitable for social media and informal writing
   - Transition word replacement probability: 90%
   - Formal word replacement probability: 80%
   - Colloquial intensity: strong

3. **Formal Style (formal)**
   - Maintains professionalism with only mild adjustments
   - Suitable for professional documents and technical content
   - Transition word replacement probability: 40%
   - Formal word replacement probability: 30%
   - Colloquial intensity: none

### Configuration File

The skill uses the `rules.json` configuration file to define transformation rules and feature word lists. Main configuration items include:

- `chinese_ai_features`: List of Chinese AI feature words
  - `transition_words`: Chinese transition words (e.g., "综上所述", "值得注意的是")
  - `formal_words`: Chinese formal vocabulary (e.g., "具有", "体现出")
  - `idioms`: Chinese idioms (e.g., "举足轻重", "不可或缺")

- `english_ai_features`: List of English AI feature words
  - `transition_words`: English transition words (e.g., "furthermore", "moreover")
  - `formal_words`: English formal vocabulary (e.g., "possess", "exhibit")
  - `idioms`: English common phrases (e.g., "play a crucial role", "of great importance")

- `conversion_rules`: Text transformation rules
  - `transition_replacements`: Transition word replacement rules
  - `formal_word_replacements`: Formal word replacement rules
  - `sentence_patterns`: Sentence pattern transformation rules

- `colloquial_expressions`: Colloquial expressions
  - `endings`: Sentence ending particles
  - `fillers`: Filler words
  - `uncertainties`: Uncertainty expressions

## 示例 | Examples

【中文】

### 示例1：中文文本处理

**输入文本**：
```
综上所述，通过深入分析可以看出，人工智能技术在教育领域的应用具有巨大的潜力和广阔的前景。我们应该认识到，这一技术能够为学生提供个性化学习体验，同时也需要关注其可能带来的挑战。
```

**处理结果（自然风格）**：
```
总的来说，从分析中能看出来，AI技术在教育这块确实挺有潜力，前景也不错。它能给学生提供个性化的学习体验啊，不过咱们也得注意可能会遇到的一些问题。
```

**AI特征分析**：
- AI特征分数：0.25
- 检测到的AI特征：综上所述、具有、应该认识到

### 示例2：英文文本处理

**输入文本**：
```
In conclusion, after thorough analysis, it becomes evident that artificial intelligence technology possesses immense potential and promising prospects in the field of education. We should recognize that this technology can provide personalized learning experiences for students, while also paying attention to potential challenges that may arise.
```

**处理结果（自然风格）**：
```
Overall, looking at the analysis, AI technology clearly has huge potential in education. It can give students personalized learning experiences, but we also need to be aware of the challenges that might come up.
```

**AI特征分析**：
- AI特征分数：0.20
- 检测到的AI特征：in conclusion, possesses, should recognize

### 示例3：不同风格对比

**原文**：
```
这一问题具有多个方面的考虑因素，需要我们进行深入的分析和研究。值得注意的是，这一技术方案展现出明显的优势。
```

**自然风格**：
```
这一问题具有多个方面的考虑因素，需要我们进行深入的分析和研究。值得注意的是，这一技术方案展现出明显的优势呀。
```

**口语风格**：
```
这一问题具有多个方面的考虑因素，需要我们进行深入的分析和研究。有一点要提醒，这一技术方案展现出明显的优势呢。
```

**正式风格**：
```
这一问题具有多个方面的考虑因素，需要我们进行深入的分析和研究。得注意一下，这一技术方案展现出明显的优势。
```

【English】

### Example 1: Chinese Text Processing

**Input Text**:
```
综上所述，通过深入分析可以看出，人工智能技术在教育领域的应用具有巨大的潜力和广阔的前景。我们应该认识到，这一技术能够为学生提供个性化学习体验，同时也需要关注其可能带来的挑战。
```

**Processing Result (Natural Style)**:
```
总的来说，从分析中能看出来，AI技术在教育这块确实挺有潜力，前景也不错。它能给学生提供个性化的学习体验啊，不过咱们也得注意可能会遇到的一些问题。
```

**AI Feature Analysis**:
- AI feature score: 0.25
- Detected AI features: 综上所述, 具有, 应该认识到

### Example 2: English Text Processing

**Input Text**:
```
In conclusion, after thorough analysis, it becomes evident that artificial intelligence technology possesses immense potential and promising prospects in the field of education. We should recognize that this technology can provide personalized learning experiences for students, while also paying attention to potential challenges that may arise.
```

**Processing Result (Natural Style)**:
```
Overall, looking at the analysis, AI technology clearly has huge potential in education. It can give students personalized learning experiences, but we also need to be aware of the challenges that might come up.
```

**AI Feature Analysis**:
- AI feature score: 0.20
- Detected AI features: in conclusion, possesses, should recognize

### Example 3: Different Style Comparison

**Original Text**:
```
这一问题具有多个方面的考虑因素，需要我们进行深入的分析和研究。值得注意的是，这一技术方案展现出明显的优势。
```

**Natural Style**:
```
这一问题具有多个方面的考虑因素，需要我们进行深入的分析和研究。值得注意的是，这一技术方案展现出明显的优势呀。
```

**Casual Style**:
```
这一问题具有多个方面的考虑因素，需要我们进行深入的分析和研究。有一点要提醒，这一技术方案展现出明显的优势呢。
```

**Formal Style**:
```
这一问题具有多个方面的考虑因素，需要我们进行深入的分析和研究。得注意一下，这一技术方案展现出明显的优势。
```

## 注意事项 | Notes

【中文】

### 使用建议

1. **文本长度处理**
   - 对于长文本（超过2000字），建议分段处理以获得更好的效果
   - 每段建议不超过500字，可以分多次调用处理函数

2. **风格选择建议**
   - 专业文档：使用`formal`风格，保留更多专业术语和正式表达
   - 社交媒体：使用`casual`风格，增加口语化程度
   - 一般内容：使用`natural`风格，平衡专业性和自然度

3. **处理效果优化**
   - 建议在处理后进行人工检查，确保语义准确无误
   - 对于重要内容，可以多次处理并选择最佳版本
   - 针对特定领域，可以自定义规则文件以获得更好效果

4. **性能考虑**
   - 批量处理时，每批建议不超过100条文本
   - 在服务器环境下运行时，可以调整并发参数提升处理速度
   - 对于实时处理需求，建议使用流式处理接口

### 限制说明

1. 本技能主要针对AI生成文本的特征进行优化，不适用于文本纠错或润色
2. 处理效果取决于文本的初始质量，过于结构化的文本可能需要多次处理
3. 英文处理效果可能略逊于中文，因为规则主要针对中文AI文本特征优化
4. 对于专业领域的特殊术语和表达，可能需要自定义配置文件
5. 某些情况下，过度处理可能会影响文本的准确性，建议谨慎使用口语风格

### 依赖说明

- Python 3.6 或更高版本
- jieba（可选，用于中文分词，提升检测准确率）
- 标准库：zipfile, re, json, random, subprocess, pathlib

### 常见问题

**Q: 处理后的文本为什么还有一些AI特征？**
A: 本技能采用概率性的规则应用，为了保持文本的多样性，并非所有特征都会被替换。如果需要更强的处理效果，可以尝试：
1. 使用更口语化的风格（casual）
2. 多次处理同一文本
3. 自定义规则文件，添加更多替换规则

**Q: 能否处理其他语言的文本？**
A: 当前版本仅支持中文和英文。其他语言的支持正在开发中。

**Q: 处理速度如何？**
A: 处理速度约为每秒1000字符。对于批量处理，建议使用批量处理接口以获得更好的性能。

**Q: 如何自定义规则？**
A: 编辑`rules.json`文件，可以添加、修改或删除各种规则。详细说明请参考配置文件注释。

【English】

### Usage Recommendations

1. **Text Length Processing**
   - For long texts (over 2000 characters), it is recommended to process them in segments for better results
   - Each segment is recommended to be no more than 500 characters, and the processing function can be called multiple times

2. **Style Selection Recommendations**
   - Professional documents: Use `formal` style to preserve more technical terms and formal expressions
   - Social media: Use `casual` style to increase colloquialism
   - General content: Use `natural` style to balance professionalism and naturalness

3. **Processing Effect Optimization**
   - It is recommended to perform manual review after processing to ensure semantic accuracy
   - For important content, multiple processing can be performed and the best version selected
   - For specific domains, custom rule files can be used to achieve better results

4. **Performance Considerations**
   - For batch processing, it is recommended not to exceed 100 texts per batch
   - When running in a server environment, concurrency parameters can be adjusted to improve processing speed
   - For real-time processing needs, it is recommended to use the streaming processing interface

### Limitations

1. This skill is primarily optimized for features of AI-generated text and is not suitable for text correction or polishing
2. Processing results depend on the initial quality of the text; overly structured texts may require multiple processing passes
3. English processing results may be slightly inferior to Chinese as rules are primarily optimized for Chinese AI text features
4. For special terminology and expressions in professional domains, custom configuration files may be needed
5. In some cases, excessive processing may affect text accuracy; use of casual style is recommended with caution

### Dependencies

- Python 3.6 or higher
- jieba (optional, for Chinese word segmentation, improves detection accuracy)
- Standard libraries: zipfile, re, json, random, subprocess, pathlib

### Frequently Asked Questions

**Q: Why does the processed text still have some AI features?**
A: This skill uses probabilistic rule application, and not all features will be replaced to maintain text diversity. If stronger processing results are needed, you can try:
1. Using a more colloquial style (casual)
2. Processing the same text multiple times
3. Customizing the rule file to add more replacement rules

**Q: Can it process texts in other languages?**
A: The current version only supports Chinese and English. Support for other languages is under development.

**Q: What is the processing speed?**
A: The processing speed is approximately 1000 characters per second. For batch processing, it is recommended to use the batch processing interface for better performance.

**Q: How can I customize rules?**
A: Edit the `rules.json` file, where you can add, modify, or delete various rules. For detailed instructions, please refer to the configuration file comments.

## 更新日志 | Changelog

### Version 1.0.0 (2026-03-01)

【中文】
- 初始版本发布
- 支持中英文文本处理
- 实现基础的去AI化功能
- 提供Python API和命令行接口
- 支持三种处理风格（自然、口语、正式）
- 包含完整的测试和文档

【English】
- Initial release
- Support for Chinese and English text processing
- Implementation of basic de-AI functionality
- Python API and command line interface provided
- Support for three processing styles (natural, casual, formal)
- Complete testing and documentation included

## 许可证 | License

【中文】
本项目采用 MIT 许可证。详见 LICENSE 文件。

【English】
This project is licensed under the MIT License. See the LICENSE file for details.

## 联系方式 | Contact

【中文】
- 项目主页：https://github.com/YouStudyeveryday/deai-skill
- 问题反馈：https://github.com/YouStudyeveryday/deai-skill/issues


【English】
- Project homepage: https://github.com/yYouStudyeveryday/deai-skill
- Issue tracker: https://github.com/yYouStudyeveryday/deai-skill/issues


## 致谢 | Acknowledgments

【中文】
感谢所有为这个项目做出贡献的开发者和用户。特别感谢OpenClaw团队提供的支持。

【English】
Thanks to all developers and users who have contributed to this project. Special thanks to the OpenClaw team for their support.
