#!/usr/bin/env python3
"""
腾讯云 MPS 媒体处理任务查询脚本

功能：
  通过任务 ID 查询 ProcessMedia 提交的媒体处理任务的执行状态和结果详情。
  最多可以查询 7 天之内提交的任务。

  支持查询任务的整体状态（WAITING / PROCESSING / FINISH），以及各子任务
  （转码、截图、字幕、画质增强等）的执行结果和输出文件信息。

用法：
  # 查询指定任务
  python mps_get_video_task.py --task-id 1234567890-WorkflowTask-80108cc3380155d98b2e3573a48a

  # 查询并输出完整 JSON 响应
  python mps_get_video_task.py --task-id 1234567890-WorkflowTask-80108cc3380155d98b2e3573a48a --verbose

  # 仅输出原始 JSON（方便管道处理）
  python mps_get_video_task.py --task-id 1234567890-WorkflowTask-80108cc3380155d98b2e3573a48a --json

环境变量：
  TENCENTCLOUD_SECRET_ID   - 腾讯云 SecretId
  TENCENTCLOUD_SECRET_KEY  - 腾讯云 SecretKey
"""

import argparse
import json
import os
import sys

try:
    from tencentcloud.common import credential
    from tencentcloud.common.profile.client_profile import ClientProfile
    from tencentcloud.common.profile.http_profile import HttpProfile
    from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
    from tencentcloud.mps.v20190612 import mps_client, models
except ImportError:
    print("错误：请先安装腾讯云 SDK：pip install tencentcloud-sdk-python", file=sys.stderr)
    sys.exit(1)


try:
    from qcloud_cos import CosConfig, CosS3Client
    _COS_SDK_AVAILABLE = True
except ImportError:
    _COS_SDK_AVAILABLE = False

try:
    from load_env import ensure_env_loaded as _ensure_env_loaded
    _LOAD_ENV_AVAILABLE = True
except ImportError:
    _LOAD_ENV_AVAILABLE = False
    def _ensure_env_loaded(**kwargs):
        return False

# 任务状态中文映射
STATUS_MAP = {
    "WAITING": "等待中",
    "PROCESSING": "处理中",
    "FINISH": "已完成",
    "SUCCESS": "成功",
    "FAIL": "失败",
}

# 子任务类型中文映射
TASK_TYPE_MAP = {
    "Transcode": "转码",
    "AnimatedGraphics": "转动图",
    "SnapshotByTimeOffset": "时间点截图",
    "SampleSnapshot": "采样截图",
    "ImageSprites": "雪碧图",
    "AdaptiveDynamicStreaming": "自适应码流",
    "AudioExtract": "音频分离",
    "CoverBySnapshot": "截图做封面",
    "AiAnalysis": "AI 内容分析",
    "AiRecognition": "AI 内容识别",
    "AiContentReview": "AI 内容审核",
    "AiQualityControl": "媒体质检",
    "SmartSubtitles": "智能字幕",
    "SmartErase": "智能擦除",
    "Classification": "分类",
    "Cover": "封面",
    "Cutout": "抠图",
    "DeLogo": "去台标",
    "Description": "描述",
    "Dubbing": "配音",
    "FrameTag": "帧标签",
    "HeadTail": "片头片尾",
    "Highlight": "精彩集锦",
    "HorizontalToVertical": "横转竖",
    "Reel": "智能二创",
    "Segment": "分镜拆条",
    "Tag": "标签",
    "VideoComprehension": "视频理解",
    "VideoRemake": "视频二创",
    "Face": "人脸识别",
    "Asr": "语音识别",
    "AsrFullText": "语音全文识别",
    "AsrWords": "语音分词识别",
    "Ocr": "文字识别",
    "OcrFullText": "文字全文识别",
    "OcrWords": "文字分词识别",
    "Object": "物体识别",
    "TransText": "语音翻译",
    "Porn": "涉黄审核",
    "Terrorism": "涉恐审核",
    "Political": "涉政审核",
    "Prohibited": "违禁审核",
    "PoliticalAsr": "涉政语音审核",
    "PoliticalOcr": "涉政文字审核",
    "PornAsr": "涉黄语音审核",
    "PornOcr": "涉黄文字审核",
    "ProhibitedAsr": "违禁语音审核",
    "ProhibitedOcr": "违禁文字审核",
    "TerrorismOcr": "涉恐文字审核",
}


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


def format_status(status):
    """格式化状态显示。"""
    return STATUS_MAP.get(status, status)


def _try_print_cos_presigned_url(bucket, region, out_path, indent="       "):
    """尝试为 COS 输出文件生成预签名下载链接并打印，失败时静默跳过。"""
    if not bucket or not out_path or not _COS_SDK_AVAILABLE:
        return
    try:
        cred = get_credentials()
        cos_config = CosConfig(Region=region, SecretId=cred.secret_id, SecretKey=cred.secret_key)
        cos_client = CosS3Client(cos_config)
        signed_url = cos_client.get_presigned_url(
            Bucket=bucket,
            Key=out_path.lstrip("/"),
            Method="GET",
            Expired=3600
        )
        print(f"{indent}🔗 下载链接（预签名，1小时有效）: {signed_url}")
    except Exception as e:
        print(f"{indent}⚠️  生成预签名 URL 失败: {e}")


def print_input_info(input_info):
    """打印输入文件信息。"""
    if not input_info:
        return
    input_type = input_info.get("Type", "")
    if input_type == "COS":
        cos = input_info.get("CosInputInfo", {}) or {}
        print(f"   输入: COS - {cos.get('Bucket', '')}:{cos.get('Object', '')} (region: {cos.get('Region', '')})")
    elif input_type == "URL":
        url_info = input_info.get("UrlInputInfo", {}) or {}
        print(f"   输入: URL - {url_info.get('Url', '')}")
    else:
        print(f"   输入类型: {input_type}")


def print_meta_data(meta):
    """打印媒体元信息。"""
    if not meta:
        return
    duration = meta.get("Duration", 0)
    width = meta.get("Width", 0)
    height = meta.get("Height", 0)
    bitrate = meta.get("Bitrate", 0)
    container = meta.get("Container", "")
    size = meta.get("Size", 0)
    print(f"   原始信息: {container.upper() if container else 'N/A'} | "
          f"{width}x{height} | "
          f"{bitrate // 1000 if bitrate else 0} kbps | "
          f"{duration:.1f}s | "
          f"{size / 1024 / 1024:.2f} MB")


def print_media_process_results(result_set):
    """打印媒体处理子任务结果。"""
    if not result_set:
        print("   子任务: 无")
        return

    for i, item in enumerate(result_set, 1):
        task_type = item.get("Type", "")
        type_name = TASK_TYPE_MAP.get(task_type, task_type)

        # 根据类型取对应的任务详情字段
        task_key_map = {
            "Transcode": "TranscodeTask",
            "AnimatedGraphics": "AnimatedGraphicsTask",
            "SnapshotByTimeOffset": "SnapshotByTimeOffsetTask",
            "SampleSnapshot": "SampleSnapshotTask",
            "ImageSprites": "ImageSpritesTask",
            "AdaptiveDynamicStreaming": "AdaptiveDynamicStreamingTask",
            "AudioExtract": "AudioExtractTask",
            "CoverBySnapshot": "CoverBySnapshotTask",
        }
        task_key = task_key_map.get(task_type, "")
        task_detail = item.get(task_key, {}) if task_key else None

        if task_detail:
            status = task_detail.get("Status", "")
            err_code = task_detail.get("ErrCode") or 0
            message = task_detail.get("Message", "")
            progress = task_detail.get("Progress", None)

            status_str = format_status(status)
            progress_str = f" ({progress}%)" if progress is not None else ""
            err_str = f" | 错误码: {err_code} - {message}" if err_code != 0 else ""

            print(f"   [{i}] {type_name}: {status_str}{progress_str}{err_str}")

            # 打印输出文件信息
            output = task_detail.get("Output", {})
            if output:
                out_storage = output.get("OutputStorage", {}) or {}
                out_path = output.get("Path", "")
                out_type = out_storage.get("Type", "")
                if out_type == "COS":
                    cos_out = out_storage.get("CosOutputStorage", {}) or {}
                    bucket = cos_out.get("Bucket", "")
                    region = cos_out.get("Region", "")
                    print(f"       输出: COS - {bucket}:{out_path} (region: {region})")
                    _try_print_cos_presigned_url(bucket, region, out_path)
                elif out_path:
                    print(f"       输出: {out_path}")

                # 打印输出视频信息
                out_width = output.get("Width", 0)
                out_height = output.get("Height", 0)
                out_bitrate = output.get("Bitrate", 0)
                out_duration = output.get("Duration", 0)
                out_size = output.get("Size", 0)
                out_container = output.get("Container", "")
                if out_width or out_height:
                    print(f"       规格: {out_container.upper() if out_container else 'N/A'} | "
                          f"{out_width}x{out_height} | "
                          f"{out_bitrate // 1000 if out_bitrate else 0} kbps | "
                          f"{out_duration:.1f}s | "
                          f"{out_size / 1024 / 1024:.2f} MB")
        else:
            print(f"   [{i}] {type_name}: 无详情")


def print_ai_analysis_results(result_set):
    """打印 AI 内容分析任务结果，包含错误检测。"""
    if not result_set:
        return

    for i, item in enumerate(result_set, 1):
        task_type = item.get("Type", "")
        # 根据类型获取对应的任务详情
        task_key_map = {
            "Classification": "ClassificationTask",
            "Cover": "CoverTask",
            "Tag": "TagTask",
            "FrameTag": "FrameTagTask",
            "Highlight": "HighlightTask",
            "DeLogo": "DeLogoTask",
            "Description": "DescriptionTask",
            "Dubbing": "DubbingTask",
            "VideoRemake": "VideoRemakeTask",
            "VideoComprehension": "VideoComprehensionTask",
            "Cutout": "CutoutTask",
            "Reel": "ReelTask",
            "HeadTail": "HeadTailTask",
            "HorizontalToVertical": "HorizontalToVerticalTask",
            "Segment": "SegmentTask",
        }
        task_key = task_key_map.get(task_type, "")
        task_detail = item.get(task_key, {}) if task_key else None

        if task_detail:
            status = task_detail.get("Status", "")
            err_code = task_detail.get("ErrCode") or 0
            err_code_ext = task_detail.get("ErrCodeExt", "")
            message = task_detail.get("Message", "")

            status_str = format_status(status)
            err_str = ""
            if err_code != 0:
                err_str = f" | 错误码: {err_code}"
            if err_code_ext:
                err_str += f" ({err_code_ext})"
            if message and message != "SUCCESS":
                err_str += f" - {message}"

            print(f"   [{i}] AI分析-{task_type}: {status_str}{err_str}")

            # 打印分析输出信息
            output = task_detail.get("Output", {})
            if output:
                # 分类结果
                classifications = output.get("Classifications", [])
                if classifications:
                    print(f"       分类结果:")
                    for cls in classifications[:5]:  # 最多显示5个
                        name = cls.get("Name", "")
                        conf = cls.get("Confidence", 0)
                        print(f"         - {name} ({conf * 100:.1f}%)")

                # 标签
                tags = output.get("Tags", [])
                if tags:
                    print(f"       标签: {', '.join(tags[:10])}")  # 最多显示10个标签

                # 封面
                cover_path = output.get("CoverPath", "")
                if cover_path:
                    print(f"       封面: {cover_path}")

                # 描述
                description = output.get("Description", "")
                if description:
                    print(f"       描述: {description[:100]}{'...' if len(description) > 100 else ''}")

                # 精彩片段
                highlights = output.get("Highlights", [])
                if highlights:
                    print(f"       精彩片段:")
                    for hl in highlights[:3]:  # 最多显示3个
                        start = hl.get("StartTime", 0)
                        end = hl.get("EndTime", 0)
                        conf = hl.get("Confidence", 0)
                        print(f"         - {start}s - {end}s (置信度: {conf * 100:.1f}%)")
        else:
            print(f"   [{i}] AI分析-{task_type}: 无详情")


def print_ai_recognition_results(result_set):
    """打印 AI 内容识别任务结果，包含错误检测。"""
    if not result_set:
        return

    for i, item in enumerate(result_set, 1):
        task_type = item.get("Type", "")
        # 根据类型获取对应的任务详情
        task_key_map = {
            "Face": "FaceTask",
            "Asr": "AsrTask",
            "Ocr": "OcrTask",
            "Object": "ObjectTask",
            "AsrWords": "AsrWordsTask",
            "OcrWords": "OcrWordsTask",
            "TransText": "TransTextTask",
        }
        task_key = task_key_map.get(task_type, "")
        task_detail = item.get(task_key, {}) if task_key else None

        if task_detail:
            status = task_detail.get("Status", "")
            err_code = task_detail.get("ErrCode") or 0
            err_code_ext = task_detail.get("ErrCodeExt", "")
            message = task_detail.get("Message", "")

            status_str = format_status(status)
            err_str = ""
            if err_code != 0:
                err_str = f" | 错误码: {err_code}"
            if err_code_ext:
                err_str += f" ({err_code_ext})"
            if message and message != "SUCCESS":
                err_str += f" - {message}"

            print(f"   [{i}] AI识别-{task_type}: {status_str}{err_str}")

            # 打印识别输出信息
            output = task_detail.get("Output", {})
            if output:
                # 人脸识别
                if task_type == "Face":
                    face_set = output.get("FaceSet", [])
                    if face_set:
                        print(f"       识别到 {len(face_set)} 个人脸:")
                        for face in face_set[:5]:  # 最多显示5个
                            name = face.get("Name", "未知")
                            conf = face.get("Confidence", 0)
                            print(f"         - {name} ({conf * 100:.1f}%)")

                # 语音识别
                elif task_type == "Asr":
                    subtitle_path = output.get("SubtitlePath", "")
                    if subtitle_path:
                        print(f"       字幕文件: {subtitle_path}")

                # 文字识别
                elif task_type == "Ocr":
                    text_set = output.get("TextSet", [])
                    if text_set:
                        print(f"       识别到 {len(text_set)} 个文本框")

                # 物体识别
                elif task_type == "Object":
                    object_set = output.get("ObjectSet", [])
                    if object_set:
                        print(f"       识别到 {len(object_set)} 个物体:")
                        for obj in object_set[:5]:  # 最多显示5个
                            name = obj.get("Name", "")
                            conf = obj.get("Confidence", 0)
                            print(f"         - {name} ({conf * 100:.1f}%)")

                # 语音翻译
                elif task_type == "TransText":
                    subtitle_path = output.get("SubtitlePath", "")
                    if subtitle_path:
                        print(f"       翻译字幕文件: {subtitle_path}")
        else:
            print(f"   [{i}] AI识别-{task_type}: 无详情")


def print_ai_content_review_results(result_set):
    """打印 AI 内容审核任务结果，包含错误检测。"""
    if not result_set:
        return

    for i, item in enumerate(result_set, 1):
        task_type = item.get("Type", "")
        # 根据类型获取对应的任务详情
        task_key_map = {
            "Porn": "PornTask",
            "Terrorism": "TerrorismTask",
            "Political": "PoliticalTask",
            "Prohibited": "ProhibitedTask",
            "PoliticalAsr": "PoliticalAsrTask",
            "PoliticalOcr": "PoliticalOcrTask",
            "PornAsr": "PornAsrTask",
            "PornOcr": "PornOcrTask",
            "ProhibitedAsr": "ProhibitedAsrTask",
            "ProhibitedOcr": "ProhibitedOcrTask",
            "TerrorismOcr": "TerrorismOcrTask",
        }
        task_key = task_key_map.get(task_type, "")
        task_detail = item.get(task_key, {}) if task_key else None

        if task_detail:
            status = task_detail.get("Status", "")
            err_code = task_detail.get("ErrCode") or 0
            err_code_ext = task_detail.get("ErrCodeExt", "")
            message = task_detail.get("Message", "")

            status_str = format_status(status)
            err_str = ""
            if err_code != 0:
                err_str = f" | 错误码: {err_code}"
            if err_code_ext:
                err_str += f" ({err_code_ext})"
            if message and message != "SUCCESS":
                err_str += f" - {message}"

            print(f"   [{i}] AI审核-{task_type}: {status_str}{err_str}")

            # 打印审核输出信息
            output = task_detail.get("Output", {})
            if output:
                suggestion = output.get("Suggestion", "")
                label = output.get("Label", "")
                confidence = output.get("Confidence", 0)

                if suggestion:
                    suggestion_map = {
                        "pass": "通过",
                        "review": "复核",
                        "block": "拦截"
                    }
                    sug_text = suggestion_map.get(suggestion, suggestion)
                    print(f"       建议: {sug_text}")
                if label:
                    print(f"       标签: {label}")
                if confidence:
                    print(f"       置信度: {confidence * 100:.1f}%")
        else:
            print(f"   [{i}] AI审核-{task_type}: 无详情")


def print_ai_quality_control_result(result):
    """打印 AI 媒体质检任务结果，包含错误检测。"""
    if not result:
        return

    status = result.get("Status", "")
    err_code = result.get("ErrCode") or 0
    err_code_ext = result.get("ErrCodeExt", "")
    message = result.get("Message", "")

    status_str = format_status(status)
    err_str = ""
    if err_code != 0:
        err_str = f" | 错误码: {err_code}"
    if err_code_ext:
        err_str += f" ({err_code_ext})"
    if message and message != "SUCCESS":
        err_str += f" - {message}"

    print(f"   AI质检: {status_str}{err_str}")

    # 获取输出信息
    output = result.get("Output", {})

    # 检查是否缺失音视频
    no_audio = output.get("NoAudio", False)
    no_video = output.get("NoVideo", False)
    if no_audio or no_video:
        issues = []
        if no_audio:
            issues.append("缺失音频")
        if no_video:
            issues.append("缺失视频")
        print(f"   ⚠️  {', '.join(issues)}")

    # 质量评分
    score = output.get("QualityEvaluationScore")
    if score is not None:
        print(f"   质量评分: {score}")

    # 检查容器诊断结果
    diagnose_results = output.get("ContainerDiagnoseResultSet", [])
    if diagnose_results:
        has_fatal = False
        has_warning = False

        print(f"   质检诊断结果：")
        for diagnose in diagnose_results:
            category = diagnose.get("Category", "")
            type_name = diagnose.get("Type", "")
            severity = diagnose.get("SeverityLevel", "")

            # 根据严重级别输出
            if severity == "Fatal":
                has_fatal = True
                print(f"       ❌ 【致命】{category}/{type_name}")
            elif severity == "Warning":
                has_warning = True
                print(f"       ⚠️  【警告】{category}/{type_name}")
            else:
                print(f"       ℹ️  【{severity}】{category}/{type_name}")

            # 输出时间戳（如果有）
            timestamps = diagnose.get("TimestampSet", [])
            if timestamps:
                print(f"          时间点: {', '.join(map(str, timestamps))} 秒")

        # 如果有致命错误，在开头标记任务失败
        if has_fatal and status_str == "已完成":
            print(f"   ⚠️  质检检测到致命错误，任务状态应为失败")

    # 检查质检统计信息
    qc_stats = output.get("QualityControlStatSet", [])
    if qc_stats:
        print(f"   质检统计：")
        for stat in qc_stats:
            stat_type = stat.get("Type", "")
            avg_val = stat.get("AvgValue", 0)
            max_val = stat.get("MaxValue", 0)
            min_val = stat.get("MinValue", 0)

            # 只输出有意义的统计数据（非零值）
            if max_val > 0 or avg_val > 0:
                print(f"       {stat_type}: 平均={avg_val}, 最大={max_val}, 最小={min_val}")


def print_smart_subtitles_results(result_set):
    """打印智能字幕任务结果，包含错误检测。"""
    if not result_set:
        return

    for i, item in enumerate(result_set, 1):
        task_type = item.get("Type", "")
        task_key_map = {
            "AsrFullText": "AsrFullTextTask",
            "TransText": "TransTextTask",
            "PureSubtitleTrans": "PureSubtitleTransTask",
            "OcrFullText": "OcrFullTextTask",
        }
        task_key = task_key_map.get(task_type, "")
        task_detail = item.get(task_key, {}) if task_key else None

        if task_detail:
            status = task_detail.get("Status", "")
            err_code = task_detail.get("ErrCode") or 0
            err_code_ext = task_detail.get("ErrCodeExt", "")
            message = task_detail.get("Message", "")

            status_str = format_status(status)
            err_str = ""
            if err_code != 0:
                err_str = f" | 错误码: {err_code}"
            if err_code_ext:
                err_str += f" ({err_code_ext})"
            if message and message != "SUCCESS":
                err_str += f" - {message}"

            print(f"   [{i}] 智能字幕-{task_type}: {status_str}{err_str}")

            # 检查字幕结果中的错误
            output = task_detail.get("Output", {})
            if output:
                # TransTextTask 的字幕结果
                subtitle_results = output.get("SubtitleResults", [])
                for j, sub in enumerate(subtitle_results, 1):
                    sub_status = sub.get("Status", "")
                    sub_err = sub.get("ErrCode") or 0
                    sub_err_ext = sub.get("ErrCodeExt", "")
                    sub_msg = sub.get("Message", "")
                    if sub_err != 0 or sub_status == "FAIL":
                        err_info = f"错误码: {sub_err}"
                        if sub_err_ext:
                            err_info += f" ({sub_err_ext})"
                        if sub_msg:
                            err_info += f" - {sub_msg}"
                        print(f"       字幕结果[{j}]: {format_status(sub_status)} | {err_info}")

                # OcrFullTextTask 的识别结果
                recognize_results = output.get("RecognizeSubtitleResult", [])
                for j, rec in enumerate(recognize_results, 1):
                    rec_status = rec.get("Status", "")
                    rec_err = rec.get("ErrCode") or 0
                    rec_err_ext = rec.get("ErrCodeExt", "")
                    rec_msg = rec.get("Message", "")
                    if rec_err != 0 or rec_status == "FAIL":
                        err_info = f"错误码: {rec_err}"
                        if rec_err_ext:
                            err_info += f" ({rec_err_ext})"
                        if rec_msg:
                            err_info += f" - {rec_msg}"
                        print(f"       OCR识别结果[{j}]: {format_status(rec_status)} | {err_info}")

                # OcrFullTextTask 的翻译结果
                trans_results = output.get("TransSubtitleResult", [])
                for j, trans in enumerate(trans_results, 1):
                    trans_status = trans.get("Status", "")
                    trans_err = trans.get("ErrCode") or 0
                    trans_err_ext = trans.get("ErrCodeExt", "")
                    trans_msg = trans.get("Message", "")
                    if trans_err != 0 or trans_status == "FAIL":
                        err_info = f"错误码: {trans_err}"
                        if trans_err_ext:
                            err_info += f" ({trans_err_ext})"
                        if trans_msg:
                            err_info += f" - {trans_msg}"
                        print(f"       字幕翻译结果[{j}]: {format_status(trans_status)} | {err_info}")
        else:
            print(f"   [{i}] 智能字幕-{task_type}: 无详情")


def print_smart_erase_result(result):
    """打印智能擦除任务结果，包含错误检测。"""
    if not result:
        return

    status = result.get("Status", "")
    err_code = result.get("ErrCode") or 0
    message = result.get("Message", "")

    status_str = format_status(status)
    err_str = ""
    if err_code != 0:
        err_str = f" | 错误码: {err_code}"
    if message and message != "SUCCESS":
        err_str += f" - {message}"

    print(f"   智能擦除: {status_str}{err_str}")


def print_edit_media_task(task):
    """打印视频编辑任务结果，包含错误检测。"""
    if not task:
        return

    status = task.get("Status", "")
    err_code = task.get("ErrCode") or 0
    message = task.get("Message", "")

    status_str = format_status(status)
    err_str = ""
    if err_code != 0:
        err_str = f" | 错误码: {err_code}"
    if message and message != "SUCCESS":
        err_str += f" - {message}"

    print(f"   视频编辑: {status_str}{err_str}")

    # 输入信息
    print_input_info(task.get("InputInfo"))

    # 输出信息
    output = task.get("Output", {})
    if output:
        out_storage = output.get("OutputStorage", {}) or {}
        out_path = output.get("Path", "")
        out_type = out_storage.get("Type", "")
        if out_type == "COS":
            cos_out = out_storage.get("CosOutputStorage", {}) or {}
            bucket = cos_out.get("Bucket", "")
            region = cos_out.get("Region", "")
            print(f"       输出: COS - {bucket}:{out_path} (region: {region})")
            _try_print_cos_presigned_url(bucket, region, out_path)


def print_live_stream_task(task):
    """打印直播流处理任务结果，包含错误检测。"""
    if not task:
        return

    status = task.get("Status", "")
    err_code = task.get("ErrCode") or 0
    message = task.get("Message", "")

    status_str = format_status(status)
    err_str = ""
    if err_code != 0:
        err_str = f" | 错误码: {err_code}"
    if message and message != "SUCCESS":
        err_str += f" - {message}"

    print(f"   直播流处理: {status_str}{err_str}")


def print_extract_blind_watermark_task(task):
    """打印提取盲水印任务结果，包含错误检测。"""
    if not task:
        return

    status = task.get("Status", "")
    err_code = task.get("ErrCode") or 0
    message = task.get("Message", "")

    status_str = format_status(status)
    err_str = ""
    if err_code != 0:
        err_str = f" | 错误码: {err_code}"
    if message and message != "SUCCESS":
        err_str += f" - {message}"

    print(f"   提取盲水印: {status_str}{err_str}")

    # 输出文本
    output_text = task.get("OutputText", "")
    if output_text:
        print(f"       提取内容: {output_text}")


def print_schedule_activity_results(result_set):
    """
    打印编排任务活动结果，包含错误检测。
    
    根据 ActivityType 动态获取对应的任务详情，递归处理每个子任务的
    ErrCode、ErrCodeExt 和 Message。
    """
    if not result_set:
        return

    # ActivityType 到任务详情字段的映射
    ACTIVITY_TYPE_MAP = {
        "Transcode": "TranscodeTask",
        "AnimatedGraphics": "AnimatedGraphicsTask",
        "SnapshotByTimeOffset": "SnapshotByTimeOffsetTask",
        "SampleSnapshot": "SampleSnapshotTask",
        "ImageSprites": "ImageSpritesTask",
        "AdaptiveDynamicStreaming": "AdaptiveDynamicStreamingTask",
        "Recognition": "RecognitionTask",
        "Review": "ReviewTask",
        "Analysis": "AnalysisTask",
        "QualityControl": "QualityControlTask",
        "SmartSubtitles": "SmartSubtitlesTask",
        "SmartErase": "SmartEraseTask",
        "ExecRule": "ExecRuleTask",
        "AudioExtract": "AudioExtractTask",
        "CoverBySnapshot": "CoverBySnapshotTask",
        "Classification": "ClassificationTask",
        "Cover": "CoverTask",
        "Cutout": "CutoutTask",
        "DeLogo": "DeLogoTask",
        "Description": "DescriptionTask",
        "Dubbing": "DubbingTask",
        "FrameTag": "FrameTagTask",
        "HeadTail": "HeadTailTask",
        "Highlight": "HighlightTask",
        "HorizontalToVertical": "HorizontalToVerticalTask",
        "Reel": "ReelTask",
        "Segment": "SegmentTask",
        "Tag": "TagTask",
        "VideoComprehension": "VideoComprehensionTask",
        "VideoRemake": "VideoRemakeTask",
        "Face": "FaceTask",
        "Asr": "AsrTask",
        "AsrFullText": "AsrFullTextTask",
        "AsrWords": "AsrWordsTask",
        "Ocr": "OcrTask",
        "OcrFullText": "OcrFullTextTask",
        "OcrWords": "OcrWordsTask",
        "Object": "ObjectTask",
        "TransText": "TransTextTask",
        "Porn": "PornTask",
        "Terrorism": "TerrorismTask",
        "Political": "PoliticalTask",
        "Prohibited": "ProhibitedTask",
        "PoliticalAsr": "PoliticalAsrTask",
        "PoliticalOcr": "PoliticalOcrTask",
        "PornAsr": "PornAsrTask",
        "PornOcr": "PornOcrTask",
        "ProhibitedAsr": "ProhibitedAsrTask",
        "ProhibitedOcr": "ProhibitedOcrTask",
        "TerrorismOcr": "TerrorismOcrTask",
    }

    for i, item in enumerate(result_set, 1):
        activity_res = item.get("ActivityResItem", {})
        activity_type = item.get("ActivityType", "")

        # 根据 ActivityType 获取对应的任务详情字段名
        task_key = ACTIVITY_TYPE_MAP.get(activity_type)
        
        if task_key and task_key in activity_res:
            task = activity_res[task_key]
            # 统一处理所有子任务类型的错误信息
            _print_schedule_subtask_error(task, activity_type, i)
        else:
            # 未知类型，尝试遍历所有可能的任务字段
            _print_unknown_activity_type(activity_res, activity_type, i)


def _print_schedule_subtask_error(task, activity_type, index):
    """
    统一打印编排子任务错误信息。
    递归处理 ErrCode、ErrCodeExt 和 Message。
    """
    if not task:
        return
    
    status = task.get("Status", "")
    err_code = task.get("ErrCode") or 0
    err_code_ext = task.get("ErrCodeExt", "")
    message = task.get("Message", "")
    progress = task.get("Progress")
    
    # 类型名称映射
    type_name_map = {
        "Transcode": "转码",
        "AnimatedGraphics": "转动图",
        "SnapshotByTimeOffset": "时间点截图",
        "SampleSnapshot": "采样截图",
        "ImageSprites": "雪碧图",
        "AdaptiveDynamicStreaming": "自适应码流",
        "AudioExtract": "音频分离",
        "CoverBySnapshot": "截图做封面",
        "Recognition": "AI识别",
        "Review": "AI审核",
        "Analysis": "AI分析",
        "QualityControl": "质检",
        "SmartSubtitles": "智能字幕",
        "SmartErase": "智能擦除",
        "ExecRule": "规则执行",
        "Classification": "分类",
        "Cover": "封面",
        "Cutout": "抠图",
        "DeLogo": "去台标",
        "Description": "描述",
        "Dubbing": "配音",
        "FrameTag": "帧标签",
        "HeadTail": "片头片尾",
        "Highlight": "精彩集锦",
        "HorizontalToVertical": "横转竖",
        "Reel": "智能二创",
        "Segment": "分镜拆条",
        "Tag": "标签",
        "VideoComprehension": "视频理解",
        "VideoRemake": "视频二创",
        "Face": "人脸识别",
        "Asr": "语音识别",
        "AsrFullText": "语音全文识别",
        "AsrWords": "语音分词识别",
        "Ocr": "文字识别",
        "OcrFullText": "文字全文识别",
        "OcrWords": "文字分词识别",
        "Object": "物体识别",
        "TransText": "翻译",
        "Porn": "涉黄审核",
        "Terrorism": "涉恐审核",
        "Political": "涉政审核",
        "Prohibited": "违禁审核",
        "PoliticalAsr": "涉政语音审核",
        "PoliticalOcr": "涉政文字审核",
        "PornAsr": "涉黄语音审核",
        "PornOcr": "涉黄文字审核",
        "ProhibitedAsr": "违禁语音审核",
        "ProhibitedOcr": "违禁文字审核",
        "TerrorismOcr": "涉恐文字审核",
    }
    type_name = type_name_map.get(activity_type, activity_type)
    
    status_str = format_status(status)
    progress_str = f" ({progress}%)" if progress is not None else ""
    
    # 构建错误信息字符串
    err_str = ""
    if err_code != 0:
        err_str = f" | 错误码: {err_code}"
    if err_code_ext:
        err_str += f" ({err_code_ext})"
    if message and message != "SUCCESS":
        err_str += f" - {message}"
    
    print(f"   编排-{type_name}[{index}]: {status_str}{progress_str}{err_str}")
    
    # 递归处理嵌套的输出结果中的错误（如字幕任务的子结果）
    _print_nested_task_errors(task, f"编排-{type_name}[{index}]")


def _print_nested_task_errors(task, parent_label):
    """递归打印嵌套任务的错误信息。"""
    if not task:
        return

    output = task.get("Output", {})
    if not output:
        return

    # 处理字幕结果的嵌套错误
    subtitle_results = output.get("SubtitleResults", [])
    for j, sub in enumerate(subtitle_results, 1):
        sub_status = sub.get("Status", "")
        sub_err = sub.get("ErrCode") or 0
        sub_err_ext = sub.get("ErrCodeExt", "")
        sub_msg = sub.get("Message", "")
        if sub_err != 0 or sub_status == "FAIL":
            err_info = f"错误码: {sub_err}"
            if sub_err_ext:
                err_info += f" ({sub_err_ext})"
            if sub_msg:
                err_info += f" - {sub_msg}"
            print(f"       └─ 字幕结果[{j}]: {format_status(sub_status)} | {err_info}")

    # 处理 OCR 识别结果的嵌套错误
    recognize_results = output.get("RecognizeSubtitleResult", [])
    for j, rec in enumerate(recognize_results, 1):
        rec_status = rec.get("Status", "")
        rec_err = rec.get("ErrCode") or 0
        rec_err_ext = rec.get("ErrCodeExt", "")
        rec_msg = rec.get("Message", "")
        if rec_err != 0 or rec_status == "FAIL":
            err_info = f"错误码: {rec_err}"
            if rec_err_ext:
                err_info += f" ({rec_err_ext})"
            if rec_msg:
                err_info += f" - {rec_msg}"
            print(f"       └─ OCR识别结果[{j}]: {format_status(rec_status)} | {err_info}")

    # 处理字幕翻译结果的嵌套错误
    trans_results = output.get("TransSubtitleResult", [])
    for j, trans in enumerate(trans_results, 1):
        trans_status = trans.get("Status", "")
        trans_err = trans.get("ErrCode") or 0
        trans_err_ext = trans.get("ErrCodeExt", "")
        trans_msg = trans.get("Message", "")
        if trans_err != 0 or trans_status == "FAIL":
            err_info = f"错误码: {trans_err}"
            if trans_err_ext:
                err_info += f" ({trans_err_ext})"
            if trans_msg:
                err_info += f" - {trans_msg}"
            print(f"       └─ 字幕翻译结果[{j}]: {format_status(trans_status)} | {err_info}")

    # 处理质检任务的诊断结果
    diagnose_results = output.get("ContainerDiagnoseResultSet", [])
    if diagnose_results:
        print(f"       └─ 质检诊断结果：")
        has_fatal = False
        has_warning = False

        for diagnose in diagnose_results:
            category = diagnose.get("Category", "")
            type_name = diagnose.get("Type", "")
            severity = diagnose.get("SeverityLevel", "")

            if severity == "Fatal":
                has_fatal = True
                print(f"          ❌ 【致命】{category}/{type_name}")
            elif severity == "Warning":
                has_warning = True
                print(f"          ⚠️  【警告】{category}/{type_name}")
            else:
                print(f"          ℹ️  【{severity}】{category}/{type_name}")

            timestamps = diagnose.get("TimestampSet", [])
            if timestamps:
                print(f"             时间点: {', '.join(map(str, timestamps))} 秒")

        if has_fatal:
            print(f"       ⚠️  质检检测到致命错误")


def _print_unknown_activity_type(activity_res, activity_type, index):
    """处理未知的 ActivityType，尝试遍历所有可能的任务字段。"""
    # 尝试所有已知的任务字段
    known_tasks = [
        ("TranscodeTask", "转码"),
        ("AnimatedGraphicsTask", "转动图"),
        ("SnapshotByTimeOffsetTask", "时间点截图"),
        ("SampleSnapshotTask", "采样截图"),
        ("ImageSpritesTask", "雪碧图"),
        ("AdaptiveDynamicStreamingTask", "自适应码流"),
        ("AudioExtractTask", "音频分离"),
        ("CoverBySnapshotTask", "截图做封面"),
        ("RecognitionTask", "AI识别"),
        ("ReviewTask", "AI审核"),
        ("AnalysisTask", "AI分析"),
        ("QualityControlTask", "质检"),
        ("SmartSubtitlesTask", "智能字幕"),
        ("SmartEraseTask", "智能擦除"),
        ("ExecRuleTask", "规则执行"),
        ("ClassificationTask", "分类"),
        ("CoverTask", "封面"),
        ("CutoutTask", "抠图"),
        ("DeLogoTask", "去台标"),
        ("DescriptionTask", "描述"),
        ("DubbingTask", "配音"),
        ("FrameTagTask", "帧标签"),
        ("HeadTailTask", "片头片尾"),
        ("HighlightTask", "精彩集锦"),
        ("HorizontalToVerticalTask", "横转竖"),
        ("ReelTask", "智能二创"),
        ("SegmentTask", "分镜拆条"),
        ("TagTask", "标签"),
        ("VideoComprehensionTask", "视频理解"),
        ("VideoRemakeTask", "视频二创"),
        ("FaceTask", "人脸识别"),
        ("AsrTask", "语音识别"),
        ("AsrFullTextTask", "语音全文识别"),
        ("AsrWordsTask", "语音分词识别"),
        ("OcrTask", "文字识别"),
        ("OcrFullTextTask", "文字全文识别"),
        ("OcrWordsTask", "文字分词识别"),
        ("ObjectTask", "物体识别"),
        ("TransTextTask", "翻译"),
        ("PornTask", "涉黄审核"),
        ("TerrorismTask", "涉恐审核"),
        ("PoliticalTask", "涉政审核"),
        ("ProhibitedTask", "违禁审核"),
        ("PoliticalAsrTask", "涉政语音审核"),
        ("PoliticalOcrTask", "涉政文字审核"),
        ("PornAsrTask", "涉黄语音审核"),
        ("PornOcrTask", "涉黄文字审核"),
        ("ProhibitedAsrTask", "违禁语音审核"),
        ("ProhibitedOcrTask", "违禁文字审核"),
        ("TerrorismOcrTask", "涉恐文字审核"),
    ]
    
    found = False
    for task_key, type_name in known_tasks:
        if task_key in activity_res:
            task = activity_res[task_key]
            _print_schedule_subtask_error(task, type_name, index)
            found = True
            break
    
    if not found:
        # 完全未知的类型，打印警告
        print(f"   编排-未知类型[{index}] (ActivityType: {activity_type}): 无法识别的任务类型")


def print_media_task_error(task, label):
    """打印媒体处理任务错误信息。"""
    if not task:
        return
    status = task.get("Status", "")
    err_code = task.get("ErrCode") or 0
    err_code_ext = task.get("ErrCodeExt", "")
    message = task.get("Message", "")
    progress = task.get("Progress", None)

    status_str = format_status(status)
    progress_str = f" ({progress}%)" if progress is not None else ""
    err_str = ""
    if err_code != 0:
        err_str = f" | 错误码: {err_code}"
    if err_code_ext:
        err_str += f" ({err_code_ext})"
    if message and message != "SUCCESS":
        err_str += f" - {message}"

    print(f"   {label}: {status_str}{progress_str}{err_str}")


def print_ai_task_error(task, label):
    """打印AI任务错误信息。"""
    if not task:
        return
    status = task.get("Status", "")
    err_code = task.get("ErrCode") or 0
    err_code_ext = task.get("ErrCodeExt", "")
    message = task.get("Message", "")

    status_str = format_status(status)
    err_str = ""
    if err_code != 0:
        err_str = f" | 错误码: {err_code}"
    if err_code_ext:
        err_str += f" ({err_code_ext})"
    if message and message != "SUCCESS":
        err_str += f" - {message}"

    print(f"   {label}: {status_str}{err_str}")


def print_schedule_task(task):
    """打印编排任务结果，包含错误检测。"""
    if not task:
        return

    status = task.get("Status", "")
    err_code = task.get("ErrCode") or 0
    message = task.get("Message", "")

    status_str = format_status(status)
    err_str = ""
    if err_code != 0:
        err_str = f" | 错误码: {err_code}"
    if message and message != "SUCCESS":
        err_str += f" - {message}"

    print(f"   编排任务: {status_str}{err_str}")

    # 输入信息
    print_input_info(task.get("InputInfo"))

    # 活动结果
    print("-" * 60)
    print("   编排活动结果：")
    print_schedule_activity_results(task.get("ActivityResultSet", []))


def print_live_schedule_task(task):
    """打印直播编排任务结果，包含错误检测。"""
    if not task:
        return

    status = task.get("Status", "")
    err_code = task.get("ErrCode") or 0
    message = task.get("Message", "")

    status_str = format_status(status)
    err_str = ""
    if err_code != 0:
        err_str = f" | 错误码: {err_code}"
    if message and message != "SUCCESS":
        err_str += f" - {message}"

    print(f"   直播编排: {status_str}{err_str}")

    # 直播活动结果
    live_results = task.get("LiveActivityResultSet", [])
    if live_results:
        print("-" * 60)
        print("   直播活动结果：")
        for i, item in enumerate(live_results, 1):
            live_res = item.get("LiveActivityResItem", {})

            if "LiveRecordTask" in live_res:
                record_task = live_res["LiveRecordTask"]
                rec_status = record_task.get("Status", "")
                rec_err = record_task.get("ErrCode") or 0
                rec_msg = record_task.get("Message", "")
                rec_status_str = format_status(rec_status)
                rec_err_str = ""
                if rec_err != 0:
                    rec_err_str = f" | 错误码: {rec_err}"
                if rec_msg and rec_msg != "SUCCESS":
                    rec_err_str += f" - {rec_msg}"
                print(f"   [{i}] 直播录制: {rec_status_str}{rec_err_str}")

            if "LiveQualityControlTask" in live_res:
                qc_task = live_res["LiveQualityControlTask"]
                qc_status = qc_task.get("Status", "")
                qc_err = qc_task.get("ErrCode") or 0
                qc_msg = qc_task.get("Message", "")
                qc_status_str = format_status(qc_status)
                qc_err_str = ""
                if qc_err != 0:
                    qc_err_str = f" | 错误码: {qc_err}"
                if qc_msg and qc_msg != "SUCCESS":
                    qc_err_str += f" - {qc_msg}"
                print(f"   [{i}] 直播质检: {qc_status_str}{qc_err_str}")


def query_task(args):
    """查询媒体处理任务详情。"""
    region = args.region or "ap-guangzhou"

    # 1. 获取凭证和客户端
    cred = get_credentials()
    client = create_mps_client(cred, region)

    # 2. 构建请求
    params = {"TaskId": args.task_id}

    # 3. 发起调用
    try:
        req = models.DescribeTaskDetailRequest()
        req.from_json_string(json.dumps(params))

        resp = client.DescribeTaskDetail(req)
        result = json.loads(resp.to_json_string())

        # 仅输出 JSON 模式
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return result

        # 解析响应
        task_type = result.get("TaskType", "")
        status = result.get("Status", "")
        create_time = result.get("CreateTime", "")
        begin_time = result.get("BeginProcessTime", "")
        finish_time = result.get("FinishTime", "")

        print("=" * 60)
        print("腾讯云 MPS 媒体处理任务详情")
        print("=" * 60)
        print(f"   TaskId:    {args.task_id}")
        print(f"   任务类型:  {task_type}")
        print(f"   状态:      {format_status(status)}")
        print(f"   创建时间:  {create_time}")
        if begin_time:
            print(f"   开始时间:  {begin_time}")
        if finish_time:
            print(f"   完成时间:  {finish_time}")
        print("-" * 60)

        # WorkflowTask（ProcessMedia 提交的任务）
        workflow_task = result.get("WorkflowTask")
        if workflow_task:
            wf_status = workflow_task.get("Status", "")
            wf_err = workflow_task.get("ErrCode") or 0
            wf_msg = workflow_task.get("Message", "")

            print(f"   工作流状态: {format_status(wf_status)}", end="")
            if wf_err != 0:
                print(f" | 错误码: {wf_err} - {wf_msg}", end="")
            print()

            # 输入信息
            print_input_info(workflow_task.get("InputInfo"))

            # 元信息
            print_meta_data(workflow_task.get("MetaData"))

            # 子任务结果
            print("-" * 60)
            print("   子任务结果：")
            print_media_process_results(workflow_task.get("MediaProcessResultSet", []))

            # AI 任务结果
            print("-" * 60)
            print("   AI 任务结果：")
            print_ai_analysis_results(workflow_task.get("AiAnalysisResultSet", []))
            print_ai_recognition_results(workflow_task.get("AiRecognitionResultSet", []))
            print_ai_content_review_results(workflow_task.get("AiContentReviewResultSet", []))
            print_ai_quality_control_result(workflow_task.get("AiQualityControlTaskResult", {}))
            
            # 智能字幕任务
            smart_subtitles = workflow_task.get("SmartSubtitlesTaskResultSet", [])
            if smart_subtitles:
                print("-" * 60)
                print("   智能字幕任务：")
                print_smart_subtitles_results(smart_subtitles)
            
            # 智能擦除任务
            smart_erase = workflow_task.get("SmartEraseTaskResult", {})
            if smart_erase:
                print("-" * 60)
                print("   智能擦除任务：")
                print_smart_erase_result(smart_erase)
        
        # EditMediaTask（视频编辑任务）
        elif result.get("EditMediaTask"):
            edit_task = result.get("EditMediaTask")
            print_edit_media_task(edit_task)
        
        # LiveStreamProcessTask（直播流处理任务）
        elif result.get("LiveStreamProcessTask"):
            live_task = result.get("LiveStreamProcessTask")
            print_live_stream_task(live_task)
        
        # ExtractBlindWatermarkTask（提取盲水印任务）
        elif result.get("ExtractBlindWatermarkTask"):
            watermark_task = result.get("ExtractBlindWatermarkTask")
            print_extract_blind_watermark_task(watermark_task)
        
        # ScheduleTask（编排任务）
        elif result.get("ScheduleTask"):
            schedule_task = result.get("ScheduleTask")
            print_schedule_task(schedule_task)
        
        # LiveScheduleTask（直播编排任务）
        elif result.get("LiveScheduleTask"):
            live_schedule_task = result.get("LiveScheduleTask")
            print_live_schedule_task(live_schedule_task)
        
        else:
            # 其他任务类型，提示用户
            print(f"   提示：该任务类型为 {task_type}，当前脚本可能未完全支持此类型的详细展示。")
            print(f"         如需查看完整信息，请使用 --verbose 或 --json 参数。")

        print("-" * 60)
        print(f"   RequestId: {result.get('RequestId', 'N/A')}")

        # 详细模式：输出完整 JSON
        if args.verbose:
            print("\n完整响应：")
            print(json.dumps(result, ensure_ascii=False, indent=2))

        return result

    except TencentCloudSDKException as e:
        print(f"❌ 请求失败: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="腾讯云 MPS 媒体处理任务查询 —— 查询 ProcessMedia 提交的任务状态和结果",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 查询指定任务
  python mps_get_video_task.py --task-id 235303-WorkflowTask-80108cc3380155d98b2e3573a48a

  # 查询并输出完整 JSON 响应
  python mps_get_video_task.py --task-id 235303-WorkflowTask-80108cc3380155d98b2e3573a48a --verbose

  # 仅输出原始 JSON（方便管道处理）
  python mps_get_video_task.py --task-id 235303-WorkflowTask-80108cc3380155d98b2e3573a48a --json

环境变量：
  TENCENTCLOUD_SECRET_ID   腾讯云 SecretId
  TENCENTCLOUD_SECRET_KEY  腾讯云 SecretKey
        """
    )

    parser.add_argument("--task-id", type=str, required=True,
                        help="媒体处理任务 ID，由 ProcessMedia 接口返回")
    parser.add_argument("--region", type=str,
                        help="MPS 服务区域（默认 ap-guangzhou）")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="输出完整 JSON 响应")
    parser.add_argument("--json", action="store_true",
                        help="仅输出原始 JSON，不打印格式化摘要")

    args = parser.parse_args()

    print("=" * 60)
    print("腾讯云 MPS 媒体处理任务查询")
    print("=" * 60)
    print(f"TaskId: {args.task_id}")
    print("-" * 60)

    query_task(args)


if __name__ == "__main__":
    main()