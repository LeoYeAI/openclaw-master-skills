# HubSpot Lead Scoring Setup Guide

## Prerequisites

Before setting up lead scoring in HubSpot, ensure you have:
- HubSpot Marketing Hub Professional or Enterprise
- Admin access to your HubSpot portal
- At least 3 months of historical contact data
- Clear ideal customer profile definition
- Sales team alignment on lead quality criteria

## Phase 1: Property Setup

### Step 1: Create Custom Scoring Properties

Navigate to **Settings > Properties > Contact Properties**

#### Create Lead Score Property
1. Click **Create Property**
2. **Property Information**:
   - Label: `Lead Score`
   - Internal name: `lead_score`
   - Description: `Composite lead score based on demographic fit and behavioral engagement`
   - Property type: `Number`
3. **Field Settings**:
   - Number format: `Unformatted number`
   - Min value: `0`
   - Max value: `200`
   - Default value: `0`
4. **Rules**:
   - Required: `No`
   - Show in forms: `No`
   - Show on contact record: `Yes`

#### Create Demographic Score Property
1. Click **Create Property**
2. **Property Information**:
   - Label: `Demographic Score`
   - Internal name: `demographic_score`
   - Description: `Score based on company size, industry, job title fit`
   - Property type: `Number`
3. **Field Settings**:
   - Number format: `Unformatted number`
   - Min value: `0`
   - Max value: `100`
   - Default value: `0`

#### Create Behavioral Score Property
1. Click **Create Property**
2. **Property Information**:
   - Label: `Behavioral Score`
   - Internal name: `behavioral_score`
   - Description: `Score based on website, email, content engagement`
   - Property type: `Number`
3. **Field Settings**:
   - Number format: `Unformatted number`
   - Min value: `0`
   - Max value: `100`
   - Default value: `0`

#### Create Supporting Properties
Create these additional properties:

**Last Score Update**:
- Label: `Last Score Update`
- Type: `Date picker`
- Description: `When lead score was last calculated`

**Lead Grade**:
- Label: `Lead Grade`
- Type: `Dropdown select`
- Options: `A+, A, A-, B+, B, B-, C+, C, D`
- Description: `Demographic fit grade`

**Score Change**:
- Label: `Score Change (30 days)`
- Type: `Number`
- Description: `Score change in last 30 days`

**Scoring Notes**:
- Label: `Scoring Notes`
- Type: `Multi-line text`
- Description: `Internal notes on scoring rationale`

### Step 2: Company Scoring Properties

Navigate to **Settings > Properties > Company Properties**

#### Create Company Score Property
1. Click **Create Property**
2. **Property Information**:
   - Label: `Company Score`
   - Internal name: `company_score`
   - Description: `Account-level scoring for ABM`
   - Property type: `Number`
3. Set min/max values: `0-100`

#### Create Company Grade Property
1. **Property Information**:
   - Label: `Company Grade`
   - Type: `Dropdown select`
   - Options: `A+, A, A-, B+, B, B-, C+, C, D`

## Phase 2: Demographic Scoring Setup

### Step 3: Industry Scoring Workflow

Create workflow: **Settings > Automation > Workflows**

1. **Workflow Settings**:
   - Type: `Contact-based`
   - Name: `Lead Scoring - Industry`
   - Description: `Assigns industry-based demographic points`

2. **Enrollment Triggers**:
   - Contact is created
   - Company industry is known

3. **Re-enrollment**: Enable when "Company industry" changes

4. **Workflow Actions**:

```
IF Company industry is any of:
- Technology
- Software
- SaaS
THEN Set property value:
- Property: Demographic Score
- Value: Increase by 10

IF Company industry is any of:  
- Professional Services
- Consulting
- Financial Services
THEN Set property value:
- Property: Demographic Score  
- Value: Increase by 8

IF Company industry is any of:
- Healthcare
- Manufacturing
- Education
THEN Set property value:
- Property: Demographic Score
- Value: Increase by 5

IF Company industry is any of:
- Government
- Non-profit
THEN Set property value:
- Property: Demographic Score
- Value: Increase by 2
```

### Step 4: Company Size Scoring Workflow

1. **Workflow Settings**:
   - Name: `Lead Scoring - Company Size`
   - Type: `Contact-based`

2. **Enrollment Triggers**:
   - Number of employees is known
   - Contact is created

3. **Workflow Actions**:

```
IF Number of employees is between 100 and 1000:
THEN Set property value:
- Property: Demographic Score
- Value: Increase by 15

IF Number of employees is between 50 and 99:
THEN Set property value:
- Property: Demographic Score  
- Value: Increase by 12

IF Number of employees is between 1001 and 5000:
THEN Set property value:
- Property: Demographic Score
- Value: Increase by 10

IF Number of employees is less than 50:
THEN Set property value:
- Property: Demographic Score
- Value: Increase by 5

IF Number of employees is greater than 5000:
THEN Set property value:
- Property: Demographic Score
- Value: Increase by 3
```

### Step 5: Job Title Scoring Workflow

1. **Workflow Settings**:
   - Name: `Lead Scoring - Job Title`
   - Type: `Contact-based`

2. **Enrollment Triggers**:
   - Job title is known
   - Contact is created

3. **Workflow Actions**:

```
IF Job title contains any of:
- CEO, CTO, CMO, CFO, President, Owner, Founder
THEN Set property value:
- Property: Demographic Score
- Value: Increase by 20

IF Job title contains any of:
- VP, Vice President, SVP, EVP
THEN Set property value:
- Property: Demographic Score
- Value: Increase by 15

IF Job title contains any of:
- Director, Head of
THEN Set property value:
- Property: Demographic Score
- Value: Increase by 12

IF Job title contains any of:
- Manager, Lead, Senior
THEN Set property value:
- Property: Demographic Score
- Value: Increase by 8

IF Job title contains any of:
- Coordinator, Specialist, Analyst
THEN Set property value:
- Property: Demographic Score
- Value: Increase by 5
```

## Phase 3: Behavioral Scoring Setup

### Step 6: Website Activity Scoring

1. **Workflow Settings**:
   - Name: `Lead Scoring - Website Activity`
   - Type: `Contact-based`

2. **Enrollment Triggers**:
   - Page view (specific pages)
   - Set re-enrollment for repeated page views

3. **Workflow Actions** (create separate branches for each):

```
Page View - Pricing Page:
IF Visited pricing page in last 30 days
THEN Set property value:
- Property: Behavioral Score
- Value: Increase by 8

Page View - Demo Page:
IF Visited demo page in last 30 days  
THEN Set property value:
- Property: Behavioral Score
- Value: Increase by 6

Page View - Case Studies:
IF Visited case study page in last 30 days
THEN Set property value:
- Property: Behavioral Score
- Value: Increase by 4

Page View - Blog:
IF Visited blog page in last 30 days
THEN Set property value:
- Property: Behavioral Score
- Value: Increase by 2
```

### Step 7: Form Submission Scoring

1. **Workflow Settings**:
   - Name: `Lead Scoring - Form Submissions`
   - Type: `Contact-based`

2. **Enrollment Triggers**:
   - Form submission (select specific forms)

3. **Workflow Actions**:

```
Demo Request Form:
IF Submitted demo request form
THEN Set property value:
- Property: Behavioral Score
- Value: Increase by 15

Whitepaper Download:
IF Submitted whitepaper form
THEN Set property value:
- Property: Behavioral Score
- Value: Increase by 10

Newsletter Signup:
IF Submitted newsletter form
THEN Set property value:
- Property: Behavioral Score
- Value: Increase by 3

Contact Us Form:
IF Submitted contact form
THEN Set property value:
- Property: Behavioral Score
- Value: Increase by 12
```

### Step 8: Email Engagement Scoring

1. **Workflow Settings**:
   - Name: `Lead Scoring - Email Engagement`
   - Type: `Contact-based`

2. **Enrollment Triggers**:
   - Email opened
   - Email clicked
   - Email replied to

3. **Workflow Actions**:

```
Email Open:
IF Opened marketing email in last 7 days
THEN Set property value:
- Property: Behavioral Score
- Value: Increase by 1

Email Click:
IF Clicked link in marketing email in last 7 days
THEN Set property value:
- Property: Behavioral Score
- Value: Increase by 3

Email Reply:
IF Replied to marketing email in last 30 days
THEN Set property value:
- Property: Behavioral Score
- Value: Increase by 8
```

## Phase 4: Composite Score Calculation

### Step 9: Master Scoring Workflow

1. **Workflow Settings**:
   - Name: `Lead Scoring - Master Calculation`
   - Type: `Contact-based`

2. **Enrollment Triggers**:
   - Demographic score is known
   - Behavioral score is known
   - Contact is created or updated

3. **Workflow Actions**:

```
Calculate Total Score:
Set property value:
- Property: Lead Score  
- Value: [Demographic Score] + [Behavioral Score]

Update Last Score Date:
Set property value:
- Property: Last Score Update
- Value: Current date/time

Calculate Score Change:
Set property value:
- Property: Score Change (30 days)
- Value: [Current Lead Score] - [Lead Score from 30 days ago]
```

### Step 10: Grade Assignment Workflow

1. **Workflow Settings**:
   - Name: `Lead Scoring - Grade Assignment`
   - Type: `Contact-based`

2. **Enrollment Criteria**:
   - Lead score is known

3. **Workflow Actions**:

```
Grade A+ (90+ points):
IF Lead Score is greater than or equal to 90
THEN Set property value:
- Property: Lead Grade
- Value: A+

Grade A (80-89 points):
IF Lead Score is between 80 and 89
THEN Set property value:
- Property: Lead Grade  
- Value: A

Grade A- (70-79 points):
IF Lead Score is between 70 and 79
THEN Set property value:
- Property: Lead Grade
- Value: A-

[Continue for all grades B+, B, B-, C+, C, D]
```

## Phase 5: Lifecycle Stage Automation

### Step 11: MQL Promotion Workflow

1. **Workflow Settings**:
   - Name: `Lead Scoring - MQL Promotion`
   - Type: `Contact-based`

2. **Enrollment Criteria**:
   - Lead Score ≥ 50
   - Lifecycle stage is "Lead"
   - Last activity date is less than 30 days ago

3. **Workflow Actions**:
   - Set Lifecycle stage to "Marketing Qualified Lead"
   - Create task for marketing team
   - Send internal notification
   - Add to MQL nurturing sequence

### Step 12: SQL Promotion Workflow  

1. **Workflow Settings**:
   - Name: `Lead Scoring - SQL Promotion`
   - Type: `Contact-based`

2. **Enrollment Criteria**:
   - Lead Score ≥ 80
   - Lead Grade is A-, A, or A+
   - Lifecycle stage is "Marketing Qualified Lead"
   - Recent activity (7 days)

3. **Workflow Actions**:
   - Set Lifecycle stage to "Sales Qualified Lead"
   - Create task for sales rep
   - Send notification to sales team
   - Remove from marketing nurturing

## Phase 6: Score Decay Implementation

### Step 13: Behavioral Score Decay

1. **Workflow Settings**:
   - Name: `Lead Scoring - Behavioral Decay`
   - Type: `Contact-based`
   - Enrollment: `Daily at 9:00 AM`

2. **Enrollment Criteria**:
   - Last activity date is more than 30 days ago
   - Behavioral score is greater than 0

3. **Workflow Actions**:
   - Decrease behavioral score by 25%
   - Update last score date
   - Add note to contact record

### Step 14: Demographic Score Refresh

1. **Workflow Settings**:
   - Name: `Lead Scoring - Demographic Refresh`
   - Type: `Contact-based`
   - Enrollment: `Weekly on Monday at 10:00 AM`

2. **Actions**:
   - Recalculate demographic scores
   - Update company information
   - Refresh industry classifications

## Phase 7: Reporting and Dashboards

### Step 15: Lead Scoring Dashboard

Create custom dashboard: **Reports > Dashboards**

**Dashboard Name**: `Lead Scoring Performance`

**Report Widgets**:

1. **Score Distribution**:
   - Chart type: Bar chart
   - X-axis: Lead Score ranges (0-20, 21-40, etc.)
   - Y-axis: Number of contacts

2. **Lifecycle Funnel by Score**:
   - Chart type: Funnel
   - Stages: Lead → MQL → SQL → Opportunity
   - Breakdown by score ranges

3. **Top Scoring Activities**:
   - Chart type: Table
   - Columns: Activity type, Average score increase
   - Sort by: Score impact

4. **Score vs Conversion Rate**:
   - Chart type: Line graph
   - X-axis: Score ranges
   - Y-axis: Conversion rate to customer

5. **Monthly Score Trends**:
   - Chart type: Line graph
   - X-axis: Month
   - Y-axis: Average lead score
   - Multiple lines for different sources

### Step 16: Sales Team Reports

Create reports for sales team visibility:

**High Score Leads Report**:
- Filter: Lead Score ≥ 70
- Columns: Name, Company, Score, Grade, Last Activity
- Sort: Score (descending)
- Refresh: Daily

**Score Change Alert Report**:
- Filter: Score increased by 20+ in last 7 days
- Purpose: Identify hot prospects
- Delivery: Daily email to sales team

## Phase 8: Testing and Validation

### Step 17: Score Accuracy Testing

1. **Create Test Lists**:
   - Known customers (positive examples)
   - Unqualified leads (negative examples)
   - Recent SQLs (validation set)

2. **Analyze Scores**:
   - Do customers have high scores?
   - Do unqualified leads have low scores?
   - Are SQLs scoring appropriately?

3. **Adjust Thresholds**:
   - Modify point allocations
   - Update workflow conditions
   - Refine grade boundaries

### Step 18: A/B Testing Framework

**Test Scenarios**:
- Different MQL score thresholds
- Alternative point allocations
- Various decay rates
- Modified lifecycle criteria

**Measurement**:
- Conversion rates by test group
- Sales team feedback
- Lead quality metrics
- Pipeline impact

## Phase 9: Advanced Features

### Step 19: Company-Level Scoring

For Account-Based Marketing:

1. **Company Score Calculation**:
   - Average of contact scores
   - Weighted by job title importance
   - Account-level demographics

2. **Multi-Contact Scoring**:
   - Track engagement breadth
   - Identify buying committee
   - Score stakeholder influence

### Step 20: Predictive Scoring

If using HubSpot Enterprise:

1. **Enable Predictive Lead Scoring**:
   - Settings > Marketing > Lead Scoring
   - Choose predictive scoring model
   - Configure data requirements

2. **Combine with Custom Scores**:
   - Use predictive score as baseline
   - Add custom behavioral scoring
   - Weight demographic factors

## Maintenance and Optimization

### Monthly Tasks

1. **Review Score Distribution**:
   - Analyze score ranges
   - Check for score inflation
   - Validate accuracy metrics

2. **Sales Team Feedback**:
   - Survey lead quality perception
   - Gather disqualification reasons
   - Adjust criteria based on feedback

3. **Performance Analysis**:
   - Conversion rates by score
   - Sales cycle correlation
   - Revenue attribution

### Quarterly Tasks

1. **Model Optimization**:
   - Analyze successful customers
   - Update ideal customer profile
   - Refine point allocations

2. **Threshold Adjustments**:
   - Modify MQL/SQL criteria
   - Update lifecycle promotions
   - Adjust decay parameters

3. **Integration Updates**:
   - Connect new data sources
   - Add additional scoring factors
   - Improve automation workflows

## Troubleshooting Common Issues

### Issue: Score Not Updating
**Causes**:
- Workflow not enrolled
- Re-enrollment not enabled
- Property permissions

**Solutions**:
- Check workflow enrollment history
- Verify trigger conditions
- Test with sample contacts

### Issue: Scores Too High/Low
**Causes**:
- Incorrect point allocations
- Missing decay rules
- Data quality issues

**Solutions**:
- Recalibrate scoring matrix
- Implement proper decay
- Clean contact data

### Issue: Poor Sales Adoption
**Causes**:
- Complex scoring model
- Unclear criteria
- Lack of training

**Solutions**:
- Simplify score interpretation
- Provide clear documentation
- Regular training sessions

This comprehensive setup guide will establish a robust lead scoring system in HubSpot that aligns marketing and sales efforts while providing actionable insights for lead prioritization and nurturing.