#!/usr/bin/env python3
"""
腾讯云 MPS 用量统计查询脚本

功能：
  查询指定时间范围内的 MPS 媒体处理用量信息，支持按任务类型和地域过滤。
  可查询最近 365 天内的数据，单次查询跨度不超过 90 天。

支持的任务类型（--type 参数）：
  Transcode         转码
  Enhance           增强
  AIAnalysis        智能分析
  AIRecognition     智能识别
  AIReview          内容审核
  Snapshot          截图
  AnimatedGraphics  转动图
  AiQualityControl  质检
  Evaluation        视频评测
  ImageProcess      图片处理
  AddBlindWatermark 添加基础版权数字水印
  AIGC              AIGC（生图/生视频）

支持的地域（--region 参数）：
  ap-guangzhou（默认）、ap-hongkong、ap-singapore、
  na-siliconvalley、eu-frankfurt 等

用法：
  # 查询最近 7 天转码用量（默认）
  python scripts/mps_usage.py

  # 查询指定日期范围
  python scripts/mps_usage.py --start 2024-01-01 --end 2024-01-31

  # 查询多个任务类型
  python scripts/mps_usage.py --type Transcode Enhance AIGC

  # 查询指定地域
  python scripts/mps_usage.py --region ap-guangzhou ap-hongkong

  # 输出 JSON 格式（方便程序处理）
  python scripts/mps_usage.py --json

  # 查询最近 30 天所有类型
  python scripts/mps_usage.py --days 30 --all-types
"""

import sys
import os
import json
import argparse
from datetime import datetime, timedelta, timezone

# ── 加载环境变量 ──
_script_dir = os.path.dirname(os.path.abspath(__file__))
_load_env = os.path.join(_script_dir, "load_env.py")
if os.path.exists(_load_env):
    import importlib.util
    spec = importlib.util.spec_from_file_location("load_env", _load_env)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

try:
    from tencentcloud.common import credential
    from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
    from tencentcloud.mps.v20190612 import mps_client, models
except ImportError:
    print("❌ 缺少依赖，请运行: pip install tencentcloud-sdk-python", file=sys.stderr)
    sys.exit(1)

# 所有支持的任务类型
ALL_TASK_TYPES = [
    "Transcode", "Enhance", "AIAnalysis", "AIRecognition",
    "AIReview", "Snapshot", "AnimatedGraphics", "AiQualityControl",
    "Evaluation", "ImageProcess", "AddBlindWatermark",
    "AddNagraWatermark", "ExtractBlindWatermark", "AIGC",
]

# 任务类型中文名（AvUnderstand 属于 AIAnalysis，不是独立类型）
TYPE_NAMES = {
    "Transcode":              "转码",
    "Enhance":                "增强",
    "AIAnalysis":             "智能分析（含大模型音视频理解 AvUnderstand）",
    "AIRecognition":          "智能识别",
    "AIReview":               "内容审核",
    "Snapshot":               "截图",
    "AnimatedGraphics":       "转动图",
    "AiQualityControl":       "质检",
    "Evaluation":             "视频评测",
    "ImageProcess":           "图片处理",
    "AddBlindWatermark":      "添加基础版权数字水印",
    "AddNagraWatermark":      "添加NAGRA数字水印",
    "ExtractBlindWatermark":  "提取基础版权数字水印",
    "AIGC":                   "AIGC（生图/生视频）",
}


def get_credentials():
    secret_id = os.environ.get("TENCENTCLOUD_SECRET_ID", "")
    secret_key = os.environ.get("TENCENTCLOUD_SECRET_KEY", "")
    if not secret_id or not secret_key:
        print("❌ 请配置环境变量 TENCENTCLOUD_SECRET_ID 和 TENCENTCLOUD_SECRET_KEY", file=sys.stderr)
        sys.exit(1)
    return credential.Credential(secret_id, secret_key)


def to_iso8601(date_str: str) -> str:
    """将 YYYY-MM-DD 转换为 ISO 8601 格式（+08:00）"""
    dt = datetime.strptime(date_str, "%Y-%m-%d")
    return dt.strftime("%Y-%m-%dT00:00:00+08:00")


def query_usage(
    start_time: str,
    end_time: str,
    types: list = None,
    regions: list = None,
    region: str = "ap-guangzhou",
    dry_run: bool = False,
    raise_on_error: bool = False,
) -> dict:
    """
    调用 DescribeUsageData 接口查询用量
    返回原始 API 响应数据
    raise_on_error=True 时抛出异常而非 sys.exit（用于批量容错场景）
    """
    cred = get_credentials()
    client = mps_client.MpsClient(cred, region)

    req = models.DescribeUsageDataRequest()
    req.StartTime = to_iso8601(start_time)
    req.EndTime = to_iso8601(end_time)

    if types:
        req.Types = types
    if regions:
        req.ProcessRegions = regions

    if dry_run:
        print("[dry-run] 请求参数:")
        print(f"  StartTime: {req.StartTime}")
        print(f"  EndTime:   {req.EndTime}")
        print(f"  Types:     {types or '默认(Transcode)'}")
        print(f"  Regions:   {regions or '[ap-guangzhou]'}")
        return {}

    try:
        resp = client.DescribeUsageData(req)
        return json.loads(resp.to_json_string())
    except TencentCloudSDKException as e:
        if raise_on_error:
            raise
        print(f"❌ API 调用失败: {e}", file=sys.stderr)
        sys.exit(1)


def format_usage(usage_seconds: int, task_type: str) -> str:
    """格式化用量数值（转码类用分钟，AIGC 类用次数）"""
    aigc_types = {"AIGC", "AIAnalysis", "AIRecognition", "AIReview",
                  "AiQualityControl", "Evaluation", "AddBlindWatermark",
                  "AddNagraWatermark", "ExtractBlindWatermark"}
    if task_type in aigc_types:
        return f"{usage_seconds} 次"
    # 转码/增强/图片处理等：Usage 单位为秒
    minutes = usage_seconds / 60
    if minutes >= 60:
        return f"{minutes/60:.2f} 小时 ({minutes:.1f} 分钟)"
    return f"{minutes:.2f} 分钟"


def print_report(data: dict, output_json: bool = False):
    """格式化输出用量报告"""
    if output_json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    task_data_list = data.get("Data", [])
    if not task_data_list:
        print("📊 查询结果为空（该时间段内无用量数据）")
        return

    print("\n" + "═" * 60)
    print("  📊 MPS 媒体处理用量报告")
    print("═" * 60)

    for task_data in task_data_list:
        task_type = task_data.get("TaskType", "Unknown")
        type_name = TYPE_NAMES.get(task_type, task_type)
        summary = task_data.get("Summary", [])
        details = task_data.get("Details", [])

        # 汇总统计
        total_count = sum(s.get("Count", 0) for s in summary)
        total_usage = sum(s.get("Usage", 0) for s in summary)

        print(f"\n▶ {task_type} — {type_name}")
        print(f"  总调用次数: {total_count:,}")
        print(f"  总用量:     {format_usage(total_usage, task_type)}")

        # 按天明细
        if summary:
            print(f"  {'日期':<22} {'次数':>8} {'用量':>20}")
            print(f"  {'-'*22} {'-'*8} {'-'*20}")
            for s in summary:
                date = s.get("Time", "")[:10]
                count = s.get("Count", 0)
                usage = s.get("Usage", 0)
                usage_str = format_usage(usage, task_type)
                print(f"  {date:<22} {count:>8,} {usage_str:>20}")

        # 规格明细
        if details:
            print(f"\n  规格明细:")
            for detail in details:
                spec = detail.get("Specification", "")
                spec_data = detail.get("Data", [])
                spec_count = sum(d.get("Count", 0) for d in spec_data)
                spec_usage = sum(d.get("Usage", 0) for d in spec_data)
                if spec_count > 0:
                    print(f"    {spec:<35} {spec_count:>8,} 次  {format_usage(spec_usage, task_type)}")

    print("\n" + "═" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="查询 MPS 媒体处理用量统计",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    # 时间参数
    time_group = parser.add_mutually_exclusive_group()
    time_group.add_argument("--days", type=int, default=7,
                            help="查询最近 N 天（默认 7 天，最大 90）")
    time_group.add_argument("--start", metavar="YYYY-MM-DD",
                            help="起始日期（与 --end 配合使用）")
    parser.add_argument("--end", metavar="YYYY-MM-DD",
                        help="结束日期（默认为今天）")

    # 类型参数
    type_group = parser.add_mutually_exclusive_group()
    type_group.add_argument("--type", nargs="+", choices=ALL_TASK_TYPES,
                            metavar="TYPE", dest="types",
                            help="查询的任务类型（可多选），默认: Transcode")
    type_group.add_argument("--all-types", action="store_true",
                            help="查询所有任务类型")

    # 地域参数
    parser.add_argument("--region", nargs="+", dest="process_regions",
                        metavar="REGION",
                        help="处理地域（可多选），默认: ap-guangzhou")

    # 输出参数
    parser.add_argument("--json", action="store_true",
                        help="以 JSON 格式输出原始数据")
    parser.add_argument("--dry-run", action="store_true",
                        help="仅打印请求参数，不实际调用")

    args = parser.parse_args()

    # ── 计算时间范围 ──
    today = datetime.now(tz=timezone(timedelta(hours=8))).strftime("%Y-%m-%d")

    if args.start:
        start_date = args.start
        end_date = args.end or today
    else:
        days = min(args.days, 90)
        end_date = today
        start_dt = datetime.strptime(end_date, "%Y-%m-%d") - timedelta(days=days - 1)
        start_date = start_dt.strftime("%Y-%m-%d")

    # ── 确定任务类型 ──
    if args.all_types:
        types = ALL_TASK_TYPES
    elif args.types:
        types = args.types
    else:
        types = None  # 默认由 API 返回 Transcode

    print(f"🔍 查询时间: {start_date} ~ {end_date}")
    print(f"📋 任务类型: {', '.join(types) if types else '默认(Transcode)'}")
    print(f"🌏 处理地域: {', '.join(args.process_regions) if args.process_regions else 'ap-guangzhou'}")

    # ── 调用 API ──
    if args.all_types:
        # --all-types 模式：逐个类型查询，容错处理
        all_data = []
        failed_types = []
        for t in types:
            try:
                data = query_usage(
                    start_time=start_date,
                    end_time=end_date,
                    types=[t],
                    regions=args.process_regions,
                    dry_run=args.dry_run,
                    raise_on_error=True,
                )
                if not args.dry_run:
                    task_list = data.get("Data", [])
                    if task_list:
                        all_data.extend(task_list)
            except TencentCloudSDKException as e:
                print(f"  ⚠️  {t} 查询失败: {e}", file=sys.stderr)
                failed_types.append(t)

        if failed_types:
            print(f"\n⚠️  以下类型查询失败（可能不支持或无权限）: {', '.join(failed_types)}", file=sys.stderr)

        if not args.dry_run:
            merged = {"Data": all_data}
            print_report(merged, output_json=args.json)
    else:
        data = query_usage(
            start_time=start_date,
            end_time=end_date,
            types=types,
            regions=args.process_regions,
            dry_run=args.dry_run,
        )

        if not args.dry_run:
            print_report(data, output_json=args.json)


if __name__ == "__main__":
    main()
