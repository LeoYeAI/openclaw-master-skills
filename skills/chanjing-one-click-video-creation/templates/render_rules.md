# 渲染规则（`render_rules`）

本文件为**渲染阶段**细则的维护位置：`scripts/run_render.py`、手工编排 TTS / 数字人 / AI 轨 / **ffmpeg** 拼接时均须遵守。  
**`ref_prompt` 的装配、题材路由、D.1–D.4、自检问句**以技能包 **`templates/storyboard_prompt.md`**（当代与 **D.1b** 共用真值）及 **`templates/history_storyboard_prompt.md`**（非当代）为准；**`SKILL.md` §4.2** 为指针，本文不重复。

---

## 1. 工作流中的 Render 与成功状态

对应端到端流水线中 **Plan → Script → Storyboard** 之后的阶段：

4. **Render**  
   - 须满足本文 **§3 技术规则**与 **§4 硬性约束**；`ref_prompt` 内容与质检须同时满足 **`storyboard_prompt.md`** / **`history_storyboard_prompt.md`**（见 **`SKILL.md` §4.2** 指针）。  
   - **重试**：可按 **`max_retry_per_step`**（见 `SKILL.md` **§6**，默认 `1`）等配置做逐步重试；语义为「每步基础 1 次 + 允许的额外重试」，具体以实现为准。  
   - **仍失败**：在尽量保留已产出物的前提下，返回 `video_plan`、口播与分镜等，**`status=partial`**（或产品线等价状态），便于排错或人工续跑。**`partial` 表示当次未成成片或中途失败**，与「是否自动降级为简化成片链路」无关；**渲染无降级**仍指不自动切换为「仅数字人 / 仅 AI」等替代方案。

5. **成功**  
   - **`status=success`**；记录耗时、镜数、成片路径等。

**渲染无降级**：混合渲染链路中，任关键环节失败即中断，**不**自动降级为「仅数字人」或「仅 AI」成片（除非产品另有显式开关）。成功时 `degrade_log` 为 `[]`。

---

## 2. 输出 JSON 中与渲染相关的约定

- **`status`**：`success` | `partial` | `failed`（以实际 API 为准）。  
- **`render_result`**：`video_file`、`scene_video_urls`、`render_path`、`degrade_log` 等。  
- 失败时仍尽量返回文案与分镜（`partial`），详见流水线实现。

---

## 3. 技术规则（编排指针见 `SKILL.md` §4.1）

### C.1 环境与基础

- 成片默认竖屏 **1080×1920**（以数字人分镜为准）。
- 子进程可至约 10 分钟级。
- 多镜并行与 CDN 下载须**限并发**。
- 仓库自动化：配置 **`SKILLS_DIR`** 或 **`CHANJING_ONE_CLICK_VIDEO_SKILLS_ROOT`**（兼容 **`CHAN_SKILLS_DIR`**；见 `SKILL.md` §3）。
- 远程下载与 ffmpeg 受并发控制；多段拼接；必要时按音频裁视频或末帧 / `tpad` 延长。

### C.2 封装与编码（对齐数字人轨）

**目标**：AI 等非数字人轨在进入最终 concat 前，与**本任务内**公共数字人 `poll_task.py` 落盘样例在分辨率、帧率、编码、码率量级上对齐。

| 步骤 | 要求 |
|------|------|
| 1. 参照轨 | 任取一条本任务已下载数字人 mp4，`ffprobe` 读 `v:0`：`width,height,r_frame_rate,avg_frame_rate,pix_fmt,codec_name,bit_rate`；`format.bit_rate`；`a:0`：`codec_name,sample_rate`。**以当次文件为准**，勿写死假设。 |
| 2. 空间 | AI 常见非 1080×1920：`scale`+`pad` 到参照宽高，`setsar=1`，`pix_fmt` 与参照一致（常见 `yuv420p`）。 |
| 3. 帧率 | 参照 CFR 而 AI 为 VFR 或偏低时，concat 前 AI 轨 `fps=参照帧率` 或 `minterpolate`（计算大，仅必要时）。 |
| 4. 视频编码与码率 | **团队择一统一**：软件如 **`libx264`**，或硬件如 **`h264_videotoolbox`**；码率参照 `ffprobe bit_rate`，用 `-b:v`/`-maxrate`/`-bufsize` 或 `-crf`；**各镜一致**，避免一镜糊一镜爆码。 |
| 5. 音频 | 各段 mux 时统一采样率/编码（常见 **AAC-LC** 与参照一致）；成片可再做单轨归一。 |
| 6. concat | 各段编码、分辨率、fps、`pix_fmt` 已统一后再 concat；**禁止**参数不一致时盲目 `-c copy`。 |

### C.3 数字人（选型与合成）

- 每次拉**最新**列表；不用过期 person id。
- 请求里须显式提供 `person_id`/`avatar_id` 与 **`figure_type`**（公共多形态时与 `list_figures.py` 列一致）；**禁止**用环境变量覆盖数字人/形象类型。
- **`list_figures.py` 默认 `--source customised`**，空列表正常；**公共形象**须显式执行 `list_figures.py --source common`（脚本无环境变量改默认源）。
- **选型须对比，勿默认列表排序**：`--json` 下对每条公共数字人比对 `name`、`figures[].type`、`figures[].width`/`height`、`audio_man_id`、`audio_name` 与当次策划/口播人设；必要时增大 `--page-size` 或翻页。**禁止**未比较即取返回列表最前几条。**默认偏好年轻形象**（名称或 `audio_name` 体现青年/元气/学生等气质者优先；题材需要成熟/中老年时再调整），与 **`chanjing-one-click-video-creation` `SKILL.md` §3** 一致。
- TTS **`audio_man`** 宜与该形象返回的 **`audio_man_id`** 一致；**须在 `workflow.json` 中写明**，禁止依赖环境变量默认音色。
- 失败可在**同套切段音频**下换列表中其它形象重试。

**数字人镜操作**：

- 上传该镜音频 `file_id`，`create_task.py` **音频驱动**。
- 数字人镜字幕：**默认** **`--subtitle hide`**；`workflow.json` 根级 **`subtitle_required`: true** 时 **`--subtitle show`**。`show` 且未传 `--subtitle-color` 时默认 **`#FFFFFF`（白字）**，位置与其它样式见 **`chanjing-video-compose`** skill / `create_task.py`。
- 公共多形态时 **`--figure-type` 与列表一致**。

### C.4 音频与 TTS

- 蝉镜单次 TTS 通常 **少于 4000 字**。
- **`run_render.py`**：按分镜 `voiceover` 连续合并时以 **`TTS_BATCH_MAX=3900`**（字符）为**合并阈值**，使各批低于接口上限并留余量；提交前仍校验单批不超过 **4000** 字。
- **默认**：整段一次合成。
- **超长**：按分镜 `voiceover`**连续合并成块**，每块 **少于 4000 字**且**批次数最少**；同 `audio_man`、同 `speed`/`pitch`；各批 ffmpeg **concat** 成**一条总轨**（批间极短静音慎用）。
- **禁止**：同镜内逐句多次 TTS。
- `poll` 可能给 `.mp3`；多批须合并后再 `ffprobe` **总时长**。
- 切段与 AI 条数用**实测**，勿按 `duration_sec` 硬裁口播。

### C.5 口播与画面对齐（强约束）

1. 须从 **`audio_task_state`** 得到 **`data.subtitles[]`**（`start_time` / `end_time` / `subtitle`）。多批 TTS 须给每批字幕加**累计时间偏移**再拼**全局表**。
2. 第 *k* 镜：用 `voiceover` 与全局字幕做**字符串级对齐**（允许轻微标点/语气差异）；得 `t_start`/`t_end`（秒）；切音频用 **`-ss`/`-to`**（或重编码切），保证与分镜文案一致。
3. 对不齐：退化为该镜在**全局时间轴比例区间**切段，`silencedetect` 边界 ±0.3s 吸附静音谷；仍失败则批内按比例，`debug` 标 **`align_quality=low`**。
4. 字幕 norm 常短于 `norm(full_script)`：**不得**强行按字幕与全文逐字对齐；标 **`align_quality=low_prop`**，在 **TTS 总时长**上按各镜 `norm(voiceover)` 占 `norm(full_script)` **比例**分配 `t_start`/`t_end`。
5. 数字人轨用**切段音频**；AI 轨用**同段音频** mux（`-shortest` 或 `apad`/`tpad`）；**禁止**用整段未切音频驱动单镜。

**切段上传**：数字人驱动用 **PCM WAV**（如 24kHz mono）较稳；从总轨按 `t_start`/`t_end` 切出。

### C.6 AI 分镜（文生视频与合成）

- `ref_prompt` 规则见 **`storyboard_prompt.md`**「文生视频提示词」（**D.1a**/**D.1b**/**画幅与数字人一致** 等；见 **`SKILL.md` §4.2**）。
- **提交文生视频前**须已有**首条公共数字人**成片落盘：`ffprobe` 读 **显示宽高**（编码宽高 + 常见 **`rotate`** 元数据），据此映射蝉镜 API 的 **`aspect_ratio`**（如 `9:16` / `16:9` / `1:1` / `3:4` / `4:3`）与 **`clarity`**（**720** 或 **1080**，按短边映射）。**禁止**在仍有 AI 镜时写死与当次数字人不一致的文生画幅。**纯 AI、无数字人镜**时回退默认 **9:16** + **1080**。
- **`run_render.py`** 将上述参数写入 `workflow_result.json` → **`debug.ai_video_submit_params`**，便于核对是否与所选公共数字人一致。
- 模型如 `Doubao-Seedance-1.0-pro` 等。
- **单段 5 或 10 秒**（模型允许）；镜内音频更长则 `N ≥ ceil(音频秒/单段)` 条；无音轨视频 **concat** 再与该镜音频 **mux**（`-shortest`）。
- 须做 **C.2** 与**当次数字人 mp4 `ffprobe` 参照**一致封装。

### C.7 收尾与并发

- 各镜顺序拼成成片；成功记本地路径与 `mixed_dh_ai` 类标记。
- 数字人与 AI **`poll_task.py` 可并行**。
- CDN 下载限并发（见 **§4 硬性约束** 表 **#7**）。

---

## 4. 硬性约束（原 `SKILL.md` §8）

| # | 约束 |
|---|------|
| 1 | **先定稿再渲染**：plan / 全文 / 分镜确认后再渲染。 |
| 2 | **TTS**：默认整段一次再按 scene 切；超过约 **4000 字**则分镜连续块**尽量少批**、同参数、**拼一条总音频**；**禁止**无必要按句/按镜碎 TTS。 |
| 3 | **镜头**：第 1、最后一镜数字人；中间奇数数字人、偶数 AI（规程见 **`storyboard_prompt.md`**「分镜结构与切段」；无自动化时 Agent 自检）。**首镜**：第 1 分镜 `voiceover` **≤20 字（硬上限）**，见同文件「文本切段」**首个分镜约束（硬）**。 |
| 4 | **人物族裔与造型**：AI 镜出现**可辨识人物**（或英文描述易使模型生成带人种特征的人像）时，须先据口播写清**与叙述一致的可见身份、动作、着装或现场关系**（**`storyboard_prompt.md`·D.1a**），**禁止**无依据的库存人设。族裔处理：**触发条件**、默认 profile、推荐英文短语及禁止项一律以 **`visual_prompt_people_constraint.md`·「显式族裔锚定（硬规则）」** 为准；满足触发条件时**必须在** `ref_prompt` 中**显式写入**族裔锚定，**禁止**仅用无族裔信息的通用人物描述依赖模型默认。口播或用户已能合理推断其他人种/地域时，须自洽。**语境缺省与由叙事推断之国别、朝代、文明圈**须与画面符号一致（无异域穿帮），见 **`storyboard_prompt.md`·D.0**、**`history_storyboard_prompt.md`·「文明圈与国别自洽」**、**`visual_prompt_people_constraint.md`·「历史 / 非当代」**。 |
| 5 | **AI 提示词**：自动路径按 **非当代/当代** 与口播组装；缺省与文明圈推断见 **`storyboard_prompt.md`·D.0**；**非特定人物题材**见 **`storyboard_prompt.md`·D.1a**。人工覆盖以 `storyboard_prompt.md` 为主；**勿**写死行业长篇样例或抄用他题 `ref_prompt`（示例仅演示结构）。 |
| 6 | **文生视频负向校验**：`ref_prompt` 须通过 **`storyboard_prompt.md`·D.1b**（负向清单 / 正向替换 / 可选英文否定短句）；命中负向而未改写不得提交。 |
| 7 | **CDN**：下载限流，防 429。 |
| 8 | **当次任务**：以**本次**任务 id 轮询为准；**勿**用 `list_tasks.py` 等历史列表替代当次提交与下载（除非用户明确要求复用历史任务）。 |

---

## 5. 与 `run_render.py` 的对应关系（摘要）

- 脚本**不**生成 plan / script / storyboard；不自动推断非当代/当代 `ref_prompt`。  
- 行为须符合本文 **§3、§4** 与 **`SKILL.md` §5** 字段契约。  
- 详细职责列表见 **`SKILL.md` §5**（「职责」）。
