import React, { useState, useEffect } from "react";

const CATEGORIES = ["feature", "bug", "research", "content", "ops", "automation", "general"];
const URGENCY = ["critical", "urgent", "normal", "low", "wishlist"];
const STATUS_COLORS = {
  pending: "bg-amber-500/20 text-amber-400 border-amber-500/30",
  triaging: "bg-blue-500/20 text-blue-400 border-blue-500/30",
  approved: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
  rejected: "bg-red-500/20 text-red-400 border-red-500/30",
  converted: "bg-indigo-500/20 text-indigo-400 border-indigo-500/30",
  deferred: "bg-gray-500/20 text-gray-400 border-gray-500/30",
};
const URGENCY_COLORS = {
  critical: "bg-red-500/20 text-red-400",
  urgent: "bg-orange-500/20 text-orange-400",
  normal: "bg-blue-500/20 text-blue-400",
  low: "bg-gray-500/20 text-gray-400",
  wishlist: "bg-purple-500/20 text-purple-400",
};
const CAT_EMOJI = { feature: "✦", bug: "⚠", research: "◎", content: "✎", ops: "⚙", automation: "↻", general: "●" };

function SubmitForm({ onSubmit, onCancel }) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [category, setCategory] = useState("general");
  const [urgency, setUrgency] = useState("normal");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!title.trim()) return;
    onSubmit({ title: title.trim(), description, category, urgency });
    setTitle(""); setDescription(""); setCategory("general"); setUrgency("normal");
  };

  return (
    <div className="bg-mc-card border border-mc-accent/30 rounded-xl p-6">
      <h3 className="text-base font-semibold text-white mb-4">Submit New Request</h3>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="text-xs text-gray-500 block mb-1">What do you need? *</label>
          <input value={title} onChange={(e) => setTitle(e.target.value)}
            className="w-full bg-mc-bg border border-mc-border rounded-lg px-3 py-2.5 text-sm text-white outline-none focus:border-mc-accent transition-colors"
            placeholder="e.g. Build a customer onboarding flow" autoFocus />
        </div>
        <div>
          <label className="text-xs text-gray-500 block mb-1">Details</label>
          <textarea value={description} onChange={(e) => setDescription(e.target.value)}
            className="w-full bg-mc-bg border border-mc-border rounded-lg px-3 py-2.5 text-sm text-gray-300 outline-none focus:border-mc-accent resize-none h-28 transition-colors"
            placeholder="Describe the goals, constraints, and expected outcomes..." />
        </div>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="text-xs text-gray-500 block mb-1">Category</label>
            <select value={category} onChange={(e) => setCategory(e.target.value)}
              className="w-full bg-mc-bg border border-mc-border rounded-lg px-3 py-2 text-sm text-gray-300">
              {CATEGORIES.map(c => <option key={c} value={c}>{CAT_EMOJI[c]} {c}</option>)}
            </select>
          </div>
          <div>
            <label className="text-xs text-gray-500 block mb-1">Urgency</label>
            <select value={urgency} onChange={(e) => setUrgency(e.target.value)}
              className="w-full bg-mc-bg border border-mc-border rounded-lg px-3 py-2 text-sm text-gray-300">
              {URGENCY.map(u => <option key={u} value={u}>{u}</option>)}
            </select>
          </div>
        </div>
        <div className="flex justify-end gap-3 pt-2">
          <button type="button" onClick={onCancel} className="text-sm px-4 py-2 text-gray-500 hover:text-gray-300 transition-colors">Cancel</button>
          <button type="submit" className="text-sm px-5 py-2 rounded-lg bg-mc-accent text-white hover:bg-mc-accent-hover transition-colors font-medium">Submit Request</button>
        </div>
      </form>
    </div>
  );
}

function TriageModal({ request: req, agents, onTriage, onConvert, onClose }) {
  const [status, setStatus] = useState("approved");
  const [notes, setNotes] = useState("");
  const [owner, setOwner] = useState("");

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-mc-card border border-mc-border rounded-xl p-6 w-full max-w-lg" onClick={e => e.stopPropagation()}>
        <h2 className="text-lg font-semibold text-white mb-1">Triage Request</h2>
        <p className="text-sm text-gray-500 mb-4">{req.title}</p>
        {req.description && <p className="text-xs text-gray-400 mb-4 p-3 bg-mc-bg/50 rounded-lg">{req.description}</p>}

        <div className="space-y-3">
          <div>
            <label className="text-xs text-gray-500 block mb-1">Decision</label>
            <select value={status} onChange={e => setStatus(e.target.value)}
              className="w-full bg-mc-bg border border-mc-border rounded-lg px-3 py-2 text-sm text-gray-300">
              <option value="approved">Approve → Convert to Project</option>
              <option value="deferred">Defer (revisit later)</option>
              <option value="rejected">Reject</option>
            </select>
          </div>
          {status === "approved" && (
            <div>
              <label className="text-xs text-gray-500 block mb-1">Assign to Agent</label>
              <select value={owner} onChange={e => setOwner(e.target.value)}
                className="w-full bg-mc-bg border border-mc-border rounded-lg px-3 py-2 text-sm text-gray-300">
                <option value="">Unassigned</option>
                {agents?.map(a => <option key={a.id} value={a.id}>{a.display_name || a.id}</option>)}
              </select>
            </div>
          )}
          <div>
            <label className="text-xs text-gray-500 block mb-1">Notes</label>
            <textarea value={notes} onChange={e => setNotes(e.target.value)}
              className="w-full bg-mc-bg border border-mc-border rounded-lg px-3 py-2 text-xs text-gray-400 outline-none resize-none h-16"
              placeholder="Reason for decision..." />
          </div>
        </div>

        <div className="flex justify-end gap-3 pt-4">
          <button onClick={onClose} className="text-sm px-4 py-2 text-gray-500 hover:text-gray-300 transition-colors">Cancel</button>
          <button onClick={() => {
            if (status === "approved") {
              onConvert(req.id, { owner_agent: owner || undefined });
            } else {
              onTriage(req.id, { status, review_notes: notes });
            }
            onClose();
          }} className={`text-sm px-5 py-2 rounded-lg font-medium transition-colors ${
            status === "rejected" ? "bg-red-500/20 text-red-400 hover:bg-red-500/30" :
            status === "approved" ? "bg-mc-accent text-white hover:bg-mc-accent-hover" :
            "bg-amber-500/20 text-amber-400 hover:bg-amber-500/30"
          }`}>
            {status === "approved" ? "Approve & Create Project" : status === "rejected" ? "Reject" : "Defer"}
          </button>
        </div>
      </div>
    </div>
  );
}

export default function Requests({ refresh, agents, api: apiClient }) {
  const [requests, setRequests] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [triaging, setTriaging] = useState(null);
  const [filter, setFilter] = useState("pending");

  useEffect(() => {
    loadRequests();
  }, [filter]);

  const loadRequests = async () => {
    try {
      const params = filter === "all" ? {} : { status: filter };
      const data = await apiClient.getRequests(params);
      setRequests(data);
    } catch {}
  };

  const handleSubmit = async (data) => {
    try {
      await apiClient.submitRequest(data);
      setShowForm(false);
      loadRequests();
      refresh();
    } catch (err) { alert(`Failed: ${err.message}`); }
  };

  const handleTriage = async (id, data) => {
    try {
      await apiClient.triageRequest(id, data);
      loadRequests();
      refresh();
    } catch (err) { alert(`Failed: ${err.message}`); }
  };

  const handleConvert = async (id, data) => {
    try {
      await apiClient.convertRequest(id, data);
      loadRequests();
      refresh();
    } catch (err) { alert(`Failed: ${err.message}`); }
  };

  const pendingCount = requests.filter(r => r.status === "pending" || r.status === "triaging").length;

  return (
    <div className="space-y-5 max-w-[1100px]">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <select value={filter} onChange={e => setFilter(e.target.value)}
            className="text-xs bg-mc-card border border-mc-border rounded-lg px-3 py-2 text-gray-300">
            <option value="pending">Pending</option>
            <option value="triaging">Triaging</option>
            <option value="approved">Approved</option>
            <option value="converted">Converted</option>
            <option value="rejected">Rejected</option>
            <option value="deferred">Deferred</option>
            <option value="all">All</option>
          </select>
          <span className="text-xs text-gray-500">{requests.length} requests</span>
          {pendingCount > 0 && filter !== "pending" && (
            <span className="text-[10px] px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-400">{pendingCount} pending</span>
          )}
        </div>
        <button onClick={() => setShowForm(!showForm)}
          className="text-sm px-4 py-2 rounded-lg bg-mc-accent text-white hover:bg-mc-accent-hover transition-colors">
          + New Request
        </button>
      </div>

      {/* Submit form */}
      {showForm && <SubmitForm onSubmit={handleSubmit} onCancel={() => setShowForm(false)} />}

      {/* Requests list */}
      <div className="space-y-2">
        {requests.map(r => (
          <div key={r.id} className="bg-mc-card border border-mc-border rounded-xl p-4 card-hover">
            <div className="flex items-start gap-4">
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-xs text-gray-600">{CAT_EMOJI[r.category] || "●"}</span>
                  <h3 className="text-sm font-medium text-white truncate">{r.title}</h3>
                  <span className={`text-[10px] px-2 py-0.5 rounded-full border ${STATUS_COLORS[r.status]}`}>{r.status}</span>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded ${URGENCY_COLORS[r.urgency]}`}>{r.urgency}</span>
                </div>
                {r.description && <p className="text-xs text-gray-500 line-clamp-2 mb-1.5">{r.description}</p>}
                <div className="flex gap-3 text-[10px] text-gray-600">
                  <span>From: {r.requester}</span>
                  <span>{r.category}</span>
                  <span>{new Date(r.created_at).toLocaleDateString()}</span>
                  {r.reviewer && <span>Reviewed by: {r.reviewer}</span>}
                  {r.converted_project_id && <span>→ Project: {r.converted_project_id}</span>}
                </div>
                {r.review_notes && <div className="text-[11px] text-gray-500 mt-1.5 italic">"{r.review_notes}"</div>}
              </div>

              {/* Actions */}
              {(r.status === "pending" || r.status === "triaging") && (
                <button onClick={() => setTriaging(r)}
                  className="text-xs px-3 py-1.5 rounded-lg bg-mc-accent/10 text-mc-accent hover:bg-mc-accent/20 transition-colors flex-shrink-0">
                  Triage
                </button>
              )}
            </div>
          </div>
        ))}
      </div>

      {requests.length === 0 && !showForm && (
        <div className="text-center py-12">
          <div className="text-gray-600 text-sm mb-2">
            {filter === "pending" ? "No pending requests" : "No requests found"}
          </div>
          <button onClick={() => setShowForm(true)} className="text-xs text-mc-accent hover:text-mc-accent-hover">
            Submit a new request →
          </button>
        </div>
      )}

      {triaging && (
        <TriageModal request={triaging} agents={agents} onTriage={handleTriage} onConvert={handleConvert} onClose={() => setTriaging(null)} />
      )}
    </div>
  );
}
