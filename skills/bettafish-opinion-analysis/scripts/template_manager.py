"""
BettaFish Skill 报告模板管理器
用于加载、解析和管理不同类型的舆情分析报告模板
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional

# 模板文件路径
TEMPLATES_DIR = Path(__file__).parent.parent / "assets" / "templates"

# 模板类型映射
TEMPLATE_MAPPING = {
    "企业品牌声誉分析": {
        "keywords": ["品牌声誉", "品牌形象", "品牌口碑", "企业舆情", "声誉"],
        "filename": "企业品牌声誉分析报告模板.md",
        "description": "适用于品牌月度/季度声誉监测"
    },
    "突发事件与危机公关": {
        "keywords": ["危机", "突发事件", "负面舆情", "公关", "回应", "道歉", "事故"],
        "filename": "突发事件与危机公关舆情报告模板.md",
        "description": "适用于危机事件应急分析"
    },
    "社会公共热点事件": {
        "keywords": ["热点事件", "社会热议", "舆论焦点", "公众关注", "热议话题"],
        "filename": "社会公共热点事件分析报告模板.md",
        "description": "适用于社会热点追踪"
    },
    "市场竞争格局分析": {
        "keywords": ["竞品", "对比", "竞争", "市场份额", "vs", "比较"],
        "filename": "市场竞争格局舆情分析报告模板.md",
        "description": "适用于竞品对比、市场份额分析"
    },
    "特定政策或行业动态": {
        "keywords": ["政策", "行业", "新规", "监管", "法规", "指导意见"],
        "filename": "特定政策或行业动态舆情分析报告模板.md",
        "description": "适用于政策解读、行业分析"
    },
    "日常或定期舆情监测": {
        "keywords": ["定期", "周报", "月报", "监测", "追踪", "日报"],
        "filename": "日常或定期舆情监测报告模板.md",
        "description": "适用于周期性监测报告"
    }
}


def select_report_template(user_query: str) -> Tuple[str, str]:
    """
    根据用户查询选择最合适的报告模板

    Args:
        user_query: 用户的分析请求

    Returns:
        (template_name, template_path) 元组
    """
    query = user_query.lower()

    # 遍历所有模板类型进行关键词匹配
    for template_name, config in TEMPLATE_MAPPING.items():
        if any(keyword in query for keyword in config["keywords"]):
            template_path = TEMPLATES_DIR / config["filename"]
            if template_path.exists():
                return template_name, str(template_path)

    # 默认使用企业品牌声誉分析模板
    default_config = TEMPLATE_MAPPING["企业品牌声誉分析"]
    default_path = TEMPLATES_DIR / default_config["filename"]
    return "企业品牌声誉分析", str(default_path)


def parse_template_structure(template_path: str) -> Dict:
    """
    解析模板文件，提取章节结构

    Args:
        template_path: 模板文件路径

    Returns:
        包含模板结构的字典
    """
    with open(template_path, 'r', encoding='utf-8') as f:
        content = f.read()

    structure = {
        "template_name": "",
        "chapters": []
    }

    # 提取模板名称
    title_match = re.search(r'### \*\*(.+?)报告模板\*\*', content)
    if title_match:
        structure["template_name"] = title_match.group(1)

    # 解析章节结构
    lines = content.split('\n')
    current_chapter = None

    for line in lines:
        line = line.strip()

        # 匹配一级章节 (如: - **1.0 报告摘要**)
        chapter_match = re.match(r'- \*\*(\d+\.\d+)\s+(.+?)\*\*', line)
        if chapter_match:
            if current_chapter:
                structure["chapters"].append(current_chapter)

            current_chapter = {
                "id": chapter_match.group(1),
                "title": chapter_match.group(2),
                "subsections": []
            }

        # 匹配二级章节 (如: - 1.1 事件定性)
        subchapter_match = re.match(r'- (\d+\.\d+)\s+(.+)', line)
        if subchapter_match and current_chapter:
            current_chapter["subsections"].append({
                "id": subchapter_match.group(1),
                "title": subchapter_match.group(2)
            })

    # 添加最后一个章节
    if current_chapter:
        structure["chapters"].append(current_chapter)

    return structure


def get_template_description(template_name: str) -> str:
    """获取模板的描述信息"""
    if template_name in TEMPLATE_MAPPING:
        return TEMPLATE_MAPPING[template_name]["description"]
    return "通用舆情分析报告模板"


def list_all_templates() -> List[Dict]:
    """
    列出所有可用的模板

    Returns:
        模板信息列表
    """
    templates = []
    for name, config in TEMPLATE_MAPPING.items():
        templates.append({
            "name": name,
            "description": config["description"],
            "keywords": config["keywords"],
            "filename": config["filename"]
        })
    return templates


def validate_template(template_path: str) -> bool:
    """
    验证模板文件是否有效

    Args:
        template_path: 模板文件路径

    Returns:
        是否有效
    """
    if not os.path.exists(template_path):
        return False

    try:
        structure = parse_template_structure(template_path)
        return len(structure["chapters"]) > 0
    except Exception:
        return False


def get_section_content_guidance(section_title: str) -> str:
    """
    根据章节标题获取内容填充指导

    Args:
        section_title: 章节标题

    Returns:
        内容填充指导
    """
    guidance_map = {
        "时间线": """
        该章节需要包含：
        1. 结构化时间线表格（时间、事件、来源、影响力）
        2. 每个关键节点的详细说明
        3. 时间线背后的趋势分析
        """,
        "对比": """
        该章节需要包含：
        1. 对比维度表格
        2. 数据差异分析
        3. 优劣势总结
        """,
        "摘要": """
        该章节需要包含：
        1. 核心结论（3-5条）
        2. 关键指标表现
        3. 主要建议
        """,
        "分析": """
        该章节需要包含：
        1. 3-5段详细分析文字
        2. 数据支撑和案例
        3. 洞察和趋势判断
        """,
        "风险": """
        该章节需要包含：
        1. 风险识别和分类
        2. 风险等级评估
        3. 应对建议
        """,
        "建议": """
        该章节需要包含：
        1. 具体可执行的建议
        2. 优先级排序
        3. 实施路径
        """
    }

    for key, guidance in guidance_map.items():
        if key in section_title:
            return guidance

    return """
    该章节需要包含：
    1. 3-5段详细分析文字
    2. 具体数据支撑
    3. 深度洞察和结论
    """


# 便捷函数
def load_template_for_query(user_query: str) -> Dict:
    """
    一站式函数：根据用户查询加载并解析模板

    Args:
        user_query: 用户查询

    Returns:
        完整的模板结构字典
    """
    template_name, template_path = select_report_template(user_query)
    structure = parse_template_structure(template_path)
    structure["selected_template_name"] = template_name
    structure["template_path"] = template_path
    structure["description"] = get_template_description(template_name)

    # 为每个子章节添加内容指导
    for chapter in structure["chapters"]:
        for subsec in chapter["subsections"]:
            subsec["guidance"] = get_section_content_guidance(subsec["title"])

    return structure


if __name__ == "__main__":
    # 测试代码
    print("=" * 50)
    print("BettaFish Skill 模板管理器测试")
    print("=" * 50)

    # 测试模板选择
    test_queries = [
        "分析某咖啡连锁品牌 的品牌声誉",
        "某音乐节安全事故危机分析",
        "对比可口可乐和百事可乐的舆情表现",
        "追踪环保新规的饮料行业影响",
        "本周我司品牌舆情监测"
    ]

    print("\n【模板选择测试】")
    for query in test_queries:
        name, path = select_report_template(query)
        print(f"\n查询: {query}")
        print(f"选择模板: {name}")
        print(f"文件路径: {path}")

    # 测试模板解析
    print("\n\n【模板结构解析测试】")
    name, path = select_report_template("品牌声誉分析")
    structure = parse_template_structure(path)

    print(f"\n模板名称: {structure['template_name']}")
    print(f"章节数量: {len(structure['chapters'])}")

    for chapter in structure["chapters"]:
        print(f"\n{chapter['id']} {chapter['title']}")
        for sub in chapter["subsections"]:
            print(f"  - {sub['id']} {sub['title']}")

    # 列出所有模板
    print("\n\n【可用模板列表】")
    templates = list_all_templates()
    for t in templates:
        print(f"\n- {t['name']}")
        print(f"  描述: {t['description']}")
        print(f"  关键词: {', '.join(t['keywords'][:3])}...")
