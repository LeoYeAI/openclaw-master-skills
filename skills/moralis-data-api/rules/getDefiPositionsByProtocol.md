# Get detailed DeFi positions by protocol for a wallet

Fetch detailed DeFi positions for a given wallet and protocol.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/wallets/:address/defi/:protocol/positions`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| address | string | Yes | Wallet address | \`0xd100d8b69c5ae23d6aa30c6c3874bf47539b95fd\` |
| protocol | string (uniswap-v2, uniswap-v3, pancakeswap-v2, pancakeswap-v3, quickswap-v2, quickswap-v3, sushiswap-v2, aave-v2, aave-v3, aave-lido, fraxswap-v1, fraxswap-v2, lido, makerdao, eigenlayer, pendle, etherfi, rocketpool, sparkfi, takara-lend, neverland, kintsu) | Yes | The protocol to query | \`uniswap-v3\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| chain | string (eth, 0x1, sepolia, 0xaa36a7, polygon, 0x89, bsc, 0x38, bsc testnet, 0x61, avalanche, 0xa86a, fantom, 0xfa, cronos, 0x19, arbitrum, 0xa4b1, chiliz, 0x15b38, chiliz testnet, 0x15b32, gnosis, 0x64, gnosis testnet, 0x27d8, base, 0x2105, base sepolia, 0x14a34, optimism, 0xa, polygon amoy, 0x13882, linea, 0xe708, moonbeam, 0x504, moonriver, 0x505, moonbase, 0x507, linea sepolia, 0xe705, flow, 0x2eb, flow-testnet, 0x221, ronin, 0x7e4, ronin-testnet, 0x31769, lisk, 0x46f, lisk-sepolia, 0x106a, pulse, 0x171, sei-testnet, 0x530, sei, 0x531, monad, 0x8f) | No | The chain to query | \`eth\` |

## Response Example

Status: 200

Returns the defi positions by protocol for the wallet address.

```json
{
  "protocol_name": "Uniswap v2",
  "protocol_id": "uniswap-v2",
  "protocol_url": "https://app.uniswap.org/pools/v2",
  "protocol_logo": "https://cdn.moralis.io/defi/uniswap.png",
  "total_usd_value": 47754.14278954011,
  "total_unclaimed_usd_value": null,
  "positions": [
    {
      "label": "liquidity",
      "tokens": [
        {
          "token_type": "defi-token",
          "name": "Wrapped Ether",
          "symbol": "WETH",
          "contract_address": "0x06012c8cf97bead5deae237070f9587f8e7a266d",
          "decimals": "18",
          "logo": "https://cdn.moralis.io/tokens/0x0000000000085d4780b73119b644ae5ecd22b376.png",
          "thumbnail": "https://cdn.moralis.io/tokens/0x0000000000085d4780b73119b644ae5ecd22b376.png",
          "balance": "1000000",
          "balance_formatted": "1.000000",
          "usd_price": "1000000",
          "usd_value": "1000000"
        }
      ],
      "address": "0x06012c8cf97bead5deae237070f9587f8e7a266d",
      "balance_usd": "1000000",
      "total_unclaimed_usd_value": "1000000",
      "position_details": {
        "fee_tier": 0,
        "range_tnd": 0,
        "reserves": [],
        "current_price": 0,
        "is_in_range": true,
        "price_upper": 0,
        "price_lower": 0,
        "price_label": "price_label_example",
        "liquidity": 0,
        "range_start": 0,
        "pool_address": "pool_address_example",
        "position_key": "position_key_example",
        "nft_metadata": {},
        "asset_standard": "asset_standard_example",
        "apy": 0,
        "is_debt": true,
        "is_variable_debt": true,
        "is_stable_debt": true,
        "shares": "shares_example",
        "reserve0": "reserve0_example",
        "reserve1": "reserve1_example",
        "factory": "factory_example",
        "pair": "pair_example",
        "share_of_pool": 0,
        "no_price_available": true,
        "shares_in_strategy": "shares_in_strategy_example",
        "strategy_address": "strategy_address_example",
        "base_type": "base_type_example",
        "health_factor": 0,
        "is_enabled_collateral": true
      }
    }
  ]
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/wallets/0xd100d8b69c5ae23d6aa30c6c3874bf47539b95fd/defi/uniswap-v3/positions?chain=eth" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
