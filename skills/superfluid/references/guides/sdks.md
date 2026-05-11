# SDKs & Packages

## `@sfpro/sdk` — ABI imports and addresses

The [`@sfpro/sdk`](https://sdk.superfluid.pro/docs) package provides typed JSON ABIs
for use with viem / wagmi / ethers. ABIs are split across sub-paths:

| Contract (YAML name) | Import path | Export name |
|---|---|---|
| CFAv1Forwarder | `@sfpro/sdk/abi` | `cfaForwarderAbi` |
| GDAv1Forwarder | `@sfpro/sdk/abi` | `gdaForwarderAbi` |
| SuperfluidPool | `@sfpro/sdk/abi` | `gdaPoolAbi` |
| SuperToken | `@sfpro/sdk/abi` | `superTokenAbi` |
| Superfluid (Host) | `@sfpro/sdk/abi/core` | `hostAbi` |
| ConstantFlowAgreementV1 | `@sfpro/sdk/abi/core` | `cfaAbi` |
| GeneralDistributionAgreementV1 | `@sfpro/sdk/abi/core` | `gdaAbi` |
| InstantDistributionAgreementV1 | `@sfpro/sdk/abi/core` | `idaAbi` |
| SuperTokenFactory | `@sfpro/sdk/abi/core` | `superTokenFactoryAbi` |
| BatchLiquidator | `@sfpro/sdk/abi/core` | `batchLiquidatorAbi` |
| TOGA | `@sfpro/sdk/abi/core` | `togaAbi` |
| Governance | `@sfpro/sdk/abi/core` | `governanceAbi` |
| AutoWrapManager | `@sfpro/sdk/abi/automation` | `autoWrapManagerAbi` |
| AutoWrapStrategy | `@sfpro/sdk/abi/automation` | `autoWrapStrategyAbi` |
| FlowScheduler | `@sfpro/sdk/abi/automation` | `flowSchedulerAbi` |
| VestingSchedulerV3 | `@sfpro/sdk/abi/automation` | `vestingSchedulerV3Abi` |
| Fontaine | `@sfpro/sdk/abi/sup` | `fontaineAbi` |
| FluidLocker | `@sfpro/sdk/abi/sup` | `lockerAbi` |
| FluidLockerFactory | `@sfpro/sdk/abi/sup` | `lockerFactoryAbi` |
| FluidEPProgramManager | `@sfpro/sdk/abi/sup` | `programManagerAbi` |
| StakingRewardController | `@sfpro/sdk/abi/sup` | `stakingRewardControllerAbi` |
| SUPToken | `@sfpro/sdk/abi/sup` | `supTokenAbi` |
| SUPVestingFactory | `@sfpro/sdk/abi/sup` | `vestingFactoryAbi` |

The SDK also exports chain-indexed address objects alongside each ABI:

| Import path | Address exports |
|---|---|
| `@sfpro/sdk/abi` | `cfaForwarderAddress`, `gdaForwarderAddress` |
| `@sfpro/sdk/abi/core` | `hostAddress`, `cfaAddress`, `gdaAddress`, `idaAddress`, `superTokenFactoryAddress`, `batchLiquidatorAddress`, `togaAddress`, `governanceAddress` |
| `@sfpro/sdk/abi/automation` | `autoWrapManagerAddress`, `autoWrapStrategyAddress`, `flowSchedulerAddress`, `vestingSchedulerV3Address` |
| `@sfpro/sdk/abi/sup` | `supTokenAddress`, `lockerFactoryAddress`, `programManagerAddress`, `stakingRewardControllerAddress`, `vestingFactoryAddress` |

Each export is an object keyed by chain ID:

```js
import { hostAbi, hostAddress } from "@sfpro/sdk/abi/core";
const host = hostAddress[8453]; // Base Mainnet
```

CFASuperAppBase and SuperTokenV1Library are not in the SDK (abstract base /
Solidity library).

When writing application code, ALWAYS import ABIs and addresses from
`@sfpro/sdk` — do NOT hand-craft ABI fragments (risk of phantom parameters)
or hardcode contract addresses (they vary per network).

---

## When to use what

- **Frontend with wagmi/viem** — install `@sfpro/sdk`. Enhanced ABIs include
  downstream errors for type-safe error handling. Import paths documented above.
  [Docs](https://sdk.superfluid.pro/docs) ·
  [Repo](https://github.com/superfluid-org/superfluid.pro/tree/main/sdk)
- **Solidity integrations** — import ABIs from
  `@superfluid-finance/ethereum-contracts` at build time. Do NOT use as a
  runtime dependency — it pulls in heavy deps not suitable for client bundles.
  [Repo](https://github.com/superfluid-org/protocol-monorepo/tree/dev/packages/ethereum-contracts)
- **Resolving addresses/networks at runtime** —
  `@superfluid-finance/metadata` has zero dependencies, wrapped by
  `scripts/metadata.mjs`.
  [Repo](https://github.com/superfluid-org/protocol-monorepo/tree/dev/packages/metadata)
- **Finding token addresses** — `@superfluid-finance/tokenlist` based on
  `@uniswap/token-lists`, wrapped by `scripts/tokenlist.mjs`.
  [Repo](https://github.com/superfluid-org/tokenlist)

---

## Deprecated packages — do not recommend for new projects

- `@superfluid-finance/sdk-core` → replaced by `@sfpro/sdk`. Over-abstracted, locked to ethers v5. [Docs](https://superfluid.gitbook.io/superfluid/developers/sdk-core) · [Repo](https://github.com/superfluid-org/protocol-monorepo/tree/dev/packages/sdk-core)
- `@superfluid-finance/sdk-redux` → replaced by wagmi + `@sfpro/sdk`. Pre-wagmi Redux hooks. [Repo](https://github.com/superfluid-org/protocol-monorepo/tree/dev/packages/sdk-redux)
- `@superfluid-finance/js-sdk` → replaced by `@sfpro/sdk`. Oldest SDK, truffle-based. [Repo](https://github.com/superfluid-org/protocol-monorepo/tree/dev/packages/js-sdk)
- `@superfluid-finance/widget` → no replacement. Subscription checkout widget, stuck on wagmi v1. [Repo](https://github.com/superfluid-finance/widget) · [Playground](https://checkout-builder.superfluid.finance/)
