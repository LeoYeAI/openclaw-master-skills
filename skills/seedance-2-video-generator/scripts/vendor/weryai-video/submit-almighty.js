import { createClient } from '../weryai-core/client.js';
import { formatApiError, formatNetworkError, isApiSuccess } from '../weryai-core/errors.js';
import { DEFAULT_MODEL } from './models.js';
import { normalizeVideoInput } from './normalize-input.js';
import { collectLocalUploadPreview, resolveUploadSources } from './upload.js';
import { resolveDefaultGenerateAudio } from './audio-default.js';
import { validateLocalSourcesForMode, validateSubmitAlmighty } from './validators.js';

export async function execute(input, ctx) {
  const normalizedInput = normalizeVideoInput(input);
  const structErrors = validateSubmitAlmighty(normalizedInput);
  const localErrors = await validateLocalSourcesForMode(normalizedInput, 'almighty');
  const allErrors = [...structErrors, ...localErrors];

  if (allErrors.length > 0) {
    return { ok: false, phase: 'failed', errorCode: 'VALIDATION', errorMessage: allErrors.join(' ') };
  }

  const body = buildAlmightyBody(normalizedInput);
  const uploadPreview = collectLocalUploadPreview(body, 'almighty_reference_to_video');
  const apiPath = '/v1/generation/almighty-reference-to-video';

  if (ctx.dryRun) {
    return {
      ok: true,
      phase: 'dry-run',
      dryRun: true,
      requestMode: 'almighty_reference_to_video',
      requestBody: body,
      requestUrl: `${ctx.baseUrl}${apiPath}`,
      uploadPreview,
      notes: 'dry-run does not upload local files. Local sources in uploadPreview will be uploaded in a real run via /v1/generation/upload-file.',
    };
  }

  let resolvedBody;
  try {
    resolvedBody = await resolveUploadSources(ctx, body, 'almighty_reference_to_video');
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
    balance: null,
    requestSummary: buildRequestSummary(resolvedBody),
    errorCode: null,
    errorMessage: null,
  };
}

function buildRequestSummary(body) {
  return {
    mode: 'almighty_reference_to_video',
    model: body?.model ?? null,
    duration: body?.duration ?? null,
    aspectRatio: body?.aspect_ratio ?? null,
    resolution: body?.resolution ?? null,
    generateAudio: body?.generate_audio ?? null,
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

export default execute;
