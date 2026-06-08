# SMS Verification Codes

How to handle SMS verification codes during booking flows.

Load config: `CONFIG=$(cat ~/.openclaw/skills/date-night/config.json)`

---

## Overview

OpenTable sends a 6-digit verification code via SMS when completing a guest checkout. The code arrives from a short code and must be entered during the booking flow.

---

## OpenTable Verification

**Short code:** 22395 (US)
**Code length:** 6 digits
**Expiry:** 10 minutes

### First-Time Setup

You need to discover your SMS client's chat ID for the OpenTable short code. On first use:

```bash
# If using imsg (iMessage CLI)
# After triggering an OpenTable verification, find the chat:
imsg chats --limit 20 --json 2>/dev/null | jq -r 'select(.name | test("22395|opentable";"i")) | "\(.id) \(.name)"' 2>/dev/null || true

# Or search recent messages for the verification sender only:
imsg history --limit 10 2>/dev/null | grep -i "opentable\|22395\|verification code" || true
```

Once you find it, **save the chat ID** to `~/.openclaw/skills/date-night/config.json`:
```bash
cat ~/.openclaw/skills/date-night/config.json | \
  jq '. + {"opentable_sms_chat_id": {CHAT_ID}}' > /tmp/conf.json && \
  mv /tmp/conf.json ~/.openclaw/skills/date-night/config.json
```

### Retrieve Code
```bash
OT_CHAT=$(cat ~/.openclaw/skills/date-night/config.json | jq -r '.opentable_sms_chat_id // "unknown"')

# Get latest code
imsg history --chat-id ${OT_CHAT} --limit 1 2>/dev/null | grep -oE '[0-9]{6}' || true

# If chat ID unknown, broad search:
imsg history --limit 10 2>/dev/null | grep -oE '[0-9]{6}' | head -1 || true
```

---

## Resy Verification

**Short code:** TBD — discover on first Resy booking.
**Code length:** 4–6 digits

```bash
# After triggering Resy SMS:
imsg history --limit 10 2>/dev/null | grep -i "resy\|verification\|code" || true
# Note the chat ID and update config similarly to OpenTable above
```

---

## Entering Codes in Cross-Origin Iframes

Both OpenTable and Resy may render verification inputs in **cross-origin iframes** where DOM access is blocked. Use keyboard press instead of fill:

```bash
# Code: 714289
playwright-cli press 7
playwright-cli press 1
playwright-cli press 4
playwright-cli press 2
playwright-cli press 8
playwright-cli press 9
```

**Tips:**
- Verification input usually auto-focuses — check snapshot first
- If not focused: `playwright-cli press Tab` to move focus
- Some forms auto-submit after all digits are entered
- Wrong digit: `playwright-cli press Backspace` to correct

---

## Resend Code

If code doesn't arrive within ~15 seconds:

```bash
playwright-cli snapshot
playwright-cli click {resend-code-ref}
sleep 10
imsg history --chat-id ${OT_CHAT} --limit 1 2>/dev/null | grep -oE '[0-9]{6}' || true
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| No code received | Wait up to 60s. Click "Resend code". Check cellular signal. |
| Code expired | Click "Resend code" for a fresh code. Move quickly on retry. |
| Multiple codes in history | Use the most recent (highest timestamp). |
| Code from wrong service | Verify chat ID — filter by short code number if possible. |
| SMS client not returning results | Test with `imsg chats --limit 5` to verify CLI is working. |
| Wrong SMS tool configured | Check `config.notify_channel` — different tool may be needed |

---

## Alternative SMS Tools

If not using `imsg` (iMessage), adapt the code retrieval for your SMS client:

| Tool | Command Pattern |
|------|----------------|
| iMessage (imsg) | `imsg history --chat-id {id} --limit 1` |
| Telegram | Check Telegram bot or specific chat for SMS forwarding |
| Other | Adapt based on your SMS CLI / tool |

The underlying pattern is always: wait for SMS → find in inbox → extract digits → press each digit individually in the browser.
