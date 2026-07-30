---
name: story-music
description: 辅助讲故事和放音乐的技能。用于生成故事内容、选择背景音乐、调整音量、控制播放顺序，以及为故事添加语音旁白。使用场景包括：睡前故事、儿童故事、小说朗读、戏剧表演、播客制作等。
---

# 故事音乐技能

辅助创建故事内容并配合背景音乐播放的工具。

## 核心功能

### 1. 故事生成

提供各种类型的故事生成功能。

**支持的故事类型：**
- 睡前故事 - 轻柔、平静、适合放松
- 儿童故事 - 富有想象力、简单易懂
- 奇幻故事 - 冒险、魔法、奇幻元素
- 科幻故事 - 未来科技、太空探索
- 悬疑故事 - 谜题、推理、紧张氛围
- 历史故事 - 时代背景、人文历史
- 成长故事 - 青春、励志、人生感悟

### 2. 音乐选择与播放

为故事选择合适的背景音乐。

**音乐分类：**
- 轻松舒缓 - 适合放松、日常背景
- 欢快活泼 - 适合儿童、积极主题
- 悲伤感人 - 适合情感故事、回忆
- 紧张刺激 - 适合悬疑、冒险
- 神秘奇幻 - 适合魔法、超自然主题
- 古典优雅 - 适合历史、正式场合
- 现代流行 - 适合现代、青春主题

**音乐控制：**
- 播放/暂停
- 音量调节 (0-100%)
- 切换歌曲
- 循环播放
- 随机播放

### 3. 语音旁白

生成故事语音旁白文本。

**功能：**
- 根据故事内容生成旁白脚本
- 调整语速 (正常/慢速/极慢)
- 调整音调 (柔和/标准/戏剧)
- 分段朗读

## 快速开始

### 基础故事生成

```python
# 生成一个睡前故事
story = generate_story(
    genre="bedtime",
    character="小兔子",
    setting="森林",
    duration="5分钟"
)

print(story.content)
# 输出：故事内容...
```

### 添加背景音乐

```python
# 选择适合的音乐
music = select_music(
    mood="relaxing",
    genre="instrumental",
    tempo="slow"
)

# 播放音乐
play_music(music)
```

### 完整故事播放

```python
# 创建完整的故事体验
story_experience = StoryExperience(
    title="小兔子的森林冒险",
    content=story.content,
    music=music,
    narration_speed="slow",
    narration_tone="gentle"
)

# 播放
story_experience.play()

# 停止
story_experience.stop()
```

## 音乐素材

### 默认音乐库

| 风格 | 文件名 | 时长 | 适用场景 |
|------|--------|------|----------|
| 轻松舒缓 | relaxing.mp3 | 3:45 | 睡前、放松 |
| 欢快活泼 | cheerful.mp3 | 2:30 | 儿童、日常 |
| 悲伤感人 | emotional.mp3 | 4:12 | 情感故事 |
| 紧张刺激 | intense.mp3 | 3:00 | 悬疑、冒险 |
| 神秘奇幻 | magical.mp3 | 3:50 | 魔法、超自然 |
| 古典优雅 | classical.mp3 | 5:00 | 历史、正式 |
| 现代流行 | pop.mp3 | 3:20 | 现代、青春 |

### 添加自定义音乐

1. 将音乐文件放入 `assets/music/` 目录
2. 在代码中引用：

```python
from assets.music import track_list

# 添加到音乐库
track_list.append({
    'name': '我的故事音乐',
    'file': 'my_story_music.mp3',
    'mood': 'happy',
    'duration': 3:30
})
```

## 语音功能

### 使用TTS生成语音

```python
from tts import text_to_speech

# 生成旁白语音
audio = text_to_speech(
    text=story.narration,
    voice='gentle',
    speed=0.8,  # 80% 正常速度
    pitch='lower'
)

# 播放语音
play_audio(audio)
```

### 语音控制

**语音风格选项：**
- `gentle` - 柔和（适合睡前）
- `warm` - 温暖（适合情感故事）
- `energetic` - 活力（适合儿童）
- `dramatic` - 戏剧（适合冒险）
- `calm` - 平静（适合放松）

**语速选项：**
- `normal` - 正常 (100%)
- `slow` - 慢速 (80%)
- `very_slow` - 极慢 (60%)
- `fast` - 快速 (120%)

## 故事模板

### 睡前故事模板

```python
bedtime_story = {
    'title': '睡梦之旅',
    'characters': ['小星星', '云朵'],
    'setting': '夜空',
    'plot': [
        '开头：介绍角色和场景',
        '发展：小星星的冒险',
        '高潮：遇到小云朵',
        '结尾：温馨的睡眠氛围'
    ],
    'music': 'relaxing',
    'narration_tone': 'gentle',
    'narration_speed': 'slow'
}
```

### 儿童故事模板

```python
children_story = {
    'title': '勇敢的小猫',
    'characters': ['小猫咪', '小老鼠'],
    'setting': '花园',
    'plot': [
        '开头：介绍小猫咪',
        '发展：遇到小老鼠',
        '高潮：合作解决问题',
        '结尾：友谊和快乐'
    ],
    'music': 'cheerful',
    'narration_tone': 'energetic',
    'narration_speed': 'normal'
}
```

## 使用场景

### 场景1：睡前故事

```python
# 为孩子生成睡前故事
experience = create_bedtime_story(
    child_name="小明",
    favorite_animal="小熊",
    duration="10分钟"
)

# 播放
experience.play()
```

### 场景2：小说朗读

```python
# 朗读小说章节
narrate_chapter(
    title="第一章：神秘的森林",
    text=novel_chapter,
    voice='dramatic',
    speed=1.0,
    add_background_music=True,
    music='magical'
)
```

### 场景3：播客制作

```python
# 制作故事播客
podcast = create_podcast(
    title="每晚故事时间",
    episode="第5期",
    stories=[
        {
            'title': '森林里的音乐会',
            'content': '...',
            'music': 'classical',
            'duration': '8分钟'
        },
        {
            'title': '月亮的故事',
            'content': '...',
            'music': 'relaxing',
            'duration': '6分钟'
        }
    ]
)

# 播放列表模式
podcast.play_playlist()
```

## 音频管理

### 播放列表

```python
# 创建播放列表
playlist = StoryPlaylist([
    'relaxing',  # 开场音乐
    'story_with_music',  # 故事+音乐
    'emotional',  # 情感转折
    'relaxing'  # 结尾放松
])

# 播放
playlist.play()
```

### 音量控制

```python
# 调节音量
set_volume(80)  # 80%
set_volume(50)  # 50%

# 淡入淡出
fade_in(duration=3)  # 3秒淡入
fade_out(duration=5)  # 5秒淡出
```

## 高级功能

### 动态音乐切换

根据故事情节自动切换音乐：

```python
dynamic_music = DynamicMusicController()

# 设置情节触发点
dynamic_music.add_trigger(
    trigger="情节开始",
    music="magical",
    volume=70
)

dynamic_music.add_trigger(
    trigger="情节高潮",
    music="intense",
    volume=85
)

# 在故事中应用
dynamic_music.apply_to_story(story)
```

### 多角色对话

```python
dialogue = CharacterDialogue([
    {
        'character': '小熊',
        'voice': 'gentle',
        'lines': ['大家好！', '今天天气真好！']
    },
    {
        'character': '小兔子',
        'voice': 'cheerful',
        'lines': ['是啊！我们去冒险吧！']
    }
])

dialogue.narrate_with_music(music='cheerful')
```

### 情感氛围调节

根据故事情感调整整体氛围：

```python
atmosphere = AtmosphereController(
    story=story,
    music='emotional',
    voice='warm',
    speed=0.9
)

# 播放
atmosphere.play()

# 调整氛围
atmosphere.set_mood('sad', intensity=0.7)
atmosphere.set_mood('happy', intensity=0.8)
```

## 故事参数配置

### 生成故事参数

```python
story_params = {
    'genre': 'bedtime',  # 故事类型
    'age_group': '6-12',  # 年龄组
    'length': 'medium',  # 长度
    'language': 'zh-CN',  # 语言
    'custom_elements': {  # 自定义元素
        'main_character': '小狐狸',
        'setting': '森林',
        'themes': ['友谊', '勇气']
    },
    'music': {
        'style': 'relaxing',
        'volume': 60,
        'loop': True
    }
}
```

### 音频播放参数

```python
audio_params = {
    'voice': 'gentle',  # 语音风格
    'speed': 0.8,  # 语速
    'pitch': 'lower',  # 音调
    'volume': 70,  # 音量
    'fade_in': 3,  # 淡入时间
    'fade_out': 5,  # 淡出时间
    'crossfade': 2  # 交叉淡入时间
}
```

## 故事示例

### 示例1：睡前故事

```
标题：小星星的梦
类型：睡前故事
角色：小星星、云朵妈妈
场景：夜空
时长：5分钟

[音乐：relaxing - 开始播放]

旁白：很久很久以前，在遥远的夜空上...

[情节：小星星想要去找朋友]

[音乐：切换到magical]

旁白：小星星飘啊飘，飘到了云端...

[高潮：遇到云朵妈妈]

[音乐：切换到cheerful - 暂停]

旁白：云朵妈妈温柔地说...

[结尾：温馨入睡]

[音乐：relaxing - 淡出]
```

### 示例2：儿童故事

```
标题：勇敢的小猫
类型：儿童故事
角色：小猫咪、小老鼠
场景：花园
时长：8分钟

[音乐：cheerful - 开始播放]

小猫咪：（欢快）今天天气真好！

[音乐：切换到dramatic]

旁白：突然，小猫咪遇到了困难...

[高潮：合作解决问题]

[音乐：切换到magical]

小老鼠：（惊喜）我也有办法！

[结尾：友谊和快乐]

[音乐：切换到relaxing - 持续播放]
```

## 故事生成工作流

### 标准流程

1. **选择故事类型**
   ```
   睡前故事 / 儿童故事 / 奇幻故事 / 科幻故事...
   ```

2. **设定参数**
   ```
   - 故事标题
   - 主要角色
   - 故事背景
   - 目标时长
   - 年龄组
   ```

3. **选择音乐风格**
   ```
   - 轻松 / 欢快 / 悲伤 / 紧张...
   ```

4. **生成故事**
   ```
   自动生成故事内容
   ```

5. **配置音频**
   ```
   - 语音风格
   - 语速
   - 音量
   ```

6. **播放故事**
   ```
   旁白 + 背景音乐
   ```

### 自定义流程

```python
# 自定义故事生成
custom_story = create_custom_story(
    theme="环保",
    length="长篇",
    age_group="12+",
    characters=["小树苗", "小水滴"],
    plot_outline=[
        "小树苗努力生长",
        "遇到干旱困难",
        "小水滴帮助它",
        "最终茁壮成长"
    ],
    music_style="emotional",
    voice_style='gentle'
)

# 播放
custom_story.play()
```

## 故事库管理

### 存储故事

```python
# 保存故事
save_story(
    title="我的睡前故事",
    content=story_content,
    metadata={
        'type': 'bedtime',
        'age_group': '3-6',
        'created_date': '2026-03-06'
    }
)

# 从库加载
loaded_story = load_story("我的睡前故事")
```

### 故事分类

```
stories/
├── bedtime/           # 睡前故事
│   ├── 小星星的梦.mp3
│   ├── 森林里的音乐会.mp3
│   └── 月亮的故事.mp3
├── children/          # 儿童故事
│   ├── 勇敢的小猫.mp3
│   ├── 小兔子的冒险.mp3
│   └── 快乐的小熊.mp3
├── fantasy/           # 奇幻故事
│   └── 魔法森林.mp3
└── science_fiction/   # 科幻故事
    └── 太空之旅.mp3
```

## 故事分享

### 导出故事

```python
# 导出为文本
export_story(story, format='txt', filename='story.txt')

# 导出为音频
export_story(story, format='audio', filename='story.mp3')

# 导出为视频
export_story(story, format='video', filename='story.mp4')
```

### 分享故事

```python
# 生成分享链接
share_link = generate_share_link(story)

# 分享到平台
share_to_platform('wechat', story)
share_to_platform('wechat_moments', story)
```

## 故事编辑

### 编辑故事内容

```python
# 修改故事文本
edit_story_text(
    story="小星星的梦",
    change=from="小星星飘啊飘",
    to="小星星慢慢地飘"
)

# 调整播放顺序
reorder_stories([
    "月亮的故事",
    "森林里的音乐会",
    "小星星的梦"
])
```

### 编辑音频

```python
# 调整音乐音量
adjust_music_volume(
    story="小星星的梦",
    volume=75
)

# 调整旁白语速
adjust_narration_speed(
    story="小星星的梦",
    speed=0.7
)

# 切换语音风格
switch_voice(
    story="小星星的梦",
    voice='warm'
)
```

## 故事播放器

### 基础播放器

```python
from player import StoryPlayer

# 创建播放器
player = StoryPlayer()

# 播放故事
player.play(story="小星星的梦")

# 暂停
player.pause()

# 恢复
player.resume()

# 停止
player.stop()
```

### 高级播放器

```python
# 创建高级播放器
player = AdvancedStoryPlayer()

# 设置播放模式
player.set_mode('continuous')  # 连续播放
player.set_mode('single')      # 单首播放
player.set_mode('shuffle')     # 随机播放

# 设置循环
player.set_loop(True)  # 循环播放
player.set_loop(False)  # 不循环

# 设置音量
player.set_volume(80)

# 设置静音
player.set_muted(True)

# 播放历史
print(player.get_history())

# 删除播放历史
player.clear_history()
```

## 故事效果

### 音效添加

```python
# 添加环境音效
add_sound_effect(
    story="小星星的梦",
    effect='night_noise',  # 夜晚声音
    volume=20
)

# 添加特殊音效
add_sound_effect(
    story="魔法森林",
    effect='magic_chime',  # 魔法铃声
    volume=30
)
```

### 背景氛围

```python
# 设置背景氛围
set_background_atmosphere(
    story="悲伤的故事",
    atmosphere='rain',  # 雨声氛围
    intensity=60
)

set_background_atmosphere(
    story="欢快的舞会",
    atmosphere='party',  # 聚会氛围
    intensity=70
)
```

## 常见问题

### Q: 如何添加自己的音乐？

**A:** 将音乐文件放入 `assets/music/` 目录，然后在代码中引用：

```python
# 添加到音乐库
from assets.music import track_list

track_list.append({
    'name': '我的音乐',
    'file': 'my_music.mp3',
    'mood': 'happy',
    'duration': 3:30
})
```

### Q: 如何调整语速？

**A:** 使用 `narration_speed` 参数：

```python
narrate(
    text="故事内容",
    speed=0.7  # 0.6-1.5 之间
)
```

- 1.0: 正常速度
- 0.8: 慢速（适合睡前）
- 0.6: 极慢（适合儿童）
- 1.2: 快速

### Q: 如何选择合适的音乐？

**A:** 根据故事类型选择：

| 故事类型 | 推荐音乐 |
|---------|---------|
| 睡前故事 | relaxing, gentle |
| 儿童故事 | cheerful, playful |
| 悲伤故事 | emotional, piano |
| 悬疑故事 | intense, dramatic |
| 奇幻故事 | magical, ethereal |
| 历史故事 | classical, orchestral |

### Q: 可以同时播放多个音频吗？

**A:** 可以，使用交叉淡入淡出：

```python
# 播放音乐
play_music('relaxing', crossfade=2)

# 播放旁白
play_narration(story, crossfade=3)

# 淡出音乐
fade_out_music(duration=5)
```

## 故事创作技巧

### 1. 保持节奏

- 开头：快速引入
- 中间：逐渐展开
- 高潮：紧张刺激
- 结尾：温馨收尾

### 2. 情感起伏

- 设置1-2个情感高潮
- 使用音乐配合情感变化
- 适当的音量变化

### 3. 互动性

- 添加提问环节
- 让听众参与决策
- 增加互动音效

### 4. 重复性

- 重要情节重复强调
- 主题反复出现
- 使用重复的音乐节奏

## 故事制作清单

### 制作前检查

- [ ] 确定故事类型和目标受众
- [ ] 选择合适的故事主题
- [ ] 设定主要角色
- [ ] 规划故事情节
- [ ] 选择音乐风格
- [ ] 准备背景音效

### 制作中检查

- [ ] 生成故事内容
- [ ] 选择合适的音乐
- [ ] 设置语音参数
- [ ] 测试播放效果
- [ ] 调整音量和节奏

### 制作后检查

- [ ] 完整测试播放流程
- [ ] 检查音频质量
- [ ] 确认所有功能正常
- [ ] 保存故事文件
- [ ] 分享给目标受众

## 技术支持

### 问题反馈

遇到问题请记录：

1. **问题描述**
2. **错误信息**（如有）
3. **操作步骤**
4. **预期结果**
5. **实际结果**

### 功能建议

欢迎提出功能改进建议：

- 新的故事类型
- 更多音乐素材
- 特殊音效
- 视频功能
- 跨平台支持

## 更新日志

### v1.0.0 (2026-03-06)

**新增功能：**
- 故事生成基础功能
- 音乐选择和播放
- 语音旁白
- 音频控制

**基础素材：**
- 7种背景音乐风格
- 多种语音风格
- 故事模板

**支持场景：**
- 睡前故事
- 儿童故事
- 小说朗读
- 播客制作

---

**使用提示：**
- 首次使用建议从简单场景开始
- 可以根据需要自定义音乐和语音
- 建议定期保存故事文件
- 探索不同组合创造独特体验
