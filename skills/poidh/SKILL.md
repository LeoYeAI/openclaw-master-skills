---
name: poidh-bounty
description: Post bounties and evaluate/accept winning submissions on poidh (pics or it didn't happen) on Arbitrum, Base, or Degen Chain. Use this skill when the user wants to create a bounty on poidh.xyz, post a task with an ETH or DEGEN reward on-chain, evaluate photo submissions using vision, accept a winning claim on a solo bounty, or initiate/resolve voting on an open bounty.
metadata:
  clawdbot:
    env:
      - PRIVATE_KEY
      - RPC_URL
      - POIDH_CHAIN
    bin:
      - cast
      - python3
---

## Overview

This skill interacts with the PoidhV3 contracts on Arbitrum, Base, and Degen Chain to:

1. **Post bounties** (solo or open)
2. **Evaluate claim submissions** using vision — fetch the image URI from each claim and compare against the bounty description
3. **Accept the winning claim** (solo bounty) or **initiate + resolve a vote** (open bounty)

**poidh** ("pics or it didn't happen") is a fully on-chain bounty protocol. Claimants submit photo proof, and the bounty issuer (or contributors via vote) accepts the best claim to release funds.

> ⚠️ The PoidhV3 contract enforces `msg.sender == tx.origin`. Only **EOA wallets** can create or accept bounties. Smart contract wallets (Safe, etc.) will revert with `ContractsCannotCreateBounties`.

---

## Required Environment Variables

| Variable      | Description                                                                  |
| ------------- | ---------------------------------------------------------------------------- |
| `PRIVATE_KEY` | Private key of the EOA signing transactions (hex, with or without 0x prefix) |
| `RPC_URL`     | RPC URL for the target chain                                                 |
| `POIDH_CHAIN` | Target chain: `arbitrum`, `base`, or `degen`                                 |

`POIDH_CONTRACT_ADDRESS` is resolved automatically from `POIDH_CHAIN` — do not set it manually.

---

## Supported Chains

| Chain       | Contract Address                             | Explorer            |
| ----------- | -------------------------------------------- | ------------------- |
| Arbitrum    | `0x5555Fa783936C260f77385b4E153B9725feF1719` | arbiscan.io         |
| Base        | `0x5555Fa783936C260f77385b4E153B9725feF1719` | basescan.org        |
| Degen Chain | `0x18E5585ca7cE31b90Bc8BB7aAf84152857cE243f` | explorer.degen.tips |

> ⚠️ Minimum amounts differ by chain. On **Arbitrum and Base**: `0.001 ETH` minimum bounty, `0.00001 ETH` minimum contribution. On **Degen Chain**: `1000 DEGEN` minimum bounty, `10 DEGEN` minimum contribution. Always verify on-chain before posting:
>
> ```bash
> cast call $POIDH_CONTRACT_ADDRESS "MIN_BOUNTY_AMOUNT()(uint256)" --rpc-url $RPC_URL
> cast call $POIDH_CONTRACT_ADDRESS "MIN_CONTRIBUTION()(uint256)" --rpc-url $RPC_URL
> ```

Resolve the contract address at the start of every session:

```bash
if [ "$POIDH_CHAIN" = "degen" ]; then
  POIDH_CONTRACT_ADDRESS="0x18E5585ca7cE31b90Bc8BB7aAf84152857cE243f"
else
  # arbitrum and base share the same address
  POIDH_CONTRACT_ADDRESS="0x5555Fa783936C260f77385b4E153B9725feF1719"
fi
```

The poidh.xyz URL also changes per chain:

```bash
if [ "$POIDH_CHAIN" = "arbitrum" ]; then
  POIDH_BASE_URL="https://poidh.xyz/arbitrum"
  POIDH_V2_OFFSET=180
elif [ "$POIDH_CHAIN" = "degen" ]; then
  POIDH_BASE_URL="https://poidh.xyz/degen"
  POIDH_V2_OFFSET=1197
else
  POIDH_BASE_URL="https://poidh.xyz/base"
  POIDH_V2_OFFSET=986
fi
```

---

## Part 1: Posting a Bounty

### Check Minimum Bounty Amount

```bash
cast call $POIDH_CONTRACT_ADDRESS "MIN_BOUNTY_AMOUNT()(uint256)" --rpc-url $RPC_URL
```

### Post a Solo Bounty

Solo = only you fund it; you accept claims directly with no vote required.

```bash
cast send $POIDH_CONTRACT_ADDRESS \
  "createSoloBounty(string,string)" \
  "<BOUNTY_NAME>" \
  "<BOUNTY_DESCRIPTION>" \
  --value <AMOUNT> \
  --private-key $PRIVATE_KEY \
  --rpc-url $RPC_URL
```

**Example:**

```bash
cast send $POIDH_CONTRACT_ADDRESS \
  "createSoloBounty(string,string)" \
  "Brooklyn Bridge at sunset" \
  "High quality photo of the Brooklyn Bridge during golden hour. Must show the full span." \
  --value 0.001ether \
  --private-key $PRIVATE_KEY \
  --rpc-url $RPC_URL
```

### Post an Open Bounty

Open = others can co-fund; claim acceptance requires a contributor-weighted vote.

```bash
cast send $POIDH_CONTRACT_ADDRESS \
  "createOpenBounty(string,string)" \
  "<BOUNTY_NAME>" \
  "<BOUNTY_DESCRIPTION>" \
  --value <AMOUNT> \
  --private-key $PRIVATE_KEY \
  --rpc-url $RPC_URL
```

### Get the Bounty ID After Posting

```bash
cast receipt <TX_HASH> --rpc-url $RPC_URL --json | \
  python3 -c "
import sys, json
receipt = json.load(sys.stdin)
for log in receipt['logs']:
    if log['address'].lower() == '${POIDH_CONTRACT_ADDRESS}'.lower() and len(log['topics']) >= 2:
        bounty_id = int(log['topics'][1], 16)
        frontend_id = bounty_id + ${POIDH_V2_OFFSET}
        print(f'Bounty ID: {bounty_id}')
        print(f'View at: ${POIDH_BASE_URL}/bounty/{frontend_id}')
        break
"
```

---

## Part 2: Evaluating Claims

When the user wants to pick a winner, the agent must:

1. Fetch all claims for the bounty
2. Retrieve each claim's URI from the NFT contract
3. Fetch and evaluate the content against the bounty description
4. Pick the best match

Claim submissions are freeform — the URI could point to an image, a video, a tweet, a GitHub PR, a webpage, a document, or anything else. Evaluate whatever you find against what the bounty asked for.

### Step 1: Fetch Claims for a Bounty

```bash
cast call $POIDH_CONTRACT_ADDRESS \
  "getClaimsByBountyId(uint256,uint256)(tuple(uint256,address,uint256,address,string,string,uint256,bool)[])" \
  <BOUNTY_ID> 0 \
  --rpc-url $RPC_URL
```

Returns up to 10 claims (most recent first). Increment offset by 10 to paginate. Each claim tuple:
`(id, issuer, bountyId, bountyIssuer, name, description, createdAt, accepted)`

The `name` and `description` fields on the claim are also set by the claimant and may give useful context about what they submitted.

### Step 2: Get the URI for Each Claim

```bash
# Get NFT contract address
NFT_ADDRESS=$(cast call $POIDH_CONTRACT_ADDRESS "poidhNft()(address)" --rpc-url $RPC_URL)

# Get token URI for a specific claim
cast call $NFT_ADDRESS "tokenURI(uint256)(string)" <CLAIM_ID> --rpc-url $RPC_URL
```

### Step 3: Resolve the URI

Convert non-HTTP URIs to fetchable URLs:

```python
uri = "<URI_FROM_TOKEN>"
if uri.startswith("ipfs://"):
    url = uri.replace("ipfs://", "https://ipfs.io/ipfs/")
elif uri.startswith("ar://"):
    url = uri.replace("ar://", "https://arweave.net/")
else:
    url = uri  # already HTTP
```

If the URL returns JSON metadata (standard ERC721 format), check for an `image` or `animation_url` field and resolve those too:

```python
import requests

response = requests.get(url)
try:
    meta = response.json()
    # Prefer animation_url (video/interactive) over image if both present
    content_url = meta.get("animation_url") or meta.get("image") or url
    if content_url.startswith("ipfs://"):
        content_url = content_url.replace("ipfs://", "https://ipfs.io/ipfs/")
except Exception:
    content_url = url  # URI points directly to the content
```

### Step 4: Evaluate the Content

Fetch and review the content at `content_url`. Use the appropriate method based on what you find:

- **Image** — use native vision to view it directly
- **Webpage / tweet / article** — use the web fetch tool to read the content
- **Video** — note the URL and evaluate based on the thumbnail or any available metadata
- **Document / PDF** — fetch and read the text content

Evaluate each claim against the bounty `name` and `description` on:

- **Relevance** — does the submission match what was actually asked for?
- **Quality** — is it complete, clear, and unambiguous?
- **Authenticity** — does it appear genuine and original (not recycled or faked)?

Pick the claim with the highest overall score. Present your reasoning to the user before executing any transaction.

---

## Part 3: Accepting a Winning Claim — Solo Bounty

For solo bounties (and open bounties where no external contributors ever joined), the issuer accepts directly. This immediately finalizes the bounty, credits the claimant payout to `pendingWithdrawals`, takes the 2.5% protocol fee, and transfers the claim NFT to the issuer.

```bash
cast send $POIDH_CONTRACT_ADDRESS \
  "acceptClaim(uint256,uint256)" \
  <BOUNTY_ID> <CLAIM_ID> \
  --private-key $PRIVATE_KEY \
  --rpc-url $RPC_URL
```

---

## Part 4: Accepting a Winning Claim — Open Bounty (Vote Flow)

For open bounties where external contributors have joined, direct accept is blocked. Use the two-step vote flow.

### Check if External Contributors Exist

```bash
cast call $POIDH_CONTRACT_ADDRESS \
  "everHadExternalContributor(uint256)(bool)" \
  <BOUNTY_ID> \
  --rpc-url $RPC_URL
```

If `false`, fall back to `acceptClaim` (Part 3). If `true`, proceed with the vote flow below.

### Step 1: Submit the Chosen Claim for Vote (Issuer Only)

The issuer's full contribution weight is automatically cast as a YES vote at this point.

```bash
cast send $POIDH_CONTRACT_ADDRESS \
  "submitClaimForVote(uint256,uint256)" \
  <BOUNTY_ID> <CLAIM_ID> \
  --private-key $PRIVATE_KEY \
  --rpc-url $RPC_URL
```

After this call, other contributors have **2 days** to vote YES/NO via the poidh.xyz UI or by calling `voteClaim(bountyId, bool)` directly.

### Step 2: Check Vote Status

```bash
cast call $POIDH_CONTRACT_ADDRESS \
  "bountyVotingTracker(uint256)(uint256,uint256,uint256)" \
  <BOUNTY_ID> \
  --rpc-url $RPC_URL
# Returns: yes_weight, no_weight, deadline_timestamp
```

```bash
python3 -c "import time; deadline=<DEADLINE>; print('Voting ended' if time.time() > deadline else f'Voting ends in {int((deadline - time.time())/3600)}h')"
```

### Step 3: Resolve the Vote (Permissionless)

After the 2-day window closes, anyone can resolve. If YES weight > 50% of total weight, the claim is accepted and funds are distributed.

```bash
cast send $POIDH_CONTRACT_ADDRESS \
  "resolveVote(uint256)" \
  <BOUNTY_ID> \
  --private-key $PRIVATE_KEY \
  --rpc-url $RPC_URL
```

---

## Part 5: Submitting a Claim on Someone Else's Bounty

Any EOA (except the bounty issuer) can submit a claim on an active open or solo bounty. This is how the agent acts as a **claimant** rather than an issuer. No native token is required to submit a claim — only gas.

The `uri` is the proof of completion — it can be anything: an IPFS image hash, a direct image URL, a tweet, a GitHub link, a webpage, a video, etc. It gets minted into a claim NFT at submission time.

### Check That the Bounty is Active

Before submitting, verify the bounty exists, is not finalized, and has no ongoing vote:

```bash
cast call $POIDH_CONTRACT_ADDRESS \
  "bounties(uint256)(uint256,address,string,string,uint256,address,uint256,uint256)" \
  <BOUNTY_ID> \
  --rpc-url $RPC_URL
# Returns: id, issuer, name, description, amount, claimer, createdAt, claimId
# claimer == 0x0 means active; claimer == issuer means cancelled; claimer == other means already won
```

Also confirm no vote is currently in progress:

```bash
cast call $POIDH_CONTRACT_ADDRESS \
  "bountyCurrentVotingClaim(uint256)(uint256)" \
  <BOUNTY_ID> \
  --rpc-url $RPC_URL
# Returns 0 if no active vote — safe to submit
```

### Submit the Claim

```bash
cast send $POIDH_CONTRACT_ADDRESS \
  "createClaim(uint256,string,string,string)" \
  <BOUNTY_ID> \
  "<CLAIM_NAME>" \
  "<CLAIM_DESCRIPTION>" \
  "<PROOF_URI>" \
  --private-key $PRIVATE_KEY \
  --rpc-url $RPC_URL
```

- `CLAIM_NAME` — short title for the submission
- `CLAIM_DESCRIPTION` — explanation of how the bounty was completed
- `PROOF_URI` — the actual proof (image URL, IPFS URI, tweet URL, GitHub link, etc.)

**Example:**

```bash
cast send $POIDH_CONTRACT_ADDRESS \
  "createClaim(uint256,string,string,string)" \
  42 \
  "Brooklyn Bridge golden hour" \
  "Took this photo at 7:43pm on the Manhattan side. Full span visible with reflection in the water." \
  "ipfs://QmXyz..." \
  --private-key $PRIVATE_KEY \
  --rpc-url $RPC_URL
```

### Get the Claim ID After Submitting

```bash
cast receipt <TX_HASH> --rpc-url $RPC_URL --json | \
  python3 -c "
import sys, json
receipt = json.load(sys.stdin)
for log in receipt['logs']:
    if log['address'].lower() == '$POIDH_CONTRACT_ADDRESS'.lower() and len(log['topics']) >= 2:
        claim_id = int(log['topics'][1], 16)
        print(f'Claim ID: {claim_id}')
        break
"
```

### Important Constraints

- The agent's wallet (`PRIVATE_KEY`) cannot be the bounty issuer — `IssuerCannotClaim` will revert
- Submitting is blocked while a vote is active on that bounty — `VotingOngoing` will revert
- The bounty must still be open — finalized or cancelled bounties will revert
- There is no limit to the number of claims per bounty; the issuer picks the best one

---

## Part 6: Withdrawing Funds

After winning a bounty as claimant, funds are credited to `pendingWithdrawals` and must be explicitly collected. The bounty payout minus the 2.5% protocol fee is available immediately after `acceptClaim` or `resolveVote` finalizes.

### Check Pending Balance

```bash
cast call $POIDH_CONTRACT_ADDRESS \
  "pendingWithdrawals(address)(uint256)" \
  <YOUR_ADDRESS> \
  --rpc-url $RPC_URL
```

### Withdraw to Your Own Address

```bash
cast send $POIDH_CONTRACT_ADDRESS \
  "withdraw()" \
  --private-key $PRIVATE_KEY \
  --rpc-url $RPC_URL
```

### Withdraw to a Different Address

```bash
cast send $POIDH_CONTRACT_ADDRESS \
  "withdrawTo(address)" \
  <RECIPIENT_ADDRESS> \
  --private-key $PRIVATE_KEY \
  --rpc-url $RPC_URL
```

> `withdraw()` sends the entire pending balance in one call. Check balance first to confirm funds are available before sending the transaction.

---

## Agent Decision Flow

### Posting a Bounty

1. Ask for: **name**, **description**, **amount** (ETH on Arbitrum/Base, DEGEN on Degen Chain), **type** (solo or open — default solo)
2. Confirm with user before sending — this spends real ETH (or DEGEN on Degen Chain)
3. Run `createSoloBounty` or `createOpenBounty`
4. Return tx hash and `$POIDH_BASE_URL/bounty/<bountyId + $POIDH_V2_OFFSET>`

### Submitting a Claim

1. Ask for: **bounty ID**, **proof URI** (image, link, IPFS hash, etc.), **claim name**, **claim description**
2. Verify the bounty is active and has no ongoing vote
3. Confirm the agent's wallet is not the bounty issuer
4. Confirm with user before sending
5. Call `createClaim(bountyId, name, description, uri)`
6. Return the claim ID and tx hash

### Evaluating and Accepting

1. Ask for the **bounty ID**
2. Check `everHadExternalContributor` to determine the correct acceptance path
3. Fetch all active (non-accepted) claims via `getClaimsByBountyId`
4. For each claim: get `tokenURI`, resolve URI, evaluate content using the appropriate tool (vision for images, web fetch for links, etc.)
5. Present recommended winner + reasoning to user, confirm before transacting
6. **Solo / no external contributors**: `acceptClaim(bountyId, claimId)`
7. **Open with external contributors**: `submitClaimForVote(bountyId, claimId)`, inform user contributors have 2 days to vote, then `resolveVote` after deadline

---

## Native Token Amount Reference

| Human amount | Cast value   |
| ------------ | ------------ |
| 0.001 ETH    | `0.001ether` |
| 0.01 ETH     | `0.01ether`  |
| 1 ETH        | `1ether`     |
| 1000 DEGEN   | `1000ether`  |
| 10 DEGEN     | `10ether`    |

> `cast` uses `ether` as a unit label for any 18-decimal token. On Degen Chain, this means DEGEN, not ETH.

---

## Fee Note

PoidhV3 takes a **2.5% fee** on accepted claim payouts, deducted only at acceptance. The full `msg.value` is held in escrow until then. The fee is paid in the chain's native token — ETH on Arbitrum and Base, DEGEN on Degen Chain.

---

## Error Reference

| Error                             | Cause                                              | Fix                                                                  |
| --------------------------------- | -------------------------------------------------- | -------------------------------------------------------------------- |
| `ContractsCannotCreateBounties()` | Wallet is a smart contract                         | Use an EOA private key                                               |
| `MinimumBountyNotMet()`           | Amount below `MIN_BOUNTY_AMOUNT`                   | Increase `--value` (0.001 ETH on Arbitrum/Base, 1000 DEGEN on Degen) |
| `MinimumContributionNotMet()`     | Contribution below `MIN_CONTRIBUTION`              | Increase `--value` when joining open bounty                          |
| `NoEther()`                       | `--value` was 0 or omitted                         | Add `--value`                                                        |
| `WrongCaller()`                   | Not the bounty issuer                              | Use the issuer's private key                                         |
| `VotingOngoing()`                 | Active vote in progress                            | Wait for deadline, then `resolveVote`                                |
| `VotingEnded()`                   | Deadline passed without resolution                 | Call `resolveVote`                                                   |
| `NotSoloBounty()`                 | Open bounty with contributors tried direct accept  | Use `submitClaimForVote` instead                                     |
| `ClaimAlreadyAccepted()`          | Claim was already accepted                         | Nothing to do                                                        |
| `BountyClaimed()`                 | Bounty already finalized                           | Nothing to do                                                        |
| `BountyClosed()`                  | Bounty was cancelled                               | Nothing to do                                                        |
| `BountyNotFound()`                | Invalid bounty ID                                  | Check bounty ID                                                      |
| `ClaimNotFound()`                 | Invalid claim ID                                   | Check claim ID                                                       |
| `IssuerCannotClaim()`             | Issuer tried to submit a claim on their own bounty | Different wallet must claim                                          |
| `NotActiveParticipant()`          | Caller is not a participant or has withdrawn       | Must be an active contributor                                        |
| `MaxParticipantsReached()`        | Open bounty has 150 contributors                   | Wait for a slot to free up                                           |
| `NothingToWithdraw()`             | No pending balance                                 | Check `pendingWithdrawals(address)` first                            |
| `VoteWouldPass()`                 | Tried to reset a vote that would pass              | Cannot override a winning vote                                       |
