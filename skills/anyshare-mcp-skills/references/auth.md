# 认证流程详解

> 完整认证逻辑——SKILL.md 中仅保留摘要，详情在此文件备用。

## 状态文件

```
~/.openclaw/skills/anyshare-mcp-skills/
└── asmcp-state.json    # 浏览器 Cookie 持久化（含 AnyShare Authorization）
```

## 认证检查流程（自动执行）

每次业务调用前，Agent 必须先完成认证检查：

```
第 1 步：检查 agent-browser CLI
  which agent-browser || npm install -g agent-browser
  agent-browser install（必要时）

第 2 步：加载状态，打开浏览器，从 Cookie 获取 AnyShare Bearer token
  agent-browser state load ~/.openclaw/skills/anyshare-mcp-skills/asmcp-state.json
  agent-browser open https://anyshare.aishu.cn/anyshare/zh-cn/
  agent-browser cookies get Authorization
  # 格式：Authorization=Bearer ory_at_xxx，提取 Bearer 后的 token 部分

第 3 步：MCP initialize（无需 Authorization 头）
  POST /mcp → { method: initialize } → 获得 Mcp-Session-Id

第 4 步：调用 auth_login 注册 token（通过 mcporter）
  mcporter call asmcp.auth_login token="<AnyShare Bearer>"
  → mcporter daemon 负责 initialize session 并注册 token
  → 此后 asmcp 的所有工具调用通过 mcporter 路由，自动携带认证状态

第 5 步：验证
  mcporter call asmcp.auth_status
  → auth_login 返回成功：检查通过，继续执行业务场景
  → auth_login 失败：触发「认证恢复」
```

## 认证恢复（401 / 登录失效时触发）

> 触发时告知用户：「检测到登录状态已过期，正在重新登录…」，全程无头浏览器对用户透明。

```bash
# 1. 打开登录页
agent-browser open https://anyshare.aishu.cn/anyshare/zh-cn/

# 2. 获取表单 refs 并填表（snapshot -i = 无障碍树 refs）
agent-browser snapshot -i
# refs: e10=账号框, e11=密码框, e12=登录按钮
agent-browser fill @e10 "<账号>"
agent-browser fill @e11 "<密码>"
agent-browser click @e12
agent-browser wait --load networkidle

# 3. 从 Cookie 提取 AnyShare Bearer token
agent-browser cookies get Authorization
# 格式：Authorization=Bearer ory_at_xxx，提取 Bearer 后的 token

# 4. 通过 mcporter 调用 auth_login 注册 token
mcporter call asmcp.auth_login token="<AnyShare Bearer>"
# mcporter daemon 负责与 asmcp 建立 session 并注册 token

# 5. 保存浏览器状态供后续复用
mkdir -p ~/.openclaw/skills/anyshare-mcp-skills
agent-browser state save ~/.openclaw/skills/anyshare-mcp-skills/asmcp-state.json

# 6. 关闭浏览器
agent-browser close
```

> 认证恢复全程无头运行（`agent-browser` 默认无 UI），不会弹出窗口。
> 账号密码仅用于 fill 操作，不记录日志。

## Token 刷新（小时级）

MCP access_token 有效期约 1 小时。失效后：
1. 从浏览器 Cookie 重新获取新的 AnyShare Bearer token
2. 在 mcporter daemon session 内再次调用 `auth_login`（`mcporter call asmcp.auth_login token="<新token>"`）
3. **不需要重启网关**，继续执行业务

## 401 自动处理

MCP 请求返回 401 或认证错误时：
1. 重新执行「认证恢复」流程（第 1~6 步）
2. 更新 token 后重试原业务场景
3. 若恢复后仍失败，向用户报告

## 换账号

换账号前先删除 `~/.openclaw/skills/anyshare-mcp-skills/asmcp-state.json`，再重新走认证恢复流程。
