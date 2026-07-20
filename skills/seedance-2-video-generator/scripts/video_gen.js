#!/usr/bin/env node
/**
 * Werydance 2.0 video generation CLI for WeryAI.
 *
 * Commands:
 *   wait | submit-text | submit-image | submit-multi-image | submit-almighty | status | models
 *
 * Examples:
 *   node video_gen.js models
 *   node video_gen.js wait --json '{"prompt":"A neon koi swims through ink clouds","duration":5}'
 *   node video_gen.js wait --json '{"prompt":"Bridge first and last frame","first_frame":"https://...","last_frame":"https://...","duration":5}'
 *   node video_gen.js wait --json '{"prompt":"Use @video1 style","videos":["./clip.mp4"],"images":["./frame.png"],"duration":5}'
 *   node video_gen.js wait --json '...' --dry-run
 *
 * Required environment variable for paid calls:
 *   WERYAI_API_KEY
 */
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { formatApiError as formatSharedApiError, formatNetworkError as formatSharedNetworkError } from './vendor/weryai-core/errors.js';

const DEFAULT_MODEL = 'WERYDANCE_2_0';
const BASE_URL = (process.env.WERYAI_BASE_URL || 'https://api.weryai.com').replace(/\/$/, '');
const MODELS_BASE_URL = (process.env.WERYAI_MODELS_BASE_URL || 'https://api-growth-agent.weryai.com').replace(
  /\/$/,
  '',
);
const MODELS_API_PATH = '/growthai/v1/video/models';
const UPLOAD_API_PATH = '/v1/generation/upload-file';
const POLL_INTERVAL_MS = Number(process.env.WERYAI_POLL_INTERVAL_MS || 6000);
const POLL_TIMEOUT_OVERRIDE_MS = resolveNonNegativeNumber(process.env.WERYAI_POLL_TIMEOUT_MS);
const SHORT_TASK_TIMEOUT_MS = resolveNonNegativeNumber(process.env.WERYAI_SHORT_TASK_TIMEOUT_MS) ?? 300000;
const LONG_TASK_TIMEOUT_MS = resolveNonNegativeNumber(process.env.WERYAI_LONG_TASK_TIMEOUT_MS) ?? 1200000;
const IMAGE_EXTS = new Set(['.jpg', '.jpeg', '.png', '.webp', '.gif']);
const VIDEO_EXTS = new Set(['.mp4', '.mov']);
const AUDIO_EXTS = new Set(['.mp3', '.wav']);
const IMAGE_SIZE_MAX_BYTES = 10 * 1024 * 1024;
const MEDIA_SIZE_MAX_BYTES = 50 * 1024 * 1024;
const AUDIO_CAPABLE_MODEL_KEYS = new Set([
  'WERYDANCE_2_0',
  'DOUBAO_1_5_PRO',
  'KLING_V3_0_STA',
  'KLING_V3_0_PRO',
  'KLING_V2_6_PRO',
  'VIDU_Q3',
  'VEO_3',
  'VEO_3_FAST',
  'VEO_3_1',
  'VEO_3_1_FAST',
  'CHATBOT_VEO_3_1_FAST',
]);

const STATUS_MAP = {
  waiting: 'waiting',
  WAITING: 'waiting',
  pending: 'waiting',
  PENDING: 'waiting',
  processing: 'processing',
  PROCESSING: 'processing',
  succeed: 'completed',
  SUCCEED: 'completed',
  success: 'completed',
  SUCCESS: 'completed',
  failed: 'failed',
  FAILED: 'failed',
};

function resolveNonNegativeNumber(value) {
  const numeric = Number(value);
  return Number.isFinite(numeric) && numeric >= 0 ? numeric : null;
}

function log(msg) {
  process.stderr.write(`[seedance] ${msg}\n`);
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function coerceBool(value, defaultValue = false) {
  if (value == null) return defaultValue;
  if (typeof value === 'boolean') return value;
  return String(value).toLowerCase() === 'true';
}

function coerceBoolString(value, defaultValue = false) {
  return coerceBool(value, defaultValue) ? 'true' : 'false';
}

function resolveDefaultGenerateAudio(params, modelKey) {
  const userAudio = params.generate_audio ?? params.generateAudio;
  if (userAudio != null) return coerceBool(userAudio, false);
  return AUDIO_CAPABLE_MODEL_KEYS.has(String(modelKey || DEFAULT_MODEL));
}

function isRemoteUrl(value) {
  if (typeof value !== 'string' || value.trim().length === 0) return false;
  try {
    const url = new URL(value);
    return url.protocol === 'https:' || url.protocol === 'http:';
  } catch {
    return false;
  }
}

function normalizeLocalFilePath(value) {
  if (typeof value !== 'string' || value.trim().length === 0) return null;
  if (value.startsWith('file://')) {
    return fileURLToPath(new URL(value));
  }
  return path.resolve(value);
}

function normalizeSourceArray(value) {
  if (Array.isArray(value)) return value;
  if (typeof value === 'string' && value.trim()) return [value];
  return [];
}

function normalizeParams(input) {
  const params = { ...input };
  const firstFrame =
    params.first_frame ??
    params.firstFrame ??
    params.start_frame ??
    params.startFrame ??
    params.first_image ??
    params.firstImage;
  const lastFrame =
    params.last_frame ??
    params.lastFrame ??
    params.end_frame ??
    params.endFrame ??
    params.last_image ??
    params.lastImage;
  const singleImage =
    params.image ??
    params.source_image ??
    params.sourceImage ??
    firstFrame;

  if (singleImage && !params.image) {
    params.image = singleImage;
  }
  if ((!Array.isArray(params.images) || params.images.length === 0) && lastFrame && (firstFrame || params.image)) {
    params.images = [firstFrame || params.image, lastFrame];
  }

  params.videos = normalizeSourceArray(params.videos ?? params.video_refs ?? params.videoRefs);
  params.audios = normalizeSourceArray(params.audios ?? params.audio_refs ?? params.audioRefs);

  if ((params.videos.length > 0 || params.audios.length > 0) && (!Array.isArray(params.images) || params.images.length === 0) && params.image) {
    params.images = [params.image];
  }

  return params;
}

function detectMode(params) {
  if ((Array.isArray(params.videos) && params.videos.length > 0) || (Array.isArray(params.audios) && params.audios.length > 0)) {
    return 'almighty';
  }
  if (Array.isArray(params.images) && params.images.length > 0) return 'multi_image';
  if (typeof params.image === 'string' && params.image) return 'image';
  return 'text';
}

function normalizeTaskClass(value) {
  const normalized = String(value ?? 'auto').trim().toLowerCase();
  if (normalized === 'auto' || normalized === 'short' || normalized === 'long') return normalized;
  return null;
}

function resolveTaskClassFromMode(mode) {
  return mode === 'text' ? 'short' : 'long';
}

function resolvePollTimeoutMs(taskClass) {
  if (POLL_TIMEOUT_OVERRIDE_MS != null) return POLL_TIMEOUT_OVERRIDE_MS;
  return taskClass === 'short' ? SHORT_TASK_TIMEOUT_MS : LONG_TASK_TIMEOUT_MS;
}

function validateSourceValue(value, fieldName, errors) {
  if (typeof value !== 'string' || value.trim().length === 0) {
    errors.push(`${fieldName} must be a non-empty string.`);
    return;
  }
}

async function validateLocalSource(value, kind, fieldName, errors) {
  if (isRemoteUrl(value) || !value || typeof value !== 'string') return;
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
    if (!IMAGE_EXTS.has(ext)) {
      errors.push(`${fieldName} must use one of image formats: jpg, jpeg, png, webp, gif.`);
    }
    if (stat.size > IMAGE_SIZE_MAX_BYTES) {
      errors.push(`${fieldName} exceeds 10MB image limit.`);
    }
    return;
  }

  if (kind === 'video') {
    if (!VIDEO_EXTS.has(ext)) {
      errors.push(`${fieldName} must use one of video formats: mp4, mov.`);
    }
    if (stat.size > MEDIA_SIZE_MAX_BYTES) {
      errors.push(`${fieldName} exceeds 50MB media limit.`);
    }
    return;
  }

  if (kind === 'audio') {
    if (!AUDIO_EXTS.has(ext)) {
      errors.push(`${fieldName} must use one of audio formats: mp3, wav.`);
    }
    if (stat.size > MEDIA_SIZE_MAX_BYTES) {
      errors.push(`${fieldName} exceeds 50MB media limit.`);
    }
  }
}

async function validateParams(params) {
  const errors = [];
  const mode = detectMode(params);
  const firstFrame =
    params.first_frame ??
    params.firstFrame ??
    params.start_frame ??
    params.startFrame ??
    params.first_image ??
    params.firstImage ??
    params.image;
  const lastFrame =
    params.last_frame ??
    params.lastFrame ??
    params.end_frame ??
    params.endFrame ??
    params.last_image ??
    params.lastImage;

  if (!params.prompt || typeof params.prompt !== 'string' || params.prompt.trim().length === 0) {
    errors.push('prompt is required and must be a non-empty string.');
  }

  const duration = params.duration ?? params.dur;
  if (duration == null) {
    errors.push('duration is required (integer seconds).');
  } else {
    const numericDuration = Number(duration);
    if (!Number.isInteger(numericDuration) || numericDuration < 1) {
      errors.push('duration must be a positive integer (seconds).');
    }
    if (mode === 'almighty' && (numericDuration < 5 || numericDuration > 15)) {
      errors.push('almighty duration must be between 5 and 15 seconds.');
    }
  }

  if (!firstFrame && lastFrame) {
    errors.push('last_frame/last_image requires a start image (`image` or `first_frame`).');
  }

  if (mode === 'text') {
    return errors;
  }

  if (mode === 'image') {
    validateSourceValue(params.image, 'image', errors);
    await validateLocalSource(params.image, 'image', 'image', errors);
    return errors;
  }

  if (mode === 'multi_image') {
    if (!Array.isArray(params.images) || params.images.length === 0) {
      errors.push('images must be a non-empty array.');
      return errors;
    }
    params.images.forEach((url, index) => validateSourceValue(url, `images[${index}]`, errors));
    await Promise.all(params.images.map((url, index) => validateLocalSource(url, 'image', `images[${index}]`, errors)));
    return errors;
  }

  if (params.prompt && params.prompt.length > 500) {
    errors.push(`almighty prompt exceeds 500 characters (${params.prompt.length}/500).`);
  }

  const images = Array.isArray(params.images) ? params.images : [];
  const videos = Array.isArray(params.videos) ? params.videos : [];
  const audios = Array.isArray(params.audios) ? params.audios : [];

  if (images.length > 9) errors.push('almighty images must be <= 9.');
  if (videos.length > 3) errors.push('almighty videos must be <= 3.');
  if (audios.length > 3) errors.push('almighty audios must be <= 3.');
  if (images.length + videos.length + audios.length > 12) {
    errors.push('almighty mixed input total must be <= 12 files.');
  }
  if (images.length === 0 && videos.length === 0) {
    errors.push('almighty requires at least one of `images` or `videos`.');
  }

  if (params.video_number != null) {
    const n = Number(params.video_number);
    if (!Number.isInteger(n) || n < 1 || n > 4) {
      errors.push('video_number must be an integer between 1 and 4.');
    }
  }

  images.forEach((value, index) => validateSourceValue(value, `images[${index}]`, errors));
  videos.forEach((value, index) => validateSourceValue(value, `videos[${index}]`, errors));
  audios.forEach((value, index) => validateSourceValue(value, `audios[${index}]`, errors));

  await Promise.all([
    ...images.map((value, index) => validateLocalSource(value, 'image', `images[${index}]`, errors)),
    ...videos.map((value, index) => validateLocalSource(value, 'video', `videos[${index}]`, errors)),
    ...audios.map((value, index) => validateLocalSource(value, 'audio', `audios[${index}]`, errors)),
  ]);

  return errors;
}

function buildRequestBody(params, mode = detectMode(params)) {
  const body = {
    prompt: params.prompt,
    model: params.model || DEFAULT_MODEL,
    duration: Number(params.duration ?? params.dur) || 5,
  };

  if (params.aspect_ratio) body.aspect_ratio = params.aspect_ratio;
  if (params.resolution) body.resolution = params.resolution;

  if (mode === 'almighty') {
    if (Array.isArray(params.images) && params.images.length > 0) body.images = params.images.slice(0, 9);
    if (Array.isArray(params.videos) && params.videos.length > 0) body.videos = params.videos.slice(0, 3);
    if (Array.isArray(params.audios) && params.audios.length > 0) body.audios = params.audios.slice(0, 3);
    body.generate_audio = coerceBoolString(resolveDefaultGenerateAudio(params, body.model), false);
    if (params.video_number != null) {
      body.video_number = Number(params.video_number);
    }
    return body;
  }

  body.generate_audio = resolveDefaultGenerateAudio(params, body.model);
  if (params.negative_prompt || params.negativePrompt) {
    body.negative_prompt = params.negative_prompt || params.negativePrompt;
  }
  if (mode === 'image' && params.image) {
    body.image = params.image;
  }
  if (mode === 'multi_image' && Array.isArray(params.images) && params.images.length > 0) {
    body.images = params.images.slice(0, 3);
  }

  return body;
}

function collectLocalSources(body, mode) {
  const out = [];
  const collect = (fieldName, values, kind) => {
    values.forEach((value, idx) => {
      if (typeof value === 'string' && value.trim() && !isRemoteUrl(value)) {
        out.push({ field: `${fieldName}[${idx}]`, source: value, kind });
      }
    });
  };

  if (mode === 'image' && typeof body.image === 'string' && !isRemoteUrl(body.image)) {
    out.push({ field: 'image', source: body.image, kind: 'image' });
  }
  if (mode === 'multi_image' || mode === 'almighty') {
    collect('images', Array.isArray(body.images) ? body.images : [], 'image');
  }
  if (mode === 'almighty') {
    collect('videos', Array.isArray(body.videos) ? body.videos : [], 'video');
    collect('audios', Array.isArray(body.audios) ? body.audios : [], 'audio');
  }

  return out;
}

async function httpJson(method, fullUrl, body, apiKey) {
  const headers = {
    Authorization: `Bearer ${apiKey}`,
    'Content-Type': 'application/json',
  };
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 30000);

  try {
    const res = await fetch(fullUrl, {
      method,
      headers,
      body: body != null ? JSON.stringify(body) : undefined,
      signal: controller.signal,
    });
    clearTimeout(timer);

    let data;
    try {
      data = await res.json();
    } catch {
      data = { status: res.status, msg: `Non-JSON response (HTTP ${res.status})` };
    }

    return { httpStatus: res.status, ...data };
  } catch (err) {
    clearTimeout(timer);
    if (err.name === 'AbortError') {
      throw new Error(`Request timeout: ${method} ${fullUrl}`);
    }
    throw err;
  }
}

async function apiRequest(method, pathName, body, apiKey) {
  return httpJson(method, BASE_URL + pathName, body, apiKey);
}

async function fetchModelsRegistry(apiKey) {
  return httpJson('GET', MODELS_BASE_URL + MODELS_API_PATH, null, apiKey);
}

function isApiSuccess(res) {
  const httpOk = res.httpStatus >= 200 && res.httpStatus < 300;
  const bodyOk = res.status === 0 || res.status === 200;
  return httpOk && bodyOk;
}

function formatApiError(res) {
  return formatSharedApiError(res);
}

function formatNetworkError(err) {
  return formatSharedNetworkError(err);
}

function inferMimeTypeByExtension(filePath) {
  const ext = path.extname(filePath).toLowerCase();
  if (IMAGE_EXTS.has(ext)) {
    if (ext === '.jpg' || ext === '.jpeg') return 'image/jpeg';
    if (ext === '.png') return 'image/png';
    if (ext === '.webp') return 'image/webp';
    if (ext === '.gif') return 'image/gif';
  }
  if (VIDEO_EXTS.has(ext)) {
    if (ext === '.mp4') return 'video/mp4';
    if (ext === '.mov') return 'video/quicktime';
  }
  if (AUDIO_EXTS.has(ext)) {
    if (ext === '.mp3') return 'audio/mpeg';
    if (ext === '.wav') return 'audio/wav';
  }
  return 'application/octet-stream';
}

function extractUploadUrl(res) {
  const list = res?.data?.object_url_list;
  if (Array.isArray(list) && typeof list[0] === 'string' && list[0].trim()) {
    return list[0].trim();
  }
  return null;
}

function makeUploadBatchNo() {
  return `seedance-upload-${Date.now()}`;
}

async function uploadLocalSource(localPathInput, apiKey) {
  const localPath = normalizeLocalFilePath(localPathInput);
  if (!localPath) {
    throw new Error(`Invalid local path: ${localPathInput}`);
  }

  const stat = await fs.stat(localPath);
  if (!stat.isFile()) {
    throw new Error(`Local path is not a file: ${localPathInput}`);
  }

  const fileBuffer = await fs.readFile(localPath);
  const fileName = path.basename(localPath);
  const mimeType = inferMimeTypeByExtension(localPath);
  const form = new FormData();
  form.append('file', new Blob([fileBuffer], { type: mimeType }), fileName);
  form.append('batch_no', makeUploadBatchNo());
  form.append('fixed', 'false');

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 60000);

  let res;
  try {
    res = await fetch(`${BASE_URL}${UPLOAD_API_PATH}`, {
      method: 'POST',
      headers: {
        Authorization: `Bearer ${apiKey}`,
      },
      body: form,
      signal: controller.signal,
    });
  } catch (err) {
    clearTimeout(timer);
    if (err.name === 'AbortError') {
      throw new Error(`Upload timeout: ${localPathInput}`);
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

async function ensurePublicSource(value, apiKey) {
  if (typeof value !== 'string' || value.trim().length === 0) {
    throw new Error('media source must be a non-empty string.');
  }

  if (isRemoteUrl(value)) return value;

  log(`Uploading local source: ${value}`);
  return uploadLocalSource(value, apiKey);
}

async function prepareBodyWithUploads(body, mode, apiKey) {
  const out = { ...body };

  if (mode === 'image' && out.image) {
    out.image = await ensurePublicSource(out.image, apiKey);
  }
  if ((mode === 'multi_image' || mode === 'almighty') && Array.isArray(out.images) && out.images.length > 0) {
    out.images = await Promise.all(out.images.map((item) => ensurePublicSource(item, apiKey)));
  }
  if (mode === 'almighty') {
    if (Array.isArray(out.videos) && out.videos.length > 0) {
      out.videos = await Promise.all(out.videos.map((item) => ensurePublicSource(item, apiKey)));
    }
    if (Array.isArray(out.audios) && out.audios.length > 0) {
      out.audios = await Promise.all(out.audios.map((item) => ensurePublicSource(item, apiKey)));
    }
  }

  return out;
}

function extractVideos(taskData) {
  const result = taskData.task_result || {};
  const raw = result.videos || taskData.videos || [];
  return raw.map((item) => {
    if (typeof item === 'string') {
      return { url: item, cover_url: '' };
    }
    return {
      url: item?.url || item?.video_url || '',
      cover_url: item?.cover_image_url || item?.cover_url || '',
    };
  });
}

async function submitTask(params, apiKey, allowedModes = null) {
  const errors = await validateParams(params);
  if (errors.length > 0) {
    return { ok: false, phase: 'failed', errorCode: 'VALIDATION', errorMessage: errors.join(' ') };
  }

  const mode = detectMode(params);
  if (Array.isArray(allowedModes) && allowedModes.length > 0 && !allowedModes.includes(mode)) {
    return {
      ok: false,
      phase: 'failed',
      errorCode: 'VALIDATION',
      errorMessage: `This command expects mode ${allowedModes.join(' or ')}, but the normalized payload resolves to ${mode}.`,
    };
  }

  const pathMap = {
    text: '/v1/generation/text-to-video',
    image: '/v1/generation/image-to-video',
    multi_image: '/v1/generation/multi-image-to-video',
    almighty: '/v1/generation/almighty-reference-to-video',
  };

  const rawBody = buildRequestBody(params, mode);
  let body;
  try {
    body = await prepareBodyWithUploads(rawBody, mode, apiKey);
  } catch (err) {
    return {
      ok: false,
      phase: 'failed',
      errorCode: 'UPLOAD_FAILED',
      errorMessage: err.message || String(err),
    };
  }

  let res;
  try {
    res = await apiRequest('POST', pathMap[mode], body, apiKey);
  } catch (err) {
    return formatNetworkError(err);
  }

  if (!isApiSuccess(res)) return formatApiError(res);

  const data = res.data || {};
  const taskIds = data.task_ids ?? (data.task_id ? [data.task_id] : []);
  return {
    ok: true,
    phase: 'submitted',
    requestMode: mode,
    batchId: data.batch_id ?? null,
    taskIds,
    taskId: taskIds[0] ?? null,
    taskStatus: null,
    videos: null,
    errorTitle: null,
    errorCode: null,
    errorCategory: null,
    retryable: null,
    errorMessage: null,
  };
}

async function pollUntilDone(taskId, batchId, taskIds, apiKey, pollTimeoutMs) {
  const start = Date.now();

  while (true) {
    if (Date.now() - start >= pollTimeoutMs) {
      return {
        ok: false,
        phase: 'failed',
        errorTitle: 'Request timed out',
        errorCode: 'TIMEOUT',
        errorCategory: 'timeout',
        retryable: true,
        errorMessage: `Poll timeout after ${Math.floor((Date.now() - start) / 1000)}s.`,
        batchId,
        taskIds,
        taskId,
        taskStatus: 'unknown',
        videos: null,
      };
    }

    await sleep(POLL_INTERVAL_MS);

    let res;
    try {
      res = await apiRequest('GET', `/v1/generation/${taskId}/status`, null, apiKey);
    } catch (err) {
      log(`Warning: poll failed (${err.message}). Retrying.`);
      continue;
    }

    if (!isApiSuccess(res)) {
      log('Warning: poll returned non-success status. Retrying.');
      continue;
    }

    const taskData = res.data || {};
    const rawStatus = taskData.task_status || '';
    const normalized = STATUS_MAP[rawStatus] || 'unknown';
    log(`Polling ${taskId}: ${rawStatus || 'unknown'}`);

    if (normalized === 'completed') {
      const videos = extractVideos(taskData);
      return {
        ok: true,
        phase: 'completed',
        batchId,
        taskIds,
        taskId,
        taskStatus: rawStatus,
        videos: videos.length > 0 ? videos : null,
        errorTitle: null,
        errorCode: null,
        errorCategory: null,
        retryable: null,
        errorMessage: null,
      };
    }

    if (normalized === 'failed') {
      const result = taskData.task_result || {};
      return {
        ok: false,
        phase: 'failed',
        batchId,
        taskIds,
        taskId,
        taskStatus: rawStatus,
        videos: null,
        errorTitle: 'Task failed',
        errorCode: 'TASK_FAILED',
        errorCategory: 'task',
        retryable: false,
        errorMessage: result.message || taskData.msg || 'The task could not be completed. Please review the request and try again.',
      };
    }
  }
}

async function cmdWait(params, apiKey, taskClassRaw) {
  const requestedTaskClass = normalizeTaskClass(taskClassRaw ?? params.task_class ?? params.taskClass ?? 'auto');
  if (!requestedTaskClass) {
    return {
      ok: false,
      phase: 'failed',
      errorCode: 'VALIDATION',
      errorMessage: 'task_class must be one of: auto, short, long.',
    };
  }

  const submitResult = await submitTask(params, apiKey);
  if (!submitResult.ok) return submitResult;

  const taskClass = requestedTaskClass === 'auto'
    ? resolveTaskClassFromMode(submitResult.requestMode)
    : requestedTaskClass;
  const pollTimeoutMs = resolvePollTimeoutMs(taskClass);
  const result = await pollUntilDone(
    submitResult.taskId,
    submitResult.batchId,
    submitResult.taskIds || [submitResult.taskId],
    apiKey,
    pollTimeoutMs,
  );
  return { ...result, taskClass, pollTimeoutMs };
}

async function cmdStatus(taskId, apiKey) {
  let res;
  try {
    res = await apiRequest('GET', `/v1/generation/${taskId}/status`, null, apiKey);
  } catch (err) {
    return formatNetworkError(err);
  }

  if (!isApiSuccess(res)) return formatApiError(res);

  const taskData = res.data || {};
  const rawStatus = taskData.task_status || '';
  const normalized = STATUS_MAP[rawStatus] || 'unknown';
  const videos = extractVideos(taskData);
  const phase = normalized === 'completed' ? 'completed' : normalized === 'failed' ? 'failed' : 'running';
  const result = taskData.task_result || {};

  return {
    ok: phase !== 'failed',
    phase,
    batchId: null,
    taskIds: [taskId],
    taskId,
    taskStatus: rawStatus,
    videos: videos.length > 0 ? videos : null,
    errorTitle: phase === 'failed' ? 'Task failed' : null,
    errorCode: phase === 'failed' ? 'TASK_FAILED' : null,
    errorCategory: phase === 'failed' ? 'task' : null,
    retryable: phase === 'failed' ? false : null,
    errorMessage: phase === 'failed' ? result.message || taskData.msg || 'The task could not be completed. Please review the request and try again.' : null,
  };
}

const VALID_MODEL_MODES = ['text_to_video', 'image_to_video', 'multi_image_to_video'];

async function cmdModels(modeFilter, apiKey) {
  let res;
  try {
    res = await fetchModelsRegistry(apiKey);
  } catch (err) {
    return formatNetworkError(err);
  }

  if (!isApiSuccess(res)) return formatApiError(res);

  const data = res.data || {};
  const out = { ok: true, phase: 'completed' };

  if (modeFilter) {
    if (!VALID_MODEL_MODES.includes(modeFilter)) {
      return {
        ok: false,
        phase: 'failed',
        errorCode: 'VALIDATION',
        errorMessage: `Invalid --mode. Use one of: ${VALID_MODEL_MODES.join(', ')}`,
      };
    }
    out[modeFilter] = data[modeFilter] || [];
    return out;
  }

  out.text_to_video = data.text_to_video || [];
  out.image_to_video = data.image_to_video || [];
  out.multi_image_to_video = data.multi_image_to_video || [];
  return out;
}

function parseArgs(argv) {
  const command = argv[0];
  let jsonStr = null;
  let taskId = null;
  let dryRun = false;
  let modelsMode = null;
  let taskClass = null;

  for (let i = 1; i < argv.length; i += 1) {
    if (argv[i] === '--json') jsonStr = argv[++i];
    else if (argv[i] === '--task-id') taskId = argv[++i];
    else if (argv[i] === '--dry-run') dryRun = true;
    else if (argv[i] === '--mode') modelsMode = argv[++i];
    else if (argv[i] === '--task-class') taskClass = argv[++i];
  }

  return { command, jsonStr, taskId, dryRun, modelsMode, taskClass };
}

function getAllowedModesForCommand(command) {
  if (command === 'submit-text') return ['text'];
  if (command === 'submit-image') return ['image', 'multi_image'];
  if (command === 'submit-multi-image') return ['multi_image'];
  if (command === 'submit-almighty') return ['almighty'];
  return null;
}

function printJson(obj) {
  process.stdout.write(`${JSON.stringify(obj, null, 2)}\n`);
}

async function main() {
  const validCommands = new Set(['wait', 'submit-text', 'submit-image', 'submit-multi-image', 'submit-almighty', 'status', 'models']);
  const { command, jsonStr, taskId: cliTaskId, dryRun, modelsMode, taskClass } = parseArgs(process.argv.slice(2));

  if (!command || !validCommands.has(command)) {
    printJson({
      ok: false,
      phase: 'failed',
      errorCode: 'USAGE',
      errorMessage:
        'Usage: node video_gen.js <wait|submit-text|submit-image|submit-multi-image|submit-almighty|status|models> [--json \'...\'] [--task-id id] [--dry-run] [--task-class auto|short|long] [--mode text_to_video|image_to_video|multi_image_to_video]',
    });
    process.exit(1);
  }

  let params = {};
  if (jsonStr) {
    try {
      params = normalizeParams(JSON.parse(jsonStr));
    } catch (err) {
      printJson({ ok: false, phase: 'failed', errorCode: 'INVALID_JSON', errorMessage: `Invalid JSON: ${err.message}` });
      process.exit(1);
    }
  }

  if (command === 'models') {
    const apiKey = (process.env.WERYAI_API_KEY || '').trim();
    if (!apiKey) {
      printJson({ ok: false, phase: 'failed', errorTitle: 'Missing API key', errorCode: 'NO_API_KEY', errorCategory: 'auth', retryable: false, errorMessage: 'Missing WERYAI_API_KEY environment variable.' });
      process.exit(1);
    }
    const result = await cmdModels(modelsMode, apiKey);
    printJson(result);
    process.exit(result.ok ? 0 : 1);
  }

  if (dryRun) {
    const validationErrors = command === 'status' ? [] : await validateParams(params);
    if (validationErrors.length > 0) {
      printJson({ ok: false, phase: 'failed', errorTitle: 'Invalid request', errorCode: 'VALIDATION', errorCategory: 'validation', retryable: false, errorMessage: validationErrors.join(' ') });
      process.exit(1);
    }

    const mode = detectMode(params);
    const allowedModes = getAllowedModesForCommand(command);
    if (Array.isArray(allowedModes) && allowedModes.length > 0 && !allowedModes.includes(mode)) {
      printJson({
        ok: false,
        phase: 'failed',
        errorTitle: 'Invalid request',
        errorCode: 'VALIDATION',
        errorCategory: 'validation',
        retryable: false,
        errorMessage: `This command expects mode ${allowedModes.join(' or ')}, but the normalized payload resolves to ${mode}.`,
      });
      process.exit(1);
    }

    const pathMap = {
      text: '/v1/generation/text-to-video',
      image: '/v1/generation/image-to-video',
      multi_image: '/v1/generation/multi-image-to-video',
      almighty: '/v1/generation/almighty-reference-to-video',
    };
    const requestBody = command === 'status' ? {} : buildRequestBody(params, mode);
    const dryRunTaskClassRaw = normalizeTaskClass(taskClass ?? params.task_class ?? params.taskClass ?? 'auto');
    if (!dryRunTaskClassRaw) {
      printJson({ ok: false, phase: 'failed', errorCode: 'VALIDATION', errorMessage: 'task_class must be one of: auto, short, long.' });
      process.exit(1);
    }
    const dryRunTaskClass = dryRunTaskClassRaw === 'auto' ? resolveTaskClassFromMode(mode) : dryRunTaskClassRaw;
    const dryRunPollTimeoutMs = resolvePollTimeoutMs(dryRunTaskClass);

    printJson({
      ok: true,
      phase: 'dry-run',
      dryRun: true,
      requestMode: mode,
      taskClass: dryRunTaskClass,
      pollTimeoutMs: dryRunPollTimeoutMs,
      requestBody,
      requestUrl: BASE_URL + (pathMap[mode] || pathMap.text),
      uploadPreview: command === 'status' ? [] : collectLocalSources(requestBody, mode),
      notes: 'dry-run does not upload local files. Local sources in uploadPreview will be uploaded in a real run via /v1/generation/upload-file.',
    });
    process.exit(0);
  }

  const apiKey = (process.env.WERYAI_API_KEY || '').trim();
  if (!apiKey) {
    printJson({ ok: false, phase: 'failed', errorTitle: 'Missing API key', errorCode: 'NO_API_KEY', errorCategory: 'auth', retryable: false, errorMessage: 'Missing WERYAI_API_KEY environment variable.' });
    process.exit(1);
  }

  let result;
  if (command === 'status') {
    const taskId = cliTaskId || params.task_id || params.taskId;
    if (!taskId) {
      printJson({ ok: false, phase: 'failed', errorCode: 'MISSING_PARAM', errorMessage: 'status requires --task-id <id>.' });
      process.exit(1);
    }
    result = await cmdStatus(taskId, apiKey);
  } else {
    result =
      command === 'wait'
        ? await cmdWait(params, apiKey, taskClass)
        : await submitTask(params, apiKey, getAllowedModesForCommand(command));
  }

  printJson(result);
  process.exit(result.ok ? 0 : 1);
}

main().catch((err) => {
  printJson({ ok: false, phase: 'failed', errorCode: 'FATAL', errorMessage: err.message || String(err) });
  process.exit(1);
});
