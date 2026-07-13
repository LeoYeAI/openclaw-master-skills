---
name: biotech-pitch-deck-narrative
description: Use when creating biotech pitch decks, translating scientific data for investors, preparing fundraising presentations, or developing investor Q&A. Transforms complex scientific and clinical data into compelling investor narratives for biotech fundraising.
allowed-tools: "Read Write Bash Edit"
license: MIT
metadata:
  skill-author: AIPOCH
  version: "1.0"
---

# Biotech Pitch Deck Narrative

## Overview

Strategic communication tool that translates complex biotechnology innovations into compelling business narratives optimized for venture capital, pharmaceutical partnerships, and public market investors.

**Key Capabilities:**
- **Science Translation**: Convert technical data into business value language
- **Narrative Architecture**: Structure Problem→Solution→Market→Traction→Vision flow
- **Stage Optimization**: Tailor messaging for seed through IPO fundraising
- **Investor Calibration**: Adapt for generalist vs. specialist audiences
- **Risk Mitigation**: Frame scientific and regulatory risks as manageable challenges
- **Q&A Preparation**: Anticipate investor questions and prepare responses

## When to Use

**✅ Use this skill when:**
- Preparing Series A/B pitch decks for VC presentations
- Creating management presentations for IPO roadshows
- Developing BD materials for pharma partnership discussions
- Crafting executive summaries for grant applications
- Rehearsing investor Q&A for earnings calls
- Translating clinical data into commercial narratives
- Adapting academic presentations for business audiences

**❌ Do NOT use when:**
- Scientific conference presentations → Use technical language
- Regulatory submission documents → Use formal FDA/EMA formats
- Internal R&D team communications → Use full scientific detail
- Patent applications → Use precise legal/scientific terminology
- Patient-facing materials → Use `lay-summary-gen`

**Integration:**
- **Upstream**: `market-access-value` (commercial assessment), `competitor-trial-monitor` (competitive landscape)
- **Downstream**: `business-model-canvas` (strategy development), `investor-relations-prep` (ongoing communications)

## Core Capabilities

### 1. Science-to-Business Translation

Convert technical concepts into investor-friendly language:

```python
from scripts.narrative_engine import BiotechNarrativeEngine

engine = BiotechNarrativeEngine()

# Translate technical description
translation = engine.translate_science(
    technical_description="""
    Our proprietary AAV9-based gene therapy utilizes a codon-optimized 
    transgene under control of a liver-specific promoter to restore 
    functional enzyme in patients with MPS I deficiency.
    """,
    audience="generalist_vc",
    preserve_accuracy=True
)

print(translation.business_narrative)
# "One-time gene therapy delivering a functional copy of the missing enzyme, 
#  potentially curing MPS I rather than managing symptoms"
```

**Translation Strategies:**
| Technical Concept | Business Translation | Why It Works |
|-------------------|---------------------|--------------|
| "CRISPR-Cas9 gene editing" | "Precision genetic medicine platform" | Platform implies scalability |
| "Phase II clinical data" | "De-risked asset with human proof-of-concept" | Reduces perceived risk |
| "Off-target effects" | "Industry-leading specificity profile" | Competitive framing |
| "MOA via JAK-STAT pathway" | "Novel mechanism addressing root cause" | Value proposition |

### 2. Narrative Architecture

Structure pitch deck flow for maximum impact:

```python
# Generate complete narrative arc
narrative = engine.build_narrative(
    company_stage="series_b",
    science_type="gene_therapy",
    clinical_stage="phase_2",
    target_market="rare_disease",
    key_differentiation="one_time_cure"
)

# Access each component
print(narrative.hook)           # Opening grab
print(narrative.problem)        # Market pain point
print(narrative.solution)       # Your approach
print(narrative.traction)       # Validation to date
print(narrative.ask)            # Funding request
```

**Narrative Structure:**
1. **Hook** (30 seconds): Why this, why now, why you
2. **Problem** ($B+ market): Unmet medical need, current standard limitations
3. **Solution**: Your technology/platform, mechanism of action
4. **Traction**: Clinical data, partnerships, validation
5. **Market**: Size, competition, your advantage
6. **Team**: Track record, why you'll succeed
7. **Ask**: Funding amount, use of proceeds, milestones

### 3. Stage-Specific Optimization

Calibrate message depth for funding round:

```python
# Optimize for different stages
seed_narrative = engine.optimize_for_stage(
    base_narrative=narrative,
    stage="seed",
    focus="team_and_vision"  # Seed cares about team and big idea
)

series_a_narrative = engine.optimize_for_stage(
    base_narrative=narrative,
    stage="series_a",
    focus="proof_of_concept"  # Series A needs validation
)

ipo_narrative = engine.optimize_for_stage(
    base_narrative=narrative,
    stage="ipo",
    focus="commercial_readiness"  # IPO requires near-term revenue
)
```

**Stage Requirements:**
| Stage | Key Questions | Focus Areas |
|-------|---------------|-------------|
| **Seed** ($500K-$2M) | Can you execute? | Team, vision, early validation |
| **Series A** ($10-30M) | Does it work? | POC data, IP position, market entry |
| **Series B** ($30-75M) | Will it scale? | Phase 2/3 data, BD traction, team expansion |
| **Series C/IPO** ($100M+) | Commercial execution | Registration trials, launch prep, revenue path |

### 4. Investor Audience Calibration

Adapt tone and depth for different investor types:

```python
# Calibrate for specific investor
calibrated = engine.calibrate_for_audience(
    narrative=narrative,
    investor_type="healthcare_vc",  # vs "generalist_vc" or "pharma_corp"
    technical_depth="moderate",      # Depth of scientific detail
    risk_tolerance="high"            # Early vs late stage framing
)
```

**Investor Types:**
- **Generalist VC**: Focus on market size, business model, team pedigree
- **Healthcare VC**: Balance science rigor with commercial potential
- **Pharma BD**: Emphasize strategic fit, validation data, partnership potential
- **Public Market**: Highlight near-term catalysts, revenue projections, risk mitigation

## Common Patterns

### Pattern 1: Clinical-Stage Therapeutics

**Scenario**: Phase 2 biotech raising Series B.

```bash
# Generate complete pitch narrative
python scripts/main.py \
  --science "Small molecule inhibitor targeting mutant KRAS G12C" \
  --stage "phase_2" \
  --indication "lung_cancer" \
  --data "ORR 45%, median PFS 6.5 months" \
  --competition "Mirati, J&J" \
  --output series_b_narrative.json
```

**Narrative Elements:**
- **Problem**: KRAS mutations in 30% of cancers; previously "undruggable"
- **Solution**: First-in-class covalent inhibitor with superior selectivity
- **Traction**: Phase 2 data showing 45% response rate, durable responses
- **Market**: $15B+ opportunity across multiple tumor types
- **Differentiation**: Best-in-class potency, favorable safety profile
- **Ask**: $75M to complete Phase 3 and prepare NDA

### Pattern 2: Platform Company

**Scenario**: Novel delivery platform company raising seed.

```python
platform_narrative = engine.generate_platform_narrative(
    platform_technology="Lipid nanoparticle for CNS delivery",
    differentiator="Crosses BBB with 50x improvement over existing LNPs",
    applications=["Alzheimer's", "Parkinson's", "brain_cancer"],
    stage="seed",
    target="platform_value_creation"
)
```

**Platform Story Arc:**
- **Platform Thesis**: Solving delivery problem unlocks multiple indications
- **Validation**: Proof-of-mechanism in 2+ disease models
- **Breadth**: Pipeline across CNS, oncology, rare disease
- **Partnership Appeal": Pharma interest in accessing CNS targets
- **Scalability**: Manufacturing platform supports multiple assets

### Pattern 3: MedTech Device

**Scenario**: Surgical robotics company Series A.

```python
device_narrative = engine.generate_device_narrative(
    device_type="surgical_robot",
    clinical_benefit="50% reduction in complications, 30% faster recovery",
    regulatory_path="510k_de_novo",
    reimbursement="CPT_code_established",
    stage="series_a"
)
```

**Device-Specific Elements:**
- **Clinical Evidence**: Superior outcomes vs. standard of care
- **Economic Value**: Cost savings to healthcare system
- **Regulatory Clarity**: Clear FDA pathway, reimbursement strategy
- **Adoption Strategy**: Training, support, key opinion leader engagement

### Pattern 4: Pharma Partnership Pitch

**Scenario**: Out-licensing asset to big pharma.

```bash
# Generate BD materials
python scripts/main.py \
  --mode partnership \
  --asset "Phase 2 ready asset" \
  --indication "NASH" \
  --data_package "Phase 1b complete, biomarker validated" \
  --partner_profile "novo_nordisk" \
  --output bd_presentation.json
```

**Partnership Framing:**
- **Strategic Fit**: Complements partner's metabolism franchise
- **Validation**: De-risked with human proof-of-mechanism
- **Value Creation**: $500M+ peak sales potential
- **Deal Structure**: Flexible partnership terms proposed

## Complete Workflow Example

**Building comprehensive fundraising materials:**

```python
from scripts.narrative_engine import BiotechNarrativeEngine
from scripts.slide_generator import SlideGenerator
from scripts.qa_prep import QAPreparation

# Initialize
engine = BiotechNarrativeEngine()
slides = SlideGenerator()
qa = QAPreparation()

# Step 1: Generate core narrative
narrative = engine.build_narrative(
    company_stage="series_a",
    therapeutic_area="oncology",
    modality="cell_therapy",
    clinical_stage="phase_1",
    key_differentiation="allogeneic_off_the_shelf"
)

# Step 2: Create slide-by-slide guidance
slide_guide = slides.generate_guide(
    narrative=narrative,
    n_slides=12,
    include_visual_suggestions=True
)

# Step 3: Prepare Q&A
qa_prep = qa.generate_qa(
    narrative=narrative,
    investor_type="healthcare_vc",
    depth="comprehensive"
)

# Step 4: Export complete package
engine.export_package(
    narrative=narrative,
    slides=slide_guide,
    qa=qa_prep,
    output_dir="series_a_pitch_package/"
)
```

## Quality Checklist

**Narrative Quality:**
- [ ] Opening hook grabs attention in 30 seconds
- [ ] Problem is a $B+ market with clear unmet need
- [ ] Solution is differentiated vs. competition
- [ ] Traction validates technical and commercial hypotheses
- [ ] Team has relevant track record
- [ ] Ask is specific with clear milestones

**Translation Accuracy:**
- [ ] Scientific claims remain accurate after simplification
- [ ] No misleading statements or exaggerated claims
- [ ] Risk factors disclosed appropriately
- [ ] Regulatory pathway is realistic
- [ ] Market size assumptions are defensible

**Investor Alignment:**
- [ ] Appropriate for stage and investor type
- [ ] Addresses likely investor concerns proactively
- [ ] Financial projections are reasonable
- [ ] Exit strategy is credible

**Before Presentation:**
- [ ] **CRITICAL**: Legal review of all claims
- [ ] **CRITICAL**: Scientific accuracy check by domain expert
- [ ] Rehearsed with feedback from experienced biotech investors
- [ ] Backup slides prepared for detailed questions

## Common Pitfalls

**Translation Errors:**
- ❌ **Oversimplification** → "Our drug cures cancer" (misleading)
  - ✅ "Our drug showed tumor shrinkage in 40% of patients"

- ❌ **Jargon overload** → Technical terms without explanation
  - ✅ Use analogies: "Like a molecular GPS guiding drugs to tumors"

- ❌ **Hiding risks** → No mention of side effects or competition
  - ✅ Acknowledge risks with mitigation strategies

**Narrative Mistakes:**
- ❌ **Technology in search of problem** → Cool science, no market
  - ✅ Start with problem, solution follows naturally

- ❌ **Ignoring competition** → "We have no competitors"
  - ✅ Acknowledge competition, explain differentiation

- ❌ **Unrealistic projections** → $10B revenue in Year 3
  - ✅ Conservative estimates with clear assumptions

**Stage Mismatch:**
- ❌ **Seed deck with Phase 3 projections** → Too far ahead
  - ✅ Match milestones to stage-appropriate timelines

- ❌ **IPO presentation to seed investors** → Wrong focus
  - ✅ Tailor depth and emphasis to investor sophistication

## References

Available in `references/` directory:

- `vc_presentation_best_practices.md` - Venture capital pitch guidelines
- `biotech_valuation_models.md` - Valuation methodologies by stage
- `regulatory_pathway_guides.md` - FDA/EMA approval timelines
- `market_sizing_methodologies.md` - TAM/SAM/SOM calculations
- `investor_question_bank.md` - Common Q&A by investor type
- `competitive_landscape_templates.md` - Positioning frameworks

## Scripts

Located in `scripts/` directory:

- `main.py` - CLI interface for narrative generation
- `narrative_engine.py` - Core story architecture
- `science_translator.py` - Technical to business translation
- `slide_generator.py` - Deck structure and visual guidance
- `qa_preparation.py` - Investor Q&A preparation
- `competitive_analyzer.py` - Market positioning analysis
- `risk_framer.py` - Risk mitigation messaging
- `stage_optimizer.py` - Funding round calibration

## Limitations

- **Not Financial Advice**: Cannot provide investment recommendations
- **Regulatory Compliance**: Does not ensure SEC or other regulatory compliance
- **Market Specificity**: May not capture niche investor preferences
- **Real-Time Adaptation**: Cannot adjust to live investor reactions
- **Confidentiality**: Does not handle material non-public information protection
- **Legal Review**: All materials require legal counsel review before use

## Parameters

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `--science` | string | - | Yes* | Scientific description of technology |
| `--stage` | string | - | Yes* | Funding stage (pre-seed, seed, series-a, etc.) |
| `--audience` | string | - | Yes* | Target audience type (generalist-vc, healthcare-vc, etc.) |
| `--section` | string | - | No | Section to rewrite (hook, problem, solution, etc.) |
| `--content` | string | - | No | Content to rewrite |
| `--input` | string | - | No | Input file path |
| `--output`, `-o` | string | - | No | Output file path |

*Required depending on subcommand

## Usage

### Basic Usage

```bash
# Generate narrative from science description
python scripts/main.py generate --science "CRISPR gene therapy for sickle cell" --stage series-a --audience healthcare-vc

# Rewrite specific section
python scripts/main.py rewrite --section technology --content "We use AAV vectors..." --audience generalist-vc

# Analyze existing pitch deck
python scripts/main.py analyze --input pitch.pptx --stage series-a
```

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python script executed locally | Low |
| Network Access | No external API calls | Low |
| File System Access | Read/write files | Low |
| Data Exposure | May process confidential business info | Medium |
| Regulatory | Does not ensure SEC compliance | Medium |

## Security Checklist

- [x] No hardcoded credentials or API keys
- [x] No unauthorized file system access
- [x] Output does not expose sensitive information
- [x] Prompt injection protections in place
- [x] Error messages sanitized
- [x] Script execution in sandboxed environment

## Prerequisites

```bash
# Python 3.7+
# No additional packages required (uses standard library)
```

## Evaluation Criteria

### Success Metrics
- [x] Successfully generates pitch narratives
- [x] Adapts content to different investor types
- [x] Rewrites technical content for business audiences
- [x] Provides stage-appropriate messaging

### Test Cases
1. **Generate Narrative**: Science description → Complete pitch narrative
2. **Rewrite Section**: Technical content → Business-friendly version
3. **Audience Adaptation**: Same content for different VC types

## Lifecycle Status

- **Current Stage**: Draft
- **Next Review Date**: 2026-03-06
- **Known Issues**: Help text in Chinese
- **Planned Improvements**:
  - Translate all interface text to English
  - Add more investor personas
  - Enhance narrative templates

---

**💼 Business Note: Successful biotech fundraising requires balancing scientific credibility with business appeal. This tool helps structure narratives, but the underlying science and team execution ultimately determine success. Always maintain integrity—overpromising destroys credibility with sophisticated investors.**
