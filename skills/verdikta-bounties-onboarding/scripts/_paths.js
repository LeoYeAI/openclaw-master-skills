import os from 'node:os';
import path from 'node:path';
import fs from 'node:fs/promises';

export function defaultSecretsDir() {
  // Prefer XDG-ish location; keeps secrets out of the repo.
  return process.env.VERDIKTA_SECRETS_DIR || path.join(os.homedir(), '.config', 'verdikta-bounties');
}

export async function ensureDir(dir) {
  await fs.mkdir(dir, { recursive: true, mode: 0o700 });
}
