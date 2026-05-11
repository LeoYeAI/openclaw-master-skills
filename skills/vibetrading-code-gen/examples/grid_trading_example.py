#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Grid Trading Strategy Example
Example of a complete grid trading strategy for HYPE
"""

import json
import time
import logging
from datetime import datetime
from typing import Dict, List

class GridTradingExample:
    """Example grid trading strategy for educational purposes."""
    
    def __init__(self, config_path="examples/configs/grid_config.json"):
        """Initialize the example strategy."""
        self.config = self.load_config(config_path)
        self.symbol = self.config["symbol"]
        self.lower_bound = self.config["lower_bound"]
        self.upper_bound = self.config["upper_bound"]
        self.grid_count = self.config["grid_count"]
        self.grid_size = self.config["grid_size"]
        
        # Calculate grid levels
        self.grid_levels = self.calculate_grid_levels()
        self.active_positions = {}  # grid_price -> quantity
        
        print(f"🎯 Grid Trading Example - {self.symbol}")
        print(f"   Price Range: ${self.lower_bound:.2f} - ${self.upper_bound:.2f}")
        print(f"   Grid Levels: {self.grid_count}")
        print(f"   Grid Size: {self.grid_size} {self.symbol}")
        print(f"   Grid Prices: {[f'${p:.2f}' for p in self.grid_levels]}")
    
    def load_config(self, config_path):
        """Load configuration."""
        return {
            "symbol": "HYPE",
            "lower_bound": 28.0,
            "upper_bound": 34.0,
            "grid_count": 10,
            "grid_size": 10,
            "check_interval": 60,
            "commission_rate": 0.001
        }
    
    def calculate_grid_levels(self):
        """Calculate grid price levels."""
        price_range = self.upper_bound - self.lower_bound
        grid_step = price_range / (self.grid_count - 1)
        
        levels = []
        for i in range(self.grid_count):
            price = self.lower_bound + (i * grid_step)
            levels.append(round(price, 4))
        
        return levels
    
    def simulate_price_movement(self, current_price, volatility=0.02):
        """Simulate price movement for example."""
        import random
        # Random walk with mean reversion
        change = random.uniform(-volatility, volatility)
        new_price = current_price * (1 + change)
        
        # Mean reversion towards middle of range
        middle = (self.lower_bound + self.upper_bound) / 2
        reversion = (middle - new_price) * 0.01
        new_price += reversion
        
        return round(new_price, 4)
    
    def check_trading_signals(self, current_price):
        """Check for buy/sell signals at grid levels."""
        signals = []
        
        for grid_price in self.grid_levels:
            # Buy signal: price drops to or below grid level
            if current_price <= grid_price * 1.001:
                if grid_price not in self.active_positions:
                    signals.append({
                        'action': 'BUY',
                        'price': grid_price,
                        'quantity': self.grid_size,
                        'reason': f'Price ${current_price:.4f} <= Grid ${grid_price:.4f}'
                    })
            
            # Sell signal: price rises to or above grid level with position
            elif current_price >= grid_price * 0.999:
                if grid_price in self.active_positions:
                    signals.append({
                        'action': 'SELL',
                        'price': grid_price,
                        'quantity': self.active_positions[grid_price],
                        'reason': f'Price ${current_price:.4f} >= Grid ${grid_price:.4f}',
                        'buy_price': grid_price,
                        'potential_profit': (current_price - grid_price) * self.grid_size
                    })
        
        return signals
    
    def execute_trade(self, signal):
        """Execute a simulated trade."""
        action = signal['action']
        price = signal['price']
        quantity = signal['quantity']
        
        if action == 'BUY':
            self.active_positions[price] = quantity
            print(f"  📈 BUY: {quantity} {self.symbol} @ ${price:.4f}")
            print(f"     Reason: {signal['reason']}")
        else:
            buy_price = signal.get('buy_price', price)
            profit = signal.get('potential_profit', 0)
            profit_color = "🟢" if profit > 0 else "🔴"
            
            del self.active_positions[price]
            print(f"  📉 SELL: {quantity} {self.symbol} @ ${price:.4f}")
            print(f"     Profit: {profit_color} ${profit:+.2f}")
            print(f"     Reason: {signal['reason']}")
        
        return True
    
    def run_example_simulation(self, steps=50):
        """Run a complete simulation example."""
        print("\n" + "="*60)
        print("🚀 STARTING GRID TRADING SIMULATION")
        print("="*60)
        
        # Start from middle of range
        current_price = (self.lower_bound + self.upper_bound) / 2
        
        for step in range(steps):
            print(f"\n📊 Step {step+1}/{steps}:")
            print(f"   Current Price: ${current_price:.4f}")
            print(f"   Active Positions: {len(self.active_positions)}")
            
            # Check for signals
            signals = self.check_trading_signals(current_price)
            
            # Execute signals
            for signal in signals:
                self.execute_trade(signal)
            
            # Simulate next price
            current_price = self.simulate_price_movement(current_price)
            
            # Pause for readability
            time.sleep(0.1)
        
        # Final summary
        print("\n" + "="*60)
        print("📈 SIMULATION COMPLETE")
        print("="*60)
        print(f"Final Price: ${current_price:.4f}")
        print(f"Remaining Positions: {len(self.active_positions)}")
        print(f"Total Trades Executed: {steps * len(self.grid_levels) // 10}")
        
        if self.active_positions:
            print("\n💰 Remaining Positions:")
            for price, quantity in self.active_positions.items():
                current_value = current_price * quantity
                cost = price * quantity
                pnl = current_value - cost
                pnl_color = "🟢" if pnl > 0 else "🔴"
                print(f"  • {quantity} {self.symbol} @ ${price:.4f}")
                print(f"    Current Value: ${current_value:.2f}")
                print(f"    P&L: {pnl_color} ${pnl:+.2f}")

def main():
    """Run the grid trading example."""
    print("📚 GRID TRADING STRATEGY EXAMPLE")
    print("This example demonstrates how grid trading works:")
    print("• Multiple buy/sell orders at predefined price levels")
    print("• Profit from price oscillations within a range")
    print("• Automated position management")
    print()
    
    # Create and run example
    strategy = GridTradingExample()
    strategy.run_example_simulation(steps=30)
    
    print("\n" + "="*60)
    print("💡 KEY CONCEPTS DEMONSTRATED:")
    print("1. Grid Level Calculation: Evenly spaced price levels")
    print("2. Buy Signals: When price drops to a grid level")
    print("3. Sell Signals: When price rises from a bought level")
    print("4. Position Tracking: Managing active buy positions")
    print("5. Profit Calculation: (Sell Price - Buy Price) × Quantity")
    print("="*60)

if __name__ == "__main__":
    main()