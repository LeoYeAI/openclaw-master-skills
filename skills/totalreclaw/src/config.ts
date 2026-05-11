/**
 * TotalReclaw Skill - Configuration Module
 *
 * Handles loading, merging, and validating configuration from multiple sources:
 * - skill.json defaults
 * - OpenClaw config (agents.defaults.totalreclaw.*)
 * - Environment variables (TOTALRECLAW_*)
 */

import type { TotalReclawSkillConfig } from './types';
import { DEFAULT_SKILL_CONFIG } from './types';

// ============================================================================
// Types
// ============================================================================

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
 * Skill.json configuration defaults (extracted from skill.json)
 */
const SKILL_JSON_DEFAULTS: TotalReclawSkillConfig = {
  serverUrl: 'http://127.0.0.1:8080',
  autoExtractEveryTurns: 3,
  minImportanceForAutoStore: 6,
  maxMemoriesInContext: 8,
  forgetThreshold: 0.3,
  rerankerModel: 'BAAI/bge-reranker-base',
};

// ============================================================================
// Environment Variable Mapping
// ============================================================================

/**
 * Maps environment variable names to config keys and their parsers
 */
const ENV_VAR_MAPPING: Record<
  string,
  { key: keyof TotalReclawSkillConfig; parser: (value: string) => unknown }
> = {
  TOTALRECLAW_SERVER_URL: {
    key: 'serverUrl',
    parser: (v) => v,
  },
  TOTALRECLAW_AUTO_EXTRACT_EVERY_TURNS: {
    key: 'autoExtractEveryTurns',
    parser: (v) => parseInt(v, 10),
  },
  TOTALRECLAW_MIN_IMPORTANCE: {
    key: 'minImportanceForAutoStore',
    parser: (v) => parseInt(v, 10),
  },
  TOTALRECLAW_MAX_MEMORIES: {
    key: 'maxMemoriesInContext',
    parser: (v) => parseInt(v, 10),
  },
  TOTALRECLAW_FORGET_THRESHOLD: {
    key: 'forgetThreshold',
    parser: (v) => parseFloat(v),
  },
  TOTALRECLAW_RERANKER_MODEL: {
    key: 'rerankerModel',
    parser: (v) => v,
  },
  TOTALRECLAW_RECOVERY_PHRASE: {
    key: 'masterPassword',
    parser: (v) => v,
  },
  TOTALRECLAW_USER_ID: {
    key: 'userId',
    parser: (v) => v,
  },
};

// ============================================================================
// Configuration Loading
// ============================================================================

/**
 * Load configuration from environment variables
 *
 * @returns Partial config from environment variables
 */
function loadFromEnv(): Partial<TotalReclawSkillConfig> {
  const config: Partial<TotalReclawSkillConfig> = {};

  for (const [envVar, mapping] of Object.entries(ENV_VAR_MAPPING)) {
    const value = process.env[envVar];
    if (value !== undefined && value !== '') {
      try {
        (config as Record<string, unknown>)[mapping.key] = mapping.parser(value);
      } catch {
        // Skip invalid values - validation will catch them
        console.warn(`Failed to parse environment variable ${envVar}: ${value}`);
      }
    }
  }

  return config;
}

/**
 * Load configuration from OpenClaw config object
 *
 * @param openclawConfig - OpenClaw configuration object
 * @returns Partial config from OpenClaw
 */
function loadFromOpenClaw(openclawConfig?: OpenClawConfig): Partial<TotalReclawSkillConfig> {
  return openclawConfig?.agents?.defaults?.totalreclaw ?? {};
}

/**
 * Load skill.json defaults
 *
 * @returns Default configuration from skill.json
 */
function loadFromSkillJson(): TotalReclawSkillConfig {
  return { ...SKILL_JSON_DEFAULTS };
}

/**
 * Deep merge configuration objects
 * Later objects override earlier ones
 *
 * @param sources - Configuration sources to merge (in priority order, lowest first)
 * @returns Merged configuration
 */
function mergeConfigs(...sources: Partial<TotalReclawSkillConfig>[]): TotalReclawSkillConfig {
  const result = { ...DEFAULT_SKILL_CONFIG };

  for (const source of sources) {
    for (const [key, value] of Object.entries(source)) {
      if (value !== undefined) {
        (result as Record<string, unknown>)[key] = value;
      }
    }
  }

  return result;
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
export function loadConfig(options?: {
  /** OpenClaw configuration object */
  openclawConfig?: OpenClawConfig;
  /** Explicit configuration overrides */
  overrides?: Partial<TotalReclawSkillConfig>;
}): TotalReclawSkillConfig {
  const { openclawConfig, overrides } = options ?? {};

  // Load from all sources (in priority order, lowest to highest)
  const skillJsonDefaults = loadFromSkillJson();
  const openclawPartial = loadFromOpenClaw(openclawConfig);
  const envPartial = loadFromEnv();

  // Merge all sources (later sources override earlier ones)
  return mergeConfigs(skillJsonDefaults, openclawPartial, envPartial, overrides ?? {});
}

// ============================================================================
// Configuration Validation
// ============================================================================

/**
 * Validate that a string is a valid URL
 *
 * @param value - String to validate
 * @returns true if valid URL
 */
function isValidUrl(value: string): boolean {
  try {
    const url = new URL(value);
    return url.protocol === 'http:' || url.protocol === 'https:';
  } catch {
    return false;
  }
}

/**
 * Validate that a number is within a range (inclusive)
 *
 * @param value - Number to validate
 * @param min - Minimum value (inclusive)
 * @param max - Maximum value (inclusive)
 * @returns true if within range
 */
function isInRange(value: number, min: number, max: number): boolean {
  return typeof value === 'number' && !isNaN(value) && value >= min && value <= max;
}

/**
 * Field validators for configuration
 */
const FIELD_VALIDATORS: Record<
  keyof TotalReclawSkillConfig,
  {
    validate: (value: unknown) => boolean;
    getError: (value: unknown) => string;
    getWarning?: (value: unknown) => string | null;
    required?: boolean;
  }
> = {
  serverUrl: {
    validate: (v) => typeof v === 'string' && isValidUrl(v),
    getError: (v) => `Invalid serverUrl: "${v}" is not a valid HTTP/HTTPS URL`,
    getWarning: (v) => {
      if (typeof v === 'string' && v.startsWith('http://')) {
        return 'Using HTTP (not HTTPS) for serverUrl - not recommended for production';
      }
      return null;
    },
    required: true,
  },
  autoExtractEveryTurns: {
    validate: (v) => typeof v === 'number' && isInRange(v, 1, 100),
    getError: (v) => `Invalid autoExtractEveryTurns: ${v} (must be 1-100)`,
    required: true,
  },
  minImportanceForAutoStore: {
    validate: (v) => typeof v === 'number' && isInRange(v, 1, 10),
    getError: (v) => `Invalid minImportanceForAutoStore: ${v} (must be 1-10)`,
    required: true,
  },
  maxMemoriesInContext: {
    validate: (v) => typeof v === 'number' && isInRange(v, 1, 50),
    getError: (v) => `Invalid maxMemoriesInContext: ${v} (must be 1-50)`,
    getWarning: (v) => {
      if (typeof v === 'number' && v > 20) {
        return `High maxMemoriesInContext (${v}) may impact context window usage`;
      }
      return null;
    },
    required: true,
  },
  forgetThreshold: {
    validate: (v) => typeof v === 'number' && isInRange(v, 0, 1),
    getError: (v) => `Invalid forgetThreshold: ${v} (must be 0-1)`,
    getWarning: (v) => {
      if (typeof v === 'number') {
        if (v < 0.1) {
          return `Very low forgetThreshold (${v}) may cause memory bloat`;
        }
        if (v > 0.8) {
          return `High forgetThreshold (${v}) may cause excessive memory loss`;
        }
      }
      return null;
    },
    required: true,
  },
  rerankerModel: {
    validate: (v) => v === undefined || (typeof v === 'string' && v.length > 0),
    getError: (v) => `Invalid rerankerModel: ${v} (must be a non-empty string or undefined)`,
    required: false,
  },
  masterPassword: {
    validate: (v) => v === undefined || typeof v === 'string',
    getError: (v) => `Invalid masterPassword: must be a string or undefined`,
    required: false,
  },
  userId: {
    validate: (v) => v === undefined || typeof v === 'string',
    getError: (v) => `Invalid userId: must be a string or undefined`,
    required: false,
  },
  salt: {
    validate: (v) => v === undefined || Buffer.isBuffer(v),
    getError: (v) => `Invalid salt: must be a Buffer or undefined`,
    required: false,
  },
};

/**
 * Validate configuration values
 *
 * @param config - Configuration to validate
 * @returns Validation result with errors and warnings
 */
export function validateConfig(config: TotalReclawSkillConfig): ConfigValidationResult {
  const errors: ConfigValidationError[] = [];
  const warnings: ConfigValidationWarning[] = [];

  // Validate each field
  for (const [field, validator] of Object.entries(FIELD_VALIDATORS)) {
    const value = config[field as keyof TotalReclawSkillConfig];

    // Check required fields
    if (validator.required && value === undefined) {
      errors.push({
        field,
        value,
        message: `Missing required field: ${field}`,
      });
      continue;
    }

    // Skip validation for undefined optional fields
    if (value === undefined && !validator.required) {
      continue;
    }

    // Validate value
    if (!validator.validate(value)) {
      errors.push({
        field,
        value,
        message: validator.getError(value),
      });
    }

    // Check for warnings
    if (validator.getWarning) {
      const warning = validator.getWarning(value);
      if (warning) {
        warnings.push({
          field,
          value,
          message: warning,
        });
      }
    }
  }

  // Additional cross-field validations
  if (
    config.masterPassword &&
    typeof config.masterPassword === 'string' &&
    config.masterPassword.length < 12
  ) {
    warnings.push({
      field: 'masterPassword',
      value: '[REDACTED]',
      message: 'masterPassword is shorter than recommended (12+ characters)',
    });
  }

  return {
    valid: errors.length === 0,
    errors,
    warnings,
  };
}

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Assert that configuration is valid, throwing on errors
 *
 * @param config - Configuration to validate
 * @throws Error if configuration is invalid
 */
export function assertValidConfig(config: TotalReclawSkillConfig): void {
  const result = validateConfig(config);

  if (!result.valid) {
    const errorMessages = result.errors.map((e) => `  - ${e.field}: ${e.message}`).join('\n');
    throw new Error(`Invalid TotalReclaw configuration:\n${errorMessages}`);
  }

  // Log warnings
  for (const warning of result.warnings) {
    console.warn(`[TotalReclaw] Config warning - ${warning.field}: ${warning.message}`);
  }
}

/**
 * Create a configuration with defaults and validate it
 *
 * @param partial - Partial configuration to merge with defaults
 * @param options - Additional loading options
 * @returns Validated, complete configuration
 * @throws Error if resulting configuration is invalid
 */
export function createConfig(
  partial?: Partial<TotalReclawSkillConfig>,
  options?: Parameters<typeof loadConfig>[0],
): TotalReclawSkillConfig {
  const config = loadConfig({
    ...options,
    overrides: partial,
  });

  assertValidConfig(config);
  return config;
}
