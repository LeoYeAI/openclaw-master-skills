import { z } from "zod";

const MAINNET_CONFIRM_PHRASE = "I_UNDERSTAND_MAINNET_RISK" as const;

const ConfigSchema = z.object({
  // LLM provider
  LLM_PROVIDER: z.enum(["anthropic", "openai_compatible"]).default("anthropic"),
  ANTHROPIC_API_KEY: z.string().optional(),
  ANTHROPIC_MODEL: z.string().default("claude-haiku-4-5-20251001"),
  LLM_API_KEY: z.string().optional(),
  LLM_BASE_URL: z.string().url().optional(),
  LLM_MODEL: z.string().default("gpt-4o-mini"),

  // Wallet provider selection: "auto" | "coinbase" | "privy"
  WALLET_PROVIDER: z.enum(["auto", "coinbase", "privy"]).default("auto"),

  // Privy wallet (required when WALLET_PROVIDER=privy)
  PRIVY_APP_ID: z.string().optional(),
  PRIVY_APP_SECRET: z.string().optional(),
  PRIVY_WALLET_ID: z.string().optional(),

  // Coinbase AgentKit (required when WALLET_PROVIDER=coinbase)
  COINBASE_CDP_API_KEY_NAME: z.string().optional(),
  COINBASE_CDP_API_KEY_PRIVATE_KEY: z.string().optional(),
  COINBASE_WALLET_DATA: z.string().optional(),

  // Base chain
  BASE_RPC_URL: z.string().url().default("https://sepolia.base.org"),

  // Mainnet safety gate
  MAINNET_ENABLED: z.coerce.boolean().default(false),
  MAINNET_CONFIRM_TEXT: z.string().optional(),

  // Deployed contracts
  ERC8004_REGISTRY_ADDRESS: z
    .string()
    .regex(/^0x[a-fA-F0-9]{40}$/, "Must be a valid EVM address")
    .optional(),
  SAFE_ESCROW_ADDRESS: z
    .string()
    .regex(/^0x[a-fA-F0-9]{40}$/, "Must be a valid EVM address")
    .optional(),

  // x402
  X402_FACILITATOR_URL: z.string().url().default("https://x402.org/facilitator"),
  REDIS_URL: z.string().url().optional(),
  REDIS_PREFIX: z.string().default("SafeLink"),

  // Tenderly simulation
  TENDERLY_ACCESS_KEY: z.string().optional(),
  TENDERLY_PROJECT_SLUG: z.string().default("SafeLink"),
  TENDERLY_ACCOUNT_ID: z.string().optional(),

  // Block explorer
  BASESCAN_API_KEY: z.string().optional(),

  // Memory/storage
  AUTONOMYS_NETWORK: z.enum(["taurus-testnet", "mainnet"]).default("taurus-testnet"),
  AUTONOMYS_RPC_URL: z.string().url().optional(),

  // Agent identity
  AGENT_ID: z.string().optional(),
  AGENT_NAME: z.string().default("my-SafeLink"),

  // HTTP task server
  TASK_SERVER_PORT: z.coerce.number().int().min(1024).max(65535).default(3402),
  TASK_AUTH_REQUIRED: z.coerce.boolean().default(false),
  TASK_AUTH_SHARED_SECRET: z.string().optional(),
  TASK_AUTH_MAX_SKEW_SECONDS: z.coerce.number().int().min(30).max(3600).default(300),
  SIWX_REQUIRED: z.coerce.boolean().default(false),
  SIWX_VERIFIER_URL: z.string().url().optional(),

  // Runtime
  NODE_ENV: z.enum(["development", "test", "production"]).default("development"),
  LOG_LEVEL: z.enum(["error", "warn", "info", "debug"]).default("info"),
  RISK_APPROVAL_THRESHOLD: z.coerce.number().min(0).max(100).default(70),
  MIN_REPUTATION_SCORE: z.coerce.number().min(0).max(100).default(70),
  ANALYTICS_STORE_PATH: z.string().default(".safelink-analytics.json"),
});

export type Config = z.infer<typeof ConfigSchema>;

let _config: Config | undefined;

export function getConfig(): Config {
  if (_config) return _config;

  const result = ConfigSchema.safeParse(process.env);

  if (!result.success) {
    const issues = result.error.issues
      .map((i) => `  - ${i.path.join(".")}: ${i.message}`)
      .join("\n");
    throw new Error(
      `SafeLink: invalid environment configuration.\n${issues}\n\nRun \`npm run setup\` to configure your .env file.`
    );
  }

  const cfg = result.data;

  // LLM provider validation
  if (cfg.LLM_PROVIDER === "anthropic") {
    if (!cfg.ANTHROPIC_API_KEY) {
      throw new Error(
        "LLM_PROVIDER=anthropic but ANTHROPIC_API_KEY is not set.\n" +
          "Set ANTHROPIC_API_KEY or switch to LLM_PROVIDER=openai_compatible."
      );
    }
  } else {
    if (!cfg.LLM_API_KEY || !cfg.LLM_BASE_URL) {
      throw new Error(
        "LLM_PROVIDER=openai_compatible but LLM_API_KEY / LLM_BASE_URL are not set.\n" +
          "Example: LLM_BASE_URL=https://your-openclaw-gateway/v1"
      );
    }
  }

  // Wallet provider validation
  const hasCoinbase = !!(cfg.COINBASE_CDP_API_KEY_NAME && cfg.COINBASE_CDP_API_KEY_PRIVATE_KEY);
  const hasPrivy = !!(cfg.PRIVY_APP_ID && cfg.PRIVY_APP_SECRET);

  if (cfg.WALLET_PROVIDER === "coinbase" && !hasCoinbase) {
    throw new Error(
      "WALLET_PROVIDER=coinbase but COINBASE_CDP_API_KEY_NAME / COINBASE_CDP_API_KEY_PRIVATE_KEY are not set.\n" +
        "Get keys at portal.cdp.coinbase.com."
    );
  }
  if (cfg.WALLET_PROVIDER === "privy" && !hasPrivy) {
    throw new Error(
      "WALLET_PROVIDER=privy but PRIVY_APP_ID / PRIVY_APP_SECRET are not set.\n" +
        "Set from dashboard.privy.io."
    );
  }
  if (cfg.WALLET_PROVIDER === "auto" && !hasCoinbase && !hasPrivy) {
    throw new Error(
      "No wallet provider configured.\n" +
        "Set Coinbase CDP keys (recommended) or Privy credentials."
    );
  }

  // Mainnet explicit acknowledgment gate
  const isMainnet = cfg.BASE_RPC_URL.includes("mainnet");
  if (isMainnet) {
    if (!cfg.MAINNET_ENABLED) {
      throw new Error(
        "Base mainnet is selected, but MAINNET_ENABLED is not true.\n" +
          "Set MAINNET_ENABLED=true to explicitly allow mainnet operations."
      );
    }
    if (cfg.MAINNET_CONFIRM_TEXT !== MAINNET_CONFIRM_PHRASE) {
      throw new Error(
        "Base mainnet is selected, but MAINNET_CONFIRM_TEXT is missing or incorrect.\n" +
          `Set MAINNET_CONFIRM_TEXT=${MAINNET_CONFIRM_PHRASE}`
      );
    }
  }

  if (cfg.TASK_AUTH_REQUIRED) {
    if (!cfg.TASK_AUTH_SHARED_SECRET || cfg.TASK_AUTH_SHARED_SECRET.length < 32) {
      throw new Error(
        "TASK_AUTH_REQUIRED=true but TASK_AUTH_SHARED_SECRET is missing/too short.\n" +
          "Set TASK_AUTH_SHARED_SECRET to a high-entropy secret (>= 32 chars)."
      );
    }
  }

  if (cfg.SIWX_REQUIRED && !cfg.SIWX_VERIFIER_URL) {
    throw new Error(
      "SIWX_REQUIRED=true but SIWX_VERIFIER_URL is not set.\n" +
        "Set SIWX_VERIFIER_URL to your SIWx verifier endpoint."
    );
  }

  _config = cfg;
  return _config;
}

export function resetConfig(): void {
  _config = undefined;
}

export { MAINNET_CONFIRM_PHRASE };


