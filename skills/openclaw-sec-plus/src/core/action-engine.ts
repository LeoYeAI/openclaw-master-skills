import { Severity, Action, SecurityConfig } from '../types';
import { DatabaseManager } from './database-manager';

/**
 * Result of action determination
 */
export interface ActionResult {
  action: Action;
  reasoning: string;
  bypassReason?: 'owner' | 'allowlisted' | 'trusted';
  upgraded?: boolean;
}

/**
 * ActionEngine determines what action to take based on severity level,
 * user configuration, and user reputation.
 *
 * Decision hierarchy:
 * 1. Blocklisted users - always BLOCK
 * 2. Owner users - always ALLOW (unless CRITICAL)
 * 3. Allowlisted users - ALLOW for non-CRITICAL
 * 4. Low trust score - upgrade action by one level
 * 5. Default action mapping from config
 *
 * @example
 * ```typescript
 * const engine = new ActionEngine(config, dbManager);
 * const result = await engine.determineAction(Severity.HIGH, 'user-123');
 * console.log(result.action); // Action.BLOCK
 * console.log(result.reasoning); // "Severity HIGH maps to BLOCK action"
 * ```
 */
export class ActionEngine {
  private readonly config: SecurityConfig;
  private readonly dbManager: DatabaseManager;
  private readonly actionHierarchy: Action[] = [
    Action.ALLOW,
    Action.LOG,
    Action.WARN,
    Action.BLOCK,
    Action.BLOCK_NOTIFY
  ];

  /**
   * Default action mappings if not specified in config
   */
  private readonly defaultActionMap: Record<Severity, Action> = {
    [Severity.SAFE]: Action.ALLOW,
    [Severity.LOW]: Action.LOG,
    [Severity.MEDIUM]: Action.WARN,
    [Severity.HIGH]: Action.BLOCK,
    [Severity.CRITICAL]: Action.BLOCK_NOTIFY
  };

  /**
   * Creates a new ActionEngine instance
   *
   * @param config - Security configuration
   * @param dbManager - Database manager for reputation lookups
   * @throws Error if config or dbManager is missing
   */
  constructor(config: SecurityConfig, dbManager?: DatabaseManager | null) {
    if (!config) {
      throw new Error('Configuration is required');
    }
    this.config = config;
    this.dbManager = dbManager!;
  }

  /**
   * Determine the appropriate action for a given severity and user
   *
   * @param severity - The severity level from SeverityScorer
   * @param userId - The user ID to check reputation
   * @returns ActionResult with action and reasoning
   * @throws Error if severity is invalid or userId is missing
   */
  async determineAction(severity: Severity, userId: string): Promise<ActionResult> {
    // Validate inputs
    if (!Object.values(Severity).includes(severity)) {
      throw new Error(`Invalid severity: ${severity}`);
    }

    if (!userId || userId.trim().length === 0) {
      throw new Error('User ID is required');
    }

    // Get base action from config or defaults
    const baseAction = this.config.actions?.[severity] ?? this.defaultActionMap[severity];

    try {
      // Check if user is blocklisted
      const reputation = await this.getUserReputation(userId);
      if (reputation?.is_blocklisted === 1) {
        return {
          action: Action.BLOCK,
          reasoning: `User is blocklisted. All requests blocked regardless of severity.`
        };
      }

      // Check if user is an owner
      if (this.config.owner_ids.includes(userId)) {
        return {
          action: Action.ALLOW,
          reasoning: `User is an owner. Request allowed.`,
          bypassReason: 'owner'
        };
      }

      // Check if user is allowlisted (but not for CRITICAL severity)
      if (reputation?.is_allowlisted === 1 && severity !== Severity.CRITICAL) {
        return {
          action: Action.ALLOW,
          reasoning: `User is allowlisted. Severity ${severity} allowed.`,
          bypassReason: 'allowlisted'
        };
      }

      // Check trust score and potentially upgrade action
      if (reputation && reputation.trust_score < 20) {
        const upgradedAction = this.upgradeAction(baseAction);
        if (upgradedAction !== baseAction) {
          return {
            action: upgradedAction,
            reasoning: `Severity ${severity} with low trust score (${reputation.trust_score}). Action upgraded from ${baseAction} to ${upgradedAction}.`,
            upgraded: true
          };
        }
      }

      // Return base action
      return {
        action: baseAction,
        reasoning: `Severity ${severity} maps to ${baseAction} action.`
      };
    } catch (error) {
      // If database lookup fails, use base action
      // This ensures the system is resilient to database issues
      return {
        action: baseAction,
        reasoning: `Severity ${severity} maps to ${baseAction} action.`
      };
    }
  }

  /**
   * Get user reputation from database
   * @private
   */
  private async getUserReputation(userId: string) {
    if (!this.dbManager) return null; // NO_DB mode
    try {
      return this.dbManager.getUserReputation(userId);
    } catch (error) {
      // Return null if database error - system will use defaults
      return null;
    }
  }

  /**
   * Upgrade action to next level in hierarchy
   * @private
   */
  private upgradeAction(action: Action): Action {
    const currentIndex = this.actionHierarchy.indexOf(action);

    // If already at highest level or not found, return as-is
    if (currentIndex === -1 || currentIndex >= this.actionHierarchy.length - 1) {
      return action;
    }

    // Return next level action
    return this.actionHierarchy[currentIndex + 1];
  }
}
