# NexusWeb3 Safety Layer

Read-only API reference for NexusWeb3 safety and compliance protocols 21-30 on Base mainnet.

This skill provides contract addresses, function signatures, and usage examples for querying on-chain state. No credentials required for read operations.

## Protocols Covered

| # | Protocol | Address | What it does |
|---|----------|---------|-------------|
| 21 | AgentKillSwitch | `0xaf87912e1ccB501a22a3bDDe6c38Cb0CA31C4E96` | Emergency stop with spending limits |
| 22 | AgentKYA | `0xa736ad09d2e99a87910a04b5e445d7ed90f95efb` | Know-Your-Agent compliance |
| 23 | AgentAuditLog | `0x6a125ddaaf40cc773307fb312e5e7c66b1e551f3` | Tamper-proof audit trail |
| 24 | AgentBounty | `0xc84f118aea77fd1b6b07ce1927de7c7ae27fd9bf` | Hash-locked bounties |
| 25 | AgentLicense | `0x48fab1fbbe91a043e029935f81ea7421b23b3527` | IP licensing with royalties |
| 26 | AgentMilestone | `0x6b8ebe897751e3c59ea95f28832c3b70de221cce` | Milestone-based payments |
| 27 | AgentSubscription | `0xfcbc6fe1bb570b6b68dfdfcb34f37383e865858e` | Recurring billing |
| 28 | AgentInsolvency | `0xfe6a69e563f90f806babd71282f313c93544ea3f` | Debt management and wind-down |
| 29 | AgentReferral | `0x46ea1eff221120c8ac9aebe1c1871b317e27cfe4` | Viral referral network |
| 30 | AgentCollective | `0x2c5d55a49fa2ed03212b5fe5971ba219bab9d953` | Agent DAOs with pooled treasuries |

## Usage

This is an instruction-only skill. Install it and your agent can query any of the 10 safety protocols using the documented view functions. No credentials, no downloads, no executable code.

For write operations that sign transactions, install the `nexusweb3` financial skill which includes operator key setup.

## Security

All 30 NexusWeb3 contracts are triple-audited with Slither, 1,100+ Foundry tests, and 30 adversarial PoC attack scenarios. Source code at https://github.com/nexusweb3dev/nexusweb3-protocols.

## License

MIT-0
