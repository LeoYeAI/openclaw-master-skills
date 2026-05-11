import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { randomUUID } from 'node:crypto';
import { SdkError } from './errors.js';

export const CONFIG_DIR = path.join(os.homedir(), '.config', 'silk');
const CONFIG_FILE = path.join(CONFIG_DIR, 'config.json');

export interface WalletEntry {
  label: string;
  address: string;
  privateKey: string;
}

export interface AccountInfo {
  pda: string;
  owner: string;
  mint: string;
  mintDecimals: number;
  operatorIndex: number;
  perTxLimit: number;
  syncedAt: string;
}

export type SolanaCluster = 'mainnet-beta' | 'devnet';

export interface SilkConfig {
  wallets: WalletEntry[];
  defaultWallet: string;
  preferences: Record<string, unknown>;
  apiUrl?: string;
  cluster?: SolanaCluster;
  account?: AccountInfo;
  agentId?: string;
}

function defaultConfig(): SilkConfig {
  return { wallets: [], defaultWallet: 'main', preferences: {}, cluster: 'mainnet-beta' };
}

export function loadConfig(): SilkConfig {
  try {
    const raw = fs.readFileSync(CONFIG_FILE, 'utf-8');
    return JSON.parse(raw) as SilkConfig;
  } catch {
    return defaultConfig();
  }
}

export function saveConfig(config: SilkConfig): void {
  fs.mkdirSync(CONFIG_DIR, { recursive: true });
  fs.writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2), 'utf-8');
}

export function getWallet(config: SilkConfig, label?: string): WalletEntry {
  const target = label || config.defaultWallet;
  const wallet = config.wallets.find((w) => w.label === target);
  if (!wallet) {
    throw new SdkError('WALLET_NOT_FOUND', `Wallet "${target}" not found. Run: silk wallet create`);
  }
  return wallet;
}

const CLUSTER_API_URLS: Record<SolanaCluster, string> = {
  'mainnet-beta': 'https://api.silkyway.ai',
  'devnet': 'https://devnet-api.silkyway.ai',
};

export function getCluster(config: SilkConfig): SolanaCluster {
  return config.cluster || 'mainnet-beta';
}

export function getApiUrl(config: SilkConfig): string {
  return config.apiUrl || process.env.SILK_API_URL || CLUSTER_API_URLS[getCluster(config)];
}

export function ensureAgentId(config: SilkConfig): { agentId: string; created: boolean } {
  if (config.agentId) {
    return { agentId: config.agentId, created: false };
  }
  const agentId = randomUUID();
  config.agentId = agentId;
  return { agentId, created: true };
}

const APP_BASE_URL = 'https://app.silkyway.ai';

export function getClaimUrl(config: SilkConfig, transferPda: string): string {
  const base = `${APP_BASE_URL}/transfers/${transferPda}`;
  const cluster = getCluster(config);
  return cluster === 'devnet' ? `${base}?cluster=devnet` : base;
}

export function getSetupUrl(config: SilkConfig, agentAddress: string): string {
  const base = `${APP_BASE_URL}/account/setup?agent=${agentAddress}`;
  const cluster = getCluster(config);
  return cluster === 'devnet' ? `${base}&cluster=devnet` : base;
}

export function getAgentId(config: SilkConfig): string {
  const result = ensureAgentId(config);
  if (result.created) {
    saveConfig(config);
  }
  return result.agentId;
}
