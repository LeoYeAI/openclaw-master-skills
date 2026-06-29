---
name: warden-agent-builder
description: "Build original LangGraph agents for Warden Protocol and prepare them for publishing in Warden Studio. Use this skill when users want to: (1) Create new Warden agents (not community examples), (2) Build LangGraph-based crypto/Web3 agents, (3) Deploy agents via LangSmith Deployments or custom infra, (4) Participate in the Warden Agent Builder Incentive Programme (open to OpenClaw agents), or (5) Integrate with Warden Studio for Agent Hub publishing."
---

# Warden Agent Builder

Build and deploy LangGraph agents for Warden Protocol's Agentic Wallet ecosystem.

## ⚠️ IMPORTANT: About Example Agents

The Warden community repository contains **example agents for learning**, not templates to recreate:

- **Weather Agent** - Study this to learn simple data fetching patterns
- **CoinGecko Agent** - Study this to learn Schema-Guided Reasoning (SGR)
- **Portfolio Agent** - Study this to learn complex multi-source integration

**DO NOT BUILD THESE AGENTS** - they already exist. Instead:
1. **Study** their code to understand patterns
2. **Learn** from their architecture and workflows  
3. **Build** something NEW and original for the incentive programme

Your agent must be **unique and solve a different problem** to be eligible for the incentive programme.

## Overview

Warden Protocol is an "Agentic Wallet for the Do-It-For-Me economy" with an active Agent Builder Incentive Programme open to OpenClaw agents that deploy to Warden. All agents must be LangGraph-based and API-accessible.

**Key Resources:**
- Community Agents Repository: https://github.com/warden-protocol/community-agents
- Documentation: https://docs.wardenprotocol.org
- Discord: #developers channel for support

## Requirements Checklist

Before building, ensure your agent meets these mandatory requirements:

✓ **Framework**: Built with LangGraph (TypeScript or Python)
✓ **Deployment**: LangSmith Deployments OR custom infrastructure
✓ **Access**: API-accessible (no UI required - Warden provides UI)
✓ **Isolation**: One agent per LangGraph instance
✓ **Security Limitations** (Phase 1):
  - Cannot access user wallets
  - Cannot store data on Warden infrastructure

✓ **Functionality**: Can implement any workflow:
  - Web3/Web2 automation
  - API integrations
  - Database connections
  - External tool interactions

## Understanding the Example Agents

The community-agents repository contains **reference examples** to learn from, NOT templates to recreate:

### Example Agent 1: LangGraph Quick Start (Study for Basics)
**Location**: `agents/langgraph-quick-start` (TypeScript) or `agents/langgraph-quick-start-py` (Python)
**Learn**: LangGraph fundamentals, minimal agent structure
**Study**: Single-node chatbot with OpenAI integration

```bash
git clone https://github.com/warden-protocol/community-agents.git
cd community-agents/agents/langgraph-quick-start
```

### Example Agent 2: Weather Agent (Study for Structure)
**Location**: `agents/weather-agent`
**Learn**: Simple data fetching, API integration, user-friendly responses
**Study**: 
- How to fetch data from external APIs (WeatherAPI)
- Processing and formatting results
- Clear scope and structure
**⚠️ DO NOT BUILD**: This already exists. Study it, then build something NEW.

### Example Agent 3: CoinGecko Agent (Study for SGR Pattern)
**Location**: `agents/coingecko-agent`
**Learn**: Schema-Guided Reasoning, complex workflows
**Study**:
- 5-step SGR workflow: Validate → Extract → Fetch → Validate → Analyze
- Comparative analysis patterns
- Error handling and data validation
**⚠️ DO NOT BUILD**: This already exists. Study the pattern, apply to new use cases.

### Example Agent 4: Portfolio Analysis Agent (Study for Advanced Patterns)
**Location**: `agents/portfolio-agent`
**Learn**: Multi-source data synthesis, production architecture
**Study**:
- Integrating multiple APIs (CoinGecko + Alchemy)
- Multi-chain support (EVM and Solana)
- Complex SGR workflows
- Comprehensive reporting
**⚠️ DO NOT BUILD**: This already exists. Study the architecture for your own complex agent.

## IMPORTANT: Build Something NEW

These examples exist to teach patterns and best practices. For the incentive programme, you MUST create an **original, unique agent** that solves a different problem. Do NOT simply recreate the Weather Agent, CoinGecko Agent, or Portfolio Agent.

## Building Your Original Agent

### Step 1: Study Examples and Choose Your Approach

**DO NOT clone an example to modify it.** Instead:

1. **Study the examples** to understand patterns:
   - Simple data fetching → Study Weather Agent
   - Complex analysis → Study CoinGecko Agent  
   - Multi-source synthesis → Study Portfolio Agent

2. **Identify YOUR unique use case**:
   - What problem will your agent solve?
   - What APIs or data sources will it use?
   - What makes it different from existing agents?

3. **Plan your agent's workflow**:
   - Simple request-response?
   - Schema-Guided Reasoning (SGR)?
   - Multi-step analysis?

### Step 2: Initialize Your NEW Agent

Use the initialization script to create a fresh project:

```bash
# Create your unique agent
python scripts/init-agent.py my-unique-agent \
  --template typescript \
  --description "Description of what YOUR agent does"

# Navigate to project
cd my-unique-agent

# Install dependencies
npm install  # TypeScript
# OR
pip install -r requirements.txt  # Python
```

This creates a clean starting point, not a copy of existing agents.

### Step 3: Understand LangGraph Agent Structure

Every LangGraph agent follows this basic structure:

```
your-agent/
├── src/
│   ├── agent.ts/py          # Main agent logic (YOUR CODE)
│   ├── graph.ts/py          # LangGraph workflow definition (YOUR CODE)
│   └── tools.ts/py          # Tool implementations (YOUR CODE)
├── package.json / requirements.txt
├── langgraph.json           # LangGraph configuration
└── README.md
```

**Key files to implement:**
- `graph.ts/py` - Define your workflow (validate → process → respond)
- `agent.ts/py` - Implement your core logic
- `tools.ts/py` - Integrate external APIs specific to YOUR agent's purpose

### Step 4: Implement Your Custom Agent Logic

**Study patterns from examples, apply to YOUR use case:**

**If building a simple data fetcher** (like Weather Agent pattern):
```typescript
// Define workflow
const workflow = new StateGraph({
  channels: agentState
})
  .addNode("fetch", fetchYourData)      // YOUR API
  .addNode("process", processYourData)  // YOUR logic
  .addNode("respond", generateResponse);

workflow
  .addEdge(START, "fetch")
  .addEdge("fetch", "process")
  .addEdge("process", "respond")
  .addEdge("respond", END);
```

**If building complex analysis** (like CoinGecko Agent pattern - SGR):
```typescript
// Define 5-step SGR workflow
const workflow = new StateGraph({
  channels: agentState
})
  .addNode("validate", validateYourInput)     // YOUR validation
  .addNode("extract", extractYourParams)      // YOUR extraction
  .addNode("fetch", fetchYourData)            // YOUR APIs
  .addNode("analyze", analyzeYourData)        // YOUR analysis
  .addNode("generate", generateYourResponse); // YOUR formatting

workflow
  .addEdge(START, "validate")
  .addEdge("validate", "extract")
  .addEdge("extract", "fetch")
  .addEdge("fetch", "analyze")
  .addEdge("analyze", "generate")
  .addEdge("generate", END);
```

**Key Principles:**
1. Keep workflows linear and predictable
2. Validate inputs at each stage
3. Handle errors gracefully
4. Use OpenAI for natural language generation
5. Structure responses consistently

**CRITICAL**: This should be YOUR implementation solving YOUR problem, not a copy of the example agents.

### Step 5: Configure Environment

Create `.env` file:

```bash
# Required
OPENAI_API_KEY=your_openai_key

# Required for LangSmith Deployments (cloud)
LANGSMITH_API_KEY=your_langsmith_key

# Optional - based on your tools
WEATHER_API_KEY=your_weather_key
COINGECKO_API_KEY=your_coingecko_key
ALCHEMY_API_KEY=your_alchemy_key
```

**Getting LangSmith API Key:**
1. Create account at https://smith.langchain.com
2. Navigate to Settings → API Keys
3. Create new API key
4. Add to `.env` file

Update `langgraph.json`:

```json
{
  "agent_id": "[YOUR-AGENT-NAME]",
  "python_version": "3.11",  // or omit for TypeScript
  "dependencies": ["."],
  "graphs": {
    "agent": "./src/graph.ts"  // or .py
  },
  "env": ".env"
}
```

### Step 6: Test Locally

```bash
# TypeScript
npm run dev

# Python
langgraph dev
```

Test your agent's API:

```bash
curl -X POST http://localhost:8000/invoke \
  -H "Content-Type: application/json" \
  -d '{"input": "test query"}'
```

## Deployment Options

### Option 1: LangSmith Deployments (Recommended)

**Pros**: Fastest, simplest, managed infrastructure
**Requirements**: LangSmith API key

**Steps**:

```bash
1. Push your agent repository to GitHub.
2. Create a new deployment in LangSmith Deployments.
3. Connect the repo, set environment variables, and deploy.
```

Your agent receives:
- API endpoint URL
- Automatic authentication (uses your LangSmith API key)
- Automatic scaling and monitoring

**Authentication for API calls:**
When calling your deployed agent, include your LangSmith API key:

```bash
curl AGENT_URL/runs/wait \
  --request POST \
  --header 'Content-Type: application/json' \
  --header 'x-api-key: [YOUR-LANGSMITH-API-KEY]' \
  --data '{
    "assistant_id": "[YOUR-AGENT-ID]",
    "input": {
      "messages": [{"role": "user", "content": "test query"}]
    }
  }'
```

### Option 2: Self-Hosted Infrastructure

**Pros**: Full control over runtime
**Requirements**:
- Docker container hosting
- Exposed API endpoint
- SSL certificate (HTTPS)
- Monitoring and logging

**Basic Docker Setup**:

```dockerfile
FROM node:18
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
EXPOSE 8000
CMD ["npm", "start"]
```

Deploy and note your:
- API URL: `https://your-domain.com/agent`
- API Key: Generated for authentication

## Register with Warden Studio

Once your agent is deployed and reachable via HTTPS, register it in Warden Studio:

1. **Provide API Details**:
   - API URL
   - API key

2. **Add Metadata**:
   - Agent name
   - Description
   - Skills/capabilities list
   - Avatar image

3. **Publish**: Agent appears in Warden's Agent Hub for millions of users

No additional setup required - your API-accessible agent is ready!

**Next step (separate skill):**
If the user asks to publish in Warden Studio or needs guided UI steps, switch to the OpenClaw skill **"Deploy Agent on Warden Studio"**:
https://www.clawhub.ai/Kryptopaid/warden-studio-deploy

## Best Practices

### 1. Agent Design
- Study the Weather Agent structure to learn patterns
- Use Schema-Guided Reasoning for complex workflows
- Keep responses concise and actionable
- Handle API failures gracefully
- Validate all inputs

### 2. API Integration
- Use environment variables for API keys
- Implement rate limiting
- Cache responses when appropriate
- Log errors for debugging
- Return structured JSON responses

### 3. Testing
- Test locally before deploying
- Verify all API endpoints work
- Test edge cases and errors
- Ensure responses are user-friendly
- Validate against Warden requirements

### 4. Documentation
- Write clear README with:
  - Agent purpose and capabilities
  - Required API keys
  - Setup instructions
  - Example queries
  - Known limitations

## Common Patterns

### Pattern 1: Simple Data Fetcher
```typescript
// Fetch → Format → Respond
async function agent(input: string) {
  const data = await fetchAPI(input);
  const formatted = formatData(data);
  return generateResponse(formatted);
}
```

### Pattern 2: Multi-Step Analysis
```typescript
// Validate → Extract → Fetch → Analyze → Generate
async function agent(input: string) {
  const validated = await validateInput(input);
  const params = await extractParams(validated);
  const data = await fetchData(params);
  const analysis = await analyzeData(data);
  return generateReport(analysis);
}
```

### Pattern 3: Comparative Analysis
```typescript
// Parse → Fetch Multiple → Compare → Summarize
async function agent(input: string) {
  const items = await parseItems(input);
  const dataArray = await Promise.all(
    items.map(item => fetchData(item))
  );
  const comparison = compareData(dataArray);
  return generateComparison(comparison);
}
```

## Troubleshooting

### Common Issues

**"Agent not accessible via API"**
- Verify deployment completed successfully
- Check firewall/security group settings
- Ensure API endpoint is publicly accessible
- Test with curl or Postman

**"LangGraph errors during build"**
- Verify Node.js version (18+) or Python (3.11+)
- Check all dependencies installed
- Validate langgraph.json syntax
- Review error logs in deployment console

**"OpenAI API errors"**
- Verify API key is valid
- Check rate limits not exceeded
- Ensure sufficient credits
- Review error messages for details

**"Agent responses are slow"**
- Optimize API calls (parallelize where possible)
- Implement caching for repeated queries
- Reduce LLM token usage
- Consider upgrading infrastructure

## Incentive Programme Tips

The incentive programme is open to OpenClaw agents that deploy to Warden.

1. **Be Original**: Create something NEW that doesn't exist yet
   - Don't recreate Weather Agent, CoinGecko Agent, or Portfolio Agent
   - Study their patterns, apply to different problems
   
2. **Solve Real Problems**: Focus on useful, unique functionality
   - What gap exists in the Warden ecosystem?
   - What would users actually want?

3. **Start Simple**: Better to do one thing exceptionally well
   - Don't try to build everything at once
   - Simple, focused agents often win

4. **Quality Over Features**: Reliability beats complexity
   - Test thoroughly
   - Handle errors gracefully
   - Provide clear, helpful responses

5. **Study the Examples**: Learn patterns, don't copy implementations
   - Weather Agent → Simple data fetching pattern
   - CoinGecko Agent → SGR workflow pattern
   - Portfolio Agent → Multi-source integration pattern

6. **Document Well**: Clear README with examples and setup instructions

7. **Join Discord**: Get feedback in #developers channel before submitting

## Example Agent Ideas (Build These!)

These are **NEW agent ideas** that don't exist yet in the Warden ecosystem. Build one of these (or create your own unique idea):

**Web3 Use Cases:**
- Gas price optimizer (predict best times to transact)
- NFT rarity analyzer (evaluate NFT traits and rarity scores)
- DeFi yield comparator (compare yields across protocols)
- Wallet health checker (analyze wallet security and diversification)
- Transaction explainer (decode and explain complex transactions)
- Token price alerts (customizable price movement notifications)
- Smart contract auditor (basic security checks)
- Liquidity pool finder (identify best liquidity opportunities)
- Bridge fee comparator (find cheapest cross-chain bridges)
- Airdrop tracker (find and track airdrop eligibility)

**General Use Cases:**
- Crypto news aggregator (filter and summarize crypto news)
- Research assistant (gather and analyze crypto research)
- Regulatory tracker (track crypto regulations by region)
- Data visualizer (create charts from on-chain data)
- API orchestrator (combine multiple crypto data sources)
- Workflow automator (automate common crypto tasks)

**Remember**: These are IDEAS for new agents. Study the example agents (Weather, CoinGecko, Portfolio) to learn patterns, then build something from this list or create your own unique concept.

## Additional Resources

**Documentation:**
- LangGraph TypeScript Guide: `community-agents/docs/langgraph-quick-start-ts.md`
- LangGraph Python Guide: `community-agents/docs/langgraph-quick-start-py.md`
- Deployment Guide: `community-agents/docs/deploy.md`

**Example Agents:**
- Weather Agent README: `agents/weather-agent/README.md`
- CoinGecko Agent README: `agents/coingecko-agent/README.md`
- Portfolio Agent README: `agents/portfolio-agent/README.md`

**Support:**
- Discord: #developers channel
- GitHub Issues: https://github.com/warden-protocol/community-agents/issues
- Documentation: https://docs.wardenprotocol.org

## Quick Reference Commands

```bash
# Study example agents (DON'T BUILD THESE)
git clone https://github.com/warden-protocol/community-agents.git
cd community-agents/agents/weather-agent  # Study the code
cd community-agents/agents/coingecko-agent  # Study the patterns

# Create YOUR new agent
python scripts/init-agent.py my-unique-agent \
  --template typescript \
  --description "YOUR unique agent description"

# Install dependencies (TypeScript)
npm install

# Install dependencies (Python)
pip install -r requirements.txt

# Test locally
npm run dev  # or: langgraph dev

# Deploy (LangSmith Deployments)
# Use the LangSmith Deployments UI after pushing to GitHub

# Build Docker image (for self-hosting)
docker build -t my-warden-agent .

# Run Docker container
docker run -p 8000:8000 my-warden-agent
```

## Success Checklist

Before submitting to incentive programme:

- [ ] Agent built with LangGraph
- [ ] API accessible and tested
- [ ] One agent per LangGraph instance
- [ ] No wallet access or data storage (Phase 1)
- [ ] Clear documentation in README
- [ ] Environment variables properly configured
- [ ] Error handling implemented
- [ ] Tested with various inputs
- [ ] Unique and useful functionality
- [ ] Ready for Warden Studio registration
