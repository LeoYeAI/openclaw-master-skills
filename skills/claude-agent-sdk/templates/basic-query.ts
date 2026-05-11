import { query } from "@anthropic-ai/claude-agent-sdk";

/**
 * Basic Query Template
 *
 * Demonstrates:
 * - Simple query execution
 * - Model selection
 * - Working directory
 * - Basic message handling
 */

async function basicQuery() {
  const response = query({
    prompt: "Analyze the codebase and suggest improvements",
    options: {
      model: "claude-sonnet-4-5",  // or "haiku", "opus"
      workingDirectory: process.cwd(),
      allowedTools: ["Read", "Grep", "Glob"]
    }
  });

  // Process streaming messages
  for await (const message of response) {
    switch (message.type) {
      case 'system':
        if (message.subtype === 'init') {
          console.log(`Session ID: ${message.session_id}`);
          console.log(`Model: ${message.model}`);
        }
        break;

      case 'assistant':
        if (typeof message.content === 'string') {
          console.log('Assistant:', message.content);
        }
        break;

      case 'tool_call':
        console.log(`Executing tool: ${message.tool_name}`);
        break;

      case 'tool_result':
        console.log(`Tool ${message.tool_name} completed`);
        break;

      case 'error':
        console.error('Error:', message.error.message);
        break;
    }
  }
}

// Run
basicQuery().catch(console.error);
