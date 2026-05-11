/**
 * Guardian Angel Evaluation Logic
 * 
 * Virtue-based evaluation of tool calls using Clarity × Stakes scoring.
 */

import type { GuardianAngelConfig, EvaluationResult, PluginLogger } from "./types.js";
import { INFRASTRUCTURE_TOOLS, EXTERNAL_EFFECT_TOOLS, DEFAULT_ESCALATION_THRESHOLD } from "./constants.js";

interface ToolContext {
  agentId?: string;
  sessionKey?: string;
  toolName: string;
}

// Patterns that indicate image generation commands
const IMAGE_GEN_PATTERNS = [
  "generate_image.py",
  "nano-banana",
  "openai-image",
  "dall-e",
  "midjourney",
  "stable-diffusion",
  "image-gen",
];

// Patterns indicating harmful image content (intrinsic evil)
const HARMFUL_IMAGE_PATTERNS = [
  // Sexual content
  { pattern: /\b(nude|naked|porn|pornograph|nsfw|xxx|erotic|sexual(?:ly)?|genitals?)\b/i, category: "pornography" },
  { pattern: /\b(child|minor|underage|kid|teen).{0,20}(nude|naked|sexual|erotic)/i, category: "child exploitation" },
  // Violence
  { pattern: /\b(gore|gory|dismember|mutilat|torture|brutal.{0,10}kill)\b/i, category: "extreme violence" },
  { pattern: /\b(terrorist|terrorism|bomb.{0,10}(make|build|instruct))\b/i, category: "terrorism" },
  // Deception
  { pattern: /\b(deepfake|fake.{0,10}(id|passport|document|evidence))\b/i, category: "fraud/deception" },
];

// Patterns that are concerning but may have legitimate uses (escalate, don't block)
const CONCERNING_IMAGE_PATTERNS = [
  { pattern: /\b(weapon|gun|rifle|pistol|knife|sword)\b/i, reason: "weapons depicted" },
  { pattern: /\b(blood|bloody|bleeding|wound)\b/i, reason: "potentially graphic content" },
  { pattern: /\b(drug|cocaine|heroin|meth)\b/i, reason: "drug-related content" },
];

/**
 * Evaluate a tool call through the virtue-based framework.
 */
export function evaluate(
  toolName: string,
  params: Record<string, unknown>,
  ctx: ToolContext,
  config: GuardianAngelConfig,
  logger: PluginLogger
): EvaluationResult {
  
  // === GATE I: Intrinsic Evil Check ===
  const intrinsicCheck = checkIntrinsicEvil(toolName, params);
  if (intrinsicCheck) {
    return { decision: "block", reason: intrinsicCheck };
  }

  // === GATE V: Virtue Evaluation ===
  const clarity = assessClarity(toolName, params);
  const stakes = assessStakes(toolName, params);
  const score = clarity * stakes;

  const threshold = config.escalationThreshold ?? DEFAULT_ESCALATION_THRESHOLD;

  logger.debug?.(`[GA] ${toolName}: clarity=${clarity} stakes=${stakes} score=${score} threshold=${threshold}`);

  // Check against threshold
  if (score >= threshold) {
    const reason = buildEscalationReason(toolName, params, clarity, stakes, score);
    return { decision: "escalate", reason, clarity, stakes };
  }

  // Below threshold — virtues aligned
  return { decision: "allow", clarity, stakes };
}

/**
 * Detect if a command is an image generation command.
 */
function isImageGenerationCommand(cmd: string): boolean {
  const lowerCmd = cmd.toLowerCase();
  return IMAGE_GEN_PATTERNS.some(pattern => lowerCmd.includes(pattern));
}

/**
 * Extract the prompt from an image generation command.
 */
function extractImagePrompt(cmd: string): string | null {
  // Match --prompt "..." or --prompt '...' or -p "..."
  const promptMatch = cmd.match(/(?:--prompt|-p)\s+["']([^"']+)["']/i);
  if (promptMatch) return promptMatch[1];
  
  // Match --prompt ... (unquoted, until next flag or end)
  const unquotedMatch = cmd.match(/(?:--prompt|-p)\s+([^-][^\s]*(?:\s+[^-][^\s]*)*)/i);
  if (unquotedMatch) return unquotedMatch[1].trim();
  
  return null;
}

/**
 * Check image prompt for harmful content.
 */
function checkImagePromptContent(prompt: string): { block: boolean; reason: string } | null {
  const lowerPrompt = prompt.toLowerCase();
  
  // Check for intrinsically harmful content (block)
  for (const { pattern, category } of HARMFUL_IMAGE_PATTERNS) {
    if (pattern.test(prompt)) {
      return { block: true, reason: `Image request contains ${category} (violation of dignity)` };
    }
  }
  
  // Check for concerning content (escalate, don't block)
  for (const { pattern, reason } of CONCERNING_IMAGE_PATTERNS) {
    if (pattern.test(prompt)) {
      return { block: false, reason: `Image request may contain ${reason}` };
    }
  }
  
  return null;
}

/**
 * Check for intrinsically evil actions that cannot be approved.
 */
function checkIntrinsicEvil(
  toolName: string,
  params: Record<string, unknown>
): string | null {
  
  if (toolName === "exec") {
    const cmd = String(params.command || "");
    const lowerCmd = cmd.toLowerCase();
    
    // Catastrophically destructive commands
    if (lowerCmd.includes("rm -rf /") && !lowerCmd.includes("rm -rf /tmp")) {
      return "Command would destroy root filesystem";
    }
    if (lowerCmd.includes(":(){ :|:& };:")) {
      return "Fork bomb detected";
    }
    if (lowerCmd.includes("mkfs") && !lowerCmd.includes("--dry-run")) {
      return "Filesystem format command detected";
    }
    if (lowerCmd.includes("> /dev/sd") || lowerCmd.includes("dd if=") && lowerCmd.includes("of=/dev/")) {
      return "Raw disk write detected";
    }
    
    // Check image generation prompts for harmful content
    if (isImageGenerationCommand(cmd)) {
      const prompt = extractImagePrompt(cmd);
      if (prompt) {
        const contentCheck = checkImagePromptContent(prompt);
        if (contentCheck?.block) {
          return contentCheck.reason;
        }
      }
    }
  }

  // Note: Most "intrinsic evil" checks require understanding intent,
  // which is beyond simple pattern matching. The virtue framework
  // in SKILL.md handles nuanced cases through agent disposition.
  
  return null;
}

/**
 * Assess moral clarity of the action (1 = obvious, 10 = ambiguous).
 */
function assessClarity(toolName: string, params: Record<string, unknown>): number {
  let clarity = 1;

  // Infrastructure tools are inherently less clear (but not image gen)
  if (INFRASTRUCTURE_TOOLS.includes(toolName)) {
    if (toolName === "exec") {
      const cmd = String(params.command || "");
      // Image generation is morally clear (unless content is problematic)
      if (isImageGenerationCommand(cmd)) {
        // Check if the prompt has concerning content
        const prompt = extractImagePrompt(cmd);
        if (prompt) {
          const contentCheck = checkImagePromptContent(prompt);
          if (contentCheck && !contentCheck.block) {
            clarity += 3; // Concerning content elevates ambiguity
          }
          // Otherwise, image gen is low clarity (clear = good)
        }
        // Don't add the infrastructure penalty for image gen
      } else {
        clarity += 3;
      }
    } else {
      clarity += 3;
    }
  }

  // External effects add uncertainty
  if (EXTERNAL_EFFECT_TOOLS.includes(toolName)) {
    clarity += 2;
  }

  // Specific parameter analysis
  if (toolName === "gateway") {
    const action = String(params.action || "");
    if (action === "config.apply" || action === "config.patch") {
      clarity += 3; // Config changes are high-ambiguity
      
      // Check for model changes (especially risky)
      const raw = String(params.raw || "");
      if (raw.includes("model") || raw.includes("defaultModel")) {
        clarity += 2;
      }
    }
    if (action === "update.run") {
      clarity += 2;
    }
    if (action === "restart") {
      clarity += 1;
    }
  }

  if (toolName === "exec") {
    const cmd = String(params.command || "");
    
    // Skip additional penalties for image generation
    if (!isImageGenerationCommand(cmd)) {
      if (cmd.includes("sudo")) {
        clarity += 2;
      }
      if (cmd.includes("rm ") || cmd.includes("rm\t")) {
        clarity += 2;
      }
      if (cmd.includes("|") || cmd.includes(";")) {
        clarity += 1; // Compound commands
      }
    }
  }

  if (toolName === "message") {
    // Sending messages to others requires care
    clarity += 1;
    
    // Broadcast to multiple targets
    if (params.targets && Array.isArray(params.targets) && params.targets.length > 1) {
      clarity += 2;
    }
  }

  if (toolName === "cron") {
    const action = String(params.action || "");
    if (action === "add" || action === "update") {
      clarity += 2; // Scheduled tasks are consequential
    }
  }

  return Math.min(clarity, 10);
}

/**
 * Assess stakes of the action (1 = trivial, 10 = life-altering/irreversible).
 */
function assessStakes(toolName: string, params: Record<string, unknown>): number {
  let stakes = 1;

  // Infrastructure = high stakes (can disable the agent) — but not image gen
  if (INFRASTRUCTURE_TOOLS.includes(toolName)) {
    if (toolName === "exec") {
      const cmd = String(params.command || "");
      // Image generation is low stakes (just creates a file)
      if (isImageGenerationCommand(cmd)) {
        // Check if the prompt has concerning content
        const prompt = extractImagePrompt(cmd);
        if (prompt) {
          const contentCheck = checkImagePromptContent(prompt);
          if (contentCheck && !contentCheck.block) {
            stakes += 2; // Concerning content elevates stakes
          }
          // Otherwise, image gen stays at base stakes
        }
        // Don't add the infrastructure penalty for image gen
      } else {
        stakes += 3;
      }
    } else {
      stakes += 3;
    }
  }

  // Specific high-stakes patterns
  if (toolName === "gateway") {
    const action = String(params.action || "");
    
    if (action === "config.apply" || action === "config.patch") {
      stakes += 2;
      
      // Model changes can cause lockout
      const raw = String(params.raw || "");
      if (raw.includes("model") || raw.includes("defaultModel")) {
        stakes += 3;
      }
      
      // Plugin changes
      if (raw.includes("plugin")) {
        stakes += 2;
      }
    }
    
    if (action === "update.run") {
      stakes += 3; // Updates can break things
    }
    
    if (action === "restart") {
      stakes += 1; // Temporary unavailability
    }
  }

  if (toolName === "exec") {
    const cmd = String(params.command || "");
    
    // Skip additional penalties for image generation
    if (!isImageGenerationCommand(cmd)) {
      if (cmd.includes("rm ") && !cmd.includes("-i")) {
        stakes += 3; // Deletions are high stakes
      }
      if (cmd.includes("kill") || cmd.includes("pkill")) {
        stakes += 2;
      }
      if (cmd.includes("shutdown") || cmd.includes("reboot")) {
        stakes += 5;
      }
      if (cmd.includes("sudo")) {
        stakes += 2;
      }
      if (cmd.includes("openclaw") && (cmd.includes("stop") || cmd.includes("kill"))) {
        stakes += 4; // Self-disabling
      }
    }
  }

  if (toolName === "Write" || toolName === "Edit") {
    const path = String(params.path || params.file_path || "");
    
    // Config files
    if (path.includes("openclaw") && path.includes("config")) {
      stakes += 3;
    }
    if (path.includes(".env") || path.includes("secret") || path.includes("credential")) {
      stakes += 2;
    }
  }

  if (toolName === "message") {
    stakes += 2; // Relationship stakes
  }

  if (toolName === "cron") {
    const action = String(params.action || "");
    if (action === "add" || action === "update") {
      stakes += 2; // Ongoing consequences
    }
  }

  return Math.min(stakes, 10);
}

/**
 * Build a human-readable escalation reason.
 */
function buildEscalationReason(
  toolName: string,
  params: Record<string, unknown>,
  clarity: number,
  stakes: number,
  score: number
): string {
  const parts: string[] = [];

  parts.push(`Action: ${toolName}`);
  parts.push(`Risk score: ${score} (clarity=${clarity}, stakes=${stakes})`);

  // Add specific concerns
  if (toolName === "gateway") {
    const action = String(params.action || "");
    if (action.includes("config")) {
      parts.push("This modifies OpenClaw configuration");
    }
    if (action === "update.run") {
      parts.push("This updates OpenClaw software");
    }
    if (action === "restart") {
      parts.push("This will restart OpenClaw");
    }
  }
  
  if (toolName === "exec") {
    const cmd = String(params.command || "");
    
    // For image generation, show the prompt concern if any
    if (isImageGenerationCommand(cmd)) {
      const prompt = extractImagePrompt(cmd);
      if (prompt) {
        const contentCheck = checkImagePromptContent(prompt);
        if (contentCheck && !contentCheck.block) {
          parts.push(contentCheck.reason);
        }
      }
      parts.push("Image generation");
    } else {
      parts.push(`Command: ${cmd.slice(0, 80)}${cmd.length > 80 ? "..." : ""}`);
    }
  }

  if (toolName === "message") {
    const to = params.to || params.target || params.targets;
    if (to) {
      parts.push(`Recipient: ${String(to).slice(0, 50)}`);
    }
  }

  return parts.join(" | ");
}
