# Get block by hash

Get the contents of a block given the block hash.

## Method

GET

## Base URL

`https://deep-index.moralis.io/api/v2.2`

## Path

`/block/:block_number_or_hash`

## Path Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| block_number_or_hash | string | Yes | The block number or block hash | \`15863321\` |

## Query Params

| Name | Type | Required | Description | Example |
|------|------|----------|-------------|----------|
| chain | string (eth, 0x1, sepolia, 0xaa36a7, polygon, 0x89, bsc, 0x38, bsc testnet, 0x61, avalanche, 0xa86a, fantom, 0xfa, cronos, 0x19, arbitrum, 0xa4b1, chiliz, 0x15b38, chiliz testnet, 0x15b32, gnosis, 0x64, gnosis testnet, 0x27d8, base, 0x2105, base sepolia, 0x14a34, optimism, 0xa, polygon amoy, 0x13882, linea, 0xe708, moonbeam, 0x504, moonriver, 0x505, moonbase, 0x507, linea sepolia, 0xe705, flow, 0x2eb, flow-testnet, 0x221, ronin, 0x7e4, ronin-testnet, 0x31769, lisk, 0x46f, lisk-sepolia, 0x106a, pulse, 0x171, sei-testnet, 0x530, sei, 0x531, monad, 0x8f) | No | The chain to query | \`eth\` |
| include | string (internal_transactions) | No | If the result should contain the internal transactions. | \`-\` |

## Response Example

Status: 200

Returns the contents of a block

```json
{
  "timestamp": "2021-05-07T11:08:35.000Z",
  "number": 12386788,
  "hash": "0x9b559aef7ea858608c2e554246fe4a24287e7aeeb976848df2b9a2531f4b9171",
  "parent_hash": "0x011d1fc45839de975cc55d758943f9f1d204f80a90eb631f3bf064b80d53e045",
  "nonce": "0xedeb2d8fd2b2bdec",
  "sha3_uncles": "0x1dcc4de8dec75d7aab85b567b6ccd41ad312451b948a7413f0a142fd40d49347",
  "logs_bloom": "0xdde5fc46c5d8bcbd58207bc9f267bf43298e23791a326ff02661e99790da9996b3e0dd912c0b8202d389d282c56e4d11eb2dec4898a32b6b165f1f4cae6aa0079498eab50293f3b8defbf6af11bb75f0408a563ddfc26a3323d1ff5f9849e95d5f034d88a757ddea032c75c00708c9ff34d2207f997cc7d93fd1fa160a6bfaf62a54e31f9fe67ab95752106ba9d185bfdc9b6dc3e17427f844ee74e5c09b17b83ad6e8fc7360f5c7c3e4e1939e77a6374bee57d1fa6b2322b11ad56ad0398302de9b26d6fbfe414aa416bff141fad9d4af6aea19322e47595e342cd377403f417dfd396ab5f151095a5535f51cbc34a40ce9648927b7d1d72ab9daf253e31daf",
  "transactions_root": "0xe4c7bf3aff7ad07f9e80d57f7189f0252592fee6321c2a9bd9b09b6ce0690d27",
  "state_root": "0x49e3bfe7b618e27fde8fa08884803a8458b502c6534af69873a3cc926a7c724b",
  "receipts_root": "0x7cf43d7e837284f036cf92c56973f5e27bdd253ca46168fa195a6b07fa719f23",
  "miner": "0xea674fdde714fd979de3edf0f56aa9716b898ec8",
  "difficulty": "7253857437305950",
  "total_difficulty": "24325637817906576196890",
  "size": "61271",
  "extra_data": "0x65746865726d696e652d6575726f70652d7765737433",
  "gas_limit": "14977947",
  "gas_used": "14964688",
  "transaction_count": "252",
  "transactions": [
    {
      "hash": "0x1ed85b3757a6d31d01a4d6677fc52fd3911d649a0af21fe5ca3f886b153773ed",
      "nonce": "1848059",
      "transaction_index": "108",
      "from_address_entity": "Opensea",
      "from_address_entity_logo": "https://opensea.io/favicon.ico",
      "from_address": "0x267be1c1d684f78cb4f6a176c4911b741e4ffdc0",
      "from_address_label": "Binance 1",
      "to_address_entity": "Beaver Build",
      "to_address_entity_logo": "https://beaverbuild.com/favicon.ico",
      "to_address": "0x003dde3494f30d861d063232c6a8c04394b686ff",
      "to_address_label": "Binance 2",
      "value": "115580000000000000",
      "gas": "30000",
      "gas_price": "52500000000",
      "input": "0x",
      "receipt_cumulative_gas_used": "4923073",
      "receipt_gas_used": "21000",
      "receipt_contract_address": null,
      "receipt_root": null,
      "receipt_status": "1",
      "block_timestamp": "2021-05-07T11:08:35.000Z",
      "block_number": "12386788",
      "block_hash": "0x9b559aef7ea858608c2e554246fe4a24287e7aeeb976848df2b9a2531f4b9171",
      "logs": [
        {
          "log_index": "273",
          "transaction_hash": "0xdd9006489e46670e0e85d1fb88823099e7f596b08aeaac023e9da0851f26fdd5",
          "transaction_index": "204",
          "address": "0x3105d328c66d8d55092358cf595d54608178e9b5",
          "data": "0x00000000000000000000000000000000000000000000000de05239bccd4d537400000000000000000000000000024dbc80a9f80e3d5fc0a0ee30e2693781a443",
          "topic0": "0x2caecd17d02f56fa897705dcc740da2d237c373f70686f4e0d9bd3bf0400ea7a",
          "topic1": "0x000000000000000000000000031002d15b0d0cd7c9129d6f644446368deae391",
          "topic2": "0x000000000000000000000000d25943be09f968ba740e0782a34e710100defae9",
          "topic3": null,
          "block_timestamp": "2021-05-07T11:08:35.000Z",
          "block_number": "12386788",
          "block_hash": "0x9b559aef7ea858608c2e554246fe4a24287e7aeeb976848df2b9a2531f4b9171"
        }
      ],
      "internal_transactions": [
        {
          "transaction_hash": "0x057Ec652A4F150f7FF94f089A38008f49a0DF88e",
          "block_number": 12526958,
          "block_hash": "0x0372c302e3c52e8f2e15d155e2c545e6d802e479236564af052759253b20fd86",
          "type": "CALL",
          "from": "0xd4a3BebD824189481FC45363602b83C9c7e9cbDf",
          "to": "0xa71db868318f0a0bae9411347cd4a6fa23d8d4ef",
          "value": "650000000000000000",
          "gas": "6721975",
          "gas_used": "6721975",
          "input": "0x",
          "output": "0x",
          "error": "Execution reverted"
        }
      ]
    }
  ]
}
```

## Example (curl)

```bash
curl -X GET "https://deep-index.moralis.io/api/v2.2/block/15863321?chain=eth&include=" \
  -H "accept: application/json" \
  -H "X-API-Key: $MORALIS_API_KEY"
```
