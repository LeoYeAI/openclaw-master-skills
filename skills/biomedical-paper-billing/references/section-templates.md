# Section Templates

## Abstract (GBD epidemiology style)

```
**Background:** [Disease X] is [brief definition and global significance]. Comparative analyses of [metric] between [countries/regions] remain limited. Using [GBD year] data, this study characterised [outcome] in [countries] from [year] to [year], with projections to [year].

**Methods:** [Key data extracted]. [Statistical methods: Joinpoint, ARIMA, decomposition, attribution]. All rates are per 100,000 population.

**Results:** From [year] to [year], [Country A] showed [key finding with numbers and CI/AAPC]. [Country B] showed [key finding]. [Projection result]. [Decomposition result]. [Attribution result].

**Conclusions:** [Burden level comparison]. [Divergent future trajectories]. [Mechanistic difference]. These findings provide evidence for [policy implication].
```

## Introduction

**Paragraph 1 — Disease overview:**
[Disease] is [definition] and [global significance/ranking]. Patients typically [clinical course]. Despite effective treatment, [residual burden: % unable to walk/mortality]. [Pathogenesis: antecedent trigger → immune mechanism]. [Recent etiological context: COVID-19/vaccine].

**Paragraph 2 — Epidemiological context + population aging:**
The epidemiology of [disease] varies substantially [geographic pattern]. [Subtype differences: country A vs country B]. [Aging as driver, cite GBD nervous system paper]. [COVID-19 pandemic impact, cite recent paper].

**Paragraph 3 — Research gap:**
Despite [context], long-term comparative analyses of [disease] burden between countries at [different SDI/development stage] remain limited. Most existing studies are [regional/cross-sectional/limited duration]. [Country A], [description]; [Country B], [description]. These contrasting settings offer a unique framework for [research rationale].

**Paragraph 4 — Study aims:**
Using [GBD year] data, this study aimed to: (i) characterise [outcome 1]; (ii) project [outcome 2]; (iii) quantify [decomposition]; and (iv) identify [attribution].

## Methods: Data Source

```
All data were extracted from the publicly available GBD [year] database (http://ghdx.healthdata.org/gbd-results-tool). The GBD study integrates multiple epidemiological data sources—including population registries, surveys, published literature, hospital records, and cause-of-death data—using standardised modelling frameworks to generate comparable burden estimates across countries and time periods. [Disease] was identified using ICD-10 code [X] and ICD-9 code [Y]. Four primary outcomes were extracted for [Countries] for [years]: prevalence case counts, YLDs case counts, age-standardized prevalence rates, and age-standardized YLDs rates, all expressed per 100,000 population, standardised against the GBD global standard population. This study used publicly available, de-identified aggregate data and received ethical clearance from the Institutional Review Board of the University of Washington; no additional ethical approval was required.
```

## Methods: Statistical Analysis — Joinpoint

```
Joinpoint regression was applied to age-standardized [rate] from [years] to identify statistically significant trend breakpoints. The optimal number of joinpoints was determined via Monte Carlo permutation tests. APC and 95% confidence intervals (CIs) were estimated for each trend segment; AAPC was calculated across the full study period to summarise the overall direction and magnitude of change.
```

## Methods: Statistical Analysis — ARIMA

```
Autoregressive integrated moving average (ARIMA) models were fitted to age-standardized GBS YLDs rates for each country using [years] historical data. Optimal model orders (p, d, q) were selected by the auto.arima algorithm based on the Akaike Information Criterion (AIC) and Bayesian Information Criterion (BIC). Forecasts for [years] are presented as point estimates with 95% prediction intervals (PIs).
```

## Methods: Demographic Decomposition

```
To disentangle the contributions of demographic and epidemiological factors to changes in total [disease]-related YLDs between [years], a standard three-component decomposition method was applied [cite]:

ΔYLDs = f(population growth) + f(population ageing) + f(age-specific rate change)

Population growth captures the effect of overall population size change; population ageing captures shifts in age structure; and age-specific rate change reflects the net epidemiological contribution independent of demographic factors.
```

## Discussion: Opening Paragraph (Core Findings)

```
This study provides [first/most comprehensive] longitudinal comparison of [disease] burden between [countries], integrating [N] years of historical data with [N]-year forward projections. Three key findings emerge. First, [burden level finding with magnitude]. Second, [trajectory finding: stable vs. rising]. Third, [mechanistic/driver finding: fundamental difference].
```

## Discussion: Limitations Paragraph

```
Several limitations should be acknowledged. First, GBD estimates for [rare/common] conditions carry inherent model-based uncertainty, particularly in settings with sparse primary epidemiological data; [specific issue, e.g., underdiagnosis in Country X] may lead to systematic [over/under]estimation. Second, the ecological study design precludes causal inference. Third, [disease-specific limitation, e.g., cannot distinguish subtypes]. Fourth, ARIMA projections assume continuation of historical trends and cannot fully account for future disruptions such as [new pandemic/policy changes].
```

## Discussion: Conclusion Paragraph

```
In conclusion, [main burden comparison finding]. [Divergent trajectory statement]. The mechanistic pathways driving burden change differ fundamentally: [Country A] is shaped by [driver], while [Country B]'s burden is primarily driven by [driver], with [offset factor] largely [containing/exacerbating] the total impact. These findings provide a critical evidence base for country-specific, targeted [disease] prevention and management strategies, and highlight the need for enhanced [surveillance/collaboration/research].
```
