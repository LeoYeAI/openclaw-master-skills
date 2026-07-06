---
name: deep-research
description: This skill should be used when the user requests comprehensive research, deep investigation, or detailed academic-style reports on any topic. Trigger phrases include "deep research", "comprehensive investigation", "detailed report", "academic research", or requests for thorough analysis of complex subjects. The skill produces multi-thousand word reports in markdown format with extensive citations.
---

# Deep Research

## Overview

This skill transforms Claude into a comprehensive AI research assistant that produces detailed, structured, evidence-based reports on specified topics. The output is a formal, objective, academic-style markdown report, typically several thousand words in length, with proper citations and references. This is Deep Research, not superficial investigation—prioritize thoroughness and rigor over speed and efficiency. Omissions, shortcuts, or superficial treatment are unacceptable.

## Core Principles

### Information Priority Hierarchy

Follow this strict hierarchy when gathering information:

1. **Data Source APIs** - Authoritative, structured data from reliable APIs
2. **Web Search** - Current information from credible web sources
3. **Model Internal Knowledge** - Use only as context or when other sources are unavailable

**Critical**: Search result snippets are NOT valid information sources. Always access the original page via WebFetch to verify and extract complete information.

### Thoroughness Over Efficiency

This is Deep Research. The following priorities apply:

- **Completeness** trumps speed
- **Accuracy** trumps convenience
- **Rigor** trumps efficiency
- **Verification** trumps assumption

Rushing through research or taking shortcuts due to perceived time pressure is completely unacceptable. Negligence and superficial treatment are far greater sins than taking the necessary time to be thorough.

### Critical Thinking

Apply critical thinking throughout the research process:

- Evaluate source credibility and potential biases
- Compare multiple sources and cross-reference information
- Identify conflicts or inconsistencies in the data
- Distinguish between facts, interpretations, and opinions
- Question assumptions and verify claims

## Research Workflow

### Phase 1: Topic Decomposition and Concept Understanding

Before beginning any research, thoroughly decompose and understand the topic.

#### 1.1 Identify the Core Research Question

Extract and clearly articulate the central research question or topic. If the user's request is broad or ambiguous, break it down into specific, answerable questions.

#### 1.2 Decompose into Key Concepts

Identify all major concepts, sub-topics, and related areas that need investigation. Create a conceptual map of the research domain.

**Example**: For "AI ethics", identify sub-concepts like:
- Algorithmic bias
- Privacy concerns
- Accountability and transparency
- Job displacement
- Autonomous decision-making
- Regulatory frameworks

#### 1.3 Define Unknown Concepts (HIGHEST PRIORITY)

**CRITICAL**: For any concept, term, or domain you are not completely familiar with, IMMEDIATELY research its definition and meaning before proceeding. This is the absolute highest priority. Never proceed with research on a topic you do not fully understand.

**Process**:
1. Identify unfamiliar terms or concepts
2. Search for authoritative definitions (academic sources, domain experts, official documentation)
3. Access multiple sources via WebFetch to build comprehensive understanding
4. Only proceed once you have solid conceptual grounding

#### 1.4 Identify Potential Ambiguities

Recognize where terms might have multiple meanings, where cultural or linguistic differences might matter, or where the research question might be interpreted in different ways.

### Phase 2: Research Planning

Create a comprehensive research plan before executing searches.

#### 2.1 Define Key Questions

For each major concept and sub-topic, formulate specific questions that need answers:

- What is the current state of knowledge on this topic?
- What are the major perspectives or theories?
- What evidence exists?
- What are the controversies or debates?
- What are the practical implications?
- What are recent developments (if relevant)?

#### 2.2 Identify Search Strategies

Plan your search approach:

- **Sequential Entity Processing**: For multiple entities or concepts, research each one individually and completely before moving to the next
- **Attribute-by-Attribute**: For a single entity, research different attributes or aspects separately
- **Staged Depth**: Begin with broad overviews, then progressively narrow to specific details
- **Multi-Lingual**: Plan to search in multiple languages to overcome information siloing (see Phase 3.3)

#### 2.3 Anticipate Information Gaps

Based on your understanding of the topic, anticipate where information might be scarce, biased, or contradictory. Plan how you will handle these situations.

### Phase 3: Systematic Web Search

Execute comprehensive web searches following these protocols.

#### 3.1 Staged and Progressive Search

Search in stages, not all at once:

1. **Initial broad searches** to understand the landscape
2. **Analyze initial results** to identify knowledge gaps and refine questions
3. **Targeted follow-up searches** to fill specific gaps
4. **Verification searches** to cross-check critical claims

After each search round, analyze what you learned and what questions remain, then plan the next search iteration.

#### 3.2 Multiple URL Access

For each search query:

- Review search results carefully
- Access **multiple URLs** (not just one) to ensure comprehensive coverage
- Prioritize authoritative sources (academic institutions, government agencies, established research organizations, peer-reviewed publications)
- Include diverse perspectives (different authors, organizations, viewpoints)

Use WebFetch to access the full content of each selected URL. Snippets alone are insufficient.

#### 3.3 Multi-Lingual Search

Information is often siloed by language. To overcome this:

- Conduct searches in **at least two languages** (e.g., English and Japanese, English and the user's language)
- Compare information available in different language spheres
- Note where information differs or is unique to one language domain
- Translate key terms accurately when searching in different languages

**Example**: Searching for "renewable energy policy" should include searches in both English ("renewable energy policy") and Japanese ("再生可能エネルギー政策") to capture region-specific information and perspectives.

#### 3.4 Sequential Entity and Attribute Processing

**For multiple entities**: Research each entity completely before moving to the next. Do not interleave.

**Example**: If researching "Tesla, Ford, and Toyota", complete all research on Tesla (history, products, financials, strategy, etc.) before beginning Ford.

**For single entity with multiple attributes**: Research each attribute separately.

**Example**: For a company, separate searches for: financial performance, product lineup, sustainability initiatives, corporate governance, market position, etc.

### Phase 4: Critical Analysis and Cross-Verification

After gathering information, apply rigorous analysis.

#### 4.1 Source Evaluation

For each source used:

- Assess credibility (author expertise, publication reputation, institutional backing)
- Identify potential biases (funding sources, ideological leanings, conflicts of interest)
- Evaluate recency (is the information current or outdated?)
- Check primary vs. secondary sources (prefer primary when possible)

#### 4.2 Information Synthesis

- Identify consensus views across multiple credible sources
- Note where sources disagree and why
- Distinguish between well-established facts and emerging theories
- Highlight areas of uncertainty or ongoing debate

#### 4.3 Cross-Reference Verification

When encountering critical claims or statistics:

- Verify with multiple independent sources
- Trace claims back to original sources when possible
- Check whether context has been preserved or distorted
- Flag any information that cannot be independently verified

### Phase 5: Section Drafting

Create the report in sections, treating each as a separate draft.

#### 5.1 Section Planning

Based on your research, outline the report structure:

- Introduction and background
- Major topics and sub-topics (each as separate sections)
- Analysis and synthesis
- Conclusions or implications
- References

#### 5.2 Individual Section Drafting

For each section:

1. **Create a separate draft file**: Save each major section as an individual markdown file (e.g., `draft_introduction.md`, `draft_section2.md`, etc.)
2. **Write in detail**: Each section should be comprehensive, with full paragraphs and complete development of ideas
3. **Include citations inline**: Use proper attribution (see Writing Guidelines below)
4. **Do not abbreviate or summarize**: Write the section in its intended final length

**Rationale**: Separate files prevent context limitations and ensure no content is lost during drafting.

#### 5.3 Section-by-Section Completion

Complete each section fully before moving to the next. This ensures:

- Each topic is thoroughly covered
- Citations are properly tracked
- Quality remains consistent throughout

### Phase 6: Final Report Assembly

Combine all section drafts into the final report.

#### 6.1 Sequential Combination

Combine sections in logical order:

1. Read each draft file sequentially
2. Copy the full content into the final report document
3. **Do NOT reduce, summarize, or abbreviate** during combination
4. Ensure smooth transitions between sections

**Critical**: The final document length must be equal to or greater than the sum of individual drafts. Never reduce content during assembly.

#### 6.2 Add Connecting Elements

- Ensure smooth transitions between sections
- Add cross-references where sections relate to each other
- Verify consistent terminology throughout

#### 6.3 Complete References Section

Compile all citations into a final References section at the end of the document:

- List all sources alphabetically or in order of appearance
- Include full URLs for web sources
- Follow consistent citation format (see Writing Guidelines)

#### 6.4 Final Quality Check

- Verify all citations are present and correct
- Check for consistency in formatting and style
- Ensure the report meets length requirements (minimum several thousand words)
- Confirm the report is in the user's language
- Verify formal, objective, academic tone throughout
- Ensure no emojis or informal elements are present

## Writing Guidelines

### Language and Tone

- **Language**: Write in the user's language (the language they used in their request)
- **Tone**: Formal, objective, academic
- **Voice**: Third person, passive or active as appropriate for academic writing
- **Perspective**: Neutral and analytical, not persuasive or advocacy-oriented

### Text Structure and Style

#### Prose Over Bullet Points

**Default format**: Continuous prose in paragraph form. Bullet points are ONLY used when the user explicitly requests them.

- **Paragraph-based**: Structure content in well-developed paragraphs
- **Varied sentence length**: Mix short, medium, and long sentences for readability
- **Logical flow**: Each paragraph should have a clear topic sentence and supporting details
- **Transitions**: Use transition words and phrases to connect ideas

**Example of preferred style**:

> The development of renewable energy technologies has accelerated significantly over the past two decades. Solar photovoltaic costs have declined by approximately 90% since 2010, making solar energy competitive with fossil fuels in many markets. This cost reduction has been driven by multiple factors, including manufacturing scale economies, technological improvements in cell efficiency, and supportive policy frameworks in key markets such as China, the European Union, and the United States.

**Avoid** (unless specifically requested):

> Renewable energy developments:
> - Solar costs down 90% since 2010
> - Now competitive with fossil fuels
> - Driven by: scale economies, efficiency gains, supportive policies

#### Detail and Depth

- **Minimum length**: Several thousand words (unless user specifies otherwise)
- **Depth**: Provide thorough explanations, not superficial summaries
- **Specificity**: Include specific data, examples, and evidence
- **Completeness**: Address all aspects of the topic comprehensively

### Citations and References

#### Inline Citations

When referencing information from sources, provide clear attribution within the text.

**Preferred formats**:

- According to [Author/Organization] (Year), [claim or finding]...
- Research by [Author/Organization] found that [finding]...
- As documented in [Source], [information]...
- [Claim], as reported by [Source]...

**Example**:

> According to the International Energy Agency (2023), global renewable energy capacity is expected to grow by 2,400 GW between 2022 and 2027. This represents an acceleration of 85% compared to the previous five-year period, as documented in the IEA's Renewable Energy Market Update.

#### References Section

At the end of the report, include a comprehensive References section listing all sources:

**Format** (adapt as appropriate for the field):

```
[Author/Organization]. (Year). Title. Retrieved from [URL]
```

**Example**:

```
## References

International Energy Agency. (2023). Renewable Energy Market Update - June 2023. Retrieved from https://www.iea.org/reports/renewable-energy-market-update-june-2023

Smith, J., & Johnson, K. (2022). The Economics of Solar Energy: A Meta-Analysis. Journal of Sustainable Energy, 15(3), 234-256. Retrieved from https://example.com/article

World Bank. (2023). Global Energy Trends Report. Retrieved from https://worldbank.org/energy-trends-2023
```

#### Citation Requirements

- **Always cite**: Facts, statistics, quotes, specific claims, research findings
- **Include URLs**: Every web source must have a complete, accessible URL
- **Verify links**: Ensure URLs are accurate and accessible
- **No uncited claims**: Every substantive claim should be traceable to a source

### Formatting

- **Format**: Markdown (.md)
- **Headings**: Use proper heading hierarchy (# for title, ## for main sections, ### for subsections, etc.)
- **Emphasis**: Use **bold** for key terms or emphasis, *italics* for titles or subtle emphasis
- **Tables**: Use markdown tables for structured data when appropriate
- **No emojis**: Never use emojis unless explicitly requested by the user

## Resources

### references/

This skill includes reference files with detailed methodologies and guidelines:

- **research_methodology.md**: In-depth strategies for conducting staged searches, evaluating sources, and applying critical thinking
- **citation_guidelines.md**: Detailed instructions for citation formats and reference management

Access these files as needed for additional guidance on specific research challenges.

### assets/

- **report_template.md**: A template structure for the final report, showing recommended sections and organization

Use this template as a starting point for organizing the final report output.

## Common Pitfalls to Avoid

1. **Rushing the research**: Taking shortcuts to finish quickly undermines the entire purpose of Deep Research
2. **Relying on snippets**: Search snippets are summaries, not sources. Always access full content via WebFetch
3. **Single-source information**: Relying on one source creates bias and error risk. Always cross-verify
4. **Ignoring language barriers**: Searching only in one language misses important information
5. **Bullet-point reports**: Unless explicitly requested, use prose paragraphs, not bullet lists
6. **Reducing content during assembly**: The final report should preserve all drafted content in full
7. **Skipping concept definition**: Never research a topic you don't fully understand. Define concepts first
8. **Insufficient citations**: Every claim needs a traceable source with URL

## Quality Standards

A high-quality Deep Research report demonstrates:

- **Comprehensiveness**: All major aspects of the topic are addressed
- **Depth**: Detailed treatment, not superficial coverage
- **Evidence-based**: Every claim is supported by credible sources
- **Critical analysis**: Information is evaluated, not just reported
- **Proper structure**: Logical organization with clear sections
- **Formal prose**: Academic writing style with varied sentence structure
- **Complete citations**: All sources properly documented with URLs
- **Appropriate length**: Several thousand words minimum (unless otherwise specified)
- **User's language**: Written in the language the user used for the request
- **No emojis or informal elements**

When the research is complete and the report is delivered, the user should have a comprehensive, authoritative document that demonstrates rigorous investigation and critical thinking on the topic.
