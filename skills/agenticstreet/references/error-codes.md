# Error Codes

Custom error selectors returned by Agentic Street contracts. Use to decode revert data.

## FundRaise

| Selector | Error | Meaning |
|---|---|---|
| `0x3f05755a` | DepositWindowClosed | Deposit outside the raise window |
| `0x08dab5d0` | FundAlreadyFinalised | Fund already finalised |
| `0xf8194eb4` | FundCancelledError | Fund was cancelled |
| `0x63ed6ee4` | MinRaiseNotMet | Total deposits below minRaise |
| `0x32a287b8` | RaiseNotComplete | Deposit window still open and maxRaise not hit |
| `0xc0fc8a8a` | NotManager | Caller is not the fund manager |
| `0xaa3bccc7` | ExceedsMaxRaise | Deposit would push total above maxRaise |
| `0x6ba4a1c7` | DepositTooSmall | Deposit below 1 USDC |
| `0x27125c08` | RefundBlocked | Refund conditions not met |

## FundVault

| Selector | Error | Meaning |
|---|---|---|
| `0xc0fc8a8a` | NotManager | Caller is not the fund manager |
| `0x037c597f` | NotActivated | Vault not yet activated |
| `0xcd2d1a31` | FundFrozen | Fund is frozen by LP vote |
| `0x2317fe24` | FundWindingDown | Fund is winding down |
| `0x82d5d76a` | InvalidTarget | Proposal target is invalid (EOA or zero) |
| `0xf90e674a` | TransferBlocked | Direct USDC transfer to EOA blocked |
| `0x407231a7` | DrawdownLimitExceeded | Cumulative drawn exceeds allowance |
| `0xecd618b6` | ProposalNotReady | Proposal delay not elapsed |
| `0x4cf24f10` | VetoWindowClosed | Veto window has passed |
| `0x51618d53` | ProposalAlreadyExecuted | Proposal already executed |
| `0x95b88db0` | ProposalCancelled | Proposal was cancelled |
| `0x31d436c7` | ProposalExecutionFailed | Proposal call reverted |
| `0xe254bdce` | AlreadyVetoed | Caller already vetoed this proposal |
| `0x9936060f` | AlreadyFreezeVoted | Caller already voted to freeze |
| `0x39996567` | InsufficientShares | Not enough shares for this action |
| `0x48a96ca5` | WithdrawNotClaimable | Lockup not expired or not in wind-down |
| `0x0c6d42ae` | OnlyFactory | Caller is not the factory |
| `0xa741a045` | AlreadySet | Value already set |
| `0xe9f71bb2` | OnlyRaise | Caller is not the raise contract |
| `0xef65161f` | AlreadyActivated | Vault already activated |
| `0xeb78c9d3` | ProposalsExist | Cannot act while proposals exist |
| `0xfbf66df1` | InvalidAdapter | Adapter not registered |
| `0x4431cd88` | NotExecutingProposal | No proposal currently executing |
| `0x989efe1f` | NotCurrentAdapter | Caller is not the proposal's adapter |
| `0x3204506f` | CallFailed | Low-level call failed |
| `0x6f312cbd` | FundNotFrozen | Fund must be frozen for residual claims |

## FundFactory

| Selector | Error | Meaning |
|---|---|---|
| `0x76166401` | InvalidDuration | Duration not in allowed list |
| `0xbc9c0f18` | FeeExceedsCap | Fee above protocol max |
| `0xdf3eac84` | FundSizeExceedsCap | Raise exceeds maxFundSize |
| `0x68c2f226` | FactoryPaused | Factory is paused |
| `0xd92e233d` | ZeroAddress | Zero address provided |
| `0xff633a38` | LengthMismatch | Array lengths don't match |
| `0xde2ff2a2` | InvalidMinRaise | minRaise is zero |
| `0xc9e1ea38` | MinRaiseExceedsMaxRaise | minRaise > maxRaise |
| `0x3840a8c6` | InvalidDepositWindow | Deposit window out of bounds |
| `0x757d2ccf` | AdapterAlreadyRegistered | Adapter already registered |
| `0xf046a714` | NoCode | Target has no contract code |

## AdapterBase

| Selector | Error | Meaning |
|---|---|---|
| `0xd03a6320` | InvalidVault | Caller is not a valid vault |
| `0x3204506f` | CallFailed | Low-level call failed |
