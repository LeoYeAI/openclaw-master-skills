/**
 * OpenClaw Hook System Types
 *
 * Type definitions for OpenClaw's event-driven hook system.
 */

/**
 * Hook Event - base event structure
 */
export interface HookEvent {
  type: string;
  action: string;
  data?: Record<string, any>;
  user?: {
    id: string;
    email?: string;
    name?: string;
  };
  session?: {
    id: string;
    startTime?: Date;
  };
  api?: {
    registerPlugin?: (name: string, handler: PluginHandler) => void;
    [key: string]: any;
  };
}

/**
 * Command Event - triggered when user executes commands
 */
export interface CommandEvent extends HookEvent {
  type: "command";
  action: "new" | "edit" | "cancel";
  data: {
    input?: string;
    prompt?: string;
    userId?: string;
    sessionId?: string;
    [key: string]: any;
  };
}

/**
 * Agent Event - triggered during agent lifecycle
 */
export interface AgentEvent extends HookEvent {
  type: "agent";
  action: "bootstrap" | "start" | "stop" | "error";
  data?: {
    agentId?: string;
    [key: string]: any;
  };
}

/**
 * Tool Event - triggered during tool execution
 */
export interface ToolEvent extends HookEvent {
  type: "tool";
  action: "call" | "result" | "error";
  data: {
    toolName?: string;
    parameters?: Array<{
      name: string;
      value: any;
      type?: string;
    }>;
    result?: any;
    error?: Error;
    [key: string]: any;
  };
}

/**
 * Plugin Handler - function signature for plugin API handlers
 */
export type PluginHandler = (data: any) => Promise<void> | void;

/**
 * Hook Handler - main function signature for hook handlers
 */
export type HookHandler = (event: HookEvent) => Promise<void> | void;

/**
 * Hook Metadata - from HOOK.md frontmatter
 */
export interface HookMetadata {
  name: string;
  description: string;
  metadata: {
    openclaw: {
      emoji: string;
      events: string[];
      plugin_api?: string;
    };
  };
}
