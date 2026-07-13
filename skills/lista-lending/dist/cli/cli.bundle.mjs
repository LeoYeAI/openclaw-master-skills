#!/usr/bin/env tsx

// src/cli/args.ts
import { parseArgs } from "util";
function parseCsv(value) {
  if (!value) return void 0;
  const items = value.split(",").map((v) => v.trim()).filter(Boolean);
  return items.length > 0 ? items : void 0;
}
function parseCliInput() {
  const { positionals, values } = parseArgs({
    allowPositionals: true,
    options: {
      vault: { type: "string" },
      market: { type: "string" },
      amount: { type: "string" },
      chain: { type: "string" },
      address: { type: "string" },
      page: { type: "string" },
      "page-size": { type: "string" },
      sort: { type: "string" },
      order: { type: "string" },
      scope: { type: "string" },
      zone: { type: "string" },
      keyword: { type: "string" },
      assets: { type: "string" },
      curators: { type: "string" },
      loans: { type: "string" },
      collaterals: { type: "string" },
      "wallet-topic": { type: "string" },
      "wallet-address": { type: "string" },
      "withdraw-all": { type: "boolean" },
      "repay-all": { type: "boolean" },
      simulate: { type: "boolean" },
      "simulate-supply": { type: "string" },
      show: { type: "boolean" },
      clear: { type: "boolean" },
      "set-rpc": { type: "boolean" },
      "clear-rpc": { type: "boolean" },
      url: { type: "string" },
      "debug-log-file": { type: "string" },
      help: { type: "boolean", short: "h" }
    }
  });
  const command = positionals[0];
  const page = typeof values.page === "string" && values.page.trim() !== "" ? Number(values.page) : void 0;
  const pageSize = typeof values["page-size"] === "string" && values["page-size"].trim() !== "" ? Number(values["page-size"]) : void 0;
  return {
    command,
    help: Boolean(values.help),
    debugLogFile: values["debug-log-file"],
    args: {
      vault: values.vault,
      market: values.market,
      amount: values.amount,
      chain: values.chain,
      walletTopic: values["wallet-topic"],
      walletAddress: values["wallet-address"],
      withdrawAll: values["withdraw-all"],
      repayAll: values["repay-all"],
      simulate: values.simulate,
      simulateSupply: values["simulate-supply"],
      help: values.help
    },
    configArgs: {
      show: values.show,
      setRpc: values["set-rpc"],
      clearRpc: values["clear-rpc"],
      chain: values.chain,
      url: values.url
    },
    vaultsArgs: {
      chain: values.chain,
      page,
      pageSize,
      sort: values.sort,
      order: values.order,
      zone: values.zone,
      keyword: values.keyword,
      assets: parseCsv(values.assets),
      curators: parseCsv(values.curators)
    },
    marketsArgs: {
      chain: values.chain,
      page,
      pageSize,
      sort: values.sort,
      order: values.order,
      zone: values.zone,
      keyword: values.keyword,
      loans: parseCsv(values.loans),
      collaterals: parseCsv(values.collaterals)
    },
    holdingsArgs: {
      address: values.address || values["wallet-address"],
      scope: values.scope
    },
    selectArgs: {
      vault: values.vault,
      market: values.market,
      chain: values.chain,
      walletTopic: values["wallet-topic"],
      walletAddress: values["wallet-address"],
      clear: values.clear,
      show: values.show
    }
  };
}

// src/cli/debug-log.ts
import { appendFileSync, mkdirSync } from "fs";
import { dirname, resolve } from "path";
function writeRecord(filePath, record) {
  try {
    appendFileSync(filePath, `${JSON.stringify(record)}
`, "utf8");
  } catch {
  }
}
function toText(chunk, encoding) {
  if (typeof chunk === "string") return chunk;
  if (chunk instanceof Uint8Array) {
    return Buffer.from(chunk).toString(encoding || "utf8");
  }
  return String(chunk);
}
function normalizeWriteArgs(encodingOrCb, cb) {
  if (typeof encodingOrCb === "function") {
    return { encoding: void 0, callback: encodingOrCb };
  }
  return { encoding: encodingOrCb, callback: cb };
}
function parseJsonIfPossible(line) {
  try {
    return JSON.parse(line);
  } catch {
    return void 0;
  }
}
function isStructuredJson(value) {
  return Array.isArray(value) || typeof value === "object" && value !== null;
}
function patchWriteStream(streamName, stream, filePath, skill) {
  const originalWrite = stream.write.bind(stream);
  let buffer = "";
  const emitLine = (line) => {
    if (!line) return;
    const parsed2 = parseJsonIfPossible(line);
    const record = {
      ts: (/* @__PURE__ */ new Date()).toISOString(),
      pid: process.pid,
      skill,
      stream: streamName,
      line
    };
    if (isStructuredJson(parsed2)) {
      record.json = parsed2;
    }
    writeRecord(filePath, record);
  };
  const flushBuffer = () => {
    if (!buffer) return;
    emitLine(buffer.replace(/\r$/, ""));
    buffer = "";
  };
  stream.write = ((chunk, encodingOrCb, cb) => {
    const { encoding, callback } = normalizeWriteArgs(encodingOrCb, cb);
    const text = toText(chunk, encoding);
    buffer += text;
    let index = buffer.indexOf("\n");
    while (index >= 0) {
      const line = buffer.slice(0, index).replace(/\r$/, "");
      emitLine(line);
      buffer = buffer.slice(index + 1);
      index = buffer.indexOf("\n");
    }
    if (encoding !== void 0 && callback) {
      return originalWrite(chunk, encoding, callback);
    }
    if (encoding !== void 0) {
      return originalWrite(chunk, encoding);
    }
    if (callback) {
      return originalWrite(chunk, callback);
    }
    return originalWrite(chunk);
  });
  return flushBuffer;
}
function setupDebugLogFile(skill, cliLogFile) {
  const requested = cliLogFile || process.env.SKILL_DEBUG_LOG_FILE || process.env.DEBUG_LOG_FILE;
  if (!requested) return null;
  const filePath = resolve(requested);
  try {
    mkdirSync(dirname(filePath), { recursive: true });
  } catch {
  }
  process.env.SKILL_DEBUG_LOG_FILE = filePath;
  const flushStdout = patchWriteStream("stdout", process.stdout, filePath, skill);
  const flushStderr = patchWriteStream("stderr", process.stderr, filePath, skill);
  const flushAll = () => {
    flushStdout();
    flushStderr();
  };
  process.on("beforeExit", flushAll);
  process.on("exit", flushAll);
  writeRecord(filePath, {
    ts: (/* @__PURE__ */ new Date()).toISOString(),
    pid: process.pid,
    skill,
    stream: "stderr",
    line: "debug_log_enabled",
    config: {
      filePath,
      argv: process.argv.slice(2)
    }
  });
  return filePath;
}

// src/cli/help.ts
function renderHelp(meta2) {
  return `${meta2.skillName} v${meta2.skillVersion}

Usage: dist/cli/cli.bundle.mjs <command> [options]

Vault Commands:
  vaults           List available vaults
  deposit          Deposit assets into selected vault
  withdraw         Withdraw assets from selected vault

Market Commands:
  markets          List available markets (excludes SmartLending & Fixed)
  supply           Supply collateral to selected market
  borrow           Borrow loan tokens (use --simulate to check max)
  repay            Repay borrowed loan tokens (use --simulate to preview impact)
  market-withdraw  Withdraw collateral from selected market

Common Commands:
  holdings         Query user's positions (vault + market)
  select           Select a vault or market for operations
  config           Manage RPC URLs and settings
  version          Show version information

Discovery:
  node dist/cli/cli.bundle.mjs vaults [--chain eip155:56]
  node dist/cli/cli.bundle.mjs markets [--chain eip155:56]
  node dist/cli/cli.bundle.mjs holdings --address 0x...

Selection:
  node dist/cli/cli.bundle.mjs select --vault 0x... --wallet-topic <t> --wallet-address 0x...
  node dist/cli/cli.bundle.mjs select --market 0x... --wallet-topic <t> --wallet-address 0x...
  node dist/cli/cli.bundle.mjs select --show
  node dist/cli/cli.bundle.mjs select --clear

Vault Operations:
  node dist/cli/cli.bundle.mjs deposit --amount 100
  node dist/cli/cli.bundle.mjs withdraw --amount 50
  node dist/cli/cli.bundle.mjs withdraw --withdraw-all

Market Operations:
  node dist/cli/cli.bundle.mjs supply --amount 1
  node dist/cli/cli.bundle.mjs borrow --simulate
  node dist/cli/cli.bundle.mjs borrow --simulate --simulate-supply 1
  node dist/cli/cli.bundle.mjs borrow --amount 100
  node dist/cli/cli.bundle.mjs repay --simulate --amount 50
  node dist/cli/cli.bundle.mjs repay --simulate --repay-all
  node dist/cli/cli.bundle.mjs repay --amount 50
  node dist/cli/cli.bundle.mjs repay --repay-all
  node dist/cli/cli.bundle.mjs market-withdraw --amount 0.5
  node dist/cli/cli.bundle.mjs market-withdraw --withdraw-all

Options:
  --vault <address>          Vault contract address
  --market <address>         Market ID (contract address)
  --amount <number>          Amount in token units
  --chain <chain>            Chain ID (default: eip155:56)
  --page <number>            List page
  --page-size <number>       List page size
  --sort <field>             Sort field
  --order <asc|desc>         Sort direction
  --zone <zone>              Zone filter
  --keyword <text>           Search keyword
  --assets <a,b>             Asset filter (vaults)
  --curators <a,b>           Curator filter (vaults)
  --loans <a,b>              Loan token filter (markets)
  --collaterals <a,b>        Collateral token filter (markets)
  --withdraw-all             Withdraw entire vault position
  --repay-all                Repay entire loan
  --simulate                 Simulate borrow/repay impact without executing
  --simulate-supply <amt>    Show max borrowable after hypothetical supply
  --wallet-topic <topic>     WalletConnect session topic
  --wallet-address <addr>    Connected wallet address
  --address <addr>           User address for holdings query
  --scope <type>             Holdings scope: all|vault|market|selected
  --show                     Show current selection/config
  --clear                    Clear selection
  --debug-log-file <path>    Append structured stdout/stderr logs to a file (jsonl)

Workflow Examples:
  Vault:
    1. holdings --address 0xUSER
    2. select --vault 0xVAULT --wallet-topic ... --wallet-address ...
    3. deposit --amount 100
    4. withdraw --amount 50

  Market:
    1. markets --chain eip155:56
    2. select --market 0xMARKET --wallet-topic ... --wallet-address ...
    3. supply --amount 1
    4. borrow --simulate
    5. borrow --amount 500
    6. repay --amount 250
    7. market-withdraw --amount 0.5

Supported Chains:
  eip155:56   BSC (default)
  eip155:1    Ethereum`;
}

// src/cli/meta.ts
import { readFileSync } from "fs";
import { resolve as resolve2, dirname as dirname2 } from "path";
import { fileURLToPath } from "url";
function loadCliMeta() {
  const __dirname2 = dirname2(fileURLToPath(import.meta.url));
  const pkgPath = resolve2(__dirname2, "../../package.json");
  const pkg = JSON.parse(readFileSync(pkgPath, "utf8"));
  return {
    skillVersion: pkg.version || "0.1.0",
    skillName: pkg.name || "@lista-dao/lista-lending-skill",
    walletConnectVersion: pkg.skillRequires?.["lista-wallet-connect"] || ">=1.0.0"
  };
}

// src/sdk/client.ts
import { MoolahSDK } from "@lista-dao/moolah-lending-sdk";

// src/config.ts
import { existsSync, mkdirSync as mkdirSync2, readFileSync as readFileSync2, writeFileSync } from "fs";
import { homedir } from "os";
import { join } from "path";
var CONFIG_DIR = join(homedir(), ".agent-wallet");
var CONFIG_FILE = join(CONFIG_DIR, "lending-config.json");
var DEFAULT_RPCS = {
  "eip155:56": [
    "https://bsc-dataseed.binance.org",
    "https://bsc-dataseed1.bnbchain.org",
    "https://bsc-dataseed2.bnbchain.org",
    "https://bsc-dataseed3.bnbchain.org",
    "https://bsc-rpc.publicnode.com",
    "https://bsc-dataseed1.binance.org"
  ],
  "eip155:1": [
    "https://eth.drpc.org",
    "https://mainnet.gateway.tenderly.co",
    "https://ethereum-rpc.publicnode.com",
    "https://cloudflare-eth.com",
    "https://eth.llamarpc.com"
  ]
};
var CHAIN_IDS = {
  "eip155:56": 56,
  "eip155:1": 1
};
var SUPPORTED_CHAINS = ["eip155:56", "eip155:1"];
var DEFAULT_CONFIG = {
  rpcUrls: {},
  defaultChain: "eip155:56"
};
function ensureConfigDir() {
  if (!existsSync(CONFIG_DIR)) {
    mkdirSync2(CONFIG_DIR, { recursive: true });
  }
}
function loadConfig() {
  try {
    if (existsSync(CONFIG_FILE)) {
      const data = readFileSync2(CONFIG_FILE, "utf-8");
      const parsed2 = JSON.parse(data);
      return {
        ...DEFAULT_CONFIG,
        ...parsed2
      };
    }
  } catch {
  }
  return { ...DEFAULT_CONFIG };
}
function saveConfig(config) {
  ensureConfigDir();
  writeFileSync(CONFIG_FILE, JSON.stringify(config, null, 2));
}
function getRpcUrl(chain) {
  const candidates = getRpcUrls(chain);
  if (candidates.length > 0) {
    return candidates[0];
  }
  throw new Error(`No RPC URL configured for chain: ${chain}`);
}
function getRpcUrls(chain) {
  const config = loadConfig();
  const result = [];
  const seen = /* @__PURE__ */ new Set();
  const addUrl = (value) => {
    if (!value) return;
    const normalized = value.trim();
    if (!normalized || seen.has(normalized)) return;
    seen.add(normalized);
    result.push(normalized);
  };
  addUrl(config.rpcUrls[chain]);
  const defaults = DEFAULT_RPCS[chain] || [];
  for (const url of defaults) {
    addUrl(url);
  }
  return result;
}
function setRpcUrl(chain, url) {
  if (!SUPPORTED_CHAINS.includes(chain)) {
    throw new Error(
      `Unsupported chain: ${chain}. Supported: ${SUPPORTED_CHAINS.join(", ")}`
    );
  }
  const config = loadConfig();
  config.rpcUrls[chain] = url;
  saveConfig(config);
}
function clearRpcUrl(chain) {
  const config = loadConfig();
  delete config.rpcUrls[chain];
  saveConfig(config);
}
function getChainId(chain) {
  const chainId = CHAIN_IDS[chain];
  if (!chainId) {
    throw new Error(
      `Unknown chain: ${chain}. Supported: ${SUPPORTED_CHAINS.join(", ")}`
    );
  }
  return chainId;
}
function isUsingCustomRpc(chain) {
  const config = loadConfig();
  return !!config.rpcUrls[chain];
}
function getRpcType(chain) {
  return isUsingCustomRpc(chain) ? "custom" : "public";
}
function getRpcConfig(chain) {
  const type = getRpcType(chain);
  if (type === "custom") {
    return {
      type: "custom",
      vaultConcurrency: 5,
      marketConcurrency: 3,
      itemTimeout: 8e3,
      totalBudget: 35e3,
      retryCount: 2,
      retryDelay: 500
    };
  }
  return {
    type: "public",
    vaultConcurrency: 2,
    marketConcurrency: 1,
    itemTimeout: 12e3,
    totalBudget: 7e4,
    retryCount: 3,
    retryDelay: 800
  };
}

// src/sdk/client.ts
var sdkInstance = null;
var sdkSignature = null;
function parseIntEnv(value, fallback) {
  const parsed2 = Number.parseInt(value || "", 10);
  return Number.isFinite(parsed2) ? parsed2 : fallback;
}
function buildRpcConfig() {
  const config = {};
  for (const chain of SUPPORTED_CHAINS) {
    const rpcUrls = getRpcUrls(chain);
    if (rpcUrls.length === 0) continue;
    config[String(getChainId(chain))] = rpcUrls;
  }
  return config;
}
function buildTransportConfigByChain() {
  const transportByChainId = {};
  for (const chain of SUPPORTED_CHAINS) {
    const rpcConfig = getRpcConfig(chain);
    transportByChainId[String(getChainId(chain))] = {
      timeout: parseIntEnv(process.env.LISTA_RPC_TIMEOUT_MS, rpcConfig.itemTimeout),
      retryCount: parseIntEnv(process.env.LISTA_RPC_RETRY_COUNT, rpcConfig.retryCount),
      retryDelay: parseIntEnv(process.env.LISTA_RPC_RETRY_DELAY_MS, rpcConfig.retryDelay)
    };
  }
  return transportByChainId;
}
function buildSdkSignature(rpcUrls, transportByChainId) {
  return JSON.stringify({ rpcUrls, transportByChainId });
}
function getSDK() {
  const rpcUrls = buildRpcConfig();
  const transportByChainId = buildTransportConfigByChain();
  const signature = buildSdkSignature(rpcUrls, transportByChainId);
  if (!sdkInstance || sdkSignature !== signature) {
    sdkInstance = new MoolahSDK({
      rpcUrls,
      transportByChainId
    });
    sdkSignature = signature;
  }
  return sdkInstance;
}

// src/sdk/market-runtime.ts
async function getMarketRuntimeData(chainId, marketId, walletAddress) {
  return getSDK().getMarketRuntimeData(chainId, marketId, walletAddress);
}

// src/executor.ts
import { execSync } from "child_process";

// src/utils/tx-error.ts
function toText2(value) {
  if (value === null || value === void 0) return "";
  if (typeof value === "string") return value;
  if (value instanceof Buffer) return value.toString("utf-8");
  return String(value);
}
function parseJsonLines(text) {
  const responses = [];
  for (const raw of text.split("\n")) {
    const line = raw.trim();
    if (!line.startsWith("{") || !line.endsWith("}")) continue;
    try {
      responses.push(JSON.parse(line));
    } catch {
    }
  }
  return responses;
}
function extractWalletConnectResponses(err) {
  const e = err;
  const chunks = [
    toText2(e.stdout),
    toText2(e.stderr),
    ...Array.isArray(e.output) ? e.output.map((item) => toText2(item)) : []
  ].filter(Boolean);
  const responses = [];
  for (const chunk of chunks) {
    responses.push(...parseJsonLines(chunk));
  }
  return responses;
}
function extractRevertReason(value) {
  const normalize = (reason) => {
    const cleaned = reason.replace(/\.$/, "").trim();
    const hexSuffix = cleaned.match(/^(.*?):\s*0x[0-9a-fA-F]+$/);
    if (hexSuffix?.[1]) {
      return hexSuffix[1].trim();
    }
    return cleaned;
  };
  const withReasonMatch = value.match(/with reason:\s*([^\n]+)/i);
  if (withReasonMatch?.[1]) {
    return normalize(withReasonMatch[1]);
  }
  const revertedMatch = value.match(/execution reverted:?\s*([^\n]+)/i);
  if (revertedMatch?.[1]) {
    return normalize(revertedMatch[1]);
  }
  return normalize(value);
}
function mapWalletConnectResponse(response, step, explorerUrl) {
  if (response.status === "sent") {
    if (!response.txHash) {
      return {
        status: "error",
        reason: "wallet_connect_missing_tx_hash",
        step
      };
    }
    return {
      status: "sent",
      txHash: response.txHash,
      explorer: explorerUrl,
      step
    };
  }
  if (response.status === "rejected") {
    return {
      status: "rejected",
      reason: "user_rejected",
      step
    };
  }
  return {
    status: "error",
    reason: response.error || "Unknown error",
    step
  };
}
function mapExecutionError(err, step) {
  const responses = extractWalletConnectResponses(err);
  const simulationFailed = responses.find((r) => r.status === "simulation_failed");
  if (simulationFailed) {
    const rawReason = simulationFailed.revertReason || simulationFailed.error || simulationFailed.reason || "Transaction simulation failed";
    return {
      status: "reverted",
      reason: extractRevertReason(rawReason),
      step
    };
  }
  const rejected = responses.find((r) => r.status === "rejected");
  if (rejected) {
    return {
      status: "rejected",
      reason: "user_rejected",
      step
    };
  }
  const message = err?.message || String(err);
  if (message.includes("User rejected") || message.includes("rejected")) {
    return {
      status: "rejected",
      reason: "user_rejected",
      step
    };
  }
  if (message.includes("revert") || message.includes("execution reverted")) {
    const revertMatch = message.match(/reason="([^"]+)"/);
    return {
      status: "reverted",
      reason: revertMatch ? revertMatch[1] : "Contract execution reverted",
      step
    };
  }
  if (message.includes("insufficient funds")) {
    return {
      status: "error",
      reason: "insufficient_balance",
      step
    };
  }
  return {
    status: "error",
    reason: message,
    step
  };
}

// src/executor/constants.ts
import { resolve as resolve3, dirname as dirname3 } from "path";
import { fileURLToPath as fileURLToPath2 } from "url";
var __dirname = dirname3(fileURLToPath2(import.meta.url));
var WALLET_CONNECT_CLI = resolve3(
  __dirname,
  "../../../lista-wallet-connect/dist/cli/cli.bundle.mjs"
);
var EXPLORER_URLS = {
  "eip155:56": "https://bscscan.com/tx/",
  "eip155:1": "https://etherscan.io/tx/"
};
function getExplorerUrl(chain, txHash) {
  const baseUrl = EXPLORER_URLS[chain] || EXPLORER_URLS["eip155:56"];
  return `${baseUrl}${txHash}`;
}

// src/executor/receipt.ts
import { createPublicClient, http } from "viem";
import { bsc, mainnet } from "viem/chains";
var CHAIN_TO_VIEM = {
  "eip155:56": bsc,
  "eip155:1": mainnet
};
function parseIntEnv2(value, fallback) {
  const parsed2 = Number.parseInt(value || "", 10);
  return Number.isFinite(parsed2) ? parsed2 : fallback;
}
var TX_RECEIPT_TIMEOUT_MS = parseIntEnv2(
  process.env.LISTA_TX_RECEIPT_TIMEOUT_MS,
  12e4
);
var TX_RECEIPT_POLLING_MS = parseIntEnv2(
  process.env.LISTA_TX_RECEIPT_POLLING_MS,
  1500
);
var TX_RECEIPT_CONFIRMATIONS = parseIntEnv2(
  process.env.LISTA_TX_RECEIPT_CONFIRMATIONS,
  1
);
function isTimeoutErrorMessage(message) {
  const lower = message.toLowerCase();
  return lower.includes("timeout") || lower.includes("timed out") || lower.includes("deadline") || lower.includes("aborted");
}
async function waitForTransactionFinality(chain, txHash) {
  const viemChain = CHAIN_TO_VIEM[chain];
  if (!viemChain) {
    return {
      ok: false,
      reason: "tx_receipt_wait_unsupported_chain",
      attempts: [{ rpcUrl: "n/a", error: `Unsupported chain for receipt wait: ${chain}` }]
    };
  }
  const rpcUrls = getRpcUrls(chain);
  if (rpcUrls.length === 0) {
    return {
      ok: false,
      reason: "tx_receipt_wait_no_rpc_candidates",
      attempts: [{ rpcUrl: "n/a", error: `No RPC candidates configured for ${chain}` }]
    };
  }
  const attempts = [];
  let timeoutDetected = false;
  for (const rpcUrl of rpcUrls) {
    const client = createPublicClient({
      chain: viemChain,
      transport: http(rpcUrl, {
        timeout: Math.max(1e3, TX_RECEIPT_TIMEOUT_MS),
        retryCount: 1,
        retryDelay: 250
      })
    });
    try {
      const receipt = await client.waitForTransactionReceipt({
        hash: txHash,
        confirmations: Math.max(1, TX_RECEIPT_CONFIRMATIONS),
        timeout: Math.max(1e3, TX_RECEIPT_TIMEOUT_MS),
        pollingInterval: Math.max(250, TX_RECEIPT_POLLING_MS)
      });
      return {
        ok: true,
        reverted: receipt.status === "reverted",
        rpcUrl,
        blockNumber: receipt.blockNumber.toString()
      };
    } catch (err) {
      const message = err.message || String(err);
      attempts.push({ rpcUrl, error: message });
      if (isTimeoutErrorMessage(message)) {
        timeoutDetected = true;
      }
    }
  }
  return {
    ok: false,
    reason: timeoutDetected ? "tx_submitted_pending_confirmation" : "tx_submitted_receipt_unavailable",
    attempts
  };
}

// src/executor.ts
async function executeStep(step, options) {
  const { topic, chain = "eip155:56" } = options;
  const { params } = step;
  const args = [
    "call",
    "--topic",
    topic,
    "--chain",
    chain,
    "--to",
    params.to,
    "--data",
    params.data
  ];
  if (params.value && params.value > 0n) {
    args.push("--value", params.value.toString());
  }
  try {
    const cmd = `node "${WALLET_CONNECT_CLI}" ${args.map((a) => `"${a}"`).join(" ")}`;
    const result = execSync(cmd, {
      encoding: "utf-8",
      timeout: 5 * 60 * 1e3,
      env: {
        ...process.env,
        WALLETCONNECT_PROJECT_ID: process.env.WALLETCONNECT_PROJECT_ID
      }
    });
    const lines = result.trim().split("\n");
    const response = JSON.parse(lines[lines.length - 1]);
    const txResult = mapWalletConnectResponse(
      response,
      step.step,
      response.txHash ? getExplorerUrl(chain, response.txHash) : void 0
    );
    if (txResult.status !== "sent") {
      return txResult;
    }
    if (!txResult.txHash) {
      return {
        status: "error",
        reason: "wallet_connect_missing_tx_hash",
        step: step.step
      };
    }
    const receiptResult = await waitForTransactionFinality(chain, txResult.txHash);
    if (!receiptResult.ok) {
      return {
        status: "pending",
        reason: receiptResult.reason || "tx_submitted_pending_confirmation",
        step: step.step,
        txHash: txResult.txHash,
        explorer: txResult.explorer
      };
    }
    if (receiptResult.reverted) {
      return {
        status: "reverted",
        reason: "transaction_reverted_onchain",
        step: step.step,
        txHash: txResult.txHash,
        explorer: txResult.explorer
      };
    }
    return txResult;
  } catch (err) {
    return mapExecutionError(err, step.step);
  }
}
async function executeSteps(steps, options) {
  const results = [];
  for (let i = 0; i < steps.length; i++) {
    const result = await executeStep(steps[i], options);
    results.push(result);
    if (result.status !== "sent") break;
  }
  return results;
}

// src/context.ts
import { existsSync as existsSync2, mkdirSync as mkdirSync3, readFileSync as readFileSync3, writeFileSync as writeFileSync2 } from "fs";
import { homedir as homedir2 } from "os";
import { join as join2 } from "path";
var CONFIG_DIR2 = join2(homedir2(), ".agent-wallet");
var CONTEXT_FILE = join2(CONFIG_DIR2, "lending-context.json");
var CONTEXT_SCHEMA_VERSION = 2;
var DEFAULT_CONTEXT = {
  schemaVersion: CONTEXT_SCHEMA_VERSION,
  selectedVault: null,
  selectedMarket: null,
  userAddress: null,
  walletTopic: null,
  userPosition: null,
  lastFilters: null,
  lastUpdated: null
};
function ensureConfigDir2() {
  if (!existsSync2(CONFIG_DIR2)) {
    mkdirSync3(CONFIG_DIR2, { recursive: true });
  }
}
function isObject(value) {
  return typeof value === "object" && value !== null;
}
function isSelectedVault(value) {
  if (!isObject(value)) return false;
  if (typeof value.address !== "string") return false;
  if (typeof value.name !== "string") return false;
  if (typeof value.chain !== "string") return false;
  if (!isObject(value.asset)) return false;
  return typeof value.asset.symbol === "string" && typeof value.asset.address === "string" && typeof value.asset.decimals === "number";
}
function isSelectedMarket(value) {
  if (!isObject(value)) return false;
  return typeof value.marketId === "string" && typeof value.chain === "string";
}
function isUserPosition(value) {
  if (!isObject(value)) return false;
  return typeof value.shares === "string" && typeof value.assets === "string";
}
function isLastFilters(value) {
  return isObject(value);
}
function migrateContext(raw) {
  const base = { ...DEFAULT_CONTEXT };
  if (!isObject(raw)) {
    return base;
  }
  const old = raw;
  const selectedVault = isSelectedVault(old.selectedVault) ? old.selectedVault : null;
  const selectedMarket = isSelectedMarket(old.selectedMarket) ? old.selectedMarket : null;
  const userPosition = isUserPosition(old.userPosition) ? old.userPosition : null;
  const lastFilters = isLastFilters(old.lastFilters) ? old.lastFilters : null;
  return {
    schemaVersion: CONTEXT_SCHEMA_VERSION,
    selectedVault,
    selectedMarket,
    userAddress: typeof old.userAddress === "string" ? old.userAddress : base.userAddress,
    walletTopic: typeof old.walletTopic === "string" ? old.walletTopic : base.walletTopic,
    userPosition,
    lastFilters,
    lastUpdated: typeof old.lastUpdated === "string" ? old.lastUpdated : base.lastUpdated
  };
}
function loadContext() {
  try {
    if (existsSync2(CONTEXT_FILE)) {
      const data = readFileSync3(CONTEXT_FILE, "utf-8");
      return migrateContext(JSON.parse(data));
    }
  } catch {
  }
  return { ...DEFAULT_CONTEXT };
}
function saveContext(context) {
  ensureConfigDir2();
  context.schemaVersion = CONTEXT_SCHEMA_VERSION;
  context.lastUpdated = (/* @__PURE__ */ new Date()).toISOString();
  writeFileSync2(CONTEXT_FILE, JSON.stringify(context, null, 2));
}
function setSelectedVault(vault, userAddress, walletTopic, position) {
  const context = loadContext();
  context.selectedVault = vault;
  context.selectedMarket = null;
  context.userAddress = userAddress;
  context.walletTopic = walletTopic;
  context.userPosition = position || null;
  saveContext(context);
}
function setSelectedMarket(market, userAddress, walletTopic) {
  const context = loadContext();
  context.selectedMarket = market;
  context.selectedVault = null;
  context.userPosition = null;
  context.userAddress = userAddress;
  context.walletTopic = walletTopic;
  saveContext(context);
}
function updatePosition(position) {
  const context = loadContext();
  context.userPosition = position;
  saveContext(context);
}
function setLastFilters(filters) {
  const context = loadContext();
  context.lastFilters = {
    ...context.lastFilters || {},
    ...filters
  };
  saveContext(context);
}
function clearContext() {
  saveContext({ ...DEFAULT_CONTEXT });
}

// src/utils/position.ts
import { Decimal } from "@lista-dao/moolah-lending-sdk";
function mapVaultUserPosition(userData) {
  const shares = userData.shares?.toFixed(8) || "0";
  const assets = userData.locked?.toFixed(8) || "0";
  const walletBalance = userData.balance?.toFixed(8) || "0";
  return {
    position: {
      shares,
      assets
    },
    shares,
    assets,
    walletBalance,
    hasPosition: Number.parseFloat(assets) > 0
  };
}
function mapMarketUserPosition(userData, prices) {
  const collateralPrice = Decimal.parse(prices.collateralPrice || 0);
  const loanPrice = Decimal.parse(prices.loanPrice || 0);
  const collateral = userData.collateral?.toFixed(8) || "0";
  const borrowed = userData.borrowed?.toFixed(8) || "0";
  const collateralUsd = userData.collateral.mul(collateralPrice).toFixed(8);
  const borrowedUsd = userData.borrowed.mul(loanPrice).toFixed(8);
  const healthValue = userData.LTV.gt(0) ? userData.LLTV.div(userData.LTV).roundDown(18) : Decimal.parse(100);
  return {
    collateral,
    collateralUsd,
    borrowed,
    borrowedUsd,
    ltv: userData.LTV.toFixed(8),
    lltv: userData.LLTV.toFixed(8),
    health: healthValue.toFixed(8),
    liquidationPriceRate: userData.liqPriceRate.toFixed(18),
    borrowRate: userData.borrowRate.toFixed(8),
    walletCollateralBalance: userData.balances.collateral?.toFixed(8) || "0",
    walletLoanBalance: userData.balances.loan?.toFixed(8) || "0",
    hasPosition: Number.parseFloat(collateral) > 0 || Number.parseFloat(borrowed) > 0,
    isWhitelisted: userData.isWhiteList
  };
}

// src/utils/validators.ts
import { isAddress, parseUnits } from "viem";
var InputValidationError = class extends Error {
  constructor(message) {
    super(message);
    this.name = "InputValidationError";
  }
};
function isSupportedChain(chain, supportedChains) {
  return supportedChains.includes(chain);
}
function isPositiveInteger(value) {
  return value !== void 0 && Number.isInteger(value) && value > 0;
}
function isValidOrder(value) {
  return value === "asc" || value === "desc";
}
function isValidAddress(value) {
  return isAddress(value);
}
function isValidMarketId(value) {
  if (isAddress(value)) return true;
  return /^0x[a-fA-F0-9]{64}$/.test(value);
}
function parsePositiveUnits(value, decimals, fieldName) {
  try {
    const parsed2 = parseUnits(value, decimals);
    if (parsed2 <= 0n) {
      throw new InputValidationError(`--${fieldName} must be a positive number`);
    }
    return parsed2;
  } catch (err) {
    if (err instanceof InputValidationError) throw err;
    throw new InputValidationError(`--${fieldName} must be a valid positive number`);
  }
}
function normalizeHoldingChain(chain) {
  const normalized = chain.trim().toLowerCase();
  if (normalized === "bsc") return "eip155:56";
  if (normalized === "ethereum" || normalized === "eth") return "eip155:1";
  throw new InputValidationError(`Unsupported holdings chain from API: ${chain}`);
}

// src/commands/shared/wallet-session.ts
import { existsSync as existsSync3, readFileSync as readFileSync4 } from "fs";
import { homedir as homedir3 } from "os";
import { join as join3 } from "path";
var WALLET_SESSIONS_FILE = join3(homedir3(), ".agent-wallet", "sessions.json");
function parseAccountAddress(account) {
  return account.split(":").slice(2).join(":");
}
function inferLatestTopicByAddress(address) {
  if (!existsSync3(WALLET_SESSIONS_FILE)) return null;
  try {
    const sessions = JSON.parse(
      readFileSync4(WALLET_SESSIONS_FILE, "utf-8")
    );
    const needle = address.toLowerCase();
    const matches = Object.entries(sessions).filter(
      ([, session]) => (session.accounts || []).some(
        (account) => parseAccountAddress(account).toLowerCase() === needle
      )
    ).map(([topic, session]) => ({
      topic,
      sortKey: session.updatedAt || session.createdAt || ""
    })).sort((a, b) => b.sortKey.localeCompare(a.sortKey));
    if (matches.length === 0) return null;
    return matches[0].topic;
  } catch {
    return null;
  }
}

// src/commands/shared/context.ts
var DEFAULT_CHAIN = "eip155:56";
function requireAddress(value, missingMessage, invalidMessageFactory) {
  if (!value) {
    throw new InputValidationError(missingMessage);
  }
  if (!isValidAddress(value)) {
    throw new InputValidationError(invalidMessageFactory(value));
  }
  return value;
}
function requireWalletTopic(value) {
  if (!value) {
    throw new InputValidationError(
      "No wallet connected. Use 'select' or provide --wallet-topic"
    );
  }
  return value;
}
function requireMarketId(value) {
  if (!value) {
    throw new InputValidationError(
      "No market selected. Use 'select --market <id>' or provide --market"
    );
  }
  if (!isValidMarketId(value)) {
    throw new InputValidationError(`Invalid market ID: ${value}`);
  }
  return value;
}
function requireSupportedChain(chain, supportedChains) {
  if (!isSupportedChain(chain, supportedChains)) {
    throw new InputValidationError(
      `Unsupported chain: ${chain}. Supported: ${supportedChains.join(", ")}`
    );
  }
  return chain;
}
function requireAmount(value) {
  if (!value) {
    throw new InputValidationError("--amount required");
  }
  return value;
}
function requireAmountOrAll(amount, allFlag, allFlagName) {
  if (!amount && !allFlag) {
    throw new InputValidationError(`--amount or ${allFlagName} required`);
  }
  if (amount && allFlag) {
    throw new InputValidationError(
      `--amount and ${allFlagName} cannot be used together`
    );
  }
}
function resolveVaultContext(args, ctx, options) {
  const vaultAddressInput = args.vault || ctx.selectedVault?.address;
  const chain = args.chain || ctx.selectedVault?.chain || DEFAULT_CHAIN;
  let walletTopicInput = args.walletTopic || null;
  const walletAddressInput = args.walletAddress || ctx.userAddress;
  if (args.walletAddress && !args.walletTopic) {
    const inferredTopic = inferLatestTopicByAddress(args.walletAddress);
    if (inferredTopic) {
      walletTopicInput = inferredTopic;
    } else if (options.requireWalletTopic !== false) {
      throw new InputValidationError(
        `No wallet session found for ${args.walletAddress}. Provide --wallet-topic or reconnect this wallet`
      );
    }
  } else if (!walletTopicInput) {
    walletTopicInput = ctx.walletTopic || null;
  }
  const vaultAddress = requireAddress(
    vaultAddressInput,
    "No vault selected. Use 'select --vault <address>' or provide --vault",
    (value) => `Invalid vault address: ${value}`
  );
  const walletAddress = requireAddress(
    walletAddressInput,
    "No wallet address. Use 'select' or provide --wallet-address",
    (value) => `Invalid wallet address: ${value}`
  );
  requireSupportedChain(chain, options.supportedChains);
  const walletTopic = options.requireWalletTopic === false ? walletTopicInput || null : requireWalletTopic(walletTopicInput);
  return {
    vaultAddress,
    chain,
    walletAddress,
    walletTopic
  };
}
function resolveMarketContext(args, ctx, options) {
  const marketIdInput = args.market || ctx.selectedMarket?.marketId;
  const chain = args.chain || ctx.selectedMarket?.chain || DEFAULT_CHAIN;
  let walletTopicInput = args.walletTopic || null;
  const walletAddressInput = args.walletAddress || ctx.userAddress;
  if (args.walletAddress && !args.walletTopic) {
    const inferredTopic = inferLatestTopicByAddress(args.walletAddress);
    if (inferredTopic) {
      walletTopicInput = inferredTopic;
    } else if (options.requireWalletTopic !== false) {
      throw new InputValidationError(
        `No wallet session found for ${args.walletAddress}. Provide --wallet-topic or reconnect this wallet`
      );
    }
  } else if (!walletTopicInput) {
    walletTopicInput = ctx.walletTopic || null;
  }
  const validMarketId = requireMarketId(marketIdInput);
  const walletAddress = requireAddress(
    walletAddressInput,
    "No wallet address. Use 'select' or provide --wallet-address",
    (value) => `Invalid wallet address: ${value}`
  );
  requireSupportedChain(chain, options.supportedChains);
  const walletTopic = options.requireWalletTopic === false ? walletTopicInput || null : requireWalletTopic(walletTopicInput);
  return {
    marketId: validMarketId,
    chain,
    walletAddress,
    walletTopic
  };
}

// src/commands/shared/output.ts
function stringifyJson(payload) {
  return JSON.stringify(payload);
}
function printJson(payload) {
  console.log(stringifyJson(payload));
}
function printErrorJson(payload) {
  console.error(stringifyJson(payload));
}
function exitWithCode(code) {
  process.exit(code);
}

// src/commands/shared/tx.ts
function ensureStepsGenerated(steps) {
  if (steps.length === 0) {
    throw new InputValidationError("No steps generated");
  }
  return steps;
}
function buildExecutionFailureOutput(results, totalSteps) {
  const lastResult = results[results.length - 1];
  const completedSteps = countCompletedSentSteps(results);
  const output = {
    status: lastResult?.status || "error",
    reason: lastResult?.reason || "execution_failed",
    failedStep: lastResult?.step,
    completedSteps,
    totalSteps
  };
  const successfulTxs = collectSuccessfulTxs(results);
  if (successfulTxs.length > 0) {
    output.completedTxs = successfulTxs;
  }
  return output;
}
function buildPendingExecutionOutput(result, results, totalSteps) {
  return {
    status: "pending",
    reason: result.reason || "tx_submitted_pending_confirmation",
    pendingStep: result.step,
    txHash: result.txHash,
    explorer: result.explorer,
    completedSteps: countCompletedSentSteps(results),
    totalSteps,
    message: "Transaction was submitted but confirmation is still pending. Please check explorer and avoid resubmitting the same action."
  };
}
function countCompletedSentSteps(results) {
  return results.filter((r) => r.status === "sent").length;
}
function collectSuccessfulTxs(results) {
  return results.filter((r) => r.status === "sent").map((r) => ({ step: r.step, txHash: r.txHash }));
}

// src/commands/shared/errors.ts
var DEFAULT_INSUFFICIENT_KEYWORDS = ["insufficient", "exceeds", "balance"];
function buildSdkErrorOutput(message, options) {
  const targetLabel = options.targetType === "vault" /* Vault */ ? "Vault" : "Market";
  const invalidPhrase = options.targetType === "vault" /* Vault */ ? message.includes("vault not found") || message.includes("invalid vault") : message.includes("market not found") || message.includes("invalid market");
  if (invalidPhrase) {
    return {
      status: "error",
      reason: options.targetType === "vault" /* Vault */ ? "invalid_vault" : "invalid_market",
      message: options.targetId ? `${targetLabel} ${options.targetId} not found or invalid` : `${targetLabel} not found or invalid`
    };
  }
  const insufficientKeywords = options.insufficientKeywords || DEFAULT_INSUFFICIENT_KEYWORDS;
  const isInsufficient = insufficientKeywords.some(
    (keyword) => message.toLowerCase().includes(keyword.toLowerCase())
  );
  if (isInsufficient && options.insufficientReason && options.insufficientMessage) {
    return {
      status: "error",
      reason: options.insufficientReason,
      message: options.insufficientMessage
    };
  }
  if (message.includes("RPC") || message.includes("fetch")) {
    return {
      status: "error",
      reason: "rpc_error",
      message,
      hint: "Try setting a custom RPC with: config --set-rpc --chain <chain> --url <url>"
    };
  }
  return {
    status: "error",
    reason: "sdk_error",
    message
  };
}

// src/commands/deposit.ts
async function cmdDeposit(args) {
  const ctx = loadContext();
  let operationContext;
  try {
    const amount = requireAmount(args.amount);
    const { vaultAddress, chain, walletAddress, walletTopic } = resolveVaultContext(
      args,
      ctx,
      { supportedChains: SUPPORTED_CHAINS }
    );
    const chainId = getChainId(chain);
    const sdk = getSDK();
    operationContext = {
      vaultAddress,
      chain,
      amount
    };
    const vaultInfo = await sdk.getVaultInfo(chainId, vaultAddress);
    const assetInfo = vaultInfo.assetInfo;
    const decimals = assetInfo.decimals;
    const assets = parsePositiveUnits(amount, decimals, "amount");
    const steps = ensureStepsGenerated(
      await sdk.buildVaultDepositParams({
        chainId,
        vaultAddress,
        assets,
        walletAddress,
        vaultInfo
      })
    );
    const results = await executeSteps(steps, {
      topic: walletTopic,
      chain
    });
    const lastResult = results[results.length - 1];
    if (lastResult.status === "pending") {
      printJson(buildPendingExecutionOutput(lastResult, results, steps.length));
      exitWithCode(0);
    }
    if (lastResult.status === "sent") {
      const freshVaultInfo = await sdk.getVaultInfo(chainId, vaultAddress);
      const userData = await sdk.getVaultUserData(
        chainId,
        vaultAddress,
        walletAddress,
        freshVaultInfo
      );
      const mappedPosition = mapVaultUserPosition(userData);
      const newPosition = mappedPosition.position;
      if (ctx.selectedVault?.address === vaultAddress) {
        updatePosition(newPosition);
      }
      printJson({
        status: "success",
        vault: vaultAddress,
        chain,
        asset: assetInfo.symbol,
        deposited: amount,
        steps: results.length,
        txHash: lastResult.txHash,
        explorer: lastResult.explorer,
        balance: mappedPosition.walletBalance,
        vaultBalance: newPosition.assets,
        position: {
          balance: newPosition.assets,
          assets: newPosition.assets,
          walletBalance: mappedPosition.walletBalance,
          assetSymbol: assetInfo.symbol
        }
      });
      exitWithCode(0);
    }
    printJson(buildExecutionFailureOutput(results, steps.length));
    exitWithCode(1);
  } catch (err) {
    if (err instanceof InputValidationError) {
      printJson({
        status: "error",
        reason: err.message
      });
      exitWithCode(1);
    }
    const message = err.message || String(err);
    printJson(
      buildSdkErrorOutput(message, {
        targetType: "vault" /* Vault */,
        targetId: operationContext?.vaultAddress
      })
    );
    exitWithCode(1);
  }
}

// src/commands/withdraw.ts
async function cmdWithdraw(args) {
  const ctx = loadContext();
  let operationContext;
  try {
    requireAmountOrAll(args.amount, args.withdrawAll, "--withdraw-all");
    const { vaultAddress, chain, walletAddress, walletTopic } = resolveVaultContext(
      args,
      ctx,
      { supportedChains: SUPPORTED_CHAINS }
    );
    const chainId = getChainId(chain);
    const sdk = getSDK();
    const vaultInfo = await sdk.getVaultInfo(chainId, vaultAddress);
    const userData = await sdk.getVaultUserData(
      chainId,
      vaultAddress,
      walletAddress,
      vaultInfo
    );
    if (args.withdrawAll && (!userData.shares || userData.shares.isZero())) {
      printJson({
        status: "error",
        reason: "no_position",
        message: "No shares to withdraw from this vault"
      });
      exitWithCode(1);
    }
    const assetInfo = vaultInfo.assetInfo;
    const decimals = assetInfo.decimals;
    let assets;
    if (args.amount) {
      assets = parsePositiveUnits(args.amount, decimals, "amount");
    }
    const operationAmount = args.amount || "all";
    operationContext = {
      vaultAddress,
      chain,
      amount: operationAmount
    };
    const steps = ensureStepsGenerated(
      await sdk.buildVaultWithdrawParams({
        chainId,
        vaultAddress,
        assets,
        withdrawAll: args.withdrawAll,
        walletAddress,
        vaultInfo,
        userData
      })
    );
    const results = await executeSteps(steps, {
      topic: walletTopic,
      chain
    });
    const lastResult = results[results.length - 1];
    if (lastResult.status === "pending") {
      printJson(buildPendingExecutionOutput(lastResult, results, steps.length));
      exitWithCode(0);
    }
    if (lastResult.status === "sent") {
      const freshVaultInfo = await sdk.getVaultInfo(chainId, vaultAddress);
      const newUserData = await sdk.getVaultUserData(
        chainId,
        vaultAddress,
        walletAddress,
        freshVaultInfo
      );
      const mappedPosition = mapVaultUserPosition(newUserData);
      const newPosition = mappedPosition.position;
      if (ctx.selectedVault?.address === vaultAddress) {
        updatePosition(newPosition);
      }
      printJson({
        status: "success",
        vault: vaultAddress,
        chain,
        asset: assetInfo.symbol,
        withdrawn: operationAmount,
        txHash: lastResult.txHash,
        explorer: lastResult.explorer,
        balance: mappedPosition.walletBalance,
        vaultBalance: newPosition.assets,
        position: {
          balance: newPosition.assets,
          assets: newPosition.assets,
          walletBalance: mappedPosition.walletBalance,
          assetSymbol: assetInfo.symbol,
          remaining: newPosition.assets !== "0"
        }
      });
      exitWithCode(0);
    }
    printJson(buildExecutionFailureOutput(results, steps.length));
    exitWithCode(1);
  } catch (err) {
    if (err instanceof InputValidationError) {
      printJson({
        status: "error",
        reason: err.message
      });
      exitWithCode(1);
    }
    const message = err.message || String(err);
    printJson(
      buildSdkErrorOutput(message, {
        targetType: "vault" /* Vault */,
        targetId: operationContext?.vaultAddress,
        insufficientReason: "insufficient_assets",
        insufficientMessage: "Withdrawal amount exceeds your vault balance",
        insufficientKeywords: ["insufficient", "exceeds balance"]
      })
    );
    exitWithCode(1);
  }
}

// src/commands/config.ts
async function cmdConfig(args) {
  if (args.show || !args.setRpc && !args.clearRpc) {
    const config = loadConfig();
    const rpcStatus = {};
    for (const chain of SUPPORTED_CHAINS) {
      const customUrl = config.rpcUrls[chain];
      const defaultUrl = DEFAULT_RPCS[chain]?.[0];
      rpcStatus[chain] = {
        url: customUrl || defaultUrl || "not configured",
        source: customUrl ? "custom" : "default"
      };
    }
    printJson({
      defaultChain: config.defaultChain,
      supportedChains: SUPPORTED_CHAINS,
      rpcUrls: rpcStatus,
      configFile: "~/.agent-wallet/lending-config.json"
    });
    return;
  }
  if (args.setRpc) {
    if (!args.chain) {
      printJson({ status: "error", reason: "--chain required" });
      process.exit(1);
    }
    if (!args.url) {
      printJson({ status: "error", reason: "--url required" });
      process.exit(1);
    }
    try {
      setRpcUrl(args.chain, args.url);
      printJson({
        status: "success",
        action: "set_rpc",
        chain: args.chain,
        url: args.url
      });
    } catch (err) {
      printJson({
        status: "error",
        reason: err.message
      });
      process.exit(1);
    }
    return;
  }
  if (args.clearRpc) {
    if (!args.chain) {
      printJson({ status: "error", reason: "--chain required" });
      process.exit(1);
    }
    try {
      clearRpcUrl(args.chain);
      const defaultUrl = getRpcUrl(args.chain);
      printJson({
        status: "success",
        action: "clear_rpc",
        chain: args.chain,
        revertedTo: defaultUrl
      });
    } catch (err) {
      printJson({
        status: "error",
        reason: err.message
      });
      process.exit(1);
    }
    return;
  }
}

// src/api/vault.ts
import { Decimal as Decimal2 } from "@lista-dao/moolah-lending-sdk";

// src/api/error-position.ts
function mapVaultErrorPosition(holding, chain, error) {
  return {
    kind: "vault",
    vaultAddress: holding.address,
    vaultName: holding.name,
    curator: holding.curator,
    apy: holding.apy,
    emissionApy: holding.emissionApy,
    chain,
    assetSymbol: "UNKNOWN",
    assetPrice: holding.assetPrice || "0",
    walletBalance: "0",
    deposited: "0",
    depositedUsd: "0",
    shares: "0",
    hasPosition: false,
    error
  };
}
function mapMarketErrorPosition(holding, chain, error) {
  const isSmartLending = holding.zone === 3;
  const isFixedTerm = holding.termType === 1;
  return {
    kind: "market",
    marketId: holding.marketId,
    chain,
    zone: holding.zone,
    termType: holding.termType,
    isSmartLending,
    isFixedTerm,
    isActionable: !isSmartLending && !isFixedTerm,
    broker: holding.broker || void 0,
    collateralSymbol: holding.collateralSymbol,
    collateralAddress: holding.collateralToken,
    collateralPrice: holding.collateralPrice,
    loanSymbol: holding.loanSymbol,
    loanAddress: holding.loanToken,
    loanPrice: holding.loanPrice,
    supplyApy: holding.supplyApy,
    borrowRate: "0",
    collateral: "0",
    collateralUsd: "0",
    borrowed: "0",
    borrowedUsd: "0",
    ltv: "0",
    lltv: holding.zone === 3 ? "0.909" : "0",
    health: "0",
    liquidationPriceRate: "0",
    walletCollateralBalance: "0",
    walletLoanBalance: "0",
    isWhitelisted: false,
    error
  };
}

// src/api/shared.ts
function parseIntEnv3(value, fallback) {
  const parsed2 = Number.parseInt(value || "", 10);
  return Number.isFinite(parsed2) ? parsed2 : fallback;
}
function getVaultConcurrency(chain) {
  const { vaultConcurrency } = getRpcConfig(chain);
  const envValue = process.env.LISTA_VAULT_ONCHAIN_CONCURRENCY;
  if (envValue) return parseIntEnv3(envValue, vaultConcurrency);
  return vaultConcurrency;
}
function getMarketConcurrency(chain) {
  const { marketConcurrency } = getRpcConfig(chain);
  const envValue = process.env.LISTA_MARKET_ONCHAIN_CONCURRENCY;
  if (envValue) return parseIntEnv3(envValue, marketConcurrency);
  return marketConcurrency;
}
function getItemTimeout(chain) {
  const { itemTimeout } = getRpcConfig(chain);
  const envValue = process.env.LISTA_ONCHAIN_ITEM_TIMEOUT_MS;
  if (envValue) return parseIntEnv3(envValue, itemTimeout);
  return itemTimeout;
}
function getTotalBudget(chain) {
  const { totalBudget } = getRpcConfig(chain);
  const envValue = process.env.LISTA_ONCHAIN_TOTAL_BUDGET_MS;
  if (envValue) return parseIntEnv3(envValue, totalBudget);
  return totalBudget;
}
async function withRpcGuard(operation, chain, label) {
  return withTimeout(operation(), getItemTimeout(chain), label);
}
function toApiChainFilter(chain, sdk) {
  const toApiChain = (chainValue) => {
    const normalized = chainValue.trim().toLowerCase();
    if (normalized === "bsc" || normalized === "ethereum") return normalized;
    if (normalized === "eth") return "ethereum";
    return sdk.getApiChain(getChainId(chainValue));
  };
  if (Array.isArray(chain)) {
    return chain.map(toApiChain);
  }
  return toApiChain(chain);
}
async function withTimeout(promise, timeoutMs, label) {
  let timeoutId;
  try {
    return await new Promise((resolve4, reject) => {
      timeoutId = setTimeout(() => {
        reject(new Error(`${label}_timeout_${timeoutMs}ms`));
      }, timeoutMs);
      promise.then(resolve4).catch(reject);
    });
  } finally {
    if (timeoutId) clearTimeout(timeoutId);
  }
}
async function mapWithConcurrency(items, concurrency, mapper) {
  if (items.length === 0) return [];
  const safeConcurrency = Math.max(
    1,
    Math.min(items.length, Number.isFinite(concurrency) ? concurrency : 1)
  );
  const results = new Array(items.length);
  let nextIndex = 0;
  const worker = async () => {
    while (true) {
      const current = nextIndex;
      nextIndex += 1;
      if (current >= items.length) return;
      results[current] = await mapper(items[current], current);
    }
  };
  await Promise.all(Array.from({ length: safeConcurrency }, () => worker()));
  return results;
}
async function mapByChainWithConcurrency(items, resolveChain, resolveConcurrency, mapper) {
  if (items.length === 0) return [];
  const buckets = /* @__PURE__ */ new Map();
  items.forEach((item, index) => {
    const chain = resolveChain(item);
    const bucket = buckets.get(chain);
    if (bucket) {
      bucket.push({ item, index });
      return;
    }
    buckets.set(chain, [{ item, index }]);
  });
  const results = new Array(items.length);
  await Promise.all(
    Array.from(buckets.entries()).map(async ([chain, bucketItems]) => {
      const concurrency = resolveConcurrency(chain);
      const mapped = await mapWithConcurrency(
        bucketItems,
        concurrency,
        async ({ item, index }) => ({
          index,
          value: await mapper(item, index)
        })
      );
      mapped.forEach(({ index, value }) => {
        results[index] = value;
      });
    })
  );
  return results.map((item, index) => {
    if (item === void 0) {
      throw new Error(`internal_missing_result_${index}`);
    }
    return item;
  });
}
function toAddress(value) {
  return value;
}
function sortByNumericDesc(items, getValue) {
  return [...items].sort((a, b) => {
    const aValue = Number.parseFloat(getValue(a));
    const bValue = Number.parseFloat(getValue(b));
    if (!Number.isFinite(aValue) && !Number.isFinite(bValue)) return 0;
    if (!Number.isFinite(aValue)) return 1;
    if (!Number.isFinite(bValue)) return -1;
    return bValue - aValue;
  });
}
function safeNormalizeHoldingChain(chain) {
  try {
    return normalizeHoldingChain(chain);
  } catch {
    return chain;
  }
}

// src/api/vault.ts
async function fetchVaults(query = {}) {
  const {
    chain = "eip155:56",
    page = 1,
    pageSize = 100,
    sort,
    order,
    zone,
    keyword,
    assets,
    curators
  } = query;
  const sdk = getSDK();
  const apiChain = toApiChainFilter(chain, sdk);
  const data = await sdk.getVaultList({
    chain: apiChain,
    page,
    pageSize,
    sort,
    order,
    zone,
    keyword,
    assets,
    curators
  });
  return data.list || [];
}
async function fetchVaultPositions(userAddress) {
  const sdk = getSDK();
  const data = await sdk.getHoldings({
    userAddress: toAddress(userAddress),
    type: "vault"
  });
  const holdings = data.objs || [];
  const chains = Array.from(
    new Set(holdings.map((holding) => safeNormalizeHoldingChain(holding.chain)))
  );
  const chainDeadlines = new Map(
    chains.map((chain) => [chain, Date.now() + getTotalBudget(chain)])
  );
  const fallbackDeadline = Date.now() + getTotalBudget("eip155:56");
  const positions = await mapByChainWithConcurrency(
    holdings,
    (holding) => safeNormalizeHoldingChain(holding.chain),
    getVaultConcurrency,
    async (h) => {
      let chain = safeNormalizeHoldingChain(h.chain);
      const chainDeadline = chainDeadlines.get(chain) ?? fallbackDeadline;
      if (Date.now() > chainDeadline) {
        return mapVaultErrorPosition(h, chain, "skipped_onchain_due_to_time_budget");
      }
      try {
        chain = normalizeHoldingChain(h.chain);
        const chainId = getChainId(chain);
        const vaultAddress = toAddress(h.address);
        const walletAddress = toAddress(userAddress);
        const vaultInfo = await withRpcGuard(
          () => sdk.getVaultInfo(chainId, vaultAddress),
          chain,
          "getVaultInfo"
        );
        const userData = await withRpcGuard(
          () => sdk.getVaultUserData(chainId, vaultAddress, walletAddress, vaultInfo),
          chain,
          "getVaultUserData"
        );
        const mapped = mapVaultUserPosition(userData);
        const depositedUsd = userData.locked.mul(Decimal2.parse(h.assetPrice || 0)).toFixed(8);
        return {
          kind: "vault",
          vaultAddress: h.address,
          vaultName: h.name,
          curator: h.curator,
          apy: h.apy,
          emissionApy: h.emissionApy,
          chain,
          assetSymbol: vaultInfo.assetInfo.symbol,
          assetPrice: h.assetPrice,
          walletBalance: mapped.walletBalance,
          deposited: mapped.assets,
          depositedUsd,
          shares: mapped.shares,
          hasPosition: mapped.hasPosition
        };
      } catch (err) {
        const message = err.message || String(err);
        return mapVaultErrorPosition(h, chain, message);
      }
    }
  );
  return sortByNumericDesc(positions, (item) => item.depositedUsd);
}

// src/api/market.ts
async function fetchMarkets(query = {}) {
  const {
    chain = "eip155:56",
    page = 1,
    pageSize = 100,
    sort = "liquidity",
    order = "desc",
    zone,
    keyword,
    loans,
    collaterals,
    termType,
    smartLendingChecked = true
  } = query;
  const sdk = getSDK();
  const apiChain = toApiChainFilter(chain, sdk);
  const data = await sdk.getMarketList({
    chain: apiChain,
    page,
    pageSize,
    sort,
    order,
    zone,
    keyword,
    loans,
    collaterals,
    termType,
    smartLendingChecked
  });
  return data.list || [];
}
async function fetchMarketPositions(userAddress) {
  const sdk = getSDK();
  const data = await sdk.getHoldings({
    userAddress: toAddress(userAddress),
    type: "market"
  });
  const holdings = data.objs || [];
  const chains = Array.from(
    new Set(holdings.map((holding) => safeNormalizeHoldingChain(holding.chain)))
  );
  const chainDeadlines = new Map(
    chains.map((chain) => [chain, Date.now() + getTotalBudget(chain)])
  );
  const fallbackDeadline = Date.now() + getTotalBudget("eip155:56");
  const markets = await mapByChainWithConcurrency(
    holdings,
    (holding) => safeNormalizeHoldingChain(holding.chain),
    getMarketConcurrency,
    async (h) => {
      let chain = safeNormalizeHoldingChain(h.chain);
      const isSmartLending = h.zone === 3;
      const isFixedTerm = h.termType === 1;
      const isActionable = !isSmartLending && !isFixedTerm;
      const chainDeadline = chainDeadlines.get(chain) ?? fallbackDeadline;
      if (Date.now() > chainDeadline) {
        return mapMarketErrorPosition(h, chain, "skipped_onchain_due_to_time_budget");
      }
      try {
        chain = normalizeHoldingChain(h.chain);
        const chainId = getChainId(chain);
        const marketId = toAddress(h.marketId);
        const walletAddress = toAddress(userAddress);
        const userData = await withRpcGuard(
          () => sdk.getMarketUserData(chainId, marketId, walletAddress),
          chain,
          "getMarketUserData"
        );
        const mapped = mapMarketUserPosition(userData, {
          collateralPrice: h.collateralPrice,
          loanPrice: h.loanPrice
        });
        return {
          kind: "market",
          marketId: h.marketId,
          chain,
          zone: h.zone,
          termType: h.termType,
          isSmartLending,
          isFixedTerm,
          isActionable,
          broker: h.broker || void 0,
          collateralSymbol: h.collateralSymbol,
          collateralAddress: h.collateralToken,
          collateralPrice: h.collateralPrice,
          loanSymbol: h.loanSymbol,
          loanAddress: h.loanToken,
          loanPrice: h.loanPrice,
          supplyApy: h.supplyApy,
          borrowRate: mapped.borrowRate,
          collateral: mapped.collateral,
          collateralUsd: mapped.collateralUsd,
          borrowed: mapped.borrowed,
          borrowedUsd: mapped.borrowedUsd,
          ltv: mapped.ltv,
          lltv: mapped.lltv,
          health: mapped.health,
          liquidationPriceRate: mapped.liquidationPriceRate,
          walletCollateralBalance: mapped.walletCollateralBalance,
          walletLoanBalance: mapped.walletLoanBalance,
          isWhitelisted: mapped.isWhitelisted
        };
      } catch (err) {
        const message = err.message || String(err);
        return mapMarketErrorPosition(h, chain, message);
      }
    }
  );
  return sortByNumericDesc(markets, (item) => item.borrowedUsd);
}

// src/api/user.ts
async function fetchUserPositions(userAddress) {
  const [vaults, markets] = await Promise.all([
    fetchVaultPositions(userAddress),
    fetchMarketPositions(userAddress)
  ]);
  return {
    vaults,
    markets
  };
}

// src/presenters/lending.ts
function formatVaultDisplay(vault, index) {
  const prefix = index !== void 0 ? `[${index}] ` : "";
  const tvl = Number.parseFloat(vault.depositsUsd).toLocaleString("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0
  });
  const apy = (Number.parseFloat(vault.apy) * 100).toFixed(2);
  return `${prefix}${vault.name} (${vault.assetSymbol}) - TVL: ${tvl}, APY: ${apy}%`;
}

// src/commands/vaults.ts
async function cmdVaults(args) {
  const chain = args.chain || "eip155:56";
  if (!isSupportedChain(chain, SUPPORTED_CHAINS)) {
    printJson({
      status: "error",
      reason: `Unsupported chain: ${chain}. Supported: ${SUPPORTED_CHAINS.join(", ")}`
    });
    process.exit(1);
  }
  if (args.page !== void 0 && !isPositiveInteger(args.page)) {
    printJson({
      status: "error",
      reason: "--page must be a positive integer"
    });
    process.exit(1);
  }
  if (args.pageSize !== void 0 && !isPositiveInteger(args.pageSize)) {
    printJson({
      status: "error",
      reason: "--page-size must be a positive integer"
    });
    process.exit(1);
  }
  if (args.order && !isValidOrder(args.order)) {
    printJson({
      status: "error",
      reason: "--order must be asc or desc"
    });
    process.exit(1);
  }
  try {
    const vaults = await fetchVaults({
      chain,
      page: args.page,
      pageSize: args.pageSize,
      sort: args.sort,
      order: args.order,
      zone: args.zone,
      keyword: args.keyword,
      assets: args.assets,
      curators: args.curators
    });
    setLastFilters({
      vaults: {
        chain,
        page: args.page || 1,
        pageSize: args.pageSize || 100,
        sort: args.sort,
        order: args.order,
        zone: args.zone,
        keyword: args.keyword,
        assets: args.assets,
        curators: args.curators,
        at: (/* @__PURE__ */ new Date()).toISOString()
      }
    });
    if (vaults.length === 0) {
      printJson({
        status: "success",
        chain,
        vaults: [],
        message: "No vaults found"
      });
      return;
    }
    printJson({
      status: "success",
      chain,
      count: vaults.length,
      filters: {
        page: args.page || 1,
        pageSize: args.pageSize || 100,
        sort: args.sort,
        order: args.order,
        zone: args.zone,
        keyword: args.keyword,
        assets: args.assets,
        curators: args.curators
      },
      vaults: vaults.map((v, i) => ({
        index: i,
        address: v.address,
        name: v.name,
        asset: v.assetSymbol,
        assetAddress: v.asset,
        decimals: v.displayDecimal,
        tvl: v.depositsUsd,
        apy: v.apy,
        curator: v.curator,
        display: formatVaultDisplay(v, i)
      }))
    });
  } catch (err) {
    printJson({
      status: "error",
      reason: "sdk_error",
      message: err.message
    });
    process.exit(1);
  }
}

// src/commands/markets.ts
var ZONE_SMART_LENDING = 3;
var TERM_TYPE_FIXED = 1;
var MARKET_OPERATION_LIMITATION_NOTE = "Smart Lending and fixed-term market operations are currently not supported in this skill. For full functionality, please use the Lista website.";
function formatUsd(value) {
  const num = Number.parseFloat(value);
  if (!Number.isFinite(num)) return "0";
  if (num >= 1e6) return `${(num / 1e6).toFixed(2)}M`;
  if (num >= 1e3) return `${(num / 1e3).toFixed(2)}K`;
  return num.toFixed(2);
}
async function cmdMarkets(args) {
  const chain = args.chain || "eip155:56";
  if (!isSupportedChain(chain, SUPPORTED_CHAINS)) {
    printJson({
      status: "error",
      reason: `Unsupported chain: ${chain}. Supported: ${SUPPORTED_CHAINS.join(", ")}`
    });
    process.exit(1);
  }
  if (args.page !== void 0 && !isPositiveInteger(args.page)) {
    printJson({
      status: "error",
      reason: "--page must be a positive integer"
    });
    process.exit(1);
  }
  if (args.pageSize !== void 0 && !isPositiveInteger(args.pageSize)) {
    printJson({
      status: "error",
      reason: "--page-size must be a positive integer"
    });
    process.exit(1);
  }
  if (args.order && !isValidOrder(args.order)) {
    printJson({
      status: "error",
      reason: "--order must be asc or desc"
    });
    process.exit(1);
  }
  try {
    const markets = await fetchMarkets({
      chain,
      page: args.page,
      pageSize: args.pageSize,
      sort: args.sort,
      order: args.order,
      zone: args.zone,
      keyword: args.keyword,
      loans: args.loans,
      collaterals: args.collaterals
    });
    const filteredMarkets = markets.filter(
      (m) => m.zone !== ZONE_SMART_LENDING && m.termType !== TERM_TYPE_FIXED
    );
    setLastFilters({
      markets: {
        chain,
        page: args.page || 1,
        pageSize: args.pageSize || 100,
        sort: args.sort,
        order: args.order,
        zone: args.zone,
        keyword: args.keyword,
        loans: args.loans,
        collaterals: args.collaterals,
        at: (/* @__PURE__ */ new Date()).toISOString()
      }
    });
    if (filteredMarkets.length === 0) {
      printJson({
        status: "success",
        chain,
        markets: [],
        message: "No markets found",
        note: MARKET_OPERATION_LIMITATION_NOTE
      });
      return;
    }
    printJson({
      status: "success",
      chain,
      count: filteredMarkets.length,
      filters: {
        page: args.page || 1,
        pageSize: args.pageSize || 100,
        sort: args.sort,
        order: args.order,
        zone: args.zone,
        keyword: args.keyword,
        loans: args.loans,
        collaterals: args.collaterals
      },
      note: MARKET_OPERATION_LIMITATION_NOTE,
      markets: filteredMarkets.map((m, i) => ({
        index: i,
        marketId: m.id,
        collateralSymbol: m.collateral,
        loanSymbol: m.loan,
        zone: m.zone,
        termType: m.termType,
        lltv: m.lltv,
        supplyApy: m.supplyApy,
        borrowRate: m.rate,
        liquidity: m.liquidity,
        liquidityUsd: m.liquidityUsd,
        vaults: m.vaults?.map((v) => v.name).join(", "),
        display: `[${i}] ${m.collateral}/${m.loan} - LLTV: ${(Number.parseFloat(m.lltv) * 100).toFixed(1)}%, Liquidity: $${formatUsd(m.liquidityUsd)}`
      }))
    });
  } catch (err) {
    printJson({
      status: "error",
      reason: "sdk_error",
      message: err.message
    });
    process.exit(1);
  }
}

// src/commands/holdings.ts
async function cmdHoldings(args) {
  const ctx = loadContext();
  const address = args.address || ctx.userAddress;
  const scope = args.scope || "all";
  if (!address) {
    printJson({
      status: "error",
      reason: "--address required (or select a wallet first)"
    });
    process.exit(1);
  }
  if (!isValidAddress(address)) {
    printJson({
      status: "error",
      reason: `Invalid address: ${address}`
    });
    process.exit(1);
  }
  if (!["all", "vault", "market", "selected"].includes(scope)) {
    printJson({
      status: "error",
      reason: "--scope must be all, vault, market, or selected"
    });
    process.exit(1);
  }
  try {
    let vaults = [];
    let markets = [];
    if (scope === "all") {
      const data = await fetchUserPositions(address);
      vaults = data.vaults;
      markets = data.markets;
    } else if (scope === "vault") {
      vaults = await fetchVaultPositions(address);
    } else if (scope === "market") {
      markets = await fetchMarketPositions(address);
    } else {
      if (!ctx.selectedVault && !ctx.selectedMarket) {
        printJson({
          status: "error",
          reason: "No selected position. Use select first or query --scope all"
        });
        process.exit(1);
      }
      const [vaultData, marketData] = await Promise.all([
        ctx.selectedVault ? fetchVaultPositions(address) : Promise.resolve([]),
        ctx.selectedMarket ? fetchMarketPositions(address) : Promise.resolve([])
      ]);
      if (ctx.selectedVault) {
        vaults = vaultData.filter(
          (item) => item.vaultAddress.toLowerCase() === ctx.selectedVault.address.toLowerCase() && item.chain === ctx.selectedVault.chain
        );
        if (vaults.length === 0 && ctx.userPosition && ctx.userAddress && ctx.userAddress.toLowerCase() === address.toLowerCase()) {
          vaults = [
            {
              kind: "vault",
              vaultAddress: ctx.selectedVault.address,
              vaultName: ctx.selectedVault.name,
              curator: "N/A",
              apy: "0",
              chain: ctx.selectedVault.chain,
              assetSymbol: ctx.selectedVault.asset.symbol,
              assetPrice: "0",
              walletBalance: "0",
              deposited: ctx.userPosition.assets,
              depositedUsd: ctx.userPosition.assetsUsd || "0",
              shares: ctx.userPosition.shares,
              hasPosition: Number.parseFloat(ctx.userPosition.assets) > 0
            }
          ];
        }
      }
      if (ctx.selectedMarket) {
        markets = marketData.filter(
          (item) => item.marketId.toLowerCase() === ctx.selectedMarket.marketId.toLowerCase() && item.chain === ctx.selectedMarket.chain
        );
      }
    }
    setLastFilters({
      holdings: {
        scope,
        address,
        at: (/* @__PURE__ */ new Date()).toISOString()
      }
    });
    const count = vaults.length + markets.length;
    const diagnostics = {
      vaultErrors: vaults.filter((item) => Boolean(item.error)).length,
      marketErrors: markets.filter((item) => Boolean(item.error)).length
    };
    if (count === 0) {
      printJson({
        status: "success",
        address,
        scope,
        counts: {
          vaults: 0,
          markets: 0,
          total: 0
        },
        diagnostics,
        vaults: [],
        markets: [],
        message: "No positions found"
      });
      process.exit(0);
    }
    printJson({
      status: "success",
      address,
      scope,
      counts: {
        vaults: vaults.length,
        markets: markets.length,
        total: count
      },
      diagnostics,
      vaults,
      markets
    });
    process.exit(0);
  } catch (err) {
    printJson({
      status: "error",
      reason: "sdk_error",
      message: err.message
    });
    process.exit(1);
  }
}

// src/commands/select/market.ts
var ZONE_SMART_LENDING2 = 3;
var TERM_TYPE_FIXED2 = 1;
async function runSelectMarket(args) {
  if (!args.walletTopic) {
    return { exitCode: 1, payload: { status: "error", reason: "--wallet-topic required" } };
  }
  if (!args.walletAddress) {
    return {
      exitCode: 1,
      payload: { status: "error", reason: "--wallet-address required" }
    };
  }
  if (!args.market) {
    return {
      exitCode: 1,
      payload: { status: "error", reason: "--market required" }
    };
  }
  const chain = args.chain || "eip155:56";
  if (!isSupportedChain(chain, SUPPORTED_CHAINS)) {
    return {
      exitCode: 1,
      payload: {
        status: "error",
        reason: `Unsupported chain: ${chain}. Supported: ${SUPPORTED_CHAINS.join(", ")}`
      }
    };
  }
  if (!isValidMarketId(args.market)) {
    return {
      exitCode: 1,
      payload: {
        status: "error",
        reason: `Invalid market ID: ${args.market}`
      }
    };
  }
  if (!isValidAddress(args.walletAddress)) {
    return {
      exitCode: 1,
      payload: {
        status: "error",
        reason: `Invalid wallet address: ${args.walletAddress}`
      }
    };
  }
  const marketId = args.market;
  const walletAddress = args.walletAddress;
  const chainId = getChainId(chain);
  try {
    const sdk = getSDK();
    const marketInfo = await sdk.getMarketInfo(chainId, marketId);
    const marketZone = marketInfo.zone;
    const marketTermType = marketInfo.termType;
    if (marketZone === ZONE_SMART_LENDING2) {
      return {
        exitCode: 1,
        payload: {
          status: "error",
          reason: "unsupported_market_type",
          message: "SmartLending markets are not supported. Use regular markets only."
        }
      };
    }
    if (marketTermType === TERM_TYPE_FIXED2) {
      return {
        exitCode: 1,
        payload: {
          status: "error",
          reason: "unsupported_market_type",
          message: "Fixed-term markets are not supported. Use regular markets only."
        }
      };
    }
    const userData = await sdk.getMarketUserData(chainId, marketId, walletAddress);
    const selectedMarket = {
      marketId,
      chain,
      collateralSymbol: userData.collateralInfo.symbol,
      loanSymbol: userData.loanInfo.symbol,
      zone: marketZone,
      termType: marketTermType
    };
    const mappedPosition = mapMarketUserPosition(userData, {
      collateralPrice: 0,
      loanPrice: 0
    });
    setSelectedMarket(selectedMarket, walletAddress, args.walletTopic);
    return {
      exitCode: 0,
      payload: {
        status: "success",
        action: "selected",
        market: selectedMarket,
        userAddress: walletAddress,
        position: {
          collateral: mappedPosition.collateral,
          borrowed: mappedPosition.borrowed,
          ltv: mappedPosition.ltv,
          lltv: mappedPosition.lltv,
          health: mappedPosition.health,
          loanable: userData.loanable?.toFixed(8) || "0",
          withdrawable: userData.withdrawable?.toFixed(8) || "0",
          walletCollateralBalance: mappedPosition.walletCollateralBalance,
          walletLoanBalance: mappedPosition.walletLoanBalance,
          hasPosition: mappedPosition.hasPosition
        },
        message: mappedPosition.hasPosition ? `Selected ${selectedMarket.collateralSymbol}/${selectedMarket.loanSymbol} market. Collateral: ${mappedPosition.collateral}, Borrowed: ${mappedPosition.borrowed}` : `Selected ${selectedMarket.collateralSymbol}/${selectedMarket.loanSymbol} market. No existing position.`
      }
    };
  } catch (err) {
    const message = err.message || String(err);
    if (message.includes("market not found") || message.includes("invalid")) {
      return {
        exitCode: 1,
        payload: {
          status: "error",
          reason: "invalid_market",
          message: `Market ${marketId} not found or invalid on ${chain}`
        }
      };
    }
    return {
      exitCode: 1,
      payload: {
        status: "error",
        reason: "sdk_error",
        message
      }
    };
  }
}

// src/commands/select/show.ts
function buildSelectShowPayload() {
  const ctx = loadContext();
  if (!ctx.selectedVault && !ctx.selectedMarket) {
    return {
      status: "success",
      selected: null,
      selectedMarket: null,
      message: "No position selected. Use 'select --vault <address>' or 'select --market <id>'."
    };
  }
  const position = ctx.selectedVault && ctx.userPosition ? {
    assets: ctx.userPosition.assets,
    balance: ctx.userPosition.assets,
    assetsUsd: ctx.userPosition.assetsUsd
  } : null;
  return {
    status: "success",
    selected: ctx.selectedVault,
    selectedMarket: ctx.selectedMarket,
    userAddress: ctx.userAddress,
    walletTopic: ctx.walletTopic,
    position,
    lastFilters: ctx.lastFilters,
    lastUpdated: ctx.lastUpdated
  };
}
function buildSelectClearedPayload() {
  return {
    status: "success",
    action: "cleared",
    message: "Selection cleared"
  };
}

// src/commands/select/vault.ts
async function runSelectVault(args) {
  if (!args.walletTopic) {
    return { exitCode: 1, payload: { status: "error", reason: "--wallet-topic required" } };
  }
  if (!args.walletAddress) {
    return {
      exitCode: 1,
      payload: { status: "error", reason: "--wallet-address required" }
    };
  }
  if (!args.vault) {
    return {
      exitCode: 1,
      payload: { status: "error", reason: "--vault required" }
    };
  }
  const chain = args.chain || "eip155:56";
  if (!isSupportedChain(chain, SUPPORTED_CHAINS)) {
    return {
      exitCode: 1,
      payload: {
        status: "error",
        reason: `Unsupported chain: ${chain}. Supported: ${SUPPORTED_CHAINS.join(", ")}`
      }
    };
  }
  if (!isValidAddress(args.vault)) {
    return {
      exitCode: 1,
      payload: {
        status: "error",
        reason: `Invalid vault address: ${args.vault}`
      }
    };
  }
  if (!isValidAddress(args.walletAddress)) {
    return {
      exitCode: 1,
      payload: {
        status: "error",
        reason: `Invalid wallet address: ${args.walletAddress}`
      }
    };
  }
  const vaultAddress = args.vault;
  const walletAddress = args.walletAddress;
  const chainId = getChainId(chain);
  try {
    const sdk = getSDK();
    const vaultInfo = await sdk.getVaultInfo(chainId, vaultAddress);
    const userData = await sdk.getVaultUserData(
      chainId,
      vaultAddress,
      walletAddress,
      vaultInfo
    );
    const assetInfo = vaultInfo.assetInfo;
    const selectedVault = {
      address: vaultAddress,
      name: `${assetInfo.symbol} Vault`,
      asset: {
        symbol: assetInfo.symbol,
        address: assetInfo.address,
        decimals: assetInfo.decimals
      },
      chain
    };
    const mappedPosition = mapVaultUserPosition(userData);
    setSelectedVault(
      selectedVault,
      walletAddress,
      args.walletTopic,
      mappedPosition.position
    );
    return {
      exitCode: 0,
      payload: {
        status: "success",
        action: "selected",
        vault: selectedVault,
        userAddress: walletAddress,
        balance: mappedPosition.walletBalance,
        vaultBalance: mappedPosition.position.assets,
        position: {
          assets: mappedPosition.position.assets,
          balance: mappedPosition.position.assets,
          walletBalance: mappedPosition.walletBalance,
          assetSymbol: assetInfo.symbol,
          hasPosition: mappedPosition.hasPosition
        },
        message: mappedPosition.hasPosition ? `Selected ${selectedVault.name}. You have ${mappedPosition.position.assets} ${assetInfo.symbol} deposited. Wallet balance: ${mappedPosition.walletBalance} ${assetInfo.symbol}.` : `Selected ${selectedVault.name}. No existing position.`
      }
    };
  } catch (err) {
    const message = err.message || String(err);
    if (message.includes("vault not found") || message.includes("invalid")) {
      return {
        exitCode: 1,
        payload: {
          status: "error",
          reason: "invalid_vault",
          message: `Vault ${vaultAddress} not found or invalid on ${chain}`
        }
      };
    }
    return {
      exitCode: 1,
      payload: {
        status: "error",
        reason: "sdk_error",
        message
      }
    };
  }
}

// src/commands/select.ts
async function cmdSelect(args) {
  if (args.clear) {
    clearContext();
    printJson(buildSelectClearedPayload());
    exitWithCode(0);
  }
  if (args.show) {
    printJson(buildSelectShowPayload());
    exitWithCode(0);
  }
  if (!args.vault && !args.market) {
    printJson({
      status: "error",
      reason: "--vault or --market required (or use --show to see current selection)"
    });
    exitWithCode(1);
  }
  if (args.vault && args.market) {
    printJson({
      status: "error",
      reason: "Cannot select both --vault and --market at the same time"
    });
    exitWithCode(1);
  }
  const result = args.market ? await runSelectMarket(args) : await runSelectVault(args);
  printJson(result.payload);
  exitWithCode(result.exitCode);
}

// src/commands/shared/market.ts
function buildMarketPositionPayload(mappedPosition, extras = {}) {
  return {
    collateral: mappedPosition.collateral,
    borrowed: mappedPosition.borrowed,
    ltv: mappedPosition.ltv,
    lltv: mappedPosition.lltv,
    health: mappedPosition.health,
    walletCollateralBalance: mappedPosition.walletCollateralBalance,
    walletLoanBalance: mappedPosition.walletLoanBalance,
    ...extras
  };
}
function buildRepayHint(userData) {
  if (userData.withdrawable?.gt(0) && userData.borrowed.isZero()) {
    return `Debt fully repaid. You can withdraw up to ${userData.withdrawable.toFixed(4)} ${userData.collateralInfo.symbol} collateral.`;
  }
  return void 0;
}
function getRepayNoDebtError() {
  return {
    status: "error",
    reason: "no_debt",
    message: "No debt to repay in this market"
  };
}
function getWithdrawNoCollateralError() {
  return {
    status: "error",
    reason: "no_collateral",
    message: "No collateral to withdraw from this market"
  };
}
function getWithdrawAllHasDebtError(userData) {
  return {
    status: "error",
    reason: "has_debt",
    message: "Cannot withdraw all collateral while you have outstanding debt. Repay debt first or use --amount.",
    debt: userData.borrowed.toFixed(8),
    withdrawable: userData.withdrawable.toFixed(8)
  };
}
function getExceedsWithdrawableError(requestedAmount, userData, collateralSymbol) {
  return {
    status: "error",
    reason: "exceeds_withdrawable",
    message: `Cannot withdraw ${requestedAmount} ${collateralSymbol}. Max withdrawable: ${userData.withdrawable.toFixed(4)} ${collateralSymbol}`,
    maxWithdrawable: userData.withdrawable.toFixed(8),
    hint: "Repay some debt to increase withdrawable amount"
  };
}

// src/commands/supply.ts
async function cmdSupply(args) {
  const ctx = loadContext();
  let operationContext;
  try {
    const amount = requireAmount(args.amount);
    const { marketId, chain, walletAddress, walletTopic } = resolveMarketContext(
      args,
      ctx,
      { supportedChains: SUPPORTED_CHAINS }
    );
    const chainId = getChainId(chain);
    const sdk = getSDK();
    const marketInfo = await sdk.getWriteConfig(chainId, marketId);
    const collateralInfo = marketInfo.collateralInfo;
    const decimals = collateralInfo.decimals;
    const assets = parsePositiveUnits(amount, decimals, "amount");
    operationContext = { marketId, chain, amount };
    const steps = ensureStepsGenerated(
      await sdk.buildSupplyParams({
        chainId,
        marketId,
        assets,
        walletAddress,
        marketInfo
      })
    );
    const results = await executeSteps(steps, {
      topic: walletTopic,
      chain
    });
    const lastResult = results[results.length - 1];
    if (lastResult.status === "pending") {
      printJson(buildPendingExecutionOutput(lastResult, results, steps.length));
      exitWithCode(0);
    }
    if (lastResult.status === "sent") {
      const userData = await sdk.getMarketUserData(chainId, marketId, walletAddress);
      const mappedPosition = mapMarketUserPosition(userData, {
        collateralPrice: 0,
        loanPrice: 0
      });
      printJson({
        status: "success",
        market: marketId,
        chain,
        collateral: collateralInfo.symbol,
        supplied: amount,
        steps: results.length,
        txHash: lastResult.txHash,
        explorer: lastResult.explorer,
        position: buildMarketPositionPayload(mappedPosition, {
          loanable: userData.loanable?.toFixed(8) || "0"
        }),
        hint: userData.loanable?.gt(0) ? `You can now borrow up to ${userData.loanable.toFixed(4)} ${userData.loanInfo.symbol}` : void 0
      });
      exitWithCode(0);
    }
    printJson(buildExecutionFailureOutput(results, steps.length));
    exitWithCode(1);
  } catch (err) {
    if (err instanceof InputValidationError) {
      printJson({
        status: "error",
        reason: err.message
      });
      exitWithCode(1);
    }
    const message = err.message || String(err);
    printJson(
      buildSdkErrorOutput(message, {
        targetType: "market" /* Market */,
        targetId: operationContext?.marketId
      })
    );
    exitWithCode(1);
  }
}

// src/commands/borrow/execute.ts
import { Decimal as Decimal3 } from "@lista-dao/moolah-sdk-core";
async function executeBorrowTransaction(runtime, amount) {
  const {
    marketId,
    chain,
    chainId,
    walletAddress,
    walletTopic,
    marketInfo,
    userData
  } = runtime;
  const loanInfo = marketInfo.loanInfo;
  const assets = parsePositiveUnits(amount, loanInfo.decimals, "amount");
  const requestedAmount = new Decimal3(assets, loanInfo.decimals);
  if (userData.loanable.lt(requestedAmount)) {
    return {
      exitCode: 1,
      payload: {
        status: "error",
        reason: "insufficient_collateral",
        message: `Cannot borrow ${amount} ${loanInfo.symbol}. Max borrowable: ${userData.loanable.toFixed(4)} ${loanInfo.symbol}`,
        maxBorrowable: userData.loanable.toFixed(8),
        hint: "Supply more collateral or reduce borrow amount"
      }
    };
  }
  const steps = ensureStepsGenerated(
    await runtime.sdk.buildBorrowParams({
      chainId,
      marketId,
      assets,
      walletAddress,
      marketInfo
    })
  );
  const results = await executeSteps(steps, {
    topic: walletTopic,
    chain
  });
  const lastResult = results[results.length - 1];
  if (lastResult.status === "pending") {
    return {
      exitCode: 0,
      payload: buildPendingExecutionOutput(lastResult, results, steps.length)
    };
  }
  if (lastResult.status === "sent") {
    const newUserData = await runtime.sdk.getMarketUserData(
      chainId,
      marketId,
      walletAddress
    );
    const mappedPosition = mapMarketUserPosition(newUserData, {
      collateralPrice: 0,
      loanPrice: 0
    });
    return {
      exitCode: 0,
      payload: {
        status: "success",
        market: marketId,
        chain,
        loan: loanInfo.symbol,
        borrowed: amount,
        txHash: lastResult.txHash,
        explorer: lastResult.explorer,
        position: buildMarketPositionPayload(mappedPosition, {
          loanable: newUserData.loanable?.toFixed(8) || "0"
        }),
        warning: parseFloat(mappedPosition.health) < 1.2 ? "Health factor is low. Consider repaying some debt to avoid liquidation." : void 0
      }
    };
  }
  return {
    exitCode: 1,
    payload: buildExecutionFailureOutput(results, steps.length)
  };
}

// src/commands/borrow/simulate.ts
async function buildBorrowSimulationPayload(args, runtime) {
  const { marketId, chain, marketInfo, marketExtraInfo, userData } = runtime;
  const currentLoanable = userData.loanable;
  const currentSafeBorrow = currentLoanable.mul(0.95).roundDown(userData.decimals.l);
  let afterSupplyLoanable = currentLoanable;
  let afterSupplyAmount;
  if (args.simulateSupply) {
    const parsedSupplyAmount = parsePositiveUnits(
      args.simulateSupply,
      userData.decimals.c,
      "simulate-supply"
    );
    afterSupplyAmount = args.simulateSupply;
    const simulated = await runtime.sdk.simulateBorrowPosition({
      chainId: runtime.chainId,
      marketId,
      walletAddress: runtime.walletAddress,
      supplyAssets: parsedSupplyAmount,
      marketExtraInfo,
      userData
    });
    afterSupplyLoanable = simulated.simulation.baseLoanable;
  }
  const safeAfterSupplyBorrow = afterSupplyLoanable.mul(0.95).roundDown(userData.decimals.l);
  const mappedPosition = mapMarketUserPosition(userData, {
    collateralPrice: 0,
    loanPrice: 0
  });
  return {
    status: "success",
    action: "simulate",
    market: marketId,
    chain,
    collateral: {
      symbol: marketInfo.collateralInfo.symbol,
      deposited: mappedPosition.collateral,
      walletBalance: mappedPosition.walletCollateralBalance
    },
    loan: {
      symbol: marketInfo.loanInfo.symbol,
      borrowed: mappedPosition.borrowed,
      walletBalance: mappedPosition.walletLoanBalance
    },
    position: {
      ltv: mappedPosition.ltv,
      lltv: mappedPosition.lltv,
      health: mappedPosition.health
    },
    borrowable: {
      max: currentLoanable.toFixed(8),
      safe: currentSafeBorrow.toFixed(8),
      afterSupply: afterSupplyAmount ? {
        supplyAmount: afterSupplyAmount,
        maxBorrow: afterSupplyLoanable.toFixed(8),
        safeBorrow: safeAfterSupplyBorrow.toFixed(8)
      } : void 0
    },
    hint: afterSupplyLoanable.gt(0) ? `You can safely borrow up to ${safeAfterSupplyBorrow.toFixed(4)} ${marketInfo.loanInfo.symbol} (95% of max: ${afterSupplyLoanable.toFixed(4)})` : "No borrowing capacity. Supply collateral first."
  };
}

// src/commands/borrow.ts
async function cmdBorrow(args) {
  const ctx = loadContext();
  let marketId;
  try {
    if (!args.simulate && !args.amount) {
      throw new InputValidationError("--amount or --simulate required");
    }
    const {
      marketId: resolvedMarketId,
      chain,
      walletAddress,
      walletTopic
    } = resolveMarketContext(args, ctx, {
      supportedChains: SUPPORTED_CHAINS,
      requireWalletTopic: !args.simulate
    });
    marketId = resolvedMarketId;
    const chainId = getChainId(chain);
    const runtime = {
      sdk: getSDK(),
      marketId: resolvedMarketId,
      chain,
      chainId,
      walletAddress,
      walletTopic,
      ...await getMarketRuntimeData(chainId, resolvedMarketId, walletAddress)
    };
    if (args.simulate) {
      printJson(await buildBorrowSimulationPayload(args, runtime));
      exitWithCode(0);
    }
    const result = await executeBorrowTransaction(runtime, args.amount);
    printJson(result.payload);
    exitWithCode(result.exitCode);
  } catch (err) {
    if (err instanceof InputValidationError) {
      printJson({
        status: "error",
        reason: err.message
      });
      exitWithCode(1);
    }
    const message = err.message || String(err);
    printJson(
      buildSdkErrorOutput(message, {
        targetType: "market" /* Market */,
        targetId: marketId,
        insufficientReason: "insufficient_collateral",
        insufficientMessage: "Borrow amount exceeds available collateral capacity"
      })
    );
    exitWithCode(1);
  }
}

// src/commands/repay/execute.ts
async function executeRepayTransaction(runtime, args) {
  const { marketId, chain, chainId, walletAddress, walletTopic, marketInfo, userData } = runtime;
  let assets;
  if (args.amount) {
    assets = parsePositiveUnits(args.amount, marketInfo.loanInfo.decimals, "amount");
  }
  const steps = ensureStepsGenerated(
    await runtime.sdk.buildRepayParams({
      chainId,
      marketId,
      assets,
      repayAll: args.repayAll,
      walletAddress,
      marketInfo,
      userData
    })
  );
  const results = await executeSteps(steps, {
    topic: walletTopic,
    chain
  });
  const lastResult = results[results.length - 1];
  if (lastResult.status === "pending") {
    return {
      exitCode: 0,
      payload: buildPendingExecutionOutput(lastResult, results, steps.length)
    };
  }
  if (lastResult.status === "sent") {
    const newUserData = await runtime.sdk.getMarketUserData(
      chainId,
      marketId,
      walletAddress
    );
    const mappedPosition = mapMarketUserPosition(newUserData, {
      collateralPrice: 0,
      loanPrice: 0
    });
    return {
      exitCode: 0,
      payload: {
        status: "success",
        market: marketId,
        chain,
        loan: marketInfo.loanInfo.symbol,
        repaid: args.amount || "all",
        txHash: lastResult.txHash,
        explorer: lastResult.explorer,
        position: buildMarketPositionPayload(mappedPosition, {
          withdrawable: newUserData.withdrawable?.toFixed(8) || "0",
          remainingDebt: mappedPosition.borrowed !== "0"
        }),
        hint: buildRepayHint(newUserData)
      }
    };
  }
  return {
    exitCode: 1,
    payload: buildExecutionFailureOutput(results, steps.length)
  };
}

// src/commands/repay/simulate.ts
import { Decimal as Decimal4 } from "@lista-dao/moolah-sdk-core";
async function buildRepaySimulationPayload(args, runtime) {
  const { marketId, chain, marketExtraInfo, userData, marketInfo } = runtime;
  const loanSymbol = marketInfo.loanInfo.symbol;
  let repayAssets = 0n;
  let estimatedRepay = "0";
  if (args.repayAll) {
    repayAssets = userData.borrowed.roundDown(userData.decimals.l).numerator;
    estimatedRepay = userData.borrowed.toFixed(8);
  } else if (args.amount) {
    const parsedAmount = parsePositiveUnits(args.amount, userData.decimals.l, "amount");
    if (userData.borrowed.lt(new Decimal4(parsedAmount, userData.decimals.l))) {
      throw new InputValidationError(
        `Repay amount exceeds current debt (${userData.borrowed.toFixed(8)} ${loanSymbol})`
      );
    }
    repayAssets = parsedAmount;
    estimatedRepay = args.amount;
  }
  const simulated = await runtime.sdk.simulateRepayPosition({
    chainId: runtime.chainId,
    marketId,
    walletAddress: runtime.walletAddress,
    repayAssets,
    repayAll: Boolean(args.repayAll),
    marketExtraInfo,
    userData
  });
  const simulation = simulated.simulation;
  const mappedPosition = mapMarketUserPosition(userData, {
    collateralPrice: 0,
    loanPrice: 0
  });
  return {
    status: "success",
    action: "simulate",
    market: marketId,
    chain,
    loan: loanSymbol,
    repay: {
      amount: args.repayAll ? "all" : args.amount,
      repayAll: Boolean(args.repayAll),
      currentDebt: userData.borrowed.toFixed(8),
      estimatedRepay
    },
    current: {
      borrowed: mappedPosition.borrowed,
      ltv: mappedPosition.ltv,
      withdrawable: userData.withdrawable.toFixed(8),
      health: mappedPosition.health
    },
    afterRepay: {
      borrowed: simulation.borrowed.toFixed(8),
      ltv: simulation.LTV.toFixed(8),
      withdrawable: simulation.withdrawable.toFixed(8)
    },
    hint: simulation.borrowed.isZero() ? "Repay will fully clear debt." : `Estimated remaining debt: ${simulation.borrowed.toFixed(8)} ${loanSymbol}`
  };
}

// src/commands/repay.ts
async function cmdRepay(args) {
  const ctx = loadContext();
  let marketId;
  try {
    requireAmountOrAll(args.amount, args.repayAll, "--repay-all");
    const {
      marketId: resolvedMarketId,
      chain,
      walletAddress,
      walletTopic
    } = resolveMarketContext(args, ctx, {
      supportedChains: SUPPORTED_CHAINS,
      requireWalletTopic: !args.simulate
    });
    marketId = resolvedMarketId;
    const chainId = getChainId(chain);
    const runtime = {
      sdk: getSDK(),
      marketId: resolvedMarketId,
      chain,
      chainId,
      walletAddress,
      walletTopic,
      ...await getMarketRuntimeData(chainId, resolvedMarketId, walletAddress)
    };
    if (runtime.userData.borrowed.isZero()) {
      printJson(getRepayNoDebtError());
      exitWithCode(1);
    }
    if (args.simulate) {
      printJson(await buildRepaySimulationPayload(args, runtime));
      exitWithCode(0);
    }
    const result = await executeRepayTransaction(runtime, args);
    printJson(result.payload);
    exitWithCode(result.exitCode);
  } catch (err) {
    if (err instanceof InputValidationError) {
      printJson({
        status: "error",
        reason: err.message
      });
      exitWithCode(1);
    }
    const message = err.message || String(err);
    printJson(
      buildSdkErrorOutput(message, {
        targetType: "market" /* Market */,
        targetId: marketId,
        insufficientReason: "insufficient_balance",
        insufficientMessage: "Insufficient loan token balance in wallet to repay"
      })
    );
    exitWithCode(1);
  }
}

// src/commands/market-withdraw.ts
import { Decimal as Decimal5 } from "@lista-dao/moolah-sdk-core";
async function cmdMarketWithdraw(args) {
  const ctx = loadContext();
  let operationContext;
  try {
    requireAmountOrAll(args.amount, args.withdrawAll, "--withdraw-all");
    const { marketId, chain, walletAddress, walletTopic } = resolveMarketContext(
      args,
      ctx,
      { supportedChains: SUPPORTED_CHAINS }
    );
    const chainId = getChainId(chain);
    const sdk = getSDK();
    const { marketInfo, userData } = await getMarketRuntimeData(
      chainId,
      marketId,
      walletAddress
    );
    const collateralInfo = marketInfo.collateralInfo;
    if (userData.collateral.isZero()) {
      printJson(getWithdrawNoCollateralError());
      exitWithCode(1);
    }
    if (args.withdrawAll && !userData.borrowed.isZero()) {
      printJson(getWithdrawAllHasDebtError(userData));
      exitWithCode(1);
    }
    const decimals = collateralInfo.decimals;
    let assets;
    if (args.amount) {
      assets = parsePositiveUnits(args.amount, decimals, "amount");
      const requestedWithdrawAmount = new Decimal5(assets, decimals);
      if (userData.withdrawable.lt(requestedWithdrawAmount)) {
        printJson(
          getExceedsWithdrawableError(args.amount, userData, collateralInfo.symbol)
        );
        exitWithCode(1);
      }
    }
    const operationAmount = args.amount || "all";
    operationContext = {
      marketId,
      chain,
      amount: operationAmount
    };
    const steps = ensureStepsGenerated(
      await sdk.buildWithdrawParams({
        chainId,
        marketId,
        assets,
        withdrawAll: args.withdrawAll,
        walletAddress,
        marketInfo,
        userData
      })
    );
    const results = await executeSteps(steps, {
      topic: walletTopic,
      chain
    });
    const lastResult = results[results.length - 1];
    if (lastResult.status === "pending") {
      printJson(buildPendingExecutionOutput(lastResult, results, steps.length));
      exitWithCode(0);
    }
    if (lastResult.status === "sent") {
      const newUserData = await sdk.getMarketUserData(chainId, marketId, walletAddress);
      const mappedPosition = mapMarketUserPosition(newUserData, {
        collateralPrice: 0,
        loanPrice: 0
      });
      printJson({
        status: "success",
        market: marketId,
        chain,
        collateral: collateralInfo.symbol,
        withdrawn: operationAmount,
        txHash: lastResult.txHash,
        explorer: lastResult.explorer,
        position: buildMarketPositionPayload(mappedPosition, {
          withdrawable: newUserData.withdrawable?.toFixed(8) || "0",
          remainingCollateral: mappedPosition.collateral !== "0"
        })
      });
      exitWithCode(0);
    }
    printJson(buildExecutionFailureOutput(results, steps.length));
    exitWithCode(1);
  } catch (err) {
    if (err instanceof InputValidationError) {
      printJson({
        status: "error",
        reason: err.message
      });
      exitWithCode(1);
    }
    const message = err.message || String(err);
    printJson(
      buildSdkErrorOutput(message, {
        targetType: "market" /* Market */,
        targetId: operationContext?.marketId,
        insufficientReason: "exceeds_withdrawable",
        insufficientMessage: "Withdraw amount exceeds available withdrawable collateral"
      })
    );
    exitWithCode(1);
  }
}

// src/cli/run.ts
async function runCommand(command, routedArgs, meta2) {
  const { args, configArgs, vaultsArgs, marketsArgs, holdingsArgs, selectArgs } = routedArgs;
  switch (command) {
    case "config":
      await cmdConfig(configArgs);
      return;
    case "holdings":
      await cmdHoldings(holdingsArgs);
      return;
    case "select":
      await cmdSelect(selectArgs);
      return;
    case "version":
      console.log(
        JSON.stringify({
          skill: meta2.skillName,
          version: meta2.skillVersion,
          dependencies: {
            "lista-wallet-connect": meta2.walletConnectVersion
          },
          hint: "If version mismatch, run: npm install && npm run build"
        })
      );
      return;
    case "vaults":
      await cmdVaults(vaultsArgs);
      return;
    case "deposit":
      await cmdDeposit(args);
      return;
    case "withdraw":
      await cmdWithdraw(args);
      return;
    case "markets":
      await cmdMarkets(marketsArgs);
      return;
    case "supply":
      await cmdSupply(args);
      return;
    case "borrow":
      await cmdBorrow(args);
      return;
    case "repay":
      await cmdRepay(args);
      return;
    case "market-withdraw":
      await cmdMarketWithdraw(args);
      return;
    default:
      console.error(`Unknown command: ${command}`);
      console.error("Run with --help for usage information");
      process.exit(1);
  }
}

// src/cli.ts
var parsed = parseCliInput();
setupDebugLogFile("@lista-dao/lista-lending-skill", parsed.debugLogFile);
var meta = loadCliMeta();
var SKILL_VERSION = meta.skillVersion;
var SKILL_NAME = meta.skillName;
var WALLET_CONNECT_VERSION = meta.walletConnectVersion;
if (!parsed.command || parsed.help) {
  console.log(renderHelp(meta));
  process.exit(0);
}
runCommand(
  parsed.command,
  {
    args: parsed.args,
    configArgs: parsed.configArgs,
    vaultsArgs: parsed.vaultsArgs,
    marketsArgs: parsed.marketsArgs,
    holdingsArgs: parsed.holdingsArgs,
    selectArgs: parsed.selectArgs
  },
  meta
).catch((err) => {
  printErrorJson({ error: err.message });
  process.exit(1);
});
export {
  SKILL_NAME,
  SKILL_VERSION,
  WALLET_CONNECT_VERSION
};
