---
name: greek-document-ocr
description: Greek-language OCR using Tesseract. Processes scanned invoices, receipts, and government documents. Local processing, no cloud APIs.
version: 1.0.0
author: openclaw-greek-accounting
homepage: https://github.com/satoshistackalotto/openclaw-greek-accounting
tags: ["greek", "accounting", "ocr", "document-processing", "greek-language"]
metadata: {"openclaw": {"requires": {"bins": ["jq", "tesseract"], "env": ["OPENCLAW_DATA_DIR"]}, "optional_env": {"QUICKBOOKS_IMPORT_DIR": "Directory for QuickBooks-compatible OCR export files", "XERO_API_KEY": "Xero API key for direct OCR result push"}, "notes": "Requires Tesseract OCR with Greek language pack (tesseract-ocr-ell). All processing is local — no cloud OCR APIs. Optional QuickBooks/Xero export formats available for accounting software integration."}}
---

# Greek Document OCR

This skill provides advanced Greek language optical character recognition and document processing capabilities, specifically designed for Greek business documents, invoices, receipts, and handwritten materials commonly found in Greek accounting workflows.


## Setup

```bash
export OPENCLAW_DATA_DIR="/data"

# Install Tesseract OCR with Greek language support
sudo apt install tesseract-ocr tesseract-ocr-ell
which jq || sudo apt install jq

mkdir -p $OPENCLAW_DATA_DIR/ocr/{incoming/{scanned,photos,government},output/{text-extracted,structured-data}}
```

All OCR processing happens locally using Tesseract — no cloud OCR APIs are used. No credentials required.


## Core Philosophy

- **Greek Language Excellence**: Superior recognition of Greek characters, accents, and business terminology
- **OpenClaw Integration**: Built to enhance existing `deepread` skill with Greek-specific capabilities
- **Business Document Focus**: Optimized for invoices, receipts, contracts, and government forms
- **Production Accuracy**: High-precision text extraction suitable for automated accounting workflows
- **Handwritten Support**: Advanced recognition of handwritten Greek text and signatures

## OpenClaw Commands

### Core OCR Operations
```bash
# Primary Greek document processing
openclaw ocr process-greek --input-dir /data/ocr/incoming/scanned/ --enhance-greek-chars
openclaw ocr batch-process --greek-language --confidence-threshold 0.95 --auto-classify
openclaw ocr extract-invoices --greek-format --vat-detection --amount-parsing
openclaw ocr process-receipts --greek-business --expense-categorization

# Integration with existing deepread skill
openclaw ocr enhance-deepread --greek-language-pack --improve-accuracy
openclaw ocr greek-preprocessing --image-enhancement --character-optimization
openclaw ocr validate-extraction --greek-language --business-rules

# Specialized Greek document types
openclaw ocr process-handwritten --greek-cursive --signature-detection
openclaw ocr government-forms --aade-forms --efka-documents --municipal-papers
openclaw ocr process-contracts --greek-legal --clause-extraction --signature-verification
```

### Advanced Greek Text Processing
```bash
# Greek language enhancement and correction
openclaw ocr correct-greek --spell-check --accent-correction --business-terminology
openclaw ocr standardize-text --greek-formatting --currency-amounts --date-formats
openclaw ocr extract-entities --greek-names --addresses --vat-numbers --amounts

# Document intelligence and categorization
openclaw ocr classify-documents --greek-business-types --confidence-scoring
openclaw ocr extract-structured-data --invoices --receipts --contracts --forms
openclaw ocr generate-searchable-pdf --greek-text-layer --preserve-formatting
```

### Quality Control & Validation
```bash
# Accuracy monitoring and improvement
openclaw ocr accuracy-test --greek-documents --known-text-samples
openclaw ocr confidence-analysis --character-level --word-level --document-level
openclaw ocr manual-review --low-confidence --flagged-documents --greek-verification

# Integration and export
openclaw ocr export-accounting --format csv --greek-standards
openclaw ocr export-accounting --target quickbooks --xero --greek-formats  # Optional: accounting software formats
openclaw ocr integrate-banking --match-bank-transactions --reference-extraction
openclaw ocr coordinate-compliance --vat-analysis --tax-document-processing
```

## Greek Language Processing Architecture

### Greek Character Recognition Enhancement
```yaml
Greek_Character_Optimization:
  alphabet_coverage:
    uppercase: "ΑΒΓΔΕ΀“ΗΜΙΡ΀ºΜΝξθΠΡΣΤΥΦΧΨΩ"
    lowercase: "αβγδεζηθικλμνξοπρσπžυπ π¡ψπ°"
    accented_characters: "άέήίςύϽΐΰ"
    special_characters: "πš" # Final sigma
    punctuation: "·" # Greek middle dot
    
  character_enhancement:
    similar_character_disambiguation:
      - "Α vs A (Latin A)"
      - "Β vs B (Latin B)" 
      - "Ε vs E (Latin E)"
      - "Η vs H (Latin H)"
      - "Ι vs I (Latin I)"
      - "Ρ vs K (Latin K)"
      - "Μ vs M (Latin M)"
      - "Ν vs N (Latin N)"
      - "θ vs O (Latin O)"
      - "Π vs P (Latin P)"
      - "Ρ vs P (Latin P confusion)"
      - "Τ vs T (Latin T)"
      - "Υ vs Y (Latin Y)"
      - "Χ vs X (Latin X)"
      
  accent_recognition:
    acute_accents: "ά έ ή ί ς ύ Ͻ"
    diaeresis: "Ϡ π¹" 
    combined_accents: "ΐ ΰ"
    accent_correction: "Auto-correct missing or incorrect accents"
```

### Greek Business Document Intelligence
```yaml
Greek_Business_Document_Types:
  invoices:
    greek_keywords: ["ΤΙΜθ΀ºθΓΙθ", "ΑΠθΔΕΙξΗ", "ΠΑΡΑΣΤΑΤΙΡθ"]
    required_elements: ["ΑΦΜ", "ΦΠΑ", "ΗΜΕΡθΜΗΝΙΑ", "ΠθΣθ"]
    amount_patterns: ["‚¬\\d+[.,]\\d+", "\\d+[.,]\\d+\\s*‚¬", "\\d+[.,]\\d+\\s*EUR"]
    vat_patterns: ["ΦΠΑ\\s*\\d+%", "VAT\\s*\\d+%", "24%", "13%", "6%"]
    
  receipts:
    types: ["ΑΠθΔΕΙξΗ ΀ºΙΑΝΙΡΗΣ", "ΑΠθΔΕΙξΗ ΠΑΡθΧΗΣ ΥΠΗΡΕΣΙΩΝ"]
    essential_info: ["ΗΜΕΡθΜΗΝΙΑ", "ΩΡΑΗ", "ΠθΣθ", "ΑΦΜ ΡΑΤΑΣΤΗΜΑΤθΣ"]
    pos_indicators: ["POS", "ΡΑΡΤΑ", "ΜΕΤΡΗΤΑ"]
    
  government_forms:
    aade_forms: ["Ε1", "Ε3", "ΦΠΑ", "ΕΝΦΙΑ"]
    efka_forms: ["Α.Π.Δ.", "ΑΠΑ", "ΕΦΡ", "ΕΡΓθΔθΤΙΡΕΣ ΕΙΣΦθΡΕΣ"]
    municipal_forms: ["ΔΗΜθΤΙΡθΣ ΦθΡθΣ", "ΤΕ΀ºθΣ ΡΑΜΑΡΙθΤΗΤΑΣ"]
    
  contracts:
    contract_types: ["ΣΥΜΒΑΣΗ", "ΣΥΜΦΩΝΙΑ", "ΠΑΡΑΧΩΡΗΣΗ"]
    key_clauses: ["ΑΝΤΙΡΕΙΜΕΝθ", "ΤΙΜΗ", "ΔΙΑΡΡΕΙΑ", "ΥΠθΧΡΕΩΣΕΙΣ"]
    signature_areas: ["ΥΠθΓΡΑΦΗ", "ΣΦΡΑΓΙΔΑ", "ΗΜΕΡθΜΗΝΙΑ ΥΠθΓΡΑΦΗΣ"]
```

### OpenClaw File Processing Integration
```yaml
Greek_OCR_File_Structure:
  input_processing:
    - /data/ocr/incoming/scanned/         # Scanned documents (PDF, JPG, PNG, TIFF)
    - /data/ocr/incoming/photos/          # Mobile phone document photos
    - /data/ocr/incoming/handwritten/     # Handwritten Greek documents
    - /data/ocr/incoming/government/      # Government forms and official documents
    
  processing_workspace:
    - /data/ocr/preprocessing/enhanced/   # Image enhancement and optimization
    - /data/ocr/processing/greek-ocr/     # Greek language OCR processing
    - /data/ocr/processing/validation/    # Text validation and correction
    - /data/ocr/processing/classification/# Document type classification
    
  output_delivery:
    - /data/ocr/output/text-extracted/      # Clean extracted text files
    - /data/ocr/output/structured-data/     # Structured business data (JSON)
    - /data/ocr/output/searchable-pdf/      # PDFs with Greek text layer
    - /data/ocr/output/accounting-ready/    # Data ready for accounting integration
```

## Enhanced Greek OCR Processing Pipeline

### Pre-Processing Optimization for Greek Documents
```yaml
Image_Enhancement_Pipeline:
  step_1_assessment:
    command: "openclaw ocr assess-quality --greek-text --character-density"
    functions: ["Image quality analysis", "Greek text detection", "Optimal processing path selection"]
    
  step_2_enhancement:
    command: "openclaw ocr enhance-image --greek-characters --contrast-optimization"
    functions: ["Noise reduction", "Contrast enhancement", "Greek character sharpening"]
    
  step_3_preprocessing:
    command: "openclaw ocr preprocess --deskew --border-removal --greek-layout"
    functions: ["Document alignment", "Border detection", "Greek text layout analysis"]
    
Greek_Specific_Enhancements:
  character_enhancement:
    accent_sharpening: "Enhance accent mark visibility"
    character_separation: "Improve separation of connected Greek letters"
    font_optimization: "Optimize for common Greek fonts (Times New Roman Greek, Arial Greek)"
    
  layout_analysis:
    greek_reading_order: "Right-to-left aware processing for mixed text"
    column_detection: "Handle Greek newspaper and document column layouts"
    table_recognition: "Greek table headers and structure recognition"
```

### Advanced Greek Text Extraction
```yaml
Greek_OCR_Engine_Configuration:
  primary_ocr_engine:
    base: "OpenClaw deepread skill enhancement"
    greek_language_model: "el-GR with business terminology"
    confidence_threshold: 0.95
    character_whitelist: "Greek alphabet + Latin numbers + common punctuation"
    
  secondary_engines:
    tesseract_greek: "Fallback for challenging documents"
    handwriting_recognition: "Specialized for Greek cursive and signatures"
    form_processing: "Template-based for government forms"
    
  post_processing:
    spell_checking: "Greek business dictionary with 50,000+ terms"
    context_correction: "Business context-aware text correction"
    accent_normalization: "Standard Greek accent placement"
    
Text_Validation_Rules:
  greek_business_validation:
    vat_number_format: "EL followed by 9 digits"
    date_validation: "dd/MM/yyyy or dd-MM-yyyy Greek formats"
    amount_validation: "Greek currency formatting (1.234,56 ‚¬)"
    address_validation: "Greek address patterns and postal codes"
    
  confidence_scoring:
    character_confidence: "Per-character accuracy scoring"
    word_confidence: "Greek word validation against dictionary"
    context_confidence: "Business context appropriateness"
    overall_confidence: "Weighted average with manual review threshold"
```

## Handwritten Greek Document Processing

### Greek Cursive Recognition
```yaml
Handwritten_Greek_Support:
  cursive_patterns:
    connected_letters: "Common Greek letter combinations (ου, ει, αι, etc.)"
    character_variations: "Individual handwriting style adaptation"
    historical_forms: "Recognition of older Greek handwriting styles"
    
  signature_recognition:
    greek_signatures: "Greek name pattern recognition"
    official_stamps: "Government and business stamp recognition"
    verification_marks: "Legal document verification signatures"
    
  enhancement_techniques:
    contrast_boosting: "Improve handwritten text visibility"
    stroke_analysis: "Greek letter stroke pattern recognition"
    word_segmentation: "Separate connected handwritten Greek words"
    
Handwriting_Processing_Workflow:
  preprocessing:
    - "Handwriting-specific image enhancement"
    - "Stroke width normalization"  
    - "Background noise removal"
    
  recognition:
    - "Greek cursive letter recognition"
    - "Word boundary detection"
    - "Context-based correction"
    
  validation:
    - "Greek word dictionary validation"
    - "Business context verification"
    - "Manual review flagging for low confidence"
```

## Greek Document Classification Intelligence

### Automated Document Type Recognition
```yaml
Greek_Document_Classifier:
  invoice_detection:
    visual_cues: ["ΤΙΜθ΀ºθΓΙθ header", "Company logos", "VAT number placement"]
    text_patterns: ["ΑΦΜ patterns", "Invoice numbering", "Due date formats"]
    layout_features: ["Table structures", "Total amount positioning", "VAT breakdowns"]
    confidence_threshold: 0.92
    
  receipt_detection:
    visual_cues: ["POS receipt format", "Thermal paper patterns", "Store logos"]
    text_patterns: ["ΑΠθΔΕΙξΗ", "Date/time stamps", "Payment method indicators"]
    layout_features: ["Linear item listing", "Total at bottom", "Change calculation"]
    confidence_threshold: 0.90
    
  government_form_detection:
    visual_cues: ["Government letterheads", "Official stamps", "Form numbers"]
    text_patterns: ["Ε΀º΀ºΗΝΙΡΗ ΔΗΜθΡΡΑΤΙΑ", "Ministry names", "Official references"]
    layout_features: ["Standard form layouts", "Checkbox structures", "Signature lines"]
    confidence_threshold: 0.95
    
  contract_detection:
    visual_cues: ["Multi-page documents", "Legal formatting", "Signature pages"]
    text_patterns: ["ΣΥΜΒΑΣΗ", "Legal terminology", "Clause numbering"]
    layout_features: ["Paragraph structures", "Section headers", "Signature blocks"]
    confidence_threshold: 0.88
```

### Greek Business Data Extraction
```yaml
Structured_Data_Extraction:
  invoice_data_extraction:
    company_info:
      - supplier_name: "Extract from header/footer"
      - supplier_vat: "ΑΦΜ: pattern recognition"
      - supplier_address: "Greek address format extraction"
      
    transaction_info:
      - invoice_number: "Αριθμςπš πžιμολογίου pattern"
      - invoice_date: "Greek date format recognition"
      - due_date: "Ημερομηνία πληρπ°μήπš extraction"
      
    financial_info:
      - line_items: "Table extraction with Greek descriptions"
      - vat_amounts: "ΦΠΑ calculation validation"
      - total_amount: "ΣΥΝθ΀ºθ or TOTAL pattern recognition"
      
  receipt_data_extraction:
    merchant_info:
      - business_name: "Store name from receipt header"
      - vat_number: "ΑΦΜ from receipt footer"
      - location: "Address or branch information"
      
    transaction_info:
      - date_time: "Greek date/time format extraction"
      - payment_method: "ΡΑΡΤΑ, ΜΕΤΡΗΤΑ, etc."
      - receipt_number: "Αριθμςπš απςδειξηπš"
      
    items_and_amounts:
      - purchased_items: "Item list with Greek descriptions"
      - individual_prices: "Price extraction per item"
      - vat_breakdown: "VAT rate identification (24%, 13%, 6%)"
      - total_amount: "Final amount with currency"
```

## Quality Control & Accuracy Optimization

### Greek OCR Accuracy Monitoring
```yaml
Quality_Control_System:
  accuracy_metrics:
    character_accuracy: "Greek character recognition rate >98%"
    word_accuracy: "Greek word recognition rate >95%"
    document_accuracy: "Complete document processing rate >92%"
    
  confidence_monitoring:
    low_confidence_threshold: "<0.85 flags for manual review"
    medium_confidence: "0.85-0.92 requires validation"
    high_confidence: ">0.92 auto-processed"
    
  error_pattern_analysis:
    common_errors: "Track frequent Greek OCR mistakes"
    improvement_feedback: "Learn from manual corrections"
    model_updates: "Continuous improvement based on corrections"
    
Manual_Review_Workflow:
  flagging_criteria:
    - "Greek accent recognition issues"
    - "Similar character confusion (Α vs A)"
    - "Handwritten text with low confidence"
    - "Complex table structures"
    - "Damaged or poor quality documents"
    
  review_interface:
    original_image: "Side-by-side with extracted text"
    character_highlighting: "Mark uncertain characters"
    greek_keyboard: "Easy Greek text correction interface"
    validation_tools: "Business rule checking (VAT numbers, dates)"
```

### Integration with Greek Accounting Workflows
```yaml
Accounting_Integration:
  invoice_processing:
    workflow: "OCR †’ Validation †’ Accounting Software Export"
    vat_verification: "Cross-check extracted VAT with business rules"
    amount_validation: "Verify calculated totals match extracted amounts"
    
  expense_categorization:
    greek_expense_categories: "Map to Greek chart of accounts"
    vat_rate_assignment: "Automatic VAT rate based on expense type"
    supplier_recognition: "Match suppliers to existing accounting records"
    
  compliance_support:
    audit_trail: "Maintain OCR processing history"
    document_retention: "Store original images with extracted data"
    accuracy_reporting: "Generate accuracy reports for auditors"
```

## Production Deployment Features

### Performance Optimization for Greek Documents
```bash
# Performance monitoring and optimization
openclaw ocr performance-monitor --greek-processing --throughput-analysis
openclaw ocr optimize-batch --large-documents --parallel-processing
openclaw ocr cache-optimization --greek-models --frequent-terms

# Scalability commands
openclaw ocr scale-processing --concurrent-documents 5 --memory-optimization
openclaw ocr distributed-ocr --worker-nodes --greek-language-models
openclaw ocr load-balancing --priority-queues --document-types
```

### Greek Language Model Management
```yaml
Model_Management:
  greek_language_models:
    business_terminology: "50,000+ Greek business terms"
    accounting_vocabulary: "Specialized accounting and tax terminology"
    government_terminology: "Official government document language"
    
  model_updates:
    automatic_updates: "Monthly model improvements"
    custom_training: "Client-specific terminology learning"
    accuracy_feedback: "Continuous learning from corrections"
    
  deployment_options:
    cloud_models: "High accuracy, internet required"
    local_models: "Good accuracy, offline capability"
    hybrid_mode: "Cloud for complex, local for routine"
```

## Usage Examples for Greek Company Testing

### Daily Document Processing
```bash
# Morning document processing workflow
$ openclaw ocr morning-batch --process-overnight --greek-priority

📀ž Greek OCR Processing Summary - February 19, 2026:

📊 Documents Processed: 23 total
✅ Invoices: 8 processed (avg confidence: 96.2%)
   - SUPPLIER A AE: Invoice #2026-0234, ‚¬1,234.56 ✅
   - ΠΡθΜΗΜΕΥΤΗΣ Β ΕΠΕ: Τιμολςγιο #456, ‚¬890.00 ✅
   
✅ Receipts: 12 processed (avg confidence: 94.8%)
   - Restaurant receipts: 4 (13% VAT detected)
   - Fuel receipts: 3 (24% VAT detected)
   - Office supplies: 5 (24% VAT detected)

⚠ï¸ Manual Review Required: 3 documents
   - Handwritten note (confidence: 78%)
   - Damaged invoice (confidence: 82%)
   - Complex government form (confidence: 84%)

📤 Accounting Export: 20 documents ready for CSV export import
💾 Searchable PDFs: 23 documents with Greek text layer created
```

### Complex Greek Document Processing
```bash
$ openclaw ocr process-complex --handwritten --government-forms --contracts

📀¹ Complex Greek Document Processing:

âœÂï¸ Handwritten Documents (5):
✅ Handwritten invoice corrections - ‚¬234.50 adjustment recognized
✅ Client note with payment instructions - "Πληρπ°μή σπžιπš 25/02" extracted
⚠ï¸ Signature verification needed - Legal contract signature page

ðŸÂ€ºï¸ Government Forms (3):
✅ AADE E1 Form - Individual tax data extracted completely
✅ EFKA contribution form - Employee data processed
✅ Municipal tax payment receipt - ‚¬456.78 payment confirmed

📀ž Contracts (2):
✅ Service contract - Key terms extracted (Duration: 12 months, ‚¬2,000/month)
⚠ï¸ Real estate contract - Complex legal clauses flagged for manual review

📊 Overall Success Rate: 91.3%
âÂ±ï¸ Processing Time: 4 minutes 32 seconds
ðŸ” Manual Review Items: 4 documents requiring attention
```

### Integration with Meta-Skill
```bash
# Meta-skill coordinated document processing
$ openclaw greek document-intelligence --scan-and-process --coordinate-all

# Behind the scenes coordination:
# 1. Greek OCR: Process scanned documents and photos
# 2. Banking Integration: Match receipts to bank transactions
# 3. Compliance AADE: Validate VAT rates and amounts
# 4. Email Processor: Send processing confirmations to clients
# 5. Accounting Workflows: Export to accounting software
# 6. Individual Taxes: Update personal expense tracking
```

### Accuracy Analysis and Improvement
```bash
$ openclaw ocr accuracy-report --greek-documents --monthly-analysis

📈 Greek OCR Accuracy Analysis - February 2026:

📊 Character Recognition:
✅ Greek Letters: 98.7% accuracy (target: >98%)
✅ Accented Characters: 97.2% accuracy (ά, έ, ή, etc.)
✅ Numbers/Currency: 99.4% accuracy (‚¬ amounts)
⚠ï¸ Handwritten Text: 89.3% accuracy (target: >90%)

📀¹ Document Type Accuracy:
✅ Printed Invoices: 96.8% complete extraction
✅ POS Receipts: 95.2% complete extraction  
✅ Government Forms: 94.1% complete extraction
⚠ï¸ Handwritten Notes: 85.7% complete extraction

🔧 Improvement Actions:
- Enhanced handwritten Greek cursive training scheduled
- Updated business terminology dictionary (+347 new terms)
- Improved accent recognition for damaged documents
- Added 3 new Greek receipt format templates

📈 Month-over-Month: +2.3% accuracy improvement
🎯 Next Target: 97% overall accuracy by March 2026
```

## Success Metrics for Greek OCR Deployment

A successful Greek OCR system should achieve:
- ✅ 98%+ accuracy for printed Greek business documents
- ✅ 95%+ accuracy for clear handwritten Greek text
- ✅ 90%+ accuracy for damaged or poor quality documents
- ✅ Complete integration with existing OpenClaw deepread skill
- ✅ Automatic Greek VAT rate and amount extraction
- ✅ Professional searchable PDF generation with Greek text layer
- ✅ Real-time processing suitable for daily business workflows
- ✅ Robust error handling and manual review workflow

Remember: This skill transforms OpenClaw into a production-ready Greek document processing system, enabling automated processing of all types of Greek business documents with high accuracy and intelligent data extraction suitable for Greek accounting workflows.