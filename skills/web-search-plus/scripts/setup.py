#!/usr/bin/env python3
"""
Web Search Plus - Interactive Setup Wizard
==========================================

Runs on first use (when no config.json exists) to configure providers and API keys.
Creates config.json with your settings. API keys are stored locally only.

Usage:
    python3 scripts/setup.py          # Interactive setup
    python3 scripts/setup.py --reset  # Reset and reconfigure
"""

import json
import os
import sys
from pathlib import Path

# ANSI colors for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'

def color(text: str, c: str) -> str:
    """Wrap text in color codes."""
    return f"{c}{text}{Colors.RESET}"

def print_header():
    """Print the setup wizard header."""
    print()
    print(color("╔════════════════════════════════════════════════════════════╗", Colors.CYAN))
    print(color("║          🔍 Web Search Plus - Setup Wizard                 ║", Colors.CYAN))
    print(color("╚════════════════════════════════════════════════════════════╝", Colors.CYAN))
    print()
    print(color("This wizard will help you configure your search providers.", Colors.DIM))
    print(color("API keys are stored locally in config.json (gitignored).", Colors.DIM))
    print()

def print_provider_info():
    """Print information about each provider."""
    print(color("📚 Available Providers:", Colors.BOLD))
    print()
    
    providers = [
        {
            "name": "Serper",
            "emoji": "🔎",
            "best_for": "Google results, shopping, local businesses, news",
            "free_tier": "2,500 queries/month",
            "signup": "https://serper.dev",
            "strengths": ["Fastest response times", "Product prices & specs", "Knowledge Graph", "Local business data"]
        },
        {
            "name": "Tavily", 
            "emoji": "📖",
            "best_for": "Research, explanations, in-depth analysis",
            "free_tier": "1,000 queries/month",
            "signup": "https://tavily.com",
            "strengths": ["AI-synthesized answers", "Full page content", "Domain filtering", "Academic research"]
        },
        {
            "name": "Exa",
            "emoji": "🧠",
            "best_for": "Semantic search, finding similar content, discovery",
            "free_tier": "1,000 queries/month", 
            "signup": "https://exa.ai",
            "strengths": ["Neural/semantic understanding", "Similar page discovery", "Startup/company finder", "Date filtering"]
        },
        {
            "name": "You.com",
            "emoji": "🤖",
            "best_for": "RAG applications, real-time info, LLM-ready snippets",
            "free_tier": "Limited free tier",
            "signup": "https://api.you.com",
            "strengths": ["LLM-ready snippets", "Combined web + news", "Live page crawling", "Real-time information"]
        },
        {
            "name": "SearXNG",
            "emoji": "🔒",
            "best_for": "Privacy-first search, multi-source aggregation, $0 API cost",
            "free_tier": "FREE (self-hosted)",
            "signup": "https://docs.searxng.org/admin/installation.html",
            "strengths": ["Privacy-preserving (no tracking)", "70+ search engines", "Self-hosted = $0 API cost", "Diverse results"]
        }
    ]
    
    for p in providers:
        print(f"  {p['emoji']} {color(p['name'], Colors.BOLD)}")
        print(f"     Best for: {color(p['best_for'], Colors.GREEN)}")
        print(f"     Free tier: {p['free_tier']}")
        print(f"     Sign up: {color(p['signup'], Colors.BLUE)}")
        print()

def ask_yes_no(prompt: str, default: bool = True) -> bool:
    """Ask a yes/no question."""
    suffix = "[Y/n]" if default else "[y/N]"
    while True:
        response = input(f"{prompt} {color(suffix, Colors.DIM)}: ").strip().lower()
        if response == "":
            return default
        if response in ("y", "yes"):
            return True
        if response in ("n", "no"):
            return False
        print(color("  Please enter 'y' or 'n'", Colors.YELLOW))

def ask_choice(prompt: str, options: list, default: str = None) -> str:
    """Ask user to choose from a list of options."""
    print(f"\n{prompt}")
    for i, opt in enumerate(options, 1):
        marker = color("→", Colors.GREEN) if opt == default else " "
        print(f"  {marker} {i}. {opt}")
    
    while True:
        hint = f" [default: {default}]" if default else ""
        response = input(f"Enter number (1-{len(options)}){color(hint, Colors.DIM)}: ").strip()
        
        if response == "" and default:
            return default
        
        try:
            idx = int(response)
            if 1 <= idx <= len(options):
                return options[idx - 1]
        except ValueError:
            pass
        
        print(color(f"  Please enter a number between 1 and {len(options)}", Colors.YELLOW))

def ask_api_key(provider: str, signup_url: str) -> str:
    """Ask for an API key with validation."""
    print()
    print(f"  {color(f'Get your {provider} API key:', Colors.DIM)} {color(signup_url, Colors.BLUE)}")
    
    while True:
        key = input(f"  Enter your {provider} API key: ").strip()
        
        if not key:
            print(color("    ⚠️  No key entered. This provider will be disabled.", Colors.YELLOW))
            return None
        
        # Basic validation
        if len(key) < 10:
            print(color("    ⚠️  Key seems too short. Please check and try again.", Colors.YELLOW))
            continue
        
        # Mask key for confirmation
        masked = key[:4] + "..." + key[-4:] if len(key) > 12 else key[:2] + "..."
        print(color(f"    ✓ Key saved: {masked}", Colors.GREEN))
        return key


def ask_searxng_instance(docs_url: str) -> str:
    """Ask for SearXNG instance URL with connection test."""
    print()
    print(f"  {color('SearXNG is self-hosted. You need your own instance.', Colors.DIM)}")
    print(f"  {color('Setup guide:', Colors.DIM)} {color(docs_url, Colors.BLUE)}")
    print()
    print(f"  {color('Example URLs:', Colors.DIM)}")
    print(f"    • http://localhost:8080 (local Docker)")
    print(f"    • https://searx.your-domain.com (self-hosted)")
    print()
    
    while True:
        url = input(f"  Enter your SearXNG instance URL: ").strip()
        
        if not url:
            print(color("    ⚠️  No URL entered. SearXNG will be disabled.", Colors.YELLOW))
            return None
        
        # Basic URL validation
        if not url.startswith(("http://", "https://")):
            print(color("    ⚠️  URL must start with http:// or https://", Colors.YELLOW))
            continue
        
        # SSRF protection: validate URL before connecting
        try:
            import ipaddress
            import socket
            from urllib.parse import urlparse as _urlparse
            _parsed = _urlparse(url)
            _hostname = _parsed.hostname or ""
            _blocked = {"169.254.169.254", "metadata.google.internal", "metadata.internal"}
            if _hostname in _blocked:
                print(color(f"    ❌ Blocked: {_hostname} is a cloud metadata endpoint.", Colors.RED))
                continue
            if not os.environ.get("SEARXNG_ALLOW_PRIVATE", "").strip() == "1":
                _resolved = socket.getaddrinfo(_hostname, _parsed.port or 80, proto=socket.IPPROTO_TCP)
                for _fam, _t, _p, _cn, _sa in _resolved:
                    _ip = ipaddress.ip_address(_sa[0])
                    if _ip.is_loopback or _ip.is_private or _ip.is_link_local or _ip.is_reserved:
                        print(color(f"    ❌ Blocked: {_hostname} resolves to private IP {_ip}.", Colors.RED))
                        print(color(f"       Set SEARXNG_ALLOW_PRIVATE=1 if intentional.", Colors.DIM))
                        raise ValueError("private_ip")
        except ValueError as _ve:
            if str(_ve) == "private_ip":
                continue
            raise
        except socket.gaierror:
            print(color(f"    ❌ Cannot resolve hostname: {_hostname}", Colors.RED))
            continue

        # Test connection
        print(color(f"    Testing connection to {url}...", Colors.DIM))
        try:
            import urllib.request
            import urllib.error
            
            test_url = f"{url.rstrip('/')}/search?q=test&format=json"
            req = urllib.request.Request(
                test_url,
                headers={"User-Agent": "ClawdBot-WebSearchPlus/2.5", "Accept": "application/json"}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                data = response.read().decode("utf-8")
                import json
                result = json.loads(data)
                
                # Check if it looks like SearXNG JSON response
                if "results" in result or "query" in result:
                    print(color(f"    ✓ Connection successful! SearXNG instance is working.", Colors.GREEN))
                    return url.rstrip("/")
                else:
                    print(color(f"    ⚠️  Connected but response doesn't look like SearXNG JSON.", Colors.YELLOW))
                    if ask_yes_no("    Use this URL anyway?", default=False):
                        return url.rstrip("/")
                        
        except urllib.error.HTTPError as e:
            if e.code == 403:
                print(color(f"    ⚠️  JSON API is disabled (403 Forbidden).", Colors.YELLOW))
                print(color(f"       Enable JSON in settings.yml: search.formats: [html, json]", Colors.DIM))
            else:
                print(color(f"    ⚠️  HTTP error: {e.code} {e.reason}", Colors.YELLOW))
            
            if ask_yes_no("    Try a different URL?", default=True):
                continue
            return None
            
        except urllib.error.URLError as e:
            print(color(f"    ⚠️  Cannot reach instance: {e.reason}", Colors.YELLOW))
            if ask_yes_no("    Try a different URL?", default=True):
                continue
            return None
            
        except Exception as e:
            print(color(f"    ⚠️  Error: {e}", Colors.YELLOW))
            if ask_yes_no("    Try a different URL?", default=True):
                continue
            return None

def ask_result_count() -> int:
    """Ask for default result count."""
    options = ["3 (fast, minimal)", "5 (balanced - recommended)", "10 (comprehensive)"]
    choice = ask_choice("Default number of results per search?", options, "5 (balanced - recommended)")
    
    if "3" in choice:
        return 3
    elif "10" in choice:
        return 10
    return 5

def run_setup(skill_dir: Path, force_reset: bool = False):
    """Run the interactive setup wizard."""
    config_path = skill_dir / "config.json"
    example_path = skill_dir / "config.example.json"
    
    # Check if config already exists
    if config_path.exists() and not force_reset:
        print(color("✓ config.json already exists!", Colors.GREEN))
        print()
        if not ask_yes_no("Do you want to reconfigure?", default=False):
            print(color("Setup cancelled. Your existing config is unchanged.", Colors.DIM))
            return False
        print()
    
    print_header()
    print_provider_info()
    
    # Load example config as base
    if example_path.exists():
        with open(example_path) as f:
            config = json.load(f)
    else:
        config = {
            "defaults": {"provider": "serper", "max_results": 5},
            "auto_routing": {"enabled": True, "fallback_provider": "serper"},
            "serper": {},
            "tavily": {},
            "exa": {}
        }
    
    # Remove any existing API keys from example
    for provider in ["serper", "tavily", "exa"]:
        if provider in config:
            config[provider].pop("api_key", None)
    
    enabled_providers = []
    
    # ===== Question 1: Which providers to enable =====
    print(color("─" * 60, Colors.DIM))
    print(color("\n📋 Step 1: Choose Your Providers\n", Colors.BOLD))
    print("Select which search providers you want to enable.")
    print(color("(You need at least one API key to use this skill)", Colors.DIM))
    print()
    
    providers_info = {
        "serper": ("Serper", "https://serper.dev", "Google results, shopping, local"),
        "tavily": ("Tavily", "https://tavily.com", "Research, explanations, analysis"),
        "exa": ("Exa", "https://exa.ai", "Semantic search, similar content"),
        "you": ("You.com", "https://api.you.com", "RAG applications, real-time info"),
        "searxng": ("SearXNG", "https://docs.searxng.org/admin/installation.html", "Privacy-first, self-hosted, $0 cost")
    }
    
    for provider, (name, url, desc) in providers_info.items():
        print(f"  {color(name, Colors.BOLD)}: {desc}")
        
        # Special handling for SearXNG
        if provider == "searxng":
            print(color("    Note: SearXNG requires a self-hosted instance (no API key needed)", Colors.DIM))
            if ask_yes_no(f"    Do you have a SearXNG instance?", default=False):
                instance_url = ask_searxng_instance(url)
                if instance_url:
                    if "searxng" not in config:
                        config["searxng"] = {}
                    config["searxng"]["instance_url"] = instance_url
                    enabled_providers.append(provider)
                else:
                    print(color(f"    → {name} disabled (no instance URL)", Colors.DIM))
            else:
                print(color(f"    → {name} skipped (no instance)", Colors.DIM))
        else:
            if ask_yes_no(f"    Enable {name}?", default=True):
                # ===== Question 2: API key for each enabled provider =====
                api_key = ask_api_key(name, url)
                if api_key:
                    config[provider]["api_key"] = api_key
                    enabled_providers.append(provider)
                else:
                    print(color(f"    → {name} disabled (no API key)", Colors.DIM))
            else:
                print(color(f"    → {name} disabled", Colors.DIM))
        print()
    
    if not enabled_providers:
        print()
        print(color("⚠️  No providers enabled!", Colors.RED))
        print("You need at least one API key to use web-search-plus.")
        print("Run this setup again when you have an API key.")
        return False
    
    # ===== Question 3: Default provider =====
    print(color("─" * 60, Colors.DIM))
    print(color("\n⚙️  Step 2: Default Settings\n", Colors.BOLD))
    
    if len(enabled_providers) > 1:
        default_provider = ask_choice(
            "Which provider should be the default for general queries?",
            enabled_providers,
            enabled_providers[0]
        )
    else:
        default_provider = enabled_providers[0]
        print(f"Default provider: {color(default_provider, Colors.GREEN)} (only one enabled)")
    
    config["defaults"]["provider"] = default_provider
    config["auto_routing"]["fallback_provider"] = default_provider
    
    # ===== Question 4: Auto-routing =====
    print()
    print(color("Auto-routing", Colors.BOLD) + " automatically picks the best provider for each query:")
    print(color("  • 'iPhone price' → Serper (shopping intent)", Colors.DIM))
    print(color("  • 'how does TCP work' → Tavily (research intent)", Colors.DIM))  
    print(color("  • 'companies like Stripe' → Exa (discovery intent)", Colors.DIM))
    print()
    
    auto_routing = ask_yes_no("Enable auto-routing?", default=True)
    config["auto_routing"]["enabled"] = auto_routing
    
    if not auto_routing:
        print(color(f"  → All queries will use {default_provider}", Colors.DIM))
    
    # ===== Question 5: Result count =====
    print()
    max_results = ask_result_count()
    config["defaults"]["max_results"] = max_results
    
    # Set disabled providers
    all_providers = ["serper", "tavily", "exa", "you", "searxng"]
    disabled = [p for p in all_providers if p not in enabled_providers]
    config["auto_routing"]["disabled_providers"] = disabled
    
    # ===== Save config =====
    print()
    print(color("─" * 60, Colors.DIM))
    print(color("\n💾 Saving Configuration\n", Colors.BOLD))
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(color(f"✓ Configuration saved to: {config_path}", Colors.GREEN))
    print()
    
    # ===== Summary =====
    print(color("📋 Configuration Summary:", Colors.BOLD))
    print(f"   Enabled providers: {', '.join(enabled_providers)}")
    print(f"   Default provider: {default_provider}")
    print(f"   Auto-routing: {'enabled' if auto_routing else 'disabled'}")
    print(f"   Results per search: {max_results}")
    print()
    
    # ===== Test suggestion =====
    print(color("🚀 Ready to search! Try:", Colors.BOLD))
    print(color(f"   python3 scripts/search.py -q \"your query here\"", Colors.CYAN))
    print()
    
    return True

def check_first_run(skill_dir: Path) -> bool:
    """Check if this is the first run (no config.json)."""
    config_path = skill_dir / "config.json"
    return not config_path.exists()

def main():
    # Determine skill directory
    script_path = Path(__file__).resolve()
    skill_dir = script_path.parent.parent
    
    # Check for --reset flag
    force_reset = "--reset" in sys.argv
    
    # Check for --check flag (just check if setup needed)
    if "--check" in sys.argv:
        if check_first_run(skill_dir):
            print("Setup required: config.json not found")
            sys.exit(1)
        else:
            print("Setup complete: config.json exists")
            sys.exit(0)
    
    # Run setup
    success = run_setup(skill_dir, force_reset)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
