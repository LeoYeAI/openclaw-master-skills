/**
 * TotalReclaw Skill - Type Definitions
 *
 * Types for the OpenClaw skill integration.
 */
import type { RerankedResult } from '@totalreclaw/client';
/**
 * TotalReclaw skill configuration
 */
export interface TotalReclawSkillConfig {
    /** TotalReclaw server URL */
    serverUrl: string;
    /** Number of turns between automatic extractions */
    autoExtractEveryTurns: number;
    /** Minimum importance (1-10) to auto-store */
    minImportanceForAutoStore: number;
    /** Maximum memories to inject into context */
    maxMemoriesInContext: number;
    /** Decay score threshold for eviction */
    forgetThreshold: number;
    /** ONNX reranker model path */
    rerankerModel?: string;
    /** Master password (from user) */
    masterPassword?: string;
    /** User ID (from previous registration) */
    userId?: string;
    /** Salt (from previous registration) */
    salt?: Buffer;
}
/**
 * Default skill configuration
 */
export declare const DEFAULT_SKILL_CONFIG: TotalReclawSkillConfig;
/**
 * Action type for fact extraction (Mem0 pattern)
 */
export type ExtractionAction = 'ADD' | 'UPDATE' | 'DELETE' | 'NOOP';
/**
 * Extracted fact from LLM
 */
export interface ExtractedFact {
    /** The fact text (atomic, concise) */
    factText: string;
    /** Type of fact */
    type: 'fact' | 'preference' | 'decision' | 'episodic' | 'goal';
    /** Importance score (1-10) */
    importance: number;
    /** Confidence (0-1) */
    confidence: number;
    /** Action to take */
    action: ExtractionAction;
    /** Existing fact ID if UPDATE or DELETE */
    existingFactId?: string;
    /** Extracted entities */
    entities: Entity[];
    /** Extracted relations */
    relations: Relation[];
}
/**
 * Entity extracted from text
 */
export interface Entity {
    id: string;
    name: string;
    type: 'person' | 'project' | 'tool' | 'preference' | 'concept' | 'location' | string;
}
/**
 * Relation between entities
 */
export interface Relation {
    subjectId: string;
    predicate: string;
    objectId: string;
    confidence: number;
}
/**
 * Extraction result from LLM
 */
export interface ExtractionResult {
    facts: ExtractedFact[];
    rawResponse: string;
    processingTimeMs: number;
}
/**
 * OpenClaw context for hooks
 */
export interface OpenClawContext {
    /** Current user message */
    userMessage: string;
    /** Conversation history */
    history: ConversationTurn[];
    /** Agent ID */
    agentId: string;
    /** Session ID */
    sessionId: string;
    /** Current token count */
    tokenCount: number;
    /** Token limit */
    tokenLimit: number;
}
/**
 * Conversation turn
 */
export interface ConversationTurn {
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}
/**
 * Result from before_agent_start hook
 */
export interface BeforeAgentStartResult {
    /** Memories to inject into context */
    memories: RerankedResult[];
    /** Formatted context string */
    contextString: string;
    /** Search latency in ms */
    latencyMs: number;
}
/**
 * Result from agent_end hook
 */
export interface AgentEndResult {
    /** Number of facts extracted */
    factsExtracted: number;
    /** Number of facts stored */
    factsStored: number;
    /** Processing time in ms */
    processingTimeMs: number;
    /** Whether quota was exceeded (403) */
    quotaExceeded?: boolean;
    /** Human-readable quota message for the agent */
    quotaMessage?: string;
}
/**
 * Result from pre_compaction hook
 */
export interface PreCompactionResult {
    /** Number of facts extracted */
    factsExtracted: number;
    /** Number of facts stored */
    factsStored: number;
    /** Number of duplicates skipped */
    duplicatesSkipped: number;
    /** Processing time in ms */
    processingTimeMs: number;
}
/**
 * Parameters for totalreclaw_remember tool
 */
export interface RememberToolParams {
    text: string;
    type?: ExtractedFact['type'];
    importance?: number;
}
/**
 * Parameters for totalreclaw_recall tool
 */
export interface RecallToolParams {
    query: string;
    k?: number;
}
/**
 * Parameters for totalreclaw_forget tool
 */
export interface ForgetToolParams {
    factId: string;
}
/**
 * Parameters for totalreclaw_export tool
 */
export interface ExportToolParams {
    format?: 'json' | 'markdown';
}
/**
 * Internal state for the skill
 */
export interface SkillState {
    /** Turn counter for periodic extraction */
    turnCount: number;
    /** Last extraction timestamp */
    lastExtraction: Date | null;
    /** Cached memories for context */
    cachedMemories: RerankedResult[];
    /** Whether client is initialized */
    isInitialized: boolean;
    /** Pending extractions (async queue) */
    pendingExtractions: ExtractedFact[];
}
//# sourceMappingURL=types.d.ts.map