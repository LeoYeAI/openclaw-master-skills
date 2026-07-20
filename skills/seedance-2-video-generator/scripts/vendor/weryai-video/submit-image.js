import { createClient, log } from '../weryai-core/client.js';
import { formatApiError, formatNetworkError, isApiSuccess } from '../weryai-core/errors.js';
import { buildBody, fetchModelRegistry, lookupModel, validateWithModel } from './model-registry.js';
import { DEFAULT_MODEL, FALLBACK_DEFAULTS } from './models.js';
import { normalizeVideoInput } from './normalize-input.js';
import { collectLocalUploadPreview, resolveUploadSources } from './upload.js';
import { resolveDefaultGenerateAudio } from './audio-default.js';
import { validateLocalSourcesForMode, validateSubmitImage } from './validators.js';

export async function execute(input, ctx) {
  const normalizedInput = normalizeVideoInput(input);
  const structErrors = validateSubmitImage(normalizedInput);
  const localErrors = await validateLocalSourcesForMode(normalizedInput, 'image');
  const allErrors = [...structErrors, ...localErrors];
  if (allErrors.length > 0) {
    return { ok: false, phase: 'failed', errorCode: 'VALIDATION', errorMessage: allErrors.join(' ') };
  }

  const registry = await fetchModelRegistry(ctx);
  const model = normalizedInput.model || DEFAULT_MODEL;
  const meta = lookupModel(registry, model, 'image_to_video');

  if (meta) {
    const { errors, warnings } = validateWithModel(meta, normalizedInput, 'image_to_video');
    warnings.forEach((warning) => log(`Warning: ${warning}`));
    if (errors.length > 0) {
      return { ok: false, phase: 'failed', errorCode: 'VALIDATION', errorMessage: errors.join(' ') };
    }
  } else if (registry) {
    log(`Warning: model "${model}" not found in image_to_video registry. Proceeding anyway.`);
  }

  const body = meta ? buildBody(meta, normalizedInput, 'image_to_video') : buildFallbackBody(normalizedInput, model);

  const uploadPreview = collectLocalUploadPreview(body, 'image_to_video');

  if (ctx.dryRun) {
    return {
      ok: true,
      phase: 'dry-run',
      dryRun: true,
      requestBody: body,
      requestUrl: `${ctx.baseUrl}/v1/generation/image-to-video`,
      uploadPreview,
      notes: 'dry-run does not upload local files. Local sources in uploadPreview will be uploaded in a real run via /v1/generation/upload-file.',
    };
  }

  let resolvedBody;
  try {
    resolvedBody = await resolveUploadSources(ctx, body, 'image_to_video');
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
    res = await client.post('/v1/generation/image-to-video', resolvedBody);
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
    requestSummary: buildRequestSummary(resolvedBody),
    errorCode: null,
    errorMessage: null,
  };
}

function buildRequestSummary(body) {
  return {
    model: body?.model ?? null,
    duration: body?.duration ?? null,
    aspectRatio: body?.aspect_ratio ?? null,
    resolution: body?.resolution ?? null,
    generateAudio: body?.generate_audio ?? null,
  };
}

function buildFallbackBody(input, model) {
  const body = {
    prompt: input.prompt,
    model,
    image: input.image,
    duration: Number(input.duration ?? input.dur) || FALLBACK_DEFAULTS.duration,
  };
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
