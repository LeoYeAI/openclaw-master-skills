---
name: ezviz-audio-broadcast
description: |
  萤石语音广播技能。支持本地音频文件上传或文本转语音，实现语音内容下发到设备播放。
  Use when: 需要向萤石设备发送语音通知、广播、提醒等音频内容。
  
  ⚠️ 安全要求：必须设置 EZVIZ_APP_KEY 和 EZVIZ_APP_SECRET 环境变量，使用最小权限凭证。
metadata:
  openclaw:
    emoji: "🔊"
    requires:
      env: ["EZVIZ_APP_KEY", "EZVIZ_APP_SECRET", "EZVIZ_DEVICE_SERIAL"]
      pip: ["requests"]
    primaryEnv: "EZVIZ_APP_KEY"
    warnings:
      - "Requires Ezviz credentials with minimal permissions"
      - "Token cached in system temp directory (configurable)"
      - "Uses system TTS commands (say/espeak/ffmpeg) via subprocess"
      - "May read ~/.openclaw/*.json for credentials (env vars have priority)"
    config:
      tokenCache:
        default: true
        envVar: "EZVIZ_TOKEN_CACHE"
        description: "Enable token caching (default: true). Set to 0 to disable."
        path: "/tmp/ezviz_global_token_cache/global_token_cache.json"
        permissions: "0600"
      configFileRead:
        paths:
          - "~/.openclaw/config.json"
          - "~/.openclaw/gateway/config.json"
          - "~/.openclaw/channels.json"
        priority: "lower than environment variables"
        description: "Reads Ezviz credentials from OpenClaw config files as fallback"
---

# Ezviz Audio Broadcast (萤石语音广播)

通过萤石语音上传和下发接口，实现语音内容到设备的广播播放。

---

## ⚠️ 安全警告 (安装前必读)

**在使用此技能前，请完成以下安全检查：**

| # | 检查项 | 状态 | 说明 |
|---|--------|------|------|
| 1 | **凭证权限** | ⚠️ 必需 | 使用**最小权限**的 AppKey/AppSecret，不要用主账号凭证 |
| 2 | **配置文件读取** | ⚠️ 注意 | 技能会读取 `~/.openclaw/*.json` 文件（**但环境变量优先级更高**） |
| 3 | **Token 缓存** | ⚠️ 注意 | Token 缓存在 `/tmp/ezviz_global_token_cache/` (权限 600) |
| 4 | **系统命令** | ⚠️ 注意 | 使用 `say`/`espeak`/`ffmpeg` 进行 TTS (通过 subprocess) |
| 5 | **API 域名** | ✅ 已验证 | `openai.ys7.com` 是萤石官方 API 端点（`openai` = Open API，不是 AI） |
| 6 | **代码审查** | ✅ 推荐 | 审查 `scripts/audio_broadcast.py` 和 `lib/token_manager.py` |

### 🔒 配置文件读取详细说明

**凭证获取优先级**（从高到低）：

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 环境变量 (最高优先级 - 推荐)                                │
│    ├─ EZVIZ_APP_KEY                                         │
│    ├─ EZVIZ_APP_SECRET                                      │
│    └─ EZVIZ_DEVICE_SERIAL                                   │
│    ✅ 优点：不读取配置文件，完全隔离                           │
├─────────────────────────────────────────────────────────────┤
│ 2. OpenClaw 配置文件 (仅当环境变量未设置时使用)                 │
│    ├─ ~/.openclaw/config.json                               │
│    ├─ ~/.openclaw/gateway/config.json                       │
│    └─ ~/.openclaw/channels.json                             │
│    ⚠️ 注意：只读取 channels.ezviz 字段，不读取其他服务凭证     │
├─────────────────────────────────────────────────────────────┤
│ 3. 命令行参数 (最低优先级)                                     │
│    python3 audio_broadcast.py appKey appSecret deviceSerial │
└─────────────────────────────────────────────────────────────┘
```

**安全建议**:
- ✅ **最佳实践**: 使用环境变量，完全避免配置文件读取
- ✅ **隔离配置**: 在专用配置文件只存放萤石凭证，不混用其他服务
- ⚠️ **风险缓解**: 设置环境变量覆盖配置文件（即使配置文件存在也会被忽略）

### 快速安全配置

```bash
# 1. 使用环境变量（优先级最高，避免配置文件意外使用）
export EZVIZ_APP_KEY="your_dedicated_app_key"
export EZVIZ_APP_SECRET="your_dedicated_app_secret"
export EZVIZ_DEVICE_SERIAL="device1,device2"

# 2. 高安全环境：禁用 Token 缓存
export EZVIZ_TOKEN_CACHE=0

# 3. 测试凭证（推荐先用测试账号）
# 登录 https://openai.ys7.com/ 创建专用应用，仅开通语音相关权限
```

### 凭证优先级

技能按以下顺序获取凭证（**优先级从高到低**）：
1. **环境变量** (`EZVIZ_APP_KEY`, `EZVIZ_APP_SECRET`) ← 推荐
2. **Channels 配置** (`~/.openclaw/config.json` 等)
3. **命令行参数** (直接传入)

---

## 快速开始

### 安装依赖

```bash
pip install requests
```

### 设置环境变量

```bash
export EZVIZ_APP_KEY="your_app_key"
export EZVIZ_APP_SECRET="your_app_secret"
export EZVIZ_DEVICE_SERIAL="dev1,dev2,dev3"
```

可选环境变量：
```bash
export EZVIZ_CHANNEL_NO="1"        # 通道号，默认 1
export EZVIZ_AUDIO_FILE="/path/to/audio.mp3"  # 本地音频文件路径（二选一）
export EZVIZ_TEXT_CONTENT="语音内容文本"      # 文本内容（二选一）
export EZVIZ_VOICE_NAME="custom_name"         # 自定义语音名称
export EZVIZ_TOKEN_CACHE="1"                  # Token 缓存：1=启用 (默认), 0=禁用
```

**Token 缓存说明**:
- ✅ **默认启用**: 技能默认使用 Token 缓存，提升效率
- ⚠️ **禁用缓存**: 设置 `EZVIZ_TOKEN_CACHE=0` 每次重新获取 Token
- 📁 **缓存位置**: `/tmp/ezviz_global_token_cache/global_token_cache.json`
- 🔒 **文件权限**: 600 (仅所有者可读写)
- ⏰ **有效期**: 7 天，到期前 5 分钟自动刷新

**注意**: 
- 不需要设置 `EZVIZ_ACCESS_TOKEN`！技能会自动获取 Token
- 必须提供 `EZVIZ_AUDIO_FILE` 或 `EZVIZ_TEXT_CONTENT` 其中一个
- 设备需要支持对讲功能（`support_talk=1或3`）

### 运行

```bash
python3 {baseDir}/scripts/audio_broadcast.py
```

命令行参数：
```bash
# 使用本地音频文件
python3 {baseDir}/scripts/audio_broadcast.py appKey appSecret dev1 /path/to/audio.mp3 [channel_no]

# 使用文本内容（自动生成语音）
python3 {baseDir}/scripts/audio_broadcast.py appKey appSecret dev1 "语音内容文本" [channel_no]
```

## 工作流程

```
1. 获取 Token (appKey + appSecret → accessToken)
 ↓
2a. 如果提供音频文件：直接上传文件
2b. 如果提供文本：调用TTS生成音频文件，然后上传
 ↓
3. 下发语音 (accessToken + deviceSerial + fileUrl → 设备播放)
 ↓
4. 输出结果 (JSON + 控制台)
```

## Token 自动获取说明

**你不需要手动获取或配置 `EZVIZ_ACCESS_TOKEN`！**

技能会自动处理 Token 的获取：

```
首次运行:
 appKey + appSecret → 调用萤石 API → 获取 accessToken (有效期 7 天)
 ↓
保存到缓存文件（系统临时目录）
 ↓
后续运行:
 检查缓存 Token 是否过期
 ├─ 未过期 → 直接使用缓存 Token ✅
 └─ 已过期 → 重新获取新 Token
```

**Token 管理特性**:
- ✅ **自动获取**: 首次运行自动调用萤石 API 获取
- ✅ **有效期 7 天**: 获取的 Token 7 天内有效
- ✅ **智能缓存**: Token 有效期内不重复获取，提升效率
- ✅ **安全缓冲**: 到期前 5 分钟自动刷新，避免边界问题
- ✅ **无需配置**: 不需要手动设置 `EZVIZ_ACCESS_TOKEN` 环境变量
- ✅ **安全存储**: 缓存文件存储在系统临时目录，权限 600
- ⚠️ **可选禁用**: 设置 `EZVIZ_TOKEN_CACHE=0` 可禁用缓存（每次运行重新获取）

## 输出示例

```
======================================================================
Ezviz Audio Broadcast Skill (萤石语音广播)
======================================================================
[Time] 2026-03-16 16:30:00
[INFO] Target devices: 2
 - dev1 (Channel: 1)
 - dev2 (Channel: 1)
[INFO] Mode: Text-to-Speech
[INFO] Content: 接下来插播一个广告

======================================================================
[Step 1] Getting access token...
[SUCCESS] Token obtained, expires: 2026-03-23 16:30:00

======================================================================
[Step 2] Generating and uploading audio...
[INFO] Generated TTS file: /tmp/ezviz_tts_12345.mp3
[SUCCESS] Audio uploaded successfully!
[INFO] Voice Name: ad_broadcast
[INFO] File URL: https://oss-cn-shenzhen.aliyuncs.com/voice/...

======================================================================
[Step 3] Broadcasting audio to devices...
======================================================================

[Device] dev1 (Channel: 1)
[SUCCESS] Audio broadcast completed!

[Device] dev2 (Channel: 1)  
[SUCCESS] Audio broadcast completed!

======================================================================
BROADCAST SUMMARY
======================================================================
 Total devices: 2
 Success: 2
 Failed: 0
======================================================================
```

## 多设备格式

| 格式 | 示例 | 说明 |
|------|------|------|
| 单设备 | `dev1` | 默认通道 1 |
| 多设备 | `dev1,dev2,dev3` | 全部使用默认通道 |
| 指定通道 | `dev1:1,dev2:2` | 每个设备独立通道 |
| 混合 | `dev1,dev2:2,dev3` | 部分指定通道 |

## API 接口

| 接口 | URL | 文档 |
|------|-----|------|
| 获取 Token | `POST /api/lapp/token/get` | https://openai.ys7.com/help/81 |
| 语音上传 | `POST /api/lapp/voice/upload` | https://openai.ys7.com/help/1241 |
| 语音下发 | `POST /api/lapp/voice/send` | https://openai.ys7.com/help/1253 |

## 网络端点

| 域名 | 用途 |
|------|------|
| `openai.ys7.com` | 萤石开放平台 API（Token、语音上传、下发） |

## 音频要求

| 格式 | 支持 | 限制 |
|------|------|------|
| WAV | ✅ | 最大5MB，最长60秒 |
| MP3 | ✅ | 最大5MB，最长60秒 |
| AAC | ✅ | 最大5MB，最长60秒 |

## 注意事项

⚠️ **设备兼容性**: 设备必须支持对讲功能（`support_talk=1或3`），否则返回错误码 `20015`

⚠️ **频率限制**: 语音下发接口有调用频率限制，建议设备间间隔1秒以上

⚠️ **文件大小**: 音频文件不能超过5MB，时长不能超过60秒

⚠️ **Token 安全**: Token 缓存到系统临时目录（权限 600），不写入日志，不发送到非萤石端点

⚠️ **TTS依赖**: 文本转语音功能依赖系统TTS服务，确保系统支持

## 数据流出说明

**本技能会向第三方服务发送数据**：

| 数据类型 | 发送到 | 用途 | 是否必需 |
|----------|--------|------|----------|
| 音频文件 | `openai.ys7.com` (萤石) | 语音上传和下发 | ✅ 必需 |
| appKey/appSecret | `openai.ys7.com` (萤石) | 获取访问 Token | ✅ 必需 |
| 设备序列号 | `openai.ys7.com` (萤石) | 请求下发 | ✅ 必需 |
| **EZVIZ_ACCESS_TOKEN** | **自动生成** | **每次运行自动获取** | **✅ 自动** |

**数据流出说明**:
- ✅ **萤石开放平台** (`openai.ys7.com`): 所有API调用 - 萤石官方 API
- ❌ **无其他第三方**: 不会发送数据到其他服务

**凭证权限建议**:
- 使用**最小权限**的 appKey/appSecret
- 仅开通必要的 API 权限（语音上传、下发）
- 定期轮换凭证
- 不要使用主账号凭证

**本地处理**:
- ✅ Token 缓存到系统临时目录（权限 600）
- ✅ TTS临时文件自动清理
- ✅ 不记录完整 API 响应

## 应用场景

- ✅ 可选禁用缓存：设置 EZVIZ_TOKEN_CACHE=0
| 场景 | 说明 |
|------|------|
| 📢 安全广播 | 向监控区域发送安全提醒、紧急通知 |
| 🏢 办公通知 | 办公室广播会议提醒、访客通知 |
| 🏪 商业应用 | 商店促销广播、排队叫号 |
| 🏠 智能家居 | 家庭语音提醒、门铃通知 |
| 🏭 工厂管理 | 生产线通知、安全警示 |

## 使用示例

**场景1: 紧急安全通知**
```bash
python3 audio_broadcast.py your_key your_secret "kitchen_cam,dining_area" "注意！检测到安全隐患，请立即检查！"
```

**场景2: 商业促销广播**
```bash
export EZVIZ_TEXT_CONTENT="欢迎光临！今日特价商品限时优惠，详情请咨询店员！"
export EZVIZ_DEVICE_SERIAL="store_front,store_back"
python3 audio_broadcast.py
```

**场景3: 使用预录制音频**
```bash
python3 audio_broadcast.py your_key your_secret entrance_cam /path/to/welcome_message.mp3
```

---

## API 端点

| 接口 | URL | 文档 |
|------|-----|------|
| 获取 Token | `POST /api/lapp/token/get` | https://open.ys7.com/help/81 |
| 语音上传 | `POST /api/lapp/voice/upload` | https://open.ys7.com/help/1241 |
| 语音下发 | `POST /api/lapp/voice/send` | https://open.ys7.com/help/1253 |

**API 域名**: `https://openai.ys7.com` (萤石开放平台 API 专用)

### ⚠️ 域名说明

**为什么是 `openai.ys7.com` 而不是 `open.ys7.com`？**

| 域名 | 用途 | 说明 |
|------|------|------|
| `openai.ys7.com` | ✅ API 接口 | 萤石开放平台 **API 专用域名**（AI 不是指人工智能） |
| `open.ys7.com` | 🌐 官方网站 | 萤石开放平台 **官网/文档** 入口 |

**`openai` 的含义**: 这里是 "Open API" 的缩写，**不是** 指 OpenAI 或人工智能。

### ✅ 域名验证

```bash
# 验证 API 域名连通性
curl -I https://openai.ys7.com/api/lapp/token/get

# 验证官网连通性
curl -I https://open.ys7.com/

# 检查 SSL 证书（API 域名）
curl -vI https://openai.ys7.com/api/lapp/token/get 2>&1 | grep -A5 "SSL certificate"

# 验证域名所有权（萤石）
whois ys7.com
```

**官方文档**: https://open.ys7.com/

**安全提示**: 
- ✅ `openai.ys7.com` 是萤石官方 API 域名
- ✅ 两个域名都属于萤石（ys7.com）
- ⚠️ 如果担心域名安全，先用测试凭证验证

### ⚠️ 配置文件扫描说明

技能会读取以下路径中的萤石配置（仅当环境变量未设置时）：

```
~/.openclaw/config.json
~/.openclaw/gateway/config.json
~/.openclaw/channels.json
```

**配置格式**:
```json
{
  "channels": {
    "ezviz": {
      "appId": "your_app_id",
      "appSecret": "your_app_secret",
      "domain": "https://openai.ys7.com",
      "enabled": true
    }
  }
}
```

**安全建议**:
- ✅ 使用**专用萤石凭证**，不要与其他服务共享
- ✅ 如果不想使用配置文件扫描，设置环境变量覆盖
- ✅ 定期审查配置文件中的凭证权限
- ❌ 不要在配置文件中存储主账号凭证

**禁用配置文件扫描**（环境变量优先）:
```bash
export EZVIZ_APP_KEY="your_key"
export EZVIZ_APP_SECRET="your_secret"
# 环境变量优先级高于配置文件
```

---

## 系统依赖

**Python 包**:
```bash
pip install requests
```

**系统工具** (仅 TTS 需要):
- macOS: `say`, `afconvert`
- Linux: `espeak`, `ffmpeg`

### ⚠️ 系统命令安全说明

技能通过 `subprocess` 调用系统 TTS 命令：

```python
# macOS TTS
subprocess.run(['say', '-o', temp_aiff, text_with_pauses], check=True, capture_output=True)
subprocess.run(['afconvert', '-f', 'WAVE', '-d', 'LEI16@44100', temp_aiff, output_path], ...)

# Linux TTS
subprocess.run(['espeak', '-w', output_path, text], check=True, capture_output=True)
subprocess.run(['ffmpeg', '-i', input, '-acodec', 'libmp3lame', output], ...)
```

**安全措施** (v1.0.2+):
- ✅ 使用**列表参数**调用 subprocess（避免 shell 注入）
- ✅ **输入验证**: 文本内容经过 `validate_text_input()` 验证
- ✅ **危险字符拦截**: 拒绝包含 `;`, `|`, `&`, `$()`, 等字符的输入
- ✅ **长度限制**: 文本内容最多 500 字符
- ✅ 临时文件存储在系统临时目录，使用后清理

**输入验证规则**:
| 检查项 | 限制 | 说明 |
|--------|------|------|
| 空内容 | ❌ 拒绝 | 文本不能为空 |
| 长度 | ≤500 字符 | 防止过长输入 |
| 危险字符 | ❌ 拒绝 | `;`, `|`, `&`, `` ` ``, `$()`, `${}` 等 |
| 设备序列号 | 字母数字 | 只允许 `A-Za-z0-9_:,` |

**安全建议**:
- ✅ 确保系统二进制文件来自可信源
- ✅ 在高安全环境运行前审查 `text_to_speech()` 函数
- ✅ 使用容器/沙箱隔离执行环境
- ✅ 输入验证提供额外保护层（防御纵深）

**不使用 TTS** (仅提供音频文件，避免系统命令):
```bash
python3 scripts/audio_broadcast.py appKey appSecret deviceSerial --audio-file /path/to/audio.mp3
```

---

## 安全说明

### ⚠️ 环境变量声明

**必需环境变量** (在 SKILL.md metadata 中声明):
```yaml
metadata:
  openclaw:
    requires:
      env: ["EZVIZ_APP_KEY", "EZVIZ_APP_SECRET", "EZVIZ_DEVICE_SERIAL"]
```

**⚠️ 注意**: 如果 Registry metadata 未显示必需环境变量，以 SKILL.md 为准。

### ⚠️ Token 持久化说明

**默认行为**:
- Token 会缓存到系统临时目录（`/tmp/ezviz_global_token_cache/global_token_cache.json`）
- 缓存有效期 7 天，文件权限 600（仅所有者可读写）
- 所有萤石技能共享同一个全局缓存

**缓存位置查询**:
```bash
# macOS
ls -la /var/folders/*/T/ezviz_global_token_cache/

# Linux
ls -la /tmp/ezviz_global_token_cache/

# 查看缓存内容（脱敏）
cat /tmp/ezviz_global_token_cache/global_token_cache.json
```

**⚠️ 潜在风险**:
| 风险 | 等级 | 说明 |
|------|------|------|
| Token 明文存储 | 🟡 中 | 文件权限 600，但仍是明文 |
| 跨技能共享 | 🟡 中 | 同一用户的技能可共享 Token |
| 多用户系统 | 🟠 高 | 其他用户可能访问临时目录 |
| 临时目录清理 | 🟢 低 | 系统重启可能清理临时文件 |

**禁用缓存** (高安全环境/共享系统):
```bash
export EZVIZ_TOKEN_CACHE=0
python3 scripts/audio_broadcast.py ...
```

**清除缓存**:
```bash
# 清除所有缓存 Token
rm -rf /tmp/ezviz_global_token_cache/

# 或使用 Token 管理器
python3 lib/token_manager.py clear
```

**安全建议**:
| 环境 | 建议 |
|------|------|
| 单用户个人设备 | ✅ 默认缓存安全（文件权限 600） |
| 多用户共享系统 | ⚠️ 设置 `EZVIZ_TOKEN_CACHE=0` |
| 高安全环境 | ⚠️ 禁用缓存 + 专用 OS 用户 + 容器隔离 |
| 生产环境 | ⚠️ 容器/VM 隔离 + 禁用缓存 + 密钥管理器 |

### ⚠️ 凭证轮换通知

**⚠️ 早期版本用户必须轮换凭证！**

如果您曾经使用过旧版本的 .env 文件:
```
🚨 您的凭证可能已泄露！

立即执行:
1. 登录 https://openai.ys7.com/
2. 删除旧应用，创建新应用
3. 获取新的 AppKey 和 AppSecret
```

**正确做法**:
- ❌ 不要使用 .env 文件（已删除）
- ✅ 使用环境变量
- ✅ 使用最小权限凭证
- ✅ 定期轮换凭证（建议每 90 天）
- ✅ 使用密钥管理器（生产环境）

### 数据流出说明

| 数据类型 | 发送到 | 用途 |
|----------|--------|------|
| AppKey/AppSecret | `openai.ys7.com` | 获取 Token |
| 设备序列号 | `openai.ys7.com` | API 调用 |
| 音频文件 | `openai.ys7.com` | 语音上传 |

---

## 代码审查

**推荐审查的文件**:
- `scripts/audio_broadcast.py` - 主脚本
- `lib/token_manager.py` - Token 管理器

**代码特点**:
- ✅ 代码未混淆，易于审查
- ✅ 使用 `requests` 库（标准做法）
- ✅ 使用 `subprocess` 带列表参数（减少 shell 注入风险）
- ⚠️ TTS 调用系统二进制文件（say/espeak/ffmpeg）

---

## 降低风险操作清单

**安装前**:
- [ ] 审查所有代码（scripts/, lib/）
- [ ] 验证 API 域名和 SSL 证书
- [ ] 准备测试凭证（非生产环境）
- [ ] 确认环境变量名称一致（EZVIZ_TEXT_CONTENT）

**安装时**:
- [ ] 设置 `EZVIZ_TOKEN_CACHE=0`（共享系统/多用户环境）
- [ ] 使用专用 OS 用户账户
- [ ] 在隔离环境运行（容器/VM）
- [ ] 使用环境变量而非 .env 文件

**安装后**:
- [ ] 验证缓存文件权限（600）
- [ ] 监控 API 调用日志
- [ ] 定期轮换凭证（90 天）
- [ ] 使用后清除缓存（高安全环境）
- [ ] 验证环境变量名称一致性

---

---

## 🔒 安全审计清单 (安装前完成)

根据安全审计建议，请在安装前完成以下检查：

### 安装前检查

- [ ] **审查代码** — 阅读 `scripts/audio_broadcast.py` 和 `lib/token_manager.py`
- [ ] **验证 API 域名** — 确认 `openai.ys7.com` 是萤石官方端点
- [ ] **准备测试凭证** — 创建专用萤石应用，仅开通语音相关权限
- [ ] **检查配置文件** — 审查 `~/.openclaw/*.json` 中是否有敏感凭证
- [ ] **确认缓存位置** — 确认 `/tmp/ezviz_global_token_cache/` 可接受

### 安装时配置

- [ ] **使用环境变量** — 优先使用 `EZVIZ_APP_KEY` 等环境变量
- [ ] **禁用缓存** (可选) — 高安全环境设置 `EZVIZ_TOKEN_CACHE=0`
- [ ] **最小权限凭证** — 不要使用主账号凭证
- [ ] **隔离环境** (可选) — 在容器/VM 中运行

### 安装后验证

- [ ] **验证缓存权限** — 确认缓存文件权限为 600
- [ ] **测试功能** — 使用测试设备验证广播功能
- [ ] **监控日志** — 检查 API 调用是否正常
- [ ] **记录凭证** — 安全存储凭证信息（密钥管理器）

### 持续维护

- [ ] **定期轮换凭证** — 建议每 90 天轮换一次
- [ ] **审查依赖** — 定期检查 `requests` 等依赖的安全更新
- [ ] **清理缓存** — 高安全环境使用后清除缓存
- [ ] **监控异常** — 关注异常 API 调用或错误

---

**更新日志**:

| 日期 | 版本 | 变更 | 说明 |
|------|------|------|------|
| 2026-03-18 | 1.0.5 | 完整披露 metadata | 添加 `configFileRead` 和 `tokenCache` 完整说明 |
| 2026-03-18 | 1.0.5 | 明确优先级 | 环境变量 > 配置文件 > 命令行参数 |
| 2026-03-18 | 1.0.4 | 澄清 API 域名 | 说明 `openai.ys7.com` 是官方 API 域名（`openai` = Open API） |
| 2026-03-18 | 1.0.3 | 修复 metadata | 添加 `config.tokenCache` 配置说明 |
| 2026-03-18 | 1.0.3 | 明确缓存行为 | 默认启用缓存，支持 `EZVIZ_TOKEN_CACHE=0` 禁用 |
| 2026-03-18 | 1.0.2 | 添加输入验证 | `validate_text_input()` 和 `validate_device_serial()` |
| 2026-03-18 | 1.0.2 | 添加凭证来源警告 | 从配置文件读取时显示警告 |
| 2026-03-18 | 1.0.2 | 更新 metadata 格式 | 使用 YAML 格式，添加 warnings 字段 |
| 2026-03-18 | 1.0.1 | 修复 Token 缓存 bug | `use_cache=None` 改为 `use_cache=True` |
| 2026-03-18 | 1.0.1 | 添加安全审计清单 | 根据安全建议添加完整检查清单 |
| 2026-03-18 | 1.0.1 | 明确配置文件行为 | 说明 `~/.openclaw/*.json` 读取逻辑 |
| 2026-03-18 | 1.0.1 | 添加 API 域名验证 | 提供域名和 SSL 验证命令 |
| 2026-03-18 | 1.0.1 | 添加 TTS 安全说明 | 说明 subprocess 调用系统命令的安全措施 |

**最后更新**: 2026-03-18  
**版本**: 1.0.5 (完整信息披露版)

---

## Channels 配置（推荐）

技能支持从 OpenClaw 的 channels 配置中自动读取萤石凭证，无需单独设置环境变量。

### 配置方式

在 `~/.openclaw/config.json` 或 `~/.openclaw/channels.json` 中添加：

```json
{
  "channels": {
    "ezviz": {
      "appId": "your_app_id",
      "appSecret": "your_app_secret",
      "domain": "https://openai.ys7.com",
      "enabled": true
    }
  }
}
```

### 配置搜索顺序

技能会按以下顺序查找配置文件：
1. `~/.openclaw/config.json`
2. `~/.openclaw/gateway/config.json`
3. `~/.openclaw/channels.json`

### 优先级

凭证获取优先级：
1. **环境变量** (最高优先级)
   - `EZVIZ_APP_KEY`
   - `EZVIZ_APP_SECRET`
2. **Channels 配置** (中等优先级)
   - `channels.ezviz.appId`
   - `channels.ezviz.appSecret`
3. **命令行参数** (最低优先级)

### 优势

- ✅ 集中管理凭证
- ✅ 无需每次设置环境变量
- ✅ 多个技能共享同一配置
- ✅ 更符合 OpenClaw 最佳实践
