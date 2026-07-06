// LS-LMSR pricing model and market math helpers used by quote.mjs.
//
// LSLMSR  — full class implementation of the Logarithmic Scoring Rule
//           Market Maker with liquidity-sensitive parameter (alpha).
//           Used for --price target resolution (maxSharesFromPrice).
//
// marketSharesFromCost / marketPriceAfterTrade / getFuturePriceAfterTrade —
//           standalone functions that mirror the on-chain cost curve.
//           Used for --cost / --all resolution and probability-after-trade display.

// ── LSLMSR class ──────────────────────────────────────────────────────────────

export class LSLMSR {
    constructor(outcomes, alpha, initialShares = 0, sellFee = 0) {
      this.outcomes = outcomes;
      this.alpha = alpha;
      this.initialShares = initialShares;
      this.sellFee = sellFee;
  
      this.q = {};
      for (const o of outcomes) this.q[o] = this.initialShares;
  
      this.initialCost = this.cost();
      this.collectedFees = 0;
    }
  
    static fromState(outcomesBalances, alpha) {
      const outcomes = Object.keys(outcomesBalances);
      const initialShares = Math.min(...Object.values(outcomesBalances));
      const market = new LSLMSR(outcomes, alpha, initialShares);
      market.q = outcomesBalances;
      return market;
    }
  
    b(q = this.q) {
      return this.alpha * this.outcomes.reduce((sum, o) => sum + q[o], 0);
    }
  
    cost(q = this.q) {
      const bq = this.b(q);
      if (bq === 0) return 0;
  
      const sumExp = this.outcomes.reduce((sum, o) => sum + Math.exp(q[o] / bq), 0);
      return bq * Math.log(sumExp);
    }
  
    prices() {
      const result = {};
      for (const o of this.outcomes) {
        result[o] = this.tradeCost(o, 1);
      }
      return result;
    }
  
    trade(outcome, deltaQ) {
      const oldCost = this.cost();
      this.q[outcome] += deltaQ;
      const newCost = this.cost();
      return Math.abs(newCost - oldCost);
    }
  
    buy(outcome, shares) {
      return this.trade(outcome, Math.abs(shares));
    }
  
    sell(outcome, shares) {
      const tradeReturn = this.trade(outcome, -Math.abs(shares));
      const tradeFee = tradeReturn * this.sellFee;
      this.collectedFees += tradeFee;
      return tradeReturn - tradeFee;
    }
  
    tradeCost(outcome, deltaQ) {
      const tempQ = { ...this.q };
      tempQ[outcome] += deltaQ;
  
      const tradeCost = Math.abs(this.cost(tempQ) - this.cost(this.q));
      let tradeFee = 0;
  
      if (deltaQ < 0) tradeFee = tradeCost * this.sellFee;
  
      return tradeCost - tradeFee;
    }
  
    getBalances() {
      return { ...this.q };
    }
  
    getOutcome(outcome_index) {
      return this.outcomes[outcome_index - 1];
    }
  
    pricesAfterTrade(outcome, deltaQ) {
      const tempQ = { ...this.q };
      tempQ[outcome] += deltaQ;
  
      const result = {};
  
      for (const o of this.outcomes) {
        const qWith1More = { ...tempQ };
        qWith1More[o] += 1;
        result[o] = this.cost(qWith1More) - this.cost(tempQ);
      }
  
      return result;
    }
  
    maxSharesFromCost(outcome, budget, precision = 1e-9) {
      let low = 0;
      let high = 1;
  
      while (this.tradeCost(outcome, high) < budget) {
        high *= 2;
      }
  
      while (high - low > precision) {
        const mid = (low + high) / 2;
        const cost = this.tradeCost(outcome, mid);
  
        if (cost > budget) {
          high = mid;
        } else {
          low = mid;
        }
      }
  
      return low;
    }
  
    maxSharesFromPrice(outcome, targetPrice, precision = 1e-9) {
      let low = 0;
      let high = 1;
  
      while (true) {
        const price = this.pricesAfterTrade(outcome, high)[outcome];
        if (price >= targetPrice) break;
        high *= 2;
      }
  
      while (high - low > precision) {
        const mid = (low + high) / 2;
        const price = this.pricesAfterTrade(outcome, mid)[outcome];
  
        if (price > targetPrice) {
          high = mid;
        } else {
          low = mid;
        }
      }
  
      return low;
    }
  
    maxLoss() {
      const n = this.outcomes.length;
      const overround = this.alpha * (n * Math.log(n));
      return this.initialShares * overround;
    }
  
    addLiquidity(value) {
      const k = value / this.cost();
  
      for (const outcome in this.outcomes) {
        this.buy(outcome, this.q[outcome] * k);
      }
    }
  }



// ── Standalone market cost / price functions ──────────────────────────────────

/**
 * Calculate the total amount of collateral deposited in a Market
 *
 * @param shares - List of shares balances for all outcomes in the Market
 * @param alpha - Fixed PrecogMarket contract variable defined on market initialization
 */
const marketCost = (shares, alpha) => {
    const totalShares = shares.reduce((sum, s) => sum + s, 0);
    const beta = totalShares * alpha;
  
    const sumTotal = shares.reduce((sum, s) => (s === 0 ? sum : sum + Math.exp(s / beta)), 0);
    return beta * Math.log(sumTotal);
  };
  
  /**
   * Calculate the total amount of collateral that will be deposited after a trade
   */
  const marketCostAfterTrade = (shares, alpha, outcome, amount) => {
    const newShares = [...shares];
    newShares[outcome] += amount;
  
    return marketCost(newShares, alpha);
  };
  
  /**
   * Calculate the amount of collateral required for a trade
   */
  const marketTradeCost = (shares, alpha, outcome, amount) => {
    const cost = marketCost(shares, alpha);
    const costAfterTrade = marketCostAfterTrade(shares, alpha, outcome, amount);
    return Math.abs(costAfterTrade - cost);
  };
  
  /**
   * Calculate shares purchasable from a given cost
   */
  export const marketSharesFromCost = (shares, alpha, outcome, totalCost) => {
    const maxIterations = 100;
    const tolerance = 0.0001;
  
    let low = totalCost * 0.999;
    let high = totalCost * 10000;
    let mid = 0;
  
    for (let i = 0; i < maxIterations; i++) {
      mid = (low + high) / 2;
      const cost = marketTradeCost(shares, alpha, outcome, mid);
  
      if (Math.abs(cost - totalCost) < tolerance) return mid;
      if (cost < totalCost) low = mid;
      else high = mid;
    }
  
    return mid;
  };
  
  /**
   * Calculate price of a single share after a trade
   */
  export const marketPriceAfterTrade = (shares, alpha, outcome, amount) => {
    const costAfterTrade = marketCostAfterTrade(shares, alpha, outcome, amount);
  
    const oneShareDelta = amount > 0 ? amount + 1 : amount - 1;
    const costAfterTradeWithDelta = marketCostAfterTrade(shares, alpha, outcome, oneShareDelta);
  
    return Math.abs(costAfterTradeWithDelta - costAfterTrade);
  };
  
  /**
   * Calculates the price of buying/selling one share after a trade is completed
   */
  export const getFuturePriceAfterTrade = (
    shares,
    alpha,
    outcome,
    tradeAmount
  ) => {
    const sharesAfterTrade = [...shares];
    sharesAfterTrade[outcome] += tradeAmount;
  
    return marketTradeCost(sharesAfterTrade, alpha, outcome, 1);
  };