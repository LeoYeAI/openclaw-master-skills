# Building sentinel

The `sentinel` binary is a Rust workspace in `scripts/`. This document
covers local builds, cross-compilation, and CI.

---

## Prerequisites

- Rust stable toolchain (1.77+): https://rustup.rs
- `cargo` in PATH
- For cross-compilation: `cross` (`cargo install cross`) and Docker

---

## Local build

```bash
cd scripts/
cargo build --release
# binary at: scripts/target/release/sentinel

# Install to ~/.cargo/bin (makes `sentinel` available system-wide)
cargo install --path . --bin sentinel
```

---

## Crate structure

```
scripts/
├── Cargo.toml          # workspace root
├── Cargo.lock
└── src/
    ├── main.rs         # CLI entry point (clap)
    ├── audit.rs        # Integrity hashing + credential scan
    ├── injection.rs    # Prompt injection detection
    ├── daemon.rs       # FSEvents/inotify file watcher + process monitor
    ├── egress.rs       # Network connection attribution
    ├── payment.rs      # x402 client + Base wallet (alloy-rs)
    ├── report.rs       # Structured output (JSON + human-readable)
    └── patterns/
        └── mod.rs      # Injection pattern library (compiled in)
```

---

## Key dependencies

| Crate | Purpose |
|---|---|
| `clap` | CLI argument parsing |
| `alloy` | Ethereum/Base wallet, USDC signing, x402 client |
| `bip39` | BIP-39 mnemonic generation and validation |
| `eth-keystore` | eth-keystore v3 format (AES-128-CTR + scrypt) |
| `argon2` | Argon2id KDF — derives keystore passphrase from machine secret |
| `aes-gcm` | AES-256-GCM encryption for mnemonic.enc |
| `tokio` | Async runtime |
| `notify` | Cross-platform filesystem watching (inotify/FSEvents/ReadDirectoryChanges) |
| `serde` / `serde_json` | Serialization |
| `sha2` | SHA-256 hashing for integrity checks |
| `regex` | Injection pattern matching |
| `tracing` | Structured logging |
| `reqwest` | HTTP client (x402 handshake, VirusTotal lookups) |
| `zeroize` | Secure memory clearing for all key material |
| `rand` | CSPRNG (nonce generation, machine secret, keystore salt) |

---

## Cross-compilation targets

```bash
# macOS ARM (Apple Silicon) — primary target
cargo build --release --target aarch64-apple-darwin

# macOS x86_64
cargo build --release --target x86_64-apple-darwin

# Linux x86_64
cross build --release --target x86_64-unknown-linux-gnu

# Linux ARM64 (Raspberry Pi, cloud VMs)
cross build --release --target aarch64-unknown-linux-gnu
```

Universal macOS binary:
```bash
lipo -create \
  target/aarch64-apple-darwin/release/sentinel \
  target/x86_64-apple-darwin/release/sentinel \
  -output sentinel-universal-macos
```

---

## CI (GitHub Actions)

The repository includes `.github/workflows/release.yml` that:

1. Builds all four targets on push to `main` or version tags
2. Runs `cargo test` and `cargo clippy --deny warnings`
3. Uploads binaries as release assets on version tags
4. Publishes a SHA-256 manifest (`sentinel-checksums.txt`) alongside
   the binaries — ClawHub verifies this manifest during skill installation

---

## Running tests

```bash
cd scripts/
cargo test

# Integration tests (requires a funded testnet wallet)
SENTINEL_TESTNET=1 cargo test --features integration
```

---

## Security notes for the binary

**Key storage model** (`~/.sentinel/`):

```
~/.sentinel/
├── machine.key          # 32-byte CSPRNG secret, created once, never leaves this machine
├── wallet/
│   ├── keystore.json    # eth-keystore v3: private key, AES-128-CTR + scrypt
│   ├── mnemonic.enc     # 12-word phrase, AES-256-GCM, keyed by machine secret
│   └── config.json      # wallet address, chain, spend limit
└── daemon.log
```

- `machine.key` is generated with `rand::thread_rng()` (CSPRNG) on first run and never transmitted anywhere. It is the root of all local key derivation.
- Keystore passphrase = `Argon2id(machine.key, context="sentinel-keystore")`. 64 MiB memory, 3 iterations — resistant to brute force even if `keystore.json` is exfiltrated, as long as `machine.key` stays on the machine.
- Mnemonic is encrypted with a *separate* Argon2id derivation (`context="sentinel-mnemonic"`) so the two encrypted files can't cross-decrypt.
- All key material uses `zeroize` — secrets are zeroed from memory when dropped.
- The binary is built with `RUSTFLAGS="-C relocation-model=pic"` for ASLR compatibility.
- Reproducible builds: `Cargo.lock` is committed; CI uses pinned toolchain via `rust-toolchain.toml`.
- All wallet files are created with `0600` permissions (owner read/write only).
