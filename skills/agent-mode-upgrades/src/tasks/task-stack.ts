/**
 * Hierarchical Task Management
 * 
 * Provides structured working memory for complex multi-step tasks.
 */

import type { Task, TaskResult, TaskStack, TaskStatus } from "../types.js";

/**
 * Generate a unique task ID
 */
function generateTaskId(): string {
  return `task_${Date.now()}_${Math.random().toString(36).slice(2, 9)}`;
}

/**
 * Create a new task
 */
export function createTask(
  stack: TaskStack,
  task: Partial<Omit<Task, "id" | "createdAt" | "updatedAt" | "subtasks">>
): Task {
  const newTask: Task = {
    id: generateTaskId(),
    parentId: task.parentId ?? null,
    title: task.title ?? "Untitled",
    description: task.description ?? "",
    status: task.status ?? "pending",
    priority: task.priority ?? 0,
    createdAt: Date.now(),
    updatedAt: Date.now(),
    subtasks: [],
    dependencies: task.dependencies ?? [],
    metadata: task.metadata ?? {},
  };

  if (newTask.parentId) {
    const parent = findTask(stack, newTask.parentId);
    if (parent) {
      parent.subtasks.push(newTask);
      parent.updatedAt = Date.now();
    } else {
      // Parent not found, add as root task
      stack.tasks.push(newTask);
    }
  } else {
    stack.tasks.push(newTask);
  }

  return newTask;
}

/**
 * Find a task by ID (recursive)
 */
export function findTask(stack: TaskStack, taskId: string): Task | null {
  function search(tasks: Task[]): Task | null {
    for (const task of tasks) {
      if (task.id === taskId) return task;
      const found = search(task.subtasks);
      if (found) return found;
    }
    return null;
  }
  return search(stack.tasks);
}

/**
 * Flatten the task tree into a list
 */
export function flattenTasks(stack: TaskStack): Task[] {
  const result: Task[] = [];

  function collect(tasks: Task[]): void {
    for (const task of tasks) {
      result.push(task);
      collect(task.subtasks);
    }
  }

  collect(stack.tasks);
  return result;
}

/**
 * Update task status with result propagation
 */
export function updateTaskStatus(
  stack: TaskStack,
  taskId: string,
  status: TaskStatus,
  result?: TaskResult
): void {
  const task = findTask(stack, taskId);
  if (!task) return;

  task.status = status;
  task.updatedAt = Date.now();
  if (result) task.result = result;

  // If completing, check if parent should also complete
  if (status === "complete" && task.parentId) {
    const parent = findTask(stack, task.parentId);
    if (parent) {
      const allComplete = parent.subtasks.every((t) => t.status === "complete");
      if (allComplete) {
        updateTaskStatus(stack, parent.id, "complete", {
          success: true,
          summary: `All ${parent.subtasks.length} subtasks completed`,
        });
      }
    }
  }

  // If failing, might need to mark parent as blocked
  if (status === "failed" && task.parentId) {
    const parent = findTask(stack, task.parentId);
    if (parent && parent.status === "in_progress") {
      // Check if there are remaining pending subtasks
      const hasPending = parent.subtasks.some((t) => t.status === "pending");
      if (!hasPending) {
        // All subtasks either complete or failed
        const anySuccess = parent.subtasks.some((t) => t.status === "complete");
        updateTaskStatus(stack, parent.id, anySuccess ? "complete" : "failed", {
          success: anySuccess,
          summary: anySuccess
            ? "Some subtasks completed with failures"
            : "All subtasks failed",
        });
      }
    }
  }
}

/**
 * Check if a task has pending dependencies
 */
export function hasPendingDependencies(stack: TaskStack, task: Task): boolean {
  for (const depId of task.dependencies) {
    const dep = findTask(stack, depId);
    if (dep && dep.status !== "complete") {
      return true;
    }
  }
  return false;
}

/**
 * Get the next task to execute (highest priority, no pending deps)
 */
export function getNextTask(stack: TaskStack): Task | null {
  const candidates = flattenTasks(stack)
    .filter((t) => t.status === "pending")
    .filter((t) => !hasPendingDependencies(stack, t))
    .sort((a, b) => b.priority - a.priority);

  return candidates[0] ?? null;
}

/**
 * Get the active task
 */
export function getActiveTask(stack: TaskStack): Task | null {
  if (!stack.activeTaskId) return null;
  return findTask(stack, stack.activeTaskId);
}

/**
 * Set the active task
 */
export function setActiveTask(stack: TaskStack, taskId: string | null): void {
  stack.activeTaskId = taskId;
  if (taskId) {
    const task = findTask(stack, taskId);
    if (task && task.status === "pending") {
      task.status = "in_progress";
      task.updatedAt = Date.now();
    }
  }
}

/**
 * Handle an interruption (steering message)
 */
export function handleInterruption(
  stack: TaskStack,
  message: string,
  urgency: "low" | "medium" | "high" | "critical"
): { action: string; pausedTask?: string; taskId?: string } {
  const activeTask = getActiveTask(stack);

  if (urgency === "critical") {
    // Pause everything, handle immediately
    if (activeTask) {
      activeTask.status = "blocked";
      activeTask.metadata.pausedAt = Date.now();
      activeTask.metadata.pausedBy = "steering";
      activeTask.updatedAt = Date.now();
    }
    return { action: "handle_now", pausedTask: activeTask?.id };
  }

  if (urgency === "high") {
    // Complete current step, then switch
    return { action: "finish_step_then_handle" };
  }

  // Queue for after current task branch
  const interruptTask = createTask(stack, {
    title: "Handle steering message",
    description: message,
    priority: urgency === "medium" ? 5 : 1,
  });

  return { action: "queued", taskId: interruptTask.id };
}

/**
 * Build a context prompt from the task stack
 */
export function buildTaskContextPrompt(stack: TaskStack): string {
  const active = getActiveTask(stack);

  if (!active) return "";

  const allTasks = flattenTasks(stack);
  const completed = allTasks
    .filter((t) => t.status === "complete")
    .map((t) => `- ✓ ${t.title}${t.result?.summary ? ` (${t.result.summary})` : ""}`);

  const pending = allTasks
    .filter((t) => t.status === "pending")
    .map((t) => `- ○ ${t.title}`);

  const inProgress = allTasks
    .filter((t) => t.status === "in_progress" && t.id !== active.id)
    .map((t) => `- ◐ ${t.title}`);

  const lines: string[] = [
    "## Current Task",
    `**${active.title}**`,
  ];

  if (active.description) {
    lines.push(active.description);
  }

  lines.push("");
  lines.push("## Progress");

  if (completed.length > 0) {
    lines.push("### Completed");
    lines.push(...completed);
  }

  if (inProgress.length > 0) {
    lines.push("### In Progress");
    lines.push(...inProgress);
  }

  if (pending.length > 0) {
    lines.push("### Remaining");
    lines.push(...pending);
  }

  return lines.join("\n").trim();
}

/**
 * Create an empty task stack
 */
export function createTaskStack(): TaskStack {
  return {
    tasks: [],
    activeTaskId: null,
  };
}

/**
 * Serialize task stack for persistence
 */
export function serializeTaskStack(stack: TaskStack): string {
  return JSON.stringify(stack, null, 2);
}

/**
 * Restore task stack from persistence
 */
export function restoreTaskStack(serialized: string): TaskStack {
  try {
    return JSON.parse(serialized) as TaskStack;
  } catch {
    return createTaskStack();
  }
}

/**
 * Calculate task completion progress (0-100)
 */
export function calculateProgress(stack: TaskStack): number {
  const allTasks = flattenTasks(stack);
  if (allTasks.length === 0) return 0;

  const completed = allTasks.filter((t) => t.status === "complete").length;
  return Math.round((completed / allTasks.length) * 100);
}

/**
 * Get task statistics
 */
export function getTaskStats(stack: TaskStack): {
  total: number;
  byStatus: Record<TaskStatus, number>;
  maxDepth: number;
  progress: number;
} {
  const allTasks = flattenTasks(stack);
  const byStatus: Record<TaskStatus, number> = {
    pending: 0,
    in_progress: 0,
    blocked: 0,
    complete: 0,
    failed: 0,
    skipped: 0,
  };

  for (const task of allTasks) {
    byStatus[task.status] = (byStatus[task.status] ?? 0) + 1;
  }

  // Calculate max depth
  function depth(task: Task): number {
    if (task.subtasks.length === 0) return 0;
    return 1 + Math.max(...task.subtasks.map(depth));
  }

  const maxDepth = stack.tasks.length > 0
    ? Math.max(...stack.tasks.map(depth))
    : 0;

  return {
    total: allTasks.length,
    byStatus,
    maxDepth,
    progress: calculateProgress(stack),
  };
}
