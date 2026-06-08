#!/usr/bin/env python3
"""
🧬 Soul Archive Initializer (Cross-platform)
Create ~/.skills_data/soul-archive/ data directory and default configuration files.

The soul data is stored under the current user's home directory (~/.skills_data/soul-archive/)
so it can be accessed across different IDEs, AI tools, and workspaces on the same machine.

Usage:
  python soul_init.py [--soul-dir /custom/path]
  python3 soul_init.py

Works on: macOS, Linux, Windows
"""

import argparse
import base64
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_SOUL_DIR = Path.home() / ".skills_data" / "soul-archive"


def now_iso() -> str:
    """Current time in ISO 8601 format."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S+00:00")


def write_json(path: Path, data: dict):
    """Write JSON file with UTF-8 encoding."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    parser = argparse.ArgumentParser(description="🧬 灵魂存档初始化")
    parser.add_argument("--soul-dir", type=Path, default=DEFAULT_SOUL_DIR,
                        help=f"灵魂数据目录路径（默认: {DEFAULT_SOUL_DIR}）")
    parser.add_argument("--enable-encryption", action="store_true",
                        help="启用数据加密（AES-256-GCM）")
    args = parser.parse_args()

    soul_dir = args.soul_dir

    # Check if already initialized
    if (soul_dir / "profile.json").exists():
        print(f"⚠️  灵魂存档已存在于 {soul_dir}")
        print(f"   如需重新初始化，请先删除 {soul_dir} 目录")
        return

    print("🧬 正在初始化灵魂存档...")
    print(f"   路径: {soul_dir}")

    now = now_iso()

    # Create directory structure
    dirs = [
        soul_dir / "identity",
        soul_dir / "memory" / "episodic",
        soul_dir / "memory" / "semantic",
        soul_dir / "memory" / "emotional",
        soul_dir / "style",
        soul_dir / "voice" / "samples",
        soul_dir / "relationships",
        soul_dir / "reports",
        soul_dir / "agent" / "episodes",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)

    # profile.json
    write_json(soul_dir / "profile.json", {
        "soul_version": "1.0",
        "created_at": now,
        "last_updated": now,
        "total_conversations": 0,
        "total_extractions": 0,
        "completeness_score": 0.0,
        "dimensions": {
            "identity": 0.0,
            "personality": 0.0,
            "language_style": 0.0,
            "knowledge": 0.0,
            "memory": 0.0,
            "relationships": 0.0,
            "voice": 0.0
        }
    })

    # config.json
    config_data = {
        "privacy_level": "standard",
        "auto_extract": True,
        "extract_dimensions": {
            "identity": True,
            "personality": True,
            "language_style": True,
            "knowledge": True,
            "episodic_memory": True,
            "emotional_patterns": True,
            "relationships": False,
            "voice": False
        },
        "sensitive_topics_filter": True,
        "require_confirmation_for": ["health", "finance", "intimate_relationships"],
        "data_retention_days": None,
        "encryption": False,
        "auto_reflect": True,
        "agent_self_improvement": {
            "enabled": True,
            "auto_reflect_on_completion": True,
            "auto_critique_on_correction": True,
            "pattern_extraction": True
        }
    }

    # Handle encryption setup
    crypto = None
    if args.enable_encryption:
        sys.path.insert(0, str(Path(__file__).parent))
        from soul_crypto import SoulCrypto, prompt_password, encrypt_archive

        print()
        print("🔐 正在设置数据加密...")
        print("   ⚠️  请牢记此密码！密码丢失将无法恢复数据，没有后门。")
        print()
        password = prompt_password(confirm=True)

        salt = SoulCrypto.generate_salt()
        crypto_inst = SoulCrypto(password, salt)

        config_data["encryption"] = True
        config_data["encryption_algorithm"] = "AES-256-GCM"
        config_data["encryption_key_derivation"] = "PBKDF2-SHA256"
        config_data["encryption_salt"] = base64.b64encode(salt).decode("ascii")
        config_data["encryption_verify"] = crypto_inst.create_verify_token()
        crypto = crypto_inst

    write_json(soul_dir / "config.json", config_data)

    # identity/basic_info.json
    write_json(soul_dir / "identity" / "basic_info.json", {
        "name": None, "nickname": None, "age": None, "birth_year": None,
        "gender": None, "location": None, "hometown": None,
        "occupation": None, "company": None, "education": None,
        "languages": [], "hobbies": [], "self_description": None, "life_motto": None,
        "daily_routine": None, "sleep_schedule": None,
        "food_preferences": [], "food_dislikes": [],
        "music_taste": [], "movie_taste": [], "book_taste": [],
        "travel_preferences": None, "pet_preference": None,
        "aesthetic_style": None, "spending_style": None,
        "online_personas": [], "favorite_apps": [], "social_platforms": [],
        "digital_habits": None, "tech_proficiency": None,
        "_meta": {}
    })

    # identity/personality.json
    write_json(soul_dir / "identity" / "personality.json", {
        "mbti": None,
        "big_five": {
            "openness": None, "conscientiousness": None,
            "extraversion": None, "agreeableness": None, "neuroticism": None
        },
        "traits": [], "values": [],
        "decision_style": None, "communication_preference": None,
        "strengths": [], "weaknesses": [],
        "risk_tolerance": None, "procrastination_level": None,
        "perfectionism_level": None, "planning_style": None,
        "learning_style": None, "work_style": None,
        "social_energy": None, "group_role": None,
        "trust_building": None, "conflict_approach": None,
        "stress_response": None, "motivation_drivers": [], "growth_areas": [],
        "_meta": {}
    })

    # style/language.json
    write_json(soul_dir / "style" / "language.json", {
        "catchphrases": [], "sentence_patterns": [],
        "preferred_words": [], "avoided_words": [],
        "emoji_usage": {"frequency": "unknown", "favorites": []},
        "punctuation_habits": {},
        "formality_level": None, "verbosity": None,
        "humor_style": None, "response_length_preference": None,
        "thinking_expression": None, "examples": [],
        "dialect_features": [], "filler_words": [],
        "persuasion_style": None, "storytelling_style": None,
        "question_style": None, "agreement_expressions": [],
        "disagreement_expressions": [],
        "greeting_style": None, "farewell_style": None,
        "typing_habits": None,
        "_meta": {}
    })

    # style/communication.json
    write_json(soul_dir / "style" / "communication.json", {
        "directness": None, "logic_vs_emotion": None,
        "detail_level": None, "listening_style": None,
        "conflict_style": None, "encouragement_style": None,
        "criticism_style": None, "_meta": {}
    })

    # memory/semantic/topics.json
    write_json(soul_dir / "memory" / "semantic" / "topics.json", {
        "topics": [], "_meta": {}
    })

    # memory/semantic/knowledge.json
    write_json(soul_dir / "memory" / "semantic" / "knowledge.json", {
        "domains": [], "skills": [], "expertise_level": {}, "_meta": {}
    })

    # memory/emotional/patterns.json
    write_json(soul_dir / "memory" / "emotional" / "patterns.json", {
        "triggers": {
            "joy": [], "anger": [], "sadness": [], "anxiety": [],
            "excitement": [], "nostalgia": [], "pride": [], "gratitude": [],
            "frustration": [], "curiosity": [], "peace": [], "guilt": []
        },
        "expression_style": None, "emotional_range": None,
        "emotional_awareness": None, "empathy_level": None,
        "coping_mechanisms": [], "comfort_activities": [],
        "celebration_style": None, "_meta": {}
    })

    # relationships/people.json
    write_json(soul_dir / "relationships" / "people.json", {
        "people": [], "_meta": {}
    })

    # voice/voice_profile.json
    write_json(soul_dir / "voice" / "voice_profile.json", {
        "description": None, "pitch": None, "speed": None,
        "accent": None, "sample_count": 0, "_meta": {}
    })

    # agent/patterns.json — AI 自我学习：抽象行为模式
    write_json(soul_dir / "agent" / "patterns.json", {
        "patterns": {},
        "_meta": {"description": "AI behavioral patterns learned from experience"}
    })

    # agent/corrections.jsonl — AI 自我批评日志（空文件）
    corrections = soul_dir / "agent" / "corrections.jsonl"
    if not corrections.exists():
        corrections.touch()

    # agent/reflections.jsonl — AI 自我反思日志（空文件）
    reflections = soul_dir / "agent" / "reflections.jsonl"
    if not reflections.exists():
        reflections.touch()

    # soul_changelog.jsonl (empty)
    changelog = soul_dir / "soul_changelog.jsonl"
    if not changelog.exists():
        changelog.touch()

    # .gitignore
    gitignore = soul_dir / ".gitignore"
    gitignore.write_text(
        "# Soul archive data — highly private, never commit to VCS\n*\n!.gitignore\n",
        encoding="utf-8"
    )

    print()
    print("✅ 灵魂存档初始化完成！")
    print()
    print(f"   📂 数据目录: {soul_dir}")
    print(f"   📋 配置文件: {soul_dir / 'config.json'}")
    print(f"   🔒 隐私提示: 数据存储在用户主目录下，不会进入任何 git 仓库")

    # Encrypt all data files if encryption is enabled
    if crypto is not None:
        encrypted_files = encrypt_archive(soul_dir, crypto)
        if encrypted_files:
            print(f"   🔐 加密已启用: {len(encrypted_files)} 个数据文件已加密 (AES-256-GCM)")
        else:
            print(f"   🔐 加密已启用: 数据文件将在写入时自动加密")
    else:
        print(f"   💡 提示: 可通过 --enable-encryption 启用数据加密")

    print()
    print("   下一步:")
    print('   1. 开始与 AI 对话，灵魂存档会静默采集你的信息')
    print('   2. 随时说 "灵魂报告" 查看你的人格画像')
    print('   3. 说 "灵魂对话" 让你的克隆体跟别人聊天')


if __name__ == "__main__":
    main()
