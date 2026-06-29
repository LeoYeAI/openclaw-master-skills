#!/usr/bin/env python3
"""
Warden Agent Initializer
Quickly scaffold a new Warden Protocol agent from templates.
"""

import os
import sys
import json
import argparse
from pathlib import Path

TEMPLATES = {
    "typescript": {
        "name": "TypeScript Agent",
        "base": "langgraph-quick-start",
        "files": {
            "package.json": """{
  "name": "{agent_name}",
  "version": "1.0.0",
  "description": "{description}",
  "main": "dist/index.js",
  "scripts": {
    "dev": "langgraph dev",
    "build": "tsc",
    "start": "node dist/index.js",
    "test": "vitest"
  },
  "dependencies": {
    "@langchain/langgraph": "^0.0.19",
    "@langchain/openai": "^0.0.19",
    "dotenv": "^16.0.3",
    "express": "^4.18.2"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0",
    "vitest": "^1.0.0"
  }
}""",
            "tsconfig.json": """{
  "compilerOptions": {
    "target": "ES2022",
    "module": "commonjs",
    "lib": ["ES2022"],
    "outDir": "./dist",
    "rootDir": "./src",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}""",
            "langgraph.json": """{
  "agent_id": "{agent_name}",
  "dependencies": ["."],
  "graphs": {
    "agent": "./src/graph.ts"
  },
  "env": ".env"
}""",
            ".env.example": """# OpenAI Configuration
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-4

# LangSmith Configuration (required for LangSmith Deployments deployment)
LANGSMITH_API_KEY=your_langsmith_key_here

# Agent Configuration
PORT=8000
NODE_ENV=development

# Add your API keys here
# COINGECKO_API_KEY=
# ALCHEMY_API_KEY=
# WEATHER_API_KEY=""",
            ".gitignore": """node_modules/
dist/
.env
*.log
.DS_Store""",
            "src/graph.ts": """import { StateGraph, END } from "@langchain/langgraph";
import { ChatOpenAI } from "@langchain/openai";

// Define the agent state
interface AgentState {
  input: string;
  output?: string;
  error?: string;
}

// Main agent logic
async function processRequest(state: AgentState): Promise<Partial<AgentState>> {
  try {
    const llm = new ChatOpenAI({
      modelName: process.env.OPENAI_MODEL || "gpt-4",
      temperature: 0.7
    });
    
    // TODO: Implement your agent logic here
    const response = await llm.invoke(state.input);
    
    return { output: response.content as string };
  } catch (error) {
    return { error: (error as Error).message };
  }
}

// Build the graph
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
""",
            "README.md": """# {agent_name}

{description}

## Setup

1. Install dependencies:
```bash
npm install
```

2. Copy `.env.example` to `.env` and add your API keys:
```bash
cp .env.example .env
```

3. Run development server:
```bash
npm run dev
```

## Testing

Test the agent API:
```bash
curl -X POST http://localhost:8000/invoke \\
  -H "Content-Type: application/json" \\
  -d '{{"input": "test query"}}'
```

## Deployment

Deploy to LangSmith Deployments:
1. Push your repo to GitHub
2. Create a deployment in the LangSmith Deployments UI
3. Set environment variables and deploy

## Requirements

- Node.js 18+
- OpenAI API key
- LangGraph CLI (optional, for local dev)

## License

MIT
"""
        }
    },
    "python": {
        "name": "Python Agent",
        "base": "langgraph-quick-start-py",
        "files": {
            "requirements.txt": """langgraph>=0.0.19
langchain-openai>=0.0.19
python-dotenv>=1.0.0
fastapi>=0.100.0
uvicorn>=0.23.0""",
            "langgraph.json": """{
  "agent_id": "{agent_name}",
  "python_version": "3.11",
  "dependencies": ["."],
  "graphs": {
    "agent": "./src/graph.py"
  },
  "env": ".env"
}""",
            ".env.example": """# OpenAI Configuration
OPENAI_API_KEY=your_openai_key_here
OPENAI_MODEL=gpt-4

# LangSmith Configuration (required for LangSmith Deployments deployment)
LANGSMITH_API_KEY=your_langsmith_key_here

# Agent Configuration
PORT=8000

# Add your API keys here
# COINGECKO_API_KEY=
# ALCHEMY_API_KEY=
# WEATHER_API_KEY=""",
            ".gitignore": """__pycache__/
*.py[cod]
.env
*.log
.DS_Store
venv/""",
            "src/__init__.py": "",
            "src/graph.py": """from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from typing import TypedDict, Optional
import os

# Define the agent state
class AgentState(TypedDict):
    input: str
    output: Optional[str]
    error: Optional[str]

# Main agent logic
async def process_request(state: AgentState) -> AgentState:
    try:
        llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4"),
            temperature=0.7
        )
        
        # TODO: Implement your agent logic here
        response = await llm.ainvoke(state["input"])
        
        return {"output": response.content}
    except Exception as e:
        return {"error": str(e)}

# Build the graph
workflow = StateGraph(AgentState)
workflow.add_node("process", process_request)
workflow.set_entry_point("process")
workflow.add_edge("process", END)

agent = workflow.compile()
""",
            "README.md": """# {agent_name}

{description}

## Setup

1. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy `.env.example` to `.env` and add your API keys:
```bash
cp .env.example .env
```

4. Run development server:
```bash
langgraph dev
```

## Testing

Test the agent API:
```bash
curl -X POST http://localhost:8000/invoke \\
  -H "Content-Type: application/json" \\
  -d '{{"input": "test query"}}'
```

## Deployment

Deploy to LangSmith Deployments:
1. Push your repo to GitHub
2. Create a deployment in the LangSmith Deployments UI
3. Set environment variables and deploy

## Requirements

- Python 3.11+
- OpenAI API key
- LangGraph CLI (optional, for local dev)

## License

MIT
"""
        }
    }
}


def create_agent(agent_name: str, description: str, template: str, output_dir: str):
    """Create a new Warden agent from template."""
    
    # Validate template
    if template not in TEMPLATES:
        print(f"Error: Unknown template '{template}'")
        print(f"Available templates: {', '.join(TEMPLATES.keys())}")
        sys.exit(1)
    
    # Create output directory
    agent_dir = Path(output_dir) / agent_name
    if agent_dir.exists():
        print(f"Error: Directory '{agent_dir}' already exists")
        sys.exit(1)
    
    agent_dir.mkdir(parents=True)
    
    # Get template
    template_data = TEMPLATES[template]
    
    print(f"Creating {template_data['name']}...")
    print(f"Name: {agent_name}")
    print(f"Description: {description}")
    print(f"Location: {agent_dir}")
    print()
    
    # Create files
    for filename, content in template_data["files"].items():
        filepath = agent_dir / filename
        
        # Create parent directories if needed
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Format content with variables
        formatted_content = content.format(
            agent_name=agent_name,
            description=description
        )
        
        # Write file
        filepath.write_text(formatted_content)
        print(f"✓ Created {filename}")
    
    print()
    print("Agent created successfully!")
    print()
    print("Next steps:")
    print(f"1. cd {agent_dir}")
    
    if template == "typescript":
        print("2. npm install")
    else:
        print("2. python -m venv venv && source venv/bin/activate")
        print("3. pip install -r requirements.txt")
    
    print(f"{3 if template == 'typescript' else 4}. Copy .env.example to .env and add your API keys")
    print(f"{4 if template == 'typescript' else 5}. npm run dev (or langgraph dev)")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Initialize a new Warden Protocol agent"
    )
    parser.add_argument(
        "name",
        help="Agent name (e.g., 'my-warden-agent')"
    )
    parser.add_argument(
        "--description",
        "-d",
        default="A Warden Protocol agent",
        help="Agent description"
    )
    parser.add_argument(
        "--template",
        "-t",
        choices=list(TEMPLATES.keys()),
        default="typescript",
        help="Template to use (default: typescript)"
    )
    parser.add_argument(
        "--output",
        "-o",
        default=".",
        help="Output directory (default: current directory)"
    )
    
    args = parser.parse_args()
    
    create_agent(
        agent_name=args.name,
        description=args.description,
        template=args.template,
        output_dir=args.output
    )


if __name__ == "__main__":
    main()
