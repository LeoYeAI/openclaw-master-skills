import * as fs from 'fs';
import * as yaml from 'yaml';
import { SecurityConfig, Severity, Action } from '../types';

/**
 * ConfigManager handles loading and validating security configuration from YAML files.
 * Supports deep merging of user configs with defaults and comprehensive validation.
 */
export class ConfigManager {
  /**
   * Returns the default security configuration.
   * This is used when no config file exists or as a base for merging user configs.
   */
  static getDefaultConfig(): SecurityConfig {
    return {
      enabled: true,
      sensitivity: 'medium',
      owner_ids: [],
      modules: {
        prompt_injection: { enabled: true },
        command_validator: { enabled: true },
        url_validator: { enabled: true },
        path_validator: { enabled: true },
        secret_detector: { enabled: true },
        content_scanner: { enabled: true },
        injection_validator: { enabled: true },
        exfiltration_detector: { enabled: true },
        code_execution_detector: { enabled: true },
        serialization_detector: { enabled: true }
      },
      actions: {
        [Severity.SAFE]: Action.ALLOW,
        [Severity.LOW]: Action.LOG,
        [Severity.MEDIUM]: Action.WARN,
        [Severity.HIGH]: Action.BLOCK,
        [Severity.CRITICAL]: Action.BLOCK_NOTIFY
      },
      rate_limit: {
        enabled: true,
        max_requests_per_minute: 30,
        lockout_threshold: 5
      },
      notifications: {
        enabled: false,
        channels: {},
        severity_threshold: Severity.HIGH
      },
      logging: {
        enabled: true,
        level: 'info',
        file: '~/.openclaw/logs/security-events.log',
        rotation: 'daily',
        retention_days: 90
      },
      database: {
        path: '.openclaw-sec.db',
        analytics_enabled: true,
        retention_days: 365
      }
    };
  }

  /**
   * Loads configuration from a YAML file, merging with defaults.
   * Returns default config if file doesn't exist.
   *
   * @param configPath - Path to the YAML config file
   * @returns Promise<SecurityConfig> - The merged and validated configuration
   * @throws Error if YAML is invalid or config validation fails
   */
  static async load(configPath: string): Promise<SecurityConfig> {
    // Return defaults if file doesn't exist
    if (!fs.existsSync(configPath)) {
      return this.getDefaultConfig();
    }

    try {
      // Read and parse YAML file
      const fileContent = fs.readFileSync(configPath, 'utf8');
      const parsed = yaml.parse(fileContent);

      if (!parsed) {
        throw new Error(`Invalid YAML in config file: ${configPath}`);
      }

      // Extract openclaw_security section
      const userConfig = parsed.openclaw_security || {};
      const defaultConfig = this.getDefaultConfig();

      // Deep merge user config with defaults
      const merged = this.deepMerge(defaultConfig, userConfig);

      // Validate the merged configuration
      this.validateConfig(merged);

      return merged;
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Failed to load config from ${configPath}: ${error.message}`);
      }
      throw error;
    }
  }

  /**
   * Deep merges two objects, with source values overriding target values.
   * Arrays are replaced entirely, not merged.
   *
   * @param target - The base object
   * @param source - The object to merge in
   * @returns The merged object
   */
  static deepMerge(target: any, source: any): any {
    const output = { ...target };

    if (this.isObject(target) && this.isObject(source)) {
      Object.keys(source).forEach(key => {
        if (this.isObject(source[key]) && !Array.isArray(source[key])) {
          if (!(key in target)) {
            output[key] = source[key];
          } else {
            output[key] = this.deepMerge(target[key], source[key]);
          }
        } else {
          // Replace arrays and primitive values entirely
          output[key] = source[key];
        }
      });
    }

    return output;
  }

  /**
   * Checks if a value is a plain object (not null, array, or other type).
   */
  private static isObject(item: any): boolean {
    return item && typeof item === 'object' && !Array.isArray(item);
  }

  /**
   * Validates a security configuration.
   * Checks sensitivity levels and actions for correctness.
   *
   * @param config - The config to validate
   * @throws Error if validation fails
   */
  static validateConfig(config: SecurityConfig): void {
    // Validate sensitivity level
    const validSensitivities: Array<SecurityConfig['sensitivity']> = [
      'paranoid',
      'strict',
      'medium',
      'permissive'
    ];

    if (!validSensitivities.includes(config.sensitivity)) {
      throw new Error(`Invalid sensitivity level: ${config.sensitivity}. Must be one of: ${validSensitivities.join(', ')}`);
    }

    // Validate actions
    const validActions = Object.values(Action);

    if (config.actions) {
      Object.entries(config.actions).forEach(([severity, action]) => {
        if (!validActions.includes(action)) {
          throw new Error(`Invalid action for ${severity}: ${action}. Must be one of: ${validActions.join(', ')}`);
        }
      });
    }

    // Validate module-specific sensitivity levels if present
    if (config.modules) {
      Object.entries(config.modules).forEach(([moduleName, moduleConfig]) => {
        if (moduleConfig.sensitivity && !validSensitivities.includes(moduleConfig.sensitivity)) {
          throw new Error(`Invalid sensitivity level for module ${moduleName}: ${moduleConfig.sensitivity}`);
        }
      });
    }
  }
}
