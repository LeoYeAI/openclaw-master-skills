# Legacy Hooks (Deprecated)

This directory contains the legacy Claude Code hook implementations. These hooks are **deprecated** and have been replaced with OpenClaw-compatible hooks.

## Migration Guide

### Old Structure (Claude Code)

```
hooks/
├── user-prompt-submit-hook.ts   # ❌ Deprecated
└── tool-call-hook.ts             # ❌ Deprecated
```

**Installation:** `~/.claude-code/hooks/`

**Limitations:**
- Designed for Claude Code CLI only
- Standalone TypeScript files
- Manual stdin/stdout handling
- No standardized metadata

### New Structure (OpenClaw)

```
hooks/
├── security-input-validator/     # ✅ Use this
│   ├── HOOK.md
│   └── handler.ts
└── security-tool-validator/      # ✅ Use this
    ├── HOOK.md
    └── handler.ts
```

**Installation:** `~/.openclaw/hooks/`

**Improvements:**
- Works with OpenClaw's hook system
- Standardized directory structure
- YAML frontmatter metadata
- Event-driven architecture
- Plugin API support
- CLI management (`openclaw hooks enable/disable`)

## Migration Steps

1. **Remove old hooks:**
   ```bash
   rm -rf ~/.claude-code/hooks/user-prompt-submit-hook.ts
   rm -rf ~/.claude-code/hooks/tool-call-hook.ts
   ```

2. **Install new hooks:**
   ```bash
   cd hooks/
   ./install-hooks.sh
   ```

3. **Enable hooks:**
   ```bash
   openclaw hooks enable security-input-validator
   openclaw hooks enable security-tool-validator
   ```

4. **Verify:**
   ```bash
   openclaw hooks list
   ```

## Compatibility

The legacy hooks are kept for reference only. They will not receive updates or bug fixes. Please migrate to the new OpenClaw-compatible hooks.

## Key Differences

### Event Handling

**Old:** Manual stdin/stdout processing
```typescript
process.stdin.on('data', (chunk) => {
  const input = JSON.parse(chunk);
  // Process input
  console.log(JSON.stringify(output));
});
```

**New:** Event-driven handlers
```typescript
const handler: HookHandler = async (event) => {
  if (event.type !== "command" || event.action !== "new") return;
  // Process event
};
```

### Metadata

**Old:** No standardized metadata

**New:** YAML frontmatter
```yaml
---
name: security-input-validator
description: "..."
metadata:
  openclaw:
    emoji: "🛡️"
    events: ["command:new"]
---
```

### Plugin API

**Old:** Not supported

**New:** Full plugin API support
```typescript
event.api?.registerPlugin("tool_result_persist", async (toolCall) => {
  // Intercept and validate tool calls
});
```

## Support

For questions about the new hook system, see:
- [hooks/README.md](../README.md)
- [HOOK.md files](../security-input-validator/HOOK.md) in each hook directory
- OpenClaw documentation
