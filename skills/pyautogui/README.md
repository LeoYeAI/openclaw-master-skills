# OpenClaw PyAutoGUI Skill

Cross-platform mouse/keyboard automation and image utilities

## Overview

This skill provides a complete set of cross-platform automation tools for Windows, Linux, and macOS. It is built on PyAutoGUI, Pillow, and OpenCV, and can be used for:

- Mouse control (move, click, drag, scroll)
- Keyboard control (press keys, hotkeys, type text)
- Screen operations (screenshot, mouse position, screen size)
- Image utilities (read image metadata, crop)
- Screen overlay markers (temporary markers for coordinate verification)
- Drawing on images (persist markers into image files)
- Image/text locating (template matching and OCR)
- File cleanup (remove generated screenshots/marked files to free disk space)

## Quick Start

### Install dependencies

```bash
# Mouse/keyboard automation
pip install pyautogui

# Image utilities
pip install Pillow
```

### Basic usage

```bash
# Screen size
python scripts/keyboard_mouse.py screen_size

# Move mouse and click
python scripts/keyboard_mouse.py mouse_move 500 300
python scripts/keyboard_mouse.py mouse_click left

# Screenshot
python scripts/keyboard_mouse.py screenshot screenshot.png

# Region screenshot (x1, y1, x2, y2)
python scripts/keyboard_mouse.py screenshot_region qq_window.png 2800 300 3800 1200

# Copy and paste (fastest way to input text)
python scripts/keyboard_mouse.py copy_paste "Hello World!"

# Image info
python scripts/image_utils.py info screenshot.png
```

## Modules

### 1) Mouse & Keyboard (`keyboard_mouse.py`)

#### Mouse
- `screen_size` - Get screen size
- `mouse_position` - Get current mouse position
- `mouse_move x y` - Move mouse to (x, y)
- `mouse_click button` - Click mouse (left/right/middle)
- `mouse_click_at x y button` - Click at (x, y)
- `mouse_double_click x y` - Double click at (x, y)
- `mouse_drag x1 y1 x2 y2` - Drag from (x1, y1) to (x2, y2)
- `mouse_scroll amount` - Scroll (positive = up, negative = down)

#### Keyboard
- `key_press key` - Press a single key
- `key_hotkey key1 key2 ...` - Press a hotkey combination
- `type_text text` - Type text

#### Screenshot
- `screenshot path` - Capture the primary screen to a file
- `screenshot_region path x1 y1 x2 y2` - Capture specific region

#### Clipboard
- `copy text` - Copy text to clipboard
- `paste` - Paste from clipboard (Ctrl+V)
- `copy_paste text` - Copy and paste in one command (fastest text input)

### 2) Image Utilities (`image_utils.py`)

#### Image info
- `info path` - Full info (size/format/filesize/etc.)
- `size path` - Size only (fast)

#### Image processing
- `crop x1 y1 x2 y2` - Crop an image

### 3) Screen Overlay (`draw_overlay.py`)

Draw temporary markers on the screen for coordinate calibration and debugging.

#### Commands
- `marker type x y` - Draw a marker at (x, y) (cross/circle/square/arrow/target)
- `area x1 y1 x2 y2` - Draw a rectangular area

#### Marker types
- `cross` - Crosshair
- `circle` - Circle
- `square` - Square
- `arrow` - Arrow (direction: up/down/left/right)
- `target` - Target (circle + crosshair)

### 4) Draw on Image (`draw_on_image.py`)

Draw markers permanently into an image file, useful for batch-marking candidates and generating references.

#### Commands
- `marker type x y` - Draw a marker (cross/circle/square/arrow/target/point)
- `area x1 y1 x2 y2` - Draw a rectangular area

#### Highlights
- Batch mark many candidates cheaply
- Generate shareable, annotated reference images
- Supports incremental marking (mark an already-marked image again)

### 5) Image Finder (`image_finder.py`)

Built on OpenCV + RapidOCR. Supports template matching and OCR text locating.

#### Template matching
- `image template` - Find template on screen
- Supports multi-scale matching and multiple results
- More accurate and repeatable than manual coordinate guessing

#### OCR text locating
- `text str` - Recognize and locate text on the screen
- `text-all` - Recognize all text on the screen
- Uses RapidOCR (lightweight and fast)

#### Highlights
- Pixel-level matching for templates
- Local compute (no API cost)
- Fast response time

### 6) Cleanup (`cleanup.py`)

Clean up temporary files (screenshots / annotated images) to free disk space.

#### Commands
- `analyze dir` - Analyze disk usage
- `clean dir` - Clean by age/size filters
- `auto dir` - Auto clean when limits are exceeded (delete oldest first)

#### Highlights
- Preview mode by default to prevent accidental deletion
- Filter by days and/or file size
- Customizable file matching patterns

## Examples

### Send a message automatically
```bash
python scripts/keyboard_mouse.py mouse_click_at 800 600 left
python scripts/keyboard_mouse.py type_text "Hello World"
python scripts/keyboard_mouse.py key_press enter
```

### Screenshot and analyze
```bash
python scripts/keyboard_mouse.py screenshot screen.png
python scripts/image_utils.py info screen.png

python scripts/image_utils.py crop screen.png 1520 880 1920 1080 -o corner.png
```

### Fill a form automatically
```bash
python scripts/keyboard_mouse.py mouse_click_at 500 400 left
python scripts/keyboard_mouse.py type_text "username@example.com"

python scripts/keyboard_mouse.py key_press tab
python scripts/keyboard_mouse.py type_text "password123"

python scripts/keyboard_mouse.py mouse_click_at 500 600 left
```

### Coordinate calibration workflow
```bash
python scripts/draw_overlay.py marker target 3788 2080 --text "Send button" --duration 10
python scripts/draw_overlay.py marker target 3790 2090 --text "Send button (adjusted)" --duration 10
python scripts/keyboard_mouse.py mouse_click_at 3790 2090 left
```

### Image annotation workflow (cost-saving)
```bash
python scripts/keyboard_mouse.py screenshot screen.png

python scripts/draw_on_image.py screen.png marker target 3788 2080 --text "Candidate 1" -o marked1.png
python scripts/draw_on_image.py screen.png marker target 3790 2090 --text "Candidate 2" -o marked2.png
python scripts/draw_on_image.py screen.png marker target 3785 2085 --text "Candidate 3" -o marked3.png

python scripts/draw_overlay.py marker target 3790 2090 --duration 3
python scripts/keyboard_mouse.py mouse_click_at 3790 2090 left
```

### Image locating workflow (recommended)
```bash
python scripts/image_finder.py image template.png --threshold 0.9
python scripts/image_finder.py image template.png --click

python scripts/image_finder.py text "Send" --click
python scripts/image_finder.py text "Send" --mark-on-image checked.png
python scripts/image_finder.py text-all --mark
```

### Cleanup workflow
```bash
python scripts/cleanup.py analyze .
python scripts/cleanup.py clean . --days 7
python scripts/cleanup.py clean . --days 7 --execute
python scripts/cleanup.py auto . --max-files 20 --max-size 50
```

## Coordinates

- Origin (0, 0) is the top-left corner of the screen
- X increases to the right
- Y increases downward

## Safety Notes

1. Make sure the target window is focused before running actions
2. Be careful with system hotkeys to avoid unintended side effects
3. Moving the mouse to the top-left corner (0, 0) triggers PyAutoGUI failsafe
4. Add delays when needed to give yourself time to interrupt

## Cross-platform Support

| Platform | Status | Notes |
|----------|--------|-------|
| Windows | ✅ Full | May require admin permissions in some environments |
| Linux | ✅ Supported | Requires X11; Wayland may not work |
| macOS | ✅ Supported | Requires Accessibility permission for Terminal/Python |

## Project Layout

```
openclaw-pyautogui-skill/
├── SKILL.md              # Skill documentation
├── README.md             # This file
└── scripts/
    ├── keyboard_mouse.py # Mouse/keyboard automation
    ├── image_utils.py    # Image utilities
    ├── draw_overlay.py   # Screen overlay markers
    ├── draw_on_image.py  # Draw markers on images
    ├── image_finder.py   # Template matching + OCR locating
    └── cleanup.py        # Cleanup tool
```

## Dependencies

- Python 3.7+
- pyautogui
- Pillow
- opencv-python
- numpy
- rapidocr_onnxruntime

## License

MIT License
