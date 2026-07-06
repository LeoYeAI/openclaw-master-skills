# Quick Start Guide

Get up and running with eval-skills in 5 minutes.

## Prerequisites

- **Node.js** >= 18.0.0
- **pnpm** >= 8.0.0
- **Python 3** (for subprocess-based skills)

## 1. Install

```bash
git clone https://github.com/eval-skills/eval-skills.git
cd eval-skills
pnpm install
pnpm build
```

## 2. Initialize a Project

```bash
eval-skills init
```

This creates:
- `eval-skills.config.yaml` — global configuration
- `skills/` — directory for your skills
- `benchmarks/` — directory for custom benchmarks
- `reports/` — output directory for reports

## 3. Run Your First Evaluation

Evaluate the built-in calculator example against the coding-easy benchmark:

```bash
eval-skills eval \
  --skills ./examples/skills/calculator/skill.json \
  --benchmark coding-easy \
  --format json markdown
```

You should see output like:

```
✔ Evaluation complete! 1 skill(s) evaluated.
  calculator — CR: 100.0% | ER: 0.0% | Score: 0.999
```

## 4. View Reports

```bash
# Reports are saved to ./reports/ by default
cat ./reports/eval-result-*.md
```

## 5. Create Your Own Skill

```bash
# Generate a Python subprocess skill skeleton
eval-skills create --name my_skill --from-template python_script

# Or an HTTP skill
eval-skills create --name my_api --from-template http_request
```

This generates:
```
skills/my_skill/
├── skill.json          # Skill metadata
├── adapter.config.json # Adapter configuration
├── skill.py            # Python implementation (for python_script template)
└── tests/
    └── basic.eval.json # Example evaluation tasks
```

## 6. Search Registered Skills

```bash
eval-skills find --query "calculator" --skills-dir ./examples/skills/
eval-skills find --tag math --adapter subprocess
```

## 7. End-to-End Pipeline

```bash
eval-skills run \
  --skills-dir ./examples/skills/ \
  --benchmark coding-easy \
  --top-k 3
```

This runs: **find** -> **eval** -> **select** -> **report** in one command.

## Next Steps

- [Create a Custom Skill](./create-skill.md)
- [Create a Custom Benchmark](./custom-benchmark.md)
- [CI/CD Integration](./ci-cd-integration.md)
