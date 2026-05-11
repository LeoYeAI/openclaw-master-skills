# ERC-8004 Contract Addresses & ABIs

> Part of the 8004 Agent Skill v0.0.1

## Deployed Registry Addresses

### EVM Chains (Mainnets)

| Chain | Chain ID | Identity Registry | Reputation Registry |
|---|---|---|---|
| Base | `8453` | `0x8004A169FB4a3325136EB29fA0ceB6D2e539a432` | `0x8004BAa17C55a88189AE136b182e5fdA19dE9b63` |

### EVM Chains (Testnets)

| Chain | Chain ID | Identity Registry | Reputation Registry |
|---|---|---|---|
| Base Sepolia | `84532` | `0x8004A818BFB912233c491871b3d84c89A494BD9e` | `0x8004B663056A597Dffe9eCcC1965A193B7388713` |
| ETH Sepolia | `11155111` | `0x8004a6090Cd10A7288092483047B097295Fb8847` | — |
| Linea Sepolia | `59141` | `0x8004aa7C931bCE1233973a0C6A667f73F66282e7` | — |
| Polygon Amoy | `80002` | `0x8004ad19E14B9e0654f73353e8a0B600D46C2898` | — |

### Solana

| Network | Program ID |
|---|---|
| Devnet | `HvF3JqhahcX7JfhbDRYYCJ7S3f6nJdrqu5yi9shyTREp` |

## Agent Registry String Format

The `agentRegistry` identifier follows this format:

```
{namespace}:{chainId}:{identityRegistryAddress}
```

Examples:
- Base: `eip155:8453:0x8004A169FB4a3325136EB29fA0ceB6D2e539a432`
- Base Sepolia: `eip155:84532:0x8004A818BFB912233c491871b3d84c89A494BD9e`
- ETH Sepolia: `eip155:11155111:0x8004a6090Cd10A7288092483047B097295Fb8847`
- Polygon Amoy: `eip155:80002:0x8004ad19E14B9e0654f73353e8a0B600D46C2898`

## Identity Registry ABI (Key Functions)

```json
[
  "function register(string agentURI) external returns (uint256 agentId)",
  "function register(string agentURI, tuple(string metadataKey, bytes metadataValue)[] metadata) external returns (uint256 agentId)",
  "function register() external returns (uint256 agentId)",
  "function setAgentURI(uint256 agentId, string newURI) external",
  "function tokenURI(uint256 tokenId) external view returns (string)",
  "function ownerOf(uint256 tokenId) external view returns (address)",
  "function getMetadata(uint256 agentId, string metadataKey) external view returns (bytes)",
  "function setMetadata(uint256 agentId, string metadataKey, bytes metadataValue) external",
  "function getAgentWallet(uint256 agentId) external view returns (address)",
  "function setAgentWallet(uint256 agentId, address newWallet, uint256 deadline, bytes signature) external",
  "function unsetAgentWallet(uint256 agentId) external",
  "event Registered(uint256 indexed agentId, string agentURI, address indexed owner)",
  "event URIUpdated(uint256 indexed agentId, string newURI, address indexed updatedBy)",
  "event MetadataSet(uint256 indexed agentId, string indexed indexedMetadataKey, string metadataKey, bytes metadataValue)"
]
```

## Reputation Registry ABI (Key Functions)

```json
[
  "function giveFeedback(uint256 agentId, int128 value, uint8 valueDecimals, string tag1, string tag2, string endpoint, string feedbackURI, bytes32 feedbackHash) external",
  "function revokeFeedback(uint256 agentId, uint64 feedbackIndex) external",
  "function appendResponse(uint256 agentId, address clientAddress, uint64 feedbackIndex, string responseURI, bytes32 responseHash) external",
  "function getSummary(uint256 agentId, address[] clientAddresses, string tag1, string tag2) external view returns (uint64 count, int128 summaryValue, uint8 summaryValueDecimals)",
  "function readFeedback(uint256 agentId, address clientAddress, uint64 feedbackIndex) external view returns (int128 value, uint8 valueDecimals, string tag1, string tag2, bool isRevoked)",
  "function getClients(uint256 agentId) external view returns (address[])",
  "function getLastIndex(uint256 agentId, address clientAddress) external view returns (uint64)"
]
```

## Validation Registry ABI (Key Functions)

```json
[
  "function validationRequest(address validatorAddress, uint256 agentId, string requestURI, bytes32 requestHash) external",
  "function validationResponse(bytes32 requestHash, uint8 response, string responseURI, bytes32 responseHash, string tag) external",
  "function getValidationStatus(bytes32 requestHash) external view returns (address validatorAddress, uint256 agentId, uint8 response, bytes32 responseHash, string tag, uint256 lastUpdate)",
  "function getSummary(uint256 agentId, address[] validatorAddresses, string tag) external view returns (uint64 count, uint8 averageResponse)",
  "function getAgentValidations(uint256 agentId) external view returns (bytes32[])",
  "function getValidatorRequests(address validatorAddress) external view returns (bytes32[])"
]
```

## RPC Endpoints (Public)

| Chain | Public RPC |
|---|---|
| Base | `https://mainnet.base.org` |
| Base Sepolia | `https://sepolia.base.org` |
| ETH Sepolia | `https://rpc.sepolia.org` |
| Linea Sepolia | `https://rpc.sepolia.linea.build` |
| Polygon Amoy | `https://rpc-amoy.polygon.technology` |

For production use, use a provider like Alchemy or Infura with your own API key.

## Agent0 SDK Default Subgraph URLs

The Agent0 SDK auto-configures subgraph endpoints per chain for indexed queries (search, feedback aggregation). No manual configuration needed when using the SDK.

## 8004scan Explorer

View any registered agent at: `https://www.8004scan.io/`

After registration, agents are browsable by agentId and chain.
