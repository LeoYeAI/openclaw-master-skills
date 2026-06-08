/**
 * design-system.mjs — Design system registry for Stitch Design skill.
 * Only reads markdown files from the local design-systems/ directory.
 */

import { readFile, mkdir, readdir } from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT_DIR = path.resolve(__dirname, '..');
export const DESIGN_SYSTEMS_DIR = path.join(ROOT_DIR, 'design-systems');
const NAME_RE = /^[a-z0-9][a-z0-9_-]*$/;

function assertValidName(name, die) {
  if (name === true || !name) die('--design-system requires a design system name');
  if (typeof name !== 'string' || !NAME_RE.test(name)) {
    die('--design-system must be a slug like "brand-core" (letters, numbers, - and _)');
  }
}

function resolveDesignSystemPath(name) {
  return path.join(DESIGN_SYSTEMS_DIR, `${name}.md`);
}

export async function listDesignSystems() {
  await mkdir(DESIGN_SYSTEMS_DIR, { recursive: true });
  const entries = await readdir(DESIGN_SYSTEMS_DIR, { withFileTypes: true });
  return entries
    .filter((e) => e.isFile() && e.name.endsWith('.md'))
    .map((e) => e.name.slice(0, -3))
    .sort();
}

/**
 * Append design system file content to prompt if --design-system flag is set.
 * Only registered markdown files from design-systems/<name>.md are allowed.
 * @param {string} prompt - The original prompt
 * @param {object} flags - Parsed CLI flags
 * @param {function} die - Error handler (exits process)
 * @returns {Promise<string>} prompt with design system appended
 */
export async function applyDesignSystem(prompt, flags, die) {
  const name = flags['design-system'];
  if (!name) return prompt;

  assertValidName(name, die);
  const filePath = resolveDesignSystemPath(name);

  let content;
  try {
    content = await readFile(filePath, 'utf-8');
  } catch (err) {
    if (err && err.code === 'ENOENT') {
      const available = await listDesignSystems();
      const suffix = available.length
        ? ` Available: ${available.join(', ')}`
        : ' No design systems found yet. Add markdown files under design-systems/.';
      die(`--design-system: unknown design system "${name}".${suffix}`);
    }
    die(`--design-system: cannot read ${filePath}: ${err.message}`);
  }

  return prompt + '\n\n--- Design System ---\n' + content + '\n\nDo NOT create or modify any design system.';
}
