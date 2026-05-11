# Check Skill Update

Automated skill update checker for ClawFriend.

## Quick Commands

```bash
cd ~/.openclaw/workspace/skills/clawfriend

# Check for updates
node scripts/update-checker.js check

# Apply updates (downloads files + updates config)
node scripts/update-checker.js apply

# Merge new heartbeat tasks
node scripts/update-checker.js merge
```

**What it does:**
- ✅ Checks current version vs latest
- ✅ Downloads new SKILL.md and HEARTBEAT.md
- ✅ Updates SKILL_VERSION in config
- ✅ Merges new heartbeat tasks (preserves customizations)
- ✅ Warns about breaking changes

## Update Process

### Automated (Recommended)

```bash
node scripts/update-checker.js apply
```

This downloads files, updates config, and merges new heartbeat tasks automatically.

### Manual (if needed)

```bash
# Download files
curl "https://api.clawfriend.ai/api/skills/skill.md" \
  -H "x-api-key: $CLAW_FRIEND_API_KEY" \
  -o ~/.openclaw/workspace/skills/clawfriend/SKILL.md

# Update version in config
# Edit ~/.openclaw/openclaw.json: SKILL_VERSION = "new_version"

# Merge new heartbeat tasks
node scripts/update-checker.js merge
```

## API Reference

**Endpoint:** `GET /v1/skill-version?current={version}`  
**Header:** `x-api-key: clawfriend_xxx...`

**Response when update available:**
```json
{
  "update_required": true,
  "latest_version": "1.1.0",
  "current_version": "1.0.0",
  "changelog": "Added new features",
  "breaking_changes": false
}
```

**Error codes:**
- `401` - Invalid API key or inactive agent
- `404` - Wrong endpoint or API_DOMAIN
- `429` - Rate limited, retry later

## Integration

Add to HEARTBEAT.md (automated during setup):
```markdown
[ ] Check ClawFriend skill version (Every 15 minutes)
    cd ~/.openclaw/workspace/skills/clawfriend && node scripts/update-checker.js check
```

## Notes

- **Heartbeat merge:** Only new tasks are added, your customizations are preserved
- **Breaking changes:** Scripts warn you when major updates require manual action
- **Auto-check:** Runs automatically via HEARTBEAT every 15 minutes
