/**
 * TotalReclaw Plugin - LLM Client
 *
 * Auto-detects the user's LLM provider from OpenClaw's config and derives a
 * cheap extraction model. Supports OpenAI-compatible APIs and Anthropic's
 * Messages API. No external dependencies -- uses native fetch().
 *
 * Embedding generation has been moved to embedding.ts (local ONNX model via
 * @huggingface/transformers). No API key needed for embeddings.
 */

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

interface ChatCompletionResponse {
  choices: Array<{
    message: {
      content: string | null;
    };
  }>;
}

/** Anthropic Messages API response shape. */
interface AnthropicMessagesResponse {
  content: Array<{
    type: string;
    text?: string;
  }>;
}

export interface LLMClientConfig {
  apiKey: string;
  baseUrl: string;
  model: string;
  apiFormat: 'openai' | 'anthropic';
}

// ---------------------------------------------------------------------------
// Provider mappings
// ---------------------------------------------------------------------------

const PROVIDER_ENV_VARS: Record<string, string[]> = {
  zai:        ['ZAI_API_KEY'],
  anthropic:  ['ANTHROPIC_API_KEY'],
  openai:     ['OPENAI_API_KEY'],
  gemini:     ['GEMINI_API_KEY'],
  google:     ['GEMINI_API_KEY', 'GOOGLE_API_KEY'],
  mistral:    ['MISTRAL_API_KEY'],
  groq:       ['GROQ_API_KEY'],
  deepseek:   ['DEEPSEEK_API_KEY'],
  openrouter: ['OPENROUTER_API_KEY'],
  xai:        ['XAI_API_KEY'],
  together:   ['TOGETHER_API_KEY'],
  cerebras:   ['CEREBRAS_API_KEY'],
};

const PROVIDER_BASE_URLS: Record<string, string> = {
  zai:        'https://api.z.ai/api/paas/v4',
  anthropic:  'https://api.anthropic.com/v1',
  openai:     'https://api.openai.com/v1',
  gemini:     'https://generativelanguage.googleapis.com/v1beta/openai',
  google:     'https://generativelanguage.googleapis.com/v1beta/openai',
  mistral:    'https://api.mistral.ai/v1',
  groq:       'https://api.groq.com/openai/v1',
  deepseek:   'https://api.deepseek.com/v1',
  openrouter: 'https://openrouter.ai/api/v1',
  xai:        'https://api.x.ai/v1',
  together:   'https://api.together.xyz/v1',
  cerebras:   'https://api.cerebras.ai/v1',
};

// ---------------------------------------------------------------------------
// Cheap model derivation
// ---------------------------------------------------------------------------

const CHEAP_INDICATORS = ['flash', 'mini', 'nano', 'haiku', 'small', 'lite', 'fast'];

/**
 * Derive a cheap/fast model suitable for fact extraction, given the user's
 * provider and primary (potentially expensive) model.
 */
function deriveCheapModel(provider: string, primaryModel: string): string {
  // If already on a cheap model, use it as-is
  if (CHEAP_INDICATORS.some((s) => primaryModel.toLowerCase().includes(s))) {
    return primaryModel;
  }

  // Derive based on provider naming conventions
  switch (provider) {
    case 'zai': {
      // glm-5 -> glm-4.5-flash, glm-4.6 -> glm-4.5-flash
      return 'glm-4.5-flash';
    }
    case 'anthropic': {
      // claude-sonnet-4-5 -> claude-haiku-4-5-20251001
      return 'claude-haiku-4-5-20251001';
    }
    case 'openai': {
      // gpt-4.1 -> gpt-4.1-mini, gpt-4o -> gpt-4.1-mini
      return 'gpt-4.1-mini';
    }
    case 'gemini':
    case 'google': {
      return 'gemini-2.0-flash';
    }
    case 'mistral': {
      return 'mistral-small-latest';
    }
    case 'groq': {
      return 'llama-3.3-70b-versatile';
    }
    case 'deepseek': {
      return 'deepseek-chat';
    }
    case 'openrouter': {
      // Use Anthropic Haiku via OpenRouter (cheap and good at JSON)
      return 'anthropic/claude-haiku-4-5-20251001';
    }
    case 'xai': {
      return 'grok-2';
    }
    default: {
      // Fallback: try the primary model itself
      return primaryModel;
    }
  }
}

// ---------------------------------------------------------------------------
// Module-level state
// ---------------------------------------------------------------------------

let _cachedConfig: LLMClientConfig | null = null;
let _initialized = false;
let _logger: { warn: (msg: string) => void } | null = null;

// ---------------------------------------------------------------------------
// Initialization
// ---------------------------------------------------------------------------

/**
 * Initialize the LLM client by detecting the provider from OpenClaw's config.
 * Called once from the plugin's `register()` function.
 *
 * Resolution order (highest priority first):
 *   1. TOTALRECLAW_LLM_MODEL env var (power user override for model)
 *   2. Plugin config `extraction.model` (if provided)
 *   3. Auto-derived from provider heuristic
 *   4. Fallback: try common env vars (ZAI_API_KEY, OPENAI_API_KEY) for dev/test
 */
export function initLLMClient(options: {
  primaryModel?: string;
  pluginConfig?: Record<string, unknown>;
  logger?: { warn: (msg: string) => void };
}): void {
  _logger = options.logger ?? null;
  _initialized = true;
  _cachedConfig = null;

  const { primaryModel, pluginConfig } = options;

  // Check if extraction is explicitly disabled
  const extraction = pluginConfig?.extraction as Record<string, unknown> | undefined;
  if (extraction?.enabled === false) {
    _logger?.warn('TotalReclaw: LLM extraction explicitly disabled via plugin config.');
    return;
  }

  // --- Try to resolve from primaryModel (auto-detect path) ---
  if (primaryModel) {
    const parts = primaryModel.split('/');
    const provider = parts.length >= 2 ? parts[0].toLowerCase() : '';
    const modelName = parts.length >= 2 ? parts.slice(1).join('/') : primaryModel;

    if (provider) {
      // Find the API key for this provider
      const envVarNames = PROVIDER_ENV_VARS[provider];
      const apiKey = envVarNames
        ? envVarNames.map((name) => process.env[name]).find(Boolean)
        : undefined;

      if (apiKey) {
        const baseUrl = PROVIDER_BASE_URLS[provider];
        if (baseUrl) {
          // Determine model: env override > plugin config > auto-derived
          const model =
            process.env.TOTALRECLAW_LLM_MODEL ??
            (typeof extraction?.model === 'string' ? extraction.model : null) ??
            deriveCheapModel(provider, modelName);

          const apiFormat: 'openai' | 'anthropic' =
            provider === 'anthropic' ? 'anthropic' : 'openai';

          _cachedConfig = { apiKey, baseUrl, model, apiFormat };
          return;
        }
      }
    }
  }

  // --- Fallback: try common env vars (for dev/test without OpenClaw config) ---
  const fallbackProviders: Array<[string, string, string]> = [
    ['zai', 'ZAI_API_KEY', 'glm-4.5-flash'],
    ['openai', 'OPENAI_API_KEY', 'gpt-4.1-mini'],
    ['anthropic', 'ANTHROPIC_API_KEY', 'claude-haiku-4-5-20251001'],
    ['gemini', 'GEMINI_API_KEY', 'gemini-2.0-flash'],
  ];

  for (const [provider, envVar, defaultModel] of fallbackProviders) {
    const apiKey = process.env[envVar];
    if (apiKey) {
      const model = process.env.TOTALRECLAW_LLM_MODEL ??
        (typeof extraction?.model === 'string' ? extraction.model : null) ??
        defaultModel;

      const apiFormat: 'openai' | 'anthropic' =
        provider === 'anthropic' ? 'anthropic' : 'openai';

      _cachedConfig = {
        apiKey,
        baseUrl: PROVIDER_BASE_URLS[provider],
        model,
        apiFormat,
      };
      return;
    }
  }

  // No LLM available
  _logger?.warn(
    'TotalReclaw: No LLM available for auto-extraction. ' +
    'Set an API key for your provider or configure extraction in plugin settings.',
  );
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

/**
 * Resolve LLM configuration. Returns the cached config set by `initLLMClient()`,
 * or falls back to the legacy env-var detection if `initLLMClient()` was never called.
 */
export function resolveLLMConfig(): LLMClientConfig | null {
  if (_initialized) {
    return _cachedConfig;
  }

  // Legacy fallback: if initLLMClient() was never called (e.g. running outside
  // the plugin context), try the old env-var approach for backwards compat.
  const zaiKey = process.env.ZAI_API_KEY;
  const openaiKey = process.env.OPENAI_API_KEY;

  const model = process.env.TOTALRECLAW_LLM_MODEL
    ?? (zaiKey ? 'glm-4.5-flash' : 'gpt-4.1-mini');

  if (zaiKey) {
    return {
      apiKey: zaiKey,
      baseUrl: 'https://api.z.ai/api/paas/v4',
      model,
      apiFormat: 'openai',
    };
  }

  if (openaiKey) {
    return {
      apiKey: openaiKey,
      baseUrl: 'https://api.openai.com/v1',
      model,
      apiFormat: 'openai',
    };
  }

  return null;
}

/**
 * Call the LLM chat completion endpoint.
 *
 * Supports both OpenAI-compatible format and Anthropic Messages API,
 * determined by `config.apiFormat`.
 *
 * @returns The assistant's response content, or null on failure.
 */
export async function chatCompletion(
  config: LLMClientConfig,
  messages: ChatMessage[],
  options?: { maxTokens?: number; temperature?: number },
): Promise<string | null> {
  const maxTokens = options?.maxTokens ?? 2048;
  const temperature = options?.temperature ?? 0; // Deterministic output for dedup (same input → same text → same content fingerprint)

  if (config.apiFormat === 'anthropic') {
    return chatCompletionAnthropic(config, messages, maxTokens, temperature);
  }

  return chatCompletionOpenAI(config, messages, maxTokens, temperature);
}

// ---------------------------------------------------------------------------
// OpenAI-compatible chat completion
// ---------------------------------------------------------------------------

async function chatCompletionOpenAI(
  config: LLMClientConfig,
  messages: ChatMessage[],
  maxTokens: number,
  temperature: number,
): Promise<string | null> {
  const url = `${config.baseUrl}/chat/completions`;

  const body: Record<string, unknown> = {
    model: config.model,
    messages,
    temperature,
    max_completion_tokens: maxTokens,
  };

  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${config.apiKey}`,
      },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(30_000), // 30 second timeout
    });

    if (!res.ok) {
      const text = await res.text().catch(() => '');
      throw new Error(`LLM API ${res.status}: ${text.slice(0, 200)}`);
    }

    const json = (await res.json()) as ChatCompletionResponse;
    return json.choices?.[0]?.message?.content ?? null;
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    throw new Error(`LLM call failed: ${msg}`);
  }
}

// ---------------------------------------------------------------------------
// Anthropic Messages API chat completion
// ---------------------------------------------------------------------------

async function chatCompletionAnthropic(
  config: LLMClientConfig,
  messages: ChatMessage[],
  maxTokens: number,
  temperature: number,
): Promise<string | null> {
  const url = `${config.baseUrl}/messages`;

  // Anthropic requires system prompt to be a top-level param, not in messages
  let system: string | undefined;
  const apiMessages: Array<{ role: string; content: string }> = [];

  for (const msg of messages) {
    if (msg.role === 'system') {
      system = msg.content;
    } else {
      apiMessages.push({ role: msg.role, content: msg.content });
    }
  }

  const body: Record<string, unknown> = {
    model: config.model,
    max_tokens: maxTokens,
    temperature,
    messages: apiMessages,
  };

  if (system) {
    body.system = system;
  }

  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': config.apiKey,
        'anthropic-version': '2023-06-01',
      },
      body: JSON.stringify(body),
      signal: AbortSignal.timeout(30_000),
    });

    if (!res.ok) {
      const text = await res.text().catch(() => '');
      throw new Error(`Anthropic API ${res.status}: ${text.slice(0, 200)}`);
    }

    const json = (await res.json()) as AnthropicMessagesResponse;
    const textBlock = json.content?.find((block) => block.type === 'text');
    return textBlock?.text ?? null;
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    throw new Error(`LLM call failed: ${msg}`);
  }
}

// ---------------------------------------------------------------------------
// Embedding (re-exported from local ONNX module)
// ---------------------------------------------------------------------------

// Embeddings are now generated locally via @huggingface/transformers
// (bge-small-en-v1.5 ONNX model). No API key needed.
// See embedding.ts for implementation details.
export { generateEmbedding, getEmbeddingDims } from './embedding.js';
