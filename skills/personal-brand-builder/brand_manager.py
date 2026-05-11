#!/usr/bin/env python3
"""
brand_manager.py — Personal Brand Builder CLI
Commands: init, status, morning-brief, content, audit, proof, network, evening-review
"""

import argparse
import json
import os
import sys
from datetime import datetime, date

# ── Paths ─────────────────────────────────────────────────────────────────────
BRAND_DIR    = os.environ.get("BRAND_DIR", "/workspace/brand")
IDENTITY_F   = f"{BRAND_DIR}/identity.json"
PLATFORMS_D  = f"{BRAND_DIR}/platforms"
CONTENT_D    = f"{BRAND_DIR}/content"
NETWORK_D    = f"{BRAND_DIR}/network"
PROOF_D      = f"{BRAND_DIR}/proof"
AUDIT_F      = f"{BRAND_DIR}/AUDIT.md"
LEARNINGS_F  = "/workspace/.learnings/LEARNINGS.md"
ERRORS_F     = "/workspace/.learnings/ERRORS.md"

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")


# ── Helpers ───────────────────────────────────────────────────────────────────
def ensure_dirs():
    for d in [BRAND_DIR, PLATFORMS_D, CONTENT_D, NETWORK_D,
              f"{PROOF_D}/revenue", f"{PROOF_D}/testimonials",
              f"{PROOF_D}/milestones", f"{PROOF_D}/media",
              "/workspace/.learnings"]:
        os.makedirs(d, exist_ok=True)


def load_identity() -> dict:
    if not os.path.exists(IDENTITY_F):
        return {}
    with open(IDENTITY_F, encoding="utf-8") as f:
        return json.load(f)


def save_identity(data: dict):
    ensure_dirs()
    data["last_updated"] = date.today().isoformat()
    with open(IDENTITY_F, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def log_audit(message: str):
    ensure_dirs()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(AUDIT_F, "a", encoding="utf-8") as f:
        f.write(f"\n[{ts}] {message}")


def log_error(message: str):
    ensure_dirs()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(ERRORS_F, "a", encoding="utf-8") as f:
        f.write(f"\n[{ts}] {message}")


def notify_telegram(message: str):
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print(f"  [Telegram] Not configured — message: {message[:80]}")
        return
    try:
        import urllib.request, urllib.parse
        payload = json.dumps({"chat_id": chat_id, "text": message, "parse_mode": "Markdown"})
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload.encode(), headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10):
            pass
        print(f"  ✅ Telegram notification sent")
    except Exception as e:
        log_error(f"Telegram notification failed: {e}")
        print(f"  ⚠️  Telegram failed: {e}")


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_init(args):
    """Initialize brand identity."""
    print("\n🏆 Personal Brand Builder — Identity Setup\n")

    # Load template
    template_path = os.path.join(TEMPLATE_DIR, "identity.json")
    if os.path.exists(template_path):
        with open(template_path) as f:
            identity = json.load(f)
    else:
        identity = {}

    # Apply args if provided
    if args.name:
        identity["principal_name"] = args.name
    if args.positioning:
        identity.setdefault("positioning", {})["unique_angle"] = args.positioning
    if args.niches:
        identity["niches"] = [n.strip() for n in args.niches.split(",")]
    if args.platforms:
        identity["platforms"] = [p.strip() for p in args.platforms.split(",")]

    identity["setup_date"] = date.today().isoformat()

    ensure_dirs()
    save_identity(identity)

    # Copy platform config template
    plat_template = os.path.join(TEMPLATE_DIR, "platform_config.json")
    plat_dest = f"{PLATFORMS_D}/config.json"
    if os.path.exists(plat_template) and not os.path.exists(plat_dest):
        import shutil
        shutil.copy(plat_template, plat_dest)

    # Copy voice guide template
    voice_template = os.path.join(TEMPLATE_DIR, "voice_guide.md")
    voice_dest = f"{PLATFORMS_D}/voice_guide.md"
    if os.path.exists(voice_template) and not os.path.exists(voice_dest):
        import shutil
        shutil.copy(voice_template, voice_dest)

    # Initialize content queue
    queue_f = f"{CONTENT_D}/queue.json"
    if not os.path.exists(queue_f):
        with open(queue_f, "w") as f:
            json.dump({"queue": [], "generated": date.today().isoformat()}, f, indent=2)

    # Initialize network contacts
    contacts_f = f"{NETWORK_D}/contacts.json"
    if not os.path.exists(contacts_f):
        with open(contacts_f, "w") as f:
            json.dump({"contacts": [], "last_reviewed": date.today().isoformat()}, f, indent=2)

    log_audit("Brand identity initialized")
    print(f"✅ Brand identity initialized")
    print(f"   Identity: {IDENTITY_F}")
    print(f"   Platforms: {PLATFORMS_D}/config.json")
    print(f"   Voice guide: {PLATFORMS_D}/voice_guide.md")
    print(f"\n   Next: review {IDENTITY_F} and adjust positioning")
    print(f"   Then: python3 brand_manager.py status")


def cmd_status(args):
    """Show brand configuration status."""
    identity = load_identity()
    print("\n🏆 Personal Brand Builder — Status\n")

    # Identity
    name = identity.get("principal_name", "")
    print(f"  Principal:    {'✅ ' + name if name else '❌ not set — run init'}")
    print(f"  Identity:     {'✅ configured' if identity else '❌ missing — run init'}")
    print(f"  Niches:       {', '.join(identity.get('niches', [])) or '❌ not set'}")
    print(f"  Platforms:    {', '.join(identity.get('platforms', [])) or '❌ not set'}")

    # Files
    print(f"\n  Files:")
    files = {
        "identity.json":      IDENTITY_F,
        "platform config":    f"{PLATFORMS_D}/config.json",
        "voice guide":        f"{PLATFORMS_D}/voice_guide.md",
        "content queue":      f"{CONTENT_D}/queue.json",
        "network contacts":   f"{NETWORK_D}/contacts.json",
    }
    for label, path in files.items():
        exists = os.path.exists(path)
        print(f"    {'✅' if exists else '❌'} {label}")

    # Credentials
    print(f"\n  Credentials:")
    creds = {
        "TELEGRAM_BOT_TOKEN":    os.environ.get("TELEGRAM_BOT_TOKEN"),
        "TELEGRAM_CHAT_ID":      os.environ.get("TELEGRAM_CHAT_ID"),
        "TWITTER_API_KEY":       os.environ.get("TWITTER_API_KEY"),
        "TWITTER_ACCESS_TOKEN":  os.environ.get("TWITTER_ACCESS_TOKEN"),
    }
    for k, v in creds.items():
        configured = bool(v)
        tag = "Twitter/X automation" if "TWITTER" in k else "Notifications"
        print(f"    {'✅' if configured else '⚪'} {k} ({tag})")

    # Proof vault
    proof_count = 0
    if os.path.exists(PROOF_D):
        for root, _, files_in in os.walk(PROOF_D):
            proof_count += len(files_in)
    print(f"\n  Proof vault:  {proof_count} items")

    if not identity:
        print(f"\n  ⚡ Quick start: python3 brand_manager.py init")


def cmd_morning_brief(args):
    """Generate morning brief and queue first post."""
    identity = load_identity()
    if not identity:
        print("❌ Identity not configured — run: python3 brand_manager.py init")
        return

    today = date.today().strftime("%A %d %B %Y")
    name = identity.get("principal_name", "[PRINCIPAL_NAME]")
    pillars = identity.get("pillars", {})

    print(f"\n🌅 Morning Brief — {today}\n")

    # Determine today's pillar (rotate by day of week)
    pillar_rotation = {
        0: "pillar_1",  # Monday   → AI Automation
        1: "pillar_2",  # Tuesday  → Trading
        2: "pillar_3",  # Wednesday → Entrepreneurship
        3: "pillar_1",  # Thursday → AI Automation
        4: "pillar_4",  # Friday   → Behind the Scenes
        5: "pillar_2",  # Saturday → Trading
        6: "pillar_3",  # Sunday   → Entrepreneurship
    }
    today_pillar_key = pillar_rotation.get(date.today().weekday(), "pillar_1")
    today_pillar = pillars.get(today_pillar_key, {})

    print(f"  Today's pillar: {today_pillar.get('name', 'AI Automation')}")
    print(f"  Hook formula:   {today_pillar.get('hook_formula', 'N/A')}")
    print(f"  Goal:           {today_pillar.get('goal', 'N/A')}")

    # Check queue
    queue_f = f"{CONTENT_D}/queue.json"
    queue_count = 0
    if os.path.exists(queue_f):
        with open(queue_f) as f:
            q = json.load(f)
            queue_count = len(q.get("queue", []))
    print(f"\n  Content queue: {queue_count} items pending")

    # Check proof vault
    proof_count = sum(len(fs) for _, _, fs in os.walk(PROOF_D)) if os.path.exists(PROOF_D) else 0
    if proof_count == 0:
        print(f"  ⚠️  Proof vault empty — add results to /workspace/brand/proof/")

    log_audit(f"Morning brief generated — pillar: {today_pillar.get('name', 'N/A')}")
    notify_telegram(
        f"🌅 *Morning Brief — {today}*\n"
        f"Today's pillar: {today_pillar.get('name', 'AI Automation')}\n"
        f"Hook: {today_pillar.get('hook_formula', 'N/A')}\n"
        f"Queue: {queue_count} items"
    )
    print(f"\n  ✅ Brief complete")


def cmd_content(args):
    """Generate content ideas or plan the week."""
    identity = load_identity()
    if not identity:
        print("❌ Identity not configured — run init first")
        return

    if args.action == "plan-week":
        print("\n📅 Weekly Content Plan\n")
        schedule = {
            "Monday":    ("Podcast episode drops → clips", "pillar_1", "all"),
            "Tuesday":   ("YouTube tutorial → clips", "pillar_1", "youtube"),
            "Wednesday": ("LinkedIn deep article → repurpose as thread", "pillar_3", "linkedin"),
            "Thursday":  ("Case study or result reveal", "pillar_2", "twitter"),
            "Friday":    ("Community engagement + week recap", "pillar_4", "all"),
            "Saturday":  ("Behind the scenes or tool review", "pillar_4", "instagram"),
            "Sunday":    ("Week preview + content tease", "pillar_3", "twitter"),
        }
        for day, (content, pillar, platform) in schedule.items():
            print(f"  {day:12s} → {content}")
            print(f"              Pillar: {pillar} | Platform: {platform}")

        # Save to queue
        queue_f = f"{CONTENT_D}/queue.json"
        queue_data = {
            "queue": [
                {"day": day, "content": c, "pillar": p, "platform": pl, "status": "planned"}
                for day, (c, p, pl) in schedule.items()
            ],
            "generated": date.today().isoformat()
        }
        with open(queue_f, "w") as f:
            json.dump(queue_data, f, indent=2)

        log_audit("Weekly content plan generated")
        print(f"\n  ✅ Saved to {queue_f}")

    else:
        # Generate ideas for a specific platform + pillar
        platform = args.platform or "twitter"
        pillar = args.pillar or "ai-automation"
        fmt = args.format or "thread"

        pillars = identity.get("pillars", {})
        pillar_map = {
            "ai-automation": "pillar_1",
            "trading": "pillar_2",
            "entrepreneurship": "pillar_3",
            "behind-scenes": "pillar_4",
        }
        p_data = pillars.get(pillar_map.get(pillar, "pillar_1"), {})

        print(f"\n✍️  Content Brief — {platform.upper()} | {pillar} | {fmt}\n")
        print(f"  Hook formula: {p_data.get('hook_formula', 'N/A')}")
        print(f"  Goal:         {p_data.get('goal', 'N/A')}")
        print(f"\n  Ideas:")

        ideas = {
            "ai-automation": [
                "Show the build: 'I automated [task] in [X] hours — full walkthrough'",
                "Agent result: 'My AI agent generated €X this week — here's the log'",
                "Tool comparison: 'I tested 5 AI tools for [use case] — honest results'",
            ],
            "trading": [
                "Signal thread: 'Spotted a setup on [asset] — here's what I'm watching'",
                "Performance update: 'This week's P&L — what worked and what didn't'",
                "Framework: 'The 3 criteria I check before entering any trade'",
            ],
            "entrepreneurship": [
                "Monthly update: 'Month [X] — honest revenue breakdown'",
                "Lesson: 'The mistake that cost me €X (and how to avoid it)'",
                "System reveal: 'How I generate [outcome] without doing [task]'",
            ],
            "behind-scenes": [
                "Tool reveal: 'The tool I use for [task] that nobody talks about'",
                "Process: 'My actual daily workflow — no filters'",
                "Failure: 'What went wrong this week and what I changed'",
            ],
        }

        for i, idea in enumerate(ideas.get(pillar, ideas["ai-automation"]), 1):
            print(f"  {i}. {idea}")

        log_audit(f"Content ideas generated — {platform}/{pillar}/{fmt}")


def cmd_audit(args):
    """Run brand performance audit."""
    period = args.period or "weekly"
    print(f"\n📊 Brand Audit — {period.capitalize()}\n")

    identity = load_identity()
    name = identity.get("principal_name", "[PRINCIPAL_NAME]")

    # Count proof items
    proof_by_type = {}
    if os.path.exists(PROOF_D):
        for proof_type in ["revenue", "testimonials", "milestones", "media"]:
            type_dir = f"{PROOF_D}/{proof_type}"
            count = len(os.listdir(type_dir)) if os.path.exists(type_dir) else 0
            proof_by_type[proof_type] = count

    print(f"  Principal:    {name}")
    print(f"  Period:       {period}")
    print(f"\n  Proof Vault:")
    for proof_type, count in proof_by_type.items():
        icon = "✅" if count > 0 else "⚠️ "
        print(f"    {icon} {proof_type}: {count} items")

    # Check content queue
    queue_f = f"{CONTENT_D}/queue.json"
    queue_count = 0
    if os.path.exists(queue_f):
        with open(queue_f) as f:
            q = json.load(f)
            queue_count = len([x for x in q.get("queue", []) if x.get("status") == "planned"])

    # Check network
    contacts_f = f"{NETWORK_D}/contacts.json"
    contact_count = 0
    if os.path.exists(contacts_f):
        with open(contacts_f) as f:
            c = json.load(f)
            contact_count = len(c.get("contacts", []))

    print(f"\n  Content queue: {queue_count} planned items")
    print(f"  Network:       {contact_count} contacts tracked")

    # Recommendations
    print(f"\n  Recommendations:")
    if proof_by_type.get("revenue", 0) == 0:
        print(f"  ⚡ Add revenue proof: brand_manager.py proof --type revenue")
    if proof_by_type.get("testimonials", 0) == 0:
        print(f"  ⚡ Collect testimonials: ask 2 followers for feedback this week")
    if queue_count == 0:
        print(f"  ⚡ Plan content: brand_manager.py content --action plan-week")
    if contact_count == 0:
        print(f"  ⚡ Start networking: brand_manager.py network --action queue")

    log_audit(f"Audit completed — {period}")
    notify_telegram(
        f"📊 *Brand Audit — {period.capitalize()}*\n"
        f"Revenue proof: {proof_by_type.get('revenue', 0)} items\n"
        f"Testimonials: {proof_by_type.get('testimonials', 0)} items\n"
        f"Content queue: {queue_count} planned\n"
        f"Network: {contact_count} contacts"
    )
    print(f"\n  ✅ Audit complete")


def cmd_proof(args):
    """Log a proof item to the vault."""
    proof_type = args.type or "revenue"
    note = args.note or "Proof item added"

    ensure_dirs()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    proof_file = f"{PROOF_D}/{proof_type}/{ts}.json"

    entry = {
        "date": date.today().isoformat(),
        "type": proof_type,
        "note": note,
        "file": proof_file,
    }

    with open(proof_file, "w") as f:
        json.dump(entry, f, indent=2)

    log_audit(f"Proof added: {proof_type} — {note}")
    print(f"✅ Proof logged: {proof_file}")
    print(f"   Type: {proof_type}")
    print(f"   Note: {note}")


def cmd_network(args):
    """Manage networking targets."""
    action = args.action or "queue"

    if action == "queue":
        print("\n🤝 Networking Queue\n")
        print("  TIER 1 — Micro Influencers (1K-50K followers)")
        print("    → Engage genuinely for 2 weeks before outreach")
        print("    → DM with specific compliment + collaboration idea")
        print("")
        print("  TIER 2 — Mid Influencers (50K-500K followers)")
        print("    → Quote-tweet, mention, comment value for 30 days")
        print("    → Outreach only after they've noticed you")
        print("")
        print("  TIER 3 — Macro Influencers (500K+)")
        print("    → Long-term relationship building (3-6 months)")
        print("    → Through warm introductions from Tier 2")
        print("")
        print("  Use acquisition-master for outreach sequencing")
        log_audit("Network queue reviewed")

    elif action == "add":
        contacts_f = f"{NETWORK_D}/contacts.json"
        ensure_dirs()
        if os.path.exists(contacts_f):
            with open(contacts_f) as f:
                data = json.load(f)
        else:
            data = {"contacts": []}

        contact = {
            "name": args.name or "Unknown",
            "platform": args.platform or "twitter",
            "tier": args.tier or "1",
            "status": "to_engage",
            "added": date.today().isoformat(),
        }
        data["contacts"].append(contact)

        with open(contacts_f, "w") as f:
            json.dump(data, f, indent=2)

        print(f"✅ Contact added: {contact['name']} ({contact['platform']}, Tier {contact['tier']})")
        log_audit(f"Network contact added: {contact['name']}")


def cmd_evening_review(args):
    """Evening review — analyze day, queue tomorrow."""
    print("\n🌙 Evening Review\n")

    identity = load_identity()
    name = identity.get("principal_name", "[PRINCIPAL_NAME]")
    tomorrow = date.today().strftime("%A")

    print(f"  Principal: {name}")
    print(f"  ✅ Day complete")
    print(f"\n  Tomorrow: {tomorrow}")
    print(f"  Action: Run morning-brief at 07h30")

    # Check if any proof was added today
    today_str = date.today().isoformat()
    today_proof = 0
    if os.path.exists(PROOF_D):
        for root, _, files_in in os.walk(PROOF_D):
            for fname in files_in:
                if today_str.replace("-", "") in fname:
                    today_proof += 1

    print(f"\n  Proof added today: {today_proof} items")
    if today_proof == 0:
        print(f"  ⚡ Consider adding a proof item:")
        print(f"     brand_manager.py proof --type revenue --note 'Today summary'")

    log_audit("Evening review completed")
    notify_telegram(
        f"🌙 *Evening Review*\n"
        f"Day complete for {name}.\n"
        f"Proof added today: {today_proof} items\n"
        f"Tomorrow: morning-brief at 07h30"
    )
    print(f"\n  ✅ Evening review complete")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Personal Brand Builder — Authority at Scale"
    )
    sub = parser.add_subparsers(dest="command")

    # init
    p_init = sub.add_parser("init", help="Initialize brand identity")
    p_init.add_argument("--name",        help="Principal name")
    p_init.add_argument("--positioning", help="Positioning key (e.g. autonomous-wealth)")
    p_init.add_argument("--niches",      help="Comma-separated niches")
    p_init.add_argument("--platforms",   help="Comma-separated platforms")

    # status
    sub.add_parser("status", help="Show brand configuration status")

    # morning-brief
    sub.add_parser("morning-brief", help="Generate daily morning brief")

    # evening-review
    sub.add_parser("evening-review", help="Evening review and tomorrow prep")

    # content
    p_content = sub.add_parser("content", help="Generate content ideas or plan week")
    p_content.add_argument("--action",   choices=["plan-week", "generate"], default="generate")
    p_content.add_argument("--platform", choices=["twitter", "linkedin", "instagram", "youtube", "tiktok", "podcast"])
    p_content.add_argument("--pillar",   choices=["ai-automation", "trading", "entrepreneurship", "behind-scenes"])
    p_content.add_argument("--format",   choices=["thread", "post", "reel", "article", "video"])

    # audit
    p_audit = sub.add_parser("audit", help="Run brand performance audit")
    p_audit.add_argument("--period", choices=["daily", "weekly", "monthly"], default="weekly")

    # proof
    p_proof = sub.add_parser("proof", help="Log a proof item to the vault")
    p_proof.add_argument("--type", choices=["revenue", "testimonials", "milestones", "media"], default="revenue")
    p_proof.add_argument("--note", help="Description of the proof item")

    # network
    p_net = sub.add_parser("network", help="Manage networking targets")
    p_net.add_argument("--action", choices=["queue", "add"], default="queue")
    p_net.add_argument("--name",     help="Contact name (for --action add)")
    p_net.add_argument("--platform", help="Platform (for --action add)")
    p_net.add_argument("--tier",     help="Tier 1/2/3 (for --action add)")

    args = parser.parse_args()

    dispatch = {
        "init":           cmd_init,
        "status":         cmd_status,
        "morning-brief":  cmd_morning_brief,
        "evening-review": cmd_evening_review,
        "content":        cmd_content,
        "audit":          cmd_audit,
        "proof":          cmd_proof,
        "network":        cmd_network,
    }

    if args.command in dispatch:
        dispatch[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
