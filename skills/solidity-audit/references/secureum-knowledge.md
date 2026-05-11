# SecureUM Mind Map Knowledge Base

> Source: https://github.com/x676f64/secureum-mind_map
> Integrated: 2026-03-20
> Purpose: Audit checklist extension reference

---

## Part 1: Pitfalls and Best Practices 101 (Basic)

### Compiler & Version

| ID | Issue | Check Point |
|----|-------|-------------|
| 1 | Solidity versions | Use latest stable |
| 2 | Unlocked pragma | Lock version `0.8.20` |
| 3 | Multiple pragma | Use single version |

### Access Control

| ID | Issue | Check Point |
|----|-------|-------------|
| 4 | Incorrect access control | Check visibility/modifiers |
| 5 | Unprotected withdraw | Must have permission |
| 6 | Unprotected selfdestruct | Strict permission control |
| 7 | Modifier side-effects | No unexpected effects |
| 8 | Incorrect modifier | Verify logic |

### Delegatecall Dangers

| ID | Issue | Check Point |
|----|-------|-------------|
| 12 | Controlled delegatecall | Target must be trusted |

### Reentrancy

| ID | Issue | Check Point |
|----|-------|-------------|
| 13 | Reentrancy vulnerabilities | CEI pattern or guard |
| 14 | ERC777 callbacks | Hooks can trigger reentrancy |
| 15 | Avoid transfer()/send() | Only pass 2300 gas |

### Randomness & Time

| ID | Issue | Check Point |
|----|-------|-------------|
| 16 | Private on-chain data | No real privacy |
| 17 | Weak PRNG | Don't use block.timestamp |
| 18 | Block values as time proxies | Miner manipulable |

### Arithmetic

| ID | Issue | Check Point |
|----|-------|-------------|
| 19 | Integer overflow | Check unchecked blocks |
| 20 | Divide before multiply | Multiply first |

### Transaction Ordering

| ID | Issue | Check Point |
|----|-------|-------------|
| 21 | Transaction order dependence | Consider commit-reveal |
| 22 | ERC20 approve() race | approve(0) then approve(new) |

### Signature Security

| ID | Issue | Check Point |
|----|-------|-------------|
| 23 | Signature malleability | Verify before ecrecover |

### ERC Standard Pitfalls

| ID | Issue | Check Point |
|----|-------|-------------|
| 24 | ERC20 transfer() no return | Use SafeERC20 |
| 25 | Incorrect ERC721 return | Check implementation |
| 26 | Unexpected Ether | selfdestruct can force send |
| 27 | fallback vs receive | Distinguish purpose |

---

## Part 2: Pitfalls 201 (Advanced)

### ERC20 Token Pitfalls

| ID | Issue | Check Point |
|----|-------|-------------|
| 102 | Transfer return values | Check return value |
| 105 | Approve race-condition | Zero first |
| 106 | ERC777 hooks | Reentrancy possible |
| 107 | Deflation via fees | Amount may not match |
| 108 | Inflation via interest | Balance changes |

### Guarded Launch

| ID | Issue | Check Point |
|----|-------|-------------|
| 128 | Asset limits | Cap on assets |
| 132 | Composability limits | Limit interactions |
| 134 | Circuit breakers | Pause mechanism |
| 135 | Emergency shutdown | Emergency stop |

---

## Part 3: Audit Techniques

### Audit Techniques

| ID | Technique | Type |
|----|-----------|------|
| 20 | Specification analysis | Manual |
| 21 | Documentation analysis | Manual |
| 22 | Testing | Automated |
| 23 | Static analysis | Automated |
| 24 | Fuzzing | Automated |
| 25 | Symbolic checking | Automated |
| 26 | Formal verification | Automated |
| 27 | Manual analysis | Manual |

### Tools

| Tool | Type | Use |
|------|------|-----|
| Slither | Static | Fast scanning |
| Manticore | Symbolic | Deep analysis |
| Echidna | Fuzz | Property testing |
| MythX | SaaS | Multiple techniques |

---

## Part 4: Top 30 Must-Check Items

| # | Check | Description |
|---|-------|-------------|
| 1 | pragma locked | Fixed version |
| 2 | Access control | All modifiers |
| 3 | delegatecall target | Must trust |
| 4 | Reentrancy | CEI or guard |
| 5 | Randomness | No block values |
| 6 | Overflow | Check unchecked |
| 7 | Multiply first | Precision |
| 8 | approve race | Zero first |
| 9 | Signature malleability | Verify format |
| 10 | ERC20 return | SafeERC20 |
| 11 | Unexpected ETH | selfdestruct |
| 12 | tx.origin | No auth |
| 13 | mapping deletion | Manual clear |
| 14 | Low-level calls | Check return |
| 15 | Calls in loops | DoS risk |
| 16 | Unbounded loops | Gas limit |
| 17 | Events | Emit on changes |
| 18 | Zero address | Validate |
| 19 | require vs assert | Correct use |
| 20 | Deprecated | Avoid old |
| 21 | Visibility | Explicit |
| 22 | Inheritance order | Initialization |
| 23 | Hash collision | encodePacked |
| 24 | Assembly | Document |
| 25 | Uninitialized | Especially storage |
| 26 | Proxy init | initializer |
| 27 | Proxy storage | Layout consistent |
| 28 | ERC777 hooks | Reentrancy |
| 29 | Fee tokens | Amount check |
| 30 | Two-step auth | Timelock |

---

## Reference

- SecureUM Mind Map: https://github.com/x676f64/secureum-mind_map
- SWC Registry: https://swcregistry.io/