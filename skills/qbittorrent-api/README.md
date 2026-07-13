# qBittorrent API Skill

一个用于 Claude Code 的 skill，提供 qBittorrent Web API 的完整参考文档和常用操作模式。

## 功能

- **完整的 API 端点速查表** - 涵盖认证、种子管理、文件管理、分类标签、RSS、搜索等所有模块
- **常用操作示例** - curl 命令示例，可直接复制使用
- **工作流指南** - 添加种子时的最佳实践（查询路径 → 询问用户 → 添加）
- **错误排查** - 常见问题和解决方案

## 安装

### 方法 1: 复制到 Claude Code skills 目录

```bash
# 克隆或下载此仓库
git clone https://github.com/your-username/pub-skills.git

# 复制 skill 到 Claude Code 的 skills 目录
cp -r pub-skills/skills/qbittorrent-api ~/.claude/skills/
```

### 方法 2: 直接使用

将此仓库作为你的 skills 目录的一部分：

```bash
# 在 ~/.claude/settings.json 中配置 skills 路径
{
  "skillDirectories": [
    "~/.claude/skills",
    "/path/to/pub-skills/skills"
  ]
}
```

## 配置

在项目根目录创建 `.env` 文件：

```bash
# .env 文件格式
QB_URL="http://192.168.31.88:8080"
QB_USER="admin"
QB_PASS="your_password"
```

> **注意**: `.env` 文件包含敏感信息，请确保已添加到 `.gitignore`

## 使用示例

在 Claude Code 中，直接描述你的需求即可触发此 skill：

```
# 添加种子
帮我添加这个 magnet 链接到 qBittorrent: magnet:?xt=urn:btih:xxxx

# 查看下载状态
查看当前正在下载的种子

# 管理种子
暂停所有下载中的种子

# 分类管理
创建一个名为 "movies" 的分类，保存路径为 /downloads/movies
```

## API 覆盖范围

| 模块 | 端点数量 |
|------|----------|
| 认证 | 2 |
| 种子管理 | 15+ |
| 文件管理 | 4 |
| 速度限制 | 5 |
| 分类/标签 | 8 |
| Tracker 管理 | 4 |
| RSS | 10 |
| 搜索 | 10 |
| 应用/日志/同步 | 10+ |

## 参考资料

- [qBittorrent OpenAPI 文档](https://www.qbittorrent.org/openapi-demo/)
- [WebUI API Wiki](https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1))
- [API Changelog](https://github.com/qbittorrent/qBittorrent/blob/master/WebAPI_Changelog.md)

## License

MIT
