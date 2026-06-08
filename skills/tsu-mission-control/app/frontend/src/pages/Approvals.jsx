import React, { useState, useEffect } from "react";

const TYPE_LABELS = {
  task_review: "Task Review",
  project_approval: "Project Approval",
  workflow_gate: "Workflow Gate",
  cost_alert: "Cost Alert",
  request_triage: "Request Triage",
  custom: "Action Needed",
};
const TYPE_COLORS = {
  task_review: "bg-purple-500/20 text-purple-400",
  project_approval: "bg-indigo-500/20 text-indigo-400",
  workflow_gate: "bg-amber-500/20 text-amber-400",
  cost_alert: "bg-red-500/20 text-red-400",
  request_triage: "bg-blue-500/20 text-blue-400",
  custom: "bg-gray-500/20 text-gray-400",
};
const URGENCY_RING = {
  critical: "border-l-red-500",
  urgent: "border-l-orange-500",
  normal: "border-l-blue-500",
  low: "border-l-gray-500",
};
const STATUS_BADGE = {
  pending: "bg-amber-500/20 text-amber-400",
  approved: "bg-emerald-500/20 text-emerald-400",
  rejected: "bg-red-500/20 text-red-400",
  expired: "bg-gray-500/20 text-gray-500",
  cancelled: "bg-gray-500/20 text-gray-500",
};

function DecisionModal({ approval, onDecide, onClose }) {
  const [notes, setNotes] = useState("");

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-mc-card border border-mc-border rounded-xl p-6 w-full max-w-lg" onClick={e => e.stopPropagation()}>
        <div className="flex items-center gap-2 mb-2">
          <span className={`text-[10px] px-2 py-0.5 rounded ${TYPE_COLORS[approval.type]}`}>
            {TYPE_LABELS[approval.type]}
          </span>
          {approval.urgency !== "normal" && (
            <span className="text-[10px] text-orange-400 uppercase">{approval.urgency}</span>
          )}
        </div>
        <h2 className="text-base font-semibold text-white mb-2">{approval.title}</h2>
        {approval.description && (
          <p className="text-xs text-gray-400 mb-3 p-3 bg-mc-bg/50 rounded-lg leading-relaxed">{approval.description}</p>
        )}

        {/* Entity info */}
        {approval.entity && (
          <div className="text-[11px] text-gray-500 mb-3 p-2 rounded-lg bg-mc-bg/30 border border-mc-border/30">
            {approval.entity_type === "task" && <>Task: <span className="text-white">{approval.entity.title}</span> · Stage: {approval.entity.pipeline_stage} · Agent: {approval.entity.assigned_agent || "none"}</>}
            {approval.entity_type === "project" && <>Project: <span className="text-white">{approval.entity.name}</span> · Status: {approval.entity.status}</>}
            {approval.entity_type === "request" && <>Request: <span className="text-white">{approval.entity.title}</span> · Urgency: {approval.entity.urgency}</>}
          </div>
        )}

        {approval.resume_token && (
          <div className="text-[10px] text-amber-400 mb-3 p-2 bg-amber-500/10 rounded-lg border border-amber-500/20">
            This approval is linked to a Lobster workflow gate. Approving will resume the paused workflow.
          </div>
        )}

        <div className="mb-4">
          <label className="text-xs text-gray-500 block mb-1">Decision notes (optional)</label>
          <textarea value={notes} onChange={e => setNotes(e.target.value)}
            className="w-full bg-mc-bg border border-mc-border rounded-lg px-3 py-2 text-xs text-gray-300 outline-none resize-none h-16 focus:border-mc-accent transition-colors"
            placeholder="Add context for your decision..." />
        </div>

        <div className="flex justify-between">
          <button onClick={onClose} className="text-sm px-4 py-2 text-gray-500 hover:text-gray-300 transition-colors">Cancel</button>
          <div className="flex gap-2">
            <button onClick={() => { onDecide(approval.id, "rejected", notes); onClose(); }}
              className="text-sm px-5 py-2 rounded-lg bg-red-500/15 text-red-400 hover:bg-red-500/25 transition-colors font-medium">
              Reject
            </button>
            <button onClick={() => { onDecide(approval.id, "approved", notes); onClose(); }}
              className="text-sm px-5 py-2 rounded-lg bg-emerald-500/15 text-emerald-400 hover:bg-emerald-500/25 transition-colors font-medium">
              Approve
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default function Approvals({ refresh, api: apiClient }) {
  const [approvals, setApprovals] = useState([]);
  const [filter, setFilter] = useState("pending");
  const [deciding, setDeciding] = useState(null);

  useEffect(() => { loadApprovals(); }, [filter]);

  const loadApprovals = async () => {
    try {
      const data = await apiClient.getApprovals({ status: filter });
      setApprovals(data);
    } catch {}
  };

  const handleDecide = async (id, decision, notes) => {
    try {
      await apiClient.decideApproval(id, decision, notes, "user");
      loadApprovals();
      refresh();
    } catch (err) { alert(`Failed: ${err.message}`); }
  };

  const pendingCount = filter !== "pending"
    ? approvals.filter(a => a.status === "pending").length
    : approvals.length;

  return (
    <div className="space-y-5 max-w-[1000px]">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <select value={filter} onChange={e => setFilter(e.target.value)}
            className="text-xs bg-mc-card border border-mc-border rounded-lg px-3 py-2 text-gray-300">
            <option value="pending">Pending</option>
            <option value="approved">Approved</option>
            <option value="rejected">Rejected</option>
            <option value="expired">Expired</option>
            <option value="all">All</option>
          </select>
          <span className="text-xs text-gray-500">{approvals.length} items</span>
        </div>
        {pendingCount > 0 && (
          <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-amber-500/10 border border-amber-500/20">
            <span className="w-2 h-2 rounded-full bg-amber-500 status-pulse" />
            <span className="text-xs text-amber-400 font-medium">{pendingCount} awaiting decision</span>
          </div>
        )}
      </div>

      {/* Approvals list */}
      <div className="space-y-2">
        {approvals.map(a => (
          <div key={a.id}
            className={`bg-mc-card border border-mc-border rounded-xl p-4 card-hover border-l-4 ${URGENCY_RING[a.urgency] || URGENCY_RING.normal}`}>
            <div className="flex items-start gap-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1 flex-wrap">
                  <span className={`text-[10px] px-2 py-0.5 rounded ${TYPE_COLORS[a.type]}`}>
                    {TYPE_LABELS[a.type]}
                  </span>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded ${STATUS_BADGE[a.status]}`}>
                    {a.status}
                  </span>
                  {a.urgency !== "normal" && (
                    <span className="text-[10px] text-orange-400 font-medium uppercase">{a.urgency}</span>
                  )}
                  {a.resume_token && (
                    <span className="text-[10px] text-amber-400">⚡ workflow gate</span>
                  )}
                </div>
                <h3 className="text-sm font-medium text-white mb-1">{a.title}</h3>
                {a.description && <p className="text-xs text-gray-500 line-clamp-2 mb-1">{a.description}</p>}

                {/* Entity preview */}
                {a.entity && (
                  <div className="text-[10px] text-gray-600 mt-1">
                    {a.entity_type}: <span className="text-gray-400">{a.entity.title || a.entity.name}</span>
                  </div>
                )}

                <div className="flex gap-3 text-[10px] text-gray-600 mt-1.5">
                  <span>From: {a.requested_by}</span>
                  <span>{new Date(a.created_at).toLocaleString()}</span>
                  {a.decided_by && <span>Decided by: {a.decided_by}</span>}
                  {a.decided_at && <span>at {new Date(a.decided_at).toLocaleString()}</span>}
                </div>
                {a.decision_notes && (
                  <div className="text-[11px] text-gray-500 mt-1 italic">"{a.decision_notes}"</div>
                )}
              </div>

              {/* Quick actions for pending */}
              {a.status === "pending" && (
                <div className="flex gap-1.5 flex-shrink-0">
                  <button onClick={() => handleDecide(a.id, "approved", "")}
                    className="text-[11px] px-3 py-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 transition-colors">
                    ✓
                  </button>
                  <button onClick={() => setDeciding(a)}
                    className="text-[11px] px-3 py-1.5 rounded-lg bg-mc-bg text-gray-400 hover:text-gray-200 hover:bg-white/5 transition-colors">
                    Review
                  </button>
                  <button onClick={() => handleDecide(a.id, "rejected", "")}
                    className="text-[11px] px-3 py-1.5 rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500/20 transition-colors">
                    ✕
                  </button>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {approvals.length === 0 && (
        <div className="text-center py-16">
          <div className="text-2xl mb-2">✓</div>
          <div className="text-gray-500 text-sm">
            {filter === "pending" ? "No pending approvals — you're all caught up" : "No approvals found"}
          </div>
        </div>
      )}

      {deciding && <DecisionModal approval={deciding} onDecide={handleDecide} onClose={() => setDeciding(null)} />}
    </div>
  );
}
