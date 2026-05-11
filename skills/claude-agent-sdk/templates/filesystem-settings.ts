import { query } from "@anthropic-ai/claude-agent-sdk";

/**
 * Filesystem Settings Template
 *
 * Demonstrates:
 * - Loading settings from user, project, local
 * - Settings priority and merging
 * - Isolated vs configured execution
 * - Loading CLAUDE.md project instructions
 */

// Example 1: Load All Settings (Legacy Behavior)
async function loadAllSettings() {
  const response = query({
    prompt: "Build a new feature following project conventions",
    options: {
      model: "claude-sonnet-4-5",
      settingSources: ["user", "project", "local"]
      // Loads:
      // 1. ~/.claude/settings.json (user)
      // 2. .claude/settings.json (project)
      // 3. .claude/settings.local.json (local overrides)
      //
      // Priority (highest first):
      // 1. Programmatic options (this config)
      // 2. Local settings
      // 3. Project settings
      // 4. User settings
    }
  });

  for await (const message of response) {
    if (message.type === 'assistant') {
      console.log(message.content);
    }
  }
}

// Example 2: Project Settings Only (CI/CD Pattern)
async function projectSettingsOnly() {
  const response = query({
    prompt: "Run automated code review",
    options: {
      model: "claude-sonnet-4-5",
      settingSources: ["project"]
      // Only .claude/settings.json
      // Ignores user and local settings
      // Ensures consistent behavior in CI/CD
    }
  });

  for await (const message of response) {
    if (message.type === 'assistant') {
      console.log(message.content);
    }
  }
}

// Example 3: No Filesystem Settings (Fully Isolated)
async function isolatedExecution() {
  const response = query({
    prompt: "Analyze this code snippet",
    options: {
      model: "claude-sonnet-4-5",
      settingSources: [],  // Empty = no filesystem settings
      workingDirectory: "/tmp/sandbox",
      allowedTools: ["Read", "Grep", "Glob"],
      systemPrompt: "You are a code analyzer."
      // Fully isolated, no filesystem dependencies
      // Perfect for sandboxed/containerized environments
    }
  });

  for await (const message of response) {
    if (message.type === 'assistant') {
      console.log(message.content);
    }
  }
}

// Example 4: Hybrid Approach (Project + Programmatic)
async function hybridConfiguration() {
  const response = query({
    prompt: "Implement user authentication system",
    options: {
      model: "claude-sonnet-4-5",
      settingSources: ["project"],  // Load CLAUDE.md and project settings
      systemPrompt: "Follow security best practices and company coding standards.",
      agents: {
        "security-checker": {
          description: "Security validation specialist",
          prompt: "Validate all security implementations against OWASP guidelines.",
          tools: ["Read", "Grep"],
          model: "sonnet"
        }
      },
      allowedTools: ["Read", "Write", "Edit", "Grep", "Glob"]
      // Project settings + programmatic overrides
      // Programmatic settings always win
    }
  });

  for await (const message of response) {
    if (message.type === 'assistant') {
      console.log(message.content);
    }
  }
}

// Example 5: Loading CLAUDE.md Project Instructions
async function loadProjectInstructions() {
  const response = query({
    prompt: "Implement new feature according to project guidelines",
    options: {
      model: "claude-sonnet-4-5",
      systemPrompt: {
        type: 'preset',
        preset: 'claude_code'  // Required to use CLAUDE.md
      },
      settingSources: ["project"],  // Reads CLAUDE.md from project directory
      workingDirectory: process.cwd()
    }
  });

  for await (const message of response) {
    if (message.type === 'assistant') {
      console.log(message.content);
    }
  }
}

// Example 6: Environment-Specific Settings
async function environmentSpecificSettings(
  environment: 'development' | 'staging' | 'production'
) {
  let settingSources: Array<'user' | 'project' | 'local'>;
  let permissionMode: 'default' | 'acceptEdits' | 'bypassPermissions';

  switch (environment) {
    case 'development':
      settingSources = ["user", "project", "local"];
      permissionMode = "acceptEdits";
      break;

    case 'staging':
      settingSources = ["project"];
      permissionMode = "default";
      break;

    case 'production':
      settingSources = ["project"];
      permissionMode = "default";
      break;
  }

  const response = query({
    prompt: "Deploy application",
    options: {
      model: "claude-sonnet-4-5",
      settingSources,
      permissionMode,
      workingDirectory: process.cwd()
    }
  });

  for await (const message of response) {
    if (message.type === 'assistant') {
      console.log(message.content);
    }
  }
}

// Settings File Examples:

/**
 * ~/.claude/settings.json (User Settings)
 * {
 *   "model": "claude-sonnet-4-5",
 *   "allowedTools": ["Read", "Write", "Edit", "Bash", "Grep", "Glob"],
 *   "permissionMode": "default"
 * }
 */

/**
 * .claude/settings.json (Project Settings - version controlled)
 * {
 *   "model": "claude-sonnet-4-5",
 *   "allowedTools": ["Read", "Write", "Edit", "Grep", "Glob"],
 *   "disallowedTools": ["Bash"],
 *   "agents": {
 *     "code-reviewer": {
 *       "description": "Review code for quality",
 *       "prompt": "You review code for best practices.",
 *       "tools": ["Read", "Grep"],
 *       "model": "haiku"
 *     }
 *   }
 * }
 */

/**
 * .claude/settings.local.json (Local Overrides - gitignored)
 * {
 *   "permissionMode": "acceptEdits",
 *   "allowedTools": ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
 * }
 */

// Run
hybridConfiguration().catch(console.error);
