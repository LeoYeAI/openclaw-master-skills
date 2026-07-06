# Pharmacoeconomic Evaluation Skill

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.8+-blue)

Comprehensive pharmacoeconomic evaluation skill for AI agents, providing guidance and tools for cost-effectiveness analysis, cost-utility analysis, budget impact analysis, and more.

## Features

- **Cost-Effectiveness Analysis (CEA)**: ICER calculation, incremental analysis
- **Cost-Utility Analysis (CUA)**: QALY calculation, utility measurement
- **Budget Impact Analysis (BIA)**: Multi-scenario budget modeling
- **Sensitivity Analysis**: Deterministic and probabilistic methods
- **Decision Analytic Models**: Markov, decision tree, DES, PSM
- **Chinese Guidelines**: Follows China Pharmacoeconomic Evaluation Guidelines (2023)

## Installation

```bash
# For Claude Code / CodeBuddy users
npx skills add your-username/pharmacoeconomic-evaluation
```

Or manually copy the `pharmacoeconomic-evaluation` folder to your skills directory:
- CodeBuddy: `~/.codebuddy/skills/`
- WorkBuddy: `~/.workbuddy/skills/`

## Usage

This skill provides comprehensive guidance for conducting pharmacoeconomic evaluations:

### Basic Analysis Workflow

1. **Define Research Framework**: Determine perspective, time horizon, evaluation type
2. **Identify Costs**: Direct medical, direct non-medical, indirect costs
3. **Measure Effects/Utilities**: Clinical outcomes, QALYs
4. **Build Decision Model**: Markov, decision tree, or DES
5. **Calculate Key Metrics**: ICER, QALYs, Net Benefit
6. **Sensitivity Analysis**: One-way and probabilistic methods
7. **Report Results**: Follow CHEERS 2022 guidelines

### Python Scripts

```python
# ICER Calculation
from cost_effectiveness_analysis import calculate_icere

result = calculate_icere(
    cost_intervention=50000,
    effect_intervention=5.2,  # QALYs
    cost_control=30000,
    effect_control=4.5,
    threshold=120000  # 1x GDP per QALY
)

# QALY Calculation
from cost_effectiveness_analysis import calculate_qaly

qalys = calculate_qaly(
    life_years=10,
    utility_scores=[0.8, 0.75, 0.7, 0.65, 0.6],
    discount_rate=0.03
)

# Budget Impact Analysis
from budget_impact_analysis import BudgetImpactModel

model = BudgetImpactModel(
    target_population=100000,
    treatment_cost_new=15000,
    treatment_cost_old=10000,
    horizon_years=5,
    uptake_rate=0.2
)
```

## Skill Structure

```
pharmacoeconomic-evaluation/
├── SKILL.md                    # Main skill definition
├── README.md                   # This file
├── scripts/
│   ├── cost_effectiveness_analysis.py   # CEA calculations
│   ├── budget_impact_analysis.py        # BIA model
│   ├── monte_carlo_simulation.py        # PSA simulations
│   └── example.py                       # Parameter examples
└── references/
    ├── china_guidelines.md      # China HTA guidelines
    ├── model_methods.md         # Decision model methods
    └── api_reference.md         # API documentation
```

## Key Parameters (China Context)

| Parameter | Value | Source |
|-----------|-------|--------|
| Discount Rate | 3%-5% | China Guidelines 2023 |
| Threshold | 1-3x GDP/QALY | China Guidelines 2023 |
| Perspective | Societal | Recommended |

## License

MIT License

## Contributing

Contributions welcome! Please submit issues and pull requests.
