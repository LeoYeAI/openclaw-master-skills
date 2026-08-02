#!/bin/bash
# bd-init.sh - Initialize business development workspace
# Usage: ./bd-init.sh

BD_DIR="${HOME}/.openclaw/workspace/business-development"

echo "🚀 Initializing Business Development Workspace"
echo "=============================================="

# Create directory structure
mkdir -p "$BD_DIR"/{partners,research,proposals,pipeline,templates}

# Create partner directory readme
cat > "$BD_DIR/partners/README.md" << 'EOF'
# Partners Directory

Store partner profiles here as individual markdown files.

## Naming Convention
Use: `company-name.md`

## Template
Copy from `../templates/partner-profile.md`

## Stages
- 📋 Research
- 📤 Outreach
- 💬 Discussion
- 📝 Proposal
- 🤝 Negotiation
- ⚖️ Legal
- ✅ Active
EOF

# Create partner profile template
cat > "$BD_DIR/templates/partner-profile.md" << 'EOF'
# Partner Profile: [Company Name]

## Overview
- **Company:** 
- **Website:** 
- **Industry:** 
- **Size:** 
- **Founded:** 
- **HQ:** 

## Key Contacts
- **Primary:** [Name, Title, Email, LinkedIn]
- **Secondary:** 

## Their Business
- **What they do:** 
- **Target customers:** 
- **Key products:** 
- **Competitive advantage:** 

## Partnership Opportunity
- **Type:** [Integration/Reseller/Co-marketing/etc.]
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

## Status
- **Current stage:** Prospect
- **Last contact:** 
- **Next action:** 
EOF

# Create proposal template
cat > "$BD_DIR/templates/proposal.md" << 'EOF'
# Partnership Proposal: [Your Company] × [Partner Company]

## Executive Summary
[1 paragraph overview of the opportunity and mutual value]

---

## The Opportunity

### Market Context
[Brief market opportunity both companies can address]

### Why Now
[Timing factors that make this partnership timely]

---

## The Partnership

### Concept
[Clear description of what you're proposing]

### Value to [Partner]
1. 
2. 
3. 

### Value to [Your Company]
1. 
2. 
3. 

---

## How It Works

### Roles & Responsibilities
| Area | [Your Company] | [Partner] |
|------|----------------|-----------|
| | | |

### Timeline
- **Phase 1:** 
- **Phase 2:** 
- **Phase 3:** 

---

## Success Metrics
| Metric | Target | How Measured |
|--------|--------|--------------|
| | | |

---

## Next Steps
1. 
2. 

**Contact:**
[Name, Title, Email]
EOF

# Create pipeline tracker
cat > "$BD_DIR/pipeline/current.md" << 'EOF'
# BD Pipeline

## Summary
- Total opportunities: 0
- Pipeline value: $0
- Weighted value: $0

## By Stage

### 📋 Research
| Partner | Type | PARTNER Score | Next Action |
|---------|------|---------------|-------------|

### 📤 Outreach
| Partner | Type | Outreach # | Last Contact |
|---------|------|------------|--------------|

### 💬 Discussion
| Partner | Type | Est. Value | Next Meeting |
|---------|------|------------|--------------|

### 📝 Proposal
| Partner | Type | Proposal Date | Decision Expected |
|---------|------|---------------|-------------------|

### 🤝 Negotiation
| Partner | Type | Est. Value | Blocker |
|---------|------|------------|---------|

### ⚖️ Legal
| Partner | Type | Est. Value | Target Close |
|---------|------|------------|--------------|

## ✅ Active Partnerships
| Partner | Type | Started | Annual Value | Owner |
|---------|------|---------|--------------|-------|
EOF

# Create research templates
cat > "$BD_DIR/research/market-template.md" << 'EOF'
# Market Research: [Market/Industry]

## Executive Summary
[2-3 sentences on key findings]

## Market Size
- **TAM:** $
- **SAM:** $
- **SOM:** $
- **CAGR:** %

## Key Players
| Company | Market Share | Strengths | Weaknesses |
|---------|--------------|-----------|------------|
| | | | |

## Trends
1. **[Trend]:** [Impact]
2. **[Trend]:** [Impact]

## Opportunities
1. 
2. 

## Threats
1. 
2. 

## Recommendations
1. 
2. 

## Sources
- 
EOF

cat > "$BD_DIR/research/competitor-template.md" << 'EOF'
# Competitor Analysis: [Company Name]

## Overview
- **Company:** 
- **Website:** 
- **Founded:** 
- **Funding:** 
- **Employees:** 

## Product/Service
- **Core offering:** 
- **Key features:** 
- **Pricing:** 
- **Target customers:** 

## Strengths
1. 
2. 

## Weaknesses
1. 
2. 

## How We Compare
| Factor | Us | Them | Advantage |
|--------|-----|------|-----------|
| | | | |

## Recent Moves
- 

## Battlecard
- **When we win:** 
- **When we lose:** 
- **Key talking points:** 
EOF

echo "✅ Created: $BD_DIR/partners/"
echo "✅ Created: $BD_DIR/research/"
echo "✅ Created: $BD_DIR/proposals/"
echo "✅ Created: $BD_DIR/pipeline/current.md"
echo "✅ Created: $BD_DIR/templates/"
echo ""
echo "🎉 Business Development workspace ready!"
echo ""
echo "Quick start:"
echo "  1. Use templates/ for partner profiles and proposals"
echo "  2. Track opportunities in pipeline/current.md"
echo "  3. Store research in research/"
echo "  4. Keep partner profiles in partners/"
