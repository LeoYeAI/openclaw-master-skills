import React, { useState } from "react";

const STATUS_OPTIONS = ["draft", "approved", "active", "paused", "completed", "archived"];
const STATUS_COLORS = {
  draft: "bg-gray-500/20 text-gray-400 border-gray-500/30",
  approved: "bg-blue-500/20 text-blue-400 border-blue-500/30",
  active: "bg-emerald-500/20 text-emerald-400 border-emerald-500/30",
  paused: "bg-amber-500/20 text-amber-400 border-amber-500/30",
  completed: "bg-green-500/20 text-green-400 border-green-500/30",
  archived: "bg-gray-500/20 text-gray-500 border-gray-500/30",
};

function CreateProjectModal({ agents, onSubmit, onClose }) {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState("medium");
  const [owner, setOwner] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!name.trim()) return;
    onSubmit({ name: name.trim(), description, priority, owner_agent: owner || undefined });
  };

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-mc-card border border-mc-border rounded-xl p-6 w-full max-w-lg" onClick={(e) => e.stopPropagation()}>
        <h2 className="text-lg font-semibold text-white mb-4">New Project</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="text-xs text-gray-500 block mb-1">Project Name *</label>
            <input
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full bg-mc-bg border border-mc-border rounded-lg px-3 py-2 text-sm text-white outline-none focus:border-mc-accent"
              placeholder="e.g. Website Redesign"
              autoFocus
            />
          </div>
          <div>
            <label className="text-xs text-gray-500 block mb-1">Description</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full bg-mc-bg border border-mc-border rounded-lg px-3 py-2 text-sm text-gray-300 outline-none focus:border-mc-accent resize-none h-24"
              placeholder="What should be accomplished?"
            />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs text-gray-500 block mb-1">Priority</label>
              <select
                value={priority}
                onChange={(e) => setPriority(e.target.value)}
                className="w-full bg-mc-bg border border-mc-border rounded-lg px-3 py-2 text-sm text-gray-300"
              >
                <option value="low">Low</option>
                <option value="medium">Medium</option>
                <option value="high">High</option>
                <option value="critical">Critical</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-gray-500 block mb-1">Owner Agent</label>
              <select
                value={owner}
                onChange={(e) => setOwner(e.target.value)}
                className="w-full bg-mc-bg border border-mc-border rounded-lg px-3 py-2 text-sm text-gray-300"
              >
                <option value="">Unassigned</option>
                {agents?.map((a) => (
                  <option key={a.id} value={a.id}>{a.display_name || a.id}</option>
                ))}
              </select>
            </div>
          </div>
          <div className="flex justify-end gap-3 pt-2">
            <button type="button" onClick={onClose} className="text-sm px-4 py-2 text-gray-500 hover:text-gray-300 transition-colors">
              Cancel
            </button>
            <button type="submit" className="text-sm px-4 py-2 rounded-lg bg-mc-accent text-white hover:bg-mc-accent-hover transition-colors">
              Create Project
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default function Projects({ projects, agents, refresh, api: apiClient }) {
  const [showCreate, setShowCreate] = useState(false);
  const [filter, setFilter] = useState("all");
  const [selected, setSelected] = useState(null);

  const handleCreate = async (data) => {
    try {
      await apiClient.createProject(data);
      setShowCreate(false);
      refresh();
    } catch (err) {
      alert(`Failed: ${err.message}`);
    }
  };

  const handleStatusChange = async (id, status) => {
    try {
      await apiClient.updateProject(id, { status });
      refresh();
    } catch (err) {
      alert(`Failed: ${err.message}`);
    }
  };

  const handleDelete = async (id) => {
    if (!confirm("Delete this project and all its tasks?")) return;
    try {
      await apiClient.deleteProject(id);
      setSelected(null);
      refresh();
    } catch (err) {
      alert(`Failed: ${err.message}`);
    }
  };

  const filtered = filter === "all" ? projects : projects?.filter((p) => p.status === filter);

  return (
    <div className="space-y-4 max-w-[1200px]">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <select
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="text-xs bg-mc-card border border-mc-border rounded-lg px-3 py-2 text-gray-300"
          >
            <option value="all">All statuses</option>
            {STATUS_OPTIONS.map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>
          <span className="text-xs text-gray-500">{filtered?.length || 0} projects</span>
        </div>
        <button
          onClick={() => setShowCreate(true)}
          className="text-sm px-4 py-2 rounded-lg bg-mc-accent text-white hover:bg-mc-accent-hover transition-colors"
        >
          + New Project
        </button>
      </div>

      {/* Project list */}
      <div className="space-y-3">
        {filtered?.map((p) => {
          const totalTasks = Object.values(p.task_counts || {}).reduce((s, n) => s + n, 0);
          const doneTasks = p.task_counts?.done || 0;
          const progress = totalTasks > 0 ? Math.round((doneTasks / totalTasks) * 100) : 0;

          return (
            <div key={p.id} className="bg-mc-card border border-mc-border rounded-xl p-5 card-hover">
              <div className="flex items-start gap-4">
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-3 mb-1">
                    <h3 className="text-base font-semibold text-white truncate">{p.name}</h3>
                    <span className={`text-[10px] px-2 py-0.5 rounded-full border ${STATUS_COLORS[p.status]}`}>
                      {p.status}
                    </span>
                  </div>
                  {p.description && (
                    <p className="text-xs text-gray-500 mb-3 line-clamp-2">{p.description}</p>
                  )}

                  {/* Progress bar */}
                  <div className="flex items-center gap-3 mb-2">
                    <div className="flex-1 h-1.5 bg-mc-border rounded-full overflow-hidden">
                      <div
                        className="h-full bg-mc-accent rounded-full transition-all"
                        style={{ width: `${progress}%` }}
                      />
                    </div>
                    <span className="text-[11px] text-gray-500">{progress}%</span>
                  </div>

                  <div className="flex gap-4 text-[11px] text-gray-600">
                    <span>{totalTasks} tasks</span>
                    {p.owner_agent && <span>Agent: {p.owner_agent}</span>}
                    <span>Created: {new Date(p.created_at).toLocaleDateString()}</span>
                    {p.completed_at && <span>Completed: {new Date(p.completed_at).toLocaleDateString()}</span>}
                  </div>
                </div>

                {/* Actions */}
                <div className="flex flex-col gap-1.5 flex-shrink-0">
                  <select
                    value={p.status}
                    onChange={(e) => handleStatusChange(p.id, e.target.value)}
                    className="text-[11px] bg-mc-bg border border-mc-border rounded px-2 py-1 text-gray-400"
                  >
                    {STATUS_OPTIONS.map((s) => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                  <button
                    onClick={() => handleDelete(p.id)}
                    className="text-[11px] px-2 py-1 rounded text-red-400/50 hover:text-red-400 hover:bg-red-500/10 transition-colors"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {filtered?.length === 0 && (
        <div className="text-center py-12">
          <div className="text-gray-600 text-sm mb-2">No projects found</div>
          <button
            onClick={() => setShowCreate(true)}
            className="text-xs text-mc-accent hover:text-mc-accent-hover"
          >
            Create your first project →
          </button>
        </div>
      )}

      {showCreate && (
        <CreateProjectModal agents={agents} onSubmit={handleCreate} onClose={() => setShowCreate(false)} />
      )}
    </div>
  );
}
