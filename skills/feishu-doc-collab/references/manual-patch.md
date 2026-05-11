# Manual Patching Guide

If the automatic patch script fails (e.g., after a major OpenClaw update that restructures `monitor.ts`),
follow these steps to apply the patch manually.

## What the Patch Does

The patch adds code to the `drive.file.edit_v1` event handler in the Feishu extension's `monitor.ts`.
After the default system event is enqueued, it additionally:

1. Reads `~/.openclaw/openclaw.json` to get the hooks token and gateway port
2. POSTs to `http://127.0.0.1:{port}/hooks/agent` with an isolated agent turn
3. The agent turn instructs the AI to read the document, check for new messages per the
   Doc Chat Protocol, and respond if appropriate

## Target File

```
/usr/lib/node_modules/openclaw/extensions/feishu/src/monitor.ts
```

## Where to Inject

Find the `drive.file.edit_v1` event handler. Look for the line:

```typescript
log(`feishu[${accountId}]: injected drive.file.edit system event for file ${fileToken}`);
```

Insert the hooks trigger code **immediately after** this line.

## Code to Insert

See `scripts/patch-monitor.sh` for the exact code block — it's the section between
`// [feishu-doc-collab] Trigger isolated agent turn` and the closing `catch` block.

## Key Variables

- `fileToken` — the document token from the edit event
- `fileType` — document type (docx, sheet, etc.)
- `accountId` — Feishu account identifier
- `hooksToken` — from openclaw.json `hooks.token`
- `port` — from openclaw.json `gateway.port` (default 18789)

## After Patching

Restart the gateway:

```bash
openclaw gateway restart
```

## Verification

Check the logs for:
```
feishu[default]: triggered /hooks/agent for doc edit on <fileToken>
```

If you see this after editing a Feishu doc, the patch is working.
