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

import fs from "node:fs/promises";
import path from "node:path";
import { resolveOpenClawAgentDir } from "./agent-paths.js";

// ============================================================================
// Configuration
// ============================================================================

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

const DEFAULT_CONFIG: EnhancedLoopConfig = {
  enabled: false,
  planning: {
    enabled: true,
    reflectionAfterTools: true,
    maxPlanSteps: 7,
  },
  execution: {
    parallelTools: true,
    maxConcurrentTools: 5,
    confidenceGates: true,
    confidenceThreshold: 0.7,
  },
  context: {
    proactiveManagement: true,
    summarizeAfterIterations: 5,
    contextThreshold: 0.7,
  },
  errorRecovery: {
    enabled: true,
    maxAttempts: 3,
    learnFromErrors: true,
  },
  stateMachine: {
    enabled: true,
    logging: true,
    metrics: false,
  },
};

// ============================================================================
// Configuration Loading
// ============================================================================

function getConfigPath(): string {
  const agentDir = resolveOpenClawAgentDir();
  return path.join(agentDir, "enhanced-loop-config.json");
}

let cachedConfig: EnhancedLoopConfig | null = null;
let configLoadedAt = 0;
const CONFIG_TTL_MS = 5000; // Reload config every 5 seconds

/**
 * Load enhanced loop configuration
 */
export async function loadEnhancedLoopConfig(): Promise<EnhancedLoopConfig> {
  const now = Date.now();
  
  // Return cached config if fresh
  if (cachedConfig && now - configLoadedAt < CONFIG_TTL_MS) {
    return cachedConfig;
  }
  
  const configPath = getConfigPath();
  
  try {
    const content = await fs.readFile(configPath, "utf-8");
    const saved = JSON.parse(content) as { config?: Partial<EnhancedLoopConfig> };
    
    // Deep merge with defaults
    cachedConfig = deepMerge(DEFAULT_CONFIG, saved.config ?? {});
    configLoadedAt = now;
    
    return cachedConfig;
  } catch {
    // File doesn't exist or invalid - return defaults
    cachedConfig = { ...DEFAULT_CONFIG };
    configLoadedAt = now;
    return cachedConfig;
  }
}

/**
 * Check if enhanced loop is enabled (sync, uses cache)
 */
export function isEnhancedLoopEnabled(openclawConfig?: { agents?: { enhancedLoop?: { enabled?: boolean } } }): boolean {
  // Check main config first
  if (openclawConfig?.agents?.enhancedLoop?.enabled === true) {
    return true;
  }
  
  // Check cached config
  if (cachedConfig?.enabled) {
    return true;
  }
  
  return false;
}

/**
 * Check if enhanced loop is enabled (async, loads fresh config)
 */
export async function checkEnhancedLoopEnabled(): Promise<boolean> {
  const config = await loadEnhancedLoopConfig();
  return config.enabled;
}

// ============================================================================
// Enhanced Loop Wrapper
// ============================================================================

export interface EnhancedLoopWrapper {
  config: EnhancedLoopConfig;
  wrapRun: (params: unknown, originalRunner: (params: unknown) => Promise<unknown>) => Promise<unknown>;
}

/**
 * Try to load and initialize the enhanced loop
 * Returns null if not enabled or loading fails
 */
export async function tryLoadEnhancedLoop(
  openclawConfig?: { agents?: { enhancedLoop?: { enabled?: boolean } } }
): Promise<EnhancedLoopWrapper | null> {
  try {
    const config = await loadEnhancedLoopConfig();
    
    if (!config.enabled && !openclawConfig?.agents?.enhancedLoop?.enabled) {
      return null;
    }
    
    // For now, return a simple wrapper that logs and delegates
    // In full implementation, this would integrate the EnhancedAgentLoop class
    return {
      config,
      wrapRun: async (params, originalRunner) => {
        console.log("[enhanced-loop] Running with enhanced loop enabled");
        console.log("[enhanced-loop] Config:", JSON.stringify(config, null, 2));
        
        // For initial implementation, just run the original
        // Full integration would wrap with planning, parallel execution, etc.
        const result = await originalRunner(params);
        
        console.log("[enhanced-loop] Run completed");
        return result;
      },
    };
  } catch (err) {
    console.error("[enhanced-loop] Failed to load:", err);
    return null;
  }
}

// ============================================================================
// Utilities
// ============================================================================

function deepMerge<T extends object>(target: T, source: Partial<T>): T {
  const result = { ...target };

  for (const key of Object.keys(source) as Array<keyof T>) {
    const sourceValue = source[key];
    const targetValue = target[key];

    if (
      sourceValue !== undefined &&
      typeof sourceValue === "object" &&
      sourceValue !== null &&
      !Array.isArray(sourceValue) &&
      typeof targetValue === "object" &&
      targetValue !== null &&
      !Array.isArray(targetValue)
    ) {
      result[key] = deepMerge(
        targetValue as object,
        sourceValue as object
      ) as T[keyof T];
    } else if (sourceValue !== undefined) {
      result[key] = sourceValue as T[keyof T];
    }
  }

  return result;
}
