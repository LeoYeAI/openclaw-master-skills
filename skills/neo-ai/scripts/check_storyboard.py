#!/usr/bin/env python3
"""
分镜图片质量检查脚本
检查项：
1. 图片中的明显错误
2. 人物一致性
3. 镜头连续性
"""

import argparse
import json
import os
import sys
from pathlib import Path

# 角色参考图URL映射
CHARACTER_REFS = {
    "苏曼": "https://wlpaas.oss-cn-shanghai.aliyuncs.com/temp/20260311/f1d4c814.jpeg",
    "凤天天": "https://wlpaas.oss-cn-shanghai.aliyuncs.com/temp/20260311/f1d4c814.jpeg",
    "家暴男": "https://wlpaas.oss-cn-shanghai.aliyuncs.com/temp/20260311/3ebd2034.jpeg",
    "大伯": "https://wlpaas.oss-cn-shanghai.aliyuncs.com/temp/20260311/fae42bbf.jpeg",
    "苏强": "https://wlpaas.oss-cn-shanghai.aliyuncs.com/temp/20260311/020e4be7.jpeg",
    "王媒婆": "https://wlpaas.oss-cn-shanghai.aliyuncs.com/temp/20260311/5c806c4f.jpeg",
    "秦枭": "https://wlpaas.oss-cn-shanghai.aliyuncs.com/temp/20260311/322cc6f8.jpeg",
    "云修竹": "https://wlpaas.oss-cn-shanghai.aliyuncs.com/temp/20260311/322cc6f8.jpeg",
    "谢云渊": "https://wlpaas.oss-cn-shanghai.aliyuncs.com/temp/20260311/322cc6f8.jpeg",
    "许易安": "https://wlpaas.oss-cn-shanghai.aliyuncs.com/temp/20260311/f1d4c814.jpeg",
    "正道人士": "https://wlpaas.oss-cn-shanghai.aliyuncs.com/temp/20260311/3ebd2034.jpeg",
}

# 从剧本中提取的分镜信息
SCENE_INFO = {
    1: {"角色": ["凤天天"], "情绪": "疲惫愤怒"},
    2: {"角色": ["凤天天"], "情绪": "震惊"},
    3: {"角色": ["凤天天", "冷烨"], "情绪": "冷静决绝"},
    4: {"角色": ["凤天天"], "情绪": "决绝坚定"},
    5: {"角色": ["凤天天"], "情绪": "坚定希望"},
    18: {"角色": ["苏曼"], "情绪": "恐惧"},
    19: {"角色": ["凤天天"], "情绪": "平静"},
    20: {"角色": ["凤天天", "正道人士"], "情绪": "紧张危险"},
    21: {"角色": ["凤天天"], "情绪": "惊喜"},
    22: {"角色": ["凤天天"], "情绪": "得意搞笑"},
    23: {"角色": ["凤天天"], "情绪": "得意反转"},
}


def analyze_image_issues(image_path: str, scene_num: int) -> dict:
    """分析图片问题（这里只返回检查项，实际分析需要调用图像模型）"""
    scene_info = SCENE_INFO.get(scene_num, {})
    
    return {
        "scene_num": scene_num,
        "expected_characters": scene_info.get("角色", []),
        "expected_mood": scene_info.get("情绪", ""),
        "image_path": image_path,
        "issues": [],  # 由AI填充
        "suggestions": [],  # 由AI填充
    }


def main():
    parser = argparse.ArgumentParser(description="检查分镜图片质量")
    parser.add_argument("--storyboard-dir", required=True, help="分镜图片目录")
    parser.add_argument("--output", default="quality_report.json", help="输出报告文件")
    
    args = parser.parse_args()
    
    storyboard_dir = Path(args.storyboard_dir)
    
    # 扫描所有分镜图片
    images = sorted(storyboard_dir.glob("shot_*.jpeg"))
    
    print(f"📸 检查 {len(images)} 个分镜图片...")
    
    results = []
    for img in images:
        # 提取镜头编号
        scene_num = int(img.stem.replace("shot_", ""))
        
        info = analyze_image_issues(str(img), scene_num)
        results.append(info)
        
        print(f"  镜头 {scene_num}: 预期角色 {info['expected_characters']}, 情绪 {info['expected_mood']}")
    
    # 保存检查清单
    with open(args.output, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 检查清单已保存到: {args.output}")
    print("\n请使用图像分析工具逐个检查图片，提出修改意见。")


if __name__ == "__main__":
    main()
