#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI文本去味技能 - 使用示例
演示如何使用 de-ai-fy-text 技能进行文本处理
"""

from deai_skill import DeAIProcessor, AITextDetector, TextHumanizer
import json


def example_basic_usage():
    """基础使用示例"""
    print("=" * 60)
    print("示例1：基础使用")
    print("=" * 60)
    
    # 创建处理器实例
    processor = DeAIProcessor()
    
    # 中文文本示例
    chinese_text = "综上所述，我们可以看出人工智能技术正在改变我们的生活方式。这一技术具有巨大的潜力和广阔的前景。"
    
    print("\n原文（中文）：")
    print(chinese_text)
    
    # 处理文本
    result, features = processor.process(chinese_text, language='zh')
    
    print("\n处理后的文本：")
    print(result)
    
    print("\nAI特征信息：")
    print(f"AI特征分数: {features['ai_score']:.2f}")
    print(f"检测到的AI特征: {features['ai_phrases']}")
    print(f"句式相似度: {features['sentence_similarity']:.2f}")
    
    # 英文文本示例
    english_text = "In conclusion, it is important to note that artificial intelligence technology is transforming our way of life. This technology possesses immense potential and promising prospects."
    
    print("\n原文（英文）：")
    print(english_text)
    
    # 处理英文文本
    result_en, features_en = processor.process(english_text, language='en')
    
    print("\n处理后的文本：")
    print(result_en)
    
    print("\nAI特征信息：")
    print(f"AI特征分数: {features_en['ai_score']:.2f}")
    print(f"检测到的AI特征: {features_en['ai_phrases']}")


def example_different_styles():
    """不同风格的转换示例"""
    print("\n\n" + "=" * 60)
    print("示例2：不同风格的转换")
    print("=" * 60)
    
    processor = DeAIProcessor()
    
    text = "这一问题具有多个方面的考虑因素，需要我们进行深入的分析和研究。值得注意的是，这一技术方案展现出明显的优势。"
    
    print("\n原文：")
    print(text)
    
    # 自然风格
    result_natural = processor.process(text, language='zh', style='natural')[0]
    print("\n自然风格：")
    print(result_natural)
    
    # 口语风格
    result_casual = processor.process(text, language='zh', style='casual')[0]
    print("\n口语风格：")
    print(result_casual)
    
    # 正式风格
    result_formal = processor.process(text, language='zh', style='formal')[0]
    print("\n正式风格：")
    print(result_formal)


def example_batch_processing():
    """批量处理示例"""
    print("\n\n" + "=" * 60)
    print("示例3：批量处理")
    print("=" * 60)
    
    processor = DeAIProcessor()
    
    texts = [
        "这一技术方案具有显著的优势和潜在的应用价值。",
        "通过深入分析，我们可以看出这种方法的有效性。",
        "需要注意的是，在实际应用中可能会遇到一些挑战。",
        "综上所述，人工智能技术在教育领域的应用具有广阔的前景。",
        "这一技术具有多方面的特点，需要我们全面考虑。"
    ]
    
    results = processor.batch_process(texts, language='zh', style='natural')
    
    for i, (original, (humanized, features)) in enumerate(zip(texts, results), 1):
        print(f"\n【文本 {i}】")
        print(f"原文: {original}")
        print(f"处理后: {humanized}")
        print(f"AI分数: {features['ai_score']:.2f}")


def example_ai_detection():
    """AI特征检测示例"""
    print("\n\n" + "=" * 60)
    print("示例4：AI特征检测")
    print("=" * 60)
    
    detector = AITextDetector()
    
    # AI生成的文本
    ai_text = "综上所述，这一技术具有重大的意义和深远的影响。我们需要认识到，在实施过程中可能会遇到诸多挑战，但通过共同努力，我们能够克服这些困难。"
    
    # 人类写的文本
    human_text = "这个技术挺有意思的，虽然实施起来可能有点难，但大家一起努力应该没问题。"
    
    print("\nAI生成的文本：")
    print(ai_text)
    ai_features = detector.detect_ai_features(ai_text, language='zh')
    print(f"AI特征分数: {ai_features['ai_score']:.2f}")
    print(f"检测到的AI特征: {ai_features['ai_phrases']}")
    
    print("\n\n人类写的文本：")
    print(human_text)
    human_features = detector.detect_ai_features(human_text, language='zh')
    print(f"AI特征分数: {human_features['ai_score']:.2f}")
    print(f"检测到的AI特征: {human_features['ai_phrases']}")


def example_multilingual():
    """多语言处理示例"""
    print("\n\n" + "=" * 60)
    print("示例5：中英文多语言处理")
    print("=" * 60)
    
    processor = DeAIProcessor()
    
    # 中文段落
    zh_text = """
    总的来说，人工智能技术在教育领域的应用具有广阔的前景和巨大的潜力。需要注意的是，在实际应用过程中，我们可能会面临一些挑战。因此，我们需要采取适当的策略来应对这些挑战。具体来说，我们可以通过以下几个方面来推进这一技术的应用。
    """
    
    print("中文段落：")
    print(zh_text)
    zh_result = processor.process(zh_text.strip(), language='zh', style='natural')[0]
    print("\n处理后：")
    print(zh_result)
    
    # 英文段落
    en_text = """
    In conclusion, artificial intelligence technology has broad prospects and immense potential in the field of education. It is important to note that we may face some challenges during the practical application process. Therefore, we need to adopt appropriate strategies to address these challenges. Specifically, we can advance the application of this technology through the following aspects.
    """
    
    print("\n\n英文段落：")
    print(en_text)
    en_result = processor.process(en_text.strip(), language='en', style='natural')[0]
    print("\n处理后：")
    print(en_result)


def example_comparison():
    """处理前后对比示例"""
    print("\n\n" + "=" * 60)
    print("示例6：处理前后对比")
    print("=" * 60)
    
    processor = DeAIProcessor()
    
    examples = [
        {
            "text": "这一方案具有重要的意义和深远的影响，需要我们认真对待。",
            "type": "中文 - 正式表达"
        },
        {
            "text": "The implementation of this technology plays a crucial role in promoting the development of the industry.",
            "type": "英文 - 正式表达"
        },
        {
            "text": "值得注意的是，这一技术展现出显著的优势和巨大的潜力。",
            "type": "中文 - 常见AI特征"
        },
        {
            "text": "It is worth noting that this technology demonstrates significant advantages and immense potential.",
            "type": "英文 - 常见AI特征"
        }
    ]
    
    for example in examples:
        print(f"\n【{example['type']}】")
        print("原文：", example['text'])
        
        language = 'zh' if '中文' in example['type'] else 'en'
        result, features = processor.process(example['text'], language=language, style='natural')
        
        print("处理后：", result)
        print(f"AI特征分数: {features['ai_score']:.2f}")


def example_score_analysis():
    """AI分数分析示例"""
    print("\n\n" + "=" * 60)
    print("示例7：AI分数分析")
    print("=" * 60)
    
    processor = DeAIProcessor()
    
    test_cases = [
        "这是一个简单的句子。",
        "综上所述，我们可以得出结论，这个问题具有多个方面的考虑因素，需要我们进行深入的分析和研究。",
        "这个项目挺有意思的，虽然有点难，但我觉得能搞定。",
        "需要注意的是，这一技术方案具有显著的优势，同时也面临一些挑战。"
    ]
    
    print("\n文本AI特征分数分析：\n")
    print(f"{'文本':<60} {'AI分数':<10} {'特征数量':<10}")
    print("-" * 80)
    
    for text in test_cases:
        score = processor.get_ai_score(text, language='zh')
        features = processor.detector.detect_ai_features(text, language='zh')
        print(f"{text[:57]:<57}... {score:<10.2f} {len(features['ai_phrases']):<10}")


def main():
    """运行所有示例"""
    print("AI文本去味技能 - 使用示例集合")
    print("=" * 60)
    
    # 运行所有示例
    example_basic_usage()
    example_different_styles()
    example_batch_processing()
    example_ai_detection()
    example_multilingual()
    example_comparison()
    example_score_analysis()
    
    print("\n\n" + "=" * 60)
    print("所有示例运行完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()