import React from "react";
import Icon from "../lib/icons";

// ── Colors ──────────────────────────────────────────
const STAGE_COLORS = {
  backlog: { bg: "rgba(100,116,139,0.12)", fill: "#64748b", label: "Backlog" },
  todo:    { bg: "rgba(59,130,246,0.12)", fill: "#3b82f6", label: "To Do" },
  doing:   { bg: "rgba(245,158,11,0.12)", fill: "#f59e0b", label: "Doing" },
  review:  { bg: "rgba(168,85,247,0.12)", fill: "#a855f7", label: "Review" },
  done:    { bg: "rgba(16,185,129,0.12)", fill: "#10b981", label: "Done" },
};

const AGENT_DOT = { online: "#10b981", busy: "#f59e0b", idle: "#3b82f6", offline: "#334155", error: "#ef4444" };
const PROJ_BADGE = {
  active: { bg: "rgba(16,185,129,0.12)", color: "#34d399" },
  draft: { bg: "rgba(100,116,139,0.12)", color: "#94a3b8" },
  paused: { bg: "rgba(245,158,11,0.12)", color: "#fbbf24" },
  completed: { bg: "rgba(16,185,129,0.12)", color: "#6ee7b7" },
};

function formatUSD(n) {
  if (!n || n === 0) return "$0.00";
  return n < 0.01 ? `$${n.toFixed(4)}` : `$${n.toFixed(2)}`;
}

// ── Stat Card ───────────────────────────────────────
function StatCard({ icon, label, value, sub, accentColor = "#6366f1", alert }) {
  return (
    <div style={{
      background: "#0f1528",
      border: `1px solid ${alert ? "rgba(245,158,11,0.2)" : "rgba(255,255,255,0.04)"}`,
      borderRadius: 14,
      padding: "16px 18px",
      position: "relative",
      overflow: "hidden",
      transition: "transform 0.15s, box-shadow 0.2s",
    }} className="mc-card">
      {/* Accent glow */}
      <div style={{
        position: "absolute", top: -20, right: -20,
        width: 80, height: 80, borderRadius: "50%",
        background: `radial-gradient(circle, ${accentColor}15 0%, transparent 70%)`,
        pointerEvents: "none",
      }} />
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
        <div style={{
          width: 30, height: 30, borderRadius: 8,
          background: `${accentColor}12`,
          display: "flex", alignItems: "center", justifyContent: "center",
          color: accentColor,
        }}>
          <Icon name={icon} size={16} />
        </div>
        <span style={{ fontSize: 10, fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.08em", color: "#475569" }}>{label}</span>
      </div>
      <div style={{ fontSize: 28, fontWeight: 700, color: "#f1f5f9", letterSpacing: "-0.02em", lineHeight: 1 }}>{value ?? "—"}</div>
      {sub && <div style={{ fontSize: 11, color: "#475569", marginTop: 5 }}>{sub}</div>}
    </div>
  );
}

// ── Pipeline Bar ────────────────────────────────────
function PipelineBar({ counts }) {
  const stages = ["backlog", "todo", "doing", "review", "done"];
  const total = stages.reduce((s, k) => s + (counts?.[k] || 0), 0) || 1;
  return (
    <div style={{ display: "flex", gap: 2, height: 6, borderRadius: 99, overflow: "hidden", background: "rgba(255,255,255,0.03)" }}>
      {stages.map(s => {
        const c = counts?.[s] || 0;
        if (!c) return null;
        return <div key={s} style={{ width: `${(c / total) * 100}%`, background: STAGE_COLORS[s].fill, borderRadius: 99, transition: "width 0.5s ease" }} />;
      })}
    </div>
  );
}

// ── Alert Banner ────────────────────────────────────
function Alert({ icon, color, children }) {
  return (
    <div style={{
      display: "flex", alignItems: "center", gap: 10,
      padding: "8px 14px", borderRadius: 10,
      background: `${color}08`, border: `1px solid ${color}18`,
    }}>
      <span style={{ width: 6, height: 6, borderRadius: "50%", background: color, flexShrink: 0 }} className="status-pulse" />
      <Icon name={icon} size={14} style={{ color, flexShrink: 0 }} />
      <span style={{ fontSize: 12, color }}>{children}</span>
    </div>
  );
}

// ── Section Header ──────────────────────────────────
function SectionHeader({ icon, children, right }) {
  return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 14 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <Icon name={icon} size={14} style={{ color: "#475569" }} />
        <span style={{ fontSize: 12, fontWeight: 600, color: "#e2e8f0" }}>{children}</span>
      </div>
      {right && <span style={{ fontSize: 10, color: "#334155" }}>{right}</span>}
    </div>
  );
}

// ── Card wrapper ────────────────────────────────────
function Card({ children, style: s = {} }) {
  return (
    <div style={{
      background: "#0f1528",
      border: "1px solid rgba(255,255,255,0.04)",
      borderRadius: 14,
      padding: 20,
      ...s,
    }}>
      {children}
    </div>
  );
}

// ── Main Dashboard ──────────────────────────────────
export default function Dashboard({ stats, projects, agents, activity, loading }) {
  if (loading && !stats) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 300 }}>
        <div style={{ color: "#475569", fontSize: 13 }}>Loading dashboard...</div>
      </div>
    );
  }

  const s = stats || {};
  const activeAgents = agents?.filter(a => a.status === "online" || a.status === "busy") || [];
  const stalledCount = s.stalledTasks?.length || 0;
  const blockedCount = s.blockedTasks?.length || 0;

  return (
    <div style={{ maxWidth: 1400, display: "flex", flexDirection: "column", gap: 16 }}>

      {/* ─── Alerts ────────────────────────────────── */}
      {(s.pendingApprovals > 0 || s.pendingRequests > 0 || stalledCount > 0) && (
        <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
          {s.pendingApprovals > 0 && (
            <Alert icon="bell" color="#f59e0b">
              {s.pendingApprovals} approval{s.pendingApprovals > 1 ? "s" : ""} waiting
            </Alert>
          )}
          {s.pendingRequests > 0 && (
            <Alert icon="inbox" color="#3b82f6">
              {s.pendingRequests} request{s.pendingRequests > 1 ? "s" : ""} pending triage
            </Alert>
          )}
          {stalledCount > 0 && (
            <Alert icon="alertTriangle" color="#ef4444">
              {stalledCount} stalled task{stalledCount > 1 ? "s" : ""}
            </Alert>
          )}
        </div>
      )}

      {/* ─── Stats ─────────────────────────────────── */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 12 }}>
        <StatCard icon="folder" label="Projects" value={s.totalProjects || 0} sub={`${s.projects?.active || 0} active`} accentColor="#6366f1" />
        <StatCard icon="pipeline" label="Tasks" value={s.totalTasks || 0} sub={`${s.tasks?.doing || 0} in progress`} accentColor="#3b82f6" />
        <StatCard icon="cpu" label="Agents" value={s.totalAgents || 0} sub={`${activeAgents.length} online`} accentColor="#10b981" />
        <StatCard icon="alertCircle" label="Blocked" value={blockedCount} sub={blockedCount > 0 ? "Needs attention" : "All clear"} accentColor={blockedCount > 0 ? "#ef4444" : "#10b981"} alert={blockedCount > 0} />
        <StatCard icon="costs" label="Today" value={formatUSD(s.todayCost)} sub="Token spend" accentColor="#a855f7" />
      </div>

      {/* ─── Pipeline + Agents row ─────────────────── */}
      <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr", gap: 12 }}>
        <Card>
          <SectionHeader icon="pipeline">Pipeline Overview</SectionHeader>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 8, marginBottom: 14 }}>
            {Object.entries(STAGE_COLORS).map(([stage, cfg]) => {
              const count = s.tasks?.[stage] || 0;
              return (
                <div key={stage} style={{
                  textAlign: "center", padding: "12px 4px", borderRadius: 10,
                  background: cfg.bg, transition: "background 0.2s",
                }}>
                  <div style={{ fontSize: 22, fontWeight: 700, color: cfg.fill, lineHeight: 1 }}>{count}</div>
                  <div style={{ fontSize: 10, color: "#64748b", marginTop: 4 }}>{cfg.label}</div>
                </div>
              );
            })}
          </div>
          <PipelineBar counts={s.tasks} />
        </Card>

        <Card>
          <SectionHeader icon="cpu">Agents</SectionHeader>
          {agents?.length === 0 ? (
            <div style={{ fontSize: 12, color: "#334155", padding: "16px 0", textAlign: "center" }}>No agents registered</div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
              {agents?.slice(0, 6).map(a => (
                <div key={a.id} style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  {/* Avatar dot */}
                  <div style={{
                    width: 28, height: 28, borderRadius: 8,
                    background: `${AGENT_DOT[a.status] || "#334155"}14`,
                    display: "flex", alignItems: "center", justifyContent: "center",
                    position: "relative",
                  }}>
                    <Icon name="cpu" size={14} style={{ color: AGENT_DOT[a.status] || "#334155" }} />
                    <span style={{
                      position: "absolute", bottom: -1, right: -1,
                      width: 8, height: 8, borderRadius: "50%",
                      background: AGENT_DOT[a.status] || "#334155",
                      border: "2px solid #0f1528",
                    }} className={(a.status === "online" || a.status === "busy") ? "status-pulse" : ""} />
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: 12, color: "#e2e8f0", fontWeight: 500 }}>{a.display_name || a.id}</div>
                    <div style={{ fontSize: 10, color: "#475569" }}>
                      {a.status}{a.model ? ` · ${a.model.split("/").pop()}` : ""}
                      {a.active_tasks ? ` · ${a.active_tasks} tasks` : ""}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </Card>
      </div>

      {/* ─── Projects + Activity row ───────────────── */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
        <Card>
          <SectionHeader icon="folder" right={`${projects?.filter(p => p.status === "active").length || 0} active`}>
            Projects
          </SectionHeader>
          {projects?.length === 0 ? (
            <div style={{ fontSize: 12, color: "#334155", padding: 20, textAlign: "center" }}>No projects yet</div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {projects?.slice(0, 5).map(p => {
                const total = Object.values(p.task_counts || {}).reduce((s, n) => s + n, 0);
                const done = p.task_counts?.done || 0;
                const pct = total > 0 ? Math.round((done / total) * 100) : 0;
                const badge = PROJ_BADGE[p.status] || PROJ_BADGE.draft;
                return (
                  <div key={p.id} style={{ padding: "10px 12px", borderRadius: 10, background: "rgba(6,10,20,0.5)", border: "1px solid rgba(255,255,255,0.03)" }}>
                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 6 }}>
                      <span style={{ fontSize: 12, fontWeight: 500, color: "#e2e8f0" }}>{p.name}</span>
                      <span style={{ fontSize: 9, padding: "1px 7px", borderRadius: 6, background: badge.bg, color: badge.color, fontWeight: 500 }}>{p.status}</span>
                    </div>
                    {/* Progress bar */}
                    <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 4 }}>
                      <div style={{ flex: 1, height: 3, borderRadius: 99, background: "rgba(255,255,255,0.04)", overflow: "hidden" }}>
                        <div style={{ height: "100%", width: `${pct}%`, borderRadius: 99, background: "linear-gradient(90deg, #6366f1, #818cf8)", transition: "width 0.5s" }} />
                      </div>
                      <span style={{ fontSize: 10, color: "#475569", minWidth: 28, textAlign: "right" }}>{pct}%</span>
                    </div>
                    <div style={{ display: "flex", gap: 8, fontSize: 10, color: "#334155" }}>
                      {p.owner_agent && <span style={{ display: "flex", alignItems: "center", gap: 3 }}><Icon name="cpu" size={10} />{p.owner_agent}</span>}
                      <span>{total} task{total !== 1 ? "s" : ""}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </Card>

        <Card>
          <SectionHeader icon="activity">Recent Activity</SectionHeader>
          {activity?.length === 0 ? (
            <div style={{ fontSize: 12, color: "#334155", padding: 20, textAlign: "center" }}>No activity yet</div>
          ) : (
            <div style={{ maxHeight: 300, overflowY: "auto", display: "flex", flexDirection: "column", gap: 0 }}>
              {activity?.slice(0, 15).map(a => {
                const dotColor =
                  (a.action.includes("created") || a.action.includes("submitted") || a.action.includes("published")) ? "#10b981" :
                  (a.action.includes("completed") || a.action.includes("approved")) ? "#6ee7b7" :
                  (a.action.includes("failed") || a.action.includes("rejected") || a.action.includes("stall")) ? "#ef4444" :
                  (a.action.includes("stage") || a.action.includes("triaged") || a.action.includes("assigned")) ? "#f59e0b" :
                  "#334155";
                return (
                  <div key={a.id} style={{ display: "flex", gap: 10, padding: "7px 0", borderBottom: "1px solid rgba(255,255,255,0.025)" }}>
                    <span style={{ width: 6, height: 6, borderRadius: "50%", background: dotColor, flexShrink: 0, marginTop: 5 }} />
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: 11, color: "#94a3b8", lineHeight: 1.4 }}>{a.message}</div>
                      <div style={{ fontSize: 9, color: "#334155", marginTop: 2 }}>
                        {new Date(a.created_at).toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })}
                        {a.actor && <span> · {a.actor}</span>}
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </Card>
      </div>

      {/* ─── Stalled Tasks ─────────────────────────── */}
      {stalledCount > 0 && (
        <div style={{ background: "rgba(239,68,68,0.06)", border: "1px solid rgba(239,68,68,0.12)", borderRadius: 14, padding: 20 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
            <Icon name="alertTriangle" size={16} style={{ color: "#f87171" }} />
            <span style={{ fontSize: 13, fontWeight: 600, color: "#f87171" }}>Stalled Tasks ({stalledCount})</span>
          </div>
          <p style={{ fontSize: 11, color: "#64748b", marginBottom: 12, lineHeight: 1.5 }}>
            These tasks have been in progress with no updates past the configured threshold.
          </p>
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {s.stalledTasks?.map(t => (
              <div key={t.id} style={{ display: "flex", alignItems: "center", gap: 10, padding: "6px 10px", borderRadius: 8, background: "rgba(239,68,68,0.04)" }}>
                <span style={{ width: 5, height: 5, borderRadius: "50%", background: "#f87171" }} />
                <span style={{ flex: 1, fontSize: 12, color: "#e2e8f0" }}>{t.title}</span>
                <span style={{ fontSize: 10, color: "#64748b" }}>{t.assigned_agent || "unassigned"}</span>
                <span style={{ fontSize: 10, color: "#475569" }}>{new Date(t.updated_at).toLocaleString([], { month: "short", day: "numeric", hour: "2-digit", minute: "2-digit" })}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
