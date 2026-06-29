# doubao-tts

> 豆包语音合成 Agent Skill —— 让 AI Agent 开口说话

[![ClawHub](https://img.shields.io/badge/ClawHub-doubao--tts-blue)](https://clawhub.ai/jianjun156/doubao-tts)
[![GitHub](https://img.shields.io/badge/GitHub-jianjun156%2Fdoubao--tts-181717?logo=github)](https://github.com/jianjun156/doubao-tts)

基于火山引擎**豆包语音合成大模型**的 Agent Skill，供 [OpenClaw](https://openclaw.ai) 等 AI Agent 框架调用。支持 100+ 官方预置音色、声音复刻、多情感控制，一行命令即可将文本转为高质量语音。

---

## 功能特性

- **开箱即用**：配置好环境变量即可直接调用，无需额外开发
- **100+ 官方音色**：涵盖通用、客服、有声书、角色扮演、趣味口音等多种场景
- **声音复刻**：支持 `S_` 开头的个人复刻音色，让 Agent 用你的声音说话
- **多情感控制**：支持 `happy` / `sad` / `angry` 等 20+ 种情感，可调节情绪强度
- **智能默认值**：`resource_id` 根据音色 ID 自动推断，无需手动指定
- **Agent 友好**：内置音色对照表，Agent 可根据上下文自动选择最合适的音色

---

## 快速开始

### 1. 通过 ClawHub 安装（推荐）

访问 [clawhub.ai/jianjun156/doubao-tts](https://clawhub.ai/jianjun156/doubao-tts)，一键安装到你的 OpenClaw 环境。

### 2. 手动安装

```bash
# 克隆仓库
git clone https://github.com/jianjun156/doubao-tts.git

# 安装依赖
pip install requests
```

### 3. 配置环境变量

登录 [火山引擎控制台](https://console.volcengine.com/speech) → 豆包语音 → 应用管理，获取 APP ID 和 Access Token。

```bash
export DOUBAO_APP_ID="your_app_id"
export DOUBAO_ACCESS_KEY="your_access_key"

# 可选：指定默认音色（不设置则使用小何 2.0）
export DOUBAO_SPEAKER="zh_female_xiaohe_uranus_bigtts"
```

### 4. 测试运行

```bash
python3 scripts/tts_synthesize.py \
  --text "你好，我是豆包语音合成" \
  --output output.mp3
```

---

## 环境变量

| 变量名 | 必填 | 说明 |
|--------|------|------|
| `DOUBAO_APP_ID` | ✅ | 火山引擎控制台的 APP ID |
| `DOUBAO_ACCESS_KEY` | ✅ | 火山引擎控制台的 Access Token |
| `DOUBAO_SPEAKER` | ❌ | 默认音色 ID，未设置时使用 `zh_female_xiaohe_uranus_bigtts` |

> **声音复刻**：前往 [音色复刻控制台](https://console.volcengine.com/speech/new/experience/clone?projectName=default) 创建个人音色，获取 `S_` 开头的音色 ID 后设置为 `DOUBAO_SPEAKER`。

---

## 脚本参数

```
python3 scripts/tts_synthesize.py [选项]

必填:
  --text TEXT               待合成的文本内容

音色参数:
  --speaker SPEAKER         音色 ID（默认读取 DOUBAO_SPEAKER 环境变量）
  --resource-id ID          资源 ID（默认根据音色自动推断）

音频参数:
  --format {mp3,ogg_opus,pcm}   音频格式（默认: mp3）
  --sample-rate RATE            采样率（默认: 24000）
  --speech-rate N               语速 [-50, 100]（默认: 0）
  --loudness-rate N             音量 [-50, 100]（默认: 0）
  --pitch N                     音调 [-12, 12]（默认: 0）

情感参数:
  --emotion EMOTION         情感类型，如 happy/sad/angry（仅部分音色支持）
  --emotion-scale N         情绪强度 [1-5]，默认 4，需配合 --emotion 使用

输出:
  --output PATH             输出文件路径（默认: output.mp3）

认证（可通过环境变量替代）:
  --app-id ID               APP ID
  --access-key KEY          Access Key
```

---

## 使用示例

```bash
# 使用默认音色合成
python3 scripts/tts_synthesize.py --text "欢迎使用豆包语音合成"

# 指定音色（2.0 大模型音色，自动推断 resource-id）
python3 scripts/tts_synthesize.py \
  --text "今天天气真不错" \
  --speaker zh_female_shuangkuaisisi_uranus_bigtts

# 使用个人复刻音色（自动使用 seed-icl-1.0）
python3 scripts/tts_synthesize.py \
  --text "这是我的声音" \
  --speaker S_xxxxxxxx

# 带情感合成（愤怒，强度 5）
python3 scripts/tts_synthesize.py \
  --text "你怎么能这样！" \
  --speaker zh_female_shuangkuaisisi_emo_v2_mars_bigtts \
  --emotion angry \
  --emotion-scale 5

# 指定输出格式和路径
python3 scripts/tts_synthesize.py \
  --text "Hello, world!" \
  --speaker en_female_dacey_uranus_bigtts \
  --format mp3 \
  --output /tmp/hello.mp3
```

---

## 音色推荐

| 场景 | 音色名称 | 音色 ID |
|------|---------|--------|
| 通用（默认）| 小何 2.0 | `zh_female_xiaohe_uranus_bigtts` |
| 通用女声 | 爽快思思 2.0 | `zh_female_shuangkuaisisi_uranus_bigtts` |
| 通用男声 | 云舟 2.0 | `zh_male_m191_uranus_bigtts` |
| 英语 | Dacey | `en_female_dacey_uranus_bigtts` |
| 有声书 | 流畅女声 2.0 | `zh_female_liuchangnv_uranus_bigtts` |
| 儿童故事 | 儿童绘本 2.0 | `zh_female_xiaoxue_uranus_bigtts` |
| 客服 | 暖阳女声 2.0 | `zh_female_kefunvsheng_uranus_bigtts` |
| 情感丰富 | 爽快思思（多情感）| `zh_female_shuangkuaisisi_emo_v2_mars_bigtts` |
| 霸道总裁 | 傲娇霸总 | `zh_male_aojiaobazong_moon_bigtts` |
| 台湾腔 | 湾湾小何 | `zh_female_wanwanxiaohe_moon_bigtts` |

完整音色对照表见 [SKILL.md](./SKILL.md) 或 [官方音色列表](https://www.volcengine.com/docs/6561/1257544?lang=zh)。

---

## 支持的情感

多情感音色支持通过 `--emotion` 参数控制（不同音色支持范围不同）：

| 参数值 | 含义 |
|--------|------|
| `happy` | 开心 |
| `sad` | 悲伤 |
| `angry` | 生气 |
| `surprised` | 惊讶 |
| `fear` | 恐惧 |
| `hate` | 厌恶 |
| `excited` | 激动 |
| `coldness` | 冷漠 |
| `neutral` | 中性 |

---

## 官方文档

- [API 接口文档](https://www.volcengine.com/docs/6561/1598757?lang=zh)
- [音色列表](https://www.volcengine.com/docs/6561/1257544?lang=zh)
- [火山引擎控制台](https://console.volcengine.com/speech)
- [音色复刻](https://console.volcengine.com/speech/new/experience/clone?projectName=default)

---

## License

MIT
