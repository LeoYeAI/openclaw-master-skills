/**
 * Planning and Reflection
 *
 * Generates execution plans and assesses progress after actions.
 */
import type { TaskPlan, PlanStep, ReflectionResult, LLMCaller, ToolCall, ToolResult, PlanningConfig } from "../types.js";
/**
 * Check if planning is needed for this goal.
 * Creates a new plan if: no plan exists, existing plan is completed/stale,
 * or the user's goal has pivoted away from the existing plan.
 */
export declare function shouldGeneratePlan(goal: string, existingPlan: TaskPlan | null, config: PlanningConfig): boolean;
/**
 * Generate an execution plan
 */
export declare function generatePlan(goal: string, context: string, config: PlanningConfig, llmCall: LLMCaller): Promise<TaskPlan>;
/**
 * Reflect on progress after a tool execution
 */
export declare function reflect(plan: TaskPlan, lastAction: ToolCall, result: ToolResult, config: PlanningConfig, llmCall: LLMCaller): Promise<ReflectionResult>;
/**
 * Revise the plan based on reflection
 */
export declare function replan(plan: TaskPlan, reason: string, config: PlanningConfig, llmCall: LLMCaller): Promise<TaskPlan>;
/**
 * Mark a plan step as complete
 */
export declare function completeStep(plan: TaskPlan, stepId: string, result?: string): TaskPlan;
/**
 * Mark a plan step as failed
 */
export declare function failStep(plan: TaskPlan, stepId: string, error: string): TaskPlan;
/**
 * Get the next pending step
 */
export declare function getNextStep(plan: TaskPlan): PlanStep | null;
/**
 * Format plan for context injection
 */
export declare function formatPlanForContext(plan: TaskPlan): string;
//# sourceMappingURL=planner.d.ts.map