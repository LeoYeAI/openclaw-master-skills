import React, { useState, useEffect } from "react";
import Icon from "../lib/icons";

function formatUSD(n) {
  if (!n || n === 0) return "$0.00";
  return n < 0.01 ? `$${n.toFixed(4)}` : `$${n.toFixed(2)}`;
}

function formatTokens(n) {
  if (!n) return "0";
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(1)}K`;
  return String(n);
}

function BarChart({ data, labelKey, valueKey, formatValue, maxBars = 8, accentColor = "#6366f1" }) {
  const items = data.slice(0, maxBars);
  const max = Math.max(...items.map(d => d[valueKey] || 0), 0.001);

  return (
    <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
      {items.map((d, i) => (
        <div key={i} style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div style={{ width: 90, fontSize: 11, color: "#94a3b8", textAlign: "right", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{d[labelKey]}</div>
          <div style={{ flex: 1, height: 20, background: "rgba(255,255,255,0.02)", borderRadius: 6, overflow: "hidden" }}>
            <div style={{
              height: "100%", borderRadius: 6,
              width: `${Math.max((d[valueKey] / max) * 100, 2)}%`,
              background: `linear-gradient(90deg, ${accentColor}60, ${accentColor}30)`,
              transition: "width 0.5s ease",
            }} />
          </div>
          <div style={{ width: 72, fontSize: 11, color: "#e2e8f0", textAlign: "right", fontFamily: "var(--font-mono)" }}>
            {formatValue ? formatValue(d[valueKey]) : d[valueKey]}
          </div>
        </div>
      ))}
      {data.length === 0 && (
        <div style={{ fontSize: 12, color: "#334155", textAlign: "center", padding: 16 }}>No data yet</div>
      )}
    </div>
  );
}

function SparkLine({ data, valueKey, height = 50 }) {
  if (!data.length) return <div style={{ fontSize: 12, color: "#334155", textAlign: "center", padding: 8 }}>No data</div>;

  const values = data.map(d => d[valueKey] || 0);
  const max = Math.max(...values, 0.001);
  const min = Math.min(...values, 0);
  const range = max - min || 1;
  const w = 100;

  const points = values.map((v, i) => {
    const x = (i / Math.max(values.length - 1, 1)) * w;
    const y = height - ((v - min) / range) * (height - 6) - 3;
    return `${x},${y}`;
  }).join(" ");

  const areaPoints = `0,${height} ${points} ${w},${height}`;

  return (
    <svg viewBox={`0 0 ${w} ${height}`} style={{ width: "100%", height, display: "block" }} preserveAspectRatio="none">
      <defs>
        <linearGradient id="sparkGrad" x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="#6366f1" stopOpacity="0.2" />
          <stop offset="100%" stopColor="#6366f1" stopOpacity="0" />
        </linearGradient>
      </defs>
      <polygon points={areaPoints} fill="url(#sparkGrad)" />
      <polyline points={points} fill="none" stroke="#6366f1" strokeWidth="1.5" vectorEffect="non-scaling-stroke" strokeLinejoin="round" />
    </svg>
  );
}

function Card({ children, style: s = {} }) {
  return (
    <div style={{ background: "#0f1528", border: "1px solid rgba(255,255,255,0.04)", borderRadius: 14, padding: 20, ...s }}>
      {children}
    </div>
  );
}

function StatCard({ icon, label, value, sub, accentColor = "#6366f1" }) {
  return (
    <Card>
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
        <div style={{
          width: 28, height: 28, borderRadius: 7,
          background: `${accentColor}12`,
          display: "flex", alignItems: "center", justifyContent: "center",
          color: accentColor,
        }}>
          <Icon name={icon} size={14} />
        </div>
        <span style={{ fontSize: 10, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.08em", color: "#475569" }}>{label}</span>
      </div>
      <div style={{ fontSize: 26, fontWeight: 700, color: "#f1f5f9", letterSpacing: "-0.02em", lineHeight: 1 }}>{value}</div>
      {sub && <div style={{ fontSize: 11, color: "#475569", marginTop: 5 }}>{sub}</div>}
    </Card>
  );
}

export default function Costs({ api: apiClient }) {
  const [summary, setSummary] = useState(null);
  const [days, setDays] = useState(30);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    apiClient.getCostSummary(days).then(d => setSummary(d)).catch(() => {}).finally(() => setLoading(false));
  }, [days]);

  if (loading && !summary) {
    return <div style={{ color: "#475569", fontSize: 13, padding: 40, textAlign: "center" }}>Loading cost data...</div>;
  }

  const s = summary || {};
  const total = s.total || {};
  const today = s.today || {};

  return (
    <div style={{ maxWidth: 1200, display: "flex", flexDirection: "column", gap: 14 }}>
      {/* Period selector */}
      <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
        {[7, 14, 30, 90].map(d => (
          <button key={d} onClick={() => setDays(d)}
            style={{
              fontSize: 11, padding: "5px 14px", borderRadius: 8, border: "none", cursor: "pointer",
              background: days === d ? "rgba(99,102,241,0.12)" : "transparent",
              color: days === d ? "#a5b4fc" : "#475569",
              fontWeight: days === d ? 500 : 400,
              transition: "all 0.15s",
            }}>
            {d}d
          </button>
        ))}
      </div>

      {/* Top-line stats */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 12 }}>
        <StatCard icon="costs" label={`Total (${days}d)`} value={formatUSD(total.total_cost)} sub={`${total.run_count || 0} runs`} accentColor="#6366f1" />
        <StatCard icon="zap" label="Today" value={formatUSD(today.cost)} sub={`${today.runs || 0} runs`} accentColor="#10b981" />
        <StatCard icon="arrowDown" label="Input Tokens" value={formatTokens(total.total_input)} sub={`${days}d total`} accentColor="#3b82f6" />
        <StatCard icon="arrowUp" label="Output Tokens" value={formatTokens(total.total_output)} sub={`${days}d total`} accentColor="#a855f7" />
      </div>

      {/* Daily trend */}
      <Card>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
            <Icon name="activity" size={14} style={{ color: "#475569" }} />
            <span style={{ fontSize: 12, fontWeight: 600, color: "#e2e8f0" }}>Daily Spend Trend</span>
          </div>
          <span style={{ fontSize: 10, color: "#334155" }}>Last {days} days</span>
        </div>
        <SparkLine data={s.daily || []} valueKey="cost" height={70} />
        {(s.daily?.length || 0) > 0 && (
          <div style={{ display: "flex", justifyContent: "space-between", marginTop: 6, fontSize: 10, color: "#334155" }}>
            <span>{s.daily[0]?.date}</span>
            <span>{s.daily[s.daily.length - 1]?.date}</span>
          </div>
        )}
      </Card>

      {/* Breakdowns */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        <Card>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
            <Icon name="cpu" size={14} style={{ color: "#475569" }} />
            <span style={{ fontSize: 12, fontWeight: 600, color: "#e2e8f0" }}>By Agent</span>
          </div>
          <BarChart data={s.byAgent || []} labelKey="agent_id" valueKey="cost" formatValue={formatUSD} accentColor="#6366f1" />
        </Card>

        <Card>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
            <Icon name="zap" size={14} style={{ color: "#475569" }} />
            <span style={{ fontSize: 12, fontWeight: 600, color: "#e2e8f0" }}>By Model</span>
          </div>
          <BarChart data={s.byModel || []} labelKey="model" valueKey="cost" formatValue={formatUSD} accentColor="#a855f7" />
        </Card>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        <Card>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
            <Icon name="folder" size={14} style={{ color: "#475569" }} />
            <span style={{ fontSize: 12, fontWeight: 600, color: "#e2e8f0" }}>By Project</span>
          </div>
          <BarChart data={s.byProject || []} labelKey="project_name" valueKey="cost" formatValue={formatUSD} accentColor="#3b82f6" />
        </Card>

        <Card>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
            <Icon name="star" size={14} style={{ color: "#475569" }} />
            <span style={{ fontSize: 12, fontWeight: 600, color: "#e2e8f0" }}>Most Expensive Tasks</span>
          </div>
          {(s.topTasks || []).length === 0 ? (
            <div style={{ fontSize: 12, color: "#334155", textAlign: "center", padding: 16 }}>No task-level data yet</div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
              {(s.topTasks || []).slice(0, 6).map((t, i) => (
                <div key={t.task_id} style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <span style={{ fontSize: 10, color: "#475569", width: 16 }}>{i + 1}.</span>
                  <span style={{ flex: 1, fontSize: 12, color: "#94a3b8", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{t.title}</span>
                  <span style={{ fontSize: 11, color: "#64748b", fontFamily: "var(--font-mono)" }}>{formatTokens(t.tokens)}</span>
                  <span style={{ fontSize: 11, color: "#e2e8f0", fontFamily: "var(--font-mono)", fontWeight: 500 }}>{formatUSD(t.cost)}</span>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
