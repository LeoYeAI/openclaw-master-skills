# Prompt: 基于《The Complete Guide to Building Skills for Claude》的 doubao-asr 迭代建议

> 以下内容来自另一个 session 的分析成果。该 session 完整阅读了 Anthropic 官方发布的《The Complete Guide to Building Skills for Claude》(PDF, 32页)，并结合 doubao-asr 项目现状给出了具体的迭代建议。请消化这些信息并执行改进。

---

## 一、指南核心要点摘要

### 1. Skill 文件结构规范

```
your-skill-name/          # kebab-case 命名
├── SKILL.md               # 必须，大小写敏感
├── scripts/               # 可选，可执行代码
├── references/            # 可选，按需加载的文档
└── assets/                # 可选，模板、图标等
```

- 不要在 skill 文件夹内放 README.md（README 用于 GitHub 仓库层面给人类看，不放在 skill 内部）
- SKILL.md 建议控制在 5000 词以内

### 2. 三级渐进披露（Progressive Disclosure）

这是指南最核心的设计理念：

- **第一级（YAML frontmatter）**：始终加载到 Claude 的 system prompt。只提供"这个 skill 干什么、何时触发"的最少信息。
- **第二级（SKILL.md body）**：当 Claude 判断 skill 与当前任务相关时加载。包含完整指令。
- **第三级（references/ 链接文件）**：Claude 按需导航和发现。详细文档放这里。

目的：最小化 token 消耗，同时保留专业能力。

### 3. YAML Frontmatter — description 字段的写法

description 必须同时包含：
- **做什么**（What it does）
- **何时使用**（When to use — trigger conditions）
- 具体的用户可能说的短语
- 相关文件类型（如适用）
- 不超过 1024 字符，不含 XML 标签

好的例子：
```yaml
description: "Analyzes Figma design files and generates developer handoff documentation. Use when user uploads .fig files, asks for 'design specs', 'component documentation', or 'design-to-code handoff'."
```

坏的例子：
```yaml
description: "Helps with projects."  # 太模糊
description: "Creates sophisticated multi-page documentation systems."  # 缺少触发条件
```

**负面触发（Negative Triggers）**：防止 overtriggering
```yaml
description: "...Do NOT use for simple data exploration (use data-viz skill instead)."
```

### 4. 三类 Skill 用例

| 类别 | 说明 | doubao-asr 属于 |
|------|------|----------------|
| Category 1: 文档/资产创建 | 创建一致的高质量输出 | ❌ |
| Category 2: 工作流自动化 | 多步骤流程 + 一致方法论 | ❌ |
| Category 3: MCP 增强 | 为工具访问添加工作流知识 | ✅ 最接近 |

### 5. 五种设计模式

- **Pattern 1: 顺序工作流编排** — 多步骤按特定顺序执行
- **Pattern 2: 多 MCP 协调** — 跨多个服务的工作流
- **Pattern 3: 迭代精炼** — 输出质量通过迭代提升
- **Pattern 4: 上下文感知工具选择** — 同一目标，根据上下文选不同工具（doubao-asr 的区域选择逻辑适用此模式）
- **Pattern 5: 领域知识嵌入** — skill 添加超越工具访问的专业知识（doubao-asr 的 Agent Instruction 和错误黑名单正是此模式）

### 6. 测试方法论

指南推荐三层测试：

1. **触发测试**：skill 是否在正确时机加载？（目标：90% 相关查询触发）
2. **功能测试**：输出是否正确？API 调用是否成功？
3. **性能对比**：有无 skill 的效果差异

调试方法：问 Claude "When would you use the [skill name] skill?" — Claude 会引用 description 回答，据此调整。

### 7. Troubleshooting 段的推荐格式

```markdown
## Troubleshooting
### Error: [Common error message]
Cause: [Why it happens]
Solution: [How to fix]
```

### 8. 其他要点

- `allowed-tools` 字段可限制 skill 的工具访问范围（如 `"Bash(python3:*)"`)
- 关键指令放在 SKILL.md 顶部，使用 `## Important` 或 `## Critical` 标题
- 对于关键验证，考虑用 script 而非语言指令——代码是确定性的，语言解释不是
- 对付模型"偷懒"：加 "Take your time to do this thoroughly" / "Quality is more important than speed"（但指南指出这在用户 prompt 中比在 SKILL.md 中更有效）

---

## 二、doubao-asr 现状评估

### 已经做得好的

1. ✅ description 包含触发词（"transcribe recorded audio files", "Doubao/豆包/Volcengine/火山引擎"）
2. ✅ kebab-case 命名 `doubao-asr`
3. ✅ metadata 完整（author, version, homepage, tags, requires）
4. ✅ Agent Instruction v2 + 错误黑名单 — 完全对应 Pattern 5（领域知识嵌入），这是项目亮点
5. ✅ transcribe.py 有重试机制和清晰错误信息
6. ✅ 区域选择决策树 — 对应 Pattern 4（上下文感知工具选择）

### 需要改进的

以下按优先级排序：

---

## 三、具体迭代任务（请执行）

### 任务 1: 🔴 README.md 同步 TOS_REGION 为 Required（2 分钟）

README.md 凭证表中 `VOLCENGINE_TOS_REGION` 标记为 `Required: No`，但最新 commit（8a6f2ca）已将其改为必填。需同步更新为 `Required: Yes`。

### 任务 2: 🔴 description 补充负面触发条件（5 分钟）

当前 description 没有排除条件，可能导致 overtriggering。在 description 末尾追加：

```
Do NOT use for real-time/streaming speech recognition, text-to-speech (TTS), or live captioning.
```

注意保持总长度在 1024 字符以内。

### 任务 3: 🟡 SKILL.md 添加 Troubleshooting 段（10 分钟）

在 SKILL.md 末尾（Supported formats 之后）添加：

```markdown
## Troubleshooting

### TOS upload extremely slow (~15KB/s) / TOS 上传极慢
**Cause**: Bucket region mismatch — server is overseas but bucket is in cn-beijing
**Solution**: Create a new bucket in `cn-hongkong`, update `VOLCENGINE_TOS_REGION=cn-hongkong`

原因：桶区域不匹配——服务器在海外但桶在 cn-beijing
解决：在 cn-hongkong 新建桶，更新 VOLCENGINE_TOS_REGION=cn-hongkong

### Submit failed: status code not 20000000 / 提交失败
**Cause**: Invalid or expired API key
**Solution**: Re-generate API key at https://console.volcengine.com/speech/new/ → API Call → Step 1

原因：API Key 无效或过期
解决：在 https://console.volcengine.com/speech/new/ → API 调用 → 第一步，重新创建

### "Silent audio, no transcript" / 静音音频
**Cause**: Audio file has no detectable speech
**Solution**: Verify audio plays correctly. Ensure format is supported (WAV/MP3/MP4/M4A/OGG/FLAC)

原因：音频中未检测到语音
解决：确认音频能正常播放，格式受支持

### TOS upload failed (403) / TOS 上传 403 错误
**Cause**: Bucket policy not configured or IAM key mismatch
**Solution**: Check bucket → Permission Management → verify "Folder Read/Write" policy exists and is applied to your main account

原因：桶策略未配置或 IAM 密钥不匹配
解决：进入桶 → 权限管理 → 确认已添加「文件夹读写」策略并授权给当前主账号
```

### 任务 4: 🟡 创建触发测试用例（10 分钟）

创建 `references/trigger-tests.md`：

```markdown
# doubao-asr Trigger Tests

Based on Anthropic's skill testing methodology.

## Should trigger ✅

- "帮我转写这段录音"
- "用豆包识别这个音频文件"
- "transcribe this audio file"
- "我有一段会议录音需要转成文字"
- "火山引擎语音识别"
- "doubao asr this mp3"
- "把这个 m4a 文件转成文字"
- "transcribe with speaker diarization"
- "用 Volcengine 转写"
- "帮我识别这段音频里说了什么"

## Should NOT trigger ❌

- "帮我做语音合成"（TTS, not ASR）
- "实时语音转文字"（streaming, not recorded file）
- "翻译这段文字"（translation, not transcription）
- "帮我写 Python 代码"（general programming）
- "用 Whisper 转写"（different tool）
- "今天天气怎么样"（unrelated）
- "帮我录一段音频"（recording, not transcription）

## Debugging method

Ask Claude: "When would you use the doubao-asr skill?"
Claude should quote the description back. Adjust based on what's missing.
```

### 任务 5: 🟢 考虑拆分凭证配置到 references/（20 分钟）

这是一个需要权衡的改进。指南建议 SKILL.md 控制在 5000 词以内，详细文档放 references/。但 doubao-asr 的 Agent Instruction 要求"展示完整引导"。

**折中方案**：
- 创建 `references/credentials-setup.md`，将 Step 1-3 完整内容移入
- SKILL.md 凭证段改为简短概述 + 指向 references 的链接
- Agent Instruction 改为：*"当用户需要配置凭证时，读取并展示 `references/credentials-setup.md` 的完整内容"*

**注意**：此任务需要验证 Claude 是否真的会按指令去读取 references/ 文件。如果不确定，可以先跳过，等有测试环境后再做。

### 任务 6: 🟢 添加 allowed-tools 字段（2 分钟）

在 YAML frontmatter 中添加：

```yaml
allowed-tools: "Bash(python3:*)"
```

这限制 skill 只能通过 Bash 执行 python3 命令，增加安全边界。

---

## 四、执行注意事项

1. 所有改动遵循项目现有的治理规范（AGENTS.md）
2. 改动后需写 task log（`docs/workspace/logs/YYYYMMDD_*.md`）
3. 显式 stage 文件（不要 `git add -A`）
4. 保持双语（中英文）风格一致
5. description 修改后可以用调试方法验证：问 Claude "When would you use the doubao-asr skill?"
