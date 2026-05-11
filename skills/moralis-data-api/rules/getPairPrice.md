# Get DEX token pair price

Fetch the current price of a token pair on Uniswap V2-based DEXs.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/:token0_address/:token1_address/price`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| token0_address | string | Yes | The token0 address | \`0xae7ab96520de3a18e5e111b5eaab095312d7fe84\` |
| token1_address | string | Yes | The token1 address | \`0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| chain | string (eth, 0x1, sepolia, 0xaa36a7, polygon, 0x89, bsc, 0x38, bsc testnet, 0x61, avalanche, 0xa86a, fantom, 0xfa, cronos, 0x19, arbitrum, 0xa4b1, chiliz, 0x15b38, chiliz testnet, 0x15b32, gnosis, 0x64, gnosis testnet, 0x27d8, base, 0x2105, base sepolia, 0x14a34, optimism, 0xa, polygon amoy, 0x13882, linea, 0xe708, moonbeam, 0x504, moonriver, 0x505, moonbase, 0x507, linea sepolia, 0xe705, flow, 0x2eb, flow-testnet, 0x221, ronin, 0x7e4, ronin-testnet, 0x31769, lisk, 0x46f, lisk-sepolia, 0x106a, pulse, 0x171, sei-testnet, 0x530, sei, 0x531, monad, 0x8f) | No | The chain to query | \`eth\` |
| to_block | string | No | The block number to get the reserves from | - |
| to_date | string | No | Get the price up to this date (format in seconds or datestring accepted by momentjs)
* Provide the param 'to_block' or 'to_date'
* If 'to_date' and 'to_block' are provided, 'to_block' will be used.
 | - |
| exchange | string | No | The factory name or address of the token exchange | - |

## Response Example

Status: 200

Returns the pair price

```json
{
  "pair_address": "0x4028daac072e492d34a3afdbef0ba7e35d8b55c4",
  "pair_label": "stETH/WETH",
  "exchange": "Uniswap v2",
  "quote_price": "1.000094331827400707",
  "price_usd": "2905.023454928171304346",
  "base_token": {
    "address": "0x6982508145454ce325ddbe47a25d4ec3d2311933",
    "address_label": "Binance 1",
    "name": "Kylin Network",
    "symbol": "KYL",
    "decimals": "18",
    "logo": "https://cdn.moralis.io/eth/0x67b6d479c7bb412c54e03dca8e1bc6740ce6b99c.png",
    "logo_hash": "ee7aa2cdf100649a3521a082116258e862e6971261a39b5cd4e4354fcccbc54d",
    "thumbnail": "https://cdn.moralis.io/eth/0x67b6d479c7bb412c54e03dca8e1bc6740ce6b99c_thumb.png",
    "total_supply": "420689899999994793099999999997400",
    "total_supply_formatted": "420689899999994.7930999999999974",
    "implementations": [
      {
        "chainId": "0x1",
        "chain": "eth",
        "chainName": "Ethereum",
        "address": "0x6982508145454ce325ddbe47a25d4ec3d2311933"
      }
    ],
    "fully_diluted_valuation": "3407271444.05",
    "block_number": "block_number_example",
    "validated": 0,
    "created_at": "created_at_example",
    "possible_spam": "false",
    "verified_contract": false,
    "categories": [
      "stablecoin"
    ],
    "circulating_supply": "4206864.7489303",
    "market_cap": "3407271444.05"
  },
  "quote_token": {
    "address": "0x6982508145454ce325ddbe47a25d4ec3d2311933",
    "address_label": "Binance 1",
    "name": "Kylin Network",
    "symbol": "KYL",
    "decimals": "18",
    "logo": "https://cdn.moralis.io/eth/0x67b6d479c7bb412c54e03dca8e1bc6740ce6b99c.png",
    "logo_hash": "ee7aa2cdf100649a3521a082116258e862e6971261a39b5cd4e4354fcccbc54d",
    "thumbnail": "https://cdn.moralis.io/eth/0x67b6d479c7bb412c54e03dca8e1bc6740ce6b99c_thumb.png",
    "total_supply": "420689899999994793099999999997400",
    "total_supply_formatted": "420689899999994.7930999999999974",
    "implementations": [
      {
        "chainId": "0x1",
        "chain": "eth",
        "chainName": "Ethereum",
        "address": "0x6982508145454ce325ddbe47a25d4ec3d2311933"
      }
    ],
    "fully_diluted_valuation": "3407271444.05",
    "block_number": "block_number_example",
    "validated": 0,
    "created_at": "created_at_example",
    "possible_spam": "false",
    "verified_contract": false,
    "categories": [
      "stablecoin"
    ],
    "circulating_supply": "4206864.7489303",
    "market_cap": "3407271444.05"
  }
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/0xae7ab96520de3a18e5e111b5eaab095312d7fe84/0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2/price?chain=eth" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
