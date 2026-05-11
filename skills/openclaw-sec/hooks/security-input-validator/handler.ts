import type { HookHandler } from "../../src/hooks/hooks.js";
import { SecurityEngine, ValidationMetadata } from "../../src/core/security-engine.js";
import { ConfigManager } from "../../src/core/config-manager.js";
import { DatabaseManager } from "../../src/core/database-manager.js";
import { Action } from "../../src/types/index.js";
import * as path from "path";
import * as fs from "fs";

/**
 * Security Input Validator Hook
 *
 * Validates user prompts before submission to AI agents.
 * Runs on the "command:new" event.
 */
const handler: HookHandler = async (event) => {
  // Only process command:new events
  if (event.type !== "command" || event.action !== "new") {
    return;
  }

  try {
    // Extract user input from event
    const userInput = event.data?.input || event.data?.prompt || "";
    if (!userInput) {
      return; // No input to validate
    }

    // Find config file
    const configPaths = [
      path.join(process.cwd(), ".openclaw-sec.yaml"),
      path.join(process.env.HOME || "~", ".openclaw", "security-config.yaml"),
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
      return; // Security disabled, allow through
    }

    // Initialize database
    const dbPath = config.database?.path || path.join(
      process.env.HOME || "~",
      ".openclaw",
      "security.db"
    );
    const dbManager = new DatabaseManager(dbPath);

    // Initialize security engine
    const engine = new SecurityEngine(config, dbManager);

    // Prepare validation metadata
    const metadata: ValidationMetadata = {
      userId: event.data?.userId || event.user?.id || "unknown-user",
      sessionId: event.data?.sessionId || event.session?.id || `session-${Date.now()}`,
      context: {
        hookType: "security-input-validator",
        eventType: event.type,
        eventAction: event.action,
        timestamp: new Date().toISOString(),
      },
    };

    // Validate the input
    const result = await engine.validate(userInput, metadata);

    // Stop engine and cleanup
    await engine.stop();
    dbManager.close();

    // Determine response based on action
    const shouldBlock = result.action === Action.BLOCK || result.action === Action.BLOCK_NOTIFY;

    if (shouldBlock) {
      // Block the request
      throw new Error(
        `🚫 Security Warning: This input has been blocked due to ${result.severity} severity threats.\n\n` +
        `Findings: ${result.findings.length}\n` +
        result.findings.map((f, i) =>
          `${i + 1}. ${f.pattern.category}: ${f.pattern.description}`
        ).join("\n") +
        `\n\nPlease modify your input and try again.`
      );
    } else if (result.action === Action.WARN) {
      // Show warning but allow
      console.warn(
        `⚠️  Security Notice: Potential security issues detected (${result.severity} severity).\n` +
        `The request will be allowed but logged for review.\n` +
        `Findings: ${result.findings.map(f => f.pattern.category).join(", ")}`
      );
    }

    // Allow the request to proceed
  } catch (error) {
    // On error, log but allow the request (fail-open)
    if (error instanceof Error && error.message.includes("🚫 Security Warning")) {
      // This is our blocking error, re-throw it
      throw error;
    }

    // Other errors - log and allow
    console.error("OpenClaw Security Hook Error:", error);
    // Don't block on error
  }
};

export default handler;
