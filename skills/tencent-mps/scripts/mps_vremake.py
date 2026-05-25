#!/usr/bin/env python3
"""
腾讯云 MPS 视频去重脚本

功能：
  调用 MPS VideoRemake 能力，对视频进行去重处理，避免因重复内容被平台限流。
  通过 ExtendedParameter 的 vremake 参数控制去重模式。

  API 文档：https://cloud.tencent.com/document/product/862/124394
  接口：ProcessMedia → AiAnalysisTask.Definition=29（视频去重模板）

支持的去重模式（--mode）：
  PicInPic         画中画：将视频以画中画形式嵌入新背景
  BackgroundExtend 视频扩展：扩展视频画面边界
  VerticalExtend   垂直填充：在视频上下方向添加填充内容
  HorizontalExtend 水平填充：在视频左右方向添加填充内容
  AB               视频交错：AB 视频交错模式
  SwapFace         换脸：视频人脸替换（需提供 --src-faces 和 --dst-faces）
  SwapCharacter    换人：视频人物替换（需提供 --src-character 和 --dst-character）

用法：
  # URL 输入 + 画中画去重（等待结果）
  python scripts/mps_vremake.py \\
      --url https://example.com/video.mp4 \\
      --mode PicInPic \\
      --wait

  # COS 对象输入 + 视频扩展
  python scripts/mps_vremake.py \\
      --cos-object input/video.mp4 \\
      --mode BackgroundExtend \\
      --wait

  # 换脸模式
  python scripts/mps_vremake.py \\
      --url https://example.com/video.mp4 \\
      --mode SwapFace \\
      --src-faces https://example.com/src.png \\
      --dst-faces https://example.com/dst.png \\
      --wait

  # 换人模式
  python scripts/mps_vremake.py \\
      --url https://example.com/video.mp4 \\
      --mode SwapCharacter \\
      --src-character https://example.com/src_person.png \\
      --dst-character https://example.com/dst_person.png \\
      --wait

  # 画中画 + 自定义 LLM 提示词
  python scripts/mps_vremake.py \\
      --url https://example.com/video.mp4 \\
      --mode PicInPic \\
      --llm-prompt "生成一个唯美的自然风景背景图片" \\
      --wait

  # 异步提交（不等待）
  python scripts/mps_vremake.py \\
      --url https://example.com/video.mp4 \\
      --mode PicInPic

  # 查询已有任务结果
  python scripts/mps_vremake.py --task-id 2600011633-WorkflowTask-xxxxx

  # JSON 格式输出
  python scripts/mps_vremake.py \\
      --url https://example.com/video.mp4 \\
      --mode PicInPic --wait --json

  # dry-run 预览（含 ExtendedParameter）
  python scripts/mps_vremake.py \\
      --url https://example.com/video.mp4 \\
      --mode BackgroundExtend --dry-run
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

try:
    from qcloud_cos import CosConfig, CosS3Client
    _COS_SDK_AVAILABLE = True
except ImportError:
    _COS_SDK_AVAILABLE = False

# ─────────────────────────────────────────────
# 配置
# ─────────────────────────────────────────────
DEFAULT_REGION     = "ap-guangzhou"
DEFAULT_DEFINITION = 29    # 视频去重模板 ID（官方）
POLL_INTERVAL      = 15    # 轮询间隔（秒）
POLL_TIMEOUT       = 3600  # 最大等待时间（秒）

VALID_MODES = [
    "PicInPic", "BackgroundExtend", "VerticalExtend",
    "HorizontalExtend", "AB", "SwapFace", "SwapCharacter",
]

MODE_CN = {
    "PicInPic":         "画中画",
    "BackgroundExtend": "视频扩展",
    "VerticalExtend":   "垂直填充",
    "HorizontalExtend": "水平填充",
    "AB":               "视频交错",
    "SwapFace":         "换脸",
    "SwapCharacter":    "换人",
}


# ─────────────────────────────────────────────
# SDK 客户端
# ─────────────────────────────────────────────

def get_client(region: str = DEFAULT_REGION):
    secret_id  = os.environ.get("TENCENTCLOUD_SECRET_ID", "")
    secret_key = os.environ.get("TENCENTCLOUD_SECRET_KEY", "")
    if not secret_id or not secret_key:
        print("错误: 请设置 TENCENTCLOUD_SECRET_ID 和 TENCENTCLOUD_SECRET_KEY", file=sys.stderr)
        sys.exit(1)
    return mps_client.MpsClient(credential.Credential(secret_id, secret_key), region)


# ─────────────────────────────────────────────
# 构建 ExtendedParameter
# ─────────────────────────────────────────────

def build_extended_parameter(args) -> str:
    """
    构建 AiAnalysisTask.ExtendedParameter 的 JSON 字符串。

    结构示例：
      {"vremake": {"mode": "PicInPic", "picInPic": {"llmPrompt": "..."}}}
    """
    mode = args.mode
    vremake: dict = {"mode": mode}

    if mode == "PicInPic":
        pic_params: dict = {}
        if args.llm_video_prompt:
            pic_params["llmVideoPrompt"] = args.llm_video_prompt
        elif args.llm_prompt:
            pic_params["llmPrompt"] = args.llm_prompt
        if args.random_move:
            pic_params["randomMove"] = True
        if pic_params:
            vremake["picInPic"] = pic_params

    elif mode == "BackgroundExtend":
        bg_params: dict = {}
        if args.min_scene_secs is not None:
            bg_params["minSceneSecs"] = args.min_scene_secs
        if bg_params:
            vremake["backgroundExtend"] = bg_params

    elif mode in ("VerticalExtend", "HorizontalExtend", "AB"):
        ext_params: dict = {}
        if args.llm_video_prompt:
            ext_params["llmVideoPrompt"] = args.llm_video_prompt
        elif args.llm_prompt and mode == "AB":
            ext_params["llmPrompt"] = args.llm_prompt
        if args.random_flip is not None:
            ext_params["randomFlip"] = args.random_flip
        if args.random_cut:
            ext_params["randomCut"] = True
        if args.random_speed:
            ext_params["randomSpeed"] = True
        if args.ext_mode is not None:
            ext_params["extMode"] = args.ext_mode
        if args.append_image:
            ext_params["appendImage"] = True
        if args.append_image_prompt:
            ext_params["appendImagePrompt"] = args.append_image_prompt
        key_map = {
            "VerticalExtend":   "verticalExtend",
            "HorizontalExtend": "horizontalExtend",
            "AB":               "AB",
        }
        if ext_params:
            vremake[key_map[mode]] = ext_params

    elif mode == "SwapFace":
        if not args.src_faces or not args.dst_faces:
            print("错误: SwapFace 模式需要提供 --src-faces 和 --dst-faces", file=sys.stderr)
            sys.exit(1)
        if len(args.src_faces) != len(args.dst_faces):
            print("错误: --src-faces 和 --dst-faces 数量必须一致", file=sys.stderr)
            sys.exit(1)
        vremake["swapFace"] = {
            "srcFaces": args.src_faces,
            "dstFaces": args.dst_faces,
        }

    elif mode == "SwapCharacter":
        if not args.src_character or not args.dst_character:
            print("错误: SwapCharacter 模式需要提供 --src-character 和 --dst-character", file=sys.stderr)
            sys.exit(1)
        vremake["swapCharacter"] = {
            "srcCharacter": args.src_character,
            "character":    args.dst_character,
        }

    # 支持 --custom-json 合并
    if args.custom_json:
        try:
            custom = json.loads(args.custom_json)
            # 若 custom 包含 vremake 字段，深度合并
            if "vremake" in custom:
                for k, v in custom["vremake"].items():
                    if k != "mode":
                        vremake[k] = v
            else:
                # 直接合并到 vremake
                vremake.update(custom)
        except json.JSONDecodeError as e:
            print(f"错误: --custom-json 格式错误: {e}", file=sys.stderr)
            sys.exit(1)

    return json.dumps({"vremake": vremake}, ensure_ascii=False)


# ─────────────────────────────────────────────
# 创建任务
# ─────────────────────────────────────────────

def create_task(client, args) -> str:
    """提交视频去重任务，返回 TaskId。"""
    req = models.ProcessMediaRequest()

    # 输入源
    input_info = models.MediaInputInfo()
    if args.url:
        input_info.Type = "URL"
        url_input = models.UrlInputInfo()
        url_input.Url = args.url
        input_info.UrlInputInfo = url_input
    elif args.cos_input_key:
        # 新版 COS 路径输入（--cos-input-bucket + --cos-input-region + --cos-input-key）
        input_info.Type = "COS"
        cos_input = models.CosInputInfo()
        bucket = args.cos_input_bucket or os.environ.get("TENCENTCLOUD_COS_BUCKET", "")
        cos_region = args.cos_input_region or os.environ.get("TENCENTCLOUD_COS_REGION", args.region)
        if not bucket:
            print("错误: 使用 COS 输入时请指定 --cos-input-bucket 或设置 TENCENTCLOUD_COS_BUCKET 环境变量", file=sys.stderr)
            sys.exit(1)
        cos_input.Bucket = bucket
        cos_input.Region = cos_region
        # 确保 key 以 / 开头
        cos_input.Object = args.cos_input_key if args.cos_input_key.startswith("/") else f"/{args.cos_input_key}"
        input_info.CosInputInfo = cos_input
    elif args.cos_object:
        # 旧版 COS 对象路径（已废弃，保持兼容）
        input_info.Type = "COS"
        cos_input  = models.CosInputInfo()
        bucket     = os.environ.get("TENCENTCLOUD_COS_BUCKET", "")
        cos_region = os.environ.get("TENCENTCLOUD_COS_REGION", args.region)
        if not bucket:
            print("错误: 使用 COS 输入时请设置 TENCENTCLOUD_COS_BUCKET", file=sys.stderr)
            sys.exit(1)
        cos_input.Bucket = bucket
        cos_input.Region = cos_region
        cos_input.Object = args.cos_object
        input_info.CosInputInfo = cos_input
    else:
        print("错误: 请提供 --url、--cos-input-key 或 --cos-object", file=sys.stderr)
        sys.exit(1)

    req.InputInfo = input_info

    # AiAnalysisTask
    ai_task = models.AiAnalysisTaskInput()
    ai_task.Definition = args.definition
    ai_task.ExtendedParameter = build_extended_parameter(args)
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
            icon = "✅" if status == "FINISH" else "❌"
            print(f"{icon} 任务{status}，耗时 {elapsed}s")
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
    """从 WorkflowTask.AiAnalysisResultSet 中提取 VideoRemake 结果"""
    out = {
        "task_id":     task_detail.get("TaskId", ""),
        "status":      task_detail.get("Status", ""),
        "create_time": task_detail.get("CreateTime", ""),
        "finish_time": task_detail.get("FinishTime", ""),
        "remake":      None,
        "error":       None,
    }

    wf = task_detail.get("WorkflowTask", {}) or {}
    for item in wf.get("AiAnalysisResultSet", []):
        if item.get("Type") == "VideoRemake":
            vr = item.get("VideoRemakeTask", {}) or {}
            if vr.get("ErrCode", 0) != 0:
                out["error"] = {"code": vr["ErrCode"], "message": vr.get("Message", "")}
            else:
                task_out = vr.get("Output", {}) or {}
                out["remake"] = {
                    "output_object_path": task_out.get("OutputObjectPath", ""),
                    "output_storage":     task_out.get("OutputStorage", {}),
                    "progress":           vr.get("Progress", 0),
                    "begin_time":         vr.get("BeginProcessTime", ""),
                    "finish_time":        vr.get("FinishTime", ""),
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
        elif result.get("remake"):
            r = result["remake"]
            print(f"\n✅ 去重完成（进度: {r['progress']}%）")
            if r.get("output_object_path"):
                out_path = r["output_object_path"]
                print(f"   输出路径: {out_path}")
                # 尝试生成预签名下载链接
                out_storage = r.get("output_storage") or {}
                out_type = out_storage.get("Type", "")
                if out_type == "COS" and _COS_SDK_AVAILABLE:
                    cos_out = out_storage.get("CosOutputStorage", {}) or {}
                    bucket = cos_out.get("Bucket", "")
                    region = cos_out.get("Region", "")
                    if bucket and region:
                        try:
                            secret_id = os.environ.get("TENCENTCLOUD_SECRET_ID", "")
                            secret_key = os.environ.get("TENCENTCLOUD_SECRET_KEY", "")
                            cos_config = CosConfig(Region=region, SecretId=secret_id, SecretKey=secret_key)
                            cos_client = CosS3Client(cos_config)
                            signed_url = cos_client.get_presigned_url(
                                Bucket=bucket,
                                Key=out_path.lstrip("/"),
                                Method="GET",
                                Expired=3600
                            )
                            print(f"   🔗 下载链接（预签名，1小时有效）: {signed_url}")
                        except Exception as e:
                            print(f"   ⚠️  生成预签名 URL 失败: {e}")
        else:
            print("\n⚠️  暂无结果（任务可能仍在处理中）")
        print(f"{sep}\n")

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        fname = f"vremake_{result['task_id'].replace('/', '_')}.json"
        fpath = os.path.join(output_dir, fname)
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"结果已保存: {fpath}")   


# ─────────────────────────────────────────────
# CLI 入口
# ─────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="腾讯云 MPS 视频去重（VideoRemake）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    # 输入源（三选一）
    input_grp = parser.add_mutually_exclusive_group()
    input_grp.add_argument("--url",        help="视频 URL（HTTP/HTTPS）")
    input_grp.add_argument("--cos-object", help="COS 对象路径（如 input/video.mp4，已废弃，请使用 --cos-input-key）")
    input_grp.add_argument("--task-id",    help="直接查询已有任务结果（跳过创建）")
    
    # COS 路径输入（新版，与 mps_transcode.py 等保持一致）
    parser.add_argument("--cos-input-bucket", help="输入文件所在 COS Bucket 名称")
    parser.add_argument("--cos-input-region", help="输入文件所在 COS Region（如 ap-guangzhou）")
    parser.add_argument("--cos-input-key",    help="输入文件的 COS Key（如 /input/video.mp4）")

    # 去重模式
    parser.add_argument(
        "--mode", choices=VALID_MODES,
        help="去重模式（提交任务时必填）：" + " / ".join(f"{m}({MODE_CN[m]})" for m in VALID_MODES),
    )

    # 换脸/换人参数
    parser.add_argument("--src-faces",      nargs="+", metavar="URL", help="[SwapFace] 原视频中人脸 URL 列表")
    parser.add_argument("--dst-faces",      nargs="+", metavar="URL", help="[SwapFace] 目标人脸 URL 列表（与 --src-faces 一一对应）")
    parser.add_argument("--src-character",  metavar="URL", help="[SwapCharacter] 原视频人物 URL（正面全身图）")
    parser.add_argument("--dst-character",  metavar="URL", help="[SwapCharacter] 目标人物 URL（正面全身图）")

    # 通用扩展参数
    parser.add_argument("--llm-prompt",       metavar="TEXT", help="大模型提示词（生成背景图片）")
    parser.add_argument("--llm-video-prompt", metavar="TEXT", help="大模型提示词（生成背景视频，优先于 --llm-prompt）")
    parser.add_argument("--min-scene-secs",   type=float, help="[BackgroundExtend] 插入扩展画面的最小间隔（秒，默认2.0）")
    parser.add_argument("--random-move",      action="store_true", help="[PicInPic] 随机移动画中画")
    parser.add_argument("--random-cut",       action="store_true", help="随机裁剪")
    parser.add_argument("--random-speed",     action="store_true", help="随机加速")
    parser.add_argument("--random-flip",      type=lambda x: x.lower() != "false",
                        metavar="true/false", help="随机镜像（默认 true）")
    parser.add_argument("--append-image",     action="store_true", help="在视频开头/结尾插入图片")
    parser.add_argument("--append-image-prompt", metavar="TEXT", help="开头/结尾图片生成提示词")
    parser.add_argument("--ext-mode",         type=int, choices=[1, 2, 3], help="扩展模式 1/2/3（HorizontalExtend/AB）")
    parser.add_argument("--custom-json",      metavar="JSON", help="自定义 vremake 扩展参数 JSON（与 --mode 合并）")

    # 任务参数
    parser.add_argument("--definition", type=int, default=DEFAULT_DEFINITION,
                        help=f"AiAnalysisTask 模板 ID（默认 {DEFAULT_DEFINITION}，即视频去重模板）")
    parser.add_argument("--region", default=DEFAULT_REGION,
                        help=f"地域（默认 {DEFAULT_REGION}）")

    # 输出控制
    parser.add_argument("--wait",       action="store_true", help="等待任务完成（默认异步，只提交）")
    parser.add_argument("--json",       action="store_true", dest="json_output", help="JSON 格式输出")
    parser.add_argument("--output-dir", help="将结果 JSON 保存到指定目录")
    parser.add_argument("--dry-run",    action="store_true", help="只打印参数预览（含 ExtendedParameter），不调用 API")

    args = parser.parse_args()

    # ── dry-run ──
    if args.dry_run:
        print("🔍 dry-run 参数预览:")
        if args.task_id:
            print(f"  task-id    = {args.task_id}")
        else:
            if args.url:
                src = f"URL={args.url}"
            elif args.cos_input_key:
                bucket = args.cos_input_bucket or os.environ.get("TENCENTCLOUD_COS_BUCKET", "")
                region = args.cos_input_region or os.environ.get("TENCENTCLOUD_COS_REGION", args.region)
                src = f"COS={bucket}/{region}{args.cos_input_key}"
            else:
                src = f"COS={args.cos_object} (旧版)"
            print(f"  输入       = {src}")
            print(f"  mode       = {args.mode}（{MODE_CN.get(args.mode, '?')}）")
            print(f"  definition = {args.definition}")
            print(f"  region     = {args.region}")
            print(f"  wait       = {args.wait}")
        if args.mode and (args.url or args.cos_object or args.cos_input_key):
            ep = build_extended_parameter(args)
            print(f"\n  ExtendedParameter =\n  {ep}")
        return

    client = get_client(args.region)

    # ── 查询模式 ──
    if args.task_id:
        print(f"🔍 查询任务: {args.task_id}")
        detail = query_task(client, args.task_id)
        result = extract_result(detail)
        print_result(result, as_json=args.json_output, output_dir=args.output_dir)
        return

    # ── 提交任务 ──
    has_input = bool(args.url) or bool(args.cos_object) or bool(args.cos_input_key)
    if not has_input:
        parser.error("请提供 --url、--cos-input-key、--cos-object 或 --task-id 之一")
    if not args.mode:
        parser.error("提交任务时 --mode 为必填参数")

    # 确定输入源显示
    if args.url:
        src = f"URL={args.url}"
    elif args.cos_input_key:
        bucket = args.cos_input_bucket or os.environ.get("TENCENTCLOUD_COS_BUCKET", "")
        region = args.cos_input_region or os.environ.get("TENCENTCLOUD_COS_REGION", args.region)
        src = f"COS={bucket}/{region}{args.cos_input_key}"
    else:
        src = f"COS={args.cos_object} (旧版)"
    
    mode_cn = MODE_CN.get(args.mode, args.mode)
    print(f"🚀 提交视频去重任务")
    print(f"   输入  : {src}")
    print(f"   模式  : {args.mode}（{mode_cn}）")
    print(f"   模板  : {args.definition}  地域: {args.region}")

    try:
        task_id = create_task(client, args)
        print(f"✅ 任务已提交，TaskId: {task_id}")
    except TencentCloudSDKException as e:
        print(f"❌ 提交失败: {e}", file=sys.stderr)
        sys.exit(1)

    # ── 异步模式（默认） ──
    if not args.wait:
        result = {
            "task_id": task_id,
            "status":  "PROCESSING",
            "message": "任务已提交，使用 --task-id 查询结果，或重新提交时加 --wait 等待完成",
        }
        print_result(result, as_json=args.json_output, output_dir=args.output_dir)
        return

    # ── 等待完成 ──
    try:
        detail = poll_task(client, task_id)
        result = extract_result(detail)
        print_result(result, as_json=args.json_output, output_dir=args.output_dir)
        if result.get("status") == "FAIL":
            sys.exit(1)
    except TencentCloudSDKException as e:
        print(f"❌ 查询失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
