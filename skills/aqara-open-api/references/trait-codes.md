# 功能点代码一览

下表汇总了 Aqara 支持的全部功能点代码（trait code）：

> 说明
> 
> 下表仅展示各功能点代码（trait code）的基本信息，包括类型、可读写、可上报等。若需了解每个 trait 的详细定义（如取值范围、枚举说明等），请通过接口 [GetDevicesRequest](./trait-api.mdx#查询设备的-spec-配置) 获取完整的配置信息。

| trait_code | trait_name(chinese) | trait_name(English) | 功能类型 | 单位 | 可读 | 可写 | 可上报 |
|---|---|---|---|---|---|---|---|
| CODetected | 一氧化碳检测状态 | Carbon Monoxide Detection State | boolean |  | ✔ | ✘ | ✔ |
| ExpressedState | 报警器状态 | Alarm Status | enum |  | ✔ | ✘ | ✔ |
| WindSetting | 风类型 | Wind Type | enum |  | ✔ | ✔ | ✔ |
| AirflowDirection | 风向 | Airflow Direction | enum |  | ✔ | ✔ | ✔ |
| FanSpeed | 风速 | Fan Speed | number | % | ✔ | ✔ | ✔ |
| AirQuality | 空气质量等级 | Air Quality Level | enum |  | ✔ | ✘ | ✔ |
| BooleanState | 布尔状态 | Boolean State | boolean |  | ✔ | ✘ | ✔ |
| MatterVendorID | Matter Vendor ID | Matter Vendor ID | string |  | ✔ | ✘ | ✔ |
| FreshAirMode | 新风模式 | Fresh Air Mode | enum |  | ✔ | ✔ | ✔ |
| InvertedRotationAngle | 倒置旋转角度 | Inverted Rotation Angle | number | ° | ✘ | ✘ | ✔ |
| ConnectionStatus | 连接状态 | Connection Status | enum |  | ✔ | ✘ | ✔ |
| ScreenBrightness | 屏幕亮度 | Screen Brightness | number | % | ✔ | ✔ | ✔ |
| TemperatureUIDisplayMode | 温度用户界面显示模式 | Temperature UI Display Mode | enum |  | ✔ | ✔ | ✔ |
| BatReplacementNeeded | 是否需要更换电池 | Battery Replacement Needed | boolean |  | ✔ | ✘ | ✔ |
| BatQuantity | 电池数量 | Battery Quantity | number |  | ✔ | ✘ | ✔ |
| Rechargeable | 是否可充电 | Rechargeable | boolean |  | ✔ | ✘ | ✔ |
| CircuitCurrent | 电路电流 | Circuit Current | number | A | ✔ | ✘ | ✔ |
| P2PCaptureEnabled | 是否支持P2P抓图 | P2P Capture Enabled | boolean |  | ✔ | ✔ | ✔ |
| MotorOperationStatus | 电机运行状态 | Motor Operation Status | enum |  | ✔ | ✘ | ✔ |
| MotorDirectionReversed | 电机方向反转 | Motor Direction Reversed | boolean |  | ✔ | ✔ | ✔ |
| MotorControllability | 电机是否可控制 | Motor Controllable | boolean |  | ✔ | ✘ | ✔ |
| CurrentValveState | 当前阀门状态 | Current Valve State | enum |  | ✔ | ✘ | ✔ |
| Condition | 滤芯剩余寿命 | Filter Remaining Life | number | % | ✔ | ✘ | ✔ |
| ChangeIndication | 滤芯寿命状态 | Filter Life Status | enum |  | ✔ | ✘ | ✔ |
| FilterType | 滤芯类型 | Filter Type | enum |  | ✔ | ✘ | ✔ |
| OperationalState | 设备状态 | Device Status | enum |  | ✔ | ✘ | ✔ |
| CurrentFlow | 当前流量 | Current Flow | number | m³/h | ✔ | ✘ | ✔ |
| CurrentMode | 当前模式 | Current Mode | enum |  | ✔ | ✘ | ✔ |
| ChangeToModeResponse | 模式切换反馈 | Change Mode Response | enum |  | ✔ | ✘ | ✔ |
| VacuumOperationalState | 扫地机器人状态 | Robot Vacuum State | enum |  | ✔ | ✘ | ✔ |
| RefrigeratorAlarm | 冰箱报警 | Refrigerator Alarm | other |  | ✔ | ✘ | ✔ |
| EvseState | 充电枪状态 | EVSE Gun State | enum |  | ✔ | ✘ | ✔ |
| EvseSupplyState | 充电桩状态 | EVSE Supply State | enum |  | ✔ | ✘ | ✔ |
| ChargingEnabledUntil | 允许继续充电时间 | Charging Allowed Until | number | A | ✔ | ✘ | ✔ |
| MaxChargeCurrent | 最大电流 | Max Charge Current | number | A | ✔ | ✘ | ✔ |
| BatteryCapacity | 电池容量 | Battery Capacity | number |  | ✔ | ✘ | ✔ |
| MinChargeCurrent | 最小电流 | Min Charge Current | number | A | ✔ | ✘ | ✔ |
| SetTemperature | 设置温度 | Set Temperature | number | °C | ✔ | ✔ | ✔ |
| SetTemperatureLevel | 设置温度等级 | Set Temperature Level | number |  | ✔ | ✔ | ✔ |
| MediaInput | 播放源 | Media Source | enum |  | ✔ | ✔ | ✔ |
| SetBack | 温度浮动 | Temperature Offset | number | °C | ✔ | ✔ | ✔ |
| OpenAngle | 开合角度 | Opening Angle | number |  | ✔ | ✘ | ✔ |
| BSSID | BSSID | BSSID | string |  | ✔ | ✘ | ✔ |
| CurrentTemperatureCalibration | 温度补偿 | Temperature Calibration | number | °C | ✔ | ✔ | ✔ |
| HeaterCoolerButtonEvent | 温控按键事件 | Thermostat Button Event | enum |  | ✔ | ✘ | ✔ |
| HeaterCoolerPolarity | 温控器极性设置 | Thermostat Polarity Setting | enum |  | ✔ | ✔ | ✔ |
| SelfCheck | 报警器自检 | Alarm Self-Check | boolean |  | ✔ | ✔ | ✔ |
| FirmwareRevision | 固件版本 | Firmware Version | string |  | ✔ | ✘ | ✔ |
| SerialNumber | 序列号 | Serial Number | string |  | ✔ | ✘ | ✔ |
| VendorName | 厂商名 | Vendor Name | string |  | ✔ | ✘ | ✔ |
| VendorID | 厂商ID | Vendor ID | string |  | ✔ | ✘ | ✔ |
| ProductName | 产品名称 | Product Name | string |  | ✔ | ✘ | ✔ |
| Reachable | 连接状态 | Connection Status | boolean |  | ✔ | ✘ | ✔ |
| HardwareVersion | 硬件版本 | Hardware Version | string |  | ✔ | ✘ | ✔ |
| Mac | Mac地址 | MAC Address | string |  | ✔ | ✘ | ✔ |
| DeviceID | 设备ID | Device ID | string |  | ✔ | ✘ | ✔ |
| EndpointName | 设备或卡片名称 | Device or Card Name | string |  | ✔ | ✔ | ✔ |
| OnOff | 开关状态 | On / Off State | boolean |  | ✔ | ✔ | ✔ |
| CurrentLevel | 当前等级 | Current Level | number | % | ✔ | ✔ | ✔ |
| CurrentX | X值 | X Value | number |  | ✔ | ✔ | ✔ |
| CurrentY | Y值 | Y Value | number |  | ✔ | ✔ | ✔ |
| ColorTemperature | 色温值 | Color Temperature | number |  | ✔ | ✔ | ✔ |
| ButtonEvent | 按钮事件 | Button Event | enum |  | ✘ | ✘ | ✔ |
| CameraActiveStatus | 摄像头休眠状态 | Camera Sleep Status | boolean |  | ✔ | ✔ | ✔ |
| CurrentPositionPercentage | 当前位置百分比 | Current Position Percentage | number | % | ✔ | ✘ | ✔ |
| TargetPositionPercentage | 目标位置百分比 | Target Position Percentage | number | % | ✘ | ✔ | ✔ |
| IRType | 红外类型 | IR Type | enum |  | ✔ | ✔ | ✔ |
| IRBrand | 红外品牌 | IR Brand | number |  | ✔ | ✔ | ✔ |
| CurrentVoltage | 电压值 | Voltage Value | number | V | ✔ | ✘ | ✔ |
| CurrentPower | 功率值 | Power Value | number | W | ✔ | ✘ | ✔ |
| CumulativeEnergyConsumption | 累计耗电量 | Cumulative Energy Consumption | number | W·h | ✔ | ✘ | ✔ |
| HeaterCoolerMode | 制热制冷模式 | Heat/Cool Mode | enum |  | ✔ | ✔ | ✔ |
| HeatingTemperature | 制热温度 | Heating Temperature | number | °C | ✔ | ✔ | ✔ |
| CoolingTemperature | 制冷温度 | Cooling Temperature | number | °C | ✔ | ✔ | ✔ |
| FanMode | 风扇模式 | Fan Mode | enum |  | ✔ | ✔ | ✔ |
| RockSetting | 摆风 | Swing Mode | enum |  | ✔ | ✔ | ✔ |
| CurrentHumidity | 湿度 | Humidity | number | % | ✔ | ✘ | ✔ |
| CurrentPlaybackState | 播放状态 | Playback State | enum |  | ✔ | ✘ | ✔ |
| PlaybackDuration | 时长 | Duration | number | ms | ✔ | ✘ | ✔ |
| SampledPosition | 播放进度 | Playback Progress | number | ms | ✔ | ✘ | ✔ |
| PlaybackMode | 播放模式 | Playback Mode | enum |  | ✔ | ✔ | ✔ |
| MediaInformation | 媒体信息 | Media Information | string |  | ✔ | ✘ | ✔ |
| Volume | 音量 | Volume | number | % | ✔ | ✔ | ✔ |
| Mute | 静音 | Mute | boolean |  | ✔ | ✔ | ✔ |
| LockState | 锁状态 | Lock Status | enum |  | ✔ | ✘ | ✔ |
| DoorState | 门状态 | Door Status | enum |  | ✔ | ✘ | ✔ |
| IRKey | 红外指令 | IR Command | enum |  | ✘ | ✔ | ✘ |
| BatPercentRemaining | 电量百分比 | Battery Percentage Remaining | number | % | ✔ | ✘ | ✔ |
| SweeperState | 扫地状态 | Sweeper State | enum |  | ✔ | ✘ | ✔ |
| VOCDensity | VOC浓度 | VOC Concentration | number | ppb | ✔ | ✘ | ✔ |
| VOCQuality | VOC等级 | VOC Level | enum |  | ✔ | ✘ | ✔ |
| CurrentPressure | 压力 | Pressure | number | kPa | ✔ | ✘ | ✔ |
| PM2.5Density | PM2.5浓度 | PM2.5 Concentration | number | ug/m³ | ✔ | ✘ | ✔ |
| PM2.5Level | PM2.5等级 | PM2.5 Level | enum |  | ✔ | ✘ | ✔ |
| PM1.0Density | PM1.0浓度 | PM1.0 Concentration | number | ug/m³ | ✔ | ✘ | ✔ |
| PM10Density | PM10浓度 | PM10 Concentration | number | ug/m³ | ✔ | ✘ | ✔ |
| CO2Density | CO2浓度 | CO2 Concentration | number | ppm | ✔ | ✘ | ✔ |
| CO2Level | CO2等级 | CO2 Level | enum |  | ✔ | ✘ | ✔ |
| CurrentIlluminance | 光照度 | Illuminance | number | lux | ✔ | ✘ | ✔ |
| ContactSensorState | 接触状态 | Contact State | boolean |  | ✔ | ✘ | ✔ |
| SmokeDensity | 烟雾浓度 | Smoke Concentration | number | OBS%/FT | ✔ | ✘ | ✔ |
| SmokeDetected | 烟雾检测状态 | Smoke Detection State | boolean |  | ✔ | ✘ | ✔ |
| GasDensity | 气体浓度 | Gas Concentration | number | %LEL | ✔ | ✘ | ✔ |
| GasDetected | 气体检测状态 | Gas Detection State | boolean |  | ✔ | ✘ | ✔ |
| SleepState | 睡眠状态 | Sleep State | enum |  | ✔ | ✘ | ✔ |
| SleepQuality | 睡眠质量 | Sleep Quality | number |  | ✔ | ✘ | ✔ |
| OnBed | 在床状态 | On Bed State | boolean |  | ✔ | ✘ | ✔ |
| SleepStage | 睡眠阶段 | Sleep Stage | enum |  | ✔ | ✘ | ✔ |
| LeakState | 泄漏状态 | Leak State | boolean |  | ✔ | ✘ | ✔ |
| Occupancy | 存在状态 | Occupancy State | boolean |  | ✔ | ✘ | ✔ |
| OccupancySensorType | 存在传感类型 | Occupancy Sensor Type | enum |  | ✔ | ✘ | ✔ |
| MotionDetected | 移动侦测 | Motion Detection | enum |  | ✘ | ✘ | ✔ |
| RotationAngle | 旋转角度 | Rotation Angle | number |  | ✘ | ✘ | ✔ |
| RotationDirection | 旋转方向 | Rotation Direction | enum |  | ✘ | ✘ | ✔ |
| RotationEvent | 旋转事件 | Rotation Event | enum |  | ✘ | ✘ | ✔ |
| CubeEvent | 魔方事件 | Cube Event | enum |  | ✘ | ✘ | ✔ |
| VibrationEvent | 动静贴事件 | Vibration Event | enum |  | ✘ | ✘ | ✔ |
| SmokeDensitydB | 烟雾浓度dB | Smoke Concentration (dB) | number | dB/m | ✔ | ✘ | ✔ |
| CurrentR | 红色值 | Red Value | number |  | ✔ | ✔ | ✔ |
| CurrentG | 绿色值 | Green Value | number |  | ✔ | ✔ | ✔ |
| CurrentB | 蓝色值 | Blue Value | number |  | ✔ | ✔ | ✔ |
| EndpointArrayDynamic | 节点动态数组 | Dynamic Endpoint Array | other |  | ✔ | ✘ | ✔ |
| Feed | 喂食 | Feeding | enum |  | ✔ | ✘ | ✔ |
| AttitudeDetected | 姿态检测 | Posture Detection | enum |  | ✔ | ✘ | ✔ |
| TargetPlaybackState | 目标播放状态 | Target Playback State | enum |  | ✔ | ✔ | ✔ |
| EnableRemoteControl | 远程控制使能 | Remote Control Enabled | boolean |  | ✔ | ✔ | ✔ |
| HardwareVersionString | 硬件版本号（字符串类型） | Hardware Version (string) | string |  | ✔ | ✘ | ✔ |
| FirmwareRevisionString | 固件版本号（字符串类型） | Firmware Version (string) | string |  | ✔ | ✘ | ✔ |
| ProductID | 产品ID | Product ID | number |  | ✔ | ✘ | ✔ |
| MinPINCodeLength | 最小PINCode长度 | Minimum PINCode Length | number |  | ✔ | ✘ | ✔ |
| MinRFIDCodeLength | 最小RFID长度 | Minimum RFID Length | number |  | ✔ | ✘ | ✔ |
| OperatingMode | 操作模式 | Operating Mode | enum |  | ✔ | ✘ | ✔ |
| ActuatorEnabled | 执行器启用 | Actuator Enabled | boolean |  | ✔ | ✘ | ✔ |
| ReverseIdentify | 反向识别 | Reverse Identify | number |  | ✘ | ✘ | ✔ |
| Hue | Hue | Hue | number | ° | ✔ | ✔ | ✔ |
| Saturation | 饱和度 | Saturation | number | % | ✔ | ✔ | ✔ |
| MinHeatCoolDeadBand | 制冷制热温度最小死区 | Min Heat/Cool Deadband | number | °C | ✔ | ✔ | ✔ |
| Channel | 无线信道 | Wireless Channel | number |  | ✔ | ✘ | ✔ |
| ExtendedPANID | 网络ExtendedPANID | Network ExtendedPANID | number |  | ✔ | ✘ | ✔ |
| WindowCoveringMotorsBinding | 窗帘电机绑定为统一总控 | Curtain Motors Unified Control | boolean |  | ✔ | ✔ | ✔ |
| CurrentRotationAngle | 窗帘的当前旋转角度 | Current Curtain Rotation Angle | number | ° | ✔ | ✘ | ✔ |
| TargetRotationAngle | 窗帘的目标旋转角度 | Target Curtain Rotation Angle | number | ° | ✔ | ✔ | ✔ |
| CurrentGarageDoorState | 当前（车库）门状态 | Current Garage Door State | enum |  | ✔ | ✘ | ✔ |
| TargetGarageDoorState | 目标（车库）门状态 | Target Garage Door State | enum |  | ✔ | ✔ | ✔ |
| HoldRotationAngle | 按住旋转角度 | Hold Rotation Angle | number | ° | ✘ | ✘ | ✔ |
| ModeCount | 模式数量 | Mode Count | number |  | ✔ | ✘ | ✔ |
| PlaybackSampledPosition | 当前媒体播放位置 | Current Media Playback Position | number | ms | ✔ | ✔ | ✔ |
| SelectedMediaOutputSource | 当前播放输出源 | Current Media Output Source | enum |  | ✔ | ✔ | ✔ |
| LockOperation | 门锁操作（事件）上报 | Lock Operation (Event) Report | other |  | ✘ | ✘ | ✔ |
| DoorLockAlarm | 门锁报警（事件）上报 | Door Lock Alarm (Event) Report | other |  | ✘ | ✘ | ✔ |
| LockUserChange | 门锁用户变更上报 | Lock User Change Report | other |  | ✘ | ✘ | ✔ |
| ModelValue | 模型值 | Model Value | string |  | ✔ | ✘ | ✔ |

