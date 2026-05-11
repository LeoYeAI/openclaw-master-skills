# Super Apps — Callback Lifecycle, App Credit & Jailing

## What Is a Super App

A Super App is a smart contract registered with the Superfluid Host that
receives **agreement callbacks** — `beforeAgreement*` and `afterAgreement*`
hooks invoked when an agreement operation (create/update/delete a flow or
distribution) involves the Super App as sender or receiver. This enables
reactive on-chain logic: a Super App can automatically relay, split, or
transform streams in response to incoming flows.

## Callback Lifecycle

When an agreement operation targets a Super App, the Host orchestrates this
sequence:

1. User calls `Host.callAgreement(agreement, callData, userData)`
2. Host creates a context (`ctx`) encoding the original `msg.sender`
3. Host delegates to the agreement (e.g. CFA)
4. Agreement detects the receiver (or sender) is a registered Super App
5. Agreement calls **`Host.appCallbackPush`** — sets up app credit, increments
   the callback nesting level, and validates composite-app whitelisting
6. Agreement calls **`Host.callAppBeforeCallback`** — a `staticcall` to the
   app's `beforeAgreementCreated/Updated/Terminated` hook (read-only; the app
   can inspect state but not modify it). Returns `cbdata` passed to the after hook.
7. Agreement executes its **core logic** (creates/updates/deletes the flow)
8. Agreement calls **`Host.callAppAfterCallback`** — a regular call to the
   app's `afterAgreementCreated/Updated/Terminated` hook. This is where the
   Super App opens outgoing streams, distributes tokens, or performs other
   state-changing logic using app credit.
9. Agreement calls **`Host.appCallbackPop`** — finalizes credit accounting
   (accumulates `appCreditUsedDelta`)
10. Host validates: context was not corrupted, app credit not exceeded

**Important notes:**

- `CFASuperAppBase` sets `BEFORE_AGREEMENT_CREATED_NOOP`, so the before hook
  is skipped on flow creation. The simplified API exposes only after-hooks via
  `onFlowCreated`, `onFlowUpdated`, `onFlowDeleted`.
- Termination (delete) callbacks **must not revert**. If `afterAgreementTerminated`
  reverts, the Super App is immediately **jailed** (see below).

## App Credit

### Zero-Balance Design Goal

App credit enables **zero-balance Super Apps** — contracts that relay incoming
streams to outgoing streams without holding any tokens upfront. Without app
credit, a Super App would need pre-funded tokens to cover the buffer deposit
required when opening an outgoing stream.

### Lending Rules

Three rules govern how much credit the CFA grants:

- **Rule A — Transactional allowance**: App credit is a temporary allowance
  extended within a single transaction. The Super App can "borrow" deposit from
  the incoming flow's sender to open outgoing streams. After the transaction,
  the borrowed amount is settled as `owedDeposit` on the sender's account.

- **Rule CFA-1 — 1:1 forwarding guarantee**: When a Super App receives one
  incoming CFA stream, the CFA allocates a matching buffer amount for one
  outgoing stream. A zero-balance 1:1 relay (receive at rate R, send at rate R)
  **always works** — no tokens required.

- **Rule CFA-2 — Minimum buffer supplementation**: For fan-out patterns
  (1 incoming → N outgoing), additional minimum buffer is borrowed per extra
  flow to cover rounding gaps. The zero-balance guarantee **no longer holds** —
  the Super App needs to hold some tokens to cover the additional deposits
  beyond the 1:1 credit.

### App Credit Is CFA-Only

**GDA does not have an app credit mechanism.** A Super App that receives CFA
inflows and distributes via GDA pool cannot borrow the deposit buffer — it
must fund the GDA buffer separately (e.g., via ERC-20 `transferFrom` from
the user or pre-funding the contract). See `smart-contract-patterns.md` § A
for the workaround pattern.

### Deposit Impact on Sender

The deposits for the Super App's outgoing streams are tracked as **owed deposit**
(`owedDeposit`) on the original sender's account. The sender's total locked
capital roughly doubles: their own deposit for the stream to the Super App,
plus the owed deposit backing the Super App's outgoing streams.

Fan-out patterns amplify this — each outgoing stream adds its own deposit to
the sender's owed amount, so total locked capital can exceed 2×.

This connects to the balance formula:
`availableBalance = settledBalance + dynamics - max(0, deposit - owedDeposit)`.
Higher locked capital means the sender reaches **critical** status (negative
available balance, eligible for liquidation) sooner than they would streaming
to a regular account.

## App Levels & Composition

Super Apps have a **level** set during registration via the `configWord` bitmask:

- **FINAL** (level 1, `APP_LEVEL_FINAL = 1 << 1`): Cannot interact with other
  Super Apps downstream. This is the default — `CFASuperAppBase` always uses it.
- **SECOND** (level 2, `APP_LEVEL_SECOND = 1 << 0`): Can call whitelisted
  FINAL-level Super Apps. The source app must whitelist each target via
  `Host.allowCompositeApp(targetApp)`.

`MAX_APP_CALLBACK_LEVEL` is **1**, meaning at most two Super Apps in a chain
(SECOND → FINAL). This prevents unbounded callback recursion.

If a SECOND-level app calls a non-whitelisted Super App, the transaction
reverts with `APP_RULE` code 30 (`COMPOSITE_APP_IS_NOT_WHITELISTED`).

## Jailing

### Causes — APP_RULE Reason Codes

A Super App is **jailed** when it violates any protocol rule. The `APP_RULE`
error and `Jail` event carry a reason code (from `SuperAppDefinitions.sol`):

- 10 `NO_REVERT_ON_TERMINATION_CALLBACK` — Delete/termination callback reverted
- 11 `NO_CRITICAL_SENDER_ACCOUNT` — Callback made the flow sender critical
- 12 `NO_CRITICAL_RECEIVER_ACCOUNT` — Callback made the flow receiver critical
- 20 `CTX_IS_READONLY` — State change during a `staticcall` (before) callback
- 21 `CTX_IS_NOT_CLEAN` — Context was not properly returned after callback
- 22 `CTX_IS_MALFORMATED` — Context bytes were corrupted or fabricated
- 30 `COMPOSITE_APP_IS_NOT_WHITELISTED` — Called downstream Super App without `allowCompositeApp`
- 31 `COMPOSITE_APP_IS_JAILED` — Called a downstream Super App that is jailed
- 40 `MAX_APP_LEVEL_REACHED` — Callback nesting exceeded `MAX_APP_CALLBACK_LEVEL`

### Consequences

Once jailed, a Super App's callbacks are **permanently bypassed**. Existing
flows continue streaming tokens, but the app's logic no longer executes on
create/update/delete events. If the app had outgoing flows backed by app
credit and the income stream is deleted, the app's balance drains until its
outgoing flows are liquidated.

A jailed app cannot be un-jailed — it is effectively defunct as a Super App.
Query `Host.isAppJailed(app)` or `Host.getAppManifest(app)` to check status.

### Practical Rules for Avoiding Jailing

- **Never revert in delete/termination callbacks.** This is the most common
  cause of jailing. Use try/catch for any external calls in `onFlowDeleted`.
- **Don't corrupt the Superfluid context.** Callbacks receive `ctx` and must
  return `newCtx`. When performing multiple agreement operations inside a
  callback, chain the context through each call using the `WithCtx` library
  variants (e.g., `token.createFlowWithCtx`, `token.deleteFlowWithCtx`). Each
  call returns a new `newCtx` — pass it to the next operation. Never manually
  construct or modify `ctx` bytes.
- **Don't exceed granted app credit.** Opening too many outgoing streams
  relative to the credit available will fail.
- **Whitelist composite apps.** If your SECOND-level app calls a downstream
  Super App, call `Host.allowCompositeApp(target)` first.

## See Also

- Production patterns (GDA pools, CFA→GDA splitting, custom tokens, proxies, automation) → `smart-contract-patterns.md`
