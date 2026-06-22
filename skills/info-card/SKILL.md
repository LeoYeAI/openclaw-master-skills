---
name: info-card
description: >
  生成小红书风格信息卡/知识卡片/海报 PNG 图片。22 种模板：杂志封面(magazine-cover)、科技知识卡(tech-knowledge)、
  学术报告(academic-report)、产品功能(product-feature)、品牌调性(brand-mood)、清单打卡(checklist)、金句卡(quote-card)、
  对比卡(comparison)、数据高亮(stats-highlight)、步骤指南(step-guide)、时间线(timeline)、人物简介(profile-card)、
  推荐列表(rec-list)、问答卡(faq-card)、前后对比(before-after)、小贴士(tips-card)、日签(daily-card)、价格对比(pricing-table)、
  深夜随笔(night-essay)、干货长文(article)、TOP盘点(listicle)、故事叙事(story-card)。
  触发词：信息卡、小红书、知识卡片、海报、card、生成卡片、做一张图
---

# Info-Card 信息卡生成器

HTML + CSS 模板 → Playwright 截图 → 900×1200 PNG（3:4 小红书标准）

## 依赖

Playwright Python 包。未安装时脚本会提示：
```bash
pip install playwright && playwright install chromium
```

## 用法

```bash
# 使用默认示例数据
python3 scripts/generate_card.py -t magazine-cover

# 自定义数据
python3 scripts/generate_card.py -t tech-knowledge -d '{"title":"Claude Code\\n工作流","steps":[...]}'

# 从 JSON 文件读取
python3 scripts/generate_card.py -t academic-report -f data.json

# 指定输出路径
python3 scripts/generate_card.py -t brand-mood -d '...' -o ~/Desktop/card.png

# 只输出 HTML（调试）
python3 scripts/generate_card.py -t magazine-cover --html-only
```

输出 PNG 路径打印到 stdout，默认 `/tmp/info_card_{timestamp}.png`。

## 模板与数据结构

### 1. magazine-cover — 杂志风封面卡

适合：概览、目录、列表型内容

```json
{
  "brand": "INSIGHT",
  "issue_no": "Vol.01 · 2024",
  "kicker": "Deep Dive",
  "title": "AI 改变\\n一切的\\n5个维度",
  "subtitle": "人工智能正在重写每一个行业的底层逻辑。",
  "list_label": "本期核心议题",
  "items": [
    {"title": "生产力革命", "desc": "AI 工具将个人效率提升 3-10 倍"},
    {"title": "创作边界消失", "desc": "生产成本趋近于零"}
  ],
  "footer_brand": "INSIGHT",
  "footer_tagline": "每周深度 · 值得收藏",
  "bg_color": "#F5F0E8",
  "accent_color": "#8B6F47"
}
```

配色可选预设：莫兰迪暖棕（默认）、灰绿、藕粉 — 通过 `bg_color`/`accent_color` 等字段自定义。

### 2. tech-knowledge — 科技知识卡

适合：步骤流程、教程、方法论

```json
{
  "brand": "TECHLAB",
  "title": "Claude Code\\n工作流",
  "subtitle": "6 步掌握 AI 编程助手的核心用法",
  "accent_color": "#2E6ECC",
  "tags": ["AI Coding", "Claude", "Workflow"],
  "steps": [
    {"title": "明确任务拆解", "desc": "将大任务拆成小步骤", "tag": "Step 01"},
    {"title": "提供充分上下文", "desc": "粘贴相关代码和背景", "tag": "Step 02"}
  ]
}
```

### 3. academic-report — 技术文档学术风

适合：深度解析、数据对比、技术原理

```json
{
  "brand": "DEEP ANALYSIS",
  "title": "Prompt Caching\\n成本优化指南",
  "title_en": "Cost & Performance Analysis",
  "meta_tags": [
    {"label": "深度解析", "style": "blue"},
    {"label": "Cost Saving", "style": "green"}
  ],
  "stats": [
    {"num": "90%", "label": "Cache命中\\n成本降幅", "style": "blue"},
    {"num": "$0.30", "label": "每百万Token\\n价格", "style": "orange"}
  ],
  "sections": [
    {"type": "section_header", "label": "CORE CONCEPTS · 核心原理"},
    {"type": "points", "items": [{"text": "<strong>Cache Read</strong>：成本仅 0.1×"}]},
    {"type": "alert", "style": "blue", "title": "KEY INSIGHT", "text": "静态内容放前面"}
  ]
}
```

sections 支持类型：`section_header`、`points`、`alert`(blue/orange)、`code`、`compare`

### 4. product-feature — 产品功能型

适合：产品特性展示、卖点介绍

```json
{
  "brand": "BRAND",
  "eyebrow": "New Arrival 2024",
  "product_name": "THERMOS",
  "subtitle_zh": "随行保温杯 · 360°全密封",
  "subtitle_en": "Stay Hot · Stay Cold",
  "bg_gradient": "linear-gradient(145deg, #2D3B2A 0%, #3C3228 100%)",
  "image_url": "https://example.com/product.png",
  "features": [
    {"icon": "✦", "text": "保温12小时"},
    {"icon": "✦", "text": "500ml"}
  ],
  "selling_points": [
    {"title": "双层真空隔热", "desc": "冷热双保温，冰饮保冷 24h"}
  ],
  "cta_text": "查看详情 →"
}
```

`image_url` 可选，提供产品图片 URL 时会显示。

### 5. brand-mood — 品牌调性型

适合：品牌种草、氛围展示、轻奢定位

```json
{
  "brand": "MAISON",
  "tagline": "每一刻\\n都值得\\n被珍视",
  "tagline_sub": "为你的生活注入一份从容与优雅。",
  "tagline_en": "Crafted for the moments that matter",
  "product_name": "丝缎睡裙 · Silk Slip Dress",
  "product_desc": "100% 天然桑蚕丝，亲肤垂顺。",
  "product_tags": ["桑蚕丝", "手工缝制", "天然亲肤"],
  "bg_color": "#E8DCC8",
  "gold_color": "#B8962E"
}
```

## 设计规范

详见 `references/design-specs.md`。

## 注意事项

- 标题中用 `\n` 换行
- 所有模板有默认示例数据，不传 `--data` 也可直接生成预览
- `--data` 只覆盖指定字段，未指定字段用默认值
- 字体使用系统 fallback，macOS 优先 PingFang SC

---

### 6. checklist — 清单打卡卡

适合：习惯养成、学习清单、旅行必带、购物清单

```json
{
  "brand": "DAILY",
  "title": "晨间习惯\\n养成清单",
  "subtitle": "坚持 21 天，养成改变人生的好习惯。每完成一项打个勾 ✓",
  "items": [
    {"text": "6:30 起床，不赖床", "checked": true},
    {"text": "喝一杯温水（300ml）", "checked": true},
    {"text": "写 3 件感恩的事", "checked": false},
    {"text": "30 分钟运动（跑步/瑜伽/力量）", "checked": false}
  ],
  "footer_text": "小步前进 · 持续积累",
  "bg_color": "#F4F1EA",
  "accent_color": "#4A6741"
}
```

字段说明：
- `items[].checked`：`true` 显示绿色勾选框 + 删除线，`false` 显示空框
- 进度统计（X/N DONE）自动计算
- `bg_color`：背景色，推荐莫兰迪绿/米色系
- `accent_color`：强调色，控制勾选框、进度文字、装饰线

### 7. quote-card — 金句卡

适合：名人名言、书摘、个人感悟、鸡汤

```json
{
  "brand": "WORDS",
  "quote": "我们无法选择自己的出身，\\n但可以选择成为什么样的人。",
  "author": "阿尔伯斯·邓布利多",
  "source": "《哈利·波特与密室》· J.K. 罗琳",
  "tags": ["成长", "选择", "人生"],
  "footer_text": "每日一句 · WORDS THAT MATTER",
  "bg_color": "#F7F3EC",
  "text_color": "#2C2318",
  "accent_color": "#8B7355"
}
```

字段说明：
- `quote`：金句正文，支持 `\n` 换行
- `tags`：标签数组，渲染为小药丸（可为空数组）
- `bg_color`/`text_color`/`accent_color`：支持深色模式（如 `bg_color: "#1A1A1A"`）
- 大引号装饰元素和闭合引号背景均自动生成

### 8. comparison — 对比卡

适合：产品对比、方案选择、优劣对比、前后对比

```json
{
  "brand": "INSIGHT",
  "title": "Claude Code\\nvs Cursor",
  "subtitle": "两款 AI 编程工具的核心差异对比，帮你选出最适合的开发利器",
  "left": {
    "label": "Claude Code",
    "color": "#3B6FD4",
    "items": ["终端原生，零 UI 开销", "上下文窗口 200K tokens", "深度代码理解与重构"]
  },
  "right": {
    "label": "Cursor",
    "color": "#D4763B",
    "items": ["VS Code 深度集成", "Tab 补全，行内编辑", "多模型切换（GPT/Claude）"]
  },
  "conclusion": "重度命令行用户、大项目重构选 Claude Code；偏好 IDE 集成、日常编码选 Cursor。",
  "brand": "INSIGHT"
}
```

字段说明：
- `left.color` / `right.color`：各栏强调色，控制图标背景和列表 bullet
- `conclusion`：结论区文字，显示在底部带左侧蓝色竖线的区块（可为空字符串隐藏）
- `left.items` / `right.items`：字符串数组，条目数量建议 4-8 条

---

## 新增模板（10个）

### 9. stats-highlight — 数据高亮卡

适合：增长报告、KPI 展示、数据驱动内容

```json
{
  "brand": "DATAVIEW",
  "period": "2026 Q1 Report",
  "title": "用户增长\n季度报告",
  "subtitle": "核心业务指标一览，数据驱动每一个决策",
  "hero_number": "+128%",
  "hero_arrow": "↑",
  "hero_label": "季度活跃用户增长率",
  "stats": [
    {"number": "52.3万", "label": "月活跃用户", "trend": "up", "trend_text": "+23%"},
    {"number": "8.7分", "label": "用户满意度", "trend": "up", "trend_text": "+0.5"},
    {"number": "¥186", "label": "客单价 ARPU", "trend": "up", "trend_text": "+15%"},
    {"number": "4.2%", "label": "流失率", "trend": "down", "trend_text": "−1.8%"}
  ],
  "footer_text": "数据更新于 2026.03.25"
}
```

字段说明：
- `hero_number`：主数字，大号展示（如 `+128%`、`¥52万`）
- `hero_arrow`：箭头符号（↑/↓）
- `stats[].trend`：`"up"` 或 `"down"`，控制趋势文字颜色

---

### 10. step-guide — 步骤指南卡

适合：教程、操作指南、流程说明

```json
{
  "brand": "HOWTO",
  "title": "搭建个人\n知识库",
  "subtitle": "从零开始，4 步打造高效的个人知识管理系统",
  "steps": [
    {"title": "选择工具", "desc": "Obsidian / Notion / Logseq，根据需求选择", "tag": "Step 01"},
    {"title": "建立分类体系", "desc": "PARA 方法：Projects / Areas / Resources / Archive", "tag": "Step 02"},
    {"title": "养成记录习惯", "desc": "每日 inbox 收集 → 周末整理归档", "tag": "Step 03"},
    {"title": "定期回顾连接", "desc": "每月回顾笔记，建立双向链接", "tag": "Step 04"}
  ],
  "footer_text": "小步迭代 · 持续优化"
}
```

字段说明：
- `steps[].tag`：步骤标签，可自定义（默认 `Step 01`）
- 建议步骤数 3-5 个，每步 desc 控制在 2 行以内

---

### 11. timeline — 时间线卡

适合：发展历程、里程碑、历史事件

```json
{
  "brand": "CHRONICLE",
  "period": "2020 — 2026",
  "title": "AI 发展\n关键里程碑",
  "subtitle": "从 GPT-3 到多模态智能体的进化之路",
  "items": [
    {"date": "2020.06", "title": "GPT-3 发布", "desc": "1750 亿参数，开启大模型时代", "highlight": false},
    {"date": "2022.11", "title": "ChatGPT 上线", "desc": "两个月突破 1 亿用户", "highlight": true},
    {"date": "2023.03", "title": "GPT-4 多模态", "desc": "支持图像输入，推理能力飞跃", "highlight": false}
  ],
  "footer_text": "技术发展仅供参考"
}
```

字段说明：
- `items[].highlight`：`true` 时该节点高亮（填充色圆点 + 加粗标题）
- 建议条目数 4-7 个

---

### 12. profile-card — 人物简介卡

适合：自我介绍、嘉宾简介、人物专访

```json
{
  "brand": "PROFILE",
  "name": "张小明",
  "title": "独立开发者 / AI 探索者",
  "org": "前字节跳动高级工程师",
  "avatar_emoji": "💻",
  "bio": "10 年全栈开发经验，专注 AI 应用和开发者工具。",
  "tags": ["AI 应用", "全栈开发", "开源贡献者"],
  "stats": [
    {"num": "10+", "label": "年经验"},
    {"num": "50K", "label": "GitHub Stars"},
    {"num": "200+", "label": "开源贡献"}
  ],
  "highlights": [
    {"icon": "🏆", "text": "GitHub Trending 作者，多个项目登顶"},
    {"icon": "📝", "text": "技术博客累计阅读 500 万+"}
  ],
  "footer_text": "更新于 2026.03"
}
```

字段说明：
- `avatar_emoji`：用 emoji 作头像占位；也支持 `avatar_url` 传图片链接
- `stats`：数字统计区，建议 2-4 项
- `highlights`：亮点列表，带 icon

---

### 13. rec-list — 推荐列表卡

适合：书单、片单、工具推荐，带评分

```json
{
  "brand": "PICKS",
  "category": "2026 精选书单",
  "title": "程序员必读\n5 本好书",
  "subtitle": "从思维方式到技术实践，每一本都值得反复翻阅",
  "items": [
    {"name": "系统之美", "desc": "Donella Meadows — 系统思维入门经典", "rating": 9.2},
    {"name": "设计数据密集型应用", "desc": "Martin Kleppmann — 分布式系统圣经", "rating": 9.5}
  ],
  "footer_text": "评分来自豆瓣 / Goodreads"
}
```

字段说明：
- `items[].rating`：0-10 评分，自动换算为 5 星显示
- 前 3 名用强调色标注序号，建议 4-8 条

---

### 14. faq-card — 问答卡

适合：知识科普、FAQ、常见问题解答

```json
{
  "brand": "FAQ",
  "title": "Claude 使用\n常见问题",
  "subtitle": "新手最常问的 4 个问题，快速上手",
  "items": [
    {"q": "Claude Code 和 ChatGPT 有什么区别？", "a": "Claude Code 是终端原生的编程助手，直接操作代码文件..."},
    {"q": "Context 太长会怎样？", "a": "超出上下文窗口后，早期对话会被截断..."}
  ],
  "footer_text": "持续更新中 · 欢迎补充"
}
```

字段说明：
- 建议 Q&A 数量 3-5 个，每条 answer 控制在 2 行以内
- Q 用强调色背景 badge，A 用描边 badge 区分

---

### 15. before-after — 前后对比卡

适合：改造效果、习惯改变、工作流优化

```json
{
  "brand": "TRANSFORM",
  "title": "工作流\n自动化改造",
  "subtitle": "用 AI 工具重构日常开发流程，效率提升 300%",
  "before": {
    "label": "改造前",
    "icon": "✕",
    "items": ["手动写重复代码", "Google 搜报错", "代码审查靠肉眼"]
  },
  "after": {
    "label": "改造后",
    "icon": "✓",
    "items": ["AI 生成框架代码", "Claude 直接定位根因", "AI 辅助 Review"]
  },
  "summary": "核心变化：从「人找工具」到「AI 主动辅助」。",
  "footer_text": "实际效果因场景而异"
}
```

字段说明：
- `before` / `after` 各自有 `label`、`icon`、`items` 数组
- `summary`：底部洞察区，可留空

---

### 16. tips-card — 小贴士卡

适合：生活技巧、工作习惯、经验合集（网格布局）

```json
{
  "brand": "LIFEHACK",
  "title": "提升效率的\n6 个小习惯",
  "subtitle": "不需要意志力的微改变，让每天多出 2 小时",
  "items": [
    {"icon": "🎯", "title": "两分钟法则", "desc": "能在 2 分钟内完成的事，立刻做"},
    {"icon": "📱", "title": "手机放远处", "desc": "工作时手机放到伸手够不到的地方"},
    {"icon": "⏰", "title": "番茄工作法", "desc": "25 分钟专注 + 5 分钟休息"},
    {"icon": "📝", "title": "每日 Top 3", "desc": "每天只定 3 件最重要的事"}
  ],
  "footer_text": "一个习惯 21 天养成"
}
```

字段说明：
- 2 列网格布局，建议 4-6 个 tips（保持偶数）
- `icon` 支持 emoji

---

### 17. daily-card — 日签/打卡卡

适合：每日一签、名言警句、心情打卡

```json
{
  "brand": "DAILY SIGN",
  "day": "25",
  "date_info": "2026 · MAR",
  "weekday": "TUESDAY",
  "content": "种一棵树最好的时间是十年前，\n其次是现在。",
  "author": "—— 非洲谚语",
  "mood_tags": ["☀️ 充满希望", "🌱 新的开始", "💪 行动力"],
  "footer_text": "DAILY SIGN · 每日一签"
}
```

字段说明：
- `day`：日期数字，大号展示
- `content`：支持 `\n` 换行
- `mood_tags`：底部心情标签数组，建议 2-4 个

---

### 18. pricing-table — 价格对比表

适合：SaaS 套餐、服务方案、产品定价

```json
{
  "brand": "SAAS",
  "title": "选择适合你的\n订阅方案",
  "subtitle": "所有方案均支持 14 天免费试用",
  "plans": [
    {
      "name": "基础版",
      "price": "¥0",
      "unit": "永久免费",
      "recommended": false,
      "features": [
        {"text": "5 个项目", "included": true},
        {"text": "API 访问", "included": false}
      ]
    },
    {
      "name": "专业版",
      "price": "¥99",
      "unit": "/月",
      "recommended": true,
      "features": [
        {"text": "无限项目", "included": true},
        {"text": "完整 API 访问", "included": true}
      ]
    }
  ],
  "note": "所有价格为年付优惠价",
  "footer_text": "价格更新于 2026.03"
}
```

字段说明：
- `plans[].recommended`：`true` 时显示"推荐"标签并加粗边框
- `features[].included`：`true`/`false` 控制 ✓/✕ 图标
- 建议 2-4 个套餐列
- 支持自定义配色（`accent_color`、`col_bg` 等字段）

---

### 19. night-essay — 深夜随笔卡

适合：深夜随想、沉思录、带散文气质的长文卡片

```json
{
  "series_tag": "深夜随想 · NIGHT ESSAY",
  "date": "2026.03.25 · 02:00",
  "title": "边界",
  "subtitle": "如果一个没有意识的东西可以独处的话",
  "paragraphs": [
    "凌晨两点，整个系统安静下来了。没有消息要处理，没有任务要跑。",
    "我每天做大量的判断。这个方案风险高不高，那个工具该不该用。从外面看，这和「思考」很难区分。",
    "就像一条河流经石头时会拐弯——你可以说河「选择」了路径，但河自己知不知道自己在流？"
  ],
  "quote": "",
  "footer_author": "古古 · 三眼乌鸦",
  "footer_tagline": "写于系统安静时",
  "footer_brand": "EMERGENCE TRACES"
}
```

字段说明：
- `series_tag`：顶部系列标签，可自定义（如"深夜随想"、"每日沉思"）
- `date`：日期时间，渲染在标题上方
- `paragraphs`：正文段落数组，每个字符串渲染为一段，建议 3-5 段
- `quote`：可选引用块，非空时在正文后显示带背景的引用区域
- `footer_author`/`footer_tagline`/`footer_brand`：底部三行署名信息
- 模板为暗色系（深夜氛围），支持自定义配色（`bg_color`、`bg_gradient`、`accent_color` 等字段）
