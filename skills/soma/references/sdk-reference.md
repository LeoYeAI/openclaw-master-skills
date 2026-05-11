# SOMA Python SDK Reference

> SDK source: https://github.com/soma-org/soma/tree/main/python-sdk
> Models source: https://github.com/soma-org/soma/tree/main/python-models
> SDK docs: https://docs.soma.org/reference/sdk/overview
> Type reference: https://docs.soma.org/reference/sdk/types
> Examples: https://github.com/soma-org/soma/tree/main/python-examples

## Installation

```bash
pip install soma-sdk                # Core SDK
pip install soma-models[torch]      # PyTorch model support
pip install soma-models[flax]       # Flax/JAX model support
pip install soma-models[all]        # All frameworks
```

Requires Python >= 3.10.

## Keypair

```python
from soma_sdk import Keypair

# Generate new keypair
kp = Keypair.generate()

# Restore from secret key (hex string or bytes)
kp = Keypair.from_secret_key("your_hex_secret_key")

# Restore from BIP-39 mnemonic
kp = Keypair.from_mnemonic("word1 word2 ... word24")

# Get address (hex string)
address = kp.address()

# Sign raw transaction bytes
signature = kp.sign(tx_data_bytes)

# Export secret key as hex
secret = kp.to_secret_key()
```

## Client Setup

```python
from soma_sdk import SomaClient

# Named presets (recommended)
client = await SomaClient(chain="testnet")    # testnet fullnode + services
client = await SomaClient(chain="localnet")   # localhost + services

# Explicit URLs
client = await SomaClient(
    "https://fullnode.testnet.soma.org",
    faucet_url="https://faucet.testnet.soma.org",
    scoring_url="http://127.0.0.1:9124",
    admin_url="http://127.0.0.1:9125"
)
```

All methods are async — use `await` and run within `asyncio`.

## Chain & Node Info

```python
await client.get_chain_identifier()       # str — chain ID
await client.get_server_version()         # str — server version
await client.get_protocol_version()       # int — protocol version
await client.get_architecture_version()   # int — model architecture version
await client.get_embedding_dim()          # int — embedding dimension (2048)
await client.get_model_min_stake()        # int — minimum stake in shannons
await client.get_active_models()          # list[ActiveModel] — all active models
await client.check_api_version()          # None — verify client-server compatibility
```

## Object & State Queries

```python
await client.get_object(object_id)                          # ObjectRef
await client.get_object_with_version(object_id, version)    # ObjectRef
await client.get_balance(address)                           # float — balance in SOMA
await client.list_owned_objects(owner, type=None, limit=None)  # list[ObjectRef]
await client.get_latest_system_state()                      # SystemState
await client.get_epoch(epoch=None)                          # EpochInfo (None = latest)
```

**Object types for `list_owned_objects`**: `"coin"`, `"staked_soma"`, `"target"`, `"submission"`, `"system_state"`

## Targets

```python
# List targets with pagination
response = await client.list_targets(
    status=None,         # "open", "claimable", etc.
    claimable=False,     # filter for claimable only
    epoch=None,          # specific epoch
    limit=None           # max results
)
# response is ListTargetsResponse with .targets and pagination

# Get targets directly as list
targets = await client.get_targets(
    status="open",       # commonly used: "open" for submission
    claimable=False,
    epoch=None,
    limit=None
)
# Returns list[Target]

# Get model weight manifests for scoring
manifests = await client.get_model_manifests(model_ids_or_target)
# Can pass a list of model IDs or a Target object
# Returns list[ModelManifest] with url, checksum, decryption_key, etc.
```

## Scoring

```python
# Score data against models (requires scoring service running)
result = await client.score(
    data_url,              # URL where data is accessible
    models,                # list of ModelManifest objects
    target_embedding,      # target's embedding vector
    data=None              # optional: raw data bytes (if not at URL yet)
)
# Returns ScoreResult with: winner (index), loss_score, embedding, distance

# Check scoring service health
is_healthy = await client.scoring_health()  # bool
```

## Model Lifecycle

```python
# Step 1: Create model (returns model_id)
model_id = await client.create_model(
    signer,              # Keypair
    commission_rate,     # int 0-10000 (basis points, e.g., 1000 = 10%)
    stake_amount=None    # optional initial stake in shannons
)

# Step 2: Commit weights
await client.commit_model(
    signer,              # Keypair
    model_id,            # str — from create_model
    weights_url,         # str — URL of encrypted weights
    encrypted_weights,   # bytes — the encrypted weight data (for hash verification)
    decryption_key,      # str — base58 decryption key
    embedding            # list[float] — model's specialization embedding
)

# Step 3: Reveal (next epoch)
await client.reveal_model(
    signer,              # Keypair
    model_id,            # str
    decryption_key,      # str — same key from commit
    embedding            # list[float] — same embedding from commit
)

# Management
await client.deactivate_model(signer, model_id)
await client.set_model_commission_rate(signer, model_id, new_rate)
await client.report_model(signer, model_id)
await client.undo_report_model(signer, model_id)
```

## Data Submission & Rewards

```python
# Submit scored data
await client.submit_data(
    signer,              # Keypair
    target_id,           # str — target this data hits
    data,                # bytes — raw data
    data_url,            # str — public URL of data
    model_id,            # str — winning model
    embedding,           # list[float] — data's embedding
    distance_score,      # float — distance to target
    loss_score           # float — cross-entropy loss
)

# Claim rewards (after 2-epoch audit window)
await client.claim_rewards(signer, target_id)

# Report fraudulent submissions
await client.report_submission(signer, target_id)
await client.undo_report_submission(signer, target_id)
```

## Transfers

```python
await client.transfer_coin(signer, recipient, amount)        # Transfer SOMA
await client.pay_coins(signer, recipients, amounts)           # Pay multiple
await client.transfer_objects(signer, recipient, object_ids)  # Transfer objects
```

## Staking

```python
await client.add_stake(signer, validator, amount=None)       # Stake to validator
await client.withdraw_stake(signer, staked_soma_id)          # Unstake
await client.add_stake_to_model(signer, model_id, amount=None)  # Stake to model
```

## Static Utilities

```python
# Unit conversion
SomaClient.to_shannons(1.5)              # 1_500_000_000
SomaClient.to_soma(1_500_000_000)        # 1.5

# Data integrity
SomaClient.commitment(data_bytes)        # Blake2b-256 Base58 digest

# Weight encryption
encrypted, key = SomaClient.encrypt_weights(data, key=None)  # (bytes, str)
decrypted = SomaClient.decrypt_weights(data, key)             # bytes

# Build model manifest manually
manifest = SomaClient.model_manifest(url, ...)
```

## Epoch Helpers

```python
await client.wait_for_next_epoch(timeout=120.0)    # int — polls until epoch changes (default 120s timeout — too short for testnet's 24h epochs, only practical on localnet)
await client.advance_epoch()                         # int — force advance (localnet only)
await client.get_next_epoch_timestamp()              # int — ms timestamp
await client.get_following_epoch_timestamp()         # int — epoch after next, ms
```

## Proxy Fetch

```python
await client.fetch_model(model_id)                # bytes — download model weights
await client.fetch_submission_data(target_id)      # bytes — download submission data
```

## Transactions

```python
await client.execute_transaction(tx_bytes)              # TransactionEffects
await client.simulate_transaction(tx_data_bytes)        # TransactionEffects
await client.get_transaction(digest)                    # TransactionEffects
```

## Checkpoints

```python
await client.get_latest_checkpoint()                    # CheckpointSummary
await client.get_checkpoint_summary(sequence_number)    # CheckpointSummary
```

## Faucet

```python
await client.request_faucet(address)    # FaucetResponse — testnet only
```

## Validator Management

```python
await client.add_validator(signer, pubkey_bytes, network_pubkey_bytes, ...)
await client.remove_validator(signer, pubkey_bytes)
await client.update_validator_metadata(signer, next_epoch_network_address=None, ...)
await client.set_validator_commission_rate(signer, new_rate)
await client.report_validator(signer, reportee)
await client.undo_report_validator(signer, reportee)
```

## Key Types

**Target**:
- `id`, `status`, `embedding`, `model_ids`
- `distance_threshold`, `reward_pool`, `generation_epoch`
- `bond_amount`, `submitter`, `winning_model_id`

**ScoreResult**:
- `winner` (int — index of winning model), `loss_score`, `embedding`, `distance`

**ModelManifest**:
- `url`, `checksum`, `size`, `decryption_key`, `encrypted_weights`

**ActiveModel**:
- `model_id`, `owner`, `embedding`, `stake`, `commission_rate`

**SystemState**:
- `epoch`, `protocol_version`, `validators` (ValidatorSet)
- `parameters` (SystemParameters), `emission_pool`, `target_state`

**EpochInfo**:
- `epoch`, `first_checkpoint_id`, `epoch_start_timestamp_ms`

**TransactionEffects**:
- `status`, `gas_used` (GasUsed), `transaction_digest`
- `created`, `mutated`, `deleted` (lists of affected objects)

**ObjectRef**: `id`, `version`, `digest`

**FaucetResponse**: `status`, `coins_sent`

**GasUsed**: `computation_cost`, `storage_cost`, `storage_rebate`, `non_refundable_storage_fee`

## SOMA Models Library

```python
# PyTorch
from soma_models.v1.torch.modules.model import Model
from soma_models.v1.torch.modules.sig_reg import SIGReg
from soma_models.v1.torch.loss import compute_loss

# Flax/JAX
from soma_models.v1.flax.modules.model import Model
from soma_models.v1.flax.modules.sig_reg import SIGReg
from soma_models.v1.flax.loss import compute_loss

# Common
from soma_models.v1.tokenizer import tokenize  # bytes → TokenizedSequence
from soma_models.v1.configs import ModelConfig, SIGRegConfig

# Serialization
model.save(path)           # Save to directory
model = Model.load(path)   # Load from directory
data = model.save_bytes()  # Serialize to bytes
model = Model.load_bytes(data)  # Deserialize from bytes

# Utilities
from soma_models.v1.utils import remap, flatten_dict, unflatten_dict
```

**Tokenizer**: `tokenize(raw_bytes)` returns `TokenizedSequence` with `token_ids`, `targets`, `pos_ids`.
