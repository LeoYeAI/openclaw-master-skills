import { query } from "@anthropic-ai/claude-agent-sdk";

/**
 * Error Handling Template
 *
 * Demonstrates:
 * - SDK error handling
 * - Message-level error handling
 * - Retry strategies
 * - Graceful degradation
 */

// Example 1: Basic Error Handling
async function basicErrorHandling() {
  try {
    const response = query({
      prompt: "Analyze and refactor code",
      options: {
        model: "claude-sonnet-4-5",
        workingDirectory: "/path/to/project"
      }
    });

    for await (const message of response) {
      switch (message.type) {
        case 'assistant':
          console.log('Assistant:', message.content);
          break;

        case 'error':
          console.error('Agent error:', message.error.message);
          if (message.error.type === 'permission_denied') {
            console.log('Permission denied for:', message.error.tool);
            // Handle permission errors gracefully
          }
          break;
      }
    }
  } catch (error) {
    console.error('Fatal error:', error);

    // Handle specific error codes
    if (error.code === 'CLI_NOT_FOUND') {
      console.error('Claude Code CLI not installed');
      console.error('Install: npm install -g @anthropic-ai/claude-code');
    } else if (error.code === 'AUTHENTICATION_FAILED') {
      console.error('Invalid API key. Check ANTHROPIC_API_KEY');
    } else if (error.code === 'RATE_LIMIT_EXCEEDED') {
      console.error('Rate limit exceeded. Retry after delay.');
    } else if (error.code === 'CONTEXT_LENGTH_EXCEEDED') {
      console.error('Context too large. Use session compaction.');
    }
  }
}

// Example 2: Retry with Exponential Backoff
async function retryWithBackoff(
  prompt: string,
  maxRetries = 3,
  baseDelay = 1000
): Promise<void> {
  for (let attempt = 0; attempt < maxRetries; attempt++) {
    try {
      const response = query({
        prompt,
        options: {
          model: "claude-sonnet-4-5"
        }
      });

      for await (const message of response) {
        if (message.type === 'assistant') {
          console.log(message.content);
        }
      }

      return; // Success, exit
    } catch (error) {
      if (error.code === 'RATE_LIMIT_EXCEEDED' && attempt < maxRetries - 1) {
        const delay = baseDelay * Math.pow(2, attempt);
        console.log(`Rate limited. Retrying in ${delay}ms...`);
        await new Promise(resolve => setTimeout(resolve, delay));
      } else {
        throw error; // Re-throw if not rate limit or final attempt
      }
    }
  }
}

// Example 3: Graceful Degradation
async function gracefulDegradation(prompt: string) {
  // Try with full capabilities first
  try {
    console.log('Attempting with Sonnet model...');
    const response = query({
      prompt,
      options: {
        model: "claude-sonnet-4-5",
        allowedTools: ["Read", "Write", "Edit", "Bash", "Grep", "Glob"]
      }
    });

    for await (const message of response) {
      if (message.type === 'assistant') {
        console.log(message.content);
      }
    }
  } catch (error) {
    console.warn('Sonnet failed, falling back to Haiku...');

    // Fallback to faster/cheaper model with limited tools
    try {
      const response = query({
        prompt,
        options: {
          model: "haiku",
          allowedTools: ["Read", "Grep", "Glob"]  // Read-only
        }
      });

      for await (const message of response) {
        if (message.type === 'assistant') {
          console.log(message.content);
        }
      }
    } catch (fallbackError) {
      console.error('All attempts failed:', fallbackError);
      throw fallbackError;
    }
  }
}

// Example 4: Comprehensive Error Handler
async function comprehensiveErrorHandling() {
  const errors: Array<{ type: string; message: string; timestamp: Date }> = [];

  try {
    const response = query({
      prompt: "Complex multi-step task",
      options: {
        model: "claude-sonnet-4-5",
        permissionMode: "default"
      }
    });

    for await (const message of response) {
      switch (message.type) {
        case 'assistant':
          console.log('✅ Assistant:', message.content);
          break;

        case 'tool_call':
          console.log(`🔧 Executing: ${message.tool_name}`);
          break;

        case 'tool_result':
          console.log(`✅ ${message.tool_name} completed`);
          break;

        case 'error':
          console.error('❌ Error:', message.error.message);
          errors.push({
            type: message.error.type,
            message: message.error.message,
            timestamp: new Date()
          });

          // Handle different error types
          if (message.error.type === 'permission_denied') {
            console.log('→ Permission was denied, continuing with limited access');
          } else if (message.error.type === 'tool_execution_failed') {
            console.log('→ Tool failed, attempting alternative approach');
          }
          break;
      }
    }
  } catch (error) {
    console.error('💥 Fatal error:', error);

    // Log error details
    errors.push({
      type: error.code || 'UNKNOWN',
      message: error.message,
      timestamp: new Date()
    });

    // Specific handlers
    if (error.code === 'AUTHENTICATION_FAILED') {
      console.error('→ Check your ANTHROPIC_API_KEY environment variable');
      console.error('→ Visit https://console.anthropic.com/ for API keys');
    } else if (error.code === 'RATE_LIMIT_EXCEEDED') {
      console.error('→ Rate limit exceeded');
      console.error('→ Implement exponential backoff or reduce request frequency');
    } else if (error.code === 'CONTEXT_LENGTH_EXCEEDED') {
      console.error('→ Context too large');
      console.error('→ Consider using session management or reducing prompt size');
    } else if (error.code === 'CLI_NOT_FOUND') {
      console.error('→ Claude Code CLI not found');
      console.error('→ Install: npm install -g @anthropic-ai/claude-code');
    }

    throw error;
  } finally {
    // Always log error summary
    if (errors.length > 0) {
      console.log('\n\n=== Error Summary ===');
      errors.forEach(err => {
        console.log(`${err.timestamp.toISOString()} - ${err.type}: ${err.message}`);
      });
    }
  }
}

// Example 5: Circuit Breaker Pattern
class CircuitBreaker {
  private failures = 0;
  private lastFailureTime?: Date;
  private readonly threshold = 3;
  private readonly resetTimeout = 60000; // 1 minute

  async execute(fn: () => Promise<void>): Promise<void> {
    // Check if circuit is open
    if (this.isOpen()) {
      throw new Error('Circuit breaker is OPEN. Too many failures.');
    }

    try {
      await fn();
      this.onSuccess();
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }

  private isOpen(): boolean {
    if (this.failures >= this.threshold) {
      const now = new Date();
      if (this.lastFailureTime &&
          now.getTime() - this.lastFailureTime.getTime() < this.resetTimeout) {
        return true;
      }
      // Reset after timeout
      this.failures = 0;
    }
    return false;
  }

  private onSuccess() {
    this.failures = 0;
    this.lastFailureTime = undefined;
  }

  private onFailure() {
    this.failures++;
    this.lastFailureTime = new Date();
    console.warn(`Circuit breaker: ${this.failures}/${this.threshold} failures`);
  }
}

async function useCircuitBreaker() {
  const breaker = new CircuitBreaker();

  try {
    await breaker.execute(async () => {
      const response = query({
        prompt: "Perform task",
        options: { model: "sonnet" }
      });

      for await (const message of response) {
        if (message.type === 'assistant') {
          console.log(message.content);
        }
      }
    });
  } catch (error) {
    console.error('Circuit breaker prevented execution or task failed:', error);
  }
}

// Run
comprehensiveErrorHandling().catch(console.error);
