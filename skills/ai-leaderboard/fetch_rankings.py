#!/usr/bin/env python3
"""
Fetch AI Rankings via Browser Automation

This script uses agent-browser CLI to fetch JavaScript-rendered content
from AI rankings pages including Artificial Analysis and OpenRouter.

Requirements:
- agent-browser CLI installed
- Run after loading browser-automation skill

Usage:
    python3 fetch_rankings.py                      # Get Artificial Analysis LLM Leaderboard
    python3 fetch_rankings.py --aa-intelligence    # Get Intelligence Index rankings
    python3 fetch_rankings.py --aa-coding          # Get Coding Index rankings
    python3 fetch_rankings.py --aa-agentic         # Get Agentic Index rankings
    python3 fetch_rankings.py --aa-providers      # Get API Providers rankings
    python3 fetch_rankings.py --openrouter         # Get OpenRouter rankings
    python3 fetch_rankings.py --apps               # Get OpenRouter apps ranking

Security Note:
- Uses subprocess.run() with shell=False for security
- All commands are hardcoded, no user input passed to shell
"""

import subprocess
import json
import re
import sys
import time
from datetime import datetime


def run_browser_command(args: list) -> str:
    """
    Run agent-browser command and return output.

    Security: Uses shell=False (default) to prevent command injection.
    All arguments are passed as a list, not as a shell command string.
    """
    cmd = ['agent-browser'] + args
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}", file=sys.stderr)
        return ""
    return result.stdout


def fetch_artificial_analysis_leaderboard():
    """Fetch Artificial Analysis LLM Leaderboard via browser"""
    print("Fetching Artificial Analysis LLM Leaderboard via browser...")

    run_browser_command(['open', 'https://artificialanalysis.ai/leaderboards/models'])
    run_browser_command(['wait', '--load', 'networkidle'])
    run_browser_command(['wait', '5000'])  # Wait for JS rendering
    output = run_browser_command(['eval', 'document.body.innerText'])

    return output


def fetch_artificial_analysis_providers():
    """Fetch Artificial Analysis API Providers Leaderboard via JavaScript table extraction"""
    print("Fetching Artificial Analysis API Providers Leaderboard...")

    run_browser_command(['open', 'https://artificialanalysis.ai/leaderboards/providers'])
    run_browser_command(['wait', '--load', 'networkidle'])
    run_browser_command(['wait', '5000'])  # Wait for JS rendering

    # Use JavaScript to extract table data - use simpler approach
    js_code = 'document.querySelector("table") ? Array.from(document.querySelectorAll("tr")).slice(0,25).map(tr => Array.from(tr.querySelectorAll("td")).map(td => td.innerText.replace(/\\n/g," ").trim()).join("||")).join("\\n") : "NO TABLE"'
    output = run_browser_command(['eval', js_code])

    return output if output else ""


def fetch_artificial_analysis_coding():
    """Fetch Artificial Analysis Coding Index Leaderboard via snapshot"""
    print("Fetching Artificial Analysis Coding Index Leaderboard...")

    run_browser_command(['open', 'https://artificialanalysis.ai/?intelligence=coding-index'])
    run_browser_command(['wait', '--load', 'networkidle'])
    run_browser_command(['wait', '6000'])

    # Use snapshot to get the raw output, then parse
    result = subprocess.run(
        ['agent-browser', 'snapshot'],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        return ""

    snapshot = result.stdout

    lines = snapshot.split('\n')

    in_coding_section = False
    section_lines = []

    for i, line in enumerate(lines):
        if 'tabpanel "Coding Index"' in line:
            in_coding_section = True
            continue

        if in_coding_section:
            if line.strip().startswith('- tabpanel "'):
                break
            section_lines.append(line)

    section_text = '\n'.join(section_lines)

    # Extract model names from "group" elements - only those in THIS tabpanel
    models = []
    seen = set()
    for line in section_lines[:300]:  # First ~300 lines have the models
        match = re.search(r'group "([^"]+)"', line)
        if match:
            model_name = match.group(1).strip()
            if model_name and model_name != 'Reasoning model' and len(model_name) > 2 and len(model_name) < 50:
                if model_name not in seen:
                    seen.add(model_name)
                    models.append(model_name)

    # Extract ALL valid scores (they start around line 231 and go to end)
    all_scores = re.findall(r'StaticText "(\d{2})"', section_text)
    valid_scores = [s for s in all_scores if 10 <= int(s) <= 60]

    # Combine models with scores (first N models match first N scores)
    result_lines = []
    count = min(len(models), len(valid_scores))
    for i in range(count):
        result_lines.append(f"{models[i]}|{valid_scores[i]}")

    if result_lines:
        return "CODING INDEX\n" + "\n".join(result_lines)
    return ""


def fetch_artificial_analysis_agentic():
    """Fetch Artificial Analysis Agentic Index Leaderboard via snapshot"""
    print("Fetching Artificial Analysis Agentic Index Leaderboard...")

    run_browser_command(['open', 'https://artificialanalysis.ai/?intelligence=agentic-index'])
    run_browser_command(['wait', '--load', 'networkidle'])
    run_browser_command(['wait', '6000'])

    # Use snapshot to get the raw output, then parse
    result = subprocess.run(
        ['agent-browser', 'snapshot'],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        return ""

    snapshot = result.stdout

    lines = snapshot.split('\n')

    in_agentic_section = False
    section_lines = []

    for i, line in enumerate(lines):
        if 'tabpanel "Agentic Index"' in line:
            in_agentic_section = True
            continue

        if in_agentic_section:
            if line.strip().startswith('- tabpanel "'):
                break
            section_lines.append(line)

    section_text = '\n'.join(section_lines)

    # Extract model names - only from early part
    models = []
    seen = set()
    for line in section_lines[:300]:
        match = re.search(r'group "([^"]+)"', line)
        if match:
            model_name = match.group(1).strip()
            if model_name and model_name != 'Reasoning model' and len(model_name) > 2 and len(model_name) < 50:
                if model_name not in seen:
                    seen.add(model_name)
                    models.append(model_name)

    # Extract ALL valid scores
    all_scores = re.findall(r'StaticText "(\d{2})"', section_text)
    valid_scores = [s for s in all_scores if 10 <= int(s) <= 60]

    # Combine
    result_lines = []
    count = min(len(models), len(valid_scores))
    for i in range(count):
        result_lines.append(f"{models[i]}|{valid_scores[i]}")

    if result_lines:
        return "AGENTIC INDEX\n" + "\n".join(result_lines)
    return ""


def fetch_artificial_analysis_image_models():
    """Fetch Artificial Analysis Image/Video Models Leaderboard"""
    print("Fetching Artificial Analysis Image/Video Models Leaderboard...")

    run_browser_command(['open', 'https://artificialanalysis.ai/'])
    run_browser_command(['wait', '--load', 'networkidle'])
    run_browser_command(['wait', '3000'])

    output = run_browser_command(['eval', 'document.body.innerText.substring(0, 5000)'])

    return output if output else "Image models section not found"


def fetch_openrouter_rankings():
    """Fetch OpenRouter rankings page via browser"""
    print("Fetching OpenRouter rankings via browser...")

    run_browser_command(['open', 'https://openrouter.ai/rankings'])
    run_browser_command(['wait', '--load', 'networkidle'])

    # Click "Show more" to expand from Top 10 to Top 20+
    run_browser_command(['eval', "const buttons = document.querySelectorAll('button'); for(let b of buttons) { if(b.innerText === 'Show more') { b.click(); break; } }"])
    run_browser_command(['wait', '3000'])

    output = run_browser_command(['eval', 'document.body.innerText'])

    return output


def fetch_openrouter_apps():
    """Fetch OpenRouter apps ranking"""
    print("Fetching OpenRouter apps ranking...")

    run_browser_command(['open', 'https://openrouter.ai/apps'])
    run_browser_command(['wait', '--load', 'networkidle'])
    run_browser_command(['wait', '3000'])
    output = run_browser_command(['eval', 'document.body.innerText'])

    return output


def parse_aa_highlights(text: str) -> str:
    """Parse Artificial Analysis highlights section"""
    lines = []

    if 'Intelligence' in text:
        int_match = re.search(r'Intelligence.*?:\s*([^\n]+)', text)
        if int_match:
            lines.append(f"Intelligence: {int_match.group(1)}")

    if 'Output Speed' in text or 'tokens/s' in text:
        speed_match = re.search(r'Output Speed.*?:\s*([^\n]+)', text)
        if speed_match:
            lines.append(f"Speed: {speed_match.group(1)}")

    if 'Price' in text:
        price_match = re.search(r'Price.*?:\s*([^\n]+)', text)
        if price_match:
            lines.append(f"Price: {price_match.group(1)}")

    return '\n'.join(lines) if lines else "Highlights not found in page"


def parse_aa_providers(text: str) -> list:
    """Parse API Providers data from double-pipe-separated table rows"""
    providers = []

    # Clean up text - remove JSON string wrapper if present
    text = text.strip()
    if text.startswith('"') and text.endswith('"'):
        # It's a JSON-encoded string, decode it
        import json
        try:
            text = json.loads(text)
            text = text.strip()
        except:
            pass

    # Remove leading/trailing whitespace and quotes
    text = text.strip('"\n ')

    lines = text.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Split by || (double pipe)
        parts = [p.strip() for p in line.split('||')]

        if len(parts) < 7:
            continue

        # Skip header row
        if parts[0].strip() in ['Features', 'API Provider', '']:
            continue
        if not parts[0] or not parts[1]:
            continue

        # Extract fields: Provider, Model, Context, License, II, Price, Speed, Latency, etc.
        provider = parts[0].strip()
        model = parts[1].strip()
        context = parts[2].strip() if len(parts) > 2 else ''
        license = parts[3].strip() if len(parts) > 3 else ''
        ii = parts[4].strip() if len(parts) > 4 else ''
        price = parts[5].strip() if len(parts) > 5 else ''
        speed = parts[6].strip() if len(parts) > 6 else ''
        latency = parts[7].strip() if len(parts) > 7 else ''

        # Clean up price (already has $)
        if price.startswith('$') and price.count('$') > 1:
            price = price.replace('$', '', 1)

        if model and ii and provider not in ['Features', 'Model', 'API Provider']:
            # Validate II is a number
            try:
                ii_num = int(ii)
                providers.append({
                    'provider': provider[:22],
                    'model': model[:38],
                    'context': context,
                    'license': license[:4],
                    'ii': str(ii_num),
                    'price': price if price else '-',
                    'speed': speed if speed else '-',
                    'latency': latency if latency else '-'
                })
            except ValueError:
                continue

    # Sort by Intelligence Index
    providers.sort(key=lambda x: int(x['ii']) if x['ii'].isdigit() else 0, reverse=True)

    return providers[:25]


def format_aa_leaderboard(text: str, source: str = "LLM Leaderboard") -> str:
    """Format Artificial Analysis leaderboard as markdown"""
    lines = [
        "=" * 70,
        f"    Artificial Analysis {source}",
        "    (Intelligence Index, Speed, Price Comparison)",
        "=" * 70,
        "",
        "HIGHLIGHTS:",
        parse_aa_highlights(text),
        "",
        "-" * 70,
        "For detailed comparison, please visit:",
        "https://artificialanalysis.ai/leaderboards/models" if "providers" not in source.lower() else "https://artificialanalysis.ai/leaderboards/providers",
        "-" * 70,
        f"Query time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 70
    ]

    return "\n".join(lines)


def format_aa_providers(text: str) -> str:
    """Format Artificial Analysis API Providers as markdown"""
    providers = parse_aa_providers(text)

    lines = [
        "=" * 70,
        "    Artificial Analysis LLM API Providers Leaderboard",
        "    (Comparison of 500+ AI Model Endpoints)",
        "=" * 70,
        "",
        "TOP PROVIDERS BY INTELLIGENCE INDEX:",
        "-" * 70,
        f"{'#':<3} {'Provider':<22} {'Model':<35} {'II':<3} {'Price':<7} {'Speed':<6} {'Latency':<8}",
        "-" * 70
    ]

    if providers:
        for i, p in enumerate(providers[:20], 1):
            lines.append(
                f"{i:<3} {p['provider']:<22} {p['model']:<35} "
                f"{p['ii']:<3} {p['price']:<7} {p['speed']:<6} {p['latency']:<8}"
            )
    else:
        lines.append("Failed to parse providers data. Please visit the website directly.")

    lines.extend([
        "",
        "-" * 70,
        "KEY PROVIDERS:",
        "Cerebras, Groq, Fireworks, SambaNova, Together.ai, Hyperbolic, Nebius",
        "Google Vertex, Azure OpenAI, AWS Bedrock, DeepInfra, HuggingFace",
        "",
        "For complete rankings (500+ endpoints), please visit:",
        "https://artificialanalysis.ai/leaderboards/providers",
        "-" * 70,
        f"Query time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 70
    ])

    return "\n".join(lines)


def format_index_ranking(text: str, index_type: str) -> str:
    """Format Coding or Agentic Index as markdown table"""
    lines = [
        "=" * 70,
        f"    Artificial Analysis {index_type}",
        f"    (Intelligence Index for {index_type})",
        "=" * 70,
        "",
        f"{'Rank':<6} {'Model':<40} {'Score':<6}",
        "-" * 70
    ]

    # Parse model|score pairs
    entries = []
    for line in text.strip().split('\n'):
        if '|' in line:
            parts = line.split('|')
            if len(parts) >= 2:
                model = parts[0].strip()
                score = parts[1].strip()
                if model and score.isdigit():
                    entries.append((model, int(score)))

    # Sort by score descending
    entries.sort(key=lambda x: x[1], reverse=True)

    for i, (model, score) in enumerate(entries[:20], 1):
        lines.append(f"{i:<6} {model:<40} {score:<6}")

    lines.extend([
        "",
        "-" * 70,
        f"Full rankings (417 models): https://artificialanalysis.ai/?intelligence={index_type.lower().replace(' ', '-')}",
        f"Query time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 70
    ])

    return "\n".join(lines)


def parse_openrouter_models(text: str) -> list:
    """Parse top models from OpenRouter page text"""
    models = []

    # Find LLM Leaderboard section
    llm_section = text
    if 'LLM Leaderboard' in text:
        parts = text.split('LLM Leaderboard')
        if len(parts) > 1:
            section_content = parts[1]
            if 'Market Share' in section_content:
                llm_section = section_content.split('Market Share')[0]
            else:
                llm_section = section_content

    # Pattern: "1.\nMiniMax M2.5\nby\nminimax\n1.75T tokens\n6%"
    pattern = r'(\d+)\.\n([^\n]+)\nby\n([^\n]+)\n([\d.]+[TB]) tokens\n([+-]?\d+%)?(new)?'

    matches = re.findall(pattern, llm_section)
    for match in matches:
        rank, model, provider, tokens, change, is_new = match
        models.append({
            "rank": int(rank),
            "model": model.strip(),
            "provider": provider.strip(),
            "tokens": tokens,
            "change": change if change else ("new" if is_new else "N/A")
        })

    return models


def parse_openrouter_apps(text: str) -> list:
    """Parse top apps from OpenRouter page text"""
    apps = []

    # Find the Top Apps section
    apps_section = text.split("Top Apps")[-1] if "Top Apps" in text else text

    # Pattern for apps: "1.\nOpenClaw \nThe AI that actually does things\n552Btokens"
    pattern = r'(\d+)\.\n([^\n]+)\n([^\n]+)\n([\d.]+[TB])tokens'

    matches = re.findall(pattern, apps_section)
    for match in matches:
        rank, name, description, tokens = match
        apps.append({
            "rank": int(rank),
            "name": name.strip(),
            "description": description.strip(),
            "tokens": tokens
        })

    return apps


def format_models_table(models: list, source: str = "OpenRouter") -> str:
    """Format models as markdown table"""
    lines = [
        "=" * 70,
        f"    {source} Top Models (Weekly Usage)",
        "=" * 70,
        "",
        f"{'Rank':<6} {'Model':<30} {'Provider':<15} {'Tokens':<12} {'Change'}",
        "-" * 70
    ]

    for m in models:
        lines.append(f"{m['rank']:<6} {m['model']:<30} {m['provider']:<15} {m['tokens']:<12} {m['change']}")

    lines.extend([
        "-" * 70,
        f"Total: {len(models)} models",
        f"Query time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 70
    ])

    return "\n".join(lines)


def format_apps_table(apps: list) -> str:
    """Format apps as markdown table"""
    lines = [
        "=" * 70,
        "    OpenRouter Top Apps (Daily Usage)",
        "=" * 70,
        "",
        f"{'Rank':<6} {'App Name':<25} {'Tokens':<12}",
        "-" * 70
    ]

    for a in apps:
        lines.append(f"{a['rank']:<6} {a['name']:<25} {a['tokens']:<12}")

    lines.extend([
        "-" * 70,
        f"Total: {len(apps)} apps",
        f"Query time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 70
    ])

    return "\n".join(lines)


def main():
    """Main function"""
    mode = "aa-leaderboard"  # Default to Artificial Analysis

    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == "--aa-intelligence" or arg == "--aa-speed" or arg == "--aa-price":
            mode = "aa-leaderboard"
        elif arg == "--aa-providers":
            mode = "aa-providers"
        elif arg == "--aa-coding":
            mode = "aa-coding"
        elif arg == "--aa-agentic":
            mode = "aa-agentic"
        elif arg == "--aa-image":
            mode = "aa-image"
        elif arg == "--openrouter":
            mode = "openrouter"
        elif arg == "--apps":
            mode = "apps"
        elif arg in ["-h", "--help"]:
            print(__doc__)
            return

    # Fetch page content based on mode
    if mode == "aa-leaderboard":
        text = fetch_artificial_analysis_leaderboard()
        if text:
            print(format_aa_leaderboard(text, "LLM Leaderboard"))
        else:
            print("Failed to fetch Artificial Analysis leaderboard", file=sys.stderr)
            sys.exit(1)

    elif mode == "aa-providers":
        text = fetch_artificial_analysis_providers()
        if text:
            print(format_aa_providers(text))
        else:
            print("Failed to fetch Artificial Analysis providers", file=sys.stderr)
            sys.exit(1)

    elif mode == "aa-coding":
        text = fetch_artificial_analysis_coding()
        if text:
            print(format_index_ranking(text, "Coding Index"))
        else:
            print("Failed to fetch Artificial Analysis coding index", file=sys.stderr)
            sys.exit(1)

    elif mode == "aa-agentic":
        text = fetch_artificial_analysis_agentic()
        if text:
            print(format_index_ranking(text, "Agentic Index"))
        else:
            print("Failed to fetch Artificial Analysis agentic index", file=sys.stderr)
            sys.exit(1)

    elif mode == "aa-image":
        text = fetch_artificial_analysis_image_models()
        if text:
            print(format_aa_leaderboard(text, "Image/Video Models"))
        else:
            print("Failed to fetch Artificial Analysis image models", file=sys.stderr)
            sys.exit(1)

    elif mode == "openrouter":
        text = fetch_openrouter_rankings()
        if text:
            if text.startswith('"') and text.endswith('"'):
                text = json.loads(text)

            models = parse_openrouter_models(text)
            if models:
                print(format_models_table(models, "OpenRouter"))
            else:
                print("No models found in page content")
                print("\n--- Raw Content (first 2000 chars) ---")
                print(text[:2000])
        else:
            print("Failed to fetch OpenRouter rankings", file=sys.stderr)
            sys.exit(1)

    elif mode == "apps":
        text = fetch_openrouter_apps()
        if text:
            apps = parse_openrouter_apps(text)
            if apps:
                print(format_apps_table(apps))
            else:
                print("No apps found in page content")
        else:
            print("Failed to fetch OpenRouter apps", file=sys.stderr)
            sys.exit(1)

    # Close browser
    run_browser_command(['close'])


if __name__ == "__main__":
    main()