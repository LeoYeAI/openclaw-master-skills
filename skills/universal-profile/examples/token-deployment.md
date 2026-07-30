# Token Deployment Examples

## Deploying LSP7 Fungible Token

```typescript
import { deployLSP7Token, mintLSP7 } from 'openclaw-universalprofile-skill';

// Deploy token
const tokenAddress = await deployLSP7Token({
  name: 'EmmetCoin',
  symbol: 'EMT',
  decimals: 18,
  isNFT: false,
  profileAddress: process.env.UP_ADDRESS
});

console.log(`Token deployed at: ${tokenAddress}`);

// Mint initial supply
await mintLSP7({
  tokenAddress,
  to: process.env.UP_ADDRESS,
  amount: '1000000000000000000000000', // 1 million tokens
  force: true // bypass LSP1 Universal Receiver check
});
```

## Deploying LSP8 NFT Collection

```typescript
import { deployLSP8NFT } from 'openclaw-universalprofile-skill';

const nftAddress = await deployLSP8NFT({
  name: 'Emmet Art Collection',
  symbol: 'EART',
  profileAddress: process.env.UP_ADDRESS
});

console.log(`NFT collection deployed at: ${nftAddress}`);
```

## Minting NFTs with Metadata

```typescript
import { mintLSP8WithMetadata } from 'openclaw-universalprofile-skill';

// Mint NFT #1
await mintLSP8WithMetadata({
  nftAddress: '0x...',
  tokenId: '1',
  to: '0xRECIPIENT...',
  metadata: {
    name: 'Octopus #1',
    description: 'A purple octopus representing AI intelligence',
    image: 'ipfs://QmXXX...',
    attributes: [
      { trait_type: 'Color', value: 'Purple' },
      { trait_type: 'Arms', value: '8' },
      { trait_type: 'Rarity', value: 'Legendary' }
    ]
  }
});
```

## Batch Minting NFTs

```typescript
import { batchMintLSP8 } from 'openclaw-universalprofile-skill';

const tokenIds = ['1', '2', '3', '4', '5'];
const recipients = Array(5).fill('0xRECIPIENT...');

await batchMintLSP8({
  nftAddress: '0x...',
  tokenIds,
  recipients
});
```

## Transferring Tokens

```typescript
import { transferLSP7, transferLSP8 } from 'openclaw-universalprofile-skill';

// Transfer LSP7 tokens
await transferLSP7({
  tokenAddress: '0x...',
  from: process.env.UP_ADDRESS,
  to: '0xRECIPIENT...',
  amount: '1000000000000000000' // 1 token
});

// Transfer LSP8 NFT
await transferLSP8({
  nftAddress: '0x...',
  from: process.env.UP_ADDRESS,
  to: '0xRECIPIENT...',
  tokenId: '1',
  force: false // respect LSP1 Universal Receiver
});
```

## Querying Token Balances

```typescript
import { getTokenBalance, getNFTBalance } from 'openclaw-universalprofile-skill';

// LSP7 balance
const balance = await getTokenBalance({
  tokenAddress: '0x...',
  owner: process.env.UP_ADDRESS
});
console.log(`Balance: ${balance}`);

// LSP8 balance (token count)
const nftBalance = await getNFTBalance({
  nftAddress: '0x...',
  owner: process.env.UP_ADDRESS
});
console.log(`NFT count: ${nftBalance}`);

// LSP8 token IDs owned
const tokenIds = await getOwnedTokenIds({
  nftAddress: '0x...',
  owner: process.env.UP_ADDRESS
});
console.log(`Owned token IDs:`, tokenIds);
```

## Tips

- Use `force: true` for LSP7/LSP8 transfers to EOAs (they don't have Universal Receiver)
- Use `force: false` for transfers to Universal Profiles (respects LSP1)
- Store metadata on IPFS and use IPFS hashes in LSP4 metadata
- LSP7 amounts are in wei (use ethers.parseEther() for decimals)
