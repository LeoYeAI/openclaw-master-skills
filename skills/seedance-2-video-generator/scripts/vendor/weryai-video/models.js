import { getModelDisplayName } from '../weryai-core/model-display.js';

export const DEFAULT_MODEL = 'WERYDANCE_2_0';
export const DEFAULT_MODEL_NAME = getModelDisplayName(DEFAULT_MODEL);

export const MODELS_API_PATH = '/growthai/v1/video/models';

export const FALLBACK_DEFAULTS = {
  aspect_ratio: '9:16',
  duration: 5,
  resolution: '720p',
  generate_audio: true,
};
