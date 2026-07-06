# Telegram File Browser Interaction Patterns

## 0. Explicit skill invocation

If the user explicitly asks to use `telegram-file-browser`, open the browser UI immediately.

Recommended default root:
- `~/.openclaw/workspace` for OpenClaw-local browsing
- otherwise the explicitly requested root

Do not stop at describing the skill unless the user asked for documentation rather than execution.

## 1. Display mode configuration

Support a persisted browser config in `config.json`.

Recommended command-style entry:
- `/telegram_file_browser config`

Recommended options:
- `edit-message`
- `new-message`

Behavioral rule:
- in `new-message` mode, directory navigation and file-action transitions should send a fresh menu message instead of editing the current one
- once the send succeeds, the new message becomes the live menu id for subsequent callbacks

Use `scripts/browser_config.py` to read and write this configuration instead of ad-hoc temporary scripts.

## 2. Single-message navigation

Preferred behavior:
- one live menu message
- all directory navigation edits that message in place
- previews and copyable outputs are separate messages

Why:
- avoids chat clutter
- preserves user orientation
- feels closer to a real browser panel

## 2. File actions

For files, use a second-level action menu instead of opening content immediately.

Recommended actions:
- `👁 预览`
- `📋 路径`
- `⬇️ 下载`
- `⬅️ 返回`
- `❌ 关闭`

Default rule:
- clicking a file in a directory view should open the file action menu
- it should not immediately dump a preview unless the user explicitly asked for instant preview behavior

This gives the user intent-level control before producing extra output.

## 3. Download behavior

For downloadable files:
1. user clicks `⬇️ 下载`
2. send the local file as a Telegram attachment
3. keep the menu message alive

If the target is not a file, fail with a short message instead of breaking the browser state.

## 4. Copyable path behavior

Telegram buttons cannot directly write to the client clipboard.

Best practical pattern:
1. user clicks `📋 路径`
2. send a new message containing only the path
3. user long-presses to copy

Keep the message plain and short.

Good:

```text
~/Workspace/justcj-skills/.git/config
```

Less good:
- wrapping in lots of commentary
- mixing path with explanation text

## 4. Pagination

Use pagination when a directory is too large to fit comfortably in one menu.

Recommended controls:
- `⬅️ 上一页`
- `➡️ 下一页`
- `⬆️ 上级目录`
- `❌ 关闭`

Keep the page state in local view state, not in the path itself.

## 5. Callback replay protection

Use menu-versioned callback payloads such as `tfb_preview_v3_w10`.

Rules:
- if callback version != current state menuVersion, ignore it as stale
- if the same callback arrives again within a short debounce window, ignore it as duplicate
- do not let old `下载` callbacks survive after the menu has already changed state

This prevents repeated queued callback events from making the UI feel haunted.

## 6. Error recovery

If message edit fails:
- if the message was deleted or cannot be edited, send a fresh menu
- update the stored live message id
- preserve the current path and stack if possible

If a file or directory no longer exists:
- edit the menu with a short error message
- keep `⬅️ 返回` available

## 6. Suggested sorting

Use:
1. directories first
2. files second
3. case-insensitive alphabetical order within each group

This matches user expectations for a file browser.

## 7. Suggested preview policy

For text files:
- preview the first useful chunk
- avoid dumping extremely large content by default
- mention truncation when applicable

For binary or unsupported files:
- show metadata or offer path only

## 8. State model

Track at least:
- root
- current path
- stack
- live message id
- current view item map

Without this, navigation quickly becomes brittle.

Implementation note:
- prefer `scripts/run_browser_action.py` as the first runtime entrypoint
- prefer `scripts/browser_controller.py` as the browser coordinator behind it
- prefer `scripts/file_browser_state.py` for state persistence
- prefer `scripts/build_view.py` for directory enumeration and pagination
- prefer `scripts/render_buttons.py` for stable Telegram button layout generation
- prefer `scripts/resolve_callback.py` for callback routing
- prefer `scripts/preview_file.py` for file preview generation
