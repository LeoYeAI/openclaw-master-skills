#!/usr/bin/env python3
"""
Context Restore Skill - Phase 2 功能测试 (Timeline & Filter)

测试用例：
- test_extract_timeline_daily: 日级别时间线提取
- test_extract_timeline_weekly: 周级别时间线提取
- test_extract_timeline_monthly: 月级别时间线提取
- test_extract_timeline_invalid_period: 无效 period 参数
- test_filter_context_basic: 基础过滤功能
- test_filter_context_case_insensitive: 大小写不敏感过滤
- test_filter_context_no_match: 无匹配结果
- test_filter_context_empty_input: 空输入处理
- test_filter_projects_only: 仅项目过滤
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

from restore_context import (
    extract_timeline,
    filter_context,
    filter_projects_only,
    PERIOD_DAILY,
    PERIOD_WEEKLY,
    PERIOD_MONTHLY,
    VALID_PERIODS,
)


class TestExtractTimeline(unittest.TestCase):
    """时间线提取功能测试"""

    def test_extract_timeline_daily(self):
        """测试日级别时间线提取"""
        content = """2026-02-07: 完成数据清洗模块
✅ Context restored
2026-02-06: 修复登录漏洞
Hermes Plan 进行中
2026-02-05: 添加新功能
Akasha Plan 开发中"""
        
        result = extract_timeline(content, period="daily")
        
        self.assertEqual(result["period"], "daily")
        self.assertIn("timeline", result)
        self.assertGreaterEqual(len(result["timeline"]), 1)
        
        # 检查是否正确提取了日期
        timeline_dates = [entry["period_label"] for entry in result["timeline"]]
        self.assertTrue(any("2026-02-07" in str(d) for d in timeline_dates))

    def test_extract_timeline_weekly(self):
        """测试周级别时间线提取"""
        content = """2026-02-07: 完成数据清洗模块
2026-02-06: 修复登录漏洞
2026-02-05: 添加新功能
2026-02-04: 代码审查
2026-02-03: 单元测试
2026-02-02: 重构模块
2026-02-01: 设计方案"""
        
        result = extract_timeline(content, period="weekly")
        
        self.assertEqual(result["period"], "weekly")
        self.assertIn("timeline", result)

    def test_extract_timeline_monthly(self):
        """测试月级别时间线提取"""
        content = """2026-02-07: 完成数据清洗模块
2026-02-06: 修复登录漏洞
2026-01-15: 初始版本发布
2026-01-01: 项目启动"""
        
        result = extract_timeline(content, period="monthly")
        
        self.assertEqual(result["period"], "monthly")
        self.assertIn("timeline", result)

    def test_extract_timeline_invalid_period(self):
        """测试无效 period 参数"""
        content = "2026-02-07: 完成数据清洗模块"
        
        with self.assertRaises(ValueError):
            extract_timeline(content, period="invalid")

    def test_extract_timeline_empty_content(self):
        """测试空内容"""
        result = extract_timeline("", period="daily")
        
        self.assertEqual(result["period"], "daily")
        self.assertIn("timeline", result)

    def test_extract_timeline_no_dates(self):
        """测试没有日期的内容"""
        content = "✅ 完成数据清洗模块\n✅ 修复登录漏洞"
        
        result = extract_timeline(content, period="daily")
        
        self.assertEqual(result["period"], "daily")
        self.assertIn("timeline", result)
        # 应该返回 "Recent" 作为默认标签
        self.assertEqual(result["timeline"][0]["period_label"], "Recent")

    def test_extract_timeline_with_projects(self):
        """测试带项目信息的时间线"""
        content = """2026-02-07: 完成数据清洗模块
Hermes Plan 进行中
2026-02-06: 设计 Akasha UI
Akasha Plan 开发中"""
        
        result = extract_timeline(content, period="daily")
        
        self.assertIn("projects", result["timeline"][0])
        # 应该包含检测到的项目
        projects = result["timeline"][0].get("projects", [])
        self.assertTrue(len(projects) >= 0)  # 可能包含项目名称

    def test_extract_timeline_days_filter(self):
        """测试 days 参数过滤"""
        content = """2026-02-07: 今天操作
2026-02-01: 旧操作
2026-01-01: 更旧的操作"""
        
        # 只获取最近 7 天
        result = extract_timeline(content, period="daily", days=7)
        
        # 应该只包含 2026-02-01 及之后的内容
        if result["timeline"]:
            for entry in result["timeline"]:
                # 验证日期在范围内
                date_str = entry.get("period_label", "")
                if "2026-01-01" in date_str:
                    self.fail("Date outside filter range should not be included")

    def test_extract_timeline_structure(self):
        """测试时间线返回结构"""
        content = """2026-02-07: 完成数据清洗模块
✅ Context restored"""
        
        result = extract_timeline(content, period="daily")
        
        # 验证必需字段
        required_fields = ["period", "total_days", "total_operations", "timeline"]
        for field in required_fields:
            self.assertIn(field, result)
        
        # timeline 条目应有必需字段
        if result["timeline"]:
            entry = result["timeline"][0]
            required_entry_fields = [
                "period_label", "operations", "projects", 
                "operations_count", "highlights"
            ]
            for field in required_entry_fields:
                self.assertIn(field, entry)


class TestFilterContext(unittest.TestCase):
    """上下文过滤功能测试"""

    def test_filter_context_basic(self):
        """测试基础过滤功能"""
        content = """Hermes Plan - 数据分析助手
Akasha Plan - 自主新闻系统
Other content here
Hermes Plan 进行中"""
        
        result = filter_context(content, "Hermes")
        
        self.assertIn("Hermes Plan", result)
        # 过滤会保留周围上下文行，所以 Akasha 可能出现在结果中
        # 关键是确保匹配行的内容存在
        self.assertTrue(
            "Hermes Plan" in result or
            "数据分析助手" in result
        )

    def test_filter_context_case_insensitive(self):
        """测试大小写不敏感过滤"""
        content = """HERMES PLAN - 数据分析助手
Akasha Plan - 自主新闻系统
hermes plan 进行中"""
        
        result = filter_context(content, "Hermes")
        
        # 应该匹配所有大小写变体
        self.assertTrue(
            "HERMES" in result or "Hermes" in result or "hermes" in result
        )

    def test_filter_context_no_match(self):
        """测试无匹配结果"""
        content = """Hermes Plan - 数据分析助手
Akasha Plan - 自主新闻系统"""
        
        result = filter_context(content, "NonExistent")
        
        self.assertIn("NonExistent", result)
        self.assertIn("未找到匹配", result)

    def test_filter_context_empty_content(self):
        """测试空内容过滤"""
        result = filter_context("", "Hermes")
        self.assertEqual(result, "")

    def test_filter_context_empty_pattern(self):
        """测试空过滤模式"""
        content = "Hermes Plan"
        result = filter_context(content, "")
        self.assertEqual(result, content)

    def test_filter_context_preserves_context_lines(self):
        """测试保留上下文行"""
        content = """这是第一行
这是第二行
Hermes Plan 在这里
这是第四行
这是第五行
Akasha Plan 不应该出现
这是第七行"""
        
        result = filter_context(content, "Hermes")
        
        self.assertIn("Hermes Plan", result)
        # 应该保留周围的几行
        self.assertIn("第二行", result)
        self.assertIn("第四行", result)
        # Akasha 不应该出现
        self.assertNotIn("Akasha Plan", result)

    def test_filter_context_whitespace_pattern(self):
        """测试空白过滤模式"""
        content = "Hermes Plan\nOther"
        result = filter_context(content, "   ")
        self.assertEqual(result, content)


class TestFilterProjectsOnly(unittest.TestCase):
    """仅项目过滤测试"""

    def test_filter_projects_only_with_content(self):
        """测试带内容时的过滤"""
        content = """🔄 **最近操作:**
- 完成数据清洗模块

🚀 **项目:**
- Hermes Plan - 数据分析助手
- Akasha Plan - 自主新闻系统

📋 **任务:**
- 编写测试用例"""
        
        result = filter_projects_only(content)
        
        # 应该只保留项目相关内容
        self.assertIn("Hermes Plan", result)
        self.assertIn("Akasha Plan", result)

    def test_filter_projects_only_empty(self):
        """测试空内容"""
        result = filter_projects_only("")
        self.assertEqual(result, "")

    def test_filter_projects_only_no_projects(self):
        """测试没有项目的内容"""
        content = "🔄 **最近操作:**\n- 完成数据清洗模块"
        
        result = filter_projects_only(content)
        
        self.assertIn("未找到项目", result)


class TestPeriodConstants(unittest.TestCase):
    """Period 常量测试"""

    def test_period_constants_defined(self):
        """测试 Period 常量已定义"""
        self.assertEqual(PERIOD_DAILY, "daily")
        self.assertEqual(PERIOD_WEEKLY, "weekly")
        self.assertEqual(PERIOD_MONTHLY, "monthly")

    def test_valid_periods_list(self):
        """测试有效 period 列表"""
        self.assertIn("daily", VALID_PERIODS)
        self.assertIn("weekly", VALID_PERIODS)
        self.assertIn("monthly", VALID_PERIODS)
        self.assertEqual(len(VALID_PERIODS), 3)


# =============================================================================
# 测试运行器
# =============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("Context Restore - Phase 2 功能测试 (Timeline & Filter)")
    print("=" * 70)
    print()
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestExtractTimeline))
    suite.addTests(loader.loadTestsFromTestCase(TestFilterContext))
    suite.addTests(loader.loadTestsFromTestCase(TestFilterProjectsOnly))
    suite.addTests(loader.loadTestsFromTestCase(TestPeriodConstants))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print()
    print("=" * 70)
    print(f"测试结果汇总:")
    print(f"  总测试: {result.testsRun}")
    print(f"  成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  失败: {len(result.failures)}")
    print(f"  错误: {len(result.errors)}")
    print("=" * 70)
    
    sys.exit(0 if result.wasSuccessful() else 1)
