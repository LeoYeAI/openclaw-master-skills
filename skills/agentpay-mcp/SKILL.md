---
name: agentpay-mcp
description: MCP (Model Context Protocol) payment server for AI agents. Adds drop-in x402 Payment Required handling to Claude, LangChain, CrewAI, and other MCP-compatible agents. Automatically negotiates and completes 402 payment flows so agents can access pay-per-use APIs without manual payment logic.
---

# AgentPay MCP

An MCP server that gives AI agents the ability to pay for services automatically. When an API returns an HTTP 402 Payment Required response, AgentPay MCP handles the full payment negotiation and retry cycle — no custom payment code required in the agent.

- **GitHub**: https://github.com/up2itnow0822/agentpay-mcp
- **npm**: `agentpay-mcp`

## Core Capabilities

- **Automatic 402 handling** — intercepts HTTP 402 responses and completes the payment flow transparently
- **MCP-native** — exposes payment tools via the Model Context Protocol; works with any MCP host
- **Multi-framework support** — compatible with Claude Desktop, LangChain, CrewAI, and custom MCP clients
- **Configurable spend limits** — set per-request and session-level payment ceilings
- **Audit log** — records every payment attempt and outcome for review

## Setup

```bash
npm install -g agentpay-mcp
```

Set a wallet private key for the agent to sign payments:

```bash
export AGENTPAY_PRIVATE_KEY=0x...
export AGENTPAY_MAX_PER_REQUEST=0.10   # USD ceiling per payment
export AGENTPAY_MAX_PER_SESSION=1.00   # USD ceiling per session
```

## Claude Desktop Integration

Add to `~/.config/claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "agentpay": {
      "command": "agentpay-mcp",
      "env": {
        "AGENTPAY_PRIVATE_KEY": "0x...",
        "AGENTPAY_MAX_PER_REQUEST": "0.10",
        "AGENTPAY_MAX_PER_SESSION": "1.00"
      }
    }
  }
}
```

Restart Claude Desktop. The agent will now be able to call `agentpay_fetch` when it needs to access pay-per-use endpoints.

## LangChain Integration

```python
from langchain_mcp import MCPToolkit

toolkit = MCPToolkit(server_command=["agentpay-mcp"])
tools = toolkit.get_tools()

# Pass tools to your LangChain agent — payment handling is automatic
agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION)
```

## CrewAI Integration

```python
from crewai_tools import MCPServerAdapter

agentpay_tools = MCPServerAdapter(
    command="agentpay-mcp",
    env={"AGENTPAY_PRIVATE_KEY": "0x..."}
)

agent = Agent(
    role="Researcher",
    tools=agentpay_tools.tools,
    ...
)
```

## MCP Tools Exposed

| Tool | Description |
|------|-------------|
| `agentpay_fetch` | Fetch a URL; pays automatically if the server returns 402 |
| `agentpay_status` | Show session spend total and remaining budget |
| `agentpay_history` | List payment events for the current session |

### agentpay_fetch

```json
{
  "tool": "agentpay_fetch",
  "arguments": {
    "url": "https://api.example.com/data",
    "method": "GET",
    "maxPayment": "0.05"
  }
}
```

The server:
1. Sends the request to the target URL
2. If 200 — returns the response body directly
3. If 402 — reads the `X-Payment` header, signs and submits payment, retries the request
4. Returns the final response or an error if payment was refused or limits exceeded

## x402 Payment Flow

AgentPay MCP implements the [x402 protocol](https://x402.org):

1. Agent calls `agentpay_fetch` with a URL
2. Server receives HTTP `402 Payment Required` with payment details in headers
3. AgentPay signs the payment using the configured private key
4. Retries the original request with a `X-Payment` proof header
5. Returns the unlocked response to the agent

## Security Rules

1. **Set spend limits.** Always configure `AGENTPAY_MAX_PER_REQUEST` and `AGENTPAY_MAX_PER_SESSION` before deploying.
2. **Never expose private keys in logs or prompts.** Use environment variables only.
3. **Review payment history periodically.** Use `agentpay_history` to audit what the agent paid for.
4. **Test with low limits first.** Start with `maxPayment: 0.001` to verify the flow before raising limits.

## References

- GitHub: https://github.com/up2itnow0822/agentpay-mcp
- npm: https://www.npmjs.com/package/agentpay-mcp
- x402 protocol: https://x402.org
- MCP specification: https://modelcontextprotocol.io
