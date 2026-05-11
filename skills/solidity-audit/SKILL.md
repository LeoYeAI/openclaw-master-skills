---
name: solidity-audit
description: >
  Solidity smart contract security audit assistant following EEA EthTrust V3 specification.
  Performs structured audit workflow: vulnerability scanning, security analysis, audit reports.
  Detects reentrancy, integer overflow, access control issues, and more.
  Supports Slither/Aderyn static analysis and Foundry testing.
  Triggers: smart contract audit, solidity audit, security review, vulnerability assessment.
---

# Solidity Smart Contract Audit Assistant

A structured smart contract security audit workflow based on EEA EthTrust Security Levels V3 specification.

## Audit Process Overview

```
1. Project Preparation → 2. Automated Scanning → 3. Manual Review → 4. Testing & Verification → 5. Report Generation
```

### ⚡ Quick Audit Mode (Within 30 minutes)

Suitable for emergency situations or preliminary assessment:

```
1. Access Control Check (5 minutes)
   - Owner permissions
   - Sensitive function modifiers
   
2. Reentrancy Risk Check (5 minutes)
   - External call positions
   - State update order
   
3. Token Security Check (10 minutes)
   - SafeERC20 usage
   - Return value checks
   
4. Critical Vulnerability Scan (10 minutes)
   - Integer overflow
   - Signature verification
   - Permission bypass
```

### 📊 Audit Capability Baseline (Based on 10 rounds of training)

| Capability Dimension | AI Audit | Professional Audit | Gap |
|---------------------|----------|-------------------|-----|
| Basic Vulnerabilities | 90% | 100% | -10% |
| Business Logic | 75% | 95% | -20% |
| Math Boundaries | 50% | 85% | -35% |
| Complex Interactions | 60% | 90% | -30% |

**AI Advantages**: Fast coverage, pattern matching, broad knowledge
**AI Disadvantages**: Missing toolchain, limited depth analysis, boundary conditions

## Step 1: Project Scope & Preparation

### Input Confirmation
- Contract source code (preferably frozen version for audit)
- Compiler version and optimization settings
- Project documentation (architecture diagrams, functional descriptions)
- Test cases (if available)

### Audit Scope Definition
```
□ Number of logic contracts and their functions
□ Whether proxy contracts are included (upgradeability)
□ External dependencies (oracles, cross-chain bridges, etc.)
□ Deployment network (mainnet/L2/testnet)
```

### Security Level Selection
| Level | Applicable Scenarios | Core Requirements |
|-------|---------------------|-------------------|
| [S] Basic | Simple token contracts, basic DeFi | No known high-risk vulnerabilities, basic protection |
| [M] Intermediate | Complex DeFi, NFT markets, DAOs | External call security, access control, oracle verification |
| [Q] Advanced | Cross-chain bridges, lending protocols, treasury management | Business logic verification, MEV protection, complete documentation |

### Pre-Audit Checklist
- [ ] Code is frozen, no modifications during audit period
- [ ] Compiler version is fixed (e.g., `pragma solidity 0.8.20`)
- [ ] All dependency versions are locked
- [ ] Deployment scripts or configurations are provided
- [ ] Test coverage report is available (if exists)

## Step 2: Automated Tool Scanning

### Static Analysis Tools

**Slither (Trail of Bits)**
```bash
# Installation
pip install slither-analyzer

# Basic scan
slither . --exclude-dependencies

# Output JSON format
slither . --exclude-dependencies --json output.json

# Specific detectors
slither . --detect reentrancy-eth,uninitialized-state
```

**Aderyn (Rust-based, fast)**
```bash
# Installation
cargo install aderyn

# Scan
aderyn .

# Output report
aderyn . -o report.md
```

### Tool Output Mapping to EEA Specification

| Tool Detection | EEA Requirement | Security Level |
|----------------|-----------------|----------------|
| `tx.origin` usage | [S] No tx.origin | S |
| `selfdestruct` | [S] No selfdestruct() | S |
| `CREATE2` | [S] No CREATE2 | S |
| `assembly` blocks | [S] No assembly {} | S |
| Reentrancy detection | [M] External Calls | M |
| Uninitialized variables | [S] Initialize State | S |
| Unchecked return values | [M] Check Return Values | M |

### Compiler Version Check
```bash
# Check for known compiler bugs
slither . --check-compiler-bugs
```

Refer to EEA § 3.9 Source code, pragma, and compilers for compiler-related security requirements.

## Step 3: Manual Review Checklist

### [S] Basic Level Review

#### 3.1 Replay Attack Protection
```solidity
// Check: Does transaction hash include chainId?
// Correct example:
keccak256(abi.encodePacked(
    "\x19\x01",
    DOMAIN_SEPARATOR,  // Includes chainId
    hashStruct
))

// Dangerous: Without chainId allows cross-chain replay
```

#### 3.2 Dangerous Opcodes
- [ ] Check `CREATE2` usage justification, whether necessary
- [ ] Check `selfdestruct` calls, confirm legitimate reason
- [ ] Verify `delegatecall` target address controllability

#### 3.3 Permission Verification
```solidity
// Dangerous: Using tx.origin for authorization
require(tx.origin == owner);  // Phishing attack risk

// Correct: Use msg.sender
require(msg.sender == owner);
```

#### 3.4 Encoding Security
```solidity
// Dangerous: Hash collision with consecutive variable-length parameters
keccak256(abi.encodePacked(str1, str2));  // str1="ab", str2="c" == str1="a", str2="bc"

// Safe: Use encode or fixed length
keccak256(abi.encode(str1, str2));
```

#### 3.5 Inline Assembly
- [ ] List all `assembly` blocks
- [ ] Check if detailed comments explain the reason
- [ ] Focus on memory operations and storage operations

### [M] Intermediate Level Review

#### 3.6 External Calls & Reentrancy
```solidity
// CEI Pattern Check (Checks-Effects-Interactions)
function withdraw() external {
    // 1. Checks
    require(balances[msg.sender] > 0, "No balance");
    
    // 2. Effects (update state first)
    balances[msg.sender] = 0;
    
    // 3. Interactions (external calls last)
    (bool success, ) = msg.sender.call{value: amount}("");
    require(success, "Transfer failed");
}

// Read-only reentrancy check: Are view functions called externally before state updates?
```

#### 3.7 Oracle Dependencies
- [ ] Is the price data source trustworthy?
- [ ] Is there a TWAP time window?
- [ ] Is there a data staleness detection mechanism?
- [ ] Is there a failover plan?

```solidity
// Check: Is there price deviation detection?
uint256 price = oracle.getPrice();
require(price > 0 && price < MAX_PRICE, "Invalid price");

// Check: Is there timestamp validation?
require(block.timestamp - oracle.lastUpdate() < HEARTBEAT, "Stale data");
```

#### 3.8 Access Control
- [ ] Check permission modifiers on critical functions
- [ ] Is role management correctly implemented
- [ ] Can initialization functions be called repeatedly

```solidity
// Dangerous: Unprotected initialization function
function initialize() external {
    owner = msg.sender;  // Anyone can call!
}

// Safe: Use OpenZeppelin Initializable
function initialize() external initializer {
    owner = msg.sender;
}
```

#### 3.9 Integer Overflow
```solidity
// Solidity 0.8+ checks overflow by default
// But need to check unchecked blocks:
unchecked {
    // Overflow here will not be detected!
    uint256 result = a + b;  // Dangerous
}

// Special case: Loop counters can safely use unchecked
for (uint256 i; i < n; ) {
    // ...
    unchecked { i++; }
}
```

### [Q] Advanced Level Review

#### 3.10 Logic & Documentation Consistency
- [ ] Compare code implementation with whitepaper/documentation
- [ ] Check for undocumented "hidden features"
- [ ] Verify mathematical formula implementation correctness

#### 3.11 MEV Attack Surface
- [ ] Sandwich attack risk (AMM pricing)
- [ ] Front-running risk (public mempool)
- [ ] Liquidation mechanism exploitable

```solidity
// AMM sandwich attack example
// User transaction: A -> B
// Attacker: Buy B before user transaction, sell B after
// Protection: Use TWAP, slippage protection
```

#### 3.12 Upgradeable Contract Security
```solidity
// Check items:
// 1. Is the proxy contract implementation correct?
// 2. Is the initialization function protected against reentry?
// 3. Are upgrade permissions reasonable?
// 4. Is there storage layout conflict?

// Dangerous: Storage layout conflict
// V1: uint256 a; uint256 b;
// V2: uint256 a; address c; uint256 b;  // c overwrites b's slot!
```

### Special Focus: Governance Module

Governance contract vulnerabilities are often more subtle but have greater impact, requiring specialized review.

#### 3.13 Voting Power & Stake Synchronization
```solidity
// Dangerous example: State sync uses wrong account balance
function notifyFor(address account) external {
    _notifyFor(account, balanceOf(msg.sender));  // Wrong!
    // Should be balanceOf(account)
}

// Check points:
// 1. Is governance module synchronized with main contract state
// 2. Does notify function use correct account address
// 3. Is stake increase/decrease order correct
```

#### 3.14 Voting Mechanism Security
- [ ] Can users manipulate results through extreme voting
- [ ] Is voting weight calculation correct
- [ ] Is voting cooldown period reasonable

#### 3.15 Copy-Paste Error Detection
```solidity
// High-risk pattern: Similar code blocks
function _beforeTokenTransfer(address from, address to, uint256 amount) {
    uint256 balanceFrom = (from != address(0)) ? balanceOf(from) : 0;
    uint256 balanceTo = (from != address(0)) ? balanceOf(to) : 0;  // Copy-paste error!
    // Should be: (to != address(0)) ? balanceOf(to) : 0
}

// Detection method:
// 1. Find code blocks with > 80% similarity
// 2. Compare each difference character by character
// 3. Verify each difference is intentional
```

### Special Focus: System Architecture

#### 3.16 Contract Dependency Analysis

**Must Complete**:
1. Draw contract dependency graph
2. Mark external call directions
3. Identify trust boundaries

```
Example dependency graph:
┌─────────────────┐
│ GovernanceMothership │
│ (Master)        │
└────────┬────────┘
         │ notify
         ▼
┌─────────────────┐    ┌─────────────────┐
│ FactoryGovernance │    │ RewardsGovernance │
│ (Slave 1)       │    │ (Slave 2)       │
└─────────────────┘    └─────────────────┘
```

**Check Points**:
- [ ] Do Slave contracts trust Master
- [ ] Can external contract addresses be replaced
- [ ] Is state synchronization safe

#### 3.17 Trust Assumption Verification
- [ ] "Only contracts deployed by factory are trusted" → Is there verification?
- [ ] "Governance tokens have no callbacks" → Is there checking?
- [ ] "Price oracle returns real price" → Is there boundary checking?

### Special Focus: Permission Model

#### 3.18 Admin Permission Scope
```solidity
// List all onlyOwner/onlyAdmin functions
// Analyze impact scope of each function

// Dangerous pattern: Admin can lock user funds
function emergencyPause() external onlyOwner {
    paused = true;  // Users cannot withdraw funds!
}

// Dangerous pattern: Parameter modification without timelock
function setFeeReceiver(address newReceiver) external onlyOwner {
    feeReceiver = newReceiver;  // Can immediately set malicious contract
}
```

#### 3.19 Permission Bypass Check
- [ ] Can removeMarket + addMarket bypass time restrictions
- [ ] Does adding/removing sub-modules affect fund safety
- [ ] Does modifying contract addresses bypass security checks

#### 3.20 Timelock Integrity
- [ ] Do all critical parameter changes have timelock
- [ ] Does timelock cover all bypass paths
- [ ] Do users have enough time to respond

### Special Focus: Flash Loans & Oracles

#### 3.21 Flash Loan Attack Surface
```solidity
// Check point: State validation after flash loan callback
// Dangerous example: Only check balance, not mapping
function flashLoan(uint256 amount) external {
    uint256 balanceBefore = address(this).balance;
    IFlashLoanReceiver(msg.sender).execute{value: amount}();
    // ⚠️ Only check balance, not balances mapping!
    if (address(this).balance < balanceBefore) revert RepayFailed();
}

// Correct approach: Check all relevant states
function flashLoan(uint256 amount) external {
    uint256 balanceBefore = address(this).balance;
    uint256 depositsBefore = totalDeposits;  // Record mapping state
    IFlashLoanReceiver(msg.sender).execute{value: amount}();
    require(address(this).balance >= balanceBefore, "Balance not restored");
    require(totalDeposits == depositsBefore, "Deposits changed");  // Verify mapping
}
```

#### 3.22 Oracle Manipulation Protection
```solidity
// Dangerous: Using current reserves as price
function _computePrice() private view returns (uint256) {
    return uniswapPair.balance * 1e18 / token.balanceOf(uniswapPair);
    // ⚠️ Reserves can be manipulated by large trades!
}

// Safe: Use TWAP or Chainlink
function _computePrice() private view returns (uint256) {
    (uint256 price0Cumulative, uint256 price1Cumulative,) = 
        UniswapV2OracleLibrary.currentCumulativePrices(pair);
    // Use time-weighted average price
}

// Safe Chainlink usage
function getPrice() public view returns (uint256) {
    (, int256 price,, uint256 timestamp,) = oracle.latestRoundData();
    require(price > 0, "Invalid price");
    require(block.timestamp - timestamp < HEARTBEAT, "Stale data");
    return uint256(price);
}
```

#### 3.23 Governance Voting Power Persistence
```solidity
// Dangerous: Only check current voting power
function queueAction(...) external returns (uint256) {
    if (!_hasEnoughVotes(msg.sender)) revert NotEnoughVotes();
    // ⚠️ Attacker can temporarily gain voting power via flash loan!
}

// Safe: Require voting power holding time
function queueAction(...) external returns (uint256) {
    if (!_hasHeldVotesFor(msg.sender, VOTING_DELAY)) revert NotEnoughVotes();
    // Check voting power for past N blocks
}

function _hasHeldVotesFor(address who, uint256 blocks) private view returns (bool) {
    for (uint256 i = 0; i < blocks; i++) {
        if (getVotesAtBlock(who, block.number - i) <= threshold) return false;
    }
    return true;
}
```

### SecureUM Quick Checklist

> See [references/secureum-knowledge.md](references/secureum-knowledge.md) for details

#### Top 30 Must-Check Items

| # | Check Item | Description | Reference |
|---|------------|-------------|-----------|
| 1 | pragma version locked | `pragma solidity 0.8.20;` not `^0.8.0` | #2 |
| 2 | Access control completeness | All sensitive functions have permission modifiers | #4-8 |
| 3 | delegatecall target verification | Target address must be trusted | #12 |
| 4 | Reentrancy protection | CEI pattern or ReentrancyGuard | #13-15 |
| 5 | Random number safety | Don't use block.timestamp/blockhash as random source | #17 |
| 6 | Integer overflow | Check unchecked blocks | #19 |
| 7 | Multiply before divide | Avoid precision loss | #20 |
| 8 | ERC20 approve race | approve(0) then approve(new) | #22, #105 |
| 9 | Signature malleability | Verify signature format before ecrecover | #23 |
| 10 | ERC20 return values | Use SafeERC20 | #24 |
| 11 | Unexpected ETH | selfdestruct can force send ETH | #26 |
| 12 | tx.origin authorization | Prohibit for authorization checks | #30 |
| 13 | mapping deletion | Deleting struct doesn't clear internal mapping | #32 |
| 14 | Low-level call return values | Check call/send/delegatecall return values | #37 |
| 15 | External calls in loops | May cause DoS | #43 |
| 16 | Unbounded loops | May cause out of gas | #44 |
| 17 | Event emission | Emit events for critical state changes | #45 |
| 18 | Zero address validation | Check address parameters | #49 |
| 19 | require vs assert | require for conditions, assert for invariants | #52 |
| 20 | Deprecated keywords | Avoid throw/callcode/suicide | #53 |
| 21 | Function visibility | Must be explicitly declared | #54 |
| 22 | Inheritance order | Affects initialization order | #55 |
| 23 | Hash collision | `abi.encodePacked` with multiple variable parameters | #60 |
| 24 | Assembly code | Needs detailed comments and review | #63 |
| 25 | Uninitialized variables | Especially storage pointers | #67-68 |
| 26 | Proxy initialization protection | initializer modifier | #95-96 |
| 27 | Proxy storage layout | Maintain consistency during upgrades | #99 |
| 28 | ERC777 hooks | May trigger reentrancy | #106 |
| 29 | Deflationary/inflationary tokens | Transfer amounts may not match | #107-108 |
| 30 | Two-step permission change | Critical operations need timelock or two-step verification | #162-163 |

#### Audit Process

```
1. Read specification docs → 2. Run static analyzers → 3. Manual code review
4. Run deep tools → 5. Discuss with team → 6. Write report
```

#### Manual Review Approaches

| Method | Starting Point |
|--------|----------------|
| Access Control | Start with permission checks |
| Asset Flow | Start with asset flow |
| Control Flow | Evaluate control flow |
| Data Flow | Evaluate data flow |
| Constraints | Infer constraint conditions |
| Dependencies | Understand dependencies |
| Assumptions | Evaluate assumptions |
| Checklists | Use checklists |

#### Security Design Principles

1. **Least Privilege** - Grant only necessary permissions
2. **Separation of Privilege** | Critical operations require multiple authorizations
3. **Fail-safe Defaults** - Default to deny, not allow
4. **Complete Mediation** - Check permissions on every access
5. **Open Design** - Security doesn't depend on secrecy

## Step 4: Testing & Verification

### Foundry Test Framework

```bash
# Installation
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Initialize
forge init my-test

# Run tests
forge test -vvv

# Fuzz testing
forge test --fuzz-runs 10000

# Gas report
forge test --gas-report
```

### Vulnerability PoC Template

```solidity
// test/ReentrancyPoC.t.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/VulnerableContract.sol";

contract ReentrancyPoC is Test {
    VulnerableContract target;
    Attacker attacker;
    
    function setUp() public {
        target = new VulnerableContract();
        attacker = new Attacker(address(target));
        vm.deal(address(target), 10 ether);
        vm.deal(address(attacker), 1 ether);
    }
    
    function test_Reentrancy() public {
        uint256 initialBalance = address(attacker).balance;
        
        // Execute attack
        attacker.attack{value: 1 ether}();
        
        // Verify: Attacker balance should be greater than initial
        assertGt(address(attacker).balance, initialBalance);
        console.log("Stolen:", address(attacker).balance - initialBalance);
    }
}

contract Attacker {
    VulnerableContract target;
    
    constructor(address _target) {
        target = VulnerableContract(_target);
    }
    
    function attack() external payable {
        target.deposit{value: msg.value}();
        target.withdraw();
    }
    
    receive() external payable {
        if (address(target).balance > 0) {
            target.withdraw();
        }
    }
}
```

### Fuzz Testing Example

```solidity
// test/FuzzTest.t.sol
function testFuzz_Transfer(address to, uint256 amount) public {
    vm.assume(to != address(0));
    vm.assume(to != address(this));
    vm.assume(amount <= token.balanceOf(address(this)));
    
    uint256 balanceBefore = token.balanceOf(to);
    token.transfer(to, amount);
    uint256 balanceAfter = token.balanceOf(to);
    
    assertEq(balanceAfter - balanceBefore, amount);
}
```

### Test Coverage Requirements

| Vulnerability Type | Test Method | Coverage Target |
|-------------------|-------------|-----------------|
| Reentrancy attacks | Unit tests + PoC | All external call points |
| Integer overflow | Fuzz testing | unchecked blocks |
| Access control | Unit tests | All permission functions |
| Business logic | Integration tests | Core functionality paths |

## Step 5: Report Generation

### Report Structure Template

```markdown
# [Project Name] Smart Contract Security Audit Report

## 1. Summary
- **Audit Period**: YYYY-MM-DD to YYYY-MM-DD
- **Audit Scope**: Contract list and versions
- **Security Level Target**: [S]/[M]/[Q]
- **Total Findings**: High X / Medium Y / Low Z / Informational W

## 2. Audit Scope
| File | Lines | Description |
|------|-------|-------------|
| ContractA.sol | 123 | Core logic |
| ContractB.sol | 456 | Proxy contract |

## 3. Findings Details

### [High] R-01: Reentrancy Vulnerability
**Location**: `Vault.sol#withdraw()` line 42  
**EEA Spec**: Violates [M] External Calls  
**Description**: External call before state update, attacker can reenter to drain funds  
**Impact**: Funds can be completely stolen  

**Reproduction Steps**:
1. Deploy attacker contract
2. Call deposit to deposit 1 ETH
3. Call withdraw to trigger reentrancy
4. Verify contract balance is zero

**Recommendation**:
```solidity
// Use ReentrancyGuard or CEI pattern
function withdraw() external nonReentrant {
    // ...
}
```

## 4. Test Coverage
- Static analysis: Slither 4.12.0
- Dynamic testing: Foundry fuzz + unit tests
- Coverage: XX%

## 5. EEA Compliance Statement
| Requirement | Status | Notes |
|-------------|--------|-------|
| [S] No tx.origin | ✅ Pass | - |
| [S] No selfdestruct | ✅ Pass | - |
| [M] External Calls | ❌ Fail | R-01 |
| [Q] Documentation | ⚠️ Partial | Missing architecture diagram |

## 6. Appendix
- Compiler version: solc 0.8.20
- Optimization settings: enabled, runs=200
- Deployment network: Ethereum Mainnet
```

## References

### Detailed Reference Documents
- **EEA Specification Details**: See [references/eea-requirements.md](references/eea-requirements.md)
- **Vulnerability Checklist**: See [references/vulnerability-checklist.md](references/vulnerability-checklist.md)
- **Testing Guide**: See [references/testing-guide.md](references/testing-guide.md)
- **SecureUM Knowledge Base**: See [references/secureum-knowledge.md](references/secureum-knowledge.md) - 200+ audit knowledge points

### External Resources
- EEA EthTrust V3 Specification: https://entethalliance.org/specs/ethtrust-sl/v3/
- Secureum Knowledge Graph: https://github.com/x676f64/secureum-mind_map
- OpenZeppelin Contracts: https://docs.openzeppelin.com/contracts
- EIP Standards List: https://eips.ethereum.org/all
- Mastering Ethereum: https://masteringethereum.xyz/

### Common Tools
| Tool | Purpose | Link |
|------|---------|------|
| Slither | Static analysis | https://github.com/crytic/slither |
| Aderyn | Fast scanning | https://github.com/Cyfrin/aderyn |
| Foundry | Test framework | https://github.com/foundry-rs/foundry |
| Echidna | Fuzz testing | https://github.com/crytic/echidna |
| Mythril | Symbolic execution | https://github.com/ConsenSys/mythril |

## Usage Example

```
User: Help me audit this ERC20 contract for security

AI: I will perform a basic audit following EEA EthTrust specification:

1. **Project Preparation**
   - Please provide contract source code
   - Target security level: [S] Basic
   
2. **Execute Scanning**
   - Running Slither static analysis...
   - Detected the following issues...

3. **Manual Review**
   - Checking access control...
   - Checking reentrancy risks...
```

## Audit Capability Assessment Framework

### Audit Quality Self-Assessment

After completing an audit, use this framework for self-evaluation:

| Dimension | Check Item | Assessment Method |
|-----------|------------|-------------------|
| Coverage | Did you review all core contracts | Contract checklist |
| Depth | Did you discover complex logic vulnerabilities | PoC verification |
| Tools | Did you use automated tools | Slither/Aderyn reports |
| Comparison | Compare with professional reports | Gap analysis |

### Capability Level Classification

| Level | Standard | Typical Performance |
|-------|----------|---------------------|
| Junior | Can find basic vulnerabilities | Reentrancy, permission issues, overflow |
| Intermediate | Can find business logic issues | Price manipulation, liquidation issues |
| Senior | Can find complex interaction vulnerabilities | Cross-chain, composability attacks |
| Expert | Can design security architecture | Formal verification, zero-knowledge proofs |

### Audit Time Reference

| Contract Size | Junior | Intermediate | Senior |
|---------------|--------|--------------|--------|
| <500 lines | 2 hours | 1 hour | 30 minutes |
| 500-2000 lines | 8 hours | 4 hours | 2 hours |
| 2000-10000 lines | 40 hours | 20 hours | 10 hours |
| >10000 lines | 2 weeks+ | 1 week+ | 3 days+ |

### Common Missed Checks

After completing an audit, check if you missed:

- [ ] Callback function security
- [ ] Multi-signature/timelock configuration
- [ ] Special token compatibility (rebasing, fee-on-transfer)
- [ ] Cross-chain message verification
- [ ] Price precision issues
- [ ] Gas limit boundary conditions
- [ ] Upgrade pattern security
- [ ] Signature verification security

### 🎯 Professional Audit Comparison Template

After completing an audit, compare using this format:

```markdown
## My Findings vs Professional Audit

### Matched Items
| My Finding | Professional Audit Finding | Match Level |
|------------|---------------------------|-------------|
| Reentrancy risk | ✅ Usually found | High |
| Permission issues | ✅ Usually found | High |

### Missed Items
| Professional Finding | Why I Missed It |
|---------------------|-----------------|
| Math boundaries | Need fuzz testing |
| Interaction vulnerabilities | Need symbolic execution |

### Capability Score
- This round score: X/100
- Cumulative average: Y/100
```

### 📈 Audit Capability Improvement Path

| Stage | Target | Method |
|-------|--------|--------|
| Junior→Intermediate | 78→85 points | More practice cases, learn vulnerability patterns |
| Intermediate→Senior | 85→92 points | Use toolchain, deep protocol research |
| Senior→Expert | 92→98 points | Formal verification, innovative attack vectors |

### 🔧 Toolchain Gap Solution (Addressing 60% gap)

**Problem**: AI cannot directly run Slither/Foundry

**Solution**: Request user to run tools, AI analyzes results

```
Please provide tool scan results for audit:

# Slither quick scan
slither . --exclude-dependencies --json slither.json

# Or Aderyn scan
aderyn . -o report.md

Provide the output to me, and I will combine tool findings with deep analysis.
```

**Tool Output Mapping**:

| Slither Detector | AI Analysis Focus |
|------------------|-------------------|
| reentrancy-eth | Verify reentrancy protection |
| uninitialized-state | Check initialization |
| arbitrary-send | Verify sending logic |
| controlled-delegatecall | Verify target address |

### ⏱️ Time Optimization Solution (Addressing 25% gap)

**Problem**: Limited audit time

**Solution**: Focus on high-risk modules

**35-minute Allocation**:
```
Access Control (5 minutes): owner/governor/permission modifiers
Reentrancy Check (5 minutes): external calls + state update order
Token Security (10 minutes): SafeERC20/return value checks
Critical Vulnerabilities (10 minutes): liquidation/price/permission bypass
Report Output (5 minutes): formatted output
```

**High-Risk Function Priority**:
1. withdraw/transfer/claim
2. liquidate/absorb/seize
3. setOwner/setConfig
4. getPrice/updatePrice

### 📚 Knowledge Gap Solution (Addressing 15% gap)

**Problem**: Unfamiliar with new protocol features

**Solution**: Protocol type knowledge base

| Protocol Type | Core Check Points |
|---------------|-------------------|
| AMM | Price calculation, liquidity, slippage |
| Lending | Liquidation factors, interest rates, oracles |
| Cross-chain | Signature verification, message replay |
| Aggregator | Interaction order, composability risks |
| NFT | Transfers, royalties, authorization |

See: [references/toolchain-guide.md](references/toolchain-guide.md) for details