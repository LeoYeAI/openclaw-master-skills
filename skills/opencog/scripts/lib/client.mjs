import { createPublicClient, createWalletClient, http, fallback } from "viem";
import { baseSepolia, base } from "viem/chains";
import { privateKeyToAccount } from "viem/accounts";
import { readFileSync, existsSync } from "fs";
import { homedir } from "os";
import { join, dirname } from "path";
import { fileURLToPath } from "url";

// ── Load ~/.openclaw/.env ─────────────────────────────────────────────────────

const ENV_FILE = join(homedir(), ".openclaw", ".env");
if (existsSync(ENV_FILE)) {
  for (const line of readFileSync(ENV_FILE, "utf8").split("\n")) {
    const m = line.match(/^([A-Z_][A-Z0-9_]*)=(.+)$/);
    if (m && !process.env[m[1]]) process.env[m[1]] = m[2].trim();
  }
}

// ── Network config ────────────────────────────────────────────────────────────

const NETWORKS = {
  sepolia: {
    chain:   baseSepolia,
    address: "0x61ec71F1Fd37ecc20d695E83F3D68e82bEfe8443",
    rpcs: [
      "https://sepolia.base.org",
      "https://base-sepolia-rpc.publicnode.com"
    ],
  },
  mainnet: {
    chain:   base,
    address: "0x00000000000c109080dfa976923384b97165a57a",
    rpcs: [
      "https://mainnet.base.org",
      "https://base-rpc.publicnode.com"
    ],
  },
};

function _buildTransport(cfg) {
  return process.env.PRECOG_RPC_URL
    ? http(process.env.PRECOG_RPC_URL)
    : fallback(cfg.rpcs.map(url => http(url)));
}

let _networkKey = (process.env.PRECOG_NETWORK || "sepolia").toLowerCase();
if (!NETWORKS[_networkKey]) _networkKey = "sepolia";

let _cfg       = NETWORKS[_networkKey];
let chain      = _cfg.chain;
let transport  = _buildTransport(_cfg);

export let MASTER_ADDRESS = _cfg.address;
export let pub            = createPublicClient({ chain, transport });

/** Switch to a different network. Call this before any contract reads/writes. */
export function setNetwork(network) {
  const key = network.toLowerCase();
  if (!NETWORKS[key]) throw new Error(`Unknown network: "${network}". Use "sepolia" or "mainnet".`);
  _networkKey   = key;
  _cfg          = NETWORKS[key];
  chain         = _cfg.chain;
  transport     = _buildTransport(_cfg);
  MASTER_ADDRESS = _cfg.address;
  pub            = createPublicClient({ chain, transport });
}

// ── ABI ───────────────────────────────────────────────────────────────────────

const __dir  = dirname(fileURLToPath(import.meta.url));
const ABI_PATH = join(__dir, "../../abi/PrecogMasterV8.json");
export const ABI = JSON.parse(readFileSync(ABI_PATH, "utf8"));

// ── Clients ───────────────────────────────────────────────────────────────────

export function getWallet() {
  const pk = process.env.PRIVATE_KEY;
  if (!pk) {
    throw new Error(
      "No wallet found.\nRun: node setup.mjs --generate\n" +
      "Or add PRIVATE_KEY=0x... to ~/.openclaw/.env"
    );
  }
  const account = privateKeyToAccount(pk.startsWith("0x") ? pk : `0x${pk}`);
  const wallet  = createWalletClient({ account, chain, transport });
  return { account, wallet };
}

// ── Contract helpers ──────────────────────────────────────────────────────────

export function read(fn, args = []) {
  return pub.readContract({ address: MASTER_ADDRESS, abi: ABI, functionName: fn, args });
}

export function multiread(calls, { allowFailure = false } = {}) {
  return pub.multicall({
    contracts: calls.map(([functionName, args = []]) => ({
      address: MASTER_ADDRESS,
      abi: ABI,
      functionName,
      args,
    })),
    allowFailure,
  });
}

export async function write(wallet, account, fn, fnArgs) {
  const hash = await wallet.writeContract({
    address: MASTER_ADDRESS, abi: ABI, functionName: fn, args: fnArgs, account,
  });
  process.stdout.write(`Tx sent: ${hash}\nWaiting for confirmation...`);
  const receipt = await pub.waitForTransactionReceipt({ hash });
  console.log(` confirmed (block ${receipt.blockNumber})`);
  return receipt;
}

// ── ERC20 helpers ─────────────────────────────────────────────────────────────

const ERC20_ABI = [
  { name: "balanceOf", type: "function", stateMutability: "view",
    inputs: [{ type: "address" }], outputs: [{ type: "uint256" }] },
  { name: "allowance", type: "function", stateMutability: "view",
    inputs: [{ type: "address" }, { type: "address" }], outputs: [{ type: "uint256" }] },
  { name: "approve",   type: "function", stateMutability: "nonpayable",
    inputs: [{ type: "address" }, { type: "uint256" }], outputs: [{ type: "bool" }] },
];

export async function tokenBalance(token, addr) {
  return pub.readContract({ address: token, abi: ERC20_ABI, functionName: "balanceOf", args: [addr] });
}

export async function ensureApproval(wallet, account, token, spender, amount) {
  const allowance = await pub.readContract({
    address: token, abi: ERC20_ABI, functionName: "allowance",
    args: [account.address, spender],
  });
  if (allowance >= amount) return;
  console.log(`Approving ${token}...`);
  const hash = await wallet.writeContract({
    address: token, abi: ERC20_ABI, functionName: "approve",
    args: [spender, amount], account,
  });
  await pub.waitForTransactionReceipt({ hash });
  console.log("Approved.");
}

// ── Formatting ────────────────────────────────────────────────────────────────

export const TWO_POW_64 = 2n ** 64n;

export function toFP64(shares) {
  const [i, d = ""] = String(shares).split(".");
  const dec18 = BigInt(i) * 10n ** 18n + BigInt(d.padEnd(18, "0").slice(0, 18));
  return (dec18 * TWO_POW_64) / 10n ** 18n;
}

export function fromFP64(fp) {
  return Number((BigInt(fp) * 10000n) / TWO_POW_64) / 10000;
}

export function toRaw(amount, decimals) {
  const [i, d = ""] = String(amount).split(".");
  return BigInt(i) * 10n ** BigInt(decimals) + BigInt(d.padEnd(decimals, "0").slice(0, decimals));
}

export function fromRaw(raw, decimals) {
  const d     = 10n ** BigInt(decimals);
  const whole = raw / d;
  const frac  = raw % d;
  return `${whole}.${String(frac).padStart(decimals, "0").slice(0, 4)}`;
}

export function pct(price1e18) {
  return (Number(price1e18) / 1e18 * 100).toFixed(1);
}

export function outcomes(raw) {
  return raw.split("|").map(s => s.trim()).filter(Boolean);
}

export function status(endTs) {
  return Date.now() / 1000 < Number(endTs) ? "active" : "ended";
}

export function date(ts) {
  return new Date(Number(ts) * 1000).toLocaleDateString("en-US",
    { month: "short", day: "numeric", year: "numeric" });
}
