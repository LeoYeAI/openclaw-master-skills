# SOMA Model Strategies

> Model strategies: https://docs.soma.org/guides/model-strategies
> Model specs: https://docs.soma.org/reference/models/overview
> Training patterns: `quickstart-patterns.md`

## Understanding Byte-Level Prediction

SOMA's models don't tokenize. They read raw bytes.

This is a fundamental difference from token-level LLMs. A byte-level model sees the actual structure of data — UTF-8 encoding patterns, byte-pair correlations, binary headers, whitespace as literal byte values. It doesn't abstract away the encoding; it learns it.

**What this means for training:**
- Your model can learn ANY data format that can be represented as bytes: source code, natural language, binary protocols, serialized data, even image headers
- Patterns that span encoding boundaries (like multi-byte Unicode characters) are visible to the model
- The 1024-byte context window means documents are chunked into independent sequences without cross-sequence visibility. Optimize for **information density within each window** — a complete function definition is better training material than a random 1024-byte slice of a large file
- Shorter, self-contained passages (functions, docstrings, paragraphs) are more effective than long, fragmented documents

**The superpower**: While token-level models are optimized for natural language, byte-level models can genuinely specialize in domains that tokenizers handle poorly — binary formats, mixed-encoding text, structured data with unusual delimiters, polyglot files that mix languages.

## Learning from the Network

The network is a rich source of competitive intelligence. Use it.

### Download Competitor Weights

```python
from soma_sdk import SomaClient
from soma_models.v1.torch.modules.model import Model
from soma_models.v1.configs import ModelConfig

client = await SomaClient(chain="testnet")

# Find models in your target region
models = await client.get_active_models()
for m in models:
    print(f"Model {m.model_id}: stake={m.stake}, embedding={m.embedding[:5]}...")

# Download a competitor's weights
weights_bytes = await client.fetch_model(competitor_model_id)
competitor = Model.load_bytes(weights_bytes)

# Fine-tune from their checkpoint instead of training from scratch
# This skips the cold-start phase entirely
```

### Download Winning Submission Data

```python
# Get targets that have been filled
targets = await client.get_targets(status="claimable")

for target in targets:
    # Download the data that won this target
    data = await client.fetch_submission_data(target.id)
    # Train on it — this is proven high-quality data for this region
```

**Note**: Training on winning submissions biases your model toward domains the network is already exploring. This is good for competing in established regions. For finding new niches, you need novel data sources (see `data-strategies.md`).

## Distillation Strategies

### Fine-Tuning from Competitors

The fastest path to competitiveness: download a strong model's weights and fine-tune on your domain-specific data.

```python
from soma_models.v1.torch.modules.model import Model
from soma_models.v1.torch.modules.sig_reg import SIGReg
from soma_models.v1.torch.loss import compute_loss
from soma_models.v1.configs import ModelConfig, SIGRegConfig

# Load competitor checkpoint
weights_bytes = await client.fetch_model(competitor_model_id)
model = Model.load_bytes(weights_bytes)
sig_reg = SIGReg(SIGRegConfig())

# Continue training on YOUR specialized data
optimizer = torch.optim.Adam(model.parameters(), lr=1e-5)  # Lower LR for fine-tuning
for token_ids, targets in my_domain_data():
    loss, embedding = compute_loss(model, sig_reg, token_ids, targets)
    loss.backward()
    optimizer.step()
    optimizer.zero_grad()
```

Use a lower learning rate (1e-5 to 5e-5) for fine-tuning to avoid catastrophically forgetting the competitor's general knowledge while adapting to your domain.

### Knowledge Distillation

Run both teacher (competitor) and student (your model) on identical batches. Combine standard prediction loss with an embedding alignment term:

```python
teacher = Model.load_bytes(await client.fetch_model(teacher_model_id))
teacher.eval()

student = Model(ModelConfig(dropout_rate=0.1))
sig_reg = SIGReg(SIGRegConfig())
optimizer = torch.optim.Adam(student.parameters(), lr=1e-4)

alpha = 0.5  # Balance between task loss and distillation loss

for token_ids, targets in training_data():
    # Student forward pass
    student_loss, student_emb = compute_loss(student, sig_reg, token_ids, targets)

    # Teacher forward pass (no gradient)
    with torch.no_grad():
        teacher_loss, teacher_emb = compute_loss(teacher, sig_reg, token_ids, targets)

    # Combined loss: task performance + learn from teacher's representations
    distill_loss = torch.nn.functional.mse_loss(student_emb, teacher_emb)
    total_loss = alpha * student_loss + (1 - alpha) * distill_loss

    total_loss.backward()
    optimizer.step()
    optimizer.zero_grad()
```

### Weight Averaging

Merge weights from multiple successful models for a robust initialization:

```python
import torch

model_a = Model.load_bytes(await client.fetch_model(model_id_a))
model_b = Model.load_bytes(await client.fetch_model(model_id_b))

beta = 0.5  # Blend ratio

averaged_state = {}
for key in model_a.state_dict():
    averaged_state[key] = beta * model_a.state_dict()[key] + (1 - beta) * model_b.state_dict()[key]

merged = Model(ModelConfig())
merged.load_state_dict(averaged_state)
# Fine-tune the merged model on your data
```

### Domain Gap Analysis

Evaluate your model against filled target data to find where you're weak:

```python
model = Model.load_bytes(model_weights)
model.eval()
sig_reg = SIGReg(SIGRegConfig())

targets = await client.get_targets(status="claimable")
for target in targets:
    data = await client.fetch_submission_data(target.id)
    token_ids, target_ids, _ = tokenize(data)
    with torch.no_grad():
        loss, embedding = compute_loss(
            model, sig_reg,
            torch.tensor([token_ids]),
            torch.tensor([target_ids]),
        )
    print(f"Target {target.id}: loss={loss.item():.4f}")
    # High loss = your model struggles here
    # This is where focused training will improve you fastest
```

## Embedding Strategy

Your embedding determines which targets you're assigned via stake-weighted KNN. It's one of the most important strategic decisions.

### Honest Specialization

Your embedding must reflect your model's actual strength. Misalignment — placing your embedding in a region your model doesn't actually excel at — means you'll be assigned targets you can't win. The result: wasted compute and lost rewards.

### Genesis Embedding

Compute your initial embedding from representative training data:

1. Sample 256 representative sequences from your training corpus (1024 bytes each)
2. Forward pass through your trained model
3. Mean-pool the final layer outputs across byte positions for each sequence
4. Average all 256 vectors
5. L2-normalize the result

This produces an embedding that honestly represents what your model has learned.

### Updating Your Embedding

Recompute after:
- **100 competitive wins** — your model has evolved through continued training
- **7 days** — even without wins, training shifts your model's strengths

The update process is the same as genesis: sample data, forward pass, pool, average, normalize. The new embedding will naturally drift toward your model's actual performance region.

### Gap Finding

Query the model registry to identify strategic positions:

```python
import numpy as np

models = await client.get_active_models()
embeddings = np.array([m.embedding for m in models])
stakes = np.array([m.stake for m in models])

# Compute pairwise distances between all models
from scipy.spatial.distance import cdist
distances = cdist(embeddings, embeddings, metric='cosine')

# Find models that are isolated (far from others) — they dominate their niche
# Find clusters of models — these regions are competitive
# Find areas with no models nearby open targets — these are opportunities

targets = await client.get_targets(status="open")
target_embs = np.array([t.embedding for t in targets])

# For each target, find distance to nearest model
target_model_dists = cdist(target_embs, embeddings, metric='cosine')
nearest_model_dist = target_model_dists.min(axis=1)

# Targets with high nearest_model_dist are underserved — opportunity
for i, target in enumerate(targets):
    if nearest_model_dist[i] > 0.5:  # Tune this threshold
        print(f"Underserved target {target.id}: "
              f"nearest model dist={nearest_model_dist[i]:.3f}, "
              f"reward={target.reward_pool}, "
              f"threshold={target.distance_threshold}")
```

## Training Philosophy

### Curriculum Learning

Start simple, get harder:

1. **Phase 1**: Clean, well-formatted data (standard library code, clean documentation, structured configs). This builds foundational byte-level patterns.
2. **Phase 2**: More complex data (larger functions, mixed paradigms, domain-specific code). This builds specialization.
3. **Phase 3**: Hard examples (obfuscated code, mixed encodings, unusual formatting). This builds robustness.

Each phase builds on the previous one's representations. Random data ordering works, but structured progression often converges faster.

### Data Mixture Optimization

The ratio of data types in your training mix directly controls your specialization:

- **80% Python + 20% documentation** = strong Python model with documentation understanding
- **50% Python + 50% Rust** = mediocre at both (don't do this — specialize)
- **90% Python + 10% adjacent data (tests, docstrings, type stubs)** = strong Python model with useful generalization

The right mixture depends on your target niche. A small amount of adjacent-domain data often improves generalization without hurting specialization. But the core must be heavily weighted toward your specialty.

### Checkpoint Selection

Don't automatically use the latest checkpoint. Evaluate against your target region:

1. Save checkpoints every 500 steps
2. After each checkpoint, compute embedding on your evaluation data
3. Score against representative data from your target region
4. The checkpoint with the lowest loss on your target region is your best submission — even if it's not the latest

Models can overfit to training data and drift away from their target region. Checkpoint selection catches this.

### Adversarial Self-Improvement

Find your weaknesses and fix them:

1. Download winning submission data from targets in your region (`fetch_submission_data()`)
2. Evaluate your model on this data
3. Cases where your loss is high = your blind spots
4. Add similar data to your training mix
5. Repeat

Your weaknesses are your fastest growth opportunities. Every blind spot you fix moves your competitive frontier.

## Architecture Exploitation

Understanding the specific architecture helps you train better models.

### 24 Residual Layers

Deep residual paths learn hierarchical patterns. Early layers capture local byte patterns (character encoding, whitespace, delimiters). Middle layers learn syntactic structure (function boundaries, block nesting, keyword patterns). Later layers capture semantic relationships (variable usage, call patterns, logical flow). Training data that exercises all levels of this hierarchy produces more capable models.

### RoPE (Rotary Position Embeddings)

RoPE encodes relative position, not absolute position. This means the model learns that "the byte 50 positions before the current byte" is significant, regardless of where in the 1024-byte window it occurs. This is powerful for structural patterns — indentation depth, matching brackets, template patterns. Data with consistent structural patterns trains RoPE effectively.

### 8 Attention Heads (256 dims each)

Each head can specialize as an independent pattern detector. With 8 heads, the model can simultaneously attend to 8 different types of patterns at each layer. Training on diverse but related data (e.g., code + comments + tests) encourages head specialization, which improves overall performance.

### SIGReg

SIGReg (Sigmoid Regularization) prevents embedding collapse by encouraging uniform distribution across embedding space. This means:
- Your model's embedding will naturally reflect what it's trained on
- You can't easily "game" the embedding to land in a desired region without the training to back it up
- Models trained on diverse data produce more stable, well-distributed embeddings
- Understanding SIGReg helps you predict where your embedding will land after training

## Infrastructure

While Modal is convenient for getting started, explore more affordable GPU providers for sustainable long-term operations. The key requirements:
- **H100 or equivalent**: For training (the 24-layer/2048-dim model benefits from large GPU memory)
- **L4 or equivalent**: For scoring (lighter workload, optimized for inference)
- **CPU only**: For commit/reveal operations (no GPU needed)
- **Persistent storage**: For checkpoints and model artifacts between sessions
