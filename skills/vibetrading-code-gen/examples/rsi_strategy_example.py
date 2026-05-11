#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RSI Trading Strategy Example
Example of an RSI-based mean reversion strategy
"""

import json
import time
import random
from datetime import datetime
from typing import List, Dict

class RSIStrategyExample:
    """Example RSI (Relative Strength Index) trading strategy."""
    
    def __init__(self, config_path="examples/configs/rsi_config.json"):
        """Initialize the RSI strategy."""
        self.config = self.load_config(config_path)
        self.symbol = self.config["symbol"]
        self.rsi_period = self.config["rsi_period"]
        self.oversold = self.config["oversold_threshold"]
        self.overbought = self.config["overbought_threshold"]
        self.position_size = self.config["position_size"]
        
        self.position = 0  # Current position (positive = long, negative = short)
        self.entry_price = 0
        self.trade_history = []
        
        print(f"🎯 RSI Strategy Example - {self.symbol}")
        print(f"   RSI Period: {self.rsi_period} periods")
        print(f"   Oversold: RSI < {self.oversold} (Buy signal)")
        print(f"   Overbought: RSI > {self.overbought} (Sell signal)")
        print(f"   Position Size: {self.position_size} {self.symbol}")
    
    def load_config(self, config_path):
        """Load configuration."""
        return {
            "symbol": "HYPE",
            "rsi_period": 14,
            "oversold_threshold": 30,
            "overbought_threshold": 70,
            "position_size": 10,
            "stop_loss": 0.05,
            "take_profit": 0.10
        }
    
    def calculate_rsi(self, prices: List[float]) -> float:
        """
        Calculate RSI (Relative Strength Index).
        
        RSI = 100 - (100 / (1 + RS))
        RS = Average Gain / Average Loss
        """
        if len(prices) < self.rsi_period + 1:
            return 50  # Neutral if not enough data
        
        # Calculate gains and losses
        gains = []
        losses = []
        
        for i in range(1, self.rsi_period + 1):
            change = prices[-i] - prices[-i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        # Calculate averages
        avg_gain = sum(gains) / self.rsi_period
        avg_loss = sum(losses) / self.rsi_period
        
        if avg_loss == 0:
            return 100  # All gains, extremely bullish
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi, 2)
    
    def generate_price_data(self, base_price=30.0, volatility=0.02, count=100) -> List[float]:
        """Generate sample price data with trends."""
        prices = [base_price]
        
        # Create some market cycles
        for i in range(1, count):
            prev = prices[-1]
            
            # Add some trend cycles
            if i % 40 < 20:
                # Uptrend
                trend = 0.001
            else:
                # Downtrend
                trend = -0.001
            
            # Random movement
            random_move = random.uniform(-volatility, volatility)
            
            new_price = prev * (1 + trend + random_move)
            prices.append(round(new_price, 4))
        
        return prices
    
    def check_rsi_signals(self, prices: List[float], current_price: float) -> Dict:
        """Check for RSI-based trading signals."""
        rsi = self.calculate_rsi(prices)
        
        signal = {
            'rsi': rsi,
            'price': current_price,
            'action': 'HOLD',
            'reason': 'RSI in neutral range',
            'position': self.position
        }
        
        # Buy signal: RSI below oversold threshold
        if rsi < self.oversold and self.position <= 0:
            signal['action'] = 'BUY'
            signal['reason'] = f'RSI {rsi} < {self.oversold} (oversold)'
        
        # Sell signal: RSI above overbought threshold
        elif rsi > self.overbought and self.position >= 0:
            signal['action'] = 'SELL'
            signal['reason'] = f'RSI {rsi} > {self.overbought} (overbought)'
        
        # Exit signal: RSI returns to neutral after position
        elif self.position > 0 and rsi > 50:  # Exit long
            signal['action'] = 'SELL'
            signal['reason'] = f'Exit long: RSI {rsi} returned to neutral'
        elif self.position < 0 and rsi < 50:  # Exit short
            signal['action'] = 'BUY'
            signal['reason'] = f'Exit short: RSI {rsi} returned to neutral'
        
        return signal
    
    def execute_trade(self, signal: Dict):
        """Execute a trade based on RSI signal."""
        action = signal['action']
        price = signal['price']
        rsi = signal['rsi']
        
        if action == 'BUY':
            if self.position <= 0:  # Enter long or exit short
                quantity = self.position_size if self.position >= 0 else abs(self.position)
                self.position = quantity
                self.entry_price = price
                
                trade_type = "ENTER LONG" if signal['position'] >= 0 else "EXIT SHORT"
                print(f"  📈 {trade_type}: {quantity} {self.symbol} @ ${price:.4f}")
                print(f"     RSI: {rsi}, Reason: {signal['reason']}")
                
                self.trade_history.append({
                    'type': 'BUY',
                    'price': price,
                    'quantity': quantity,
                    'rsi': rsi,
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
        
        elif action == 'SELL':
            if self.position >= 0:  # Exit long or enter short
                quantity = self.position_size if self.position <= 0 else self.position
                self.position = -quantity
                self.entry_price = price
                
                trade_type = "EXIT LONG" if signal['position'] > 0 else "ENTER SHORT"
                print(f"  📉 {trade_type}: {quantity} {self.symbol} @ ${price:.4f}")
                print(f"     RSI: {rsi}, Reason: {signal['reason']}")
                
                self.trade_history.append({
                    'type': 'SELL',
                    'price': price,
                    'quantity': quantity,
                    'rsi': rsi,
                    'timestamp': datetime.now().strftime('%H:%M:%S')
                })
        
        return True
    
    def calculate_pnl(self, current_price: float) -> float:
        """Calculate profit/loss for current position."""
        if self.position == 0:
            return 0
        
        if self.position > 0:  # Long position
            return (current_price - self.entry_price) * self.position
        else:  # Short position
            return (self.entry_price - current_price) * abs(self.position)
    
    def run_example_simulation(self):
        """Run a complete RSI strategy simulation."""
        print("\n" + "="*60)
        print("🚀 STARTING RSI STRATEGY SIMULATION")
        print("="*60)
        
        # Generate price data
        print("\n📊 Generating market data...")
        prices = self.generate_price_data(base_price=30.0, count=100)
        
        print(f"📈 Price range: ${min(prices):.2f} - ${max(prices):.2f}")
        print(f"📉 Initial price: ${prices[0]:.2f}")
        print(f"📈 Final price: ${prices[-1]:.2f}")
        
        # Run simulation
        print("\n🔄 Running RSI strategy...")
        
        for i in range(self.rsi_period, len(prices)):
            current_price = prices[i]
            price_history = prices[:i+1]
            
            # Get RSI signal
            signal = self.check_rsi_signals(price_history, current_price)
            
            # Display status
            print(f"\n📊 Step {i+1}/{len(prices)}:")
            print(f"   Price: ${current_price:.4f}")
            print(f"   RSI: {signal['rsi']:.1f}")
            print(f"   Position: {self.position} {self.symbol}")
            
            pnl = self.calculate_pnl(current_price)
            pnl_color = "🟢" if pnl > 0 else "🔴"
            print(f"   P&L: {pnl_color} ${pnl:+.2f}")
            
            # Execute trade if signal
            if signal['action'] != 'HOLD':
                self.execute_trade(signal)
            
            time.sleep(0.05)
        
        # Final summary
        print("\n" + "="*60)
        print("📈 RSI STRATEGY SIMULATION COMPLETE")
        print("="*60)
        
        final_pnl = self.calculate_pnl(prices[-1])
        total_trades = len(self.trade_history)
        
        print(f"Final Position: {self.position} {self.symbol}")
        print(f"Total Trades: {total_trades}")
        print(f"Final P&L: ${final_pnl:+.2f}")
        
        if total_trades > 0:
            winning_trades = sum(1 for t in self.trade_history 
                               if (t['type'] == 'SELL' and t['price'] > self.entry_price) or
                                  (t['type'] == 'BUY' and t['price'] < self.entry_price))
            
            win_rate = (winning_trades / total_trades) * 100
            print(f"Win Rate: {win_rate:.1f}%")
            
            print("\n📋 Trade History:")
            for trade in self.trade_history[-5:]:  # Last 5 trades
                print(f"  {trade['timestamp']} - {trade['type']}: "
                      f"{trade['quantity']} @ ${trade['price']:.4f} (RSI: {trade['rsi']:.1f})")

def main():
    """Run the RSI strategy example."""
    print("📚 RSI (RELATIVE STRENGTH INDEX) STRATEGY EXAMPLE")
    print("This example demonstrates how RSI-based mean reversion works:")
    print("• RSI measures speed and change of price movements")
    print("• Values range from 0 to 100")
    print("• Below 30: Oversold (potential buy)")
    print("• Above 70: Overbought (potential sell)")
    print("• 50: Neutral")
    print()
    
    # Create and run example
    strategy = RSIStrategyExample()
    strategy.run_example_simulation()
    
    print("\n" + "="*60)
    print("💡 KEY CONCEPTS DEMONSTRATED:")
    print("1. RSI Calculation: Based on average gains vs losses")
    print("2. Oversold Signals: RSI < 30 suggests buying opportunity")
    print("3. Overbought Signals: RSI > 70 suggests selling opportunity")
    print("4. Mean Reversion: Prices tend to return to average")
    print("5. Position Management: Enter/exit based on RSI levels")
    print("="*60)
    
    print("\n🔧 RSI STRATEGY PARAMETERS TO EXPERIMENT WITH:")
    print("• RSI Period: Shorter (7-10) = more sensitive, Longer (20-25) = smoother")
    print("• Oversold Threshold: Lower (20-25) = fewer but stronger signals")
    print("• Overbought Threshold: Higher (75-80) = fewer but stronger signals")
    print("• Position Sizing: Adjust based on risk tolerance")

if __name__ == "__main__":
    main()