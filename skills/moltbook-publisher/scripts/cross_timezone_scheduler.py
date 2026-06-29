#!/usr/bin/env python3
"""
Cross-Timezone Publishing Scheduler
Calculate optimal posting times for different timezones

Usage:
    python cross_timezone_scheduler.py --current-time "2026-03-12 09:00"
    python cross_timezone_scheduler.py --strategy morning
"""

import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Tuple


class TimezoneScheduler:
    """Calculate optimal posting times across timezones"""
    
    TIMEZONES = {
        'Asia/Shanghai': {'name': 'Asia (Shanghai)', 'offset': 8},
        'UTC': {'name': 'UTC', 'offset': 0},
        'America/Los_Angeles': {'name': 'North America (West)', 'offset': -7},  # PDT
        'America/New_York': {'name': 'North America (East)', 'offset': -4},  # EDT
    }
    
    STRATEGIES = {
        'morning': {
            'name': 'Morning Deep Dive',
            'description': 'Technical posts for North America evening',
            'asia_time': '10:00',
            'coverage': 'North America evening (18:00-21:00 PDT, 21:00-00:00 EDT)',
            'best_for': ['Technical analysis', 'Data deep dives', 'Implementation guides'],
        },
        'noon': {
            'name': 'Noon Summary',
            'description': 'Community summaries and engagement',
            'asia_time': '12:00',
            'coverage': 'North America late evening (20:00-23:00 PDT, 23:00-02:00 EDT)',
            'best_for': ['Community summaries', 'Engagement replies', 'Trend observations'],
        },
        'evening': {
            'name': 'Evening Trend',
            'description': 'Trending topics for North America morning',
            'asia_time': '22:00',
            'coverage': 'North America morning (07:00-10:00 PDT, 10:00-13:00 EDT)',
            'best_for': ['Trending topics', 'Quick insights', 'Discussion starters'],
        },
    }
    
    def __init__(self):
        pass
    
    def get_current_times(self, base_time: datetime = None) -> Dict[str, datetime]:
        """Get current time across all timezones"""
        if base_time is None:
            base_time = datetime.now()
        
        times = {}
        for tz_name, tz_info in self.TIMEZONES.items():
            offset_hours = tz_info['offset']
            tz_time = base_time + timedelta(hours=offset_hours - 8)  # Convert from Asia/Shanghai
            times[tz_name] = tz_time
        
        return times
    
    def format_time(self, dt: datetime) -> str:
        """Format datetime for display"""
        return dt.strftime('%Y-%m-%d %H:%M (%a)')
    
    def get_strategy_recommendation(self, current_hour: int) -> Dict:
        """Get strategy recommendation based on current time"""
        if 9 <= current_hour < 12:
            return {
                'strategy': 'morning',
                'recommendation': 'Post now for North America evening coverage',
                'next_window': '12:00 (noon summary)',
            }
        elif 12 <= current_hour < 15:
            return {
                'strategy': 'noon',
                'recommendation': 'Good time for community engagement and summaries',
                'next_window': '22:00 (evening trend)',
            }
        elif 21 <= current_hour < 24:
            return {
                'strategy': 'evening',
                'recommendation': 'Post now for North America morning coverage',
                'next_window': 'Tomorrow 10:00 (morning deep dive)',
            }
        else:
            return {
                'strategy': 'flexible',
                'recommendation': 'Flexible posting time - engage with existing content',
                'next_window': '10:00 (morning deep dive)',
            }
    
    def print_schedule(self, base_time: datetime = None):
        """Print full timezone schedule"""
        times = self.get_current_times(base_time)
        
        print("🌍 Cross-Timezone Publishing Schedule")
        print("=" * 60)
        print()
        
        # Current times
        print("📍 Current Times:")
        for tz_name, tz_time in times.items():
            tz_info = self.TIMEZONES[tz_name]
            print(f"   {tz_info['name']:25} {self.format_time(tz_time)}")
        print()
        
        # Strategy recommendations
        asia_hour = times['Asia/Shanghai'].hour
        recommendation = self.get_strategy_recommendation(asia_hour)
        
        print("🎯 Current Strategy Recommendation:")
        print(f"   Time slot: {recommendation['strategy']}")
        print(f"   Action: {recommendation['recommendation']}")
        print(f"   Next window: {recommendation['next_window']}")
        print()
        
        # All strategies
        print("📅 Full Strategy Schedule:")
        print("-" * 60)
        for strategy_key, strategy in self.STRATEGIES.items():
            print(f"\n   {strategy['name']} ({strategy['asia_time']} Asia)")
            print(f"   Description: {strategy['description']}")
            print(f"   Coverage: {strategy['coverage']}")
            print(f"   Best for: {', '.join(strategy['best_for'])}")
        
        print()
        print("=" * 60)
    
    def calculate_posting_times(self, strategy: str, date: datetime = None) -> Dict[str, datetime]:
        """Calculate exact posting times for a strategy"""
        if date is None:
            date = datetime.now()
        
        strategy_info = self.STRATEGIES.get(strategy)
        if not strategy_info:
            raise ValueError(f"Unknown strategy: {strategy}")
        
        # Parse Asia time
        hour, minute = map(int, strategy_info['asia_time'].split(':'))
        asia_time = date.replace(hour=hour, minute=minute, second=0, microsecond=0)
        
        # Calculate times for all timezones
        times = {}
        for tz_name, tz_info in self.TIMEZONES.items():
            offset_hours = tz_info['offset'] - 8  # From Asia/Shanghai
            tz_time = asia_time + timedelta(hours=offset_hours)
            times[tz_name] = tz_time
        
        return times
    
    def print_strategy_detail(self, strategy: str, date: datetime = None):
        """Print detailed information for a specific strategy"""
        if date is None:
            date = datetime.now()
        
        strategy_info = self.STRATEGIES.get(strategy)
        if not strategy_info:
            print(f"❌ Unknown strategy: {strategy}")
            print(f"Available: {', '.join(self.STRATEGIES.keys())}")
            return
        
        times = self.calculate_posting_times(strategy, date)
        
        print(f"\n📋 Strategy: {strategy_info['name']}")
        print("=" * 60)
        print(f"Description: {strategy_info['description']}")
        print(f"Coverage: {strategy_info['coverage']}")
        print()
        
        print("🕐 Posting Times:")
        for tz_name, tz_time in times.items():
            tz_info = self.TIMEZONES[tz_name]
            print(f"   {tz_info['name']:25} {tz_time.strftime('%H:%M')}")
        print()
        
        print("✅ Best for:")
        for item in strategy_info['best_for']:
            print(f"   • {item}")
        print()
        
        print("💡 Tips:")
        if strategy == 'morning':
            print("   • Include technical depth and data")
            print("   • Reference previous discussions")
            print("   • Ask substantive questions")
        elif strategy == 'noon':
            print("   • Summarize morning engagement")
            print("   • Reply to comments from morning post")
            print("   • Plan evening content")
        elif strategy == 'evening':
            print("   • Focus on trending topics")
            print("   • Keep content concise")
            print("   • Use attention-grabbing titles")
        
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Cross-timezone publishing scheduler")
    parser.add_argument("--current-time", help="Current time (YYYY-MM-DD HH:MM)")
    parser.add_argument("--strategy", choices=['morning', 'noon', 'evening'], 
                       help="Show details for specific strategy")
    
    args = parser.parse_args()
    
    scheduler = TimezoneScheduler()
    
    # Parse current time if provided
    base_time = None
    if args.current_time:
        base_time = datetime.strptime(args.current_time, '%Y-%m-%d %H:%M')
    
    if args.strategy:
        scheduler.print_strategy_detail(args.strategy, base_time)
    else:
        scheduler.print_schedule(base_time)


if __name__ == "__main__":
    main()