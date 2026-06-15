/**
 * Hierarchical Task Management
 *
 * Provides structured working memory for complex multi-step tasks.
 */
import type { Task, TaskResult, TaskStack, TaskStatus } from "../types.js";
/**
 * Create a new task
 */
export declare function createTask(stack: TaskStack, task: Partial<Omit<Task, "id" | "createdAt" | "updatedAt" | "subtasks">>): Task;
/**
 * Find a task by ID (recursive)
 */
export declare function findTask(stack: TaskStack, taskId: string): Task | null;
/**
 * Flatten the task tree into a list
 */
export declare function flattenTasks(stack: TaskStack): Task[];
/**
 * Update task status with result propagation
 */
export declare function updateTaskStatus(stack: TaskStack, taskId: string, status: TaskStatus, result?: TaskResult): void;
/**
 * Check if a task has pending dependencies
 */
export declare function hasPendingDependencies(stack: TaskStack, task: Task): boolean;
/**
 * Get the next task to execute (highest priority, no pending deps)
 */
export declare function getNextTask(stack: TaskStack): Task | null;
/**
 * Get the active task
 */
export declare function getActiveTask(stack: TaskStack): Task | null;
/**
 * Set the active task
 */
export declare function setActiveTask(stack: TaskStack, taskId: string | null): void;
/**
 * Handle an interruption (steering message)
 */
export declare function handleInterruption(stack: TaskStack, message: string, urgency: "low" | "medium" | "high" | "critical"): {
    action: string;
    pausedTask?: string;
    taskId?: string;
};
/**
 * Build a context prompt from the task stack
 */
export declare function buildTaskContextPrompt(stack: TaskStack): string;
/**
 * Create an empty task stack
 */
export declare function createTaskStack(): TaskStack;
/**
 * Serialize task stack for persistence
 */
export declare function serializeTaskStack(stack: TaskStack): string;
/**
 * Restore task stack from persistence
 */
export declare function restoreTaskStack(serialized: string): TaskStack;
/**
 * Calculate task completion progress (0-100)
 */
export declare function calculateProgress(stack: TaskStack): number;
/**
 * Get task statistics
 */
export declare function getTaskStats(stack: TaskStack): {
    total: number;
    byStatus: Record<TaskStatus, number>;
    maxDepth: number;
    progress: number;
};
//# sourceMappingURL=task-stack.d.ts.map