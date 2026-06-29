#!/usr/bin/env python3
"""
Daydreamer — Conductor Script

Manages the mechanical parts of a daydream session:
- Cycle loop (guaranteed count)
- Random number generation (true randomness)
- Memory parsing and retrieval
- State tracking (visited memories, accumulated context)
- Mode dispatch (rolls mode, prepares agent prompts with full context)

The agent handles the creative parts:
- Semantic matching (Mode 1)
- Hypothetical generation and reasoning (Mode 2)
- Web search query construction and insight extraction (Mode 3)
- Analytical questioning (Mode 4)
- Final synthesis

Architecture: The script runs once per cycle. Each invocation reads
the agent's previous response, folds it into accumulated context,
rolls the next mode, and writes a new prompt with the FULL context
from all previous cycles. The agent never has to reconstruct state.

    start       → picks seed, writes prompt for cycle 1
    next-cycle  → reads response N, writes prompt for cycle N+1
    synthesize  → reads last response, writes synthesis prompt
    finalize    → reads synthesis response, writes log, cleans up
"""

import json
import os
import random
import re
import sys
from datetime import datetime, date
from pathlib import Path


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

def workspace_root():
    """Return the workspace root — the directory where Daydreams.MD lives."""
    return Path(os.environ.get("DAYDREAM_WORKSPACE", Path.cwd()))


def dreams_path():
    return workspace_root() / "Daydreams.MD"


def log_path():
    return workspace_root() / "Daydreamlog.MD"


def config_path():
    return workspace_root() / "daydreamer-config.json"


def exchange_dir():
    """Directory for script↔agent JSON exchange files."""
    d = workspace_root() / ".daydream-session"
    d.mkdir(exist_ok=True)
    return d


def state_path():
    """Persistent session state file — the script's memory across invocations."""
    return exchange_dir() / "session_state.json"


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

def load_config():
    path = config_path()
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_config(cfg):
    with open(config_path(), "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2)
        f.write("\n")


def default_config():
    return {
        "frequency": "once_daily",
        "cycles_per_session": 10,
        "default_daydream_type": "full",
        "last_daydream_date": None,
        "last_memory_write_date": None,
    }


# ---------------------------------------------------------------------------
# Daydream types
# ---------------------------------------------------------------------------

DAYDREAM_TYPES = {
    "full": {
        "name": "Full Daydream",
        "synthesis_instructions": (
            "Review the accumulated context from all cycles. Think freely and associatively. "
            "Your output is UNCONSTRAINED — it can be anything that emerges naturally: "
            "a novel idea, a practical recommendation, a question worth investigating, "
            "an observation about patterns, a warning about risks, an analogy, a hypothesis, "
            "or something else entirely. Do not force an idea if what actually emerged is a "
            "question or an observation. Report honestly what the daydream produced."
        ),
    },
    "idea": {
        "name": "Idea Generation",
        "synthesis_instructions": (
            "Review the accumulated context from all cycles. Your goal is to produce a "
            "novel, actionable IDEA — something that could be built, implemented, or pursued. "
            "Look for unexpected connections between the memories visited. What solution, tool, "
            "product, approach, or invention does this combination suggest? The idea should be "
            "something that would not have emerged from any single memory alone. Be specific "
            "and concrete — not just a theme, but a thing someone could act on."
        ),
    },
}


# ---------------------------------------------------------------------------
# Memory parsing
# ---------------------------------------------------------------------------

MEMORY_RE = re.compile(r"^(\d+)\.\s+\[(\d{4}-\d{2}-\d{2})\]\s+(.+)$")


def parse_memories(path=None):
    """Parse Daydreams.MD into a dict of {number: full_line_text}."""
    path = path or dreams_path()
    memories = {}
    if not path.exists():
        return memories
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            m = MEMORY_RE.match(line.strip())
            if m:
                num = int(m.group(1))
                memories[num] = line.strip()
    return memories


def get_memory_text(memories, index):
    """Return the text content of a memory (without the number prefix)."""
    line = memories.get(index, "")
    m = MEMORY_RE.match(line)
    if m:
        return m.group(3)
    return line


def max_memory_number(memories):
    """Return the highest memory number, or 0 if empty."""
    return max(memories.keys()) if memories else 0


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

def load_state():
    """Load persistent session state."""
    path = state_path()
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(state):
    """Save persistent session state."""
    with open(state_path(), "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)


# ---------------------------------------------------------------------------
# Exchange protocol
# ---------------------------------------------------------------------------

def write_prompt(cycle_num, mode, data):
    """Write a prompt file for the agent to pick up."""
    payload = {
        "cycle": cycle_num,
        "mode": mode,
        "data": data,
        "timestamp": datetime.now().isoformat(),
    }
    path = exchange_dir() / f"prompt_cycle_{cycle_num:03d}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return path


def read_response(cycle_num):
    """Read the agent's response file for a given cycle."""
    path = exchange_dir() / f"response_cycle_{cycle_num:03d}.json"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def write_synthesis_prompt(data):
    """Write the final synthesis prompt for the agent."""
    payload = {
        "phase": "synthesis",
        "data": data,
        "timestamp": datetime.now().isoformat(),
    }
    path = exchange_dir() / "prompt_synthesis.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    return path


def read_synthesis_response():
    """Read the agent's synthesis response."""
    path = exchange_dir() / "response_synthesis.json"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Session log
# ---------------------------------------------------------------------------

def write_session_log(seed_index, seed_text, cycles_completed, cycle_log, synthesis, status, daydream_type="full"):
    """Append a session report to Daydreamlog.MD."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    seed_preview = " ".join(seed_text.split()[:20])
    type_name = DAYDREAM_TYPES.get(daydream_type, DAYDREAM_TYPES["full"])["name"]

    cycle_lines = "\n".join(f"- {entry}" for entry in cycle_log)

    entry = f"""
---

## Daydream Session — {now}

**Type:** {type_name}
**Seed memory:** #{seed_index} — {seed_preview}
**Cycles completed:** {cycles_completed}
**Cycle log:**
{cycle_lines}

**Synthesis:**
{synthesis}

**Status:** {status}
"""

    with open(log_path(), "a", encoding="utf-8") as f:
        f.write(entry)


# ---------------------------------------------------------------------------
# Mode names
# ---------------------------------------------------------------------------

MODE_NAMES = {
    1: "Semantic Association",
    2: "Hypothetical Exploration",
    3: "Web Search Excursion",
    4: "Analytical Question",
}


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_start(args):
    """
    Start a new daydream session.
    Picks a random seed, rolls mode for cycle 1, writes the first prompt.
    The prompt contains the seed memory and full memory bank.

    Usage: daydream.py start [--cycles N] [--type full|idea] [--forced]
    """
    cycles = None
    forced = "--forced" in args
    daydream_type = None

    for i, arg in enumerate(args):
        if arg == "--cycles" and i + 1 < len(args):
            cycles = int(args[i + 1])
        if arg == "--type" and i + 1 < len(args):
            daydream_type = args[i + 1]

    # --- Load config ---
    cfg = load_config()
    if cfg is None:
        print(json.dumps({"error": "first_install_needed", "message": "No daydreamer-config.json found. Run: daydream.py init"}))
        return

    if cycles is None:
        cycles = cfg.get("cycles_per_session", 10)

    if daydream_type is None:
        daydream_type = cfg.get("default_daydream_type", "full")

    if daydream_type not in DAYDREAM_TYPES:
        print(json.dumps({"error": "invalid_type", "message": f"Unknown daydream type '{daydream_type}'. Valid types: {', '.join(DAYDREAM_TYPES.keys())}"}))
        return

    # --- Parse memories ---
    memories = parse_memories()
    max_n = max_memory_number(memories)

    if max_n < 2:
        print(json.dumps({
            "error": "insufficient_memories",
            "message": f"Only {max_n} memories found. Need at least 2 to daydream.",
            "memory_count": max_n,
        }))
        return

    # --- Pick seed ---
    seed_index = random.randint(1, max_n)
    while seed_index not in memories and seed_index > 0:
        seed_index -= 1
    if seed_index == 0:
        seed_index = min(memories.keys())

    seed_text = get_memory_text(memories, seed_index)

    # --- Clean exchange dir ---
    ex_dir = exchange_dir()
    for f in ex_dir.iterdir():
        f.unlink()

    # --- Initialize session state ---
    state = {
        "seed_index": seed_index,
        "seed_text": seed_text,
        "total_cycles": cycles,
        "current_cycle": 1,
        "forced": forced,
        "daydream_type": daydream_type,
        "max_memory_number": max_n,
        "visited_memory_indices": [seed_index],
        "accumulated_context": [
            {"source": "seed", "memory_index": seed_index, "text": seed_text}
        ],
        "cycle_log": [],
        "all_memories": {str(k): v for k, v in memories.items()},
    }
    save_state(state)

    # --- Roll mode for cycle 1 and write prompt ---
    mode = random.randint(1, 4)
    prompt_data = build_prompt_data(state, 1, mode)
    write_prompt(1, mode, prompt_data)

    print(json.dumps({
        "status": "session_started",
        "seed_index": seed_index,
        "seed_text": seed_text,
        "total_cycles": cycles,
        "daydream_type": daydream_type,
        "daydream_type_name": DAYDREAM_TYPES[daydream_type]["name"],
        "cycle": 1,
        "mode": mode,
        "mode_name": MODE_NAMES[mode],
        "prompt_file": f"prompt_cycle_001.json",
        "response_file": f"response_cycle_001.json",
    }, indent=2))


def cmd_next_cycle(args):
    """
    Read the agent's response for the current cycle, fold it into
    accumulated context, roll the next mode, and write the next prompt.

    Usage: daydream.py next-cycle
    """
    state = load_state()
    if state is None:
        print(json.dumps({"error": "no_session", "message": "No active session. Run: daydream.py start"}))
        return

    current = state["current_cycle"]
    total = state["total_cycles"]

    # --- Read the agent's response for the current cycle ---
    response = read_response(current)
    if response is None:
        print(json.dumps({
            "error": "no_response",
            "message": f"No response found for cycle {current}. Write response_cycle_{current:03d}.json first.",
        }))
        return

    # --- Fold response into accumulated context ---
    new_memory_index = response.get("selected_memory_index")
    new_text = response.get("text", "")
    log_entry = response.get("log_entry", f"[Cycle {current} | Mode ?] —")

    if new_memory_index:
        state["visited_memory_indices"].append(new_memory_index)

    state["accumulated_context"].append({
        "source": f"cycle_{current}",
        "memory_index": new_memory_index,
        "text": new_text[:500],
    })
    state["cycle_log"].append(log_entry)

    # --- Check if we're done with cycles ---
    next_cycle = current + 1
    if next_cycle > total:
        # All cycles done — write synthesis prompt
        state["current_cycle"] = next_cycle
        save_state(state)

        daydream_type = state.get("daydream_type", "full")
        type_info = DAYDREAM_TYPES.get(daydream_type, DAYDREAM_TYPES["full"])

        synthesis_data = {
            "accumulated_context": state["accumulated_context"],
            "visited_memory_indices": state["visited_memory_indices"],
            "total_cycles": total,
            "seed_index": state["seed_index"],
            "seed_text": state["seed_text"],
            "cycle_log": state["cycle_log"],
            "daydream_type": daydream_type,
            "daydream_type_name": type_info["name"],
            "synthesis_instructions": type_info["synthesis_instructions"],
        }
        write_synthesis_prompt(synthesis_data)

        print(json.dumps({
            "status": "cycles_complete",
            "message": f"All {total} cycles done. Synthesis prompt written.",
            "prompt_file": "prompt_synthesis.json",
            "response_file": "response_synthesis.json",
            "accumulated_context_size": len(state["accumulated_context"]),
            "visited_memories": state["visited_memory_indices"],
        }, indent=2))
        return

    # --- Roll mode for next cycle and write prompt ---
    state["current_cycle"] = next_cycle
    mode = random.randint(1, 4)

    prompt_data = build_prompt_data(state, next_cycle, mode)
    write_prompt(next_cycle, mode, prompt_data)
    save_state(state)

    print(json.dumps({
        "status": "next_cycle_ready",
        "cycle": next_cycle,
        "total_cycles": total,
        "mode": mode,
        "mode_name": MODE_NAMES[mode],
        "prompt_file": f"prompt_cycle_{next_cycle:03d}.json",
        "response_file": f"response_cycle_{next_cycle:03d}.json",
        "accumulated_context_size": len(state["accumulated_context"]),
    }, indent=2))


def build_prompt_data(state, cycle_num, mode):
    """Build the prompt data for a cycle, including full accumulated context."""

    # Build rich context summary from ALL previous cycles
    context_parts = []
    for item in state["accumulated_context"]:
        source = item["source"]
        mem_idx = item.get("memory_index", "?")
        text = item["text"]
        context_parts.append(f"[{source} | memory #{mem_idx}] {text}")

    context_summary = "\n".join(context_parts)

    prompt_data = {
        "mode": mode,
        "mode_name": MODE_NAMES[mode],
        "cycle_number": cycle_num,
        "total_cycles": state["total_cycles"],
        "seed_index": state["seed_index"],
        "accumulated_context": context_summary,
        "visited_memory_indices": state["visited_memory_indices"][:],
        "memory_count": state["max_memory_number"],
        "all_memories": state["all_memories"],
    }

    # Mode-specific additions
    if mode == 3:
        prompt_data["target_result_rank"] = random.randint(1, 10)

    return prompt_data


def write_idea_file(synthesis_text, status, state):
    """Write the daydream's synthesis to a standalone file in ideas/."""
    ideas_dir = workspace_root() / "ideas"
    ideas_dir.mkdir(exist_ok=True)

    # Find next idea number
    existing = sorted(ideas_dir.glob("*.md"))
    if existing:
        # Extract number from filenames like "001-some-title.md"
        nums = []
        for f in existing:
            match = re.match(r"^(\d+)", f.stem)
            if match:
                nums.append(int(match.group(1)))
        next_num = max(nums) + 1 if nums else 1
    else:
        next_num = 1

    # Generate a short slug from the first few words of synthesis
    words = re.sub(r"[^a-z0-9\s]", "", synthesis_text.lower()).split()[:5]
    slug = "-".join(words) if words else "idea"

    filename = f"{next_num:03d}-{slug}.md"
    filepath = ideas_dir / filename

    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    seed_preview = " ".join(state["seed_text"].split()[:15])

    # Build memory trail
    trail_lines = []
    for item in state["accumulated_context"]:
        source = item["source"]
        mem_idx = item.get("memory_index", "?")
        text = item["text"][:120]
        trail_lines.append(f"| {source} | #{mem_idx} | {text} |")
    trail_table = "\n".join(trail_lines)

    cycle_log_lines = "\n".join(f"- {entry}" for entry in state["cycle_log"])

    daydream_type = state.get("daydream_type", "full")
    type_name = DAYDREAM_TYPES.get(daydream_type, DAYDREAM_TYPES["full"])["name"]

    content = f"""# Daydream #{next_num:03d}

**Generated:** {now}
**Type:** {type_name}
**Source:** Daydream session ({len(state['cycle_log'])} cycles, seed memory #{state['seed_index']})
**Status:** {status}

---

## Synthesis

{synthesis_text}

---

## Memory Trail

| Source | Memory | Content |
|--------|--------|---------|
{trail_table}

## Cycle Log

{cycle_log_lines}

---

*Seed memory:* #{state['seed_index']} — {seed_preview}
"""

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)

    return filepath


def cmd_finalize(args):
    """
    Read the synthesis response, write the session log to Daydreamlog.MD,
    update config, and clean up the exchange directory.

    Usage: daydream.py finalize [--forced]
    """
    forced_arg = "--forced" in args

    state = load_state()
    if state is None:
        print(json.dumps({"error": "no_session", "message": "No active session to finalize."}))
        return

    forced = forced_arg or state.get("forced", False)

    # Read synthesis response
    synthesis_resp = read_synthesis_response()
    if synthesis_resp is None:
        print(json.dumps({"error": "no_synthesis", "message": "No synthesis response found. Write response_synthesis.json first."}))
        return

    synthesis_text = synthesis_resp.get("synthesis", "No synthesis produced.")
    status = synthesis_resp.get("status", "Complete")

    # Write to Daydreamlog.MD
    write_session_log(
        seed_index=state["seed_index"],
        seed_text=state["seed_text"],
        cycles_completed=len(state["cycle_log"]),
        cycle_log=state["cycle_log"],
        synthesis=synthesis_text,
        status=status,
        daydream_type=state.get("daydream_type", "full"),
    )

    # Write idea file to ideas/ folder
    idea_path = write_idea_file(
        synthesis_text=synthesis_text,
        status=status,
        state=state,
    )

    # Update config
    if not forced:
        cfg = load_config()
        if cfg:
            cfg["last_daydream_date"] = date.today().isoformat()
            save_config(cfg)

    # Clean up exchange dir
    ex_dir = exchange_dir()
    for f in ex_dir.iterdir():
        f.unlink()
    ex_dir.rmdir()

    daydream_type = state.get("daydream_type", "full")

    print(json.dumps({
        "status": "finalized",
        "daydream_type": daydream_type,
        "daydream_type_name": DAYDREAM_TYPES.get(daydream_type, DAYDREAM_TYPES["full"])["name"],
        "cycles_completed": len(state["cycle_log"]),
        "synthesis": synthesis_text,
        "daydream_status": status,
        "schedule_updated": not forced,
        "idea_file": str(idea_path) if idea_path else None,
    }, indent=2))


# ---------------------------------------------------------------------------
# Utility commands
# ---------------------------------------------------------------------------

def cmd_init():
    """First-install: create config and empty files."""
    if config_path().exists():
        print("Config already exists. Skipping init.")
        return

    save_config(default_config())
    print(f"Created {config_path()}")

    if not dreams_path().exists():
        with open(dreams_path(), "w", encoding="utf-8") as f:
            f.write("# Daydreams Memory Log\n\n<!-- Numbered memory entries below. Do not edit manually. -->\n\n")
        print(f"Created {dreams_path()}")

    if not log_path().exists():
        with open(log_path(), "w", encoding="utf-8") as f:
            f.write("# Daydream Session Log\n\n<!-- Completed daydream session reports are appended below. -->\n\n")
        print(f"Created {log_path()}")

    print("Daydreamer initialized with default settings (once daily, 10 cycles, full daydream type).")
    print("Run: python daydream.py seed-memories  → to populate Daydreams.MD from session logs")


def cmd_seed_memories(args):
    """
    Locate Claude Code session logs and report their paths for the agent to read.
    The agent reads these files and extracts ~50 starter memories.

    Usage: daydream.py seed-memories [--log-dir PATH] [--limit N]
    """
    log_dir_override = None
    limit = 20  # max number of log files to surface

    for i, arg in enumerate(args):
        if arg == "--log-dir" and i + 1 < len(args):
            log_dir_override = args[i + 1]
        if arg == "--limit" and i + 1 < len(args):
            try:
                limit = int(args[i + 1])
            except ValueError:
                pass

    # Current memory count
    memories = parse_memories()
    current_count = len(memories)

    if current_count >= 50:
        print(json.dumps({
            "status": "skipped",
            "message": f"Already have {current_count} memories. Seeding is for initial setup (< 50 memories).",
            "memory_count": current_count,
        }, indent=2))
        return

    # Find Openclaw session logs
    search_dirs = []
    if log_dir_override:
        search_dirs.append(Path(log_dir_override))
    else:
        # Standard Openclaw session log location
        home = Path.home()
        search_dirs = [
            home / ".openclaw" / "agents" / "main" / "sessions",
        ]

    log_files = []
    for search_dir in search_dirs:
        if not search_dir.exists():
            continue
        # Recursively find JSONL files (Claude Code conversation logs)
        for f in sorted(search_dir.rglob("*.jsonl"), key=lambda p: p.stat().st_mtime, reverse=True):
            log_files.append(str(f))
            if len(log_files) >= limit:
                break

    if not log_files:
        print(json.dumps({
            "status": "no_logs_found",
            "message": "No session log files found. Provide --log-dir PATH to specify a custom location.",
            "searched": [str(d) for d in search_dirs],
            "memory_count": current_count,
        }, indent=2))
        return

    print(json.dumps({
        "status": "ready",
        "message": f"Found {len(log_files)} session log file(s). Agent should read these and extract ~{50 - current_count} memories.",
        "memory_count": current_count,
        "memories_needed": max(0, 50 - current_count),
        "log_files": log_files,
        "instructions": (
            "Read each log file. For each meaningful event (decisions, requests, bugs fixed, "
            "things built, insights gained), write one memory using: "
            "python daydream.py add-memory \"<WHO> <WHAT>. <WHY if known.>\""
        ),
    }, indent=2))


def cmd_status():
    """Show current state."""
    cfg = load_config()
    if cfg is None:
        print("Not initialized. Run: python daydream.py init")
        return

    memories = parse_memories()
    max_n = max_memory_number(memories)

    default_type = cfg.get("default_daydream_type", "full")
    type_name = DAYDREAM_TYPES.get(default_type, DAYDREAM_TYPES["full"])["name"]

    print(f"Memories:           {len(memories)} entries (highest #{max_n})")
    print(f"Frequency:          {cfg.get('frequency', 'unknown')}")
    print(f"Cycles per session: {cfg.get('cycles_per_session', 'unknown')}")
    print(f"Default type:       {default_type} ({type_name})")
    print(f"Last daydream:      {cfg.get('last_daydream_date', 'never')}")
    print(f"Last memory write:  {cfg.get('last_memory_write_date', 'never')}")

    # Check if daydream is due
    last = cfg.get("last_daydream_date")
    if last is None or last < date.today().isoformat():
        print("Status:             Daydream is DUE")
    else:
        print("Status:             Already daydreamed today")

    # Check for active session
    if state_path().exists():
        state = load_state()
        if state:
            print(f"Active session:     Cycle {state['current_cycle']}/{state['total_cycles']}")


def cmd_add_memory(text):
    """Append a memory to Daydreams.MD."""
    memories = parse_memories()
    max_n = max_memory_number(memories)
    new_num = max_n + 1
    today = date.today().isoformat()

    line = f"{new_num}. [{today}] {text}\n"

    with open(dreams_path(), "a", encoding="utf-8") as f:
        f.write(line)

    # Update config
    cfg = load_config()
    if cfg:
        cfg["last_memory_write_date"] = today
        save_config(cfg)

    print(f"Memory #{new_num} added.")


def print_usage():
    print("""
Usage: python daydream.py <command> [options]

Commands:
  init                    Create config and empty Daydreams/Daydreamlog files
  seed-memories           Locate session logs for agent to extract ~50 starter memories
    [--log-dir PATH]      Override default log search directory (~/.claude/projects)
    [--limit N]           Max log files to surface (default: 20)
  start [--cycles N]      Start a new daydream session, write prompt for cycle 1
        [--type TYPE]     Daydream type: "full" (open-ended) or "idea" (idea generation)
        [--forced]        Mark as forced (won't update last_daydream_date)
  next-cycle              Read response for current cycle, write prompt for next
                          (or write synthesis prompt if all cycles are done)
  finalize [--forced]     Write session log and clean up after synthesis
  status                  Show config, memory count, and active session info
  add-memory <text>       Append a new memory to Daydreams.MD

Daydream Types:
  full    Open-ended. Output can be an idea, recommendation, question,
          observation, warning, or anything else that emerges.
  idea    Focused on generating a novel, actionable idea.

Flow:
  1. daydream.py start --cycles 10 --type idea
     → Agent reads prompt_cycle_001.json, does creative work,
       writes response_cycle_001.json

  2. daydream.py next-cycle      (repeat for each cycle)
     → Script reads response, builds full context, writes next prompt
     → Agent reads prompt, does creative work, writes response

  3. (after last cycle, next-cycle writes prompt_synthesis.json)
     → Agent reads synthesis prompt, writes response_synthesis.json

  4. daydream.py finalize
     → Writes Daydreamlog.MD, updates config, cleans up

Examples:
  python daydream.py init
  python daydream.py start --cycles 5
  python daydream.py next-cycle
  python daydream.py finalize
  python daydream.py status
  python daydream.py add-memory "User asked Claude to debug a race condition in the auth module caused by missing await on token refresh."
  python daydream.py seed-memories
  python daydream.py seed-memories --log-dir ~/.openclaw/agents/main/sessions
""")


def main():
    if len(sys.argv) < 2:
        print_usage()
        return

    command = sys.argv[1]

    if command == "init":
        cmd_init()
    elif command == "seed-memories":
        cmd_seed_memories(sys.argv[2:])
    elif command == "status":
        cmd_status()
    elif command == "add-memory":
        text = " ".join(sys.argv[2:])
        if not text:
            print("Error: Provide memory text. Example: python daydream.py add-memory \"Fixed a bug.\"")
            return
        cmd_add_memory(text)
    elif command == "start":
        cmd_start(sys.argv[2:])
    elif command == "next-cycle":
        cmd_next_cycle(sys.argv[2:])
    elif command == "finalize":
        cmd_finalize(sys.argv[2:])
    elif command in ("-h", "--help", "help"):
        print_usage()
    else:
        print(f"Unknown command: {command}")
        print_usage()


if __name__ == "__main__":
    main()
