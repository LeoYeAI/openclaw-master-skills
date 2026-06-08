#!/usr/bin/env python3
"""
图片工具脚本 - 获取图片基本参数
支持获取图片尺寸、格式、模式等信息
"""

import sys
import argparse
import os

try:
    from PIL import Image
except ImportError:
    print("错误: 未安装 Pillow。请运行: pip3 install Pillow")
    sys.exit(1)


def get_image_info(image_path):
    """获取图片完整信息"""
    if not os.path.exists(image_path):
        print(f'错误: 文件不存在: {image_path}', file=sys.stderr)
        sys.exit(1)
    
    try:
        with Image.open(image_path) as img:
            info = {
                "path": image_path,
                "filename": os.path.basename(image_path),
                "size": {
                    "width": img.width,
                    "height": img.height
                },
                "format": img.format,
                "mode": img.mode,
                "file_size_bytes": os.path.getsize(image_path),
                "file_size_kb": round(os.path.getsize(image_path) / 1024, 2)
            }
            
            # 打印 JSON 格式结果
            import json
            print(json.dumps(info, ensure_ascii=False, indent=2))
            
    except Exception as e:
        print(f'读取图片失败: {e}', file=sys.stderr)
        sys.exit(1)


def get_image_size(image_path):
    """仅获取图片尺寸（快速模式）"""
    if not os.path.exists(image_path):
        print(f'错误: 文件不存在: {image_path}', file=sys.stderr)
        sys.exit(1)
    
    try:
        with Image.open(image_path) as img:
            print(f'{{"width": {img.width}, "height": {img.height}}}')
    except Exception as e:
        print(f'读取图片失败: {e}', file=sys.stderr)
        sys.exit(1)


def crop_image(image_path, x1, y1, x2, y2, output_path=None):
    """裁剪图片并保存"""
    if not os.path.exists(image_path):
        print(f'错误: 文件不存在: {image_path}', file=sys.stderr)
        sys.exit(1)
    
    try:
        with Image.open(image_path) as img:
            # 验证坐标
            if x1 < 0 or y1 < 0 or x2 > img.width or y2 > img.height:
                print(f'错误: 裁剪坐标超出图片范围', file=sys.stderr)
                print(f'图片尺寸: {img.width}x{img.height}, 裁剪区域: ({x1},{y1})-({x2},{y2})', file=sys.stderr)
                sys.exit(1)
            
            if x1 >= x2 or y1 >= y2:
                print(f'错误: 无效的裁剪坐标', file=sys.stderr)
                sys.exit(1)
            
            # 裁剪
            cropped = img.crop((x1, y1, x2, y2))
            
            # 保存
            if output_path is None:
                base, ext = os.path.splitext(image_path)
                output_path = f'{base}_cropped{ext}'
            
            cropped.save(output_path)
            print(f'裁剪完成: {output_path}')
            print(f'裁剪区域: ({x1}, {y1}) - ({x2}, {y2})')
            print(f'裁剪后尺寸: {cropped.width}x{cropped.height}')
            
    except Exception as e:
        print(f'裁剪图片失败: {e}', file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='图片工具 - 获取图片参数信息',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  python image_utils.py info screenshot.png          # 获取完整信息
  python image_utils.py size photo.jpg               # 仅获取尺寸
  python image_utils.py crop img.png 100 100 500 500 # 裁剪图片
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # info 命令
    info_parser = subparsers.add_parser('info', help='获取图片完整信息')
    info_parser.add_argument('image_path', help='图片文件路径')
    
    # size 命令
    size_parser = subparsers.add_parser('size', help='仅获取图片尺寸')
    size_parser.add_argument('image_path', help='图片文件路径')
    
    # crop 命令
    crop_parser = subparsers.add_parser('crop', help='裁剪图片')
    crop_parser.add_argument('image_path', help='图片文件路径')
    crop_parser.add_argument('x1', type=int, help='左上角 x 坐标')
    crop_parser.add_argument('y1', type=int, help='左上角 y 坐标')
    crop_parser.add_argument('x2', type=int, help='右下角 x 坐标')
    crop_parser.add_argument('y2', type=int, help='右下角 y 坐标')
    crop_parser.add_argument('-o', '--output', help='输出文件路径（可选）')
    
    args = parser.parse_args()
    
    if args.command == 'info':
        get_image_info(args.image_path)
    elif args.command == 'size':
        get_image_size(args.image_path)
    elif args.command == 'crop':
        crop_image(args.image_path, args.x1, args.y1, args.x2, args.y2, args.output)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
