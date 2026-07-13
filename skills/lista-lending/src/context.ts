/**
 * Context storage for Lista Lending skill
 * Stores selected position and user info for session continuity
 */

import { existsSync, mkdirSync, readFileSync, writeFileSync } from "fs";
import { homedir } from "os";
import { join } from "path";

const CONFIG_DIR = join(homedir(), ".agent-wallet");
const CONTEXT_FILE = join(CONFIG_DIR, "lending-context.json");
const CONTEXT_SCHEMA_VERSION = 2;

export interface SelectedVault {
  address: string;
  name: string;
  asset: {
    symbol: string;
    address: string;
    decimals: number;
  };
  chain: string;
}

export interface UserPosition {
  shares: string;
  assets: string;
  assetsUsd?: string;
}

export interface SelectedMarket {
  marketId: string;
  chain: string;
  collateralSymbol?: string;
  loanSymbol?: string;
  zone?: number;
  termType?: number;
}

export enum TargetType {
  Vault = "vault",
  Market = "market",
}

export interface LastFilters {
  vaults?: Record<string, unknown>;
  markets?: Record<string, unknown>;
  holdings?: Record<string, unknown>;
}

export interface LendingContext {
  schemaVersion: number;
  selectedVault: SelectedVault | null;
  selectedMarket: SelectedMarket | null;
  userAddress: string | null;
  walletTopic: string | null;
  userPosition: UserPosition | null;
  lastFilters: LastFilters | null;
  lastUpdated: string | null;
}

const DEFAULT_CONTEXT: LendingContext = {
  schemaVersion: CONTEXT_SCHEMA_VERSION,
  selectedVault: null,
  selectedMarket: null,
  userAddress: null,
  walletTopic: null,
  userPosition: null,
  lastFilters: null,
  lastUpdated: null,
};

/**
 * Ensure config directory exists
 */
function ensureConfigDir(): void {
  if (!existsSync(CONFIG_DIR)) {
    mkdirSync(CONFIG_DIR, { recursive: true });
  }
}

function isObject(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

function isSelectedVault(value: unknown): value is SelectedVault {
  if (!isObject(value)) return false;
  if (typeof value.address !== "string") return false;
  if (typeof value.name !== "string") return false;
  if (typeof value.chain !== "string") return false;
  if (!isObject(value.asset)) return false;
  return (
    typeof value.asset.symbol === "string" &&
    typeof value.asset.address === "string" &&
    typeof value.asset.decimals === "number"
  );
}

function isSelectedMarket(value: unknown): value is SelectedMarket {
  if (!isObject(value)) return false;
  return (
    typeof value.marketId === "string" &&
    typeof value.chain === "string"
  );
}

function isUserPosition(value: unknown): value is UserPosition {
  if (!isObject(value)) return false;
  return (
    typeof value.shares === "string" &&
    typeof value.assets === "string"
  );
}

function isLastFilters(value: unknown): value is LastFilters {
  return isObject(value);
}

function migrateContext(raw: unknown): LendingContext {
  const base: LendingContext = { ...DEFAULT_CONTEXT };

  if (!isObject(raw)) {
    return base;
  }

  const old = raw as Record<string, unknown>;
  const selectedVault = isSelectedVault(old.selectedVault)
    ? old.selectedVault
    : null;
  const selectedMarket = isSelectedMarket(old.selectedMarket)
    ? old.selectedMarket
    : null;
  const userPosition = isUserPosition(old.userPosition)
    ? old.userPosition
    : null;
  const lastFilters = isLastFilters(old.lastFilters)
    ? old.lastFilters
    : null;

  return {
    schemaVersion: CONTEXT_SCHEMA_VERSION,
    selectedVault,
    selectedMarket,
    userAddress:
      typeof old.userAddress === "string" ? old.userAddress : base.userAddress,
    walletTopic:
      typeof old.walletTopic === "string" ? old.walletTopic : base.walletTopic,
    userPosition,
    lastFilters,
    lastUpdated:
      typeof old.lastUpdated === "string" ? old.lastUpdated : base.lastUpdated,
  };
}

/**
 * Load context from disk
 */
export function loadContext(): LendingContext {
  try {
    if (existsSync(CONTEXT_FILE)) {
      const data = readFileSync(CONTEXT_FILE, "utf-8");
      return migrateContext(JSON.parse(data));
    }
  } catch {
    // Ignore errors, return default
  }
  return { ...DEFAULT_CONTEXT };
}

/**
 * Save context to disk
 */
export function saveContext(context: LendingContext): void {
  ensureConfigDir();
  context.schemaVersion = CONTEXT_SCHEMA_VERSION;
  context.lastUpdated = new Date().toISOString();
  writeFileSync(CONTEXT_FILE, JSON.stringify(context, null, 2));
}

/**
 * Set selected vault
 */
export function setSelectedVault(
  vault: SelectedVault,
  userAddress: string,
  walletTopic: string,
  position?: UserPosition
): void {
  const context = loadContext();
  context.selectedVault = vault;
  context.selectedMarket = null;
  context.userAddress = userAddress;
  context.walletTopic = walletTopic;
  context.userPosition = position || null;
  saveContext(context);
}

/**
 * Set selected market
 */
export function setSelectedMarket(
  market: SelectedMarket,
  userAddress: string,
  walletTopic: string
): void {
  const context = loadContext();
  context.selectedMarket = market;
  context.selectedVault = null; // Clear vault when selecting market
  context.userPosition = null; // Clear vault position
  context.userAddress = userAddress;
  context.walletTopic = walletTopic;
  saveContext(context);
}

/**
 * Update user position for selected vault
 */
export function updatePosition(position: UserPosition): void {
  const context = loadContext();
  context.userPosition = position;
  saveContext(context);
}

/**
 * Persist latest user-facing filters for vaults/markets/holdings.
 */
export function setLastFilters(filters: LastFilters): void {
  const context = loadContext();
  context.lastFilters = {
    ...(context.lastFilters || {}),
    ...filters,
  };
  saveContext(context);
}

/**
 * Clear selection context.
 */
export function clearContext(): void {
  saveContext({ ...DEFAULT_CONTEXT });
}
