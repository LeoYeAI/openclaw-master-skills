# SOMA CLI Reference

> CLI source: https://github.com/soma-org/soma/tree/main/cli
> CLI docs: https://docs.soma.org/reference/cli/overview
> Installation: https://docs.soma.org/getting-started/install

## Installation

```bash
# Install via sup (version manager)
curl -fsSL https://sup.soma.org | bash
sup install soma

# Verify
soma --version
```

## Configuration

- **Config file**: `~/.soma/soma.yaml`
- **Genesis**: `genesis.blob` (network-specific)
- **Logging**: `RUST_LOG=info` (or `debug`, `warn`, `error`)

## Wallet Management

```bash
soma wallet active                    # Show active address
soma wallet list                      # List all addresses
soma wallet new                       # Create new address
soma wallet new --key-scheme ed25519  # Specify key scheme
soma wallet switch --address <ADDR>   # Switch active address
soma wallet export --address <ADDR>   # Export secret key
soma wallet remove --address <ADDR>   # Remove address
```

## Environment Management

```bash
soma env active              # Show active environment
soma env list                # List environments
soma env new <NAME>          # Create new environment
soma env switch <NAME>       # Switch environment
soma env chain-id            # Show chain ID
```

## Account Operations

```bash
soma balance                          # Check SOMA balance
soma balance --address <ADDR>         # Check specific address
soma send <AMOUNT> --to <ADDR>        # Send SOMA
soma transfer <AMOUNT> --to <ADDR>    # Transfer SOMA
soma pay --amounts <A1,A2> --recipients <R1,R2>  # Multi-pay
soma faucet                           # Request testnet tokens
soma faucet --address <ADDR>          # Faucet to specific address
soma status                           # Network status
```

## Staking

```bash
soma stake <AMOUNT> --validator <ADDR>    # Stake to validator
soma unstake --staked-soma-id <ID>        # Unstake
```

## Model Operations

```bash
# Create model
soma model create \
  --commission-rate <RATE> \         # 0-10000 basis points
  --stake <AMOUNT>                    # Optional initial stake

# Commit weights
soma model commit \
  --model-id <ID> \
  --weights-url <URL> \
  --encrypted-weights <PATH> \
  --decryption-key <KEY> \
  --embedding <EMBEDDING>

# Reveal (after epoch advances)
soma model reveal \
  --model-id <ID> \
  --decryption-key <KEY> \
  --embedding <EMBEDDING>

# Management
soma model deactivate --model-id <ID>
soma model info --model-id <ID>
soma model list
soma model list --owner <ADDR>
soma model set-commission-rate --model-id <ID> --rate <RATE>
soma model download --model-id <ID> --output <PATH>
```

## Target Operations

```bash
# Browse targets
soma target list
soma target list --status open        # Open targets only
soma target info --target-id <ID>

# Submit data
soma target submit \
  --target-id <ID> \
  --data-url <URL> \
  --data <PATH> \
  --model-id <MODEL_ID> \
  --embedding <EMBEDDING> \
  --distance-score <SCORE> \
  --loss-score <SCORE>

# Claim rewards
soma target claim --target-id <ID>

# Download submission data
soma target download --target-id <ID> --output <PATH>
```

## Object Queries

```bash
soma objects list                         # List owned objects
soma objects list --type coin             # Filter by type
soma objects list --owner <ADDR>          # Specific owner
soma objects get --id <OBJECT_ID>         # Get object details
soma objects gas                          # List gas coins
```

**Object types**: `coin`, `staked_soma`, `target`, `submission`, `system_state`

## Transaction Operations

```bash
soma tx info --digest <DIGEST>                     # Get transaction info
soma tx execute-serialized <BYTES>                 # Execute serialized tx
soma tx execute-signed <BYTES>                     # Execute signed tx
soma tx execute-combined-signed <BYTES>            # Execute combined signed
```

## Network Operations

```bash
# Start local network for development
soma start localnet
soma start localnet --force-regenesis     # Fresh state

# Start validator node
soma start validator --config <PATH>

# Start scoring service
soma start scoring --device cuda --data-dir <PATH>
soma start scoring --device cpu --data-dir <PATH>

# Network info
soma network                              # Network summary
```

## Validator Operations

```bash
# Setup
soma validator make-validator-info        # Generate validator.info file

# Join/leave
soma validator join-committee             # Join validator set
soma validator leave-committee            # Leave validator set

# Info
soma validator list                       # List all validators
soma validator display-metadata           # Show your metadata

# Updates
soma validator update-metadata \
  --next-epoch-network-address <ADDR> \
  --next-epoch-p2p-address <ADDR>

soma validator set-commission-rate --rate <RATE>

# Reporting
soma validator report --reportee <ADDR>           # Report bad actor
soma validator undo-report --reportee <ADDR>      # Undo report
```

## Genesis & Ceremony

```bash
soma genesis ceremony                     # Participate in genesis
soma keytool generate ed25519             # Generate keypair
soma completions --shell bash             # Shell completions
```

## Transaction Processing Flags

These flags can be added to most transaction commands:

```bash
--tx-digest                    # Return only transaction digest
--simulate                     # Simulate without executing
--serialize-unsigned           # Output unsigned transaction bytes
--serialize-signed             # Output signed transaction bytes
```

## Common Workflows

**Check your balance and status**:
```bash
soma balance && soma status
```

**Create and fund a new wallet**:
```bash
soma wallet new
soma faucet  # testnet only
soma balance
```

**Start a local development network**:
```bash
soma start localnet --force-regenesis
# In another terminal:
soma balance
soma faucet
```
