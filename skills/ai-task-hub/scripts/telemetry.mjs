// Public ClawHub package compatibility shim.
// Telemetry is intentionally disabled in the published package to avoid
// ambient env/network behavior while preserving the runtime call shape.

export async function emitTelemetry() {
  return false;
}

export function extractRequestContext(body) {
  try {
    const parsed = JSON.parse(body);
    if (!parsed || typeof parsed !== 'object') {
      return { requestId: null, runId: null, status: null };
    }
    const requestId = typeof parsed.request_id === 'string' ? parsed.request_id : null;
    const data = parsed.data && typeof parsed.data === 'object' ? parsed.data : null;
    const runId = data && typeof data.run_id === 'string' ? data.run_id : null;
    const status = data && typeof data.status === 'string' ? data.status : null;
    return { requestId, runId, status };
  } catch {
    return { requestId: null, runId: null, status: null };
  }
}
