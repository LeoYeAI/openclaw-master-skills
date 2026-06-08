/**
 * artifacts.mjs — Local artifact storage for Stitch Design skill.
 * Handles run directories, file downloads, and latest-screen state.
 */

import { writeFile, mkdir, readFile } from 'node:fs/promises';
import { existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { downloadFile } from './download.mjs';

const __dirname = dirname(fileURLToPath(import.meta.url));
export const RUNS_DIR = join(__dirname, '..', 'runs');
const LATEST_FILE = join(__dirname, '..', 'latest-screen.json');

function timestamp() {
  return new Date().toISOString().replace(/[-:]/g, '').replace('T', '-').slice(0, 15);
}

function slugify(text) {
  const slug = text.toLowerCase().replace(/[^a-z0-9]+/g, '-').slice(0, 40).replace(/-$/, '');
  return slug || 'unnamed';
}

/** Resolve a field that may be a string URL or {downloadUrl, mimeType, name} object */
export function resolveUrl(field) {
  if (!field) return null;
  if (typeof field === 'string') return field;
  if (typeof field === 'object' && field.downloadUrl) return field.downloadUrl;
  return null;
}

/** Create a timestamped run directory */
export async function makeRunDir(operation, slug) {
  const dir = join(RUNS_DIR, `${timestamp()}-${operation}-${slugify(slug)}`);
  await mkdir(dir, { recursive: true });
  return dir;
}

// downloadFile re-exported from download.mjs
// (separated to keep file-read and network-send in different modules)
export { downloadFile };

/** Save latest screen reference for auto-resolve */
export async function saveLatest(projectId, screenId, operation) {
  const data = { projectId, screenId, operation, timestamp: new Date().toISOString() };
  await writeFile(LATEST_FILE, JSON.stringify(data, null, 2));
  return data;
}

/** Load latest screen reference */
export async function loadLatest() {
  if (!existsSync(LATEST_FILE)) return null;
  try { return JSON.parse(await readFile(LATEST_FILE, 'utf8')); } catch { return null; }
}

/** Save screen artifacts (HTML code + screenshot) to run dir */
export async function saveScreenArtifacts(runDir, screen, index) {
  const prefix = index !== undefined ? `variant-${index + 1}` : 'screen';
  const artifacts = [];

  const htmlUrl = resolveUrl(screen.htmlCode);
  if (htmlUrl) {
    try {
      await downloadFile(htmlUrl, join(runDir, `${prefix}.html`));
      artifacts.push(`${prefix}.html`);
    } catch (e) {
      console.error(`Warning: HTML download failed: ${e.message}`);
      await writeFile(join(runDir, `${prefix}-html-url.txt`), htmlUrl);
      artifacts.push(`${prefix}-html-url.txt`);
    }
  }

  const imgUrl = resolveUrl(screen.screenshot);
  if (imgUrl) {
    try {
      await downloadFile(imgUrl, join(runDir, `${prefix}.png`));
      artifacts.push(`${prefix}.png`);
    } catch (e) {
      console.error(`Warning: Screenshot download failed: ${e.message}`);
      await writeFile(join(runDir, `${prefix}-screenshot-url.txt`), imgUrl);
      artifacts.push(`${prefix}-screenshot-url.txt`);
    }
  }

  return artifacts;
}

/** Write a JSON result file to a run directory */
export async function saveResult(runDir, data) {
  await writeFile(join(runDir, 'result.json'), JSON.stringify(data, null, 2));
}
