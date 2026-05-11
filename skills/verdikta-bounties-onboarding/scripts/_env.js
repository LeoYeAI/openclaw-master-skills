// Loads environment variables from .env (if present) for local dev convenience.
// This avoids needing to manually export vars in the shell.
// Safe: does NOT print secrets.

import path from 'node:path';
import fs from 'node:fs';
import { fileURLToPath } from 'node:url';
import dotenv from 'dotenv';

function loadIfExists(p) {
  try {
    if (fs.existsSync(p)) {
      dotenv.config({ path: p });
      return true;
    }
  } catch {}
  return false;
}

// Priority:
// 1) .env in current working directory (where user runs scripts)
// 2) .env next to this file (scripts/.env)
loadIfExists(path.resolve(process.cwd(), '.env'));
loadIfExists(path.resolve(path.dirname(fileURLToPath(import.meta.url)), '.env'));
