#!/usr/bin/env python3
"""
腾讯云 MPS 极速高清转码脚本

功能：
  使用 MPS 极速高清转码功能，在保证一定画质的基础上最大限度压缩码率、压缩文件大小，
  极大节约带宽和存储成本！

  默认使用 100305 预设模板（极速高清-H265-MP4-1080P）。
  如果用户提出一些参数要求（分辨率、码率等），会基于 100305 预设模板的参数修改。

COS 存储约定：
  通过环境变量 TENCENTCLOUD_COS_BUCKET 指定 COS Bucket 名称。
  - 输入文件默认路径：{TENCENTCLOUD_COS_BUCKET}/input/   （即 COS Object 以 /input/ 开头）
  - 输出文件默认路径：{TENCENTCLOUD_COS_BUCKET}/output/transcode/  （即输出目录为 /output/transcode/）

  当使用 COS 输入时，如果未显式指定 --cos-bucket，自动使用 TENCENTCLOUD_COS_BUCKET。
  当未显式指定 --output-bucket，自动使用 TENCENTCLOUD_COS_BUCKET 作为输出 Bucket。
  当未显式指定 --output-dir，自动使用 /output/transcode/ 作为输出目录。

用法：
  # 最简用法：使用 URL 输入 + 默认模板（输出到 TENCENTCLOUD_COS_BUCKET/output/transcode/）
  python mps_transcode.py --url https://example.com/video.mp4

  # COS 输入（自动使用 TENCENTCLOUD_COS_BUCKET，对象路径在 /input/ 下）
  python mps_transcode.py --cos-object /input/video/test.mp4

  # COS 输入 + 显式指定 bucket（覆盖环境变量）
  python mps_transcode.py --cos-bucket mybucket-125xxx --cos-region ap-guangzhou --cos-object /input/video/test.mp4

  # 自定义输出 COS 位置（覆盖默认的 /output/transcode/ 目录）
  python mps_transcode.py --url https://example.com/video.mp4 \\
      --output-bucket mybucket-125xxx --output-region ap-guangzhou --output-dir /custom_output/

  # 自定义分辨率（宽1920，高度自适应）
  python mps_transcode.py --url https://example.com/video.mp4 --width 1920

  # 自定义分辨率（720P）
  python mps_transcode.py --url https://example.com/video.mp4 --width 1280 --height 720

  # 自定义码率上限（单位 kbps）
  python mps_transcode.py --url https://example.com/video.mp4 --bitrate 2000

  # 自定义编码格式
  python mps_transcode.py --url https://example.com/video.mp4 --codec h264

  # 自定义封装格式
  python mps_transcode.py --url https://example.com/video.mp4 --container hls

  # 自定义帧率
  python mps_transcode.py --url https://example.com/video.mp4 --fps 30

  # 使用自定义参数覆盖（完全自定义模式，不使用预设模板）
  python mps_transcode.py --url https://example.com/video.mp4 \\
      --codec h265 --width 1920 --height 1080 --bitrate 3000 --fps 30 --container mp4

  # 极致压缩模式
  python mps_transcode.py --url https://example.com/video.mp4 --compress-type ultra_compress

  # 画质优先模式
  python mps_transcode.py --url https://example.com/video.mp4 --compress-type low_compress

  # 指定场景化转码（如 UGC 短视频）
  python mps_transcode.py --url https://example.com/video.mp4 --scene-type ugc

  # 设置回调 URL
  python mps_transcode.py --url https://example.com/video.mp4 --notify-url https://example.com/callback

环境变量：
  TENCENTCLOUD_SECRET_ID   - 腾讯云 SecretId
  TENCENTCLOUD_SECRET_KEY  - 腾讯云 SecretKey
  TENCENTCLOUD_COS_BUCKET       - COS Bucket 名称（如 mybucket-125xxx，默认 test_bucket）
  TENCENTCLOUD_COS_REGION       - COS Bucket 区域（默认 ap-guangzhou）
"""

import argparse
import json
import os
import sys

# 轮询模块（同目录）
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _SCRIPT_DIR)
try:
    from load_env import ensure_env_loaded as _ensure_env_loaded
    _LOAD_ENV_AVAILABLE = True
except ImportError:
    _LOAD_ENV_AVAILABLE = False
try:
    from poll_task import poll_video_task
    _POLL_AVAILABLE = True
except ImportError:
    _POLL_AVAILABLE = False

try:
    from tencentcloud.common import credential
    from tencentcloud.common.profile.client_profile import ClientProfile
    from tencentcloud.common.profile.http_profile import HttpProfile
    from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
    from tencentcloud.mps.v20190612 import mps_client, models
except ImportError:
    print("错误：请先安装腾讯云 SDK：pip install tencentcloud-sdk-python", file=sys.stderr)
    sys.exit(1)


# =============================================================================
# 预设模板 100305 的默认参数（极速高清-H265-MP4-1080P）
# =============================================================================
PRESET_TEMPLATE_ID = 100305
PRESET_DEFAULTS = {
    "container": "mp4",
    "codec": "h265",
    "width": 1920,
    "height": 0,          # 0 表示按比例缩放
    "bitrate": 0,         # 0 表示与原始保持一致，由极速高清自动优化
    "fps": 0,             # 0 表示与原始保持一致
    "audio_codec": "aac",
    "audio_bitrate": 128,
    "audio_sample_rate": 44100,
}


def get_cos_bucket():
    """从环境变量获取 COS Bucket 名称。"""
    return os.environ.get("TENCENTCLOUD_COS_BUCKET", "")


def get_cos_region():
    """从环境变量获取 COS Bucket 区域，默认 ap-guangzhou。"""
    return os.environ.get("TENCENTCLOUD_COS_REGION", "ap-guangzhou")


def get_credentials():
    """从环境变量获取腾讯云凭证。若缺失则尝试从系统文件自动加载后重试。"""
    secret_id = os.environ.get("TENCENTCLOUD_SECRET_ID", "")
    secret_key = os.environ.get("TENCENTCLOUD_SECRET_KEY", "")
    if not secret_id or not secret_key:
        # 尝试从系统环境变量文件自动加载
        if _LOAD_ENV_AVAILABLE:
            print("[load_env] 环境变量未设置，尝试从系统文件自动加载...", file=sys.stderr)
            _ensure_env_loaded(verbose=True)
            secret_id = os.environ.get("TENCENTCLOUD_SECRET_ID", "")
            secret_key = os.environ.get("TENCENTCLOUD_SECRET_KEY", "")
        if not secret_id or not secret_key:
            if _LOAD_ENV_AVAILABLE:
                from load_env import _print_setup_hint, _TARGET_VARS
                _print_setup_hint(["TENCENTCLOUD_SECRET_ID", "TENCENTCLOUD_SECRET_KEY"])
            else:
                print(
                    "\n错误：TENCENTCLOUD_SECRET_ID / TENCENTCLOUD_SECRET_KEY 未设置。\n"
                    "请在 /etc/environment、~/.profile 等文件中添加这些变量后重新发起对话，\n"
                    "或直接在对话中发送变量值，由 AI 帮您配置。",
                    file=sys.stderr,
                )
            sys.exit(1)
    return credential.Credential(secret_id, secret_key)


def create_mps_client(cred, region):
    """创建 MPS 客户端。"""
    http_profile = HttpProfile()
    http_profile.endpoint = "mps.tencentcloudapi.com"
    http_profile.reqMethod = "POST"

    client_profile = ClientProfile()
    client_profile.httpProfile = http_profile

    return mps_client.MpsClient(cred, region, client_profile)


def build_input_info(args):
    """
    构建输入信息。

    支持三种输入方式：
    1. URL 输入：--url
    2. COS 对象路径（兼容旧版）：--cos-object（配合 --cos-bucket/--cos-region 或环境变量）
    3. COS 完整路径（新版，推荐）：--cos-input-bucket + --cos-input-region + --cos-input-key
    """
    # 方式1: URL 输入
    if args.url:
        return {
            "Type": "URL",
            "UrlInputInfo": {
                "Url": args.url
            }
        }
    
    # 方式3: COS 完整路径输入（新版，推荐）
    # 检查是否使用了新的COS路径参数
    cos_input_bucket = getattr(args, 'cos_input_bucket', None)
    cos_input_region = getattr(args, 'cos_input_region', None)
    cos_input_key = getattr(args, 'cos_input_key', None)
    
    if cos_input_bucket and cos_input_region and cos_input_key:
        return {
            "Type": "COS",
            "CosInputInfo": {
                "Bucket": cos_input_bucket,
                "Region": cos_input_region,
                "Object": cos_input_key
            }
        }
    
    # 方式2: COS 对象路径（兼容旧版）
    if args.cos_object:
        # COS 输入模式：bucket 和 region 支持从环境变量自动获取
        bucket = args.cos_bucket or get_cos_bucket()
        region = args.cos_region or get_cos_region()

        if not bucket:
            print("错误：COS 输入需要指定 Bucket。请通过 --cos-bucket 参数或 TENCENTCLOUD_COS_BUCKET 环境变量设置",
                  file=sys.stderr)
            sys.exit(1)
        if not region:
            print("错误：COS 输入需要指定 Region。请通过 --cos-region 参数或 TENCENTCLOUD_COS_REGION 环境变量设置",
                  file=sys.stderr)
            sys.exit(1)

        # 提示用户建议的路径规范
        if not args.cos_object.startswith("/input/"):
            print(f"提示：输入文件对象路径建议以 /input/ 开头（当前为 {args.cos_object}）", file=sys.stderr)

        return {
            "Type": "COS",
            "CosInputInfo": {
                "Bucket": bucket,
                "Region": region,
                "Object": args.cos_object
            }
        }
    
    print("错误：请指定输入源：\n"
          "  - URL: --url <URL>\n"
          "  - COS路径(推荐): --cos-input-bucket <bucket> --cos-input-region <region> --cos-input-key <key>\n"
          "  - COS对象(旧版): --cos-object <key>（配合环境变量或--cos-bucket/--cos-region）",
          file=sys.stderr)
    sys.exit(1)


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


def has_custom_params(args):
    """检测用户是否传入了任何自定义转码参数。"""
    return any([
        args.codec is not None,
        args.width is not None,
        args.height is not None,
        args.bitrate is not None,
        args.fps is not None,
        args.container is not None,
        args.audio_codec is not None,
        args.audio_bitrate is not None,
        args.scene_type is not None,
        args.compress_type is not None,
    ])


def build_transcode_task(args):
    """
    构建转码任务参数。

    策略：
    - 如果用户没有指定任何自定义参数 → 直接使用预设模板 100305
    - 如果用户指定了自定义参数 → 基于 100305 的默认值构建 RawParameter，用用户值覆盖
    """
    task = {}

    if not has_custom_params(args):
        # 纯预设模板模式
        task["Definition"] = PRESET_TEMPLATE_ID
    else:
        # 自定义参数模式：基于预设模板的默认参数，用户值覆盖
        container = args.container if args.container else PRESET_DEFAULTS["container"]
        codec = args.codec if args.codec else PRESET_DEFAULTS["codec"]
        width = args.width if args.width is not None else PRESET_DEFAULTS["width"]
        height = args.height if args.height is not None else PRESET_DEFAULTS["height"]
        bitrate = args.bitrate if args.bitrate is not None else PRESET_DEFAULTS["bitrate"]
        fps = args.fps if args.fps is not None else PRESET_DEFAULTS["fps"]
        audio_codec = args.audio_codec if args.audio_codec else PRESET_DEFAULTS["audio_codec"]
        audio_bitrate = args.audio_bitrate if args.audio_bitrate is not None else PRESET_DEFAULTS["audio_bitrate"]

        video_template = {
            "Codec": codec,
            "Fps": fps,
            "Bitrate": bitrate,
            "Width": width,
            "Height": height,
            "ResolutionAdaptive": "open",
            "FillType": "black",
        }

        # 场景化配置
        if args.scene_type or args.compress_type:
            video_template["ScenarioBased"] = 1
            if args.scene_type:
                video_template["SceneType"] = args.scene_type
            if args.compress_type:
                video_template["CompressType"] = args.compress_type
        else:
            # 默认极致压缩模式
            video_template["ScenarioBased"] = 1
            video_template["CompressType"] = "standard_compress"

        audio_template = {
            "Codec": audio_codec,
            "Bitrate": audio_bitrate,
            "SampleRate": PRESET_DEFAULTS["audio_sample_rate"],
            "AudioChannel": 2,
        }

        raw_parameter = {
            "Container": container,
            "RemoveVideo": 0,
            "RemoveAudio": 0,
            "VideoTemplate": video_template,
            "AudioTemplate": audio_template,
            "TEHDConfig": {
                "Type": "TEHD-100",   # 极速高清-100（视频极速高清）
                "MaxVideoBitrate": 0,  # 不设上限，由极速高清自动优化
            }
        }

        task["RawParameter"] = raw_parameter

    # 覆盖输出文件名（可选）
    if args.output_object_path:
        task["OutputObjectPath"] = args.output_object_path

    return task


def build_request_params(args):
    """构建完整的 ProcessMedia 请求参数。"""
    params = {}

    # 输入
    params["InputInfo"] = build_input_info(args)

    # 输出存储
    output_storage = build_output_storage(args)
    if output_storage:
        params["OutputStorage"] = output_storage

    # 输出目录：默认 /output/transcode/，用户可通过 --output-dir 覆盖
    params["OutputDir"] = args.output_dir if args.output_dir else "/output/transcode/"

    # 转码任务
    transcode_task = build_transcode_task(args)
    params["MediaProcessTask"] = {
        "TranscodeTaskSet": [transcode_task]
    }

    # 回调配置
    if args.notify_url:
        params["TaskNotifyConfig"] = {
            "NotifyType": "URL",
            "NotifyUrl": args.notify_url,
        }

    return params


def process_media(args):
    """发起极速高清转码任务。"""
    region = args.region or "ap-guangzhou"

    # 1. 获取凭证和客户端
    cred = get_credentials()
    client = create_mps_client(cred, region)

    # 2. 构建请求
    params = build_request_params(args)

    if args.dry_run:
        print("=" * 60)
        print("【Dry Run 模式】仅打印请求参数，不实际调用 API")
        print("=" * 60)
        print(json.dumps(params, ensure_ascii=False, indent=2))
        return

    # 打印请求参数（调试用）
    if args.verbose:
        print("请求参数：")
        print(json.dumps(params, ensure_ascii=False, indent=2))
        print()

    # 3. 发起调用
    try:
        req = models.ProcessMediaRequest()
        req.from_json_string(json.dumps(params))

        resp = client.ProcessMedia(req)
        result = json.loads(resp.to_json_string())

        task_id = result.get('TaskId', 'N/A')
        print("✅ 极速高清转码任务提交成功！")
        print(f"   TaskId: {task_id}")
        print(f"   RequestId: {result.get('RequestId', 'N/A')}")

        if not has_custom_params(args):
            print(f"   模板: 预设模板 {PRESET_TEMPLATE_ID}（极速高清-H265-MP4-1080P）")
        else:
            codec = args.codec or PRESET_DEFAULTS["codec"]
            container = args.container or PRESET_DEFAULTS["container"]
            print(f"   模式: 自定义参数（基于 {PRESET_TEMPLATE_ID} 预设参数修改）")
            print(f"   编码: {codec.upper()}, 封装: {container.upper()}")
            if args.width:
                w = args.width
                h = args.height if args.height else "自适应"
                print(f"   分辨率: {w} x {h}")
            if args.bitrate:
                print(f"   码率: {args.bitrate} kbps")
            compress = args.compress_type or "standard_compress"
            print(f"   压缩策略: {compress}")

        if args.verbose:
            print("\n完整响应：")
            print(json.dumps(result, ensure_ascii=False, indent=2))

        # 自动轮询（除非指定 --no-wait）
        no_wait = getattr(args, 'no_wait', False)
        if not no_wait and _POLL_AVAILABLE and task_id != 'N/A':
            poll_interval = getattr(args, 'poll_interval', 10)
            max_wait = getattr(args, 'max_wait', 1800)
            poll_video_task(task_id, region=region, interval=poll_interval,
                            max_wait=max_wait, verbose=args.verbose)
        else:
            print()
            print(f"提示：任务在后台处理中，可使用以下命令查询进度：")
            print(f"  python scripts/mps_get_video_task.py --task-id {task_id}")

        return result

    except TencentCloudSDKException as e:
        print(f"❌ 请求失败: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="腾讯云 MPS 极速高清转码 —— 在保证画质的基础上最大限度压缩码率，节约带宽和存储成本",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # URL输入 + 默认模板（极速高清-H265-1080P），输出到 TENCENTCLOUD_COS_BUCKET/output/transcode/
  python mps_transcode.py --url https://example.com/video.mp4

  # COS路径输入（推荐，本地上传后使用）
  python mps_transcode.py --cos-input-bucket mybucket-125xxx --cos-input-region ap-guangzhou --cos-input-key /input/video/test.mp4

  # COS对象输入（bucket 和 region 自动从环境变量获取）
  python mps_transcode.py --cos-object /input/video/test.mp4

  # COS对象输入 + 显式指定 bucket（覆盖环境变量）
  python mps_transcode.py --cos-bucket mybucket-125xxx --cos-region ap-guangzhou --cos-object /input/video/test.mp4

  # 自定义720P + 2Mbps码率上限
  python mps_transcode.py --url https://example.com/video.mp4 --width 1280 --height 720 --bitrate 2000

  # 极致压缩模式
  python mps_transcode.py --url https://example.com/video.mp4 --compress-type ultra_compress

  # UGC短视频场景优化
  python mps_transcode.py --url https://example.com/video.mp4 --scene-type ugc

  # 自定义输出目录（覆盖默认 /output/transcode/）
  python mps_transcode.py --url https://example.com/video.mp4 --output-dir /custom/

  # Dry Run（仅打印请求参数）
  python mps_transcode.py --url https://example.com/video.mp4 --dry-run

环境变量：
  TENCENTCLOUD_SECRET_ID   腾讯云 SecretId
  TENCENTCLOUD_SECRET_KEY  腾讯云 SecretKey
  TENCENTCLOUD_COS_BUCKET       COS Bucket 名称（如 mybucket-125xxx，默认 test_bucket）
  TENCENTCLOUD_COS_REGION       COS Bucket 区域（默认 ap-guangzhou）
        """
    )

    # ---- 输入源 ----
    input_group = parser.add_argument_group("输入源（三选一）")
    input_group.add_argument("--url", type=str, help="视频 URL 地址")
    
    # COS 路径输入（新版，推荐）- 用于本地上传后直接使用COS路径
    input_group.add_argument("--cos-input-bucket", type=str,
                             help="输入 COS Bucket 名称（与 --cos-input-region/--cos-input-key 配合使用）")
    input_group.add_argument("--cos-input-region", type=str,
                             help="输入 COS Bucket 区域（如 ap-guangzhou）")
    input_group.add_argument("--cos-input-key", type=str,
                             help="输入 COS 对象 Key（如 /input/video.mp4）")
    
    # COS 对象输入（旧版，兼容）
    input_group.add_argument("--cos-bucket", type=str,
                             help="COS Bucket 名称（默认取 TENCENTCLOUD_COS_BUCKET 环境变量）")
    input_group.add_argument("--cos-region", type=str,
                             help="COS Bucket 区域（默认取 TENCENTCLOUD_COS_REGION 环境变量，默认 ap-guangzhou）")
    input_group.add_argument("--cos-object", type=str,
                             help="COS 对象路径，建议以 /input/ 开头，如 /input/video/test.mp4")

    # ---- 输出 ----
    output_group = parser.add_argument_group("输出配置（可选，默认输出到 TENCENTCLOUD_COS_BUCKET/output/transcode/）")
    output_group.add_argument("--output-bucket", type=str,
                              help="输出 COS Bucket 名称（默认取 TENCENTCLOUD_COS_BUCKET 环境变量）")
    output_group.add_argument("--output-region", type=str,
                              help="输出 COS Bucket 区域（默认取 TENCENTCLOUD_COS_REGION 环境变量，默认 ap-guangzhou）")
    output_group.add_argument("--output-dir", type=str,
                              help="输出目录（默认 /output/transcode/），以 / 开头和结尾")
    output_group.add_argument("--output-object-path", type=str,
                              help="输出文件路径，如 /output/{inputName}_transcode.{format}")

    # ---- 视频转码参数 ----
    video_group = parser.add_argument_group("视频参数（可选，不指定则使用预设模板100305）")
    video_group.add_argument("--codec", type=str, choices=["h264", "h265", "h266", "av1", "vp9"],
                             help="视频编码格式（默认 h265）")
    video_group.add_argument("--width", type=int, help="视频宽度/长边（px），如 1920、1280、854")
    video_group.add_argument("--height", type=int, help="视频高度/短边（px），0=按比例缩放")
    video_group.add_argument("--bitrate", type=int,
                             help="视频码率（kbps），0=自动。极速高清会自动优化码率")
    video_group.add_argument("--fps", type=int, help="视频帧率（Hz），0=保持原始")
    video_group.add_argument("--container", type=str, choices=["mp4", "hls", "flv", "mp3", "m4a"],
                             help="封装格式（默认 mp4）")

    # ---- 音频参数 ----
    audio_group = parser.add_argument_group("音频参数（可选）")
    audio_group.add_argument("--audio-codec", type=str, choices=["aac", "mp3", "copy"],
                             help="音频编码格式（默认 aac）")
    audio_group.add_argument("--audio-bitrate", type=int, help="音频码率（kbps），默认 128")

    # ---- 极速高清策略 ----
    tehd_group = parser.add_argument_group("极速高清策略（可选）")
    tehd_group.add_argument("--compress-type", type=str,
                            choices=["ultra_compress", "standard_compress", "high_compress", "low_compress"],
                            help="压缩策略：ultra_compress=极致压缩 | standard_compress=综合最优 | "
                                 "high_compress=码率优先 | low_compress=画质优先")
    tehd_group.add_argument("--scene-type", type=str,
                            choices=["normal", "pgc", "materials_video", "ugc",
                                     "e-commerce_video", "educational_video"],
                            help="视频场景：normal=通用 | pgc=高清影视 | ugc=UGC短视频 | "
                                 "e-commerce_video=电商 | educational_video=教育")

    # ---- 其他 ----
    other_group = parser.add_argument_group("其他配置")
    other_group.add_argument("--region", type=str, help="MPS 服务区域（默认 ap-guangzhou）")
    other_group.add_argument("--notify-url", type=str, help="任务完成回调 URL")
    other_group.add_argument("--no-wait", action="store_true",
                             help="仅提交任务，不等待结果（默认会自动轮询直到完成）")
    other_group.add_argument("--poll-interval", type=int, default=10,
                             help="轮询间隔（秒），默认 10")
    other_group.add_argument("--max-wait", type=int, default=1800,
                             help="最长等待时间（秒），默认 1800（30分钟）")
    other_group.add_argument("--verbose", "-v", action="store_true", help="输出详细信息")
    other_group.add_argument("--dry-run", action="store_true", help="仅打印请求参数，不实际调用 API")

    args = parser.parse_args()

    # 校验输入
    has_url = bool(args.url)
    has_cos_object = bool(args.cos_object)
    has_cos_path = bool(getattr(args, 'cos_input_bucket', None) and 
                        getattr(args, 'cos_input_region', None) and 
                        getattr(args, 'cos_input_key', None))
    
    if not has_url and not has_cos_object and not has_cos_path:
        parser.error("请指定输入源：--url、--cos-object 或 --cos-input-bucket/--cos-input-region/--cos-input-key")

    # 打印环境变量信息
    cos_bucket_env = get_cos_bucket()
    cos_region_env = get_cos_region()

    # 打印执行信息
    print("=" * 60)
    print("腾讯云 MPS 极速高清转码")
    print("=" * 60)
    if args.url:
        print(f"输入: URL - {args.url}")
    elif getattr(args, 'cos_input_bucket', None):
        # 新版COS路径输入
        print(f"输入: COS - {args.cos_input_bucket}:{args.cos_input_key} (region: {args.cos_input_region})")
    else:
        bucket_display = args.cos_bucket or cos_bucket_env or "未设置"
        region_display = args.cos_region or cos_region_env
        print(f"输入: COS - {bucket_display}:{args.cos_object} (region: {region_display})")

    # 输出信息
    out_bucket = args.output_bucket or cos_bucket_env or "未设置"
    out_region = args.output_region or cos_region_env
    # 设置输出目录，默认为 /output/transcode/
    out_dir = args.output_dir or "/output/transcode/"
    print(f"输出: COS - {out_bucket}:{out_dir} (region: {out_region})")

    if cos_bucket_env:
        print(f"COS Bucket (环境变量): {cos_bucket_env}")
    else:
        print("提示: 未设置 TENCENTCLOUD_COS_BUCKET 环境变量，COS 功能可能受限")

    if not has_custom_params(args):
        print(f"模板: 预设模板 {PRESET_TEMPLATE_ID}（极速高清-H265-MP4-1080P）")
    else:
        print("模板: 自定义参数（基于预设模板 100305 修改）")
    print("-" * 60)

    # 执行
    process_media(args)


if __name__ == "__main__":
    main()