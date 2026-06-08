import React, { useState, useRef } from "react";

const STAGES = [
  { id: "backlog", label: "Backlog", color: "border-gray-600", bg: "bg-gray-600/10" },
  { id: "todo", label: "To Do", color: "border-blue-500", bg: "bg-blue-500/10" },
  { id: "doing", label: "In Progress", color: "border-amber-500", bg: "bg-amber-500/10" },
  { id: "review", label: "Review", color: "border-purple-500", bg: "bg-purple-500/10" },
  { id: "done", label: "Done", color: "border-emerald-500", bg: "bg-emerald-500/10" },
];

const PRIORITY_BADGES = {
  critical: "bg-red-500/20 text-red-400",
  high: "bg-orange-500/20 text-orange-400",
  medium: "bg-blue-500/20 text-blue-400",
  low: "bg-gray-500/20 text-gray-400",
};

const VALID_TRANSITIONS = {
  backlog: ["todo"],
  todo: ["doing", "backlog"],
  doing: ["review", "todo"],
  review: ["done", "doing"],
  done: [],
};

function TaskCard({ task, onMove, onEdit }) {
  const [expanded, setExpanded] = useState(false);
  const nextStages = VALID_TRANSITIONS[task.pipeline_stage] || [];

  return (
    <div className="bg-mc-card border border-mc-border rounded-lg p-3 card-hover cursor-pointer group">
      <div onClick={() => setExpanded(!expanded)}>
        <div className="flex items-start justify-between gap-2">
          <h4 className="text-sm font-medium text-white leading-snug">{task.title}</h4>
          <span className={`text-[10px] px-1.5 py-0.5 rounded flex-shrink-0 ${PRIORITY_BADGES[task.priority] || PRIORITY_BADGES.medium}`}>
            {task.priority}
          </span>
        </div>
        {task.assigned_agent && (
          <div className="text-[11px] text-gray-500 mt-1.5 flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 flex-shrink-0" />
            {task.assigned_agent}
          </div>
        )}
        {task.description && !expanded && (
          <div className="text-[11px] text-gray-600 mt-1 line-clamp-2">{task.description}</div>
        )}
      </div>

      {expanded && (
        <div className="mt-3 pt-3 border-t border-mc-border/50 space-y-2">
          {task.description && (
            <div className="text-xs text-gray-400">{task.description}</div>
          )}
          <div className="text-[10px] text-gray-600 space-y-0.5">
            <div>ID: <span style={{ fontFamily: "var(--font-mono)" }}>{task.id}</span></div>
            {task.project_id && <div>Project: {task.project_id}</div>}
            {task.started_at && <div>Started: {new Date(task.started_at).toLocaleDateString()}</div>}
            {task.estimated_mins && <div>Est: {task.estimated_mins}m</div>}
          </div>

          {nextStages.length > 0 && (
            <div className="flex gap-1.5 pt-1">
              {nextStages.map((stage) => (
                <button
                  key={stage}
                  onClick={(e) => { e.stopPropagation(); onMove(task.id, stage); }}
                  className="text-[10px] px-2 py-1 rounded bg-mc-accent/10 text-mc-accent hover:bg-mc-accent/20 transition-colors"
                >
                  → {stage}
                </button>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function NewTaskForm({ stage, projects, onSubmit, onCancel }) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState("medium");
  const [projectId, setProjectId] = useState("");
  const [assignedAgent, setAssignedAgent] = useState("");

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!title.trim()) return;
    onSubmit({
      title: title.trim(),
      description,
      priority,
      project_id: projectId || undefined,
      assigned_agent: assignedAgent || undefined,
      pipeline_stage: stage,
    });
    setTitle("");
    setDescription("");
  };

  return (
    <form onSubmit={handleSubmit} className="bg-mc-bg/80 border border-mc-accent/30 rounded-lg p-3 space-y-2">
      <input
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        placeholder="Task title..."
        className="w-full bg-transparent text-sm text-white placeholder-gray-600 outline-none"
        autoFocus
      />
      <textarea
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        placeholder="Description (optional)"
        className="w-full bg-transparent text-xs text-gray-400 placeholder-gray-700 outline-none resize-none h-12"
      />
      <div className="flex gap-2">
        <select
          value={priority}
          onChange={(e) => setPriority(e.target.value)}
          className="text-[11px] bg-mc-card border border-mc-border rounded px-2 py-1 text-gray-300"
        >
          <option value="low">Low</option>
          <option value="medium">Medium</option>
          <option value="high">High</option>
          <option value="critical">Critical</option>
        </select>
        {projects?.length > 0 && (
          <select
            value={projectId}
            onChange={(e) => setProjectId(e.target.value)}
            className="text-[11px] bg-mc-card border border-mc-border rounded px-2 py-1 text-gray-300 flex-1 min-w-0"
          >
            <option value="">No project</option>
            {projects.map((p) => (
              <option key={p.id} value={p.id}>{p.name}</option>
            ))}
          </select>
        )}
      </div>
      <div className="flex gap-2 pt-1">
        <button type="submit" className="text-[11px] px-3 py-1 rounded bg-mc-accent text-white hover:bg-mc-accent-hover transition-colors">
          Create
        </button>
        <button type="button" onClick={onCancel} className="text-[11px] px-3 py-1 rounded text-gray-500 hover:text-gray-300 transition-colors">
          Cancel
        </button>
      </div>
    </form>
  );
}

export default function Pipeline({ pipeline, projects, refresh, api: apiClient }) {
  const [adding, setAdding] = useState(null);
  const [filter, setFilter] = useState("all");
  const [dragTask, setDragTask] = useState(null);
  const [dragOver, setDragOver] = useState(null);

  const handleMove = async (taskId, toStage) => {
    try {
      await apiClient.moveTask(taskId, toStage, "user");
      refresh();
    } catch (err) {
      alert(`Move failed: ${err.message}`);
    }
  };

  const handleCreate = async (data) => {
    try {
      await apiClient.createTask(data);
      setAdding(null);
      refresh();
    } catch (err) {
      alert(`Create failed: ${err.message}`);
    }
  };

  // Drag handlers
  const handleDragStart = (e, task) => {
    setDragTask(task);
    e.dataTransfer.effectAllowed = "move";
  };

  const handleDragOver = (e, stageId) => {
    e.preventDefault();
    if (dragTask && VALID_TRANSITIONS[dragTask.pipeline_stage]?.includes(stageId)) {
      setDragOver(stageId);
      e.dataTransfer.dropEffect = "move";
    }
  };

  const handleDrop = (e, stageId) => {
    e.preventDefault();
    setDragOver(null);
    if (dragTask && VALID_TRANSITIONS[dragTask.pipeline_stage]?.includes(stageId)) {
      handleMove(dragTask.id, stageId);
    }
    setDragTask(null);
  };

  const filteredPipeline = (stageId) => {
    const tasks = pipeline?.[stageId] || [];
    if (filter === "all") return tasks;
    return tasks.filter((t) => t.project_id === filter);
  };

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex items-center gap-3">
        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="text-xs bg-mc-card border border-mc-border rounded-lg px-3 py-2 text-gray-300"
        >
          <option value="all">All projects</option>
          {projects?.map((p) => (
            <option key={p.id} value={p.id}>{p.name}</option>
          ))}
        </select>
        <div className="text-xs text-gray-500">
          {Object.values(pipeline || {}).flat().length} total tasks
        </div>
      </div>

      {/* Pipeline columns */}
      <div className="grid grid-cols-5 gap-4 min-h-[500px]">
        {STAGES.map((stage) => {
          const tasks = filteredPipeline(stage.id);
          const isValidDrop = dragTask && VALID_TRANSITIONS[dragTask.pipeline_stage]?.includes(stage.id);

          return (
            <div
              key={stage.id}
              className={`pipeline-col rounded-xl ${dragOver === stage.id ? "drag-over" : ""}`}
              onDragOver={(e) => handleDragOver(e, stage.id)}
              onDragLeave={() => setDragOver(null)}
              onDrop={(e) => handleDrop(e, stage.id)}
            >
              {/* Column header */}
              <div className={`flex items-center justify-between mb-3 pb-2 border-b-2 ${stage.color}`}>
                <div className="flex items-center gap-2">
                  <span className="text-sm font-medium text-white">{stage.label}</span>
                  <span className="text-[11px] text-gray-500 bg-mc-bg/50 px-1.5 py-0.5 rounded">
                    {tasks.length}
                  </span>
                </div>
                <button
                  onClick={() => setAdding(adding === stage.id ? null : stage.id)}
                  className="text-gray-600 hover:text-gray-300 text-lg leading-none transition-colors"
                  title="Add task"
                >
                  +
                </button>
              </div>

              {/* Add form */}
              {adding === stage.id && (
                <div className="mb-3">
                  <NewTaskForm
                    stage={stage.id}
                    projects={projects}
                    onSubmit={handleCreate}
                    onCancel={() => setAdding(null)}
                  />
                </div>
              )}

              {/* Cards */}
              <div className="space-y-2">
                {tasks.map((task) => (
                  <div
                    key={task.id}
                    draggable
                    onDragStart={(e) => handleDragStart(e, task)}
                    onDragEnd={() => { setDragTask(null); setDragOver(null); }}
                  >
                    <TaskCard task={task} onMove={handleMove} />
                  </div>
                ))}
              </div>

              {/* Empty state */}
              {tasks.length === 0 && adding !== stage.id && (
                <div className={`rounded-lg ${stage.bg} border border-dashed border-mc-border/50 p-4 text-center`}>
                  <div className="text-xs text-gray-600">
                    {isValidDrop ? "Drop here" : "No tasks"}
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
