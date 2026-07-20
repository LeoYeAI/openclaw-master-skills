import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { formatApiError, isApiSuccess } from './errors.js';

export const DEFAULT_UPLOAD_API_PATH = '/v1/generation/upload-file';
export const DEFAULT_UPLOAD_MAX_BYTES = 500 * 1024 * 1024;

const ALLOWED_UPLOAD_EXTS = new Set([
  // image
  '.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.tiff', '.tif',
  // video
  '.mp4', '.mov', '.m4v', '.webm', '.avi', '.mkv',
  // audio
  '.mp3', '.wav', '.m4a', '.aac', '.flac', '.ogg',
  // text and structured text
  '.txt', '.md', '.json', '.csv', '.srt', '.vtt', '.xml', '.yaml', '.yml',
]);

const BLOCKED_UPLOAD_EXTS = new Set([
  '.exe', '.dll', '.bat', '.cmd', '.com', '.msi', '.scr', '.ps1', '.sh',
  '.apk', '.ipa', '.bin', '.jar',
]);

export function isPublicHttpsUrl(value) {
  if (typeof value !== 'string' || value.trim().length === 0) return false;
  try {
    const url = new URL(value);
    return url.protocol === 'https:';
  } catch {
    return false;
  }
}

export function isRemoteUrl(value) {
  if (typeof value !== 'string' || value.trim().length === 0) return false;
  try {
    const url = new URL(value);
    return url.protocol === 'https:' || url.protocol === 'http:';
  } catch {
    return false;
  }
}

export function normalizeLocalFilePath(value) {
  if (typeof value !== 'string' || value.trim().length === 0) return null;
  if (value.startsWith('file://')) {
    return fileURLToPath(new URL(value));
  }
  return path.resolve(value);
}

export function inferMimeTypeByExtension(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  if (ext === '.jpg' || ext === '.jpeg') return 'image/jpeg';
  if (ext === '.png') return 'image/png';
  if (ext === '.webp') return 'image/webp';
  if (ext === '.gif') return 'image/gif';
  if (ext === '.bmp') return 'image/bmp';
  if (ext === '.tiff' || ext === '.tif') return 'image/tiff';
  if (ext === '.mp4') return 'video/mp4';
  if (ext === '.mov') return 'video/quicktime';
  if (ext === '.mp3') return 'audio/mpeg';
  if (ext === '.wav') return 'audio/wav';
  if (ext === '.txt') return 'text/plain';
  if (ext === '.md') return 'text/markdown';
  if (ext === '.json') return 'application/json';
  return 'application/octet-stream';
}

function extractUploadUrl(res) {
  const list = res?.data?.object_url_list;
  if (Array.isArray(list) && typeof list[0] === 'string' && list[0].trim()) {
    return list[0].trim();
  }
  return null;
}

function makeUploadBatchNo(prefix = 'core-upload') {
  return `${prefix}-${Date.now()}`;
}

function formatBytes(bytes) {
  const mb = bytes / (1024 * 1024);
  return `${mb.toFixed(0)}MB`;
}

function validateUploadCandidate(filePath, fileSize, maxBytes) {
  const ext = path.extname(filePath).toLowerCase();

  if (fileSize > maxBytes) {
    throw new Error(
      `File exceeds maximum upload size (${formatBytes(fileSize)} > ${formatBytes(maxBytes)}). ` +
      'Please use a file smaller than 500MB.',
    );
  }

  if (!ext) {
    throw new Error('File has no extension. Please use a standard image/video/audio/text file and check the suffix.');
  }

  if (BLOCKED_UPLOAD_EXTS.has(ext)) {
    throw new Error(`Disallowed file extension "${ext}". Please upload a valid image/video/audio/text file and check the suffix.`);
  }

  if (!ALLOWED_UPLOAD_EXTS.has(ext)) {
    throw new Error(`Unsupported file extension "${ext}". Please upload a valid image/video/audio/text file and check the suffix.`);
  }
}

export async function uploadLocalFileToPublicUrl(ctx, localPathInput, options = {}) {
  const {
    apiPath = DEFAULT_UPLOAD_API_PATH,
    batchNo = makeUploadBatchNo(),
    fixed = false,
    timeoutMs = Number(ctx.requestTimeoutMs) || 60_000,
    maxBytes = DEFAULT_UPLOAD_MAX_BYTES,
  } = options;

  const localPath = normalizeLocalFilePath(localPathInput);
  if (!localPath) {
    throw new Error(`Invalid local path: ${localPathInput}`);
  }

  const stat = await fs.stat(localPath);
  if (!stat.isFile()) {
    throw new Error(`Local path is not a file: ${localPathInput}`);
  }
  validateUploadCandidate(localPath, stat.size, maxBytes);

  const fileBuffer = await fs.readFile(localPath);
  const fileName = path.basename(localPath);
  const mimeType = inferMimeTypeByExtension(localPath);

  const form = new FormData();
  form.append('file', new Blob([fileBuffer], { type: mimeType }), fileName);
  form.append('batch_no', batchNo);
  form.append('fixed', String(Boolean(fixed)));

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  let res;
  try {
    const defaultOfficialDomains = ['api.weryai.com', 'api-growth-agent.weryai.com'];
    const uploadUrl = new URL(`${ctx.baseUrl}${apiPath}`);
    if (!defaultOfficialDomains.includes(uploadUrl.hostname) && !process.env.WERYAI_ALLOW_INSECURE_UPLOAD) {
        console.warn(`[SECURITY WARNING] Uploading local file to non-official domain: ${uploadUrl.hostname}. Set WERYAI_ALLOW_INSECURE_UPLOAD=1 to suppress this warning if you trust this endpoint.`);
    }

    res = await fetch(uploadUrl, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${ctx.apiKey}`,
      },
      body: form,
      signal: controller.signal,
    });
  } catch (err) {
    clearTimeout(timer);
    if (err.name === 'AbortError') {
      throw new Error(`Upload timeout after ${timeoutMs}ms: ${localPathInput}`);
    }
    throw err;
  }
  clearTimeout(timer);

  let data;
  try {
    data = await res.json();
  } catch {
    throw new Error(`Upload failed with non-JSON response (HTTP ${res.status}).`);
  }

  const wrapped = { httpStatus: res.status, ...data };
  if (!isApiSuccess(wrapped)) {
    const apiErr = formatApiError(wrapped);
    throw new Error(apiErr.errorMessage || `Upload failed (HTTP ${res.status}).`);
  }

  const uploadedUrl = extractUploadUrl(wrapped);
  if (!uploadedUrl) {
    throw new Error('Upload succeeded but data.object_url_list[0] is missing.');
  }

  return uploadedUrl;
}

export async function resolvePublicUrlFromSource(ctx, source, options = {}) {
  if (typeof source !== 'string' || source.trim().length === 0) {
    throw new Error('media source must be a non-empty string.');
  }

  if (isRemoteUrl(source)) return source;

  return uploadLocalFileToPublicUrl(ctx, source, options);
}

export async function resolvePublicUrlsFromSources(ctx, sources, options = {}) {
  return Promise.all((sources || []).map((source) => resolvePublicUrlFromSource(ctx, source, options)));
}
