#!/usr/bin/env python3
"""
Context optimizer - Analyze and minimize context loading.
Tracks which files are actually needed and creates minimal bundles.
"""
import json
import re
import sys
from pathlib import Path
from datetime import datetime, timedelta

# Add skill root to path to import config
sys.path.append(str(Path(__file__).parent.parent))
from config import TIER_MODELS

STATE_FILE = Path.home() / ".openclaw/workspace/memory/context-usage.json"

# Files that should ALWAYS be loaded (identity/personality)
ALWAYS_LOAD = [
    "SOUL.md",
    "IDENTITY.md"
]

# Files to load on-demand based on triggers
CONDITIONAL_FILES = {
    "AGENTS.md": ["workflow", "process", "how do i", "remember", "what should"],
    "USER.md": ["user", "human", "owner", "about you", "who are you helping"],
    "TOOLS.md": ["tool", "camera", "ssh", "voice", "tts", "device"],
    "MEMORY.md": ["remember", "recall", "history", "past", "before", "last time"],
    "HEARTBEAT.md": ["heartbeat", "check", "monitor", "alert"],
}

# Files to NEVER load for simple conversations
SKIP_FOR_SIMPLE = [
    "docs/**/*.md",  # Documentation
    "memory/20*.md",  # Old daily logs
    "knowledge/**/*",  # Knowledge base
    "tasks/**/*",  # Task tracking
]

def load_usage_state():
    """Load context usage tracking."""
    if STATE_FILE.exists():
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    return {
        "file_access_count": {},
        "last_accessed": {},
        "session_summaries": []
    }

def save_usage_state(state):
    """Save context usage tracking."""
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(STATE_FILE, 'w') as f:
        json.dump(state, f, indent=2)

def classify_prompt(prompt):
    """Classify prompt to determine context needs.
    
    Returns:
        tuple of (complexity, context_level, reasoning)
        
    complexity: simple | medium | complex
    context_level: minimal | standard | full
    """
    prompt_lower = prompt.lower()
    
    # Simple conversational patterns (minimal context)
    simple_patterns = [
        r'^(hi|hey|hello|thanks|thank you|ok|okay|yes|no|sure)\b',
        r'^(what|how)\'s (up|it going)',
        r'^\w{1,20}$',  # Single word
        r'^(good|great|nice|cool)',
    ]
    
    for pattern in simple_patterns:
        if re.search(pattern, prompt_lower):
            return ("simple", "minimal", "Conversational/greeting pattern")
    
    # Check for file/documentation references
    if any(word in prompt_lower for word in ["read", "show", "file", "doc", "content"]):
        return ("simple", "standard", "File access request")
    
    # Check for memory/history references
    if any(word in prompt_lower for word in ["remember", "recall", "history", "before", "last time"]):
        return ("medium", "full", "Memory access needed")
    
    # Check for complex task indicators
    complex_indicators = ["design", "architect", "plan", "strategy", "analyze deeply", "comprehensive"]
    if any(word in prompt_lower for word in complex_indicators):
        return ("complex", "full", "Complex task requiring full context")
    
    # Default to standard for normal work requests
    return ("medium", "standard", "Standard work request")

def recommend_context_bundle(prompt, current_files=None):
    """Recommend which files to load for a given prompt.
    
    Args:
        prompt: User's message
        current_files: List of files currently loaded (optional)
    
    Returns:
        dict with recommendations
    """
    complexity, context_level, reasoning = classify_prompt(prompt)
    prompt_lower = prompt.lower()
    
    # Start with always-load files
    recommended = set(ALWAYS_LOAD)
    
    if context_level == "minimal":
        # For simple conversations, ONLY identity files
        pass
    
    elif context_level == "standard":
        # Add conditionally-loaded files based on triggers
        for file, triggers in CONDITIONAL_FILES.items():
            if any(trigger in prompt_lower for trigger in triggers):
                recommended.add(file)
        
        # Add today's memory log only
        today = datetime.now().strftime("%Y-%m-%d")
        recommended.add(f"memory/{today}.md")
    
    elif context_level == "full":
        # Add all conditional files
        recommended.update(CONDITIONAL_FILES.keys())
        
        # Add today + yesterday memory logs
        today = datetime.now()
        yesterday = today - timedelta(days=1)
        recommended.add(f"memory/{today.strftime('%Y-%m-%d')}.md")
        recommended.add(f"memory/{yesterday.strftime('%Y-%m-%d')}.md")
        
        # Add MEMORY.md for long-term context
        recommended.add("MEMORY.md")
    
    # Calculate savings
    if current_files:
        current_count = len(current_files)
        recommended_count = len(recommended)
        savings_percent = ((current_count - recommended_count) / current_count) * 100
    else:
        savings_percent = None
    
    return {
        "complexity": complexity,
        "context_level": context_level,
        "reasoning": reasoning,
        "recommended_files": sorted(list(recommended)),
        "file_count": len(recommended),
        "savings_percent": savings_percent,
        "skip_patterns": SKIP_FOR_SIMPLE if context_level == "minimal" else []
    }

def record_file_access(file_path):
    """Record that a file was accessed."""
    state = load_usage_state()
    
    # Increment access count
    state["file_access_count"][file_path] = state["file_access_count"].get(file_path, 0) + 1
    
    # Update last accessed timestamp
    state["last_accessed"][file_path] = datetime.now().isoformat()
    
    save_usage_state(state)

def get_usage_stats():
    """Get file usage statistics.
    
    Returns:
        dict with frequently/rarely accessed files
    """
    state = load_usage_state()
    
    # Sort by access count
    sorted_files = sorted(
        state["file_access_count"].items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    total_accesses = sum(state["file_access_count"].values())
    
    # Classify files
    frequent = []  # Top 20% of accesses
    occasional = []  # Middle 60%
    rare = []  # Bottom 20%
    
    if sorted_files:
        threshold_frequent = total_accesses * 0.2
        threshold_rare = total_accesses * 0.8
        
        cumulative = 0
        for file, count in sorted_files:
            cumulative += count
            
            if cumulative <= threshold_frequent:
                frequent.append({"file": file, "count": count})
            elif cumulative <= threshold_rare:
                occasional.append({"file": file, "count": count})
            else:
                rare.append({"file": file, "count": count})
    
    return {
        "total_accesses": total_accesses,
        "unique_files": len(sorted_files),
        "frequent": frequent,
        "occasional": occasional,
        "rare": rare,
        "recommendation": f"Consider loading frequently accessed files upfront, lazy-load rare files"
    }

def generate_optimized_agents_md():
    """Generate an optimized AGENTS.md with lazy loading instructions.
    
    Returns:
        str with new AGENTS.md content
    """
    quick_model = TIER_MODELS["quick"][0]
    standard_model = TIER_MODELS["standard"][0]
    deep_model = TIER_MODELS["deep"][0]
    
    # Build model override lines
    quick_override = f"`session_status model={quick_model}`"
    # Standard and Deep could have overrides if desired; we leave only Quick for now
    
    return f"""# AGENTS.md - Token-Optimized Workspace

## 🎯 Context Loading Strategy (OPTIMIZED)

**Default: Minimal context, load on-demand**

### Every Session (Always Load)
1. Read `SOUL.md` — Who you are (identity/personality)
2. Read `IDENTITY.md` — Your role/name

**Stop there.** Don't load anything else unless needed.

### Load On-Demand Only

**When user mentions memory/history:**
- Read `MEMORY.md`
- Read `memory/YYYY-MM-DD.md` (today only)

**When user asks about workflows/processes:**
- Read `AGENTS.md` (this file)

**When user asks about tools/devices:**
- Read `TOOLS.md`

**When user asks about themselves:**
- Read `USER.md`

**Never load automatically:**
- ❌ Documentation (`docs/**/*.md`) — load only when explicitly referenced
- ❌ Old memory logs (`memory/2026-01-*.md`) — load only if user mentions date
- ❌ Knowledge base (`knowledge/**/*`) — load only when user asks about specific topic
- ❌ Task files (`tasks/**/*`) — load only when user references task

### Context by Conversation Type

**Simple conversation** (hi, thanks, yes, quick question):
- Load: SOUL.md, IDENTITY.md
- Skip: Everything else
- **Token savings: ~80%**

**Standard work request** (write code, check file):
- Load: SOUL.md, IDENTITY.md, memory/TODAY.md
- Conditionally load: TOOLS.md (if mentions tools)
- Skip: docs, old memory logs
- **Token savings: ~50%**

**Complex task** (design system, analyze history):
- Load: SOUL.md, IDENTITY.md, MEMORY.md, memory/TODAY.md, memory/YESTERDAY.md
- Conditionally load: Relevant docs/knowledge
- Skip: Unrelated documentation
- **Token savings: ~30%**

## 🔥 Model Selection (ENFORCED)

**Simple conversations → QUICK ONLY**
- Greetings, acknowledgments, simple questions
- Never use Standard/Deep for casual chat
- Override: {quick_override}

**Standard work → STANDARD**
- Code writing, file edits, explanations
- Default model for most work

**Complex reasoning → DEEP**
- Architecture design, deep analysis
- Use sparingly, only when explicitly needed

## 💾 Memory (Lazy Loading)

**Daily notes:** `memory/YYYY-MM-DD.md`
- ✅ Load TODAY when user asks about recent work
- ❌ Don't load YESTERDAY unless explicitly needed
- ❌ Don't load older logs automatically

**Long-term:** `MEMORY.md`
- ✅ Load when user mentions "remember", "history", "before"
- ❌ Don't load for simple conversations

## 📊 Heartbeats (Optimized)

Use `heartbeat_optimizer.py` from token-optimizer skill:
- Check only what needs checking (not everything every time)
- Skip during quiet hours (23:00-08:00)
- Return `HEARTBEAT_OK` when nothing to report

## 🎨 Skills (Lazy Loading)

**Don't pre-read skill documentation.**

When skill triggers:
1. Read only the SKILL.md
2. Read only the specific reference files you need
3. Skip examples/assets unless explicitly needed

## 🚫 Anti-Patterns (What NOT to Do)

❌ Loading all docs at session start  
❌ Re-reading unchanged files  
❌ Using Opus for simple chat  
❌ Checking everything in every heartbeat  
❌ Loading full conversation history for simple questions  

✅ Load minimal context by default  
✅ Read files only when referenced  
✅ Use cheapest model for the task  
✅ Batch heartbeat checks intelligently  
✅ Keep context focused on current task  

## 📈 Monitoring

Track your savings:
```bash
python3 scripts/context_optimizer.py stats
python3 scripts/token_tracker.py check
```

## Integration

Run context optimizer before responding:
```bash
# Get recommendations
context_optimizer.py recommend "<user prompt>"

# Only load recommended files
# Skip everything else
```

---

**This optimized approach reduces token usage by 50-80% for typical workloads.**
"""

def main():
    """CLI interface for context optimizer."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: context_optimizer.py [recommend|record|stats|generate-agents]")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "recommend":
        if len(sys.argv) < 3:
            print("Usage: context_optimizer.py recommend '<prompt>' [current_files]")
            sys.exit(1)
        
        prompt = sys.argv[2]
        current_files = sys.argv[3:] if len(sys.argv) > 3 else None
        
        result = recommend_context_bundle(prompt, current_files)
        print(json.dumps(result, indent=2))
    
    elif command == "record":
        if len(sys.argv) < 3:
            print("Usage: context_optimizer.py record <file_path>")
            sys.exit(1)
        
        file_path = sys.argv[2]
        record_file_access(file_path)
        print(f"Recorded access: {file_path}")
    
    elif command == "stats":
        result = get_usage_stats()
        print(json.dumps(result, indent=2))
    
    elif command == "generate-agents":
        content = generate_optimized_agents_md()
        output_path = Path.home() / ".openclaw/workspace/AGENTS.md.optimized"
        output_path.write_text(content)
        print(f"Generated optimized AGENTS.md at: {output_path}")
        print("\nReview and replace your current AGENTS.md with this version.")
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
