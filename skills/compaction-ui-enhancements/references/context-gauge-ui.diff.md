diff --git a/ui/src/ui/app-render.helpers.ts b/ui/src/ui/app-render.helpers.ts
index 36aa91524..b12bcdd75 100644
--- a/ui/src/ui/app-render.helpers.ts
+++ b/ui/src/ui/app-render.helpers.ts
@@ -84,6 +84,183 @@ export function renderTab(state: AppViewState, tab: Tab) {
   `;
 }
 
+/**
+ * Renders a context window utilization gauge with a compact button.
+ * Shows a small circular progress ring indicating how full the context is,
+ * plus a click-to-compact action.
+ */
+function renderContextGauge(state: AppViewState) {
+  // Find the current session row to get token info
+  const currentRow = (state.sessionsResult?.sessions ?? []).find(
+    (s) => s.key === state.sessionKey,
+  );
+  const totalTokens = currentRow?.totalTokens ?? 0;
+  const contextWindow = currentRow?.contextTokens ?? (state as unknown as OpenClawApp).contextWindow ?? 200000;
+
+  if (!totalTokens || !contextWindow) {
+    return nothing;
+  }
+
+  const pct = Math.min(100, Math.round((totalTokens / contextWindow) * 100));
+  const radius = 9;
+  const circumference = 2 * Math.PI * radius;
+  const dashOffset = circumference - (pct / 100) * circumference;
+
+  // Color based on utilization
+  const color =
+    pct >= 85 ? "var(--clr-danger, #ef4444)" :
+    pct >= 60 ? "var(--clr-warning, #f59e0b)" :
+    "var(--clr-success, #22c55e)";
+
+  const compactState = ((state as unknown as Record<string, unknown>).__compactState ?? {}) as {
+    active?: boolean;
+    phase?: string;
+    error?: string;
+    result?: { compacted?: boolean; tokensBefore?: number; tokensAfter?: number; reason?: string };
+  };
+
+  const handleCompact = () => {
+    if (compactState.active || !state.connected) return;
+    const app = state as unknown as OpenClawApp;
+    const s = state as unknown as Record<string, unknown>;
+    s.__compactState = { active: true, phase: "starting" };
+    app.requestUpdate();
+
+    // Animate phases for user feedback
+    const phases = [
+      { phase: "reading", delay: 400 },
+      { phase: "summarizing", delay: 1200 },
+      { phase: "compacting", delay: 800 },
+    ];
+    let phaseIdx = 0;
+    const advancePhase = () => {
+      if (phaseIdx < phases.length && (s.__compactState as Record<string, unknown>)?.active) {
+        (s.__compactState as Record<string, unknown>).phase = phases[phaseIdx].phase;
+        app.requestUpdate();
+        phaseIdx++;
+        if (phaseIdx < phases.length) {
+          setTimeout(advancePhase, phases[phaseIdx - 1].delay);
+        }
+      }
+    };
+    setTimeout(advancePhase, 300);
+
+    app.client?.request<{ ok: boolean; compacted: boolean; kept?: number; reason?: string }>(
+      "sessions.compact",
+      { key: state.sessionKey },
+    ).then((result) => {
+      s.__compactState = { active: true, phase: "complete", result: result ?? { compacted: false } };
+      app.requestUpdate();
+      // Hold "Compaction Complete" for 2s, then close and refresh
+      setTimeout(() => {
+        s.__compactState = {};
+        app.requestUpdate();
+        if (result?.compacted) {
+          void refreshChat(state as unknown as Parameters<typeof refreshChat>[0], {
+            scheduleScroll: false,
+          });
+        }
+      }, 2000);
+    }).catch((err: unknown) => {
+      s.__compactState = { active: false, phase: "error", error: String(err) };
+      app.requestUpdate();
+      setTimeout(() => {
+        s.__compactState = {};
+        app.requestUpdate();
+      }, 4000);
+    });
+  };
+
+  const tokensK = totalTokens >= 1000 ? `${Math.round(totalTokens / 1000)}K` : String(totalTokens);
+  const ctxK = contextWindow >= 1000 ? `${Math.round(contextWindow / 1000)}K` : String(contextWindow);
+  const tooltip = `Context: ${tokensK} / ${ctxK} tokens (${pct}%)${pct >= 60 ? " — Click to compact" : ""}`;
+
+  const phaseLabels: Record<string, string> = {
+    starting: "Preparing compaction…",
+    reading: "Reading session history…",
+    summarizing: "Summarizing conversation…",
+    compacting: "Compacting context window…",
+    complete: compactState.result?.compacted
+      ? `✅ Compaction Complete${compactState.result.tokensBefore && compactState.result.tokensAfter ? ` — ${Math.round(compactState.result.tokensBefore / 1000)}K → ${Math.round(compactState.result.tokensAfter / 1000)}K tokens` : ""}`
+      : `ℹ️ ${compactState.result?.reason ?? "Nothing to compact."}`,
+    error: `❌ ${compactState.error ?? "Compaction failed."}`,
+  };
+  const phaseLabel = phaseLabels[compactState.phase ?? ""] ?? "";
+  const isWorking = compactState.active && compactState.phase !== "complete" && compactState.phase !== "error";
+
+  const gaugeRing = html`
+    <svg width="18" height="18" viewBox="0 0 24 24" style="transform:rotate(-90deg);">
+      <circle cx="12" cy="12" r="${radius}" fill="none" stroke="var(--clr-surface-3, #333)" stroke-width="3" />
+      <circle cx="12" cy="12" r="${radius}" fill="none" stroke="${color}" stroke-width="3"
+        stroke-dasharray="${circumference}" stroke-dashoffset="${dashOffset}" stroke-linecap="round"
+        style="transition: stroke-dashoffset 0.3s ease;" />
+    </svg>
+  `;
+
+  return html`
+    <button
+      class="btn btn--sm btn--icon"
+      title=${tooltip}
+      ?disabled=${compactState.active || !state.connected || pct < 20}
+      @click=${handleCompact}
+    >
+      ${gaugeRing}
+    </button>
+    ${compactState.phase ? html`
+      <div style="
+        position:fixed; inset:0; z-index:1000;
+        background:rgba(0,0,0,0.55); backdrop-filter:blur(3px);
+        display:flex; align-items:center; justify-content:center;
+      ">
+        <div style="
+          background:var(--bg-card, #1a1a2e);
+          border:1px solid var(--border, #333);
+          border-radius:12px;
+          padding:28px 36px;
+          min-width:360px; max-width:440px;
+          box-shadow:0 20px 60px rgba(0,0,0,0.5);
+          text-align:center;
+        ">
+          <div style="margin-bottom:16px;">
+            ${gaugeRing}
+          </div>
+          <div style="font-size:15px; font-weight:600; margin-bottom:6px; color:var(--text, #eee);">
+            Memory Compaction
+          </div>
+          <div style="font-size:13px; color:var(--text-muted, #999); margin-bottom:18px;">
+            ${phaseLabel}
+          </div>
+          ${isWorking ? html`
+            <div style="
+              height:4px; border-radius:2px;
+              background:var(--clr-surface-3, #333);
+              overflow:hidden;
+            ">
+              <div style="
+                height:100%; border-radius:2px;
+                background:${color};
+                animation:compactProgress 2s ease-in-out infinite;
+              "></div>
+            </div>
+            <style>
+              @keyframes compactProgress {
+                0% { width: 5%; margin-left: 0; }
+                50% { width: 60%; margin-left: 20%; }
+                100% { width: 5%; margin-left: 95%; }
+              }
+            </style>
+          ` : nothing}
+          ${compactState.phase === "complete" || compactState.phase === "error" ? html`
+            <div style="font-size:11px; color:var(--text-muted, #666); margin-top:12px;">
+              Closing automatically…
+            </div>
+          ` : nothing}
+        </div>
+      </div>
+    ` : nothing}
+  `;
+}
+
 export function renderChatControls(state: AppViewState) {
   const mainSessionKey = resolveMainSessionKey(state.hello, state.sessionsResult);
 
@@ -231,6 +408,7 @@ export function renderChatControls(state: AppViewState) {
           )}
         </select>
       </label>
+      ${renderContextGauge(state)}
       <button
         class="btn btn--sm btn--icon"
         ?disabled=${!state.connected}
