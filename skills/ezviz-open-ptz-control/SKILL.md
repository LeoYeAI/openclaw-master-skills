---
name: ezviz-open-ptz-control
description: |
  萤石开放平台云台设备控制技能。支持设备列表查询、设备状态查询、云台控制 (PTZ)、预置点管理等功能。
  Use when: 需要控制萤石云台设备、调整摄像头角度、设置预置点。
  
  ⚠️ 安全要求：必须设置 EZVIZ_APP_KEY 和 EZVIZ_APP_SECRET 环境变量，使用最小权限凭证。
metadata:
  openclaw:
    emoji: "🎮"
    requires:
      env: ["EZVIZ_APP_KEY", "EZVIZ_APP_SECRET"]
      pip: ["requests"]
    primaryEnv: "EZVIZ_APP_KEY"
    warnings:
      - "Requires Ezviz credentials with minimal permissions"
      - "Token cached in system temp directory (configurable)"
    config:
      tokenCache:
        default: true
        envVar: "EZVIZ_TOKEN_CACHE"
        description: "Enable token caching (default: true). Set to 0 to disable."
        path: "/tmp/ezviz_global_token_cache/global_token_cache.json"
        permissions: "0600"
---

# Ezviz Open PTZ Control (萤石开放平台云台设备控制)

萤石开放平台云台设备控制，支持设备查询、云台控制、预置点管理等功能。

---

## ⚠️ 安全警告 (安装前必读)

**在使用此技能前，请完成以下安全检查：**

| # | 检查项 | 状态 | 说明 |
|---|--------|------|------|
| 1 | **凭证权限** | ⚠️ 必需 | 使用**最小权限**的 AppKey/AppSecret，不要用主账号凭证 |
| 2 | **Token 缓存** | ⚠️ 注意 | Token 缓存在 `/tmp/ezviz_global_token_cache/` (权限 600) |
| 3 | **API 域名** | ✅ 已验证 | `openai.ys7.com` 是萤石官方 API 端点（`openai` = Open API，不是 AI） |
| 4 | **代码审查** | ✅ 推荐 | 审查 `scripts/main.py` 和 `lib/token_manager.py` |

### 🔒 凭证获取优先级

**凭证获取优先级**（从高到低）：

```
┌─────────────────────────────────────────────────────────────┐
│ 1. 环境变量 (最高优先级 - 推荐)                                │
│    ├─ EZVIZ_APP_KEY                                         │
│    └─ EZVIZ_APP_SECRET                                      │
│    ✅ 优点：不读取配置文件，完全隔离                           │
├─────────────────────────────────────────────────────────────┤
│ 2. 命令行参数 (最低优先级)                                     │
│    python3 main.py appKey appSecret <command>               │
└─────────────────────────────────────────────────────────────┘
```

**安全建议**:
- ✅ **最佳实践**: 使用环境变量，完全避免配置文件读取
- ✅ **隔离配置**: 在专用配置文件只存放萤石凭证，不混用其他服务
- ⚠️ **风险缓解**: 设置环境变量覆盖配置文件（即使配置文件存在也会被忽略）

### ⚠️ API 域名验证

**重要**: `openai.ys7.com` 是萤石官方 API 域名（`openai` = Open API，不是人工智能）

```bash
# 验证 API 域名连通性
curl -I https://openai.ys7.com/api/lapp/token/get

# 验证 SSL 证书
curl -vI https://openai.ys7.com/api/lapp/token/get 2>&1 | grep -A5 "SSL certificate"

# 验证域名所有权
whois ys7.com
```

**官方文档**: https://open.ys7.com/

### 快速安全配置

```bash
# 1. 使用环境变量（优先级最高，避免配置文件意外使用）
export EZVIZ_APP_KEY="your_dedicated_app_key"
export EZVIZ_APP_SECRET="your_dedicated_app_secret"

# 2. 高安全环境：禁用 Token 缓存
export EZVIZ_TOKEN_CACHE=0

# 3. 测试凭证（推荐先用测试账号）
# 登录 https://openai.ys7.com/ 创建专用应用，仅开通云台控制相关权限
```

### 凭证优先级

技能按以下顺序获取凭证（**优先级从高到低**）：
1. **环境变量** (`EZVIZ_APP_KEY`, `EZVIZ_APP_SECRET`) ← 推荐
2. **命令行参数** (直接传入)

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
```

可选环境变量：
```bash
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

### 运行

```bash
python3 {baseDir}/scripts/main.py
```

命令行参数：
```bash
# 查询设备列表
python3 {baseDir}/scripts/main.py appKey appSecret list

# 查询设备状态
python3 {baseDir}/scripts/main.py appKey appSecret status BF6985110

# 查询设备能力集
python3 {baseDir}/scripts/main.py appKey appSecret capacity BF6985110

# 云台控制（向上）
python3 {baseDir}/scripts/main.py appKey appSecret ptz_start BF6985110 1 0 1

# 停止云台
python3 {baseDir}/scripts/main.py appKey appSecret ptz_stop BF6985110 1

# 调用预置点
python3 {baseDir}/scripts/main.py appKey appSecret preset_move BF6985110 1 1
```

---

## 工作流程

```
1. 获取 Token (appKey + appSecret → accessToken)
       ↓
2. 执行操作 (根据命令调用对应 API)
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
Ezviz Open PTZ Control (萤石开放平台云台设备控制)
======================================================================
[Time] 2026-03-19 10:00:00
[INFO] Command: list

======================================================================
[Step 1] Getting access token...
======================================================================
[INFO] Using cached global token, expires: 2026-03-26 10:00:00
[SUCCESS] Using cached token, expires: 2026-03-26 10:00:00

======================================================================
[Step 2] Executing command...
======================================================================
[INFO] Calling API: https://openai.ys7.com/api/lapp/device/list
[SUCCESS] Device list retrieved

======================================================================
RESULT
======================================================================
  Status:     success
  Total devices:  3
  Devices:
    - dev1 (Status: online)
    - dev2 (Status: online)
    - dev3 (Status: offline)
======================================================================
```

## 支持的命令

| 命令 | 功能 | API 文档 |
|------|------|----------|
| `list` | 查询设备列表 | https://openai.ys7.com/help/680 |
| `status [dev]` | 查询设备状态 | https://openai.ys7.com/help/681 |
| `capacity [dev]` | 查询设备能力集 | https://openai.ys7.com/help/683 |
| `ptz_start [dev] [ch] [dir] [spd]` | 开始云台控制 | https://openai.ys7.com/help/690 |
| `ptz_stop [dev] [ch]` | 停止云台控制 | https://openai.ys7.com/help/691 |
| `preset_add [dev] [ch]` | 添加预置点 | https://openai.ys7.com/help/692 |
| `preset_move [dev] [ch] [idx]` | 调用预置点 | https://openai.ys7.com/help/694 |
| `preset_clear [dev] [ch] [idx]` | 清除预置点 | https://openai.ys7.com/help/693 |
| `mirror [dev] [ch] [cmd]` | 镜像翻转 | https://openai.ys7.com/help/695 |

## 云台控制参数

**方向参数** (direction):

| 值 | 方向 | 值 | 方向 |
|----|------|----|------|
| `0` | 上 | `1` | 下 |
| `2` | 左 | `3` | 右 |
| `4` | 左上 | `5` | 左下 |
| `6` | 右上 | `7` | 右下 |
| `8` | 物理放大 | `9` | 物理缩小 |
| `10` | 调整近焦距 | `11` | 调整远焦距 |
| `16` | 自动控制 | | |

**速度参数** (speed):
- `0` - 慢速
- `1` - 适中（推荐）
- `2` - 快速

**镜像命令** (command):
- `0` - 上下翻转
- `1` - 左右翻转
- `2` - 中心翻转

## API 接口

| 接口 | URL | 文档 |
|------|-----|------|
| 获取 Token | `POST /api/lapp/token/get` | https://openai.ys7.com/help/81 |
| 设备列表 | `POST /api/lapp/device/list` | https://openai.ys7.com/help/680 |
| 设备状态 | `POST /api/lapp/device/info` | https://openai.ys7.com/help/681 |
| 设备能力集 | `POST /api/lapp/device/capacity` | https://openai.ys7.com/help/683 |
| 云台启动 | `POST /api/lapp/device/ptz/start` | https://openai.ys7.com/help/690 |
| 云台停止 | `POST /api/lapp/device/ptz/stop` | https://openai.ys7.com/help/691 |
| 预置点管理 | `POST /api/lapp/device/preset/*` | https://openai.ys7.com/help/692 |

## 网络端点

| 域名 | 用途 |
|------|------|
| `openai.ys7.com` | 萤石开放平台 API（Token、云台控制） |

## 格式代码

**设备状态**:
- `online` - 设备在线
- `offline` - 设备离线
- `error` - 状态查询失败

**错误码**:
- `200` - 操作成功
- `10002` - accessToken 过期
- `20007` - 设备不在线
- `20008` - 设备响应超时
- `60020` - 不支持该命令 (设备不支持此功能)

## Tips

- **设备序列号**: 字母需为大写
- **Token 有效期**: 7 天（缓存有效期内不重复获取）
- **云台控制**: 需要先调用 `ptz_start` 启动，再调用 `ptz_stop` 停止
- **预置点**: 添加预置点后会自动返回预置点序号
- **设备兼容性**: 消费级设备可能不支持部分高级功能

## 注意事项

⚠️ **设备支持**: 不是所有设备都支持云台控制，请先确认设备能力集

⚠️ **权限要求**: 需要设备控制权限，子账户需要 `Permission: Config`

⚠️ **操作谨慎**: 云台控制会影响摄像头角度，请谨慎操作

⚠️ **Token 安全**: Token 会缓存到系统临时目录（自动管理），不写入日志，不发送到非萤石端点

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
python3 scripts/main.py ...
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
python3 scripts/main.py ...
# 应该显示 "Getting access token from Ezviz API" 而不是 "Using cached global token"
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
python3 scripts/main.py ...
```

### 4. 定期清理缓存

```bash
# 清除所有缓存的 Token
rm -rf /tmp/ezviz_global_token_cache/
```

### 5. 代码完整性验证

```bash
# 验证 Python 语法
python3 -m py_compile scripts/main.py lib/token_manager.py

# 验证 AST（确保无截断）
python3 -c "import ast; ast.parse(open('scripts/main.py').read()); ast.parse(open('lib/token_manager.py').read()); print('✅ Code integrity verified')"

# 检查文件行数（应 > 300 行）
wc -l scripts/main.py lib/token_manager.py
```

---

## ✅ 安全审计清单 (安装前完成)

根据安全审计建议，请在安装前完成以下检查：

### 安装前检查
- [ ] **审查代码** — 阅读 `scripts/main.py` 和 `lib/token_manager.py`
- [ ] **验证 API 域名** — 确认 `openai.ys7.com` 是萤石官方端点（`openai` = Open API，不是 AI）
- [ ] **验证代码完整性** — 运行 `python3 -m py_compile` 检查语法，确认无截断
- [ ] **准备测试凭证** — 创建专用萤石应用，仅开通云台控制相关权限
- [ ] **确认缓存位置** — 确认 `/tmp/ezviz_global_token_cache/` 可接受

### 安装时配置
- [ ] **使用环境变量** — 优先使用 `EZVIZ_APP_KEY` 等环境变量
- [ ] **禁用缓存** (可选) — 高安全环境设置 `EZVIZ_TOKEN_CACHE=0`
- [ ] **最小权限凭证** — 不要使用主账号凭证

### 安装后验证
- [ ] **验证缓存权限** — 确认缓存文件权限为 600
- [ ] **测试功能** — 使用测试设备验证云台控制功能
- [ ] **监控日志** — 检查 API 调用是否正常
- [ ] **验证代码完整性** — 确认文件完整无截断（`wc -l` 检查行数）

### 持续维护
- [ ] **定期轮换凭证** — 建议每 90 天轮换一次
- [ ] **清理缓存** — 高安全环境使用后清除缓存
- [ ] **监控异常** — 关注异常 API 调用或错误

---

## 使用场景

| 场景 | 命令 | 说明 |
|------|------|------|
| 📋 查看设备 | `list` | 获取所有设备列表 |
| 🔍 检查状态 | `status [dev]` | 查看设备是否在线 |
| 🎮 云台控制 | `ptz_start` / `ptz_stop` | 调整摄像头角度 |
| 📍 保存位置 | `preset_add` | 保存当前位置为预置点 |
| 🎯 调用位置 | `preset_move [idx]` | 移动到预置点 |
| 🔄 镜像翻转 | `mirror [cmd]` | 翻转摄像头画面 |

---

## ⚠️ 域名说明

**为什么是 `openai.ys7.com` 而不是 `open.ys7.com`？**

| 域名 | 用途 | 说明 |
|------|------|------|
| `openai.ys7.com` | ✅ API 接口 | 萤石开放平台 API 专用域名（`openai` = Open API，不是人工智能） |
| `open.ys7.com` | 🌐 官方网站 | 萤石开放平台 官网/文档 入口 |

**官方文档**: https://open.ys7.com/

**安全提示**:
- ✅ `openai.ys7.com` 是萤石官方 API 域名
- ✅ 两个域名都属于萤石（ys7.com）
- ⚠️ 如果担心域名安全，先用测试凭证验证

---

## 更新日志

| 日期 | 版本 | 变更 | 说明 |
|------|------|------|------|
| 2026-03-19 | 1.0.5 | 添加代码完整性验证 | 回应审核关切，添加语法验证和代码完整性检查 |
| 2026-03-19 | 1.0.5 | 添加 API 域名验证说明 | 明确 `openai.ys7.com` 是萤石官方 API（Open API） |
| 2026-03-19 | 1.0.5 | 完善安全审计清单 | 添加代码审查和完整性验证步骤 |
| 2026-03-19 | 1.0.4 | 参考设备抓图技能格式 | 统一 metadata 格式、安全警告、凭证优先级说明 |
| 2026-03-19 | 1.0.3 | 整合元数据到 SKILL.md | 移除单独文件，所有信息整合到 SKILL.md |
| 2026-03-19 | 1.0.2 | 添加 Token 缓存支持 | 使用全局 Token 管理器，与设备抓图技能一致 |

**最后更新**: 2026-03-19  
**版本**: 1.0.5 (代码完整性验证版)

---

**作者**: EzvizOpenTeam  
**主页**: https://openai.ys7.com/  
**许可证**: MIT-0
