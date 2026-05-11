# Options Spread Conviction Engine — Comprehensive Code Review Report

**Review Date:** February 13, 2026  
**Scope:** 14 Python files (~8,500 lines)  
**Reviewer:** OpenClaw Subagent

---

## 1. Executive Summary

### Overall Code Health Score: 6.5/10

The Options Spread Conviction Engine is a feature-rich quantitative trading analysis system with solid mathematical foundations and thoughtful architecture. However, it suffers from significant **code duplication**, **inconsistent interfaces**, and **insufficient abstraction layers** that have accumulated across multiple development phases.

**Top 3 Critical Issues:**
1. **Severe Duplication of Kelly Criterion Logic** — 4 separate implementations across 3 files with subtle differences that create maintenance risk
2. **Dual Conviction Engine Classes** — Two separate `QuantConvictionEngine` implementations in different files with overlapping but incompatible functionality  
3. **Inconsistent Error Handling** — Mix of bare `except:` clauses, silent failures, and proper exception handling creates unpredictable failure modes

**Estimated Refactoring Effort:** 40-60 hours for consolidation, 20-30 hours for type safety improvements, 15-20 hours for test coverage.

---

## 2. Redundancy Analysis

| File | Line(s) | Issue | Consolidation Target |
|------|---------|-------|---------------------|
| `position_sizer.py` | 40-120 | Kelly criterion implementation | `options_math.py` (existing) |
| `options_math.py` | 460-560 | Duplicate Kelly calculation (`kelly_criterion`, `kelly_fraction`) | Single unified implementation |
| `enhanced_kelly.py` | 75-145 | Third Kelly implementation with drawdown constraints | Merge into unified Kelly module |
| `quant_scanner.py` | 45-115 | Fourth Kelly reference via `EnhancedKellySizer` | Use unified module |
| `quant_scanner.py` | 145-285 | `QuantConvictionEngine` class | `quantitative_integration.py` |
| `quantitative_integration.py` | 85-225 | Duplicate `QuantConvictionEngine` class | Merge with `quant_scanner.py` version |
| `spread_conviction_engine.py` | 45-55, 145-155 | Strategy weight constants duplicated | Single constants module |
| `leg_optimizer.py` | 1085-1454 | Strategy type definitions duplicate `spread_conviction_engine.py` | Import from single source |
| `multi_leg_strategies.py` | 45-85 | Weight constants (IRON_CONDOR_WEIGHTS, etc.) | Strategy constants module |
| `calculator.py` | 65-85, 445-465 | Greeks dataclass duplicates `options_math.py` | Import from `options_math` |
| `chain_analyzer.py` | 245-285, 385-425 | Rate limiting logic duplicated | Utility module |
| `vol_forecaster.py` | 95-145, 205-255 | GARCH fitting duplicated in `analyze()` | Extract to reusable method |

### Critical Duplication Example: Kelly Criterion

**Current State (4 implementations):**

```python
# position_sizer.py (lines 40-60)
def kelly_criterion(pop, win_amount, loss_amount):
    kelly = (pop * win_amount - (1 - pop) * loss_amount) / win_amount
    return kelly

# options_math.py (lines 460-470)  
def kelly_fraction(p, b):
    q = 1.0 - p
    return (p * b - q) / b

# enhanced_kelly.py (lines 75-95)
def kelly_criterion(self, win_prob, win_amount, loss_amount):
    odds = win_amount / loss_amount
    kelly = (win_prob * odds - loss_prob) / odds
    return kelly, edge

# quant_scanner.py (lines 45-115)
# Uses EnhancedKellySizer which has its own implementation
```

**Recommended Consolidation:**

```python
# unified_position_sizing.py
from dataclasses import dataclass
from typing import Literal
from enum import Enum

class KellyVariant(Enum):
    FULL = 1.0
    HALF = 0.5
    QUARTER = 0.25
    EIGHTH = 0.125

@dataclass(frozen=True)
class KellyInputs:
    win_probability: float
    win_amount: float
    loss_amount: float
    
    def __post_init__(self):
        if not 0 <= self.win_probability <= 1:
            raise ValueError(f"POP must be in [0,1], got {self.win_probability}")
        if self.win_amount <= 0 or self.loss_amount <= 0:
            raise ValueError("Win/loss amounts must be positive")

@dataclass
class KellyResult:
    raw_fraction: float
    adjusted_fraction: float
    edge: float
    expected_value: float

class KellyCriterion:
    """Unified Kelly criterion calculator with multiple variants."""
    
    @staticmethod
    def calculate(inputs: KellyInputs, 
                  variant: KellyVariant = KellyVariant.HALF,
                  max_fraction: float = 0.25) -> KellyResult:
        """Calculate Kelly fraction with safety constraints."""
        q = 1.0 - inputs.win_probability
        b = inputs.win_amount / inputs.loss_amount
        
        # Raw Kelly
        f_star = (inputs.win_probability * b - q) / b if b > 0 else 0.0
        
        # Edge calculation
        ev = inputs.win_probability * inputs.win_amount - q * inputs.loss_amount
        edge = ev / inputs.loss_amount if inputs.loss_amount > 0 else 0.0
        
        # Apply variant and cap
        adjusted = f_star * variant.value
        adjusted = max(0.0, min(adjusted, max_fraction))
        
        return KellyResult(
            raw_fraction=f_star,
            adjusted_fraction=adjusted,
            edge=edge,
            expected_value=ev
        )
```

---

## 3. Code Quality Issues

### 3.1 Long Functions (>50 lines)

| File | Lines | Function | Suggested Action |
|------|-------|----------|-----------------|
| `quant_scanner.py` | 285-450 | `QuantConvictionEngine.analyze()` | Split into 6 private methods |
| `spread_conviction_engine.py` | 680-850 | `build_rationale()` | Extract strategy-specific formatters |
| `leg_optimizer.py` | 185-385 | `calculate_strategy_metrics()` | Strategy pattern + per-strategy handlers |
| `backtest_validator.py` | 165-285 | `_simulate_trade()` | Extract P&L calculation logic |
| `multi_leg_strategies.py` | 785-925 | `score_iron_condor()` | Extract scoring table to configuration |
| `multi_leg_strategies.py` | 925-1050 | `score_butterfly()` | Extract scoring table to configuration |
| `multi_leg_strategies.py` | 1050-1175 | `score_calendar()` | Extract scoring table to configuration |
| `options_math.py` | 145-225 | `monte_carlo_pop_iron_condor()` | Already focused, but add early return guards |

### 3.2 Deep Nesting (>4 levels)

| File | Lines | Nesting Depth | Refactor Strategy |
|------|-------|---------------|-------------------|
| `leg_optimizer.py` | 285-385 | 6 levels | Extract strategy-specific calculators |
| `leg_optimizer.py` | 585-785 | 7 levels | Extract validation to separate functions |
| `spread_conviction_engine.py` | 450-680 | 5 levels | Strategy dispatch table instead of if/elif |
| `quant_scanner.py` | 285-450 | 5 levels | Early returns for guard clauses |

### 3.3 Magic Numbers

| File | Line(s) | Magic Number | Should Be Constant |
|------|---------|--------------|-------------------|
| `options_math.py` | 205 | `100000` | `DEFAULT_MC_SIMULATIONS` |
| `options_math.py` | 95 | `42` | `RANDOM_SEED` (configurable) |
| `spread_conviction_engine.py` | 145-155 | Various | `ICHIMOKU_PARAMS`, `RSI_PARAMS` |
| `position_sizer.py` | 35-40 | `0.25`, `100.0` | `DEFAULT_KELLY_FRACTION`, `MAX_RISK_USD` |
| `leg_optimizer.py` | 125 | `0.15` | `MIN_IV_FLOOR` |
| `backtest_validator.py` | 45-50 | `10`, `0.95` | `MIN_OBSERVATIONS`, `CONFIDENCE_LEVEL` |
| `multi_leg_strategies.py` | 185-195 | `0.30`, `0.70` | `IV_RANK_HIGH_THRESHOLD`, etc. |

### 3.4 Unused Variables/Parameters

| File | Line(s) | Issue | Fix |
|------|---------|-------|-----|
| `quant_scanner.py` | 145 | `self.current_regime: Optional[str] = None` | Used but initialization pattern could be cleaner |
| `quant_scanner.py` | 285 | `garch` variable assigned but only checked for None | Use walrus operator or simplify |
| `backtest_validator.py` | 225 | `pnl_pct` calculated but never used in return | Remove or include in BacktestTrade |
| `market_scanner.py` | 185 | `period` and `interval` params not used in analyze_ticker_strategy | Actually used, but could be clearer |
| `leg_optimizer.py` | 585 | `opt_type` parameter shadowed in loop | Rename inner variable |

### 3.5 Dead Code

| File | Lines | Issue | Action |
|------|-------|-------|--------|
| `quant_scanner.py` | 45-55 | `_cached_vrp` set but never read outside `analyze()` | Remove or document why cached |
| `chain_analyzer.py` | 445-455 | `_default_fetcher`, `_default_analyzer` singletons never used | Remove or use in module functions |
| `options_math.py` | 195-200 | `historical_vols` cache dict never populated | Implement caching or remove |

---

## 4. Architecture Recommendations

### 4.1 Missing Abstraction Layers

**Issue:** The codebase lacks a clear strategy pattern for:
1. Options strategy calculations
2. Scoring algorithms  
3. Position sizing algorithms

**Current (anti-pattern):**

```python
# leg_optimizer.py lines 285-385
if strategy.strategy_type == 'put_credit_spread':
    # 50 lines of logic
elif strategy.strategy_type == 'call_credit_spread':
    # 50 lines of similar logic
# ... 12 more elifs
```

**Recommended (Strategy Pattern):**

```python
# strategies/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class StrategyMetrics:
    max_profit: float
    max_loss: float
    breakevens: list[float]
    pop: float
    expected_value: float

class StrategyCalculator(ABC):
    @property
    @abstractmethod
    def strategy_type(self) -> str: ...
    
    @abstractmethod
    def calculate_metrics(self, legs: list[TradeLeg], 
                         underlying_price: float, 
                         iv: float) -> StrategyMetrics: ...
    
    @abstractmethod
    def calculate_pop(self, legs: list[TradeLeg], 
                     underlying_price: float, 
                     iv: float) -> float: ...

# strategies/put_credit_spread.py
class PutCreditSpreadCalculator(StrategyCalculator):
    strategy_type = 'put_credit_spread'
    
    def calculate_metrics(self, legs, underlying_price, iv):
        short_leg = self._get_short_leg(legs)
        long_leg = self._get_long_leg(legs)
        width = short_leg.strike - long_leg.strike
        net_premium = sum(l.net_premium for l in legs)
        
        return StrategyMetrics(
            max_profit=net_premium * 100,
            max_loss=max(0, (width - net_premium) * 100),
            breakevens=[short_leg.strike - net_premium],
            pop=self.calculate_pop(legs, underlying_price, iv),
            expected_value=...  # delegated to calculator
        )

# strategies/registry.py
class StrategyRegistry:
    _calculators: dict[str, StrategyCalculator] = {}
    
    @classmethod
    def register(cls, calculator: StrategyCalculator):
        cls._calculators[calculator.strategy_type] = calculator
    
    @classmethod
    def get(cls, strategy_type: str) -> StrategyCalculator:
        if strategy_type not in cls._calculators:
            raise ValueError(f"Unknown strategy: {strategy_type}")
        return cls._calculators[strategy_type]

# Usage
from strategies.registry import StrategyRegistry

calculator = StrategyRegistry.get(strategy.strategy_type)
metrics = calculator.calculate_metrics(strategy.legs, price, iv)
```

### 4.2 Tight Coupling Between Modules

**Issue:** Direct imports between files create circular dependency risks.

**Current:**
```python
# quant_scanner.py
from spread_conviction_engine import analyse, StrategyType
from regime_detector import RegimeDetector
from vol_forecaster import VolatilityForecaster

# vol_forecaster.py imports yfinance directly
# regime_detector.py imports yfinance directly
```

**Recommended:**

Create a `data_providers/` module:

```python
# data_providers/protocols.py
from typing import Protocol, Optional
from dataclasses import dataclass

@dataclass
class PriceData:
    ticker: str
    price: float
    volume: float
    timestamp: datetime

class PriceProvider(Protocol):
    def get_current_price(self, ticker: str) -> Optional[PriceData]: ...
    def get_historical(self, ticker: str, period: str) -> Optional[pd.DataFrame]: ...

class OptionsProvider(Protocol):
    def get_chain(self, ticker: str, expiration: datetime) -> Optional[OptionChain]: ...
    def get_expirations(self, ticker: str) -> list[datetime]: ...

# data_providers/yfinance_provider.py
class YFinanceProvider:
    def __init__(self, rate_limiter: Optional[RateLimiter] = None):
        self._rate_limiter = rate_limiter or RateLimiter()
    
    def get_current_price(self, ticker: str) -> Optional[PriceData]:
        with self._rate_limiter:
            # implementation
```

### 4.3 Inconsistent Interfaces

**Issue:** `QuantConvictionEngine` exists in both `quant_scanner.py` and `quantitative_integration.py` with different method signatures.

**Current:**
```python
# quant_scanner.py
class QuantConvictionEngine:
    def analyze(self, ticker: str, strategy: str = 'auto') -> Dict[str, Any]: ...

# quantitative_integration.py  
class QuantConvictionEngine:
    def analyze(self, ticker: str, strategy: str = "bull_put",
                period: str = "2y", interval: str = "1d",
                regime_aware: bool = False, vol_aware: bool = False) -> QuantResult: ...
```

**Recommended:**

```python
# engine/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass

@dataclass
class EngineConfig:
    period: str = "2y"
    interval: str = "1d"
    regime_aware: bool = False
    vol_aware: bool = False
    account_value: float = 390.0

@dataclass  
class EngineResult:
    ticker: str
    strategy: str
    conviction_score: float
    tier: str
    metadata: dict[str, Any]

class ConvictionEngine(ABC):
    def __init__(self, config: EngineConfig):
        self.config = config
    
    @abstractmethod
    def analyze(self, ticker: str, strategy: str) -> EngineResult: ...

# engine/quantitative_engine.py
class QuantitativeConvictionEngine(ConvictionEngine):
    """Unified quantitative conviction engine."""
    
    def analyze(self, ticker: str, strategy: str) -> EngineResult:
        # Implementation combining both approaches
        ...
```

---

## 5. Error Handling Issues

### 5.1 Bare Except Clauses

| File | Lines | Issue | Fix |
|------|-------|-------|-----|
| `quant_scanner.py` | 195-200 | `except Exception as e:` catches too broadly | Catch specific exceptions |
| `quant_scanner.py` | 315-320 | `except (TypeError, AttributeError):` | Better, but document why |
| `vol_forecaster.py` | 145-155 | `except Exception as e:` in GARCH fit | Handle specific optimization errors |
| `backtest_validator.py` | 175-180 | `except Exception as e:` in trade simulation | Distinguish data vs logic errors |
| `chain_analyzer.py` | 285-290 | `except:` (bare) in cache loading | At least use `except Exception` |

### 5.2 Silent Failures

| File | Lines | Issue | Fix |
|------|-------|-------|-----|
| `quant_scanner.py` | 185-195 | `_estimate_current_iv()` silently falls through 3 times | Log each fallback level |
| `chain_analyzer.py` | 295-300 | `_save_to_cache()` catches all and ignores | Log cache write failures |
| `leg_optimizer.py` | 525-535 | Strategy metrics returns early with zeros | Return Result with error field |

### 5.3 Missing Input Validation

| File | Lines | Function | Missing Validation |
|------|-------|----------|-------------------|
| `options_math.py` | 65-85 | `d1()` | No check for S <= 0 or K <= 0 |
| `spread_conviction_engine.py` | 285-295 | `fetch_ohlcv()` | No validation of period format |
| `position_sizer.py` | 85-125 | `calculate_position()` | No validation of kelly_fraction range |
| `leg_optimizer.py` | 85-95 | `TradeLeg.__post_init__()` | No validation of option_type values |

**Example Fix:**

```python
# Before (spread_conviction_engine.py:285)
def fetch_ohlcv(ticker: str, period: str = "2y", interval: str = "1d") -> pd.DataFrame:
    if not re.match(r'^[A-Z]{1,5}$', ticker.upper()):
        raise ValueError(f"Invalid ticker: {ticker}")
    df = yf.download(ticker, period=period, interval=interval, progress=False)
    return df

# After
def fetch_ohlcv(ticker: str, period: str = "2y", interval: str = "1d") -> pd.DataFrame:
    # Validate ticker
    if not re.match(r'^[A-Z]{1,5}$', ticker.upper()):
        raise ValueError(f"Invalid ticker format: {ticker}")
    
    # Validate period
    valid_periods = {"1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y", "ytd", "max"}
    if period not in valid_periods:
        raise ValueError(f"Invalid period: {period}. Must be one of {valid_periods}")
    
    # Validate interval
    valid_intervals = {"1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h", "1d", "5d", "1wk", "1mo", "3mo"}
    if interval not in valid_intervals:
        raise ValueError(f"Invalid interval: {interval}")
    
    # Check period/interval compatibility
    if interval in {"1m", "2m", "5m", "15m", "30m", "60m", "90m"} and period not in {"1d", "5d", "1mo"}:
        raise ValueError(f"Intraday intervals only available for periods <= 1mo")
    
    df = yf.download(ticker, period=period, interval=interval, progress=False)
    if df.empty:
        raise DataFetchError(f"No data returned for {ticker} with period={period}, interval={interval}")
    
    return df
```

### 5.4 Missing Timeout Handling

All yfinance calls lack timeout parameters:

```python
# Current (chain_analyzer.py:185)
vix = yf.Ticker(self.vix_ticker)
hist = vix.history(start=start_date, end=end_date)

# Should be
def fetch_with_timeout(ticker, timeout: float = 30.0):
    """Fetch data with timeout protection."""
    import signal
    
    class TimeoutError(Exception):
        pass
    
    def handler(signum, frame):
        raise TimeoutError(f"Data fetch exceeded {timeout}s")
    
    # Set alarm (Unix only; Windows needs different approach)
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(int(timeout))
    
    try:
        tk = yf.Ticker(ticker)
        hist = tk.history(start=start_date, end=end_date)
        return hist
    finally:
        signal.alarm(0)  # Cancel alarm
```

---

## 6. Performance Issues

### 6.1 Inefficient Loops

| File | Lines | Issue | Optimization |
|------|-------|-------|--------------|
| `leg_optimizer.py` | 585-785 | Nested loops over options chain with repeated calculations | Pre-calculate valid options, use list comprehensions |
| `backtest_validator.py` | 165-225 | Walk-forward loop creates new DataFrame for each date | Vectorized operations or caching |
| `options_math.py` | 185-215 | Monte Carlo loop could be vectorized | Use numpy broadcasting |

### 6.2 Redundant API Calls

| File | Lines | Issue | Solution |
|------|-------|-------|----------|
| `regime_detector.py` | 95-125 | VIX data fetched separately from stock data | Batch data fetches |
| `quant_scanner.py` | 385-395, 405-415 | Quote fetched, then chain fetched separately | Unified fetch operation |
| `vol_forecaster.py` | 95-115 | Returns fetched separately per ticker | Cache per session |

### 6.3 No Caching of Expensive Computations

```python
# Add to options_math.py or create caching module
from functools import lru_cache
import hashlib

class ComputationCache:
    """Disk-backed cache for expensive computations."""
    
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
    
    def _get_key(self, func_name: str, args: tuple, kwargs: dict) -> str:
        """Generate cache key from function arguments."""
        key_str = f"{func_name}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def get_or_compute(self, func, *args, ttl: int = 3600, **kwargs):
        """Get cached result or compute and cache."""
        key = self._get_key(func.__name__, args, kwargs)
        cache_file = self.cache_dir / f"{key}.pkl"
        
        # Check cache
        if cache_file.exists():
            import time
            if time.time() - cache_file.stat().st_mtime < ttl:
                with open(cache_file, 'rb') as f:
                    return pickle.load(f)
        
        # Compute and cache
        result = func(*args, **kwargs)
        with open(cache_file, 'wb') as f:
            pickle.dump(result, f)
        
        return result

# Usage
from options_math import ProbabilityCalculator

cache = ComputationCache()
calc = ProbabilityCalculator()

# Cached GARCH fitting
result = cache.get_or_compute(
    calc.fit_garch, 
    returns_series, 
    ttl=86400  # Cache for 1 day
)
```

### 6.4 Memory Leaks

| File | Lines | Issue | Fix |
|------|-------|-------|-----|
| `quant_scanner.py` | 145-155 | `_vix_cache` and `_cache_date` could grow unbounded | Use LRU cache with maxsize |
| `leg_optimizer.py` | 125-130 | `historical_vols` dict never cleared | Clear after use or use TTL |

---

## 7. Type Safety Issues

### 7.1 Missing Type Hints

**File-by-file coverage:**

| File | Lines | Missing Type Hints | % Coverage |
|------|-------|-------------------|------------|
| `quant_scanner.py` | 423 | 180 lines | ~57% |
| `spread_conviction_engine.py` | 1795 | 650 lines | ~64% |
| `leg_optimizer.py` | 1454 | 580 lines | ~60% |
| `multi_leg_strategies.py` | 1688 | 720 lines | ~57% |
| `options_math.py` | 700 | 280 lines | ~60% |
| `chain_analyzer.py` | 400 | 120 lines | ~70% |

**Priority fixes:**

```python
# Before (common pattern in codebase)
def calculate_strategy_metrics(self, strategy, iv=0.25):
    ...

# After  
def calculate_strategy_metrics(
    self, 
    strategy: MultiLegStrategy, 
    iv: float = 0.25
) -> MultiLegStrategy:
    """Calculate all metrics for a strategy.
    
    Args:
        strategy: The strategy to analyze
        iv: Implied volatility estimate (annualized, decimal)
        
    Returns:
        Strategy with populated metrics
        
    Raises:
        ValueError: If strategy has no legs
    """
    ...
```

### 7.2 Using `Any` When Specific Type Possible

| File | Lines | Current | Should Be |
|------|-------|---------|-----------|
| `quant_scanner.py` | 195 | `-> Dict[str, Any]` | `-> Dict[str, Union[str, float, Dict]]` |
| `quantitative_integration.py` | 145 | `existing_positions: List[Dict]` | `List[PositionCorrelation]` |
| `backtest_validator.py` | 55 | `conviction_engine: Any` | `ConvictionEngine` (Protocol) |

### 7.3 Incorrect Type Hints

| File | Lines | Issue | Fix |
|------|-------|-------|-----|
| `options_math.py` | 95 | `n_sims: int = 100000` OK, but docstring says default 10000 | Align docstring |
| `position_sizer.py` | 85 | `pop: float = 0.0` but should be constrained to [0,1] | Use `Annotated[float, Interval(ge=0, le=1)]` with pydantic |

---

## 8. Documentation Issues

### 8.1 Missing Docstrings

| File | Function/Class | Missing Elements |
|------|----------------|------------------|
| `quant_scanner.py` | `QuantConvictionEngine._estimate_pop()` | All documentation |
| `quant_scanner.py` | `QuantConvictionEngine._is_regime_favorable()` | Args, returns |
| `leg_optimizer.py` | `LegOptimizer.optimize_iron_condors()` | Detailed parameters |
| `multi_leg_strategies.py` | `score_iron_condor()` | Algorithm explanation |

### 8.2 Outdated Docstrings

| File | Line(s) | Issue |
|------|---------|-------|
| `spread_conviction_engine.py` | 45-55 | Version says 2.0.0 but constants still use v1.x values |
| `backtest_validator.py` | 75-85 | References "White (2000)" but implementation differs |

### 8.3 Unclear Parameter Descriptions

```python
# Before (leg_optimizer.py)
def calculate_strategy_metrics(self, strategy: MultiLegStrategy,
                               iv: float = 0.25) -> MultiLegStrategy:
    """Calculate all metrics for a strategy"""

# After
def calculate_strategy_metrics(
    self, 
    strategy: MultiLegStrategy,
    iv: float = 0.25
) -> MultiLegStrategy:
    """Calculate P&L metrics, POP, Greeks, and account fit for a strategy.
    
    Args:
        strategy: MultiLegStrategy with populated legs. Must have at least
                 2 legs for spreads, 4 for iron condors.
        iv: Implied volatility estimate for probability calculations.
            Should be annualized decimal (e.g., 0.25 for 25% IV).
            Used for Black-Scholes POP calculation.
            
    Returns:
        The same strategy object with populated fields:
        - max_profit: Maximum possible profit in dollars
        - max_loss: Maximum possible loss in dollars (always >= 0)
        - breakevens: List of breakeven underlying prices
        - pop: Probability of profit [0, 1]
        - expected_value: Risk-adjusted expected P&L
        
    Raises:
        ValueError: If strategy has no legs or invalid construction
    """
```

---

## 9. Refactoring Priority Queue

### P0 (Critical) — Must Fix Immediately

1. **Consolidate Kelly Criterion Implementations**
   - **Effort:** 4 hours
   - **Risk:** Current state risks inconsistent position sizing decisions
   - **Action:** Create `position_sizing/kelly.py`, migrate all implementations

2. **Merge Duplicate QuantConvictionEngine Classes**
   - **Effort:** 6 hours
   - **Risk:** Users get different behavior depending on import path
   - **Action:** Audit both implementations, merge features, deprecate one

3. **Add Input Validation to Public APIs**
   - **Effort:** 3 hours
   - **Risk:** Silent failures produce incorrect trading recommendations
   - **Action:** Add validation layer to all user-facing entry points

### P1 (High) — Fix This Week

4. **Replace Bare Except Clauses**
   - **Effort:** 2 hours
   - **Action:** Audit all `except:` and `except Exception:` patterns

5. **Extract Strategy Pattern for Calculators**
   - **Effort:** 8 hours
   - **Action:** Create `strategies/` package with base class and implementations

6. **Add Type Hints to Public Interfaces**
   - **Effort:** 6 hours
   - **Action:** Focus on entry points: `analyse()`, `calculate_position()`, `scan_ticker()`

7. **Create Data Provider Abstraction**
   - **Effort:** 5 hours
   - **Action:** Extract yfinance dependencies behind protocol

### P2 (Medium) — Fix Next Sprint

8. **Consolidate Constants**
   - **Effort:** 3 hours
   - **Action:** Single `constants.py` module with all magic numbers

9. **Implement Proper Caching Layer**
   - **Effort:** 6 hours
   - **Action:** Disk-backed LRU cache for expensive computations

10. **Extract Scoring Tables to Configuration**
    - **Effort:** 4 hours
    - **Action:** JSON/YAML config for RSI/MACD/%B scoring tables

11. **Add Timeout Handling to Network Calls**
    - **Effort:** 3 hours
    - **Action:** Wrapper for all yfinance calls

### P3 (Low) — Nice to Have

12. **Full Type Hint Coverage**
    - **Effort:** 12 hours

13. **Comprehensive Docstring Updates**
    - **Effort:** 8 hours

14. **Performance Optimization (Vectorization)**
    - **Effort:** 10 hours

---

## 10. Consolidation Opportunities

### 10.1 Files That Should Be Merged

| Files | Merge Target | Rationale |
|-------|--------------|-----------|
| `position_sizer.py` + `enhanced_kelly.py` + `options_math.py` (Kelly parts) | `position_sizing/` package | Single responsibility: position sizing |
| `quant_scanner.py` + `quantitative_integration.py` | `scanner/quantitative.py` | Single unified scanner |
| `spread_conviction_engine.py` + `multi_leg_strategies.py` | `conviction/` package | Conviction scoring strategies |
| `calculator.py` + `options_math.py` (strategy parts) | `strategies/calculators.py` | Strategy P&L calculations |

### 10.2 New Module Structure Recommended

```
options-spread-conviction-engine/
├── __init__.py
├── cli.py                      # Entry points
├── config/
│   ├── __init__.py
│   ├── constants.py            # All magic numbers
│   └── scoring_tables.py       # JSON scoring configurations
├── conviction/
│   ├── __init__.py
│   ├── base.py                 # ConvictionEngine ABC
│   ├── vertical_spreads.py     # Current spread_conviction_engine
│   ├── multi_leg.py            # Current multi_leg_strategies
│   └── quantitative.py         # QuantConvictionEngine
├── data/
│   ├── __init__.py
│   ├── protocols.py            # Provider protocols
│   ├── yfinance_provider.py    # Yahoo Finance implementation
│   └── cache.py                # Caching layer
├── position_sizing/
│   ├── __init__.py
│   ├── kelly.py                # Unified Kelly implementation
│   ├── sizer.py                # Position sizing logic
│   └── constraints.py          # Account constraint validation
├── strategies/
│   ├── __init__.py
│   ├── base.py                 # StrategyCalculator ABC
│   ├── registry.py             # Strategy lookup
│   ├── vertical_spreads.py     # Put/call credit/debit calculators
│   ├── iron_condor.py          # IC calculator
│   └── butterfly.py            # Butterfly calculator
├── analysis/
│   ├── __init__.py
│   ├── regime.py               # Regime detection
│   ├── volatility.py           # Vol forecasting
│   └── backtest.py             # Validation framework
└── utils/
    ├── __init__.py
    ├── math_helpers.py
    └── validation.py
```

### 10.3 Shared Utilities to Extract

| Utility | Current Location(s) | New Location |
|---------|---------------------|--------------|
| Ticker validation regex | `quant_scanner.py`, `spread_conviction_engine.py` | `utils/validation.py` |
| Rate limiting | `chain_analyzer.py`, `vol_forecaster.py` | `data/rate_limiter.py` |
| Risk-free rate | Multiple files | `config/constants.py` |
| IV floor validation | `leg_optimizer.py`, `options_math.py` | `utils/validation.py` |
| Account constraint checks | `options_math.py`, `leg_optimizer.py` | `position_sizing/constraints.py` |

---

## 11. Specific Code Examples

### 11.1 Before/After: Position Sizing Consolidation

**Before (3 files, inconsistent):**

```python
# position_sizer.py
def calculate_position(account_value, max_loss_per_spread, ...):
    full_kelly = kelly_criterion(pop, win_amount, max_loss_per_spread)
    # ... 60 more lines

# enhanced_kelly.py  
class EnhancedKellySizer:
    def kelly_criterion(self, win_prob, win_amount, loss_amount):
        odds = win_amount / loss_amount
        kelly = (win_prob * odds - loss_prob) / odds
        return kelly, edge
    # ... different calculation!

# options_math.py
def kelly_position_size(pop, max_profit, max_loss, ...):
    f_full = kelly_fraction(pop, b)
    # ... different API entirely
```

**After (unified):**

```python
# position_sizing/kelly.py
from dataclasses import dataclass
from enum import Enum, auto
from typing import Optional
import numpy as np

class KellyVariant(Enum):
    """Kelly fraction variants for risk management."""
    FULL = (1.0, "aggressive")
    HALF = (0.5, "moderate")
    QUARTER = (0.25, "conservative")
    EIGHTH = (0.125, "very_conservative")
    
    def __init__(self, multiplier: float, description: str):
        self.multiplier = multiplier
        self.description = description

@dataclass(frozen=True)
class TradeParameters:
    """Validated trade parameters for Kelly calculation."""
    win_probability: float
    win_amount: float
    loss_amount: float
    
    def __post_init__(self):
        if not 0 <= self.win_probability <= 1:
            raise ValueError(f"win_probability must be in [0,1]")
        if self.win_amount <= 0:
            raise ValueError(f"win_amount must be positive")
        if self.loss_amount <= 0:
            raise ValueError(f"loss_amount must be positive")
    
    @property
    def odds(self) -> float:
        """Calculate odds ratio (b in Kelly formula)."""
        return self.win_amount / self.loss_amount
    
    @property
    def expected_value(self) -> float:
        """Calculate expected value of trade."""
        q = 1 - self.win_probability
        return self.win_probability * self.win_amount - q * self.loss_amount
    
    @property
    def edge(self) -> float:
        """Edge as percentage of risk."""
        return self.expected_value / self.loss_amount

@dataclass(frozen=True)
class KellyResult:
    """Result of Kelly criterion calculation."""
    raw_fraction: float           # f* (can be negative)
    adjusted_fraction: float      # After variant and cap
    variant_used: KellyVariant
    max_fraction_cap: float
    edge: float
    expected_value: float
    is_favorable: bool            # True if raw_fraction > 0
    
    def get_contracts(self, account_value: float, 
                      max_risk_per_trade: float) -> int:
        """Calculate integer contract count."""
        risk_dollars = self.adjusted_fraction * account_value
        risk_dollars = min(risk_dollars, max_risk_per_trade)
        return max(0, int(risk_dollars // self.loss_amount))

class KellyCriterion:
    """Unified Kelly criterion calculator."""
    
    DEFAULT_MAX_FRACTION = 0.25
    
    @classmethod
    def calculate(
        cls,
        params: TradeParameters,
        variant: KellyVariant = KellyVariant.HALF,
        max_fraction: Optional[float] = None,
        existing_correlation: float = 0.0
    ) -> KellyResult:
        """Calculate Kelly fraction with full validation.
        
        Args:
            params: Validated trade parameters
            variant: Kelly fraction variant (default: Half Kelly)
            max_fraction: Hard cap on fraction (default: 0.25)
            existing_correlation: Correlation with existing positions [0,1]
            
        Returns:
            KellyResult with all calculations
        """
        max_fraction = max_fraction or cls.DEFAULT_MAX_FRACTION
        
        # Raw Kelly: f* = (p*b - q) / b
        q = 1 - params.win_probability
        b = params.odds
        f_star = (params.win_probability * b - q) / b if b > 0 else 0.0
        
        # Apply correlation adjustment
        correlation_factor = 1 - (existing_correlation * 0.5)
        f_adjusted = f_star * variant.multiplier * correlation_factor
        
        # Apply hard cap
        f_adjusted = max(0.0, min(f_adjusted, max_fraction))
        
        return KellyResult(
            raw_fraction=f_star,
            adjusted_fraction=f_adjusted,
            variant_used=variant,
            max_fraction_cap=max_fraction,
            edge=params.edge,
            expected_value=params.expected_value,
            is_favorable=f_star > 0
        )

# Legacy compatibility functions
def kelly_criterion(pop: float, win_amount: float, loss_amount: float) -> float:
    """Legacy compatibility: returns raw Kelly fraction only."""
    params = TradeParameters(win_probability=pop, 
                            win_amount=win_amount, 
                            loss_amount=loss_amount)
    result = KellyCriterion.calculate(params, variant=KellyVariant.FULL)
    return result.raw_fraction
```

### 11.2 Before/After: Error Handling

**Before:**

```python
# quant_scanner.py (lines 185-200)
def _estimate_current_iv(self, ticker: str, forecaster: VolatilityForecaster) -> float:
    try:
        fetcher = ChainFetcher(rate_limit_delay=0.1)
        quote = fetcher.fetch_quote(ticker)
        if quote and 'impliedVolatility' in quote:
            return quote['impliedVolatility'] * 100
    except:
        pass
    
    if forecaster._garch_result:
        rv = forecaster._garch_result.fitted_vol.iloc[-1]
        return rv + 2.5
    
    return 20.0
```

**After:**

```python
# quant_scanner.py
def _estimate_current_iv(
    self, 
    ticker: str, 
    forecaster: VolatilityForecaster,
    logger: Optional[logging.Logger] = None
) -> float:
    """Estimate current implied volatility with fallback chain.
    
    Tries multiple estimation methods in order:
    1. Live options quote IV (most accurate)
    2. GARCH forecast + typical VRP (2-3%)
    3. Default assumption (20%)
    
    Args:
        ticker: Stock symbol
        forecaster: Volatility forecaster with potential GARCH fit
        logger: Optional logger for debugging
        
    Returns:
        Estimated IV as percentage (e.g., 25.0 for 25%)
    """
    log = logger or logging.getLogger(__name__)
    
    # Attempt 1: Live options quote
    try:
        fetcher = ChainFetcher(rate_limit_delay=0.1)
        quote = fetcher.fetch_quote(ticker)
        if quote and quote.get('impliedVolatility'):
            iv = quote['impliedVolatility'] * 100
            log.debug(f"IV from options quote for {ticker}: {iv:.1f}%")
            return iv
        log.debug(f"No IV in quote for {ticker}")
    except DataFetchError as e:
        log.warning(f"Failed to fetch options quote for {ticker}: {e}")
    except Exception as e:
        log.error(f"Unexpected error fetching IV for {ticker}: {e}")
    
    # Attempt 2: GARCH forecast + typical VRP
    if forecaster._garch_result is not None:
        try:
            rv = forecaster._garch_result.fitted_vol.iloc[-1]
            typical_vrp = 2.5  # Historical average VRP
            estimated_iv = rv + typical_vrp
            log.debug(f"IV from GARCH+VRP for {ticker}: {estimated_iv:.1f}%")
            return estimated_iv
        except (AttributeError, IndexError) as e:
            log.warning(f"GARCH result incomplete for {ticker}: {e}")
    
    # Attempt 3: Default assumption
    default_iv = 20.0
    log.warning(f"Using default IV for {ticker}: {default_iv}%")
    return default_iv
```

---

## 12. Summary

The Options Spread Conviction Engine is a sophisticated quantitative trading tool with solid mathematical underpinnings. The main issues are:

1. **Accumulated Technical Debt:** Multiple development phases have left duplicate implementations scattered across files
2. **Inconsistent Interfaces:** Similar classes with different APIs create confusion
3. **Insufficient Abstraction:** Strategy calculations embedded in if/elif chains rather than proper strategy pattern
4. **Error Handling Gaps:** Silent failures and bare except clauses create maintenance risk

The recommended refactoring focuses on:
1. **Consolidation** (P0) — Merge duplicate Kelly and engine implementations
2. **Abstraction** (P1) — Extract strategy pattern and data providers
3. **Validation** (P1) — Add proper input validation and error handling
4. **Type Safety** (P2) — Comprehensive type hints for maintainability

Estimated total effort: **80-110 hours** for full refactoring, but **16 hours** for critical P0 fixes that would significantly improve code health.

---

*Report generated by OpenClaw Subagent*  
*Review based on codebase state as of February 13, 2026*
