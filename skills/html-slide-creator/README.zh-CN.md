# slide-creator

> 很多人有很好的内容，却无法有效地展现。虽然大模型现在能帮你写 PPT，但输出效果不稳定，多次抽卡又很头疼。Slide-Creator 帮助你简单、稳定地输出演示文稿——根据场景选择喜欢的风格即可，其他的就让大模型去干，喝杯咖啡吧 ☕

适用于 [Claude Code](https://claude.ai/claude-code) 和 [OpenClaw](https://openclaw.ai) 的演示文稿生成 skill，零依赖、纯浏览器运行的 HTML 幻灯片。

**v1.9.0** — 21 种设计预设，每种风格包含命名布局变体；新增内容类型 → 风格智能路由；视觉节奏规则让幻灯片层次更分明；语言自动检测；两款全新风格：**Modern Newspaper**（报纸编辑风）和 **Neo-Retro Dev Deck**（复古工程师风）。演讲者模式（`P` 键）、内联 SVG 图表、自定义主题系统（`themes/` 目录）。PPTX 导出通过 Playwright + 系统 Chrome，无需 Node.js。

[English](README.md) | 简体中文

## 效果演示

用浏览器直接打开，零安装查看效果：

- 🇨🇳 [slide-creator 介绍（中文）](https://kaisersong.github.io/slide-creator/demos/intro-zh.html) — 功能和使用方式介绍
- 🇺🇸 [slide-creator intro (English)](https://kaisersong.github.io/slide-creator/demos/intro-en.html) — same in English

以上两个演示使用 Blue Sky 风格。点击下方任意截图可打开对应的在线演示：

<table>
<tr>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/intro-zh.html"><img src="demos/screenshots/blue-sky.png" width="240" alt="Blue Sky"/><br/><b>Blue Sky</b> ✨</a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/bold-signal.html"><img src="demos/screenshots/bold-signal.png" width="240" alt="Bold Signal"/><br/><b>Bold Signal</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/electric-studio.html"><img src="demos/screenshots/electric-studio.png" width="240" alt="Electric Studio"/><br/><b>Electric Studio</b></a></td>
</tr>
<tr>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/creative-voltage.html"><img src="demos/screenshots/creative-voltage.png" width="240" alt="Creative Voltage"/><br/><b>Creative Voltage</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/dark-botanical.html"><img src="demos/screenshots/dark-botanical.png" width="240" alt="Dark Botanical"/><br/><b>Dark Botanical</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/notebook-tabs.html"><img src="demos/screenshots/notebook-tabs.png" width="240" alt="Notebook Tabs"/><br/><b>Notebook Tabs</b></a></td>
</tr>
<tr>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/pastel-geometry.html"><img src="demos/screenshots/pastel-geometry.png" width="240" alt="Pastel Geometry"/><br/><b>Pastel Geometry</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/split-pastel.html"><img src="demos/screenshots/split-pastel.png" width="240" alt="Split Pastel"/><br/><b>Split Pastel</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/vintage-editorial.html"><img src="demos/screenshots/vintage-editorial.png" width="240" alt="Vintage Editorial"/><br/><b>Vintage Editorial</b></a></td>
</tr>
<tr>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/neon-cyber.html"><img src="demos/screenshots/neon-cyber.png" width="240" alt="Neon Cyber"/><br/><b>Neon Cyber</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/terminal-green.html"><img src="demos/screenshots/terminal-green.png" width="240" alt="Terminal Green"/><br/><b>Terminal Green</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/swiss-modern.html"><img src="demos/screenshots/swiss-modern.png" width="240" alt="Swiss Modern"/><br/><b>Swiss Modern</b></a></td>
</tr>
<tr>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/paper-ink.html"><img src="demos/screenshots/paper-ink.png" width="240" alt="Paper &amp; Ink"/><br/><b>Paper &amp; Ink</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/aurora-mesh.html"><img src="demos/screenshots/aurora-mesh.png" width="240" alt="Aurora Mesh"/><br/><b>Aurora Mesh</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/enterprise-dark.html"><img src="demos/screenshots/enterprise-dark.png" width="240" alt="Enterprise Dark"/><br/><b>Enterprise Dark</b></a></td>
</tr>
<tr>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/glassmorphism.html"><img src="demos/screenshots/glassmorphism.png" width="240" alt="Glassmorphism"/><br/><b>Glassmorphism</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/neo-brutalism.html"><img src="demos/screenshots/neo-brutalism.png" width="240" alt="Neo-Brutalism"/><br/><b>Neo-Brutalism</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/chinese-chan.html"><img src="demos/screenshots/chinese-chan.png" width="240" alt="Chinese Chan"/><br/><b>Chinese Chan</b></a></td>
</tr>
<tr>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/data-story.html"><img src="demos/screenshots/data-story.png" width="240" alt="Data Story"/><br/><b>Data Story</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/intro-modern-newspaper.html"><img src="demos/screenshots/modern-newspaper.png" width="240" alt="Modern Newspaper"/><br/><b>Modern Newspaper</b></a></td>
<td align="center"><a href="https://kaisersong.github.io/slide-creator/demos/intro-neo-retro-dev.html"><img src="demos/screenshots/neo-retro-dev.png" width="240" alt="Neo-Retro Dev Deck"/><br/><b>Neo-Retro Dev Deck</b></a></td>
</tr>
</table>

所有演示文稿内容相同（均为 slide-creator 自我介绍），方便直观感受不同设计哲学的视觉差异。

---

## 功能特性

- **两阶段工作流** — `--plan` 生成大纲，`--generate` 输出幻灯片
- **21 种设计预设** — Bold Signal、Blue Sky、Modern Newspaper、Neo-Retro Dev Deck 等，每种风格含命名布局变体
- **内容类型智能路由** — 根据路演、开发工具、数据报告、编辑内容等自动推荐最匹配的风格
- **视觉风格探索** — 先生成 3 个预览，看图选风格而非描述风格
- **演讲者模式** — 按 `P` 打开同步演讲者窗口：备注、计时器、页数、翻页导航；窗口高度随备注自动调整
- **备注编辑面板** — 编辑模式（`E` 键）下底部出现备注栏，点击标题可收起/展开，输入实时同步到演讲者窗口
- **内联 SVG 图表** — 流程图、时间轴、条形图、对比矩阵、组织架构图，无需 Mermaid.js 或外部库
- **自定义主题系统** — 在 `themes/你的主题/` 放入 `reference.md` 即可添加专属设计预设；可选提供 `starter.html`
- **Blue Sky Starter 模板** — 完整 boilerplate，任何模型都能正确实现全套视觉系统
- **图片处理流水线** — 自动评估和处理素材（Pillow）
- **PPT 导入** — 将 `.pptx` 文件转换为网页演示
- **PPTX 导出** — `--export pptx`，通过 Playwright + 系统 Chrome 导出
- **浏览器内编辑** — 直接在浏览器中编辑文字，Ctrl+S 保存
- **视口自适应** — 每张幻灯片精确填充 100vh，永不出现滚动条
- **中英双语** — 完整支持中文内容

---

## 安装

### Claude Code

```bash
git clone https://github.com/kaisersong/slide-creator ~/.claude/skills/slide-creator
```

重启 Claude Code，使用 `/slide-creator` 调用。

### OpenClaw

```bash
# 通过 ClawHub 安装（推荐）
clawhub install html-slide-creator

# 或手动克隆
git clone https://github.com/kaisersong/slide-creator ~/.openclaw/skills/slide-creator
```

> ClawHub 页面：https://clawhub.ai/skills/html-slide-creator

OpenClaw 首次使用时会自动安装依赖（Pillow、python-pptx、playwright）。

---

## 使用方法

```
/slide-creator --plan       # 分析内容和 resources/ 目录，生成 PLANNING.md 大纲
/slide-creator --generate   # 根据 PLANNING.md 生成 HTML 演示文稿
/slide-creator --export pptx  # 导出为 PowerPoint
/slide-creator              # 从零开始（交互式风格探索）
```

### 典型工作流

**方式一：交互式创建**
1. 运行 `/slide-creator`，回答目的、长度、内容和图片四个问题
2. 查看 3 个风格预览，选择喜欢的风格
3. 生成完整演示文稿，在浏览器中打开

**方式二：两阶段工作流（复杂内容推荐）**
1. 在项目目录放入素材（`resources/` 文件夹）
2. 运行 `/slide-creator --plan 我的AI创业公司融资路演`
3. 审阅 `PLANNING.md` 大纲，确认后运行 `/slide-creator --generate`

**方式三：PPT 转换**
1. 将 `.pptx` 文件放到当前目录
2. 运行 `/slide-creator`，Skill 会自动识别并提取内容

---

## 依赖要求

| 依赖 | 用途 | OpenClaw 自动安装 |
|------|------|------------------|
| Python 3 + `Pillow` | 图片处理 | ✅ via uv |
| Python 3 + `python-pptx` | PPT 导入/导出 | ✅ via uv |
| Python 3 + `playwright` | PPTX 导出（使用系统 Chrome） | ✅ via uv |

不再需要 Node.js。PPTX 导出使用你已安装的 Chrome/Edge/Brave，无需下载 300MB 的 Chromium。

**Claude Code 用户** 需手动安装：
```bash
pip install Pillow python-pptx playwright
```

---

## 输出文件

- `presentation.html` — 零依赖单文件，直接用浏览器打开
- `PRESENTATION_SCRIPT.md` — 演讲稿（幻灯片 8 张以上时自动生成）
- `*.pptx` — 通过 `--export pptx` 导出

---

## 浏览器内编辑

生成的演示文稿内置文字编辑功能，无需修改 HTML 源码。

**进入编辑模式：**

- 将鼠标移到屏幕**左上角** → 出现编辑按钮，点击即可
- 或直接按键盘 **`E`** 键

**编辑模式下：**

- 点击幻灯片上的任意文字，直接修改
- **底部备注栏** — 可编辑当前幻灯片的演讲备注；点击标题栏中央横线可收起/展开，避免遮挡内容
- **`Ctrl+S`**（Mac 上为 `Cmd+S`）— 保存所有修改（包括备注）到 HTML 文件
- **`Escape`** — 退出编辑模式，不保存

**如何开启：** 在 slide-creator 生成时，选择启用「浏览器内编辑」（默认推荐开启）。如果之前没有选，重新执行 `/slide-creator --generate` 并选择开启即可。

## 演讲者模式

按 **`P`** 键打开演讲者窗口，包含：

- 当前幻灯片备注（可在编辑模式下实时修改并同步）
- 已用时计时器
- 当前页 / 总页数
- 上一张 / 下一张导航

---

## 设计预设

| 预设 | 风格 | 适合场景 |
|------|------|----------|
| **Bold Signal** | 自信、强冲击 | 路演、主题演讲 |
| **Electric Studio** | 简洁、专业 | 商务演示 |
| **Creative Voltage** | 活力、复古现代 | 创意提案 |
| **Dark Botanical** | 优雅、精致 | 高端品牌 |
| **Blue Sky** ✨ | 清透、企业 SaaS | 产品发布、科技路演 |
| **Notebook Tabs** | 编辑感、有条理 | 报告、评审 |
| **Pastel Geometry** | 友好、亲切 | 产品介绍 |
| **Split Pastel** | 活泼、现代 | 创意机构 |
| **Vintage Editorial** | 个性鲜明 | 个人品牌 |
| **Neon Cyber** | 科技感、未来感 | 科技创业 |
| **Terminal Green** | 开发者风格 | 开发工具、API |
| **Swiss Modern** | 极简、精确 | 企业、数据 |
| **Paper & Ink** | 文学、沉思 | 叙事演讲 |
| **Aurora Mesh** | 鲜明、高端 SaaS | 产品发布、VC 融资路演 |
| **Enterprise Dark** | 权威、数据驱动 | B2B、投资者 deck、战略 |
| **Glassmorphism** | 轻盈、毛玻璃、现代 | 消费科技、品牌发布 |
| **Neo-Brutalism** | 大胆、不妥协 | 独立开发者、创意宣言 |
| **Chinese Chan** | 静谧、沉思 | 设计哲学、品牌、文化 |
| **Data Story** | 清晰、精确、说服力 | 业务回顾、KPI、数据分析 |
| **Modern Newspaper** | 犀利、权威、编辑感 | 业务报告、思想领导力演讲 |
| **Neo-Retro Dev Deck** | 有主见、技术感、手作风 | 开发工具发布、API 文档、黑客松 |

### Blue Sky

天空渐变背景（`#f0f9ff → #e0f2fe`）搭配浮动玻璃拟态卡片与动态环境光球。灵感来自真实的企业 AI 路演文稿（CloudHub V12 MVP），呈现出高空晴日般开阔、自信、精致的视觉气质。

标志性元素：SVG 颗粒噪声纹理叠层 · 3 个按幻灯片类型重新布阵的模糊光球 · `backdrop-filter: blur(24px)` 玻璃拟态卡片 · 40px 科技网格底层 · 弹簧物理横向切换动画 · 封面专属双层流动云朵效果。

附带完整 starter 模板（`references/blue-sky-starter.html`）—— 全部 10 个签名视觉元素预置完毕，模型只需填充幻灯片内容即可。

---

## 兼容性

| 平台 | 版本 | 安装路径 |
|------|------|----------|
| Claude Code | 任意 | `~/.claude/skills/slide-creator/` |
| OpenClaw | ≥ 0.9 | `~/.openclaw/skills/slide-creator/` |
