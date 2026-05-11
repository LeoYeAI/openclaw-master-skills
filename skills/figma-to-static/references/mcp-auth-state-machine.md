# Figma MCP Auth State Machine

## Goal

Make Claude + Figma MCP auth boring, deterministic, and resistant to stale-state mistakes.

Core principle: **one live session, one active state, one accepted handoff artifact**.

## Non-Negotiables

1. Keep exactly **one** live Claude/Figma auth session.
2. Never start a second login/auth flow until the first is explicitly killed or succeeds.
3. In chat/remote/headless handoff, prefer **`code#state`** over a full callback URL.
4. Use full callback URL only for:
   - state-mismatch diagnostics
   - localhost redirect recovery
5. Never hand-retype long OAuth URLs; extract/copy them exactly.
6. Never accept `done` / `好了` / `完成` / `ok` as proof of auth success.
7. Never report success until a verification command passes.

## Phase Gate

Do not skip phases.

### Phase A — Claude login

Evidence:
- `claude auth status` shows `loggedIn: false`

Action:
1. Run `python3 scripts/auth_session_guard.py --mode claude-login`
2. Start exactly one Claude login flow:
   - safe bootstrap/status: `bash scripts/setup_claude_mcp.sh`
   - explicit local start only: `bash scripts/setup_claude_mcp.sh --start-login`
   - local interactive direct: `claude auth login`
   - remote/chat/headless: `claude` → `/login`
3. If URL is wrapped, extract it exactly:
   - `python3 scripts/extract_auth_url.py --stdin`
4. Scrape the live REPL output and classify it:
   - `python3 scripts/claude_repl_state.py --stdin`
   - Only continue if it reports `state=waiting-for-code`
5. Persist the active state immediately:
   - `python3 scripts/claude_auth_lock.py acquire --session-id <session-id> --auth-url "<authorize-url>"`
6. Ask user for **`code#state`** first
7. Validate it before submission:
   - `python3 scripts/claude_auth_lock.py verify-code --code-state "<code#state>"`
8. Paste it back into the **same** waiting Claude session

Exit condition:
- `claude auth status` shows `loggedIn: true`

### Phase B — Figma MCP server exists

Evidence:
- `claude auth status` logged in
- `claude mcp list` has no `figma:` entry

Action:
- `claude mcp add --scope user --transport http figma https://mcp.figma.com/mcp`

Exit condition:
- `claude mcp list` shows `figma:`

### Phase C — Figma MCP auth

Evidence:
- `claude mcp list` shows `figma ... Needs authentication`

Action:
1. Run `python3 scripts/auth_session_guard.py --mode figma-mcp`
2. Open exactly one Claude REPL: `claude`
3. Run `/mcp`
4. Select `figma`
5. Choose `Authenticate/Connect`
6. Complete browser consent
7. If browser redirects to localhost and fails, ask user for the **full localhost callback URL** and paste it into the same waiting Claude session

Exit condition:
- `claude mcp list` shows `figma ... Connected`

### Phase D — MCP tool verification

Evidence:
- Claude logged in
- Figma MCP shows Connected

Action:
- `python3 scripts/fetch_figma_mcp.py --allow-claude-credentials --action tools`

Exit condition:
- tool list is returned successfully

## Abort Conditions

Stop immediately if any of the following is true:

- another live Claude auth/login process already exists
- callback/code belongs to an older session
- callback `state` does not match active auth `state`
- previous auth session is still waiting for input
- REPL state is not explicitly classified as `waiting-for-code`
- OAuth URL appears truncated, line-wrapped, or whitespace-corrupted

When an abort condition is met:
1. explain the exact stage and blocker
2. kill/abandon stale session(s)
3. start one clean session
4. ask for only one auth artifact

Do **not** “try one more thing” inside the dirty flow.

## Remote Chat Response Policy

During auth, replies must stay procedural:

- state the **current phase**
- state the **exact blocker**
- state the **next action**
- state the **single artifact needed** from the user

Template:

- 阶段：`Claude 登录` / `Figma MCP 配置` / `Figma MCP 授权` / `MCP 工具验证`
- 状态：`成功` / `阻塞` / `需用户操作`
- 原因：一句话具体原因
- 下一步：一句话具体动作
- 需要用户提供：`code#state` / `callback URL` / `nothing`

## Decision Notes

### User says “授权失败了”
- First check whether an auth session is already alive
- Continue that same session if it exists
- Otherwise start one clean session only

### User sends callback URL
- Validate `state` against the active authorize URL / auth lock first
- Command: `python3 scripts/claude_auth_lock.py verify-callback --callback-url "<callback-url>"`
- Paste into the same waiting session immediately

### Browser shows localhost redirect error
- Ask for full localhost callback URL
- Paste into the same waiting session
- Do not treat the browser error page itself as final failure

### Claude login succeeded but Figma MCP still not connected
- This is **not** the same problem
- Enter `/mcp` and finish the Figma auth phase separately

### MCP connected but extraction still fails
- Verify account/file access before blaming auth wiring
- Treat as account/file/service issue unless auth proof regresses
