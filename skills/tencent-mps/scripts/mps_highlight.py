#!/usr/bin/env python3
"""
腾讯云 MPS 精彩集锦脚本

功能：
  使用 MPS 智能分析功能，通过 AI 算法自动捕捉并生成视频中的精彩片段（高光集锦）。
  支持 VLOG、短剧、足球赛事、篮球赛事等多种场景。

  ⚠️ 重要提示：
  - 本脚本仅支持处理离线文件，不支持直播流
  - ExtendedParameter 必须从预设场景参数中选择，禁止自行拼装或扩展字段

  底层 API：ProcessMedia（离线文件）
  固定使用智能分析 26 号预设模板（AiAnalysisTask.Definition=26），不支持自定义模板

预设场景（通过 --scene 指定）：
  - vlog          VLOG、风景、无人机视频（大模型版）
  - vlog-panorama 全景相机（开启全景优化，大模型版）
  - short-drama   短剧、影视剧，提取主角出场/BGM高光（大模型版）
  - football      足球赛事，识别射门/进球/红黄牌/回放（高级版）
  - basketball    篮球赛事（高级版）
  - custom        自定义场景，可传 --prompt 和 --scenario（大模型版）

COS 存储约定：
  通过环境变量 TENCENTCLOUD_COS_BUCKET 指定 COS Bucket 名称。
  - 输入文件默认路径：{TENCENTCLOUD_COS_BUCKET}/input/   （即 COS Object 以 /input/ 开头）
  - 输出文件默认路径：{TENCENTCLOUD_COS_BUCKET}/output/highlight/  （即输出目录为 /output/highlight/）

用法：
  # 足球赛事精彩集锦
  python mps_highlight.py --cos-object /input/football.mp4 --scene football

  # 短剧影视高光
  python mps_highlight.py --cos-object /input/drama.mp4 --scene short-drama

  # VLOG 全景相机
  python mps_highlight.py --url https://example.com/vlog.mp4 --scene vlog-panorama

  # 自定义场景（大模型版）
  python mps_highlight.py --url https://example.com/skiing.mp4 \
      --scene custom --prompt "滑雪场景，输出人物高光" --scenario "滑雪"

  # 篮球赛事
  python mps_highlight.py --cos-object /input/basketball.mp4 --scene basketball

  # Dry Run（仅打印请求参数，不实际调用 API）
  python mps_highlight.py --cos-object /input/game.mp4 --scene football --dry-run

环境变量：
  TENCENTCLOUD_SECRET_ID   - 腾讯云 SecretId
  TENCENTCLOUD_SECRET_KEY  - 腾讯云 SecretKey
  TENCENTCLOUD_COS_BUCKET  - COS Bucket 名称（如 mybucket-125xxx）
  TENCENTCLOUD_COS_REGION  - COS Bucket 区域（默认 ap-guangzhou）
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
# 精彩集锦预设场景参数（固定值，禁止修改或扩展）
# =============================================================================

# 智能分析模板 ID（固定使用 26 号预设模板）
AI_ANALYSIS_DEFINITION = 26

# 预设场景参数表（ExtendedParameter 固定值，禁止动态拼装）
SCENE_PRESETS = {
    "vlog": {
        "desc": "VLOG、风景、无人机视频",
        "version": "大模型版",
        "extended_parameter": {
            "hht": {
                "top_clip": 5,
                "force_cls": 10020,
                "model_segment_limit": [3, 6]
            }
        },
        "allow_top_clip": True,
    },
    "vlog-panorama": {
        "desc": "全景相机（开启全景优化）",
        "version": "大模型版",
        "extended_parameter": {
            "hht": {
                "top_clip": 5,
                "force_cls": 10020,
                "model_segment_limit": [3, 6],
                "use_panorama_direct": 1,
                "panorama_video": 1
            }
        },
        "allow_top_clip": True,
    },
    "short-drama": {
        "desc": "短剧、影视剧，提取主角出场/BGM高光",
        "version": "大模型版",
        "extended_parameter": {
            "hht": {
                "force_cls": "10010",
                "merge_type": 0,
                "need_vad": 1,
                "top_clip": 100,
                "res_save_type": 1,
                "scenario": "电视剧高光"
            }
        },
        "allow_top_clip": False,
    },
    "football": {
        "desc": "足球赛事，识别射门/进球/红黄牌/回放",
        "version": "高级版",
        "extended_parameter": {
            "hht": {
                "force_cls": "4001",
                "merge_type": 0,
                "need_vad": 1,
                "top_clip": 100,
                "res_save_type": 1
            }
        },
        "allow_top_clip": False,
    },
    "basketball": {
        "desc": "篮球赛事",
        "version": "高级版",
        "extended_parameter": {
            "hht": {
                "force_cls": "4002",
                "merge_type": 0,
                "need_vad": 1,
                "top_clip": 100,
                "res_save_type": 1
            }
        },
        "allow_top_clip": False,
    },
    "custom": {
        "desc": "自定义场景，可传 --prompt 和 --scenario",
        "version": "大模型版",
        "extended_parameter_template": {
            "hht": {
                "top_clip": 5,
                "force_cls": 10020,
                "prompts": {
                    "multimodal_prompt": "{prompt}"
                },
                "scenario": "{scenario}",
                "model_segment_limit": [3, 6]
            }
        },
        "allow_top_clip": True,
    },
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


def build_extended_parameter(scene, top_clip=None, prompt=None, scenario=None):
    """
    构建 ExtendedParameter 参数。

    ⚠️ 严格从预设表中获取，禁止动态拼装字段。
    """
    if scene not in SCENE_PRESETS:
        raise ValueError(f"未知场景: {scene}")

    preset = SCENE_PRESETS[scene]

    if scene == "custom":
        # 自定义场景：使用模板填充 prompt 和 scenario
        template = preset["extended_parameter_template"]
        # 深拷贝模板
        import copy
        param = copy.deepcopy(template)

        # 填充 prompt
        if prompt:
            param["hht"]["prompts"]["multimodal_prompt"] = prompt
        else:
            # 如果没有 prompt，移除 prompts 字段
            del param["hht"]["prompts"]

        # 填充 scenario
        if scenario:
            param["hht"]["scenario"] = scenario
        else:
            # 如果没有 scenario，移除 scenario 字段
            del param["hht"]["scenario"]

        # 处理 top_clip
        if top_clip is not None and preset.get("allow_top_clip"):
            param["hht"]["top_clip"] = top_clip

        return param
    else:
        # 预设场景：直接返回固定值
        import copy
        param = copy.deepcopy(preset["extended_parameter"])

        # 处理 top_clip（仅允许在特定场景下覆盖）
        if top_clip is not None and preset.get("allow_top_clip"):
            param["hht"]["top_clip"] = top_clip

        return param


def build_ai_analysis_task(args):
    """
    构建智能分析任务参数（精彩集锦）。

    固定使用 26 号预设模板，通过 ExtendedParameter 指定具体场景。
    """
    # 构建 ExtendedParameter
    extended_param = build_extended_parameter(
        args.scene,
        top_clip=args.top_clip,
        prompt=getattr(args, 'prompt', None),
        scenario=getattr(args, 'scenario', None)
    )

    task = {
        "Definition": AI_ANALYSIS_DEFINITION,
        "ExtendedParameter": json.dumps(extended_param, ensure_ascii=False)
    }

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

    # 输出目录：默认 /output/highlight/
    params["OutputDir"] = args.output_dir if args.output_dir else "/output/highlight/"

    # 智能分析任务（精彩集锦）
    ai_analysis_task = build_ai_analysis_task(args)
    params["AiAnalysisTask"] = ai_analysis_task

    # 回调配置
    if args.notify_url:
        params["TaskNotifyConfig"] = {
            "NotifyType": "URL",
            "NotifyUrl": args.notify_url,
        }

    return params


def get_scene_summary(args):
    """生成场景配置摘要文本。"""
    items = []
    preset = SCENE_PRESETS.get(args.scene, {})

    items.append(f"🎬 场景: {args.scene}（{preset.get('desc', '')}）")
    items.append(f"📊 计费版本: {preset.get('version', '')}")

    # top_clip 信息
    if args.top_clip is not None:
        if preset.get("allow_top_clip"):
            items.append(f"🔢 集锦片段数: 最多 {args.top_clip} 个")
        else:
            items.append(f"⚠️ 注意: --top-clip 参数在 {args.scene} 场景下不生效")

    # 自定义场景信息
    if args.scene == "custom":
        if getattr(args, 'prompt', None):
            items.append(f"💬 Prompt: {args.prompt}")
        if getattr(args, 'scenario', None):
            items.append(f"📝 Scenario: {args.scenario}")

    return items


def process_media(args):
    """发起精彩集锦任务。"""
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
        print("✅ 精彩集锦任务提交成功！")
        print(f"   TaskId: {task_id}")
        print(f"   RequestId: {result.get('RequestId', 'N/A')}")

        # 打印场景信息
        scene_items = get_scene_summary(args)
        if scene_items:
            print("   配置详情:")
            for item in scene_items:
                print(f"     {item}")

        print()
        print("⚠️  注意：精彩集锦任务处理时间较长，请耐心等待。")

        if args.verbose:
            print("\n完整响应：")
            print(json.dumps(result, ensure_ascii=False, indent=2))

        # 自动轮询（除非指定 --no-wait）
        no_wait = getattr(args, 'no_wait', False)
        if not no_wait and _POLL_AVAILABLE and task_id != 'N/A':
            poll_interval = getattr(args, 'poll_interval', 10)
            max_wait = getattr(args, 'max_wait', 1800)  # 精彩集锦耗时较长，默认30分钟
            poll_video_task(task_id, region=region, interval=poll_interval,
                            max_wait=max_wait, verbose=args.verbose)
        else:
            print(f"\n提示：任务在后台处理中，可使用以下命令查询进度：")
            print(f"  python scripts/mps_get_video_task.py --task-id {task_id}")

        return result

    except TencentCloudSDKException as e:
        print(f"❌ 请求失败: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="腾讯云 MPS 精彩集锦 —— AI自动提取视频高光片段",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 足球赛事精彩集锦
  python mps_highlight.py --cos-object /input/football.mp4 --scene football

  # 短剧影视高光
  python mps_highlight.py --cos-object /input/drama.mp4 --scene short-drama

  # VLOG 全景相机
  python mps_highlight.py --url https://example.com/vlog.mp4 --scene vlog-panorama

  # 自定义场景（大模型版）
  python mps_highlight.py --url https://example.com/skiing.mp4 \\
      --scene custom --prompt "滑雪场景，输出人物高光" --scenario "滑雪"

  # 篮球赛事
  python mps_highlight.py --cos-object /input/basketball.mp4 --scene basketball

  # 指定输出片段数（仅 vlog/vlog-panorama/custom 支持）
  python mps_highlight.py --cos-object /input/vlog.mp4 --scene vlog --top-clip 10

  # Dry Run（仅打印请求参数）
  python mps_highlight.py --cos-object /input/game.mp4 --scene football --dry-run

预设场景（--scene）：
  vlog          VLOG、风景、无人机视频（大模型版）
  vlog-panorama 全景相机（开启全景优化，大模型版）
  short-drama   短剧、影视剧，提取主角出场/BGM高光（大模型版）
  football      足球赛事，识别射门/进球/红黄牌/回放（高级版）
  basketball    篮球赛事（高级版）
  custom        自定义场景，可传 --prompt 和 --scenario（大模型版）

⚠️ 重要提示：
  - 本脚本仅支持处理离线文件，不支持直播流
  - --top-clip 仅允许在 vlog / vlog-panorama / custom 场景下使用
  - --prompt 和 --scenario 仅在 --scene custom 时生效
  - ExtendedParameter 必须从预设场景参数中选择，禁止自行拼装

环境变量：
  TENCENTCLOUD_SECRET_ID   腾讯云 SecretId
  TENCENTCLOUD_SECRET_KEY  腾讯云 SecretKey
  TENCENTCLOUD_COS_BUCKET  COS Bucket 名称
  TENCENTCLOUD_COS_REGION  COS Bucket 区域（默认 ap-guangzhou）
        """
    )

    # ---- 输入源 ----
    input_group = parser.add_argument_group("输入源（三选一）")
    input_group.add_argument("--url", type=str, help="视频 URL 地址")

    # COS 路径输入（新版，推荐）
    input_group.add_argument("--cos-input-bucket", type=str,
                             help="输入 COS Bucket 名称")
    input_group.add_argument("--cos-input-region", type=str,
                             help="输入 COS Bucket 区域（如 ap-guangzhou）")
    input_group.add_argument("--cos-input-key", type=str,
                             help="输入 COS 对象 Key（如 /input/video.mp4）")

    # COS 对象输入（旧版，兼容）
    input_group.add_argument("--cos-bucket", type=str,
                             help="COS Bucket 名称（默认取 TENCENTCLOUD_COS_BUCKET 环境变量）")
    input_group.add_argument("--cos-region", type=str,
                             help="COS Bucket 区域（默认取 TENCENTCLOUD_COS_REGION 环境变量）")
    input_group.add_argument("--cos-object", type=str,
                             help="COS 对象路径，建议以 /input/ 开头")

    # ---- 场景选择（必填）----
    scene_group = parser.add_argument_group("场景选择（必填）")
    scene_group.add_argument(
        "--scene", type=str, required=True,
        choices=list(SCENE_PRESETS.keys()),
        metavar="SCENE",
        help=(
            "预设场景。可选值："
            "vlog=VLOG风景 | "
            "vlog-panorama=全景相机 | "
            "short-drama=短剧影视 | "
            "football=足球赛事 | "
            "basketball=篮球赛事 | "
            "custom=自定义场景"
        )
    )

    # ---- 自定义场景参数（仅 custom 场景生效）----
    custom_group = parser.add_argument_group("自定义场景参数（仅 --scene custom 生效）")
    custom_group.add_argument("--prompt", type=str,
                              help="multimodal_prompt 内容，描述需要提取的高光内容")
    custom_group.add_argument("--scenario", type=str,
                              help="场景名称描述")

    # ---- 输出 ----
    output_group = parser.add_argument_group("输出配置（可选）")
    output_group.add_argument("--output-bucket", type=str,
                              help="输出 COS Bucket 名称")
    output_group.add_argument("--output-region", type=str,
                              help="输出 COS Bucket 区域")
    output_group.add_argument("--output-dir", type=str,
                              help="输出目录（默认 /output/highlight/）")
    output_group.add_argument("--output-object-path", type=str,
                              help="输出文件路径")

    # ---- 集锦配置 ----
    highlight_group = parser.add_argument_group("集锦配置")
    highlight_group.add_argument("--top-clip", type=int,
                                 help="最多输出集锦片段数（仅 vlog/vlog-panorama/custom 场景可用，默认5）")

    # ---- 其他 ----
    other_group = parser.add_argument_group("其他配置")
    other_group.add_argument("--region", type=str, help="MPS 服务区域（默认 ap-guangzhou）")
    other_group.add_argument("--notify-url", type=str, help="任务完成回调 URL")
    other_group.add_argument("--no-wait", action="store_true",
                             help="仅提交任务，不等待结果")
    other_group.add_argument("--poll-interval", type=int, default=10,
                             help="轮询间隔（秒），默认 10")
    other_group.add_argument("--max-wait", type=int, default=1800,
                             help="最长等待时间（秒），默认 1800（30分钟）")
    other_group.add_argument("--verbose", "-v", action="store_true", help="输出详细信息")
    other_group.add_argument("--dry-run", action="store_true", help="仅打印参数，不调用 API")

    args = parser.parse_args()

    # ---- 校验 ----
    # 1. 输入源
    has_url = bool(args.url)
    has_cos_object = bool(args.cos_object)
    has_cos_path = bool(getattr(args, 'cos_input_bucket', None) and
                        getattr(args, 'cos_input_region', None) and
                        getattr(args, 'cos_input_key', None))

    if not has_url and not has_cos_object and not has_cos_path:
        parser.error("请指定输入源：--url、--cos-object 或 --cos-input-bucket/--cos-input-region/--cos-input-key")

    # 2. --top-clip 仅允许在特定场景下使用
    if args.top_clip is not None:
        preset = SCENE_PRESETS.get(args.scene, {})
        if not preset.get("allow_top_clip"):
            allowed_scenes = [s for s, p in SCENE_PRESETS.items() if p.get("allow_top_clip")]
            parser.error(
                f"--top-clip 参数仅在以下场景可用: {', '.join(allowed_scenes)}。"
                f"当前场景 '{args.scene}' 不支持此参数。"
            )

    # 3. --prompt 和 --scenario 仅在 custom 场景下生效
    if args.prompt and args.scene != "custom":
        parser.error("--prompt 仅在 --scene custom 时生效")
    if args.scenario and args.scene != "custom":
        parser.error("--scenario 仅在 --scene custom 时生效")

    # 打印环境变量信息
    cos_bucket_env = get_cos_bucket()
    cos_region_env = get_cos_region()

    # 打印执行信息
    preset = SCENE_PRESETS.get(args.scene, {})
    print("=" * 60)
    print(f"腾讯云 MPS 精彩集锦 — {preset.get('desc', args.scene)}")
    print("=" * 60)
    if args.url:
        print(f"输入: URL - {args.url}")
    elif getattr(args, 'cos_input_bucket', None):
        print(f"输入: COS - {args.cos_input_bucket}:{args.cos_input_key} (region: {args.cos_input_region})")
    else:
        bucket_display = args.cos_bucket or cos_bucket_env or "未设置"
        region_display = args.cos_region or cos_region_env
        print(f"输入: COS - {bucket_display}:{args.cos_object} (region: {region_display})")

    # 输出信息
    out_bucket = args.output_bucket or cos_bucket_env or "未设置"
    out_region = args.output_region or cos_region_env
    out_dir = args.output_dir or "/output/highlight/"
    print(f"输出: COS - {out_bucket}:{out_dir} (region: {out_region})")

    if cos_bucket_env:
        print(f"COS Bucket (环境变量): {cos_bucket_env}")
    else:
        print("提示: 未设置 TENCENTCLOUD_COS_BUCKET 环境变量，COS 功能可能受限")

    print(f"场景: {args.scene}（{preset.get('version', '')}）")

    # 打印场景配置
    scene_items = get_scene_summary(args)
    if scene_items:
        print("配置详情:")
        for item in scene_items:
            print(f"  {item}")

    print()
    print("⚠️  提示：精彩集锦任务处理时间较长，请耐心等待。")
    print("-" * 60)

    # 执行
    process_media(args)


if __name__ == "__main__":
    main()
