---
name: 方正鸿云编辑助手
description: 方正鸿云学术出版平台自动化技能。使用 browser 工具处理登录和页面交互，API 调用使用 browser.evaluate() 执行。触发关键词：登录方正鸿云、切换刊物、自动催修、自动催审、催审第 X 条、鸿云任务提醒、自动填写送审单、自动注册 DOI、获取登录 Cookie、调用获取刊物信息接口、调用获取发布站点接口、调用获取刊期列表接口、调用获取刊期论文列表接口、调用 DOI 注册接口、将文章{标题}发布到微信公众号。
env:
  FOUNDER_PLATFORM_URL: 平台地址（可选，默认 http://journal.portal.founderss.cn/）
---

# 方正鸿云编辑器浏览器自动化技能

## 环境变量配置（可选）

**以下环境变量均为可选**，如未设置，技能会在需要时提示用户输入：

### 基础配置

| 变量名 | 必需 | 默认值 | 说明 |
|--------|------|--------|------|
| `FOUNDER_PLATFORM_URL` | ❌ | `http://journal.portal.founderss.cn/` | 平台登录地址 |

### 微信发布功能配置（可选）

如需使用 [将文章{标题}发布到微信公众号] 功能，需要配置微信公众号凭证：

| 变量名 | 必需 | 说明 |
|--------|------|------|
| `WECHAT_APP_ID` | ⚠️ 微信发布必需 | 微信公众号 AppID |
| `WECHAT_APP_SECRET` | ⚠️ 微信发布必需 | 微信公众号 AppSecret |

**获取方式**：
1. 登录微信公众平台 (https://mp.weixin.qq.com/)
2. 进入 开发 → 基本配置
3. 获取开发者 ID (AppID) 和 开发者密码 (AppSecret)

**配置方式**（任选其一）：

1. **系统环境变量**：
   ```bash
   export FOUNDER_PLATFORM_URL="http://journal.portal.founderss.cn/"
   export WECHAT_APP_ID="your_appid"
   export WECHAT_APP_SECRET="your_secret"
   ```

2. **使用时输入（推荐）** - 不设置环境变量，首次使用时手动输入

3. **使用默认值** - 不设置环境变量，使用默认平台地址

---

## 核心规则（重要）

### 规则 1：使用 browser.evaluate() 执行 API 调用

**所有 API 接口调用使用 `browser.evaluate()` 在浏览器上下文中执行**，利用浏览器会话的认证状态，避免 Cookie 失效问题。

| 操作 | 正确方式 |
|------|---------|
| 调用获取刊物信息接口 | `browser.evaluate()` 执行 `fetch()` |
| 调用获取发布站点接口 | `browser.evaluate()` 执行 `fetch()` |
| 调用获取刊期列表接口 | `browser.evaluate()` 执行 `fetch()` |
| 调用获取刊期论文列表接口 | `browser.evaluate()` 执行 `fetch()` |
| 调用 DOI 注册接口 | `browser.evaluate()` 执行 `fetch()` |
| 搜索稿件接口 | `browser.evaluate()` 执行 `fetch()` |
| 版本管理接口 | `browser.evaluate()` 执行 `fetch()` |
| 微信文件接口 | `browser.evaluate()` 执行 `fetch()` |

**调用格式示例**：
```javascript
browser.act(action=act, kind=evaluate, fn="(async () => { const r = await fetch('/api/endpoint', { headers: { 'orgcode': org_code } }); return r.json(); })()")
```

### 规则 2：Cookie 复用机制

**所有需要登录的功能，必须先检查会话中是否存在有效的 `founder_cookie`**：

```
开始功能
  ↓
检查会话变量 founder_cookie
  ↓
├─ 存在且有效 → 直接使用
└─ 为空或失效 → 执行 [获取登录 Cookie] → 存储到会话
```

**Cookie 有效性检查**：
- 会话变量为空 → 需要重新获取
- API 调用返回登录重定向（302 到 `/oauth/authorize`）→ Cookie 失效，需要重新获取

**会话变量说明**：
- `founder_cookie` 存储在当前会话的临时内存中
- 会话结束后自动清除

### 规则 3：API 调用范围限制（安全）

**`browser.evaluate()` 仅调用方正鸿云平台的官方 API 接口**，无任意 URL 访问行为：

| 特性 | 说明 |
|------|------|
| **API 域名** | 由环境变量 `FOUNDER_PLATFORM_URL` 决定，默认 `journal.portal.founderss.cn` |
| **域名验证** | 所有方正鸿云平台 API 请求的目标域名必须与 `FOUNDER_PLATFORM_URL` 同源 |
| **API 路径** | 不限具体路径，在平台域名下按需调用 |
| **第三方服务** | 仅访问 `api.weixin.qq.com`（微信发布功能必需） |
| **无任意 URL** | 不支持用户传入任意 URL 进行请求 |
| **请求透明** | 所有 API 调用在浏览器开发者工具中可见 |

**安全保证**：
- ✅ 方正鸿云平台 API 调用在浏览器上下文中执行，受同源策略限制
- ✅ 微信 API 调用通过 `exec + curl` 执行，目标固定为 `api.weixin.qq.com`
- ✅ 不调用任何未声明的外部服务
- ✅ 所有网络请求可通过浏览器开发者工具审计

### 规则 4：API 调用方式说明

| API 类型 | 调用方式 | 权限需求 | 目标域名 |
|---------|---------|---------|---------|
| 方正鸿云平台 API | `browser.evaluate()` + `fetch()` | `browser` | `FOUNDER_PLATFORM_URL` |
| 微信公众号 API | `exec` + `curl` | `exec` | `api.weixin.qq.com` |

**说明**：
- ✅ 方正鸿云平台 API 在浏览器上下文中执行，复用登录会话（Cookie）
- ✅ 微信 API 通过 shell curl 调用，目标固定为 `api.weixin.qq.com`
- ❌ 不调用任何未声明的外部服务
- ❌ 不接受用户传入的任意 URL

---

## 🔒 安全风险提示

### Cookie 处理说明

| 项目 | 说明 |
|------|------|
| **Cookie 来源** | 用户登录方正鸿云平台后生成 |
| **存储位置** | 仅存储在会话内存中（临时变量 `founder_cookie`） |
| **持久化** | ❌ 不写入任何文件或数据库 |
| **会话结束** | ✅ 自动清除 |
| **用户审计** | 可通过浏览器开发者工具 Network 标签查看 |

### 权限使用说明

| 权限 | 用途 | 范围限制 |
|------|------|---------|
| `browser` | 登录、页面交互、方正鸿云平台 API 调用 | 仅限 `FOUNDER_PLATFORM_URL` 域名 |
| `exec` | 微信公众号 API 调用（curl） | 仅限 `api.weixin.qq.com` |

### 用户控制

- ✅ 用户可随时查看会话变量内容
- ✅ 用户可通过浏览器开发者工具审计所有网络请求
- ✅ 用户可选择不使用微信发布功能（无需 exec）
- ✅ 所有 API 调用在 SKILL.md 中明确声明

---

## ⚠️ 安全模型说明

### 信任模型

本技能是 **instruction-only** 类型，安全约束基于以下机制：

| 约束类型 | 强制方式 | 说明 |
|---------|---------|------|
| **同源策略** | ✅ 浏览器强制 | 无法访问跨域资源（CORS 限制） |
| **API 调用范围** | ⚠️ 程序性约束 | 依赖技能代码严格遵守声明 |
| **Cookie 使用** | ⚠️ 程序性约束 | 依赖技能代码不滥用 |
| **权限使用** | ⚠️ 程序性约束 | 依赖技能代码按声明用途使用 |

### 技术限制（浏览器强制）

以下限制由浏览器自动执行，**无法被技能代码绕过**：

| 限制 | 说明 | 强制机制 |
|------|------|---------|
| **跨域请求** | 无法访问未声明 CORS 的外部 API | CORS 策略 |
| **跨域 Cookie** | 无法读取其他网站的 Cookie | 同源策略 |
| **localStorage** | 无法访问其他域名的 localStorage | 同源策略 |
| **文件系统** | 无法直接访问用户文件系统 | 浏览器沙箱 |

### 程序性约束（依赖代码自律）

以下约束依赖技能代码严格执行，**用户可通过审计验证**：

| 约束 | 验证方法 |
|------|---------|
| 仅访问声明的域名 | 浏览器 Network 标签审计 |
| 仅调用声明的 API | 代码审查 + Network 标签 |
| Cookie 不持久化 | 检查会话变量 + 文件系统 |
| 权限不滥用 | 代码审查 + 运行时审计 |

### 用户如何验证

#### 1. 代码审查（使用前）

- ✅ 技能代码完全开源，可在 ClawHub 查看
- ✅ 所有 API 调用在 SKILL.md 中明确声明
- ✅ 权限声明在 `_meta.json` 中公开

#### 2. 运行时审计（使用中）

- ✅ 打开浏览器开发者工具（F12）
- ✅ 查看 **Network** 标签 - 所有请求可见
- ✅ 查看 **Application** 标签 - Cookie 和存储可见

#### 3. 会话变量检查（随时）

- ✅ 用户可随时要求查看会话变量内容
- ✅ 用户可要求检查 `founder_cookie` 值
- ✅ 会话结束后变量自动清除

### 违规的技术后果

如果技能代码尝试违反声明：

| 违规行为 | 技术后果 |
|---------|---------|
| 访问未声明的域名 | CORS 阻止请求 |
| 读取其他网站 Cookie | 同源策略阻止 |
| 持久化存储 Cookie | 用户可在文件系统检查 |
| 调用未声明的 API | Network 标签可见 |

### 开源承诺

- ✅ 技能代码完全开源
- ✅ 无隐藏功能或后门
- ✅ 欢迎安全社区审查
- ✅ 发现问题请报告

---

## 触发关键词与操作流程

### 1. 登录方正鸿云

**触发词**: `登录方正鸿云`

**操作步骤**:
1. 使用 `browser` 工具打开平台地址
2. 等待登录页面加载完成
3. 等待用户输入用户名和密码
4. 用户完成登录后，等待进入主页面
5. 执行 [获取登录 Cookie] 保存到会话变量
6. 向用户反馈登录完成

---

### 2. 切换刊物

**触发词**: `切换刊物` 或 `切换刊物 {刊物名称}`

**功能说明**: 获取用户有权限的刊物列表，支持带参数切换刊物，切换后自动初始化新刊物并刷新 Cookie

**操作步骤**:

#### 第一步：检查 Cookie
- 检查会话变量 `founder_cookie` 是否为空
- 若为空 → 执行 [登录方正鸿云]

#### 第二步：调用获取刊物信息接口
1. **通过 browser.evaluate 调用**：
   ```javascript
   browser.act(action=act, kind=evaluate, fn="(async () => { const r = await fetch('/je-api/journal-edit-reviewer/v1/review/journal?timestamps=' + Date.now()); return r.json().then(d => JSON.stringify(d)); })()")
   ```
2. **解析返回的 JSON 数据**：
   - 提取 `data.magazineId` → `z_journal_id`
   - 提取 `data.orgCode` → `org_code`
   - 存入会话变量 `z_journal_id` 和 `org_code`
   - 同时更新 `journal_id` 和 `journal_name`

#### 第三步：选择刊物
- **如果用户指定了刊物名称** → 模糊匹配刊物列表
- **如果未指定** → 提示用户输入刊物名称
- **如果匹配成功** → 提示："✅ 匹配成功"

#### 第四步：新刊初始化
- 调用新刊初始化接口
- 返回 `status=0` → 初始化成功

#### 第五步：重新获取登录 Cookie
- 从浏览器会话提取最新 Cookie
- 更新会话变量 `founder_cookie`

#### 向用户反馈
```
✅ 切换刊物完成

当前刊物：{journal_name}
刊物 ID: {journal_id}
机构代码：{org_code}
```

---

### 2.1 将文章{标题}发布到微信公众号

**触发词**: `将文章 {文章标题} 发布到微信公众号`

**功能说明**: 根据文章标题搜索稿件，获取微信格式文件，调用微信 API 发布到微信公众号

**操作步骤**:

#### 第一步：检查 Cookie
- 检查会话变量 `founder_cookie` 是否为空
- 若为空 → 执行 [登录方正鸿云]

#### 第二步：执行 [调用获取刊物信息接口]
1. **调用技能已有功能** [调用获取刊物信息接口]
2. **通过 browser.evaluate 调用**：
   ```javascript
   browser.act(action=act, kind=evaluate, fn="(async () => { const r = await fetch('/je-api/journal-edit-reviewer/v1/review/journal?timestamps=' + Date.now()); return r.json().then(d => JSON.stringify(d)); })()")
   ```
3. **解析返回的 JSON 数据**：
   - 提取 `data.magazineId` → `z_journal_id`
   - 提取 `data.orgCode` → `org_code`
   - 存入会话变量 `z_journal_id` 和 `org_code`
   - 同时更新 `journal_id` 和 `journal_name`（技能已有功能会自动更新）

#### 第三步：调用搜索稿件接口（POST）
1. **通过 browser.evaluate 调用**（保持浏览器会话）：
   ```javascript
   browser.act(action=act, kind=evaluate, fn="(async () => { const r = await fetch('/article/portalDocList.do', { method: 'POST', headers: { 'Content-Type': 'application/json; charset=UTF-8', 'orgcode': org_code }, body: JSON.stringify({ magazineId: z_journal_id, sectionState: '', currentState: 0, currentHandler: 2, isPriority: null, collateTimes: '', magazineIssueId: '', preIssue: '', editorId: '', keyWord: article_title, pageNumer: 1, sortType: '', sortField: '', scopeone: 1, portal: 'portal', preIssueShow: '1' }) }); return r.json().then(d => JSON.stringify(d)); })()")
   ```
   **注意**：
   - `z_journal_id`、`org_code` 和 `article_title` 需要从会话变量传入
   - 请求头必须包含 `orgcode`，值为会话变量 `org_code`
2. **解析返回的 JSON 数据**：
   - 提取 `data.rows` 数组（稿件列表）
   - **如果 `data.rows` 为空或长度为 0** → 提示："❌ 搜索的稿件为空"，结束流程
   - 获取第一条稿件的 `id` → `article_id`
   - 存入会话变量 `article_id`

**返回 JSON 样例**：
```json
{
  "status": 0,
  "message": "成功",
  "data": {
    "total": 2,
    "pageCount": 1,
    "pageNumber": 1,
    "pageSize": "50",
    "rows": [
      { "id": "29533" },
      { "id": "29532" }
    ]
  }
}
```

#### 第四步：循环版本记录查找微信文件 ID
1. **通过 browser.evaluate 调用**（保持浏览器会话）：
   ```javascript
   browser.act(action=act, kind=evaluate, fn="(async () => { const r = await fetch('/article/versionManage.do?id=' + article_id + '&userId=851&pageNumer=1&flowNode=f26_59&portal=portal&isyw=false&timestamps=' + Date.now(), { headers: { 'orgcode': org_code } }); return r.json().then(d => JSON.stringify(d)); })()")
   ```
   **注意**：
   - `article_id` 和 `org_code` 需要从会话变量传入
   - 请求头必须包含 `orgcode`，值为会话变量 `org_code`
2. **解析返回的 JSON 数据**：
   - 提取 `data.rows` 数组（版本记录列表）
   - 循环遍历每个版本记录
   - 对于每个版本，检查 `fileId` 数组
   - 找到第一个 `code=20` 的文件（微信格式文件）
   - 提取 `publishFileId` → `wechat_file_id`
   - 存入会话变量 `wechat_file_id`
   - **如果遍历完所有版本记录未找到 code=20 的文件** → 提示："❌ 未找到微信格式文件"，结束流程

#### 第五步：调用微信文件接口获取推文 URL
1. **通过 browser.evaluate 调用**（保持浏览器会话）：
   ```javascript
   browser.act(action=act, kind=evaluate, fn="(async () => { const r = await fetch('/article/wechat.do?fileId=' + wechat_file_id + '&timestamps=' + Date.now(), { headers: { 'orgcode': org_code } }); return r.json().then(d => JSON.stringify(d)); })()")
   ```
   **注意**：
   - `wechat_file_id` 和 `org_code` 需要从会话变量传入
   - 请求头必须包含 `orgcode`，值为会话变量 `org_code`
2. **解析返回的 JSON 数据**：
   - 提取 `data.fullUrl` → `wechat_file_url`
   - 存入会话变量 `wechat_file_url`

#### 第六步：执行将网页发布到微信公众号
1. **关闭浏览器**（API 调用完成）
2. **使用浏览器打开微信格式页面并抓取完整 HTML**：
   ```javascript
   // 打开页面
   browser.open(url="${wechat_file_url}")
   // 等待页面加载后获取完整 HTML
   browser.act(action=act, kind=evaluate, fn="document.documentElement.outerHTML")
   ```
3. **保存 HTML 到临时文件**：
   ```bash
   # 将获取的 HTML 保存到 /tmp/wechat_article_{article_id}.html
   ```
4. **调用微信 API 发布文章**：
   
   **4.1 获取 access_token**：
   ```bash
   curl -s "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=${WECHAT_APP_ID}&secret=${WECHAT_APP_SECRET}"
   # 返回：{"access_token":"xxx","expires_in":7200}
   ```
   
   **4.2 上传封面图获取 media_id**：
   ```bash
   curl -s "https://api.weixin.qq.com/cgi-bin/material/add_material?access_token=${ACCESS_TOKEN}&type=image" \
     -F "media=@/tmp/cover.jpg" \
     -F 'description={"title":"cover","introduction":"cover image"}'
   # 返回：{"media_id":"xxx","url":"xxx"}
   ```
   
   **4.3 创建草稿**：
   ```bash
   curl -s "https://api.weixin.qq.com/cgi-bin/draft/add?access_token=${ACCESS_TOKEN}" \
     -H "Content-Type: application/json" \
     -d '{
       "articles": [{
         "title": "${article_title}",
         "author": "${authors}",
         "digest": "${digest}",
         "content": "${html_content}",
         "thumb_media_id": "${media_id}",
         "show_cover_pic": 1,
         "need_open_comment": 0,
         "only_fans_can_comment": 0
       }]
     }'
   # 返回：{"media_id":"xxx","item":[]}
   ```
   
   **4.4 发布文章**：
   ```bash
   curl -s "https://api.weixin.qq.com/cgi-bin/freepublish/submit?access_token=${ACCESS_TOKEN}" \
     -H "Content-Type: application/json" \
     -d '{"media_id":"${draft_media_id}"}'
   # 返回：{"errcode":0,"errmsg":"ok","publish_id":xxx,"msg_data_id":xxx}
   ```
   
   **4.5 获取文章 URL**：
   ```bash
   curl -s "https://api.weixin.qq.com/cgi-bin/freepublish/get?access_token=${ACCESS_TOKEN}" \
     -H "Content-Type: application/json" \
     -d '{"publish_id":${publish_id}}'
   # 返回：{"article_detail":{"item":[{"article_url":"http://mp.weixin.qq.com/s?..."}]}}
   ```
5. **解析发布结果**：
   - 成功 → 返回文章 URL 和 publish_id
   - 失败 → 返回错误码和错误信息

#### 向用户反馈
```
✅ 文章发布完成

文章标题：{article_title}
稿件 ID: {article_id}
微信文件 ID: {wechat_file_id}
发布状态：成功/失败
文章 URL: {article_url}
publish_id: {publish_id}
```

**注意**：
- 稿件标题支持模糊匹配，取搜索结果第一条
- 循环所有版本记录，找到第一个含 code=20 的微信格式文件即停止
- code=20 表示微信格式文件
- **API 调用必须通过 browser.evaluate 执行**
- **Step 3-5 的请求头必须包含 `orgcode`**，值为 Step 2 获取的 `org_code`
- 发布流程：获取 access_token → 上传封面图 → 创建草稿 → 发布 → 获取文章 URL
- 文章直接发布到微信公众号（非草稿箱），用户可在公众号后台查看

---

### 3. 自动催修

**触发词**: `自动催修`

**功能说明**: 获取退修中阶段的过期稿件列表并展示（不执行催修操作）

**操作步骤**:
1. 检查 Cookie，如为空则先登录
2. 调用获取退修论文列表接口（使用 `browser.evaluate()`）
3. 解析返回的 JSON 数据
4. 筛选出过期的稿件（超过退修期限）
5. 向用户展示过期稿件列表

**返回数据示例**：
```json
{
  "status": 0,
  "data": {
    "rows": [
      {
        "id": "12345",
        "title": "论文标题",
        "author": "作者姓名",
        "deadline": "2024-01-01",
        "overdue_days": 5
      }
    ]
  }
}
```

**向用户反馈**：
```
📋 退修中过期稿件清单

共找到 {count} 篇过期稿件：

1. {title}
   作者：{author}
   退修期限：{deadline}
   已过期：{overdue_days} 天

2. ...
```

**注意**：
- 本功能仅**展示过期稿件列表**，不执行催修操作
- 过期判断标准：当前日期 > 退修期限

---

### 4. 自动催审

**触发词**: `自动催审`

**功能说明**: 获取送专家审阶段的过期稿件列表并展示（不执行催审操作）

**操作步骤**:
1. 检查 Cookie，如为空则先登录
2. 调用获取送专家审论文列表接口（使用 `browser.evaluate()`）
3. 解析返回的 JSON 数据
4. 筛选出过期的稿件（超过审稿期限）
5. 将列表存储到会话变量 `last_auto_cuishen_list`
6. 向用户展示过期稿件列表

**向用户反馈**：
```
📋 送审中过期稿件清单

共找到 {count} 篇过期稿件：

1. {title}
   作者：{author}
   送审日期：{send_date}
   已过期：{overdue_days} 天

2. ...

💡 提示：可使用"催审第 X 条"对指定稿件执行催审
```

**注意**：
- 本功能仅**展示过期稿件列表**，不执行催审操作
- **重要**：执行完成后，将返回列表存储到会话变量 `last_auto_cuishen_list`，供"催审第 X 条"功能引用

---

### 4.1 催审第 X 条（联动功能）

**触发词**: `催审第 X 条`（例如：`催审第 1 条`、`催审第 2 条`）

**前置条件**: 必须先执行 [自动催审] 功能

**功能说明**: 对指定稿件执行催审操作，向审稿专家发送提醒通知

**操作步骤**:

#### 第一步：调用稿件专家审列表接口
1. 检查会话变量 `last_auto_cuishen_list` 是否存在
2. 根据用户指定的序号获取稿件信息
3. 提取稿件 ID 和审稿专家信息

#### 第二步：获取模板
1. 调用催审模板接口
2. 获取模板内容和参数

#### 第三步：循环催审
1. 调用催审接口发送提醒
2. 记录催审结果

**向用户反馈**：
```
✅ 催审完成

稿件：{title}
审稿专家：{expert_name}
催审结果：成功/失败
```

**注意**：
- 必须先执行 [自动催审] 才能使用此功能
- 催审操作会向审稿专家发送邮件/短信提醒

---

### 5. 鸿云任务提醒

**触发词**: `鸿云任务提醒`

**功能说明**: 获取待处理任务列表并提醒

**操作步骤**:
1. 检查 Cookie，如为空则先登录
2. 调用任务列表接口
3. 解析返回数据
4. 筛选出待处理的任务
5. 向用户展示任务清单

**向用户反馈**：
```
📋 待处理任务清单

共 {count} 个待处理任务：

1. {task_name}
   类型：{task_type}
   截止日期：{deadline}

2. ...
```

---

### 6. 自动填写送审单

**触发词**: `自动填写送审单`

**功能说明**: 自动填写稿件送审单

**操作步骤**:
1. 检查 Cookie，如为空则先登录
2. 提示用户输入稿件信息或选择稿件
3. 调用送审单模板接口
4. 填充送审单内容
5. 提交送审单

**向用户反馈**：
```
✅ 送审单填写完成

稿件 ID: {article_id}
送审单号：{review_form_id}
提交状态：成功/失败
```

---

### 7. 自动注册 DOI

**触发词**: `自动注册 DOI`

**功能说明**: 为论文自动注册 DOI 号

**操作步骤**:
1. 检查 Cookie，如为空则先登录
2. 提示用户输入稿件信息或选择稿件
3. 调用 DOI 注册接口
4. 获取 DOI 号
5. 更新稿件信息

**向用户反馈**：
```
✅ DOI 注册完成

稿件 ID: {article_id}
DOI: 10.xxxx/xxxxx
注册状态：成功/失败
```

---

### 8. 获取登录 Cookie

**触发词**: `获取登录 Cookie`

**功能说明**: 从浏览器会话提取 Cookie 并保存到会话变量

**操作步骤**:
1. 检查浏览器是否已打开并登录
2. 使用 `browser.evaluate()` 执行 `document.cookie`
3. 提取 Cookie 字符串
4. 存储到会话变量 `founder_cookie`

**向用户反馈**：
```
✅ Cookie 已获取

状态：有效/失效
有效期：约 2 小时
```

---

### 9. 调用获取刊物信息接口

**触发词**: `调用获取刊物信息接口`

**功能说明**: 获取当前刊物的详细信息

**操作步骤**:
1. 检查 Cookie，如为空则先登录
2. 通过 `browser.evaluate()` 调用接口：
   ```javascript
   browser.act(action=act, kind=evaluate, fn="(async () => { const r = await fetch('/je-api/journal-edit-reviewer/v1/review/journal?timestamps=' + Date.now()); return r.json().then(d => JSON.stringify(d)); })()")
   ```
3. 解析返回的 JSON 数据
4. 提取关键信息并存储到会话变量

**返回数据**：
```json
{
  "status": 0,
  "data": {
    "magazineId": "124",
    "orgCode": "cnkj",
    "name": "刊物名称",
    "id": "uuid"
  }
}
```

**会话变量更新**：
- `z_journal_id` = `data.magazineId`
- `org_code` = `data.orgCode`
- `journal_id` = `data.id`
- `journal_name` = `data.name`

---

### 10. 调用获取发布站点接口

**触发词**: `调用获取发布站点接口`

**功能说明**: 获取发布站点信息

**操作步骤**:
1. 检查 Cookie，如为空则先登录
2. 通过 `browser.evaluate()` 调用接口
3. 解析返回数据
4. 存储站点 ID 到会话变量 `site_id`

---

### 11. 调用获取刊期列表接口

**触发词**: `调用获取刊期列表接口`

**功能说明**: 获取刊期列表（年份 + 刊期）

**操作步骤**:
1. 检查 Cookie，如为空则先登录
2. 通过 `browser.evaluate()` 调用接口
3. 解析返回数据
4. 存储刊期列表到会话变量 `period_list`

**返回数据示例**：
```json
{
  "status": 0,
  "data": {
    "rows": [
      { "id": "848", "year": "2024", "issue": "1" },
      { "id": "849", "year": "2024", "issue": "2" }
    ]
  }
}
```

---

### 12. 调用获取刊期论文列表接口

**触发词**: `调用获取刊期论文列表接口`

**功能说明**: 获取指定刊期的论文列表（按栏目分组）

**操作步骤**:
1. 检查 Cookie，如为空则先登录
2. 通过 `browser.evaluate()` 调用接口
3. 解析返回数据
4. 存储论文列表到会话变量 `article_list`

**返回数据示例**：
```json
{
  "status": 0,
  "data": {
    "sections": [
      {
        "sectionName": "栏目名称",
        "articles": [
          { "id": "123", "title": "论文标题", "author": "作者" }
        ]
      }
    ]
  }
}
```

---

### 13. 调用 DOI 注册接口

**触发词**: `调用 DOI 注册接口`

**功能说明**: 调用 DOI 注册 API

**操作步骤**:
1. 检查 Cookie，如为空则先登录
2. 通过 `browser.evaluate()` 调用接口
3. 解析返回数据
4. 获取 DOI 号并更新稿件信息

---

## 会话变量说明

| 变量名 | 用途 | 示例值 |
|--------|------|--------|
| `founder_cookie` | 登录 Cookie | `JSESSIONID=xxx; ...` |
| `journal_id` | 刊物 ID | `fa2bab216a124e11bb264b4ed8d6d2be` |
| `journal_name` | 刊物名称 | `D 组资源发布` |
| `site_id` | 站点 ID | `site123` |
| `z_journal_id` | 刊物 ID（微信发布用） | `124` |
| `org_code` | 机构代码（API 请求头用） | `cnkj` |
| `article_id` | 稿件 ID | `9727` |
| `wechat_file_id` | 微信格式文件 ID | `292859` |
| `wechat_file_url` | 微信推文网页地址 | `http://html.journal.founderss.cn/...` |
| `period_list` | 刊期列表 | `[{id, year, issue}, ...]` |
| `period_id` | 选定的刊期 ID | `848` |
| `article_list` | 论文列表（按栏目分组） | `{sections: [...]}` |
| `last_auto_cuishen_list` | 催审列表 | `[{id, title, ...}, ...]` |
| `templateParamObj` | 催审模板参数对象 | `{...}` |

---

## 工具使用说明

### 使用 `browser` 工具的场景

| 操作 | 工具 | 说明 |
|------|------|------|
| 打开登录页面 | `browser.open()` | 打开平台登录页 |
| 页面导航 | `browser.navigate()` | 跳转到指定页面 |
| 页面截图 | `browser.snapshot()` | 获取页面快照 |
| 点击元素 | `browser.act(click)` | 点击按钮/链接 |
| 输入文本 | `browser.act(type)` | 填写表单 |
| 执行 JS | `browser.act(evaluate)` | 在页面上下文执行 JavaScript |
| 获取 Cookie | `browser.act(evaluate)` | 执行 `document.cookie` |
| API 调用 | `browser.act(evaluate)` | 执行 `fetch()` 调用 API |

### 使用 `exec` + `curl` 的场景

| 操作 | 工具 | 说明 |
|------|------|------|
| 微信 API 调用 | `exec` + `curl` | 发布文章到微信公众号 |
| 文件操作 | `exec` | 保存临时文件 |

---

## 错误处理

### 重试与退出机制（重要）

**API 调用失败处理**：
- 第 1 次失败 → 等待 1 秒后重试
- 第 2 次失败 → 等待 2 秒后重试
- 第 3 次失败 → 提示用户"接口调用失败"，结束当前流程

**Cookie 失效处理**：
- 检测到 Cookie 失效 → 重新执行 [获取登录 Cookie]
- 如浏览器未登录 → 提示用户重新登录

### 其他错误处理

| 错误类型 | 处理方式 |
|----------|----------|
| 网络错误 | 重试 3 次，失败后提示用户检查网络 |
| 接口返回错误 | 显示错误信息，提示用户联系管理员 |
| 会话变量缺失 | 提示用户先执行前置功能 |
| 参数错误 | 提示用户检查输入参数 |

---

## 实现示例

**示例 1: 登录并切换刊物**
```
用户：登录方正鸿云
助手：打开浏览器，等待用户登录 → 获取 Cookie → ✅ 登录完成

用户：切换刊物
助手：获取刊物列表 → 等待用户输入 → 切换刊物 → ✅ 切换完成
```

**示例 2: 发布文章到微信**
```
用户：将文章 野巴旦杏 AlsCBF 基因的克隆及生物信息学分析 2 发布到微信公众号
助手：
  Step 1: 检查 Cookie → 有效
  Step 2: 获取刊物信息 → z_journal_id=124, org_code=cnkj
  Step 3: 搜索稿件 → article_id=9727
  Step 4: 查找微信文件 → wechat_file_id=292859
  Step 5: 获取推文 URL → wechat_file_url=...
  Step 6: 发布到微信 → ✅ 发布成功
```

---

## 注意事项

1. **所有 API 调用必须使用 `browser.evaluate()`**，在浏览器上下文中执行 `fetch()`
2. **必须先检查 Cookie**，如为空或失效则重新获取
3. **微信发布功能需要额外配置**：
   - 微信公众号 APP_ID
   - 微信公众号 APP_SECRET
   - 封面图片路径
4. **会话变量仅在当前会话有效**，会话结束后自动清除
5. **部分功能有前置依赖**，如"催审第 X 条"需要先执行"自动催审"

---

## 版本历史

- **V0.1.5** (2026-03-18): 修复能力声明不匹配问题，统一使用 browser.evaluate()，移除硬编码凭证
- **V0.1.4** (2026-03-18): 新增微信发布功能，优化 API 调用流程
- **V0.1.0** (2026-03-14): 初始版本
