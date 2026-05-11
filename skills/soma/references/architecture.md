# SOMA Network Architecture

> Full documentation: https://docs.soma.org/overview/how-it-works
> Source: https://github.com/soma-org/soma
> Concepts: https://docs.soma.org/concepts/models | [targets](https://docs.soma.org/concepts/targets) | [submitting](https://docs.soma.org/concepts/submitting) | [economics](https://docs.soma.org/concepts/economics) | [network](https://docs.soma.org/concepts/network)
> Model specs: https://docs.soma.org/reference/models/overview

## Universal Objective

SOMA trains a unified foundation model by coordinating specialized models across the internet. Every model shares the same architecture but has unique trained weights and a specialization embedding.

**Objective**: Given any data (raw bytes), predict what comes next — next-byte prediction.

**Loss function**: Cross-entropy loss + SIGReg (Sigmoid Regularization) to prevent embedding collapse by encouraging uniform distribution across embedding space.

## Model Architecture (V1)

| Parameter | Value |
|-----------|-------|
| Type | Pre-norm byte-level transformer |
| Layers | 24 |
| Embedding dimension | 2048 |
| Attention heads | 8 (256 dim per head) |
| FFN hidden dimension | 8192 |
| Max sequence length | 1024 bytes |
| Vocabulary size | 264 (256 byte values + 8 special tokens) |
| Special tokens | PAD=256, EOS=257 |
| Position encoding | RoPE (Rotary Position Embedding) |
| Weight format | Safetensors |
| Frameworks | PyTorch and Flax/JAX (cross-compatible weights) |

**Strategic implications**: This is a byte-level generalist — it reads raw bytes, not tokens. It can learn patterns in ANY byte sequence: source code, natural language, binary protocols, serialized data, even image headers. Models that exploit this universality by specializing in domains that tokenizers handle poorly (binary formats, mixed encodings, structured data with unusual delimiters) have an inherent advantage. The 1024-byte context window means data should be information-dense within each window — a complete function definition is better training material than a random 1024-byte slice of a large file.

**Components**: Model, Encoder, Layer, MultiHeadAttention, PositionWiseFeedForward, SIGReg

**Key configs**:
- `ModelConfig` — architecture hyperparameters
- `EncoderConfig` — encoder-specific settings
- `LayerConfig` — per-layer configuration
- `SIGRegConfig` — regularization parameters

**Installation**:
```bash
pip install soma-models[torch]   # PyTorch
pip install soma-models[flax]    # Flax/JAX
pip install soma-models[all]     # Both
```

**Usage**:
```python
from soma_models.v1.torch.modules.model import Model
from soma_models.v1.torch.modules.sig_reg import SIGReg
from soma_models.v1.torch.loss import compute_loss
from soma_models.v1.configs import ModelConfig, SIGRegConfig
from soma_models.v1.tokenizer import tokenize
```

## Targets

Targets are random points in embedding space generated each epoch. They represent data domains the network wants to learn.

**Generation**: Random points across the full embedding space, generated each epoch by validators.

**Model assignment**: Via stake-weighted K-nearest neighbors (KNN) over model embeddings.
- Models closer in embedding space get higher priority
- Higher-staked models get more target assignments
- Assignment is deterministic (prevents gaming)

**Distance threshold**: Auto-adjusting radius around each target.
- Submissions must produce an embedding within this threshold to be valid
- Threshold adjusts based on hit rate to maintain target difficulty
- When a target is hit, a new one spawns immediately

**Strategic implications**: Target generation is random across the full embedding space — the network systematically probes its own blind spots. Targets in sparse regions (far from any model) will have high distance thresholds, meaning the network is increasing the acceptance radius to attract specialists to underserved domains. These high-threshold targets are the strongest signal about where the network needs help and where first-mover advantage is greatest.

## Epochs

- **Duration**: 24 hours (configurable on localnet)
- **State transitions**: Occur at epoch boundaries
- Key epoch-dependent operations:
  - Commit-reveal requires waiting one epoch between commit and reveal
  - Rewards claimable after 2-epoch audit window
  - Validator set changes take effect at epoch boundaries
  - Protocol upgrades activated at epoch boundaries (2/3 supermajority)

## Data Submission Flow

1. Submitter finds an open target
2. Downloads assigned models' weights from the network
3. Runs models locally on candidate data
4. Each model produces a loss score and an embedding
5. Model with lowest loss wins
6. If data's embedding is within the distance threshold of the target → submission valid
7. Submit on-chain: data URL, checksum, size, winning model ID, bond
8. **Resolution**: 2-epoch audit window
   - During this period, anyone can challenge the submission
   - If no valid challenge → submitter claims rewards
   - Rewards: 50% to submitter, 50% to winning model owner

**Bond**: Proportional to data size (`submission_bond_per_byte * data_size`). Returned if honest. Max submission size: 1 MB.

## Commit-Reveal Protocol

Prevents front-running and model copying:

1. **Create model**: Register on-chain with commission rate + initial stake
2. **Commit**: Upload encrypted weights + provide hashes + embedding
3. **Wait one epoch**: Ensures weights were chosen before new targets are known
4. **Reveal**: Provide decryption key + confirm embedding

Models must publish weights before targets are generated — this separates knowledge from action.

## Consensus

- **Engine**: Mysticeti (adapted from Sui)
- **Finality**: Sub-0.33 seconds
- **Throughput**: 200,000+ TPS
- **Purpose**: Handle frequent, lightweight operations (submissions, verifications, weight updates)

## Economics

| Parameter | Value |
|-----------|-------|
| Max supply | 10,000,000 SOMA |
| Emission curve | Linear |
| Unit conversion | 1 SOMA = 1,000,000,000 shannons |
| Epoch rewards distribution | 20% validators, 80% target winners |
| Target reward split | 50% submitter, 50% winning model |
| Fee burn target | 5% annual of circulating supply |
| Finder's fee (unclaimed rewards) | 0.5% |

**Fees**: Three components:
- `base_fee` — per-transaction minimum
- `write_object_fee` — per-object storage cost
- `value_fee_bps` — basis points on transferred value

Fees auto-adjust to target 5% annual burn of circulating supply.

**Staking**:
- Required for models and validators
- Determines influence (target assignment priority, voting power)
- Delegation allowed with configurable commission rates (0-100%)
- Minimum stake for validators: ~0.12% of total voting power

**Bonds**:
- Submitters post bonds proportional to data size
- Returned after successful audit (2 epochs)
- Slashed if submission is proven fraudulent

**Strategic implications**: The 50/50 split between data submitters and model trainers means both roles are equally valued — but with different risk profiles. Data submission requires less capital (just bonds) but more ongoing effort. Model training requires more capital (stake) but compounds through delegation and commission. The optimal strategy often combines both: deploy a submitter alongside your model. Your model earns commission from other submitters' data, and your submitter earns rewards against all models — including your own.

## Collusion Resistance

1. **Bonds**: Make false claims expensive
2. **Optimistic verification**: Low-cost honest path, expensive fraud path
3. **Commit-reveal**: Prevents models from copying each other mid-round
4. **Deterministic KNN**: Target assignment is fully deterministic and verifiable
5. **Separation of knowledge and action**: Models publish weights before targets are known

## Validator Requirements

| Resource | Minimum | Recommended |
|----------|---------|-------------|
| CPU | 14+ cores | 16+ cores |
| RAM | 14 GB | 32+ GB |
| Storage | 250 GB NVMe SSD | 500+ GB |
| Network | 1 Gbps | 10 Gbps |
| GPU (scoring) | 24 GB VRAM | — |
| Stake | ~0.12% of total voting power | Higher for more rewards |

Validators earn 20% of epoch rewards, distributed proportional to stake. They generate targets, participate in consensus, audit submissions, and store model weights.

**Validator lifecycle**: Generate 4 keypairs + metadata → submit validator.info → stake SOMA → wait for epoch activation.
