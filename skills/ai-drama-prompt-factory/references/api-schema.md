# API 输出 Schema

## 文件结构

```
output/
├── project-manifest.json           # 项目级：角色库+场景库+道具库+风格
├── ep01-prompt-package.json        # 第1集完整提示词包
├── ep02-prompt-package.json        # 第2集
└── ...
```

---

## project-manifest.json

项目初始化时生成，角色/场景/道具增删时增量更新。

```json
{
  "$schema": "drama-manifest-v1",
  "project": {
    "title": "项目名称",
    "source_title": "原著名称",
    "genre": "都市逆袭",
    "era": "现代",
    "total_episodes": 20,
    "target_ratio": "9:16"
  },
  "style": {
    "type": "电影写实",
    "character_suffix": "电影写实风格，高质量，真实光影，电影级打光，8K分辨率，超高清细节",
    "scene_suffix": "电影写实风格",
    "storyboard_suffix": "写实风格，电影级打光，8K分辨率，超细节刻画"
  },
  "characters": {
    "陈易": {
      "gender": "男",
      "age": 24,
      "variants": {
        "觉醒前": {
          "prompt": "现代、24岁、男、短发凌乱/黑色、蓝白条纹病号服、病号裤、无、面色苍白，电影写实风格，高质量，真实光影，电影级打光，8K分辨率，超高清细节，全身，纯色背景，面向镜头",
          "desc": "病号服，虚弱苍白"
        },
        "觉醒后": {
          "prompt": "现代、24岁、男、短发利落/黑色、灰色运动外套、深蓝色运动裤、白色运动鞋、无配饰，电影写实风格，高质量，真实光影，电影级打光，8K分辨率，超高清细节，全身，纯色背景，面向镜头",
          "desc": "运动装，精神焕发"
        }
      }
    },
    "张慧芬": {
      "gender": "女",
      "age": 48,
      "variants": {
        "默认": {
          "prompt": "现代、48岁、女、短发烫卷/深棕色、浅蓝色护士上衣、白色裤子、白色护士鞋、无配饰、面容疲惫但温和，电影写实风格，高质量，真实光影，电影级打光，8K分辨率，超高清细节，全身，纯色背景，面向镜头",
          "desc": "护士装"
        }
      }
    }
  },
  "scenes": {
    "医院普通病房": {
      "variants": {
        "白天": {
          "prompt": "中国现代，电影写实风格，室内，白天，现代医院普通病房，白色墙面干净整洁，输液架立在病床旁，病床白色床单，窗户透入柔和自然光"
        },
        "深夜": {
          "prompt": "中国现代，电影写实风格，室内，深夜，现代医院普通病房，白色墙面，走廊灯光透过门缝微弱照入，氛围安静压抑"
        }
      }
    }
  },
  "props": {
    "天机古卷": {
      "prompt": "中国古代，电影写实风格，信物，泛黄卷边的线装书，封面为深蓝色布面，边角磨损严重，书页间夹有干枯的银杏叶书签，是主角被雷劈时的护身符，纸质（泛黄），封面深蓝色布面，书签枯黄色"
    }
  }
}
```

---

## ep{N}-prompt-package.json

单集完整提示词包。每个 shot 包含三个核心字段：`storyboard_prompt`（分镜图片）、`video_prompt`（视频）、`audio_spec`（音频）。

```json
{
  "$schema": "drama-prompt-package-v1",
  "episode": {
    "number": 1,
    "title": "天降奇才",
    "shot_count": 15,
    "characters_used": ["陈易", "张慧芬", "陈勇"],
    "scenes_used": ["医院普通病房"]
  },
  "shots": [
    {
      "shot_id": "ep01_sh01",
      "shot_number": 1,
      "duration": "5s",
      "script": {
        "characters": [
          { "name": "陈勇", "variant": "默认" },
          { "name": "张慧芬", "variant": "默认" },
          { "name": "陈易", "variant": "觉醒前" }
        ],
        "scene": "医院普通病房",
        "scene_variant": "白天",
        "shot_type": "近景",
        "action": "画面右侧陈勇背影离去，张慧芬转身替病床上的陈易整理输液管，轻叹气",
        "dialogue": {
          "speaker": "张慧芬",
          "text": "唉，陈易，你的医药费已经拖欠三天了...",
          "emotion": "无奈叹息"
        },
        "source_anchor": "P-003"
      },

      "storyboard_prompt": "中国现代，医院普通病房，白色墙面，输液架，病床，柔和冷光，近景镜头（胸部以上），画面右侧陈勇背影离去，张慧芬转身替病床上的陈易（觉醒前）整理输液管，轻叹气，眼神略带无奈，写实风格，电影级打光，8K分辨率，超细节刻画",

      "video_prompt": "场景为中国现代医院普通病房，白色墙面干净整洁，输液架立在病床旁，柔和冷光洒满房间。镜头从张慧芬(女)的近景开始，她站在病床边，目光望向画面右侧，陈勇(男)的背影正缓缓走出病房门口，写实风格，电影级打光。切镜到张慧芬(女)的近景（胸部以上），她收回目光转身面向病床上的陈易，双手轻柔整理输液管，轻叹气，嘴唇微动说着：\"唉，陈易，你的医药费已经拖欠三天了...\"，眼神略带无奈，超细节刻画手部动作，8K分辨率。最后切镜到两人同框的中景，张慧芬(女)整理好输液管后低头看着陈易，病房里安静无声，氛围忧虑而沉重，无背景音乐。陈勇是男性，张慧芬是女性",

      "audio_spec": {
        "dialogue": {
          "text": "唉，陈易，你的医药费已经拖欠三天了...",
          "speaker": "张慧芬",
          "speaker_gender": "female",
          "emotion": "无奈叹息",
          "voice_desc": "中年女性，声音疲惫温和，带叹息感，语速缓慢"
        },
        "sfx": [
          { "type": "脚步声远去", "timing": "陈勇离开时", "volume": "低" },
          { "type": "输液管碰撞", "timing": "张慧芬整理时", "volume": "轻微" }
        ],
        "bgm": { "mood": "无", "note": "无背景音乐，安静压抑" }
      }
    },

    {
      "shot_id": "ep01_sh08",
      "shot_number": 8,
      "duration": "5s",
      "script": {
        "characters": [
          { "name": "林峰", "variant": "觉醒后" }
        ],
        "scene": "世界杯决赛球场",
        "scene_variant": "比赛中",
        "shot_type": "近景",
        "action": "林峰双手快速结印，张嘴向场内大吼，额头青筋暴起",
        "dialogue": {
          "speaker": "林峰",
          "text": "赵小天！坎位七步，转身盲传！",
          "emotion": "激动狂热"
        },
        "source_anchor": "P-042"
      },

      "storyboard_prompt": "中国现代，世界杯决赛球场，绿茵草地背景，球场灯光璀璨，观众席人山人海虚化，近景镜头，林峰（觉醒后），双手快速结印，张嘴向场内大吼，额头青筋暴起，眼神犀利望向球场中央，神情激动狂热，汗水飞溅，动态模糊感，高对比度光影，电影级质感，8K超高清，日系动漫风格，唯美画风",

      "video_prompt": "场景为中国现代的世界杯决赛球场，绿茵草地在璀璨灯光下格外耀眼，背景中虚化的人山人海观众席沸腾喧嚣。镜头从林峰的中景开始，他觉醒后的神情狂热，猛地冲到球场边线，带起一阵破空呼啸声，汗水在剧烈运动中飞溅。切镜到林峰的面部特写，额头青筋暴起，眼神犀利如电死死盯着球场中央，双手快速结印，张嘴向场内大吼：\"赵小天！坎位七步，转身盲传！\"最后切镜到球场内视角的远景，林峰的身影在场边显得极具爆发力，高对比度光影下，整个画面充满紧张激烈的决战氛围。",

      "audio_spec": {
        "dialogue": {
          "text": "赵小天！坎位七步，转身盲传！",
          "speaker": "林峰",
          "speaker_gender": "male",
          "emotion": "激动狂热",
          "voice_desc": "青年男性，嘶吼式呐喊，爆发力极强，带破音感"
        },
        "sfx": [
          { "type": "观众欢呼", "timing": "全程背景", "volume": "中" },
          { "type": "破空呼啸", "timing": "林峰冲到边线时", "volume": "强" }
        ],
        "bgm": { "mood": "紧张激烈", "note": "快节奏电子鼓点，渐强到高潮" }
      }
    }
  ],

  "diagnosis": {
    "score": 87,
    "passed": true
  },

  "continuity": {
    "character_states": {
      "陈易": { "variant_at_end": "觉醒前", "location": "医院病房" },
      "林峰": { "variant_at_end": "觉醒后", "location": "球场" }
    },
    "next_episode_hook": "陈易在病床上突然睁开双眼，瞳孔中闪过金色光芒"
  }
}
```

---

## 字段说明

### shot 核心三字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `storyboard_prompt` | string | 分镜图片提示词。角色用名字引用。用于生成静态画面。 |
| `video_prompt` | string | 视频提示词。基于 storyboard_prompt 派生。包含动态描述+切镜+对白+性别。 |
| `audio_spec` | object | 音频描述。对白+音效+BGM。 |

### storyboard_prompt → video_prompt 的关系

```
storyboard_prompt: 静态画面描述
  → 角色用名字 → 生成工具匹配角色立绘 → 输出分镜图片

video_prompt: 动态叙事（基于 storyboard_prompt 派生）
  → 场景扩写 + 动作展开 + 切镜 + 对白 + 性别
  → 输入分镜图片 + video_prompt → 生成视频

两者的场景和角色必须完全对应。
```

---

## 外部消费示例

```python
import json

# 1. 加载项目清单
manifest = json.load(open("project-manifest.json"))

# 2. 生成角色参考图（项目初始化）
for name, char in manifest["characters"].items():
    for variant, data in char["variants"].items():
        img = generate_image(prompt=data["prompt"])
        register_character(name=f"{name}（{variant}）", image=img)

# 3. 生成场景参考图
for name, scene in manifest["scenes"].items():
    for variant, data in scene["variants"].items():
        img = generate_image(prompt=data["prompt"])
        register_scene(name=f"{name}_{variant}", image=img)

# 4. 生成道具参考图
for name, prop in manifest["props"].items():
    img = generate_image(prompt=prop["prompt"])
    register_prop(name=name, image=img)

# 5. 逐集逐镜头生成
package = json.load(open("ep01-prompt-package.json"))

for shot in package["shots"]:
    # 5a. 用分镜提示词生成图片
    #     提示词中的角色名字会匹配到已注册的角色参考图
    storyboard_img = generate_image(
        prompt=shot["storyboard_prompt"],
        character_refs=get_refs(shot["script"]["characters"])
    )
    
    # 5b. 用分镜图片 + 视频提示词生成视频
    #     分镜图片作为首帧，视频提示词指导动态展开
    video = generate_video(
        first_frame=storyboard_img,
        prompt=shot["video_prompt"]
    )
    
    # 5c. 生成对白音频
    if shot["audio_spec"]["dialogue"]:
        d = shot["audio_spec"]["dialogue"]
        audio = generate_tts(
            text=d["text"],
            voice_desc=d["voice_desc"],
            emotion=d["emotion"]
        )
    
    # 5d. 合成
    final = compose(video, audio, shot["audio_spec"]["sfx"], shot["audio_spec"]["bgm"])
```
