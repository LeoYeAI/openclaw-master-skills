import { query } from "@anthropic-ai/claude-agent-sdk";

/**
 * Permission Control Template
 *
 * Demonstrates:
 * - Permission modes (default, acceptEdits, bypassPermissions)
 * - Custom canUseTool callback
 * - Safety controls for dangerous operations
 * - Conditional tool approval
 */

// Example 1: Accept Edits Mode (auto-approve file edits)
async function autoApproveEdits() {
  const response = query({
    prompt: "Refactor the user service to use async/await throughout",
    options: {
      model: "claude-sonnet-4-5",
      workingDirectory: "/path/to/project",
      permissionMode: "acceptEdits"  // Auto-approve file edits
    }
  });

  for await (const message of response) {
    if (message.type === 'assistant') {
      console.log(message.content);
    }
  }
}

// Example 2: Bypass Permissions (use with caution!)
async function bypassAllPermissions() {
  const response = query({
    prompt: "Run comprehensive test suite and fix all failures",
    options: {
      model: "claude-sonnet-4-5",
      permissionMode: "bypassPermissions"
      // ⚠️ CAUTION: Skips ALL permission checks
      // Use only in trusted, sandboxed environments
    }
  });

  for await (const message of response) {
    if (message.type === 'assistant') {
      console.log(message.content);
    }
  }
}

// Example 3: Custom Permission Logic
async function customPermissions() {
  const response = query({
    prompt: "Deploy the application to production",
    options: {
      model: "claude-sonnet-4-5",
      permissionMode: "default",
      canUseTool: async (toolName, input) => {
        // Allow read-only operations
        if (['Read', 'Grep', 'Glob'].includes(toolName)) {
          return { behavior: "allow" };
        }

        // Deny destructive bash commands
        if (toolName === 'Bash') {
          const dangerous = [
            'rm -rf',
            'dd if=',
            'mkfs',
            '> /dev/',
            'shutdown',
            'reboot'
          ];

          if (dangerous.some(pattern => input.command.includes(pattern))) {
            return {
              behavior: "deny",
              message: `Destructive command blocked: ${input.command}`
            };
          }
        }

        // Require confirmation for deployments
        if (input.command?.includes('deploy') ||
            input.command?.includes('kubectl apply') ||
            input.command?.includes('terraform apply')) {
          return {
            behavior: "ask",
            message: `Confirm deployment: ${input.command}?`
          };
        }

        // Require confirmation for file writes to sensitive paths
        if (toolName === 'Write' || toolName === 'Edit') {
          const sensitivePaths = [
            '/etc/',
            '/root/',
            '.env',
            'credentials',
            'secrets',
            'config/production'
          ];

          if (sensitivePaths.some(path => input.file_path?.includes(path))) {
            return {
              behavior: "ask",
              message: `Modify sensitive file ${input.file_path}?`
            };
          }
        }

        // Allow by default
        return { behavior: "allow" };
      }
    }
  });

  for await (const message of response) {
    if (message.type === 'assistant') {
      console.log(message.content);
    }
  }
}

// Example 4: Environment-Based Permissions
async function environmentBasedPermissions(environment: 'development' | 'staging' | 'production') {
  const response = query({
    prompt: "Deploy the latest changes",
    options: {
      model: "claude-sonnet-4-5",
      permissionMode: "default",
      canUseTool: async (toolName, input) => {
        // Production requires approval for everything
        if (environment === 'production') {
          if (toolName === 'Bash' || toolName === 'Write' || toolName === 'Edit') {
            return {
              behavior: "ask",
              message: `PRODUCTION: Approve ${toolName}?`
            };
          }
        }

        // Staging auto-approves edits
        if (environment === 'staging') {
          if (toolName === 'Write' || toolName === 'Edit') {
            return { behavior: "allow" };
          }
        }

        // Development bypasses most checks
        if (environment === 'development') {
          return { behavior: "allow" };
        }

        return { behavior: "allow" };
      }
    }
  });

  for await (const message of response) {
    if (message.type === 'assistant') {
      console.log(message.content);
    }
  }
}

// Example 5: Logging & Auditing
async function loggingPermissions() {
  const toolLog: Array<{ tool: string; input: any; decision: string; timestamp: Date }> = [];

  const response = query({
    prompt: "Implement new feature X",
    options: {
      model: "claude-sonnet-4-5",
      permissionMode: "default",
      canUseTool: async (toolName, input) => {
        // Log all tool usage
        console.log(`[${new Date().toISOString()}] Tool requested: ${toolName}`);

        const decision = { behavior: "allow" as const };

        // Audit log
        toolLog.push({
          tool: toolName,
          input,
          decision: decision.behavior,
          timestamp: new Date()
        });

        // Could also send to external logging service
        // await logToDatabase(toolName, input, decision);

        return decision;
      }
    }
  });

  for await (const message of response) {
    if (message.type === 'assistant') {
      console.log(message.content);
    }
  }

  // Print audit log
  console.log('\n\n=== Audit Log ===');
  toolLog.forEach(entry => {
    console.log(`${entry.timestamp.toISOString()} - ${entry.tool} - ${entry.decision}`);
  });
}

// Run
customPermissions().catch(console.error);
