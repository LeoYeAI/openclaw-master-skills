import {
  createPublicClient,
  createWalletClient,
  defineChain,
  getAddress,
  http,
} from "viem";
import { privateKeyToAccount } from "viem/accounts";

export const MAINNET_IDENTITY = "0x8004A169FB4a3325136EB29fA0ceB6D2e539a432";

export const NETWORKS = {
  "monad-mainnet": { chainId: 143, registry: MAINNET_IDENTITY },
  "monad-testnet": { chainId: 10143, registry: MAINNET_IDENTITY },
};

export function parseArgs(argv) {
  const args = {};
  for (let i = 2; i < argv.length; i += 1) {
    const token = argv[i];
    if (!token.startsWith("--")) continue;
    const key = token.slice(2);
    const next = argv[i + 1];
    if (!next || next.startsWith("--")) {
      args[key] = true;
      continue;
    }
    args[key] = next;
    i += 1;
  }
  return args;
}

export function requiredEnv(name) {
  const value = process.env[name];
  if (!value || value.trim() === "") throw new Error(`Missing required env var: ${name}`);
  return value.trim();
}

export function resolveNetwork(args = {}) {
  const envChainId = Number(process.env.MONAD_CHAIN_ID ?? "143");
  const networkName = args.network ?? "monad-mainnet";
  const fromMap = NETWORKS[networkName];
  const chainId = args.chainId ? Number(args.chainId) : fromMap?.chainId ?? envChainId;
  const rpcUrl = args.rpcUrl ?? process.env.MONAD_RPC_URL;
  if (!rpcUrl) throw new Error("Missing RPC URL. Pass --rpcUrl or set MONAD_RPC_URL.");
  const registry = getAddress(args.registry ?? fromMap?.registry ?? MAINNET_IDENTITY);
  return { networkName, chainId, rpcUrl, registry };
}

export function createClients(params) {
  const account = privateKeyToAccount(requiredEnv("AGENT_PRIVATE_KEY"));
  const chain = defineChain({
    id: params.chainId,
    name: params.networkName,
    nativeCurrency: { name: "MON", symbol: "MON", decimals: 18 },
    rpcUrls: { default: { http: [params.rpcUrl] } },
  });
  const transport = http(params.rpcUrl);
  const publicClient = createPublicClient({ chain, transport });
  const walletClient = createWalletClient({ chain, transport, account });
  return { account, publicClient, walletClient, chain };
}
