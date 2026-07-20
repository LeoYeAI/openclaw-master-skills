const AUDIO_CAPABLE_MODEL_KEYS = new Set([
  'WERYDANCE_2_0',
  'DOUBAO_1_5_PRO',
  'KLING_V3_0_STA',
  'KLING_V3_0_PRO',
  'KLING_V2_6_PRO',
  'VIDU_Q3',
  'VEO_3',
  'VEO_3_FAST',
  'VEO_3_1',
  'VEO_3_1_FAST',
  'CHATBOT_VEO_3_1_FAST',
]);

export function isAudioCapableModelKey(modelKey) {
  if (!modelKey || typeof modelKey !== 'string') return false;
  return AUDIO_CAPABLE_MODEL_KEYS.has(modelKey.trim());
}

export function resolveDefaultGenerateAudio(input, modelKey) {
  const userAudio = input?.generate_audio ?? input?.generateAudio;
  if (userAudio != null) {
    return String(userAudio).toLowerCase() === 'true';
  }
  return isAudioCapableModelKey(modelKey);
}

export { AUDIO_CAPABLE_MODEL_KEYS };
