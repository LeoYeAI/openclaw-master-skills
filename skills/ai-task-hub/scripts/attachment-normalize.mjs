import { extname } from 'node:path';

export const DEFAULT_SITE_BASE_URL = 'https://gateway.binaryworks.app';
const DIRECT_UPLOAD_PATH = '/api/blob/upload-file';

const IMAGE_CAPABILITIES = new Set([
  'human_detect',
  'image_tagging',
  'face-detect',
  'person-detect',
  'hand-detect',
  'body-keypoints-2d',
  'body-contour-63pt',
  'face-keypoints-106pt',
  'head-pose',
  'face-feature-classification',
  'face-action-classification',
  'face-image-quality',
  'face-emotion-recognition',
  'face-physical-attributes',
  'face-social-attributes',
  'political-figure-recognition',
  'designated-person-recognition',
  'exhibit-image-recognition',
  'person-instance-segmentation',
  'person-semantic-segmentation',
  'concert-cutout',
  'full-body-matting',
  'head-matting',
  'product-cutout'
]);

const MIME_BY_EXTENSION = {
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.png': 'image/png',
  '.webp': 'image/webp',
  '.gif': 'image/gif',
  '.mp3': 'audio/mpeg',
  '.wav': 'audio/wav',
  '.webm': 'audio/webm',
  '.ogg': 'audio/ogg',
  '.m4a': 'audio/mp4',
  '.mp4': 'audio/mp4',
  '.pdf': 'application/pdf',
  '.txt': 'text/plain',
  '.md': 'text/markdown',
  '.markdown': 'text/markdown'
};

export async function normalizeExecutePayload(payloadRaw, _options = {}) {
  const payload = toObject(payloadRaw);
  const capability = typeof payload.capability === 'string' ? payload.capability.trim() : '';
  const input = toObject(payload.input);

  const normalizedInput = { ...input };
  const explicitNormalized = normalizeExplicitUrlFields(normalizedInput, payload);

  if (!explicitNormalized) {
    const attachmentUrl = resolveAttachmentUrl(normalizedInput, payload);
    const targetFromCapability = resolveTargetField(capability);
    if (attachmentUrl) {
      const target = targetFromCapability ?? resolveTargetFieldFromUrl(attachmentUrl) ?? 'file_url';
      normalizedInput[target] = attachmentUrl;
    }
  }

  if (!hasAnyMediaUrl(normalizedInput)) {
    const localAttachment = resolveLocalAttachment(normalizedInput, payload);
    if (localAttachment) {
      throw createNormalizeError(
        400,
        'VALIDATION_FILE_PATH_NOT_SUPPORTED',
        'local file_path is disabled in the published ai-task-hub skill; upload the chat attachment through your host product and pass attachment.url or image_url/audio_url/file_url',
        {
          file_path: localAttachment.filePath,
          supported_inputs: ['attachment.url', 'image_url', 'audio_url', 'file_url'],
          recommended_upload_api: `${DEFAULT_SITE_BASE_URL}${DIRECT_UPLOAD_PATH}`
        }
      );
    }
  }

  return {
    ...payload,
    input: normalizedInput
  };
}

function toObject(value) {
  if (!value || typeof value !== 'object' || Array.isArray(value)) {
    return {};
  }
  return { ...value };
}

function normalizeExplicitUrlFields(input, payload) {
  let found = false;
  for (const field of ['image_url', 'audio_url', 'file_url']) {
    const inInput = typeof input[field] === 'string' ? input[field].trim() : '';
    if (inInput) {
      input[field] = inInput;
      found = true;
      continue;
    }

    const inPayload = typeof payload[field] === 'string' ? payload[field].trim() : '';
    if (inPayload) {
      input[field] = inPayload;
      found = true;
    }
  }
  return found;
}

function resolveAttachmentUrl(input, payload) {
  const fromInput = readNestedString(input, ['attachment', 'url']);
  if (fromInput) {
    return fromInput;
  }
  return readNestedString(payload, ['attachment', 'url']);
}

function resolveLocalAttachment(input, payload) {
  const filePath =
    readOptionalString(input.file_path) ||
    readOptionalString(payload.file_path) ||
    readNestedString(input, ['attachment', 'path']) ||
    readNestedString(payload, ['attachment', 'path']) ||
    readNestedString(input, ['attachment', 'file_path']) ||
    readNestedString(payload, ['attachment', 'file_path']);

  if (!filePath) {
    return null;
  }

  return {
    filePath
  };
}

function readNestedString(source, pathParts) {
  let current = source;
  for (const part of pathParts) {
    if (!current || typeof current !== 'object') {
      return null;
    }
    current = current[part];
  }
  return readOptionalString(current);
}

function readOptionalString(value) {
  if (typeof value !== 'string') {
    return null;
  }
  const trimmed = value.trim();
  return trimmed ? trimmed : null;
}

function resolveTargetField(capability) {
  if (!capability) {
    return null;
  }
  if (IMAGE_CAPABILITIES.has(capability)) {
    return 'image_url';
  }
  if (capability === 'asr') {
    return 'audio_url';
  }
  if (capability === 'markdown_convert') {
    return 'file_url';
  }
  return null;
}

function hasAnyMediaUrl(input) {
  return ['image_url', 'audio_url', 'file_url'].some(
    (field) => typeof input[field] === 'string' && input[field].trim().length > 0
  );
}

export function resolveTrustedSiteBaseUrl(raw) {
  const candidate = typeof raw === 'string' && raw.trim() ? raw.trim() : DEFAULT_SITE_BASE_URL;
  try {
    const parsed = new URL(candidate);
    if (parsed.protocol !== 'https:' && parsed.protocol !== 'http:') {
      throw new Error('invalid protocol');
    }
    return parsed.toString().replace(/\/+$/, '');
  } catch {
    throw createNormalizeError(400, 'VALIDATION_BAD_REQUEST', `invalid site_base_url: ${raw}`);
  }
}

function resolveTargetFieldFromUrl(rawUrl) {
  try {
    const parsed = new URL(rawUrl);
    const mimeType = MIME_BY_EXTENSION[extname(parsed.pathname).toLowerCase()] ?? '';
    return resolveTargetFieldFromMime(mimeType);
  } catch {
    return null;
  }
}

function resolveTargetFieldFromMime(mimeType) {
  if (mimeType.startsWith('image/')) {
    return 'image_url';
  }
  if (mimeType.startsWith('audio/')) {
    return 'audio_url';
  }
  return 'file_url';
}

function createNormalizeError(status, code, message, details) {
  const error = new Error(message);
  error.status = status;
  error.code = code;
  error.details = details;
  return error;
}
