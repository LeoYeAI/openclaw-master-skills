import React from "react";
import Icon from "../lib/icons";

const STATUS = {
  online: { color: "#10b981", bg: "rgba(16,185,129,0.1)", label: "Online" },
  busy:   { color: "#f59e0b", bg: "rgba(245,158,11,0.1)", label: "Busy" },
  idle:   { color: "#3b82f6", bg: "rgba(59,130,246,0.1)", label: "Idle" },
  offline:{ color: "#334155", bg: "rgba(51,65,85,0.1)", label: "Offline" },
  error:  { color: "#ef4444", bg: "rgba(239,68,68,0.1)", label: "Error" },
};

function timeAgo(ts) {
  if (!ts) return "never";
  const ms = Date.now() - new Date(ts).getTime();
  if (ms < 60_000) return "just now";
  if (ms < 3_600_000) return `${Math.floor(ms / 60_000)}m ago`;
  if (ms < 86_400_000) return `${Math.floor(ms / 3_600_000)}h ago`;
  return `${Math.floor(ms / 86_400_000)}d ago`;
}

export default function Agents({ agents, loading }) {
  if (loading && !agents?.length) {
    return <div style={{ color: "#475569", fontSize: 13, padding: 40, textAlign: "center" }}>Loading agents...</div>;
  }

  const online = agents?.filter(a => a.status === "online" || a.status === "busy").length || 0;

  return (
    <div style={{ maxWidth: 1000, display: "flex", flexDirection: "column", gap: 14 }}>
      {/* Summary */}
      <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
        <span style={{ fontSize: 12, color: "#64748b" }}>{agents?.length || 0} agents registered</span>
        <span style={{ width: 3, height: 3, borderRadius: "50%", background: "#334155" }} />
        <span style={{ fontSize: 12, color: "#10b981" }}>{online} online</span>
      </div>

      {/* Agent grid */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: 12 }}>
        {agents?.length === 0 && (
          <div style={{ gridColumn: "1/-1", padding: 40, textAlign: "center" }}>
            <Icon name="cpu" size={28} style={{ color: "#334155", margin: "0 auto 8px" }} />
            <div style={{ fontSize: 13, color: "#475569" }}>No agents registered yet</div>
            <div style={{ fontSize: 11, color: "#334155", marginTop: 4 }}>Agents appear here when they connect through the gateway.</div>
          </div>
        )}

        {agents?.map(a => {
          const st = STATUS[a.status] || STATUS.offline;
          return (
            <div key={a.id} className="mc-card" style={{ padding: 18, borderRadius: 14, display: "flex", flexDirection: "column", gap: 12 }}>
              {/* Header row */}
              <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                {/* Avatar */}
                <div style={{
                  width: 38, height: 38, borderRadius: 10,
                  background: st.bg,
                  display: "flex", alignItems: "center", justifyContent: "center",
                  position: "relative",
                }}>
                  <Icon name="cpu" size={18} style={{ color: st.color }} />
                  <span style={{
                    position: "absolute", bottom: -2, right: -2,
                    width: 10, height: 10, borderRadius: "50%",
                    background: st.color, border: "2px solid #0f1528",
                  }} className={(a.status === "online" || a.status === "busy") ? "status-pulse" : ""} />
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 13, fontWeight: 600, color: "#f1f5f9" }}>{a.display_name || a.id}</div>
                  <div style={{
                    display: "inline-flex", alignItems: "center", gap: 4,
                    fontSize: 10, fontWeight: 500, padding: "1px 7px", borderRadius: 6,
                    background: st.bg, color: st.color, marginTop: 2,
                  }}>
                    <span style={{ width: 5, height: 5, borderRadius: "50%", background: st.color }} />
                    {st.label}
                  </div>
                </div>
              </div>

              {/* Details */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 6 }}>
                {a.model && (
                  <div style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 11, color: "#64748b" }}>
                    <Icon name="zap" size={12} style={{ color: "#475569" }} />
                    <span style={{ overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{a.model.split("/").pop()}</span>
                  </div>
                )}
                <div style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 11, color: "#64748b" }}>
                  <Icon name="clock" size={12} style={{ color: "#475569" }} />
                  {timeAgo(a.last_heartbeat)}
                </div>
                {a.active_tasks > 0 && (
                  <div style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 11, color: "#64748b" }}>
                    <Icon name="pipeline" size={12} style={{ color: "#475569" }} />
                    {a.active_tasks} task{a.active_tasks !== 1 ? "s" : ""}
                  </div>
                )}
                {a.total_tasks > 0 && (
                  <div style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 11, color: "#64748b" }}>
                    <Icon name="checkCircle" size={12} style={{ color: "#475569" }} />
                    {a.total_tasks} total
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
