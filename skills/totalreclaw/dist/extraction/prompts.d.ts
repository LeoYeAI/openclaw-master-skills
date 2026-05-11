/**
 * TotalReclaw Skill - LLM Prompts for Fact Extraction
 *
 * Prompts follow Mem0-style ADD/UPDATE/DELETE/NOOP pattern for
 * intelligent deduplication and conflict resolution.
 */
import type { ExtractedFact } from '../types';
/**
 * JSON schema for extraction response validation
 */
export declare const EXTRACTION_RESPONSE_SCHEMA: {
    type: string;
    properties: {
        facts: {
            type: string;
            items: {
                type: string;
                properties: {
                    factText: {
                        type: string;
                        maxLength: number;
                    };
                    type: {
                        type: string;
                        enum: string[];
                    };
                    importance: {
                        type: string;
                        minimum: number;
                        maximum: number;
                    };
                    confidence: {
                        type: string;
                        minimum: number;
                        maximum: number;
                    };
                    action: {
                        type: string;
                        enum: string[];
                    };
                    existingFactId: {
                        type: string;
                    };
                    entities: {
                        type: string;
                        items: {
                            type: string;
                            properties: {
                                id: {
                                    type: string;
                                };
                                name: {
                                    type: string;
                                };
                                type: {
                                    type: string;
                                };
                            };
                            required: string[];
                        };
                    };
                    relations: {
                        type: string;
                        items: {
                            type: string;
                            properties: {
                                subjectId: {
                                    type: string;
                                };
                                predicate: {
                                    type: string;
                                };
                                objectId: {
                                    type: string;
                                };
                                confidence: {
                                    type: string;
                                    minimum: number;
                                    maximum: number;
                                };
                            };
                            required: string[];
                        };
                    };
                    reasoning: {
                        type: string;
                    };
                };
                required: string[];
            };
        };
        metadata: {
            type: string;
            properties: {
                totalTurnsAnalyzed: {
                    type: string;
                };
                extractionTimestamp: {
                    type: string;
                };
            };
        };
    };
    required: string[];
};
/**
 * JSON schema for deduplication judge response
 */
export declare const DEDUP_JUDGE_SCHEMA: {
    type: string;
    properties: {
        decision: {
            type: string;
            enum: string[];
        };
        existingFactId: {
            type: string;
        };
        confidence: {
            type: string;
            minimum: number;
            maximum: number;
        };
        reasoning: {
            type: string;
        };
    };
    required: string[];
};
/**
 * Pre-compaction prompt - comprehensive extraction from last 20 turns
 */
export declare const PRE_COMPACTION_PROMPT: {
    system: string;
    user: string;
    /**
     * Format the pre-compaction prompt with actual data
     */
    format(context: {
        conversationHistory: string;
        existingMemories: string;
    }): {
        system: string;
        user: string;
    };
};
/**
 * Post-turn prompt - lightweight extraction from last 3 turns
 */
export declare const POST_TURN_PROMPT: {
    system: string;
    user: string;
    /**
     * Format the post-turn prompt with actual data
     */
    format(context: {
        conversationHistory: string;
        existingMemories: string;
    }): {
        system: string;
        user: string;
    };
};
/**
 * Explicit command prompt - for "remember that..." style commands
 */
export declare const EXPLICIT_COMMAND_PROMPT: {
    system: string;
    user: string;
    /**
     * Format the explicit command prompt with actual data
     */
    format(context: {
        userRequest: string;
        conversationContext: string;
    }): {
        system: string;
        user: string;
    };
};
/**
 * LLM judge prompt for determining ADD vs UPDATE vs DELETE
 */
export declare const DEDUP_JUDGE_PROMPT: {
    system: string;
    user: string;
    /**
     * Format the dedup judge prompt with actual data
     */
    format(context: {
        newFact: string;
        existingFacts: string;
    }): {
        system: string;
        user: string;
    };
};
/**
 * Contradiction detection prompt
 */
export declare const CONTRADICTION_DETECTION_PROMPT: {
    system: string;
    user: string;
    format(context: {
        factA: string;
        factB: string;
    }): {
        system: string;
        user: string;
    };
};
/**
 * Entity extraction prompt (can be used standalone)
 */
export declare const ENTITY_EXTRACTION_PROMPT: {
    system: string;
    user: string;
    format(text: string): {
        system: string;
        user: string;
    };
};
/**
 * Format conversation history for prompts
 */
export declare function formatConversationHistory(turns: Array<{
    role: 'user' | 'assistant';
    content: string;
    timestamp: Date;
}>): string;
/**
 * Format existing memories for deduplication context
 */
export declare function formatExistingMemories(memories: Array<{
    id: string;
    factText: string;
    type: string;
    importance: number;
}>): string;
/**
 * Generate a stable entity ID from name and type
 */
export declare function generateEntityId(name: string, type: string): string;
/**
 * Validate extraction response against schema
 */
export declare function validateExtractionResponse(response: unknown): {
    valid: boolean;
    errors: string[];
    facts?: ExtractedFact[];
};
/**
 * All extraction prompts bundled together
 */
export declare const EXTRACTION_PROMPTS: {
    preCompaction: {
        system: string;
        user: string;
        /**
         * Format the pre-compaction prompt with actual data
         */
        format(context: {
            conversationHistory: string;
            existingMemories: string;
        }): {
            system: string;
            user: string;
        };
    };
    postTurn: {
        system: string;
        user: string;
        /**
         * Format the post-turn prompt with actual data
         */
        format(context: {
            conversationHistory: string;
            existingMemories: string;
        }): {
            system: string;
            user: string;
        };
    };
    explicitCommand: {
        system: string;
        user: string;
        /**
         * Format the explicit command prompt with actual data
         */
        format(context: {
            userRequest: string;
            conversationContext: string;
        }): {
            system: string;
            user: string;
        };
    };
    dedupJudge: {
        system: string;
        user: string;
        /**
         * Format the dedup judge prompt with actual data
         */
        format(context: {
            newFact: string;
            existingFacts: string;
        }): {
            system: string;
            user: string;
        };
    };
    contradictionDetection: {
        system: string;
        user: string;
        format(context: {
            factA: string;
            factB: string;
        }): {
            system: string;
            user: string;
        };
    };
    entityExtraction: {
        system: string;
        user: string;
        format(text: string): {
            system: string;
            user: string;
        };
    };
};
//# sourceMappingURL=prompts.d.ts.map