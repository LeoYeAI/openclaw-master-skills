# Foundry Deployment Guide for Polygon PoS

Comprehensive guide for deploying smart contracts to Polygon PoS using Foundry.

## Installation and Setup

### Install Foundry

```bash
curl -L https://foundry.paradigm.xyz | bash
foundryup
```

Verify installation:
```bash
forge --version
cast --version
```

### Initialize New Project

```bash
forge init my-project
cd my-project
```

This creates:
- `src/` - Smart contracts
- `test/` - Test files
- `script/` - Deployment scripts
- `lib/` - Dependencies
- `foundry.toml` - Configuration

## Project Configuration

### foundry.toml for Polygon

Create or update `foundry.toml`:

```toml
[profile.default]
src = "src"
out = "out"
libs = ["lib"]
solc_version = "0.8.24"
optimizer = true
optimizer_runs = 200
via_ir = false

[rpc_endpoints]
amoy = "https://rpc-amoy.polygon.technology"
polygon = "https://polygon-rpc.com"

[etherscan]
amoy = { key = "${POLYGONSCAN_API_KEY}", url = "https://api-amoy.polygonscan.com/api" }
polygon = { key = "${POLYGONSCAN_API_KEY}", url = "https://api.polygonscan.com/api" }

# Amoy testnet profile
[profile.amoy]
eth_rpc_url = "https://rpc-amoy.polygon.technology"
etherscan_api_key = "${POLYGONSCAN_API_KEY}"

# Polygon mainnet profile
[profile.polygon]
eth_rpc_url = "https://polygon-rpc.com"
etherscan_api_key = "${POLYGONSCAN_API_KEY}"
```

### Environment Variables

Create `.env` file (never commit this):

```bash
PRIVATE_KEY=your_private_key_here
POLYGONSCAN_API_KEY=your_polygonscan_api_key
WALLET_ADDRESS=your_wallet_address

# RPC URLs (optional - can use foundry.toml)
AMOY_RPC_URL=https://rpc-amoy.polygon.technology
POLYGON_RPC_URL=https://polygon-rpc.com
```

Add to `.gitignore`:
```
.env
broadcast/
deployments/
```

## Writing Deployment Scripts

### Basic Deployment Script

Create `script/Deploy.s.sol`:

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.24;

import "forge-std/Script.sol";
import "../src/MyContract.sol";

contract DeployScript is Script {
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        
        vm.startBroadcast(deployerPrivateKey);
        
        MyContract myContract = new MyContract();
        
        vm.stopBroadcast();
        
        console.log("MyContract deployed to:", address(myContract));
    }
}
```

### Deployment with Constructor Arguments

```solidity
contract DeployScript is Script {
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        
        // Constructor arguments
        address owner = vm.envAddress("WALLET_ADDRESS");
        uint256 initialSupply = 1_000_000 * 10**18;
        
        vm.startBroadcast(deployerPrivateKey);
        
        MyToken token = new MyToken(owner, initialSupply);
        
        vm.stopBroadcast();
        
        console.log("Token deployed to:", address(token));
        console.log("Owner:", owner);
        console.log("Initial supply:", initialSupply);
    }
}
```

### Multi-Contract Deployment

```solidity
contract DeployScript is Script {
    function run() external {
        uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
        
        vm.startBroadcast(deployerPrivateKey);
        
        // Deploy in order
        TokenA tokenA = new TokenA();
        console.log("TokenA:", address(tokenA));
        
        TokenB tokenB = new TokenB();
        console.log("TokenB:", address(tokenB));
        
        // Deploy contract that depends on others
        Exchange exchange = new Exchange(
            address(tokenA),
            address(tokenB)
        );
        console.log("Exchange:", address(exchange));
        
        vm.stopBroadcast();
    }
}
```

## Deployment Process

### 1. Compile Contracts

```bash
forge build
```

Check for errors and warnings.

### 2. Dry Run (Simulation)

Test deployment without broadcasting:

```bash
forge script script/Deploy.s.sol --rpc-url amoy
```

### 3. Deploy to Testnet

```bash
forge script script/Deploy.s.sol \
    --rpc-url amoy \
    --private-key $PRIVATE_KEY \
    --broadcast
```

Or using the helper script:
```bash
./scripts/deploy-foundry.sh
```

### 4. Deploy with Verification

Deploy and verify in one command:

```bash
forge script script/Deploy.s.sol \
    --rpc-url amoy \
    --private-key $PRIVATE_KEY \
    --broadcast \
    --verify \
    --etherscan-api-key $POLYGONSCAN_API_KEY
```

### 5. Deploy to Mainnet

**IMPORTANT: Test thoroughly on Amoy first!**

```bash
forge script script/Deploy.s.sol \
    --rpc-url polygon \
    --private-key $PRIVATE_KEY \
    --broadcast \
    --verify \
    --etherscan-api-key $POLYGONSCAN_API_KEY
```

## Gas Optimization

### Optimizer Settings

For Polygon (cheap gas), balance between deployment and runtime:

```toml
[profile.default]
optimizer = true
optimizer_runs = 200  # Standard

[profile.production]
optimizer = true
optimizer_runs = 1000  # More runtime optimization
```

### Gas Estimation

Check gas before deployment:

```bash
forge test --gas-report
```

### Priority Fee

For faster transactions on mainnet:

```bash
forge script script/Deploy.s.sol \
    --rpc-url polygon \
    --private-key $PRIVATE_KEY \
    --broadcast \
    --priority-gas-price 50  # in gwei
```

## Deployment Tracking

### Save Deployment Info

Foundry saves broadcasts to `broadcast/` directory:
- Transaction details
- Contract addresses
- ABI

### Manual Tracking

Create `deployments/` directory:

```bash
mkdir deployments
echo "MyContract=0xABCD..." > deployments/amoy.txt
```

Or use JSON:

```json
{
  "network": "amoy",
  "chainId": 80002,
  "contracts": {
    "MyContract": "0xABCD...",
    "MyToken": "0xDEF..."
  },
  "timestamp": "2026-02-05T10:30:00Z"
}
```

## Advanced Features

### Deploy from Specific Account

```solidity
// Use different account than PRIVATE_KEY
address deployer = 0x1234...;
vm.startBroadcast(deployer);
```

### Conditional Deployment

```solidity
function run() external {
    uint256 deployerPrivateKey = vm.envUint("PRIVATE_KEY");
    uint256 chainId = block.chainid;
    
    vm.startBroadcast(deployerPrivateKey);
    
    if (chainId == 80002) {
        // Amoy testnet specific
        MyContract myContract = new MyContract(true); // debug mode
    } else if (chainId == 137) {
        // Mainnet specific
        MyContract myContract = new MyContract(false); // production
    }
    
    vm.stopBroadcast();
}
```

### Using Create2 for Deterministic Addresses

```solidity
bytes32 salt = keccak256("my-salt");
MyContract myContract = new MyContract{salt: salt}();
```

## Troubleshooting

### Insufficient Funds

```
Error: insufficient funds for gas * price + value
```

Get testnet tokens from faucets (see `scripts/get-testnet-tokens.sh`).

### Nonce Issues

```
Error: nonce too low
```

Reset nonce or wait for pending transactions to complete.

### RPC Rate Limiting

Use dedicated RPC provider:
- Alchemy: https://www.alchemy.com/
- QuickNode: https://www.quicknode.com/
- Infura: https://infura.io/

### Verification Failed

- Wait a few minutes for contract to be indexed
- Check constructor arguments are ABI-encoded correctly
- Ensure compilation settings match exactly

## Best Practices

1. **Test First**: Always deploy to Amoy before mainnet
2. **Use .env**: Never hardcode private keys
3. **Verify Contracts**: Always verify for transparency
4. **Gas Estimation**: Check gas costs before deployment
5. **Save Addresses**: Track deployed contract addresses
6. **Use Profiles**: Separate testnet/mainnet configs
7. **Incremental**: Deploy one contract at a time for complex systems
8. **Audit**: Get security audit before mainnet deployment

## Resources

- Foundry Book: https://book.getfoundry.sh/
- Polygon Docs: https://docs.polygon.technology/
- Foundry Scripts: https://book.getfoundry.sh/tutorials/solidity-scripting
