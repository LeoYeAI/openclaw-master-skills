#!/usr/bin/env python3
"""
腾讯云 MPS 大模型音视频理解脚本

功能：
  调用 MPS 大模型音视频理解能力（AiAnalysisTask + VideoComprehension），
  通过提示词控制理解侧重点，实现对视频/音频的内容分析、场景识别、摘要生成等。

  API 文档：https://cloud.tencent.com/document/product/862/126094
  接口说明：ProcessMedia — AiAnalysisTask.Definition=33，ExtendedParameter 传 mvc 参数

核心参数说明：
  --mode   : "video"（理解视频画面+音频）或 "audio"（仅音频，视频会自动提取音频）
  --prompt : 大模型提示词，决定理解侧重点和输出格式（必填，建议明确描述分析目标）
  --extend-url : 第二段音视频 URL，用于对比分析（最多支持 2 个文件）

用法：
  # 基础：视频内容理解
  python scripts/mps_av_understand.py \\
      --url https://example.com/video.mp4 \\
      --mode video \\
      --prompt "请分析这个视频的主要内容、场景和关键信息"

  # 音频模式（上传视频时自动提取音频）
  python scripts/mps_av_understand.py \\
      --url https://example.com/video.mp4 \\
      --mode audio \\
      --prompt "请对这段音频进行语音识别，输出完整文字内容"

  # 对比分析（两段音视频）
  python scripts/mps_av_understand.py \\
      --url https://example.com/video1.mp4 \\
      --extend-url https://example.com/video2.mp4 \\
      --mode audio \\
      --prompt "请对比这两段音频，分析演奏水平的差异"

  # 指定 COS 对象输入
  python scripts/mps_av_understand.py \\
      --cos-object input/video.mp4 \\
      --mode video \\
      --prompt "总结视频内容"

  # 异步模式（只提交任务，不等待）
  python scripts/mps_av_understand.py \\
      --url https://example.com/video.mp4 \\
      --mode video --prompt "分析视频内容" --no-wait

  # 查询已有任务结果
  python scripts/mps_av_understand.py --task-id 2600011633-WorkflowTask-xxxxx

  # JSON 格式输出
  python scripts/mps_av_understand.py \\
      --url https://example.com/video.mp4 \\
      --mode video --prompt "分析视频内容" --json

  # dry-run 模式（预览参数，不调用 API）
  python scripts/mps_av_understand.py \\
      --url https://example.com/video.mp4 \\
      --mode video --prompt "分析视频内容" --dry-run
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
DEFAULT_DEFINITION = 33   # 预设视频理解模板（官方推荐）
DEFAULT_MODE       = "video"
POLL_INTERVAL      = 10   # 轮询间隔（秒）
POLL_TIMEOUT       = 600  # 最大等待时间（秒）


# ─────────────────────────────────────────────
# SDK 客户端
# ─────────────────────────────────────────────

def get_client(region: str = DEFAULT_REGION):
    secret_id  = os.environ.get("TENCENTCLOUD_SECRET_ID", "")
    secret_key = os.environ.get("TENCENTCLOUD_SECRET_KEY", "")
    if not secret_id or not secret_key:
        print("错误: 请设置环境变量 TENCENTCLOUD_SECRET_ID 和 TENCENTCLOUD_SECRET_KEY",
              file=sys.stderr)
        sys.exit(1)
    cred = credential.Credential(secret_id, secret_key)
    return mps_client.MpsClient(cred, region)


# ─────────────────────────────────────────────
# 构建 ExtendedParameter
# ─────────────────────────────────────────────

def build_extended_parameter(
    mode: str,
    prompt: str,
    extend_urls: list = None,
) -> str:
    """
    构建 AiAnalysisTask.ExtendedParameter 的 JSON 字符串。

    结构：
      {"mvc": {"mode": "video|audio", "prompt": "...", "extendData": [{"url": "..."}]}}

    Args:
        mode        : "video" 或 "audio"
        prompt      : 大模型提示词
        extend_urls : 额外对比文件 URL 列表（最多 1 条，即总共 2 个文件）
    """
    mvc: dict = {
        "mode":   mode,
        "prompt": prompt,
    }
    if extend_urls:
        mvc["extendData"] = [{"url": u} for u in extend_urls[:1]]  # 最多 1 条扩展

    return json.dumps({"mvc": mvc}, ensure_ascii=False)


# ─────────────────────────────────────────────
# 创建任务
# ─────────────────────────────────────────────

def create_understand_task(
    client,
    url: str = None,
    cos_object: str = None,
    cos_input_bucket: str = None,
    cos_input_region: str = None,
    cos_input_key: str = None,
    definition: int = DEFAULT_DEFINITION,
    mode: str = DEFAULT_MODE,
    prompt: str = "",
    extend_urls: list = None,
    region: str = DEFAULT_REGION,
) -> str:
    """
    提交音视频理解任务，返回 TaskId。
    """
    req = models.ProcessMediaRequest()

    # ── 输入源 ──
    input_info = models.MediaInputInfo()
    if url:
        input_info.Type = "URL"
        url_input = models.UrlInputInfo()
        url_input.Url = url
        input_info.UrlInputInfo = url_input
    elif cos_input_key:
        # 新版 COS 路径输入（--cos-input-bucket + --cos-input-region + --cos-input-key）
        input_info.Type = "COS"
        cos_input = models.CosInputInfo()
        bucket = cos_input_bucket or os.environ.get("TENCENTCLOUD_COS_BUCKET", "")
        cos_region = cos_input_region or os.environ.get("TENCENTCLOUD_COS_REGION", region)
        if not bucket:
            print("错误: 使用 COS 输入时请指定 --cos-input-bucket 或设置 TENCENTCLOUD_COS_BUCKET 环境变量", file=sys.stderr)
            sys.exit(1)
        cos_input.Bucket = bucket
        cos_input.Region = cos_region
        # 确保 key 以 / 开头
        cos_input.Object = cos_input_key if cos_input_key.startswith("/") else f"/{cos_input_key}"
        input_info.CosInputInfo = cos_input
    elif cos_object:
        # 旧版 COS 对象路径（已废弃，保持兼容）
        input_info.Type = "COS"
        cos_input  = models.CosInputInfo()
        bucket     = os.environ.get("TENCENTCLOUD_COS_BUCKET", "")
        cos_region = os.environ.get("TENCENTCLOUD_COS_REGION", region)
        if not bucket:
            print("错误: 使用 COS 输入时请设置 TENCENTCLOUD_COS_BUCKET", file=sys.stderr)
            sys.exit(1)
        cos_input.Bucket = bucket
        cos_input.Region = cos_region
        cos_input.Object = cos_object
        input_info.CosInputInfo = cos_input
    else:
        print("错误: 请提供 --url 或 --cos-input-key 或 --cos-object", file=sys.stderr)
        sys.exit(1)

    req.InputInfo = input_info

    # ── AiAnalysisTask ──
    ai_task = models.AiAnalysisTaskInput()
    ai_task.Definition = definition
    if prompt:  # 有 prompt 才构建 ExtendedParameter
        ai_task.ExtendedParameter = build_extended_parameter(
            mode=mode,
            prompt=prompt,
            extend_urls=extend_urls,
        )
    req.AiAnalysisTask = ai_task

    resp = client.ProcessMedia(req)
    return resp.TaskId


# ─────────────────────────────────────────────
# 查询任务
# ─────────────────────────────────────────────

def query_task(client, task_id: str) -> dict:
    req = models.DescribeTaskDetailRequest()
    req.TaskId = task_id
    resp = client.DescribeTaskDetail(req)
    return json.loads(resp.to_json_string())


def poll_task(client, task_id: str, timeout: int = POLL_TIMEOUT) -> dict:
    start = time.time()
    print(f"⏳ 等待任务完成: {task_id}")
    while True:
        result = query_task(client, task_id)
        status = result.get("Status", "")
        if status in ("FINISH", "FAIL"):
            elapsed = int(time.time() - start)
            print(f"{'✅' if status == 'FINISH' else '❌'} 任务{status}，耗时 {elapsed}s")
            return result
        if time.time() - start > timeout:
            print(f"⚠️  超时（{timeout}s），任务仍在处理", file=sys.stderr)
            return result
        elapsed = int(time.time() - start)
        print(f"   [{elapsed}s] 状态: {status}，继续等待...")
        time.sleep(POLL_INTERVAL)


# ─────────────────────────────────────────────
# 结果解析
# ─────────────────────────────────────────────

def extract_result(task_detail: dict) -> dict:
    """从 WorkflowTask.AiAnalysisResultSet 中提取 VideoComprehension 结果"""
    out = {
        "task_id":     task_detail.get("TaskId", ""),
        "status":      task_detail.get("Status", ""),
        "create_time": task_detail.get("CreateTime", ""),
        "finish_time": task_detail.get("FinishTime", ""),
        "comprehension": None,
        "error": None,
    }

    wf = task_detail.get("WorkflowTask", {}) or {}
    for item in wf.get("AiAnalysisResultSet", []):
        if item.get("Type") == "VideoComprehension":
            vc = item.get("VideoComprehensionTask", {}) or {}
            if vc.get("ErrCode", 0) != 0:
                out["error"] = {"code": vc["ErrCode"], "message": vc.get("Message", "")}
            else:
                task_out = vc.get("Output", {}) or {}
                out["comprehension"] = {
                    "result":      task_out.get("VideoComprehensionAnalysisResult", ""),
                    "progress":    vc.get("Progress", 0),
                    "begin_time":  vc.get("BeginProcessTime", ""),
                    "finish_time": vc.get("FinishTime", ""),
                }
            break
    return out


def print_result(result: dict, as_json: bool = False, output_dir: str = None):
    if as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        sep = "=" * 60
        print(f"\n{sep}")
        print(f"任务 ID : {result['task_id']}")
        print(f"状态    : {result['status']}")
        print(f"完成时间: {result.get('finish_time', '-')}")
        if result.get("error"):
            err = result["error"]
            print(f"\n❌ 错误: [{err['code']}] {err['message']}")
        elif result.get("comprehension"):
            comp = result["comprehension"]
            print(f"\n✅ 理解结果（进度: {comp['progress']}%）")
            print("─" * 60)
            print(comp["result"])
        else:
            print("\n⚠️  暂无结果（任务可能仍在处理中）")
        print(f"{sep}\n")

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        fname = f"av_understand_{result['task_id'].replace('/', '_')}.json"
        fpath = os.path.join(output_dir, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"结果已保存: {fpath}")


# ─────────────────────────────────────────────
# CLI 入口
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="腾讯云 MPS 大模型音视频理解",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # 输入源（三选一）
    input_grp = parser.add_mutually_exclusive_group()
    input_grp.add_argument("--url",        help="音视频 URL（HTTP/HTTPS）")
    input_grp.add_argument("--cos-object", help="COS 对象路径（如 input/video.mp4，已废弃，请使用 --cos-input-key）")
    input_grp.add_argument("--task-id",    help="直接查询已有任务结果（跳过创建）")
    
    # COS 路径输入（新版，与 mps_transcode.py 等保持一致）
    parser.add_argument("--cos-input-bucket", help="输入文件所在 COS Bucket 名称")
    parser.add_argument("--cos-input-region", help="输入文件所在 COS Region（如 ap-guangzhou）")
    parser.add_argument("--cos-input-key",    help="输入文件的 COS Key（如 /input/video.mp4）")

    # 核心理解参数
    parser.add_argument(
        "--mode", choices=["video", "audio"], default=DEFAULT_MODE,
        help=(
            "理解模式（默认 video）：\n"
            "  video — 理解视频画面内容\n"
            "  audio — 仅处理音频（上传视频时自动提取音频）"
        ),
    )
    parser.add_argument(
        "--prompt", default="",
        help="大模型提示词（强烈建议填写，控制理解侧重点和输出格式）",
    )
    parser.add_argument(
        "--extend-url", metavar="URL", action="append", dest="extend_urls",
        help="第二段对比音视频 URL（可与主输入做对比分析，最多 1 条）",
    )

    # 任务参数
    parser.add_argument(
        "--definition", type=int, default=DEFAULT_DEFINITION,
        help=f"AiAnalysisTask 模板 ID（默认 {DEFAULT_DEFINITION}，即预设视频理解模板）",
    )
    parser.add_argument("--region", default=DEFAULT_REGION,
                        help=f"地域（默认 {DEFAULT_REGION}）")

    # 输出控制
    parser.add_argument("--no-wait",    action="store_true", help="异步模式：只提交任务，不等待结果")
    parser.add_argument("--json",       action="store_true", dest="json_output", help="JSON 格式输出")
    parser.add_argument("--output-dir", help="将结果 JSON 保存到指定目录")
    parser.add_argument("--dry-run",    action="store_true", help="只打印参数预览，不调用 API")
    parser.add_argument("-v", "--verbose", action="store_true", help="显示详细日志信息")

    args = parser.parse_args()

    # ── dry-run ──
    if args.dry_run:
        print("🔍 dry-run 参数预览:")
        if args.task_id:
            print(f"  task-id    = {args.task_id}")
        else:
            if args.url:
                print(f"  输入       = URL={args.url}")
            elif args.cos_input_key:
                bucket = args.cos_input_bucket or os.environ.get("TENCENTCLOUD_COS_BUCKET", "")
                region = args.cos_input_region or os.environ.get("TENCENTCLOUD_COS_REGION", args.region)
                print(f"  输入       = COS={bucket}/{region}{args.cos_input_key}")
            elif args.cos_object:
                print(f"  输入       = COS={args.cos_object} (旧版)")
            print(f"  mode       = {args.mode}")
            print(f"  prompt     = {args.prompt!r}")
            print(f"  extend-url = {args.extend_urls}")
            print(f"  definition = {args.definition}")
            print(f"  region     = {args.region}")
            print(f"  no-wait    = {args.no_wait}")
            print(f"  verbose    = {args.verbose}")
        if args.prompt:
            ep = build_extended_parameter(args.mode, args.prompt, args.extend_urls)
            print(f"\n  ExtendedParameter =\n  {ep}")
        return

    client = get_client(args.region)

    # ── 查询模式 ──
    if args.task_id:
        print(f"🔍 查询任务: {args.task_id}")
        if args.verbose:
            print(f"   客户端区域: {args.region}")
        detail = query_task(client, args.task_id)
        result = extract_result(detail)
        print_result(result, as_json=args.json_output, output_dir=args.output_dir)
        return

    # ── 提交任务 ──
    has_input = bool(args.url) or bool(args.cos_input_key) or bool(args.cos_object)
    if not has_input:
        parser.error("请提供 --url、--cos-input-key、--cos-object 或 --task-id 之一")

    # 确定输入源显示
    if args.url:
        src = f"URL={args.url}"
    elif args.cos_input_key:
        bucket = args.cos_input_bucket or os.environ.get("TENCENTCLOUD_COS_BUCKET", "")
        region = args.cos_input_region or os.environ.get("TENCENTCLOUD_COS_REGION", args.region)
        src = f"COS={bucket}/{region}{args.cos_input_key}"
    else:
        src = f"COS={args.cos_object} (旧版)"
    
    print(f"🚀 提交音视频理解任务")
    print(f"   输入     : {src}")
    print(f"   mode     : {args.mode}")
    print(f"   prompt   : {args.prompt[:80]!r}{'...' if len(args.prompt) > 80 else ''}")
    if args.extend_urls:
        print(f"   对比文件 : {args.extend_urls}")
    print(f"   definition: {args.definition}  region: {args.region}")
    
    if args.verbose:
        print(f"\n📋 详细参数:")
        print(f"   bucket   : {args.cos_input_bucket or os.environ.get('TENCENTCLOUD_COS_BUCKET', 'N/A')}")
        print(f"   cos_region: {args.cos_input_region or os.environ.get('TENCENTCLOUD_COS_REGION', args.region)}")
        if args.cos_input_key:
            print(f"   cos_key  : {args.cos_input_key}")
        elif args.cos_object:
            print(f"   cos_object: {args.cos_object}")
        ep = build_extended_parameter(args.mode, args.prompt, args.extend_urls)
        print(f"   extended_param: {ep}")

    try:
        task_id = create_understand_task(
            client,
            url=args.url,
            cos_object=args.cos_object,
            cos_input_bucket=args.cos_input_bucket,
            cos_input_region=args.cos_input_region,
            cos_input_key=args.cos_input_key,
            definition=args.definition,
            mode=args.mode,
            prompt=args.prompt,
            extend_urls=args.extend_urls,
            region=args.region,
        )
        print(f"✅ 任务已提交，TaskId: {task_id}")
        if args.verbose:
            print(f"   轮询间隔: {POLL_INTERVAL}秒  最大等待: {POLL_TIMEOUT}秒")
    except TencentCloudSDKException as e:
        print(f"❌ 提交失败: {e}", file=sys.stderr)
        sys.exit(1)

    # ── 异步模式 ──
    if args.no_wait:
        result = {
            "task_id": task_id,
            "status":  "PROCESSING",
            "message": "任务已提交，使用 --task-id 查询结果",
        }
        print_result(result, as_json=args.json_output, output_dir=args.output_dir)
        return

    # ── 同步等待 ──
    try:
        if args.verbose:
            print(f"\n⏳ 开始轮询任务状态...")
        detail = poll_task(client, task_id)
        if args.verbose:
            print(f"✅ 任务完成")
        result = extract_result(detail)
        print_result(result, as_json=args.json_output, output_dir=args.output_dir)
        if result.get("status") == "FAIL":
            sys.exit(1)
    except TencentCloudSDKException as e:
        print(f"❌ 查询失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
