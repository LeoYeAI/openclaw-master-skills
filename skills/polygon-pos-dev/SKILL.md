---
name: polygon-pos-dev
description: Comprehensive guide for Polygon PoS blockchain development. Use when deploying smart contracts to Polygon, testing on Amoy testnet, getting test tokens from faucets, or verifying contracts on Polygonscan. Supports Foundry framework with deployment scripts and testing strategies.
---

# Polygon PoS Development

End-to-end guide for developing and deploying smart contracts on Polygon PoS blockchain using Foundry.

## Overview

Polygon PoS is an EVM-compatible Proof-of-Stake sidechain for Ethereum with:
- Low transaction costs (fraction of a cent)
- Fast block times (~2 seconds)
- High throughput (65,000+ TPS theoretical)
- Full Ethereum tooling compatibility
- POL token for gas fees

**Default Network**: Amoy Testnet (Chain ID: 80002) - Use for all testing before mainnet.

---

## 🚀 Quick Navigation

**For Agents/Fast Deployment**: Jump to [Quick Start Path](#quick-start-path) (5-10 min)

**For Production/Thorough Testing**: Jump to [Complete Development Path](#complete-development-path) (30-60 min)

**For Reference**: See sections below for [Network Configuration](#network-configuration), [Faucets](#getting-testnet-tokens), [Troubleshooting](#troubleshooting)

---

## Two Development Paths

Choose based on your needs:

| Aspect | Quick Start Path | Complete Development Path |
|--------|------------------|---------------------------|
| **Time** | 5-10 minutes | 30-60 minutes |
| **Best for** | Prototypes, demos, simple contracts | Production, complex systems, mainnet |
| **Testing** | Basic compilation check | Unit tests, integration tests, fork tests |
| **Scripts Used** | None (direct forge commands) | Direct forge commands with all options |
| **Documentation** | Minimal | Full reference guides |
| **Verification** | Automatic during deploy | Multiple methods with troubleshooting |
| **Agent-Friendly** | ✅ Optimized for speed | ⚠️ Comprehensive but slower |

### Path 1: Quick Start (Minimal Time - Agent-Friendly)
**Best for**: Fast deployment, simple contracts, prototyping
**Time**: 5-10 minutes
**What you get**: Contract deployed and verified on testnet

Skip to [Quick Start Path](#quick-start-path) below.

### Path 2: Complete Guide (Full Development Workflow)
**Best for**: Production contracts, complex systems, thorough testing
**Time**: 30-60 minutes
**What you get**: Fully tested, optimized, and production-ready deployment

Skip to [Complete Development Path](#complete-development-path) below.

---

## Quick Start Path

**Goal**: Deploy a contract to Polygon Amoy testnet in minimal steps.

### Prerequisites

- Foundry installed: `curl -L https://foundry.paradigm.xyz | bash && foundryup`
- Wallet with private key
- Polygonscan API key (get from https://polygonscan.com/myapikey)

### Step 1: Create Project (30 seconds)

```bash
forge init my-polygon-project
cd my-polygon-project
```

### Step 2: Configure Environment (1 minute)

Create `.env` file:
```bash
PRIVATE_KEY=your_private_key_without_0x_prefix
```

### Step 3: Get Testnet Tokens (2 minutes)

Visit: https://www.alchemy.com/faucets/polygon-amoy
- Paste your wallet address
- Claim 0.2-0.5 POL (no signup needed)

### Step 4: Deploy (1 minute)

```bash
# Deploy to Amoy testnet
forge script script/Counter.s.sol:CounterScript \
    --rpc-url https://rpc-amoy.polygon.technology \
    --private-key $PRIVATE_KEY \
    --broadcast
```

**Done!** Your contract is deployed and verified on Amoy testnet.

View at: `https://amoy.polygonscan.com/address/YOUR_CONTRACT_ADDRESS`

---

## Complete Development Path

**Goal**: Production-ready deployment with comprehensive testing and optimization.

### Phase 1: Setup (5 minutes)

1. **Install Foundry**:
```bash
curl -L https://foundry.paradigm.xyz | bash
foundryup
```

2. **Initialize Project**:
```bash
forge init my-polygon-project
cd my-polygon-project
```

3. **Configure for Polygon**:

Update `foundry.toml` with Polygon settings:
```toml
[profile.default]
src = "src"
out = "out"
libs = ["lib"]
solc_version = "0.8.24"
optimizer = true
optimizer_runs = 200

[rpc_endpoints]
amoy = "https://rpc-amoy.polygon.technology"
polygon = "https://polygon-rpc.com"

[etherscan]
amoy = { key = "${POLYGONSCAN_API_KEY}", url = "https://api-amoy.polygonscan.com/api" }
polygon = { key = "${POLYGONSCAN_API_KEY}", url = "https://api.polygonscan.com/api" }
```

4. **Setup Environment**:

Create `.env` file:
```bash
PRIVATE_KEY=your_private_key
WALLET_ADDRESS=0xYourAddress
POLYGONSCAN_API_KEY=your_api_key
```

### Phase 2: Write & Test Contracts (10-20 minutes)

1. **Write Contract** (or use `assets/sample-contracts/HelloWorld.sol` as template)

2. **Write Tests**:
```solidity
// test/MyContract.t.sol
import "forge-std/Test.sol";
import "../src/MyContract.sol";

contract MyContractTest is Test {
    MyContract public myContract;
    
    function setUp() public {
        myContract = new MyContract();
    }
    
    function testDeployment() public {
        assertEq(myContract.owner(), address(this));
    }
}
```

3. **Run Tests**:
```bash
forge test -vvv                    # Run tests
forge test --gas-report            # Check gas usage
forge coverage                     # Check coverage
```

4. **Fork Testing** (optional):
```bash
# Test against real Polygon state
forge test --fork-url https://polygon-rpc.com
```

See `references/testing-strategies.md` for comprehensive testing patterns.

### Phase 3: Get Testnet Tokens (2-5 minutes)

Visit one of these faucets:

**Alchemy** (recommended - no auth): https://www.alchemy.com/faucets/polygon-amoy
**QuickNode**: https://faucet.quicknode.com/polygon/amoy
**GetBlock**: https://getblock.io/faucet/matic-amoy/
**Chainlink**: https://faucets.chain.link/polygon-amoy
**LearnWeb3**: https://learnweb3.io/faucets/polygon_amoy/

### Phase 4: Deploy to Testnet (2-5 minutes)
```bash
forge script script/Deploy.s.sol \
    --rpc-url amoy \
    --private-key $PRIVATE_KEY \
    --broadcast \
    --verify \
    --etherscan-api-key $POLYGONSCAN_API_KEY
```

Create a deployment script in `script/Deploy.s.sol`:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Script.sol";
import "../src/YourContract.sol";

contract DeployScript is Script {
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        
        vm.startBroadcast(deployerPrivateKey);
        
        // Deploy your contract
        YourContract yourContract = new YourContract();
        
        vm.stopBroadcast();
        
        console.log("Contract deployed to:", address(yourContract));
    }
}
```

See `references/foundry-deployment.md` for advanced deployment patterns.

### Phase 5: Verify Contract (1-2 minutes)

If not verified during deployment:
```bash
forge verify-contract \
    CONTRACT_ADDRESS \
    src/MyContract.sol:MyContract \
    --chain-id 80002 \
    --etherscan-api-key $POLYGONSCAN_API_KEY
```

See `references/contract-verification.md` for troubleshooting verification issues.

### Phase 6: Test on Testnet (5-10 minutes)

1. **View on Explorer**: https://amoy.polygonscan.com/address/CONTRACT_ADDRESS
2. **Interact with Contract**: Use cast or web interface
3. **Test All Functions**: Verify behavior matches expectations
4. **Monitor Gas Costs**: Check if optimization needed

### Phase 7: Deploy to Mainnet (5 minutes)

**⚠️ IMPORTANT: Complete mainnet deployment checklist first!**

See [Mainnet Deployment Checklist](#mainnet-deployment-checklist) below.

```bash
forge script script/Deploy.s.sol \
    --rpc-url polygon \
    --private-key $PRIVATE_KEY \
    --broadcast \
    --verify \
    --etherscan-api-key $POLYGONSCAN_API_KEY
```

**End of Complete Development Path** ✅

## Network Configuration

### Amoy Testnet (Recommended for Testing)

| Property | Value |
|----------|-------|
| Network Name | Polygon Amoy |
| Chain ID | 80002 |
| Currency | POL |
| RPC URL | https://rpc-amoy.polygon.technology |
| WebSocket | wss://polygon-amoy.drpc.org |
| Explorer | https://amoy.polygonscan.com |
| Faucets | Multiple (see below) |

### Polygon Mainnet

| Property | Value |
|----------|-------|
| Network Name | Polygon |
| Chain ID | 137 |
| Currency | POL |
| RPC URL | https://polygon-rpc.com |
| WebSocket | wss://polygon.drpc.org |
| Explorer | https://polygonscan.com |

## Getting Testnet Tokens

Multiple faucets available for Amoy testnet POL tokens.

### Quick Access

Run the faucet helper script:
```bash
./scripts/get-testnet-tokens.sh
```

### Available Faucets

**Alchemy Faucet** (Recommended - No auth required)
- URL: https://www.alchemy.com/faucets/polygon-amoy
- Amount: 0.5 POL/day (with account), 0.2 POL/day (without)
- Requirements: None

**QuickNode Faucet**
- URL: https://faucet.quicknode.com/polygon/amoy
- Amount: 0.1 POL/day (2x with tweet)
- Requirements: Connect wallet

**GetBlock Faucet**
- URL: https://getblock.io/faucet/matic-amoy/
- Amount: 0.1 POL/day
- Requirements: Login

**Chainlink Faucet**
- URL: https://faucets.chain.link/polygon-amoy
- Amount: 0.1 POL/day
- Requirements: GitHub auth

**LearnWeb3 Faucet**
- URL: https://learnweb3.io/faucets/polygon_amoy/
- Amount: 0.1 POL/day
- Requirements: GitHub auth

**Tips:**
- Most faucets limit to 1 request per 24 hours
- If rate-limited, try a different faucet
- Some offer bonus tokens for tweeting

## Deployment Workflow

### Environment Setup

Create `.env` file (see `assets/sample-contracts/.env.example`):
```bash
PRIVATE_KEY=your_private_key_here
WALLET_ADDRESS=0xYourAddress
POLYGONSCAN_API_KEY=your_api_key_here
```

Add to `.gitignore`:
```
.env
broadcast/
deployments/
```

### Deploy to Testnet

**Option 1: Use helper script** (recommended)
```bash
./scripts/deploy-foundry.sh
```

**Option 2: Manual deployment**
```bash
forge script script/Deploy.s.sol \
    --rpc-url amoy \
    --private-key $PRIVATE_KEY \
    --broadcast \
    --verify
```

**Option 3: Deploy without verification**
```bash
forge script script/Deploy.s.sol \
    --rpc-url amoy \
    --private-key $PRIVATE_KEY \
    --broadcast
```

### Deploy to Mainnet

**⚠️ IMPORTANT: Test thoroughly on Amoy first!**

```bash
# Use deployment script and select mainnet option
./scripts/deploy-foundry.sh
```

For detailed deployment patterns, see `references/foundry-deployment.md`.

## Testing Strategies

### Local Testing

Write tests in `test/` directory:
```solidity
// test/MyContract.t.sol
import "forge-std/Test.sol";
import "../src/MyContract.sol";

contract MyContractTest is Test {
    MyContract public myContract;
    
    function setUp() public {
        myContract = new MyContract();
    }
    
    function testFunction() public {
        // Test logic
    }
}
```

Run tests:
```bash
forge test              # Run all tests
forge test -vvv         # Verbose output
forge test --gas-report # Show gas usage
```

### Fork Testing

Test against real Polygon state:
```bash
forge test --fork-url https://polygon-rpc.com
```

### Testnet Testing

Deploy to Amoy and test with real transactions. See `references/testing-strategies.md` for comprehensive testing patterns.

## Contract Verification

Verification makes your contract code public and trustworthy.

### During Deployment (Recommended)

```bash
forge script script/Deploy.s.sol \
    --rpc-url amoy \
    --private-key $PRIVATE_KEY \
    --broadcast \
    --verify \
    --etherscan-api-key $POLYGONSCAN_API_KEY
```

### After Deployment

**Option 1: Use helper script**
```bash
./scripts/verify-contract.sh
```

**Option 2: Manual verification**
```bash
forge verify-contract \
    CONTRACT_ADDRESS \
    src/MyContract.sol:MyContract \
    --chain-id 80002 \
    --etherscan-api-key $POLYGONSCAN_API_KEY \
    --verifier-url https://api-amoy.polygonscan.com/api
```

### With Constructor Arguments

```bash
forge verify-contract \
    CONTRACT_ADDRESS \
    src/MyContract.sol:MyContract \
    --chain-id 80002 \
    --etherscan-api-key $POLYGONSCAN_API_KEY \
    --constructor-args $(cast abi-encode "constructor(address,uint256)" 0x123... 1000)
```

For troubleshooting verification issues, see `references/contract-verification.md`.

## Common Workflows

### Which Path Should I Use?

**Use Quick Start Path when**:
- You need fast deployment (prototyping, demos)
- Contract is simple and low-risk
- You're an AI agent with limited time
- Testing is minimal or done elsewhere

**Use Complete Development Path when**:
- Deploying to mainnet
- Contract handles real value
- Complex logic requiring thorough testing
- Team collaboration and code review needed
- Security is critical

### Mainnet Deployment Checklist

Before deploying to mainnet:
- [ ] All tests passing (`forge test`)
- [ ] Deployed and tested on Amoy testnet
- [ ] Contract verified on Amoy
- [ ] Security review completed
- [ ] Gas optimization done
- [ ] Documentation complete
- [ ] Constructor arguments double-checked
- [ ] Sufficient POL in wallet for gas
- [ ] Deployment script tested
- [ ] Team notified of deployment

## Sample Contract Pattern

Example smart contract structure for Polygon:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

contract HelloWorld {
    address public owner;
    string public message;
    uint256 public updateCount;
    
    event MessageUpdated(address indexed updater, string newMessage);
    
    error NotOwner();
    error EmptyMessage();
    
    constructor(string memory initialMessage) {
        owner = msg.sender;
        message = initialMessage;
    }
    
    modifier onlyOwner() {
        if (msg.sender != owner) revert NotOwner();
        _;
    }
    
    function setMessage(string calldata newMessage) external {
        if (bytes(newMessage).length == 0) revert EmptyMessage();
        message = newMessage;
        updateCount++;
        emit MessageUpdated(msg.sender, newMessage);
    }
}
```

**Key patterns:**
- Use custom errors instead of require strings (gas-efficient)
- Emit events for important state changes
- Use modifiers for access control
- Optimize for Polygon's low gas costs

## Safety Rules

1. **Test First**: Always test on Amoy before mainnet
2. **Never Commit Keys**: Add .env to .gitignore
3. **Verify Contracts**: Always verify for transparency
4. **Check Network**: Double-check chain ID before deployment
5. **Sufficient Balance**: Ensure enough POL for gas
6. **Save Addresses**: Document deployed contract addresses
7. **Audit Code**: Security review before mainnet
8. **Use Scripts**: Automate deployments to reduce errors
9. **Backup Keys**: Securely backup private keys
10. **Test Verification**: Verify contracts on testnet first

## Troubleshooting

### Insufficient Funds for Gas

**Error**: `insufficient funds for gas * price + value`

**Solution**: Get testnet POL from faucets (run `./scripts/get-testnet-tokens.sh`)

### Contract Not Found

**Error**: `src/MyContract.sol:MyContract not found`

**Solution**: Check file path and contract name match exactly

### RPC Connection Issues

**Error**: `failed to get chain id`

**Solution**: 
- Check internet connection
- Try alternative RPC URL
- Use dedicated RPC provider (Alchemy, QuickNode)

### Verification Failed

**Error**: `bytecode does not match`

**Solution**:
- Wait 1-2 minutes for contract to be indexed
- Check constructor arguments are correct
- Verify compiler settings match deployment

### Gas Estimation Failed

**Error**: `gas estimation failed`

**Solution**:
- Check contract logic for reverts
- Ensure sufficient balance
- Check function parameters

## Resources

**Foundry Documentation**
- Book: https://book.getfoundry.sh/
- GitHub: https://github.com/foundry-rs/foundry

**Polygon Documentation**
- Docs: https://docs.polygon.technology/
- Gas Station: https://gasstation.polygon.technology/
- Faucets: https://faucet.polygon.technology/

**Block Explorers**
- Amoy: https://amoy.polygonscan.com
- Mainnet: https://polygonscan.com

**RPC Providers**
- Alchemy: https://www.alchemy.com/
- QuickNode: https://www.quicknode.com/
- Infura: https://infura.io/

**Community**
- Discord: https://discord.com/invite/0xPolygonCommunity
- Telegram: https://t.me/polygonhq

## Reference Files

For detailed information:
- `references/foundry-deployment.md` - Complete deployment guide
- `references/testing-strategies.md` - Testing best practices
- `references/contract-verification.md` - Verification troubleshooting

## Scripts

