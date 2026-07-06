---
name: pharmacoeconomic-evaluation
description: This skill provides comprehensive guidance and tools for conducting pharmacoeconomic evaluations including cost-effectiveness analysis (CEA), cost-utility analysis (CUA), cost-benefit analysis (CBA), budget impact analysis (BIA), sensitivity analysis, and decision-analytic model construction (Markov, decision tree, DES, PSM). Follows ISPOR Good Practices for Outcomes Research Reports. Use this skill for HTA projects, drug pricing, reimbursement decisions, and health economic research.
---

# Pharmacoeconomic Evaluation Skill

## Overview

This skill provides comprehensive guidance for conducting pharmacoeconomic evaluations, including cost-effectiveness analysis, cost-utility analysis, cost-benefit analysis, budget impact analysis, sensitivity analysis, and model construction. Following the Chinese Pharmacoeconomic Evaluation Guidelines (2023 Edition), it provides complete workflows, calculation tools, and reference materials for economic evaluation of healthcare interventions.

## Evaluation Types

Choose the appropriate evaluation type based on research objectives and data characteristics:

- **Cost-Effectiveness Analysis (CEA)**: Use when intervention effect can be measured by a single clinical indicator (e.g., life years, survival rate)
- **Cost-Utility Analysis (CUA)**: Use when both quality and quantity of life need to be considered; outcome measure is QALYs
- **Cost-Benefit Analysis (CBA)**: Use when intervention effects can be expressed in monetary terms
- **Cost-Minimization Analysis (CMA)**: Use when two interventions have proven equivalent efficacy; only compare costs
- **Budget Impact Analysis (BIA)**: Use to assess financial impact of new drugs or technologies on healthcare insurance funds

## Core Workflow

### Step 1: Define Research Framework

1. Define research question
   - Identify target disease and population
   - Determine intervention and comparator
   - Set perspective (recommended: societal)

2. Select evaluation type
   - Choose CEA, CUA, CBA, or CMA based on outcome measure
   - Consider discounting for long-term studies (both costs and outcomes)
   - Recommended discount rate: 3.5%

3. Determine time horizon
   - Chronic diseases: lifetime or sufficiently long
   - Acute diseases: short-term follow-up (1-3 years)
   - Budget impact analysis: typically 3-5 years

### Step 2: Identify and Measure Costs

Identify costs following Chinese Pharmacoeconomic Evaluation Guidelines:

**Direct Medical Costs**
- Medication costs
- Outpatient costs
- Inpatient costs
- Diagnostic and test costs
- Surgical treatment costs
- Adverse event treatment costs

**Direct Non-Medical Costs**
- Transportation
- Accommodation
- Nutritional support
- Unprofessional caregiving

**Indirect Costs**
- Productivity loss (premature death or sick leave)
- Caregiver burden

**Intangible Costs**
- Pain, anxiety, quality of life reduction not included in monetary costs; considered in utility analysis

Cost Data Sources:
- Hospital Information Systems
- Insurance Databases
- Epidemiological Studies
- Literature Review
- Questionnaire Surveys

### Step 3: Measure Effects/Utilities

**Effect Measure Selection**
- Survival indicators: Life Years (LY), Survival Rate
- Disease-specific indicators: Event-free survival, Symptom improvement
- Others: Complication rate, Hospitalization frequency

**Utility Measurement (Recommended Indirect Methods)**
- EQ-5D (EuroQol Five-Dimensional Questionnaire)
- SF-6D (Based on SF-36)
- QWB (Quality of Well-Being Index)

Utility Value Source Priority:
1. Primary data from target population (best)
2. Published Chinese population utility values
3. Data from other countries (requires adjustment)

### Step 4: Build Decision Analytic Models

Select appropriate model type based on research characteristics:

#### Decision Tree Model
- **Scenarios**: Short-term, single decision, clear event sequence
- **Advantages**: Intuitive, easy to understand, suitable for analyzing decision processes
- **Steps**:
  1. Define decision nodes, chance nodes, terminal nodes
  2. Assign probabilities to each chance node (sum to 1)
  3. Assign costs and effects to each terminal node
  4. Roll back to calculate expected values
  5. Compare decision options

#### Markov Model
- **Usage scenario**: Chronic diseases, long-term follow-up, recurrent events
- **Advantages**: Can handle cyclical state transitions, clear structure
- **Steps**:
  1. Define health states (e.g., healthy, mild, moderate, severe, death)
  2. Build transition matrix (describe state-to-state transition probabilities)
  3. Estimate transition probabilities (from incidence, survival curves, or literature)
  4. Assign cycle costs and utilities to each state
  5. Set cycle length (typically 1 year) and model time horizon
  6. Run Markov simulation

#### Discrete Event Simulation (DES)
- **Scenarios**: Large individual variation, irregular event timing, resource constraints
- **Advantages**: Most flexible, can simulate individual paths, precise time-dependent modeling
- **步骤**:
  1. Define entities (patients) and their attributes
  2. Define possible event types
  3. Establish event scheduling mechanism
  4. Run simulation
  5. Aggregate results

#### Partitioned Survival Model (PSM)
- **Scenarios**: Oncology research, based on survival curves
- **Advantages**: Directly based on survival data, reasonable extrapolation
- **Steps**:
  1. Obtain PFS and OS survival curves
  2. Fit parametric distributions (exponential, Weibull, etc.)
  3. Extrapolate to model time horizon
  4. Calculate population distribution across partitions
  5. Accumulate costs and utilities

See `references/model_methods.md` for detailed modeling methods.

### Step 5: Calculate Key Metrics

Use calculation tools in `scripts/`:

#### Incremental Cost-Effectiveness Ratio (ICER)
Use `calculate_icere()` from `scripts/cost_effectiveness_analysis.py`:

```python
from cost_effectiveness_analysis import calculate_icere

result = calculate_icere(
    cost_intervention,  # Intervention group cost
    effect_intervention,  # Intervention group effect (e.g., QALYs)
    cost_control,  # Control group cost
    effect_control,  # Control group effect
    threshold=30000  # Threshold (30KUSD for US & UK, and close to 2x GDP per QALY of China)
)
```

ICER Formula:
\[ ICER = \frac{C_A - C_B}{E_A - E_B} = \frac{\Delta C}{\Delta E} \]

#### Quality-Adjusted Life Years (QALYs)
Use `calculate_qaly()` from `scripts/cost_effectiveness_analysis.py`:

```python
from cost_effectiveness_analysis import calculate_qaly

qalys = calculate_qaly(
    life_years=10,  # Life years
    utility_scores=np.array([...]),  # Utility scores for each period
    discount_rate=0.03  # Discount rate
)
```

QALY Formula:
\[ QALY = \sum_{t=1}^{T} U_t \times \frac{1}{(1+r)^{t-1}} \]

#### Net Benefit
\[ NB = \lambda \times E - C \]

Where:
- NB = Net Benefit
- λ = Willingness-to-pay threshold
- E = Effect
- C = Cost

#### Budget Impact Analysis
Use `BudgetImpactModel` from `scripts/budget_impact_analysis.py`:

```python
from budget_impact_analysis import BudgetImpactModel

model = BudgetImpactModel(
    target_population=100000,
    treatment_cost_new=15000,
    treatment_cost_old=10000,
    horizon_years=5,
    uptake_rate=0.2,
    discount_rate=0.03
)

# Calculate multi-scenario budget impact
scenarios = {
    "Base Case": [0.2, 0.3, 0.4, 0.5, 0.6],
    "Optimistic": [0.3, 0.5, 0.7, 0.8, 0.9],
    "Conservative": [0.1, 0.15, 0.2, 0.25, 0.3]
}

results = model.compare_scenarios(
    scenarios,
    population_growth_rate=0.02,
    treatment_cost_inflation=0.01
)
```

### Step 6: Conduct Sensitivity Analysis

#### One-Way Sensitivity Analysis
Use `deterministic_sensitivity_analysis()` from `scripts/cost_effectiveness_analysis.py`:

```python
from cost_effectiveness_analysis import deterministic_sensitivity_analysis

# Define parameter ranges
param_ranges = {
    'drug_cost': (10000, 20000),
    'hospital_cost': (5000, 15000),
    'effectiveness': (0.8, 1.2)
}

# Run sensitivity analysis
results_df = deterministic_sensitivity_analysis(
    base_params=base_parameters,
    param_ranges=param_ranges,
    outcome_func=outcome_function
)
```

**Tornado Plot Data**: Use `tornado_plot_data()` function

#### Probabilistic Sensitivity Analysis (PSA)
Use `MonteCarloSimulator` from `scripts/monte_carlo_simulation.py`:

```python
from monte_carlo_simulation import MonteCarloSimulator

# Create simulator
simulator = MonteCarloSimulator(n_simulations=10000, seed=42)

# Define parameter distributions
parameters = {
    'cost': {
        'distribution': 'gamma',
        'params': (2, 15000),  # shape, scale
        'min_value': 0
    },
    'effect': {
        'distribution': 'beta',
        'params': (5, 3),  # alpha, beta
        'min_value': 0,
        'max_value': 10
    }
}

# Run PSA
results_df = simulator.probabilistic_sensitivity_analysis(
    parameters=parameters,
    outcome_func=outcome_function,
    threshold=120000
)
```

**Generate CEAC**: Use `generate_ceac()` function

**Value of Information (VOI)**: Use `value_of_information_analysis()` function

### Step 7: Interpret and Report Results

#### Willingness-to-Pay Threshold (Reference)
- 1x GDP/QALY: ~¥120,000
- 2x GDP/QALY: ~¥240,000
- 3x GDP/QALY: ~¥360,000

#### Interpretation
- **ICER ≤ Threshold**: Cost-effective
- **ICER > Threshold**: Not cost-effective
- **Strict Dominance**: Lower cost and better effect
- **Strict Disadvantage**: Higher cost and worse effect

#### Reporting Requirements
Follow CHEERS 2022 and Chinese Pharmacoeconomic Evaluation Guidelines:
1. Clearly describe research design and methods
2. Report baseline analysis results
3. Provide sensitivity analysis results (one-way and probabilistic)
4. Report confidence intervals
5. Discuss limitations and generalizability
6. Clearly state funding sources and potential conflicts of interest

See `references/guidelines.md` for detailed guidelines.

## Scripts Guide

### cost_effectiveness_analysis.py
Core functions: Cost-effectiveness analysis, ICER calculation, QALY calculation, deterministic sensitivity analysis

Main functions:
- `calculate_icere()`: Calculate ICER
- `calculate_qaly()`: Calculate QALYs
- `calculate_ceac()`: Calculate Cost-Effectiveness Acceptability Curve
- `deterministic_sensitivity_analysis()`: One-way sensitivity analysis
- `tornado_plot_data()`: Prepare tornado plot data
- `markov_model_transition()`: Markov model simulation
- `discount_costs()`: Cost discounting

### budget_impact_analysis.py
Core functions: Budget impact analysis model

Main classes and methods:
- `BudgetImpactModel`: Budget impact analysis model
  - `calculate_budget_impact_scenario()`: Calculate single scenario budget impact
  - `compare_scenarios()`: Compare multiple scenarios
  - `sensitivity_analysis()`: Sensitivity analysis
  - `generate_summary()`: Generate analysis summary
- `calculate_incremental_budget_impact()`: Calculate incremental budget impact
- `budget_impact_report()`: Generate budget impact report

### monte_carlo_simulation.py
Core functions: Monte Carlo simulation, probabilistic sensitivity analysis, value of information analysis

Main classes and methods:
- `MonteCarloSimulator`: Monte Carlo simulator
  - `generate_samples()`: Generate samples from specified distribution
  - `probabilistic_sensitivity_analysis()`: Run PSA
  - `generate_ceac()`: Generate CEAC
  - `value_of_information_analysis()`: VOI analysis
  - `scatter_plot_data()`: Prepare cost-effectiveness scatter plot data

## References Guide

### guidelines.md
Summary of key content from ISPOR Good Practices, including:
- Evaluation framework and perspective
- Cost identification and measurement
- Effect/utility measurement
- Model construction methods
- Discounting principles
- Sensitivity analysis requirements
- Result presentation and reporting standards
- Common calculation formulas

**Use case**: Query specific requirements, standards, and methods for Chinese pharmacoeconomic evaluation

### model_methods.md
Detailed decision analytic model construction methods, including:
- Markov model (basic concepts, transition matrix, probability estimation)
- Decision tree model (structure, probability assignment, rollback calculation)
- Discrete event simulation (core elements, advantages/disadvantages)
- Partitioned survival model (survival curve fitting)
- Model comparison and selection
- Modeling best practices

**Use case**: Learn specific modeling methods, build decision analytic models

## Common Task Scenarios

### Scenario 1: Conduct Cost-Effectiveness Analysis for New Drug
1. Determine research perspective (societal)
2. Identify direct medical and non-medical costs
3. Collect clinical trial data for effect measures (survival, QALYs)
4. Build Markov model to simulate disease progression
5. Calculate ICER and compare with threshold
6. Conduct one-way and probabilistic sensitivity analysis
7. Write report following CHEERS standards

### Scenario 2: Budget Impact Analysis
1. Determine target population size
2. Obtain costs for new drug and comparator
3. Set uptake rate scenarios (base, optimistic, conservative)
4. Use `BudgetImpactModel` to calculate budget impact for each scenario
5. Conduct sensitivity analysis
6. Generate budget impact report

### Scenario 3: Model Building and Validation
1. Select model type based on disease characteristics
2. Learn modeling methods from `references/model_methods.md`
3. Estimate model parameters from literature or clinical trials
4. Validate model (internal and external validation)
5. Run baseline analysis
6. Conduct sensitivity analysis to verify model stability

### Scenario 4: Probabilistic Sensitivity Analysis
1. Specify probability distributions for each key parameter
2. Run 10,000+ simulations using `MonteCarloSimulator`
3. Generate cost-effectiveness scatter plot
4. Generate Cost-Effectiveness Acceptability Curve (CEAC)
5. Conduct Value of Information (VOI) analysis
6. Report cost-effectiveness probability and confidence intervals

## Parameter Management Best Practices

### Parameter Organization
Organize parameters by category:
- **Research Framework Parameters**: Perspective, time horizon, discount rate, threshold
- **Model Structure Parameters**: Health states, initial distribution
- **Transition Probability Parameters**: State-to-state transition probabilities
- **Cost Parameters**: Annual costs by state
- **Utility Parameters**: Utility values by state
- **Sensitivity Analysis Parameters**: Parameter ranges and probability distributions
- **Simulation Parameters**: Number of simulations, random seed, etc.

### Parameter Source Documentation
Each parameter value must have a clear data source:
- **Literature Citation**: Author, journal, year, pages
- **Database**: Database name, version, access date
- **Guidelines/Standards**: Guideline name, version, issuing organization
- **Expert Opinion**: Expert source and judgment basis
- **Research Assumption**: Rationale for assumption

### Example Code Format
```python
# ========== Parameter Category Title ==========
PARAMETER_NAME = {
    'parameter_key': value,  # Source: Detailed source description
    'another_key': value,    # Source: Reference [Author, Journal, Year]
}
```

See `scripts/example.py` for complete parameter organization format.

## Important Notes

1. **Follow Chinese Guidelines**: Ensure research methods meet requirements of Chinese Pharmacoeconomic Evaluation Guidelines (2023)

2. **Transparency**: Clearly describe all assumptions, data sources, and calculation methods

3. **Parameter Source Documentation**: All parameter values must cite sources for traceability and verification

4. **Discounting**: Both costs and outcomes need discounting; recommended rate is 3.5%

5. **Sensitivity Analysis**: Conduct sufficient sensitivity analysis to evaluate uncertainty

6. **Model Validation**: Validate model internally; conduct external validation if possible

7. **Reporting Standards**: Follow CHEERS 2022 reporting standards

8. **Threshold**: Clearly state the threshold used and its basis (Reference: 1-3x GDP/QALY)

9. **Time Horizon**: Select sufficiently long time horizon to capture all relevant costs and outcomes

10. **Cost Measurement**: Avoid using payment prices (reimbursed prices); use actual costs or standardized charges

11. **Utility Measurement**: Prioritize Chinese population utility values; note applicability of measurement tools

12. **Parameter Organization**: Reference format in `scripts/example.py`, organize parameters neatly and document sources in detail
