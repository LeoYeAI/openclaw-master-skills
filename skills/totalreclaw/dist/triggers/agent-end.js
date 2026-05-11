"use strict";
/**
 * TotalReclaw Skill - Agent End Hook
 *
 * This hook runs AFTER the agent completes its turn.
 * It extracts facts from the recent conversation and stores them.
 *
 * Flow:
 * 1. Check turn counter (only extract every N turns)
 * 2. Extract facts from recent conversation
 * 3. Deduplicate against existing memories
 * 4. Store high-importance facts
 * 5. Return AgentEndResult with stats
 *
 * This hook is ASYNC and does NOT block the user.
 */
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || (function () {
    var ownKeys = function(o) {
        ownKeys = Object.getOwnPropertyNames || function (o) {
            var ar = [];
            for (var k in o) if (Object.prototype.hasOwnProperty.call(o, k)) ar[ar.length] = k;
            return ar;
        };
        return ownKeys(o);
    };
    return function (mod) {
        if (mod && mod.__esModule) return mod;
        var result = {};
        if (mod != null) for (var k = ownKeys(mod), i = 0; i < k.length; i++) if (k[i] !== "default") __createBinding(result, mod, k[i]);
        __setModuleDefault(result, mod);
        return result;
    };
})();
Object.defineProperty(exports, "__esModule", { value: true });
exports.agentEnd = agentEnd;
const fs = __importStar(require("fs"));
const path = __importStar(require("path"));
const os = __importStar(require("os"));
const extraction_1 = require("../extraction");
const debug_1 = require("../debug");
const BILLING_CACHE_PATH = path.join(os.homedir(), '.totalreclaw', 'billing-cache.json');
// ============================================================================
// Main Hook Function
// ============================================================================
/**
 * Execute the agent-end hook
 *
 * This extracts facts from the conversation and stores them asynchronously.
 *
 * @param context - OpenClaw context containing user message and history
 * @param options - Hook options including client and configuration
 * @returns AgentEndResult with extraction and storage stats
 *
 * @example
 * ```typescript
 * const result = await agentEnd(context, {
 *   client: openMemoryClient,
 *   config: skillConfig,
 *   state: skillState,
 *   llmClient: myLLMClient,
 * });
 *
 * console.log(`Extracted ${result.factsExtracted} facts, stored ${result.factsStored}`);
 * ```
 */
async function agentEnd(context, options) {
    const startTime = Date.now();
    // Update turn counter
    options.state.turnCount++;
    (0, debug_1.debugLog)(!!options.debug, `Agent end hook - Turn ${options.state.turnCount}`);
    try {
        // Step 1: Check if we should extract this turn
        const shouldExtract = shouldExtractThisTurn(context, options);
        if (!shouldExtract) {
            (0, debug_1.debugLog)(!!options.debug, `Skipping extraction this turn`);
            return {
                factsExtracted: 0,
                factsStored: 0,
                processingTimeMs: Date.now() - startTime,
            };
        }
        // Step 2: Run extraction (can be async)
        if (options.async) {
            // Fire and forget - don't await
            runExtractionAsync(context, options).catch(error => {
                console.error('[TotalReclaw] Async extraction failed:', error);
            });
            return {
                factsExtracted: 0, // Will be updated asynchronously
                factsStored: 0,
                processingTimeMs: Date.now() - startTime,
            };
        }
        // Step 3: Run extraction synchronously
        const result = await runExtraction(context, options);
        // Propagate quota exceeded info
        if (result.quotaExceeded) {
            return {
                factsExtracted: result.factsExtracted,
                factsStored: result.factsStored,
                processingTimeMs: Date.now() - startTime,
                quotaExceeded: true,
                quotaMessage: result.quotaMessage,
            };
        }
        return {
            factsExtracted: result.factsExtracted,
            factsStored: result.factsStored,
            processingTimeMs: Date.now() - startTime,
        };
    }
    catch (error) {
        const errorMsg = error instanceof Error ? error.message : 'Unknown error';
        console.error('[TotalReclaw] agentEnd hook failed:', errorMsg);
        return {
            factsExtracted: 0,
            factsStored: 0,
            processingTimeMs: Date.now() - startTime,
        };
    }
}
// ============================================================================
// Helper Functions
// ============================================================================
/**
 * Determine if we should extract facts this turn
 */
function shouldExtractThisTurn(context, options) {
    const { config, state } = options;
    // Always extract for explicit memory commands
    if ((0, extraction_1.isExplicitMemoryCommand)(context.userMessage)) {
        (0, debug_1.debugLog)(!!options.debug, `Explicit memory command detected`);
        return true;
    }
    // Check if turn counter matches extraction interval
    if (state.turnCount % config.autoExtractEveryTurns === 0) {
        return true;
    }
    // Check if we have pending extractions
    if (state.pendingExtractions.length > 0) {
        return true;
    }
    return false;
}
/**
 * Run extraction asynchronously (fire and forget)
 */
async function runExtractionAsync(context, options) {
    const result = await runExtraction(context, options);
    (0, debug_1.debugLog)(!!options.debug, `Async extraction completed: ${result.factsExtracted} extracted, ` +
        `${result.factsStored} stored, ${result.factsSkipped} skipped`);
}
/**
 * Run the actual extraction and storage
 */
async function runExtraction(context, options) {
    const result = {
        factsExtracted: 0,
        factsStored: 0,
        factsSkipped: 0,
        processingTimeMs: 0,
    };
    const startTime = Date.now();
    try {
        // Get or create fact extractor
        const extractor = options.extractor || (0, extraction_1.createFactExtractor)(options.llmClient, options.vectorStoreClient, {
            minImportance: options.config.minImportanceForAutoStore,
            postTurnWindow: 3, // Last 3 turns
        });
        // Determine extraction trigger
        const trigger = (0, extraction_1.isExplicitMemoryCommand)(context.userMessage) ? 'explicit' : 'post_turn';
        // Extract facts from conversation
        const extractionResult = await extractor.extractFacts(context, trigger);
        result.factsExtracted = extractionResult.facts.length;
        (0, debug_1.debugLog)(!!options.debug, `Extracted ${result.factsExtracted} facts in ${extractionResult.processingTimeMs}ms`);
        // Filter and store facts
        for (const fact of extractionResult.facts) {
            // Skip NOOP facts
            if (fact.action === 'NOOP') {
                result.factsSkipped++;
                continue;
            }
            // Skip low importance facts (unless explicit command)
            if (trigger !== 'explicit' && fact.importance < options.config.minImportanceForAutoStore) {
                result.factsSkipped++;
                continue;
            }
            // Store the fact
            try {
                await storeFact(fact, options);
                result.factsStored++;
                (0, debug_1.debugLog)(!!options.debug, `Stored fact: "${fact.factText}" (importance: ${fact.importance})`);
            }
            catch (storeError) {
                const storeErrorMsg = storeError instanceof Error ? storeError.message : String(storeError);
                // Check for 403 quota exceeded
                if (storeErrorMsg.includes('403') || storeErrorMsg.includes('quota') || storeErrorMsg.includes('Quota')) {
                    (0, debug_1.debugLog)(!!options.debug, `Quota exceeded (403) during store: ${storeErrorMsg}`);
                    // Invalidate billing cache so next before_agent_start refreshes
                    try {
                        if (fs.existsSync(BILLING_CACHE_PATH)) {
                            fs.unlinkSync(BILLING_CACHE_PATH);
                        }
                    }
                    catch (e) {
                        (0, debug_1.debugLog)(!!options.debug, 'Failed to invalidate billing cache:', e);
                    }
                    result.quotaExceeded = true;
                    result.quotaMessage = 'TotalReclaw quota exceeded. New memories cannot be stored until the quota resets next month or you upgrade your plan.';
                    // Stop trying to store more facts
                    break;
                }
                console.error(`[TotalReclaw] Failed to store fact:`, storeError);
                result.factsSkipped++;
            }
        }
        // Update state
        options.state.lastExtraction = new Date();
        options.state.pendingExtractions = [];
    }
    catch (error) {
        const errorMsg = error instanceof Error ? error.message : 'Unknown error';
        console.error('[TotalReclaw] Extraction failed:', errorMsg);
    }
    result.processingTimeMs = Date.now() - startTime;
    return result;
}
/**
 * Store a single fact in TotalReclaw
 */
async function storeFact(fact, options) {
    const { client, config } = options;
    switch (fact.action) {
        case 'ADD':
            // Store new fact
            await client.remember(fact.factText, {
                importance: fact.importance / 10, // Normalize to 0-1
                source: 'extracted',
                tags: [fact.type],
            });
            break;
        case 'UPDATE':
            // Delete old and add new (simple update strategy)
            if (fact.existingFactId) {
                try {
                    await client.forget(fact.existingFactId);
                }
                catch {
                    // Ignore if old fact doesn't exist
                }
            }
            await client.remember(fact.factText, {
                importance: fact.importance / 10,
                source: 'extracted',
                tags: [fact.type],
            });
            break;
        case 'DELETE':
            // Delete existing fact
            if (fact.existingFactId) {
                await client.forget(fact.existingFactId);
            }
            break;
        case 'NOOP':
        default:
            // Do nothing
            break;
    }
}
// ============================================================================
// Exports
// ============================================================================
exports.default = agentEnd;
//# sourceMappingURL=agent-end.js.map