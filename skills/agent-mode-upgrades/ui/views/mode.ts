import { html, nothing } from "lit";

export type AgentLoopMode = "core" | "enhanced";

export type ModelInfo = {
  id: string;
  name?: string;
  provider: string;
  contextWindow?: number;
};

export type EnhancedLoopConfig = {
  enabled: boolean;
  /** Provider for orchestrator LLM calls (planning, reflection). */
  orchestratorProvider?: string;
  /** Model for orchestrator LLM calls. */
  orchestratorModel?: string;
  planning: {
    enabled: boolean;
    reflectionAfterTools: boolean;
    maxPlanSteps: number;
  };
  execution: {
    parallelTools: boolean;
    maxConcurrentTools: number;
    confidenceGates: boolean;
    confidenceThreshold: number;
  };
  context: {
    proactiveManagement: boolean;
    summarizeAfterIterations: number;
    contextThreshold: number;
  };
  errorRecovery: {
    enabled: boolean;
    maxAttempts: number;
    learnFromErrors: boolean;
  };
  stateMachine: {
    enabled: boolean;
    logging: boolean;
    metrics: boolean;
  };
};

export type ModeProps = {
  loading: boolean;
  currentMode: AgentLoopMode;
  config: EnhancedLoopConfig | null;
  saving: boolean;
  error: string | null;
  success: string | null;
  availableModels: ModelInfo[];
  onToggleMode: (mode: AgentLoopMode) => void;
  onUpdateConfig: (config: Partial<EnhancedLoopConfig>) => void;
  onSave: () => void;
  onReset: () => void;
};

const DEFAULT_CONFIG: EnhancedLoopConfig = {
  enabled: false,
  planning: {
    enabled: true,
    reflectionAfterTools: true,
    maxPlanSteps: 7,
  },
  execution: {
    parallelTools: true,
    maxConcurrentTools: 5,
    confidenceGates: true,
    confidenceThreshold: 0.7,
  },
  context: {
    proactiveManagement: true,
    summarizeAfterIterations: 5,
    contextThreshold: 0.7,
  },
  errorRecovery: {
    enabled: true,
    maxAttempts: 3,
    learnFromErrors: true,
  },
  stateMachine: {
    enabled: true,
    logging: true,
    metrics: false,
  },
};

export function getDefaultConfig(): EnhancedLoopConfig {
  return JSON.parse(JSON.stringify(DEFAULT_CONFIG));
}

export function renderMode(props: ModeProps) {
  const config = props.config ?? getDefaultConfig();
  const isEnhanced = props.currentMode === "enhanced";

  return html`
    <section class="card">
      <div class="row" style="justify-content: space-between; align-items: flex-start;">
        <div>
          <div class="card-title">⚡ Agent Loop Mode</div>
          <div class="card-sub">
            Switch between core and enhanced agentic loop implementations.
          </div>
        </div>
        <div class="row" style="gap: 8px;">
          ${props.success
            ? html`<span class="chip chip-ok">${props.success}</span>`
            : nothing}
          <button 
            class="btn" 
            ?disabled=${props.loading || props.saving}
            @click=${props.onReset}
          >
            Reset Defaults
          </button>
          <button 
            class="btn primary" 
            ?disabled=${props.loading || props.saving}
            @click=${props.onSave}
          >
            ${props.saving ? "Saving…" : "💾 Save Configuration"}
          </button>
        </div>
      </div>

      ${props.error
        ? html`<div class="callout danger" style="margin-top: 12px;">${props.error}</div>`
        : nothing}
    </section>

    <!-- Mode Toggle -->
    <section class="card" style="margin-top: 16px;">
      <div class="card-title">🔄 Active Mode</div>
      <div class="row" style="margin-top: 16px; gap: 16px;">
        ${renderModeCard({
          title: "Core Loop",
          description: "Original OpenClaw agent loop. Reactive, sequential tool execution with retry-based error handling.",
          icon: "🔧",
          active: !isEnhanced,
          features: [
            "Sequential tool execution",
            "Auth rotation on failure",
            "Context compaction on overflow",
            "Thinking level fallback",
          ],
          onClick: () => props.onToggleMode("core"),
        })}
        ${renderModeCard({
          title: "Enhanced Loop",
          description: "Advanced agentic infrastructure with planning, parallel execution, and confidence-gated autonomy.",
          icon: "🚀",
          active: isEnhanced,
          features: [
            "Planning + reflection layers",
            "Parallel tool execution",
            "Confidence-gated actions",
            "Semantic error recovery",
            "Observable state machine",
          ],
          onClick: () => props.onToggleMode("enhanced"),
          badge: "Experimental",
        })}
      </div>
    </section>

    <!-- Enhanced Loop Configuration (only shown when enhanced is selected) -->
    ${isEnhanced ? renderEnhancedConfig(config, props.onUpdateConfig, props.availableModels) : nothing}
  `;
}

function renderModeCard(opts: {
  title: string;
  description: string;
  icon: string;
  active: boolean;
  features: string[];
  onClick: () => void;
  badge?: string;
}) {
  return html`
    <div 
      class="mode-card ${opts.active ? "active" : ""}"
      style="
        flex: 1;
        padding: 20px;
        border: 2px solid ${opts.active ? "var(--primary-color, #58a6ff)" : "var(--border-color, #30363d)"};
        border-radius: 12px;
        background: ${opts.active ? "var(--bg-tertiary, #161b22)" : "var(--bg-secondary, #0d1117)"};
        cursor: pointer;
        transition: all 0.2s ease;
      "
      @click=${opts.onClick}
    >
      <div class="row" style="justify-content: space-between; align-items: flex-start;">
        <div style="font-size: 32px;">${opts.icon}</div>
        ${opts.badge
          ? html`<span class="chip chip-warn" style="font-size: 11px;">${opts.badge}</span>`
          : nothing}
      </div>
      <div style="margin-top: 12px;">
        <div style="font-size: 18px; font-weight: 600;">${opts.title}</div>
        <div class="muted" style="margin-top: 4px; font-size: 13px;">${opts.description}</div>
      </div>
      <div style="margin-top: 16px;">
        ${opts.features.map(
          (f) => html`
            <div style="display: flex; align-items: center; gap: 8px; margin-top: 6px; font-size: 13px;">
              <span style="color: ${opts.active ? "var(--success-color, #3fb950)" : "var(--text-muted, #8b949e)"};">
                ${opts.active ? "✓" : "○"}
              </span>
              <span>${f}</span>
            </div>
          `
        )}
      </div>
      ${opts.active
        ? html`<div style="margin-top: 16px; text-align: center;">
            <span class="chip chip-ok">Active</span>
          </div>`
        : nothing}
    </div>
  `;
}

function renderEnhancedConfig(
  config: EnhancedLoopConfig,
  onUpdate: (config: Partial<EnhancedLoopConfig>) => void,
  availableModels: ModelInfo[] = [],
) {
  const currentModel = config.orchestratorModel || "claude-haiku-3.5";
  const currentProvider = config.orchestratorProvider || "anthropic";
  const currentValue = `${currentProvider}/${currentModel}`;

  // Group models by provider for the dropdown
  const providerGroups = new Map<string, ModelInfo[]>();
  for (const model of availableModels) {
    const group = providerGroups.get(model.provider) || [];
    group.push(model);
    providerGroups.set(model.provider, group);
  }

  return html`
    <!-- Orchestrator Model -->
    <section class="card" style="margin-top: 16px;">
      <div class="card-title">🤖 Orchestrator Model</div>
      <div class="muted" style="margin-top: 4px; font-size: 13px;">
        Model used for planning, reflection, and orchestration calls. Use a cheaper model to save costs.
      </div>
      <div style="margin-top: 16px; display: flex; align-items: center; gap: 12px;">
        <select
          style="
            flex: 1;
            padding: 8px 12px;
            background: var(--bg-secondary, #0d1117);
            border: 1px solid var(--border-color, #30363d);
            border-radius: 6px;
            color: var(--text-primary, #e6edf3);
            font-size: 14px;
          "
          @change=${(e: Event) => {
            const value = (e.target as HTMLSelectElement).value;
            const slashIdx = value.indexOf("/");
            if (slashIdx > 0) {
              onUpdate({
                orchestratorProvider: value.slice(0, slashIdx),
                orchestratorModel: value.slice(slashIdx + 1),
              });
            }
          }}
        >
          ${availableModels.length === 0
            ? html`<option value="${currentValue}" selected>${currentValue}</option>`
            : html`
                ${[...providerGroups.entries()].map(
                  ([provider, models]) => html`
                    <optgroup label="${provider}">
                      ${models.map(
                        (m) => html`
                          <option
                            value="${m.provider}/${m.id}"
                            ?selected=${m.provider === currentProvider && m.id === currentModel}
                          >
                            ${m.name || m.id}${m.contextWindow ? ` (${Math.round(m.contextWindow / 1000)}k ctx)` : ""}
                          </option>
                        `
                      )}
                    </optgroup>
                  `
                )}
              `}
        </select>
        <span class="chip">${currentProvider}/${currentModel}</span>
      </div>
    </section>

    <div class="row" style="margin-top: 16px; gap: 16px; align-items: flex-start;">
      <!-- Planning & Reflection -->
      <section class="card" style="flex: 1; min-width: 300px;">
        <div class="card-title">🎯 Planning & Reflection</div>
        <div class="muted" style="margin-top: 4px; font-size: 13px;">
          Decompose goals and assess progress after each action.
        </div>
        
        <div style="margin-top: 16px;">
          ${renderToggle({
            label: "Enable Planning",
            description: "Generate execution plans before complex tasks",
            checked: config.planning.enabled,
            onChange: (v) => onUpdate({ planning: { ...config.planning, enabled: v } }),
          })}
          
          ${renderToggle({
            label: "Reflection After Tools",
            description: "Assess progress after each tool execution",
            checked: config.planning.reflectionAfterTools,
            onChange: (v) => onUpdate({ planning: { ...config.planning, reflectionAfterTools: v } }),
            disabled: !config.planning.enabled,
          })}
          
          ${renderSlider({
            label: "Max Plan Steps",
            value: config.planning.maxPlanSteps,
            min: 2,
            max: 15,
            onChange: (v) => onUpdate({ planning: { ...config.planning, maxPlanSteps: v } }),
            disabled: !config.planning.enabled,
          })}
        </div>
      </section>

      <!-- Execution -->
      <section class="card" style="flex: 1; min-width: 300px;">
        <div class="card-title">⚡ Execution</div>
        <div class="muted" style="margin-top: 4px; font-size: 13px;">
          Parallel execution and confidence-gated actions.
        </div>
        
        <div style="margin-top: 16px;">
          ${renderToggle({
            label: "Parallel Tools",
            description: "Execute independent tools concurrently",
            checked: config.execution.parallelTools,
            onChange: (v) => onUpdate({ execution: { ...config.execution, parallelTools: v } }),
          })}
          
          ${renderSlider({
            label: "Max Concurrent",
            value: config.execution.maxConcurrentTools,
            min: 1,
            max: 10,
            onChange: (v) => onUpdate({ execution: { ...config.execution, maxConcurrentTools: v } }),
            disabled: !config.execution.parallelTools,
          })}
          
          ${renderToggle({
            label: "Confidence Gates",
            description: "Assess confidence before risky actions",
            checked: config.execution.confidenceGates,
            onChange: (v) => onUpdate({ execution: { ...config.execution, confidenceGates: v } }),
          })}
          
          ${renderSlider({
            label: "Confidence Threshold",
            value: Math.round(config.execution.confidenceThreshold * 100),
            min: 30,
            max: 95,
            suffix: "%",
            onChange: (v) => onUpdate({ execution: { ...config.execution, confidenceThreshold: v / 100 } }),
            disabled: !config.execution.confidenceGates,
          })}
        </div>
      </section>
    </div>

    <div class="row" style="margin-top: 16px; gap: 16px; align-items: flex-start;">
      <!-- Context Management -->
      <section class="card" style="flex: 1; min-width: 300px;">
        <div class="card-title">📊 Context Management</div>
        <div class="muted" style="margin-top: 4px; font-size: 13px;">
          Proactive context pruning and summarization.
        </div>
        
        <div style="margin-top: 16px;">
          ${renderToggle({
            label: "Proactive Management",
            description: "Summarize and prune before overflow",
            checked: config.context.proactiveManagement,
            onChange: (v) => onUpdate({ context: { ...config.context, proactiveManagement: v } }),
          })}
          
          ${renderSlider({
            label: "Summarize After N Iterations",
            value: config.context.summarizeAfterIterations,
            min: 2,
            max: 15,
            onChange: (v) => onUpdate({ context: { ...config.context, summarizeAfterIterations: v } }),
            disabled: !config.context.proactiveManagement,
          })}
          
          ${renderSlider({
            label: "Context Threshold",
            value: Math.round(config.context.contextThreshold * 100),
            min: 50,
            max: 90,
            suffix: "%",
            onChange: (v) => onUpdate({ context: { ...config.context, contextThreshold: v / 100 } }),
            disabled: !config.context.proactiveManagement,
          })}
        </div>
      </section>

      <!-- Error Recovery -->
      <section class="card" style="flex: 1; min-width: 300px;">
        <div class="card-title">🔧 Error Recovery</div>
        <div class="muted" style="margin-top: 4px; font-size: 13px;">
          Semantic error diagnosis and adaptive recovery.
        </div>
        
        <div style="margin-top: 16px;">
          ${renderToggle({
            label: "Semantic Recovery",
            description: "Diagnose errors and adapt approach",
            checked: config.errorRecovery.enabled,
            onChange: (v) => onUpdate({ errorRecovery: { ...config.errorRecovery, enabled: v } }),
          })}
          
          ${renderSlider({
            label: "Max Recovery Attempts",
            value: config.errorRecovery.maxAttempts,
            min: 1,
            max: 5,
            onChange: (v) => onUpdate({ errorRecovery: { ...config.errorRecovery, maxAttempts: v } }),
            disabled: !config.errorRecovery.enabled,
          })}
          
          ${renderToggle({
            label: "Learn From Errors",
            description: "Store successful recoveries for future use",
            checked: config.errorRecovery.learnFromErrors,
            onChange: (v) => onUpdate({ errorRecovery: { ...config.errorRecovery, learnFromErrors: v } }),
            disabled: !config.errorRecovery.enabled,
          })}
        </div>
      </section>
    </div>

    <!-- State Machine -->
    <section class="card" style="margin-top: 16px;">
      <div class="card-title">📈 State Machine & Observability</div>
      <div class="muted" style="margin-top: 4px; font-size: 13px;">
        Explicit state tracking for debugging and dashboards.
      </div>
      
      <div class="row" style="margin-top: 16px; gap: 32px;">
        ${renderToggle({
          label: "Enable State Machine",
          description: "Track agent state transitions",
          checked: config.stateMachine.enabled,
          onChange: (v) => onUpdate({ stateMachine: { ...config.stateMachine, enabled: v } }),
        })}
        
        ${renderToggle({
          label: "State Logging",
          description: "Log all state transitions",
          checked: config.stateMachine.logging,
          onChange: (v) => onUpdate({ stateMachine: { ...config.stateMachine, logging: v } }),
          disabled: !config.stateMachine.enabled,
        })}
        
        ${renderToggle({
          label: "Metrics Collection",
          description: "Collect timing metrics per state",
          checked: config.stateMachine.metrics,
          onChange: (v) => onUpdate({ stateMachine: { ...config.stateMachine, metrics: v } }),
          disabled: !config.stateMachine.enabled,
        })}
      </div>
    </section>
  `;
}

function renderToggle(opts: {
  label: string;
  description: string;
  checked: boolean;
  onChange: (value: boolean) => void;
  disabled?: boolean;
}) {
  return html`
    <div style="display: flex; justify-content: space-between; align-items: center; padding: 12px 0; border-bottom: 1px solid var(--border-color, #30363d); ${opts.disabled ? 'opacity: 0.5;' : ''}">
      <div>
        <div style="font-weight: 500;">${opts.label}</div>
        <div class="muted" style="font-size: 12px; margin-top: 2px;">${opts.description}</div>
      </div>
      <label class="toggle" style="pointer-events: ${opts.disabled ? 'none' : 'auto'};">
        <input 
          type="checkbox" 
          .checked=${opts.checked}
          ?disabled=${opts.disabled}
          @change=${(e: Event) => opts.onChange((e.target as HTMLInputElement).checked)}
        />
        <span class="toggle-slider"></span>
      </label>
    </div>
  `;
}

function renderSlider(opts: {
  label: string;
  value: number;
  min: number;
  max: number;
  suffix?: string;
  onChange: (value: number) => void;
  disabled?: boolean;
}) {
  return html`
    <div style="padding: 12px 0; border-bottom: 1px solid var(--border-color, #30363d); ${opts.disabled ? 'opacity: 0.5;' : ''}">
      <div style="display: flex; justify-content: space-between; align-items: center;">
        <span style="font-weight: 500;">${opts.label}</span>
        <span class="chip">${opts.value}${opts.suffix ?? ""}</span>
      </div>
      <input 
        type="range" 
        min=${opts.min} 
        max=${opts.max} 
        .value=${String(opts.value)}
        ?disabled=${opts.disabled}
        @input=${(e: Event) => opts.onChange(Number((e.target as HTMLInputElement).value))}
        style="width: 100%; margin-top: 8px;"
      />
    </div>
  `;
}
