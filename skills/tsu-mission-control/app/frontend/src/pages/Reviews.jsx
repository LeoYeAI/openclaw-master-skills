import React, { useState, useEffect } from "react";

const STATUS_BADGE = {
  pending: "bg-amber-500/20 text-amber-400",
  in_review: "bg-blue-500/20 text-blue-400",
  approved: "bg-emerald-500/20 text-emerald-400",
  changes_requested: "bg-orange-500/20 text-orange-400",
  rejected: "bg-red-500/20 text-red-400",
};
const PRI_C = {
  critical: "bg-red-500/20 text-red-400",
  high: "bg-orange-500/20 text-orange-400",
  medium: "bg-blue-500/20 text-blue-400",
  low: "bg-gray-500/20 text-gray-400",
};

function Stars({ value, onChange, readonly }) {
  return (
    <div className="flex gap-1">
      {[1, 2, 3, 4, 5].map(n => (
        <button key={n} type="button"
          onClick={() => !readonly && onChange?.(n)}
          className={`text-lg transition-colors ${
            n <= (value || 0)
              ? "text-amber-400"
              : readonly ? "text-gray-700" : "text-gray-600 hover:text-amber-300"
          }`}
          disabled={readonly}
        >
          ★
        </button>
      ))}
    </div>
  );
}

function ReviewDetail({ review, onDecide, onComment, onClose }) {
  const [decision, setDecision] = useState("");
  const [notes, setNotes] = useState("");
  const [score, setScore] = useState(review.quality_score || 0);
  const [comment, setComment] = useState("");
  const [checklist, setChecklist] = useState(
    JSON.parse(review.checklist || "[]")
  );

  const deliverables = JSON.parse(review.deliverables || "[]");
  const prevRounds = review.previous_rounds || [];
  const comments = review.comments || [];
  const taskActivity = review.task_activity || [];

  const handleDecide = (d) => {
    onDecide(review.id, d, notes, score);
    onClose();
  };

  const handleComment = () => {
    if (!comment.trim()) return;
    onComment(review.id, comment.trim());
    setComment("");
  };

  const toggleCheck = (i) => {
    const next = [...checklist];
    next[i] = { ...next[i], checked: !next[i].checked };
    setChecklist(next);
  };

  const checkProgress = checklist.length > 0
    ? `${checklist.filter(c => c.checked).length}/${checklist.length}`
    : null;

  return (
    <div className="fixed inset-0 bg-black/70 flex items-start justify-center z-50 overflow-y-auto py-8" onClick={onClose}>
      <div className="bg-mc-card border border-mc-border rounded-xl w-full max-w-2xl mx-4" onClick={e => e.stopPropagation()}>
        {/* Header */}
        <div className="p-5 border-b border-mc-border">
          <div className="flex items-center gap-2 mb-2 flex-wrap">
            <span className={`text-[10px] px-2 py-0.5 rounded ${STATUS_BADGE[review.status]}`}>{review.status.replace("_", " ")}</span>
            {review.task_priority && (
              <span className={`text-[10px] px-1.5 py-0.5 rounded ${PRI_C[review.task_priority]}`}>{review.task_priority}</span>
            )}
            <span className="text-[10px] text-gray-600">Round {review.round}</span>
            {review.project_name && (
              <span className="text-[10px] text-gray-600">· {review.project_name}</span>
            )}
          </div>
          <h2 className="text-base font-semibold text-white">{review.task_title}</h2>
          {review.task_description && (
            <p className="text-xs text-gray-500 mt-1">{review.task_description}</p>
          )}
          <div className="flex gap-4 text-[10px] text-gray-600 mt-2">
            <span>Agent: {review.submitted_by || review.assigned_agent || "—"}</span>
            <span>Submitted: {new Date(review.submitted_at).toLocaleString()}</span>
            {review.task_cost && <span>Cost: ${(review.task_cost.cost || 0).toFixed(2)} · {((review.task_cost.tokens || 0) / 1000).toFixed(0)}K tokens</span>}
          </div>
        </div>

        {/* Body */}
        <div className="p-5 space-y-5 max-h-[60vh] overflow-y-auto">
          {/* Work summary */}
          {review.work_summary && (
            <div>
              <h4 className="text-xs font-medium text-gray-400 mb-1.5">Work Summary</h4>
              <div className="text-sm text-gray-300 p-3 rounded-lg bg-mc-bg/50 border border-mc-border/50 leading-relaxed">
                {review.work_summary}
              </div>
            </div>
          )}

          {/* Deliverables */}
          {deliverables.length > 0 && (
            <div>
              <h4 className="text-xs font-medium text-gray-400 mb-1.5">Deliverables ({deliverables.length})</h4>
              <div className="space-y-1.5">
                {deliverables.map((d, i) => (
                  <div key={i} className="flex items-center gap-3 p-2.5 rounded-lg bg-mc-bg/50 border border-mc-border/50">
                    <div className="w-8 h-8 rounded bg-mc-accent/10 flex items-center justify-center text-mc-accent text-[10px] font-bold flex-shrink-0">
                      {d.type === "file" ? "📄" : d.type === "code" ? "💻" : d.type === "doc" ? "📝" : "📦"}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="text-xs text-white truncate">{d.name}</div>
                      {d.path && <div className="text-[10px] text-gray-600 font-mono truncate">{d.path}</div>}
                      {d.summary && <div className="text-[10px] text-gray-500 mt-0.5">{d.summary}</div>}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Checklist */}
          {checklist.length > 0 && (
            <div>
              <div className="flex items-center justify-between mb-1.5">
                <h4 className="text-xs font-medium text-gray-400">Review Checklist</h4>
                {checkProgress && <span className="text-[10px] text-gray-500">{checkProgress}</span>}
              </div>
              <div className="space-y-1">
                {checklist.map((item, i) => (
                  <label key={i} className="flex items-center gap-2.5 p-2 rounded-lg hover:bg-white/[0.02] cursor-pointer transition-colors">
                    <input type="checkbox" checked={item.checked || false} onChange={() => toggleCheck(i)}
                      className="w-3.5 h-3.5 rounded border-gray-600 text-mc-accent focus:ring-0 focus:ring-offset-0 cursor-pointer" />
                    <span className={`text-xs ${item.checked ? "text-gray-500 line-through" : "text-gray-300"}`}>{item.label}</span>
                  </label>
                ))}
              </div>
            </div>
          )}

          {/* Previous rounds */}
          {prevRounds.length > 0 && (
            <div>
              <h4 className="text-xs font-medium text-gray-400 mb-1.5">Previous Rounds</h4>
              <div className="space-y-1">
                {prevRounds.map(r => (
                  <div key={r.id} className="flex items-center gap-3 text-[11px] p-2 rounded-lg bg-mc-bg/30">
                    <span className="text-gray-500">Round {r.round}</span>
                    <span className={`px-1.5 py-0.5 rounded ${STATUS_BADGE[r.status]}`}>{r.status.replace("_", " ")}</span>
                    {r.quality_score && <span className="text-amber-400">{"★".repeat(r.quality_score)}</span>}
                    {r.decision_notes && <span className="text-gray-500 truncate flex-1">— {r.decision_notes}</span>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Comments */}
          <div>
            <h4 className="text-xs font-medium text-gray-400 mb-1.5">Discussion ({comments.length})</h4>
            <div className="space-y-2 mb-3">
              {comments.length === 0 && (
                <div className="text-[11px] text-gray-600 py-2">No comments yet</div>
              )}
              {comments.map(c => (
                <div key={c.id} className="p-2.5 rounded-lg bg-mc-bg/40 border border-mc-border/30">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-[10px] font-medium text-gray-400">{c.author}</span>
                    <span className="text-[9px] text-gray-700">{new Date(c.created_at).toLocaleString()}</span>
                    {c.deliverable_ref && <span className="text-[9px] text-mc-accent">re: {c.deliverable_ref}</span>}
                  </div>
                  <div className="text-xs text-gray-300 leading-relaxed">{c.content}</div>
                </div>
              ))}
            </div>
            <div className="flex gap-2">
              <input value={comment} onChange={e => setComment(e.target.value)}
                onKeyDown={e => e.key === "Enter" && handleComment()}
                placeholder="Add a comment..."
                className="flex-1 bg-mc-bg border border-mc-border rounded-lg px-3 py-2 text-xs text-white outline-none focus:border-mc-accent transition-colors" />
              <button onClick={handleComment}
                className="text-xs px-3 py-2 rounded-lg bg-mc-accent/10 text-mc-accent hover:bg-mc-accent/20 transition-colors">
                Send
              </button>
            </div>
          </div>
        </div>

        {/* Decision footer */}
        {(review.status === "pending" || review.status === "in_review") && (
          <div className="p-5 border-t border-mc-border space-y-3">
            <div className="flex items-center gap-4">
              <div>
                <div className="text-[10px] text-gray-500 mb-1">Quality Score</div>
                <Stars value={score} onChange={setScore} />
              </div>
              <div className="flex-1">
                <div className="text-[10px] text-gray-500 mb-1">Decision Notes</div>
                <input value={notes} onChange={e => setNotes(e.target.value)}
                  placeholder="Feedback for the agent..."
                  className="w-full bg-mc-bg border border-mc-border rounded-lg px-3 py-2 text-xs text-white outline-none focus:border-mc-accent" />
              </div>
            </div>
            <div className="flex justify-between">
              <button onClick={onClose} className="text-xs px-4 py-2 text-gray-500 hover:text-gray-300 transition-colors">Close</button>
              <div className="flex gap-2">
                <button onClick={() => handleDecide("rejected")}
                  className="text-xs px-4 py-2 rounded-lg bg-red-500/10 text-red-400 hover:bg-red-500/20 transition-colors font-medium">
                  Reject
                </button>
                <button onClick={() => handleDecide("changes_requested")}
                  className="text-xs px-4 py-2 rounded-lg bg-orange-500/10 text-orange-400 hover:bg-orange-500/20 transition-colors font-medium">
                  Request Changes
                </button>
                <button onClick={() => handleDecide("approved")}
                  className="text-xs px-5 py-2 rounded-lg bg-emerald-500/15 text-emerald-400 hover:bg-emerald-500/25 transition-colors font-medium">
                  ✓ Approve
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Read-only footer for decided reviews */}
        {review.status !== "pending" && review.status !== "in_review" && (
          <div className="p-5 border-t border-mc-border flex items-center justify-between">
            <div className="flex items-center gap-3">
              {review.quality_score && <Stars value={review.quality_score} readonly />}
              {review.decision_notes && <span className="text-xs text-gray-500 italic">"{review.decision_notes}"</span>}
            </div>
            <button onClick={onClose} className="text-xs px-4 py-2 text-gray-500 hover:text-gray-300 transition-colors">Close</button>
          </div>
        )}
      </div>
    </div>
  );
}

export default function Reviews({ projects, refresh, api: apiClient }) {
  const [reviews, setReviews] = useState([]);
  const [filter, setFilter] = useState("pending");
  const [selected, setSelected] = useState(null);
  const [stats, setStats] = useState(null);

  useEffect(() => { loadReviews(); loadStats(); }, [filter]);

  const loadReviews = async () => {
    try {
      const data = await apiClient.getReviews({ status: filter });
      setReviews(data);
    } catch {}
  };

  const loadStats = async () => {
    try {
      const data = await apiClient.getReviewStats();
      setStats(data);
    } catch {}
  };

  const openReview = async (id) => {
    try {
      const detail = await apiClient.getReview(id);
      setSelected(detail);
    } catch (err) { alert(`Failed to load: ${err.message}`); }
  };

  const handleDecide = async (id, decision, notes, score) => {
    try {
      await apiClient.decideReview(id, decision, notes, score, "user");
      loadReviews();
      loadStats();
      refresh();
    } catch (err) { alert(`Failed: ${err.message}`); }
  };

  const handleComment = async (id, content) => {
    try {
      const comments = await apiClient.addReviewComment(id, content, "user");
      if (selected && selected.id === id) {
        setSelected(prev => ({ ...prev, comments }));
      }
    } catch (err) { alert(`Failed: ${err.message}`); }
  };

  const pendingCount = reviews.filter(r => r.status === "pending" || r.status === "in_review").length;

  return (
    <div className="space-y-5 max-w-[1100px]">
      {/* Stats bar */}
      {stats && (
        <div className="flex gap-4 flex-wrap">
          {[
            { l: "Pending", v: stats.pending, c: "text-amber-400" },
            { l: "Approved", v: stats.approved, c: "text-emerald-400" },
            { l: "Changes Req.", v: stats.changesRequested, c: "text-orange-400" },
            { l: "Avg Score", v: stats.avgScore ? `${stats.avgScore} ★` : "—", c: "text-amber-400" },
            { l: "Avg Rounds", v: stats.avgRounds || "—", c: "text-gray-400" },
          ].map(s => (
            <div key={s.l} className="text-xs text-gray-500">
              {s.l}: <span className={`font-medium ${s.c}`}>{s.v}</span>
            </div>
          ))}
        </div>
      )}

      {/* Filters */}
      <div className="flex items-center gap-3">
        <select value={filter} onChange={e => setFilter(e.target.value)}
          className="text-xs bg-mc-card border border-mc-border rounded-lg px-3 py-2 text-gray-300">
          <option value="pending">Pending Review</option>
          <option value="in_review">In Review</option>
          <option value="approved">Approved</option>
          <option value="changes_requested">Changes Requested</option>
          <option value="rejected">Rejected</option>
          <option value="all">All</option>
        </select>
        <span className="text-xs text-gray-500">{reviews.length} reviews</span>
      </div>

      {/* Review list */}
      <div className="space-y-2">
        {reviews.map(r => {
          const deliverables = JSON.parse(r.deliverables || "[]");
          return (
            <div key={r.id}
              onClick={() => openReview(r.id)}
              className="bg-mc-card border border-mc-border rounded-xl p-4 card-hover cursor-pointer">
              <div className="flex items-start gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 mb-1 flex-wrap">
                    <span className={`text-[10px] px-2 py-0.5 rounded ${STATUS_BADGE[r.status]}`}>
                      {r.status.replace("_", " ")}
                    </span>
                    {r.task_priority && (
                      <span className={`text-[10px] px-1.5 py-0.5 rounded ${PRI_C[r.task_priority]}`}>
                        {r.task_priority}
                      </span>
                    )}
                    <span className="text-[10px] text-gray-600">Round {r.round}</span>
                    {deliverables.length > 0 && (
                      <span className="text-[10px] text-gray-600">{deliverables.length} deliverable{deliverables.length > 1 ? "s" : ""}</span>
                    )}
                  </div>
                  <h3 className="text-sm font-medium text-white mb-0.5">{r.task_title}</h3>
                  {r.work_summary && <p className="text-[11px] text-gray-500 line-clamp-2">{r.work_summary}</p>}
                  <div className="flex gap-3 text-[10px] text-gray-600 mt-1.5">
                    <span>Agent: {r.submitted_by || r.assigned_agent || "—"}</span>
                    {r.project_name && <span>Project: {r.project_name}</span>}
                    <span>{new Date(r.submitted_at).toLocaleString()}</span>
                    {r.quality_score && <span className="text-amber-400">{"★".repeat(r.quality_score)}</span>}
                  </div>
                </div>

                {/* Quick actions */}
                {(r.status === "pending" || r.status === "in_review") && (
                  <div className="flex gap-1.5 flex-shrink-0" onClick={e => e.stopPropagation()}>
                    <button onClick={() => handleDecide(r.id, "approved", "", null)}
                      className="text-[11px] px-2.5 py-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 transition-colors">
                      ✓
                    </button>
                    <button onClick={() => openReview(r.id)}
                      className="text-[11px] px-2.5 py-1.5 rounded-lg bg-mc-bg text-gray-400 hover:text-gray-200 hover:bg-white/5 transition-colors">
                      Review
                    </button>
                    <button onClick={() => handleDecide(r.id, "changes_requested", "", null)}
                      className="text-[11px] px-2.5 py-1.5 rounded-lg bg-orange-500/10 text-orange-400 hover:bg-orange-500/20 transition-colors">
                      ↩
                    </button>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {reviews.length === 0 && (
        <div className="text-center py-16">
          <div className="text-2xl mb-2">✓</div>
          <div className="text-gray-500 text-sm">
            {filter === "pending" ? "No reviews pending — all caught up" : "No reviews found"}
          </div>
          <div className="text-xs text-gray-700 mt-2 max-w-sm mx-auto">
            Reviews are created automatically when agents submit tasks for review via the pipeline or the lifecycle hook.
          </div>
        </div>
      )}

      {selected && (
        <ReviewDetail
          review={selected}
          onDecide={handleDecide}
          onComment={handleComment}
          onClose={() => setSelected(null)}
        />
      )}
    </div>
  );
}
