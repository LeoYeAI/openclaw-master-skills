const BASE = "/api";

async function request(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ error: res.statusText }));
    throw new Error(err.error || `HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  // Projects
  getProjects: (params) => request(`/projects?${new URLSearchParams(params || {})}`),
  getProject: (id) => request(`/projects/${id}`),
  createProject: (data) => request("/projects", { method: "POST", body: JSON.stringify(data) }),
  updateProject: (id, data) => request(`/projects/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteProject: (id) => request(`/projects/${id}`, { method: "DELETE" }),

  // Tasks
  getTasks: (params) => request(`/tasks?${new URLSearchParams(params || {})}`),
  getTask: (id) => request(`/tasks/${id}`),
  createTask: (data) => request("/tasks", { method: "POST", body: JSON.stringify(data) }),
  updateTask: (id, data) => request(`/tasks/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  moveTask: (id, toStage, actor) =>
    request(`/tasks/${id}/move`, { method: "POST", body: JSON.stringify({ to_stage: toStage, actor }) }),
  deleteTask: (id) => request(`/tasks/${id}`, { method: "DELETE" }),
  getPipeline: (projectId) =>
    request(`/tasks/pipeline/overview${projectId ? `?project_id=${projectId}` : ""}`),

  // Agents
  getAgents: () => request("/agents"),
  upsertAgent: (id, data) => request(`/agents/${id}`, { method: "PUT", body: JSON.stringify(data) }),

  // Events / Stats
  getStats: () => request("/events/stats"),
  getActivity: (params) => request(`/events/activity?${new URLSearchParams(params || {})}`),

  // Health
  getHealth: () => request("/health"),

  // ── NEW: Project Requests ───────────────────────────
  getRequests: (params) => request(`/requests?${new URLSearchParams(params || {})}`),
  getRequest: (id) => request(`/requests/${id}`),
  submitRequest: (data) => request("/requests", { method: "POST", body: JSON.stringify(data) }),
  triageRequest: (id, data) => request(`/requests/${id}/triage`, { method: "POST", body: JSON.stringify(data) }),
  convertRequest: (id, data) => request(`/requests/${id}/convert`, { method: "POST", body: JSON.stringify(data) }),
  deleteRequest: (id) => request(`/requests/${id}`, { method: "DELETE" }),
  getRequestStats: () => request("/requests/stats/summary"),

  // ── NEW: Approvals ──────────────────────────────────
  getApprovals: (params) => request(`/approvals?${new URLSearchParams(params || {})}`),
  getApproval: (id) => request(`/approvals/${id}`),
  createApproval: (data) => request("/approvals", { method: "POST", body: JSON.stringify(data) }),
  decideApproval: (id, decision, notes, decidedBy) =>
    request(`/approvals/${id}/decide`, { method: "POST", body: JSON.stringify({ decision, notes, decided_by: decidedBy }) }),
  getPendingCount: () => request("/approvals/count/pending"),

  // ── NEW: Costs ──────────────────────────────────────
  getCostSummary: (days) => request(`/costs/summary?days=${days || 30}`),
  getCostEntries: (params) => request(`/costs/entries?${new URLSearchParams(params || {})}`),
  recordCost: (data) => request("/costs", { method: "POST", body: JSON.stringify(data) }),

  // ── NEW: Reviews ────────────────────────────────────
  getReviews: (params) => request(`/reviews?${new URLSearchParams(params || {})}`),
  getReview: (id) => request(`/reviews/${id}`),
  createReview: (data) => request("/reviews", { method: "POST", body: JSON.stringify(data) }),
  addReviewComment: (id, content, author) =>
    request(`/reviews/${id}/comment`, { method: "POST", body: JSON.stringify({ content, author }) }),
  decideReview: (id, decision, notes, qualityScore, reviewer) =>
    request(`/reviews/${id}/decide`, { method: "POST", body: JSON.stringify({ decision, notes, quality_score: qualityScore, reviewer }) }),
  updateChecklist: (id, checklist) =>
    request(`/reviews/${id}/checklist`, { method: "PATCH", body: JSON.stringify({ checklist }) }),
  getReviewStats: () => request("/reviews/stats/summary"),

  // ── Unified Inbox ───────────────────────────────────
  getInbox: (params) => request(`/inbox?${new URLSearchParams(params || {})}`),
  getInboxCounts: () => request("/inbox/counts"),

  // ── Library ─────────────────────────────────────────
  getCollections: () => request("/library/collections"),
  createCollection: (data) => request("/library/collections", { method: "POST", body: JSON.stringify(data) }),
  updateCollection: (id, data) => request(`/library/collections/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteCollection: (id) => request(`/library/collections/${id}`, { method: "DELETE" }),
  getDocuments: (params) => request(`/library/documents?${new URLSearchParams(params || {})}`),
  getDocument: (id) => request(`/library/documents/${id}`),
  createDocument: (data) => request("/library/documents", { method: "POST", body: JSON.stringify(data) }),
  updateDocument: (id, data) => request(`/library/documents/${id}`, { method: "PATCH", body: JSON.stringify(data) }),
  deleteDocument: (id) => request(`/library/documents/${id}`, { method: "DELETE" }),
  searchLibrary: (q) => request(`/library/search?q=${encodeURIComponent(q)}`),
  getLibraryTags: () => request("/library/tags"),
  createLibraryTag: (data) => request("/library/tags", { method: "POST", body: JSON.stringify(data) }),
  getLibraryStats: () => request("/library/stats"),
  getDocVersion: (id, v) => request(`/library/documents/${id}/versions/${v}`),
};
