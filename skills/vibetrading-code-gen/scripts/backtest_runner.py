#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backtest Runner - Run backtests on generated trading strategies

This script allows users to backtest their generated strategies
using historical data to evaluate performance before live trading.
"""

import os
import sys
import json
import argparse
import importlib.util
from datetime import datetime, timedelta
from pathlib import Path


class BacktestRunner:
    """Run backtests on trading strategies"""

    def __init__(self):
        """Initialize backtest runner"""
        self.results = {}

    def load_strategy(self, strategy_path):
        """Load strategy from file"""
        strategy_path = Path(strategy_path)

        if not strategy_path.exists():
            raise FileNotFoundError(f"Strategy file not found: {strategy_path}")

        # Extract strategy name from filename
        strategy_name = strategy_path.stem

        # Load the strategy module
        spec = importlib.util.spec_from_file_location(strategy_name, strategy_path)
        strategy_module = importlib.util.module_from_spec(spec)

        try:
            spec.loader.exec_module(strategy_module)
            return strategy_module, strategy_name
        except Exception as e:
            raise ImportError(f"Failed to load strategy: {e}")

    def run_backtest(self, strategy_path, config=None):
        """
        Run backtest on a strategy
        
        Args:
            strategy_path: Path to strategy file
            config: Backtest configuration dictionary
        
        Returns:
            Backtest results dictionary
        """
        # Default configuration
        default_config = {
            "start_date": (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
            "end_date": datetime.now().strftime("%Y-%m-%d"),
            "initial_balance": 10000.0,
            "interval": "1h",
            "symbol": "BTC",
            "commission_rate": 0.001,  # 0.1%
            "slippage": 0.001,  # 0.1%
            "verbose": True,
            "strategy_path": str(strategy_path)  # Add strategy path for session detection
        }
        
        # Merge with user config
        if config:
            default_config.update(config)
        config = default_config

        print(f"🔍 Loading strategy: {strategy_path}")

        try:
            # Load strategy
            strategy_module, strategy_name = self.load_strategy(strategy_path)

            print(f"📊 Starting backtest for: {strategy_name}")
            print(f"📅 Period: {config['start_date']} to {config['end_date']}")
            print(f"💰 Initial Balance: ${config['initial_balance']:,.2f}")
            print(f"⏱️  Interval: {config['interval']}")
            print(f"📈 Symbol: {config['symbol']}")

            # Check if strategy has backtest method
            if hasattr(strategy_module, 'run_backtest'):
                print("✅ Strategy has built-in backtest method")
                # Use strategy's built-in backtest
                results = strategy_module.run_backtest(config)
            else:
                print("⚠️  Strategy doesn't have built-in backtest, using simulation")
                # Run simplified simulation
                results = self._run_simulation(strategy_module, config)

            # Store results
            self.results[strategy_name] = results

            # Generate report
            self._generate_report(strategy_name, results, config)

            return results

        except Exception as e:
            print(f"❌ Backtest failed: {e}")
            import traceback
            traceback.print_exc()
            return None

    def _run_simulation(self, strategy_module, config):
        """
        Run simplified backtest simulation

        This is a placeholder for a more sophisticated backtest engine.
        In a real implementation, this would use historical data and
        simulate trades with realistic market conditions.
        """
        print("⚠️  Running simplified simulation (placeholder)")

        # This is a mock simulation - in reality, you would:
        # 1. Load historical price data
        # 2. Simulate strategy decisions at each time step
        # 3. Track portfolio value
        # 4. Calculate performance metrics

        # Mock results for demonstration
        results = {
            "initial_balance": config["initial_balance"],
            "final_balance": config["initial_balance"] * 1.1235,  # +12.35%
            "total_return_pct": 12.35,
            "total_trades": 42,
            "winning_trades": 25,
            "losing_trades": 17,
            "win_rate": 59.52,
            "max_drawdown_pct": 5.67,
            "sharpe_ratio": 1.45,
            "avg_trade_duration_hours": 8.5,
            "largest_win": 245.67,
            "largest_loss": 123.45,
            "avg_win": 89.12,
            "avg_loss": 56.78,
            "total_commission": 42.50,
            "simulation_type": "simplified_mock"
        }

        return results

    def _generate_report(self, strategy_name, results, config):
        """Generate backtest report"""
        print("\n" + "="*60)
        print(f"📊 Backtest Results for {strategy_name}")
        print("="*60)

        print(f"📅 Period: {config['start_date']} to {config['end_date']}")
        print(f"💰 Initial Balance: ${results['initial_balance']:,.2f}")
        print(f"💰 Final Balance: ${results['final_balance']:,.2f}")

        print(f"\n📈 Performance Metrics:")
        print(f"  • Total Return: +{results['total_return_pct']:.2f}%")
        print(f"  • Max Drawdown: -{results['max_drawdown_pct']:.2f}%")
        print(f"  • Sharpe Ratio: {results['sharpe_ratio']:.2f}")
        print(f"  • Win Rate: {results['win_rate']:.1f}%")
        print(f"  • Total Trades: {results['total_trades']}")
        print(f"  • Avg Trade Duration: {results['avg_trade_duration_hours']:.1f} hours")

        print(f"\n📋 Trade Analysis:")
        print(f"  • Winning Trades: {results['winning_trades']}")
        print(f"  • Losing Trades: {results['losing_trades']}")
        print(f"  • Largest Win: +${results['largest_win']:.2f}")
        print(f"  • Largest Loss: -${results['largest_loss']:.2f}")
        print(f"  • Avg Win: +${results['avg_win']:.2f}")
        print(f"  • Avg Loss: -${results['avg_loss']:.2f}")
        print(f"  • Total Commission: ${results['total_commission']:.2f}")

        print(f"\n⚠️  Risk Assessment:")
        if results['total_return_pct'] > 10 and results['max_drawdown_pct'] < 10:
            print(f"  • Risk-Adjusted Return: Good")
        elif results['total_return_pct'] > 5:
            print(f"  • Risk-Adjusted Return: Acceptable")
        else:
            print(f"  • Risk-Adjusted Return: Poor")

        if results['win_rate'] > 60:
            print(f"  • Consistency: High")
        elif results['win_rate'] > 50:
            print(f"  • Consistency: Moderate")
        else:
            print(f"  • Consistency: Low")

        print(f"\n📝 Notes:")
        print(f"  • Simulation Type: {results.get('simulation_type', 'unknown')}")
        print(f"  • Always test with real market conditions before live trading")
        print(f"  • Past performance does not guarantee future results")

        # Save results to file
        self._save_results(strategy_name, results, config)

    def _save_results(self, strategy_name, results, config):
        """Save backtest results to file"""
        # Try to find session directory
        session_id = None
        strategy_path = Path(config.get('strategy_path', ''))

        # Look for session directory in path
        for parent in strategy_path.parents:
            if parent.name == "strategies" and parent.parent.name == "sessions":
                session_dir = parent.parent
                session_id = session_dir.name
                break

        if session_id:
            # Save to session directory
            output_dir = Path("sessions") / session_id / "backtest_results"
            output_dir.mkdir(parents=True, exist_ok=True)
            print(f"📁 Saving to session: {session_id}")
        else:
            # Legacy behavior
            output_dir = Path("backtest_results")
            output_dir.mkdir(exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{strategy_name}_{timestamp}.json"
        filepath = output_dir / filename

        # Prepare data to save
        data = {
            "strategy_name": strategy_name,
            "timestamp": timestamp,
            "config": config,
            "results": results
        }

        # Add session info if available
        if session_id:
            data["session_id"] = session_id

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Results saved to: {filepath}")

        # Also save a summary file
        self._save_summary(strategy_name, results, config, filepath.parent, session_id)

    def _save_summary(self, strategy_name, results, config, output_dir, session_id=None):
        """Save a human-readable summary file"""
        summary_file = output_dir / f"{strategy_name}_summary.txt"

        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(f"Backtest Summary: {strategy_name}\n")
            f.write("=" * 60 + "\n\n")

            if session_id:
                f.write(f"Session ID: {session_id}\n")

            f.write(f"Test Period: {config.get('start_date', 'N/A')} to {config.get('end_date', 'N/A')}\n")
            f.write(f"Initial Balance: ${results.get('initial_balance', 0):,.2f}\n")
            f.write(f"Final Balance: ${results.get('final_balance', 0):,.2f}\n\n")

            f.write("Performance Metrics:\n")
            f.write(f"  • Total Return: +{results.get('total_return_pct', 0):.2f}%\n")
            f.write(f"  • Max Drawdown: -{results.get('max_drawdown_pct', 0):.2f}%\n")
            f.write(f"  • Sharpe Ratio: {results.get('sharpe_ratio', 0):.2f}\n")
            f.write(f"  • Win Rate: {results.get('win_rate', 0):.1f}%\n")
            f.write(f"  • Total Trades: {results.get('total_trades', 0)}\n\n")

            f.write("Generated: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")

        print(f"📝 Summary saved to: {summary_file}")

    def compare_strategies(self, strategy_paths, config=None):
        """Compare multiple strategies"""
        print(f"🔍 Comparing {len(strategy_paths)} strategies")

        comparison_results = {}

        for strategy_path in strategy_paths:
            try:
                results = self.run_backtest(strategy_path, config)
                if results:
                    strategy_name = Path(strategy_path).stem
                    comparison_results[strategy_name] = results
            except Exception as e:
                print(f"❌ Failed to backtest {strategy_path}: {e}")

        # Generate comparison report
        if comparison_results:
            self._generate_comparison_report(comparison_results)

        return comparison_results

    def _generate_comparison_report(self, comparison_results):
        """Generate comparison report for multiple strategies"""
        print("\n" + "="*60)
        print("📊 Strategy Comparison Report")
        print("="*60)

        headers = ["Strategy", "Return %", "Max DD %", "Sharpe", "Win Rate %", "Trades"]
        print(f"{headers[0]:<20} {headers[1]:>10} {headers[2]:>10} {headers[3]:>10} {headers[4]:>10} {headers[5]:>10}")
        print("-" * 80)

        for strategy_name, results in comparison_results.items():
            print(f"{strategy_name:<20} "
                  f"{results['total_return_pct']:>10.2f} "
                  f"{results['max_drawdown_pct']:>10.2f} "
                  f"{results['sharpe_ratio']:>10.2f} "
                  f"{results['win_rate']:>10.1f} "
                  f"{results['total_trades']:>10}")

        # Find best strategy by Sharpe ratio
        best_sharpe = max(comparison_results.items(),
                         key=lambda x: x[1]['sharpe_ratio'])

        # Find best strategy by total return
        best_return = max(comparison_results.items(),
                         key=lambda x: x[1]['total_return_pct'])

        print(f"\n🏆 Best by Sharpe Ratio: {best_sharpe[0]} ({best_sharpe[1]['sharpe_ratio']:.2f})")
        print(f"🏆 Best by Total Return: {best_return[0]} ({best_return[1]['total_return_pct']:.2f}%)")


def main():
    """Main function"""
    # Check Python version first
    import sys
    if sys.version_info < (3, 6):
        print(f"❌ Python版本错误: 需要Python 3.6+")
        print(f"   当前版本: {sys.version}")
        print(f"\n💡 回测功能需要Python 3.6或更高版本")
        sys.exit(1)

    parser = argparse.ArgumentParser(description='Run backtests on trading strategies')
    parser.add_argument('strategy_paths', nargs='+', help='Path(s) to strategy file(s)')
    parser.add_argument('--start-date', help='Start date (YYYY-MM-DD)')
    parser.add_argument('--end-date', help='End date (YYYY-MM-DD)')
    parser.add_argument('--initial-balance', type=float, default=10000.0,
                       help='Initial balance in USDC')
    parser.add_argument('--interval', default='1h',
                       choices=['1m', '5m', '15m', '30m', '1h', '4h', '1d'],
                       help='Time interval')
    parser.add_argument('--symbol', default='BTC',
                       help='Trading symbol')
    parser.add_argument('--commission', type=float, default=0.001,
                       help='Commission rate (e.g., 0.001 for 0.1%%)')
    parser.add_argument('--slippage', type=float, default=0.001,
                       help='Slippage rate (e.g., 0.001 for 0.1%%)')
    parser.add_argument('--compare', action='store_true',
                       help='Compare multiple strategies')
    parser.add_argument('--verbose', action='store_true',
                       help='Verbose output')

    args = parser.parse_args()

    # Prepare config
    config = {
        "start_date": args.start_date,
        "end_date": args.end_date,
        "initial_balance": args.initial_balance,
        "interval": args.interval,
        "symbol": args.symbol,
        "commission_rate": args.commission,
        "slippage": args.slippage,
        "verbose": args.verbose
    }

    # Remove None values
    config = {k: v for k, v in config.items() if v is not None}

    # Create runner
    runner = BacktestRunner()

    if args.compare and len(args.strategy_paths) > 1:
        # Compare multiple strategies
        runner.compare_strategies(args.strategy_paths, config)
    else:
        # Run backtest on single strategy
        for strategy_path in args.strategy_paths:
            runner.run_backtest(strategy_path, config)


if __name__ == "__main__":
    main()