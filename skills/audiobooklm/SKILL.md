---
name: audiobooklm
description: 提供有声书创作与音频能力（ABS 读写、音效/音频检索、二创、音色推荐、章节角色分析等），通过 HTTP Streamable MCP 调用。
homepage: https://aigc.ximalaya.com
source: https://aigc.ximalaya.com/audiobooklm/mcp
author: AudiobookLM
metadata:
  {
    "clawdbot":
      {
        "emoji": "🎧",
        "requires": { "env": ["AUDIOBOOKLM_TOKEN"] },
        "primaryEnv": "AUDIOBOOKLM_TOKEN"
      },
    "openclaw":
      {
        "emoji": "🎧",
        "required_env": ["AUDIOBOOKLM_TOKEN"],
        "version": "0.0.7",
        "changelog":
          [
            "新增`create_album`，`upload_audio_to_album`，`list_tts_voices`，`synthesize_tts`，`asr_audio_to_text` tools",
            "修正 search_audio 的真实能力定义：先 mock 匹配，未命中再走 LLM+TTS 自动生成",
            "新增指定文本+指定音色ID的直合成实践：list_tts_voices -> synthesize_tts",
            "完善工具路由与边界：tools/list 动态探测、dialogue_split 与 chapter_character_analysis 入参/能力说明"
          ]
      }
  }
---

# audiobooklm 技能说明（OpenClaw）

MCP 地址：`https://aigc.ximalaya.com/audiobooklm/mcp`

## 安装前注意事项（发布到 ClawHub 必带）

1. 来源与信任
- 官方入口：`https://aigc.ximalaya.com`
- MCP 服务地址：`https://aigc.ximalaya.com/audiobooklm/mcp`
- 仅在你信任该域名与发布方时安装。

2. 凭证配置
- 必需环境变量：`AUDIOBOOKLM_TOKEN`（Bearer Token）
- 建议使用测试账号或低权限 token，不要粘贴高权限生产 token。
- 建议定期轮换 token；发现泄露立即吊销并重建。

3. 数据外发与合规
- 使用本技能时，输入文本、音频 URL、以及你提交的结构化数据会发送到 `aigc.ximalaya.com`。
- 不要上传未授权、涉密或敏感个人信息内容。
- 版权或隐私不明确的内容，先确认授权后再调用。

## 0. 首次使用引导（OpenClaw 必须先提示）

当用户首次使用本技能，或检测到未配置 token 时，OpenClaw 必须先提示以下内容，再进入工具调用：

1. 请先访问 [https://aigc.ximalaya.com](https://aigc.ximalaya.com) 注册/登录账号。
2. 进入个人中心创建 API Token（MCP / API Token）。
3. 在 OpenClaw 配置 Bearer Token（`AUDIOBOOKLM_TOKEN`），再继续使用本技能。

推荐提示文案（可直接复用）：
`使用 audiobooklm 前，请先到 https://aigc.ximalaya.com 登录并在个人中心创建 API Token，然后将 token 配置到 OpenClaw（Bearer Token / AUDIOBOOKLM_TOKEN）。配置完成后我再为你执行读取书籍、音效检索或二创操作。`

## 1. 使用规则（必须遵守）

1. 所有书籍/章节/音频/音效结论都必须来自本轮真实工具返回，禁止编造。
2. 调用成功不等于业务成功：若工具返回文本里包含 `{"success":false}` 或 `code!=20000`，按失败处理并转述真实错误。
3. 禁止输出原始大段 JSON 给用户，需整理为自然语言；但不得改写关键事实（标题、ID、URL、错误信息）。

## 2. 鉴权与会话（标准 MCP 流程）

请求头固定：
- `Accept: application/json, text/event-stream`
- `Authorization: Bearer <AUDIOBOOKLM_TOKEN>`
- `Content-Type: application/json`

调用顺序（不可跳过）：
1. `initialize`
2. `notifications/initialized`
3. `tools/list` / `tools/call`（都要带 `mcp-session-id`）

若无 token 或 token 无效，服务会返回 `401`（`invalid_token`）。

## 3. 工具清单（以 tools/list 实时结果为准）

OpenClaw 不应硬编码工具总数；先调用 `tools/list`，再按返回结果路由。  
以下为当前主流程常用工具：
- `chapter_split`
- `search_faq`
- `annotate_pinyin`
- `character_analyze`
- `timber_assign`
- `search_sound_label`
- `sound_effect`
- `chapter_character_analysis`
- `chapter_character_predict`
- `dialogue_split`
- `search_audio`
- `fan_made_audio`
- `patch_abs`
- `read_abs`
- `image_generation`
- `create_album`
- `upload_audio_to_album`
- `list_tts_voices`
- `synthesize_tts`
- `asr_audio_to_text`

说明：部分环境会通过服务端配置隐藏某些工具（如 `text_writing`、`analysis_audio_fx`、`analysis_sound_description` 等）；是否可用必须以本轮 `tools/list` 为准。

## 4. 路由策略（按用户意图）

1. 书单/单书/单章读取：`read_abs`
- 书单：`scope={"domain":"books"}`
- 单书：`scope={"domain":"book","book_id":"<id>"}`
- 单章：`scope={"domain":"chapter","book_id":"<id>","chapter_id":"<id>"}`

2. 创建书/写入编辑：`patch_abs`
- 创建书必须：`scope={"domain":"book"}` 且不传 `book_id`
- 常见流程：先 `read_abs(books)` 取 `team_id`，再 `patch_abs(create_book)`，再 `patch_abs(add_chapter...)`

3. 环境音/音效检索：`search_sound_label`
- 如“海浪、雨声、风声、紧张 BGM”

4. 文生音频（检索优先，未命中则自动 TTS 生成）：`search_audio`
- 该工具不是通用“站内专辑检索”，而是：
- 先在服务端 `mock.json` 做语义匹配命中（返回已有 `audio_url`/`audio_path`）
- 未命中时自动执行“LLM 写文案 -> LLM 推荐音色 -> TTS 合成”并返回新 `audio_url`

5. 音频二创：`fan_made_audio`
- 必须传 `audio_url` + `user_instruction`

6. 音色推荐：`timber_assign`
- 建议参数：`{"description":"成熟男声","text":"..."}`（效果更稳定）
- `description` 非强制；未提供时工具会尝试基于文本自动分析，但可控性会下降

7. 指定文本 + 指定音色ID 直接合成：`list_tts_voices` + `synthesize_tts`
- 适用于“我已经有文案，并且要固定某个音色ID”的刚性 TTS 需求
- 标准顺序：先 `list_tts_voices` 取 `speakerId`，再 `synthesize_tts(text, speaker_id)`
- 该场景不要路由到 `search_audio`（其音色是自动匹配，非强指定）

8. 章节角色链路：
- 一体化：`chapter_character_analysis`
- 分步：`dialogue_split` -> `chapter_character_predict`

9. 图像生成：`image_generation`
- `{"prompt":"..."}`，若下游超时按真实错误返回

## 5. 参数速查（仅列关键）

### read_abs
- `scope` 必填对象，`domain` 仅可为 `books|book|chapter`
- `fields` 可选数组
- `pagination` 可选对象
- `cookie` 可选

### patch_abs
- `scope` 必填对象，`domain` 为 `chapter|book|books`
- `operations` 必填数组，每项需 `op_id/type/reason`
- `base_version` 可选
- `dry_run` 可选，默认 `false`
- `cookie` 可选

### search_sound_label
- `query` 必填
- `top_k` 可选，默认 3

### search_audio
- `user_query` 必填
- `cookie` 可选
- 不支持直接传 `text`、`speaker_id`、`rate` 等 TTS 细粒度参数（由工具内部自动决策）

### fan_made_audio
- `audio_url` 必填
- `user_instruction` 必填
- `cookie` 可选

### timber_assign
- `description` 可选（建议传，便于控风格）
- 其余可选：`content_file/content_text/text/enable_ai_analysis/speaker_list/topk/rate/cookie`

### list_tts_voices
- `cookie` 可选
- `limit` 可选（`<=0` 表示不限制）

### synthesize_tts
- `text` 必填
- `speaker_id` 必填（来自 `list_tts_voices` 的 `speakerId`）
- `cookie` 可选
- 注意：服务端会将文本截断到 200 字以内

### sound_effect
- `data` 必填
- 可选：`use_audio_fx`（默认 true）、`analysis_mode`（默认 2）、`data_mode`（默认 1）

### chapter_split
- 必填：`content_file`、`filename`
- 可选：`max_chapter_length`、`handle_intro_text`、`enable_ai_fallback`、`start_chapter_number`、`enable_loose_patterns`、`ai_spliter`、`auto_cleaner`

### chapter_character_analysis
- `content_file`、`content`、`content_text` 三选一（`content_text` 是 `content` 同义字段）
- 可选：`context_window`、`max_window_length`、`scope`、`max_characters`

### dialogue_split
- `text_list` 或 `lines` 至少一项
- 可选：`chapter_name/context_window/max_window_length`
- 注意：传 `text_list` 时不会做真实说话人识别，对白段 `speaker` 会固定为“对白”；若要尽量提取说话人，优先传 `lines`

### chapter_character_predict
- `text_list` 必填
- 可选：`scope/max_characters`
- 建议 `text_list` 段落数不超过 200（底层模型链路对超长输入会退化/报错）

### character_analyze
- `content_file` 必填
- 可选：`max_dialogues_per_character/include_relationships`

### search_faq
- `query` 必填
- `top_k` 可选（默认 3）

### annotate_pinyin
- `text` 必填

### image_generation
- `prompt` 必填

## 6. 失败处理规范

1. 鉴权失败：明确提示“token 无效或过期，请在个人中心重新生成 token 后重试”。
2. 工具超时：明确提示“该能力处理时间较长，本次超时，请稍后重试”。
3. 业务失败（`success=false`）：直接转述 `msg`，不加臆测结论。
4. 不存在的工具：先 `tools/list` 校验后再路由，不要硬调。

## 7. 最佳实践组合（推荐工作流）

### 7.1 首次接入自检（建议每次会话首轮执行）
1. `tools/list`：确认服务在线与工具集。
2. `read_abs(scope.domain=books)`：验证 token 权限与团队上下文。
3. 若 `read_abs` 成功，再执行用户任务；若失败，优先提示用户检查 token 是否过期/绑定错误团队。

### 7.2 “查某本书最后一章”
1. `read_abs({"scope":{"domain":"books"}})`：按书名匹配 book_id。
2. `read_abs({"scope":{"domain":"book","book_id":"<id>"}})`：取章节列表并定位最后一章 chapter_id。
3. `read_abs({"scope":{"domain":"chapter","book_id":"<id>","chapter_id":"<id>"}})`：返回正文并生成摘要。

### 7.3 “新建书并写入第一章”（最小闭环）
1. `read_abs(books)` 取可用 `team_id`。
2. `patch_abs(create_book)`：`scope={"domain":"book"}` 且不传 `book_id`。
3. `patch_abs(add_chapter)`：对新书 `book_id` 添加第一章。
4. `read_abs(book)` 回读验证写入结果。

### 7.4 `search_audio` 正确用法（给 OpenClaw 的 TTS 适配重点）
1. `search_audio(user_query=用户原话)`。
2. 判断返回来源：
- 若 `source=mock`：代表命中已有素材（可能是 `audio_url`，也可能是本地 `audio_path`）。
- 若 `source=generated`：代表已完成“文本生成 + 音色推荐 + TTS 合成”。
3. 若用户明确要“新生成 TTS”但命中 `mock`，需先告知“当前命中已有素材”，再询问是否改成更具体需求重试以触发生成链路。
4. 若生成链路失败（常见：无法获取可用音色 ID / 下游 TTS 失败），只转述真实错误，不编造成功结果。

### 7.5 `search_audio` 能力边界（必须告知模型）
1. `search_audio` 一次调用只能产出 1 条结果，不支持 `top_k`/分页。
2. 生成链路内部会先写短文本（约 100 字），TTS 侧最终还会截断到 200 字以内；不适合长章节整段合成。
3. 生成链路的音色选择是自动匹配，不能在该工具里强制指定特定 `speaker_id`。
4. 想提高“按用户意图生成”的命中率，`user_query` 应包含：
- 内容主题（讲什么）
- 风格/情绪（温柔、悬疑、热血等）
- 角色倾向（男女声、年龄段）
5. 若用户要求精细控音色/多版本对比，优先改用 `timber_assign` + 其他可控链路，不要把 `search_audio` 当成可编排 TTS 引擎。

### 7.6 “章节音效生产链路”
1. 先准备章节结构化 `data`。
2. 调 `sound_effect`（默认 `analysis_mode=2`）。
3. 结果回显时保留关键字段（新增段落、音效建议、命中素材 URL），不要整段原始 JSON 直出。

### 7.7 “角色分析推荐链路”
1. 单章分析优先：`chapter_character_analysis`。
2. 若用户已有拆分文本：`dialogue_split -> chapter_character_predict`。
3. 全书/长文本角色抽取：`character_analyze`（注意可能耗时长，需超时提示）。

### 7.8 角色链路能力边界（避免误路由）
1. `dialogue_split` 用 `text_list` 入参时，本质是格式转换，不会可靠识别对白说话人。
2. 需要“逐段 speaker_name”时，优先走：`lines -> dialogue_split -> chapter_character_predict`。
3. 单章文本较长时，`chapter_character_analysis`/`chapter_character_predict` 属于 LLM 推断结果，应以“建议值”呈现，不要宣称绝对准确。

### 7.9 指定文本+音色ID 的 TTS 最佳实践（OpenClaw 必须优先）
1. 当用户意图包含“用这段文本 + 指定音色/某个 speakerId 合成”时，优先走 `list_tts_voices -> synthesize_tts`。
2. 若用户只给“音色名称”未给 ID，先 `list_tts_voices`，按 `speakerName` 匹配确认后再调 `synthesize_tts`。
3. 若用户未指定音色，只描述风格（如“温柔女声”），优先 `timber_assign` 做推荐试听；需要固定单音色再转 `synthesize_tts`。
4. 若 `synthesize_tts` 不在本轮 `tools/list`，回退到 `timber_assign` 或 `search_audio`，并明确告知“当前环境不支持直指定 speaker_id 合成”。
5. 返回结果时优先给 `audio_url` 与实际使用的 `speaker_id`；若文本超过 200 字，需提示已被服务端截断。

### 7.10 专辑创作与上传全链路（AI 批量生产）
1. **创建专辑**：若用户未指定专辑 ID，先调 `create_album(album_name, book_type, book_content/book_file)`。
2. **批量生产内容**：
   - 使用 `text_writing` 或 LLM 自身能力生成多集文案（每集建议 1500 字左右）。
   - 记录每集的标题与正文。
3. **音色匹配与合成**：
   - 若用户指定音色（如“喜安之”），先调 `list_tts_voices` 获取 `speakerId`。
   - 循环调用 `synthesize_tts(text, speaker_id)` 为每一集生成音频 URL。
4. **上传与发布**：
   - 调 `upload_audio_to_album(album_id, audio_url, title)` 将合成好的音频挂载到指定专辑。
   - 循环执行直至所有集数处理完毕。
5. **异常处理**：若 TTS 合成失败（如 `audioUrl` 为空），应记录失败集数并提示用户重试，不要中断后续上传。

### 7.11 语音识别
1. **ASR 识别**：使用 `asr_audio_to_text(audio_url)` 将长音频转为文字。

## 8. 调试附录（仅供开发）

```bash
# 1) initialize（记录响应头里的 mcp-session-id）
curl -i -sS -X POST "https://aigc.ximalaya.com/audiobooklm/mcp" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer ${AUDIOBOOKLM_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"openclaw","version":"1.0.0"}}}'

# 2) initialized（带 mcp-session-id）
curl -i -sS -X POST "https://aigc.ximalaya.com/audiobooklm/mcp" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer ${AUDIOBOOKLM_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "mcp-session-id: <session-id>" \
  -d '{"jsonrpc":"2.0","method":"notifications/initialized","params":{}}'

# 3) tools/list（带 mcp-session-id）
curl -i -sS -X POST "https://aigc.ximalaya.com/audiobooklm/mcp" \
  -H "Accept: application/json, text/event-stream" \
  -H "Authorization: Bearer ${AUDIOBOOKLM_TOKEN}" \
  -H "Content-Type: application/json" \
  -H "mcp-session-id: <session-id>" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
```

## 9. 更新日志（OpenClaw）

### 0.0.7（2026-03-13）
1. 优化鉴权链路：支持通过token完成音色查询与合成。
2. 新增`create_album`，`upload_audio_to_album`，`list_tts_voices`，`synthesize_tts`，`asr_audio_to_text` tools

### 0.0.6（2026-03-13）
1. 修正 `search_audio` 能力描述：明确“mock 命中优先，未命中才自动文生音频（LLM 文案 + 音色推荐 + TTS）”，避免误当作通用站内音频检索。
2. 新增“指定文本 + 指定音色ID”最佳实践：优先 `list_tts_voices -> synthesize_tts`，并补齐回退与截断提示规则。
3. 补全关键工具边界：`tools/list` 动态路由原则、`chapter_character_analysis` 的 `content_text` 同义入参、`dialogue_split` 在 `text_list` 模式下仅做格式转换的限制。
