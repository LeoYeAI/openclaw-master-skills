# Digital Life Import - 数据源导入指南

## 概述

Digital Life Import 是 OpenClaw Diary 的核心功能，支持从多种数据源导入用户的数字生活数据，统一转换为 AI Memory。

## 支持的数据源

| 数据源 | MCP 服务器 | 授权方式 | 状态 |
|--------|-----------|----------|------|
| OpenClaw Memory | 无（本地文件） | 无需授权 | ✅ 可用 |
| Obsidian | [mcp-obsidian](https://github.com/smithery-ai/mcp-obsidian) | Vault 路径 | ✅ 可用 |
| Notion | [notion-mcp](https://developers.notion.com/docs/mcp) | Integration Token | ✅ 可用 |
| Gmail | [google-workspace-mcp](https://github.com/taylorwilsdon/google_workspace_mcp) | OAuth | ✅ 可用 |
| Google Docs | google-workspace-mcp | OAuth | ✅ 可用 |
| Google Drive | google-workspace-mcp | OAuth | ✅ 可用 |
| 飞书 | feishu-mcp | App ID + Secret | ✅ 可用 |
| Slack | [slack-mcp](https://lobehub.com/mcp/atlasfutures-claude-mcp-slack) | Bot Token | ✅ 可用 |
| Dropbox | [dbx-mcp-server](https://github.com/amgadabdelhafez/dbx-mcp-server) | OAuth | ✅ 可用 |
| GitHub | 原生支持 | Token | ✅ 可用 |
| X/Twitter | [twitter-mcp](https://github.com/EnesCinr/twitter-mcp) | API Key | ✅ 可用 |
| RSS | [mcp-rss-aggregator](https://github.com/imprvhub/mcp-rss-aggregator) | 无需授权 | ✅ 可用 |

## MCP 服务器配置

### Google Workspace MCP

支持 Gmail、Google Docs、Google Drive、Google Calendar。

**安装**：
```bash
npm install -g @anthropic/google-workspace-mcp
```

**配置** (`~/.claude/mcp_servers.json`)：
```json
{
  "google-workspace": {
    "command": "google-workspace-mcp",
    "env": {
      "GOOGLE_CLIENT_ID": "your_client_id",
      "GOOGLE_CLIENT_SECRET": "your_client_secret"
    }
  }
}
```

**获取凭证**：
1. 访问 [Google Cloud Console](https://console.cloud.google.com/)
2. 创建项目并启用 Gmail API、Drive API、Docs API
3. 创建 OAuth 2.0 凭证
4. 下载凭证并配置环境变量

### Notion MCP

**安装**：
```bash
npm install -g @notionhq/notion-mcp
```

**配置**：
```json
{
  "notion": {
    "command": "notion-mcp",
    "env": {
      "NOTION_TOKEN": "your_integration_token"
    }
  }
}
```

**获取 Token**：
1. 访问 [Notion Integrations](https://www.notion.so/my-integrations)
2. 创建新的 Integration
3. 复制 Internal Integration Token
4. 在 Notion 中分享页面给这个 Integration

### Obsidian MCP

**安装**：
```bash
npm install -g mcp-obsidian
```

**配置**：
```json
{
  "obsidian": {
    "command": "mcp-obsidian",
    "args": ["--vault", "/path/to/your/vault"]
  }
}
```

### Slack MCP

**安装**：
```bash
npm install -g @anthropic/slack-mcp
```

**配置**：
```json
{
  "slack": {
    "command": "slack-mcp",
    "env": {
      "SLACK_BOT_TOKEN": "xoxb-your-bot-token"
    }
  }
}
```

**获取 Bot Token**：
1. 访问 [Slack API](https://api.slack.com/apps)
2. 创建新应用
3. 添加 Bot Token Scopes
4. 安装到工作区
5. 复制 Bot User OAuth Token

### Twitter/X MCP

**安装**：
```bash
npm install -g twitter-mcp
```

**配置**：
```json
{
  "twitter": {
    "command": "twitter-mcp",
    "env": {
      "TWITTER_API_KEY": "your_api_key",
      "TWITTER_API_SECRET": "your_api_secret",
      "TWITTER_ACCESS_TOKEN": "your_access_token",
      "TWITTER_ACCESS_SECRET": "your_access_secret"
    }
  }
}
```

### Dropbox MCP

**安装**：
```bash
npm install -g dbx-mcp-server
```

**配置**：
```json
{
  "dropbox": {
    "command": "dbx-mcp-server",
    "env": {
      "DROPBOX_ACCESS_TOKEN": "your_access_token"
    }
  }
}
```

### RSS MCP

**安装**：
```bash
npm install -g mcp-rss-aggregator
```

**配置**：
```json
{
  "rss": {
    "command": "mcp-rss-aggregator",
    "args": ["--config", "~/.config/rss-feeds.json"]
  }
}
```

## 导入流程

### 1. 自动检测

系统会自动检测已配置的数据源：

```python
def detect_sources():
    """检测可用的数据源"""
    sources = {}

    # OpenClaw Memory（本地文件）
    if glob.glob(os.path.expanduser("~/.claude/projects/*/memory/*.md")):
        sources["openclaw_memory"] = {"status": "available", "auth": False}

    # Obsidian
    obsidian_paths = [
        "~/Documents/Obsidian",
        "~/Obsidian",
        "~/.obsidian"
    ]
    for path in obsidian_paths:
        if os.path.exists(os.path.expanduser(path)):
            sources["obsidian"] = {"status": "available", "path": path}
            break

    # 检测 MCP 服务器配置
    mcp_config = load_mcp_config()

    if "google-workspace" in mcp_config:
        sources["gmail"] = {"status": "available", "auth": True}
        sources["google_docs"] = {"status": "available", "auth": True}
        sources["google_drive"] = {"status": "available", "auth": True}

    if "notion" in mcp_config:
        sources["notion"] = {"status": "available", "auth": True}

    # ... 其他数据源

    return sources
```

### 2. 用户选择

根据检测结果，向用户展示可用的数据源并让其选择。

### 3. 授权收集

对于需要授权的数据源，智能合并授权请求：
- Google 系列（Gmail + Docs + Drive）共用一个 OAuth
- 如果导入和存储使用同一平台，只需授权一次

### 4. 执行导入

使用统一的 `importSource(source)` 接口执行导入。

### 5. 数据转换

所有数据经过 Memory Pipeline 处理：
```
source data → markdown → memory chunk → memory graph
```

## 输出目录结构

```
~/write_me/01studio/me/
├── identity/
│   ├── identity.md
│   └── preferences.md
├── auth/
│   └── *.json
├── imports/
│   ├── openclaw-memory/
│   ├── obsidian/
│   ├── notion/
│   ├── gmail/
│   ├── google-docs/
│   ├── google-drive/
│   ├── feishu/
│   ├── slack/
│   ├── dropbox/
│   ├── github/
│   ├── twitter/
│   └── rss/
└── memory/
    ├── knowledge/
    ├── contacts/
    ├── writing/
    └── projects/
```

## 命令行接口

```bash
# 显示导入向导
/import-data

# 导入特定数据源
/import-data github
/import-data notion
/import-data gmail

# 导入所有已配置的数据源
/import-data --all

# 刷新已导入的数据
/import-data --refresh

# 查看导入状态
/import-data --status
```

## 错误处理

### 授权失败

```
❌ {平台} 授权失败

可能的原因：
1. Token/API Key 不正确
2. 权限不足
3. Token 已过期

解决方案：
- 检查环境变量配置
- 重新获取授权凭证
- 确认应用权限设置
```

### MCP 服务器未安装

```
❌ {平台} MCP 服务器未安装

安装命令：
npm install -g {mcp-package-name}

配置说明：
{配置示例}
```

### 网络问题

```
❌ 网络连接失败

建议：
- 检查网络连接
- 检查代理设置
- 稍后重试
```

## 最佳实践

1. **渐进式导入**：先导入最重要的数据源，逐步添加其他来源
2. **定期刷新**：使用 `--refresh` 保持数据同步
3. **隐私保护**：敏感数据保存在本地，不上传云端
4. **备份**：定期备份 `~/write_me/01studio/me/` 目录

---

最后更新：2026-03-15
