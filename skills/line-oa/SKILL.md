---
name: line-oa
description: Operate LINE Official Account Manager (chat.line.biz) via browser automation. Use when asked to check LINE messages, reply to LINE customers, or manage LINE OA chat interface.
---

# LINE Official Account Manager

⚠️ **CRITICAL**: Always use `profile:"openclaw"` (isolated browser) for all browser actions. Never use Chrome relay. Keep the same `targetId` across operations to avoid losing the tab.

⚠️ **CONTEXT Management**:
- Snapshot results are large. Do NOT repeat them in thinking.
- Extract needed info and process immediately. Do not re-describe the entire snapshot.
- **Preferred approach**: Use `snapshot refs:"aria" compact:true` to find element refs, then `act` + `click`/`type` with ref.
- **Avoid**: Hard-coded `evaluate` with `textContent.includes()` — unreliable due to DOM timing and structure variations.

⚠️ **AUTO-LOGIN SCRIPTS**:
- `auto-login.mjs` is a **reference implementation** (not directly executable by agents)
- `login-flow.md` is the **agent-executable version** (use this for automation)
- **Why separate?** Agents use browser tool calls, not Node module imports

## Configuration

Before first use, check if `config.json` exists:
```
read file_path:"skills/line-oa/config.json"
```

⚠️ **PATH RULE**: Always use workspace-relative paths starting from `skills/line-oa/`. Never use `../` or absolute paths starting with `/`.

If missing, help the user run the following command to start the setup wizard:
```bash
cd skills/line-oa
node scripts/setup.js
```

# Enter LINE OA Manager
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

2. **Read config to get chatUrl:**
   ```
   read file_path:"skills/line-oa/config.json"
   ```
   Extract `chatUrl` from the JSON (e.g., `https://chat.line.biz/U1234567890abcdef1234567890abcdef/`).

2. **Open browser:**
   ```
   browser action:"open" profile:"openclaw" targetUrl:"<chatUrl>"
   ```
   Capture `targetId` and `url` from response.

3. **Wait for page load:**
   ```
   browser action:"act" profile:"openclaw" targetId:"<targetId>" request:{"kind":"wait","timeMs":2000}
   ```

4. **Check current URL:**
   ```
   browser action:"act" profile:"openclaw" targetId:"<targetId>" request:{"kind":"evaluate","fn":"function(){return window.location.href;}"}
   ```
   
   Key result: If the current URL matches `chatUrl`, you have successfully logged in! Go to step 5, else proceed to troubleshooting.

   ### Troubleshooting
   If you see the login page (the URL redirects to `account.line.biz`), use these automation scripts:

   a. **Click LINE Account button:**
      ```
      read file_path:"skills/line-oa/scripts/click-line-account.js"
      ```
      Execute the script directly:
      ```
      browser action:"act" profile:"openclaw" targetId:"<targetId>" request:{"kind":"evaluate","fn":"<script_content>"}
      ```
      Wait 2 seconds.

   b. **Click Login button:**
      ```
      read file_path:"skills/line-oa/scripts/click-login.js"
      ```
      Execute the script directly:
      ```
      browser action:"act" profile:"openclaw" targetId:"<targetId>" request:{"kind":"evaluate","fn":"<script_content>"}
      ```
      Wait 3 seconds.

   c. **Reload chatUrl:**
      ```
      browser action:"navigate" profile:"openclaw" targetId:"<targetId>" targetUrl:"<chatUrl>"
      ```
      Wait 2 seconds, then take snapshot to verify left-side chat list is visible.

   ###  After Check

5. **Proceed with the user's other requests.**
6. **Clean Up Browser Tabs**:
   
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
   
   **Important**: Always clean up tabs after all operations to prevent resource accumulation. The blank tab keeps the browser service running for faster next use.

## Quick Check (for cron / automated checks)

Complete flow: login → list chats → report. Follow these steps exactly.

1. Read config: `read file_path:"skills/line-oa/config.json"` → get `chatUrl`
2. Open browser: `browser action:"open" profile:"openclaw" targetUrl:<chatUrl>` → get `targetId`
3. Wait: `browser action:"act" profile:"openclaw" targetId:<targetId> request:{"kind":"wait","timeMs":3000}`
4. Check URL: `browser action:"act" profile:"openclaw" targetId:<targetId> request:{"kind":"evaluate","fn":"function(){return window.location.href;}"}`
   - If URL contains `account.line.biz` → go to **Troubleshooting** section below to login, then come back
   - If URL contains `chat.line.biz` → continue
5. Run this one-liner script **as-is, do not modify**:
   ```
   browser action:"act" profile:"openclaw" targetId:<targetId> request:{"kind":"evaluate","fn":"(function(){var r=document.querySelectorAll('.list-group-item-chat');return Array.from(r).map(function(e){var h=e.querySelector('h6');var p=e.querySelector('.text-muted.small');var pt=p?p.textContent.trim():'';var ms=e.querySelectorAll('.text-muted');var t='';for(var i=0;i<ms.length;i++){var v=ms[i].textContent.trim();if(v&&v.length<20&&v!==pt)t=v;}var d=e.querySelector('span.badge.badge-pin');var u=!!d&&getComputedStyle(d).display!=='none';return{name:h?h.textContent.trim():'',time:t,lastMsg:pt.substring(0,100),unread:u};}).filter(function(i){return i.name;});})()"}
   ```
   ⚠️ **CHECKPOINT**: Did you actually call the browser tool above? If you only thought about it but didn't call it, STOP and call it NOW. You MUST see a tool result before continuing.
6. Report: take the first 5 items, format each as: `<name> (<time>) <lastMsg> [未讀]` or `[已讀]` based on `unread` field. If empty array, say "目前沒有聊天記錄".
7. Clean up: open `about:blank`, list all tabs, close everything except `about:blank`.

---

## Check LINE Messages

Extracts all chats from the left-side chat list with unread status. Does NOT require clicking into each chat.

**Prerequisites**: You must be logged in and on the chat list page (see Login section Step 5 for verification).

### Steps

1. Read the script content:
   ```
   read file_path:"skills/line-oa/scripts/list-chats.js"
   ```
2. Run the script via browser evaluate:
   
   Pass the script content directly as the `fn` parameter:
   ```
   browser action:"act" profile:"openclaw" targetId:"<your_targetId>" request:{"kind":"evaluate","fn":"<script_content>"}
   ```

3. The script returns a JSON array of **all** chat items with structure:
   ```
   [{ name: string, time: string, lastMsg: string, unread: boolean }]
   ```
   - `name`: customer display name
   - `time`: timestamp (e.g., "21:32", "Yesterday", "Friday")
   - `lastMsg`: last message preview (~100 chars)
   - `unread`: `true` if green dot present, `false` otherwise

4. **Get URLs for unread chats** (optional but recommended for faster follow-up):
   
   For each unread chat, click into it to get the direct URL, then return to list:
   ```
   browser action:"act" profile:"openclaw" targetId:"<your_targetId>" request:{"kind":"evaluate","fn":"function(){const items=document.querySelectorAll('.list-group-item-chat');const target=Array.from(items).find(el=>{const h6=el.querySelector('h6');return h6&&h6.textContent.includes('<customer_name>');});if(target){const link=target.querySelector('a.d-flex');if(link){link.click();return {clicked:true};}return {linkNotFound:true};}return {itemNotFound:true};}"}
   ```
   
   Wait 500ms, then get the URL:
   ```
   browser action:"act" profile:"openclaw" targetId:"<your_targetId>" request:{"kind":"evaluate","fn":"function(){return window.location.href;}"}
   ```
   
   Navigate back to list:
   ```
   browser action:"navigate" profile:"openclaw" targetId:"<your_targetId>" targetUrl:"<chatUrl>"
   ```
   
   Wait 1 second before processing next unread chat.
   
   **Result**: Store the chat URL (e.g., `https://chat.line.biz/U1234567890abcdef1234567890abcdef/chat/U803dc04f...`) alongside the chat info for faster access later.

### How to Report Results

- **If `unread: true` exists**: List each unread chat with name, time, preview, and URL (if obtained)
- **If no unread**: Say "No unread messages at this time"

### Notes

- **Unread indicator**: `span.badge.badge-pin` inside each chat list item (green dot)
- **Limitation**: `lastMsg` shows the last message in the thread, which may be an auto-response rather than the customer's original message
- **Chat URLs**: Getting URLs requires clicking each chat. Do this for unread chats to enable faster replies later.
- **To read full messages**: See "View Specific Messages" section below

## View Specific Messages

Opens any chat (read or unread) and displays its messages. Works for viewing message history, checking context, or preparing to reply.

**Prerequisites**: You must be logged in and on the chat list page. You should know the customer name (from `list-chats.js` or user request).

### Steps

1. **Find and click the chat item** to open messages:
   
   Use evaluate to find the chat item by name (more reliable than snapshot for dynamic chat list):
   ```
   browser action:"act" profile:"openclaw" targetId:"<your_targetId>" request:{"kind":"evaluate","fn":"function(){const items=document.querySelectorAll('.list-group-item-chat');const target=Array.from(items).find(el=>{const h6=el.querySelector('h6');return h6&&h6.textContent.includes('<customer_name>');});if(target){const link=target.querySelector('a.d-flex');if(link){link.click();return {clicked:true};}return {linkNotFound:true};}return {itemNotFound:true};}"}
   ```
   Replace `<customer_name>` with the actual customer name.

2. **Wait for messages panel to load:**
   ```
   browser action:"act" profile:"openclaw" targetId:"<your_targetId>" request:{"kind":"wait","timeMs":2000}
   ```

3. **Take a screenshot to view the messages:**
   ```
   browser action:"screenshot" profile:"openclaw" targetId:"<your_targetId>"
   ```
   
   The screenshot will show:
   - Recent messages in the chat (right panel)
   - Customer info and tags (far right panel)
   - Auto-response status banner (if active)

4. **Optional: Read recent messages programmatically**
   
   If you need structured message data instead of a screenshot, read and run this script:
   ```
   read file_path:"skills/line-oa/scripts/read-messages.js"
   ```
   Execute:
   ```
   browser action:"act" profile:"openclaw" targetId:"<your_targetId>" request:{"kind":"evaluate","fn":"<script_content>"}
   ```
   
   Returns an array of recent messages with:
   - `time`: timestamp
   - `text`: message content
   - `isCustomer`: true if from customer, false if from you
   - `hasImage`: true if message contains an image

### Navigation Tips

**To scroll to earlier messages:**
- The messages panel auto-scrolls to the bottom by default
- To see earlier history, use:
  ```
  browser action:"act" profile:"openclaw" targetId:"<your_targetId>" request:{"kind":"evaluate","fn":"function(){const panel=document.querySelector('.conversation-panel, .messages-container, [class*=\"chat-container\"]');if(panel){panel.scrollTo({top:0,behavior:'smooth'});return {scrolled:true};}return {error:'Messages panel not found'};}"}
  ```
- Wait 1 second after scrolling, then take another screenshot

**Common issues:**
- If messages don't load: increase wait time to 3000ms
- If customer name has special characters: use partial match (e.g., "John" instead of "John ⭐️")
- If click fails: the chat might not be visible in the current scroll position of the left panel

### Handling Images

When you see images in the screenshot or `hasImage: true` in message data:

1. **Find and download the image:**
   ```javascript
   function(){
     const allPhotoImgs = Array.from(document.querySelectorAll('img[alt="Photo"]'));
     const targetImg = allPhotoImgs.find(img => {
       const parent = img.closest('.chat');
       return parent && !parent.classList.contains('chat-reverse') && parent.innerText.includes('<time>');
     });
     
     if (!targetImg) return {error: 'Image not found'};
     
     const parent = targetImg.closest('.chat');
     const downloadLink = Array.from(parent.querySelectorAll('a')).find(a => a.textContent.trim() === 'Download');
     
     if (downloadLink) {
       downloadLink.click();
       return {clicked: true};
     }
     return {error: 'Download link not found'};
   }
   ```
   Replace `<time>` with the message timestamp (e.g., "09:11").

2. **Wait and locate downloaded file:**
   ```
   browser action:"act" profile:"openclaw" targetId:"<your_targetId>" request:{"kind":"wait","timeMs":2000}
   ```
   ```
   exec command:"ls -t ~/Downloads/line_oa_chat_*.jpg 2>/dev/null | head -1"
   ```

3. **Send to user:**
   ```
   message action:"send" target:"<user>" filePath:"<path>" message:"Customer sent this image"
   ```

**Note:** Downloaded images are named `line_oa_chat_YYMMDD_HHMMSS.jpg`

## Reply to a Message

**⚡ Fast Path**: If you already have the chat URL from a previous "Check LINE Messages" operation, skip steps 1-2 and go directly to step 3:
```
browser action:"navigate" profile:"openclaw" targetId:"<your_targetId>" targetUrl:"<chat_url>"
```
Wait 2 seconds, then proceed to step 3.

**Standard Path** (when you don't have the chat URL):

1. Take a snapshot to find the chat item:
   ```
   browser action:"snapshot" profile:"openclaw" targetId:"<your_targetId>" refs:"aria"
   ```
2. Click a chat item link in the left panel (e.g., `ref:"e68"`):
   ```
   browser action:"act" profile:"openclaw" targetId:"<your_targetId>" request:{"kind":"click","ref":"e68"}
   ```
3. If the input box is locked (auto-response mode), click the manual chat toggle button in the top banner to unlock it.
4. Take another snapshot to find the input box and send button.
5. Click the text input box (e.g., `ref:"e509"`):
   ```
   browser action:"act" profile:"openclaw" targetId:"<your_targetId>" request:{"kind":"click","ref":"e509"}
   ```
6. Type the reply message:
   ```
   browser action:"act" profile:"openclaw" targetId:"<your_targetId>" request:{"kind":"type","ref":"e509","text":"Hello! I'm Emma, happy to help you!"}
   ```
7. Click the green **Send** button (e.g., `ref:"e522"`) or press Enter:
   ```
   browser action:"act" profile:"openclaw" targetId:"<your_targetId>" request:{"kind":"click","ref":"e522"}
   ```

## Manage Notes

Each chat has a Notes panel on the right side. Notes are internal-only (not visible to customers). Max 300 characters per note.

### Add a note
1. Open the conversation.
2. Click the **+** button next to the Notes heading in the right panel.
3. Type content in the textarea.
4. Click **Save**.

### Edit a note
1. Find the note in the right panel.
2. Click the pencil icon at the note's bottom-right corner.
3. Modify the textarea content.
4. Click **Save**.

### Delete a note
1. Click the trash icon at the note's bottom-right corner.
2. A confirmation dialog appears — click **Delete** to confirm.

## Manage Tags

Tags are shown in the right panel below the user's name. They are predefined labels for categorizing chats.

### Add a tag
1. Open the conversation.
2. Click the **Add tags** link (or the pencil icon next to existing tags) in the right panel.
3. The Edit tags modal opens, showing an input field and all available tags.
4. Click a tag from the "All tags" list to select it (it moves to the input field).
5. Click **Save**.

### Remove a tag
1. Open the Edit tags modal (same as above).
2. Click the **×** next to the tag in the input field to deselect it.
3. Click **Save**.

## Switch Account

LINE OA Manager can manage multiple official accounts. Switch between them using the account dropdown in the top-left corner.

1. Take a snapshot to find the account selector:
   ```
   browser action:"snapshot" profile:"openclaw" targetId:"<your_targetId>" refs:"aria"
   ```
2. Click the account combobox (shows current account name):
   ```
   browser action:"act" profile:"openclaw" targetId:"<your_targetId>" request:{"kind":"click","ref":"e11"}
   ```
3. Wait for the dropdown menu to appear:
   ```
   browser action:"act" profile:"openclaw" targetId:"<your_targetId>" request:{"kind":"wait","timeMs":1000}
   ```
4. Take another snapshot to see available accounts in the listbox:
   ```
   browser action:"snapshot" profile:"openclaw" targetId:"<your_targetId>" refs:"aria"
   ```
   The snapshot will show a list of accounts you have access to. Look for generic items in the listbox (each account will have a name and "Administrator" or role label).
5. Click the desired account item (e.g., `ref:"e589"`):
   ```
   browser action:"act" profile:"openclaw" targetId:"<your_targetId>" request:{"kind":"click","ref":"e589"}
   ```
6. Wait for the page to load the new account's chat list:
   ```
   browser action:"act" profile:"openclaw" targetId:"<your_targetId>" request:{"kind":"wait","timeMs":2000}
   ```

## Notes

- LINE periodically expires sessions; re-login required when that happens
- Session is usually active for several hours if the browser remains open
