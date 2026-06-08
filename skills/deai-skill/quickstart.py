#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI文本去味技能 - 快速入门指南
演示如何快速使用 de-ai-fy-text 技能
"""

from deai_skill import DeAIProcessor


def print_section(title):
    """打印章节标题"""
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def demo_basic_usage():
    """演示基础使用"""
    print_section("1. 基础使用 - 处理中文文本")
    
    # 创建处理器
    processor = DeAIProcessor()
    
    # 示例文本
    text = "综上所述，我们可以看出人工智能技术正在改变我们的生活方式。这一技术具有巨大的潜力和广阔的前景。"
    
    print(f"\n原文：")
    print(f"  {text}")
    
    # 处理文本
    result, features = processor.process(text, language='zh')
    
    print(f"\n处理后：")
    print(f"  {result}")
    
    print(f"\nAI特征分析：")
    print(f"  AI特征分数: {features['ai_score']:.2f}/1.00")
    if features['ai_phrases']:
        print(f"  检测到的AI特征: {', '.join(features['ai_phrases'])}")
    else:
        print(f"  检测到的AI特征: 无")


def demo_english_text():
    """演示英文文本处理"""
    print_section("2. 英文文本处理")
    
    processor = DeAIProcessor()
    
    text = "In conclusion, it is important to note that artificial intelligence technology is transforming our way of life. This technology possesses immense potential and promising prospects."
    
    print(f"\n原文：")
    print(f"  {text}")
    
    result, features = processor.process(text, language='en')
    
    print(f"\n处理后：")
    print(f"  {result}")
    
    print(f"\nAI特征分数: {features['ai_score']:.2f}/1.00")


def demo_styles():
    """演示不同风格的处理"""
    print_section("3. 不同风格处理")
    
    processor = DeAIProcessor()
    
    text = "这一问题具有多个方面的考虑因素，需要我们进行深入的分析和研究。值得注意的是，这一技术方案展现出明显的优势。"
    
    print(f"\n原文：")
    print(f"  {text}")
    
    # 自然风格
    result_natural, _ = processor.process(text, language='zh', style='natural')
    print(f"\n自然风格：")
    print(f"  {result_natural}")
    
    # 口语风格
    result_casual, _ = processor.process(text, language='zh', style='casual')
    print(f"\n口语风格：")
    print(f"  {result_casual}")
    
    # 正式风格
    result_formal, _ = processor.process(text, language='zh', style='formal')
    print(f"\n正式风格：")
    print(f"  {result_formal}")


def demo_batch_processing():
    """演示批量处理"""
    print_section("4. 批量处理")
    
    processor = DeAIProcessor()
    
    texts = [
        "这一技术方案具有显著的优势和潜在的应用价值。",
        "通过深入分析，我们可以看出这种方法的有效性。",
        "需要注意的是，在实际应用中可能会遇到一些挑战。",
        "综上所述，人工智能技术在教育领域的应用具有广阔的前景。",
        "这一技术具有多方面的特点，需要我们全面考虑。"
    ]
    
    results = processor.batch_process(texts, language='zh')
    
    print(f"\n批量处理 {len(texts)} 条文本：\n")
    for i, (original, (humanized, features)) in enumerate(zip(texts, results), 1):
        print(f"【文本 {i}】")
        print(f"  原文: {original[:50]}...")
        print(f"  处理: {humanized[:50]}...")
        print(f"  AI分数: {features['ai_score']:.2f}")
        print()


def demo_ai_detection():
    """演示AI特征检测"""
    print_section("5. AI特征检测")
    
    processor = DeAIProcessor()
    
    test_cases = [
        ("这是一个简单的句子。", "人类文本"),
        ("综上所述，我们可以得出结论，这个问题具有多个方面的考虑因素。", "AI文本"),
        ("这个项目挺有意思的，虽然有点难，但我觉得能搞定。", "人类文本"),
        ("需要注意的是，这一技术方案具有显著的优势，同时也面临一些挑战。", "AI文本")
    ]
    
    print("\n文本AI特征分析：\n")
    for text, label in test_cases:
        score = processor.get_ai_score(text, language='zh')
        print(f"{label:12} | AI分数: {score:.2f} | 文本: {text}")
    
    print(f"\n说明：分数越高，越像AI生成的文本（0-1分）")


def demo_practical_examples():
    """演示实际应用场景"""
    print_section("6. 实际应用场景")
    
    processor = DeAIProcessor()
    
    # 场景1：社交媒体文案
    print("\n场景1：社交媒体文案")
    social_text = "综上所述，这款产品具有显著的优势，能够为用户带来良好的体验。"
    result, _ = processor.process(social_text, language='zh', style='casual')
    print(f"  原文: {social_text}")
    print(f"  优化: {result}")
    
    # 场景2：博客文章
    print("\n场景2：博客文章")
    blog_text = "需要注意的是，在使用这一技术时，我们需要考虑多个方面的因素。"
    result, _ = processor.process(blog_text, language='zh', style='natural')
    print(f"  原文: {blog_text}")
    print(f"  优化: {result}")
    
    # 场景3：技术文档
    print("\n场景3：技术文档")
    doc_text = "这一技术方案具有重要的作用和意义，值得进一步研究和推广。"
    result, _ = processor.process(doc_text, language='zh', style='formal')
    print(f"  原文: {doc_text}")
    print(f"  优化: {result}")


def main():
    """主函数"""
    print("""
╔════════════════════════════════════════════════════════════════════╗
║                                                                    ║
║              AI文本去味技能 (de-ai-fy-text) - 快速入门             ║
║                                                                    ║
║  一个专业的AI文本去味处理工具，让AI生成的文本更自然、更人性化      ║
║                                                                    ║
╚════════════════════════════════════════════════════════════════════╝
    """)
    
    try:
        # 运行所有演示
        demo_basic_usage()
        demo_english_text()
        demo_styles()
        demo_batch_processing()
        demo_ai_detection()
        demo_practical_examples()
        
        print_section("演示完成")
        print("""
你可以开始使用以下方式：
  
  Python API:
    from deai_skill import DeAIProcessor
    processor = DeAIProcessor()
    result, features = processor.process("你的文本", language='zh')
  
  命令行:
    python deai_skill.py --input input.txt --output output.txt --language zh
    
  交互模式:
    python deai_skill.py
    
更多详细信息请参考:
  - SKILL.md: 技能说明文档
  - README.md: 项目说明文档
  - example_usage.py: 更多使用示例
        """)
    
    except ImportError as e:
        print(f"\n错误: 缺少必要的依赖 - {e}")
        print("请运行: pip install jieba")
    except Exception as e:
        print(f"\n错误: {e}")


if __name__ == '__main__':
    main()