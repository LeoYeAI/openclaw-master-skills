#!/usr/bin/env python3
"""
腾讯云 MPS AIGC 智能生图脚本

功能：
  使用 MPS AIGC 智能内容创作功能，通过输入文本描述和/或参考图片，生成图片结果。
  媒体处理汇聚多家大模型能力（Hunyuan / GEM / Qwen），提供一站式的调用。
  封装 CreateAigcImageTask + DescribeAigcImageTask 两个 API，
  支持创建任务 + 自动轮询等待结果。

支持的模型：
  - Hunyuan（腾讯混元）
  - GEM（支持版本 2.5 / 3.0，支持多图输入最多3张）
  - Qwen（通义千问）

核心能力：
  - 文生图（Text-to-Image）：输入文本描述生成图片
  - 图生图（Image-to-Image）：输入参考图片 + 文本描述生成图片
  - 多图参考（仅 GEM）：最多3张参考图，支持 asset / style 参考类型
  - 反向提示词（Negative Prompt）：排除不想生成的内容
  - 提示词增强（Enhance Prompt）：自动优化提示词以提升效果
  - 自定义宽高比和分辨率
  - 结果存储到 COS

COS 存储配置（可选）：
  通过 --cos-bucket-name / --cos-bucket-region / --cos-bucket-path 参数，
  或环境变量 TENCENTCLOUD_COS_BUCKET / TENCENTCLOUD_COS_REGION 指定存储桶。
  不配置时使用 MPS 默认临时存储（图片存储12小时）。

用法：
  # 文生图：最简用法（Hunyuan 模型）
  python mps_aigc_image.py --prompt "一只可爱的橘猫在阳光下打盹"

  # 指定模型和版本
  python mps_aigc_image.py --prompt "赛博朋克城市夜景" --model GEM --model-version 3.0

  # 文生图 + 反向提示词
  python mps_aigc_image.py --prompt "美丽的风景画" --negative-prompt "人物、动物、文字"

  # 文生图 + 提示词增强
  python mps_aigc_image.py --prompt "日落海滩" --enhance-prompt

  # 图生图：参考图片 + 描述
  python mps_aigc_image.py --prompt "将这张照片变成油画风格" \
      --image-url https://example.com/photo.jpg

  # GEM 多图参考（最多3张，支持 asset/style 参考类型）
  python mps_aigc_image.py --prompt "融合这些元素" --model GEM \
      --image-url https://example.com/img1.jpg --image-ref-type asset \
      --image-url https://example.com/img2.jpg --image-ref-type style

  # 指定宽高比和分辨率
  python mps_aigc_image.py --prompt "全景山水画" --aspect-ratio 16:9 --resolution 2K

  # 存储到 COS
  python mps_aigc_image.py --prompt "产品海报" \
      --cos-bucket-name mybucket-125xxx --cos-bucket-region ap-guangzhou --cos-bucket-path aigc_output

  # 仅创建任务（不等待结果）
  python mps_aigc_image.py --prompt "星空" --no-wait

  # 查询已有任务结果
  python mps_aigc_image.py --task-id 1234567890-xxxxxxxxxxxxx

  # Dry Run（仅打印请求参数，不实际调用 API）
  python mps_aigc_image.py --prompt "测试图片" --dry-run

环境变量：
  TENCENTCLOUD_SECRET_ID   - 腾讯云 SecretId
  TENCENTCLOUD_SECRET_KEY  - 腾讯云 SecretKey
  TENCENTCLOUD_COS_BUCKET       - COS Bucket 名称（可选，用于结果存储）
  TENCENTCLOUD_COS_REGION       - COS Bucket 区域（默认 ap-guangzhou）
"""

import argparse
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

# COS SDK（可选，用于生成临时URL）
try:
    from qcloud_cos import CosConfig, CosS3Client
    _COS_SDK_AVAILABLE = True
except ImportError:
    _COS_SDK_AVAILABLE = False


# =============================================================================
# 模型信息
# =============================================================================
SUPPORTED_MODELS = {
    "Hunyuan": {
        "description": "腾讯混元大模型",
        "versions": [],
        "max_images": 1,
    },
    "GEM": {
        "description": "GEM 生图模型",
        "versions": ["2.5", "3.0"],
        "max_images": 3,
    },
    "Qwen": {
        "description": "通义千问生图模型",
        "versions": [],
        "max_images": 1,
    },
}

# 支持的宽高比（GEM 模型支持最多）
SUPPORTED_ASPECT_RATIOS = [
    "1:1", "3:2", "2:3", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"
]

# 支持的分辨率
SUPPORTED_RESOLUTIONS = ["720P", "1080P", "2K", "4K"]

# 轮询配置
DEFAULT_POLL_INTERVAL = 5   # 秒
DEFAULT_MAX_WAIT = 300      # 最长等待5分钟


def get_cos_bucket():
    """从环境变量获取 COS Bucket 名称。"""
    return os.environ.get("TENCENTCLOUD_COS_BUCKET", "")


def get_cos_region():
    """从环境变量获取 COS Bucket 区域，默认 ap-guangzhou。"""
    return os.environ.get("TENCENTCLOUD_COS_REGION", "ap-guangzhou")


# =============================================================================
# COS 临时 URL 生成
# =============================================================================
def get_cos_presigned_url(bucket: str, region: str, key: str, 
                          secret_id: str = None, secret_key: str = None,
                          expired: int = 3600) -> str:
    """
    生成 COS 临时访问 URL（预签名 URL）
    
    Args:
        bucket: COS Bucket 名称
        region: COS Bucket 区域
        key: COS 对象 Key
        secret_id: 腾讯云 SecretId（默认从环境变量获取）
        secret_key: 腾讯云 SecretKey（默认从环境变量获取）
        expired: URL 有效期（秒），默认 3600（1小时）
    
    Returns:
        预签名 URL，失败返回 None
    """
    if not _COS_SDK_AVAILABLE:
        print("警告：COS SDK 未安装，无法生成临时 URL。请安装：pip install cos-python-sdk-v5", 
              file=sys.stderr)
        return None
    
    secret_id = secret_id or os.environ.get("TENCENTCLOUD_SECRET_ID")
    secret_key = secret_key or os.environ.get("TENCENTCLOUD_SECRET_KEY")
    
    if not secret_id or not secret_key:
        print("警告：缺少腾讯云密钥，无法生成临时 URL", file=sys.stderr)
        return None
    
    try:
        config = CosConfig(
            Region=region,
            SecretId=secret_id,
            SecretKey=secret_key
        )
        client = CosS3Client(config)
        
        url = client.get_presigned_url(
            Method='GET',
            Bucket=bucket,
            Key=key,
            Expired=expired
        )
        return url
    except Exception as e:
        print(f"警告：生成临时 URL 失败: {e}", file=sys.stderr)
        return None


def resolve_cos_input(cos_bucket: str, cos_region: str, cos_key: str,
                      secret_id: str = None, secret_key: str = None) -> str:
    """
    将 COS 路径解析为可访问的 URL
    
    Args:
        cos_bucket: COS Bucket 名称
        cos_region: COS Bucket 区域
        cos_key: COS 对象 Key
        secret_id: 腾讯云 SecretId
        secret_key: 腾讯云 SecretKey
    
    Returns:
        可访问的 URL（临时 URL 或永久 URL）
    """
    if not cos_bucket or not cos_region or not cos_key:
        return None
    
    # 尝试生成临时 URL
    presigned_url = get_cos_presigned_url(cos_bucket, cos_region, cos_key, 
                                          secret_id, secret_key)
    if presigned_url:
        return presigned_url
    
    # 如果生成失败，返回永久 URL（可能无法访问）
    return f"https://{cos_bucket}.cos.{cos_region}.myqcloud.com/{cos_key.lstrip('/')}"


try:
    from load_env import ensure_env_loaded as _ensure_env_loaded
    _LOAD_ENV_AVAILABLE = True
except ImportError:
    _LOAD_ENV_AVAILABLE = False
    def _ensure_env_loaded(**kwargs):
        return False

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


def build_create_params(args):
    """构建 CreateAigcImageTask 请求参数。"""
    params = {}

    # 模型名称（必填）
    params["ModelName"] = args.model

    # 模型版本（可选）
    if args.model_version:
        params["ModelVersion"] = args.model_version

    # 提示词
    if args.prompt:
        params["Prompt"] = args.prompt

    # 反向提示词
    if args.negative_prompt:
        params["NegativePrompt"] = args.negative_prompt

    # 提示词增强
    if args.enhance_prompt:
        params["EnhancePrompt"] = True

    # 参考图片 - 合并 URL 和 COS 路径输入
    image_infos = []
    ref_types = args.image_ref_type or []
    
    # 1. 处理直接传入的 URL
    if args.image_url:
        for i, url in enumerate(args.image_url):
            info = {"ImageUrl": url}
            if i < len(ref_types):
                info["ReferenceType"] = ref_types[i]
            image_infos.append(info)
    
    # 2. 处理 COS 路径输入 - 使用 CosInputInfo 结构（推荐，解决权限问题）
    if args.image_cos_key:
        cos_buckets = args.image_cos_bucket or []
        cos_regions = args.image_cos_region or []
        
        for i, key in enumerate(args.image_cos_key):
            # 获取对应的 bucket 和 region
            bucket = cos_buckets[i] if i < len(cos_buckets) else (cos_buckets[0] if cos_buckets else None)
            region = cos_regions[i] if i < len(cos_regions) else (cos_regions[0] if cos_regions else "ap-guangzhou")
            
            if not bucket:
                print(f"❌ 错误: --image-cos-key[{i}] 缺少对应的 --image-cos-bucket", file=sys.stderr)
                sys.exit(1)
            
            # 使用 CosInputInfo 结构传递 COS 路径（而不是拼接 URL）
            # 这样 MPS 可以通过内部权限读取文件，不受公网访问权限限制
            info = {
                "CosInputInfo": {
                    "Bucket": bucket,
                    "Region": region,
                    "Object": key if key.startswith("/") else f"/{key}"
                }
            }
            # COS 路径输入的参考类型，如果提供了 ref_types，则使用；否则不设置
            url_idx = len(args.image_url) if args.image_url else 0
            ref_type_idx = url_idx + i
            if ref_type_idx < len(ref_types):
                info["ReferenceType"] = ref_types[ref_type_idx]
            image_infos.append(info)
    
    if image_infos:
        params["ImageInfos"] = image_infos

    # 额外参数
    extra = {}
    if args.aspect_ratio:
        extra["AspectRatio"] = args.aspect_ratio
    if args.resolution:
        extra["Resolution"] = args.resolution
    if extra:
        params["ExtraParameters"] = extra

    # COS 存储
    cos_param = build_store_cos_param(args)
    if cos_param:
        params["StoreCosParam"] = cos_param

    # 额外参数（特殊场景）
    if args.additional_parameters:
        params["AdditionalParameters"] = args.additional_parameters

    # 操作者
    if args.operator:
        params["Operator"] = args.operator

    return params


def build_store_cos_param(args):
    """构建 COS 存储参数。"""
    bucket_name = args.cos_bucket_name or get_cos_bucket()
    bucket_region = args.cos_bucket_region or get_cos_region()

    if not bucket_name:
        return None

    cos_param = {
        "CosBucketName": bucket_name,
        "CosBucketRegion": bucket_region,
    }
    if args.cos_bucket_path:
        cos_param["CosBucketPath"] = args.cos_bucket_path

    return cos_param


def create_aigc_image_task(client, params):
    """调用 CreateAigcImageTask API 创建生图任务。"""
    req = models.CreateAigcImageTaskRequest()
    req.from_json_string(json.dumps(params))
    resp = client.CreateAigcImageTask(req)
    return json.loads(resp.to_json_string())


def describe_aigc_image_task(client, task_id):
    """调用 DescribeAigcImageTask API 查询任务状态。"""
    req = models.DescribeAigcImageTaskRequest()
    req.from_json_string(json.dumps({"TaskId": task_id}))
    resp = client.DescribeAigcImageTask(req)
    return json.loads(resp.to_json_string())


def poll_task_result(client, task_id, poll_interval, max_wait):
    """轮询等待任务完成。"""
    elapsed = 0
    while elapsed < max_wait:
        result = describe_aigc_image_task(client, task_id)
        status = result.get("Status", "")

        if status == "DONE":
            return result
        elif status == "FAIL":
            message = result.get("Message", "未知错误")
            print(f"\n❌ 任务失败: {message}", file=sys.stderr)
            sys.exit(1)

        # 打印进度
        status_text = {"WAIT": "等待中", "RUN": "执行中"}.get(status, status)
        print(f"\r⏳ 任务状态: {status_text}（已等待 {elapsed}s / 最长 {max_wait}s）", end="", flush=True)

        time.sleep(poll_interval)
        elapsed += poll_interval

    print(f"\n⚠️  等待超时（已等待 {max_wait}s），任务仍在进行中。", file=sys.stderr)
    print(f"   请稍后使用 --task-id {task_id} 查询结果。", file=sys.stderr)
    sys.exit(1)


def validate_args(args, parser):
    """校验参数。"""
    # 如果是查询模式，不需要其他参数
    if args.task_id:
        return

    # 创建模式：至少需要 prompt 或 image_url 或 image_cos_key
    has_image_input = bool(args.image_url) or bool(args.image_cos_key)
    if not args.prompt and not has_image_input:
        parser.error("请至少指定 --prompt（文本描述）或 --image-url/--image-cos-key（参考图片）")

    # 模型版本校验
    model_info = SUPPORTED_MODELS.get(args.model)
    if model_info and args.model_version:
        valid_versions = model_info["versions"]
        if valid_versions and args.model_version not in valid_versions:
            parser.error(
                f"模型 {args.model} 支持的版本为: {', '.join(valid_versions)}，"
                f"当前指定: {args.model_version}"
            )

    # 多图参考校验（合并 URL 和 COS 路径输入）
    total_images = 0
    if args.image_url:
        total_images += len(args.image_url)
    if args.image_cos_key:
        total_images += len(args.image_cos_key)
    
    if total_images > 0 and model_info:
        max_images = model_info["max_images"]
        if total_images > max_images:
            parser.error(
                f"模型 {args.model} 最多支持 {max_images} 张参考图片，"
                f"当前传入 {total_images} 张（URL: {len(args.image_url) if args.image_url else 0}, COS: {len(args.image_cos_key) if args.image_cos_key else 0}）"
            )

    # image_ref_type 数量不能超过总图片数量
    if args.image_ref_type:
        if len(args.image_ref_type) > total_images:
            parser.error("--image-ref-type 数量不能超过参考图片总数")
    
    # COS 路径参数校验
    if args.image_cos_key:
        # 检查是否提供了 bucket
        if not args.image_cos_bucket:
            parser.error("使用 --image-cos-key 时必须指定 --image-cos-bucket")
        # 如果提供了 region，数量应该与 key 相同或为 1
        if args.image_cos_region and len(args.image_cos_region) > 1:
            if len(args.image_cos_region) != len(args.image_cos_key):
                parser.error("--image-cos-region 数量必须与 --image-cos-key 相同，或只指定一个")

    # 宽高比校验
    if args.aspect_ratio and args.aspect_ratio not in SUPPORTED_ASPECT_RATIOS:
        parser.error(
            f"不支持的宽高比: {args.aspect_ratio}，"
            f"支持: {', '.join(SUPPORTED_ASPECT_RATIOS)}"
        )

    # 分辨率校验
    if args.resolution and args.resolution not in SUPPORTED_RESOLUTIONS:
        parser.error(
            f"不支持的分辨率: {args.resolution}，"
            f"支持: {', '.join(SUPPORTED_RESOLUTIONS)}"
        )

    # AdditionalParameters JSON 格式校验
    if args.additional_parameters:
        try:
            json.loads(args.additional_parameters)
        except json.JSONDecodeError:
            parser.error(
                f"--additional-parameters 必须是有效的 JSON 格式字符串。\n"
                f"示例: '{{\"size\":\"2048x2048\"}}'"
            )


def run(args):
    """执行主流程。"""
    region = args.region or "ap-guangzhou"
    cred = get_credentials()
    client = create_mps_client(cred, region)

    # 模式1: 查询已有任务
    if args.task_id:
        print("=" * 60)
        print("腾讯云 MPS AIGC 生图 — 查询任务")
        print("=" * 60)
        print(f"TaskId: {args.task_id}")
        print("-" * 60)

        try:
            result = describe_aigc_image_task(client, args.task_id)
            status = result.get("Status", "")
            status_text = {
                "WAIT": "等待中", "RUN": "执行中",
                "DONE": "已完成", "FAIL": "失败"
            }.get(status, status)

            print(f"任务状态: {status_text}")

            if status == "DONE":
                image_urls = result.get("ImageUrls", [])
                print(f"生成图片数量: {len(image_urls)}")
                for i, url in enumerate(image_urls, 1):
                    print(f"  图片 {i}: {url}")
                print("\n⚠️  图片存储12小时，请尽快下载使用。")
            elif status == "FAIL":
                print(f"失败原因: {result.get('Message', '未知')}")

            if args.verbose:
                print("\n完整响应：")
                print(json.dumps(result, ensure_ascii=False, indent=2))

        except TencentCloudSDKException as e:
            print(f"❌ 查询失败: {e}", file=sys.stderr)
            sys.exit(1)
        return

    # 模式2: 创建任务
    params = build_create_params(args)

    if args.dry_run:
        print("=" * 60)
        print("【Dry Run 模式】仅打印请求参数，不实际调用 API")
        print("=" * 60)
        print(json.dumps(params, ensure_ascii=False, indent=2))
        return

    # 打印执行信息
    print("=" * 60)
    print("腾讯云 MPS AIGC 智能生图")
    print("=" * 60)
    model_info = SUPPORTED_MODELS.get(args.model, {})
    model_desc = model_info.get("description", args.model)
    print(f"模型: {args.model}（{model_desc}）")
    if args.model_version:
        print(f"版本: {args.model_version}")
    if args.prompt:
        prompt_display = args.prompt[:80] + "..." if len(args.prompt) > 80 else args.prompt
        print(f"提示词: {prompt_display}")
    if args.negative_prompt:
        print(f"反向提示词: {args.negative_prompt}")
    if args.enhance_prompt:
        print("提示词增强: 开启")
    
    # 显示参考图片信息（URL + COS 路径）
    total_images = 0
    if args.image_url:
        total_images += len(args.image_url)
    if args.image_cos_key:
        total_images += len(args.image_cos_key)
    
    if total_images > 0:
        print(f"参考图片: {total_images} 张")
        # 显示直接 URL
        if args.image_url:
            for i, url in enumerate(args.image_url, 1):
                ref_type = ""
                if args.image_ref_type and i - 1 < len(args.image_ref_type):
                    ref_type = f"（{args.image_ref_type[i - 1]}）"
                print(f"  图片 {i}{ref_type}: {url}")
        # 显示 COS 路径
        if args.image_cos_key:
            start_idx = len(args.image_url) if args.image_url else 0
            for i, key in enumerate(args.image_cos_key, 1):
                idx = start_idx + i
                ref_type = ""
                if args.image_ref_type and idx - 1 < len(args.image_ref_type):
                    ref_type = f"（{args.image_ref_type[idx - 1]}）"
                bucket = args.image_cos_bucket[i-1] if i-1 < len(args.image_cos_bucket) else args.image_cos_bucket[0]
                region = args.image_cos_region[i-1] if args.image_cos_region and i-1 < len(args.image_cos_region) else "ap-guangzhou"
                print(f"  图片 {idx}{ref_type}: [COS] {bucket}/{region}{key}")
    
    if args.aspect_ratio:
        print(f"宽高比: {args.aspect_ratio}")
    if args.resolution:
        print(f"分辨率: {args.resolution}")
    print("-" * 60)

    if args.verbose:
        print("请求参数：")
        print(json.dumps(params, ensure_ascii=False, indent=2))
        print()

    try:
        result = create_aigc_image_task(client, params)
        task_id = result.get("TaskId", "N/A")
        request_id = result.get("RequestId", "N/A")

        print(f"✅ AIGC 生图任务创建成功！")
        print(f"   TaskId: {task_id}")
        print(f"   RequestId: {request_id}")

        if args.no_wait:
            print(f"\n提示：使用以下命令查询任务结果：")
            print(f"  python mps_aigc_image.py --task-id {task_id}")
            return result

        # 自动轮询等待结果
        print(f"\n正在等待任务完成（轮询间隔 {args.poll_interval}s，最长等待 {args.max_wait}s）...")
        poll_result = poll_task_result(client, task_id, args.poll_interval, args.max_wait)

        image_urls = poll_result.get("ImageUrls", [])
        print(f"\n✅ 任务完成！生成图片数量: {len(image_urls)}")
        for i, url in enumerate(image_urls, 1):
            print(f"  图片 {i}: {url}")
        print("\n⚠️  图片存储12小时，请尽快下载使用。")

        if args.verbose:
            print("\n完整响应：")
            print(json.dumps(poll_result, ensure_ascii=False, indent=2))

        return poll_result

    except TencentCloudSDKException as e:
        print(f"❌ 请求失败: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="腾讯云 MPS AIGC 智能生图 —— 汇聚 Hunyuan / GEM / Qwen 等多家大模型，一站式文生图、图生图",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 文生图（默认 Hunyuan 模型）
  python mps_aigc_image.py --prompt "一只可爱的橘猫在阳光下打盹"

  # 指定 GEM 模型 3.0 版本
  python mps_aigc_image.py --prompt "赛博朋克城市夜景" --model GEM --model-version 3.0

  # 文生图 + 反向提示词 + 提示词增强
  python mps_aigc_image.py --prompt "美丽的风景画" --negative-prompt "人物、动物" --enhance-prompt

  # 图生图（参考图片 + 描述）
  python mps_aigc_image.py --prompt "油画风格" --image-url https://example.com/photo.jpg

  # GEM 多图参考（最多3张，指定参考类型）
  python mps_aigc_image.py --prompt "融合元素" --model GEM \\
      --image-url https://example.com/img1.jpg --image-ref-type asset \\
      --image-url https://example.com/img2.jpg --image-ref-type style

  # 指定宽高比 + 分辨率
  python mps_aigc_image.py --prompt "全景山水画" --aspect-ratio 16:9 --resolution 2K

  # 结果存储到 COS
  python mps_aigc_image.py --prompt "产品海报" \\
      --cos-bucket-name mybucket-125xxx --cos-bucket-region ap-guangzhou

  # 查询任务结果
  python mps_aigc_image.py --task-id 1234567890-xxxxxxxxxxxxx

  # 仅创建任务不等待
  python mps_aigc_image.py --prompt "星空" --no-wait

  # Dry Run（仅打印请求参数）
  python mps_aigc_image.py --prompt "测试" --dry-run

支持的模型：
  Hunyuan     腾讯混元大模型（默认）
  GEM         GEM 生图模型，版本 2.5 / 3.0，支持最多3张参考图
  Qwen        通义千问生图模型

宽高比选项（部分模型支持）：
  1:1  3:2  2:3  3:4  4:3  4:5  5:4  9:16  16:9  21:9

分辨率选项：
  720P  1080P  2K  4K

环境变量：
  TENCENTCLOUD_SECRET_ID   腾讯云 SecretId
  TENCENTCLOUD_SECRET_KEY  腾讯云 SecretKey
  TENCENTCLOUD_COS_BUCKET       COS Bucket 名称（可选，用于结果存储）
  TENCENTCLOUD_COS_REGION       COS Bucket 区域（默认 ap-guangzhou）
        """
    )

    # ---- 任务查询 ----
    query_group = parser.add_argument_group("任务查询（查询已有任务，与创建任务互斥）")
    query_group.add_argument("--task-id", type=str,
                             help="查询已有任务的 TaskId")

    # ---- 模型配置 ----
    model_group = parser.add_argument_group("模型配置")
    model_group.add_argument("--model", type=str, default="Hunyuan",
                             choices=["Hunyuan", "GEM", "Qwen"],
                             help="模型名称（默认 Hunyuan）")
    model_group.add_argument("--model-version", type=str,
                             help="模型版本号（如 GEM: 2.5 / 3.0）")

    # ---- 生图内容 ----
    content_group = parser.add_argument_group("生图内容")
    content_group.add_argument("--prompt", type=str,
                               help="图片描述文本（最多1000字符）。未传参考图时必填")
    content_group.add_argument("--negative-prompt", type=str,
                               help="反向提示词：描述不想生成的内容（部分模型支持）")
    content_group.add_argument("--enhance-prompt", action="store_true",
                               help="开启提示词增强：自动优化 prompt 以提升生成质量")

    # ---- 参考图片 ----
    image_group = parser.add_argument_group("参考图片（可选，图生图）")
    image_group.add_argument("--image-url", type=str, action="append",
                             help="参考图片 URL（可多次指定，GEM 最多3张）。推荐 < 7M，支持 jpeg/png/webp")
    image_group.add_argument("--image-ref-type", type=str, action="append",
                             choices=["asset", "style"],
                             help="参考类型（与 --image-url 一一对应）: asset=素材 | style=风格")
    
    # COS 路径输入（用于本地上传后使用）
    image_group.add_argument("--image-cos-bucket", type=str, action="append",
                             help="参考图片所在 COS Bucket（与 --image-cos-region/--image-cos-key 配合使用，可多次指定）")
    image_group.add_argument("--image-cos-region", type=str, action="append",
                             help="参考图片所在 COS Region（如 ap-guangzhou，与 --image-cos-key 一一对应）")
    image_group.add_argument("--image-cos-key", type=str, action="append",
                             help="参考图片的 COS Key（如 /input/image.jpg，与 --image-cos-bucket/--image-cos-region 配合使用）")

    # ---- 输出配置 ----
    output_group = parser.add_argument_group("输出配置")
    output_group.add_argument("--aspect-ratio", type=str,
                              help="宽高比（如 16:9, 1:1, 9:16）。不同模型支持不同选项")
    output_group.add_argument("--resolution", type=str,
                              choices=["720P", "1080P", "2K", "4K"],
                              help="输出分辨率（部分模型支持）")
    output_group.add_argument("--additional-parameters", type=str,
                              help="特殊场景参数（JSON格式字符串），例如：'{\"size\":\"2048x2048\"}'")

    # ---- COS 存储 ----
    cos_group = parser.add_argument_group("COS 存储配置（可选，不配置则使用 MPS 临时存储，12小时有效）")
    cos_group.add_argument("--cos-bucket-name", type=str,
                           help="COS Bucket 名称（默认取 TENCENTCLOUD_COS_BUCKET 环境变量）")
    cos_group.add_argument("--cos-bucket-region", type=str,
                           help="COS Bucket 区域（默认取 TENCENTCLOUD_COS_REGION 环境变量，默认 ap-guangzhou）")
    cos_group.add_argument("--cos-bucket-path", type=str, default="/output/aigc-image/",
                          help="COS 存储桶中的输出目录路径 (默认: /output/aigc-image/)")

    # ---- 执行控制 ----
    control_group = parser.add_argument_group("执行控制")
    control_group.add_argument("--no-wait", action="store_true",
                               help="仅创建任务，不等待结果。稍后用 --task-id 查询")
    control_group.add_argument("--poll-interval", type=int, default=DEFAULT_POLL_INTERVAL,
                               help=f"轮询间隔（秒），默认 {DEFAULT_POLL_INTERVAL}")
    control_group.add_argument("--max-wait", type=int, default=DEFAULT_MAX_WAIT,
                               help=f"最长等待时间（秒），默认 {DEFAULT_MAX_WAIT}")
    control_group.add_argument("--operator", type=str,
                               help="操作者名称")

    # ---- 其他 ----
    other_group = parser.add_argument_group("其他配置")
    other_group.add_argument("--region", type=str,
                             help="MPS 服务区域（默认 ap-guangzhou）")
    other_group.add_argument("--verbose", "-v", action="store_true",
                             help="输出详细信息")
    other_group.add_argument("--dry-run", action="store_true",
                             help="仅打印请求参数，不实际调用 API")

    args = parser.parse_args()

    # 参数校验
    validate_args(args, parser)

    # 执行
    run(args)


if __name__ == "__main__":
    main()