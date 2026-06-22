#!/usr/bin/env python3
"""
炒股大师模拟器 - 核心引擎
支持多位大师风格，集成MX系列工具和Stock Monitor
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any

# 配置路径
SKILL_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SKILL_DIR, "data")
PROMPTS_DIR = os.path.join(SKILL_DIR, "prompts")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(PROMPTS_DIR, exist_ok=True)

# ============== 炒大师配置 ==============

class MasterProfiles:
    """炒大师风格配置管理"""
    
    # 内置大师配置
    BUILDIN_MASTERS = {
        "文主任": {
            "name": "文主任",
            "source": "抖音",
            "followers": "20万",
            "style_tags": ["#因子投资", "#量化思维", "#五维度分析", "#恒生科技", "#金融常识"],
            "analysis_method": "宏观（基本面+量化因子）+ 技术面",
            "core_indicators": [
                "布林线", "均线（MA5/MA10/MA200）", "动量因子",
                "M2流动性（港元M2同比）", "PPI工业品价格指数", "换手率", "估值+增速差"
            ],
            "target_markets": ["港股", "恒生科技", "美股", "原油", "宽基指数"],
            "investment_strategy": {
                "position": "轻仓实盘（3-5成）",
                "hedge": "期权/期货对冲",
                "style": "左侧交易，逢低布局",
                "time_horizon": "中长期",
                "entry_strategy": "分批建仓，越跌越买"
            },
            "philosophy": [
                "相信数据，不信主观判断",
                "因子投资降低容错，追求稳健回撤",
                "事件驱动是散户陷阱，资讯太慢跟不上机构",
                "短线是零和博弈，散户玩不过高频算法",
                "推荐宽基指数定投+波段，适合普通人"
            ],
            "tools": ["IFIND", "WIND", "Python/Excel"],
            "sectors_preference": ["科技", "互联网", "金融"],
            "stock_filter": {
                "min_market_cap": 100e8,  # 100亿市值
                "max_pe": 50,
                "min_volume": 1e7  # 日均成交量
            }
        },
        
        # 示例：可以继续添加更多大师
        # "某大V": { ... }
    }
    
    def __init__(self):
        self.custom_masters = self._load_custom_masters()
    
    def _load_custom_masters(self) -> Dict:
        """加载自定义大师配置"""
        config_path = os.path.join(DATA_DIR, "masters.json")
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def get_master(self, name: str) -> Optional[Dict]:
        """获取大师配置"""
        if name in self.BUILDIN_MASTERS:
            return self.BUILDIN_MASTERS[name].copy()
        if name in self.custom_masters:
            return self.custom_masters[name].copy()
        return None
    
    def list_masters(self) -> List[str]:
        """列出所有可用大师"""
        return list(self.BUILDIN_MASTERS.keys()) + list(self.custom_masters.keys())
    
    def add_master(self, name: str, profile: Dict) -> bool:
        """添加新大师"""
        self.custom_masters[name] = profile
        config_path = os.path.join(DATA_DIR, "masters.json")
        try:
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(self.custom_masters, f, ensure_ascii=False, indent=2)
            return True
        except:
            return False


# ============== MX工具调用器 ==============

class MXTools:
    """MX系列工具调用器 - 支持依赖检查"""
    
    def __init__(self):
        self.available_tools = self._check_dependencies()
        self.results = {}
    
    def _check_dependencies(self) -> Dict[str, bool]:
        """检查依赖是否可用"""
        # 实际运行时检查skill是否安装
        # 这里返回状态，实际调用时会尝试调用
        return {
            "mx_search": True,  # 需用户安装 mx_search skill
            "mx_data": True,     # 需用户安装 mx_data skill
            "mx_selfselect": True,  # 需用户安装 mx_selfselect skill
            "mx_select_stock": True,  # 需用户安装 mx_select_stock skill
            "stock_monitor": True  # 需用户安装 stock-monitor-skill
        }
    
    def get_status(self) -> str:
        """获取工具状态"""
        status = "🔧 依赖检查:\n"
        for tool, available in self.available_tools.items():
            icon = "✅" if available else "❌"
            status += f"{icon} {tool}\n"
        status += "\n如需安装，请运行:\n"
        status += "clawhub install mx_search mx_data mx_selfselect mx_select_stock stock-monitor-skill"
        return status
    
    async def search_news(self, query: str) -> List[Dict]:
        """调用mx_search搜索资讯"""
        # 这里模拟调用MX Search API
        # 实际使用时通过消息接口调用skill
        result = {
            "query": query,
            "status": "simulated",
            "note": "实际通过消息接口调用mx_search skill"
        }
        self.results['search'] = result
        return [result]
    
    async def get_stock_data(self, code: str) -> Dict:
        """调用mx_data获取股票数据"""
        result = {
            "code": code,
            "status": "simulated",
            "note": "实际通过消息接口调用mx_data skill"
        }
        self.results['data'] = result
        return result
    
    async def add_to_watchlist(self, code: str, name: str) -> bool:
        """调用mx_selfselect添加自选股"""
        result = {
            "code": code,
            "name": name,
            "status": "simulated",
            "note": "实际通过消息接口调用mx_selfselect skill"
        }
        self.results['watchlist'] = result
        return True
    
    async def select_stocks(self, criteria: Dict) -> List[Dict]:
        """调用mx_select_stock智能选股"""
        result = {
            "criteria": criteria,
            "status": "simulated",
            "note": "实际通过消息接口调用mx_select_stock skill"
        }
        self.results['select'] = result
        return [result]
    
    async def setup_monitor(self, code: str, alerts: Dict) -> bool:
        """调用stock_monitor设置监控"""
        result = {
            "code": code,
            "alerts": alerts,
            "status": "simulated",
            "note": "实际通过消息接口调用stock_monitor skill"
        }
        self.results['monitor'] = result
        return True


# ============== 选股推荐引擎 ==============

class RecommendationEngine:
    """基于大师风格生成选股建议"""
    
    def __init__(self, profile: Dict, mx_tools: MXTools = None):
        self.profile = profile
        self.mx_tools = mx_tools or MXTools()
    
    async def generate_recommendations(self, market_data: Dict = None) -> Dict:
        """生成符合风格的选股建议"""
        
        recommendations = {
            "style_summary": "",
            "market_view": "",
            "stock_picks": [],
            "operation_suggestion": "",
            "tools_used": [],
            "risk_warning": "⚠️ 本报告仅供学习参考，不构成投资建议"
        }
        
        # 1. 风格总结
        tags = self.profile.get("style_tags", [])
        recommendations["style_summary"] = f"根据【{self.profile.get('name')}】的风格分析：\n" + \
            f"核心标签: {' '.join(tags)}\n" + \
            f"分析方法: {self.profile.get('analysis_method', 'N/A')}"
        
        # 2. 市场判断
        target_markets = self.profile.get("target_markets", [])
        indicators = self.profile.get("core_indicators", [])
        
        # 调用MX Search搜索大师关注的市场动态
        for market in target_markets[:2]:
            search_result = await self.mx_tools.search_news(f"{market} 最新资讯")
            recommendations["tools_used"].append(f"mx_search: {market}")
        
        recommendations["market_view"] = f"关注市场: {', '.join(target_markets)}\n" + \
            f"核心指标: {', '.join(indicators[:5])}"
        
        # 3. 操作建议
        strategy = self.profile.get("investment_strategy", {})
        recommendations["operation_suggestion"] = f"""仓位建议: {strategy.get('position', 'N/A')}
对冲策略: {strategy.get('hedge', 'N/A')}
交易风格: {strategy.get('style', 'N/A')}
时间周期: {strategy.get('time_horizon', 'N/A')}"""
        
        # 4. 生成模拟选股
        stock_picks = await self._generate_picks()
        recommendations["stock_picks"] = stock_picks
        
        # 5. 设置监控
        for pick in stock_picks[:3]:
            await self.mx_tools.setup_monitor(pick.get("code"), {
                "change_pct_above": 5.0,
                "change_pct_below": -5.0,
                "volume_surge": 2.0
            })
            recommendations["tools_used"].append(f"stock_monitor: {pick.get('code')}")
        
        return recommendations
    
    async def _generate_picks(self) -> List[Dict]:
        """基于风格特征生成选股"""
        picks = []
        
        # 获取偏好
        preference = self.profile.get("sectors_preference", [])
        stock_filter = self.profile.get("stock_filter", {})
        
        # 调用MX Select Stock按条件筛选
        if preference:
            criteria = {
                "sectors": preference,
                "market_cap_min": stock_filter.get("min_market_cap", 0),
                "pe_max": stock_filter.get("max_pe", 100),
                "volume_min": stock_filter.get("min_volume", 0)
            }
            select_result = await self.mx_tools.select_stocks(criteria)
        
        # 根据关注市场生成模拟选股
        target_markets = self.profile.get("target_markets", [])
        
        if "港股" in target_markets or "恒生科技" in str(self.profile.get("style_tags", [])):
            picks.extend([
                {"code": "00700", "name": "腾讯控股", "market": "港股", "reason": "恒生科技权重股，流动性好"},
                {"code": "09988", "name": "阿里巴巴", "market": "港股", "reason": "港股互联网龙头"},
                {"code": "03690", "name": "美团-W", "market": "港股", "reason": "本地生活龙头"}
            ])
        
        if "A股" in target_markets:
            picks.extend([
                {"code": "300059", "name": "东方财富", "market": "A股", "reason": "互联网券商龙头"},
                {"code": "002594", "name": "比亚迪", "market": "A股", "reason": "新能源龙头"}
            ])
        
        return picks[:5]


# ============== 报告生成器 ==============

def generate_report(master_name: str, style_profile: Dict, recommendations: Dict) -> str:
    """生成完整的模拟报告"""
    
    tools_used = recommendations.get("tools_used", [])
    
    report = f"""# 📊 【{master_name}】风格模拟报告

> 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M')}

---

## 🎯 风格画像

**大师**: {master_name}  
**来源**: {style_profile.get('source', 'N/A')}  
**粉丝**: {style_profile.get('followers', 'N/A')}

### 风格标签
{', '.join(style_profile.get('style_tags', []))}

### 分析方法
{style_profile.get('analysis_method', 'N/A')}

### 核心技术指标
{', '.join(style_profile.get('core_indicators', []))}

### 关注市场
{', '.join(style_profile.get('target_markets', []))}

---

## 💡 投资理念

{chr(10).join([f'- {p}' for p in style_profile.get('philosophy', [])[:5]])}

---

## 📈 当前市场判断

{recommendations.get('market_view', 'N/A')}

---

## 🔍 推荐关注

| 代码 | 名称 | 市场 | 推荐理由 |
|------|------|------|----------|
"""
    
    for pick in recommendations.get("stock_picks", []):
        report += f"| {pick.get('code', '')} | {pick.get('name', '')} | {pick.get('market', '')} | {pick.get('reason', '')} |\n"
    
    report += f"""
---

## ⚙️ 操作建议

{recommendations.get('operation_suggestion', 'N/A')}

---

## 🔧 已调用工具

"""
    
    for tool in tools_used:
        report += f"- {tool}\n"
    
    report += f"""
---

## ⚠️ 风险提示

{recommendations.get('risk_warning', '投资有风险，入市需谨慎')}

---

*本报告由 CC (炒股大师模拟器) 自动生成，仅供学习参考*
"""
    
    return report


# ============== 主接口 ==============

class TraderMasterSimulator:
    """炒股大师模拟器主类"""
    
    def __init__(self):
        self.profiles = MasterProfiles()
        self.mx_tools = MXTools()
    
    def list_masters(self) -> List[str]:
        """列出所有可用大师"""
        return self.profiles.list_masters()
    
    def get_master(self, name: str) -> Optional[Dict]:
        """获取大师配置"""
        return self.profiles.get_master(name)
    
    async def simulate(self, master_name: str) -> str:
        """模拟指定大师的选股思路"""
        
        # 获取大师配置
        profile = self.get_master(master_name)
        if not profile:
            available = ", ".join(self.list_masters())
            return f"❌ 未找到大师【{master_name}】\n可用大师: {available}"
        
        # 生成推荐
        engine = RecommendationEngine(profile, self.mx_tools)
        recommendations = await engine.generate_recommendations({})
        
        # 生成报告
        report = generate_report(master_name, profile, recommendations)
        
        return report
    
    def add_master_from_analysis(self, name: str, video_summaries: List[str]) -> str:
        """从视频分析结果添加新大师"""
        # 这里可以接入视频分析逻辑
        # 简化版本：用户手动输入配置
        return f"请提供【{name}】的风格配置（分析方法和关注指标），我会保存到配置中"


# ============== CLI ==============

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="炒股大师模拟器")
    parser.add_argument("command", choices=["list", "simulate", "add"], help="命令")
    parser.add_argument("--name", "-n", help="大师名称")
    
    args = parser.parse_args()
    
    simulator = TraderMasterSimulator()
    
    if args.command == "list":
        print("\n📋 可用炒股大师:")
        for name in simulator.list_masters():
            profile = simulator.get_master(name)
            tags = ", ".join(profile.get("style_tags", [])[:3])
            print(f"  • {name}: {tags}")
    
    elif args.command == "simulate":
        name = args.name or "文主任"
        print(f"\n🚀 正在模拟【{name}】的选股思路...\n")
        report = await simulator.simulate(name)
        print(report)
    
    elif args.command == "add":
        print("\n➕ 添加新大师功能开发中...\n")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
