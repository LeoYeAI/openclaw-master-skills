const LOG_PREFIX = '[weryai]';

export function createClient(ctx) {
  const { apiKey, baseUrl, requestTimeoutMs, verbose } = ctx;

  async function request(method, path, body = null, { retries = 0 } = {}) {
    if (!apiKey) {
      throw Object.assign(
        new Error('Missing API key environment variable.'),
        { code: 'NO_API_KEY' },
      );
    }

    const url = `${baseUrl}${path}`;
    const headers = {
      Authorization: `Bearer ${apiKey}`,
      'Content-Type': 'application/json; charset=utf-8',
      Accept: 'application/json; charset=utf-8',
    };

    if (verbose) {
      const sanitized = body ? sanitizeForLog(body) : null;
      log(`${method} ${url}${sanitized ? ` ${JSON.stringify(sanitized)}` : ''}`);
    }

    let lastError;
    const maxAttempts = 1 + retries;

    for (let attempt = 0; attempt < maxAttempts; attempt += 1) {
      if (attempt > 0) {
        const delay = Math.min(2000 * Math.pow(2, attempt - 1), 8000);
        if (verbose) log(`Retry ${attempt}/${retries} after ${delay}ms...`);
        await sleep(delay);
      }

      try {
        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), requestTimeoutMs);

        const res = await fetch(url, {
          method,
          headers,
          body: body ? JSON.stringify(body) : undefined,
          signal: controller.signal,
        });

        clearTimeout(timer);

        let data;
        try {
          data = await res.json();
        } catch {
          data = { status: res.status, msg: `Non-JSON response (HTTP ${res.status})` };
        }

        if (verbose) {
          log(`Response ${res.status}: ${JSON.stringify(sanitizeForLog(data))}`);
        }

        return { httpStatus: res.status, ...data };
      } catch (err) {
        lastError = err;
        if (err.name === 'AbortError') {
          lastError = new Error(`Request timeout after ${requestTimeoutMs}ms: ${method} ${path}`);
          lastError.code = 'TIMEOUT';
        }
        if (attempt === maxAttempts - 1) break;
      }
    }

    throw lastError;
  }

  return {
    post: (path, body, opts) => request('POST', path, body, opts),
    get: (path, opts) => request('GET', path, null, opts),
  };
}

function sanitizeForLog(obj) {
  if (!obj || typeof obj !== 'object') return obj;
  const copy = Array.isArray(obj) ? [...obj] : { ...obj };

  for (const key of Object.keys(copy)) {
    const value = copy[key];
    if (/authorization|api[_-]?key/i.test(key)) {
      copy[key] = '***';
    } else if (typeof value === 'string' && /^(prompt|negative_prompt|negativePrompt|description|lyrics)$/i.test(key)) {
      copy[key] = truncate(value);
    } else if (typeof value === 'string' && /^(image|reference_audio|webhook_url)$/i.test(key)) {
      copy[key] = truncate(value);
    } else if (Array.isArray(value) && /^(images|videos|audios|image_url)$/i.test(key)) {
      copy[key] = value.map((item) => (typeof item === 'string' ? truncate(item) : item));
    } else if (value && typeof value === 'object') {
      copy[key] = sanitizeForLog(value);
    }
  }

  return copy;
}

function truncate(value, limit = 80) {
  return value.length > limit ? `${value.slice(0, limit)}...` : value;
}

function log(msg) {
  process.stderr.write(`${LOG_PREFIX} ${msg}\n`);
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export { log, sleep };
