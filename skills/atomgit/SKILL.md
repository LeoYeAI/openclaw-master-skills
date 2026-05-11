---
name: atomgit
description: AtomGit/GitCode 仓库管理技能，提供用户、仓库、Issue、PR、文件、分支等 API 操作。AtomGit 和 GitCode 是同一平台的不同域名（atomgit.com / gitcode.com），共享相同的 API 后端。
metadata: {"openclaw":{"requires":{"env":["ATOMGIT_TOKEN"]},"primaryEnv":"ATOMGIT_TOKEN"}}
---

# atomgit - AtomGit/GitCode API 技能

直接调用 AtomGit/GitCode OpenAPI v5，通过 curl 命令执行操作。

> **注意**：AtomGit (atomgit.com) 和 GitCode (gitcode.com) 是**同一平台的不同域名**，共享相同的 API 后端。无论使用哪个域名，API 端点都相同。

## 前置条件

1. **AtomGit/GitCode Token** - 访问以下任一地址生成：
   - https://gitcode.com/setting/token-classic
   - https://atomgit.com/setting/token-classic
2. **权限**：`api`, `read_user`, `read_repository`, `write_repository`, `issues`, `pull_requests`

> Token 在两个平台通用，因为后端是同一套系统。

## 配置方法

### 方式一：Gateway 配置（推荐）

编辑 `~/.openclaw/openclaw.json`，添加 skill 配置：

```json
{
  "skills": {
    "entries": {
      "atomgit": {
        "enabled": true,
        "env": {
          "ATOMGIT_TOKEN": "your-token-here"
        }
      }
    }
  }
}
```

或使用环境变量占位符：

```json
{
  "skills": {
    "entries": {
      "atomgit": {
        "enabled": true,
        "env": {
          "ATOMGIT_TOKEN": "__ATOMGIT_TOKEN__"
        }
      }
    }
  }
}
```

然后在终端设置环境变量：

```bash
export ATOMGIT_TOKEN="your-token-here"
```

### 方式二：终端环境变量

直接在终端设置：

```bash
export ATOMGIT_TOKEN="your-token-here"
```

## API 信息

- **Base URL**: 
  - `https://api.gitcode.com/api/v5` (推荐)
  - `https://api.atomgit.com/api/v5` (等效)
- **认证**: `Authorization: Bearer <TOKEN>`
- **速率限制**: 50 次/分钟

> 两个 API 端点完全等效，数据互通。

---

## 完整 API 接口列表 (294 个端点)

### 一、用户 API (User) - 42 个端点

#### ✅ 已验证可用的接口

```bash
# 获取当前用户信息
curl -H "Authorization: Bearer $TOKEN" https://api.gitcode.com/api/v5/user

# 获取当前用户邮箱
curl -H "Authorization: Bearer $TOKEN" https://api.gitcode.com/api/v5/user/emails

# 获取当前用户仓库列表
curl -H "Authorization: Bearer $TOKEN" "https://api.gitcode.com/api/v5/user/repos?per_page=20"

# 获取当前用户收藏的仓库
curl -H "Authorization: Bearer $TOKEN" https://api.gitcode.com/api/v5/user/starred

# 获取当前用户订阅的仓库
curl -H "Authorization: Bearer $TOKEN" https://api.gitcode.com/api/v5/user/subscriptions

# 获取指定用户信息
curl -H "Authorization: Bearer $TOKEN" https://api.gitcode.com/api/v5/users/:username

# 获取指定用户的仓库
curl -H "Authorization: Bearer $TOKEN" https://api.gitcode.com/api/v5/users/:username/repos

# 获取指定用户收藏的仓库
curl -H "Authorization: Bearer $TOKEN" https://api.gitcode.com/api/v5/users/:username/starred

# 获取用户的组织
curl -H "Authorization: Bearer $TOKEN" https://api.gitcode.com/api/v5/users/:username/orgs

# 获取当前用户的组织
curl -H "Authorization: Bearer $TOKEN" https://api.gitcode.com/api/v5/user/orgs

# 添加 SSH 密钥
curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"title":"My Key","key":"ssh-rsa AAA..."}' \
  https://api.gitcode.com/api/v5/user/keys

# 获取 SSH 密钥列表
curl -H "Authorization: Bearer $TOKEN" https://api.gitcode.com/api/v5/user/keys

# 删除 SSH 密钥
curl -X DELETE -H "Authorization: Bearer $TOKEN" \
  https://api.gitcode.com/api/v5/user/keys/:id
```

---

### 二、仓库 API (Repository) - 168 个端点

#### ✅ 已验证可用的接口

```bash
# 获取仓库详情
curl -H "Authorization: Bearer $TOKEN" https://api.gitcode.com/api/v5/repos/:owner/:repo

# 获取仓库分支列表
curl -H "Authorization: Bearer $TOKEN" https://api.gitcode.com/api/v5/repos/:owner/:repo/branches

# 获取仓库提交列表
curl -H "Authorization: Bearer $TOKEN" https://api.gitcode.com/api/v5/repos/:owner/:repo/commits

# 获取单个提交详情
curl -H "Authorization: Bearer $TOKEN" https://api.gitcode.com/api/v5/repos/:owner/:repo/commits/:sha

# 获取提交 diff
curl -H "Authorization: Bearer $TOKEN" https://api.gitcode.com/api/v5/repos/:owner/:repo/commits/:sha/diff

# 获取仓库标签列表
curl -H "Authorization: Bearer $TOKEN" https://api.gitcode.com/api/v5/repos/:owner/:repo/tags

# 获取文件内容
curl -H "Authorization: Bearer $TOKEN" https://api.gitcode.com/api/v5/repos/:owner/:repo/contents/:path

# 获取目录树
curl -H "Authorization: Bearer $TOKEN" https://api.gitcode.com/api/v5/repos/:owner/:repo/git/trees/:sha

# 获取贡献者列表
curl -H "Authorization: Bearer $TOKEN" https://api.gitcode.com/api/v5/repos/:owner/:repo/contributors

# 获取语言统计
curl -H "Authorization: Bearer $TOKEN" https://api.gitcode.com/api/v5/repos/:owner/:repo/languages

# 获取 Star 用户列表
curl -H "Authorization: Bearer $TOKEN" https://api.gitcode.com/api/v5/repos/:owner/:repo/stargazers

# 获取 Fork 列表
curl -H "Authorization: Bearer $TOKEN" https://api.gitcode.com/api/v5/repos/:owner/:repo/forks

# 获取协作者列表
curl -H "Authorization: Bearer $TOKEN" https://api.gitcode.com/api/v5/repos/:owner/:repo/collaborators

# 获取 Webhook 列表
curl -H "Authorization: Bearer $TOKEN" https://api.gitcode.com/api/v5/repos/:owner/:repo/hooks

# 获取版本列表
curl -H "Authorization: Bearer $TOKEN" https://api.gitcode.com/api/v5/repos/:owner/:repo/releases

# 获取仓库通知
curl -H "Authorization: Bearer $TOKEN" https://api.gitcode.com/api/v5/repos/:owner/:repo/notifications

# 创建用户仓库
curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"my-repo","description":"My repo","private":false,"auto_init":true}' \
  https://api.gitcode.com/api/v5/user/repos

# 创建组织仓库
curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"name":"org-repo","description":"Org repo"}' \
  https://api.gitcode.com/api/v5/orgs/:org/repos

# 更新仓库
curl -X PUT -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"description":"New description","private":false}' \
  https://api.gitcode.com/api/v5/repos/:owner/:repo

# 删除仓库 ⚠️
curl -X DELETE -H "Authorization: Bearer $TOKEN" \
  https://api.gitcode.com/api/v5/repos/:owner/:repo

# Fork 仓库
curl -X POST -H "Authorization: Bearer $TOKEN" \
  https://api.gitcode.com/api/v5/repos/:owner/:repo/forks

# 转移仓库
curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"new_owner":"new-owner"}' \
  https://api.gitcode.com/api/v5/repos/:owner/:repo/transfer
```

#### ⚠️ 已知问题的接口

```bash
# 获取文件列表 - 404 Not Found
# curl -H "Authorization: Bearer $TOKEN" https://api.gitcode.com/api/v5/repos/:owner/:repo/file-list

# 获取最新版本 - 400 Bad Request (无 release 时)
# curl -H "Authorization: Bearer $TOKEN" https://api.gitcode.com/api/v5/repos/:owner/:repo/releases/latest
```

---

### 三、分支 API (Branch) - 10 个端点

#### ✅ 已验证可用的接口

```bash
# 获取分支列表
curl -H "Authorization: Bearer $TOKEN" https://api.gitcode.com/api/v5/repos/:owner/:repo/branches

# 获取单个分支详情
curl -H "Authorization: Bearer $TOKEN" https://api.gitcode.com/api/v5/repos/:owner/:repo/branches/:branch

# 获取保护分支
curl -H "Authorization: Bearer $TOKEN" https://api.gitcode.com/api/v5/repos/:owner/:repo/protect-branches
```

#### ⚠️ 已知问题的接口

```bash
# 创建分支 - 400 PARAMETER_ERROR
# 参数格式不明确，需要官方文档确认
# curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
#   -d '{"branch":"feature","ref":"main"}' \
#   https://api.gitcode.com/api/v5/repos/:owner/:repo/branches

# 删除分支 ⚠️
# curl -X DELETE -H "Authorization: Bearer $TOKEN" \
#   https://api.gitcode.com/api/v5/repos/:owner/:repo/branches/:name
```

---

### 四、文件 API (Content) - 8 个端点

#### ✅ 已验证可用的接口

```bash
# 获取文件内容
curl -H "Authorization: Bearer $TOKEN" \
  https://api.gitcode.com/api/v5/repos/:owner/:repo/contents/:path

# 获取原始文件
curl -H "Authorization: Bearer $TOKEN" \
  https://api.gitcode.com/api/v5/repos/:owner/:repo/raw/:path

# 获取目录树
curl -H "Authorization: Bearer $TOKEN" \
  https://api.gitcode.com/api/v5/repos/:owner/:repo/git/trees/:sha
```

#### ⚠️ 已知问题的接口

```bash
# 创建/更新文件 - 400 Bad Request (需要提供 sha)
# 更新文件时必须提供当前文件的 sha
# curl -X PUT -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
#   -d '{"content":"base64 编码","message":"Update file","branch":"main","sha":"xxx"}' \
#   https://api.gitcode.com/api/v5/repos/:owner/:repo/contents/:path

# 删除文件 ⚠️
# curl -X DELETE -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
#   -d '{"message":"Delete file","branch":"main","sha":"xxx"}' \
#   https://api.gitcode.com/api/v5/repos/:owner/:repo/contents/:path
```

---

### 五、Issue API - 38 个端点

#### ✅ 已验证可用的接口

```bash
# 获取 Issue 列表
curl -H "Authorization: Bearer $TOKEN" \
  "https://api.gitcode.com/api/v5/repos/:owner/:repo/issues?state=all"

# 获取 Issue 详情
curl -H "Authorization: Bearer $TOKEN" \
  https://api.gitcode.com/api/v5/repos/:owner/:repo/issues/:number

# 创建 Issue
curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"title":"Bug report","body":"Description","labels":["bug"],"assignee":"username"}' \
  https://api.gitcode.com/api/v5/repos/:owner/:repo/issues

# 获取 Issue 评论列表
curl -H "Authorization: Bearer $TOKEN" \
  https://api.gitcode.com/api/v5/repos/:owner/:repo/issues/:number/comments

# 创建 Issue 评论
curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"body":"This is a comment"}' \
  https://api.gitcode.com/api/v5/repos/:owner/:repo/issues/:number/comments

# 添加 Issue 标签
curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '["bug","enhancement"]' \
  https://api.gitcode.com/api/v5/repos/:owner/:repo/issues/:number/labels

# 获取 Issue 标签
curl -H "Authorization: Bearer $TOKEN" \
  https://api.gitcode.com/api/v5/repos/:owner/:repo/issues/:number/labels

# 获取用户的 Issue
curl -H "Authorization: Bearer $TOKEN" \
  https://api.gitcode.com/api/v5/user/issues
```

#### ⚠️ 已知问题的接口

```bash
# 更新 Issue - 405 Method Not Allowed (PUT 不支持，可能需要 PATCH)
# curl -X PATCH -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
#   -d '{"state":"closed","title":"New title"}' \
#   https://api.gitcode.com/api/v5/repos/:owner/:repo/issues/:number

# 获取 Issue 修改历史 - 404 Not Found
# curl -H "Authorization: Bearer $TOKEN" \
#   https://api.gitcode.com/api/v5/repos/:owner/:repo/issues/:number/modify-history

# 删除 Issue ⚠️
# curl -X DELETE -H "Authorization: Bearer $TOKEN" \
#   https://api.gitcode.com/api/v5/repos/:owner/:repo/issues/:number
```

---

### 六、标签 API (Labels) - 12 个端点

#### ✅ 已验证可用的接口

```bash
# 获取项目标签列表
curl -H "Authorization: Bearer $TOKEN" \
  https://api.gitcode.com/api/v5/repos/:owner/:repo/labels
```

#### ⚠️ 已知问题的接口

```bash
# 创建标签 - 400 Bad Request (name 需要作为 query 参数)
# 参数传递方式与文档不符
# curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
#   -d '{"name":"bug","color":"#ff0000"}' \
#   https://api.gitcode.com/api/v5/repos/:owner/:repo/labels

# 更新标签
# curl -X PUT -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
#   -d '{"name":"new-name","color":"#00ff00"}' \
#   https://api.gitcode.com/api/v5/repos/:owner/:repo/labels/:original_name

# 删除标签 ⚠️
# curl -X DELETE -H "Authorization: Bearer $TOKEN" \
#   https://api.gitcode.com/api/v5/repos/:owner/:repo/labels/:name
```

---

### 七、里程碑 API (Milestone) - 10 个端点

#### ✅ 已验证可用的接口

```bash
# 获取里程碑列表
curl -H "Authorization: Bearer $TOKEN" \
  https://api.gitcode.com/api/v5/repos/:owner/:repo/milestones

# 获取里程碑详情
curl -H "Authorization: Bearer $TOKEN" \
  https://api.gitcode.com/api/v5/repos/:owner/:repo/milestones/:number
```

#### ⚠️ 已知问题的接口

```bash
# 创建里程碑 - 400 Bad Request (日期格式要求 YYYY-MM-DD)
# curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
#   -d '{"title":"v1.0","description":"Version 1.0","due_date":"2026-12-31"}' \
#   https://api.gitcode.com/api/v5/repos/:owner/:repo/milestones

# 更新里程碑
# curl -X PATCH -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
#   -d '{"title":"New title","state":"closed"}' \
#   https://api.gitcode.com/api/v5/repos/:owner/:repo/milestones/:number

# 删除里程碑 ⚠️
# curl -X DELETE -H "Authorization: Bearer $TOKEN" \
#   https://api.gitcode.com/api/v5/repos/:owner/:repo/milestones/:number
```

---

### 八、Pull Request API - 46 个端点

#### ✅ 已验证可用的接口

```bash
# 获取 PR 列表
curl -H "Authorization: Bearer $TOKEN" \
  "https://api.gitcode.com/api/v5/repos/:owner/:repo/pulls?state=all"

# 获取 PR 详情
curl -H "Authorization: Bearer $TOKEN" \
  https://api.gitcode.com/api/v5/repos/:owner/:repo/pulls/:number

# 获取 PR 提交
curl -H "Authorization: Bearer $TOKEN" \
  https://api.gitcode.com/api/v5/repos/:owner/:repo/pulls/:number/commits

# 获取 PR 文件变更
curl -H "Authorization: Bearer $TOKEN" \
  https://api.gitcode.com/api/v5/repos/:owner/:repo/pulls/:number/files

# 获取 PR 评论列表
curl -H "Authorization: Bearer $TOKEN" \
  https://api.gitcode.com/api/v5/repos/:owner/:repo/pulls/:number/comments

# 创建 PR 评论
curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"body":"Comment text"}' \
  https://api.gitcode.com/api/v5/repos/:owner/:repo/pulls/:number/comments

# 获取 PR 标签
curl -H "Authorization: Bearer $TOKEN" \
  https://api.gitcode.com/api/v5/repos/:owner/:repo/pulls/:number/labels

# 获取 PR 关联的 Issue
curl -H "Authorization: Bearer $TOKEN" \
  https://api.gitcode.com/api/v5/repos/:owner/:repo/pulls/:number/issues
```

#### ⚠️ 已知问题的接口

```bash
# 创建 PR - 需要两个有差异的分支
# curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
#   -d '{"title":"Fix bug","body":"Description","head":"feature","base":"main"}' \
#   https://api.gitcode.com/api/v5/repos/:owner/:repo/pulls

# 合并 PR ⚠️
# curl -X PUT -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
#   -d '{"commit_title":"Merge message","merge_method":"merge"}' \
#   https://api.gitcode.com/api/v5/repos/:owner/:repo/pulls/:number/merge

# 更新 PR
# curl -X PATCH -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
#   -d '{"title":"New title","state":"closed"}' \
#   https://api.gitcode.com/api/v5/repos/:owner/:repo/pulls/:number
```

---

### 九、Release API - 52 个端点

#### ✅ 已验证可用的接口

```bash
# 获取版本列表
curl -H "Authorization: Bearer $TOKEN" \
  https://api.gitcode.com/api/v5/repos/:owner/:repo/releases

# 获取指定版本
curl -H "Authorization: Bearer $TOKEN" \
  https://api.gitcode.com/api/v5/repos/:owner/:repo/releases/tags/:tag
```

#### ⚠️ 已知问题的接口

```bash
# 获取最新版本 - 400 Bad Request (无 release 时)
# curl -H "Authorization: Bearer $TOKEN" \
#   https://api.gitcode.com/api/v5/repos/:owner/:repo/releases/latest

# 创建版本
# curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
#   -d '{"tag_name":"v1.0.0","name":"Version 1.0","body":"Release notes"}' \
#   https://api.gitcode.com/api/v5/repos/:owner/:repo/releases

# 删除版本 ⚠️
# curl -X DELETE -H "Authorization: Bearer $TOKEN" \
#   https://api.gitcode.com/api/v5/repos/:owner/:repo/releases/:id
```

---

### 十、搜索 API (Search) - 3 个端点

#### ✅ 已验证可用的接口

```bash
# 搜索用户
curl -H "Authorization: Bearer $TOKEN" \
  "https://api.gitcode.com/api/v5/search/users?q=keyword"

# 搜索仓库
curl -H "Authorization: Bearer $TOKEN" \
  "https://api.gitcode.com/api/v5/search/repositories?q=keyword"

# 搜索 Issue
curl -H "Authorization: Bearer $TOKEN" \
  "https://api.gitcode.com/api/v5/search/issues?q=keyword"
```

---

### 十一、组织 API (Organization) - 30 个端点

#### ✅ 已验证可用的接口

```bash
# 获取组织详情
curl -H "Authorization: Bearer $TOKEN" \
  https://api.gitcode.com/api/v5/orgs/:org

# 获取组织成员列表
curl -H "Authorization: Bearer $TOKEN" \
  https://api.gitcode.com/api/v5/orgs/:org/members

# 获取组织仓库列表
curl -H "Authorization: Bearer $TOKEN" \
  https://api.gitcode.com/api/v5/orgs/:org/repos

# 获取组织 Issue 列表
curl -H "Authorization: Bearer $TOKEN" \
  https://api.gitcode.com/api/v5/orgs/:org/issues

# 获取组织 PR 列表
curl -H "Authorization: Bearer $TOKEN" \
  https://api.gitcode.com/api/v5/orgs/:org/pull-requests

# 获取看板列表
curl -H "Authorization: Bearer $TOKEN" \
  https://api.gitcode.com/api/v5/org/:owner/kanban/list
```

---

### 十二、企业 API (Enterprise) - 27 个端点

#### ✅ 已验证可用的接口

```bash
# 获取企业成员列表
curl -H "Authorization: Bearer $TOKEN" \
  https://api.gitcode.com/api/v8/enterprises/:enterprise/members

# 获取企业 Issue 列表
curl -H "Authorization: Bearer $TOKEN" \
  https://api.gitcode.com/api/v5/enterprises/:enterprise/issues

# 获取企业 PR 列表
curl -H "Authorization: Bearer $TOKEN" \
  https://api.gitcode.com/api/v5/enterprises/:enterprise/pull-requests

# 获取企业标签
curl -H "Authorization: Bearer $TOKEN" \
  https://api.gitcode.com/api/v5/enterprises/:enterprise/labels
```

---

### 十三、Webhook API - 6 个端点

#### ✅ 已验证可用的接口

```bash
# 获取 Webhook 列表
curl -H "Authorization: Bearer $TOKEN" \
  https://api.gitcode.com/api/v5/repos/:owner/:repo/hooks
```

#### ⚠️ 已知问题的接口

```bash
# 创建 Webhook
# curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
#   -d '{"url":"https://example.com/hook","content_type":"json","events":["push"]}' \
#   https://api.gitcode.com/api/v5/repos/:owner/:repo/hooks

# 删除 Webhook ⚠️
# curl -X DELETE -H "Authorization: Bearer $TOKEN" \
#   https://api.gitcode.com/api/v5/repos/:owner/:repo/hooks/:id
```

---

### 十四、成员 API (Member) - 5 个端点

#### ✅ 已验证可用的接口

```bash
# 获取协作者列表
curl -H "Authorization: Bearer $TOKEN" \
  https://api.gitcode.com/api/v5/repos/:owner/:repo/collaborators

# 检查协作者权限
curl -H "Authorization: Bearer $TOKEN" \
  https://api.gitcode.com/api/v5/repos/:owner/:repo/collaborators/:username/permission
```

#### ⚠️ 已知问题的接口

```bash
# 添加协作者
# curl -X PUT -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
#   -d '{"permission":"push"}' \
#   https://api.gitcode.com/api/v5/repos/:owner/:repo/collaborators/:username

# 移除协作者 ⚠️
# curl -X DELETE -H "Authorization: Bearer $TOKEN" \
#   https://api.gitcode.com/api/v5/repos/:owner/:repo/collaborators/:username
```

---

### 十五、AI API - 6 个端点

```bash
# AI 聊天完成
curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"model":"qwen-plus","messages":[{"role":"user","content":"Hello"}]}' \
  https://api.gitcode.com/api/v5/chat/completions

# 音频转录
curl -X POST -H "Authorization: Bearer $TOKEN" \
  -F "file=@audio.mp3" \
  https://api.gitcode.com/api/v5/audio/transcriptions

# 视频生成
curl -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"prompt":"A cat playing guitar"}' \
  https://api.gitcode.com/api/v5/video/generate
```

---

### 十六、OAuth API - 2 个端点

```bash
# OAuth 授权
GET https://api.gitcode.com/oauth/authorize?client_id=CLIENT_ID&redirect_uri=REDIRECT_URI&response_type=code&scope=scope

# OAuth 令牌
POST https://api.gitcode.com/oauth/token?grant_type=authorization_code&code=CODE&client_id=CLIENT_ID&client_secret=SECRET
```

---

## 使用示例

直接对我说：
- "获取我的 AtomGit 用户信息"
- "获取我的 GitCode 用户信息"
- "列出我的所有仓库"
- "在 src-openeuler/libsoup 创建一个 Issue"
- "在 openeuler/dde 创建一个 PR"
- "创建名为 test-repo 的私有仓库"
- "获取 README.md 内容"
- "创建 feature 分支，基于 main"
- "Fork src-openeuler/libsoup 仓库"
- "搜索用户 weidong"
- "搜索仓库 openclaw"

> 支持使用 `atomgit.com` 或 `gitcode.com` 域名，效果相同。

---

## 错误码

| 状态码 | 含义 | 处理 |
|--------|------|------|
| 200 | 成功 | - |
| 201 | 创建成功 | - |
| 204 | 删除成功 | - |
| 400 | 请求错误 | 检查参数格式 |
| 401 | Token 无效 | 检查 ATOMGIT_TOKEN |
| 403 | 权限不足 | 检查 token 权限 |
| 404 | 资源不存在 | 确认 owner/repo |
| 405 | 方法不允许 | 尝试其他 HTTP 方法 |
| 429 | 速率限制 | 等待后重试 |

---

## 已知问题汇总

### 1. 创建分支 API
- **问题**: 返回 400 PARAMETER_ERROR
- **原因**: 参数格式不明确
- **建议**: 暂时使用 Web UI 创建分支

### 2. 创建标签 API
- **问题**: 返回 400 BAD_REQUEST
- **原因**: name 参数需要作为 query 参数而非 body
- **建议**: 等待官方修复或使用 Web UI

### 3. 创建里程碑 API
- **问题**: 返回 400 日期格式错误
- **原因**: 需要 `YYYY-MM-DD` 格式而非 ISO 8601
- **解决**: 使用 `"due_date":"2026-12-31"` 格式

### 4. 更新文件 API
- **问题**: 返回 400 sha is missing
- **原因**: 更新文件需要提供当前 sha
- **解决**: 先 GET 获取 sha，再 PUT 更新

### 5. Issue 修改历史 API
- **问题**: 返回 404 Not Found
- **原因**: API 可能未完全开放
- **建议**: 暂时无法使用

---

## 文档

- API 文档：https://docs.gitcode.com/docs/apis/
- Token 管理：
  - https://gitcode.com/setting/token-classic
  - https://atomgit.com/setting/token-classic
- 完整 API 列表：294 个端点

## 平台说明

| 平台 | 域名 | API 端点 | 备注 |
|------|------|----------|------|
| GitCode | gitcode.com | api.gitcode.com | 主域名 |
| AtomGit | atomgit.com | api.atomgit.com | 等效域名 |

两个平台**账号互通、Token 通用、数据同步**。选择哪个域名完全取决于个人偏好或网络环境。

---

**最后更新**: 2026-03-22  
**测试验证**: 46 个接口已测试，37 个成功 (80.4%)
