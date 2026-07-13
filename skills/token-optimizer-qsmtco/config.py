# Token Optimizer Configuration
# Central source of truth for tier model assignments.
# Edit this file to change which models are used for each tier.

# Model IDs as they appear in OpenClaw configuration (e.g., openclaw.json)
TIER_MODELS = {
    "quick": ["openrouter/stepfun/step-3.5-flash:free"],
    "standard": ["openrouter/stepfun/step-3.5-flash:free"],
    "deep": ["openrouter/minimax/minimax-m2.5"]
}

# Helper: flatten to set of all models
ALL_MODELS = set()
for models in TIER_MODELS.values():
    ALL_MODELS.update(models)

def get_model(tier):
    """Return the first model assigned to the given tier."""
    return TIER_MODELS[tier][0]

def validate():
    """Validate configuration.
    Raises ValueError if something is misconfigured.
    """
    required_tiers = ["quick", "standard", "deep"]
    for tier in required_tiers:
        if tier not in TIER_MODELS:
            raise ValueError(f"Missing tier '{tier}' in TIER_MODELS")
        models = TIER_MODELS[tier]
        if not isinstance(models, list) or len(models) == 0:
            raise ValueError(f"Tier '{tier}' must have at least one model")
        for m in models:
            if not isinstance(m, str) or not m.strip():
                raise ValueError(f"Invalid model ID in tier '{tier}': {m!r}")
    return True

# Run validation on import
validate()
