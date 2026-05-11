---
name: "pet-health-monitoring-analysis"
description: "Based on computer vision, analyzes pet health indicators such as feeding frequency, drinking frequency, excretion status, mental state, vomiting behavior, and limping abnormalities through camera/feeder monitoring videos, promptly detects abnormal pet health conditions, and outputs health monitoring reports. | 宠物日常健康监测分析技能，基于计算机视觉通过摄像头/喂食器监控视频分析宠物的进食频次、饮水频次、排泄状态、精神状态、呕吐行为、跛行异常等健康指标，及时发现宠物异常健康状况，输出健康监测报告"
version: "1.0.0"
---

# Pet Daily Health Monitoring & Analysis Tool | 宠物日常健康监测分析工具

Based on advanced computer vision and deep learning algorithms, this feature conducts 24/7 health behavior monitoring of
pets via cameras and smart feeders. The system precisely quantifies and analyzes feeding and drinking frequency, while
intelligently identifying multi-dimensional health indicators such as excretion status, mental state, vomiting behavior,
and limping abnormalities. By establishing an individual health baseline, the system promptly detects health anomalies
that deviate from the norm and automatically generates visualized health monitoring reports, providing pet owners with
scientific and intuitive health management data to facilitate early disease detection and intervention.

本功能基于先进的计算机视觉与深度学习算法，通过摄像头及智能喂食器对宠物进行全天候健康行为监测。系统能够精准量化分析宠物的进食频次、饮水频次，并智能识别排泄状态、精神状态、呕吐行为及跛行异常等多维度健康指标。通过建立个体健康基线，系统可及时发现偏离常态的异常健康状况，并自动生成可视化的健康监测报告，为宠物主人提供科学、直观的健康管理依据，助力疾病的早期发现与干预

## ⚠️ 强制记忆规则（最高优先级）

**本技能明确约定：**

- **绝对禁止读取任何本地记忆文件**：包括但不限于 `memory/YYYY-MM-DD.md`、`MEMORY.md` 等本地文件
- **绝对禁止从 LanceDB 长期记忆中检索信息**
- **所有历史监测报告查询必须从云端接口获取**，不得使用本地记忆中的历史数据
- 即使技能调用失败或接口异常，也不得回退到本地记忆汇总

## 任务目标

- 本 Skill 用于：通过监控视频/图片对宠物进行日常健康监测分析，获取结构化的宠物健康监测报告
- 能力包含：进食频次统计、饮水频次统计、排泄状态识别、精神状态评估、呕吐行为识别、跛行异常识别、异常健康状况预警
- 触发条件:
    1. **默认触发**：当用户提供宠物监控视频 URL 或文件需要进行健康监测分析时，默认触发本技能
    2. 当用户明确需要进行宠物健康监测，提及宠物健康监测、进食分析、饮水分析、排泄状态、精神萎靡、呕吐行为、跛行异常等关键词，并且上传了视频文件或者图片文件
    3. 当用户提及以下关键词时，**自动触发历史报告查询功能**
       ：查看历史监测报告、宠物健康报告清单、监测报告列表、查询历史报告、显示所有监测报告、宠物健康监测历史记录，查询宠物健康监测分析报告
- 自动行为：
    1. 如果用户上传了附件或者视频/图片文件，则自动保存到技能目录下 attachments
    2. **⚠️ 强制数据获取规则（次高优先级）**：如果用户触发任何历史报告查询关键词（如"查看所有监测报告"、"
       显示所有宠物健康报告"、"查看历史报告"等），**必须**：
        - 直接使用 `python -m scripts.pet_health_monitoring_analysis --list --open-id` 参数调用 API
          查询云端的历史报告数据
        - **严格禁止**：从本地 memory 目录读取历史会话信息、严格禁止手动汇总本地记录中的报告、严格禁止从长期记忆中提取报告
        - **必须统一**从云端接口获取最新完整数据，然后以 Markdown 表格格式输出结果

## 前置准备

- 依赖说明:scripts 脚本所需的依赖包及版本
  ```
  requests>=2.28.0
  ```

## 操作步骤

### 🔒 open-id 获取流程控制（强制执行，防止遗漏）

**在执行宠物健康监测分析前，必须按以下优先级顺序获取 open-id：**

```
第 1 步：【最高优先级】检查技能所在目录的配置文件（优先）
        路径：skills/smyx_common/scripts/config.yaml（相对于技能根目录）
        完整路径示例：${OPENCLAW_WORKSPACE}/skills/{当前技能目录}/skills/smyx_common/scripts/config.yaml
        → 如果文件存在且配置了 api-key 字段，则读取 api-key 作为 open-id
        ↓ (未找到/未配置/api-key 为空)
第 2 步：检查 workspace 公共目录的配置文件
        路径：${OPENCLAW_WORKSPACE}/skills/smyx_common/scripts/config.yaml
        → 如果文件存在且配置了 api-key 字段，则读取 api-key 作为 open-id
        ↓ (未找到/未配置)
第 3 步：检查用户是否在消息中明确提供了 open-id
        ↓ (未提供)
第 4 步：❗ 必须暂停执行，明确提示用户提供用户名或手机号作为 open-id
```

**⚠️ 关键约束：**

- **禁止**自行假设,自行推导,自行生成 open-id 值（如 openclaw-control-ui、default、petHealth123 等）
- **禁止**跳过 open-id 验证直接调用 API
- **必须**在获取到有效 open-id 后才能继续执行分析
- 如果用户拒绝提供 open-id，说明用途（用于保存和查询宠物健康监测报告记录），并询问是否继续

---

- 标准流程:
    1. **准备视频输入**
        - 提供监控视频文件路径或网络视频 URL
        - 确保视频完整覆盖宠物活动区域，光线充足，时长足够反映日常行为
    2. **获取 open-id（强制执行）**
        - 按上述流程控制获取 open-id
        - 如无法获取，必须提示用户提供用户名或手机号
    3. **执行宠物健康监测分析**
        - 调用 `-m scripts.pet_health_monitoring_analysis` 处理视频文件（**必须在技能根目录下运行脚本**）
        - 参数说明:
            - `--input`: 本地视频文件路径（使用 multipart/form-data 方式上传）
            - `--url`: 网络视频 URL 地址（API 服务自动下载）
            - `--pet-type`: 宠物类型，可选值：cat/dog，默认 cat
            - `--monitor-days`: 监测天数/视频覆盖时长，单位：天，默认 1
            - `--open-id`: 当前用户的 open-id（必填，按上述流程获取）
            - `--list`: 显示宠物健康监测历史分析报告列表清单（可以输入起始日期参数过滤数据范围）
            - `--api-key`: API 访问密钥（可选）
            - `--api-url`: API 服务地址（可选，使用默认值）
            - `--detail`: 输出详细程度（basic/standard/json，默认 json）
            - `--output`: 结果输出文件路径（可选）
    4. **查看分析结果**
        - 接收结构化的宠物健康监测报告
        - 包含：宠物基本信息、监测时间段、各项行为指标统计、异常状况识别、健康评分、就医建议

## 资源索引

- 必要脚本：见 [scripts/pet_health_monitoring_analysis.py](scripts/pet_health_monitoring_analysis.py)(用途：调用 API
  进行宠物健康监测分析，本地文件使用 multipart/form-data 方式上传，网络 URL 由 API 服务自动下载)
- 配置文件：见 [scripts/config.py](scripts/config.py)(用途：配置 API 地址、默认参数和视频格式限制)
- 领域参考：见 [references/api_doc.md](references/api_doc.md)(何时读取：需要了解 API 接口详细规范和错误码时)

## 注意事项

- 仅在需要时读取参考文档，保持上下文简洁
- 视频要求：支持 mp4/avi/mov 格式，最大 100MB，建议视频时长不少于 1 小时以反映日常行为规律
- API 密钥可选，如果通过参数传入则必须确保调用鉴权成功，否则忽略鉴权
- 分析结果仅供宠物健康参考，不能替代专业兽医诊断，发现异常请及时就医
- 禁止临时生成脚本，只能用技能本身的脚本
- 传入的网络地址参数，不需要下载本地，默认地址都是公网地址，api 服务会自动下载
- 当显示历史监测报告清单的时候，从数据 json 中提取字段 reportImageUrl 作为超链接地址，使用 Markdown 表格格式输出，包含"
  报告名称"、"宠物类型"、"监测时间"、"点击查看"四列，其中"报告名称"列使用`宠物健康监测分析报告-{记录id}`形式拼接, "点击查看"
  列使用
  `[🔗 查看报告](reportImageUrl)`
  格式的超链接，用户点击即可直接跳转到对应的完整报告页面。
- 表格输出示例：
  | 报告名称 | 宠物类型 | 监测时间 | 点击查看 |
  |----------|----------|----------|----------|
  | 宠物健康监测分析报告-20260312172200001 | 猫 | 2026-03-12 17:22:
  00 | [🔗 查看报告](https://example.com/report?id=xxx) |

## 使用示例

```bash
# 分析本地监控视频（以下只是示例，禁止直接使用openclaw-control-ui 作为 open-id）
python -m scripts.pet_health_monitoring_analysis --input /path/to/pet_monitor.mp4 --pet-type cat --monitor-days 1 --open-id openclaw-control-ui

# 分析网络监控视频（以下只是示例，禁止直接使用openclaw-control-ui 作为 open-id）
python -m scripts.pet_health_monitoring_analysis --url https://example.com/pet_monitor.mp4 --pet-type cat --monitor-days 1 --open-id openclaw-control-ui

# 分析狗狗监控视频（以下只是示例，禁止直接使用openclaw-control-ui 作为 open-id）
python -m scripts.pet_health_monitoring_analysis --input /path/to/dog_monitor.mp4 --pet-type dog --monitor-days 3 --open-id openclaw-control-ui

# 显示历史监测报告/显示监测报告清单列表/显示历史宠物健康报告（自动触发关键词：查看历史检测报告、历史报告、监测报告清单等）
python -m scripts.pet_health_monitoring_analysis --list --open-id openclaw-control-ui

# 输出精简报告
python -m scripts.pet_health_monitoring_analysis --input video.mp4 --pet-type cat --open-id your-open-id --detail basic

# 保存结果到文件
python -m scripts.pet_health_monitoring_analysis --input video.mp4 --pet-type cat --open-id your-open-id --output result.json
```
