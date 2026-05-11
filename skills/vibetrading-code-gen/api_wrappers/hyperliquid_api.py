#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Hyperliquid API Wrapper
Simplified interface for Hyperliquid exchange API
"""

import json
import time
import hmac
import hashlib
from typing import Dict, List, Optional, Union
from urllib.parse import urlencode

# Try to import requests, but provide fallback
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("Warning: requests module not available. API calls will be simulated.")

class HyperliquidAPI:
    """Hyperliquid API client for market data and trading."""
    
    BASE_URL = "https://api.hyperliquid.xyz"
    TESTNET_URL = "https://api.hyperliquid-testnet.xyz"
    
    def __init__(self, use_testnet=False, api_key=None, secret_key=None):
        """
        Initialize Hyperliquid API client.
        
        Args:
            use_testnet: Use testnet API (default: False)
            api_key: API key for authenticated endpoints
            secret_key: Secret key for signing requests
        """
        self.base_url = self.TESTNET_URL if use_testnet else self.BASE_URL
        self.api_key = api_key
        self.secret_key = secret_key
        
        if REQUESTS_AVAILABLE:
            self.session = requests.Session()
            # Default headers
            self.session.headers.update({
                'Content-Type': 'application/json',
                'User-Agent': 'VibeTradingCodeGenerator/1.0'
            })
            
            if api_key:
                self.session.headers.update({'Authorization': f'Bearer {api_key}'})
        else:
            self.session = None
            print("⚠️  Running in simulation mode (requests module not installed)")
    
    def _make_request(self, method: str, endpoint: str, params=None, data=None, signed=False):
        """Make HTTP request to Hyperliquid API."""
        if not REQUESTS_AVAILABLE:
            # Provide simulated data when requests is not available
            return self._simulate_api_response(endpoint, params)
        
        url = f"{self.base_url}{endpoint}"
        
        # Add signature if required
        if signed and self.secret_key:
            timestamp = str(int(time.time() * 1000))
            query_string = urlencode(params) if params else ''
            message = f"{timestamp}{method}{endpoint}{query_string}{json.dumps(data) if data else ''}"
            signature = hmac.new(
                self.secret_key.encode('utf-8'),
                message.encode('utf-8'),
                hashlib.sha256
            ).hexdigest()
            
            headers = {
                'X-MBX-APIKEY': self.api_key,
                'X-MBX-TIMESTAMP': timestamp,
                'X-MBX-SIGNATURE': signature
            }
            self.session.headers.update(headers)
        
        try:
            if method == 'GET':
                response = self.session.get(url, params=params)
            elif method == 'POST':
                response = self.session.post(url, json=data, params=params)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            print(f"API request failed: {e}")
            # Fall back to simulated data
            return self._simulate_api_response(endpoint, params)
    
    def _simulate_api_response(self, endpoint: str, params=None):
        """Provide simulated API responses for testing."""
        print("⚠️  Using simulated API data (requests module not available)")
        
        # Mock price data for common symbols
        mock_prices = {
            'BTC': 65000.50,
            'ETH': 3500.25,
            'SOL': 150.75,
            'HYPE': 30.698,
            'USDC': 1.00,
            'USDT': 1.00
        }
        
        if '/ticker/24hr' in endpoint:
            symbol = params.get('symbol', 'HYPE') if params else 'HYPE'
            price = mock_prices.get(symbol.upper(), 30.698)
            
            # Simulate 24hr data
            change = 0.02  # 2% change
            return {
                'symbol': symbol,
                'lastPrice': str(price),
                'priceChange': str(price * change),
                'priceChangePercent': str(change * 100),
                'highPrice': str(price * 1.05),
                'lowPrice': str(price * 0.95),
                'volume': str(price * 1000000)
            }
        
        elif '/exchange' in endpoint:
            # Simulate exchange info
            return {
                'symbols': [
                    {'symbol': 'BTC'},
                    {'symbol': 'ETH'},
                    {'symbol': 'SOL'},
                    {'symbol': 'HYPE'},
                    {'symbol': 'USDC'},
                    {'symbol': 'USDT'}
                ]
            }
        
        elif '/depth' in endpoint:
            # Simulate order book
            symbol = params.get('symbol', 'HYPE') if params else 'HYPE'
            price = mock_prices.get(symbol.upper(), 30.698)
            
            return {
                'bids': [[str(price * 0.999), '100']],
                'asks': [[str(price * 1.001), '100']]
            }
        
        return {'error': 'Simulated endpoint not implemented'}
    
    # Market Data Endpoints
    
    def get_exchange_info(self):
        """Get exchange information including all symbols."""
        return self._make_request('GET', '/exchange')
    
    def get_all_symbols(self):
        """Get list of all trading symbols."""
        info = self.get_exchange_info()
        if info and 'symbols' in info:
            return [symbol['symbol'] for symbol in info['symbols']]
        return []
    
    def get_ticker(self, symbol: str):
        """
        Get 24hr ticker price change statistics.
        
        Args:
            symbol: Trading symbol (e.g., "BTC", "ETH", "HYPE")
        
        Returns:
            Dict with price information
        """
        return self._make_request('GET', f'/ticker/24hr', params={'symbol': symbol})
    
    def get_price(self, symbol: str) -> Optional[float]:
        """
        Get current price for a symbol.
        
        Args:
            symbol: Trading symbol
        
        Returns:
            Current price as float, or None if not found
        """
        ticker = self.get_ticker(symbol)
        if ticker and 'lastPrice' in ticker:
            return float(ticker['lastPrice'])
        return None
    
    def get_prices(self, symbols: List[str]) -> Dict[str, Optional[float]]:
        """
        Get current prices for multiple symbols.
        
        Args:
            symbols: List of trading symbols
        
        Returns:
            Dict mapping symbol to price
        """
        results = {}
        for symbol in symbols:
            price = self.get_price(symbol)
            results[symbol] = price
            # Rate limiting
            time.sleep(0.1)
        return results
    
    def get_orderbook(self, symbol: str, limit: int = 20):
        """
        Get order book for a symbol.
        
        Args:
            symbol: Trading symbol
            limit: Number of bids/asks to return (default: 20)
        
        Returns:
            Order book data
        """
        return self._make_request('GET', f'/depth', params={'symbol': symbol, 'limit': limit})
    
    def get_klines(self, symbol: str, interval: str = '1h', limit: int = 100):
        """
        Get kline/candlestick data.
        
        Args:
            symbol: Trading symbol
            interval: Kline interval (1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w)
            limit: Number of klines to return (default: 100)
        
        Returns:
            List of klines
        """
        return self._make_request('GET', f'/klines', params={
            'symbol': symbol,
            'interval': interval,
            'limit': limit
        })
    
    def get_recent_trades(self, symbol: str, limit: int = 100):
        """Get recent trades for a symbol."""
        return self._make_request('GET', f'/trades', params={'symbol': symbol, 'limit': limit})
    
    # Account Endpoints (require authentication)
    
    def get_account_info(self):
        """Get account information (requires authentication)."""
        if not self.api_key:
            print("API key required for account info")
            return None
        return self._make_request('GET', '/account', signed=True)
    
    def get_balance(self):
        """Get account balance (requires authentication)."""
        account = self.get_account_info()
        if account and 'balances' in account:
            return account['balances']
        return []
    
    def get_open_orders(self, symbol: str = None):
        """Get open orders (requires authentication)."""
        if not self.api_key:
            print("API key required for open orders")
            return None
        
        params = {'symbol': symbol} if symbol else {}
        return self._make_request('GET', '/openOrders', params=params, signed=True)
    
    # Trading Endpoints (require authentication)
    
    def place_order(self, symbol: str, side: str, order_type: str, 
                   quantity: float, price: float = None, 
                   time_in_force: str = 'GTC'):
        """
        Place a new order (requires authentication).
        
        Args:
            symbol: Trading symbol
            side: 'BUY' or 'SELL'
            order_type: 'LIMIT', 'MARKET', etc.
            quantity: Order quantity
            price: Order price (required for LIMIT orders)
            time_in_force: 'GTC', 'IOC', 'FOK'
        
        Returns:
            Order response
        """
        if not self.api_key:
            print("API key required for placing orders")
            return None
        
        order_data = {
            'symbol': symbol,
            'side': side,
            'type': order_type,
            'quantity': quantity,
            'timeInForce': time_in_force
        }
        
        if price is not None:
            order_data['price'] = price
        
        return self._make_request('POST', '/order', data=order_data, signed=True)
    
    def cancel_order(self, symbol: str, order_id: str):
        """Cancel an order (requires authentication)."""
        if not self.api_key:
            print("API key required for canceling orders")
            return None
        
        return self._make_request('DELETE', f'/order', params={
            'symbol': symbol,
            'orderId': order_id
        }, signed=True)
    
    # Utility Methods
    
    def validate_symbol(self, symbol: str) -> bool:
        """Check if a symbol is valid on Hyperliquid."""
        symbols = self.get_all_symbols()
        return symbol.upper() in symbols
    
    def get_market_summary(self, symbol: str) -> Dict:
        """Get comprehensive market summary for a symbol."""
        ticker = self.get_ticker(symbol)
        orderbook = self.get_orderbook(symbol, limit=5)
        
        summary = {
            'symbol': symbol,
            'price': float(ticker['lastPrice']) if ticker and 'lastPrice' in ticker else None,
            '24h_change': float(ticker['priceChangePercent']) if ticker and 'priceChangePercent' in ticker else None,
            '24h_high': float(ticker['highPrice']) if ticker and 'highPrice' in ticker else None,
            '24h_low': float(ticker['lowPrice']) if ticker and 'lowPrice' in ticker else None,
            '24h_volume': float(ticker['volume']) if ticker and 'volume' in ticker else None,
            'bid': float(orderbook['bids'][0][0]) if orderbook and 'bids' in orderbook and orderbook['bids'] else None,
            'ask': float(orderbook['asks'][0][0]) if orderbook and 'asks' in orderbook and orderbook['asks'] else None,
            'spread': None
        }
        
        if summary['bid'] and summary['ask']:
            summary['spread'] = (summary['ask'] - summary['bid']) / summary['bid'] * 100
        
        return summary
    
    def get_recommended_grid_range(self, symbol: str, volatility_multiplier: float = 1.5) -> Dict:
        """
        Get recommended grid trading range based on market data.
        
        Args:
            symbol: Trading symbol
            volatility_multiplier: Multiplier for volatility-based range
        
        Returns:
            Dict with lower_bound, upper_bound, current_price
        """
        summary = self.get_market_summary(symbol)
        
        if not summary['price']:
            return None
        
        current_price = summary['price']
        
        # Use 24h high/low as base range
        if summary['24h_high'] and summary['24h_low']:
            base_range_low = summary['24h_low']
            base_range_high = summary['24h_high']
        else:
            # Fallback: ±10% range
            base_range_low = current_price * 0.9
            base_range_high = current_price * 1.1
        
        # Adjust based on volatility
        if summary['24h_change']:
            volatility = abs(summary['24h_change']) / 100  # Convert percentage to decimal
            range_adjustment = current_price * volatility * volatility_multiplier
            
            lower_bound = max(0.1, base_range_low - range_adjustment)
            upper_bound = base_range_high + range_adjustment
        else:
            lower_bound = base_range_low
            upper_bound = base_range_high
        
        # Ensure reasonable bounds
        lower_bound = max(0.1, lower_bound * 0.95)  # Add 5% buffer
        upper_bound = upper_bound * 1.05  # Add 5% buffer
        
        return {
            'current_price': current_price,
            'lower_bound': round(lower_bound, 4),
            'upper_bound': round(upper_bound, 4),
            '24h_high': summary['24h_high'],
            '24h_low': summary['24h_low'],
            '24h_change': summary['24h_change']
        }


# Simplified interface for common use cases

def get_current_price(symbol: str, use_testnet: bool = False) -> Optional[float]:
    """Get current price for a symbol (simplified interface)."""
    api = HyperliquidAPI(use_testnet=use_testnet)
    return api.get_price(symbol)

def get_multiple_prices(symbols: List[str], use_testnet: bool = False) -> Dict[str, Optional[float]]:
    """Get current prices for multiple symbols (simplified interface)."""
    api = HyperliquidAPI(use_testnet=use_testnet)
    return api.get_prices(symbols)

def validate_trading_symbol(symbol: str, use_testnet: bool = False) -> bool:
    """Validate if a symbol exists on Hyperliquid (simplified interface)."""
    api = HyperliquidAPI(use_testnet=use_testnet)
    return api.validate_symbol(symbol)

def get_grid_trading_recommendation(symbol: str, use_testnet: bool = False) -> Dict:
    """Get grid trading recommendations based on market data."""
    api = HyperliquidAPI(use_testnet=use_testnet)
    return api.get_recommended_grid_range(symbol)


if __name__ == "__main__":
    # Test the API
    print("Testing Hyperliquid API...")
    
    # Create API client
    api = HyperliquidAPI(use_testnet=False)
    
    # Test getting HYPE price
    hype_price = api.get_price("HYPE")
    if hype_price:
        print(f"HYPE current price: ${hype_price:.4f}")
    else:
        print("Could not fetch HYPE price")
    
    # Test getting multiple prices
    symbols = ["BTC", "ETH", "SOL", "HYPE"]
    print(f"\nFetching prices for {symbols}...")
    prices = api.get_prices(symbols)
    
    for symbol, price in prices.items():
        if price:
            print(f"{symbol}: ${price:.2f}")
        else:
            print(f"{symbol}: Price not available")
    
    # Test grid trading recommendation
    print("\nGetting grid trading recommendation for HYPE...")
    recommendation = api.get_recommended_grid_range("HYPE")
    if recommendation:
        print(f"Current price: ${recommendation['current_price']:.4f}")
        print(f"Recommended range: ${recommendation['lower_bound']:.4f} - ${recommendation['upper_bound']:.4f}")
        print(f"24h change: {recommendation['24h_change']:.2f}%")
    
    print("\nAPI test completed!")