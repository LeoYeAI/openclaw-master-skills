const DEFAULT_BASE_URL = 'https://gateway-api.binaryworks.app';

export function getDefaultBaseUrl() {
  return DEFAULT_BASE_URL;
}

export function normalizeBaseUrl(baseUrlRaw) {
  const candidate = readToken(baseUrlRaw) || DEFAULT_BASE_URL;
  try {
    const parsed = new URL(candidate);
    if (parsed.protocol !== 'http:' && parsed.protocol !== 'https:') {
      throw new Error('invalid protocol');
    }
    return parsed.toString().replace(/\/+$/, '');
  } catch {
    throw createBaseUrlError(400, `invalid base_url: ${String(baseUrlRaw ?? '')}`);
  }
}

export function isHttpBaseUrl(value) {
  try {
    const parsed = new URL(value);
    return parsed.protocol === 'http:' || parsed.protocol === 'https:';
  } catch {
    return false;
  }
}

function readToken(value) {
  if (typeof value !== 'string') {
    return '';
  }
  return value.trim();
}

function createBaseUrlError(status, message) {
  const error = new Error(message);
  error.status = status;
  error.code = 'VALIDATION_BAD_REQUEST';
  return error;
}
