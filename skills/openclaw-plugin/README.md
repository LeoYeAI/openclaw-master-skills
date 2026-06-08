# @kevros/openclaw-plugin

Cryptographic policy enforcement for agent tool calls via the [Kevros governance gateway](https://governance.taskhawktech.com).

Every action verified. Every decision signed. Every record hash-chained.

## What it does

This plugin intercepts agent tool calls and enforces governance policy before execution:

1. **before_tool_call** -- Calls `POST /governance/verify` for high-risk tools. Returns `ALLOW`, `CLAMP`, or `DENY` with a cryptographic release token.
2. **after_tool_call** -- Calls `POST /governance/attest` after execution, building a hash-chained provenance record for the agent.

The plugin also registers two callable tools:

- `kevros_verify` -- Verify any action against governance policy on demand.
- `kevros_passport` -- Look up an agent's trust passport (score, tier, badges).

## Installation

```bash
npm install @kevros/openclaw-plugin
```

## Configuration

Add to your OpenClaw configuration:

```json
{
  "plugins": [
    {
      "name": "kevros-governance",
      "config": {
        "gatewayUrl": "https://governance.taskhawktech.com",
        "apiKey": "your-api-key",
        "agentId": "my-agent",
        "mode": "enforce",
        "highRiskTools": ["bash", "computer", "terminal", "exec", "write_file", "edit_file"],
        "autoAttest": true
      }
    }
  ]
}
```

### Configuration options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `gatewayUrl` | `string` | `https://governance.taskhawktech.com` | Kevros gateway base URL |
| `apiKey` | `string` | _(auto-provisions)_ | API key. If not set, the plugin auto-signs up for a free tier key (1,000 calls/month) |
| `agentId` | `string` | hostname | Agent identifier for governance tracking |
| `mode` | `string` | `enforce` | `enforce` (fail-closed), `advisory` (log-only), or `deny` (block all) |
| `highRiskTools` | `string[]` | `["bash", "computer", ...]` | Tool names requiring governance verification |
| `autoAttest` | `boolean` | `true` | Automatically attest tool executions after completion |

## Enforcement modes

### `enforce` (default)

Fail-closed. If the gateway returns `DENY`, the tool call is blocked. If the gateway is unreachable, the tool call is blocked. This is the recommended mode for production.

### `advisory`

Fail-open. All decisions are logged but never enforced. Use this to evaluate governance impact before switching to `enforce`.

### `deny`

Hard block. All high-risk tool calls are unconditionally blocked regardless of gateway state. Use this as a kill-switch.

## Auto-provisioning

If no `apiKey` is configured, the plugin automatically calls `POST /signup` on first use to provision a free-tier API key:

- 1,000 governance calls per month
- 10 requests per minute rate limit
- No credit card or email required

The key is cached in memory for the duration of the session. For persistent usage, set the `apiKey` in your configuration after signup.

## How verification works

When a high-risk tool is called:

```
Agent calls bash("rm -rf /tmp/data")
    |
    v
before_tool_call hook fires
    |
    v
POST /governance/verify
  action_type: "tool:bash"
  action_payload: { tool: "bash", input: { command: "rm -rf /tmp/data" } }
    |
    v
Gateway returns: { decision: "ALLOW", release_token: "abc123...", epoch: 42 }
    |
    v
Tool executes
    |
    v
after_tool_call hook fires
    |
    v
POST /governance/attest
  action_description: "Executed tool: bash"
  action_payload: { tool: "bash", input: {...}, output_summary: "...", release_token: "abc123..." }
    |
    v
Hash-chained provenance record created (epoch 43)
```

## Using the tools

The plugin registers two tools that agents can call directly:

### kevros_verify

```
kevros_verify({
  action_type: "api_call",
  action_payload: { endpoint: "/users", method: "DELETE", user_id: "123" }
})
```

Returns the verification decision, reason, and release token.

### kevros_passport

```
kevros_passport({ agent_id: "some-agent" })
```

Returns trust score, tier, badges, verification/attestation counts, and chain integrity status.

## Requirements

- Node.js 18+ (uses native `fetch`)
- Zero runtime dependencies

## Building from source

```bash
npm install
npm run build
```

## License

MIT
