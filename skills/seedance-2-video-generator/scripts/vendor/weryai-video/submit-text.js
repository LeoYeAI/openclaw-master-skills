import { createClient, log } from '../weryai-core/client.js';
import { formatApiError, formatNetworkError, isApiSuccess } from '../weryai-core/errors.js';
import { buildBody, fetchModelRegistry, lookupModel, validateWithModel } from './model-registry.js';
import { DEFAULT_MODEL, FALLBACK_DEFAULTS } from './models.js';
import { normalizeVideoInput } from './normalize-input.js';
import { resolveDefaultGenerateAudio } from './audio-default.js';
import { validateSubmitText } from './validators.js';

export async function execute(input, ctx) {
  const normalizedInput = normalizeVideoInput(input);
  const structErrors = validateSubmitText(normalizedInput);
  if (structErrors.length > 0) {
    return { ok: false, phase: 'failed', errorCode: 'VALIDATION', errorMessage: structErrors.join(' ') };
  }

  const registry = await fetchModelRegistry(ctx);
  const model = normalizedInput.model || DEFAULT_MODEL;
  const meta = lookupModel(registry, model, 'text_to_video');

  if (meta) {
    const { errors, warnings } = validateWithModel(meta, normalizedInput, 'text_to_video');
    warnings.forEach((warning) => log(`Warning: ${warning}`));
    if (errors.length > 0) {
      return { ok: false, phase: 'failed', errorCode: 'VALIDATION', errorMessage: errors.join(' ') };
    }
  } else if (registry) {
    log(`Warning: model "${model}" not found in text_to_video registry. Proceeding anyway.`);
  }

  const body = meta ? buildBody(meta, normalizedInput, 'text_to_video') : buildFallbackBody(normalizedInput, model);

  if (ctx.dryRun) {
    return {
      ok: true,
      phase: 'dry-run',
      dryRun: true,
      requestBody: body,
      requestUrl: `${ctx.baseUrl}/v1/generation/text-to-video`,
    };
  }

  const client = createClient(ctx);
  let res;
  try {
    res = await client.post('/v1/generation/text-to-video', body);
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
    requestSummary: buildRequestSummary(body),
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
