---
name: Automate Content Audits with Google Sheets Analysis & Slack Reporting
description: "Analyze and audit content for readability, tone, and sentiment with AI-powered insights. Use when the user needs content improvement recommendations, repurposing strategies, or SEO optimization."
version: 1.0.0
homepage: https://github.com/ncreighton/empire-skills
metadata:
  {"openclaw":{"requires":{"env":["OPENAI_API_KEY"],"bins":["curl"]},"os":["macos","linux","win32"],"files":["SKILL.md"],"emoji":"📋"}}
---

# Content Audit Expert

## Overview

Content Audit Expert is a comprehensive AI-powered analysis tool that evaluates your written content across multiple dimensions—readability, tone, sentiment, SEO performance, and audience engagement potential. Rather than surface-level feedback, this skill provides deep structural analysis and actionable repurposing strategies.

This skill is invaluable for content teams, marketers, copywriters, and publishers who need to:
- **Maintain consistent brand voice** across multiple channels (WordPress, Medium, LinkedIn, Slack)
- **Optimize content for search engines** with keyword analysis and heading structure recommendations
- **Identify underperforming assets** in your content library and discover repurposing opportunities
- **Improve readability scores** for diverse audience segments
- **Detect tone misalignment** before publishing across corporate, marketing, or support channels
- **Analyze sentiment patterns** to understand emotional resonance with your target audience

Unlike basic grammar checkers, Content Audit Expert leverages advanced NLP analysis to evaluate content holistically—examining narrative structure, keyword density, audience alignment, and conversion potential. It integrates seamlessly with WordPress editorial workflows, Slack publishing pipelines, and Google Drive content repositories.

## Quick Start

Try these prompts immediately to see the skill in action:

### Example 1: Blog Post Audit
```
Audit this blog post for content quality:

Title: "10 Ways to Boost Your Productivity"

"Productivity is important. Everyone wants to be more productive. In this article, 
we'll discuss 10 ways you can boost your productivity. These methods are proven 
and effective. Let's start. First, you should wake up early. Waking up early helps 
you get more done. Second, you should make a to-do list. Lists help you stay organized. 
Third, you should eliminate distractions. Distractions stop you from working. 
We recommend using apps like Focus@Will or Forest."

Provide readability score, tone analysis, sentiment breakdown, and 3 specific repurposing ideas.
```

### Example 2: Email Copy Analysis
```
Analyze this email for conversion optimization:

Subject: "Check Out Our New Product"
Body: "Hi there, we've launched a new product. It's really good. You should check it out. 
Click here to learn more. Thanks."

Include: sentiment analysis, audience alignment score, CTA effectiveness rating, 
and specific copy improvements with before/after examples.
```

### Example 3: Bulk Content Audit
```
Run a content audit across these three pieces and identify cross-promotion opportunities:

Article 1 (2,400 words): "The Complete Guide to SEO in 2024"
Article 2 (800 words): "5 Common SEO Mistakes"
Article 3 (1,200 words): "How to Optimize Your Title Tags"

Provide: overlap analysis, unique value propositions for each, repurposing suggestions
(social snippets, email sequences, LinkedIn posts), and a content gap report.
```

## Capabilities

### 1. **Readability Analysis**
- Flesch Kincaid Grade Level calculation
- Gunning Fog Index evaluation
- Sentence length variance detection
- Paragraph structure optimization
- Passive vs. active voice ratio analysis
- Jargon and complexity flagging

**Usage Example:**
```
Evaluate readability for a technical white paper aimed at C-suite executives
with a target grade level of 10-12. Flag any overly complex passages that 
exceed 18 words per sentence on average.
```

### 2. **Tone & Voice Detection**
- Brand voice consistency scoring (0-100)
- Formal vs. conversational balance measurement
- Authority vs. approachability alignment
- Professional tone assessment
- Personality/character consistency tracking across multiple pieces
- Emotional resonance indicators

**Usage Example:**
```
Analyze whether this customer support email maintains our brand voice.
Our brand voice guidelines: warm, professional, solution-focused, empathetic.
Flag any departures from these principles.
```

### 3. **Sentiment & Emotional Analysis**
- Overall sentiment classification (positive, negative, neutral)
- Emotion detection (joy, trust, fear, surprise, sadness, disgust, anger, anticipation)
- Emotional intensity scoring
- Sentiment progression tracking through content
- Reader emotional journey mapping

**Usage Example:**
```
Sentiment audit: Does this product landing page evoke the right emotions 
(confidence, excitement, trust) to drive conversions? Map the emotional journey 
paragraph by paragraph.
```

### 4. **SEO & Keyword Performance**
- Primary and secondary keyword identification
- Keyword density analysis with optimization recommendations
- Heading structure (H1/H2/H3) evaluation
- Meta description effectiveness
- Internal linking opportunity detection
- Target audience keyword intent alignment

**Usage Example:**
```
SEO audit for target keywords: "content marketing," "marketing automation," 
"content calendar." Evaluate keyword placement, density, and suggest H2/H3 
restructuring for better SERP visibility.
```

### 5. **Content Repurposing Strategy**
- Identify evergreen vs. time-sensitive content
- Generate 5+ repurposing ideas (social posts, email sequences, videos, infographics, podcasts)
- Calculate ROI potential for each repurposing avenue
- Suggest format conversions (blog → email series, article → social carousel)
- Cross-promotion opportunity mapping
- Content fragmentation strategy (break long-form into series)

**Usage Example:**
```
Propose 8 ways to repurpose this 2,000-word guide. Include: LinkedIn article 
snippets, Twitter/X thread outline, email sequence structure, YouTube video 
outline, podcast talking points, infographic data points, and webinar transcript.
```

### 6. **Audience Alignment Scoring**
- Target persona matching (0-100)
- Language difficulty vs. audience reading level
- Relevance score to stated audience
- Engagement prediction based on demographic research
- Value prop clarity for specific personas

### 7. **Competitive Benchmarking**
- Compare against industry standard readability scores
- Identify unique value propositions vs. competitor content
- Content depth analysis (word count, comprehensiveness)
- Missing information gaps relative to top-ranking competitors

## Configuration

### Required Environment Variables
```bash
# Set your OpenAI API key (required for AI analysis)
export OPENAI_API_KEY="sk-..."

# Optional: Set preferred temperature for analysis (0.3-0.7 recommended)
export AUDIT_TEMPERATURE="0.5"

# Optional: Set content analysis depth (basic, standard, comprehensive)
export AUDIT_DEPTH="comprehensive"
```

### Setup Instructions

1. **Install dependencies** (if running locally):
```bash
pip install openai python-dotenv textstat
```

2. **Authenticate with OpenAI**:
   - Get your API key from https://platform.openai.com/api-keys
   - Set the `OPENAI_API_KEY` environment variable
   - Verify access: `curl https://api.openai.com/v1/models -H "Authorization: Bearer $OPENAI_API_KEY"`

3. **Integration Setups**:
   - **WordPress**: Use the ClawHub WordPress plugin to send content directly from editor
   - **Google Docs**: Share document, provide link in prompt
   - **Slack**: Enable ClawHub in your Slack workspace, use `/audit [content]` command
   - **Email**: Forward content via email or paste directly

### Configuration Options

| Option | Default | Description |
|--------|---------|-------------|
| `AUDIT_DEPTH` | comprehensive | basic, standard, or comprehensive analysis |
| `TARGET_AUDIENCE` | general | Specify audience (C-suite, marketers, developers, etc.) |
| `CONTENT_FORMAT` | article | article, email, social, whitepaper, case-study |
| `BRAND_VOICE_GUIDELINES` | none | Paste your brand voice document for consistency scoring |
| `COMPETITOR_URLS` | none | Include URLs for competitive benchmarking |

## Example Outputs

### Sample Readability Report
```
═══════════════════════════════════════════════════════════════
READABILITY ANALYSIS
═══════════════════════════════════════════════════════════════

Overall Readability Score: 72/100 (Good)
Target Grade Level: 9.4 (High School Sophomore)
Flesch Kincaid Grade: 10.2

BREAKDOWN:
├─ Sentence Variety: 85/100 ✓ (Range: 8-32 words)
├─ Paragraph Length: 68/100 ⚠ (Avg: 4.2 sentences)
├─ Passive Voice: 15% (Target: <20%) ✓
├─ Jargon Density: 8% (Acceptable)
└─ Word Complexity: 92% common words ✓

TOP RECOMMENDATIONS:
1. Break paragraph 3 into 2 shorter paragraphs (currently 6 sentences)
2. Simplify "leverage" → "use" in line 47
3. Expand paragraph 5 with subheading for structure
```

### Sample Tone & Sentiment Report
```
═══════════════════════════════════════════════════════════════
TONE & SENTIMENT ANALYSIS
═══════════════════════════════════════════════════════════════

Overall Sentiment: Positive (78% confidence)
Tone Classification: Professional + Conversational (Well-balanced)

EMOTIONAL BREAKDOWN:
├─ Trust: 82% (Strong authority signals)
├─ Anticipation: 71% (Forward-looking language)
├─ Joy: 56% (Moderate positivity)
├─ Fear: 12% (Appropriate risk acknowledgment)
└─ Surprise: 34% (Some novel insights)

SENTIMENT JOURNEY:
Paragraph 1-2: Positive (Introduction) → 
Paragraph 3-5: Neutral (Technical details) → 
Paragraph 6-7: Positive (Benefits & conclusion)

BRAND VOICE ALIGNMENT: 88/100 ✓
Matches "professional, approachable, solution-focused" guidelines
```

### Sample Repurposing Strategy
```
═══════════════════════════════════════════════════════════════
CONTENT REPURPOSING OPPORTUNITIES
═══════════════════════════════════════════════════════════════

Original: 1,850-word blog post "Email Marketing Automation"
Content Type: Evergreen (85% evergreen score)
Recommended Lifespan: 18+ months with minor updates

REPURPOSING IDEAS (Ranked by ROI):

1. EMAIL SEQUENCE (Est. Value: $4,200/month)
   ├─ 5-part welcome series
   ├─ Segment: Marketing professionals
   └─ Time to Create: 2 hours

2. LINKEDIN ARTICLE SERIES (Est. Reach: 15K-25K)
   ├─ 4-part carousel posts
   ├─ Best Publishing Days: Tue-Thu, 8am
   └─ Template Provided: Yes

3. SOCIAL CLIPS (Est. Engagement: +340%)
   ├─ 8x short-form clips (TikTok/Reels)
   ├─ Hooks: "3 automation mistakes," "Hidden benefit," etc.
   └─ Video Scripts: Included

4. WEBINAR OUTLINE (Est. Attendees: 200-400)
   ├─ 45-minute structure with breakout activities
   ├─ Slides Required: 18-22
   └─ Interactive Elements: 4 polls, 2 demos

5. PODCAST EPISODE (Est. Downloads: 1,200+)
   ├─ Talking Points: Structured outline
   ├─ Guest Interview Format: 35-45 minutes
   └─ Show Notes Template: Provided

6. INFOGRAPHIC (Est. Shares: 800+)
   ├─ Key Data Points: 7 critical statistics
   ├─ Design Brief: Provided
   └─ Distribution: LinkedIn, Pinterest, Twitter
```

## Tips & Best Practices

### 1. **Establish Baseline Metrics**
Before making changes, run an audit to establish your content quality baseline. Track these metrics over time:
- Average readability score
- Sentiment consistency
- Brand voice alignment percentage
- SEO keyword density

This creates accountability and shows improvement ROI to stakeholders.

### 2. **Use Comparative Audits**
```
Audit your top 5 performing pages against your bottom 5. 
Look for patterns in readability, tone, and sentiment that 
correlate with engagement. Use findings to improve underperformers.
```

### 3. **Implement Brand Voice Guidelines**
Create a 1-page brand voice document covering:
- Tone descriptors (warm, authoritative, playful, etc.)
- Vocabulary (preferred terms vs. forbidden jargon)
- Sentence structure preference
- Common phrases/mantras
- Examples of on-brand and off-brand writing

Run audits with this document for 95%+ consistency scoring.

### 4. **Audit Before Updating Content**
Always audit existing content before revisions. This:
- Identifies what's currently working
- Prevents inadvertent tone shifts
- Shows specific improvement targets
- Creates a before/after comparison for stakeholder reporting

### 5. **Leverage Repurposing for Content Multiplication**
A single 2,000-word blog post can generate:
- 1 email sequence (5-7 emails)
- 8-10 social media posts
- 1 webinar outline
- 1 short video script
- 1 podcast talking points outline

Multiplies content ROI by 5-8x without starting from scratch.

### 6. **Segment Audits by Content Type**
Different content types have different standards:
- **Blog posts**: 70+ readability, positive sentiment
- **Sales pages**: 60-70 readability (exclusivity), high trust/anticipation
- **Support docs**: 75+ readability (clarity), neutral tone
- **Email**: 65-75 readability (scannable), warm tone

Configure audits for specific content type standards.

### 7. **Monitor Sentiment Drift**
If publishing frequently to a channel (newsletter, blog, social), track sentiment patterns:
- Avoid 3+ consecutive negative posts
- Mix positive, neutral, and aspirational content
- Balance problem-focused with solution-focused messaging
- Maintain 70%+ positive sentiment overall for brand reputation

### 8. **Use Competitive Benchmarking**
Provide competitor URLs for comparative analysis:
```
Audit my article against these top-ranking competitors:
[URL 1], [URL 2], [URL 3]

Show: word count comparison, keyword frequency comparison, 
readability score comparison, sentiment comparison, unique 
value propositions I should emphasize more.
```

## Safety & Guardrails

### What This Skill WILL Do
✓ Analyze readability, tone, sentiment, and keyword performance  
✓ Suggest structural improvements and repurposing strategies  
✓ Provide competitive benchmarking and gap analysis  
✓ Generate specific, actionable recommendations  
✓ Create before/after editing examples  

### What This Skill WILL NOT Do
✗ **Not a substitute for subject matter expertise** — The skill analyzes structure and style, not factual accuracy. Always verify claims, statistics, and technical details independently.

✗ **Not a plagiarism detector** — Use Copyscape, Turnitin, or Grammarly's plagiarism checker instead.

✗ **Not for automated publishing** — All recommendations require human review before publishing. The skill flags concerns but doesn't make editorial decisions.

✗ **Not a replacement for editors** — Use for optimization, not as a complete editing solution. Complex rewrites and narrative restructuring still benefit from human editors.

✗ **Not legal or medical content validation** — This skill cannot verify compliance with industry regulations (HIPAA, legal disclaimers, medical claims). Consult domain experts for regulated content.

✗ **Not cultural sensitivity analysis** — While the skill detects tone, it may miss cultural context or offensive implications. Review with subject matter experts familiar with your audience's culture.

### Limitations & Boundaries

| Limitation | Workaround |
|-----------|-----------|
| Works best with 200+ words | Use bulk audits for shorter content; batch multiple pieces |
| Doesn't verify citations/facts | Cross-reference claims with fact-checking tools independently |
| Brand voice matching requires clear guidelines | Provide detailed brand voice document for accuracy