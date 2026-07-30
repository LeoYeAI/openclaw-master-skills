---
name: unihiker-k10-arduino
description: Use when programming Unihiker K10 board with Arduino/C++, uploading code, flashing firmware, or accessing K10 Arduino APIs (screen, sensors, RGB, audio, AI, TTS, ASR)
---

# Unihiker K10 - Arduino

## Overview

CLI toolkit for Unihiker K10 board Arduino programming. **Core principle:** Follow reference docs exactly—no improvisation.

**Firmware Version**: 0.9.2
**FQBN**: `UNIHIKER:esp32:k10`

## When to Use

- Uploading Arduino/C++ code to K10
- Flashing Arduino firmware
- Looking up K10 Arduino APIs (screen, canvas, sensors, RGB, audio)
- Setting up development environment for the first time
- Port detection or connectivity issues

## Environment Setup (MANDATORY - First Time Only)

Before uploading code, ensure your Arduino environment is configured correctly.

### Windows 快速安装 (推荐)

在Windows上，skill目录已包含预下载的 `arduino-cli.exe`，可直接使用：

```powershell
# 进入skill脚本目录
cd ~/.agents/skills/unihiker-k10-arduino/scripts

# 验证arduino-cli可用
.\arduino-cli.exe version

# 添加到PATH (PowerShell)
$env:PATH = "$env:PATH;$env:USERPROFILE\.agents\skills\unihiker-k10-arduino\scripts"

# 永久添加到PATH (可选)
[Environment]::SetEnvironmentVariable("PATH", $env:PATH, "User")
```

### Step 1: Check arduino-cli Installation

```bash
# Check if arduino-cli is installed
which arduino-cli

# Check installed version
arduino-cli version
```

**Expected output:**
```bash
arduino-cli 0.35.0
# Or any version number
```

**If `which arduino-cli` returns empty or "arduino-cli: not found":** Proceed to Step 2.

### Step 2: Install arduino-cli (If Not Installed)

**macOS:**
```bash
# Download the latest release from GitHub
# Visit: https://github.com/arduino/arduino-cli/releases
# Or use Homebrew
brew install arduino-cli
```

**Linux (Ubuntu/Debian):**
```bash
# Download the latest release from GitHub
# Visit: https://github.com/arduino/arduino-cli/releases
# Or use apt (may be outdated)
sudo apt install arduino-cli

# Or download the binary and add to PATH
wget https://github.com/arduino/arduino-cli/releases/download/0.35.0/arduino-cli_0.35.0_Linux_64bit.tar.gz
tar -xzf arduino-cli_0.35.0_Linux_64bit.tar.gz
sudo mv arduino-cli /usr/local/bin/
```

**Windows:**
```powershell
# 方法1: 使用skill自带的arduino-cli (推荐)
# 文件位置: ~/.agents/skills/unihiker-k10-arduino/scripts/arduino-cli.exe

# 方法2: 手动下载
# Visit: https://github.com/arduino/arduino-cli/releases
# Download: arduino-cli_1.2.0_Windows_64bit.zip
# Extract to a folder and add to PATH
```

### Step 3: Install K10 BSP (Board Support Package)

The K10 BSP is required for arduino-cli to recognize the Unihiker K10 board.

```bash
# Add K10 BSP URL to arduino-cli
arduino-cli config add board_manager.additional_urls https://downloadcd.dfrobot.com.cn/UNIHIKER/package_unihiker_index.json

# Update core index
arduino-cli core update-index

# Install K10 core
arduino-cli core install UNIHIKER:esp32

# Verify installation
arduino-cli board listall | findstr unihiker
```

**Expected output:**
```bash
UNIHIKER:esp32:k10
```

**注意:** BSP包大小约500MB，首次下载需要较长时间。

### Verification

After completing Steps 1-3, verify your environment:

```bash
# Check arduino-cli
arduino-cli version

# Check K10 board
arduino-cli board listall | findstr unihiker

# Check ports
arduino-cli board list
```

## Commands

| Command | Description |
|---------|-------------|
| `k10-arduino upload <file.ino>` | Compile & upload Arduino sketch |
| `k10-arduino ports` | List serial ports |
| `k10-arduino doctor` | Environment diagnostic |

## Coding

### Basic Template

```cpp
#include "unihiker_k10.h"

UNIHIKER_K10 k10;

void setup() {
  k10.begin();
  k10.initScreen(2);           // Screen direction: 0-3
  k10.creatCanvas();           // Create canvas object
  k10.setScreenBackground(0x000000);  // Background color (black)

  // Canvas drawing methods (use k10.canvas->)
  k10.canvas->canvasSetLineWidth(3);
  k10.canvas->canvasLine(0, 0, 100, 100, 0xFFFF00);
  k10.canvas->canvasCircle(80, 80, 40, 0x00FF00, 0x0000FF, false);
  k10.canvas->updateCanvas();   // Update display
}

void loop() {
  // Your code here
}
```

**Important:**
- **File structure**: `.ino` file must be in a directory with the same name (e.g., `star/star.ino`)
- **Canvas API**: All canvas methods use `k10.canvas->`, not `k10.`
- **FQBN**: `UNIHIKER:esp32:k10`
- **Reference**: [`references/arduino-api.md`](references/arduino-api.md)

## Common Issues

| Issue | Solution |
|-------|----------|
| **arduino-cli: command not found** | Windows用户使用skill目录下的arduino-cli.exe，或安装并添加到PATH |
| **Platform 'UNIHIKER:esp32:k10' not found** | 安装K10 BSP: `arduino-cli core install UNIHIKER:esp32` |
| **Can't open sketch: main file missing** | `.ino`文件必须放在同名目录中 (如 `star/star.ino`) |
| **Class has no member named 'canvasLine'** | Canvas方法使用 `k10.canvas->`，不是 `k10.` |
| **编译错误: No such file or directory** | 检查库依赖，部分库需要手动安装到Documents/Arduino/libraries |
| **上传失败/无法连接** | 按住BOOT按钮，按RST重置，释放BOOT进入下载模式 |
| **屏幕闪烁** | 使用局部刷新，避免每帧调用 `canvasClear()`，详见性能优化章节 |
| **Windows PowerShell执行策略限制** | 运行 `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser` |

## 上传脚本使用说明

Skill目录提供多种上传方式：

### Windows 用户

```powershell
# 方法1: PowerShell脚本
.\scripts\upload-arduino.ps1 .\your_sketch\your_sketch.ino

# 方法2: Python脚本
python .\scripts\upload_k10.py .\your_sketch\your_sketch.ino

# 方法3: Batch脚本
.\scripts\upload-k10.bat .\your_sketch\your_sketch.ino
```

### macOS/Linux 用户

```bash
# Bash脚本
bash scripts/upload-arduino.sh ./your_sketch/your_sketch.ino
```

## Performance Tips

### Screen Rendering Optimization

K10 的屏幕刷新率有限，频繁的全屏清除 (`canvasClear()`) 会导致闪烁和卡顿。推荐使用**局部刷新**技术：

**核心思想：**
1. 只擦除变化的部分，而不是整个屏幕
2. 用背景色填充旧位置来"擦除"
3. 在新位置绘制元素

**示例代码：**

```cpp
// 保存上一帧位置
int lastX = 0, lastY = 0;

void drawSprite(int x, int y, uint32_t color) {
  k10.canvas->canvasCircle(x, y, 10, color, color, true);
}

void eraseSprite(int x, int y) {
  // 用背景色填充来擦除
  k10.canvas->canvasRectangle(x-12, y-12, 24, 24, COLOR_BG, COLOR_BG, true);
}

void update() {
  // 1. 擦除旧位置
  eraseSprite(lastX, lastY);
  
  // 2. 更新位置
  x += speed;
  
  // 3. 绘制新位置
  drawSprite(x, y, 0xFF0000);
  
  // 4. 保存当前位置
  lastX = x;
  lastY = y;
  
  k10.canvas->updateCanvas();
}
```

**优化建议：**
- 静态背景（如云朵、地面）只绘制一次
- 降低帧率到 30-40fps 以平衡流畅度和性能
- 避免每帧都调用 `canvasClear()`
- 使用 `delay(25-33)` 控制帧率 (对应 30-40fps)

## 开发经验教训

### 2025-03-22 实践总结

**成功的经验：**
1. **预下载工具链**: 在skill目录中预置arduino-cli.exe，避免用户下载问题
2. **多脚本支持**: 提供PowerShell、Python、Batch三种上传脚本，适应不同Windows环境
3. **自动端口检测**: 脚本自动检测K10端口，减少用户配置负担

**遇到的问题及解决：**
1. **BSP安装问题**: 最初使用 `esp32:unihiker` 不正确，应使用 `UNIHIKER:esp32`
2. **库依赖问题**: 部分第三方库（如arduinoFFT）需要手动安装到Documents/Arduino/libraries
3. **Windows执行策略**: PowerShell脚本需要调整执行策略才能运行
4. **INO文件结构**: 必须将.ino文件放在同名目录中，否则编译失败

**改进建议：**
- 首次使用前运行环境检查脚本
- 提供依赖库自动安装功能
- 添加更详细的错误提示和解决方案

## Files

```
unihiker-k10-arduino/
├── SKILL.md                 # This file
└── references/            # Arduino API docs
    ├── arduino-api.md     # Arduino C++ API reference
    └── arduino-examples.md # Arduino code examples
```

**Manual usage without CLI:**
```bash
# Upload Arduino
bash path/to/unihiker-k10-arduino/scripts/upload-arduino.sh sketch.ino /dev/cu.usbmodem2201 UNIHIKER:esp32:k10
```

## Quick Development Workflow

```bash
# 1. Create Arduino sketch in project directory
your_project/
└── your_sketch/
    └── your_sketch.ino

# 2. Upload sketch
k10-arduino upload your_project/your_sketch/your_sketch.ino
```

## Key Features

**Screen & Canvas:**
- Screen initialization and direction control
- Canvas drawing: text, lines, circles, rectangles, images, QR codes
- Background color management

**Sensors:**
- Buttons A/B (pressed callback and polling)
- Accelerometer (X, Y, Z axes)
- Temperature & humidity (AHT20)
- Light sensor (ALS)
- Pedometer (step counting)
- Microphone (recording and playback)

**RGB LED Control:**
- Individual LED control (0, 1, 2)
- All LEDs control (-1)
- Brightness control (0-9)

**Audio:**
- Buzzer control (playTone, playMusic)
- Microphone recording to TF card
- Audio playback from TF card
- TTS (Text-to-Speech)

**AI Recognition:**
- Face detection and recognition
- Cat/Dog recognition
- Movement detection
- QR code scanning
- Face enrollment and deletion

**ASR (Speech Recognition):**
- Wake-up command
- Custom command words
- Continuous or single-shot mode

**GPIO:**
- P0/P1: Digital I/O and Analog/PWM
- Extended GPIO via Edge Connector (digital I/O only)

## API Quick Reference

### Display

**Import**: `#include "unihiker_k10.h"`

```cpp
k10.initScreen(dir=2, frame=0);              // Initialize screen
k10.creatCanvas();                            // Create canvas
k10.setScreenBackground(color=0x000000);       // Background color
k10.initBgCamerImage();                      // Init camera image
k10.setBgCamerImage(sta=true);              // Display camera image

// Canvas drawing (use k10.canvas->)
k10.canvas->canvasSetLineWidth(3);
k10.canvas->canvasLine(x1, y1, x2, y2, color);              // Draw line
k10.canvas->canvasPoint(x, y, color);                       // Draw point
k10.canvas->canvasCircle(x, y, r, border, fill, isFill);   // Draw circle
k10.canvas->canvasRectangle(x, y, w, h, border, fill, isFill); // Draw rect
k10.canvas->canvasText(text, row, color);                     // Draw text
k10.canvas->canvasDrawImage(x, y, imagePath);                  // Draw image
k10.canvas->canvasDrawCode(code);                          // Draw QR code
k10.canvas->clearCode();                                  // Clear QR code
k10.canvas->canvasClear();                                // Clear canvas
k10.canvas->updateCanvas();                             // Update display
```

### SD Card (TF Card)

```cpp
k10.initSDFile();                                 // Initialize SD card
k10.photoSaveToTFCard(imagePath);              // Save photo
k10.playTFCardAudio(path);                       // Play audio
k10.recordSaveToTFCard(path, time);            // Record audio (seconds)
```

### Onboard Sensors

**Buttons A/B**:
```cpp
k10.buttonA->isPressed();                           // Check state
k10.buttonA->setPressedCallback(callback);            // Press callback
k10.buttonA->setUnPressedCallback(callback);          // Release callback
```

**Temperature & Humidity (AHT20)**:
```cpp
AHT20 aht20;
k10.getData(AHT20::eAHT20TempC);    // Temperature (°C)
k10.getData(AHT20::eAHT20TempF);    // Temperature (°F)
k10.getData(AHT20::eAHT20HumiRH);   // Humidity (%RH)
```

**Light Sensor (ALS)**:
```cpp
k10.readALS();  // Light intensity
```

**Accelerometer**:
```cpp
k10.getAccelerometerX();  // X-axis
k10.getAccelerometerY();  // Y-axis
k10.getAccelerometerZ();  // Z-axis
k10.getStrength();        // Strength
k10.isGesture(Gesture);  // Tilt detection (TiltForward, TiltBack, TiltLeft, TiltRight)
```

**Pedometer**:
```cpp
k10.getStrength();  // Step count
```

**RGB LED**:
```cpp
k10.write(index, r, g, b);        // Set color (0,1,2,-1=all)
k10.setRangeColor(start, end, color); // Set range
k10.brightness(b);                  // Brightness (0-9)
```

**Audio**:
```cpp
// Buzzer
k10.playTone(freq, beat);      // Play tone (samples: 8000=full, 4000=half)
k10.stopPlayTone();           // Stop tone
k10.playMusic(Melodies, options); // Built-in music
k10.stopPlayAudio();            // Stop audio

// TTS (Text-to-Speech)
asr.setAsrSpeed(speed);      // Set speed
asr.speak(text);             // Speak text
```

**Microphone**:
```cpp
// Recording and playback
k10.recordSaveToTFCard(path, time);  // Record to TF card
k10.playTFCardAudio(path);          // Play from TF card
```

### AI Recognition

**Import**: `#include "AIRecognition.h"`

```cpp
AIRecognition ai;

ai.initAi();                           // Initialize AI
ai.switchAiMode(mode);                // Select mode: Face, Cat, Move, Code, NoMode

// Face recognition
ai.sendFaceCmd(ENROLL);               // Learn face
ai.sendFaceCmd(RECOGNIZE);           // Recognize face
ai.sendFaceCmd(DELETEALL);           // Delete all faces
ai.sendFaceCmd(DELETE, id);           // Delete specific face ID

int faceId = ai.getRecognitionID();     // Get recognized face ID
int faceData = ai.getFaceData(type);   // Get face data (Length, Width, CenterX, CenterY, etc.)
bool recognized = ai.isRecognized();      // Check if recognition complete

// Cat/Dog recognition
int catData = ai.getCatData(type);      // Get cat data

// Movement detection
ai.setMotinoThreshold(10);              // Set sensitivity (10-200)

// QR code
String qrCode = ai.getQrCodeContent();  // Get scanned QR code

// Content detection
bool detected = ai.isDetectContent(mode);
```

### ASR (Speech Recognition)

**Import**: `#include "asr.h"`

```cpp
ASR asr;

// Initialize
asr.asrInit(mode=ONCE|CONTINUOUS, lang=EN_MODE|CN_MODE, wakeUpTime=6000);

// Add commands
asr.addASRCommand(id, "command text");
asr.addASRCommand(id, "拼音文本");  // For Chinese commands

// Check status
bool wakeUp = asr.isWakeUp();             // Wake-up status
bool cmdDetected = asr.isDetectCmdID(id);  // Command detected
```

**ASR Constants**:
- `ONCE`, `CONTINUOUS`
- `EN_MODE`, `CN_MODE`

### GPIO

**P0/P1 (on-board)**:
```cpp
pinMode(P0, OUTPUT);           // Set pin mode
digitalWrite(P0, HIGH);         // Digital write
digitalRead(P1);                // Digital read
analogWrite(P0, value);          // PWM output (0-255)
analogRead(P1);                 // Analog input
```

**Extended GPIO (Edge Connector)**:
```cpp
digital_write(eP2, HIGH);      // Digital write
digital_read(eP3);             // Digital read
// Note: Extended GPIO is digital I/O only
```

## Common Imports

```cpp
// K10 library
#include "unihiker_k10.h"

// AI Recognition
#include "AIRecognition.h"

// ASR
#include "asr.h"

// Arduino core
#include <Arduino.h>
```

## Examples Available

**See [`references/arduino-examples.md`](references/arduino-examples.md)**

1. **Display Examples**
   - Background color cycling
   - Drawing points, lines, circles, rectangles
   - QR code generation
   - Electronic photo album

2. **Sensor Examples**
   - Button A/B control (interrupt and polling)
   - Accelerometer ball movement
   - Pedometer display
   - All sensors display on screen

3. **RGB LED Examples**
   - Rainbow cycle (7 colors)
   - Brightness breathing effect

4. **Audio Examples**
   - Built-in music playback
   - Audio recording to TF card
   - Audio playback from TF card
   - TTS examples

5. **GPIO Examples**
   - Digital input/output on P0/P1
   - Analog input/PWM output on P0

6. **AI Examples**
   - Face detection and recognition
   - Cat/Dog recognition
   - Movement detection
   - QR code scanning
   - Face enrollment and deletion

7. **ASR Examples**
   - Wake-up command
   - Custom command words
   - Light control via voice

8. **Combined Examples**
   - Sensor data display (temperature, humidity, light, acceleration, steps)
   - Multi-sensor dashboard
