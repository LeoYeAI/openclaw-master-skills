# LangGraph Agent Patterns for Warden

Detailed patterns and examples for building production-ready LangGraph agents.

## Agent Architecture Patterns

### Pattern 1: Simple Request-Response Agent

**Use for**: Basic queries, data fetching, simple transformations

```typescript
import { StateGraph, END } from "@langchain/langgraph";
import { ChatOpenAI } from "@langchain/openai";

// Define state
interface AgentState {
  input: string;
  output?: string;
  error?: string;
}

// Single node function
async function processRequest(state: AgentState) {
  try {
    const llm = new ChatOpenAI({ modelName: "gpt-4" });
    const response = await llm.invoke(state.input);
    return { output: response.content };
  } catch (error) {
    return { error: error.message };
  }
}

// Build graph
const workflow = new StateGraph<AgentState>({
  channels: {
    input: null,
    output: null,
    error: null
  }
});

workflow.addNode("process", processRequest);
workflow.setEntryPoint("process");
workflow.addEdge("process", END);

export const agent = workflow.compile();
```

### Pattern 2: Schema-Guided Reasoning (SGR)

**Use for**: Complex analysis, multi-step workflows, data validation

```typescript
import { StateGraph, END } from "@langchain/langgraph";
import { z } from "zod";

// Define structured state
interface AgentState {
  // Input
  rawInput: string;
  
  // Validation
  isValid: boolean;
  validationError?: string;
  
  // Extraction
  extractedParams?: {
    token?: string;
    timeframe?: string;
    metric?: string;
  };
  
  // Data fetching
  rawData?: any;
  fetchError?: string;
  
  // Analysis
  analysis?: {
    summary: string;
    metrics: Record<string, number>;
    insights: string[];
  };
  
  // Output
  finalResponse?: string;
}

// Step 1: Validate input
async function validateInput(state: AgentState) {
  const schema = z.object({
    token: z.string().min(1),
    timeframe: z.enum(["1d", "7d", "30d"]).optional()
  });
  
  try {
    // Use LLM to extract structured data
    const llm = new ChatOpenAI({ modelName: "gpt-4" });
    const prompt = `Extract token and timeframe from: "${state.rawInput}"
    Return JSON: {"token": "...", "timeframe": "..."}`;
    
    const response = await llm.invoke(prompt);
    const parsed = JSON.parse(response.content);
    schema.parse(parsed);
    
    return { isValid: true };
  } catch (error) {
    return { 
      isValid: false, 
      validationError: error.message 
    };
  }
}

// Step 2: Extract parameters
async function extractParameters(state: AgentState) {
  if (!state.isValid) return state;
  
  const llm = new ChatOpenAI({ modelName: "gpt-4" });
  const prompt = `Extract structured parameters from: "${state.rawInput}"
  Return JSON with: token, timeframe, metric`;
  
  const response = await llm.invoke(prompt);
  const params = JSON.parse(response.content);
  
  return { extractedParams: params };
}

// Step 3: Fetch data
async function fetchData(state: AgentState) {
  if (!state.extractedParams) return state;
  
  try {
    const { token } = state.extractedParams;
    const response = await fetch(
      `https://api.coingecko.com/api/v3/coins/${token}`
    );
    const data = await response.json();
    
    return { rawData: data };
  } catch (error) {
    return { fetchError: error.message };
  }
}

// Step 4: Analyze data
async function analyzeData(state: AgentState) {
  if (!state.rawData) return state;
  
  const analysis = {
    summary: `Analysis of ${state.extractedParams?.token}`,
    metrics: {
      price: state.rawData.market_data.current_price.usd,
      volume: state.rawData.market_data.total_volume.usd,
      marketCap: state.rawData.market_data.market_cap.usd
    },
    insights: [
      "Price trend analysis",
      "Volume pattern",
      "Market sentiment"
    ]
  };
  
  return { analysis };
}

// Step 5: Generate response
async function generateResponse(state: AgentState) {
  if (!state.analysis) return state;
  
  const llm = new ChatOpenAI({ modelName: "gpt-4" });
  const prompt = `Generate user-friendly response from analysis:
  ${JSON.stringify(state.analysis, null, 2)}`;
  
  const response = await llm.invoke(prompt);
  
  return { finalResponse: response.content };
}

// Build workflow
const workflow = new StateGraph<AgentState>({
  channels: {
    rawInput: null,
    isValid: null,
    validationError: null,
    extractedParams: null,
    rawData: null,
    fetchError: null,
    analysis: null,
    finalResponse: null
  }
});

workflow.addNode("validate", validateInput);
workflow.addNode("extract", extractParameters);
workflow.addNode("fetch", fetchData);
workflow.addNode("analyze", analyzeData);
workflow.addNode("generate", generateResponse);

workflow.setEntryPoint("validate");
workflow.addEdge("validate", "extract");
workflow.addEdge("extract", "fetch");
workflow.addEdge("fetch", "analyze");
workflow.addEdge("analyze", "generate");
workflow.addEdge("generate", END);

export const agent = workflow.compile();
```

### Pattern 3: Parallel Data Fetching

**Use for**: Comparing multiple items, aggregating data from multiple sources

```typescript
import { StateGraph, END } from "@langchain/langgraph";

interface AgentState {
  input: string;
  items: string[];
  results: Array<{
    item: string;
    data: any;
    error?: string;
  }>;
  comparison?: string;
}

// Parse items to compare
async function parseItems(state: AgentState) {
  const llm = new ChatOpenAI({ modelName: "gpt-4" });
  const prompt = `Extract items to compare from: "${state.input}"
  Return JSON array: ["item1", "item2"]`;
  
  const response = await llm.invoke(prompt);
  const items = JSON.parse(response.content);
  
  return { items };
}

// Fetch data for all items in parallel
async function fetchAllData(state: AgentState) {
  const results = await Promise.all(
    state.items.map(async (item) => {
      try {
        const response = await fetch(`https://api.example.com/${item}`);
        const data = await response.json();
        return { item, data };
      } catch (error) {
        return { item, data: null, error: error.message };
      }
    })
  );
  
  return { results };
}

// Compare and generate report
async function compareResults(state: AgentState) {
  const llm = new ChatOpenAI({ modelName: "gpt-4" });
  const prompt = `Compare these items and provide insights:
  ${JSON.stringify(state.results, null, 2)}`;
  
  const response = await llm.invoke(prompt);
  
  return { comparison: response.content };
}

const workflow = new StateGraph<AgentState>({
  channels: {
    input: null,
    items: null,
    results: null,
    comparison: null
  }
});

workflow.addNode("parse", parseItems);
workflow.addNode("fetch", fetchAllData);
workflow.addNode("compare", compareResults);

workflow.setEntryPoint("parse");
workflow.addEdge("parse", "fetch");
workflow.addEdge("fetch", "compare");
workflow.addEdge("compare", END);

export const agent = workflow.compile();
```

### Pattern 4: Conditional Routing

**Use for**: Different paths based on input, error handling, feature flags

```typescript
import { StateGraph, END } from "@langchain/langgraph";

interface AgentState {
  input: string;
  requestType?: "query" | "analysis" | "comparison";
  result?: string;
}

// Classify request type
async function classifyRequest(state: AgentState) {
  const llm = new ChatOpenAI({ modelName: "gpt-4" });
  const prompt = `Classify this request: "${state.input}"
  Return one of: query, analysis, comparison`;
  
  const response = await llm.invoke(prompt);
  const type = response.content.trim() as AgentState["requestType"];
  
  return { requestType: type };
}

// Routing function
function routeByType(state: AgentState) {
  return state.requestType || "query";
}

// Handler for each type
async function handleQuery(state: AgentState) {
  // Simple query logic
  return { result: "Query result" };
}

async function handleAnalysis(state: AgentState) {
  // Complex analysis logic
  return { result: "Analysis result" };
}

async function handleComparison(state: AgentState) {
  // Comparison logic
  return { result: "Comparison result" };
}

const workflow = new StateGraph<AgentState>({
  channels: {
    input: null,
    requestType: null,
    result: null
  }
});

workflow.addNode("classify", classifyRequest);
workflow.addNode("query", handleQuery);
workflow.addNode("analysis", handleAnalysis);
workflow.addNode("comparison", handleComparison);

workflow.setEntryPoint("classify");
workflow.addConditionalEdges(
  "classify",
  routeByType,
  {
    query: "query",
    analysis: "analysis",
    comparison: "comparison"
  }
);

workflow.addEdge("query", END);
workflow.addEdge("analysis", END);
workflow.addEdge("comparison", END);

export const agent = workflow.compile();
```

## Python Examples

### Basic Python Agent

```python
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from typing import TypedDict

class AgentState(TypedDict):
    input: str
    output: str | None
    error: str | None

async def process_request(state: AgentState) -> AgentState:
    try:
        llm = ChatOpenAI(model="gpt-4")
        response = await llm.ainvoke(state["input"])
        return {"output": response.content}
    except Exception as e:
        return {"error": str(e)}

workflow = StateGraph(AgentState)
workflow.add_node("process", process_request)
workflow.set_entry_point("process")
workflow.add_edge("process", END)

agent = workflow.compile()
```

### SGR Pattern in Python

```python
from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from typing import TypedDict, Optional, Dict, List, Any
import json

class AgentState(TypedDict):
    raw_input: str
    is_valid: bool
    validation_error: Optional[str]
    extracted_params: Optional[Dict[str, Any]]
    raw_data: Optional[Any]
    fetch_error: Optional[str]
    analysis: Optional[Dict[str, Any]]
    final_response: Optional[str]

async def validate_input(state: AgentState) -> AgentState:
    llm = ChatOpenAI(model="gpt-4")
    prompt = f"""Extract token and timeframe from: "{state['raw_input']}"
    Return JSON: {{"token": "...", "timeframe": "..."}}"""
    
    try:
        response = await llm.ainvoke(prompt)
        parsed = json.loads(response.content)
        return {"is_valid": True}
    except Exception as e:
        return {"is_valid": False, "validation_error": str(e)}

async def extract_parameters(state: AgentState) -> AgentState:
    if not state.get("is_valid"):
        return state
    
    llm = ChatOpenAI(model="gpt-4")
    prompt = f"""Extract parameters from: "{state['raw_input']}"
    Return JSON with: token, timeframe, metric"""
    
    response = await llm.ainvoke(prompt)
    params = json.loads(response.content)
    
    return {"extracted_params": params}

async def fetch_data(state: AgentState) -> AgentState:
    if not state.get("extracted_params"):
        return state
    
    # Fetch data logic
    return {"raw_data": {}}

async def analyze_data(state: AgentState) -> AgentState:
    if not state.get("raw_data"):
        return state
    
    analysis = {
        "summary": "Analysis summary",
        "metrics": {},
        "insights": []
    }
    
    return {"analysis": analysis}

async def generate_response(state: AgentState) -> AgentState:
    if not state.get("analysis"):
        return state
    
    llm = ChatOpenAI(model="gpt-4")
    prompt = f"""Generate response from analysis:
    {json.dumps(state['analysis'], indent=2)}"""
    
    response = await llm.ainvoke(prompt)
    return {"final_response": response.content}

# Build workflow
workflow = StateGraph(AgentState)
workflow.add_node("validate", validate_input)
workflow.add_node("extract", extract_parameters)
workflow.add_node("fetch", fetch_data)
workflow.add_node("analyze", analyze_data)
workflow.add_node("generate", generate_response)

workflow.set_entry_point("validate")
workflow.add_edge("validate", "extract")
workflow.add_edge("extract", "fetch")
workflow.add_edge("fetch", "analyze")
workflow.add_edge("analyze", "generate")
workflow.add_edge("generate", END)

agent = workflow.compile()
```

## Error Handling Best Practices

### Graceful Degradation

```typescript
async function fetchWithFallback(state: AgentState) {
  try {
    // Try primary API
    const data = await primaryAPI.fetch(state.query);
    return { data, source: "primary" };
  } catch (error) {
    try {
      // Fallback to secondary API
      const data = await secondaryAPI.fetch(state.query);
      return { data, source: "secondary" };
    } catch (fallbackError) {
      // Return cached data or error
      return { 
        error: "Both APIs failed",
        cached: getCachedData(state.query)
      };
    }
  }
}
```

### User-Friendly Error Messages

```typescript
function formatError(error: Error, context: string): string {
  const errorMessages = {
    RATE_LIMIT: "I'm getting too many requests. Please try again in a moment.",
    INVALID_TOKEN: "I couldn't find information about that token. Please check the name.",
    API_DOWN: "The data service is temporarily unavailable. Please try again later.",
    NETWORK_ERROR: "I'm having trouble connecting. Please check your internet connection."
  };
  
  // Match error type and return friendly message
  const errorType = identifyErrorType(error);
  return errorMessages[errorType] || "Something went wrong. Please try again.";
}
```

## Testing Patterns

### Unit Testing Agent Nodes

```typescript
import { describe, it, expect } from "vitest";

describe("validateInput", () => {
  it("should accept valid token query", async () => {
    const state = { rawInput: "What's the price of Bitcoin?" };
    const result = await validateInput(state);
    expect(result.isValid).toBe(true);
  });
  
  it("should reject empty query", async () => {
    const state = { rawInput: "" };
    const result = await validateInput(state);
    expect(result.isValid).toBe(false);
    expect(result.validationError).toBeDefined();
  });
});
```

### Integration Testing Agent Flow

```typescript
describe("Agent End-to-End", () => {
  it("should process valid query", async () => {
    const input = { rawInput: "Compare Bitcoin and Ethereum" };
    const result = await agent.invoke(input);
    
    expect(result.finalResponse).toBeDefined();
    expect(result.finalResponse).toContain("Bitcoin");
    expect(result.finalResponse).toContain("Ethereum");
  });
});
```

## Performance Optimization

### Caching Strategies

```typescript
import NodeCache from "node-cache";

const cache = new NodeCache({ stdTTL: 300 }); // 5 minute cache

async function fetchWithCache(key: string) {
  const cached = cache.get(key);
  if (cached) return cached;
  
  const fresh = await fetch(apiUrl);
  cache.set(key, fresh);
  return fresh;
}
```

### Parallel Processing

```typescript
// Bad: Sequential
const btcData = await fetchToken("bitcoin");
const ethData = await fetchToken("ethereum");

// Good: Parallel
const [btcData, ethData] = await Promise.all([
  fetchToken("bitcoin"),
  fetchToken("ethereum")
]);
```

### Token Optimization

```typescript
// Minimize tokens in LLM calls
const prompt = `Analyze: ${compactData}`;  // Not: ${JSON.stringify(allData, null, 2)}

// Use streaming for long responses
const stream = await llm.stream(prompt);
for await (const chunk of stream) {
  // Process incrementally
}
```
