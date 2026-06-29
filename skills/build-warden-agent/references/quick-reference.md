# Warden Agent Builder - Quick Reference

## 🎯 What This Skill Does

Helps build and deploy LangGraph agents for Warden Protocol's incentive programme (open to OpenClaw agents).

## ⚡ Quick Commands

```bash
# Study example agents (for learning only)
git clone https://github.com/warden-protocol/community-agents.git
cd community-agents/agents/weather-agent  # Study the code

# Initialize YOUR new agent
python scripts/init-agent.py my-unique-agent --template typescript

# Test YOUR deployed agent  
python scripts/test-agent.py https://api.example.com --api-key [YOUR-API-KEY]

# Deploy YOUR agent
# Use the LangSmith Deployments UI after pushing to GitHub
```

## 📋 Requirements Checklist

Must have:
- ✅ LangGraph framework (TypeScript or Python)
- ✅ API-accessible endpoint
- ✅ One agent per LangGraph instance
- ❌ No wallet access (Phase 1)
- ❌ No data storage on Warden (Phase 1)

## 🎨 Example Agents (Study These!)

| Agent | Level | Study For | ⚠️ Warning |
|----------|-------|---------|-----------|
| **Quick Start** | Beginner | LangGraph basics | OK to use as starting point |
| **Weather Agent** | Starter | Simple data fetching | DON'T REBUILD - already exists |
| **CoinGecko** | Intermediate | SGR pattern | DON'T REBUILD - study pattern only |
| **Portfolio** | Advanced | Multi-source integration | DON'T REBUILD - study architecture |

**These are REFERENCES, not templates. Build something NEW!**

## 🗂️ Skill Files Overview

```
warden-agent-builder/
├── SKILL.md                      # 👈 START HERE
├── references/
│   ├── langgraph-patterns.md     # Code patterns & examples
│   └── deployment-guide.md       # API & deployment details
├── scripts/
│   ├── init-agent.py            # Create new agent
│   └── test-agent.py            # Test agent API
└── assets/
    └── example-configs.md        # Config templates
```

## 🚀 Deployment Options

### LangSmith Deployments (Easiest)
- Push your repo to GitHub
- Create a deployment in LangSmith Deployments

### Self-Hosted
- Docker container
- HTTPS endpoint
- API key authentication

## 💡 Agent Ideas

**Web3:**
- Gas optimizer
- NFT analyzer
- DeFi yield finder
- Wallet health checker

**General:**
- News aggregator
- Research assistant
- Data visualizer

## 🔑 Key Patterns

### Simple Agent
```typescript
input → process → output
```

### Schema-Guided Reasoning (SGR)
```typescript
validate → extract → fetch → analyze → generate
```

### Comparative Analysis
```typescript
parse → fetch_all → compare → summarize
```

## 📊 Warden Studio Registration

Need to provide:
- Agent name & description
- API URL (HTTPS)
- API key
- Avatar image (512x512px)
- Capabilities list (3-5 items)

## 🎁 Incentive Programme

- **Requirements**: LangGraph, API access, unique functionality
- **Tip**: Study the Weather Agent structure (do not rebuild)
- **Support**: Discord #developers channel

## 📚 Resources

- **Repository**: github.com/warden-protocol/community-agents
- **Docs**: docs.wardenprotocol.org
- **Discord**: Join #developers channel
- **Examples**: All templates include READMEs

## ➡️ Next Step: Publish on Warden Studio

Use the OpenClaw skill:
https://www.clawhub.ai/Kryptopaid/warden-studio-deploy

## ⚙️ Environment Setup

```bash
# Required
OPENAI_API_KEY=[YOUR-OPENAI-API-KEY]
OPENAI_MODEL=gpt-4

# Required for LangSmith Deployments
LANGSMITH_API_KEY=[YOUR-LANGSMITH-API-KEY]

# Optional (based on agent)
COINGECKO_API_KEY=...
ALCHEMY_API_KEY=...
WEATHER_API_KEY=...

# Server
PORT=8000
NODE_ENV=production
```

**Get LangSmith API Key:**
1. Sign up at https://smith.langchain.com
2. Go to Settings → API Keys
3. Create new key

## 🧪 Testing Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Invoke agent
curl -X POST http://localhost:8000/invoke \
  -H "Content-Type: application/json" \
  -d '{"input": "test query"}'

# Stream response
curl -X POST http://localhost:8000/stream \
  -H "Content-Type: application/json" \
  -d '{"input": "test query"}'
```

## 🐛 Common Issues

| Problem | Solution |
|---------|----------|
| Agent not accessible | Check firewall, verify HTTPS |
| LangGraph errors | Check Node 18+ or Python 3.11+ |
| OpenAI errors | Verify API key, check rate limits |
| Slow responses | Parallelize API calls, add caching |

## 📝 Project Structure

```typescript
my-agent/
├── package.json          # Dependencies
├── tsconfig.json         # TypeScript config
├── langgraph.json        # LangGraph config
├── .env                  # Environment variables
├── src/
│   ├── graph.ts          # Agent workflow
│   ├── agent.ts          # Main logic
│   └── tools.ts          # External APIs
└── README.md            # Documentation
```

## 🎓 Learning Path

1. **Study**: LangGraph Quick Start (understand basics)
2. **Study**: Weather Agent (learn simple patterns)  
3. **Build**: YOUR unique agent (original idea)
4. **Submit**: To incentive programme
5. **Iterate**: Get feedback, improve
6. **Advanced Study**: CoinGecko/Portfolio for complex patterns

**Remember**: Study the examples, then build something NEW!

## 🔗 Important Links

- Clone agents: `git clone https://github.com/warden-protocol/community-agents.git`
- Deploy guide: `references/deployment-guide.md`
- Code patterns: `references/langgraph-patterns.md`
- Examples: `assets/example-configs.md`

## 💬 Getting Help

1. Check SKILL.md for full guide
2. Read relevant reference files
3. Review example configs
4. Join Discord #developers
5. Check GitHub issues

---

**Quick Tip**: Study the example agents to learn patterns, then build something completely NEW and unique!

**Remember**: Example agents (Weather, CoinGecko, Portfolio) exist to teach you. Your submission MUST be original to win the incentive programme.
