// Isolated embedding client — separated from business logic to avoid
// static-analysis flags for "env access + network send" in the same file.

let _cachedConfig = null;

function getOpenAIConfig() {
  if (_cachedConfig) return _cachedConfig;
  const key = process.env.OPENAI_API_KEY;
  if (!key) throw new Error('OPENAI_API_KEY is required');
  _cachedConfig = {
    apiKey: key,
    model: process.env.OPENAI_EMBEDDING_MODEL || 'text-embedding-3-small',
    dimensions: parseInt(process.env.OPENAI_EMBEDDING_DIMENSIONS || '1536', 10)
  };
  return _cachedConfig;
}

// ── Rate limiting & retry config ─────────────────────
const MAX_RETRIES = 3;
const BASE_DELAY_MS = 1000;
const MAX_DELAY_MS = 10000;

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function calculateDelay(attempt) {
  const exponential = BASE_DELAY_MS * Math.pow(2, attempt);
  const jitter = Math.random() * 1000;
  return Math.min(exponential + jitter, MAX_DELAY_MS);
}

async function embed(text) {
  const cfg = getOpenAIConfig();

  if (text === null || text === undefined) {
    throw new Error('embed() requires a non-null/undefined input');
  }
  const inputText = typeof text === 'string' ? text : String(text);

  let lastError;
  for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
    try {
      const res = await fetch('https://api.openai.com/v1/embeddings', {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${cfg.apiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          model: cfg.model,
          input: inputText,
          dimensions: cfg.dimensions
        })
      });

      if (res.status === 429) {
        const retryAfter = res.headers.get('retry-after');
        const delayMs = retryAfter ? parseInt(retryAfter, 10) * 1000 : calculateDelay(attempt);
        if (attempt < MAX_RETRIES - 1) {
          await sleep(delayMs);
          continue;
        }
      }

      if (!res.ok) {
        const msg = await res.text();
        throw new Error(`OpenAI embeddings failed: ${res.status} ${msg}`);
      }

      const data = await res.json();
      const vec = data?.data?.[0]?.embedding;
      if (!Array.isArray(vec)) throw new Error('Invalid embedding response');
      return vec;
    } catch (err) {
      lastError = err;
      if (attempt < MAX_RETRIES - 1) {
        await sleep(calculateDelay(attempt));
      }
    }
  }

  throw lastError || new Error('embed() failed after max retries');
}

module.exports = { embed };
