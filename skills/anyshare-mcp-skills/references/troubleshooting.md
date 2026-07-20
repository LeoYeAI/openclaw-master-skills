# AnyShare MCP — 常见错误与排查

> 按需查阅。完整流程以技能根目录 **`SKILL.md`** 为准；首次安装与 `mcporter.json` 写入见同目录 **`setup.md`**。  
> 认证由 **agent-browser** 取 Cookie + **`mcporter call asmcp.auth_login`** 完成，**不要**在 `~/.mcporter/mcporter.json` 的 `headers` 中配置 Bearer。

---

## 初始化与 mcporter 配置

| 现象 | 可能原因 | 处理 |
|------|----------|------|
| 首次使用不知道填什么地址 | 技能包默认仅为占位；**企业客户**应向运维索取**本企业** **MCP 服务地址** | 按 **`setup.md`**：写入后无论成败都请用户确认是否为本企业正式端点 |
| 找不到 `asmcp` 或 `mcporter list` 无 asmcp | 未配置或未重载 daemon | 按 **`setup.md`** 写入 `~/.mcporter/mcporter.json`，执行 `mcporter daemon restart` 后再 `mcporter list` |
| 换网关后工具全失败 | **MCP 服务地址**已变但配置未更新 | 按 **`setup.md`「修改 MCP 服务地址」** 更新 `asmcp.url` 并重启 daemon |
| `mcporter list` 有 `asmcp` 但请求返回 **503** | 默认官方 URL 在你网络/部署下不可达，或需私有化网关 | 向运维索取实际 MCP 端点并更新 `asmcp.url`；非技能文档错误 |
| 配置写入后仍连不上 MCP | **MCP 服务地址**（`url`）错误或服务未监听 | 核对 **MCP 服务地址**与端口；确认服务端 HTTP 可达 |

---

## 认证与令牌

| 现象 | 可能原因 | 处理 |
|------|----------|------|
| `auth_login` 失败或 `auth_status` 异常 | Cookie 无效、未登录或 session 过期 | 按 `SKILL.md`「认证恢复」：agent-browser 登录 → `cookies get Authorization` → `mcporter call asmcp.auth_login token="<Bearer 值>"` |
| 401 / 业务接口报未授权 | MCP access_token 过期（约小时级） | 从 Cookie 取新 AnyShare Bearer，在同一 mcporter session 内再次 `auth_login`，**无需**改 `mcporter.json`、**无需**重启网关（除非 daemon 异常） |
| 换账号后仍是旧用户 | 浏览器状态未清 | 先删除 `~/.openclaw/skills/anyshare-mcp-skills/asmcp-state.json`，再按 `SKILL.md` 重新登录与 `auth_login` |
| `agent-browser` 不可用 | 未安装或未 `install` | `npm install -g agent-browser`，必要时 `agent-browser install` 补全浏览器 |

---

## 工具发现与调用

| 现象 | 可能原因 | 处理 |
|------|----------|------|
| 不知道有哪些工具 / 参数 | 与主技能约定不一致 | 以 **`mcporter list asmcp`** 返回的 schema 为准（`SKILL.md` 核心注意第 5 条） |
| `mcporter call` 报错或参数无效 | 使用了 `--key value` 风格 | 使用 **`key=value`**，例如：`mcporter call asmcp.file_search keyword="文档" type="doc" start=0 rows=25` |
| `Call to asmcp.* timed out after 60000ms`（或类似） | **mcporter** 对单次 `call` 的默认超时（约 60s），非 MCP 网关配置 | **运行 OpenClaw 的设备**：将技能包 **`openclaw.skill-entry.json`** 合并进 **`~/.openclaw/openclaw.json`** → **`skills.entries["anyshare-mcp-skills"].env`**（见 **`setup.md`「OpenClaw 运行时环境变量」**）；兜底：单次命令加 **`--timeout 600000`**；daemon 变更后建议 **`mcporter daemon restart`** |
| 直连 HTTP `tools/list` 无响应 | 未先 initialize 或地址错误 | 备选：按 `SKILL.md`「工具调用方式」③；日常优先 mcporter |

---

## 文件与搜索

| 现象 | 可能原因 | 处理 |
|------|----------|------|
| `file_upload` 失败 | 路径在 MCP 服务端不可读 | 确认文件在服务端本机或已挂载路径上 |
| `file_search` 分页/范围与预期不符 | 参数与实现不一致 | 仅传 `SKILL.md` 场景一允许的字段；以 `mcporter list asmcp` 中 `file_search` 的 schema 为准 |
| 搜索结果为空 | 关键词不匹配或路径/标签过滤过严 | 放宽关键词，或减少 `range`、标签限制 |
| `file_convert_path` 失败或 **`namepath` 为空** | `docid` 非完整 gns、无权限、或 `/efast/v1/file/convertpath` 报错 | 核对传入 **完整 `gns://…` docid** 与登录态；仍失败时**仅展示完整 docid**，路径展示可省略，**不阻塞**搜索/上传/下载主流程 |

---

## 上传 / 下载

| 现象 | 可能原因 | 处理 |
|------|----------|------|
| `file_upload` 目标无效（invalid docid） | docid 不存在或无权限 | 仅用 `file_search` 定位并由用户确认 docid（见 `SKILL.md` 安全约束） |
| `file_osdownload` 失败 | 文件删除、无权限或 docid 错误 | 重新 `file_search` 并由用户确认 |

---

## Bot 对话（chat_send）

| 现象 | 可能原因 | 处理 |
|------|----------|------|
| 流式返回截断 / 空答 | `query` 过长或网络问题 | 缩短 `query` 或拆多轮 |
| `mcporter call asmcp.chat_send` 超时 | 服务端推理久于 mcporter 默认 **call** 超时 | 优先确认 **`~/.openclaw/openclaw.json`** 已合并 **`openclaw.skill-entry.json`**（`skills.entries.anyshare-mcp-skills.env`）；沙箱会话另配 **`agents.defaults.sandbox.docker.env`**（见 **`setup.md`**）；兜底 **`--timeout 600000`** |
| 多轮中断 | 未回传 `conversation_id` | 从上一轮响应补传；`version` / `temporary_area_id` 不传（见 `SKILL.md` 场景四） |
| `source_ranges` 无效 | 传了文件夹 ID 或格式错误 | 按 `SKILL.md`「AnyShare 基础知识」：`chat_send` 的 `id` 为 docid **最后一段**，`type` 为 `"doc"` |

---

## 网络与 TLS（测试环境）

| 现象 | 可能原因 | 处理 |
|------|----------|------|
| TLS 证书错误 | 自签名或内网证书 | 测试环境按部署说明处理；生产环境使用有效证书 |
| `connection refused` | **MCP 服务地址**或端口错误、防火墙 | 检查 **MCP 服务地址** URL 与网络连通性 |
