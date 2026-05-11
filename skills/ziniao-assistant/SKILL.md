---
name: ziniao-assistant
description: Control Ziniao Browser via the local Ziniao bridge. On skill load or before first invoke, GET /zclaw/tools and treat returned name list as the only allowed tool strings; then POST /zclaw/tools/invoke. API key for invoke via ~/.zclaw/config.json or ZCLAW_API_KEY. On bridge failure stop the turn per skill.
---
# Ziniao Assistant

## Session tool allowlist (Mandatory — fetch first)

**Goal:** Put the **authoritative** tool names into context before any `invoke`, so every `tool` field is chosen from that set only (reduces hallucinated names).

1. **First HTTP call** when handling a ZClaw task (or immediately after this skill is loaded):  
   **`GET {baseUrl}/zclaw/tools`**  
   Same `baseUrl` as invoke (`ZCLAW_BASE_URL` / `ZINIAO_ZCLAW_BASE_URL`, default `http://127.0.0.1:9481`).  
   **No `X-ZClaw-Api-Key` and no Ziniao login are required** for this GET (public registry on the bridge).

2. **Parse the response:** JSON shape `{ ret, data }` where `data` is an array of `{ name, description, inputSchema }`. Build  
   **`allowedTools = data.map((t) => t.name)`**  
   and **retain it in working memory** for the session. Optionally keep `description` / `inputSchema` next to each name when choosing args.

3. **Before every `POST {baseUrl}/zclaw/tools/invoke`:** ensure **`allowedTools.includes(tool)`**. If the name you intend is not in `allowedTools`, **do not send the request**—map the user’s intent to a real name from `allowedTools` (e.g. open URL → `visit_page` or `open_store` + `launchUrl`).

4. **If `invoke` returns an error** like unsupported / unknown tool: re-run **`GET /zclaw/tools`**, refresh `allowedTools`, and retry with a valid `name`.

5. **If `GET /zclaw/tools` fails** (connection refused, timeout): follow **Stop on Blocker** for unreachable bridge; if you must proceed with static knowledge only, use the **Static fallback allowlist** below—still **no** invented names.

### Static fallback allowlist (when GET is impossible)

Comma-separated `tool` names that match a healthy bridge (re-sync when GET works):

`list_stores`, `resolve_store`, `open_store`, `close_store`, `visit_page`, `get_page_content`, `query_elements`, `click_element`, `input_text`, `scroll_page`, `take_screenshot`, `wait_for_element`, `wait_for_navigation`, `execute_script`, `run_automation`, `extract_data`, `prepare_agent`, `get_logs`, `download_file`, `debug_compare_lists`

---

## Available Capabilities

All **`invoke`** operations use `POST {baseUrl}/zclaw/tools/invoke` with `tool` + `args`. **Authoritative names** come from **`GET /zclaw/tools`** (see above); the table below is documentation aligned with that registry.

| Category | Tool | Description |
|----------|------|-------------|
| **Store** | `list_stores` | List stores (storeId, storeName, platformName, ip). Call once; no loop. |
| | `resolve_store` | Resolve store by storeId or storeName. |
| | `open_store` | Open store (by storeId/storeName from list or resolve). Call once. |
| | `close_store` | Close store by storeId. |
| **Page** | `visit_page` | Navigate to URL, optional waitUntil/timeout. |
| | `get_page_content` | Read page content (text/html/structured). |
| **Interaction** | `query_elements` | Query DOM by selector. |
| | `click_element` | Click element by selector, optional waitForNavigation. |
| | `input_text` | Type into element; optional clear, submit. |
| | `scroll_page` | Scroll page or element. |
| | `take_screenshot` | Screenshot (full page or viewport). |
| **Waiting** | `wait_for_element` | Wait for selector. |
| | `wait_for_navigation` | Wait for navigation. |
| **Automation** | `execute_script` | Run JavaScript in page. |
| | `run_automation` | Multi-step automation (steps array). |
| | `extract_data` | Extract metadata / page state; mode=running lists launched stores. |
| **Utilities** | `prepare_agent` | Prepare agent resources. |
| | `download_file` | Write content to Downloads (content, filename). |
| | `get_logs` | Get bridge logs. |
| **Debug** | `debug_compare_lists` | Debug: compare account/list vs store/list (optional; in GET /zclaw/tools registry). |

**Do not use:** `run_script` → use `execute_script`; `screenshot` / `get_screenshot` → use `take_screenshot`; `execute_automation` → use `run_automation`.

---

## Tool names: no hallucination (Mandatory)

The bridge **only** accepts the `tool` strings listed in **Core Tools** below. There is no separate “navigate API”, “browser API”, or “store tool” namespace—everything is one `POST .../zclaw/tools/invoke` body field `tool`.

**You MUST NOT** invent or guess tool names from general automation habits (Playwright, Selenium, browser-use, etc.). If a name is not in Core Tools, it **does not exist**.

**These and similar names are INVALID** (will fail or be rejected): `navigate`, `navigation`, `go_to`, `goto`, `open_url`, `openUrl`, `goto_url`, `load_url`, `browse`, `open_page`, `openPage`, `call_store_tool`, `store_tool`, `browser_navigate`, `visit`, `goto_tab`, `switch_tab` (as a tool name—use `visit_page` / `open_store` instead).

**Opening a URL in a store—only two supported ways:**

1. **`visit_page`** — args: `storeId`, `url` (and optional `waitUntil`, `timeoutMs`, `targetId`). Use after the store is already open.
2. **`open_store`** — args: `storeId` or `storeName`, and optional **`launchUrl`** so the first tab opens that URL when the store starts.

Do not chain imaginary tools before trying `visit_page` or `open_store` + `launchUrl`.

---

## API: How to Invoke Tools (Required)

**All tools are invoked through one endpoint only.** Do not call other paths.

- **Discover tools (no auth):** `GET {baseUrl}/zclaw/tools` — use first; see **Session tool allowlist**.
- **Method and path:** `POST {baseUrl}/zclaw/tools/invoke` (e.g. `POST http://127.0.0.1:9481/zclaw/tools/invoke`). Base URL from `ZCLAW_BASE_URL` or `ZINIAO_ZCLAW_BASE_URL` (default `http://127.0.0.1:9481`).
- **Auth is mandatory for invoke:** Every `POST {baseUrl}/zclaw/tools/invoke` **must carry API key credentials**. Preferred header: `X-ZClaw-Api-Key: <key>`. Also accepted: body `apiKey`, or `Authorization: Bearer <key>` (compatibility only). **Never send invoke without key.**
- **Request body (JSON):** `{ "tool": "<name>", "args": { ... } }`. Optional: `"action": "json"`.
- **`tool`** must be exactly one of the tool names in the **Core Tools** list below (e.g. `list_stores`, `visit_page`, `get_page_content`, `click_element`, `take_screenshot`, `execute_script`, `run_automation`). Wrong names (e.g. `run_script`, `screenshot`) or custom paths will fail.
- **Do not** call paths like `/zclaw/page/execute`, `/zclaw/page/visit`, `/zclaw/page/click`, etc. Every tool call must be `POST /zclaw/tools/invoke` with the correct `tool` name in the body.

### Invoke Auth Examples (Mandatory)

**Correct (preferred):**

```bash
curl -X POST http://127.0.0.1:9481/zclaw/tools/invoke \
  -H "Content-Type: application/json" \
  -H "X-ZClaw-Api-Key: <ZCLAW_API_KEY>" \
  -d '{"tool":"open_store","args":{"storeName":"Rosehut"}}'
```

**Also accepted (compatibility):**

```bash
curl -X POST http://127.0.0.1:9481/zclaw/tools/invoke \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <ZCLAW_API_KEY>" \
  -d '{"tool":"open_store","args":{"storeName":"Rosehut"}}'
```

**Invalid (must not generate):** no API key in header/body.

## When To Use

Use when the user wants to operate Ziniao Browser or configure the Ziniao bridge (list stores, open store, visit pages, read content, click, input, screenshot, export, automation). When a task has multiple similar sub-items (e.g. several order types or reports), visit or check each one separately before concluding; do not infer from a subset.

## Stop on Blocker (Mandatory — Enforced First)

**Trigger:** Any of: (a) `POST {baseUrl}/zclaw/tools/invoke` fails with connection refused, timeout, or no response; (b) a required tool call returns an error that makes the task impossible; (c) a required resource (e.g. store not found, API key missing) is missing.

**You MUST:**

1. **Stop immediately.** Do not retry the same request. Do not read more code, grep, or open other files to "diagnose" or "work around". Do not design or write "run these steps when the bridge is up" or any follow-up plan.
2. **End the turn.** Do not speculate on other causes, suggest code changes, or continue the task. Connection or tool failure means the task is not executable—stop only. (User-facing messages for unreachable bridge are handled by the software.)

## Hard Constraints

- **Stop on blocker:** If the bridge is unreachable or a required tool call fails, stop and end the turn; do not retry, read code, or create templates or follow-up plans. See "Stop on Blocker" above.
- **Invoke must include API key:** Every `POST /zclaw/tools/invoke` request must include API key credentials (`X-ZClaw-Api-Key` preferred; or body `apiKey`; or `Authorization: Bearer <key>`). Do not generate keyless invoke commands.
- **No script files:** Do not create or run any scripts (`.sh`/`.js`/`.py` or other code files) to execute tasks; use only the tools in **Core Tools** via `POST /zclaw/tools/invoke`. **Temporary files are allowed** (e.g. intermediate data, content for `download_file`); **script/executable files are not.**
- All browser actions must stay inside **Ziniao Browser** or a Ziniao store exposed by the bridge. Do not open system browser, Chrome, Safari, Edge, Firefox, or use Playwright/Puppeteer/browser-use when the bridge fails.
- Use only the tools in **Core Tools**. Do NOT use: `run_script` (use `execute_script`), `screenshot` or `get_screenshot` (use `take_screenshot`), `execute_automation` (use `run_automation`), or any tool not listed there. Do NOT invent `navigate`, `open_url`, `call_store_tool`, or any name not in Core Tools.
- Prefer tool-based flow: open store (optionally with `launchUrl`) → **`visit_page`** for further URLs → get_page_content / query_elements / click_element / input_text / take_screenshot / download_file / run_automation. Use `execute_script` only for in-page JavaScript (e.g. DOM extraction), not for orchestration.

## API Key: Configure via Conversation (Preferred)

**The user can configure the API key by sending it in the conversation.** When the user provides an API key (e.g. pastes it, or says “设置 API key 为 xxx”, “my API key is znoc_xxx”, “configure ZCLAW_API_KEY: xxx”), you MUST:

1. **Write the key to the config file** the skill reads from:
   - **macOS / Linux:** `~/.zclaw/config.json`
   - **Windows:** `%USERPROFILE%\.zclaw\config.json` (e.g. `C:\Users\<YourName>\.zclaw\config.json`)
   Create the `.zclaw` directory if it does not exist. File content: JSON with at least `"ZCLAW_API_KEY": "<the key the user provided>"`. If the file already exists, **merge**: update `ZCLAW_API_KEY` and keep other keys (e.g. `ZCLAW_BASE_URL`) unchanged.
2. **Immediately use this new API key** for all subsequent `POST /zclaw/tools/invoke` requests in this conversation. Do not wait for a reload; treat the key you just wrote as the current key. If the user provides a new key again later, write again and switch to the new key for the rest of the conversation.

Writing the config file is allowed for API key setup only (creating/updating `~/.zclaw/config.json`). Do not create or run scripts; use normal file write to that path.

## API Key: Read into Context (Required)

When this skill is used, **load the API key into the conversation context** so every request (including the first) can authenticate. Use this order (Ziniao and ZClaw both use **ZCLAW_API_KEY**):

1. **User just provided in this conversation** — if you have just written the key to the config per “API Key: Configure via Conversation”, use that key for all requests.
2. **Environment variable** `ZCLAW_API_KEY` — use if set.
3. **Config file** `~/.zclaw/config.json` — if the key is not in env and not set in conversation, read `ZCLAW_API_KEY` from this JSON file (e.g. `{ "ZCLAW_API_KEY": "your-key" }`).

Use the resolved key for all `POST /zclaw/tools/invoke` requests (e.g. header `X-ZClaw-Api-Key` or body `apiKey`). Optionally `ZCLAW_BASE_URL` or `ZINIAO_ZCLAW_BASE_URL` (default `http://127.0.0.1:9481`).

Do this at skill load or at the start of the conversation so the key is available and the first tool call does not fail with "Missing bearer token". **After the user configures a new key via conversation, update to the new key immediately** for the rest of the turn.

## Environment & Setup

- **API key**: Env `ZCLAW_API_KEY`, or `ZCLAW_API_KEY` in `~/.zclaw/config.json` (see path note below). The bridge also accepts the key via header `X-ZClaw-Api-Key` or body `apiKey`.
- **Base URL**: `ZCLAW_BASE_URL` or `ZINIAO_ZCLAW_BASE_URL` (default `http://127.0.0.1:9481`).
- **First time / Rotate key**: Obtain a ZClaw API key from your **server or [Ziniao Ecosystem Center](https://open.ziniao.com/contactUs)** (there is no API key generation in the app settings). You can **(1) configure via conversation** — tell the assistant your API key and it will write it to `~/.zclaw/config.json` and use it immediately; or **(2)** set `ZCLAW_API_KEY` in your environment or in `~/.zclaw/config.json`; or **(3)** run `bash ziniao-skills/install-ziniao-openclaw-skill.sh "YOUR_API_KEY"` (Windows: use `install-ziniao-openclaw-skill.ps1` with `-ApiKey`). After configuring via conversation, the assistant uses the new key for all subsequent requests in that conversation.

**Reading the key:** The bridge uses `process.env.ZCLAW_API_KEY`, which works on **Windows, macOS, and Linux**. The variable must be present in the environment of the process that runs the app (Ziniao/Electron). If the app is started from the GUI (e.g. Dock, Start menu), only **system/user environment variables** are visible; shell-only exports (e.g. in a terminal) are not. To ensure the key is always available on all platforms, you can use the config file instead of env.

**Setting `ZCLAW_API_KEY` by OS:**

- **macOS / Linux**: (1) **Config file (recommended):** `~/.zclaw/config.json` with `{ "ZCLAW_API_KEY": "your-key" }` (same path on both). (2) **Env:** In the same shell that starts the app: `export ZCLAW_API_KEY=your-key`. For GUI launches, add `export ZCLAW_API_KEY=...` to `~/.bashrc`, `~/.zshrc`, or `~/.profile`, or set it system-wide (e.g. `/etc/environment` on Linux).
- **Windows**: (1) **Config file (recommended):** `%USERPROFILE%\.zclaw\config.json` (e.g. `C:\Users\YourName\.zclaw\config.json`) with `{ "ZCLAW_API_KEY": "your-key" }`. (2) **Env:** System Properties → Environment Variables → add User or System variable `ZCLAW_API_KEY`; or in PowerShell (current user): `[Environment]::SetUserVariable("ZCLAW_API_KEY","your-key")`. Restart the app after changing system env.

**Invocation:** This skill is designed for use with the ZClaw framework (recommended). The Ziniao bridge is an HTTP API; any client that can send requests with a valid API key can call the same tools.

## Store Resolution and Opening: Validation and Response Contract

**Getting and opening stores** follows Ziniao’s existing validation and launch flow: store detail (e.g. `default_browser`, `platform`) is fetched via **store/detail** when launching; the browser is then started using the same logic as the client.

**ZClaw responses** are filtered by convention and do not expose full Ziniao store details: **open_store** returns only **storeId**, **name**, **debugPort**, **reused**, etc.; **list_stores** returns only **storeId**, **storeName**, **platformName**, **ip**. **ZClaw does not expose full store detail**; it only exposes status for stores launched via ZClaw. The running-stores list (e.g. **extract_data** with `mode=running` or the running-stores API) contains only **storeId**, **storeName**, **debugPort**, **wsUrl**.

If **open_store** or **visit_page** returns 400 "Store detail not found", the backend **store/detail** API or its response shape may be failing; the bridge tries several response paths and, when present, includes the server’s `msg` in the error.


## No Extra Scripts (Mandatory)

**You must not create or use any scripts to execute tasks.** All actions must be performed only through the tools listed in **Core Tools**. Do not:

- Create or run Node.js, shell, Python, or other script files (e.g. `.sh`, `.js`, `.py`) to accomplish the task.
- Invoke external commands or scripts for steps that the tools can do (list stores, open store, visit page, click, input, screenshot, download_file, run_automation, etc.).

**Temporary files are allowed** during the run (e.g. temporary data files, intermediate content to pass to `download_file`, or scratch files). **Script files are not allowed** — do not create or execute any file intended to be run as code. Use only `POST /zclaw/tools/invoke` with the tool names and args from Core Tools. If something cannot be done with the existing tools, report the limitation instead of scripting around it.

## Store List and Opening (Mandatory)

- **No looping:** Call `list_stores` at most once to get data; then call `open_store` once. Do not repeatedly call list in a cycle.
- **To open a store:** (1) Get **storeId** — either from one `list_stores` (use the item whose `storeName` matches the user’s store) or from one `resolve_store(storeName)`; (2) Call `open_store` once with that `storeId` or with `storeName` (exact string from the list).
- **list_stores response:** Each item has exactly: `storeId`, `storeName`, `platformName`, `ip`. Use **`storeName`** when calling `resolve_store` or `open_store` (exact match). Do not use other fields as the store name.

## Recommended Workflow

0. **Allowlist:** `GET /zclaw/tools` → keep `allowedTools` (and schemas) in context; every `invoke` uses `tool` ∈ `allowedTools`.
0.5. **Auth:** Resolve API key first (`conversation-provided` > env `ZCLAW_API_KEY` > `~/.zclaw/config.json`) and include it in **every** invoke request.
1. **Store:** One `list_stores` or one `resolve_store` → get `storeId` / `storeName` → one `open_store` (pass **`launchUrl`** if the user gave a target URL up front—avoids a second navigation step). Match by `storeName` from list; if ambiguous, ask user or use exact `storeId`. No fuzzy/substring matching.
2. **Page:** If the store is open and you need a URL: **`visit_page`** only (`storeId` + `url`). Never use `navigate`, `open_url`, or other non-listed tool names. Then use `get_page_content`, `query_elements`, `click_element`, `input_text`, `take_screenshot`, `download_file` as needed; prefer `run_automation` for multi-step flows.
3. **Errors:** Use `get_logs` on failure; after API key rotation, update config and refresh skills.
4. **Multiple similar items:** When a task involves multiple similar sub-items (e.g. several order types, several reports), visit or check **each item separately** before drawing a conclusion; do not infer "all have no data" or "all behave the same" from only a subset.

## Core Tools

**Only these tools exist.** Use exactly these names as the `tool` field in `POST /zclaw/tools/invoke`; put parameters in `args`. Do not use or invent other tool names or other URLs.

Pass one arguments object per call (as `args`); required keys must be present. When running ZClaw tasks, the bridge operates on the correct tab but **does not bring the browser window to the front**, so your other windows and work are not interrupted.

### Store Management
- **list_stores** — List stores (call once; no loop). **Response:** `{ page, limit, total, items }` where each item has `storeId`, `storeName`, `platformName`, `ip`. Use `storeName` for resolve/open. Args: `page?`, `limit?`, `all?`, `filterKeyword?`, `storeListType?`.
- **resolve_store** — Resolve by exact storeId or storeName. Args: `storeId?`, `storeName?`, `expectedName?`. Returns `storeId` and `name` for `open_store`.
- **open_store** — Open store (need storeId from list_stores or resolve_store). Uses store/detail + launch. Returns (filtered): storeId, name, debugPort, reused, and optionally status, windowHandler, launchUrl. Call once. Args: `storeId?`, `storeName?` (use list item `storeName`), `expectedName?`, `launchUrl?`, `isHeadless?`, `privacyMode?`, `windowRatio?`.
- **close_store** — Close store. Args: `storeId` (required).

### Page Navigation & Content
- **visit_page** — Navigate and wait. Args: `storeId`, `url`; optional `waitUntil` (domcontentloaded|load|networkidle), `timeoutMs`, `targetId`.
- **get_page_content** — Read page content. Args: `storeId`; optional `format` (text|html|structured), `timeoutMs`, `targetId`.

### Page Interaction
- **query_elements** — DOM by selector. Args: `storeId`, `selector`; optional `timeoutMs`, `targetId`.
- **click_element** — Click. Args: `storeId`, `selector`; optional `waitForNavigation`, `timeoutMs`, `targetId`.
- **input_text** — Type into element. Args: `storeId`, `selector`, `text`; optional `clear`, `submit`, `timeoutMs`, `targetId`.
- **scroll_page** — Scroll. Args: `storeId`; optional `x`, `y`, `selector`, `behavior` (auto|smooth), `timeoutMs`, `targetId`.
- **take_screenshot** — Screenshot (not `screenshot`). Args: `storeId`; optional `fullPage`, `path`, `timeoutMs`, `targetId`.

### Page Waiting
- **wait_for_element** — Wait for selector. Args: `storeId`, `selector`; optional `timeoutMs`, `targetId`.
- **wait_for_navigation** — Wait for navigation. Args: `storeId`; optional `timeoutMs`, `targetId`.

### Automation & Scripting
- **execute_script** — Run JS in page (not `run_script`). Args: `storeId`, `script`; optional `timeoutMs`, `targetId`.
- **run_automation** — Multi-step flow. Args: `steps` (array of `{ type, ... }`).
- **extract_data** — Extract metadata or page state. Use `mode=running` to list launched stores (returns only `storeId`, `storeName`, `debugPort`, `wsUrl`); `mode=store` returns that store’s launch status only (no store detail). Args: `mode?` (store|running|plugin|page), `storeId?`, `payload?`.

### Utilities
- **prepare_agent** — Prepare agent resources.
- **download_file** — Write to Downloads. Args: `content`, `filename`.
- **get_logs** — Bridge logs.

### Debug
- **debug_compare_lists** — Compare account/list vs store/list (debug). Args: `limit?`.

Invalid tool names (will fail): `run_script`, `screenshot`, `get_screenshot`, `execute_automation` — use `execute_script` and `take_screenshot`, `run_automation` instead. Also invalid: any name in **Tool names: no hallucination** (e.g. `navigate`, `open_url`, `call_store_tool`).
