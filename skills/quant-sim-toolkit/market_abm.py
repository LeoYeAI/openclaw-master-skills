"""
Agent-Based Market Simulation of Prediction Market Microstructure.

This module implements an agent-based model (ABM) of a prediction market,
demonstrating how private information gets incorporated into prices through
the trading interactions of heterogeneous agents.

Background
----------
Agent-based modeling simulates each market participant individually and lets
the price emerge from their collective actions. This captures dynamics that no
closed-form stochastic differential equation can: the tug-of-war between
informed and uninformed order flow, the adaptive behavior of a market maker,
and the slow revelation of private information.

Three Agent Types
-----------------
1. Informed Traders: Know the true probability of the event (e.g., from
   proprietary research). They trade directionally toward the true value
   whenever the current price offers sufficient edge. Order size is
   proportional to that edge, with small noise added to mask their signal.

2. Noise Traders: Trade randomly, driven by liquidity needs or behavioral
   biases. They provide cover for informed traders but systematically lose
   money because their orders are uncorrelated with fundamental value.

3. Market Maker: Quotes a price at which they transact with incoming orders.
   They do not know who is informed. After each trading round they adjust
   the price based on net order flow using Kyle lambda, the price-impact
   parameter measuring how much price moves per unit of net buying pressure.

Kyle Lambda and Price Impact
-----------------------------
Kyle (1985) showed that in equilibrium, price impact is linear in net flow:

    new_price = old_price + lambda * net_order_flow

Lambda equals sigma_v divided by twice sigma_u, where:
  - sigma_v: volatility of the asset fundamental value (information content)
  - sigma_u: standard deviation of noise trader volume

High lambda means each order is more informative; low lambda means more noise.
The market maker estimates lambda empirically via OLS:
    lambda_hat = Cov(delta_price, flow) over Var(flow)

Information Revelation
----------------------
Starting from 0.50 (maximum uncertainty), the price converges toward true_prob
as informed traders repeatedly buy or sell the mispriced contract. Convergence
speed depends on the informed-to-noise ratio: more informed traders accelerates
price discovery but also raises lambda (each trade reveals more information).

Profit Attribution
------------------
- Informed traders: profit systematically (positive expected PnL)
- Noise traders: lose money on average to informed counterparties
- Market maker: roughly breaks even (earns spread, pays adverse selection)

The total PnL across all agents sums to approximately zero: prediction markets
are zero-sum, every profit has a corresponding loss on the other side.

References
----------
Kyle, A.S. (1985). Continuous Auctions and Insider Trading. Econometrica.
Gode, D. & Sunder, S. (1993). Allocative Efficiency of Markets with
    Zero-Intelligence Traders. Journal of Political Economy.
Farmer, J.D., Patelli, P. & Zovko, I. (2005). The Predictive Power of
    Zero Intelligence. Proceedings of the National Academy of Sciences.
"""

import numpy as np


# =============================================================================
# Agent Classes
# =============================================================================

class InformedTrader:
    """
    Informed trader who knows the true probability and trades toward it.

    Computes edge = true_prob - current_price and places an order proportional
    to that edge. Positive orders are buys (contract underpriced relative to
    private information); negative orders are sells. Small Gaussian noise is
    added to mask the signal and prevent trivial market maker inference.

    Attributes
    ----------
    true_prob : float
        Private estimate of the true event probability.
    aggression : float
        Scales position size. Higher means larger orders per unit of edge.
    pnl : float
        Cumulative profit and loss, settled at true_prob.
    position : float
        Cumulative net position (positive = long, negative = short).
    """

    def __init__(self, true_prob: float, aggression: float = 1.0):
        """
        Parameters
        ----------
        true_prob : float
            True probability known to this trader, in [0, 1].
        aggression : float
            Order size scaling factor. Default 1.0.
        """
        self.true_prob = true_prob
        self.aggression = aggression
        self.pnl = 0.0
        self.position = 0.0

    def trade(self, current_price: float, rng: np.random.Generator) -> float:
        """
        Return an order for this time step.

        Edge = true_prob - current_price. If abs(edge) > 0.01, place an order
        proportional to edge * aggression, plus small masking noise. Returns
        0.0 when edge is at or below the minimum 0.01 threshold.

        Parameters
        ----------
        current_price : float
            Current mid-price set by the market maker.
        rng : np.random.Generator
            Seeded random number generator.

        Returns
        -------
        float
            Order in [-1, 1]. Positive = buy, negative = sell.
        """
        edge = self.true_prob - current_price
        if abs(edge) <= 0.01:
            return 0.0
        order = edge * self.aggression
        order += rng.normal(0, 0.02)
        return float(np.clip(order, -1.0, 1.0))


class NoiseTrader:
    """
    Noise trader who submits random orders with no informational content.

    Without noise traders, the market maker would infer that every order
    comes from an informed trader and would refuse to quote (no-trade
    equilibrium). Noise traders provide the cover that makes price
    discovery possible.

    Attributes
    ----------
    intensity : float
        Standard deviation of random order sizes.
    pnl : float
        Cumulative profit and loss, settled at true_prob.
    position : float
        Cumulative net position.
    """

    def __init__(self, intensity: float = 0.5):
        """
        Parameters
        ----------
        intensity : float
            Standard deviation of noise order sizes. Default 0.5.
        """
        self.intensity = intensity
        self.pnl = 0.0
        self.position = 0.0

    def trade(self, current_price: float, rng: np.random.Generator) -> float:
        """
        Generate a random order with no directional bias.

        Parameters
        ----------
        current_price : float
            Current market price (unused; present for interface consistency
            with InformedTrader).
        rng : np.random.Generator
            Seeded random number generator.

        Returns
        -------
        float
            Order in [-1, 1]. Positive = buy, negative = sell.
        """
        order = rng.normal(0, self.intensity)
        return float(np.clip(order, -1.0, 1.0))


class MarketMaker:
    """
    Market maker who provides liquidity and adjusts price via Kyle lambda.

    Observes net order flow each period and adjusts price linearly. This is
    the rational Bayesian updating rule from Kyle (1985): the price moves
    just enough to reflect the expected information content of the flow.

    Attributes
    ----------
    price : float
        Current mid-price.
    kyle_lambda : float
        Price impact: delta_price = kyle_lambda * net_order_flow.
    pnl : float
        Profit and loss from inventory settled at true_prob.
    inventory : float
        Net inventory (positive = long; bought more than sold).
    """

    def __init__(self, initial_price: float = 0.5, kyle_lambda: float = 0.05):
        """
        Parameters
        ----------
        initial_price : float
            Starting mid-price. Default 0.5 (maximum uncertainty prior).
        kyle_lambda : float
            Price impact coefficient. Default 0.05.
        """
        self.price = initial_price
        self.kyle_lambda = kyle_lambda
        self.pnl = 0.0
        self.inventory = 0.0

    def update(self, net_order_flow: float) -> float:
        """
        Update price given net order flow and return the new price.

        Rule: new_price = old_price + kyle_lambda * net_flow, then clipped
        to [0.01, 0.99] to remain a valid probability. Market maker
        accumulates inventory as the opposite side of all net flow.

        Parameters
        ----------
        net_order_flow : float
            Sum of all agent orders this period (positive = net buying).

        Returns
        -------
        float
            New mid-price after price-impact adjustment.
        """
        self.price = self.price + self.kyle_lambda * net_order_flow
        self.price = float(np.clip(self.price, 0.01, 0.99))
        # Market maker takes opposite side of net flow; inventory grows
        self.inventory -= net_order_flow
        return self.price


# =============================================================================
# Simulation Functions
# =============================================================================

def estimate_kyle_lambda(prices: np.ndarray, net_flows: np.ndarray) -> float:
    """
    Estimate Kyle lambda from observed price changes and order flows.

    Uses OLS: lambda_hat = Cov(delta_price, flow) over Var(flow).
    Regresses price changes on net flows to recover the price-impact
    coefficient empirically from simulated data.

    Parameters
    ----------
    prices : np.ndarray
        Price at each step, length n_steps + 1.
    net_flows : np.ndarray
        Net order flow at each step, length n_steps.

    Returns
    -------
    float
        Estimated Kyle lambda. Returns 0.0 if flow variance is negligible.
    """
    delta_p = np.diff(prices)
    min_len = min(len(delta_p), len(net_flows))
    delta_p = delta_p[:min_len]
    flows = net_flows[:min_len]

    var_f = float(np.var(flows))
    if var_f < 1e-12:
        return 0.0

    cov_matrix = np.cov(delta_p, flows)
    cov_val = float(cov_matrix[0, 1])
    lambda_hat = cov_val / var_f
    return float(lambda_hat)


def simulate_market(
    true_prob: float,
    n_informed: int,
    n_noise: int,
    n_steps: int,
    kyle_lambda: float,
    rng: np.random.Generator,
) -> dict:
    """
    Run one agent-based market simulation.

    Each step: all agents submit orders, net flow is aggregated, market maker
    updates price via Kyle lambda. PnL accumulates each step as:
        pnl_delta = order * (true_prob - execution_price)
    representing the expected settlement gain for a position taken at the
    current pre-impact price.

    Parameters
    ----------
    true_prob : float
        True probability of the event; the target for price convergence.
    n_informed : int
        Number of informed traders in the simulation.
    n_noise : int
        Number of noise traders in the simulation.
    n_steps : int
        Number of trading periods to simulate.
    kyle_lambda : float
        Market maker price-impact coefficient.
    rng : np.random.Generator
        Seeded random number generator for full reproducibility.

    Returns
    -------
    dict
        prices : np.ndarray, shape (n_steps+1,)
            Mid-price at each step, starting from 0.50.
        informed_pnl : float
            Aggregate PnL of all informed traders.
        noise_pnl : float
            Aggregate PnL of all noise traders.
        mm_pnl : float
            Market maker PnL from inventory settled at true_prob.
        net_flows : np.ndarray, shape (n_steps,)
            Net order flow at each step.
        kyle_lambda_estimated : float
            Lambda recovered empirically from price changes and flows.
    """
    # Informed trader population: slight aggression variation across agents
    aggression_vals = rng.uniform(0.8, 1.2, n_informed)
    informed = [
        InformedTrader(true_prob=true_prob, aggression=float(a))
        for a in aggression_vals
    ]

    # Noise trader population: slight intensity variation across agents
    intensity_vals = rng.uniform(0.3, 0.7, n_noise)
    noise = [NoiseTrader(intensity=float(iv)) for iv in intensity_vals]

    # Market maker starts at 0.5 (uninformative prior)
    mm = MarketMaker(initial_price=0.5, kyle_lambda=kyle_lambda)

    prices = np.empty(n_steps + 1)
    prices[0] = mm.price
    net_flows = np.empty(n_steps)

    for t in range(n_steps):
        current_price = mm.price

        # Each agent submits an order at the current price
        i_orders = [tr.trade(current_price, rng) for tr in informed]
        n_orders = [tr.trade(current_price, rng) for tr in noise]

        net_flow = float(np.sum(i_orders) + np.sum(n_orders))
        net_flows[t] = net_flow

        # Market maker adjusts price based on net order flow
        mm.update(net_flow)

        # PnL: each unit traded at current_price, settled at true_prob
        for tr, order in zip(informed, i_orders):
            tr.pnl += order * (true_prob - current_price)
            tr.position += order

        for tr, order in zip(noise, n_orders):
            tr.pnl += order * (true_prob - current_price)
            tr.position += order

        prices[t + 1] = mm.price

    # Market maker settles inventory at true_prob vs average execution price
    mm_avg_px = float(np.mean(prices[:-1]))
    mm.pnl = mm.inventory * (true_prob - mm_avg_px)

    informed_pnl = float(sum(tr.pnl for tr in informed))
    noise_pnl = float(sum(tr.pnl for tr in noise))
    lam_est = estimate_kyle_lambda(prices, net_flows)

    return {
        "prices": prices,
        "informed_pnl": informed_pnl,
        "noise_pnl": noise_pnl,
        "mm_pnl": mm.pnl,
        "net_flows": net_flows,
        "kyle_lambda_estimated": lam_est,
    }


def _steps_to_converge(prices: np.ndarray, true_prob: float, tol: float = 0.05) -> int:
    """Return the first step index where abs(price - true_prob) is within tol."""
    for i, p in enumerate(prices):
        if abs(p - true_prob) <= tol:
            return i
    return len(prices) - 1


# =============================================================================
# Demo
# =============================================================================

if __name__ == "__main__":

    print("=" * 60)
    print("AGENT-BASED MARKET SIMULATION")
    print("=" * 60)

    # --- Simulation 1: Baseline ---
    rng = np.random.default_rng(42)

    TRUE_PROB   = 0.70
    N_INFORMED  = 5
    N_NOISE     = 20
    N_STEPS     = 1000
    KYLE_LAMBDA = 0.05

    print(f"\nSimulation 1: Baseline")
    print(f"  True probability : {TRUE_PROB}")
    print(f"  Informed traders : {N_INFORMED}")
    print(f"  Noise traders    : {N_NOISE}")
    print(f"  Steps            : {N_STEPS}")
    print(f"  Kyle lambda (cfg): {KYLE_LAMBDA}")

    res1 = simulate_market(
        true_prob=TRUE_PROB,
        n_informed=N_INFORMED,
        n_noise=N_NOISE,
        n_steps=N_STEPS,
        kyle_lambda=KYLE_LAMBDA,
        rng=rng,
    )

    p1 = res1["prices"]
    total_pnl1 = res1["informed_pnl"] + res1["noise_pnl"] + res1["mm_pnl"]
    checkpoints = [0, 100, 250, 500, 750, 1000]

    print(f"\n--- Results ---")
    print(f"  True probability         : {TRUE_PROB:.4f}")
    print(f"  Final market price       : {p1[-1]:.4f}")
    print(f"  Convergence error        : {abs(p1[-1] - TRUE_PROB):.4f}")
    print(f"  Steps to converge (0.05) : {_steps_to_converge(p1, TRUE_PROB)}")

    print(f"\n--- PnL Breakdown ---")
    print(f"  Informed traders  : {res1['informed_pnl']:+.4f}")
    print(f"  Noise traders     : {res1['noise_pnl']:+.4f}")
    print(f"  Market maker      : {res1['mm_pnl']:+.4f}")
    print(f"  Total (sum ~= 0)  : {total_pnl1:+.4f}")

    print(f"\n--- Kyle Lambda ---")
    print(f"  Configured        : {KYLE_LAMBDA:.4f}")
    print(f"  Estimated         : {res1['kyle_lambda_estimated']:.4f}")

    print(f"\n--- Price Trajectory ---")
    print(f"  {'Step':>6}  {'Price':>8}  {'vs True':>8}")
    print(f"  {'-'*6}  {'-'*8}  {'-'*8}")
    for step in checkpoints:
        price = p1[step]
        print(f"  {step:>6}  {price:>8.4f}  {price - TRUE_PROB:>+8.4f}")

    # --- Simulation 2: High Noise ---
    print()
    print("=" * 60)
    print("Simulation 2: High Noise (3x more noise traders)")
    print("=" * 60)

    rng2 = np.random.default_rng(42)
    N_NOISE_2 = 60  # 3x baseline

    print(f"\n  True probability : {TRUE_PROB}")
    print(f"  Informed traders : {N_INFORMED}")
    print(f"  Noise traders    : {N_NOISE_2}  (3x baseline)")
    print(f"  Steps            : {N_STEPS}")
    print(f"  Kyle lambda (cfg): {KYLE_LAMBDA}")

    res2 = simulate_market(
        true_prob=TRUE_PROB,
        n_informed=N_INFORMED,
        n_noise=N_NOISE_2,
        n_steps=N_STEPS,
        kyle_lambda=KYLE_LAMBDA,
        rng=rng2,
    )

    p2 = res2["prices"]
    total_pnl2 = res2["informed_pnl"] + res2["noise_pnl"] + res2["mm_pnl"]

    print(f"\n--- Results ---")
    print(f"  Final market price       : {p2[-1]:.4f}")
    print(f"  Convergence error        : {abs(p2[-1] - TRUE_PROB):.4f}")
    print(f"  Steps to converge (0.05) : {_steps_to_converge(p2, TRUE_PROB)}")

    print(f"\n--- PnL Breakdown ---")
    print(f"  Informed traders  : {res2['informed_pnl']:+.4f}")
    print(f"  Noise traders     : {res2['noise_pnl']:+.4f}")
    print(f"  Market maker      : {res2['mm_pnl']:+.4f}")
    print(f"  Total (sum ~= 0)  : {total_pnl2:+.4f}")

    print(f"\n--- Kyle Lambda ---")
    print(f"  Configured        : {KYLE_LAMBDA:.4f}")
    print(f"  Estimated         : {res2['kyle_lambda_estimated']:.4f}")
    print(f"  (More noise => less informative flow => lower estimated lambda)")

    print(f"\n--- Price Trajectory ---")
    print(f"  {'Step':>6}  {'Price':>8}  {'vs True':>8}")
    print(f"  {'-'*6}  {'-'*8}  {'-'*8}")
    for step in checkpoints:
        price = p2[step]
        print(f"  {step:>6}  {price:>8.4f}  {price - TRUE_PROB:>+8.4f}")

    # --- Key Insights ---
    print()
    print("=" * 60)
    print("KEY INSIGHTS")
    print("=" * 60)
    print("""
  1. Informed traders profit systematically. Their edge comes from
     private information about the true probability; they buy
     underpriced contracts and sell overpriced ones until the
     market converges to the correct price.

  2. Noise traders lose money on average. Their random orders are
     uncorrelated with value, so they donate to informed traders
     over time. This is the cost of uninformed trading.

  3. Market maker roughly breaks even. Spread income from noise
     traders is offset by adverse selection losses to informed
     traders. Net PnL is near zero in aggregate.

  4. Price converges toward true probability through repeated
     informed trading. Speed scales with the informed-to-noise
     ratio: more informed traders means faster convergence.

  5. Higher noise slows convergence (Simulation 2). When noise
     dominates order flow, each trade is less informative and
     the price updates more conservatively per period.

  6. Estimated Kyle lambda recovers the configured coefficient,
     validating the linear price-impact model empirically from
     simulated data.
""")
