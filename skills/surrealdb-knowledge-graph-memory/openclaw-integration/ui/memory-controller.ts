import type { GatewayBrowserClient } from "../gateway";
import type { MemoryHealthStatus, MemoryStats } from "../views/memory";

export type ExtractionProgress = {
  running: boolean;
  phase?: string;
  current?: number;
  total?: number;
  percent?: number;
  message?: string;
  detail?: string;
  error?: string;
};

export type MemoryState = {
  client: GatewayBrowserClient | null;
  connected: boolean;
  memoryLoading: boolean;
  memoryHealth: MemoryHealthStatus | null;
  memoryStats: MemoryStats | null;
  memoryError: string | null;
  memoryMaintenanceLog: string | null;
  memoryInstallLog: string | null;
  memoryExtractionLog: string | null;
  memoryExtractionProgress: ExtractionProgress | null;
  memoryBusyAction: string | null;
  _progressPollInterval?: ReturnType<typeof setInterval>;
};

function getErrorMessage(err: unknown) {
  if (err instanceof Error) return err.message;
  return String(err);
}

export async function loadMemoryStatus(state: MemoryState) {
  if (!state.client || !state.connected) return;
  if (state.memoryLoading) return;

  state.memoryLoading = true;
  state.memoryError = null;

  try {
    // Load health status
    const healthRes = (await state.client.request("memory.health", {})) as
      | MemoryHealthStatus
      | { error: string }
      | undefined;

    if (healthRes && "error" in healthRes) {
      state.memoryError = healthRes.error;
    } else if (healthRes) {
      state.memoryHealth = healthRes;
    }

    // Load stats if server is running
    if (state.memoryHealth?.surrealdb_server?.running) {
      const statsRes = (await state.client.request("memory.stats", {})) as
        | MemoryStats
        | { error: string }
        | undefined;

      if (statsRes && "error" in statsRes) {
        state.memoryStats = { ...statsRes, facts: 0, entities: 0, relationships: 0, archived: 0, avg_confidence: 0, by_source: [] } as MemoryStats;
      } else if (statsRes) {
        state.memoryStats = statsRes;
      }
    }
  } catch (err) {
    state.memoryError = getErrorMessage(err);
  } finally {
    state.memoryLoading = false;
  }
}

export async function autoRepairMemory(state: MemoryState) {
  if (!state.client || !state.connected) return;
  if (state.memoryBusyAction) return;

  state.memoryBusyAction = "repair";
  state.memoryError = null;
  state.memoryInstallLog = null;

  try {
    const result = (await state.client.request("memory.repair", {
      timeoutMs: 120000,
    })) as { success: boolean; steps: unknown[]; error?: string } | undefined;

    if (result) {
      state.memoryInstallLog = JSON.stringify(result, null, 2);
      if (!result.success && result.error) {
        state.memoryError = result.error;
      }
    }

    // Refresh status
    await loadMemoryStatus(state);
  } catch (err) {
    state.memoryError = getErrorMessage(err);
  } finally {
    state.memoryBusyAction = null;
  }
}

export async function installMemoryBinary(state: MemoryState) {
  if (!state.client || !state.connected) return;
  if (state.memoryBusyAction) return;

  state.memoryBusyAction = "binary";
  state.memoryInstallLog = null;

  try {
    const result = (await state.client.request("memory.install.binary", {
      timeoutMs: 120000,
    })) as { success: boolean; stdout?: string; stderr?: string; error?: string } | undefined;

    if (result) {
      state.memoryInstallLog = result.stdout || result.stderr || result.error || JSON.stringify(result);
    }

    await loadMemoryStatus(state);
  } catch (err) {
    state.memoryError = getErrorMessage(err);
  } finally {
    state.memoryBusyAction = null;
  }
}

export async function installMemoryPython(state: MemoryState) {
  if (!state.client || !state.connected) return;
  if (state.memoryBusyAction) return;

  state.memoryBusyAction = "python";
  state.memoryInstallLog = null;

  try {
    const result = (await state.client.request("memory.install.python", {
      timeoutMs: 120000,
    })) as { success: boolean; stdout?: string; stderr?: string; error?: string } | undefined;

    if (result) {
      state.memoryInstallLog = result.stdout || result.stderr || result.error || JSON.stringify(result);
    }

    await loadMemoryStatus(state);
  } catch (err) {
    state.memoryError = getErrorMessage(err);
  } finally {
    state.memoryBusyAction = null;
  }
}

export async function startMemoryServer(state: MemoryState) {
  if (!state.client || !state.connected) return;
  if (state.memoryBusyAction) return;

  state.memoryBusyAction = "start";
  state.memoryInstallLog = null;

  try {
    const result = (await state.client.request("memory.install.start", {
      timeoutMs: 30000,
    })) as { success: boolean; pid?: number; error?: string } | undefined;

    if (result) {
      state.memoryInstallLog = JSON.stringify(result, null, 2);
    }

    // Wait a moment for server to start
    await new Promise((r) => setTimeout(r, 2000));
    await loadMemoryStatus(state);
  } catch (err) {
    state.memoryError = getErrorMessage(err);
  } finally {
    state.memoryBusyAction = null;
  }
}

export async function initMemorySchema(state: MemoryState) {
  if (!state.client || !state.connected) return;
  if (state.memoryBusyAction) return;

  state.memoryBusyAction = "schema";
  state.memoryInstallLog = null;

  try {
    const result = (await state.client.request("memory.install.schema", {
      timeoutMs: 30000,
    })) as { success: boolean; stdout?: string; stderr?: string; error?: string } | undefined;

    if (result) {
      state.memoryInstallLog = result.stdout || result.stderr || result.error || JSON.stringify(result);
    }

    await loadMemoryStatus(state);
  } catch (err) {
    state.memoryError = getErrorMessage(err);
  } finally {
    state.memoryBusyAction = null;
  }
}

export async function runMemoryMaintenance(
  state: MemoryState,
  operation: "decay" | "prune" | "full"
) {
  if (!state.client || !state.connected) return;
  if (state.memoryBusyAction) return;

  state.memoryBusyAction = operation;
  state.memoryMaintenanceLog = null;

  try {
    const result = (await state.client.request("memory.maintenance", {
      operation,
      timeoutMs: 60000,
    })) as { success: boolean; [key: string]: unknown } | undefined;

    if (result) {
      state.memoryMaintenanceLog = JSON.stringify(result, null, 2);
    }

    await loadMemoryStatus(state);
  } catch (err) {
    state.memoryError = getErrorMessage(err);
  } finally {
    state.memoryBusyAction = null;
  }
}

export async function pollExtractionProgress(state: MemoryState) {
  if (!state.client || !state.connected) return;
  
  try {
    const result = (await state.client.request("memory.extractionProgress", {})) as ExtractionProgress | undefined;
    if (result) {
      state.memoryExtractionProgress = result;
      
      // If completed, stop polling and refresh stats
      if (!result.running && state._progressPollInterval) {
        clearInterval(state._progressPollInterval);
        state._progressPollInterval = undefined;
        await loadMemoryStatus(state);
      }
    }
  } catch {
    // Ignore polling errors
  }
}

function startProgressPolling(state: MemoryState) {
  // Clear any existing interval
  if (state._progressPollInterval) {
    clearInterval(state._progressPollInterval);
  }
  
  // Poll every 500ms
  state._progressPollInterval = setInterval(() => {
    pollExtractionProgress(state);
  }, 500);
  
  // Initial poll
  pollExtractionProgress(state);
}

function stopProgressPolling(state: MemoryState) {
  if (state._progressPollInterval) {
    clearInterval(state._progressPollInterval);
    state._progressPollInterval = undefined;
  }
}

export async function runMemoryExtraction(
  state: MemoryState,
  operation: "extract" | "relations" | "full"
) {
  if (!state.client || !state.connected) return;
  if (state.memoryBusyAction) return;

  const actionName = operation === "relations" ? "relations" : operation === "full" ? "full-extract" : "extract";
  state.memoryBusyAction = actionName;
  state.memoryExtractionLog = null;
  state.memoryExtractionProgress = { running: true, phase: "starting", percent: 0, message: "Starting..." };

  // Start polling for progress
  startProgressPolling(state);

  try {
    const params: { full?: boolean; reconcile?: boolean; relations?: boolean; timeoutMs: number } = {
      timeoutMs: 300000, // 5 minutes - extraction can take a while
    };

    if (operation === "extract") {
      // Just extract changed files
    } else if (operation === "relations") {
      params.relations = true;
    } else if (operation === "full") {
      params.full = true;
    }

    const result = (await state.client.request("memory.runExtraction", params)) as 
      | { success: boolean; output?: string; stderr?: string; error?: string }
      | undefined;

    if (result) {
      if (result.success) {
        state.memoryExtractionLog = result.output || "Extraction completed successfully";
      } else {
        state.memoryExtractionLog = result.error || result.stderr || "Extraction failed";
        state.memoryError = result.error || "Extraction failed";
      }
    }

    await loadMemoryStatus(state);
  } catch (err) {
    state.memoryError = getErrorMessage(err);
    state.memoryExtractionLog = getErrorMessage(err);
  } finally {
    stopProgressPolling(state);
    state.memoryBusyAction = null;
    state.memoryExtractionProgress = null;
  }
}
