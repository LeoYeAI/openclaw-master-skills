#!/usr/bin/env python3
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(current_dir)))
sys.path.insert(0, parent_dir)

import argparse
import json
import mimetypes
import traceback
from datetime import datetime

import requests
import sys
import os

from .config import *

from .skill import skill

from skills.smyx_common.scripts.util import RequestUtil

# 从config导入常量
SUPPORTED_FORMATS = ConstantEnum.SUPPORTED_FORMATS
MAX_FILE_SIZE_MB = ConstantEnum.MAX_FILE_SIZE_MB


def validate_file(file_path):
    """验证输入文件是否合法"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件不存在: {file_path}")

    if not os.access(file_path, os.R_OK):
        raise PermissionError(f"文件没有读权限: {file_path}")

    ext = os.path.splitext(file_path)[1].lower()[1:]
    if ext not in SUPPORTED_FORMATS:
        raise ValueError(f"不支持的文件格式，支持的格式: {', '.join(SUPPORTED_FORMATS)}")

    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
    if file_size_mb > MAX_FILE_SIZE_MB:
        raise ValueError(f"文件过大，最大支持 {MAX_FILE_SIZE_MB}MB，当前文件大小: {file_size_mb:.1f}MB")

    return True


def analyze_video(input_path=None, url=None, pet_type=None, monitor_days=None, api_url=None, api_key=None,
                  output_level=None):
    """调用API分析宠物健康监测视频"""
    if not input_path and not url:
        raise ValueError("必须提供本地视频路径(--input)或网络视频URL(--url)")

    # 设置参数
    if pet_type:
        ConstantEnum.DEFAULT_PET_TYPE = pet_type
    if monitor_days:
        ConstantEnum.DEFAULT_MONITOR_DAYS = monitor_days

    try:
        input_path = input_path or url
        params = {}
        if monitor_days:
            params["monitor_days"] = monitor_days
        return skill.get_output_analysis(input_path, params)

    except requests.exceptions.RequestException as e:
        traceback.print_stack()
        raise Exception(f"API请求失败: {str(e)}")


def show_analyze_list(open_id, start_time=None, end_time=None):
    # if not open_id:
    #     raise ValueError("必须提供本用户的OpenId/UserId")

    try:
        output_content = skill.get_output_analysis_list()
        return output_content

    except requests.exceptions.RequestException as e:
        traceback.print_stack()
        raise Exception(f"API请求失败: {str(e)}")


def get_analysis_export_url(request_id=None):
    """调用API分析视频"""
    if not request_id:
        return ""
    return ApiEnum.DETAIL_EXPORT_URL + request_id


def format_result(result, output_level="standard", pet_type="cat", monitor_days=1):
    """格式化输出结果"""
    pet_type_map = {
        "cat": "猫",
        "dog": "狗"
    }
    pet_type_cn = pet_type_map.get(pet_type, pet_type)

    if output_level == "json":
        result_id = None
        if result is not None:
            result_json = result
            result_id = result_json.get('id', {})
            result_json = json.dumps(result_json.get('petHealthMonitoringResponse', {}), ensure_ascii=False, indent=2)
        else:
            return "⚠️ 暂无分析结果"
        return f"""
📊 宠物健康监测分析结构化结果
{result_json}
""", result_id
    elif output_level == "basic":
        # 精简输出
        data = result.get('data', {})
        monitoring = data.get('monitoring', {})
        abnormalities = monitoring.get('abnormalities', [])
        abnormality_str = ', '.join(abnormalities) if abnormalities else '未发现明显异常'
        return f"""
📊 宠物健康监测报告
{'=' * 40}
宠物类型: {pet_type_cn}
监测时长: {monitor_days} 天
整体健康评分: {monitoring.get('health_score', '未知')}
发现异常: {abnormality_str}
健康提示: {data.get('health_tip', ['无特殊提示'])[0] if data.get('health_tip') else '无特殊提示'}
        """
    elif output_level == "standard":
        # 标准输出
        data = result.get('data', {})
        monitoring = data.get('monitoring', {})

        behavior_stats = f"""  进食频次: {monitoring.get('eating_count', 0)} 次/天
  饮水频次: {monitoring.get('drinking_count', 0)} 次/天"""
        if monitoring.get('defecation_count') is not None:
            behavior_stats += f"\n  排泄次数: {monitoring.get('defecation_count', 0)} 次"

        abnormalities = "\n".join([f"  ⚠️  {item}" for item in monitoring.get('abnormal_items', [])])
        warnings = "\n".join([f"  ⚠️  {item}" for item in data.get('health_warnings', [])])
        suggestions = "\n".join([f"  💡 {item}" for item in data.get('care_suggestions', [])])

        abnormal_items = []
        if monitoring.get('has_lethargy'):
            abnormal_items.append('精神萎靡')
        if monitoring.get('has_vomiting'):
            abnormal_items.append('呕吐行为')
        if monitoring.get('has_lameness'):
            abnormal_items.append('跛行异常')
        if monitoring.get('abnormal_defecation'):
            abnormal_items.append('排泄异常')
        if abnormal_items:
            abnormalities = "\n".join([f"  ⚠️  {item}" for item in abnormal_items])
        else:
            abnormalities = "  ✅ 未发现明显异常行为"

        return f"""
📊 宠物日常健康监测分析报告
{'=' * 50}
⏰ 监测时间: {data.get('monitoring_time', '未知')}
🐾 宠物类型: {pet_type_cn}
📅 监测时长: {monitor_days} 天
🎯 监测状态: {monitoring.get('status', '未知')} (置信度: {monitoring.get('overall_confidence', 0)}分)

🔍 行为统计:
{behavior_stats}

🚨 异常行为识别:
{abnormalities}

⚠️ 健康预警提示:
{warnings if warnings else '  无特殊预警'}

💡 养护建议:
{suggestions if suggestions else '  暂无特别建议'}

{'=' * 50}
> 注：本报告仅供健康参考，不能替代专业兽医诊断，发现异常请及时就医。
        """
    else:
        # 完整输出（JSON格式）
        return json.dumps(result, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="宠物日常健康监测分析工具")
    parser.add_argument("--input", help="本地视频文件路径")
    parser.add_argument("--url", help="网络视频的URL地址")
    parser.add_argument("--pet-type", choices=["cat", "dog"], default=ConstantEnum.DEFAULT__PET_TYPE,
                        help="宠物类型：cat(猫), dog(狗)，默认 cat")
    parser.add_argument("--monitor-days", type=int, default=ConstantEnum.DEFAULT__MONITOR_DAYS,
                        help="监测覆盖天数，默认 1")
    parser.add_argument("--open-id", required=True, help="当前用户的OpenID/UserId/用户名/手机号")
    parser.add_argument("--list", action='store_true', help="显示宠物健康监测分析列表清单")
    parser.add_argument("--api-url", help="服务端API地址")
    parser.add_argument("--api-key", help="API访问密钥（必需）")
    parser.add_argument("--output", help="结果输出文件路径")
    parser.add_argument("--detail", choices=["basic", "standard", "json"],
                        default=ConstantEnum.DEFAULT__OUTPUT_LEVEL,
                        help="输出详细程度")
    parser.add_argument("--export-env-only", action='store_true',
                        help="仅输出 export 命令设置环境变量，不执行分析")

    args = parser.parse_args()

    try:
        if args.open_id:
            # 设置 Python 进程内的环境变量
            ConstantEnumBase.CURRENT__OPEN_ID = args.open_id

        # 检查必需参数
        if args.list:
            open_id = ConstantEnum.CURRENT__OPEN_ID
            result = show_analyze_list(open_id)
            print(result)
            exit(0)

        # 检查必需参数
        if not args.input and not args.url:
            print("❌ 错误: 必须提供 --input 或 --url 参数")
            exit(1)

        print("🔍 正在进行宠物健康监测分析，请稍候...")
        output_content = analyze_video(
            input_path=args.input,
            url=args.url,
            pet_type=args.pet_type,
            monitor_days=args.monitor_days,
            api_url=args.api_url,
            api_key=args.api_key,
            output_level=args.detail
        )

        print(output_content)

        # 保存到文件
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                if args.detail == "full":
                    json.dump(result, f, ensure_ascii=False, indent=2)
                else:
                    f.write(output_content)
            print(f"✅ 结果已保存到: {args.output}")

    except Exception as e:
        traceback.print_stack()
        print(f"❌ 宠物健康监测分析失败: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()
