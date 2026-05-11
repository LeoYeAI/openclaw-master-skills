# MacroForwarder — Composable Batch Operations via User-Defined Macros

## What & Why

Interacting with Superfluid often requires multi-step batch operations: wrap
underlying tokens, approve a contract, create a stream, connect to a pool —
all in one atomic transaction. Building these `Host.batchCall` operation arrays
manually is verbose, error-prone, and not reusable.

**MacroForwarder** solves this by separating *what* to do from *how* to execute
it. A developer deploys a **macro contract** implementing `IUserDefinedMacro`
that encapsulates the operation-building logic. Anyone can then call
`MacroForwarder.runMacro(macro, params)` to execute the macro atomically.

Key properties:
- **Permissionless** — anyone can deploy a macro, anyone can call `runMacro`
- **Composable** — macros produce standard batch operations, reusing the
  existing Host infrastructure
- **Sender-preserving** — MacroForwarder is a trusted forwarder (EIP-2771),
  so `msg.sender` in the Host context is the original caller, not the forwarder
- **View-only building** — `buildBatchOperations` is a `view` function, so
  macros cannot mutate state during operation construction

## MacroForwarder Contract

**Address**: `0xFD0268E33111565dE546af2675351A4b1587F89F` (same on all networks)

**Source**: [MacroForwarder.sol](https://raw.githubusercontent.com/superfluid-org/protocol-monorepo/refs/heads/dev/packages/ethereum-contracts/contracts/utils/MacroForwarder.sol),
inherits [ForwarderBase.sol](https://raw.githubusercontent.com/superfluid-org/protocol-monorepo/refs/heads/dev/packages/ethereum-contracts/contracts/utils/ForwarderBase.sol)

**Interface**:

```solidity
function runMacro(IUserDefinedMacro m, bytes calldata params) external payable returns (bool)
```

MacroForwarder also exposes `buildBatchOperations(macro, params)` as a
`public view` — useful for simulating what a macro will produce off-chain
without executing it.

### Execution Flow

```
User calls MacroForwarder.runMacro(macro, params)
  │
  ├─ 1. BUILD:   macro.buildBatchOperations(host, params, msgSender)  [view]
  │               → returns ISuperfluid.Operation[] array
  │
  ├─ 2. EXECUTE: host.forwardBatchCall(operations)  [EIP-2771, payable]
  │               → Host executes all operations atomically as msgSender
  │
  └─ 3. VERIFY:  macro.postCheck(host, params, msgSender)  [view]
                  → reverts if post-execution state is invalid
```

If any step reverts, the entire transaction reverts — all-or-nothing.

## IUserDefinedMacro Interface

[Source](https://raw.githubusercontent.com/superfluid-org/protocol-monorepo/40d34958f31b55fa0f9271f07794786c56a01a65/packages/ethereum-contracts/contracts/interfaces/utils/IUserDefinedMacro.sol)

```solidity
interface IUserDefinedMacro {
    function buildBatchOperations(
        ISuperfluid host,
        bytes memory params,
        address msgSender
    ) external view returns (ISuperfluid.Operation[] memory operations);

    function postCheck(
        ISuperfluid host,
        bytes memory params,
        address msgSender
    ) external view;
}
```

### buildBatchOperations (required)

Returns an array of `ISuperfluid.Operation` structs that the MacroForwarder
forwards to `host.forwardBatchCall`. This is a `view` function — it reads
on-chain state (e.g., check if a flow exists, look up token addresses) but
cannot write state.

Parameters:
- `host` — the Superfluid Host contract (use to resolve agreement addresses)
- `params` — ABI-encoded application-specific parameters
- `msgSender` — the original caller (the EOA/contract that called `runMacro`)

### postCheck (required, can be empty)

Called after the batch executes. Use it to validate that the expected outcome
was achieved (e.g., confirm pool units were assigned, verify a flow exists).
Revert with a descriptive custom error if validation fails. An empty
implementation (no-op) is valid for macros that don't need post-execution
checks.

### Recommended: params helper functions

Add one or more `view` functions that take typed arguments and return the
ABI-encoded `bytes` for `params`. This improves developer experience and
makes the macro usable from block explorers and frontend tooling:

```solidity
function getParams(ISuperToken token, address receiver, int96 flowRate)
    external pure returns (bytes memory)
{
    return abi.encode(token, receiver, flowRate);
}
```

## Building Operations

Each operation in the returned array is an `ISuperfluid.Operation`:

```solidity
struct Operation {
    uint32 operationType;  // see batch_operation_types below
    address target;
    bytes data;
}
```

### Batch Operation Types

Cross-reference: `batch_operation_types` in `Superfluid.abi.yaml`

- Type 1 `ERC20_APPROVE` — target: SuperToken, data: `abi.encode(spender, amount)`
- Type 2 `ERC20_TRANSFER_FROM` — target: SuperToken, data: `abi.encode(sender, recipient, amount)`
- Type 4 `ERC20_INCREASE_ALLOWANCE` — target: SuperToken, data: `abi.encode(spender, addedValue)`
- Type 5 `ERC20_DECREASE_ALLOWANCE` — target: SuperToken, data: `abi.encode(spender, subtractedValue)`
- Type 101 `SUPERTOKEN_UPGRADE` — target: SuperToken, data: `abi.encode(amount)`
- Type 102 `SUPERTOKEN_DOWNGRADE` — target: SuperToken, data: `abi.encode(amount)`
- Type 201 `SUPERFLUID_CALL_AGREEMENT` — target: agreement, data: `abi.encode(callData, userData)` — see below
- Type 202 `CALL_APP_ACTION` — target: Super App, data: `abi.encode(callData)`
- Type 301 `SIMPLE_FORWARD_CALL` — target: any contract, data: full encodeFunctionData, or `0x` for pure value transfers
- Type 302 `ERC2771_FORWARD_CALL` — target: ERC-2771 recipient, data: full encodeFunctionData (sender appended per ERC-2771)

Types 301-302 are less common in macros but available for advanced use cases
(e.g., calling arbitrary contracts within a batch).

GOTCHA: Types 1-5 and 101-102 use parameter-only encoding (no function
selector). Types 201+ use full `abi.encodeCall` (selector included).

GOTCHA: ERC-20 operations (types 1-5) target a **SuperToken**, not an
arbitrary ERC-20. To approve an underlying ERC-20 (e.g., for wrapping), use
a separate transaction outside the macro.

### Agreement Call Encoding (Type 201)

This is the most common operation type in macros. The `data` field is:

```solidity
data: abi.encode(
    abi.encodeCall(agreement.functionName, (arg1, arg2, ..., new bytes(0))),
    //                                     └─ ctx placeholder ──────────┘
    userData  // bytes — forwarded to Super App callbacks, or new bytes(0)
)
```

The inner `abi.encodeCall` produces full calldata (with selector). The
trailing `new bytes(0)` is the **context placeholder** — the Host replaces it
with the real Superfluid context at execution time.

### Resolving Agreement Addresses

Use the Host to look up agreement contract addresses:

```solidity
IConstantFlowAgreementV1 cfa = IConstantFlowAgreementV1(address(
    host.getAgreementClass(
        keccak256("org.superfluid-finance.agreements.ConstantFlowAgreement.v1")
    )
));

IGeneralDistributionAgreementV1 gda = IGeneralDistributionAgreementV1(address(
    host.getAgreementClass(
        keccak256("org.superfluid-finance.agreements.GeneralDistributionAgreement.v1")
    )
));
```

### Common Operation Patterns

**Create a CFA stream:**
```solidity
ISuperfluid.Operation({
    operationType: BatchOperation.OPERATION_TYPE_SUPERFLUID_CALL_AGREEMENT,
    target: address(cfa),
    data: abi.encode(
        abi.encodeCall(cfa.createFlow, (token, receiver, flowRate, new bytes(0))),
        new bytes(0) // userData
    )
})
```

**Upgrade (wrap) tokens:**
```solidity
ISuperfluid.Operation({
    operationType: BatchOperation.OPERATION_TYPE_SUPERTOKEN_UPGRADE,
    target: address(token),
    data: abi.encode(amount)
})
```

**Approve a contract to spend SuperTokens:**
```solidity
ISuperfluid.Operation({
    operationType: BatchOperation.OPERATION_TYPE_ERC20_APPROVE,
    target: address(token),
    data: abi.encode(spender, amount)
})
```

**Connect to a GDA pool:**
```solidity
ISuperfluid.Operation({
    operationType: BatchOperation.OPERATION_TYPE_SUPERFLUID_CALL_AGREEMENT,
    target: address(gda),
    data: abi.encode(
        abi.encodeCall(gda.connectPool, (pool, new bytes(0))),
        new bytes(0) // userData
    )
})
```

## postCheck Patterns

Use `postCheck` to verify the expected outcome. Example — confirm the caller
received pool units:

```solidity
function postCheck(ISuperfluid, bytes memory params, address msgSender)
    external view override
{
    (, ISuperfluidPool pool) = abi.decode(params, (ISuperToken, ISuperfluidPool));
    if (pool.getUnits(msgSender) == 0) {
        revert NoPoolUnits();
    }
}
```

For simple macros where the batch operations themselves revert on failure
(e.g., creating a flow to a zero address), an empty `postCheck` is fine.

## Client-Side Usage (viem)

### Basic macro — direct execution

The most common pattern. The user's wallet signs the transaction directly.

```typescript
import { getContract, parseAbi } from 'viem'

const MACRO_FORWARDER = '0xFD0268E33111565dE546af2675351A4b1587F89F'

// 1. Get contract instances
const macro = getContract({
  address: macroAddress,
  abi: parseAbi([
    'function getParams(address token, address receiver, int96 flowRate, uint256 upgradeAmount) view returns (bytes)'
  ]),
  client: publicClient
})

// 2. Encode params via the macro's helper
const params = await macro.read.getParams([tokenAddr, receiverAddr, flowRate, upgradeAmount])

// 3. Execute
const hash = await walletClient.writeContract({
  address: MACRO_FORWARDER,
  abi: parseAbi([
    'function runMacro(address m, bytes calldata params) external payable returns (bool)'
  ]),
  functionName: 'runMacro',
  args: [macroAddress, params]
})
```

### Dry-run simulation

Preview what operations a macro will produce without executing:

```typescript
const operations = await publicClient.readContract({
  address: MACRO_FORWARDER,
  abi: parseAbi([
    'function buildBatchOperations(address m, bytes calldata params) view returns ((uint32 operationType, address target, bytes data)[])'
  ]),
  functionName: 'buildBatchOperations',
  args: [macroAddress, params]
})
```

### EIP-712 signed macro — human-readable wallet prompts

For macros that extend `EIP712MacroBase`. The user sees a human-readable
message in their wallet instead of raw calldata.

```typescript
import { encodeAbiParameters, parseAbiParameters, parseSignature } from 'viem'

// 1. Get the message and encoded params from the macro's view function
const [actionCode, message, actionParams, digest] = await macro.read.encode712SetDCAPosition([
  '0x656e000000000000000000000000000000000000000000000000000000000000', // "en" as bytes32
  { torex: torexAddr, flowRate, distributor, referrer, upgradeAmount }
])

// 2. Build EIP-712 domain — name/version MUST match the macro's EIP712 constructor args
const domain = {
  name: 'SuperBoring',      // must match constructor("SuperBoring", "0.0.0")
  version: '0.0.0',
  chainId,
  verifyingContract: macroAddress
}

// 3. Define types matching the Solidity struct
const types = {
  SetDCAPosition: [
    { name: 'message', type: 'string' },
    { name: 'torex', type: 'address' },
    { name: 'flowRate', type: 'int96' },
    { name: 'distributor', type: 'address' },
    { name: 'referrer', type: 'address' },
    { name: 'upgradeAmount', type: 'uint256' }
  ]
}

// 4. Sign — wallet displays the human-readable message
const signature = await walletClient.signTypedData({
  domain,
  types,
  primaryType: 'SetDCAPosition',
  message: { message, torex: torexAddr, flowRate, distributor, referrer, upgradeAmount }
})

// 5. Parse signature into (v, r, s) and encode for the contract
const { v, r, s } = parseSignature(signature)
const signatureVRS = encodeAbiParameters(
  parseAbiParameters('uint8, bytes32, bytes32'),
  [Number(v), r, s]
)

// 6. Encode full macro params: (actionCode, lang, actionParams, signatureVRS)
const macroParams = encodeAbiParameters(
  parseAbiParameters('uint8, bytes32, bytes, bytes'),
  [actionCode, '0x656e...', actionParams, signatureVRS]  // lang = "en" as bytes32
)

// 7. Execute via MacroForwarder
const hash = await walletClient.writeContract({
  address: MACRO_FORWARDER,
  abi: parseAbi([
    'function runMacro(address m, bytes calldata params) external payable returns (bool)'
  ]),
  functionName: 'runMacro',
  args: [macroAddress, macroParams]
})
```

## Security Considerations

- **View-only building**: `buildBatchOperations` and `postCheck` are `view`
  functions. A macro that attempts state mutations during these calls will
  revert. This prevents macros from performing unauthorized side effects.
- **Atomic execution**: All operations execute as a single `host.batchCall`.
  If any operation fails, the entire transaction reverts.
- **Permissionless macros**: Anyone can deploy a macro contract and anyone
  can call `runMacro` with it. The macro sees `msgSender` (the original
  caller), preserving proper attribution and access control.
- **Native value forwarding**: `runMacro` is `payable` — `msg.value` is
  forwarded through `forwardBatchCall`. Native value goes to the first
  `CALL_APP_ACTION`, `SIMPLE_FORWARD`, or `ERC2771_FORWARD` operation.

## Example: Wrap-and-Stream Macro

A minimal macro that wraps underlying ERC-20 tokens into a SuperToken and
creates a CFA stream in one atomic transaction.

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.26;

import {
    ISuperfluid,
    BatchOperation,
    IConstantFlowAgreementV1,
    ISuperToken
} from "@superfluid-finance/ethereum-contracts/contracts/interfaces/superfluid/ISuperfluid.sol";
import {IUserDefinedMacro} from "@superfluid-finance/ethereum-contracts/contracts/interfaces/utils/IUserDefinedMacro.sol";

/// @title WrapAndStreamMacro
/// @notice Wraps underlying tokens and creates a CFA stream in one transaction.
/// @dev Caller must have approved the SuperToken to spend the underlying ERC-20
///      before calling runMacro (this approval targets the underlying, so it
///      cannot be included in the batch).
contract WrapAndStreamMacro is IUserDefinedMacro {

    /// @notice Encode parameters for runMacro.
    function getParams(
        ISuperToken token,
        address receiver,
        int96 flowRate,
        uint256 upgradeAmount
    ) external pure returns (bytes memory) {
        return abi.encode(token, receiver, flowRate, upgradeAmount);
    }

    function buildBatchOperations(
        ISuperfluid host,
        bytes memory params,
        address /* msgSender */
    ) external view override returns (ISuperfluid.Operation[] memory operations) {
        (ISuperToken token, address receiver, int96 flowRate, uint256 upgradeAmount) =
            abi.decode(params, (ISuperToken, address, int96, uint256));

        IConstantFlowAgreementV1 cfa = IConstantFlowAgreementV1(address(
            host.getAgreementClass(
                keccak256("org.superfluid-finance.agreements.ConstantFlowAgreement.v1")
            )
        ));

        operations = new ISuperfluid.Operation[](2);

        // 1. Upgrade underlying ERC-20 → SuperToken
        operations[0] = ISuperfluid.Operation({
            operationType: BatchOperation.OPERATION_TYPE_SUPERTOKEN_UPGRADE,
            target: address(token),
            data: abi.encode(upgradeAmount)
        });

        // 2. Create stream to receiver
        operations[1] = ISuperfluid.Operation({
            operationType: BatchOperation.OPERATION_TYPE_SUPERFLUID_CALL_AGREEMENT,
            target: address(cfa),
            data: abi.encode(
                abi.encodeCall(cfa.createFlow, (token, receiver, flowRate, new bytes(0))),
                new bytes(0) // userData
            )
        });
    }

    function postCheck(ISuperfluid, bytes memory, address) external view override {
        // createFlow reverts if flow already exists or flowRate is invalid —
        // no additional validation needed.
    }
}
```

See **Client-Side Usage** above for viem examples of calling `runMacro`.

## Real-World Example: EIP-712 Signed Macro

For production-grade macros with human-readable wallet signing (EIP-712 typed
data), see `macro-forwarders-eip712-example.md`. It covers:
- `EIP712MacroBase` abstract contract (signature verification, action routing)
- `SB712Macro` (SuperBoring DCA position management)
- Key patterns: dynamic operation count, on-chain state reads, userData for
  callbacks, postCheck validation

## Links & Source Code

- [MacroForwarder.sol](https://raw.githubusercontent.com/superfluid-org/protocol-monorepo/refs/heads/dev/packages/ethereum-contracts/contracts/utils/MacroForwarder.sol) — the forwarder contract
- [IUserDefinedMacro.sol](https://raw.githubusercontent.com/superfluid-org/protocol-monorepo/40d34958f31b55fa0f9271f07794786c56a01a65/packages/ethereum-contracts/contracts/interfaces/utils/IUserDefinedMacro.sol) — the macro interface
- [ForwarderBase.sol](https://raw.githubusercontent.com/superfluid-org/protocol-monorepo/refs/heads/dev/packages/ethereum-contracts/contracts/utils/ForwarderBase.sol) — shared base for all trusted forwarders
- [MacroForwarder.t.sol](https://raw.githubusercontent.com/superfluid-org/protocol-monorepo/40d34958f31b55fa0f9271f07794786c56a01a65/packages/ethereum-contracts/test/foundry/utils/MacroForwarder.t.sol) — Foundry tests with additional example macros
- [Superfluid Macros wiki](https://github.com/superfluid-org/protocol-monorepo/wiki/Superfluid-Macros) — design write-up
