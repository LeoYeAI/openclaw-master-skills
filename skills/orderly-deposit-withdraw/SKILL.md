---
name: orderly-deposit-withdraw
description: Handle token deposits and withdrawals across chains, including allowance approval, vault interactions, and cross-chain operations
---

# Orderly Network: Deposit & Withdraw

This skill covers depositing and withdrawing assets on Orderly Network, including token approvals, vault interactions, cross-chain operations, and internal transfers.

## When to Use

- Building deposit/withdrawal interfaces
- Managing collateral
- Implementing cross-chain transfers
- Handling token approvals
- Internal transfers between accounts

## Prerequisites

- Connected Web3 wallet (EVM or Solana)
- Tokens on supported chain
- Understanding of ERC20 approve pattern
- Ed25519 key pair for API operations

## Supported Chains & Tokens

| Chain    | Chain ID  | USDC | USDT |
| -------- | --------- | ---- | ---- |
| Arbitrum | 42161     | ✅   | ✅   |
| Optimism | 10        | ✅   | ✅   |
| Base     | 8453      | ✅   | ✅   |
| Ethereum | 1         | ✅   | ✅   |
| Mantle   | 5000      | ✅   | -    |
| Solana   | 900900900 | ✅   | -    |

**Note**: Fetch supported chains dynamically using `GET /v1/public/chain_info?broker_id={your_broker_id}`

## Deposit Flow

```
1. Fetch chain information
2. Check if token is native (ETH, SOL)
3. Approve token allowance (if not native)
4. Calculate brokerHash and tokenHash
5. Get deposit fee from vault
6. Execute deposit transaction with fee
7. Wait for confirmation
8. Balance updates on Orderly
```

## React SDK: Complete Deposit Workflow

### Step 1: Fetch Chain Information

```typescript
import { useChain } from "@orderly.network/hooks";

function DepositForm() {
  const { chains, isLoading } = useChain("USDC");

  if (isLoading) return <div>Loading chains...</div>;

  return (
    <select>
      {chains.map(chain => (
        <option key={chain.id} value={chain.id}>
          {chain.name}
        </option>
      ))}
    </select>
  );
}
```

### Step 2: Get Deposit Metadata

```typescript
import { useDeposit } from '@orderly.network/hooks';

function DepositInfo({ tokenSymbol }: { tokenSymbol: string }) {
  const { symbol, address, decimals, chainId, network } = useDeposit(tokenSymbol);

  if (!address) return <div>Loading deposit info...</div>;

  return (
    <div>
      <h3>Deposit {symbol}</h3>
      <p><strong>Network:</strong> {network}</p>
      <p><strong>Chain ID:</strong> {chainId}</p>
      <p><strong>Contract Address:</strong> {address}</p>
      <p><strong>Decimals:</strong> {decimals}</p>

      <div className="mt-2 text-xs text-gray-500">
        Send only {symbol} to this address on {network}.
      </div>
    </div>
  );
}
```

### Step 3: Execute Deposit via Contract

```typescript
import { ethers } from 'ethers';

const ERC20_ABI = [
  'function approve(address spender, uint256 amount) returns (bool)',
  'function allowance(address owner, address spender) view returns (uint256)',
  'function balanceOf(address owner) view returns (uint256)',
];

const VAULT_ABI = [
  'function deposit(tuple(bytes32 accountId, bytes32 brokerHash, bytes32 tokenHash, uint256 tokenAmount) input) external payable',
  'function getDepositFee(address account, tuple(bytes32 accountId, bytes32 brokerHash, bytes32 tokenHash, uint256 tokenAmount) input) view returns (uint256)',
];

async function depositUSDC(
  provider: ethers.BrowserProvider,
  amount: string,
  vaultAddress: string,
  usdcAddress: string,
  brokerId: string,
  orderlyAccountId: string
) {
  const signer = await provider.getSigner();
  const userAddress = await signer.getAddress();

  // 1. Approve token
  const usdc = new ethers.Contract(usdcAddress, ERC20_ABI, signer);
  const amountWei = ethers.parseUnits(amount, 6);
  const allowance = await usdc.allowance(userAddress, vaultAddress);

  if (allowance < amountWei) {
    console.log('Approving USDC...');
    const approveTx = await usdc.approve(vaultAddress, ethers.MaxUint256);
    await approveTx.wait();
    console.log('Approved');
  }

  // 2. Calculate hashes
  const encoder = new TextEncoder();
  const brokerHash = ethers.keccak256(encoder.encode(brokerId));
  const tokenHash = ethers.keccak256(encoder.encode('USDC'));

  // 3. Create deposit input struct
  const depositInput = {
    accountId: orderlyAccountId,
    brokerHash: brokerHash,
    tokenHash: tokenHash,
    tokenAmount: amountWei,
  };

  // 4. Get deposit fee
  const vault = new ethers.Contract(vaultAddress, VAULT_ABI, signer);
  const depositFee = await vault.getDepositFee(userAddress, depositInput);
  console.log('Deposit fee:', ethers.formatEther(depositFee), 'ETH');

  // 5. Execute deposit with fee
  console.log('Depositing...');
  const depositTx = await vault.deposit(depositInput, { value: depositFee });
  const receipt = await depositTx.wait();
  console.log('Deposited:', receipt.hash);

  return receipt;
}
```

## REST API: Get Deposit Info

```typescript
// Get supported tokens with collateral factors
GET /v1/public/token

// Response
{
  "success": true,
  "data": {
    "rows": [
      {
        "token": "USDC",
        "decimals": 6,
        "address": {
          "42161": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",
          "10": "0x0b2C639c533813f4Aa9D7837CAf62653d097Ff85"
        },
        "collateral_factor": 1.0
      },
      {
        "token": "USDT",
        "decimals": 6,
        "address": { ... },
        "collateral_factor": 0.95
      }
    ]
  }
}

// Get chain info
GET /v1/public/chain_info?broker_id={broker_id}

// Get vault balance (TVL)
GET /v1/public/vault_balance
```

### Understanding Collateral Factors

Each token has a **collateral factor** (0.0 to 1.0) that determines how much of your deposit counts toward trading collateral:

| Token | Collateral Factor | $1000 Deposit = Collateral Value |
| ----- | ----------------- | -------------------------------- |
| USDC  | 1.0 (100%)        | $1000                            |
| USDT  | 0.95 (95%)        | $950                             |
| Other | Varies            | Depends on risk assessment       |

**Example**: If you deposit $1000 USDT with a 0.95 collateral factor, only $950 counts as collateral for margin calculations.

## Withdrawal Flow

```
1. Get withdrawal nonce
2. Sign withdrawal message with EIP-712 (EVM) or Ed25519 (Solana)
3. Submit signed request with Ed25519 API auth
4. Wait for processing
5. Receive tokens on chain
```

## React SDK: useWithdraw Hook

```typescript
import { useWithdraw } from '@orderly.network/hooks';

function WithdrawForm() {
  const { withdraw, isLoading } = useWithdraw();

  const [amount, setAmount] = useState('');
  const [destination, setDestination] = useState('');

  const handleWithdraw = async () => {
    try {
      await withdraw({
        symbol: "USDC",
        amount: "50",
        address: "0x123...",
        chainId: 1, // Ethereum Mainnet
        network: "ethereum"
      });
      alert('Withdrawal initiated!');
    } catch (error) {
      console.error('Withdrawal failed:', error);
    }
  };

  return (
    <div className="withdraw-form">
      <input
        type="text"
        placeholder="Amount"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
      />

      <input
        type="text"
        placeholder="Destination Address"
        value={destination}
        onChange={(e) => setDestination(e.target.value)}
      />

      <button onClick={handleWithdraw} disabled={isLoading}>
        {isLoading ? 'Processing...' : 'Withdraw'}
      </button>
    </div>
  );
}
```

## REST API: Withdrawal

### Step 1: Get Withdrawal Nonce

```typescript
GET /v1/withdraw_nonce
// Requires Ed25519 API authentication

// Response
{
  "success": true,
  "data": {
    "withdraw_nonce": 123456
  }
}
```

### Step 2: Create EIP-712 Signature (EVM)

```typescript
// Use ON-CHAIN domain for withdrawals (see EIP-712 Domain Configuration in orderly-api-authentication)
const domain = {
  name: 'Orderly',
  version: '1',
  chainId: 42161,
  verifyingContract: '0x6F7a338F2aA472838dEFD3283eB360d4Dff5D203', // Mainnet Ledger
  // verifyingContract: '0x1826B75e2ef249173FC735149AE4B8e9ea10abff' // Testnet Ledger
};

const types = {
  Withdraw: [
    { name: 'brokerId', type: 'string' },
    { name: 'chainId', type: 'uint256' },
    { name: 'receiver', type: 'address' },
    { name: 'token', type: 'string' },
    { name: 'amount', type: 'uint256' },
    { name: 'withdrawNonce', type: 'uint64' },
    { name: 'timestamp', type: 'uint64' },
  ],
};

const withdrawMessage = {
  brokerId: 'woofi_dex',
  chainId: 42161,
  receiver: '0xTargetAddress',
  token: 'USDC',
  amount: '10000000', // 10 USDC (6 decimals)
  withdrawNonce: withdrawNonceFromStep1,
  timestamp: Date.now(),
};

// Sign with wallet
const signature = await wallet.signTypedData(domain, types, withdrawMessage);
```

### Step 3: Submit Withdrawal Request

```typescript
POST /v1/withdraw_request
Body: {
  "message": withdrawMessage,
  "signature": "0x..."
}
// Requires Ed25519 API authentication

// Response
{
  "success": true,
  "data": {
    "withdraw_id": 123
  },
  "timestamp": 1702989203989
}
```

### Withdrawal for Solana

```typescript
import { DefaultSolanaWalletAdapter } from '@orderly.network/default-solana-adapter';
import { signAsync } from '@noble/ed25519';

const walletAdapter = new DefaultSolanaWalletAdapter();
await walletAdapter.active({
  address: solanaAddress,
  provider: {
    signMessage: async (msg: Uint8Array) => {
      return await signAsync(msg, privateKey);
    }
  }
});

const withdrawMessage = await walletAdapter.generateWithdrawMessage({
  brokerId: BROKER_ID,
  receiver: solanaAddress,
  token: 'USDC',
  amount: '1000',
  timestamp: Date.now(),
  nonce: withdrawNonceFromStep1,
});

const signature = await walletAdapter.signMessage(withdrawMessage.message);

// Submit withdrawal request
POST /v1/withdraw_request
Body: {
  "message": withdrawMessage.message,
  "signature": signature,
  "userAddress": solanaAddress,
  "verifyingContract": "0x6F7a338F2aA472838dEFD3283eB360d4Dff5D203"
  // "verifyingContract": "0x1826B75e2ef249173FC735149AE4B8e9ea10abff"
}
Headers: { Standard Orderly Auth Headers }
```

## Cross-Chain Withdrawal

Cross-chain withdrawal is required when the destination chain differs from the chain where funds were deposited.

```typescript
POST /v1/withdraw_request
Body: {
  "message": {
    ...withdrawMessage,
    "chainId": 10,
    "allowCrossChainWithdraw": true
  },
  "signature": signature,
  "userAddress": walletAddress,
  "verifyingContract": "0x6F7a338F2aA472838dEFD3283eB360d4Dff5D203"
}
// Requires Ed25519 API authentication

// Response
{
  "success": true,
  "data": {
    "withdraw_id": 123
  },
  "timestamp": 1702989203989
}
```

**Error Code 22**: If `allowCrossChainWithdraw` is `false` when a cross-chain withdrawal is needed, the API returns:

```json
{
  "success": false,
  "code": 22,
  "message": "Cross-chain withdrawal required for this withdrawal request"
}
```

## Internal Transfer

Transfer funds between Orderly accounts instantly with no gas fees.

### React SDK: useInternalTransfer Hook

```typescript
import { useInternalTransfer } from '@orderly.network/hooks';

function TransferFunds() {
  const [amount, setAmount] = useState('');
  const { transfer, isLoading } = useInternalTransfer();

  const handleTransfer = async () => {
    try {
      await transfer({
        token: 'USDC',
        amount: parseFloat(amount),
      });
      alert('Transfer successful!');
    } catch (e) {
      console.error(e);
    }
  };

  return (
    <div>
      <input
        type="number"
        value={amount}
        onChange={(e) => setAmount(e.target.value)}
        placeholder="Amount"
      />
      <button
        onClick={handleTransfer}
        disabled={isLoading || !amount}
      >
        {isLoading ? 'Transferring...' : 'Transfer'}
      </button>
    </div>
  );
}
```

### REST API: Internal Transfer (v2)

Internal transfers move funds between Orderly accounts instantly with no gas fees.

**Allowed scenarios:**

- Main and sub-accounts
- Accounts within the same wallet group
- Same address across all brokers
- Whitelisted accounts
- Accounts under the same whitelisted broker

#### EVM (EIP-712 Signing)

```typescript
// Step 1: Get transfer nonce (Ed25519 API auth)
GET /v1/transfer_nonce
// Requires Ed25519 API authentication

// Response
{
  "success": true,
  "data": {
    "transfer_nonce": "789012"
  }
}

// Step 2: Sign EIP-712 message with wallet (ON-CHAIN domain - see orderly-api-authentication)
const receiverHex = receiverAddress.startsWith('0x')
  ? receiverAddress.slice(2)
  : receiverAddress;
const receiverBytes32 = ethers.zeroPadValue('0x' + receiverHex, 32);

const domain = {
  name: 'Orderly',
  version: '1',
  chainId: 42161,
  verifyingContract: '0x6F7a338F2aA472838dEFD3283eB360d4Dff5D203' // Mainnet Ledger
};

const types = {
  InternalTransfer: [
    { name: 'receiver', type: 'bytes32' },
    { name: 'token', type: 'string' },
    { name: 'amount', type: 'uint256' },
    { name: 'transferNonce', type: 'uint64' }
  ]
};

const message = {
  receiver: receiverBytes32,
  token: 'USDC',
  amount: ethers.parseUnits('100', 6),
  transferNonce: Number(transferNonce)
};

const signature = await wallet.signTypedData(domain, types, message);

// Step 3: Submit to v2 endpoint
POST /v2/internal_transfer
Body: {
  "message": {
    "receiver": "0xReceiverAddress",
    "token": "USDC",
    "amount": "100",
    "transferNonce": "789012",
    "chainId": "42161",
    "chainType": "EVM"
  },
  "signature": "0x...",
  "userAddress": "0xSenderAddress",
  "verifyingContract": "0x6F7a338F2aA472838dEFD3283eB360d4Dff5D203"
}
// Requires Ed25519 API authentication
```

#### Solana (Adapter Signing)

```typescript
import { DefaultSolanaWalletAdapter } from '@orderly.network/default-solana-adapter';

// Step 1: Get transfer nonce
GET /v1/transfer_nonce
// Requires Ed25519 API authentication

// Step 2: Generate and sign message with adapter
const walletAdapter = new DefaultSolanaWalletAdapter();
// ... initialize adapter ...

const transferMessage = await walletAdapter.generateTransferMessage({
  receiver: receiverAddress,
  token: 'USDC',
  amount: '100',
  transferNonce: nonceFromStep1,
  chainId: 900900900,
  chainType: 'SOL'
});

const signature = await walletAdapter.signMessage(transferMessage.message);

// Step 3: Submit to v2 endpoint
POST /v2/internal_transfer
Body: {
  "message": {
    "receiver": "SolanaReceiverAddress",
    "token": "USDC",
    "amount": "100",
    "transferNonce": "789012",
    "chainId": "900900900",
    "chainType": "SOL"
  },
  "signature": signature,
  "userAddress": solanaAddress,
  "verifyingContract": "0x6F7a338F2aA472838dEFD3283eB360d4Dff5D203"
}
// Requires Ed25519 API authentication
```

**Important Notes:**

- Transfer nonce must be obtained before each transfer (via Ed25519 auth)
- The actual transfer requires wallet signature (EIP-712 for EVM, adapter for Solana)
- Receiver address must be converted to bytes32 for EVM signing
- Internal transfers are not available for Delegate Signer accounts
- v2 endpoint includes optional memo field

## Asset History

```typescript
// Get deposit/withdrawal history
GET /v1/asset/history?token=USDC&side=DEPOSIT&page=1&size=20
// Requires Ed25519 API authentication

// Query parameters (all optional):
//   token: USDC
//   side: DEPOSIT | WITHDRAW
//   status: NEW | CONFIRM | PROCESSING | COMPLETED | FAILED | PENDING_REBALANCE
//   start_t: timestamp (e.g., 1702989203989)
//   end_t: timestamp (e.g., 1702989203989)
//   page: 1 (default)
//   size: 20 (default)

// Response
{
  "success": true,
  "data": {
    "rows": [
      {
        "id": "tx_123",
        "token": "USDC",
        "side": "DEPOSIT",
        "amount": "1000.00",
        "status": "COMPLETED",
        "tx_hash": "0x...",
        "chain_id": 42161,
        "created_at": 1699123456
      }
    ],
    "total": 50
  }
}
```

## Testnet Faucet

```typescript
// Get testnet USDC (testnet only)
POST /v1/faucet/usdc
Headers: { Standard Orderly Auth Headers }

// EVM Testnet
POST https://testnet-operator-evm.orderly.org/v1/faucet/usdc

// Solana Testnet
POST https://testnet-operator-sol.orderly.org/v1/faucet/usdc

// Each account can use faucet max 5 times
// EVM: 1000 USDC per request
// Solana: 100 USDC per request
```

## Get Contract Addresses

```typescript
import { getContractAddresses } from '@orderly.network/contracts';

// EVM chains
const addresses = getContractAddresses('arbitrum', 'mainnet');
// {
//   vault: '0x816f722424B49Cf1275cc86DA9840Fbd5a6167e9',
//   usdc: '0xaf88d065e77c8cC2239327C5EDb3A432268e5831',
//   usdt: '0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9'
// }

// Or fetch dynamically
GET /v1/public/chain_info?broker_id={broker_id}
```

### Verifying Contract Addresses

| Environment | Verifying Contract                           |
| ----------- | -------------------------------------------- |
| Mainnet     | `0x6F7a338F2aA472838dEFD3283eB360d4Dff5D203` |
| Testnet     | `0x1826B75e2ef249173FC735149AE4B8e9ea10abff` |

## Common Issues

### "Insufficient allowance" error

- Call `approve()` before deposit
- Check if approval transaction confirmed
- Ensure you're approving the vault address, not token address

### "Insufficient balance" error

- Check wallet balance, not just Orderly balance
- Ensure correct token decimals
- Account for deposit fee (native token like ETH)

### Withdrawal stuck in "PROCESSING"

- Check `/v1/asset/history` for status updates
- Contact support if stuck > 24 hours

### "Cross-chain withdrawal required" error (Code 22)

- Set `allow_cross_chain_withdrawal: true` in request body
- Destination chain differs from deposit chain
- Expect longer processing time

### Internal transfer not available

- Not available for Delegate Signer accounts
- Ensure accounts meet allowed transfer scenarios
- Check that Ed25519 authentication is properly signed

### EIP-712 signature mismatch

Common mistakes:

- `withdrawNonce` type should be `uint64`, not `uint256`
- `token` type should be `string`, not `address`
- Missing `fee` field in message
- Wrong verifying contract address
- Wrong chain ID in domain

## Related Skills

- **orderly-api-authentication** - Ed25519 API authentication and EIP-712 signing
- **orderly-sdk-react-hooks** - React SDK hooks reference
- **orderly-onboarding** - Account setup and getting started
