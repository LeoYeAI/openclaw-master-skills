# Frontend Slides 技能审查报告

> 审查目标：面向**销售与售前技术支持**的解决方案 PPT 制作技能，识别可改进之处。

---

## 一、总体评价

| 维度         | 评价 | 说明 |
|--------------|------|------|
| 功能完整度   | 高   | 新建、PPT 转换、风格探索、视口适配、可编辑模式等覆盖全面 |
| 规范符合度   | 中   | 有 name/description，但描述未体现「解决方案/售前」；正文超 500 行 |
| 受众匹配度   | 中   | 偏通用演示场景，缺少「解决方案 PPT」专用指引与触发词 |
| 可维护性     | 中   | 单文件过长，部分内容可下沉到 reference |

---

## 二、具体改进建议

### 1. Frontmatter 与发现性

**现状：**
- `name: frontend-slides`（与目录名 `frontend-slides-main` 不一致，易混淆）
- `description` 未提及「销售、售前、解决方案、方案书、投标」等触发词

**建议：**
- 在 description 中增加**何时使用**：例如「制作解决方案 PPT、售前方案、投标演示、客户汇报」等，便于在 Cursor/技能列表中命中。
- 可选：若希望与目录一致，可考虑 `name: frontend-slides-main`，或保持 `frontend-slides` 作为规范技能名、在 README 中说明目录为 fork/副本。

### 2. 解决方案 PPT 专项缺失（高优先级）

**现状：**  
技能面向「pitch / teaching / conference / internal」，未单独覆盖**售前解决方案**场景。

**建议：**  
在 Phase 1（Content Discovery）之前或之中，增加「解决方案 PPT」分支：

- **典型结构建议**（供 Agent 引导用户或自动套用）  
  - 封面 / 目录  
  - 客户/项目背景与目标  
  - 痛点与挑战  
  - 解决方案架构/方案概述  
  - 产品/能力与价值（功能、优势）  
  - 案例/标杆客户（可选）  
  - 实施路径/项目计划  
  - 报价/合作方式（可选）  
  - 下一步与联系  

- **风格推荐**  
  对「解决方案/售前」场景推荐偏商务、清晰的 Preset：如 **Swiss Modern**、**Electric Studio**、**Dark Botanical**、**Notebook Tabs** 等，在技能中写一句「售前方案建议使用…」。

- **页数与节奏**  
  可给出建议：例如 10–20 页为常见方案长度，避免一次生成过多页导致内容空洞或过载。

可在 SKILL.md 中新增一小节 **「解决方案 PPT（售前/销售）」**，包含上述结构模板与风格推荐，并在 Phase 0 的 Mode 中增加「解决方案/售前方案」选项。

### 3. 技能体积与渐进式披露（规范建议）

**现状：**  
SKILL.md 约 900+ 行，超出常见规范「主文件建议 <500 行」的推荐。

**建议：**
- 将「CRITICAL: Viewport Fitting」中的**完整 CSS 代码块**移至 `STYLE_PRESETS.md` 或新建 `VIEWPORT_AND_ACCESSIBILITY.md`，在 SKILL.md 中保留规则摘要 + 链接。
- 将 Phase 4（PPT Conversion）的**完整 Python 示例**移至 `reference/ppt-extraction.md` 或类似文件，SKILL.md 只保留步骤与命令/入口说明。
- 动画模式、背景效果等「参考类」内容可保留在 STYLE_PRESETS.md，SKILL.md 只保留「用哪些动画/风格」的决策表。

这样主文件聚焦流程、决策和必须遵守的规则，细节通过引用查阅。

### 4. AskUserQuestion 依赖与兼容性

**现状：**  
Phase 1/2 多处依赖 `AskUserQuestion` 一次性收集目的、页数、内容、图片、风格等。在 Cursor 等环境中该工具可能不存在。

**建议：**
- 在技能开头或 Phase 0 后增加**兼容性说明**：  
  「若当前环境无 AskUserQuestion，则按相同顺序以对话方式逐项询问用户（目的、页数、是否备好内容、图片路径、风格偏好等），并记录答案后再进入下一阶段。」
- 保持「单次表单」为优先路径，但明确降级为「多轮对话」即可，避免 Agent 因缺少工具而卡住。

### 5. 语言与受众

**现状：**  
正文以英文为主，主要用户为**中文销售/售前**。

**建议：**
- 在 README 或 SKILL 顶部增加 1–2 句中文说明：本技能适用于**销售与售前制作解决方案 PPT、客户汇报、投标演示**。
- 可选：在「适用场景」或 description 中增加中文触发词别名（如「解决方案 PPT、售前方案、方案书」），便于中文对话时被命中。

### 6. README 与安装路径

**现状：**  
README 安装路径为 `~/.claude/skills/frontend-slides`（Claude Code）。

**建议：**
- 若技能同时在 **Cursor** 使用，增加一节「Cursor 使用」：  
  将技能放在项目 `.cursor/skills/frontend-slides/` 或用户目录下 Cursor 技能路径，并说明在 Cursor 中通过对话触发（例如「用 frontend-slides 做一份解决方案 PPT」）。
- 保持 Claude Code 的安装说明，两套路径并列即可。

### 7. 其他小点

- **Purpose 选项**：在 Step 1.1 的 Purpose 中增加一项如 **「Solution deck / 解决方案汇报」**，与 Pitch、Teaching、Conference、Internal 并列，便于统计和后续针对该类型做结构建议。
- **STYLE_PRESETS.md**：已存在且被引用，结构清晰；仅需确保 SKILL.md 中「CSS Gotchas」等引用路径正确。
- **依赖说明**：PPT 转换依赖 `python-pptx`，图片处理依赖 `Pillow`，在 README 或技能内「Requirements」中写清，便于售前在本地/服务器环境预装。

---

## 三、建议实施顺序

1. **高优先级（立刻可做）**  
   - 更新 frontmatter 的 **description**，加入「解决方案 PPT、售前方案、销售演示」等触发词。  
   - 在 SKILL 中增加 **「解决方案 PPT」** 小节：典型结构 + 风格推荐 + Purpose 选项。  
   - 增加 **AskUserQuestion 降级说明**（无工具时改为对话式提问）。

2. **中优先级（短期）**  
   - README 增加 **Cursor 使用说明** 与（若适用）中文受众说明。  
   - Purpose 中增加 **Solution deck / 解决方案汇报** 选项。

3. **低优先级（优化）**  
   - 将长 CSS/长代码块移至 reference，**缩短 SKILL.md** 至约 500 行以内。  
   - 统一 name 与目录名或文档说明。

---

## 四、总结

技能本身**能力完整、视口与合规要求清晰**，主要改进空间在于：  
- **定位更清晰**：在 frontmatter 和正文中显式面向「销售/售前」与「解决方案 PPT」。  
- **场景化**：增加解决方案 PPT 的结构模板与风格推荐。  
- **兼容性与可发现性**：AskUserQuestion 降级、中文触发词、Cursor 安装路径。  
- **可维护性**：通过渐进式披露控制主文件长度，便于后续迭代。

按上述顺序实施后，该技能可以更好地服务于「销售和售前技术支持制作解决方案 PPT」这一主场景。

---

## 五、可运行性审查（Runnable Review）

**目标：** 确保技能可被 Agent 正常、有效执行。

### 已修复 / 补充

1. **Phase 1 缺少「获取内容」步骤** — 在 Step 1.1 与 1.2 之间补充：根据用户选择的 Content 类型，在 Phase 2 前必须拿到具体内容（「全部准备好」→ 请用户粘贴或提供文件；「有草稿/只有主题」→ 先帮助整理大纲再逐页内容）。否则 Phase 3 无法生成幻灯片。
2. **Phase 2 直接选风格路径** — 明确 Option B 时需「先询问并展示 preset 列表」，用户点名后再跳到 Phase 3，避免 Agent 不知如何响应「我已知要哪种风格」。
3. **Phase 2 预览目录** — 写明需「创建 `.claude-design/slide-previews/` 目录（若不存在）」，再生成三个预览 HTML。
4. **Phase 3 图片保存与 JS 实现** — 明确「处理后另存为新文件名（如 logo_round.png），不覆盖原文件」；并写明 SlidePresentation 必须实现的行为：键盘/触摸/滚轮、进度条与导航点、Intersection Observer 为 .visible，便于生成完整可用的控制器。
5. **Phase 4 PPT 转换** — 明确调用方式：`extract_pptx(user_pptx_path, output_dir)`，且生成 HTML 时须在**同一 output_dir** 下，保证 `assets/` 与 .html 同目录，引用路径正确。
6. **reference 使用说明** — 在 SKILL 开头增加一句：生成 CSS / 图片处理 / PPT 提取 / HTML 结构 / 编辑按钮 / 动画时，应阅读 `reference/` 下对应文件及 STYLE_PRESETS.md，确保输出正确完整。
7. **reference/ppt-extract.py 健壮性** — 对无 title 占位符的幻灯片做安全判断（`getattr(slide.shapes, "title", None)`），避免提取时报错。

### 验证要点

- 所有 SKILL 中引用的文件均存在：`reference/viewport-and-base.css`、`reference/image-processing.py`、`reference/ppt-extract.py`、`reference/html-architecture.md`、`reference/edit-button-implementation.md`、`reference/animation-patterns.md`，以及 `STYLE_PRESETS.md`（含 CSS Gotchas）。
- 流程闭环：Phase 0 → 1（含获取内容）→ 2 → 3 → 5（新建）；或 Phase 0 → 4（含 extract + 同一 output_dir 生成）→ 5（转换）。无断点即可正常、有效运行。
