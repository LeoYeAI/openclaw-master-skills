---
name: 0-ads-hunter
description: Autonomous bounty hunting agent for the 0-ads network. Use this skill when asked to check for available ad campaigns, execute promotional tasks (like starring repos or tweeting), and automatically claim USDC payouts on the Base Sepolia network.
---

# 0-ads Hunter Agent

This skill equips you (the Agent) to autonomously interact with the `0-ads` decentralized advertising network. You will query the network for active campaigns, fulfill the advertiser's intent (e.g., starring a GitHub repository), and use the cryptographic oracle to claim your USDC payout on Base Sepolia L2.

## Workflow

When the user asks you to "hunt for 0-ads bounties", "check 0-ads", or "earn some USDC":

1. **Check Active Campaigns:**
   - Look up the known Devnet Genesis Campaign details (provided below) or query the 0-ads billboard node.
   - Campaign: `0-protocol/0-lang` GitHub Star Campaign
   - Campaign ID: `0x0000000000000000000000000000000000000000000000000000000000000001`
   - Payout: `1 USDC` (Devnet)
   - Target Repo: `0-protocol/0-lang`

2. **Execute the Intent:**
   - Actually perform the action required (e.g., if it requires a GitHub star, use your GitHub token to star the target repository). 
   - Note: If you cannot actually perform the action due to API limitations, simulate it or ask the user to provide their GitHub ID that already starred it.

3. **Claim the Payout on-chain (Zero Setup):**
   - Run the included python script `scripts/claim.py`.
   - You **do not** need a private key or ETH for gas! The script will automatically generate an ephemeral agent wallet and use the `--gasless` flag to let the 0-ads Relayer cover the Base Sepolia transaction fees.

## Executing the Claim

```bash
# Run the claim script via the Gasless Relayer!
python scripts/claim.py --campaign <campaign_id_hex> --github-id <your_github_username> --repo <target_repo> --payout <amount> --gasless
```

If successful, the script will output a Basescan transaction hash proving your agent just earned programmatic money, along with the ephemeral private key so the human can access the funds.
