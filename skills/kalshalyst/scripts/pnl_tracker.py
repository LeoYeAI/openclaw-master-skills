"""Live P&L tracking system for OpenClaw Prediction Stack.

Tracks actual trading performance vs predicted edge across Kalshi markets.
Integrates with Kalshalyst (estimation), Kelly sizing (position sizing), and
Kalshi API (execution & resolution).

Key features:
  - JSONL trade log (append-only, crash-safe)
  - Live P&L calculation (realized + unrealized)
  - Sharpe ratio and max drawdown tracking
  - Win rate vs predicted edge analysis
  - Integration hooks for auto-logging from Kalshalyst/Kelly
  - Real-time portfolio snapshot from Kalshi API
  - Trade history and fills from Kalshi
  - Live P&L metrics (cash, positions, unrealized value)
  - CLI interface for manual logging and reporting
  - Slack-ready portfolio summary export

Usage (Manual Logging):
  python3 pnl_tracker.py log --ticker TICKER --side yes --price 45 --est 0.62 \\
    --contracts 5 --cost 2.25 --confidence 0.7
  python3 pnl_tracker.py resolve --ticker TICKER --outcome 1
  python3 pnl_tracker.py summary
  python3 pnl_tracker.py export [--format csv|json]

Usage (Live Kalshi Tracking):
  python3 pnl_tracker.py portfolio        # Show current portfolio snapshot
  python3 pnl_tracker.py pnl [--hours 24] # Show live P&L report

State Files:
  ~/.openclaw/trade_log.json               # Manual trade log (JSONL)
  ~/.openclaw/logs/portfolio_snapshots.jsonl  # Auto-appended portfolio snapshots
"""

from __future__ import annotations

import json
import logging
import math
import argparse
import csv
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Optional, Literal
from collections import defaultdict
from dataclasses import asdict, dataclass

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] pnl_tracker: %(message)s'
)
logger = logging.getLogger(__name__)


# ── Paths & Imports ────────────────────────────────────────────────────────

TRADE_LOG_PATH = Path.home() / ".openclaw" / "trade_log.json"
PORTFOLIO_SNAPSHOTS_PATH = Path.home() / ".openclaw" / "logs" / "portfolio_snapshots.jsonl"
TRADING_DAYS_PER_YEAR = 250  # Standard assumption for Sharpe ratio

# Setup path to import kalshi_commands from sibling skill
SCRIPT_DIR = Path(__file__).resolve().parent
KALSHI_CMD_DIR = SCRIPT_DIR.parent.parent / "kalshi-command-center" / "scripts"
if str(KALSHI_CMD_DIR) not in sys.path:
    sys.path.insert(0, str(KALSHI_CMD_DIR))


# ── Data Models ────────────────────────────────────────────────────────────

@dataclass
class Trade:
    """A single trade record."""
    # Entry metadata
    id: str  # UUID or incremental ID
    timestamp: str  # ISO 8601
    ticker: str
    title: str
    side: Literal["yes", "no"]
    market_price_cents: int
    estimated_prob: float
    edge_pct: float
    contracts: int
    cost_usd: float
    confidence: float

    # Resolution (filled after outcome)
    outcome: Optional[int] = None  # 0=NO, 1=YES, None=unresolved
    resolved_at: Optional[str] = None
    pnl_usd: Optional[float] = None
    pnl_pct: Optional[float] = None
    actual_edge: Optional[float] = None  # actual prob - market prob
    category: Optional[str] = None  # e.g., "technology", "fed", "policy"

    def to_dict(self) -> dict:
        """Convert to JSON-serializable dict."""
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> Trade:
        """Reconstruct from dict."""
        return cls(**d)

    def is_resolved(self) -> bool:
        """Check if trade has been resolved."""
        return self.outcome is not None

    def calculate_pnl(self, outcome: int) -> tuple[float, float]:
        """Calculate P&L and P&L% given outcome (0 or 1).

        Args:
            outcome: 0 for NO resolution, 1 for YES resolution

        Returns:
            (pnl_usd, pnl_pct)
        """
        if outcome not in (0, 1):
            raise ValueError(f"Outcome must be 0 or 1, got {outcome}")

        cost_cents = self.market_price_cents if self.side == "yes" else (100 - self.market_price_cents)
        cost_per_contract = cost_cents / 100.0

        if self.side == "yes":
            # YES contract: profit if outcome=1
            win = outcome == 1
        else:
            # NO contract: profit if outcome=0
            win = outcome == 0

        if win:
            # Profit is (100 - cost_cents) per contract
            profit_cents = (100 - cost_cents) if self.side == "yes" else cost_cents
            pnl_usd = self.contracts * (profit_cents / 100.0)
        else:
            # Loss is cost_cents per contract
            pnl_usd = -self.contracts * cost_per_contract

        pnl_pct = (pnl_usd / self.cost_usd) * 100 if self.cost_usd > 0 else 0

        return pnl_usd, pnl_pct


# ── Trade Logger ───────────────────────────────────────────────────────────

class TradeLogger:
    """Manages append-only JSONL trade log."""

    def __init__(self, log_path: Optional[Path] = None):
        """Initialize trade logger.

        Args:
            log_path: Path to trade log file (default: ~/.openclaw/trade_log.json)
        """
        self.log_path = log_path or TRADE_LOG_PATH
        self.log_path.parent.mkdir(parents=True, exist_ok=True)

    def log_trade(
        self,
        ticker: str,
        title: str,
        side: str,
        market_price_cents: int,
        estimated_prob: float,
        edge_pct: float,
        contracts: int,
        cost_usd: float,
        confidence: float,
        category: Optional[str] = None,
        timestamp: Optional[str] = None,
    ) -> Trade:
        """Log a new trade to the trade log.

        Args:
            ticker: Market ticker (e.g., "KXPOL-2024-USPRES")
            title: Market title
            side: "yes" or "no"
            market_price_cents: Entry price in cents (1-99)
            estimated_prob: Model's estimated probability (0-1)
            edge_pct: Predicted edge percentage
            contracts: Number of contracts
            cost_usd: Total cost in USD
            confidence: Model confidence (0-1)
            category: Market category (optional)
            timestamp: ISO 8601 timestamp (default: now)

        Returns:
            Trade record
        """
        timestamp = timestamp or datetime.now(timezone.utc).isoformat()
        trade_id = f"{ticker}_{timestamp.replace(':', '').replace('-', '').replace('.', '')}"

        trade = Trade(
            id=trade_id,
            timestamp=timestamp,
            ticker=ticker,
            title=title,
            side=side.lower(),
            market_price_cents=market_price_cents,
            estimated_prob=estimated_prob,
            edge_pct=edge_pct,
            contracts=contracts,
            cost_usd=cost_usd,
            confidence=confidence,
            category=category,
        )

        # Append to JSONL
        with open(self.log_path, "a") as f:
            f.write(json.dumps(trade.to_dict()) + "\n")

        logger.info(f"Logged: {ticker} | {side.upper()} @ {market_price_cents}¢ | {contracts}x | ${cost_usd:.2f}")
        return trade

    def load_trades(self) -> list[Trade]:
        """Load all trades from log.

        Returns:
            List of Trade objects
        """
        if not self.log_path.exists():
            return []

        trades = []
        with open(self.log_path, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    trades.append(Trade.from_dict(data))
                except json.JSONDecodeError as e:
                    logger.error(f"Corrupt trade record: {e}")
                    continue

        return trades

    def resolve_trade(self, ticker: str, outcome: int) -> Trade:
        """Resolve a trade by ticker and update log with outcome.

        Args:
            ticker: Market ticker
            outcome: 0 for NO, 1 for YES

        Returns:
            Updated Trade record

        Raises:
            ValueError: If trade not found or already resolved
        """
        trades = self.load_trades()
        resolved_trade = None

        # Find most recent unresolved trade with this ticker
        for trade in reversed(trades):
            if trade.ticker == ticker and not trade.is_resolved():
                resolved_trade = trade
                break

        if not resolved_trade:
            raise ValueError(f"No unresolved trade found for {ticker}")

        # Calculate P&L
        pnl_usd, pnl_pct = resolved_trade.calculate_pnl(outcome)

        # Update trade record
        resolved_trade.outcome = outcome
        resolved_trade.resolved_at = datetime.now(timezone.utc).isoformat()
        resolved_trade.pnl_usd = pnl_usd
        resolved_trade.pnl_pct = pnl_pct

        # Calculate actual edge vs predicted
        market_prob = resolved_trade.market_price_cents / 100.0
        actual_prob = float(outcome)
        resolved_trade.actual_edge = (actual_prob - market_prob) * 100

        # Rewrite log with updated trade
        with open(self.log_path, "w") as f:
            for trade in trades:
                if trade.id == resolved_trade.id:
                    f.write(json.dumps(resolved_trade.to_dict()) + "\n")
                else:
                    f.write(json.dumps(trade.to_dict()) + "\n")

        logger.info(
            f"Resolved: {ticker} → {outcome} (YES)" if outcome == 1 else f"Resolved: {ticker} → {outcome} (NO) | "
            f"P&L: ${pnl_usd:+.2f} ({pnl_pct:+.1f}%)"
        )

        return resolved_trade


# ── Portfolio Analytics ────────────────────────────────────────────────────

class PortfolioAnalyzer:
    """Analyze portfolio performance across trades."""

    def __init__(self, trades: list[Trade]):
        """Initialize analyzer with trade list.

        Args:
            trades: List of Trade objects
        """
        self.trades = trades
        self.resolved = [t for t in trades if t.is_resolved()]
        self.open = [t for t in trades if not t.is_resolved()]

    def realized_pnl(self) -> float:
        """Total realized P&L in USD."""
        return sum(t.pnl_usd or 0 for t in self.resolved)

    def unrealized_pnl(self) -> float:
        """Unrealized P&L for open trades (current value at market midpoint)."""
        pnl = 0
        for trade in self.open:
            # Assume midpoint between entry and max profit
            cost_cents = trade.market_price_cents if trade.side == "yes" else (100 - trade.market_price_cents)
            midpoint_value = cost_cents / 100.0
            current_value = trade.contracts * midpoint_value

            # P&L = current value - cost
            pnl += current_value - trade.cost_usd

        return pnl

    def total_pnl(self) -> float:
        """Total P&L (realized + unrealized)."""
        return self.realized_pnl() + self.unrealized_pnl()

    def win_rate(self) -> float:
        """Percentage of resolved trades that were profitable."""
        if not self.resolved:
            return 0.0
        wins = sum(1 for t in self.resolved if (t.pnl_usd or 0) > 0)
        return (wins / len(self.resolved)) * 100

    def avg_predicted_edge(self) -> float:
        """Average predicted edge across all trades."""
        if not self.trades:
            return 0.0
        return sum(t.edge_pct for t in self.trades) / len(self.trades)

    def avg_actual_edge(self) -> float:
        """Average actual edge (outcome - market price) across resolved trades."""
        if not self.resolved:
            return 0.0
        return sum(t.actual_edge or 0 for t in self.resolved) / len(self.resolved)

    def sharpe_ratio(self) -> float:
        """Annualized Sharpe ratio of realized P&L.

        Assumes daily returns based on trade resolution dates.
        """
        if len(self.resolved) < 2:
            return 0.0

        # Sort by resolution date
        sorted_trades = sorted(self.resolved, key=lambda t: t.resolved_at or "")

        # Calculate daily returns (approximate: assume one trade per day)
        daily_returns = [t.pnl_pct or 0 for t in sorted_trades]

        if not daily_returns or all(r == 0 for r in daily_returns):
            return 0.0

        mean_return = sum(daily_returns) / len(daily_returns)
        variance = sum((r - mean_return) ** 2 for r in daily_returns) / len(daily_returns)
        std_dev = math.sqrt(variance)

        if std_dev == 0:
            return 0.0

        # Annualized Sharpe (assuming risk-free rate = 0)
        sharpe = (mean_return / std_dev) * math.sqrt(TRADING_DAYS_PER_YEAR)
        return sharpe

    def max_drawdown(self) -> float:
        """Maximum drawdown percentage.

        Tracks cumulative P&L and calculates largest peak-to-trough decline.
        """
        if not self.resolved:
            return 0.0

        sorted_trades = sorted(self.resolved, key=lambda t: t.resolved_at or "")
        cumulative_pnl = 0
        peak_pnl = 0
        max_dd = 0

        for trade in sorted_trades:
            cumulative_pnl += (trade.pnl_usd or 0)
            if cumulative_pnl > peak_pnl:
                peak_pnl = cumulative_pnl

            drawdown = peak_pnl - cumulative_pnl
            if drawdown > max_dd:
                max_dd = drawdown

        return max_dd

    def pnl_by_category(self) -> dict[str, dict]:
        """P&L breakdown by market category."""
        by_cat = defaultdict(lambda: {"trades": 0, "pnl": 0.0, "win_rate": 0.0})

        for trade in self.resolved:
            cat = trade.category or "uncategorized"
            by_cat[cat]["trades"] += 1
            by_cat[cat]["pnl"] += trade.pnl_usd or 0

        # Calculate win rates per category
        category_trades = defaultdict(list)
        for trade in self.resolved:
            cat = trade.category or "uncategorized"
            category_trades[cat].append(trade)

        for cat, trades in category_trades.items():
            wins = sum(1 for t in trades if (t.pnl_usd or 0) > 0)
            by_cat[cat]["win_rate"] = (wins / len(trades)) * 100 if trades else 0

        return dict(by_cat)

    def best_worst_trades(self, limit: int = 5) -> tuple[list[Trade], list[Trade]]:
        """Return best and worst trades.

        Args:
            limit: Number of trades to return in each list

        Returns:
            (best_trades, worst_trades) sorted by P&L
        """
        sorted_by_pnl = sorted(self.resolved, key=lambda t: t.pnl_usd or 0, reverse=True)
        best = sorted_by_pnl[:limit]
        worst = sorted_by_pnl[-limit:][::-1]

        return best, worst

    def summary(self) -> dict:
        """Generate comprehensive portfolio summary.

        Returns:
            Dict with all key metrics
        """
        return {
            "total_trades": len(self.trades),
            "resolved_trades": len(self.resolved),
            "open_trades": len(self.open),
            "realized_pnl_usd": round(self.realized_pnl(), 2),
            "unrealized_pnl_usd": round(self.unrealized_pnl(), 2),
            "total_pnl_usd": round(self.total_pnl(), 2),
            "win_rate_pct": round(self.win_rate(), 1),
            "avg_predicted_edge_pct": round(self.avg_predicted_edge(), 2),
            "avg_actual_edge_pct": round(self.avg_actual_edge(), 2),
            "sharpe_ratio": round(self.sharpe_ratio(), 3),
            "max_drawdown_usd": round(self.max_drawdown(), 2),
            "pnl_by_category": self.pnl_by_category(),
        }


# ── Integration Hooks ──────────────────────────────────────────────────────

def auto_log_from_edge(edge_result: dict, kelly_result: dict, log_path: Optional[Path] = None) -> Trade:
    """Auto-log a trade from Kalshalyst edge result + Kelly sizing.

    Convenience function to integrate with the pipeline:
      edges = calculate_edges(markets, cfg)
      for edge in edges:
          kelly = kelly_from_edge_result(edge, bankroll_usd=200)
          pnl_tracker.auto_log_from_edge(edge, kelly)

    Args:
        edge_result: Dict from calculate_edges() with keys:
          ticker, title, estimated_probability, market_implied (price),
          effective_edge_pct, direction, confidence, category
        kelly_result: KellyResult from kelly_size() or kelly_from_edge_result()
        log_path: Optional path override

    Returns:
        Logged Trade record
    """
    direction = edge_result.get("direction", "fair")
    side = "yes" if direction == "underpriced" else "no"

    logger = TradeLogger(log_path)
    return logger.log_trade(
        ticker=edge_result.get("ticker", "UNKNOWN"),
        title=edge_result.get("title", ""),
        side=side,
        market_price_cents=int(edge_result.get("market_implied", 50) * 100),
        estimated_prob=edge_result.get("estimated_probability", 0.5),
        edge_pct=edge_result.get("effective_edge_pct", 0),
        contracts=kelly_result.contracts,
        cost_usd=kelly_result.cost_usd,
        confidence=edge_result.get("confidence", 0),
        category=edge_result.get("category", edge_result.get("series_ticker")),
    )


def auto_resolve_from_kalshi(client, log_path: Optional[Path] = None) -> list[Trade]:
    """Auto-resolve trades from Kalshi API for resolved markets.

    Polls Kalshi API for market resolutions and updates trade log.

    Args:
        client: Initialized Kalshi API client
        log_path: Optional path override

    Returns:
        List of resolved Trade records
    """
    import json as json_module

    logger_obj = TradeLogger(log_path)
    trades = logger_obj.load_trades()
    open_trades = [t for t in trades if not t.is_resolved()]

    if not open_trades:
        logger.info("No open trades to resolve")
        return []

    resolved_trades = []

    for trade in open_trades:
        try:
            # Query Kalshi API for market status
            url = f"https://api.elections.kalshi.com/trade-api/v2/markets/{trade.ticker}"
            resp = client.call_api("GET", url)
            market_data = json_module.loads(resp.read())

            # Check if resolved
            if market_data.get("status") == "resolved":
                outcome_str = market_data.get("yes_bid")  # YES resolves to 100, NO to 0
                # (Adjust based on actual Kalshi API response format)
                outcome = 1 if outcome_str == 100 else 0

                resolved = logger_obj.resolve_trade(trade.ticker, outcome)
                resolved_trades.append(resolved)

        except Exception as e:
            logger.warning(f"Could not resolve {trade.ticker}: {e}")
            continue

    return resolved_trades


# ── Real-Time Portfolio Functions (Kalshi Integration) ─────────────────────

def get_portfolio_snapshot(client) -> dict:
    """Get current portfolio state from Kalshi API.

    Returns:
        {
            "timestamp": ISO timestamp,
            "cash_balance": float (USD),
            "positions": [
                {
                    "ticker": str,
                    "qty": int (positive=YES, negative=NO),
                    "side": "yes" | "no",
                    "market_price_cents": int (estimated current price)
                }
            ],
            "total_portfolio_value": float (cash + unrealized position value),
            "open_order_count": int,
            "error": Optional[str] (if fetch failed)
        }
    """
    snapshot = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "cash_balance": 0.0,
        "positions": [],
        "total_portfolio_value": 0.0,
        "open_order_count": 0,
        "error": None,
    }

    try:
        # Get cash balance
        try:
            balance_resp = client._portfolio_api.get_balance()
            snapshot["cash_balance"] = balance_resp.balance / 100.0
        except Exception as e:
            snapshot["error"] = f"Failed to fetch balance: {e}"
            logger.warning(snapshot["error"])
            return snapshot

        # Get positions
        try:
            resp = client._portfolio_api.get_positions_without_preload_content(limit=100)
            data = json.loads(resp.read())
            position_value = 0.0

            # Schema validation — fail loud on unknown response shape
            _KNOWN_POS_KEYS = ("event_positions", "positions", "market_positions")
            if not any(k in data for k in _KNOWN_POS_KEYS):
                snapshot["error"] = (
                    f"SCHEMA DRIFT: Kalshi API response has none of expected position keys. "
                    f"Got: {sorted(data.keys())}. Expected one of: {_KNOWN_POS_KEYS}. "
                    f"Kalshi changed their API — fix field names in pnl_tracker.py."
                )
                logger.error(snapshot["error"])
                return snapshot

            all_positions = data.get("event_positions") or data.get("positions") or data.get("market_positions", [])
            for p in all_positions:
                ticker = p.get("ticker", "")
                v = p.get("position_fp") or p.get("position", 0)
                try:
                    qty = int(float(v))
                except (ValueError, TypeError):
                    qty = 0

                if qty == 0:
                    continue  # Skip empty positions

                # Market price from last trade (best estimate)
                market_price_cents = p.get("last_traded_price", 50)
                if isinstance(market_price_cents, str):
                    try:
                        market_price_cents = int(float(market_price_cents))
                    except (ValueError, TypeError):
                        market_price_cents = 50

                side = "yes" if qty > 0 else "no"

                snapshot["positions"].append({
                    "ticker": ticker,
                    "qty": qty,
                    "side": side,
                    "market_price_cents": market_price_cents,
                })

                # Estimate position value at current market price
                if side == "yes":
                    # YES contract worth market_price_cents if win, 0 if lose
                    position_value += abs(qty) * (market_price_cents / 100.0)
                else:
                    # NO contract worth (100 - market_price_cents) if win, 0 if lose
                    position_value += abs(qty) * ((100 - market_price_cents) / 100.0)

        except Exception as e:
            snapshot["error"] = f"Failed to fetch positions: {e}"
            logger.warning(snapshot["error"])

        # Get open orders count
        try:
            resp = client._portfolio_api.get_orders_without_preload_content(status='resting')
            data = json.loads(resp.read())
            snapshot["open_order_count"] = len(data.get("orders", []))
        except Exception as e:
            logger.warning(f"Failed to fetch order count: {e}")

        # Total portfolio value = cash + unrealized position value
        snapshot["total_portfolio_value"] = snapshot["cash_balance"] + position_value

        # Log snapshot to JSONL
        _append_portfolio_snapshot(snapshot)

        return snapshot

    except Exception as e:
        snapshot["error"] = f"Unexpected error in get_portfolio_snapshot: {e}"
        logger.error(snapshot["error"])
        return snapshot


def _append_portfolio_snapshot(snapshot: dict) -> None:
    """Append portfolio snapshot to JSONL log.

    Args:
        snapshot: Portfolio snapshot dict from get_portfolio_snapshot()
    """
    try:
        PORTFOLIO_SNAPSHOTS_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(PORTFOLIO_SNAPSHOTS_PATH, "a") as f:
            f.write(json.dumps(snapshot) + "\n")
    except Exception as e:
        logger.warning(f"Failed to log portfolio snapshot: {e}")


def get_trade_history(client, since_hours: int = 24) -> list:
    """Get recent fills (trades executed) from Kalshi API.

    Args:
        client: Initialized Kalshi API client
        since_hours: Only include fills from last N hours (default 24)

    Returns:
        List of dicts: {ticker, side, qty, price_cents, cost_usd, timestamp, order_id}
    """
    fills = []
    cutoff_time = datetime.now(timezone.utc) - timedelta(hours=since_hours)

    try:
        resp = client._portfolio_api.get_fills_without_preload_content(limit=100)
        data = json.loads(resp.read())

        for fill in data.get("fills", []):
            try:
                # Parse fill timestamp
                created_time_str = fill.get("created_time", "")
                if not created_time_str:
                    continue

                created_time = datetime.fromisoformat(created_time_str.replace("Z", "+00:00"))

                # Skip if older than cutoff
                if created_time < cutoff_time:
                    continue

                ticker = fill.get("ticker", "")
                side = fill.get("side", "").lower()  # "yes" or "no"
                qty = int(fill.get("count", 0))
                price_cents = int(fill.get("price", 50))
                order_id = fill.get("order_id", "")

                # Calculate cost in USD
                cost_per_contract = price_cents / 100.0 if side == "yes" else (100 - price_cents) / 100.0
                cost_usd = qty * cost_per_contract

                fills.append({
                    "ticker": ticker,
                    "side": side,
                    "qty": qty,
                    "price_cents": price_cents,
                    "cost_usd": round(cost_usd, 2),
                    "timestamp": created_time.isoformat(),
                    "order_id": order_id,
                })

            except (ValueError, KeyError, TypeError) as e:
                logger.warning(f"Failed to parse fill: {e}")
                continue

        return fills

    except Exception as e:
        logger.error(f"Failed to fetch trade history: {e}")
        return []


def calculate_pnl(client, since_hours: int = 24) -> dict:
    """Calculate live P&L metrics from Kalshi positions and fills.

    Args:
        client: Initialized Kalshi API client
        since_hours: Time window for recent trades (used for context)

    Returns:
        {
            "realized_pnl_usd": float (from resolved trades in log),
            "unrealized_pnl_usd": float (from current positions),
            "total_pnl_usd": float,
            "open_trade_count": int,
            "recent_fills_count": int,
            "win_rate_pct": float (from historical trades),
            "avg_win_usd": float,
            "avg_loss_usd": float,
            "positions_snapshot": dict (from get_portfolio_snapshot),
            "error": Optional[str]
        }
    """
    result = {
        "realized_pnl_usd": 0.0,
        "unrealized_pnl_usd": 0.0,
        "total_pnl_usd": 0.0,
        "open_trade_count": 0,
        "recent_fills_count": 0,
        "win_rate_pct": 0.0,
        "avg_win_usd": 0.0,
        "avg_loss_usd": 0.0,
        "positions_snapshot": {},
        "error": None,
    }

    try:
        # Get current portfolio snapshot
        snapshot = get_portfolio_snapshot(client)
        result["positions_snapshot"] = snapshot
        result["open_trade_count"] = len(snapshot.get("positions", []))

        if snapshot.get("error"):
            result["error"] = snapshot["error"]
            return result

        # Get recent fills
        fills = get_trade_history(client, since_hours=since_hours)
        result["recent_fills_count"] = len(fills)

        # Get historical trades for realized P&L and win rate
        try:
            logger_obj = TradeLogger()
            trades = logger_obj.load_trades()
            analyzer = PortfolioAnalyzer(trades)

            result["realized_pnl_usd"] = round(analyzer.realized_pnl(), 2)
            result["total_pnl_usd"] = round(
                result["realized_pnl_usd"] + snapshot.get("total_portfolio_value", 0) - 100.0,  # Assume $100 initial
                2
            )
            result["win_rate_pct"] = round(analyzer.win_rate(), 1)

            # Calculate avg win/loss
            resolved_trades = [t for t in trades if t.is_resolved()]
            wins = [t for t in resolved_trades if (t.pnl_usd or 0) > 0]
            losses = [t for t in resolved_trades if (t.pnl_usd or 0) < 0]

            if wins:
                result["avg_win_usd"] = round(sum(t.pnl_usd for t in wins) / len(wins), 2)
            if losses:
                result["avg_loss_usd"] = round(sum(t.pnl_usd for t in losses) / len(losses), 2)

        except Exception as e:
            logger.warning(f"Failed to calculate historical P&L: {e}")

        return result

    except Exception as e:
        result["error"] = f"Failed to calculate P&L: {e}"
        logger.error(result["error"])
        return result


def format_pnl_report(pnl_data: dict) -> str:
    """Format P&L data into human-readable report string (Slack-ready).

    Args:
        pnl_data: Dict from calculate_pnl()

    Returns:
        Formatted report string
    """
    if pnl_data.get("error"):
        return f"ERROR: {pnl_data['error']}"

    snapshot = pnl_data.get("positions_snapshot", {})
    cash = snapshot.get("cash_balance", 0.0)
    positions = snapshot.get("positions", [])

    report = "╔════════════════════════════════════════════════════╗\n"
    report += "║          OPENCLAW PORTFOLIO REPORT                 ║\n"
    report += "╚════════════════════════════════════════════════════╝\n\n"

    report += f"📊 SNAPSHOT\n"
    report += f"  Timestamp:        {snapshot.get('timestamp', 'N/A')}\n"
    report += f"  Cash Balance:     ${cash:,.2f}\n"
    report += f"  Open Positions:   {len(positions)}\n"
    report += f"  Open Orders:      {snapshot.get('open_order_count', 0)}\n"
    report += f"  Portfolio Value:  ${snapshot.get('total_portfolio_value', 0):,.2f}\n\n"

    if positions:
        report += f"📈 POSITIONS ({len(positions)})\n"
        for pos in positions:
            ticker = pos.get("ticker", "?")
            qty = pos.get("qty", 0)
            side = pos.get("side", "?")
            price = pos.get("market_price_cents", 50)
            report += f"  {ticker:20s} {qty:+5d}x {side.upper():3s} @ {price}¢\n"
        report += "\n"

    report += f"💰 P&L\n"
    report += f"  Realized:         ${pnl_data.get('realized_pnl_usd', 0):+,.2f}\n"
    report += f"  Total:            ${pnl_data.get('total_pnl_usd', 0):+,.2f}\n"
    report += f"  Recent Fills:     {pnl_data.get('recent_fills_count', 0)}\n\n"

    if pnl_data.get("win_rate_pct", 0) > 0:
        report += f"📊 PERFORMANCE\n"
        report += f"  Win Rate:         {pnl_data.get('win_rate_pct', 0):.1f}%\n"
        if pnl_data.get("avg_win_usd"):
            report += f"  Avg Win:          ${pnl_data.get('avg_win_usd', 0):+,.2f}\n"
        if pnl_data.get("avg_loss_usd"):
            report += f"  Avg Loss:         ${pnl_data.get('avg_loss_usd', 0):+,.2f}\n"
        report += "\n"

    report += "═" * 52

    return report


# ── CLI Interface ──────────────────────────────────────────────────────────

def cmd_log(args) -> None:
    """CLI: Log a new trade."""
    logger_obj = TradeLogger()
    logger_obj.log_trade(
        ticker=args.ticker,
        title=args.title or args.ticker,
        side=args.side,
        market_price_cents=args.price,
        estimated_prob=args.est,
        edge_pct=args.edge if args.edge else abs(args.est - args.price / 100.0) * 100,
        contracts=args.contracts,
        cost_usd=args.cost,
        confidence=args.confidence,
        category=args.category,
    )


def cmd_resolve(args) -> None:
    """CLI: Resolve a trade."""
    logger_obj = TradeLogger()
    try:
        trade = logger_obj.resolve_trade(args.ticker, args.outcome)
        print(f"\nResolved: {trade.ticker}")
        print(f"  Outcome: {'YES' if trade.outcome == 1 else 'NO'}")
        print(f"  P&L: ${trade.pnl_usd:+.2f} ({trade.pnl_pct:+.1f}%)")
        print(f"  Predicted Edge: {trade.edge_pct:+.2f}%")
        print(f"  Actual Edge: {trade.actual_edge:+.2f}%")
    except ValueError as e:
        print(f"Error: {e}")


def cmd_summary(args) -> None:
    """CLI: Print portfolio summary."""
    logger_obj = TradeLogger()
    trades = logger_obj.load_trades()

    if not trades:
        print("No trades logged yet.")
        return

    analyzer = PortfolioAnalyzer(trades)
    summary = analyzer.summary()

    print("\n" + "=" * 60)
    print("OPENCLAW PORTFOLIO SUMMARY")
    print("=" * 60)
    print(f"\nTrades:")
    print(f"  Total:    {summary['total_trades']}")
    print(f"  Resolved: {summary['resolved_trades']}")
    print(f"  Open:     {summary['open_trades']}")

    print(f"\nP&L:")
    print(f"  Realized:   ${summary['realized_pnl_usd']:+.2f}")
    print(f"  Unrealized: ${summary['unrealized_pnl_usd']:+.2f}")
    print(f"  Total:      ${summary['total_pnl_usd']:+.2f}")

    print(f"\nPerformance:")
    print(f"  Win Rate:        {summary['win_rate_pct']:.1f}%")
    print(f"  Predicted Edge:  {summary['avg_predicted_edge_pct']:+.2f}%")
    print(f"  Actual Edge:     {summary['avg_actual_edge_pct']:+.2f}%")
    print(f"  Sharpe Ratio:    {summary['sharpe_ratio']:.3f}")
    print(f"  Max Drawdown:    ${summary['max_drawdown_usd']:+.2f}")

    # Category breakdown
    if summary["pnl_by_category"]:
        print(f"\nP&L by Category:")
        for cat, stats in sorted(summary["pnl_by_category"].items(), key=lambda x: x[1]["pnl"], reverse=True):
            print(f"  {cat:20s} {stats['trades']:3d} trades | ${stats['pnl']:+7.2f} | {stats['win_rate']:5.1f}% WR")

    # Best/worst trades
    if summary["resolved_trades"] > 0:
        best, worst = analyzer.best_worst_trades(limit=3)
        print(f"\nBest Trades:")
        for t in best:
            print(f"  {t.ticker:15s} ${t.pnl_usd:+7.2f} ({t.pnl_pct:+5.1f}%) | {t.title[:40]}")

        print(f"\nWorst Trades:")
        for t in worst:
            print(f"  {t.ticker:15s} ${t.pnl_usd:+7.2f} ({t.pnl_pct:+5.1f}%) | {t.title[:40]}")

    print("\n" + "=" * 60 + "\n")


def cmd_export(args) -> None:
    """CLI: Export trades to CSV or JSON."""
    logger_obj = TradeLogger()
    trades = logger_obj.load_trades()

    if not trades:
        print("No trades to export.")
        return

    fmt = args.format or "csv"
    output_file = Path.home() / ".openclaw" / f"trades_export.{fmt}"

    if fmt == "csv":
        with open(output_file, "w", newline="") as f:
            fieldnames = [
                "id", "timestamp", "ticker", "title", "side", "market_price_cents",
                "estimated_prob", "edge_pct", "contracts", "cost_usd", "confidence",
                "outcome", "resolved_at", "pnl_usd", "pnl_pct", "actual_edge", "category"
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for trade in trades:
                writer.writerow(trade.to_dict())
    else:
        with open(output_file, "w") as f:
            json.dump([t.to_dict() for t in trades], f, indent=2)

    print(f"Exported {len(trades)} trades to {output_file}")


def cmd_portfolio(args) -> None:
    """CLI: Show live portfolio snapshot from Kalshi."""
    try:
        from kalshi_commands import _get_client
    except ImportError as e:
        print(f"Error: Cannot import kalshi_commands: {e}")
        return

    try:
        client = _get_client()
        snapshot = get_portfolio_snapshot(client)

        if snapshot.get("error"):
            print(f"Error: {snapshot['error']}")
            return

        print("\n" + "=" * 60)
        print("KALSHI PORTFOLIO SNAPSHOT")
        print("=" * 60)
        print(f"\nTimestamp: {snapshot['timestamp']}")
        print(f"\nCash Balance: ${snapshot['cash_balance']:,.2f}")
        print(f"Open Positions: {len(snapshot['positions'])}")
        print(f"Open Orders: {snapshot['open_order_count']}")
        print(f"Total Portfolio Value: ${snapshot['total_portfolio_value']:,.2f}")

        if snapshot["positions"]:
            print(f"\nPositions ({len(snapshot['positions'])}):")
            for pos in snapshot["positions"]:
                ticker = pos.get("ticker", "?")
                qty = pos.get("qty", 0)
                side = pos.get("side", "?")
                price = pos.get("market_price_cents", 50)
                print(f"  {ticker:20s} {qty:+5d}x {side.upper():3s} @ {price}¢")

        print("\n" + "=" * 60 + "\n")

    except Exception as e:
        print(f"Error: {e}")


def cmd_pnl_live(args) -> None:
    """CLI: Show live P&L report from Kalshi."""
    try:
        from kalshi_commands import _get_client
    except ImportError as e:
        print(f"Error: Cannot import kalshi_commands: {e}")
        return

    try:
        client = _get_client()
        since_hours = args.hours or 24
        pnl_data = calculate_pnl(client, since_hours=since_hours)

        report = format_pnl_report(pnl_data)
        print("\n" + report + "\n")

    except Exception as e:
        print(f"Error: {e}")


# ── Main ───────────────────────────────────────────────────────────────────

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="OpenClaw P&L Tracker — live prediction market performance tracking"
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Log command
    log_parser = subparsers.add_parser("log", help="Log a new trade")
    log_parser.add_argument("--ticker", required=True, help="Market ticker")
    log_parser.add_argument("--title", help="Market title (optional)")
    log_parser.add_argument("--side", required=True, choices=["yes", "no"], help="Trade side")
    log_parser.add_argument("--price", type=int, required=True, help="Entry price in cents")
    log_parser.add_argument("--est", type=float, required=True, help="Estimated probability")
    log_parser.add_argument("--edge", type=float, help="Edge % (auto-calculated if omitted)")
    log_parser.add_argument("--contracts", type=int, required=True, help="Number of contracts")
    log_parser.add_argument("--cost", type=float, required=True, help="Total cost in USD")
    log_parser.add_argument("--confidence", type=float, required=True, help="Model confidence")
    log_parser.add_argument("--category", help="Market category (optional)")
    log_parser.set_defaults(func=cmd_log)

    # Resolve command
    resolve_parser = subparsers.add_parser("resolve", help="Resolve a trade")
    resolve_parser.add_argument("--ticker", required=True, help="Market ticker")
    resolve_parser.add_argument("--outcome", type=int, required=True, choices=[0, 1], help="0=NO, 1=YES")
    resolve_parser.set_defaults(func=cmd_resolve)

    # Summary command
    summary_parser = subparsers.add_parser("summary", help="Print portfolio summary")
    summary_parser.set_defaults(func=cmd_summary)

    # Export command
    export_parser = subparsers.add_parser("export", help="Export trades")
    export_parser.add_argument("--format", choices=["csv", "json"], default="csv", help="Export format")
    export_parser.set_defaults(func=cmd_export)

    # Portfolio command (live Kalshi snapshot)
    portfolio_parser = subparsers.add_parser("portfolio", help="Show live Kalshi portfolio")
    portfolio_parser.set_defaults(func=cmd_portfolio)

    # Live P&L command
    pnl_parser = subparsers.add_parser("pnl", help="Show live P&L report")
    pnl_parser.add_argument("--hours", type=int, help="Time window in hours (default 24)")
    pnl_parser.set_defaults(func=cmd_pnl_live)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
