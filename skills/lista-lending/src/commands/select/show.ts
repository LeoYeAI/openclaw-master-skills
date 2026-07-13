import { loadContext } from "../../context.js";

export function buildSelectShowPayload(): Record<string, unknown> {
  const ctx = loadContext();
  if (!ctx.selectedVault && !ctx.selectedMarket) {
    return {
      status: "success",
      selected: null,
      selectedMarket: null,
      message:
        "No position selected. Use 'select --vault <address>' or 'select --market <id>'.",
    };
  }

  const position =
    ctx.selectedVault && ctx.userPosition
      ? {
          assets: ctx.userPosition.assets,
          balance: ctx.userPosition.assets,
          assetsUsd: ctx.userPosition.assetsUsd,
        }
      : null;

  return {
    status: "success",
    selected: ctx.selectedVault,
    selectedMarket: ctx.selectedMarket,
    userAddress: ctx.userAddress,
    walletTopic: ctx.walletTopic,
    position,
    lastFilters: ctx.lastFilters,
    lastUpdated: ctx.lastUpdated,
  };
}

export function buildSelectClearedPayload(): Record<string, unknown> {
  return {
    status: "success",
    action: "cleared",
    message: "Selection cleared",
  };
}
