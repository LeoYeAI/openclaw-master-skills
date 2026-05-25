#!/usr/bin/env python3
"""
腾讯云 MPS AI 解说二创脚本

功能：
  输入原始视频，一站式自动完成解说脚本生成、脚本匹配成片、AI 配音、去字幕等操作，
  输出带有解说文案、配音和字幕的新视频。

  封装 ProcessMedia API，固定使用智能分析 35 号预设模板（AiAnalysisTask.Definition=35）。

预设场景（通过 --scene 指定）：
  - short-drama          短剧视频，画面上有字幕（默认，含擦除）
  - short-drama-no-erase 短剧视频，画面上没有字幕（关闭擦除）

默认行为：
  - 擦除（eraseOff）：开启（eraseOff=0），可通过 --no-erase 关闭
  - 转场（concatTransition）：flashwhite，时长 0.3s
  - 配音音色（voiceId）：不传（使用MPS默认系统音色），engine 固定 auto
  - 输出视频数量（outputVideoCount）：1，可通过 --output-count 指定，最大5
  - 解说模式（onlyNarration）：1（纯解说视频）
  - 输出语言（outputLanguage）：zh

多集视频支持：
  - 第一集通过 --url 或 --cos-object 传入
  - 后续集通过 --extra-urls 按顺序传入（分辨率须与第一集一致）

COS 存储约定：
  通过环境变量 TENCENTCLOUD_COS_BUCKET 指定 COS Bucket 名称。
  - 输入文件默认路径：{TENCENTCLOUD_COS_BUCKET}/input/   （即 COS Object 以 /input/ 开头）
  - 输出文件默认路径：{TENCENTCLOUD_COS_BUCKET}/output/narrate/  （即输出目录为 /output/narrate/）

用法：
  # 短剧单集解说（默认含擦除，输出1个视频）
  python mps_narrate.py --url https://example.com/drama_ep01.mp4 --scene short-drama

  # COS对象输入
  python mps_narrate.py --cos-object /input/drama_ep01.mp4 --scene short-drama

  # 短剧三集合并解说，输出3个不同版本
  python mps_narrate.py \\
      --url https://example.com/ep01.mp4 \\
      --extra-urls https://example.com/ep02.mp4 https://example.com/ep03.mp4 \\
      --scene short-drama \\
      --output-count 3

  # 原视频无字幕，关闭擦除
  python mps_narrate.py --url https://example.com/drama.mp4 --scene short-drama-no-erase

  # Dry Run（预览转义后的 ExtendedParameter）
  python mps_narrate.py --url https://example.com/drama.mp4 --scene short-drama --dry-run

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
# 预设场景参数（完整枚举，禁止扩展）
# =============================================================================

# 智能分析模板 ID（固定使用 35 号预设模板）
AI_ANALYSIS_TEMPLATE_ID = 35

# 预设场景配置
PRESET_SCENES = {
    "short-drama": {
        "desc": "短剧视频，画面上有字幕（默认，含擦除）",
        "erase_off": False,
        "extended_param": {
            "reel": {
                "processType": "narrate",
                "narrateParam": {
                    "onlyNarration": 1,
                    "concatTransition": "flashwhite",
                    "concatTransitionDuration": 0.3
                },
                "outputLanguage": "zh",
                "ttsParam": {
                    "engine": "auto"
                }
            }
        }
    },
    "short-drama-no-erase": {
        "desc": "短剧视频，画面上没有字幕（关闭擦除）",
        "erase_off": True,
        "extended_param": {
            "reel": {
                "processType": "narrate",
                "narrateParam": {
                    "onlyNarration": 1,
                    "concatTransition": "flashwhite",
                    "concatTransitionDuration": 0.3
                },
                "outputLanguage": "zh",
                "eraseParam": {
                    "eraseOff": 1
                },
                "ttsParam": {
                    "engine": "auto"
                }
            }
        }
    }
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


def build_extended_parameter(scene_config, output_count):
    """
    构建 ExtendedParameter。

    根据预设场景配置构建，并动态注入 outputVideoCount。
    """
    extended_param = json.loads(json.dumps(scene_config["extended_param"]))  # 深拷贝
    
    # 动态注入 outputVideoCount
    if "reel" not in extended_param:
        extended_param["reel"] = {}
    extended_param["reel"]["outputVideoCount"] = output_count
    
    return extended_param


def build_request_params(args):
    """构建完整的 ProcessMedia 请求参数。"""
    params = {}

    # 输入
    params["InputInfo"] = build_input_info(args)

    # 输出存储
    output_storage = build_output_storage(args)
    if output_storage:
        params["OutputStorage"] = output_storage

    # 输出目录：默认 /output/narrate/，用户可通过 --output-dir 覆盖
    params["OutputDir"] = args.output_dir if args.output_dir else "/output/narrate/"

    # 获取预设场景配置
    scene_config = PRESET_SCENES[args.scene]
    
    # 构建 ExtendedParameter
    extended_param = build_extended_parameter(scene_config, args.output_count)
    extended_param_str = json.dumps(extended_param, ensure_ascii=False)

    # AI 分析任务（固定使用 35 号预设模板）
    ai_analysis_task = {
        "Definition": AI_ANALYSIS_TEMPLATE_ID,
        "ExtendedParameter": extended_param_str
    }
    
    params["AiAnalysisTask"] = ai_analysis_task

    # 回调配置
    if args.notify_url:
        params["TaskNotifyConfig"] = {
            "NotifyType": "URL",
            "NotifyUrl": args.notify_url,
        }

    return params


def process_media(args):
    """发起 AI 解说二创任务。"""
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
        print("✅ AI 解说二创任务提交成功！")
        print(f"   TaskId: {task_id}")
        print(f"   RequestId: {result.get('RequestId', 'N/A')}")
        print(f"   场景: {args.scene} ({PRESET_SCENES[args.scene]['desc']})")
        print(f"   输出数量: {args.output_count}")
        
        if args.extra_urls:
            print(f"   输入视频: 1个主视频 + {len(args.extra_urls)}个额外视频")
        else:
            print(f"   输入视频: 1个")

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
        description="腾讯云 MPS AI 解说二创 —— 输入原始视频，自动生成解说脚本并生成解说视频",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # URL输入 + 默认场景（short-drama，含擦除），输出到 TENCENTCLOUD_COS_BUCKET/output/narrate/
  python mps_narrate.py --url https://example.com/drama.mp4 --scene short-drama

  # COS路径输入（推荐，本地上传后使用）
  python mps_narrate.py --cos-input-bucket mybucket-125xxx --cos-input-region ap-guangzhou --cos-input-key /input/drama.mp4 --scene short-drama

  # COS对象输入（bucket 和 region 自动从环境变量获取）
  python mps_narrate.py --cos-object /input/drama.mp4 --scene short-drama

  # 原视频无字幕，关闭擦除
  python mps_narrate.py --url https://example.com/drama.mp4 --scene short-drama-no-erase

  # 多集视频合并解说（第一集用 --url，后续集用 --extra-urls）
  python mps_narrate.py \\
      --url https://example.com/ep01.mp4 \\
      --extra-urls https://example.com/ep02.mp4 https://example.com/ep03.mp4 \\
      --scene short-drama

  # 输出3个不同版本的视频
  python mps_narrate.py --url https://example.com/drama.mp4 --scene short-drama --output-count 3

  # Dry Run（仅打印请求参数）
  python mps_narrate.py --url https://example.com/drama.mp4 --scene short-drama --dry-run

  # 不等待任务完成，仅提交
  python mps_narrate.py --url https://example.com/drama.mp4 --scene short-drama --no-wait

预设场景：
  short-drama          短剧视频，画面上有字幕（默认，含擦除）
  short-drama-no-erase 短剧视频，画面上没有字幕（关闭擦除）

环境变量：
  TENCENTCLOUD_SECRET_ID   腾讯云 SecretId
  TENCENTCLOUD_SECRET_KEY  腾讯云 SecretKey
  TENCENTCLOUD_COS_BUCKET       COS Bucket 名称（如 mybucket-125xxx，默认 test_bucket）
  TENCENTCLOUD_COS_REGION       COS Bucket 区域（默认 ap-guangzhou）
        """
    )

    # 输入参数（二选一）
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument("--url", help="输入视频 URL（第一集）")
    input_group.add_argument("--cos-object", dest="cos_object", help="COS 对象路径（第一集，如 /input/video.mp4）")
    
    # COS 完整路径输入（新版）
    parser.add_argument("--cos-input-bucket", dest="cos_input_bucket", help="COS 输入 Bucket 名称")
    parser.add_argument("--cos-input-region", dest="cos_input_region", help="COS 输入 Bucket 区域")
    parser.add_argument("--cos-input-key", dest="cos_input_key", help="COS 输入 Object Key")
    
    # COS 对象路径兼容参数
    parser.add_argument("--cos-bucket", dest="cos_bucket", help="COS Bucket 名称（用于 --cos-object）")
    parser.add_argument("--cos-region", dest="cos_region", help="COS Bucket 区域（用于 --cos-object）")
    
    # 多集视频支持
    parser.add_argument("--extra-urls", nargs="+", help="第2集及之后的视频 URL（按顺序，分辨率须与第一集一致）")

    # 场景（必填）
    parser.add_argument("--scene", required=True, choices=list(PRESET_SCENES.keys()),
                        help="预设场景（必填）")

    # 输出数量
    parser.add_argument("--output-count", type=int, default=1,
                        help="输出视频数量，默认1，最大5（超过5将截断为5）")

    # 输出配置
    parser.add_argument("--output-bucket", dest="output_bucket", help="输出 COS Bucket")
    parser.add_argument("--output-region", dest="output_region", help="输出 COS Region")
    parser.add_argument("--output-dir", dest="output_dir", help="输出目录（默认 /output/narrate/）")

    # 其他
    parser.add_argument("--region", help="MPS 服务区域（默认 ap-guangzhou）")
    parser.add_argument("--notify-url", dest="notify_url", help="回调 URL")
    parser.add_argument("--no-wait", action="store_true", help="仅提交任务，不轮询等待")
    parser.add_argument("--poll-interval", type=int, default=10, help="轮询间隔（秒，默认10）")
    parser.add_argument("--max-wait", type=int, default=1800, help="最大等待时间（秒，默认1800）")
    parser.add_argument("--dry-run", action="store_true", help="仅打印请求参数，不实际调用 API")
    parser.add_argument("--verbose", "-v", action="store_true", help="输出详细信息")

    args = parser.parse_args()

    # 参数校验
    if args.output_count < 1:
        print("错误：--output-count 必须大于等于1", file=sys.stderr)
        sys.exit(1)
    if args.output_count > 5:
        print(f"警告：--output-count 超过最大值5，已截断为5", file=sys.stderr)
        args.output_count = 5

    # 多集视频提示
    if args.extra_urls:
        print(f"提示：多集视频模式，共 {len(args.extra_urls) + 1} 个视频")
        print(f"  第1集（主视频）: {args.url or args.cos_object or args.cos_input_key}")
        for i, url in enumerate(args.extra_urls, 2):
            print(f"  第{i}集: {url}")
        print("  注意：所有视频分辨率须保持一致\n")

    process_media(args)


if __name__ == "__main__":
    main()
