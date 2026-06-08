# Knowledge Vault — Setup Prompt

Copy and paste this entire block into your agent's chat to install Knowledge Vault.

---

```
I need you to set up the Knowledge Vault skill. Follow these steps exactly:

set -euo pipefail
umask 077

## Step 1: Create Data Directories

Run these commands to create the required directories with secure permissions:

mkdir -p data/exports
mkdir -p config
mkdir -p scripts
chmod 700 data
chmod 700 data/exports
chmod 700 config
chmod 700 scripts

## Step 2: Copy Skill Files to Workspace

Resolve a trusted skill path and copy files from it:

KV_SKILL_DIR=$(find "$HOME" -path "*/skills/knowledge-vault/config/vault-config.json" -type f 2>/dev/null | head -1 | sed 's|/config/vault-config.json||')
if [ -z "$KV_SKILL_DIR" ]; then
  echo "ERROR: Could not find knowledge-vault skill package." >&2
  echo "Set KV_SKILL_DIR manually to the knowledge-vault directory path, then re-run setup." >&2
  exit 1
fi

install -m 600 "$KV_SKILL_DIR/config/vault-config.json" config/vault-config.json
install -m 700 "$KV_SKILL_DIR/scripts/vault-stats.sh" scripts/vault-stats.sh

## Step 3: Initialize Vault Database Files

Create the initial empty data files:

printf '%s\n' '[]' > data/vault-entries.json
chmod 600 data/vault-entries.json

TODAY="$(date +%Y-%m-%d)"
printf '[{"name":"general","description":"Default collection for all entries","created":"%s"},{"name":"read-later","description":"Queue for unprocessed URLs","created":"%s"}]\n' "$TODAY" "$TODAY" > data/collections.json
chmod 600 data/collections.json

## Step 4: Read the Skill File

Now read the SKILL.md file to learn how Knowledge Vault works:

cat "$KV_SKILL_DIR/SKILL.md"

## Step 5: Verify Installation

Confirm the setup by checking that all files exist:

echo "=== Knowledge Vault Installation Check ==="
echo ""
echo "Config:"
[ -f config/vault-config.json ] && echo "  ✅ vault-config.json" || echo "  ❌ vault-config.json MISSING"
echo ""
echo "Scripts:"
[ -f scripts/vault-stats.sh ] && echo "  ✅ vault-stats.sh" || echo "  ❌ vault-stats.sh MISSING"
echo ""
echo "Data:"
[ -f data/vault-entries.json ] && echo "  ✅ vault-entries.json" || echo "  ❌ vault-entries.json MISSING"
[ -f data/collections.json ] && echo "  ✅ collections.json" || echo "  ❌ collections.json MISSING"
[ -d data/exports ] && echo "  ✅ exports/" || echo "  ❌ exports/ MISSING"
echo ""
echo "=== Installation Complete ==="

## Step 6: Test It

Let's do a quick test. Send me any URL — an article, YouTube video, or tweet — and I'll digest it into your vault.
```

---

## What Happens Next

After running the setup prompt, your agent will:
1. Create secure directories for your vault data
2. Copy the configuration and scripts into place
3. Initialize empty database files
4. Read the SKILL.md to learn all capabilities
5. Verify everything is in place
6. Ask you to test it with a real URL

**That's it.** Your Knowledge Vault is ready to use. Just send links and your agent handles the rest.

---

## Troubleshooting

- **"Permission denied" errors:** Make sure your agent has write access to the workspace directory.
- **"Could not find knowledge-vault skill package":** Set `KV_SKILL_DIR` manually to the full path of your knowledge-vault skill directory, then re-run Step 2.
- **Config not copying:** Manually copy `config/vault-config.json` from the skill package to your workspace's `config/` directory.
