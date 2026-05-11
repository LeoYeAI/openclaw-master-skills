# Contracts API Reference

## Overview

Smart contract source code retrieval, ABI query, and verification services. This API allows you to retrieve verified contract source code and ABIs, submit contracts for verification, and check verification status for both regular and proxy contracts.

**Supported chains:** BSC Mainnet, BSC Testnet, opBNB Mainnet, opBNB Testnet

**Base URLs:**

| Chain | Endpoint |
|-------|----------|
| BSC Mainnet | `https://open-platform.nodereal.io/{apiKey}/bsc-mainnet/contract/` |
| BSC Testnet | `https://open-platform.nodereal.io/{apiKey}/bsc-testnet/contract/` |
| opBNB Mainnet | `https://open-platform.nodereal.io/{apiKey}/op-bnb-mainnet/contract/` |
| opBNB Testnet | `https://open-platform.nodereal.io/{apiKey}/op-bnb-testnet/contract/` |

## Table of Contents

1. [Get Contract Source Code for Verified Contracts](#get-contract-source-code-for-verified-contracts) -- retrieve Solidity source code of a verified smart contract
2. [Get Contract ABI for Verified Contracts](#get-contract-abi-for-verified-contracts) -- retrieve the ABI for a verified smart contract
3. [Verify Source Code](#verify-source-code) -- submit contract source code for verification
4. [Check Source Code Verification Status](#check-source-code-verification-status) -- check the status of a source code verification submission
5. [Verify Proxy Contract](#verify-proxy-contract) -- submit a proxy contract for verification
6. [Check Proxy Verification Status](#check-proxy-verification-status) -- check the status of a proxy contract verification
7. [Contracts API Summary](#contracts-api-summary) -- quick reference table of all actions
8. [Sourcify Fallback](#sourcify-fallback) -- fallback when contract is not verified on BscTrace

---

## Get Contract Source Code for Verified Contracts

Returns the Solidity source code of a verified smart contract.

```
GET https://open-platform.nodereal.io/{apiKey}/bsc-mainnet/contract/?action=getsourcecode&address={contractAddress}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| address | yes | Contract address with verified source code |

**Response example:**
```json
{
  "status": "1",
  "message": "OK",
  "result": [
    {
      "SourceCode": "pragma solidity 0.6.12; ...",
      "ABI": "[{\"inputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"constructor\"}, ...]",
      "ContractName": "CakeToken",
      "CompilerVersion": "v0.6.12+commit.27d51765",
      "OptimizationUsed": "1",
      "Runs": "5000",
      "ConstructorArguments": "",
      "EVMVersion": "Default",
      "Library": "",
      "LicenseType": "None",
      "Proxy": "0",
      "Implementation": "",
      "SwarmSource": "ipfs://9755240809e31aec9fa5790314682233ca431b7c4f252d7e4bba347e2e742086"
    }
  ]
}
```

---

## Get Contract ABI for Verified Contracts

Returns the ABI for a verified smart contract.

```
GET https://open-platform.nodereal.io/{apiKey}/bsc-mainnet/contract/?action=getabi&address={contractAddress}
```

| Parameter | Required | Description |
|-----------|----------|-------------|
| address | yes | Contract address with verified source code |

**Response example:**
```json
{
  "status": "1",
  "message": "OK",
  "result": "[{\"inputs\":[],\"stateMutability\":\"nonpayable\",\"type\":\"constructor\"}, ...]"
}
```

**Usage with Web3.js:**
```javascript
var Web3 = require('web3');
var web3 = new Web3(new Web3.providers.HttpProvider());
$.getJSON(
  'https://open-platform.nodereal.io/{apiKey}/bsc-mainnet/contract/?action=getabi&address=0x55d398326f99059ff775485246999027b3197955',
  function (data) {
    var contractABI = JSON.parse(data.result);
    var MyContract = web3.eth.contract(contractABI);
    var myContractInstance = MyContract.at("0x55d398326f99059ff775485246999027b3197955");
    var result = myContractInstance.balanceOf("0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb");
  }
);
```

---

## Verify Source Code

Submits contract source code for verification. Returns a GUID receipt for tracking status.

```
POST https://open-platform.nodereal.io/{apiKey}/bsc-mainnet/contract?action=verifysourcecode
```

**Request parameters (form data):**

| Parameter | Required | Description |
|-----------|----------|-------------|
| contractaddress | yes | Contract address starting with 0x |
| sourceCode | yes | Contract source code (flattened if necessary) |
| codeformat | no | `solidity-single-file` (default) or `solidity-standard-json-input` |
| contractname | yes | Contract name |
| compilerversion | yes | Compiler version (e.g., `v0.8.19+commit.7dd6d404`) |
| optimizationUsed | no | `0` = No optimization, `1` = Optimization used |
| runs | no | Default 200 |
| constructorArguements | no | Constructor arguments if applicable |
| evmversion | no | EVM version (homestead, byzantium, istanbul, etc.) |
| licenseType | no | License code 1-12 (1=No License, 12=Apache 2.0) |

**Limits:**
- 100 submissions per day per user
- Only POST supported (HTTP GET size limitations)
- Supports up to 10 library pairs
- Only solc v0.4.11 and above

## Check Source Code Verification Status

```
GET https://open-platform.nodereal.io/{apiKey}/bsc-mainnet/contract?action=checkverifystatus&guid={guid}
```

**Response:**
```json
{"status": "1", "message": "OK", "result": "Pass - Verified"}
```

---

## Verify Proxy Contract

Submits a proxy contract for verification.

```
POST https://open-platform.nodereal.io/{apiKey}/bsc-mainnet/contract?action=verifyproxycontract
```

**Request parameters (form data):**

| Parameter | Required | Description |
|-----------|----------|-------------|
| address | yes | Proxy contract address |
| expectedimplementation | no | Expected implementation contract address |

**Response example:**
```json
{"status": "1", "message": "OK", "result": "gwgrrnfy56zf6vc1fljuejwg6pelnc5yns6fg6y2i6zfpgzquz"}
```

## Check Proxy Verification Status

```
GET https://open-platform.nodereal.io/{apiKey}/bsc-mainnet/contract?action=checkproxyverification&guid={guid}
```

**Response:**
```json
{
  "status": "1",
  "message": "OK",
  "result": "The proxy's (0xbc46363a7669f6e12353fa95bb067aead3675c29) implementation contract is found at 0xe45a5176bc0f2c1198e2451c4e4501d4ed9b65a6 and is successfully updated."
}
```

---

## Contracts API Summary

| Action | HTTP | Description |
|--------|------|-------------|
| `getsourcecode` | GET | Get verified contract source code |
| `getabi` | GET | Get verified contract ABI |
| `verifysourcecode` | POST | Submit source for verification |
| `checkverifystatus` | GET | Check verification status |
| `verifyproxycontract` | POST | Submit proxy contract for verification |
| `checkproxyverification` | GET | Check proxy verification status |

---

## Sourcify Fallback

When a contract is not verified on BscTrace (NodeReal Contracts API returns no source), use [Sourcify](https://sourcify.dev) as a fallback source for verified contract metadata, ABI, and source code.

### Endpoint

```
GET https://sourcify.dev/server/files/{chainId}/{contractAddress}
```

### Common Chain IDs

| Chain | Chain ID |
|-------|----------|
| BSC Mainnet | `56` |
| BSC Testnet | `97` |
| Ethereum Mainnet | `1` |
| opBNB Mainnet | `204` |

### Example

```bash
# Fallback: get source code from Sourcify when BscTrace verification is unavailable
curl -s "https://sourcify.dev/server/files/56/0x1e3b3c89bd76992edb85e733b1965b796bcbdbd5"
```

### Recommended Flow

1. First try NodeReal Contracts API (`getsourcecode` / `getabi`)
2. If result is empty or contract is not verified, fallback to Sourcify
3. If Sourcify also has no match, inform the user the contract is unverified on both sources

**Important:** When reporting verification status to the user, always specify the platform name. For example:
- "This contract is verified on **BscTrace**" (NodeReal Contracts API returned source)
- "This contract is not verified on BscTrace, but is verified on **Sourcify**" (fallback succeeded)
- "This contract is not verified on **BscTrace** or **Sourcify**" (both sources returned no match)

---
