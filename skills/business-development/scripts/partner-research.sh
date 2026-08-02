#!/bin/bash
# partner-research.sh - Quick partner research and profile generation
# Usage: ./partner-research.sh <company_name> [--profile]

BD_DIR="${HOME}/.openclaw/workspace/business-development"
PARTNERS_DIR="$BD_DIR/partners"
TEMPLATE="$BD_DIR/templates/partner-profile.md"

mkdir -p "$PARTNERS_DIR"

show_help() {
    echo "Partner Research Tool"
    echo "====================="
    echo ""
    echo "Usage:"
    echo "  $0 <company_name>           - Show research checklist"
    echo "  $0 <company_name> --profile - Create partner profile"
    echo ""
    echo "Examples:"
    echo "  $0 'Acme Corp'"
    echo "  $0 'Acme Corp' --profile"
}

research_checklist() {
    local company="$1"
    
    echo "🔍 Research Checklist for: $company"
    echo "===================================="
    echo ""
    echo "## Company Research"
    echo "- [ ] Visit website: https://www.google.com/search?q=$company"
    echo "- [ ] Check Crunchbase/LinkedIn for company info"
    echo "- [ ] Look for recent news/press releases"
    echo "- [ ] Identify key products/services"
    echo "- [ ] Understand their target market"
    echo ""
    echo "## People Research"
    echo "- [ ] Find decision makers on LinkedIn"
    echo "- [ ] Look for mutual connections"
    echo "- [ ] Check their recent posts/activity"
    echo "- [ ] Find email pattern (use Hunter.io or similar)"
    echo ""
    echo "## Partnership Fit"
    echo "- [ ] What could we offer them?"
    echo "- [ ] What could they offer us?"
    echo "- [ ] Do they have existing partnerships like ours?"
    echo "- [ ] What's the timing like for them?"
    echo ""
    echo "## Competition"
    echo "- [ ] Who are their competitors?"
    echo "- [ ] Do they work with any of our competitors?"
    echo ""
    echo "Useful Links:"
    echo "  - LinkedIn: https://www.linkedin.com/search/results/companies/?keywords=$company"
    echo "  - Crunchbase: https://www.crunchbase.com/textsearch?q=$company"
    echo "  - Google News: https://news.google.com/search?q=$company"
}

create_profile() {
    local company="$1"
    local filename=$(echo "$company" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')
    local profile_file="$PARTNERS_DIR/${filename}.md"
    
    if [ -f "$TEMPLATE" ]; then
        sed "s/\[Company Name\]/$company/g" "$TEMPLATE" > "$profile_file"
    else
        cat > "$profile_file" << EOF
# Partner Profile: $company

## Overview
- **Company:** $company
- **Website:** 
- **Industry:** 
- **Size:** 
- **Founded:** 
- **HQ:** 

## Key Contacts
- **Primary:** 
- **Secondary:** 

## Their Business
- **What they do:** 
- **Target customers:** 
- **Key products:** 
- **Competitive advantage:** 

## Partnership Opportunity
- **Type:** 
- **Value to them:** 
- **Value to us:** 
- **Synergy:** 

## Qualification (PARTNER Score)
- Potential: /10
- Alignment: /10
- Reach: /10
- Timing: /10
- Need: /10
- Experience: /10
- Risk: /10
- **Total:** /70

## Research Notes


## Activity Log
| Date | Activity | Notes |
|------|----------|-------|
| $(date +%Y-%m-%d) | Created | Initial profile |

## Status
- **Current stage:** Research
- **Last contact:** N/A
- **Next action:** Complete research
EOF
    fi
    
    echo "✅ Partner profile created: $profile_file"
    echo ""
    echo "Next steps:"
    echo "  1. Fill in the profile with your research"
    echo "  2. Calculate PARTNER score"
    echo "  3. Add to pipeline if score > 50"
}

# Parse arguments
if [ -z "$1" ]; then
    show_help
    exit 0
fi

COMPANY="$1"
CREATE_PROFILE=false

if [ "$2" = "--profile" ]; then
    CREATE_PROFILE=true
fi

if [ "$CREATE_PROFILE" = true ]; then
    create_profile "$COMPANY"
else
    research_checklist "$COMPANY"
fi
