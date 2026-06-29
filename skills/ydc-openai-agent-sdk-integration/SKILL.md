---
name: ydc-openai-agent-sdk-integration
description: Integrate OpenAI Agents SDK with You.com MCP server - Hosted and Streamable HTTP support for Python and TypeScript. Use when developer mentions OpenAI Agents SDK, OpenAI agents, or integrating OpenAI with MCP.
license: MIT
compatibility: Python 3.10+ or Node.js 18+ with TypeScript
metadata:
  author: youdotcom-oss
  category: sdk-integration
  version: "1.0.0"
  keywords: openai,openai-agents,agent-sdk,mcp,you.com,integration,hosted-mcp,streamable-http,web-search,python,typescript
---

# Integrate OpenAI Agents SDK with You.com MCP

Interactive workflow to set up OpenAI Agents SDK with You.com's MCP server.

## Workflow

1. **Ask: Language Choice**
   * Python or TypeScript?

2. **Ask: MCP Configuration Type**
   * **Hosted MCP** (OpenAI-managed with server URL): Recommended for simplicity
   * **Streamable HTTP** (Self-managed connection): For custom infrastructure

3. **Install Package**
   * Python: `pip install openai-agents`
   * TypeScript: `npm install @openai/agents`

4. **Ask: Environment Variables**

   **For Both Modes:**
   * `YDC_API_KEY` (You.com API key for Bearer token)
   * `OPENAI_API_KEY` (OpenAI API key)

   Have they set them?
   * If NO: Guide to get keys:
     - YDC_API_KEY: https://you.com/platform/api-keys
     - OPENAI_API_KEY: https://platform.openai.com/api-keys

5. **Ask: File Location**
   * NEW file: Ask where to create and what to name
   * EXISTING file: Ask which file to integrate into (add MCP config)

6. **Create/Update File**

   **For NEW files:**
   * Use the complete template code from the "Complete Templates" section below
   * User can run immediately with their API keys set

   **For EXISTING files:**
   * Add MCP server configuration to their existing code

   **Hosted MCP configuration block (Python)**:
   ```python
   from agents import Agent, Runner
   from agents.mcp import HostedMCPTool

   # Validate: ydc_api_key = os.getenv("YDC_API_KEY")
   agent = Agent(
       name="Assistant",
       instructions="Use You.com tools to answer questions.",
       tools=[
           HostedMCPTool(
               tool_config={
                   "type": "mcp",
                   "server_label": "ydc",
                   "server_url": "https://api.you.com/mcp",
                   "headers": {
                       "Authorization": f"Bearer {ydc_api_key}"
                   },
                   "require_approval": "never",
               }
           )
       ],
   )
   ```

   **Hosted MCP configuration block (TypeScript)**:
   ```typescript
   import { Agent, hostedMcpTool } from '@openai/agents';

   // Validate: const ydcApiKey = process.env.YDC_API_KEY;
   const agent = new Agent({
     name: 'Assistant',
     instructions: 'Use You.com tools to answer questions.',
     tools: [
       hostedMcpTool({
        serverLabel: 'ydc',
         serverUrl: 'https://api.you.com/mcp',
         headers: {
           Authorization: `Bearer ${ydcApiKey}`,
         },
       }),
     ],
   });
   ```

   **Streamable HTTP configuration block (Python)**:
   ```python
   from agents import Agent, Runner
   from agents.mcp import MCPServerStreamableHttp

   # Validate: ydc_api_key = os.getenv("YDC_API_KEY")
   async with MCPServerStreamableHttp(
       name="You.com MCP Server",
       params={
           "url": "https://api.you.com/mcp",
           "headers": {"Authorization": f"Bearer {ydc_api_key}"},
           "timeout": 10,
       },
       cache_tools_list=True,
       max_retry_attempts=3,
   ) as server:
       agent = Agent(
           name="Assistant",
           instructions="Use You.com tools to answer questions.",
           mcp_servers=[server],
       )
   ```

   **Streamable HTTP configuration block (TypeScript)**:
   ```typescript
   import { Agent, MCPServerStreamableHttp } from '@openai/agents';

   // Validate: const ydcApiKey = process.env.YDC_API_KEY;
   const mcpServer = new MCPServerStreamableHttp({
     url: 'https://api.you.com/mcp',
     name: 'You.com MCP Server',
     requestInit: {
       headers: {
         Authorization: `Bearer ${ydcApiKey}`,
       },
     },
   });

   const agent = new Agent({
     name: 'Assistant',
     instructions: 'Use You.com tools to answer questions.',
     mcpServers: [mcpServer],
   });
   ```

## Complete Templates

Use these complete templates for new files. Each template is ready to run with your API keys set.

### Python Hosted MCP Template (Complete Example)

```python
"""
OpenAI Agents SDK with You.com Hosted MCP
Python implementation with OpenAI-managed infrastructure
"""

import os
import asyncio
from agents import Agent, Runner
from agents.mcp import HostedMCPTool

# Validate environment variables
ydc_api_key = os.getenv("YDC_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

if not ydc_api_key:
    raise ValueError(
        "YDC_API_KEY environment variable is required. "
        "Get your key at: https://you.com/platform/api-keys"
    )

if not openai_api_key:
    raise ValueError(
        "OPENAI_API_KEY environment variable is required. "
        "Get your key at: https://platform.openai.com/api-keys"
    )


async def main():
    """
    Example: Search for AI news using You.com hosted MCP tools
    """
    # Configure agent with hosted MCP tools
    agent = Agent(
        name="AI News Assistant",
        instructions="Use You.com tools to search for and answer questions about AI news.",
        tools=[
            HostedMCPTool(
                tool_config={
                    "type": "mcp",
                    "server_label": "ydc",
                    "server_url": "https://api.you.com/mcp",
                    "headers": {
                        "Authorization": f"Bearer {ydc_api_key}"
                    },
                    "require_approval": "never",
                }
            )
        ],
    )

    # Run agent with user query
    result = await Runner.run(
        agent,
        "Search for the latest AI news from this week"
    )

    print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
```

### Python Streamable HTTP Template (Complete Example)

```python
"""
OpenAI Agents SDK with You.com Streamable HTTP MCP
Python implementation with self-managed connection
"""

import os
import asyncio
from agents import Agent, Runner
from agents.mcp import MCPServerStreamableHttp

# Validate environment variables
ydc_api_key = os.getenv("YDC_API_KEY")
openai_api_key = os.getenv("OPENAI_API_KEY")

if not ydc_api_key:
    raise ValueError(
        "YDC_API_KEY environment variable is required. "
        "Get your key at: https://you.com/platform/api-keys"
    )

if not openai_api_key:
    raise ValueError(
        "OPENAI_API_KEY environment variable is required. "
        "Get your key at: https://platform.openai.com/api-keys"
    )


async def main():
    """
    Example: Search for AI news using You.com streamable HTTP MCP server
    """
    # Configure streamable HTTP MCP server
    async with MCPServerStreamableHttp(
        name="You.com MCP Server",
        params={
            "url": "https://api.you.com/mcp",
            "headers": {"Authorization": f"Bearer {ydc_api_key}"},
            "timeout": 10,
        },
        cache_tools_list=True,
        max_retry_attempts=3,
    ) as server:
        # Configure agent with MCP server
        agent = Agent(
            name="AI News Assistant",
            instructions="Use You.com tools to search for and answer questions about AI news.",
            mcp_servers=[server],
        )

        # Run agent with user query
        result = await Runner.run(
            agent,
            "Search for the latest AI news from this week"
        )

        print(result.final_output)


if __name__ == "__main__":
    asyncio.run(main())
```

### TypeScript Hosted MCP Template (Complete Example)

```typescript
/**
 * OpenAI Agents SDK with You.com Hosted MCP
 * TypeScript implementation with OpenAI-managed infrastructure
 */

import { Agent, run, hostedMcpTool } from '@openai/agents';

// Validate environment variables
const ydcApiKey = process.env.YDC_API_KEY;
const openaiApiKey = process.env.OPENAI_API_KEY;

if (!ydcApiKey) {
  throw new Error(
    'YDC_API_KEY environment variable is required. ' +
      'Get your key at: https://you.com/platform/api-keys'
  );
}

if (!openaiApiKey) {
  throw new Error(
    'OPENAI_API_KEY environment variable is required. ' +
      'Get your key at: https://platform.openai.com/api-keys'
  );
}

/**
 * Example: Search for AI news using You.com hosted MCP tools
 */
async function main() {
  // Configure agent with hosted MCP tools
  const agent = new Agent({
    name: 'AI News Assistant',
    instructions:
      'Use You.com tools to search for and answer questions about AI news.',
    tools: [
      hostedMcpTool({
        serverLabel: 'ydc',
        serverUrl: 'https://api.you.com/mcp',
        headers: {
          Authorization: `Bearer ${ydcApiKey}`,
        },
      }),
    ],
  });

  // Run agent with user query
  const result = await run(
    agent,
    'Search for the latest AI news from this week'
  );

  console.log(result.finalOutput);
}

main().catch(console.error);
```

### TypeScript Streamable HTTP Template (Complete Example)

```typescript
/**
 * OpenAI Agents SDK with You.com Streamable HTTP MCP
 * TypeScript implementation with self-managed connection
 */

import { Agent, run, MCPServerStreamableHttp } from '@openai/agents';

// Validate environment variables
const ydcApiKey = process.env.YDC_API_KEY;
const openaiApiKey = process.env.OPENAI_API_KEY;

if (!ydcApiKey) {
  throw new Error(
    'YDC_API_KEY environment variable is required. ' +
      'Get your key at: https://you.com/platform/api-keys'
  );
}

if (!openaiApiKey) {
  throw new Error(
    'OPENAI_API_KEY environment variable is required. ' +
      'Get your key at: https://platform.openai.com/api-keys'
  );
}

/**
 * Example: Search for AI news using You.com streamable HTTP MCP server
 */
async function main() {
  // Configure streamable HTTP MCP server
  const mcpServer = new MCPServerStreamableHttp({
    url: 'https://api.you.com/mcp',
    name: 'You.com MCP Server',
    requestInit: {
      headers: {
        Authorization: `Bearer ${ydcApiKey}`,
      },
    },
  });

  try {
    // Connect to MCP server
    await mcpServer.connect();

    // Configure agent with MCP server
    const agent = new Agent({
      name: 'AI News Assistant',
      instructions:
        'Use You.com tools to search for and answer questions about AI news.',
      mcpServers: [mcpServer],
    });

    // Run agent with user query
    const result = await run(
      agent,
      'Search for the latest AI news from this week'
    );

    console.log(result.finalOutput);
  } finally {
    // Clean up connection
    await mcpServer.close();
  }
}

main().catch(console.error);
```

## MCP Configuration Types

### Hosted MCP (Recommended)

**What it is:** OpenAI manages the MCP connection and tool routing through their Responses API.

**Benefits:**
- ✅ Simpler configuration (no connection management)
- ✅ OpenAI handles authentication and retries
- ✅ Lower latency (tools run in OpenAI infrastructure)
- ✅ Automatic tool discovery and listing
- ✅ No need to manage async context or cleanup

**Use when:**
- Building production applications
- Want minimal boilerplate code
- Need reliable tool execution
- Don't require custom transport layer

**Configuration:**

**Python:**
```python
from agents.mcp import HostedMCPTool

tools=[
    HostedMCPTool(
        tool_config={
            "type": "mcp",
            "server_label": "ydc",
            "server_url": "https://api.you.com/mcp",
            "headers": {
                "Authorization": f"Bearer {os.environ['YDC_API_KEY']}"
            },
            "require_approval": "never",
        }
    )
]
```

**TypeScript:**
```typescript
import { hostedMcpTool } from '@openai/agents';

tools: [
  hostedMcpTool({
    serverLabel: 'ydc',
    serverUrl: 'https://api.you.com/mcp',
    headers: {
      Authorization: `Bearer ${process.env.YDC_API_KEY}`,
    },
  }),
]
```

### Streamable HTTP MCP

**What it is:** You manage the MCP connection and transport layer yourself.

**Benefits:**
- ✅ Full control over network connection
- ✅ Custom infrastructure integration
- ✅ Can add custom headers, timeouts, retry logic
- ✅ Run MCP server in your own environment
- ✅ Better for testing and development

**Use when:**
- Need custom transport configuration
- Running MCP server in your infrastructure
- Require specific networking setup
- Development and testing scenarios

**Configuration:**

**Python:**
```python
from agents.mcp import MCPServerStreamableHttp

async with MCPServerStreamableHttp(
    name="You.com MCP Server",
    params={
        "url": "https://api.you.com/mcp",
        "headers": {"Authorization": f"Bearer {os.environ['YDC_API_KEY']}"},
        "timeout": 10,
    },
    cache_tools_list=True,
    max_retry_attempts=3,
) as server:
    agent = Agent(mcp_servers=[server])
```

**TypeScript:**
```typescript
import { MCPServerStreamableHttp } from '@openai/agents';

const mcpServer = new MCPServerStreamableHttp({
  url: 'https://api.you.com/mcp',
  name: 'You.com MCP Server',
  requestInit: {
    headers: {
      Authorization: `Bearer ${process.env.YDC_API_KEY}`,
    },
  },
});

await mcpServer.connect();
try {
  const agent = new Agent({ mcpServers: [mcpServer] });
  // Use agent
} finally {
  await mcpServer.close();
}
```

## Available You.com Tools

After configuration, agents can discover and use:
- `mcp__ydc__you_search` - Web and news search
- `mcp__ydc__you_express` - AI-powered answers with web context  
- `mcp__ydc__you_contents` - Web page content extraction

## Environment Variables

Both API keys are required for both configuration modes:

```bash
# Add to your .env file or shell profile
export YDC_API_KEY="your-you-api-key-here"
export OPENAI_API_KEY="your-openai-api-key-here"
```

**Get your API keys:**
- You.com: https://you.com/platform/api-keys
- OpenAI: https://platform.openai.com/api-keys

## Validation Checklist

Before completing:

- [ ] Package installed: `openai-agents` (Python) or `@openai/agents` (TypeScript)
- [ ] Environment variables set: `YDC_API_KEY` and `OPENAI_API_KEY`
- [ ] Template copied or configuration added to existing file
- [ ] MCP configuration type chosen (Hosted or Streamable HTTP)
- [ ] Authorization headers configured with Bearer token
- [ ] File is executable (Python) or can be compiled (TypeScript)
- [ ] Ready to test with example query

## Testing Your Integration

**Python:**
```bash
python your-file.py
```

**TypeScript:**
```bash
# With tsx (recommended for quick testing)
npx tsx your-file.ts

# Or compile and run
tsc your-file.ts && node your-file.js
```

## Common Issues

<details>
<summary><strong>Cannot find module @openai/agents</strong></summary>

Install the package:

```bash
# NPM
npm install @openai/agents

# Bun
bun add @openai/agents

# Yarn
yarn add @openai/agents

# pnpm
pnpm add @openai/agents
```

</details>

<details>
<summary><strong>YDC_API_KEY environment variable is required</strong></summary>

Set your You.com API key:

```bash
export YDC_API_KEY="your-api-key-here"
```

Get your key at: https://you.com/platform/api-keys

</details>

<details>
<summary><strong>OPENAI_API_KEY environment variable is required</strong></summary>

Set your OpenAI API key:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

Get your key at: https://platform.openai.com/api-keys

</details>

<details>
<summary><strong>MCP connection fails with 401 Unauthorized</strong></summary>

Verify your YDC_API_KEY is valid:
1. Check the key at https://you.com/platform/api-keys
2. Ensure no extra spaces or quotes in the environment variable
3. Verify the Authorization header format: `Bearer ${YDC_API_KEY}`

</details>

<details>
<summary><strong>Tools not available or not being called</strong></summary>

**For Both Modes:**
- Ensure `server_url: "https://api.you.com/mcp"` is correct
- Verify Authorization header includes `Bearer` prefix
- Check `YDC_API_KEY` environment variable is set
- Confirm `require_approval` is set to `"never"` for automatic execution

**For Streamable HTTP specifically:**
- Ensure MCP server is connected before creating agent
- Verify connection was successful before running agent

</details>

<details>
<summary><strong>Connection timeout or network errors</strong></summary>

**For Streamable HTTP only:**

Increase timeout or retry attempts:

**Python:**
```python
async with MCPServerStreamableHttp(
    params={
        "url": "https://api.you.com/mcp",
        "headers": {"Authorization": f"Bearer {os.environ['YDC_API_KEY']}"},
        "timeout": 30,  # Increased timeout
    },
    max_retry_attempts=5,  # More retries
) as server:
    # ...
```

**TypeScript:**
```typescript
const mcpServer = new MCPServerStreamableHttp({
  url: 'https://api.you.com/mcp',
  requestInit: {
    headers: { Authorization: `Bearer ${process.env.YDC_API_KEY}` },
    // Add custom timeout via fetch options
  },
});
```

</details>



## Additional Resources

* **OpenAI Agents SDK (Python)**: https://openai.github.io/openai-agents-python/
* **OpenAI Agents SDK (TypeScript)**: https://openai.github.io/openai-agents-js/
* **MCP Configuration (Python)**: https://openai.github.io/openai-agents-python/mcp/
* **MCP Configuration (TypeScript)**: https://openai.github.io/openai-agents-js/guides/mcp/
* **You.com MCP Server**: https://documentation.you.com/developer-resources/mcp-server
* **API Keys**:
  - You.com: https://you.com/platform/api-keys
  - OpenAI: https://platform.openai.com/api-keys
