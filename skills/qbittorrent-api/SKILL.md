---
name: qbittorrent-api
description: Use when working with qBittorrent Web API - adding torrents, managing downloads, checking status, or any qBittorrent automation task. Includes curl examples and common patterns.
---

# qBittorrent Web API

## 配置信息

**优先级顺序**：
1. 项目目录的 `.env` 文件（默认）
2. 项目 `CLAUDE.md` 文件
3. 询问用户提供

```bash
# .env 文件格式
QB_URL="http://192.168.31.88:8080"
QB_USER="admin"
QB_PASS="123123"
```

> **注意**: 执行任何 API 操作前，先检查 `.env` 文件是否存在并包含配置。如果缺少配置，询问用户。

## 认证

qBittorrent 使用 **cookie-based 认证**：

```bash
# 配置（从 .env 读取）
source .env 2>/dev/null || true
COOKIE_FILE="/tmp/qb_cookies.txt"

# 登录并保存 cookie
curl -c "$COOKIE_FILE" -b "$COOKIE_FILE" \
  -H "Referer: $QB_URL" \
  -d "username=$QB_USER&password=$QB_PASS" \
  "$QB_URL/api/v2/auth/login"

# 登出
curl -c "$COOKIE_FILE" -b "$COOKIE_FILE" \
  "$QB_URL/api/v2/auth/logout"
```

**重要**: 登录请求需要 `Referer` header。

---

## API 端点速查

### 认证 `/api/v2/auth`

| 操作 | 端点 | 方法 | 参数 |
|------|------|------|------|
| 登录 | `/login` | POST | `username`, `password` |
| 登出 | `/logout` | POST | - |

### 种子管理 `/api/v2/torrents`

| 操作 | 端点 | 方法 | 参数 |
|------|------|------|------|
| 种子列表 | `/info` | GET | `filter`, `hashes`, `category`, `tag` |
| 种子数量 | `/count` | GET | `filter` |
| 种子详情 | `/properties` | GET | `hash` |
| 添加种子 | `/add` | POST | `urls`, `savepath`, `category`, `tags` |
| 删除种子 | `/delete` | POST | `hashes`, `deleteFiles` |
| 开始 | `/start` | POST | `hashes` |
| 停止 | `/stop` | POST | `hashes` |
| 重新检查 | `/recheck` | POST | `hashes` |
| 重新宣告 | `/reannounce` | POST | `hashes` |
| 重命名 | `/rename` | POST | `hash`, `name` |
| 设置注释 | `/setComment` | POST | `hashes`, `comment` |

### 文件管理 `/api/v2/torrents`

| 操作 | 端点 | 方法 | 参数 |
|------|------|------|------|
| 文件列表 | `/files` | GET | `hash` |
| 文件优先级 | `/filePrio` | POST | `hash`, `id`, `priority` |
| 重命名文件 | `/renameFile` | POST | `hash`, `oldPath`, `newPath` |
| 重命名文件夹 | `/renameFolder` | POST | `hash`, `oldPath`, `newPath` |

### 速度限制 `/api/v2/torrents`

| 操作 | 端点 | 方法 | 参数 |
|------|------|------|------|
| 获取下载限速 | `/downloadLimit` | GET | `hashes` |
| 获取上传限速 | `/uploadLimit` | GET | `hashes` |
| 设置下载限速 | `/setDownloadLimit` | POST | `hashes`, `limit` |
| 设置上传限速 | `/setUploadLimit` | POST | `hashes`, `limit` |
| 设置分享限制 | `/setShareLimits` | POST | `hashes`, `ratioLimit`, `seedingTimeLimit` |

### 优先级 `/api/v2/torrents`

| 操作 | 端点 | 方法 | 参数 |
|------|------|------|------|
| 提高优先级 | `/increasePrio` | POST | `hashes` |
| 降低优先级 | `/decreasePrio` | POST | `hashes` |
| 最高优先级 | `/topPrio` | POST | `hashes` |
| 最低优先级 | `/bottomPrio` | POST | `hashes` |

### 路径管理 `/api/v2/torrents`

| 操作 | 端点 | 方法 | 参数 |
|------|------|------|------|
| 设置保存路径 | `/setLocation` | POST | `hashes`, `location` |
| 设置保存目录 | `/setSavePath` | POST | `hashes`, `path` |
| 设置下载目录 | `/setDownloadPath` | POST | `hashes`, `path` |

### 分类管理 `/api/v2/torrents`

| 操作 | 端点 | 方法 | 参数 |
|------|------|------|------|
| 获取分类 | `/categories` | GET | - |
| 创建分类 | `/createCategory` | POST | `category`, `savePath` |
| 编辑分类 | `/editCategory` | POST | `category`, `savePath` |
| 删除分类 | `/removeCategories` | POST | `categories` |
| 设置分类 | `/setCategory` | POST | `hashes`, `category` |

### 标签管理 `/api/v2/torrents`

| 操作 | 端点 | 方法 | 参数 |
|------|------|------|------|
| 获取标签 | `/tags` | GET | - |
| 创建标签 | `/createTags` | POST | `tags` |
| 删除标签 | `/deleteTags` | POST | `tags` |
| 添加标签 | `/addTags` | POST | `hashes`, `tags` |
| 设置标签 | `/setTags` | POST | `hashes`, `tags` |
| 移除标签 | `/removeTags` | POST | `hashes`, `tags` |

### Tracker 管理 `/api/v2/torrents`

| 操作 | 端点 | 方法 | 参数 |
|------|------|------|------|
| 获取 Trackers | `/trackers` | GET | `hash` |
| 添加 Trackers | `/addTrackers` | POST | `hash`, `urls` |
| 编辑 Tracker | `/editTracker` | POST | `hash`, `origUrl`, `newUrl` |
| 删除 Trackers | `/removeTrackers` | POST | `hash`, `urls` |

### Web Seeds 管理 `/api/v2/torrents`

| 操作 | 端点 | 方法 | 参数 |
|------|------|------|------|
| 获取 Web Seeds | `/webseeds` | GET | `hash` |
| 添加 Web Seeds | `/addWebSeeds` | POST | `hash`, `urls` |
| 编辑 Web Seed | `/editWebSeed` | POST | `hash`, `origUrl`, `newUrl` |
| 删除 Web Seeds | `/removeWebSeeds` | POST | `hash`, `urls` |

### Peers 管理 `/api/v2/torrents`

| 操作 | 端点 | 方法 | 参数 |
|------|------|------|------|
| 添加 Peers | `/addPeers` | POST | `hashes`, `peers` |

### 其他设置 `/api/v2/torrents`

| 操作 | 端点 | 方法 | 参数 |
|------|------|------|------|
| 自动管理 | `/setAutoManagement` | POST | `hashes`, `enable` |
| 超级做种 | `/setSuperSeeding` | POST | `hashes`, `value` |
| 强制开始 | `/setForceStart` | POST | `hashes`, `value` |
| 顺序下载 | `/toggleSequentialDownload` | POST | `hashes` |
| 首尾块优先 | `/toggleFirstLastPiecePrio` | POST | `hashes` |

### 传输信息 `/api/v2/transfer`

| 操作 | 端点 | 方法 | 参数 |
|------|------|------|------|
| 传输信息 | `/info` | GET | - |
| 下载限速 | `/downloadLimit` | GET | - |
| 上传限速 | `/uploadLimit` | GET | - |
| 设置下载限速 | `/setDownloadLimit` | POST | `limit` |
| 设置上传限速 | `/setUploadLimit` | POST | `limit` |
| 切换备用限速 | `/toggleSpeedLimitsMode` | POST | - |

### 应用程序 `/api/v2/app`

| 操作 | 端点 | 方法 | 参数 |
|------|------|------|------|
| 版本 | `/version` | GET | - |
| API 版本 | `/webapiVersion` | GET | - |
| 构建信息 | `/buildInfo` | GET | - |
| 关闭 | `/shutdown` | POST | - |
| 获取设置 | `/preferences` | GET | - |
| 设置偏好 | `/setPreferences` | POST | `json` |
| 默认保存路径 | `/defaultSavePath` | GET | - |

### 日志 `/api/v2/log`

| 操作 | 端点 | 方法 | 参数 |
|------|------|------|------|
| 日志 | `/main` | GET | `normal`, `info`, `warning`, `critical` |
| Peer 日志 | `/peers` | GET | `last_known_id` |

### 同步 `/api/v2/sync`

| 操作 | 端点 | 方法 | 参数 |
|------|------|------|------|
| 主数据 | `/maindata` | GET | `rid` |
| 种子 Peers | `/torrentPeers` | GET | `hash`, `rid` |

### RSS `/api/v2/rss`

| 操作 | 端点 | 方法 | 参数 |
|------|------|------|------|
| 添加文件夹 | `/addFolder` | POST | `path` |
| 添加订阅 | `/addFeed` | POST | `url`, `path` |
| 移除 | `/removeItem` | POST | `path` |
| 移动 | `/moveItem` | POST | `itemPath`, `destPath` |
| 获取文章 | `/items` | GET | `withData` |
| 标记已读 | `/markAsRead` | POST | `itemPath`, `articleId` |
| 刷新 | `/refreshItem` | POST | `itemPath` |
| 设置自动下载规则 | `/setRule` | POST | `ruleName`, `ruleDef` |
| 删除规则 | `/removeRule` | POST | `ruleName` |
| 获取规则 | `/rules` | GET | - |
| 匹配规则 | `/matchingArticles` | GET | `ruleName` |

### 搜索 `/api/v2/search`

| 操作 | 端点 | 方法 | 参数 |
|------|------|------|------|
| 启动搜索 | `/start` | POST | `pattern`, `plugins`, `category` |
| 停止搜索 | `/stop` | POST | `id` |
| 搜索状态 | `/status` | GET | `id` |
| 搜索结果 | `/results` | GET | `id`, `limit`, `offset` |
| 删除搜索 | `/delete` | POST | `id` |
| 获取插件 | `/plugins` | GET | - |
| 安装插件 | `/installPlugin` | POST | `sources` |
| 卸载插件 | `/uninstallPlugin` | POST | `names` |
| 启用插件 | `/enablePlugin` | POST | `names`, `enable` |
| 更新插件 | `/updatePlugins` | POST | - |

---

## 单位说明

| 参数 | 单位 | 换算 |
|------|------|------|
| `limit` (限速) | **bytes/second** | 1 MB/s = 1048576 |
| `size` | bytes | - |
| `progress` | 0-1 浮点数 | 0.5 = 50% |
| `priority` | 整数 | 0=不下载, 1=正常, 6=高, 7=最大 |

---

## 种子状态

| 状态 | 含义 |
|------|------|
| `error` | 错误 |
| `missingFiles` | 文件丢失 |
| `uploading` | 做种中 |
| `pausedUP` | 暂停做种 |
| `queuedUP` | 排队做种 |
| `stalledUP` | 做种停滞 |
| `checkingUP` | 检查中 |
| `forcedUP` | 强制做种 |
| `allocating` | 分配空间 |
| `downloading` | 下载中 |
| `metaDL` | 下载元数据 |
| `pausedDL` | 暂停下载 |
| `queuedDL` | 排队下载 |
| `stalledDL` | 下载停滞 |
| `checkingDL` | 检查中 |
| `forcedDL` | 强制下载 |
| `checkingResumeData` | 检查恢复数据 |
| `moving` | 移动中 |
| `unknown` | 未知 |

---

## 过滤器

`torrents/info` 支持的过滤器：
- `all` - 全部
- `downloading` - 下载中
- `seeding` - 做种中
- `completed` - 已完成
- `paused` - 已暂停
- `active` - 活跃
- `inactive` - 不活跃
- `resumed` - 已恢复
- `stalled` - 停滞
- `stalled_uploading` - 上传停滞
- `stalled_downloading` - 下载停滞
- `errored` - 错误

---

## 添加种子工作流

> **重要**: 添加种子前必须先查询已有保存路径，然后询问用户保存位置。

### 步骤 1: 查询已有保存路径

```bash
# 获取已有保存路径（按使用频率排序，显示前 10 个）
curl -c cookies.txt -b cookies.txt \
  "$QB_URL/api/v2/torrents/info" | \
  jq -r '.[].save_path' | sort | uniq -c | sort -rn | head -10

# 获取默认保存路径
curl -c cookies.txt -b cookies.txt \
  "$QB_URL/api/v2/app/defaultSavePath"
```

### 步骤 2: 询问用户保存位置

使用 `AskUserQuestion` 工具，展示已有路径供用户选择：

```
问题: 下载文件保存到哪个目录？

选项:
- /m2/ani/番剧 (最常用)
- /m2/movies
- /downloads (默认)
- 其他路径 (用户自定义)
```

### 步骤 3: 添加种子

用户选择路径后，执行添加操作：

```bash
# Magnet link（用户选择或指定的路径）
curl -c cookies.txt -b cookies.txt \
  -d "urls=magnet:?xt=urn:btih:xxxx" \
  -d "savepath=$USER_SELECTED_PATH" \
  "$QB_URL/api/v2/torrents/add"

# 带分类和标签
curl -c cookies.txt -b cookies.txt \
  -d "urls=magnet:?xt=urn:btih:xxxx" \
  -d "savepath=$USER_SELECTED_PATH" \
  -d "category=movies" \
  -d "tags=hd,2024" \
  "$QB_URL/api/v2/torrents/add"

# Torrent 文件
curl -c cookies.txt -b cookies.txt \
  -F "torrents=@file.torrent" \
  -d "savepath=$USER_SELECTED_PATH" \
  "$QB_URL/api/v2/torrents/add"
```

---

## 其他操作示例

### 获取种子列表

```bash
# 全部
curl -c cookies.txt -b cookies.txt \
  "$QB_URL/api/v2/torrents/info"

# 按状态过滤
curl -c cookies.txt -b cookies.txt \
  "$QB_URL/api/v2/torrents/info?filter=downloading"

# 按分类过滤
curl -c cookies.txt -b cookies.txt \
  "$QB_URL/api/v2/torrents/info?category=movies"

# 按标签过滤
curl -c cookies.txt -b cookies.txt \
  "$QB_URL/api/v2/torrents/info?tag=hd"

# 指定种子
curl -c cookies.txt -b cookies.txt \
  "$QB_URL/api/v2/torrents/info?hashes=abc123,def456"
```

### 控制种子

```bash
# 开始
curl -c cookies.txt -b cookies.txt \
  -d "hashes=abc123" \
  "$QB_URL/api/v2/torrents/start"

# 停止
curl -c cookies.txt -b cookies.txt \
  -d "hashes=abc123" \
  "$QB_URL/api/v2/torrents/stop"

### 删除种子

> **重要**: 删除种子时的 `deleteFiles` 参数规则：
>
> | 场景 | deleteFiles | 说明 |
> |------|-------------|------|
> | **默认行为** | `false` | 只删除任务，保留已下载的文件 |
> | 用户明确要求删除文件 | `true` | 用户指定要删除文件时 |
> | 未下载完成的种子 | `true` | progress < 100% 时，删除不完整的文件 |
>
> **安全原则**: 除非用户明确指定或种子未完成，否则默认不删除文件。

```bash
# 删除种子（保留文件）- 默认行为
curl -c cookies.txt -b cookies.txt \
  -d "hashes=abc123&deleteFiles=false" \
  "$QB_URL/api/v2/torrents/delete"

# 删除种子（同时删除文件）- 用户明确要求时
curl -c cookies.txt -b cookies.txt \
  -d "hashes=abc123&deleteFiles=true" \
  "$QB_URL/api/v2/torrents/delete"

# 删除多个种子（用 | 分隔）
curl -c cookies.txt -b cookies.txt \
  -d "hashes=abc123|def456|ghi789&deleteFiles=false" \
  "$QB_URL/api/v2/torrents/delete"

# 删除全部种子
curl -c cookies.txt -b cookies.txt \
  -d "hashes=all&deleteFiles=false" \
  "$QB_URL/api/v2/torrents/delete"
```

**删除前建议检查**:
```bash
# 检查种子是否完成 (progress=1 表示 100%)
curl -c cookies.txt -b cookies.txt \
  "$QB_URL/api/v2/torrents/info?hashes=abc123" | jq '.[0].progress'
```

#### 删除 API 参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `hashes` | string | ✅ | 种子 hash，多个用 `\|` 分隔，`all` 删除全部 |
| `deleteFiles` | bool | ❌ | 是否删除文件，默认 `false` |

### 设置限速

```bash
# 设置种子下载限速 1 MB/s
curl -c cookies.txt -b cookies.txt \
  -d "hashes=abc123&limit=1048576" \
  "$QB_URL/api/v2/torrents/setDownloadLimit"

# 设置种子上传限速 512 KB/s
curl -c cookies.txt -b cookies.txt \
  -d "hashes=abc123&limit=524288" \
  "$QB_URL/api/v2/torrents/setUploadLimit"

# 全局限速
curl -c cookies.txt -b cookies.txt \
  -d "limit=1048576" \
  "$QB_URL/api/v2/transfer/setDownloadLimit"
```

### 分类和标签

```bash
# 创建分类
curl -c cookies.txt -b cookies.txt \
  -d "category=movies&savePath=/downloads/movies" \
  "$QB_URL/api/v2/torrents/createCategory"

# 设置分类
curl -c cookies.txt -b cookies.txt \
  -d "hashes=abc123&category=movies" \
  "$QB_URL/api/v2/torrents/setCategory"

# 创建标签
curl -c cookies.txt -b cookies.txt \
  -d "tags=hd,4k" \
  "$QB_URL/api/v2/torrents/createTags"

# 添加标签
curl -c cookies.txt -b cookies.txt \
  -d "hashes=abc123&tags=hd" \
  "$QB_URL/api/v2/torrents/addTags"
```

### 文件优先级

```bash
# 设置文件优先级
# priority: 0=不下载, 1=正常, 6=高, 7=最大
curl -c cookies.txt -b cookies.txt \
  -d "hash=abc123&id=0&priority=0" \
  "$QB_URL/api/v2/torrents/filePrio"
```

### Tracker 管理

```bash
# 获取 trackers
curl -c cookies.txt -b cookies.txt \
  "$QB_URL/api/v2/torrents/trackers?hash=abc123"

# 添加 tracker
curl -c cookies.txt -b cookies.txt \
  -d "hash=abc123&urls=udp://tracker.example.com:1337/announce" \
  "$QB_URL/api/v2/torrents/addTrackers"
```

### 获取传输信息

```bash
curl -c cookies.txt -b cookies.txt \
  "$QB_URL/api/v2/transfer/info"
```

返回示例：
```json
{
  "dl_info_speed": 1048576,
  "dl_info_data": 10737418240,
  "up_info_speed": 524288,
  "up_info_data": 5368709120,
  "dl_rate_limit": 0,
  "up_rate_limit": 0,
  "dht_nodes": 1234,
  "connection_status": "connected"
}
```

---

## 完整脚本模板

```bash
#!/bin/bash
# 配置 - 从 CLAUDE.md 获取或使用环境变量
QB_URL="${QB_URL:-http://192.168.31.88:8080}"
QB_USER="${QB_USER:-admin}"
QB_PASS="${QB_PASS:-123123}"
COOKIE_FILE="/tmp/qb_cookies.txt"

# 登录
qb_login() {
  curl -s -c "$COOKIE_FILE" -b "$COOKIE_FILE" \
    -H "Referer: $QB_URL" \
    -d "username=$QB_USER&password=$QB_PASS" \
    "$QB_URL/api/v2/auth/login"
}

# 登出
qb_logout() {
  curl -s -c "$COOKIE_FILE" -b "$COOKIE_FILE" \
    "$QB_URL/api/v2/auth/logout"
  rm -f "$COOKIE_FILE"
}

# GET 请求
qb_get() {
  local endpoint="$1"
  curl -s -c "$COOKIE_FILE" -b "$COOKIE_FILE" \
    "$QB_URL/api/v2/$endpoint"
}

# POST 请求
qb_post() {
  local endpoint="$1"
  local data="$2"
  curl -s -c "$COOKIE_FILE" -b "$COOKIE_FILE" \
    -d "$data" \
    "$QB_URL/api/v2/$endpoint"
}

# 使用示例
qb_login

# 获取下载中的种子
qb_get "torrents/info?filter=downloading" | jq '.'

# 添加种子
qb_post "torrents/add" "urls=magnet:?xt=urn:btih:xxxx&savepath=/downloads"

qb_logout
```

---

## 常见问题

| 问题 | 解决方案 |
|------|----------|
| 登录失败 | 检查 Referer header |
| Cookie 不生效 | 确保同时使用 `-c` 和 `-b` |
| 限速不生效 | 单位是 bytes/s，不是 KB/s |
| 找不到种子 | 用 `torrents/info` 查询 hash |
| 中文乱码 | 确保 URL 编码 |
| 403 Forbidden | 检查白名单设置或 CSRF 保护 |

---

## 官方文档

- OpenAPI: https://www.qbittorrent.org/openapi-demo/
- Wiki: https://github.com/qbittorrent/qBittorrent/wiki/WebUI-API-(qBittorrent-4.1)
- API Changelog: https://github.com/qbittorrent/qBittorrent/blob/master/WebAPI_Changelog.md
