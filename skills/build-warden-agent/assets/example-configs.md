# Example Warden Agent Configurations

This file contains example configurations for common Warden agent patterns.

## 1. Simple Weather Agent Configuration

```json
{
  "agent_id": "weather-agent",
  "name": "Weather Agent",
  "description": "Provides current weather information for any location",
  "capabilities": [
    "Current weather lookup",
    "Temperature conversion",
    "Weather forecasts"
  ],
  "required_apis": {
    "WEATHER_API_KEY": "https://www.weatherapi.com"
  },
  "deployment": {
    "type": "langgraph-cloud",
    "runtime": "typescript",
    "node_version": "18"
  }
}
```

## 2. Crypto Price Analyzer Configuration

```json
{
  "agent_id": "crypto-analyzer",
  "name": "Crypto Price Analyzer",
  "description": "Analyzes cryptocurrency prices and market trends",
  "capabilities": [
    "Real-time price lookup",
    "Historical price analysis",
    "Market trend identification",
    "Comparative analysis"
  ],
  "required_apis": {
    "COINGECKO_API_KEY": "https://www.coingecko.com/api",
    "OPENAI_API_KEY": "https://platform.openai.com"
  },
  "deployment": {
    "type": "langgraph-cloud",
    "runtime": "typescript",
    "node_version": "18"
  }
}
```

## 3. Portfolio Tracker Configuration

```json
{
  "agent_id": "portfolio-tracker",
  "name": "Portfolio Tracker",
  "description": "Tracks and analyzes cryptocurrency portfolios across multiple chains",
  "capabilities": [
    "Multi-chain balance tracking",
    "Portfolio value calculation",
    "Performance analysis",
    "Risk assessment"
  ],
  "required_apis": {
    "ALCHEMY_API_KEY": "https://www.alchemy.com",
    "COINGECKO_API_KEY": "https://www.coingecko.com/api",
    "OPENAI_API_KEY": "https://platform.openai.com"
  },
  "supported_chains": [
    "ethereum",
    "polygon",
    "solana",
    "arbitrum"
  ],
  "deployment": {
    "type": "langgraph-cloud",
    "runtime": "typescript",
    "node_version": "18"
  }
}
```

## 4. DeFi Yield Finder Configuration

```json
{
  "agent_id": "defi-yield-finder",
  "name": "DeFi Yield Finder",
  "description": "Finds and compares DeFi yield opportunities",
  "capabilities": [
    "Yield rate comparison",
    "Protocol safety analysis",
    "APY calculations",
    "Historical performance"
  ],
  "required_apis": {
    "DEFILLAMA_API": "https://api.llama.fi",
    "COINGECKO_API_KEY": "https://www.coingecko.com/api",
    "OPENAI_API_KEY": "https://platform.openai.com"
  },
  "protocols": [
    "aave",
    "compound",
    "uniswap",
    "curve"
  ],
  "deployment": {
    "type": "self-hosted",
    "runtime": "python",
    "python_version": "3.11"
  }
}
```

## Environment Variable Template

```bash
# ===========================
# Core Configuration
# ===========================
NODE_ENV=production
PORT=8000
LOG_LEVEL=info

# ===========================
# OpenAI Configuration
# ===========================
OPENAI_API_KEY=[YOUR-OPENAI-API-KEY]
OPENAI_MODEL=gpt-4
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=1000

# ===========================
# LangSmith Configuration
# ===========================
# Required for LangSmith Deployments deployment
LANGSMITH_API_KEY=[YOUR-LANGSMITH-API-KEY]
# Optional: Enable tracing
LANGSMITH_TRACING=true
LANGSMITH_PROJECT=your-project-name

# ===========================
# Web3 APIs
# ===========================
# Alchemy - Ethereum/Polygon
ALCHEMY_API_KEY=...
ALCHEMY_NETWORK=mainnet

# CoinGecko - Price Data
COINGECKO_API_KEY=...

# Etherscan - Ethereum Explorer
ETHERSCAN_API_KEY=...

# ===========================
# Traditional APIs
# ===========================
# Weather API
WEATHER_API_KEY=...

# News API
NEWS_API_KEY=...

# ===========================
# Database (if needed)
# ===========================
DATABASE_URL=postgresql://user:pass@host:5432/db

# Redis (if using caching)
REDIS_URL=redis://localhost:6379

# ===========================
# Monitoring
# ===========================
SENTRY_DSN=...
```

## LangGraph Configuration Templates

### TypeScript Agent

```json
{
  "agent_id": "my-agent",
  "dependencies": ["."],
  "graphs": {
    "agent": "./src/graph.ts"
  },
  "env": ".env",
  "python_version": null
}
```

### Python Agent

```json
{
  "agent_id": "my-agent",
  "python_version": "3.11",
  "dependencies": ["."],
  "graphs": {
    "agent": "./src/graph.py"
  },
  "env": ".env"
}
```

## Docker Compose Examples

### Simple Agent

```yaml
version: '3.8'

services:
  agent:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 3s
      retries: 3
```

### Agent with Redis Cache

```yaml
version: '3.8'

services:
  agent:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      - REDIS_URL=redis://redis:6379
    depends_on:
      - redis
    restart: unless-stopped
  
  redis:
    image: redis:alpine
    ports:
      - "6379:6379"
    volumes:
      - redis-data:/data
    restart: unless-stopped

volumes:
  redis-data:
```

### Agent with PostgreSQL

```yaml
version: '3.8'

services:
  agent:
    build: .
    ports:
      - "8000:8000"
    env_file:
      - .env
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/agent
    depends_on:
      - db
    restart: unless-stopped
  
  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: agent
    volumes:
      - postgres-data:/var/lib/postgresql/data
    restart: unless-stopped

volumes:
  postgres-data:
```

## Warden Studio Registration Checklist

When registering your agent with Warden Studio:

### Required Information
- [ ] Agent name (user-facing)
- [ ] Clear description (2-3 sentences)
- [ ] API URL (must be HTTPS)
- [ ] API key for authentication
- [ ] Avatar/logo image (recommended: 512x512px PNG)

### Capabilities List
List 3-5 specific capabilities:
- [ ] Capability 1 (e.g., "Real-time price lookup")
- [ ] Capability 2 (e.g., "Historical analysis")
- [ ] Capability 3 (e.g., "Trend prediction")

### Testing Checklist
Before registration:
- [ ] Agent responds to health checks
- [ ] All API endpoints work correctly
- [ ] Error handling is implemented
- [ ] Response times are acceptable (<5s)
- [ ] API authentication works
- [ ] Documentation is complete

### Example Registration Data

```json
{
  "agent": {
    "name": "Crypto Analyzer Pro",
    "description": "Advanced cryptocurrency analysis tool that provides real-time price data, technical analysis, and market insights across 1000+ tokens.",
    "api_url": "https://api.myagent.com",
    "api_key": "warden_xxxxxxxxxxxxx",
    "avatar_url": "https://cdn.myagent.com/avatar.png",
    "capabilities": [
      "Real-time price lookup for 1000+ tokens",
      "Technical analysis with 20+ indicators",
      "Market sentiment analysis",
      "Historical price charts",
      "Portfolio tracking"
    ],
    "categories": [
      "defi",
      "analytics",
      "trading"
    ],
    "supported_chains": [
      "ethereum",
      "bsc",
      "polygon",
      "solana"
    ],
    "pricing": {
      "model": "free",
      "rate_limits": {
        "requests_per_minute": 60,
        "requests_per_day": 1000
      }
    }
  }
}
```

## API Response Format Standards

### Success Response

```json
{
  "success": true,
  "data": {
    "output": "Agent response here...",
    "metadata": {
      "tokens_used": 150,
      "processing_time_ms": 1234,
      "model": "gpt-4"
    }
  }
}
```

### Error Response

```json
{
  "success": false,
  "error": {
    "code": "INVALID_INPUT",
    "message": "User-friendly error message",
    "details": "Technical details for debugging"
  }
}
```

### Streaming Response

```
data: {"type": "start", "timestamp": "2025-01-15T10:00:00Z"}

data: {"type": "chunk", "content": "Analyzing data..."}

data: {"type": "chunk", "content": "Results show..."}

data: {"type": "end", "metadata": {"tokens": 150}}
```
