# OpenClaw Token Optimizer

**Reduce OpenClaw API costs by 50-80% through intelligent context loading and model selection.**

## What This Does

This skill helps you reduce token usage (and thus API costs) by:
- Loading only the context files you actually need (not everything)
- Using cheaper models for simple tasks
- Optimizing heartbeat check intervals
- Tracking usage against budgets

## Safety & Security

**This skill is 100% safe:**
- ✅ No unsolicited network requests
- ✅ Network only for optional pricing refresh (user-initiated, requires OPENROUTER_API_KEY)
- ✅ No code execution (no eval/exec)
- ✅ Only reads/writes local JSON files for state tracking
- ✅ Uses only Python standard library
- ✅ All code is auditable

See [SECURITY.md](SECURITY.md) for detailed security analysis.

**Note**: Some antivirus tools may flag this as "suspicious" due to the word "optimizer" + file operations. This is a false positive. Review the code yourself or check the security documentation.

## Quick Start

```bash
# Install
clawhub install openclaw-token-optimizer

# Generate optimized context loading strategy
python3 scripts/context_optimizer.py generate-agents
# Review output: AGENTS.md.optimized

# Check what context you need for a prompt
python3 scripts/context_optimizer.py recommend "hi, how are you?"
# Output: Only load SOUL.md + IDENTITY.md (saves 80% tokens!)

# Check token budget status
python3 scripts/token_tracker.py check
```

## Documentation

- [SKILL.md](SKILL.md) - Full documentation
- [SECURITY.md](SECURITY.md) - Security analysis
- `.clawhubsafe` - File checksums

## License

Apache 2.0

## Author

Asif2BD - https://clawhub.ai/Asif2BD
