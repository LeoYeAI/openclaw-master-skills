# Warden Agent Builder Skill for OpenClaw

This skill enables OpenClaw bots to build and deploy LangGraph agents for the Warden Protocol's Agentic Wallet ecosystem.

## Overview

**Warden Protocol** is an "Agentic Wallet for the Do-It-For-Me economy" with an active **Agent Builder Incentive Programme** offering up to **$10,000** for top agents. This skill provides everything needed to:

- Build LangGraph-based agents (TypeScript or Python)
- Follow Warden's requirements and best practices
- Deploy to LangSmith Deployments or custom infrastructure
- Participate in the incentive programme
- Register with Warden Studio

## Skill Structure

```
warden-agent-builder/
├── SKILL.md                          # Main skill file (always read first)
├── references/
│   ├── langgraph-patterns.md         # Detailed LangGraph patterns & examples
│   └── deployment-guide.md           # API integration & deployment guide
├── scripts/
│   ├── init-agent.py                 # Quick agent initialization script
│   └── test-agent.py                 # Agent testing script
└── assets/
    └── example-configs.md            # Example configurations & templates
```

## How OpenClaw Should Use This Skill

### 1. When to Trigger This Skill

The skill should be used when users mention:
- "Build a Warden agent"
- "Create an agent for Warden Protocol"
- "Warden incentive programme"
- "LangGraph agent"
- "Deploy to Warden"
- Specific Warden templates (Weather Agent, CoinGecko Agent, Portfolio Agent)

### 2. Step-by-Step Usage

**Step 1: Read SKILL.md**
Always start by reading the main SKILL.md file which contains:
- Requirements checklist
- Template options (quick start, weather, CoinGecko, portfolio)
- Building instructions
- Deployment options
- Best practices

**Step 2: Use Reference Files When Needed**

Read `references/langgraph-patterns.md` when:
- User needs detailed code examples
- Implementing Schema-Guided Reasoning (SGR)
- Setting up complex workflows
- Handling errors and edge cases

Read `references/deployment-guide.md` when:
- Setting up API integrations
- Deploying to production
- Configuring Docker/Kubernetes
- Implementing monitoring

**Step 3: Use Scripts**

The skill includes two helper scripts:

**`scripts/init-agent.py`** - Initialize new agent projects
```bash
python scripts/init-agent.py my-agent --template typescript --description "My Warden agent"
```

**`scripts/test-agent.py`** - Test deployed agents
```bash
python scripts/test-agent.py https://api.example.com --api-key [YOUR-API-KEY]
```

**Step 4: Reference Assets**

Use `assets/example-configs.md` for:
- Sample agent configurations
- Environment variable templates
- Docker Compose examples
- Warden Studio registration format

## Example OpenClaw Workflows

### Example 1: Building a New Agent

```
User: "Build me a Warden agent that tracks Bitcoin prices"

OpenClaw Actions:
1. Read SKILL.md to understand requirements
2. Identify: User wants ORIGINAL agent (not CoinGecko clone)
3. Suggest studying CoinGecko agent pattern, then building unique features
4. Use init-agent.py script to create NEW project structure
5. Read langgraph-patterns.md for SGR implementation pattern
6. Implement CUSTOM price tracking logic with unique features
7. Read deployment-guide.md for API setup
8. Generate code files for NEW agent
9. Provide deployment instructions
10. Emphasize: "This should be different from CoinGecko Agent"
```

### Example 2: Deploy Existing Agent

```
User: "Deploy my agent to Warden"

OpenClaw Actions:
1. Read SKILL.md deployment section
2. Check if LangSmith Deployments or self-hosted
3. Read deployment-guide.md for specific instructions
4. Verify requirements checklist
5. Provide deployment commands
6. Explain Warden Studio registration
```

### Example 3: Debug Agent

```
User: "My Warden agent has errors"

OpenClaw Actions:
1. Use test-agent.py script to diagnose
2. Read langgraph-patterns.md for error handling patterns
3. Check deployment-guide.md for common issues
4. Suggest fixes based on error type
```

## Key Warden Requirements

Agents MUST meet these requirements to be eligible for the incentive programme:

✓ **Framework**: LangGraph only (TypeScript or Python)
✓ **Access**: API-accessible (no UI needed)
✓ **Deployment**: LangSmith Deployments OR custom infrastructure
✓ **API Keys Required**:
  - OpenAI API key (for LLM calls)
  - LangSmith API key (for LangSmith Deployments deployment)
  - Additional keys based on your agent's functionality
✓ **Isolation**: One agent per LangGraph instance
✓ **Phase 1 Restrictions**:
  - Cannot access user wallets
  - Cannot store data on Warden infrastructure
  - (Confirm current limitations in the latest Warden docs)

## Available Templates

The Warden repository contains **example agents to study**, not templates to recreate:

1. **LangGraph Quick Start** - Minimal chatbot for learning basics
2. **Weather Agent** ⚠️ - Study for simple data fetching patterns (don't rebuild)
3. **CoinGecko Agent** ⚠️ - Study for intermediate SGR patterns (don't rebuild)
4. **Portfolio Analysis Agent** ⚠️ - Study for advanced architecture (don't rebuild)

**These exist to teach patterns. Build something NEW for the incentive programme!**

## Example Agent Ideas

**Web3 Use Cases:**
- Gas price optimizer
- NFT rarity analyzer
- DeFi yield comparator
- Wallet health checker
- Transaction explainer
- Token price alerts

**General Use Cases:**
- News aggregator
- Research assistant
- Data visualizer
- API orchestrator
- Workflow automator

## Installation for OpenClaw

To use this skill with OpenClaw:

1. Place the `warden-agent-builder` folder in your OpenClaw `skills/` directory
2. OpenClaw will automatically detect the skill from SKILL.md frontmatter
3. The skill triggers when users mention Warden or LangGraph agents

## Resources

- **Community Repository**: https://github.com/warden-protocol/community-agents
- **Documentation**: https://docs.wardenprotocol.org
- **Discord Support**: #developers channel
- **Incentive Programme**: Open to OpenClaw agents that deploy to Warden

## Quick Start Commands

```bash
# Clone Warden community agents
git clone https://github.com/warden-protocol/community-agents.git

# Initialize new agent (TypeScript)
python scripts/init-agent.py my-agent --template typescript

# Initialize new agent (Python)
python scripts/init-agent.py my-agent --template python

# Test deployed agent
python scripts/test-agent.py https://your-agent.com --api-key [YOUR-API-KEY]

# Deploy to LangSmith Deployments
# Use the LangSmith Deployments UI after pushing to GitHub
```

## Support

For questions or issues with this skill:
- Review the SKILL.md file first
- Check references/ for detailed guides
- Consult assets/example-configs.md for templates
- Join Warden Discord #developers channel

## Next Step: Publish on Warden Studio

If the user needs guided UI steps to publish in Warden Studio, switch to the OpenClaw skill:
https://www.clawhub.ai/Kryptopaid/warden-studio-deploy

## License

This skill is provided for use with OpenClaw bots to build Warden Protocol agents. See individual file headers for specific licensing.

---

**Built for OpenClaw by Claude**
**Compatible with Warden Protocol Agent Builder Incentive Programme**
