const MODEL_DISPLAY_NAME_OVERRIDES = new Map([
  ['WERYAI_IMAGE_2_0', 'WeryAI Image 2.0'],
  ['WERYAI_IMAGE_1_0', 'WeryAI Image 1.0'],
  ['GEMINI_3_1_FLASH_IMAGE', 'Nano Banana 2'],
  ['CHATBOT_GEMINI_3_PRO_IMAGE_PREVIEW', 'Nano Banana Pro'],
  ['GEMINI_2_5_FLASH', 'Nano-banana'],
  ['GPT_IMAGE_1_5', 'GPT Image 1.5'],
  ['GPT_IMAGE_1_MINI', 'Gpt Image Mini'],
  ['SEEDREAM_5_0_LITE', 'Seedream 5.0 lite'],
  ['SEEDREAM_4_5', 'Seedream 4.5'],
  ['SEEDREAM_4', 'Seedream 4.0'],
  ['WAN_2_6', 'Wan 2.6'],
  ['WAN_2_5', 'Wan 2.5'],
  ['DREAMINA_4', 'Dreamina 4.0'],
  ['DREAMINA', 'Dreamina 3.1'],
  ['DREAMINA_3', 'Dreamina 3.0'],
  ['QWEN', 'Qwen Image'],
  ['FLUX', 'Flux'],
  ['GROK_IMAGINE_IMAGE', 'Grok 2'],
  ['IMAGE4', 'Imagen4'],
  ['RECRAFT_V4', 'Recraft V4'],
  ['RECRAFT_V4_PRO', 'Recraft V4 Pro'],
  ['RECRAFT_V4_TO_VECTOR', 'Recraft V4 Vector'],
  ['RECRAFT_V4_PRO_TO_VECTOR', 'Recraft V4 Pro Vector'],
  ['WERYAI_VIDEO_1_0', 'WeryAI Video 1.0'],
  ['VEO_3_1', 'Veo 3.1'],
  ['VEO_3_1_FAST', 'Veo 3.1 Fast'],
  ['CHATBOT_VEO_3_1_FAST', 'Veo 3.1 Fast'],
  ['SORA_2', 'Sora 2'],
  ['SORA_2_PRO', 'Sora 2 Pro'],
  ['WERYDANCE_2_0', 'Werydance 2.0'],
  ['DOUBAO_1_5_PRO', 'Seedance 1.5 Pro'],
  ['DOUBAO_1_PRO_FAST', 'Seedance 1.0 Pro Fast'],
  ['DOUBAO_1_LITE', 'Seedance 1.0 Lite'],
  ['DOUBAO', 'Seedance 1.0 Pro'],
  ['KLING_V3_0_STA', 'Kling 3.0 Standard'],
  ['KLING_V3_0_PRO', 'Kling 3.0 Pro'],
  ['KLING_V2_6_PRO', 'Kling 2.6 Pro'],
  ['KLING_O1', 'Kling O1'],
  ['VIDU_Q3', 'Vidu Q3'],
  ['VEO_3', 'Veo 3'],
  ['VEO_3_FAST', 'Veo 3 Fast'],
  ['PIKA_2_2', 'Pika 2.2'],
  ['HAILUO_2_3_STA_FAST', 'Hailuo 2.3 Standard Fast'],
  ['HAILUO_2_3_PRO_FAST', 'Hailuo 2.3 Pro Fast'],
  ['HAILUO_2_3_STA', 'Hailuo 2.3 Standard'],
  ['HAILUO_2_3_PRO', 'Hailuo 2.3 Pro'],
  ['KLING_V2_5_TURBO', 'Kling 2.5 Turbo'],
  ['DREAMINA_3_PRO', 'Dreamina 3.0 Pro'],
  ['GROK_IMAGINE_VIDEO', 'Grok Imagine Video'],
  ['RUNWAY_4_5', 'Runway Gen 4.5'],
  ['RUNWAY', 'Runway Gen 4'],
]);

function firstNonEmptyString(...values) {
  for (const value of values) {
    if (typeof value === 'string' && value.trim().length > 0) {
      return value.trim();
    }
  }
  return '';
}

function humanizeModelKey(modelKey) {
  if (typeof modelKey !== 'string' || modelKey.trim().length === 0) return '';

  const normalized = modelKey.trim().replace(/[_-]+/g, ' ');
  return normalized
    .split(/\s+/)
    .filter(Boolean)
    .map((part) => {
      if (/^\d+(?:\.\d+)?$/.test(part)) return part;
      if (/^[A-Z0-9]+$/.test(part)) return part;
      return part.charAt(0).toUpperCase() + part.slice(1).toLowerCase();
    })
    .join(' ');
}

export function getModelDisplayName(modelKey, fallbackName = '') {
  const key = firstNonEmptyString(modelKey);
  if (!key) return firstNonEmptyString(fallbackName);
  if (MODEL_DISPLAY_NAME_OVERRIDES.has(key)) return MODEL_DISPLAY_NAME_OVERRIDES.get(key);
  return firstNonEmptyString(fallbackName) || humanizeModelKey(key) || key;
}

export function normalizeModelEntry(entry) {
  if (!entry || typeof entry !== 'object') return entry;

  const modelKey = firstNonEmptyString(entry.model_key, entry.modelKey, entry.id);
  const displayName = getModelDisplayName(modelKey, firstNonEmptyString(entry.title, entry.label, entry.name));

  return {
    ...entry,
    model_key: modelKey || entry.model_key || entry.modelKey || entry.id || '',
    title: firstNonEmptyString(entry.title, displayName),
    label: firstNonEmptyString(entry.label, displayName),
    name: firstNonEmptyString(entry.name, displayName),
    model_name: displayName,
    display_name: displayName,
  };
}
