#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI文本去味技能 - 单元测试
测试 de-ai-fy-text 技能的各项功能
"""

import unittest
import sys
from pathlib import Path

# 添加当前目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from deai_skill import DeAIProcessor, AITextDetector, TextHumanizer


class TestAITextDetector(unittest.TestCase):
    """测试AI特征检测器"""
    
    def setUp(self):
        """设置测试环境"""
        self.detector = AITextDetector()
    
    def test_chinese_ai_detection(self):
        """测试中文AI特征检测"""
        # 包含明显AI特征的文本
        ai_text = "综上所述，我们可以看出人工智能技术具有巨大的潜力和广阔的前景。"
        features = self.detector.detect_ai_features(ai_text, language='zh')
        
        self.assertGreater(features['ai_score'], 0, "AI分数应该大于0")
        self.assertIn('综上所述', features['ai_phrases'], "应该检测到'综上所述'")
    
    def test_english_ai_detection(self):
        """测试英文AI特征检测"""
        ai_text = "In conclusion, it is important to note that this technology has significant potential."
        features = self.detector.detect_ai_features(ai_text, language='en')
        
        self.assertGreater(features['ai_score'], 0, "AI分数应该大于0")
    
    def test_human_text_detection(self):
        """测试人类文本的检测"""
        human_text = "这个技术挺有意思的，虽然有点难，但我觉得能搞定。"
        features = self.detector.detect_ai_features(human_text, language='zh')
        
        self.assertLess(features['ai_score'], 0.2, "人类文本的AI分数应该较低")
    
    def test_sentence_similarity(self):
        """测试句式相似度检测"""
        # 句式相似的文本
        uniform_text = "这很好。那很好。一切都很好。"
        features = self.detector.detect_ai_features(uniform_text, language='zh')
        
        # 句式不同的文本
        varied_text = "这挺好的。那也不错，挺好的就是。"
        features_varied = self.detector.detect_ai_features(varied_text, language='zh')
        
        # 句式相似的文本应该有更高的句式相似度
        self.assertGreater(features['sentence_similarity'], 
                          features_varied['sentence_similarity'],
                         "句式相似的文本应该有更高的相似度分数")


class TestTextHumanizer(unittest.TestCase):
    """测试文本人性化处理器"""
    
    def setUp(self):
        """设置测试环境"""
        self.humanizer = TextHumanizer()
    
    def test_chinese_transition_replacement(self):
        """测试中文过渡词替换"""
        text = "综上所述，这是一个重要的发现。"
        result = self.humanizer._replace_transitions(text, 'zh', probability=1.0)
        
        self.assertNotEqual(result, text, "文本应该被修改")
        self.assertNotIn("综上所述", result, "应该替换掉'综上所述'")
    
    def test_english_transition_replacement(self):
        """测试英文过渡词替换"""
        text = "Furthermore, this is an important finding."
        result = self.humanizer._replace_transitions(text, 'en', probability=1.0)
        
        self.assertNotEqual(result, text, "文本应该被修改")
        self.assertNotIn("furthermore", result.lower(), "应该替换掉'furthermore'")
    
    def test_colloquial_elements_addition(self):
        """测试口语化元素添加"""
        text = "这个技术很有用。"
        result = self.humanizer._add_colloquial_elements(text, 'zh', intensity='strong')
        
        # 应该添加一些口语化元素
        self.assertGreater(len(result), len(text), "处理后文本长度应该增加")
    
    def test_natural_style(self):
        """测试自然风格处理"""
        text = "综上所述，这一技术具有重要的作用和意义。"
        result = self.humanizer._apply_natural_style(text, 'zh')
        
        self.assertIsInstance(result, str, "结果应该是字符串")
        self.assertGreater(len(result), 0, "结果不应为空")
    
    def test_casual_style(self):
        """测试口语风格处理"""
        text = "这一技术具有重要意义。"
        result = self.humanizer._apply_casual_style(text, 'zh')
        
        self.assertIsInstance(result, str, "结果应该是字符串")
    
    def test_formal_style(self):
        """测试正式风格处理"""
        text = "这一技术具有重要意义。"
        result = self.humanizer._apply_formal_style(text, 'zh')
        
        self.assertIsInstance(result, str, "结果应该是字符串")
        # 正式风格应该保留更多原文特征
        self.assertIn("重要", result, "正式风格应保留重要信息")


class TestDeAIProcessor(unittest.TestCase):
    """测试去AI味处理器主类"""
    
    def setUp(self):
        """设置测试环境"""
        self.processor = DeAIProcessor()
    
    def test_basic_processing(self):
        """测试基础处理功能"""
        text = "综上所述，这一技术具有重要的作用和意义。"
        result, features = self.processor.process(text, language='zh')
        
        self.assertIsInstance(result, str, "结果应该是字符串")
        self.assertIsInstance(features, dict, "特征信息应该是字典")
        self.assertIn('ai_score', features, "特征信息应包含ai_score")
    
    def test_batch_processing(self):
        """测试批量处理功能"""
        texts = [
            "综上所述，这是一个重要的发现。",
            "这一技术具有显著的优点。",
            "需要注意的是，这只是一个开始。"
        ]
        
        results = self.processor.batch_process(texts, language='zh')
        
        self.assertEqual(len(results), len(texts), "结果数量应与输入数量相同")
        for result in results:
            self.assertIsInstance(result, tuple, "每个结果应该是元组")
            self.assertEqual(len(result), 2, "每个结果应包含两个元素")
    
    def test_get_ai_score(self):
        """测试获取AI分数"""
        ai_text = "综上所述，我们可以得出一个重要的结论。"
        human_text = "这个挺好的。"
        
        ai_score = self.processor.get_ai_score(ai_text, language='zh')
        human_score = self.processor.get_ai_score(human_text, language='zh')
        
        self.assertGreater(ai_score, human_score, "AI文本的分数应该更高")
    
    def test_chinese_processing(self):
        """测试中文处理"""
        text = "值得注意的是，这一技术展现出显著的优势。"
        result, _ = self.processor.process(text, language='zh')
        
        self.assertIsInstance(result, str, "结果应该是字符串")
        self.assertNotEqual(result, text, "处理后文本应该有所不同")
    
    def test_english_processing(self):
        """测试英文处理"""
        text = "It is important to note that this technology demonstrates significant advantages."
        result, _ = self.processor.process(text, language='en')
        
        self.assertIsInstance(result, str, "结果应该是字符串")
    
    def test_different_styles(self):
        """测试不同风格的处理"""
        text = "这一技术具有重要意义。"
        
        natural_result = self.processor.process(text, language='zh', style='natural')[0]
        casual_result = self.processor.process(text, language='zh', style='casual')[0]
        formal_result = self.processor.process(text, language='zh', style='formal')[0]
        
        self.assertIsInstance(natural_result, str, "自然风格结果应该是字符串")
        self.assertIsInstance(casual_result, str, "口语风格结果应该是字符串")
        self.assertIsInstance(formal_result, str, "正式风格结果应该是字符串")
        
        # 不同风格的结果应该有所区别
        self.assertTrue(
            natural_result != casual_result or natural_result != formal_result,
            "不同风格应该产生不同的结果"
        )
    
    def test_detect_only_mode(self):
        """测试仅检测模式"""
        text = "综上所述，这是一个重要的结论。"
        result, features = self.processor.process(text, language='zh', detect_only=True)
        
        self.assertEqual(result, text, "仅检测模式应返回原文")
        self.assertGreater(features['ai_score'], 0, "应该检测到AI特征")


class TestEdgeCases(unittest.TestCase):
    """测试边缘情况"""
    
    def setUp(self):
        """设置测试环境"""
        self.processor = DeAIProcessor()
    
    def test_empty_text(self):
        """测试空文本"""
        text = ""
        result, features = self.processor.process(text, language='zh')
        
        self.assertEqual(result, text, "空文本应保持不变")
        self.assertEqual(features['ai_score'], 0.0, "空文本的AI分数应为0")
    
    def test_short_text(self):
        """测试极短文本"""
        text = "好的。"
        result, _ = self.processor.process(text, language='zh')
        
        self.assertIsInstance(result, str, "短文本处理结果应该是字符串")
    
    def test_long_text(self):
        """测试长文本"""
        text = "综上所述，" * 50
        result, _ = self.processor.process(text, language='zh')
        
        self.assertIsInstance(result, str, "长文本处理结果应该是字符串")
    
    def test_mixed_language(self):
        """测试混合语言文本"""
        text = "综上所述，this is a test."
        result, _ = self.processor.process(text, language='zh')
        
        self.assertIsInstance(result, str, "混合语言文本处理结果应该是字符串")
    
    def test_special_characters(self):
        """测试特殊字符"""
        text = "综上所述，这个技术@#$%^&*()很重要！"
        result, _ = self.processor.process(text, language='zh')
        
        self.assertIsInstance(result, str, "包含特殊字符的文本处理结果应该是字符串")


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_complete_workflow(self):
        """测试完整工作流程"""
        processor = DeAIProcessor()
        
        # 测试完整的处理流程
        original_text = "综上所述，我们可以看出这一技术具有重要的作用和意义。"
        
        # 第一步：检测
        ai_score = processor.get_ai_score(original_text, language='zh')
        self.assertGreater(ai_score, 0, "初始文本应该有AI特征")
        
        # 第二步：处理
        processed_text, features = processor.process(original_text, language='zh', style='natural')
        self.assertIsInstance(processed_text, str, "处理后文本应该是字符串")
        
        # 第三步：验证
        final_score = processor.get_ai_score(processed_text, language='zh')
        self.assertLessEqual(final_score, ai_score, "处理后AI分数应该降低或不增加")
    
    def test_multiple_iterations(self):
        """测试多次迭代处理"""
        processor = DeAIProcessor()
        
        text = "综上所述，这一技术具有重要的作用和意义。"
        
        # 第一次处理
        text1, _ = processor.process(text, language='zh')
        # 第二次处理
        text2, _ = processor.process(text1, language='zh')
        
        # 多次处理不应该出错
        self.assertIsInstance(text2, str, "多次处理结果应该是字符串")


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestAITextDetector))
    suite.addTests(loader.loadTestsFromTestCase(TestTextHumanizer))
    suite.addTests(loader.loadTestsFromTestCase(TestDeAIProcessor))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    print("=" * 70)
    print("AI文本去味技能 - 单元测试")
    print("=" * 70)
    
    result = run_tests()
    
    print("\n" + "=" * 70)
    print(f"测试完成！")
    print(f"运行测试: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print("=" * 70)
    
    # 返回退出码
    sys.exit(0 if result.wasSuccessful() else 1)