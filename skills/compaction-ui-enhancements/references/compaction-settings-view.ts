/**
 * Compaction Settings Tab
 *
 * Plugin-registered view for managing compaction behavior:
 * - Auto/manual toggle
 * - Dynamic threshold slider
 * - Last result before/after display
 * - Store results opt-in
 */

import { html, nothing } from "lit";

interface ModelInfo {
  id: string;
  name?: string;
  provider: string;
  contextWindow?: number;
}

export interface CompactionSettingsProps {
  client: { request: <T>(method: string, params: unknown) => Promise<T> } | null;
  connected: boolean;
}

interface CompactionSettingsState {
  loaded: boolean;
  saving: boolean;
  autoEnabled: boolean;
  autoThresholdPercent: number;
  storeLastResult: boolean;
  compactionModel: string; // "provider/model" or "" for default
  availableModels: ModelInfo[];
  showSummary: boolean;
  lastResult: {
    timestamp: number;
    trigger: string;
    tokensBefore: number;
    tokensAfter: number;
    tokensSaved: number;
    percentReduction: number;
    sessionKey?: string;
    summary?: string;
  } | null;
}

// Module-level state (persists across re-renders)
let _state: CompactionSettingsState = {
  loaded: false,
  saving: false,
  autoEnabled: true,
  autoThresholdPercent: 60,
  storeLastResult: false,
  compactionModel: "",
  availableModels: [],
  showSummary: false,
  lastResult: null,
};

let _loadPromise: Promise<void> | null = null;
let _requestUpdate: (() => void) | null = null;
let _lastLoadTime = 0;

async function loadSettings(client: CompactionSettingsProps["client"]) {
  if (!client) return;
  try {
    const [settingsRes, resultRes, modelsRes] = await Promise.all([
      client.request<{ ok: boolean; settings: CompactionSettingsState }>("compaction.getSettings", {}),
      client.request<{ ok: boolean; lastResult: CompactionSettingsState["lastResult"] }>("compaction.getLastResult", {}),
      client.request<{ models?: ModelInfo[] }>("models.list", {}).catch(() => ({ models: [] })),
    ]);
    if (settingsRes?.settings) {
      _state.autoEnabled = settingsRes.settings.autoEnabled;
      _state.autoThresholdPercent = settingsRes.settings.autoThresholdPercent;
      _state.storeLastResult = settingsRes.settings.storeLastResult;
      _state.compactionModel = settingsRes.settings.compactionModel || "";
    }
    _state.availableModels = modelsRes?.models ?? [];
    _state.lastResult = resultRes?.lastResult ?? null;
    _state.loaded = true;
    _requestUpdate?.();
  } catch {
    _state.loaded = true;
    _requestUpdate?.();
  }
}

async function saveSettings(client: CompactionSettingsProps["client"]) {
  if (!client || _state.saving) return;
  _state.saving = true;
  _requestUpdate?.();
  try {
    await client.request("compaction.saveSettings", {
      autoEnabled: _state.autoEnabled,
      autoThresholdPercent: _state.autoThresholdPercent,
      storeLastResult: _state.storeLastResult,
      compactionModel: _state.compactionModel || undefined,
    });
  } catch {
    // silent
  }
  _state.saving = false;
  _requestUpdate?.();
}

function formatTimestamp(ts: number): string {
  return new Date(ts).toLocaleString(undefined, {
    month: "short", day: "numeric",
    hour: "2-digit", minute: "2-digit",
  });
}

function formatTokens(n: number): string {
  return n >= 1000 ? `${Math.round(n / 1000)}K` : String(n);
}

export function renderCompactionSettings(
  props: CompactionSettingsProps,
  requestUpdate: () => void,
) {
  _requestUpdate = requestUpdate;

  // Reload settings on first render AND when re-entering the tab (stale > 2s)
  const now = Date.now();
  if ((!_state.loaded || now - _lastLoadTime > 2000) && !_loadPromise && props.client) {
    _lastLoadTime = now;
    _loadPromise = loadSettings(props.client).finally(() => { _loadPromise = null; });
  }

  if (!_state.loaded) {
    return html`<div class="page-body"><div class="card"><div class="card__body" style="text-align:center;padding:40px;color:var(--text-muted)">Loading settings…</div></div></div>`;
  }

  const thresholdColor =
    _state.autoThresholdPercent >= 85 ? "var(--clr-danger, #ef4444)"
      : _state.autoThresholdPercent >= 60 ? "var(--clr-warning, #f59e0b)"
        : "var(--clr-success, #22c55e)";

  const last = _state.lastResult;

  return html`
    <div class="page-body" style="max-width:680px;">
      <!-- Auto-Compaction Card -->
      <div class="card" style="margin-bottom:16px;">
        <div class="card__header">
          <div class="card__title">Auto-Compaction</div>
        </div>
        <div class="card__body">
          <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;">
            <div>
              <div style="font-weight:500;color:var(--text);">Automatic Compaction</div>
              <div style="font-size:12px;color:var(--text-muted);margin-top:2px;">
                Triggers background compaction when token usage exceeds threshold
              </div>
            </div>
            <input type="checkbox" ?checked=${_state.autoEnabled}
              style="width:18px;height:18px;cursor:pointer;accent-color:var(--clr-primary, #6366f1);"
              @change=${(e: Event) => {
                _state.autoEnabled = (e.target as HTMLInputElement).checked;
                requestUpdate();
                void saveSettings(props.client);
              }} />
          </div>

          <div style="margin-bottom:8px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
              <span style="font-size:13px;color:var(--text-muted);">Threshold</span>
              <span style="font-size:13px;font-weight:600;color:${thresholdColor};">
                ${_state.autoThresholdPercent}%
              </span>
            </div>
            <input type="range" min="10" max="95" step="5"
              .value=${String(_state.autoThresholdPercent)}
              ?disabled=${!_state.autoEnabled}
              style="width:100%;accent-color:${thresholdColor};"
              @input=${(e: Event) => {
                _state.autoThresholdPercent = Number((e.target as HTMLInputElement).value);
                requestUpdate();
              }}
              @change=${() => { void saveSettings(props.client); }}
            />
            <div style="display:flex;justify-content:space-between;font-size:11px;color:var(--text-muted);margin-top:2px;">
              <span>10%</span>
              <span>95%</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Model Selector Card -->
      <div class="card" style="margin-bottom:16px;">
        <div class="card__header">
          <div class="card__title">Model</div>
        </div>
        <div class="card__body">
          <div style="margin-bottom:12px;">
            <div style="font-weight:500;color:var(--text);margin-bottom:4px;">Compaction Model</div>
            <div style="font-size:12px;color:var(--text-muted);margin-bottom:10px;">
              Select a model for compaction, or leave as default to use the current session's model and auth hierarchy.
            </div>
            <select
              style="width:100%;padding:8px 12px;background:var(--bg-surface, #0d1117);border:1px solid var(--border, #30363d);border-radius:6px;color:var(--text, #e6edf3);font-size:14px;"
              @change=${(e: Event) => {
                _state.compactionModel = (e.target as HTMLSelectElement).value;
                requestUpdate();
                void saveSettings(props.client);
              }}
            >
              <option value="" ?selected=${!_state.compactionModel}>Default (session model)</option>
              ${(() => {
                const groups = new Map<string, ModelInfo[]>();
                for (const m of _state.availableModels) {
                  const g = groups.get(m.provider) || [];
                  g.push(m);
                  groups.set(m.provider, g);
                }
                return [...groups.entries()].map(
                  ([prov, models]) => html`
                    <optgroup label="${prov}">
                      ${models.map(
                        (m) => html`
                          <option
                            value="${m.provider}/${m.id}"
                            ?selected=${_state.compactionModel === `${m.provider}/${m.id}`}
                          >${m.name || m.id}${m.contextWindow ? ` (${Math.round(m.contextWindow / 1000)}k)` : ""}</option>
                        `,
                      )}
                    </optgroup>
                  `,
                );
              })()}
            </select>
          </div>
          ${_state.compactionModel ? html`
            <div style="padding:10px 12px;background:var(--bg-surface, #1e1e2e);border-radius:6px;border-left:3px solid var(--clr-warning, #f59e0b);font-size:12px;color:var(--text-muted);">
              ⚠️ Make sure the correct API keys are configured for <strong style="color:var(--text);">${_state.compactionModel.split("/")[0]}</strong>.
              If this model fails, compaction will automatically fall back to your session's default model.
            </div>
          ` : nothing}
        </div>
      </div>

      <!-- Storage Card -->
      <div class="card" style="margin-bottom:16px;">
        <div class="card__header">
          <div class="card__title">Result Storage</div>
        </div>
        <div class="card__body">
          <div style="display:flex;align-items:center;justify-content:space-between;">
            <div>
              <div style="font-weight:500;color:var(--text);">Store Compaction Results</div>
              <div style="font-size:12px;color:var(--text-muted);margin-top:2px;">
                Save the summary text from the most recent compaction for review
              </div>
            </div>
            <input type="checkbox" ?checked=${_state.storeLastResult}
              style="width:18px;height:18px;cursor:pointer;accent-color:var(--clr-primary, #6366f1);"
              @change=${(e: Event) => {
                _state.storeLastResult = (e.target as HTMLInputElement).checked;
                requestUpdate();
                void saveSettings(props.client);
              }} />
          </div>
        </div>
      </div>

      <!-- Last Result Card -->
      <div class="card">
        <div class="card__header">
          <div class="card__title">Last Compaction</div>
          ${last ? html`
            <div style="display:flex;gap:6px;">
              <button class="btn btn--sm" style="background:${last.summary ? "var(--clr-primary, #6366f1)" : "var(--bg-surface, #333)"};color:${last.summary ? "#fff" : "var(--text-muted)"};border:none;padding:4px 12px;border-radius:4px;cursor:${last.summary ? "pointer" : "not-allowed"};font-size:12px;opacity:${last.summary ? "1" : "0.6"};" @click=${() => {
                if (!last.summary) return;
                _state.showSummary = !_state.showSummary;
                requestUpdate();
              }}>${_state.showSummary ? "Hide" : "View Results"}</button>
              <button class="btn btn--sm" @click=${async () => {
                await props.client?.request("compaction.clearLastResult", {});
                _state.lastResult = null;
                _state.showSummary = false;
                requestUpdate();
              }}>Clear</button>
            </div>
          ` : nothing}
        </div>
        <div class="card__body">
          ${last ? html`
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:16px;">
              <div style="background:var(--bg-surface, #1e1e2e);border-radius:8px;padding:14px;text-align:center;">
                <div style="font-size:11px;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">Before</div>
                <div style="font-size:22px;font-weight:700;color:var(--clr-warning, #f59e0b);">${formatTokens(last.tokensBefore)}</div>
              </div>
              <div style="background:var(--bg-surface, #1e1e2e);border-radius:8px;padding:14px;text-align:center;">
                <div style="font-size:11px;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.5px;margin-bottom:4px;">After</div>
                <div style="font-size:22px;font-weight:700;color:var(--clr-success, #22c55e);">${formatTokens(last.tokensAfter)}</div>
              </div>
            </div>
            <div style="display:flex;justify-content:space-between;font-size:12px;color:var(--text-muted);margin-bottom:8px;">
              <span>Saved: <strong style="color:var(--text);">${formatTokens(last.tokensSaved)}</strong> (${last.percentReduction}%)</span>
              <span>Trigger: <strong style="color:var(--text);">${last.trigger}</strong></span>
            </div>
            <div style="font-size:12px;color:var(--text-muted);">
              ${formatTimestamp(last.timestamp)}${last.sessionKey ? html` · <code style="font-size:11px;">${last.sessionKey.length > 40 ? last.sessionKey.slice(0, 40) + "…" : last.sessionKey}</code>` : nothing}
            </div>
            ${!last.summary ? html`
              <div style="margin-top:12px;padding:10px;font-size:12px;color:var(--text-muted);background:var(--bg-surface, #1e1e2e);border-radius:6px;text-align:center;">
                Enable "Store Compaction Results" above to save summary text for review
              </div>
            ` : nothing}
            ${_state.showSummary && last.summary ? html`
              <div style="margin-top:16px;border:1px solid var(--border, #30363d);border-radius:8px;overflow:hidden;">
                <div style="padding:10px 14px;background:var(--bg-surface, #1e1e2e);border-bottom:1px solid var(--border, #30363d);display:flex;justify-content:space-between;align-items:center;">
                  <span style="font-size:13px;font-weight:600;color:var(--text);">📋 Compaction Summary</span>
                  <button style="background:none;border:none;color:var(--text-muted);cursor:pointer;font-size:18px;padding:0 4px;line-height:1;" @click=${() => {
                    _state.showSummary = false;
                    requestUpdate();
                  }}>✕</button>
                </div>
                <div style="padding:16px;max-height:500px;overflow-y:auto;">
                  <pre style="margin:0;font-size:12px;line-height:1.6;white-space:pre-wrap;word-break:break-word;color:var(--text);font-family:inherit;">${last.summary}</pre>
                </div>
              </div>
            ` : nothing}
          ` : html`
            <div style="text-align:center;padding:24px;color:var(--text-muted);font-size:13px;">
              No compaction has been run yet
            </div>
          `}
        </div>
      </div>

      <!-- Auth Info -->
      <div style="margin-top:16px;padding:12px;font-size:12px;color:var(--text-muted);border-left:3px solid var(--border, #333);">
        Compaction uses the same auth hierarchy as chat: <strong>OAuth → API Key → Fallback</strong>.
        ${_state.compactionModel
          ? html`Custom model will use this auth chain independently. Fallback uses the session default.`
          : html`No separate configuration needed.`}
      </div>
    </div>
  `;
}

/** Reset module state (for tests or tab switches). */
export function resetCompactionSettingsState() {
  _state = {
    loaded: false, saving: false,
    autoEnabled: true, autoThresholdPercent: 60, storeLastResult: false,
    compactionModel: "", availableModels: [], showSummary: false, lastResult: null,
  };
  _loadPromise = null;
  _requestUpdate = null;
  _lastLoadTime = 0;
}
