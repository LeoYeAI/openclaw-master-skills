import { createClient, log } from '../weryai-core/client.js';
import { formatApiError, formatNetworkError, isApiSuccess } from '../weryai-core/errors.js';
import { buildBody, fetchModelRegistry, resolveSubmissionPlan, validateWithModel } from './model-registry.js';
import { DEFAULT_MODEL, FALLBACK_DEFAULTS } from './models.js';
import { normalizeVideoInput } from './normalize-input.js';
import { collectLocalUploadPreview, resolveUploadSources } from './upload.js';
import { resolveDefaultGenerateAudio } from './audio-default.js';
import { validateLocalSourcesForMode, validateSubmitMultiImage } from './validators.js';

export async function execute(input, ctx) {
  const normalizedInput = normalizeVideoInput(input);
  const structErrors = validateSubmitMultiImage(normalizedInput);
  const localErrors = await validateLocalSourcesForMode(normalizedInput, 'multi_image');
  const allErrors = [...structErrors, ...localErrors];
  if (allErrors.length > 0) {
    return { ok: false, phase: 'failed', errorCode: 'VALIDATION', errorMessage: allErrors.join(' ') };
  }

  const registry = await fetchModelRegistry(ctx);
  const model = normalizedInput.model || DEFAULT_MODEL;
  const plan = resolveSubmissionPlan(registry, model, normalizedInput, 'multi_image_to_video');
  const effectiveInput = plan.input;
  const effectiveMode = plan.mode;
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

  const body = meta ? buildBody(meta, effectiveInput, effectiveMode) : buildFallbackBody(effectiveInput, model, effectiveMode);
  const apiPath = effectiveMode === 'image_to_video'
    ? '/v1/generation/image-to-video'
    : '/v1/generation/multi-image-to-video';

  const uploadPreview = collectLocalUploadPreview(body, effectiveMode);

  if (ctx.dryRun) {
    return {
      ok: true,
      phase: 'dry-run',
      dryRun: true,
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
  let res;
  try {
    res = await client.post(apiPath, resolvedBody);
  } catch (err) {
    return formatNetworkError(err);
  }

  if (!isApiSuccess(res)) {
    return formatApiError(res);
  }

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
    balance: null,
    requestSummary: buildRequestSummary(resolvedBody, effectiveMode),
    errorCode: null,
    errorMessage: null,
  };
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

function buildFallbackBody(input, model, effectiveMode) {
  const body = {
    prompt: input.prompt,
    model,
    duration: Number(input.duration ?? input.dur) || FALLBACK_DEFAULTS.duration,
  };
  if (effectiveMode === 'image_to_video') {
    body.image = input.image;
  } else {
    body.images = input.images.slice(0, 3);
  }
  const aspectRatio = input.aspect_ratio || input.aspectRatio;
  if (aspectRatio) body.aspect_ratio = aspectRatio;
  if (input.resolution) body.resolution = input.resolution;
  body.generate_audio = resolveDefaultGenerateAudio(input, model);
  if (input.negative_prompt || input.negativePrompt) {
    body.negative_prompt = input.negative_prompt || input.negativePrompt;
  }
  return body;
}

export default execute;
