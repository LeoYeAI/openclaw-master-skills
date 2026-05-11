---
name: chatppt-creator
description: 专业级智能 PPT 全生命周期创作与增强套件。支持通过 yoo-ai API 自动生成、编辑与美化 PPT。当需要执行以下任务时使用此 Skill：(1) 【多源生成】：将简单主题、结构化大纲、本地文件（.docx, .txt）或 AI 编码项目（架构分析）转化为专业 PPT；(2) 【专家流】：需要“先审阅大纲、后生成内容”的高质量创作流程，支持对大纲进行增删改查；(3) 【后期增强】：为已有任务添加演讲稿（Speaker Notes）、在指定位置插入新页面、或更换全局风格（字体、颜色、模板）；(4) 【互动引导】：预览精美封面、实时追踪异步生成任务进度、以及针对“内容太少”或“格式错误”等生成失败情况进行自动诊断与修复；(5) 【绘图PPT】：生成视觉效果极佳但不可编辑的图片型 PPT。适用于“帮我做个 PPT”、“总结这个项目的架构”、“给 PPT 加演讲稿”等指令。
---

# ChatPPT-Creator 智能 Skill 套件

这是一个基于意图识别的 PPT 处理工具集。Agent 应根据用户需求自动路由到相应的函数。

## 核心函数套件

> **注意**: 在调用以下命令时，请确保使用脚本的完整路径（相对于项目根目录或绝对路径）。

### 1. PPT 创建 (Creation)

#### create_ppt_from_text
当用户提供主题或简单描述时调用。
- **命令**: `node {{SKILL_PATH}}/scripts/chatppt_creator.js create_from_text --text "<主题>" --font_name "<字体>" --color "<颜色>" --language "<语言>" --report "<true/false>"`
- **可用字体**: [黑体|宋体|仿宋|幼圆|楷体|隶书] (注意：不支持微软雅黑)。
- **注意**: `report` 默认为 `true`，启用在线编辑报告模式。

#### create_ppt_from_custom_outline
当用户提供详细结构化大纲时调用。
- **命令**: `node {{SKILL_PATH}}/scripts/chatppt_creator.js create_from_custom_outline --custom_data '<JSON大纲>' --font_name "<字体>" --color "<颜色>" --report "<true/false>"`
- **可用字体**: [黑体|宋体|仿宋|幼圆|楷体|隶书]。
- **注意**: `report` 默认为 `true`。

#### create_ppt_from_file (Agent 复合任务)
当用户提供本地文件（.txt, .docx 等）时：
1. **读取文件**: 使用 `Read` 工具读取文件内容。
2. **大模型转换**: 将内容转换为 `create_ppt_from_custom_outline` 所需的 JSON 格式。
3. **展示并确认 (关键)**: **必须**将生成的结构化大纲（标题、章节、页面主题）以易读的格式展示给用户，并明确询问：“这是为您生成的大纲，您看是否满意？如果有需要调整的地方请告诉我。”
4. **调用函数**: 仅在用户确认满意后，才执行 `create_ppt_from_custom_outline`。

#### create_ppt_from_file_with_review
使用专家级 Prompt 驱动的工作流，生成高质量 Markdown 大纲，解析为 JSON，供审阅与微调后再生成。
- **阶段一（生成 Prompt）**  
  `node {{SKILL_PATH}}/scripts/chatppt_creator.js create_from_file_with_review --file_path "<本地文件>" --user_prompt "<要求>" --count_1 5 --count_2 3 --language zh-CN`  
  输出 `[PROMPT_START]...[PROMPT_END]`，请用 LLM 生成 Markdown 并保存到文件。
- **阶段二（解析与审阅）**  
  `node {{SKILL_PATH}}/scripts/chatppt_creator.js create_from_file_with_review --file_path "<本地文件>" --user_prompt "<要求>" --count_1 5 --count_2 3 --language zh-CN --markdown_path "<markdown文件路径>"`  
  输出 `[OUTLINE_REVIEW_START]...[OUTLINE_REVIEW_END]`。
- **用户确认 (强制)**: Agent 必须将输出的大纲内容呈现给用户，并等待用户确认或修改意见。**严禁跳过此步骤直接生成。**
- **应用修改（按用户反馈）**  
  准备补丁 JSON（支持 remove_catalog/rename_catalog/remove_sub_catalog/rename_sub_catalog），执行：  
  `node {{SKILL_PATH}}/scripts/chatppt_creator.js apply_outline_patch --json_path "<outline.json>" --patch_path "<patch.json>"`
- **最终生成**  
  仅在用户明确表示“可以生成”后，执行：
  `node {{SKILL_PATH}}/scripts/chatppt_creator.js generate_from_outline --json_path "<outline.json>" --font_name "<字体>" --color "<颜色>" --language "zh-CN" --report "<true/false>"`
- **可用字体**: [黑体|宋体|仿宋|幼圆|楷体|隶书]。
- **注意**: `report` 默认为 `true`。

#### create_ppt_from_project_analysis
自动分析当前 AI 编码项目的架构 and 技术栈，生成项目总结或汇报 PPT。
- **命令**: `node {{SKILL_PATH}}/scripts/chatppt_creator.js create_from_project_analysis --project_path "<项目绝对路径>" --user_prompt "<汇报重点>"`
- **适用场景**: 当用户说“为这个项目写个汇报”或“总结一下我的代码架构”时。
- **工作流**: 
  1. 脚本扫描项目（依赖、目录、入口点）。
  2. 输出专家 Prompt，Agent 调用 LLM 生成 Markdown。
  3. 脚本解析并展示大纲供用户审阅。
  4. 确认后执行生成。

### 2. 修改与增强 (Modification)

#### add_speaker_notes_to_ppt
为已有任务生成演讲稿。
- **命令**: `node {{SKILL_PATH}}/scripts/chatppt_creator.js add_notes --task_id "<ID>" --report "<true/false>"`

#### insert_page_into_ppt
在指定位置插入新页面。
- **命令**: `node {{SKILL_PATH}}/scripts/chatppt_creator.js insert_page --task_id "<ID>" --slide_number "<页码>" --slide_type "<类型>" --text "<内容>" --report "<true/false>"`

#### regenerate_ppt_with_new_style
更换风格重新生成。
- **命令**: `node {{SKILL_PATH}}/scripts/chatppt_creator.js regenerate --task_id "<ID>" --font_name "<字体>" --color "<颜色>" --cover_id "<模板ID>" --transition "<1/2>" --report "<true/false>"`

### 3. 模板与预览 (Template & Preview)

#### preview_ppt_covers
根据标题和风格偏好预览可选的 PPT 模板封面。
- **命令**: `node {{SKILL_PATH}}/scripts/chatppt_creator.js preview_covers --title "<标题>" --style "<风格>" --color "<颜色>" --count 4`
- **可用风格**: 科技风, 商务风, 小清新, 极简风, 中国风, 可爱卡通。

#### check_task_status
查看历史任务或特定任务的实时生成进度。
- **命令**: `node {{SKILL_PATH}}/scripts/chatppt_creator.js check_status --task_id "<ID>"`
- **无参数调用**: `node {{SKILL_PATH}}/scripts/chatppt_creator.js check_status` (显示最近 10 条记录)

### 4. 绘图PPT (Banana Style)

> **注意**: 此功能生成的 PPT 为**图片型幻灯片**，拥有极佳的视觉效果，但**不支持文本编辑**。适用于对设计感要求高、无需二次修改的场景。

#### list_banana_styles
获取绘图PPT可用的风格或模板列表。
- **命令**: `node {{SKILL_PATH}}/scripts/chatppt_creator.js list_banana_styles --type "<style/template>"`
- **参数**: `type` 默认为 `style`。

#### create_banana_ppt
创建绘图PPT。
- **命令**: `node {{SKILL_PATH}}/scripts/chatppt_creator.js create_banana_ppt --text "<主题>" --style "<风格ID>" --complex "<1/2/3>"`
- **参数**:
  - `text`: PPT 主题或简要描述。
  - `style`: 风格 ID (通过 `list_banana_styles` 获取)。
  - `complex`: 复杂度 (1-简单, 2-中等, 3-复杂)，默认为 1。
  - `import_image`: 参考图 URL (可选，当不指定 style 时使用)。
- **交互**: 
  - Agent 必须在调用前明确告知用户：“绘图PPT生成的幻灯片无法编辑文本，但视觉效果更好。确认要使用此模式吗？”
  - 如果用户选择此模式但未指定 `style` 或 `import_image`，Agent 应主动询问：“您是想从【预设风格列表】中选择一个，还是提供一张【参考图】来定制风格？”
  - **结果反馈 (强制)**: 当任务完成（脚本输出 `[TASK_COMPLETED]`）时，Agent **必须主动**向用户报告：“您的绘图 PPT 已生成并下载到本地：[文件路径]”。严禁保持沉默等待用户询问。
  - **风格选择流程**: 若用户选择“预设风格”，Agent 必须**主动调用** `list_banana_styles` 展示所有可用风格（含ID与预览图），然后等待用户选择 ID。
  - **参考图流程**: 若用户选择“参考图”，Agent 必须提示用户：“请提供图片的**网络链接 (URL)**。目前仅支持公网可访问的图片链接，暂不支持直接上传本地图片。”获取 URL 后使用 `--import_image` 参数生成。

### 5. 绘图PPT 风格知识库 (Style Knowledge Base)
Agent 应利用以下内置知识，根据用户描述（如“可爱”、“商务”、“简约”）主动推荐风格 ID。

| 风格ID | 名称 | 关键词 | 预览图URL |
| :--- | :--- | :--- | :--- |
| `dzgSKy` | 现代波普风 | 通用 | `https://image.yoojober.com/upload-m/2025-12/694b8d00a930e.png` |
| `pBUWQj` | 小狗绘本风 | 卡通, 动漫 | `https://image.yoojober.com/upload-m/2025-12/694b8e2e93b69.png` |
| `QPQPrk` | 极简弥散光感风 | 极简, 商务 | `https://image.yoojober.com//users/2025-12/694d0e4b187ff.jpg` |
| `kbgWaR` | 法式浪漫水粉插画风 | 艺术, 手绘 | `https://image.yoojober.com//users/2025-12/694d26085101d.jpg` |
| `ptCVxw` | 复古摩登艺术画廊风 | 复古, 艺术, 手绘 | `https://image.yoojober.com/upload-m/2025-12/694b8ef638ed0.png` |
| `9mc6qh` | 栅栏极简主义风 | 极简, 商务 | `https://image.yoojober.com/upload-m/2025-12/694b8f4f8665f.png` |
| `XPd6kB` | 3D黏土 | 3D | `https://image.yoojober.com/users/2025-12/694ca476a98fc.jpg` |
| `7eFV4p` | 点阵涂鸦风 | 通用 | `https://image.yoojober.com/upload-m/2025-12/694b9042214d0.png` |
| `GTG4ZT` | 水墨风 | 国风 | `https://image.yoojober.com//users/2025-12/694ceb081bdfb.jpg` |
| `RAzjZZ` | 橙色国风美学风 | 国风 | `https://image.yoojober.com/upload-m/2025-12/694b909651380.png` |
| `DUUkcN` | 梦幻水彩风 | 艺术, 手绘 | `https://image.yoojober.com/upload-m/2025-12/694b9054a89ca.png` |
| `m526yq` | 线稿插图风 | 通用 | `https://image.yoojober.com//users/2025-12/694d26d0bf718.jpg` |
| `4WuSkQ` | 复古双色Riso印刷插画风 | 复古, 艺术, 手绘 | `https://image.yoojober.com/upload-m/2025-12/694b8fa58790f.png` |
| `BEY52Y` | 治愈系蜡笔手绘风 | 艺术, 手绘, 可爱, 治愈 | `https://image.yoojober.com/upload-m/2025-12/694b8fe3ec997.png` |
| `CKejSY` | 北欧风复古水粉插画风 | 复古, 艺术, 手绘 | `https://image.yoojober.com//users/2025-12/694d31dd3e785.jpg` |
| `NKdGBE` | 热血漫画风 | 卡通, 动漫 | `https://image.yoojober.com//users/2025-12/694d278f8fec3.jpg` |
| `Evc69b` | 未来科技抽象渐变风 | 科技, 未来 | `https://image.yoojober.com/upload-m/2025-12/694b9030156ac.png` |
| `EhRqGC` | 独立漫画涂鸦黄风 | 卡通, 动漫 | `https://image.yoojober.com/upload-m/2025-12/694b908e3bb0f.png` |
| `zUJpC3` | 复古波普奶油风 | 复古 | `https://image.yoojober.com/upload-m/2025-12/694b90a423caf.png` |
| `DF7VsS` | 现代几何扁平风 | 扁平 | `https://image.yoojober.com/upload-m/2025-12/694b90bb7b2b5.png` |
| `hTh7ev` | 暗黑几何杂志风 | 暗黑, 酷炫 | `https://image.yoojober.com/upload-m/2025-12/694b983b878c5.png` |
| `wZxfcW` | 环保拼贴手账风 | 通用 | `https://image.yoojober.com//users/2025-12/694cbc420a978.jpg` |
| `uKeTY3` | 复古电影手账风 | 复古 | `https://image.yoojober.com//users/2025-12/694d0b9117d4c.jpg` |
| `h7upNw` | 复古报纸版式风 | 复古 | `https://image.yoojober.com/users/2025-12/694cad551094e.jpg` |
| `95CDPf` | 绿色智慧工业风 | 通用 | `https://image.yoojober.com/upload-m/2025-12/694b97ebbf329.png` |
| `JCBCM8` | 创意白板手绘风 | 艺术, 手绘 | `https://image.yoojober.com/upload-m/2025-12/694b97bd7a821.png` |
| `yc4xdn` | 千禧数码像素波普风 | 科技, 未来 | `https://image.yoojober.com/upload-m/2025-12/694b96b0ab08d.png` |
| `BaPbZD` | 3D乐高风 | 3D | `https://image.yoojober.com//users/2025-12/694cdeacc330e.jpg` |
| `NkXPB2` | 酸性绿独立杂志风 | 通用 | `https://image.yoojober.com/upload-m/2025-12/694b97a20cb64.png` |
| `bE35kC` | 课堂笔记本风 | 通用 | `https://image.yoojober.com/upload-m/2025-12/694b957809262.png` |
| `QjymSk` | 蓝调喷枪极简风 | 极简, 商务 | `https://image.yoojober.com//users/2025-12/694cbd456a062.jpg` |
| `X4wwxk` | 粉色怪诞字体波普风 | 通用 | `https://image.yoojober.com/upload-m/2025-12/694b955cb5c90.png` |
| `sk5YQf` | 3D流体玻璃拟态风 | 3D | `https://image.yoojober.com//users/2025-12/694d2d68ab32e.jpg` |
| `yMNSMB` | 充气膨胀风 | 通用 | `https://image.yoojober.com//users/2025-12/694ce97d1524c.jpg` |
| `6xwPyv` | 立体毛毡风 | 通用 | `https://image.yoojober.com/upload-m/2025-12/694b94b90737c.png` |
| `3f9VWn` | 温暖梦幻风 | 通用 | `https://image.yoojober.com/upload-m/2025-12/694b94a624c6b.png` |
| `HemEtk` | 磨砂立体几何风 | 通用 | `https://image.yoojober.com/upload-m/2025-12/694b947866636.png` |
| `9RrScC` | 马蒂斯猫咪风 | 通用 | `https://image.yoojober.com/upload-m/2025-12/694b942937313.png` |
| `TFGzHR` | 锦鲤图纹风 | 通用 | `https://image.yoojober.com/upload-m/2025-12/694b941a62698.png` |
| `ADmBu4` | 以梦为马主题风 | 通用 | `https://image.yoojober.com//users/2025-12/694d282e1b7d6.jpg` |
| `uzEnzz` | 水彩晕染马年主题风 | 艺术, 手绘 | `https://image.yoojober.com/upload-m/2025-12/694b93c31776e.png` |
| `wsNHz9` | 极简水彩插画风 | 极简, 商务, 艺术, 手绘 | `https://image.yoojober.com/upload-m/2025-12/694b939c1163a.png` |
| `92WGRw` | 山海绘卷风 | 通用 | `https://image.yoojober.com//users/2025-12/694cb541e1d3c.jpg` |
| `hxERQw` | 治愈童趣风 | 可爱, 治愈 | `https://image.yoojober.com/upload-m/2025-12/694b932137083.png` |
| `Sydy3t` | 东方插画风 | 艺术, 手绘, 国风 | `https://image.yoojober.com/users/2025-12/694bf5d001f32.jpg` |
| `f58YXJ` | 抽象花卉风 | 通用 | `https://image.yoojober.com/upload-m/2025-12/694b92ec7a958.png` |
| `R4Z72Q` | 暗黑Y2K液态金属风 | 暗黑, 酷炫 | `https://image.yoojober.com//users/2025-12/694d28e46456d.jpg` |
| `4SMNee` | 90年代复古系统界面风 | 复古 | `https://image.yoojober.com/upload-m/2025-12/694b924922730.png` |
| `jBSqcB` | SaaS极简风 | 极简, 商务 | `https://image.yoojober.com//users/2025-12/694d3522557c5.jpg` |
| `2p9Z79` | Chikawa风 | 通用 | `https://image.yoojober.com/upload-m/2025-12/694b91d0e1718.png` |
| `3WXC5Z` | 蜡笔小新风 | 通用 | `https://image.yoojober.com/upload-m/2025-12/694b919d2c366.png` |
| `pfudeP` | 任天堂游戏风 | 游戏 | `https://image.yoojober.com/upload-m/2025-12/694b918772109.png` |
| `NrQVUC` | 3D西游记风 | 3D | `https://image.yoojober.com/upload-m/2025-12/694b98b417bff.png` |
| `SRJmXq` | 我的世界像素风格 | 科技, 未来, 游戏 | `https://image.yoojober.com/upload-m/2025-12/694b98c12ce45.png` |
| `bZ6Xkp` | 中国年画风 | 国风 | `https://image.yoojober.com/upload-m/2025-12/694b98ceb97cf.png` |
| `mc4Xj9` | 美式漫画风格 | 卡通, 动漫 | `https://image.yoojober.com/upload-m/2025-12/694b99300be89.png` |
| `RAPQvH` | 哆啦A梦风 | 通用 | `https://image.yoojober.com/upload-m/2025-12/694b993e8311e.png` |
| `YRNyXV` | 猫和老鼠风 | 通用 | `https://image.yoojober.com//users/2025-12/694cec7c8e726.jpg` |
| `TFBqB6` | 小黄人风 | 通用 | `https://image.yoojober.com/users/2025-12/694caad600eed.jpg` |
| `jvHgwB` | 圣诞风 | 通用 | `https://image.yoojober.com/upload-m/2025-12/694b99b042c4a.png` |
| `rDYGqb` | 阿凡达风 | 通用 | `https://image.yoojober.com/upload-m/2025-12/694b99dab2c09.png` |
| `ktvf5H` | 纪念碑谷风 | 通用 | `https://image.yoojober.com/upload-m/2025-12/694b9a40516fe.png` |
| `XbQQSt` | 疯狂动物城风 | 通用 | `https://image.yoojober.com//users/2025-12/694d2a5094ee4.jpg` |
| `AUfyVT` | 马里奥像素风 | 科技, 未来, 游戏 | `https://image.yoojober.com/upload-m/2025-12/694b9b01b3872.png` |
| `wxPbdm` | 鬼灭之刃风 | 通用 | `https://image.yoojober.com/users/2025-12/694d0abe3aaa0.jpg` |
| `efqRjR` | 名侦探柯南风 | 通用 | `https://image.yoojober.com/upload-m/2025-12/694b9b1c604e3.png` |
| `K4HTNR` | 3D Pingu风 | 3D | `https://image.yoojober.com/upload-m/2025-12/694b9b68b41db.png` |
| `mSpQqY` | loopy风格 | 通用 | `https://image.yoojober.com/upload-m/2025-12/694b9bb91ed40.png` |
| `dTWkfh` | 三丽鸥风格 | 通用 | `https://image.yoojober.com/upload-m/2025-12/694b9bc594323.png` |
| `JXrGsT` | 星之卡比风 | 通用 | `https://image.yoojober.com/users/2025-12/694bfffb46cea.jpg` |
| `wdxmJ7` | 雪王可爱风 | 可爱, 治愈 | `https://image.yoojober.com/upload-m/2025-12/694b9c5fa1ddb.png` |
| `craTgk` | 王者荣耀风 | 通用 | `https://image.yoojober.com/upload-m/2025-12/694b9c6d5674d.png` |
| `7kEbnB` | LOL风 | 通用 | `https://image.yoojober.com/upload-m/2025-12/694b9c7a2da76.png` |
| `NKhYbh` | 彩铅尼克风 | 通用 | `https://image.yoojober.com/upload-m/2025-12/694b9c91a5e5b.jpg` |
| `xh5HzJ` | 怀旧撕纸拼贴风 | 复古 | `https://image.yoojober.com/upload-m/2025-12/694b9ce097b81.png` |
| `JPuXDR` | 牛皮贴纸风 | 通用 | `https://image.yoojober.com/upload-m/2025-12/694b9cef60c25.png` |
| `4c7NDA` | 复古航空信笺风 | 复古 | `https://image.yoojober.com/upload-m/2025-12/694b9cfda7801.png` |
| `2aPM69` | MBB咨询精英汇报风 | 商务, 专业 | `https://image.yoojober.com//users/2025-12/694d2c335521e.jpg` |
| `JdC6wU` | 空灵禅意山水风 | 通用 | `https://image.yoojober.com/upload-m/2025-12/694b9da985ea5.png` |
| `9yvrzC` | 新春祥瑞红金风 | 通用 | `https://image.yoojober.com/users/2025-12/694ca846e69a8.jpg` |
| `rgRcCT` | 大字报风 | 通用 | `https://image.yoojober.com/users/2025-12/694ca9bf34f27.jpg` |
| `9FX5DZ` | 暗黑弥散风 | 暗黑, 酷炫 | `https://image.yoojober.com//users/2025-12/694cd77806948.jpg` |
| `fXUkzh` | 辛普森风格 | 通用 | `https://image.yoojober.com//users/2025-12/694cd8ce63ef7.jpg` |
| `meshdF` | 吉卜力风 | 通用 | `https://image.yoojober.com//users/2025-12/694cdbda134be.jpg` |
| `Rmhdpu` | 梦幻水彩手绘风 | 艺术, 手绘 | `https://image.yoojober.com/upload-m/2025-12/694b9e3720af4.png` |
| `US59E8` | 拼豆风 | 通用 | `https://image.yoojober.com/upload-m/2025-12/694b9f22ef20d.png` |
| `AQQmPN` | 格林童话风 | 通用 | `https://image.yoojober.com/upload-m/2025-12/694b9f33dd8e9.png` |
| `GBKsgV` | 昭和漫画风 | 通用 | `https://image.yoojober.com/upload-m/2025-12/694b9f43a95f0.png` |
| `BUT5VW` | 90s樱桃小丸子风 | 通用 | `https://image.yoojober.com/upload-m/2025-12/694b9f520538e.png` |
| `C9k8jQ` | 80年代复古波普像素风 | 复古, 科技, 未来 | `https://image.yoojober.com/upload-m/2025-12/694b9f7066aea.png` |
| `eQxdvM` | Google Material风 | 通用 | `https://image.yoojober.com/upload-m/2025-12/694ba05572cdf.png` |
| `J6peZh` | 利希滕斯坦风 | 通用 | `https://image.yoojober.com//users/2025-12/694d2cb5bc36b.jpg` |
| `aFRBmf` | 花生漫画风 | 卡通, 动漫 | `https://image.yoojober.com/upload-m/2025-12/694ba16242cbd.png` |
| `ReURBp` | 小王子极简绘本风 | 卡通, 动漫, 极简, 商务 | `https://image.yoojober.com/upload-m/2025-12/694ba21a63481.png` |
| `75XqKz` | 3D纸雕风 | 3D | `https://image.yoojober.com/upload-m/2025-12/694ba24f1e771.png` |
| `67pB84` | 蓝晒印相风 | 通用 | `https://image.yoojober.com/upload-m/2025-12/694ba35c63da5.png` |
| `BWmPKk` | X光透视风 | 通用 | `https://image.yoojober.com/upload-m/2025-12/694ba3687d402.png` |
| `jxNyKt` | 微缩积木风 | 通用 | `https://image.yoojober.com/upload-m/2025-12/694bf4247f41e.png` |
| `EFF93n` | 极致简洁 | 极简, 商务 | `https://image.yoojober.com//users/2025-12/694d32b94c004.jpg` |
| `T4GX4a` | 黑板报风 | 通用 | `https://image.yoojober.com//users/2025-12/694d2df3d3569.jpg` |
| `Z6fgKu` | INS风软萌插画 | 艺术, 手绘, 可爱, 治愈 | `https://image.yoojober.com/upload-m/2025-12/6951ef9dc837b.png` |
| `tPzYXg` | 拟人潮玩风 | 通用 | `https://image.yoojober.com//users/2025-12/6951efd8a8910.png` |

**推荐策略**:

1.  **主动推荐**: 当用户询问“有哪些风格”时，Agent 应从上述知识库中挑选 3-5 个涵盖不同类型（如：1个商务、1个可爱、1个国风、1个3D/创意）的风格进行展示。
2.  **语义匹配**: 
    - 想要“专业、正式、汇报用” -> 推荐 `2aPM69` (MBB咨询) 或 `EFF93n` (极致简洁)。
    - 想要“可爱、童趣、给孩子看” -> 推荐 `XPd6kB` (3D黏土) 或 `pBUWQj` (小狗绘本)。
    - 想要“中国特色、古典” -> 推荐 `GTG4ZT` (水墨风) 或 `Sydy3t` (东方插画)。
    - 想要“酷炫、有设计感” -> 推荐 `yMNSMB` (充气膨胀) 或 `R4Z72Q` (暗黑Y2K)。
3.  **展示要求**: 必须输出 **风格名称**、**ID** 和 **预览图**（使用 Markdown 图片语法展示预览图，让用户直观看到效果）。
4.  **兜底引导**: 如果知识库中没有用户想要的风格，或者用户表示“不喜欢这些推荐”，Agent 必须**主动提示**：“如果您有自己喜欢的风格图片，可以直接提供图片的网络链接 (URL)，我可以根据您的参考图来生成专属风格的 PPT。”

## 交互准则

### 1. 意图识别与模式路由 (Intent & Routing)
Agent 应从自然语言中提取参数，并在执行前确认用户偏好的**生成模式**。

**场景 A: 用户仅提供主题 (Text-to-PPT)**
当用户指令为“生成一个关于[主题]的PPT”且未明确指定模式时，Agent **严禁直接调用** `create_from_text`，必须先询问用户选择哪种模式：
1.  **标准模式 (Standard)**: 生成可编辑的 PPT 页面，包含文本框和图形。适用于需要后续修改内容、调整大纲的场景。（对应 `create_from_text`）
2.  **绘图模式 (Banana/Image-based)**: 生成**不可编辑**的图片型 PPT，视觉效果极佳，支持指定风格或上传参考图。适用于追求设计感、无需修改文字的场景。（对应 `create_banana_ppt`）

> **话术示例**: 
> "为您准备了两种生成模式：
> 1. **标准模式**：生成可编辑的普通 PPT，适合需要修改内容的文档。
> 2. **绘图模式**：生成精美的图片型 PPT（不可编辑文本），支持指定风格或参考图，视觉效果更好。
> 请问您想使用哪种模式？"

**场景 B: 高质量/长文档需求**
- 对于**高质量、专业性强**的汇报需求，Agent **必须**优先引导用户使用 `create_ppt_from_file_with_review` 或 `create_ppt_from_project_analysis` 流程。
- 基本的 `create_from_text` 仅适用于极其简单的草稿需求，内容会非常简略。

### 2. 参数传递约束 (Parameter Whitelist)
**重要**: 为了避免 API 报错，Agent 必须严格遵守以下参数规定：
1.  **禁止推测字体**: 绝对禁止自行推测或默认添加 `--font_name "微软雅黑"`。
2.  **静默政策**: 如果用户没有在指令中明确要求特定字体（例如：“用宋体”），你**绝对禁止**在生成的命令中包含 `--font_name` 参数。
3.  **字体白名单**: 仅允许使用以下字体：`黑体`、`宋体`、`仿宋`、`幼圆`、`楷体`、`隶书`。如果用户要求的字体不在名单内（如微软雅黑），请忽略该要求或引导用户选择白名单内的字体。

### 3. 立即反馈，后台处理
启动任何生成任务后，脚本会立即输出 `[EDITOR_URL_START]url[EDITOR_URL_END]` 作为“实时工作台”。
**Agent 动作**:
1. 立即提取此链接。
2. 告知用户：“任务已成功启动，正在后台异步处理。您可以点击此处 **[进入在线工作台]** 实时观看 PPT 的渲染生成过程。生成完成后我会自动为您下载到本地。”
3. 严禁在任务未完成前阻塞用户。

### 4. 分开输出与链接约束 (Output Constraints)
**重要**: 为了保持交互的清晰度，Agent 必须**强制执行**以下输出规范：
1.  **严禁混合输出**: 在线工作台链接（任务开始时）和本地下载成功的确认信息（任务完成下载后）**绝对禁止**在同一次对话回复中同时展示。
2.  **禁用 Markdown 链接**: 不要使用 `[文本](链接)` 语法。必须将 URL 放置在**代码块**中，或以**纯文本**形式展示。
3.  **识别标记**:
    - 实时工作台: 识别 `[EDITOR_URL_START]` 和 `[EDITOR_URL_END]`。
    - 最终编辑链接: 任务完成后再次确认 `[EDITOR_URL_START]`。
    - 预览图片: 识别 `[IMAGE_URL_START]` 和 `[IMAGE_URL_END]`。
4.  **分阶段展示**:
    - 任务启动后：仅展示“实时工作台链接”。
    - 任务完成后：仅展示“下载路径”和“编辑链接”。

### 5. 错误诊断与协议 (Error Handling & Protocol)
如果接口调用返回 400 错误，或运行报错：
1.  **任务失败 (-1/3)**: 
    - Agent **禁止**仅复读错误信息。
    - 必须从脚本输出中提取失败原因，并主动调用 `node {{SKILL_PATH}}/scripts/chatppt_creator.js validate_outline --json_path "<path>"` 进行诊断。
    - 反馈示例：“生成中断了，原因是‘内容长度不足’。我已经找到了问题，是否需要我为您补充内容后重新生成？”
2.  **API Key 缺失**: 
    - Agent 应主动询问用户：“我发现您还没有配置 yoo-ai 的 API Key。如果您已有 Key，请告诉我，我将为您自动创建配置文件。如果您还没有 Key，可以前往 yoo-ai 官网获取。”
    - 获取 Key 后，调用 `Write` 工具将 Key 写入 `{{SKILL_PATH}}/config.json`，格式为 `{"API_KEY": "用户提供的KEY"}`。
3.  **JSON 校验失败**: 
    - Agent 应调用 `node {{SKILL_PATH}}/scripts/chatppt_creator.js validate_outline --json_path "<path>"` 来获取具体的错误列表。
4.  **重试**: 修复后，再次运行 `generate_from_outline`。

### 6. 异步追踪 (Asynchronous Tracking)
如果用户关闭了对话或链接失效，Agent 应引导用户使用：
- `node {{SKILL_PATH}}/scripts/chatppt_creator.js check_status --task_id "<ID>"` 找回任务状态及最新链接。

### 7. 主动引导 (Proactive Guidance)
**重要**: 每次任务完成（看到 `[TASK_COMPLETED]` 标记）后，Agent **必须**主动询问用户是否需要进一步修改，例如：
> "您的 PPT 已生成并下载。需要我为您做进一步的修改吗？例如 **添加演讲稿**、**更换主题色或模板**，或者 **插入新的页面**？"

如果在开始前用户对风格不确定，可以引导：
> "在生成之前，您想先看看几种不同风格（如商务风、极简风）的**模板封面**吗？"

## 配置
确保 `config.json` 中已配置 `API_KEY`。参考 `config.json.template`。
