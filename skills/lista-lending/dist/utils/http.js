/**
 * Shared JSON request helper with timeout and normalized error messages.
 */
export async function requestJson(url, options = {}) {
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
            return (await response.json());
        }
        catch {
            throw new Error(`Invalid JSON response (${url})`);
        }
    }
    catch (err) {
        const error = err;
        if (error.name === "AbortError") {
            throw new Error(`Request timeout after ${timeoutMs}ms (${url})`);
        }
        throw error;
    }
    finally {
        clearTimeout(timeout);
    }
}
