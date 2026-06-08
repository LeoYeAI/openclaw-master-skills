import React, { useState, useEffect, useCallback } from "react";

// ── Type config ───────────────────────────────────────
const TYPE_CONFIG = {
  request: { label: "Request", color: "#3b82f6", icon: "◆" },
  review: { label: "Review", color: "#a855f7", icon: "◎" },
  approval: { label: "Approval", color: "#f59e0b", icon: "✓" },
};
const URGENCY_ORDER = { critical: 0, urgent: 1, normal: 2, low: 3 };
const URGENCY_COLORS = { critical: "#ef4444", urgent: "#f97316", normal: "#3b82f6", low: "#64748b" };
const STATUS_COLORS = {
  pending: "#f59e0b", approved: "#10b981", rejected: "#ef4444",
  changes_requested: "#f97316", converted: "#6366f1", deferred: "#64748b",
};
const C = {
  bg: "#0a0e1a", card: "#1a2035", border: "#1e293b", accent: "#6366f1",
  text: "#e2e8f0", muted: "#94a3b8", dim: "#64748b", faint: "#475569",
  green: "#10b981", amber: "#f59e0b", red: "#ef4444", orange: "#f97316", purple: "#a855f7",
};

const pill = (fg, bg) => ({ fontSize: 9, padding: "2px 7px", borderRadius: 4, color: fg, background: bg || (fg + "20"), display: "inline-block", lineHeight: "16px" });

// ── Stars ─────────────────────────────────────────────
function Stars({ value, onChange, readonly }) {
  return (
    <div style={{ display: "flex", gap: 2 }}>
      {[1, 2, 3, 4, 5].map(n => (
        <span key={n} onClick={() => !readonly && onChange?.(n)}
          style={{ cursor: readonly ? "default" : "pointer", fontSize: 16, color: n <= (value || 0) ? C.amber : "#374151" }}>★</span>
      ))}
    </div>
  );
}

// ── Review Detail Modal ───────────────────────────────
function ReviewModal({ item, onDecide, onComment, onToggleCheck, onClose }) {
  const [comment, setComment] = useState("");
  const [score, setScore] = useState(item.quality_score || 0);
  const [notes, setNotes] = useState("");

  const deliverables = JSON.parse(item.deliverables || "[]");
  const checklist = JSON.parse(item.checklist || "[]");
  const comments = item._comments || [];
  const prevRounds = item._prev || [];

  return (
    <div onClick={onClose} style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.7)", display: "flex", justifyContent: "center", alignItems: "flex-start", zIndex: 50, overflowY: "auto", padding: "32px 16px" }}>
      <div onClick={e => e.stopPropagation()} style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 12, width: "100%", maxWidth: 620 }}>

        {/* Header */}
        <div style={{ padding: 20, borderBottom: `1px solid ${C.border}` }}>
          <div style={{ display: "flex", gap: 6, alignItems: "center", flexWrap: "wrap", marginBottom: 6 }}>
            <span style={pill(C.purple)}>Review</span>
            <span style={pill(STATUS_COLORS[item.raw_status])}>{item.raw_status.replace(/_/g, " ")}</span>
            <span style={{ fontSize: 10, color: C.faint }}>{item.subtitle}</span>
          </div>
          <div style={{ fontSize: 16, fontWeight: 600, color: "#fff" }}>{item.title}</div>
          {item.task_description && <div style={{ fontSize: 12, color: C.dim, marginTop: 4 }}>{item.task_description}</div>}
          <div style={{ display: "flex", gap: 12, fontSize: 10, color: C.faint, marginTop: 8 }}>
            <span>Agent: {item.submitted_by}</span>
            {item.project_name && <span>Project: {item.project_name}</span>}
            {item.deliverable_count > 0 && <span>{item.deliverable_count} deliverable{item.deliverable_count > 1 ? "s" : ""}</span>}
          </div>
        </div>

        {/* Body */}
        <div style={{ padding: 20, maxHeight: "50vh", overflowY: "auto", display: "flex", flexDirection: "column", gap: 18 }}>
          {/* Summary */}
          {item.work_summary && (
            <div>
              <div style={{ fontSize: 11, fontWeight: 500, color: C.muted, marginBottom: 6 }}>Work Summary</div>
              <div style={{ fontSize: 13, color: C.text, padding: 12, borderRadius: 8, background: C.bg + "80", border: `1px solid ${C.border}50`, lineHeight: 1.6 }}>{item.work_summary}</div>
            </div>
          )}

          {/* Deliverables */}
          {deliverables.length > 0 && (
            <div>
              <div style={{ fontSize: 11, fontWeight: 500, color: C.muted, marginBottom: 6 }}>Deliverables ({deliverables.length})</div>
              <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                {deliverables.map((d, i) => (
                  <div key={i} style={{ display: "flex", alignItems: "center", gap: 10, padding: 10, borderRadius: 8, background: C.bg + "60", border: `1px solid ${C.border}40` }}>
                    <div style={{ width: 32, height: 32, borderRadius: 6, background: C.accent + "15", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 14, flexShrink: 0 }}>
                      {d.type === "code" ? "💻" : d.type === "doc" ? "📝" : "📄"}
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: 12, color: "#fff" }}>{d.name}</div>
                      {d.path && <div style={{ fontSize: 9, color: C.faint, fontFamily: "monospace" }}>{d.path}</div>}
                      {d.summary && <div style={{ fontSize: 10, color: C.dim, marginTop: 2 }}>{d.summary}</div>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Checklist */}
          {checklist.length > 0 && (
            <div>
              <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                <span style={{ fontSize: 11, fontWeight: 500, color: C.muted }}>Review Checklist</span>
                <span style={{ fontSize: 10, color: C.faint }}>{checklist.filter(c => c.checked).length}/{checklist.length}</span>
              </div>
              {checklist.map((c, i) => (
                <label key={i} style={{ display: "flex", alignItems: "center", gap: 8, padding: "5px 8px", cursor: "pointer" }}>
                  <input type="checkbox" checked={c.checked || false} onChange={() => onToggleCheck?.(item.id, i)} style={{ accentColor: C.accent }} />
                  <span style={{ fontSize: 12, color: c.checked ? C.faint : C.text, textDecoration: c.checked ? "line-through" : "none" }}>{c.label}</span>
                </label>
              ))}
            </div>
          )}

          {/* Previous rounds */}
          {prevRounds.length > 0 && (
            <div>
              <div style={{ fontSize: 11, fontWeight: 500, color: C.muted, marginBottom: 6 }}>Previous Rounds</div>
              {prevRounds.map(r => (
                <div key={r.round} style={{ display: "flex", alignItems: "center", gap: 8, fontSize: 11, padding: 8, borderRadius: 8, background: C.bg + "40", marginBottom: 4 }}>
                  <span style={{ color: C.faint }}>Round {r.round}</span>
                  <span style={pill(STATUS_COLORS[r.status])}>{r.status.replace(/_/g, " ")}</span>
                  {r.score && <span style={{ color: C.amber }}>{"★".repeat(r.score)}</span>}
                  {r.notes && <span style={{ color: C.faint, flex: 1 }}>— {r.notes}</span>}
                </div>
              ))}
            </div>
          )}

          {/* Comments */}
          <div>
            <div style={{ fontSize: 11, fontWeight: 500, color: C.muted, marginBottom: 6 }}>Discussion ({comments.length})</div>
            {comments.map(c => (
              <div key={c.id} style={{ padding: 10, borderRadius: 8, background: C.bg + "50", border: `1px solid ${C.border}30`, marginBottom: 6 }}>
                <div style={{ fontSize: 10, fontWeight: 500, color: C.muted, marginBottom: 3 }}>{c.author}</div>
                <div style={{ fontSize: 12, color: C.text, lineHeight: 1.5 }}>{c.text}</div>
              </div>
            ))}
            <div style={{ display: "flex", gap: 8, marginTop: 8 }}>
              <input value={comment} onChange={e => setComment(e.target.value)}
                onKeyDown={e => { if (e.key === "Enter" && comment.trim()) { onComment?.(item.id, comment.trim()); setComment(""); } }}
                placeholder="Add a comment..."
                style={{ flex: 1, background: C.bg, border: `1px solid ${C.border}`, borderRadius: 8, padding: "6px 12px", fontSize: 12, color: "#fff", outline: "none" }} />
              <button onClick={() => { if (comment.trim()) { onComment?.(item.id, comment.trim()); setComment(""); } }}
                style={{ fontSize: 11, padding: "6px 12px", borderRadius: 8, background: C.accent + "18", color: C.accent, border: "none", cursor: "pointer" }}>Send</button>
            </div>
          </div>
        </div>

        {/* Decision footer */}
        {item.status === "pending" ? (
          <div style={{ padding: 20, borderTop: `1px solid ${C.border}`, display: "flex", flexDirection: "column", gap: 12 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
              <div><div style={{ fontSize: 10, color: C.faint, marginBottom: 4 }}>Quality</div><Stars value={score} onChange={setScore} /></div>
              <div style={{ flex: 1 }}><div style={{ fontSize: 10, color: C.faint, marginBottom: 4 }}>Feedback</div>
                <input value={notes} onChange={e => setNotes(e.target.value)} placeholder="Notes for the agent..."
                  style={{ width: "100%", background: C.bg, border: `1px solid ${C.border}`, borderRadius: 8, padding: "6px 12px", fontSize: 12, color: "#fff", outline: "none", boxSizing: "border-box" }} />
              </div>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between" }}>
              <button onClick={onClose} style={{ fontSize: 12, padding: "6px 14px", color: C.dim, background: "none", border: "none", cursor: "pointer" }}>Close</button>
              <div style={{ display: "flex", gap: 8 }}>
                <button onClick={() => { onDecide(item, "rejected", notes, score); onClose(); }}
                  style={{ fontSize: 12, padding: "6px 16px", borderRadius: 8, background: C.red + "15", color: C.red, border: "none", cursor: "pointer", fontWeight: 500 }}>Reject</button>
                <button onClick={() => { onDecide(item, "changes_requested", notes, score); onClose(); }}
                  style={{ fontSize: 12, padding: "6px 16px", borderRadius: 8, background: C.orange + "15", color: C.orange, border: "none", cursor: "pointer", fontWeight: 500 }}>Request Changes</button>
                <button onClick={() => { onDecide(item, "approved", notes, score); onClose(); }}
                  style={{ fontSize: 12, padding: "6px 16px", borderRadius: 8, background: C.green + "15", color: C.green, border: "none", cursor: "pointer", fontWeight: 500 }}>✓ Approve</button>
              </div>
            </div>
          </div>
        ) : (
          <div style={{ padding: 16, borderTop: `1px solid ${C.border}`, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
              {item.quality_score && <Stars value={item.quality_score} readonly />}
              {item.decided_notes && <span style={{ fontSize: 12, color: C.faint, fontStyle: "italic" }}>"{item.decided_notes}"</span>}
            </div>
            <button onClick={onClose} style={{ fontSize: 12, color: C.dim, background: "none", border: "none", cursor: "pointer" }}>Close</button>
          </div>
        )}
      </div>
    </div>
  );
}

// ── Simple Decision Modal (for requests & approvals) ──
function DecisionModal({ item, onDecide, onClose }) {
  const [notes, setNotes] = useState("");
  const isRequest = item.inbox_type === "request";

  const options = isRequest
    ? [{ d: "approved", label: "Approve", color: C.green }, { d: "deferred", label: "Defer", color: C.amber }, { d: "rejected", label: "Reject", color: C.red }]
    : [{ d: "approved", label: "Approve", color: C.green }, { d: "rejected", label: "Reject", color: C.red }];

  return (
    <div onClick={onClose} style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.7)", display: "flex", justifyContent: "center", alignItems: "center", zIndex: 50 }}>
      <div onClick={e => e.stopPropagation()} style={{ background: C.card, border: `1px solid ${C.border}`, borderRadius: 12, padding: 24, width: "100%", maxWidth: 480 }}>
        <div style={{ display: "flex", gap: 6, alignItems: "center", marginBottom: 6 }}>
          <span style={pill(TYPE_CONFIG[item.inbox_type].color)}>{TYPE_CONFIG[item.inbox_type].label}</span>
          {item.urgency !== "normal" && <span style={{ fontSize: 10, color: URGENCY_COLORS[item.urgency], fontWeight: 500, textTransform: "uppercase" }}>{item.urgency}</span>}
        </div>
        <div style={{ fontSize: 16, fontWeight: 600, color: "#fff", marginBottom: 4 }}>{item.title}</div>
        {item.description && <div style={{ fontSize: 12, color: C.dim, marginBottom: 12, padding: 12, borderRadius: 8, background: C.bg + "80", lineHeight: 1.5 }}>{item.description}</div>}

        {item.resume_token && (
          <div style={{ fontSize: 10, color: C.amber, padding: 8, borderRadius: 8, background: C.amber + "10", border: `1px solid ${C.amber}20`, marginBottom: 12 }}>
            ⚡ This is a Lobster workflow gate. Approving resumes the paused pipeline.
          </div>
        )}

        <div style={{ marginBottom: 16 }}>
          <div style={{ fontSize: 10, color: C.faint, marginBottom: 4 }}>Notes</div>
          <textarea value={notes} onChange={e => setNotes(e.target.value)} placeholder="Reason for decision..."
            style={{ width: "100%", background: C.bg, border: `1px solid ${C.border}`, borderRadius: 8, padding: "8px 12px", fontSize: 12, color: C.text, outline: "none", resize: "none", height: 56, boxSizing: "border-box" }} />
        </div>

        <div style={{ display: "flex", justifyContent: "space-between" }}>
          <button onClick={onClose} style={{ fontSize: 12, padding: "6px 14px", color: C.dim, background: "none", border: "none", cursor: "pointer" }}>Cancel</button>
          <div style={{ display: "flex", gap: 8 }}>
            {options.map(o => (
              <button key={o.d} onClick={() => { onDecide(item, o.d, notes); onClose(); }}
                style={{ fontSize: 12, padding: "6px 16px", borderRadius: 8, background: o.color + "15", color: o.color, border: "none", cursor: "pointer", fontWeight: 500 }}>
                {o.label}
              </button>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

// ── New Request Form ──────────────────────────────────
function RequestForm({ onSubmit, onCancel }) {
  const [title, setTitle] = useState("");
  const [desc, setDesc] = useState("");
  const [cat, setCat] = useState("general");
  const [urg, setUrg] = useState("normal");

  return (
    <div style={{ background: C.card, border: `1px solid ${C.accent}40`, borderRadius: 12, padding: 20 }}>
      <div style={{ fontSize: 14, fontWeight: 600, color: "#fff", marginBottom: 12 }}>Submit New Request</div>
      <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
        <input value={title} onChange={e => setTitle(e.target.value)} placeholder="What do you need?"
          style={{ width: "100%", background: "transparent", border: `1px solid ${C.border}`, borderRadius: 8, padding: "8px 12px", fontSize: 13, color: "#fff", outline: "none", boxSizing: "border-box" }} autoFocus />
        <textarea value={desc} onChange={e => setDesc(e.target.value)} placeholder="Details, goals, constraints..."
          style={{ width: "100%", background: "transparent", border: `1px solid ${C.border}`, borderRadius: 8, padding: "8px 12px", fontSize: 11, color: C.muted, outline: "none", resize: "none", height: 72, boxSizing: "border-box" }} />
        <div style={{ display: "flex", gap: 10 }}>
          <select value={cat} onChange={e => setCat(e.target.value)}
            style={{ fontSize: 11, background: C.bg, border: `1px solid ${C.border}`, borderRadius: 6, padding: "5px 8px", color: C.muted, outline: "none" }}>
            {["feature", "bug", "research", "content", "ops", "automation", "general"].map(c => <option key={c} value={c}>{c}</option>)}
          </select>
          <select value={urg} onChange={e => setUrg(e.target.value)}
            style={{ fontSize: 11, background: C.bg, border: `1px solid ${C.border}`, borderRadius: 6, padding: "5px 8px", color: C.muted, outline: "none" }}>
            {["critical", "urgent", "normal", "low"].map(u => <option key={u} value={u}>{u}</option>)}
          </select>
        </div>
        <div style={{ display: "flex", justifyContent: "flex-end", gap: 8, marginTop: 4 }}>
          <button onClick={onCancel} style={{ fontSize: 12, padding: "6px 14px", color: C.dim, background: "none", border: "none", cursor: "pointer" }}>Cancel</button>
          <button onClick={() => { if (title.trim()) { onSubmit({ title: title.trim(), description: desc, category: cat, urgency: urg }); } }}
            style={{ fontSize: 12, padding: "6px 16px", borderRadius: 8, background: C.accent, color: "#fff", border: "none", cursor: "pointer" }}>Submit Request</button>
        </div>
      </div>
    </div>
  );
}

// ── Main Inbox Component ──────────────────────────────
export default function Inbox({ refresh, agents, api: apiClient }) {
  const [items, setItems] = useState([]);
  const [counts, setCounts] = useState({ requests: 0, reviews: 0, approvals: 0, total: 0 });
  const [filter, setFilter] = useState("pending");
  const [typeFilter, setTypeFilter] = useState("");
  const [modal, setModal] = useState(null);
  const [showForm, setShowForm] = useState(false);

  const load = useCallback(async () => {
    try {
      const params = {};
      if (filter !== "all") params.status = filter;
      if (typeFilter) params.type = typeFilter;
      const [data, c] = await Promise.all([
        apiClient.getInbox(params),
        apiClient.getInboxCounts(),
      ]);
      setItems(data);
      setCounts(c);
    } catch (err) {
      console.error("Inbox load failed:", err);
    }
  }, [filter, typeFilter, apiClient]);

  useEffect(() => { load(); }, [load]);

  // ── Actions ─────────────────────────────────────
  const handleDecide = async (item, decision, notes, score) => {
    try {
      switch (item.inbox_type) {
        case "request":
          if (decision === "approved") {
            await apiClient.convertRequest(item.id, { owner_agent: undefined });
          } else {
            await apiClient.triageRequest(item.id, { status: decision, review_notes: notes });
          }
          break;
        case "review":
          await apiClient.decideReview(item.id, decision, notes, score, "user");
          break;
        case "approval":
          await apiClient.decideApproval(item.id, decision, notes, "user");
          break;
      }
      load();
      refresh();
    } catch (err) {
      alert(`Failed: ${err.message}`);
    }
  };

  const handleQuickApprove = (item) => handleDecide(item, "approved", "", null);

  const handleSubmitRequest = async (data) => {
    try {
      await apiClient.submitRequest(data);
      setShowForm(false);
      load();
      refresh();
    } catch (err) {
      alert(`Failed: ${err.message}`);
    }
  };

  const openDetail = async (item) => {
    if (item.inbox_type === "review") {
      // Load full review detail with comments and previous rounds
      try {
        const detail = await apiClient.getReview(item.id);
        setModal({
          ...item,
          _comments: detail.comments || [],
          _prev: detail.previous_rounds || [],
          work_summary: detail.work_summary,
          deliverables: detail.deliverables,
          checklist: detail.checklist,
          task_description: detail.task_description,
          quality_score: detail.quality_score,
        });
      } catch {
        setModal(item);
      }
    } else {
      setModal(item);
    }
  };

  const handleComment = async (reviewId, content) => {
    try {
      const comments = await apiClient.addReviewComment(reviewId, content, "user");
      setModal(prev => prev ? { ...prev, _comments: comments } : prev);
    } catch (err) {
      alert(`Failed: ${err.message}`);
    }
  };

  // ── Render ──────────────────────────────────────
  const pendingCount = counts.total;

  return (
    <div style={{ maxWidth: 1000, display: "flex", flexDirection: "column", gap: 14 }}>
      {/* Header bar */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <select value={filter} onChange={e => setFilter(e.target.value)}
            style={{ fontSize: 11, background: C.card, border: `1px solid ${C.border}`, borderRadius: 8, padding: "6px 10px", color: C.muted, outline: "none" }}>
            <option value="pending">Needs Decision</option>
            <option value="decided">Decided</option>
            <option value="all">All</option>
          </select>
          <select value={typeFilter} onChange={e => setTypeFilter(e.target.value)}
            style={{ fontSize: 11, background: C.card, border: `1px solid ${C.border}`, borderRadius: 8, padding: "6px 10px", color: C.muted, outline: "none" }}>
            <option value="">All Types</option>
            <option value="request">Requests</option>
            <option value="review">Reviews</option>
            <option value="approval">Approvals</option>
          </select>
          {/* Count chips */}
          <div style={{ display: "flex", gap: 6 }}>
            {counts.requests > 0 && <span style={pill(TYPE_CONFIG.request.color)}>{counts.requests} request{counts.requests > 1 ? "s" : ""}</span>}
            {counts.reviews > 0 && <span style={pill(TYPE_CONFIG.review.color)}>{counts.reviews} review{counts.reviews > 1 ? "s" : ""}</span>}
            {counts.approvals > 0 && <span style={pill(TYPE_CONFIG.approval.color)}>{counts.approvals} approval{counts.approvals > 1 ? "s" : ""}</span>}
          </div>
        </div>
        <button onClick={() => setShowForm(!showForm)}
          style={{ fontSize: 12, padding: "6px 14px", borderRadius: 8, background: C.accent, color: "#fff", border: "none", cursor: "pointer" }}>
          + New Request
        </button>
      </div>

      {/* Request form */}
      {showForm && <RequestForm onSubmit={handleSubmitRequest} onCancel={() => setShowForm(false)} />}

      {/* Items */}
      {items.map(item => {
        const tc = TYPE_CONFIG[item.inbox_type];
        const isPending = item.status === "pending";
        const borderLeft = item.urgency === "critical" ? `3px solid ${C.red}`
          : item.urgency === "urgent" ? `3px solid ${C.orange}`
          : `3px solid ${C.border}`;

        return (
          <div key={`${item.inbox_type}-${item.id}`}
            onClick={() => openDetail(item)}
            style={{
              background: C.card, border: `1px solid ${C.border}`, borderLeft,
              borderRadius: 12, padding: 16, cursor: "pointer",
              transition: "transform 0.15s, box-shadow 0.15s",
            }}
            onMouseEnter={e => { e.currentTarget.style.transform = "translateY(-1px)"; e.currentTarget.style.boxShadow = "0 4px 20px rgba(0,0,0,0.3)"; }}
            onMouseLeave={e => { e.currentTarget.style.transform = ""; e.currentTarget.style.boxShadow = ""; }}
          >
            <div style={{ display: "flex", gap: 12 }}>
              <div style={{ flex: 1, minWidth: 0 }}>
                {/* Tags row */}
                <div style={{ display: "flex", gap: 6, alignItems: "center", flexWrap: "wrap", marginBottom: 4 }}>
                  <span style={pill(tc.color)}>{tc.icon} {tc.label}</span>
                  <span style={pill(STATUS_COLORS[item.raw_status] || C.dim)}>{item.raw_status.replace(/_/g, " ")}</span>
                  {item.urgency !== "normal" && <span style={{ fontSize: 9, color: URGENCY_COLORS[item.urgency], fontWeight: 600, textTransform: "uppercase" }}>{item.urgency}</span>}
                  {item.resume_token && <span style={{ fontSize: 9, color: C.amber }}>⚡ workflow</span>}
                  {item.inbox_type === "review" && item.deliverable_count > 0 && (
                    <span style={{ fontSize: 9, color: C.faint }}>{item.deliverable_count} deliverable{item.deliverable_count > 1 ? "s" : ""}</span>
                  )}
                </div>

                {/* Title */}
                <div style={{ fontSize: 13, fontWeight: 500, color: "#fff", marginBottom: 2 }}>{item.title}</div>

                {/* Subtitle / description */}
                <div style={{ fontSize: 11, color: C.dim, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                  {item.description || item.subtitle}
                </div>

                {/* Meta */}
                <div style={{ display: "flex", gap: 12, fontSize: 10, color: C.faint, marginTop: 6 }}>
                  <span>From: {item.submitted_by}</span>
                  <span>{item.subtitle}</span>
                  <span>{new Date(item.created_at).toLocaleString()}</span>
                  {item.quality_score && <span style={{ color: C.amber }}>{"★".repeat(item.quality_score)}</span>}
                  {item.decided_by && <span>Decided: {item.decided_by}</span>}
                </div>
                {item.decided_notes && (
                  <div style={{ fontSize: 11, color: C.faint, marginTop: 4, fontStyle: "italic" }}>"{item.decided_notes}"</div>
                )}
              </div>

              {/* Quick actions */}
              {isPending && (
                <div style={{ display: "flex", gap: 4, flexShrink: 0, alignItems: "flex-start" }} onClick={e => e.stopPropagation()}>
                  <button onClick={() => handleQuickApprove(item)}
                    style={{ fontSize: 10, padding: "5px 10px", borderRadius: 8, background: C.green + "18", color: C.green, border: "none", cursor: "pointer" }}>✓</button>
                  <button onClick={() => openDetail(item)}
                    style={{ fontSize: 10, padding: "5px 10px", borderRadius: 8, background: "#ffffff08", color: C.muted, border: "none", cursor: "pointer" }}>
                    {item.inbox_type === "review" ? "Review" : "Decide"}
                  </button>
                  <button onClick={() => handleDecide(item, "rejected", "", null)}
                    style={{ fontSize: 10, padding: "5px 10px", borderRadius: 8, background: C.red + "18", color: C.red, border: "none", cursor: "pointer" }}>✕</button>
                </div>
              )}
            </div>
          </div>
        );
      })}

      {/* Empty state */}
      {items.length === 0 && !showForm && (
        <div style={{ textAlign: "center", padding: "48px 0" }}>
          <div style={{ fontSize: 28, marginBottom: 8 }}>✓</div>
          <div style={{ fontSize: 14, color: C.muted, marginBottom: 4 }}>
            {filter === "pending" ? "Inbox zero — nothing needs your attention" : "No items found"}
          </div>
          <div style={{ fontSize: 11, color: C.faint }}>
            Requests, reviews, and approvals all appear here when they need a decision.
          </div>
        </div>
      )}

      {/* Modals */}
      {modal && modal.inbox_type === "review" && (
        <ReviewModal item={modal} onDecide={handleDecide} onComment={handleComment} onClose={() => setModal(null)} />
      )}
      {modal && modal.inbox_type !== "review" && (
        <DecisionModal item={modal} onDecide={handleDecide} onClose={() => setModal(null)} />
      )}
    </div>
  );
}
