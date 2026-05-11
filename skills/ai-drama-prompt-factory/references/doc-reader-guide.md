# 大文档读取指南 (Doc Reader Guide)

## 何时使用

输入文本超过3万字时，需要先建立索引再按需读取。

## 索引策略

### 按章节索引
```
source/
├── chapter-01.txt (或整体文件)
├── chapter-02.txt
└── source-index.json
```

### source-index.json 格式
```json
{
  "title": "作品名",
  "total_chars": 150000,
  "total_chapters": 30,
  "chapters": [
    {
      "id": "ch01",
      "title": "第一章 雷劫",
      "char_range": [0, 5000],
      "summary": "主角陈易被雷劈中，在医院醒来发现获得异能",
      "key_events": ["被雷劈", "醒来", "发现异能"],
      "characters_introduced": ["陈易", "张慧芬"],
      "props_introduced": ["天机古卷"]
    }
  ]
}
```

## 读取策略

### Phase 1（策划）
- 通读全文概要/索引，不需逐字读取
- 重点提取：核心冲突、主要角色、关键事件

### Phase 2（设计）
- 精读角色首次出现的章节，提取外貌描述
- 精读关键场景描写段落

### Phase 3（剧本）
- 逐集精读对应章节
- 提取对白原文、动作描述、环境描写

### Phase 4（诊断）
- 回读原文锚点段落，校验忠实度
