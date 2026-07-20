import { fetchModelRegistry } from './model-registry.js';

const VALID_MODES = ['text_to_video', 'image_to_video', 'multi_image_to_video'];

export async function execute(input, ctx) {
  const registry = await fetchModelRegistry(ctx);

  if (!registry) {
    return {
      ok: false,
      phase: 'failed',
      errorCode: 'REGISTRY_UNAVAILABLE',
      errorMessage: 'Could not fetch model list from WeryAI API. Check API key and network.',
    };
  }

  const mode = input.mode;
  if (mode && !VALID_MODES.includes(mode)) {
    return {
      ok: false,
      phase: 'failed',
      errorCode: 'VALIDATION',
      errorMessage: `Invalid mode "${mode}". Use one of: ${VALID_MODES.join(', ')}.`,
    };
  }

  const result = { ok: true, phase: 'completed' };
  if (!mode || mode === 'text_to_video') result.text_to_video = Array.from(registry.text_to_video.values());
  if (!mode || mode === 'image_to_video') result.image_to_video = Array.from(registry.image_to_video.values());
  if (!mode || mode === 'multi_image_to_video') {
    result.multi_image_to_video = Array.from(registry.multi_image_to_video.values());
  }
  return result;
}

export default execute;
