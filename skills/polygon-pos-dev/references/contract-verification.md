# Contract Verification on Polygonscan

Complete guide for verifying smart contracts on Polygonscan (Amoy testnet and Polygon mainnet).

## Why Verify Contracts

**Transparency**: Users can read your contract code before interacting.

**Trust**: Verified contracts show you have nothing to hide.

**Integration**: Many dApps and tools require verified contracts.

**Debugging**: Easier to debug transactions on block explorers.

**Standards**: Required for token listings and DEX integration.

## Prerequisites

### Get Polygonscan API Key

1. Visit https://polygonscan.com/register (or https://amoy.polygonscan.com for testnet)
2. Create account
3. Navigate to API Keys section
4. Generate new API key
5. Add to `.env`:

```bash
POLYGONSCAN_API_KEY=your_api_key_here
```

### Verify Foundry Setup

```bash
forge --version
```

## Verification Methods

### Method 1: Verify During Deployment (Recommended)

Deploy and verify in one command:

```bash
forge script script/Deploy.s.sol \
    --rpc-url amoy \
    --private-key $PRIVATE_KEY \
    --broadcast \
    --verify \
    --etherscan-api-key $POLYGONSCAN_API_KEY
```

This is the easiest method - verification happens automatically after deployment.

### Method 2: Verify After Deployment

Using helper script:
```bash
./scripts/verify-contract.sh
```

Or manually:

**Without Constructor Arguments:**
```bash
forge verify-contract \
    CONTRACT_ADDRESS \
    src/MyContract.sol:MyContract \
    --chain-id 80002 \
    --etherscan-api-key $POLYGONSCAN_API_KEY \
    --verifier-url https://api-amoy.polygonscan.com/api
```

**With Constructor Arguments:**
```bash
forge verify-contract \
    CONTRACT_ADDRESS \
    src/MyContract.sol:MyContract \
    --chain-id 80002 \
    --etherscan-api-key $POLYGONSCAN_API_KEY \
    --verifier-url https://api-amoy.polygonscan.com/api \
    --constructor-args $(cast abi-encode "constructor(address,uint256)" 0x1234... 1000000)
```

### Method 3: Manual Verification via UI

1. Go to contract page: `https://amoy.polygonscan.com/address/CONTRACT_ADDRESS`
2. Click "Contract" tab
3. Click "Verify and Publish"
4. Select verification method
5. Fill in details

## Network-Specific Configuration

### Amoy Testnet

```bash
forge verify-contract \
    CONTRACT_ADDRESS \
    src/MyContract.sol:MyContract \
    --chain-id 80002 \
    --etherscan-api-key $POLYGONSCAN_API_KEY \
    --verifier-url https://api-amoy.polygonscan.com/api
```

Explorer: https://amoy.polygonscan.com

### Polygon Mainnet

```bash
forge verify-contract \
    CONTRACT_ADDRESS \
    src/MyContract.sol:MyContract \
    --chain-id 137 \
    --etherscan-api-key $POLYGONSCAN_API_KEY \
    --verifier-url https://api.polygonscan.com/api
```

Explorer: https://polygonscan.com

## Handling Constructor Arguments

### Simple Arguments

Encode with cast:
```bash
cast abi-encode "constructor(address,uint256)" 0x1234... 1000000
```

Use output with `--constructor-args`.

### Complex Arguments

For structs or arrays:

```solidity
// Contract constructor
constructor(
    address _owner,
    uint256[] memory _values,
    Config memory _config
) { ... }
```

Encode:
```bash
cast abi-encode \
    "constructor(address,uint256[],tuple(uint256,bool))" \
    0x1234... \
    "[100,200,300]" \
    "(1000,true)"
```

### Get Constructor Args from Deployment

From broadcast file:
```bash
cat broadcast/Deploy.s.sol/80002/run-latest.json | jq '.transactions[0].arguments'
```

## Multi-File Contracts

Foundry automatically handles imports - no need to flatten.

```bash
forge verify-contract \
    CONTRACT_ADDRESS \
    src/MyContract.sol:MyContract \
    --chain-id 80002 \
    --etherscan-api-key $POLYGONSCAN_API_KEY \
    --watch
```

The `--watch` flag polls until verification completes.

## Verification with Libraries

If your contract uses libraries:

```bash
forge verify-contract \
    CONTRACT_ADDRESS \
    src/MyContract.sol:MyContract \
    --chain-id 80002 \
    --etherscan-api-key $POLYGONSCAN_API_KEY \
    --libraries src/MyLibrary.sol:MyLibrary:LIBRARY_ADDRESS
```

Multiple libraries:
```bash
--libraries \
    src/LibA.sol:LibA:0x123... \
    src/LibB.sol:LibB:0x456...
```

## Verification Status

### Check Via CLI

```bash
forge verify-check \
    VERIFICATION_GUID \
    --chain-id 80002 \
    --etherscan-api-key $POLYGONSCAN_API_KEY
```

### Check Via Browser

Visit:
```
https://amoy.polygonscan.com/address/CONTRACT_ADDRESS#code
```

Status will show:
- ✅ "Contract Source Code Verified"
- ⏳ "Pending in queue"
- ❌ "Verification failed"

## Advanced Verification

### Via IR Compilation

If you used `via_ir = true` in foundry.toml:

```bash
forge verify-contract \
    CONTRACT_ADDRESS \
    src/MyContract.sol:MyContract \
    --chain-id 80002 \
    --etherscan-api-key $POLYGONSCAN_API_KEY \
    --via-ir
```

### Specific Compiler Version

```bash
forge verify-contract \
    CONTRACT_ADDRESS \
    src/MyContract.sol:MyContract \
    --chain-id 80002 \
    --etherscan-api-key $POLYGONSCAN_API_KEY \
    --compiler-version v0.8.24+commit.e11b9ed9
```

### Custom Optimizer Runs

```bash
forge verify-contract \
    CONTRACT_ADDRESS \
    src/MyContract.sol:MyContract \
    --chain-id 80002 \
    --etherscan-api-key $POLYGONSCAN_API_KEY \
    --num-of-optimizations 200
```

## Troubleshooting

### Error: "Contract not yet indexed"

**Solution**: Wait 1-5 minutes after deployment for the contract to be indexed by Polygonscan.

### Error: "Bytecode does not match"

**Causes**:
- Constructor arguments incorrect
- Compiler version mismatch
- Optimizer settings mismatch
- Using wrong contract source

**Solutions**:
1. Verify compiler settings match foundry.toml
2. Check constructor arguments are ABI-encoded correctly
3. Ensure you're verifying the right contract file
4. Check optimizer runs match deployment

### Error: "Already verified"

Contract already verified. Visit explorer to see.

### Error: "Rate limit exceeded"

**Solution**: Wait a few minutes between verification attempts. Free API keys have rate limits.

### Error: "Invalid API key"

**Solution**: 
- Check `.env` file has correct API key
- Ensure no extra spaces in API key
- Verify API key is for the correct network (testnet vs mainnet)

### Constructor Arguments Not Working

Get the exact arguments from deployment:

```bash
# From broadcast file
cast to-hex $(cast abi-encode "constructor(...)" args)

# Or extract from transaction
cast run TX_HASH --rpc-url amoy
```

## Verification Best Practices

1. **Verify Immediately**: Verify right after deployment while settings are fresh
2. **Save Verification Info**: Keep verification GUID for tracking
3. **Use --watch**: Add `--watch` flag to wait for verification to complete
4. **Document Constructor Args**: Save constructor arguments in deployment logs
5. **Test on Testnet First**: Verify process on Amoy before mainnet
6. **Use Scripts**: Automate verification with deployment scripts
7. **Keep Config**: Maintain consistent foundry.toml settings

## Verification Checklist

Before verifying:
- [ ] Contract deployed successfully
- [ ] Have contract address
- [ ] Have Polygonscan API key in .env
- [ ] Know compiler version used
- [ ] Have constructor arguments (if any)
- [ ] Know optimizer settings used
- [ ] Contract has been indexed (wait 1-2 minutes)

## Batch Verification

Verify multiple contracts:

```bash
#!/bin/bash
contracts=(
    "0x1234:MyContractA"
    "0x5678:MyContractB"
    "0xabcd:MyContractC"
)

for contract in "${contracts[@]}"; do
    IFS=':' read -r address name <<< "$contract"
    
    forge verify-contract \
        $address \
        src/$name.sol:$name \
        --chain-id 80002 \
        --etherscan-api-key $POLYGONSCAN_API_KEY
    
    sleep 10  # Rate limit protection
done
```

## Alternative: Hardhat Verification

If using Hardhat alongside Foundry:

```bash
npx hardhat verify --network polygonAmoy CONTRACT_ADDRESS "Constructor Arg 1" "Constructor Arg 2"
```

## Resources

- Foundry Verification Docs: https://book.getfoundry.sh/reference/forge/forge-verify-contract
- Polygonscan API: https://docs.polygonscan.com/
- Block Explorer:
  - Testnet: https://amoy.polygonscan.com
  - Mainnet: https://polygonscan.com
