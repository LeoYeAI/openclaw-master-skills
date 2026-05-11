"""
Desktop Control Demo - Quick examples and tests
"""

import sys
import time
from pathlib import Path

# Add skills to path
sys.path.insert(0, str(Path(__file__).parent))

from desktop_control import DesktopController

def demo_mouse_control():
    """Demo: Mouse movement and clicking"""
    print("\n🖱️  === MOUSE CONTROL DEMO ===")
    
    dc = DesktopController(failsafe=True)
    
    print(f"Current position: {dc.get_mouse_position()}")
    
    # Smooth movement
    print("\n1. Moving mouse smoothly to center of screen...")
    screen_w, screen_h = dc.get_screen_size()
    center_x, center_y = screen_w // 2, screen_h // 2
    dc.move_mouse(center_x, center_y, duration=1.0)
    
    # Relative movement
    print("2. Moving 100px right...")
    dc.move_relative(100, 0, duration=0.5)
    
    print(f"Final position: {dc.get_mouse_position()}")
    
    print("✅ Mouse demo complete!")


def demo_keyboard_control():
    """Demo: Keyboard typing"""
    print("\n⌨️  === KEYBOARD CONTROL DEMO ===")
    
    dc = DesktopController()
    
    print("\n⚠️  In 3 seconds, I'll type 'Hello from OpenClaw!' in the active window")
    print("Switch to Notepad or any text editor NOW!")
    time.sleep(3)
    
    # Type with human-like speed
    dc.type_text("Hello from OpenClaw! ", wpm=60)
    dc.type_text("This is desktop automation in action. ", wpm=80)
    
    # Press Enter
    dc.press('enter')
    dc.press('enter')
    
    # Type instant
    dc.type_text("This was typed instantly!", interval=0)
    
    print("\n✅ Keyboard demo complete!")


def demo_screen_capture():
    """Demo: Screenshot functionality"""
    print("\n📸 === SCREEN CAPTURE DEMO ===")
    
    dc = DesktopController()
    
    # Full screenshot
    print("\n1. Capturing full screen...")
    dc.screenshot(filename="demo_fullscreen.png")
    print("   Saved: demo_fullscreen.png")
    
    # Region screenshot (center 800x600)
    print("\n2. Capturing center region (800x600)...")
    screen_w, screen_h = dc.get_screen_size()
    region = (
        (screen_w - 800) // 2,  # left
        (screen_h - 600) // 2,  # top
        800,  # width
        600   # height
    )
    dc.screenshot(region=region, filename="demo_region.png")
    print("   Saved: demo_region.png")
    
    # Get pixel color
    print("\n3. Getting pixel color at center...")
    center_x, center_y = screen_w // 2, screen_h // 2
    r, g, b = dc.get_pixel_color(center_x, center_y)
    print(f"   Color at ({center_x}, {center_y}): RGB({r}, {g}, {b})")
    
    print("\n✅ Screen capture demo complete!")


def demo_window_management():
    """Demo: Window operations"""
    print("\n🪟 === WINDOW MANAGEMENT DEMO ===")
    
    dc = DesktopController()
    
    # Get current window
    print(f"\n1. Active window: {dc.get_active_window()}")
    
    # List all windows
    windows = dc.get_all_windows()
    print(f"\n2. Found {len(windows)} open windows:")
    for i, title in enumerate(windows[:15], 1):  # Show first 15
        print(f"   {i}. {title}")
    
    print("\n✅ Window management demo complete!")


def demo_hotkeys():
    """Demo: Keyboard shortcuts"""
    print("\n🔥 === HOTKEY DEMO ===")
    
    dc = DesktopController()
    
    print("\n⚠️  This demo will:")
    print("   1. Open Windows Run dialog (Win+R)")
    print("   2. Type 'notepad'")
    print("   3. Press Enter to open Notepad")
    print("   4. Type a message")
    print("\nPress Enter to continue...")
    input()
    
    # Open Run dialog
    print("\n1. Opening Run dialog...")
    dc.hotkey('win', 'r')
    time.sleep(0.5)
    
    # Type notepad command
    print("2. Typing 'notepad'...")
    dc.type_text('notepad', wpm=80)
    time.sleep(0.3)
    
    # Press Enter
    print("3. Launching Notepad...")
    dc.press('enter')
    time.sleep(1)
    
    # Type message
    print("4. Typing message in Notepad...")
    dc.type_text("Desktop Control Skill Test\n\n", wpm=60)
    dc.type_text("This was automated by OpenClaw!\n", wpm=60)
    dc.type_text("- Mouse control ✓\n", wpm=60)
    dc.type_text("- Keyboard control ✓\n", wpm=60)
    dc.type_text("- Hotkeys ✓\n", wpm=60)
    
    print("\n✅ Hotkey demo complete!")


def demo_advanced_automation():
    """Demo: Complete automation workflow"""
    print("\n🚀 === ADVANCED AUTOMATION DEMO ===")
    
    dc = DesktopController()
    
    print("\nThis demo will:")
    print("1. Get your clipboard content")
    print("2. Copy a new string to clipboard")
    print("3. Show the changes")
    print("\nPress Enter to continue...")
    input()
    
    # Get current clipboard
    original = dc.get_from_clipboard()
    print(f"\n1. Original clipboard: '{original}'")
    
    # Copy new content
    test_text = "Hello from OpenClaw Desktop Control!"
    dc.copy_to_clipboard(test_text)
    print(f"2. Copied to clipboard: '{test_text}'")
    
    # Verify
    new_clipboard = dc.get_from_clipboard()
    print(f"3. Verified clipboard: '{new_clipboard}'")
    
    # Restore original
    if original:
        dc.copy_to_clipboard(original)
        print("4. Restored original clipboard")
    
    print("\n✅ Advanced automation demo complete!")


def  main():
    """Run all demos"""
    print("=" * 60)
    print("🎮 DESKTOP CONTROL SKILL - DEMO SUITE")
    print("=" * 60)
    print("\n⚠️  IMPORTANT:")
    print("- Failsafe is ENABLED (move mouse to corner to abort)")
    print("- Some demos will control your mouse and keyboard")
    print("- Close important applications before continuing")
    print("\n" + "=" * 60)
    
    demos = [
        ("Mouse Control", demo_mouse_control),
        ("Window Management", demo_window_management),
        ("Screen Capture", demo_screen_capture),
        ("Hotkeys", demo_hotkeys),
        ("Keyboard Control", demo_keyboard_control),
        ("Advanced Automation", demo_advanced_automation),
    ]
    
    while True:
        print("\n📋 SELECT DEMO:")
        for i, (name, _) in enumerate(demos, 1):
            print(f"  {i}. {name}")
        print(f"  {len(demos) + 1}. Run All")
        print("  0. Exit")
        
        choice = input("\nEnter choice: ").strip()
        
        if choice == '0':
            print("\n👋 Goodbye!")
            break
        elif choice == str(len(demos) + 1):
            for name, func in demos:
                print(f"\n{'=' * 60}")
                func()
                time.sleep(1)
            print(f"\n{'=' * 60}")
            print("🎉 All demos complete!")
        elif choice.isdigit() and 1 <= int(choice) <= len(demos):
            demos[int(choice) - 1][1]()
        else:
            print("❌ Invalid choice!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
