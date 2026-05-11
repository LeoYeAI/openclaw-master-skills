"""
Options Chain Analyzer

Fetches and parses options chains from Yahoo Finance.
Handles caching, rate limiting, and data normalization.
"""

import time
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import os
import pickle

import yfinance

logger = logging.getLogger(__name__)


@dataclass
class OptionChain:
    """Container for full options chain data"""
    ticker: str
    underlying_price: float
    expiration_date: str
    expiration_timestamp: int
    dte: int
    calls: List[Dict] = field(default_factory=list)
    puts: List[Dict] = field(default_factory=list)
    
    @property
    def all_options(self) -> List[Dict]:
        """All options combined"""
        result = []
        for opt in self.calls:
            opt['type'] = 'call'
            result.append(opt)
        for opt in self.puts:
            opt['type'] = 'put'
            result.append(opt)
        return result


class ChainFetcher:
    """
    Fetches options chains from Yahoo Finance with rate limiting
    """
    
    def __init__(self, cache_dir: str = None, rate_limit_delay: float = 0.5):
        self.rate_limit_delay = rate_limit_delay
        self.last_fetch_time = 0
        
        # Setup cache
        if cache_dir is None:
            cache_dir = os.path.expanduser('~/.openclaw/options_cache')
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
        
        self.cache = {}
        self.cache_ttl = 300  # 5 minute cache
    
    def _rate_limit(self):
        """Ensure we don't exceed rate limits"""
        elapsed = time.time() - self.last_fetch_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_fetch_time = time.time()
    
    def _get_cache_key(self, ticker: str, date_timestamp: int = None) -> str:
        """Generate cache key"""
        if date_timestamp:
            return f"{ticker}_{date_timestamp}"
        return f"{ticker}_all"
    
    def _get_cache_path(self, cache_key: str) -> str:
        """Get cache file path"""
        return os.path.join(self.cache_dir, f"{cache_key}.pkl")
    
    def _load_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Load data from cache if valid"""
        cache_path = self._get_cache_path(cache_key)
        
        if not os.path.exists(cache_path):
            return None
        
        try:
            with open(cache_path, 'rb') as f:
                cached = pickle.load(f)
            
            # Check TTL
            if time.time() - cached.get('timestamp', 0) > self.cache_ttl:
                return None
            
            return cached.get('data')
        except (FileNotFoundError, PermissionError, pickle.PickleError, IOError):
            return None
    
    def _save_to_cache(self, cache_key: str, data: Dict):
        """Save data to cache"""
        cache_path = self._get_cache_path(cache_key)
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump({'timestamp': time.time(), 'data': data}, f)
        except (FileNotFoundError, PermissionError, pickle.PickleError, IOError) as e:
            logger.warning(f"Failed to save cache: {e}")
    
    def fetch_quote(self, ticker: str) -> Optional[Dict]:
        """Fetch current stock quote via yfinance"""
        self._rate_limit()
        
        try:
            info = yfinance.Ticker(ticker).info
            if not info or 'regularMarketPrice' not in info:
                return None
            return info
        except Exception as e:
            print(f"Error fetching quote for {ticker}: {e}")
            return None
    
    def fetch_expirations(self, ticker: str) -> List[Dict]:
        """Fetch available expiration dates via yfinance"""
        cache_key = self._get_cache_key(ticker)
        cached = self._load_from_cache(cache_key)
        
        if cached and 'expirations' in cached:
            return cached['expirations']
        
        self._rate_limit()
        
        try:
            tk = yfinance.Ticker(ticker)
            date_strings = tk.options  # tuple of 'YYYY-MM-DD' strings
            
            if not date_strings:
                return []
            
            expirations = []
            for date_str in date_strings:
                try:
                    dt = datetime.strptime(date_str, '%Y-%m-%d')
                    timestamp = int(dt.timestamp())
                    dte = (dt.date() - datetime.now().date()).days
                    
                    if dte >= 0:
                        expirations.append({
                            'date': date_str,
                            'timestamp': timestamp,
                            'dte': dte,
                            'datetime': dt
                        })
                except (ValueError, TypeError) as e:
                    logger.debug(f"Skipping invalid expiration date {date_str}: {e}")
                    continue
            
            expirations.sort(key=lambda x: x['dte'])
            self._save_to_cache(cache_key, {'expirations': expirations})
            
            return expirations
            
        except Exception as e:
            print(f"Error fetching expirations for {ticker}: {e}")
            return []
    
    def fetch_chain_for_date(self, ticker: str, timestamp: int) -> Optional[OptionChain]:
        """Fetch options chain for specific expiration date via yfinance"""
        cache_key = self._get_cache_key(ticker, timestamp)
        cached = self._load_from_cache(cache_key)

        if cached:
            return OptionChain(**cached)

        self._rate_limit()

        try:
            date_dt = datetime.fromtimestamp(timestamp)
            date_str = date_dt.strftime('%Y-%m-%d')

            tk = yfinance.Ticker(ticker)

            # Get underlying price
            underlying = tk.info.get('regularMarketPrice', 0) or 0

            # Fetch option chain for this date
            opt_chain = tk.option_chain(date_str)

            if opt_chain.calls.empty and opt_chain.puts.empty:
                return None

            dte = (date_dt.date() - datetime.now().date()).days

            calls = self._normalize_options(
                opt_chain.calls.to_dict('records'),
                'call',
                underlying,
                date_str,
                dte
            )

            puts = self._normalize_options(
                opt_chain.puts.to_dict('records'),
                'put',
                underlying,
                date_str,
                dte
            )

            if not calls and not puts:
                return None

            chain = OptionChain(
                ticker=ticker,
                underlying_price=underlying,
                expiration_date=date_str,
                expiration_timestamp=timestamp,
                dte=dte,
                calls=calls,
                puts=puts
            )

            self._save_to_cache(cache_key, chain.__dict__)
            return chain

        except Exception as e:
            print(f"Error fetching chain for {ticker} @ {timestamp}: {e}")
            return None
    
    def _normalize_options(self, options: List[Dict], opt_type: str,
                          underlying: float, expiration: str, dte: int) -> List[Dict]:
        """Normalize option data to consistent format with edge case handling"""
        normalized = []

        for opt in options:
            # Handle missing values gracefully
            # yfinance uses camelCase: lastPrice, openInterest, impliedVolatility
            bid = opt.get('bid', 0) or 0
            ask = opt.get('ask', 0) or 0
            last = opt.get('lastPrice', opt.get('lastprice', 0)) or 0
            volume = opt.get('volume', 0) or 0
            oi = opt.get('openInterest', opt.get('openinterest', 0)) or 0
            iv = opt.get('impliedVolatility', opt.get('impliedvolatility', 0)) or 0
            strike = opt.get('strike', 0) or 0
            
            # Handle NaN values from pandas/yfinance
            import math
            def safe_num(val, default=0):
                if val is None:
                    return default
                if isinstance(val, float) and math.isnan(val):
                    return default
                return val
            
            bid = safe_num(bid)
            ask = safe_num(ask)
            last = safe_num(last)
            volume = safe_num(volume)
            oi = safe_num(oi)
            iv = safe_num(iv)
            strike = safe_num(strike)

            # Yahoo returns IV as decimal (e.g., 0.25 for 25%)
            if iv > 1:
                iv = iv / 100.0

            # Handle missing bid/ask - use lastPrice as fallback
            # This is critical for post-market data when bid/ask may be 0
            has_valid_bid_ask = bid > 0 and ask > 0

            if has_valid_bid_ask:
                mid_price = (bid + ask) / 2
                spread = ask - bid
            else:
                # Fallback: use lastPrice as mid, 0 spread
                # Flag as potentially illiquid
                mid_price = last if last > 0 else 0
                spread = 0

            # Flag wide spreads as illiquid (>20% of option value)
            spread_pct = 0
            if mid_price > 0:
                spread_pct = spread / mid_price
            illiquid = spread_pct > 0.20 or not has_valid_bid_ask

            # Flag post-market/zero volume as potentially stale
            stale_data = volume == 0 and oi < 10

            norm_opt = {
                'strike': float(opt.get('strike', 0)),
                'bid': float(bid),
                'ask': float(ask),
                'last_price': float(last),
                'mid_price': float(mid_price),
                'spread': float(spread),
                'spread_pct': float(spread_pct),
                'volume': int(volume),
                'open_interest': int(oi),
                'implied_vol': float(iv),
                'type': opt_type,
                'underlying': underlying,
                'expiration': expiration,
                'dte': dte,
                # Liquidity flags
                'illiquid': illiquid,
                'stale_data': stale_data,
                'has_valid_bid_ask': has_valid_bid_ask,
                # Greeks (if available from Yahoo)
                'delta': opt.get('delta'),
                'gamma': opt.get('gamma'),
                'theta': opt.get('theta'),
                'vega': opt.get('vega'),
            }

            normalized.append(norm_opt)

        # Sort by strike
        normalized.sort(key=lambda x: x['strike'])

        return normalized
    
    def fetch_default_chain(self, ticker: str) -> Optional[OptionChain]:
        """
        Fetch the default options chain (nearest expiration) via yfinance
        """
        cache_key = self._get_cache_key(ticker, 'default')
        cached = self._load_from_cache(cache_key)
        
        if cached:
            return OptionChain(**cached)
        
        self._rate_limit()
        
        try:
            tk = yfinance.Ticker(ticker)
            
            # Get available expirations
            exp_dates = tk.options
            if not exp_dates:
                return None
            
            # Use nearest expiration
            nearest_date = exp_dates[0]
            
            # Get underlying price
            underlying = tk.info.get('regularMarketPrice', 0) or 0
            
            # Fetch chain
            opt_chain = tk.option_chain(nearest_date)
            
            exp_dt = datetime.strptime(nearest_date, '%Y-%m-%d')
            dte = (exp_dt.date() - datetime.now().date()).days
            timestamp = int(exp_dt.timestamp())
            
            calls = self._normalize_options(
                opt_chain.calls.to_dict('records'),
                'call',
                underlying,
                nearest_date,
                dte
            )
            
            puts = self._normalize_options(
                opt_chain.puts.to_dict('records'),
                'put',
                underlying,
                nearest_date,
                dte
            )
            
            chain = OptionChain(
                ticker=ticker,
                underlying_price=underlying,
                expiration_date=nearest_date,
                expiration_timestamp=timestamp,
                dte=dte,
                calls=calls,
                puts=puts
            )
            
            self._save_to_cache(cache_key, chain.__dict__)
            return chain
            
        except Exception as e:
            print(f"Error fetching default chain for {ticker}: {e}")
            return None
    
    def fetch_multiple_expirations(self, ticker: str, num_expirations: int = 4,
                                   min_dte: int = 7, max_dte: int = 45) -> List[OptionChain]:
        """
        Fetch chains for multiple expiration dates
        
        Filters for DTE within specified range (default 7-45 days)
        """
        # First get the default chain (which works reliably)
        default_chain = self.fetch_default_chain(ticker)
        
        if not default_chain:
            return []
        
        # Check if default chain fits DTE criteria
        chains = []
        if min_dte <= default_chain.dte <= max_dte:
            chains.append(default_chain)
        
        # Get available expirations
        expirations = self.fetch_expirations(ticker)
        
        # Filter by DTE range
        filtered = [e for e in expirations 
                   if min_dte <= e['dte'] <= max_dte 
                   and e['dte'] != default_chain.dte]
        
        # Try to fetch additional chains
        for exp in filtered[:num_expirations-1]:
            chain = self.fetch_chain_for_date(ticker, exp['timestamp'])
            if chain and (chain.calls or chain.puts):
                chains.append(chain)
        
        return chains


class ChainAnalyzer:
    """
    Analyze options chains for trading opportunities
    """
    
    def __init__(self, fetcher: ChainFetcher = None):
        self.fetcher = fetcher or ChainFetcher()
    
    def get_atm_option(self, chain: OptionChain, opt_type: str = 'call',
                      offset: int = 0) -> Optional[Dict]:
        """
        Get at-the-money (or near-ATM) option
        
        offset: 0=ATM, positive=OTM, negative=ITM
        """
        options = chain.calls if opt_type == 'call' else chain.puts
        
        if not options:
            return None
        
        # Find closest to ATM
        strikes = [opt['strike'] for opt in options]
        atm_idx = min(range(len(strikes)), 
                     key=lambda i: abs(strikes[i] - chain.underlying_price))
        
        # Apply offset
        target_idx = max(0, min(len(options) - 1, atm_idx + offset))
        
        return options[target_idx]
    
    def get_otm_option(self, chain: OptionChain, opt_type: str = 'call',
                      delta_target: float = 0.30) -> Optional[Dict]:
        """
        Get OTM option near target delta
        
        For small accounts, we typically target ~30 delta for short options
        """
        options = chain.calls if opt_type == 'call' else chain.puts
        
        if not options:
            return None
        
        # Find closest to target delta if available, otherwise by strike distance
        best_opt = None
        best_score = float('inf')
        
        for opt in options:
            # Skip if too wide spread (>20% of option value)
            if opt['mid_price'] > 0 and opt['spread'] / opt['mid_price'] > 0.20:
                continue
            
            # Skip low/no volume (liquidity check)
            if opt['volume'] < 1 and opt['open_interest'] < 10:
                continue
            
            # Calculate score based on strike distance from target
            if opt_type == 'call':
                # OTM call: strike > underlying
                if opt['strike'] <= chain.underlying_price:
                    continue
            else:
                # OTM put: strike < underlying
                if opt['strike'] >= chain.underlying_price:
                    continue
            
            # Score by delta if available, otherwise by distance
            if opt.get('delta') is not None:
                delta = abs(opt['delta'])
                score = abs(delta - delta_target)
            else:
                # Score by moneyness
                distance = abs(opt['strike'] - chain.underlying_price)
                score = distance / chain.underlying_price
            
            if score < best_score:
                best_score = score
                best_opt = opt
        
        return best_opt
    
    def get_strikes_by_width(self, chain: OptionChain, opt_type: str = 'put',
                            width: float = 5.0, start_otm: bool = True) -> List[List[Dict]]:
        """
        Get strike pairs at specified width for spreads
        
        Returns list of [short_strike, long_strike] pairs
        """
        options = chain.calls if opt_type == 'call' else chain.puts
        
        if not options:
            return []
        
        pairs = []
        strikes = [opt['strike'] for opt in options]
        
        for i, opt in enumerate(options):
            # For put spreads, we sell higher strike, buy lower
            # For call spreads, we sell lower strike, buy higher
            
            if opt_type == 'put':
                # Look for long strike $width below short strike
                target_strike = opt['strike'] - width
                # Find closest available strike
                try:
                    j = min(range(len(strikes)), 
                           key=lambda k: abs(strikes[k] - target_strike))
                    if abs(strikes[j] - target_strike) < 0.5:  # Within $0.50
                        pairs.append([opt, options[j]])
                except (ValueError, IndexError) as e:
                    logger.debug(f"Could not find matching put strike: {e}")
            else:  # call
                # Look for long strike $width above short strike
                target_strike = opt['strike'] + width
                try:
                    j = min(range(len(strikes)),
                           key=lambda k: abs(strikes[k] - target_strike))
                    if abs(strikes[j] - target_strike) < 0.5:
                        pairs.append([opt, options[j]])
                except (ValueError, IndexError) as e:
                    logger.debug(f"Could not find matching call strike: {e}")
        
        return pairs
    
    def analyze_liquidity(self, chain: OptionChain) -> Dict:
        """
        Analyze liquidity of options chain
        """
        all_options = chain.all_options
        
        if not all_options:
            return {'score': 0, 'bid_ask_spread_avg': 1.0, 'volume_avg': 0}
        
        # Calculate average bid-ask spread as % of mid price
        spreads = []
        volumes = []
        
        for opt in all_options:
            if opt['mid_price'] > 0.05:  # Skip deep OTM
                spread_pct = opt['spread'] / opt['mid_price']
                spreads.append(spread_pct)
            volumes.append(opt['volume'])
        
        avg_spread = sum(spreads) / len(spreads) if spreads else 1.0
        avg_volume = sum(volumes) / len(volumes) if volumes else 0
        
        # Liquidity score (0-100)
        # Lower spread and higher volume = better
        spread_score = max(0, 100 - (avg_spread * 500))  # 0.20 spread = 0 score
        volume_score = min(100, avg_volume * 2)  # 50+ volume = 100
        
        score = (spread_score * 0.6) + (volume_score * 0.4)
        
        return {
            'score': score,
            'bid_ask_spread_avg': avg_spread,
            'volume_avg': avg_volume,
            'spread_score': spread_score,
            'volume_score': volume_score
        }
    
    def find_iv_skew(self, chain: OptionChain) -> Dict:
        """
        Analyze IV skew in the chain
        
        Returns dict with skew metrics
        """
        calls = chain.calls
        puts = chain.puts
        
        if not calls or not puts:
            return {}
        
        # Find ATM options
        atm_call = self.get_atm_option(chain, 'call')
        atm_put = self.get_atm_option(chain, 'put')
        
        if not atm_call or not atm_put:
            return {}
        
        atm_iv = (atm_call['implied_vol'] + atm_put['implied_vol']) / 2
        
        # Find ~10% OTM options
        otm_put_target = chain.underlying_price * 0.90
        otm_call_target = chain.underlying_price * 1.10
        
        otm_put_iv = atm_put['implied_vol']
        otm_call_iv = atm_call['implied_vol']
        
        for put in puts:
            if put['strike'] <= otm_put_target:
                otm_put_iv = put['implied_vol']
                break
        
        for call in calls:
            if call['strike'] >= otm_call_target:
                otm_call_iv = call['implied_vol']
                break
        
        # Calculate skew
        put_skew = (otm_put_iv - atm_iv) / atm_iv if atm_iv > 0 else 0
        call_skew = (otm_call_iv - atm_iv) / atm_iv if atm_iv > 0 else 0
        
        return {
            'atm_iv': atm_iv,
            'otm_put_iv': otm_put_iv,
            'otm_call_iv': otm_call_iv,
            'put_skew_pct': put_skew * 100,
            'call_skew_pct': call_skew * 100,
            'skew_bias': put_skew - call_skew  # Positive = fear of downside
        }


# Singleton instance for reuse
_default_fetcher = None
_default_analyzer = None

def get_fetcher() -> ChainFetcher:
    global _default_fetcher
    if _default_fetcher is None:
        _default_fetcher = ChainFetcher()
    return _default_fetcher

def get_analyzer() -> ChainAnalyzer:
    global _default_analyzer
    if _default_analyzer is None:
        _default_analyzer = ChainAnalyzer(get_fetcher())
    return _default_analyzer
