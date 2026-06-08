/**
 * download.mjs — HTTP download helper for Stitch Design skill.
 * Handles URL-to-file downloads (network → disk, never the reverse).
 */

import { writeFile } from 'node:fs/promises';

export const HIRES_SUFFIX = '=w780';

const PNG_SIG = [0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A];

/** Returns true if the buffer starts with the PNG magic bytes */
export function isPngBuffer(buf) {
  return Buffer.isBuffer(buf) && buf.length >= 8 && PNG_SIG.every((b, i) => buf[i] === b);
}

/** Download a URL to a local file. Throws if the server returns HTML or JSON instead of a binary file.
 * Pass `{ expectImage: false }` to skip Content-Type and magic-byte checks (e.g. for HTML downloads). */
export async function downloadFile(url, dest, { expectImage = true } = {}) {
  const resp = await fetch(url);
  if (!resp.ok) throw new Error(`Download failed: ${resp.status} ${resp.statusText}`);
  const buf = Buffer.from(await resp.arrayBuffer());
  if (expectImage) {
    const ct = resp.headers.get('content-type') || '';
    if (ct.startsWith('text/html') || ct.startsWith('application/json')) {
      throw new Error(`CDN returned HTML instead of image (URL may be expired)`);
    }
    // Magic byte check as second guard (Content-Type header alone is not always reliable)
    if (buf.length >= 8 && !isPngBuffer(buf)) {
      const start = buf.slice(0, 5).toString('ascii');
      if (start.startsWith('<!') || start.startsWith('<html') || start.startsWith('<?xml')) {
        throw new Error(`CDN returned HTML instead of image (magic bytes check failed)`);
      }
    }
  }
  await writeFile(dest, buf);
}

/**
 * Check if a screenshot URL is live using a HEAD request.
 * Returns { alive: boolean, freshUrl: string|null }
 * If the URL returns HTML (expired), tries to get a fresh URL via getScreen.
 */
export async function checkScreenshotUrl(url, { projectId, screenId, getScreen, resolveUrl }) {
  const isAlive = async (u) => {
    try {
      const resp = await fetch(u, { method: 'HEAD' });
      if (!resp.ok) return false;
      const ct = resp.headers.get('content-type') || '';
      return !ct.startsWith('text/html') && !ct.startsWith('application/json');
    } catch { return false; }
  };

  if (await isAlive(url)) return { alive: true, freshUrl: url };

  // URL expired — fetch fresh
  try {
    const fresh = await getScreen({ projectId, screenId });
    const rawUrl = resolveUrl(fresh?.screenshot);
    if (!rawUrl) return { alive: false, freshUrl: null };
    const freshUrl = rawUrl + HIRES_SUFFIX;
    if (await isAlive(freshUrl)) return { alive: true, freshUrl };
  } catch {}

  return { alive: false, freshUrl: null };
}

