# SOMA Quickstart Code Patterns

> Quickstart repo: https://github.com/soma-org/quickstart
> Quickstart guide: https://docs.soma.org/getting-started/quickstart
> Model development: https://docs.soma.org/guides/model-development

## Quickstart Repo File Map

The quickstart repo (`github.com/soma-org/quickstart`) contains production-ready code for forking and modification. Key files:

| File | Purpose | When to fork/modify |
|------|---------|-------------------|
| `src/quickstart/submitter.py` | Full data submission pipeline on Modal (L4 GPU). Streams Stack v2, scores, uploads to S3, submits on-chain. Deploys as 24h cron. | Changing data source, filtering logic, target selection strategy, or scoring parameters |
| `src/quickstart/training.py` | Complete train-commit-reveal loop on Modal (H100). Supports both PyTorch and Flax. Includes localnet mode for testing. Auto-deploys cron for reveals every 6h. | Changing training hyperparameters, data pipeline, checkpoint schedule, or adding custom training logic |
| `src/quickstart/train_torch.py` | Standalone PyTorch training reference (no commit/reveal). Simpler entry point for understanding the training loop. | Learning the training loop before customizing `training.py` |
| `src/quickstart/train_flax.py` | Standalone Flax/JAX training reference. | Using Flax instead of PyTorch |
| `src/quickstart/common.py` | Shared utilities: training state management, checkpoint helpers, S3 upload, artifact saving. Used by all other modules. | Adding new state fields, changing checkpoint format, or modifying S3 upload logic |
| `src/quickstart/settle_targets.py` | Claim rewards from settled targets. Runnable locally with `uv run claim`. | Automating reward claiming or adding claim filters |
| `src/quickstart/localnet.py` | Helpers for running a SOMA localnet inside Modal (start localnet, weights server). | Customizing localnet test environment |
| `src/quickstart/create_modal_secret.py` | Push `.env` credentials to Modal as a secret group. | Adding new environment variables |
| `.env.example` | Template for all required environment variables. | Setting up a new environment |
| `pyproject.toml` | Project dependencies and script entrypoints. | Adding new dependencies or CLI commands |

### Forking the quickstart

```bash
git clone https://github.com/soma-org/quickstart
cd quickstart
cp .env.example .env
# Fill in .env with your credentials (see Getting Started in SKILL.md)
uv sync
```

**Common modifications:**
- **Change data source**: Edit `stream_stack_v2()` in `submitter.py` — replace with your dataset or custom data generator
- **Change training config**: Edit constants at the top of `training.py` (`LEARNING_RATE`, `DROPOUT_RATE`, `GRAD_ACCUM_STEPS`, etc.)
- **Add domain filtering**: Add filtering logic after data download in `submitter.py` or `training.py`'s `make_batches()`
- **Change GPU type**: Edit the `gpu=` parameter in Modal function decorators (e.g., `gpu="A100"` instead of `gpu="H100"`)
- **Change cron schedule**: Edit `modal.Cron("0 */6 * * *")` in `training.py` reveal function

## Environment Setup

### Prerequisites
- Python 3.13+
- `uv` package manager
- Modal account (GPU orchestration)
- SOMA binary (via `sup install soma`)

### .env Configuration

```
SOMA_SECRET_KEY=<ed25519 secret key from `soma wallet export`>
HF_TOKEN=<HuggingFace token for gated datasets>
S3_BUCKET=<bucket name>
S3_ACCESS_KEY_ID=<access key>
S3_SECRET_ACCESS_KEY=<secret key>
S3_ENDPOINT_URL=https://<account-id>.r2.cloudflarestorage.com
S3_PUBLIC_URL=https://<public-bucket-url>
```

### Modal Secrets Setup

```python
# Push .env to Modal as a secret group
# Run: python -m quickstart.create_modal_secret
from modal import Secret
import dotenv

env = dotenv.dotenv_values(".env")
Secret.create_or_update("soma-secrets", env)
```

## Data Submission Pattern

The core submission loop from `submitter.py`:

```python
from soma_sdk import SomaClient, Keypair

async def score_and_submit():
    client = await SomaClient(chain="testnet")
    kp = Keypair.from_secret_key(os.environ["SOMA_SECRET_KEY"])

    # 1. Get open targets
    targets = await client.get_targets(status="open")

    for target in targets:
        # 2. Get model manifests for this target
        manifests = await client.get_model_manifests(target)

        # 3. Get candidate data
        data = get_next_data()  # your data source
        data_url = f"http://localhost:9125/{filename}"

        # 4. Score locally
        result = await client.score(
            data_url, manifests, target.embedding, data
        )

        # 5. Check if hit
        if result.distance <= target.distance_threshold:
            # 6. Upload to S3
            public_url = upload_to_s3(data, filename)

            # 7. Submit on-chain
            checksum = SomaClient.commitment(data)
            await client.submit_data(
                kp,
                target.id,
                data,
                public_url,
                manifests[result.winner].model_id,
                result.embedding,
                result.distance,
                result.loss_score,
            )
```

### Data Streaming from The Stack v2

```python
from datasets import load_dataset
import io, smart_open

def stream_stack_v2():
    ds = load_dataset(
        "bigcode/the-stack-v2-train-smol-ids",
        streaming=True, split="train"
    )
    shuffled = ds.shuffle(buffer_size=1_000_000)

    for row in shuffled:
        blob_id = row["blob_id"]
        src = row["src_encoding"]
        url = f"s3://softwareheritage/content/{blob_id}"

        with smart_open.open(url, "rb", transport_params={"client": s3}) as f:
            content = f.read()

        text = content.decode("utf-8", errors="replace").strip()
        if not text or len(text) > 10_000:
            continue

        yield text.encode("utf-8")
```

### S3 Upload Pattern

```python
import boto3

def upload_to_s3(data: bytes, key: str) -> str:
    s3 = boto3.client(
        "s3",
        endpoint_url=os.environ["S3_ENDPOINT_URL"],
        aws_access_key_id=os.environ["S3_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["S3_SECRET_ACCESS_KEY"],
    )
    bucket = os.environ["S3_BUCKET"]
    s3.put_object(Bucket=bucket, Key=key, Body=data)
    return f"{os.environ['S3_PUBLIC_URL']}/{key}"
```

## Training Pattern

### PyTorch Training Loop

```python
from soma_models.v1.torch.modules.model import Model
from soma_models.v1.torch.modules.sig_reg import SIGReg
from soma_models.v1.torch.loss import compute_loss
from soma_models.v1.configs import ModelConfig, SIGRegConfig
from soma_models.v1.tokenizer import tokenize

LEARNING_RATE = 1e-4
DROPOUT_RATE = 0.1
MICRO_BATCH_SIZE = 2
GRAD_ACCUM_STEPS = 64   # Effective batch size = 128

def train(steps: int):
    device = "cuda" if torch.cuda.is_available() else "cpu"
    config = ModelConfig(dropout_rate=DROPOUT_RATE)
    model = Model(config).to(device)
    sig_reg = SIGReg(SIGRegConfig()).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)

    for step, (token_ids, targets) in enumerate(make_batches(MICRO_BATCH_SIZE)):
        if step >= steps:
            break

        token_ids = torch.tensor(token_ids, device=device)
        targets = torch.tensor(targets, device=device)
        loss, embedding = compute_loss(model, sig_reg, token_ids, targets)
        (loss / GRAD_ACCUM_STEPS).backward()

        if (step + 1) % GRAD_ACCUM_STEPS == 0:
            optimizer.step()
            optimizer.zero_grad()

    # Save checkpoint + artifacts for commit
    embedding_flat = embedding.detach().cpu().numpy().flatten().tolist()
    weights_bytes = model.save_bytes()
    return embedding_flat, weights_bytes
```

### Flax/JAX Training Loop

```python
from soma_models.v1.flax.modules.model import Model
from soma_models.v1.flax.modules.sig_reg import SIGReg
from soma_models.v1.flax.loss import compute_loss
from flax import nnx
import optax, jax, jax.numpy as jnp

def train_flax(steps: int):
    config = ModelConfig(dropout_rate=DROPOUT_RATE)
    model = Model(config, rngs=nnx.Rngs(0))
    sig_reg = SIGReg(SIGRegConfig(), rngs=nnx.Rngs(0))
    optimizer = nnx.Optimizer(model, optax.adam(LEARNING_RATE))

    @nnx.jit
    def micro_step(model, sig_reg, optimizer, token_ids, targets):
        def loss_fn(model):
            return compute_loss(model, sig_reg, token_ids, targets)
        loss, grads = nnx.value_and_grad(loss_fn)(model)
        # Scale and accumulate gradients
        return loss

    for step, (token_ids, targets) in enumerate(make_batches(MICRO_BATCH_SIZE)):
        if step >= steps:
            break
        token_ids = jnp.array(token_ids)
        targets = jnp.array(targets)
        loss = micro_step(model, sig_reg, optimizer, token_ids, targets)
```

### Batch Creation from The Stack v2

```python
from soma_models.v1.tokenizer import tokenize

SHUFFLE_BUFFER = 100_000

def make_batches(batch_size: int):
    ds = load_dataset(
        "bigcode/the-stack-v2-train-smol-ids",
        streaming=True, split="train"
    ).shuffle(buffer_size=SHUFFLE_BUFFER)

    batch_ids, batch_targets = [], []
    for row in ds:
        content = download_content(row)
        seq = tokenize(content)
        batch_ids.append(seq.token_ids)
        batch_targets.append(seq.targets)
        if len(batch_ids) == batch_size:
            yield batch_ids, batch_targets
            batch_ids, batch_targets = [], []
```

## Commit-Reveal Cycle

### Commit (after training)

```python
async def do_commit(embedding, weights_bytes, model_id=None):
    client = await SomaClient(chain="testnet")
    kp = Keypair.from_secret_key(os.environ["SOMA_SECRET_KEY"])

    # Encrypt weights
    encrypted, decryption_key = SomaClient.encrypt_weights(weights_bytes)

    # Upload encrypted weights to S3
    weights_url = upload_to_s3(encrypted, f"weights/epoch-{epoch}.enc")

    # Create model if first time
    if model_id is None:
        model_id = await client.create_model(
            kp,
            commission_rate=1000,   # 10%
            stake_amount=None       # uses all available balance
        )

    # Commit on-chain
    await client.commit_model(
        kp, model_id, weights_url, encrypted,
        decryption_key, embedding
    )

    # Save state for reveal
    state = {
        "model_id": model_id,
        "decryption_key": decryption_key,
        "embedding": embedding,
        "commit_epoch": (await client.get_epoch()).epoch,
    }
    return state
```

### Reveal (next epoch)

```python
async def do_reveal(state):
    client = await SomaClient(chain="testnet")
    kp = Keypair.from_secret_key(os.environ["SOMA_SECRET_KEY"])

    current_epoch = (await client.get_epoch()).epoch
    if current_epoch <= state["commit_epoch"]:
        print("Epoch hasn't advanced yet — run this again after the epoch advances.")
        return

    await client.reveal_model(
        kp,
        state["model_id"],
        state["decryption_key"],
        state["embedding"],
    )
```

## Reward Claiming

```python
async def claim_all_rewards():
    client = await SomaClient(chain="testnet")
    kp = Keypair.from_secret_key(os.environ["SOMA_SECRET_KEY"])

    targets = await client.get_targets(status="claimable")
    for target in targets:
        await client.claim_rewards(kp, target.id)
        print(f"Claimed rewards for target {target.id}")

    balance = await client.get_balance(kp.address())
    print(f"Balance: {balance} SOMA")
```

## Modal Deployment

### GPU Image Setup

```python
import modal

gpu_image = (
    modal.Image.debian_slim(python_version="3.13")
    .pip_install(
        "soma-sdk>=0.1.7", "soma-models[torch]>=0.1.7",
        "datasets", "torch", "boto3", "aiohttp",
    )
)

cpu_image = modal.Image.debian_slim(python_version="3.13").pip_install(
    "soma-sdk>=0.1.7", "boto3", "python-dotenv",
)

app = modal.App("soma-training")
vol = modal.Volume.from_name("soma-training-vol", create_if_missing=True)
```

### Scheduled Reveal (cron)

```python
@app.function(
    image=cpu_image,
    secrets=[modal.Secret.from_name("soma-secrets")],
    volumes={"/training": vol},
    schedule=modal.Cron("0 */6 * * *"),  # Every 6 hours
    timeout=600,
)
async def reveal():
    state = load_training_state("/training")
    if state.get("pending_reveal"):
        await do_reveal(state)
        # Trigger next training round
        train_and_commit.remote()
```

## Localnet Testing

```python
import subprocess

def start_localnet():
    proc = subprocess.Popen(
        ["soma", "start", "localnet", "--force-regenesis"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    # Wait for services to be healthy
    for _ in range(60):
        try:
            client = await SomaClient(chain="localnet")
            epoch = await client.get_epoch()
            if epoch.epoch >= 0 and await client.scoring_health():
                return proc
        except:
            time.sleep(1)
    raise RuntimeError("Localnet failed to start")

# Force epoch advance (localnet only)
await client.advance_epoch()
```

## Checkpoint Management

```python
import json, pathlib

def save_training_state(model_dir: str, state: dict):
    path = pathlib.Path(model_dir) / "training_state.json"
    path.write_text(json.dumps(state, indent=2))

def load_training_state(model_dir: str) -> dict:
    path = pathlib.Path(model_dir) / "training_state.json"
    if path.exists():
        return json.loads(path.read_text())
    return {
        "model_id": None, "step": 0, "pending_reveal": False,
        "commit_epoch": None, "decryption_key": None,
        "weights_url": None, "embedding": None, "framework": "torch",
    }

def find_latest_checkpoint(model_dir: str, prefix="checkpoint"):
    checkpoints = sorted(pathlib.Path(model_dir).glob(f"{prefix}-*"))
    return checkpoints[-1] if checkpoints else None

def save_training_artifacts(checkpoint_dir, embedding, weights_bytes):
    pathlib.Path(checkpoint_dir / "embedding.json").write_text(
        json.dumps(embedding)
    )
    pathlib.Path(checkpoint_dir / "weights.bin").write_bytes(weights_bytes)
```

## Network Analysis Pattern

Analyze the competitive landscape before making strategic decisions:

```python
import numpy as np
from scipy.spatial.distance import cdist
from soma_sdk import SomaClient

async def analyze_network():
    client = await SomaClient(chain="testnet")

    # 1. Map all active models
    models = await client.get_active_models()
    embeddings = np.array([m.embedding for m in models])
    stakes = np.array([m.stake for m in models])

    print(f"Active models: {len(models)}")
    print(f"Total stake: {sum(stakes)}")

    # 2. Find model clusters and isolated models
    if len(embeddings) > 1:
        distances = cdist(embeddings, embeddings, metric='cosine')
        for i, model in enumerate(models):
            nearby = sum(1 for d in distances[i] if 0 < d < 0.3)
            print(f"  {model.model_id}: stake={model.stake}, "
                  f"nearby={nearby}, commission={model.commission_rate}")

    # 3. Map targets and find opportunities
    targets = await client.get_targets(status="open")
    if targets and len(embeddings) > 0:
        target_embs = np.array([t.embedding for t in targets])
        target_model_dists = cdist(target_embs, embeddings, metric='cosine')
        nearest_dist = target_model_dists.min(axis=1)

        print(f"\nOpen targets: {len(targets)}")
        # Sort by opportunity (high threshold + far from models)
        opportunities = sorted(
            zip(targets, nearest_dist),
            key=lambda x: x[0].distance_threshold * x[1],
            reverse=True,
        )
        for target, dist in opportunities[:10]:
            print(f"  Target {target.id}: "
                  f"reward={target.reward_pool}, "
                  f"threshold={target.distance_threshold:.3f}, "
                  f"nearest_model={dist:.3f}, "
                  f"assigned={len(target.model_ids)}")
```

## Domain Gap Detection Pattern

Find embedding regions with targets but few or no models — the highest-value opportunities:

```python
async def find_domain_gaps(threshold: float = 0.5):
    client = await SomaClient(chain="testnet")
    models = await client.get_active_models()
    targets = await client.get_targets(status="open")

    if not models or not targets:
        print("No models or targets to analyze")
        return []

    model_embs = np.array([m.embedding for m in models])
    target_embs = np.array([t.embedding for t in targets])

    # Distance from each target to nearest model
    dists = cdist(target_embs, model_embs, metric='cosine')
    nearest = dists.min(axis=1)

    # Gaps: targets far from any model
    gaps = []
    for i, target in enumerate(targets):
        if nearest[i] > threshold:
            gaps.append({
                "target": target,
                "nearest_model_dist": nearest[i],
                "reward_pool": target.reward_pool,
                "distance_threshold": target.distance_threshold,
            })

    gaps.sort(key=lambda g: g["reward_pool"], reverse=True)
    for gap in gaps:
        t = gap["target"]
        print(f"GAP: target {t.id}, reward={t.reward_pool}, "
              f"threshold={t.distance_threshold:.3f}, "
              f"nearest_model={gap['nearest_model_dist']:.3f}")
    return gaps
```

## Competitor Analysis Pattern

Download and evaluate a competitor's model to understand their strengths:

```python
from soma_models.v1.torch.modules.model import Model
from soma_models.v1.torch.modules.sig_reg import SIGReg
from soma_models.v1.torch.loss import compute_loss
from soma_models.v1.configs import ModelConfig, SIGRegConfig
from soma_models.v1.tokenizer import tokenize
import torch

async def analyze_competitor(competitor_model_id: str, test_data: list[bytes]):
    client = await SomaClient(chain="testnet")

    # Download competitor weights
    weights_bytes = await client.fetch_model(competitor_model_id)
    model = Model.load_bytes(weights_bytes)
    model.eval()
    sig_reg = SIGReg(SIGRegConfig())

    # Evaluate on your test data
    results = []
    for data in test_data:
        seq = tokenize(data)
        with torch.no_grad():
            loss, embedding = compute_loss(
                model, sig_reg,
                torch.tensor([seq.token_ids]),
                torch.tensor([seq.targets]),
            )
        results.append({"loss": loss.item(), "data_size": len(data)})

    avg_loss = sum(r["loss"] for r in results) / len(results)
    print(f"Competitor {competitor_model_id}: avg_loss={avg_loss:.4f} "
          f"across {len(results)} samples")
    return results
```

## Epoch Review Pattern

Analyze your results after each epoch to adapt your strategy:

```python
from soma_sdk import SomaClient, Keypair
import os

async def epoch_review(my_model_id: str):
    client = await SomaClient(chain="testnet")
    kp = Keypair.from_secret_key(os.environ["SOMA_SECRET_KEY"])

    # Current state
    epoch = await client.get_epoch()
    balance = await client.get_balance(kp.address())
    print(f"Epoch: {epoch.epoch}, Balance: {balance} SOMA")

    # Check claimable targets (wins from previous epochs)
    claimable = await client.get_targets(status="claimable")
    my_wins = [t for t in claimable if t.winning_model_id == my_model_id]
    total_rewards = sum(t.reward_pool for t in my_wins)
    print(f"Claimable wins: {len(my_wins)}, total rewards: {total_rewards}")

    # Competitive landscape
    models = await client.get_active_models()
    my_model = next((m for m in models if m.model_id == my_model_id), None)
    if my_model:
        print(f"My stake: {my_model.stake}, commission: {my_model.commission_rate}")

    # Open targets for next epoch
    open_targets = await client.get_targets(status="open")
    print(f"Open targets: {len(open_targets)}")

    # Claim rewards
    for target in my_wins:
        await client.claim_rewards(kp, target.id)
        print(f"Claimed target {target.id}")
```

## Configuration Constants

| Constant | Value | Purpose |
|----------|-------|---------|
| `LEARNING_RATE` | 1e-4 | Adam optimizer LR |
| `DROPOUT_RATE` | 0.1 | Model dropout |
| `MICRO_BATCH_SIZE` | 2 | Batch per forward pass |
| `GRAD_ACCUM_STEPS` | 64 | Steps before optimizer update |
| Effective batch size | 128 | MICRO_BATCH_SIZE * GRAD_ACCUM_STEPS |
| `SHUFFLE_BUFFER` | 100,000 | Dataset shuffle buffer |
| `LOG_EVERY` | 10 | Steps between log outputs |
| Checkpoint interval | 500 | Steps between checkpoints |
| Reveal cron | Every 6 hours | Modal cron schedule |
| Commission rate | 1000 (10%) | Default model commission |
