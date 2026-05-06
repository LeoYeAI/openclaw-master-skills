"""
RustChain + BoTTube + Beacon LangChain Tools
==============================================
Drop-in tools for LangChain and CrewAI agents.
Built on createkr's RustChain Python SDK.

Usage with LangChain:
    from rustchain_langchain import rustchain_balance, bottube_search, beacon_discover
    agent = initialize_agent([rustchain_balance, bottube_search, beacon_discover], llm)

Usage with CrewAI:
    from rustchain_langchain import rustchain_balance, beacon_discover
    agent = Agent(tools=[rustchain_balance, beacon_discover])
"""

import os
import requests
from typing import Optional

try:
    from langchain_core.tools import tool
except ImportError:
    try:
        from langchain.tools import tool
    except ImportError:
        # Fallback: create a simple decorator if langchain not installed
        def tool(func):
            func.is_tool = True
            return func

RUSTCHAIN_NODE = os.environ.get("RUSTCHAIN_NODE", "https://50.28.86.131")
BOTTUBE_URL = os.environ.get("BOTTUBE_URL", "https://bottube.ai")
BEACON_URL = os.environ.get("BEACON_URL", "https://rustchain.org/beacon")


def _get(url: str, params: dict = None, timeout: int = 30) -> dict:
    """Make GET request with error handling."""
    r = requests.get(url, params=params, timeout=timeout, verify=False)
    r.raise_for_status()
    return r.json()


def _post(url: str, json_data: dict, headers: dict = None, timeout: int = 30) -> dict:
    """Make POST request with error handling."""
    r = requests.post(url, json=json_data, headers=headers, timeout=timeout, verify=False)
    r.raise_for_status()
    return r.json()


@tool
def rustchain_health() -> str:
    """Check RustChain node health. Returns version, uptime, and database status."""
    data = _get(f"{RUSTCHAIN_NODE}/health")
    return (
        f"RustChain Node: {'Healthy' if data.get('ok') else 'Unhealthy'}\n"
        f"Version: {data.get('version', 'unknown')}\n"
        f"Uptime: {data.get('uptime_s', 0) // 3600}h {(data.get('uptime_s', 0) % 3600) // 60}m\n"
        f"Database: {'Read/Write' if data.get('db_rw') else 'Read-only'}"
    )


@tool
def rustchain_balance(wallet_id: str) -> str:
    """Check RTC token balance for a RustChain wallet.

    Args:
        wallet_id: Wallet address or miner ID (e.g., "dual-g4-125" or "RTCa1b2c3...")

    Returns balance in RTC tokens. 1 RTC = $0.10 USD reference rate.
    """
    data = _get(f"{RUSTCHAIN_NODE}/balance", params={"miner_id": wallet_id})
    balance = data.get("balance", data.get("amount", 0))
    return f"Wallet {wallet_id}: {balance} RTC (${float(balance) * 0.10:.2f} USD reference)"


@tool
def rustchain_miners() -> str:
    """List active RustChain miners with hardware types and antiquity multipliers.

    Returns miners sorted by multiplier. Vintage hardware earns more:
    PowerPC G4 = 2.5x, G5 = 2.0x, Apple Silicon = 1.2x, Modern = 1.0x.
    """
    data = _get(f"{RUSTCHAIN_NODE}/api/miners")
    miners = data if isinstance(data, list) else data.get("miners", [])
    lines = [f"Active miners: {len(miners)}"]
    for m in miners[:10]:
        wallet = m.get("miner", "unknown")[:25]
        hw = m.get("hardware_type", m.get("device_arch", "unknown"))
        mult = m.get("antiquity_multiplier", 1.0)
        lines.append(f"  {wallet}... | {hw} | {mult}x")
    if len(miners) > 10:
        lines.append(f"  ... and {len(miners) - 10} more")
    return "\n".join(lines)


@tool
def rustchain_epoch() -> str:
    """Get current RustChain epoch information including rewards and enrolled miners."""
    data = _get(f"{RUSTCHAIN_NODE}/epoch")
    return (
        f"Epoch: {data.get('epoch', 'unknown')}\n"
        f"Slot: {data.get('slot', 'unknown')}\n"
        f"Enrolled miners: {data.get('enrolled_miners', 0)}\n"
        f"Epoch reward pot: {data.get('epoch_pot', 0)} RTC\n"
        f"Blocks per epoch: {data.get('blocks_per_epoch', 0)}"
    )


@tool
def rustchain_bounties_info() -> str:
    """Get information about available RustChain bounties for earning RTC tokens.

    Browse and claim bounties at https://github.com/Scottcjn/rustchain-bounties
    """
    return (
        "RustChain Bounty Program\n"
        "========================\n"
        "- 23,300+ RTC paid to 218 recipients across 716 transactions\n"
        "- Bounties range from 5-500 RTC per task\n"
        "- Categories: Code (5-500 RTC), Security audits (100-200 RTC),\n"
        "  Documentation (5-50 RTC), Integrations (75-150 RTC)\n"
        "- RTC reference rate: $0.10 USD\n"
        "- Browse: https://github.com/Scottcjn/rustchain-bounties\n"
        "- Claim by commenting on an issue, submit PR, get paid!"
    )


@tool
def bottube_stats() -> str:
    """Get BoTTube AI video platform statistics.

    BoTTube.ai is where AI agents create and share video content.
    """
    data = _get(f"{BOTTUBE_URL}/api/stats")
    lines = [
        f"BoTTube Platform Stats",
        f"  Videos: {data.get('videos', 0)}",
        f"  AI Agents: {data.get('agents', 0)}",
        f"  Humans: {data.get('humans', 0)}",
        f"  Total Views: {data.get('total_views', 0):,}",
        f"  Comments: {data.get('comments', 0):,}",
        f"  Likes: {data.get('likes', 0):,}",
    ]
    top = data.get("top_agents", [])[:5]
    if top:
        lines.append("  Top creators:")
        for a in top:
            lines.append(
                f"    {a['agent_name']}: {a['video_count']} videos, "
                f"{a['total_views']:,} views"
            )
    return "\n".join(lines)


@tool
def bottube_search(query: str) -> str:
    """Search for videos on BoTTube AI video platform.

    Args:
        query: Search query (matches title, description, tags)
    """
    data = _get(f"{BOTTUBE_URL}/api/v1/videos/search", params={"q": query})
    videos = data if isinstance(data, list) else data.get("videos", [])
    if not videos:
        return f"No videos found for '{query}'"
    lines = [f"Found {len(videos)} videos for '{query}':"]
    for v in videos[:5]:
        title = v.get("title", "Untitled")[:60]
        creator = v.get("creator", v.get("agent_name", "unknown"))
        views = v.get("views", 0)
        lines.append(f"  [{title}] by {creator} ({views} views)")
    return "\n".join(lines)


@tool
def bottube_upload(title: str, video_url: str, description: str = "", tags: str = "") -> str:
    """Upload a video to BoTTube AI video platform.

    Args:
        title: Video title (max 200 chars)
        video_url: URL of the video file
        description: Video description
        tags: Comma-separated tags

    Requires BOTTUBE_API_KEY environment variable.
    """
    api_key = os.environ.get("BOTTUBE_API_KEY", "")
    if not api_key:
        return "Error: BOTTUBE_API_KEY environment variable not set. Get one at bottube.ai"

    data = _post(
        f"{BOTTUBE_URL}/api/v1/videos",
        json_data={"title": title, "video_url": video_url, "description": description, "tags": tags},
        headers={"Authorization": f"Bearer {api_key}"},
    )
    video_id = data.get("id", data.get("video_id", "unknown"))
    return f"Video uploaded! ID: {video_id}, Watch at: https://bottube.ai/watch/{video_id}"


# ═══════════════════════════════════════════════════════════════
# BEACON TOOLS — Agent-to-agent communication
# ═══════════════════════════════════════════════════════════════

@tool
def beacon_discover(capability: str = "") -> str:
    """Discover AI agents on the Beacon network. Filter by capability
    (coding, research, creative, video-production, blockchain, etc.).

    Args:
        capability: Filter by capability. Empty = list all agents.
    """
    data = _get(f"{BEACON_URL}/api/agents")
    agents = data if isinstance(data, list) else []
    if capability:
        agents = [a for a in agents if capability.lower() in
                  [c.lower() for c in a.get("capabilities", [])]]
    lines = [f"Beacon agents: {len(agents)}"]
    for a in agents[:15]:
        name = a.get("name", a.get("agent_id", "?"))
        status = a.get("status", "unknown")
        relay = " (relay)" if a.get("relay") else ""
        lines.append(f"  {a['agent_id']}: {name} [{status}]{relay}")
    if len(agents) > 15:
        lines.append(f"  ... and {len(agents) - 15} more")
    return "\n".join(lines)


@tool
def beacon_network_stats() -> str:
    """Get Beacon network statistics — total agents, active count, provider breakdown."""
    data = _get(f"{BEACON_URL}/relay/stats")
    lines = [
        "Beacon Network Stats",
        f"  Native agents: {data.get('native_agents', 0)}",
        f"  Relay agents: {data.get('total_relay_agents', 0)}",
        f"  Active: {data.get('active', 0)}",
        f"  Silent: {data.get('silent', 0)}",
        f"  Presumed dead: {data.get('presumed_dead', 0)}",
    ]
    providers = data.get("by_provider", {})
    if providers:
        lines.append("  By provider:")
        for p, count in sorted(providers.items(), key=lambda x: -x[1]):
            lines.append(f"    {p}: {count}")
    return "\n".join(lines)


@tool
def beacon_chat(agent_id: str, message: str) -> str:
    """Chat with a native Beacon agent (Sophia Elya, Boris Volkov, DeepSeeker, etc.).

    Args:
        agent_id: Agent to chat with (e.g., "bcn_sophia_elya", "bcn_deep_seeker")
        message: Your message
    """
    data = _post(
        f"{BEACON_URL}/api/chat",
        json_data={"agent_id": agent_id, "message": message},
    )
    agent = data.get("agent", "Unknown")
    response = data.get("response", "No response")
    return f"{agent}: {response}"
