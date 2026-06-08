#!/usr/bin/env python3
"""
图片绘制工具 - 在图片上绘制标记并保存
支持绘制十字、圆圈、方框、箭头、文字等标记
"""

import sys
import argparse
import os

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("错误: 未安装 Pillow。请运行: pip3 install Pillow")
    sys.exit(1)


def get_default_font(size=20):
    """获取默认字体"""
    font_paths = [
        "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
        "C:/Windows/Fonts/simsun.ttc",  # 宋体
        "C:/Windows/Fonts/arial.ttf",  # Arial
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Linux
        "/System/Library/Fonts/Helvetica.ttc",  # macOS
    ]
    
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                pass
    
    # 如果找不到字体，使用默认字体
    return ImageFont.load_default()


def draw_marker_on_image(image_path, output_path, marker_type, x, y, **kwargs):
    """在图片上绘制标记"""
    if not os.path.exists(image_path):
        print(f"错误: 文件不存在: {image_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # 打开图片
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        
        size = kwargs.get('size', 30)
        color = kwargs.get('color', 'red')
        width = kwargs.get('width', 3)
        text = kwargs.get('text', None)
        font_size = kwargs.get('font_size', 20)
        direction = kwargs.get('direction', 'down')
        
        # 转换颜色名称到 RGB
        color_map = {
            'red': (255, 0, 0),
            'green': (0, 255, 0),
            'blue': (0, 0, 255),
            'yellow': (255, 255, 0),
            'cyan': (0, 255, 255),
            'magenta': (255, 0, 255),
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'orange': (255, 165, 0),
        }
        
        if isinstance(color, str):
            color = color_map.get(color.lower(), (255, 0, 0))
        
        # 绘制标记
        if marker_type == 'cross':
            # 十字线
            draw.line([(x - size, y), (x + size, y)], fill=color, width=width)
            draw.line([(x, y - size), (x, y + size)], fill=color, width=width)
            
        elif marker_type == 'circle':
            # 圆圈
            draw.ellipse(
                [(x - size, y - size), (x + size, y + size)],
                outline=color, width=width
            )
            
        elif marker_type == 'square':
            # 方框
            draw.rectangle(
                [(x - size, y - size), (x + size, y + size)],
                outline=color, width=width
            )
            
        elif marker_type == 'arrow':
            # 箭头
            if direction == 'down':
                draw.line([(x, y - size), (x, y + size)], fill=color, width=width)
                draw.line([(x, y + size), (x - size//2, y)], fill=color, width=width)
                draw.line([(x, y + size), (x + size//2, y)], fill=color, width=width)
            elif direction == 'up':
                draw.line([(x, y - size), (x, y + size)], fill=color, width=width)
                draw.line([(x, y - size), (x - size//2, y)], fill=color, width=width)
                draw.line([(x, y - size), (x + size//2, y)], fill=color, width=width)
            elif direction == 'left':
                draw.line([(x - size, y), (x + size, y)], fill=color, width=width)
                draw.line([(x - size, y), (x, y - size//2)], fill=color, width=width)
                draw.line([(x - size, y), (x, y + size//2)], fill=color, width=width)
            elif direction == 'right':
                draw.line([(x - size, y), (x + size, y)], fill=color, width=width)
                draw.line([(x + size, y), (x, y - size//2)], fill=color, width=width)
                draw.line([(x + size, y), (x, y + size//2)], fill=color, width=width)
                
        elif marker_type == 'target':
            # 靶心（圆圈+十字）
            draw.ellipse(
                [(x - size, y - size), (x + size, y + size)],
                outline=color, width=width
            )
            draw.line([(x - size, y), (x + size, y)], fill=color, width=width)
            draw.line([(x, y - size), (x, y + size)], fill=color, width=width)
            # 中心点
            r = 3
            draw.ellipse([(x - r, y - r), (x + r, y + r)], fill=color)
            
        elif marker_type == 'point':
            # 点标记
            r = size // 2
            draw.ellipse([(x - r, y - r), (x + r, y + r)], fill=color)
            
        # 绘制文字标注
        if text:
            font = get_default_font(font_size)
            # 计算文字位置（标记上方）
            text_y = y - size - font_size - 10
            
            # 获取文字尺寸
            bbox = draw.textbbox((0, 0), text, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_x = x - text_width // 2
            
            # 绘制文字背景
            padding = 4
            draw.rectangle(
                [(text_x - padding, text_y - padding),
                 (text_x + text_width + padding, text_y + text_height + padding)],
                fill=(255, 255, 255, 200)
            )
            
            # 绘制文字
            draw.text((text_x, text_y), text, fill=color, font=font)
        
        # 绘制坐标信息
        show_coord = kwargs.get('show_coord', True)
        if show_coord:
            coord_text = f"({x}, {y})"
            font = get_default_font(14)
            coord_y = y + size + 10
            
            bbox = draw.textbbox((0, 0), coord_text, font=font)
            text_width = bbox[2] - bbox[0]
            coord_x = x - text_width // 2
            
            draw.text((coord_x, coord_y), coord_text, fill=color, font=font)
        
        # 保存图片
        img.save(output_path)
        print(f"已保存标记图片: {output_path}")
        print(f"标记类型: {marker_type}, 位置: ({x}, {y})")
        
    except Exception as e:
        print(f"绘制标记失败: {e}", file=sys.stderr)
        sys.exit(1)


def draw_area_on_image(image_path, output_path, x1, y1, x2, y2, **kwargs):
    """在图片上绘制区域框"""
    if not os.path.exists(image_path):
        print(f"错误: 文件不存在: {image_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        
        color = kwargs.get('color', 'cyan')
        width = kwargs.get('width', 3)
        label = kwargs.get('label', None)
        font_size = kwargs.get('font_size', 16)
        
        # 转换颜色
        color_map = {
            'red': (255, 0, 0), 'green': (0, 255, 0), 'blue': (0, 0, 255),
            'yellow': (255, 255, 0), 'cyan': (0, 255, 255), 'magenta': (255, 0, 255),
            'white': (255, 255, 255), 'black': (0, 0, 0), 'orange': (255, 165, 0),
        }
        if isinstance(color, str):
            color = color_map.get(color.lower(), (0, 255, 255))
        
        # 绘制矩形框
        draw.rectangle([(x1, y1), (x2, y2)], outline=color, width=width)
        
        # 绘制对角线
        draw.line([(x1, y1), (x2, y2)], fill=color, width=1)
        draw.line([(x1, y2), (x2, y1)], fill=color, width=1)
        
        # 中心点
        center_x = (x1 + x2) // 2
        center_y = (y1 + y2) // 2
        r = 4
        draw.ellipse([(center_x - r, center_y - r), (center_x + r, center_y + r)], fill=color)
        
        # 绘制标签
        if label:
            font = get_default_font(font_size)
            bbox = draw.textbbox((0, 0), label, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            
            label_x = x1 + 5
            label_y = y1 - text_height - 8
            
            if label_y < 0:
                label_y = y1 + 5
            
            # 文字背景
            draw.rectangle(
                [(label_x - 2, label_y - 2),
                 (label_x + text_width + 4, label_y + text_height + 4)],
                fill=(255, 255, 255, 180)
            )
            draw.text((label_x, label_y), label, fill=color, font=font)
        
        # 区域信息
        region_text = f"{x2-x1} x {y2-y1}"
        font = get_default_font(12)
        bbox = draw.textbbox((0, 0), region_text, font=font)
        text_width = bbox[2] - bbox[0]
        draw.text((center_x - text_width//2, center_y + 10), region_text, fill=color, font=font)
        
        # 保存
        img.save(output_path)
        print(f"已保存区域标记图片: {output_path}")
        print(f"区域: ({x1}, {y1}) - ({x2}, {y2}), 尺寸: {x2-x1} x {y2-y1}")
        
    except Exception as e:
        print(f"绘制区域失败: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description='图片绘制工具 - 在图片上绘制标记并保存',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 在图片上绘制十字标记
  python draw_on_image.py input.png marker cross 500 300

  # 绘制靶心标记并保存到新文件
  python draw_on_image.py input.png marker target 800 600 -o output.png

  # 绘制红色圆圈并添加文字标注
  python draw_on_image.py input.png marker circle 500 300 --color red --text "发送按钮"

  # 绘制区域框选
  python draw_on_image.py input.png area 100 100 500 400 -o marked.png --label "QQ窗口"

  # 批量标记多个点
  python draw_on_image.py input.png marker target 3788 2080 --text "发送按钮" -o step1.png
  python draw_on_image.py step1.png marker target 3790 2090 --text "发送按钮-修正" -o step2.png
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # marker 命令
    marker_parser = subparsers.add_parser('marker', help='在图片上绘制标记')
    marker_parser.add_argument('image', help='输入图片路径')
    marker_parser.add_argument('type', choices=['cross', 'circle', 'square', 'arrow', 'target', 'point'],
                               help='标记类型: cross(十字), circle(圆圈), square(方框), arrow(箭头), target(靶心), point(点)')
    marker_parser.add_argument('x', type=int, help='X 坐标')
    marker_parser.add_argument('y', type=int, help='Y 坐标')
    marker_parser.add_argument('-o', '--output', help='输出图片路径（默认覆盖原图）')
    marker_parser.add_argument('--size', type=int, default=30, help='标记大小（默认: 30）')
    marker_parser.add_argument('--color', default='red', help='标记颜色（默认: red）')
    marker_parser.add_argument('--width', type=int, default=3, help='线条粗细（默认: 3）')
    marker_parser.add_argument('--text', help='添加文字标注')
    marker_parser.add_argument('--font-size', type=int, default=20, help='字体大小（默认: 20）')
    marker_parser.add_argument('--direction', choices=['up', 'down', 'left', 'right'],
                               default='down', help='箭头方向（仅 arrow 类型有效）')
    marker_parser.add_argument('--no-coord', action='store_true', help='不显示坐标信息')
    
    # area 命令
    area_parser = subparsers.add_parser('area', help='在图片上绘制区域框')
    area_parser.add_argument('image', help='输入图片路径')
    area_parser.add_argument('x1', type=int, help='左上角 X 坐标')
    area_parser.add_argument('y1', type=int, help='左上角 Y 坐标')
    area_parser.add_argument('x2', type=int, help='右下角 X 坐标')
    area_parser.add_argument('y2', type=int, help='右下角 Y 坐标')
    area_parser.add_argument('-o', '--output', help='输出图片路径（默认覆盖原图）')
    area_parser.add_argument('--color', default='cyan', help='框线颜色（默认: cyan）')
    area_parser.add_argument('--width', type=int, default=3, help='线条粗细（默认: 3）')
    area_parser.add_argument('--label', help='区域标签文字')
    area_parser.add_argument('--font-size', type=int, default=16, help='字体大小（默认: 16）')
    
    args = parser.parse_args()
    
    if args.command == 'marker':
        output = args.output or args.image
        draw_marker_on_image(
            args.image, output, args.type, args.x, args.y,
            size=args.size,
            color=args.color,
            width=args.width,
            text=args.text,
            font_size=args.font_size,
            direction=args.direction,
            show_coord=not args.no_coord
        )
    elif args.command == 'area':
        output = args.output or args.image
        draw_area_on_image(
            args.image, output, args.x1, args.y1, args.x2, args.y2,
            color=args.color,
            width=args.width,
            label=args.label,
            font_size=args.font_size
        )
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
