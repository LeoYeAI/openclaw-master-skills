---
name: adme-property-predictor
description: Predict ADME (Absorption, Distribution, Metabolism, Excretion) properties 
  for drug candidates using cheminformatics models and molecular descriptors. 
  Evaluates drug-likeness, bioavailability, and pharmacokinetic profile to guide 
  lead optimization and candidate selection in drug discovery.
allowed-tools: [Read, Write, Bash, Edit]
license: MIT
metadata:
    skill-author: AIPOCH
---

# ADME Property Predictor

## Overview

Comprehensive pharmacokinetic prediction tool that assesses drug-likeness and ADME properties of small molecules using validated cheminformatics models, molecular descriptors, and structure-property relationships.

**Key Capabilities:**
- **Multi-Property Prediction**: Absorption, Distribution, Metabolism, Excretion
- **Drug-Likeness Scoring**: Lipinski's Rule of 5, Veber rules, QED score
- **Batch Processing**: Analyze compound libraries efficiently
- **Structure-Based Insights**: Identify liability hotspots and optimization opportunities
- **Comparative Analysis**: Rank candidates by predicted PK profile

## When to Use

**✅ Use this skill when:**
- Screening compound libraries for drug-like properties in early discovery
- Prioritizing lead compounds for advancement based on predicted PK
- Identifying ADME liabilities requiring structural optimization
- Comparing analogs to select candidates with optimal ADME profiles
- Filtering virtual screening hits before synthesis
- Generating ADME data for regulatory pre-submission packages
- Teaching pharmacokinetics and drug design principles

**❌ Do NOT use when:**
- Exact PK parameters needed for dosing → Use experimental PK studies
- Biologics (antibodies, proteins) → Use `antibody-pk-predictor`
- Natural products with complex structures → Models trained on synthetic small molecules
- Prodrugs requiring metabolic activation → Use `prodrug-activation-predictor`
- Prediction for clinical dosing decisions → **CRITICAL**: Experimental validation required
- Assessing toxicity or safety → Use `toxicity-structure-alert` or `admetox-predictor`

**Related Skills:**
- **上游**: `chemical-structure-converter` (structure preparation), `lipinski-rule-filter` (rule-based filtering)
- **下游**: `drug-candidate-evaluator` (integrated scoring), `molecular-dynamics-sim` (detailed binding)

## Integration with Other Skills

**Upstream Skills:**
- `chemical-structure-converter`: Convert between SMILES, InChI, MOL formats
- `lipinski-rule-filter`: Initial rule-based drug-likeness screening
- `chemical-structure-converter`: Generate 3D conformers for structure-based predictions
- `smiles-de-salter`: Remove salt counterions before analysis

**Downstream Skills:**
- `drug-candidate-evaluator`: Multi-parameter optimization including ADME
- `toxicity-structure-alert`: Assess safety alongside ADME
- `target-novelty-scorer`: Evaluate target uniqueness for selected candidates
- `biotech-pitch-deck-narrative`: Create investor materials with PK data

**Complete Workflow:**
```
Chemical Structure Converter (prepare structures) → 
  Lipinski Rule Filter (initial filtering) → 
    ADME Property Predictor (this skill, detailed PK) → 
      Drug Candidate Evaluator (integrated scoring) → 
        Toxicity Structure Alert (safety check)
```

## Core Capabilities

### 1. Absorption (A) Prediction

Predict intestinal absorption, solubility, and permeability:

```python
from scripts.adme_predictor import ADMEPredictor

predictor = ADMEPredictor()

# Predict absorption properties
absorption = predictor.predict_absorption(
    smiles="CC(=O)Oc1ccccc1C(=O)O",  # Aspirin
    properties=["all"]  # or specific: ["hia", "caco2", "solubility"]
)

print(absorption.summary())
```

**Predicted Properties:**
| Property | Model | Units | Interpretation |
|----------|-------|-------|----------------|
| **HIA** | ML + physicochemical | % | Human intestinal absorption; >80% good |
| **Caco-2** | QSPR | 10⁻⁶ cm/s | Permeability; >70 high, <25 low |
| **Solubility** | QSPR | mg/mL | Aqueous solubility; >0.1 mg/mL acceptable |
| **LogS** | QSPR | unitless | Intrinsic solubility; >-4 acceptable |
| **Lipinski Pass** | Rule-based | boolean | Passes all 5 rules |
| **Veber Pass** | Rule-based | boolean | PSA <140, rotatable bonds <10 |

**Best Practices:**
- ✅ Consider HIA and solubility together (high HIA but low solubility = dissolution-limited)
- ✅ Caco-2 good for oral absorption prediction; poor for BBB penetration
- ✅ Use both rule-based (Lipinski) and ML-based predictions for consensus
- ✅ Check solubility at physiological pH (not just intrinsic)

**Common Issues and Solutions:**

**Issue: Lipinski pass but poor solubility**
- Symptom: "Passes Rule of 5 but LogS = -5"
- Solution: Lipinski checks MW and LogP, not solubility directly; use explicit solubility prediction

**Issue: Caco-2 predicts high absorption but HIA low**
- Symptom: "Caco-2 = 85 (high) but HIA = 60%"
- Solution: Models have different training sets; Caco-2 is in vitro, HIA in vivo; HIA generally more reliable

### 2. Distribution (D) Prediction

Predict tissue distribution, protein binding, and brain penetration:

```python
# Predict distribution properties
distribution = predictor.predict_distribution(
    smiles="CC(=O)Oc1ccccc1C(=O)O",
    properties=["vd", "ppb", "bbb"]
)

# Access specific predictions
vd = distribution.volume_of_distribution
bbb = distribution.blood_brain_barrier
ppb = distribution.plasma_protein_binding
```

**Predicted Properties:**
| Property | Model | Units | Interpretation |
|----------|-------|-------|----------------|
| **Vd** | QSPR | L/kg | Volume of distribution; 0.1-10 typical |
| **PPB** | ML | % | Plasma protein binding; >90% high, <50% low |
| **BBB** | LogBB | unitless | Brain penetration; >0.3 penetrant |
| **fu** | Calculated | fraction | Free (unbound) fraction; 1 - PPB/100 |

**Best Practices:**
- ✅ High PPB (>90%) may require higher doses but longer half-life
- ✅ Low Vd (<0.3) = mainly in plasma; high Vd (>3) = extensive tissue distribution
- ✅ BBB penetration critical for CNS drugs; avoid for peripherally-acting drugs
- ✅ fu (free fraction) drives pharmacological activity, not total concentration

**Common Issues and Solutions:**

**Issue: BBB predictions unreliable for certain chemotypes**
- Symptom: "BBB model gives conflicting predictions for peptides"
- Solution: Models trained on small molecules; use specialized BBB predictors for peptides, macrocycles

**Issue: PPB overestimated for acidic drugs**
- Symptom: "PPB predicted 95% but experimental is 70%"
- Solution: Some models biased toward neutral/basic compounds; check model training set overlap

### 3. Metabolism (M) Prediction

Predict metabolic stability, CYP interactions, and liability sites:

```python
# Predict metabolism properties
metabolism = predictor.predict_metabolism(
    smiles="CC(=O)Oc1ccccc1C(=O)O",
    include_site_prediction=True
)

# Check CYP interactions
cyp_profile = metabolism.cyp_profile
stability = metabolism.metabolic_stability
```

**Predicted Properties:**
| Property | Model | Output | Interpretation |
|----------|-------|--------|----------------|
| **CYP Inhibition** | ML | IC50 or class | Potential DDI; <1 μM high risk |
| **CYP Substrate** | Classification | Boolean/Probability | Metabolized by specific CYP |
| **Stability** | ML | T1/2 or class | Microsomal/ hepatocyte stability |
| **Liability Sites** | Reactivity models | Atom indices | Soft spots for metabolism |
| **MAO Substrate** | Classification | Boolean | Monoamine oxidase substrate |

**Best Practices:**
- ✅ Screen for CYP3A4 inhibition early (most common DDI)
- ✅ Check if compound is CYP substrate (for polymorphism concerns)
- ✅ Identify metabolic hotspots for structural blocking
- ✅ Consider species differences (human vs rodent metabolism)

**Common Issues and Solutions:**

**Issue: False negatives for time-dependent inhibition (TDI)**
- Symptom: "No CYP inhibition predicted but TDI observed experimentally"
- Solution: Standard models predict reversible inhibition; use specialized TDI predictors

**Issue: Metabolic site prediction shows multiple hotspots**
- Symptom: "5 different atoms flagged as metabolic liabilities"
- Solution: Prioritize by reactivity score; consider blocking highest-risk site first

### 4. Excretion (E) Prediction

Predict clearance routes and elimination kinetics:

```python
# Predict excretion properties
excretion = predictor.predict_excretion(
    smiles="CC(=O)Oc1ccccc1C(=O)O",
    properties=["clearance", "half_life", "route"]
)

# Access predictions
clearance = excretion.clearance_ml_min_kg
t12 = excretion.half_life_hours
route = excretion.primary_route
```

**Predicted Properties:**
| Property | Model | Units | Interpretation |
|----------|-------|-------|----------------|
| **CL** | QSPR | mL/min/kg | Clearance; <5 low, 5-15 moderate, >15 high |
| **T1/2** | QSPR | hours | Half-life; 2-8h typical for oral drugs |
| **Route** | Classification | renal/biliary/mixed | Primary excretion pathway |
| **LogD** | QSPR | unitless | Distribution coefficient; affects clearance |

**Best Practices:**
- ✅ Half-life determines dosing frequency (T1/2 × 5 = time to steady state)
- ✅ Renal clearance predictable for polar compounds; hepatic less predictable
- ✅ High clearance (>15) may require high doses or prodrug approach
- ✅ Very long T1/2 (>24h) good for adherence but risk accumulation

**Common Issues and Solutions:**

**Issue: Clearance predictions highly variable**
- Symptom: "Same compound, different models give CL = 5 vs 20 mL/min/kg"
- Solution: Allometry-based methods unreliable for novel scaffolds; use average of multiple models

**Issue: Route prediction contradicts structure**
- Symptom: "Highly polar compound predicted biliary, expected renal"
- Solution: Check LogP/LogD; polar compounds (<0) usually renal; neutral/lipophilic (>1) usually hepatic

### 5. Integrated Drug-Likeness Scoring

Overall assessment combining all ADME properties:

```python
# Generate comprehensive drug-likeness score
druglikeness = predictor.calculate_druglikeness(
    smiles="CC(=O)Oc1ccccc1C(=O)O",
    methods=["qed", "muegge", "golden_triangle"]
)

# Multi-parameter optimization
mpo_score = predictor.mpo_score(
    smiles="CC(=O)Oc1ccccc1C(=O)O",
    target_profile={"hia": >80, "bbb": <0.3, "t12": "2-8h"}
)
```

**Scoring Methods:**
| Method | Description | Range | Good Score |
|--------|-------------|-------|------------|
| **QED** | Quantitative Estimation of Drug-likeness | 0-1 | >0.6 |
| **Muegge** | Bioavailability score | 0-6 | >4 |
| **MPO** | Multi-Parameter Optimization | 0-10 | >6 |

**Best Practices:**
- ✅ Use QED as quick overall metric; MPO for property-weighted scoring
- ✅ Don't rely solely on drug-likeness; efficacy and safety equally important
- ✅ Compare to marketed drugs in same class for context
- ✅ Track drug-likeness trends during optimization (should improve)

**Common Issues and Solutions:**

**Issue: Drug-likeness score conflicts with project needs**
- Symptom: "CNS drug has low QED (0.5) because high LogP needed for BBB"
- Solution: Drug-likeness rules biased toward oral drugs; use category-specific models (CNS, oncology, etc.)

### 6. Batch Processing and Library Screening

Analyze compound libraries efficiently:

```python
# Batch process library
results = predictor.batch_predict(
    input_file="library.smi",  # SMILES file
    properties=["all"],
    output_format="csv",
    n_workers=4  # Parallel processing
)

# Filter by criteria
filtered = results.filter(
    lipinski_pass=True,
    hia__gt=80,
    t12__between=(2, 8)
)

# Rank by multi-parameter score
ranked = results.rank(by="mpo_score", ascending=False)
```

**Best Practices:**
- ✅ Process in batches of 1000-10000 for memory efficiency
- ✅ Save intermediate results (crash recovery)
- ✅ Apply filters sequentially (Lipinski first, then detailed ADME)
- ✅ Check property distributions to identify outliers

**Common Issues and Solutions:**

**Issue: Batch processing runs out of memory**
- Symptom: "Killed: Out of memory" with 50K compounds
- Solution: Process in chunks; use generators instead of loading all into RAM

**Issue: Some compounds fail prediction**
- Symptom: "30% of library returns NaN"
- Solution: Check for invalid SMILES, unusual atoms, or molecules outside training set domain

## Complete Workflow Example

**From SMILES to prioritized candidates:**

```bash
# Step 1: Predict ADME for single compound
python scripts/main.py \
  --smiles "CC(=O)Oc1ccccc1C(=O)O" \
  --properties all \
  --output aspirin_adme.json

# Step 2: Batch process compound library
python scripts/main.py \
  --input library.smi \
  --properties absorption,distribution \
  --format csv \
  --output library_adme.csv

# Step 3: Filter and rank
python scripts/main.py \
  --input library_adme.csv \
  --filter "lipinski_pass=True,hia>80" \
  --rank-by qed \
  --top-n 100 \
  --output top_candidates.csv

```

**Python API Usage:**

```python
from scripts.adme_predictor import ADMEPredictor
from scripts.batch_processor import BatchProcessor

# Initialize
predictor = ADMEPredictor()
batch = BatchProcessor()

# Single compound analysis
aspirin = predictor.predict_all("CC(=O)Oc1ccccc1C(=O)O")
print(f"HIA: {aspirin.absorption.hia}%")
print(f"Half-life: {aspirin.excretion.t12} hours")

# Batch screening
results = batch.process(
    input_file="library.smi",
    predictor=predictor,
    properties=["absorption", "distribution"],
    n_workers=4
)

# Filter good candidates
good_candidates = results[
    (results.lipinski_pass == True) &
    (results.hia > 80) &
    (results.bbb < 0.3) &
    (results.t12.between(2, 8))
]
```

**Expected Output Files:**
```
output/
├── aspirin_adme.json           # Single compound detailed results
├── library_adme.csv            # Batch screening results
├── top_candidates.csv          # Filtered and ranked candidates
```

## Quality Checklist

**Pre-Prediction Checks:**
- [ ] SMILES string is valid and canonical
- [ ] Salt forms removed (if analyzing parent compound)
- [ ] Tautomeric state appropriate for physiological pH
- [ ] Stereochemistry specified (if relevant for activity)

**During Prediction:**
- [ ] Compound within model applicability domain (check similarity to training set)
- [ ] No unusual atoms or functional groups (models trained on typical drug-like space)
- [ ] MW in range 100-800 Da (outside range predictions less reliable)
- [ ] Predictions complete (no missing values for critical properties)

**Post-Prediction Verification:**
- [ ] Drug-likeness scores in reasonable range (sanity check)
- [ ] Individual properties internally consistent (e.g., high LogP predicts low solubility)
- [ ] **CRITICAL**: Comparison to experimental data if available (validate model for chemotype)
- [ ] Rankings align with medicinal chemistry intuition

**Before Making Decisions:**
- [ ] **CRITICAL**: Predictions are NOT experimental data; use for prioritization only
- [ ] Multiple orthogonal models give consistent results
- [ ] Structural alerts checked (toxicity, reactivity)
- [ ] Top candidates selected for experimental validation
- [ ] Documentation of model versions and confidence intervals

**For Regulatory Submissions:**
- [ ] Model validation documented (training set, test set performance)
- [ ] Applicability domain clearly defined
- [ ] Prediction uncertainty quantified
- [ ] Experimental confirmation for key predictions

## Common Pitfalls

**Over-Reliance Issues:**
- ❌ **Treating predictions as experimental facts** → Poor decision making
  - ✅ Use predictions for prioritization; experimental validation required for lead optimization

- ❌ **Single model dependency** → Miss model-specific biases
  - ✅ Compare multiple models; consensus predictions more reliable

- ❌ **Ignoring prediction confidence** → False sense of certainty
  - ✅ Check confidence intervals; low confidence predictions need higher scrutiny

**Input Issues:**
- ❌ **Invalid or non-canonical SMILES** → Wrong compound analyzed
  - ✅ Validate SMILES before prediction; use canonical forms

- ❌ **Analyzing salt forms** → Properties skewed by counterion
  - ✅ Remove salts using `smiles-de-salter`; analyze free base/acid

- ❌ **Ignoring stereochemistry** → Inaccurate predictions for chiral drugs
  - ✅ Specify stereochemistry explicitly; use 3D descriptors if available

**Interpretation Issues:**
- ❌ **Focusing on single property** → Miss overall profile
  - ✅ Consider all ADME properties; use integrated scores like QED or MPO

- ❌ **Rigid cutoff application** → Discard good candidates
  - ✅ Use cutoffs as guidelines; consider project-specific needs

- ❌ **Ignoring property correlations** → Unrealistic optimization
  - ✅ Recognize trade-offs (e.g., increasing LogP improves BBB but reduces solubility)

**Domain Issues:**
- ❌ **Applying to biologics** → Completely inappropriate
  - ✅ These models for small molecules only; use specialized tools for biologics

- ❌ **Extrapolating beyond training set** → Unreliable predictions
  - ✅ Check applicability domain; novel scaffolds need experimental validation

**Workflow Issues:**
- ❌ **No experimental validation** → Continue with false leads
  - ✅ Always validate top predictions experimentally

- ❌ **Not documenting model versions** → Irreproducible results
  - ✅ Record software version, model versions, prediction dates

## Troubleshooting

**Problem: All predictions show "out of domain" warning**
- Symptoms: "Compound outside training set" for entire library
- Causes: Library contains unusual chemotypes (peptidomimetics, macrocycles, etc.)
- Solutions:
  - Use specialized models for non-traditional chemotypes
  - Check if input format correct (SMILES vs InChI)
  - Verify no strange atoms (metals, silicon, etc.)

**Problem: Extreme predictions (negative solubility, >100% absorption)**
- Symptoms: "LogS = -15" or "HIA = 150%"
- Causes: Model extrapolation errors; invalid input structures
- Solutions:
  - Check input structure validity
  - Cap extreme values at physiologically plausible limits
  - Flag for manual review if outside typical ranges

**Problem: Batch processing extremely slow**
- Symptoms: "100 compounds taking 30 minutes"
- Causes: Single-threaded execution; complex models
- Solutions:
  - Enable parallel processing (--n-workers 4)
  - Use faster models for initial screening (QSAR vs ML)
  - Pre-filter with rule-based methods (Lipinski) before detailed ADME

**Problem: Inconsistent predictions across runs**
- Symptoms: "Same compound, different predictions on re-run"
- Causes: Random seed issues; stochastic models
- Solutions:
  - Set random seeds for reproducibility
  - Use deterministic models when consistency critical
  - Average multiple predictions if stochastic models necessary

**Problem: Properties contradict each other**
- Symptoms: "High LogP (4.5) but predicted very soluble"
- Causes: Model inconsistencies; prediction errors
- Solutions:
  - Check input structure (tautomeric form matters for both)
  - Lipophilic compounds (LogP > 3) typically have poor solubility
  - Use thermodynamic cycle checks if available

**Problem: Cannot process certain file formats**
- Symptoms: "Error: Unsupported format" for SDF or MOL files
- Causes: Format limitations; parser issues
- Solutions:
  - Convert to SMILES using `chemical-structure-converter`
  - Check file encoding (UTF-8 vs Latin-1)
  - Verify structure validity with external tools

## References

Available in `references/` directory:

- `lipinski_rules.md` - Detailed explanation of Rule of 5 and variants
- `qsar_models.md` - Technical documentation of predictive models
- `adme_databases.md` - Experimental ADME data sources for validation
- `property_ranges.md` - Acceptable ranges for marketed drugs by class
- `model_validation.md` - Validation statistics and applicability domains
- `cheminformatics_basics.md` - Introduction to molecular descriptors

## Scripts

Located in `scripts/` directory:

- `main.py` - CLI interface for ADME prediction
- `adme_predictor.py` - Core prediction engine
- `absorption.py` - Absorption property models
- `distribution.py` - Distribution property models
- `metabolism.py` - Metabolism prediction models
- `excretion.py` - Excretion and clearance models
- `druglikeness.py` - QED, MPO, and other scoring functions
- `batch_processor.py` - Library screening and parallel processing
- `validator.py` - Input validation and applicability domain checking

## Performance and Resources

**Prediction Speed:**
| Task | Time | Hardware |
|------|------|----------|
| Single compound | 0.5-2 sec | CPU |
| 100 compounds | 30-60 sec | CPU |
| 1000 compounds | 5-10 min | CPU |
| 1000 compounds | 2-3 min | 4-core parallel |
| 10,000 compounds | 30-60 min | 4-core parallel |

**System Requirements:**
- **RAM**: 4 GB minimum; 8 GB for large libraries (>10K compounds)
- **Storage**: 100 MB for models and dependencies
- **CPU**: Multi-core recommended for batch processing
- **No GPU required**: All models CPU-based

**Optimization Tips:**
- Process libraries in batches of 5000-10000
- Use rule-based filters (Lipinski) before expensive ML predictions
- Cache results to avoid re-prediction
- Parallel processing scales nearly linearly up to 8 cores

## Limitations

- **Small Molecules Only**: Models trained on drugs with MW 100-800 Da; unreliable for larger compounds
- **pH 7.4 Assumption**: Most models predict properties at physiological pH
- **Human-Specific**: Predictions for human PK; animal models may differ
- **Healthy Subject Assumption**: Does not account for disease states, drug interactions
- **Single Compound**: Does not predict formulation effects, salt form impact
- **Static Models**: Do not account for induction, inhibition, or time-dependent changes
- **Training Set Bias**: Underperforms for novel scaffolds not in training data
- **Qualitative Only**: For Go/No-Go decisions; not for precise quantitative predictions
- **No Toxicity**: ADME only; use separate tools for safety assessment

**Model Accuracy (Typical):**
- LogP: R² = 0.85-0.95 (very good)
- Solubility: R² = 0.65-0.80 (moderate)
- HIA: Accuracy = 75-85% (good)
- BBB: Accuracy = 70-80% (moderate)
- Metabolic stability: R² = 0.60-0.75 (moderate)
- T1/2: R² = 0.50-0.65 (challenging)

## Version History

- **v1.0.0** (Current): Initial release with 20+ ADME endpoints, QED scoring, batch processing
- Planned: Integration with PK simulation, population variability modeling, formulation effects

---

**⚠️ CRITICAL DISCLAIMER: These predictions are computational estimates for prioritization and guidance only. They do NOT replace experimental ADME studies required for regulatory submissions or clinical decision-making. Always validate predictions with appropriate in vitro and in vivo assays before advancing compounds.**

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `--smiles` | str | Required | SMILES string of the molecule |
| `--properties` | str | ["all"] | Specific properties to calculate |
| `--format` | str | "json" | Output format |
| `--input` | str | Required | Input CSV file with SMILES column |
| `--output` | str | Required | Output file for results |
