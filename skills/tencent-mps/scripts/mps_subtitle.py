#!/usr/bin/env python3
"""
腾讯云 MPS 智能字幕脚本

功能：
  使用 MPS 智能字幕功能，基于 ASR 语音识别、OCR 文字识别提取视频中的字幕，
  并支持大模型翻译为其他语言。视频译制、短剧出海、字幕提取首选！

  封装"智能字幕"API，支持三种处理模式：
    - ASR 识别字幕（默认）：通过语音识别提取字幕，支持 30+ 种源语言
    - OCR 识别字幕：通过画面文字识别提取字幕（适合硬字幕场景）
    - 纯字幕翻译：对已有字幕文件进行翻译，不做识别

  系统预设模板（推荐使用 Definition 方式，字幕具体模板 ID 以控制台为准）：
    - 110167  ASR 识别字幕（示例）

  字幕处理类型（ProcessType）：
    - 0  ASR 识别字幕（默认）— 通过语音识别提取字幕
    - 1  纯字幕翻译        — 对已有字幕文件翻译为其他语言
    - 2  OCR 识别字幕      — 通过画面文字识别提取字幕

  字幕语言类型（SubtitleType）：
    - 0  源语言字幕（默认）
    - 1  翻译语言字幕（需开启翻译）
    - 2  源语言 + 翻译语言双语字幕（需开启翻译）

COS 存储约定：
  通过环境变量 TENCENTCLOUD_COS_BUCKET 指定 COS Bucket 名称。
  - 输入文件默认路径：{TENCENTCLOUD_COS_BUCKET}/input/   （即 COS Object 以 /input/ 开头）
  - 输出文件默认路径：{TENCENTCLOUD_COS_BUCKET}/output/subtitle/  （即输出目录为 /output/subtitle/）

  当使用 COS 输入时，如果未显式指定 --cos-bucket，自动使用 TENCENTCLOUD_COS_BUCKET。
  当未显式指定 --output-bucket，自动使用 TENCENTCLOUD_COS_BUCKET 作为输出 Bucket。
  当未显式指定 --output-dir，自动使用 /output/subtitle/ 作为输出目录。

用法：
  # 最简用法：ASR 识别字幕（源语言字幕，自动识别语言）
  python mps_subtitle.py --url https://example.com/video.mp4

  # 指定视频源语言为中文
  python mps_subtitle.py --url https://example.com/video.mp4 --src-lang zh

  # ASR 识别 + 翻译为英文（双语字幕）
  python mps_subtitle.py --url https://example.com/video.mp4 --src-lang zh --translate en

  # ASR 识别 + 翻译为英文，仅输出翻译语言字幕
  python mps_subtitle.py --url https://example.com/video.mp4 --src-lang zh --translate en --subtitle-type 1

  # ASR 识别 + 同时翻译为英文和日文（多语言翻译）
  python mps_subtitle.py --url https://example.com/video.mp4 --src-lang zh --translate en/ja

  # OCR 识别字幕（适合硬字幕、花字等场景）
  python mps_subtitle.py --url https://example.com/video.mp4 --process-type ocr --src-lang zh_en

  # OCR 识别 + 翻译为英文
  python mps_subtitle.py --url https://example.com/video.mp4 --process-type ocr --src-lang zh_en --translate en

  # OCR 识别 + 自定义识别区域（底部30%区域）
  python mps_subtitle.py --url https://example.com/video.mp4 --process-type ocr --src-lang zh_en \\
      --ocr-area 0,0.7,1,1

  # 纯字幕翻译（翻译已有字幕文件）
  python mps_subtitle.py --url https://example.com/video.mp4 --process-type translate --translate en

  # 输出 SRT 格式字幕
  python mps_subtitle.py --url https://example.com/video.mp4 --subtitle-format srt

  # 使用预设模板
  python mps_subtitle.py --url https://example.com/video.mp4 --template 110167

  # COS 输入
  python mps_subtitle.py --cos-object /input/video/test.mp4

  # 自定义输出路径
  python mps_subtitle.py --url https://example.com/video.mp4 \\
      --output-object-path /output/{inputName}_subtitle.{format}

  # ASR 热词库（提升专业术语识别准确率）
  python mps_subtitle.py --url https://example.com/video.mp4 --hotwords-id hwd-xxxxx

  # Dry Run（仅打印请求参数，不实际调用 API）
  python mps_subtitle.py --url https://example.com/video.mp4 --dry-run

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
# 处理类型映射
# =============================================================================
PROCESS_TYPE_MAP = {
    "asr": 0,        # ASR 语音识别字幕
    "translate": 1,  # 纯字幕翻译
    "ocr": 2,        # OCR 文字识别字幕
}

PROCESS_TYPE_DESC = {
    0: "ASR 语音识别字幕",
    1: "纯字幕翻译",
    2: "OCR 文字识别字幕",
}

# 字幕语言类型说明
SUBTITLE_TYPE_DESC = {
    0: "源语言字幕",
    1: "翻译语言字幕",
    2: "源语言 + 翻译语言双语字幕",
}

# ASR 识别支持的常用源语言
ASR_SRC_LANGUAGES = {
    "auto": "自动识别（仅纯字幕翻译模式）",
    "zh": "简体中文",
    "en": "英语",
    "ja": "日语",
    "ko": "韩语",
    "zh-PY": "中英粤",
    "zh_medical": "中文医疗",
    "vi": "越南语",
    "ms": "马来语",
    "id": "印度尼西亚语",
    "fil": "菲律宾语",
    "th": "泰语",
    "pt": "葡萄牙语",
    "tr": "土耳其语",
    "ar": "阿拉伯语",
    "es": "西班牙语",
    "hi": "印地语",
    "fr": "法语",
    "de": "德语",
    "it": "意大利语",
    "zh_dialect": "中文方言",
    "zh_en": "中英（OCR 识别用）",
    "yue": "粤语",
    "ru": "俄语",
    "prime_zh": "中英方言",
    "multi": "其他多语种（OCR 识别用）",
}

# 翻译目标语言（常用子集，完整列表支持 200+ 种语言）
TRANSLATE_DST_LANGUAGES = {
    "zh": "简体中文",
    "zh-TW": "中文（繁体）",
    "en": "英语",
    "ja": "日语",
    "ko": "韩语",
    "fr": "法语",
    "fr-CA": "法语（加拿大）",
    "es": "西班牙语",
    "pt": "葡萄牙语",
    "pt-BR": "葡萄牙语（巴西）",
    "de": "德语",
    "it": "意大利语",
    "ru": "俄语",
    "ar": "阿拉伯语",
    "hi": "印地语",
    "th": "泰语",
    "vi": "越南语",
    "id": "印度尼西亚语",
    "ms": "马来语",
    "tr": "土耳其语",
    "nl": "荷兰语",
    "pl": "波兰语",
    "sv": "瑞典语",
    "da": "丹麦语",
    "fi": "芬兰语",
    "no": "挪威语",
    "cs": "捷克语",
    "el": "希腊语",
    "ro": "罗马尼亚语",
    "hu": "匈牙利语",
    "uk": "乌克兰语",
    "he": "希伯来语",
    "fil": "菲律宾语",
    "yue": "粤语",
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


def parse_ocr_area(area_str):
    """
    解析 OCR 区域字符串为 AutoAreas 对象。

    格式：LeftTopX,LeftTopY,RightBottomX,RightBottomY
    例如：0,0.7,1,1 表示底部30%区域
    坐标为百分比值（0~1），使用百分比单位。
    """
    parts = area_str.split(",")
    if len(parts) != 4:
        print(f"错误：OCR 区域格式不正确 '{area_str}'，应为 LeftTopX,LeftTopY,RightBottomX,RightBottomY（如 0,0.7,1,1）",
              file=sys.stderr)
        sys.exit(1)
    try:
        left_top_x = float(parts[0])
        left_top_y = float(parts[1])
        right_bottom_x = float(parts[2])
        right_bottom_y = float(parts[3])
    except ValueError:
        print(f"错误：OCR 区域坐标必须为数字 '{area_str}'", file=sys.stderr)
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


def build_raw_parameter(args):
    """
    构建 SmartSubtitlesTask 的 RawParameter。

    包含：SubtitleType, VideoSrcLanguage, SubtitleFormat, TranslateSwitch,
          TranslateDstLanguage, ProcessType, AsrHotWordsConfigure,
          SelectingSubtitleAreasConfig 等参数。
    """
    raw = {}

    # ------ 处理类型（ProcessType）------
    process_type_str = args.process_type or "asr"
    process_type = PROCESS_TYPE_MAP.get(process_type_str, 0)
    raw["ProcessType"] = process_type

    # ------ 视频源语言（VideoSrcLanguage）------
    if args.src_lang:
        raw["VideoSrcLanguage"] = args.src_lang
    else:
        # 默认源语言
        if process_type == 0:
            raw["VideoSrcLanguage"] = "zh"  # ASR 默认中文
        elif process_type == 1:
            raw["VideoSrcLanguage"] = "auto"  # 纯翻译默认自动识别
        elif process_type == 2:
            raw["VideoSrcLanguage"] = "zh_en"  # OCR 默认中英

    # ------ 翻译开关和目标语言 ------
    if args.translate:
        raw["TranslateSwitch"] = "ON"
        raw["TranslateDstLanguage"] = args.translate
    else:
        raw["TranslateSwitch"] = "OFF"

    # ------ 字幕语言类型（SubtitleType）------
    if args.subtitle_type is not None:
        raw["SubtitleType"] = args.subtitle_type
    else:
        # 自动推断
        if args.translate:
            raw["SubtitleType"] = 2  # 有翻译时默认源语言+翻译语言
        else:
            raw["SubtitleType"] = 0  # 无翻译时默认源语言

    # ------ 字幕文件格式（SubtitleFormat）------
    if args.subtitle_format:
        raw["SubtitleFormat"] = args.subtitle_format
    else:
        # 默认格式
        if process_type == 0:
            # ASR 模式：翻译多语言时必须指定格式
            if args.translate:
                raw["SubtitleFormat"] = "vtt"
            else:
                raw["SubtitleFormat"] = "vtt"  # ASR 默认 vtt
        elif process_type == 1:
            raw["SubtitleFormat"] = "original"  # 纯翻译默认与源文件一致
        elif process_type == 2:
            raw["SubtitleFormat"] = "vtt"  # OCR 默认 vtt

    # ------ ASR 热词库 ------
    if args.hotwords_id:
        raw["AsrHotWordsConfigure"] = {
            "Switch": "ON",
            "LibraryId": args.hotwords_id,
        }

    # ------ OCR 区域配置（仅 OCR 模式）------
    if process_type == 2 and args.ocr_area:
        auto_areas = []
        for area_str in args.ocr_area:
            auto_areas.append(parse_ocr_area(area_str))

        selecting_config = {
            "AutoAreas": auto_areas,
        }
        # 可选的示例视频尺寸
        if args.sample_width:
            selecting_config["SampleWidth"] = args.sample_width
        if args.sample_height:
            selecting_config["SampleHeight"] = args.sample_height

        raw["SelectingSubtitleAreasConfig"] = selecting_config

    # ------ 扩展参数 ------
    if args.ext_info:
        raw["ExtInfo"] = args.ext_info

    return raw


def build_smart_subtitles_task(args):
    """
    构建智能字幕任务参数。

    策略：
    - 如果使用 --template 指定模板 ID → 使用 Definition 模式
    - 否则 → 使用 RawParameter 自定义参数模式（Definition=0）
    """
    task = {}

    if args.template:
        # 预设模板模式
        task["Definition"] = args.template

        # 如果同时有自定义参数，也构建 RawParameter 覆盖
        if has_custom_params(args):
            task["RawParameter"] = build_raw_parameter(args)
    else:
        # 自定义参数模式（Definition=0 启用 RawParameter）
        task["Definition"] = 0
        task["RawParameter"] = build_raw_parameter(args)

    # 用户扩展字段
    if args.user_ext_para:
        task["UserExtPara"] = args.user_ext_para

    # 输出存储（任务级别）
    output_storage = build_output_storage(args)
    if output_storage:
        task["OutputStorage"] = output_storage

    # 输出文件路径
    if args.output_object_path:
        task["OutputObjectPath"] = args.output_object_path

    return task


def has_custom_params(args):
    """检测用户是否传入了任何自定义字幕参数（需要构建 RawParameter）。"""
    return any([
        args.process_type is not None,
        args.src_lang is not None,
        args.translate is not None,
        args.subtitle_type is not None,
        args.subtitle_format is not None,
        args.hotwords_id is not None,
        args.ocr_area is not None and len(args.ocr_area) > 0,
        args.ext_info is not None,
    ])


def build_request_params(args):
    """构建完整的 ProcessMedia 请求参数。"""
    params = {}

    # 输入
    params["InputInfo"] = build_input_info(args)

    # 输出存储
    output_storage = build_output_storage(args)
    if output_storage:
        params["OutputStorage"] = output_storage

    # 输出目录：默认 /output/subtitle/，用户可通过 --output-dir 覆盖
    params["OutputDir"] = args.output_dir if args.output_dir else "/output/subtitle/"

    # 智能字幕任务
    smart_subtitles_task = build_smart_subtitles_task(args)
    params["SmartSubtitlesTask"] = smart_subtitles_task

    # 回调配置
    if args.notify_url:
        params["TaskNotifyConfig"] = {
            "NotifyType": "URL",
            "NotifyUrl": args.notify_url,
        }

    return params


def get_subtitle_summary(args):
    """生成智能字幕配置摘要文本。"""
    items = []

    # 处理类型
    process_type_str = args.process_type or "asr"
    process_type = PROCESS_TYPE_MAP.get(process_type_str, 0)
    desc = PROCESS_TYPE_DESC.get(process_type, "未知")
    items.append(f"📝 处理类型: {desc}（{process_type_str}）")

    # 源语言
    src_lang = args.src_lang
    if not src_lang:
        if process_type == 0:
            src_lang = "zh"
        elif process_type == 1:
            src_lang = "auto"
        elif process_type == 2:
            src_lang = "zh_en"
    src_lang_desc = ASR_SRC_LANGUAGES.get(src_lang, src_lang)
    items.append(f"🗣️ 源语言: {src_lang_desc}（{src_lang}）")

    # 翻译
    if args.translate:
        # 支持多语言，用 / 分隔
        dst_langs = args.translate.split("/")
        lang_descs = []
        for lang in dst_langs:
            lang_desc = TRANSLATE_DST_LANGUAGES.get(lang, lang)
            lang_descs.append(f"{lang_desc}（{lang}）")
        items.append(f"🌐 翻译目标: {', '.join(lang_descs)}")
    else:
        items.append("🌐 翻译: 关闭")

    # 字幕语言类型
    subtitle_type = args.subtitle_type
    if subtitle_type is None:
        subtitle_type = 2 if args.translate else 0
    st_desc = SUBTITLE_TYPE_DESC.get(subtitle_type, "未知")
    items.append(f"📋 字幕类型: {st_desc}（SubtitleType={subtitle_type}）")

    # 字幕格式
    fmt = args.subtitle_format
    if not fmt:
        if process_type == 1:
            fmt = "original"
        else:
            fmt = "vtt"
    items.append(f"📄 字幕格式: {fmt}")

    # 热词库
    if args.hotwords_id:
        items.append(f"🔤 ASR 热词库: {args.hotwords_id}")

    # OCR 区域
    if args.ocr_area:
        items.append(f"📐 OCR 识别区域: {len(args.ocr_area)} 个区域")
        for i, area_str in enumerate(args.ocr_area, 1):
            items.append(f"     区域{i}: {area_str}")

    return items


def process_media(args):
    """发起智能字幕任务。"""
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
        print("✅ 智能字幕任务提交成功！")
        print(f"   TaskId: {task_id}")
        print(f"   RequestId: {result.get('RequestId', 'N/A')}")

        if args.template and not has_custom_params(args):
            print(f"   模板: 预设模板 {args.template}")
        else:
            process_type_str = args.process_type or "asr"
            process_type = PROCESS_TYPE_MAP.get(process_type_str, 0)
            desc = PROCESS_TYPE_DESC.get(process_type, "未知")
            print(f"   模式: 自定义参数（{desc}）")

        subtitle_items = get_subtitle_summary(args)
        if subtitle_items:
            print("   配置详情:")
            for item in subtitle_items:
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
        description="腾讯云 MPS 智能字幕 —— 基于 ASR/OCR 提取视频字幕，支持大模型翻译，视频译制、短剧出海首选",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # ASR 识别字幕（最简用法，默认中文 + VTT 格式）
  python mps_subtitle.py --url https://example.com/video.mp4

  # 指定源语言为英语
  python mps_subtitle.py --url https://example.com/video.mp4 --src-lang en

  # ASR 识别 + 翻译为英文（默认输出双语字幕）
  python mps_subtitle.py --url https://example.com/video.mp4 --src-lang zh --translate en

  # ASR 识别 + 翻译为英文，仅输出翻译字幕
  python mps_subtitle.py --url https://example.com/video.mp4 --src-lang zh --translate en --subtitle-type 1

  # ASR 识别 + 多语言翻译（英文和日文）
  python mps_subtitle.py --url https://example.com/video.mp4 --src-lang zh --translate en/ja

  # OCR 识别字幕（硬字幕场景）
  python mps_subtitle.py --url https://example.com/video.mp4 --process-type ocr --src-lang zh_en

  # OCR + 自定义区域（只识别画面底部30%区域的字幕）
  python mps_subtitle.py --url https://example.com/video.mp4 --process-type ocr --src-lang zh_en \\
      --ocr-area 0,0.7,1,1

  # OCR + 翻译为英文
  python mps_subtitle.py --url https://example.com/video.mp4 --process-type ocr --src-lang zh_en --translate en

  # 纯字幕翻译（翻译已有字幕文件，不做识别）
  python mps_subtitle.py --url https://example.com/video.mp4 --process-type translate --translate en

  # 输出 SRT 格式
  python mps_subtitle.py --url https://example.com/video.mp4 --subtitle-format srt

  # 使用预设模板（字幕模板 ID 请在控制台查看）
  python mps_subtitle.py --url https://example.com/video.mp4 --template 110167

  # ASR 热词库（提高专业术语识别准确率）
  python mps_subtitle.py --url https://example.com/video.mp4 --hotwords-id hwd-xxxxx

  # COS路径输入（推荐，本地上传后使用）
  python mps_subtitle.py --cos-input-bucket mybucket-125xxx --cos-input-region ap-guangzhou --cos-input-key /input/video/test.mp4

  # COS对象输入（自动使用环境变量）
  python mps_subtitle.py --cos-object /input/video/test.mp4

  # Dry Run（仅打印请求参数）
  python mps_subtitle.py --url https://example.com/video.mp4 --dry-run

处理类型说明（--process-type）：
  asr         ASR 语音识别字幕（默认）— 通过语音识别提取字幕
  ocr         OCR 文字识别字幕       — 通过画面文字识别提取硬字幕
  translate   纯字幕翻译             — 翻译已有字幕文件，不做识别

字幕语言类型（--subtitle-type）：
  0   源语言字幕（默认，无翻译时）
  1   翻译语言字幕
  2   源语言 + 翻译语言双语字幕（默认，有翻译时）

ASR 识别常用源语言（--src-lang）：
  zh=简体中文  en=英语  ja=日语  ko=韩语  zh-PY=中英粤
  vi=越南语  ms=马来语  id=印尼语  th=泰语  fr=法语
  de=德语  es=西班牙语  pt=葡萄牙语  ru=俄语  ar=阿拉伯语
  yue=粤语  zh_dialect=中文方言  prime_zh=中英方言

OCR 识别源语言（--src-lang）：
  zh_en=中英  multi=其他多语种

翻译目标语言（--translate，多语言用 / 分隔，如 en/ja）：
  zh=中文  en=英语  ja=日语  ko=韩语  fr=法语  es=西班牙语
  de=德语  it=意大利语  ru=俄语  pt=葡萄牙语  ar=阿拉伯语
  th=泰语  vi=越南语  id=印尼语  ms=马来语  tr=土耳其语
  nl=荷兰语  pl=波兰语  sv=瑞典语  更多语言见 API 文档

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
    output_group = parser.add_argument_group("输出配置（可选，默认输出到 TENCENTCLOUD_COS_BUCKET/output/subtitle/）")
    output_group.add_argument("--output-bucket", type=str,
                              help="输出 COS Bucket 名称（默认取 TENCENTCLOUD_COS_BUCKET 环境变量）")
    output_group.add_argument("--output-region", type=str,
                              help="输出 COS Bucket 区域（默认取 TENCENTCLOUD_COS_REGION 环境变量，默认 ap-guangzhou）")
    output_group.add_argument("--output-dir", type=str,
                              help="输出目录（默认 /output/subtitle/），以 / 开头和结尾")
    output_group.add_argument("--output-object-path", type=str,
                              help="输出字幕文件路径，如 /output/{inputName}_subtitle.{format}")

    # ---- 字幕处理类型 ----
    subtitle_group = parser.add_argument_group("字幕处理配置")
    subtitle_group.add_argument("--process-type", type=str,
                                choices=["asr", "ocr", "translate"],
                                help="字幕处理类型: asr=ASR语音识别（默认） | ocr=OCR文字识别 | "
                                     "translate=纯字幕翻译")
    subtitle_group.add_argument("--src-lang", type=str,
                                help="视频源语言。ASR 模式: zh/en/ja/ko 等（默认 zh）；"
                                     "OCR 模式: zh_en/multi（默认 zh_en）；"
                                     "纯翻译模式: auto 或指定语言（默认 auto）")
    subtitle_group.add_argument("--subtitle-type", type=int, choices=[0, 1, 2],
                                help="字幕语言类型: 0=源语言 | 1=翻译语言 | 2=源语言+翻译语言双语（默认）。"
                                     "无翻译时仅支持 0，有翻译时支持 1 或 2")
    subtitle_group.add_argument("--subtitle-format", type=str, choices=["vtt", "srt", "original"],
                                help="字幕文件格式: vtt=WebVTT（默认） | srt=SRT | "
                                     "original=与源文件一致（仅纯翻译模式）")

    # ---- 翻译 ----
    translate_group = parser.add_argument_group("翻译配置（可选，开启后默认输出双语字幕）")
    translate_group.add_argument("--translate", type=str, metavar="LANG",
                                 help="翻译目标语言，如 en/ja/ko/zh 等。"
                                      "多语言用 / 分隔，如 en/ja 表示同时翻译为英语和日语")

    # ---- ASR 配置 ----
    asr_group = parser.add_argument_group("ASR 语音识别配置（可选，仅 ASR 模式）")
    asr_group.add_argument("--hotwords-id", type=str,
                           help="ASR 热词库 ID（提高专业术语识别准确率），如 hwd-xxxxx")

    # ---- OCR 配置 ----
    ocr_group = parser.add_argument_group("OCR 文字识别配置（可选，仅 OCR 模式）")
    ocr_group.add_argument("--ocr-area", type=str, action="append", metavar="X1,Y1,X2,Y2",
                           help="OCR 识别区域（百分比坐标 0~1）。"
                                "格式: LeftTopX,LeftTopY,RightBottomX,RightBottomY。"
                                "例如 0,0.7,1,1 表示只识别画面底部30%%区域的字幕。可多次指定")
    ocr_group.add_argument("--sample-width", type=int,
                           help="示例视频/图片的宽度（像素），配合 --ocr-area 使用")
    ocr_group.add_argument("--sample-height", type=int,
                           help="示例视频/图片的高度（像素），配合 --ocr-area 使用")

    # ---- 模板 ----
    template_group = parser.add_argument_group("模板配置（可选）")
    template_group.add_argument("--template", type=int, metavar="ID",
                                help="智能字幕预设模板 ID（如 110167）。"
                                     "不指定则使用自定义参数模式（Definition=0 + RawParameter）")

    # ---- 高级 ----
    advanced_group = parser.add_argument_group("高级配置（可选）")
    advanced_group.add_argument("--user-ext-para", type=str,
                                help="用户扩展字段，一般场景不用填")
    advanced_group.add_argument("--ext-info", type=str,
                                help="自定义扩展参数（JSON 字符串）")

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

    # ---- 参数校验 ----
    # 1. 输入源
    has_url = bool(args.url)
    has_cos_object = bool(args.cos_object)
    has_cos_path = bool(getattr(args, 'cos_input_bucket', None) and 
                        getattr(args, 'cos_input_region', None) and 
                        getattr(args, 'cos_input_key', None))
    
    if not has_url and not has_cos_object and not has_cos_path:
        parser.error("请指定输入源：--url、--cos-object 或 --cos-input-bucket/--cos-input-region/--cos-input-key")

    # 2. 处理类型相关校验
    process_type_str = args.process_type or "asr"

    # 纯字幕翻译模式必须开启翻译
    if process_type_str == "translate" and not args.translate:
        parser.error("纯字幕翻译模式（--process-type translate）必须指定 --translate 目标语言")

    # 纯字幕翻译模式不支持关闭翻译时的 subtitle-type=0
    if process_type_str == "translate" and args.subtitle_type == 0:
        parser.error("纯字幕翻译模式（--process-type translate）的 --subtitle-type 不支持 0（源语言），"
                     "请使用 1（翻译语言）或 2（双语）")

    # 3. 翻译相关校验
    if not args.translate and args.subtitle_type is not None and args.subtitle_type > 0:
        parser.error("--subtitle-type 1 或 2 需要开启翻译（--translate）")

    # 4. OCR 区域仅在 OCR 模式下使用
    if args.ocr_area and process_type_str != "ocr":
        parser.error("--ocr-area 仅在 OCR 识别模式下可用（--process-type ocr）")

    # 5. 热词库仅在 ASR 模式下使用
    if args.hotwords_id and process_type_str != "asr":
        parser.error("--hotwords-id 仅在 ASR 语音识别模式下可用（--process-type asr 或默认）")

    # 6. original 格式仅在纯翻译模式下使用
    if args.subtitle_format == "original" and process_type_str != "translate":
        parser.error("字幕格式 'original' 仅在纯字幕翻译模式下可用（--process-type translate）")

    # 7. sample-width / sample-height 需要 --ocr-area
    if (args.sample_width or args.sample_height) and not args.ocr_area:
        parser.error("--sample-width / --sample-height 需要配合 --ocr-area 使用")

    # 打印环境变量信息
    cos_bucket_env = get_cos_bucket()
    cos_region_env = get_cos_region()

    # 打印执行信息
    print("=" * 60)
    print("腾讯云 MPS 智能字幕")
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
    # 设置输出目录，默认为 /output/subtitle/
    out_dir = args.output_dir or "/output/subtitle/"
    print(f"输出: COS - {out_bucket}:{out_dir} (region: {out_region})")

    if cos_bucket_env:
        print(f"COS Bucket (环境变量): {cos_bucket_env}")
    else:
        print("提示: 未设置 TENCENTCLOUD_COS_BUCKET 环境变量，COS 功能可能受限")

    if args.template and not has_custom_params(args):
        print(f"模板: 预设模板 {args.template}")
    else:
        print("模板: 自定义参数模式（Definition=0 + RawParameter）")

    # 配置摘要
    subtitle_items = get_subtitle_summary(args)
    if subtitle_items:
        print("配置详情:")
        for item in subtitle_items:
            print(f"  {item}")

    print("-" * 60)

    # 执行
    process_media(args)


if __name__ == "__main__":
    main()