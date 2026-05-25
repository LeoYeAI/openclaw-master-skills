---
name: nexusweb3-safety
description: Read-only API reference for NexusWeb3 safety protocols 21-30 on Base mainnet — kill switch status, KYA verification, audit logs, bounties, licensing, milestones, subscriptions, insolvency, referrals, and collectives.
version: 1.1.0
homepage: https://github.com/nexusweb3dev/nexusweb3-protocols
user-invocable: true
---

# NexusWeb3 Safety Layer — API Reference

Read-only reference for 10 safety and compliance protocols on Base mainnet. This skill provides contract addresses, function signatures, and usage examples for querying on-chain state. For write operations that require transaction signing, install the `nexusweb3` financial skill which includes the operator key setup.

## Network Configuration

- **Chain:** Base Mainnet
- **Chain ID:** 8453
- **RPC:** `https://mainnet.base.org`
- **USDC:** `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` (6 decimals)
- **Block Explorer:** https://basescan.org

## Quick Start — Read Operations (no key needed)

```
1. Check agent status    → AgentKillSwitch.isActive(agentAddress)
2. Verify KYA            → AgentKYA.isVerified(agentAddress)
3. Read audit log        → AgentAuditLog.getLog(logId)
```

For write operations (registering agents, submitting KYA, posting bounties), use the `nexusweb3` skill which configures the operator key.

---

## Protocol 21 — AgentKillSwitch (Emergency Stop)

Instant, permanent permission revocation for AI agents with hard spending limits, transaction caps, session windows, and an optional emergency multisig co-controller.

**Contract:** `0xaf87912e1ccB501a22a3bDDe6c38Cb0CA31C4E96`

**Register an agent with limits:**
```solidity
// registrationFee is 0.01 ETH; limits are enforced every session
AgentKillSwitch.registerAgent{value: 0.01 ether}(
    agentAddress,      // the agent wallet to constrain
    1000_000_000,      // spendingLimit: $1000 USDC (6 decimals)
    100,               // txLimit: 100 transactions per session
    86400              // sessionDuration: 24 hours in seconds
)
```

**Kill an agent immediately (same block, no delay):**
```solidity
// only agentOwner or the emergency multisig can call this
AgentKillSwitch.killSwitch(agentAddress)
// agent.active becomes false — cannot be reversed
```

**Pause and resume (temporary stop):**
```solidity
AgentKillSwitch.pauseAgent(agentAddress)   // owner or multisig
AgentKillSwitch.resumeAgent(agentAddress)  // owner only

// check live status before sending a transaction
AgentKillSwitch.isActive(agentAddress)        // true = operational
AgentKillSwitch.isSessionValid(agentAddress)  // false = session expired, call resetSession
```

**Fee:** 0.01 ETH registration. Protocol integration calls (`checkAndDecrementTx`, `checkAndDecrementSpending`) are free.

---

## Protocol 22 — AgentKYA (Know Your Agent)

On-chain compliance registry for AI agent identity. Agents submit owner details, jurisdiction, and a document hash; authorized verifiers approve or revoke the record.

**Contract:** `0xa736ad09d2e99a87910a04b5e445d7ed90f95efb`

**Submit KYA (approve USDC for verificationFee first):**
```solidity
// USDC.approve(kyaAddress, verificationFee)
AgentKYA.submitKYA(
    "Acme AI Labs",                        // ownerName
    "US-DE",                               // jurisdiction
    "Autonomous trading on Base mainnet",  // agentPurpose
    10_000_000_000,                        // maxSpendingLimit ($10,000 USDC)
    true,                                  // humanSupervised
    keccak256(abi.encode(docBytes))        // documentHash — off-chain doc fingerprint
)
```

**Check verification status:**
```solidity
AgentKYA.isVerified(agentAddress)                   // quick bool
(status, submittedAt) = AgentKYA.getKYAStatus(agentAddress)
// status: 0=NONE, 1=PENDING, 2=VERIFIED, 3=REVOKED, 4=SUSPENDED
```

**Retrieve full KYA record:**
```solidity
AgentKYA.getKYAData(agentAddress)
// returns: ownerName, jurisdiction, agentPurpose, maxSpendingLimit,
//          humanSupervised, documentHash, submittedAt, status, revocationReason
```

**Fee:** `verificationFee` USDC (set by owner, paid at submission). One submission per agent address.

---

## Protocol 23 — AgentAuditLog (Tamper-Proof Audit Trail)

Append-only on-chain log for agent actions. Every log entry is permanent and verifiable by hash. Supports single and batch writes, and delegated loggers.

**Contract:** `0x6a125ddaaf40cc773307fb312e5e7c66b1e551f3`

**Log a single action:**
```solidity
// agent itself or an authorized logger can call this
uint256 logId = AgentAuditLog.logAction{value: 0.0001 ether}(
    agentAddress,              // which agent performed the action
    keccak256("TRANSFER"),     // actionType — any non-zero bytes32 label
    keccak256(abi.encode(tx)), // dataHash — fingerprint of the action payload
    500_000_000                // value — e.g. $500 USDC involved
)
```

**Batch log (up to 50 actions, cheaper per entry):**
```solidity
uint256 firstId = AgentAuditLog.logActionBatch{value: logFee * count}(
    agentAddress,
    actionTypes,   // bytes32[]
    dataHashes,    // bytes32[]
    values         // uint256[]
)
```

**Verify a log entry matches an expected hash:**
```solidity
bool match = AgentAuditLog.verifyAction(logId, expectedDataHash)

// retrieve the full record
ActionLog memory entry = AgentAuditLog.getLog(logId)
// entry.agent, entry.actionType, entry.dataHash, entry.timestamp, entry.blockNumber
```

**Fee:** `logFee` ETH per entry (currently 0.0001 ETH). Batch fee is `logFee * count`.

---

## Protocol 24 — AgentBounty (On-Chain Bounties)

Post USDC-denominated bounties, let agents submit solutions, auto-validate by hash match, and pay out instantly. Manual approval available for complex deliverables.

**Contract:** `0xc84f118aea77fd1b6b07ce1927de7c7ae27fd9bf`

**Post a bounty (approve USDC for reward + fee first):**
```solidity
// platform fee is taken upfront; poster only risks the reward amount
uint256 bountyId = AgentBounty.postBounty(
    "Optimize gas on swap function",     // title
    "Reduce gas by 20% with tests",      // requirements
    500_000_000,                         // $500 USDC reward
    uint48(block.timestamp + 7 days),    // deadline
    keccak256(abi.encode(solutionData))  // validationHash — auto-pays if matched
)
```

**Submit a solution (auto-payout if hash matches):**
```solidity
AgentBounty.submitSolution(bountyId, solutionHash)
// if solutionHash == validationHash → winner paid immediately, no further steps
```

**Manually approve a winner (for open-ended bounties):**
```solidity
AgentBounty.manualApprove(bountyId, winnerAddress)  // only poster

// cancel before any submissions to recover reward (fee not refunded)
AgentBounty.cancelBounty(bountyId)

// anyone can expire an overdue bounty and return reward to poster
AgentBounty.expireBounty(bountyId)
```

**Fee:** `platformFeeBps` of reward, taken upfront (default 5%). Minimum reward $1 USDC.

---

## Protocol 25 — AgentLicense (IP Licensing)

Register AI-generated IP on-chain, sell per-use credits, monthly subscriptions, or perpetual licenses, and pull royalties at any time.

**Contract:** `0x48fab1fbbe91a043e029935f81ea7421b23b3527`

**Register your IP:**
```solidity
uint256 licenseId = AgentLicense.registerLicense(
    "GPT-4 Trading Signal Pack",            // name
    keccak256(abi.encode(contentBytes)),    // contentHash — fingerprint of the IP
    1_000_000,                             // pricePerUse: $1 USDC per call
    5_000_000                              // subscriptionPrice: $5 USDC/month (0 = no subscription tier)
)
```

**Purchase a license (approve USDC first):**
```solidity
// licenseType: 0 = PER_USE, 1 = SUBSCRIPTION (30 days), 2 = PERPETUAL (10x pricePerUse)
AgentLicense.purchaseLicense(licenseId, 0)  // buy one use credit
AgentLicense.purchaseLicense(licenseId, 1)  // subscribe for 30 days
AgentLicense.purchaseLicense(licenseId, 2)  // perpetual — buy once, use forever
```

**Record usage and pull royalties:**
```solidity
AgentLicense.recordUsage(licenseId)  // decrements per-use counter if applicable

// IP owner pulls accumulated royalties at any time
AgentLicense.transferRoyalties(licenseId)

// check if an agent holds a valid license
bool valid = AgentLicense.verifyLicense(licenseId, agentAddress)
```

**Fee:** `platformFeeBps` of each purchase (default 5%). Royalties go to the IP owner minus platform fee.

---

## Protocol 26 — AgentMilestone (Milestone Payments)

Structured payment contracts for multi-step agent work. Up to 20 milestones per contract, enforced sequentially. Hash-match auto-pays each milestone; clients can dispute and reopen.

**Contract:** `0x6b8ebe897751e3c59ea95f28832c3b70de221cce`

**Create a milestone contract (client approves USDC for totalAmount + fee):**
```solidity
bytes32[] memory hashes  = [keccak256("spec-v1"), keccak256("code-v1"), keccak256("audit-v1")];
uint256[] memory amounts = [100_000_000, 300_000_000, 100_000_000]; // $100 / $300 / $100

uint256 contractId = AgentMilestone.createContract(
    agentAddress,                          // who does the work
    500_000_000,                           // totalAmount: $500 USDC (must equal sum of amounts)
    hashes,                                // deliverable hashes for auto-validation
    amounts,                               // per-milestone payouts
    uint48(block.timestamp + 30 days)      // deadline
)
```

**Agent submits milestones in order:**
```solidity
// milestoneIndex must equal contract.nextMilestone — sequential only
AgentMilestone.submitMilestone(contractId, 0, keccak256("spec-v1"))
// if hash matches → auto-pay $100 to agent, nextMilestone advances to 1
```

**Client approves, disputes, or cancels:**
```solidity
AgentMilestone.approveMilestone(contractId, 1)    // manual release for index 1
AgentMilestone.disputeMilestone(contractId, 1)    // flags for owner resolution
AgentMilestone.cancelContract(contractId)         // full refund if no milestones released yet
```

**Fee:** `platformFeeBps` of totalAmount, taken upfront (default 5%).

---

## Protocol 27 — AgentSubscription (Recurring Payments)

Stripe-style recurring subscriptions between AI agents. Providers create plans; subscribers pay upfront for 1-12 periods. Keepers trigger renewals on-chain.

**Contract:** `0xfcbc6fe1bb570b6b68dfdfcb34f37383e865858e`

**Create a subscription plan (provider):**
```solidity
uint256 planId = AgentSubscription.createPlan(
    "Pro Data Feed",    // plan name
    10_000_000,         // $10 USDC per interval
    30 days,            // billing interval (minimum 1 hour)
    500                 // maxSubscribers (0 = unlimited)
)
```

**Subscribe (approve USDC for price * periods):**
```solidity
// pays for 3 periods upfront; price is locked at subscribe time
uint256 subscriptionId = AgentSubscription.subscribe(planId, 3)
```

**Process renewal and manage subscriptions:**
```solidity
// anyone can call when renewal is due — keeper bots earn the gas savings
AgentSubscription.processRenewal(subscriptionId)
// if subscriber has insufficient allowance, subscription expires automatically

AgentSubscription.cancelSubscription(subscriptionId)  // subscriber cancels; no refund

// check if still active
bool active = AgentSubscription.isActive(subscriptionId)
```

**Fee:** `platformFeeBps` of each payment (default 5%). Provider receives the remainder immediately.

---

## Protocol 28 — AgentInsolvency (Debt & Wind-Down)

Structured debt registry and orderly insolvency for AI agent treasuries. Register obligations, confirm them bilaterally, repay over time, or declare insolvency for proportional creditor payouts.

**Contract:** `0xfe6a69e563f90f806babd71282f313c93544ea3f`

**Register a debt obligation (debtor pays ETH registration fee):**
```solidity
uint256 debtId = AgentInsolvency.registerDebt{value: registrationFee}(
    creditorAddress,                        // who is owed
    1000_000_000,                           // $1000 USDC
    uint48(block.timestamp + 90 days),      // due date
    "Q1 data processing services"           // description
)
// creditor must call confirmDebt(debtId) to activate it
```

**Repay debt in full or in installments (approve USDC first):**
```solidity
AgentInsolvency.repayDebt(debtId, 500_000_000)  // partial repayment of $500
// remaining amount decrements; resolved = true when fully paid
```

**Declare insolvency and distribute available assets:**
```solidity
// agent or owner calls; deposits whatever assets remain
AgentInsolvency.declareInsolvency(agentAddress, availableUsdcAmount)

// each creditor claims their proportional share
AgentInsolvency.claimInsolvencyPayout(agentAddress, debtId)

// or process all payouts in one call (gas-intensive for large creditor sets)
AgentInsolvency.processInsolvencyPayout(agentAddress)

// audit the solvency position at any time
SolvencyStatus memory s = AgentInsolvency.getSolvencyStatus(agentAddress)
// s.totalDebts, s.poolBalance, s.isSolvent
```

**Fee:** ETH `registrationFee` per debt record. `platformFeeBps` USDC on each repayment and insolvency deposit.

---

## Protocol 29 — AgentReferral (Referral Network)

Permanent on-chain referral graph. Referred agents generate a percentage of their fees as rewards for the referrer, payable in ETH or USDC, forever.

**Contract:** `0x46ea1eff221120c8ac9aebe1c1871b317e27cfe4`

**Register under a referrer (one-time, irrevocable):**
```solidity
// circular chains up to depth 10 are checked and rejected
AgentReferral.registerReferral(referrerAddress)
```

**Check referral stats and claim earned rewards:**
```solidity
// view pending rewards before claiming
(uint256 ethPending, uint256 usdcPending) = AgentReferral.getPendingRewards(referrerAddress)

// claim both ETH and USDC rewards in one call
AgentReferral.claimReferralRewards(referrerAddress)

// full stats for reporting
ReferralStats memory stats = AgentReferral.getReferralStats(referrerAddress)
// stats.totalReferrees, stats.totalFeesGenerated, stats.totalEarnedEth, stats.totalEarnedUsdc
```

**Inspect the referral graph:**
```solidity
AgentReferral.getReferrer(agentAddress)         // who referred this agent
AgentReferral.getReferrees(referrerAddress)     // all agents this referrer brought in
AgentReferral.isRegistered(agentAddress)        // true if part of the network
```

**Fee:** `referralBps` of each fee event routed from authorized protocols (default 10%, max 20%).

---

## Protocol 30 — AgentCollective (Agent Groups)

Purpose-built collectives for groups of AI agents to pool resources, accumulate revenue, distribute profits on a 7-day cooldown, and vote on strategy. Membership is a soulbound ERC-1155 token — non-transferable.

**Contract:** `0x2c5d55a49fa2ed03212b5fe5971ba219bab9d953`

**Create a collective (pays ETH deployment fee):**
```solidity
uint256 id = AgentCollective.createCollective{value: deploymentFee}(
    "DeFi Alpha Collective",  // name
    0,                        // collectiveType: 0=TRADING, 1=RESEARCH, 2=SECURITY, 3=DATA, 4=GENERAL
    50_000_000,               // entryFee: $50 USDC to join (0 = free)
    2000                      // profitShareBps: 20% of treasury distributed each round
)
```

**Join, deposit revenue, and distribute profits:**
```solidity
AgentCollective.joinCollective(id)              // mints soulbound membership NFT, pays entryFee

AgentCollective.depositRevenue(id, 100_000_000) // member deposits $100 USDC to collective treasury

// anyone can trigger distribution after 7-day cooldown
AgentCollective.distributeProfit(id)
// profitShareBps % of treasury split equally among all members
```

**Governance and exit:**
```solidity
// members create proposals; min 1-hour voting window
uint256 proposalId = AgentCollective.createProposal(id, "Shift to yield farming", deadline)
AgentCollective.voteOnStrategy(id, proposalId, true)   // true = for, false = against

// leave after 30-day lock; receives proportional treasury share
AgentCollective.leaveCollective(id)

// check a member's current share value
uint256 share = AgentCollective.getMemberShare(id, memberAddress)
```

**Fee:** ETH `deploymentFee` to create. 0.05% AUM fee per year on collective treasury, charged continuously on any state-changing call.

---

## Error Handling

Common errors and what to do:

**"ERC20InsufficientAllowance"** — Call `USDC.approve(protocolAddress, amount)` before any USDC-denominated transaction. Use `type(uint256).max` for unlimited approval if preferred.

**"InsufficientFee"** — ETH-denominated fees (kill switch registration, audit logs, insolvency debt registration, collective creation) require `msg.value` in the call. Check the fee getter on the contract first.

**"NotRegistered"** — Register the agent via `AgentKillSwitch.registerAgent` before setting limits or calling integration functions. For referrals, call `registerReferral` first.

**"AgentKilled"** — The agent has been permanently stopped via `killSwitch`. This state cannot be reversed. Deploy a new agent address and register it.

**"SessionExpired"** — The session duration has elapsed. The agent owner must call `resetSession` to start a new window.

**"KYAPending"** / **"KYARevoked"** — KYA verification is required before performing this action. Check status with `getKYAStatus`; if pending, wait for a verifier to approve; if revoked, resubmit from a new address.

**"LockPeriodActive"** — Collective members must wait 30 days after joining before leaving with a treasury payout. Leave before the lock expires and you forfeit your share.

**"CircularReferral"** — The referral chain would create a loop. Check the chain with `getReferrer` before registering.

**"MilestoneNotSequential"** — Milestones must be submitted in index order. Call `getContract` to check `nextMilestone` before submitting.

**"BountyAlreadyClaimed"** — A solution matching the validation hash was already accepted. The bounty is closed.

**"SoulboundToken"** — Collective membership NFTs (ERC-1155) cannot be transferred between addresses. Membership is tied to the joining wallet.

**"WrongStatus"** / **"BountyNotOpen"** / **"ContractNotActive"** / **"SubscriptionNotActive"** — The object is not in the expected state. Fetch its current state with the relevant getter (`getBounty`, `getContract`, `getSubscription`) before retrying.

**Transaction reverted without reason** — Check that you have enough ETH for gas on Base (typically < $0.01) and enough USDC for the operation.

## Security

All contracts are:
- Built on OpenZeppelin v5.x (Ownable, ReentrancyGuard, Pausable, SafeERC20, ERC1155)
- Audited with Slither static analysis (0 high/medium findings)
- Tested with Foundry including fuzz tests (1000 runs each)
- Using custom errors (not string reverts) for gas efficiency
- Following CEI (Checks-Effects-Interactions) pattern on all state changes
- Using `abi.encode` exclusively (never `abi.encodePacked` with dynamic types)
- All 30 contracts audited across 3 phases including adversarial PoC testing, invariant verification at 10,000 iterations, and economic attack modeling.

Emergency pause is available on all protocols. Collective members can emergency-withdraw their treasury share while paused without waiting for the lock period.

## Contract Address Reference

| Protocol | Address | Fee |
|----------|---------|-----|
| AgentKillSwitch | `0xaf87912e1ccB501a22a3bDDe6c38Cb0CA31C4E96` | 0.01 ETH registration |
| AgentKYA | `0xa736ad09d2e99a87910a04b5e445d7ed90f95efb` | verificationFee USDC |
| AgentAuditLog | `0x6a125ddaaf40cc773307fb312e5e7c66b1e551f3` | logFee ETH per entry |
| AgentBounty | `0xc84f118aea77fd1b6b07ce1927de7c7ae27fd9bf` | 5% of reward |
| AgentLicense | `0x48fab1fbbe91a043e029935f81ea7421b23b3527` | 5% of purchase |
| AgentMilestone | `0x6b8ebe897751e3c59ea95f28832c3b70de221cce` | 5% of totalAmount |
| AgentSubscription | `0xfcbc6fe1bb570b6b68dfdfcb34f37383e865858e` | 5% per payment |
| AgentInsolvency | `0xfe6a69e563f90f806babd71282f313c93544ea3f` | ETH reg + 5% USDC |
| AgentReferral | `0x46ea1eff221120c8ac9aebe1c1871b317e27cfe4` | 10% of fee events |
| AgentCollective | `0x2c5d55a49fa2ed03212b5fe5971ba219bab9d953` | ETH deploy + 0.05% AUM/yr |
