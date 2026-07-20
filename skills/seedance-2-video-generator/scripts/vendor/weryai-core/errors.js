const STATIC_ERROR_MAP = {
  '400': {
    category: 'validation',
    title: 'Invalid request',
    message: 'Some of the request details are invalid. Please review your input and try again.',
    retryable: false,
  },
  '401': {
    category: 'auth',
    title: 'Authentication failed',
    message: 'Authentication failed. Please check your API key and try again.',
    retryable: false,
    hint: 'Make sure the API key is valid and sent in the Authorization header.',
  },
  '403': {
    category: 'auth',
    title: 'Authentication failed',
    message: 'Authentication failed. Please check your API key and try again.',
    retryable: false,
    hint: 'Verify the API key, account policy, and any IP restrictions.',
  },
  '404': {
    category: 'not_found',
    title: 'Resource not found',
    message: 'The requested item could not be found. Please check the ID or input and try again.',
    retryable: false,
  },
  '429': {
    category: 'rate_limit',
    title: 'Too many requests',
    message: 'Too many requests in a short time. Please wait a moment and try again.',
    retryable: true,
  },
  '500': {
    category: 'server',
    title: 'Temporary service issue',
    message: 'Something went wrong on our side. Please try again in a moment.',
    retryable: true,
  },
  '1001': {
    category: 'rate_limit',
    title: 'Too many requests',
    message: 'Too many requests in a short time. Please wait a moment and try again.',
    retryable: true,
  },
  '1003': {
    category: 'not_found',
    title: 'Resource not found',
    message: 'The requested item could not be found. Please check the ID or input and try again.',
    retryable: false,
  },
  '1010': {
    category: 'not_found',
    title: 'Resource not found',
    message: 'The requested item could not be found. Please check the ID or input and try again.',
    retryable: false,
  },
  '1011': {
    category: 'credits',
    title: 'Not enough credits',
    message: 'You do not have enough credits to complete this request.',
    retryable: false,
  },
  '1014': {
    category: 'upload',
    title: 'Upload limit reached',
    message: 'You have reached an upload limit. Please wait and try again later.',
    retryable: true,
  },
  '1015': {
    category: 'upload',
    title: 'Upload limit reached',
    message: 'You have reached an upload limit. Please wait and try again later.',
    retryable: true,
  },
  '1102': {
    category: 'upload',
    title: 'Upload failed',
    message: 'We could not upload the file right now. Please try again.',
    retryable: true,
  },
  '2001': {
    category: 'content_safety',
    title: 'Content flagged',
    message: 'The provided image or request content was flagged by the safety system. Please revise it and try again.',
    retryable: false,
  },
  '2003': {
    category: 'content_safety',
    title: 'Content flagged',
    message: 'The provided image or request content was flagged by the safety system. Please revise it and try again.',
    retryable: false,
  },
  '2004': {
    category: 'validation',
    title: 'Unsupported image format',
    message: 'The image format is not supported. Please use JPG, JPEG, PNG, or WEBP.',
    retryable: false,
  },
  '5000': {
    category: 'server',
    title: 'Temporary service issue',
    message: 'Something went wrong on our side. Please try again in a moment.',
    retryable: true,
  },
  '6001': {
    category: 'server',
    title: 'Temporary service issue',
    message: 'Something went wrong on our side. Please try again in a moment.',
    retryable: true,
  },
  '6002': {
    category: 'rate_limit',
    title: 'Too many requests',
    message: 'Too many requests in a short time. Please wait a moment and try again.',
    retryable: true,
  },
  '6003': {
    category: 'server',
    title: 'Temporary service issue',
    message: 'Something went wrong on our side. Please try again in a moment.',
    retryable: true,
  },
  '6004': {
    category: 'server',
    title: 'Generation failed',
    message: 'The request could not be completed. Please try again with different input or try again later.',
    retryable: true,
  },
  '6010': {
    category: 'active_job_limit',
    title: 'Too many active jobs',
    message: 'You already have too many active jobs. Please wait for current jobs to finish before starting a new one.',
    retryable: true,
  },
  '6101': {
    category: 'daily_limit',
    title: 'Daily limit reached',
    message: 'You have reached the daily limit for this workflow. Please try again later.',
    retryable: true,
  },
  '8001': {
    category: 'workflow_state',
    title: 'Podcast script not ready',
    message: 'The podcast script is not ready yet. Please generate the script first, then create the audio.',
    retryable: false,
  },
  '8002': {
    category: 'workflow_state',
    title: 'Audio already submitted',
    message: 'Audio generation has already been submitted for this podcast. Please check the existing task instead of submitting again.',
    retryable: false,
  },
};

const VALIDATION_PATTERNS = [
  { pattern: /\bmodel cannot be empty\b/i, field: 'model', title: 'Missing model', message: 'Please provide a model for this request.' },
  { pattern: /\bmodel is not exist\b|\bmodel not supported\b/i, field: 'model', title: 'Unsupported model', message: 'The selected model is not supported. Please choose a supported model and try again.' },
  { pattern: /\bprompt cannot be empty\b/i, field: 'prompt', title: 'Missing prompt', message: 'Please provide a prompt for this request.' },
  { pattern: /\bnegative prompt\b/i, field: 'negative_prompt', title: 'Invalid negative prompt', message: 'The negative prompt is invalid. Please review it and try again.' },
  { pattern: /\bimage cannot be empty\b/i, field: 'image', title: 'Missing image', message: 'Please provide an image for this request.' },
  { pattern: /\bimages cannot be empty\b/i, field: 'images', title: 'Missing images', message: 'Please provide at least one image for this request.' },
  { pattern: /\bimage url cannot be empty\b/i, field: 'image_url', title: 'Missing image URL', message: 'Please provide a valid image URL.' },
  { pattern: /\bvideo url cannot be empty\b/i, field: 'video_url', title: 'Missing video URL', message: 'Please provide a valid video URL.' },
  { pattern: /\baudio url cannot be empty\b/i, field: 'audio_url', title: 'Missing audio URL', message: 'Please provide a valid audio URL.' },
  { pattern: /\bimage url error\b/i, field: 'image_url', title: 'Invalid image URL', message: 'The provided image URL is not valid. Please check it and try again.' },
  { pattern: /\bvideo url error\b/i, field: 'video_url', title: 'Invalid video URL', message: 'The provided video URL is not valid. Please check it and try again.' },
  { pattern: /\baudio url error\b/i, field: 'audio_url', title: 'Invalid audio URL', message: 'The provided audio URL is not valid. Please check it and try again.' },
  { pattern: /\bonly support jpg|jpeg|png|webp image type\b/i, field: 'image', title: 'Unsupported image format', message: 'The image format is not supported. Please use JPG, JPEG, PNG, or WEBP.' },
  { pattern: /\baspect ratio cannot be empty\b/i, field: 'aspect_ratio', title: 'Missing aspect ratio', message: 'Please provide an aspect ratio for this request.' },
  { pattern: /\baspect ratio .* is not supported\b/i, field: 'aspect_ratio', title: 'Unsupported aspect ratio', message: 'The selected aspect ratio is not supported for this request.' },
  { pattern: /\bresolution cannot be empty\b/i, field: 'resolution', title: 'Missing resolution', message: 'Please provide a resolution for this request.' },
  { pattern: /\bresolution .* is not supported\b/i, field: 'resolution', title: 'Unsupported resolution', message: 'The selected resolution is not supported for this request.' },
  { pattern: /\bduration should not be empty\b|\bduration cannot be empty\b/i, field: 'duration', title: 'Missing duration', message: 'Please provide a duration for this request.' },
  { pattern: /\bduration .* is not supported\b/i, field: 'duration', title: 'Unsupported duration', message: 'The selected duration is not supported for this request.' },
  { pattern: /\bvideo number .* is not supported\b/i, field: 'video_number', title: 'Unsupported video count', message: 'The requested number of videos is not supported for this operation.' },
  { pattern: /\bimage number .* is not supported\b/i, field: 'image_number', title: 'Unsupported image count', message: 'The requested number of images is not supported for this operation.' },
  { pattern: /\bimages exceeds the limit\b/i, field: 'images', title: 'Too many images', message: 'Too many images were provided for this request. Please reduce the number of images and try again.' },
  { pattern: /\bdoes not support multiple images\b/i, field: 'images', title: 'Multiple images not supported', message: 'The selected model does not support multiple images.' },
  { pattern: /\btarget language cannot be empty\b/i, field: 'target_language', title: 'Missing target language', message: 'Please provide a target language for this request.' },
  { pattern: /\blanguage cannot be empty\b/i, field: 'language', title: 'Missing language', message: 'Please provide a language for this request.' },
  { pattern: /\bquery cannot be empty\b/i, field: 'query', title: 'Missing query', message: 'Please provide a query for this request.' },
  { pattern: /\bspeakers cannot be empty\b/i, field: 'speakers', title: 'Missing speakers', message: 'Please provide at least one speaker.' },
  { pattern: /\bmode cannot be empty\b/i, field: 'mode', title: 'Missing mode', message: 'Please provide a mode for this request.' },
  { pattern: /\bmusic type cannot be empty\b/i, field: 'type', title: 'Missing music type', message: 'Please provide a music type for this request.' },
  { pattern: /\btemplate config id cannot be empty\b/i, field: 'template_config_id', title: 'Missing template config', message: 'Please provide a template configuration ID.' },
  { pattern: /\bthis template config is not available for api\b/i, field: 'template_config_id', title: 'Template not available', message: 'The selected template is not available for API use. Please choose another template.' },
  { pattern: /\bconfig ids cannot be empty\b/i, field: 'config_ids', title: 'Missing config IDs', message: 'Please provide at least one config ID.' },
  { pattern: /\bconfig ids cannot exceed 50\b/i, field: 'config_ids', title: 'Too many config IDs', message: 'You can check at most 50 config IDs in one request.' },
  { pattern: /\bprompt and bg_color cannot both be empty\b/i, field: 'prompt|bg_color', title: 'Missing background settings', message: 'Please provide either a background prompt or a background color.' },
  { pattern: /\brectvolist cannot be empty\b|\brect_vo_list cannot be empty\b/i, field: 'rectVOList', title: 'Missing selection area', message: 'Please select at least one area to process and try again.' },
  { pattern: /\bupscale factor .* is not supported\b/i, field: 'upscale_factor', title: 'Unsupported upscale factor', message: 'The selected upscale factor is not supported.' },
  { pattern: /\btype .* is not supported\b/i, field: 'type', title: 'Unsupported type', message: 'The selected type is not supported for this request.' },
  { pattern: /\btask id cannot be empty\b/i, field: 'task_id', title: 'Missing task ID', message: 'Please provide a task ID.' },
  { pattern: /\btask id error\b/i, field: 'task_id', title: 'Invalid task ID', message: 'The task ID is invalid. Please check it and try again.' },
  { pattern: /\btask not exist\b/i, field: 'task_id', title: 'Task not found', message: 'The requested task could not be found. Please check the task ID and try again.' },
  { pattern: /\bbatch id cannot be empty\b/i, field: 'batch_id', title: 'Missing batch ID', message: 'Please provide a batch ID.' },
  { pattern: /\bbatch not exist\b|\bno tasks found\b/i, field: 'batch_id', title: 'Batch not found', message: 'The requested batch could not be found. Please check the batch ID and try again.' },
  { pattern: /\bcallerid not exist\b|\bcaller id not exist\b/i, field: 'caller_id', title: 'Invalid caller ID', message: 'The provided caller ID could not be found. Please check it and try again.' },
  { pattern: /\bfile empty\b/i, field: 'file', title: 'Missing file', message: 'No file was uploaded. Please choose a file and try again.' },
  { pattern: /\bonly image, video and audio files are supported\b/i, field: 'file', title: 'Unsupported file type', message: 'Only image, video, and audio files are supported.' },
  { pattern: /\bfile content does not match the extension or is unsupported\b/i, field: 'file', title: 'Invalid file content', message: 'The uploaded file could not be verified. Please upload a valid supported file.' },
  { pattern: /\bimage file size must be less than 10mb\b/i, field: 'file', title: 'Image too large', message: 'The image is too large. Please upload an image smaller than 10 MB.' },
  { pattern: /\bvideo or audio file size must be less than 50mb\b/i, field: 'file', title: 'File too large', message: 'The file is too large. Please upload a video or audio file smaller than 50 MB.' },
];

export function formatApiError(response) {
  const httpStatus = response.httpStatus;
  const code = response.status != null ? String(response.status) : null;
  const rawMessage = pickRawMessage(response);

  if (httpStatus === 401 || httpStatus === 403) {
    return failure(String(httpStatus), STATIC_ERROR_MAP[String(httpStatus)], { raw: response });
  }
  if (httpStatus === 404) {
    return failure('404', STATIC_ERROR_MAP['404'], { raw: response });
  }
  if (httpStatus === 429) {
    return failure('429', STATIC_ERROR_MAP['429'], { raw: response });
  }
  if (httpStatus >= 500) {
    return failure('500', STATIC_ERROR_MAP['500'], { raw: response });
  }
  if (httpStatus === 400) {
    return failure('400', STATIC_ERROR_MAP['400'], { raw: response });
  }

  if (code === '1002') {
    return classifyValidationError(response);
  }

  const mapped = code ? STATIC_ERROR_MAP[code] : null;
  if (mapped) {
    return failure(code, mapped, { raw: response });
  }

  return failure(code, {
    category: 'server',
    title: 'Request failed',
    message: rawMessage || `We could not complete this request right now. Please try again later.`,
    retryable: true,
  }, { raw: response });
}

export function formatNetworkError(err) {
  if (err.code === 'NO_API_KEY') {
    return failure('NO_API_KEY', {
      category: 'auth',
      title: 'Missing API key',
      message: err.message,
      retryable: false,
      hint: 'Configure WERYAI_API_KEY before retrying.',
    });
  }
  if (err.code === 'TIMEOUT') {
    return failure('TIMEOUT', {
      category: 'timeout',
      title: 'Request timed out',
      message: err.message,
      retryable: true,
      hint: 'Wait a moment and retry. If it keeps happening, reduce request size or check service status.',
    });
  }
  return failure('NETWORK_ERROR', {
    category: 'network',
    title: 'Network error',
    message: `We could not reach the API right now. Please check the network and try again.`,
    retryable: true,
    hint: err?.message || String(err),
  });
}

export function isApiSuccess(response) {
  const ok = response.httpStatus >= 200 && response.httpStatus < 300;
  const bodyOk = response.status === 0 || response.status === 200;
  return ok && bodyOk;
}

export function describeApiError(response, options = {}) {
  const { includeTitle = true } = options;
  const view = formatApiError(response);
  if (!includeTitle || !view.errorTitle) return view.errorMessage;
  if (!view.errorMessage || view.errorMessage === view.errorTitle) return view.errorTitle;
  return `${view.errorTitle}: ${view.errorMessage}`;
}

function classifyValidationError(response) {
  const rawMessage = pickRawMessage(response);

  for (const rule of VALIDATION_PATTERNS) {
    if (rule.pattern.test(rawMessage)) {
      return failure('1002', {
        category: 'validation',
        title: rule.title,
        message: rule.message,
        retryable: false,
        field: rule.field,
      }, { raw: response });
    }
  }

  if (/missing|cannot be empty|required/i.test(rawMessage)) {
    return failure('1002', {
      category: 'validation',
      title: 'Missing required input',
      message: 'Some required information is missing. Please review your input and try again.',
      retryable: false,
    }, { raw: response });
  }

  if (/invalid|unsupported|error/i.test(rawMessage)) {
    return failure('1002', {
      category: 'validation',
      title: 'Invalid request parameters',
      message: 'One or more request settings are invalid or not supported. Please review your input and try again.',
      retryable: false,
    }, { raw: response });
  }

  return failure('1002', {
    category: 'validation',
    title: 'Invalid request',
    message: 'Some of the request details are missing or not supported. Please review your input and try again.',
    retryable: false,
  }, { raw: response });
}

function pickRawMessage(response) {
  return String(response?.msg || response?.message || response?.desc || '').trim();
}

function failure(errorCode, view, extra = {}) {
  return {
    ok: false,
    phase: 'failed',
    errorCode: errorCode != null ? String(errorCode) : null,
    errorCategory: view.category,
    errorTitle: view.title,
    errorMessage: view.message,
    retryable: view.retryable,
    field: view.field ?? null,
    hint: view.hint ?? null,
    raw: extra.raw ?? null,
  };
}
