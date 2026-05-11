---
name: figma-to-static
description: >
  Convert Figma design files to pixel-level mobile-first static HTML/CSS pages.
  Use when: (1) user provides a Figma file link and wants a static web page,
  (2) user sends design screenshots/assets and says "按设计图还原",
  (3) user asks to build a landing page from Figma,
  (4) iterating on Figma-to-code pixel accuracy.
  Handles: Figma MCP-first extraction (metadata/context/screenshots) with REST API fallback,
  layered DOM reconstruction (not whole-image paste), visual diff pipeline with region heatmap for
  quality validation, mobile-first responsive layout.
  NOT for: React/Vue/SPA frameworks, server-side rendering, interactive JS-heavy pages.
metadata: {"clawdbot":{"emoji":"🎨","requires":{"bins":["python3"],"env":["FIGMA_MCP_TOKEN","FIGMA_TOKEN"]},"configPaths":["~/.claude/.credentials.json"]}}
---

# Figma → Static HTML/CSS

## Recommended Runtime Profile

- **Preferred model:** `anthropic/claude-opus-4-6`
- **Preferred thinking level:** `high`
- Use this profile for full-page restoration, asset extraction planning, and multi-section iteration.
- If only doing quick environment checks or tiny CSS tweaks, lower-cost models are acceptable.

## MCP Auth Non-Negotiables

When handling Claude/Figma MCP authentication, follow these rules with zero improvisation:

1. Keep **exactly one live auth session**.
2. Never start a second Claude/Figma auth flow until the first one is explicitly killed or succeeds.
3. Never manually retype or reconstruct long OAuth URLs in chat.
4. In remote/chat/headless handoff, prefer receiving **Authentication Code (`code#state`)** over full callback URL.
5. Use full callback URL only for **state-mismatch diagnostics** or localhost redirect recovery.
6. Treat vague confirmations (`done` / `好了` / `完成` / `ok`) as invalid auth evidence.
7. After Claude login succeeds, do **not** assume Figma MCP is authenticated; verify separately.
8. If a state/session mismatch is suspected, **stop immediately**, kill stale flow(s), and restart from one clean session.

## Remote Chat Handoff Rule

In chat/remote/headless environments:

- Prefer asking the user to return **`code#state`**.
- Request the **full callback URL** only when debugging state mismatch or localhost redirect failures.
- If the CLI already displayed an authorize URL, copy it exactly from tool output or extract it with `scripts/extract_auth_url.py`; never hand-retype long URLs.
- Before opening a fresh login flow, run `scripts/auth_session_guard.py` to detect conflicts or stale state.
- **Do not ask the user for `code#state` until REPL state is explicitly verified as `waiting-for-code`.**
  - Scrape the current REPL output.
  - Classify it with `python3 scripts/claude_repl_state.py --stdin`.
  - Only if `safeForCodeSubmission=true`, lock the auth URL/state and ask the user for code.

## Abort Conditions

Stop immediately and explain the issue if any of the following is true:

- another live Claude auth/login process already exists
- callback/code belongs to an older session
- callback `state` does not match the active auth `state`
- a previous auth session is still waiting for input
- an OAuth URL appears truncated, wrapped, or whitespace-corrupted

When an abort condition is met, do **not** “try one more thing” inside the same flow. Kill or abandon stale session(s), start one clean session, and ask for only one auth artifact.

## Auth Status Reply Template

During auth, report progress in this shape:

- 阶段：`Claude 登录` / `Figma MCP 配置` / `Figma MCP 授权` / `MCP 工具验证`
- 状态：`成功` / `阻塞` / `需用户操作`
- 原因：一句话具体原因
- 下一步：一句话具体动作
- 需要用户提供：`code#state` / `callback URL` / `nothing`

## Constraints

- **Only native HTML + CSS.** No React, Vue, or any framework.
- **Mobile-first.** PC: centered `max-width`, background stretches.
- **Directory structure:** `assets/ css/ html/`
- **Layered UI structure.** Never paste a whole section as a single `<img>` unless the design element is truly an image (photo/illustration). Text, buttons, status indicators → real DOM. **Navigation bars and menus must always be real DOM** — they need to align with content width and have interactive states.
- **MCP screenshots for component images only.** Use MCP `get_screenshot` for visual assets (video covers, banners, illustrations). Use MCP `get_design_context` for components that need real DOM (nav, menus, footers) — it returns structured data with asset URLs for individual icons/logos.
- **Avoid absolute positioning.** Prefer `flexbox`, `grid`, `margin`, `padding`, and normal document flow. Only use `position: absolute` as last resort (e.g., decorative badges on cards, small floating labels).
- **Image dimensions must be declared.** Every `<img>` must have explicit `width`/`height` attributes or CSS `aspect-ratio` to prevent layout shift (CLS).
- **BEM-like semantic class names.** Use `.block__element--modifier` (e.g. `.signin-card__label`, `.hero-topbar__brand`). Never use `.s1`, `.btn2`, `.c-red` abbreviations.
- **1:1 pixel-level restoration target.** Use visual diff pipeline to validate.
## Multi-Page Strategy

- If the user specifies multiple pages (e.g., "首页 + 活动页 + 个人中心"), create separate HTML files: `html/index.html`, `html/activity.html`, `html/profile.html`, etc.
- If the user does not specify, **default to single page** (`html/index.html`).
- Each page shares the same `css/styles.css` and `assets/` directory.
- If Figma file has multiple pages (top-level Page nodes), ask user which pages to implement.

## Version Control

- **Commit after each completed section** (not after every CSS tweak).
- Commit message format: `feat: add <section-name> section` or `fix: adjust <section-name> <what>`
- **Never push** unless user explicitly asks.
- Small, reversible commits. If unsure about a change, commit current state first, then experiment.

## Completion Criteria

The page is "done" when ALL of the following are met:
1. **Layout confirmed** by user (skeleton step).
2. **All sections implemented** with real DOM and real assets (no placeholders).
3. **Visual diff similarity ≥ 90%** against the full-page design reference.
4. **No horizontal scroll** on mobile viewport (375px-414px test).
5. **User explicitly confirms** final result.
6. **If custom generation rules were provided**, output satisfies those rules.

## Workflow

### 0. Environment Check

Check Figma access in strict priority order (**must attempt MCP first**):

**Priority 1 (required first attempt): Claude CLI + Figma MCP**
```bash
# Explicit token mode (recommended)
export FIGMA_MCP_TOKEN=...
python3 scripts/fetch_figma_mcp.py --action tools

# OR opt-in read from Claude credential file
python3 scripts/fetch_figma_mcp.py --allow-claude-credentials --action tools
```
- Lists tools → MCP authenticated, proceed with MCP workflow.
- If it fails with "No Figma MCP token found", **must first try one-click bootstrap**:
  - `bash scripts/setup_claude_mcp.sh`
    - safe default = preflight/status only; does **not** auto-start a login flow
    - explicit opt-in to start login: `bash scripts/setup_claude_mcp.sh --start-login`
  - Before any fresh login flow, run:
    - `python3 scripts/auth_session_guard.py --mode claude-login`
    - if a user-facing authorize URL is created, immediately persist the active state:
      - `python3 scripts/claude_auth_lock.py acquire --session-id <session-id> --auth-url "<authorize-url>"`
  - In remote/chat/headless environments, prefer **one persistent `claude` REPL session** over repeated `claude auth login` attempts.
  - Login rule: once a Claude auth prompt has produced an authorize URL, **do not create a second login flow** until the first one either succeeds or is explicitly abandoned.
  - During remote/chat handoff, ask for **Authentication Code (`code#state`) first**.
  - Before asking for it, prove the REPL is actually waiting for code:
    - scrape current terminal output
    - classify with `python3 scripts/claude_repl_state.py --stdin`
    - proceed only when `state=waiting-for-code` and `safeForCodeSubmission=true`
  - Request full callback URL only for stale-state diagnostics or localhost redirect failures:
    - `https://platform.claude.com/oauth/code/callback?code=...&state=...`
  - Do **not** accept only "好了/完成/ok" as auth completion signal.
- If one-click bootstrap is unavailable, use manual onboarding:
  1. Install Claude CLI: `npm install -g @anthropic-ai/claude-code`
  2. Login:
     - **Local interactive shell:** try `claude auth login`
     - **Remote/headless/chat handoff (preferred):** run `claude`, then `/login`, keep that same REPL session alive, and paste Authentication Code (`code#state`) when prompted.
     - Do **not** bounce between `claude auth login` and `claude` REPL during the same auth attempt.
  3. Add server: `claude mcp add --scope user --transport http figma https://mcp.figma.com/mcp`
  4. Open Claude UI and finish MCP auth in **one session**:
     - run `claude`
     - run `/mcp`
     - select `figma` and complete Authenticate/Connect flow
     - if Figma browser redirects to localhost and fails, paste the **full localhost callback URL** back into Claude
  5. Verify: `claude mcp list` (expect `figma ... Connected`)
- After step 5, retry `python3 scripts/fetch_figma_mcp.py --allow-claude-credentials --action tools`.
- See `references/figma-mcp-usage.md` for details.

**Priority 2: Figma REST API** (fallback, detailed CSS properties)
```bash
curl -s -o /dev/null -w "%{http_code}" \
  -H "X-Figma-Token: $FIGMA_TOKEN" \
  "https://api.figma.com/v1/me"
```
- **200** → Token valid. Use quota-aware REST mode first:
  - `python3 scripts/fetch_figma_rest.py --file-key FILE_KEY --nodes "NODE1,NODE2" --quota-aware --batch-size 3 --max-retry-after 60`
- **401/403** → Guide user to generate token at Figma → Account Settings → Personal access tokens.
- **429** → Do not tight-retry. Reduce batch size (`--batch-size 1~2`) or switch to `--metadata-only` skeleton flow.

**Priority 3: User-provided assets** (fallback)
- ZIP of design assets + design screenshots.

### Quick Troubleshooting

Before troubleshooting remote/chat/headless MCP auth, read:
- `references/mcp-auth-state-machine.md`

When MCP is not ready, guide the user in this exact order:

Auth policy while replying:
- be terse and procedural
- do not improvise or summarize partial auth as success
- do not reassure unless a verification command passed
- always state: current stage, blocker, exact next action, exact artifact needed from user

1. **One-click setup (recommended first, default path)**
   - Run a single command:
     - `bash scripts/setup_claude_mcp.sh`
   - Preflight guard (must pass before new flow):
     - `python3 scripts/auth_session_guard.py --mode claude-login`
   - This script handles: install Claude CLI → login preflight → add figma MCP → status verification.
   - Safe default: it does **not** auto-start a fresh login flow.
   - Start login only with explicit opt-in:
     - `bash scripts/setup_claude_mcp.sh --start-login`
   - If an authorize URL is generated, persist the active state before asking the user for auth data:
     - `python3 scripts/claude_auth_lock.py acquire --session-id <session-id> --auth-url "<authorize-url>"`
   - In remote/headless/chat flows, prefer **one persistent `claude` REPL session**:
     - run `claude`
     - complete any first-run setup screens first (theme / login method)
     - scrape the visible REPL output and classify with `python3 scripts/claude_repl_state.py --stdin`
     - if state is not `waiting-for-code`, do not ask user for auth data yet
     - run `/login` if needed
     - open the authorize URL shown by Claude
     - if you need to pass the URL through chat, first extract it exactly with `python3 scripts/extract_auth_url.py --stdin`
     - persist the active state via `python3 scripts/claude_auth_lock.py acquire --session-id <session-id> --auth-url "<authorize-url>"`
     - paste Authentication Code (`code#state`) into `Paste code here if prompted >`
     - keep that same Claude session alive until login succeeds
   - Reject vague confirmations ("好了/完成"). Require exact auth handoff text (`code#state`, callback URL, or localhost callback URL).
   - Before asking for auth data, classify the live REPL output with `python3 scripts/claude_repl_state.py --stdin`; only continue when it reports `waiting-for-code`.
   - Validate user-returned auth data against the active lock **before** submission:
     - `python3 scripts/claude_auth_lock.py verify-code --code-state "<code#state>"`
     - or `python3 scripts/claude_auth_lock.py verify-callback --callback-url "<callback-url>"`
   - **Never** start another login attempt while one Claude session is already waiting for callback/code.

2. **Check Claude usage quota early (avoid dead-end loops)**
   - Quick probe:
     - `claude --print "quota-check"`
   - If output contains phrases like `You've hit your limit` / reset time:
     - Stop MCP auth retry loop (this is quota, not auth wiring)
     - Wait for reset, or switch/upgrade Claude account
     - Continue delivery via REST fallback (`FIGMA_TOKEN`) with skeleton-first + quota-aware pulling

3. **If one-click setup fails, use manual checks**
   - Follow `references/mcp-auth-state-machine.md` strictly; do not improvise auth retries.
   - `claude` command not found:
     - `npm install -g @anthropic-ai/claude-code`
     - Re-check: `claude --version`
   - Not logged in:
     - local shell: `claude auth login`
     - remote/headless/chat: `claude` → `/login` → keep the same REPL alive → paste Authentication Code (`code#state`)
   - Figma MCP server missing:
     - `claude mcp add --scope user --transport http figma https://mcp.figma.com/mcp`
   - Figma MCP shows `Needs authentication`:
     - open `claude` → `/mcp` → figma → Authenticate/Connect
     - if browser redirects to localhost and fails, paste the full localhost callback URL back into the same Claude session
     - verify with `claude mcp list` (must be `Connected`)

4. **Script cannot find token**
   - Preferred explicit mode:
     - `export FIGMA_MCP_TOKEN=...`
     - `python3 scripts/fetch_figma_mcp.py --action tools`
   - Optional credential-file mode:
     - `python3 scripts/fetch_figma_mcp.py --allow-claude-credentials --action tools`

5. **Still blocked after MCP auth is truly stabilized**
   - Do **not** recommend PAT/REST just because Claude auth handoff was messy once.
   - First confirm all of the following:
     - `claude auth status` shows logged in
     - `claude mcp list` shows `figma ... Connected`
     - the MCP `whoami` result matches the intended Figma account
     - only then test `fetch_figma_mcp.py`
   - Only if MCP is authenticated yet the target file remains inaccessible or the user explicitly wants fallback, use REST API mode (quota-aware, low burst):
     - `export FIGMA_TOKEN=...`
     - `python3 scripts/fetch_figma_rest.py --file-key FILE_KEY --nodes "NODE1,NODE2" --quota-aware --batch-size 2 --sleep-ms 1500 --max-retry-after 60`
   - If 429 persists with long `Retry-After`, stop image pull and continue with metadata-only skeleton:
     - `python3 scripts/fetch_figma_rest.py --file-key FILE_KEY --nodes "NODE1,NODE2" --metadata-only`
   - Or continue with user-provided ZIP/screenshots.

6. **Callback invalid / stale diagnostics (must check before retry loop)**
   - Most common causes:
     1) stale callback from an older auth attempt (state mismatch)
     2) multiple concurrent `claude auth login` sessions created different states
     3) waiting login process was terminated (timeout/SIGTERM) before callback handoff
     4) authorize URL was copied through chat with truncation/whitespace corruption
   - Enforce single-session rule: keep only one active Claude login process at a time.
   - Run guard first:
     - `python3 scripts/auth_session_guard.py --mode claude-login`
   - Extract the authorize URL from raw CLI output instead of hand-copying:
     - `python3 scripts/extract_auth_url.py --stdin`
   - Validate callback state against current authorize URL:
     - `python3 scripts/parse_claude_oauth_callback.py --auth-url "<latest_auth_url>" --callback-url "<user_callback_url>"`
   - If mismatch, stop immediately, kill stale flow(s), and use **only one new authorize URL**.

### 0.3 Validate Figma Link (must run before rule intake)

Before asking custom rules, validate link/file/node first:

```bash
# Fast syntax check (no token required)
python3 scripts/validate_figma_input.py --figma-url "<figma-url>"

# Strong check (requires FIGMA_TOKEN): verify file accessibility + full-page heuristic
FIGMA_TOKEN=... python3 scripts/validate_figma_input.py --figma-url "<figma-url>" --check-api
```

Decision rules:
- `INVALID_URL` / `FILE_INVALID_OR_UNAUTHORIZED` / `NODE_INVALID` → stop and ask user for corrected link/access.
- `FULL_PAGE_ASSESSMENT: likely partial/component` → ask user to confirm whether they want component restore or provide page-level node-id.
- If no `node-id`, default target is whole file/page and continue.

### 0.5 Rule Intake Gate (Optional, Can Be Empty)

Before generating code, offer user an optional rule intake. If user leaves it blank, proceed with defaults.

Collect only these six fields:

1. **Adaptive strategy**
   - User options: `mobile-first` / `desktop-first` / `mobile-only` / `desktop-only`
   - Default: `mobile-first`

2. **Breakpoints**
   - User format example: `375, 768, 1200`
   - Default: `375, 768, 1200`

3. **Layout width strategy**
   - User options: `fixed width` / `fluid` / `max-width centered`
   - Default: `max-width centered`

4. **Typography sizing strategy**
   - User options: `px` / `rem` / `clamp`
   - Default: `clamp` for responsive text, with pixel-accurate base ratio

5. **Interactive states**
   - User options: `none` / `basic` (`:hover,:active,:disabled`) / `full`
   - Default: `basic`

6. **Browser compatibility target**
   - User options: `modern evergreen only` / `include Safari stable`
   - Default: `include Safari stable`

If any field is empty, keep the default and continue execution without blocking.

Quick prompt template:

```text
可选自定义生成规则（可留空，留空=默认）：
1) 端适配策略（mobile-first/desktop-first/mobile-only/desktop-only）：
2) 断点（例如 375,768,1200）：
3) 页面宽度策略（fixed/fluid/max-width centered）：
4) 字体策略（px/rem/clamp）：
5) 交互态（none/basic/full）：
6) 浏览器兼容目标（modern only/include Safari stable）：
```

### 1. Gather Inputs

Required (at least one):
- Figma file URL + fileKey
- User-provided ZIP of design assets (PNG/SVG)
- Design reference screenshots

**If Figma MCP available** (preferred):
```bash
# Choose auth mode once:
# A) export FIGMA_MCP_TOKEN=...
# B) MCP_AUTH="--allow-claude-credentials"

# Step 1: Batch pull metadata+screenshot+context in one MCP session
python3 scripts/fetch_figma_mcp.py ${MCP_AUTH:-} \
  --file-key FILE_KEY \
  --node-ids "NODE_ID NAV_NODE_ID COVER1 COVER2" \
  --action bundle \
  --out-dir ./mcp-assets

# Step 2: Parse/download context assets automatically (SVG normalization included)
python3 scripts/parse_design_context.py \
  --context-glob "./mcp-assets/context-*.txt" \
  --assets-dir ./assets \
  --manifest ./source/context-assets.json

# Step 3: Optional targeted screenshots for image-heavy sections
python3 scripts/fetch_figma_mcp.py ${MCP_AUTH:-} \
  --file-key FILE_KEY \
  --node-ids "BANNER1 FOOTER" \
  --action screenshot \
  --out-dir ./assets
```

**If REST API available** (for detailed CSS extraction):
- First run quota-aware small-batch pull:
  - `python3 scripts/fetch_figma_rest.py --file-key FILE_KEY --nodes "NODE1,NODE2" --quota-aware --batch-size 2 --sleep-ms 1500 --max-retry-after 60`
- If image quota is blocked, switch to skeleton-safe metadata mode:
  - `python3 scripts/fetch_figma_rest.py --file-key FILE_KEY --nodes "NODE1,NODE2" --metadata-only`
- Then run `scripts/figma_to_css.py` on the exported `nodes.json`.

**If ZIP provided:**
- Unzip to `source/`, rename files meaningfully, copy usable assets to `assets/`.

### 2. Analyze Structure → Layout First, Then Details

**Critical rule: always build the skeleton before polishing pixels.**

1. **Identify sections** from the full-page design:
   - Scan top-to-bottom, name each visual block (hero, signin, feature-1, feature-2, footer…).
   - Output a section map with approximate vertical order and height ratios.

2. **Build the skeleton** — placeholder-only HTML/CSS:
   - One `<section>` per block with a colored background or placeholder text.
   - Flex/grid layout structure in place (no absolute positioning).
   - Correct vertical stacking order and relative heights.
   - `overflow-x: hidden` on body, scrollable rows marked.

3. **Take skeleton screenshot → send to user for confirmation.**
   - Ask: "布局结构和分段顺序对吗？"
   - Do NOT proceed to detail work until user confirms the layout.

4. **Layer in details** per confirmed section:
   - Insert real assets (images, icons).
   - Build real DOM for text, buttons, status indicators, timelines.
   - Apply typography, colors, spacing, borders from Figma node data.
   - Take screenshot → send to user after each section completes.
   - Git commit after each section is done.

6. **Missing assets? Try to fetch before asking:**
   - Check if the asset exists in `assets/` or `source/` (cache first).
   - If REST API is available, pull only the needed nodes in small batches:
     - `python3 scripts/fetch_figma_rest.py --file-key FILE_KEY --nodes "<node-id>" --quota-aware --batch-size 1`
   - If the node ID is unknown, ask the user for the specific layer/node ID.
   - If REST API quota is blocked (`quota-status.json` shows degraded), continue skeleton and ask user for direct asset file.

7. **NEVER generate fake assets.**
   - Do NOT screenshot a design and crop it to create an "asset".
   - Do NOT draw/create placeholder images to simulate missing design elements.
   - Do NOT use solid-color boxes or emoji to stand in for real icons/photos.
   - Every pixel must come from either: (a) Figma export, (b) user-provided file, or (c) CSS/SVG reconstruction of simple shapes (borders, backgrounds, gradients — NOT complex illustrations).

### 3. Build the Page

First apply resolved rule-intake profile (user values or defaults), then generate files.

Generate three directories:

**`html/index.html`** (or `html/<page>.html` for multi-page)
- Semantic `<section>` per design block.
- Real DOM elements for text, status, buttons, timelines.
- Images only for true visual assets (backgrounds, illustrations, photos).
- `<meta viewport>` with `width=device-width, initial-scale=1`.

**`css/styles.css`**
- `:root` variables for max-width and theme colors.
- `overflow-x: hidden` on `html, body, .page-shell` to prevent horizontal scroll.
- `overflow-x: clip` on `.stage` containers; only specific scrollable rows get `overflow-x: auto`.
- Percentage-based positioning for overlays (derived from Figma node coordinates).
- `clamp()` for responsive typography.
- `@media (min-width: 801px)` for PC centered layout.

**`assets/*`**
- Named meaningfully (not `figma-01.png`).
- Prefer user-provided assets over Figma exports when available.

### 4. Auto-Extract CSS from Figma Nodes

After fetching `nodes.json`, run the auto-extraction script:

```bash
python3 scripts/figma_to_css.py --nodes rest-assets/nodes.json --out source/figma-extracted.css
```

This parses every node and outputs CSS property blocks for:
- Colors, fonts, spacing, shadows, borders, border-radius
- Auto-layout: flex-direction, gap, justify-content, align-items, padding

Use the extracted CSS as a reference when writing `styles.css`. Do NOT copy-paste blindly — adapt to the actual DOM structure.

### 5. Extract Exact Properties from Figma Nodes

**Do not guess.** Read `nodes.json`, then map values to CSS.

Use this reference for full mapping table + strict rules:
- `references/css-extraction-rules.md`

### 6. Visual Diff Validation (with Region Heatmap)

After each major iteration:

```bash
# 1. Screenshot current render
google-chrome --headless=new --disable-gpu --no-sandbox \
  --window-size=800,5338 \
  --screenshot=compare/current.png \
  http://127.0.0.1:PORT/html/

# 2. Compare with region heatmap + structure metrics (default 5x5 grid)
python3 scripts/visual_diff.py \
  --current compare/current.png \
  --target assets/design-main.png \
  --diff compare/diff.png \
  --regions 5 \
  --threshold 30 \
  --json-out compare/metrics.json
```

The tool outputs:
- **MAE similarity** (pixel-level)
- **SSIM similarity** (structure-level)
- **Composite similarity** (weighted MAE + SSIM)
- Heatmap overlay (green/yellow/red), plus labeled bad regions by MAE threshold

Focus iteration on red regions first, then raise composite similarity.

### 7. Preview Server

When running on a cloud server, start a temporary HTTP server for public preview:

```bash
# Find an available port (e.g. 8090 if 8080 is taken)
python3 -m http.server PORT --bind 0.0.0.0
```

- Run in background so it persists across iterations.
- Bind to `0.0.0.0` (not `127.0.0.1`) so it's accessible via public IP.
- Check for port conflicts before starting (`lsof -i :PORT` or `ss -tlnp`).
- Provide user with `http://<PUBLIC_IP>:PORT/html/` link.
- If running behind a firewall, ensure the port is open.

### 8. Screenshot & Send to User (Every Iteration)

After each code generation iteration, before reporting results:

1. Take a screenshot of the current render:
```bash
google-chrome --headless=new --disable-gpu --no-sandbox \
  --window-size=800,5338 \
  --screenshot=compare/current.png \
  http://127.0.0.1:PORT/html/
```

2. **Send the screenshot to the user** via the messaging platform (Telegram/Discord/etc.) using the media/file sending tool — do NOT just send a URL, send the actual image.

3. Then optionally run visual diff against target and mention the similarity score.

This ensures the user can verify visual quality **without opening a browser** on every iteration.

## Anti-Patterns (Shortlist)

1. Never use a full-section screenshot when real DOM is required.
2. Never invent content or fake assets.
3. Never skip mobile overflow controls (`overflow-x: hidden` where needed).
4. Never guess properties that exist in Figma JSON.
5. Never build nav/menu/timeline as image slices when interactive DOM is expected.

Full checklist: `references/anti-patterns.md`

## Scripts

- `scripts/validate_figma_input.py` — Validate Figma URL/file/node; optionally classify whether target is full-page vs component (`--check-api`).
- `scripts/fetch_figma_mcp.py` — **Primary.** MCP fetcher with token auto-refresh, batch node extraction (`--node-ids`), and bundle mode (`--action bundle`).
- `scripts/auth_session_guard.py` — Detect conflicting Claude sessions and refuse fresh login attempts while an active auth lock or existing Claude process is present.
- `scripts/claude_auth_lock.py` — Persist the one active Claude auth state (`sessionId` + authorize URL/state) and validate incoming `code#state` or callback URLs before submission.
- `scripts/claude_repl_state.py` — Classify raw Claude REPL output (theme picker / login method picker / waiting-for-code / ambiguous) and block auth handoff unless the REPL is actually waiting for code.
- `scripts/extract_auth_url.py` — Extract an unbroken Claude OAuth authorize URL from raw terminal output; use instead of hand-copying wrapped URLs.
- `scripts/parse_claude_oauth_callback.py` — Validate callback URL or `code#state` against the active authorize URL to detect stale/invalid callbacks.
- `scripts/parse_design_context.py` — Parse MCP context files, download asset URLs, and normalize SVG stretch issues.
- `scripts/fetch_figma_rest.py` — Extract node metadata + images via Figma REST API (needs `FIGMA_TOKEN`), with quota-aware batching, retry-after guardrail, metadata-only degradation, and local cache reuse.
- `scripts/figma_to_css.py` — Auto-parse REST `nodes.json` → CSS property blocks.
- `scripts/visual_diff.py` — Compare render vs target with MAE + SSIM + heatmap.

## References

- `references/figma-mcp-usage.md` — Figma MCP tools reference, setup, auth modes, and batch usage.
- `references/css-extraction-rules.md` — Strict property mapping and non-negotiable CSS extraction rules.
- `references/file-structure.md` — Standard project directory layout.
- `references/css-patterns.md` — Reusable CSS patterns for common design elements.
- `references/anti-patterns.md` — Full anti-pattern checklist for QA passes.
