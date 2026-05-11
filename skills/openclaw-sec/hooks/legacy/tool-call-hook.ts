#!/usr/bin/env node

/**
 * OpenClaw Security: Tool Call Hook
 *
 * This hook intercepts tool/function calls before execution,
 * validating parameters for security threats including:
 * - Command injection in shell commands
 * - SSRF in URL parameters
 * - Path traversal in file operations
 * - Malicious file content
 *
 * Installation:
 *   Copy this file to your Claude Code hooks directory:
 *   ~/.claude-code/hooks/tool-call-hook.ts
 *
 * Usage:
 *   The hook runs automatically before tool calls are executed.
 */

import { SecurityEngine, ValidationMetadata } from '../src/core/security-engine';
import { ConfigManager } from '../src/core/config-manager';
import { DatabaseManager } from '../src/core/database-manager';
import { Action, Severity } from '../src/types';
import * as path from 'path';
import * as fs from 'fs';

interface ToolParameter {
  name: string;
  value: any;
  type?: string;
}

interface HookInput {
  toolName: string;
  parameters: ToolParameter[];
  userId?: string;
  sessionId?: string;
  context?: Record<string, any>;
}

interface HookOutput {
  allow: boolean;
  message?: string;
  severity?: Severity;
  modifiedParameters?: ToolParameter[];
}

/**
 * Determine which parameters need security validation based on tool
 */
function getValidatableParameters(toolName: string, parameters: ToolParameter[]): ToolParameter[] {
  const validatable: ToolParameter[] = [];

  // Map of tools to parameters that need validation
  const toolParamMap: Record<string, string[]> = {
    'bash': ['command'],
    'exec': ['command', 'script'],
    'read': ['file_path', 'path'],
    'write': ['file_path', 'path', 'content'],
    'edit': ['file_path', 'old_string', 'new_string'],
    'web_fetch': ['url'],
    'web_search': ['query'],
    'fetch': ['url'],
    'curl': ['url'],
    'wget': ['url']
  };

  const paramsToCheck = toolParamMap[toolName.toLowerCase()] || [];

  parameters.forEach(param => {
    // Check if this parameter should be validated
    if (paramsToCheck.includes(param.name.toLowerCase())) {
      validatable.push(param);
    }
    // Also check any parameter with 'command', 'url', 'path' in name
    else if (
      param.name.toLowerCase().includes('command') ||
      param.name.toLowerCase().includes('url') ||
      param.name.toLowerCase().includes('path') ||
      param.name.toLowerCase().includes('file')
    ) {
      validatable.push(param);
    }
  });

  return validatable;
}

/**
 * Main hook function
 */
async function toolCallHook(input: HookInput): Promise<HookOutput> {
  try {
    // Find config file
    const configPaths = [
      path.join(process.cwd(), '.openclaw-sec.yaml'),
      path.join(process.env.HOME || '~', '.openclaw', 'security-config.yaml')
    ];

    let config;
    for (const configPath of configPaths) {
      if (fs.existsSync(configPath)) {
        config = await ConfigManager.load(configPath);
        break;
      }
    }

    // Use default config if none found
    if (!config) {
      config = ConfigManager.getDefaultConfig();
    }

    // Check if security is disabled
    if (!config.enabled) {
      return {
        allow: true,
        message: 'Security validation is disabled'
      };
    }

    // Initialize database
    const dbPath = config.database?.path || '.openclaw-sec.db';
    const dbManager = new DatabaseManager(dbPath);

    // Initialize security engine
    const engine = new SecurityEngine(config, dbManager);

    // Get parameters that need validation
    const validatableParams = getValidatableParameters(input.toolName, input.parameters);

    if (validatableParams.length === 0) {
      // No parameters need validation
      await engine.stop();
      dbManager.close();
      return { allow: true };
    }

    // Validate each parameter
    const allFindings: any[] = [];
    let maxSeverity = Severity.SAFE;
    let finalAction = Action.ALLOW;

    for (const param of validatableParams) {
      // Convert parameter value to string for validation
      const valueStr = typeof param.value === 'string'
        ? param.value
        : JSON.stringify(param.value);

      const metadata: ValidationMetadata = {
        userId: input.userId || 'unknown-user',
        sessionId: input.sessionId || `session-${Date.now()}`,
        context: {
          ...input.context,
          hookType: 'tool-call',
          toolName: input.toolName,
          parameterName: param.name,
          timestamp: new Date().toISOString()
        }
      };

      const result = await engine.validate(valueStr, metadata);

      // Track findings
      if (result.findings.length > 0) {
        allFindings.push(...result.findings.map(f => ({
          parameter: param.name,
          module: f.module,
          category: f.pattern.category,
          description: f.pattern.description,
          severity: f.severity
        })));
      }

      // Update max severity and action
      if (compareSeverity(result.severity, maxSeverity) > 0) {
        maxSeverity = result.severity;
      }

      if (shouldBlock(result.action) && !shouldBlock(finalAction)) {
        finalAction = result.action;
      }
    }

    // Stop engine and cleanup
    await engine.stop();
    dbManager.close();

    // Determine response
    const response: HookOutput = {
      allow: !shouldBlock(finalAction),
      severity: maxSeverity
    };

    // Add message if there are findings
    if (allFindings.length > 0) {
      if (shouldBlock(finalAction)) {
        response.message = `🚫 Tool Call Blocked: Security threats detected in ${input.toolName}\n\n` +
          `Severity: ${maxSeverity}\n` +
          `Findings:\n` +
          allFindings.map((f, i) =>
            `${i + 1}. [${f.parameter}] ${f.category}: ${f.description}`
          ).join('\n');
      } else {
        response.message = `⚠️  Security Notice: Potential issues detected in ${input.toolName}\n` +
          `The call will be allowed but logged for review.`;
      }
    }

    return response;
  } catch (error) {
    // On error, allow the request but log the error
    console.error('OpenClaw Security Tool Hook Error:', error);
    return {
      allow: true,
      message: 'Security validation encountered an error and was bypassed'
    };
  }
}

/**
 * Helper: Compare severity levels
 */
function compareSeverity(s1: Severity, s2: Severity): number {
  const order = {
    [Severity.SAFE]: 0,
    [Severity.LOW]: 1,
    [Severity.MEDIUM]: 2,
    [Severity.HIGH]: 3,
    [Severity.CRITICAL]: 4
  };

  return order[s1] - order[s2];
}

/**
 * Helper: Check if action should block
 */
function shouldBlock(action: Action): boolean {
  return action === Action.BLOCK || action === Action.BLOCK_NOTIFY;
}

/**
 * Hook entry point
 */
async function main() {
  try {
    // Read input from stdin
    let inputData = '';
    process.stdin.setEncoding('utf8');

    for await (const chunk of process.stdin) {
      inputData += chunk;
    }

    // Parse input
    const input: HookInput = JSON.parse(inputData);

    // Run validation
    const output = await toolCallHook(input);

    // Write output to stdout
    console.log(JSON.stringify(output, null, 2));

    // Exit with appropriate code
    process.exit(output.allow ? 0 : 1);
  } catch (error) {
    console.error('Hook execution error:', error);
    // On error, allow by default
    console.log(JSON.stringify({ allow: true, message: 'Hook error' }, null, 2));
    process.exit(0);
  }
}

// Run if called directly
if (require.main === module) {
  main();
}

// Export only runtime values, not types
export { toolCallHook };
export type { HookInput, HookOutput };
