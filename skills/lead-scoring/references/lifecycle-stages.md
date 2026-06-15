# Lifecycle Stages and Transition Criteria

## Overview

Lead lifecycle stages represent the progression of a prospect through your sales and marketing funnel. Each stage has specific entry/exit criteria, associated actions, and ownership responsibilities. This document defines the standard B2B lifecycle stages and their relationship to lead scoring.

## Lifecycle Stage Definitions

### 1. Visitor (Entry Point)
**Definition**: Someone who has visited your website or engaged with your content but hasn't provided contact information.

**Characteristics**:
- Anonymous web visitor
- Social media follower/engager
- Content consumer (no form fill)
- Event attendee (no contact capture)

**Score Range**: N/A (anonymous)
**Ownership**: Marketing
**Duration**: Indefinite

**Key Activities**:
- Website browsing
- Content consumption
- Social media engagement
- Paid ad interaction

**Transition Criteria**:
→ **Lead**: Provides contact information through any channel

---

### 2. Lead (Initial Contact)
**Definition**: Someone who has provided contact information but hasn't been qualified yet.

**Entry Criteria**:
- Contact information captured (email required)
- Initial engagement action completed
- Not yet scored or qualified

**Characteristics**:
- New to database
- Minimal behavioral data
- Unknown company/role information
- Early funnel activity

**Score Range**: 0-29 points
**Ownership**: Marketing
**Duration**: 0-30 days typically

**Key Activities**:
- Form submissions
- Content downloads
- Newsletter signups
- Contact page inquiries

**Automation Actions**:
- Welcome email sequence
- Progressive profiling
- Basic lead scoring
- Data enrichment attempts

**Transition Criteria**:
→ **Marketing Qualified Lead**: Score ≥30 AND recent activity
→ **Sales Qualified Lead**: Direct request for sales contact
→ **Customer**: Direct purchase (PLG/self-serve)

---

### 3. Marketing Qualified Lead (MQL)
**Definition**: A lead that has shown enough engagement and fit to warrant marketing nurturing and eventual sales consideration.

**Entry Criteria**:
- Lead score ≥30 points
- Company information available
- Job title/role identified
- Activity within last 30 days

**Characteristics**:
- Moderate demographic fit
- Consistent engagement pattern
- Consuming educational content
- Multiple touchpoints

**Score Range**: 30-69 points
**Ownership**: Marketing (with sales visibility)
**Duration**: 30-90 days typically

**Key Activities**:
- Regular content consumption
- Email engagement
- Website return visits
- Social media interaction

**Automation Actions**:
- Targeted nurturing campaigns
- Advanced content offers
- Event invitations
- Behavioral tracking intensifies

**Transition Criteria**:
→ **Sales Qualified Lead**: Score ≥70 AND qualification criteria met
→ **Lead**: Score drops below 30 for 60+ days
→ **Customer**: Self-serve purchase

**Qualification Checkpoints**:
- Budget confirmation
- Timeline identification
- Authority validation
- Need confirmation (BANT)

---

### 4. Sales Qualified Lead (SQL)
**Definition**: A lead that marketing has determined is ready for direct sales engagement based on scoring and qualification criteria.

**Entry Criteria**:
- Lead score ≥70 points
- BANT criteria partially met
- Demographic grade B+ or higher
- Recent high-intent activity

**Characteristics**:
- Strong demographic fit
- High engagement level
- Bottom-funnel content consumption
- Expressed buying interest

**Score Range**: 70-89 points
**Ownership**: Sales (with marketing support)
**Duration**: 14-60 days typically

**Key Activities**:
- Demo requests
- Pricing page visits
- Sales contact requests
- ROI calculator usage

**Sales Actions**:
- Initial qualification call
- Discovery conversation
- Needs assessment
- Stakeholder identification

**Transition Criteria**:
→ **Opportunity**: Qualified through sales process
→ **MQL**: Disqualified by sales, score maintained
→ **Lead**: Disqualified with score decrease

**Disqualification Reasons**:
- No budget
- No timeline
- Wrong decision maker
- Poor fit for solution

---

### 5. Opportunity
**Definition**: A qualified prospect that has entered the formal sales process with identified need, budget, timeline, and decision-making process.

**Entry Criteria**:
- Sales qualification completed
- Budget confirmed
- Timeline established (6-12 months)
- Decision process mapped
- Key stakeholders identified

**Characteristics**:
- Active sales engagement
- Multiple contacts at account
- Formal evaluation process
- Competitive situation defined

**Score Range**: 90+ points
**Ownership**: Sales
**Duration**: 30-180 days (varies by deal size)

**Key Activities**:
- Formal demonstrations
- Proposal development
- Reference calls
- Technical evaluations
- Contract negotiations

**Sales Process Stages**:
1. **Discovery**: Need and situation analysis
2. **Qualification**: Budget, authority, need, timeline
3. **Proposal**: Solution design and pricing
4. **Negotiation**: Terms and contract discussion
5. **Closed Won/Lost**: Final outcome

**Transition Criteria**:
→ **Customer**: Deal closed won
→ **SQL**: Deal lost, prospect still viable
→ **MQL**: Deal lost, reduced engagement

---

### 6. Customer
**Definition**: Someone who has purchased your product or service.

**Entry Criteria**:
- Signed contract/agreement
- Payment processed
- Product/service delivered

**Characteristics**:
- Active product usage
- Implementation in progress
- Success metrics defined
- Expansion opportunities

**Score Impact**: Reset/recalibrated for expansion
**Ownership**: Customer Success/Sales (expansion)
**Duration**: Ongoing relationship

**Key Activities**:
- Onboarding
- Training
- Support
- Expansion discussions
- Renewal negotiations

**Success Metrics**:
- Time to value
- Product adoption
- Usage metrics
- Satisfaction scores
- Expansion revenue

**Transition Opportunities**:
→ **Evangelist**: High satisfaction, reference potential
→ **At-Risk**: Low usage, support issues
→ **Churned**: Cancelled subscription/service

---

### 7. Evangelist
**Definition**: A highly satisfied customer who actively promotes your solution.

**Entry Criteria**:
- Customer for 6+ months
- High satisfaction scores
- Active product usage
- Willing to provide references

**Characteristics**:
- Case study participation
- Reference calls
- User community involvement
- Social media advocacy

**Key Activities**:
- Reference calls
- Case study development
- Event speaking
- Review site testimonials
- Referral generation

---

### 8. Other/Recycled
**Definition**: Contacts who don't fit other categories or are being re-engaged.

**Subcategories**:
- **Subscriber**: Newsletter/content only
- **Recycled**: Former SQL/Opportunity re-engaging
- **Unqualified**: Doesn't meet criteria
- **Bad Data**: Invalid/incomplete information

---

## Transition Rules and Automation

### Score-Based Transitions

```
Visitor → Lead: Contact information captured
Score 0-29 → MQL: Score ≥30 + activity
Score 30-69 → SQL: Score ≥70 + qualification
Score 70-89 → Opportunity: Sales qualification complete
Score 90+ → Customer: Purchase completed
```

### Time-Based Rules

**Automatic Downgrade Triggers**:
- Lead → Visitor: 180 days no activity
- MQL → Lead: 90 days no activity + score <30
- SQL → MQL: 60 days no sales contact + no meeting set

**Re-engagement Triggers**:
- Recycled → MQL: Former customer showing new interest
- Unqualified → Lead: Job change to relevant role
- Subscriber → MQL: Increased engagement pattern

### Activity-Based Triggers

**Fast-Track Promotions**:
- Lead → SQL: Demo request + good fit company
- MQL → Opportunity: Multiple stakeholders engaged
- Any stage → SQL: Direct sales inquiry

**Negative Triggers**:
- Any stage → Unqualified: Competitor identification
- SQL/Opportunity → Lead: Budget/timeline issues

## Lifecycle Stage Reporting

### Key Metrics by Stage

**Visitor**:
- Traffic volume
- Conversion rate to Lead
- Top content consumed
- Traffic sources

**Lead**:
- Lead volume by source
- Time in stage
- Conversion rate to MQL
- Lead quality indicators

**Marketing Qualified Lead**:
- MQL volume and quality
- MQL → SQL conversion rate
- Time to qualification
- Nurturing campaign performance

**Sales Qualified Lead**:
- SQL volume and quality  
- SQL → Opportunity conversion
- Sales response time
- Disqualification reasons

**Opportunity**:
- Pipeline value
- Conversion rates
- Sales cycle length
- Win/loss analysis

**Customer**:
- Customer satisfaction
- Expansion revenue
- Retention rates
- Reference participation

### Lifecycle Funnel Analysis

**Conversion Rates**:
- Visitor → Lead: Target 2-5%
- Lead → MQL: Target 15-25%
- MQL → SQL: Target 25-40%
- SQL → Opportunity: Target 50-75%
- Opportunity → Customer: Target 20-35%

**Velocity Metrics**:
- Lead → MQL: 30-60 days
- MQL → SQL: 30-90 days
- SQL → Opportunity: 14-30 days
- Opportunity → Customer: 30-180 days

## Stage-Specific Nurturing

### Lead Nurturing (Score 0-29)
- Educational content series
- Industry insights
- Problem-awareness content
- Company introduction materials

### MQL Nurturing (Score 30-69)
- Solution-focused content
- Case studies and testimonials
- Webinar invitations
- Free tools and assessments

### SQL Follow-up (Score 70+)
- Personalized sales outreach
- Custom demonstrations
- ROI calculators
- Reference customers
- Competitive comparisons

### Opportunity Support
- Proposal development
- Stakeholder education
- Implementation planning
- Success metrics definition

## Regional/Market Variations

### Enterprise vs SMB

**Enterprise Path**:
- Longer lifecycle stages
- Multiple stakeholders
- Complex qualification
- Extended sales cycles

**SMB Path**:
- Compressed stages
- Faster transitions
- Self-service options
- Shorter sales cycles

### Geographic Considerations

**North America**:
- Standard lifecycle model
- Direct sales approach
- Traditional qualification

**Europe**:
- Privacy compliance (GDPR)
- Relationship-focused
- Longer qualification process

**Asia-Pacific**:
- Relationship building emphasis
- Group decision making
- Extended evaluation periods

## Integration with Sales Process

### CRM Configuration

**Salesforce Setup**:
- Lead Status = Lifecycle Stage
- Lead Score field updates
- Workflow automations
- Dashboard reporting

**HubSpot Setup**:
- Lifecycle stage property
- Score-based workflows
- Automated task creation
- Reporting dashboards

### Sales Team Training

**Stage Definitions**:
- Clear criteria for each stage
- Transition requirements
- Ownership responsibilities
- Success metrics

**Process Training**:
- When to advance stages
- Disqualification criteria
- Feedback to marketing
- CRM data hygiene

## Optimization Guidelines

### Monthly Reviews

**Conversion Analysis**:
- Stage-to-stage conversion rates
- Time in stage analysis
- Drop-off point identification
- Success factor correlation

**Score Correlation**:
- Score ranges by stage
- Conversion rates by score
- Optimal threshold identification
- Model refinement needs

### Quarterly Adjustments

**Threshold Updates**:
- MQL score requirements
- SQL qualification criteria
- Time-based transitions
- Activity-based promotions

**Process Refinement**:
- Stage definition updates
- Automation improvements
- Sales process alignment
- Reporting enhancements

This lifecycle stage framework provides the foundation for effective lead management and ensures smooth handoffs between marketing and sales teams while maintaining data integrity and process consistency.