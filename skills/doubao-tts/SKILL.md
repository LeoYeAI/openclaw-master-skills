---
name: doubao-tts
description: 使用豆包（火山引擎）语音合成大模型 API 将文本转换为语音音频文件。支持声音复刻音色（S_ 开头的音色ID）和官方预置音色。当用户要求"语音合成"、"文字转语音"、"TTS"、"朗读文本"、"生成语音"、"用我的声音读"、"豆包语音"、"声音复刻合成"等相关请求时，务必使用此 skill。即使用户只是说"帮我把这段话读出来"或"生成一段音频"，也应触发此 skill。
credentials:
  required:
    - name: DOUBAO_APP_ID
      description: 火山引擎控制台获取的 APP ID，用于调用豆包 TTS 云端 API 的身份标识
    - name: DOUBAO_ACCESS_KEY
      description: 火山引擎控制台获取的 Access Token，用于调用豆包 TTS 云端 API 的鉴权密钥
  optional:
    - name: DOUBAO_SPEAKER
      description: 音色 ID，默认为 zh_female_xiaohe_uranus_bigtts（小何 2.0，通用中文女声）
---

# 豆包语音合成 Skill（Doubao TTS）

本 skill 通过火山引擎豆包语音合成大模型的**单向流式 HTTP V3 接口**，将文本合成为语音音频文件。

官方文档：[豆包语音合成 API 文档](https://www.volcengine.com/docs/6561/1598757?lang=zh)

## 前置要求

用户需要提供以下环境变量（通过 `export` 设置或在脚本参数中传入）：

- `DOUBAO_APP_ID`：火山引擎控制台获取的 APP ID
- `DOUBAO_ACCESS_KEY`：火山引擎控制台获取的 Access Token
- `DOUBAO_SPEAKER`：音色 ID（可选，默认为 `zh_female_xiaohe_uranus_bigtts`）
  - 声音复刻音色以 `S_` 开头，可前往官方后台创建：[音色复刻控制台](https://console.volcengine.com/speech/new/experience/clone?projectName=default)
  - 官方预置音色详见下方音色对照表

如果用户没有设置 `DOUBAO_APP_ID` 和 `DOUBAO_ACCESS_KEY`，**先提醒用户设置**，并告知获取方式：登录火山引擎控制台 → 豆包语音 → 创建应用 → 获取 APP ID 和 Access Token。

如果用户未设置 `DOUBAO_SPEAKER`，默认使用 `zh_female_xiaohe_uranus_bigtts`（小何 2.0，通用中文女声）。

## 使用流程

### 1. 确认参数

向用户确认以下信息（有合理默认值的可以跳过确认）：

| 参数 | 说明 | 默认值 |
|------|------|--------|
| 待合成文本 | 要转语音的文字内容 | （必填） |
| 音色 ID（speaker） | 音色标识符。声音复刻音色以 `S_` 开头；根据上下文从下方音色表中选择合适音色 | `$DOUBAO_SPEAKER` 或 `zh_female_xiaohe_uranus_bigtts` |
| 资源 ID（resource_id） | 声音复刻用 `seed-icl-1.0`；官方 1.0 音色用 `seed-tts-1.0`；官方 2.0 音色用 `seed-tts-2.0` | `seed-tts-2.0` |
| 音频格式（format） | `mp3` / `ogg_opus` / `pcm` | `mp3` |
| 采样率（sample_rate） | 可选 8000/16000/22050/24000/32000/44100/48000 | `24000` |
| 情感（emotion） | 情感类型，仅多情感音色支持。中文音色：`happy` / `sad` / `angry` / `surprised` / `fear` / `hate` / `excited` / `coldness` / `neutral` 等；英文音色：`neutral` / `happy` / `angry` / `sad` / `excited` / `chat` / `warm` 等 | 不设置 |
| 情绪强度（emotion_scale） | 范围 1~5，值越大情感越明显（非线性），需配合 `emotion` 使用 | `4` |
| 输出文件名 | 生成的音频文件名 | `output.mp3` |

### 2. 执行合成

运行脚本：

```bash
# 基础用法（resource-id 自动推断）
python3 /path/to/doubao-tts/scripts/tts_synthesize.py \
  --text "要合成的文本" \
  --speaker "${DOUBAO_SPEAKER:-zh_female_xiaohe_uranus_bigtts}" \
  --format mp3 \
  --sample-rate 24000 \
  --output /mnt/user-data/outputs/output.mp3

# 带情感的合成（仅多情感音色支持）
python3 /path/to/doubao-tts/scripts/tts_synthesize.py \
  --text "要合成的文本" \
  --speaker "zh_female_shuangkuaisisi_emo_v2_mars_bigtts" \
  --emotion happy \
  --emotion-scale 4 \
  --output /mnt/user-data/outputs/output.mp3
```

环境变量 `DOUBAO_APP_ID` 和 `DOUBAO_ACCESS_KEY` 必须已设置。也可以通过 `--app-id` 和 `--access-key` 参数直接传入。

### 3. 输出结果

脚本会将合成的音频保存到指定路径。合成完成后，使用 `present_files` 工具将文件呈现给用户。

## 音色对照表

Agent 应根据上下文（用户要求的角色、场景、风格）从下表中选择最合适的音色 ID。

> 完整音色列表参见官方文档：[音色列表](https://www.volcengine.com/docs/6561/1257544?lang=zh)

### 豆包语音合成 2.0 音色（推荐，resource_id 使用 `seed-tts-2.0`）

| 场景 | 音色名称 | voice_type（音色ID） | 语种 | 适用角色/描述 |
|------|---------|---------------------|------|--------------|
| 通用场景 | 小何 2.0 ⭐默认 | `zh_female_xiaohe_uranus_bigtts` | 中文 | 通用女声，自然亲切 |
| 通用场景 | Vivi 2.0 | `zh_female_vv_uranus_bigtts` | 中文/日文/印尼语/西班牙语 | 多语种女声，情感丰富 |
| 通用场景 | 云舟 2.0 | `zh_male_m191_uranus_bigtts` | 中文 | 通用男声 |
| 通用场景 | 小天 2.0 | `zh_male_taocheng_uranus_bigtts` | 中文 | 通用男声，年轻 |
| 通用场景 | 刘飞 2.0 | `zh_male_liufei_uranus_bigtts` | 中文 | 通用男声 |
| 通用场景 | 魅力苏菲 2.0 | `zh_male_sophie_uranus_bigtts` | 中文 | 通用男声 |
| 通用场景 | 清新女声 2.0 | `zh_female_qingxinnvsheng_uranus_bigtts` | 中文 | 清新淡雅女声 |
| 通用场景 | 甜美小源 2.0 | `zh_female_tianmeixiaoyuan_uranus_bigtts` | 中文 | 甜美女声 |
| 通用场景 | 甜美桃子 2.0 | `zh_female_tianmeitaozi_uranus_bigtts` | 中文 | 甜美女声 |
| 通用场景 | 爽快思思 2.0 | `zh_female_shuangkuaisisi_uranus_bigtts` | 中文 | 爽朗活泼女声 |
| 通用场景 | 邻家女孩 2.0 | `zh_female_linjianvhai_uranus_bigtts` | 中文 | 亲切邻家风格女声 |
| 通用场景 | 少年梓辛 2.0 | `zh_male_shaonianzixin_uranus_bigtts` | 中文 | 少年男声，青春感 |
| 通用场景 | 魅力女友 2.0 | `zh_female_meilinvyou_uranus_bigtts` | 中文 | 魅力成熟女声 |
| 通用场景 | 流畅女声 2.0 | `zh_female_liuchangnv_uranus_bigtts` | 中文 | 流畅自然女声，适合长文朗读 |
| 通用场景 | 儒雅逸辰 2.0 | `zh_male_ruyayichen_uranus_bigtts` | 中文 | 儒雅成熟男声 |
| 角色扮演 | 知性灿灿 2.0 | `zh_female_cancan_uranus_bigtts` | 中文 | 知性干练女声 |
| 角色扮演 | 撒娇学妹 2.0 | `zh_female_sajiaoxuemei_uranus_bigtts` | 中文 | 撒娇可爱女声 |
| 视频配音 | 猴哥 2.0 | `zh_male_sunwukong_uranus_bigtts` | 中文 | 孙悟空角色，豪迈 |
| 视频配音 | 佩奇猪 2.0 | `zh_female_peiqi_uranus_bigtts` | 中文 | 卡通儿童角色 |
| 视频配音 | 大壹 2.0 | `zh_male_dayi_uranus_bigtts` | 中文 | 视频配音男声 |
| 视频配音 | 黑猫侦探社咪仔 2.0 | `zh_female_mizai_uranus_bigtts` | 中文 | 可爱卡通女声 |
| 视频配音 | 鸡汤女 2.0 | `zh_female_jitangnv_uranus_bigtts` | 中文 | 温情励志女声 |
| 教育场景 | Tina老师 2.0 | `zh_female_yingyujiaoxue_uranus_bigtts` | 中文/英式英语 | 教师/教育场景 |
| 客服场景 | 暖阳女声 2.0 | `zh_female_kefunvsheng_uranus_bigtts` | 中文 | 客服专用，温暖专业 |
| 有声阅读 | 儿童绘本 2.0 | `zh_female_xiaoxue_uranus_bigtts` | 中文 | 儿童故事、绘本朗读 |
| 多语种 | Tim | `en_male_tim_uranus_bigtts` | 美式英语 | 英文男声 |
| 多语种 | Dacey | `en_female_dacey_uranus_bigtts` | 美式英语 | 英文女声 |
| 多语种 | Stokie | `en_female_stokie_uranus_bigtts` | 美式英语 | 英文女声 |

### 豆包语音合成 1.0 音色（resource_id 使用 `seed-tts-1.0`）

#### 通用场景

| 场景 | 音色名称 | voice_type（音色ID） | 语种 | 适用角色/描述 |
|------|---------|---------------------|------|--------------|
| 通用 | 灿灿/Shiny | `zh_female_cancan_mars_bigtts` | 中文/美式英语 | 活泼开朗女声 |
| 通用 | Vivi | `zh_female_vv_mars_bigtts` | 中文 | 标准女声 |
| 通用 | 爽快思思/Skye | `zh_female_shuangkuaisisi_moon_bigtts` | 中文/美式英语 | 爽朗活泼女声 |
| 通用 | 温暖阿虎/Alvin | `zh_male_wennuanahu_moon_bigtts` | 中文/美式英语 | 温暖亲切男声 |
| 通用 | 少年梓辛/Brayan | `zh_male_shaonianzixin_moon_bigtts` | 中文/美式英语 | 青春少年男声 |
| 通用 | 清新女声 | `zh_female_qingxinnvsheng_mars_bigtts` | 中文 | 清新淡雅 |
| 通用 | 知性女声 | `zh_female_zhixingnvsheng_mars_bigtts` | 中文 | 知性成熟女声 |
| 通用 | 清爽男大 | `zh_male_qingshuangnanda_mars_bigtts` | 中文 | 清爽大学生男声 |
| 通用 | 邻家女孩 | `zh_female_linjianvhai_moon_bigtts` | 中文 | 亲切邻家风 |
| 通用 | 渊博小叔 | `zh_male_yuanboxiaoshu_moon_bigtts` | 中文 | 知识渊博叔叔感 |
| 通用 | 阳光青年 | `zh_male_yangguangqingnian_moon_bigtts` | 中文 | 积极阳光男声 |
| 通用 | 甜美小源 | `zh_female_tianmeixiaoyuan_moon_bigtts` | 中文 | 甜美女声 |
| 通用 | 甜美悦悦 | `zh_female_tianmeiyueyue_moon_bigtts` | 中文 | 甜美女声 |
| 通用 | 清澈梓梓 | `zh_female_qingchezizi_moon_bigtts` | 中文 | 清澈干净女声 |
| 通用 | 开朗姐姐 | `zh_female_kailangjiejie_moon_bigtts` | 中文 | 开朗大姐姐 |
| 通用 | 邻家男孩 | `zh_male_linjiananhai_moon_bigtts` | 中文 | 亲切邻家男声 |
| 通用 | 心灵鸡汤 | `zh_female_xinlingjitang_moon_bigtts` | 中文 | 温情励志女声 |
| 通用 | 快乐小东 | `zh_male_xudong_conversation_wvae_bigtts` | 中文 | 对话场景男声 |
| 通用 | 亲切女声 | `zh_female_qinqienvsheng_moon_bigtts` | 中文 | 亲切温和女声 |
| 教育 | Tina老师 | `zh_female_yingyujiaoyu_mars_bigtts` | 中文/英式英语 | 教学场景 |

#### 多情感音色（支持 emotion 参数）

| 音色名称 | voice_type（音色ID） | 支持的情感 | 适用场景 |
|---------|---------------------|-----------|---------|
| 爽快思思（多情感） | `zh_female_shuangkuaisisi_emo_v2_mars_bigtts` | 开心/悲伤/生气/惊讶/激动/冷漠/中性 | 情感丰富的对话、故事 |
| 柔美女友（多情感） | `zh_female_roumeinvyou_emo_v2_mars_bigtts` | 开心/悲伤/生气/惊讶/恐惧/厌恶/激动/冷漠/中性 | 情感丰富女声 |
| 高冷御姐（多情感） | `zh_female_gaolengyujie_emo_v2_mars_bigtts` | 开心/悲伤/生气/惊讶/恐惧/厌恶/激动/冷漠/中性 | 御姐/高冷女性角色 |
| 冷酷哥哥（多情感） | `zh_male_lengkugege_emo_v2_mars_bigtts` | 生气/冷漠/恐惧/开心/厌恶/中性/悲伤/沮丧 | 冷酷/高冷男性角色 |
| 傲娇霸总（多情感） | `zh_male_aojiaobazong_emo_v2_mars_bigtts` | 中性/开心/愤怒/厌恶 | 霸道总裁、强势男性 |
| 儒雅男友（多情感） | `zh_male_ruyayichen_emo_v2_mars_bigtts` | 开心/悲伤/生气/恐惧/激动/冷漠/中性 | 温文尔雅男友 |
| 俊朗男友（多情感） | `zh_male_junlangnanyou_emo_v2_mars_bigtts` | 开心/悲伤/生气/惊讶/恐惧/中性 | 帅气男友 |
| 阳光青年（多情感） | `zh_male_yangguangqingnian_emo_v2_mars_bigtts` | 开心/悲伤/生气/恐惧/激动/冷漠/中性 | 阳光积极青年 |
| 优柔公子（多情感） | `zh_male_yourougongzi_emo_v2_mars_bigtts` | 开心/生气/恐惧/厌恶/激动/中性/沮丧 | 温柔优雅男性 |
| 北京小爷（多情感） | `zh_male_beijingxiaoye_emo_v2_mars_bigtts` | 生气/惊讶/恐惧/激动/冷漠/中性 | 北京腔调男声 |
| 广州德哥（多情感） | `zh_male_guangzhoudege_emo_mars_bigtts` | 生气/恐惧/中性 | 广州方言男声 |
| 京腔侃爷（多情感） | `zh_male_jingqiangkanye_emo_mars_bigtts` | 开心/生气/惊讶/厌恶/中性 | 京腔侃爷风格 |
| 甜心小美（多情感） | `zh_female_tianxinxiaomei_emo_v2_mars_bigtts` | 悲伤/恐惧/厌恶/中性 | 甜美女声 |
| 邻居阿姨（多情感） | `zh_female_linjuayi_emo_v2_mars_bigtts` | 中性/愤怒/冷漠/沮丧/惊讶 | 中年女性 |
| 深夜播客（多情感） | `zh_male_shenyeboke_emo_v2_mars_bigtts` | 惊讶/悲伤/中性/厌恶/开心/恐惧/激动/沮丧/冷漠/生气 | 深夜播客/电台 |
| Candice | `en_female_candice_emo_v2_mars_bigtts` | 深情/愤怒/ASMR/对话/兴奋/愉悦/中性/温暖 | 英文女声 |
| Serena | `en_female_skye_emo_v2_mars_bigtts` | 深情/愤怒/ASMR/对话/兴奋/愉悦/中性/悲伤/温暖 | 英文女声 |
| Glen | `en_male_glen_emo_v2_mars_bigtts` | 深情/愤怒/ASMR/对话/兴奋/愉悦/中性/悲伤/温暖 | 英文男声 |
| Sylus | `en_male_sylus_emo_v2_mars_bigtts` | 深情/愤怒/ASMR/权威/对话/兴奋/愉悦/中性/悲伤/温暖 | 英文男声 |
| Corey | `en_male_corey_emo_v2_mars_bigtts` | 愤怒/ASMR/权威/对话/深情/兴奋/愉悦/中性/悲伤/温暖 | 英式英语男声 |
| Nadia | `en_female_nadia_tips_emo_v2_mars_bigtts` | 深情/愤怒/ASMR/对话/兴奋/愉悦/中性/悲伤/温暖 | 英式英语女声 |

#### 趣味口音

| 音色名称 | voice_type（音色ID） | 口音/语种 | 描述 |
|---------|---------------------|----------|------|
| 湾湾小何 | `zh_female_wanwanxiaohe_moon_bigtts` | 台湾普通话 | 台湾腔女声 |
| 京腔侃爷/Harmony | `zh_male_jingqiangkanye_moon_bigtts` | 北京口音 | 北京腔侃爷 |
| 北京小爷 | `zh_male_beijingxiaoye_moon_bigtts` | 北京口音 | 北京腔男声 |
| 呆萌川妹 | `zh_female_daimengchuanmei_moon_bigtts` | 四川口音 | 川味女声 |
| 豫州子轩 | `zh_male_yuzhouzixuan_moon_bigtts` | 河南口音 | 河南腔男声 |
| 广西远舟 | `zh_male_guangxiyuanzhou_moon_bigtts` | 广西口音 | 广西腔男声 |
| 广州德哥 | `zh_male_guozhoudege_moon_bigtts` | 广东口音 | 广东腔男声 |
| 湾区大叔 | `zh_female_wanqudashu_moon_bigtts` | 广东口音 | 广东腔 |
| 浩宇小哥 | `zh_male_haoyuxiaoge_moon_bigtts` | 青岛口音 | 青岛腔男声 |
| 妹坨洁儿 | `zh_female_meituojieer_moon_bigtts` | 长沙口音 | 长沙腔女声 |
| 粤语小溏 | `zh_female_yueyunv_mars_bigtts` | 粤语 | 粤语女声 |

#### 角色扮演

| 音色名称 | voice_type（音色ID） | 角色特征 |
|---------|---------------------|---------|
| 奶气萌娃 | `zh_male_naiqimengwa_mars_bigtts` | 萌娃、儿童角色 |
| 婆婆 | `zh_female_popo_mars_bigtts` | 老年女性、祖母 |
| 高冷御姐 | `zh_female_gaolengyujie_moon_bigtts` | 高冷御姐风格 |
| 傲娇霸总 | `zh_male_aojiaobazong_moon_bigtts` | 霸道总裁、傲娇男 |
| 魅力女友 | `zh_female_meilinvyou_moon_bigtts` | 魅力女友 |
| 柔美女友 | `zh_female_sajiaonvyou_moon_bigtts` | 柔美撒娇女友 |
| 撒娇学妹 | `zh_female_yuanqinvyou_moon_bigtts` | 撒娇可爱学妹 |
| 东方浩然 | `zh_male_dongfanghaoran_moon_bigtts` | 正义男主角 |
| 深夜播客 | `zh_male_shenyeboke_moon_bigtts` | 深夜电台主播 |

#### IP 仿音

| 音色名称 | voice_type（音色ID） | 角色/原型 |
|---------|---------------------|---------|
| 猪八戒 | `zh_male_zhubajie_mars_bigtts` | 西游记猪八戒 |
| 唐僧 | `zh_male_tangseng_mars_bigtts` | 西游记唐僧 |
| 鲁班七号 | `zh_male_lubanqihao_mars_bigtts` | 王者荣耀鲁班七号 |
| 春日部姐姐 | `zh_female_jiyejizi2_mars_bigtts` | 哆啦A梦角色 |
| 女雷神 | `zh_female_leidian_mars_bigtts` | 雷神角色 |
| 庄周 | `zh_male_zhuangzhou_mars_bigtts` | 王者荣耀庄周 |

### Agent 音色选择指南

根据上下文智能选择音色：

| 使用场景 | 推荐音色 | 音色ID |
|---------|---------|--------|
| 默认/通用 | 小何 2.0 | `zh_female_xiaohe_uranus_bigtts` |
| 正式/新闻播报 | 知性女声 | `zh_female_zhixingnvsheng_mars_bigtts` |
| 儿童故事/绘本 | 儿童绘本 2.0 | `zh_female_xiaoxue_uranus_bigtts` |
| 英语内容 | Dacey | `en_female_dacey_uranus_bigtts` |
| 深夜/电台/播客 | 深夜播客（多情感） | `zh_male_shenyeboke_emo_v2_mars_bigtts` |
| 有声书/长文朗读 | 流畅女声 2.0 | `zh_female_liuchangnv_uranus_bigtts` |
| 客服/助手 | 暖阳女声 2.0 | `zh_female_kefunvsheng_uranus_bigtts` |
| 教育/教学 | Tina老师 2.0 | `zh_female_yingyujiaoxue_uranus_bigtts` |
| 台湾腔 | 湾湾小何 | `zh_female_wanwanxiaohe_moon_bigtts` |
| 北京腔 | 京腔侃爷 | `zh_male_jingqiangkanye_moon_bigtts` |
| 古风/武侠角色 | 东方浩然 | `zh_male_dongfanghaoran_moon_bigtts` |
| 霸道总裁 | 傲娇霸总 | `zh_male_aojiaobazong_moon_bigtts` |
| 可爱萌娃 | 奶气萌娃 | `zh_male_naiqimengwa_mars_bigtts` |
| 情感化对话 | 爽快思思（多情感） | `zh_female_shuangkuaisisi_emo_v2_mars_bigtts` |
| 用户自定义复刻声音 | 用户提供的 S_ 音色 | `S_xxxxxxxx`（用户声音复刻ID） |

## 重要注意事项

- **声音复刻音色**（S_ 开头）必须使用 `seed-icl-1.0` 作为 resource_id，不能用 `seed-tts-1.0` 或 `seed-tts-2.0`
- **2.0 音色**（uranus 系列）必须使用 `seed-tts-2.0`，不支持旧版 V1 接口
- **1.0 音色**（mars/moon 系列）使用 `seed-tts-1.0`
- 如果用户提供的文本非常长（超过 5000 字），建议分段合成后拼接
- 脚本使用 `requests.Session` 实现连接复用，符合官方最佳实践
- 流式接口返回的音频数据是 base64 编码的，脚本会自动解码拼接
- 如果用户要求调整语速、音量、音调等，可传入对应参数

## 错误处理

- `40402003`：文本超长，需要分段
- `40000001`：参数错误，检查音色 ID 和 resource_id 是否匹配
- `40300001`：鉴权失败，检查 APP ID 和 Access Key
- 出现 quota 相关错误：试用版用量已用完，需开通正式版
