# -*- coding: utf-8 -*-
#!/usr/bin/env python3
"""
Template Manager - Manages strategy templates and selects appropriate ones.
"""

import os
import json
from pathlib import Path


class TemplateManager:
    """Manages trading strategy templates."""
    
    def __init__(self, templates_dir=None):
        """Initialize template manager."""
        if templates_dir is None:
            templates_dir = Path(__file__).parent.parent / "templates"
        self.templates_dir = Path(templates_dir)
        self.templates = self._load_templates()
    
    def _load_templates(self):
        """Load all templates from templates directory."""
        templates = {}
        
        # Walk through template directories
        for root, dirs, files in os.walk(self.templates_dir):
            for file in files:
                if file.endswith('.py'):
                    template_path = Path(root) / file
                    template_name = template_path.stem
                    
                    # Read template metadata from first few lines
                    with open(template_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract metadata (looking for comments with specific format)
                    metadata = self._extract_metadata(content)
                    
                    templates[template_name] = {
                        'name': template_name,
                        'path': str(template_path),
                        'content': content,
                        'metadata': metadata,
                        'category': Path(root).relative_to(self.templates_dir).parts[0] if Path(root) != self.templates_dir else 'root'
                    }
        
        return templates
    
    def _extract_metadata(self, content):
        """Extract metadata from template content."""
        metadata = {
            'description': '',
            'strategy_type': '',
            'supported_symbols': ['BTC', 'ETH', 'SOL', '其他'],
            'parameters': {},
            'tags': []
        }
        
        lines = content.split('\n')
        in_metadata = False
        
        for line in lines[:50]:  # Check first 50 lines
            line = line.strip()
            
            # Look for metadata section
            if line.startswith('# METADATA:'):
                in_metadata = True
                continue
            
            if in_metadata and line.startswith('# END METADATA'):
                break
            
            if in_metadata and line.startswith('#'):
                # Parse metadata line
                line = line[1:].strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    key = key.strip().lower()
                    value = value.strip()
                    
                    if key == 'description':
                        metadata['description'] = value
                    elif key == 'strategy_type':
                        metadata['strategy_type'] = value
                    elif key == 'supported_symbols':
                        metadata['supported_symbols'] = [s.strip() for s in value.split(',')]
                    elif key == 'tags':
                        metadata['tags'] = [t.strip() for t in value.split(',')]
        
        return metadata
    
    def select_template(self, strategy_info):
        """Select appropriate template based on strategy information."""
        strategy_type = strategy_info.get('type', '').lower()
        symbol = strategy_info.get('symbol', '').upper()
        
        # Score each template
        template_scores = []
        
        for template_name, template in self.templates.items():
            score = 0
            
            # Check strategy type match
            template_type = template['metadata'].get('strategy_type', '').lower()
            if strategy_type in template_type or template_type in strategy_type:
                score += 10
            
            # Check symbol support
            supported_symbols = template['metadata'].get('supported_symbols', [])
            if symbol in supported_symbols or '其他' in supported_symbols:
                score += 5
            
            # Check tags match (if any)
            strategy_tags = strategy_info.get('tags', [])
            template_tags = template['metadata'].get('tags', [])
            common_tags = set(strategy_tags) & set(template_tags)
            score += len(common_tags) * 2
            
            # Prefer templates with higher scores
            template_scores.append((score, template))
        
        # Sort by score (descending)
        template_scores.sort(key=lambda x: x[0], reverse=True)
        
        if template_scores and template_scores[0][0] > 0:
            return template_scores[0][1]
        else:
            # Return default template
            return self.get_default_template()
    
    def get_default_template(self):
        """Get default template (basic RSI strategy)."""
        default_template_name = 'rsi_strategy'
        
        if default_template_name in self.templates:
            return self.templates[default_template_name]
        else:
            # Create a simple default template
            return {
                'name': 'default_strategy',
                'path': '',
                'content': self._create_default_template(),
                'metadata': {
                    'description': 'Default trading strategy template',
                    'strategy_type': 'basic',
                    'supported_symbols': ['BTC', 'ETH', 'SOL', '其他'],
                    'tags': ['basic', 'default']
                },
                'category': 'basic'
            }
    
    def _create_default_template(self):
        """Create a default template when no templates are available."""
        return '''#!/usr/bin/env python3
"""
Default Trading Strategy Template
Generated by VibeTrading Code Generator
"""

import os
import time
import logging


# METADATA:
# Description: 默认交易策略模板
# Strategy_Type: basic
# Supported_Symbols: BTC,ETH,SOL,其他
# Tags: basic,default
# END METADATA

class DefaultTradingStrategy:
    """默认交易策略模板类"""
    
    def __init__(self, api_key, account_address, symbol = "BTC"):
        """
        初始化策略
        
        Args:
            api_key: Hyperliquid API密钥
            account_address: Hyperliquid账户地址
            symbol: 交易品种符号
        """
        self.api_key = api_key
        self.account_address = account_address
        self.symbol = symbol
        
        # 配置日志
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
        self.logger.info("初始化 {symbol} 交易策略")
    
    def run(self):
        """运行策略主循环"""
        self.logger.info("开始运行策略...")
        
        try:
            while True:
                self._execute_trading_logic()
                time.sleep(60)  # 每分钟检查一次
                
        except KeyboardInterrupt:
            self.logger.info("用户中断策略运行")
        except Exception as e:
            self.logger.error("策略运行出错: {e}")
            raise
    
    def _execute_trading_logic(self):
        """执行交易逻辑"""
        self.logger.info("执行交易逻辑...")
        # 这里添加具体的交易逻辑
        
        # 示例: 获取价格并记录
        current_price = self._get_current_price()
        self.logger.info("当前 {self.symbol} 价格: ${current_price}")
    
    def _get_current_price(self):
        """获取当前价格（示例方法）"""
        # 这里应该实现实际的API调用
        # 返回示例价格
        return 50000.0
    
    def _place_order(self, side, quantity, price[float] = None):
        """下单（示例方法）"""
        order_type = "limit" if price else "market"
        self.logger.info("准备下单: {side} {quantity} {self.symbol} {order_type}")

def main():
    """主函数"""
    # 从环境变量获取API密钥和账户地址
    api_key = os.getenv("HYPERLIQUID_API_KEY")
    account_address = os.getenv("HYPERLIQUID_ACCOUNT_ADDRESS")
    
    if not api_key or not account_address:
        print("错误: 请设置环境变量 HYPERLIQUID_API_KEY 和 HYPERLIQUID_ACCOUNT_ADDRESS")
        print("示例:")
        print("  export HYPERLIQUID_API_KEY='your_api_key'")
        print("  export HYPERLIQUID_ACCOUNT_ADDRESS='your_account_address'")
        return
    
    # 创建并运行策略
    strategy = DefaultTradingStrategy(
        api_key=api_key,
        account_address=account_address,
        symbol="BTC"  # 默认使用BTC
    )
    
    strategy.run()

if __name__ == "__main__":
    main()
'''
    
    def list_templates(self):
        """List all available templates."""
        templates_by_category = {}
        
        for template_name, template in self.templates.items():
            category = template['category']
            if category not in templates_by_category:
                templates_by_category[category] = []
            
            templates_by_category[category].append({
                'name': template_name,
                'description': template['metadata'].get('description', ''),
                'strategy_type': template['metadata'].get('strategy_type', ''),
                'supported_symbols': template['metadata'].get('supported_symbols', [])
            })
        
        return templates_by_category
    
    def get_template(self, template_name):
        """Get specific template by name."""
        return self.templates.get(template_name)