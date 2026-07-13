export interface RequestJsonOptions {
  timeoutMs?: number;
  init?: RequestInit;
}

/**
 * Shared JSON request helper with timeout and normalized error messages.
 */
export async function requestJson<T>(
  url: string,
  options: RequestJsonOptions = {}
): Promise<T> {
  const { timeoutMs = 15_000, init } = options;
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), timeoutMs);

  try {
    const response = await fetch(url, {
      ...init,
      signal: controller.signal,
    });

    if (!response.ok) {
      throw new Error(`HTTP ${response.status} ${response.statusText} (${url})`);
    }

    try {
      return (await response.json()) as T;
    } catch {
      throw new Error(`Invalid JSON response (${url})`);
    }
  } catch (err) {
    const error = err as Error;
    if (error.name === "AbortError") {
      throw new Error(`Request timeout after ${timeoutMs}ms (${url})`);
    }
    throw error;
  } finally {
    clearTimeout(timeout);
  }
}
