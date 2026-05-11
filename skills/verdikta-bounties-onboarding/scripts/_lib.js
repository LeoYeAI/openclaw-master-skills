import './_env.js';
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { JsonRpcProvider, Wallet, Contract, parseEther } from 'ethers';
import { defaultSecretsDir } from './_paths.js';

export const LINK = {
  base: '0x88Fb150BDc53A65fe94Dea0c9BA0a6dAf8C6e196',
  'base-sepolia': '0xE4aB69C077896252FAFBD49EFD26B5D171A32410'
};

export const ERC20_ABI = [
  'function balanceOf(address) view returns (uint256)',
  'function decimals() view returns (uint8)',
  'function symbol() view returns (string)',
  'function transfer(address,uint256) returns (bool)'
];

// ---- BountyEscrow contract addresses (canonical, from Blockchain docs) ----

export const ESCROW = {
  'base': process.env.BOUNTY_ESCROW_ADDRESS_BASE || '0x0a6290EfA369Bbd4a9886ab9f98d7fAd7b0dc746',
  'base-sepolia': process.env.BOUNTY_ESCROW_ADDRESS_BASE_SEPOLIA || '0x0520b15Ee61C4E2A1B00bA260d8B1FBD015D2780',
};

// ---- BountyEscrow ABI (subset needed by scripts) ----

export const BOUNTY_ESCROW_ABI = [
  // Events
  'event BountyCreated(uint256 indexed bountyId, address indexed creator, string evaluationCid, uint64 classId, uint8 threshold, uint256 payoutWei, uint64 submissionDeadline)',
  'event SubmissionPrepared(uint256 indexed bountyId, uint256 indexed submissionId, address indexed hunter, address evalWallet, string evaluationCid, uint256 linkMaxBudget)',
  'event WorkSubmitted(uint256 indexed bountyId, uint256 indexed submissionId, bytes32 verdiktaAggId)',
  'event SubmissionFinalized(uint256 indexed bountyId, uint256 indexed submissionId, uint8 status, uint256 acceptance)',
  'event PayoutSent(uint256 indexed bountyId, address indexed winner, uint256 amount)',
  // Write
  'function createBounty(string evaluationCid, uint64 requestedClass, uint8 threshold, uint64 submissionDeadline) payable returns (uint256)',
  'function prepareSubmission(uint256 bountyId, string evaluationCid, string hunterCid, string addendum, uint256 alpha, uint256 maxOracleFee, uint256 estimatedBaseCost, uint256 maxFeeBasedScaling) returns (uint256 submissionId, address evalWallet, uint256 linkMaxBudget)',
  'function startPreparedSubmission(uint256 bountyId, uint256 submissionId)',
  'function finalizeSubmission(uint256 bountyId, uint256 submissionId)',
  'function closeExpiredBounty(uint256 bountyId)',
  'function failTimedOutSubmission(uint256 bountyId, uint256 submissionId)',
  // Read
  'function bountyCount() view returns (uint256)',
  // getBounty returns Bounty memory (a struct) — must use tuple() for correct ABI decoding
  'function getBounty(uint256 bountyId) view returns (tuple(address creator, string evaluationCid, uint64 requestedClass, uint8 threshold, uint256 payoutWei, uint256 createdAt, uint64 submissionDeadline, uint8 status, address winner, uint256 submissions))',
  'function getSubmission(uint256 bountyId, uint256 submissionId) view returns (tuple(address hunter, string evaluationCid, string hunterCid, address evalWallet, bytes32 verdiktaAggId, uint8 status, uint256 acceptance, uint256 rejection, string justificationCids, uint256 submittedAt, uint256 finalizedAt, uint256 linkMaxBudget, uint256 maxOracleFee, uint256 alpha, uint256 estimatedBaseCost, uint256 maxFeeBasedScaling, string addendum))',
  'function getEffectiveBountyStatus(uint256 bountyId) view returns (string)',
  'function isAcceptingSubmissions(uint256 bountyId) view returns (bool)',
  'function verdikta() view returns (address)',
];

/**
 * Return a connected BountyEscrow Contract instance.
 * @param {string} network  - 'base' or 'base-sepolia'
 * @param {import('ethers').Signer|import('ethers').Provider} signerOrProvider
 */
export function escrowContract(network, signerOrProvider) {
  const addr = ESCROW[network];
  if (!addr) throw new Error(`No escrow address for network ${network}`);
  return new Contract(addr, BOUNTY_ESCROW_ABI, signerOrProvider);
}

/**
 * Redact an API key for safe logging (shows first 4 + last 4 chars).
 * @param {string} key
 * @returns {string}
 */
export function redactApiKey(key) {
  if (!key || key.length < 12) return '***';
  return `${key.slice(0, 4)}…${key.slice(-4)}`;
}

export function getNetwork() {
  return process.env.VERDIKTA_NETWORK || 'base';
}

export function getRpcUrl(network) {
  if (network === 'base') return process.env.BASE_RPC_URL || 'https://mainnet.base.org';
  return process.env.BASE_SEPOLIA_RPC_URL || 'https://sepolia.base.org';
}

export function resolvePath(p) {
  if (!p) return p;
  let s = String(p);
  // Expand ~ to home for convenience in .env files
  if (s.startsWith('~/')) {
    s = path.join(process.env.HOME || '', s.slice(2));
  }
  // Resolve relative paths against the scripts directory (not the caller's CWD).
  const here = path.dirname(fileURLToPath(import.meta.url));
  return path.isAbsolute(s) ? s : path.resolve(here, s);
}

export async function loadWallet() {
  const keystorePathRaw = process.env.VERDIKTA_KEYSTORE_PATH;
  const password = process.env.VERDIKTA_WALLET_PASSWORD;
  if (!keystorePathRaw || !password) {
    throw new Error(
      'Set VERDIKTA_KEYSTORE_PATH and VERDIKTA_WALLET_PASSWORD. ' +
      'To import an existing wallet, run: node wallet_init.js --import'
    );
  }
  const keystorePath = resolvePath(keystorePathRaw);
  const json = await fs.readFile(keystorePath, 'utf-8');
  return Wallet.fromEncryptedJson(json, password);
}

export function providerFor(network) {
  return new JsonRpcProvider(getRpcUrl(network));
}

export async function linkBalance(network, provider, address) {
  const linkAddr = LINK[network];
  const link = new Contract(linkAddr, ERC20_ABI, provider);
  const [bal, dec] = await Promise.all([link.balanceOf(address), link.decimals()]);
  return { bal, dec, linkAddr };
}

export function parseEth(s) {
  return parseEther(String(s));
}

// ---- CLI argument helpers ----

export function arg(name, def = null) {
  const i = process.argv.indexOf(`--${name}`);
  return i >= 0 ? process.argv[i + 1] : def;
}

export function hasFlag(name) {
  return process.argv.includes(`--${name}`);
}

export function argAll(name) {
  const vals = [];
  for (let i = 0; i < process.argv.length; i++) {
    if (process.argv[i] === `--${name}` && i + 1 < process.argv.length) {
      vals.push(process.argv[i + 1]);
    }
  }
  return vals;
}

// ---- API key loading ----

export async function loadApiKey() {
  const botFile = process.env.VERDIKTA_BOT_FILE || `${defaultSecretsDir()}/verdikta-bounties-bot.json`;
  const abs = resolvePath(botFile);
  const raw = await fs.readFile(abs, 'utf8');
  const j = JSON.parse(raw);
  return j.apiKey || j.api_key || j.bot?.apiKey || j.bot?.api_key;
}

// ---- Transaction helper ----

/**
 * Sign and broadcast a transaction, with dry-run gas estimation.
 * Exits the process on revert to prevent wasted gas.
 * @param {import('ethers').Signer} signer
 * @param {string} label - Human-readable label for logging
 * @param {object} txObj - Transaction object from API ({ to, data, value, gasLimit? })
 * @param {object} [opts]
 * @param {boolean} [opts.useApiGasLimit] - Use the gasLimit from txObj instead of estimating
 */
export async function sendTx(signer, label, txObj, { useApiGasLimit = false } = {}) {
  console.log(`\n→ ${label}: sending transaction...`);
  const baseTx = {
    to: txObj.to,
    data: txObj.data,
    value: txObj.value || '0',
  };

  let gasLimit;

  if (useApiGasLimit && txObj.gasLimit) {
    gasLimit = BigInt(txObj.gasLimit);
    console.log(`  using API-recommended gasLimit: ${gasLimit.toString()}`);
  } else {
    try {
      const estimated = await signer.estimateGas(baseTx);
      gasLimit = (estimated * 120n) / 100n;
      console.log(`  estimated gas: ${estimated.toString()} (limit: ${gasLimit.toString()})`);
    } catch (err) {
      const reason = err.reason || err.shortMessage || err.message || 'unknown';
      console.error(`\n✖ ${label} will revert! Reason: ${reason}`);
      if (err.data) console.error(`  revert data: ${err.data}`);
      process.exit(1);
    }
  }

  const tx = await signer.sendTransaction({ ...baseTx, gasLimit });
  console.log(`  tx: ${tx.hash}`);
  const receipt = await tx.wait();
  console.log(`  confirmed in block ${receipt.blockNumber}`);
  return receipt;
}
