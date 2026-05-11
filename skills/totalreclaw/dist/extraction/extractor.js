"use strict";
/**
 * TotalReclaw Skill - Fact Extractor
 *
 * Main extraction module that:
 * 1. Extracts facts from conversation context
 * 2. Deduplicates against existing memories
 * 3. Scores importance
 * 4. Extracts entities and relations
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.createDeduplicator = exports.FactDeduplicator = exports.FactExtractor = exports.DEFAULT_EXTRACTOR_CONFIG = void 0;
exports.createFactExtractor = createFactExtractor;
exports.extractFactsFromText = extractFactsFromText;
exports.isExplicitMemoryCommand = isExplicitMemoryCommand;
exports.parseExplicitMemoryCommand = parseExplicitMemoryCommand;
const prompts_1 = require("./prompts");
const dedup_1 = require("./dedup");
Object.defineProperty(exports, "FactDeduplicator", { enumerable: true, get: function () { return dedup_1.FactDeduplicator; } });
Object.defineProperty(exports, "createDeduplicator", { enumerable: true, get: function () { return dedup_1.createDeduplicator; } });
/**
 * Default extraction configuration
 */
exports.DEFAULT_EXTRACTOR_CONFIG = {
    extractionModel: 'claude-3-5-haiku-20241022',
    extractionTemperature: 0.3,
    minImportance: 1,
    autoDeduplicate: true,
    postTurnWindow: 3,
    preCompactionWindow: 20,
    dedupConfig: {}
};
// ============================================================================
// Fact Extractor Class
// ============================================================================
/**
 * Main fact extraction class
 */
class FactExtractor {
    config;
    llmClient;
    vectorStore;
    deduplicator;
    constructor(llmClient, vectorStore, config = {}) {
        this.config = {
            ...exports.DEFAULT_EXTRACTOR_CONFIG,
            ...config
        };
        this.llmClient = llmClient;
        this.vectorStore = vectorStore || null;
        this.deduplicator = (0, dedup_1.createDeduplicator)(llmClient, vectorStore, this.config.dedupConfig);
    }
    /**
     * Extract facts from OpenClaw context
     */
    async extractFacts(context, trigger = 'post_turn') {
        const startTime = Date.now();
        // Select appropriate prompt based on trigger
        const prompt = this.selectPrompt(context, trigger);
        // Call LLM for extraction
        const rawResponse = await this.llmClient.complete(prompt);
        // Parse and validate response
        const { facts, errors } = await this.parseExtractionResponse(rawResponse);
        if (errors.length > 0) {
            console.warn('Extraction validation warnings:', errors);
        }
        // Filter by minimum importance
        const filteredFacts = facts.filter(f => f.importance >= this.config.minImportance);
        // Post-process: normalize entities and relations
        const processedFacts = filteredFacts.map(fact => this.postProcessFact(fact));
        return {
            facts: processedFacts,
            rawResponse,
            processingTimeMs: Date.now() - startTime
        };
    }
    /**
     * Deduplicate extracted facts against existing memories
     */
    async deduplicateAgainstExisting(facts, existingFacts) {
        if (!this.config.autoDeduplicate) {
            return facts;
        }
        return this.deduplicator.deduplicateFacts(facts, existingFacts);
    }
    /**
     * Score importance of a fact (1-10 scale)
     * Can be used to re-score or validate LLM scores
     */
    scoreImportance(fact) {
        let score = fact.importance;
        // Boost for explicit user requests
        if (fact.action === 'ADD' && fact.confidence > 0.9) {
            score = Math.min(10, score + 1);
        }
        // Boost for decisions (they tend to be important)
        if (fact.type === 'decision') {
            score = Math.min(10, score + 1);
        }
        // Boost for goals
        if (fact.type === 'goal') {
            score = Math.min(10, score + 0.5);
        }
        // Reduce for low confidence
        if (fact.confidence < 0.5) {
            score = Math.max(1, score - 1);
        }
        return Math.round(score);
    }
    /**
     * Extract entities from text (standalone entity extraction)
     */
    async extractEntities(text) {
        const prompt = prompts_1.ENTITY_EXTRACTION_PROMPT.format(text);
        try {
            const response = await this.llmClient.complete(prompt);
            const parsed = JSON.parse(response);
            if (!Array.isArray(parsed.entities)) {
                return [];
            }
            return parsed.entities.map((e) => ({
                id: e.id || (0, prompts_1.generateEntityId)(e.name, e.type),
                name: e.name,
                type: e.type
            }));
        }
        catch (error) {
            console.error('Entity extraction failed:', error);
            return [];
        }
    }
    /**
     * Extract relations from a fact
     */
    async extractRelations(fact) {
        // If relations already extracted by LLM, validate and return
        if (fact.relations.length > 0) {
            return fact.relations.filter(r => r.subjectId &&
                r.predicate &&
                r.objectId &&
                r.confidence >= 0 &&
                r.confidence <= 1);
        }
        // Otherwise, extract relations from entities
        const relations = [];
        const entities = fact.entities;
        // Generate "mentions" relations between entities
        for (let i = 0; i < entities.length; i++) {
            for (let j = i + 1; j < entities.length; j++) {
                // Infer relation type based on fact type
                let predicate = 'related_to';
                if (fact.type === 'preference') {
                    predicate = 'prefers_with';
                }
                else if (fact.type === 'decision') {
                    predicate = 'decided_with';
                }
                relations.push({
                    subjectId: entities[i].id,
                    predicate,
                    objectId: entities[j].id,
                    confidence: 0.5 // Lower confidence for inferred relations
                });
            }
        }
        return relations;
    }
    // ============================================================================
    // Private Methods
    // ============================================================================
    /**
     * Select the appropriate prompt based on trigger type
     */
    selectPrompt(context, trigger) {
        switch (trigger) {
            case 'pre_compaction':
                return this.buildPreCompactionPrompt(context);
            case 'explicit':
                return this.buildExplicitPrompt(context);
            case 'post_turn':
            default:
                return this.buildPostTurnPrompt(context);
        }
    }
    /**
     * Build pre-compaction extraction prompt
     */
    buildPreCompactionPrompt(context) {
        // Get last N turns
        const turns = context.history.slice(-this.config.preCompactionWindow);
        const historyStr = (0, prompts_1.formatConversationHistory)(turns);
        // Get existing memories for dedup context
        const existingMemoriesStr = '(Existing memories will be checked during deduplication)';
        return prompts_1.PRE_COMPACTION_PROMPT.format({
            conversationHistory: historyStr,
            existingMemories: existingMemoriesStr
        });
    }
    /**
     * Build post-turn extraction prompt
     */
    buildPostTurnPrompt(context) {
        // Get last N turns
        const turns = context.history.slice(-this.config.postTurnWindow);
        const historyStr = (0, prompts_1.formatConversationHistory)(turns);
        // Include current message if not in history
        const fullHistory = turns.length === 0 || turns[turns.length - 1]?.content !== context.userMessage
            ? `${historyStr}\n\n[LATEST] USER:\n${context.userMessage}`
            : historyStr;
        const existingMemoriesStr = '(Existing memories will be checked during deduplication)';
        return prompts_1.POST_TURN_PROMPT.format({
            conversationHistory: fullHistory,
            existingMemories: existingMemoriesStr
        });
    }
    /**
     * Build explicit command extraction prompt
     */
    buildExplicitPrompt(context) {
        // The user message should contain the explicit request
        const turns = context.history.slice(-5);
        const contextStr = (0, prompts_1.formatConversationHistory)(turns);
        return prompts_1.EXPLICIT_COMMAND_PROMPT.format({
            userRequest: context.userMessage,
            conversationContext: contextStr
        });
    }
    /**
     * Parse and validate LLM extraction response
     */
    async parseExtractionResponse(rawResponse) {
        const errors = [];
        try {
            // Try to extract JSON from the response
            let jsonStr = rawResponse;
            // Handle markdown code blocks
            const jsonMatch = rawResponse.match(/```(?:json)?\s*([\s\S]*?)```/);
            if (jsonMatch) {
                jsonStr = jsonMatch[1].trim();
            }
            const parsed = JSON.parse(jsonStr);
            if (!Array.isArray(parsed.facts)) {
                return { facts: [], errors: ['Response does not contain a facts array'] };
            }
            // Validate each fact
            const facts = [];
            for (let i = 0; i < parsed.facts.length; i++) {
                const rawFact = parsed.facts[i];
                const validation = this.validateFact(rawFact, i);
                if (validation.errors.length > 0) {
                    errors.push(...validation.errors);
                }
                if (validation.fact) {
                    facts.push(validation.fact);
                }
            }
            return { facts, errors };
        }
        catch (error) {
            const errorMsg = error instanceof Error ? error.message : 'Unknown parsing error';
            return { facts: [], errors: [`Failed to parse LLM response: ${errorMsg}`] };
        }
    }
    /**
     * Validate a single extracted fact
     */
    validateFact(rawFact, index) {
        const errors = [];
        const prefix = `facts[${index}]`;
        // Validate required fields
        if (!rawFact.factText || typeof rawFact.factText !== 'string') {
            errors.push(`${prefix}.factText must be a non-empty string`);
        }
        const validTypes = ['fact', 'preference', 'decision', 'episodic', 'goal'];
        if (!validTypes.includes(rawFact.type)) {
            errors.push(`${prefix}.type must be one of: ${validTypes.join(', ')}`);
        }
        if (typeof rawFact.importance !== 'number' || rawFact.importance < 1 || rawFact.importance > 10) {
            errors.push(`${prefix}.importance must be a number between 1 and 10`);
        }
        if (typeof rawFact.confidence !== 'number' || rawFact.confidence < 0 || rawFact.confidence > 1) {
            errors.push(`${prefix}.confidence must be a number between 0 and 1`);
        }
        const validActions = ['ADD', 'UPDATE', 'DELETE', 'NOOP'];
        if (!validActions.includes(rawFact.action)) {
            errors.push(`${prefix}.action must be one of: ${validActions.join(', ')}`);
        }
        if (errors.length > 0) {
            return { fact: null, errors };
        }
        // Build validated fact
        const fact = {
            factText: rawFact.factText.trim().slice(0, 512), // Limit length
            type: rawFact.type,
            importance: Math.round(Math.max(1, Math.min(10, rawFact.importance))),
            confidence: Math.max(0, Math.min(1, rawFact.confidence)),
            action: rawFact.action,
            existingFactId: rawFact.existingFactId,
            entities: (rawFact.entities || []).map(e => ({
                id: e.id || (0, prompts_1.generateEntityId)(e.name, e.type),
                name: e.name,
                type: e.type
            })),
            relations: (rawFact.relations || []).filter(r => r.subjectId && r.predicate && r.objectId).map(r => ({
                subjectId: r.subjectId,
                predicate: r.predicate,
                objectId: r.objectId,
                confidence: Math.max(0, Math.min(1, r.confidence || 0.5))
            }))
        };
        return { fact, errors: [] };
    }
    /**
     * Post-process a fact (normalize entities, etc.)
     */
    postProcessFact(fact) {
        // Normalize entity IDs
        const normalizedEntities = fact.entities.map(entity => ({
            ...entity,
            id: entity.id || (0, prompts_1.generateEntityId)(entity.name, entity.type)
        }));
        // Update relation subject/object IDs to match normalized entity IDs
        const entityMap = new Map(normalizedEntities.map(e => [e.name.toLowerCase(), e.id]));
        const normalizedRelations = fact.relations.map(relation => {
            // Try to find matching entity IDs
            let subjectId = relation.subjectId;
            let objectId = relation.objectId;
            // If relation uses entity names instead of IDs, try to resolve
            for (const entry of Array.from(entityMap.entries())) {
                const [name, id] = entry;
                if (relation.subjectId.toLowerCase().includes(name)) {
                    subjectId = id;
                }
                if (relation.objectId.toLowerCase().includes(name)) {
                    objectId = id;
                }
            }
            return {
                ...relation,
                subjectId,
                objectId
            };
        });
        // Re-score importance
        const importance = this.scoreImportance(fact);
        return {
            ...fact,
            entities: normalizedEntities,
            relations: normalizedRelations,
            importance
        };
    }
}
exports.FactExtractor = FactExtractor;
// ============================================================================
// Convenience Functions
// ============================================================================
/**
 * Create a fact extractor with default configuration
 */
function createFactExtractor(llmClient, vectorStore, config) {
    return new FactExtractor(llmClient, vectorStore, config);
}
/**
 * Quick extraction function for simple use cases
 */
async function extractFactsFromText(text, llmClient, options) {
    // Create a minimal context
    const context = {
        userMessage: text,
        history: [{ role: 'user', content: text, timestamp: new Date() }],
        agentId: 'quick-extract',
        sessionId: 'quick-extract',
        tokenCount: 0,
        tokenLimit: 1000
    };
    const extractor = new FactExtractor(llmClient);
    const result = await extractor.extractFacts(context, 'explicit');
    // Apply options
    if (options?.type) {
        return result.facts.filter(f => f.type === options.type);
    }
    if (options?.importance) {
        return result.facts.filter(f => f.importance >= (options.importance || 1));
    }
    return result.facts;
}
/**
 * Detect if a message is an explicit memory command
 */
function isExplicitMemoryCommand(message) {
    const patterns = [
        /^(remember|note|don't forget|keep in mind|make sure to remember)\s+(that|to|the|this|how|what|when|where|why|which)/i,
        /^(i prefer|i like|i hate|i dislike|i want|i need|i always|i never)\s+/i,
        /^(important|critical|essential|vital):\s*/i,
        /^forget\s+(that|about|the)\s+/i,
        /^(add|save|store)\s+(to\s+)?memory/i
    ];
    return patterns.some(pattern => pattern.test(message.trim()));
}
/**
 * Parse an explicit memory command to extract the core content
 */
function parseExplicitMemoryCommand(message) {
    const trimmed = message.trim();
    // Check for forget commands
    if (/^forget\s+/i.test(trimmed)) {
        return {
            isMemoryCommand: true,
            commandType: 'forget',
            content: trimmed.replace(/^forget\s+/i, '').trim()
        };
    }
    // Check for update commands
    if (/^update\s+(memory|the\s+fact)\s+/i.test(trimmed)) {
        return {
            isMemoryCommand: true,
            commandType: 'update',
            content: trimmed.replace(/^update\s+(memory|the\s+fact)\s+/i, '').trim()
        };
    }
    // Check for remember commands
    const rememberPatterns = [
        /^(remember|note|don't forget|keep in mind|make sure to remember)\s+(that\s+)?/i,
        /^(important|critical|essential|vital):\s*/i,
        /^(add|save|store)\s+(to\s+memory\s+)?(that\s+)?/i
    ];
    for (const pattern of rememberPatterns) {
        if (pattern.test(trimmed)) {
            return {
                isMemoryCommand: true,
                commandType: 'remember',
                content: trimmed.replace(pattern, '').trim()
            };
        }
    }
    // Check for preference/need statements
    const preferencePatterns = [
        /^(i prefer|i like|i hate|i dislike|i want|i need)\s+/i
    ];
    for (const pattern of preferencePatterns) {
        if (pattern.test(trimmed)) {
            return {
                isMemoryCommand: true,
                commandType: 'remember',
                content: trimmed
            };
        }
    }
    return {
        isMemoryCommand: false,
        commandType: 'remember',
        content: trimmed
    };
}
//# sourceMappingURL=extractor.js.map