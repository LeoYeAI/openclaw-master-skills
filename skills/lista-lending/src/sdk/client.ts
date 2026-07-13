import { MoolahSDK, type SdkTransportConfig } from "@lista-dao/moolah-lending-sdk";
import { getRpcUrls, getChainId, getRpcConfig, SUPPORTED_CHAINS } from "../config.js";

let sdkInstance: MoolahSDK | null = null;
let sdkSignature: string | null = null;

function parseIntEnv(value: string | undefined, fallback: number): number {
  const parsed = Number.parseInt(value || "", 10);
  return Number.isFinite(parsed) ? parsed : fallback;
}

function buildRpcConfig(): Record<string, string[]> {
  const config: Record<string, string[]> = {};

  for (const chain of SUPPORTED_CHAINS) {
    const rpcUrls = getRpcUrls(chain);
    if (rpcUrls.length === 0) continue;
    config[String(getChainId(chain))] = rpcUrls;
  }

  return config;
}

function buildTransportConfigByChain(): Record<string, SdkTransportConfig> {
  const transportByChainId: Record<string, SdkTransportConfig> = {};

  for (const chain of SUPPORTED_CHAINS) {
    const rpcConfig = getRpcConfig(chain);
    transportByChainId[String(getChainId(chain))] = {
      timeout: parseIntEnv(process.env.LISTA_RPC_TIMEOUT_MS, rpcConfig.itemTimeout),
      retryCount: parseIntEnv(process.env.LISTA_RPC_RETRY_COUNT, rpcConfig.retryCount),
      retryDelay: parseIntEnv(process.env.LISTA_RPC_RETRY_DELAY_MS, rpcConfig.retryDelay),
    };
  }

  return transportByChainId;
}

function buildSdkSignature(
  rpcUrls: Record<string, string[]>,
  transportByChainId: Record<string, SdkTransportConfig>
): string {
  return JSON.stringify({ rpcUrls, transportByChainId });
}

export function getSDK(): MoolahSDK {
  const rpcUrls = buildRpcConfig();
  const transportByChainId = buildTransportConfigByChain();
  const signature = buildSdkSignature(rpcUrls, transportByChainId);

  if (!sdkInstance || sdkSignature !== signature) {
    sdkInstance = new MoolahSDK({
      rpcUrls,
      transportByChainId,
    });
    sdkSignature = signature;
  }

  return sdkInstance;
}
