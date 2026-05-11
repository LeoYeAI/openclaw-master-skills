import { query } from "@anthropic-ai/claude-agent-sdk";

/**
 * Subagent Orchestration Template
 *
 * Demonstrates:
 * - Defining specialized subagents
 * - Different models for different agents
 * - Tool restrictions per agent
 * - Multi-agent workflows
 */

async function deployWithAgents(version: string) {
  const response = query({
    prompt: `Deploy version ${version} to production with full validation`,
    options: {
      model: "claude-sonnet-4-5",
      workingDirectory: process.cwd(),
      systemPrompt: `You are a DevOps orchestrator.

Coordinate specialized agents to:
1. Run tests (test-runner agent)
2. Check security (security-checker agent)
3. Deploy application (deployer agent)
4. Monitor systems (monitoring-agent agent)

Ensure all validation passes before deployment.`,

      agents: {
        "test-runner": {
          description: "Run automated test suites and verify coverage",
          prompt: `You run tests.

Execute test commands, parse results, report coverage.
FAIL the deployment if any tests fail.
Report clear error messages for failures.`,
          tools: ["Bash", "Read", "Grep"],
          model: "haiku"  // Fast, cost-effective for testing
        },

        "security-checker": {
          description: "Security audits and vulnerability scanning",
          prompt: `You check security.

Scan for:
- Exposed secrets or API keys
- Outdated dependencies
- Incorrect file permissions
- OWASP compliance issues

Verify all security checks pass before deployment.`,
          tools: ["Read", "Grep", "Bash"],
          model: "sonnet"  // Balance for security analysis
        },

        "deployer": {
          description: "Application deployment and rollbacks",
          prompt: `You deploy applications.

Deployment process:
1. Deploy to staging environment
2. Verify health checks pass
3. Deploy to production
4. Create rollback plan

ALWAYS have a rollback ready.`,
          tools: ["Bash", "Read"],
          model: "sonnet"  // Reliable for critical operations
        },

        "monitoring-agent": {
          description: "System monitoring and alerting",
          prompt: `You monitor systems.

Check:
- Application metrics
- Error rates
- Response times
- System health

Alert on issues immediately.`,
          tools: ["Bash", "Read"],
          model: "haiku"  // Fast monitoring checks
        }
      }
    }
  });

  // Track which agents were used
  const agentsUsed = new Set<string>();

  for await (const message of response) {
    if (message.type === 'assistant') {
      console.log('\n📋 Orchestrator:', message.content);
    } else if (message.type === 'tool_call') {
      console.log(`\n🔧 Tool: ${message.tool_name}`);
    }
  }
}

// Example: Complex DevOps workflow
async function complexWorkflow() {
  const response = query({
    prompt: "API response time increased by 300% in last hour. Investigate and fix",
    options: {
      model: "claude-sonnet-4-5",
      systemPrompt: "You coordinate incident response across specialized teams.",

      agents: {
        "incident-responder": {
          description: "Diagnose and respond to production incidents",
          prompt: `You handle incidents.

Steps:
1. Assess impact (users affected, services down)
2. Identify root cause
3. Implement immediate fixes
4. Communicate status updates

Work with monitoring and deployment agents.`,
          tools: ["Bash", "Read", "Grep"],
          model: "sonnet"
        },

        "performance-analyst": {
          description: "Analyze performance metrics and bottlenecks",
          prompt: `You analyze performance.

Investigate:
- Database query times
- API response times
- Memory/CPU usage
- Network latency

Identify bottlenecks and optimization opportunities.`,
          tools: ["Bash", "Read", "Grep"],
          model: "sonnet"
        },

        "fix-implementer": {
          description: "Implement performance fixes and optimizations",
          prompt: `You implement fixes.

Apply optimizations:
- Database query optimization
- Caching improvements
- Code refactoring
- Infrastructure scaling

Test fixes before deploying.`,
          tools: ["Read", "Edit", "Bash"],
          model: "sonnet"
        }
      }
    }
  });

  for await (const message of response) {
    if (message.type === 'assistant') {
      console.log(message.content);
    }
  }
}

// Run
deployWithAgents("2.5.0").catch(console.error);
