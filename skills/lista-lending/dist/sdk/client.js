import { MoolahSDK } from "@lista-dao/moolah-lending-sdk";
import { getRpcUrls, getChainId, getRpcConfig, SUPPORTED_CHAINS } from "../config.js";
let sdkInstance = null;
let sdkSignature = null;
function parseIntEnv(value, fallback) {
    const parsed = Number.parseInt(value || "", 10);
    return Number.isFinite(parsed) ? parsed : fallback;
}
function buildRpcConfig() {
    const config = {};
    for (const chain of SUPPORTED_CHAINS) {
        const rpcUrls = getRpcUrls(chain);
        if (rpcUrls.length === 0)
            continue;
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
            retryDelay: parseIntEnv(process.env.LISTA_RPC_RETRY_DELAY_MS, rpcConfig.retryDelay),
        };
    }
    return transportByChainId;
}
function buildSdkSignature(rpcUrls, transportByChainId) {
    return JSON.stringify({ rpcUrls, transportByChainId });
}
export function getSDK() {
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
