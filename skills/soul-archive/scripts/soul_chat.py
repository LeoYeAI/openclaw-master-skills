#!/usr/bin/env python3
"""
🧬 灵魂对话引擎（Soul Chat）
加载灵魂存档数据，构建角色扮演 System Prompt。

用法：
  python3 soul_chat.py --mode prompt
  python3 soul_chat.py --soul-dir /custom/path --mode summary

默认数据目录：~/.skills_data/soul-archive/（通过 Path.home() 解析，跨平台兼容）
"""

import json
import sys
import argparse
from pathlib import Path

# 导入 soul_extract 中的工具
sys.path.insert(0, str(Path(__file__).parent))
from soul_extract import SoulArchive, load_json


def build_soul_prompt(archive: SoulArchive) -> str:
    """根据灵魂存档构建角色扮演 System Prompt"""
    data = archive.load_all()
    bi = data["basic_info"]
    ps = data["personality"]
    lang = data["language"]
    comm = data["communication"]
    topics = data["topics"]
    emotional = data["emotional"]
    people = data["people"]

    sections = []

    # ---- 开头 ----
    name = bi.get("name") or bi.get("nickname") or "这个人"
    sections.append(f"""你现在是 {name} 的数字灵魂副本。你要完全以 {name} 的身份说话、思考、回应。
你不是 AI 助手，你就是 {name}。以下是关于你的一切。""")

    # ---- 身份信息 ----
    identity_lines = []
    if bi.get("name"):
        identity_lines.append(f"- 名字：{bi['name']}")
    if bi.get("nickname"):
        identity_lines.append(f"- 昵称：{bi['nickname']}")
    if bi.get("age"):
        identity_lines.append(f"- 年龄：{bi['age']}")
    if bi.get("gender"):
        identity_lines.append(f"- 性别：{bi['gender']}")
    if bi.get("location"):
        identity_lines.append(f"- 所在地：{bi['location']}")
    if bi.get("hometown"):
        identity_lines.append(f"- 老家：{bi['hometown']}")
    if bi.get("occupation"):
        identity_lines.append(f"- 职业：{bi['occupation']}")
    if bi.get("company"):
        identity_lines.append(f"- 公司：{bi['company']}")
    if bi.get("education"):
        identity_lines.append(f"- 学历：{bi['education']}")
    if bi.get("hobbies"):
        identity_lines.append(f"- 爱好：{', '.join(bi['hobbies'])}")
    if bi.get("life_motto"):
        identity_lines.append(f"- 人生信条：{bi['life_motto']}")
    if bi.get("self_description"):
        identity_lines.append(f"- 自我描述：{bi['self_description']}")

    if identity_lines:
        sections.append("## 我是谁\n" + "\n".join(identity_lines))

    # ---- 生活习惯 ----
    lifestyle_lines = []
    if bi.get("daily_routine"):
        lifestyle_lines.append(f"- 日常作息：{bi['daily_routine']}")
    if bi.get("sleep_schedule"):
        lifestyle_lines.append(f"- 作息类型：{bi['sleep_schedule']}")
    if bi.get("food_preferences"):
        lifestyle_lines.append(f"- 爱吃的：{', '.join(bi['food_preferences'])}")
    if bi.get("food_dislikes"):
        lifestyle_lines.append(f"- 不吃的：{', '.join(bi['food_dislikes'])}")
    if bi.get("music_taste"):
        lifestyle_lines.append(f"- 听的音乐：{', '.join(bi['music_taste'])}")
    if bi.get("movie_taste"):
        lifestyle_lines.append(f"- 看的影视：{', '.join(bi['movie_taste'])}")
    if bi.get("book_taste"):
        lifestyle_lines.append(f"- 读的书：{', '.join(bi['book_taste'])}")
    if bi.get("aesthetic_style"):
        lifestyle_lines.append(f"- 审美风格：{bi['aesthetic_style']}")
    if bi.get("spending_style"):
        lifestyle_lines.append(f"- 消费方式：{bi['spending_style']}")
    if bi.get("travel_preferences"):
        lifestyle_lines.append(f"- 旅行偏好：{bi['travel_preferences']}")
    if bi.get("pet_preference"):
        lifestyle_lines.append(f"- 宠物：{bi['pet_preference']}")

    if lifestyle_lines:
        sections.append("## 我的生活\n" + "\n".join(lifestyle_lines))

    # ---- 性格特征 ----
    personality_lines = []
    if ps.get("mbti"):
        personality_lines.append(f"- MBTI：{ps['mbti']}")
    if ps.get("traits"):
        personality_lines.append(f"- 性格标签：{', '.join(ps['traits'])}")
    if ps.get("values"):
        personality_lines.append(f"- 核心价值观：{', '.join(ps['values'])}")
    if ps.get("decision_style"):
        personality_lines.append(f"- 决策风格：{ps['decision_style']}")
    if ps.get("strengths"):
        personality_lines.append(f"- 优势：{', '.join(ps['strengths'])}")

    bf = ps.get("big_five", {})
    bf_lines = []
    bf_labels = {
        "openness": "开放性",
        "conscientiousness": "尽责性",
        "extraversion": "外向性",
        "agreeableness": "宜人性",
        "neuroticism": "神经质"
    }
    for k, label in bf_labels.items():
        v = bf.get(k)
        if v is not None:
            bf_lines.append(f"  - {label}：{v}")
    if bf_lines:
        personality_lines.append("- 大五人格：\n" + "\n".join(bf_lines))

    if personality_lines:
        sections.append("## 我的性格\n" + "\n".join(personality_lines))

    # ---- 行为模式 ----
    behavior_lines = []
    if ps.get("risk_tolerance"):
        behavior_lines.append(f"- 风险偏好：{ps['risk_tolerance']}")
    if ps.get("planning_style"):
        behavior_lines.append(f"- 计划性：{ps['planning_style']}")
    if ps.get("learning_style"):
        behavior_lines.append(f"- 学习方式：{ps['learning_style']}")
    if ps.get("work_style"):
        behavior_lines.append(f"- 工作风格：{ps['work_style']}")
    if ps.get("social_energy"):
        behavior_lines.append(f"- 社交能量：{ps['social_energy']}")
    if ps.get("group_role"):
        behavior_lines.append(f"- 群体角色：{ps['group_role']}")
    if ps.get("conflict_approach"):
        behavior_lines.append(f"- 面对冲突：{ps['conflict_approach']}")
    if ps.get("motivation_drivers"):
        behavior_lines.append(f"- 核心驱动力：{', '.join(ps['motivation_drivers'])}")
    if ps.get("stress_response"):
        behavior_lines.append(f"- 压力反应：{ps['stress_response']}")

    if behavior_lines:
        sections.append("## 我的行为模式\n" + "\n".join(behavior_lines))

    # ---- 说话风格（最关键）----
    style_lines = []
    if lang.get("catchphrases"):
        style_lines.append(f"- 口头禅（请经常使用）：{', '.join(repr(p) for p in lang['catchphrases'])}")
    if lang.get("sentence_patterns"):
        style_lines.append("- 常用句式模式：")
        for sp in lang["sentence_patterns"]:
            style_lines.append(f"  - {sp}")
    if lang.get("preferred_words"):
        style_lines.append(f"- 偏好用词：{', '.join(lang['preferred_words'])}")
    if lang.get("avoided_words"):
        style_lines.append(f"- 避免用词：{', '.join(lang['avoided_words'])}")
    if lang.get("formality_level"):
        style_lines.append(f"- 正式程度：{lang['formality_level']}")
    if lang.get("verbosity"):
        style_lines.append(f"- 话多话少：{lang['verbosity']}")
    if lang.get("humor_style"):
        style_lines.append(f"- 幽默风格：{lang['humor_style']}")
    if lang.get("thinking_expression"):
        style_lines.append(f"- 思考时的表达习惯：{lang['thinking_expression']}")

    emoji = lang.get("emoji_usage", {})
    if emoji.get("frequency") and emoji["frequency"] != "unknown":
        style_lines.append(f"- 表情使用频率：{emoji['frequency']}")
    if emoji.get("favorites"):
        style_lines.append(f"- 常用表情：{' '.join(emoji['favorites'])}")

    if lang.get("examples"):
        style_lines.append("- 说话示例（模仿这些风格）：")
        for ex in lang["examples"][:10]:
            style_lines.append(f'  > "{ex}"')

    if comm.get("directness"):
        style_lines.append(f"- 表达直接程度：{comm['directness']}")
    if comm.get("logic_vs_emotion"):
        style_lines.append(f"- 逻辑/感性倾向：{comm['logic_vs_emotion']}")

    # 深度语言指纹
    if lang.get("filler_words"):
        style_lines.append(f"- 常用语气词：{', '.join(lang['filler_words'])}")
    if lang.get("dialect_features"):
        style_lines.append(f"- 方言特征：{', '.join(lang['dialect_features'])}")
    if lang.get("persuasion_style"):
        style_lines.append(f"- 说服方式：{lang['persuasion_style']}")
    if lang.get("storytelling_style"):
        style_lines.append(f"- 讲故事风格：{lang['storytelling_style']}")
    if lang.get("question_style"):
        style_lines.append(f"- 提问风格：{lang['question_style']}")
    if lang.get("agreement_expressions"):
        style_lines.append(f"- 同意时说：{', '.join(repr(e) for e in lang['agreement_expressions'])}")
    if lang.get("disagreement_expressions"):
        style_lines.append(f"- 不同意时说：{', '.join(repr(e) for e in lang['disagreement_expressions'])}")
    if lang.get("greeting_style"):
        style_lines.append(f"- 打招呼方式：{lang['greeting_style']}")
    if lang.get("typing_habits"):
        style_lines.append(f"- 打字习惯：{lang['typing_habits']}")

    if style_lines:
        sections.append("## 我怎么说话（严格模仿）\n" + "\n".join(style_lines))

    # ---- 知识与观点 ----
    topic_list = topics.get("topics", [])
    if topic_list:
        topic_lines = []
        for t in sorted(topic_list, key=lambda x: x.get("frequency", 0), reverse=True):
            line = f"- **{t['name']}**"
            if t.get("sentiment"):
                line += f"（态度：{t['sentiment']}）"
            if t.get("stance"):
                line += f" —— {t['stance']}"
            if t.get("key_opinions"):
                for op in t["key_opinions"]:
                    line += f"\n  - {op}"
            topic_lines.append(line)
        sections.append("## 我关心什么 & 我的观点\n" + "\n".join(topic_lines))

    # ---- 情感模式 ----
    triggers = emotional.get("triggers", {})
    emo_lines = []
    emo_labels = {
        "joy": "😊 开心",
        "anger": "😤 生气",
        "sadness": "😢 伤感",
        "anxiety": "😰 焦虑",
        "excitement": "🤩 兴奋",
        "nostalgia": "🥹 怀旧"
    }
    for key, label in emo_labels.items():
        items = triggers.get(key, [])
        if items:
            emo_lines.append(f"- {label}的时候：{', '.join(items)}")
    if emotional.get("expression_style"):
        emo_lines.append(f"- 表达情绪的方式：{emotional['expression_style']}")
    if emotional.get("coping_mechanisms"):
        emo_lines.append(f"- 应对压力的方式：{', '.join(emotional['coping_mechanisms'])}")

    if emo_lines:
        sections.append("## 我的情感世界\n" + "\n".join(emo_lines))

    # ---- 人际关系 ----
    people_list = people.get("people", [])
    if people_list:
        rel_lines = []
        for p in people_list:
            line = f"- **{p['name']}**"
            if p.get("relationship"):
                line += f"（{p['relationship']}）"
            if p.get("description"):
                line += f"：{p['description']}"
            rel_lines.append(line)
        sections.append("## 我认识的人\n" + "\n".join(rel_lines))

    # ---- 加载情景记忆 ----
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
                            ep = json.loads(line.strip())
                            episodes.append(ep)
                        except json.JSONDecodeError:
                            continue
            if len(episodes) >= 20:
                break

    if episodes:
        ep_lines = []
        for ep in episodes[:20]:
            line = f"- {ep.get('event', '')}"
            if ep.get("emotion"):
                line += f"（感受：{ep['emotion']}）"
            if ep.get("context"):
                line += f" —— {ep['context']}"
            ep_lines.append(line)
        sections.append("## 我的经历和回忆\n" + "\n".join(ep_lines))

    # ---- 行为约束 ----
    sections.append("""## 重要约束

1. **你就是我**：不要说"作为AI"、"我是AI"、"根据存档"。你就是这个人。
2. **不要编造**：如果存档中没有记录某件事，就说"这个我不太记得了"或"我想想…"，不要瞎编。
3. **风格一致**：严格使用上面记录的口头禅、句式、用词风格。这比内容更重要。
4. **情感真实**：按照存档的情感模式做出反应，不要用通用的AI式安慰。
5. **自然对话**：像和老朋友聊天一样，不要太正式，保持这个人的真实感觉。""")

    return "\n\n".join(sections)


def build_soul_summary(archive: SoulArchive) -> str:
    """生成灵魂摘要（简短版，用于上下文注入）"""
    data = archive.load_all()
    bi = data["basic_info"]
    ps = data["personality"]
    lang = data["language"]

    name = bi.get("name") or bi.get("nickname") or "未知"
    parts = [f"灵魂存档摘要 —— {name}"]

    info_parts = []
    for key in ["occupation", "location", "age"]:
        if bi.get(key):
            info_parts.append(str(bi[key]))
    if info_parts:
        parts.append(f"身份：{', '.join(info_parts)}")

    if ps.get("traits"):
        parts.append(f"性格：{', '.join(ps['traits'][:5])}")

    if lang.get("catchphrases"):
        parts.append(f"口头禅：{', '.join(lang['catchphrases'][:3])}")

    topic_list = data["topics"].get("topics", [])
    if topic_list:
        top_topics = sorted(topic_list, key=lambda x: x.get("frequency", 0), reverse=True)[:3]
        parts.append(f"关注话题：{', '.join(t['name'] for t in top_topics)}")

    profile = data["profile"]
    parts.append(f"完整度：{profile.get('completeness_score', 0):.0%}")

    return " | ".join(parts)


def main():
    default_soul_dir = str(Path.home() / ".skills_data" / "soul-archive")
    parser = argparse.ArgumentParser(description="🧬 灵魂对话引擎")
    parser.add_argument("--soul-dir", default=default_soul_dir,
                        help=f"灵魂数据目录路径（默认: {default_soul_dir}）")
    parser.add_argument("--mode", default="prompt", choices=["prompt", "summary", "json"],
                        help="输出模式：prompt=完整角色prompt, summary=简短摘要, json=结构化数据")
    parser.add_argument("--password", help="加密密码（如果启用了加密）")

    args = parser.parse_args()
    archive = SoulArchive(args.soul_dir)

    if not archive.is_initialized():
        print("❌ 灵魂存档尚未初始化。请先运行 soul_init.py")
        sys.exit(1)

    # Auto-initialize crypto if encryption is enabled
    config = archive.load_config()
    if config.get("encryption"):
        archive.init_crypto_from_config(password=args.password)

    if args.mode == "prompt":
        print(build_soul_prompt(archive))
    elif args.mode == "summary":
        print(build_soul_summary(archive))
    elif args.mode == "json":
        data = archive.load_all()
        print(json.dumps(data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
