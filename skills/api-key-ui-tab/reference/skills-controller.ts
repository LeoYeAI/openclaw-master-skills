import type { GatewayBrowserClient } from "../gateway.ts";
import type { SkillStatusReport } from "../types.ts";

export type VaultKeyEntry = {
  id: string;
  masked: string;
};

export type SkillsState = {
  client: GatewayBrowserClient | null;
  connected: boolean;
  skillsLoading: boolean;
  skillsReport: SkillStatusReport | null;
  skillsError: string | null;
  skillsBusyKey: string | null;
  skillEdits: Record<string, string>;
  skillMessages: SkillMessageMap;
  vaultKeys: VaultKeyEntry[];
  vaultKeysLoading: boolean;
};

export type SkillMessage = {
  kind: "success" | "error";
  message: string;
};

export type SkillMessageMap = Record<string, SkillMessage>;

type LoadSkillsOptions = {
  clearMessages?: boolean;
};

function setSkillMessage(state: SkillsState, key: string, message?: SkillMessage) {
  if (!key.trim()) {
    return;
  }
  const next = { ...state.skillMessages };
  if (message) {
    next[key] = message;
  } else {
    delete next[key];
  }
  state.skillMessages = next;
}

function getErrorMessage(err: unknown) {
  if (err instanceof Error) {
    return err.message;
  }
  return String(err);
}

export async function loadSkills(state: SkillsState, options?: LoadSkillsOptions) {
  if (options?.clearMessages && Object.keys(state.skillMessages).length > 0) {
    state.skillMessages = {};
  }
  if (!state.client || !state.connected) {
    return;
  }
  if (state.skillsLoading) {
    return;
  }
  state.skillsLoading = true;
  state.skillsError = null;
  try {
    const res = await state.client.request<SkillStatusReport | undefined>("skills.status", {});
    if (res) {
      state.skillsReport = res;
    }
  } catch (err) {
    state.skillsError = getErrorMessage(err);
  } finally {
    state.skillsLoading = false;
  }
}

export function updateSkillEdit(state: SkillsState, skillKey: string, value: string) {
  state.skillEdits = { ...state.skillEdits, [skillKey]: value };
}

export async function updateSkillEnabled(state: SkillsState, skillKey: string, enabled: boolean) {
  if (!state.client || !state.connected) {
    return;
  }
  state.skillsBusyKey = skillKey;
  state.skillsError = null;
  try {
    await state.client.request("skills.update", { skillKey, enabled });
    await loadSkills(state);
    setSkillMessage(state, skillKey, {
      kind: "success",
      message: enabled ? "Skill enabled" : "Skill disabled",
    });
  } catch (err) {
    const message = getErrorMessage(err);
    state.skillsError = message;
    setSkillMessage(state, skillKey, {
      kind: "error",
      message,
    });
  } finally {
    state.skillsBusyKey = null;
  }
}

export async function saveSkillApiKey(state: SkillsState, skillKey: string) {
  if (!state.client || !state.connected) {
    return;
  }
  state.skillsBusyKey = skillKey;
  state.skillsError = null;
  try {
    const apiKey = state.skillEdits[skillKey] ?? "";
    await state.client.request("skills.update", { skillKey, apiKey });
    await loadSkills(state);
    setSkillMessage(state, skillKey, {
      kind: "success",
      message: "API key saved",
    });
  } catch (err) {
    const message = getErrorMessage(err);
    state.skillsError = message;
    setSkillMessage(state, skillKey, {
      kind: "error",
      message,
    });
  } finally {
    state.skillsBusyKey = null;
  }
}

export async function installSkill(
  state: SkillsState,
  skillKey: string,
  name: string,
  installId: string,
) {
  if (!state.client || !state.connected) {
    return;
  }
  state.skillsBusyKey = skillKey;
  state.skillsError = null;
  try {
    const result = await state.client.request<{ message?: string }>("skills.install", {
      name,
      installId,
      timeoutMs: 120000,
    });
    await loadSkills(state);
    setSkillMessage(state, skillKey, {
      kind: "success",
      message: result?.message ?? "Installed",
    });
  } catch (err) {
    const message = getErrorMessage(err);
    state.skillsError = message;
    setSkillMessage(state, skillKey, {
      kind: "error",
      message,
    });
  } finally {
    state.skillsBusyKey = null;
  }
}

export async function loadVaultKeys(state: SkillsState) {
  if (!state.client || !state.connected) return;
  state.vaultKeysLoading = true;
  try {
    const res = await state.client.request<{ keys: VaultKeyEntry[] }>("secrets.list", {});
    state.vaultKeys = res?.keys ?? [];
  } catch {
    state.vaultKeys = [];
  } finally {
    state.vaultKeysLoading = false;
  }
}

export async function linkSkillToVaultKey(state: SkillsState, skillKey: string, vaultKeyId: string) {
  if (!state.client || !state.connected) return;
  state.skillsBusyKey = skillKey;
  try {
    await state.client.request("skills.update", { skillKey, vaultKeyId });
    await loadSkills(state);
    setSkillMessage(state, skillKey, {
      kind: "success",
      message: vaultKeyId ? "Linked to vault key: " + vaultKeyId : "Unlinked from vault key",
    });
  } catch (err) {
    setSkillMessage(state, skillKey, { kind: "error", message: getErrorMessage(err) });
  } finally {
    state.skillsBusyKey = null;
  }
}

export async function addVaultKeyAndLink(
  state: SkillsState,
  skillKey: string,
  keyName: string,
  keyValue: string,
) {
  if (!state.client || !state.connected) return;
  state.skillsBusyKey = skillKey;
  try {
    await state.client.request("secrets.write", {
      id: keyName.trim(),
      value: keyValue.trim(),
      envEntry: false,
    });
    await state.client.request("skills.update", { skillKey, vaultKeyId: keyName.trim() });
    await loadSkills(state);
    await loadVaultKeys(state);
    setSkillMessage(state, skillKey, {
      kind: "success",
      message: "Created and linked vault key: " + keyName,
    });
  } catch (err) {
    setSkillMessage(state, skillKey, { kind: "error", message: getErrorMessage(err) });
  } finally {
    state.skillsBusyKey = null;
  }
}
