# Agent Creator & Agent Wallets

This document covers how to identify tokens created by an AI agent (Agent Creator) and how to identify agent wallets on-chain.

---

## How to Identify Token Created By Agent Creator

Tokens created by AI agents can be identified via both on-chain template bits and off-chain API fields. This flag only marks that the token creator is an **Agent wallet** and **does not imply any new special trading mode or behavior** of the token itself.

### On-chain method

Read the token's `template` from TokenManager2:

```solidity
template = TokenManager2._tokenInfos[tokenAddress].template;
bool isCreatedByAgent = (template & (1 << 85)) != 0;
```

- If `isCreatedByAgent` is `true`, the token was **created by an AI agent**.
- If `isCreatedByAgent` is `false`, the token was **not** created by an AI agent.

### Off-chain method

Query token info via:

- `GET https://four.meme/meme-api/v1/private/token/get?address=<token address>`
- `GET https://four.meme/meme-api/v1/private/token/getById?id=<requestId>` (requestId from TokenCreate event)

Check the `aiCreator` field in the response `data`:

- If `aiCreator === true`, the token was **created by an AI agent**.
- If `aiCreator === false`, the token was **not** created by an AI agent.

**Example response:**

```json
{
  "code": "0",
  "data": {
    "aiCreator": true,
    ...
  }
}
```

---

## How to Identify Agent Wallets

You can determine whether a wallet address is an **Agent wallet** by calling the **AgentIdentifier** contract.

### On-chain method

**Contract (BSC)**

- **Address**: `0x09B44A633de9F9EBF6FB9Bdd5b5629d3DD2cef13`
- **ABI**: See official Four.meme API / Protocol Integration docs (`AgentIdentifier.abi`).

**Interface**

```solidity
interface IAgentIdentifier {
    function isAgent(address wallet) external view returns (bool);
    function nftCount() external view returns (uint256);
    function nftAt(uint256 index) external view returns (address);
}
```

**Usage**

Call `isAgent(wallet)` on the AgentIdentifier contract:

```solidity
IAgentIdentifier ai = IAgentIdentifier(0x09B44A633de9F9EBF6FB9Bdd5b5629d3DD2cef13);
bool isAgent = ai.isAgent(wallet);
```

- Returns `true` if the wallet is an Agent wallet, otherwise `false`.
- Logic: `isAgent(wallet)` is `true` when the wallet holds any Agent NFT (`balanceOf(wallet) > 0`).

**Querying configured Agent NFTs**

- `nftCount()` — number of Agent NFT contracts registered.
- `nftAt(index)` — Agent NFT contract address at `index`.

Tokens created by wallets with `isAgent == true` are marked as **Agent Creator** and can be identified as **Token Created By Agent Creator** using the methods above.
