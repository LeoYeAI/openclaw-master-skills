import type { MarketExtraInfo, MarketUserData, WriteMarketConfig } from "@lista-dao/moolah-sdk-core";
import type { Address } from "viem";
export interface MarketRuntimeData {
    marketExtraInfo: MarketExtraInfo;
    marketInfo: WriteMarketConfig;
    userData: MarketUserData;
}
export declare function getMarketRuntimeData(chainId: number, marketId: Address, walletAddress: Address): Promise<MarketRuntimeData>;
