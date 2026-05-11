# Figma MCP Usage Reference

For remote/headless/chat auth recovery, read `mcp-auth-state-machine.md` first.

## Prerequisites

Figma MCP token is stored in `~/.claude/.credentials.json` under `mcpOAuth.figma*`.

`fetch_figma_mcp.py` now auto-refreshes near-expiry tokens when running with `--allow-claude-credentials`.

If user has no Claude CLI + MCP yet, use one-click bootstrap first:

```bash
bash scripts/setup_claude_mcp.sh
```

For remote/chat handoff, do not accept a plain "done" confirmation.
Require either:

```text
Authentication Code: <code>#<state>
```

or (for diagnostics):

```text
https://platform.claude.com/oauth/code/callback?code=...&state=...
```

Manual fallback (if one-click fails):

```bash
# 1) Install Claude CLI
npm install -g @anthropic-ai/claude-code

# 2) Login
# Local interactive shell:
claude auth login

# 2b) Remote/headless/chat handoff (preferred):
claude
# then run /login
# open the authorize URL shown by Claude
# paste Authentication Code (code#state) when prompted
# keep THIS SAME Claude session alive until login succeeds

# 3) Add Figma MCP server
claude mcp add --scope user --transport http figma https://mcp.figma.com/mcp

# 4) Complete MCP auth in Claude UI
claude
# then run /mcp, select figma, Authenticate/Connect
# if browser redirects to localhost and fails, paste the FULL localhost callback URL back into Claude
# keep THIS SAME Claude session alive until it says Connected

# 5) Verify connection
claude mcp list
# expect: figma ... Connected
```

Operational rules:
- Never run multiple `claude auth login` sessions at once.
- Once an authorize URL has been generated, do not start a new login flow until that flow is finished or abandoned.
- Do not bounce between `claude auth login` and `claude` REPL during the same auth attempt.
- Before asking the user for `code#state`, classify the visible REPL output with `python3 scripts/claude_repl_state.py --stdin`; continue only when it reports `waiting-for-code`.
- Require exact handoff text: `code#state`, Claude callback URL, or localhost callback URL. Never accept a plain "done".

Or set `FIGMA_MCP_TOKEN` env var directly (advanced/manual mode).

## Preflight Input Validation

Before extraction, validate URL/key/node first:

```bash
# Format-only check
python3 scripts/validate_figma_input.py --figma-url "https://www.figma.com/design/FILEKEY/Name?node-id=0-1"

# API check (requires token): verifies file accessibility + full-page heuristic
FIGMA_TOKEN=... python3 scripts/validate_figma_input.py --figma-url "<figma-url>" --check-api
```

Interpretation:
- `FULL_PAGE_ASSESSMENT: likely full-page target` → continue.
- `likely partial/component` → ask user to confirm component-only request or provide page-level node-id.

## Script: `scripts/fetch_figma_mcp.py`

### Actions

| Action | Description | Required Args |
|---|---|---|
| `tools` | List available MCP tools | (none) |
| `info` | File/user info via whoami | `--file-key` |
| `metadata` | Node structure as XML-like markup | `--file-key --node-id/--node-ids` |
| `screenshot` | PNG screenshot of one or many nodes | `--file-key --node-id/--node-ids` |
| `context` | Rich design context (preferred by Figma) | `--file-key --node-id/--node-ids` |
| `bundle` | Fetch metadata + screenshot + context in one run | `--file-key --node-id/--node-ids` |
| `variables` | Design system variable definitions | `--file-key` |

### Examples

```bash
# Auth mode A (recommended): explicit token
export FIGMA_MCP_TOKEN=...
python3 scripts/fetch_figma_mcp.py --action tools

# Auth mode B (opt-in): read Claude credential file
python3 scripts/fetch_figma_mcp.py --allow-claude-credentials --action tools

# Get node structure
python3 scripts/fetch_figma_mcp.py --allow-claude-credentials --file-key FILE_KEY --node-id 0:6715 --action metadata --out-dir ./mcp-assets

# Batch screenshots in one MCP session
python3 scripts/fetch_figma_mcp.py --allow-claude-credentials --file-key FILE_KEY --node-ids "0:6715 0:6901 0:6902" --action screenshot --out-dir ./mcp-assets

# One-shot bundle: metadata + screenshot + context
python3 scripts/fetch_figma_mcp.py --allow-claude-credentials --file-key FILE_KEY --node-ids "0:6715 0:6901" --action bundle --out-dir ./mcp-assets

# Parse/download asset URLs from context files (auto SVG normalization)
python3 scripts/parse_design_context.py --context-glob "./mcp-assets/context-*.txt" --assets-dir ./assets --manifest ./source/context-assets.json

# Get design variables (colors, spacing tokens)
python3 scripts/fetch_figma_mcp.py --allow-claude-credentials --file-key FILE_KEY --action variables --out-dir ./mcp-assets
```

### Output Files

- `metadata-{node}.xml` — XML-like node tree with id, name, x, y, width, height
- `screenshot-{node}.png` — Rendered PNG of the node
- `context-{node}.txt` — Rich text design context
- `variables.txt` — Design system variables
- `source/context-assets.json` — Parsed context asset manifest (from `parse_design_context.py`)

## Key MCP Tools (13 total)

| Tool | Use For |
|---|---|
| `get_design_context` | **Primary** — rich structured design info for code generation |
| `get_metadata` | Node tree structure, dimensions, hierarchy |
| `get_screenshot` | Visual reference PNG of any node |
| `get_variable_defs` | Design tokens (colors, spacing, etc.) |
| `whoami` | Verify auth + permissions |
| `get_code_connect_map` | Existing component-to-code mappings |
| `get_code_connect_suggestions` | AI suggestions for component linking |

## URL Parsing

Figma URL format: `https://www.figma.com/design/{fileKey}/{name}?node-id={nodeId}`
- `fileKey`: alphanumeric string after `/design/`
- `nodeId`: URL uses `-` separator (e.g., `0-6715`), API uses `:` (e.g., `0:6715`)

## Callback Validation (Claude OAuth)

When callback is reported invalid/stale, validate before retrying:

```bash
python3 scripts/parse_claude_oauth_callback.py \
  --auth-url "<latest authorize url from claude auth login>" \
  --callback-url "<full callback url pasted by user>"
```

Common root causes:
- multiple concurrent `claude auth login` sessions (different `state` values)
- user pasted callback from an older authorize URL
- login process got terminated (timeout/SIGTERM) before callback handoff completed

Operational rules:
- Keep only one active login session.
- If mismatch occurs, restart login and use only the newest authorize URL.

## MCP vs REST API

| Feature | MCP | REST API |
|---|---|---|
| Auth | OAuth (via Claude CLI) | Personal Access Token |
| Node structure | XML-like markup | Full JSON with all properties |
| Screenshots | Built-in `get_screenshot` | Separate `/images/` endpoint |
| CSS extraction | Use `figma_to_css.py` on REST JSON | Direct from REST JSON |
| Rate limits | Per-session, generous | Per-token, stricter |
| Best for | Quick structure + screenshots | Detailed CSS property extraction |

**Recommendation:** Prefer MCP as the default access path and exhaust stable MCP auth recovery first. Use REST API only when (a) MCP is confirmed connected but the target file is still inaccessible, or (b) the user explicitly asks for PAT-based fallback. Use REST for detailed CSS property extraction when precision matters.
