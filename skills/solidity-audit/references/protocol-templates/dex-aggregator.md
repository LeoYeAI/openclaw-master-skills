# DEX Aggregator Protocol Audit Template

## Protocol Type Identification

**Characteristics**:
- Multi-source liquidity routing
- Order matching and settlement
- Multiple AMM/DEX integrations

**Key Contracts**:
- Exchange / Settlement
- OrderMatcher
- AssetProxy / Bridge

---

## 1. Order Matching Security

### Checklist

- [ ] Order signature verification (EIP-712, EthSign, EIP-1271)
- [ ] Order expiration check
- [ ] Order cancellation mechanism
- [ ] Fill amount validation

### Risks

| Risk | Check |
|------|-------|
| Order collision | Nonce tracking |
| Price manipulation | Price bounds |
| Front-running | Commit-reveal |

---

## 2. Asset Transfer Security

### Checklist

- [ ] AssetProxy registration has access control
- [ ] Token transfers use SafeERC20
- [ ] ETH refunds handled correctly

---

## 3. Signature Security

### Multi-Type Signatures

| Type | Check Points |
|------|--------------|
| EIP-712 | Domain separator, type hash |
| EthSign | Replay protection |
| EIP-1271 | isValidSignature |

---

## 4. Settlement Security

| Risk | Mitigation |
|------|------------|
| Reentrancy | Reentrancy guards |
| Partial fill | Atomic operations |
| Gas exhaustion | Batch limits |

---

## 5. Known Vulnerabilities

| Issue | Detection |
|-------|-----------|
| Routing manipulation | Pool whitelist |
| Fee-on-transfer | Balance checks |
| Flash loan | TWAP usage |