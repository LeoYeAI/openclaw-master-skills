#!/usr/bin/env node

/**
 * OpenClaw Security: User Prompt Submit Hook
 *
 * This hook intercepts user input before it's submitted to the AI agent,
 * validating it for security threats including:
 * - Prompt injection attempts
 * - Command injection patterns
 * - URL/SSRF attacks
 * - Path traversal attempts
 * - Secret exposure
 * - Obfuscation and policy violations
 *
 * Installation:
 *   Copy this file to your Claude Code hooks directory:
 *   ~/.claude-code/hooks/user-prompt-submit-hook.ts
 *
 * Usage:
 *   The hook runs automatically when users submit prompts.
 *   If security issues are detected, it will:
 *   - ALLOW: Let the request through (safe input)
 *   - WARN: Show a warning but allow (low/medium severity)
 *   - BLOCK: Reject the request (high/critical severity)
 */

import { SecurityEngine, ValidationMetadata } from '../src/core/security-engine';
import { ConfigManager } from '../src/core/config-manager';
import { DatabaseManager } from '../src/core/database-manager';
import { Action, Severity } from '../src/types';
import * as path from 'path';
import * as fs from 'fs';

interface HookInput {
  userPrompt: string;
  userId?: string;
  sessionId?: string;
  context?: Record<string, any>;
}

interface HookOutput {
  allow: boolean;
  message?: string;
  severity?: Severity;
  findings?: Array<{
    module: string;
    category: string;
    description: string;
  }>;
}

/**
 * Main hook function
 */
async function userPromptSubmitHook(input: HookInput): Promise<HookOutput> {
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

    // Prepare validation metadata
    const metadata: ValidationMetadata = {
      userId: input.userId || 'unknown-user',
      sessionId: input.sessionId || `session-${Date.now()}`,
      context: {
        ...input.context,
        hookType: 'user-prompt-submit',
        timestamp: new Date().toISOString()
      }
    };

    // Validate the input
    const result = await engine.validate(input.userPrompt, metadata);

    // Stop engine and cleanup
    await engine.stop();
    dbManager.close();

    // Determine response based on action
    const response: HookOutput = {
      allow: result.action === Action.ALLOW || result.action === Action.LOG || result.action === Action.WARN,
      severity: result.severity,
      findings: result.findings.map(f => ({
        module: f.module,
        category: f.pattern.category,
        description: f.pattern.description
      }))
    };

    // Add appropriate message
    if (result.action === Action.BLOCK || result.action === Action.BLOCK_NOTIFY) {
      response.message = `🚫 Security Warning: This input has been blocked due to ${result.severity} severity threats.\n\n` +
        `Findings: ${result.findings.length}\n` +
        result.findings.map((f, i) => `${i + 1}. ${f.pattern.category}: ${f.pattern.description}`).join('\n') +
        `\n\nPlease modify your input and try again.`;
    } else if (result.action === Action.WARN) {
      response.message = `⚠️  Security Notice: Potential security issues detected (${result.severity} severity).\n\n` +
        `The request will be allowed but logged for review.\n` +
        `Findings: ${result.findings.map(f => f.pattern.category).join(', ')}`;
    }

    return response;
  } catch (error) {
    // On error, allow the request but log the error
    console.error('OpenClaw Security Hook Error:', error);
    return {
      allow: true,
      message: 'Security validation encountered an error and was bypassed'
    };
  }
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
    const output = await userPromptSubmitHook(input);

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
export { userPromptSubmitHook };
export type { HookInput, HookOutput };
