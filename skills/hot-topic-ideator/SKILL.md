---
name: hot-topic-ideator
description: 生成小红书热点选题和内容创意。当用户提到"热点选题"、"内容创意"、"小红书选题"、"trending topics"、"content ideas"、"热门话题"、"爆款选题"时使用。适用于品牌社媒运营、内容策划、热点借势营销场景。
metadata: {"clawdbot":{"emoji":"🔥","requires":{"bins":["uv"]},"install":[{"id":"uv-brew","kind":"brew","formula":"uv","bins":["uv"],"label":"Install uv (brew)"}]}}
---

# 热点选题生成器 (Hot Topic Content Ideator)

基于小红书真实数据，为品牌生成5-10个高质量热点选题创意，输出为专业 HTML 报告并转换为 PDF。

## 快速开始

**使用示例：**
```
用户：帮雪碧生成小红书热点选题
用户：给元气森林做5个内容创意
用户：为喜茶策划热点借势内容
```

## 环境配置

### 必需的环境变量
```bash
export CHATDAM_API_TOKEN="YOUR_TOKEN_HERE"
```

## 工作流程

### Step 1: 品牌信息收集

**若用户只提供品牌名称，需收集以下信息：**

1. **品牌核心价值观** - 品牌代表什么？
2. **目标受众** - 主要消费群体特征
3. **应用场景** - 产品典型使用场景
4. **品牌调性** - 活泼/专业/高端/亲民等
5. **竞品品牌** - 主要竞争对手（用于差异化分析）

**若用户已提供详细信息，直接进入Step 2。**

---

### Step 2: 生成搜索关键词

基于品牌DNA，生成5-8个搜索关键词：

**关键词公式：**

| 类型 | 公式 | 示例 |
|------|------|------|
| 品牌+品类 | [品牌名] [产品类型] | 雪碧 气泡水 |
| 品牌+场景 | [品牌名] [使用场景] | 雪碧 火锅 |
| 品牌+情绪 | [品牌名] [情感词] | 雪碧 爽快 |
| 品类+热点 | [品类] [潜在热词] | 碳酸饮料 搞抽象 |
| 场景+趋势 | [消费场景] [流行词] | 聚餐 氛围感 |

**输出：** 5-8个关键词列表

---

### Step 3: 搜索小红书笔记

**对每个关键词调用API：**

```bash
curl --request GET 'https://asset.tezign.com/chatdam/api/notes/search?keyword=[KEYWORD_URL_ENCODED]' \
--header "Authorization: Bearer ${CHATDAM_API_TOKEN}" \
--header 'Content-Type: application/json'
```

**响应结构：**
```json
{
  "data": {
    "keyword": "雪碧 火锅",
    "notes": [
      {
        "noteId": "69800480000000000e03c5b1",
        "title": "火锅配雪碧太爽了",
        "description": "辣到飞起的时候来一口冰爽雪碧 #火锅 #雪碧 #聚餐",
        "likedCount": 1205,
        "commentCount": 43,
        "collectedCount": 89,
        "sharedCount": 12
      }
    ],
    "total": 20
  }
}
```

**数据处理：**

为每篇笔记计算互动分数：
```
engagement_score = likedCount + (commentCount × 2) + (collectedCount × 3) + (sharedCount × 1.5)
```

**从description中提取话题标签（#xxx格式）**

---

### Step 4: 获取热门笔记详情

**对每个关键词的前3篇高互动笔记，获取详情：**

```bash
curl --request GET 'https://asset.tezign.com/chatdam/api/notes/detail?noteId=[NOTE_ID]' \
--header "Authorization: Bearer ${CHATDAM_API_TOKEN}"
```

**分析要点：**

1. **内容结构**
   - 开头钩子（如何吸引注意）
   - 主体内容（信息传递方式）
   - 结尾CTA（互动引导）

2. **话题策略**
   - 主话题（高流量）
   - 副话题（精准定位）
   - 品牌话题（转化追踪）

3. **成功要素**
   - 情绪触发点
   - 用户价值点
   - 可分享性

---

### Step 5: 话题挖掘与评估

**汇总所有提取的话题标签，计算得分：**

```
话题得分 = (出现频次 × 0.4) + (关联笔记平均互动 × 0.6)
```

**筛选Top 10话题，评估维度：**

| 维度 | 权重 | 评分标准 |
|------|------|----------|
| 品牌相关性 | 30% | 与品牌价值观/场景的契合度 |
| 用户互动量 | 25% | 关联笔记的平均互动表现 |
| 内容可复制性 | 20% | 品牌执行的难易程度 |
| 趋势热度 | 15% | 话题的增长势头 |
| 竞品空白度 | 10% | 竞品是否已切入 |

---

### Step 6: 热榜验证

**调用官方热榜API验证话题热度：**

```bash
curl --request GET 'https://asset.tezign.com/chatdam/api/hot-trends?limit=20' \
--header "Authorization: Bearer ${CHATDAM_API_TOKEN}"
```

**验证结果标记：**

- ✅ **官方热榜验证** - 话题在Top 20热榜中
- 🌱 **新兴趋势** - 话题未上榜但数据强劲
- ⚠️ **小众话题** - 数据一般，需谨慎

---

### Step 7: 深度话题分析（可选）

**对高分话题，以话题为关键词再次搜索：**

```bash
curl --request GET 'https://asset.tezign.com/chatdam/api/notes/search?keyword=%23搞抽象' \
--header "Authorization: Bearer ${CHATDAM_API_TOKEN}"
```

**分析：**
- 话题下的内容主题分布
- 高互动内容的共性特征
- UGC创作模式
- 品牌切入角度

---

### Step 8: 生成热点选题 HTML 报告

**基于前述分析结果，生成专业 HTML 报告，包含5-10个热点选题。**

报告整体结构如下，每个选题需包含完整信息：

1. **报告封面区域**
   - 品牌名称 + "小红书热点选题 Brief"
   - 数据基础概要（搜索关键词数、分析笔记数、提取话题数、热榜验证数）

2. **选题概览表**
   - 表格形式展示所有选题：序号、选题名称、热度等级、执行难度、推荐度

3. **每个选题详情卡片**，包含以下信息：
   - **选题标题**
   - **热点来源**：关联话题标签、热度验证状态（✅官方热榜 / 🌱新兴趋势）、数据支撑
   - **创意概念**：1-2句话核心创意（<30字）
   - **创意阐释**：创意逻辑和品牌结合点（100-150字）
   - **内容形式**：形式（图文/视频/合集）、预估篇幅、参考风格
   - **互动设计**：用户互动引导、评论区玩法
   - **执行要点**：3个关键执行点
   - **参考笔记**：Note ID、互动数据、成功要素

---

## 设计风格

基于品牌属性，为报告选取合适的设计风格。以下为设计框架：

### 核心设计哲学

社媒热点选题报告面向品牌运营团队和决策者，视觉风格需兼顾**数据专业性**和**社交媒体活力感**——既有策略报告的严肃信服力，又有社媒内容的灵动气质。

**设计方向参考**：
- 以杂志编辑式排版为底，融入数据看板的信息密度
- 参考 Monocle 杂志的优雅信息设计 + Spotify 年度报告的活力呈现
- 黑白灰为骨架，品牌色或亮色为点缀，不喧宾夺主

### 设计规范

**色彩策略**：
- 黑、白、灰为基础色系
- 可选单一强调色（如品牌色、亮橙、亮红、深蓝）作为点缀
- 严禁大面积彩色卡片、背景色块、粗彩色边框
- 热度等级可用色阶表示（如灰→深色→强调色），保持克制

**排版层级**：
- 通过字重（Regular → Medium → Bold）建立层级，而非颜色
- 字号标识重要性，留白创造呼吸感
- 中文正文推荐使用系统默认字体，英文/数字可用 Inter / SF Pro 等

**信息密度**：
- 紧凑但不拥挤，确保每屏有足够信息量
- 清晰的视觉分组和适度呼吸空间
- 表格、卡片、列表混合使用，提高扫读效率

## 必须遵循的设计标准

### 【核心设计哲学：Less is More】

用最有力的专业方式呈现最有价值的洞察。报告视觉语言应使用成熟专业的手法（编辑设计、信息图表美学），而非廉价的技术感装饰（霓虹渐变、3D效果、花哨特效）。

**关键原则**：
- 真实而有戏剧性——避免合成塑料感，拥抱有力的视觉呈现
- 力量与深度兼备——视觉冲击力和经得起细看的内涵
- 专业但不疏远——咨询级严谨 + 社媒运营的亲切
- 色彩是戏剧，不是装饰——有目的的戏剧性对比，而非无意义的彩色点缀

**色彩策略**：
- 黑白灰为基底，可选单一强调色（深蓝、炭灰、暖棕、亮橙均可）
- 严禁大面积彩色卡片、背景色块、粗彩色边框
- 克制在于布局和结构，而非把所有东西变灰

**排版层级**：
- 通过字重（Regular → Medium → Bold）建立层级，而非颜色
- 字号表示重要性，留白创造呼吸空间
- 最好的排版应当不被察觉——直到你需要阅读时，感觉毫不费力

**信息密度与阅读效率**：
- 布局紧凑，保证每屏信息量充足——避免过多留白导致"一眼看不到东西"
- 紧凑≠拥挤——保持清晰的视觉分组和适度呼吸空间
- 目标是高阅读效率：读者可快速扫描抓住要点，深入阅读时也感觉舒适
- 段落间距和标题间距适中——层次分明又节省空间

### 【专业标准】
- 报告需体现咨询级专业水准
- 使用社媒运营和品牌策略的标准框架和术语
- 保持客观严谨的分析态度
- 数据引用需标注来源（API数据 / 网络搜索）

### 【内容生成原则】
- 基于真实API数据进行分析和推荐
- 数据不足时使用行业标准假设和经验判断
- 保持逻辑连贯和分析深度
- 所有推论必须有清晰的逻辑支撑和数据佐证

### 【热点选题报告特有设计要求】
- 建立清晰的信息层级：通过字重、字号、衬线/无衬线字体组合区分内容重要性
- 精心安排布局结构：较高信息密度，减少不必要的留白，用精确的分组和对齐突出重点内容
- 表格展示数据对比分析，通过加粗、边框等强调方式突出关键数字和重要发现
- 选题卡片设计统一，便于快速浏览和对比
- 禁止使用超过4种颜色、彩色卡片块、装饰性边框，保持简洁克制的专业美感

### 【视觉内容限制】
- **严禁**：使用图片生成API创建任何图表、表格、数据可视化、统计图、流程图
- **严禁**：使用外部图片链接
- 所有数据可视化通过 HTML/CSS 原生实现（表格、进度条、色阶等）
- 不使用复杂的CSS图表或可视化
- 报告开头不包含日期信息

### 【技术实现】
- 使用 Tailwind CSS（通过 CDN）进行响应式布局
- 优化不同屏幕尺寸的布局
- 所有样式和内容包含在单个 HTML 文件中
- 不使用外部图片链接或资源
- 避免生成无效链接和URL
- 不使用复杂的CSS图表或可视化
- 输出内容仅为可直接使用的 HTML 代码，以 `<!DOCTYPE html>` 开头

---

## API参考

### 1. 笔记搜索
```
GET https://asset.tezign.com/chatdam/api/notes/search?keyword=[ENCODED_KEYWORD]
Header: Authorization: Bearer ${CHATDAM_API_TOKEN}
返回: 20篇笔记，含标题、描述、互动数据
```

### 2. 笔记详情
```
GET https://asset.tezign.com/chatdam/api/notes/detail?noteId=[NOTE_ID]
Header: Authorization: Bearer ${CHATDAM_API_TOKEN}
返回: 完整笔记内容、话题标签、详细数据
```

### 3. 热榜数据
```
GET https://asset.tezign.com/chatdam/api/hot-trends?limit=20
Header: Authorization: Bearer ${CHATDAM_API_TOKEN}
返回: 官方热榜Top20，含热度值和排名变化
```

---

## 最佳实践

### ✅ DO
- 生成多样化关键词，覆盖不同场景
- 分析至少100篇笔记建立数据基础
- 用真实互动数据支撑选题判断
- 提取可复制的内容模板
- 验证热榜确认趋势真实性
- 每个选题提供具体执行指导

### ❌ DON'T
- 不要捏造互动数据
- 不要只依赖热榜（可能与品牌无关）
- 不要提供无法执行的创意
- 不要忽略品牌调性限制
- 不要照搬竞品已做过的内容

---

## 输出格式

### Step 1: 生成 HTML 报告

创建 HTML 报告文件，保存到指定路径：
- 单个 HTML 文件: `{base_dir}/{品牌名}-hot-topics/report.html`

**HTML 报告内容包括：**
1. **报告封面** — 品牌名、报告标题、数据基础概要
2. **选题概览表** — 选题名称、热度等级、执行难度、推荐度
3. **选题详情卡片** — 每个选题的完整 brief（热点来源、创意概念、创意阐释、内容形式、互动设计、执行要点、参考笔记）
4. **数据来源说明** — 搜索关键词、分析笔记数量、数据采集方式

**技术要求：**
- 以 `<!DOCTYPE html>` 开头的完整 HTML 文件
- 使用 Tailwind CSS CDN 进行样式控制
- 单文件，无外部依赖
- 响应式设计，适配不同屏幕

### Step 2: 转换为 PDF

使用转换脚本生成最终 PDF：

```bash
uv run {baseDir}/scripts/html_to_pdf.py --html {base_dir}/{品牌名}-hot-topics/report.html --output {base_dir}/{品牌名}-hot-topics/report.pdf
```

脚本会：
- 正确处理相对图片路径
- 生成专业 PDF
- 打印 `MEDIA:` 行用于自动附件

---

## 错误处理

**API调用失败：**
- 重试1次
- 若仍失败，使用web_search作为备选数据源
- 标注数据来源为"网络搜索（非API）"

**笔记数量不足：**
- 扩展关键词范围
- 降低品牌强关联要求
- 提示用户"该品牌小红书声量较低，建议扩大搜索范围"

**热榜API不可用：**
- 继续基于笔记数据分析
- 标注"热度未经官方验证"

---

## 示例 HTML 结构参考

以下为报告 HTML 的骨架结构示意（实际生成时需填充真实数据和完整样式）：

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>[品牌名] 小红书热点选题 Brief</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <style>
        /* 自定义字体和基础样式 */
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
            background: #fafafa;
            color: #1a1a1a;
        }
        /* 打印优化 */
        @media print {
            body { background: white; }
            .page-break { page-break-before: always; }
        }
    </style>
</head>
<body class="min-h-screen">

    <!-- 封面区域 -->
    <header class="bg-white border-b border-gray-200 px-8 py-12 mb-8">
        <p class="text-sm tracking-widest text-gray-400 uppercase mb-4">Xiaohongshu Content Strategy</p>
        <h1 class="text-4xl font-bold text-gray-900 mb-2">[品牌名]</h1>
        <h2 class="text-xl font-light text-gray-500 mb-8">小红书热点选题 Brief</h2>
        <div class="grid grid-cols-4 gap-6 mt-8">
            <div class="border-l-2 border-gray-900 pl-4">
                <p class="text-2xl font-bold">6</p>
                <p class="text-xs text-gray-500 mt-1">搜索关键词</p>
            </div>
            <div class="border-l-2 border-gray-900 pl-4">
                <p class="text-2xl font-bold">120</p>
                <p class="text-xs text-gray-500 mt-1">分析笔记</p>
            </div>
            <div class="border-l-2 border-gray-900 pl-4">
                <p class="text-2xl font-bold">85</p>
                <p class="text-xs text-gray-500 mt-1">提取话题</p>
            </div>
            <div class="border-l-2 border-gray-900 pl-4">
                <p class="text-2xl font-bold">3</p>
                <p class="text-xs text-gray-500 mt-1">热榜验证</p>
            </div>
        </div>
    </header>

    <!-- 选题概览表 -->
    <section class="bg-white mx-8 mb-8 p-6 border border-gray-100">
        <h3 class="text-lg font-bold text-gray-900 mb-4">选题概览</h3>
        <table class="w-full text-sm">
            <thead>
                <tr class="border-b-2 border-gray-900">
                    <th class="text-left py-2 font-medium">#</th>
                    <th class="text-left py-2 font-medium">选题</th>
                    <th class="text-left py-2 font-medium">热度</th>
                    <th class="text-left py-2 font-medium">执行难度</th>
                    <th class="text-left py-2 font-medium">推荐度</th>
                </tr>
            </thead>
            <tbody>
                <!-- 由实际数据填充 -->
                <tr class="border-b border-gray-100">
                    <td class="py-3 font-bold">1</td>
                    <td class="py-3">选题标题示例</td>
                    <td class="py-3">⭐⭐⭐⭐⭐</td>
                    <td class="py-3">中</td>
                    <td class="py-3">★★★★★</td>
                </tr>
            </tbody>
        </table>
    </section>

    <!-- 选题详情卡片（重复N个） -->
    <section class="mx-8 mb-8">
        <article class="bg-white border border-gray-100 p-6 mb-6">
            <div class="flex items-center justify-between mb-4">
                <h3 class="text-xl font-bold text-gray-900">选题 1: 选题标题</h3>
                <span class="text-xs px-3 py-1 bg-gray-900 text-white">✅ 官方热榜</span>
            </div>

            <div class="grid grid-cols-3 gap-4 mb-4 text-sm">
                <div>
                    <p class="text-gray-400 text-xs mb-1">关联话题</p>
                    <p>#话题1 #话题2 #话题3</p>
                </div>
                <div>
                    <p class="text-gray-400 text-xs mb-1">数据支撑</p>
                    <p>XX篇相关笔记，平均互动XX</p>
                </div>
                <div>
                    <p class="text-gray-400 text-xs mb-1">内容形式</p>
                    <p>图文 / 6张图</p>
                </div>
            </div>

            <div class="mb-4">
                <p class="text-gray-400 text-xs mb-1">创意概念</p>
                <p class="text-lg font-medium">一句话核心创意描述</p>
            </div>

            <div class="mb-4">
                <p class="text-gray-400 text-xs mb-1">创意阐释</p>
                <p class="text-sm text-gray-700 leading-relaxed">详细说明创意逻辑和品牌结合点...</p>
            </div>

            <div class="mb-4">
                <p class="text-gray-400 text-xs mb-1">互动设计</p>
                <p class="text-sm text-gray-700">如何引导用户互动，评论区玩法...</p>
            </div>

            <div class="mb-4">
                <p class="text-gray-400 text-xs mb-1">执行要点</p>
                <ol class="text-sm text-gray-700 list-decimal list-inside space-y-1">
                    <li>关键执行点1</li>
                    <li>关键执行点2</li>
                    <li>关键执行点3</li>
                </ol>
            </div>

            <div class="border-t border-gray-100 pt-3 text-xs text-gray-400">
                参考笔记: Note ID xxx | 互动: xxx | 成功要素: xxx
            </div>
        </article>
    </section>

    <!-- 数据来源说明 -->
    <footer class="mx-8 mb-12 py-4 border-t border-gray-200 text-xs text-gray-400">
        <p>数据来源：小红书笔记搜索API / 官方热榜API | 搜索关键词：xxx, xxx | 分析笔记数：xxx篇</p>
    </footer>

</body>
</html>
```

以上仅为骨架参考，实际生成时需要：
- 根据品牌调性微调强调色
- 填充真实分析数据
- 根据选题数量重复卡片组件
- 确保所有数据引用来自真实API响应
