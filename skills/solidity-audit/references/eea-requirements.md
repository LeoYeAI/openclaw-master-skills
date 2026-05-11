# EEA EthTrust Security Levels V3 Specification Guide

This document summarizes EEA EthTrust Security Levels requirements for audit reference.

---

## Security Levels

- **[S] Standard**: Basic requirements
- **[M] Moderate**: External interaction checks
- **[Q] Qualified**: Comprehensive measures

---

## [S] Standard Requirements

### S.1 No tx.origin for Authorization

```solidity
// DANGEROUS
require(tx.origin == owner);

// SAFE
require(msg.sender == owner);
```

### S.2 No selfdestruct()

Avoid unless absolutely necessary with proper controls.

### S.3 No CREATE2

Avoid or carefully control.

### S.4 No Inline Assembly

Avoid or document thoroughly.

### S.5 Initialize State Variables

All state variables properly initialized.

### S.6 Lock Pragma Version

Use: `pragma solidity 0.8.20;` not `^0.8.0`

---

## [M] Moderate Requirements

### M.1 External Calls Safety

- Check return values
- Use CEI pattern
- Use reentrancy guards

### M.2 Check Return Values

```solidity
// SAFE
(bool success, ) = token.call(...);
require(success);
```

### M.3 Verify Ether Transfers

Use pull over push pattern.

---

## [Q] Qualified Requirements

### Q.1 Documentation

- Architecture diagrams
- Function specifications
- Security considerations

### Q.2 Test Coverage

- Unit tests > 90%
- Integration tests
- Fuzz testing

---

## Reference

- Official: https://entethalliance.org/specs/ethtrust-sl/v3/