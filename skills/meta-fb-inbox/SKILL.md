---
name: meta-fb-inbox
description: Check Facebook page inbox messages via Meta Business Suite browser automation. Use when asked to check Facebook messages, reply to FB customers, or manage Facebook page inbox. Supports multiple pages with custom aliases.
---

# Meta Facebook Inbox

⚠️ **CRITICAL**: Always use `profile:"openclaw"` (isolated browser) for all browser actions. Never use Chrome relay. Keep the same `targetId` across operations to avoid losing the tab.

⚠️ **CONTEXT Management**:
- Snapshot results are large. Do NOT repeat them in thinking.
- Extract needed info and process immediately.
- **Preferred approach**: Use `snapshot refs:"aria" compact:true` to find element refs, then `act` + `click`/`type` with ref.

## Configuration

Before first use, check if `config.json` exists:
```
read file_path:"skills/meta-fb-inbox/config.json"
```

⚠️ **PATH RULE**: Always use workspace-relative paths starting from `skills/meta-fb-inbox/`. Never use `../` or absolute paths.

If missing or empty, help the user run the setup wizard:
```bash
cd skills/meta-fb-inbox
node scripts/setup.js
```

### Config Format

`config.json` contains a `pages` array. Each page has an `alias` (display name) and `url` (Meta Business Suite inbox URL):
```json
{
  "pages": [
    {
      "alias": "fb fanpage",
      "url": "https://business.facebook.com/latest/inbox/all/?&asset_id=123456789012345"
    },
    {
      "alias": "fb fanpage 2",
      "url": "https://business.facebook.com/latest/inbox/all/?&asset_id=987654321098765"
    }
  ]
}
```

### Resolving a Page

When the user asks to check messages:
- If they specify an alias (e.g. "fb fanpage 2"), look it up in `config.json` → `pages`.
- If they don't specify, use the **first** page in the array.
- If only one page exists, use it directly.
- If multiple pages exist and no alias given, list available aliases and ask which one.

## Enter Facebook Inbox

This is the first step for all operations below.

1. **Check and start browser service:**
   ```
   browser action:"status"
   ```
   If `"running": false`, start the browser service:
   ```
   browser action:"start" profile:"openclaw"
   ```
   Wait 2-3 seconds for the service to initialize.

2. **Read config to get the target page URL:**
   ```
   read file_path:"skills/meta-fb-inbox/config.json"
   ```
   Resolve the page alias to a URL (see "Resolving a Page" above).

3. **Open browser:**
   ```
   browser action:"open" profile:"openclaw" targetUrl:"<pageUrl>"
   ```
   Capture `targetId` and `url` from response.

4. **Wait for page load:**
   ```
   browser action:"act" profile:"openclaw" targetId:"<targetId>" request:{"kind":"wait","timeMs":3000}
   ```

5. **Check login state:**
   ```
   browser action:"act" profile:"openclaw" targetId:"<targetId>" request:{"kind":"evaluate","fn":"function(){return window.location.href;}"}
   ```

   - If URL contains `business.facebook.com` and shows the inbox → logged in, proceed.
   - If redirected to a login page → notify the user they need to log in manually in the OpenClaw browser, then retry.

6. **Proceed with the user's request.**

7. **Clean Up Browser Tabs** (after all operations):

   a. Open a blank tab:
   ```
   browser action:"open" profile:"openclaw" targetUrl:"about:blank"
   ```

   b. Get all tabs:
   ```
   browser action:"tabs" profile:"openclaw"
   ```

   c. Close all tabs except the newest one (about:blank):
   ```
   browser action:"close" profile:"openclaw" targetId:"<your_targetId>"
   ```

## Quick Check (for cron / automated checks)

Complete flow: open page → screenshot → report.

1. Read config: `read file_path:"skills/meta-fb-inbox/config.json"` → resolve page URL
2. Start browser if needed: `browser action:"start" profile:"openclaw"`
3. Open page: `browser action:"open" profile:"openclaw" targetUrl:<pageUrl>` → get `targetId`
4. Wait: `browser action:"act" profile:"openclaw" targetId:<targetId> request:{"kind":"wait","timeMs":4000}`
5. Check URL to verify login (see step 5 above)
6. Take snapshot: `browser action:"snapshot" profile:"openclaw" targetId:<targetId> refs:"aria" compact:true`
7. Look for conversation items in the inbox list. Each conversation typically shows:
   - Customer name
   - Last message preview
   - Timestamp
   - Unread indicator (bold text or dot)
8. Report results in format: `<name> (<time>) <preview> [未讀/已讀]`
9. Clean up tabs.

If the snapshot is hard to parse (Meta's DOM is complex), fall back to:
```
browser action:"screenshot" profile:"openclaw" targetId:<targetId>
```
Then describe what you see in the screenshot.

## Check Inbox Messages

1. Follow "Enter Facebook Inbox" steps to get to the inbox page.
2. Take a snapshot or screenshot to see the conversation list.
3. Report conversations with name, time, preview, and read/unread status.

### Get URLs for Conversations (取得對話網址 - Simple!)

**Why get URLs?** Having the direct conversation URL lets you jump straight to a chat later without searching for it again. Saves time when replying.

**When to get URLs:** After listing chats, get URLs for unread conversations or any conversation you might need to access again.

**📝 Simple 3-Step Method:**

1. **Click into the conversation** using the customer name:
   ```
   browser action:"act" profile:"openclaw" targetId:"<targetId>" request:{"kind":"evaluate","fn":"function() { const containers = document.querySelectorAll('div[style*=\"position: absolute\"]'); for (let container of containers) { const nameEl = container.querySelector('div.x1vvvo52.x1fvot60.xxio538'); if (nameEl && nameEl.textContent.trim() === '<customer_name>') { nameEl.click(); return {clicked: true}; } } return {error: 'not found'}; }"}
   ```
   Replace `<customer_name>` with the actual customer name from your conversation list.

2. **Wait 2 seconds for page to load and URL to update:**
   ```
   browser action:"act" profile:"openclaw" targetId:"<targetId>" request:{"kind":"wait","timeMs":2000}
   ```

3. **Get the current URL - it's automatically updated!**
   ```
   browser action:"act" profile:"openclaw" targetId:"<targetId>" request:{"kind":"evaluate","fn":"function(){return window.location.href;}"}
   ```

4. **Store the URL** alongside the chat info.

**✅ Example URL Format:**

```
https://business.facebook.com/latest/inbox/all/?&asset_id=123456789012345&selected_item_id=1234567890&thread_type=FB_MESSAGE
```

Or with optional mailbox_id:
```
https://business.facebook.com/latest/inbox/all/?&asset_id=123456789012345&mailbox_id=123456789012345&selected_item_id=9876543210&thread_type=FB_MESSAGE
```

**🔍 Understanding the URL:**
- `asset_id` = Your Facebook page ID (stays the same)
- `selected_item_id` = Unique conversation ID (different for each customer)
- `thread_type=FB_MESSAGE` = Messenger conversation type
- `mailbox_id` = Optional, may appear for some conversations

**💾 How to Use Later:**

Next time you need to access this conversation, skip all the searching:
```
browser action:"navigate" profile:"openclaw" targetId:"<targetId>" targetUrl:"<saved_conversation_url>"
```
Wait 2 seconds, and you're in the conversation!

**💡 Tip:** Get URLs for unread messages during your check routine, store them in a file or memory, and reuse them for instant access.

**🔄 Getting Multiple URLs:**

If you need URLs for multiple conversations:
1. Get URL for first conversation (steps 1-3 above)
2. Navigate back to inbox list:
   ```
   browser action:"navigate" profile:"openclaw" targetId:"<targetId>" targetUrl:"<pageUrl>"
   ```
   Wait 2 seconds.
3. Repeat for next conversation.

**Alternative method (when already in conversation):**
If you're already viewing a conversation and just need its URL, skip step 1 and directly run step 3 - the URL is already there!

## View Specific Conversation

**⚡ Fast Path:** If you have the conversation URL from "Get URLs for Conversations":
```
browser action:"navigate" profile:"openclaw" targetId:"<targetId>" targetUrl:"<conversation_url>"
```
Wait 2 seconds, then skip to step 3.

**Standard Path:**

1. From the inbox list, find and click the conversation (use snapshot + click by ref).
2. Wait for messages to load (2-3 seconds).
3. Take a screenshot to see the message thread.
4. Report the messages with sender, time, and content.

### Extract Messages with Images

To programmatically read messages:

1. **Navigate to the conversation** (if not already there).
2. **Inject the read-messages script:**
   ```
   browser action:"act" profile:"openclaw" targetId:"<targetId>" request:{"kind":"evaluate","fn":"<contents_of_scripts/read-messages.js>"}
   ```
   Read the script file:
   ```
   read file_path:"skills/meta-fb-inbox/scripts/read-messages.js"
   ```
   And pass its entire contents as the `fn` parameter (wrapped in parentheses).

3. **Parse the response:**
   The script returns an array of message objects:
   ```json
   [
     {"text": "你好", "isCustomer": true, "hasImage": false, "imageUrl": null},
     {"text": "[Image]", "isCustomer": true, "hasImage": true, "imageUrl": "https://scontent-..."}
   ]
   ```

4. **Download images (if any):**
   
   ⚠️ **Default download location**: `~/Downloads` (do NOT clutter the workspace).
   
   For each message with `hasImage: true`:
   ```bash
   cd ~/Downloads
   curl -O "<imageUrl>"
   ```
   
   The downloaded file will use the original filename from the URL.
   
   If you want a custom filename:
   ```bash
   cd ~/Downloads
   curl -o "fb-message-$(date +%Y%m%d-%H%M%S).jpg" "<imageUrl>"
   ```

## Reply to a Message

**⚡ Fast Path (if you have conversation URL):**

If you already obtained the conversation URL from "Get URLs for Conversations" section, skip step 1 and go directly:

```
browser action:"navigate" profile:"openclaw" targetId:"<targetId>" targetUrl:"<conversation_url>"
```

Wait 2 seconds, then proceed to step 2 (Take snapshot to find input box).

**Standard Path (when you don't have the URL):**

1. **Open the conversation:**
   
   Click the customer name in the conversation list:
   ```
   browser action:"act" profile:"openclaw" targetId:"<targetId>" request:{"kind":"evaluate","fn":"function() { const containers = document.querySelectorAll('div[style*=\"position: absolute\"]'); for (let container of containers) { const nameEl = container.querySelector('div.x1vvvo52.x1fvot60.xxio538'); if (nameEl && nameEl.textContent.trim() === '<customer_name>') { nameEl.click(); return {clicked: true}; } } return {error: 'not found'}; }"}
   ```
   Replace `<customer_name>` with the actual customer name.
   
   Wait 2 seconds for the conversation to load.

2. **Take a snapshot to find the input box:**
   ```
   browser action:"snapshot" profile:"openclaw" targetId:"<targetId>" refs:"aria" compact:true
   ```
   Look for `textbox` with `[active]` attribute.

3. **Type the reply message:**
   ```
   browser action:"act" profile:"openclaw" targetId:"<targetId>" request:{"kind":"type","ref":"<input_ref>","text":"<your_message>"}
   ```
   After typing, wait 1 second for the send button to appear.

4. **Take another snapshot to find the send button:**
   ```
   browser action:"snapshot" profile:"openclaw" targetId:"<targetId>" refs:"aria" compact:true
   ```
   Look for a new `button` near the textbox. The send button appears after you type text (it replaces the "like" button).

5. **Click the send button:**
   ```
   browser action:"act" profile:"openclaw" targetId:"<targetId>" request:{"kind":"click","ref":"<send_button_ref>"}
   ```

6. **Verify the message was sent:**
   
   Wait 2 seconds, then take a screenshot or check the conversation list to confirm the message appears.

## Manage Labels

**⚡ Fast Path:** If you have the conversation URL, navigate directly:
```
browser action:"navigate" profile:"openclaw" targetId:"<targetId>" targetUrl:"<conversation_url>"
```
Wait 2 seconds, then proceed to the label operations.

### Remove a Label

1. **Open the conversation** (if not already open, and you don't have URL).

2. **Take a snapshot to locate the label's remove button:**
   ```
   browser action:"snapshot" profile:"openclaw" targetId:"<targetId>" refs:"aria" compact:true
   ```
   
   Look for the Labels section in the right sidebar (appears before Notes section):
   - A `heading` with level=3 (the Labels heading)
   - Each label appears as a `button` element
   - Inside each label button, there's a nested `button` with text "clearLabel"
   - The clearLabel button is the "×" (remove) icon

3. **Click the clearLabel button:**
   ```
   browser action:"act" profile:"openclaw" targetId:"<targetId>" request:{"kind":"click","ref":"<clearLabel_ref>"}
   ```
   
   **Example from snapshot:**
   ```
   - heading [level=3] [ref=eAAA]        ← Labels heading
   - button [ref=e949]:                  ← Label button (shows label name)
       - button "clearLabel" [ref=e952]  ← Remove button (THIS ONE!)
   ```
   Click the clearLabel button (`ref=e952`) to remove the label.

4. **Wait for the change to apply:**
   ```
   browser action:"act" profile:"openclaw" targetId:"<targetId>" request:{"kind":"wait","timeMs":1500}
   ```

5. **Verify the label was removed** (optional):
   Take a screenshot or snapshot to confirm the label is gone.

### Add a Label

1. Open the conversation.
2. Take a snapshot to find the label input combobox:
   ```
   - combobox "label" [ref=eXXX]
   ```
3. Type the label name:
   ```
   browser action:"act" profile:"openclaw" targetId:"<targetId>" request:{"kind":"type","ref":"<combobox_ref>","text":"<label_name>","submit":true}
   ```
4. Wait and verify.

## Manage Notes (備註)

**⚡ Fast Path:** If you have the conversation URL, navigate directly:
```
browser action:"navigate" profile:"openclaw" targetId:"<targetId>" targetUrl:"<conversation_url>"
```
Wait 2 seconds, then proceed to the note operations.

### Quick Decision Guide (看這裡！)

**Question: Do you need to ADD or EDIT a note?**

1. Take a snapshot of the conversation sidebar.
2. Look for the Notes section (usually appears after Labels section).
3. Check what you see:

   - **ONLY see a "Add note" type button/link (single button, no existing note text)**
     → Contact has NO note → Use **"Add a New Note"** section below.

   - **See an "Edit" link + existing note text (usually with timestamp)**
     → Contact has existing note → Use **"Edit an Existing Note"** section below.

**Simple rule:** 
- No note = Add new (only one button visible)
- Has note = Edit existing (edit link + note text visible)

**How to identify in snapshot:**
- **No note**: Look for pattern like `button [ref=eXXX]` or `link [ref=eXXX]` with NO paragraph text nearby
- **Has note**: Look for pattern like `link [ref=eXXX]` (edit) + `link [ref=eYYY]` (delete) + `paragraph [ref=eZZZ]: "note text"`

### Note Structure

The Notes section is located below the Labels section in the right sidebar. There are two states:

1. **No note exists**: You will see a single button or link (typically the "add note" action).
2. **Note exists**: You will see:
   - The note text (in a `paragraph` element)
   - An Edit link (usually appears before the note text with timestamp)
   - A Delete link (next to edit link)
   - Sometimes an "add note" link (for additional notes, but we prefer single-note approach)

**Best Practice**: Keep only one note per contact. Use "Edit" to update existing notes rather than adding multiple notes.

**In snapshot, look for these patterns:**

No note:
```
- heading [level=3] [ref=eXXX]     ← Notes heading
- button [ref=eYYY]                 ← Single "add note" button
```

Has note:
```
- heading [level=3] [ref=eXXX]     ← Notes heading
- link [ref=eYYY]                   ← "add note" link
  - text: "X minutes ago ·"        ← Timestamp
  - link [ref=eZZZ]                 ← Edit link (THIS ONE for editing!)
  - text: "·"
  - link [ref=eAAA]                 ← Delete link
- paragraph [ref=eBBB]: "note text" ← Existing note content
```

### Edit an Existing Note (編輯註記 - Simple Steps for AI)

**When to use:** Contact already has a note. You will see an Edit link next to existing note text with timestamp.

**Step-by-step:**

1. **Open the conversation** (click customer name in chat list).
   Wait 2 seconds for it to load.

2. **Take snapshot** to find the Edit button:
   ```
   browser action:"snapshot" profile:"openclaw" targetId:"<targetId>" refs:"aria" compact:true
   ```
   Look for the pattern (Notes section):
   ```
   - heading [level=3] [ref=eAAA]           ← Notes heading
   - link [ref=eBBB]                        ← "add note" link
     - text: "4 hours ago ·"                ← Timestamp
     - link [ref=eXXX]                      ← Edit link (THIS ONE!)
     - text: "·"
     - link [ref=eYYY]                      ← Delete link
   - paragraph [ref=eZZZ]: "Customer note" ← Current note
   ```
   
   **Key**: Find the link that appears AFTER the timestamp text and BEFORE the "·" separator. That's your Edit button.

3. **Click Edit button:**
   ```
   browser action:"act" profile:"openclaw" targetId:"<targetId>" request:{"kind":"click","ref":"<edit_button_ref>"}
   ```

4. **Wait for edit form:**
   ```
   browser action:"act" profile:"openclaw" targetId:"<targetId>" request:{"kind":"wait","timeMs":1500}
   ```

5. **Take snapshot** to find the textbox:
   ```
   browser action:"snapshot" profile:"openclaw" targetId:"<targetId>" refs:"aria" compact:true
   ```
   Look for:
   ```
   - textbox [ref=eXXX]: "Customer note"  ← Current text (contains existing note)
   - button [ref=eYYY]                     ← Cancel button
   - button [ref=eZZZ]                     ← Delete button
   - button [disabled] [ref=eAAA]          ← Save button (disabled until you change text)
   ```
   
   **Key**: The textbox will have the current note text. The Save button will show `[disabled]` attribute.

6. **Click textbox to focus:**
   ```
   browser action:"act" profile:"openclaw" targetId:"<targetId>" request:{"kind":"click","ref":"<textbox_ref>"}
   ```

7. **Select all existing text (Cmd+A):**
   ```
   browser action:"act" profile:"openclaw" targetId:"<targetId>" request:{"kind":"press","key":"Meta+a"}
   ```

8. **Type new text (replaces selected text):**
   ```
   browser action:"act" profile:"openclaw" targetId:"<targetId>" request:{"kind":"type","ref":"<textbox_ref>","text":"Customer ID: 12345 ✅"}
   ```

9. **Wait for Save button to enable:**
   ```
   browser action:"act" profile:"openclaw" targetId:"<targetId>" request:{"kind":"wait","timeMs":500}
   ```

10. **Take snapshot** to find enabled Save button:
    ```
    browser action:"snapshot" profile:"openclaw" targetId:"<targetId>" refs:"aria" compact:true
    ```
    Look for:
    ```
    - button [ref=eXXX] [cursor=pointer]:  ← Now enabled! (no [disabled] attribute)
    ```
    
    **Key**: The Save button will now show `[cursor=pointer]` and will NOT have `[disabled]` attribute.

11. **Click Save:**
    ```
    browser action:"act" profile:"openclaw" targetId:"<targetId>" request:{"kind":"click","ref":"<save_button_ref>"}
    ```

12. **Wait and verify:**
    ```
    browser action:"act" profile:"openclaw" targetId:"<targetId>" request:{"kind":"wait","timeMs":2000}
    ```
    Take screenshot to confirm update.

**Common mistakes to avoid:**
- Don't forget to select all (Cmd+A) before typing — otherwise you append to existing text!
- Don't skip the wait after clicking — buttons need time to load.
- Always take a fresh snapshot to get new ref numbers.

### Add a New Note (新增註記 - Simple Steps for AI)

**When to use:** Contact has NO existing note. You will see ONLY a single button/link (no existing note text).

**Step-by-step:**

1. **Open the conversation** (click customer name in chat list).
   Wait 2 seconds for it to load.

2. **Take snapshot** to find the "add note" button:
   ```
   browser action:"snapshot" profile:"openclaw" targetId:"<targetId>" refs:"aria" compact:true
   ```
   Look for the pattern (Notes section with NO existing note):
   ```
   - heading [level=3] [ref=eAAA]  ← Notes heading
   - button [ref=eXXX]             ← Single "add note" button (THIS ONE!)
   ```
   
   **Key**: You should see ONLY one button/link under the Notes heading, with NO paragraph element containing note text.

3. **Click "add note" button:**
   ```
   browser action:"act" profile:"openclaw" targetId:"<targetId>" request:{"kind":"click","ref":"<button_ref>"}
   ```

4. **Wait for the textbox:**
   ```
   browser action:"act" profile:"openclaw" targetId:"<targetId>" request:{"kind":"wait","timeMs":1500}
   ```

5. **Take snapshot** to find the textbox:
   ```
   browser action:"snapshot" profile:"openclaw" targetId:"<targetId>" refs:"aria" compact:true
   ```
   Look for:
   ```
   - textbox [ref=eXXX]:              ← Input field (may show "Hidden Label")
     /placeholder: ...                 ← Placeholder text
   - button [ref=eYYY]                 ← Cancel button
   - button [disabled] [ref=eZZZ]     ← Save button (disabled at first)
   ```
   
   **Key**: The textbox might be labeled "Hidden Label" or similar. Look for `[disabled]` attribute on the Save button.

6. **Type the note text:**
   ```
   browser action:"act" profile:"openclaw" targetId:"<targetId>" request:{"kind":"type","ref":"<textbox_ref>","text":"Customer note text here"}
   ```

7. **Wait for Save button to become enabled:**
   ```
   browser action:"act" profile:"openclaw" targetId:"<targetId>" request:{"kind":"wait","timeMs":500}
   ```

8. **Take snapshot** to find the enabled Save button:
   ```
   browser action:"snapshot" profile:"openclaw" targetId:"<targetId>" refs:"aria" compact:true
   ```
   Look for:
   ```
   - button [ref=eXXX] [cursor=pointer]:  ← Now enabled (no [disabled] attribute!)
   ```

9. **Click Save button:**
   ```
   browser action:"act" profile:"openclaw" targetId:"<targetId>" request:{"kind":"click","ref":"<save_button_ref>"}
   ```

10. **Wait and verify:**
    ```
    browser action:"act" profile:"openclaw" targetId:"<targetId>" request:{"kind":"wait","timeMs":2000}
    ```
    Take a screenshot to confirm the note appears in the sidebar.

**Common mistakes to avoid:**
- Don't skip snapshots — you need the ref numbers!
- Don't reuse old ref numbers — they change every snapshot.
- Wait after clicking before taking next snapshot.

### Delete a Note

1. Take a snapshot to find the Delete link (appears next to Edit link when a note exists).
2. Click the Delete link (the link that appears AFTER the "·" separator, next to the Edit link).
3. Confirm the deletion if prompted.

**In snapshot:**
```
- link [ref=eXXX]  ← Edit link
- text: "·"
- link [ref=eYYY]  ← Delete link (THIS ONE!)
```

## Switch Between Pages

If multiple pages are configured:
1. Read config to see all available pages.
2. Navigate to the desired page URL:
   ```
   browser action:"navigate" profile:"openclaw" targetId:"<targetId>" targetUrl:"<newPageUrl>"
   ```
3. Wait for the page to load.

## Notes

- Meta Business Suite sessions expire periodically; re-login may be required.
- Facebook's DOM structure is complex and changes frequently. Prefer screenshots over DOM parsing when snapshots are unreliable.
- The inbox URL format: `https://business.facebook.com/latest/inbox/all/?&asset_id=<PAGE_ID>`
- Some pages may require specific permissions in Meta Business Suite.
