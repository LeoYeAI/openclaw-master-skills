"""
Enhanced Kelly Position Sizer for Options Conviction Engine

Implements drawdown-constrained, correlation-aware position sizing
based on Kelly Criterion with modifications for small account trading.

The Kelly Criterion maximizes long-term growth by sizing positions
proportional to edge: f = (p*b - q) / b

Where:
- f = optimal fraction of bankroll to bet
- p = probability of win
- q = probability of loss (1-p)
- b = win/loss ratio (average win / average loss)

References:
- Kelly, J.L. (1956). "A New Interpretation of Information Rate." Bell System Technical Journal
- Thorp, E. (2006). "The Kelly Criterion in Blackjack, Sports Betting, and the Stock Market"
- Rotando, L. & Thorp, E. (1992). "The Kelly Criterion and the Stock Market"
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class KellyFraction(Enum):
    """Kelly fraction options for different risk tolerances."""
    FULL = 1.0      # Full Kelly (aggressive, high variance)
    HALF = 0.5      # Half Kelly (moderate, recommended)
    QUARTER = 0.25  # Quarter Kelly (conservative)
    EIGHTH = 0.125  # Eighth Kelly (very conservative)


@dataclass
class PositionResult:
    """Complete position sizing result."""
    contracts: int
    total_risk: float
    kelly_fraction: float
    adjusted_kelly: float
    risk_per_contract: float
    max_loss: float
    expected_value: float
    recommendation: str
    reasoning: str
    drawdown_estimate: float


@dataclass
class CorrelationPenalty:
    """Correlation-based position size penalty."""
    correlation: float
    penalty_factor: float
    reason: str


class EnhancedKellySizer:
    """
    Drawdown-constrained, correlation-aware Kelly position sizing.
    
    Features:
    - Standard Kelly calculation with configurable fraction
    - Drawdown constraint (won't suggest sizes that could exceed max drawdown)
    - Correlation penalty (reduces size when correlated positions exist)
    - Conviction-based Kelly scaling (higher conviction = larger fraction)
    - Small account guardrails (min/max position limits)
    
    Usage:
        sizer = EnhancedKellySizer(account_value=390, max_drawdown=0.20)
        result = sizer.calculate_position(
            spread_cost=100,
            max_loss_per_spread=85,
            win_amount=35,
            conviction=85,
            pop=0.68,
            existing_positions=[{"ticker": "SPY", "correlation": 0.85}]
        )
    """
    
    def __init__(self, 
                 account_value: float = 390,
                 max_drawdown: float = 0.20,
                 min_contracts: int = 1,
                 max_risk_per_trade: float = 100,
                 max_risk_total: float = 150):
        """
        Initialize EnhancedKellySizer.
        
        Args:
            account_value: Total account value in dollars
            max_drawdown: Maximum acceptable drawdown (0.20 = 20%)
            min_contracts: Minimum contracts per trade (usually 1)
            max_risk_per_trade: Maximum risk per trade in dollars
            max_risk_total: Maximum total risk across all positions
        """
        self.account = account_value
        self.max_dd = max_drawdown
        self.min_contracts = min_contracts
        self.max_risk_trade = max_risk_per_trade
        self.max_risk_total = max_risk_total
        
    def kelly_criterion(self, 
                       win_prob: float, 
                       win_amount: float, 
                       loss_amount: float) -> Tuple[float, float]:
        """
        Calculate Kelly Criterion optimal fraction.
        
        Kelly formula: f = (p*b - q) / b
        Where b = win_amount / loss_amount (odds received)
        
        Args:
            win_prob: Probability of winning (0-1)
            win_amount: Average win amount ($)
            loss_amount: Average loss amount ($)
            
        Returns:
            Tuple of (kelly_fraction, edge)
        """
        if loss_amount <= 0:
            raise ValueError("Loss amount must be positive")
        
        loss_prob = 1 - win_prob
        odds = win_amount / loss_amount
        
        # Kelly fraction (can be negative if no edge)
        kelly = (win_prob * odds - loss_prob) / odds if odds > 0 else 0
        
        # Edge calculation: expected value per dollar risked
        edge = (win_prob * win_amount) - (loss_prob * loss_amount)
        
        return kelly, edge
    
    def drawdown_constrained_kelly(self,
                                   full_kelly: float,
                                   existing_correlation: float = 0) -> float:
        """
        Adjust Kelly for maximum drawdown constraint.
        
        Formula accounts for the fact that full Kelly can produce
        large drawdowns even with positive expectancy.
        
        For uncorrelated bets, theoretical max drawdown at full Kelly
        can approach 100%. We constrain to acceptable level.
        
        Args:
            full_kelly: Unconstrained Kelly fraction
            existing_correlation: Correlation with existing positions (0-1)
            
        Returns:
            Drawdown-constrained Kelly fraction
        """
        if full_kelly <= 0:
            return 0
        
        # Full Kelly with correlation adjustment
        # Higher correlation = lower effective Kelly due to concentration risk
        correlation_adjustment = 1 - (existing_correlation * 0.5)
        adjusted_kelly = full_kelly * correlation_adjustment
        
        # Drawdown constraint
        # At full Kelly, expected max drawdown ≈ 1 / (2 * growth_rate)
        # Simplified: limit Kelly such that expected drawdown <= max_dd
        # This is approximate; true calculation requires simulation
        
        # Drawdown constraint based on Thorp (2006)
        # Full Kelly can produce ~50-80% max drawdown depending on variance
        # Scale proportionally to target max_dd (conservative heuristic)
        drawdown_scaling = self.max_dd / 0.50  # Target DD / typical full-Kelly DD
        constrained_kelly = adjusted_kelly * drawdown_scaling
        
        return max(0, constrained_kelly)
    
    def conviction_based_kelly(self, 
                              base_kelly: float,
                              conviction_score: float) -> Tuple[float, KellyFraction]:
        """
        Scale Kelly by conviction tier.
        
        Higher conviction = larger fraction of Kelly used.
        This reflects confidence in the edge estimation.
        
        Args:
            base_kelly: Drawdown-constrained Kelly fraction
            conviction_score: Conviction score (0-100)
            
        Returns:
            Tuple of (scaled_kelly, kelly_tier_used)
        """
        if base_kelly <= 0:
            return 0, KellyFraction.FULL
        
        # Map conviction to Kelly fraction
        if conviction_score >= 90:
            fraction = KellyFraction.HALF  # 0.50
        elif conviction_score >= 80:
            fraction = KellyFraction.QUARTER  # 0.25
        elif conviction_score >= 60:
            fraction = KellyFraction.EIGHTH  # 0.125
        else:
            # Below 60 conviction - no position
            return 0, KellyFraction.EIGHTH
        
        scaled = base_kelly * fraction.value
        
        return scaled, fraction
    
    def calculate_correlation_penalty(self,
                                     ticker: str,
                                     existing_positions: List[Dict]) -> CorrelationPenalty:
        """
        Calculate position size reduction due to correlations.
        
        If existing positions are highly correlated with new trade,
        reduce size to avoid concentration risk.
        
        Args:
            ticker: Ticker symbol for new trade
            existing_positions: List of dicts with 'ticker' and 'correlation' keys
            
        Returns:
            CorrelationPenalty with penalty factor
        """
        if not existing_positions:
            return CorrelationPenalty(0, 1.0, "No existing positions")
        
        # Find highest correlation with existing positions
        max_corr = max(pos.get('correlation', 0) for pos in existing_positions)
        avg_corr = np.mean([pos.get('correlation', 0) for pos in existing_positions])
        
        # Penalty increases with correlation
        if max_corr > 0.9:
            penalty = 0.3  # 70% reduction for very high correlation
            reason = f"Very high correlation ({max_corr:.0%}) with existing position"
        elif max_corr > 0.7:
            penalty = 0.5  # 50% reduction
            reason = f"High correlation ({max_corr:.0%}) with existing position"
        elif max_corr > 0.5:
            penalty = 0.7  # 30% reduction
            reason = f"Moderate correlation ({max_corr:.0%}) with existing position"
        else:
            penalty = 1.0  # No penalty
            reason = f"Low correlation ({max_corr:.0%}) - no reduction"
        
        return CorrelationPenalty(
            correlation=max_corr,
            penalty_factor=penalty,
            reason=reason
        )
    
    def calculate_position(self,
                          spread_cost: float,
                          max_loss_per_spread: float,
                          win_amount: float,
                          conviction: float,
                          pop: float,
                          ticker: str = "",
                          existing_positions: Optional[List[Dict]] = None) -> PositionResult:
        """
        Calculate optimal position size using Enhanced Kelly.
        
        Pipeline:
        1. Calculate base Kelly from win probability and payoff
        2. Apply drawdown constraint
        3. Apply conviction scaling
        4. Apply correlation penalty
        5. Enforce small account guardrails
        6. Round to integer contracts
        
        Args:
            spread_cost: Total cost to enter spread ($)
            max_loss_per_spread: Maximum loss if spread goes to max loss ($)
            win_amount: Expected win amount ($)
            conviction: Conviction score (0-100)
            pop: Probability of profit (0-1)
            ticker: Ticker symbol
            existing_positions: List of existing position correlations
            
        Returns:
            PositionResult with sizing recommendation
        """
        if existing_positions is None:
            existing_positions = []
        
        # Validate inputs
        if not (0 <= pop <= 1):
            raise ValueError(f"POP must be between 0 and 1, got {pop}")
        if not (0 <= conviction <= 100):
            raise ValueError(f"Conviction must be between 0 and 100, got {conviction}")
        
        # Step 1: Base Kelly calculation
        try:
            full_kelly, edge = self.kelly_criterion(pop, win_amount, max_loss_per_spread)
        except ValueError as e:
            return PositionResult(
                contracts=0,
                total_risk=0,
                kelly_fraction=0,
                adjusted_kelly=0,
                risk_per_contract=max_loss_per_spread,
                max_loss=0,
                expected_value=0,
                recommendation="NO_TRADE",
                reasoning=f"Kelly calculation error: {e}",
                drawdown_estimate=0
            )
        
        if full_kelly <= 0:
            return PositionResult(
                contracts=0,
                total_risk=0,
                kelly_fraction=0,
                adjusted_kelly=0,
                risk_per_contract=max_loss_per_spread,
                max_loss=0,
                expected_value=edge,
                recommendation="NO_TRADE",
                reasoning="Negative Kelly - no mathematical edge",
                drawdown_estimate=0
            )
        
        # Step 2: Drawdown constraint
        avg_correlation = np.mean([p.get('correlation', 0) for p in existing_positions]) if existing_positions else 0
        dd_constrained = self.drawdown_constrained_kelly(full_kelly, avg_correlation)
        
        # Step 3: Conviction scaling
        conviction_scaled, kelly_tier = self.conviction_based_kelly(dd_constrained, conviction)
        
        # Step 4: Correlation penalty
        corr_penalty = self.calculate_correlation_penalty(ticker, existing_positions)
        after_correlation = conviction_scaled * corr_penalty.penalty_factor
        
        # Step 5: Calculate contracts
        # Kelly suggests fraction of bankroll to risk
        suggested_risk = self.account * after_correlation
        
        # Enforce guardrails
        suggested_risk = min(suggested_risk, self.max_risk_trade)  # Per-trade limit
        suggested_risk = min(suggested_risk, self.max_risk_total - self._current_total_risk(existing_positions))
        
        # If constrained risk can't afford even 1 contract, exit
        if suggested_risk < max_loss_per_spread:
            contracts = 0
        else:
            # Convert risk to contracts
            contracts = int(suggested_risk / max_loss_per_spread)
            contracts = max(0, contracts)  # No negative contracts
        
        # Step 6: Final calculations
        total_risk = contracts * max_loss_per_spread
        expected_value = contracts * edge
        
        # Estimate drawdown for this position
        dd_estimate = self._estimate_position_drawdown(contracts, max_loss_per_spread, pop)
        
        # Generate recommendation
        if contracts == 0:
            if full_kelly <= 0:
                recommendation = "NO_TRADE"
                reasoning = "No mathematical edge (Kelly <= 0)"
            elif conviction < 60:
                recommendation = "NO_TRADE"
                reasoning = f"Conviction too low ({conviction}) - minimum 60 required"
            else:
                recommendation = "NO_TRADE"
                reasoning = "Risk constraints prevent position (correlation or capital limits)"
        elif contracts == 1:
            recommendation = "MINIMAL_SIZE"
            reasoning = self._build_reasoning(full_kelly, kelly_tier, corr_penalty, "Minimal size due to constraints")
        elif contracts >= 4 and conviction >= 90:
            recommendation = "AGGRESSIVE"
            reasoning = self._build_reasoning(full_kelly, kelly_tier, corr_penalty, "High conviction allows aggressive sizing")
        else:
            recommendation = "STANDARD"
            reasoning = self._build_reasoning(full_kelly, kelly_tier, corr_penalty, "Standard Kelly sizing")
        
        return PositionResult(
            contracts=contracts,
            total_risk=round(total_risk, 2),
            kelly_fraction=round(full_kelly, 4),
            adjusted_kelly=round(after_correlation, 4),
            risk_per_contract=round(max_loss_per_spread, 2),
            max_loss=round(total_risk, 2),
            expected_value=round(expected_value, 2),
            recommendation=recommendation,
            reasoning=reasoning,
            drawdown_estimate=round(dd_estimate, 3)
        )
    
    def _current_total_risk(self, existing_positions: List[Dict]) -> float:
        """Calculate current total risk from existing positions."""
        return sum(pos.get('risk', 0) for pos in existing_positions)
    
    def _estimate_position_drawdown(self, 
                                   contracts: int, 
                                   max_loss: float, 
                                   pop: float) -> float:
        """
        Estimate expected drawdown from this position.
        
        Simplified estimate: assume loss with probability (1-POP)
        """
        if contracts == 0:
            return 0
        expected_loss = contracts * max_loss * (1 - pop)
        return expected_loss / self.account
    
    def _build_reasoning(self,
                        full_kelly: float,
                        kelly_tier: KellyFraction,
                        corr_penalty: CorrelationPenalty,
                        note: str) -> str:
        """Build human-readable reasoning string."""
        parts = [
            f"Full Kelly: {full_kelly:.2%}",
            f"Using: {kelly_tier.name} Kelly ({kelly_tier.value:.0%})",
        ]
        
        if corr_penalty.penalty_factor < 1.0:
            parts.append(f"Correlation penalty: {corr_penalty.penalty_factor:.0%}")
        
        parts.append(note)
        return " | ".join(parts)


def quick_size(account: float,
               max_loss: float,
               win_amount: float,
               pop: float,
               conviction: float = 75) -> PositionResult:
    """Quick position sizing with default parameters."""
    sizer = EnhancedKellySizer(account_value=account)
    return sizer.calculate_position(
        spread_cost=max_loss,
        max_loss_per_spread=max_loss,
        win_amount=win_amount,
        conviction=conviction,
        pop=pop
    )


if __name__ == "__main__":
    """Demo: Enhanced Kelly position sizing examples."""
    print("=" * 70)
    print("ENHANCED KELLY POSITION SIZER DEMO")
    print("=" * 70)
    
    # Demo 1: Standard position
    print("\n--- Demo 1: Standard Credit Spread ---")
    sizer = EnhancedKellySizer(account_value=390, max_drawdown=0.20)
    result = sizer.calculate_position(
        spread_cost=85,
        max_loss_per_spread=85,
        win_amount=35,
        conviction=85,
        pop=0.68,
        ticker="SPY"
    )
    
    print(f"Contracts: {result.contracts}")
    print(f"Total Risk: ${result.total_risk}")
    print(f"Full Kelly: {result.kelly_fraction:.2%}")
    print(f"Adjusted Kelly: {result.adjusted_kelly:.2%}")
    print(f"Expected Value: ${result.expected_value}")
    print(f"Recommendation: {result.recommendation}")
    print(f"Reasoning: {result.reasoning}")
    
    # Demo 2: High conviction
    print("\n--- Demo 2: High Conviction Trade ---")
    result2 = sizer.calculate_position(
        spread_cost=75,
        max_loss_per_spread=75,
        win_amount=40,
        conviction=95,
        pop=0.72,
        ticker="QQQ"
    )
    
    print(f"Contracts: {result2.contracts}")
    print(f"Total Risk: ${result2.total_risk}")
    print(f"Recommendation: {result2.recommendation}")
    print(f"Reasoning: {result2.reasoning}")
    
    # Demo 3: With correlation penalty
    print("\n--- Demo 3: With Existing Correlated Position ---")
    existing = [{"ticker": "SPY", "correlation": 0.85, "risk": 85}]
    result3 = sizer.calculate_position(
        spread_cost=80,
        max_loss_per_spread=80,
        win_amount=30,
        conviction=80,
        pop=0.65,
        ticker="VOO",  # Highly correlated with SPY
        existing_positions=existing
    )
    
    print(f"Contracts: {result3.contracts}")
    print(f"Total Risk: ${result3.total_risk}")
    print(f"Recommendation: {result3.recommendation}")
    print(f"Reasoning: {result3.reasoning}")
    
    # Demo 4: No edge case
    print("\n--- Demo 4: Negative Kelly (No Edge) ---")
    result4 = sizer.calculate_position(
        spread_cost=100,
        max_loss_per_spread=100,
        win_amount=20,
        conviction=70,
        pop=0.45,  # Less than 50% win rate with bad payoff
        ticker="TSLA"
    )
    
    print(f"Contracts: {result4.contracts}")
    print(f"Recommendation: {result4.recommendation}")
    print(f"Reasoning: {result4.reasoning}")
    
    print("\n" + "=" * 70)
