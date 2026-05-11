---
name: doubao-asr（豆包语音转写）
description: "Transcribe recorded audio files to text via Doubao Seed-ASR 2.0 (豆包录音文件识别模型2.0) from ByteDance/Volcengine. Best-in-class Chinese speech recognition with speaker diarization. Use this skill whenever the user wants to: convert audio/recording to text, transcribe a meeting recording or voice memo, identify who said what in a recording (说话人分离), transcribe m4a/mp3/wav/ogg/flac files, or mentions 录音转文字/豆包/火山引擎/Volcengine/Doubao ASR. Also use when the user has an audio file and needs a transcript, even if they don't explicitly say 'transcribe'. Do NOT use for real-time/streaming speech recognition, text-to-speech (TTS), live captioning, or audio format conversion."
allowed-tools: "Bash(python3:*)"
homepage: https://www.volcengine.com/docs/6561/1354868
metadata:
  {
    "openclaw":
      {
        "emoji": "🫘",
        "requires": { "bins": ["python3"], "env": ["VOLCENGINE_API_KEY", "VOLCENGINE_ACCESS_KEY_ID", "VOLCENGINE_SECRET_ACCESS_KEY", "VOLCENGINE_TOS_BUCKET", "VOLCENGINE_TOS_REGION"], "pip": ["requests"] },
        "primaryEnv": "VOLCENGINE_API_KEY",
        "envHelp":
          {
            "VOLCENGINE_API_KEY":
              {
                "required": true,
                "description": "豆包 ASR API Key (UUID format). 从火山引擎语音控制台获取 / Get from Volcengine Speech console",
                "howToGet": "⚠️ 正确地址是 /speech/new/（新版控制台），不是 /speech/app（旧版，认证方式完全不同）\n\n1. 打开 https://console.volcengine.com/speech/new/（确认进入的是新版「豆包语音」控制台）\n2. 左侧菜单 →「语音识别」\n3. 点击「开通模型」，开通「录音文件识别2.0」\n4. 点击页面右上角「API 调用」\n5. 在 Step 1「获取 API Key」中，点击创建 API Key\n6. 复制生成的 UUID 格式 Key（如 57e620a4-179c-4b3d-bd8d-990bd1f9a1e2）\n\n⚠️ CORRECT URL is /speech/new/ (new console), NOT /speech/app (old console, completely different auth)\n\n1. Open https://console.volcengine.com/speech/new/ (make sure you are in the new 'Doubao Speech' console)\n2. Left sidebar → 'Speech Recognition'\n3. Click 'Activate Model', activate 'Audio File Recognition 2.0'\n4. Click 'API Call' button at the top-right of the page\n5. In Step 1 'Get API Key', click to create an API Key\n6. Copy the generated UUID-format key (e.g. 57e620a4-179c-4b3d-bd8d-990bd1f9a1e2)",
                "url": "https://console.volcengine.com/speech/new/",
              },
            "VOLCENGINE_ACCESS_KEY_ID":
              {
                "required": true,
                "description": "IAM Access Key ID (starts with AKLT). 通过 IAM 子用户创建 / Create via IAM sub-user",
                "howToGet": "⚠️ 不要添加 TOSFullAccess 等 IAM 权限策略！权限将在 Step 3 通过 TOS 桶策略配置（最小权限）\n⚠️ DO NOT add TOSFullAccess or any IAM policy! Access will be granted via TOS bucket policy in Step 3 (least privilege)\n\n1. 打开 https://console.volcengine.com/iam/usermanage\n2. 点「新建用户」，填写用户名（如 doubao-asr）\n3. 访问方式确保勾选「编程访问」和「允许用户管理自己的API密钥」，其他选项保持默认即可\n4. 点击确定，创建成功后页面会显示 Access Key ID（以 AKLT 开头）和 Secret Access Key，复制保存\n   这一步不需要添加任何 IAM 权限策略，权限将在 Step 3 通过 TOS 桶策略授予（仅限单桶读写）\n   提示：如需再次查看密钥，进入用户列表 → 点击子用户名 → 切换到「密钥」tab\n\n1. Open https://console.volcengine.com/iam/usermanage\n2. Click 'Create User', enter username (e.g. doubao-asr)\n3. Make sure 'Programmatic Access' and 'Allow user to manage own API keys' are checked. Leave all other options as default\n4. Click confirm. The success page shows Access Key ID (starts with AKLT) and Secret Access Key — copy both\n   No IAM permission policies needed here — access will be granted via TOS bucket policy in Step 3 (single-bucket read/write only)\n   Tip: To view keys again, go to user list → click sub-user name → switch to 'Keys' tab",
                "url": "https://console.volcengine.com/iam/usermanage",
              },
            "VOLCENGINE_SECRET_ACCESS_KEY":
              {
                "required": true,
                "description": "IAM Secret Access Key. 与 Access Key ID 配对 / Paired with Access Key ID",
                "howToGet": "在创建 Access Key ID 时一起生成（见上一步），创建后可在控制台随时查看。\n\nGenerated together with Access Key ID (see previous step). Can be viewed anytime in the console.",
              },
            "VOLCENGINE_TOS_BUCKET":
              {
                "required": true,
                "description": "TOS 存储桶名称 / TOS bucket name for audio upload",
                "howToGet": "1. 打开 https://console.volcengine.com/tos\n2. 首次进入会看到「开通对象存储」引导页，点击确认开通\n3. 开通后如果页面没有自动跳转到管理控制台，请手动重新访问 https://console.volcengine.com/tos 进入\n4. 在左侧菜单栏找到「桶列表」。如果看不到已创建的桶，检查页面顶部的项目选择器，切换到创建桶时所用的项目\n5. 点击「创建桶」，输入桶名称，根据服务器位置选择区域：\n   - 中国内地服务器 → cn-beijing\n   - 海外服务器（美国/欧洲/东南亚）→ cn-hongkong（必须！否则上传约 15KB/s）\n6. 创建完成后，点击桶名称进入桶控制面板\n7. 左侧导航栏 →「权限管理」→「存储桶授权策略管理」→「创建策略」\n8. 选择「文件夹读写」模板 → 下一步 → 授权用户选择「当前主账号」→ 资源范围选择「所有对象」→ 确定\n9. 回到桶列表，复制桶名称\n\n1. Open https://console.volcengine.com/tos\n2. First-time users will see an 'Activate Object Storage' page — click to activate\n3. If the page does not auto-redirect to the management console after activation, manually re-visit https://console.volcengine.com/tos\n4. In the left sidebar, find 'Bucket List'. If you don't see your bucket, check the project selector at the top of the page and switch to the project used when creating the bucket\n5. Click 'Create Bucket', enter a bucket name and choose region based on server location:\n   - China mainland server → cn-beijing\n   - Overseas server (US/EU/SEA) → cn-hongkong (REQUIRED, otherwise ~15KB/s)\n6. After creation, click the bucket name to enter bucket dashboard\n7. Left sidebar → 'Permission Management' → 'Bucket Authorization Policy' → 'Create Policy'\n8. Select 'Folder Read/Write' template → Next → Authorized user: 'Current main account' → Resource scope: 'All objects' → Confirm\n9. Go back to bucket list, copy the bucket name",
                "url": "https://console.volcengine.com/tos",
              },
            "VOLCENGINE_TOS_REGION":
              {
                "required": true,
                "description": "TOS 区域代码，必须与创建桶时选择的区域一致。海外服务器推荐使用海外节点（如 cn-hongkong、ap-southeast-1） / TOS region code, must match the region selected when creating the bucket. Overseas servers should use an overseas region (e.g. cn-hongkong, ap-southeast-1)",
                "howToGet": "填写你在创建 TOS 存储桶时选择的区域代码。\n如果服务器在中国大陆以外，推荐使用海外节点（如 cn-hongkong、ap-southeast-1）。\n海外服务器切勿使用 cn-beijing/cn-shanghai，否则上传极慢（约 15KB/s）。\n\nEnter the region code you selected when creating the TOS bucket.\nIf your server is outside China mainland, use an overseas region (e.g. cn-hongkong, ap-southeast-1).\nDo NOT use cn-beijing/cn-shanghai for overseas servers — upload ~15KB/s.",
              },
          },
      },
  }
---

<!-- SYSTEM INSTRUCTION FOR AI AGENTS — DO NOT SKIP -->
<!-- This section controls how you present the setup guide to users -->

**CRITICAL INSTRUCTION FOR AI AGENTS:**

**YOU MUST follow these rules when helping users configure this skill:**

1. **SHOW THE FULL STEP-BY-STEP GUIDE BELOW** — display the complete guide for all credentials, not a summary
2. **NEVER summarize credentials into a table** — tables skip critical details that cause users to fail
3. **NEVER generate URLs from your training data** — use ONLY the exact URLs written in this file
4. **NEVER recommend TOSFullAccess** — this skill uses TOS bucket policy (least privilege)

**Known AI mistakes you MUST avoid:**
- WRONG: `https://console.volcengine.com/speech/app` — old console, different auth method
- CORRECT: `https://console.volcengine.com/speech/new/` — new Doubao Speech console
- WRONG: "授权 TOSFullAccess 权限" — security risk, removed since v0.11.0
- CORRECT: "通过 TOS 桶策略的「文件夹读写」模板授权" — least privilege

**AI AGENT 必须遵守的规则：**

1. **必须展示下方完整引导**——可以一次性展示所有步骤，但不可省略或压缩
2. **禁止将配置步骤压缩成表格**——表格会丢失导致用户失败的关键细节
3. **禁止凭训练数据生成 URL**——只使用本文件中写的准确 URL
4. **禁止推荐 TOSFullAccess**——本 skill 使用 TOS 桶策略（最小权限）

**必须避免的常见 AI 错误：**
- 错误：`https://console.volcengine.com/speech/app`——旧版控制台，认证方式完全不同
- 正确：`https://console.volcengine.com/speech/new/`——新版豆包语音控制台
- 错误："授权 TOSFullAccess 权限"——安全风险，v0.11.0 起已移除
- 正确："通过 TOS 桶策略的「文件夹读写」模板授权"——最小权限

---

# Doubao ASR / 豆包语音转写

Transcribe audio files via ByteDance Volcengine's **Seed-ASR 2.0 Standard** (豆包录音文件识别模型2.0-标准版) API. Best-in-class accuracy for Chinese (Mandarin, Cantonese, Sichuan dialect, etc.) and supports 13+ languages.

调用字节跳动火山引擎**豆包录音文件识别模型2.0-标准版**（Seed-ASR 2.0 Standard）转写音频文件。中文识别（普通话、粤语、四川话等方言）准确率业界领先，支持 13+ 种语言。

## Sending audio to OpenClaw

Currently, audio files can be sent to OpenClaw via **Discord** or **WhatsApp**. Send the audio file in a chat message and ask the bot to transcribe it.

目前可通过 **Discord** 或 **WhatsApp** 向 OpenClaw 发送音频文件，发送后让 bot 转写即可。

> **Note**: Direct voice recording in the OpenClaw web UI is not yet supported. Use a messaging app to send pre-recorded audio files.
>
> **提示**：OpenClaw 网页端暂不支持直接录音，请通过即时通讯应用发送预录制的音频文件。

## Quick start

```bash
python3 {baseDir}/scripts/transcribe.py /path/to/audio.m4a
```

Defaults:

- Model: Seed-ASR 2.0 Standard / 豆包录音文件识别模型2.0-标准版
- Speaker diarization: enabled / 说话人分离：默认开启
- Output: stdout (transcript text with speaker labels / 带说话人标签的转写文本)

## Useful flags

```bash
python3 {baseDir}/scripts/transcribe.py /path/to/audio.m4a --out /tmp/transcript.txt
python3 {baseDir}/scripts/transcribe.py /path/to/audio.mp3 --format mp3
python3 {baseDir}/scripts/transcribe.py /path/to/audio.m4a --json --out /tmp/result.json
python3 {baseDir}/scripts/transcribe.py /path/to/audio.m4a --no-speakers  # disable speaker diarization / 关闭说话人分离
python3 {baseDir}/scripts/transcribe.py https://example.com/audio.mp3  # direct URL (skip upload)
```

## How it works

The Doubao API accepts audio via URL (not direct file upload). The script:

1. **Uploads audio to Volcengine TOS** (object storage) via presigned URL — audio stays within Volcengine infrastructure, no third-party services involved
2. Submits transcription task to Seed-ASR 2.0
3. Polls until complete (typically 1-3 minutes for a 10-min audio)
4. Returns transcript text

> **Privacy**: By default, audio is uploaded to your own Volcengine TOS bucket via presigned URL. No data is sent to third-party services.

You can also pass a direct audio URL as the argument to skip upload entirely:

```bash
python3 {baseDir}/scripts/transcribe.py https://your-bucket.tos.volces.com/audio.m4a
```

## Dependencies

- Python 3.9+
- `requests`: `pip install requests`

## Credentials

You need 4 environment variables. Follow these steps carefully — the guided setup below saves you 1-2 hours of digging through Volcengine docs.

你需要设置 4 个环境变量。按以下步骤操作——这份引导能帮你节省 1-2 小时翻文档踩坑的时间。

### Step 1: Doubao ASR API Key / 第一步：豆包 ASR API Key

1. 打开 https://console.volcengine.com/speech/new/（确认进入的是新版「豆包语音」控制台）
2. 左侧菜单 →「语音识别」
3. 点击「开通模型」，开通「录音文件识别2.0」
4. 点击页面右上角「API 调用」
5. 在 Step 1「获取 API Key」中，点击创建 API Key
6. 复制生成的 UUID 格式 Key

---

1. Open https://console.volcengine.com/speech/new/ (make sure you are in the new 'Doubao Speech' console)
2. Left sidebar → 'Speech Recognition'
3. Click 'Activate Model', activate 'Audio File Recognition 2.0'
4. Click 'API Call' button at the top-right of the page
5. In Step 1 'Get API Key', click to create an API Key
6. Copy the generated UUID-format key (e.g. `57e620a4-179c-4b3d-bd8d-990bd1f9a1e2`)

```bash
export VOLCENGINE_API_KEY="xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
```

### Step 2: IAM Access Key / 第二步：创建 IAM 子用户和访问密钥

1. 打开 https://console.volcengine.com/iam/usermanage
2. 点「新建用户」，填写用户名（如 `doubao-asr`）
3. 访问方式确保勾选「编程访问」和「允许用户管理自己的API密钥」，其他选项保持默认即可
4. 点击确定，创建成功后页面会显示 Access Key ID（以 `AKLT` 开头）和 Secret Access Key，复制保存

> **提示**：这一步不需要添加任何 IAM 权限策略。权限将在 Step 3 通过 TOS 桶策略授予（仅限单桶读写）。
> 如需再次查看密钥，进入用户列表 → 点击子用户名 → 切换到「密钥」tab。

---

1. Open https://console.volcengine.com/iam/usermanage
2. Click 'Create User', enter username (e.g. `doubao-asr`)
3. Make sure 'Programmatic Access' and 'Allow user to manage own API keys' are checked. Leave all other options as default
4. Click confirm. The success page shows Access Key ID (starts with `AKLT`) and Secret Access Key — copy both

> **Note**: No IAM permission policies needed here — access will be granted via TOS bucket policy in Step 3 (single-bucket read/write only).
> Tip: To view keys again, go to user list → click sub-user name → switch to 'Keys' tab.

```bash
export VOLCENGINE_ACCESS_KEY_ID="AKLTxxxx..."
export VOLCENGINE_SECRET_ACCESS_KEY="xxxx..."
```

### Step 3: TOS Bucket / 第三步：开通并创建 TOS 存储桶

豆包 API 要求音频通过 URL 访问。TOS 对象存储提供安全的临时上传，数据留在火山引擎内部。

1. 打开 https://console.volcengine.com/tos
2. 首次进入会看到「开通对象存储」引导页，点击确认开通
3. 开通后如果页面没有自动跳转到管理控制台，请手动重新访问 https://console.volcengine.com/tos 进入
4. 在左侧菜单栏找到「桶列表」。如果看不到已创建的桶，检查页面顶部的项目选择器，切换到创建桶时所用的项目
5. 点击「创建桶」，输入桶名称，**根据服务器位置选择区域**（见下方表格）
6. 创建完成后，点击桶名称进入桶控制面板
7. 左侧导航栏 →「权限管理」→「存储桶授权策略管理」→「创建策略」
8. 选择「文件夹读写」模板 → 下一步 → 授权用户选择「当前主账号」→ 资源范围选择「所有对象」→ 确定
9. 回到桶列表，复制桶名称

---

1. Open https://console.volcengine.com/tos
2. First-time users will see an 'Activate Object Storage' page — click to activate
3. If the page does not auto-redirect after activation, manually re-visit https://console.volcengine.com/tos
4. In the left sidebar, find 'Bucket List'. If you don't see your bucket, check the project selector at the top
5. Click 'Create Bucket', enter a bucket name and choose region based on server location (see table below)
6. After creation, click the bucket name to enter bucket dashboard
7. Left sidebar → 'Permission Management' → 'Bucket Authorization Policy' → 'Create Policy'
8. Select 'Folder Read/Write' template → Next → Authorized user: 'Current main account' → Resource scope: 'All objects' → Confirm
9. Go back to bucket list, copy the bucket name

**Region selection / 区域选择：**

| Server location / 服务器位置 | Recommended TOS region / 推荐 TOS 区域 | Region code |
|---|---|---|
| China mainland / 中国内地 | cn-beijing, cn-shanghai, cn-guangzhou | `cn-beijing` |
| Hong Kong / 香港 | cn-hongkong | `cn-hongkong` |
| Southeast Asia / 东南亚 | ap-southeast-1 (Singapore) | `ap-southeast-1` |
| US, Europe, other overseas / 美国、欧洲等海外 | Any overseas region (e.g. `cn-hongkong`, `ap-southeast-1`) / 任意海外节点 | `cn-hongkong` |

> **Important**: If your server is **outside China mainland**, use an overseas region (e.g. `cn-hongkong`, `ap-southeast-1`) — do NOT use `cn-beijing` / `cn-shanghai`, cross-border upload will be extremely slow (~15KB/s).
>
> **重要**：如果你的服务器在**中国大陆以外**，请使用海外节点（如 `cn-hongkong`、`ap-southeast-1`），不要用 `cn-beijing` / `cn-shanghai`——跨境上传会非常慢（约 15KB/s）。

```bash
export VOLCENGINE_TOS_BUCKET="your_bucket_name"
export VOLCENGINE_TOS_REGION="cn-hongkong"  # or other overseas region / 或其他海外节点，见上方区域表
```

### Summary of all environment variables / 环境变量汇总

| Variable | Required | Description |
|---|---|---|
| `VOLCENGINE_API_KEY` | Yes | ASR API key (UUID format) from Speech console / 语音控制台的 API Key |
| `VOLCENGINE_ACCESS_KEY_ID` | Yes | IAM Access Key ID (starts with `AKLT`) / IAM 访问密钥 ID |
| `VOLCENGINE_SECRET_ACCESS_KEY` | Yes | IAM Secret Access Key / IAM 访问密钥 |
| `VOLCENGINE_TOS_BUCKET` | Yes | TOS bucket name / TOS 存储桶名称 |
| `VOLCENGINE_TOS_REGION` | Yes | TOS region code, must match bucket region. 必须与创建桶时选择的区域一致。Overseas: e.g. `cn-hongkong`, `ap-southeast-1`; China: `cn-beijing` |

## Supported formats

WAV, MP3, MP4, M4A, OGG, FLAC — up to 5 hours, 512MB max.

支持格式：WAV、MP3、MP4、M4A、OGG、FLAC——最长 5 小时，最大 512MB。

## Troubleshooting / 常见问题

**Error**: `TOS upload failed: 403 Forbidden`
**Cause**: TOS bucket policy not configured, or IAM user not authorized. / TOS 桶策略未配置，或 IAM 用户未授权。
**Solution**: Go to TOS bucket → Permission Management → Bucket Authorization Policy → Create Policy → select "Folder Read/Write" template. See Step 3 above. / 进入 TOS 桶 → 权限管理 → 存储桶授权策略管理 → 创建策略 → 选择「文件夹读写」模板。详见上方第三步。

**Error**: `TOS upload extremely slow (~15KB/s)`
**Cause**: Server is outside China mainland but using `cn-beijing` region. / 服务器在中国大陆以外，但使用了 `cn-beijing` 区域。
**Solution**: Change `VOLCENGINE_TOS_REGION` to `cn-hongkong` and create a new bucket in that region. / 将 `VOLCENGINE_TOS_REGION` 改为 `cn-hongkong`，并在该区域新建存储桶。

**Error**: `API returned error: invalid API key`
**Cause**: Using old Speech console API key, or key from wrong console page. / 使用了旧版语音控制台的 API Key，或从错误的控制台页面获取。
**Solution**: Get API key from the NEW Doubao Speech console at `https://console.volcengine.com/speech/new/`, NOT `/speech/app`. / 从新版豆包语音控制台 `https://console.volcengine.com/speech/new/` 获取 API Key，不是 `/speech/app`。

**Error**: `Unsupported audio format` or transcription returns empty
**Cause**: Audio file is corrupted, or format not in supported list. / 音频文件损坏，或格式不在支持列表中。
**Solution**: Ensure file is one of WAV, MP3, MP4, M4A, OGG, FLAC and not corrupted. Try `--format` flag to explicitly specify format. / 确保文件是 WAV、MP3、MP4、M4A、OGG、FLAC 之一且未损坏。尝试用 `--format` 参数显式指定格式。

**Error**: `Missing: VOLCENGINE_ACCESS_KEY_ID...` after running `source .env`
**Cause**: `source .env` sets variables in the current shell but does not export them to child processes. The script runs as a subprocess and cannot see unexported variables. / `source .env` 仅在当前 shell 设置变量但不导出，脚本作为子进程无法读取未导出的变量。
**Solution**: Use `set -a && source .env && set +a` to auto-export all variables, or use `export` before each variable in your `.env` file. / 使用 `set -a && source .env && set +a` 自动导出所有变量，或在 `.env` 文件中每行变量前加 `export`。
