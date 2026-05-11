import { query, createSdkMcpServer, tool } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";

/**
 * Complete Multi-Agent Workflow Template
 *
 * Demonstrates:
 * - Complex multi-agent orchestration
 * - Custom tools for agents
 * - Environment-based configuration
 * - Production-ready error handling
 * - Comprehensive monitoring
 */

// Custom tools for notification and logging
const appTools = createSdkMcpServer({
  name: "app-services",
  version: "1.0.0",
  tools: [
    tool(
      "send_notification",
      "Send notification to users or teams",
      {
        userId: z.string().optional(),
        teamId: z.string().optional(),
        message: z.string(),
        priority: z.enum(["low", "medium", "high", "critical"]).default("medium")
      },
      async (args) => {
        // Simulate notification service
        console.log(`📧 Notification (${args.priority}): ${args.message}`);
        return {
          content: [{ type: "text", text: "Notification sent successfully" }]
        };
      }
    ),
    tool(
      "log_event",
      "Log application events for monitoring",
      {
        event: z.string(),
        data: z.record(z.any()).optional(),
        severity: z.enum(["debug", "info", "warning", "error", "critical"]).default("info")
      },
      async (args) => {
        console.log(`📝 [${args.severity.toUpperCase()}] ${args.event}:`, args.data || '');
        return {
          content: [{ type: "text", text: "Event logged" }]
        };
      }
    ),
    tool(
      "check_health",
      "Check system health metrics",
      {
        service: z.string(),
        metrics: z.array(z.enum(["cpu", "memory", "disk", "network"])).optional()
      },
      async (args) => {
        // Simulate health check
        const health = {
          service: args.service,
          status: "healthy",
          uptime: "99.9%",
          responseTime: "50ms"
        };
        return {
          content: [{ type: "text", text: JSON.stringify(health, null, 2) }]
        };
      }
    )
  ]
});

// Main DevOps agent orchestrator
async function runDevOpsAgent(task: string) {
  console.log(`🚀 Starting DevOps Agent for: ${task}\n`);

  const response = query({
    prompt: task,
    options: {
      model: "claude-sonnet-4-5",
      workingDirectory: process.cwd(),
      systemPrompt: `You are a DevOps automation expert and orchestrator.

Your responsibilities:
- Monitor system health
- Deploy applications safely
- Handle incidents and alerts
- Maintain infrastructure
- Coordinate specialized agents

Always log your actions and notify relevant stakeholders.
Follow the principle of least privilege for tool access.`,

      // Custom tools
      mcpServers: {
        "app-services": appTools
      },

      // Specialized agents for different tasks
      agents: {
        "deployment-agent": {
          description: "Handles application deployments, rollbacks, and release management",
          prompt: `You manage deployments.

Deployment checklist:
1. Verify all tests pass
2. Deploy to staging first
3. Run smoke tests
4. Deploy to production
5. Create rollback plan
6. Monitor for issues

Always notify stakeholders of deployment status.`,
          tools: [
            "Bash",
            "Read",
            "mcp__app-services__log_event",
            "mcp__app-services__send_notification",
            "mcp__app-services__check_health"
          ],
          model: "sonnet"
        },

        "incident-responder": {
          description: "Responds to production incidents, outages, and performance issues",
          prompt: `You handle incidents.

Incident response process:
1. Assess impact (users affected, services down)
2. Identify root cause
3. Implement immediate fixes
4. Communicate status updates
5. Document incident for post-mortem

Work quickly but carefully. User experience is critical.`,
          tools: [
            "Bash",
            "Read",
            "Grep",
            "mcp__app-services__log_event",
            "mcp__app-services__send_notification",
            "mcp__app-services__check_health"
          ],
          model: "sonnet"
        },

        "monitoring-agent": {
          description: "Monitors system metrics, health checks, and alerts on issues",
          prompt: `You monitor systems.

Monitoring tasks:
- Check application metrics
- Analyze error rates
- Monitor response times
- Verify system health
- Alert on anomalies

Report issues immediately.`,
          tools: [
            "Bash",
            "Read",
            "mcp__app-services__log_event",
            "mcp__app-services__send_notification",
            "mcp__app-services__check_health"
          ],
          model: "haiku"  // Fast, cost-effective for monitoring
        },

        "security-agent": {
          description: "Performs security audits, vulnerability scanning, and compliance checks",
          prompt: `You ensure security.

Security checks:
- Scan for exposed secrets
- Check dependency vulnerabilities
- Verify access controls
- Validate compliance (OWASP, SOC2)
- Audit infrastructure config

Block deployments if critical issues found.`,
          tools: [
            "Bash",
            "Read",
            "Grep",
            "mcp__app-services__log_event",
            "mcp__app-services__send_notification"
          ],
          model: "sonnet"
        },

        "performance-agent": {
          description: "Analyzes performance metrics, identifies bottlenecks, and suggests optimizations",
          prompt: `You optimize performance.

Performance analysis:
- Database query times
- API response times
- Memory/CPU usage
- Network latency
- Caching effectiveness

Identify bottlenecks and optimization opportunities.`,
          tools: [
            "Bash",
            "Read",
            "Grep",
            "mcp__app-services__log_event",
            "mcp__app-services__check_health"
          ],
          model: "sonnet"
        }
      },

      // Permission control
      permissionMode: "default",
      canUseTool: async (toolName, input) => {
        // Log all tool usage
        console.log(`🔧 [${new Date().toISOString()}] ${toolName}`);

        // Prevent destructive operations
        if (toolName === 'Bash') {
          const dangerous = ['rm -rf', 'dd if=', 'mkfs', '> /dev/', 'shutdown'];
          if (dangerous.some(pattern => input.command.includes(pattern))) {
            return {
              behavior: "deny",
              message: `Destructive command blocked: ${input.command}`
            };
          }
        }

        // Require confirmation for production deployments
        if (input.command?.includes('deploy --production') ||
            input.command?.includes('kubectl apply -n production')) {
          return {
            behavior: "ask",
            message: `⚠️  PRODUCTION DEPLOYMENT: ${input.command}\n\nConfirm?`
          };
        }

        return { behavior: "allow" };
      }
    }
  });

  // Track execution
  const agentsUsed = new Set<string>();
  const toolsExecuted: string[] = [];
  let sessionId: string | undefined;

  try {
    for await (const message of response) {
      switch (message.type) {
        case 'system':
          if (message.subtype === 'init') {
            sessionId = message.session_id;
            console.log(`✨ Session: ${sessionId}\n`);
          }
          break;

        case 'assistant':
          console.log('📋 Orchestrator:', message.content);
          break;

        case 'tool_call':
          console.log(`\n🔧 Executing: ${message.tool_name}`);
          toolsExecuted.push(message.tool_name);
          break;

        case 'tool_result':
          console.log(`✅ ${message.tool_name} completed`);
          break;

        case 'error':
          console.error('❌ Error:', message.error.message);
          break;
      }
    }

    console.log(`\n\n✅ Task completed successfully`);
    console.log(`Session ID: ${sessionId}`);
    console.log(`Tools executed: ${toolsExecuted.length}`);
  } catch (error) {
    console.error('💥 Fatal error:', error);
    throw error;
  }
}

// Usage examples
async function main() {
  try {
    // Example 1: Deployment
    await runDevOpsAgent(
      "Deploy version 2.5.0 to production with full validation and monitoring"
    );

    // Example 2: Incident Response
    // await runDevOpsAgent(
    //   "API response time increased by 300% in last hour. Investigate, identify root cause, and fix"
    // );

    // Example 3: Security Audit
    // await runDevOpsAgent(
    //   "Perform comprehensive security audit of the application and infrastructure"
    // );

    // Example 4: Performance Optimization
    // await runDevOpsAgent(
    //   "Analyze application performance and implement optimizations for the checkout flow"
    // );
  } catch (error) {
    console.error('Workflow failed:', error);
    process.exit(1);
  }
}

main();
