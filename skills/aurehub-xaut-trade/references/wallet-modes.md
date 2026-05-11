# Wallet Modes

## WDK Mode (Recommended)

- **Storage**: Encrypted vault (`~/.aurehub/.wdk_vault`) using PBKDF2-SHA256 + XSalsa20-Poly1305
- **Encryption**: PBKDF2 with 100k iterations, seed never stored as plaintext
- **Dependencies**: Node.js >= 18 only — no external tools required
- **Setup**: Choose password → encrypted vault created automatically
- **Config**: `WALLET_MODE=wdk` + `WDK_PASSWORD_FILE` in `.env`

## Foundry Mode (Advanced)

- **Storage**: Foundry keystore (`~/.foundry/keystores/<account>`) — standard Web3 Secret Storage
- **Encryption**: Scrypt-based (Foundry default)
- **Dependencies**: Foundry (`cast`) must be installed
- **Setup**: Install Foundry → import/create keystore → set password file
- **Config**: `WALLET_MODE=foundry` + `FOUNDRY_ACCOUNT` + `KEYSTORE_PASSWORD_FILE` in `.env`

## Switching Modes

Re-run `setup.sh` and select the other mode. Existing wallet data is not deleted.

## Security Comparison

| Feature | WDK | Foundry |
|---------|-----|---------|
| Seed/key encryption at rest | PBKDF2 + XSalsa20-Poly1305 | Scrypt |
| Password file | `~/.aurehub/.wdk_password` | `~/.aurehub/.wallet.password` |
| External tool required | No | Yes (Foundry) |
| Key derivation | BIP-39/BIP-44 (HD wallet) | Single key per keystore |
