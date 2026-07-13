import { html, nothing } from "lit";
import type { SkillMessageMap, VaultKeyEntry } from "../controllers/skills.ts";
import { clampText } from "../format.ts";
import type { SkillStatusEntry, SkillStatusReport } from "../types.ts";
import { groupSkills } from "./skills-grouping.ts";
import {
  computeSkillMissing,
  computeSkillReasons,
  renderSkillStatusChips,
} from "./skills-shared.ts";

export type SkillsProps = {
  loading: boolean;
  report: SkillStatusReport | null;
  error: string | null;
  filter: string;
  edits: Record<string, string>;
  busyKey: string | null;
  messages: SkillMessageMap;
  vaultKeys: VaultKeyEntry[];
  skillAddingKey: Record<string, boolean>;
  skillNewKeyName: Record<string, string>;
  skillNewKeyValue: Record<string, string>;
  onFilterChange: (next: string) => void;
  onRefresh: () => void;
  onToggle: (skillKey: string, enabled: boolean) => void;
  onEdit: (skillKey: string, value: string) => void;
  onSaveKey: (skillKey: string) => void;
  onInstall: (skillKey: string, name: string, installId: string) => void;
  onLinkVaultKey: (skillKey: string, vaultKeyId: string) => void;
  onToggleAddKey: (skillKey: string) => void;
  onNewKeyNameChange: (skillKey: string, name: string) => void;
  onNewKeyValueChange: (skillKey: string, value: string) => void;
  onAddKeyAndLink: (skillKey: string) => void;
};

export function renderSkills(props: SkillsProps) {
  const skills = props.report?.skills ?? [];
  const filter = props.filter.trim().toLowerCase();
  const filtered = filter
    ? skills.filter((skill) =>
        [skill.name, skill.description, skill.source].join(" ").toLowerCase().includes(filter),
      )
    : skills;
  const groups = groupSkills(filtered);

  return html`
    <section class="card">
      <div class="row" style="justify-content: space-between;">
        <div>
          <div class="card-title">Skills</div>
          <div class="card-sub">Bundled, managed, and workspace skills.</div>
        </div>
        <button class="btn" ?disabled=${props.loading} @click=${props.onRefresh}>
          ${props.loading ? "Loading…" : "Refresh"}
        </button>
      </div>

      <div class="filters" style="margin-top: 14px;">
        <label class="field" style="flex: 1;">
          <span>Filter</span>
          <input
            .value=${props.filter}
            @input=${(e: Event) => props.onFilterChange((e.target as HTMLInputElement).value)}
            placeholder="Search skills"
          />
        </label>
        <div class="muted">${filtered.length} shown</div>
      </div>

      ${
        props.error
          ? html`<div class="callout danger" style="margin-top: 12px;">${props.error}</div>`
          : nothing
      }

      ${
        filtered.length === 0
          ? html`
              <div class="muted" style="margin-top: 16px">No skills found.</div>
            `
          : html`
            <div class="agent-skills-groups" style="margin-top: 16px;">
              ${groups.map((group) => {
                const collapsedByDefault = false;
                return html`
                  <details class="agent-skills-group" ?open=${!collapsedByDefault}>
                    <summary class="agent-skills-header">
                      <span>${group.label}</span>
                      <span class="muted">${group.skills.length}</span>
                    </summary>
                    <div class="list skills-grid">
                      ${group.skills.map((skill) => renderSkill(skill, props))}
                    </div>
                  </details>
                `;
              })}
            </div>
          `
      }
    </section>
  `;
}

function renderSkill(skill: SkillStatusEntry, props: SkillsProps) {
  const busy = props.busyKey === skill.skillKey;
  const apiKey = props.edits[skill.skillKey] ?? "";
  const message = props.messages[skill.skillKey] ?? null;
  const canInstall = skill.install.length > 0 && skill.missing.bins.length > 0;
  const showBundledBadge = Boolean(skill.bundled && skill.source !== "openclaw-bundled");
  const missing = computeSkillMissing(skill);
  const reasons = computeSkillReasons(skill);
  return html`
    <div class="list-item">
      <div class="list-main">
        <div class="list-title">
          ${skill.emoji ? `${skill.emoji} ` : ""}${skill.name}
        </div>
        <div class="list-sub">${clampText(skill.description, 140)}</div>
        ${renderSkillStatusChips({ skill, showBundledBadge })}
        ${
          missing.length > 0
            ? html`
              <div class="muted" style="margin-top: 6px;">
                Missing: ${missing.join(", ")}
              </div>
            `
            : nothing
        }
        ${
          reasons.length > 0
            ? html`
              <div class="muted" style="margin-top: 6px;">
                Reason: ${reasons.join(", ")}
              </div>
            `
            : nothing
        }
      </div>
      <div class="list-meta">
        <div class="row" style="justify-content: flex-end; flex-wrap: wrap;">
          <button
            class="btn"
            ?disabled=${busy}
            @click=${() => props.onToggle(skill.skillKey, skill.disabled)}
          >
            ${skill.disabled ? "Enable" : "Disable"}
          </button>
          ${
            canInstall
              ? html`<button
                class="btn"
                ?disabled=${busy}
                @click=${() => props.onInstall(skill.skillKey, skill.name, skill.install[0].id)}
              >
                ${busy ? "Installing…" : skill.install[0].label}
              </button>`
              : nothing
          }
        </div>
        ${
          message
            ? html`<div
              class="muted"
              style="margin-top: 8px; color: ${
                message.kind === "error"
                  ? "var(--danger-color, #d14343)"
                  : "var(--success-color, #0a7f5a)"
              };"
            >
              ${message.message}
            </div>`
            : nothing
        }
        ${
          skill.primaryEnv
            ? renderVaultKeySelector(skill, props)
            : nothing
        }
      </div>
    </div>
  `;
}

function renderVaultKeySelector(skill: SkillStatusEntry, props: SkillsProps) {
  const busy = props.busyKey === skill.skillKey;
  const isLinked = Boolean(skill.vaultKeyId);
  const adding = props.skillAddingKey[skill.skillKey] ?? false;
  const newName = props.skillNewKeyName[skill.skillKey] ?? "";
  const newValue = props.skillNewKeyValue[skill.skillKey] ?? "";

  if (isLinked) {
    // Show current vault link
    return html`
      <div style="margin-top:10px;display:flex;align-items:center;gap:8px;">
        <span style="font-size:12px;color:var(--text-muted);">🔒</span>
        <span style="font-size:13px;font-family:monospace;color:var(--text);">${skill.vaultKeyId}</span>
        <button class="btn" style="font-size:11px;padding:2px 8px;" ?disabled=${busy}
          @click=${() => props.onLinkVaultKey(skill.skillKey, "")}
          title="Unlink vault key">Unlink</button>
      </div>
    `;
  }

  // Show dropdown selector
  return html`
    <div style="margin-top:10px;">
      <div style="display:flex;align-items:center;gap:8px;">
        <select
          style="flex:1;padding:5px 8px;background:var(--bg-surface,#0d1117);border:1px solid var(--border,#30363d);border-radius:6px;color:var(--text);font-size:13px;"
          ?disabled=${busy}
          @change=${(e: Event) => {
            const val = (e.target as HTMLSelectElement).value;
            if (val === "__add__") {
              props.onToggleAddKey(skill.skillKey);
              (e.target as HTMLSelectElement).value = "";
            } else if (val) {
              props.onLinkVaultKey(skill.skillKey, val);
            }
          }}
        >
          <option value="">Select vault key for ${skill.primaryEnv}…</option>
          ${props.vaultKeys.map((k) => html`
            <option value=${k.id}>🔒 ${k.id}</option>
          `)}
          <option disabled>──────────</option>
          <option value="__add__">＋ Add new vault key…</option>
        </select>
      </div>
      ${adding ? html`
        <div style="margin-top:8px;padding:10px;background:var(--bg-surface,#0d1117);border:1px solid var(--border,#30363d);border-radius:6px;">
          <div style="display:flex;gap:6px;align-items:center;flex-wrap:wrap;">
            <input type="text" placeholder="KEY_NAME"
              style="width:160px;padding:5px 8px;background:var(--bg-surface,#0d1117);border:1px solid var(--border,#30363d);border-radius:4px;color:var(--text);font-size:12px;font-family:monospace;"
              .value=${newName}
              @input=${(e: Event) => props.onNewKeyNameChange(skill.skillKey, (e.target as HTMLInputElement).value)}
            />
            <input type="password" placeholder="Secret value"
              style="flex:1;min-width:120px;padding:5px 8px;background:var(--bg-surface,#0d1117);border:1px solid var(--border,#30363d);border-radius:4px;color:var(--text);font-size:12px;"
              .value=${newValue}
              @input=${(e: Event) => props.onNewKeyValueChange(skill.skillKey, (e.target as HTMLInputElement).value)}
            />
            <button class="btn primary" style="font-size:11px;padding:4px 10px;"
              ?disabled=${busy || !newName.trim() || !newValue.trim()}
              @click=${() => props.onAddKeyAndLink(skill.skillKey)}>Save & Link</button>
            <button class="btn" style="font-size:11px;padding:4px 10px;"
              @click=${() => props.onToggleAddKey(skill.skillKey)}>Cancel</button>
          </div>
        </div>
      ` : nothing}
    </div>
  `;
}
