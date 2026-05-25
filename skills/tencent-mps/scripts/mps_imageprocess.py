#!/usr/bin/env python3
"""
腾讯云 MPS 图片处理脚本

功能：
  使用 MPS 图片处理功能，支持图片增强、降噪、超分、美颜&加滤镜等丰富能力！

  支持的处理能力（可组合使用）：
    1. 图片编码配置（转格式）     — 格式转换（JPEG/PNG/BMP/WebP）、质量调整
    2. 图片增强配置               — 超分辨率、高级超分、降噪、综合增强、色彩增强、
                                    细节增强、人脸增强、低光照增强
    3. 图片擦除配置               — 擦除图标/文字/水印（支持自动检测和指定区域）
    4. 盲水印配置                 — 添加盲水印、提取盲水印、移除盲水印
    5. 美颜配置                   — 美白/美黑/磨皮/瘦脸/大眼/口红/美妆等20+效果
    6. 滤镜配置                   — 东京/轻胶片/美味等风格滤镜
    7. 图片基础转换能力（缩放）   — 百分比缩放、等比缩放、固定尺寸、裁剪填充

COS 存储约定：
  通过环境变量 TENCENTCLOUD_COS_BUCKET 指定 COS Bucket 名称。
  - 输入文件默认路径：{TENCENTCLOUD_COS_BUCKET}/input/
  - 输出文件默认路径：{TENCENTCLOUD_COS_BUCKET}/output/image/

用法：
  # 最简用法：仅指定输入图片（不做任何处理，用于测试连通性）
  python mps_imageprocess.py --url https://example.com/image.jpg

  # === 图片编码（转格式） ===
  # 转为 PNG 格式
  python mps_imageprocess.py --url https://example.com/image.jpg --format PNG

  # 转为 WebP 格式 + 指定质量80
  python mps_imageprocess.py --url https://example.com/image.jpg --format WebP --quality 80

  # === 图片增强 ===
  # 超分辨率（2倍放大）
  python mps_imageprocess.py --url https://example.com/image.jpg --super-resolution

  # 高级超分（指定目标宽高）
  python mps_imageprocess.py --url https://example.com/image.jpg --advanced-sr --sr-width 3840 --sr-height 2160

  # 高级超分（倍率模式，3倍放大）
  python mps_imageprocess.py --url https://example.com/image.jpg --advanced-sr --sr-percent 3.0

  # 降噪（强力）
  python mps_imageprocess.py --url https://example.com/image.jpg --denoise strong

  # 综合增强（强力）
  python mps_imageprocess.py --url https://example.com/image.jpg --quality-enhance strong

  # 色彩增强
  python mps_imageprocess.py --url https://example.com/image.jpg --color-enhance normal

  # 细节增强（强度0.8）
  python mps_imageprocess.py --url https://example.com/image.jpg --sharp-enhance 0.8

  # 人脸增强（强度0.5）
  python mps_imageprocess.py --url https://example.com/image.jpg --face-enhance 0.5

  # 低光照增强
  python mps_imageprocess.py --url https://example.com/image.jpg --lowlight-enhance

  # 组合：降噪 + 超分 + 色彩增强
  python mps_imageprocess.py --url https://example.com/image.jpg \\
      --denoise weak --super-resolution --color-enhance normal

  # === 图片擦除 ===
  # 自动检测并擦除图标和文字
  python mps_imageprocess.py --url https://example.com/image.jpg --erase-detect logo text

  # 自动检测并擦除水印
  python mps_imageprocess.py --url https://example.com/image.jpg --erase-detect watermark

  # 指定区域擦除（像素坐标）
  python mps_imageprocess.py --url https://example.com/image.jpg --erase-area 100,50,300,200

  # 指定区域擦除（百分比坐标）
  python mps_imageprocess.py --url https://example.com/image.jpg --erase-box 0.1,0.1,0.3,0.3

  # === 盲水印 ===
  # 添加盲水印
  python mps_imageprocess.py --url https://example.com/image.jpg --add-watermark "test"

  # 提取盲水印
  python mps_imageprocess.py --url https://example.com/image.jpg --extract-watermark

  # 移除盲水印
  python mps_imageprocess.py --url https://example.com/image.jpg --remove-watermark

  # === 美颜 ===
  # 美白（强度50）
  python mps_imageprocess.py --url https://example.com/image.jpg --beauty Whiten:50

  # 磨皮 + 瘦脸
  python mps_imageprocess.py --url https://example.com/image.jpg \\
      --beauty Smooth:60 --beauty BeautyThinFace:40

  # 口红（指定颜色）
  python mps_imageprocess.py --url https://example.com/image.jpg \\
      --beauty 'FaceFeatureLipsLut:50:#ff0000'

  # === 滤镜 ===
  # 轻胶片滤镜（强度70）
  python mps_imageprocess.py --url https://example.com/image.jpg --filter Qingjiaopian:70

  # === 图片缩放 ===
  # 百分比缩放（2倍放大）
  python mps_imageprocess.py --url https://example.com/image.jpg --resize-percent 2.0

  # 等比缩放到指定宽高（较小矩形）
  python mps_imageprocess.py --url https://example.com/image.jpg --resize-mode lfit --resize-width 800 --resize-height 600

  # 固定尺寸缩放
  python mps_imageprocess.py --url https://example.com/image.jpg --resize-mode fixed --resize-width 1920 --resize-height 1080

  # === 组合使用 ===
  # 降噪 + 超分 + 美颜 + 转格式
  python mps_imageprocess.py --url https://example.com/image.jpg \\
      --denoise weak --super-resolution --beauty Whiten:30 --beauty Smooth:40 \\
      --format PNG --quality 90

  # Dry Run（仅打印请求参数，不实际调用 API）
  python mps_imageprocess.py --url https://example.com/image.jpg --super-resolution --dry-run

环境变量：
  TENCENTCLOUD_SECRET_ID   - 腾讯云 SecretId
  TENCENTCLOUD_SECRET_KEY  - 腾讯云 SecretKey
  TENCENTCLOUD_COS_BUCKET       - COS Bucket 名称（如 mybucket-125xxx）
  TENCENTCLOUD_COS_REGION       - COS Bucket 区域（默认 ap-guangzhou）
"""

import argparse
import base64
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
    from poll_task import poll_image_task
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
# 美颜效果类型说明
# =============================================================================
BEAUTY_EFFECT_TYPES = {
    "Whiten": "美白",
    "BlackAlpha1": "美黑",
    "BlackAlpha2": "较强美黑",
    "FoundationAlpha2": "美白(粉白)",
    "Clear": "清晰度",
    "Sharpen": "锐化",
    "Smooth": "磨皮",
    "BeautyThinFace": "瘦脸",
    "NatureFace": "自然脸型",
    "VFace": "V脸",
    "EnlargeEye": "大眼",
    "EyeLighten": "亮眼",
    "RemoveEyeBags": "祛眼袋",
    "ThinNose": "瘦鼻",
    "RemoveLawLine": "祛法令纹",
    "CheekboneThin": "瘦颧骨",
    "FaceFeatureLipsLut": "口红",
    "ToothWhiten": "牙齿美白",
    "FaceFeatureSoftlight": "柔光",
    "Makeup": "美妆",
}

# 滤镜类型说明
FILTER_TYPES = {
    "Dongjing": "东京",
    "Qingjiaopian": "轻胶片",
    "Meiwei": "美味",
}

# 缩放模式说明
RESIZE_MODES = {
    "percent": "百分比缩放",
    "mfit": "等比缩放至较大矩形",
    "lfit": "等比缩放至较小矩形",
    "fill": "等比缩放至较大矩形并居中裁剪",
    "pad": "等比缩放至较小矩形并填充",
    "fixed": "固定宽高强制缩放",
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
                from load_env import _print_setup_hint
                _print_setup_hint(["TENCENTCLOUD_SECRET_ID", "TENCENTCLOUD_SECRET_KEY"])
            else:
                print(
                    "\n错误：TENCENTCLOUD_SECRET_ID / TENCENTCLOUD_SECRET_KEY 未设置。\n"
                    "请在 /etc/environment、~/.profile 等文件中添加这些变量后重新发起对话，\n"
                    "或直接在对话中发送变量值，由 AI 帮您配置。"
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
    构建输出存储信息（COS 类型）。

    优先级：
    1. 命令行参数 --output-bucket / --output-region
    2. 环境变量 TENCENTCLOUD_COS_BUCKET / TENCENTCLOUD_COS_REGION
    """
    # COS 类型
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


# =============================================================================
# 图片编码配置构建
# =============================================================================
def build_encode_config(args):
    """构建图片编码配置（EncodeConfig）— 格式转换和质量调整。"""
    if not args.format and args.quality is None:
        return None

    config = {}
    if args.format:
        config["Format"] = args.format
    if args.quality is not None:
        config["Quality"] = args.quality
    return config


# =============================================================================
# 图片增强配置构建
# =============================================================================
def build_enhance_config(args):
    """
    构建图片增强配置（EnhanceConfig）。

    包含：超分辨率、高级超分、降噪、综合增强、色彩增强、细节增强、人脸增强、低光照增强。
    """
    has_enhance = any([
        args.super_resolution,
        args.advanced_sr,
        args.denoise is not None,
        args.quality_enhance is not None,
        args.color_enhance is not None,
        args.sharp_enhance is not None,
        args.face_enhance is not None,
        args.lowlight_enhance,
    ])
    if not has_enhance:
        return None

    config = {}

    # 超分辨率
    if args.super_resolution:
        sr_config = {
            "Switch": "ON",
            "Type": args.sr_type or "lq",
            "Size": 2,
        }
        config["SuperResolution"] = sr_config

    # 高级超分
    if args.advanced_sr:
        adv_sr = {
            "Switch": "ON",
            "Type": args.adv_sr_type or "standard",
        }
        if args.sr_percent is not None:
            adv_sr["Mode"] = "percent"
            adv_sr["Percent"] = args.sr_percent
        elif args.sr_width is not None or args.sr_height is not None:
            if args.sr_width and args.sr_height:
                adv_sr["Mode"] = args.sr_mode or "aspect"
                adv_sr["Width"] = args.sr_width
                adv_sr["Height"] = args.sr_height
            elif args.sr_long_side or args.sr_short_side:
                adv_sr["Mode"] = args.sr_mode or "aspect"
                if args.sr_long_side:
                    adv_sr["LongSide"] = args.sr_long_side
                if args.sr_short_side:
                    adv_sr["ShortSide"] = args.sr_short_side
            else:
                adv_sr["Mode"] = args.sr_mode or "aspect"
                if args.sr_width:
                    adv_sr["Width"] = args.sr_width
                if args.sr_height:
                    adv_sr["Height"] = args.sr_height
        else:
            adv_sr["Mode"] = "percent"
            adv_sr["Percent"] = 2.0
        config["AdvancedSuperResolutionConfig"] = adv_sr

    # 降噪
    if args.denoise is not None:
        config["Denoise"] = {
            "Switch": "ON",
            "Type": args.denoise,
        }

    # 综合增强
    if args.quality_enhance is not None:
        config["ImageQualityEnhance"] = {
            "Switch": "ON",
            "Type": args.quality_enhance,
        }

    # 色彩增强
    if args.color_enhance is not None:
        config["ColorEnhance"] = {
            "Switch": "ON",
            "Type": args.color_enhance,
        }

    # 细节增强
    if args.sharp_enhance is not None:
        config["SharpEnhance"] = {
            "Switch": "ON",
            "Intensity": args.sharp_enhance,
        }

    # 人脸增强
    if args.face_enhance is not None:
        config["FaceEnhance"] = {
            "Switch": "ON",
            "Intensity": args.face_enhance,
        }

    # 低光照增强
    if args.lowlight_enhance:
        config["LowLightEnhance"] = {
            "Switch": "ON",
            "Type": "normal",
        }

    return config


# =============================================================================
# 图片擦除配置构建
# =============================================================================
def parse_erase_area(area_str, area_type="pixel"):
    """
    解析擦除区域字符串。

    pixel 格式: x1,y1,x2,y2 （像素坐标）
    ratio 格式: x1,y1,x2,y2 （百分比坐标）
    """
    parts = area_str.split(",")
    if len(parts) != 4:
        print(f"错误：擦除区域格式不正确 '{area_str}'，应为 x1,y1,x2,y2", file=sys.stderr)
        sys.exit(1)

    try:
        coords = [float(p) for p in parts]
    except ValueError:
        print(f"错误：擦除区域坐标必须为数字 '{area_str}'", file=sys.stderr)
        sys.exit(1)

    area = {}
    if area_type == "pixel":
        area["AreaCoordSet"] = [int(c) for c in coords]
    else:
        area["BoundingBox"] = coords
        area["BoundingBoxUnitType"] = 1  # 百分比单位
    return area


def build_erase_config(args):
    """构建图片擦除配置（EraseConfig）— 擦除图标/文字/水印。"""
    has_erase = any([
        args.erase_detect,
        args.erase_area,
        args.erase_box,
    ])
    if not has_erase:
        return None

    erase_logo = {"Switch": "ON"}

    # 指定擦除区域
    area_boxes = []

    # 像素坐标区域
    if args.erase_area:
        for area_str in args.erase_area:
            area = parse_erase_area(area_str, "pixel")
            area["Type"] = args.erase_area_type or "logo"
            area_boxes.append(area)

    # 百分比坐标区域
    if args.erase_box:
        for box_str in args.erase_box:
            area = parse_erase_area(box_str, "ratio")
            area["Type"] = args.erase_area_type or "logo"
            area_boxes.append(area)

    if area_boxes:
        erase_logo["ImageAreaBoxes"] = area_boxes

    # 自动检测类型
    if args.erase_detect:
        erase_logo["DetectTypes"] = args.erase_detect

    return {"ImageEraseLogo": erase_logo}


# =============================================================================
# 盲水印配置构建
# =============================================================================
def build_blind_watermark_config(args):
    """构建盲水印配置（BlindWatermarkConfig）— 添加/提取/移除盲水印。"""
    has_watermark = any([
        args.add_watermark is not None,
        args.extract_watermark,
        args.remove_watermark,
    ])
    if not has_watermark:
        return None

    config = {}

    # 添加盲水印
    if args.add_watermark is not None:
        raw_bytes = args.add_watermark.encode("utf-8")
        # 超过 4 字节时给出提醒
        if len(raw_bytes) > 4:
            truncated = raw_bytes[:4].decode("utf-8", errors="replace")
            print(
                f"⚠️  盲水印文字 '{args.add_watermark}' 的 UTF-8 编码超过 4 字节（共 {len(raw_bytes)} 字节），"
                f"将截断为前 4 字节（实际嵌入: '{truncated}'）",
                file=sys.stderr,
            )
        # 取前 4 字节；不足 4 字节则填充 0x00
        text_bytes = raw_bytes[:4].ljust(4, b'\x00')
        embed_text = base64.b64encode(text_bytes).decode("utf-8")

        config["AddBlindWatermark"] = {
            "Switch": "ON",
            "EmbedInfo": {
                "EmbedText": embed_text,
            }
        }

    # 提取盲水印
    if args.extract_watermark:
        config["ExtractBlindWatermark"] = {"Switch": "ON"}

    # 移除盲水印
    if args.remove_watermark:
        config["RemoveBlindWatermark"] = {"Switch": "ON"}

    return config


# =============================================================================
# 美颜配置构建
# =============================================================================
def parse_beauty_item(beauty_str):
    """
    解析美颜效果字符串。

    格式: Type:Value 或 Type:Value:Color
    例如: Whiten:50 或 FaceFeatureLipsLut:50:#ff0000
    """
    parts = beauty_str.split(":")
    if len(parts) < 2:
        print(f"错误：美颜效果格式不正确 '{beauty_str}'，应为 Type:Value（如 Whiten:50）", file=sys.stderr)
        sys.exit(1)

    effect_type = parts[0]
    if effect_type not in BEAUTY_EFFECT_TYPES:
        valid_types = ", ".join(BEAUTY_EFFECT_TYPES.keys())
        print(f"错误：不支持的美颜效果 '{effect_type}'。支持的类型: {valid_types}", file=sys.stderr)
        sys.exit(1)

    try:
        value = int(parts[1])
    except ValueError:
        print(f"错误：美颜效果强度必须为整数 '{parts[1]}'", file=sys.stderr)
        sys.exit(1)

    if value < 0 or value > 100:
        print(f"错误：美颜效果强度范围 [0, 100]，当前为 {value}", file=sys.stderr)
        sys.exit(1)

    item = {
        "Type": effect_type,
        "Switch": "ON",
        "Value": value,
    }

    # 可选的颜色参数（如口红颜色）
    if len(parts) >= 3:
        color = parts[2]
        item["ExtInfo"] = json.dumps({"Color": color})

    return item


def parse_filter_item(filter_str):
    """
    解析滤镜效果字符串。

    格式: Type:Value
    例如: Qingjiaopian:70
    """
    parts = filter_str.split(":")
    if len(parts) < 2:
        print(f"错误：滤镜格式不正确 '{filter_str}'，应为 Type:Value（如 Qingjiaopian:70）", file=sys.stderr)
        sys.exit(1)

    filter_type = parts[0]
    if filter_type not in FILTER_TYPES:
        valid_types = ", ".join(f"{k}({v})" for k, v in FILTER_TYPES.items())
        print(f"错误：不支持的滤镜类型 '{filter_type}'。支持的类型: {valid_types}", file=sys.stderr)
        sys.exit(1)

    try:
        value = int(parts[1])
    except ValueError:
        print(f"错误：滤镜强度必须为整数 '{parts[1]}'", file=sys.stderr)
        sys.exit(1)

    if value < -100 or value > 100:
        print(f"错误：滤镜强度范围 [-100, 100]，当前为 {value}", file=sys.stderr)
        sys.exit(1)

    return {
        "Type": filter_type,
        "Switch": "ON",
        "Value": value,
    }


def build_beauty_config(args):
    """构建美颜配置（BeautyConfig）— 美颜效果和滤镜。"""
    has_beauty = any([
        args.beauty,
        args.filter,
    ])
    if not has_beauty:
        return None

    config = {}

    # 美颜效果
    if args.beauty:
        effect_items = []
        for beauty_str in args.beauty:
            effect_items.append(parse_beauty_item(beauty_str))
        config["BeautyEffectItems"] = effect_items

    # 滤镜
    if args.filter:
        filter_items = []
        for filter_str in args.filter:
            filter_items.append(parse_filter_item(filter_str))
        config["BeautyFilterItems"] = filter_items

    return config


# =============================================================================
# 图片缩放配置构建
# =============================================================================
def build_transform_config(args):
    """构建图片基础转换配置（TransformConfig）— 缩放。"""
    has_transform = any([
        args.resize_percent is not None,
        args.resize_mode is not None,
        args.resize_width is not None,
        args.resize_height is not None,
        args.resize_long_side is not None,
        args.resize_short_side is not None,
    ])
    if not has_transform:
        return None

    resize = {"Switch": "ON"}

    if args.resize_percent is not None:
        resize["Mode"] = "percent"
        resize["Percent"] = args.resize_percent
    elif args.resize_mode:
        resize["Mode"] = args.resize_mode
        if args.resize_width:
            resize["Width"] = args.resize_width
        if args.resize_height:
            resize["Height"] = args.resize_height
        if args.resize_long_side:
            resize["LongSide"] = args.resize_long_side
        if args.resize_short_side:
            resize["ShortSide"] = args.resize_short_side
    else:
        # 仅指定了宽高但没有模式，默认 lfit
        resize["Mode"] = "lfit"
        if args.resize_width:
            resize["Width"] = args.resize_width
        if args.resize_height:
            resize["Height"] = args.resize_height
        if args.resize_long_side:
            resize["LongSide"] = args.resize_long_side
        if args.resize_short_side:
            resize["ShortSide"] = args.resize_short_side

    return {"ImageResize": resize}


# =============================================================================
# ImageTask 构建
# =============================================================================
def build_image_task(args):
    """
    构建图片处理参数（ImageTask）。

    将所有图片处理子配置组合到 ImageTask 中。
    """
    task = {}

    # 1. 图片编码配置
    encode_config = build_encode_config(args)
    if encode_config:
        task["EncodeConfig"] = encode_config

    # 2. 图片增强配置
    enhance_config = build_enhance_config(args)
    if enhance_config:
        task["EnhanceConfig"] = enhance_config

    # 3. 图片擦除配置
    erase_config = build_erase_config(args)
    if erase_config:
        task["EraseConfig"] = erase_config

    # 4. 盲水印配置
    watermark_config = build_blind_watermark_config(args)
    if watermark_config:
        task["BlindWatermarkConfig"] = watermark_config

    # 5. 美颜配置
    beauty_config = build_beauty_config(args)
    if beauty_config:
        task["BeautyConfig"] = beauty_config

    # 6. 图片缩放配置
    transform_config = build_transform_config(args)
    if transform_config:
        task["TransformConfig"] = transform_config

    return task if task else None


# =============================================================================
# 请求参数构建
# =============================================================================
def build_request_params(args):
    """构建完整的 ProcessImage 请求参数。"""
    params = {}

    # 输入
    params["InputInfo"] = build_input_info(args)

    # 输出存储
    output_storage = build_output_storage(args)
    if output_storage:
        params["OutputStorage"] = output_storage

    # 输出目录（未指定时默认使用 /output/image/）
    output_dir = args.output_dir or "/output/image/"
    params["OutputDir"] = output_dir

    # 输出路径
    if args.output_path:
        params["OutputPath"] = args.output_path

    # 图片处理参数
    image_task = build_image_task(args)
    if image_task:
        params["ImageTask"] = image_task

    # 图片处理模板（可选）
    if args.definition:
        params["Definition"] = args.definition

    # 资源 ID（可选）
    if args.resource_id:
        params["ResourceId"] = args.resource_id

    # 编排场景 ID（可选）
    if args.schedule_id:
        params["ScheduleId"] = args.schedule_id

    return params


# =============================================================================
# 配置摘要
# =============================================================================
def get_task_summary(args):
    """生成图片处理配置摘要文本。"""
    items = []

    # 编码配置
    if args.format or args.quality is not None:
        fmt = args.format or "原格式"
        quality = f"质量{args.quality}" if args.quality is not None else "原质量"
        items.append(f"🖼️  编码配置: 格式={fmt}, {quality}")

    # 增强配置
    if args.super_resolution:
        sr_type = args.sr_type or "lq"
        items.append(f"🔍 超分辨率: 2倍放大（类型: {sr_type}）")

    if args.advanced_sr:
        adv_type = args.adv_sr_type or "standard"
        if args.sr_percent is not None:
            items.append(f"🔍 高级超分: {args.sr_percent}倍放大（类型: {adv_type}）")
        elif args.sr_width or args.sr_height:
            w = args.sr_width or "自适应"
            h = args.sr_height or "自适应"
            items.append(f"🔍 高级超分: 目标 {w}x{h}（类型: {adv_type}）")
        else:
            items.append(f"🔍 高级超分: 2倍放大（类型: {adv_type}）")

    if args.denoise:
        items.append(f"🔇 降噪: {args.denoise}")

    if args.quality_enhance:
        items.append(f"✨ 综合增强: {args.quality_enhance}")

    if args.color_enhance:
        items.append(f"🎨 色彩增强: {args.color_enhance}")

    if args.sharp_enhance is not None:
        items.append(f"🔬 细节增强: 强度 {args.sharp_enhance}")

    if args.face_enhance is not None:
        items.append(f"👤 人脸增强: 强度 {args.face_enhance}")

    if args.lowlight_enhance:
        items.append("🌙 低光照增强: 已开启")

    # 擦除配置
    if args.erase_detect:
        items.append(f"🧹 自动检测擦除: {', '.join(args.erase_detect)}")
    if args.erase_area:
        items.append(f"🧹 指定区域擦除（像素）: {len(args.erase_area)} 个区域")
    if args.erase_box:
        items.append(f"🧹 指定区域擦除（百分比）: {len(args.erase_box)} 个区域")

    # 盲水印
    if args.add_watermark is not None:
        items.append(f"💧 添加盲水印: '{args.add_watermark}'")
    if args.extract_watermark:
        items.append("💧 提取盲水印: 已开启")
    if args.remove_watermark:
        items.append("💧 移除盲水印: 已开启")

    # 美颜
    if args.beauty:
        for beauty_str in args.beauty:
            parts = beauty_str.split(":")
            effect_type = parts[0]
            value = parts[1] if len(parts) > 1 else "默认"
            desc = BEAUTY_EFFECT_TYPES.get(effect_type, effect_type)
            items.append(f"💄 美颜效果: {desc}({effect_type}) 强度={value}")

    # 滤镜
    if args.filter:
        for filter_str in args.filter:
            parts = filter_str.split(":")
            filter_type = parts[0]
            value = parts[1] if len(parts) > 1 else "默认"
            desc = FILTER_TYPES.get(filter_type, filter_type)
            items.append(f"🎬 滤镜: {desc}({filter_type}) 强度={value}")

    # 缩放
    if args.resize_percent is not None:
        items.append(f"📐 缩放: {args.resize_percent}倍")
    elif args.resize_mode:
        mode_desc = RESIZE_MODES.get(args.resize_mode, args.resize_mode)
        w = args.resize_width or "自适应"
        h = args.resize_height or "自适应"
        items.append(f"📐 缩放: {mode_desc}({args.resize_mode}) → {w}x{h}")
    elif args.resize_width or args.resize_height:
        w = args.resize_width or "自适应"
        h = args.resize_height or "自适应"
        items.append(f"📐 缩放: 等比缩放 → {w}x{h}")

    return items


# =============================================================================
# 主流程
# =============================================================================
def process_image(args):
    """发起图片处理任务。"""
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
        req = models.ProcessImageRequest()
        req.from_json_string(json.dumps(params))

        resp = client.ProcessImage(req)
        result = json.loads(resp.to_json_string())

        task_id = result.get('TaskId', 'N/A')
        print("✅ 图片处理任务提交成功！")
        print(f"   TaskId: {task_id}")
        print(f"   RequestId: {result.get('RequestId', 'N/A')}")

        summary = get_task_summary(args)
        if summary:
            print("   处理详情:")
            for item in summary:
                print(f"     {item}")
        else:
            if args.definition:
                print(f"   模板: 预设模板 {args.definition}")
            else:
                print("   模式: 直接处理（未指定处理参数）")

        if args.verbose:
            print("\n完整响应：")
            print(json.dumps(result, ensure_ascii=False, indent=2))

        # 自动轮询（除非指定 --no-wait）
        no_wait = getattr(args, 'no_wait', False)
        if not no_wait and _POLL_AVAILABLE and task_id != 'N/A':
            poll_interval = getattr(args, 'poll_interval', 5)
            max_wait = getattr(args, 'max_wait', 300)
            poll_image_task(task_id, region=region, interval=poll_interval,
                            max_wait=max_wait, verbose=args.verbose)
        else:
            print(f"\n提示：任务在后台处理中，可使用以下命令查询进度：")
            print(f"  python scripts/mps_get_image_task.py --task-id {task_id}")

        return result

    except TencentCloudSDKException as e:
        print(f"❌ 请求失败: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="腾讯云 MPS 图片处理 —— 支持图片增强、降噪、超分、美颜&加滤镜等丰富能力",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # === 输入方式 ===
  # URL输入
  python mps_imageprocess.py --url https://example.com/image.jpg --format PNG
  
  # COS路径输入（推荐，本地上传后使用）
  python mps_imageprocess.py --cos-input-bucket mybucket-125xxx --cos-input-region ap-guangzhou --cos-input-key /input/image.jpg --format PNG
  
  # COS对象输入（自动使用环境变量）
  python mps_imageprocess.py --cos-object /input/image/test.jpg --format PNG

  # === 格式转换 ===
  python mps_imageprocess.py --url https://example.com/image.jpg --format PNG
  python mps_imageprocess.py --url https://example.com/image.jpg --format WebP --quality 80

  # === 图片增强 ===
  # 超分辨率（2倍放大）
  python mps_imageprocess.py --url https://example.com/image.jpg --super-resolution

  # 高级超分（指定目标尺寸）
  python mps_imageprocess.py --url https://example.com/image.jpg --advanced-sr --sr-width 3840 --sr-height 2160

  # 高级超分（倍率模式）
  python mps_imageprocess.py --url https://example.com/image.jpg --advanced-sr --sr-percent 3.0

  # 降噪 + 色彩增强
  python mps_imageprocess.py --url https://example.com/image.jpg --denoise strong --color-enhance normal

  # 低光照增强
  python mps_imageprocess.py --url https://example.com/image.jpg --lowlight-enhance

  # === 图片擦除 ===
  # 自动检测擦除图标和文字
  python mps_imageprocess.py --url https://example.com/image.jpg --erase-detect logo text

  # 自动检测擦除水印
  python mps_imageprocess.py --url https://example.com/image.jpg --erase-detect watermark

  # 指定区域擦除（像素坐标）
  python mps_imageprocess.py --url https://example.com/image.jpg --erase-area 100,50,300,200

  # 指定区域擦除（百分比坐标）
  python mps_imageprocess.py --url https://example.com/image.jpg --erase-box 0.1,0.1,0.3,0.3

  # === 盲水印 ===
  python mps_imageprocess.py --url https://example.com/image.jpg --add-watermark "test"
  python mps_imageprocess.py --url https://example.com/image.jpg --extract-watermark
  python mps_imageprocess.py --url https://example.com/image.jpg --remove-watermark

  # === 美颜 ===
  python mps_imageprocess.py --url https://example.com/image.jpg --beauty Whiten:50
  python mps_imageprocess.py --url https://example.com/image.jpg --beauty Smooth:60 --beauty BeautyThinFace:40
  python mps_imageprocess.py --url https://example.com/image.jpg --beauty 'FaceFeatureLipsLut:50:#ff0000'

  # === 滤镜 ===
  python mps_imageprocess.py --url https://example.com/image.jpg --filter Qingjiaopian:70

  # === 缩放 ===
  python mps_imageprocess.py --url https://example.com/image.jpg --resize-percent 2.0
  python mps_imageprocess.py --url https://example.com/image.jpg --resize-mode lfit --resize-width 800 --resize-height 600

  # === 组合使用 ===
  python mps_imageprocess.py --url https://example.com/image.jpg \\
      --denoise weak --super-resolution --beauty Whiten:30 --format PNG

  # Dry Run（仅打印请求参数）
  python mps_imageprocess.py --url https://example.com/image.jpg --super-resolution --dry-run

处理能力说明：
  1. 图片编码   格式转换（JPEG/PNG/BMP/WebP）、质量调整
  2. 图片增强   超分辨率、高级超分、降噪、综合增强、色彩增强、细节增强、人脸增强、低光照增强
  3. 图片擦除   擦除图标/文字/水印（支持自动检测和指定区域）
  4. 盲水印     添加/提取/移除盲水印（文本嵌入）
  5. 美颜       20+美颜效果（美白/磨皮/瘦脸/大眼/口红/美妆等）
  6. 滤镜       东京/轻胶片/美味等风格滤镜
  7. 图片缩放   百分比缩放、等比缩放、固定尺寸、裁剪填充

美颜效果类型（--beauty Type:Value）：
  Whiten=美白  BlackAlpha1=美黑  BlackAlpha2=较强美黑  FoundationAlpha2=粉白
  Clear=清晰度  Sharpen=锐化  Smooth=磨皮
  BeautyThinFace=瘦脸  NatureFace=自然脸型  VFace=V脸
  EnlargeEye=大眼  EyeLighten=亮眼  RemoveEyeBags=祛眼袋
  ThinNose=瘦鼻  RemoveLawLine=祛法令纹  CheekboneThin=瘦颧骨
  FaceFeatureLipsLut=口红  ToothWhiten=牙齿美白
  FaceFeatureSoftlight=柔光  Makeup=美妆

滤镜类型（--filter Type:Value）：
  Dongjing=东京  Qingjiaopian=轻胶片  Meiwei=美味

缩放模式（--resize-mode）：
  percent=百分比缩放  mfit=等比缩放至较大矩形  lfit=等比缩放至较小矩形
  fill=等比缩放+居中裁剪  pad=等比缩放+填充  fixed=固定宽高强制缩放

环境变量：
  TENCENTCLOUD_SECRET_ID   腾讯云 SecretId
  TENCENTCLOUD_SECRET_KEY  腾讯云 SecretKey
  TENCENTCLOUD_COS_BUCKET       COS Bucket 名称（如 mybucket-125xxx）
  TENCENTCLOUD_COS_REGION       COS Bucket 区域（默认 ap-guangzhou）
        """
    )

    # ---- 输入源 ----
    input_group = parser.add_argument_group("输入源（三选一）")
    input_group.add_argument("--url", type=str, help="图片 URL 地址")
    
    # COS 路径输入（新版，推荐）- 用于本地上传后直接使用COS路径
    input_group.add_argument("--cos-input-bucket", type=str,
                             help="输入 COS Bucket 名称（与 --cos-input-region/--cos-input-key 配合使用）")
    input_group.add_argument("--cos-input-region", type=str,
                             help="输入 COS Bucket 区域（如 ap-guangzhou）")
    input_group.add_argument("--cos-input-key", type=str,
                             help="输入 COS 对象 Key（如 /input/image.jpg）")
    
    # COS 对象输入（旧版，兼容）
    input_group.add_argument("--cos-bucket", type=str,
                             help="COS Bucket 名称（默认取 TENCENTCLOUD_COS_BUCKET 环境变量）")
    input_group.add_argument("--cos-region", type=str,
                             help="COS Bucket 区域（默认取 TENCENTCLOUD_COS_REGION 环境变量，默认 ap-guangzhou）")
    input_group.add_argument("--cos-object", type=str,
                             help="COS 对象路径，建议以 /input/ 开头，如 /input/image/test.jpg")

    # ---- 输出 ----
    output_group = parser.add_argument_group("输出配置（可选）")
    output_group.add_argument("--output-bucket", type=str,
                              help="输出 COS Bucket 名称（默认取 TENCENTCLOUD_COS_BUCKET 环境变量）")
    output_group.add_argument("--output-region", type=str,
                              help="输出 COS Bucket 区域（默认取 TENCENTCLOUD_COS_REGION 环境变量）")
    output_group.add_argument("--output-dir", type=str,
                              help="输出目录，以 / 开头和结尾（如 /output/）")
    output_group.add_argument("--output-path", type=str,
                              help="输出文件路径（如 /output/{inputName}.{format}）")

    # ---- 图片编码（转格式） ----
    encode_group = parser.add_argument_group("图片编码配置（转格式）")
    encode_group.add_argument("--format", type=str, choices=["JPEG", "PNG", "BMP", "WebP"],
                              help="输出图片格式（默认保持原格式）")
    encode_group.add_argument("--quality", type=int,
                              help="图片质量 [1-100]（默认保持原质量）")

    # ---- 图片增强 ----
    enhance_group = parser.add_argument_group("图片增强配置")
    enhance_group.add_argument("--super-resolution", action="store_true",
                               help="开启超分辨率（2倍放大）")
    enhance_group.add_argument("--sr-type", type=str, choices=["lq", "hq"],
                               help="超分类型: lq=针对低清有噪声（默认） | hq=针对高清")

    enhance_group.add_argument("--advanced-sr", action="store_true",
                               help="开启高级超分辨率")
    enhance_group.add_argument("--adv-sr-type", type=str, choices=["standard", "super", "ultra"],
                               help="高级超分类型: standard=通用（默认） | super=高级super | ultra=高级ultra")
    enhance_group.add_argument("--sr-mode", type=str, choices=["percent", "aspect", "fixed"],
                               help="高级超分输出模式: percent=倍率 | aspect=等比（默认） | fixed=固定")
    enhance_group.add_argument("--sr-percent", type=float,
                               help="高级超分倍率（配合 --sr-mode percent，如 2.0 表示2倍）")
    enhance_group.add_argument("--sr-width", type=int,
                               help="高级超分目标宽度（不超过4096）")
    enhance_group.add_argument("--sr-height", type=int,
                               help="高级超分目标高度（不超过4096）")
    enhance_group.add_argument("--sr-long-side", type=int,
                               help="高级超分目标长边（不超过4096）")
    enhance_group.add_argument("--sr-short-side", type=int,
                               help="高级超分目标短边（不超过4096）")

    enhance_group.add_argument("--denoise", type=str, choices=["weak", "strong"],
                               help="降噪: weak=轻度降噪 | strong=强力降噪")
    enhance_group.add_argument("--quality-enhance", type=str, choices=["weak", "normal", "strong"],
                               help="综合增强: weak=轻度 | normal=中度 | strong=强力")
    enhance_group.add_argument("--color-enhance", type=str, choices=["weak", "normal", "strong"],
                               help="色彩增强: weak=轻度 | normal=中度 | strong=强力")
    enhance_group.add_argument("--sharp-enhance", type=float,
                               help="细节增强强度 [0.0-1.0]")
    enhance_group.add_argument("--face-enhance", type=float,
                               help="人脸增强强度 [0.0-1.0]")
    enhance_group.add_argument("--lowlight-enhance", action="store_true",
                               help="开启低光照增强")

    # ---- 图片擦除 ----
    erase_group = parser.add_argument_group("图片擦除配置")
    erase_group.add_argument("--erase-detect", type=str, nargs="+",
                             choices=["logo", "text", "watermark"],
                             help="自动检测并擦除的类型: logo=图标 | text=文字 | watermark=水印（可多选）")
    erase_group.add_argument("--erase-area", type=str, action="append", metavar="X1,Y1,X2,Y2",
                             help="指定擦除区域（像素坐标）。格式: x1,y1,x2,y2。可多次指定")
    erase_group.add_argument("--erase-box", type=str, action="append", metavar="X1,Y1,X2,Y2",
                             help="指定擦除区域（百分比坐标 0~1）。格式: x1,y1,x2,y2。可多次指定")
    erase_group.add_argument("--erase-area-type", type=str, choices=["logo", "text"],
                             help="指定区域擦除的类型: logo=图标（默认） | text=文字")

    # ---- 盲水印 ----
    watermark_group = parser.add_argument_group("盲水印配置")
    watermark_group.add_argument("--add-watermark", type=str, metavar="TEXT",
                                 help="添加盲水印（文本，最多4字节）")
    watermark_group.add_argument("--extract-watermark", action="store_true",
                                 help="提取盲水印")
    watermark_group.add_argument("--remove-watermark", action="store_true",
                                 help="移除盲水印")

    # ---- 美颜 ----
    beauty_group = parser.add_argument_group("美颜配置")
    beauty_group.add_argument("--beauty", type=str, action="append", metavar="TYPE:VALUE",
                              help="美颜效果。格式: Type:Value（如 Whiten:50）。"
                                   "口红可附加颜色: FaceFeatureLipsLut:50:#ff0000。"
                                   "可多次指定叠加效果。强度范围 [0-100]")

    # ---- 滤镜 ----
    filter_group = parser.add_argument_group("滤镜配置")
    filter_group.add_argument("--filter", type=str, action="append", metavar="TYPE:VALUE",
                              help="滤镜效果。格式: Type:Value（如 Qingjiaopian:70）。"
                                   "类型: Dongjing=东京 | Qingjiaopian=轻胶片 | Meiwei=美味。"
                                   "强度范围 [-100, 100]")

    # ---- 图片缩放 ----
    resize_group = parser.add_argument_group("图片缩放配置")
    resize_group.add_argument("--resize-percent", type=float,
                              help="百分比缩放倍率 [0.1-10.0]（如 2.0 表示放大2倍）")
    resize_group.add_argument("--resize-mode", type=str,
                              choices=list(RESIZE_MODES.keys()),
                              help="缩放模式: percent=百分比 | mfit=等比大矩形 | lfit=等比小矩形 | "
                                   "fill=等比裁剪 | pad=等比填充 | fixed=固定尺寸")
    resize_group.add_argument("--resize-width", type=int,
                              help="目标宽度 [1-16384]")
    resize_group.add_argument("--resize-height", type=int,
                              help="目标高度 [1-16384]")
    resize_group.add_argument("--resize-long-side", type=int,
                              help="目标长边 [1-16384]（未指定宽高时使用）")
    resize_group.add_argument("--resize-short-side", type=int,
                              help="目标短边 [1-16384]（未指定宽高时使用）")

    # ---- 高级选项 ----
    advanced_group = parser.add_argument_group("高级选项")
    advanced_group.add_argument("--definition", type=int,
                                help="图片处理模板 ID（使用预设模板时指定）")
    advanced_group.add_argument("--schedule-id", type=int,
                                help="编排场景 ID（30000=文字水印擦除 | 30010=图片扩展 | 30100=换装）")
    advanced_group.add_argument("--resource-id", type=str,
                                help="资源 ID（默认为账号主资源 ID）")

    # ---- 其他 ----
    other_group = parser.add_argument_group("其他配置")
    other_group.add_argument("--region", type=str, help="MPS 服务区域（默认 ap-guangzhou）")
    other_group.add_argument("--no-wait", action="store_true",
                             help="仅提交任务，不等待结果（默认会自动轮询直到完成）")
    other_group.add_argument("--poll-interval", type=int, default=5,
                             help="轮询间隔（秒），默认 5")
    other_group.add_argument("--max-wait", type=int, default=300,
                             help="最长等待时间（秒），默认 300（5分钟）")
    other_group.add_argument("--verbose", "-v", action="store_true", help="输出详细信息")
    other_group.add_argument("--dry-run", action="store_true", help="仅打印请求参数，不实际调用 API")

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

    # 2. 质量范围
    if args.quality is not None and (args.quality < 1 or args.quality > 100):
        parser.error("--quality 范围为 [1, 100]")

    # 3. 细节增强强度范围
    if args.sharp_enhance is not None and (args.sharp_enhance < 0 or args.sharp_enhance > 1):
        parser.error("--sharp-enhance 范围为 [0.0, 1.0]")

    # 4. 人脸增强强度范围
    if args.face_enhance is not None and (args.face_enhance < 0 or args.face_enhance > 1):
        parser.error("--face-enhance 范围为 [0.0, 1.0]")

    # 5. 缩放百分比范围
    if args.resize_percent is not None and (args.resize_percent < 0.1 or args.resize_percent > 10):
        parser.error("--resize-percent 范围为 [0.1, 10.0]")

    # 6. 超分 + 高级超分互斥
    if args.super_resolution and args.advanced_sr:
        parser.error("--super-resolution 和 --advanced-sr 不能同时使用，请选择其一")

    # 7. 盲水印操作互斥
    watermark_count = sum([
        args.add_watermark is not None,
        args.extract_watermark,
        args.remove_watermark,
    ])
    if watermark_count > 1:
        parser.error("--add-watermark、--extract-watermark、--remove-watermark 不能同时使用，请选择其一")

    # 打印环境变量信息
    cos_bucket_env = get_cos_bucket()
    cos_region_env = get_cos_region()

    # 打印执行信息
    print("=" * 60)
    print("腾讯云 MPS 图片处理")
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
    # 设置输出目录，默认为 /output/image/
    out_dir = args.output_dir or "/output/image/"
    print(f"输出: COS - {out_bucket}:{out_dir} (region: {out_region})")

    if cos_bucket_env:
        print(f"COS Bucket (环境变量): {cos_bucket_env}")
    else:
        print("提示: 未设置 TENCENTCLOUD_COS_BUCKET 环境变量，COS 功能可能受限")

    # 处理摘要
    summary = get_task_summary(args)
    if summary:
        print("处理配置:")
        for item in summary:
            print(f"  {item}")
    elif args.definition:
        print(f"模板: 预设模板 {args.definition}")
    elif args.schedule_id:
        print(f"编排场景: {args.schedule_id}")
    else:
        print("⚠️  未指定任何处理参数，图片将不做处理")

    print("-" * 60)

    # 执行
    process_image(args)


if __name__ == "__main__":
    main()