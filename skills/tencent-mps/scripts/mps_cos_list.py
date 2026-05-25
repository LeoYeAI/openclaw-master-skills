#!/usr/bin/env python3
"""
腾讯云 COS 文件列表脚本

功能：
  使用腾讯云 COS Python SDK 列出指定 Bucket 中的文件列表，支持路径前缀过滤和文件名搜索。

用法：
  # 列出 Bucket 根目录下的所有文件（使用环境变量中的 bucket）
  python mps_cos_list.py

  # 列出指定路径下的文件
  python mps_cos_list.py --prefix output/transcode/

  # 搜索指定文件名的文件（模糊匹配）
  python mps_cos_list.py --search video

  # 精确匹配文件名
  python mps_cos_list.py --search "result.mp4" --exact

  # 指定 bucket 和 region
  python mps_cos_list.py --prefix input/ --bucket mybucket-125xxx --region ap-guangzhou

  # 限制返回数量
  python mps_cos_list.py --prefix output/ --limit 50

环境变量：
  TENCENTCLOUD_SECRET_ID   - 腾讯云 SecretId
  TENCENTCLOUD_SECRET_KEY  - 腾讯云 SecretKey
  TENCENTCLOUD_COS_BUCKET  - COS Bucket 名称（如 mybucket-125xxx）
  TENCENTCLOUD_COS_REGION  - COS Bucket 区域（默认 ap-guangzhou）
"""

import argparse
import os
import sys
from datetime import datetime

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
        description="腾讯云 COS 文件列表工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例：
  # 列出 Bucket 根目录所有文件
  python mps_cos_list.py

  # 列出指定路径下的文件
  python mps_cos_list.py --prefix output/transcode/

  # 模糊搜索文件名包含 "video" 的文件
  python mps_cos_list.py --search video

  # 精确匹配文件名 "result.mp4"
  python mps_cos_list.py --search "result.mp4" --exact

  # 列出前 50 个文件
  python mps_cos_list.py --prefix output/ --limit 50
        """
    )
    
    parser.add_argument(
        "--prefix", "-p",
        default="",
        help="路径前缀，用于过滤指定目录下的文件（如 output/transcode/）"
    )
    parser.add_argument(
        "--search", "-s",
        default=None,
        help="文件名搜索关键字，支持模糊匹配"
    )
    parser.add_argument(
        "--exact",
        action="store_true",
        help="精确匹配模式，只返回文件名完全匹配的文件"
    )
    parser.add_argument(
        "--limit", "-l",
        type=int,
        default=1000,
        help="最大返回文件数量（默认 1000，最大 1000）"
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
    parser.add_argument(
        "--show-url",
        action="store_true",
        help="显示文件完整 URL"
    )
    
    return parser.parse_args()


def format_size(size_bytes):
    """格式化文件大小"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.2f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / 1024 / 1024:.2f} MB"
    else:
        return f"{size_bytes / 1024 / 1024 / 1024:.2f} GB"


def format_time(time_str):
    """格式化时间字符串"""
    try:
        # COS 返回的时间格式: 2024-01-15T08:30:00.000Z
        dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return time_str


def match_filename(key, search_term, exact=False):
    """
    匹配文件名
    
    Args:
        key: COS 对象键（完整路径）
        search_term: 搜索关键字
        exact: 是否精确匹配
    
    Returns:
        bool: 是否匹配
    """
    if not search_term:
        return True
    
    # 获取文件名（去掉路径）
    filename = os.path.basename(key)
    
    if exact:
        return filename == search_term
    else:
        # 模糊匹配：文件名包含搜索关键字（不区分大小写）
        return search_term.lower() in filename.lower()


def list_files(bucket, region, secret_id, secret_key, prefix="", search_term=None, 
               exact=False, limit=1000, show_url=False, verbose=False):
    """
    列出 COS Bucket 中的文件
    
    Args:
        bucket: COS Bucket 名称
        region: COS Bucket 区域
        secret_id: 腾讯云 SecretId
        secret_key: 腾讯云 SecretKey
        prefix: 路径前缀
        search_term: 文件名搜索关键字
        exact: 是否精确匹配
        limit: 最大返回数量
        show_url: 是否显示完整 URL
        verbose: 是否显示详细日志
    
    Returns:
        list: 文件列表
    """
    # 创建 COS 客户端
    config = CosConfig(
        Region=region,
        SecretId=secret_id,
        SecretKey=secret_key
    )
    client = CosS3Client(config)
    
    if verbose:
        print(f"Bucket: {bucket}")
        print(f"Region: {region}")
        print(f"Prefix: {prefix if prefix else '(根目录)'}")
        if search_term:
            match_type = "精确匹配" if exact else "模糊匹配"
            print(f"搜索: {search_term} ({match_type})")
        print(f"限制: 最多 {limit} 个文件")
        print("-" * 60)
    
    # 列出文件
    files = []
    marker = ""
    
    try:
        while len(files) < limit:
            # 每次请求最多 1000 个
            max_keys = min(1000, limit - len(files))
            
            response = client.list_objects(
                Bucket=bucket,
                Prefix=prefix,
                Marker=marker,
                MaxKeys=max_keys
            )
            
            # 获取文件列表
            contents = response.get('Contents', [])
            
            for item in contents:
                key = item.get('Key', '')
                
                # 跳过目录（以 / 结尾的 key）
                if key.endswith('/'):
                    continue
                
                # 文件名匹配检查
                if not match_filename(key, search_term, exact):
                    continue
                
                file_info = {
                    'Key': key,
                    'Size': int(item.get('Size', 0)),
                    'LastModified': item.get('LastModified', ''),
                    'ETag': item.get('ETag', '').strip('"'),
                }
                
                if show_url:
                    file_info['URL'] = f"https://{bucket}.cos.{region}.myqcloud.com/{key.lstrip('/')}"
                
                files.append(file_info)
                
                if len(files) >= limit:
                    break
            
            # 检查是否还有更多文件
            is_truncated = response.get('IsTruncated', 'false')
            if is_truncated == 'false' or is_truncated == False:
                break
            
            # 获取下一页的 marker
            marker = response.get('NextMarker', '')
            if not marker:
                break
        
        return files
        
    except Exception as e:
        print(f"列出文件失败: {e}", file=sys.stderr)
        return None


def print_files(files, show_url=False, bucket=None, region=None):
    """
    打印文件列表
    
    Args:
        files: 文件列表
        show_url: 是否显示 URL
        bucket: Bucket 名称
        region: 区域
    """
    if not files:
        print("未找到文件。")
        return
    
    print(f"\n共找到 {len(files)} 个文件\n")
    
    # 表头
    if show_url:
        print(f"{'序号':<6} {'文件名':<40} {'大小':<12} {'修改时间':<20} {'URL'}")
        print("-" * 120)
    else:
        print(f"{'序号':<6} {'文件名':<50} {'大小':<12} {'修改时间'}")
        print("-" * 90)
    
    # 打印文件信息
    for idx, file in enumerate(files, 1):
        key = file['Key']
        filename = os.path.basename(key)
        size = format_size(file['Size'])
        last_modified = format_time(file['LastModified'])
        
        # 截断文件名以适应显示
        display_name = filename[:38] + "..." if len(filename) > 40 else filename
        
        if show_url:
            url = file.get('URL', '')
            print(f"{idx:<6} {display_name:<40} {size:<12} {last_modified:<20} {url}")
        else:
            print(f"{idx:<6} {display_name:<50} {size:<12} {last_modified}")
    
    print()
    
    # 统计信息
    total_size = sum(f['Size'] for f in files)
    print(f"总大小: {format_size(total_size)}")


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
    
    # 限制最大返回数量
    limit = min(args.limit, 1000)
    
    # 列出文件
    files = list_files(
        bucket=bucket,
        region=region,
        secret_id=secret_id,
        secret_key=secret_key,
        prefix=args.prefix,
        search_term=args.search,
        exact=args.exact,
        limit=limit,
        show_url=args.show_url,
        verbose=args.verbose
    )
    
    if files is not None:
        print_files(files, show_url=args.show_url, bucket=bucket, region=region)
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
