import type { GatewayBrowserClient } from "../gateway";
import type { AgentLoopMode, EnhancedLoopConfig, ModelInfo } from "../views/mode";
import { getDefaultConfig } from "../views/mode";

export type ModeState = {
  client: GatewayBrowserClient | null;
  connected: boolean;
  modeLoading: boolean;
  modeCurrentMode: AgentLoopMode;
  modeConfig: EnhancedLoopConfig | null;
  modeSaving: boolean;
  modeError: string | null;
  modeSuccess: string | null;
  modeAvailableModels: ModelInfo[];
};

function getErrorMessage(err: unknown): string {
  if (err instanceof Error) return err.message;
  return String(err);
}

export async function loadModeStatus(state: ModeState): Promise<void> {
  if (!state.client || !state.connected) return;
  if (state.modeLoading) return;

  state.modeLoading = true;
  state.modeError = null;
  state.modeSuccess = null;

  try {
    // Fetch mode config and available models in parallel
    const [result, modelsResult] = await Promise.all([
      state.client.request("mode.status", {}) as Promise<{
        mode: AgentLoopMode;
        config: EnhancedLoopConfig;
        error?: string;
      } | undefined>,
      state.client.request("models.list", {}) as Promise<{
        models?: ModelInfo[];
      } | undefined>,
    ]);

    if (result) {
      if (result.error) {
        state.modeError = result.error;
      } else {
        state.modeCurrentMode = result.mode;
        state.modeConfig = result.config;
      }
    }

    // Populate available models from the catalog (same as agents page)
    state.modeAvailableModels = modelsResult?.models ?? [];
  } catch (err) {
    state.modeError = getErrorMessage(err);
  } finally {
    state.modeLoading = false;
  }
}

export async function setAgentLoopMode(
  state: ModeState,
  mode: AgentLoopMode
): Promise<void> {
  if (!state.client || !state.connected) return;

  state.modeError = null;
  state.modeSuccess = null;

  // Update local state immediately for responsiveness
  const previousMode = state.modeCurrentMode;
  state.modeCurrentMode = mode;

  // If switching to enhanced, ensure config exists
  if (mode === "enhanced" && !state.modeConfig) {
    state.modeConfig = getDefaultConfig();
  }

  // Update the enabled flag in config
  if (state.modeConfig) {
    state.modeConfig = {
      ...state.modeConfig,
      enabled: mode === "enhanced",
    };
  }
}

export function updateModeConfig(
  state: ModeState,
  update: Partial<EnhancedLoopConfig>
): void {
  if (!state.modeConfig) {
    state.modeConfig = getDefaultConfig();
  }

  // Deep merge the update
  state.modeConfig = deepMerge(state.modeConfig, update);
}

export async function saveModeConfig(state: ModeState): Promise<void> {
  if (!state.client || !state.connected) return;
  if (state.modeSaving) return;

  state.modeSaving = true;
  state.modeError = null;
  state.modeSuccess = null;

  try {
    const result = (await state.client.request("mode.save", {
      mode: state.modeCurrentMode,
      config: state.modeConfig,
    })) as { success: boolean; error?: string } | undefined;

    if (result) {
      if (result.error) {
        state.modeError = result.error;
      } else if (result.success) {
        state.modeSuccess = "Configuration saved";
        // Clear success message after 3 seconds
        setTimeout(() => {
          state.modeSuccess = null;
        }, 3000);
      }
    }
  } catch (err) {
    state.modeError = getErrorMessage(err);
  } finally {
    state.modeSaving = false;
  }
}

export function resetModeConfig(state: ModeState): void {
  state.modeConfig = getDefaultConfig();
  state.modeCurrentMode = "core";
  state.modeConfig.enabled = false;
  state.modeSuccess = null;
  state.modeError = null;
}

// Helper for deep merging config objects
function deepMerge<T extends Record<string, unknown>>(
  target: T,
  source: Partial<T>
): T {
  const result = { ...target };

  for (const key of Object.keys(source) as Array<keyof T>) {
    const sourceValue = source[key];
    const targetValue = target[key];

    if (
      sourceValue !== undefined &&
      typeof sourceValue === "object" &&
      sourceValue !== null &&
      !Array.isArray(sourceValue) &&
      typeof targetValue === "object" &&
      targetValue !== null &&
      !Array.isArray(targetValue)
    ) {
      result[key] = deepMerge(
        targetValue as Record<string, unknown>,
        sourceValue as Record<string, unknown>
      ) as T[keyof T];
    } else if (sourceValue !== undefined) {
      result[key] = sourceValue as T[keyof T];
    }
  }

  return result;
}
