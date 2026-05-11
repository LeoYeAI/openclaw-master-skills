import { query, createSdkMcpServer, tool } from "@anthropic-ai/claude-agent-sdk";
import { z } from "zod";

/**
 * Custom MCP Server Template
 *
 * Demonstrates:
 * - Creating in-process MCP server
 * - Defining tools with Zod schemas
 * - Multiple tools in one server
 * - Error handling in tools
 */

// Define a custom MCP server with multiple tools
const weatherServer = createSdkMcpServer({
  name: "weather-service",
  version: "1.0.0",
  tools: [
    tool(
      "get_weather",
      "Get current weather for a location",
      {
        location: z.string().describe("City name or coordinates"),
        units: z.enum(["celsius", "fahrenheit"]).default("celsius")
      },
      async (args) => {
        try {
          // Simulate API call
          const response = await fetch(
            `https://api.weather.com/v1/current?location=${args.location}&units=${args.units}`
          );
          const data = await response.json();

          return {
            content: [{
              type: "text",
              text: `Temperature: ${data.temp}° ${args.units}\nConditions: ${data.conditions}\nHumidity: ${data.humidity}%`
            }]
          };
        } catch (error) {
          return {
            content: [{
              type: "text",
              text: `Error fetching weather: ${error.message}`
            }],
            isError: true
          };
        }
      }
    ),
    tool(
      "get_forecast",
      "Get weather forecast for next 7 days",
      {
        location: z.string(),
        days: z.number().min(1).max(7).default(7)
      },
      async (args) => {
        // Simulated forecast data
        return {
          content: [{
            type: "text",
            text: `7-day forecast for ${args.location}: Mostly sunny with temperatures ranging from 15-25°C`
          }]
        };
      }
    )
  ]
});

// Database tools server
const databaseServer = createSdkMcpServer({
  name: "database",
  version: "1.0.0",
  tools: [
    tool(
      "query_users",
      "Query user records from the database",
      {
        email: z.string().email().optional(),
        limit: z.number().min(1).max(100).default(10),
        offset: z.number().min(0).default(0)
      },
      async (args) => {
        // Simulated database query
        const results = [
          { id: 1, email: "user1@example.com", name: "User 1" },
          { id: 2, email: "user2@example.com", name: "User 2" }
        ];

        return {
          content: [{
            type: "text",
            text: JSON.stringify(results, null, 2)
          }]
        };
      }
    ),
    tool(
      "calculate",
      "Perform mathematical calculations",
      {
        expression: z.string().describe("Mathematical expression to evaluate"),
        precision: z.number().min(0).max(10).default(2)
      },
      async (args) => {
        try {
          // In production, use a proper math parser (e.g., mathjs)
          const result = eval(args.expression);
          const rounded = Number(result.toFixed(args.precision));

          return {
            content: [{
              type: "text",
              text: `Result: ${rounded}`
            }]
          };
        } catch (error) {
          return {
            content: [{
              type: "text",
              text: `Invalid expression: ${error.message}`
            }],
            isError: true
          };
        }
      }
    )
  ]
});

// Use custom tools in query
async function useCustomTools() {
  const response = query({
    prompt: "What's the weather in San Francisco? Also query users with gmail addresses and calculate 15% tip on $85.50",
    options: {
      model: "claude-sonnet-4-5",
      mcpServers: {
        "weather-service": weatherServer,
        "database": databaseServer
      },
      allowedTools: [
        "mcp__weather-service__get_weather",
        "mcp__weather-service__get_forecast",
        "mcp__database__query_users",
        "mcp__database__calculate"
      ]
    }
  });

  for await (const message of response) {
    if (message.type === 'assistant') {
      console.log('Assistant:', message.content);
    } else if (message.type === 'tool_call') {
      console.log(`\n🔧 ${message.tool_name}:`, message.input);
    }
  }
}

// Run
useCustomTools().catch(console.error);
