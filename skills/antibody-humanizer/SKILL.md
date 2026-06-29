---
name: antibody-humanizer
description: Humanize murine antibody sequences using CDR grafting and framework 
  optimization to reduce immunogenicity while preserving antigen binding. Predicts 
  optimal human germline frameworks and identifies critical back-mutations for 
  therapeutic antibody development.
allowed-tools: [Read, Write, Bash, Edit]
license: MIT
metadata:
    skill-author: AIPOCH
---

# Antibody Humanizer

## Overview

Bioinformatics platform for converting murine antibodies into humanized variants by grafting complementarity-determining regions (CDRs) onto human framework templates while preserving antigen-binding affinity and reducing immunogenicity risk.

**Key Capabilities:**
- **CDR Identification**: Automatic CDR boundary detection (Kabat/Chothia/IMGT schemes)
- **Framework Matching**: Database search for optimal human germline templates
- **Humanization Scoring**: Multi-parameter immunogenicity risk assessment
- **Back-Mutation Prediction**: Identify critical framework residues for retention
- **Batch Processing**: Humanize multiple antibody candidates efficiently
- **Immunogenicity Assessment**: T-cell epitope and humanness scoring

## When to Use

**✅ Use this skill when:**
- Converting murine hybridoma antibodies to therapeutic candidates
- Reducing immunogenicity risk of rodent-derived antibodies
- Selecting human framework templates for CDR grafting
- Identifying critical framework residues for antigen binding
- Comparing multiple humanization strategies for lead optimization
- Preparing antibody sequences for patent filings
- Teaching antibody engineering principles

**❌ Do NOT use when:**
- Fully human antibody generation from phage display → Use `phage-display-library`
- De novo antibody design → Use `antibody-design-ai`
- Affinity maturation → Use `affinity-maturation-predictor`
- ADCC/CDC optimization → Use `fc-engineering-toolkit`
- Final therapeutic candidate selection → Requires experimental validation

**Integration:**
- **Upstream**: `antibody-sequencer` (VH/VL sequence determination), `cdr-grafting-validator` (structural assessment)
- **Downstream**: `protein-struct-viz` (3D visualization), `immunogenicity-predictor` (T-cell epitope analysis)

## Core Capabilities

### 1. CDR Region Identification

Parse antibody sequences and identify CDR boundaries:

```python
from scripts.humanizer import AntibodyHumanizer

humanizer = AntibodyHumanizer()

# Analyze antibody sequence
analysis = humanizer.analyze_sequence(
    vh_sequence="QVQLQQSGPELVKPGASVKISCKASGYTFTDYYMHWVKQSHGKSLEWIGYINPSTGYTEYNQKFKDKATLTVDKSSSTAYMQLSSLTSEDSAVYYCAR...",
    vl_sequence="DIQMTQSPSSLSASVGDRVTITCRASQGISSWLAWYQQKPGKAPKLLIYKASSLESGVPSRFSGSGSGTDFTLTISSLQPEDFATYYCQQYSSYPYT...",
    scheme="chothia"  # Options: kabat, chothia, imgt
)

# Output CDR locations
print(analysis.cdr_regions)
# {
#   "VH_CDR1": {"start": 26, "end": 32, "seq": "GYTFTDY"},
#   "VH_CDR2": {"start": 52, "end": 58, "seq": "INPSTGY"},
#   ...
# }
```

**Numbering Schemes:**
| Scheme | VH CDR1 | VH CDR2 | VH CDR3 | Best For |
|--------|---------|---------|---------|----------|
| **Chothia** | 26-32 | 52-56 | 95-102 | Structural analysis |
| **Kabat** | 31-35 | 50-65 | 95-102 | Sequence-based work |
| **IMGT** | 27-38 | 56-65 | 105-117 | Standardized analysis |

### 2. Human Framework Matching

Identify optimal human germline templates:

```python
# Match against human germline database
matches = humanizer.find_human_frameworks(
    vh_framework=analysis.vh_frameworks,
    vl_framework=analysis.vl_frameworks,
    top_n=5,
    criteria=["homology", "canonical_structure", "vernier_similarity"]
)

# Evaluate each candidate
for match in matches:
    print(f"Template: {match.germline_genes}")
    print(f"Homology: {match.homology:.2%}")
    print(f"Vernier Score: {match.vernier_score:.1f}")
    print(f"Risk Level: {match.immunogenicity_risk}")
```

**Matching Criteria:**
- **Sequence Homology**: Percent identity to human germline
- **Canonical Structure**: Loop conformation compatibility
- **Vernier Region**: Framework residues contacting CDRs
- **Interface Residues**: Packing interactions with CDRs

### 3. Humanization Scoring

Assess immunogenicity risk of candidates:

```python
# Score humanization candidates
scores = humanizer.score_candidates(
    murine_antibody=analysis,
    human_templates=matches,
    scoring_methods=["t20", "h_score", "germline_deviation", "paratope_diversity"]
)

# Rank by overall score
ranked = scores.rank_by_composite_score(
    weights={"humanness": 0.4, "binding_retention": 0.4, "developability": 0.2}
)
```

**Scoring Methods:**
| Method | Description | Target |
|--------|-------------|--------|
| **T20 Score** | 20-mer peptide humanization | >80% human |
| **H-Score** | Hummerblind germline distance | <15 mutations |
| **Paratope Diversity** | CDR germline gene diversity | Low diversity |
| **Developability** | Aggregation/pH stability prediction | High score |

### 4. Back-Mutation Prediction

Identify critical residues to retain from murine framework:

```python
# Predict back-mutations
back_mutations = humanizer.predict_back_mutations(
    murine_vh=analysis.vh_sequence,
    human_vh=matches[0].human_template,
    cdr_regions=analysis.cdr_regions,
    rationale_required=True
)

# Output shows position-specific recommendations
for mutation in back_mutations:
    print(f"Position {mutation.position}: {mutation.human_aa} → {mutation.murine_aa}")
    print(f"Rationale: {mutation.reason}")  # e.g., "Vernier region contact"
    print(f"Priority: {mutation.priority}")  # Critical/Important/Optional
```

**Critical Residue Classes:**
- **Vernier Positions**: Framework residues contacting CDRs (VH 24, 71, 94)
- **Interface Packs**: Residue packing between VH and VL
- **Canonical Anchors**: Cysteines and conserved framework positions
- ** Buried Positions**: Core packing residues affecting stability

## Common Patterns

### Pattern 1: Standard Therapeutic Humanization

**Scenario**: Convert murine anti-tumor antibody to therapeutic candidate.

```bash
# Humanize single antibody
python scripts/main.py \
  --vh "QVQLQQSGPELVKPGASVKISCKAS..." \
  --vl "DIQMTQSPSSLSASVGDRVTITCRAS..." \
  --name "Anti-HER2-Murine-1" \
  --scheme chothia \
  --top-n 3 \
  --output humanization_report.json

# Review top candidates
cat humanization_report.json | jq '.candidates[0]'
```

**Workflow:**
1. Input murine VH/VL sequences
2. Identify CDRs using Chothia scheme
3. Match to human germline database
4. Score top 3 candidates
5. Identify required back-mutations
6. Output humanized sequences

### Pattern 2: Batch Humanization Screening

**Scenario**: Screen multiple murine clones from hybridoma campaign.

```python
# Process multiple antibodies
antibodies = [
    {"name": "Clone-A", "vh": "...", "vl": "..."},
    {"name": "Clone-B", "vh": "...", "vl": "..."},
    {"name": "Clone-C", "vh": "...", "vl": "..."}
]

results = humanizer.batch_humanize(
    antibodies=antibodies,
    ranking_criteria="composite_score",
    min_humanness=0.85
)

# Rank by developability
ranked = results.rank_by(criteria=["humanness", "binding_retention", "stability"])
```

**Selection Criteria:**
- Highest humanness score (>85%)
- Fewest back-mutations required (<6)
- Low immunogenicity risk
- Good developability profile

### Pattern 3: Framework Template Comparison

**Scenario**: Compare different humanization strategies for lead candidate.

```python
# Test multiple framework combinations
strategies = [
    {"vh": "IGHV1-2*02", "vl": "IGKV1-12*01", "name": "Template-A"},
    {"vh": "IGHV3-23*01", "vl": "IGKV3-20*01", "name": "Template-B"},
    {"vh": "IGHV4-34*01", "vl": "IGKV1-5*01", "name": "Template-C"}
]

comparison = humanizer.compare_strategies(
    murine_antibody=analysis,
    strategies=strategies,
    metrics=["homology", "back_mutations", "immunogenicity", "paratope_structure"]
)

comparison.generate_report("framework_comparison.pdf")
```

**Comparison Metrics:**
- Sequence identity to human germline
- Number and location of back-mutations
- Predicted immunogenicity risk
- CDR conformation preservation

### Pattern 4: Intellectual Property Analysis

**Scenario**: Assess humanization for patent landscape analysis.

```bash
# Generate humanized variants
python scripts/main.py \
  --input murine_lead.json \
  --generate-variants 10 \
  --include-back-mutations \
  --output variants_for_ip.json

# Check novelty against patent databases
python scripts/patent_check.py \
  --sequences variants_for_ip.json \
  --databases [USPTO, EPO, WIPO] \
  --output novelty_report.pdf
```

**IP Considerations:**
- Human framework combinations may be patented
- CDR sequences determine antigen specificity
- Back-mutation positions may be prior art
- Document humanization rationale for filings

## Complete Workflow Example

**From murine hybridoma to therapeutic candidate:**

```bash
# Step 1: Sequence analysis and CDR identification
python scripts/main.py \
  --vh $VH_SEQUENCE \
  --vl $VL_SEQUENCE \
  --scheme chothia \
  --output step1_analysis.json

# Step 2: Find best human frameworks
python scripts/main.py \
  --input step1_analysis.json \
  --find-frameworks \
  --top-n 5 \
  --output step2_frameworks.json

# Step 3: Score and rank candidates
python scripts/main.py \
  --input step2_frameworks.json \
  --score-candidates \
  --include-immunogenicity \
  --output step3_scored.json

# Step 4: Predict back-mutations
python scripts/main.py \
  --input step3_scored.json \
  --predict-back-mutations \
  --rationale \
  --output step4_backmutations.json

# Step 5: Generate final humanized sequences
python scripts/main.py \
  --input step4_backmutations.json \
  --generate-sequences \
  --format fasta \
  --output humanized_antibody.fasta
```

**Python API:**

```python
from scripts.humanizer import AntibodyHumanizer
from scripts.scoring import HumanizationScorer
from scripts.backmutation import BackMutationPredictor

# Initialize pipeline
humanizer = AntibodyHumanizer()
scorer = HumanizationScorer()
bm_predictor = BackMutationPredictor()

# Step 1: Parse and analyze
antibody = humanizer.analyze_sequence(
    vh_sequence=murine_vh,
    vl_sequence=murine_vl,
    scheme="chothia"
)

# Step 2: Find human frameworks
candidates = humanizer.find_human_frameworks(
    antibody,
    top_n=5
)

# Step 3: Score candidates
for candidate in candidates:
    scores = scorer.calculate_scores(
        murine=antibody,
        humanized=candidate
    )
    candidate.composite_score = scores.weighted_score()

# Step 4: Select best and predict back-mutations
best = max(candidates, key=lambda x: x.composite_score)
back_mutations = bm_predictor.predict(
    murine=antibody,
    human_template=best
)

# Step 5: Generate final sequence
final_sequence = humanizer.generate_humanized_sequence(
    template=best,
    back_mutations=back_mutations,
    cdrs=antibody.cdr_regions
)

print(f"Humanized antibody generated:")
print(f"- Humanness: {best.humanness:.1%}")
print(f"- Back-mutations: {len(back_mutations)}")
print(f"- Risk level: {best.immunogenicity_risk}")
```

## Quality Checklist

**Input Quality:**
- [ ] VH and VL sequences complete (110-130 aa typical)
- [ ] No ambiguous residues (B, Z, X)
- [ ] Signal peptide removed
- [ ] Constant region removed (variable region only)

**Humanization Assessment:**
- [ ] CDR boundaries correctly identified
- [ ] Human framework homology >80%
- [ ] T20 score >75 (high humanness)
- [ ] Vernier positions analyzed for back-mutations
- [ ] Interface residues checked for packing

**Output Validation:**
- [ ] Humanized sequence valid (no stop codons)
- [ ] CDRs preserved exactly
- [ ] Framework length conserved
- [ ] Back-mutations documented with rationale
- [ ] **CRITICAL**: Immunogenicity risk assessed

**Before Experimental Work:**
- [ ] **CRITICAL**: Top 2-3 candidates selected for expression
- [ ] Binding affinity to be tested (ELISA/Biacore)
- [ ] Stability assessed (thermal/aggregation)
- [ ] Immunogenicity in vitro assays planned

## Common Pitfalls

**Sequence Issues:**
- ❌ **Incomplete sequences** → Missing framework regions
  - ✅ Ensure full VH/VL variable domains provided
  
- ❌ **Wrong numbering scheme** → CDR boundaries incorrect
  - ✅ Verify scheme matches experimental data source

- ❌ **Non-standard residues** → Unusual amino acids
  - ✅ Clean sequences; remove signal peptides

**Design Issues:**
- ❌ **Over-humanization** → Losing antigen binding
  - ✅ Don't exceed 85-90% humanness; retain critical residues

- ❌ **Ignoring back-mutations** → Assuming 100% human framework works
  - ✅ Always predict and test back-mutations

- ❌ **Single candidate only** → No backup options
  - ✅ Generate 2-3 candidates with different frameworks

**Experimental Issues:**
- ❌ **Skipping binding validation** → Assuming in silico = in vivo
  - ✅ Always confirm antigen binding experimentally

- ❌ **Ignoring developability** → Aggregation or instability
  - ✅ Check for problematic residues (unpaired cysteines, hydrophobic patches)

## References

Available in `references/` directory:

- `imgt_germline_database.md` - Human germline gene reference sequences
- `cdr_numbering_schemes.md` - Kabat, Chothia, IMGT comparison
- `humanization_case_studies.md` - Successful therapeutic examples
- `vernier_positions_guide.md` - Critical framework residues
- `immunogenicity_assessment.md` - T-cell epitope prediction methods
- `patent_landscape.md` - Humanization IP considerations

## Scripts

Located in `scripts/` directory:

- `main.py` - CLI interface for humanization
- `humanizer.py` - Core humanization engine
- `cdr_parser.py` - CDR identification and numbering
- `framework_matcher.py` - Human germline database search
- `scoring.py` - Humanization quality assessment
- `backmutation.py` - Critical residue prediction
- `batch_processor.py` - Multiple antibody screening
- `structure_predictor.py` - CDR conformation analysis

## Limitations

- **Binding Prediction**: Cannot accurately predict impact on antigen affinity
- **Developability**: Limited prediction of aggregation or stability issues
- **Immunogenicity**: In silico T-cell epitope prediction has false positives
- **Non-Standard Antibodies**: May not handle camelid, shark, or engineered scaffolds
- **Experimental Validation Required**: All predictions must be confirmed in vitro/vivo
- **Intellectual Property**: Does not check for existing patent claims on sequences

## Parameters

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `--vh` | string | - | No | Murine VH sequence (amino acids) |
| `--vl` | string | - | No | Murine VL sequence (amino acids) |
| `--input`, `-i` | string | - | No | Input JSON file path |
| `--name`, `-n` | string | "" | No | Antibody name |
| `--output`, `-o` | string | - | No | Output file path |
| `--format`, `-f` | string | json | No | Output format (json, fasta, csv) |
| `--scheme`, `-s` | string | chothia | No | Numbering scheme (kabat, chothia, imgt) |
| `--top-n` | int | 3 | No | Number of best candidates to return |

## Usage

### Basic Usage

```bash
# Humanize with direct sequence input
python scripts/main.py --vh "QVQLQQSGPELVKPGASVKMSCKAS..." --vl "DIQMTQSPSSLSASVGDRVTITC..." --name "MyAntibody"

# Use JSON input file
python scripts/main.py --input antibody.json --output results.json

# Use IMGT numbering scheme
python scripts/main.py --vh "SEQUENCE" --vl "SEQUENCE" --scheme imgt
```

### Input JSON Format

```json
{
  "vh_sequence": "QVQLQQSGPELVKPGASVKMSCKAS...",
  "vl_sequence": "DIQMTQSPSSLSASVGDRVTITC...",
  "name": "MyAntibody",
  "scheme": "chothia"
}
```

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python script executed locally | Medium |
| Network Access | No external API calls | Low |
| File System Access | Read input files, write output files | Low |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Output may contain proprietary sequences | Medium |

## Security Checklist

- [x] No hardcoded credentials or API keys
- [x] No unauthorized file system access (../)
- [x] Input validation for sequences
- [x] Prompt injection protections in place
- [x] Error messages sanitized
- [x] Output directory restricted to workspace
- [x] Script execution in sandboxed environment

## Prerequisites

```bash
# Python 3.7+
# No external packages required (uses standard library)
```

## Evaluation Criteria

### Success Metrics
- [x] Successfully parses antibody sequences
- [x] Identifies CDR regions correctly
- [x] Matches human germline frameworks
- [x] Predicts back-mutations
- [x] Generates valid humanized sequences

### Test Cases
1. **Basic Functionality**: Humanize valid VH/VL sequences → Returns candidates
2. **Edge Case**: Invalid sequence characters → Graceful error message
3. **File Input**: Process JSON input → Correctly parses and outputs

## Lifecycle Status

- **Current Stage**: Draft
- **Next Review Date**: 2026-03-06
- **Known Issues**: None
- **Planned Improvements**:
  - Add T20 score database integration
  - Support for camelid and shark antibodies
  - Structure-based CDR prediction

---

**🔬 Critical Note: Computational humanization is a design tool, not a substitute for experimental validation. Always express and test humanized candidates for binding affinity, specificity, stability, and immunogenicity before therapeutic development.**
