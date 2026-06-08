#!/usr/bin/env python3
"""
屏幕绘图标记工具 - 在屏幕上绘制临时标记以确认坐标位置
支持绘制十字、圆圈、方框、箭头等标记
"""

import sys
import argparse
import tkinter as tk
import threading
import time

try:
    import pyautogui
except ImportError:
    print("错误: 未安装 pyautogui。请运行: pip3 install pyautogui")
    sys.exit(1)


class OverlayWindow:
    """半透明覆盖层窗口，用于绘制标记"""
    
    def __init__(self):
        self.root = None
        self.canvas = None
        self.screen_width = 0
        self.screen_height = 0
        
    def create_window(self):
        """创建全屏透明窗口"""
        self.root = tk.Tk()
        self.root.title("")
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.7)  # 透明度
        self.root.attributes('-fullscreen', True)
        self.root.configure(bg='black')
        self.root.overrideredirect(True)  # 无边框
        
        # 获取屏幕尺寸
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        
        # 创建画布
        self.canvas = tk.Canvas(
            self.root,
            width=self.screen_width,
            height=self.screen_height,
            bg='black',
            highlightthickness=0
        )
        self.canvas.pack()
        
        # 点击任意位置关闭
        self.root.bind('<Button-1>', lambda e: self.close())
        self.root.bind('<Key>', lambda e: self.close())
        
    def close(self):
        """关闭窗口"""
        if self.root:
            self.root.quit()
            self.root.destroy()
            
    def draw_cross(self, x, y, size=20, color='red', width=3):
        """绘制十字标记"""
        self.canvas.create_line(
            x - size, y, x + size, y,
            fill=color, width=width
        )
        self.canvas.create_line(
            x, y - size, x, y + size,
            fill=color, width=width
        )
        
    def draw_circle(self, x, y, radius=20, color='red', width=3):
        """绘制圆圈标记"""
        self.canvas.create_oval(
            x - radius, y - radius,
            x + radius, y + radius,
            outline=color, width=width
        )
        
    def draw_square(self, x, y, size=20, color='red', width=3):
        """绘制方框标记"""
        self.canvas.create_rectangle(
            x - size, y - size,
            x + size, y + size,
            outline=color, width=width
        )
        
    def draw_arrow(self, x, y, direction='down', size=30, color='red', width=3):
        """绘制箭头标记"""
        if direction == 'down':
            self.canvas.create_line(
                x, y - size, x, y + size,
                fill=color, width=width
            )
            self.canvas.create_line(
                x - size//2, y, x, y + size,
                fill=color, width=width
            )
            self.canvas.create_line(
                x + size//2, y, x, y + size,
                fill=color, width=width
            )
        elif direction == 'up':
            self.canvas.create_line(
                x, y - size, x, y + size,
                fill=color, width=width
            )
            self.canvas.create_line(
                x - size//2, y, x, y - size,
                fill=color, width=width
            )
            self.canvas.create_line(
                x + size//2, y, x, y - size,
                fill=color, width=width
            )
        elif direction == 'left':
            self.canvas.create_line(
                x - size, y, x + size, y,
                fill=color, width=width
            )
            self.canvas.create_line(
                x, y - size//2, x - size, y,
                fill=color, width=width
            )
            self.canvas.create_line(
                x, y + size//2, x - size, y,
                fill=color, width=width
            )
        elif direction == 'right':
            self.canvas.create_line(
                x - size, y, x + size, y,
                fill=color, width=width
            )
            self.canvas.create_line(
                x, y - size//2, x + size, y,
                fill=color, width=width
            )
            self.canvas.create_line(
                x, y + size//2, x + size, y,
                fill=color, width=width
            )
                
    def draw_target(self, x, y, size=30, color='red', width=3):
        """绘制靶心标记（圆圈+十字）"""
        self.draw_circle(x, y, size, color, width)
        self.draw_cross(x, y, size, color, width)
        
    def draw_text(self, x, y, text, color='yellow', size=14):
        """绘制文字标注"""
        self.canvas.create_text(
            x, y - 40,
            text=text,
            fill=color,
            font=('Arial', size, 'bold')
        )
        
    def draw_coordinate_info(self, x, y):
        """绘制坐标信息"""
        info_text = f"({x}, {y})"
        self.canvas.create_text(
            x, y + 50,
            text=info_text,
            fill='white',
            font=('Consolas', 12, 'bold')
        )


def draw_marker(marker_type, x, y, **kwargs):
    """在指定位置绘制标记"""
    overlay = OverlayWindow()
    overlay.create_window()
    
    size = kwargs.get('size', 30)
    color = kwargs.get('color', 'red')
    width = kwargs.get('width', 3)
    text = kwargs.get('text', None)
    duration = kwargs.get('duration', 5)
    show_info = kwargs.get('show_info', True)
    direction = kwargs.get('direction', 'down')
    
    # 绘制标记
    if marker_type == 'cross':
        overlay.draw_cross(x, y, size, color, width)
    elif marker_type == 'circle':
        overlay.draw_circle(x, y, size, color, width)
    elif marker_type == 'square':
        overlay.draw_square(x, y, size, color, width)
    elif marker_type == 'arrow':
        overlay.draw_arrow(x, y, direction, size, color, width)
    elif marker_type == 'target':
        overlay.draw_target(x, y, size, color, width)
    else:
        print(f"未知标记类型: {marker_type}")
        overlay.close()
        return
        
    # 绘制文字标注
    if text:
        overlay.draw_text(x, y, text, color, size)
        
    # 绘制坐标信息
    if show_info:
        overlay.draw_coordinate_info(x, y)
        
    # 自动关闭
    def auto_close():
        time.sleep(duration)
        try:
            overlay.close()
        except:
            pass
            
    if duration > 0:
        threading.Thread(target=auto_close, daemon=True).start()
        
    print(f"已在 ({x}, {y}) 绘制 {marker_type} 标记，持续 {duration} 秒（点击屏幕或按任意键关闭）")
    
    # 运行窗口
    overlay.root.mainloop()


def draw_area(x1, y1, x2, y2, **kwargs):
    """绘制区域框选"""
    overlay = OverlayWindow()
    overlay.create_window()
    
    color = kwargs.get('color', 'cyan')
    width = kwargs.get('width', 3)
    duration = kwargs.get('duration', 5)
    label = kwargs.get('label', None)
    
    # 绘制矩形框
    overlay.canvas.create_rectangle(
        x1, y1, x2, y2,
        outline=color, width=width
    )
    
    # 绘制对角线
    overlay.canvas.create_line(x1, y1, x2, y2, fill=color, width=1, dash=(5, 5))
    overlay.canvas.create_line(x1, y2, x2, y1, fill=color, width=1, dash=(5, 5))
    
    # 绘制中心点
    center_x = (x1 + x2) // 2
    center_y = (y1 + y2) // 2
    overlay.draw_cross(center_x, center_y, 10, color, 2)
    
    # 标注区域信息
    region_text = f"({x1}, {y1}) - ({x2}, {y2})"
    size_text = f"{x2-x1} x {y2-y1}"
    
    if label:
        overlay.canvas.create_text(
            center_x, center_y - 30,
            text=label,
            fill='yellow',
            font=('Arial', 14, 'bold')
        )
        
    overlay.canvas.create_text(
        center_x, center_y + 20,
        text=region_text,
        fill='white',
        font=('Consolas', 11)
    )
    overlay.canvas.create_text(
        center_x, center_y + 40,
        text=size_text,
        fill='white',
        font=('Consolas', 11)
    )
    
    # 自动关闭
    def auto_close():
        time.sleep(duration)
        try:
            overlay.close()
        except:
            pass
            
    if duration > 0:
        threading.Thread(target=auto_close, daemon=True).start()
        
    print(f"已绘制区域框: ({x1}, {y1}) - ({x2}, {y2})，持续 {duration} 秒（点击屏幕或按任意键关闭）")
    
    overlay.root.mainloop()


def main():
    parser = argparse.ArgumentParser(
        description='屏幕绘图标记工具 - 在屏幕上绘制临时标记以确认坐标位置',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 在 (500, 300) 绘制十字标记
  python draw_overlay.py marker cross 500 300
  
  # 绘制靶心标记，持续 10 秒
  python draw_overlay.py marker target 800 600 --duration 10
  
  # 绘制蓝色圆圈并添加文字标注
  python draw_overlay.py marker circle 500 300 --color blue --text "发送按钮"
  
  # 绘制区域框选
  python draw_overlay.py area 100 100 500 400 --label "QQ窗口"
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # marker 命令
    marker_parser = subparsers.add_parser('marker', help='在指定位置绘制标记')
    marker_parser.add_argument('type', choices=['cross', 'circle', 'square', 'arrow', 'target'],
                               help='标记类型: cross(十字), circle(圆圈), square(方框), arrow(箭头), target(靶心)')
    marker_parser.add_argument('x', type=int, help='X 坐标')
    marker_parser.add_argument('y', type=int, help='Y 坐标')
    marker_parser.add_argument('--size', type=int, default=30, help='标记大小（默认: 30）')
    marker_parser.add_argument('--color', default='red', help='标记颜色（默认: red）')
    marker_parser.add_argument('--width', type=int, default=3, help='线条粗细（默认: 3）')
    marker_parser.add_argument('--text', help='添加文字标注')
    marker_parser.add_argument('--duration', type=int, default=5, help='显示时长，秒（默认: 5，0=永久）')
    marker_parser.add_argument('--direction', choices=['up', 'down', 'left', 'right'],
                               default='down', help='箭头方向（仅 arrow 类型有效）')
    
    # area 命令
    area_parser = subparsers.add_parser('area', help='绘制区域框选')
    area_parser.add_argument('x1', type=int, help='左上角 X 坐标')
    area_parser.add_argument('y1', type=int, help='左上角 Y 坐标')
    area_parser.add_argument('x2', type=int, help='右下角 X 坐标')
    area_parser.add_argument('y2', type=int, help='右下角 Y 坐标')
    area_parser.add_argument('--color', default='cyan', help='框线颜色（默认: cyan）')
    area_parser.add_argument('--width', type=int, default=3, help='线条粗细（默认: 3）')
    area_parser.add_argument('--label', help='区域标签文字')
    area_parser.add_argument('--duration', type=int, default=5, help='显示时长，秒（默认: 5）')
    
    args = parser.parse_args()
    
    if args.command == 'marker':
        draw_marker(
            args.type, args.x, args.y,
            size=args.size,
            color=args.color,
            width=args.width,
            text=args.text,
            duration=args.duration,
            direction=args.direction
        )
    elif args.command == 'area':
        draw_area(
            args.x1, args.y1, args.x2, args.y2,
            color=args.color,
            width=args.width,
            label=args.label,
            duration=args.duration
        )
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
