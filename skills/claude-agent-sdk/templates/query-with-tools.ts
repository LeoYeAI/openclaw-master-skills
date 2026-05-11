import { query } from "@anthropic-ai/claude-agent-sdk";

/**
 * Query with Tool Control Template
 *
 * Demonstrates:
 * - Allowing/disallowing tools
 * - System prompts
 * - Tool execution monitoring
 */

async function queryWithTools() {
  const response = query({
    prompt: "Review the authentication module for security issues and fix any vulnerabilities",
    options: {
      model: "claude-sonnet-4-5",
      workingDirectory: "/path/to/project",
      systemPrompt: `You are a security-focused code reviewer.

Analyze code for:
- SQL injection vulnerabilities
- XSS vulnerabilities
- Authentication bypass issues
- Insecure direct object references
- Security misconfiguration

Provide detailed recommendations and fix critical issues.`,

      // Allow reading and modification, but not bash execution
      allowedTools: ["Read", "Grep", "Glob", "Write", "Edit"],
      disallowedTools: ["Bash"]
    }
  });

  // Track tool usage
  const toolsUsed = new Set<string>();

  for await (const message of response) {
    if (message.type === 'assistant') {
      console.log('\nAssistant:', message.content);
    } else if (message.type === 'tool_call') {
      console.log(`\n🔧 Executing: ${message.tool_name}`);
      console.log(`Input:`, JSON.stringify(message.input, null, 2));
      toolsUsed.add(message.tool_name);
    } else if (message.type === 'tool_result') {
      console.log(`✅ ${message.tool_name} completed`);
    }
  }

  console.log(`\n\nTools used: ${Array.from(toolsUsed).join(', ')}`);
}

// Run
queryWithTools().catch(console.error);
