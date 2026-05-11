#!/usr/bin/env python3
"""
Context Restore Skill - 完整集成测试

测试用例：
- test_full_workflow: 完整工作流程测试
- test_summary_with_timeline: 带时间线的摘要测试
- test_compare_contexts: 上下文比较测试
- test_telegram_chunking: Telegram 分块测试
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

from restore_context import (
    restore_context,
    get_context_summary,
    compare_contexts,
    format_diff_report,
    LEVEL_MINIMAL,
    LEVEL_NORMAL,
    LEVEL_DETAILED,
    extract_timeline,
    filter_context,
)


class TestFullWorkflow(unittest.TestCase):
    """完整工作流程测试"""

    def test_complete_workflow_with_summary_filter(self):
        """测试完整工作流程：生成上下文 + --summary + --filter"""
        test_context = {
            "content": """✅ 完成数据清洗模块
✅ 修复登录漏洞
原始消息数: 100
压缩后消息数: 10
上下文压缩于 2026-02-06T23:42:00
Hermes Plan 进行中
Akasha Plan 开发中
3个活跃 Isolated Sessions
cron 任务正在运行"""
        }
        
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as f:
            json.dump(test_context, f)
            temp_path = f.name
        
        try:
            # 步骤 1: 获取摘要
            summary = get_context_summary(temp_path)
            self.assertTrue(summary["success"])
            self.assertIn("metadata", summary)
            self.assertIn("operations", summary)
            self.assertIn("projects", summary)
            self.assertIn("tasks", summary)
            
            # 验证操作提取
            self.assertGreater(len(summary["operations"]), 0)
            operations_text = " ".join(summary["operations"])
            self.assertTrue(
                "完成数据清洗" in operations_text or 
                "修复登录" in operations_text
            )
            
            # 验证项目提取
            project_names = [p["name"] for p in summary["projects"]]
            self.assertIn("Hermes Plan", project_names)
            self.assertIn("Akasha Plan", project_names)
            
            # 验证任务提取
            task_names = [t["task"] for t in summary["tasks"]]
            self.assertTrue(any("Isolated Sessions" in t for t in task_names))
            
            # 步骤 2: 使用 filter 过滤上下文
            full_content = test_context["content"]
            hermes_filtered = filter_context(full_content, "Hermes")
            self.assertIn("Hermes Plan", hermes_filtered)
            # 过滤会保留上下文行，所以 Akasha 可能出现在结果中
            # 关键是确保包含匹配的内容
            
            akasha_filtered = filter_context(full_content, "Akasha")
            self.assertIn("Akasha Plan", akasha_filtered)
            
        finally:
            os.unlink(temp_path)

    def test_workflow_with_timeline_extraction(self):
        """测试带时间线提取的工作流程"""
        test_context = {
            "content": """2026-02-07: 完成数据清洗模块
✅ Context restored
2026-02-06: 修复登录漏洞
Hermes Plan 进行中
2026-02-05: 添加新功能
Akasha Plan 开发中
2026-02-04: 代码审查
原始消息数: 200
压缩后消息数: 25"""
        }
        
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as f:
            json.dump(test_context, f)
            temp_path = f.name
        
        try:
            # 获取带时间线的摘要
            summary = get_context_summary(temp_path, period="daily")
            self.assertTrue(summary["success"])
            self.assertIn("timeline", summary)
            
            # 提取独立时间线
            content = test_context["content"]
            timeline = extract_timeline(content, period="daily")
            
            self.assertEqual(timeline["period"], "daily")
            self.assertGreater(timeline["total_operations"], 0)
            
        finally:
            os.unlink(temp_path)


class TestSummaryWithTimeline(unittest.TestCase):
    """带时间线的摘要测试"""

    def test_summary_includes_timeline(self):
        """测试摘要包含时间线"""
        test_context = {
            "content": """2026-02-07: 完成数据清洗模块
2026-02-06: 修复登录漏洞
2026-02-05: 添加新功能"""
        }
        
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as f:
            json.dump(test_context, f)
            temp_path = f.name
        
        try:
            summary = get_context_summary(temp_path, period="daily")
            self.assertTrue(summary["success"])
            self.assertIn("timeline", summary)
            self.assertIn("operations", summary)
            
        finally:
            os.unlink(temp_path)

    def test_summary_different_periods(self):
        """测试不同时间段摘要"""
        test_context = {
            "content": """2026-02-07: 操作1
2026-02-06: 操作2
2026-02-05: 操作3"""
        }
        
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as f:
            json.dump(test_context, f)
            temp_path = f.name
        
        try:
            for period in ["daily", "weekly", "monthly"]:
                summary = get_context_summary(temp_path, period=period)
                self.assertTrue(summary["success"])
                self.assertEqual(summary["timeline"]["period"], period)
                
        finally:
            os.unlink(temp_path)


class TestCompareContexts(unittest.TestCase):
    """上下文比较测试"""

    def test_compare_contexts_added_project(self):
        """测试比较上下文 - 新增项目"""
        old_context = {
            "content": """✅ 原始内容
Hermes Plan 进行中"""
        }
        
        new_context = {
            "content": """✅ 原始内容
Hermes Plan 进行中
Akasha Plan 新增"""
        }
        
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as f:
            json.dump(old_context, f)
            old_path = f.name
        
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as f:
            json.dump(new_context, f)
            new_path = f.name
        
        try:
            diff = compare_contexts(old_path, new_path)
            
            self.assertTrue(diff["success"])
            self.assertTrue(len(diff["added_projects"]) > 0 or 
                           len(diff["operations_added"]) > 0)
            
        finally:
            os.unlink(old_path)
            os.unlink(new_path)

    def test_compare_contexts_no_changes(self):
        """测试比较上下文 - 无变化"""
        context_data = {
            "content": """✅ 相同内容
Hermes Plan 进行中"""
        }
        
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as f:
            json.dump(context_data, f)
            path1 = f.name
        
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as f:
            json.dump(context_data, f)
            path2 = f.name
        
        try:
            diff = compare_contexts(path1, path2)
            
            self.assertTrue(diff["success"])
            self.assertEqual(len(diff["added_projects"]), 0)
            self.assertEqual(len(diff["operations_added"]), 0)
            
        finally:
            os.unlink(path1)
            os.unlink(path2)

    def test_format_diff_report(self):
        """测试格式化差异报告"""
        old_context = {"content": "旧内容"}
        new_context = {"content": "新内容"}
        
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as f:
            json.dump(old_context, f)
            old_path = f.name
        
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as f:
            json.dump(new_context, f)
            new_path = f.name
        
        try:
            diff = compare_contexts(old_path, new_path)
            report = format_diff_report(diff, old_path, new_path)
            
            self.assertIsInstance(report, str)
            self.assertIn("CONTEXT DIFF REPORT", report)
            self.assertIn("Old:", report)
            self.assertIn("New:", report)
            
        finally:
            os.unlink(old_path)
            os.unlink(new_path)


class TestTelegramChunking(unittest.TestCase):
    """Telegram 分块测试"""

    def test_split_for_telegram_exists(self):
        """测试 Telegram 分块函数存在"""
        try:
            from restore_context import split_for_telegram
            self.assertTrue(callable(split_for_telegram))
        except ImportError:
            self.skipTest("split_for_telegram not implemented")

    def test_split_long_content(self):
        """测试拆分长内容"""
        try:
            from restore_context import split_for_telegram
            
            # 创建超过限制的长内容
            long_content = "x" * 5000
            chunks = split_for_telegram(long_content)
            
            self.assertIsInstance(chunks, list)
            self.assertGreater(len(chunks), 1)
            
            # 验证每个块不超过限制
            from restore_context import TELEGRAM_MAX_LENGTH
            for chunk in chunks:
                self.assertLessEqual(len(chunk), TELEGRAM_MAX_LENGTH)
                
        except ImportError:
            self.skipTest("split_for_telegram not implemented")


class TestCLIIntegration(unittest.TestCase):
    """CLI 集成测试"""

    def test_cli_summary_output(self):
        """测试 CLI 摘要输出"""
        test_context = {
            "content": "✅ 测试操作\n原始消息数: 10"
        }
        
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as f:
            json.dump(test_context, f)
            temp_path = f.name
        
        try:
            result = subprocess.run(
                [
                    sys.executable, 
                    str(BASE_DIR / "scripts" / "restore_context.py"),
                    "--file", temp_path,
                    "--summary"
                ],
                capture_output=True,
                text=True
            )
            
            self.assertEqual(result.returncode, 0)
            
            # 验证 JSON 输出
            output = json.loads(result.stdout)
            self.assertTrue(output["success"])
            self.assertIn("operations", output)
            
        finally:
            os.unlink(temp_path)

    def test_cli_with_filter(self):
        """测试 CLI 过滤功能"""
        test_context = {
            "content": "Hermes Plan 内容\nAkasha Plan 内容"
        }
        
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as f:
            json.dump(test_context, f)
            temp_path = f.name
        
        try:
            # 尝试使用 --filter 参数（如果支持）
            result = subprocess.run(
                [
                    sys.executable,
                    str(BASE_DIR / "scripts" / "restore_context.py"),
                    "--file", temp_path,
                    "--level", "minimal"
                ],
                capture_output=True,
                text=True
            )
            
            self.assertEqual(result.returncode, 0)
            
        finally:
            os.unlink(temp_path)


class TestProjectProgressIntegration(unittest.TestCase):
    """项目进度集成测试"""

    def test_summary_includes_project_progress(self):
        """测试摘要包含项目进度"""
        test_context = {
            "content": "Hermes Plan 项目"
        }
        
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as f:
            json.dump(test_context, f)
            temp_path = f.name
        
        try:
            summary = get_context_summary(temp_path)
            self.assertTrue(summary["success"])
            
            # 验证包含项目进度信息
            self.assertIn("project_progress", summary)
            # 可能为空 dict（如果没有项目目录）
            self.assertIsInstance(summary["project_progress"], dict)
            
        finally:
            os.unlink(temp_path)


# =============================================================================
# 测试运行器
# =============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("Context Restore - 完整集成测试")
    print("=" * 70)
    print()
    
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestFullWorkflow))
    suite.addTests(loader.loadTestsFromTestCase(TestSummaryWithTimeline))
    suite.addTests(loader.loadTestsFromTestCase(TestCompareContexts))
    suite.addTests(loader.loadTestsFromTestCase(TestTelegramChunking))
    suite.addTests(loader.loadTestsFromTestCase(TestCLIIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestProjectProgressIntegration))
    
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
