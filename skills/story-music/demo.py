#!/usr/bin/env python3
"""故事音乐技能演示脚本"""

import sys
import time

# 添加scripts到路径
sys.path.insert(0, '/Users/liuxing/.openclaw/workspace/skills/story-music')

print("=" * 70)
print("🎵 故事音乐技能演示")
print("=" * 70)
print()

# 模拟故事生成
print("📖 步骤1: 生成睡前故事")
print("-" * 70)
story = {
    'title': '小星星的梦',
    'genre': 'bedtime',
    'characters': ['小星星', '云朵妈妈'],
    'setting': '夜空',
    'duration': '5分钟',
    'content': '''
从前，在遥远的夜空上，有一颗小星星。

一天晚上，小星星做了一个梦。

梦见自己飘啊飘，飘到了柔软的云朵上。

云朵妈妈温柔地说："晚上好，小星星。"

小星星问："我可以和你们一起玩吗？"

云朵妈妈说："当然可以！"

于是，小星星在云朵上睡着了。

夜风吹过，小星星做了一个甜甜的梦...

（故事继续...）
'''
}

print(f"标题: {story['title']}")
print(f"类型: {story['genre']}")
print(f"角色: {', '.join(story['characters'])}")
print(f"场景: {story['setting']}")
print(f"时长: {story['duration']}")
print(f"\n故事内容预览:\n{story['content']}")
print()

# 模拟音乐选择
print("🎵 步骤2: 选择背景音乐")
print("-" * 70)
music_options = {
    'style': 'relaxing',
    'name': '深夜宁静',
    'duration': '3:45',
    'volume': 60,
    'loop': True
}

print(f"音乐风格: {music_options['style']}")
print(f"音乐名称: {music_options['name']}")
print(f"时长: {music_options['duration']}")
print(f"音量: {music_options['volume']}%")
print(f"循环播放: {'是' if music_options['loop'] else '否'}")
print()

# 模拟语音旁白
print("🎙️ 步骤3: 配置语音旁白")
print("-" * 70)
narration = {
    'voice': 'gentle',
    'speed': 0.8,
    'pitch': 'lower',
    'volume': 70
}

print(f"语音风格: {narration['voice']}")
print(f"语速: {narration['speed'] * 100}% (慢速适合睡前)")
print(f"音调: {narration['pitch']}")
print(f"音量: {narration['volume']}%")
print()

# 模拟播放
print("▶️ 步骤4: 播放故事")
print("-" * 70)
print("正在播放...")
print()

# 播放演示
segments = [
    ("开场", 10, music_options['style']),
    ("情节开始", 15, 'magical'),
    ("高潮", 20, 'dramatic'),
    ("结尾", 15, 'relaxing'),
]

total_duration = sum(seg[1] for seg in segments)

for i, (segment_name, duration, music_style) in enumerate(segments, 1):
    print(f"⏱️  [{i}/{len(segments)}] {segment_name}")
    print(f"   🎵 音乐切换到: {music_style}")
    print(f"   ⏱️  时长: {duration}秒")
    time.sleep(0.5)  # 模拟播放

print()
print("✅ 播放完成!")
print()

# 模拟儿童故事示例
print("👦 儿童故事示例")
print("=" * 70)
children_story = {
    'title': '勇敢的小猫',
    'type': 'children',
    'characters': ['小猫咪', '小老鼠'],
    'music': 'cheerful',
    'narration': 'energetic'
}

print(f"标题: {children_story['title']}")
print(f"类型: {children_story['type']}")
print(f"音乐: {children_story['music']} (欢快活泼)")
print(f"旁白: {children_story['narration']} (活力充沛)")
print()

print("🎵 可用的音乐风格:")
print("  - relaxing (轻松舒缓)")
print("  - cheerful (欢快活泼)")
print("  - emotional (悲伤感人)")
print("  - intense (紧张刺激)")
print("  - magical (神秘奇幻)")
print("  - classical (古典优雅)")
print("  - pop (现代流行)")
print()

print("🎙️ 可用的语音风格:")
print("  - gentle (柔和)")
print("  - warm (温暖)")
print("  - energetic (活力)")
print("  - dramatic (戏剧)")
print("  - calm (平静)")
print()

print("=" * 70)
print("🎉 演示完成!")
print("=" * 70)
print()
print("💡 提示:")
print("  1. 使用 generate_story() 生成故事")
print("  2. 使用 select_music() 选择音乐")
print("  3. 使用 narrate() 添加旁白")
print("  4. 使用 StoryPlayer 播放故事")
print()
print("📚 更多示例请查看 SKILL.md")
