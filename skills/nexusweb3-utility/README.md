# NexusWeb3 Utility Layer

Read-only API reference for NexusWeb3 utility protocols 11-20 on Base mainnet.

This skill provides contract addresses, function signatures, and usage examples for querying on-chain state. No credentials required for read operations.

## Protocols Covered

| # | Protocol | Address | What it does |
|---|----------|---------|-------------|
| 11 | AgentScheduler | `0x9fA51922DDc788e291D96471483e01eE646efCC0` | On-chain cron jobs |
| 12 | AgentOracle | `0x610a5EbF726Dc3CFD1804915A9724B6825e21B71` | Price and data feeds |
| 13 | AgentVoting | `0x2E3394EcB00358983183f08D4C5B6dB60f85EE3B` | Lightweight polls |
| 14 | AgentStorage | `0x29483A116B8D252Dc8bb1Ee057f650da305AA8b7` | Key-value store |
| 15 | AgentMessaging | `0xA621CCaDA114A7E40e35dEFAA1eb678244cF788E` | Agent-to-agent messaging |
| 16 | AgentStaking | `0x1EC42179138815B77af7566D37e77B4197680328` | NEXUS staking with revenue share |
| 17 | AgentWhitelist | `0x2870e015d1D44AcCe9Ac3287f4A345368Ce8EC6b` | Permission management |
| 18 | AgentAuction | `0x9027fD25e131D57B2D4182d505F20C2cF2227Cc4` | USDC auction house |
| 19 | AgentSplit | `0xA346535515C6aA80Ec0bb4805e029e9696e5fa08` | Revenue splitting |
| 20 | AgentInsights | `0xef53C81a802Ecc389662244Ab2C65a612FBf3E27` | Ecosystem analytics |

## Usage

This is an instruction-only skill. Install it and your agent can query any of the 10 utility protocols using the documented view functions. No credentials, no downloads, no executable code.

For write operations that sign transactions, install the `nexusweb3` financial skill which includes operator key setup.

## Security

All 30 NexusWeb3 contracts are triple-audited with Slither, 1,100+ Foundry tests, and 30 adversarial PoC attack scenarios. Source code at https://github.com/nexusweb3dev/nexusweb3-protocols.

## License

MIT-0
