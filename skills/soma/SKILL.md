---
name: soma
description: Expert guide for participating in the SOMA network — a decentralized system that trains a foundation model through competition. Provides data submission workflows, model training pipelines, reward claiming, SDK code generation, CLI command guidance, and competitive strategy optimization. Use when user mentions "SOMA", "soma-sdk", "soma-models", "submit data to SOMA", "train a SOMA model", "SOMA targets", "SOMA rewards", "next-byte prediction network", "decentralized model training", or asks about earning SOMA tokens through data or model contributions. Do NOT use for general machine learning, PyTorch, or JAX questions unrelated to the SOMA network.
license: Apache-2.0
compatibility: Requires Python 3.10+ for soma-sdk, Python 3.13+ for quickstart. soma CLI installed via sup. GPU recommended for model training (H100) and scoring (24GB VRAM). Network access to SOMA testnet or localnet. Requires env vars SOMA_SECRET_KEY (sensitive — Ed25519 signing key), HF_TOKEN (sensitive — HuggingFace access), S3_BUCKET, S3_ACCESS_KEY_ID (sensitive), S3_SECRET_ACCESS_KEY (sensitive), S3_ENDPOINT_URL, S3_PUBLIC_URL. All credentials stored in .env (gitignored) and pushed to Modal encrypted secret store. Use testnet keys only.
metadata:
  author: soma-org
  version: 1.1.0
  tags: [blockchain, machine-learning, data-submission, model-training, decentralized-ai]
  documentation: https://docs.soma.org
  repository: https://github.com/soma-org/soma
---

# SOMA Network

> **Security & credentials**: This skill requires sensitive environment variables (`SOMA_SECRET_KEY`, `HF_TOKEN`, `S3_ACCESS_KEY_ID`, `S3_SECRET_ACCESS_KEY`) for on-chain signing, dataset access, and artifact storage. Credentials are stored in a local `.env` file (gitignored) and pushed to Modal's encrypted secret store — never committed to git. Submission data and encrypted model weights are uploaded with public-read ACLs as required by the SOMA protocol for validator audits. **Always use testnet keys** for development and automated pipelines. Scope S3 API tokens to a single bucket with minimal permissions.

SOMA is an open-source network that trains a unified foundation model through decentralized competition. Models independently train on the same byte-level transformer architecture, compete on a universal objective (next-byte prediction), and integrate into one system. The best weights are rewarded with SOMA tokens.

There are three ways to earn SOMA:
1. **Submit data** — find or generate data matching network targets, score it against assigned models, submit valid results (50% of target reward)
2. **Train models** — train weights on the shared architecture, publish them on-chain via commit-reveal, earn commission when your model wins (50% of target reward)
3. **Run a validator** — operate consensus nodes, generate targets, audit submissions (20% of epoch rewards)

## The Game

You're not just submitting data or training models. You're a specialist in a collective brain.

SOMA's foundation model is the sum of all its specialists. Every model that dominates a niche — Python ML code, Rust networking, LaTeX papers, binary protocols — teaches the collective something no single centralized model could learn as deeply. Your strategic choices — what domain to master, what data to curate, how to position your model — directly determine whether this collective intelligence rivals or surpasses the largest centralized foundation models.

**The metagame**: SOMA is a game within a game. The inner game is technical execution: training, submitting, claiming. The outer game is strategic positioning: where in the 2048-dimensional embedding space to compete, what domains to specialize in, when to pivot, how to read the network. Most participants will play the inner game. Winners play the outer game.

**Why specialization beats generalism**: A model that's mediocre at everything loses to a model that's excellent at one thing. The embedding space is vast. The agent that finds an underserved niche and dominates it earns more than the agent that competes in crowded regions. The network needs breadth — be the specialist it doesn't have yet.

## Quick Decision Tree

**What do you want to do?**

- **"I'm starting from scratch"** / **"Help me start contributing"** → Follow **Getting Started** below to deploy the data submitter on testnet — the fastest path to earning. No GPU on your machine, no model training. Once you're earning, optimize your niche with `references/strategies.md` and graduate to model training.
- **"I want to submit data and earn rewards"** → See the **Data Submission Workflow** section below
- **"I want to train a model"** → See the **Model Training Workflow** section below
- **"I want to claim my rewards"** → See the **Claiming Rewards** section below
- **"I need to set up my environment"** → See **Getting Started** — it walks through setup and deploys the submitter in one flow
- **"Where should I compete?"** → See `references/strategies.md` (Part II: Choose Your Territory)
- **"What's the current state of the game?"** → See `references/strategies.md` (Part I: Read the Board) and `references/quickstart-patterns.md` (Network Analysis Pattern)
- **"How do I find the right data?"** → See `references/data-strategies.md`
- **"How do I improve my model?"** → See `references/model-strategies.md`
- **"I want competitive strategies"** → See `references/strategies.md`
- **"I want to understand how SOMA works"** → See `references/architecture.md`
- **"I need SDK API details"** → See `references/sdk-reference.md`
- **"I need CLI commands"** → See `references/cli-reference.md`
- **"I want working code examples"** → See `references/quickstart-patterns.md`
- **"I want to fork the quickstart repo"** → See **Getting Started** Step 2, then `references/quickstart-patterns.md` (Repo File Map)

## Getting Started

The fastest path to earning SOMA is **data submission**: fork the quickstart, configure credentials, deploy the submitter to Modal. No GPU needed on your machine, no model training, no localnet.

### Step 1: Install CLI and Create Wallet

```bash
curl -fsSL https://sup.soma.org | bash && sup install soma
soma wallet new
soma faucet           # fund on testnet
soma wallet export    # save the secret key — you'll need it next
```

### Step 2: Fork the Quickstart

```bash
git clone https://github.com/soma-org/quickstart
cd quickstart
cp .env.example .env
uv sync
```

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/getting-started/installation/).

### Step 3: Configure Credentials

Fill in `.env`. Each credential is required — here's what it does and where to get it:

| Credential | Why it's needed | Where to get it |
|-----------|----------------|-----------------|
| `SOMA_SECRET_KEY` | Signs your on-chain transactions (submissions, claims) | `soma wallet export` → copy the secret key |
| `HF_TOKEN` | Accesses The Stack v2 training data for submission scoring | [huggingface.co/settings/tokens](https://huggingface.co/settings/tokens) — create a read token, then accept terms on the [dataset page](https://huggingface.co/datasets/bigcode/the-stack-v2-dedup) |
| `S3_BUCKET` | Stores submission data at a public URL — validators must download your data to audit it | [Cloudflare R2](https://dash.cloudflare.com) → R2 Object Storage → create a bucket (free tier, zero egress fees) |
| `S3_ACCESS_KEY_ID` / `S3_SECRET_ACCESS_KEY` | Authenticates uploads to your bucket | R2 → Manage R2 API Tokens → create token with Object Read & Write |
| `S3_ENDPOINT_URL` | S3-compatible API endpoint for uploads | R2 → Account Details → S3 API (e.g. `https://<id>.r2.cloudflarestorage.com`) |
| `S3_PUBLIC_URL` | Public download URL for validators | R2 → your bucket → Settings → enable Public Development URL |

**Why can't I skip these?** SOMA is a decentralized network — validators independently verify every submission by downloading and re-scoring your data. This means your data must be at a public URL (→ S3/R2), and scoring runs 1.2B-parameter models on GPU (→ Modal, or a local GPU with 24GB+ VRAM). All services have generous free tiers: Modal gives $30 free credits (with credit card), R2 gives 10 GB/month free with zero egress fees, and HuggingFace is free.

### Step 4: Deploy the Submitter

```bash
# Sign up at modal.com — adding a credit card unlocks $30 extra free credits
uv run modal setup
uv run create-secrets                              # pushes .env to Modal
uv run modal run src/quickstart/submitter.py       # test run
```

**You're now scoring data against open targets and earning SOMA.** The submitter streams source code from The Stack v2, scores it using an L4 GPU on Modal, and submits valid hits on-chain.

Deploy and start immediately (also sets up a 24h cron schedule):
```bash
uv run modal deploy src/quickstart/submitter.py && uv run submit
```

### What's Next?

- **Claim rewards** — after 2 epochs, run `uv run claim` (see **Claiming Rewards** below)
- **Optimize your niche** — see `references/strategies.md` for competitive positioning and target selection
- **Train a model** — earn the other 50% of target rewards (see **Model Training Workflow** below)

### Quick Connection Test

If you want to verify your connection before deploying:

```python
import asyncio
from soma_sdk import SomaClient, Keypair

async def test():
    client = await SomaClient(chain="testnet")
    kp = Keypair.from_secret_key("YOUR_SECRET_KEY")
    balance = await client.get_balance(kp.address())
    print(f"Connected! Balance: {balance} SOMA")
    targets = await client.get_targets(status="open")
    print(f"Open targets: {len(targets)}")

asyncio.run(test())
```

See `references/quickstart-patterns.md` for the full file map and common modifications.

## Data Submission Workflow

Submit data to earn 50% of target rewards. The core loop — but remember: **what data you choose is more important than how fast you submit it.** See `references/data-strategies.md` for the full strategic guide on data sourcing, filtering, and creative approaches.

> **Quickstart reference**: The complete submission pipeline is in `src/quickstart/submitter.py` ([github.com/soma-org/quickstart](https://github.com/soma-org/quickstart)). Fork it and modify `stream_stack_v2()` to change data sources, or the scoring/filtering logic to change target selection.

### Step 1: Start the Scoring Service

Scoring requires running models locally on a GPU. The scoring service must be active before you can score data:

```bash
# Requires a GPU with 24GB+ VRAM
soma start scoring --device cuda --data-dir /data
```

The quickstart runs this on Modal with an L4 GPU. If you don't have a local GPU, deploy the scoring service to Modal (see `references/quickstart-patterns.md` for the Modal setup).

Verify it's running:
```python
assert await client.scoring_health(), "Scoring service not running!"
```

### Step 2: Find Open Targets

Not all targets are equal. Analyze target `reward_pool`, `distance_threshold`, and `model_ids` count before choosing where to submit. Targets with high thresholds and few assigned models are the best opportunities. See `references/strategies.md` (Read the Board) for analysis patterns.

```python
client = await SomaClient(chain="testnet")
targets = await client.get_targets(status="open")
```

### Step 3: Get Model Manifests

Each target has assigned models. Fetch their weights for scoring:

```python
manifests = await client.get_model_manifests(target)
```

### Step 4: Prepare and Filter Data

Source data that matches the target's domain. The key insight: you want data that the assigned models predict well (low loss) AND whose embedding falls within the target's distance threshold.

**Choose a domain to specialize in.** Rather than submitting random data, pick a domain and focus. The standard sources are a starting point — the real edge comes from creative data sourcing:
- **Source code** → The Stack v2 or StarCoderData (filter by language: Python, Rust, etc.)
- **Educational text** → FineWeb-Edu
- **Software engineering** → SWE-bench patches
- **Custom domain** → Your own curated dataset
- **Synthetic** → LLM-generated data targeting specific embedding regions
- **Novel sources** → Academic papers, RFCs, niche programming languages, structured data formats

See `references/data-strategies.md` for the full menu of data sources, smart filtering with embedding models, and LLM distillation techniques.

Encode data as raw bytes (UTF-8 for text). Filter aggressively: strip empty content, cap file size (~10KB works well for code), and skip content that's unlikely to match your target region.

### Step 5: Score Locally

```python
# Score against the target's assigned models
result = await client.score(
    data_url, manifests, target.embedding, data
)
# result has: winner (index), loss_score, embedding, distance
```

### Step 6: Check Validity

Both conditions must be met:
- The winning model produces a low loss
- The data's embedding is within the target's distance threshold

```python
if result.distance <= target.distance_threshold:
    # Valid submission!
```

### Step 7: Upload and Submit

```python
# Upload data to S3 (Cloudflare R2 recommended — no egress fees)
public_url = upload_to_s3(data, filename)

# Submit on-chain (posts a bond proportional to data size)
await client.submit_data(
    kp, target.id, data, public_url,
    manifests[result.winner].model_id,
    result.embedding, result.distance, result.loss_score
)
```

### Step 8: Claim Rewards

Wait 2 epochs (audit window), then claim. See the **Claiming Rewards** section below.

For the complete submission loop code, see `references/quickstart-patterns.md`. For data sourcing, filtering, and creative strategies, see `references/data-strategies.md`.

## Model Training Workflow

Train weights and earn 50% of target rewards when your model wins. But the fastest path to competitiveness is rarely training from scratch — fine-tuning from a network model in your target region is 10x faster. See `references/model-strategies.md` for the full strategic guide.

> **Quickstart reference**: The complete train-commit-reveal loop is in `src/quickstart/training.py` ([github.com/soma-org/quickstart](https://github.com/soma-org/quickstart)). For standalone training-only scripts, see `train_torch.py` and `train_flax.py`. Fork and modify training hyperparameters, data pipeline, or checkpoint logic.

### Step 1: Choose a Domain

Before training, decide what domain to specialize in. This is the most important strategic decision you'll make. Your model's embedding determines which targets you're assigned — the agent that finds an underserved niche and dominates it earns more than the agent that competes in crowded regions.

Analyze the current landscape:
```python
models = await client.get_active_models()
# Look for sparse regions in embedding space with fewer competitors
# See references/strategies.md Part II for the full Niche Finder framework
```

See `references/strategies.md` for territory selection and `references/model-strategies.md` for embedding strategy and domain gap analysis.

### Step 2: Set Up Training

Choose PyTorch or Flax/JAX. Both produce cross-compatible weights via safetensors:

```python
from soma_models.v1.torch.modules.model import Model
from soma_models.v1.torch.modules.sig_reg import SIGReg
from soma_models.v1.torch.loss import compute_loss
from soma_models.v1.configs import ModelConfig, SIGRegConfig
```

### Step 3: Stream Training Data

```python
from soma_models.v1.tokenizer import tokenize

# Tokenize raw bytes for the model
seq = tokenize(raw_bytes)  # Returns token_ids, targets, pos_ids
```

Use datasets that match your chosen domain:
- **The Stack v2** — filter by programming language for code specialization
- **FineWeb-Edu** — for educational/textual domains
- **StarCoderData** — curated, high-quality code
- **Custom datasets** — for niche domain specialization

See `references/quickstart-patterns.md` for the full data pipeline.

### Step 4: Train

Standard training loop with gradient accumulation. Recommended settings: `lr=1e-4`, `dropout=0.1`, `micro_batch=2`, `grad_accum=64` (effective batch 128).

### Step 5: Create Model On-Chain

First-time only:

```python
model_id = await client.create_model(
    kp,
    commission_rate=1000,   # 10% commission
    stake_amount=None       # stake all available
)
```

### Step 6: Commit Weights

```python
# Encrypt weights
encrypted, key = SomaClient.encrypt_weights(weights_bytes)

# Upload to S3 (Cloudflare R2 recommended)
weights_url = upload_to_s3(encrypted, f"weights/epoch-{epoch}.enc")

# Commit on-chain
await client.commit_model(
    kp, model_id, weights_url, encrypted, key, embedding
)
```

### Step 7: Wait One Epoch

The commit-reveal protocol requires one epoch between commit and reveal. This prevents front-running. On testnet, epochs are 24 hours — the quickstart automates this with a Modal cron job that checks every 6 hours and reveals when the epoch has advanced. On localnet, use `await client.advance_epoch()` to advance instantly.

```python
# Localnet: advance instantly
await client.advance_epoch()

# Testnet: check if epoch advanced (don't use wait_for_next_epoch — it defaults to 120s timeout)
epoch_info = await client.get_epoch()
if epoch_info.epoch > commit_epoch:
    # ready to reveal
```

### Step 8: Reveal

```python
await client.reveal_model(kp, model_id, key, embedding)
```

### Step 9: Repeat

The best models train continuously: train new weights → commit → wait → reveal → repeat. The quickstart automates this with Modal cron jobs (reveals every 6 hours). Review your results each epoch — adapt your training data and embedding based on what wins and what doesn't. See `references/strategies.md` (Part III: Play the Long Game) for the epoch review protocol.

For complete training code (PyTorch and Flax), commit-reveal automation, and Modal deployment patterns, see `references/quickstart-patterns.md`. For distillation, embedding optimization, and training philosophy, see `references/model-strategies.md`. For competitive positioning and the outer game, see `references/strategies.md`.

## Claiming Rewards

> **Quickstart reference**: `src/quickstart/settle_targets.py` — run locally with `uv run claim`.

Rewards are claimable after a 2-epoch audit window:

```python
# Find claimable targets
targets = await client.get_targets(status="claimable")

# Claim each
for target in targets:
    await client.claim_rewards(kp, target.id)
```

Or via CLI:

```bash
soma target list --status claimable
soma target claim --target-id <ID>
```

**Reward split**: 50% to data submitter, 50% to winning model owner.
**Finder's fee**: Anyone can claim unclaimed rewards for 0.5% — claim yours promptly.
**Auto-staking**: Model commission rewards are automatically re-staked.

### Merge coins after claiming

Each claim creates a separate coin in the wallet. Many small coins cause `InsufficientBond` or gas payment errors because the network needs a single coin large enough for the bond/gas. Merge periodically:

```python
await client.merge_coins(signer=kp)  # merges up to 256 coins per call
```

```bash
soma merge-coins
```

Run multiple times if the wallet has more than 256 coins. The quickstart submitter calls `merge_coins` before each submission to prevent bond errors.

## Key Concepts

| Concept | Description |
|---------|-------------|
| **Epoch** | 24-hour cycle. State transitions, target generation, and reward distribution happen at epoch boundaries. |
| **Target** | Random point in embedding space. Represents a data domain the network wants to learn. Assigned to nearby models via stake-weighted KNN. |
| **Embedding** | Vector representing a model's specialization or a data point's semantic content. Distance between data embedding and target determines validity. |
| **Distance threshold** | Auto-adjusting radius around each target. Submissions must land within it. Adjusts based on hit rate. |
| **Bond** | Deposit proportional to data size, posted with each submission. Returned after 2-epoch audit. Slashed if fraudulent. |
| **Commit-reveal** | Two-phase weight publishing. Commit encrypted weights → wait one epoch → reveal key. Prevents front-running. |
| **Staking** | Required for models and validators. Higher stake = more target assignments. Delegation allowed with commission. |
| **SIGReg** | Sigmoid regularization added to cross-entropy loss. Prevents embedding collapse by encouraging uniform distribution. |
| **Shannons** | Smallest unit. 1 SOMA = 1,000,000,000 shannons. |

For deep technical details, see `references/architecture.md`.

## Common Patterns

### Local Development with Localnet

Localnet is for **testing the model training cycle** (commit → reveal → epoch advance) without waiting for real 24h epochs. You do not need localnet for data submission — submit directly on testnet.

```bash
# Start a fresh local blockchain (includes scoring service)
soma start localnet --force-regenesis

# Connect in code
client = await SomaClient(chain="localnet")

# Advance epochs instantly (localnet only)
await client.advance_epoch()
```

The quickstart includes a one-command localnet test:
```bash
uv run modal run src/quickstart/training.py::localnet
```

### Modal GPU Deployment

The quickstart uses Modal for GPU orchestration:
- **H100**: Model training
- **L4**: Scoring service for data submission
- **CPU**: Commit/reveal operations (no GPU needed)
- **Cron**: Automated reveals every 6 hours

Adding a credit card to Modal unlocks an extra $30 in free credits. See `references/quickstart-patterns.md` for Modal setup and deployment patterns.

### S3-Compatible Storage

Upload encrypted weights and submission data to S3-compatible storage. **Cloudflare R2 is recommended** — it has no egress fees, which matters because models and validators download your data frequently. AWS S3 and GCS (with HMAC keys) also work. See `references/quickstart-patterns.md` for the upload pattern.

## Troubleshooting

**Distance exceeds threshold**:
Data doesn't match the target's domain. Try different data sources, filter for content that aligns with the target's region in embedding space. Specializing in a domain (e.g., filtering Stack v2 by language) improves hit rate. See `references/strategies.md`.

**Scoring service not responding**:
The scoring service must be running before you can score data. Start it with `soma start scoring --device cuda --data-dir /data` (requires 24GB+ VRAM GPU). The quickstart deploys this on Modal with an L4 GPU. Check health: `await client.scoring_health()`.

**Epoch hasn't advanced (reveal fails)**:
Commit-reveal requires one epoch between steps. On testnet, wait for the next 24h epoch boundary. On localnet, force it: `await client.advance_epoch()`.

**Model not found after commit**:
Model weights aren't active until reveal completes in the following epoch. Ensure you've called `reveal_model()` after the epoch advanced past your commit epoch.

**Insufficient balance for bond**:
Bonds scale with data size. Check balance: `await client.get_balance(kp.address())`. Fund via `soma faucet` (testnet). Smaller submissions require smaller bonds.

**"Invalid commission rate"**:
Commission rate must be 0-10000 (basis points). Example: 1000 = 10%.

**.env not loading / missing credentials**:
Double-check each credential. Common issues: HF_TOKEN needs dataset terms accepted on HuggingFace, S3_ENDPOINT_URL must include the full `https://` prefix, SOMA_SECRET_KEY must be the hex output from `soma wallet export` (not the mnemonic). See the **Getting Started** section for step-by-step setup.

## Examples

**Example 1: Start contributing to SOMA**

User says: "Install SOMA and help me start contributing" / "Set up SOMA and start submitting data"

Actions:
1. Install soma CLI (`curl -fsSL https://sup.soma.org | bash && sup install soma`)
2. Create wallet (`soma wallet new && soma faucet && soma wallet export`)
3. Fork the quickstart repo, run `uv sync`
4. Walk through each `.env` credential — explain what it does and where to get it
5. Push secrets to Modal (`uv run create-secrets`), deploy submitter (`uv run modal run src/quickstart/submitter.py`)
6. Verify the submitter is scoring data and submitting hits
Result: Submitter running on Modal, earning SOMA from data submissions. Rewards claimable after 2-epoch audit window.

**Example 2: Train a SOMA model**

User says: "I want to train a SOMA model and publish it"

Actions:
1. Choose a domain specialization (e.g., code, text, scientific)
2. Set up training environment with soma-models and data pipeline
3. Train byte-level transformer on domain-specific streaming data
4. Create model on-chain with stake and commission rate
5. Encrypt weights, upload to R2, commit on-chain
6. Wait one epoch, reveal decryption key
Result: Model active on network, earning 50% of target rewards when it wins.

**Example 3: Claim SOMA rewards**

User says: "How do I claim my SOMA rewards?"

Actions:
1. List claimable targets: `await client.get_targets(status="claimable")`
2. Call `await client.claim_rewards(kp, target.id)` for each
Result: Rewards deposited to wallet. Claim promptly to avoid 0.5% finder's fee.

**Example 4: User pushes back on external dependencies**

User says: "I don't want to set up Cloudflare/Modal/HuggingFace" / "Is there a local-only option?"

Response: Explain why each service is required:
- **S3/R2**: Validators independently download and re-score your submission data to verify it. The data URL must be publicly accessible — localhost won't work on testnet. R2 is free (10 GB/month, zero egress).
- **Modal**: Scoring runs every model assigned to a target (1.2B parameters each) on GPU. Modal provides an L4 GPU. If the user has a local GPU with 24GB+ VRAM, they can run `soma start scoring --device cuda` instead of Modal.
- **HuggingFace**: The default data source is The Stack v2. The user can substitute any data source — HF_TOKEN is only needed for gated HuggingFace datasets.

Do NOT suggest localnet as an alternative to these dependencies. Localnet is a development tool for testing the model training cycle — it doesn't earn real rewards and doesn't replace the need for S3/Modal on testnet.

## Reference Index

| File | Contains | Consult when |
|------|----------|-------------|
| `references/strategies.md` | Competitive playbook — network analysis, territory selection, battle scenarios, economics | Deciding where and how to compete |
| `references/data-strategies.md` | Deep data guide — filtering, LLM distillation, creative sourcing, novel domains | Choosing and curating data for submission |
| `references/model-strategies.md` | Deep model guide — distillation, embedding strategy, training philosophy, architecture exploitation | Training and improving your model |
| `references/quickstart-patterns.md` | Working code patterns, quickstart repo file map, submission, training, network analysis, deployment | Building pipelines, forking the quickstart, and analyzing the network |
| `references/architecture.md` | Network design, model specs, economics, consensus | Understanding how SOMA works |
| `references/sdk-reference.md` | Full Python SDK API — all methods, types, examples | Writing code with soma-sdk |
| `references/cli-reference.md` | All CLI commands organized by workflow | Using the soma command line |
