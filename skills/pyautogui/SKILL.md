---
name: openclaw-pyautogui
description: Cross-platform mouse/keyboard automation skill. Supports mouse control (move/click/drag/scroll), keyboard control (key press/hotkeys/type text), screen operations (screenshots/mouse position/screen size), image utilities (metadata/crop), screen overlay markers, drawing markers on images, image locating (template matching + OCR), and file cleanup to free disk space. Activate when the user needs UI automation, screenshots, coordinate verification, image analysis/annotation, on-screen element locating, or cleanup.
description_zh: 跨平台键鼠自动化控制技能，支持鼠标控制（移动、点击、拖拽、滚动）、键盘控制（按键、组合键、输入文本）、屏幕操作（截图、获取鼠标位置）、图片处理（获取图片参数、裁剪图片）、屏幕绘图（在屏幕上绘制标记）、图片绘制（在图片上绘制标记）、图像查找（以图找图、以文找图OCR）、文件清理（释放磁盘空间）。当用户需要进行自动化键鼠操作、屏幕截图、获取鼠标位置、模拟键盘输入、获取图片信息、裁剪图片、绘制标记、图像识别定位或清理文件时激活此技能。
---

# PyAutoGUI Automation Skill

Cross-platform mouse/keyboard automation for Windows, Linux, and macOS.

## Features

- **Mouse control**: move, click, drag, scroll
- **Keyboard control**: key press, hotkeys, type text
- **Screen operations**: screenshot, mouse position, screen size
- **Image utilities**: image metadata (size/format/file size), crop images
- **Screen overlay**: draw temporary markers to validate coordinates
- **Draw on images**: draw persistent markers into an image and save
- **Image locating**: template matching and OCR-based text locating
- **Cleanup**: remove generated screenshots/marked files to free disk space

## Activation

Activate when the user asks to do things like:
- "Click a position on the screen"
- "Move the mouse to (x, y)"
- "Type text / press keys"
- "Take a screenshot"
- "Run repetitive UI automation"
- "Get the current mouse position"
- "Get image size / image info"
- "Crop an image"
- "Draw a marker on the screen"
- "Draw a marker on an image"
- "Locate an element by template"
- "Locate text on the screen (OCR)"
- "Clean up screenshots / temporary files"

## Usage

### Install dependencies

```bash
# Mouse/keyboard automation
pip3 install pyautogui

# Image utilities
pip3 install Pillow
```

### Screen info

```bash
# Screen size
python3 scripts/keyboard_mouse.py screen_size

# Mouse position
python3 scripts/keyboard_mouse.py mouse_position
```

### Mouse actions

```bash
# Move mouse to (x, y)
python3 scripts/keyboard_mouse.py mouse_move 500 300
python3 scripts/keyboard_mouse.py mouse_move 500 300 --duration 1.0

# Mouse click (left/right/middle)
python3 scripts/keyboard_mouse.py mouse_click left
python3 scripts/keyboard_mouse.py mouse_click right
python3 scripts/keyboard_mouse.py mouse_click middle --clicks 2

# Click at a specific location
python3 scripts/keyboard_mouse.py mouse_click_at 500 300 left
python3 scripts/keyboard_mouse.py mouse_click_at 500 300 right --clicks 2

# Double click
python3 scripts/keyboard_mouse.py mouse_double_click 500 300

# Drag
python3 scripts/keyboard_mouse.py mouse_drag 500 300 800 600
python3 scripts/keyboard_mouse.py mouse_drag 500 300 800 600 --duration 2.0

# Scroll (positive = up, negative = down)
python3 scripts/keyboard_mouse.py mouse_scroll 5
python3 scripts/keyboard_mouse.py mouse_scroll -3
```

### Keyboard actions

```bash
# Single key
python3 scripts/keyboard_mouse.py key_press enter
python3 scripts/keyboard_mouse.py key_press escape
python3 scripts/keyboard_mouse.py key_press tab
python3 scripts/keyboard_mouse.py key_press space

# Hotkeys
python3 scripts/keyboard_mouse.py key_hotkey ctrl c
python3 scripts/keyboard_mouse.py key_hotkey ctrl v
python3 scripts/keyboard_mouse.py key_hotkey win r
python3 scripts/keyboard_mouse.py key_hotkey alt tab
python3 scripts/keyboard_mouse.py key_hotkey ctrl alt t

# Type text
python3 scripts/keyboard_mouse.py type_text "Hello World"
python3 scripts/keyboard_mouse.py type_text "你好世界" --interval 0.05
```

### Screenshot

```bash
# Save a screenshot (primary screen)
python3 scripts/keyboard_mouse.py screenshot /tmp/screenshot.png

# Windows example
python scripts/keyboard_mouse.py screenshot "E:\\temp\\screenshot.png"
```

**Screenshot notes:**
- Supported formats: PNG (recommended), JPG, BMP, etc.
- Scope: primary monitor (in multi-monitor setups)

### Region Screenshot

```bash
# Screenshot specific region (x1, y1, x2, y2)
python3 scripts/keyboard_mouse.py screenshot_region region.png 100 100 500 500

# Windows example - capture QQ chat window area
python scripts/keyboard_mouse.py screenshot_region qq_window.png 2800 300 3800 1200
```

**Parameters:**
- `x1, y1`: Top-left corner coordinates
- `x2, y2`: Bottom-right corner coordinates
- Order doesn't matter (automatically calculated)

### Copy & Paste

```bash
# Copy text to clipboard
python3 scripts/keyboard_mouse.py copy "Text to copy"

# Paste from clipboard (Ctrl+V)
python3 scripts/keyboard_mouse.py paste

# Copy and paste in one command (fastest way to input text)
python3 scripts/keyboard_mouse.py copy_paste "Text to input directly"
```

**Use cases:**
- `copy_paste` is faster than `type_text` for long text
- Use `copy_paste` when you want to skip typing animation
- Use `type_text` when you need to simulate realistic typing

## Common key names

- Letters: `a` `b` `c` ...
- Numbers: `0` `1` `2` ...
- Function keys: `f1` `f2` ... `f12`
- Modifiers: `ctrl` `alt` `shift` `win`
- Others: `enter` `esc` `tab` `space` `backspace` `delete` `up` `down` `left` `right`

## Safety

⚠️ **Important:**
1. Make sure the target window is focused before executing actions
2. Be careful with system hotkeys to avoid unintended actions
3. Add delays when needed to give yourself time to interrupt
4. Moving the mouse to the top-left corner (0, 0) triggers PyAutoGUI failsafe

## Cross-platform notes

- **Windows**: Full support; admin permission may be needed in some environments
- **Linux**: Requires X11; Wayland may not work
- **macOS**: Grant Accessibility permission to Terminal/Python in System Settings

## Example scenarios

### Open Calculator (Windows)
```bash
python3 scripts/keyboard_mouse.py key_hotkey win r
python3 scripts/keyboard_mouse.py type_text "calc"
python3 scripts/keyboard_mouse.py key_press enter
```

### Auto-fill a form
```bash
python3 scripts/keyboard_mouse.py mouse_click_at 500 300 left
python3 scripts/keyboard_mouse.py type_text "example@email.com"
python3 scripts/keyboard_mouse.py key_press tab
python3 scripts/keyboard_mouse.py type_text "password123"
```

### Batch clicking
```bash
python3 scripts/keyboard_mouse.py mouse_click_at 100 100 left
python3 scripts/keyboard_mouse.py mouse_click_at 200 200 left
python3 scripts/keyboard_mouse.py mouse_click_at 300 300 left
```

## Included scripts

- `scripts/keyboard_mouse.py` - Mouse/keyboard control
- `scripts/image_utils.py` - Image utilities
- `scripts/draw_overlay.py` - Screen overlay markers
- `scripts/draw_on_image.py` - Draw markers on images
- `scripts/image_finder.py` - Image locating (template + OCR)
- `scripts/cleanup.py` - Cleanup tool

## Image utilities

### Image info

```bash
python3 scripts/image_utils.py info screenshot.png
python3 scripts/image_utils.py size photo.jpg
```

### Crop image

```bash
python3 scripts/image_utils.py crop screenshot.png 100 100 500 500
python3 scripts/image_utils.py crop screenshot.png 100 100 500 500 -o output.png
```

### Output example

```bash
$ python3 scripts/image_utils.py info screenshot.png
{
  "path": "screenshot.png",
  "filename": "screenshot.png",
  "size": {
    "width": 3840,
    "height": 2160
  },
  "format": "PNG",
  "mode": "RGB",
  "file_size_bytes": 2097152,
  "file_size_kb": 2048.0
}
```

### Image fields

| Field | Meaning | Example |
|------|------|--------|
| `width` | Image width (px) | 1920, 3840 |
| `height` | Image height (px) | 1080, 2160 |
| `format` | Image format | PNG, JPEG, GIF, BMP, WEBP |
| `mode` | Color mode | RGB, RGBA, L |
| `file_size_bytes` | File size (bytes) | 2097152 |
| `file_size_kb` | File size (KB) | 2048.0 |

### Coordinate system

**Screen coordinates:**
- Origin (0, 0) is the top-left corner
- X increases to the right
- Y increases downward

**Crop coordinates:**
- `x1, y1`: top-left corner of crop
- `x2, y2`: bottom-right corner of crop
- Cropped size = (x2 - x1) × (y2 - y1)

**Example:**
```bash
python3 scripts/image_utils.py crop screenshot.png 1520 880 1920 1080
```

### Typical workflows

#### Analyze positions in a screenshot
```bash
python3 scripts/image_utils.py size screenshot.png
python3 scripts/image_utils.py crop screenshot.png 3440 1960 3840 2160 -o bottom_right.png
```

#### Batch image sizing
```bash
for img in *.png; do
    echo -n "$img: "
    python3 scripts/image_utils.py size "$img"
done
```

#### Capture a region of the screen
```bash
python3 scripts/keyboard_mouse.py screenshot full.png
python3 scripts/image_utils.py crop full.png 500 300 1000 800 -o region.png
```

---

## Screen overlay markers

Draw temporary markers on the screen for coordinate verification. Useful for:
- Calibrating coordinates
- Confirming the real position of a button/element
- Debugging automation scripts

### Draw a marker

```bash
python3 scripts/draw_overlay.py marker cross 500 300
python3 scripts/draw_overlay.py marker target 800 600 --duration 10
python3 scripts/draw_overlay.py marker circle 500 300 --color blue --text "Send button"
python3 scripts/draw_overlay.py marker arrow 1000 800 --direction down --color yellow
python3 scripts/draw_overlay.py marker square 600 400 --color green --size 40
```

### Draw a rectangular area

```bash
python3 scripts/draw_overlay.py area 3028 276 3832 2098 --label "Window" --duration 8
python3 scripts/draw_overlay.py area 3744 2062 3832 2098 --label "Send button" --color red
```

### Marker types

| Type | Description | Use case |
|------|------------|----------|
| `cross` | Crosshair | Precise single-point targeting |
| `circle` | Circle | Mark buttons/circular elements |
| `square` | Square | Mark rectangular elements |
| `arrow` | Arrow | Indicate direction / draw attention |
| `target` | Target | Strongest visual cue (circle + crosshair) |

### Colors

`red`, `green`, `blue`, `yellow`, `cyan`, `magenta`, `white`, `orange`

### Coordinate calibration example

```bash
python3 scripts/keyboard_mouse.py screenshot screen.png
python3 scripts/draw_overlay.py marker target 3788 2080 --text "Send button" --duration 10
python3 scripts/draw_overlay.py marker target 3790 2090 --text "Send button (adjusted)" --duration 10
python3 scripts/keyboard_mouse.py mouse_click_at 3790 2090 left
```

---

## Draw markers on images

Draw persistent markers into image files. Useful for:
- Annotating recognized positions on a screenshot
- Producing reference images
- Batch marking candidates for comparison
- Keeping calibration records

### Draw a marker

```bash
python3 scripts/draw_on_image.py screenshot.png marker cross 500 300
python3 scripts/draw_on_image.py screenshot.png marker target 800 600 -o marked.png
python3 scripts/draw_on_image.py screenshot.png marker circle 500 300 --color red --text "Send button"
python3 scripts/draw_on_image.py screenshot.png marker arrow 1000 800 --direction down --color yellow
python3 scripts/draw_on_image.py screenshot.png marker point 600 400 --color green --size 10
```

### Draw a rectangular area

```bash
python3 scripts/draw_on_image.py screenshot.png area 3028 276 3832 2098 --label "Window"
python3 scripts/draw_on_image.py screenshot.png area 3744 2062 3832 2098 -o button_marked.png --label "Send button"
```

### Batch marking workflow

```bash
python3 scripts/keyboard_mouse.py screenshot screen.png
python3 scripts/draw_on_image.py screen.png marker target 3788 2080 --text "Send button" -o step1.png
python3 scripts/draw_on_image.py step1.png marker target 3790 2090 --text "Adjusted" -o step2.png
python3 scripts/draw_on_image.py step2.png marker circle 3000 1500 --text "Avatar area" -o final.png
```

### Screen overlay vs drawing on image

| Item | Screen overlay (draw_overlay.py) | Draw on image (draw_on_image.py) |
|------|----------------------------------|----------------------------------|
| Display | Real-time on screen | Inside the image file |
| Duration | Temporary | Persistent |
| Interaction | Auto-close (time) | No interaction |
| Best for | Real-time coordinate validation | Generating annotated references |
| Output | Not saved | Saved to file |

### Recommended coordinate calibration (cost-saving)

```bash
python3 scripts/keyboard_mouse.py screenshot screen.png
python3 scripts/image_utils.py size screen.png

python3 scripts/draw_on_image.py screen.png marker target 3788 2080 --text "Candidate 1" -o marked1.png
python3 scripts/draw_on_image.py screen.png marker target 3790 2090 --text "Candidate 2" -o marked2.png
python3 scripts/draw_on_image.py screen.png marker target 3785 2085 --text "Candidate 3" -o marked3.png

python3 scripts/draw_overlay.py marker target 3790 2090 --duration 3
python3 scripts/keyboard_mouse.py mouse_click_at 3790 2090 left
```

---

## Image locating

Built on OpenCV template matching and RapidOCR. Supports locating UI elements by image and by text.

### Install dependencies

```bash
pip install opencv-python numpy rapidocr_onnxruntime
```

**Note:** RapidOCR models are ~15MB and are downloaded automatically on first use.

### Template matching (find by image)

```bash
python3 scripts/image_finder.py image button.png
python3 scripts/image_finder.py image button.png --all
python3 scripts/image_finder.py image button.png --threshold 0.95
python3 scripts/image_finder.py image button.png --mark
python3 scripts/image_finder.py image button.png --click
```

**Output example:**
```
✅ Match found: position (3788, 2080), similarity: 98.50%
```

### OCR text locating (find by text)

```bash
python3 scripts/image_finder.py text "Send"
python3 scripts/image_finder.py text "OK" --click
python3 scripts/image_finder.py text "Send" --mark-on-image checked.png
python3 scripts/image_finder.py text-all
python3 scripts/image_finder.py text "Login" --confidence 0.9
```

**Output example:**
```
✅ Found 2 candidates containing 'Send':
  [1] Text: 'Send', position: (3788, 2080), confidence: 95%
  [2] Text: 'Send to all', position: (2100, 1500), confidence: 88%
```

### Recommended automation workflows

**Template matching (most accurate):**
```bash
python3 scripts/image_finder.py image qq_send_button.png --threshold 0.9
python3 scripts/draw_on_image.py marker screen.png target 3788 2080 --text "Candidate 1" -o check1.png
python3 scripts/keyboard_mouse.py mouse_click_at 3788 2080 left
```

**OCR text locating (when no template is available):**
```bash
python3 scripts/image_finder.py text "Send"
python3 scripts/keyboard_mouse.py mouse_click_at 3548 1462 left
```

**Important principle:**
1. OCR returns accurate screen coordinates; do not modify the returned coordinates
2. If there are multiple candidates, mark them on an image to visually choose the correct one
3. Once you choose the right candidate, click using the original coordinates

### Template matching vs OCR

| Item | Template matching | OCR text locating |
|------|-------------------|------------------|
| Accuracy | ⭐⭐⭐⭐⭐ pixel-level | ⭐⭐⭐⭐ depends on font/background |
| Speed | ⭐⭐⭐⭐⭐ milliseconds | ⭐⭐⭐ requires inference |
| Dependencies | OpenCV | RapidOCR |
| Best for | Icons/buttons/fixed UI | Text buttons/labels/inputs |

### Why this is better than guessing coordinates

1. High precision and repeatability (pixel-level)
2. Local compute with no API cost
3. Fast response
4. Easy to debug via marked outputs

---

## Cleanup

### Analyze disk usage

```bash
python3 scripts/cleanup.py analyze .
```

### Clean files

```bash
python3 scripts/cleanup.py clean . --days 7
python3 scripts/cleanup.py clean . --days 7 --execute
python3 scripts/cleanup.py clean . --size 1024 --execute
python3 scripts/cleanup.py clean . --execute
```

### Auto cleanup

```bash
python3 scripts/cleanup.py auto . --max-files 50 --max-size 100
python3 scripts/cleanup.py auto . --max-files 20 --max-size 50
```

### End-to-end example

```bash
python3 scripts/keyboard_mouse.py screenshot screen.png
python3 scripts/draw_on_image.py marker screen.png target 500 300 --text "Button" -o marked.png

python3 scripts/cleanup.py analyze .
python3 scripts/cleanup.py clean . --days 1 --execute
python3 scripts/cleanup.py auto . --max-files 10 --max-size 50
```

---

## Command quick reference

### Mouse/keyboard (`keyboard_mouse.py`)

| Command | Description | Example |
|------|------|------|
| `screen_size` | Get screen size | `keyboard_mouse.py screen_size` |
| `mouse_position` | Get mouse position | `keyboard_mouse.py mouse_position` |
| `mouse_move x y` | Move mouse | `keyboard_mouse.py mouse_move 500 300` |
| `mouse_click button` | Click mouse | `keyboard_mouse.py mouse_click left` |
| `mouse_click_at x y button` | Click at coordinates | `keyboard_mouse.py mouse_click_at 500 300 left` |
| `mouse_double_click x y` | Double click | `keyboard_mouse.py mouse_double_click 500 300` |
| `mouse_drag x1 y1 x2 y2` | Drag | `keyboard_mouse.py mouse_drag 500 300 800 600` |
| `mouse_scroll amount` | Scroll | `keyboard_mouse.py mouse_scroll 5` |
| `key_press key` | Press key | `keyboard_mouse.py key_press enter` |
| `key_hotkey key1 key2` | Hotkey | `keyboard_mouse.py key_hotkey ctrl c` |
| `type_text text` | Type text | `keyboard_mouse.py type_text "Hello"` |
| `screenshot path` | Screenshot | `keyboard_mouse.py screenshot img.png` |

### Image utilities (`image_utils.py`)

| Command | Description | Example |
|------|------|------|
| `info path` | Full image info | `image_utils.py info photo.png` |
| `size path` | Image size only | `image_utils.py size photo.jpg` |
| `crop x1 y1 x2 y2` | Crop image | `image_utils.py crop img.png 100 100 500 500` |

### Screen overlay (`draw_overlay.py`)

| Command | Description | Example |
|------|------|------|
| `marker type x y` | Draw marker | `draw_overlay.py marker target 500 300` |
| `area x1 y1 x2 y2` | Draw rectangle | `draw_overlay.py area 100 100 500 400` |

### Draw on image (`draw_on_image.py`)

| Command | Description | Example |
|------|------|------|
| `marker type x y` | Draw marker on image | `draw_on_image.py img.png marker target 500 300` |
| `area x1 y1 x2 y2` | Draw rectangle on image | `draw_on_image.py img.png area 100 100 500 400` |

### Image finder (`image_finder.py`)

| Command | Description | Example |
|------|------|------|
| `image template` | Find by template | `image_finder.py image button.png` |
| `text str` | Find by text (OCR) | `image_finder.py text "Send"` |
| `text-all` | Recognize all text | `image_finder.py text-all` |

### Cleanup (`cleanup.py`)

| Command | Description | Example |
|------|------|------|
| `analyze dir` | Analyze disk usage | `cleanup.py analyze .` |
| `clean dir` | Clean files | `cleanup.py clean . --days 7 --execute` |
| `auto dir` | Auto cleanup | `cleanup.py auto . --max-files 50` |
