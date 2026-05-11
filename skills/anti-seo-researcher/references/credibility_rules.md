# Credibility Assessment Rules Reference

> This document describes universal credibility rules. Region-specific keywords, marketing signals, and platform weights are loaded from `category_profile` at runtime. The patterns below are EXAMPLES — the actual patterns used depend on the user's locale.

## 1. Sponsored/Ad Content Identification

The following patterns lower credibility scores. Specific keywords vary by language and region (loaded from `category_profile.marketing_signals`).

### High-weight Negative Signals (each match: -20 to -30 points)

1. **Contains purchase links or promo codes**: Embedded e-commerce links, coupon codes, affiliate links in body text
2. **Opens with full brand name + model**: Real users rarely write the complete "Brand + Model + Product Line" in the first sentence
3. **Zero defects throughout**: Genuine long-term use reviews almost always mention at least one negative
4. **Heavy marketing language**: Excessive superlatives, buzzwords, hype terms (specific terms vary by language/region)
5. **Uses official promotional images**: Studio product photos instead of real-life photos
6. **Trending marketing buzzwords**: Region-specific viral marketing phrases

### Medium-weight Negative Signals (each match: -10 to -15 points)

1. **Overly polished formatting**: Clean paragraphs, neat subheadings, professional images — resembles commercial content
2. **Clustered posting times**: Multiple positive reviews for the same product appearing within 1-3 days
3. **Repetitive comment patterns**: Many comments with identical phrases (astroturfing indicators)
4. **Author history concentrated in one category**: 80%+ of the account's content is recommendations in the same category
5. **Content mirrors brand's official messaging**: Wording, feature order matches the official product page

### Low-weight Negative Signals (each match: -5 points)

1. **Title contains clickbait/review keywords**: Review, must-buy, guide, top picks (in local language)
2. **Call-to-action at the end**: "Follow for more recommendations" type prompts
3. **Cross-posted with identical content**: Same text posted on multiple platforms

## 2. Genuine User Feedback Signals

The following patterns increase credibility scores. Specific expressions vary by language (loaded from `category_profile.authenticity_signals`).

### High-weight Positive Signals (each match: +20 to +30 points)

1. **Clear usage duration**: "Used for 8 months", "Bought 2 years ago", "Came back to update after 6 months"
2. **Specific defect descriptions**: Concrete physical issues observed over time
3. **Before/after comparisons**: "Previously used Brand X, switched to this one and..."
4. **Real-life photos (not official)**: Cluttered background, natural lighting, signs of daily life
5. **After-sales experience**: Describes returns, customer service interactions, warranty claims

### Medium-weight Positive Signals (each match: +10 to +15 points)

1. **Casual, imperfect language**: Typos, filler words, incomplete sentences
2. **Responds to follow-up questions**: Answers specific usage questions in comments
3. **Diverse posting history**: Account posts about many different topics
4. **Contains purchase details**: Mentions specific price paid, where purchased, whether they waited for a sale
5. **Category-specific experience signals**: Loaded dynamically from `category_profile.category_positive_signals`
6. **Long-term change narrative**: Contains "at first... but later..." temporal progression

### Low-weight Positive Signals (each match: +5 points)

1. **Reasonable time gap between purchase and posting**
2. **Posted in niche forum or sub-community** (not category hot zone)
3. **Low follower count / ordinary user**
4. **Recent content (recency bonus)**: Content from the 90-day instant search window gets extra points

## 3. Platform Credibility Weights

Platform weights are defined in `category_profile.platform_relevance` and `category_profile.regional_platforms`. Below are REFERENCE values for common regions:

### China (zh-CN) Reference Weights

| Platform | Base Weight | Notes |
|----------|-------------|-------|
| V2EX | 0.9 | Tech community, low ad density |
| Chiphell | 0.9 | Hardcore tech forum, expert users |
| NGA | 0.85 | Vertical community, lower astroturfing |
| Douban | 0.8 | Cultural community, relatively authentic |
| Baidu Tieba (niche) | 0.75 | Niche sub-forums have real discussions |
| SMZDM (original) | 0.65 | Original long-form is decent, but has affiliate mechanisms |
| Zhihu (overall) | 0.55 | High-upvote answers often commercial |
| Zhihu (low-vote) | 0.7 | Low-vote but detailed answers tend to be genuine |
| Zhihu (high-vote) | 0.4 | High-vote answers are heavily commercialized |
| Xiaohongshu | 0.3 | Social commerce, high baseline ad probability |

### US/English (en-US) Reference Weights

| Platform | Base Weight | Notes |
|----------|-------------|-------|
| Reddit (niche subreddits) | 0.85 | Community moderation, lower ad density |
| Head-Fi / AVSForum | 0.9 | Enthusiast forums, expert users |
| Amazon (verified purchase) | 0.7 | Verified buyers, but incentivized reviews exist |
| YouTube (comments) | 0.5 | Mixed quality, some astroturfing |
| Wirecutter (comments) | 0.75 | Quality audience |
| Slickdeals | 0.65 | Deal-focused but real user feedback |

### Japan (ja-JP) Reference Weights

| Platform | Base Weight | Notes |
|----------|-------------|-------|
| Kakaku.com | 0.8 | Price comparison + reviews, relatively trusted |
| 5ch | 0.75 | Anonymous forum, raw opinions |
| Amazon.co.jp (verified) | 0.7 | Verified purchase reviews |

## 4. Scoring Calculation

### Layer 1: Regex Pre-filter

```
Regex Score = Base platform weight x 100 + positive signal score - negative signal score
```

### Layer 2: AI Semantic Deep Analysis (only for gray zone 30-85 scores)

```
AI Score = Tone authenticity (0-20) + Narrative logic (0-20) + Detail richness (0-20)
         + Emotional consistency (0-20) + Interest disclosure (0-20)
```

### Fusion Layer

```
With full text (≥200 chars): Final = Regex x 0.3 + AI x 0.7
With snippet only (<200 chars): Final = Regex x 0.6 + AI x 0.4
AI analysis failed/skipped: Final = Regex x 1.0 (fallback)
```

### Score Levels

Labels are read from `category_profile.report_labels`:
- 80+: High credibility — core reference
- 60-79: Medium credibility — supplementary reference
- 40-59: Low credibility — only when no better source available
- Below 40: Suspected ad/astroturfing — excluded
