# Smart Contract Patterns & Production Gotchas

Practical patterns and gotchas for building Superfluid smart contracts,
distilled from production apps (Banger, SuperBoring/averageX) and reference
implementations (custom-supertokens, super-examples, staking, ad-auction).
This is a pattern reference, not a tutorial — use alongside the `.abi.yaml`
files and other guides for API details.

## A. GDA Pool Patterns

### Unit Scaling for Precision

GDA distributes flow proportionally: each member receives
`flowRate × memberUnits / totalUnits` per second (integer division). If
`flowRate / totalUnits < 1`, the per-unit rate truncates to **zero** and
the entire flow goes to the pool admin as an adjustment flow.

**Rule of thumb:** choose a scaling factor `S` that divides all unit values
so that `flowRate / (totalUnits / S) ≥ 1` always holds. Equivalently,
ensure `totalUnits ≤ flowRate` after scaling.

Example from a staking contract: users stake ERC-20 tokens and get
`stakedAmount / scalingFactor` pool units. If a user's scaled amount is
`< 1`, they get 0 units and 0 rewards. The scaling factor must satisfy:

```
S > 1.5768 trillion × (totalSupplyStaked / totalSupplyRewards)
```

to keep rounding error below 0.001% over a year.

**Production example (Banger):** GDA pools use custom metadata via
`createPoolWithCustomERC20Metadata()` and time-weighted unit allocation
(`units += (block.timestamp - lastUpdate)`) so longer participation earns
proportionally more.

Cross-ref: `GDAv1Forwarder.abi.yaml` (distributeFlow rounding notes),
`SuperfluidPool.abi.yaml`, `gda-scalability.md`.

### Buffer Funding for CFA→GDA Splitting

**GDA has no app credit rule.** Unlike CFA, where a Super App can borrow
deposit buffer via app credit (see `super-apps.md`), GDA does not extend
this mechanism. A Super App that receives CFA inflows and distributes via
GDA pool **cannot** use app credit to cover the GDA stream's buffer deposit.

The contract must fund the GDA buffer from another source:

- **ERC-20 allowance from the user** — require users to `approve()` an
  estimated amount, then `transferFrom()` inside the callback to cover the
  buffer. This is how SuperBoring (averageX) handles it — users call
  `estimateApprovalRequired()` beforehand.
- **Contract's own balance** — pre-fund the contract with Super Tokens.

This is the most common reason CFA→GDA stream-splitting contracts fail
silently or revert.

Cross-ref: `super-apps.md` (App Credit section), `CFASuperAppBase.abi.yaml`.

### Defensive Unit Operations

`decreaseMemberUnits(member, amount)` reverts with uint128 underflow if
`amount` exceeds the member's current units. Units are stored exactly (no
rounding in store/retrieve), so a matched increase/decrease always works.
However, in contracts with complex multi-step accounting (bonuses,
referrals, dynamic pricing), the computed delta might exceed actual units
due to logic edge cases.

**Defensive pattern:** wrap in try/catch when your delta calculations are
non-trivial, or use `updateMemberUnits(member, 0)` directly when removing
a member entirely:

```solidity
// Option A: try/catch for complex deltas
try pool.decreaseMemberUnits(member, computedDelta) {
    // success
} catch {
    pool.updateMemberUnits(member, 0); // fallback: set to zero
}

// Option B: direct set when removing entirely
pool.updateMemberUnits(member, 0);
```

### Pool Configuration Trade-offs

When creating a pool via `GDAv1Forwarder.createPool()`, you pass a
`PoolConfig`:

- **`transferabilityForUnitsOwner`** — whether unit holders can transfer
  their units to other addresses. Most apps set `false` to prevent gaming.
- **`distributionFromAnyAddress`** — `true` means anyone can call
  `distributeFlow` or `distribute` to the pool. `false` restricts to admin
  only. Setting `true` is permissive — consider whether arbitrary flow
  additions are a risk for your use case.

### Per-Member Isolation with Satellite Contracts

Multiple production apps deploy per-user satellite contracts as GDA pool
members to isolate concerns:

- **Banger:** SocialVault (Beacon Proxy per user) — holds user's pool
  memberships, manages claiming
- **SuperBoring/averageX:** SleepPod (Beacon Proxy per user) — staking
  isolation
- **Staking example:** ClaimContract (per-staker) — dedicated contract as
  pool member

Benefits: simplified claiming, isolated state, clean `connectPool` per
member. Beacon proxy pattern lets you upgrade all satellite contracts at
once.

Cross-ref: Section D (Proxy & Factory Patterns).

## B. Super App Callback Patterns

### Flow Splitting Anatomy

Super App callbacks must handle three cases separately:

```solidity
function onFlowCreated(ISuperToken token, address sender, bytes calldata ctx)
    internal override returns (bytes memory newCtx) {
    // CREATE: set up outgoing flows for the first time
}

function onFlowUpdated(ISuperToken token, address sender,
    int96 previousFlowRate, uint256 lastUpdated, bytes calldata ctx)
    internal override returns (bytes memory newCtx) {
    // UPDATE: adjust outgoing flows proportionally
}

function onFlowDeleted(ISuperToken token, address sender, address receiver,
    int96 previousFlowRate, uint256 lastUpdated, bytes calldata ctx)
    internal override returns (bytes memory newCtx) {
    // DELETE: clean up all outgoing flows — MUST NOT REVERT
}
```

**Net flow calculation** for determining available outflow rate:

```solidity
int96 netFlowRate = token.getNetFlowRate(address(this));
int96 outFlowRate = token.getFlowRate(address(this), receiver);
int96 inFlowRate = netFlowRate + outFlowRate; // what's coming in
```

### Context Chaining

All agreement operations inside callbacks **must** use `WithCtx` variants
and chain the context through:

```solidity
function onFlowCreated(..., bytes calldata ctx)
    internal override returns (bytes memory newCtx)
{
    newCtx = token.createFlowWithCtx(receiverA, rateA, ctx);
    newCtx = token.createFlowWithCtx(receiverB, rateB, newCtx);
    // Each call returns updated context — pass it to the next
}
```

Non-context calls (`token.createFlow()`) inside callbacks corrupt the
Superfluid context and cause jailing (APP_RULE code 21 or 22).

### Receiver Validation

Prevent callback loops and zero-address sends:

```solidity
require(newReceiver != address(0), "zero address");
require(!host.isApp(ISuperApp(newReceiver)), "no Super App receivers");
```

A Super App sending to another Super App creates recursive callbacks that
can exceed the max callback level (APP_RULE code 40) or hit gas limits.
Exception: explicitly composed apps using `APP_LEVEL_SECOND` +
`allowCompositeApp()`.

### Safe External Calls in Callbacks

If your callback calls external contracts (controllers, oracles), use
gas-limited calls so failures don't block the protocol operation:

```solidity
(bool success, ) = target.call{gas: 50_000}(data);
// Log but don't revert on failure
```

SuperBoring (averageX) uses `CallbackUtils.externalCall` for this —
controller errors don't block flow create/update/delete.

### Stream Redirection on NFT Transfer

Pattern for transferring a stream when an NFT changes hands:

```solidity
function _beforeTokenTransfer(address from, address to, uint256 tokenId)
    internal override
{
    // Delete stream to old owner, create stream to new owner
    if (from != address(0)) token.deleteFlow(address(this), from);
    if (to != address(0)) token.createFlow(to, flowRate);
}
```

Cross-ref: `super-apps.md` (full callback lifecycle, app credit, jailing),
`CFASuperAppBase.abi.yaml`, `SuperTokenV1Library.abi.yaml`.

## C. Custom SuperToken Deployment

The protocol has three operational variants (see `architecture.md`):
Wrapper (ERC-20 backed), Native Asset/SETH (ETH backed, pre-deployed by
governance on each network), and Pure (pre-minted, no underlying). For
cross-chain use cases, developers can also deploy Bridged/xERC20 Super
Tokens with rate-limited bridge minting. This section covers the types
developers deploy themselves.

### Pure SuperToken (No Underlying)

Simplest variant — no backing ERC-20, pre-minted supply:

1. Deploy `UUPSProxy` pointing to the SuperToken logic
2. Call `ISuperTokenFactory.initializeCustomSuperToken(proxy)` to register
3. Call `ISuperToken(proxy).selfMint(recipient, amount, "")` for initial supply

No `upgrade()`/`downgrade()` — tokens exist only in Super Token form.

### ERC-20 Wrapper SuperToken

Wraps an existing ERC-20 with streaming capabilities:

```solidity
ISuperToken wrapper = factory.createERC20Wrapper(
    IERC20(underlying),
    underlyingDecimals, // read from underlying contract
    Upgradability.SEMI_UPGRADABLE,
    "Super Token Name",
    "STx"
);
```

Users call `wrapper.upgrade(amount)` to wrap and `downgrade(amount)` to
unwrap. Amounts are always in 18-decimal Super Token units — the contract
handles decimal scaling internally.

### Bridged / xERC20 SuperToken

For cross-chain Super Tokens with rate-limited bridge minting:

- Rolling 24-hour rate limits per bridge (mint and burn tracked separately)
- `setLimits(bridge, mintingLimit, burningLimit)` configures per-bridge caps
- Current availability recalculated on limit changes (may reduce available)
- Rolling limit boundary: `_MAX_LIMIT = type(uint256).max / 2` to prevent
  multiplication overflow

Chain-specific interfaces:
- Optimism: implement `IOptimismMintableERC20` (`mint`/`burn`, `remoteToken`)
- Arbitrum: implement `IArbToken` (`bridgeMint`/`bridgeBurn`, `l1Address`)

**Burn allowance trick:** enforce ERC-20 approval on burns by routing
through `selfTransferFrom` before `selfBurn`:

```solidity
ISuperToken(address(this)).selfTransferFrom(user, bridge, bridge, amount);
ISuperToken(address(this)).selfBurn(bridge, amount, "");
```

### Storage Layout

`CustomSuperTokenBase` reserves storage slots 0–31. `Ownable` uses slot 32.
Custom state starts at slot 33+. **Validate slot layout in tests** to
prevent proxy upgrade collisions.

### Atomic Deployment

Always deploy and initialize in one transaction (factory pattern) to
prevent frontrunning attacks where someone else calls `initialize()` on
your proxy before you do.

Cross-ref: `SuperTokenFactory.abi.yaml`, `SuperToken.abi.yaml`.

## D. Proxy & Factory Patterns

Superfluid contracts commonly use these proxy architectures:

### Beacon Proxy

Best for multi-instance contracts (per-user vaults, per-pool wrappers).
All instances share one implementation — upgrade all at once by updating
the beacon.

Used by: Banger (SocialVault, BangerPool), SuperBoring (SleepPod),
staking (ClaimContract).

### Create2 (Deterministic Addresses)

Compute the contract address before deployment using `CREATE2`. Enables
routing tokens or permissions to an address before the contract exists.

Used by: Banger (SocialVaultFactory) — pre-compute vault address for a
user, then deploy lazily on first interaction.

### Minimal Proxy (Clones / ERC-1167)

Cheapest deployment (~45 gas overhead per call). Good for many small
instances that don't need upgradeability.

Used by: stream-gating (ExistentialNFTCloneFactory).

### UUPS (Universal Upgradeable Proxy Standard)

Single-instance upgradeability. The upgrade logic lives in the
implementation, not the proxy. Combine with Beacon for satellite contracts.

Used by: SuperBoring (SuperBoring controller, EmissionTreasury),
custom-supertokens (all variants).

## E. Automation / Public Operator Pattern

The "public operator" is a contract that acts on behalf of users based on
stored intent, triggered by off-chain keepers. This is how VestingSchedulerV3
and FlowScheduler work.

### Architecture

1. **User registers intent** — schedule parameters stored on-chain (start
   date, end date, flow rate, cliff amount, etc.)
2. **User grants permissions** — two separate grants:
   - **CFA ACL** via CFAv1Forwarder: `grantPermissions(token, operator)`
     for full control, or `updateFlowOperatorPermissions(token, operator,
     permissions, flowRateAllowance)` for granular control. (Smart
     contracts can also use `SuperTokenV1Library.setFlowPermissions()`
     internally.) This lets the operator contract create/delete flows on
     behalf of the user.
   - **ERC-20 allowance**: `superToken.approve(operator, amount)` — lets
     the contract transfer tokens (for cliffs, compensation, deposits)
3. **Keeper triggers execution** — anyone can call the permissionless
   `execute*()` function when conditions are met
4. **Contract acts via delegated calls** — uses `createFlowFrom()`,
   `updateFlowFrom()`, `deleteFlowFrom()` (via SuperTokenV1Library) to
   manage flows on behalf of the user

### Time-Gated Execution

Prevent early or late execution with a time window:

```
valid execution window = [startDate, startDate + maxDelay]
```

If `block.timestamp` falls outside this window, the execution reverts.

### Execution Delay Compensation

If a keeper triggers late (within the valid window but after the scheduled
time), the contract compensates the receiver with a lump-sum transfer:

```solidity
uint256 compensation = (block.timestamp - scheduledTime) * uint256(uint96(flowRate));
token.transferFrom(sender, receiver, compensation);
```

This ensures the receiver gets the full intended value regardless of when
the keeper executes.

### Remainder / Dust Handling

When `totalAmount % duration != 0`, the stream can't deliver the exact
total. The remainder is transferred as a lump sum at the end of the
vesting/schedule period.

### Resolver Pattern for Keepers

Off-chain keepers poll a `checker()` or similar view function:

```solidity
function checker(bytes calldata checkData)
    external view returns (bool canExec, bytes memory execPayload);
```

Returns `canExec = true` with the encoded call payload when:
- Current time is within the execution window
- Required permissions (ACL + allowance) are still valid
- The schedule hasn't already been executed

Reference implementations: `VestingSchedulerV3.abi.yaml`,
`FlowScheduler.abi.yaml`. See also `ConstantFlowAgreementV1.abi.yaml`
(ACL section) for flow permission details.

## F. Stream-Based Access Control

### Passive State Query (No Super App Needed)

If you only need to check whether someone is streaming, query Superfluid
state directly in view functions — no Super App callbacks required:

```solidity
function hasAccess(address user) public view returns (bool) {
    int96 flowRate = cfa.getFlowRate(token, user, address(this));
    return flowRate >= requiredFlowRate && flowRate != 0;
}
```

This is cheaper and simpler than building a Super App. The trade-off: you
can't react to stream lifecycle events (create/update/delete). If you need
reactive logic, use a Super App instead.

### Multiple Payment Tiers

Support multiple accepted tokens or flow rates with an array of payment
options:

```solidity
struct PaymentOption {
    ISuperToken token;
    address receiver;
    int96 requiredFlowRate;
}

PaymentOption[] public paymentOptions;

function hasAccess(address user) public view returns (bool) {
    for (uint i = 0; i < paymentOptions.length; i++) {
        PaymentOption memory opt = paymentOptions[i];
        int96 rate = cfa.getFlowRate(opt.token, user, opt.receiver);
        if (rate >= opt.requiredFlowRate && rate != 0) return true;
    }
    return false;
}
```

"Last match wins" for tiered access — iterate and upgrade tier as higher
rates are found.

### When NOT to Use a Super App

Use passive state queries when:
- You only need to gate access based on stream existence/rate
- You don't need to react to stream create/update/delete
- You want minimal gas overhead and simpler contracts

Use a Super App when:
- You need to relay, split, or transform incoming streams
- You need to execute logic atomically when a stream changes
- You need app credit for zero-balance operation

**Note:** The stream-gating pattern (ExistentialNFT) used CFA stream NFTs
for dynamic ownership, but the protocol disabled CFA stream NFT creation
due to spam. The passive state query concept remains valid — just don't
rely on stream NFTs for ownership tracking.

## See Also

- Super App fundamentals (callback lifecycle, app credit, jailing, app levels) → `super-apps.md`
- GDA scalability deep-dive (O(1) math, rounding model, PDPoolIndex) → `../deep-researches/gda-scalability.md`
