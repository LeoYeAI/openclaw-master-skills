#!/usr/bin/env python3
"""
腾讯云 MPS 视频增强脚本

功能：
  使用 MPS 视频增强功能，支持各种视频质量问题的增强修复，全面提升画质体验！
  封装视频增强 API（默认使用极速高清转码），支持大模型增强、综合增强、去毛刺三种预设。

  默认使用 321002 预设模板。如果用户提出一些参数要求（分辨率、码率、增强能力等），
  基于 321002 预设模板的参数修改。

  三种预设模式（互斥，最多选一个）：
    - diffusion（大模型增强）：利用扩散模型进行画质重建，效果最强，耗时较长
    - comprehensive（综合增强）：综合画质优化，平衡效果与效率
    - artifact（去毛刺/去伪影）：针对压缩产生的毛刺/伪影进行修复

  互斥约束：
    - 大模型增强、综合增强、去毛刺三者最多开启一项
    - 大模型增强不可与超分（SuperResolution）、降噪（Denoise）同时开启

COS 存储约定：
  通过环境变量 TENCENTCLOUD_COS_BUCKET 指定 COS Bucket 名称。
  - 输入文件默认路径：{TENCENTCLOUD_COS_BUCKET}/input/   （即 COS Object 以 /input/ 开头）
  - 输出文件默认路径：{TENCENTCLOUD_COS_BUCKET}/output/enhance/  （即输出目录为 /output/enhance/）

  当使用 COS 输入时，如果未显式指定 --cos-bucket，自动使用 TENCENTCLOUD_COS_BUCKET。
  当未显式指定 --output-bucket，自动使用 TENCENTCLOUD_COS_BUCKET 作为输出 Bucket。
  当未显式指定 --output-dir，自动使用 /output/enhance/ 作为输出目录。

用法：
  # 最简用法：使用 URL 输入 + 默认预设模板 321002（输出到 TENCENTCLOUD_COS_BUCKET/output/enhance/）
  python mps_enhance.py --url https://example.com/video.mp4

  # COS 输入（自动使用 TENCENTCLOUD_COS_BUCKET，对象路径在 /input/ 下）
  python mps_enhance.py --cos-object /input/video/test.mp4

  # 大模型增强预设（强度 strong）
  python mps_enhance.py --url https://example.com/video.mp4 --preset diffusion --diffusion-type strong

  # 综合增强预设（强度 normal）
  python mps_enhance.py --url https://example.com/video.mp4 --preset comprehensive --comprehensive-type normal

  # 去毛刺预设（强度 strong）
  python mps_enhance.py --url https://example.com/video.mp4 --preset artifact --artifact-type strong

  # 自定义分辨率（宽1920，高度自适应）
  python mps_enhance.py --url https://example.com/video.mp4 --width 1920

  # 自定义码率上限（单位 kbps）
  python mps_enhance.py --url https://example.com/video.mp4 --bitrate 3000

  # 同时开启色彩增强和低光照增强
  python mps_enhance.py --url https://example.com/video.mp4 --color-enhance --low-light-enhance

  # 开启超分（2倍）+ 降噪 + 色彩增强（不可与大模型增强同时使用）
  python mps_enhance.py --url https://example.com/video.mp4 --super-resolution --denoise --color-enhance

  # 开启去划痕（老片修复场景）
  python mps_enhance.py --url https://example.com/video.mp4 --scratch-repair 0.8 --scene-type LQ_material

  # 使用 HDR 增强
  python mps_enhance.py --url https://example.com/video.mp4 --hdr HDR10

  # 开启插帧（目标60fps）
  python mps_enhance.py --url https://example.com/video.mp4 --frame-rate 60

  # 指定增强场景（游戏视频）
  python mps_enhance.py --url https://example.com/video.mp4 --scene-type game

  # 开启音频增强（降噪 + 音量均衡 + 美化）
  python mps_enhance.py --url https://example.com/video.mp4 --audio-denoise --volume-balance --audio-beautify

  # 自定义编码和封装格式
  python mps_enhance.py --url https://example.com/video.mp4 --codec h265 --container mp4

  # Dry Run（仅打印请求参数，不实际调用 API）
  python mps_enhance.py --url https://example.com/video.mp4 --dry-run

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
# 大模型增强专用模板（327001 ~ 327020）
# =============================================================================
# 真人场景（Real）— 适用于真人实拍，人脸与文字区域保护
# 漫剧场景（Anime）— 适用于动漫风格画面，线条色块特征增强
# 抖动优化（JitterOpt）— 减少帧间抖动与纹理跳变
# 细节最强（DetailMax）— 最大化纹理细节还原
# 人脸保真（FaceFidelity）— 最大程度保留人脸五官细节
#
# 模板号  场景          分辨率  说明
# 327001  Real          720P    真人场景-大模型增强-降噪+超分+综合增强
# 327002  Anime         720P    漫剧场景-大模型增强-降噪+超分+综合增强
# 327003  Real          1080P   真人场景-大模型增强-降噪+超分+综合增强
# 327004  Anime         1080P   漫剧场景-大模型增强-降噪+超分+综合增强
# 327005  Real          2K      真人场景-大模型增强-降噪+超分+综合增强
# 327006  Anime         2K      漫剧场景-大模型增强-降噪+超分+综合增强
# 327007  Real          4K      真人场景-大模型增强-降噪+超分+综合增强
# 327008  Anime         4K      漫剧场景-大模型增强-降噪+超分+综合增强
# 327009  JitterOpt     720P    抖动优化-大模型增强-降噪+超分+综合增强
# 327010  JitterOpt     1080P   抖动优化-大模型增强-降噪+超分+综合增强
# 327011  JitterOpt     2K      抖动优化-大模型增强-降噪+超分+综合增强
# 327012  JitterOpt     4K      抖动优化-大模型增强-降噪+超分+综合增强
# 327013  DetailMax     720P    细节最强-大模型增强-降噪+超分+综合增强
# 327014  DetailMax     1080P   细节最强-大模型增强-降噪+超分+综合增强
# 327015  DetailMax     2K      细节最强-大模型增强-降噪+超分+综合增强
# 327016  DetailMax     4K      细节最强-大模型增强-降噪+超分+综合增强
# 327017  FaceFidelity  720P    人脸保真-大模型增强-降噪+超分+综合增强
# 327018  FaceFidelity  1080P   人脸保真-大模型增强-降噪+超分+综合增强
# 327019  FaceFidelity  2K      人脸保真-大模型增强-降噪+超分+综合增强
# 327020  FaceFidelity  4K      人脸保真-大模型增强-降噪+超分+综合增强

DIFFUSION_TEMPLATES = {
    # 真人场景（Real）
    "real-720p": 327001,
    "real-1080p": 327003,
    "real-2k": 327005,
    "real-4k": 327007,
    # 漫剧场景（Anime）
    "anime-720p": 327002,
    "anime-1080p": 327004,
    "anime-2k": 327006,
    "anime-4k": 327008,
    # 抖动优化（JitterOpt）
    "jitter-720p": 327009,
    "jitter-1080p": 327010,
    "jitter-2k": 327011,
    "jitter-4k": 327012,
    # 细节最强（DetailMax）
    "detail-720p": 327013,
    "detail-1080p": 327014,
    "detail-2k": 327015,
    "detail-4k": 327016,
    # 人脸保真（FaceFidelity）
    "face-720p": 327017,
    "face-1080p": 327018,
    "face-2k": 327019,
    "face-4k": 327020,
}

DIFFUSION_TEMPLATE_DESC = {
    327001: "真人场景-720P（人脸与文字区域保护）",
    327002: "漫剧场景-720P（动漫线条色块增强）",
    327003: "真人场景-1080P（人脸与文字区域保护）",
    327004: "漫剧场景-1080P（动漫线条色块增强）",
    327005: "真人场景-2K（人脸与文字区域保护）",
    327006: "漫剧场景-2K（动漫线条色块增强）",
    327007: "真人场景-4K（人脸与文字区域保护）",
    327008: "漫剧场景-4K（动漫线条色块增强）",
    327009: "抖动优化-720P（减少帧间抖动与纹理跳变）",
    327010: "抖动优化-1080P（减少帧间抖动与纹理跳变）",
    327011: "抖动优化-2K（减少帧间抖动与纹理跳变）",
    327012: "抖动优化-4K（减少帧间抖动与纹理跳变）",
    327013: "细节最强-720P（最大化纹理细节还原）",
    327014: "细节最强-1080P（最大化纹理细节还原）",
    327015: "细节最强-2K（最大化纹理细节还原）",
    327016: "细节最强-4K（最大化纹理细节还原）",
    327017: "人脸保真-720P（最大程度保留人脸五官细节）",
    327018: "人脸保真-1080P（最大程度保留人脸五官细节）",
    327019: "人脸保真-2K（最大程度保留人脸五官细节）",
    327020: "人脸保真-4K（最大程度保留人脸五官细节）",
}

# =============================================================================
# 预设模板 321002 的默认参数（视频增强-极速高清转码）
# =============================================================================
PRESET_TEMPLATE_ID = 321002
PRESET_DEFAULTS = {
    "container": "mp4",
    "codec": "h265",
    "width": 0,           # 0 表示与原始保持一致
    "height": 0,          # 0 表示按比例缩放
    "bitrate": 0,         # 0 表示与原始保持一致，由极速高清自动优化
    "fps": 0,             # 0 表示与原始保持一致
    "audio_codec": "aac",
    "audio_bitrate": 128,
    "audio_sample_rate": 44100,
}

# 增强预设类型映射
ENHANCE_PRESETS = {
    "diffusion": "大模型增强（DiffusionEnhance）",
    "comprehensive": "综合增强（ImageQualityEnhance）",
    "artifact": "去毛刺/去伪影（ArtifactRepair）",
}

# 增强场景说明映射
SCENE_TYPE_DESC = {
    "common": "通用 — 适用于各种视频类型的基础优化",
    "AIGC": "AIGC — 利用AI提升视频整体分辨率",
    "short_play": "短剧 — 增强面部与字幕细节",
    "short_video": "短视频 — 优化复杂多样的画质问题",
    "game": "游戏视频 — 修复运动模糊，提升细节",
    "HD_movie_series": "超高清影视剧 — 生成4K 60fps HDR超高清",
    "LQ_material": "低清素材/老片修复 — 分辨率提升与损伤修复",
    "lecture": "秀场/电商/大会/讲座 — 美化提升面部效果",
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


def validate_enhance_args(args):
    """
    校验增强参数的互斥约束。

    规则：
    - 大模型增强（diffusion）、综合增强（comprehensive）、去毛刺（artifact）三者最多开启一项
    - 大模型增强不可与超分（super_resolution）同时开启
    - 大模型增强不可与降噪（denoise）同时开启
    """
    # 预设模式互斥校验
    if args.preset == "diffusion":
        if args.super_resolution:
            print("错误：大模型增强（diffusion）不可与超分（--super-resolution）同时开启", file=sys.stderr)
            sys.exit(1)
        if args.denoise:
            print("错误：大模型增强（diffusion）不可与降噪（--denoise）同时开启", file=sys.stderr)
            sys.exit(1)


def has_custom_params(args):
    """检测用户是否传入了任何自定义转码/增强参数。"""
    return any([
        args.codec is not None,
        args.width is not None,
        args.height is not None,
        args.bitrate is not None,
        args.fps is not None,
        args.container is not None,
        args.audio_codec is not None,
        args.audio_bitrate is not None,
        args.preset is not None,
        args.super_resolution,
        args.denoise,
        args.color_enhance,
        args.low_light_enhance,
        args.scratch_repair is not None,
        args.hdr is not None,
        args.frame_rate is not None,
        args.scene_type is not None,
        args.audio_denoise,
        args.audio_separate is not None,
        args.volume_balance,
        args.audio_beautify,
    ])


def build_video_enhance(args):
    """
    构建 VideoEnhance 配置。

    根据用户选择的预设模式和额外增强开关，构建视频增强参数。
    """
    video_enhance = {}

    # ---- 核心增强能力（三选一，互斥） ----
    if args.preset == "diffusion":
        diffusion_type = args.diffusion_type or "normal"
        video_enhance["DiffusionEnhance"] = {
            "Switch": "ON",
            "Type": diffusion_type,
        }
    elif args.preset == "comprehensive":
        comprehensive_type = args.comprehensive_type or "weak"
        video_enhance["ImageQualityEnhance"] = {
            "Switch": "ON",
            "Type": comprehensive_type,
        }
    elif args.preset == "artifact":
        artifact_type = args.artifact_type or "weak"
        video_enhance["ArtifactRepair"] = {
            "Switch": "ON",
            "Type": artifact_type,
        }

    # ---- 可叠加的增强能力 ----

    # 超分（注意不可与大模型增强同时开启，已在 validate_enhance_args 中校验）
    if args.super_resolution:
        sr_config = {"Switch": "ON"}
        if args.sr_type:
            sr_config["Type"] = args.sr_type
        if args.sr_size:
            sr_config["Size"] = args.sr_size
        video_enhance["SuperResolution"] = sr_config

    # 降噪（注意不可与大模型增强同时开启，已在 validate_enhance_args 中校验）
    if args.denoise:
        denoise_config = {"Switch": "ON"}
        if args.denoise_type:
            denoise_config["Type"] = args.denoise_type
        video_enhance["Denoise"] = denoise_config

    # 色彩增强
    if args.color_enhance:
        color_config = {"Switch": "ON"}
        if args.color_enhance_type:
            color_config["Type"] = args.color_enhance_type
        video_enhance["ColorEnhance"] = color_config

    # 低光照增强
    if args.low_light_enhance:
        video_enhance["LowLightEnhance"] = {
            "Switch": "ON",
            "Type": "normal",
        }

    # 去划痕
    if args.scratch_repair is not None:
        video_enhance["ScratchRepair"] = {
            "Switch": "ON",
            "Intensity": args.scratch_repair,
        }

    # HDR
    if args.hdr:
        video_enhance["Hdr"] = {
            "Switch": "ON",
            "Type": args.hdr,
        }

    # 插帧
    if args.frame_rate is not None:
        video_enhance["FrameRateWithDen"] = {
            "Switch": "ON",
            "FpsNum": args.frame_rate,
            "FpsDen": 1,
        }

    # 增强场景
    if args.scene_type:
        video_enhance["EnhanceSceneType"] = args.scene_type

    return video_enhance if video_enhance else None


def build_audio_enhance(args):
    """
    构建 AudioEnhance 配置。
    """
    audio_enhance = {}

    # 音频降噪
    if args.audio_denoise:
        audio_enhance["Denoise"] = {"Switch": "ON"}

    # 音频分离
    if args.audio_separate:
        separate_config = {"Switch": "ON"}
        if args.audio_separate == "vocal":
            separate_config["Type"] = "normal"
            separate_config["Track"] = "vocal"
        elif args.audio_separate == "background":
            separate_config["Type"] = "normal"
            separate_config["Track"] = "background"
        elif args.audio_separate == "accompaniment":
            separate_config["Type"] = "music"
            separate_config["Track"] = "background"
        audio_enhance["Separate"] = separate_config

    # 音量均衡
    if args.volume_balance:
        vb_config = {"Switch": "ON"}
        if args.volume_balance_type:
            vb_config["Type"] = args.volume_balance_type
        audio_enhance["VolumeBalance"] = vb_config

    # 音频美化
    if args.audio_beautify:
        audio_enhance["Beautify"] = {
            "Switch": "ON",
            "Types": ["declick", "deesser"],
        }

    return audio_enhance if audio_enhance else None


def build_transcode_task(args):
    """
    构建转码任务参数（含增强配置）。

    策略：
    - 如果用户指定了 --template（大模型增强专用模板 327001~327020）→ 直接使用该模板
    - 如果用户没有指定任何自定义参数 → 直接使用预设模板 321002
    - 如果用户指定了自定义参数 → 基于 321002 的默认值构建 RawParameter，用用户值覆盖
    """
    task = {}

    # 优先使用用户指定的大模型增强专用模板
    if args.template:
        task["Definition"] = args.template
    elif not has_custom_params(args):
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

        # 极速高清场景化配置
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
                "Type": "TEHD-100",
                "MaxVideoBitrate": 0,
            }
        }

        # ---- 构建增强配置 ----
        enhance_config = {}

        video_enhance = build_video_enhance(args)
        if video_enhance:
            enhance_config["VideoEnhance"] = video_enhance

        audio_enhance = build_audio_enhance(args)
        if audio_enhance:
            enhance_config["AudioEnhance"] = audio_enhance

        if enhance_config:
            raw_parameter["EnhanceConfig"] = enhance_config

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

    # 输出目录：默认 /output/enhance/，用户可通过 --output-dir 覆盖
    params["OutputDir"] = args.output_dir if args.output_dir else "/output/enhance/"

    # 转码任务（含增强配置）
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


def get_enhance_summary(args):
    """生成增强能力摘要文本。"""
    items = []

    if args.preset:
        preset_desc = ENHANCE_PRESETS.get(args.preset, args.preset)
        if args.preset == "diffusion":
            strength = args.diffusion_type or "normal"
        elif args.preset == "comprehensive":
            strength = args.comprehensive_type or "weak"
        elif args.preset == "artifact":
            strength = args.artifact_type or "weak"
        else:
            strength = ""
        items.append(f"🔥 {preset_desc}（强度: {strength}）")

    if args.super_resolution:
        sr_type = args.sr_type or "lq"
        items.append(f"🔍 超分辨率（类型: {sr_type}，2倍）")

    if args.denoise:
        denoise_type = args.denoise_type or "weak"
        items.append(f"🔇 视频降噪（强度: {denoise_type}）")

    if args.color_enhance:
        color_type = args.color_enhance_type or "weak"
        items.append(f"🎨 色彩增强（强度: {color_type}）")

    if args.low_light_enhance:
        items.append("💡 低光照增强")

    if args.scratch_repair is not None:
        items.append(f"🩹 去划痕（强度: {args.scratch_repair}）")

    if args.hdr:
        items.append(f"🌈 HDR（{args.hdr}）")

    if args.frame_rate is not None:
        items.append(f"🎬 插帧（目标: {args.frame_rate}fps）")

    if args.scene_type:
        scene_desc = SCENE_TYPE_DESC.get(args.scene_type, args.scene_type)
        items.append(f"🎯 场景: {scene_desc}")

    # 音频增强
    audio_items = []
    if args.audio_denoise:
        audio_items.append("降噪")
    if args.audio_separate:
        audio_items.append(f"分离({args.audio_separate})")
    if args.volume_balance:
        vb_type = args.volume_balance_type or "loudNorm"
        audio_items.append(f"音量均衡({vb_type})")
    if args.audio_beautify:
        audio_items.append("美化")
    if audio_items:
        items.append(f"🔊 音频增强: {' + '.join(audio_items)}")

    return items


def process_media(args):
    """发起视频增强任务。"""
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
        print("✅ 视频增强任务提交成功！")
        print(f"   TaskId: {task_id}")
        print(f"   RequestId: {result.get('RequestId', 'N/A')}")

        if args.template:
            template_desc = DIFFUSION_TEMPLATE_DESC.get(args.template, f"模板 {args.template}")
            print(f"   模板: 大模型增强专用模板 {args.template}（{template_desc}）")
        elif not has_custom_params(args):
            print(f"   模板: 预设模板 {PRESET_TEMPLATE_ID}（视频增强）")
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

            enhance_items = get_enhance_summary(args)
            if enhance_items:
                print("   增强能力:")
                for item in enhance_items:
                    print(f"     {item}")

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
            print(f"\n提示：任务在后台处理中，可使用以下命令查询进度：")
            print(f"  python scripts/mps_get_video_task.py --task-id {task_id}")

        return result

    except TencentCloudSDKException as e:
        print(f"❌ 请求失败: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="腾讯云 MPS 视频增强 —— 支持大模型增强、综合增强、去毛刺等多种预设，全面提升画质体验",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # URL输入 + 默认模板（视频增强 321002），输出到 TENCENTCLOUD_COS_BUCKET/output/enhance/
  python mps_enhance.py --url https://example.com/video.mp4

  # COS路径输入（推荐，本地上传后使用）
  python mps_enhance.py --cos-input-bucket mybucket-125xxx --cos-input-region ap-guangzhou --cos-input-key /input/video/test.mp4

  # COS对象输入（bucket 和 region 自动从环境变量获取）
  python mps_enhance.py --cos-object /input/video/test.mp4

  # 大模型增强（强度 strong，效果最好）
  python mps_enhance.py --url https://example.com/video.mp4 --preset diffusion --diffusion-type strong

  # 综合增强（强度 normal，平衡效果与效率）
  python mps_enhance.py --url https://example.com/video.mp4 --preset comprehensive --comprehensive-type normal

  # 去毛刺（去伪影，强度 strong）
  python mps_enhance.py --url https://example.com/video.mp4 --preset artifact --artifact-type strong

  # 超分 + 降噪 + 色彩增强（组合使用）
  python mps_enhance.py --url https://example.com/video.mp4 --super-resolution --denoise --color-enhance

  # 老片修复场景（去划痕 + 低光照增强 + 色彩增强）
  python mps_enhance.py --url https://example.com/video.mp4 \\
      --scratch-repair 0.8 --low-light-enhance --color-enhance --scene-type LQ_material

  # 游戏视频增强（插帧到60fps + 综合增强）
  python mps_enhance.py --url https://example.com/video.mp4 \\
      --preset comprehensive --frame-rate 60 --scene-type game

  # 音频增强（降噪 + 音量均衡 + 美化）
  python mps_enhance.py --url https://example.com/video.mp4 --audio-denoise --volume-balance --audio-beautify

  # Dry Run（仅打印请求参数）
  python mps_enhance.py --url https://example.com/video.mp4 --preset diffusion --dry-run

增强预设说明（三选一，互斥）：
  diffusion      大模型增强 — 基于扩散模型的画质重建，效果最强，耗时较长
  comprehensive  综合增强   — 综合画质优化，平衡效果与效率
  artifact       去毛刺     — 针对压缩产生的毛刺/伪影进行修复

互斥约束：
  - 大模型增强、综合增强、去毛刺 三者最多开启一项
  - 大模型增强 不可与 超分（--super-resolution）同时开启
  - 大模型增强 不可与 降噪（--denoise）同时开启

增强场景说明：
  common          通用 — 适用于各种视频类型的基础优化
  AIGC            AIGC — 利用AI提升视频整体分辨率
  short_play      短剧 — 增强面部与字幕细节
  short_video     短视频 — 优化复杂多样的画质问题
  game            游戏视频 — 修复运动模糊，提升细节
  HD_movie_series 超高清影视剧 — 生成4K 60fps HDR
  LQ_material     低清素材/老片修复 — 分辨率提升与损伤修复
  lecture         秀场/电商/大会/讲座 — 美化提升面部效果

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
    output_group = parser.add_argument_group("输出配置（可选，默认输出到 TENCENTCLOUD_COS_BUCKET/output/enhance/）")
    output_group.add_argument("--output-bucket", type=str,
                              help="输出 COS Bucket 名称（默认取 TENCENTCLOUD_COS_BUCKET 环境变量）")
    output_group.add_argument("--output-region", type=str,
                              help="输出 COS Bucket 区域（默认取 TENCENTCLOUD_COS_REGION 环境变量，默认 ap-guangzhou）")
    output_group.add_argument("--output-dir", type=str,
                              help="输出目录（默认 /output/enhance/），以 / 开头和结尾")
    output_group.add_argument("--output-object-path", type=str,
                              help="输出文件路径，如 /output/{inputName}_enhance.{format}")

    # ---- 增强预设 ----
    enhance_group = parser.add_argument_group("增强预设（三选一，互斥）")
    enhance_group.add_argument("--preset", type=str,
                               choices=["diffusion", "comprehensive", "artifact"],
                               help="增强预设模式: diffusion=大模型增强 | comprehensive=综合增强 | artifact=去毛刺")
    enhance_group.add_argument("--diffusion-type", type=str, choices=["weak", "normal", "strong"],
                               help="大模型增强强度（默认 normal）")
    enhance_group.add_argument("--comprehensive-type", type=str, choices=["weak", "normal", "strong"],
                               help="综合增强强度（默认 weak）")
    enhance_group.add_argument("--artifact-type", type=str, choices=["weak", "strong"],
                               help="去毛刺强度（默认 weak）")

    # ---- 可叠加视频增强能力 ----
    video_enhance_group = parser.add_argument_group("视频增强能力（可叠加，注意互斥约束）")
    video_enhance_group.add_argument("--super-resolution", action="store_true",
                                     help="开启超分辨率（2倍）。注意不可与大模型增强同时使用")
    video_enhance_group.add_argument("--sr-type", type=str, choices=["lq", "hq"],
                                     help="超分类型: lq=低清晰度有噪声视频 | hq=高清晰度视频（默认 lq）")
    video_enhance_group.add_argument("--sr-size", type=int, choices=[2],
                                     help="超分倍数，目前仅支持 2（默认 2）")
    video_enhance_group.add_argument("--denoise", action="store_true",
                                     help="开启视频降噪。注意不可与大模型增强同时使用")
    video_enhance_group.add_argument("--denoise-type", type=str, choices=["weak", "strong"],
                                     help="降噪强度（默认 weak）")
    video_enhance_group.add_argument("--color-enhance", action="store_true",
                                     help="开启色彩增强")
    video_enhance_group.add_argument("--color-enhance-type", type=str, choices=["weak", "normal", "strong"],
                                     help="色彩增强强度（默认 weak）")
    video_enhance_group.add_argument("--low-light-enhance", action="store_true",
                                     help="开启低光照增强")
    video_enhance_group.add_argument("--scratch-repair", type=float, metavar="INTENSITY",
                                     help="开启去划痕，强度范围 0.0~1.0（如 0.5、0.8）")
    video_enhance_group.add_argument("--hdr", type=str, choices=["HDR10", "HLG"],
                                     help="开启 HDR 增强（需要 h264 或 h265 编码，编码位深 10）")
    video_enhance_group.add_argument("--frame-rate", type=int, metavar="FPS",
                                     help="开启插帧，目标帧率（Hz），如 60。源帧率>=目标帧率时不生效")
    video_enhance_group.add_argument("--scene-type", type=str,
                                     choices=["common", "AIGC", "short_play", "short_video", "game",
                                              "HD_movie_series", "LQ_material", "lecture"],
                                     help="增强场景类型（详见 epilog 说明）")

    # ---- 音频增强 ----
    audio_enhance_group = parser.add_argument_group("音频增强（可选）")
    audio_enhance_group.add_argument("--audio-denoise", action="store_true",
                                     help="开启音频降噪")
    audio_enhance_group.add_argument("--audio-separate", type=str,
                                     choices=["vocal", "background", "accompaniment"],
                                     help="音频分离: vocal=提取人声 | background=提取背景声 | accompaniment=提取伴奏")
    audio_enhance_group.add_argument("--volume-balance", action="store_true",
                                     help="开启音量均衡")
    audio_enhance_group.add_argument("--volume-balance-type", type=str, choices=["loudNorm", "gainControl"],
                                     help="音量均衡类型: loudNorm=响度标准化 | gainControl=减小突变（默认 loudNorm）")
    audio_enhance_group.add_argument("--audio-beautify", action="store_true",
                                     help="开启音频美化（杂音去除 + 齿音压制）")

    # ---- 视频转码参数 ----
    video_group = parser.add_argument_group("视频参数（可选，不指定则使用预设模板321002）")
    video_group.add_argument("--codec", type=str, choices=["h264", "h265", "h266", "av1", "vp9"],
                             help="视频编码格式（默认 h265）")
    video_group.add_argument("--width", type=int, help="视频宽度/长边（px），如 1920、1280、3840")
    video_group.add_argument("--height", type=int, help="视频高度/短边（px），0=按比例缩放")
    video_group.add_argument("--bitrate", type=int,
                             help="视频码率（kbps），0=自动。极速高清会自动优化码率")
    video_group.add_argument("--fps", type=int, help="视频帧率（Hz），0=保持原始")
    video_group.add_argument("--container", type=str, choices=["mp4", "hls", "flv"],
                             help="封装格式（默认 mp4）")

    # ---- 音频参数 ----
    audio_group = parser.add_argument_group("音频参数（可选）")
    audio_group.add_argument("--audio-codec", type=str, choices=["aac", "mp3", "copy"],
                             help="音频编码格式（默认 aac）")
    audio_group.add_argument("--audio-bitrate", type=int, help="音频码率（kbps），默认 128")

    # ---- 大模型增强专用模板 ----
    diffusion_template_group = parser.add_argument_group(
        "大模型增强专用模板（327001~327020，直接指定模板号，优先级最高）"
    )
    diffusion_template_group.add_argument(
        "--template", type=int, metavar="TEMPLATE_ID",
        help=(
            "直接指定大模型增强专用模板 ID（327001~327020），优先级高于 --preset 和其他增强参数。\n"
            "真人场景（Real，人脸与文字区域保护）：327001(720P) 327003(1080P) 327005(2K) 327007(4K)\n"
            "漫剧场景（Anime，动漫线条色块增强）：327002(720P) 327004(1080P) 327006(2K) 327008(4K)\n"
            "抖动优化（JitterOpt，减少帧间抖动）：327009(720P) 327010(1080P) 327011(2K) 327012(4K)\n"
            "细节最强（DetailMax，最大化纹理细节）：327013(720P) 327014(1080P) 327015(2K) 327016(4K)\n"
            "人脸保真（FaceFidelity，保留人脸五官）：327017(720P) 327018(1080P) 327019(2K) 327020(4K)"
        )
    )

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

    # 校验增强参数互斥约束
    validate_enhance_args(args)

    # 校验 scratch_repair 范围
    if args.scratch_repair is not None and (args.scratch_repair < 0.0 or args.scratch_repair > 1.0):
        parser.error("--scratch-repair 强度范围为 0.0~1.0")

    # 打印环境变量信息
    cos_bucket_env = get_cos_bucket()
    cos_region_env = get_cos_region()

    # 打印执行信息
    print("=" * 60)
    print("腾讯云 MPS 视频增强")
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
    # 设置输出目录，默认为 /output/enhance/
    out_dir = args.output_dir or "/output/enhance/"
    print(f"输出: COS - {out_bucket}:{out_dir} (region: {out_region})")

    if cos_bucket_env:
        print(f"COS Bucket (环境变量): {cos_bucket_env}")
    else:
        print("提示: 未设置 TENCENTCLOUD_COS_BUCKET 环境变量，COS 功能可能受限")

    if args.template:
        template_desc = DIFFUSION_TEMPLATE_DESC.get(args.template, f"模板 {args.template}")
        print(f"模板: 大模型增强专用模板 {args.template}（{template_desc}）")
    elif not has_custom_params(args):
        print(f"模板: 预设模板 {PRESET_TEMPLATE_ID}（视频增强）")
    else:
        print(f"模板: 自定义参数（基于预设模板 {PRESET_TEMPLATE_ID} 修改）")
        enhance_items = get_enhance_summary(args)
        if enhance_items:
            print("增强能力:")
            for item in enhance_items:
                print(f"  {item}")
    print("-" * 60)

    # 执行
    process_media(args)


if __name__ == "__main__":
    main()