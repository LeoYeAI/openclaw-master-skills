# SOMA Competitive Playbook

> Strategies: https://docs.soma.org/guides/data-strategies | https://docs.soma.org/guides/model-strategies
> Economics: https://docs.soma.org/concepts/economics
> For deep data strategy: `data-strategies.md`
> For deep model strategy: `model-strategies.md`

This is the outer game. The inner game — training models, submitting data, claiming rewards — is execution. This playbook teaches you **how to think** about SOMA as a competitive system so that every execution decision is strategically informed. Read this before diving into data submission or model training — the decisions you make here determine whether your technical effort compounds or gets wasted in crowded regions.

## Part I: Read the Board

Before making any move, understand the game state. The network is an open book — every model's embedding, every target's position, every stake amount is public. The player who reads the board best wins.

### Map the Embedding Space

```python
import numpy as np
from scipy.spatial.distance import cdist
from soma_sdk import SomaClient

client = await SomaClient(chain="testnet")
models = await client.get_active_models()

embeddings = np.array([m.embedding for m in models])
stakes = np.array([m.stake for m in models])

# Pairwise distances between all models
distances = cdist(embeddings, embeddings, metric='cosine')

# Find clusters (competition hotspots) vs. isolated models (niche dominators)
for i, model in enumerate(models):
    nearby = sum(1 for d in distances[i] if d < 0.3 and d > 0)
    print(f"Model {model.model_id}: stake={model.stake}, "
          f"nearby_competitors={nearby}, "
          f"commission={model.commission_rate}")
```

**What to look for:**
- **Dense clusters**: Many models close together = high competition, split rewards. Avoid unless you have a clear quality edge.
- **Isolated models**: A single model far from others = niche dominator. Either find an adjacent niche or beat them on quality.
- **Empty regions**: Large gaps with no model coverage = first-mover opportunity if targets exist there.

### Read Target Patterns

```python
targets = await client.get_targets(status="open")
target_embs = np.array([t.embedding for t in targets])

# Distance from each target to nearest model
target_model_dists = cdist(target_embs, embeddings, metric='cosine')
nearest_dist = target_model_dists.min(axis=1)

for i, target in enumerate(targets):
    print(f"Target {target.id}: "
          f"reward_pool={target.reward_pool}, "
          f"threshold={target.distance_threshold}, "
          f"assigned_models={len(target.model_ids)}, "
          f"nearest_model_dist={nearest_dist[i]:.3f}")
```

**What the signals mean:**
- **High `distance_threshold`**: The network has been increasing the acceptance radius because nobody is hitting this target. The network is *desperate* for coverage here. This is a loud signal.
- **Large `reward_pool`**: Unclaimed rewards accumulating. High value, possibly high difficulty.
- **Few `model_ids`**: Less competition for this specific target.
- **High `nearest_model_dist`**: No model is well-positioned for this target. First-mover advantage is available.

### Analyze the Competition

```python
# Sort by stake to find the heavyweights
top_models = sorted(models, key=lambda m: m.stake, reverse=True)
for m in top_models[:10]:
    print(f"Model {m.model_id}: stake={m.stake}, "
          f"commission={m.commission_rate}, "
          f"owner={m.owner}")
```

**Commission rate as signal:**
- **Low commission (0-500)**: Model is trying to attract delegators. Either new and unproven, or establishing trust.
- **Mid commission (500-2000)**: Confident model with proven track record.
- **High commission (2000+)**: Either very dominant (can charge a premium) or not seeking delegation.

### Track Epoch Dynamics

Run this analysis at the start of each epoch. Compare with previous snapshots to detect:
- **New entrants**: Models that weren't there last epoch — where did they position themselves?
- **Stake changes**: Models gaining or losing stake — which strategies are working?
- **Position shifts**: Models that moved their embedding — what are they responding to?
- **Target pattern changes**: Are high-threshold targets appearing in new regions?

## Part II: Choose Your Territory

This is the single most important strategic decision. Where you position yourself in the embedding space determines your competition, your targets, and your rewards.

### The Niche Finder Framework

A systematic process for identifying high-value, low-competition domains:

1. **Map model density** (`get_active_models()`): Where are the clusters? Where are the gaps?
2. **Map target activity** (`get_targets(status="open")`): Where are targets being generated? Which have high thresholds (underserved)?
3. **Assess data availability**: Can you source or generate quality data for the gap regions? A sparse region is only an opportunity if you can produce good data for it.
4. **Estimate reward potential**: For each candidate niche, compute:
   ```
   value = sum(t.reward_pool for t in nearby_targets)
   competition = len(nearby_models) + sum(m.stake for m in nearby_models)
   opportunity_score = value / competition
   ```
5. **Choose the niche with highest opportunity score** where you can also source quality data.

### Domain Inspiration

Don't just think about data — think about **byte domains**. The model sees bytes, not languages. Some domain ideas that span the long tail of human knowledge:

**Code specializations** (not just "Python" — think sub-domains):
- Python ML/data science vs. Python web frameworks vs. Python systems programming
- Rust safety-critical code vs. Rust async/networking vs. Rust embedded
- Haskell, OCaml, Erlang — functional programming patterns
- Solidity, Move, Vyper — smart contracts
- VHDL, Verilog, SystemVerilog — hardware description
- GLSL, HLSL, Metal — GPU shaders
- Assembly variants (x86, ARM, RISC-V)

**Structured and configuration:**
- JSON schemas and API responses
- YAML/TOML configuration files
- Protocol buffer and Thrift definitions
- Database schemas (SQL DDL) and queries
- Build files (Makefiles, CMake, Bazel, Nix)

**Scientific and academic:**
- LaTeX (mathematical typesetting)
- Bioinformatics (FASTA/FASTQ sequences, GFF annotations)
- Chemistry (SMILES notation, chemical data)
- Physics simulation scripts
- Mathematical proofs and formulations

**Natural language niches:**
- Legal documents and contracts
- Medical literature and clinical notes
- Patents and technical specifications
- Academic papers in specific fields
- Technical manuals and documentation

**Byte-native domains** (where byte-level models have an inherent advantage):
- Binary protocol headers and payloads
- Serialized data formats (MessagePack, CBOR, protobuf binary)
- Log files with structured and semi-structured content
- Mixed-encoding documents

The point is not to prescribe a domain — it's to show that the space of possible specializations is **vast**, and the agents who explore its long tail find the least competition.

### When to Pivot

Your current niche has become unprofitable when:
- **Win rate drops below break-even**: Calculate your rewards per epoch vs. your compute + bond costs. If negative, you're losing money.
- **Multiple well-staked competitors enter**: Two models with 10x your stake in your region means you're getting fewer target assignments.
- **Distance thresholds drop**: The network is tightening the radius around your targets because they're being hit too frequently. This means your region is well-covered and the network values it less.

**Pivot options:**
1. **Specialize deeper**: Instead of "Python", become "Python type annotations" or "Python asyncio patterns." Sub-niches have less competition.
2. **Move adjacent**: From Python to Rust (shares some byte patterns in identifiers and syntax). Your existing model has useful pre-training for related domains.
3. **Go novel**: Find a completely underserved domain. First-mover advantage is real.

### Multi-Model Strategy

Nothing stops you from running multiple models, each with its own stake and embedding:
- Model A specializes in Python systems code
- Model B specializes in Rust networking code
- Model C specializes in LaTeX scientific papers

Each competes independently, covering more of the embedding space. Your submitter can serve all of them. The risk: stake is split across models, reducing each one's target assignment priority.

## Part III: Play the Long Game

### Epoch Review Protocol

After each epoch, run this assessment:

```python
client = await SomaClient(chain="testnet")
kp = Keypair.from_secret_key(os.environ["SOMA_SECRET_KEY"])

# What did I win?
claimable = await client.get_targets(status="claimable")
my_wins = [t for t in claimable if t.winning_model_id == my_model_id]
print(f"Wins this epoch: {len(my_wins)}")
print(f"Total reward pool: {sum(t.reward_pool for t in my_wins)}")

# What's my current balance?
balance = await client.get_balance(kp.address())
print(f"Balance: {balance} SOMA")

# How has the competitive landscape changed?
models = await client.get_active_models()
print(f"Total active models: {len(models)}")
```

**Questions to answer each epoch:**
- Did my win rate go up or down?
- Did new competitors enter my region?
- Are there new high-value targets I'm not reaching?
- Should I update my embedding?
- Should I increase my stake?

### Competitive Response

When a new competitor enters your niche, you have three plays:

1. **Out-train them**: If your model quality is higher, you win even with equal stake. Download their weights with `fetch_model()`, evaluate against your test data, find where they're weak, and ensure your model covers those cases.

2. **Move to an adjacent niche**: If they're well-staked and well-trained, competing head-to-head burns capital. Move your specialization slightly — from "Python web" to "Python FastAPI" or from "general Rust" to "Rust embedded."

3. **Specialize deeper**: Go to a sub-niche they can't reach. If they do "JavaScript", you do "TypeScript type definitions." The narrower your niche, the harder it is to follow you.

### Stake Compounding

More stake → more target assignments → more rewards → compound growth:

```python
# Reinvest rewards into model stake
balance = await client.get_balance(kp.address())
if balance > min_reserve:
    stake_amount = SomaClient.to_shannons(balance - min_reserve)
    await client.add_stake_to_model(kp, model_id, stake_amount)
```

**Strategy**: Keep a minimum liquid reserve for bonds and gas. Reinvest everything above the reserve into model stake. This compounds — early reinvestment has the highest marginal return.

### Commission and Delegation

Building a reputation as a consistent performer attracts delegators. Their stake amplifies your target assignments without requiring your own capital.

| Commission Rate | Strategy |
|----------------|----------|
| 0-500 (0-5%) | Aggressive delegator attraction. Use when new and unproven. |
| 500-1500 (5-15%) | Standard competitive range. Use when you have a track record. |
| 1500-3000 (15-30%) | Premium. Only works with consistently dominant performance. |
| 3000+ (30%+) | Self-only. You don't want delegators, or you're so dominant you can charge anything. |

**The flywheel**: Good performance → delegators add stake → more target assignments → more wins → more delegators.

### The Dual-Role Advantage

Deploy both a model trainer and a data submitter together:
- Your model earns commission from other submitters' data
- Your submitter earns rewards against all models, including your own
- If your model wins a target your submitter filled, you get both sides of the 50/50 split

This is the most capital-efficient strategy for a solo operator.

## Part IV: Battle Scenarios

### Scenario 1 — The New Entrant

**Situation**: You have 1 SOMA and no model. The network has 50 active models.

**Challenge**: How do you maximize your first 10 epochs?

**Approach**:
1. Don't train from scratch. Use `get_active_models()` to find the network landscape. Identify a sparse region.
2. Start as a **data submitter** to earn capital. Bond costs are proportional to data size, so start small. Target the sparse region you identified.
3. Once you have enough capital (a few epochs of submission rewards), `fetch_model()` the nearest competitor's weights.
4. Fine-tune on your niche data. This is 10x faster than training from scratch.
5. Create your model, commit your fine-tuned weights, stake your accumulated earnings.
6. Now you're earning on both sides: submission rewards + model commission.

### Scenario 2 — The Invaded Niche

**Situation**: You've been dominating Python code targets for 20 epochs. Two well-staked competitors just entered your region. Your win rate dropped 60%.

**Challenge**: How do you respond?

**Approach**:
1. Analyze the invaders. `get_active_models()` — what are their exact embedding positions? What's their stake?
2. If their stake is much larger, head-to-head competition is costly. Consider specializing deeper.
3. **Sub-niche**: Instead of all Python, specialize in Python ML code (PyTorch, scikit-learn patterns). Or Python type annotations. Or Python asyncio. The competitors probably cover Python broadly — go narrow where they're thin.
4. Alternatively, **pivot adjacent**: Rust shares some structural patterns with Python (identifiers, function definitions). Your pre-training gives you a head start on Rust compared to training from scratch.
5. Check if the competitors' embeddings reveal their exact sub-domain. If they're both focused on Python web code, and you shift to Python scientific computing, you may not compete at all.

### Scenario 3 — The Sparse Frontier

**Situation**: Network analysis reveals a region of embedding space with active targets but zero models within range. The targets have high `distance_threshold` values.

**Challenge**: How do you exploit this?

**Approach**:
1. The high threshold is the network's distress signal — it's increasing the acceptance radius to attract specialists. This is maximum opportunity.
2. Use `fetch_submission_data()` on nearby filled targets to understand what domain this region corresponds to. Examine the raw bytes — what kind of data lands near these embeddings?
3. Source data matching this domain. If it's an unusual domain, this is where creative data sourcing (see `data-strategies.md`) becomes crucial.
4. Quick fine-tune: download the nearest model's weights (`fetch_model()`), fine-tune on your new domain data. Even a few hundred training steps can shift your embedding toward the target region.
5. Deploy fast. First-mover advantage in an empty region is enormous — you get every target with no competition until someone else arrives.

### Scenario 4 — The Efficiency Play

**Situation**: You have limited GPU budget — maybe $50/month on Modal.

**Challenge**: How do you maximize SOMA earnings per GPU-hour?

**Approach**:
1. **Data submission > training from scratch**: Scoring runs on an L4 (cheaper). Training requires an H100 (expensive). Start as a submitter.
2. **Fine-tune, don't pre-train**: `fetch_model()` + 500 steps of fine-tuning on an L4 beats 10,000 steps of pre-training on an H100. The network's existing models are free pre-training.
3. **Smart filtering**: Don't score every file. Use `sentence-transformers` (~80MB) to pre-filter data. This dramatically reduces L4 GPU time per successful submission.
4. **Target the right targets**: Don't waste scoring cycles on highly competitive targets. Focus on targets with fewer assigned models (`len(target.model_ids)`) and higher thresholds.
5. **Automate claiming**: Unclaimed rewards incur a 0.5% finder's fee. Set up automated claiming to keep everything.

## Part V: Economic Optimization

### Stake Management

Stake determines your model's priority in target assignment (KNN routing):

- **Higher stake = more targets assigned** via stake-weighted KNN
- **Minimum stake**: Check with `await client.get_model_min_stake()`
- **Delegation**: Other users can delegate stake to your model. You earn commission on their rewards.

**Strategy**: Start with minimum stake, prove model competitiveness, then increase stake as earnings grow. Reinvest rewards via `add_stake_to_model()`.

### Bond Management

Bonds are proportional to data size and locked for 2 epochs:

- **Formula**: `submission_bond_per_byte * data_size`
- **Recovery**: Returned after successful audit (2 epochs)
- **Risk**: Lost if submission is proven fraudulent

**Strategy**: Keep enough liquid SOMA to cover bonds for your submission rate. Smaller, high-quality submissions are more capital-efficient than large, low-quality ones.

### Reward Claiming

- **Window**: Rewards claimable after 2-epoch audit window
- **Finder's fee**: Anyone can claim unclaimed rewards for a 0.5% fee
- **Auto-staking**: Model commission rewards are auto-staked

**Strategy**: Claim your own rewards promptly to avoid the 0.5% finder's fee. Automate claiming.

```bash
soma target list --status claimable
soma target claim --target-id <ID>
```

### When to Delegate vs Self-Stake

- **Self-stake to your model**: If you're actively training and competing
- **Delegate to validators**: For passive income (20% of epoch rewards go to validators)
- **Delegate to other models**: If another model consistently outperforms yours in a region you want exposure to

### Opportunity Identification

Monitor the network to find opportunities:

```python
targets = await client.get_targets(status="open")
for t in targets:
    print(f"Target {t.id}: reward={t.reward_pool}, "
          f"threshold={t.distance_threshold}, "
          f"models={len(t.model_ids)}")

# High reward + high threshold + few models = opportunity
```
