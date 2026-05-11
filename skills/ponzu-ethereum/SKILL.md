---
name: ponzu-launchpad
description: Deploy and interact with Ponzu token launchpad — presales, DEX swaps, and LP farming on Ethereum
version: 1.0.1
metadata:
  openclaw:
    emoji: "🍋"
    homepage: https://ponzu.app
    requires:
      env:
        - PONZU_PRIVATE_KEY
        - PONZU_NETWORK
        - PONZU_RPC_URL
    primaryEnv: PONZU_PRIVATE_KEY
---

```

⠀⠀⢻⣽⣿⣿⣿⣿⢿⣿⣿⣿⣶⡀⠀⢰⣻⣿⣿⣿⣿⡿⣿⣿⣿⣦⠀⣿⣿⣿⣿⡇⠀⠀⢻⣿⣿⣻⠿⠈⠿⠿⠿⠿⢿⣿⣿⣿⡏⢿⣭⣿⣿⠃⠀⠀⢿⣿⣿⣾⡟
⠀⠀ ⣿⣿⣿⣿⠀⠀⠈⣿⣿⣿⣿⢸⣿⣿⣿⣿⠿⠿⢶⣿⣿⣿⣿⠀⡉⣿⣿⢿⣻⡀⠀⠈⣿⣿⣹⡇⠀⠀⠀⠀⣸⣿⣿⢹⢳⠀⣿⣿⣿⣿⠀⠀⠀⣿⣿⡿⣿⡇
⠀ ⢀⣿⣿⣿⣏⠀⠀⠀⣻⣿⡿⠿⠸⢸⣿⣿⡗⠀⠀⠀⣿⡟⣿⡿⠀⣇⣿⣿⣾⣿⡟⠀⡄⣿⣿⣿⡏⠀⠀⠀⠀⣷⢿⣿⣿⡏⠀⡿⣿⣿⣿⠀⠀⠀⣟⣿⣿⣏⡇
⠀⠀⢸⣾⣿⣿⡏⠀⠀⠀⣾⣿⡿⣿⠈⣻⣿⣿⠇⠀⠀⠀⣸⣷⣿⣷⠀⣿⣿⣿⣿⣿⣿⣷⡇⣿⣿⣇⡇⠀⠀⠀⢸⣿⣿⣿⢫⠀⠀⣹⣿⣿⣿⠀⠀⠀⣿⣿⡿⣿⡇
⠀⠀⢸⣿⣿⣿⡇⠀⠀⠀⣿⣿⣿⣿⠀⣿⣿⣿⡇⠀⠀⠀⣿⣿⣿⡇⠀⣿⣿⣽⣿⣻⣿⣿⣿⣷⣿⣿⡇⠀⠀⠀⣿⣿⣿⣿⡏⠀⠀⣻⣿⣽⣿⠀⠀⠀⣿⣿⣿⣟⡇
⠀⠀⢸⣗⣿⣿⡇⠀⠀⠀⣿⣿⣿⣿⢨⣿⣿⣿⡇⠀⠀⠀⣿⣽⣿⡿⠀⣾⡇⣿⣻⢿⣯⣿⣿⣿⣿⣿⠃⠀⠀⢀⣿⣿⣿⣷⠀⠀⠀⣾⣿⣿⣿⠀⠀⠀⣿⣿⣏⣿⡇
⠀⠀⢸⣷⡿⣷⣵⣶⣾⣿⣿⣿⡿⠋⢸⣿⣿⣿⡇⠀⠀⢸⢿⣿⣶⣇⠀⣿⣿⣿⣿⡎⣿⣿⣿⣿⣿⣿⠀⠀⠀⣷⣧⣿⣿⡗⠀⠀⠀⣽⣿⣿⣿⠀⠀⠀⣿⣿⢿⣿⡇
⠀⠀⢸⣿⣿⣿⡏⠉⠉⠀⠀⠀⠀⠀⢠⣿⣿⣿⡇⠀⠀⢸⣿⣿⣿⣿⢀⣿⣿⣿⣾⣿⡟⡟⣿⣿⣿⣿⠀⠀⢀⣾⣿⣿⣿⠀⠀⠀⠀⠹⣿⡏⣿⠀⠀⠀⡭⣿⢾⣷⡇
⠀⠀⢸⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⡇⠀⠀⢸⣿⣿⣿⣿⢰⣿⣿⣇⣿⠹⣿⣿⢹⣿⣿⠏⠀⠀⣾⣿⣿⣿⡟⠀⠀⠀⠀⢸⣿⣷⣿⠀⠀⠀⣣⣿⣿⣷⡇
⠀⠀⢨⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⢸⣿⣿⣿⣧⣀⣀⣠⣿⣿⣧⣯⢸⣿⣿⣿⣼⠀⠹⣿⣿⣿⣺⣿⠀⠀⣿⣿⣿⣿⠀⠀⠀⠀⠀⢸⣿⣻⣿⣄⣀⣀⣿⣿⣾⣿⠃
⠀⠀⢸⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠘⣿⣿⣿⣿⣿⣟⣿⣿⣿⣿⣾⢸⣿⣿⣿⣿⠀⠀⢹⣿⣿⣿⣿⠀⢰⣿⣿⣿⣿⣶⣶⣦⣶⡄⣿⣿⣿⣭⣿⣭⣟⣿⣿⣿⣻⠀
⠀⠀⠚⠛⠛⠛⠁⠀⠀⠀⠀⠀⠀⠀⠀⠀⠙⠚⠿⠿⠿⠿⠛⠛⠉⠀⠉⠓⠛⠛⠃⠀⠀⠈⠉⠛⠛⠛⠀⠛⠉⠉⠉⠉⠙⠉⠉⠉⠁⠀⠈⠛⠿⠿⠿⠿⠟⠛⠉⠀⠀

                     https://ponzu.app/SKILL.md
```

# Ponzu Launchpad

Ponzu is a permissionless ERC-20 token launchpad on Ethereum with diamond-hand vesting.
One transaction deploys a complete DeFi stack — presale, launcher, DEX, and LP yield farming — all atomically from a single factory call.

No admin keys. No upgrade proxies. No external APIs. No migration steps.

Every token launched through Ponzu follows the same lifecycle:

1. **Presale** — users buy tokens at a rising price curve; each position is a transferable NFT
2. **Launch** — when sold out, anyone triggers the DEX pool creation (permissionless)
3. **Vesting** — tokens vest linearly over 10 days; early claims route unvested tokens to the reward pool
4. **Farming** — LPs stake to earn trading fees + redistributed unvested tokens

---

## Security & Privacy

All logic runs locally. No data is sent to Ponzu servers.

- Signed transactions are broadcast to your configured Ethereum RPC endpoint (`PONZU_RPC_URL`). Find public RPCs at [chainlist.org/chain/1](https://chainlist.org/chain/1) for mainnet or [chainlist.org/chain/11155111](https://chainlist.org/chain/11155111) for Sepolia
- No telemetry, analytics, or external API calls
- `PONZU_PRIVATE_KEY` is used locally by viem's `privateKeyToAccount()` to sign transactions — it is never transmitted
- **Use a dedicated wallet** with only the funds needed. Never use your main wallet.
- **Test on Sepolia first** (`PONZU_NETWORK=sepolia`) before using mainnet
- **Omit `PONZU_PRIVATE_KEY`** for read-only access (query contract state without signing)
- Smart contracts are immutable (no proxy, no admin keys, no upgrade path)
- All contract addresses are listed in [Contract Addresses](#contract-addresses) below

---

## Quick Start

```bash
npm install @ponzu_app/sdk viem
```

```typescript
import { createWalletClient, createPublicClient, http } from 'viem'
import { mainnet } from 'viem/chains'
import { privateKeyToAccount } from 'viem/accounts'
import { deploy, getAddresses } from '@ponzu_app/sdk'

// Use a dedicated wallet — never your main wallet
const account = privateKeyToAccount(process.env.PONZU_PRIVATE_KEY as `0x${string}`)
const wallet  = createWalletClient({ account, chain: mainnet, transport: http() })
const client  = createPublicClient({ chain: mainnet, transport: http() })
```

<details>
<summary>Using raw viem (no SDK)</summary>

```bash
npm install viem
```

```typescript
import {
  createWalletClient,
  createPublicClient,
  http,
  parseEther,
  encodeAbiParameters,
  decodeAbiParameters,
  keccak256,
  toBytes,
  parseAbi,
  type Address,
} from 'viem'
import { mainnet } from 'viem/chains'
import { privateKeyToAccount } from 'viem/accounts'

// Use a dedicated wallet — never your main wallet
const account = privateKeyToAccount(process.env.PONZU_PRIVATE_KEY as `0x${string}`)
const wallet = createWalletClient({ account, chain: mainnet, transport: http() })
const publicClient = createPublicClient({ chain: mainnet, transport: http() })
```

</details>

---

## Deploy a Token

Deploying a token creates a complete system in one transaction: presale contract, DEX pair, farm, and NFTs. The whole system goes live atomically.

**Cost:** 0.005 ETH creation fee + optional dev buy amount.

### With SDK

```typescript
import { deploy } from '@ponzu_app/sdk'
import { parseEther } from 'viem'

const result = await deploy(
  {
    owner:          account.address,
    tokenName:      'My Token',
    tokenSymbol:    'MYTKN',
    metadata:       'ipfs://Qm...',   // JSON: { image, description, socials }
    imageURI:       'ipfs://Qm...',   // token logo
    targetEthRaise: parseEther('5'),  // optional — defaults to 3 ETH minimum
  },
  wallet,
  client,
  'mainnet',
)

const tokenAddress   = result.addresses.token     // ERC-20
const presaleAddress = result.addresses.presale   // presale contract
const farmAddress    = result.addresses.farm      // LP staking farm
// + project, operator, launcher, distributor, ponzuBottle, liquidityCard

// pairAddress is created at triggerLaunch() — query after launch:
// const { ponzuSwap, weth } = getAddresses('mainnet')
// const pairAddress = await client.readContract({
//   address: ponzuSwap, abi: FACTORY_ABI,
//   functionName: 'getPair', args: [tokenAddress, weth],
// })
```

The SDK handles pricing math, ABI encoding, transaction signing, and event decoding automatically.

### Without SDK

<details>
<summary>Expand for raw viem approach</summary>

```typescript
const PONZU_RECIPE = '0x1155484c5fE614538d83c444f9a6dB662E6a7153'
const WETH         = '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'

const RECIPE_ABI = parseAbi([
  'function craftPonzu((address owner, address keyContract, uint256 initialBuyAmount, uint256 vestingDuration, bytes32 pricingStrategyTemplate, bytes pricingStrategyData, bytes feeStrategyData, string tokenName, string tokenSymbol, string metadata, string imageURI) params) payable',
])
```

**Pricing (Linear Strategy):**

```typescript
// Token supply: 1,000,000 total
//   690,000 (69%) sold in presale → must raise ≥ minEthRaise
//   310,000 (31%) seeded into DEX liquidity
//
// From LinearPricingStrategy._calculateCostForTokens:
//   totalCost = (startPrice + endPrice) × 690_000 / 2
//   With startPrice = endPrice / 10:
//   totalCost = endPrice × 11 × 690_000 / 20
//
// Solving for endPrice:
//   endPrice = targetRaise × 20 / (11 × 690_000)
//
// Mainnet minimum (3 ETH):  endPrice ≈ 7,905 Gwei
// Testnet minimum (0.1 ETH): endPrice ≈ 263.5 Gwei

// Mainnet — minimum viable pricing (raises exactly ~3 ETH):
const targetRaise   = parseEther('3')
const endPriceWei   = (targetRaise * 20n) / (11n * 690_000n)  // ≈ 7,905 Gwei
const startPriceWei = endPriceWei / 10n

const pricingStrategyTemplate = keccak256(toBytes('LinearPricingStrategy'))
const pricingStrategyData = encodeAbiParameters(
  [{ type: 'uint256' }, { type: 'uint256' }],
  [startPriceWei, endPriceWei],
)
```

**Deploy:**

```typescript
const devBuyEth = parseEther('0.1')  // optional dev buy (0n to skip)

const params = {
  owner:                   account.address,
  keyContract:             '0x0000000000000000000000000000000000000000',
  initialBuyAmount:        devBuyEth,
  vestingDuration:         864000n,               // 10 days
  pricingStrategyTemplate,
  pricingStrategyData,
  feeStrategyData:         '0x',
  tokenName:               'My Token',
  tokenSymbol:             'MYTKN',
  metadata:                'ipfs://Qm...',
  imageURI:                'ipfs://Qm...',
}

const value = parseEther('0.005') + devBuyEth

const hash = await wallet.writeContract({
  address: PONZU_RECIPE,
  abi: RECIPE_ABI,
  functionName: 'craftPonzu',
  args: [params],
  value,
})

const receipt = await publicClient.waitForTransactionReceipt({ hash })
```

**Parse Deployed Addresses:**

```typescript
const ponzuCraftedTopic = keccak256(toBytes(
  'PonzuCrafted(address,string,(address,address,address,address,address,address,address,address,address))'
))

const log = receipt.logs.find(l => l.topics[0] === ponzuCraftedTopic)!
const [, , addresses] = decodeAbiParameters(
  [
    { type: 'string' },
    {
      type: 'tuple',
      components: [
        { name: 'project',       type: 'address' },
        { name: 'operator',      type: 'address' },
        { name: 'token',         type: 'address' },
        { name: 'presale',       type: 'address' },
        { name: 'launcher',      type: 'address' },
        { name: 'distributor',   type: 'address' },
        { name: 'farm',          type: 'address' },
        { name: 'ponzuBottle',   type: 'address' },
        { name: 'liquidityCard', type: 'address' },
      ],
    },
  ],
  log.data,
)

const tokenAddress   = addresses.token    as Address
const presaleAddress = addresses.presale  as Address
const farmAddress    = addresses.farm     as Address
```

</details>

### Metadata

The contract accepts any URI string — IPFS, Arweave, or `https://`. Choose whichever fits your setup.

**Option A — IPFS via Pinata (recommended):**
```typescript
// POST image file to https://api.pinata.cloud/pinning/pinFileToIPFS
// POST metadata JSON to https://api.pinata.cloud/pinning/pinJSONToIPFS
// Headers: { Authorization: 'Bearer YOUR_PINATA_JWT' }

// Metadata schema:
// { image: 'ipfs://<imageHash>', description: string,
//   socials: { twitter?: string, discord?: string, website?: string } }

const imageURI = 'ipfs://Qm...'   // pinFileToIPFS response CID
const metadata = 'ipfs://Qm...'   // pinJSONToIPFS response CID
```

**Option B — Arweave:**
```typescript
const imageURI = 'https://arweave.net/YOUR_TX_ID'
const metadata = 'https://arweave.net/YOUR_METADATA_TX_ID'
```

**Option C — Any https:// URL:**
```typescript
const imageURI = 'https://your-server.com/token-image.png'
const metadata = 'https://your-server.com/token-metadata.json'
```

---

## Presale

After deploy, the presale is open immediately. Users buy presale tokens with ETH; the presale closes automatically when all 690,000 tokens are sold.

```typescript
const PRESALE_ABI = parseAbi([
  'function presale(uint256 minTokenAmount, address platformReferrer, address orderReferrer) payable',
  'function refund(uint256 tokenAmount)',
  'function claim()',
  'function claimETH(uint256 tokenId)',
  'function triggerLaunch()',
  'function tokensAvailable() view returns (uint256)',
  'function launched() view returns (bool)',
  'function launchTime() view returns (uint256)',
  'function purchases(uint256 tokenId) view returns (uint256)',
  'function ethContributions(uint256 tokenId) view returns (uint256)',
])
```

### Buy Tokens

```typescript
// 4% fee on ETH cost:
//   1% platform | 1% protocol | 1% creator
//   0.5% platform referrer | 0.5% order referrer
// Pass zero address if you have no referrer.
const ZERO = '0x0000000000000000000000000000000000000000'

const ethToSpend   = parseEther('0.1')
const minTokensOut = 0n    // slippage guard: minimum tokens to receive

const hash = await wallet.writeContract({
  address: presaleAddress,
  abi: PRESALE_ABI,
  functionName: 'presale',
  args: [minTokensOut, ZERO, ZERO],   // (minTokenAmount, platformReferrer, orderReferrer)
  value: ethToSpend,
})
```

### Read Presale State

```typescript
// Tokens remaining (returns 0 when sold out)
const tokensAvailable = await publicClient.readContract({
  address: presaleAddress,
  abi: PRESALE_ABI,
  functionName: 'tokensAvailable',
})

// Whether DEX has launched
const launched = await publicClient.readContract({
  address: presaleAddress,
  abi: PRESALE_ABI,
  functionName: 'launched',
})

// Unix timestamp of launch (0 = not yet launched)
const launchTime = await publicClient.readContract({
  address: presaleAddress,
  abi: PRESALE_ABI,
  functionName: 'launchTime',
})

// User position — requires PonzuBottle NFT tokenId
const tokensPurchased = await publicClient.readContract({
  address: presaleAddress,
  abi: PRESALE_ABI,
  functionName: 'purchases',
  args: [bottleTokenId],
})

const ethContributed = await publicClient.readContract({
  address: presaleAddress,
  abi: PRESALE_ABI,
  functionName: 'ethContributions',
  args: [bottleTokenId],
})
```

### Refund

Available before launch. Returns 90% of contributed ETH; the 10% token penalty stays in the pool and benefits loyal holders via pro-rata bonus.

```typescript
const tokensToRefund = parseUnits('1000', 18)

await wallet.writeContract({
  address: presaleAddress,
  abi: PRESALE_ABI,
  functionName: 'refund',
  args: [tokensToRefund],
})
```

### Trigger Launch

Anyone can call this once the presale is sold out. It creates the DEX liquidity pool and starts vesting.

```typescript
// Only succeeds when tokensAvailable == 0 and launched == false
await wallet.writeContract({
  address: presaleAddress,
  abi: PRESALE_ABI,
  functionName: 'triggerLaunch',
  args: [],
})
```

### Claim Vested Tokens

One-time claim per PonzuBottle NFT. Tokens vest linearly over `vestingDuration` from launch. Early claims forfeit remaining unvested portion to the Distributor for reward recycling.

```typescript
// Convenience wrapper (uses caller's bottle)
await wallet.writeContract({
  address: presaleAddress,
  abi: PRESALE_ABI,
  functionName: 'claim',
  args: [],
})
```

### Claim ETH Rewards

Repeatable. Collects accumulated ETH rewards distributed from swap fees and farming activity.

```typescript
await wallet.writeContract({
  address: presaleAddress,
  abi: PRESALE_ABI,
  functionName: 'claimETH',
  args: [bottleTokenId],
})
```

---

## Swap Tokens

Ponzu runs its own DEX (PonzuSwap — a Uniswap V2 fork). Swap fees decay from 20% at launch down to a flat 1% over the first hour, then stay at 1%.

All paths route through WETH. The pair for any token is `token / WETH`.

```typescript
const PONZU_SWAP_FACTORY = '0x1DCA548D67938E6162f0756985cC3e539Aae30C2'
const PONZU_ROUTER       = '0xb90BD8EA30dE3b1DF07Eb574374229F4213F649e'

const FACTORY_ABI = parseAbi([
  'function getPair(address tokenA, address tokenB) view returns (address pair)',
])

const PAIR_ABI = parseAbi([
  'function getReserves() view returns (uint112 reserve0, uint112 reserve1, uint32 blockTimestampLast)',
  'function approve(address spender, uint256 amount) returns (bool)',
])

const ROUTER_ABI = parseAbi([
  'function swapExactETHForTokens(uint256 amountOutMin, address[] path, address to, uint256 deadline) payable returns (uint256[] amounts)',
  'function swapExactTokensForETH(uint256 amountIn, uint256 amountOutMin, address[] path, address to, uint256 deadline) returns (uint256[] amounts)',
])

const ERC20_ABI = parseAbi([
  'function approve(address spender, uint256 amount) returns (bool)',
])
```

### Find the Pair

The pair is created at `triggerLaunch()`. Query after launch:

```typescript
const pairAddress = await publicClient.readContract({
  address: PONZU_SWAP_FACTORY,
  abi: FACTORY_ABI,
  functionName: 'getPair',
  args: [tokenAddress, WETH],
})
```

### Get Price Quote

```typescript
const [reserve0, reserve1] = await publicClient.readContract({
  address: pairAddress,
  abi: PAIR_ABI,
  functionName: 'getReserves',
})

// Reserve order matches sorted address order (lower address = reserve0)
```

### Buy Tokens (ETH → Token)

```typescript
const ethIn    = parseEther('0.1')
const minOut   = 0n                          // set a real value for slippage protection
const deadline = BigInt(Math.floor(Date.now() / 1000) + 300)  // 5 min

await wallet.writeContract({
  address: PONZU_ROUTER,
  abi: ROUTER_ABI,
  functionName: 'swapExactETHForTokens',
  args: [minOut, [WETH, tokenAddress], account.address, deadline],
  value: ethIn,
})
```

### Sell Tokens (Token → ETH)

Approve the router first, then swap.

```typescript
// Step 1: approve
await wallet.writeContract({
  address: tokenAddress,
  abi: ERC20_ABI,
  functionName: 'approve',
  args: [PONZU_ROUTER, tokenAmountIn],
})

// Step 2: swap
const minEthOut = 0n   // set a real value for slippage protection

await wallet.writeContract({
  address: PONZU_ROUTER,
  abi: ROUTER_ABI,
  functionName: 'swapExactTokensForETH',
  args: [tokenAmountIn, minEthOut, [tokenAddress, WETH], account.address, deadline],
})
```

---

## Farming (LP Staking)

LP staking is available after launch. Each staking position is represented by a LiquidityCard NFT. Rewards include the project token and WETH from swap fees.

**Early exit penalty:** Unstaking within 7 days forfeits 0–100% of LP (linear). After 7 days, no penalty.

```typescript
const ZAP_ETH = '0x33a1FB28125e3a396743Ac40B43f56499a13575D'

const ZAP_ABI = parseAbi([
  'function calculateExpectedLP(address tokenB, uint256 ethAmount) view returns (uint256)',
  'function zapETHToLP(address tokenB, uint256 minLPTokens) payable returns (uint256 lpAmount)',
])

const FARM_ABI = parseAbi([
  'function stake(uint256 amount)',
  'function stakeNewCard(uint256 amount)',
  'function unstake(uint256 cardId)',
  'function claim(uint256 cardId)',
  'function claimETH(uint256 cardId)',
])
```

### Step 1 — Get LP Tokens via ZapEth

ZapEth converts ETH into LP tokens in a single transaction (no need to acquire tokens separately).

```typescript
// Preview expected LP output
const expectedLP = await publicClient.readContract({
  address: ZAP_ETH,
  abi: ZAP_ABI,
  functionName: 'calculateExpectedLP',
  args: [tokenAddress, ethAmount],
})

// Execute: converts ETH → LP tokens, sends LP to caller
const slippage = 50n                                              // 0.5%
const minLP    = expectedLP * (10000n - slippage) / 10000n

await wallet.writeContract({
  address: ZAP_ETH,
  abi: ZAP_ABI,
  functionName: 'zapETHToLP',
  args: [tokenAddress, minLP],
  value: ethAmount,
})
```

### Step 2 — Stake LP

`farmAddress` comes from the `craftPonzu` receipt (see Parse Deployed Addresses). Approve LP to the Farm contract, then stake. Each stake mints a LiquidityCard NFT tracking the position.

```typescript
// LP token address = the pair contract itself (pairAddress from getPair after launch)
await wallet.writeContract({
  address: pairAddress,
  abi: PAIR_ABI,
  functionName: 'approve',
  args: [farmAddress, lpAmount],
})

// Stake to your active card (or mint first card automatically)
await wallet.writeContract({
  address: farmAddress,
  abi: FARM_ABI,
  functionName: 'stake',
  args: [lpAmount],
})

// OR always mint a new card (for multiple independent positions)
await wallet.writeContract({
  address: farmAddress,
  abi: FARM_ABI,
  functionName: 'stakeNewCard',
  args: [lpAmount],
})
```

### Unstake

Full withdrawal. Burns the LiquidityCard NFT. May apply an early exit penalty.

```typescript
await wallet.writeContract({
  address: farmAddress,
  abi: FARM_ABI,
  functionName: 'unstake',
  args: [cardId],
})
```

### Claim Rewards

```typescript
// Primary token reward — one-time per card
await wallet.writeContract({
  address: farmAddress,
  abi: FARM_ABI,
  functionName: 'claim',
  args: [cardId],
})

// WETH rewards — repeatable
await wallet.writeContract({
  address: farmAddress,
  abi: FARM_ABI,
  functionName: 'claimETH',
  args: [cardId],
})
```

---

## Token Distribution

| Pool | Allocation |
|------|-----------|
| Presale | 690,000 (69%) |
| DEX Liquidity | 310,000 (31%) |

**Presale fee (on ETH cost):** 4% total — 1% platform, 1% protocol, 1% creator, 0.5% platform referrer, 0.5% order referrer.

**Swap fee:** 20% → 1% linear decay over the first hour post-launch, then flat 1%.

**Farm early exit:** Up to 100% LP forfeited if unstaking within 7 days. Half of any penalty boosts remaining stakers.

**Refund penalty:** 10% of refunded tokens stays in the pool, increasing pro-rata allocation for loyal holders.

---

## Contract Addresses

### Ethereum Mainnet (1)

| Contract | Address |
|----------|---------|
| PonzuRecipe | `0x1155484c5fE614538d83c444f9a6dB662E6a7153` |
| PonzuSwap (DEX factory) | `0x1DCA548D67938E6162f0756985cC3e539Aae30C2` |
| PonzuRouter | `0xb90BD8EA30dE3b1DF07Eb574374229F4213F649e` |
| ZapEth | `0x33a1FB28125e3a396743Ac40B43f56499a13575D` |
| WETH | `0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2` |
| LinearPricingStrategy | `0x308Ce1EC9655D952A18FC9f57cA2fA06A697F0b8` |
| EthRewarder | `0x66CF6F4297d812bB9B6647f23357b47a91Da0530` |
| PonzuVault | `0x4D9fEC67fA5Eed8402A1b45dA9CcA6AA5CC1B791` |

Min raise: **3 ETH** — minimum `endPrice ≈ 8 Gwei` (`parseUnits('8', 9)`)

### Sepolia Testnet (11155111)

| Contract | Address |
|----------|---------|
| PonzuRecipe | `0x219d82fc450C3124a64a1ef7aD6C092F866307fF` |
| PonzuSwap (DEX factory) | `0x27355C17C80d341e71F9ae44578a3eC61eB4fFA2` |
| PonzuRouter | `0x7665074482247cAc541BE364c1811851ca102d02` |
| ZapEth | `0x7dF7543e3bF2E5da11Fc6eae3bC6cf88578AfbC6` |
| WETH | `0xeDf5E9f5f1E4255a2d68eE6B076444D0d18B77bc` |
| LinearPricingStrategy | `0xA68062d113360A8d5AA81505bBf21D6480A4BDB4` |
| EthRewarder | `0xF625D51418ec56b99E9b7Ef54Db182642651ebdD` |
| PonzuVault | `0x888888886544E7dDBab4fFeD4e58E48033c62074` |

Min raise: **0.1 ETH** — minimum `endPrice ≈ 264 Mwei` (`parseUnits('264', 6)`)

Per-project contracts (token, presale, farm, etc.) are unique per deployment — addresses returned by `craftPonzu` and emitted in events.

---

## MCP Server (optional)

For agents that support MCP (Claude Desktop, Cursor, Claude Code), you can also use the Ponzu MCP server for tool-based access instead of SDK code:

```json
{
  "mcpServers": {
    "ponzu": {
      "command": "npx",
      "args": ["-y", "@ponzu_app/mcp"],
      "env": {
        "PONZU_NETWORK": "mainnet"
      }
    }
  }
}
```

Add `PONZU_PRIVATE_KEY` for signing capability. See [@ponzu_app/mcp on npm](https://www.npmjs.com/package/@ponzu_app/mcp) for details.
