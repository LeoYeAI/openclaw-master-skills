# API Integration & Deployment Guide

Detailed guide for integrating APIs and deploying Warden agents to production.

## API Integration Patterns

### Environment Configuration

```typescript
// config.ts
import dotenv from 'dotenv';

dotenv.config();

export const config = {
  openai: {
    apiKey: process.env.OPENAI_API_KEY!,
    model: process.env.OPENAI_MODEL || 'gpt-4',
    temperature: parseFloat(process.env.OPENAI_TEMPERATURE || '0.7')
  },
  apis: {
    coingecko: {
      key: process.env.COINGECKO_API_KEY,
      baseUrl: 'https://api.coingecko.com/api/v3'
    },
    alchemy: {
      key: process.env.ALCHEMY_API_KEY!,
      network: process.env.ALCHEMY_NETWORK || 'mainnet'
    },
    weather: {
      key: process.env.WEATHER_API_KEY!,
      baseUrl: 'https://api.weatherapi.com/v1'
    }
  },
  server: {
    port: parseInt(process.env.PORT || '8000'),
    host: process.env.HOST || '0.0.0.0'
  }
};

// Validation
function validateConfig() {
  const required = ['OPENAI_API_KEY'];
  const missing = required.filter(key => !process.env[key]);
  
  if (missing.length > 0) {
    throw new Error(`Missing required env vars: ${missing.join(', ')}`);
  }
}

validateConfig();
```

### API Client Pattern

```typescript
// api-client.ts
import axios, { AxiosInstance, AxiosError } from 'axios';

export class APIClient {
  private client: AxiosInstance;
  private retryCount = 3;
  private retryDelay = 1000;
  
  constructor(baseURL: string, apiKey?: string) {
    this.client = axios.create({
      baseURL,
      timeout: 10000,
      headers: apiKey ? { 'Authorization': `Bearer ${apiKey}` } : {}
    });
    
    this.setupInterceptors();
  }
  
  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        console.log(`[API] ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => Promise.reject(error)
    );
    
    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        return this.handleError(error);
      }
    );
  }
  
  private async handleError(error: AxiosError) {
    const config = error.config!;
    
    // Retry on rate limit
    if (error.response?.status === 429) {
      const retryAfter = parseInt(
        error.response.headers['retry-after'] || '60'
      );
      
      await this.delay(retryAfter * 1000);
      return this.client.request(config);
    }
    
    // Retry on server errors
    if (error.response?.status && error.response.status >= 500) {
      const retries = (config as any).__retries || 0;
      
      if (retries < this.retryCount) {
        (config as any).__retries = retries + 1;
        await this.delay(this.retryDelay * (retries + 1));
        return this.client.request(config);
      }
    }
    
    throw this.formatError(error);
  }
  
  private formatError(error: AxiosError): Error {
    if (error.response) {
      return new Error(
        `API Error ${error.response.status}: ${error.response.data}`
      );
    } else if (error.request) {
      return new Error('No response from API');
    } else {
      return new Error(`Request failed: ${error.message}`);
    }
  }
  
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
  
  async get<T>(url: string, params?: any): Promise<T> {
    const response = await this.client.get<T>(url, { params });
    return response.data;
  }
  
  async post<T>(url: string, data?: any): Promise<T> {
    const response = await this.client.post<T>(url, data);
    return response.data;
  }
}
```

### Rate Limiting

```typescript
// rate-limiter.ts
export class RateLimiter {
  private requests: number[] = [];
  private maxRequests: number;
  private windowMs: number;
  
  constructor(maxRequests: number, windowMs: number) {
    this.maxRequests = maxRequests;
    this.windowMs = windowMs;
  }
  
  async acquire(): Promise<void> {
    const now = Date.now();
    
    // Remove old requests outside window
    this.requests = this.requests.filter(
      time => now - time < this.windowMs
    );
    
    // Check if we're at limit
    if (this.requests.length >= this.maxRequests) {
      const oldestRequest = this.requests[0];
      const waitTime = this.windowMs - (now - oldestRequest);
      await this.delay(waitTime);
      return this.acquire();
    }
    
    this.requests.push(now);
  }
  
  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Usage
const limiter = new RateLimiter(5, 1000); // 5 requests per second

async function fetchData(url: string) {
  await limiter.acquire();
  return fetch(url);
}
```

### Caching Layer

```typescript
// cache.ts
import NodeCache from 'node-cache';

export class Cache {
  private cache: NodeCache;
  
  constructor(ttlSeconds: number = 300) {
    this.cache = new NodeCache({
      stdTTL: ttlSeconds,
      checkperiod: ttlSeconds * 0.2
    });
  }
  
  get<T>(key: string): T | undefined {
    return this.cache.get<T>(key);
  }
  
  set<T>(key: string, value: T, ttl?: number): boolean {
    return this.cache.set(key, value, ttl || 0);
  }
  
  del(key: string): number {
    return this.cache.del(key);
  }
  
  flush(): void {
    this.cache.flushAll();
  }
  
  async wrap<T>(
    key: string,
    fetcher: () => Promise<T>,
    ttl?: number
  ): Promise<T> {
    const cached = this.get<T>(key);
    if (cached !== undefined) {
      return cached;
    }
    
    const fresh = await fetcher();
    this.set(key, fresh, ttl);
    return fresh;
  }
}

// Usage
const cache = new Cache(300); // 5 minute TTL

async function getCoinPrice(coinId: string): Promise<number> {
  return cache.wrap(
    `price:${coinId}`,
    async () => {
      const data = await api.get(`/coins/${coinId}`);
      return data.market_data.current_price.usd;
    },
    60 // Override: 1 minute TTL for prices
  );
}
```

## Deployment Strategies

### LangSmith Deployments (Cloud)

**Prerequisites:**
- LangSmith account (https://smith.langchain.com)
- LangSmith API key
- OpenAI API key

**Getting LangSmith API Key:**
```bash
# 1. Sign up at https://smith.langchain.com
# 2. Navigate to Settings → API Keys
# 3. Click "Create API Key"
# 4. Copy the key (starts with [YOUR-LANGSMITH-API-KEY])
# 5. Store securely - it won't be shown again
```

**Deployment Steps:**

1. Push your agent repository to GitHub.
2. Create a new deployment in LangSmith Deployments.
3. Connect the repo, set environment variables, and deploy.

**Environment Variables for Deployment:**

In LangSmith deployment settings, add:
```bash
OPENAI_API_KEY=[YOUR-OPENAI-API-KEY]
# Other API keys your agent needs
COINGECKO_API_KEY=...
ALCHEMY_API_KEY=...
```

**⚠️ Important**: Never commit API keys to Git. The LangSmith API key is used for:
- Authentication when calling your deployed agent
- Tracing and monitoring (optional)
- Access control

**Using Your Deployed Agent:**

All API calls require the `x-api-key` header with your LangSmith API key:

```bash
curl YOUR_AGENT_URL/runs/wait \
  --request POST \
  --header 'Content-Type: application/json' \
  --header 'x-api-key: [YOUR-LANGSMITH-API-KEY]' \
  --data '{
    "assistant_id": "[YOUR-AGENT-ID]",
    "input": {
      "messages": [
        {"role": "user", "content": "What can you do?"}
      ]
    }
  }'
```

### Docker Deployment

```dockerfile
# Dockerfile
FROM node:18-alpine

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy source
COPY . .

# Build TypeScript
RUN npm run build

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD node healthcheck.js

EXPOSE 8000

CMD ["node", "dist/index.js"]
```

```javascript
// healthcheck.js
const http = require('http');

const options = {
  hostname: 'localhost',
  port: 8000,
  path: '/health',
  method: 'GET',
  timeout: 2000
};

const req = http.request(options, (res) => {
  if (res.statusCode === 200) {
    process.exit(0);
  } else {
    process.exit(1);
  }
});

req.on('error', () => {
  process.exit(1);
});

req.on('timeout', () => {
  req.destroy();
  process.exit(1);
});

req.end();
```

### Docker Compose Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  agent:
    build: .
    ports:
      - "8000:8000"
    environment:
      - NODE_ENV=production
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - COINGECKO_API_KEY=${COINGECKO_API_KEY}
    restart: unless-stopped
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    healthcheck:
      test: ["CMD", "node", "healthcheck.js"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 40s
```

### Kubernetes Deployment

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: warden-agent
spec:
  replicas: 3
  selector:
    matchLabels:
      app: warden-agent
  template:
    metadata:
      labels:
        app: warden-agent
    spec:
      containers:
      - name: agent
        image: your-registry/warden-agent:latest
        ports:
        - containerPort: 8000
        env:
        - name: OPENAI_API_KEY
          valueFrom:
            secretKeyRef:
              name: agent-secrets
              key: openai-api-key
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
---
apiVersion: v1
kind: Service
metadata:
  name: warden-agent
spec:
  selector:
    app: warden-agent
  ports:
  - port: 80
    targetPort: 8000
  type: LoadBalancer
```

## Production Server Setup

### Express Server with Endpoints

```typescript
// server.ts
import express from 'express';
import helmet from 'helmet';
import cors from 'cors';
import { agent } from './agent';
import { config } from './config';

const app = express();

// Middleware
app.use(helmet());
app.use(cors());
app.use(express.json());

// Request logging
app.use((req, res, next) => {
  console.log(`${new Date().toISOString()} ${req.method} ${req.path}`);
  next();
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

// Readiness check
app.get('/ready', async (req, res) => {
  try {
    // Check dependencies
    await checkDependencies();
    res.json({ status: 'ready' });
  } catch (error) {
    res.status(503).json({ status: 'not ready', error: error.message });
  }
});

// Main agent endpoint
app.post('/invoke', async (req, res) => {
  try {
    const { input } = req.body;
    
    if (!input) {
      return res.status(400).json({ error: 'Input required' });
    }
    
    const result = await agent.invoke({ input });
    res.json(result);
    
  } catch (error) {
    console.error('Agent error:', error);
    res.status(500).json({ 
      error: 'Internal error',
      message: error.message 
    });
  }
});

// Streaming endpoint
app.post('/stream', async (req, res) => {
  try {
    const { input } = req.body;
    
    res.setHeader('Content-Type', 'text/event-stream');
    res.setHeader('Cache-Control', 'no-cache');
    res.setHeader('Connection', 'keep-alive');
    
    const stream = await agent.stream({ input });
    
    for await (const chunk of stream) {
      res.write(`data: ${JSON.stringify(chunk)}\n\n`);
    }
    
    res.end();
    
  } catch (error) {
    console.error('Streaming error:', error);
    res.write(`data: ${JSON.stringify({ error: error.message })}\n\n`);
    res.end();
  }
});

// Error handler
app.use((error, req, res, next) => {
  console.error('Unhandled error:', error);
  res.status(500).json({ error: 'Internal server error' });
});

// Start server
const port = config.server.port;
app.listen(port, () => {
  console.log(`Agent server running on port ${port}`);
});

async function checkDependencies() {
  // Check external services
  const checks = [
    checkOpenAI(),
    checkExternalAPIs()
  ];
  
  await Promise.all(checks);
}

async function checkOpenAI() {
  // Verify OpenAI API key works
}

async function checkExternalAPIs() {
  // Verify external APIs accessible
}
```

## Monitoring & Logging

### Structured Logging

```typescript
// logger.ts
import winston from 'winston';

export const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: { service: 'warden-agent' },
  transports: [
    new winston.transports.Console({
      format: winston.format.combine(
        winston.format.colorize(),
        winston.format.simple()
      )
    }),
    new winston.transports.File({ 
      filename: 'logs/error.log', 
      level: 'error' 
    }),
    new winston.transports.File({ 
      filename: 'logs/combined.log' 
    })
  ]
});

// Usage
logger.info('Agent started', { port: 8000 });
logger.error('API call failed', { error: err.message, url });
logger.debug('Processing request', { input });
```

### Metrics Collection

```typescript
// metrics.ts
import { Counter, Histogram, register } from 'prom-client';

export const metrics = {
  requests: new Counter({
    name: 'agent_requests_total',
    help: 'Total number of agent requests',
    labelNames: ['status']
  }),
  
  duration: new Histogram({
    name: 'agent_request_duration_seconds',
    help: 'Agent request duration',
    buckets: [0.1, 0.5, 1, 2, 5, 10]
  }),
  
  errors: new Counter({
    name: 'agent_errors_total',
    help: 'Total number of errors',
    labelNames: ['type']
  })
};

// Metrics endpoint
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(await register.metrics());
});

// Usage
const end = metrics.duration.startTimer();
try {
  const result = await processRequest(input);
  metrics.requests.inc({ status: 'success' });
  return result;
} catch (error) {
  metrics.requests.inc({ status: 'error' });
  metrics.errors.inc({ type: error.name });
  throw error;
} finally {
  end();
}
```

## Security Best Practices

### API Key Management

```typescript
// Never commit API keys
// Use environment variables
// Rotate keys regularly
// Use different keys for dev/prod

// secrets-manager.ts
import { SecretsManager } from 'aws-sdk';

export class SecretManager {
  private client = new SecretsManager();
  
  async getSecret(secretName: string): Promise<string> {
    const result = await this.client
      .getSecretValue({ SecretId: secretName })
      .promise();
    
    return result.SecretString!;
  }
}

// Usage
const secretManager = new SecretManager();
const apiKey = await secretManager.getSecret('openai-api-key');
```

### Input Validation

```typescript
// validate.ts
import { z } from 'zod';

const requestSchema = z.object({
  input: z.string().min(1).max(1000),
  options: z.object({
    temperature: z.number().min(0).max(1).optional(),
    maxTokens: z.number().positive().optional()
  }).optional()
});

export function validateRequest(data: unknown) {
  return requestSchema.parse(data);
}

// Usage in endpoint
app.post('/invoke', async (req, res) => {
  try {
    const validated = validateRequest(req.body);
    const result = await agent.invoke(validated.input);
    res.json(result);
  } catch (error) {
    if (error instanceof z.ZodError) {
      res.status(400).json({ errors: error.errors });
    } else {
      res.status(500).json({ error: 'Internal error' });
    }
  }
});
```

### Rate Limiting Middleware

```typescript
// rate-limit.ts
import rateLimit from 'express-rate-limit';

export const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // 100 requests per window
  message: 'Too many requests, please try again later',
  standardHeaders: true,
  legacyHeaders: false
});

// Apply to routes
app.use('/invoke', limiter);
app.use('/stream', limiter);
```

## CI/CD Pipeline

### GitHub Actions Workflow

```yaml
# .github/workflows/deploy.yml
name: Deploy Agent

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Node
        uses: actions/setup-node@v3
        with:
          node-version: '18'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Run tests
        run: npm test
      
      - name: Lint
        run: npm run lint
  
  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to LangSmith Deployments
        run: |
          echo \"Deployments are created in the LangSmith Deployments UI\"
```

This comprehensive guide covers all aspects of API integration and deployment for Warden Protocol agents. Use these patterns as reference when building production-ready agents.
