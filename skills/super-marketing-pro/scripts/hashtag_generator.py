#!/usr/bin/env python3
"""
Hashtag智能生成器 - 根据内容和平台生成最佳Hashtag

Usage:
    python3 hashtag_generator.py --content "PU leather for shoes" --platform instagram
    python3 hashtag_generator.py --content "工厂实拍" --platform douyin
"""

import argparse

# Hashtag库
HASHTAG_LIBRARY = {
    "industry": {
        "en": ["#Leather", "#SyntheticLeather", "#PULeather", "#TPU", "#Microfiber", 
               "#FauxLeather", "#ArtificialLeather", "#VeganLeather", "#EcoLeather",
               "#Textile", "#Material", "#Fabric", "#Manufacturing", "#Factory"],
        "cn": ["#皮革", "#人造革", "#PU革", "#TPU", "#超纤", "#合成革", "#环保材料", "#新材料"]
    },
    "application": {
        "en": ["#Footwear", "#Shoes", "#Bags", "#Handbags", "#Automotive", 
               "#CarInterior", "#Furniture", "#Apparel", "#Fashion", "#Design"],
        "cn": ["#鞋材", "#箱包", "#汽车内饰", "#家具", "#服装", "#设计", "#手袋"]
    },
    "business": {
        "en": ["#B2B", "#Wholesale", "#Supplier", "#Manufacturer", "#FactoryDirect",
               "#MadeInChina", "#Export", "#Business", "#Industry"],
        "cn": ["#源头工厂", "#厂家直销", "#批发", "#供应商", "#B2B", "#外贸", "#出口"]
    },
    "features": {
        "en": ["#Sustainable", "#EcoFriendly", "#Durable", "#Waterproof", 
               "#HighQuality", "#Premium", "#Soft", "#Flexible", "#Innovation"],
        "cn": ["#环保", "#耐用", "#防水", "#高品质", "#柔软", "#创新", "#可持续"]
    },
    "branding": {
        "en": ["#YuchengNewMaterial", "#YuchengLeather", "#YourBrand"],
        "cn": ["#铭扬皮革", "#裕诚新材料"]
    }
}

# 平台特定Hashtag策略
PLATFORM_STRATEGIES = {
    "instagram": {
        "max_tags": 30,
        "mix": ["popular", "medium", "niche", "branding"],
        "popular_tags": ["#Leather", "#Fashion", "#Design", "#Style"],  # 100万+
        "medium_tags": ["#PULeather", "#SyntheticLeather", "#Material"],  # 10-100万
        "niche_tags": ["#ShoeMaterial", "#BagMaterial", "#AutomotiveInterior"]  # 1-10万
    },
    "linkedin": {
        "max_tags": 5,
        "mix": ["niche", "branding"],
        "recommended": ["#Manufacturing", "#B2B", "#SustainableMaterials", "#Innovation"]
    },
    "youtube": {
        "max_tags": 15,
        "mix": ["popular", "medium", "niche"],
        "focus": "搜索关键词"
    },
    "tiktok": {
        "max_tags": 5,
        "mix": ["trending", "niche"],
        "trending": ["#Factory", "#Satisfying", "#HowItsMade", "#Manufacturing"]
    },
    "douyin": {
        "max_tags": 5,
        "mix": ["trending", "niche", "branding"],
        "trending": ["#源头工厂", "#工厂实拍", "#制造业", "#老板日常"]
    },
    "xiaohongshu": {
        "max_tags": 10,
        "mix": ["popular", "niche", "branding"],
        "popular": ["#设计师", "#材料", "#好物推荐"],
        "niche": ["#鞋材", "#箱包材料", "#汽车内饰"]
    }
}

def analyze_content(content):
    """分析内容主题"""
    content_lower = content.lower()
    
    themes = []
    
    # 检测产品类型
    if any(word in content_lower for word in ["pu", "polyurethane", "pu革"]):
        themes.append("PU")
    if any(word in content_lower for word in ["tpu", "热塑性聚氨酯"]):
        themes.append("TPU")
    if any(word in content_lower for word in ["microfiber", "超纤", "micro fibre"]):
        themes.append("Microfiber")
    
    # 检测应用场景
    if any(word in content_lower for word in ["shoe", "footwear", "鞋"]):
        themes.append("Footwear")
    if any(word in content_lower for word in ["bag", "handbag", "包"]):
        themes.append("Bags")
    if any(word in content_lower for word in ["automotive", "car", "汽车"]):
        themes.append("Automotive")
    if any(word in content_lower for word in ["furniture", "家具"]):
        themes.append("Furniture")
    
    # 检测内容类型
    if any(word in content_lower for word in ["factory", "工厂", "manufacturing"]):
        themes.append("Factory")
    if any(word in content_lower for word in ["sustainable", "eco", "环保"]):
        themes.append("Sustainable")
    if any(word in content_lower for word in ["quality", "high quality", "高品质"]):
        themes.append("Quality")
    
    return themes

def generate_hashtags(content, platform, language="en"):
    """生成Hashtag"""
    themes = analyze_content(content)
    strategy = PLATFORM_STRATEGIES.get(platform, PLATFORM_STRATEGIES["instagram"])
    
    hashtags = []
    
    # 根据平台策略选择Hashtag
    if platform == "instagram":
        # Instagram: 大中小流量混合
        hashtags.extend(strategy["popular_tags"][:2])  # 2个大流量
        hashtags.extend(strategy["medium_tags"][:3])    # 3个中流量
        hashtags.extend(strategy["niche_tags"][:2])     # 2个精准
        
        # 根据主题添加相关标签
        for theme in themes:
            if theme == "PU":
                hashtags.extend(["#PULeather", "#Polyurethane", "#SyntheticLeather"])
            elif theme == "TPU":
                hashtags.extend(["#TPU", "#ThermoplasticPolyurethane", "#FlexibleMaterial"])
            elif theme == "Microfiber":
                hashtags.extend(["#Microfiber", "#Microfibre", "#VeganLeather"])
            elif theme == "Footwear":
                hashtags.extend(["#ShoeMaterial", "#FootwearIndustry", "#ShoeDesign"])
            elif theme == "Bags":
                hashtags.extend(["#BagMaterial", "#HandbagDesign", "#BagManufacturing"])
            elif theme == "Automotive":
                hashtags.extend(["#AutomotiveInterior", "#CarSeat", "#AutoUpholstery"])
            elif theme == "Factory":
                hashtags.extend(["#FactoryLife", "#Manufacturing", "#MadeInChina"])
        
        # 添加品牌标签
        hashtags.extend(HASHTAG_LIBRARY["branding"]["en"])
        
    elif platform == "linkedin":
        # LinkedIn: 专业精准
        hashtags.extend(strategy["recommended"])
        hashtags.extend(["#B2B", "#Manufacturing", "#SustainableMaterials"])
        
        for theme in themes:
            if theme in ["PU", "TPU", "Microfiber"]:
                hashtags.append(f"#{theme}Materials")
        
    elif platform == "douyin":
        # 抖音: 热门+精准
        hashtags.extend(strategy["trending"][:3])
        
        for theme in themes:
            if theme == "Factory":
                hashtags.extend(["#源头工厂", "#工厂实拍", "#制造业"])
            elif theme == "PU":
                hashtags.extend(["#PU革", "#人造革", "#皮革"])
            elif theme == "Footwear":
                hashtags.extend(["#鞋材", "#鞋子材料"])
        
        hashtags.extend(HASHTAG_LIBRARY["branding"]["cn"])
        
    elif platform == "xiaohongshu":
        # 小红书: 种草+精准
        hashtags.extend(strategy["popular"][:3])
        hashtags.extend(strategy["niche"][:3])
        
        for theme in themes:
            if theme == "Factory":
                hashtags.extend(["#源头工厂", "#工厂探秘"])
            elif theme in ["PU", "TPU", "Microfiber"]:
                hashtags.extend(["#材料科普", "#设计师必看"])
        
        hashtags.extend(["#好物推荐", "#材料选择"])
    
    # 去重并限制数量
    hashtags = list(set(hashtags))
    max_tags = strategy.get("max_tags", 30)
    
    return hashtags[:max_tags]

def format_hashtags(hashtags, platform):
    """格式化输出"""
    if platform in ["douyin", "xiaohongshu"]:
        # 中文平台：空格分隔
        return " ".join(hashtags)
    else:
        # 国际平台：空格分隔
        return " ".join(hashtags)

def main():
    parser = argparse.ArgumentParser(description="Hashtag智能生成器 (OpenClaw 批量优化版)")
    parser.add_argument("--content", required=True, help="内容描述")
    parser.add_argument("--platform", default="instagram", help="目标平台")
    parser.add_argument("--platforms", help="逗号分隔的多个平台，如 linkedin,instagram,douyin")
    parser.add_argument("--language", default="en", choices=["en", "cn"], help="语言")
    
    args = parser.parse_args()
    
    print(f"\n🎯 内容分析: {args.content}")
    print(f"🌐 语言: {args.language}\n")
    
    themes = analyze_content(args.content)
    print(f"📥 识别主题: {', '.join(themes) if themes else '通用'}")
    
    if args.platforms:
        print(f"\n🚀 启动多平台 Hashtag 批量生成模式...")
        platforms = [p.strip() for p in args.platforms.split(',')]
        
        for plat in platforms:
            if plat in PLATFORM_STRATEGIES:
                hashtags = generate_hashtags(args.content, plat, args.language)
                print(f"\n📱 [{plat.upper()}] 推荐Hashtag ({len(hashtags)}个):")
                print("-" * 60)
                print(format_hashtags(hashtags, plat))
            else:
                print(f"\n⚠️ 警告: 不支持的平台 '{plat}'")
        print("\n" + "=" * 60)
    else:
        print(f"📱 目标平台: {args.platform}")
        hashtags = generate_hashtags(args.content, args.platform, args.language)
        
        print(f"\n✅ 推荐Hashtag ({len(hashtags)}个):")
        print("=" * 60)
        print(format_hashtags(hashtags, args.platform))
        print("=" * 60)
        
        # 分类展示
        print("\n📊 Hashtag分类:")
        print(f"  行业标签: {[t for t in hashtags if any(ind in t.lower() for ind in ['leather', 'material', 'textile', '皮革', '材料'])]}")
        print(f"  应用标签: {[t for t in hashtags if any(app in t.lower() for app in ['shoe', 'bag', 'automotive', '鞋', '包', '汽车'])]}")
        print(f"  品牌标签: {[t for t in hashtags if 'yucheng' in t.lower() or '铭扬' in t or '裕诚' in t]}")

if __name__ == "__main__":
    main()
