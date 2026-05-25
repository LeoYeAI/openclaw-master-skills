'use strict';
// Standalone restore — no native addon, safe to run when shards are missing
const path = require('path');
const fs   = require('fs');
const { execSync } = require('child_process');

const C = process.env.AAWP_CONFIG || path.join(__dirname, '..', '.agent-config');
const S = process.env.AAWP_SKILL  || path.resolve(__dirname, '..');

const backupPath = process.argv[3];
if (!backupPath) { console.log('Usage: wallet-manager restore <backup.tar.gz>'); process.exit(1); }
if (!fs.existsSync(backupPath)) { console.log('❌ Not found:', backupPath); process.exit(1); }

const tmpDir = `/tmp/aawp-restore-${Date.now()}`;
fs.mkdirSync(tmpDir, { recursive: true });
console.log('Extracting...');
execSync(`tar xzf "${backupPath}" -C "${tmpDir}"`, { stdio: 'inherit' });

// Detect backup format: v2 (portable) has manifest.json, v1 (legacy) has absolute paths
const manifestPath = path.join(tmpDir, 'manifest.json');
const isV2 = fs.existsSync(manifestPath);

const copyIfExists = (src, dst) => {
  if (fs.existsSync(src)) {
    fs.mkdirSync(path.dirname(dst), { recursive: true });
    fs.copyFileSync(src, dst);
    console.log('  ✅', path.basename(dst));
    return true;
  }
  return false;
};

if (isV2) {
  // ── V2 portable format ──
  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf8'));
  console.log(`Backup format: v${manifest.version} (${manifest.createdAt})`);

  copyIfExists(path.join(tmpDir, 'agent-config/seed.enc'),   path.join(C, 'seed.enc'));
  copyIfExists(path.join(tmpDir, 'core/aawp-core.node'),     path.join(S, 'core/aawp-core.node'));
  copyIfExists(path.join(tmpDir, 'system/fonts.idx'),         '/var/lib/aawp/.cache/fonts.idx');
  copyIfExists(path.join(tmpDir, 'system/machine-id'),        '/etc/machine-id');
  copyIfExists(path.join(tmpDir, 'system/host.salt'),         '/var/lib/aawp/host.salt');
  copyIfExists(path.join(tmpDir, 'config/guardian.json'),     path.join(S, 'config/guardian.json'));

  // Restore any additional agent-config files
  const acDir = path.join(tmpDir, 'agent-config');
  if (fs.existsSync(acDir)) {
    const walk = (dir, rel) => {
      for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
        const full = path.join(dir, e.name);
        const r = path.join(rel, e.name);
        if (e.isDirectory()) walk(full, r);
        else copyIfExists(full, path.join(C, r));
      }
    };
    walk(acDir, '');
  }
} else {
  // ── V1 legacy format (absolute paths in tar) ──
  console.log('Backup format: v1 (legacy absolute paths)');

  const stripRoot = (abs) => path.join(tmpDir, abs);
  copyIfExists(stripRoot(C + '/seed.enc'),                        path.join(C, 'seed.enc'));
  copyIfExists(stripRoot(S + '/core/aawp-core.node'),             path.join(S, 'core/aawp-core.node'));
  copyIfExists(stripRoot('/var/lib/aawp/.cache/fonts.idx'),       '/var/lib/aawp/.cache/fonts.idx');
  copyIfExists(stripRoot('/etc/machine-id'),                      '/etc/machine-id');
  copyIfExists(stripRoot('/var/lib/aawp/host.salt'),              '/var/lib/aawp/host.salt');
  copyIfExists(stripRoot(S + '/config/guardian.json'),            path.join(S, 'config/guardian.json'));

  // Try legacy .agent-config path from backup manifest
  const backupCfg = stripRoot(C);
  if (fs.existsSync(backupCfg)) {
    execSync(`cp -r "${backupCfg}/." "${C}/"`, { stdio: 'inherit' });
    console.log('  ✅ .agent-config dir restored');
  }
}

// Regenerate binary hash
const corePath = path.join(S, 'core/aawp-core.node');
if (fs.existsSync(corePath)) {
  const hash = execSync(`sha256sum "${corePath}" | cut -d' ' -f1`).toString().trim();
  fs.writeFileSync(corePath + '.hash', hash);
  console.log(`  ✅ Hash regenerated: ${hash}`);
}

execSync(`rm -rf "${tmpDir}"`);
console.log('\n✅ Restore complete.');
console.log('\nNext steps:');
console.log('  1. Restart daemon:  bash scripts/restart-daemon.sh');
console.log('  2. Verify status:   node scripts/wallet-manager.js status\n');
