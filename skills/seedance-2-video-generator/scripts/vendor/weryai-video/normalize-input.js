import { FALLBACK_DEFAULTS } from './models.js';
import { normalizeSourceArray } from './upload.js';

export function normalizeVideoInput(rawInput) {
  const input = { ...rawInput };
  const firstFrame =
    input.first_frame ??
    input.firstFrame ??
    input.start_frame ??
    input.startFrame ??
    input.first_image ??
    input.firstImage;
  const lastFrame =
    input.last_frame ??
    input.lastFrame ??
    input.end_frame ??
    input.endFrame ??
    input.last_image ??
    input.lastImage;
  const singleImage =
    input.image ??
    input.source_image ??
    input.sourceImage ??
    firstFrame;

  if (singleImage && !input.image) {
    input.image = singleImage;
  }

  if ((!Array.isArray(input.images) || input.images.length === 0) && lastFrame && (firstFrame || input.image)) {
    input.images = [firstFrame || input.image, lastFrame];
  }

  input.videos = normalizeSourceArray(input.videos ?? input.video_refs ?? input.videoRefs);
  input.audios = normalizeSourceArray(input.audios ?? input.audio_refs ?? input.audioRefs);

  if (
    (input.videos.length > 0 || input.audios.length > 0) &&
    (!Array.isArray(input.images) || input.images.length === 0) &&
    input.image
  ) {
    input.images = [input.image];
  }

  if (input.duration == null && input.dur == null) {
    input.duration = FALLBACK_DEFAULTS.duration;
  }

  return input;
}

export function detectVideoMode(input) {
  if (
    (Array.isArray(input.videos) && input.videos.length > 0) ||
    (Array.isArray(input.audios) && input.audios.length > 0)
  ) {
    return 'almighty';
  }
  if (Array.isArray(input.images) && input.images.length > 0) return 'multi_image';
  if (typeof input.image === 'string' && input.image) return 'image';
  return 'text';
}
