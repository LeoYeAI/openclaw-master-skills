# 全局规则

## 素材感知顺序
1. get_duration
2. get_resolution
3. video_detail
4. asr_llm
5. asr_nlp
6. asr_basic

## 通用策略
- 先获取时长，再做视觉和语音理解。
- 纯音频可跳过 video_detail。
- 无人声视频可跳过 asr_*。
- ASR 默认优先 asr_llm，失败后按 asr_nlp -> asr_basic 顺序降级。
- ASR 三接口回包结构不一致：`asr_basic` 解析 `result.raw.result.utterances`，`asr_nlp/asr_llm` 解析 `segments`。
- 内部统一使用秒；如果上游返回毫秒，先换算为秒。
- 执行端点请求时默认使用 `curl`，复杂任务才去生成 Python 业务编排代码。
- 云渲染标准流程：`generate_video` 发起任务，`output.task_status` 轮询到 `output.result`不为空 后返回可播放链接`output.result`。

## 通用异常处理
- 当接口返回 `{ "Code": "JWTTokenIsMissing", "Message": "the jwt token is missing" }` 时：先到 `https://www.vectcut.com` 登录并获取个人 API Key，然后设置环境变量 `VECTCUT_API_KEY` 后重试。

## 领域规则入口
- 滤镜端点（add_filter / modify_filter / remove_filter）异常处理见：`rules/filter_rules.md`
- 特效端点（add_effect / modify_effect / remove_effect）异常处理见：`rules/effect_rules.md`
- 素材感知端点（get_duration / get_resolution / video_detail）异常处理见：`rules/material_rules.md`
- ASR 端点（asr_basic / asr_nlp / asr_llm）异常处理见：`rules/asr_rules.md`
- 草稿管理端点（create_draft / modify_draft / remove_draft / query_script）异常处理见：`rules/draft_rules.md`
- 云渲染端点（generate_video / task_status）异常处理见：`rules/generate_video_rules.md`
- 贴纸端点（search_sticker / add_sticker）异常处理见：`rules/sticker_rules.md`