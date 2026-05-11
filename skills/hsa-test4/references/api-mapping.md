# 萤石设备配置 API 映射表

根据用户提供的 9 个接口文档整理 (2026-03-13 核实)：

| 文档 ID | 功能 | 配置类型 | API 路径 | 参数 |
|---------|------|----------|----------|------|
| 701 | 设置布撤防 | `defence_set` | `/api/lapp/device/defence/set` | isDefence: 0/1/8/16 |
| 702 | 获取布撤防时间计划 | `defence_plan_get` | `/api/lapp/device/defence/plan/get` | channelNo(可选) |
| 703 | 设置布撤防计划 | `defence_plan_set` | `/api/lapp/device/defence/plan/set` | startTime, stopTime, period, enable |
| 706 | 获取镜头遮蔽开关状态 | `shelter_get` | `/api/lapp/device/scene/switch/status` | - |
| 707 | 设置镜头遮蔽开关 | `shelter_set` | `/api/lapp/device/scene/switch/set` | enable: 0/1, channelNo(可选) |
| 712 | 获取全天录像开关状态 | `fullday_record_get` | `/api/lapp/device/fullday/record/switch/status` | - |
| 713 | 设置全天录像开关状态 | `fullday_record_set` | `/api/lapp/device/fullday/record/switch/set` | enable: 0/1 |
| 714 | 获取移动侦测灵敏度配置 | `motion_detect_sensitivity_get` | `/api/lapp/device/algorithm/config/get` | - |
| 715 | 设置移动侦测灵敏度配置 | `motion_detect_sensitivity_set` | `/api/lapp/device/algorithm/config/set` | type=0, value: 0-6 |

**Note**: 移动跟踪功能 (722/723) 已移除，因为该功能需要设备支持 `support_intelligent_track=1`，大多数设备不支持。

## 参数说明

### 通用参数
- `accessToken`: 访问令牌
- `deviceSerial`: 设备序列号（大写）
- `channelNo`: 通道号（可选，默认 1）

### 布防状态值 (isDefence)
- `0`: 撤防/睡眠
- `1`: 布防 (普通 IPC)
- `8`: 在家模式 (智能设备)
- `16`: 外出模式 (智能设备)

### 开关值 (enable)
- `0`: 关闭
- `1`: 开启

### 布防计划参数 (defence_plan_set)
- `startTime`: 开始时间 (格式：HH:mm，如 23:20)
- `stopTime`: 结束时间 (格式：HH:mm，如 23:21，n00:00 表示第二天 0 点)
- `period`: 周期 (周一~周日，用 0~6 表示，逗号分隔，如 "0,1,6")
- `enable`: 是否启用 (1-启用，0-不启用)

### 移动侦测灵敏度 (motion_detect_sensitivity_set)
- `sensitivity`: 0-9 (0 最低，9 最高)
