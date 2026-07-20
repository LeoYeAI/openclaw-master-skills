# Testing Strategies for Polygon PoS

Comprehensive testing guide for smart contracts deploying to Polygon PoS.

## Testing Hierarchy

1. **Unit Tests** - Test individual functions (local)
2. **Integration Tests** - Test contract interactions (local/fork)
3. **Testnet Deployment** - Test on Amoy testnet (real network)
4. **Mainnet** - Production deployment

## Local Testing with Forge

### Writing Tests

Create test file `test/MyContract.t.sol`:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Test.sol";
import "../src/MyContract.sol";

contract MyContractTest is Test {
    MyContract public myContract;
    address public owner;
    address public user1;
    
    function setUp() public {
        owner = address(this);
        user1 = address(0x1);
        
        myContract = new MyContract();
    }
    
    function testInitialState() public {
        assertEq(myContract.owner(), owner);
    }
    
    function testSetValue() public {
        myContract.setValue(42);
        assertEq(myContract.getValue(), 42);
    }
    
    function testFailUnauthorized() public {
        vm.prank(user1); // Call as user1
        myContract.ownerOnlyFunction(); // Should fail
    }
    
    function testRevertWithMessage() public {
        vm.expectRevert("Not authorized");
        vm.prank(user1);
        myContract.ownerOnlyFunction();
    }
}
```

### Running Tests

Basic test run:
```bash
forge test
```

Verbose output:
```bash
forge test -vvv
```

Test specific contract:
```bash
forge test --match-contract MyContractTest
```

Test specific function:
```bash
forge test --match-test testSetValue
```

### Gas Reporting

```bash
forge test --gas-report
```

Output shows gas usage per function.

### Coverage

```bash
forge coverage
```

Generate detailed coverage report:
```bash
forge coverage --report lcov
```

## Advanced Testing Patterns

### Testing Events

```solidity
function testEventEmission() public {
    vm.expectEmit(true, true, false, true);
    emit ValueChanged(owner, 42);
    
    myContract.setValue(42);
}
```

### Testing Time-Dependent Logic

```solidity
function testTimelock() public {
    myContract.lock();
    
    // Fast forward 1 day
    vm.warp(block.timestamp + 1 days);
    
    myContract.unlock();
}
```

### Testing with Different Senders

```solidity
function testMultipleUsers() public {
    address alice = address(0x1);
    address bob = address(0x2);
    
    vm.prank(alice);
    myContract.deposit{value: 1 ether}();
    
    vm.prank(bob);
    myContract.deposit{value: 2 ether}();
    
    assertEq(myContract.balanceOf(alice), 1 ether);
    assertEq(myContract.balanceOf(bob), 2 ether);
}
```

### Fuzzing Tests

```solidity
function testFuzz_SetValue(uint256 x) public {
    // Forge will test with random values
    vm.assume(x < 1000000); // Add constraints
    
    myContract.setValue(x);
    assertEq(myContract.getValue(), x);
}
```

### Invariant Testing

```solidity
contract InvariantTest is Test {
    MyContract public myContract;
    
    function setUp() public {
        myContract = new MyContract();
    }
    
    function invariant_TotalSupplyNeverExceeds() public {
        assertLe(myContract.totalSupply(), 1000000 * 10**18);
    }
}
```

Run invariant tests:
```bash
forge test --match-contract InvariantTest
```

## Fork Testing

Test against mainnet state without deploying.

### Setup Fork

```solidity
contract ForkTest is Test {
    uint256 polygonFork;
    
    function setUp() public {
        polygonFork = vm.createFork("https://polygon-rpc.com");
        vm.selectFork(polygonFork);
    }
    
    function testOnFork() public {
        // Test against real Polygon state
        address usdcAddress = 0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174;
        IERC20 usdc = IERC20(usdcAddress);
        
        uint256 balance = usdc.balanceOf(someAddress);
        console.log("USDC Balance:", balance);
    }
}
```

### Fork from Specific Block

```solidity
uint256 polygonFork = vm.createFork(
    "https://polygon-rpc.com",
    12345678  // block number
);
```

### Test Interactions with Real Contracts

```solidity
function testSwapOnUniswap() public {
    // Fork mainnet
    uint256 fork = vm.createFork("https://polygon-rpc.com");
    vm.selectFork(fork);
    
    // Interact with real Uniswap contracts
    IUniswapV2Router router = IUniswapV2Router(0x...");
    
    // Test your contract's interaction
    myContract.swapTokens(router, ...);
}
```

## Testnet Testing (Amoy)

### Prerequisites

1. Get testnet POL from faucets:
```bash
./scripts/get-testnet-tokens.sh
```

2. Configure `.env`:
```
PRIVATE_KEY=your_private_key
WALLET_ADDRESS=your_address
```

### Deploy to Testnet

```bash
forge script script/Deploy.s.sol \
    --rpc-url amoy \
    --private-key $PRIVATE_KEY \
    --broadcast
```

Or use helper:
```bash
./scripts/deploy-foundry.sh
```

### Interact with Deployed Contract

Using cast:
```bash
# Read function
cast call CONTRACT_ADDRESS "getValue()" --rpc-url amoy

# Write function
cast send CONTRACT_ADDRESS \
    "setValue(uint256)" 42 \
    --rpc-url amoy \
    --private-key $PRIVATE_KEY
```

### Monitor Transactions

Check on Polygonscan:
```
https://amoy.polygonscan.com/tx/TX_HASH
```

### Test Checklist for Testnet

- [ ] Deploy contract successfully
- [ ] Verify contract on Polygonscan
- [ ] Test all write functions
- [ ] Test access control (owner vs user)
- [ ] Test edge cases (zero values, max values)
- [ ] Test error conditions
- [ ] Test event emission
- [ ] Monitor gas costs
- [ ] Test with multiple accounts
- [ ] Test contract upgrades (if applicable)

## Integration Testing

Test multiple contracts working together.

```solidity
contract IntegrationTest is Test {
    TokenA public tokenA;
    TokenB public tokenB;
    Exchange public exchange;
    
    address public user1;
    address public user2;
    
    function setUp() public {
        user1 = address(0x1);
        user2 = address(0x2);
        
        tokenA = new TokenA();
        tokenB = new TokenB();
        exchange = new Exchange(address(tokenA), address(tokenB));
        
        // Fund users
        tokenA.mint(user1, 1000 * 10**18);
        tokenB.mint(user2, 1000 * 10**18);
    }
    
    function testCompleteSwap() public {
        // User1 approves exchange
        vm.prank(user1);
        tokenA.approve(address(exchange), 100 * 10**18);
        
        // User2 approves exchange
        vm.prank(user2);
        tokenB.approve(address(exchange), 100 * 10**18);
        
        // Execute swap
        vm.prank(user1);
        exchange.swap(100 * 10**18);
        
        // Verify balances changed correctly
        assertEq(tokenA.balanceOf(user1), 900 * 10**18);
        assertEq(tokenB.balanceOf(user1), 100 * 10**18);
    }
}
```

## Gas Optimization Testing

### Compare Gas Usage

```solidity
function testGasComparison() public {
    uint256 gasBefore = gasleft();
    myContract.functionV1();
    uint256 gasUsedV1 = gasBefore - gasleft();
    
    gasBefore = gasleft();
    myContract.functionV2();
    uint256 gasUsedV2 = gasBefore - gasleft();
    
    console.log("V1 gas:", gasUsedV1);
    console.log("V2 gas:", gasUsedV2);
    assertLt(gasUsedV2, gasUsedV1, "V2 should use less gas");
}
```

### Gas Snapshots

Create baseline:
```bash
forge snapshot
```

Compare after changes:
```bash
forge snapshot --diff
```

## CI/CD Integration

### GitHub Actions Example

`.github/workflows/test.yml`:

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
        with:
          submodules: recursive
      
      - name: Install Foundry
        uses: foundry-rs/foundry-toolchain@v1
      
      - name: Run tests
        run: forge test -vvv
      
      - name: Check coverage
        run: forge coverage
```

## Security Testing

### Slither Static Analysis

Install:
```bash
pip3 install slither-analyzer
```

Run:
```bash
slither .
```

### Mythril

```bash
docker run -v $(pwd):/tmp mythril/myth analyze /tmp/src/MyContract.sol
```

## Best Practices

1. **Test Coverage**: Aim for >90% code coverage
2. **Test Edge Cases**: Zero values, max values, overflows
3. **Test Access Control**: Ensure only authorized users can call functions
4. **Test Events**: Verify events are emitted correctly
5. **Gas Tests**: Monitor and optimize gas usage
6. **Fork Testing**: Test integrations with real contracts
7. **Testnet First**: Always test on Amoy before mainnet
8. **Regression Tests**: Add tests when bugs are found
9. **Fuzz Testing**: Use fuzzing for numeric inputs
10. **Integration Tests**: Test full user flows

## Troubleshooting

### Test Fails Locally But Passes in CI

- Check Foundry versions match
- Verify submodules are updated
- Check environment variables

### Fork Tests Fail

- RPC provider rate limiting (use dedicated provider)
- Block number changed (pin to specific block)
- Contract state changed (use older block)

### Gas Discrepancies

- Testnet vs mainnet gas prices differ
- Network congestion affects gas
- Use gas snapshots for consistent comparison

## Resources

- Foundry Testing: https://book.getfoundry.sh/forge/tests
- Forge Std: https://github.com/foundry-rs/forge-std
- Polygon Testnet: https://docs.polygon.technology/
