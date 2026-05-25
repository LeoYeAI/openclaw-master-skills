#!/usr/bin/env python3
"""
腾讯云 MPS 任务轮询工具模块

提供 poll_video_task() 和 poll_image_task() 两个函数，
供各处理脚本在提交任务后直接内置轮询等待，无需 Agent 手动启动查询。

用法（被其他脚本 import）：
    from poll_task import poll_video_task, poll_image_task

    # 提交任务后直接轮询
    result = poll_video_task(task_id, region="ap-guangzhou", interval=10, max_wait=1800)
    result = poll_image_task(task_id, region="ap-guangzhou", interval=5, max_wait=300)
"""

import json
import os
import sys
import time

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


STATUS_MAP = {
    "WAITING": "等待中",
    "PROCESSING": "处理中",
    "FINISH": "已完成",
    "SUCCESS": "成功",
    "FAIL": "失败",
}


def _get_credentials():
    secret_id = os.environ.get("TENCENTCLOUD_SECRET_ID", "")
    secret_key = os.environ.get("TENCENTCLOUD_SECRET_KEY", "")
    if not secret_id or not secret_key:
        print("错误：请设置环境变量 TENCENTCLOUD_SECRET_ID 和 TENCENTCLOUD_SECRET_KEY", file=sys.stderr)
        sys.exit(1)
    return credential.Credential(secret_id, secret_key)


def _create_client(region):
    cred = _get_credentials()
    http_profile = HttpProfile()
    http_profile.endpoint = "mps.tencentcloudapi.com"
    http_profile.reqMethod = "POST"
    client_profile = ClientProfile()
    client_profile.httpProfile = http_profile
    return mps_client.MpsClient(cred, region, client_profile)


def _fmt(status):
    return STATUS_MAP.get(status, status)


def _print_video_result(result):
    """打印音视频任务结果摘要（含输出文件路径）。"""
    workflow_task = result.get("WorkflowTask") or {}
    result_set = workflow_task.get("MediaProcessResultSet") or []

    TASK_KEY_MAP = {
        "Transcode": "TranscodeTask",
        "AnimatedGraphics": "AnimatedGraphicsTask",
        "SnapshotByTimeOffset": "SnapshotByTimeOffsetTask",
        "SampleSnapshot": "SampleSnapshotTask",
        "ImageSprites": "ImageSpritesTask",
        "AdaptiveDynamicStreaming": "AdaptiveDynamicStreamingTask",
    }
    TASK_NAME_MAP = {
        "Transcode": "转码",
        "AnimatedGraphics": "转动图",
        "SnapshotByTimeOffset": "时间点截图",
        "SampleSnapshot": "采样截图",
        "ImageSprites": "雪碧图",
        "AdaptiveDynamicStreaming": "自适应码流",
        "AiAnalysis": "AI 内容分析",
        "AiRecognition": "AI 内容识别",
    }

    for i, item in enumerate(result_set, 1):
        task_type = item.get("Type", "")
        type_name = TASK_NAME_MAP.get(task_type, task_type)
        task_key = TASK_KEY_MAP.get(task_type, "")
        task_detail = item.get(task_key, {}) if task_key else None

        if task_detail:
            status = task_detail.get("Status", "")
            err_code = task_detail.get("ErrCode", 0)
            message = task_detail.get("Message", "")
            err_str = f" | 错误码: {err_code} - {message}" if err_code != 0 else ""
            print(f"   [{i}] {type_name}: {_fmt(status)}{err_str}")

            output = task_detail.get("Output", {})
            if output:
                out_path = output.get("Path", "")
                out_storage = output.get("OutputStorage", {}) or {}
                out_type = out_storage.get("Type", "")
                if out_type == "COS":
                    cos_out = out_storage.get("CosOutputStorage", {}) or {}
                    bucket = cos_out.get("Bucket", "")
                    region = cos_out.get("Region", "")
                    print(f"       📁 输出: COS - {bucket}:{out_path} (region: {region})")
                    if bucket and out_path and _COS_SDK_AVAILABLE:
                        try:
                            cred = _get_credentials()
                            cos_config = CosConfig(Region=region, SecretId=cred.secret_id, SecretKey=cred.secret_key)
                            cos_client = CosS3Client(cos_config)
                            signed_url = cos_client.get_presigned_url(
                                Bucket=bucket,
                                Key=out_path.lstrip("/"),
                                Method="GET",
                                Expired=3600
                            )
                            print(f"       🔗 下载链接（预签名，1小时有效）: {signed_url}")
                        except Exception as e:
                            print(f"       ⚠️  生成预签名 URL 失败: {e}")
                elif out_path:
                    print(f"       📁 输出: {out_path}")


def _print_image_result(result):
    """打印图片任务结果摘要（含输出文件路径和签名URL）。"""
    result_set = result.get("ImageProcessTaskResultSet") or []
    for i, item in enumerate(result_set, 1):
        status = item.get("Status", "")
        err_msg = item.get("ErrMsg", "")
        err_str = f" | 错误: {err_msg}" if err_msg else ""
        print(f"   [{i}] 状态: {_fmt(status)}{err_str}")

        output = item.get("Output") or {}
        out_path = output.get("Path", "")
        signed_url = output.get("SignedUrl", "")
        out_storage = output.get("OutputStorage", {}) or {}
        out_type = out_storage.get("Type", "")

        if out_type == "COS":
            cos_out = out_storage.get("CosOutputStorage", {}) or {}
            bucket = cos_out.get("Bucket", "")
            region = cos_out.get("Region", "")
            print(f"       📁 输出: COS - {bucket}:{out_path} (region: {region})")
        elif out_path:
            print(f"       📁 输出: {out_path}")

        if signed_url:
            print(f"       🔗 下载链接: {signed_url}")
        elif out_type == "COS" and bucket and out_path and _COS_SDK_AVAILABLE:
            try:
                cred = _get_credentials()
                cos_config = CosConfig(Region=region, SecretId=cred.secret_id, SecretKey=cred.secret_key)
                cos_client = CosS3Client(cos_config)
                signed_url = cos_client.get_presigned_url(
                    Bucket=bucket,
                    Key=out_path,
                    Method="GET",
                    Expired=3600
                )
                print(f"       🔗 下载链接（预签名，1小时有效）: {signed_url}")
            except Exception as e:
                print(f"       ⚠️  生成预签名 URL 失败: {e}")

        content = output.get("Content", "")
        if content:
            display = content if len(content) <= 100 else content[:100] + "..."
            print(f"       📝 图生文结果: {display}")


def poll_video_task(task_id, region="ap-guangzhou", interval=10, max_wait=1800, verbose=False):
    """
    轮询音视频处理任务（ProcessMedia 提交的任务）直到完成。

    Args:
        task_id:   任务 ID
        region:    MPS 服务区域
        interval:  轮询间隔（秒），默认 10
        max_wait:  最长等待时间（秒），默认 1800（30分钟）
        verbose:   是否输出完整 JSON

    Returns:
        最终任务结果 dict，或 None（超时）
    """
    client = _create_client(region)
    elapsed = 0
    attempt = 0

    print(f"\n⏳ 开始轮询任务状态（间隔 {interval}s，最长等待 {max_wait}s）...")

    while elapsed < max_wait:
        attempt += 1
        try:
            req = models.DescribeTaskDetailRequest()
            req.from_json_string(json.dumps({"TaskId": task_id}))
            resp = client.DescribeTaskDetail(req)
            result = json.loads(resp.to_json_string())

            status = result.get("Status", "")
            workflow_task = result.get("WorkflowTask") or {}
            wf_status = workflow_task.get("Status", status)

            print(f"   [{attempt}] 状态: {_fmt(wf_status)}  (已等待 {elapsed}s)")

            if wf_status == "FINISH":
                wf_err = workflow_task.get("ErrCode") or 0
                wf_msg = workflow_task.get("Message") or ""
                if wf_err != 0:
                    print(f"\n❌ 任务失败！错误码: {wf_err} - {wf_msg}")
                else:
                    print(f"\n✅ 任务完成！")
                    _print_video_result(result)

                if verbose:
                    print("\n完整响应：")
                    print(json.dumps(result, ensure_ascii=False, indent=2))
                return result

            if wf_status == "FAIL":
                wf_err = workflow_task.get("ErrCode") or 0
                wf_msg = workflow_task.get("Message") or ""
                print(f"\n❌ 任务失败！错误码: {wf_err} - {wf_msg}")
                if verbose:
                    print(json.dumps(result, ensure_ascii=False, indent=2))
                return result

        except TencentCloudSDKException as e:
            print(f"   [{attempt}] 查询失败: {e}，{interval}s 后重试...")

        time.sleep(interval)
        elapsed += interval

    print(f"\n⚠️  等待超时（已等待 {max_wait}s），任务可能仍在处理中。")
    print(f"   可手动查询：python scripts/mps_get_video_task.py --task-id {task_id}")
    return None


def poll_image_task(task_id, region="ap-guangzhou", interval=5, max_wait=300, verbose=False):
    """
    轮询图片处理任务（ProcessImage 提交的任务）直到完成。

    Args:
        task_id:   任务 ID
        region:    MPS 服务区域
        interval:  轮询间隔（秒），默认 5
        max_wait:  最长等待时间（秒），默认 300（5分钟）
        verbose:   是否输出完整 JSON

    Returns:
        最终任务结果 dict，或 None（超时）
    """
    client = _create_client(region)
    elapsed = 0
    attempt = 0

    print(f"\n⏳ 开始轮询任务状态（间隔 {interval}s，最长等待 {max_wait}s）...")

    while elapsed < max_wait:
        attempt += 1
        try:
            req = models.DescribeImageTaskDetailRequest()
            req.from_json_string(json.dumps({"TaskId": task_id}))
            resp = client.DescribeImageTaskDetail(req)
            result = json.loads(resp.to_json_string())

            status = result.get("Status", "")
            print(f"   [{attempt}] 状态: {_fmt(status)}  (已等待 {elapsed}s)")

            if status == "FINISH":
                err_code = result.get("ErrCode") or 0
                err_msg = result.get("ErrMsg") or ""
                if err_code != 0:
                    print(f"\n❌ 任务失败！错误码: {err_code} - {err_msg}")
                else:
                    print(f"\n✅ 任务完成！")
                    _print_image_result(result)

                if verbose:
                    print("\n完整响应：")
                    print(json.dumps(result, ensure_ascii=False, indent=2))
                return result

            if status == "FAIL":
                err_code = result.get("ErrCode") or 0
                err_msg = result.get("ErrMsg") or ""
                print(f"\n❌ 任务失败！错误码: {err_code} - {err_msg}")
                if verbose:
                    print(json.dumps(result, ensure_ascii=False, indent=2))
                return result

        except TencentCloudSDKException as e:
            print(f"   [{attempt}] 查询失败: {e}，{interval}s 后重试...")

        time.sleep(interval)
        elapsed += interval

    print(f"\n⚠️  等待超时（已等待 {max_wait}s），任务可能仍在处理中。")
    print(f"   可手动查询：python scripts/mps_get_image_task.py --task-id {task_id}")
    return None
