import type { Address } from "viem";
import type { getSDK, MarketRuntimeData } from "../../sdk.js";

export interface RepayRuntime {
  sdk: ReturnType<typeof getSDK>;
  marketId: Address;
  chain: string;
  chainId: number;
  walletAddress: Address;
  walletTopic: string | null;
  marketInfo: MarketRuntimeData["marketInfo"];
  marketExtraInfo: MarketRuntimeData["marketExtraInfo"];
  userData: MarketRuntimeData["userData"];
}
