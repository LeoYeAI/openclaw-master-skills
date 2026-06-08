import React, { useState, useEffect, useCallback, useReducer } from "react";
import { api } from "./lib/api";
import { useSSE } from "./hooks/useSSE";
import { requestNotificationPermission, notifyInboxItem } from "./lib/notifications";
import Icon from "./lib/icons";
import Dashboard from "./pages/Dashboard";
import Pipeline from "./pages/Pipeline";
import Projects from "./pages/Projects";
import Agents from "./pages/Agents";
import Activity from "./pages/Activity";
import Requests from "./pages/Requests";
import Approvals from "./pages/Approvals";
import Costs from "./pages/Costs";
import Reviews from "./pages/Reviews";
import Inbox from "./pages/Inbox";
import Library from "./pages/Library";

// ─── State ────────────────────────────────────────────
const init = { stats: null, projects: [], pipeline: {}, agents: [], activity: [], loading: true, inboxCount: 0 };

function reducer(s, a) {
  switch (a.type) {
    case "SET_ALL": return { ...s, ...a.payload, loading: false };
    case "SET_BADGES": return { ...s, inboxCount: a.payload };
    case "REFRESH": return { ...s, loading: true };
    default: return s;
  }
}

// ─── View meta ────────────────────────────────────────
const VIEW_META = {
  dashboard: { label: "Dashboard", subtitle: "Overview & alerts", icon: "dashboard" },
  inbox:     { label: "Inbox", subtitle: "Reviews, requests & approvals", icon: "inbox" },
  pipeline:  { label: "Pipeline", subtitle: "Task flow & stages", icon: "pipeline" },
  projects:  { label: "Projects", subtitle: "All projects", icon: "folder" },
  library:   { label: "Library", subtitle: "Documents & knowledge", icon: "library" },
  agents:    { label: "Agents", subtitle: "Fleet status", icon: "cpu" },
  costs:     { label: "Costs", subtitle: "Token spend tracking", icon: "costs" },
  activity:  { label: "Activity", subtitle: "Event timeline", icon: "activity" },
};

export default function App() {
  const [view, setView] = useState("dashboard");
  const [state, dispatch] = useReducer(reducer, init);
  const [lastRefresh, setLastRefresh] = useState(new Date());
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);

  const refresh = useCallback(async () => {
    dispatch({ type: "REFRESH" });
    try {
      const [stats, projects, pipeline, agents, activity, inboxCounts] = await Promise.all([
        api.getStats(), api.getProjects(), api.getPipeline(),
        api.getAgents(), api.getActivity({ limit: 50 }), api.getInboxCounts(),
      ]);
      dispatch({ type: "SET_ALL", payload: { stats, projects, pipeline, agents, activity } });
      dispatch({ type: "SET_BADGES", payload: inboxCounts.total || 0 });
      setLastRefresh(new Date());
    } catch (err) {
      console.error("Refresh failed:", err);
      dispatch({ type: "SET_ALL", payload: {} });
    }
  }, []);

  useEffect(() => {
    refresh();
    requestNotificationPermission();
  }, [refresh]);

  const { connected } = useSSE(
    useCallback(({ event, data }) => {
      const NOTIFY_EVENTS = ["review:submitted", "approval:created", "request:submitted", "task:stalled", "task:failed", "library:published", "agent:error"];
      if (NOTIFY_EVENTS.includes(event)) notifyInboxItem(event, data || {});

      if (event.startsWith("project:") || event.startsWith("task:") || event.startsWith("agent:") ||
          event.startsWith("request:") || event.startsWith("approval:") || event.startsWith("cost:") ||
          event.startsWith("review:") || event.startsWith("library:")) {
        refresh();
      }
    }, [refresh])
  );

  const meta = VIEW_META[view] || VIEW_META.dashboard;
  const viewProps = { ...state, refresh, api };
  const views = {
    dashboard: <Dashboard {...viewProps} />,
    inbox: <Inbox {...viewProps} />,
    pipeline: <Pipeline {...viewProps} />,
    projects: <Projects {...viewProps} />,
    library: <Library {...viewProps} />,
    agents: <Agents {...viewProps} />,
    activity: <Activity {...viewProps} />,
    costs: <Costs {...viewProps} />,
  };

  const navGroups = [
    { label: "Overview", items: [
      { id: "dashboard" },
      { id: "inbox", badge: state.inboxCount },
    ]},
    { label: "Work", items: [
      { id: "pipeline" },
      { id: "projects" },
      { id: "library" },
    ]},
    { label: "System", items: [
      { id: "agents" },
      { id: "costs" },
      { id: "activity" },
    ]},
  ];

  return (
    <div style={{ display: "flex", height: "100vh", overflow: "hidden", background: "#060a14" }}>
      {/* ─── Sidebar ─────────────────────────────── */}
      <aside style={{
        width: sidebarCollapsed ? 60 : 220,
        flexShrink: 0,
        background: "#0a0f1c",
        borderRight: "1px solid rgba(255,255,255,0.04)",
        display: "flex",
        flexDirection: "column",
        transition: "width 0.2s ease",
        overflow: "hidden",
      }}>
        {/* Logo */}
        <div style={{
          padding: sidebarCollapsed ? "18px 10px" : "18px 16px",
          borderBottom: "1px solid rgba(255,255,255,0.04)",
          display: "flex",
          alignItems: "center",
          gap: 12,
          cursor: "pointer",
        }} onClick={() => setSidebarCollapsed(!sidebarCollapsed)}>
          <div style={{
            width: 34, height: 34, borderRadius: 10,
            background: "linear-gradient(135deg, #6366f1, #8b5cf6, #a855f7)",
            display: "flex", alignItems: "center", justifyContent: "center",
            color: "white", fontWeight: 800, fontSize: 13, letterSpacing: "-0.03em",
            flexShrink: 0,
            boxShadow: "0 4px 16px rgba(99,102,241,0.3)",
          }}>MC</div>
          {!sidebarCollapsed && (
            <div style={{ overflow: "hidden", whiteSpace: "nowrap" }}>
              <div style={{ fontSize: 14, fontWeight: 600, color: "#f1f5f9", letterSpacing: "-0.01em" }}>Mission Control</div>
              <div style={{ fontSize: 10, color: "#475569", marginTop: 1 }}>v1.1 · OpenClaw</div>
            </div>
          )}
        </div>

        {/* Nav */}
        <nav style={{ flex: 1, padding: "8px 6px", overflowY: "auto", overflowX: "hidden" }}>
          {navGroups.map(group => (
            <div key={group.label}>
              {!sidebarCollapsed && (
                <div style={{
                  padding: "14px 10px 5px",
                  fontSize: 9, fontWeight: 600,
                  textTransform: "uppercase", letterSpacing: "0.1em",
                  color: "#334155",
                }}>{group.label}</div>
              )}
              {sidebarCollapsed && <div style={{ height: 8 }} />}
              {group.items.map(item => {
                const m = VIEW_META[item.id];
                const isActive = view === item.id;
                return (
                  <button
                    key={item.id}
                    onClick={() => setView(item.id)}
                    title={sidebarCollapsed ? m.label : undefined}
                    className={`mc-nav-item ${isActive ? "active" : ""}`}
                    style={sidebarCollapsed ? { justifyContent: "center", padding: "10px 0" } : {}}
                  >
                    <Icon name={m.icon} size={18} />
                    {!sidebarCollapsed && (
                      <>
                        <span style={{ flex: 1 }}>{m.label}</span>
                        {item.badge > 0 && (
                          <span style={{
                            minWidth: 18, height: 18, padding: "0 5px",
                            borderRadius: 99, fontSize: 10, fontWeight: 700,
                            display: "inline-flex", alignItems: "center", justifyContent: "center",
                            background: "rgba(245,158,11,0.15)", color: "#fbbf24",
                          }}>{item.badge}</span>
                        )}
                      </>
                    )}
                  </button>
                );
              })}
            </div>
          ))}
        </nav>

        {/* Connection status */}
        <div style={{
          padding: sidebarCollapsed ? "12px 0" : "12px 16px",
          borderTop: "1px solid rgba(255,255,255,0.04)",
          display: "flex", alignItems: "center", gap: 8,
          justifyContent: sidebarCollapsed ? "center" : "flex-start",
        }}>
          <span style={{
            width: 7, height: 7, borderRadius: "50%",
            background: connected ? "#10b981" : "#475569",
            boxShadow: connected ? "0 0 8px rgba(16,185,129,0.4)" : "none",
          }} className={connected ? "status-pulse" : ""} />
          {!sidebarCollapsed && (
            <span style={{ fontSize: 11, color: connected ? "#64748b" : "#475569" }}>
              {connected ? "Connected" : "Reconnecting..."}
            </span>
          )}
        </div>
      </aside>

      {/* ─── Main ────────────────────────────────── */}
      <main style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden", minWidth: 0 }}>
        {/* Header */}
        <header style={{
          height: 56,
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          padding: "0 24px",
          borderBottom: "1px solid rgba(255,255,255,0.04)",
          background: "rgba(10,15,28,0.6)",
          backdropFilter: "blur(12px)",
          WebkitBackdropFilter: "blur(12px)",
          flexShrink: 0,
        }}>
          <div>
            <h1 style={{ fontSize: 16, fontWeight: 600, color: "#f1f5f9", letterSpacing: "-0.01em", margin: 0 }}>{meta.label}</h1>
            <p style={{ fontSize: 11, color: "#475569", margin: 0, marginTop: 1 }}>{meta.subtitle}</p>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <span style={{ fontSize: 10, color: "#334155" }}>
              {lastRefresh.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
            </span>
            <button
              onClick={refresh}
              className="mc-btn-soft"
              style={{ padding: "5px 12px", borderRadius: 8, fontSize: 11, border: "none", cursor: "pointer", display: "flex", alignItems: "center", gap: 5 }}
            >
              <Icon name="refresh" size={13} />
              Refresh
            </button>
          </div>
        </header>

        {/* Content */}
        <div style={{ flex: 1, overflowY: "auto", padding: 24 }} key={view} className="fade-in">
          {views[view] || <Dashboard {...viewProps} />}
        </div>
      </main>
    </div>
  );
}
