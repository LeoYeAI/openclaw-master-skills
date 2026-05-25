"""Terminal UI utilities for last30days skill."""

import os
import sys
import time
import threading
import random
from typing import Optional

# Check if we're in a real terminal (not captured by Claude Code)
IS_TTY = sys.stderr.isatty()

# ANSI color codes
class Colors:
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    RESET = '\033[0m'


BANNER = f"""{Colors.PURPLE}{Colors.BOLD}
  ██╗      █████╗ ███████╗████████╗██████╗  ██████╗ ██████╗  █████╗ ██╗   ██╗███████╗
  ██║     ██╔══██╗██╔════╝╚══██╔══╝╚════██╗██╔═████╗██╔══██╗██╔══██╗╚██╗ ██╔╝██╔════╝
  ██║     ███████║███████╗   ██║    █████╔╝██║██╔██║██║  ██║███████║ ╚████╔╝ ███████╗
  ██║     ██╔══██║╚════██║   ██║    ╚═══██╗████╔╝██║██║  ██║██╔══██║  ╚██╔╝  ╚════██║
  ███████╗██║  ██║███████║   ██║   ██████╔╝╚██████╔╝██████╔╝██║  ██║   ██║   ███████║
  ╚══════╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═════╝  ╚═════╝ ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚══════╝
{Colors.RESET}{Colors.DIM}  30 days of research. 30 seconds of work.{Colors.RESET}
"""

MINI_BANNER = f"""{Colors.PURPLE}{Colors.BOLD}/last30days{Colors.RESET} {Colors.DIM}· researching...{Colors.RESET}"""

# Fun status messages for each phase
REDDIT_MESSAGES = [
    "Diving into Reddit threads...",
    "Scanning subreddits for gold...",
    "Reading what Redditors are saying...",
    "Exploring the front page of the internet...",
    "Finding the good discussions...",
    "Upvoting mentally...",
    "Scrolling through comments...",
]

X_MESSAGES = [
    "Checking what X is buzzing about...",
    "Reading the timeline...",
    "Finding the hot takes...",
    "Scanning tweets and threads...",
    "Discovering trending insights...",
    "Following the conversation...",
    "Reading between the posts...",
]

ENRICHING_MESSAGES = [
    "Getting the juicy details...",
    "Fetching engagement metrics...",
    "Reading top comments...",
    "Extracting insights...",
    "Analyzing discussions...",
]

YOUTUBE_MESSAGES = [
    "Searching YouTube for videos...",
    "Finding relevant video content...",
    "Scanning YouTube channels...",
    "Discovering video discussions...",
    "Fetching transcripts...",
]

PROCESSING_MESSAGES = [
    "Crunching the data...",
    "Scoring and ranking...",
    "Finding patterns...",
    "Removing duplicates...",
    "Organizing findings...",
]

WEB_ONLY_MESSAGES = [
    "Searching the web...",
    "Finding blogs and docs...",
    "Crawling news sites...",
    "Discovering tutorials...",
]

def _build_nux_message(diag: dict = None) -> str:
    """Build conversational NUX message with dynamic source status."""
    if diag:
        reddit = "✓" if diag.get("openai") else "✗"
        x = "✓" if diag.get("x_source") else "✗"
        youtube = "✓" if diag.get("youtube") else "✗"
        web = "✓" if diag.get("web_search_backend") else "✗"
        status_line = f"Reddit {reddit}, X {x}, YouTube {youtube}, Web {web}"
    else:
        status_line = "YouTube ✓, Web ✓, Reddit ✗, X ✗"

    return f"""
I just researched that for you. Here's what I've got right now:

{status_line}

You can unlock more sources with API keys — just ask me how and I'll walk you through it. More sources means better research, but it works fine as-is.

Some examples of what you can do:
- "last30 what are people saying about Figma"
- "last30 watch my biggest competitor every week"
- "last30 watch Peter Steinberger every 30 days"
- "last30 watch AI video tools monthly"
- "last30 what have you found about AI video?"

Just start with "last30" and talk to me like normal.
"""

# Shorter promo for single missing key
PROMO_SINGLE_KEY = {
    "reddit": "\n💡 You can unlock Reddit with an OpenAI API key — just ask me how.\n",
    "x": "\n💡 You can unlock X with an xAI API key — just ask me how.\n",
}

# Bird auth help (for local users with vendored Bird CLI)
BIRD_AUTH_HELP = f"""
{Colors.YELLOW}Bird authentication failed.{Colors.RESET}

To fix this:
1. Log into X (twitter.com) in Safari, Chrome, or Firefox
2. Try again — Bird reads your browser cookies automatically.
"""

BIRD_AUTH_HELP_PLAIN = """
Bird authentication failed.

To fix this:
1. Log into X (twitter.com) in Safari, Chrome, or Firefox
2. Try again — Bird reads your browser cookies automatically.
"""

# Spinner frames
SPINNER_FRAMES = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏']
DOTS_FRAMES = ['   ', '.  ', '.. ', '...']


class Spinner:
    """Animated spinner for long-running operations."""

    def __init__(self, message: str = "Working", color: str = Colors.CYAN):
        self.message = message
        self.color = color
        self.running = False
        self.thread: Optional[threading.Thread] = None
        self.frame_idx = 0
        self.shown_static = False

    def _spin(self):
        while self.running:
            frame = SPINNER_FRAMES[self.frame_idx % len(SPINNER_FRAMES)]
            sys.stderr.write(f"\r{self.color}{frame}{Colors.RESET} {self.message}  ")
            sys.stderr.flush()
            self.frame_idx += 1
            time.sleep(0.08)

    def start(self):
        self.running = True
        if IS_TTY:
            # Real terminal - animate
            self.thread = threading.Thread(target=self._spin, daemon=True)
            self.thread.start()
        else:
            # Not a TTY (Claude Code) - just print once
            if not self.shown_static:
                sys.stderr.write(f"⏳ {self.message}\n")
                sys.stderr.flush()
                self.shown_static = True

    def update(self, message: str):
        self.message = message
        if not IS_TTY and not self.shown_static:
            # Print update in non-TTY mode
            sys.stderr.write(f"⏳ {message}\n")
            sys.stderr.flush()

    def stop(self, final_message: str = ""):
        self.running = False
        if self.thread:
            self.thread.join(timeout=0.2)
        if IS_TTY:
            # Clear the line in real terminal
            sys.stderr.write("\r" + " " * 80 + "\r")
        if final_message:
            sys.stderr.write(f"✓ {final_message}\n")
        sys.stderr.flush()


class ProgressDisplay:
    """Progress display for research phases."""

    def __init__(self, topic: str, show_banner: bool = True):
        self.topic = topic
        self.spinner: Optional[Spinner] = None
        self.start_time = time.time()

        if show_banner:
            self._show_banner()

    def _show_banner(self):
        if IS_TTY:
            sys.stderr.write(MINI_BANNER + "\n")
            sys.stderr.write(f"{Colors.DIM}Topic: {Colors.RESET}{Colors.BOLD}{self.topic}{Colors.RESET}\n\n")
        else:
            # Simple text for non-TTY
            sys.stderr.write(f"/last30days · researching: {self.topic}\n")
        sys.stderr.flush()

    def start_reddit(self):
        msg = random.choice(REDDIT_MESSAGES)
        self.spinner = Spinner(f"{Colors.YELLOW}Reddit{Colors.RESET} {msg}", Colors.YELLOW)
        self.spinner.start()

    def end_reddit(self, count: int):
        if self.spinner:
            self.spinner.stop(f"{Colors.YELLOW}Reddit{Colors.RESET} Found {count} threads")

    def start_reddit_enrich(self, current: int, total: int):
        if self.spinner:
            self.spinner.stop()
        msg = random.choice(ENRICHING_MESSAGES)
        self.spinner = Spinner(f"{Colors.YELLOW}Reddit{Colors.RESET} [{current}/{total}] {msg}", Colors.YELLOW)
        self.spinner.start()

    def update_reddit_enrich(self, current: int, total: int):
        if self.spinner:
            msg = random.choice(ENRICHING_MESSAGES)
            self.spinner.update(f"{Colors.YELLOW}Reddit{Colors.RESET} [{current}/{total}] {msg}")

    def end_reddit_enrich(self):
        if self.spinner:
            self.spinner.stop(f"{Colors.YELLOW}Reddit{Colors.RESET} Enriched with engagement data")

    def start_x(self):
        msg = random.choice(X_MESSAGES)
        self.spinner = Spinner(f"{Colors.CYAN}X{Colors.RESET} {msg}", Colors.CYAN)
        self.spinner.start()

    def end_x(self, count: int):
        if self.spinner:
            self.spinner.stop(f"{Colors.CYAN}X{Colors.RESET} Found {count} posts")

    def start_youtube(self):
        msg = random.choice(YOUTUBE_MESSAGES)
        self.spinner = Spinner(f"{Colors.RED}YouTube{Colors.RESET} {msg}", Colors.RED)
        self.spinner.start()

    def end_youtube(self, count: int):
        if self.spinner:
            self.spinner.stop(f"{Colors.RED}YouTube{Colors.RESET} Found {count} videos")

    def start_processing(self):
        msg = random.choice(PROCESSING_MESSAGES)
        self.spinner = Spinner(f"{Colors.PURPLE}Processing{Colors.RESET} {msg}", Colors.PURPLE)
        self.spinner.start()

    def end_processing(self):
        if self.spinner:
            self.spinner.stop()

    def show_complete(self, reddit_count: int, x_count: int, youtube_count: int = 0):
        elapsed = time.time() - self.start_time
        if IS_TTY:
            sys.stderr.write(f"\n{Colors.GREEN}{Colors.BOLD}✓ Research complete{Colors.RESET} ")
            sys.stderr.write(f"{Colors.DIM}({elapsed:.1f}s){Colors.RESET}\n")
            sys.stderr.write(f"  {Colors.YELLOW}Reddit:{Colors.RESET} {reddit_count} threads  ")
            sys.stderr.write(f"{Colors.CYAN}X:{Colors.RESET} {x_count} posts")
            if youtube_count:
                sys.stderr.write(f"  {Colors.RED}YouTube:{Colors.RESET} {youtube_count} videos")
            sys.stderr.write("\n\n")
        else:
            parts = [f"Reddit: {reddit_count} threads", f"X: {x_count} posts"]
            if youtube_count:
                parts.append(f"YouTube: {youtube_count} videos")
            sys.stderr.write(f"✓ Research complete ({elapsed:.1f}s) - {', '.join(parts)}\n")
        sys.stderr.flush()

    def show_cached(self, age_hours: float = None):
        if age_hours is not None:
            age_str = f" ({age_hours:.1f}h old)"
        else:
            age_str = ""
        sys.stderr.write(f"{Colors.GREEN}⚡{Colors.RESET} {Colors.DIM}Using cached results{age_str} - use --refresh for fresh data{Colors.RESET}\n\n")
        sys.stderr.flush()

    def show_error(self, message: str):
        sys.stderr.write(f"{Colors.RED}✗ Error:{Colors.RESET} {message}\n")
        sys.stderr.flush()

    def start_web_only(self):
        """Show web-only mode indicator."""
        msg = random.choice(WEB_ONLY_MESSAGES)
        self.spinner = Spinner(f"{Colors.GREEN}Web{Colors.RESET} {msg}", Colors.GREEN)
        self.spinner.start()

    def end_web_only(self):
        """End web-only spinner."""
        if self.spinner:
            self.spinner.stop(f"{Colors.GREEN}Web{Colors.RESET} assistant will search the web")

    def show_web_only_complete(self):
        """Show completion for web-only mode."""
        elapsed = time.time() - self.start_time
        if IS_TTY:
            sys.stderr.write(f"\n{Colors.GREEN}{Colors.BOLD}✓ Ready for web search{Colors.RESET} ")
            sys.stderr.write(f"{Colors.DIM}({elapsed:.1f}s){Colors.RESET}\n")
            sys.stderr.write(f"  {Colors.GREEN}Web:{Colors.RESET} assistant will search blogs, docs & news\n\n")
        else:
            sys.stderr.write(f"✓ Ready for web search ({elapsed:.1f}s)\n")
        sys.stderr.flush()

    def show_promo(self, missing: str = "both", diag: dict = None):
        """Show NUX / promotional message for missing API keys.

        Args:
            missing: 'both', 'all', 'reddit', or 'x' - which keys are missing
            diag: Optional diagnostics dict for dynamic source status
        """
        if missing in ("both", "all"):
            sys.stderr.write(_build_nux_message(diag))
        elif missing in PROMO_SINGLE_KEY:
            sys.stderr.write(PROMO_SINGLE_KEY[missing])
        sys.stderr.flush()

    def show_bird_auth_help(self):
        """Show Bird authentication help."""
        if IS_TTY:
            sys.stderr.write(BIRD_AUTH_HELP)
        else:
            sys.stderr.write(BIRD_AUTH_HELP_PLAIN)
        sys.stderr.flush()


def show_diagnostic_banner(diag: dict):
    """Show pre-flight source status banner when sources are missing.

    Args:
        diag: Dict from env diagnostics with keys:
            openai, xai, x_source, bird_installed, bird_authenticated,
            bird_username, youtube, web_search_backend
    """
    has_openai = diag.get("openai", False)
    has_x = diag.get("x_source") is not None
    has_youtube = diag.get("youtube", False)
    has_web = diag.get("web_search_backend") is not None

    # If everything is available, no banner needed
    if has_openai and has_x and has_youtube and has_web:
        return

    lines = []

    if IS_TTY:
        lines.append(f"{Colors.DIM}┌─────────────────────────────────────────────────────┐{Colors.RESET}")
        lines.append(f"{Colors.DIM}│{Colors.RESET} {Colors.BOLD}/last30days v2.1 — Source Status{Colors.RESET}                    {Colors.DIM}│{Colors.RESET}")
        lines.append(f"{Colors.DIM}│{Colors.RESET}                                                     {Colors.DIM}│{Colors.RESET}")

        # Reddit
        if has_openai:
            lines.append(f"{Colors.DIM}│{Colors.RESET}  {Colors.GREEN}✅ Reddit{Colors.RESET}    — OPENAI_API_KEY found                {Colors.DIM}│{Colors.RESET}")
        else:
            lines.append(f"{Colors.DIM}│{Colors.RESET}  {Colors.RED}❌ Reddit{Colors.RESET}    — No OPENAI_API_KEY                    {Colors.DIM}│{Colors.RESET}")
            lines.append(f"{Colors.DIM}│{Colors.RESET}     └─ Add to ~/.config/last30days/.env            {Colors.DIM}│{Colors.RESET}")

        # X/Twitter
        if has_x:
            source = diag.get("x_source", "")
            username = diag.get("bird_username", "")
            label = f"Bird ({username})" if source == "bird" and username else source.upper()
            lines.append(f"{Colors.DIM}│{Colors.RESET}  {Colors.GREEN}✅ X/Twitter{Colors.RESET} — {label}                          {Colors.DIM}│{Colors.RESET}")
        else:
            lines.append(f"{Colors.DIM}│{Colors.RESET}  {Colors.RED}❌ X/Twitter{Colors.RESET} — No Bird CLI or XAI_API_KEY          {Colors.DIM}│{Colors.RESET}")
            if diag.get("bird_installed"):
                lines.append(f"{Colors.DIM}│{Colors.RESET}     └─ Bird installed but not authenticated         {Colors.DIM}│{Colors.RESET}")
                lines.append(f"{Colors.DIM}│{Colors.RESET}     └─ Log into x.com in your browser, then retry   {Colors.DIM}│{Colors.RESET}")
            else:
                lines.append(f"{Colors.DIM}│{Colors.RESET}     └─ Needs Node.js 22+ (Bird is bundled)           {Colors.DIM}│{Colors.RESET}")

        # YouTube
        if has_youtube:
            lines.append(f"{Colors.DIM}│{Colors.RESET}  {Colors.GREEN}✅ YouTube{Colors.RESET}   — yt-dlp found                      {Colors.DIM}│{Colors.RESET}")
        else:
            lines.append(f"{Colors.DIM}│{Colors.RESET}  {Colors.RED}❌ YouTube{Colors.RESET}   — yt-dlp not installed                {Colors.DIM}│{Colors.RESET}")
            lines.append(f"{Colors.DIM}│{Colors.RESET}     └─ Fix: brew install yt-dlp (free)                {Colors.DIM}│{Colors.RESET}")

        # Web
        if has_web:
            backend = diag.get("web_search_backend", "")
            lines.append(f"{Colors.DIM}│{Colors.RESET}  {Colors.GREEN}✅ Web{Colors.RESET}       — {backend} API                       {Colors.DIM}│{Colors.RESET}")
        else:
            lines.append(f"{Colors.DIM}│{Colors.RESET}  {Colors.YELLOW}⚡ Web{Colors.RESET}       — Using assistant's search tool       {Colors.DIM}│{Colors.RESET}")

        lines.append(f"{Colors.DIM}│{Colors.RESET}                                                     {Colors.DIM}│{Colors.RESET}")
        lines.append(f"{Colors.DIM}│{Colors.RESET}  Config: {Colors.BOLD}~/.config/last30days/.env{Colors.RESET}                  {Colors.DIM}│{Colors.RESET}")
        lines.append(f"{Colors.DIM}└─────────────────────────────────────────────────────┘{Colors.RESET}")
    else:
        # Plain text for non-TTY (Claude Code / Codex)
        lines.append("┌─────────────────────────────────────────────────────┐")
        lines.append("│ /last30days v2.1 — Source Status                    │")
        lines.append("│                                                     │")

        if has_openai:
            lines.append("│  ✅ Reddit    — OPENAI_API_KEY found                │")
        else:
            lines.append("│  ❌ Reddit    — No OPENAI_API_KEY                    │")
            lines.append("│     └─ Add to ~/.config/last30days/.env            │")

        if has_x:
            lines.append("│  ✅ X/Twitter — available                            │")
        else:
            lines.append("│  ❌ X/Twitter — No Bird CLI or XAI_API_KEY          │")
            if diag.get("bird_installed"):
                lines.append("│     └─ Log into x.com in your browser, then retry   │")
            else:
                lines.append("│     └─ Needs Node.js 22+ (Bird is bundled)           │")

        if has_youtube:
            lines.append("│  ✅ YouTube   — yt-dlp found                        │")
        else:
            lines.append("│  ❌ YouTube   — yt-dlp not installed                │")
            lines.append("│     └─ Fix: brew install yt-dlp (free)                │")

        if has_web:
            lines.append("│  ✅ Web       — API search available                │")
        else:
            lines.append("│  ⚡ Web       — Using assistant's search tool       │")

        lines.append("│                                                     │")
        lines.append("│  Config: ~/.config/last30days/.env                  │")
        lines.append("└─────────────────────────────────────────────────────┘")

    sys.stderr.write("\n".join(lines) + "\n\n")
    sys.stderr.flush()


def print_phase(phase: str, message: str):
    """Print a phase message."""
    colors = {
        "reddit": Colors.YELLOW,
        "x": Colors.CYAN,
        "process": Colors.PURPLE,
        "done": Colors.GREEN,
        "error": Colors.RED,
    }
    color = colors.get(phase, Colors.RESET)
    sys.stderr.write(f"{color}▸{Colors.RESET} {message}\n")
    sys.stderr.flush()
