# Analysis Techniques — When to Use Each

## Hypothesis Testing

**Use when:** Comparing two groups to determine if a difference is real or random chance.

**Technique selection:**
| Data type | Groups | Test |
|-----------|--------|------|
| Continuous | 2 | t-test (if normal) or Mann-Whitney |
| Continuous | 3+ | ANOVA or Kruskal-Wallis |
| Proportions | 2 | Chi-square or Fisher's exact |
| Paired data | 2 | Paired t-test or Wilcoxon signed-rank |

**Key outputs:**
- p-value (probability of seeing this difference by chance)
- Effect size (how big is the difference — Cohen's d, odds ratio)
- Confidence interval (range of plausible true values)

**Watch out for:**
- Large samples make everything "significant" — focus on effect size
- Multiple comparisons inflate false positives
- Normality assumptions (use non-parametric if violated)

---

## Cohort Analysis

**Use when:** Understanding how user behavior changes over time, segmented by when they started.

**Types:**
- **Retention cohorts:** % of users still active N days after signup
- **Revenue cohorts:** Revenue per cohort over time
- **Behavioral cohorts:** Feature adoption by signup cohort

**Setup:**
1. Define cohort (usually signup week/month)
2. Define event (login, purchase, specific action)
3. Define time windows (day 1, 7, 30, 90)
4. Build matrix: cohort × time period

**Key outputs:**
- Retention curves (line chart by cohort)
- Cohort comparison (are newer cohorts performing better?)
- Time-to-event patterns

**Watch out for:**
- Cohort size differences (small cohorts = noisy data)
- Seasonality (December cohort behaves differently)
- Definition consistency (what counts as "active"?)

---

## Funnel Analysis

**Use when:** Understanding conversion through a multi-step process.

**Setup:**
1. Define stages (visit → signup → activate → purchase)
2. Count users at each stage
3. Calculate drop-off rates between stages

**Key outputs:**
- Conversion rates per stage
- Biggest drop-off points
- Segment comparison (mobile vs desktop funnels)

**Watch out for:**
- Time window (did they convert eventually, or just not today?)
- Stage ordering (users don't always follow linear paths)
- Defining "same session" vs "ever"

---

## Regression Analysis

**Use when:** Understanding what predicts an outcome, controlling for other factors.

**Types:**
- **Linear:** Continuous outcome (revenue, time spent)
- **Logistic:** Binary outcome (churned/retained, converted/didn't)
- **Poisson:** Count outcome (purchases, logins)

**Key outputs:**
- Coefficients (effect of each variable, holding others constant)
- R² (how much variance is explained)
- p-values per variable
- Residual plots (are assumptions met?)

**Watch out for:**
- Multicollinearity (correlated predictors)
- Omitted variable bias (missing important controls)
- Extrapolation beyond data range
- Causation claims from observational data

---

## Segmentation/Clustering

**Use when:** Discovering natural groups in your data.

**Techniques:**
- **K-means:** Simple, fast, assumes spherical clusters
- **Hierarchical:** Shows cluster relationships, good for exploration
- **RFM:** Business-specific (Recency, Frequency, Monetary)

**Process:**
1. Select features (what defines a segment?)
2. Normalize features (so scale doesn't dominate)
3. Choose number of clusters (elbow method, silhouette score)
4. Profile each cluster (what makes them different?)

**Key outputs:**
- Cluster profiles (avg values per segment)
- Segment sizes
- Distinguishing characteristics

**Watch out for:**
- Garbage in, garbage out (feature selection matters)
- Cluster count is subjective
- Stability (do clusters hold with different random seeds?)

---

## Anomaly Detection

**Use when:** Finding unusual data points that warrant investigation.

**Approaches:**
- **Statistical:** Points beyond 2-3 standard deviations
- **IQR method:** Below Q1-1.5×IQR or above Q3+1.5×IQR
- **Isolation Forest:** For multivariate anomalies
- **Domain rules:** Negative revenue, future dates, impossible values

**Key outputs:**
- Flagged records with anomaly scores
- Context (why is this unusual?)
- Severity (how far from normal?)

**Watch out for:**
- Seasonality (Black Friday isn't an anomaly)
- Trends (growth makes old "normal" look like anomalies)
- False positives (investigate before acting)

---

## Time Series Analysis

**Use when:** Understanding patterns in data over time.

**Components:**
- **Trend:** Long-term direction
- **Seasonality:** Repeating patterns (daily, weekly, yearly)
- **Noise:** Random variation

**Techniques:**
- **Moving averages:** Smooth out noise
- **Decomposition:** Separate trend, seasonal, residual
- **Year-over-year:** Compare same period last year

**Key outputs:**
- Trend direction and strength
- Seasonal patterns identified
- Forecast with uncertainty bands

**Watch out for:**
- Comparing different lengths (months vary in days)
- Holidays/events (one-time vs recurring)
- Structural breaks (COVID, product changes)
