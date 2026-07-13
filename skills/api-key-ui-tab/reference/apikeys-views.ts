import { html, nothing } from "lit";
import type { DiscoveredKey, VaultStatus, AuthProfile } from "../controllers/apikeys.js";

export type ApiKeysProps = {
  error: string | null;
  keys: DiscoveredKey[];
  edits: Record<string, string>;
  editing: Record<string, boolean>;
  busyKey: string | null;
  message: { kind: "success" | "error"; text: string } | null;
  loading?: boolean;
  vaultStatus?: VaultStatus | null;
  migrating?: boolean;
  authProfiles?: AuthProfile[];
  authProfilesLoading?: boolean;
  onEdit: (keyId: string, value: string) => void;
  onSave: (keyId: string) => void;
  onClear: (keyId: string) => void;
  onRefresh?: () => void;
  onMigrate?: () => void;
  onResetProfileErrors?: (profileId: string) => void;
  onDeleteProfile?: (profileId: string) => void;
  onToggleEdit?: (keyId: string) => void;
  onRefreshSecret?: (keyId: string) => void;
  showAddForm?: boolean;
  addName?: string;
  addValue?: string;
  addBusy?: boolean;
  onToggleAddForm?: () => void;
  onAddNameChange?: (name: string) => void;
  onAddValueChange?: (value: string) => void;
  onAddSecret?: () => void;
  restartNeeded?: boolean;
  onRestart?: () => void;
  vaultAllKeys?: { id: string; masked: string }[];
};

export function renderApiKeys(props: ApiKeysProps) {
  const envKeys = props.keys.filter((k) => k.path[0] === "env");
  const skillKeys = props.keys.filter((k) => k.path[0] === "skills");
  const otherKeys = props.keys.filter((k) => k.path[0] !== "env" && k.path[0] !== "skills");

  const plaintextCount = props.keys.filter((k) => k.configured && !k.inVault).length;

  return html`
    <div class="page-body" style="max-width:780px;">

      <!-- Info note at top -->
      <div style="margin-bottom:16px;padding:10px 14px;font-size:12px;color:var(--text-muted);background:var(--bg-surface,#0d1117);border:1px solid var(--border,#30363d);border-radius:8px;">
        🔒 Encrypted keys are stored in <code>~/.openclaw/secrets.json</code> (mode 0600).
        Config references point to the vault — the AI agent <strong>never sees your keys</strong>.
      </div>

      <!-- Header Card -->
      <section class="card" style="margin-bottom:16px;">
        <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;">
          <div style="flex:1;min-width:200px;">
            <div class="card-title">🔒 Vault</div>
          </div>
          <div style="display:flex;gap:8px;">
            ${plaintextCount > 0 && props.onMigrate ? html`
              <button class="btn" ?disabled=${props.migrating} @click=${props.onMigrate}
                style="background:var(--clr-warning,#f59e0b);color:#000;border:none;font-weight:600;">
                ${props.migrating ? "Migrating…" : "🔒 Migrate to Vault"}
              </button>
            ` : nothing}
            <button class="btn" @click=${() => props.onToggleAddForm?.()} title="Add a new secret to the vault">＋ Add Secret</button>
            <button class="btn" @click=${() => props.onRefresh?.()} title="Refresh">↻</button>
          </div>
        </div>

        ${props.error ? html`<div class="callout danger" style="margin-top:12px;">${props.error}</div>` : nothing}
        ${props.message ? html`<div class="callout ${props.message.kind === "error" ? "danger" : "success"}" style="margin-top:12px;">${props.message.text}</div>` : nothing}

        ${props.restartNeeded ? html`
          <div style="margin-top:12px;padding:10px 14px;background:#f59e0b18;border:1px solid var(--clr-warning,#f59e0b);border-radius:8px;display:flex;align-items:center;justify-content:space-between;gap:10px;">
            <span style="font-size:13px;color:var(--clr-warning,#f59e0b);">⚠ New secrets require a gateway restart to take effect.</span>
            <button class="btn" style="font-size:12px;padding:4px 12px;background:var(--clr-warning,#f59e0b);color:#000;border:none;font-weight:600;"
              @click=${() => props.onRestart?.()}>Restart Now</button>
          </div>
        ` : nothing}

        ${props.showAddForm ? html`
          <div style="margin-top:14px;padding:14px;background:var(--bg-surface,#0d1117);border:1px solid var(--border,#30363d);border-radius:8px;">
            <div style="font-weight:600;font-size:13px;margin-bottom:10px;">Add New Secret</div>
            <div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap;">
              <input
                type="text"
                style="width:200px;padding:6px 10px;background:var(--bg-surface,#0d1117);border:1px solid var(--border,#30363d);border-radius:6px;color:var(--text);font-size:13px;font-family:monospace;"
                .value=${props.addName ?? ""}
                placeholder="KEY_NAME"
                @input=${(e: Event) => props.onAddNameChange?.((e.target as HTMLInputElement).value)}
              />
              <input
                type="password"
                style="flex:1;min-width:200px;padding:6px 10px;background:var(--bg-surface,#0d1117);border:1px solid var(--border,#30363d);border-radius:6px;color:var(--text);font-size:13px;"
                .value=${props.addValue ?? ""}
                placeholder="Secret value"
                @input=${(e: Event) => props.onAddValueChange?.((e.target as HTMLInputElement).value)}
              />
              <button class="btn primary" style="font-size:12px;padding:6px 14px;"
                ?disabled=${props.addBusy || !(props.addName?.trim()) || !(props.addValue?.trim())}
                @click=${() => props.onAddSecret?.()}>
                ${props.addBusy ? "Saving…" : "Save"}
              </button>
              <button class="btn" style="font-size:12px;padding:6px 10px;"
                @click=${() => props.onToggleAddForm?.()}>Cancel</button>
            </div>
            <div style="font-size:11px;color:var(--text-muted);margin-top:6px;">
              Use UPPER_SNAKE_CASE for the name. The secret will be stored encrypted in the vault and can be referenced by skills.
            </div>
          </div>
        ` : nothing}
      </section>

      <!-- Auth Profiles -->
      ${renderAuthProfiles(props)}

      ${props.loading
        ? html`<div class="card"><div class="card__body" style="padding:24px;text-align:center;opacity:0.6;">Scanning for API keys...</div></div>`
        : html`
          ${renderKeySection("Environment Keys", envKeys, props)}
          ${renderKeySection("Skill Keys", skillKeys, props)}
          ${renderKeySection("Other Keys", otherKeys, props)}
          ${renderVaultOnlyKeys(props)}
        `}
    </div>
  `;
}

function renderKeySection(title: string, keys: DiscoveredKey[], props: ApiKeysProps) {
  if (keys.length === 0) return nothing;
  return html`
    <section class="card" style="margin-bottom:16px;">
      <div class="card__header"><div class="card__title">${title}</div></div>
      <div class="card__body" style="padding:0;">
        ${keys.map((key) => renderKeyRow(key, props))}
      </div>
    </section>
  `;
}

function renderVaultOnlyKeys(props: ApiKeysProps) {
  const allVault = props.vaultAllKeys ?? [];
  if (allVault.length === 0) return nothing;

  // Find keys in vault that aren't shown in the discovered keys list
  const discoveredIds = new Set<string>();
  for (const k of props.keys) {
    // env keys: the vault id is the env key name
    if (k.path[0] === "env") discoveredIds.add(k.path[1]);
    // other keys use their pathStr
    discoveredIds.add(k.pathStr);
    // Also add the id from the name (covers various naming patterns)
    discoveredIds.add(k.name);
  }
  // Also match by vault key name patterns
  const vaultOnly = allVault.filter((vk) => {
    // Check if any discovered key references this vault key
    const found = props.keys.some((k) => {
      if (k.path[0] === "env" && k.path[1] === vk.id) return true;
      if (k.id === vk.id || k.pathStr === vk.id) return true;
      // Check for SKILL_ prefix pattern
      if (k.inVault && k.name === vk.id) return true;
      return false;
    });
    return !found;
  });

  if (vaultOnly.length === 0) return nothing;

  return html`
    <section class="card" style="margin-bottom:16px;">
      <div class="card__header">
        <div class="card__title">Vault-Only Keys</div>
      </div>
      <div class="card__body" style="padding:0;">
        ${vaultOnly.map((vk) => html`
          <div style="padding:12px 16px;border-bottom:1px solid var(--border,#30363d);display:flex;align-items:center;gap:10px;">
            <div style="width:20px;flex-shrink:0;text-align:center;">
              <span style="cursor:help;" title="Encrypted — stored in secrets.json vault">🔒</span>
            </div>
            <div style="flex:1;min-width:0;">
              <div style="font-weight:600;color:var(--text);font-size:14px;font-family:monospace;">${vk.id}</div>
              <div style="font-size:11px;color:var(--text-muted);margin-top:2px;font-family:monospace;opacity:0.6;">${vk.masked}</div>
            </div>
            <button class="btn" style="font-size:12px;padding:4px 10px;color:var(--clr-danger,#ef4444);"
              @click=${() => { if (confirm("Delete vault key " + vk.id + "?")) props.onClear(vk.id); }}
              title="Delete from vault">✕</button>
          </div>
        `)}
      </div>
    </section>
  `;
}

function renderAuthProfiles(props: ApiKeysProps) {
  const profiles = props.authProfiles ?? [];
  if (props.authProfilesLoading && profiles.length === 0) {
    return html`<section class="card" style="margin-bottom:16px;">
      <div class="card__body" style="padding:24px;text-align:center;opacity:0.6;">Loading auth profiles...</div>
    </section>`;
  }
  if (profiles.length === 0) return nothing;

  return html`
    <section class="card" style="margin-bottom:16px;">
      <div class="card__header"><div class="card__title">Auth Profiles</div></div>
      <div class="card__body" style="padding:0;">
        ${profiles.map((p) => renderAuthProfileRow(p, props))}
      </div>
    </section>
  `;
}

function renderAuthProfileRow(p: AuthProfile, props: ApiKeysProps) {
  const typeLabel: Record<string, string> = { api_key: "API Key", token: "Token", oauth: "OAuth" };
  const lastUsedStr = p.lastUsed && p.lastUsed > 0 ? timeAgo(p.lastUsed) : "never";
  const isOAuth = p.type === "oauth";

  return html`
    <div style="padding:12px 16px;border-bottom:1px solid var(--border,#30363d);display:flex;align-items:flex-start;gap:10px;">
      <!-- Lock column -->
      <div style="width:20px;flex-shrink:0;padding-top:2px;text-align:center;">
        ${storageIcon(p.inVault, p.hasCredential)}
      </div>
      <!-- Info column -->
      <div style="flex:1;min-width:0;">
        <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap;">
          <span style="font-weight:600;color:var(--text);font-size:14px;">${p.provider}</span>
          <span style="font-size:11px;padding:1px 6px;background:var(--bg-surface,#0d1117);border:1px solid var(--border,#30363d);border-radius:4px;color:var(--text-muted);">${typeLabel[p.type] ?? p.type}</span>
        </div>
        <div style="font-size:12px;color:var(--text-muted);margin-top:3px;">
          <span style="font-family:monospace;opacity:0.7;">${p.id}</span>
          ${p.email ? html` · ${p.email}` : nothing}
          · last used ${lastUsedStr}
          ${p.errorCount > 0 ? html` · <span style="color:var(--clr-danger,#ef4444);">${p.errorCount} error${p.errorCount === 1 ? "" : "s"}</span>` : nothing}
        </div>
      </div>
      <!-- Actions column -->
      <div style="display:flex;gap:6px;flex-shrink:0;align-items:center;min-width:80px;justify-content:flex-end;">
        ${isOAuth ? html`
          <button class="btn" style="font-size:12px;padding:4px 10px;"
            @click=${() => props.onRefreshSecret?.(p.id)}
            title="Refresh OAuth token">↻</button>
        ` : nothing}
        ${p.status === "error" || p.status === "cooldown"
          ? html`<button class="btn" style="font-size:12px;padding:4px 10px;"
              @click=${() => props.onResetProfileErrors?.(p.id)}
              title="Reset error count and cooldown">⟲ Reset</button>`
          : nothing}
        <button class="btn" style="font-size:12px;padding:4px 10px;color:var(--clr-danger,#ef4444);"
          @click=${() => { if (confirm("Remove auth profile " + p.id + "?")) props.onDeleteProfile?.(p.id); }}
          title="Delete this auth profile">✕</button>
      </div>
    </div>
  `;
}

function storageIcon(inVault: boolean, hasCredential: boolean) {
  if (inVault) {
    return html`<span style="cursor:help;" title="Encrypted — stored in secrets.json vault">🔒</span>`;
  }
  if (hasCredential) {
    return html`<span style="cursor:help;" title="Plaintext — stored as plain text in config. Use Migrate to encrypt.">⚠️</span>`;
  }
  return html`<span style="cursor:help;opacity:0.5;" title="Not configured">—</span>`;
}

function timeAgo(ts: number): string {
  const diff = Date.now() - ts;
  if (diff < 60_000) return "just now";
  if (diff < 3_600_000) return Math.floor(diff / 60_000) + "m ago";
  if (diff < 86_400_000) return Math.floor(diff / 3_600_000) + "h ago";
  return Math.floor(diff / 86_400_000) + "d ago";
}

function renderKeyRow(key: DiscoveredKey, props: ApiKeysProps) {
  const busy = props.busyKey === key.id;
  const isEditing = props.editing[key.id] ?? false;
  const editValue = props.edits[key.id] ?? "";
  const hasEdit = editValue.length > 0;

  return html`
    <div style="padding:12px 16px;border-bottom:1px solid var(--border,#30363d);">
      <div style="display:flex;align-items:flex-start;gap:10px;">
        <!-- Lock column -->
        <div style="width:20px;flex-shrink:0;padding-top:2px;text-align:center;">
          ${storageIcon(key.inVault, key.configured)}
        </div>
        <!-- Info column -->
        <div style="flex:1;min-width:0;">
          <div style="font-weight:600;color:var(--text);font-size:14px;">${key.name}</div>
          <div style="font-size:12px;color:var(--text-muted);margin-top:2px;">${key.description}</div>
          ${key.configured ? html`
            <div style="display:flex;align-items:center;gap:6px;margin-top:4px;">
              <span style="font-size:11px;color:var(--text-muted);font-family:monospace;opacity:0.6;letter-spacing:2px;">••••••••••••</span>
              <button class="btn" style="font-size:11px;padding:2px 8px;"
                @click=${() => props.onToggleEdit?.(key.id)}
                title="${isEditing ? "Cancel editing" : "Edit this key"}"
              >${isEditing ? "Cancel" : "✎"}</button>
            </div>
          ` : html`
            <div style="margin-top:4px;">
              <button class="btn" style="font-size:11px;padding:2px 8px;"
                @click=${() => props.onToggleEdit?.(key.id)}
              >${isEditing ? "Cancel" : "＋ Set key"}</button>
            </div>
          `}
        </div>
        <!-- Actions column -->
        <div style="display:flex;gap:6px;flex-shrink:0;align-items:center;min-width:80px;justify-content:flex-end;">
          ${key.docsUrl ? html`
            <a class="btn" href=${key.docsUrl} target="_blank" rel="noopener noreferrer"
              style="font-size:12px;padding:4px 10px;white-space:nowrap;">Get key ↗</a>
          ` : nothing}
        </div>
      </div>

      ${isEditing ? html`
        <div style="display:flex;gap:8px;align-items:center;margin-top:10px;margin-left:30px;">
          <input
            type="password"
            style="flex:1;min-width:0;padding:6px 10px;background:var(--bg-surface,#0d1117);border:1px solid var(--border,#30363d);border-radius:6px;color:var(--text);font-size:13px;"
            .value=${editValue}
            placeholder=${key.configured ? "Enter new key to update..." : "Enter API key..."}
            @input=${(e: Event) => props.onEdit(key.id, (e.target as HTMLInputElement).value)}
          />
          <button class="btn primary" ?disabled=${busy || !hasEdit} @click=${() => props.onSave(key.id)}
            style="font-size:12px;padding:6px 14px;">${busy ? "…" : "Save"}</button>
          ${key.configured ? html`
            <button class="btn" ?disabled=${busy} @click=${() => props.onClear(key.id)}
              style="font-size:12px;padding:6px 10px;color:var(--clr-danger,#ef4444);" title="Remove this key">✕</button>
          ` : nothing}
        </div>
      ` : nothing}
    </div>
  `;
}
