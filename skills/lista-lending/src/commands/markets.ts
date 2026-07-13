/**
 * Markets command - list available markets
 * Excludes SmartLending (zone=3) and Fixed-term (termType=1) markets
 */

import { fetchMarkets } from "../api.js";
import { SUPPORTED_CHAINS } from "../config.js";
import { setLastFilters } from "../context.js";
import { printJson } from "./shared/output.js";
import type { ListOrder } from "../types/lista-api.js";
import {
  isPositiveInteger,
  isSupportedChain,
  isValidOrder,
} from "../utils/validators.js";

// Zone constants
const ZONE_SMART_LENDING = 3;
// TermType constants
const TERM_TYPE_FIXED = 1;
const MARKET_OPERATION_LIMITATION_NOTE =
  "Smart Lending and fixed-term market operations are currently not supported in this skill. For full functionality, please use the Lista website.";

function formatUsd(value: string): string {
  const num = Number.parseFloat(value);
  if (!Number.isFinite(num)) return "0";
  if (num >= 1_000_000) return `${(num / 1_000_000).toFixed(2)}M`;
  if (num >= 1_000) return `${(num / 1_000).toFixed(2)}K`;
  return num.toFixed(2);
}

export interface MarketsArgs {
  chain?: string;
  page?: number;
  pageSize?: number;
  sort?: string;
  order?: ListOrder;
  zone?: string | number;
  keyword?: string;
  loans?: string[];
  collaterals?: string[];
}

export async function cmdMarkets(args: MarketsArgs): Promise<void> {
  const chain = args.chain || "eip155:56";

  if (!isSupportedChain(chain, SUPPORTED_CHAINS)) {
    printJson({
      status: "error",
      reason: `Unsupported chain: ${chain}. Supported: ${SUPPORTED_CHAINS.join(", ")}`,
    });
    process.exit(1);
  }

  if (args.page !== undefined && !isPositiveInteger(args.page)) {
    printJson({
      status: "error",
      reason: "--page must be a positive integer",
    });
    process.exit(1);
  }

  if (args.pageSize !== undefined && !isPositiveInteger(args.pageSize)) {
    printJson({
      status: "error",
      reason: "--page-size must be a positive integer",
    });
    process.exit(1);
  }

  if (args.order && !isValidOrder(args.order)) {
    printJson({
      status: "error",
      reason: "--order must be asc or desc",
    });
    process.exit(1);
  }

  try {
    // Fetch markets - exclude SmartLending (zone=3) and Fixed-term (termType=1)
    // We filter client-side after fetching to ensure compatibility
    const markets = await fetchMarkets({
      chain,
      page: args.page,
      pageSize: args.pageSize,
      sort: args.sort,
      order: args.order,
      zone: args.zone,
      keyword: args.keyword,
      loans: args.loans,
      collaterals: args.collaterals,
    });

    // Additional client-side filter as safety net
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
        at: new Date().toISOString(),
      },
    });

    if (filteredMarkets.length === 0) {
      printJson({
        status: "success",
        chain,
        markets: [],
        message: "No markets found",
        note: MARKET_OPERATION_LIMITATION_NOTE,
      });
      return;
    }

    // Output JSON for agent parsing
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
        collaterals: args.collaterals,
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
        vaults: m.vaults?.map((v: { name: string }) => v.name).join(", "),
        display: `[${i}] ${m.collateral}/${m.loan} - LLTV: ${(Number.parseFloat(m.lltv) * 100).toFixed(1)}%, Liquidity: $${formatUsd(m.liquidityUsd)}`,
      })),
    });
  } catch (err) {
    printJson({
      status: "error",
      reason: "sdk_error",
      message: (err as Error).message,
    });
    process.exit(1);
  }
}
