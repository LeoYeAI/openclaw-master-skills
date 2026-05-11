# Desktop Control - Quick Reference Card

## 🚀 Instant Start

```python
from skills.desktop_control import DesktopController

dc = DesktopController()
```

## 🖱️ Mouse Control (Top 10)

```python
# 1. Move mouse
dc.move_mouse(500, 300, duration=0.5)

# 2. Click
dc.click(500, 300)  # Left click at position
dc.click()           # Click at current position

# 3. Right click
dc.right_click(500, 300)

# 4. Double click
dc.double_click(500, 300)

# 5. Drag & drop
dc.drag(100, 100, 500, 500, duration=1.0)

# 6. Scroll
dc.scroll(-5)  # Scroll down 5 clicks

# 7. Get position
x, y = dc.get_mouse_position()

# 8. Move relative
dc.move_relative(100, 50)  # Move 100px right, 50px down

# 9. Smooth movement
dc.move_mouse(1000, 500, duration=1.0, smooth=True)

# 10. Middle click
dc.middle_click()
```

## ⌨️ Keyboard Control (Top 10)

```python
# 1. Type text (instant)
dc.type_text("Hello World")

# 2. Type text (human-like, 60 WPM)
dc.type_text("Hello World", wpm=60)

# 3. Press key
dc.press('enter')
dc.press('tab')
dc.press('escape')

# 4. Hotkeys (shortcuts)
dc.hotkey('ctrl', 'c')      # Copy
dc.hotkey('ctrl', 'v')      # Paste  
dc.hotkey('ctrl', 's')      # Save
dc.hotkey('win', 'r')       # Run dialog
dc.hotkey('alt', 'tab')     # Switch window

# 5. Hold & release
dc.key_down('shift')
dc.type_text("hello")  # Types "HELLO"
dc.key_up('shift')

# 6. Arrow keys
dc.press('up')
dc.press('down')
dc.press('left')
dc.press('right')

# 7. Function keys
dc.press('f5')  # Refresh

# 8. Multiple presses
dc.press('backspace', presses=5)

# 9. Special keys
dc.press('home')
dc.press('end')
dc.press('pagedown')
dc.press('delete')

# 10. Fast combo
dc.hotkey('ctrl', 'alt', 'delete')
```

## 📸 Screen Operations (Top 5)

```python
# 1. Screenshot (full screen)
img = dc.screenshot()
dc.screenshot(filename="screen.png")

# 2. Screenshot (region)
img = dc.screenshot(region=(100, 100, 800, 600))

# 3. Get pixel color
r, g, b = dc.get_pixel_color(500, 300)

# 4. Find image on screen
location = dc.find_on_screen("button.png")

# 5. Get screen size
width, height = dc.get_screen_size()
```

## 🪟 Window Management (Top 5)

```python
# 1. Get all windows
windows = dc.get_all_windows()

# 2. Activate window
dc.activate_window("Chrome")

# 3. Get active window
active = dc.get_active_window()

# 4. List windows
for title in dc.get_all_windows():
    print(title)

# 5. Switch to app
dc.activate_window("Visual Studio Code")
```

## 📋 Clipboard (Top 2)

```python
# 1. Copy to clipboard
dc.copy_to_clipboard("Hello!")

# 2. Get from clipboard
text = dc.get_from_clipboard()
```

## 🔥 Real-World Examples

### Example 1: Auto-fill Form
```python
dc.click(300, 200)  # Name field
dc.type_text("John Doe", wpm=80)
dc.press('tab')
dc.type_text("john@email.com", wpm=80)
dc.press('tab')
dc.type_text("Password123", wpm=60)
dc.press('enter')
```

### Example 2: Copy-Paste Automation
```python
# Select all
dc.hotkey('ctrl', 'a')
# Copy
dc.hotkey('ctrl', 'c')
# Wait
dc.pause(0.5)
# Switch window
dc.hotkey('alt', 'tab')
# Paste
dc.hotkey('ctrl', 'v')
```

### Example 3: File Operations
```python
# Select multiple files
dc.key_down('ctrl')
dc.click(100, 200)
dc.click(100, 250)
dc.click(100, 300)
dc.key_up('ctrl')
# Copy
dc.hotkey('ctrl', 'c')
```

### Example 4: Screenshot Workflow
```python
# Take screenshot
dc.screenshot(filename=f"capture_{time.time()}.png")
# Open in Paint
dc.hotkey('win', 'r')
dc.pause(0.5)
dc.type_text('mspaint')
dc.press('enter')
```

### Example 5: Search & Replace
```python
# Open Find & Replace
dc.hotkey('ctrl', 'h')
dc.pause(0.3)
# Type find text
dc.type_text("old_text")
dc.press('tab')
# Type replace text
dc.type_text("new_text")
# Replace all
dc.hotkey('alt', 'a')
```

## ⚙️ Configuration

```python
# With failsafe (move to corner to abort)
dc = DesktopController(failsafe=True)

# With approval mode (ask before each action)
dc = DesktopController(require_approval=True)

# Maximum speed (no safety checks)
dc = DesktopController(failsafe=False)
```

## 🛡️ Safety

```python
# Check if safe to continue
if dc.is_safe():
    dc.click(500, 500)

# Pause execution
dc.pause(2.0)  # Wait 2 seconds

# Emergency abort: Move mouse to any screen corner
```

## 🎯 Pro Tips

1. **Instant typing**: `interval=0` or `wpm=None`
2. **Human typing**: `wpm=60` (60 words/min)
3. **Smooth mouse**: `duration=0.5, smooth=True`
4. **Instant mouse**: `duration=0`
5. **Wait for UI**: `dc.pause(0.5)` between actions
6. **Failsafe**: Always enable for safety
7. **Test first**: Use `demo.py` to test features
8. **Coordinates**: Use `get_mouse_position()` to find them
9. **Screenshots**: Capture before/after for verification
10. **Hotkeys > Menus**: Faster and more reliable

## 📦 Dependencies

```bash
pip install pyautogui pillow opencv-python pygetwindow pyperclip
```

## 🚨 Common Issues

**Mouse not moving correctly?**
- Check DPI scaling in Windows settings
- Verify coordinates with `get_mouse_position()`

**Keyboard not working?**
- Ensure target app has focus
- Some apps block automation (games, secure apps)

**Failsafe triggering?**
- Keep mouse away from screen corners
- Disable if needed: `failsafe=False`

---

**Built for OpenClaw** 🦞 - Desktop automation made easy!
