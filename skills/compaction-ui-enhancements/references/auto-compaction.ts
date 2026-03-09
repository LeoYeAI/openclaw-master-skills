/**
 * Auto-compaction trigger — from ui/src/ui/app-gateway.ts
 *
 * Called after every chat "final" event. Checks token usage against
 * configured threshold and triggers background compaction if exceeded.
 */

/** Check if auto-compaction should trigger based on settings and current token usage. */
async function checkAutoCompaction(host: GatewayHost) {
  const app = host as unknown as OpenClawApp;
  const s = host as unknown as Record<string, unknown>;
  // Don't auto-compact if a compaction is already running
  if ((s.__compactState as Record<string, unknown> | undefined)?.active) return;
  // Debounce: don't auto-compact more than once per 5 minutes
  const lastAuto = (s.__lastAutoCompactAt as number | undefined) ?? 0;
  if (Date.now() - lastAuto < 5 * 60 * 1000) return;

  try {
    const settings = await app.client?.request<{
      ok: boolean;
      settings: { autoEnabled: boolean; autoThresholdPercent: number };
    }>("compaction.getSettings", {});
    if (!settings?.settings?.autoEnabled) return;

    const currentRow = (app.sessionsResult?.sessions ?? []).find(
      (sess: { key: string }) => sess.key === app.sessionKey,
    );
    const totalTokens = (currentRow as { totalTokens?: number } | undefined)?.totalTokens ?? 0;
    const contextWindow =
      (currentRow as { contextTokens?: number } | undefined)?.contextTokens ??
      (app as unknown as { contextWindow?: number }).contextWindow ?? 200000;
    if (!totalTokens || !contextWindow) return;

    const pct = Math.round((totalTokens / contextWindow) * 100);
    if (pct < settings.settings.autoThresholdPercent) return;

    // Trigger background compaction
    if (s.__compactState && (s.__compactState as Record<string, unknown>).active) return;

    s.__lastAutoCompactAt = Date.now();
    s.__compactState = { active: true, phase: "running" };
    const jobId = "cmp-" + Date.now();
    app.backgroundJobToasts = [
      ...(app.backgroundJobToasts ?? []).filter((t) => !t.jobId.startsWith("cmp-")),
      { jobId, jobName: `Auto-Compacting (${pct}%)`, status: "running", startedAt: Date.now(), completedAt: null },
    ];
    app.requestUpdate();

    const result = await app.client?.request<{
      ok: boolean; compacted: boolean; tokensBefore?: number; tokensAfter?: number; reason?: string;
    }>("sessions.compact", { key: app.sessionKey });

    s.__compactState = {};
    if (result?.compacted && result.tokensBefore && result.tokensAfter) {
      const label = `Auto-compacted: ${Math.round(result.tokensBefore / 1000)}K → ${Math.round(result.tokensAfter / 1000)}K`;
      app.backgroundJobToasts = [
        ...(app.backgroundJobToasts ?? []).filter((t) => t.jobId !== jobId),
        { jobId, jobName: label, status: "complete", startedAt: Date.now(), completedAt: Date.now() },
      ];
      app.requestUpdate();
      void refreshChat(app, { scheduleScroll: false });
      setTimeout(() => {
        app.backgroundJobToasts = (app.backgroundJobToasts ?? []).filter((t) => t.jobId !== jobId);
        app.requestUpdate();
      }, 5000);
    } else {
      app.backgroundJobToasts = (app.backgroundJobToasts ?? []).filter((t) => t.jobId !== jobId);
      app.requestUpdate();
    }
  } catch {
    // Silent failure — auto-compaction is best-effort
  }
}
