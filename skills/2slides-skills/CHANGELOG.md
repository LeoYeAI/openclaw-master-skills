# Changelog - 2slides Skills Update

## Version 2.0.0 - 2026-02-10

Based on the updated API documentation from https://2slides.com/api.md

### New Features

#### 1. Custom PDF Slides Generation
- **New Script**: `scripts/create_pdf_slides.py`
- Generate custom-designed slides without needing a reference image
- AI creates design based on content and optional design specifications
- Same credit costs as create-like-this (100/200 credits per page)
- Supports all resolution options (1K, 2K, 4K)

**Usage:**
```bash
python scripts/create_pdf_slides.py --content "Sales Report" --design-spec "modern minimalist"
```

#### 2. AI Voice Narration
- **New Script**: `scripts/generate_narration.py`
- Add AI-generated voice narration to completed slides
- 30 voice options available (Puck, Aoede, Charon, and 27 more)
- Multi-speaker mode support
- 19 languages supported
- Cost: 210 credits per page (10 for text, 200 for audio)

**Usage:**
```bash
# List voices
python scripts/generate_narration.py --list-voices

# Generate narration
python scripts/generate_narration.py --job-id "abc-123" --voice "Aoede" --multi-speaker
```

#### 3. Download Export (Free)
- **New Script**: `scripts/download_slides_pages_voices.py`
- Download slides as PNG images
- Download voice narrations as WAV files
- Includes transcripts
- **Completely FREE** - no credit cost
- Download URLs valid for 1 hour

**Usage:**
```bash
python scripts/download_slides_pages_voices.py --job-id "abc-123" --output slides.zip
```

### Documentation Updates

#### SKILL.md
- Added Section 3: Custom PDF Generation workflow
- Added Section 5: Voice Narration workflow with voice options
- Added Section 6: Download Export workflow
- Updated workflow decision tree with new features
- Added rate limits section (Fast PPT: 10/min, Nano Banana: 6/min)
- Updated credit costs across all endpoints
- Added download URL expiration notice (1 hour)
- Enhanced error handling with specific error codes (INSUFFICIENT_CREDITS, INVALID_JOB_ID, RATE_LIMIT_EXCEEDED)
- Added polling recommendations (20-30 seconds)

#### api-reference.md
- Added Section 3: Create PDF Slides endpoint documentation
- Added Section 4: Generate Narration endpoint documentation
- Added Section 5: Download Slides Pages and Voices endpoint documentation
- Updated credit costs:
  - Fast PPT: 1 credit per slide (was 10)
  - Voice narration: 210 credits per page
  - Download: FREE
- Added rate limits per endpoint
- Added download URL expiration notice
- Enhanced error codes section
- Updated job status response to include narration status

#### mcp-integration.md
- Added documentation for 3 new MCP tools:
  - `slides_create_pdf_slides`
  - `slides_generate_narration`
  - `slides_download_pages_voices`
- Added note about requiring MCP server update
- Added voice options list
- Updated job status response format

#### README.md
- Updated Features section with 3 new features
- Added new scripts to Command Reference
- Expanded Generation Modes section
- Updated rate limits documentation
- Updated version to 2.0.0 with What's New section
- Enhanced Quick Start examples

### Technical Improvements

#### New Scripts (All Executable)
1. **create_pdf_slides.py** (5.5KB)
   - Custom PDF slide generation
   - Design specification support
   - Full parameter validation
   - Dynamic timeout calculation

2. **generate_narration.py** (5.4KB)
   - 30 voice options with --list-voices
   - Multi-speaker mode
   - Language selection
   - Job ID validation

3. **download_slides_pages_voices.py** (3.7KB)
   - ZIP download with progress
   - File size reporting
   - Custom output path support
   - Error handling

#### Enhanced Error Handling
- Added specific error codes from API
- Better rate limit messages
- UUID format validation for Nano Banana jobs
- Download URL expiration warnings

### Breaking Changes
None - all existing functionality remains backward compatible.

### Migration Guide
No migration needed. All new features are additive. Existing scripts and workflows continue to work as before.

### Credits & Costs Summary

| Feature | Cost |
|---------|------|
| Fast PPT (theme-based) | 10 credits/page |
| Nano Banana 1K/2K (image/custom) | 100 credits/page |
| Nano Banana 4K | 200 credits/page |
| Voice Narration | 210 credits/page |
| Download Export | **FREE** |

### Purchasing Credits

**Credit Packages** (up to 20% off promotion):
- 2,000 credits: $5.00
- 4,000 credits: $9.50 (5% off)
- 10,000 credits: $22.50 (10% off)
- 20,000 credits: $42.50 (15% off)
- 40,000 credits: $80.00 (20% off)

**Key Benefits:**
- 500 free credits for new users
- Credits never expire
- No subscriptions required
- Purchase at: https://2slides.com/pricing

### Rate Limits

| Endpoint | Limit |
|----------|-------|
| Fast PPT (generate) | 10 requests/min |
| Nano Banana (create-like-this, create-pdf-slides) | 6 requests/min |
| Voice Narration | 6 requests/min |
| Download | No limit |

### Files Modified

#### Updated Files
- `SKILL.md` - Major update with 3 new sections
- `references/api-reference.md` - Added 3 new endpoints
- `references/mcp-integration.md` - Added 3 new MCP tools
- `README.md` - Updated features, commands, examples

#### New Files
- `scripts/create_pdf_slides.py` - Custom PDF generation
- `scripts/generate_narration.py` - Voice narration
- `scripts/download_slides_pages_voices.py` - Export download
- `CHANGELOG.md` - This file

#### Unchanged Files
- `scripts/generate_slides.py` - No changes needed
- `scripts/search_themes.py` - No changes needed
- `scripts/get_job_status.py` - No changes needed (works with narration status)
- `.gitignore` - No changes needed

### Testing

All scripts tested and verified:
- ✅ `create_pdf_slides.py --help` - Working
- ✅ `generate_narration.py --list-voices` - Working (30 voices listed)
- ✅ `download_slides_pages_voices.py --help` - Working
- ✅ All scripts executable with proper permissions
- ✅ Help output formatted correctly

### Next Steps

To use the new features:

1. **Custom PDF Slides**: No additional setup needed
2. **Voice Narration**:
   - Generate slides first
   - Get job ID
   - Run narration script with job ID
   - Poll for completion
3. **Download Export**:
   - Complete slides (and optionally narration)
   - Run download script with job ID
   - Extract ZIP archive

### Support

- API Documentation: https://2slides.com/api
- Pricing & Credits: https://2slides.com/pricing
- Skill Documentation: See SKILL.md
- API Reference: See references/api-reference.md
- MCP Setup: See references/mcp-integration.md

### Important Notes

**Credit Cost Correction:** The Fast PPT endpoint costs **10 credits per page** (not 1 credit per slide as initially documented). This has been corrected throughout all documentation based on official pricing at https://2slides.com/pricing.
