---
name: automated-soap-note-generator
description: Transform unstructured clinical input (dictation, transcripts, or rough 
  notes) into standardized SOAP (Subjective, Objective, Assessment, Plan) medical 
  documentation. Use ONLY for initial documentation draft generation; ALL output 
  requires physician review before entering patient records. Not for complex cases 
  requiring nuanced clinical reasoning.
allowed-tools: [Read, Write, Bash, Edit]
license: MIT
metadata:
    skill-author: AIPOCH
---

# Automated SOAP Note Generator

## Overview

AI-powered clinical documentation tool that converts unstructured clinical input into professionally formatted SOAP notes compliant with medical documentation standards.

**Key Capabilities:**
- **Intelligent Parsing**: Extracts structured information from free-text clinical narratives
- **SOAP Classification**: Automatically categorizes content into Subjective, Objective, Assessment, Plan sections
- **Medical Entity Recognition**: Identifies symptoms, diagnoses, medications, procedures, and anatomical locations
- **Temporal Analysis**: Extracts timeline information (onset, duration, progression)
- **Template Generation**: Produces standardized SOAP format suitable for EHR integration
- **Multi-modal Input**: Accepts text dictation, transcripts, or clinical notes

## When to Use

**✅ Use this skill when:**
- Converting physician dictation into structured SOAP format for efficiency
- Processing audio-to-text transcripts from patient encounters
- Transforming consultation rough notes into formal documentation
- Generating initial draft documentation to reduce administrative burden
- Standardizing clinical encounter summaries for consistency
- Creating preliminary notes for routine follow-up visits

**❌ Do NOT use when:**
- Input contains PHI that hasn't been de-identified for testing/training
- Complex psychiatric cases requiring nuanced mental status documentation → Use specialized psychiatric documentation tools
- Surgical procedures requiring operative report detail → Use `operative-report-generator`
- Patient requires nuanced clinical reasoning beyond text extraction
- Legal or forensic documentation requiring exact transcription → Use verbatim transcription services
- Critical care situations requiring real-time precise documentation
- Cases requiring differential diagnosis prioritization without physician input

**⚠️ ALWAYS Required:**
- Physician review and approval before entering into patient record
- Verification of medical facts and clinical accuracy
- Confirmation of medication names, dosages, and instructions

## Integration with Other Skills

**Upstream Skills:**
- `medical-scribe-dictation`: Convert physician verbal dictation to text input
- `ehr-semantic-compressor`: Summarize lengthy EHR notes for SOAP generation
- `dicom-anonymizer`: Prepare imaging reports for SOAP inclusion
- `audio-script-writer`: Convert audio recordings to text format

**Downstream Skills:**
- `medical-email-polisher`: Professional communication of SOAP summaries to patients
- `clinical-data-cleaner`: Standardize extracted data for research databases
- `hipaa-compliance-auditor`: Verify de-identification before sharing documentation
- `discharge-summary-writer`: Generate discharge summaries from SOAP encounters
- `referral-letter-generator`: Create referral letters based on Assessment and Plan sections

**Complete Workflow:**
```
Medical Scribe Dictation (audio→text) → 
  Automated SOAP Note Generator (this skill) → 
    Physician Review → 
      EHR Entry / 
      Medical Email Polisher (patient communication) / 
      Referral Letter Generator (referrals)
```

## Core Capabilities

### 1. Input Processing and Preprocessing

Handle various input formats and prepare for NLP analysis:

```python
from scripts.soap_generator import SOAPNoteGenerator

generator = SOAPNoteGenerator()

# Process text input
soap_note = generator.generate(
    input_text="Patient presents with 2-day history of chest pain, radiating to left arm...",
    patient_id="P12345",
    encounter_date="2026-01-15",
    provider="Dr. Smith"
)

# Process from audio transcript
soap_note = generator.generate_from_transcript(
    transcript_path="consultation_transcript.txt",
    patient_id="P12345"
)
```

**Input Preprocessing Steps:**
1. **Text Cleaning**: Remove filler words ("um", "uh"), timestamps, speaker labels
2. **Sentence Segmentation**: Split into clinically meaningful segments
3. **Normalization**: Standardize abbreviations and medical shorthand
4. **Encoding Detection**: Handle various file formats (UTF-8, ASCII, etc.)

**Parameters:**
| Parameter | Type | Required | Description | Default |
|-----------|------|----------|-------------|---------|
| `input_text` | str | Yes* | Raw clinical text or dictation | None |
| `transcript_path` | str | Yes* | Path to transcript file | None |
| `patient_id` | str | No | Patient identifier (MUST be de-identified for testing) | None |
| `encounter_date` | str | No | Date in ISO 8601 format (YYYY-MM-DD) | Current date |
| `provider` | str | No | Healthcare provider name | None |
| `specialty` | str | No | Medical specialty context | "general" |
| `verbose` | bool | No | Include confidence scores | False |

*Either `input_text` or `transcript_path` required

**Best Practices:**
- Always verify input text quality (clear audio → better transcription → better SOAP)
- Remove patient identifiers before processing unless in secure environment
- Split long encounters (>30 minutes) into logical segments
- Flag ambiguous abbreviations for manual review

### 2. Medical Named Entity Recognition (NER)

Identify and extract medical concepts from unstructured text:

```python
# Extract entities with context
entities = generator.extract_medical_entities(
    "Patient has history of hypertension and diabetes, 
     currently taking lisinopril 10mg daily and metformin 500mg BID"
)

# Returns structured entities:
# {
#   "diagnoses": ["hypertension", "diabetes mellitus"],
#   "medications": [
#     {"name": "lisinopril", "dose": "10mg", "frequency": "daily"},
#     {"name": "metformin", "dose": "500mg", "frequency": "BID"}
#   ]
# }
```

**Entity Types Recognized:**
| Category | Examples | Notes |
|----------|----------|-------|
| **Diagnoses** | diabetes, hypertension, pneumonia | ICD-10 compatible where possible |
| **Symptoms** | chest pain, headache, nausea | Includes severity modifiers |
| **Medications** | metformin, lisinopril, aspirin | Extracts dose, route, frequency |
| **Procedures** | ECG, CT scan, blood draw | Includes body site |
| **Anatomy** | left arm, chest, abdomen | Laterality and location |
| **Lab Values** | glucose 120, BP 140/90 | Units and reference ranges |
| **Temporal** | yesterday, 3 days ago, chronic | Normalized to relative dates |

**Common Issues and Solutions:**

**Issue: Missed medications**
- Symptom: Generic names not recognized (e.g., "water pill" for diuretic)
- Solution: Manual review required; tool flags colloquial terms for verification

**Issue: Ambiguous abbreviations**
- Symptom: "SOB" could be shortness of breath or something else
- Solution: Context-aware disambiguation; flag uncertain cases

**Issue: Misspelled drug names**
- Symptom: "metfomin" instead of "metformin"
- Solution: Fuzzy matching with confidence threshold; flag low-confidence matches

### 3. SOAP Section Classification

Automatically categorize sentences into appropriate SOAP sections:

```python
# Classify content into SOAP sections
classified = generator.classify_soap_sections(
    "Patient reports chest pain for 2 days. Physical exam shows BP 140/90. 
     Likely angina. Schedule stress test and start aspirin 81mg daily."
)

# Output structure:
# {
#   "Subjective": ["Patient reports chest pain for 2 days"],
#   "Objective": ["Physical exam shows BP 140/90"],
#   "Assessment": ["Likely angina"],
#   "Plan": ["Schedule stress test", "start aspirin 81mg daily"]
# }
```

**Classification Rules:**
| Section | Content Type | Examples |
|---------|--------------|----------|
| **S** - Subjective | Patient-reported information | "Patient states...", "Patient reports...", "Complains of..." |
| **O** - Objective | Observable/measurable findings | Vital signs, physical exam, lab results, imaging |
| **A** - Assessment | Clinical interpretation | Diagnosis, differential, clinical impression |
| **P** - Plan | Actions to be taken | Medications, procedures, follow-up, patient education |

**Multi-label Handling:**
Some sentences span multiple sections (e.g., "Patient reports chest pain [S], which was sharp and 8/10 [S], with ECG showing ST elevation [O]")
- Tool splits compound sentences at conjunctions
- Assigns primary and secondary labels with confidence scores

**Best Practices:**
- Review classification accuracy, especially for complex multi-part statements
- Manually verify Assessment section (most critical for patient care)
- Ensure temporal context preserved (recent vs. chronic symptoms)

### 4. Temporal Information Extraction

Parse and normalize timeline information:

```python
# Extract temporal relationships
timeline = generator.extract_temporal_info(
    "Patient had chest pain starting 3 days ago, worsening since yesterday. 
     Had similar episode 2 months ago that resolved with rest."
)

# Returns:
# {
#   "onset": "3 days ago",
#   "progression": "worsening",
#   "previous_episodes": [
#     {"time": "2 months ago", "resolution": "with rest"}
#   ]
# }
```

**Temporal Elements Extracted:**
- **Onset**: When symptoms started ("2 days ago", "this morning")
- **Duration**: How long symptoms lasted ("for 3 hours", "ongoing")
- **Frequency**: How often symptoms occur ("daily", "intermittently")
- **Progression**: Getting better/worse/stable
- **Prior Episodes**: Previous similar events
- **Context**: "before meals", "with exertion", "at night"

**Normalization:**
Converts relative dates to standardized format:
- "yesterday" → Encounter date minus 1 day
- "3 days ago" → Specific date calculated
- "chronic" → Flagged for chronic condition tracking

### 5. Negation and Uncertainty Detection

Critical for accurate medical documentation:

```python
# Detect negations and uncertainties
analysis = generator.analyze_certainty(
    "Patient denies chest pain. No shortness of breath. 
     Possibly had fever yesterday but not sure."
)

# Identifies:
# - "denies chest pain" → Negative finding (important!)
# - "No shortness of breath" → Negative finding
# - "Possibly had fever" → Uncertain finding (flag for verification)
```

**Detection Categories:**
| Type | Cues | Action |
|------|------|--------|
| **Negation** | denies, no, without, absent | Mark as negative finding |
| **Uncertainty** | possibly, maybe, uncertain, ? | Flag for physician review |
| **Hypothetical** | if, would, could | Note as conditional |
| **Family History** | family history of, mother had | Separate from patient findings |

**⚠️ Critical:**
Negation errors are high-risk (e.g., missing "denies" → documenting symptom they don't have)
- Always verify negative findings in Subjective section
- Uncertain findings must be explicitly marked for review

### 6. Structured SOAP Generation

Produce final formatted output:

```python
# Generate complete SOAP note
soap_output = generator.generate_soap_document(
    structured_data=classified,
    format="markdown",  # Options: markdown, json, hl7, text
    include_metadata=True
)
```

**Output Format:**
```markdown
# SOAP Note

**Patient ID:** P12345  
**Date:** 2026-01-15  
**Provider:** Dr. Smith

## Subjective
Patient reports [extracted symptoms with duration]. History of [chronic conditions]. 
Currently taking [medications]. Patient denies [negative findings].

## Objective
**Vital Signs:** [BP, HR, RR, Temp, O2Sat]  
**Physical Examination:** [Exam findings by system]  
**Laboratory/Data:** [Relevant results]

## Assessment
[Primary diagnosis/differential]  
[Clinical reasoning summary]

## Plan
1. [Action item 1]
2. [Action item 2]
3. [Follow-up instructions]

---
*Generated by AI. REQUIRES PHYSICIAN REVIEW before entry into patient record.*
```

**Export Formats:**
| Format | Use Case | Notes |
|--------|----------|-------|
| **Markdown** | Human review, documentation | Default, readable |
| **JSON** | System integration, research | Structured data |
| **HL7 FHIR** | EHR integration | Healthcare standard |
| **Plain Text** | Simple documentation | Minimal formatting |
| **CSV** | Data analysis, research | Tabular data export |

## Complete Workflow Example

**From audio dictation to reviewed SOAP note:**

```bash
# Step 1: Process audio to text (using medical-scribe-dictation or external)
# Assuming you have transcript: consultation.txt

# Step 2: Generate SOAP note
python scripts/main.py \
  --input-file consultation.txt \
  --patient-id P12345 \
  --provider "Dr. Smith" \
  --specialty "cardiology" \
  --output soap_draft.md \
  --format markdown

# Step 3: Review output
# - Open soap_draft.md
# - Verify medical accuracy
# - Correct any errors
# - Add missing clinical reasoning

# Step 4: Finalize (after physician approval)
# - Copy approved content to EHR
# - Or use for patient communication
```

**Python API Usage:**

```python
from scripts.soap_generator import SOAPNoteGenerator
from scripts.post_processor import ReviewFormatter

# Initialize
generator = SOAPNoteGenerator()
reviewer = ReviewFormatter()

# Generate draft
with open("dictation.txt", "r") as f:
    raw_text = f.read()

draft = generator.generate(
    input_text=raw_text,
    patient_id="P12345",
    encounter_date="2026-01-15",
    provider="Dr. Smith",
    specialty="internal_medicine"
)

# Add physician review markers
marked_draft = reviewer.add_review_markers(draft)

# Save with warning header
reviewer.save_with_disclaimer(
    marked_draft, 
    output_path="soap_draft_review.md",
    disclaimer="REQUIRES PHYSICIAN REVIEW - NOT FOR DIRECT ENTRY"
)
```

**Expected Output Files:**
```
output/
├── soap_draft.md              # Generated SOAP note
├── entities_extracted.json     # Structured medical entities
├── classification_report.txt   # Confidence scores for each section
└── review_checklist.md         # Items requiring manual verification
```

## Quality Checklist

**Pre-generation Checks:**
- [ ] Input text is legible (not garbled transcription)
- [ ] Audio quality was sufficient (if from dictation)
- [ ] Patient identifiers handled per HIPAA guidelines
- [ ] No obvious transcription errors (medication names make sense)

**During Generation:**
- [ ] All medications recognized and dosages extracted
- [ ] Temporal information correctly normalized
- [ ] Negations properly detected (denies = negative finding)
- [ ] Uncertain statements flagged for review
- [ ] SOAP sections logically organized

**Post-generation Review (PHYSICIAN MUST CHECK):**
- [ ] **CRITICAL**: Medical facts are accurate
- [ ] **CRITICAL**: Medication names, dosages, and frequencies correct
- [ ] **CRITICAL**: Assessment section reflects clinical reasoning
- [ ] Allergies correctly documented
- [ ] Vital signs accurately transcribed
- [ ] Physical exam findings complete
- [ ] Plan includes all necessary actions
- [ ] Follow-up instructions clear and appropriate
- [ ] No fabricated information (hallucinations)

**Before EHR Entry:**
- [ ] Physician has reviewed and approved
- [ ] Corrections made as needed
- [ ] Signed/attested by responsible provider
- [ ] Metadata complete (date, provider, encounter type)

## Common Pitfalls

**Input Quality Issues:**
- ❌ **Poor audio quality** (background noise, mumbling) → Garbled transcription → Inaccurate SOAP
  - ✅ Ensure quiet environment for dictation; use high-quality microphone
  
- ❌ **Incomplete dictation** (provider trails off, changes subject) → Missing information
  - ✅ Dictate in complete sentences; pause between distinct thoughts

- ❌ **Heavy accents or fast speech** → Transcription errors
  - ✅ Speak clearly; review transcription immediately if possible

**Medical Accuracy Issues:**
- ❌ **Medication name confusion** ("Lipitor" vs "lipid lowerer") → Wrong drug documented
  - ✅ Always verify medication names; use generic names when possible

- ❌ **Missed negations** ("denies chest pain" → "has chest pain") → Critical error
  - ✅ Carefully review Subjective section for negative findings

- ❌ **Temporal confusion** ("pain since yesterday" vs "pain until yesterday") → Wrong timeline
  - ✅ Verify onset, duration, and progression with patient

- ❌ **Uncertain findings documented as certain** ("possibly pneumonia" → "pneumonia")
  - ✅ Flag all uncertain language for clarification

**Documentation Issues:**
- ❌ **Hallucinated information** (AI adds details not in input) → False documentation
  - ✅ Compare output directly with source material
  
- ❌ **Missing context** ("continue meds" without specifying which ones)
  - ✅ Ensure plan is specific and actionable

- ❌ **Generic assessments** ("patient is stable" without specifics)
  - ✅ Add clinical reasoning to Assessment section

**Compliance Issues:**
- ❌ **Entering AI-generated text without review** → Legal/medical liability
  - ✅ NEVER enter into patient record without physician approval
  
- ❌ **Including PHI in unsecured processing** → HIPAA violation
  - ✅ Use only in HIPAA-compliant environments

**Process Issues:**
- ❌ **Not saving original input** → Cannot verify if questions arise
  - ✅ Retain original dictation/transcript
  
- ❌ **No audit trail** → Cannot track AI involvement
  - ✅ Document that SOAP was AI-assisted in metadata

## Troubleshooting

**Problem: Poor entity recognition**
- Symptoms: Medications or diagnoses not detected
- Causes: Specialized terminology, misspellings, rare conditions
- Solutions:
  - Use generic drug names when possible
  - Check `references/medical_terminology.md` for supported terms
  - Manually add missing entities during review

**Problem: Wrong SOAP classification**
- Symptoms: Physical exam findings in Subjective; symptoms in Objective
- Causes: Ambiguous phrasing ("Patient appears in pain")
- Solutions:
  - Rephrase input for clarity ("Patient reports pain level 8/10")
  - Manually move sentences to correct sections
  - Check classification confidence scores

**Problem: Missing temporal information**
- Symptoms: All events seem to happen "now"
- Causes: Unclear time references ("recently", "a while ago")
- Solutions:
  - Use specific dates or durations in dictation
  - Manually add timeline during review
  - Ask patient for clarification on timing

**Problem: Inappropriate certainty level**
- Symptoms: "Possibly" removed; "definitely" added
- Causes: AI over-confident in uncertain situations
- Solutions:
  - Preserve physician's uncertainty language
  - Add qualifiers back during review
  - Flag all diagnostic statements for verification

**Problem: Formatting errors in output**
- Symptoms: Garbled text, wrong encoding, missing sections
- Causes: Special characters, non-ASCII text, file encoding issues
- Solutions:
  - Save input as UTF-8
  - Avoid special symbols in medication names
  - Check output file encoding

**Problem: Processing fails or hangs**
- Symptoms: Script crashes, timeout errors
- Causes: Very long input (>5000 words), complex nested clauses
- Solutions:
  - Split very long encounters into sections
  - Simplify complex sentences
  - Increase timeout limit for large inputs

## References

Available in `references/` directory:

- `clinical_guidelines.md` - Standards for medical documentation
- `sample_soap_notes.md` - Example SOAP notes by specialty
- `medical_terminology.md` - Supported medical terms and abbreviations
- `nlp_pipeline_documentation.md` - Technical details of NLP processing
- `hipaa_compliance_guide.md` - Guidelines for safe handling of PHI
- `specialty_specific_templates.md` - Templates for cardiology, orthopedics, etc.

## Scripts

Located in `scripts/` directory:

- `main.py` - CLI interface for SOAP generation
- `soap_generator.py` - Core SOAP generation logic
- `entity_extractor.py` - Medical NER module
- `soap_classifier.py` - Section classification engine
- `temporal_parser.py` - Timeline extraction
- `negation_detector.py` - Negation and uncertainty detection
- `post_processor.py` - Output formatting and review markers
- `batch_processor.py` - Process multiple encounters
- `validator.py` - Quality checks and compliance validation

## Performance and Resources

**Typical Processing Time:**
- Short encounter (<5 min dictation): 10-15 seconds
- Standard visit (10-15 min): 30-45 seconds
- Complex case (30+ min): 1-2 minutes

**System Requirements:**
- **RAM**: 4 GB minimum, 8 GB recommended for large batches
- **Storage**: ~500 MB for models and dependencies
- **CPU**: Multi-core processor recommended for batch processing
- **GPU**: Not required but speeds up NLP processing if available

**Supported Input Sizes:**
- Text: Up to 10,000 words per encounter
- File: Up to 10 MB text files
- Audio transcript: Up to 2 hours of clinical encounter

## Limitations

- **Not a diagnostic tool**: Cannot make medical decisions or diagnoses
- **Specialty coverage**: Best performance in internal medicine, family practice; variable in highly specialized fields
- **Language**: Optimized for English; limited support for other languages
- **Context window**: May lose context in very long, complex encounters
- **Ambiguity**: Struggles with highly ambiguous or contradictory input
- **Rare conditions**: May not recognize very rare diseases or new medications
- **Non-verbal cues**: Cannot interpret tone, emphasis, or non-verbal information from audio

## Regulatory and Legal Notes

- **FDA Status**: This tool is NOT FDA-approved as a medical device
- **HIPAA Compliance**: Must be used in HIPAA-compliant environment
- **Liability**: User (physician/healthcare provider) retains full responsibility for final documentation
- **Documentation**: Must disclose AI assistance in medical record per institutional policy
- **Malpractice**: AI-generated content does not replace clinical judgment

## Version History

- **v1.0.0** (Current): Initial release with core SOAP generation capabilities
- Planned: Enhanced specialty-specific models, multi-language support, EHR direct integration

## Parameters

| Parameter | Type | Default | Required | Description |
|-----------|------|---------|----------|-------------|
| `--input`, `-i` | string | - | No | Input clinical text directly |
| `--input-file`, `-f` | string | - | No | Path to input text file |
| `--output`, `-o` | string | - | No | Output file path |
| `--patient-id`, `-p` | string | - | No | Patient identifier |
| `--provider` | string | - | No | Healthcare provider name |
| `--format` | string | markdown | No | Output format (markdown, json) |

## Usage

### Basic Usage

```bash
# Generate SOAP from text
python scripts/main.py --input "Patient reports chest pain..." --output note.md

# From file
python scripts/main.py --input-file consultation.txt --patient-id P12345 --provider "Dr. Smith"

# JSON output
python scripts/main.py --input-file notes.txt --format json --output note.json
```

## Risk Assessment

| Risk Indicator | Assessment | Level |
|----------------|------------|-------|
| Code Execution | Python script executed locally | Medium |
| Network Access | No external API calls | Low |
| File System Access | Read input files, write output files | Low |
| Data Exposure | May process PHI (Protected Health Information) | High |
| HIPAA Compliance | Must be used in compliant environment | High |

## Security Checklist

- [x] No hardcoded credentials or API keys
- [x] No unauthorized file system access
- [x] Output does not contain hardcoded PHI
- [x] Prompt injection protections in place
- [x] Input validation for file paths
- [x] Error messages sanitized
- [x] **CRITICAL**: HIPAA compliance required for PHI

## Prerequisites

```bash
# Python 3.7+
# No external packages required (uses standard library)
```

## Evaluation Criteria

### Success Metrics
- [x] Successfully parses unstructured clinical text
- [x] Correctly categorizes into SOAP sections
- [x] Extracts medical entities (symptoms, diagnoses, medications)
- [x] Generates properly formatted output

### Test Cases
1. **Text Input**: Clinical text → Properly formatted SOAP note
2. **File Input**: Text file → Complete SOAP note with metadata
3. **JSON Output**: Text input → Valid JSON with all fields

## Lifecycle Status

- **Current Stage**: Draft
- **Next Review Date**: 2026-03-06
- **Known Issues**: None
- **Planned Improvements**:
  - Enhanced entity recognition
  - Specialty-specific templates
  - EHR integration support

---

**⚠️ CRITICAL REMINDER: All AI-generated SOAP notes REQUIRE physician review and approval before entry into patient records. This tool assists documentation but does not replace clinical judgment or medical decision-making.**
