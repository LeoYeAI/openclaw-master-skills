#!/usr/bin/env node
const fs = require('node:fs/promises');
const path = require('node:path');
const { fileURLToPath } = require('node:url');
const { formatApiError: formatSharedApiError, formatNetworkError: formatSharedNetworkError } = require('../../../core/weryai-core/errors.js');
/**
 * WeryAI 视频生成 — 通用 CLI（零 npm 依赖，需 Node.js 18+）
 *
 * 命令:
 *   wait | submit-text | submit-image | submit-multi-image | status | models
 *
 * 示例:
 *   node video_gen.js models
 *   node video_gen.js models --mode text_to_video
 *   node video_gen.js wait --json '{"model":"WERYAI_VIDEO_1_0","prompt":"...","duration":5}'
 *   node video_gen.js wait --json '{"model":"...","prompt":"...","image":"./local.png","duration":5}'
 *   node video_gen.js wait --json '...' --dry-run
 *
 * 环境变量:
 *   WERYAI_API_KEY（models / 生成 / status 必填；--dry-run 除外）— 敏感凭据，勿写入仓库；registry 元数据声明见同目录 SKILL.md。
 *   本脚本仅读取上述密钥；API 主机与轮询间隔为固定常量，勿用其他 env 覆盖。
 */

const BASE_URL = 'https://api.weryai.com';
const MODELS_BASE_URL = 'https://api-growth-agent.weryai.com';
const MODELS_API_PATH = '/growthai/v1/video/models';
const UPLOAD_API_PATH = '/growthai/v1/generation/upload-file';
const POLL_INTERVAL_MS = 6000;
const POLL_TIMEOUT_MS = 600000;
const IMAGE_MIME_TYPES = {
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.png': 'image/png',
  '.webp': 'image/webp',
  '.gif': 'image/gif',
};

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

const ERROR_MESSAGES = {
  400: 'Bad request — check your request parameters.',
  403: 'Invalid API key or IP access denied — verify WERYAI_API_KEY is correct.',
  500: 'WeryAI server error. Please try again later.',
  1001: 'Request rate limit exceeded — slow down and retry after a moment.',
  1002: 'Parameter error — check prompt, image URLs, aspect_ratio, model key, and duration.',
  1003: 'Resource not found — the task_id may not exist or has expired.',
  1006: 'Model not supported — check the model key or try a different model.',
  1007: 'Queue full — the service is busy, please try again later.',
  1011: 'Insufficient credits — recharge at weryai.com.',
  2003: 'Content flagged by safety system — revise your prompt or input image.',
  2004: 'Image format not supported — use jpg, png, or webp.',
  6004: 'Generation failed — please try again later.',
  6010: 'Concurrent task limit reached (max 20) — wait for existing tasks to complete.',
};

function log(msg) {
  process.stderr.write(`[weryai] ${msg}\n`);
}

function sleep(ms) {
  return new Promise((r) => setTimeout(r, ms));
}

async function httpJson(method, fullUrl, body, apiKey) {
  const headers = {
    Authorization: `Bearer ${apiKey}`,
    'Content-Type': 'application/json',
  };
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 30_000);
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

async function apiRequest(method, path, body, apiKey) {
  return httpJson(method, BASE_URL + path, body, apiKey);
}

async function fetchModelsRegistry(apiKey) {
  return httpJson('GET', MODELS_BASE_URL + MODELS_API_PATH, null, apiKey);
}

function isPublicHttpsUrl(value) {
  if (typeof value !== 'string' || !value.trim()) return false;
  try {
    const url = new URL(value);
    return url.protocol === 'https:';
  } catch {
    return false;
  }
}

function isRemoteUrl(value) {
  if (typeof value !== 'string' || !value.trim()) return false;
  try {
    const url = new URL(value);
    return url.protocol === 'https:' || url.protocol === 'http:';
  } catch {
    return false;
  }
}

function normalizeLocalFilePath(value) {
  if (typeof value !== 'string' || !value.trim()) return null;
  if (value.startsWith('file://')) {
    return new URL(value);
  }
  return path.resolve(value);
}

function inferMimeType(filePath) {
  return IMAGE_MIME_TYPES[path.extname(filePath).toLowerCase()] || 'application/octet-stream';
}

function makeUploadBatchNo() {
  return `video-gen-${Date.now()}`;
}

function collectPossibleUploadUrls(data) {
  const candidates = [];
  if (!data) return candidates;
  const maybePush = (value) => {
    if (typeof value === 'string' && value.trim()) candidates.push(value.trim());
  };
  const maybePushMany = (value) => {
    if (Array.isArray(value)) {
      for (const item of value) maybePush(item);
    }
  };

  maybePush(data.url);
  maybePush(data.file_url);
  maybePush(data.fileUrl);
  maybePush(data.https_url);
  maybePush(data.httpsUrl);
  maybePush(data.public_url);
  maybePush(data.publicUrl);
  maybePush(data.object_url);
  maybePush(data.objectUrl);
  maybePush(data.origin_url);
  maybePush(data.originUrl);
  maybePushMany(data.object_url_list);
  maybePushMany(data.objectUrlList);

  if (data.file && typeof data.file === 'object') {
    candidates.push(...collectPossibleUploadUrls(data.file));
  }
  if (data.data && typeof data.data === 'object') {
    candidates.push(...collectPossibleUploadUrls(data.data));
  }
  if (Array.isArray(data.files)) {
    for (const item of data.files) {
      candidates.push(...collectPossibleUploadUrls(item));
    }
  }
  if (Array.isArray(data.list)) {
    for (const item of data.list) {
      candidates.push(...collectPossibleUploadUrls(item));
    }
  }
  return candidates;
}

function extractUploadedFileUrl(res) {
  const urls = collectPossibleUploadUrls(res?.data);
  return urls.find(isPublicHttpsUrl) || null;
}

async function uploadFileToPublicUrl(inputPath, apiKey) {
  const resolvedPath = normalizeLocalFilePath(inputPath);
  if (!resolvedPath) {
    throw new Error(`Invalid local image path: ${inputPath}`);
  }

  const filePath = resolvedPath instanceof URL ? fileURLToPath(resolvedPath) : path.resolve(resolvedPath);
  let stat;
  try {
    stat = await fs.stat(filePath);
  } catch {
    throw new Error(`Local image file not found: ${inputPath}`);
  }
  if (!stat.isFile()) {
    throw new Error(`Local image path is not a file: ${inputPath}`);
  }

  const fileBuffer = await fs.readFile(filePath);
  const fileName = path.basename(filePath);
  const mimeType = inferMimeType(filePath);
  const form = new FormData();
  form.append('batch_no', makeUploadBatchNo());
  form.append('fixed', 'false');
  form.append('file', new Blob([fileBuffer], { type: mimeType }), fileName);

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), 60_000);
  let res;
  try {
    res = await fetch(MODELS_BASE_URL + UPLOAD_API_PATH, {
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
      throw new Error(`Upload timeout: ${filePath}`);
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

  const uploadedUrl = extractUploadedFileUrl(wrapped);
  if (!uploadedUrl) {
    throw new Error('Upload succeeded but no public file URL was returned by the API.');
  }

  return uploadedUrl;
}

async function ensurePublicImageUrl(value, apiKey) {
  if (typeof value !== 'string' || !value.trim()) {
    throw new Error('Image source must be a non-empty string.');
  }
  if (isPublicHttpsUrl(value)) return value;
  if (isRemoteUrl(value)) {
    throw new Error(`Remote image URL must use https: ${value}`);
  }

  log(`Uploading local image to public URL: ${value}`);
  return uploadFileToPublicUrl(value, apiKey);
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

function detectMode(params) {
  if (Array.isArray(params.images) && params.images.length > 0) return 'multi_image';
  if (typeof params.image === 'string' && params.image) return 'image';
  return 'text';
}

function coerceBool(v, defaultVal = false) {
  if (v == null) return defaultVal;
  if (typeof v === 'boolean') return v;
  return String(v).toLowerCase() === 'true';
}

function hasNonEmptyModel(params) {
  const m = params.model;
  return m != null && String(m).trim() !== '';
}

function buildRequestBody(params) {
  const model = String(params.model).trim();
  const body = {
    prompt: params.prompt,
    model,
    duration: Number(params.duration) || 5,
  };
  if (params.aspect_ratio) body.aspect_ratio = params.aspect_ratio;
  if (params.resolution) body.resolution = params.resolution;
  if (params.generate_audio != null) body.generate_audio = coerceBool(params.generate_audio, false);
  if (params.negative_prompt) body.negative_prompt = params.negative_prompt;
  if (params.image) body.image = params.image;
  if (params.images) body.images = params.images.slice(0, 3);
  return body;
}

async function prepareRequestBody(params, apiKey) {
  const body = buildRequestBody(params);
  if (body.image) {
    body.image = await ensurePublicImageUrl(body.image, apiKey);
  }
  if (Array.isArray(body.images) && body.images.length) {
    body.images = await Promise.all(body.images.map((item) => ensurePublicImageUrl(item, apiKey)));
  }
  return body;
}

async function submitTask(params, apiKey) {
  if (!hasNonEmptyModel(params)) {
    return {
      ok: false,
      phase: 'failed',
      errorTitle: 'Missing required parameter',
      errorCode: 'MISSING_PARAM',
      errorCategory: 'validation',
      retryable: false,
      errorMessage: "'model' is required in JSON parameters (no default model).",
    };
  }
  const mode = detectMode(params);
  const pathMap = {
    text: '/v1/generation/text-to-video',
    image: '/v1/generation/image-to-video',
    multi_image: '/v1/generation/multi-image-to-video',
  };
  let body;
  try {
    body = await prepareRequestBody(params, apiKey);
  } catch (err) {
    return {
      ok: false,
      phase: 'failed',
      errorTitle: 'Image preparation failed',
      errorCode: 'IMAGE_PREPARE_FAILED',
      errorCategory: 'validation',
      retryable: false,
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

function extractVideos(taskData) {
  const tr = taskData.task_result || {};
  const raw = tr.videos || taskData.videos || [];
  return raw.map((v) => {
    if (typeof v === 'string') {
      return { url: v, cover_url: '' };
    }
    return {
      url: v?.url || v?.video_url || '',
      cover_url: v?.cover_image_url || v?.cover_url || '',
    };
  });
}

async function pollUntilDone(taskId, batchId, taskIds, apiKey) {
  const start = Date.now();
  while (true) {
    const elapsed = (Date.now() - start) / 1000;
    if (elapsed * 1000 >= POLL_TIMEOUT_MS) {
      return {
        ok: false,
        phase: 'failed',
        errorTitle: 'Request timed out',
        errorCode: 'TIMEOUT',
        errorCategory: 'timeout',
        retryable: true,
        errorMessage: `Poll timeout after ${Math.floor(elapsed)}s.`,
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
      log(`Warning: poll failed (${err.message}), retrying...`);
      continue;
    }

    if (!isApiSuccess(res)) {
      log('Warning: poll returned non-success status, retrying...');
      continue;
    }

    const taskData = res.data || {};
    const rawStatus = taskData.task_status || '';
    const normalized = STATUS_MAP[rawStatus] || 'unknown';
    const elapsedSec = Math.floor((Date.now() - start) / 1000);
    log(`Polling ${taskId}... status: ${rawStatus} (${elapsedSec}s elapsed)`);

    if (normalized === 'completed') {
      const videos = extractVideos(taskData);
      return {
        ok: true,
        phase: 'completed',
        batchId,
        taskIds,
        taskId,
        taskStatus: rawStatus,
        videos: videos.length ? videos : null,
        errorTitle: null,
        errorCode: null,
        errorCategory: null,
        retryable: null,
        errorMessage: null,
      };
    }

    if (normalized === 'failed') {
      const tr = taskData.task_result || {};
      const errMsg = tr.message || taskData.msg || 'Task failed';
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
        errorMessage: errMsg,
      };
    }
  }
}

async function cmdWait(params, apiKey) {
  const submitResult = await submitTask(params, apiKey);
  if (!submitResult.ok) return submitResult;
  const taskId = submitResult.taskId;
  const batchId = submitResult.batchId;
  const taskIds = submitResult.taskIds || [taskId];
  log(`Submitted task ${taskId}. Polling for completion...`);
  return pollUntilDone(taskId, batchId, taskIds, apiKey);
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
  const phase =
    normalized === 'completed' ? 'completed' : normalized === 'failed' ? 'failed' : 'running';
  const tr = taskData.task_result || {};
  return {
    ok: phase !== 'failed',
    phase,
    batchId: null,
    taskIds: [taskId],
    taskId,
    taskStatus: rawStatus,
    videos: videos.length ? videos : null,
    errorTitle: phase === 'failed' ? 'Task failed' : null,
    errorCode: phase === 'failed' ? 'TASK_FAILED' : null,
    errorCategory: phase === 'failed' ? 'task' : null,
    retryable: phase === 'failed' ? false : null,
    errorMessage: phase === 'failed' ? tr.message || taskData.msg || 'The task could not be completed. Please review the request and try again.' : null,
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
        errorTitle: 'Invalid request',
        errorCode: 'VALIDATION',
        errorCategory: 'validation',
        retryable: false,
        errorMessage: `Invalid --mode. Use: ${VALID_MODEL_MODES.join(', ')}`,
      };
    }
    out[modeFilter] = data[modeFilter] || [];
  } else {
    out.text_to_video = data.text_to_video || [];
    out.image_to_video = data.image_to_video || [];
    out.multi_image_to_video = data.multi_image_to_video || [];
  }

  return out;
}

function parseArgs(argv) {
  const cmd = argv[0];
  let jsonStr = null;
  let taskId = null;
  let dryRun = false;
  let modelsMode = null;
  for (let i = 1; i < argv.length; i++) {
    if (argv[i] === '--json') jsonStr = argv[++i];
    else if (argv[i] === '--task-id') taskId = argv[++i];
    else if (argv[i] === '--dry-run') dryRun = true;
    else if (argv[i] === '--mode') modelsMode = argv[++i];
  }
  return { command: cmd, jsonStr, taskId, dryRun, modelsMode };
}

function printJson(obj) {
  process.stdout.write(`${JSON.stringify(obj, null, 2)}\n`);
}

async function main() {
  const argv = process.argv.slice(2);
  const valid = new Set([
    'wait',
    'submit-text',
    'submit-image',
    'submit-multi-image',
    'status',
    'models',
  ]);
  const { command, jsonStr, taskId: cliTaskId, dryRun, modelsMode } = parseArgs(argv);

  if (!command || !valid.has(command)) {
    printJson({
      ok: false,
      phase: 'failed',
      errorCode: 'USAGE',
      errorMessage:
        'Usage: node video_gen.js <wait|submit-text|submit-image|submit-multi-image|status|models> [--json \'...\'] [--task-id id] [--dry-run] [--mode text_to_video|image_to_video|multi_image_to_video]',
    });
    process.exit(1);
  }

  let params = {};
  if (jsonStr) {
    try {
      params = JSON.parse(jsonStr);
    } catch (e) {
      printJson({
        ok: false,
        phase: 'failed',
        errorTitle: 'Invalid JSON',
        errorCode: 'INVALID_JSON',
        errorCategory: 'validation',
        retryable: false,
        errorMessage: `Invalid JSON: ${e.message}`,
      });
      process.exit(1);
    }
  }

  if (command === 'models') {
    const apiKey = (process.env.WERYAI_API_KEY || '').trim();
    if (!apiKey) {
      printJson({
        ok: false,
        phase: 'failed',
        errorTitle: 'Missing API key',
        errorCode: 'NO_API_KEY',
        errorCategory: 'auth',
        retryable: false,
        errorMessage: 'Missing WERYAI_API_KEY environment variable.',
      });
      process.exit(1);
    }
    const result = await cmdModels(modelsMode, apiKey);
    printJson(result);
    process.exit(result.ok ? 0 : 1);
  }

  if (dryRun) {
    const mode = detectMode(params);
    const pathMap = {
      text: '/v1/generation/text-to-video',
      image: '/v1/generation/image-to-video',
      multi_image: '/v1/generation/multi-image-to-video',
    };
    if ('prompt' in params && !hasNonEmptyModel(params)) {
      printJson({
        ok: false,
        phase: 'failed',
        errorTitle: 'Missing required parameter',
        errorCode: 'MISSING_PARAM',
        errorCategory: 'validation',
        retryable: false,
        errorMessage: "'model' is required in JSON parameters (no default model).",
      });
      process.exit(1);
    }
    const body = 'prompt' in params ? buildRequestBody(params) : {};
    const notes = [];
    if (body.image && !isPublicHttpsUrl(body.image)) {
      notes.push('Local `image` paths are uploaded to WeryAI file storage during a real run; `--dry-run` does not upload files.');
    }
    if (Array.isArray(body.images) && body.images.some((item) => !isPublicHttpsUrl(item))) {
      notes.push('Local entries in `images` are uploaded to WeryAI file storage during a real run; `--dry-run` keeps the original paths.');
    }
    printJson({
      ok: true,
      phase: 'dry-run',
      dryRun: true,
      requestBody: body,
      requestUrl: BASE_URL + (pathMap[mode] || pathMap.text),
      notes: notes.length ? notes : undefined,
    });
    process.exit(0);
  }

  const apiKey = (process.env.WERYAI_API_KEY || '').trim();
  if (!apiKey) {
    printJson({
      ok: false,
      phase: 'failed',
      errorTitle: 'Missing API key',
      errorCode: 'NO_API_KEY',
      errorCategory: 'auth',
      retryable: false,
      errorMessage: 'Missing WERYAI_API_KEY environment variable.',
    });
    process.exit(1);
  }

  let result;
  if (command === 'status') {
    const tid = cliTaskId || params.task_id || params.taskId;
    if (!tid) {
      printJson({
        ok: false,
        phase: 'failed',
        errorTitle: 'Missing required parameter',
        errorCode: 'MISSING_PARAM',
        errorCategory: 'validation',
        retryable: false,
        errorMessage: 'status command requires --task-id <id>',
      });
      process.exit(1);
    }
    result = await cmdStatus(tid, apiKey);
  } else {
    if (!params.prompt) {
      printJson({
        ok: false,
        phase: 'failed',
        errorTitle: 'Missing required parameter',
        errorCode: 'MISSING_PARAM',
        errorCategory: 'validation',
        retryable: false,
        errorMessage: "'prompt' is required in JSON parameters.",
      });
      process.exit(1);
    }
    if (!hasNonEmptyModel(params)) {
      printJson({
        ok: false,
        phase: 'failed',
        errorTitle: 'Missing required parameter',
        errorCode: 'MISSING_PARAM',
        errorCategory: 'validation',
        retryable: false,
        errorMessage: "'model' is required in JSON parameters (no default model).",
      });
      process.exit(1);
    }
    result = command === 'wait' ? await cmdWait(params, apiKey) : await submitTask(params, apiKey);
  }

  printJson(result);
  process.exit(result.ok ? 0 : 1);
}

main().catch((err) => {
  printJson({
    ok: false,
    phase: 'failed',
    errorTitle: 'Unexpected failure',
    errorCode: 'FATAL',
    errorCategory: 'server',
    retryable: false,
    errorMessage: err.message || String(err),
  });
  process.exit(1);
});
