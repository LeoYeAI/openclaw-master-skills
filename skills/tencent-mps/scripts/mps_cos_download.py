#!/usr/bin/env python3
"""
腾讯云 COS 文件下载脚本

功能：
  使用腾讯云 COS Python SDK 从 COS Bucket 下载文件到本地。

用法：
  # 最简用法（使用环境变量中的 bucket 和 region）
  python mps_cos_download.py --cos-key input/video.mp4 --local-file ./downloaded/video.mp4

  # 指定 bucket 和 region（覆盖环境变量）
  python mps_cos_download.py --cos-key input/video.mp4 --local-file ./video.mp4 \\
      --bucket mybucket-125xxx --region ap-guangzhou

  # 使用环境变量中的默认 bucket，只指定 cos-key
  python mps_cos_download.py --cos-key output/result.mp4 --local-file ./result.mp4

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
        description="腾讯云 COS 文件下载工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 下载文件到本地（使用环境变量中的 bucket）
  python mps_cos_download.py --cos-key input/video.mp4 --local-file ./video.mp4

  # 指定 bucket 和 region
  python mps_cos_download.py --cos-key input/video.mp4 --local-file ./video.mp4 \\
      --bucket mybucket-125xxx --region ap-guangzhou
        """
    )
    
    parser.add_argument(
        "--cos-key", "-k",
        required=True,
        help="COS 对象键（Key），如 input/video.mp4（必填）"
    )
    parser.add_argument(
        "--local-file", "-f",
        required=True,
        help="本地保存路径（必填）"
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


def download_file(cos_key, local_file, bucket, region, secret_id, secret_key, verbose=False):
    """
    从 COS 下载文件
    
    Args:
        cos_key: COS 对象键
        local_file: 本地保存路径
        bucket: COS Bucket 名称
        region: COS Bucket 区域
        secret_id: 腾讯云 SecretId
        secret_key: 腾讯云 SecretKey
        verbose: 是否显示详细日志
    
    Returns:
        dict: 下载结果，包含文件大小和本地路径
    """
    # 创建本地目录（如果不存在）
    local_dir = os.path.dirname(os.path.abspath(local_file))
    if local_dir and not os.path.exists(local_dir):
        os.makedirs(local_dir, exist_ok=True)
        if verbose:
            print(f"创建目录: {local_dir}")
    
    if verbose:
        print(f"源 Bucket: {bucket}")
        print(f"源 Region: {region}")
        print(f"COS Key: {cos_key}")
        print(f"本地保存路径: {local_file}")
    
    # 创建 COS 客户端
    config = CosConfig(
        Region=region,
        SecretId=secret_id,
        SecretKey=secret_key
    )
    client = CosS3Client(config)
    
    # 下载文件
    try:
        if verbose:
            print(f"开始下载...")
        
        response = client.download_file(
            Bucket=bucket,
            Key=cos_key.lstrip('/'),
            DestFilePath=local_file
        )
        
        # 获取下载后的文件大小
        file_size = os.path.getsize(local_file)
        
        # 构建文件 URL
        url = f"https://{bucket}.cos.{region}.myqcloud.com/{cos_key.lstrip('/')}"
        
        result = {
            "Key": cos_key,
            "Bucket": bucket,
            "Region": region,
            "LocalFile": local_file,
            "URL": url,
            "Size": file_size
        }
        
        if verbose:
            print(f"下载成功！")
            print(f"文件大小: {file_size / 1024 / 1024:.2f} MB")
        
        return result
        
    except Exception as e:
        print(f"下载失败: {e}", file=sys.stderr)
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
    
    # 执行下载
    result = download_file(
        cos_key=args.cos_key,
        local_file=args.local_file,
        bucket=bucket,
        region=region,
        secret_id=secret_id,
        secret_key=secret_key,
        verbose=args.verbose
    )
    
    if result:
        print("\n=== 下载成功 ===")
        print(f"Bucket: {result['Bucket']}")
        print(f"Key: {result['Key']}")
        print(f"本地文件: {result['LocalFile']}")
        print(f"大小: {result['Size'] / 1024 / 1024:.2f} MB")
        print(f"URL: {result['URL']}")
        return 0
    else:
        print("\n=== 下载失败 ===", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
