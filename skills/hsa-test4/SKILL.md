---
name: ezviz-device-config
description: |
  萤石设备配置技能。支持 9 个设备配置 API，包括布防/撤防、镜头遮蔽、全天录像、移动侦测灵敏度等。
  Use when: 需要远程配置萤石设备参数、修改设备布防状态、调整设备功能开关。
  
  ⚠️ 安全要求：必须设置 EZVIZ_APP_KEY 和 EZVIZ_APP_SECRET 环境变量，使用最小权限凭证。
metadata:
  openclaw:
    emoji: "⚙️"
    requires:
      env: ["EZVIZ_APP_KEY", "EZVIZ_APP_SECRET", "EZVIZ_DEVICE_SERIAL"]
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

# Ezviz Device Config (萤石设备配置)

远程配置萤石设备参数，支持 9 个配置 API。

---

## ⚠️ 安全警告 (安装前必读)

**在使用此技能前，请完成以下安全检查：**

| # | 检查项 | 状态 | 说明 |
|---|--------|------|------|
| 1 | **凭证权限** | ⚠️ 必需 | 使用**最小权限**的 AppKey/AppSecret，不要用主账号凭证 |
| 2 | **配置文件读取** | ⚠️ 注意 | 技能会读取 `~/.openclaw/*.json` 文件（**但环境变量优先级更高**） |
| 3 | **Token 缓存** | ⚠️ 注意 | Token 缓存在 `/tmp/ezviz_global_token_cache/` (权限 600) |
| 4 | **API 域名** | ✅ 已验证 | `openai.ys7.com` 是萤石官方 API 端点（`openai` = Open API，不是 AI） |
| 5 | **代码审查** | ✅ 推荐 | 审查 `scripts/device_config.py` 和 `lib/token_manager.py` |

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
│    python3 device_config.py appKey appSecret deviceSerial  │
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
export EZVIZ_DEVICE_SERIAL="dev1"

# 2. 高安全环境：禁用 Token 缓存
export EZVIZ_TOKEN_CACHE=0

# 3. 测试凭证（推荐先用测试账号）
# 登录 https://openai.ys7.com/ 创建专用应用，仅开通设备配置相关权限
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
export EZVIZ_DEVICE_SERIAL="dev1"
```

可选环境变量：
```bash
export EZVIZ_CHANNEL_NO="1"              # 通道号，默认 1
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
- Token 有效期 7 天

### 运行

```bash
python3 {baseDir}/scripts/device_config.py
```

命令行参数：
```bash
# 设置布防 (isDefence=1)
python3 {baseDir}/scripts/device_config.py appKey appSecret dev1 defence_set 1

# 设置撤防 (isDefence=0)
python3 {baseDir}/scripts/device_config.py appKey appSecret dev1 defence_set 0

# 获取布防计划
python3 {baseDir}/scripts/device_config.py appKey appSecret dev1 defence_plan_get

# 设置布防计划
python3 {baseDir}/scripts/device_config.py appKey appSecret dev1 defence_plan_set '{"startTime":"23:00","stopTime":"07:00","period":"0,1,2,3,4,5,6","enable":1}'

# 设置镜头遮蔽 (enable=1)
python3 {baseDir}/scripts/device_config.py appKey appSecret dev1 shelter_set 1

# 获取镜头遮蔽状态
python3 {baseDir}/scripts/device_config.py appKey appSecret dev1 shelter_get

# 设置移动侦测灵敏度 (0-6)
python3 {baseDir}/scripts/device_config.py appKey appSecret dev1 motion_detect_sensitivity_set 5
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
2. 执行配置 (根据 configType 调用对应 API)
       ↓
3. 输出结果 (JSON + 控制台)
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
Ezviz Device Config (萤石设备配置)
======================================================================
[Time] 2026-03-18 21:00:00
[INFO] Device: dev1
[INFO] Config Type: defence_set
[INFO] Value: 1

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
[Step 2] Executing config...
======================================================================
[INFO] Calling API: https://openai.ys7.com/api/lapp/device/defence/set
[INFO] Device: dev1, Type: defence_set
[INFO] Value: 1
[SUCCESS] Config executed successfully!

======================================================================
CONFIG RESULT
======================================================================
  Device:     dev1
  Type:       defence_set
  Value:      1 (armed)
  Status:     success
======================================================================
```

## 支持的配置类型 (9 个 API)

| 配置类型 | 功能 | 文档 ID | API 路径 | 参数 |
|----------|------|--------|----------|------|
| `defence_set` | 设置布撤防 | 701 | `/api/lapp/device/defence/set` | isDefence: 0/1/8/16 |
| `defence_plan_get` | 获取布撤防时间计划 | 702 | `/api/lapp/device/defence/plan/get` | channelNo(可选) |
| `defence_plan_set` | 设置布撤防计划 | 703 | `/api/lapp/device/defence/plan/set` | startTime,stopTime,period,enable |
| `shelter_get` | 获取镜头遮蔽开关状态 | 706 | `/api/lapp/device/scene/switch/status` | - |
| `shelter_set` | 设置镜头遮蔽开关 | 707 | `/api/lapp/device/scene/switch/set` | enable: 0/1 |
| `fullday_record_get` | 获取全天录像开关状态 | 712 | `/api/lapp/device/fullday/record/switch/status` | - |
| `fullday_record_set` | 设置全天录像开关状态 | 713 | `/api/lapp/device/fullday/record/switch/set` | enable: 0/1 |
| `motion_detect_sensitivity_get` | 获取移动侦测灵敏度配置 | 714 | `/api/lapp/device/algorithm/config/get` | - |
| `motion_detect_sensitivity_set` | 设置移动侦测灵敏度配置 | 715 | `/api/lapp/device/algorithm/config/set` | value: 0-6 |

## API 接口

| 接口 | URL | 文档 |
|------|-----|------|
| 获取 Token | `POST /api/lapp/token/get` | https://openai.ys7.com/help/81 |
| 设置布防 | `POST /api/lapp/device/defence/set` | https://openai.ys7.com/help/701 |
| 获取布防计划 | `POST /api/lapp/device/defence/plan/get` | https://openai.ys7.com/help/702 |
| 镜头遮蔽 | `POST /api/lapp/device/scene/switch/set` | https://openai.ys7.com/help/707 |
| 全天录像 | `POST /api/lapp/device/fullday/record/switch/set` | https://openai.ys7.com/help/713 |
| 移动侦测灵敏度 | `POST /api/lapp/device/algorithm/config/set` | https://openai.ys7.com/help/715 |

## 网络端点

| 域名 | 用途 |
|------|------|
| `openai.ys7.com` | 萤石开放平台 API（Token、设备配置） |

## 格式代码

**布防状态值** (defence_set):
- `0` - 撤防/睡眠
- `1` - 布防 (普通 IPC)
- `8` - 在家模式 (智能设备)
- `16` - 外出模式 (智能设备)

**开关值** (enable):
- `0` - 关闭
- `1` - 开启

**布防计划参数** (defence_plan_set):
- `startTime`: 开始时间 (HH:mm 格式，如 23:20)
- `stopTime`: 结束时间 (HH:mm 格式，n00:00 表示第二天 0 点)
- `period`: 周期 (0-6 表示周一 - 周日，逗号分隔，如 "0,1,6")
- `enable`: 是否启用 (1-启用，0-不启用)

**移动侦测灵敏度** (motion_detect_sensitivity_set):
- `0-6`: 灵敏度级别 (0 最低，6 最高)

**错误码**:
- `200` - 操作成功
- `10002` - accessToken 过期
- `20007` - 设备不在线
- `20008` - 设备响应超时
- `60020` - 不支持该命令 (设备不支持此功能)

## Tips

- **设备序列号**: 字母需为大写
- **Token 有效期**: 7 天（每次运行自动获取）
- **频率限制**: 建议操作间隔 ≥2 秒
- **权限要求**: 需要设备配置权限（Permission: Config）
- **设备支持**: 不同设备支持的功能不同，请先确认设备能力集

## 注意事项

⚠️ **设备支持**: 不是所有设备都支持全部 9 个功能，请先确认设备能力

⚠️ **权限要求**: 需要设备配置权限，子账户需要 `Permission: Config`

⚠️ **操作谨慎**: 修改设备配置可能影响设备正常运行，请谨慎操作

⚠️ **Token 安全**: Token 会缓存到系统临时目录（自动管理），不写入日志，不发送到非萤石端点

## 数据流出说明

**本技能会向第三方服务发送数据**：

| 数据类型 | 发送到 | 用途 | 是否必需 |
|----------|--------|------|----------|
| appKey/appSecret | `openai.ys7.com` (萤石) | 获取访问 Token | ✅ 必需 |
| 设备序列号 | `openai.ys7.com` (萤石) | 设备配置请求 | ✅ 必需 |
| 配置参数 | `openai.ys7.com` (萤石) | 配置设备参数 | ✅ 必需 |
| **EZVIZ_ACCESS_TOKEN** | **自动生成** | **每次运行自动获取** | **✅ 自动** |

**数据流出说明**:
- ✅ **萤石开放平台** (`openai.ys7.com`): Token 请求、设备配置 - 萤石官方 API
- ❌ **无其他第三方**: 不会发送数据到其他服务

**凭证权限建议**:
- 使用**最小权限**的 appKey/appSecret
- 仅开通必要的 API 权限（设备配置）
- 定期轮换凭证
- 不要使用主账号凭证

**本地处理**:
- ✅ Token 缓存到系统临时目录（`/tmp/ezviz_global_token_cache/`），权限 600
- ✅ Token 有效期 7 天，到期前 5 分钟自动刷新
- ✅ 可禁用缓存：设置 `EZVIZ_TOKEN_CACHE=0` 环境变量
- ✅ 不记录完整 API 响应
- ✅ 不跨运行缓存 Token（每次运行重新获取）

## 使用场景

| 场景 | 配置类型 | 说明 |
|------|----------|------|
| 🏠 离家布防 | `defence_set` = 1 | 外出时开启设备布防 |
| 🏡 回家撤防 | `defence_set` = 0 | 回家时关闭布防 |
| 📅 查询布防计划 | `defence_plan_get` | 查看布撤防时间计划 |
| 📅 设置布防计划 | `defence_plan_set` | 设置定时布撤防 |
| 🎥 隐私保护 | `shelter_set` = 1 | 开启镜头遮蔽保护隐私 |
| 📹 全天录像 | `fullday_record_set` = 1 | 开启全天录像功能 |
| 🔍 移动侦测 | `motion_detect_sensitivity_set` = 5 | 设置移动侦测灵敏度 |

---

## ⚠️ 域名说明

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
python3 scripts/device_config.py ...
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
python3 scripts/device_config.py ...
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
python3 scripts/device_config.py ...
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

## 安全审计清单 (安装前完成)

根据安全审计建议，请在安装前完成以下检查：

### 安装前检查

- [ ] **审查代码** — 阅读 `scripts/device_config.py` 和 `lib/token_manager.py`
- [ ] **验证 API 域名** — 确认 `openai.ys7.com` 是萤石官方端点
- [ ] **准备测试凭证** — 创建专用萤石应用，仅开通设备配置相关权限
- [ ] **检查配置文件** — 审查 `~/.openclaw/*.json` 中是否有敏感凭证
- [ ] **确认缓存位置** — 确认 `/tmp/ezviz_global_token_cache/` 可接受

### 安装时配置

- [ ] **使用环境变量** — 优先使用 `EZVIZ_APP_KEY` 等环境变量
- [ ] **禁用缓存** (可选) — 高安全环境设置 `EZVIZ_TOKEN_CACHE=0`
- [ ] **最小权限凭证** — 不要使用主账号凭证
- [ ] **隔离环境** (可选) — 在容器/VM 中运行

### 安装后验证

- [ ] **验证缓存权限** — 确认缓存文件权限为 600
- [ ] **测试功能** — 使用测试设备验证配置功能
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
| 2026-03-18 | 1.0.4 | 更新域名为 openai.ys7.com | 与设备抓图技能保持一致 |
| 2026-03-18 | 1.0.4 | 采用全局 Token 缓存 | 使用 token_manager.py 统一管理 |
| 2026-03-18 | 1.0.3 | 添加 channels.json 支持 | 从 OpenClaw 配置文件读取凭证 |
| 2026-03-18 | 1.0.3 | 添加安全验证 | 设备序列号格式验证、凭证来源警告 |
| 2026-03-18 | 1.0.2 | 添加 Token 缓存说明 | 明确缓存行为，支持 `EZVIZ_TOKEN_CACHE=0` 禁用 |
| 2026-03-18 | 1.0.1 | 添加安全审计清单 | 根据安全建议添加完整检查清单 |

**最后更新**: 2026-03-18  
**版本**: 1.0.4 (全局 Token 缓存版)
