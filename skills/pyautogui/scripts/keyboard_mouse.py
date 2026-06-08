#!/usr/bin/env python3
"""
跨平台键鼠自动化控制脚本
支持 Windows、Linux、macOS
"""

import sys
import argparse
import time

try:
    import pyautogui
    # 设置安全模式 - 移动到屏幕角落会触发异常停止
    pyautogui.FAILSAFE = True
    # 添加短暂延迟，让用户有机会中断
    pyautogui.PAUSE = 0.1
except ImportError:
    print("错误: 未安装 pyautogui。请运行: pip3 install pyautogui")
    sys.exit(1)


def get_screen_size():
    """获取屏幕尺寸"""
    width, height = pyautogui.size()
    print(f'{{"width": {width}, "height": {height}}}')


def get_mouse_position():
    """获取当前鼠标位置"""
    x, y = pyautogui.position()
    print(f'{{"x": {x}, "y": {y}}}')


def mouse_move(x, y, duration=0.5):
    """移动鼠标到指定位置"""
    try:
        pyautogui.moveTo(int(x), int(y), duration=float(duration))
        print(f'鼠标已移动到: ({x}, {y})')
    except Exception as e:
        print(f'移动鼠标失败: {e}', file=sys.stderr)
        sys.exit(1)


def mouse_click(button='left', clicks=1):
    """点击鼠标"""
    try:
        pyautogui.click(button=button, clicks=clicks)
        print(f'已点击{button}键 {clicks}次')
    except Exception as e:
        print(f'点击鼠标失败: {e}', file=sys.stderr)
        sys.exit(1)


def mouse_click_at(x, y, button='left', clicks=1):
    """在指定位置点击鼠标"""
    try:
        pyautogui.click(int(x), int(y), button=button, clicks=clicks)
        print(f'已在 ({x}, {y}) 点击{button}键 {clicks}次')
    except Exception as e:
        print(f'点击鼠标失败: {e}', file=sys.stderr)
        sys.exit(1)


def mouse_double_click(x, y):
    """双击鼠标"""
    try:
        pyautogui.doubleClick(int(x), int(y))
        print(f'已在 ({x}, {y}) 双击')
    except Exception as e:
        print(f'双击鼠标失败: {e}', file=sys.stderr)
        sys.exit(1)


def mouse_drag(start_x, start_y, end_x, end_y, duration=1):
    """拖拽鼠标"""
    try:
        pyautogui.moveTo(int(start_x), int(start_y))
        pyautogui.dragTo(int(end_x), int(end_y), duration=float(duration))
        print(f'已从 ({start_x}, {start_y}) 拖拽到 ({end_x}, {end_y})')
    except Exception as e:
        print(f'拖拽鼠标失败: {e}', file=sys.stderr)
        sys.exit(1)


def mouse_scroll(amount):
    """滚动鼠标滚轮"""
    try:
        pyautogui.scroll(int(amount))
        direction = "向上" if int(amount) > 0 else "向下"
        print(f'已{direction}滚动 {abs(int(amount))} 单位')
    except Exception as e:
        print(f'滚动鼠标失败: {e}', file=sys.stderr)
        sys.exit(1)


def key_press(key):
    """按下并释放单个键"""
    try:
        pyautogui.press(key)
        print(f'已按下: {key}')
    except Exception as e:
        print(f'按键失败: {e}', file=sys.stderr)
        sys.exit(1)


def key_hotkey(*keys):
    """按下组合键"""
    try:
        pyautogui.hotkey(*keys)
        print(f'已按下组合键: {"+".join(keys)}')
    except Exception as e:
        print(f'组合键失败: {e}', file=sys.stderr)
        sys.exit(1)


def type_text(text, interval=0.01):
    """输入文字"""
    try:
        pyautogui.typewrite(text, interval=float(interval))
        print(f'已输入文字: {text[:50]}{"..." if len(text) > 50 else ""}')
    except Exception as e:
        print(f'输入文字失败: {e}', file=sys.stderr)
        sys.exit(1)


def take_screenshot(output_path):
    """截图"""
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(output_path)
        print(f'截图已保存: {output_path}')
    except Exception as e:
        print(f'截图失败: {e}', file=sys.stderr)
        sys.exit(1)


def take_region_screenshot(output_path, x1, y1, x2, y2):
    """区域截图"""
    try:
        # 确保坐标顺序正确（左上角到右下角）
        left = min(int(x1), int(x2))
        top = min(int(y1), int(y2))
        right = max(int(x1), int(x2))
        bottom = max(int(y1), int(y2))
        
        screenshot = pyautogui.screenshot(region=(left, top, right - left, bottom - top))
        screenshot.save(output_path)
        print(f'区域截图已保存: {output_path}')
        print(f'区域: ({left}, {top}) - ({right}, {bottom}), 尺寸: {right - left} x {bottom - top}')
    except Exception as e:
        print(f'区域截图失败: {e}', file=sys.stderr)
        sys.exit(1)


def copy_to_clipboard(text):
    """将文本复制到剪切板"""
    try:
        import pyperclip
        pyperclip.copy(text)
        print(f'已复制到剪切板: {text[:50]}{"..." if len(text) > 50 else ""}')
    except ImportError:
        print("错误: 未安装 pyperclip。请运行: pip3 install pyperclip", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f'复制到剪切板失败: {e}', file=sys.stderr)
        sys.exit(1)


def paste_from_clipboard():
    """从剪切板粘贴"""
    try:
        pyautogui.keyDown('ctrl')
        pyautogui.keyDown('v')
        pyautogui.keyUp('v')
        pyautogui.keyUp('ctrl')
        print('已粘贴剪切板内容')
    except Exception as e:
        print(f'粘贴失败: {e}', file=sys.stderr)
        sys.exit(1)


def copy_and_paste(text):
    """复制文本到剪切板并直接粘贴"""
    try:
        import pyperclip
        # 复制到剪切板
        pyperclip.copy(text)
        print(f'已复制到剪切板: {text[:50]}{"..." if len(text) > 50 else ""}')
        
        # 粘贴
        pyautogui.keyDown('ctrl')
        pyautogui.keyDown('v')
        pyautogui.keyUp('v')
        pyautogui.keyUp('ctrl')
        print('已粘贴')
    except ImportError:
        print("错误: 未安装 pyperclip。请运行: pip3 install pyperclip", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f'复制粘贴失败: {e}', file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description='跨平台键鼠自动化控制')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')

    # 屏幕信息
    subparsers.add_parser('screen_size', help='获取屏幕尺寸')
    subparsers.add_parser('mouse_position', help='获取鼠标当前位置')

    # 鼠标移动
    move_parser = subparsers.add_parser('mouse_move', help='移动鼠标')
    move_parser.add_argument('x', type=int, help='目标X坐标')
    move_parser.add_argument('y', type=int, help='目标Y坐标')
    move_parser.add_argument('--duration', type=float, default=0.5, help='移动持续时间')

    # 鼠标点击
    click_parser = subparsers.add_parser('mouse_click', help='点击鼠标')
    click_parser.add_argument('button', choices=['left', 'right', 'middle'], help='鼠标按键')
    click_parser.add_argument('--clicks', type=int, default=1, help='点击次数')

    # 在指定位置点击
    click_at_parser = subparsers.add_parser('mouse_click_at', help='在指定位置点击鼠标')
    click_at_parser.add_argument('x', type=int, help='X坐标')
    click_at_parser.add_argument('y', type=int, help='Y坐标')
    click_at_parser.add_argument('button', choices=['left', 'right', 'middle'], help='鼠标按键')
    click_at_parser.add_argument('--clicks', type=int, default=1, help='点击次数')

    # 双击
    double_click_parser = subparsers.add_parser('mouse_double_click', help='双击鼠标')
    double_click_parser.add_argument('x', type=int, help='X坐标')
    double_click_parser.add_argument('y', type=int, help='Y坐标')

    # 拖拽
    drag_parser = subparsers.add_parser('mouse_drag', help='拖拽鼠标')
    drag_parser.add_argument('start_x', type=int, help='起始X坐标')
    drag_parser.add_argument('start_y', type=int, help='起始Y坐标')
    drag_parser.add_argument('end_x', type=int, help='目标X坐标')
    drag_parser.add_argument('end_y', type=int, help='目标Y坐标')
    drag_parser.add_argument('--duration', type=float, default=1, help='拖拽持续时间')

    # 滚动
    scroll_parser = subparsers.add_parser('mouse_scroll', help='滚动鼠标滚轮')
    scroll_parser.add_argument('amount', type=int, help='滚动量(正数向上,负数向下)')

    # 按键
    key_parser = subparsers.add_parser('key_press', help='按下按键')
    key_parser.add_argument('key', help='按键名(如: enter, ctrl, alt, tab等)')

    # 组合键
    hotkey_parser = subparsers.add_parser('key_hotkey', help='按下组合键')
    hotkey_parser.add_argument('keys', nargs='+', help='组合键(如: ctrl c)')

    # 输入文字
    type_parser = subparsers.add_parser('type_text', help='输入文字')
    type_parser.add_argument('text', help='要输入的文字')
    type_parser.add_argument('--interval', type=float, default=0.01, help='每个字符间隔(秒)')

    # 截图
    screenshot_parser = subparsers.add_parser('screenshot', help='截图')
    screenshot_parser.add_argument('output', help='输出文件路径')
    
    # 区域截图
    region_parser = subparsers.add_parser('screenshot_region', help='区域截图')
    region_parser.add_argument('output', help='输出文件路径')
    region_parser.add_argument('x1', type=int, help='左上角X坐标')
    region_parser.add_argument('y1', type=int, help='左上角Y坐标')
    region_parser.add_argument('x2', type=int, help='右下角X坐标')
    region_parser.add_argument('y2', type=int, help='右下角Y坐标')
    
    # 复制到剪切板
    copy_parser = subparsers.add_parser('copy', help='复制文本到剪切板')
    copy_parser.add_argument('text', help='要复制的文本')
    
    # 粘贴
    subparsers.add_parser('paste', help='粘贴剪切板内容')
    
    # 复制并粘贴
    copy_paste_parser = subparsers.add_parser('copy_paste', help='复制文本并直接粘贴')
    copy_paste_parser.add_argument('text', help='要复制并粘贴的文本')

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    # 执行命令
    if args.command == 'screen_size':
        get_screen_size()
    elif args.command == 'mouse_position':
        get_mouse_position()
    elif args.command == 'mouse_move':
        mouse_move(args.x, args.y, args.duration)
    elif args.command == 'mouse_click':
        mouse_click(args.button, args.clicks)
    elif args.command == 'mouse_click_at':
        mouse_click_at(args.x, args.y, args.button, args.clicks)
    elif args.command == 'mouse_double_click':
        mouse_double_click(args.x, args.y)
    elif args.command == 'mouse_drag':
        mouse_drag(args.start_x, args.start_y, args.end_x, args.end_y, args.duration)
    elif args.command == 'mouse_scroll':
        mouse_scroll(args.amount)
    elif args.command == 'key_press':
        key_press(args.key)
    elif args.command == 'key_hotkey':
        key_hotkey(*args.keys)
    elif args.command == 'type_text':
        type_text(args.text, args.interval)
    elif args.command == 'screenshot':
        take_screenshot(args.output)
    elif args.command == 'screenshot_region':
        take_region_screenshot(args.output, args.x1, args.y1, args.x2, args.y2)
    elif args.command == 'copy':
        copy_to_clipboard(args.text)
    elif args.command == 'paste':
        paste_from_clipboard()
    elif args.command == 'copy_paste':
        copy_and_paste(args.text)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
