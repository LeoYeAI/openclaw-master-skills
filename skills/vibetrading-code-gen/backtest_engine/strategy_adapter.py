#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Strategy Adapter

Adapts existing strategies to work with the historical backtest engine
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class GridStrategyAdapter:
    """Adapter for grid trading strategies"""
    
    @staticmethod
    def create_grid_strategy(config_path):
        """
        Create a grid strategy from config file
        
        Args:
            config_path: Path to strategy config JSON
        
        Returns:
            Strategy instance with on_tick method
        """
        # Load config
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        strategy_config = config.get("strategy", {})
        params = config.get("parameters", {})
        
        # Extract parameters
        symbol = strategy_config.get("symbol", "HYPE")
        lower_bound = params.get("lower_bound", 0.1)
        upper_bound = params.get("upper_bound", 1.0)
        grid_count = params.get("grid_count", 10)
        grid_size = params.get("grid_size", 1000.0)
        
        # Create strategy instance
        strategy = GridStrategy(
            symbol=symbol,
            lower_bound=lower_bound,
            upper_bound=upper_bound,
            grid_count=grid_count,
            grid_size=grid_size
        )
        
        return strategy
    
    @staticmethod
    def wrap_existing_strategy(strategy_instance):
        """
        Wrap an existing strategy instance for backtest engine
        
        Args:
            strategy_instance: Existing strategy instance
        
        Returns:
            Wrapped strategy with on_tick method
        """
        class WrappedStrategy:
            def __init__(self, original_strategy):
                self.original = original_strategy
                self.orders = []
                
            def on_tick(self, market_state):
                """Called on each market tick"""
                decisions = []
                
                # Check if original has decision methods
                if hasattr(self.original, 'check_and_execute_orders'):
                    # This is a grid strategy
                    price = market_state["price"]
                    executed = self.original.check_and_execute_orders(price)
                    
                    # Convert executed orders to decisions
                    for order in executed:
                        decision = {
                            "action": "buy" if order.get("side") == "buy" else "sell",
                            "symbol": market_state.get("symbol", "HYPE"),
                            "quantity": order.get("quantity", 0),
                            "price": order.get("price", price)
                        }
                        decisions.append(decision)
                
                return decisions
        
        return WrappedStrategy(strategy_instance)


class GridStrategy:
    """Grid trading strategy for backtest engine"""
    
    def __init__(self, symbol="HYPE", lower_bound=0.1, upper_bound=1.0, 
                 grid_count=10, grid_size=1000.0):
        self.symbol = symbol
        self.lower_bound = lower_bound
        self.upper_bound = upper_bound
        self.grid_count = grid_count
        self.grid_size = grid_size
        
        # Calculate grid prices
        self.grid_prices = self._calculate_grid_prices()
        
        # Active orders
        self.active_orders = {}
        
        # State
        self.initialized = False
        
        logger.info(f"GridStrategy initialized: {symbol} ${lower_bound}-${upper_bound}, {grid_count} grids")
    
    def _calculate_grid_prices(self):
        """Calculate grid price levels"""
        if self.grid_count < 2:
            raise ValueError("Grid count must be at least 2")
        
        price_step = (self.upper_bound - self.lower_bound) / (self.grid_count - 1)
        grid_prices = [self.lower_bound + i * price_step for i in range(self.grid_count)]
        
        return grid_prices
    
    def initialize(self, config=None):
        """Initialize strategy (called by backtest engine)"""
        if config:
            # Update from config
            self.symbol = config.get("symbol", self.symbol)
            self.lower_bound = config.get("lower_bound", self.lower_bound)
            self.upper_bound = config.get("upper_bound", self.upper_bound)
            self.grid_count = config.get("grid_count", self.grid_count)
            self.grid_size = config.get("grid_size", self.grid_size)
            
            # Recalculate grid prices
            self.grid_prices = self._calculate_grid_prices()
        
        # Place initial grid orders
        self.place_grid_orders()
        self.initialized = True
        
        return self
    
    def place_grid_orders(self):
        """Place grid orders"""
        import time
        
        self.active_orders = {}
        
        # Place buy orders (even grid levels)
        for i, price in enumerate(self.grid_prices):
            if i % 2 == 0:  # Even levels are buy orders
                order_id = f"buy_{i}_{int(time.time())}"
                self.active_orders[order_id] = {
                    'price': price,
                    'side': 'buy',
                    'quantity': self.grid_size,
                    'status': 'pending'
                }
        
        # Place sell orders (odd grid levels)
        for i, price in enumerate(self.grid_prices):
            if i % 2 == 1:  # Odd levels are sell orders
                order_id = f"sell_{i}_{int(time.time())}"
                self.active_orders[order_id] = {
                    'price': price,
                    'side': 'sell',
                    'quantity': self.grid_size,
                    'status': 'pending'
                }
        
        logger.info(f"Placed {len(self.active_orders)} grid orders")
    
    def check_and_execute_orders(self, current_price):
        """Check and execute orders at current price"""
        executed_orders = []
        
        for order_id, order in list(self.active_orders.items()):
            order_price = order['price']
            order_side = order['side']
            
            # Check if price has crossed the order level
            if (order_side == 'buy' and current_price <= order_price) or \
               (order_side == 'sell' and current_price >= order_price):
                
                # Mark as executed
                order['status'] = 'executed'
                order['executed_price'] = current_price
                order['executed_time'] = time.time() if 'time' not in locals() else time.time()
                
                executed_orders.append(order)
                
                # Remove from active orders
                del self.active_orders[order_id]
        
        # Replenish orders if needed
        if len(self.active_orders) < self.grid_count / 2:
            self.place_grid_orders()
        
        return executed_orders
    
    def on_tick(self, market_state):
        """Called on each market tick by backtest engine"""
        decisions = []
        
        if not self.initialized:
            self.initialize()
        
        current_price = market_state.get("price", 0)
        if current_price <= 0:
            return decisions
        
        # Check and execute orders
        executed = self.check_and_execute_orders(current_price)
        
        # Convert to decisions
        for order in executed:
            decision = {
                "action": order["side"],
                "symbol": self.symbol,
                "quantity": order["quantity"],
                "price": order.get("executed_price", current_price)
            }
            decisions.append(decision)
        
        return decisions
    
    def get_status(self):
        """Get current strategy status"""
        return {
            "symbol": self.symbol,
            "lower_bound": self.lower_bound,
            "upper_bound": self.upper_bound,
            "grid_count": self.grid_count,
            "grid_size": self.grid_size,
            "active_orders": len(self.active_orders),
            "grid_prices": self.grid_prices
        }


def create_strategy_from_file(strategy_file, config_file=None):
    """
    Create strategy from Python file
    
    Args:
        strategy_file: Path to strategy Python file
        config_file: Optional config file
    
    Returns:
        Strategy instance
    """
    import importlib.util
    
    strategy_path = Path(strategy_file)
    
    if not strategy_path.exists():
        raise FileNotFoundError(f"Strategy file not found: {strategy_file}")
    
    # Load config if provided
    config = {}
    if config_file and Path(config_file).exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
    
    # Try to detect strategy type
    with open(strategy_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "GridTradingStrategy" in content or "grid_trading" in content:
        # This is a grid strategy
        if config_file:
            return GridStrategyAdapter.create_grid_strategy(config_file)
        else:
            # Create default grid strategy
            return GridStrategy()
    else:
        # Generic strategy - try to import and wrap
        spec = importlib.util.spec_from_file_location(strategy_path.stem, strategy_path)
        strategy_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(strategy_module)
        
        # Look for strategy class
        strategy_class = None
        for attr_name in dir(strategy_module):
            attr = getattr(strategy_module, attr_name)
            if isinstance(attr, type) and "Strategy" in attr_name:
                strategy_class = attr
                break
        
        if strategy_class:
            # Create instance
            instance = strategy_class()
            return GridStrategyAdapter.wrap_existing_strategy(instance)
        else:
            raise ValueError(f"No strategy class found in {strategy_file}")


def main():
    """Test the adapter"""
    # Test creating grid strategy
    print("Testing GridStrategyAdapter...")
    
    # Create a test config
    test_config = {
        "strategy": {
            "name": "test_grid",
            "symbol": "HYPE",
            "type": "grid_trading"
        },
        "parameters": {
            "lower_bound": 0.1,
            "upper_bound": 1.0,
            "grid_count": 5,
            "grid_size": 100.0
        }
    }
    
    # Save test config
    config_path = Path("test_grid_config.json")
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(test_config, f, indent=2)
    
    # Create strategy
    strategy = GridStrategyAdapter.create_grid_strategy(config_path)
    print(f"Created strategy: {strategy.get_status()}")
    
    # Test on_tick
    market_state = {
        "price": 0.5,
        "timestamp": "2024-01-01T00:00:00Z"
    }
    
    decisions = strategy.on_tick(market_state)
    print(f"Decisions: {len(decisions)}")
    
    # Clean up
    config_path.unlink()
    
    print("\n✅ Adapter test completed")

if __name__ == "__main__":
    main()