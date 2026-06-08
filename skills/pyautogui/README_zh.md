# OpenClaw PyAutoGUI Skill

跨平台键鼠自动化控制与图片处理工具

## 简介

本技能提供了一套完整的跨平台自动化工具，支持 Windows、Linux 和 macOS 系统。基于 PyAutoGUI、Pillow 和 OpenCV 实现，可用于：

- 鼠标控制（移动、点击、拖拽、滚动）
- 键盘控制（按键、组合键、文本输入）
- 屏幕操作（截图、获取鼠标位置、获取屏幕尺寸）
- 图片处理（获取图片参数、裁剪图片）
- 屏幕绘图（在屏幕上绘制标记以确认坐标位置）
- 图片绘制（在图片上永久绘制标记并保存）
- 图像查找（以图找图、以文找图OCR定位屏幕元素）
- 文件清理（清理截图和标记文件，释放磁盘空间）

## 快速开始

### 安装依赖

```bash
# 键鼠控制
pip install pyautogui

# 图片处理
pip install Pillow
```

### 基本使用

```bash
# 获取屏幕尺寸
python scripts/keyboard_mouse.py screen_size

# 移动鼠标并点击
python scripts/keyboard_mouse.py mouse_move 500 300
python scripts/keyboard_mouse.py mouse_click left

# 截图
python scripts/keyboard_mouse.py screenshot screenshot.png

# 获取图片信息
python scripts/image_utils.py info screenshot.png
```

## 功能模块

### 1. 键鼠控制 (`keyboard_mouse.py`)

#### 鼠标操作
- `screen_size` - 获取屏幕尺寸
- `mouse_position` - 获取当前鼠标位置
- `mouse_move x y` - 移动鼠标到指定位置
- `mouse_click button` - 点击鼠标（left/right/middle）
- `mouse_click_at x y button` - 在指定位置点击
- `mouse_double_click x y` - 双击
- `mouse_drag x1 y1 x2 y2` - 拖拽
- `mouse_scroll amount` - 滚动（正数向上，负数向下）

#### 键盘操作
- `key_press key` - 按下单个按键
- `key_hotkey key1 key2 ...` - 组合键
- `type_text text` - 输入文字

#### 截图
- `screenshot path` - 截取整个屏幕

### 2. 图片工具 (`image_utils.py`)

#### 获取图片信息
- `info path` - 获取完整信息（尺寸、格式、文件大小等）
- `size path` - 仅获取尺寸（快速模式）

#### 图片处理
- `crop x1 y1 x2 y2` - 裁剪图片

### 3. 屏幕绘图 (`draw_overlay.py`)

用于在屏幕上绘制临时标记以确认坐标位置，特别适用于校准坐标是否准确。

#### 绘制标记
- `marker type x y` - 在指定位置绘制标记（cross/circle/square/arrow/target）
- `area x1 y1 x2 y2` - 绘制区域框选

#### 标记类型
- `cross` - 十字线
- `circle` - 圆圈
- `square` - 方框
- `arrow` - 箭头（支持方向 up/down/left/right）
- `target` - 靶心（圆圈+十字）

### 4. 图片绘制 (`draw_on_image.py`)

在图片上永久绘制标记并保存，适用于批量标记和生成参考图。

#### 绘制标记
- `marker type x y` - 在图片上绘制标记（cross/circle/square/arrow/target/point）
- `area x1 y1 x2 y2` - 在图片上绘制区域框

#### 优势
- 批量标记多个位置，省钱高效
- 生成带标注的参考图片
- 支持连续标记（在已标记的图片上继续标记）

### 5. 图像查找 (`image_finder.py`)

基于 OpenCV 和 RapidOCR 实现，支持以图找图和以文找图。

#### 以图找图
- `image template` - 模板匹配查找图片位置
- 支持多尺度匹配、多结果返回
- 比 AI 识别更精确可靠

#### 以文找图
- `text str` - OCR 识别屏幕文字并定位
- `text-all` - 识别屏幕上所有文字
- 使用 RapidOCR，轻量快速，中文识别效果好

#### 优势
- 像素级精确匹配
- 本地计算，无需 API 费用
- 毫秒级响应速度

### 6. 文件清理 (`cleanup.py`)

清理截图和标记过程中产生的临时文件，释放磁盘空间。

#### 功能
- `analyze dir` - 分析临时文件占用情况
- `clean dir` - 按时间或大小清理文件
- `auto dir` - 自动清理（超出限制时删除最旧文件）

#### 特点
- 默认预览模式，防止误删
- 支持按天数、文件大小筛选
- 可自定义文件匹配模式

## 示例场景

### 自动发送消息
```bash
# 移动鼠标到输入框，点击，输入文字，发送
python scripts/keyboard_mouse.py mouse_click_at 800 600 left
python scripts/keyboard_mouse.py type_text "Hello World"
python scripts/keyboard_mouse.py key_press enter
```

### 截图并分析
```bash
# 截图并获取图片尺寸
python scripts/keyboard_mouse.py screenshot screen.png
python scripts/image_utils.py info screen.png

# 裁剪出右下角区域
python scripts/image_utils.py crop screen.png 1520 880 1920 1080 -o corner.png
```

### 自动化表单填写
```bash
# 点击第一个输入框
python scripts/keyboard_mouse.py mouse_click_at 500 400 left
python scripts/keyboard_mouse.py type_text "username@example.com"

# 按 Tab 切换到下一个输入框
python scripts/keyboard_mouse.py key_press tab
python scripts/keyboard_mouse.py type_text "password123"

# 点击提交按钮
python scripts/keyboard_mouse.py mouse_click_at 500 600 left
```

### 坐标校准工作流
```bash
# 1. 分析截图得到坐标 (3788, 2080)
# 2. 在屏幕上绘制标记验证位置
python scripts/draw_overlay.py marker target 3788 2080 --text "发送按钮" --duration 10

# 3. 如果位置不对，调整后重新验证
python scripts/draw_overlay.py marker target 3790 2090 --text "发送按钮-修正" --duration 10

# 4. 确认无误后执行点击
python scripts/keyboard_mouse.py mouse_click_at 3790 2090 left
```

### 图片标注工作流（省钱版）
```bash
# 1. 截图
python scripts/keyboard_mouse.py screenshot screen.png

# 2. 批量在图片上标记多个候选位置（省钱！）
python scripts/draw_on_image.py screen.png marker target 3788 2080 --text "候选1" -o marked1.png
python scripts/draw_on_image.py screen.png marker target 3790 2090 --text "候选2" -o marked2.png
python scripts/draw_on_image.py screen.png marker target 3785 2085 --text "候选3" -o marked3.png

# 3. 查看标记后的图片，选择最准确的位置
# 4. 只在确定的位置执行一次屏幕绘图确认
python scripts/draw_overlay.py marker target 3790 2090 --duration 3

# 5. 确认无误后执行点击
python scripts/keyboard_mouse.py mouse_click_at 3790 2090 left
```

### 图像查找工作流（推荐）
```bash
# 以图找图 - 最精确的自动化方案
# 1. 先手动截取目标按钮保存为 template.png
# 2. 使用模板匹配精确查找位置
python scripts/image_finder.py image template.png --threshold 0.9

# 3. 直接点击找到的位置
python scripts/image_finder.py image template.png --click

# 以文找图 - 适用于文字按钮
python scripts/image_finder.py text "发送" --click

# 在图片上标记所有候选位置（用于AI判断选择）
python scripts/image_finder.py text "发送" --mark-on-image checked.png

# 查看屏幕上所有文字
python scripts/image_finder.py text-all --mark
```

### 文件清理工作流
```bash
# 1. 分析文件占用情况
python scripts/cleanup.py analyze .

# 2. 预览清理（超过7天的文件）
python scripts/cleanup.py clean . --days 7

# 3. 确认后执行清理
python scripts/cleanup.py clean . --days 7 --execute

# 或者设置自动清理策略
python scripts/cleanup.py auto . --max-files 20 --max-size 50
```

## 坐标系统

- **原点 (0, 0)**：屏幕左上角
- **X 轴**：向右增加
- **Y 轴**：向下增加

## 安全提示

1. 操作前确认目标窗口已激活
2. 谨慎使用组合键，避免触发系统快捷键
3. 移动鼠标到屏幕左上角 (0,0) 会触发安全停止
4. 建议在操作前添加延迟，给用户反应时间

## 跨平台支持

| 平台 | 支持状态 | 备注 |
|------|----------|------|
| Windows | ✅ 完全支持 | 可能需要管理员权限 |
| Linux | ✅ 支持 | 需要 X11 环境，Wayland 可能不支持 |
| macOS | ✅ 支持 | 需要在系统设置 > 安全性与隐私 > 辅助功能 中授权 |

## 项目结构

```
openclaw-pyautogui-skill/
├── SKILL.md              # 技能说明文档
├── README.md             # 本文件
└── scripts/
    ├── keyboard_mouse.py # 键鼠控制脚本
    ├── image_utils.py    # 图片处理脚本
    ├── draw_overlay.py   # 屏幕绘图标记脚本
    ├── draw_on_image.py  # 图片绘制标记脚本
    ├── image_finder.py   # 图像查找脚本（以图找图、以文找图）
    └── cleanup.py        # 文件清理工具脚本
```

## 依赖

- Python 3.7+
- pyautogui
- Pillow
- opencv-python
- numpy
- rapidocr_onnxruntime

## 许可证

MIT License
