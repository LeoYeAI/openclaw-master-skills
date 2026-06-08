#!/usr/bin/env python3
"""
🧬 Soul Report Generator (Multi-language)
Generate an interactive HTML personality portrait report.

Supports automatic language detection:
  - Chinese name → Chinese report
  - Non-Chinese name → English report
  - Manual override via --lang zh/en

Usage:
  python3 soul_report.py [--output /path/to/report.html] [--lang zh|en]
  python3 soul_report.py --soul-dir /custom/path --output report.html

Default data directory: ~/.skills_data/soul-archive/ (resolved via Path.home(), cross-platform)
"""

import json
import re
import sys
import argparse
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from soul_extract import SoulArchive, load_json


# ============================================================
# Multi-language Translation Dictionaries
# ============================================================

I18N = {
    "zh": {
        "html_lang": "zh-CN",
        "title": "{name} 的灵魂画像",
        "subtitle": "基于 {n} 次对话提取 · 最后更新 {date}",
        "soul_completeness": "灵魂完整度",
        "dim_completeness": "各维度完整度",
        "identity": "身份信息",
        "personality": "性格特征",
        "language_fp": "语言指纹",
        "topics": "话题兴趣",
        "emotions": "情感模式",
        "relationships": "人际关系",
        "memories": "记忆片段",
        "footer": "灵魂存档 Soul Archive v1.0 · 生成于 {time}",
        # Identity fields
        "id_name": "姓名", "id_nickname": "昵称", "id_age": "年龄",
        "id_gender": "性别", "id_location": "所在地", "id_hometown": "老家",
        "id_occupation": "职业", "id_company": "公司", "id_education": "学历",
        "id_hobbies": "爱好", "id_motto": "人生信条",
        # Lifestyle
        "lifestyle": "🎯 生活习惯",
        "ls_routine": "作息", "ls_sleep": "睡眠",
        "ls_food": "饮食偏好", "ls_music": "音乐品味",
        "ls_movie": "电影品味", "ls_book": "阅读偏好",
        "ls_aesthetic": "审美风格", "ls_spending": "消费风格",
        "ls_travel": "旅行偏好", "ls_pet": "宠物",
        # Digital
        "digital": "🌐 数字身份",
        "dg_apps": "常用App", "dg_social": "社交平台",
        "dg_personas": "网名风格", "dg_tech": "技术水平",
        "dg_habits": "上网习惯",
        # Personality
        "ps_decision": "决策",
        "ps_behavior": "⚡ 行为模式",
        "ps_risk": "风险偏好", "ps_procrastination": "拖延程度",
        "ps_perfectionism": "完美主义", "ps_planning": "计划性",
        "ps_learning": "学习方式", "ps_work": "工作风格",
        "ps_social": "🤝 社交风格",
        "ps_energy": "社交能量", "ps_role": "群体角色",
        "ps_conflict": "冲突方式", "ps_trust": "信任方式",
        "ps_drivers": "🔥 核心驱动力",
        "no_data": "暂无数据",
        "no_data_chat": "暂无数据，继续聊天来补充...",
        # Language
        "catchphrases": "💬 口头禅",
        "sentence_patterns": "📐 句式模式",
        "speech_samples": "✍️ 说话示例",
        "formality": "正式度", "verbosity": "话量",
        "humor": "幽默", "thinking": "思考表达",
        "filler_words": "💭 语气词/填充词",
        "dialect": "🏠 方言特征",
        "agree_expr": "👍 同意时的表达",
        "disagree_expr": "👎 不同意时的表达",
        "deep_fp": "🔬 深度指纹",
        "persuasion": "说服方式", "storytelling": "叙事风格",
        "question_style": "提问风格", "greeting": "打招呼",
        "farewell": "告别方式", "typing": "打字习惯",
        "no_lang_data": "暂无语言数据",
        "no_topic_data": "暂无话题数据",
        "no_emotion_data": "暂无情感数据",
        "no_people_data": "暂无人际关系数据（需在 config.json 中启用 relationships 采集）",
        "no_memory_data": "暂无记忆数据，继续对话来积累...",
        # Big Five
        "bf_openness": "开放性", "bf_conscientiousness": "尽责性",
        "bf_extraversion": "外向性", "bf_agreeableness": "宜人性",
        "bf_stability": "情绪稳定",
        # Emotion labels
        "emo_joy": "😊 开心", "emo_anger": "😤 生气",
        "emo_sadness": "😢 伤感", "emo_anxiety": "😰 焦虑",
        "emo_excitement": "🤩 兴奋", "emo_nostalgia": "🥹 怀旧",
        "emo_pride": "🏆 自豪", "emo_gratitude": "🙏 感恩",
        "emo_frustration": "😤 挫败", "emo_curiosity": "🧐 好奇",
        "emo_peace": "😌 平静", "emo_guilt": "😔 愧疚",
        # Dimension names for progress bars
        "dim_identity": "身份信息", "dim_personality": "性格特征",
        "dim_language": "语言风格", "dim_knowledge": "知识观点",
        "dim_memory": "记忆经历", "dim_relationships": "人际关系",
        "dim_voice": "语音特征",
    },
    "en": {
        "html_lang": "en",
        "title": "Soul Portrait of {name}",
        "subtitle": "Extracted from {n} conversations · Last updated {date}",
        "soul_completeness": "Soul Completeness",
        "dim_completeness": "Dimension Completeness",
        "identity": "Identity",
        "personality": "Personality",
        "language_fp": "Language Fingerprint",
        "topics": "Topic Interests",
        "emotions": "Emotional Patterns",
        "relationships": "Relationships",
        "memories": "Memory Fragments",
        "footer": "Soul Archive v1.0 · Generated on {time}",
        # Identity fields
        "id_name": "Name", "id_nickname": "Nickname", "id_age": "Age",
        "id_gender": "Gender", "id_location": "Location", "id_hometown": "Hometown",
        "id_occupation": "Occupation", "id_company": "Company", "id_education": "Education",
        "id_hobbies": "Hobbies", "id_motto": "Life Motto",
        # Lifestyle
        "lifestyle": "🎯 Lifestyle",
        "ls_routine": "Routine", "ls_sleep": "Sleep",
        "ls_food": "Food Preferences", "ls_music": "Music Taste",
        "ls_movie": "Movie Taste", "ls_book": "Reading Preferences",
        "ls_aesthetic": "Aesthetic Style", "ls_spending": "Spending Style",
        "ls_travel": "Travel Preferences", "ls_pet": "Pets",
        # Digital
        "digital": "🌐 Digital Identity",
        "dg_apps": "Favorite Apps", "dg_social": "Social Platforms",
        "dg_personas": "Online Personas", "dg_tech": "Tech Proficiency",
        "dg_habits": "Digital Habits",
        # Personality
        "ps_decision": "Decision",
        "ps_behavior": "⚡ Behavioral Patterns",
        "ps_risk": "Risk Tolerance", "ps_procrastination": "Procrastination",
        "ps_perfectionism": "Perfectionism", "ps_planning": "Planning Style",
        "ps_learning": "Learning Style", "ps_work": "Work Style",
        "ps_social": "🤝 Social Style",
        "ps_energy": "Social Energy", "ps_role": "Group Role",
        "ps_conflict": "Conflict Approach", "ps_trust": "Trust Building",
        "ps_drivers": "🔥 Core Drivers",
        "no_data": "No data yet",
        "no_data_chat": "No data yet. Keep chatting to fill in...",
        # Language
        "catchphrases": "💬 Catchphrases",
        "sentence_patterns": "📐 Sentence Patterns",
        "speech_samples": "✍️ Speech Samples",
        "formality": "Formality", "verbosity": "Verbosity",
        "humor": "Humor", "thinking": "Thinking Style",
        "filler_words": "💭 Filler Words",
        "dialect": "🏠 Dialect Features",
        "agree_expr": "👍 Agreement Expressions",
        "disagree_expr": "👎 Disagreement Expressions",
        "deep_fp": "🔬 Deep Fingerprint",
        "persuasion": "Persuasion Style", "storytelling": "Storytelling Style",
        "question_style": "Question Style", "greeting": "Greeting Style",
        "farewell": "Farewell Style", "typing": "Typing Habits",
        "no_lang_data": "No language data yet",
        "no_topic_data": "No topic data yet",
        "no_emotion_data": "No emotional data yet",
        "no_people_data": "No relationship data yet (enable relationships collection in config.json)",
        "no_memory_data": "No memory data yet. Keep chatting to build up...",
        # Big Five
        "bf_openness": "Openness", "bf_conscientiousness": "Conscientiousness",
        "bf_extraversion": "Extraversion", "bf_agreeableness": "Agreeableness",
        "bf_stability": "Emotional Stability",
        # Emotion labels
        "emo_joy": "😊 Joy", "emo_anger": "😤 Anger",
        "emo_sadness": "😢 Sadness", "emo_anxiety": "😰 Anxiety",
        "emo_excitement": "🤩 Excitement", "emo_nostalgia": "🥹 Nostalgia",
        "emo_pride": "🏆 Pride", "emo_gratitude": "🙏 Gratitude",
        "emo_frustration": "😤 Frustration", "emo_curiosity": "🧐 Curiosity",
        "emo_peace": "😌 Peace", "emo_guilt": "😔 Guilt",
        # Dimension names for progress bars
        "dim_identity": "Identity", "dim_personality": "Personality",
        "dim_language": "Language Style", "dim_knowledge": "Knowledge",
        "dim_memory": "Memory", "dim_relationships": "Relationships",
        "dim_voice": "Voice",
    }
}


def _has_chinese(text: str) -> bool:
    """Check if a string contains Chinese characters."""
    if not text:
        return False
    return bool(re.search(r'[\u4e00-\u9fff\u3400-\u4dbf]', text))


def detect_language(name: str) -> str:
    """
    Auto-detect report language based on user's name.
    Chinese name → 'zh', otherwise → 'en'.
    """
    if _has_chinese(name or ""):
        return "zh"
    return "en"


def generate_html_report(archive: SoulArchive, output_path: str = None, lang: str = None) -> str:
    """Generate an HTML personality portrait report with automatic language detection."""
    data = archive.load_all()
    bi = data["basic_info"]
    ps = data["personality"]
    lang_data = data["language"]
    comm = data["communication"]
    topics_data = data["topics"]
    emotional = data["emotional"]
    people = data["people"]
    profile = data["profile"]

    name = bi.get("name") or bi.get("nickname") or "Unknown Soul"

    # Auto-detect language from name if not specified
    if lang is None:
        lang = detect_language(name)

    t = I18N.get(lang, I18N["en"])  # fallback to English

    scores = profile.get("dimensions", {})
    completeness = profile.get("completeness_score", 0)

    # --- Build data JSON for JS ---
    # Topics
    topics_list = topics_data.get("topics", [])
    topics_json = json.dumps([
        {"name": tp.get("name", ""), "frequency": tp.get("frequency", 1), "sentiment": tp.get("sentiment", "neutral")}
        for tp in sorted(topics_list, key=lambda x: x.get("frequency", 0), reverse=True)[:15]
    ], ensure_ascii=False)

    # Big Five
    bf = ps.get("big_five", {})
    bf_json = json.dumps({
        t["bf_openness"]: (bf.get("openness", 0) or 0) * 100,
        t["bf_conscientiousness"]: (bf.get("conscientiousness", 0) or 0) * 100,
        t["bf_extraversion"]: (bf.get("extraversion", 0) or 0) * 100,
        t["bf_agreeableness"]: (bf.get("agreeableness", 0) or 0) * 100,
        t["bf_stability"]: (1 - (bf.get("neuroticism", 0) or 0)) * 100
    }, ensure_ascii=False)

    # Dimension scores
    dim_json = json.dumps({
        t["dim_identity"]: scores.get("identity", 0) * 100,
        t["dim_personality"]: scores.get("personality", 0) * 100,
        t["dim_language"]: scores.get("language_style", 0) * 100,
        t["dim_knowledge"]: scores.get("knowledge", 0) * 100,
        t["dim_memory"]: scores.get("memory", 0) * 100,
        t["dim_relationships"]: scores.get("relationships", 0) * 100,
        t["dim_voice"]: scores.get("voice", 0) * 100,
    }, ensure_ascii=False)

    # Emotional triggers
    triggers = emotional.get("triggers", {})
    emo_data = []
    for emo, items in triggers.items():
        if items:
            emo_data.append({"emotion": emo, "triggers": items})
    emo_json = json.dumps(emo_data, ensure_ascii=False)

    # People
    people_list = people.get("people", [])
    people_json = json.dumps(people_list, ensure_ascii=False)

    # Episodic memory
    ep_dir = archive.root / "memory" / "episodic"
    episodes = []
    if ep_dir.exists():
        for f in sorted(ep_dir.glob("*.jsonl"), reverse=True):
            if archive.crypto is not None:
                episodes.extend(archive.crypto.read_encrypted_jsonl(f))
            else:
                with open(f, 'r', encoding='utf-8') as fh:
                    for line in fh:
                        try:
                            episodes.append(json.loads(line.strip()))
                        except json.JSONDecodeError:
                            continue
            if len(episodes) >= 20:
                break
    episodes_json = json.dumps(episodes[:20], ensure_ascii=False)

    # Emotion label map (JS)
    emo_labels_json = json.dumps({
        "joy": t["emo_joy"], "anger": t["emo_anger"],
        "sadness": t["emo_sadness"], "anxiety": t["emo_anxiety"],
        "excitement": t["emo_excitement"], "nostalgia": t["emo_nostalgia"],
        "pride": t["emo_pride"], "gratitude": t["emo_gratitude"],
        "frustration": t["emo_frustration"], "curiosity": t["emo_curiosity"],
        "peace": t["emo_peace"], "guilt": t["emo_guilt"]
    }, ensure_ascii=False)

    # Identity field label map
    id_fields_json = json.dumps([
        [t["id_name"], "name"], [t["id_nickname"], "nickname"],
        [t["id_age"], "age"], [t["id_gender"], "gender"],
        [t["id_location"], "location"], [t["id_hometown"], "hometown"],
        [t["id_occupation"], "occupation"], [t["id_company"], "company"],
        [t["id_education"], "education"],
    ], ensure_ascii=False)

    # Lifestyle labels
    ls_fields_json = json.dumps([
        [t["ls_routine"], "daily_routine"], [t["ls_sleep"], "sleep_schedule"],
        [t["ls_food"], "food_preferences"], [t["ls_music"], "music_taste"],
        [t["ls_movie"], "movie_taste"], [t["ls_book"], "book_taste"],
        [t["ls_aesthetic"], "aesthetic_style"], [t["ls_spending"], "spending_style"],
        [t["ls_travel"], "travel_preferences"], [t["ls_pet"], "pet_preference"],
    ], ensure_ascii=False)

    # Digital labels
    dg_fields_json = json.dumps([
        [t["dg_apps"], "favorite_apps"], [t["dg_social"], "social_platforms"],
        [t["dg_personas"], "online_personas"], [t["dg_tech"], "tech_proficiency"],
        [t["dg_habits"], "digital_habits"],
    ], ensure_ascii=False)

    # Behavior tags labels
    bh_fields_json = json.dumps([
        [t["ps_risk"], "risk_tolerance"], [t["ps_procrastination"], "procrastination_level"],
        [t["ps_perfectionism"], "perfectionism_level"], [t["ps_planning"], "planning_style"],
        [t["ps_learning"], "learning_style"], [t["ps_work"], "work_style"],
    ], ensure_ascii=False)

    # Social tags labels
    so_fields_json = json.dumps([
        [t["ps_energy"], "social_energy"], [t["ps_role"], "group_role"],
        [t["ps_conflict"], "conflict_approach"], [t["ps_trust"], "trust_building"],
    ], ensure_ascii=False)

    # Style tags labels
    st_fields_json = json.dumps([
        [t["formality"], "formality_level"], [t["verbosity"], "verbosity"],
        [t["humor"], "humor_style"], [t["thinking"], "thinking_expression"],
    ], ensure_ascii=False)

    # Deep lang labels
    dl_fields_json = json.dumps([
        [t["persuasion"], "persuasion_style"], [t["storytelling"], "storytelling_style"],
        [t["question_style"], "question_style"], [t["greeting"], "greeting_style"],
        [t["farewell"], "farewell_style"], [t["typing"], "typing_habits"],
    ], ensure_ascii=False)

    # Separator for arrays (Chinese uses 、, English uses ,)
    arr_sep = "、" if lang == "zh" else ", "

    html = f"""<!DOCTYPE html>
<html lang="{t['html_lang']}">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>🧬 {t['title'].format(name=name)}</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>
:root {{
  --bg: #0a0a0f;
  --card: #14141f;
  --card-hover: #1a1a2e;
  --border: #2a2a3e;
  --primary: #7c5bf5;
  --primary-glow: rgba(124, 91, 245, 0.3);
  --accent: #00d4aa;
  --text: #e8e8f0;
  --text-dim: #8888a0;
  --danger: #ff6b6b;
  --warning: #ffd93d;
  --success: #6bcb77;
}}

* {{ margin: 0; padding: 0; box-sizing: border-box; }}

body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', system-ui, sans-serif;
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
  overflow-x: hidden;
}}

body::before {{
  content: '';
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: radial-gradient(circle at 20% 50%, rgba(124,91,245,0.08) 0%, transparent 50%),
              radial-gradient(circle at 80% 20%, rgba(0,212,170,0.06) 0%, transparent 50%),
              radial-gradient(circle at 50% 80%, rgba(255,107,107,0.05) 0%, transparent 50%);
  pointer-events: none;
  z-index: 0;
}}

.container {{
  max-width: 1100px;
  margin: 0 auto;
  padding: 40px 20px;
  position: relative;
  z-index: 1;
}}

.header {{
  text-align: center;
  margin-bottom: 50px;
}}

.header h1 {{
  font-size: 2.5em;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 10px;
}}

.header .subtitle {{
  color: var(--text-dim);
  font-size: 1.1em;
}}

.completeness-ring {{
  width: 120px; height: 120px;
  margin: 20px auto;
  position: relative;
}}

.completeness-ring svg {{ width: 100%; height: 100%; transform: rotate(-90deg); }}
.completeness-ring .bg {{ fill: none; stroke: var(--border); stroke-width: 8; }}
.completeness-ring .fill {{ fill: none; stroke: var(--primary); stroke-width: 8; stroke-linecap: round;
  stroke-dasharray: 314; stroke-dashoffset: {314 - 314 * completeness}; transition: stroke-dashoffset 1.5s ease; }}
.completeness-ring .label {{
  position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);
  font-size: 1.5em; font-weight: 700; color: var(--primary);
}}

.card {{
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 28px;
  margin-bottom: 24px;
  transition: all 0.3s ease;
}}
.card:hover {{ background: var(--card-hover); border-color: var(--primary); box-shadow: 0 0 20px var(--primary-glow); }}
.card h2 {{
  font-size: 1.3em;
  margin-bottom: 20px;
  display: flex;
  align-items: center;
  gap: 10px;
}}
.card h2 .icon {{ font-size: 1.4em; }}

.grid-2 {{ display: grid; grid-template-columns: 1fr 1fr; gap: 24px; }}
@media (max-width: 768px) {{ .grid-2 {{ grid-template-columns: 1fr; }} }}

.tag {{
  display: inline-block;
  padding: 5px 14px;
  border-radius: 20px;
  font-size: 0.85em;
  margin: 3px;
  background: rgba(124, 91, 245, 0.15);
  color: var(--primary);
  border: 1px solid rgba(124, 91, 245, 0.3);
}}
.tag.green {{ background: rgba(0, 212, 170, 0.15); color: var(--accent); border-color: rgba(0, 212, 170, 0.3); }}
.tag.red {{ background: rgba(255, 107, 107, 0.15); color: var(--danger); border-color: rgba(255, 107, 107, 0.3); }}
.tag.yellow {{ background: rgba(255, 217, 61, 0.15); color: var(--warning); border-color: rgba(255, 217, 61, 0.3); }}

.progress-item {{ margin-bottom: 12px; }}
.progress-item .label {{ display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 0.9em; }}
.progress-bar {{ height: 8px; background: var(--border); border-radius: 4px; overflow: hidden; }}
.progress-bar .fill {{ height: 100%; border-radius: 4px; transition: width 1s ease;
  background: linear-gradient(90deg, var(--primary), var(--accent)); }}

.quote {{
  padding: 12px 16px;
  border-left: 3px solid var(--primary);
  background: rgba(124, 91, 245, 0.08);
  border-radius: 0 8px 8px 0;
  margin: 8px 0;
  font-style: italic;
  color: var(--text-dim);
}}

.topic-cloud {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }}
.topic-item {{
  padding: 8px 16px; border-radius: 20px; cursor: default;
  transition: all 0.3s; font-weight: 500;
}}
.topic-item:hover {{ transform: scale(1.1); }}

.timeline {{ position: relative; padding-left: 30px; }}
.timeline::before {{ content: ''; position: absolute; left: 10px; top: 0; bottom: 0; width: 2px; background: var(--border); }}
.timeline-item {{
  position: relative; margin-bottom: 20px; padding: 12px 16px;
  background: rgba(124, 91, 245, 0.05); border-radius: 8px;
}}
.timeline-item::before {{
  content: ''; position: absolute; left: -24px; top: 16px;
  width: 10px; height: 10px; border-radius: 50%;
  background: var(--primary); border: 2px solid var(--bg);
}}

.person-card {{
  display: flex; align-items: center; gap: 12px;
  padding: 12px; border-radius: 10px; margin-bottom: 8px;
  background: rgba(0, 212, 170, 0.05); border: 1px solid rgba(0, 212, 170, 0.15);
}}
.person-avatar {{
  width: 40px; height: 40px; border-radius: 50%;
  background: linear-gradient(135deg, var(--primary), var(--accent));
  display: flex; align-items: center; justify-content: center;
  font-size: 1.2em; color: white;
}}

.info-row {{ display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid var(--border); }}
.info-row:last-child {{ border-bottom: none; }}
.info-row .key {{ color: var(--text-dim); }}
.info-row .val {{ font-weight: 500; }}

.chart-container {{ position: relative; height: 280px; }}

footer {{
  text-align: center;
  padding: 40px 0 20px;
  color: var(--text-dim);
  font-size: 0.85em;
}}
</style>
</head>
<body>

<div class="container">

  <!-- Header -->
  <div class="header">
    <h1>🧬 {t['title'].format(name=name)}</h1>
    <p class="subtitle">{t['subtitle'].format(n=profile.get('total_extractions', 0), date=profile.get('last_updated', 'N/A')[:10])}</p>
    <div class="completeness-ring">
      <svg viewBox="0 0 120 120">
        <circle class="bg" cx="60" cy="60" r="50"/>
        <circle class="fill" cx="60" cy="60" r="50"/>
      </svg>
      <div class="label">{completeness:.0%}</div>
    </div>
    <p class="subtitle" style="font-size:0.9em;">{t['soul_completeness']}</p>
  </div>

  <!-- Dimension Progress -->
  <div class="card">
    <h2><span class="icon">📊</span> {t['dim_completeness']}</h2>
    <div id="dim-progress"></div>
  </div>

  <div class="grid-2">
    <!-- Identity Card -->
    <div class="card">
      <h2><span class="icon">👤</span> {t['identity']}</h2>
      <div id="identity-info"></div>
    </div>

    <!-- Personality -->
    <div class="card">
      <h2><span class="icon">💫</span> {t['personality']}</h2>
      <div id="personality-tags"></div>
      <div class="chart-container" style="margin-top:20px;">
        <canvas id="big5Chart"></canvas>
      </div>
    </div>
  </div>

  <!-- Language Style -->
  <div class="card">
    <h2><span class="icon">🗣️</span> {t['language_fp']}</h2>
    <div id="language-section"></div>
  </div>

  <div class="grid-2">
    <!-- Topic Interests -->
    <div class="card">
      <h2><span class="icon">🔥</span> {t['topics']}</h2>
      <div class="topic-cloud" id="topic-cloud"></div>
    </div>

    <!-- Emotional Patterns -->
    <div class="card">
      <h2><span class="icon">❤️</span> {t['emotions']}</h2>
      <div id="emotional-section"></div>
    </div>
  </div>

  <!-- Relationships -->
  <div class="card">
    <h2><span class="icon">🤝</span> {t['relationships']}</h2>
    <div id="people-section"></div>
  </div>

  <!-- Memory Fragments -->
  <div class="card">
    <h2><span class="icon">📝</span> {t['memories']}</h2>
    <div class="timeline" id="episodes-section"></div>
  </div>

  <footer>
    🧬 {t['footer'].format(time=datetime.now().strftime('%Y-%m-%d %H:%M'))}
  </footer>
</div>

<script>
// ---- Data ----
const basicInfo = {json.dumps(bi, ensure_ascii=False)};
const personality = {json.dumps(ps, ensure_ascii=False)};
const language = {json.dumps(lang_data, ensure_ascii=False)};
const topicsData = {topics_json};
const bigFive = {bf_json};
const dimScores = {dim_json};
const emotionalData = {emo_json};
const peopleData = {people_json};
const episodes = {episodes_json};
const emoLabels = {emo_labels_json};
const arrSep = {json.dumps(arr_sep)};

// Label maps
const idFields = {id_fields_json};
const lsFields = {ls_fields_json};
const dgFields = {dg_fields_json};
const bhFields = {bh_fields_json};
const soFields = {so_fields_json};
const stFields = {st_fields_json};
const dlFields = {dl_fields_json};

// i18n strings
const i18n = {{
  lifestyle: {json.dumps(t['lifestyle'])},
  digital: {json.dumps(t['digital'])},
  decision: {json.dumps(t['ps_decision'])},
  behavior: {json.dumps(t['ps_behavior'])},
  socialStyle: {json.dumps(t['ps_social'])},
  drivers: {json.dumps(t['ps_drivers'])},
  noData: {json.dumps(t['no_data'])},
  noDataChat: {json.dumps(t['no_data_chat'])},
  catchphrases: {json.dumps(t['catchphrases'])},
  sentencePatterns: {json.dumps(t['sentence_patterns'])},
  speechSamples: {json.dumps(t['speech_samples'])},
  fillerWords: {json.dumps(t['filler_words'])},
  dialect: {json.dumps(t['dialect'])},
  agreeExpr: {json.dumps(t['agree_expr'])},
  disagreeExpr: {json.dumps(t['disagree_expr'])},
  deepFp: {json.dumps(t['deep_fp'])},
  noLangData: {json.dumps(t['no_lang_data'])},
  noTopicData: {json.dumps(t['no_topic_data'])},
  noEmotionData: {json.dumps(t['no_emotion_data'])},
  noPeopleData: {json.dumps(t['no_people_data'])},
  noMemoryData: {json.dumps(t['no_memory_data'])},
  idHobbies: {json.dumps(t['id_hobbies'])},
  idMotto: {json.dumps(t['id_motto'])}
}};

// ---- Helpers ----
function getVal(obj, key) {{
  const v = obj[key];
  if (Array.isArray(v)) return v.length ? v.join(arrSep) : null;
  return v || null;
}}

// ---- Dimension Progress Bars ----
const dimEl = document.getElementById('dim-progress');
Object.entries(dimScores).forEach(([name, score]) => {{
  dimEl.innerHTML += `
    <div class="progress-item">
      <div class="label"><span>${{name}}</span><span>${{Math.round(score)}}%</span></div>
      <div class="progress-bar"><div class="fill" style="width:${{score}}%"></div></div>
    </div>`;
}});

// ---- Identity Info ----
const idEl = document.getElementById('identity-info');

// Core fields
idFields.forEach(([label, key]) => {{
  const v = getVal(basicInfo, key);
  if (v) idEl.innerHTML += `<div class="info-row"><span class="key">${{label}}</span><span class="val">${{v}}</span></div>`;
}});

// Hobbies and motto (special: array or string)
const hobbies = basicInfo.hobbies?.length ? basicInfo.hobbies.join(arrSep) : null;
if (hobbies) idEl.innerHTML += `<div class="info-row"><span class="key">${{i18n.idHobbies}}</span><span class="val">${{hobbies}}</span></div>`;
const motto = basicInfo.life_motto;
if (motto) idEl.innerHTML += `<div class="info-row"><span class="key">${{i18n.idMotto}}</span><span class="val">${{motto}}</span></div>`;

// Lifestyle
const filledLs = lsFields.filter(([, key]) => getVal(basicInfo, key));
if (filledLs.length) {{
  idEl.innerHTML += `<div style="margin:12px 0 6px;color:var(--accent);font-size:0.9em;font-weight:600;">${{i18n.lifestyle}}</div>`;
  filledLs.forEach(([label, key]) => {{
    idEl.innerHTML += `<div class="info-row"><span class="key">${{label}}</span><span class="val">${{getVal(basicInfo, key)}}</span></div>`;
  }});
}}

// Digital Identity
const filledDg = dgFields.filter(([, key]) => getVal(basicInfo, key));
if (filledDg.length) {{
  idEl.innerHTML += `<div style="margin:12px 0 6px;color:var(--accent);font-size:0.9em;font-weight:600;">${{i18n.digital}}</div>`;
  filledDg.forEach(([label, key]) => {{
    idEl.innerHTML += `<div class="info-row"><span class="key">${{label}}</span><span class="val">${{getVal(basicInfo, key)}}</span></div>`;
  }});
}}

if (!idEl.innerHTML) idEl.innerHTML = `<p style="color:var(--text-dim)">${{i18n.noDataChat}}</p>`;

// ---- Personality Tags ----
const psEl = document.getElementById('personality-tags');
let psHtml = '';
if (personality.mbti) psHtml += `<span class="tag green">${{personality.mbti}}</span>`;
(personality.traits || []).forEach(t => psHtml += `<span class="tag">${{t}}</span>`);
(personality.values || []).forEach(v => psHtml += `<span class="tag yellow">${{v}}</span>`);
if (personality.decision_style) psHtml += `<span class="tag green">${{i18n.decision}}: ${{personality.decision_style}}</span>`;

// Behavior patterns
const filledBh = bhFields.filter(([, key]) => personality[key]);
if (filledBh.length) {{
  psHtml += `<div style="margin:10px 0 6px;color:var(--text-dim);font-size:0.85em;">${{i18n.behavior}}</div>`;
  filledBh.forEach(([label, key]) => psHtml += `<span class="tag green">${{label}}: ${{personality[key]}}</span>`);
}}

// Social style
const filledSo = soFields.filter(([, key]) => personality[key]);
if (filledSo.length) {{
  psHtml += `<div style="margin:10px 0 6px;color:var(--text-dim);font-size:0.85em;">${{i18n.socialStyle}}</div>`;
  filledSo.forEach(([label, key]) => psHtml += `<span class="tag">${{label}}: ${{personality[key]}}</span>`);
}}

// Drivers
if (personality.motivation_drivers?.length) {{
  psHtml += `<div style="margin:10px 0 6px;color:var(--text-dim);font-size:0.85em;">${{i18n.drivers}}</div>`;
  personality.motivation_drivers.forEach(d => psHtml += `<span class="tag red">${{d}}</span>`);
}}

psEl.innerHTML = psHtml || `<p style="color:var(--text-dim)">${{i18n.noData}}</p>`;

// ---- Big Five Radar Chart ----
const bf5 = Object.entries(bigFive);
if (bf5.some(([,v]) => v > 0)) {{
  new Chart(document.getElementById('big5Chart'), {{
    type: 'radar',
    data: {{
      labels: bf5.map(([k]) => k),
      datasets: [{{
        data: bf5.map(([,v]) => v),
        backgroundColor: 'rgba(124, 91, 245, 0.2)',
        borderColor: '#7c5bf5',
        pointBackgroundColor: '#7c5bf5',
        borderWidth: 2
      }}]
    }},
    options: {{
      responsive: true,
      maintainAspectRatio: false,
      plugins: {{ legend: {{ display: false }} }},
      scales: {{ r: {{
        grid: {{ color: 'rgba(255,255,255,0.08)' }},
        angleLines: {{ color: 'rgba(255,255,255,0.08)' }},
        pointLabels: {{ color: '#e8e8f0', font: {{ size: 13 }} }},
        ticks: {{ display: false }},
        min: 0, max: 100
      }} }}
    }}
  }});
}}

// ---- Language Fingerprint ----
const langEl = document.getElementById('language-section');
let langHtml = '';
if (language.catchphrases?.length) {{
  langHtml += `<h3 style="margin-bottom:8px;font-size:1em;">${{i18n.catchphrases}}</h3>`;
  language.catchphrases.forEach(p => langHtml += `<span class="tag">"${{p}}"</span>`);
}}
if (language.sentence_patterns?.length) {{
  langHtml += `<h3 style="margin:16px 0 8px;font-size:1em;">${{i18n.sentencePatterns}}</h3>`;
  language.sentence_patterns.forEach(s => langHtml += `<div class="quote">${{s}}</div>`);
}}
if (language.examples?.length) {{
  langHtml += `<h3 style="margin:16px 0 8px;font-size:1em;">${{i18n.speechSamples}}</h3>`;
  language.examples.slice(0, 5).forEach(e => langHtml += `<div class="quote">${{e}}</div>`);
}}
const filledSt = stFields.filter(([, key]) => language[key]);
if (filledSt.length) {{
  langHtml += '<div style="margin-top:12px;">';
  filledSt.forEach(([label, key]) => langHtml += `<span class="tag green">${{label}}: ${{language[key]}}</span>`);
  langHtml += '</div>';
}}

// Deep Language Fingerprint
let deepLangHtml = '';
if (language.filler_words?.length) {{
  deepLangHtml += `<h3 style="margin:16px 0 8px;font-size:1em;">${{i18n.fillerWords}}</h3>`;
  language.filler_words.forEach(w => deepLangHtml += `<span class="tag">${{w}}</span>`);
}}
if (language.dialect_features?.length) {{
  deepLangHtml += `<h3 style="margin:16px 0 8px;font-size:1em;">${{i18n.dialect}}</h3>`;
  language.dialect_features.forEach(f => deepLangHtml += `<span class="tag yellow">${{f}}</span>`);
}}
if (language.agreement_expressions?.length) {{
  deepLangHtml += `<h3 style="margin:16px 0 8px;font-size:1em;">${{i18n.agreeExpr}}</h3>`;
  language.agreement_expressions.forEach(e => deepLangHtml += `<span class="tag green">${{e}}</span>`);
}}
if (language.disagreement_expressions?.length) {{
  deepLangHtml += `<h3 style="margin:16px 0 8px;font-size:1em;">${{i18n.disagreeExpr}}</h3>`;
  language.disagreement_expressions.forEach(e => deepLangHtml += `<span class="tag red">${{e}}</span>`);
}}
const filledDl = dlFields.filter(([, key]) => language[key]);
if (filledDl.length) {{
  deepLangHtml += `<h3 style="margin:16px 0 8px;font-size:1em;">${{i18n.deepFp}}</h3>`;
  filledDl.forEach(([label, key]) => deepLangHtml += `<span class="tag">${{label}}: ${{language[key]}}</span>`);
}}

langHtml += deepLangHtml;
langEl.innerHTML = langHtml || `<p style="color:var(--text-dim)">${{i18n.noLangData}}</p>`;

// ---- Topic Cloud ----
const tcEl = document.getElementById('topic-cloud');
const sentimentColors = {{positive:'green', negative:'red', neutral:'', mixed:'yellow'}};
const maxFreq = Math.max(...topicsData.map(t => t.frequency), 1);
topicsData.forEach(t => {{
  const size = 0.8 + (t.frequency / maxFreq) * 0.8;
  const cls = sentimentColors[t.sentiment] || '';
  tcEl.innerHTML += `<span class="topic-item tag ${{cls}}" style="font-size:${{size}}em">${{t.name}} (${{t.frequency}})</span>`;
}});
if (!topicsData.length) tcEl.innerHTML = `<p style="color:var(--text-dim)">${{i18n.noTopicData}}</p>`;

// ---- Emotional Patterns ----
const emoEl = document.getElementById('emotional-section');
let emoHtml = '';
emotionalData.forEach(e => {{
  const label = emoLabels[e.emotion] || e.emotion;
  emoHtml += `<div style="margin-bottom:12px;"><strong>${{label}}</strong><br>`;
  e.triggers.forEach(t => emoHtml += `<span class="tag" style="margin-top:4px;">${{t}}</span>`);
  emoHtml += '</div>';
}});
emoEl.innerHTML = emoHtml || `<p style="color:var(--text-dim)">${{i18n.noEmotionData}}</p>`;

// ---- Relationships ----
const pplEl = document.getElementById('people-section');
if (peopleData.length) {{
  peopleData.forEach(p => {{
    const initial = (p.name || '?')[0];
    pplEl.innerHTML += `<div class="person-card">
      <div class="person-avatar">${{initial}}</div>
      <div><strong>${{p.name}}</strong>${{p.relationship ? ' · ' + p.relationship : ''}}
      ${{p.description ? '<br><span style="color:var(--text-dim);font-size:0.9em;">' + p.description + '</span>' : ''}}</div>
    </div>`;
  }});
}} else {{
  pplEl.innerHTML = `<p style="color:var(--text-dim)">${{i18n.noPeopleData}}</p>`;
}}

// ---- Memory Fragments ----
const epEl = document.getElementById('episodes-section');
if (episodes.length) {{
  episodes.forEach(ep => {{
    epEl.innerHTML += `<div class="timeline-item">
      <strong>${{ep.event || ''}}</strong>
      ${{ep.emotion ? ' <span class="tag" style="font-size:0.8em;">' + ep.emotion + '</span>' : ''}}
      ${{ep.context ? '<br><span style="color:var(--text-dim);font-size:0.9em;">' + ep.context + '</span>' : ''}}
    </div>`;
  }});
}} else {{
  epEl.innerHTML = `<p style="color:var(--text-dim)">${{i18n.noMemoryData}}</p>`;
}}
</script>

</body>
</html>"""

    if output_path:
        output = Path(output_path)
        output.parent.mkdir(parents=True, exist_ok=True)
        with open(output, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"✅ Soul report generated ({lang}): {output}")
    else:
        print(html)

    return html


def main():
    default_soul_dir = str(Path.home() / ".skills_data" / "soul-archive")
    parser = argparse.ArgumentParser(description="🧬 Soul Report Generator (Multi-language)")
    parser.add_argument("--soul-dir", default=default_soul_dir,
                        help=f"Soul data directory path (default: {default_soul_dir})")
    parser.add_argument("--output", help="Output HTML file path")
    parser.add_argument("--lang", choices=["zh", "en"], default=None,
                        help="Report language: zh (Chinese) or en (English). "
                             "Auto-detected from user name if not specified.")
    parser.add_argument("--password", help="Encryption password (if encryption is enabled)")

    args = parser.parse_args()
    archive = SoulArchive(args.soul_dir)

    if not archive.is_initialized():
        print("❌ Soul archive not initialized. Run soul_init.py first.")
        sys.exit(1)

    # Auto-initialize crypto if encryption is enabled
    config = archive.load_config()
    if config.get("encryption"):
        archive.init_crypto_from_config(password=args.password)

    output = args.output or str(archive.root / "reports" / "soul_report.html")
    generate_html_report(archive, output, lang=args.lang)


if __name__ == "__main__":
    main()
