#!/usr/bin/env python3
"""
图像查找工具 - 以图找图、以文找图
支持模板匹配和OCR文字识别定位屏幕元素
"""

import sys
import argparse
import os
import time

try:
    import pyautogui
    import numpy as np
except ImportError:
    print("错误: 缺少依赖。请运行: pip install pyautogui numpy")
    sys.exit(1)

try:
    import cv2
except ImportError:
    print("错误: 未安装 opencv-python。请运行: pip install opencv-python")
    sys.exit(1)


def find_image_on_screen(template_path, threshold=0.8, all_matches=False, max_results=10):
    """
    在屏幕上查找模板图片
    
    Args:
        template_path: 模板图片路径
        threshold: 匹配阈值 (0-1)
        all_matches: 是否返回所有匹配结果
        max_results: 最多返回的结果数
    
    Returns:
        单个结果: (x, y, confidence) 或 None
        多个结果: [(x, y, confidence), ...]
    """
    if not os.path.exists(template_path):
        print(f"错误: 模板文件不存在: {template_path}", file=sys.stderr)
        sys.exit(1)
    
    try:
        # 截图
        screenshot = pyautogui.screenshot()
        screenshot_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        screenshot_gray = cv2.cvtColor(screenshot_cv, cv2.COLOR_BGR2GRAY)
        
        # 读取模板
        template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        if template is None:
            print(f"错误: 无法读取模板图片: {template_path}", file=sys.stderr)
            sys.exit(1)
        
        template_h, template_w = template.shape[:2]
        
        # 模板匹配
        result = cv2.matchTemplate(screenshot_gray, template, cv2.TM_CCOEFF_NORMED)
        
        if all_matches:
            # 获取所有匹配位置
            locations = np.where(result >= threshold)
            matches = []
            
            for pt in zip(*locations[::-1]):
                x = pt[0] + template_w // 2
                y = pt[1] + template_h // 2
                confidence = result[pt[1], pt[0]]
                matches.append((x, y, float(confidence)))
                
                if len(matches) >= max_results:
                    break
            
            # 去重（距离太近的认为是同一个）
            filtered = []
            for match in matches:
                x, y, conf = match
                is_duplicate = False
                for existing in filtered:
                    ex, ey, _ = existing
                    if abs(x - ex) < template_w // 2 and abs(y - ey) < template_h // 2:
                        is_duplicate = True
                        break
                if not is_duplicate:
                    filtered.append(match)
            
            return filtered
        else:
            # 获取最佳匹配
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= threshold:
                x = max_loc[0] + template_w // 2
                y = max_loc[1] + template_h // 2
                return (x, y, float(max_val))
            else:
                return None
                
    except Exception as e:
        print(f"查找图片失败: {e}", file=sys.stderr)
        sys.exit(1)


def find_text_on_screen_ocr(text, confidence_threshold=0.5):
    """
    使用RapidOCR在屏幕上查找文字
    
    Args:
        text: 要查找的文字
        confidence_threshold: OCR置信度阈值
    
    Returns:
        [(x, y, matched_text, confidence), ...] 或 []
    """
    try:
        from rapidocr_onnxruntime import RapidOCR
    except ImportError:
        print("错误: 未安装 RapidOCR。请运行: pip install rapidocr_onnxruntime", file=sys.stderr)
        sys.exit(1)
    
    try:
        # 截图
        screenshot = pyautogui.screenshot()
        temp_path = ".temp_screenshot.png"
        screenshot.save(temp_path)
        
        # 初始化OCR（RapidOCR首次使用较快）
        print("正在初始化OCR引擎...")
        ocr = RapidOCR()
        
        # OCR识别
        result, elapse = ocr(temp_path)
        
        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        matches = []
        
        if result:
            for box, detected_text, confidence in result:
                if confidence >= confidence_threshold and text in detected_text:
                    # 计算文字中心点 (box是四个角的坐标 [[x1,y1],[x2,y2],[x3,y3],[x4,y4]])
                    x_coords = [point[0] for point in box]
                    y_coords = [point[1] for point in box]
                    center_x = int(sum(x_coords) / len(x_coords))
                    center_y = int(sum(y_coords) / len(y_coords))
                    
                    matches.append((center_x, center_y, detected_text, float(confidence)))
        
        return matches
        
    except Exception as e:
        print(f"OCR识别失败: {e}", file=sys.stderr)
        # 清理临时文件
        if os.path.exists(".temp_screenshot.png"):
            os.remove(".temp_screenshot.png")
        sys.exit(1)


def find_all_text_on_screen(confidence_threshold=0.5):
    """
    识别屏幕上的所有文字
    
    Returns:
        [(x, y, text, confidence), ...]
    """
    try:
        from rapidocr_onnxruntime import RapidOCR
    except ImportError:
        print("错误: 未安装 RapidOCR。请运行: pip install rapidocr_onnxruntime", file=sys.stderr)
        sys.exit(1)
    
    try:
        # 截图
        screenshot = pyautogui.screenshot()
        temp_path = ".temp_screenshot.png"
        screenshot.save(temp_path)
        
        # 初始化OCR
        print("正在初始化OCR引擎...")
        ocr = RapidOCR()
        
        # OCR识别
        result, elapse = ocr(temp_path)
        
        # 清理临时文件
        if os.path.exists(temp_path):
            os.remove(temp_path)
        
        texts = []
        
        if result:
            for box, detected_text, confidence in result:
                if confidence >= confidence_threshold:
                    # 计算文字中心点
                    x_coords = [point[0] for point in box]
                    y_coords = [point[1] for point in box]
                    center_x = int(sum(x_coords) / len(x_coords))
                    center_y = int(sum(y_coords) / len(y_coords))
                    
                    texts.append((center_x, center_y, detected_text, float(confidence)))
        
        return texts
        
    except Exception as e:
        print(f"OCR识别失败: {e}", file=sys.stderr)
        if os.path.exists(".temp_screenshot.png"):
            os.remove(".temp_screenshot.png")
        sys.exit(1)


def draw_markers_on_result(matches, marker_type='target'):
    """在屏幕上绘制标记显示查找结果"""
    if not matches:
        print("未找到匹配项")
        return
    
    print(f"\n找到 {len(matches)} 个匹配项，将在屏幕上标记位置（点击屏幕继续）...\n")
    
    # 导入绘图模块
    try:
        import tkinter as tk
        import threading
        
        class ResultOverlay:
            def __init__(self):
                self.root = tk.Tk()
                self.root.attributes('-topmost', True)
                self.root.attributes('-alpha', 0.6)
                self.root.attributes('-fullscreen', True)
                self.root.configure(bg='black')
                self.root.overrideredirect(True)
                
                screen_width = self.root.winfo_screenwidth()
                screen_height = self.root.winfo_screenheight()
                
                self.canvas = tk.Canvas(
                    self.root,
                    width=screen_width,
                    height=screen_height,
                    bg='black',
                    highlightthickness=0
                )
                self.canvas.pack()
                
                self.root.bind('<Button-1>', lambda e: self.close())
                self.root.bind('<Key>', lambda e: self.close())
                
            def close(self):
                self.root.quit()
                self.root.destroy()
                
            def draw_marker(self, x, y, text, color='red'):
                size = 25
                self.canvas.create_line(x-size, y, x+size, y, fill=color, width=3)
                self.canvas.create_line(x, y-size, x, y+size, fill=color, width=3)
                self.canvas.create_oval(x-5, y-5, x+5, y+5, fill=color)
                
                if text:
                    self.canvas.create_text(
                        x, y-40,
                        text=text,
                        fill='yellow',
                        font=('Arial', 12, 'bold')
                    )
        
        overlay = ResultOverlay()
        
        for match in matches:
            if len(match) == 3:
                # 图片匹配结果: (x, y, confidence)
                x, y, conf = match
                text = f"({x}, {y}) {conf:.2%}"
            else:
                # OCR结果: (x, y, text, confidence)
                x, y, txt, conf = match
                text = f"{txt[:10]} ({conf:.0%})"
            
            overlay.draw_marker(x, y, text)
        
        # 显示提示
        overlay.canvas.create_text(
            overlay.root.winfo_screenwidth() // 2,
            50,
            text=f"找到 {len(matches)} 个结果，点击或按键关闭",
            fill='white',
            font=('Arial', 16, 'bold')
        )
        
        overlay.root.mainloop()
        
    except Exception as e:
        print(f"绘制标记失败: {e}")
        # 直接打印结果
        for i, match in enumerate(matches, 1):
            if len(match) == 3:
                x, y, conf = match
                print(f"  [{i}] 位置: ({x}, {y}), 置信度: {conf:.2%}")
            else:
                x, y, txt, conf = match
                print(f"  [{i}] 文字: '{txt}', 位置: ({x}, {y}), 置信度: {conf:.2%}")


def draw_matches_on_image(image_path, output_path, matches):
    """
    在图片上标记所有匹配候选位置，带编号
    用于 AI 辅助判断哪个候选是正确的
    """
    if not matches:
        print("未找到匹配项，无法标记")
        return False
    
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # 打开图片
        img = Image.open(image_path)
        draw = ImageDraw.Draw(img)
        
        # 尝试加载字体
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 20)
            small_font = ImageFont.truetype("C:/Windows/Fonts/msyh.ttc", 14)
        except:
            font = ImageFont.load_default()
            small_font = font
        
        # 为每个匹配绘制标记
        colors = ['red', 'green', 'blue', 'yellow', 'magenta', 'cyan', 'orange']
        
        for i, match in enumerate(matches, 1):
            color = colors[(i-1) % len(colors)]
            
            if len(match) == 3:
                # 图片匹配结果: (x, y, confidence)
                x, y, conf = match
                label = f"[{i}] {conf:.0%}"
            else:
                # OCR结果: (x, y, text, confidence)
                x, y, txt, conf = match
                label = f"[{i}] {txt}"
            
            # 绘制十字标记
            size = 20
            draw.line([(x-size, y), (x+size, y)], fill=color, width=3)
            draw.line([(x, y-size), (x, y+size)], fill=color, width=3)
            
            # 绘制圆圈
            r = 8
            draw.ellipse([(x-r, y-r), (x+r, y+r)], outline=color, width=2)
            
            # 绘制编号标签（在标记右上方）
            label_x = x + 15
            label_y = y - 25
            
            # 标签背景
            bbox = draw.textbbox((0, 0), label, font=font)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            draw.rectangle(
                [(label_x - 2, label_y - 2),
                 (label_x + text_width + 4, label_y + text_height + 4)],
                fill='white'
            )
            
            # 标签文字
            draw.text((label_x, label_y), label, fill=color, font=font)
            
            # 在图片底部列出所有候选信息
            info_y = img.height - 30 - (len(matches) - i) * 25
            info_text = f"[{i}] ({x}, {y})"
            if len(match) == 4:
                info_text += f" '{match[2]}' {match[3]:.0%}"
            else:
                info_text += f" {match[2]:.0%}"
            
            draw.text((10, info_y), info_text, fill=color, font=small_font)
        
        # 保存标记后的图片
        img.save(output_path)
        print(f"\n✅ 已保存标记图片: {output_path}")
        print(f"标记了 {len(matches)} 个候选位置")
        return True
        
    except Exception as e:
        print(f"在图片上标记失败: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='图像查找工具 - 以图找图、以文找图',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例:
  # 以图找图（查找单个最佳匹配）
  python image_finder.py image button.png
  
  # 以图找图（查找所有匹配）
  python image_finder.py image button.png --all
  
  # 调整匹配阈值（更严格）
  python image_finder.py image button.png --threshold 0.95
  
  # 以文找图（查找屏幕上的文字）
  python image_finder.py text "发送"
  
  # 识别屏幕上所有文字
  python image_finder.py text-all
  
  # 查找并标记在屏幕上
  python image_finder.py image button.png --mark
  python image_finder.py text "确定" --mark
  
  # 在图片上标记所有候选（用于AI判断选择）
  python image_finder.py text "发送" --mark-on-image checked.png
  python image_finder.py image button.png --all --mark-on-image checked.png
        '''
    )
    
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # image 命令 - 以图找图
    image_parser = subparsers.add_parser('image', help='以图找图')
    image_parser.add_argument('template', help='模板图片路径')
    image_parser.add_argument('--threshold', type=float, default=0.8, help='匹配阈值 0-1（默认: 0.8）')
    image_parser.add_argument('--all', action='store_true', help='返回所有匹配结果')
    image_parser.add_argument('--max', type=int, default=10, help='最多返回结果数（默认: 10）')
    image_parser.add_argument('--mark', action='store_true', help='在屏幕上标记结果')
    image_parser.add_argument('--mark-on-image', help='在图片上标记所有候选并保存到指定路径')
    image_parser.add_argument('--click', action='store_true', help='点击第一个匹配位置')
    
    # text 命令 - 以文找图
    text_parser = subparsers.add_parser('text', help='以文找图')
    text_parser.add_argument('text', help='要查找的文字')
    text_parser.add_argument('--confidence', type=float, default=0.5, help='OCR置信度阈值（默认: 0.5）')
    text_parser.add_argument('--mark', action='store_true', help='在屏幕上标记结果')
    text_parser.add_argument('--mark-on-image', help='在图片上标记所有候选并保存到指定路径')
    text_parser.add_argument('--click', action='store_true', help='点击第一个匹配位置')
    
    # text-all 命令 - 识别所有文字
    text_all_parser = subparsers.add_parser('text-all', help='识别屏幕上所有文字')
    text_all_parser.add_argument('--confidence', type=float, default=0.8, help='OCR置信度阈值（默认: 0.8）')
    text_all_parser.add_argument('--mark', action='store_true', help='在屏幕上标记结果')
    
    args = parser.parse_args()
    
    if args.command == 'image':
        print(f"正在查找图片: {args.template} (阈值: {args.threshold})")
        result = find_image_on_screen(
            args.template,
            threshold=args.threshold,
            all_matches=args.all,
            max_results=args.max
        )
        
        if result:
            if args.all:
                print(f"\n✅ 找到 {len(result)} 个匹配项:")
                for i, (x, y, conf) in enumerate(result, 1):
                    print(f"  [{i}] 位置: ({x}, {y}), 相似度: {conf:.2%}")
                
                if args.mark:
                    draw_markers_on_result(result)
                
                if args.mark_on_image:
                    # 截图并在图片上标记所有候选
                    screenshot = pyautogui.screenshot()
                    temp_path = ".temp_screenshot.png"
                    screenshot.save(temp_path)
                    draw_matches_on_image(temp_path, args.mark_on_image, result)
                    os.remove(temp_path)
                
                if args.click and result:
                    x, y, _ = result[0]
                    print(f"\n点击第一个匹配位置: ({x}, {y})")
                    pyautogui.click(x, y)
            else:
                x, y, conf = result
                print(f"\n✅ 找到匹配: 位置 ({x}, {y}), 相似度: {conf:.2%}")
                
                if args.mark:
                    draw_markers_on_result([result])
                
                if args.click:
                    print(f"\n点击位置: ({x}, {y})")
                    pyautogui.click(x, y)
        else:
            print(f"\n❌ 未找到匹配（相似度 < {args.threshold}）")
            sys.exit(1)
            
    elif args.command == 'text':
        print(f"正在查找文字: '{args.text}'")
        result = find_text_on_screen_ocr(args.text, args.confidence)
        
        if result:
            print(f"\n✅ 找到 {len(result)} 处包含 '{args.text}' 的文字:")
            for i, (x, y, txt, conf) in enumerate(result, 1):
                print(f"  [{i}] 文字: '{txt}', 位置: ({x}, {y}), 置信度: {conf:.2%}")
            
            if args.mark:
                draw_markers_on_result(result)
            
            if args.mark_on_image:
                # 截图并在图片上标记所有候选
                screenshot = pyautogui.screenshot()
                temp_path = ".temp_screenshot.png"
                screenshot.save(temp_path)
                draw_matches_on_image(temp_path, args.mark_on_image, result)
                os.remove(temp_path)
            
            if args.click:
                x, y, txt, _ = result[0]
                print(f"\n点击第一个匹配位置: ({x}, {y})")
                pyautogui.click(x, y)
        else:
            print(f"\n❌ 未找到文字: '{args.text}'")
            sys.exit(1)
            
    elif args.command == 'text-all':
        print("正在识别屏幕上的所有文字...")
        result = find_all_text_on_screen(args.confidence)
        
        if result:
            print(f"\n✅ 识别到 {len(result)} 处文字:")
            for i, (x, y, txt, conf) in enumerate(result, 1):
                print(f"  [{i}] '{txt}' - ({x}, {y}) [{conf:.0%}]")
            
            if args.mark:
                draw_markers_on_result(result)
        else:
            print(f"\n❌ 未识别到文字")
            sys.exit(1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == '__main__':
    main()
