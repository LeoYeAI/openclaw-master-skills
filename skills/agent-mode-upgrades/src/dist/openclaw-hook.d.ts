/**
 * OpenClaw Hook for Enhanced Agentic Loop
 *
 * This file should be copied to:
 *   src/agents/enhanced-loop-hook.ts
 *
 * Then add this to src/agents/pi-embedded-runner/run.ts:
 *
 *   import { tryLoadEnhancedLoop, isEnhancedLoopEnabled } from '../enhanced-loop-hook.js';
 *
 *   // At the start of runEmbeddedPiAgent:
 *   if (isEnhancedLoopEnabled(params.config)) {
 *     const enhancedLoop = tryLoadEnhancedLoop(params.config);
 *     if (enhancedLoop) {
 *       return enhancedLoop.wrapRun(params, runEmbeddedAttempt);
 *     }
 *   }
 */
export interface EnhancedLoopConfig {
    enabled: boolean;
    planning: {
        enabled: boolean;
        reflectionAfterTools: boolean;
        maxPlanSteps: number;
    };
    execution: {
        parallelTools: boolean;
        maxConcurrentTools: number;
        confidenceGates: boolean;
        confidenceThreshold: number;
    };
    context: {
        proactiveManagement: boolean;
        summarizeAfterIterations: number;
        contextThreshold: number;
    };
    errorRecovery: {
        enabled: boolean;
        maxAttempts: number;
        learnFromErrors: boolean;
    };
    stateMachine: {
        enabled: boolean;
        logging: boolean;
        metrics: boolean;
    };
}
/**
 * Load enhanced loop configuration
 */
export declare function loadEnhancedLoopConfig(): Promise<EnhancedLoopConfig>;
/**
 * Check if enhanced loop is enabled (sync, uses cache)
 */
export declare function isEnhancedLoopEnabled(openclawConfig?: {
    agents?: {
        enhancedLoop?: {
            enabled?: boolean;
        };
    };
}): boolean;
/**
 * Check if enhanced loop is enabled (async, loads fresh config)
 */
export declare function checkEnhancedLoopEnabled(): Promise<boolean>;
export interface EnhancedLoopWrapper {
    config: EnhancedLoopConfig;
    wrapRun: (params: unknown, originalRunner: (params: unknown) => Promise<unknown>) => Promise<unknown>;
}
/**
 * Try to load and initialize the enhanced loop
 * Returns null if not enabled or loading fails
 */
export declare function tryLoadEnhancedLoop(openclawConfig?: {
    agents?: {
        enhancedLoop?: {
            enabled?: boolean;
        };
    };
}): Promise<EnhancedLoopWrapper | null>;
//# sourceMappingURL=openclaw-hook.d.ts.map