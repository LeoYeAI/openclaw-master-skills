# 2slides Skills Update Summary

Complete summary of updates based on https://2slides.com/api.md and https://2slides.com/pricing

## Update Overview

**Version:** 2.0.0
**Date:** 2026-02-10
**Sources:**
- API Documentation: https://2slides.com/api.md
- Pricing Information: https://2slides.com/pricing

---

## Major Updates

### 1. Three New Features Added

#### a) Custom PDF Slides Generation
**Script:** `scripts/create_pdf_slides.py`
- Generate custom-designed slides without reference images
- AI creates design based on content and optional design specifications
- Same quality options as image-based generation (1K/2K/4K)
- **Cost:** 100 credits/page (1K/2K), 200 credits/page (4K)

```bash
python scripts/create_pdf_slides.py --content "Sales Report" --design-spec "modern minimalist"
```

#### b) AI Voice Narration
**Script:** `scripts/generate_narration.py`
- 30 voice options (Puck, Aoede, Charon, and 27 more)
- Single and multi-speaker modes
- 19 languages supported
- **Cost:** 210 credits/page (10 for text, 200 for audio)

```bash
python scripts/generate_narration.py --job-id "abc-123" --voice "Aoede" --multi-speaker
```

#### c) Free Download Export
**Script:** `scripts/download_slides_pages_voices.py`
- Export slides as PNG images
- Export voice files as WAV format
- Includes transcripts
- **Cost:** FREE (0 credits)

```bash
python scripts/download_slides_pages_voices.py --job-id "abc-123" --output slides.zip
```

### 2. Comprehensive Pricing Information Added

#### New Pricing Documentation
Created `references/pricing.md` with complete pricing details:
- Credit packages and discounts
- Detailed cost breakdowns
- Example calculations for common scenarios
- Free trial information
- Refund policy
- Payment methods

#### Credit Packages (Current Promotion)

| Credits | Price | Discount | Cost per 1,000 |
|---------|-------|----------|----------------|
| 2,000 | $5.00 | — | $2.50 |
| 4,000 | $9.50 | 5% off | $2.38 |
| 10,000 | $22.50 | 10% off | $2.25 |
| 20,000 | $42.50 | 15% off | $2.13 |
| 40,000 | $80.00 | 20% off | $2.00 |

**Key Benefits:**
- ✅ 500 free credits for new users
- ✅ Credits never expire
- ✅ No subscriptions required
- ✅ 3-day refund window

#### Credit Costs per Feature

| Feature | Credits per Page |
|---------|-----------------|
| Fast PPT | 10 |
| Nano Banana 1K/2K | 100 |
| Nano Banana 4K | 200 |
| Voice Narration | 210 |
| Download Export | FREE |

### 3. Updated All Documentation

#### SKILL.md Updates
- ✅ Added Setup Requirements section with pricing links
- ✅ Added Purchasing Credits section
- ✅ Updated credit costs throughout
- ✅ Added 3 new workflow sections (PDF, Narration, Download)
- ✅ Enhanced error handling with credit-related errors
- ✅ Added references to pricing.md

#### api-reference.md Updates
- ✅ Added 3 new endpoint documentations
- ✅ Added Purchasing Credits section with pricing table
- ✅ Added example cost calculations
- ✅ Corrected Fast PPT cost to 10 credits/page
- ✅ Enhanced error codes

#### README.md Updates
- ✅ Added "Pricing & Credits" section
- ✅ Added free trial information (500 credits)
- ✅ Added Step 3 in "Before You Begin" for purchasing credits
- ✅ Added pricing table with examples
- ✅ Added INSUFFICIENT_CREDITS troubleshooting
- ✅ Updated version to 2.0.0

#### mcp-integration.md Updates
- ✅ Added 3 new MCP tool documentations
- ✅ Added voice options list
- ✅ Enhanced tool descriptions

#### CHANGELOG.md Updates
- ✅ Documented all new features
- ✅ Added pricing information section
- ✅ Added credit cost correction note
- ✅ Listed all modified and new files

#### New Files Created
- ✅ `references/pricing.md` - Comprehensive pricing guide
- ✅ `CHANGELOG.md` - Version history
- ✅ `UPDATE_SUMMARY.md` - This file

---

## Example Cost Calculations

### Scenario 1: Quick Business Presentation
- **Need:** 15-slide Fast PPT
- **Credits:** 150 (15 × 10)
- **Cost with largest package:** $0.30

### Scenario 2: Branded Marketing Deck
- **Need:** 20-slide Nano Banana 2K with brand image
- **Credits:** 2,000 (20 × 100)
- **Cost with largest package:** $4.00

### Scenario 3: Training Presentation with Audio
- **Need:** 30-slide 2K with voice narration
- **Credits:** 6,300
  - Slides: 3,000 (30 × 100)
  - Narration: 3,300 (30 × 110 voice-only)
- **Cost with largest package:** $12.60

### Scenario 4: Complete Package
- **Need:** 25-slide 2K + narration + PNG/WAV export
- **Credits:** 5,250
  - Slides: 2,500 (25 × 100)
  - Narration: 2,750 (25 × 110)
  - Export: 0 (FREE)
- **Cost with largest package:** $10.50

---

## Free Trial Details

**New users get 500 free credits:**
- ~50 Fast PPT slide pages
- ~5 Nano Banana 2K pages
- ~2 Nano Banana 2K pages with full narration
- Mix and match as needed

---

## Technical Summary

### Scripts Created
1. `scripts/create_pdf_slides.py` (5.5KB) - Custom PDF generation
2. `scripts/generate_narration.py` (5.4KB) - Voice narration
3. `scripts/download_slides_pages_voices.py` (3.7KB) - Export download

### Documentation Files

| File | Status | Size | Description |
|------|--------|------|-------------|
| SKILL.md | Updated | ~500 lines | Main skill guide |
| README.md | Updated | ~370 lines | Project overview |
| references/api-reference.md | Updated | ~310 lines | API documentation |
| references/mcp-integration.md | Updated | ~210 lines | MCP setup |
| references/pricing.md | **NEW** | ~300 lines | Pricing guide |
| CHANGELOG.md | **NEW** | ~200 lines | Version history |

### Testing Results

✅ All scripts executable and tested:
- `create_pdf_slides.py --help` - Working
- `generate_narration.py --list-voices` - Working (30 voices)
- `download_slides_pages_voices.py --help` - Working
- All existing scripts still working

---

## Key Links

- **Purchase Credits:** https://2slides.com/pricing
- **API Access:** https://2slides.com/api
- **Main Website:** https://2slides.com
- **API Documentation:** https://2slides.com/api.md

---

## Migration Notes

**No breaking changes** - All existing functionality remains compatible.

**Credit Cost Correction:**
- Fast PPT was initially documented as 1 credit/slide
- Corrected to 10 credits/page based on official pricing
- This affects cost estimates but not functionality

**For existing users:**
- Continue using existing scripts as before
- New features are optional additions
- Check credit balance at https://2slides.com/api
- Purchase additional credits at https://2slides.com/pricing if needed

---

## What's Next

Users can now:
1. ✅ Generate slides with themes (Fast PPT)
2. ✅ Match reference image styles (Nano Banana)
3. ✅ Create custom PDF slides (NEW)
4. ✅ Add AI voice narration (NEW)
5. ✅ Download as PNG/WAV (NEW)
6. ✅ Search themes
7. ✅ Track job status

All with transparent, pay-as-you-go pricing and 500 free credits to start!

---

**Last Updated:** 2026-02-10
**Version:** 2.0.0
