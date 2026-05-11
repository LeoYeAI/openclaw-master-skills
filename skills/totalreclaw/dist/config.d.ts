/**
 * TotalReclaw Skill - Configuration Module
 *
 * Handles loading, merging, and validating configuration from multiple sources:
 * - skill.json defaults
 * - OpenClaw config (agents.defaults.totalreclaw.*)
 * - Environment variables (TOTALRECLAW_*)
 */
import type { TotalReclawSkillConfig } from './types';
/**
 * Result of configuration validation
 */
export interface ConfigValidationResult {
    valid: boolean;
    errors: ConfigValidationError[];
    warnings: ConfigValidationWarning[];
}
/**
 * Configuration validation error
 */
export interface ConfigValidationError {
    field: string;
    value: unknown;
    message: string;
}
/**
 * Configuration validation warning
 */
export interface ConfigValidationWarning {
    field: string;
    value: unknown;
    message: string;
}
/**
 * OpenClaw configuration structure (subset we care about)
 */
interface OpenClawConfig {
    agents?: {
        defaults?: {
            totalreclaw?: Partial<TotalReclawSkillConfig>;
        };
    };
}
/**
 * Load configuration from all sources with proper priority
 *
 * Priority order (highest last):
 * 1. skill.json defaults
 * 2. OpenClaw config (agents.defaults.totalreclaw.*)
 * 3. Environment variables (TOTALRECLAW_*)
 * 4. Explicit overrides (passed to this function)
 *
 * @param options - Loading options
 * @returns Complete, merged configuration
 */
export declare function loadConfig(options?: {
    /** OpenClaw configuration object */
    openclawConfig?: OpenClawConfig;
    /** Explicit configuration overrides */
    overrides?: Partial<TotalReclawSkillConfig>;
}): TotalReclawSkillConfig;
/**
 * Validate configuration values
 *
 * @param config - Configuration to validate
 * @returns Validation result with errors and warnings
 */
export declare function validateConfig(config: TotalReclawSkillConfig): ConfigValidationResult;
/**
 * Assert that configuration is valid, throwing on errors
 *
 * @param config - Configuration to validate
 * @throws Error if configuration is invalid
 */
export declare function assertValidConfig(config: TotalReclawSkillConfig): void;
/**
 * Create a configuration with defaults and validate it
 *
 * @param partial - Partial configuration to merge with defaults
 * @param options - Additional loading options
 * @returns Validated, complete configuration
 * @throws Error if resulting configuration is invalid
 */
export declare function createConfig(partial?: Partial<TotalReclawSkillConfig>, options?: Parameters<typeof loadConfig>[0]): TotalReclawSkillConfig;
export {};
//# sourceMappingURL=config.d.ts.map