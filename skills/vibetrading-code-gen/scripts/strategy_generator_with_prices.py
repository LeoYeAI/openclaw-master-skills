#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
VibeTrading Code Generator with Price Integration
Generates strategies using real-time Hyperliquid price data
"""

import os
import sys
import json
import argparse
import uuid
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import from scripts directory
from scripts.template_manager import TemplateManager
from scripts.prompt_parser import PromptParser
from scripts.code_formatter import CodeFormatter
from scripts.price_fetcher import parse_symbols_from_prompt, fetch_prices

class StrategyGeneratorWithPrices:
    """Strategy generator with integrated price fetching."""
    
    def __init__(self, use_testnet=False):
        """Initialize generator."""
        self.use_testnet = use_testnet
        self.template_manager = TemplateManager()
        self.prompt_parser = PromptParser()
        self.code_formatter = CodeFormatter()
    
    def fetch_and_analyze_prices(self, prompt: str):
        """
        Fetch prices and analyze market conditions.
        
        Args:
            prompt: Natural language strategy prompt
        
        Returns:
            Dict with price data and recommendations
        """
        print("🔍 Analyzing strategy prompt...")
        
        # Parse symbols from prompt
        symbols = parse_symbols_from_prompt(prompt)
        
        if not symbols:
            print("⚠️  No symbols detected in prompt. Using default parameters.")
            return {
                "symbols": [],
                "prices": {},
                "recommendations": {},
                "using_real_data": False
            }
        
        print(f"📈 Detected symbols: {', '.join(symbols)}")
        
        # Fetch prices from Hyperliquid
        print("🌐 Fetching real-time prices from Hyperliquid...")
        price_data = fetch_prices(symbols, self.use_testnet)
        
        if "error" in price_data:
            print(f"❌ Price fetch failed: {price_data['error']}")
            print("⚠️  Using estimated parameters instead.")
            return {
                "symbols": symbols,
                "prices": {},
                "recommendations": {},
                "using_real_data": False,
                "error": price_data["error"]
            }
        
        print("✅ Price data fetched successfully!")
        
        # Generate recommendations
        recommendations = {}
        for symbol in price_data.get("valid_symbols", []):
            if symbol in price_data.get("recommendations", {}):
                rec = price_data["recommendations"][symbol]
                recommendations[symbol] = rec
                print(f"\n🎯 {symbol} Recommendations:")
                print(f"   Current Price: ${rec['current_price']:.4f}")
                print(f"   Recommended Range: ${rec['lower_bound']:.4f} - ${rec['upper_bound']:.4f}")
        
        return {
            "symbols": symbols,
            "prices": price_data.get("prices", {}),
            "recommendations": recommendations,
            "using_real_data": True,
            "price_data": price_data
        }
    
    def enhance_prompt_with_prices(self, prompt: str, price_info: dict) -> str:
        """
        Enhance the user prompt with real price data.
        
        Args:
            prompt: Original prompt
            price_info: Price information from fetch_and_analyze_prices
        
        Returns:
            Enhanced prompt with price context
        """
        enhanced_parts = [prompt]
        
        if price_info["using_real_data"] and price_info["recommendations"]:
            enhanced_parts.append("\n\nBased on current market data:")
            
            for symbol, rec in price_info["recommendations"].items():
                current = rec['current_price']
                lower = rec['lower_bound']
                upper = rec['upper_bound']
                
                enhanced_parts.append(
                    f"{symbol} is currently at ${current:.4f}. "
                    f"Recommended grid range: ${lower:.2f}-${upper:.2f} "
                    f"(based on 24h volatility)."
                )
        
        return "\n".join(enhanced_parts)
    
    def generate_strategy_info(self, prompt: str, price_info: dict):
        """
        Generate strategy information with price-aware parameters.
        
        Args:
            prompt: Original prompt
            price_info: Price information
        
        Returns:
            Strategy info dictionary
        """
        # Parse the original prompt
        strategy_info = self.prompt_parser.parse(prompt)
        
        # Enhance with price data if available
        if price_info["using_real_data"] and price_info["recommendations"]:
            symbols = price_info["symbols"]
            
            # Use first symbol if multiple detected
            primary_symbol = symbols[0] if symbols else strategy_info.get('symbol', 'HYPE')
            
            if primary_symbol in price_info["recommendations"]:
                rec = price_info["recommendations"][primary_symbol]
                
                # Update strategy info with real price data
                strategy_info['symbol'] = primary_symbol
                
                # Set price range from recommendations
                if 'parameters' not in strategy_info:
                    strategy_info['parameters'] = {}
                
                # Only set if not already specified in prompt
                if 'price_range' not in strategy_info['parameters']:
                    strategy_info['parameters']['price_range'] = [
                        rec['lower_bound'],
                        rec['upper_bound']
                    ]
                
                # Add current price for reference
                strategy_info['current_price'] = rec['current_price']
                strategy_info['price_source'] = 'hyperliquid_api'
                strategy_info['price_timestamp'] = datetime.now().isoformat()
                
                print(f"💰 Using real price data for {primary_symbol}:")
                print(f"   Current: ${rec['current_price']:.4f}")
                print(f"   Range: ${rec['lower_bound']:.4f} - ${rec['upper_bound']:.4f}")
        
        return strategy_info
    
    def generate(self, prompt: str, output_dir: str = "generated_strategies", 
                 session_id: str = None, strategy_name: str = None, 
                 symbol: str = None, verbose: bool = False):
        """
        Generate strategy with price integration.
        
        Args:
            prompt: Natural language prompt
            output_dir: Output directory
            session_id: Session ID
            strategy_name: Custom strategy name
            symbol: Override symbol
            verbose: Verbose output
        
        Returns:
            Generated files information
        """
        print("=" * 60)
        print("🚀 VIBETRADING STRATEGY GENERATOR WITH PRICE INTEGRATION")
        print("=" * 60)
        
        # Step 1: Fetch and analyze prices
        price_info = self.fetch_and_analyze_prices(prompt)
        
        # Step 2: Enhance prompt with price context
        enhanced_prompt = self.enhance_prompt_with_prices(prompt, price_info)
        
        if verbose:
            print(f"\n📋 Enhanced Prompt:\n{enhanced_prompt}")
        
        # Step 3: Generate strategy info with price-aware parameters
        strategy_info = self.generate_strategy_info(prompt, price_info)
        
        # Override with command line arguments if provided
        if symbol:
            strategy_info['symbol'] = symbol
        if strategy_name:
            strategy_info['name'] = strategy_name
        
        # Add session info
        if session_id:
            strategy_info['session_id'] = session_id
        
        # Step 4: Select template
        template = self.template_manager.select_template(strategy_info)
        
        if verbose:
            print(f"\n📄 Selected Template: {template['name']}")
            print(f"📊 Strategy Info: {json.dumps(strategy_info, indent=2, ensure_ascii=False)}")
        
        # Step 5: Generate code
        print("\n🛠️  Generating strategy code...")
        generated_files = self.code_formatter.generate(
            template=template,
            strategy_info=strategy_info,
            output_dir=output_dir,
            session_id=session_id
        )
        
        # Step 6: Save price data alongside strategy
        if price_info["using_real_data"]:
            price_data_file = self._save_price_data(price_info, output_dir, session_id)
            if price_data_file:
                generated_files.append({
                    'type': 'price_data',
                    'path': price_data_file,
                    'description': 'Hyperliquid price data used for generation'
                })
        
        return generated_files, strategy_info, price_info
    
    def _save_price_data(self, price_info: dict, output_dir: str, session_id: str = None):
        """Save price data to file."""
        try:
            if session_id:
                save_dir = Path(output_dir) / session_id
            else:
                save_dir = Path(output_dir)
            
            save_dir.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"price_data_{timestamp}.json"
            filepath = save_dir / filename
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(price_info, f, indent=2, default=str)
            
            print(f"💾 Price data saved to: {filepath}")
            return str(filepath)
        except Exception as e:
            print(f"⚠️  Could not save price data: {e}")
            return None
    
    def print_summary(self, generated_files: list, strategy_info: dict, price_info: dict):
        """Print generation summary."""
        print("\n" + "=" * 60)
        print("✅ STRATEGY GENERATION COMPLETE!")
        print("=" * 60)
        
        # Strategy info
        symbol = strategy_info.get('symbol', 'Unknown')
        strategy_type = strategy_info.get('type', 'basic')
        
        print(f"\n📊 STRATEGY INFO:")
        print(f"   Symbol:          {symbol}")
        print(f"   Type:            {strategy_type}")
        
        if 'current_price' in strategy_info:
            print(f"   Current Price:   ${strategy_info['current_price']:.4f}")
        
        # Price source
        if price_info['using_real_data']:
            print(f"   Price Source:    Hyperliquid API (Real-time)")
        else:
            print(f"   Price Source:    Estimated")
        
        # Parameters
        params = strategy_info.get('parameters', {})
        if 'price_range' in params:
            lower, upper = params['price_range']
            print(f"   Price Range:     ${lower:.2f} - ${upper:.2f}")
        
        # Generated files
        print(f"\n📁 GENERATED FILES:")
        for file_info in generated_files:
            file_type = file_info.get('type', 'unknown')
            file_path = file_info.get('path', '')
            description = file_info.get('description', '')
            
            # Show relative path
            rel_path = Path(file_path).relative_to(Path.cwd()) if Path(file_path).is_relative_to(Path.cwd()) else file_path
            
            print(f"   📄 {file_type}: {rel_path}")
            if description:
                print(f"      {description}")
        
        # Next steps
        print(f"\n🚀 NEXT STEPS:")
        
        # Find main strategy file
        strategy_files = [f for f in generated_files if f.get('type') == 'strategy']
        if strategy_files:
            strategy_file = strategy_files[0]['path']
            strategy_name = Path(strategy_file).stem
            
            print(f"   1. Review generated code: {Path(strategy_file).name}")
            print(f"   2. Install dependencies: pip install -r requirements.txt")
            print(f"   3. Run strategy: python {strategy_name}.py")
            print(f"   4. Test with simulation before live trading")
        else:
            print("   No strategy files generated")
        
        print("\n" + "=" * 60)
        print("⚠️  RISK WARNING: Always test strategies in simulation before live trading!")
        print("=" * 60)

def main():
    """Main function."""
    parser = argparse.ArgumentParser(
        description='Generate Hyperliquid trading strategies with real-time price integration'
    )
    parser.add_argument('prompt', help='Natural language prompt describing the strategy')
    parser.add_argument('--output-dir', '-o', default='generated_strategies',
                       help='Output directory for generated files')
    parser.add_argument('--session-id', help='Session ID for organizing files')
    parser.add_argument('--strategy-name', '-n', help='Custom strategy name')
    parser.add_argument('--symbol', '-s', help='Trading symbol (overrides auto-detection)')
    parser.add_argument('--testnet', '-t', action='store_true', help='Use Hyperliquid testnet')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--no-prices', action='store_true', help='Skip price fetching')
    
    args = parser.parse_args()
    
    # Generate session ID if not provided
    if not args.session_id:
        args.session_id = str(uuid.uuid4())[:8]
    
    # Create generator
    generator = StrategyGeneratorWithPrices(use_testnet=args.testnet)
    
    try:
        # Generate strategy
        generated_files, strategy_info, price_info = generator.generate(
            prompt=args.prompt,
            output_dir=args.output_dir,
            session_id=args.session_id,
            strategy_name=args.strategy_name,
            symbol=args.symbol,
            verbose=args.verbose
        )
        
        # Print summary
        generator.print_summary(generated_files, strategy_info, price_info)
        
    except Exception as e:
        print(f"\n❌ Strategy generation failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())