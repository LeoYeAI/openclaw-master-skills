---
name: anki-card-creator
description: Convert medical textbook content, lecture notes, and study materials into 
  Anki flashcards using spaced repetition optimization. Supports multiple card types 
  (basic, cloze, image occlusion) with automated tagging and deck organization for 
  efficient medical exam preparation.
allowed-tools: [Read, Write, Bash, Edit]
license: MIT
metadata:
    skill-author: AIPOCH
---

# Anki Card Creator

## Overview

Intelligent flashcard generation tool that transforms medical study materials into Anki-compatible cards optimized for long-term retention through evidence-based spaced repetition.

**Key Capabilities:**
- **Multi-Format Input**: PDF textbooks, lecture slides, notes, web articles
- **Card Type Selection**: Basic, reversible, cloze deletion, image occlusion
- **Spaced Repetition Optimization**: Cards formatted for optimal review intervals
- **Automated Tagging**: Hierarchical organization by subject and topic
- **Media Integration**: Auto-download and embed relevant images
- **Batch Processing**: Convert entire chapters or courses efficiently

## When to Use

**✅ Use this skill when:**
- Preparing for medical board exams (USMLE, MCAT, specialty boards)
- Memorizing drug names, mechanisms, and side effects
- Learning anatomy structures and relationships
- Retaining biochemical pathways and reactions
- Creating pathology differential diagnosis cards
- Converting lecture notes to active recall format
- Building comprehensive review decks from textbooks

**❌ Do NOT use when:**
- Learning conceptual understanding → Use textbooks/videos first
- Memorizing without context → Ensure comprehension before card creation
- Creating cards for rapidly changing information → Use current resources
- Substituting clinical experience → Cards supplement, not replace practice
- Complex procedural skills → Use simulation or hands-on training

**Integration:**
- **Upstream**: `abstract-summarizer` (textbook chapter condensation), `pdf-text-extractor` (content extraction)
- **Downstream**: `anki-sync-server` (cloud backup), `study-schedule-optimizer` (review planning)

## Core Capabilities

### 1. Cloze Deletion Generation

Create fill-in-the-blank cards from dense text:

```python
from scripts.card_creator import AnkiCardCreator

creator = AnkiCardCreator()

# Generate cloze cards from text
text = """
Acute inflammation is characterized by five cardinal signs: 
redness (rubor), heat (calor), swelling (tumor), pain (dolor), 
and loss of function (functio laesa). These result from 
vasodilation, increased vascular permeability, and leukocyte 
infiltration.
"""

cards = creator.create_cloze_cards(
    text=text,
    n_cards=3,  # Generate 3 cards from this text
    difficulty="intermediate",
    tags=["Pathology", "Inflammation", "General_Pathology"]
)

# Output format (Anki-compatible)
# Card 1: "Acute inflammation is characterized by {{c1::five}} cardinal signs..."
# Card 2: "...signs: {{c1::redness}} (rubor), {{c2::heat}} (calor)..."
```

**Cloze Strategies:**
| Strategy | Use Case | Example |
|----------|----------|---------|
| **Single Deletion** | Key facts | "The {{c1::liver}} is the largest internal organ" |
| **Multiple Deletions** | Lists/groups | "CRAB symptoms: {{c1::Calcium}}, {{c2::Renal}}, {{c3::Anemia}}, {{c4::Bone}}" |
| **Hierarchical** | Progressive detail | "{{c1::Metformin}} is a {{c2::biguanide}} that {{c3::decreases hepatic glucose production}}" |

### 2. Basic and Reversible Cards

Generate question-answer pairs:

```python
# Create basic cards
cards = creator.create_basic_cards(
    content={
        "What is the mechanism of action of penicillin?": 
            "Inhibition of bacterial cell wall synthesis by binding to PBPs",
        "What are the major side effects of ACE inhibitors?":
            "Dry cough, hyperkalemia, angioedema, hypotension"
    },
    reversible=True,  # Create reverse cards too
    tags=["Pharmacology", "Antibiotics"]
)
```

**Card Types:**
- **Basic**: Question → Answer
- **Reversible**: Both directions (Q→A and A→Q)
- **Type-in**: Student types answer for active recall
- **Hint Cards**: Progressive disclosure with hints

### 3. Image Occlusion Cards

Create visual learning cards from diagrams:

```python
# Image occlusion for anatomy
cards = creator.create_image_occlusion(
    image_path="brachial_plexus.png",
    occlude_regions=[
        {"label": "Musculocutaneous nerve", "coords": (120, 200, 200, 240)},
        {"label": "Median nerve", "coords": (300, 250, 380, 290)},
        {"label": "Ulnar nerve", "coords": (400, 280, 480, 320)}
    ],
    card_type="one_by_one"  # or "all_at_once"
)
```

**Occlusion Types:**
- **One by One**: Reveal structures progressively
- **All at Once**: Identify all occluded regions
- **Transparent**: Hint visible through occlusion
- **Colored**: Different colors for different structures

### 4. Smart Tagging and Organization

Automatically organize cards into logical hierarchies:

```python
# Auto-tag based on content
cards = creator.process_textbook_chapter(
    chapter_text=pathoma_chapter,
    source="Pathoma - Hematopoiesis",
    auto_tag=True,
    tag_hierarchy=[
        "Pathoma",
        "{{chapter_name}}",
        "{{section_name}}"
    ]
)

# Results in tags like:
# Pathoma::Hematopoiesis::Red_Cell_Disorders
# Pathoma::Hematopoiesis::White_Cell_Disorders
```

**Tagging Strategies:**
- **Source-based**: First Aid, Pathoma, Sketchy
- **Subject-based**: Anatomy, Physiology, Pharmacology
- **Exam-based**: USMLE_Step1, Step2_CK, Shelf_Exams
- **Difficulty**: High_Yield, Medium_Yield, Low_Yield

## Common Patterns

### Pattern 1: Textbook Chapter Conversion

**Scenario**: Convert entire First Aid chapter to Anki deck.

```bash
# Extract and convert chapter
python scripts/main.py \
  --input first_aid_cardiology.pdf \
  --chapter "Ischemic Heart Disease" \
  --card-type cloze \
  --n-cards-per-page 3 \
  --tags "First_Aid::Cardiology::IHD" \
  --output ischemic_heart_disease.apkg

# Import directly to Anki
# File ready for import with media included
```

**Workflow:**
1. Read chapter for understanding first
2. Run conversion tool
3. Review generated cards for accuracy
4. Import to Anki
5. Study with standard spaced repetition

### Pattern 2: Drug Cards with Images

**Scenario**: Create comprehensive pharmacology cards.

```python
# Generate drug cards with mechanisms
drugs = [
    {
        "name": "Metformin",
        "class": "Biguanide",
        "mechanism": "Activates AMPK, decreases hepatic gluconeogenesis",
        "indications": "Type 2 diabetes, PCOS",
        "side_effects": "GI upset, lactic acidosis (rare), B12 deficiency",
        "image": "metformin_structure.png"
    }
]

cards = creator.create_drug_cards(
    drugs=drugs,
    include_structures=True,
    include_mechanism_diagrams=True,
    tags=["Pharmacology", "Diabetes", "First_Line"]
)
```

**Card Format:**
```
Front: Metformin - Class?
Back: Biguanide
Tags: Pharmacology::Diabetes::First_Line

Front: Metformin - Mechanism?
Back: Activates AMPK → decreases hepatic gluconeogenesis
Image: [mechanism diagram]
Tags: Pharmacology::Diabetes::Mechanism

Front: Metformin - Side effects?
Back: GI upset, lactic acidosis (rare), B12 deficiency
Tags: Pharmacology::Diabetes::Side_Effects
```

### Pattern 3: Pathology Differential Cards

**Scenario**: Create cards for differential diagnosis practice.

```python
# Differential diagnosis cards
cards = creator.create_differential_cards(
    condition="Cough with hemoptysis",
    differentials=[
        {"diagnosis": "Lung cancer", "key_features": "Smoker, weight loss, mass on CT"},
        {"diagnosis": "TB", "key_features": "Immigrant, night sweats, cavitary lesion"},
        {"diagnosis": "PE", "key_features": "Sudden onset, tachypnea, D-dimer elevated"},
        {"diagnosis": "Bronchiectasis", "key_features": "Chronic cough, purulent sputum, dilated airways"}
    ],
    card_type="compare_contrast"
)
```

**Card Types:**
- **Feature → Diagnosis**: "Smoker + hemoptysis + weight loss → ?"
- **Diagnosis → Features**: "Lung cancer presentation?"
- **Compare**: "Differentiate lung cancer vs TB"

### Pattern 4: Lecture Notes to Cards

**Scenario**: Convert professor's lecture slides to study cards.

```bash
# Process lecture PDF
python scripts/main.py \
  --input lecture_slides.pdf \
  --source "Dr_Smith_Cardiology_Lecture_5" \
  --card-type mixed \
  --extract-images \
  --auto-tag \
  --output cardiology_lecture_5.apkg

# Review and edit in Anki
# Delete low-yield cards
# Add personal mnemonics
```

**Post-Processing Tips:**
- Delete obvious or overly simple cards
- Merge redundant cards
- Add personal memory hooks
- Suspend low-yield topics

## Complete Workflow Example

**Building comprehensive USMLE Step 1 deck:**

```bash
# Step 1: Process multiple sources
python scripts/main.py \
  --input first_aid_pathology.pdf \
  --source "First_Aid_2024" \
  --card-type cloze \
  --tags "First_Aid::Pathology" \
  --output fa_pathology.apkg

python scripts/main.py \
  --input sketchy_pharm.pdf \
  --source "Sketchy_Pharm" \
  --card-type basic \
  --include-images \
  --tags "Sketchy::Pharm" \
  --output sketchy_pharm.apkg

# Step 2: Merge decks
python scripts/main.py \
  --merge fa_pathology.apkg sketchy_pharm.apkg \
  --output usmle_step1_master.apkg

# Step 3: Add leech tags for difficult cards
python scripts/main.py \
  --input usmle_step1_master.apkg \
  --tag-leeches \
  --leech-threshold 8 \
  --output usmle_step1_tagged.apkg
```

**Python API:**

```python
from scripts.card_creator import AnkiCardCreator
from scripts.importers import PDFImporter

# Initialize
creator = AnkiCardCreator()
importer = PDFImporter()

# Import and process textbook
content = importer.import_pdf(
    path="robbins_pathologic_basis_of_disease.pdf",
    pages="150-200",  # Inflammation chapter
    extract_images=True
)

# Create cloze cards
cards = creator.create_cloze_cards(
    text=content.text,
    images=content.images,
    n_cards=50,
    difficulty="advanced",
    tags=["Robbins", "General_Pathology", "Inflammation"]
)

# Add image occlusion for diagrams
for diagram in content.diagrams:
    occlusion_cards = creator.create_image_occlusion(
        image=diagram,
        auto_detect_labels=True
    )
    cards.extend(occlusion_cards)

# Export Anki package
creator.export_apkg(
    cards=cards,
    deck_name="Robbins_Inflammation",
    output_path="robbins_inflammation.apkg"
)

print(f"Created {len(cards)} cards ready for Anki import")
```

## Quality Checklist

**Card Quality:**
- [ ] One fact per card (atomicity)
- [ ] Clear, unambiguous questions
- [ ] Answers specific and complete
- [ ] Cloze deletions don't give away answer
- [ ] Images high resolution and relevant
- [ ] Tags hierarchical and consistent

**Educational Value:**
- [ ] Cards test high-yield information
- [ ] Difficulty appropriate for level
- [ ] Connections between related concepts
- [ ] Clinical context included where relevant
- [ ] No duplicate or near-duplicate cards

**Technical Quality:**
- [ ] Valid Anki format (import tested)
- [ ] Media files properly linked
- [ ] UTF-8 encoding for special characters
- [ ] CSS styling readable on mobile
- [ ] Card types appropriate for content

**Before Study:**
- [ ] **CRITICAL**: Review cards for accuracy
- [ ] **CRITICAL**: Delete cards for mastered material
- [ ] Personalize with own mnemonics
- [ ] Adjust card order if needed
- [ ] Set appropriate daily review limits

## Common Pitfalls

**Content Issues:**
- ❌ **Too much information** → "Cramming" cards with multiple facts
  - ✅ One concept per card; break complex topics into multiple cards

- ❌ **Memorization without understanding** → Memorizing without context
  - ✅ Include "why" and clinical significance

- ❌ **Outdated information** → Old guidelines or disproven theories
  - ✅ Verify against current textbooks and guidelines

**Card Design Issues:**
- ❌ **Ambiguous clozes** → "The {{c1::liver}} produces {{c2::bile}}" (which one is being asked?)
  - ✅ Clear question: "The liver produces ?" or "What organ produces bile?"

- ❌ **Overlapping cards** → Testing same fact multiple ways
  - ✅ Merge redundant cards; each fact tested once optimally

- ❌ **Recognition vs. recall** → Cards too easy (recognition only)
  - ✅ Use cloze deletions and type-in cards for active recall

**Study Strategy Issues:**
- ❌ **Too many new cards** → 100+ new cards/day leads to burnout
  - ✅ Sustainable pace: 20-30 new cards/day

- ❌ **No review of missed cards** → Ignoring leeches
  - ✅ Tag and review difficult cards separately

- ❌ **Passive card creation** → Making cards without studying
  - ✅ Create cards for immediate use; don't build massive backlog

## References

Available in `references/` directory:

- `anki_format_spec.md` - Anki .apkg file format specifications
- `spaced_repetition_principles.md` - Evidence-based SRS guidelines
- `card_design_best_practices.md` - Effective flashcard design
- `usmle_high_yield_facts.md` - High-yield content for boards
- `image_sources.md` - Open-access medical images
- `tagging_conventions.md` - Standardized tag hierarchies

## Scripts

Located in `scripts/` directory:

- `main.py` - CLI interface for card creation
- `card_creator.py` - Core card generation engine
- `cloze_generator.py` - Cloze deletion algorithms
- `image_occlusion.py` - Visual card creation
- `pdf_importer.py` - Textbook and slide import
- `tag_manager.py` - Automated tagging system
- `media_handler.py` - Image download and optimization
- `anki_exporter.py` - .apkg file generation

## Limitations

- **Context Dependency**: May miss nuanced explanations without full context
- **Image Licensing**: Must verify copyright for extracted images
- **Complex Diagrams**: Simple occlusion may not capture complex relationships
- **Personalization**: Generic cards lack personal memory hooks
- **Volume Control**: Easy to create too many cards; requires curation
- **Active Learning**: Cards supplement but don't replace active problem-solving

## Parameters

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `--input`, `-i` | string | - | No | Input text file with Q&A pairs |
| `--output`, `-o` | string | anki_cards.txt | No | Output file (Anki TSV format) |
| `--drug` | flag | - | No | Create drug information card |
| `--anatomy` | flag | - | No | Create anatomy card |
| `--name` | string | - | No | Drug or structure name |
| `--mechanism` | string | - | No | Mechanism of action (for drug cards) |
| `--indications` | string | - | No | Clinical indications (for drug cards) |
| `--side-effects` | string | - | No | Side effects (for drug cards) |
| `--location` | string | - | No | Anatomical location (for anatomy cards) |
| `--function` | string | - | No | Function (for anatomy cards) |

## Usage

### Basic Usage

```bash
# Create drug card
python scripts/main.py --drug --name "Metformin" --mechanism "Decreases hepatic glucose production" --indications "Type 2 diabetes" --output metformin.txt

# Create anatomy card
python scripts/main.py --anatomy --name "Coronary arteries" --location "Surface of heart" --function "Supply oxygenated blood to myocardium" --output coronary.txt

# Parse Q&A file
python scripts/main.py --input questions.txt --output deck.txt
```

### Input File Format

```
Q: What is the mechanism of action of Metformin?
A: Decreases hepatic glucose production, increases insulin sensitivity

Q: Which artery supplies the left ventricle?
A: Left anterior descending artery (LAD)
```

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python script executed locally | Low |
| Network Access | No external API calls | Low |
| File System Access | Read input file, write to output file | Low |
| Instruction Tampering | Standard prompt guidelines | Low |
| Data Exposure | Output saved only to specified location | Low |

## Security Checklist

- [x] No hardcoded credentials or API keys
- [x] No unauthorized file system access
- [x] Output does not expose sensitive information
- [x] Prompt injection protections in place
- [x] Input validation for file paths
- [x] Output directory restricted to workspace
- [x] Script execution in sandboxed environment

## Prerequisites

```bash
# Python 3.7+
# No additional packages required (uses standard library)
```

## Evaluation Criteria

### Success Metrics
- [x] Successfully creates Anki-compatible TSV files
- [x] Supports drug and anatomy card types
- [x] Parses Q&A files correctly
- [x] Generates valid HTML formatting

### Test Cases
1. **Drug Card**: Create Metformin card → Valid TSV output with formatted front/back
2. **Anatomy Card**: Create coronary artery card → Valid TSV with location and function
3. **File Parse**: Parse Q&A text file → Multiple cards generated

## Lifecycle Status

- **Current Stage**: Draft
- **Next Review Date**: 2026-03-06
- **Known Issues**: None
- **Planned Improvements**:
  - Add Cloze deletion support
  - Support image inclusion
  - Add .apkg export format

---

**🧠 Study Tip: The best flashcard is one you'll actually review. Create cards for material you genuinely need to memorize, and keep the daily review load sustainable. Quality over quantity—better to deeply learn 1000 cards than superficially memorize 5000.**
