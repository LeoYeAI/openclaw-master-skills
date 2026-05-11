import { html, nothing } from "lit";

export type MemoryHealthStatus = {
  surrealdb_binary: {
    installed: boolean;
    path: string | null;
    version: string | null;
  };
  surrealdb_server: {
    running: boolean;
    port: number;
    error?: string;
  };
  schema: {
    initialized: boolean;
    error?: string;
  };
  python_deps: {
    ok: boolean;
    dependencies: Record<string, boolean>;
  };
  data_dir: {
    path: string;
    exists: boolean;
  };
};

export type MemoryStats = {
  facts: number;
  entities: number;
  relationships: number;
  archived: number;
  avg_confidence: number;
  by_source: Array<{ source: string; count: number }>;
  error?: string;
};

export type ExtractionProgress = {
  running: boolean;
  phase?: string;
  current?: number;
  total?: number;
  percent?: number;
  message?: string;
  detail?: string;
};

export type MemoryProps = {
  loading: boolean;
  health: MemoryHealthStatus | null;
  stats: MemoryStats | null;
  error: string | null;
  maintenanceLog: string | null;
  installLog: string | null;
  extractionLog: string | null;
  extractionProgress: ExtractionProgress | null;
  busyAction: string | null;
  onRefresh: () => void;
  onAutoRepair: () => void;
  onInstallBinary: () => void;
  onInstallPython: () => void;
  onStartServer: () => void;
  onInitSchema: () => void;
  onRunMaintenance: (op: "decay" | "prune" | "full") => void;
  onRunExtraction: (op: "extract" | "relations" | "full") => void;
};

function isExtractionRunning(props: MemoryProps): boolean {
  return props.extractionProgress?.running || 
         props.busyAction === "extract" || 
         props.busyAction === "relations" || 
         props.busyAction === "full-extract";
}

function getExtractionLabel(busyAction: string | null): string {
  switch (busyAction) {
    case "extract": return "Extracting facts...";
    case "relations": return "Discovering relationships...";
    case "full-extract": return "Running full sync...";
    default: return "Processing...";
  }
}

export function renderMemory(props: MemoryProps) {
  const isHealthy = props.health?.surrealdb_server?.running && 
                    props.health?.schema?.initialized && 
                    props.health?.python_deps?.ok;

  return html`
    <style>
      .memory-page {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        max-width: 1400px;
      }
      @media (max-width: 1000px) {
        .memory-page { grid-template-columns: 1fr; }
      }
      .memory-column {
        display: flex;
        flex-direction: column;
        gap: 16px;
      }
      .memory-header {
        grid-column: 1 / -1;
      }
      .stat-grid {
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
      }
      .stat-box {
        background: var(--bg-tertiary, #161b22);
        border-radius: 8px;
        padding: 16px 12px;
        text-align: center;
      }
      .stat-value {
        font-size: 32px;
        font-weight: 700;
        line-height: 1.2;
      }
      .stat-label {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        color: var(--text-muted);
        margin-top: 4px;
      }
      .health-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 10px 0;
        border-bottom: 1px solid var(--border-color, #30363d);
      }
      .health-row:last-child { border-bottom: none; }
      .health-label { font-weight: 500; }
      .health-detail {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 12px;
        color: var(--text-muted);
      }
      .health-badge {
        width: 20px;
        height: 20px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 11px;
        font-weight: 600;
      }
      .health-badge.ok { background: var(--success-color, #238636); color: white; }
      .health-badge.warn { background: var(--warning-color, #9e6a03); color: white; }
      .tool-section {
        padding: 16px 0;
        border-bottom: 1px solid var(--border-color, #30363d);
      }
      .tool-section:last-child { border-bottom: none; }
      .tool-title {
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 6px;
      }
      .tool-desc {
        font-size: 12px;
        color: var(--text-muted);
        margin-bottom: 12px;
      }
      .tool-buttons {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
      }
      .confidence-bar {
        margin-top: 16px;
        background: var(--bg-tertiary, #161b22);
        border-radius: 8px;
        padding: 14px 16px;
      }
      .confidence-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 10px;
      }
      .confidence-label { font-size: 13px; color: var(--text-muted); }
      .confidence-value { font-size: 24px; font-weight: 700; }
      .confidence-track {
        height: 6px;
        background: var(--border-color, #30363d);
        border-radius: 3px;
        overflow: hidden;
      }
      .confidence-fill {
        height: 100%;
        border-radius: 3px;
        transition: width 0.3s ease;
      }
      .log-output {
        background: var(--bg-tertiary, #0d1117);
        padding: 12px;
        border-radius: 6px;
        font-size: 11px;
        font-family: monospace;
        overflow-x: auto;
        max-height: 120px;
        overflow-y: auto;
        margin-top: 12px;
        white-space: pre-wrap;
        word-break: break-word;
      }
      .section-collapsed .tool-section { display: none; }
      .section-collapsed .collapse-toggle::after { content: "▸ Show"; }
      .collapse-toggle {
        font-size: 11px;
        color: var(--text-muted);
        cursor: pointer;
        padding: 4px 8px;
        border-radius: 4px;
        background: var(--bg-tertiary);
      }
      .collapse-toggle:hover { background: var(--border-color); }
      .sources-list {
        margin-top: 12px;
        font-size: 12px;
      }
      .source-row {
        display: flex;
        justify-content: space-between;
        padding: 4px 0;
        color: var(--text-muted);
      }
      @keyframes progress-pulse {
        0%, 100% { opacity: 1; width: 5%; }
        50% { opacity: 0.7; width: 25%; }
      }
    </style>

    <div class="memory-page">
      <!-- Header -->
      <section class="card memory-header">
        <div class="row" style="justify-content: space-between; align-items: center;">
          <div>
            <div class="card-title" style="display: flex; align-items: center; gap: 8px;">
              🧠 Knowledge Graph Memory
              ${isHealthy 
                ? html`<span class="chip chip-ok" style="font-size: 11px;">Online</span>`
                : html`<span class="chip chip-warn" style="font-size: 11px;">Setup Required</span>`
              }
            </div>
            <div class="card-sub">SurrealDB-powered semantic memory with confidence scoring and graph relationships.</div>
          </div>
          <div class="row" style="gap: 8px;">
            <button class="btn" ?disabled=${props.loading || props.busyAction !== null} @click=${props.onRefresh}>
              ${props.loading ? "Loading…" : "↻ Refresh"}
            </button>
            ${!isHealthy ? html`
              <button class="btn primary" ?disabled=${props.busyAction !== null} @click=${props.onAutoRepair}>
                ${props.busyAction === "repair" ? "Repairing…" : "🔧 Auto-Repair"}
              </button>
            ` : nothing}
          </div>
        </div>
        ${props.error ? html`<div class="callout danger" style="margin-top: 12px;">${props.error}</div>` : nothing}
      </section>

      <!-- Left Column: Dashboard -->
      <div class="memory-column">
        ${renderDashboard(props)}
      </div>

      <!-- Right Column: Operations -->
      <div class="memory-column">
        ${renderOperations(props)}
      </div>
    </div>
  `;
}

function renderDashboard(props: MemoryProps) {
  const stats = props.stats;
  const health = props.health;
  const isActive = health?.surrealdb_server?.running ?? false;
  const hasData = stats && !stats.error;
  const displayStats = hasData ? stats : { facts: 0, entities: 0, relationships: 0, archived: 0, avg_confidence: 0, by_source: [] };

  return html`
    <section class="card">
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
        <div class="card-title">📊 Dashboard</div>
        ${isActive
          ? html`<a href="http://localhost:8000" target="_blank" class="btn small" title="Open SurrealDB Studio">🔗 DB Studio</a>`
          : nothing
        }
      </div>

      <!-- Stats Grid -->
      <div class="stat-grid">
        <div class="stat-box">
          <div class="stat-value" style="color: ${isActive ? 'var(--primary-color, #58a6ff)' : 'var(--text-muted)'};">
            ${displayStats.facts}
          </div>
          <div class="stat-label">Facts</div>
        </div>
        <div class="stat-box">
          <div class="stat-value" style="color: ${isActive ? 'var(--success-color, #3fb950)' : 'var(--text-muted)'};">
            ${displayStats.entities}
          </div>
          <div class="stat-label">Entities</div>
        </div>
        <div class="stat-box">
          <div class="stat-value" style="color: ${isActive ? 'var(--warning-color, #d29922)' : 'var(--text-muted)'};">
            ${displayStats.relationships}
          </div>
          <div class="stat-label">Relations</div>
        </div>
        <div class="stat-box">
          <div class="stat-value" style="color: var(--text-muted);">
            ${displayStats.archived}
          </div>
          <div class="stat-label">Archived</div>
        </div>
      </div>

      <!-- Confidence Bar -->
      <div class="confidence-bar">
        <div class="confidence-header">
          <span class="confidence-label">Average Confidence</span>
          <span class="confidence-value">${displayStats.avg_confidence.toFixed(2)}</span>
        </div>
        <div class="confidence-track">
          <div class="confidence-fill" style="width: ${displayStats.avg_confidence * 100}%; background: ${isActive ? 'var(--primary-color, #58a6ff)' : 'var(--text-muted)'};"></div>
        </div>
      </div>

      <!-- Sources -->
      ${hasData && displayStats.by_source && displayStats.by_source.length > 0 ? html`
        <div class="sources-list">
          <div style="font-size: 12px; color: var(--text-muted); margin-bottom: 6px;">By Source</div>
          ${displayStats.by_source.slice(0, 5).map(s => html`
            <div class="source-row">
              <span>${s.source}</span>
              <span class="chip" style="font-size: 10px;">${s.count}</span>
            </div>
          `)}
        </div>
      ` : nothing}
    </section>

    <!-- Health Status -->
    <section class="card">
      <div class="card-title" style="margin-bottom: 12px;">🏥 System Health</div>
      
      <div class="health-row">
        <span class="health-label">SurrealDB</span>
        <div class="health-detail">
          <span>${health?.surrealdb_binary?.installed ? (health.surrealdb_binary.version || 'Installed') : 'Not installed'}</span>
          <div class="health-badge ${health?.surrealdb_binary?.installed ? 'ok' : 'warn'}">
            ${health?.surrealdb_binary?.installed ? '✓' : '✗'}
          </div>
        </div>
      </div>

      <div class="health-row">
        <span class="health-label">Database</span>
        <div class="health-detail">
          <span>${health?.surrealdb_server?.running ? `Port ${health.surrealdb_server.port}` : 'Offline'}</span>
          <div class="health-badge ${health?.surrealdb_server?.running ? 'ok' : 'warn'}">
            ${health?.surrealdb_server?.running ? '✓' : '✗'}
          </div>
        </div>
      </div>

      <div class="health-row">
        <span class="health-label">Schema</span>
        <div class="health-detail">
          <span>${health?.schema?.initialized ? 'Ready' : 'Not initialized'}</span>
          <div class="health-badge ${health?.schema?.initialized ? 'ok' : 'warn'}">
            ${health?.schema?.initialized ? '✓' : '✗'}
          </div>
        </div>
      </div>

      <div class="health-row">
        <span class="health-label">Python</span>
        <div class="health-detail">
          <span>${health?.python_deps?.ok ? 'All deps' : 'Missing'}</span>
          <div class="health-badge ${health?.python_deps?.ok ? 'ok' : 'warn'}">
            ${health?.python_deps?.ok ? '✓' : '✗'}
          </div>
        </div>
      </div>
    </section>
  `;
}

function renderOperations(props: MemoryProps) {
  const isServerRunning = props.health?.surrealdb_server?.running ?? false;
  const hasPythonDeps = props.health?.python_deps?.ok ?? false;
  const canRunTools = isServerRunning && hasPythonDeps;
  const isHealthy = canRunTools && props.health?.schema?.initialized;

  return html`
    <section class="card">
      <div class="card-title" style="margin-bottom: 4px;">🛠️ Operations</div>
      
      <!-- Extraction Tools -->
      <div class="tool-section">
        <div class="tool-title">📥 Knowledge Extraction</div>
        <div class="tool-desc">Extract facts from MEMORY.md and memory/*.md files using AI.</div>
        
        ${isExtractionRunning(props) ? html`
          <!-- Progress Bar -->
          <div class="progress-container" style="margin: 12px 0;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
              <span style="font-size: 12px; font-weight: 500;">
                ${props.extractionProgress?.message || getExtractionLabel(props.busyAction)}
              </span>
              <span style="font-size: 12px; color: var(--text-muted);">
                ${props.extractionProgress?.percent != null ? `${Math.round(props.extractionProgress.percent)}%` : ''}
                ${props.extractionProgress?.current != null && props.extractionProgress?.total != null 
                  ? `(${props.extractionProgress.current}/${props.extractionProgress.total})` 
                  : ''}
              </span>
            </div>
            <div style="height: 8px; background: var(--border-color, #30363d); border-radius: 4px; overflow: hidden;">
              <div class="progress-bar-fill" style="
                height: 100%; 
                width: ${props.extractionProgress?.percent ?? 5}%; 
                background: linear-gradient(90deg, var(--primary-color, #58a6ff), var(--success-color, #3fb950));
                border-radius: 4px;
                transition: width 0.3s ease;
                ${!props.extractionProgress?.percent ? 'animation: progress-pulse 1.5s ease-in-out infinite;' : ''}
              "></div>
            </div>
            ${props.extractionProgress?.detail ? html`
              <div style="font-size: 11px; color: var(--text-muted); margin-top: 4px;">
                ${props.extractionProgress.detail}
              </div>
            ` : nothing}
          </div>
        ` : html`
          <div class="tool-buttons">
            <button class="btn" ?disabled=${!canRunTools || props.busyAction !== null}
              @click=${() => props.onRunExtraction("extract")}
              title="Extract new/changed facts">
              Extract Changes
            </button>
            <button class="btn" ?disabled=${!canRunTools || props.busyAction !== null}
              @click=${() => props.onRunExtraction("relations")}
              title="Discover relationships between facts">
              Find Relations
            </button>
            <button class="btn primary" ?disabled=${!canRunTools || props.busyAction !== null}
              @click=${() => props.onRunExtraction("full")}
              title="Full extraction + relation discovery">
              Full Sync
            </button>
          </div>
        `}
        
        ${!canRunTools && !isExtractionRunning(props) ? html`
          <div style="font-size: 11px; color: var(--warning-color); margin-top: 8px;">
            ⚠️ Database and Python deps required
          </div>
        ` : nothing}
        ${props.extractionLog && !isExtractionRunning(props) ? html`<div class="log-output">${props.extractionLog}</div>` : nothing}
      </div>

      <!-- Maintenance -->
      <div class="tool-section">
        <div class="tool-title">🔧 Maintenance</div>
        <div class="tool-desc">Apply confidence decay and prune low-quality facts.</div>
        <div class="tool-buttons">
          <button class="btn" ?disabled=${!isServerRunning || props.busyAction !== null}
            @click=${() => props.onRunMaintenance("decay")}>
            ${props.busyAction === "decay" ? "Running…" : "Apply Decay"}
          </button>
          <button class="btn" ?disabled=${!isServerRunning || props.busyAction !== null}
            @click=${() => props.onRunMaintenance("prune")}>
            ${props.busyAction === "prune" ? "Running…" : "Prune Stale"}
          </button>
          <button class="btn" ?disabled=${!isServerRunning || props.busyAction !== null}
            @click=${() => props.onRunMaintenance("full")}>
            ${props.busyAction === "full" ? "Running…" : "Full Sweep"}
          </button>
        </div>
        ${props.maintenanceLog ? html`<div class="log-output">${props.maintenanceLog}</div>` : nothing}
      </div>

      <!-- Installation (only show if not healthy) -->
      ${!isHealthy ? html`
        <div class="tool-section">
          <div class="tool-title">📦 Setup</div>
          <div class="tool-desc">Manual installation if auto-repair doesn't work.</div>
          <div class="tool-buttons">
            <button class="btn small" ?disabled=${props.busyAction !== null} @click=${props.onInstallBinary}>
              ${props.busyAction === "binary" ? "…" : "Install DB"}
            </button>
            <button class="btn small" ?disabled=${props.busyAction !== null} @click=${props.onInstallPython}>
              ${props.busyAction === "python" ? "…" : "Python Deps"}
            </button>
            <button class="btn small" ?disabled=${props.busyAction !== null} @click=${props.onStartServer}>
              ${props.busyAction === "start" ? "…" : "Start Server"}
            </button>
            <button class="btn small" ?disabled=${props.busyAction !== null} @click=${props.onInitSchema}>
              ${props.busyAction === "schema" ? "…" : "Init Schema"}
            </button>
          </div>
          ${props.installLog ? html`<div class="log-output">${props.installLog}</div>` : nothing}
        </div>
      ` : nothing}
    </section>

    <!-- Quick Tips -->
    <section class="card" style="background: var(--bg-tertiary, #161b22);">
      <div style="font-size: 13px; font-weight: 600; margin-bottom: 8px;">💡 Tips</div>
      <div style="font-size: 12px; color: var(--text-muted); line-height: 1.6;">
        • <strong>Extract Changes</strong> runs incrementally on modified files<br>
        • <strong>Find Relations</strong> discovers semantic connections between facts<br>
        • Run <strong>Full Sweep</strong> weekly to maintain quality<br>
        • Facts below 0.3 confidence are auto-archived
      </div>
    </section>
  `;
}
