#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Price Fetcher - Fetch current prices from Hyperliquid before strategy generation
"""

import sys
import json
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api_wrappers.hyperliquid_api import (
    get_current_price,
    get_multiple_prices,
    validate_trading_symbol,
    get_grid_trading_recommendation
)

def parse_symbols_from_prompt(prompt: str) -> list:
    """
    Parse trading symbols from natural language prompt.
    
    Args:
        prompt: Natural language strategy description
    
    Returns:
        List of symbol strings
    """
    symbols = []
    
    # Common cryptocurrency symbols
    common_symbols = ['BTC', 'ETH', 'SOL', 'HYPE', 'USDC', 'USDT', 'BNB', 'XRP', 'ADA', 'DOGE']
    
    # Look for symbols in the prompt
    prompt_upper = prompt.upper()
    
    # Check for common symbols
    for symbol in common_symbols:
        if symbol in prompt_upper:
            # Make sure it's not part of another word
            symbol_pattern = f' {symbol} '  # Space before and after
            if symbol_pattern in f' {prompt_upper} ':
                symbols.append(symbol)
    
    # Look for $SYMBOL format
    import re
    dollar_symbols = re.findall(r'\$([A-Z]{2,6})', prompt_upper)
    symbols.extend(dollar_symbols)
    
    # Remove duplicates and empty strings
    symbols = list(set([s for s in symbols if s]))
    
    return symbols

def fetch_prices(symbols: list, use_testnet: bool = False) -> dict:
    """
    Fetch current prices for symbols.
    
    Args:
        symbols: List of trading symbols
        use_testnet: Use testnet API
    
    Returns:
        Dict with price information
    """
    if not symbols:
        return {"error": "No symbols provided"}
    
    print(f"🔍 Fetching prices for {len(symbols)} symbol(s): {', '.join(symbols)}")
    
    results = {
        "symbols": symbols,
        "prices": {},
        "valid_symbols": [],
        "invalid_symbols": [],
        "recommendations": {}
    }
    
    # Validate symbols first
    for symbol in symbols:
        is_valid = validate_trading_symbol(symbol, use_testnet)
        if is_valid:
            results["valid_symbols"].append(symbol)
        else:
            results["invalid_symbols"].append(symbol)
            print(f"⚠️  Symbol '{symbol}' may not be valid on Hyperliquid")
    
    if not results["valid_symbols"]:
        return {"error": "No valid symbols found"}
    
    # Fetch prices
    prices = get_multiple_prices(results["valid_symbols"], use_testnet)
    results["prices"] = prices
    
    # Generate recommendations for valid symbols
    for symbol in results["valid_symbols"]:
        if symbol in prices and prices[symbol]:
            recommendation = get_grid_trading_recommendation(symbol, use_testnet)
            if recommendation:
                results["recommendations"][symbol] = recommendation
    
    return results

def generate_price_report(results: dict) -> str:
    """Generate formatted price report."""
    report_lines = []
    
    report_lines.append("📊 HYPERLIQUID PRICE REPORT")
    report_lines.append("=" * 50)
    
    if "error" in results:
        report_lines.append(f"❌ Error: {results['error']}")
        return "\n".join(report_lines)
    
    # Valid symbols
    if results["valid_symbols"]:
        report_lines.append(f"✅ Valid Symbols ({len(results['valid_symbols'])}):")
        for symbol in results["valid_symbols"]:
            price = results["prices"].get(symbol)
            if price:
                report_lines.append(f"   • {symbol}: ${price:.4f}")
            else:
                report_lines.append(f"   • {symbol}: Price unavailable")
    
    # Invalid symbols
    if results["invalid_symbols"]:
        report_lines.append(f"\n⚠️  Invalid Symbols ({len(results['invalid_symbols'])}):")
        for symbol in results["invalid_symbols"]:
            report_lines.append(f"   • {symbol}: Not found on Hyperliquid")
    
    # Recommendations
    if results["recommendations"]:
        report_lines.append("\n🎯 GRID TRADING RECOMMENDATIONS:")
        for symbol, rec in results["recommendations"].items():
            report_lines.append(f"\n   {symbol}:")
            report_lines.append(f"     Current Price:    ${rec['current_price']:.4f}")
            report_lines.append(f"     24h Change:      {rec.get('24h_change', 'N/A'):.2f}%")
            report_lines.append(f"     24h High:        ${rec.get('24h_high', 'N/A'):.4f}")
            report_lines.append(f"     24h Low:         ${rec.get('24h_low', 'N/A'):.4f}")
            report_lines.append(f"     Recommended Range: ${rec['lower_bound']:.4f} - ${rec['upper_bound']:.4f}")
            
            # Calculate grid parameters
            price_range = rec['upper_bound'] - rec['lower_bound']
            grid_spacing = price_range / 9  # For 10 grids
            
            report_lines.append(f"     Grid Spacing:    ${grid_spacing:.4f} per level")
            report_lines.append(f"     Range Width:     {price_range/rec['current_price']*100:.1f}% of current price")
    
    # Summary
    report_lines.append("\n" + "=" * 50)
    report_lines.append("💡 RECOMMENDED STRATEGY PARAMETERS:")
    
    if results["recommendations"]:
        for symbol, rec in results["recommendations"].items():
            current = rec['current_price']
            lower = rec['lower_bound']
            upper = rec['upper_bound']
            
            report_lines.append(f"\n   For {symbol}:")
            report_lines.append(f"     Price Range:     ${lower:.2f} - ${upper:.2f}")
            report_lines.append(f"     Grid Count:      10 (adjust based on volatility)")
            report_lines.append(f"     Position Size:   10-100 {symbol} (adjust based on capital)")
            report_lines.append(f"     Check Interval:  60-300 seconds")
    else:
        report_lines.append("   No recommendations available")
    
    report_lines.append("\n" + "=" * 50)
    
    return "\n".join(report_lines)

def save_price_data(results: dict, output_file: str = "price_data.json"):
    """Save price data to JSON file."""
    try:
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        print(f"💾 Price data saved to: {output_file}")
        return output_file
    except Exception as e:
        print(f"⚠️  Could not save price data: {e}")
        return None

def main():
    """Main function for price fetching."""
    parser = argparse.ArgumentParser(description='Fetch prices from Hyperliquid')
    parser.add_argument('--symbols', '-s', nargs='+', help='Trading symbols (e.g., BTC ETH HYPE)')
    parser.add_argument('--prompt', '-p', help='Natural language prompt to parse symbols from')
    parser.add_argument('--testnet', '-t', action='store_true', help='Use testnet API')
    parser.add_argument('--output', '-o', default='price_data.json', help='Output JSON file')
    parser.add_argument('--report', '-r', action='store_true', help='Generate detailed report')
    
    args = parser.parse_args()
    
    # Determine symbols
    symbols = []
    
    if args.symbols:
        symbols = [s.upper() for s in args.symbols]
    elif args.prompt:
        symbols = parse_symbols_from_prompt(args.prompt)
    else:
        print("❌ Please provide symbols with --symbols or a prompt with --prompt")
        parser.print_help()
        return
    
    if not symbols:
        print("❌ No symbols found in prompt")
        return
    
    print(f"🚀 Fetching prices from Hyperliquid {'Testnet' if args.testnet else 'Mainnet'}")
    print(f"📈 Symbols: {', '.join(symbols)}")
    
    # Fetch prices
    results = fetch_prices(symbols, args.testnet)
    
    # Generate report
    if args.report:
        report = generate_price_report(results)
        print("\n" + report)
    
    # Save data
    saved_file = save_price_data(results, args.output)
    
    # Print summary
    print("\n✅ Price fetching completed!")
    
    if "valid_symbols" in results:
        valid_count = len(results["valid_symbols"])
        invalid_count = len(results.get("invalid_symbols", []))
        
        print(f"   Valid symbols: {valid_count}")
        print(f"   Invalid symbols: {invalid_count}")
        
        if valid_count > 0:
            print("\n   Current Prices:")
            for symbol in results["valid_symbols"]:
                price = results["prices"].get(symbol)
                if price:
                    print(f"     {symbol}: ${price:.4f}")
    
    if saved_file:
        print(f"\n📁 Data saved to: {saved_file}")
        print(f"💡 Use this data for strategy generation with: python scripts/strategy_generator.py --price-data {saved_file}")

if __name__ == "__main__":
    main()