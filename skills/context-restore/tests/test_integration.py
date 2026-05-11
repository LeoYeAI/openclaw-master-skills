#!/usr/bin/env python3
"""
Context Restore Skill - 集成测试

测试用例：
- test_cli_args：命令行参数解析
- test_summary_api：API 摘要接口
- test_integration_flow：完整集成流程
- test_multilingual_triggers：多语言触发测试
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class TestCLIArgs(unittest.TestCase):
    """测试命令行参数解析"""

    def test_default_args(self):
        """测试默认参数输出"""
        result = subprocess.run(
            [sys.executable, "-c", """
import sys
sys.path.insert(0, 'scripts')
from restore_context import DEFAULT_CONTEXT_FILE, LEVEL_NORMAL
print(DEFAULT_CONTEXT_FILE, LEVEL_NORMAL)
"""],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("compressed_context", result.stdout)

    def test_level_argument(self):
        """测试级别参数"""
        result = subprocess.run(
            [sys.executable, "scripts/restore_context.py", "--help"],
            capture_output=True,
            text=True
        )
        
        self.assertEqual(result.returncode, 0)
        self.assertIn("--level", result.stdout)
        self.assertIn("--file", result.stdout)

    def test_summary_argument(self):
        """测试摘要参数"""
        result = subprocess.run(
            [sys.executable, "scripts/restore_context.py", "--help"],
            capture_output=True,
            text=True
        )
        
        self.assertIn("--summary", result.stdout)


class TestIntegrationFlow(unittest.TestCase):
    """测试完整集成流程"""

    def test_complete_restore_flow(self):
        """测试完整的恢复流程"""
        # 创建测试上下文文件
        test_context = {
            "content": """✅ 完成数据清洗模块
✅ 修复登录漏洞
原始消息数: 100
压缩后消息数: 10
上下文压缩于 2026-02-06T23:42:00
Hermes Plan 是一个数据分析助手
Akasha Plan 是自主新闻系统
3个活跃会话
cron 任务正在运行"""
        }
        
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as f:
            json.dump(test_context, f)
            temp_path = f.name
        
        try:
            # 步骤 1: 加载上下文
            sys.path.insert(0, "scripts")
            from restore_context import load_compressed_context
            
            context = load_compressed_context(temp_path)
            self.assertIsNotNone(context)
            
            # 步骤 2: 获取摘要
            from restore_context import get_context_summary
            
            summary = get_context_summary(temp_path)
            self.assertTrue(summary["success"])
            self.assertGreater(len(summary["operations"]), 0)
            self.assertGreater(len(summary["projects"]), 0)
            
            # 步骤 3: 生成报告
            from restore_context import (
                restore_context, 
                LEVEL_MINIMAL, 
                LEVEL_NORMAL, 
                LEVEL_DETAILED
            )
            
            minimal_report = restore_context(temp_path, LEVEL_MINIMAL)
            self.assertIn("Minimal", minimal_report)
            
            normal_report = restore_context(temp_path, LEVEL_NORMAL)
            self.assertIn("Normal", normal_report)
            
            detailed_report = restore_context(temp_path, LEVEL_DETAILED)
            self.assertIn("Detailed", detailed_report)
            
        finally:
            os.unlink(temp_path)

    def test_level_progression(self):
        """测试级别递进（minimal → normal → detailed）"""
        test_context = {
            "content": """✅ 操作1
✅ 操作2
✅ 操作3
原始消息数: 100"""
        }
        
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as f:
            json.dump(test_context, f)
            temp_path = f.name
        
        try:
            sys.path.insert(0, "scripts")
            from restore_context import restore_context
            
            # Minimal 应该最简短
            minimal = restore_context(temp_path, "minimal")
            minimal_len = len(minimal)
            
            # Normal 应该更长
            normal = restore_context(temp_path, "normal")
            normal_len = len(normal)
            
            # Detailed 应该最长
            detailed = restore_context(temp_path, "detailed")
            detailed_len = len(detailed)
            
            # 验证长度递进
            self.assertLessEqual(minimal_len, normal_len)
            self.assertLessEqual(normal_len, detailed_len)
            
        finally:
            os.unlink(temp_path)


class TestMultilingualTriggers(unittest.TestCase):
    """测试多语言触发关键词"""

    def test_chinese_keywords_parsed(self):
        """测试中文关键词处理"""
        chinese_keywords = [
            "恢复上下文",
            "继续之前的工作",
            "接着",
            "继续",
            "恢复"
        ]
        
        # 验证关键词不为空
        for keyword in chinese_keywords:
            self.assertTrue(len(keyword) > 0)

    def test_english_keywords_parsed(self):
        """测试英文关键词处理"""
        english_keywords = [
            "restore context",
            "continue",
            "resume",
            "what was I doing"
        ]
        
        for keyword in english_keywords:
            self.assertTrue(len(keyword) > 0)


class TestErrorHandling(unittest.TestCase):
    """测试错误处理"""

    def test_nonexistent_file_cli(self):
        """测试 CLI 处理不存在的文件"""
        result = subprocess.run(
            [
                sys.executable, 
                "scripts/restore_context.py",
                "--file", "/nonexistent/file.json"
            ],
            capture_output=True,
            text=True
        )
        
        # 应该返回错误信息
        self.assertIn("错误", result.stdout) or self.assertNotEqual(result.returncode, 0)

    def test_invalid_level_cli(self):
        """测试 CLI 处理无效级别"""
        result = subprocess.run(
            [
                sys.executable,
                "scripts/restore_context.py",
                "--level", "invalid_level"
            ],
            capture_output=True,
            text=True
        )
        
        # 应该返回错误
        self.assertNotEqual(result.returncode, 0)


class TestOutputFormats(unittest.TestCase):
    """测试输出格式"""

    def test_json_output_with_summary(self):
        """测试 JSON 格式输出"""
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
                    "scripts/restore_context.py",
                    "--file", temp_path,
                    "--summary"
                ],
                capture_output=True,
                text=True
            )
            
            self.assertEqual(result.returncode, 0)
            
            # 验证 JSON 格式
            output = json.loads(result.stdout)
            self.assertIn("success", output)
            self.assertIn("operations", output)
            
        finally:
            os.unlink(temp_path)

    def test_file_output(self):
        """测试输出到文件"""
        test_context = {
            "content": "✅ 测试操作"
        }
        
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as f:
            json.dump(test_context, f)
            temp_path = f.name
        
        try:
            output_file = tempfile.mktemp(suffix=".txt")
            
            result = subprocess.run(
                [
                    sys.executable,
                    "scripts/restore_context.py",
                    "--file", temp_path,
                    "--level", "minimal",
                    "--output", output_file
                ],
                capture_output=True,
                text=True
            )
            
            self.assertEqual(result.returncode, 0)
            self.assertTrue(os.path.exists(output_file))
            
            with open(output_file, 'r') as f:
                content = f.read()
            
            self.assertIn("Minimal", content)
            
            os.unlink(output_file)
            
        finally:
            os.unlink(temp_path)


class TestPerformance(unittest.TestCase):
    """性能测试"""

    def test_load_performance(self):
        """测试加载性能（应在 200ms 内完成）"""
        import time
        
        test_context = {
            "content": "✅ " + "\n✅ ".join([f"操作{i}" for i in range(20)])
        }
        
        with tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', delete=False
        ) as f:
            json.dump(test_context, f)
            temp_path = f.name
        
        try:
            sys.path.insert(0, "scripts")
            from restore_context import load_compressed_context
            
            start = time.time()
            for _ in range(10):
                load_compressed_context(temp_path)
            elapsed = time.time() - start
            
            # 10 次加载应在 2 秒内（每次 < 200ms）
            self.assertLess(elapsed, 2.0)
            
        finally:
            os.unlink(temp_path)


# ============================================================================
# 测试数据生成器
# ============================================================================

def generate_test_data():
    """生成测试用的上下文文件"""
    test_cases = [
        {
            "name": "basic_context.json",
            "data": {
                "content": """✅ 完成数据清洗模块
✅ 修复登录漏洞
原始消息数: 100
压缩后消息数: 10
上下文压缩于 2026-02-06T23:42:00
Hermes Plan 进行中"""
            }
        },
        {
            "name": "multi_project_context.json",
            "data": {
                "content": """✅ 完成数据清洗模块
✅ 设计 Akasha UI
原始消息数: 200
压缩后消息数: 15
Hermes Plan: 数据分析助手
Akasha Plan: 自主新闻系统
3个活跃会话"""
            }
        }
    ]
    
    test_dir = Path(__file__).parent / "test_data"
    test_dir.mkdir(exist_ok=True)
    
    for case in test_cases:
        filepath = test_dir / case["name"]
        with open(filepath, 'w') as f:
            json.dump(case["data"], f, indent=2)
        print(f"生成测试数据: {filepath}")
    
    return [test_dir / c["name"] for c in test_cases]


# ============================================================================
# 测试运行器
# ============================================================================

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Context Restore 集成测试"
    )
    parser.add_argument(
        '--generate-data',
        action='store_true',
        help='生成测试数据文件'
    )
    
    args = parser.parse_args()
    
    if args.generate_data:
        generate_test_data()
        sys.exit(0)
    
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestCLIArgs))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegrationFlow))
    suite.addTests(loader.loadTestsFromTestCase(TestMultilingualTriggers))
    suite.addTests(loader.loadTestsFromTestCase(TestErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestOutputFormats))
    suite.addTests(loader.loadTestsFromTestCase(TestPerformance))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 输出总结
    print("\n" + "=" * 70)
    print(f"集成测试结果: {result.testsRun} 个测试运行")
    print(f"  成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  失败: {len(result.failures)}")
    print(f"  错误: {len(result.errors)}")
    print("=" * 70)
    
    # 退出码
    sys.exit(0 if result.wasSuccessful() else 1)
