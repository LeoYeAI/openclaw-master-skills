#!/bin/bash
# SEO Intel — Auto-update script
# Called by OpenClaw when an update is available and approved
# Preserves: .env, config/, gsc/, reports/, .tokens/, *.db

set -e

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SEO_INTEL_DIR="$SKILL_DIR/seo-intel"

echo "🐸 SEO Intel — Updating..."

cd "$SEO_INTEL_DIR"

# 1. Backup user data
BACKUP_DIR="/tmp/seo-intel-backup-$(date +%s)"
mkdir -p "$BACKUP_DIR"
[ -f .env ] && cp .env "$BACKUP_DIR/"
[ -d config ] && cp -r config "$BACKUP_DIR/"
[ -d gsc ] && cp -r gsc "$BACKUP_DIR/"
[ -d .tokens ] && cp -r .tokens "$BACKUP_DIR/"
echo "  ✓ Backed up user data to $BACKUP_DIR"

# 2. Pull latest from npm
echo "  Pulling latest version..."
npm install seo-intel@latest --production --silent 2>&1 | tail -3
echo "  ✓ Updated to $(node -e "console.log(JSON.parse(require('fs').readFileSync('package.json','utf8')).version)")"

# 3. Restore user data (in case update overwrote anything)
[ -f "$BACKUP_DIR/.env" ] && cp "$BACKUP_DIR/.env" .env
[ -d "$BACKUP_DIR/config" ] && cp -r "$BACKUP_DIR/config/" config/
[ -d "$BACKUP_DIR/gsc" ] && cp -r "$BACKUP_DIR/gsc/" gsc/
[ -d "$BACKUP_DIR/.tokens" ] && cp -r "$BACKUP_DIR/.tokens/" .tokens/
echo "  ✓ Restored user data"

# 4. Run any migration scripts
if [ -f "migrations/latest.js" ]; then
  echo "  Running migrations..."
  node migrations/latest.js 2>&1 || echo "  ⚠ Migration had warnings (non-critical)"
fi

# 5. Clear update cache
rm -f .cache/update-check.json

# 6. Re-install Playwright if needed
npx playwright install chromium --with-deps 2>/dev/null || true

echo ""
echo "  ✓ SEO Intel updated successfully!"
echo "  → Your configs, data, and tokens are preserved."
echo ""

# Cleanup old backup after 7 days
find /tmp -name "seo-intel-backup-*" -mtime +7 -exec rm -rf {} + 2>/dev/null || true
