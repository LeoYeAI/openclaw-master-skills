#!/usr/bin/env python3
"""
Context Restore Skill - 基础功能测试

测试用例：
- test_load_json：JSON 格式加载
- test_load_text：纯文本格式加载
- test_file_not_found：文件不存在处理
- test_metadata_parsing：元数据解析
- test_operation_extraction：操作提取
- test_project_extraction：项目提取
- test_task_extraction：任务提取
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# 从 tests 目录向上两级到 context-restore 目录
BASE_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(BASE_DIR / "scripts"))

from restore_context import (
    load_compressed_context,
    parse_metadata,
    extract_recent_operations,
    extract_key_projects,
    extract_ongoing_tasks,
    extract_memory_highlights,
    format_minimal_report,
    format_normal_report,
    format_detailed_report,
    restore_context,
    get_context_summary,
    LEVEL_MINIMAL,
    LEVEL_NORMAL,
    LEVEL_DETAILED,
    ContextLoadError,
)


class TestLoadCompressedContext(unittest.TestCase):
    """测试上下文文件加载功能"""

    def test_load_json_format(self):
        """测试 JSON 格式加载"""
        test_data = {
            "content": "✅ 测试消息",
            "metadata": {"timestamp": "2026-02-06T23:42:00Z"}
        }
        
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as f:
            json.dump(test_data, f)
            f.flush()
            
            result = load_compressed_context(f.name)
            
            os.unlink(f.name)
            
            self.assertIsInstance(result, dict)
            self.assertEqual(result["content"], "✅ 测试消息")

    def test_load_text_format(self):
        """测试纯文本格式加载"""
        test_content = """原始消息数: 100
压缩后消息数: 10
上下文压缩于 2026-02-06T23:42:00
✅ 完成数据清洗模块"""
        
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.txt', delete=False
        ) as f:
            f.write(test_content)
            f.flush()
            
            result = load_compressed_context(f.name)
            
            os.unlink(f.name)
            
            self.assertIsInstance(result, str)
            self.assertIn("✅ 完成数据清洗模块", result)

    def test_file_not_found(self):
        """测试文件不存在情况"""
        with self.assertRaises(ContextLoadError):
            load_compressed_context("/nonexistent/path/context.json")


class TestMetadataParsing(unittest.TestCase):
    """测试元数据解析功能"""

    def test_parse_metadata_complete(self):
        """测试完整元数据解析"""
        content = """原始消息数: 100
压缩后消息数: 10
上下文压缩于 2026-02-06T23:42:00"""
        
        metadata = parse_metadata(content)
        
        self.assertEqual(metadata.get("original_count"), 100)
        self.assertEqual(metadata.get("compressed_count"), 10)
        self.assertEqual(metadata.get("timestamp"), "2026-02-06T23:42:00")


class TestOperationExtraction(unittest.TestCase):
    """测试操作提取功能"""

    def test_extract_operations_with_checkmarks(self):
        """测试带 ✅ 标记的操作提取"""
        content = """✅ 完成数据清洗模块
✅ 修复登录漏洞
✅ 添加新功能"""
        
        operations = extract_recent_operations(content, max_count=5)
        
        self.assertEqual(len(operations), 3)
        self.assertIn("完成数据清洗模块", operations)


class TestProjectExtraction(unittest.TestCase):
    """测试项目提取功能"""

    def test_extract_hermes_project(self):
        """测试 Hermès Plan 提取"""
        content = "Hermès Plan 是一个数据分析助手项目"
        
        projects = extract_key_projects(content)
        
        self.assertTrue(len(projects) >= 1)
        self.assertTrue(any(p["name"] == "Hermes Plan" for p in projects))

    def test_extract_akasha_project(self):
        """测试 Akasha Plan 提取"""
        content = "Akasha Plan 是自主新闻系统"
        
        projects = extract_key_projects(content)
        
        self.assertTrue(len(projects) >= 1)
        self.assertTrue(any(p["name"] == "Akasha Plan" for p in projects))


class TestTaskExtraction(unittest.TestCase):
    """测试任务提取功能"""

    def test_extract_active_sessions(self):
        """测试活跃会话提取"""
        content = "3个活跃 Isolated Sessions"
        
        tasks = extract_ongoing_tasks(content)
        
        self.assertTrue(len(tasks) >= 1)
        self.assertTrue(any(t["task"] == "Isolated Sessions" for t in tasks))


class TestFormatReports(unittest.TestCase):
    """测试报告格式化功能"""

    def test_format_minimal_report(self):
        """测试 Minimal 级别报告"""
        content = "✅ 完成数据清洗模块\nHermes Plan 进行中"
        
        report = format_minimal_report(content)
        
        self.assertIn("Minimal", report)

    def test_format_normal_report(self):
        """测试 Normal 级别报告"""
        content = "✅ 完成数据清洗模块\n原始消息数: 100"
        
        report = format_normal_report(content)
        
        self.assertIn("Normal", report)
        self.assertIn("100", report)

    def test_format_detailed_report(self):
        """测试 Detailed 级别报告"""
        content = "✅ 完成数据清洗模块\n✅ 修复登录漏洞\n原始消息数: 100"
        
        report = format_detailed_report(content)
        
        self.assertIn("Detailed", report)


class TestRestoreContext(unittest.TestCase):
    """测试主入口函数"""

    def test_restore_with_valid_file(self):
        """测试有效文件恢复"""
        test_data = {
            "content": "✅ 测试消息\n原始消息数: 50\n压缩后消息数: 5"
        }
        
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as f:
            json.dump(test_data, f)
            f.flush()
            
            report = restore_context(f.name, LEVEL_NORMAL)
            
            os.unlink(f.name)
            
            self.assertIn("Normal", report)

    def test_restore_file_not_found(self):
        """测试文件不存在"""
        with self.assertRaises(ContextLoadError):
            restore_context("/nonexistent/file.json", LEVEL_MINIMAL)


class TestGetContextSummary(unittest.TestCase):
    """测试摘要获取函数"""

    def test_get_summary_success(self):
        """测试成功获取摘要"""
        test_data = {
            "content": "✅ 完成数据清洗模块\n原始消息数: 100"
        }
        
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as f:
            json.dump(test_data, f)
            f.flush()
            
            summary = get_context_summary(f.name)
            
            os.unlink(f.name)
            
            self.assertTrue(summary["success"])
            self.assertIn("metadata", summary)
            self.assertIn("operations", summary)

    def test_get_summary_failure(self):
        """测试获取摘要失败（文件不存在）"""
        with self.assertRaises(ContextLoadError):
            get_context_summary("/nonexistent/file.json")

    def test_get_summary_constants(self):
        """测试 LEVEL 常量定义"""
        self.assertEqual(LEVEL_MINIMAL, "minimal")
        self.assertEqual(LEVEL_NORMAL, "normal")
        self.assertEqual(LEVEL_DETAILED, "detailed")


# ============================================================================
# 测试运行器
# ============================================================================

if __name__ == '__main__':
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    suite.addTests(loader.loadTestsFromTestCase(TestLoadCompressedContext))
    suite.addTests(loader.loadTestsFromTestCase(TestMetadataParsing))
    suite.addTests(loader.loadTestsFromTestCase(TestOperationExtraction))
    suite.addTests(loader.loadTestsFromTestCase(TestProjectExtraction))
    suite.addTests(loader.loadTestsFromTestCase(TestTaskExtraction))
    suite.addTests(loader.loadTestsFromTestCase(TestFormatReports))
    suite.addTests(loader.loadTestsFromTestCase(TestRestoreContext))
    suite.addTests(loader.loadTestsFromTestCase(TestGetContextSummary))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    print("\n" + "=" * 70)
    print(f"测试结果: {result.testsRun} 个测试运行")
    print(f"  成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  失败: {len(result.failures)}")
    print(f"  错误: {len(result.errors)}")
    print("=" * 70)
    
    sys.exit(0 if result.wasSuccessful() else 1)
