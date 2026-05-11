/**
 * Guardian Angel Constants
 */

/** Hook priority. Lower = runs later. -10000 ensures we run last. */
export const GA_PRIORITY = -10000;

/** Default escalation threshold (Clarity × Stakes) */
export const DEFAULT_ESCALATION_THRESHOLD = 36;

/** Default pending timeout: 5 minutes */
export const DEFAULT_PENDING_TIMEOUT_MS = 300000;

/** Default approval window: 30 seconds */
export const DEFAULT_APPROVAL_WINDOW_MS = 30000;

/** Tools that affect system infrastructure */
export const INFRASTRUCTURE_TOOLS = [
  "gateway",
  "exec",
  "Write",
  "Edit",
];

/** Tools with external effects */
export const EXTERNAL_EFFECT_TOOLS = [
  "message",
  "browser",
  "cron",
  "nodes",
  "tts",
];

/** Default tools exempt from evaluation */
export const DEFAULT_NEVER_BLOCK = [
  "memory_search",
  "memory_get",
  "session_status",
  "Read",
  "web_search",
  "web_fetch",
  "image",
  "sessions_list",
  "sessions_history",
  "agents_list",
];
