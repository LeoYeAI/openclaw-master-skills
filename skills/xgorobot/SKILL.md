---
name: xgorobot
description: |
  XGO 系列机器狗(Mini/Lite/Mini3W/Rider)完整控制能力。
  
  **两层执行能力：**
  1. **预置脚本**：scripts/ 目录下 80+ 个即用脚本，覆盖运动、动作、视觉、AI、传感器等
  2. **自定义代码**：参考 lib/ 中的 API 文档编写复杂逻辑和组合任务
  
  **功能覆盖：**
  - 运动控制：前进/后退/左移/右移/转向/蹲下/站立/踏步/周期运动/步态切换
  - 预设动作：坐下/趴下/招手/俯卧撑/祈祷/摇摆/匍匐/伸展/旋转等
  - 视觉识别：拍照/人脸/手势/颜色/巡线/二维码/目标检测/情绪识别
  - AI功能：语音识别/文字转语音/图片理解/图片生成
  - 传感器：电量/IMU姿态角/舵机角度
  - 屏幕音频：文字显示/图片显示/音频播放
  - 机型专用：Mini机械臂/Mini3W轮控/Rider双轮足
  
  当用户提到机器狗、XGO、走路、跑步、前进、后退、转向、蹲下、站立、摇摆、做动作、摄像头、拍照、识别、检测、手势、人脸、颜色、巡线、二维码、屏幕显示、语音、AI、机械臂、夹爪、轮控等场景时使用此 skill。
metadata:
  openclaw:
    emoji: "🐕"
    requires: { "env": ["DASHSCOPE_API_KEY"] }
    primaryEnv: "DASHSCOPE_API_KEY"
---

# XGO 机器狗控制

控制 XGO 系列机器狗（Mini/Lite/Mini3W/Rider），涵盖运动控制、视觉识别、AI 功能、传感器读取等完整能力。

## 执行环境（强制）

**必须使用指定的虚拟环境 Python：**

### 标准执行命令（必须使用）

```bash
# 统一执行模板（cd到skill目录 + 超时保护）
cd /home/pi/.npm-global/lib/node_modules/openclaw/skills/xgorobot && timeout 30 /home/pi/RaspberryPi-CM5/blocklyvenv/bin/python -u scripts/xxx.py
```

**预置脚本示例：**
```bash
cd /home/pi/.npm-global/lib/node_modules/openclaw/skills/xgorobot && timeout 30 /home/pi/RaspberryPi-CM5/blocklyvenv/bin/python -u scripts/motion/forward.py --step 15
```

**自定义代码示例：**
```bash
cd /home/pi/.npm-global/lib/node_modules/openclaw/skills/xgorobot && timeout 30 /home/pi/RaspberryPi-CM5/blocklyvenv/bin/python -u /tmp/my_script.py
```

> **重要**：
> - 不要用 sudo（openclaw 不支持）
> - 必须用 `timeout 30` 包裹，防止脚本卡死
> - 如果仍然卡住，检查机器狗是否开机、串口连接是否正常

---

## 执行策略（重要）

### 优先级 1：使用预置脚本

**优先检查 `scripts/` 目录下是否有匹配的预置脚本，直接执行：**

```bash
cd /home/pi/.npm-global/lib/node_modules/openclaw/skills/xgorobot && timeout 30 /home/pi/RaspberryPi-CM5/blocklyvenv/bin/python -u scripts/motion/forward.py --step 15
```

### 优先级 2：开放式识别优先用 AI 图片理解

**当需要识别/理解任意物体时，优先使用 `photo_understand.py`：**

| 场景 | 用 AI 图片理解 | 用 YOLO/传统视觉 |
|------|-----------------|----------------|
| 识别任意物体（纸巾、胡萝卜、杯子...） | ✓ 推荐 | ✗ 类别有限 |
| 判断物体位置（左/中/右） | ✓ 推荐 | ✗ 需额外计算 |
| 理解场景/回答问题 | ✓ 推荐 | ✗ 不支持 |
| 实时追踪已知类别（人/球） | ✗ 太慢 | ✓ 推荐 |
| 快速检测有无人脸 | ✗ 太慢 | ✓ 推荐 |

**AI 图片理解示例：**

```bash
# 问图中某物体的位置
cd /home/pi/.npm-global/lib/node_modules/openclaw/skills/xgorobot && timeout 30 /home/pi/RaspberryPi-CM5/blocklyvenv/bin/python -u scripts/ai/photo_understand.py --prompt "图中纸巾在什么位置？只回答：左边/中间/右边/没有"

# 识别图中有哪些物体
cd /home/pi/.npm-global/lib/node_modules/openclaw/skills/xgorobot && timeout 30 /home/pi/RaspberryPi-CM5/blocklyvenv/bin/python -u scripts/ai/photo_understand.py --prompt "图中有哪些物品？列出名称"

# 判断场景
cd /home/pi/.npm-global/lib/node_modules/openclaw/skills/xgorobot && timeout 30 /home/pi/RaspberryPi-CM5/blocklyvenv/bin/python -u scripts/ai/photo_understand.py --prompt "这是室内还是室外？"
```

> **简单说：** YOLO 只能识别 80 种固定类别，AI 图片理解能识别任何东西并回答问题。

### 优先级 3：预置脚本不满足时才生成代码

当预置脚本参数无法满足需求，或需要组合多个功能时，参考 `lib/` 目录的 API 编写新代码。

---

## 预置脚本列表

### 基础运动 (scripts/motion/)

| 脚本 | 功能 | 参数 |
|------|------|------|
| `forward.py` | 前进 | `--step 15` (0-25) `--duration 2` |
| `backward.py` | 后退 | `--step 15` (0-25) `--duration 2` |
| `left.py` | 左移 | `--step 10` (0-18) `--duration 2` |
| `right.py` | 右移 | `--step 10` (0-18) `--duration 2` |
| `turn.py` | 旋转 | `--speed 50` (-100~100，正左负右) `--duration 1` |
| `turn_left.py` | 左转 | `--speed 50` (0-100) `--duration 1` |
| `turn_right.py` | 右转 | `--speed 50` (0-100) `--duration 1` |
| `stop.py` | 停止 | 无参数 |
| `reset.py` | 复位 | 无参数 |

### 姿态控制 (scripts/motion/)

| 脚本 | 功能 | 参数 |
|------|------|------|
| `squat.py` | 蹲下 | `--height 80` (75-120mm) |
| `stand.py` | 站立 | `--height 115` (75-120mm) |
| `tilt.py` | 倾斜 | `--roll 0` `--pitch 0` `--yaw 0` |
| `attitude.py` | 姿态控制 | `--roll 10` (-20~20) `--pitch 5` (-22~22) `--yaw 0` (-16~16) |
| `translation.py` | 机身平移 | `--axis z` (x/y/z) `--distance 95` |
| `mark_time.py` | 原地踏步 | `--height 20` (10-35mm) `--duration 3` |

### 周期运动 (scripts/motion/)

| 脚本 | 功能 | 参数 |
|------|------|------|
| `periodic_tran.py` | 周期平移 | `--axis z` (x/y/z) `--period 2` (1.5-8秒) `--duration 5` |
| `periodic_rot.py` | 周期旋转 | `--axis r` (r/p/y) `--period 2` (1.5-8秒) `--duration 5` |

### 步态与速度 (scripts/motion/)

| 脚本 | 功能 | 参数 |
|------|------|------|
| `gait_type.py` | 步态类型 | `--mode trot` (trot/walk/high_walk/slow_trot) |
| `pace.py` | 步频控制 | `--mode normal` (normal/slow/high) |
| `imu.py` | IMU平衡 | `--mode 1` (0=关, 1=开) |

### 单腿与舵机 (scripts/motion/)

| 脚本 | 功能 | 参数 |
|------|------|------|
| `leg.py` | 单腿控制 | `--id 1` (1-4) `--x 0` `--y 0` `--z 95` |
| `motor.py` | 舵机控制 | `--id 11` (11-43,51) `--angle 45` |
| `motor_speed.py` | 舵机速度 | `--speed 128` (1-255) |
| `load_motor.py` | 加载舵机 | `--leg 1` (1-5) |
| `unload_motor.py` | 卸载舵机 | `--leg 1` (1-5) |

### 机械臂 (scripts/motion/) - Mini/Mini3W

| 脚本 | 功能 | 参数 |
|------|------|------|
| `arm.py` | 机械臂控制 | `--action open` (open/close/up/down) |

---

### 预设动作 (scripts/action/)

| 脚本 | 功能 | 参数 |
|------|------|------|
| `action.py` | 执行动作ID | `--id 1` (1-23/128-141/255) |
| `sit.py` | 坐下 | 无参数 |
| `lie_down.py` | 趴下 | 无参数 |
| `stand.py` | 起立 | 无参数 |
| `wave.py` | 招手 | 无参数 |
| `pee.py` | 撒尿 | 无参数 |
| `pushup.py` | 俯卧撑 | 无参数 |
| `pray.py` | 祈祷 | 无参数 |
| `swing.py` | 摇摆 | `--duration 5` |
| `crawl.py` | 匍匐 | 无参数 |
| `stretch.py` | 伸展 | 无参数 |
| `spin.py` | 旋转 | 无参数 |

---

### 视觉识别 (scripts/vision/)

| 脚本 | 功能 | 参数 | 输出 |
|------|------|------|------|
| `take_photo.py` | 拍照 | `--filename photo.jpg` | 照片已保存: {path} |
| `camera_preview.py` | 摄像头预览 | `--duration 10` | 预览窗口显示 |
| `face_detect.py` | 人脸检测 | `--continuous` (持续模式) | 检测到人脸: x=, y=, w=, h= 或 未检测到人脸 |
| `face_count.py` | 人脸计数 | 无 | 共检测到 N 张人脸 + 每张人脸位置 |
| `gesture_detect.py` | 手势识别 | `--continuous` | 识别到手势: {手势} 位置=({x},{y}) 或 无 |
| `color_detect.py` | 颜色识别 | `--color R` (R/G/B/Y) `--continuous` | 检测到{颜色}: 位置=({x},{y}), 半径={r} |
| `line_detect.py` | 巡线检测 | `--color K` (K黑/W白/R/G/B/Y) `--continuous` | 巡线: x={x}, angle={角度} |
| `qr_scan.py` | 二维码扫描 | `--continuous` | 二维码内容: {内容} 或 无 |
| `yolo_detect.py` | 目标检测 | `--continuous` | 检测到: {类别} 位置=({x},{y}) 或 无 |
| `emotion_detect.py` | 情绪识别 | `--continuous` | 情绪: {情绪} 位置=({x},{y}) 或 无 |

### 视觉追踪 (scripts/vision/)

| 脚本 | 功能 | 参数 | 输出 |
|------|------|------|------|
| `find_ball.py` | 寻找小球 | `--color R` `--timeout 30` | ✓ 找到{颜色}色小球 或 ✗ 超时未找到 |
| `find_person.py` | 寻找人类 | `--timeout 45` | ✓ 找到人类 或 ✗ 超时未找到 |
| `catch_ball.py` | 抓取小球 | `--color R` `--timeout 60` | ✓ 抓取成功 或 ✗ 抓取失败 |

---

### 传感器读取 (scripts/sensor/)

| 脚本 | 功能 | 输出 |
|------|------|------|
| `battery.py` | 读取电量 | 百分比 |
| `read_roll.py` | 读取Roll角 | 横滚角度 |
| `read_pitch.py` | 读取Pitch角 | 俯仰角度 |
| `read_yaw.py` | 读取Yaw角 | 偏航角度 |
| `read_imu.py` | 读取IMU | `--axis all` (roll/pitch/yaw/all) |
| `read_motor.py` | 读取舵机角度 | 所有舵机当前角度 |

---

### 屏幕显示 (scripts/display/)

| 脚本 | 功能 | 参数 |
|------|------|------|
| `text.py` | 显示文字 | `--text "Hello"` `--x 5` `--y 5` `--color WHITE` `--size 15` |
| `clear.py` | 清除屏幕 | 无参数 |
| `picture.py` | 显示本地图片 | `--filename photo.jpg` `--x 0` `--y 0` |
| `http_image.py` | 显示网络图片 | `--url "http://..."` `--x 0` `--y 0` |

---

### 音频播放 (scripts/audio/)

| 脚本 | 功能 | 参数 |
|------|------|------|
| `play.py` | 播放本地音频 | `--filename music.mp3` |
| `play_http.py` | 播放网络音频 | `--url "http://..."` |
| `play_music.py` | 播放背景音乐(Dream.mp3) | 无参数 |


---

### AI功能 (scripts/ai/) - 需要 DASHSCOPE_API_KEY

| 脚本 | 功能 | 参数 | 输出 |
|------|------|------|------|
| `photo_understand.py` | AI拍照理解 | `--prompt "提问内容"` | 问题: {prompt} / 回答: {AI回答} |
| `speech_recognition.py` | 语音识别 | `--seconds 3` | 识别结果: {文字} |
| `text_to_speech.py` | AI语音合成 | `--text "你好"` `--voice Cherry` | 语音播放（自然人声，需API） |
| `generate_image.py` | AI生成图片 | `--prompt "一只猫"` | 图片已保存: {path} |
| `goto_target.py` | AI走向目标 | `--target "黄色小鸡"` `--timeout 60` | ✓ 已到达目标 或 ✗ 未能到达 |

> **语音输出选择：** 机器狗说话优先用 `text_to_speech.py`

**photo_understand.py 常用 prompt 示例：**

| 任务 | prompt 示例 |
|------|-------------|
| 物体位置 | `--prompt "图中纸巾在什么位置？只回答：左边/中间/右边/没有"` |
| 物体列举 | `--prompt "图中有哪些物品？列出名称"` |
| 物体计数 | `--prompt "图中有几个苹果？只回答数字"` |
| 颜色判断 | `--prompt "图中最大的物体是什么颜色？"` |
| 场景理解 | `--prompt "这是什么地方？简要描述"` |
| 是非判断 | `--prompt "图中有人吗？只回答有/没有"` |
| 物体对比 | `--prompt "图中哪个物体更大？"` |

> API密钥通过环境变量 `DASHSCOPE_API_KEY` 自动读取，也可用 `--api-key` 参数覆盖

---

### Mini3W专用 (scripts/mini3w/)

| 脚本 | 功能 | 参数 |
|------|------|------|
| `enable_wheel.py` | 轮控开关 | `--mode 0` (0=启用, 1=禁用) |
| `wheel_control.py` | 轮控制 | `--w1 128` `--w2 128` `--w3 128` `--w4 128` |
| `extern_motor.py` | 外接电机 | `--position 100` |

---

### Rider专用 (scripts/rider/)

#### 运动控制
| 脚本 | 功能 | 参数 |
|------|------|------|
| `move.py` | 前后移动 | `--speed 0.5` `--runtime 3` |
| `turn.py` | 原地旋转 | `--speed 90` `--runtime 2` |
| `roll.py` | Roll姿态 | `--angle 10` |
| `height.py` | 身高调整 | `--height 90` |
| `reset.py` | 重置 | 无参数 |
| `reset_odom.py` | 重置里程计 | 无参数 |

#### 模式控制
| 脚本 | 功能 | 参数 |
|------|------|------|
| `action.py` | 预设动作 | `--id 1` (1-6/255) |
| `balance_roll.py` | Roll自平衡 | `--mode 1` (0=关, 1=开) |
| `perform.py` | 表演模式 | `--mode 1` (0=关, 1=开) |
| `calibration.py` | 软件标定 | `--state start/end` |

#### 周期运动
| 脚本 | 功能 | 参数 |
|------|------|------|
| `periodic_roll.py` | 周期Roll | `--period 1.5` `--duration 5` |
| `periodic_z.py` | 周期升降 | `--period 1.5` `--duration 5` |

#### 传感器与LED
| 脚本 | 功能 | 参数 |
|------|------|------|
| `battery.py` | 读取电量 | 无参数 |
| `read_roll.py` | 读取Roll | 无参数 |
| `read_pitch.py` | 读取Pitch | 无参数 |
| `read_yaw.py` | 读取Yaw | 无参数 |
| `led.py` | LED控制 | `--index 0` `--r 255` `--g 0` `--b 0` |

---

### 组合任务 (scripts/combo/)

| 脚本 | 功能 | 参数 |
|------|------|------|
| `ai_find_step.py` | AI智能踩物 | `--target "纸巾"` `--leg 1` (1=左前,2=右前) `--speed 100` (越小越机械) |
| `follow_face.py` | 人脸追踪 | 无参数，按C退出 |
| `follow_color.py` | 颜色追踪 | `--color R` (R/G/B/Y) |
| `gesture_control.py` | 手势控制 | 无参数，按C退出 |
| `line_follow.py` | 巡线行走 | `--color K` (K黑/W白) |
| `qr_patrol.py` | 二维码巡逻 | 无参数，按C退出 |

---

## Python 库参考（用于编写新代码）

**当预置脚本无法满足需求时，参考以下源码编写代码：**

| 模块 | 文件路径 | 功能说明 |
|------|----------|----------|
| **运动控制** | `lib/xgolib/xgolib_dog.py` | XGO_DOG 类：四足机器狗运动、姿态、机械臂控制 |
| **Rider控制** | `lib/xgolib/xgolib_rider.py` | XGO_RIDER 类：双轮足机器人专用 |
| **视觉传感器** | `lib/edulib.py` | XGOEDU 类：摄像头、屏幕、按键、各种识别功能 |

> 这些文件包含完整的方法签名、参数范围和注释，是最准确的 API 参考。

## 代码模板（必须遵循）

```python
import sys
sys.path.insert(0, '/home/pi/.npm-global/lib/node_modules/openclaw/skills/xgorobot/lib')
from xgolib import XGO       # 通用类，自动识别机型
from edulib import XGOEDU    # 视觉/屏幕/按键

# 初始化（不带参数，自动检测）
dog = XGO()
edu = XGOEDU()
```

> 重要：`sys.path.insert` 和 `XGO()` 不带参数是必须的，否则会出错或卡死

## 机型识别

XGO 类自动识别机型，无需手动指定：

```python
dog = XGO()  # 自动检测串口和机型
firmware = dog.read_firmware()  # 首字母: M=Mini, L=Lite, W=Mini3W, R=Rider
```

| 机型 | 特征 | 固件首字母 |
|------|------|----------|
| **XGO-Mini** | 12自由度，有机械臂 | M |
| **XGO-Lite** | 轻量版，无机械臂 | L |
| **XGO-Mini3W** | 支持轮控模式 | W |
| **XGO-Rider** | 双轮足，非四足 | R |

## 快速参考

### 运动控制 (XGO)

```python
dog = XGO()

# 基础运动
dog.forward(step)      # 前进 0-25
dog.back(step)         # 后退 0-25
dog.left(step)         # 左移 0-18
dog.right(step)        # 右移 0-18
dog.turnleft(step)     # 左转 0-100
dog.turnright(step)    # 右转 0-100
dog.stop()             # 停止

# 姿态控制
dog.translation('z', height)  # 身高 75-120mm
dog.attitude('r', angle)      # Roll 姿态
dog.attitude('p', angle)      # Pitch 姿态
dog.attitude('y', angle)      # Yaw 姿态

# 预设动作
dog.action(id)         # 执行预设动作 1-255
dog.reset()            # 恢复初始姿态

# 机械臂 (Mini/Mini3W)
dog.arm(x, z)          # 机械臂位置
dog.claw(pos)          # 夹爪开合 0-255

# 状态读取
dog.read_battery()     # 电量
dog.read_roll()        # Roll 角度
dog.read_pitch()       # Pitch 角度
dog.read_yaw()         # Yaw 角度
```

### 视觉传感器 (XGOEDU)

```python
edu = XGOEDU()

# 屏幕显示
edu.lcd_clear()                          # 清屏
edu.lcd_text(x, y, text, color, size)    # 显示文字
edu.lcd_picture(filename, x, y)          # 显示图片
edu.lcd_line(x1, y1, x2, y2, color)      # 画线
edu.lcd_rectangle(x1, y1, x2, y2)        # 画矩形

# 按键检测
edu.xgoButton("a")  # 左上 (True/False)
edu.xgoButton("b")  # 右上
edu.xgoButton("c")  # 左下 (常用作退出)
edu.xgoButton("d")  # 右下

# 摄像头
edu.xgoCamera(True/False)  # 开关摄像头预览
edu.xgoTakePhoto(filename) # 拍照

# 识别功能
edu.gestureRecognition()    # 手势识别 -> ('5', (x,y)) 或 None
edu.ColorRecognition(mode)  # 颜色识别 mode='R'/'G'/'B'/'Y' -> ((x,y), radius)
edu.LineRecognition(mode)   # 巡线 mode='K'(黑)/'W'(白) -> {'x':, 'angle':}
edu.QRRecognition()         # 二维码 -> ['内容1', '内容2'] 或 []
edu.AprilTagRecognition()   # AprilTag -> tag_id 或 None
edu.face_detect()           # 人脸检测 -> [x, y, w, h] 或 None
edu.emotion()               # 情绪识别 -> ('Happy', (x,y)) 或 None
edu.agesex()                # 年龄性别 -> ('Male', '(25-32)', (x,y)) 或 None
edu.yoloFast()              # 目标检测 -> ('person', (x,y)) 或 None
edu.posenetRecognition()    # 骨骼检测 -> [angle1, angle2, ...] 或 None
```

## 典型代码模板

### 基础控制

```python
import sys
sys.path.insert(0, '/home/pi/.npm-global/lib/node_modules/openclaw/skills/xgorobot/lib')
from xgolib import XGO
from edulib import XGOEDU
import time

dog = XGO()
edu = XGOEDU()

# 显示提示
edu.lcd_text(10, 100, "按C键退出", "YELLOW", 20)

# 主循环
while not edu.xgoButton("c"):
    # 你的控制逻辑
    time.sleep(0.1)

dog.stop()
dog.reset()
```

### 视觉追踪

```python
import sys
sys.path.insert(0, '/home/pi/.npm-global/lib/node_modules/openclaw/skills/xgorobot/lib')
from xgolib import XGO
from edulib import XGOEDU
import time

dog = XGO()
edu = XGOEDU()

while not edu.xgoButton("c"):
    result = edu.ColorRecognition(mode='R')  # 追踪红色
    (x, y), radius = result
    
    if radius > 10:  # 检测到目标
        error = x - 160  # 偏离中心
        if error > 30:
            dog.turnright(30)
        elif error < -30:
            dog.turnleft(30)
        else:
            dog.forward(10)
    else:
        dog.stop()
    
    time.sleep(0.1)

dog.stop()
```

### 巡线行走

```python
import sys
sys.path.insert(0, '/home/pi/.npm-global/lib/node_modules/openclaw/skills/xgorobot/lib')
from xgolib import XGO
from edulib import XGOEDU
import time

dog = XGO()
edu = XGOEDU()

while not edu.xgoButton("c"):
    result = edu.LineRecognition(mode='K')  # 黑线
    x = result['x']
    
    if x > 0:
        offset = x - 160
        if offset > 20:
            dog.turn(-20)
        elif offset < -20:
            dog.turn(20)
        else:
            dog.turn(0)
        dog.forward(10)
    else:
        dog.stop()
    
    time.sleep(0.05)

dog.stop()
```

## 注意事项

1. **API 细节**：完整参数和返回值请直接查看 `lib/` 下的源码文件
2. **串口独占**：XGO_DOG 占用串口，但可与 XGOEDU 同时使用
3. **初始化顺序**：建议先初始化 XGO_DOG，再初始化 XGOEDU
4. **摄像头资源**：视觉识别函数会自动管理摄像头
5. **按键退出**：用 `edu.xgoButton("c")` 作为程序退出条件

## 机型差异

| 功能 | Mini | Lite | Mini3W | Rider |
|------|:----:|:----:|:------:|:-----:|
| 机械臂 | ✓ | ✗ | ✓ | ✗ |
| 轮控模式 | ✗ | ✗ | ✓ | - |
| Y轴平移 | ✓ | ✓ | ✓ | ✗ |
| 四足行走 | ✓ | ✓ | ✓ | ✗ |

- **Lite**：无机械臂，调用 `arm()` 或 `claw()` 无效
- **Mini3W**：可用 `enable_wheel_control()` 切换轮控模式
- **Rider**：统一使用 `XGO()` 类，调用 `rider_*` 方法（如 `rider_move_x()`），无侧移功能


