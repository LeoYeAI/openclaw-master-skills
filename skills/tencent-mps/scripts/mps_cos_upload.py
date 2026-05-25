#!/usr/bin/env python3
"""
腾讯云 COS 文件上传脚本

功能：
  使用腾讯云 COS Python SDK 将本地文件上传到 COS Bucket。

用法：
  # 最简用法（使用环境变量中的 bucket 和 region）
  python mps_cos_upload.py --local-file /path/to/local/file.mp4 --cos-key input/video.mp4

  # 指定 bucket 和 region（覆盖环境变量）
  python mps_cos_upload.py --local-file /path/to/file.mp4 --cos-key input/video.mp4 \
      --bucket mybucket-125xxx --region ap-guangzhou

  # 使用环境变量中的默认 bucket，只指定 cos-key
  python mps_cos_upload.py --local-file ./test.mp4 --cos-key input/test.mp4

环境变量：
  TENCENTCLOUD_SECRET_ID   - 腾讯云 SecretId
  TENCENTCLOUD_SECRET_KEY  - 腾讯云 SecretKey
  TENCENTCLOUD_COS_BUCKET  - COS Bucket 名称（如 mybucket-125xxx）
  TENCENTCLOUD_COS_REGION  - COS Bucket 区域（默认 ap-guangzhou）
"""

import argparse
import os
import sys

# 加载环境变量模块（同目录）
_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _SCRIPT_DIR)
try:
    from load_env import ensure_env_loaded, check_required_vars, _print_setup_hint
    _LOAD_ENV_AVAILABLE = True
except ImportError:
    _LOAD_ENV_AVAILABLE = False

try:
    from qcloud_cos import CosConfig, CosS3Client
except ImportError:
    print("错误：未安装腾讯云 COS SDK。请运行：pip install cos-python-sdk-v5", file=sys.stderr)
    sys.exit(1)


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="腾讯云 COS 文件上传工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 上传文件到 COS（使用环境变量中的 bucket）
  python mps_cos_upload.py --local-file ./video.mp4 --cos-key input/video.mp4

  # 指定 bucket 和 region
  python mps_cos_upload.py --local-file ./video.mp4 --cos-key input/video.mp4 \\
      --bucket mybucket-125xxx --region ap-guangzhou
        """
    )
    
    parser.add_argument(
        "--local-file", "-f",
        required=True,
        help="本地文件路径（必填）"
    )
    parser.add_argument(
        "--cos-key", "-k",
        required=True,
        help="COS 对象键（Key），如 input/video.mp4（必填）"
    )
    parser.add_argument(
        "--bucket", "-b",
        default=None,
        help="COS Bucket 名称（默认使用环境变量 TENCENTCLOUD_COS_BUCKET）"
    )
    parser.add_argument(
        "--region", "-r",
        default=None,
        help="COS Bucket 区域（默认使用环境变量 TENCENTCLOUD_COS_REGION 或 ap-guangzhou）"
    )
    parser.add_argument(
        "--secret-id",
        default=None,
        help="腾讯云 SecretId（默认使用环境变量 TENCENTCLOUD_SECRET_ID）"
    )
    parser.add_argument(
        "--secret-key",
        default=None,
        help="腾讯云 SecretKey（默认使用环境变量 TENCENTCLOUD_SECRET_KEY）"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="显示详细日志"
    )
    
    return parser.parse_args()


def upload_file(local_file, cos_key, bucket, region, secret_id, secret_key, verbose=False):
    """
    上传文件到 COS
    
    Args:
        local_file: 本地文件路径
        cos_key: COS 对象键
        bucket: COS Bucket 名称
        region: COS Bucket 区域
        secret_id: 腾讯云 SecretId
        secret_key: 腾讯云 SecretKey
        verbose: 是否显示详细日志
    
    Returns:
        dict: 上传结果，包含 ETag 和 URL
    """
    # 检查本地文件是否存在
    if not os.path.isfile(local_file):
        print(f"错误：本地文件不存在: {local_file}", file=sys.stderr)
        return None
    
    # 获取文件大小
    file_size = os.path.getsize(local_file)
    if verbose:
        print(f"本地文件: {local_file}")
        print(f"文件大小: {file_size / 1024 / 1024:.2f} MB")
        print(f"目标 Bucket: {bucket}")
        print(f"目标 Region: {region}")
        print(f"COS Key: {cos_key}")
    
    # 创建 COS 客户端
    config = CosConfig(
        Region=region,
        SecretId=secret_id,
        SecretKey=secret_key
    )
    client = CosS3Client(config)
    
    # 上传文件
    try:
        if verbose:
            print(f"开始上传...")
        
        response = client.upload_file(
            Bucket=bucket,
            LocalFilePath=local_file,
            Key=cos_key,
            PartSize=10,  # 分块大小 10MB
            MAXThread=5,  # 最大线程数
            EnableMD5=False
        )
        
        # 构建文件 URL
        url = f"https://{bucket}.cos.{region}.myqcloud.com/{cos_key.lstrip('/')}"
        
        # 生成临时访问 URL（预签名URL，有效期1小时）
        presigned_url = None
        try:
            presigned_url = client.get_presigned_url(
                Method='GET',
                Bucket=bucket,
                Key=cos_key,
                Expired=3600  # 有效期1小时
            )
            if verbose:
                print(f"预签名URL已生成（有效期1小时）")
        except Exception as e:
            if verbose:
                print(f"生成预签名URL失败: {e}")
        
        result = {
            "ETag": response.get("ETag", ""),
            "Key": cos_key,
            "Bucket": bucket,
            "Region": region,
            "URL": url,
            "PresignedURL": presigned_url,
            "Size": file_size
        }
        
        if verbose:
            print(f"上传成功！")
            print(f"ETag: {result['ETag']}")
            print(f"URL: {url}")
        
        return result
        
    except Exception as e:
        print(f"上传失败: {e}", file=sys.stderr)
        return None


def main():
    """主函数"""
    args = parse_args()
    
    # 加载环境变量
    if _LOAD_ENV_AVAILABLE:
        loaded = ensure_env_loaded(verbose=args.verbose)
        if not loaded:
            missing = check_required_vars(["TENCENTCLOUD_SECRET_ID", "TENCENTCLOUD_SECRET_KEY"])
            _print_setup_hint(missing)
            sys.exit(1)
    
    # 获取配置（命令行参数优先，其次环境变量）
    secret_id = args.secret_id or os.environ.get("TENCENTCLOUD_SECRET_ID")
    secret_key = args.secret_key or os.environ.get("TENCENTCLOUD_SECRET_KEY")
    bucket = args.bucket or os.environ.get("TENCENTCLOUD_COS_BUCKET")
    region = args.region or os.environ.get("TENCENTCLOUD_COS_REGION") or "ap-guangzhou"
    
    # 检查必需参数
    if not secret_id or not secret_key:
        print("错误：缺少腾讯云密钥配置。请设置 TENCENTCLOUD_SECRET_ID 和 TENCENTCLOUD_SECRET_KEY 环境变量，或使用 --secret-id 和 --secret-key 参数。", file=sys.stderr)
        sys.exit(1)
    
    if not bucket:
        print("错误：缺少 COS Bucket 配置。请设置 TENCENTCLOUD_COS_BUCKET 环境变量，或使用 --bucket 参数。", file=sys.stderr)
        sys.exit(1)
    
    # 执行上传
    result = upload_file(
        local_file=args.local_file,
        cos_key=args.cos_key,
        bucket=bucket,
        region=region,
        secret_id=secret_id,
        secret_key=secret_key,
        verbose=args.verbose
    )
    
    if result:
        print("\n=== 上传成功 ===")
        print(f"文件: {args.local_file}")
        print(f"大小: {result['Size'] / 1024 / 1024:.2f} MB")
        print(f"Bucket: {result['Bucket']}")
        print(f"Key: {result['Key']}")
        print(f"永久URL: {result['URL']}")
        if result.get('PresignedURL'):
            print(f"临时URL: {result['PresignedURL']}")
            print("\n=== AIGC脚本参数（使用临时URL）===")
            print(f"--image-url '{result['PresignedURL']}'")
        print("\n=== COS路径格式（用于音视频处理脚本）===")
        print(f"--cos-input-bucket {result['Bucket']} --cos-input-region {result['Region']} --cos-input-key {result['Key']}")
        print("\n=== AIGC图片/视频脚本参数（使用COS路径，推荐）===")
        print(f"--image-cos-bucket {result['Bucket']} --image-cos-region {result['Region']} --image-cos-key {result['Key']}")
        print("\n=== AIGC视频脚本参数（首帧图片使用COS路径）===")
        print(f"--image-cos-bucket {result['Bucket']} --image-cos-region {result['Region']} --image-cos-key {result['Key']}")
        return 0
    else:
        print("\n=== 上传失败 ===", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
