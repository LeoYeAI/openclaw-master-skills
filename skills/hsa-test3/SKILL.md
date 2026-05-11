---
name: ezviz-multimodal-analysis
description: |
  萤石多模态理解技能。通过设备抓图 + 智能体分析接口，实现对摄像头画面的 AI 理解分析。
  Use when: 需要对监控画面进行智能分析、场景识别、行为理解、物体检测等多模态 AI 分析任务。
  
  ⚠️ 安全要求：必须设置 EZVIZ_APP_KEY 和 EZVIZ_APP_SECRET 环境变量，使用最小权限凭证。
metadata:
  openclaw:
    emoji: "🧠"
    requires:
      env: ["EZVIZ_APP_KEY", "EZVIZ_APP_SECRET", "EZVIZ_DEVICE_SERIAL", "EZVIZ_AGENT_ID"]
      pip: ["requests"]
    primaryEnv: "EZVIZ_APP_KEY"
    warnings:
      - "Requires Ezviz credentials with minimal permissions"
      - "Token cached in system temp directory (configurable)"
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

# Ezviz Multimodal Analysis (萤石多模态分析)

通过萤石设备抓图 + 智能体分析接口，实现对摄像头画面的多模态 AI 理解。

---

## ⚠️ 安全警告 (安装前必读)

**在使用此技能前，请完成以下安全检查：**

| # | 检查项 | 状态 | 说明 |
|---|--------|------|------|
| 1 | **凭证权限** | ⚠️ 必需 | 使用**最小权限**的 AppKey/AppSecret，不要用主账号凭证 |
| 2 | **配置文件读取** | ⚠️ 注意 | 技能会读取 `~/.openclaw/*.json` 文件（**但环境变量优先级更高**） |
| 3 | **Token 缓存** | ⚠️ 注意 | Token 缓存在 `/tmp/ezviz_global_token_cache/` (权限 600) |
| 4 | **API 域名** | ✅ 已验证 | `openai.ys7.com` 和 `aidialoggw.ys7.com` 是萤石官方 API 端点 |
| 5 | **代码审查** | ✅ 推荐 | 审查 `scripts/multimodal_analysis.py` 和 `lib/token_manager.py` |

### 🔒 配置文件读取详细说明

**凭证获取优先级**（从高到低）：

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 环境变量 (最高优先级 - 推荐)                                │
│    ├─ EZVIZ_APP_KEY                                         │
│    ├─ EZVIZ_APP_SECRET                                      │
│    ├─ EZVIZ_DEVICE_SERIAL                                   │
│    └─ EZVIZ_AGENT_ID                                        │
│    ✅ 优点：不读取配置文件，完全隔离                           │
├─────────────────────────────────────────────────────────────┤
│ 2. OpenClaw 配置文件 (仅当环境变量未设置时使用)                 │
│    ├─ ~/.openclaw/config.json                               │
│    ├─ ~/.openclaw/gateway/config.json                       │
│    └─ ~/.openclaw/channels.json                             │
│    ⚠️ 注意：只读取 channels.ezviz 字段，不读取其他服务凭证     │
├─────────────────────────────────────────────────────────────┤
│ 3. 命令行参数 (最低优先级)                                     │
│    python3 multimodal_analysis.py appKey appSecret ...      │
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
export EZVIZ_DEVICE_SERIAL="dev1,dev2,dev3"
export EZVIZ_AGENT_ID="your_agent_id"

# 2. 高安全环境：禁用 Token 缓存
export EZVIZ_TOKEN_CACHE=0

# 3. 测试凭证（推荐先用测试账号）
# 登录 https://openai.ys7.com/ 创建专用应用，仅开通抓图和 AI 分析相关权限
# 获取 Agent ID: https://openai.ys7.com/console/aiAgent/aiAgent.html
```

### 凭证优先级

技能按以下顺序获取凭证（**优先级从高到低**）：
1. **环境变量** (`EZVIZ_APP_KEY`, `EZVIZ_APP_SECRET`, `EZVIZ_DEVICE_SERIAL`, `EZVIZ_AGENT_ID`) ← 推荐
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
export EZVIZ_AGENT_ID="your_agent_id"
```

可选环境变量：
```bash
export EZVIZ_CHANNEL_NO="1"              # 通道号，默认 1
export EZVIZ_ANALYSIS_TEXT="请分析这张图片"  # 分析提示词
export EZVIZ_TOKEN_CACHE="1"             # Token 缓存：1=启用 (默认), 0=禁用
```

**Token 缓存说明**:
- ✅ **默认启用**: 技能默认使用 Token 缓存，提升效率
- ⚠️ **禁用缓存**: 设置 `EZVIZ_TOKEN_CACHE=0` 每次重新获取 Token
- 📁 **缓存位置**: `/tmp/ezviz_global_token_cache/global_token_cache.json`
- 🔒 **文件权限**: 600 (仅所有者可读写)
- ⏰ **有效期**: 7 天，到期前 5 分钟自动刷新

**注意**: 
- 不需要设置 `EZVIZ_ACCESS_TOKEN`！技能会自动获取 Token
- Agent ID 从萤石 AI 智能体控制台获取：https://openai.ys7.com/console/aiAgent/aiAgent.html
- 图片 URL 有效期 2 小时

### 运行

```bash
python3 {baseDir}/scripts/multimodal_analysis.py
```

命令行参数：
```bash
# 单个设备
python3 {baseDir}/scripts/multimodal_analysis.py appKey appSecret dev1 1 agentId

# 多个设备（逗号分隔）
python3 {baseDir}/scripts/multimodal_analysis.py appKey appSecret "dev1,dev2,dev3" 1 agentId

# 自定义分析提示词
python3 {baseDir}/scripts/multimodal_analysis.py appKey appSecret dev1 1 agentId "请识别画面中的人员"
```

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
   - `EZVIZ_DEVICE_SERIAL`
   - `EZVIZ_AGENT_ID`
2. **Channels 配置** (中等优先级)
   - `channels.ezviz.appId`
   - `channels.ezviz.appSecret`
3. **命令行参数** (最低优先级)

### 优势

- ✅ 集中管理凭证
- ✅ 无需每次设置环境变量
- ✅ 多个技能共享同一配置
- ✅ 更符合 OpenClaw 最佳实践

---

## 工作流程

```
1. 获取 Token (appKey + appSecret → accessToken)
 ↓
2. 设备抓图 (accessToken + deviceSerial → picUrl)
 ↓
3. AI 分析 (agentId + picUrl → 分析结果)
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
Ezviz Multimodal Analysis Skill (萤石多模态分析)
======================================================================
[Time] 2026-03-18 20:50:00
[INFO] Target devices: 2
 - dev1 (Channel: 1)
 - dev2 (Channel: 1)
[INFO] Agent ID: 98af3e...
[INFO] Analysis: 请分析这张图片的内容

======================================================================
SECURITY VALIDATION
======================================================================
[OK] Device serial format validated
[OK] Using credentials from environment variables

======================================================================
[Step 1] Getting access token...
======================================================================
[INFO] Using cached global token, expires: 2026-03-25 19:21:16
[SUCCESS] Using cached token, expires: 2026-03-25 19:21:16

======================================================================
[Step 2] Capturing and analyzing images...
======================================================================

[Device] dev1 (Channel: 1)
[SUCCESS] Image captured: https://opencapture.ys7.com/...
[SUCCESS] Analysis completed!

[Analysis Result]
{
  "场景": "办公室",
  "人员数量": 3,
  "主要物体": ["办公桌", "电脑", "椅子"]
}

[Device] dev2 (Channel: 1)
[SUCCESS] Image captured: https://opencapture.ys7.com/...
[SUCCESS] Analysis completed!

[Analysis Result]
{
  "场景": "会议室",
  "人员数量": 5,
  "主要物体": ["会议桌", "投影仪", "椅子"]
}

======================================================================
ANALYSIS SUMMARY
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
| 设备抓图 | `POST /api/lapp/device/capture` | https://openai.ys7.com/help/687 |
| 智能体分析 | `POST /api/service/open/intelligent/agent/engine/agent/anaylsis` | https://openai.ys7.com/help/5006 |

## 网络端点

| 域名 | 用途 |
|------|------|
| `openai.ys7.com` | 萤石开放平台 API（Token、抓图） |
| `aidialoggw.ys7.com` | 萤石 AI 智能体分析接口 |

## 格式代码

**返回字段**:
- `analysis` - AI 分析结果（依赖智能体配置）
- `pic_url` - 抓拍图片 URL（有效期 2 小时）

**错误码**:
- `200` - 操作成功
- `400` - 参数错误
- `500` - 服务异常
- `10002` - accessToken 过期
- `10028` - 抓图次数超限
- `20007` - 设备不在线

## Tips

- **多设备**: 逗号分隔 `dev1,dev2,dev3`
- **指定通道**: 冒号分隔 `dev1:1,dev2:2`
- **Token 有效期**: 7 天（每次运行自动获取）
- **图片有效期**: 2 小时
- **频率限制**: 设备间自动间隔 4 秒，避免限流
- **分析超时**: 默认 60 秒
- **智能体**: 从 https://openai.ys7.com/console/aiAgent/aiAgent.html 获取

## 分析提示词示例

| 场景 | 提示词 |
|------|--------|
| 通用分析 | "请分析这张图片的内容" |
| 人员识别 | "请识别画面中的人员数量和位置" |
| 行为分析 | "请分析画面中人员的行为活动" |
| 安全检测 | "请检测画面中是否存在安全隐患" |
| 物体识别 | "请识别画面中的主要物体" |

## 注意事项

⚠️ **频率限制**: 萤石抓图接口建议间隔 4 秒以上。技能已自动在设备间等待 4 秒，避免触发限流（错误码 10028）

⚠️ **隐私合规**: 使用摄像头监控可能涉及隐私问题，确保符合当地法律法规

⚠️ **设备要求**: 设备必须在线且支持抓图功能（`support_capture=1`）

⚠️ **Token 安全**: Token 会缓存到系统临时目录（自动管理），不写入日志，不发送到非萤石端点

⚠️ **分析超时**: AI 分析可能耗时较长，默认超时 60 秒

## 数据流出说明

**本技能会向第三方服务发送数据**：

| 数据类型 | 发送到 | 用途 | 是否必需 |
|----------|--------|------|----------|
| appKey/appSecret | `openai.ys7.com` (萤石) | 获取访问 Token | ✅ 必需 |
| 设备序列号 | `openai.ys7.com` (萤石) | 请求抓图 | ✅ 必需 |
| 抓拍图片 URL | `openai.ys7.com` (萤石) | AI 智能体分析 | ✅ 必需 |
| 智能体 ID | `aidialoggw.ys7.com` (萤石) | AI 分析请求 | ✅ 必需 |
| **EZVIZ_ACCESS_TOKEN** | **自动生成** | **每次运行自动获取** | **✅ 自动** |

**数据流出说明**:
- ✅ **萤石开放平台** (`openai.ys7.com`): Token 请求、设备抓图 - 萤石官方 API
- ✅ **萤石 AI 智能体** (`aidialoggw.ys7.com`): 图片分析 - 萤石官方 API
- ❌ **无其他第三方**: 不会发送数据到其他服务

**凭证权限建议**:
- 使用**最小权限**的 appKey/appSecret
- 仅开通必要的 API 权限（设备抓图、AI 分析）
- 定期轮换凭证
- 不要使用主账号凭证

**本地处理**:
- ✅ Token 缓存到系统临时目录（`/tmp/ezviz_global_token_cache/`），权限 600
- ✅ Token 有效期 7 天，到期前 5 分钟自动刷新
- ✅ 可禁用缓存：设置 `EZVIZ_TOKEN_CACHE=0` 环境变量
- ✅ 不记录完整 API 响应
- ✅ 图片 URL 只显示前 50 字符

## 应用场景

| 场景 | 说明 |
|------|------|
| 🏢 办公场景 | 识别人员数量、工作状态、办公环境 |
| 🏭 工厂监控 | 检测安全规范、设备状态、人员行为 |
| 🏪 零售分析 | 客流统计、货架状态、顾客行为 |
| 🏠 智能家居 | 场景识别、异常检测、家庭成员活动 |

## 使用示例

**场景 1: 单设备快速分析**
```bash
python3 multimodal_analysis.py your_key your_secret BF6985110 1 your_agent_id
```

**场景 2: 多设备批量分析**
```bash
export EZVIZ_DEVICE_SERIAL="dev1,dev2,dev3"
export EZVIZ_AGENT_ID="your_agent_id"
python3 multimodal_analysis.py
```

**场景 3: 自定义分析提示词**
```bash
export EZVIZ_ANALYSIS_TEXT="请检测画面中是否存在安全隐患"
python3 multimodal_analysis.py your_key your_secret dev1 1 your_agent_id
```

---

## API 详细说明

### 1. 获取 AccessToken 接口

**文档 URL**: https://openai.ys7.com/help/81

**接口说明**:
- AccessToken 是访问令牌，接口调用必备的公共参数
- **有效期 7 天**，有效期内不需要重复申请
- 新 Token 不会使老 Token 失效
- 最佳实践：本地缓存，即将过期或报错 10002 时再获取

**请求地址**:
```
POST https://openai.ys7.com/api/lapp/token/get
```

**请求参数**:
| 参数名 | 类型 | 描述 | 是否必选 |
|--------|------|------|----------|
| appKey | String | appKey | Y |
| appSecret | String | appSecret | Y |

**返回数据**:
```json
{
  "data": {
    "accessToken": "at.xxxxxxxxxxxxx",
    "expireTime": 1470810222045
  },
  "code": "200",
  "msg": "操作成功!"
}
```

### 2. 设备抓拍图片接口

**文档 URL**: https://openai.ys7.com/help/687

**接口功能**:
抓拍设备当前画面，**该接口仅适用于 IPC 或者关联 IPC 的 DVR 设备**。

**该接口需要设备支持能力集**：`support_capture=1`

> ⚠️ **注意**：设备抓图能力有限，请勿频繁调用，建议每个摄像头调用的间隔**4s 以上**。

**请求地址**:
```
POST https://openai.ys7.com/api/lapp/device/capture
```

**请求参数**:
| 参数名 | 类型 | 描述 | 是否必选 |
|--------|------|------|----------|
| accessToken | String | 授权过程获取的 access_token | Y |
| deviceSerial | String | 设备序列号，字母需为大写 | Y |
| channelNo | int | 通道号，IPC 设备填写 1 | Y |

**返回数据**:
```json
{
  "data": {
    "picUrl": "https://opencapture.ys7.com/.../capture/xxx.jpg?Expires=xxx&..."
  },
  "code": "200",
  "msg": "操作成功!"
}
```

**返回字段**:
| 字段名 | 类型 | 描述 |
|--------|------|------|
| picUrl | String | 抓拍后的图片路径，**图片保存有效期为 2 小时** |

### 3. 智能体分析接口

**文档 URL**: https://openai.ys7.com/help/5006

**接口功能**:
调用萤石 AI 智能体对图片进行多模态理解分析。

**请求地址**:
```
POST https://aidialoggw.ys7.com/api/service/open/intelligent/agent/engine/agent/anaylsis
```

**请求参数**:
| 参数名 | 类型 | 描述 | 是否必选 |
|--------|------|------|----------|
| accessToken | String | 授权过程获取的 access_token | Y |
| appId | String | 智能体 ID | Y |
| mediaType | String | 媒体类型：image | Y |
| text | String | 分析提示词 | Y |
| dataType | String | 数据类型：url | Y |
| data | String | 图片 URL | Y |

**返回数据**:
```json
{
  "meta": {
    "code": 200,
    "message": "success"
  },
  "data": "{\"场景\":\"办公室\",\"人员数量\":3}"
}
```

**返回字段**:
| 字段名 | 类型 | 描述 |
|--------|------|------|
| meta.code | Number | 响应码 |
| meta.message | String | 响应消息 |
| data | String | 分析结果（JSON 字符串） |

---

## 🔐 Token 管理与安全

### Token 缓存行为

**默认行为**:
- ✅ Token 会缓存到系统临时目录（`/tmp/ezviz_global_token_cache/global_token_cache.json`）
- ✅ 缓存有效期 7 天（与 Token 实际有效期一致）
- ✅ 到期前 5 分钟自动刷新
- ✅ 缓存文件权限 600（仅当前用户可读写）

**为什么缓存 Token**:
- ⚡ **性能**: 避免每次运行都调用 API 获取 Token（减少等待时间）
- 🌐 **稳定性**: 减少 API 调用次数，降低网络失败风险
- 💰 **限流保护**: 避免频繁调用触发 API 限流

### 禁用 Token 缓存

如果您不希望 Token 被持久化，可以通过以下方式禁用缓存：

**方法 1: 环境变量**
```bash
export EZVIZ_TOKEN_CACHE=0
python3 scripts/multimodal_analysis.py ...
```

**方法 2: 修改代码**
```python
from token_manager import get_cached_token

# 禁用缓存
token_result = get_cached_token(app_key, app_secret, use_cache=False)
```

### 缓存文件位置

| 系统 | 路径 |
|------|------|
| macOS | `/var/folders/xx/xxxx/T/ezviz_global_token_cache/` |
| Linux | `/tmp/ezviz_global_token_cache/` |
| Windows | `C:\Users\{user}\AppData\Local\Temp\ezviz_global_token_cache\` |

**查看缓存**:
```bash
# macOS/Linux
ls -la /tmp/ezviz_global_token_cache/
cat /tmp/ezviz_global_token_cache/global_token_cache.json

# 清除缓存
rm -rf /tmp/ezviz_global_token_cache/
```

### 验证命令

```bash
# 1. 验证缓存文件权限
ls -la /tmp/ezviz_global_token_cache/global_token_cache.json
# 应该显示：-rw------- (600)

# 2. 验证缓存内容
cat /tmp/ezviz_global_token_cache/global_token_cache.json | python3 -m json.tool

# 3. 验证禁用缓存
export EZVIZ_TOKEN_CACHE=0
python3 scripts/multimodal_analysis.py ...
# 应该显示 "Getting access token from Ezviz API" 而不是 "Using cached global token"

# 4. 清除缓存
python3 lib/token_manager.py clear
```

---

## 🔒 安全建议

### 1. 使用最小权限凭证

- 创建专用的 appKey/appSecret，仅开通必要的 API 权限
- 不要使用主账号凭证
- 定期轮换凭证（建议每 90 天）

### 2. 环境变量安全

```bash
# 推荐：使用 .env 文件（不要提交到版本控制）
echo "EZVIZ_APP_KEY=your_key" >> .env
echo "EZVIZ_APP_SECRET=your_secret" >> .env
chmod 600 .env

# 加载环境变量
source .env
```

### 3. 禁用缓存（高安全场景）

如果您在共享计算机或高安全环境中使用：

```bash
export EZVIZ_TOKEN_CACHE=0  # 禁用缓存
python3 scripts/multimodal_analysis.py ...
```

### 4. 定期清理缓存

```bash
# 清除所有缓存的 Token
rm -rf /tmp/ezviz_global_token_cache/
```

### 5. 配置文件扫描说明

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

## 定时任务示例

**Linux Crontab** (每 5 分钟):
```bash
*/5 * * * * cd /path/to/multimodal-analysis && python3 scripts/multimodal_analysis.py >> /var/log/analysis.log 2>&1
```

**macOS Launchd**:
```xml
<key>StartInterval</key>
<integer>300</integer>
```

---

## 安全审计清单 (安装前完成)

根据安全审计建议，请在安装前完成以下检查：

### 安装前检查

- [ ] **审查代码** — 阅读 `scripts/multimodal_analysis.py` 和 `lib/token_manager.py`
- [ ] **验证 API 域名** — 确认 `openai.ys7.com` 和 `aidialoggw.ys7.com` 是萤石官方端点
- [ ] **准备测试凭证** — 创建专用萤石应用，仅开通抓图和 AI 分析相关权限
- [ ] **获取 Agent ID** — 从 https://openai.ys7.com/console/aiAgent/aiAgent.html 获取
- [ ] **检查配置文件** — 审查 `~/.openclaw/*.json` 中是否有敏感凭证
- [ ] **确认缓存位置** — 确认 `/tmp/ezviz_global_token_cache/` 可接受

### 安装时配置

- [ ] **使用环境变量** — 优先使用 `EZVIZ_APP_KEY` 等环境变量
- [ ] **禁用缓存** (可选) — 高安全环境设置 `EZVIZ_TOKEN_CACHE=0`
- [ ] **最小权限凭证** — 不要使用主账号凭证
- [ ] **隔离环境** (可选) — 在容器/VM 中运行

### 安装后验证

- [ ] **验证缓存权限** — 确认缓存文件权限为 600
- [ ] **测试功能** — 使用测试设备验证分析和抓图功能
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
| 2026-03-18 | 1.0.1 | 初始版本 | 与 ezviz-open-picture 文档结构对齐 |
| 2026-03-18 | 1.0.1 | 添加 channels.json 支持 | 从 OpenClaw 配置文件读取凭证，优先级低于环境变量 |
| 2026-03-18 | 1.0.1 | 添加安全验证 | 设备序列号格式验证、凭证来源警告 |
| 2026-03-18 | 1.0.1 | 添加 Token 缓存说明 | 明确缓存行为，支持 `EZVIZ_TOKEN_CACHE=0` 禁用 |
| 2026-03-18 | 1.0.1 | 添加安全审计清单 | 根据安全建议添加完整检查清单 |

**最后更新**: 2026-03-18  
**版本**: 1.0.1 (Channels 配置支持版)
