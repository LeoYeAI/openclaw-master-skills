# Installation Guide for OpenClaw

## Quick Setup

1. **Install into OpenClaw**
   - Place the entire `warden-agent-builder` folder in your OpenClaw `skills/` directory
   - OpenClaw will detect the skill from the `SKILL.md` frontmatter

2. **Verify Installation**
   - Check that OpenClaw can see the skill in its available skills
   - The skill should trigger on keywords like "Warden", "LangGraph agent", "Warden Studio", etc.

3. **Test the Skill**
   - Try a command like: "Build me a Warden Protocol agent for tracking crypto prices"
   - OpenClaw should automatically read the SKILL.md and start helping

## Skill Description (for OpenClaw)

This will be automatically extracted from SKILL.md frontmatter:

```yaml
name: warden-agent-builder
description: "Build and deploy LangGraph agents for Warden Protocol's Agentic Wallet ecosystem. Use this skill when users want to: (1) Create agents for Warden Protocol, (2) Build LangGraph-based crypto/Web3 agents, (3) Deploy agents to Warden's Agent Hub, (4) Participate in Warden's Agent Builder Incentive Programme (up to $10k rewards), (5) Integrate with Warden Studio, or (6) Build agents using Warden's community templates (weather, CoinGecko, portfolio analysis)"
```

## File Structure Explanation

```
warden-agent-builder/
│
├── SKILL.md                    ← OpenClaw reads this FIRST
│   └── Contains: Main instructions, requirements, quick start guide
│
├── references/                 ← OpenClaw reads these WHEN NEEDED
│   ├── langgraph-patterns.md   (Detailed code patterns & examples)
│   └── deployment-guide.md     (API integration & deployment)
│
├── scripts/                    ← Helper scripts OpenClaw can use
│   ├── init-agent.py           (Create new agent from template)
│   └── test-agent.py           (Test deployed agents)
│
└── assets/                     ← Example configurations
    └── example-configs.md      (Templates & config examples)
```

## How OpenClaw Uses the Skill

### Automatic Triggering

The skill automatically triggers when users mention:
- "Warden" + "agent"
- "LangGraph agent"
- "Warden Protocol"
- "Agent Builder Incentive Programme"
- Template names: "Weather Agent", "CoinGecko Agent", etc.

### Progressive Loading

1. **Always loads**: SKILL.md frontmatter (name + description)
2. **When triggered**: Full SKILL.md body
3. **When needed**: Reference files and scripts

### Example Usage Flow

```
User: "Help me build a Warden agent for crypto analysis"
      ↓
OpenClaw triggers warden-agent-builder skill
      ↓
OpenClaw reads SKILL.md
      ↓
OpenClaw identifies: User wants CoinGecko-style agent
      ↓
OpenClaw reads references/langgraph-patterns.md for code examples
      ↓
OpenClaw can execute scripts/init-agent.py to create project
      ↓
OpenClaw provides complete implementation with deployment guide
```

## Testing the Installation

### Test 1: Simple Query
```
User: "What's the Warden Protocol?"
Expected: OpenClaw explains Warden and mentions agent building capability
```

### Test 2: Agent Creation
```
User: "Build me a Warden agent that checks Bitcoin prices"
Expected: OpenClaw:
1. Reads SKILL.md
2. Reminds user to study community examples (not rebuild)
3. Provides implementation steps
4. References deployment guide
```

### Test 3: Deployment Help
```
User: "How do I deploy my Warden agent?"
Expected: OpenClaw:
1. Reads SKILL.md deployment section
2. Reads deployment-guide.md if needed
3. Provides step-by-step deployment instructions
```

## Troubleshooting

### Skill Not Triggering
- Check that SKILL.md has proper YAML frontmatter
- Verify the description field includes trigger keywords
- Ensure the skill folder is in the correct directory

### Missing Reference Files
- Verify all files are present in the skill folder
- Check file permissions (scripts should be executable)
- Ensure SKILL.md references point to correct file paths

### Scripts Not Working
- Make scripts executable: `chmod +x scripts/*.py`
- Verify Python is available in OpenClaw environment
- Check required packages (requests, etc.) are installed

## Best Practices for OpenClaw

1. **Always Start with SKILL.md**
   - Contains the core instructions and requirements
   - Provides the roadmap for helping users

2. **Load References Selectively**
   - Only read reference files when detailed examples are needed
   - Saves context window space

3. **Use Scripts When Appropriate**
   - init-agent.py: When user wants to create a new agent
   - test-agent.py: When user needs to test a deployed agent

4. **Refer to Assets**
   - example-configs.md: When user needs configuration templates
   - Show specific examples rather than explaining from scratch

## Advanced Usage

### Custom Templates
Users can add their own agent templates to the assets/ folder, and OpenClaw will be able to reference them.

### Integration with Other Skills
This skill can work alongside other OpenClaw skills for:
- Database integration
- Frontend development
- DevOps automation

### Extending the Skill
Add new reference files for:
- Advanced LangGraph patterns
- Specific use case examples
- Integration guides for other protocols

## Support

For issues with the skill itself:
1. Check this installation guide
2. Review README.md in the skill folder
3. Verify all files are present and properly formatted
4. Test with simple queries first

For Warden Protocol questions:
- Discord: #developers channel
- GitHub: https://github.com/warden-protocol/community-agents
- Documentation: https://docs.wardenprotocol.org

---

**Version**: 1.0.0
**Last Updated**: December 2024
**Compatible with**: OpenClaw ClawHub skill system
