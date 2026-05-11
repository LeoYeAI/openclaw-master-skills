#!/usr/bin/env python3
"""
proof_manager.py — Proof Engine CLI
Commands: init, status, capture, add, vault, dashboard,
          story, content, opportunities, deploy,
          morning-brief, weekly-sync
"""

import argparse
import json
import os
import sys
from datetime import datetime, date

# ── Paths ─────────────────────────────────────────────────────────────────────
PROOF_DIR    = os.environ.get("PROOF_DIR", "/workspace/proof")
VAULT_DIR    = f"{PROOF_DIR}/vault"
DASHBOARD_F  = f"{PROOF_DIR}/dashboard.json"
STORIES_DIR  = f"{PROOF_DIR}/stories"
CONTENT_DIR  = f"{PROOF_DIR}/content"
OPP_DIR      = f"{PROOF_DIR}/opportunities"
AUDIT_F      = f"{PROOF_DIR}/AUDIT.md"
LEARNINGS_F  = "/workspace/.learnings/LEARNINGS.md"
ERRORS_F     = "/workspace/.learnings/ERRORS.md"

CASHFLOW_DIR = "/workspace/CASHFLOW"
BRAND_DIR    = "/workspace/brand"

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "..", "templates")
REF_DIR      = os.path.join(os.path.dirname(__file__), "..", "references")

DOMAINS = ["trading", "agents", "funnels", "content",
           "testimonials", "products", "media", "partnerships"]


# ── Helpers ───────────────────────────────────────────────────────────────────
def ensure_dirs():
    dirs = [PROOF_DIR, STORIES_DIR, CONTENT_DIR, OPP_DIR,
            "/workspace/.learnings"] + [f"{VAULT_DIR}/{d}" for d in DOMAINS]
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def load_dashboard() -> dict:
    if not os.path.exists(DASHBOARD_F):
        tpl = os.path.join(TEMPLATE_DIR, "dashboard.json")
        if os.path.exists(tpl):
            with open(tpl) as f:
                return json.load(f)
        return {}
    with open(DASHBOARD_F) as f:
        return json.load(f)


def save_dashboard(data: dict):
    data["last_updated"] = datetime.now().isoformat()
    with open(DASHBOARD_F, "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def load_vault_index() -> list:
    index_f = f"{VAULT_DIR}/index.json"
    if not os.path.exists(index_f):
        return []
    with open(index_f) as f:
        return json.load(f).get("items", [])


def save_vault_index(items: list):
    index_f = f"{VAULT_DIR}/index.json"
    with open(index_f, "w") as f:
        json.dump({"items": items, "last_updated": date.today().isoformat()}, f, indent=2)


def log_audit(message: str):
    ensure_dirs()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(AUDIT_F, "a") as f:
        f.write(f"\n[{ts}] {message}")


def log_error(message: str):
    ensure_dirs()
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(ERRORS_F, "a") as f:
        f.write(f"\n[{ts}] {message}")


def notify_telegram(message: str):
    token   = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print(f"  [Telegram] Not configured — {message[:60]}")
        return
    try:
        import urllib.request
        payload = json.dumps({"chat_id": chat_id, "text": message, "parse_mode": "Markdown"})
        req = urllib.request.Request(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data=payload.encode(),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=10):
            pass
        print("  ✅ Telegram sent")
    except Exception as e:
        log_error(f"Telegram failed: {e}")


def compute_impact_score(domain: str, metric: str, value: str) -> int:
    """Simple heuristic impact scoring."""
    score = 5
    value_lower = str(value).lower()
    # Revenue-based scoring
    for amount, pts in [("10000", 9), ("5000", 8), ("3000", 7),
                        ("1000", 6), ("500", 5), ("100", 4)]:
        if amount in value_lower.replace("€", "").replace(",", ""):
            score = pts
            break
    # Domain bonuses
    if domain == "testimonials":
        score = max(score, 7)
    if domain == "media":
        score = max(score, 6)
    return min(score, 10)


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_init(args):
    """Initialize proof engine workspace."""
    print("\n💎 Proof Engine — Initialization\n")
    ensure_dirs()

    # Dashboard
    if not os.path.exists(DASHBOARD_F):
        tpl = os.path.join(TEMPLATE_DIR, "dashboard.json")
        dash = {}
        if os.path.exists(tpl):
            with open(tpl) as f:
                dash = json.load(f)
        dash["period"] = date.today().strftime("%Y-%m")
        dash["last_updated"] = date.today().isoformat()
        save_dashboard(dash)
        print("  ✅ dashboard.json created")
    else:
        print("  ⚪ dashboard.json already exists")

    # Vault index
    index_f = f"{VAULT_DIR}/index.json"
    if not os.path.exists(index_f):
        save_vault_index([])
        print("  ✅ vault/index.json created")

    # Opportunities
    opp_f = f"{OPP_DIR}/ranked_2026.json"
    if not os.path.exists(opp_f):
        opps = _default_opportunities()
        with open(opp_f, "w") as f:
            json.dump({"opportunities": opps, "last_updated": date.today().isoformat()}, f, indent=2)
        print(f"  ✅ opportunities/ranked_2026.json seeded ({len(opps)} opportunities)")

    log_audit("Proof Engine initialized")
    print(f"\n  ✅ Proof Engine ready")
    print(f"  Next: python3 proof_manager.py capture --all")
    print(f"        python3 proof_manager.py status")


def cmd_status(args):
    """Show proof engine status."""
    print("\n💎 Proof Engine — Status\n")

    # Vault counts
    total = 0
    print("  Vault:")
    for domain in DOMAINS:
        d = f"{VAULT_DIR}/{domain}"
        count = len([f for f in os.listdir(d) if f.endswith(".json")]) if os.path.exists(d) else 0
        total += count
        icon = "✅" if count > 0 else "⚪"
        print(f"    {icon} {domain:15s} {count} items")
    print(f"    Total: {total} proof items")

    # Dashboard
    dash = load_dashboard()
    if dash:
        rev = dash.get("total_revenue", 0)
        print(f"\n  Dashboard: €{rev} total revenue tracked")
        channels = dash.get("by_channel", {})
        for ch, data in channels.items():
            r = data.get("revenue", 0)
            if r > 0:
                print(f"    {ch}: €{r}")

    # Stories
    stories = len([f for f in os.listdir(STORIES_DIR) if f.endswith(".md")]) if os.path.exists(STORIES_DIR) else 0
    print(f"\n  Stories generated: {stories}")

    # Opportunities
    opp_f = f"{OPP_DIR}/ranked_2026.json"
    opp_count = 0
    if os.path.exists(opp_f):
        with open(opp_f) as f:
            opp_count = len(json.load(f).get("opportunities", []))
    print(f"  Opportunities tracked: {opp_count}")

    # Hero proof
    items = load_vault_index()
    hero = [i for i in items if i.get("impact_score", 0) >= 8]
    print(f"\n  Hero proof items (score 8+): {len(hero)}")
    for h in hero[:3]:
        print(f"    💎 {h.get('domain')} | {h.get('metric')} | score {h.get('impact_score')}")

    if total == 0:
        print(f"\n  ⚡ Quick start: python3 proof_manager.py add --domain trading --metric revenue --value '€1000' --impact 6")


def cmd_capture(args):
    """Auto-capture proof from all domains."""
    domains = DOMAINS if args.all else ([args.domain] if args.domain else ["trading"])
    print(f"\n💎 Proof Capture — {', '.join(domains)}\n")

    captured = 0
    for domain in domains:
        print(f"  Scanning {domain}...")

        if domain == "trading":
            # Try to read from crypto-executor output
            tracker = f"{CASHFLOW_DIR}/TRACKING/tracker_state.json"
            if os.path.exists(tracker):
                try:
                    with open(tracker) as f:
                        data = json.load(f)
                    pnl = data.get("total_pnl", data.get("pnl", 0))
                    if pnl:
                        _save_proof_item(domain, "monthly_pnl", str(pnl),
                                         "Auto-captured from crypto-executor", 6)
                        print(f"    ✅ P&L captured: {pnl}")
                        captured += 1
                    else:
                        print(f"    ⚪ No P&L data in tracker_state.json")
                except Exception as e:
                    print(f"    ⚠️  Could not parse tracker: {e}")
                    log_error(f"Trading capture failed: {e}")
            else:
                print(f"    ⚪ {tracker} not found — is crypto-executor running?")

        elif domain == "agents":
            # Read from AUDIT.md files
            audit_files = []
            # Full workspace scan — all declared skill directories
            SCAN_DIRS = [
                "/workspace/proof",
                "/workspace/brand",
                "/workspace/CASHFLOW",
                "/workspace/voice",
                "/workspace/memory",
                "/workspace/revenue",
                "/workspace/content",
                "/workspace/.learnings",
            ]
            for scan_dir in SCAN_DIRS:
                if os.path.exists(scan_dir):
                    for root, _, files in os.walk(scan_dir):
                        for f in files:
                            if f == "AUDIT.md":
                                audit_files.append(os.path.join(root, f))
            if audit_files:
                print(f"    ✅ Found {len(audit_files)} AUDIT.md files")
                _save_proof_item(domain, "audit_files_count", str(len(audit_files)),
                                 "Agent audit logs present", 4)
                captured += 1
            else:
                print(f"    ⚪ No AUDIT.md files found yet")

        elif domain == "content":
            # Read from brand AUDIT.md
            brand_audit = f"{BRAND_DIR}/AUDIT.md"
            if os.path.exists(brand_audit):
                print(f"    ✅ Brand AUDIT.md found")
                _save_proof_item(domain, "brand_active", "true",
                                 "Brand engine active", 4)
                captured += 1
            else:
                print(f"    ⚪ Brand AUDIT.md not found yet")

        elif domain == "funnels":
            # Try revenue tracker
            rev_files = []
            for rev_dir in ["/workspace/revenue", "/workspace/CASHFLOW"]:
                if os.path.exists(rev_dir):
                    for root, _, files in os.walk(rev_dir):
                        for f in files:
                            if f.endswith(".json"):
                                rev_files.append(os.path.join(root, f))
            if rev_files:
                print(f"    ✅ Found {len(rev_files)} revenue files")
                _save_proof_item(domain, "revenue_files", str(len(rev_files)),
                                 "Funnel/revenue data present", 5)
                captured += 1
            else:
                print(f"    ⚪ No revenue files found yet")

        elif domain == "content":
            # Read from brand AUDIT.md AND content directory
            sources_found = 0
            for check_path in [f"{BRAND_DIR}/AUDIT.md",
                                "/workspace/content",
                                "/workspace/brand/content"]:
                if os.path.exists(check_path):
                    sources_found += 1
            if sources_found:
                print(f"    ✅ {sources_found} content sources found")
                _save_proof_item(domain, "content_sources_active", str(sources_found),
                                 "Content engine active", 4)
                captured += 1
            else:
                print(f"    ⚪ No content sources found yet")

        else:
            print(f"    ⚪ Manual domain — use: proof_manager.py add --domain {domain}")

    log_audit(f"Capture completed — {captured} items captured from {domains}")
    print(f"\n  ✅ Capture complete — {captured} items added")


def _save_proof_item(domain: str, metric: str, value: str,
                     context: str, impact: int):
    ensure_dirs()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    item_id = f"{domain}_{ts}"
    item = {
        "id": item_id,
        "domain": domain,
        "date": date.today().isoformat(),
        "metric": metric,
        "value": value,
        "context": context,
        "impact_score": impact,
        "deployed_to": [],
        "story_generated": False,
    }
    # Save to vault
    path = f"{VAULT_DIR}/{domain}/{ts}.json"
    with open(path, "w") as f:
        json.dump(item, f, indent=2)
    # Update index
    items = load_vault_index()
    items.append({"id": item_id, "domain": domain, "metric": metric,
                  "value": value, "impact_score": impact,
                  "date": date.today().isoformat()})
    save_vault_index(items)
    return item_id


def cmd_add(args):
    """Manually add a proof item."""
    domain  = args.domain or "testimonials"
    metric  = args.metric or "result"
    value   = args.value  or ""
    impact  = args.impact or compute_impact_score(domain, metric, value)
    context = args.context or f"Manual entry — {date.today().isoformat()}"

    if not value:
        print("❌ --value is required")
        return

    item_id = _save_proof_item(domain, metric, value, context, impact)
    log_audit(f"Proof added manually: {domain}/{metric} = {value} (score {impact})")

    print(f"\n✅ Proof item added")
    print(f"   ID:     {item_id}")
    print(f"   Domain: {domain}")
    print(f"   Metric: {metric}")
    print(f"   Value:  {value}")
    print(f"   Score:  {impact}/10")

    if impact >= 8:
        notify_telegram(
            f"💎 *Hero Proof Captured!*\n"
            f"Domain: {domain}\n"
            f"Result: {value}\n"
            f"Impact score: {impact}/10\n"
            f"→ Deploy recommended"
        )
        print(f"\n  🔥 Hero proof! Telegram notification sent.")


def cmd_dashboard(args):
    """View or update the multi-channel financial dashboard."""
    dash = load_dashboard()

    if args.update and args.revenue is not None:
        channel = args.update
        channels = dash.setdefault("by_channel", {})
        channels.setdefault(channel, {"revenue": 0, "trend": "stable", "note": ""})
        channels[channel]["revenue"] = args.revenue
        # Recompute total
        dash["total_revenue"] = sum(c.get("revenue", 0) for c in channels.values())
        dash["period"] = date.today().strftime("%Y-%m")
        save_dashboard(dash)
        log_audit(f"Dashboard updated: {channel} = €{args.revenue}")
        print(f"✅ {channel} updated: €{args.revenue}")
        print(f"   Total revenue: €{dash['total_revenue']}")
        return

    # Display dashboard
    period = args.period or "current"
    print(f"\n📊 Multi-Channel Financial Dashboard — {dash.get('period', 'N/A')}\n")
    total = dash.get("total_revenue", 0)
    channels = dash.get("by_channel", {})

    print(f"  {'CHANNEL':<25} {'REVENUE':>10}   TREND")
    print(f"  {'-'*45}")
    for ch, data in channels.items():
        rev   = data.get("revenue", 0)
        trend = data.get("trend", "stable")
        arrow = "📈" if trend == "up" else ("📉" if trend == "down" else "➡️ ")
        if rev > 0 or True:
            print(f"  {ch:<25} €{rev:>8.0f}   {arrow}")

    print(f"  {'-'*45}")
    print(f"  {'TOTAL':<25} €{total:>8.0f}")
    print(f"\n  Last updated: {dash.get('last_updated', 'never')}")

    if total == 0:
        print(f"\n  ⚡ Add revenue: proof_manager.py dashboard --update trading --revenue 1500")


def cmd_story(args):
    """Generate story arcs from proof items."""
    items   = load_vault_index()
    min_score = args.filter_impact if hasattr(args, 'filter_impact') and args.filter_impact else 5
    arc     = args.arc or "transformation"
    platform = args.platform or "twitter"

    eligible = [i for i in items if i.get("impact_score", 0) >= min_score]

    if not eligible:
        print(f"❌ No proof items with impact score >= {min_score}")
        print(f"   Add proof first: proof_manager.py add --domain trading --value '€X'")
        return

    print(f"\n📖 Story Generation — {arc} arc | {platform}\n")
    print(f"  Eligible items: {len(eligible)}")

    generated = 0
    for item in eligible[:5]:  # Max 5 per run
        story = _generate_story(item, arc, platform)
        ts    = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"{STORIES_DIR}/{arc}_{platform}_{item['domain']}_{ts}.md"
        with open(fname, "w") as f:
            f.write(story)
        print(f"  ✅ Story: {os.path.basename(fname)}")
        generated += 1

        # If VSL output requested
        if platform == "vsl" and args.output:
            with open(args.output, "w") as f:
                f.write(story)
            print(f"  ✅ VSL script: {args.output}")

    log_audit(f"Stories generated: {generated} ({arc}/{platform})")
    print(f"\n  ✅ {generated} stories saved to {STORIES_DIR}")


def _generate_story(item: dict, arc: str, platform: str) -> str:
    domain = item.get("domain", "")
    metric = item.get("metric", "")
    value  = item.get("value", "")
    ctx    = item.get("context", "")
    score  = item.get("impact_score", 5)

    arcs = {
        "transformation": f"""# Story — Transformation Arc
## Proof: {domain} | {metric} = {value}
## Platform: {platform} | Impact: {score}/10
---

**BEFORE (starting point — relatable):**
[FILL: What was the situation before this result?]

**TRIGGER (the action that changed things):**
[FILL: What specific action led to this result?]

**RESULT:**
{value}
Context: {ctx}

**MISSION (why sharing this):**
[FILL: What do you want readers to do / believe?]

---
*Generated: {date.today().isoformat()} | Arc: transformation | Domain: {domain}*
""",
        "system": f"""# Story — System Arc
## Proof: {domain} | {metric} = {value}
## Platform: {platform} | Impact: {score}/10
---

**PROBLEM (what most people struggle with):**
[FILL: Describe the common pain in this domain]

**SYSTEM (the automated solution):**
[FILL: Describe the system or approach that generated this result]

**PROOF:**
{value}
Context: {ctx}

**OFFER / NEXT STEP:**
[FILL: What can readers do to get similar results?]

---
*Generated: {date.today().isoformat()} | Arc: system | Domain: {domain}*
""",
        "milestone": f"""# Story — Milestone Arc
## Proof: {domain} | {metric} = {value}
## Platform: {platform} | Impact: {score}/10
---

**CONTEXT (humble starting point):**
[FILL: Where did this journey start? Be specific about time and baseline]

**JOURNEY — 3 things that made the difference:**
1. [FILL]
2. [FILL]
3. [FILL]

**TODAY:**
{value}
{ctx}

**NEXT (create anticipation):**
[FILL: What's the next milestone? When?]

---
*Generated: {date.today().isoformat()} | Arc: milestone | Domain: {domain}*
""",
    }

    return arcs.get(arc, arcs["transformation"])


def cmd_content(args):
    """Generate proof-based content briefs."""
    content_type = args.type or "thread"
    domain       = args.domain or "trading"
    platform     = args.platform or "twitter"
    min_score    = args.filter_impact if hasattr(args, 'filter_impact') and args.filter_impact else 6

    items = load_vault_index()
    eligible = [i for i in items
                if i.get("domain") == domain
                and i.get("impact_score", 0) >= min_score]

    if not eligible and not args.batch:
        print(f"❌ No proof items for domain '{domain}' with score >= {min_score}")
        print(f"   Add proof: proof_manager.py add --domain {domain}")
        return

    all_items = [i for i in items if i.get("impact_score", 0) >= min_score] if args.batch else eligible

    print(f"\n✍️  Content Generation — {content_type} | {platform}\n")

    formats = {
        "thread": _thread_brief,
        "carousel": _carousel_brief,
        "reel": _reel_brief,
        "email": _email_brief,
    }

    generated = 0
    for item in all_items[:5]:
        fn = formats.get(content_type, _thread_brief)
        brief = fn(item, platform)
        ts    = datetime.now().strftime("%Y%m%d_%H%M%S")
        fname = f"{CONTENT_DIR}/{content_type}_{item['domain']}_{ts}.md"
        with open(fname, "w") as f:
            f.write(brief)
        print(f"  ✅ Brief: {os.path.basename(fname)}")
        generated += 1

    log_audit(f"Content briefs generated: {generated} ({content_type}/{platform})")
    print(f"\n  ✅ {generated} briefs saved to {CONTENT_DIR}")


def _thread_brief(item, platform):
    return f"""# Content Brief — Thread
## Domain: {item['domain']} | Value: {item['value']} | Score: {item['impact_score']}/10
---

HOOK (tweet 1 — result first):
{item['value']} — here's how:

BODY (tweets 2-6 — the steps):
1. [FILL: First key step]
2. [FILL: Second key step]
3. [FILL: Third key step]
4. [FILL: The turning point]
5. [FILL: The result detail]

PROOF TWEET (tweet 7):
[Reference screenshot or specific metric]

CLOSE (tweet 8 — CTA):
[FILL: What should readers do next?]

---
Context: {item.get('context', '')}
*Generated: {date.today().isoformat()}*
"""


def _carousel_brief(item, platform):
    return f"""# Content Brief — Carousel
## Domain: {item['domain']} | Value: {item['value']} | Score: {item['impact_score']}/10
---

SLIDE 1 (hook — bold claim):
[FILL: Big result statement]

SLIDES 2-6 (system breakdown):
Slide 2: [FILL step 1]
Slide 3: [FILL step 2]
Slide 4: [FILL step 3]
Slide 5: [FILL step 4]
Slide 6: [FILL step 5]

SLIDE 7 (before vs after):
Before: [FILL]
After:  {item['value']}

SLIDE 8 (CTA):
[FILL: Follow / DM / Link in bio]

---
Context: {item.get('context', '')}
*Generated: {date.today().isoformat()}*
"""


def _reel_brief(item, platform):
    return f"""# Content Brief — Reel Script
## Domain: {item['domain']} | Value: {item['value']} | Score: {item['impact_score']}/10
---

0-3s   HOOK: "[FILL — first word must stop scroll]"
3-15s  CONTEXT: "[FILL — why this matters]"
15-40s VALUE: "[FILL — the 3 key moves]"
40-55s PROOF: "[Reference: {item['value']}]"
55-60s CTA: "[FILL: follow / link in bio / DM]"

Visual notes:
[FILL: screen recording / b-roll suggestions]

---
Context: {item.get('context', '')}
*Generated: {date.today().isoformat()}*
"""


def _email_brief(item, platform):
    return f"""# Content Brief — Email
## Domain: {item['domain']} | Value: {item['value']} | Score: {item['impact_score']}/10
---

SUBJECT: [FILL — contains the result, creates curiosity]

HOOK (first line — no "I" opener):
[FILL]

STORY BODY:
[Use Arc 1 Transformation or Arc 4 Milestone from storytelling.md]

PROOF POINT:
{item['value']}
{item.get('context', '')}

SOFT CTA:
[FILL — one clear next step]

P.S.:
[FILL — repeat the core proof or add urgency]

---
*Generated: {date.today().isoformat()}*
"""


def cmd_opportunities(args):
    """View or manage business opportunities."""
    opp_f = f"{OPP_DIR}/ranked_2026.json"

    if args.action == "view":
        if not os.path.exists(opp_f):
            print("❌ No opportunities file — run init first")
            return

        with open(opp_f) as f:
            data = json.load(f)

        opps = data.get("opportunities", [])
        min_score = args.filter_score if hasattr(args, 'filter_score') and args.filter_score else 0
        filtered  = sorted([o for o in opps if o.get("total_score", 0) >= min_score],
                           key=lambda x: x.get("total_score", 0), reverse=True)

        print(f"\n🚀 Business Opportunities 2026 — Top {len(filtered)}\n")
        print(f"  {'OPPORTUNITY':<35} {'SCORE':>6}  CATEGORY")
        print(f"  {'-'*60}")
        for o in filtered:
            print(f"  {o['name']:<35} {o.get('total_score',0):>5}/50  {o.get('category','')}")
            if o.get("wesleys_edge"):
                print(f"    Edge: {o['wesleys_edge']}")

    elif args.action == "add":
        if not os.path.exists(opp_f):
            with open(opp_f, "w") as f:
                json.dump({"opportunities": []}, f)

        with open(opp_f) as f:
            data = json.load(f)

        tpl = os.path.join(TEMPLATE_DIR, "opportunity_template.json")
        opp = {}
        if os.path.exists(tpl):
            with open(tpl) as f:
                opp = json.load(f)

        opp["name"]       = args.name or "New Opportunity"
        opp["category"]   = args.category or "other"
        opp["total_score"] = args.score or 0
        opp["added_date"] = date.today().isoformat()

        data["opportunities"].append(opp)
        with open(opp_f, "w") as f:
            json.dump(data, f, indent=2)

        print(f"✅ Opportunity added: {opp['name']} (score: {opp['total_score']}/50)")
        log_audit(f"Opportunity added: {opp['name']}")

    elif args.action == "report":
        print("\n📋 Opportunity Report — 2026\n")
        if os.path.exists(opp_f):
            with open(opp_f) as f:
                data = json.load(f)
            opps = sorted(data.get("opportunities", []),
                         key=lambda x: x.get("total_score", 0), reverse=True)
            for i, o in enumerate(opps[:5], 1):
                print(f"  #{i} {o['name']}")
                print(f"      Score: {o.get('total_score',0)}/50")
                print(f"      Edge:  {o.get('wesleys_edge','N/A')}")
                print(f"      Next:  {o.get('next_action','N/A')}\n")
        log_audit("Opportunity report generated")


def cmd_deploy(args):
    """Deploy proof to other skills."""
    action = args.action or "weekly-sync"
    items  = load_vault_index()
    min_score = args.filter_impact if hasattr(args, 'filter_impact') and args.filter_impact else 7

    if action == "weekly-sync":
        print(f"\n🚀 Weekly Proof Deploy Sync\n")
        hero = [i for i in items if i.get("impact_score", 0) >= min_score]
        print(f"  Items to deploy (score >= {min_score}): {len(hero)}")

        deployed = 0
        # Deploy to brand proof vault
        brand_proof = f"{BRAND_DIR}/proof"
        if os.path.exists(BRAND_DIR):
            os.makedirs(brand_proof, exist_ok=True)
            sync_file = f"{brand_proof}/proof_sync_{date.today().isoformat()}.json"
            with open(sync_file, "w") as f:
                json.dump({"items": hero, "synced": date.today().isoformat()}, f, indent=2)
            print(f"  ✅ personal-brand-builder: {len(hero)} items synced")
            deployed += 1
        else:
            print(f"  ⚪ personal-brand-builder: /workspace/brand/ not found")

        log_audit(f"Weekly sync: {deployed} skills updated, {len(hero)} items")
        notify_telegram(
            f"💎 *Weekly Proof Sync*\n"
            f"Items deployed (score {min_score}+): {len(hero)}\n"
            f"Skills updated: {deployed}\n"
            f"Next sync: Sunday 20h00"
        )
        print(f"\n  ✅ Weekly sync complete")

    else:
        # Single item deploy
        proof_id = args.proof_id if hasattr(args, 'proof_id') else None
        target   = args.target if hasattr(args, 'target') else "all"
        print(f"  Deploying proof {proof_id} to {target}")
        log_audit(f"Deploy: {proof_id} → {target}")
        print(f"  ✅ Deploy logged")


def cmd_morning_brief(args):
    """Generate morning proof brief."""
    items = load_vault_index()
    hero  = [i for i in items if i.get("impact_score", 0) >= 8]
    ready = [i for i in items if i.get("impact_score", 0) >= 5
             and not i.get("story_generated")]
    dash  = load_dashboard()
    total = dash.get("total_revenue", 0)

    print(f"\n💎 Morning Proof Brief — {date.today().strftime('%A %d %B')}\n")
    print(f"  Vault total:   {len(items)} proof items")
    print(f"  Hero proof:    {len(hero)} items (score 8+)")
    print(f"  Ready to use:  {len(ready)} items pending story")
    print(f"  Revenue total: €{total}")

    if hero:
        print(f"\n  🔥 Hero proof items:")
        for h in hero[:3]:
            print(f"    → {h['domain']}: {h['value']} (score {h['impact_score']})")

    if len(items) == 0:
        print(f"\n  ⚡ No proof yet — add your first:")
        print(f"     proof_manager.py add --domain trading --value '€500' --impact 6")

    log_audit("Morning brief generated")
    notify_telegram(
        f"💎 *Morning Proof Brief*\n"
        f"Vault: {len(items)} items | Hero: {len(hero)}\n"
        f"Revenue: €{total}\n"
        f"Ready for story: {len(ready)} items"
    )


def cmd_weekly_sync(args):
    """Full weekly sync — capture, story, deploy."""
    print("\n💎 Weekly Sync — All Engines\n")

    # 1. Capture
    class FakeArgs:
        all = True
        domain = None
    print("  [1/4] Capturing all domains...")
    cmd_capture(FakeArgs())

    # 2. Stories for new items
    print("\n  [2/4] Generating stories...")
    items = load_vault_index()
    new_items = [i for i in items if not i.get("story_generated")
                 and i.get("impact_score", 0) >= 7]
    print(f"        {len(new_items)} items eligible for story")

    # 3. Deploy
    print("\n  [3/4] Deploying to skills...")
    class DeployArgs:
        action = "weekly-sync"
        filter_impact = 7
    cmd_deploy(DeployArgs())

    # 4. Dashboard update
    print("\n  [4/4] Dashboard refresh...")
    dash = load_dashboard()
    dash["period"] = date.today().strftime("%Y-%m")
    save_dashboard(dash)
    print(f"        Dashboard updated")

    log_audit("Weekly sync completed — all engines")
    print(f"\n  ✅ Weekly sync complete")


def _default_opportunities():
    return [
        {"name": "AI Agent as a Service (AaaS)", "category": "ai-services",
         "total_score": 45, "wesleys_edge": "Already runs own agents in production",
         "next_action": "Package OpenClaw setup as a client offering"},
        {"name": "Automated Content Agency", "category": "ai-services",
         "total_score": 43, "wesleys_edge": "Full stack built: content-creator-pro + voice",
         "next_action": "Define service tiers and pricing page"},
        {"name": "Trading Signal Newsletter (paid)", "category": "digital-products",
         "total_score": 41, "wesleys_edge": "Real signals from shark-mindset + real P&L",
         "next_action": "Launch free newsletter first, convert to paid at 500 subs"},
        {"name": "AI Automation Course / Program", "category": "digital-products",
         "total_score": 40, "wesleys_edge": "Documented real results, full system built",
         "next_action": "Record module 1 using voice-agent-pro-v3"},
        {"name": "Private Community (Autonomous Wealth)", "category": "community",
         "total_score": 38, "wesleys_edge": "Personal brand + proof vault already growing",
         "next_action": "Set up Telegram or Discord — invite first 10 members"},
        {"name": "Prompt & Agent Template Marketplace", "category": "digital-products",
         "total_score": 36, "wesleys_edge": "Proven ClawHub skills already built",
         "next_action": "Package top 5 skills as paid bundles"},
        {"name": "AI Tools Affiliate Stack", "category": "affiliates",
         "total_score": 35, "wesleys_edge": "Authentic user with documented results",
         "next_action": "Apply to ElevenLabs, Systeme.io, OpenClaw affiliate programs"},
        {"name": "Mastermind / High-Ticket Coaching", "category": "community",
         "total_score": 34, "wesleys_edge": "Real P&L proof + full autonomous system",
         "next_action": "After 10K followers — launch application-only group"},
    ]


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="Proof Engine — Credibility at Scale")
    sub = parser.add_subparsers(dest="command")

    # init
    sub.add_parser("init", help="Initialize proof engine workspace")

    # status
    sub.add_parser("status", help="Show proof engine status")

    # capture
    p_cap = sub.add_parser("capture", help="Auto-capture proof from domains")
    p_cap.add_argument("--all",    action="store_true", help="Capture all domains")
    p_cap.add_argument("--domain", choices=DOMAINS)

    # add
    p_add = sub.add_parser("add", help="Manually add a proof item")
    p_add.add_argument("--domain",  choices=DOMAINS, required=True)
    p_add.add_argument("--metric",  required=True, help="What was measured")
    p_add.add_argument("--value",   required=True, help="The result (e.g. '€2500')")
    p_add.add_argument("--impact",  type=int, help="Impact score 1-10")
    p_add.add_argument("--context", help="Additional context")

    # vault
    p_vault = sub.add_parser("vault", help="Browse proof vault")
    p_vault.add_argument("--filter-impact", type=int, default=0)
    p_vault.add_argument("--sort", choices=["date", "impact"], default="impact")

    # dashboard
    p_dash = sub.add_parser("dashboard", help="View or update financial dashboard")
    p_dash.add_argument("--update",  help="Channel to update (e.g. funnels)")
    p_dash.add_argument("--revenue", type=float, help="Revenue amount")
    p_dash.add_argument("--period",  choices=["current", "monthly", "quarterly"])

    # story
    p_story = sub.add_parser("story", help="Generate story arcs from proof")
    p_story.add_argument("--proof-id",      help="Specific proof ID")
    p_story.add_argument("--arc",           choices=["transformation", "system", "mistake", "milestone", "proof", "all"], default="transformation")
    p_story.add_argument("--platform",      choices=["twitter", "linkedin", "instagram", "youtube", "tiktok", "email", "vsl"], default="twitter")
    p_story.add_argument("--filter-impact", type=int, default=5)
    p_story.add_argument("--output",        help="Output file (for VSL)")

    # content
    p_content = sub.add_parser("content", help="Generate proof-based content briefs")
    p_content.add_argument("--type",         choices=["thread", "carousel", "reel", "email"], default="thread")
    p_content.add_argument("--domain",       choices=DOMAINS)
    p_content.add_argument("--platform",     choices=["twitter", "linkedin", "instagram", "youtube", "tiktok"])
    p_content.add_argument("--filter-impact", type=int, default=6)
    p_content.add_argument("--batch",        action="store_true")

    # opportunities
    p_opp = sub.add_parser("opportunities", help="Business opportunities scanner")
    p_opp.add_argument("--action",       choices=["view", "add", "report"], default="view")
    p_opp.add_argument("--filter-score", type=int, default=0)
    p_opp.add_argument("--name",         help="Opportunity name (for add)")
    p_opp.add_argument("--category",     help="Category (for add)")
    p_opp.add_argument("--score",        type=int, help="Total score /50 (for add)")

    # deploy
    p_deploy = sub.add_parser("deploy", help="Deploy proof to other skills")
    p_deploy.add_argument("--action",        choices=["weekly-sync", "single"], default="weekly-sync")
    p_deploy.add_argument("--filter-impact", type=int, default=7)
    p_deploy.add_argument("--proof-id",      help="Specific proof ID (for single)")
    p_deploy.add_argument("--target",        help="Target skill (for single)")

    # morning-brief
    sub.add_parser("morning-brief", help="Generate morning proof brief")

    # weekly-sync
    sub.add_parser("weekly-sync", help="Full weekly sync — all engines")

    args = parser.parse_args()

    dispatch = {
        "init":           cmd_init,
        "status":         cmd_status,
        "capture":        cmd_capture,
        "add":            cmd_add,
        "vault":          cmd_status,
        "dashboard":      cmd_dashboard,
        "story":          cmd_story,
        "content":        cmd_content,
        "opportunities":  cmd_opportunities,
        "deploy":         cmd_deploy,
        "morning-brief":  cmd_morning_brief,
        "weekly-sync":    cmd_weekly_sync,
    }

    if args.command in dispatch:
        dispatch[args.command](args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
