# -*- coding: utf-8 -*-
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prompt Parser - Parses natural language prompts to extract strategy information.
"""

import re
import json

class PromptParser:
    """Parses natural language prompts for strategy generation."""
    
    # Common trading symbols
    COMMON_SYMBOLS = {
        '比特币': 'BTC', 'btc': 'BTC', '比特币': 'BTC',
        '以太坊': 'ETH', 'eth': 'ETH', '以太坊': 'ETH',
        'solana': 'SOL', 'sol': 'SOL', '索拉纳': 'SOL',
        'bnb': 'BNB', '币安币': 'BNB',
        'xrp': 'XRP', '瑞波币': 'XRP',
        'ada': 'ADA', '卡尔达诺': 'ADA',
        'doge': 'DOGE', '狗狗币': 'DOGE',
        'dot': 'DOT', '波卡': 'DOT',
        'matic': 'MATIC', '马蹄': 'MATIC',
        'avax': 'AVAX', '雪崩': 'AVAX',
        'hype': 'HYPE', 'hyper': 'HYPE'  # 添加HYPE支持
    }
    
    # Strategy type keywords
    STRATEGY_KEYWORDS = {
        'rsi': 'rsi', '相对强弱指数': 'rsi',
        'macd': 'macd', '移动平均收敛发散': 'macd',
        '移动平均': 'moving_average', '均线': 'moving_average', 'ma': 'moving_average',
        '布林带': 'bollinger_bands', '布林': 'bollinger_bands', 'bb': 'bollinger_bands',
        '网格': 'grid_trading', '网格交易': 'grid_trading',
        '均值回归': 'mean_reversion', 'mean reversion': 'mean_reversion',
        '趋势跟踪': 'trend_following', '趋势': 'trend_following',
        '套利': 'arbitrage', 'arbitrage': 'arbitrage',
        '信号': 'signal_based', '信号驱动': 'signal_based',
        '定投': 'dca', '定期投资': 'dca',
        '对冲': 'hedging', 'hedge': 'hedging'
    }
    
    # Parameter patterns
    PARAMETER_PATTERNS = {
        'price': r'(\d+(?:\.\d+)?)[\s\-~到至]+(\d+(?:\.\d+)?)',
        'grid_count': r'(\d+)\s*个?网格',
        'grid_size': r'每个网格\s*(\d+(?:\.\d+)?)',
        'quantity': r'(\d+(?:\.\d+)?)\s*(?:个|枚|btc|eth|sol)',
        'percentage': r'(\d+(?:\.\d+)?)%',
        'rsi_threshold': r'RSI\s*[低于小于<]\s*(\d+)',
        'timeframe': r'(\d+[分钟小时天日])',
        'leverage': r'(\d+)倍杠杆'
    }
    
    def parse(self, prompt):
        """
        Parse natural language prompt to extract strategy information.
        
        Args:
            prompt: Natural language prompt describing the strategy
            
        Returns:
            Dictionary containing parsed strategy information
        """
        prompt_lower = prompt.lower()
        
        # Initialize result
        result = {
            'original_prompt': prompt,
            'name': self._extract_strategy_name(prompt),
            'type': self._extract_strategy_type(prompt_lower),
            'symbol': self._extract_symbol(prompt_lower),
            'parameters': self._extract_parameters(prompt),
            'tags': self._extract_tags(prompt_lower),
            'risk_preferences': self._extract_risk_preferences(prompt),
            'timeframe': self._extract_timeframe(prompt)
        }
        
        # Clean up parameters
        result['parameters'] = self._clean_parameters(result['parameters'])
        
        # Set default values if missing
        if not result['symbol']:
            result['symbol'] = 'BTC'
        
        if not result['name']:
            result['name'] = "{result['symbol']}_{result['type']}_strategy"
        
        return result
    
    def _extract_strategy_name(self, prompt):
        """Extract strategy name from prompt."""
        # Look for patterns like "生成一个XXX策略"
        name_patterns = [
            r'生成(?:一个)?([^，,。\.]+?)策略',
            r'创建(?:一个)?([^，,。\.]+?)策略',
            r'([^，,。\.]+?)交易策略'
        ]
        
        for pattern in name_patterns:
            match = re.search(pattern, prompt)
            if match:
                name = match.group(1).strip()
                # Clean up common prefixes
                name = re.sub(r'^(?:的|一个|我的)', '', name)
                return name
        
        return ""
    
    def _extract_strategy_type(self, prompt_lower):
        """Extract strategy type from prompt."""
        # Check for specific strategy types
        for keyword, strategy_type in self.STRATEGY_KEYWORDS.items():
            if keyword in prompt_lower:
                return strategy_type
        
        # Check for indicator-based strategies
        if any(word in prompt_lower for word in ['买入', '卖出', '交易']):
            return 'basic'
        
        # Default to basic strategy
        return 'basic'
    
    def _extract_symbol(self, prompt_lower):
        """Extract trading symbol from prompt."""
        # Check for common symbols
        for keyword, symbol in self.COMMON_SYMBOLS.items():
            if keyword in prompt_lower:
                return symbol
        
        # Look for uppercase symbols (like BTC, ETH)
        symbol_match = re.search(r'\b([A-Z]{2,5})\b', prompt_lower.upper())
        if symbol_match:
            return symbol_match.group(1)
        
        return ""
    
    def _extract_parameters(self, prompt):
        """Extract strategy parameters from prompt."""
        parameters = {}
        
        # Extract price range
        price_match = re.search(self.PARAMETER_PATTERNS['price'], prompt)
        if price_match:
            lower = float(price_match.group(1))
            upper = float(price_match.group(2))
            parameters['price_range'] = [lower, upper]
        
        # Extract grid count
        grid_count_match = re.search(self.PARAMETER_PATTERNS['grid_count'], prompt)
        if grid_count_match:
            parameters['grid_count'] = int(grid_count_match.group(1))
        
        # Extract grid size
        grid_size_match = re.search(self.PARAMETER_PATTERNS['grid_size'], prompt)
        if grid_size_match:
            parameters['grid_size'] = float(grid_size_match.group(1))
        
        # Extract quantity
        quantity_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:个|枚|btc|eth|sol|比特币|以太坊)', prompt, re.IGNORECASE)
        if quantity_match:
            parameters['quantity'] = float(quantity_match.group(1))
        
        # Extract RSI thresholds
        rsi_patterns = [
            r'RSI\s*[低于小于<]\s*(\d+)',
            r'RSI\s*[高于大于>]\s*(\d+)',
            r'(\d+)\s*以下买入',
            r'(\d+)\s*以上卖出'
        ]
        
        for pattern in rsi_patterns:
            matches = re.findall(pattern, prompt)
            for match in matches:
                if 'oversold' not in parameters and ('低于' in pattern or '以下' in pattern):
                    parameters['oversold_threshold'] = int(match)
                elif 'overbought' not in parameters and ('高于' in pattern or '以上' in pattern):
                    parameters['overbought_threshold'] = int(match)
        
        # Extract percentage values
        percentage_matches = re.findall(self.PARAMETER_PATTERNS['percentage'], prompt)
        if percentage_matches:
            parameters['percentages'] = [float(p) for p in percentage_matches]
        
        # Extract leverage
        leverage_match = re.search(self.PARAMETER_PATTERNS['leverage'], prompt)
        if leverage_match:
            parameters['leverage'] = int(leverage_match.group(1))
        
        # Extract timeframe
        timeframe_match = re.search(self.PARAMETER_PATTERNS['timeframe'], prompt)
        if timeframe_match:
            parameters['timeframe'] = timeframe_match.group(1)
        
        return parameters
    
    def _clean_parameters(self, parameters):
        """Clean and normalize parameters."""
        cleaned = parameters.copy()
        
        # Ensure price range is sorted
        if 'price_range' in cleaned:
            cleaned['price_range'] = sorted(cleaned['price_range'])
        
        # Set default RSI thresholds if not specified
        if 'oversold_threshold' not in cleaned and 'overbought_threshold' not in cleaned:
            if any(key in cleaned for key in ['rsi', '相对强弱指数']):
                cleaned['oversold_threshold'] = 30
                cleaned['overbought_threshold'] = 70
        
        # Convert timeframe to standard format
        if 'timeframe' in cleaned:
            timeframe = cleaned['timeframe']
            if '分钟' in timeframe:
                minutes = int(re.search(r'(\d+)', timeframe).group(1))
                cleaned['timeframe_minutes'] = minutes
            elif '小时' in timeframe:
                hours = int(re.search(r'(\d+)', timeframe).group(1))
                cleaned['timeframe_minutes'] = hours * 60
            elif '天' in timeframe or '日' in timeframe:
                days = int(re.search(r'(\d+)', timeframe).group(1))
                cleaned['timeframe_minutes'] = days * 24 * 60
        
        return cleaned
    
    def _extract_tags(self, prompt_lower):
        """Extract tags from prompt."""
        tags = []
        
        # Add strategy type tags
        strategy_type = self._extract_strategy_type(prompt_lower)
        if strategy_type:
            tags.append(strategy_type)
        
        # Add market type tags
        if any(word in prompt_lower for word in ['现货', 'spot']):
            tags.append('spot')
        if any(word in prompt_lower for word in ['合约', '永续', 'perp', 'futures']):
            tags.append('perp')
        
        # Add risk level tags
        if any(word in prompt_lower for word in ['保守', '稳健', '保守型']):
            tags.append('conservative')
        elif any(word in prompt_lower for word in ['激进', '高风险', '激进型']):
            tags.append('aggressive')
        else:
            tags.append('moderate')
        
        # Add signal integration tags
        if any(word in prompt_lower for word in ['信号', 'vibetrading', 'vibe trading']):
            tags.append('signal_integration')
        
        return tags
    
    def _extract_risk_preferences(self, prompt):
        """Extract risk management preferences."""
        risk_prefs = {
            'stop_loss': 0.05,  # 5% default stop loss
            'take_profit': 0.10,  # 10% default take profit
            'position_size': 0.01,  # 1% default position size
            'max_drawdown': 0.20  # 20% default max drawdown
        }
        
        # Extract stop loss
        stop_loss_match = re.search(r'止损\s*(\d+(?:\.\d+)?)%', prompt)
        if stop_loss_match:
            risk_prefs['stop_loss'] = float(stop_loss_match.group(1)) / 100
        
        # Extract take profit
        take_profit_match = re.search(r'止盈\s*(\d+(?:\.\d+)?)%', prompt)
        if take_profit_match:
            risk_prefs['take_profit'] = float(take_profit_match.group(1)) / 100
        
        # Extract position size
        position_size_match = re.search(r'仓位\s*(\d+(?:\.\d+)?)%', prompt)
        if position_size_match:
            risk_prefs['position_size'] = float(position_size_match.group(1)) / 100
        
        return risk_prefs
    
    def _extract_timeframe(self, prompt):
        """Extract trading timeframe."""
        # Default timeframe
        timeframe = '1h'
        
        # Check for specific timeframes
        timeframe_patterns = {
            r'(\d+)\s*分钟': 'minute',
            r'(\d+)\s*小时': 'hour',
            r'(\d+)\s*天': 'day',
            r'(\d+)\s*日': 'day'
        }
        
        for pattern, unit in timeframe_patterns.items():
            match = re.search(pattern, prompt)
            if match:
                value = match.group(1)
                if unit == 'minute':
                    timeframe = '{value}m'
                elif unit == 'hour':
                    timeframe = '{value}h'
                elif unit == 'day':
                    timeframe = '{value}d'
                break
        
        return timeframe
    
    def parse_example(self, prompt):
        """
        Parse prompt and return detailed analysis.
        
        Useful for debugging and understanding how prompts are parsed.
        """
        result = self.parse(prompt)
        
        analysis = {
            'original_prompt': prompt,
            'parsed_result': result,
            'extraction_details': {
                'symbol_found': result['symbol'],
                'strategy_type_found': result['type'],
                'parameters_found': len(result['parameters']) > 0,
                'tags_found': len(result['tags']) > 0
            }
        }
        
        return analysis