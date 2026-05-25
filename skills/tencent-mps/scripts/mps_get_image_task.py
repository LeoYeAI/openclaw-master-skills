#!/usr/bin/env python3
"""
腾讯云 MPS 图片处理任务查询脚本

功能：
  通过任务 ID 查询 ProcessImage 提交的图片处理任务的执行状态和结果详情。
  最多可以查询 7 天之内提交的任务。

  支持查询任务的整体状态（WAITING / PROCESSING / FINISH），以及各子任务
  的执行结果、输出文件路径、签名 URL 和图生文内容等信息。

用法：
  # 查询指定任务
  python mps_get_image_task.py --task-id 1234567890-ImageTask-80108cc3380155d98b2e3573a48a

  # 查询并输出完整 JSON 响应
  python mps_get_image_task.py --task-id 1234567890-ImageTask-80108cc3380155d98b2e3573a48a --verbose

  # 仅输出原始 JSON（方便管道处理）
  python mps_get_image_task.py --task-id 1234567890-ImageTask-80108cc3380155d98b2e3573a48a --json

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


def print_output_info(output):
    """打印输出文件信息。"""
    if not output:
        return

    out_path = output.get("Path", "")
    signed_url = output.get("SignedUrl", "")
    content = output.get("Content", "")
    out_storage = output.get("OutputStorage", {}) or {}
    out_type = out_storage.get("Type", "")

    bucket = ""
    region = ""

    if out_type == "COS":
        cos_out = out_storage.get("CosOutputStorage", {}) or {}
        bucket = cos_out.get("Bucket", "")
        region = cos_out.get("Region", "")
        print(f"       输出: COS - {bucket}:{out_path} (region: {region})")
    elif out_type == "AWS-S3":
        s3_out = out_storage.get("S3OutputStorage", {}) or {}
        bucket = s3_out.get("S3Bucket", "")
        region = s3_out.get("S3Region", "")
        print(f"       输出: S3 - {bucket}:{out_path} (region: {region})")
    elif out_type == "VOD":
        vod_out = out_storage.get("VODOutputStorage", {}) or {}
        bucket = vod_out.get("Bucket", "")
        region = vod_out.get("Region", "")
        sub_app_id = vod_out.get("SubAppId", "")
        print(f"       输出: VOD - {bucket}:{out_path} (region: {region}, SubAppId: {sub_app_id})")
    elif out_path:
        print(f"       输出路径: {out_path}")

    if signed_url:
        print(f"       签名URL: {signed_url}")
    elif out_type == "COS" and bucket and out_path and _COS_SDK_AVAILABLE:
        try:
            cred = get_credentials()
            cos_config = CosConfig(Region=region, SecretId=cred.secret_id, SecretKey=cred.secret_key)
            cos_client = CosS3Client(cos_config)
            signed_url = cos_client.get_presigned_url(
                Bucket=bucket,
                Key=out_path,
                Method="GET",
                Expired=3600
            )
            print(f"       签名URL（预签名，1小时有效）: {signed_url}")
        except Exception as e:
            print(f"       签名URL: (无) ⚠️  生成预签名 URL 失败: {e}")
    else:
        print(f"       签名URL: (无)")

    if content:
        # 图生文结果，截断过长内容
        display_content = content if len(content) <= 100 else content[:100] + "..."
        print(f"       图生文结果: {display_content}")


def print_image_process_results(result_set):
    """打印图片处理子任务结果。"""
    if not result_set:
        print("   子任务: 无")
        return

    for i, item in enumerate(result_set, 1):
        status = item.get("Status", "")
        err_msg = item.get("ErrMsg", "")
        message = item.get("Message", "")
        progress = item.get("Progress", None)

        status_str = format_status(status)
        progress_str = f" ({progress}%)" if progress is not None else ""

        err_str = ""
        if err_msg:
            err_str = f" | 错误码: {err_msg}"
            if message and message != status:
                err_str += f" - {message}"

        print(f"   [{i}] 状态: {status_str}{progress_str}{err_str}")

        # 打印输出信息
        output = item.get("Output")
        if output:
            print_output_info(output)


def query_task(args):
    """查询图片处理任务详情。"""
    region = args.region or "ap-guangzhou"

    # 1. 获取凭证和客户端
    cred = get_credentials()
    client = create_mps_client(cred, region)

    # 2. 构建请求
    params = {"TaskId": args.task_id}

    # 3. 发起调用
    try:
        req = models.DescribeImageTaskDetailRequest()
        req.from_json_string(json.dumps(params))

        resp = client.DescribeImageTaskDetail(req)
        result = json.loads(resp.to_json_string())

        # 仅输出 JSON 模式
        if args.json:
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return result

        # 解析响应
        task_type = result.get("TaskType", "")
        status = result.get("Status", "")
        err_code = result.get("ErrCode") or 0
        err_msg = result.get("ErrMsg", "")
        message = result.get("Message", "")
        create_time = result.get("CreateTime", "")
        finish_time = result.get("FinishTime", "")

        # 无效 TaskId：API 返回成功但任务不存在（Status 为空/None）
        if not status and not task_type and not create_time:
            print(f"❌ 任务不存在或已过期（超过7天）: {args.task_id}", file=sys.stderr)
            sys.exit(1)

        print("=" * 60)
        print("腾讯云 MPS 图片处理任务详情")
        print("=" * 60)
        print(f"   TaskId:    {args.task_id}")
        print(f"   任务类型:  {task_type}")
        print(f"   状态:      {format_status(status)}", end="")
        if err_code != 0:
            print(f" | 错误码: {err_code}", end="")
        if err_msg:
            print(f" | {err_msg}", end="")
        if message:
            print(f" - {message}", end="")
        print()
        print(f"   创建时间:  {create_time}")
        if finish_time:
            print(f"   完成时间:  {finish_time}")
        print("-" * 60)

        # 子任务结果
        result_set = result.get("ImageProcessTaskResultSet", [])
        if result_set:
            print("   子任务结果：")
            print_image_process_results(result_set)
        else:
            print("   子任务结果: 暂无")

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
        description="腾讯云 MPS 图片处理任务查询 —— 查询 ProcessImage 提交的任务状态和结果",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 查询指定任务
  python mps_get_image_task.py --task-id 2600011633-ImageTask-80108cc3380155d98b2e3573a48a

  # 查询并输出完整 JSON 响应
  python mps_get_image_task.py --task-id 2600011633-ImageTask-80108cc3380155d98b2e3573a48a --verbose

  # 仅输出原始 JSON（方便管道处理）
  python mps_get_image_task.py --task-id 2600011633-ImageTask-80108cc3380155d98b2e3573a48a --json

环境变量：
  TENCENTCLOUD_SECRET_ID   腾讯云 SecretId
  TENCENTCLOUD_SECRET_KEY  腾讯云 SecretKey
        """
    )

    parser.add_argument("--task-id", type=str, required=True,
                        help="图片处理任务 ID，由 ProcessImage 接口返回")
    parser.add_argument("--region", type=str,
                        help="MPS 服务区域（默认 ap-guangzhou）")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="输出完整 JSON 响应")
    parser.add_argument("--json", action="store_true",
                        help="仅输出原始 JSON，不打印格式化摘要")

    args = parser.parse_args()

    print("=" * 60)
    print("腾讯云 MPS 图片处理任务查询")
    print("=" * 60)
    print(f"TaskId: {args.task_id}")
    print("-" * 60)

    query_task(args)


if __name__ == "__main__":
    main()
