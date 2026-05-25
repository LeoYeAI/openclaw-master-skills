#!/usr/bin/env python3
"""
腾讯云 MPS 媒体质检脚本

功能：
  调用 MPS 媒体质检能力（AiQualityControl），对音视频进行自动化质量检测。
  支持通过 URL 或 COS 对象路径输入，自动创建任务并轮询等待结果。

  API 文档：https://cloud.tencent.com/document/product/862/37578
  数据结构：https://cloud.tencent.com/document/api/862/37615#AiQualityControlTaskInput

质检模板说明：
  - 60（默认）：格式质检模板-Pro版，检测画面内容问题（模糊、花屏等画面受损）
  - 70：内容质检模板-Pro版，检测播放问题（播放兼容性、卡顿、播放异常等）
  - 50：Audio Detection，针对音频内容检测（音频质量、音频事件）

COS 存储约定：
  通过环境变量 TENCENTCLOUD_COS_BUCKET 指定 COS Bucket 名称。
  - 输入文件默认路径：{TENCENTCLOUD_COS_BUCKET}/input/   （即 COS Object 以 /input/ 开头）
  - 输出文件默认路径：{TENCENTCLOUD_COS_BUCKET}/output/quality_control/  （即输出目录为 /output/quality_control/）

  当使用 COS 输入时，如果未显式指定 --cos-bucket，自动使用 TENCENTCLOUD_COS_BUCKET。
  当未显式指定 --output-bucket，自动使用 TENCENTCLOUD_COS_BUCKET 作为输出 Bucket。
  当未显式指定 --output-dir，自动使用 /output/quality_control/ 作为输出目录。
用法：
  # 基础：对视频 URL 发起质检（默认模板 60，检测画面模糊/花屏等画面问题）
  python scripts/mps_qualitycontrol.py --url https://example.com/video.mp4

  # 播放兼容性检测（模板 70）：检测视频能否正常播放、播放卡顿、播放异常等兼容性问题
  python scripts/mps_qualitycontrol.py --url https://example.com/video.mp4 --definition 70

  # 画面质量检测（模板 60，默认）：检测画面模糊、花屏、画面受损等画面内容问题
  python scripts/mps_qualitycontrol.py --url https://example.com/video.mp4 --definition 60

  # 音频质检（模板 50）：检测音频质量、音频事件等音频内容问题
  python scripts/mps_qualitycontrol.py --url https://example.com/audio.mp3 --definition 50

  # 指定 COS 对象输入
  python scripts/mps_qualitycontrol.py --cos-object input/video.mp4

  # COS路径输入（推荐，本地上传后使用）
  python scripts/mps_qualitycontrol.py --cos-input-bucket mybucket-125xxx --cos-input-region ap-guangzhou --cos-input-key /input/video.mp4

  # 异步模式（只提交任务，不等待结果）
  python scripts/mps_qualitycontrol.py --url https://example.com/video.mp4 --no-wait

  # 查询已有任务结果
  python scripts/mps_qualitycontrol.py --task-id 2600011633-WorkflowTask-xxxxx

  # JSON 格式输出
  python scripts/mps_qualitycontrol.py --url https://example.com/video.mp4 --json

  # dry-run 模式（只打印参数，不实际调用）
  python scripts/mps_qualitycontrol.py --url https://example.com/video.mp4 --dry-run

  # 指定地域
  python scripts/mps_qualitycontrol.py --url https://example.com/video.mp4 --region ap-guangzhou

参数规范：
  所有命令行参数必须使用连字符形式（--task-id、--cos-object、--no-wait、--dry-run 等），
  不能使用下划线形式（--task_id、--cos_object、--no_wait 等）。
"""

import sys
import os
import json
import time
import argparse

_script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _script_dir)
try:
    import load_env as _le
    _le.load_env_files()
except Exception:
    pass

try:
    from tencentcloud.common import credential
    from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
    from tencentcloud.mps.v20190612 import mps_client, models
except ImportError:
    print("错误: 未安装腾讯云 SDK，请运行: pip install tencentcloud-sdk-python", file=sys.stderr)
    sys.exit(1)

# ─────────────────────────────────────────────
# 配置
# ─────────────────────────────────────────────
DEFAULT_REGION     = "ap-guangzhou"
DEFAULT_DEFINITION = 60   # 格式质检-Pro版（默认）
POLL_INTERVAL      = 5    # 轮询间隔（秒）
POLL_TIMEOUT       = 600  # 最大等待时间（秒）

DEFINITION_DESC = {
    50: "Audio Detection（音频质量/事件检测）",
    60: "格式质检-Pro版（画面模糊/花屏/受损检测）",
    70: "内容质检-Pro版（播放兼容性/卡顿/播放异常检测）",
}

# ─────────────────────────────────────────────
# 凭证
# ─────────────────────────────────────────────
def get_credentials():
    secret_id  = os.environ.get("TENCENTCLOUD_SECRET_ID", "")
    secret_key = os.environ.get("TENCENTCLOUD_SECRET_KEY", "")
    if not secret_id or not secret_key:
        print("❌ 请配置环境变量 TENCENTCLOUD_SECRET_ID 和 TENCENTCLOUD_SECRET_KEY", file=sys.stderr)
        sys.exit(1)
    return credential.Credential(secret_id, secret_key)


# ─────────────────────────────────────────────
# 辅助函数
# ─────────────────────────────────────────────
def get_cos_bucket():
    """获取 COS Bucket 名称（从环境变量或默认值）。"""
    return os.environ.get("TENCENTCLOUD_COS_BUCKET", "")

def get_cos_region():
    """获取 COS Region（从环境变量或默认值）。"""
    return os.environ.get("TENCENTCLOUD_COS_REGION", "")

def build_output_storage(args):
    """
    构建输出存储信息。

    优先级：
    1. 命令行参数 --output-bucket / --output-region
    2. 环境变量 TENCENTCLOUD_COS_BUCKET / TENCENTCLOUD_COS_REGION
    """
    bucket = args.output_bucket or get_cos_bucket()
    region = args.output_region or get_cos_region()

    if bucket and region:
        return {
            "Type": "COS",
            "CosOutputStorage": {
                "Bucket": bucket,
                "Region": region
            }
        }
    return None


# ─────────────────────────────────────────────
# 占位符检测
# ─────────────────────────────────────────────
def is_placeholder(value: str) -> bool:
    """检测字符串是否为占位符格式，如 <视频URL>、YOUR_URL、<YOUR_VALUE> 等。"""
    if not value:
        return False
    stripped = value.strip()
    # 尖括号包裹的占位符，如 <视频URL>、<YOUR_URL>、<your-value>
    if stripped.startswith("<") and stripped.endswith(">"):
        return True
    # YOUR_ 前缀的占位符，如 YOUR_URL、YOUR_BUCKET
    if stripped.upper().startswith("YOUR_"):
        return True
    return False


# ─────────────────────────────────────────────
# 构建输入信息
# ─────────────────────────────────────────────
def build_input_info(url: str = None, cos_object: str = None, 
                     cos_input_bucket: str = None, cos_input_region: str = None, cos_input_key: str = None,
                     region: str = DEFAULT_REGION) -> dict:
    # 方式1: URL 输入
    if url:
        if is_placeholder(url):
            print(f"❌ --url 参数值 '{url}' 是占位符，请替换为真实的视频 URL", file=sys.stderr)
            sys.exit(1)
        return {"Type": "URL", "UrlInputInfo": {"Url": url}}
    
    # 方式3: COS 完整路径输入（新版，推荐）
    if cos_input_bucket and cos_input_region and cos_input_key:
        if is_placeholder(cos_input_bucket) or is_placeholder(cos_input_region) or is_placeholder(cos_input_key):
            print("❌ --cos-input-bucket/--cos-input-region/--cos-input-key 参数值包含占位符，请替换为真实值", file=sys.stderr)
            sys.exit(1)
        return {
            "Type": "COS",
            "CosInputInfo": {"Bucket": cos_input_bucket, "Region": cos_input_region, "Object": cos_input_key},
        }
    
    # 方式2: COS 对象路径输入（旧版，兼容）
    if cos_object:
        if is_placeholder(cos_object):
            print(f"❌ --cos-object 参数值 '{cos_object}' 是占位符，请替换为真实的 COS 对象路径", file=sys.stderr)
            sys.exit(1)
        bucket = os.environ.get("TENCENTCLOUD_COS_BUCKET", "")
        if not bucket:
            print("❌ 使用 COS 对象输入时需要配置 TENCENTCLOUD_COS_BUCKET 环境变量", file=sys.stderr)
            sys.exit(1)
        return {
            "Type": "COS",
            "CosInputInfo": {"Bucket": bucket, "Region": region, "Object": cos_object},
        }
    
    print("❌ 请指定输入源：--url、--cos-object 或 --cos-input-bucket/--cos-input-region/--cos-input-key", file=sys.stderr)
    sys.exit(1)


# ─────────────────────────────────────────────
# 提交质检任务
# ─────────────────────────────────────────────
def submit_quality_check(client, input_info: dict, definition: int, output_storage: dict = None) -> str:
    req = models.ProcessMediaRequest()
    req.InputInfo = models.MediaInputInfo()
    req.InputInfo.Type = input_info["Type"]

    if input_info["Type"] == "URL":
        req.InputInfo.UrlInputInfo = models.UrlInputInfo()
        req.InputInfo.UrlInputInfo.Url = input_info["UrlInputInfo"]["Url"]
    elif input_info["Type"] == "COS":
        req.InputInfo.CosInputInfo = models.CosInputInfo()
        req.InputInfo.CosInputInfo.Bucket = input_info["CosInputInfo"]["Bucket"]
        req.InputInfo.CosInputInfo.Region = input_info["CosInputInfo"]["Region"]
        req.InputInfo.CosInputInfo.Object = input_info["CosInputInfo"]["Object"]

    req.AiQualityControlTask = models.AiQualityControlTaskInput()
    req.AiQualityControlTask.Definition = definition

    # 设置输出存储（URL 输入时必填）
    if output_storage:
        req.OutputStorage = models.TaskOutputStorage()
        req.OutputStorage.Type = output_storage["Type"]
        req.OutputStorage.CosOutputStorage = models.CosOutputStorage()
        req.OutputStorage.CosOutputStorage.Bucket = output_storage["CosOutputStorage"]["Bucket"]
        req.OutputStorage.CosOutputStorage.Region = output_storage["CosOutputStorage"]["Region"]

    resp = client.ProcessMedia(req)
    return resp.TaskId


# ─────────────────────────────────────────────
# 查询任务结果
# ─────────────────────────────────────────────
def get_task_result(client, task_id: str) -> dict:
    req = models.DescribeTaskDetailRequest()
    req.TaskId = task_id
    resp = client.DescribeTaskDetail(req)
    return json.loads(resp.to_json_string())


def poll_task(client, task_id: str, timeout: int = POLL_TIMEOUT, interval: int = POLL_INTERVAL) -> dict:
    print(f"⏳ 等待质检任务完成（TaskId: {task_id}）...")
    elapsed = 0
    while elapsed < timeout:
        result = get_task_result(client, task_id)
        status = result.get("Status", "")
        if status == "FINISH":
            print(f"✅ 任务完成（耗时约 {elapsed}s）")
            return result
        elif status in ("FAIL", "ERROR"):
            print(f"❌ 任务失败: {result.get('ErrMsg', '')}", file=sys.stderr)
            return result
        print(f"   状态: {status}，已等待 {elapsed}s...")
        time.sleep(interval)
        elapsed += interval
    print(f"⚠️  超时（{timeout}s），返回最后一次查询结果", file=sys.stderr)
    return get_task_result(client, task_id)


# ─────────────────────────────────────────────
# 提取质检结果集
# ─────────────────────────────────────────────
def extract_qc_result(result: dict) -> tuple:
    """
    从 DescribeTaskDetail 返回值中提取质检结论和结果集。
    返回 (no_audio_video: str, quality_eval_score: int|None, result_set: list, result_set_type: str)

    DescribeTaskDetail 对于 WorkflowTask 任务，结构为：
      {
        "TaskType": "WorkflowTask",
        "Status": "FINISH",
        "AiQualityControlTaskResult": {
          "Status": "SUCCESS",
          "ErrCode": 0,
          "ErrMsg": "",
          "Input": { "Definition": 60 },
          "Output": {
            "NoAudioVideo": "Yes"|"No",
            "QualityEvaluationScore": 80,
            "ContainerDiagnoseResultSet": [  # 60模板：格式质检结果
              {
                "Type": "DecodeException",
                "Confidence": 95,
                "StartTimeOffset": 48.649,
                "EndTimeOffset": 48.7,
                "AreaCoordSet": [],
                "Suggestion": "review"
              },
              ...
            ],
            "QualityEvaluationResultSet": [  # 50模板：音频质检结果
              ...
            ]
          }
        }
      }

    对于 ProcessMedia 任务，结构为：
      {
        "TaskType": "ProcessMedia",
        "Status": "FINISH",
        "AiQualityControl": {
          ...
        }
      }
    """
    # 优先从 AiQualityControlTaskResult（WorkflowTask）获取，兼容 AiQualityControl（ProcessMedia）
    qc_task = result.get("AiQualityControlTaskResult") or result.get("AiQualityControl") or {}
    output = qc_task.get("Output") or {}

    no_av = output.get("NoAudioVideo", "")
    score = output.get("QualityEvaluationScore")

    # 优先解析 ContainerDiagnoseResultSet（60模板：格式质检-Pro版）
    # 如果为空，则解析 QualityEvaluationResultSet（50模板：音频质检等）
    result_set = output.get("ContainerDiagnoseResultSet") or []
    result_set_type = "ContainerDiagnoseResultSet"

    if not result_set:
        result_set = output.get("QualityEvaluationResultSet") or []
        result_set_type = "QualityEvaluationResultSet"

    # 兼容：部分旧版本或不同字段名
    if not result_set:
        result_set = (
            output.get("AiQualityControlResultSet")
            or result.get("AiQualityControlResultSet")
            or []
        )
        result_set_type = "Legacy"

    return no_av, score, result_set, result_set_type


# ─────────────────────────────────────────────
# 格式化输出
# ─────────────────────────────────────────────
def format_result(result: dict) -> str:
    lines = []

    task_status = result.get("Status", "")
    if task_status:
        lines.append(f"任务状态: {task_status}")

    qc_task = result.get("AiQualityControl") or {}
    sub_status = qc_task.get("Status", "")
    err_code   = qc_task.get("ErrCode") or 0
    err_msg    = qc_task.get("ErrMsg", "")
    if sub_status:
        lines.append(f"质检子任务状态: {sub_status}")
    if err_code != 0:
        lines.append(f"错误码: {err_code}  错误信息: {err_msg}")

    qc_input = qc_task.get("Input") or {}
    definition = qc_input.get("Definition")
    if definition is not None:
        desc = DEFINITION_DESC.get(int(definition), str(definition))
        lines.append(f"质检模板: {definition} — {desc}")

    no_av, score, result_set, result_set_type = extract_qc_result(result)

    if no_av:
        flag = "是" if no_av == "Yes" else "否"
        lines.append(f"无音视频内容: {flag} (NoAudioVideo={no_av})")

    if score is not None:
        lines.append(f"质量评分: {score} / 100")

    lines.append("")  # 空行分隔

    if not result_set:
        lines.append("未检测到质量问题（或暂无质检结论，可使用 --json 查看原始数据）")
        return "\n".join(lines)

    lines.append(f"质检问题列表（共 {len(result_set)} 条，数据源: {result_set_type}）：")
    for idx, item in enumerate(result_set, 1):
        item_type   = item.get("Type", "未知")
        confidence  = item.get("Confidence", "")
        start       = item.get("StartTimeOffset")
        end         = item.get("EndTimeOffset")
        suggestion  = item.get("Suggestion", "")
        area        = item.get("AreaCoordSet") or []

        line = f"  {idx}. [{item_type}]"
        if confidence != "":
            line += f"  置信度={confidence}"
        if start is not None and end is not None:
            line += f"  时间段={start}s~{end}s"
        elif start is not None:
            line += f"  起始={start}s"
        if suggestion:
            line += f"  建议={suggestion}"
        if area:
            line += f"  坐标={area}"
        lines.append(line)

    return "\n".join(lines)


# ─────────────────────────────────────────────
# CLI 入口
# ─────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="腾讯云 MPS 媒体质检",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument("--url",        help="音视频 URL（HTTP/HTTPS）")
    input_group.add_argument("--cos-object", help="COS 对象路径（如 input/video.mp4，已废弃，请使用 --cos-input-key）")
    input_group.add_argument("--task-id",    help="直接查询已有任务结果（跳过创建）")
    
    # COS 路径输入（新版，与 mps_transcode.py 等保持一致）
    parser.add_argument("--cos-input-bucket", type=str,
                        help="输入文件所在 COS Bucket 名称")
    parser.add_argument("--cos-input-region", type=str,
                        help="输入文件所在 COS Region（如 ap-guangzhou）")
    parser.add_argument("--cos-input-key", type=str,
                        help="输入文件的 COS Key（如 /input/video.mp4）")

    parser.add_argument(
        "--definition", type=int, default=DEFAULT_DEFINITION,
        choices=[50, 60, 70],
        help=(
            "质检模板 ID（默认 60）：\n"
            "  50 = Audio Detection（音频质量/事件）\n"
            "  60 = 格式质检-Pro版（画面模糊/花屏，默认）\n"
            "  70 = 内容质检-Pro版（播放兼容性/卡顿）"
        ),
    )
    parser.add_argument("--region",   default=DEFAULT_REGION, help=f"地域（默认 {DEFAULT_REGION}）")
    parser.add_argument("--output-bucket", type=str, help="输出 COS Bucket 名称（默认从环境变量 TENCENTCLOUD_COS_BUCKET 读取）")
    parser.add_argument("--output-region", type=str, help="输出 COS Region（默认从环境变量 TENCENTCLOUD_COS_REGION 读取）")
    parser.add_argument("--no-wait",  action="store_true",    help="异步模式：只提交任务，不等待结果")
    parser.add_argument("--json",     action="store_true",    dest="json_output", help="JSON 格式输出原始结果")
    parser.add_argument("--dry-run",  action="store_true",    help="只打印参数，不实际调用 API")

    # 在 parse_args 之前检测下划线形式的参数，严格拒绝不规范用法。
    # 原因：Python argparse 将 --task-id 内部转换为 task_id，外部调用必须使用连字符形式；
    #       下划线形式（--task_id）不被 argparse 识别，会作为未知参数静默忽略，
    #       导致逻辑错误且难以排查，因此在此提前拦截并给出明确提示。
    _underscore_map = {
        "--task_id":     "--task-id",
        "--cos_object":  "--cos-object",
        "--no_wait":     "--no-wait",
        "--dry_run":     "--dry-run",
        "--json_output": "--json",
    }
    for raw_arg in sys.argv[1:]:
        arg_name = raw_arg.split("=")[0]
        if arg_name in _underscore_map:
            correct = _underscore_map[arg_name]
            print(
                f"错误: 参数名称不规范，请使用连字符形式 '{correct}'，"
                f"不能使用下划线形式 '{arg_name}'",
                file=sys.stderr,
            )
            sys.exit(2)

    args = parser.parse_args()

    # 检查输入源
    has_url = bool(args.url)
    has_cos_object = bool(args.cos_object)
    has_cos_path = bool(getattr(args, 'cos_input_bucket', None) and 
                        getattr(args, 'cos_input_region', None) and 
                        getattr(args, 'cos_input_key', None))
    
    if not args.task_id and not has_url and not has_cos_object and not has_cos_path:
        parser.error("请指定 --url、--cos-object、--cos-input-bucket/--cos-input-region/--cos-input-key 或 --task-id")

    # 占位符检测（在 dry-run 之前，确保任何模式下均拒绝占位符）
    if args.url and is_placeholder(args.url):
        parser.error(f"--url 参数值 '{args.url}' 是占位符，请替换为真实的视频 URL")
    if args.cos_object and is_placeholder(args.cos_object):
        parser.error(f"--cos-object 参数值 '{args.cos_object}' 是占位符，请替换为真实的 COS 对象路径")
    if has_cos_path:
        if is_placeholder(args.cos_input_bucket) or is_placeholder(args.cos_input_region) or is_placeholder(args.cos_input_key):
            parser.error("--cos-input-bucket/--cos-input-region/--cos-input-key 参数值包含占位符，请替换为真实值")

    # dry-run
    if args.dry_run:
        print("🔍 dry-run 模式，参数如下：")
        if args.task_id:
            print(f"  TaskId:     {args.task_id}")
        elif args.url:
            print(f"  输入:       URL={args.url}")
        elif has_cos_path:
            print(f"  输入:       COS={args.cos_input_bucket}:{args.cos_input_key} (region: {args.cos_input_region})")
        else:
            print(f"  输入:       COS={args.cos_object}")
        print(f"  Definition: {args.definition} ({DEFINITION_DESC.get(args.definition, '')})")
        print(f"  Region:     {args.region}")
        print(f"  No-wait:    {args.no_wait}")
        return

    cred   = get_credentials()
    client = mps_client.MpsClient(cred, args.region)

    # 仅查询已有任务
    if args.task_id:
        print(f"🔍 查询任务结果: {args.task_id}")
        result = get_task_result(client, args.task_id)
        if args.json_output:
            print(json.dumps(result, ensure_ascii=False, indent=2))
        else:
            print(format_result(result))
        return

    # 提交新任务
    input_info = build_input_info(
        url=args.url, 
        cos_object=args.cos_object,
        cos_input_bucket=getattr(args, 'cos_input_bucket', None),
        cos_input_region=getattr(args, 'cos_input_region', None),
        cos_input_key=getattr(args, 'cos_input_key', None),
        region=args.region
    )
    
    # URL 输入时必须设置输出存储
    output_storage = None
    if args.url:
        output_storage = build_output_storage(args)
        if not output_storage:
            print("❌ URL 输入时必须指定输出存储", file=sys.stderr)
            print("   请配置环境变量 TENCENTCLOUD_COS_BUCKET 和 TENCENTCLOUD_COS_REGION，", file=sys.stderr)
            print("   或使用 --output-bucket 和 --output-region 参数", file=sys.stderr)
            sys.exit(1)
    
    def_desc   = DEFINITION_DESC.get(args.definition, str(args.definition))
    print(f"🚀 提交媒体质检任务")
    if args.url:
        print(f"   输入:     URL={args.url}")
    elif has_cos_path:
        print(f"   输入:     COS={args.cos_input_bucket}:{args.cos_input_key} (region: {args.cos_input_region})")
    else:
        print(f"   输入:     COS={args.cos_object}")
    print(f"   模板:     {args.definition} — {def_desc}")
    print(f"   地域:     {args.region}")
    if output_storage:
        print(f"   输出:     COS={output_storage['CosOutputStorage']['Bucket']} (region: {output_storage['CosOutputStorage']['Region']})")

    try:
        task_id = submit_quality_check(client, input_info, args.definition, output_storage)
    except TencentCloudSDKException as e:
        print(f"❌ 提交任务失败: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"✅ 任务已提交: {task_id}")

    if args.no_wait:
        print("ℹ️  异步模式，使用以下命令查询结果：")
        print(f"   python scripts/mps_quality_check.py --task-id {task_id}")
        return

    try:
        result = poll_task(client, task_id)
    except TencentCloudSDKException as e:
        print(f"❌ 查询任务失败: {e}", file=sys.stderr)
        sys.exit(1)

    if args.json_output:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("\n📋 质检结果：")
        print(format_result(result))


if __name__ == "__main__":
    main()