#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Data Downloader for Hyperliquid Historical Data
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
import requests

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HyperliquidDataDownloader:
    """Download historical data from Hyperliquid API"""
    
    MAINNET_API_URL = "https://api.hyperliquid.xyz"
    TESTNET_API_URL = "https://api.hyperliquid-testnet.xyz"
    
    def __init__(self, use_testnet=False, data_dir="data/historical"):
        self.use_testnet = use_testnet
        self.base_url = self.TESTNET_API_URL if use_testnet else self.MAINNET_API_URL
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache
        self._markets_cache = None
        self._cache_time = None
        self.CACHE_DURATION = 8 * 3600  # 8 hours in seconds
        
        logger.info(f"DataDownloader initialized (testnet: {use_testnet})")
    
    def _make_request(self, endpoint, method="POST", data=None):
        """Make API request"""
        url = f"{self.base_url}{endpoint}"
        headers = {"Content-Type": "application/json"}
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=data, timeout=30)
            else:
                response = requests.post(url, headers=headers, json=data, timeout=30)
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"API request failed: {e}")
            return None
    
    def load_hyperliquid_markets(self):
        """Load market data with caching"""
        now = time.time()
        if self._markets_cache and self._cache_time and (now - self._cache_time) < self.CACHE_DURATION:
            logger.info("Using cached market data")
            return self._markets_cache
        
        logger.info("Fetching market data...")
        try:
            response = self._make_request("/info", data={"type": "meta"})
            if not response:
                return {}
            
            markets = {}
            for asset in response.get("universe", []):
                name = asset.get("name", "")
                if name:
                    markets[name] = {
                        "name": name,
                        "sz_decimals": asset.get("szDecimals", 0),
                        "px_decimals": asset.get("pxDecimals", 0),
                        "max_leverage": asset.get("maxLeverage", 1)
                    }
            
            self._markets_cache = markets
            self._cache_time = now
            logger.info(f"Loaded {len(markets)} markets")
            return markets
            
        except Exception as e:
            logger.error(f"Error loading markets: {e}")
            return {}
    
    def download_ohlcv(self, symbol, interval="1h", days=30):
        """Download OHLCV data"""
        cache_file = self.data_dir / f"{symbol}_{interval}_{days}d.csv"
        
        # Check cache
        if cache_file.exists():
            try:
                df = pd.read_csv(cache_file, index_col=0, parse_dates=True)
                if not df.empty:
                    logger.info(f"Loaded cached data: {len(df)} rows")
                    return df
            except Exception as e:
                logger.warning(f"Cache load failed: {e}")
        
        logger.info(f"Downloading {symbol} {interval} data ({days} days)...")
        
        try:
            # Map interval
            interval_map = {"1m": "1m", "5m": "5m", "15m": "15m", "30m": "30m", 
                          "1h": "1h", "4h": "4h", "1d": "1d"}
            if interval not in interval_map:
                logger.error(f"Unsupported interval: {interval}")
                return None
            
            # Calculate time range
            end = datetime.now(timezone.utc)
            start = end - timedelta(days=days)
            start_ms = int(start.timestamp() * 1000)
            end_ms = int(end.timestamp() * 1000)
            
            # Request data
            request_data = {
                "type": "candleSnapshot",
                "req": {
                    "coin": symbol,
                    "interval": interval_map[interval],
                    "startTime": start_ms,
                    "endTime": end_ms
                }
            }
            
            response = self._make_request("/info", data=request_data)
            if not response or "candles" not in response:
                logger.error(f"No data for {symbol}")
                return None
            
            candles = response["candles"]
            if not candles:
                logger.warning(f"Empty data for {symbol}")
                return None
            
            # Create DataFrame
            df = pd.DataFrame(candles)
            df = df.rename(columns={
                "t": "timestamp",
                "o": "open",
                "h": "high",
                "l": "low",
                "c": "close",
                "v": "volume"
            })
            
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
            df.set_index("timestamp", inplace=True)
            
            # Convert numeric columns
            for col in ["open", "high", "low", "close", "volume"]:
                df[col] = pd.to_numeric(df[col], errors="coerce")
            
            df = df.sort_index()
            df = df[~df.index.duplicated(keep="first")]
            
            # Save cache
            df.to_csv(cache_file)
            logger.info(f"Saved {len(df)} rows to {cache_file}")
            
            return df
            
        except Exception as e:
            logger.error(f"Download failed: {e}")
            return None
    
    def download_funding_rates(self, symbol, days=30):
        """Download funding rate data"""
        cache_file = self.data_dir / f"{symbol}_funding_{days}d.csv"
        
        if cache_file.exists():
            try:
                df = pd.read_csv(cache_file, index_col=0, parse_dates=True)
                if not df.empty:
                    logger.info(f"Loaded cached funding: {len(df)} rows")
                    return df
            except Exception as e:
                logger.warning(f"Funding cache load failed: {e}")
        
        logger.info(f"Downloading funding rates for {symbol}...")
        
        try:
            end = datetime.now(timezone.utc)
            start = end - timedelta(days=days)
            start_ms = int(start.timestamp() * 1000)
            end_ms = int(end.timestamp() * 1000)
            
            request_data = {
                "type": "fundingHistory",
                "coin": symbol,
                "startTime": start_ms,
                "endTime": end_ms
            }
            
            response = self._make_request("/info", data=request_data)
            if not response:
                return None
            
            df = pd.DataFrame(response)
            if df.empty:
                return None
            
            df = df.rename(columns={"time": "timestamp", "fundingRate": "funding_rate"})
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms", utc=True)
            df.set_index("timestamp", inplace=True)
            df["funding_rate"] = pd.to_numeric(df["funding_rate"], errors="coerce")
            df = df.sort_index()
            
            df.to_csv(cache_file)
            logger.info(f"Saved {len(df)} funding rates")
            
            return df
            
        except Exception as e:
            logger.error(f"Funding download failed: {e}")
            return None
    
    def get_available_symbols(self):
        """Get list of symbols"""
        markets = self.load_hyperliquid_markets()
        return list(markets.keys())
    
    def get_data_summary(self):
        """Get data summary"""
        summary = {"files": [], "total_size_mb": 0}
        
        for file in self.data_dir.glob("*.csv"):
            size_mb = file.stat().st_size / (1024 * 1024)
            summary["files"].append({
                "name": file.name,
                "size_mb": size_mb,
                "modified": datetime.fromtimestamp(file.stat().st_mtime).isoformat()
            })
            summary["total_size_mb"] += size_mb
        
        summary["file_count"] = len(summary["files"])
        return summary

def main():
    """Test function"""
    downloader = HyperliquidDataDownloader(use_testnet=True)
    
    # Test market loading
    markets = downloader.load_hyperliquid_markets()
    print(f"Loaded {len(markets)} markets")
    
    # Test data download
    symbols = ["BTC", "ETH", "HYPE"]
    for symbol in symbols:
        if symbol in markets:
            print(f"\nDownloading {symbol}...")
            data = downloader.download_ohlcv(symbol, days=7)
            if data is not None:
                print(f"  OHLCV: {len(data)} rows")
            
            funding = downloader.download_funding_rates(symbol, days=7)
            if funding is not None:
                print(f"  Funding: {len(funding)} rows")
    
    # Show summary
    summary = downloader.get_data_summary()
    print(f"\nData summary: {summary['file_count']} files, {summary['total_size_mb']:.2f} MB")

if __name__ == "__main__":
    main()