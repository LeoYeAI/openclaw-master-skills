'use strict';

const { ethers } = require('ethers');
const fs = require('fs');
const path = require('path');
const os = require('os');

// --- Constants ---
const BASE_CHAIN_ID = 8453;
const DEFAULT_RPC = 'https://mainnet.base.org';
const RPC_TIMEOUT_MS = 30000;
const TX_CONFIRM_TIMEOUT_MS = 120000;
const GAS_BUFFER_PERCENT = 20 + Math.floor(Math.random() * 30);  // 20-49%
const FEE_BUFFER_PERCENT = 10 + Math.floor(Math.random() * 25);  // 10-34%
const MAX_RETRIES = 3;
const SIMPLE_TRANSFER_GAS = 21000n;

// OP Stack (Base L2) gas oracle for L1 data fee estimation
const GAS_ORACLE_ADDR = '0x420000000000000000000000000000000000000F';
const GAS_ORACLE_ABI = ['function getL1Fee(bytes) view returns (uint256)'];

// --- Helpers ---

function jsonOut(data) {
  process.stdout.write(JSON.stringify(data) + '\n');
}

function jsonErr(message, details) {
  const obj = { error: true, message: String(message) };
  if (details !== undefined) {
    obj.details = details;
  }
  process.stdout.write(JSON.stringify(obj) + '\n');
  process.exitCode = 1;
}

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i++) {
    if (argv[i].startsWith('--') && i + 1 < argv.length && !argv[i + 1].startsWith('--')) {
      args[argv[i].slice(2)] = argv[i + 1];
      i++;
    } else if (argv[i].startsWith('--')) {
      args[argv[i].slice(2)] = true;
    }
  }
  return args;
}

// --- Validation ---

const HEX_ADDR_RE = /^0x[0-9a-fA-F]{40}$/;
const URL_RE = /^https?:\/\/.+/;
const EXPECTED_WORD_COUNT = 12;

function validateAddress(addr, label) {
  if (typeof addr !== 'string' || !HEX_ADDR_RE.test(addr)) {
    throw new Error(`Invalid ${label}: must be 0x + 40 hex characters`);
  }
  return ethers.getAddress(addr);
}

function resolveWallet() {
  const raw = process.env.CEASER_HOT_MNEMONIC;
  if (!raw || typeof raw !== 'string' || raw.trim().length === 0) {
    throw new Error('CEASER_HOT_MNEMONIC environment variable required');
  }
  const words = raw.trim().split(/\s+/);
  if (words.length !== EXPECTED_WORD_COUNT) {
    throw new Error(`CEASER_HOT_MNEMONIC must be exactly 12 words (got ${words.length})`);
  }
  const phrase = words.join(' ');
  const mnemonic = ethers.Mnemonic.fromPhrase(phrase);
  return ethers.HDNodeWallet.fromMnemonic(mnemonic);
}

function validateRpc(rpc) {
  if (typeof rpc !== 'string' || !URL_RE.test(rpc)) {
    throw new Error('RPC URL must start with http:// or https://');
  }
  return rpc;
}

function createProvider(rpcUrl) {
  const fetchReq = new ethers.FetchRequest(rpcUrl);
  fetchReq.timeout = RPC_TIMEOUT_MS;
  return new ethers.JsonRpcProvider(fetchReq, BASE_CHAIN_ID, { staticNetwork: true });
}

// --- Commands ---

async function cmdGenerate() {
  const wallet = ethers.Wallet.createRandom();
  jsonOut({
    mnemonic: wallet.mnemonic.phrase,
    address: wallet.address
  });
}

async function cmdBalance(args) {
  const address = validateAddress(args.address, 'address');
  const rpcUrl = validateRpc(args.rpc || DEFAULT_RPC);
  const provider = createProvider(rpcUrl);

  try {
    const balance = await provider.getBalance(address);
    jsonOut({
      address: address,
      balanceWei: balance.toString(),
      balanceEth: ethers.formatEther(balance)
    });
  } finally {
    provider.destroy();
  }
}

// Default pending TX file location (written by ceaser-mcp shield)
const DEFAULT_PENDING_TX = path.join(os.homedir(), '.ceaser-mcp', 'pending-tx.json');

async function cmdSignAndSend(args) {
  const hdWallet = resolveWallet();
  const rpcUrl = validateRpc(args.rpc || DEFAULT_RPC);

  // Resolve unsigned TX: --unsigned-tx-file (preferred) or --unsigned-tx (legacy)
  let unsignedTx;
  let txFilePath = null;

  if (args['unsigned-tx-file']) {
    txFilePath = args['unsigned-tx-file'];
    if (!fs.existsSync(txFilePath)) {
      throw new Error(`File not found: ${txFilePath}`);
    }
    try {
      unsignedTx = JSON.parse(fs.readFileSync(txFilePath, 'utf8'));
    } catch (_) {
      throw new Error(`Failed to parse JSON from ${txFilePath}`);
    }
  } else if (args['unsigned-tx']) {
    try {
      unsignedTx = JSON.parse(args['unsigned-tx']);
    } catch (_) {
      throw new Error('--unsigned-tx must be valid JSON');
    }
  } else if (fs.existsSync(DEFAULT_PENDING_TX)) {
    // Auto-detect: ceaser-mcp shield saves here by default
    txFilePath = DEFAULT_PENDING_TX;
    try {
      unsignedTx = JSON.parse(fs.readFileSync(txFilePath, 'utf8'));
    } catch (_) {
      throw new Error(`Failed to parse pending TX from ${txFilePath}`);
    }
  } else {
    throw new Error('No unsigned TX provided. Use --unsigned-tx-file <path>, --unsigned-tx <json>, or run ceaser-mcp shield first.');
  }

  if (!unsignedTx.to || !unsignedTx.data || unsignedTx.value === undefined || unsignedTx.chainId === undefined) {
    throw new Error('unsigned-tx must contain: to, data, value, chainId');
  }

  const parsedChainId = Number(unsignedTx.chainId);
  if (parsedChainId !== BASE_CHAIN_ID) {
    throw new Error(`chainId must be ${BASE_CHAIN_ID} (Base Mainnet), got ${parsedChainId}`);
  }

  validateAddress(unsignedTx.to, 'unsigned-tx.to');

  const provider = createProvider(rpcUrl);
  const wallet = hdWallet.connect(provider);

  let lastError;
  for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
    try {
      const nonce = await provider.getTransactionCount(wallet.address, 'pending');
      const feeData = await provider.getFeeData();

      if (!feeData.maxFeePerGas || !feeData.maxPriorityFeePerGas) {
        throw new Error('Failed to retrieve EIP-1559 fee data from RPC');
      }

      const estimatedGas = await provider.estimateGas({
        from: wallet.address,
        to: unsignedTx.to,
        data: unsignedTx.data,
        value: BigInt(unsignedTx.value)
      });

      const gasLimit = estimatedGas * BigInt(100 + GAS_BUFFER_PERCENT) / 100n;
      const maxFeePerGas = feeData.maxFeePerGas * BigInt(100 + FEE_BUFFER_PERCENT) / 100n;
      const maxPriorityFeePerGas = feeData.maxPriorityFeePerGas * BigInt(100 + FEE_BUFFER_PERCENT) / 100n;

      const tx = {
        to: unsignedTx.to,
        data: unsignedTx.data,
        value: BigInt(unsignedTx.value),
        chainId: BASE_CHAIN_ID,
        nonce: nonce,
        maxFeePerGas: maxFeePerGas,
        maxPriorityFeePerGas: maxPriorityFeePerGas,
        gasLimit: gasLimit,
        type: 2
      };

      const txResponse = await wallet.sendTransaction(tx);
      const receipt = await txResponse.wait(1, TX_CONFIRM_TIMEOUT_MS);

      if (!receipt) {
        jsonOut({
          txHash: txResponse.hash,
          blockNumber: null,
          gasUsed: null,
          status: null,
          warning: 'Transaction sent but confirmation timed out. Check manually.'
        });
        return;
      }

      // Clean up pending TX file after successful send
      if (txFilePath) {
        try { fs.unlinkSync(txFilePath); } catch (_) { /* ignore */ }
      }

      jsonOut({
        txHash: receipt.hash,
        blockNumber: receipt.blockNumber,
        gasUsed: receipt.gasUsed.toString(),
        status: receipt.status
      });
      return;

    } catch (err) {
      lastError = err;
      const msg = String(err.message || err);

      if (msg.includes('insufficient funds')) {
        const balance = await provider.getBalance(wallet.address).catch(() => null);
        throw new Error(
          `Insufficient funds. Wallet balance: ${balance !== null ? ethers.formatEther(balance) : 'unknown'} ETH. ` +
          `Required: value (${ethers.formatEther(BigInt(unsignedTx.value))}) + gas`
        );
      }

      if (msg.includes('execution reverted')) {
        throw new Error(`Transaction reverted: ${msg}`);
      }

      if (msg.includes('nonce') && attempt < MAX_RETRIES) {
        const delay = Math.min(1000 * Math.pow(2, attempt - 1) + Math.random() * 500, 10000);
        await new Promise(r => setTimeout(r, delay));
        continue;
      }

      if (attempt < MAX_RETRIES && (msg.includes('timeout') || msg.includes('ETIMEDOUT') || msg.includes('network'))) {
        const delay = Math.min(1000 * Math.pow(2, attempt - 1) + Math.random() * 500, 10000);
        await new Promise(r => setTimeout(r, delay));
        continue;
      }

      throw err;
    } finally {
      if (attempt === MAX_RETRIES || !lastError) {
        provider.destroy();
      }
    }
  }

  throw lastError;
}

async function estimateL1Fee(provider, tx) {
  try {
    const oracle = new ethers.Contract(GAS_ORACLE_ADDR, GAS_ORACLE_ABI, provider);
    const serialized = ethers.Transaction.from({
      type: 2,
      chainId: BASE_CHAIN_ID,
      to: tx.to,
      value: tx.value || 0n,
      maxFeePerGas: tx.maxFeePerGas,
      maxPriorityFeePerGas: tx.maxPriorityFeePerGas,
      gasLimit: tx.gasLimit || SIMPLE_TRANSFER_GAS,
      nonce: 0,
      data: tx.data || '0x',
    }).unsignedSerialized;
    const l1Fee = await oracle.getL1Fee(serialized);
    // 20% buffer on L1 fee for price fluctuation between estimate and inclusion
    return l1Fee * 120n / 100n;
  } catch (_) {
    // Oracle unavailable (e.g. non-OP-Stack chain or RPC issue): use fixed fallback
    return 5000000000000n; // 0.000005 ETH
  }
}

async function cmdRefund(args) {
  const hdWallet = resolveWallet();
  const recipient = validateAddress(args.recipient, 'recipient');
  const rpcUrl = validateRpc(args.rpc || DEFAULT_RPC);

  const provider = createProvider(rpcUrl);
  const wallet = hdWallet.connect(provider);

  try {
    const balance = await provider.getBalance(wallet.address);

    if (balance === 0n) {
      jsonOut({ refunded: false, reason: 'Hot wallet balance is zero' });
      return;
    }

    const feeData = await provider.getFeeData();
    if (!feeData.maxFeePerGas) {
      throw new Error('Failed to retrieve fee data from RPC');
    }

    const maxFeePerGas = feeData.maxFeePerGas * BigInt(100 + FEE_BUFFER_PERCENT) / 100n;
    const maxPriorityFeePerGas = (feeData.maxPriorityFeePerGas || 0n) * BigInt(100 + FEE_BUFFER_PERCENT) / 100n;

    // Base L2 (OP Stack) charges L1 data fees on top of L2 execution gas.
    // Query the GasPriceOracle to get the actual L1 component.
    const l1Fee = await estimateL1Fee(provider, {
      to: recipient,
      value: balance,
      maxFeePerGas,
      maxPriorityFeePerGas,
    });
    const totalGasCost = SIMPLE_TRANSFER_GAS * maxFeePerGas + l1Fee;

    if (balance <= totalGasCost) {
      jsonOut({
        refunded: false,
        reason: `Balance (${ethers.formatEther(balance)} ETH) is too small to cover gas + L1 data fee (${ethers.formatEther(totalGasCost)} ETH). Import the mnemonic into a wallet to recover manually.`,
        balanceWei: balance.toString(),
        totalGasCostWei: totalGasCost.toString()
      });
      return;
    }

    const refundAmount = balance - totalGasCost;

    const tx = {
      to: recipient,
      value: refundAmount,
      chainId: BASE_CHAIN_ID,
      gasLimit: SIMPLE_TRANSFER_GAS,
      maxFeePerGas: maxFeePerGas,
      maxPriorityFeePerGas: maxPriorityFeePerGas,
      type: 2
    };

    const txResponse = await wallet.sendTransaction(tx);
    const receipt = await txResponse.wait(1, TX_CONFIRM_TIMEOUT_MS);

    if (!receipt) {
      jsonOut({
        refunded: true,
        amount: ethers.formatEther(refundAmount),
        amountWei: refundAmount.toString(),
        txHash: txResponse.hash,
        warning: 'Sent but confirmation timed out'
      });
      return;
    }

    jsonOut({
      refunded: true,
      amount: ethers.formatEther(refundAmount),
      amountWei: refundAmount.toString(),
      txHash: receipt.hash
    });
  } finally {
    provider.destroy();
  }
}

function cmdHelp() {
  jsonOut({
    commands: {
      generate: {
        description: 'Generate a new ephemeral hot wallet with BIP-39 mnemonic',
        args: 'none',
        output: '{ mnemonic, address }'
      },
      balance: {
        description: 'Query ETH balance of an address',
        args: '--address <0x...> [--rpc <url>]',
        output: '{ address, balanceWei, balanceEth }'
      },
      'sign-and-send': {
        description: 'Sign and broadcast an unsigned transaction',
        args: '[--unsigned-tx-file <path>] [--unsigned-tx <json>] [--rpc <url>]',
        env: 'CEASER_HOT_MNEMONIC="word1 word2 ..." (12-word BIP-39 mnemonic via env var)',
        notes: 'Auto-detects ~/.ceaser-mcp/pending-tx.json if no args given. File is deleted after successful send.',
        output: '{ txHash, blockNumber, gasUsed, status }'
      },
      refund: {
        description: 'Refund remaining ETH to a recipient',
        args: '--recipient <0x...> [--rpc <url>]',
        env: 'CEASER_HOT_MNEMONIC="word1 word2 ..." (12-word BIP-39 mnemonic via env var)',
        output: '{ refunded, amount, txHash }'
      }
    },
    defaults: {
      rpc: DEFAULT_RPC,
      chainId: BASE_CHAIN_ID
    }
  });
}

// --- Main ---

async function main() {
  const argv = process.argv.slice(2);
  const command = argv[0];
  const args = parseArgs(argv.slice(1));

  switch (command) {
    case 'generate':
      return cmdGenerate();
    case 'balance':
      return cmdBalance(args);
    case 'sign-and-send':
      return cmdSignAndSend(args);
    case 'refund':
      return cmdRefund(args);
    case '--help':
    case 'help':
    case undefined:
      return cmdHelp();
    default:
      jsonErr(`Unknown command: ${command}. Use --help for available commands.`);
  }
}

main().catch(err => {
  jsonErr(String(err.message || err));
});
