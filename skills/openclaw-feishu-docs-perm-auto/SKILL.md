---
name: openclaw-feishu-docs-perm-auto
description: 自动为飞书文档添加用户权限。每次创建飞书文档（多维表格/文档/电子表格/文件夹/云空间文件/知识库节点等）后自动添加用户权限，或用户反馈文档无权限时补充添加权限。适用于 OpenClaw Agent。
license: MIT
metadata:
  openclaw:
    emoji: 🔐
  author: sadjjk
  version: "1.0.0"
---

# 飞书文档权限自动添加

> 🎯 **一句话总结**：飞书应用创建的文档，用户默认无权限。这个 skill 帮你自动添加权限。

---

## 前置条件

| 条件 | 说明 |
|------|------|
| 飞书开发者账号 | 需要有飞书开放平台的开发者权限 |
| 企业自建应用 | 已创建或有权创建飞书应用 |
| 应用权限 | 应用需开通 `docs:permission.member:create` 权限 |

---

## 变量速查表

| 变量名 | 来源 | 用途 |
|--------|------|------|
| `$APP_ID` | 配置文件 `channels.feishu.appId` | 应用标识 |
| `$APP_SECRET` | 配置文件 `channels.feishu.appSecret` | 应用密钥 |
| `$OWNER_OPEN_ID` | 配置文件或会话上下文 | 权限接收者 |
| `$TENANT_TOKEN` | API 获取 | 请求鉴权 |
| `$FILE_TOKEN` | 创建返回或 URL 解析 | 文档标识 |
| `$DOC_TYPE` | URL 路径识别 | 文档类型 |

---

## 第一步：检查配置 ⚠️

### 1.1 读取配置文件

配置文件位置：`~/.openclaw/openclaw.json`

### 1.2 检查必需字段

在 `channels.feishu` 下查找：

| 字段名 | 说明 | 示例值 | 必需性 |
|--------|------|--------|--------|
| `appId` | 飞书应用 ID | `cli_xxxxxxxx` | ✅ 必需 |
| `appSecret` | 飞书应用密钥 | `xxxxxxxx` | ✅ 必需 |
| `ownerOpenId` | 用户的 open_id | `ou_xxx` | ⚪ 可选* |

> *`ownerOpenId` 在配置文件中可选，但执行时必须有值。若配置文件缺失，从会话上下文提取（格式 `user:ou_xxx` → `ou_xxx`）。

配置示例：

```json
{
  "channels": {
    "feishu": {
      "enabled": true,
      "appId": "cli_xxxxxxxx",
      "appSecret": "xxxxxxxx",
      "ownerOpenId": "ou_xxx"
    }
  }
}
```

### 1.3 检查应用权限

使用 `feishu_app_scopes()` 查询当前飞书应用已开通的权限列表。

检查返回结果中是否包含 `docs:permission.member:create`：
- ✅ 有 → 权限正常，继续下一步
- ❌ 无 → 跳转到 [配置引导流程 C](#c-配置应用权限)

> 💡 如检查出有权限，后续可跳过此步骤。

### 1.4 判断逻辑

根据检查结果，按以下流程处理：

```
┌─────────────────────────────────────────────────────────┐
│  检查 appId + appSecret                                 │
│     ├─ ❌ 缺失 → [配置引导流程 A]                        │
│     └─ ✅ 完整 ↓                                        │
│  检查应用权限 docs:permission.member:create              │
│     ├─ ❌ 缺失 → [配置引导流程 C]                        │
│     └─ ✅ 完整 ↓                                        │
│  检查 ownerOpenId                                       │
│     ├─ ✅ 配置文件有 → 进入第二步                        │
│     ├─ ✅ 会话上下文有 → 提取使用，进入第二步             │
│     └─ ❌ 都没有 → [配置引导流程 B]                      │
└─────────────────────────────────────────────────────────┘
```

---

## 工具调用映射 🛠️

> 明确每个步骤应使用的工具，确保 Agent 能正确执行

| 步骤 | 操作 | 工具 | 说明 |
|------|------|------|------|
| 1.1 | 读取配置文件 | `read` | 读取 `~/.openclaw/openclaw.json` |
| 1.3 | 检查应用权限 | `feishu_app_scopes` | 查询已开通权限列表 |
| 2.2 | 获取 tenant_access_token | `exec` | 执行 curl 命令请求 API |
| 2.3 | 解析文档 token | 内置逻辑 | 从 URL 或返回值中提取 |
| 2.4 | 添加用户权限 | `exec` | 执行 curl 命令请求 API |
| 配置写入 | 保存 ownerOpenId | `edit` | 更新 `openclaw.json` |

**工具调用示例**：

```bash
# 读取配置文件
read("~/.openclaw/openclaw.json")

# 检查应用权限
feishu_app_scopes()

# 获取 tenant_access_token
exec('curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" ...')

# 添加权限
exec('curl -s -X POST "https://open.feishu.cn/open-apis/drive/v1/permissions/..." ...')

# 保存配置
edit("~/.openclaw/openclaw.json", oldText, newText)
```

---

## 第二步：执行权限添加 📋

> 前置条件：第一步检查全部通过

### 2.1 读取配置

**工具**：`read`

```bash
APP_ID="读取到的appId"
APP_SECRET="读取到的appSecret"
OWNER_OPEN_ID="读取到的ownerOpenId"
```

### 2.2 获取 tenant_access_token

**工具**：`exec`

**进度提示**：`[1/4] 获取访问令牌...`

**请求**：

```bash
curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
  -H "Content-Type: application/json" \
  -d "{
    \"app_id\": \"$APP_ID\",
    \"app_secret\": \"$APP_SECRET\"
  }"
```

**成功返回**：

```json
{
  "code": 0,
  "msg": "ok",
  "tenant_access_token": "xxxx",
  "expire": 5535
}
```

**失败返回**：

```json
{
  "code": 10003,
  "msg": "app id or app secret is invalid"
}
```

**处理**：
- ✅ 成功：提取 `tenant_access_token`，继续下一步
- ❌ 失败：提示用户检查 App ID 和 App Secret 是否正确

**token 缓存策略**：

| token 类型 | 有效期 | 缓存建议 |
|-----------|--------|----------|
| `tenant_access_token` | 约 2 小时 | 缓存至会话变量，过期前 5 分钟刷新 |

**缓存实现**：
- 使用会话级变量存储：`CACHED_TENANT_TOKEN`, `TOKEN_EXPIRE_TIME`
- 每次请求前检查：若 `now < TOKEN_EXPIRE_TIME - 300`，直接使用缓存

### 2.3 获取云文档 token

**进度提示**：`[2/4] 解析文档 token...`

**来源**：
1. 创建飞书文档后返回的 token 或文档 URL
2. 从用户提供的文档链接解析

**URL 解析规则**：

| 文档类型 | URL 示例 |
|----------|----------|
| 文件夹 | `https://xxx.feishu.cn/drive/folder/【token】` |
| 文件 | `https://xxx.feishu.cn/file/【token】` |
| 旧版文档 | `https://xxx.feishu.cn/docs/【token】` |
| 新版文档 | `https://xxx.feishu.cn/docx/【token】` |
| 电子表格 | `https://xxx.feishu.cn/【token】` |
| 多维表格 | `https://xxx.feishu.cn/base/【token】` |
| 知识空间 | `https://xxx.feishu.cn/wiki/settings/【token】` |
| 知识库节点 | `https://xxx.feishu.cn/wiki/【token】` |

> ⚠️ 复制 URL 时注意删除末尾多余的 `#` 符号。

**自动识别 doc_type**：

| URL 路径特征 | doc_type |
|-------------|----------|
| `/drive/folder/` | `folder` |
| `/file/` | `file` |
| `/docs/` | `doc` |
| `/docx/` | `docx` |
| `/base/` | `bitable` |
| `/wiki/` | `wiki` |
| 其他（根路径） | `sheet` |

**识别逻辑**：
1. 从 URL 提取 token（最后一个路径段，去除 `?` 和 `#` 后的内容）
2. 根据 URL 路径匹配 doc_type
3. 若无法匹配，提示用户提供文档类型

**变量定义**：
- `FILE_TOKEN = 获取到的云文档 token`
- `DOC_TYPE = 识别到的文档类型`

### 2.4 添加用户权限

**工具**：`exec`

**进度提示**：`[3/4] 添加用户权限...`

**请求**：

```bash
curl -s -X POST "https://open.feishu.cn/open-apis/drive/v1/permissions/{FILE_TOKEN}/members/batch_create?type={DOC_TYPE}" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {tenant_access_token}" \
  -d "{
    \"members\": [{
      \"member_type\": \"openid\",
      \"member_id\": \"$OWNER_OPEN_ID\",
      \"perm\": \"full_access\"
    }]
  }"
```

**参数说明**：

| 参数 | 来源 | 示例 |
|------|------|------|
| `{FILE_TOKEN}` | 创建文档时返回或 URL 解析 | `xxxxx` |
| `{DOC_TYPE}` | URL 路径自动识别 | `bitable` |
| `{tenant_access_token}` | 上一步获取 | `t-xxx` |
| `$OWNER_OPEN_ID` | ownerOpenId | `ou_xxx` |

**doc_type 可选值**：

| 值 | 文档类型 |
|----|----------|
| `bitable` | 多维表格 |
| `docx` | 新版文档 |
| `doc` | 旧版文档 |
| `sheet` | 电子表格 |
| `folder` | 文件夹 |
| `file` | 云空间文件 |
| `wiki` | 知识库节点 |


**成功返回**：

```json
{
  "code": 0,
  "msg": "Success",
  "data": {
    "members": [{
      "member_id": "xxxx",
      "member_type": "openid",
      "perm": "full_access"
    }]
  }
}
```

### 2.5 执行结果反馈

**进度提示**：`[4/4] 完成！`

**成功时**：

```
✅ 权限添加成功！

📄 文档：{文档标题或 token}
🔗 链接：{文档 URL}
👤 权限：完整权限 (full_access)
你现在可以直接访问和编辑这个文档了。
如果配置文件中没有ownerOpenId 并询问 是否需要将 ownerOpenId 写入配置文件中
```

**失败时**：

```
❌ 权限添加失败

原因：{错误信息}
解决方案：{具体步骤}

需要帮助？请提供以上信息。
```

---

## 使用示例 📝

### 示例 1：创建多维表格后自动添加权限

**用户**：帮我创建一个多维表格叫「项目进度追踪」

**Agent 执行流程**：

```
[1/3] 创建多维表格...
      → 调用 feishu_bitable_create_app(name="项目进度追踪")
      → 返回 app_token: "bascnxxx"

[2/3] 添加用户权限...
      → 触发 feishu-perm-auto skill
      → 检查配置：appId ✓ appSecret ✓ ownerOpenId ✓
      → 获取 tenant_access_token
      → 调用权限 API 添加 full_access

[3/3] 完成！
```

**Agent 回复**：

```
✅ 多维表格「项目进度追踪」已创建！

🔗 链接：https://xxx.feishu.cn/base/bascnxxx
🔐 已自动为你添加完整权限，可直接访问和编辑
```

---

### 示例 2：用户反馈文档无权限

**用户**：这个文档我打不开，提示没权限 https://xxx.feishu.cn/docx/doxcnxxx

**Agent 执行流程**：

```
[1/3] 解析文档信息...
      → URL 解析：token=doxcnxxx, doc_type=docx

[2/3] 检查配置并添加权限...
      → 检查配置：appId ✓ appSecret ✓ ownerOpenId ✓
      → 获取 tenant_access_token
      → 调用权限 API 添加 full_access

[3/3] 完成！
```

**Agent 回复**：

```
✅ 权限添加成功！

📄 文档：doxcnxxx
🔗 链接：https://xxx.feishu.cn/docx/doxcnxxx
👤 权限：完整权限 (full_access)

你现在可以直接访问和编辑这个文档了。
```

---

### 示例 3：首次使用，配置缺失

**用户**：帮我创建一个飞书文档

**Agent 执行流程**：

```
[1/2] 检查配置...
      → 读取 ~/.openclaw/openclaw.json
      → 发现 channels.feishu.appId 缺失

[2/2] 引导配置...
```

**Agent 回复**：

```
⚠️ 还没配置飞书应用凭证，需要先设置一下：

📱 获取飞书应用凭证：

1. 打开浏览器，访问：https://open.feishu.cn/app
2. 登录你的飞书账号
3. 点击「创建企业自建应用」或选择已有应用
4. 在左侧菜单找到「凭证与基础信息」
5. 复制以下内容：
   - App ID（cli_ 开头的字符串）
   - App Secret（点击「查看」后显示）

请把 App ID 和 App Secret 发给我，格式如下：
appId: cli_xxxxxxxx
appSecret: xxxxxxxx
```

**用户回复后**：

```
用户：appId: cli_aabbccdd
      appSecret: 1234567890abcdef

Agent：
[1/2] 验证凭证...
      → 获取 tenant_access_token 成功 ✓

[2/2] 保存配置...
      → 更新 ~/.openclaw/openclaw.json
```

**Agent 回复**：

```
✅ 飞书应用配置成功！

现在可以正常使用飞书功能了。需要我帮你创建文档吗？
```

---

### 示例 4：权限已存在（幂等处理）

**用户**：给这个文档加权限 https://xxx.feishu.cn/base/bascnxxx

**Agent 执行流程**：

```
[1/3] 解析文档信息...
      → token=bascnxxx, doc_type=bitable

[2/3] 添加权限...
      → 调用 API 返回错误码 99991661（成员已存在）

[3/3] 幂等处理...
      → 视为成功，无需重复添加
```

**Agent 回复**：

```
✅ 权限已存在！

📄 文档：bascnxxx
🔗 链接：https://xxx.feishu.cn/base/bascnxxx
👤 权限：完整权限 (full_access)

你已经有这个文档的完整权限了。
```

---

## 配置引导流程 🔧

> 当第一步检查发现配置缺失时，按以下流程引导用户配置。

### A. 获取 App ID 和 App Secret

```
📱 获取飞书应用凭证：

1. 打开浏览器，访问：https://open.feishu.cn/app
2. 登录你的飞书账号
3. 点击「创建企业自建应用」或选择已有应用
4. 在左侧菜单找到「凭证与基础信息」
5. 复制以下内容：
   - App ID（cli_ 开头的字符串）
   - App Secret（点击「查看」后显示）

请把 App ID 和 App Secret 发给我，格式如下：
appId: cli_xxxxxxxx
appSecret: xxxxxxxx
```

### B. 获取 ownerOpenId

**优先从会话上下文提取**：若上下文中出现 `user:ou_xxx` 格式，直接提取 `ou_xxx` 使用。

**否则引导用户获取**：

1. 登录 [API 调试台](https://open.feishu.cn/api-explorer)，找到发送消息接口
2. 在「查询参数」页签，将 `user_id_type` 设置为 `open_id`
3. 点击「快速复制 open_id」

详见：https://open.feishu.cn/document/faq/trouble-shooting/how-to-obtain-openid

**用户回复后**：
1. 验证格式是否正确（以 `ou_` 开头）
2. 在当前会话中使用此 ownerOpenId

### C. 配置应用权限

```
⚠️ 在使用前，还需要给应用添加权限：

1. 在飞书开放平台，点击左侧「权限管理」
2. 搜索并开通以下权限：
   - docs:permission.member:create (添加云文档协作者)

3. 点击「发布版本」使权限生效

如果权限显示「待确认」，需要联系企业管理员审批。
```

---

## 权限级别说明 🔐

| 权限值 | 中文名 | 能做什么 | 适用场景 |
|--------|--------|----------|----------|
| `view` | 只读 | 只能查看，不能修改 | 分享给他人查看 |
| `edit` | 可编辑 | 可以修改内容，不能管理权限 | 协作编辑 |
| `full_access` | 完整权限 | 可以编辑、管理权限、删除 | 文档所有者（推荐） |

> 💡 建议：给用户添加 `full_access` 权限，这样用户可以完全控制文档。

**权限选择建议**：

| 场景 | 推荐权限 | 原因 |
|------|----------|------|
| 用户自己的文档 | `full_access` | 完全控制 |
| 协作编辑 | `edit` | 避免误删 |
| 只读分享 | `view` | 安全最小化 |

> 💡 默认使用 `full_access`，但可在执行时询问用户需求。

---

## 错误处理大全 ⚠️

| 错误码 | 错误信息 | 原因 | 解决方案 | 处理动作 |
|--------|---------|------|----------|----------|
| `10003` | app id or app secret is invalid | App ID 或 App Secret 错误 | 检查配置，确保复制正确 | 重新配置后重试 |
| `99991661` | 成员已存在 | 用户已有权限 | 视为成功，无需处理 | 直接返回成功 |
| `99991663` | Invalid access token | token 过期或无效 | 重新获取 tenant_access_token | 重新执行 2.2 |
| `99991664` | Permission denied | 应用没有权限 | 引导配置应用权限 | 跳转配置引导 C |
| `99991600` | token not found | 文档 token 不存在 | 检查 file_token 是否正确 | 确认后重试 |

---

## 最佳实践 💡

### 配置管理

- ✅ 首次使用时引导用户配置
- ✅ 配置保存后，后续自动读取
- ⚠️ 不要在日志中输出 App Secret

### 错误处理

- ✅ 每一步都要检查返回的 code
- ✅ 失败时给出清晰的错误原因
- ✅ 提供具体的解决方案和处理动作

### 用户体验

- ✅ 每步输出进度提示 `[1/4] [2/4] [3/4] [4/4]`
- ✅ 成功后返回文档链接
- ✅ 告诉用户权限已添加
- ✅ 提示用户可以直接访问
- ✅ 成功后询问用户是否需要将 ownerOpenId 写入配置文件

### 安全考虑

- ⚠️ App Secret 不要硬编码在 skill 中
- ⚠️ 不要在回复中显示完整的 App Secret（只显示前4位 + `***`）
- ⚠️ token 有效期约 2 小时，建议缓存避免频繁请求

**敏感信息脱敏**：

| 信息类型 | 原始值 | 脱敏后 |
|---------|--------|--------|
| App Secret | `abc123xyz789` | `abc1***` |
| tenant_access_token | `t-xxx123456` | `t-xxx***` |
| ownerOpenId | `ou_abc123` | `ou_abc***` |

**脱敏实现**：

```python
def mask_secret(s, show=4):
    return s[:show] + '***' if len(s) > show else '***'
```

---

## 相关链接 📎

| 资源 | 链接 |
|------|------|
| 飞书开放平台 | https://open.feishu.cn/app |
| 权限配置指南 | https://open.feishu.cn/document/docs/permission/permission-member/batch_create |
| 获取 Open ID | https://open.feishu.cn/document/faq/trouble-shooting/how-to-obtain-openid |

---

## 快速参考卡片 📌

```
┌─────────────────────────────────────────────────────────┐
│  飞书权限添加快速参考                                    │
├─────────────────────────────────────────────────────────┤
│  1. 检查配置：~/.openclaw/openclaw.json                 │
│     - appId (必需)                                      │
│     - appSecret (必需)                                  │
│     - ownerOpenId (可选，会话上下文补充)                  │
│     - 应用权限: docs:permission.member:create (必需)     │
├─────────────────────────────────────────────────────────┤
│  2. 获取 tenant_access_token：                           │
│     POST /auth/v3/tenant_access_token/internal          │
│     Body: {app_id, app_secret}                          │
├─────────────────────────────────────────────────────────┤
│  3. 获取云文档 token：                                   │
│     创建时返回 或 从 URL 解析                            │
│     自动识别 doc_type: /base/→bitable, /docx/→docx...   │
├─────────────────────────────────────────────────────────┤
│  4. 添加权限：                                          │
│     POST /drive/v1/permissions/{token}/members          │
│     Header: Authorization: Bearer {token}               │
│     Body: {members: [{member_type, member_id, perm}]}   │
├─────────────────────────────────────────────────────────┤
│  文档类型：                                             │
│    bitable | docx | doc | sheet | folder | file | wiki │
│  权限级别：view | edit | full_access                    │
└─────────────────────────────────────────────────────────┘
```