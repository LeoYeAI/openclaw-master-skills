import fs from 'node:fs/promises';
import path from 'node:path';
import {
  isRemoteUrl,
  normalizeLocalFilePath,
  resolvePublicUrlFromSource,
} from '../weryai-core/upload.js';

const IMAGE_EXTS = new Set(['.jpg', '.jpeg', '.png', '.webp', '.gif']);
const VIDEO_EXTS = new Set(['.mp4', '.mov']);
const AUDIO_EXTS = new Set(['.mp3', '.wav']);
const IMAGE_SIZE_MAX_BYTES = 10 * 1024 * 1024;
const MEDIA_SIZE_MAX_BYTES = 50 * 1024 * 1024;

export function normalizeSourceArray(value) {
  if (Array.isArray(value)) return value;
  if (typeof value === 'string' && value.trim()) return [value];
  return [];
}

export { isRemoteUrl, normalizeLocalFilePath };

export function collectLocalUploadPreview(input, mode) {
  const out = [];
  const collect = (fieldName, values, kind) => {
    values.forEach((value, idx) => {
      if (typeof value === 'string' && value.trim() && !isRemoteUrl(value)) {
        out.push({ field: `${fieldName}[${idx}]`, source: value, kind });
      }
    });
  };

  if (mode === 'image_to_video' && typeof input.image === 'string' && !isRemoteUrl(input.image)) {
    out.push({ field: 'image', source: input.image, kind: 'image' });
  }
  if ((mode === 'multi_image_to_video' || mode === 'almighty_reference_to_video') && Array.isArray(input.images)) {
    collect('images', input.images, 'image');
  }
  if (mode === 'almighty_reference_to_video') {
    if (Array.isArray(input.videos)) collect('videos', input.videos, 'video');
    if (Array.isArray(input.audios)) collect('audios', input.audios, 'audio');
  }

  return out;
}

export async function validateLocalSource(value, kind, fieldName, errors) {
  if (!value || typeof value !== 'string') return;
  if (isRemoteUrl(value)) {
    return;
  }
  const localPath = normalizeLocalFilePath(value);
  if (!localPath) {
    errors.push(`${fieldName} local path is invalid.`);
    return;
  }

  let stat;
  try {
    stat = await fs.stat(localPath);
  } catch {
    errors.push(`${fieldName} local file not found: ${value}`);
    return;
  }

  if (!stat.isFile()) {
    errors.push(`${fieldName} local path is not a file: ${value}`);
    return;
  }

  const ext = path.extname(localPath).toLowerCase();
  if (kind === 'image') {
    if (!IMAGE_EXTS.has(ext)) errors.push(`${fieldName} must use one of image formats: jpg, jpeg, png, webp, gif.`);
    if (stat.size > IMAGE_SIZE_MAX_BYTES) errors.push(`${fieldName} exceeds 10MB image limit.`);
    return;
  }

  if (kind === 'video') {
    if (!VIDEO_EXTS.has(ext)) errors.push(`${fieldName} must use one of video formats: mp4, mov.`);
    if (stat.size > MEDIA_SIZE_MAX_BYTES) errors.push(`${fieldName} exceeds 50MB media limit.`);
    return;
  }

  if (kind === 'audio') {
    if (!AUDIO_EXTS.has(ext)) errors.push(`${fieldName} must use one of audio formats: mp3, wav.`);
    if (stat.size > MEDIA_SIZE_MAX_BYTES) errors.push(`${fieldName} exceeds 50MB media limit.`);
  }
}

export async function resolveUploadSources(ctx, body, mode) {
  const out = { ...body };

  if (mode === 'image_to_video' && out.image) {
    out.image = await resolvePublicUrlFromSource(ctx, out.image);
  }

  if ((mode === 'multi_image_to_video' || mode === 'almighty_reference_to_video') && Array.isArray(out.images)) {
    out.images = await Promise.all(out.images.map((item) => resolvePublicUrlFromSource(ctx, item)));
  }

  if (mode === 'almighty_reference_to_video') {
    if (Array.isArray(out.videos)) {
      out.videos = await Promise.all(out.videos.map((item) => resolvePublicUrlFromSource(ctx, item)));
    }
    if (Array.isArray(out.audios)) {
      out.audios = await Promise.all(out.audios.map((item) => resolvePublicUrlFromSource(ctx, item)));
    }
  }

  return out;
}

export const FILE_LIMITS = {
  imageMaxBytes: IMAGE_SIZE_MAX_BYTES,
  mediaMaxBytes: MEDIA_SIZE_MAX_BYTES,
};
