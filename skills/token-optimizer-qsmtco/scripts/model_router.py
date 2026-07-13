#!/usr/bin/env python3
"""
Smart model router - routes tasks to appropriate models based on complexity.
Helps reduce token costs by using cheaper models for simpler tasks.
"""
import re
import sys
from pathlib import Path

# Ensure we can import config from the skill root (parent of scripts/)
sys.path.append(str(Path(__file__).parent.parent))
from config import TIER_MODELS

# Communication patterns that should ALWAYS use Quick tier (never Standard/Deep)
COMMUNICATION_PATTERNS = [
    r'^(hi|hey|hello|yo|sup)\b',
    r'^(thanks|thank you|thx)\b',
    r'^(ok|okay|sure|got it|understood)\b',
    r'^(yes|yeah|yep|yup|no|nope)\b',
    r'^(good|great|nice|cool|awesome)\b',
    r"^(what|how)'s (up|it going)",
    r'^\w{1,15}$',  # Single short word
    r'^(lol|haha|lmao)\b',
]

# Background/routine tasks that should ALWAYS use Quick tier
BACKGROUND_TASK_PATTERNS = [
    # Heartbeat checks
    r'heartbeat',
    r'check\s+(email|calendar|weather|monitoring)',
    r'monitor\s+',
    r'poll\s+',
    
    # Cronjob/scheduled tasks
    r'cron',
    r'scheduled\s+task',
    r'periodic\s+check',
    r'reminder',
    
    # Document parsing/extraction
    r'parse\s+(document|file|log|csv|json|xml)',
    r'extract\s+(text|data|content)\s+from',
    r'read\s+(log|logs)',
    r'scan\s+(file|document)',
    r'process\s+(csv|json|xml|yaml)',
]

# Model routing rules (patterns and keywords remain constant; model pulled from config)
ROUTING_RULES = {
    "quick": {
        "patterns": [
            r"read\s+file",
            r"list\s+files",
            r"show\s+(me\s+)?the\s+contents?",
            r"what's\s+in",
            r"cat\s+",
            r"get\s+status",
            r"check\s+(if|whether)",
            r"is\s+\w+\s+(running|active|enabled)"
        ],
        "keywords": ["read", "list", "show", "status", "check", "get"],
        "model": TIER_MODELS["quick"][0],
        "cost_multiplier": 0.083  # vs standard
    },
    "standard": {
        "patterns": [
            r"write\s+\w+",
            r"create\s+\w+",
            r"edit\s+\w+",
            r"fix\s+\w+",
            r"debug\s+\w+",
            r"explain\s+\w+",
            r"how\s+(do|can)\s+i"
        ],
        "keywords": ["write", "create", "edit", "update", "fix", "debug", "explain"],
        "model": TIER_MODELS["standard"][0],
        "cost_multiplier": 0.083
    },
    "deep": {
        "patterns": [
            r"complex\s+\w+",
            r"design\s+\w+",
            r"architect\w+",
            r"analyze\s+deeply",
            r"comprehensive\s+\w+"
        ],
        "keywords": ["design", "architect", "complex", "comprehensive", "deep"],
        "model": TIER_MODELS["deep"][0],
        "cost_multiplier": 1.0
    }
}

def classify_task(prompt):
    """Classify task complexity based on prompt text.
    
    Args:
        prompt: User's message/request
    
    Returns:
        tuple of (tier, confidence, reasoning)
    """
    prompt_lower = prompt.lower()
    
    # FIRST: Check if this is simple communication (ALWAYS Quick)
    for pattern in COMMUNICATION_PATTERNS:
        if re.search(pattern, prompt_lower):
            return ("quick", 1.0, f"Simple communication - NEVER use Standard/Deep for chat")
    
    # SECOND: Check if this is a background/routine task (ALWAYS Quick)
    for pattern in BACKGROUND_TASK_PATTERNS:
        if re.search(pattern, prompt_lower):
            return ("quick", 1.0, f"Background task (heartbeat/cron/parsing) - ALWAYS use Quick")
    
    # Score each tier
    scores = {}
    for tier, rules in ROUTING_RULES.items():
        score = 0
        matches = []
        
        # Pattern matching
        for pattern in rules["patterns"]:
            if re.search(pattern, prompt_lower):
                score += 2
                matches.append(f"pattern:{pattern}")
        
        # Keyword matching
        for keyword in rules["keywords"]:
            if keyword in prompt_lower:
                score += 1
                matches.append(f"keyword:{keyword}")
        
        scores[tier] = {
            "score": score,
            "matches": matches
        }
    
    # Determine best tier
    best_tier = max(scores.items(), key=lambda x: x[1]["score"])
    
    if best_tier[1]["score"] == 0:
        # Default to standard if unclear
        return ("standard", 0.5, "No clear indicators, defaulting to balanced model")
    
    confidence = min(best_tier[1]["score"] / 5.0, 1.0)  # Cap at 1.0
    reasoning = f"Matched: {', '.join(best_tier[1]['matches'][:3])}"
    
    return (best_tier[0], confidence, reasoning)

def route_task(prompt, current_model=None, force_tier=None):
    """Route a task to appropriate model.
    
    Args:
        prompt: User's message/request
        current_model: Current model being used (defaults to standard tier model from config)
        force_tier: Override classification (quick/standard/deep)
    
    Returns:
        dict with routing decision
    """
    if current_model is None:
        current_model = TIER_MODELS["standard"][0]
    if force_tier:
        tier = force_tier
        confidence = 1.0
        reasoning = "User-specified tier"
    else:
        tier, confidence, reasoning = classify_task(prompt)
    
    recommended_model = ROUTING_RULES[tier]["model"]
    cost_savings = 1.0 - ROUTING_RULES[tier]["cost_multiplier"]
    
    return {
        "current_model": current_model,
        "recommended_model": recommended_model,
        "tier": tier,
        "confidence": confidence,
        "reasoning": reasoning,
        "cost_savings_percent": cost_savings * 100,
        "should_switch": recommended_model != current_model
    }

def main():
    """CLI interface for model router."""
    import sys
    import json
    
    if len(sys.argv) < 2:
        print("Usage: model_router.py '<prompt>' [current_model] [force_tier]")
        print("Example: model_router.py 'read the config file'")
        print("Tiers: quick (routine), standard (balanced), deep (complex)")
        sys.exit(1)
    
    prompt = sys.argv[1]
    current_model = sys.argv[2] if len(sys.argv) > 2 else "anthropic/claude-sonnet-4-5"
    force_tier = sys.argv[3] if len(sys.argv) > 3 else None
    
    result = route_task(prompt, current_model, force_tier)
    print(json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
