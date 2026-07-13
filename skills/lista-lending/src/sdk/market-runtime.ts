import type {
  MarketExtraInfo,
  MarketUserData,
  WriteMarketConfig,
} from "@lista-dao/moolah-sdk-core";
import type { Address } from "viem";
import { getSDK } from "./client.js";

export interface MarketRuntimeData {
  marketExtraInfo: MarketExtraInfo;
  marketInfo: WriteMarketConfig;
  userData: MarketUserData;
}

export async function getMarketRuntimeData(
  chainId: number,
  marketId: Address,
  walletAddress: Address
): Promise<MarketRuntimeData> {
  return getSDK().getMarketRuntimeData(chainId, marketId, walletAddress);
}
