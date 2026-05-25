#!/usr/bin/env python3
"""
腾讯云 MPS 去字幕脚本

功能：
  使用 MPS 智能擦除功能，可以自动识别视频"中下"部位的文字内容并进行无痕擦除，
  TOP视频译制、短剧出海业务首选！

  封装"去字幕/去水印/人脸模糊"API，默认使用 101 预设模板（去字幕 — 自动擦除 + 标准模型）。
  如果用户提出一些参数要求（强力擦除、字幕位置调整等），基于所选预设模板的参数修改。

  ⚠️ 重要提示：
  默认识别视频**中下部位**的字幕。如果发现字幕没擦掉，可能是字幕位置不在视频中下部位，
  需要通过 --area 或 --custom-area 参数指定字幕的实际方位。

  系统预设模板（通过 --template 指定）：
    - 101  去字幕（默认）              — 自动擦除 + 标准模型
    - 102  去字幕并提取OCR字幕         — 自动擦除 + 标准模型 + OCR提取
    - 201  去水印-高级版               — 高级水印擦除
    - 301  人脸模糊                    — 自动识别并模糊人脸
    - 302  人脸和车牌模糊              — 自动识别并模糊人脸和车牌

  擦除方式（仅去字幕模板 101/102 支持）：
    - auto（自动擦除，默认）：AI自动识别字幕并擦除，默认区域为画面中下部
    - custom（指定区域擦除）：直接对指定区域进行擦除，适合字幕位置固定的场景

  擦除模型（仅去字幕模板 101/102 支持）：
    - standard（标准模型，推荐）：细节无痕化效果更好
    - area（区域模型）：花体/阴影/动效等特殊字幕样式，擦除面积更大

  常用区域预设（通过 --position 指定，百分比坐标）：
    - fullscreen   全屏幕
    - top-half     上半屏幕
    - bottom-half  下半屏幕
    - center       屏幕中间
    - left         屏幕左边
    - right        屏幕右边

COS 存储约定：
  通过环境变量 TENCENTCLOUD_COS_BUCKET 指定 COS Bucket 名称。
  - 输入文件默认路径：{TENCENTCLOUD_COS_BUCKET}/input/   （即 COS Object 以 /input/ 开头）
  - 输出文件默认路径：{TENCENTCLOUD_COS_BUCKET}/output/erase/  （即输出目录为 /output/erase/）

  当使用 COS 输入时，如果未显式指定 --cos-bucket，自动使用 TENCENTCLOUD_COS_BUCKET。
  当未显式指定 --output-bucket，自动使用 TENCENTCLOUD_COS_BUCKET 作为输出 Bucket。
  当未显式指定 --output-dir，自动使用 /output/erase/ 作为输出目录。

用法：
  # 最简用法：使用 URL 输入 + 默认预设模板 101（自动擦除中下部字幕）
  python mps_erase.py --url https://example.com/video.mp4

  # COS路径输入（推荐，本地上传后使用）
  python mps_erase.py --cos-input-bucket mybucket-125xxx --cos-input-region ap-guangzhou --cos-input-key /input/video/test.mp4

  # COS对象输入（自动使用 TENCENTCLOUD_COS_BUCKET）
  python mps_erase.py --cos-object /input/video/test.mp4

  # 去字幕并提取OCR字幕（模板 102）
  python mps_erase.py --url https://example.com/video.mp4 --template 102

  # 去水印-高级版（模板 201）
  python mps_erase.py --url https://example.com/video.mp4 --template 201

  # 人脸模糊（模板 301）
  python mps_erase.py --url https://example.com/video.mp4 --template 301

  # 人脸和车牌模糊（模板 302）
  python mps_erase.py --url https://example.com/video.mp4 --template 302

  # 强力擦除模式（区域模型，擦除面积更大，适合花体/阴影/动效字幕）
  python mps_erase.py --url https://example.com/video.mp4 --model area

  # 字幕在视频上半屏（使用位置预设）
  python mps_erase.py --url https://example.com/video.mp4 --position top-half

  # 字幕在视频下半屏（使用位置预设）
  python mps_erase.py --url https://example.com/video.mp4 --position bottom-half

  # 字幕在视频左侧（竖排字幕场景）
  python mps_erase.py --url https://example.com/video.mp4 --position left

  # 字幕在视频右侧（竖排字幕场景）
  python mps_erase.py --url https://example.com/video.mp4 --position right

  # 字幕在视频顶部（自定义自动擦除区域：画面顶部0~25%的区域）
  python mps_erase.py --url https://example.com/video.mp4 --area 0,0,1,0.25

  # 多区域擦除（顶部 + 底部都有字幕）
  python mps_erase.py --url https://example.com/video.mp4 --area 0,0,1,0.15 --area 0,0.75,1,1

  # 指定区域擦除（字幕位置固定，指定时间段+区域直接擦除）
  python mps_erase.py --url https://example.com/video.mp4 \\
      --method custom --custom-area 0,0,0,0.8,0.99,0.95

  # 指定时间段+区域擦除（前10秒内擦除底部区域）
  python mps_erase.py --url https://example.com/video.mp4 \\
      --method custom --custom-area 0,10000,0,0.8,0.99,0.95

  # 去字幕 + OCR提取字幕文件
  python mps_erase.py --url https://example.com/video.mp4 --ocr

  # 去字幕 + OCR提取 + 翻译为英文（短剧出海场景）
  python mps_erase.py --url https://example.com/video.mp4 --ocr --translate en

  # 去字幕 + OCR提取 + 翻译为日文
  python mps_erase.py --url https://example.com/video.mp4 --ocr --translate ja

  # OCR识别多语种字幕
  python mps_erase.py --url https://example.com/video.mp4 --ocr --subtitle-lang multi

  # 输出字幕格式为 SRT
  python mps_erase.py --url https://example.com/video.mp4 --ocr --subtitle-format srt

  # Dry Run（仅打印请求参数，不实际调用 API）
  python mps_erase.py --url https://example.com/video.mp4 --dry-run

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
# 预设模板默认参数（去字幕 — 自动擦除 + 标准模型）
# =============================================================================
DEFAULT_TEMPLATE_ID = 101
PRESET_DEFAULTS = {
    "erase_method": "auto",       # 自动擦除
    "model": "standard",          # 标准模型
    "ocr_switch": "OFF",          # 不开启OCR
    "trans_switch": "OFF",        # 不开启翻译
}

# 系统预设模板说明
PRESET_TEMPLATES = {
    101: "去字幕（自动擦除 + 标准模型）",
    102: "去字幕并提取OCR字幕（中英文，VTT格式）",
    201: "去水印-高级版",
    301: "人脸模糊",
    302: "人脸和车牌模糊",
}

# 仅去字幕类模板（101/102）支持擦除方式/模型/区域/OCR等参数
SUBTITLE_TEMPLATES = {101, 102}

# 翻译目标语言说明
TRANSLATE_LANGS = {
    "zh": "简体中文",
    "en": "英语",
    "ja": "日语",
    "ko": "韩语",
    "fr": "法语",
    "es": "西班牙语",
    "it": "意大利语",
    "de": "德语",
    "tr": "土耳其语",
    "ru": "俄语",
    "pt": "葡萄牙语",
    "vi": "越南语",
    "id": "印度尼西亚语",
    "ms": "马来语",
    "th": "泰语",
    "ar": "阿拉伯语",
    "hi": "印地语",
}

# 常用区域预设（百分比坐标，Unit=1）
AREA_PRESETS = {
    "fullscreen":   {"desc": "全屏幕",   "coords": {"LeftTopX": 0.0000, "LeftTopY": 0.0000, "RightBottomX": 0.9999, "RightBottomY": 0.9999}},
    "top-half":     {"desc": "上半屏幕", "coords": {"LeftTopX": 0.0000, "LeftTopY": 0.0000, "RightBottomX": 0.9999, "RightBottomY": 0.5000}},
    "bottom-half":  {"desc": "下半屏幕", "coords": {"LeftTopX": 0.0000, "LeftTopY": 0.5000, "RightBottomX": 0.9999, "RightBottomY": 0.9999}},
    "center":       {"desc": "屏幕中间", "coords": {"LeftTopX": 0.1000, "LeftTopY": 0.3000, "RightBottomX": 0.9000, "RightBottomY": 0.7000}},
    "left":         {"desc": "屏幕左边", "coords": {"LeftTopX": 0.0000, "LeftTopY": 0.0000, "RightBottomX": 0.5000, "RightBottomY": 0.9999}},
    "right":        {"desc": "屏幕右边", "coords": {"LeftTopX": 0.5000, "LeftTopY": 0.0000, "RightBottomX": 0.9999, "RightBottomY": 0.9999}},
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


def parse_area_string(area_str):
    """
    解析区域字符串为 EraseArea 对象。

    格式：LeftTopX,LeftTopY,RightBottomX,RightBottomY
    例如：0,0.7,1,1 表示底部30%区域
    坐标为百分比值（0~1），使用百分比单位。
    """
    parts = area_str.split(",")
    if len(parts) != 4:
        print(f"错误：区域格式不正确 '{area_str}'，应为 LeftTopX,LeftTopY,RightBottomX,RightBottomY（如 0,0.7,1,1）",
              file=sys.stderr)
        sys.exit(1)
    try:
        left_top_x = float(parts[0])
        left_top_y = float(parts[1])
        right_bottom_x = float(parts[2])
        right_bottom_y = float(parts[3])
    except ValueError:
        print(f"错误：区域坐标必须为数字 '{area_str}'", file=sys.stderr)
        sys.exit(1)

    # 校验范围
    for val, name in [(left_top_x, "LeftTopX"), (left_top_y, "LeftTopY"),
                      (right_bottom_x, "RightBottomX"), (right_bottom_y, "RightBottomY")]:
        if val < 0 or val > 1:
            print(f"错误：{name} 的值 {val} 超出范围 [0, 1]", file=sys.stderr)
            sys.exit(1)

    return {
        "LeftTopX": left_top_x,
        "LeftTopY": left_top_y,
        "RightBottomX": right_bottom_x,
        "RightBottomY": right_bottom_y,
        "Unit": 1,  # 百分比单位
    }


def parse_custom_area_string(area_str):
    """
    解析自定义擦除区域字符串为 EraseTimeArea 对象。

    格式：BeginMs,EndMs,LeftTopX,LeftTopY,RightBottomX,RightBottomY
    例如：0,0,0,0.8,0.99,0.95 表示整个视频的底部区域（BeginMs=0,EndMs=0 表示全时段）
    例如：0,10000,0,0.8,0.99,0.95 表示前10秒的底部区域

    ⚠️ 注意：指定擦除区域（custom）的坐标范围为 [0, 1)（不含 1），
    这与自动擦除区域（auto）的 [0, 1] 不同。
    """
    parts = area_str.split(",")
    if len(parts) != 6:
        print(f"错误：指定区域格式不正确 '{area_str}'，"
              f"应为 BeginMs,EndMs,LeftTopX,LeftTopY,RightBottomX,RightBottomY（如 0,0,0,0.8,0.99,0.95）",
              file=sys.stderr)
        sys.exit(1)
    try:
        begin_ms = int(parts[0])
        end_ms = int(parts[1])
        left_top_x = float(parts[2])
        left_top_y = float(parts[3])
        right_bottom_x = float(parts[4])
        right_bottom_y = float(parts[5])
    except ValueError:
        print(f"错误：指定区域参数格式不正确 '{area_str}'", file=sys.stderr)
        sys.exit(1)

    # 校验范围：指定擦除区域坐标范围为 [0, 1)（不含 1）
    for val, name in [(left_top_x, "LeftTopX"), (left_top_y, "LeftTopY"),
                      (right_bottom_x, "RightBottomX"), (right_bottom_y, "RightBottomY")]:
        if val < 0 or val >= 1:
            print(f"错误：{name} 的值 {val} 超出指定擦除区域的坐标范围 [0, 1)（不含1）。"
                  f"提示：若需覆盖到画面边缘，请使用 0.99 代替 1", file=sys.stderr)
            sys.exit(1)

    return {
        "BeginMs": begin_ms,
        "EndMs": end_ms,
        "Areas": [{
            "LeftTopX": left_top_x,
            "LeftTopY": left_top_y,
            "RightBottomX": right_bottom_x,
            "RightBottomY": right_bottom_y,
            "Unit": 1,  # 百分比单位
        }],
    }


def get_template_id(args):
    """获取实际使用的模板 ID。"""
    return getattr(args, 'template', None) or DEFAULT_TEMPLATE_ID


def has_custom_params(args):
    """检测用户是否传入了任何自定义参数（需要覆盖预设模板）。"""
    return any([
        args.method is not None,
        args.model is not None,
        args.ocr,
        args.subtitle_lang is not None,
        args.subtitle_format is not None,
        args.translate is not None,
        args.area is not None and len(args.area) > 0,
        args.custom_area is not None and len(args.custom_area) > 0,
        args.position is not None,
    ])


def build_erase_subtitle_config(args):
    """
    构建去字幕配置（SmartEraseSubtitleConfig / UpdateSmartEraseSubtitleConfig）。

    基于 101 预设模板的默认值，用用户传入的参数覆盖。
    """
    config = {}

    # 擦除方式
    method = args.method or PRESET_DEFAULTS["erase_method"]
    config["SubtitleEraseMethod"] = method

    # 擦除模型
    model = args.model or PRESET_DEFAULTS["model"]
    config["SubtitleModel"] = model

    # OCR字幕提取
    if args.ocr:
        config["OcrSwitch"] = "ON"
        # 字幕语言
        config["SubtitleLang"] = args.subtitle_lang or "zh_en"
        # 字幕格式
        config["SubtitleFormat"] = args.subtitle_format or "vtt"
        # 字幕翻译
        if args.translate:
            config["TransSwitch"] = "ON"
            config["TransDstLang"] = args.translate
        else:
            config["TransSwitch"] = "OFF"
    else:
        config["OcrSwitch"] = PRESET_DEFAULTS["ocr_switch"]
        config["TransSwitch"] = PRESET_DEFAULTS["trans_switch"]

    # 自动擦除自定义区域（--area 或 --position）
    if method == "auto":
        areas = []

        # 优先使用 --position 预设
        if args.position:
            preset = AREA_PRESETS.get(args.position)
            if preset:
                coords = preset["coords"]
                areas.append({
                    "LeftTopX": coords["LeftTopX"],
                    "LeftTopY": coords["LeftTopY"],
                    "RightBottomX": coords["RightBottomX"],
                    "RightBottomY": coords["RightBottomY"],
                    "Unit": 1,
                })

        # --area 参数
        if args.area:
            for area_str in args.area:
                areas.append(parse_area_string(area_str))

        if areas:
            config["AutoAreas"] = areas

    # 指定区域擦除（--custom-area）
    if method == "custom":
        custom_areas = []
        if args.custom_area:
            for area_str in args.custom_area:
                custom_areas.append(parse_custom_area_string(area_str))
        if custom_areas:
            config["CustomAreas"] = custom_areas

    return config


def is_subtitle_template(args):
    """判断当前模板是否为去字幕类模板（支持擦除方式/模型/区域/OCR等参数）。"""
    return get_template_id(args) in SUBTITLE_TEMPLATES


def build_smart_erase_task(args):
    """
    构建智能擦除任务参数。

    策略：
    - 如果用户没有指定任何自定义参数 → 直接使用预设模板
    - 如果用户指定了自定义参数（仅去字幕模板支持）→ 使用 Definition + OverrideParameter 覆盖模板参数
    """
    task = {}
    template_id = get_template_id(args)

    if not has_custom_params(args):
        # 纯预设模板模式
        task["Definition"] = template_id
    else:
        # 覆盖模板参数模式：基于预设模板，用 OverrideParameter 覆盖
        task["Definition"] = template_id

        override = {
            "EraseType": "subtitle",
            "EraseSubtitleConfig": build_erase_subtitle_config(args),
        }
        task["OverrideParameter"] = override

    # 输出存储（可选）
    output_storage = build_output_storage(args)
    if output_storage:
        task["OutputStorage"] = output_storage

    # 输出文件路径（可选）
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

    # 输出目录：默认 /output/erase/，用户可通过 --output-dir 覆盖
    params["OutputDir"] = args.output_dir if args.output_dir else "/output/erase/"

    # 智能擦除任务（去字幕）
    smart_erase_task = build_smart_erase_task(args)
    params["SmartEraseTask"] = smart_erase_task

    # 回调配置
    if args.notify_url:
        params["TaskNotifyConfig"] = {
            "NotifyType": "URL",
            "NotifyUrl": args.notify_url,
        }

    return params


def get_erase_summary(args):
    """生成去字幕配置摘要文本。"""
    items = []

    # 擦除方式
    method = args.method or PRESET_DEFAULTS["erase_method"]
    if method == "auto":
        items.append("🔍 擦除方式: 自动擦除（AI识别字幕并擦除）")
    else:
        items.append("📐 擦除方式: 指定区域擦除（直接对指定区域擦除）")

    # 擦除模型
    model = args.model or PRESET_DEFAULTS["model"]
    if model == "standard":
        items.append("🤖 擦除模型: 标准模型（推荐，细节无痕化效果更好）")
    else:
        items.append("💪 擦除模型: 区域模型（强力擦除，适合花体/阴影/动效字幕）")

    # 字幕位置
    if args.position:
        preset = AREA_PRESETS.get(args.position, {})
        desc = preset.get("desc", args.position)
        coords = preset.get("coords", {})
        items.append(f"📍 字幕位置: {desc} — 区域 [{coords.get('LeftTopX')}, {coords.get('LeftTopY')}, {coords.get('RightBottomX')}, {coords.get('RightBottomY')}]")
    elif args.area:
        items.append(f"📍 自定义自动擦除区域: {len(args.area)} 个区域")
        for i, area_str in enumerate(args.area, 1):
            items.append(f"     区域{i}: {area_str}")
    elif method == "auto":
        items.append("📍 字幕位置: 默认（画面中下部）")

    # 指定区域
    if args.custom_area:
        items.append(f"📐 指定擦除区域: {len(args.custom_area)} 个区域")
        for i, area_str in enumerate(args.custom_area, 1):
            items.append(f"     区域{i}: {area_str}")

    # OCR
    if args.ocr:
        lang = args.subtitle_lang or "zh_en"
        fmt = args.subtitle_format or "vtt"
        items.append(f"📝 OCR字幕提取: 开启（语言: {lang}，格式: {fmt}）")

        # 翻译
        if args.translate:
            lang_desc = TRANSLATE_LANGS.get(args.translate, args.translate)
            items.append(f"🌐 字幕翻译: {lang_desc}（{args.translate}）")

    return items


def process_media(args):
    """发起去字幕任务。"""
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
        print("✅ 去字幕任务提交成功！")
        print(f"   TaskId: {task_id}")
        print(f"   RequestId: {result.get('RequestId', 'N/A')}")

        template_id = get_template_id(args)
        if not has_custom_params(args):
            print(f"   模板: 预设模板 {template_id}（{PRESET_TEMPLATES.get(template_id, '')}）")
        else:
            print(f"   模式: 自定义参数（基于预设模板 {template_id} 覆盖）")

            erase_items = get_erase_summary(args)
            if erase_items:
                print("   配置详情:")
                for item in erase_items:
                    print(f"     {item}")

        print()
        if is_subtitle_template(args):
            print("⚠️  注意：默认识别视频中下部位的字幕。如果发现字幕没擦掉，可能是字幕位置不在默认区域，")
            print("   请通过 --position 或 --area 参数指定字幕的实际方位。")

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
        description="腾讯云 MPS 智能擦除 —— 去字幕/去水印/人脸模糊，TOP视频译制、短剧出海首选",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # URL输入 + 默认模板（去字幕 101），输出到 TENCENTCLOUD_COS_BUCKET/output/erase/
  python mps_erase.py --url https://example.com/video.mp4

  # COS输入（bucket 和 region 自动从环境变量获取）
  python mps_erase.py --cos-object /input/video/test.mp4

  # 去字幕并提取OCR字幕（模板 102）
  python mps_erase.py --url https://example.com/video.mp4 --template 102

  # 去水印-高级版（模板 201）
  python mps_erase.py --url https://example.com/video.mp4 --template 201

  # 人脸模糊（模板 301）
  python mps_erase.py --url https://example.com/video.mp4 --template 301

  # 人脸和车牌模糊（模板 302）
  python mps_erase.py --url https://example.com/video.mp4 --template 302

  # 强力擦除（区域模型，适合花体/阴影/动效等特殊字幕）
  python mps_erase.py --url https://example.com/video.mp4 --model area

  # 字幕在上半屏（使用位置预设）
  python mps_erase.py --url https://example.com/video.mp4 --position top-half

  # 字幕在下半屏（使用位置预设）
  python mps_erase.py --url https://example.com/video.mp4 --position bottom-half

  # 字幕在左侧（竖排字幕）
  python mps_erase.py --url https://example.com/video.mp4 --position left

  # 字幕在右侧（竖排字幕）
  python mps_erase.py --url https://example.com/video.mp4 --position right

  # 自定义字幕区域（画面顶部0~25%区域）
  python mps_erase.py --url https://example.com/video.mp4 --area 0,0,1,0.25

  # 多区域擦除（顶部+底部都有字幕）
  python mps_erase.py --url https://example.com/video.mp4 --area 0,0,1,0.15 --area 0,0.75,1,1

  # 指定区域擦除（字幕位置固定，整个视频底部区域直接擦除）
  python mps_erase.py --url https://example.com/video.mp4 \\
      --method custom --custom-area 0,0,0,0.8,0.99,0.95

  # 指定时间段内擦除（前10秒内擦除底部区域）
  python mps_erase.py --url https://example.com/video.mp4 \\
      --method custom --custom-area 0,10000,0,0.8,0.99,0.95

  # 去字幕 + OCR提取字幕文件
  python mps_erase.py --url https://example.com/video.mp4 --ocr

  # 去字幕 + OCR提取 + 翻译为英文（短剧出海）
  python mps_erase.py --url https://example.com/video.mp4 --ocr --translate en

  # 去字幕 + OCR提取 + 翻译为日文
  python mps_erase.py --url https://example.com/video.mp4 --ocr --translate ja

  # Dry Run（仅打印请求参数）
  python mps_erase.py --url https://example.com/video.mp4 --dry-run

预设模板（--template）：
  101   去字幕（默认）              — 自动擦除 + 标准模型
  102   去字幕并提取OCR字幕         — 自动擦除 + 标准模型 + OCR提取
  201   去水印-高级版               — 高级水印擦除
  301   人脸模糊                    — 自动识别并模糊人脸
  302   人脸和车牌模糊              — 自动识别并模糊人脸和车牌

擦除方式说明（仅模板 101/102 支持）：
  auto      自动擦除（默认）— AI自动识别字幕并擦除，默认区域为画面中下部
  custom    指定区域擦除   — 直接对指定区域擦除，适合字幕位置固定的场景

擦除模型说明（仅模板 101/102 支持）：
  standard  标准模型（默认推荐）— 字幕样式标准时，细节无痕化效果更好
  area      区域模型（强力擦除）— 花体/阴影/动效等特殊字幕，擦除面积更大

区域预设（--position，仅模板 101/102 支持）：
  fullscreen   全屏幕
  top-half     上半屏幕
  bottom-half  下半屏幕
  center       屏幕中间
  left         屏幕左边
  right        屏幕右边

⚠️ 重要提示：
  默认识别视频中下部位的字幕。如果发现字幕没擦掉，可能是字幕位置不在
  视频中下部位，需要通过 --position 或 --area 指定字幕的实际方位。

翻译支持的目标语言（--translate）：
  zh=中文  en=英语  ja=日语  ko=韩语  fr=法语  es=西班牙语
  it=意大利语  de=德语  tr=土耳其语  ru=俄语  pt=葡萄牙语
  vi=越南语  id=印尼语  ms=马来语  th=泰语  ar=阿拉伯语  hi=印地语

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
    output_group = parser.add_argument_group("输出配置（可选，默认输出到 TENCENTCLOUD_COS_BUCKET/output/erase/）")
    output_group.add_argument("--output-bucket", type=str,
                              help="输出 COS Bucket 名称（默认取 TENCENTCLOUD_COS_BUCKET 环境变量）")
    output_group.add_argument("--output-region", type=str,
                              help="输出 COS Bucket 区域（默认取 TENCENTCLOUD_COS_REGION 环境变量，默认 ap-guangzhou）")
    output_group.add_argument("--output-dir", type=str,
                              help="输出目录（默认 /output/erase/），以 / 开头和结尾")
    output_group.add_argument("--output-object-path", type=str,
                              help="输出文件路径，如 /output/{inputName}_erase.{format}")

    # ---- 模板选择 ----
    template_group = parser.add_argument_group("模板选择")
    template_group.add_argument(
        "--template", type=int,
        choices=list(PRESET_TEMPLATES.keys()),
        default=DEFAULT_TEMPLATE_ID,
        metavar="TEMPLATE_ID",
        help=(
            "预设模板 ID（默认 101）。可选值："
            "101=去字幕 | "
            "102=去字幕并提取OCR字幕 | "
            "201=去水印-高级版 | "
            "301=人脸模糊 | "
            "302=人脸和车牌模糊"
        )
    )

    # ---- 擦除配置（仅模板 101/102 支持）----
    erase_group = parser.add_argument_group("擦除配置（仅去字幕模板 101/102 支持）")
    erase_group.add_argument("--method", type=str, choices=["auto", "custom"],
                             help="擦除方式: auto=自动擦除（默认，AI识别字幕） | custom=指定区域擦除")
    erase_group.add_argument("--model", type=str, choices=["standard", "area"],
                             help="擦除模型: standard=标准模型（推荐，细节更好） | "
                                  "area=区域模型（强力擦除，适合特殊字幕样式）")

    # ---- 字幕位置（仅模板 101/102 支持）----
    position_group = parser.add_argument_group(
        "字幕/擦除区域（默认为画面中下部，字幕没擦掉时需指定实际位置，仅去字幕模板 101/102 支持）")
    position_group.add_argument(
        "--position", type=str,
        choices=list(AREA_PRESETS.keys()),
        help=(
            "区域预设: "
            "fullscreen=全屏幕 | top-half=上半屏幕 | bottom-half=下半屏幕 | "
            "center=屏幕中间 | left=屏幕左边 | right=屏幕右边"
        )
    )
    position_group.add_argument("--area", type=str, action="append", metavar="X1,Y1,X2,Y2",
                                help="自动擦除自定义区域（百分比坐标 0~1）。格式: LeftTopX,LeftTopY,RightBottomX,RightBottomY。"
                                     "例如 0,0,1,0.3 表示画面顶部30%%区域。可多次指定实现多区域擦除")
    position_group.add_argument("--custom-area", type=str, action="append",
                                metavar="BEGIN,END,X1,Y1,X2,Y2",
                                help="指定擦除区域+时间段（用于 --method custom）。"
                                     "格式: BeginMs,EndMs,LeftTopX,LeftTopY,RightBottomX,RightBottomY。"
                                     "BeginMs=0,EndMs=0 表示全时段。"
                                     "例如 0,0,0,0.8,1,0.95 表示全时段擦除底部区域。可多次指定")

    # ---- OCR & 翻译（仅模板 101/102 支持）----
    ocr_group = parser.add_argument_group("OCR字幕提取 & 翻译（可选，仅去字幕模板 101/102 的自动擦除模式支持）")
    ocr_group.add_argument("--ocr", action="store_true",
                           help="开启OCR字幕提取（自动识别字幕区域文字并输出字幕文件）")
    ocr_group.add_argument("--subtitle-lang", type=str, choices=["zh_en", "multi"],
                           help="字幕语言: zh_en=中英文（默认） | multi=多语种")
    ocr_group.add_argument("--subtitle-format", type=str, choices=["srt", "vtt"],
                           help="字幕文件格式: srt | vtt（默认）")
    ocr_group.add_argument("--translate", type=str, metavar="LANG",
                           choices=list(TRANSLATE_LANGS.keys()),
                           help="开启字幕翻译并指定目标语言（需同时开启 --ocr）。"
                                "支持: zh/en/ja/ko/fr/es/it/de/tr/ru/pt/vi/id/ms/th/ar/hi")

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

    # ---- 校验 ----
    # 1. 输入源
    has_url = bool(args.url)
    has_cos_object = bool(args.cos_object)
    has_cos_path = bool(getattr(args, 'cos_input_bucket', None) and 
                        getattr(args, 'cos_input_region', None) and 
                        getattr(args, 'cos_input_key', None))
    
    if not has_url and not has_cos_object and not has_cos_path:
        parser.error("请指定输入源：--url、--cos-object 或 --cos-input-bucket/--cos-input-region/--cos-input-key")

    # 2. 非去字幕模板不支持擦除方式/模型/区域/OCR等参数
    if not is_subtitle_template(args):
        subtitle_only_params = [
            (args.method, "--method"),
            (args.model, "--model"),
            (args.ocr, "--ocr"),
            (args.subtitle_lang, "--subtitle-lang"),
            (args.subtitle_format, "--subtitle-format"),
            (args.translate, "--translate"),
            (args.area, "--area"),
            (args.custom_area, "--custom-area"),
            (args.position, "--position"),
        ]
        used = [name for val, name in subtitle_only_params if val]
        if used:
            template_id = get_template_id(args)
            parser.error(
                f"参数 {', '.join(used)} 仅支持去字幕模板（101/102），"
                f"当前模板 {template_id}（{PRESET_TEMPLATES.get(template_id, '')}）不支持这些参数"
            )

    # 3. --translate 需要 --ocr
    if args.translate and not args.ocr:
        parser.error("--translate 需要同时开启 --ocr（OCR字幕提取）")

    # 4. --subtitle-lang / --subtitle-format 需要 --ocr
    if (args.subtitle_lang or args.subtitle_format) and not args.ocr:
        parser.error("--subtitle-lang / --subtitle-format 需要同时开启 --ocr")

    # 5. --custom-area 需要 --method custom
    if args.custom_area and (args.method is None or args.method != "custom"):
        parser.error("--custom-area 需要配合 --method custom 使用")

    # 5b. 提前校验 --custom-area 坐标合法性（避免打印摘要后才报错）
    if args.custom_area:
        for area_str in args.custom_area:
            parse_custom_area_string(area_str)  # 内部校验失败会 sys.exit(1)

    # 6. --area / --position 不能与 --method custom 同时使用
    if args.method == "custom" and (args.area or args.position):
        parser.error("--area / --position 不能与 --method custom 同时使用。"
                     "指定区域擦除请使用 --custom-area")

    # 7. OCR 仅在自动擦除模式下支持
    if args.ocr and args.method == "custom":
        parser.error("OCR字幕提取仅在自动擦除模式（--method auto）下支持")

    # 打印环境变量信息
    cos_bucket_env = get_cos_bucket()
    cos_region_env = get_cos_region()

    # 打印执行信息
    template_id_display = get_template_id(args)
    template_name_display = PRESET_TEMPLATES.get(template_id_display, "")
    print("=" * 60)
    print(f"腾讯云 MPS 智能擦除 — {template_name_display}")
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
    out_dir = args.output_dir or "/output/erase/"
    print(f"输出: COS - {out_bucket}:{out_dir} (region: {out_region})")

    if cos_bucket_env:
        print(f"COS Bucket (环境变量): {cos_bucket_env}")
    else:
        print("提示: 未设置 TENCENTCLOUD_COS_BUCKET 环境变量，COS 功能可能受限")

    template_id = get_template_id(args)
    if not has_custom_params(args):
        print(f"模板: 预设模板 {template_id}（{PRESET_TEMPLATES.get(template_id, '')}）")
    else:
        print(f"模板: 自定义参数（基于预设模板 {template_id} 覆盖）")
        erase_items = get_erase_summary(args)
        if erase_items:
            print("配置详情:")
            for item in erase_items:
                print(f"  {item}")

    print()
    if is_subtitle_template(args):
        print("⚠️  提示：默认识别视频中下部位的字幕。如果发现字幕没擦掉，可能是字幕位置")
        print("   不在默认区域，请通过 --position 或 --area 指定字幕的实际方位。")
    print("-" * 60)

    # 执行
    process_media(args)


if __name__ == "__main__":
    main()