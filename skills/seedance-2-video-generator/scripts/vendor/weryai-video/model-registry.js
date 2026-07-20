import { createClient, log } from '../weryai-core/client.js';
import { FALLBACK_DEFAULTS, MODELS_API_PATH } from './models.js';
import { coerceBool } from './utils.js';
import { resolveDefaultGenerateAudio } from './audio-default.js';
import { normalizeModelEntry } from '../weryai-core/model-display.js';

export async function fetchModelRegistry(ctx) {
  try {
    const client = createClient({ ...ctx, baseUrl: ctx.modelsBaseUrl });
    const res = await client.get(MODELS_API_PATH, { retries: 1 });

    if (res.httpStatus < 200 || res.httpStatus >= 300 || !res.data) {
      log('Warning: models API returned non-success. Using permissive mode.');
      return null;
    }

    const data = res.data;
    return {
      text_to_video: indexByKey(data.text_to_video),
      image_to_video: indexByKey(data.image_to_video),
      multi_image_to_video: indexByKey(data.multi_image_to_video ?? data.image_to_video),
    };
  } catch (err) {
    log(`Warning: could not fetch model registry (${err.message}). Using permissive mode.`);
    return null;
  }
}

function indexByKey(arr) {
  const map = new Map();
  if (!Array.isArray(arr)) return map;
  for (const item of arr) {
    const normalized = normalizeModelEntry(item);
    if (normalized?.model_key) map.set(normalized.model_key, normalized);
  }
  return map;
}

export function lookupModel(registry, modelKey, mode) {
  if (!registry) return null;
  const modeMap = registry[mode];
  if (!modeMap) return null;
  return modeMap.get(modelKey) ?? null;
}

export function resolveSubmissionPlan(registry, modelKey, input, requestedMode) {
  if (requestedMode !== 'multi_image_to_video') {
    return {
      mode: requestedMode,
      input,
      meta: lookupModel(registry, modelKey, requestedMode),
      warnings: [],
    };
  }

  const multiMeta = lookupModel(registry, modelKey, 'multi_image_to_video');
  const imageMeta = lookupModel(registry, modelKey, 'image_to_video');
  const capabilityMeta = multiMeta ?? imageMeta;

  if (!multiMeta && imageMeta) {
    return downgradeToSingleImage(modelKey, input, imageMeta, 'Model is not listed in the multi-image registry.');
  }

  const downgradeReason = getSingleImageDowngradeReason(capabilityMeta, input);
  if (downgradeReason) {
    const firstImage = Array.isArray(input.images) ? input.images[0] : null;
    return downgradeToSingleImage(modelKey, input, imageMeta ?? capabilityMeta, downgradeReason, firstImage);
  }

  return {
    mode: 'multi_image_to_video',
    input,
    meta: multiMeta ?? capabilityMeta,
    warnings: [],
  };
}

export function validateWithModel(meta, input, mode) {
  const errors = [];
  const warnings = [];

  if (input.prompt && meta.prompt_length_limit && input.prompt.length > meta.prompt_length_limit) {
    errors.push(`prompt exceeds model limit (${input.prompt.length}/${meta.prompt_length_limit} chars).`);
  }

  const aspectRatio = input.aspect_ratio || input.aspectRatio;
  const allowedAspects = meta.aspect_ratios;
  if (aspectRatio) {
    if (!Array.isArray(allowedAspects) || allowedAspects.length === 0) {
      warnings.push(`Model "${meta.model_key}" does not list supported aspect_ratios. The parameter will be omitted.`);
    } else if (!allowedAspects.includes(aspectRatio)) {
      errors.push(
        `Model "${meta.model_key}" does not support aspect_ratio "${aspectRatio}". Allowed: [${allowedAspects.join(', ')}].`,
      );
    }
  }

  const duration = input.duration ?? input.dur;
  const allowedDurations = meta.durations;
  if (duration != null && Array.isArray(allowedDurations) && allowedDurations.length > 0) {
    const value = Number(duration);
    if (Number.isNaN(value)) {
      errors.push(`duration must be a number, got "${duration}".`);
    } else if (!allowedDurations.includes(value)) {
      errors.push(`Model "${meta.model_key}" does not support duration=${value}s. Allowed: [${allowedDurations.join(', ')}].`);
    }
  }

  const resolution = input.resolution;
  const allowedResolutions = meta.resolutions;
  if (resolution) {
    if (!Array.isArray(allowedResolutions) || allowedResolutions.length === 0) {
      warnings.push(`Model "${meta.model_key}" does not list supported resolutions. The parameter will be omitted.`);
    } else if (!allowedResolutions.includes(resolution)) {
      errors.push(
        `Model "${meta.model_key}" does not support resolution "${resolution}". Allowed: [${allowedResolutions.join(', ')}].`,
      );
    }
  }

  const negativePrompt = input.negative_prompt || input.negativePrompt;
  if (negativePrompt && meta.has_negative_prompt === false) {
    warnings.push(`Model "${meta.model_key}" does not support negative_prompt. It will be ignored.`);
  }

  const generateAudio = input.generate_audio ?? input.generateAudio;
  if (generateAudio != null && coerceBool(generateAudio, false) === true && meta.has_generate_audio === false) {
    warnings.push(`Model "${meta.model_key}" does not support generate_audio. It will be ignored.`);
  }

  if (mode === 'image_to_video') {
    const limit = meta.upload_image_limit;
    if (input.image && limit != null && limit < 1) {
      warnings.push(`Model "${meta.model_key}" may not support image input.`);
    }
  }

  if (mode === 'multi_image_to_video') {
    const images = input.images;
    const limit = meta.upload_image_limit;
    if (Array.isArray(images) && limit != null && images.length > limit) {
      warnings.push(`Model "${meta.model_key}" allows max ${limit} reference image(s). Extra images will be trimmed.`);
    }
  }

  return { errors, warnings };
}

export function buildBody(meta, input, mode) {
  const body = {
    prompt: input.prompt,
    model: meta.model_key,
  };

  const resolvedAspect = resolveFromAllowed(
    input.aspect_ratio || input.aspectRatio,
    meta.aspect_ratios,
    FALLBACK_DEFAULTS.aspect_ratio,
  );
  if (resolvedAspect != null) body.aspect_ratio = resolvedAspect;

  const resolvedDuration = resolveNumeric(input.duration ?? input.dur, meta.durations, meta.durations?.[0] ?? 5);
  if (resolvedDuration != null) body.duration = resolvedDuration;

  const resolvedResolution = resolveFromAllowed(input.resolution, meta.resolutions, '720p');
  if (resolvedResolution != null) body.resolution = resolvedResolution;

  if (meta.has_generate_audio === true) {
    body.generate_audio = resolveDefaultGenerateAudio(input, meta.model_key);
  }

  if ((input.negative_prompt || input.negativePrompt) && meta.has_negative_prompt === true) {
    body.negative_prompt = input.negative_prompt || input.negativePrompt;
  }

  if (mode === 'image_to_video' && input.image) {
    body.image = input.image;
  }
  if (mode === 'multi_image_to_video' && Array.isArray(input.images)) {
    const limit = meta.upload_image_limit ?? 3;
    body.images = input.images.slice(0, limit);
  }

  return body;
}

function resolveFromAllowed(userValue, allowed, preferred) {
  if (!Array.isArray(allowed) || allowed.length === 0) return null;
  if (userValue && allowed.includes(userValue)) return userValue;
  if (userValue && !allowed.includes(userValue)) {
    log(`Warning: "${userValue}" not in allowed list [${allowed.join(', ')}]. Using default.`);
    return allowed.includes(preferred) ? preferred : allowed[0];
  }
  return allowed.includes(preferred) ? preferred : allowed[0];
}

function resolveNumeric(userValue, allowed, fallback) {
  if (!Array.isArray(allowed) || allowed.length === 0) return fallback;
  if (userValue != null) {
    const value = Number(userValue);
    if (allowed.includes(value)) return value;
    log(`Warning: "${userValue}" not in allowed list [${allowed.join(', ')}]. Using default.`);
  }
  return allowed[0];
}

function getSingleImageDowngradeReason(meta, input) {
  if (!meta || !Array.isArray(input.images) || input.images.length === 0) {
    return null;
  }

  if (meta.support_multiple_images === false) {
    return 'Model explicitly reports support_multiple_images=false.';
  }

  if (typeof meta.upload_image_limit === 'number' && meta.upload_image_limit < 2) {
    return `Model upload_image_limit is ${meta.upload_image_limit}.`;
  }

  return null;
}

function downgradeToSingleImage(modelKey, input, meta, reason, firstImage = Array.isArray(input.images) ? input.images[0] : null) {
  return {
    mode: 'image_to_video',
    input: {
      ...input,
      image: firstImage,
    },
    meta,
    warnings: [
      `Model "${modelKey}" cannot use multi-image routing here (${reason}). Using the first image and routing to image-to-video.`,
    ],
  };
}
