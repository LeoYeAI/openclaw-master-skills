/**
 * TotalReclaw Skill for OpenClaw
 *
 * End-to-end encrypted memory for AI agents using MemOS-inspired
 * lifecycle hooks pattern.
 *
 * @example
 * ```typescript
 * import { TotalReclawSkill } from '@totalreclaw/skill';
 *
 * const skill = new TotalReclawSkill({
 *   serverUrl: 'http://127.0.0.1:8080',
 *   masterPassword: 'my-secure-password',
 * });
 *
 * await skill.init();
 * ```
 */

export { TotalReclawSkill } from './totalreclaw-skill';
export type {
  TotalReclawSkillConfig,
  DEFAULT_SKILL_CONFIG,
  ExtractedFact,
  ExtractionAction,
  ExtractionResult,
  Entity,
  Relation,
  OpenClawContext,
  ConversationTurn,
  BeforeAgentStartResult,
  AgentEndResult,
  PreCompactionResult,
  RememberToolParams,
  RecallToolParams,
  ForgetToolParams,
  ExportToolParams,
  SkillState,
} from './types';

// Tool implementations
export { rememberTool } from './tools/remember';
export { recallTool } from './tools/recall';
export { forgetTool } from './tools/forget';
export { exportTool } from './tools/export';

// Extraction
export { FactExtractor } from './extraction/extractor';
export { EXTRACTION_PROMPTS } from './extraction/prompts';

// Triggers / Lifecycle Hooks
export {
  beforeAgentStart,
  formatMemoriesForContext,
  type BeforeAgentStartOptions,
} from './triggers/before-agent-start';
export {
  agentEnd,
  type AgentEndOptions,
} from './triggers/agent-end';
export {
  preCompaction,
  type PreCompactionOptions,
} from './triggers/pre-compaction';

// Reranking
export { CrossEncoderReranker } from './reranker/cross-encoder';

// Config
export { loadConfig, validateConfig } from './config';
