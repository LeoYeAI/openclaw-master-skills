# 灵魂提取 Prompt 模板

## 对话分析提取 Prompt

分析以下对话内容，提取用户的人格信息。只提取你有把握的信息（置信度 > 0.6），不要猜测或编造。

### 提取维度

请按以下格式输出 JSON，只包含本次对话中**新发现**的信息：

```json
{
  "basic_info": {
    "字段名": {"value": "值", "confidence": 0.9}
  },
  "personality": {
    "traits": ["新发现的性格标签"],
    "values": ["新发现的价值观"]
  },
  "language": {
    "catchphrases": ["口头禅"],
    "sentence_patterns": ["句式模式描述"],
    "examples": ["原文例句"],
    "formality_level": "casual/semi-formal/formal",
    "verbosity": "concise/moderate/verbose",
    "humor_style": "描述"
  },
  "topics": [
    {
      "name": "话题名",
      "sentiment": "positive/negative/neutral/mixed",
      "stance": "立场描述",
      "key_opinions": ["具体观点"]
    }
  ],
  "episodic": [
    {
      "event": "事件描述",
      "emotion": "当时的情绪",
      "context": "背景",
      "significance": "normal/important/milestone"
    }
  ],
  "emotional": {
    "triggers": {
      "joy": ["让TA开心的事"],
      "anger": ["让TA生气的事"]
    }
  },
  "people": [
    {
      "name": "人名",
      "relationship": "关系",
      "description": "描述"
    }
  ],
  "summary": "一句话总结本次提取发现了什么"
}
```

### 提取原则

1. **只提取明确信息**：用户说"我在武汉"→ location: 武汉（✓）；用户聊到武汉的天气 → 不能推断 location（✗）
2. **语言风格看原文**：直接引用用户的原话作为 examples，不要改写
3. **口头禅要出现 2+ 次**：只出现一次的不算口头禅
4. **观点要有论据**：不只记录立场，还要记录支撑理由
5. **情感触发看语境**：不是用户提到的话题，而是能引发TA情绪变化的事物
6. **未提及的字段留空**：不要填 null 或空数组，直接不包含该字段
