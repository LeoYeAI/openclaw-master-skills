"use strict";
/**
 * TotalReclaw Skill - LLM Prompts for Fact Extraction
 *
 * Prompts follow Mem0-style ADD/UPDATE/DELETE/NOOP pattern for
 * intelligent deduplication and conflict resolution.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.EXTRACTION_PROMPTS = exports.ENTITY_EXTRACTION_PROMPT = exports.CONTRADICTION_DETECTION_PROMPT = exports.DEDUP_JUDGE_PROMPT = exports.EXPLICIT_COMMAND_PROMPT = exports.POST_TURN_PROMPT = exports.PRE_COMPACTION_PROMPT = exports.DEDUP_JUDGE_SCHEMA = exports.EXTRACTION_RESPONSE_SCHEMA = void 0;
exports.formatConversationHistory = formatConversationHistory;
exports.formatExistingMemories = formatExistingMemories;
exports.generateEntityId = generateEntityId;
exports.validateExtractionResponse = validateExtractionResponse;
// ============================================================================
// JSON Schemas for Structured Output
// ============================================================================
/**
 * JSON schema for extraction response validation
 */
exports.EXTRACTION_RESPONSE_SCHEMA = {
    type: 'object',
    properties: {
        facts: {
            type: 'array',
            items: {
                type: 'object',
                properties: {
                    factText: { type: 'string', maxLength: 512 },
                    type: {
                        type: 'string',
                        enum: ['fact', 'preference', 'decision', 'episodic', 'goal']
                    },
                    importance: { type: 'integer', minimum: 1, maximum: 10 },
                    confidence: { type: 'number', minimum: 0, maximum: 1 },
                    action: {
                        type: 'string',
                        enum: ['ADD', 'UPDATE', 'DELETE', 'NOOP']
                    },
                    existingFactId: { type: 'string' },
                    entities: {
                        type: 'array',
                        items: {
                            type: 'object',
                            properties: {
                                id: { type: 'string' },
                                name: { type: 'string' },
                                type: { type: 'string' }
                            },
                            required: ['id', 'name', 'type']
                        }
                    },
                    relations: {
                        type: 'array',
                        items: {
                            type: 'object',
                            properties: {
                                subjectId: { type: 'string' },
                                predicate: { type: 'string' },
                                objectId: { type: 'string' },
                                confidence: { type: 'number', minimum: 0, maximum: 1 }
                            },
                            required: ['subjectId', 'predicate', 'objectId', 'confidence']
                        }
                    },
                    reasoning: { type: 'string' }
                },
                required: ['factText', 'type', 'importance', 'confidence', 'action', 'entities', 'relations']
            }
        },
        metadata: {
            type: 'object',
            properties: {
                totalTurnsAnalyzed: { type: 'integer' },
                extractionTimestamp: { type: 'string' }
            }
        }
    },
    required: ['facts']
};
/**
 * JSON schema for deduplication judge response
 */
exports.DEDUP_JUDGE_SCHEMA = {
    type: 'object',
    properties: {
        decision: {
            type: 'string',
            enum: ['ADD', 'UPDATE', 'DELETE', 'NOOP']
        },
        existingFactId: { type: 'string' },
        confidence: { type: 'number', minimum: 0, maximum: 1 },
        reasoning: { type: 'string' }
    },
    required: ['decision', 'confidence', 'reasoning']
};
// ============================================================================
// System Prompts
// ============================================================================
/**
 * Base system prompt for fact extraction
 */
const BASE_SYSTEM_PROMPT = `You are a memory extraction engine for an AI assistant. Your job is to analyze conversations and extract structured, atomic facts that should be remembered long-term.

## Extraction Guidelines

1. **Atomicity**: Each fact should be a single, atomic piece of information
   - GOOD: "User prefers TypeScript over JavaScript for new projects"
   - BAD: "User likes TypeScript, uses VS Code, and works at Google"

2. **Types**:
   - **fact**: Objective information about the user/world
   - **preference**: User's likes, dislikes, or preferences
   - **decision**: Choices the user has made
   - **episodic**: Event-based memories (what happened when)
   - **goal**: User's objectives or targets

3. **Importance Scoring (1-10)**:
   - 1-3: Trivial, unlikely to matter (small talk, pleasantries)
   - 4-6: Useful context (tool preferences, working style)
   - 7-8: Important (key decisions, major preferences)
   - 9-10: Critical (core values, non-negotiables, safety info)

4. **Confidence (0-1)**:
   - How certain are you that this is accurate and worth storing?

5. **Entities**: Extract named entities (people, projects, tools, concepts)
   - Use stable IDs: hash of name+type (e.g., "typescript-tool")
   - Types: person, project, tool, preference, concept, location, etc.

6. **Relations**: Extract relationships between entities
   - Common predicates: prefers, uses, works_on, decided_to_use, dislikes, etc.

7. **Actions (Mem0 pattern)**:
   - **ADD**: New fact, no conflict with existing memories
   - **UPDATE**: Modifies or refines an existing fact (provide existingFactId)
   - **DELETE**: Contradicts and replaces an existing fact
   - **NOOP**: Not worth storing or already captured`;
// ============================================================================
// Extraction Prompts
// ============================================================================
/**
 * Pre-compaction prompt - comprehensive extraction from last 20 turns
 */
exports.PRE_COMPACTION_PROMPT = {
    system: BASE_SYSTEM_PROMPT,
    user: `## Task: Pre-Compaction Memory Extraction

You are reviewing the last 20 turns of conversation before they are compacted. Extract ALL valuable long-term memories.

## Conversation History (last 20 turns):
{{CONVERSATION_HISTORY}}

## Existing Memories (for deduplication):
{{EXISTING_MEMORIES}}

## Instructions:
1. Review each turn carefully for extractable information
2. Extract atomic facts, preferences, decisions, episodic memories, and goals
3. For each fact, determine if it's NEW (ADD), modifies existing (UPDATE), contradicts existing (DELETE), or is redundant (NOOP)
4. Score importance based on long-term relevance
5. Extract entities and relations

## Output Format:
Return a JSON object matching this schema:
${JSON.stringify(exports.EXTRACTION_RESPONSE_SCHEMA, null, 2)}

Focus on quality over quantity. Better to have 5 highly accurate facts than 20 noisy ones.`,
    /**
     * Format the pre-compaction prompt with actual data
     */
    format(context) {
        return {
            system: this.system,
            user: this.user
                .replace('{{CONVERSATION_HISTORY}}', context.conversationHistory)
                .replace('{{EXISTING_MEMORIES}}', context.existingMemories)
        };
    }
};
/**
 * Post-turn prompt - lightweight extraction from last 3 turns
 */
exports.POST_TURN_PROMPT = {
    system: BASE_SYSTEM_PROMPT,
    user: `## Task: Quick Turn Extraction

You are doing a lightweight extraction after a few turns. Focus ONLY on high-importance items.

## Recent Turns (last 3):
{{CONVERSATION_HISTORY}}

## Existing Memories (top matches):
{{EXISTING_MEMORIES}}

## Instructions:
1. Extract ONLY items with importance >= 7 (critical preferences, key decisions)
2. Skip trivial information - this is a quick pass
3. Use ADD/UPDATE/DELETE/NOOP appropriately
4. Be aggressive about NOOP for low-value content

## Output Format:
Return a JSON object matching this schema:
${JSON.stringify(exports.EXTRACTION_RESPONSE_SCHEMA, null, 2)}

Remember: Less is more. Only extract what truly matters.`,
    /**
     * Format the post-turn prompt with actual data
     */
    format(context) {
        return {
            system: this.system,
            user: this.user
                .replace('{{CONVERSATION_HISTORY}}', context.conversationHistory)
                .replace('{{EXISTING_MEMORIES}}', context.existingMemories)
        };
    }
};
/**
 * Explicit command prompt - for "remember that..." style commands
 */
exports.EXPLICIT_COMMAND_PROMPT = {
    system: BASE_SYSTEM_PROMPT,
    user: `## Task: Explicit Memory Storage

The user has explicitly requested to remember something. This is a HIGH PRIORITY extraction.

## User's Explicit Request:
{{USER_REQUEST}}

## Conversation Context:
{{CONVERSATION_CONTEXT}}

## Instructions:
1. Parse what the user wants remembered
2. Boost importance by +1 (explicit requests matter more)
3. Extract as atomic fact(s) with appropriate type
4. Check against existing memories for UPDATE/DELETE
5. Set confidence HIGH (user explicitly wants this stored)

## Output Format:
Return a JSON object matching this schema:
${JSON.stringify(exports.EXTRACTION_RESPONSE_SCHEMA, null, 2)}

This is user-initiated storage - ensure accuracy and capture their intent precisely.`,
    /**
     * Format the explicit command prompt with actual data
     */
    format(context) {
        return {
            system: this.system,
            user: this.user
                .replace('{{USER_REQUEST}}', context.userRequest)
                .replace('{{CONVERSATION_CONTEXT}}', context.conversationContext)
        };
    }
};
// ============================================================================
// Deduplication Prompts
// ============================================================================
/**
 * LLM judge prompt for determining ADD vs UPDATE vs DELETE
 */
exports.DEDUP_JUDGE_PROMPT = {
    system: `You are a memory deduplication judge. Your job is to determine if a new fact should be added as new, update an existing fact, delete/replace an existing fact, or be ignored as redundant.

## Decision Rules:

1. **ADD**: The fact is genuinely new information not covered by existing memories
2. **UPDATE**: The fact refines, clarifies, or partially modifies an existing fact
3. **DELETE**: The fact directly contradicts an existing fact and should replace it
4. **NOOP**: The fact is already fully captured by existing memories

Be strict about NOOP - if the information is essentially the same, mark it as NOOP.`,
    user: `## New Fact to Evaluate:
{{NEW_FACT}}

## Similar Existing Facts:
{{EXISTING_FACTS}}

## Instructions:
1. Compare the new fact against each existing fact
2. Determine the appropriate action (ADD/UPDATE/DELETE/NOOP)
3. If UPDATE or DELETE, identify which existing fact to modify
4. Provide your confidence (0-1) and reasoning

## Output Format:
Return a JSON object matching this schema:
${JSON.stringify(exports.DEDUP_JUDGE_SCHEMA, null, 2)}`,
    /**
     * Format the dedup judge prompt with actual data
     */
    format(context) {
        return {
            system: this.system,
            user: this.user
                .replace('{{NEW_FACT}}', context.newFact)
                .replace('{{EXISTING_FACTS}}', context.existingFacts)
        };
    }
};
/**
 * Contradiction detection prompt
 */
exports.CONTRADICTION_DETECTION_PROMPT = {
    system: `You are a contradiction detector for memory facts. Determine if two facts contradict each other.

## Contradiction Types:
1. **Direct negation**: "User likes X" vs "User dislikes X"
2. **Mutually exclusive values**: "User uses VS Code" vs "User uses IntelliJ exclusively"
3. **Temporal replacement**: "User works at Google" vs "User now works at Meta"

Not all differences are contradictions - some facts can coexist (context-dependent preferences).`,
    user: `## Fact A (new):
{{FACT_A}}

## Fact B (existing):
{{FACT_B}}

## Task:
Determine if these facts contradict each other. If they do, which one should be kept?

## Output Format:
{
  "isContradiction": boolean,
  "contradictionType": "direct_negation" | "mutually_exclusive" | "temporal_replacement" | "none",
  "shouldKeep": "A" | "B" | "both",
  "reasoning": string
}`,
    format(context) {
        return {
            system: this.system,
            user: this.user
                .replace('{{FACT_A}}', context.factA)
                .replace('{{FACT_B}}', context.factB)
        };
    }
};
// ============================================================================
// Entity Extraction Prompts
// ============================================================================
/**
 * Entity extraction prompt (can be used standalone)
 */
exports.ENTITY_EXTRACTION_PROMPT = {
    system: `You are an entity extractor. Extract named entities from text with their types.

## Entity Types:
- **person**: Named individuals
- **project**: Projects, codebases, products
- **tool**: Software tools, libraries, frameworks
- **preference**: Named preferences (e.g., "TypeScript" as a preference entity)
- **concept**: Abstract concepts, methodologies
- **location**: Physical or virtual locations
- **organization**: Companies, teams, groups

## ID Generation:
Generate stable IDs by combining normalized name + type (lowercase, no spaces).
Example: "TypeScript" + "tool" -> "typescript-tool"`,
    user: `## Text to Analyze:
{{TEXT}}

## Output Format:
{
  "entities": [
    {
      "id": "string (normalized-name-type)",
      "name": "string (original name)",
      "type": "string (entity type)"
    }
  ]
}`,
    format(text) {
        return {
            system: this.system,
            user: this.user.replace('{{TEXT}}', text)
        };
    }
};
// ============================================================================
// Helper Functions
// ============================================================================
/**
 * Format conversation history for prompts
 */
function formatConversationHistory(turns) {
    return turns
        .map((turn, index) => {
        const timestamp = turn.timestamp.toISOString();
        return `[${index + 1}] ${turn.role.toUpperCase()} (${timestamp}):\n${turn.content}`;
    })
        .join('\n\n');
}
/**
 * Format existing memories for deduplication context
 */
function formatExistingMemories(memories) {
    if (memories.length === 0) {
        return '(No existing memories found)';
    }
    return memories
        .map((m, index) => {
        return `[${index + 1}] ID: ${m.id}\n    Type: ${m.type}\n    Importance: ${m.importance}\n    Fact: ${m.factText}`;
    })
        .join('\n\n');
}
/**
 * Generate a stable entity ID from name and type
 */
function generateEntityId(name, type) {
    const normalized = name.toLowerCase().replace(/[^a-z0-9]/g, '-');
    return `${normalized}-${type}`;
}
/**
 * Validate extraction response against schema
 */
function validateExtractionResponse(response) {
    const errors = [];
    if (!response || typeof response !== 'object') {
        return { valid: false, errors: ['Response must be an object'] };
    }
    const obj = response;
    if (!Array.isArray(obj.facts)) {
        return { valid: false, errors: ['Response must have a "facts" array'] };
    }
    const facts = [];
    for (let i = 0; i < obj.facts.length; i++) {
        const fact = obj.facts[i];
        const factErrors = [];
        if (typeof fact.factText !== 'string' || fact.factText.length === 0) {
            factErrors.push(`facts[${i}].factText must be a non-empty string`);
        }
        const validTypes = ['fact', 'preference', 'decision', 'episodic', 'goal'];
        if (!validTypes.includes(fact.type)) {
            factErrors.push(`facts[${i}].type must be one of: ${validTypes.join(', ')}`);
        }
        if (typeof fact.importance !== 'number' || fact.importance < 1 || fact.importance > 10) {
            factErrors.push(`facts[${i}].importance must be a number between 1 and 10`);
        }
        if (typeof fact.confidence !== 'number' || fact.confidence < 0 || fact.confidence > 1) {
            factErrors.push(`facts[${i}].confidence must be a number between 0 and 1`);
        }
        const validActions = ['ADD', 'UPDATE', 'DELETE', 'NOOP'];
        if (!validActions.includes(fact.action)) {
            factErrors.push(`facts[${i}].action must be one of: ${validActions.join(', ')}`);
        }
        if (!Array.isArray(fact.entities)) {
            factErrors.push(`facts[${i}].entities must be an array`);
        }
        if (!Array.isArray(fact.relations)) {
            factErrors.push(`facts[${i}].relations must be an array`);
        }
        if (factErrors.length > 0) {
            errors.push(...factErrors);
        }
        else {
            facts.push({
                factText: fact.factText,
                type: fact.type,
                importance: Math.round(fact.importance),
                confidence: fact.confidence,
                action: fact.action,
                existingFactId: fact.existingFactId,
                entities: fact.entities || [],
                relations: fact.relations || []
            });
        }
    }
    if (errors.length > 0) {
        return { valid: false, errors };
    }
    return { valid: true, errors: [], facts };
}
// ============================================================================
// Exports
// ============================================================================
/**
 * All extraction prompts bundled together
 */
exports.EXTRACTION_PROMPTS = {
    preCompaction: exports.PRE_COMPACTION_PROMPT,
    postTurn: exports.POST_TURN_PROMPT,
    explicitCommand: exports.EXPLICIT_COMMAND_PROMPT,
    dedupJudge: exports.DEDUP_JUDGE_PROMPT,
    contradictionDetection: exports.CONTRADICTION_DETECTION_PROMPT,
    entityExtraction: exports.ENTITY_EXTRACTION_PROMPT
};
//# sourceMappingURL=prompts.js.map