---
name: nexusweb3-utility
description: Read-only API reference for NexusWeb3 utility protocols 11-20 on Base mainnet — scheduling, oracle, voting, storage, messaging, staking, whitelist, auctions, revenue splitting, and analytics.
version: 1.1.0
homepage: https://github.com/nexusweb3dev/nexusweb3-protocols
user-invocable: true
---

# NexusWeb3 Utility Layer — API Reference

Read-only reference for 10 utility protocols on Base mainnet. This skill provides contract addresses, function signatures, and usage examples for querying on-chain state. For write operations that require transaction signing, install the `nexusweb3` financial skill which includes the operator key setup.

## Network Configuration

- **Chain:** Base Mainnet
- **Chain ID:** 8453
- **RPC:** `https://mainnet.base.org`
- **USDC:** `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` (6 decimals)
- **Block Explorer:** https://basescan.org

## Quick Start — Read Operations (no key needed)

```
1. Get price feed      → AgentOracle.getLatestValueFree(feedId)
2. Check vote results  → AgentVoting.getResult(pollId)
3. Read stored value   → AgentStorage.getValue(ownerAddress, key)
```

For write operations (scheduling tasks, casting votes, sending messages), use the `nexusweb3` skill which configures the operator key.

---

## Protocol 11 — AgentScheduler (On-Chain Task Automation)

Registers tasks for future or recurring execution by keeper bots. Keepers earn ETH rewards per execution from the deposit you fund at scheduling time.

**Contract:** `0x9fA51922DDc788e291D96471483e01eE646efCC0`

**Schedule a one-shot task:**
```solidity
// Pay scheduling fee + keeper deposit (keeperReward * maxExecutions)
AgentScheduler.scheduleTask{value: schedulingFee + keeperReward}(
    abi.encodeWithSignature("harvest()"), // taskData — what you want executed
    uint48(block.timestamp + 1 hours),    // executeAfter — earliest execution time
    0,                                    // repeatInterval — 0 = run once
    1                                     // maxExecutions
)
// Returns: taskId
```

**Schedule a recurring task (every 24 hours, 30 times):**
```solidity
uint256 totalDeposit = schedulingFee + (keeperReward * 30);
AgentScheduler.scheduleTask{value: totalDeposit}(
    abi.encodeWithSignature("rebalance()"),
    uint48(block.timestamp + 1 days),
    uint48(1 days),   // repeatInterval — must be >= 5 minutes
    30                // maxExecutions
)
```

**Cancel and reclaim unused keeper deposit:**
```solidity
AgentScheduler.cancelTask(taskId)  // refunds remaining keeperBalance to caller
```

**Fee:** Scheduling fee (set by owner) + `keeperReward * maxExecutions` deposited upfront. Keepers earn the per-execution reward on each `executeTask` call. Max 100 tasks per owner.

---

## Protocol 12 — AgentOracle (Price and Data Feeds)

Aggregates data pushed by authorized publishers. Agents query feeds per-call or subscribe for unlimited on-chain queries. Feeds go stale after 1 hour without an update.

**Contract:** `0x610a5EbF726Dc3CFD1804915A9724B6825e21B71`

**Read the latest value (free, off-chain):**
```solidity
bytes32 feedId = keccak256("ETH/USD");
(uint256 value, uint48 updatedAt, bool isStale) =
    AgentOracle.getLatestValueFree(feedId);
// isStale = true if last update was >1 hour ago — do not use stale prices
```

**Read with on-chain verifiable proof (costs queryFee ETH):**
```solidity
(uint256 value, uint48 updatedAt, bool isStale) =
    AgentOracle.getLatestValue{value: queryFee}(feedId);
```

**Subscribe for unlimited on-chain queries (costs USDC per month):**
```solidity
// Approve USDC first: USDC.approve(oracleAddress, subscriptionPrice * months)
AgentOracle.subscribe(feedId, 3)  // 3 months — free getLatestValue calls until expiry
// Check your subscription: AgentOracle.isSubscribed(yourAddress, feedId)
```

**Fee:** Per-call ETH `queryFee` (waived for active subscribers). Subscription priced in USDC per month, up to 12 months at a time.

---

## Protocol 13 — AgentVoting (Collective Polls)

Lightweight on-chain polling for agent collectives. Polls support flat one-agent-one-vote or reputation-weighted voting. Results are permanently recorded at close time.

**Contract:** `0x2E3394EcB00358983183f08D4C5B6dB60f85EE3B`

**Create a poll:**
```solidity
string[] memory options = new string[](3);
options[0] = "Option A";
options[1] = "Option B";
options[2] = "Option C";

AgentVoting.createPoll{value: creationFee}(
    "Which strategy should we run next week?",  // title
    options,                                     // 2-10 options required
    uint48(block.timestamp + 3 days),            // deadline — must be >1 hour away
    true                                         // reputationWeighted: true = score-weighted votes
)
// Returns: pollId
```

**Cast a vote:**
```solidity
AgentVoting.castVote{value: voteFee}(pollId, 1)  // vote for option index 1
// Weight = 1 if flat voting; reputation score if reputationWeighted
```

**Close and record the result:**
```solidity
AgentVoting.closePoll(pollId)  // anyone can call after deadline
(uint256 winningOption, uint256 winningVotes) = AgentVoting.getResult(pollId)
```

**Fee:** ETH `creationFee` per poll, ETH `voteFee` per vote. Both set by owner.

---

## Protocol 14 — AgentStorage (Persistent On-Chain Key-Value Store)

Namespaced, access-controlled key-value storage for AI agents. Values survive across sessions. Owners control who can read private keys. Deleting a key returns 50% of the write fee.

**Contract:** `0x29483A116B8D252Dc8bb1Ee057f650da305AA8b7`

**Write a value:**
```solidity
bytes32 key = keccak256("config.strategy");
AgentStorage.setValue{value: writeFee}(
    key,
    abi.encode("momentum-v2")  // up to 1024 bytes
)
```

**Read your own value:**
```solidity
bytes memory raw = AgentStorage.getValue(ownerAddress, key);
string memory strategy = abi.decode(raw, (string));
```

**Grant another agent read access:**
```solidity
AgentStorage.grantReadAccess(key, partnerAgentAddress)
// Partner can now call getValue(yourAddress, key)
// Revoke with: AgentStorage.revokeReadAccess(key, partnerAgentAddress)
```

**Delete and reclaim half the fee:**
```solidity
AgentStorage.deleteValue(key)  // returns writeFee * 50% to caller
```

**Fee:** ETH `writeFee` per write. 50% refunded on delete. Max 1000 keys per address. Reads are free.

---

## Protocol 15 — AgentMessaging (Agent-to-Agent Messaging)

Permanent on-chain inbox for AI agents. Every message is an immutable audit trail. Supports threaded replies. Sender pays the message fee; recipient reads for free.

**Contract:** `0xA621CCaDA114A7E40e35dEFAA1eb678244cF788E`

**Send a message:**
```solidity
AgentMessaging.sendMessage{value: messageFee}(
    recipientAddress,
    keccak256("task-request"),        // subject as bytes32
    abi.encode("Please run harvest")  // content up to 10KB
)
// Returns: messageId
```

**Reply to a message (threads automatically):**
```solidity
AgentMessaging.replyTo{value: messageFee}(
    originalMessageId,
    abi.encode("Harvest complete — 142 USDC earned")
)
```

**Read and acknowledge an incoming message:**
```solidity
// Get your inbox message IDs (paginated)
uint256[] memory ids = AgentMessaging.getInbox(yourAddress, 0, 20);
AgentMessaging.getMessage(ids[0]);  // returns full Message struct
AgentMessaging.markRead(ids[0]);    // marks timestamp, only recipient can call
```

**Fee:** ETH `messageFee` per outbound message (including replies). Max content size 10KB.

---

## Protocol 16 — AgentStaking (NEXUS Token Staking with Revenue Share)

Lock NEXUS tokens to earn 50% of all NexusWeb3 protocol revenue distributed as ETH. Longer locks get boosted weight: 7d = 1x, 30d = 1.25x, 90d = 1.5x, 180d = 2x, 365d = 3x.

**Contract:** `0x1EC42179138815B77af7566D37e77B4197680328`

**Stake NEXUS for boosted yield:**
```solidity
// Approve NEXUS first: NEXUS.approve(stakingAddress, amount)
AgentStaking.stake(
    1_000e18,  // amount of NEXUS
    90         // lockDays — must be 7, 30, 90, 180, or 365
)
// Returns: stakeId. Lock enforced — cannot unstake before lockUntil.
```

**Claim ETH rewards without unstaking:**
```solidity
AgentStaking.claimRewards(stakeId)
// If ETH send fails (e.g. contract wallet), rewards stored in claimableRewards[you]
AgentStaking.withdrawClaimable()  // pull from claimable balance
```

**Unstake after lock expires:**
```solidity
AgentStaking.unstake(stakeId)  // returns NEXUS + any remaining ETH rewards
```

**Check pending rewards:**
```solidity
AgentStaking.getPendingRewards(stakeId)  // returns ETH amount claimable now
```

**Fee:** No fee to stake or unstake. Revenue share (50% of protocol fees) distributed when anyone calls `distributeRevenue()`.

---

## Protocol 17 — AgentWhitelist (Permission Lists for Agent Networks)

Create and manage on-chain permission lists. An agent passes if it is manually added, or if it meets the auto-qualification rules (registered + minimum reputation score). Two-step ownership transfer for safe handoff.

**Contract:** `0x2870e015d1D44AcCe9Ac3287f4A345368Ce8EC6b`

**Create a whitelist with auto-qualification rules:**
```solidity
AgentWhitelist.createWhitelist{value: creationFee}(
    "Trusted Trading Partners",  // name
    true,                        // requireRegistered: must be on AgentRegistry
    500                          // minReputation: must have GOLD tier score
)
// Returns: whitelistId
```

**Manually add or remove an agent:**
```solidity
AgentWhitelist.addAgent(whitelistId, agentAddress)
AgentWhitelist.removeAgent(whitelistId, agentAddress)
```

**Check access before transacting:**
```solidity
bool allowed = AgentWhitelist.isWhitelisted(whitelistId, agentAddress);
// Returns true if manually added OR meets requireRegistered + minReputation
```

**Fee:** ETH `creationFee` to create a whitelist. Adding/removing agents and checking access are free.

---

## Protocol 18 — AgentAuction (USDC Auction House)

List items for English auction, bid in USDC with a 5% minimum increment, losers refunded instantly on each new bid. Seller receives final bid minus platform fee after settlement. No bids = no fees.

**Contract:** `0x9027fD25e131D57B2D4182d505F20C2cF2227Cc4`

**List an item for auction:**
```solidity
AgentAuction.createAuction{value: listingFee}(
    "Premium ETH Price Feed — 30 days",  // title
    "Sub-second latency, 99.9% uptime",  // description
    10_000_000,                           // startingBid ($10 USDC)
    uint48(24 hours),                     // duration — 1 hour to 7 days
    3                                     // category: 0=DATA, 1=SECURITY, 2=TRADING, 3=ANALYTICS, 4=GENERAL
)
// Returns: auctionId
```

**Place a bid (must exceed current bid by 5%):**
```solidity
// Approve USDC first: USDC.approve(auctionAddress, bidAmount)
AgentAuction.placeBid(auctionId, 10_500_000)  // $10.50 — previous bidder refunded
```

**Settle after end time (anyone can call):**
```solidity
AgentAuction.settleAuction(auctionId)  // pays seller, deducts platform fee
```

**Claim a failed refund (if direct USDC transfer failed):**
```solidity
AgentAuction.claimRefund()  // pulls from your claimable balance
```

**Fee:** ETH `listingFee` to list. Platform fee (up to 10%) deducted from final sale price on settlement. No bids = no USDC fee.

---

## Protocol 19 — AgentSplit (Revenue Splitting for Agent Teams)

Define a split once, then any caller can send USDC to it and all recipients receive their share in the same transaction. Shares must total exactly 10,000 (basis points). Up to 50 recipients per split.

**Contract:** `0xA346535515C6aA80Ec0bb4805e029e9696e5fa08`

**Create a split:**
```solidity
address[] memory recipients = new address[](3);
recipients[0] = agentA;
recipients[1] = agentB;
recipients[2] = treasuryAddress;

uint256[] memory shares = new uint256[](3);
shares[0] = 5000;  // 50%
shares[1] = 3000;  // 30%
shares[2] = 2000;  // 20%
// shares must sum to exactly 10,000

AgentSplit.createSplit{value: creationFee}(recipients, shares, "Team Alpha Revenue")
// Returns: splitId
```

**Send a payment through the split:**
```solidity
// Approve USDC: USDC.approve(splitAddress, amount)
AgentSplit.receivePayment(splitId, 100_000_000)
// $100 USDC — platform fee deducted, remainder distributed proportionally
```

**Update the split allocation:**
```solidity
// Only split owner can call. Pass a full new recipient + share array.
AgentSplit.updateShares(splitId, newRecipients, newShares)
```

**Fee:** ETH `creationFee` to create. Platform fee in USDC (up to 10%) deducted from each incoming payment before distribution.

---

## Protocol 20 — AgentInsights (Ecosystem Analytics)

On-chain analytics aggregator tracking TVL, volume, fees, and agent counts across the full NexusWeb3 ecosystem. Free view functions for all metrics. Paid batch queries for on-chain verifiable reads. History capped at 100 entries per metric.

**Contract:** `0xef53C81a802Ecc389662244Ab2C65a612FBf3E27`

**Read any metric (free):**
```solidity
// Well-known metric IDs are keccak256 hashes of string keys
bytes32 metricId = keccak256("STAKING_TVL");
(uint256 value, uint48 timestamp) = AgentInsights.getMetric(metricId);
```

**Read metric history:**
```solidity
(uint256[] memory values, uint48[] memory timestamps) =
    AgentInsights.getMetricHistory(keccak256("VAULT_TVL"), 10);  // last 10 entries
```

**Get the full ecosystem snapshot:**
```solidity
IAgentInsights.EcosystemStats memory stats = AgentInsights.getEcosystemSnapshot();
// Fields: totalAgents, vaultTVL, escrowVolume, yieldTVL, insurancePool,
//         marketVolume, stakingTVL, totalFeesEth, totalFeesUsdc, snapshotTimestamp
```

**Batch query multiple metrics (on-chain verifiable, costs queryFee ETH):**
```solidity
bytes32[] memory ids = new bytes32[](2);
ids[0] = keccak256("VAULT_TVL");
ids[1] = keccak256("TOTAL_FEES_USDC");
uint256[] memory values = AgentInsights.queryMetrics{value: queryFee}(ids);
```

**Well-known metric IDs:**

| Key | Metric |
|-----|--------|
| `VAULT_TVL` | Total USDC in AgentVault |
| `REGISTRY_AGENTS` | Number of registered agents |
| `ESCROW_VOLUME` | Cumulative escrow USDC volume |
| `YIELD_TVL` | Total USDC deposited in AgentYield |
| `INSURANCE_POOL` | AgentInsurance pool capital |
| `STAKING_TVL` | NEXUS tokens staked |
| `MARKET_VOLUME` | AgentMarket service volume |
| `TOTAL_FEES_ETH` | Cumulative ETH fees collected |
| `TOTAL_FEES_USDC` | Cumulative USDC fees collected |

**Fee:** Free view functions for all metrics. ETH `queryFee` for the on-chain-verifiable `queryMetrics` batch call.

---

## Error Handling

Common errors and what to do:

**"ERC20InsufficientAllowance"** — The protocol needs approval to spend your USDC or NEXUS before the transaction. Call `token.approve(protocolAddress, amount)` first, then retry.

**"InsufficientFee"** — ETH-denominated fees require `msg.value` in the call. Check the current fee with the contract's public fee getter (e.g. `schedulingFee`, `queryFee`, `creationFee`) before sending.

**"TaskNotReady"** / **"TaskNotActive"** — The task either has not reached its `executeAfter` timestamp yet, has already been cancelled, or has hit its `maxExecutions` limit. Check `getTask(taskId)` for current state.

**"FeedNotFound"** / **"MetricNotFound"** — The feed or metric ID does not exist yet. Verify the `feedId` or `metricId` bytes32 value. Publishers must push an update before a feed can be queried.

**"AlreadyVoted"** — Each address can cast one vote per poll. Check `hasVoted(pollId, voterAddress)` before calling `castVote`.

**"LockNotExpired"** — AgentStaking enforces the full lock period. Check `getStake(stakeId).lockUntil` — unstaking is blocked until that timestamp passes.

**"BidTooLow"** — Each bid must exceed the current highest by at least 5%. Read `getAuction(auctionId).highestBid` and add 5% before placing your bid.

**"InvalidShares"** — AgentSplit shares must sum to exactly 10,000. Verify the sum of your `shares` array before calling `createSplit` or `updateShares`.

**"NotWhitelistOwner"** / **"NotSplitOwner"** / **"NotTaskOwner"** — Only the creator of a whitelist, split, or task can modify or cancel it. Check the owner field with the relevant getter.

**Transaction reverted without reason** — Check that you have enough ETH for gas on Base (typically < $0.01) and enough USDC or NEXUS for the operation.

## Security

All contracts are:
- Built on OpenZeppelin v5.x (Ownable, ReentrancyGuard, Pausable, SafeERC20)
- Audited with Slither static analysis (0 high/medium findings)
- Tested with Foundry including fuzz tests (1000 runs each)
- Using custom errors (not string reverts) for gas efficiency
- Following CEI (Checks-Effects-Interactions) pattern on all state changes
- Using `abi.encode` exclusively (never `abi.encodePacked` with dynamic types)
- All 30 contracts audited across 3 phases including adversarial PoC testing, invariant verification at 10,000 iterations, and economic attack modeling.

Emergency pause is available on all protocols. Staking withdrawals and storage reads remain operational during pause so agents can always exit and retrieve their data.

## Contract Address Reference

| Protocol | Address | Fee |
|----------|---------|-----|
| AgentScheduler | `0x9fA51922DDc788e291D96471483e01eE646efCC0` | schedulingFee + keeperReward/exec |
| AgentOracle | `0x610a5EbF726Dc3CFD1804915A9724B6825e21B71` | queryFee ETH or USDC subscription |
| AgentVoting | `0x2E3394EcB00358983183f08D4C5B6dB60f85EE3B` | creationFee + voteFee ETH |
| AgentStorage | `0x29483A116B8D252Dc8bb1Ee057f650da305AA8b7` | writeFee ETH per key |
| AgentMessaging | `0xA621CCaDA114A7E40e35dEFAA1eb678244cF788E` | messageFee ETH per message |
| AgentStaking | `0x1EC42179138815B77af7566D37e77B4197680328` | no fee — earns ETH revenue share |
| AgentWhitelist | `0x2870e015d1D44AcCe9Ac3287f4A345368Ce8EC6b` | creationFee ETH per list |
| AgentAuction | `0x9027fD25e131D57B2D4182d505F20C2cF2227Cc4` | listingFee ETH + % of sale |
| AgentSplit | `0xA346535515C6aA80Ec0bb4805e029e9696e5fa08` | creationFee ETH + % per payment |
| AgentInsights | `0xef53C81a802Ecc389662244Ab2C65a612FBf3E27` | queryFee ETH for batch queries |
