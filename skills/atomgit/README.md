# AtomGit (GitCode) Skill

> **ClawHub Package**: [atomgit](https://clawhub.com/skills/atomgit)  
> **Version**: 1.0.0  
> **Author**: OpenClaw Community

[English](#english) | [中文](#中文)

---

# English

## Overview

AtomGit is an OpenClaw skill that provides comprehensive GitCode/Gitee-like repository management capabilities through the MCP (Model Context Protocol) interface. It enables AI agents to interact with GitCode repositories programmatically.

## Features

- 👤 **User Management**: Get current user info, query user details
- 📦 **Repository Management**: List, create, update, delete repositories
- 🐛 **Issue Tracking**: Create, query, update issues
- 🔀 **Pull Requests**: Create, review, merge pull requests
- 📁 **File Operations**: Read, create, update repository files
- 🌿 **Branch Management**: List, create, delete branches
- 🍴 **Fork Management**: Fork repositories, view fork lists

## Installation

### Method 1: Via ClawHub (Recommended)

```bash
# Install the skill
clawhub install atomgit

# Or install from a specific author
clawhub install weidongkl/atomgit
```

### Method 2: Manual Installation

Copy the skill to your OpenClaw skills directory:

```bash
# Copy to skills directory
cp -r ~/.openclaw/extensions/wecom-openclaw-plugin/skills/atomgit ~/.openclaw/skills/atomgit
```

## Quick Start

### Step 1: Get GitCode Token

1. Visit https://gitcode.com/setting/token-classic
2. Click "Generate New Token"
3. Select required permissions:
   - `api` - API access
   - `read_user` - Read user information
   - `read_repository` - Read repositories
   - `write_repository` - Write repositories (create, update, delete)
   - `issues` - Manage issues
   - `pull_requests` - Manage pull requests
4. Click generate and copy the token (**shown only once!**)

### Step 2: Configure Gateway

Edit your Gateway configuration file (usually `~/.openclaw/openclaw.json`):

```json
{
  "mcpConfig": {
    "atomgit": {
      "command": "node",
      "args": ["/root/.openclaw/extensions/wecom-openclaw-plugin/skills/atomgit/mcp-server.js"],
      "env": {
        "ATOMGIT_TOKEN": "your-personal-access-token-here"
      }
    }
  }
}
```

**Security Tip**: Use environment variables instead of hardcoding the token:

```bash
# Add to ~/.bashrc or ~/.zshrc
export ATOMGIT_TOKEN="your-token-here"
```

Then omit the env section in config:

```json
{
  "mcpConfig": {
    "atomgit": {
      "command": "node",
      "args": ["/root/.openclaw/extensions/wecom-openclaw-plugin/skills/atomgit/mcp-server.js"]
    }
  }
}
```

### Step 3: Restart Gateway

```bash
openclaw gateway restart
```

### Step 4: Verify Configuration

```bash
# Test MCP server directly
cd /root/.openclaw/extensions/wecom-openclaw-plugin/skills/atomgit
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"getCurrentUser","arguments":{}}}' | ATOMGIT_TOKEN=your-token timeout 3 node mcp-server.js
```

## Available Tools

### User Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `getCurrentUser` | Get current authenticated user info | None |
| `getUser` | Get specified user details | `username` (string, required) |

### Repository Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `listRepos` | List user or organization repos | `username`, `type`, `sort`, `direction`, `page`, `perPage` |
| `getRepo` | Get repository details | `owner` (string, required), `repo` (string, required) |
| `createRepo` | Create new repository | `name` (required), `description`, `private`, `autoInit`, `license`, `readme` |
| `updateRepo` | Update repository info | `owner`, `repo`, `name`, `description`, `private`, `hasIssues`, `hasWiki`, `defaultBranch` |
| `deleteRepo` | Delete repository | `owner`, `repo` |

### Issue Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `listIssues` | List repository issues | `owner`, `repo`, `state`, `labels`, `sort`, `direction`, `page`, `perPage` |
| `getIssue` | Get issue details | `owner`, `repo`, `number` (required) |
| `createIssue` | Create new issue | `owner`, `repo`, `title` (required), `body`, `assignee`, `labels` |
| `updateIssue` | Update issue | `owner`, `repo`, `number`, `title`, `body`, `state`, `assignee`, `labels` |

### Pull Request Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `listPullRequests` | List pull requests | `owner`, `repo`, `state`, `sort`, `direction`, `page`, `perPage` |
| `getPullRequest` | Get PR details | `owner`, `repo`, `number` (required) |
| `createPullRequest` | Create new PR | `owner`, `repo`, `title` (required), `body`, `head` (required), `base` (required), `maintainerCanModify` |
| `mergePullRequest` | Merge PR | `owner`, `repo`, `number`, `commitTitle`, `commitMessage`, `mergeMethod` (merge/rebase/squash) |

### File & Branch Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `getRepoFile` | Get file content | `owner`, `repo`, `path` (required), `ref` (branch/tag) |
| `createFile` | Create/update file | `owner`, `repo`, `path`, `content` (required), `message` (required), `branch`, `sha` |
| `listBranches` | List branches | `owner`, `repo`, `page`, `perPage` |
| `createBranch` | Create branch | `owner`, `repo`, `branch` (required), `ref` (source branch) |
| `deleteBranch` | Delete branch | `owner`, `repo`, `branch` |

### Fork Tools

| Tool | Description | Parameters |
|------|-------------|------------|
| `forkRepo` | Fork a repository | `owner`, `repo`, `organization` (optional) |
| `listForks` | List repository forks | `owner`, `repo`, `sort`, `page`, `perPage` |

## Usage Examples

### Example 1: Get Current User Info

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"getCurrentUser","arguments":{}}}' | ATOMGIT_TOKEN=your-token node mcp-server.js
```

**Response:**
```json
{
  "content": [{
    "type": "text",
    "text": "{\"success\":true,\"data\":{\"login\":\"weidongkl\",\"name\":\"wei dong\",\"email\":\"weidongkx@gmail.com\"}}"
  }]
}
```

### Example 2: List My Repositories

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"listRepos","arguments":{"perPage":5}}}' | ATOMGIT_TOKEN=your-token node mcp-server.js
```

### Example 3: Create New Repository

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"createRepo","arguments":{"name":"my-project","description":"My awesome project","private":false,"autoInit":true}}}' | ATOMGIT_TOKEN=your-token node mcp-server.js
```

### Example 4: Create Issue

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"createIssue","arguments":{"owner":"weidongkl","repo":"my-project","title":"Bug report","body":"Found a critical bug","labels":"bug,high-priority"}}}' | ATOMGIT_TOKEN=your-token node mcp-server.js
```

### Example 5: Create Pull Request

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"createPullRequest","arguments":{"owner":"weidongkl","repo":"my-project","title":"Fix bug #1","body":"This PR fixes issue #1","head":"fix-bug-1","base":"main"}}}' | ATOMGIT_TOKEN=your-token node mcp-server.js
```

### Example 6: Update File

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"createFile","arguments":{"owner":"weidongkl","repo":"my-project","path":"README.md","content":"# My Project\n\nThis is awesome!","message":"Update README","branch":"main"}}}' | ATOMGIT_TOKEN=your-token node mcp-server.js
```

### Example 7: Fork Repository

```bash
# Fork to your account
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"forkRepo","arguments":{"owner":"openeuler","repo":"community"}}}' | ATOMGIT_TOKEN=your-token node mcp-server.js

# Fork to organization
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"forkRepo","arguments":{"owner":"openeuler","repo":"community","organization":"my-org"}}}' | ATOMGIT_TOKEN=your-token node mcp-server.js
```

## Troubleshooting

### Error: 401 Unauthorized

**Cause**: Invalid or expired token

**Solution**:
1. Check if `ATOMGIT_TOKEN` is set correctly
2. Regenerate token and update configuration
3. Verify token has required permissions

### Error: 404 Not Found

**Cause**: Resource doesn't exist or no access permission

**Solution**:
1. Verify owner/repo name is correct
2. Check token has read access to private repositories

### Error: 403 Forbidden

**Cause**: Insufficient permissions

**Solution**:
1. Check token has required permissions for the operation
2. Write operations require `write_repository` permission

### Error: 429 Too Many Requests

**Cause**: API rate limit exceeded

**Solution**:
- GitCode API limits: 50 requests/minute, 4000 requests/hour
- Wait and retry later
- Implement request throttling

## API Reference

- GitCode API Docs: https://docs.gitcode.com/docs/apis/
- Base URL: https://api.gitcode.com/api/v5
- Personal Token Management: https://gitcode.com/setting/token-classic

## Changelog

### v1.0.0

- Initial release
- User management (get current user, query user)
- Repository management (list, create, update, delete)
- Issue management (list, create, get, update)
- Pull Request management (list, create, get, merge)
- File operations (get content, create/update)
- Branch management (list, create, delete)
- Fork operations (fork repo, list forks)

---

# 中文

## 概述

AtomGit 是一个 OpenClaw 技能，通过 MCP（Model Context Protocol）接口提供全面的 GitCode/Gitee 类仓库管理能力。它使 AI 代理能够以编程方式与 GitCode 仓库交互。

## 功能特性

- 👤 **用户管理**: 获取当前用户信息、查询用户详情
- 📦 **仓库管理**: 列出、创建、更新、删除仓库
- 🐛 **Issue 跟踪**: 创建、查询、更新 Issue
- 🔀 **Pull Request**: 创建、审查、合并 PR
- 📁 **文件操作**: 读取、创建、更新仓库文件
- 🌿 **分支管理**: 列出、创建、删除分支
- 🍴 **Fork 管理**: Fork 仓库、查看 Fork 列表

## 安装方式

### 方式 1: 通过 ClawHub 安装（推荐）

```bash
# 安装技能
clawhub install atomgit

# 或从特定作者安装
clawhub install weidongkl/atomgit
```

### 方式 2: 手动安装

将技能复制到 OpenClaw skills 目录：

```bash
# 复制到 skills 目录
cp -r ~/.openclaw/extensions/wecom-openclaw-plugin/skills/atomgit ~/.openclaw/skills/atomgit
```

## 快速开始

### 步骤 1: 获取 GitCode Token

1. 访问 https://gitcode.com/setting/token-classic
2. 点击"生成新令牌"
3. 勾选需要的权限：
   - `api` - API 访问
   - `read_user` - 读取用户信息
   - `read_repository` - 读取仓库
   - `write_repository` - 写入仓库（创建、更新、删除）
   - `issues` - 管理 Issue
   - `pull_requests` - 管理 PR
4. 点击生成，复制令牌（**只显示一次！**）

### 步骤 2: 配置 Gateway

编辑 Gateway 配置文件（通常是 `~/.openclaw/openclaw.json`）：

```json
{
  "mcpConfig": {
    "atomgit": {
      "command": "node",
      "args": ["/root/.openclaw/extensions/wecom-openclaw-plugin/skills/atomgit/mcp-server.js"],
      "env": {
        "ATOMGIT_TOKEN": "your-personal-access-token-here"
      }
    }
  }
}
```

**安全提示**: 建议使用环境变量而不是硬编码 token：

```bash
# 在 ~/.bashrc 或 ~/.zshrc 中添加
export ATOMGIT_TOKEN="your-token-here"
```

然后配置中省略 env 部分：

```json
{
  "mcpConfig": {
    "atomgit": {
      "command": "node",
      "args": ["/root/.openclaw/extensions/wecom-openclaw-plugin/skills/atomgit/mcp-server.js"]
    }
  }
}
```

### 步骤 3: 重启 Gateway

```bash
openclaw gateway restart
```

### 步骤 4: 验证配置

```bash
# 直接测试 MCP 服务器
cd /root/.openclaw/extensions/wecom-openclaw-plugin/skills/atomgit
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"getCurrentUser","arguments":{}}}' | ATOMGIT_TOKEN=your-token timeout 3 node mcp-server.js
```

## 可用工具

### 用户工具

| 工具 | 描述 | 参数 |
|------|------|------|
| `getCurrentUser` | 获取当前认证用户信息 | 无 |
| `getUser` | 获取指定用户详情 | `username` (字符串，必填) |

### 仓库工具

| 工具 | 描述 | 参数 |
|------|------|------|
| `listRepos` | 列出用户或组织仓库 | `username`, `type`, `sort`, `direction`, `page`, `perPage` |
| `getRepo` | 获取仓库详情 | `owner` (字符串，必填), `repo` (字符串，必填) |
| `createRepo` | 创建新仓库 | `name` (必填), `description`, `private`, `autoInit`, `license`, `readme` |
| `updateRepo` | 更新仓库信息 | `owner`, `repo`, `name`, `description`, `private`, `hasIssues`, `hasWiki`, `defaultBranch` |
| `deleteRepo` | 删除仓库 | `owner`, `repo` |

### Issue 工具

| 工具 | 描述 | 参数 |
|------|------|------|
| `listIssues` | 列出仓库 Issue | `owner`, `repo`, `state`, `labels`, `sort`, `direction`, `page`, `perPage` |
| `getIssue` | 获取 Issue 详情 | `owner`, `repo`, `number` (必填) |
| `createIssue` | 创建新 Issue | `owner`, `repo`, `title` (必填), `body`, `assignee`, `labels` |
| `updateIssue` | 更新 Issue | `owner`, `repo`, `number`, `title`, `body`, `state`, `assignee`, `labels` |

### Pull Request 工具

| 工具 | 描述 | 参数 |
|------|------|------|
| `listPullRequests` | 列出 Pull Requests | `owner`, `repo`, `state`, `sort`, `direction`, `page`, `perPage` |
| `getPullRequest` | 获取 PR 详情 | `owner`, `repo`, `number` (必填) |
| `createPullRequest` | 创建 PR | `owner`, `repo`, `title` (必填), `body`, `head` (必填), `base` (必填), `maintainerCanModify` |
| `mergePullRequest` | 合并 PR | `owner`, `repo`, `number`, `commitTitle`, `commitMessage`, `mergeMethod` (merge/rebase/squash) |

### 文件与分支工具

| 工具 | 描述 | 参数 |
|------|------|------|
| `getRepoFile` | 获取文件内容 | `owner`, `repo`, `path` (必填), `ref` (分支/标签) |
| `createFile` | 创建/更新文件 | `owner`, `repo`, `path`, `content` (必填), `message` (必填), `branch`, `sha` |
| `listBranches` | 列出分支 | `owner`, `repo`, `page`, `perPage` |
| `createBranch` | 创建分支 | `owner`, `repo`, `branch` (必填), `ref` (源分支) |
| `deleteBranch` | 删除分支 | `owner`, `repo`, `branch` |

### Fork 工具

| 工具 | 描述 | 参数 |
|------|------|------|
| `forkRepo` | Fork 一个仓库 | `owner`, `repo`, `organization` (可选) |
| `listForks` | 列出仓库的 Forks | `owner`, `repo`, `sort`, `page`, `perPage` |

## 使用示例

### 示例 1: 获取当前用户信息

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"getCurrentUser","arguments":{}}}' | ATOMGIT_TOKEN=your-token node mcp-server.js
```

**响应:**
```json
{
  "content": [{
    "type": "text",
    "text": "{\"success\":true,\"data\":{\"login\":\"weidongkl\",\"name\":\"wei dong\",\"email\":\"weidongkx@gmail.com\"}}"
  }]
}
```

### 示例 2: 列出我的仓库

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"listRepos","arguments":{"perPage":5}}}' | ATOMGIT_TOKEN=your-token node mcp-server.js
```

### 示例 3: 创建新仓库

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"createRepo","arguments":{"name":"my-project","description":"My awesome project","private":false,"autoInit":true}}}' | ATOMGIT_TOKEN=your-token node mcp-server.js
```

### 示例 4: 创建 Issue

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"createIssue","arguments":{"owner":"weidongkl","repo":"my-project","title":"Bug 报告","body":"发现一个严重 bug","labels":"bug,high-priority"}}}' | ATOMGIT_TOKEN=your-token node mcp-server.js
```

### 示例 5: 创建 Pull Request

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"createPullRequest","arguments":{"owner":"weidongkl","repo":"my-project","title":"修复 bug #1","body":"此 PR 修复 issue #1","head":"fix-bug-1","base":"main"}}}' | ATOMGIT_TOKEN=your-token node mcp-server.js
```

### 示例 6: 更新文件

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"createFile","arguments":{"owner":"weidongkl","repo":"my-project","path":"README.md","content":"# 我的项目\n\n太棒了！","message":"更新 README","branch":"main"}}}' | ATOMGIT_TOKEN=your-token node mcp-server.js
```

### 示例 7: Fork 仓库

```bash
# Fork 到自己的账户
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"forkRepo","arguments":{"owner":"openeuler","repo":"community"}}}' | ATOMGIT_TOKEN=your-token node mcp-server.js

# Fork 到组织
echo '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"forkRepo","arguments":{"owner":"openeuler","repo":"community","organization":"my-org"}}}' | ATOMGIT_TOKEN=your-token node mcp-server.js
```

## 故障排查

### 错误：401 Unauthorized

**原因**: Token 无效或过期

**解决方法**:
1. 检查 `ATOMGIT_TOKEN` 是否正确设置
2. 重新生成 token 并更新配置
3. 确认 token 有所需的权限

### 错误：404 Not Found

**原因**: 资源不存在或无权限访问

**解决方法**:
1. 确认 owner/repo 名称正确
2. 确认 token 有读取私有仓库的权限

### 错误：403 Forbidden

**原因**: 权限不足

**解决方法**:
1. 检查 token 是否有对应操作的权限
2. 写操作需要 `write_repository` 权限

### 错误：429 Too Many Requests

**原因**: 超过 API 速率限制

**解决方法**:
- GitCode API 限制：50 次/分钟，4000 次/小时
- 等待一段时间后重试
- 实现请求节流

## API 参考

- GitCode API 文档：https://docs.gitcode.com/docs/apis/
- 基础 URL：https://api.gitcode.com/api/v5
- 个人令牌管理：https://gitcode.com/setting/token-classic

## 更新日志

### v1.0.0

- 初始发布
- 支持用户管理（获取当前用户、查询用户）
- 支持仓库管理（列表、创建、更新、删除）
- 支持 Issue 管理（列表、创建、获取、更新）
- 支持 Pull Request 管理（列表、创建、获取、合并）
- 支持文件操作（获取内容、创建/更新）
- 支持分支管理（列表、创建、删除）
- 支持 Fork 操作（Fork 仓库、查看 Forks 列表）

## 许可证

MIT License
