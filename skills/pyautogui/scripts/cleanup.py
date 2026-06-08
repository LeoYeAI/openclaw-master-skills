#!/usr/bin/env python3
"""
文件清理工具 - 清理截图和标记文件，释放磁盘空间
支持按类型、时间、大小筛选清理
"""

import sys
import argparse
import os
import glob
import time
from datetime import datetime, timedelta


def get_file_info(file_path):
    """获取文件信息"""
    try:
        stat = os.stat(file_path)
        return {
            'path': file_path,
            'size': stat.st_size,
            'size_kb': round(stat.st_size / 1024, 2),
            'mtime': stat.st_mtime,
            'mtime_str': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')
        }
    except:
        return None


def list_temp_files(directory, patterns=None):
    """列出所有临时文件"""
    if patterns is None:
        patterns = [
            '*_marked.png', '*_marked.jpg',
            '*_cropped.png', '*_cropped.jpg',
            '*_screenshot.png', '*_screenshot.jpg',
            'screen_*.png', 'screen_*.jpg',
            'qq_*.png', 'qq_*.jpg',
            '*_step*.png', '*_step*.jpg',
            '*_area_*.png', '*_area_*.jpg',
        ]
    
    files = []
    seen = set()
    
    for pattern in patterns:
        for file_path in glob.glob(os.path.join(directory, pattern)):
            if file_path not in seen and os.path.isfile(file_path):
                seen.add(file_path)
                info = get_file_info(file_path)
                if info:
                    files.append(info)
    
    return sorted(files, key=lambda x: x['mtime'], reverse=True)


def analyze_files(directory):
    """分析临时文件占用情况"""
    files = list_temp_files(directory)
    
    if not files:
        print(f"目录 '{directory}' 中没有找到临时文件")
        return
    
    total_size = sum(f['size'] for f in files)
    total_size_mb = round(total_size / 1024 / 1024, 2)
    
    print(f"\n📁 目录: {directory}")
    print(f"📊 找到 {len(files)} 个临时文件")
    print(f"💾 总占用空间: {total_size_mb} MB ({round(total_size / 1024, 2)} KB)\n")
    
    print("文件列表（按修改时间倒序）:")
    print("-" * 80)
    print(f"{'序号':<6}{'文件名':<40}{'大小':<15}{'修改时间':<20}")
    print("-" * 80)
    
    for i, f in enumerate(files[:50], 1):  # 最多显示50个
        filename = os.path.basename(f['path'])
        if len(filename) > 38:
            filename = filename[:35] + "..."
        print(f"{i:<6}{filename:<40}{f['size_kb']} KB{'':<6}{f['mtime_str']}")
    
    if len(files) > 50:
        print(f"\n... 还有 {len(files) - 50} 个文件未显示")
    
    print("-" * 80)


def clean_files(directory, days=None, size_kb=None, patterns=None, dry_run=True):
    """清理文件"""
    files = list_temp_files(directory, patterns)
    
    if not files:
        print(f"没有需要清理的文件")
        return
    
    to_delete = []
    now = time.time()
    
    for f in files:
        should_delete = False
        
        # 按时间筛选
        if days is not None:
            file_age_days = (now - f['mtime']) / (24 * 3600)
            if file_age_days >= days:
                should_delete = True
        
        # 按大小筛选
        if size_kb is not None:
            if f['size_kb'] >= size_kb:
                should_delete = True
        
        # 如果没有指定条件，删除所有
        if days is None and size_kb is None:
            should_delete = True
        
        if should_delete:
            to_delete.append(f)
    
    if not to_delete:
        print("没有符合删除条件的文件")
        return
    
    total_size = sum(f['size'] for f in to_delete)
    total_size_mb = round(total_size / 1024 / 1024, 2)
    
    print(f"\n{'[预览模式]' if dry_run else '[执行删除]'}")
    print(f"将删除 {len(to_delete)} 个文件，释放 {total_size_mb} MB 空间\n")
    
    print("待删除文件:")
    print("-" * 60)
    for f in to_delete[:20]:
        filename = os.path.basename(f['path'])
        print(f"  {filename:<45} {f['size_kb']} KB")
    
    if len(to_delete) > 20:
        print(f"  ... 还有 {len(to_delete) - 20} 个文件")
    print("-" * 60)
    
    if dry_run:
        print("\n⚠️  这是预览模式，实际并未删除文件")
        print("    如需真正删除，请添加 --execute 参数")
    else:
        deleted_count = 0
        failed_count = 0
        
        for f in to_delete:
            try:
                os.remove(f['path'])
                deleted_count += 1
                print(f"✓ 已删除: {os.path.basename(f['path'])}")
            except Exception as e:
                failed_count += 1
                print(f"✗ 删除失败: {os.path.basename(f['path'])} - {e}")
        
        print(f"\n✅ 清理完成: 成功删除 {deleted_count} 个文件，失败 {failed_count} 个")
        print(f"💾 释放空间: {total_size_mb} MB")


def auto_clean(directory, max_files=50, max_size_mb=100):
    """自动清理：当文件数或总大小超过限制时清理最旧的文件"""
    files = list_temp_files(directory)
    
    if not files:
        return
    
    total_size_mb = sum(f['size'] for f in files) / 1024 / 1024
    
    print(f"📊 当前状态: {len(files)} 个文件, {round(total_size_mb, 2)} MB")
    
    if len(files) <= max_files and total_size_mb <= max_size_mb:
        print("✅ 文件数量和大小的在限制范围内，无需清理")
        return
    
    # 按时间正序排列（最旧的在前）
    files_sorted = sorted(files, key=lambda x: x['mtime'])
    
    to_delete = []
    current_count = len(files)
    current_size_mb = total_size_mb
    
    for f in files_sorted:
        if current_count <= max_files and current_size_mb <= max_size_mb:
            break
        
        to_delete.append(f)
        current_count -= 1
        current_size_mb -= f['size'] / 1024 / 1024
    
    if to_delete:
        total_free = sum(f['size'] for f in to_delete) / 1024 / 1024
        print(f"\n🧹 自动清理: 将删除 {len(to_delete)} 个最旧的文件")
        print(f"💾 预计释放: {round(total_free, 2)} MB\n")
        
        for f in to_delete:
            try:
                os.remove(f['path'])
                print(f"✓ 已删除: {os.path.basename(f['path'])}")
            except Exception as e:
                print(f"✗ 删除失败: {os.path.basename(f['path'])} - {e}")
        
        print(f"\n✅ 自动清理完成")


def main():
    parser = argparse.ArgumentParser(
        description='文件清理工具 - 清理截图和标记文件，释放磁盘空间',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 分析当前目录的临时文件占用情况
  python cleanup.py analyze .

  # 清理超过7天的文件（预览模式）
  python cleanup.py clean . --days 7

  # 真正执行清理（超过7天的文件）
  python cleanup.py clean . --days 7 --execute

  # 清理大于1MB的文件
  python cleanup.py clean . --size 1024 --execute

  # 自动清理（保持最多50个文件或100MB）
  python cleanup.py auto . --max-files 50 --max-size 100

  # 清理所有临时文件（危险！）
  python cleanup.py clean . --execute
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # analyze 命令
    analyze_parser = subparsers.add_parser('analyze', help='分析临时文件占用情况')
    analyze_parser.add_argument('directory', help='要分析的目录')
    
    # clean 命令
    clean_parser = subparsers.add_parser('clean', help='清理文件')
    clean_parser.add_argument('directory', help='要清理的目录')
    clean_parser.add_argument('--days', type=float, help='清理超过指定天数的文件')
    clean_parser.add_argument('--size', type=float, help='清理大于指定KB的文件')
    clean_parser.add_argument('--execute', action='store_true', help='真正执行删除（默认预览模式）')
    clean_parser.add_argument('--pattern', action='append', help='自定义文件匹配模式（可多次使用）')
    
    # auto 命令
    auto_parser = subparsers.add_parser('auto', help='自动清理（超出限制时删除最旧文件）')
    auto_parser.add_argument('directory', help='要清理的目录')
    auto_parser.add_argument('--max-files', type=int, default=50, help='最大保留文件数（默认: 50）')
    auto_parser.add_argument('--max-size', type=float, default=100, help='最大占用空间MB（默认: 100）')
    
    args = parser.parse_args()
    
    if args.command == 'analyze':
        analyze_files(args.directory)
    elif args.command == 'clean':
        patterns = args.pattern if args.pattern else None
        clean_files(
            args.directory,
            days=args.days,
            size_kb=args.size,
            patterns=patterns,
            dry_run=not args.execute
        )
    elif args.command == 'auto':
        auto_clean(args.directory, args.max_files, args.max_size)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()