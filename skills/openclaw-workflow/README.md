# OpenClaw Workflow

🔀 Deterministic Workflow Engine - Run YAML Automation Pipelines

## Overview

OpenClaw Workflow is a deterministic workflow engine that conforms to the OpenClaw / AgentSkills specification. It executes 100% deterministic logic via YAML playbooks without compromising OpenClaw's flexibility.

## Features

- **Conditionals** — If-Else logic
- **Loops** — ForEach / Times iteration
- **Script Execution** — Shell / Python scripts
- **LLM Calls** — Direct language model invocation
- **Agent Calls** — Invoke OpenClaw Agent
- **Subagent** — Create parallel sub-agents for task execution
- **HTTP Requests** — Send REST API requests
- **Messaging** — iMessage / Telegram / Discord notifications

## Quick Start

```bash
# Install dependencies
pip install -r scripts/requirements.txt

# Run a workflow
python3 scripts/openclaw_workflow.py execute <workflow.yaml>

# Validate syntax
python3 scripts/openclaw_workflow.py validate <workflow.yaml>

# List available workflows
python3 scripts/openclaw_workflow.py list
```

## Documentation

For detailed usage instructions, see [SKILL.md](./SKILL.md)

## License

This project is licensed under **CC BY-NC 4.0** — Attribution-NonCommercial

See [LICENSE](./LICENSE) for details

## Author

OpenClaw Team
