import { validateLocalSource } from './upload.js';

export function validateSubmitText(input) {
  const errors = [];

  if (!input.prompt || typeof input.prompt !== 'string' || input.prompt.trim().length === 0) {
    errors.push('prompt is required and must be a non-empty string.');
  }

  const duration = input.duration ?? input.dur;
  if (duration == null) {
    errors.push('duration is required (integer, seconds).');
  } else {
    const value = Number(duration);
    if (!Number.isInteger(value) || value < 1) {
      errors.push('duration must be a positive integer (seconds).');
    }
  }

  return errors;
}

export function validateSubmitImage(input) {
  const errors = validateSubmitText(input);

  if (!input.image || typeof input.image !== 'string') {
    errors.push('image is required and must be a source string.');
  }

  return errors;
}

export function validateSubmitMultiImage(input) {
  const errors = validateSubmitText(input);

  if (!input.images || !Array.isArray(input.images) || input.images.length === 0) {
    errors.push('images is required and must be a non-empty array of source strings.');
  } else {
    for (const url of input.images) {
      if (typeof url !== 'string') {
        errors.push(`Invalid image source: "${url}".`);
      }
    }
  }

  return errors;
}

export async function validateLocalSourcesForMode(input, mode) {
  const errors = [];
  if (mode === 'image') {
    await validateLocalSource(input.image, 'image', 'image', errors);
    return errors;
  }

  if (mode === 'multi_image') {
    const images = Array.isArray(input.images) ? input.images : [];
    await Promise.all(images.map((value, index) => validateLocalSource(value, 'image', `images[${index}]`, errors)));
    return errors;
  }

  if (mode === 'almighty') {
    const images = Array.isArray(input.images) ? input.images : [];
    const videos = Array.isArray(input.videos) ? input.videos : [];
    const audios = Array.isArray(input.audios) ? input.audios : [];
    await Promise.all([
      ...images.map((value, index) => validateLocalSource(value, 'image', `images[${index}]`, errors)),
      ...videos.map((value, index) => validateLocalSource(value, 'video', `videos[${index}]`, errors)),
      ...audios.map((value, index) => validateLocalSource(value, 'audio', `audios[${index}]`, errors)),
    ]);
  }
  return errors;
}

export function validateSubmitAlmighty(input) {
  const errors = validateSubmitText(input);

  if (typeof input.prompt === 'string' && input.prompt.length > 500) {
    errors.push(`almighty prompt exceeds 500 characters (${input.prompt.length}/500).`);
  }

  const duration = Number(input.duration ?? input.dur);
  if (Number.isInteger(duration) && (duration < 5 || duration > 15)) {
    errors.push('almighty duration must be between 5 and 15 seconds.');
  }

  const images = Array.isArray(input.images) ? input.images : [];
  const videos = Array.isArray(input.videos) ? input.videos : [];
  const audios = Array.isArray(input.audios) ? input.audios : [];

  if (images.length > 9) errors.push('almighty images must be <= 9.');
  if (videos.length > 3) errors.push('almighty videos must be <= 3.');
  if (audios.length > 3) errors.push('almighty audios must be <= 3.');
  if (images.length + videos.length + audios.length > 12) {
    errors.push('almighty mixed input total must be <= 12 files.');
  }
  if (images.length === 0 && videos.length === 0) {
    errors.push('almighty requires at least one of `images` or `videos`.');
  }

  if (input.video_number != null) {
    const n = Number(input.video_number);
    if (!Number.isInteger(n) || n < 1 || n > 4) {
      errors.push('video_number must be an integer between 1 and 4.');
    }
  }

  for (const [idx, value] of images.entries()) {
    if (typeof value !== 'string') errors.push(`Invalid image source at images[${idx}].`);
  }
  for (const [idx, value] of videos.entries()) {
    if (typeof value !== 'string') errors.push(`Invalid video source at videos[${idx}].`);
  }
  for (const [idx, value] of audios.entries()) {
    if (typeof value !== 'string') errors.push(`Invalid audio source at audios[${idx}].`);
  }

  return errors;
}
