const BASE_URL = "https://qveris.ai/api/v1";

async function requestJson(path, { method = "POST", query = {}, body, timeoutMs = 30000, apiKey }) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const url = new URL(`${BASE_URL}${path}`);
    for (const [key, value] of Object.entries(query)) {
      if (value !== undefined && value !== null) {
        url.searchParams.set(key, String(value));
      }
    }

    const response = await fetch(url.toString(), {
      method,
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json",
      },
      ...(body === undefined ? {} : { body: JSON.stringify(body) }),
      signal: controller.signal,
    });

    if (!response.ok) {
      const text = await response.text();
      throw new Error(`HTTP ${response.status}: ${text}`);
    }

    return await response.json();
  } finally {
    clearTimeout(timeout);
  }
}

export function getBaseUrl() {
  return BASE_URL;
}

export async function discoverTools({ apiKey, query, limit = 10, timeoutMs = 30000 }) {
  return requestJson("/search", {
    apiKey,
    body: { query, limit },
    timeoutMs,
  });
}

export async function inspectToolsByIds({ apiKey, toolIds, discoveryId, timeoutMs = 30000 }) {
  const body = { tool_ids: toolIds };
  if (discoveryId) {
    body.search_id = discoveryId;
  }

  return requestJson("/tools/by-ids", {
    apiKey,
    body,
    timeoutMs,
  });
}

export async function callTool({
  apiKey,
  toolId,
  discoveryId,
  parameters,
  maxResponseSize = 20480,
  timeoutMs = 120000,
}) {
  return requestJson("/tools/execute", {
    apiKey,
    query: { tool_id: toolId },
    body: {
      search_id: discoveryId,
      parameters,
      max_response_size: maxResponseSize,
    },
    timeoutMs,
  });
}
