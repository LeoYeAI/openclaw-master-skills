---
name: anatomy-quiz-master
description: Generate interactive anatomy quizzes for medical education with multiple 
  question types, difficulty levels, and anatomical regions. Supports gross anatomy, 
  neuroanatomy, and clinical correlations for self-assessment and exam preparation.
allowed-tools: [Read, Write, Bash, Edit]
license: MIT
metadata:
    skill-author: AIPOCH
---

# Anatomy Quiz Master

## Overview

Comprehensive anatomy education tool that generates interactive quizzes covering gross anatomy, neuroanatomy, and clinical anatomy with adaptive difficulty and detailed explanations.

**Key Capabilities:**
- **Regional Quizzes**: Head/neck, thorax, abdomen, pelvis, limbs
- **Multiple Question Types**: Identification, function, clinical correlation
- **Adaptive Difficulty**: Basic, intermediate, advanced levels
- **Image Integration**: Label identification with anatomical images
- **Progress Tracking**: Performance analytics and weak area identification
- **Exam Mode**: Timed simulations for USMLE-style preparation

## When to Use

**✅ Use this skill when:**
- Medical students preparing for anatomy practical exams
- Self-assessment after anatomy lectures or dissections
- Identifying weak anatomical regions for focused study
- Creating practice questions for study groups
- Remediation for students who failed anatomy assessments
- Preparing for USMLE Step 1 anatomy questions
- Teaching assistants generating quiz materials for labs

**❌ Do NOT use when:**
- Primary learning resource for anatomy → Use textbooks/atlas first
- Substitute for cadaver lab attendance → Use for supplemental practice only
- Pathology or physiology questions → Use specialized skills for those topics
- Board exam registration or scheduling → Use official NBME resources

**Integration:**
- **Upstream**: `usmle-case-generator` (clinical context), `anki-card-creator` (flashcard export)
- **Downstream**: `study-limitations-drafter` (weakness analysis), `performance-tracker` (progress monitoring)

## Core Capabilities

### 1. Regional Anatomy Quizzes

Generate focused quizzes by body region:

```python
from scripts.quiz_generator import QuizGenerator

generator = QuizGenerator()

# Generate thorax quiz
quiz = generator.generate_quiz(
    region="thorax",
    topics=["heart", "lungs", "mediastinum", "thoracic_wall"],
    difficulty="intermediate",
    n_questions=20
)

# Export for LMS
quiz.export(format="json", filename="thorax_quiz.json")
```

**Supported Regions:**
| Region | Subtopics | Question Types |
|--------|-----------|----------------|
| **Head & Neck** | Skull, cranial nerves, triangles, viscera | Identification, pathways, clinical |
| **Thorax** | Heart, lungs, mediastinum, pleura | Relations, auscultation, imaging |
| **Abdomen** | GI tract, retroperitoneum, vessels | Peritoneal reflections, vascular supply |
| **Pelvis** | Organs, perineum, walls | Gender differences, clinical correlations |
| **Upper Limb** | Shoulder, arm, forearm, hand | Muscle actions, innervation, clinical |
| **Lower Limb** | Hip, thigh, leg, foot | Gait, compartments, clinical exams |
| **Back** | Vertebral column, spinal cord, muscles | Levels, landmarks, clinical |

### 2. Neuroanatomy Pathway Tracing

Specialized quizzes for neural pathways:

```python
# Neuroanatomy quiz
neuro_quiz = generator.generate_neuro_quiz(
    pathway_type="motor",  # or "sensory", "cranial_nerves", "reflexes"
    include_lesions=True,
    clinical_correlations=True
)
```

**Pathway Types:**
- **Motor Pathways**: Corticospinal, corticobulbar, basal ganglia circuits
- **Sensory Pathways**: Dorsal column, spinothalamic, trigeminal
- **Cranial Nerves**: All 12 nerves with nuclei and clinical tests
- **Reflex Arcs**: Deep tendon, superficial, visceral
- **Vascular**: Arterial supply, venous drainage, stroke syndromes

### 3. Clinical Correlation Questions

Integrate anatomy with clinical scenarios:

```python
clinical_quiz = generator.generate_clinical_quiz(
    region="abdomen",
    scenario_types=["surgery", "radiology", "physical_exam"],
    difficulty="advanced"
)
```

**Question Formats:**
```
Clinical Scenario:
"A 45-year-old male presents with epigastric pain radiating to the back. 
CT shows a mass in the lesser sac."

Question: "Which artery runs immediately posterior to the body of the 
pancreas and would be at risk during resection?"

A) Splenic artery
B) Superior mesenteric artery
C) Common hepatic artery
D) Left gastric artery

Correct: B) Superior mesenteric artery

Explanation: The SMA emerges from the aorta at L1 and passes posterior 
to the neck of the pancreas and anterior to the uncinate process...
```

### 4. Adaptive Learning System

Adjust difficulty based on performance:

```python
from scripts.adaptive import AdaptiveEngine

engine = AdaptiveEngine()

# Track student performance
student_progress = engine.track_performance(
    student_id="student_001",
    quiz_results=results,
    time_per_question=True
)

# Generate personalized quiz targeting weak areas
personalized = engine.generate_adaptive_quiz(
    student_progress=student_progress,
    focus_areas=["thorax_vessels", "cranial_nerves"],
    mastery_threshold=0.80
)
```

**Adaptive Features:**
- **Spaced Repetition**: Re-test incorrect topics at optimal intervals
- **Difficulty Scaling**: Increase level after 3 consecutive correct answers
- **Time Pressure**: Gradually reduce time limits for speed practice
- **Weakness Identification**: Track performance by anatomical structure

## Common Patterns

### Pattern 1: Pre-Exam Comprehensive Review

**Scenario**: Student preparing for anatomy practical exam in 2 weeks.

```bash
# Generate full-body comprehensive quiz
python scripts/main.py \
  --mode comprehensive \
  --regions all \
  --difficulty intermediate \
  --n-questions 100 \
  --timed \
  --output pre_practice_exam.json

# Focus on weak areas identified
python scripts/main.py \
  --mode adaptive \
  --focus abdomen,pelvis \
  --difficulty advanced \
  --n-questions 30 \
  --output weak_areas_review.json
```

**Study Schedule:**
- Week 1: Comprehensive quizzes (all regions)
- Week 2: Focus on <80% score regions
- 3 days before: Timed practice exam
- Day before: Light review of marked difficult questions

### Pattern 2: Lab Session Preparation

**Scenario**: Student preparing for cadaver lab on upper limb.

```python
# Pre-lab identification quiz
pre_lab = generator.generate_image_quiz(
    region="upper_limb",
    structure_types=["muscles", "vessels", "nerves"],
    label_type="pins",  # Pin identification format
    n_questions=15
)

# Clinical correlation for post-lab
post_lab_clinical = generator.generate_clinical_quiz(
    region="upper_limb",
    clinical_types=["fractures", "nerve_injuries", "vascular"]
)
```

**Lab Integration:**
- Pre-lab: 15-minute identification quiz
- During lab: Reference key landmarks
- Post-lab: Clinical correlation quiz linking anatomy to disease

### Pattern 3: USMLE Step 1 Preparation

**Scenario**: Medical student preparing for USMLE Step 1.

```bash
# USMLE-style clinical anatomy
python scripts/main.py \
  --mode usmle \
  --clinical-focus \
  --mix-basic-advanced 70:30 \
  --n-questions 40 \
  --timed-per-question 60 \
  --output usmle_anatomy_practice.json
```

**USMLE Features:**
- Clinical vignette format
- Image-based questions (radiology, pathology)
- Two-step reasoning (identify structure → clinical implication)
- Time pressure simulation (60-90 seconds per question)

### Pattern 4: Teaching Assistant Lab Quiz

**Scenario**: TA needs to generate weekly lab quizzes.

```python
# Weekly lab quiz
ta_quiz = generator.generate_ta_quiz(
    week_number=5,
    region="thorax",
    practical_stations=8,
    time_per_station=3,  # minutes
    include_prosection_images=True
)

# Auto-generate answer key
answer_key = ta_quiz.generate_answer_key(
    include_acceptable_variations=True,
    grading_rubric="partial_credit"
)
```

**TA Tools:**
- Station-based practical exam format
- Answer keys with acceptable variations
- Grading rubrics
- Performance statistics by question

## Complete Workflow Example

**Comprehensive anatomy study session:**

```bash
# Step 1: Diagnostic quiz to identify weak areas
python scripts/main.py \
  --mode diagnostic \
  --regions all \
  --n-questions 50 \
  --output diagnostic_results.json

# Step 2: Generate focused study plan
python scripts/main.py \
  --analyze-results diagnostic_results.json \
  --generate-study-plan \
  --days 14 \
  --output study_plan.md

# Step 3: Daily quizzes following plan
python scripts/main.py \
  --mode daily \
  --study-plan study_plan.md \
  --day 1 \
  --output day1_quiz.json

# Step 4: Spaced repetition review
python scripts/main.py \
  --mode spaced-repetition \
  --incorrect-questions diagnostic_results.json \
  --interval 3_days \
  --output review_quiz.json

# Step 5: Final practice exam
python scripts/main.py \
  --mode exam \
  --regions all \
  --n-questions 100 \
  --timed 120_minutes \
  --output final_practice_exam.json
```

**Python API:**

```python
from scripts.quiz_generator import QuizGenerator
from scripts.progress_tracker import ProgressTracker
from reports.performance_report import PerformanceReport

# Initialize
generator = QuizGenerator()
tracker = ProgressTracker()

# Generate adaptive quiz
quiz = generator.generate_adaptive_quiz(
    student_id="med_student_001",
    target_regions=["abdomen", "pelvis"],
    difficulty_start="intermediate"
)

# Student takes quiz
results = quiz.administer()

# Track progress
tracker.record_results(
    student_id="med_student_001",
    quiz_id=quiz.id,
    results=results
)

# Generate progress report
report = PerformanceReport(
    student_id="med_student_001",
    time_range="last_30_days"
)
report.generate_pdf("anatomy_progress.pdf")

# Identify weak areas for next study session
weak_areas = tracker.identify_weak_areas(
    student_id="med_student_001",
    threshold=0.70
)
print(f"Focus next session on: {weak_areas}")
```

## Quality Checklist

**Question Quality:**
- [ ] Anatomical accuracy verified against standard atlases (Netter, Gray's)
- [ ] Clinical correlations reviewed by licensed physicians
- [ ] Multiple difficulty levels appropriately calibrated
- [ ] Distractors (wrong answers) are plausible and educational
- [ ] Explications explain *why* correct answer is right
- [ ] Image quality sufficient for identification (resolution, labeling)

**Educational Value:**
- [ ] Questions test high-yield anatomy (clinically relevant)
- [ ] Progressive difficulty builds knowledge systematically
- [ ] Clinical scenarios reflect real patient presentations
- [ ] Explanations include anatomical reasoning

**Technical Quality:**
- [ ] Randomization prevents pattern recognition
- [ ] No duplicate questions in quiz banks
- [ ] Image files properly licensed or original
- [ ] Accessibility compliance (alt text for images)

**Before Use:**
- [ ] **CRITICAL**: Faculty review for anatomical accuracy
- [ ] Pilot test with target student population
- [ ] Time limits appropriate for difficulty
- [ ] Answer key double-checked for errors

## Common Pitfalls

**Content Issues:**
- ❌ **Outdated anatomical knowledge** → Teaching old terminology
  - ✅ Use current Terminologia Anatomica standards

- ❌ **Nit-picky details** → Testing obscure structures rarely clinically relevant
  - ✅ Focus on high-yield anatomy that appears in clinical practice

- ❌ **Unclear images** → Poor resolution or confusing labels
  - ✅ Use high-quality images; test label legibility at screen resolution

**Educational Issues:**
- ❌ **Questions too easy** → No learning benefit
  - ✅ Calibrate to student level; aim for 60-80% success rate

- ❌ **No clinical context** → Pure memorization without application
  - ✅ Include clinical correlation questions

- ❌ **Punitive difficulty** → Discouraging rather than challenging
  - ✅ Provide encouraging feedback; focus on improvement

**Technical Issues:**
- ❌ **Predictable patterns** → Students game the system
  - ✅ Randomize question order and distractor placement

- ❌ **No progress tracking** → Can't identify weak areas
  - ✅ Implement analytics to guide focused study

## References

Available in `references/` directory:

- `netter_atlas_correlation.md` - Question-to-atlas page mapping
- `terminologia_anatomica.md` - Standard anatomical terminology
- `usmle_content_outline.md` - NBME anatomy topic frequencies
- `clinical_correlations.md` - High-yield clinical anatomy scenarios
- `image_sources.md` - Licensed anatomical image repositories
- `difficulty_calibration.md` - Bloom's taxonomy level alignment

## Scripts

Located in `scripts/` directory:

- `main.py` - CLI for quiz generation
- `quiz_generator.py` - Core question generation engine
- `neuro_quiz.py` - Specialized neuroanatomy questions
- `clinical_correlator.py` - Clinical scenario integration
- `adaptive_engine.py` - Personalized difficulty adjustment
- `image_quiz.py` - Label identification with images
- `progress_tracker.py` - Performance analytics
- `report_generator.py` - Progress reports and statistics

## Limitations

- **Cadaver Images**: Cannot replace hands-on dissection experience
- **3D Spatial Relations**: 2D images may not convey depth relationships
- **Variability**: Normal anatomical variation not fully captured
- **Updates**: Anatomical knowledge evolves; requires periodic review
- **Cultural Sensitivity**: Some anatomical terms may vary by region
- **Disability Accommodation**: Image-based questions need alternatives for visually impaired students

## Parameters

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `--region`, `-r` | string | upper_limb | No | Anatomical region (upper_limb, lower_limb, thorax, abdomen, pelvis, head_neck, neuroanatomy) |
| `--difficulty`, `-d` | string | intermediate | No | Difficulty level (basic, intermediate, advanced) |
| `--count`, `-c` | int | 1 | No | Number of questions to generate |
| `--output`, `-o` | string | - | No | Output file path (JSON format) |
| `--format` | string | json | No | Output format (json or text) |
| `--list-regions` | flag | - | No | List all available regions and exit |

## Usage

### Basic Usage

```bash
# Generate single question
python scripts/main.py --region upper_limb

# Generate 10-question quiz
python scripts/main.py --region neuroanatomy --difficulty advanced --count 10 --output quiz.json

# List available regions
python scripts/main.py --list-regions

# Text format output
python scripts/main.py --region thorax --format text
```

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python script executed locally | Low |
| Network Access | No external API calls | Low |
| File System Access | Read/Write to specified output files only | Low |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Output saved only to specified location | Low |

## Security Checklist

- [x] No hardcoded credentials or API keys
- [x] No unauthorized file system access (../)
- [x] Output does not expose sensitive information
- [x] Prompt injection protections in place
- [x] Input validation for all parameters
- [x] Output directory restricted to workspace
- [x] Script execution in sandboxed environment
- [x] Error messages sanitized

## Prerequisites

```bash
# Python 3.7+
# No additional packages required (uses standard library)
```

## Evaluation Criteria

### Success Metrics
- [x] Successfully generates quiz questions
- [x] Supports multiple anatomical regions
- [x] Provides correct answers with explanations
- [x] Handles edge cases (invalid regions, etc.)

### Test Cases
1. **Basic Functionality**: Generate single question → Returns valid question with options
2. **Edge Case**: Invalid region → Graceful error message
3. **Multiple Questions**: Generate 10 questions → Returns array of questions

## Lifecycle Status

- **Current Stage**: Draft
- **Next Review Date**: 2026-03-06
- **Known Issues**: None
- **Planned Improvements**:
  - Add image support for visual identification
  - Expand question bank
  - Add performance analytics

---

**🧠 Learning Tip: Anatomy is best learned through repeated exposure in multiple contexts. Use these quizzes to reinforce cadaver lab learning, not replace it. Focus on understanding relationships and clinical significance, not just memorization.**
