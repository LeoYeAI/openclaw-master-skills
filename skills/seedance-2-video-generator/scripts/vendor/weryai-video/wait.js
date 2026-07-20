import { createClient, log } from '../weryai-core/client.js';
import { formatApiError, formatNetworkError, isApiSuccess } from '../weryai-core/errors.js';
import { buildBody, fetchModelRegistry, resolveSubmissionPlan, validateWithModel } from './model-registry.js';
import { DEFAULT_MODEL, FALLBACK_DEFAULTS } from './models.js';
import { detectVideoMode, normalizeVideoInput } from './normalize-input.js';
import { resolveDefaultGenerateAudio } from './audio-default.js';
import { collectLocalUploadPreview, resolveUploadSources } from './upload.js';
import {
  validateLocalSourcesForMode,
  validateSubmitAlmighty,
  validateSubmitImage,
  validateSubmitMultiImage,
  validateSubmitText,
} from './validators.js';
import { pollSubmittedTasks } from '../weryai-core/wait.js';

export async function execute(input, ctx) {
  const normalizedInput = normalizeVideoInput(input);
  const requestedTaskClass = normalizeTaskClass(input?.taskClass ?? input?.task_class ?? 'auto');
  if (!requestedTaskClass) {
    return {
      ok: false,
      phase: 'failed',
      errorCode: 'VALIDATION',
      errorMessage: 'task_class must be one of: auto, short, long.',
    };
  }
  const requestedMode = detectVideoMode(normalizedInput);

  const structErrors =
    requestedMode === 'almighty'
      ? validateSubmitAlmighty(normalizedInput)
      : requestedMode === 'multi_image'
        ? validateSubmitMultiImage(normalizedInput)
        : requestedMode === 'image'
          ? validateSubmitImage(normalizedInput)
          : validateSubmitText(normalizedInput);

  const localErrors = await validateLocalSourcesForMode(normalizedInput, requestedMode);
  const allStructErrors = [...structErrors, ...localErrors];

  if (allStructErrors.length > 0) {
    return { ok: false, phase: 'failed', errorCode: 'VALIDATION', errorMessage: allStructErrors.join(' ') };
  }

  let effectiveInput;
  let effectiveMode;
  let body;

  if (requestedMode === 'almighty') {
    effectiveInput = normalizedInput;
    effectiveMode = 'almighty_reference_to_video';
    body = buildAlmightyBody(effectiveInput);
  } else {
    const requestedRegistryMode = requestedMode === 'multi_image'
      ? 'multi_image_to_video'
      : requestedMode === 'image'
        ? 'image_to_video'
        : 'text_to_video';

    const registry = await fetchModelRegistry(ctx);
    const model = normalizedInput.model || DEFAULT_MODEL;
    const plan = resolveSubmissionPlan(registry, model, normalizedInput, requestedRegistryMode);
    effectiveInput = plan.input;
    effectiveMode = plan.mode;
    const meta = plan.meta;

    plan.warnings.forEach((warning) => log(`Warning: ${warning}`));
    if (meta) {
      const { errors, warnings } = validateWithModel(meta, effectiveInput, effectiveMode);
      warnings.forEach((warning) => log(`Warning: ${warning}`));
      if (errors.length > 0) {
        return { ok: false, phase: 'failed', errorCode: 'VALIDATION', errorMessage: errors.join(' ') };
      }
    } else if (registry) {
      log(`Warning: model "${model}" not found in ${effectiveMode} registry. Proceeding anyway.`);
    }

    body = meta ? buildBody(meta, effectiveInput, effectiveMode) : buildFallbackBody(effectiveInput, model, effectiveMode);
  }

  const uploadPreview = collectLocalUploadPreview(body, effectiveMode);
  const apiPath = toApiPath(effectiveMode);
  const taskClass = requestedTaskClass === 'auto'
    ? resolveTaskClassFromMode(effectiveMode)
    : requestedTaskClass;
  const pollTimeoutMs = resolveVideoPollTimeoutMs(ctx, taskClass);

  if (ctx.dryRun) {
    return {
      ok: true,
      phase: 'dry-run',
      dryRun: true,
      requestMode: effectiveMode,
      taskClass,
      pollTimeoutMs,
      requestBody: body,
      requestUrl: `${ctx.baseUrl}${apiPath}`,
      uploadPreview,
      notes: 'dry-run does not upload local files. Local sources in uploadPreview will be uploaded in a real run via /v1/generation/upload-file.',
    };
  }

  let resolvedBody;
  try {
    resolvedBody = await resolveUploadSources(ctx, body, effectiveMode);
  } catch (err) {
    return {
      ok: false,
      phase: 'failed',
      errorCode: 'UPLOAD_FAILED',
      errorMessage: err?.message ?? String(err),
    };
  }

  const client = createClient(ctx);
  let submitRes;
  try {
    submitRes = await client.post(apiPath, resolvedBody);
  } catch (err) {
    return formatNetworkError(err);
  }

  if (!isApiSuccess(submitRes)) {
    return formatApiError(submitRes);
  }

  const data = submitRes.data || {};
  const batchId = data.batch_id ?? null;
  const taskIds = data.task_ids ?? (data.task_id ? [data.task_id] : []);

  if (taskIds.length === 0) {
    return { ok: false, phase: 'failed', errorCode: 'PROTOCOL', errorMessage: 'API returned success but no task_ids.' };
  }

  const pollCtx = { ...ctx, pollTimeoutMs };

  const result = await pollSubmittedTasks(client, {
    batchId,
    taskIds,
    ctx: pollCtx,
    pollProfile: effectiveMode === 'text_to_video' ? 'fast' : 'slow',
    outputKey: 'videos',
    outputLabel: 'video',
    allowBatch: true,
  });

  return {
    ...result,
    taskClass,
    pollTimeoutMs,
    requestSummary: buildRequestSummary(resolvedBody, effectiveMode),
  };
}

function buildAlmightyBody(input) {
  const body = {
    prompt: input.prompt,
    model: input.model || DEFAULT_MODEL,
    duration: Number(input.duration ?? input.dur) || 5,
  };

  if (input.aspect_ratio || input.aspectRatio) body.aspect_ratio = input.aspect_ratio || input.aspectRatio;
  if (input.resolution) body.resolution = input.resolution;

  if (Array.isArray(input.images) && input.images.length > 0) body.images = input.images.slice(0, 9);
  if (Array.isArray(input.videos) && input.videos.length > 0) body.videos = input.videos.slice(0, 3);
  if (Array.isArray(input.audios) && input.audios.length > 0) body.audios = input.audios.slice(0, 3);

  body.generate_audio = resolveDefaultGenerateAudio(input, body.model) ? 'true' : 'false';

  if (input.video_number != null) body.video_number = Number(input.video_number);
  if (input.webhook_url || input.webhookUrl) body.webhook_url = input.webhook_url || input.webhookUrl;
  if (input.caller_id || input.callerId) body.caller_id = Number(input.caller_id || input.callerId);

  return body;
}

function toApiPath(mode) {
  if (mode === 'multi_image_to_video') return '/v1/generation/multi-image-to-video';
  if (mode === 'image_to_video') return '/v1/generation/image-to-video';
  if (mode === 'almighty_reference_to_video') return '/v1/generation/almighty-reference-to-video';
  return '/v1/generation/text-to-video';
}

function buildFallbackBody(input, model, effectiveMode) {
  const body = {
    prompt: input.prompt,
    model,
    duration: Number(input.duration ?? input.dur) || FALLBACK_DEFAULTS.duration,
  };
  const aspectRatio = input.aspect_ratio || input.aspectRatio;
  if (aspectRatio) body.aspect_ratio = aspectRatio;
  if (input.resolution) body.resolution = input.resolution;
  body.generate_audio = resolveDefaultGenerateAudio(input, model);
  if (effectiveMode === 'image_to_video') body.image = input.image;
  if (effectiveMode === 'multi_image_to_video') body.images = input.images.slice(0, 3);
  if (input.negative_prompt || input.negativePrompt) {
    body.negative_prompt = input.negative_prompt || input.negativePrompt;
  }
  return body;
}

function buildRequestSummary(body, mode) {
  return {
    mode,
    model: body?.model ?? null,
    duration: body?.duration ?? null,
    aspectRatio: body?.aspect_ratio ?? null,
    resolution: body?.resolution ?? null,
    generateAudio: body?.generate_audio ?? null,
  };
}

export function normalizeTaskClass(raw) {
  const value = String(raw ?? 'auto').trim().toLowerCase();
  if (value === 'auto' || value === 'short' || value === 'long') return value;
  return null;
}

export function resolveTaskClassFromMode(mode) {
  return mode === 'text_to_video' ? 'short' : 'long';
}

export function resolveVideoPollTimeoutMs(ctx, taskClass) {
  if (ctx?.pollTimeoutOverrideMs != null) {
    const override = Number(ctx.pollTimeoutOverrideMs);
    if (Number.isFinite(override) && override >= 0) {
      return override;
    }
  }

  const shortTimeout = Number(ctx?.shortTaskTimeoutMs);
  const longTimeout = Number(ctx?.longTaskTimeoutMs);

  if (taskClass === 'short') {
    if (Number.isFinite(shortTimeout) && shortTimeout >= 0) return shortTimeout;
    return 600_000;
  }
  if (Number.isFinite(longTimeout) && longTimeout >= 0) return longTimeout;
  return 1_800_000;
}

export default execute;
