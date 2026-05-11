# Solidity Testing Guide

This document covers smart contract testing methods including unit testing, fuzz testing, and formal verification.

## 1. Foundry Test Framework

### 1.1 Installation & Configuration

```bash
# Install Foundry
curl -L https://foundry.paradigm.xyz | bash
foundryup

# Initialize project
forge init my-project
cd my-project

# Project structure
my-project/
├── src/              # Contract source code
├── test/             # Test files
├── lib/              # Dependencies
└── foundry.toml      # Configuration
```

### 1.2 Basic Testing

```solidity
// test/MyContract.t.sol
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "forge-std/Test.sol";
import "../src/MyContract.sol";

contract MyContractTest is Test {
    MyContract target;

    function setUp() public {
        target = new MyContract();
    }

    function test_BasicFunctionality() public {
        // Test logic here
        assertEq(target.value(), 0);
    }
}
```

### 1.3 Fuzz Testing

```solidity
function testFuzz_Transfer(address to, uint256 amount) public {
    vm.assume(to != address(0));
    vm.assume(amount <= target.balanceOf(address(this)));

    uint256 balanceBefore = target.balanceOf(to);
    target.transfer(to, amount);

    assertEq(target.balanceOf(to), balanceBefore + amount);
}
```

### 1.4 Invariant Testing

```solidity
function invariant_TotalSupply() public {
    // This runs after every test
    assertEq(target.totalSupply(), expectedSupply);
}
```

---

## 2. Hardhat Test Framework

### 2.1 Installation

```bash
npm install --save-dev hardhat @nomicfoundation/hardhat-toolbox
npx hardhat init
```

### 2.2 Basic Testing

```javascript
// test/MyContract.js
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("MyContract", function () {
  it("Should return the correct value", async function () {
    const MyContract = await ethers.getContractFactory("MyContract");
    const contract = await MyContract.deploy();
    await contract.deployed();

    expect(await contract.value()).to.equal(0);
  });
});
```

---

## 3. Fuzz Testing Tools

### 3.1 Echidna

```yaml
# echidna.yaml
testMode: assertion
testLimit: 500000
seqLen: 100
```

```solidity
// Invariant tests for Echidna
function echidna_balanceNeverNegative() public returns (bool) {
    return balance >= 0;
}
```

### 3.2 Foundry Fuzz

```bash
# Run fuzz tests with more runs
forge test --fuzz-runs 10000

# Show coverage
forge coverage
```

---

## 4. Formal Verification

### 4.1 Certora

```bash
# Install Certora
pip install certora-cli

# Run verification
certoraRun contracts/MyContract.sol --verify MyContract:spec.spec
```

### 4.2 Scribble

```solidity
/// #if_succeeds $result == old(balance) - amount;
function withdraw(uint256 amount) public returns (uint256) {
    balance -= amount;
    return balance;
}
```

---

## 5. Test Coverage Requirements

| Vulnerability Type | Test Method | Coverage Target |
|-------------------|-------------|-----------------|
| Reentrancy | Unit + PoC | All external calls |
| Integer overflow | Fuzz | unchecked blocks |
| Access control | Unit | All permission functions |
| Business logic | Integration | Core paths |

---

## 6. Best Practices

1. **Test coverage**: Aim for >90% line coverage
2. **Fuzz testing**: Run at least 10,000 iterations
3. **Invariant testing**: Define key invariants
4. **Gas reporting**: Monitor gas usage
5. **Upgrade testing**: Test proxy upgrades