#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Historical Backtest Engine

Uses real historical data for backtesting trading strategies
"""

import os
import sys
import json
import time
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np
import importlib.util

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backtest_engine.data_downloader import HyperliquidDataDownloader

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HistoricalBacktestEngine:
    """Backtest engine using historical data"""
    
    def __init__(self, use_testnet=False, data_dir="data/historical"):
        """
        Initialize backtest engine
        
        Args:
            use_testnet: Use testnet data
            data_dir: Directory with historical data
        """
        self.data_downloader = HyperliquidDataDownloader(use_testnet=use_testnet, data_dir=data_dir)
        self.data_dir = Path(data_dir)
        
        # Backtest state
        self.current_time = None
        self.current_price = None
        self.current_index = 0
        
        # Portfolio state
        self.initial_balance = 0.0
        self.usdc_balance = 0.0
        self.asset_balance = 0.0
        self.positions = {}  # {symbol: quantity}
        self.orders = []     # List of pending orders
        self.trades = []     # List of executed trades
        
        # Performance tracking
        self.portfolio_values = []
        self.timestamps = []
        
        logger.info("HistoricalBacktestEngine initialized")
    
    def load_strategy(self, strategy_path):
        """Load trading strategy from file"""
        strategy_path = Path(strategy_path)
        
        if not strategy_path.exists():
            raise FileNotFoundError(f"Strategy not found: {strategy_path}")
        
        # Load module
        spec = importlib.util.spec_from_file_location(strategy_path.stem, strategy_path)
        strategy_module = importlib.util.module_from_spec(spec)
        
        try:
            spec.loader.exec_module(strategy_module)
            return strategy_module
        except Exception as e:
            raise ImportError(f"Failed to load strategy: {e}")
    
    def prepare_data(self, symbol, interval="1h", days=30, force_download=False):
        """
        Prepare historical data for backtest
        
        Returns:
            DataFrame with historical data
        """
        logger.info(f"Preparing data for {symbol} ({interval}, {days} days)")
        
        # Download or load data
        data = self.data_downloader.download_ohlcv(
            symbol=symbol,
            interval=interval,
            days=days,
            force_download=force_download
        )
        
        if data is None or data.empty:
            raise ValueError(f"No data available for {symbol}")
        
        logger.info(f"Data loaded: {len(data)} rows from {data.index[0]} to {data.index[-1]}")
        return data
    
    def initialize_portfolio(self, initial_balance=10000.0):
        """Initialize portfolio with starting balance"""
        self.initial_balance = initial_balance
        self.usdc_balance = initial_balance
        self.asset_balance = 0.0
        self.positions = {}
        self.orders = []
        self.trades = []
        self.portfolio_values = []
        self.timestamps = []
        
        logger.info(f"Portfolio initialized with ${initial_balance:,.2f}")
    
    def execute_buy(self, symbol, quantity, price, timestamp):
        """Execute a buy order"""
        cost = quantity * price
        commission = cost * 0.001  # 0.1% commission
        
        if self.usdc_balance >= (cost + commission):
            self.usdc_balance -= (cost + commission)
            self.asset_balance += quantity
            
            if symbol not in self.positions:
                self.positions[symbol] = 0.0
            self.positions[symbol] += quantity
            
            trade = {
                "timestamp": timestamp,
                "symbol": symbol,
                "side": "buy",
                "quantity": quantity,
                "price": price,
                "cost": cost,
                "commission": commission,
                "usdc_after": self.usdc_balance,
                "asset_after": self.positions.get(symbol, 0.0)
            }
            self.trades.append(trade)
            
            return trade
        else:
            logger.warning(f"Insufficient funds: need ${cost+commission:.2f}, have ${self.usdc_balance:.2f}")
            return None
    
    def execute_sell(self, symbol, quantity, price, timestamp):
        """Execute a sell order"""
        if symbol not in self.positions or self.positions[symbol] < quantity:
            logger.warning(f"Insufficient {symbol}: need {quantity}, have {self.positions.get(symbol, 0.0)}")
            return None
        
        revenue = quantity * price
        commission = revenue * 0.001  # 0.1% commission
        
        self.usdc_balance += (revenue - commission)
        self.asset_balance -= quantity
        self.positions[symbol] -= quantity
        
        # Remove position if zero
        if self.positions[symbol] == 0:
            del self.positions[symbol]
        
        trade = {
            "timestamp": timestamp,
            "symbol": symbol,
            "side": "sell",
            "quantity": quantity,
            "price": price,
            "revenue": revenue,
            "commission": commission,
            "usdc_after": self.usdc_balance,
            "asset_after": self.positions.get(symbol, 0.0)
        }
        self.trades.append(trade)
        
        return trade
    
    def calculate_portfolio_value(self, current_price):
        """Calculate total portfolio value"""
        asset_value = self.asset_balance * current_price
        total_value = self.usdc_balance + asset_value
        return total_value
    
    def run_backtest(self, strategy_path, config=None):
        """
        Run backtest on a strategy
        
        Args:
            strategy_path: Path to strategy file
            config: Backtest configuration
        
        Returns:
            Backtest results
        """
        # Default config
        default_config = {
            "symbol": "HYPE",
            "interval": "1h",
            "days": 30,
            "initial_balance": 10000.0,
            "commission_rate": 0.001,
            "slippage": 0.001,
            "force_download": False
        }
        
        if config:
            default_config.update(config)
        config = default_config
        
        logger.info(f"Starting backtest for {strategy_path}")
        logger.info(f"Config: {json.dumps(config, indent=2)}")
        
        try:
            # Load strategy
            strategy_module = self.load_strategy(strategy_path)
            
            # Prepare data
            data = self.prepare_data(
                symbol=config["symbol"],
                interval=config["interval"],
                days=config["days"],
                force_download=config["force_download"]
            )
            
            # Initialize portfolio
            self.initialize_portfolio(config["initial_balance"])
            
            # Initialize strategy if it has initialize method
            strategy_instance = None
            if hasattr(strategy_module, 'initialize'):
                strategy_instance = strategy_module.initialize(config)
            
            # Run backtest through historical data
            logger.info(f"Running backtest through {len(data)} time periods")
            
            for idx, (timestamp, row) in enumerate(data.iterrows()):
                self.current_time = timestamp
                self.current_price = row["close"]
                self.current_index = idx
                
                # Update portfolio value
                portfolio_value = self.calculate_portfolio_value(self.current_price)
                self.portfolio_values.append(portfolio_value)
                self.timestamps.append(timestamp)
                
                # Call strategy decision method if available
                if strategy_instance and hasattr(strategy_instance, 'on_tick'):
                    try:
                        # Pass current market state to strategy
                        market_state = {
                            "timestamp": timestamp,
                            "price": self.current_price,
                            "open": row["open"],
                            "high": row["high"],
                            "low": row["low"],
                            "close": row["close"],
                            "volume": row["volume"],
                            "portfolio_value": portfolio_value,
                            "usdc_balance": self.usdc_balance,
                            "asset_balance": self.asset_balance,
                            "positions": self.positions.copy()
                        }
                        
                        # Get strategy decisions
                        decisions = strategy_instance.on_tick(market_state)
                        
                        # Execute decisions
                        if decisions and isinstance(decisions, list):
                            for decision in decisions:
                                self._execute_decision(decision, timestamp)
                    
                    except Exception as e:
                        logger.error(f"Strategy error at {timestamp}: {e}")
                
                # Progress logging
                if (idx + 1) % 100 == 0 or idx == len(data) - 1:
                    logger.info(f"Progress: {idx + 1}/{len(data)} periods")
            
            # Calculate final results
            results = self._calculate_results(data)
            
            # Generate report
            self._generate_report(results, config)
            
            return results
            
        except Exception as e:
            logger.error(f"Backtest failed: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def _execute_decision(self, decision, timestamp):
        """Execute a trading decision"""
        if not isinstance(decision, dict):
            return
        
        action = decision.get("action")
        symbol = decision.get("symbol", "HYPE")
        quantity = decision.get("quantity", 0.0)
        
        if action == "buy" and quantity > 0:
            self.execute_buy(symbol, quantity, self.current_price, timestamp)
        elif action == "sell" and quantity > 0:
            self.execute_sell(symbol, quantity, self.current_price, timestamp)
    
    def _calculate_results(self, data):
        """Calculate backtest results"""
        if not self.portfolio_values:
            return {}
        
        # Final portfolio value
        final_price = data.iloc[-1]["close"]
        final_value = self.calculate_portfolio_value(final_price)
        
        # Calculate returns
        total_return = (final_value - self.initial_balance) / self.initial_balance * 100
        
        # Calculate max drawdown
        portfolio_series = pd.Series(self.portfolio_values, index=self.timestamps)
        rolling_max = portfolio_series.expanding().max()
        drawdowns = (portfolio_series - rolling_max) / rolling_max * 100
        max_drawdown = drawdowns.min()
        
        # Calculate Sharpe ratio (simplified)
        returns = portfolio_series.pct_change().dropna()
        if len(returns) > 1:
            sharpe_ratio = returns.mean() / returns.std() * np.sqrt(365 * 24)  # Annualized
        else:
            sharpe_ratio = 0.0
        
        # Calculate win rate
        winning_trades = len([t for t in self.trades if t.get("side") == "sell"])
        total_trades = len(self.trades)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0.0
        
        # Calculate commissions
        total_commission = sum(t.get("commission", 0) for t in self.trades)
        
        results = {
            "initial_balance": self.initial_balance,
            "final_balance": final_value,
            "total_return_pct": total_return,
            "max_drawdown_pct": max_drawdown,
            "sharpe_ratio": float(sharpe_ratio),
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": total_trades - winning_trades,
            "win_rate": win_rate,
            "total_commission": total_commission,
            "final_usdc": self.usdc_balance,
            "final_asset": self.asset_balance,
            "final_price": final_price,
            "data_points": len(data),
            "period_start": data.index[0].isoformat(),
            "period_end": data.index[-1].isoformat(),
            "trades": self.trades[-20:]  # Last 20 trades
        }
        
        return results
    
    def _generate_report(self, results, config):
        """Generate backtest report"""
        print("\n" + "="*60)
        print("📊 HISTORICAL BACKTEST RESULTS")
        print("="*60)
        
        print(f"📅 Period: {results.get('period_start', 'N/A')} to {results.get('period_end', 'N/A')}")
        print(f"📈 Symbol: {config['symbol']} | Interval: {config['interval']}")
        print(f"💰 Initial Balance: ${results['initial_balance']:,.2f}")
        print(f"💰 Final Balance: ${results['final_balance']:,.2f}")
        
        print(f"\n📊 Performance Metrics:")
        print(f"  • Total Return: {results['total_return_pct']:+.2f}%")
        print(f"  • Max Drawdown: {results['max_drawdown_pct']:.2f}%")
        print(f"  • Sharpe Ratio: {results['sharpe_ratio']:.2f}")
        print(f"  • Win Rate: {results['win_rate']:.1f}%")
        print(f"  • Total Trades: {results['total_trades']}")
        print(f"  • Total Commission: ${results['total_commission']:.2f}")
        
        print(f"\n📋 Final Position:")
        print(f"  • USDC: ${results['final_usdc']:,.2f}")
        print(f"  • {config['symbol']}: {results['final_asset']:.4f}")
        print(f"  • Current Price: ${results['final_price']:.4f}")
        
        print(f"\n📈 Data Summary:")
        print(f"  • Data Points: {results['data_points']}")
        print(f"  • Backtest Type: Historical Data")
        
        # Save results
        self._save_results(results, config)
    
    def _save_results(self, results, config):
        """Save backtest results to file"""
        output_dir = Path("backtest_results")
        output_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"historical_backtest_{config['symbol']}_{timestamp}.json"
        filepath = output_dir / filename
        
        # Add config to results
        results["config"] = config
        results["generated_at"] = datetime.now().isoformat()
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 Results saved to: {filepath}")
        
        # Also save summary
        summary_file = output_dir / f"summary_{config['symbol']}_{timestamp}.txt"
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"Historical Backtest Summary\n")
            f.write("="*50 + "\n\n")
            f.write(f"Symbol: {config['symbol']}\n")
            f.write(f"Period: {results['period_start']} to {results['period_end']}\n")
            f.write(f"Initial: ${results['initial_balance']:,.2f}\n")
            f.write(f"Final: ${results['final_balance']:,.2f}\n")
            f.write(f"Return: {results['total_return_pct']:+.2f}%\n")
            f.write(f"Trades: {results['total_trades']}\n")
            f.write(f"Win Rate: {results['win_rate']:.1f}%\n")
        
        print(f"📝 Summary saved to: {summary_file}")


def main():
    """Test the backtest engine"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Run historical backtest")
    parser.add_argument("strategy", help="Path to strategy file")
    parser.add_argument("--symbol", default="HYPE", help="Trading symbol")
    parser.add_argument("--interval", default="1h", help="Time interval")
    parser.add_argument("--days", type=int, default=30, help="Days of data")
    parser.add_argument("--balance", type=float, default=10000.0, help="Initial balance")
    parser.add_argument("--testnet", action="store_true", help="Use testnet")
    parser.add_argument("--force-download", action="store_true", help="Force data download")
    
    args = parser.parse_args()
    
    # Create engine
    engine = HistoricalBacktestEngine(use_testnet=args.testnet)
    
    # Run backtest
    config = {
        "symbol": args.symbol,
        "interval": args.interval,
        "days": args.days,
        "initial_balance": args.balance,
        "force_download": args.force_download
    }
    
    results = engine.run_backtest(args.strategy, config)
    
    if results:
        print("\n✅ Backtest completed successfully!")
    else:
        print("\n❌ Backtest failed!")

if __name__ == "__main__":
    main()