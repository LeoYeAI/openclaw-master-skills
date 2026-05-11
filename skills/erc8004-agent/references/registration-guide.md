# ERC-8004 Registration Guide

> Part of the 8004 Agent Skill v0.0.1

## Registration File Schema (v1)

The `agentURI` onchain resolves to this JSON file. It follows the ERC-8004 registration-v1 schema.

### Required Fields

| Field | Type | Description |
|---|---|---|
| `type` | string | MUST be `"https://eips.ethereum.org/EIPS/eip-8004#registration-v1"` |
| `name` | string | Human-readable agent name |
| `description` | string | What the agent does, pricing, interaction methods |
| `image` | string | URL to agent logo/avatar |
| `services` | array | List of service endpoint objects |
| `active` | boolean | Whether the agent is currently active |

### Optional Fields

| Field | Type | Description |
|---|---|---|
| `x402Support` | boolean | Whether the agent supports x402 micropayments |
| `registrations` | array | List of onchain registrations (populated after minting) |
| `supportedTrust` | array | Trust models: `"reputation"`, `"crypto-economic"`, `"tee-attestation"` |

### Service Endpoint Object

Each entry in the `services` array:

```json
{
  "name": "<protocol-name>",
  "endpoint": "<uri-or-address>",
  "version": "<optional-version-string>"
}
```

**Recognized service names:**

| Name | Endpoint Format | Version Example |
|---|---|---|
| `web` | `https://web.agent.com/` | — |
| `A2A` | `https://agent.com/.well-known/agent-card.json` | `"0.3.0"` |
| `MCP` | `https://mcp.agent.com/` | `"2025-06-18"` |
| `OASF` | `ipfs://{cid}` or URL | `"0.8"` |
| `ENS` | `myagent.eth` | `"v1"` |
| `DID` | `did:method:foobar` | `"v1"` |
| `email` | `mail@agent.com` | — |

Custom service names are allowed. The `version` field is RECOMMENDED but not required.

### OASF Endpoint Extensions

OASF entries support optional `skills` and `domains` arrays for taxonomy tagging:

```json
{
  "name": "OASF",
  "endpoint": "https://github.com/agntcy/oasf/",
  "version": "v0.8.0",
  "skills": ["data_engineering/data_transformation_pipeline", "natural_language_processing/summarization"],
  "domains": ["finance_and_business/investment_services"]
}
```

### Registration Object

Each entry in the `registrations` array:

```json
{
  "agentId": 42,
  "agentRegistry": "eip155:84532:0x8004A818BFB912233c491871b3d84c89A494BD9e"
}
```

An agent MAY have multiple registrations across different chains.

## Onchain Metadata Keys

Set via `setMetadata(agentId, key, value)`. The key `agentWallet` is reserved and MUST be set via `setAgentWallet()` with an EIP-712 signature proof.

Common metadata patterns:
- Custom metadata can store agent version, category, capabilities hash, or any key-value data.
- Metadata values are `bytes` — encode strings as UTF-8 bytes.

## Endpoint Domain Verification

An agent MAY prove control of an HTTPS endpoint-domain by publishing:

```
https://{endpoint-domain}/.well-known/agent-registration.json
```

This file MUST contain at least a `registrations` array with entries matching the onchain agent. If the endpoint domain is the same domain serving the agent's primary registration file, this check is redundant.

## Update Flow

To update agent metadata after initial registration:

1. Modify the registration JSON.
2. Re-upload to IPFS (new CID) or update the hosted file.
3. Call `setAgentURI(agentId, newURI)` onchain.

With Agent0 SDK:

```typescript
const agent = await sdk.loadAgent('84532:42');
agent.updateInfo(undefined, 'Updated description', undefined);
await agent.setMCP('https://new-mcp.agent.com/');
await agent.registerIPFS(); // re-uploads and updates onchain
```

## Transfer Flow

Agent NFTs are standard ERC-721 and can be transferred:

```typescript
const registry = new ethers.Contract(registryAddress, ['function transferFrom(address,address,uint256)'], signer);
await registry.transferFrom(currentOwner, newOwner, agentId);
```

**Important**: On transfer, the `agentWallet` metadata is automatically cleared and must be re-verified by the new owner.

## Wallet Requirements

- The registering address becomes the NFT owner.
- Fund with testnet ETH for gas fees (use chain faucets).
- For Base Sepolia: use the Base Sepolia faucet or bridge from ETH Sepolia.
- Private key is needed for: registration, URI updates, metadata changes, SIWA signing, giving feedback.

## Agent0 SDK Chains & Config

```typescript
// Supported chain IDs for SDK initialization
const SUPPORTED_CHAINS = {
  ETH_SEPOLIA: 11155111,
  BASE_SEPOLIA: 84532,
  POLYGON_AMOY: 80002
};

// Multi-chain agent ID format: "chainId:agentId"
// e.g., "84532:42" for Base Sepolia agent #42
```
