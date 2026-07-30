import { readFile, writeFile } from "fs/promises";
import { resolve } from "path";
import { getConfig } from "../utils/config.js";

export interface HireAnalyticsEvent {
  ts: number;
  target_id: `0x${string}`;
  status: "completed" | "refunded" | "failed";
  amount_paid_usdc: number;
}

interface AnalyticsStore {
  hires: HireAnalyticsEvent[];
}

let _cache: AnalyticsStore | undefined;
let _writeChain: Promise<void> = Promise.resolve();

function getStorePath(): string {
  const cfg = getConfig();
  const p = cfg.ANALYTICS_STORE_PATH || ".safelink-analytics.json";
  return resolve(process.cwd(), p);
}

async function loadStore(): Promise<AnalyticsStore> {
  if (_cache) return _cache;
  try {
    const raw = await readFile(getStorePath(), "utf8");
    const parsed = JSON.parse(raw) as AnalyticsStore;
    _cache = {
      hires: Array.isArray(parsed.hires) ? parsed.hires : [],
    };
  } catch {
    _cache = { hires: [] };
  }
  return _cache;
}

function persistStore(): Promise<void> {
  _writeChain = _writeChain.then(async () => {
    const store = await loadStore();
    await writeFile(getStorePath(), JSON.stringify(store, null, 2) + "\n", "utf8");
  });
  return _writeChain;
}

export async function recordHireEvent(event: HireAnalyticsEvent): Promise<void> {
  const store = await loadStore();
  store.hires.push(event);
  // Keep bounded history
  if (store.hires.length > 10_000) {
    store.hires = store.hires.slice(-10_000);
  }
  await persistStore();
}

export async function getHireSummary(days = 7): Promise<{
  period_days: number;
  total_hires: number;
  completed: number;
  refunded: number;
  failed: number;
  success_rate: number;
  total_spent_usdc: number;
  avg_spent_usdc: number;
  top_targets: Array<{ target_id: `0x${string}`; count: number }>;
}> {
  const store = await loadStore();
  const cutoff = Date.now() - days * 24 * 60 * 60 * 1000;
  const events = store.hires.filter((e) => e.ts >= cutoff);

  const completed = events.filter((e) => e.status === "completed");
  const refunded = events.filter((e) => e.status === "refunded");
  const failed = events.filter((e) => e.status === "failed");

  const targetCount = new Map<`0x${string}`, number>();
  for (const e of events) {
    targetCount.set(e.target_id, (targetCount.get(e.target_id) ?? 0) + 1);
  }

  const totalSpent = events.reduce((sum, e) => sum + e.amount_paid_usdc, 0);

  return {
    period_days: days,
    total_hires: events.length,
    completed: completed.length,
    refunded: refunded.length,
    failed: failed.length,
    success_rate: events.length > 0 ? Number((completed.length / events.length).toFixed(4)) : 0,
    total_spent_usdc: Number(totalSpent.toFixed(6)),
    avg_spent_usdc: events.length > 0 ? Number((totalSpent / events.length).toFixed(6)) : 0,
    top_targets: [...targetCount.entries()]
      .sort((a, b) => b[1] - a[1])
      .slice(0, 5)
      .map(([target_id, count]) => ({ target_id, count })),
  };
}

