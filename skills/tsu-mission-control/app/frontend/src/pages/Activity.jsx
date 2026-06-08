import React, { useState, useCallback } from "react";
import usePagination from "../hooks/usePagination";

const C = {
  bg: "#0a0e1a", card: "#1a2035", border: "#1e293b", accent: "#6366f1",
  text: "#e2e8f0", muted: "#94a3b8", dim: "#64748b", faint: "#475569",
  green: "#10b981", amber: "#f59e0b", red: "#ef4444", purple: "#a855f7", blue: "#3b82f6",
};

const ACTION_COLORS = {
  created: C.green, submitted: C.green, published: C.green, completed: C.green,
  approved: C.green, status_changed: C.blue, stage_changed: C.amber,
  assigned: C.purple, failed: C.red, deleted: C.dim, rejected: C.red,
  stall_detected: C.red, auto_reassigned: C.amber, recorded: C.purple,
  triaged: C.blue, converted: C.accent, commented: C.dim, updated: C.blue,
};

const ENTITY_COLORS = {
  project: C.accent, task: C.blue, agent: C.green, system: C.dim,
  request: C.blue, approval: C.amber, review: C.purple, document: C.accent,
  cost: C.purple, dispatch: C.amber,
};

export default function Activity({ refresh, api: apiClient }) {
  const [typeFilter, setTypeFilter] = useState("");

  const fetchActivity = useCallback(async (offset, limit) => {
    const params = { offset, limit };
    if (typeFilter) params.entity_type = typeFilter;
    return await apiClient.getActivity(params);
  }, [apiClient, typeFilter]);

  const { items, loading, hasMore, loadMore } = usePagination(fetchActivity, {
    pageSize: 50,
    deps: [typeFilter],
  });

  return (
    <div style={{ maxWidth: 900, display: "flex", flexDirection: "column", gap: 12 }}>
      {/* Filters */}
      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        <select value={typeFilter} onChange={e => setTypeFilter(e.target.value)}
          style={{ fontSize: 11, background: C.card, border: `1px solid ${C.border}`, borderRadius: 8, padding: "6px 10px", color: C.muted, outline: "none" }}>
          <option value="">All types</option>
          <option value="project">Projects</option>
          <option value="task">Tasks</option>
          <option value="agent">Agents</option>
          <option value="review">Reviews</option>
          <option value="approval">Approvals</option>
          <option value="request">Requests</option>
          <option value="document">Documents</option>
          <option value="cost">Costs</option>
          <option value="dispatch">Dispatches</option>
          <option value="system">System</option>
        </select>
        <span style={{ fontSize: 11, color: C.faint }}>{items.length} events{hasMore ? "+" : ""}</span>
      </div>

      {/* Activity list */}
      <div style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 12, overflow: "hidden" }}>
        {items.length === 0 && !loading && (
          <div style={{ padding: 40, textAlign: "center", fontSize: 13, color: C.dim }}>No activity recorded yet</div>
        )}
        {items.map(item => {
          const actionColor = ACTION_COLORS[item.action] || C.dim;
          const entityColor = ENTITY_COLORS[item.entity_type] || C.dim;
          return (
            <div key={item.id} style={{ display: "flex", alignItems: "flex-start", gap: 12, padding: "10px 16px", borderBottom: `1px solid rgba(30,41,59,0.3)`, transition: "background 0.1s" }}
              onMouseEnter={e => { e.currentTarget.style.background = "rgba(255,255,255,0.015)"; }}
              onMouseLeave={e => { e.currentTarget.style.background = "transparent"; }}>
              {/* Dot */}
              <span style={{ width: 8, height: 8, borderRadius: "50%", background: actionColor, flexShrink: 0, marginTop: 5 }} />

              {/* Content */}
              <div style={{ flex: 1, minWidth: 0 }}>
                <div style={{ fontSize: 12, color: C.muted, lineHeight: 1.5 }}>{item.message || item.action}</div>
                <div style={{ display: "flex", alignItems: "center", gap: 6, marginTop: 3 }}>
                  <span style={{ fontSize: 9, padding: "1px 6px", borderRadius: 4, color: entityColor, background: entityColor + "18" }}>
                    {item.entity_type}
                  </span>
                  {item.old_value && item.new_value && (
                    <span style={{ fontSize: 10, color: C.faint }}>{item.old_value} → {item.new_value}</span>
                  )}
                  <span style={{ fontSize: 10, color: C.faint, marginLeft: "auto" }}>{item.actor}</span>
                </div>
              </div>

              {/* Timestamp */}
              <div style={{ fontSize: 10, color: C.faint, flexShrink: 0, whiteSpace: "nowrap", marginTop: 2 }}>
                {new Date(item.created_at).toLocaleString()}
              </div>
            </div>
          );
        })}

        {loading && (
          <div style={{ padding: 16, textAlign: "center", fontSize: 12, color: C.dim }}>Loading...</div>
        )}
      </div>

      {/* Load more */}
      {hasMore && items.length > 0 && (
        <div style={{ textAlign: "center" }}>
          <button onClick={loadMore} disabled={loading}
            style={{ fontSize: 12, padding: "6px 20px", borderRadius: 8, background: C.accent + "15", color: C.accent, border: "none", cursor: loading ? "wait" : "pointer", opacity: loading ? 0.5 : 1 }}>
            {loading ? "Loading..." : "Load More"}
          </button>
        </div>
      )}
    </div>
  );
}
