import { getSDK } from "./client.js";
export async function getMarketRuntimeData(chainId, marketId, walletAddress) {
    return getSDK().getMarketRuntimeData(chainId, marketId, walletAddress);
}
