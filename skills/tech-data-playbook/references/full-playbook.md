# Technology & Data Playbook — Full Reference Guide

## Table of Contents

1. Software Development Deep Dive
2. Cybersecurity Implementation Guide
3. Cloud Architecture Patterns
4. Data Platform Engineering
5. AI/ML Production Playbook
6. Automation & DevOps Mastery
7. Digital Transformation Execution
8. Technology Leadership & Communication
9. Vendor Evaluation Framework
10. Glossary of Key Terms

---

## 1. Software Development Deep Dive

### Git Branching Strategies

**Trunk-Based Development (Recommended for most teams)**
- Single main branch. Short-lived feature branches (< 1 day ideal, < 3 days max)
- Feature flags for incomplete work. Continuous integration to main
- Best for: experienced teams, CI/CD maturity, high deployment frequency

**GitFlow (For release-heavy products)**
- Main + Develop + Feature + Release + Hotfix branches
- More ceremony, more control. Good for versioned software products
- Best for: mobile apps, packaged software, teams with QA gates

**GitHub Flow (Simple middle ground)**
- Main + Feature branches. PR-based workflow. Deploy from main
- Best for: web applications, SaaS products, smaller teams

### Code Review Standards

Every PR review should check:
- Does it solve the stated problem?
- Is it tested adequately (unit + integration where appropriate)?
- Are there security implications (auth, input validation, data exposure)?
- Is the code readable and maintainable by someone who didn't write it?
- Does it follow team style guide and architectural patterns?
- Is there appropriate error handling and logging?
- Are there performance implications at scale?

Review turnaround target: < 4 hours for standard PRs, < 1 hour for hotfixes.

### Testing Pyramid

```
         /  E2E Tests  \        ← Few, slow, brittle, but essential
        / Integration   \       ← Moderate number, service boundaries
       /   Unit Tests    \      ← Many, fast, isolated, comprehensive
      ‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
```

| Test Type | Quantity | Speed | Scope | Tools |
|---|---|---|---|---|
| Unit | Hundreds–Thousands | Milliseconds | Single function/class | Jest, pytest, JUnit |
| Integration | Dozens–Hundreds | Seconds | Service boundaries, DB, APIs | Testcontainers, Supertest |
| E2E | Tens | Minutes | Full user workflows | Playwright, Cypress, Selenium |
| Contract | Dozens | Seconds | API compatibility | Pact, Prism |
| Performance | Few | Minutes–Hours | Load/stress scenarios | k6, Locust, Artillery |
| Security | Automated | Varies | SAST, DAST, SCA | Snyk, SonarQube, OWASP ZAP |

### API Design Standards

- **REST** — Resource-based. HTTP verbs. Status codes. The default for most APIs
- **GraphQL** — Client-driven queries. Good for complex UIs with varied data needs
- **gRPC** — Binary protocol. High performance. Service-to-service communication
- **Versioning** — URL-based (/v1/, /v2/) or header-based. Never break existing consumers
- **Documentation** — OpenAPI/Swagger for REST. Auto-generated from code. Always current
- **Rate Limiting** — Protect all public APIs. Return 429 with Retry-After header
- **Pagination** — Cursor-based preferred over offset. Consistent performance at scale

---

## 2. Cybersecurity Implementation Guide

### Security Architecture Layers

```
Layer 1: IDENTITY — Who are you? MFA, SSO, IAM, zero-trust identity
Layer 2: ENDPOINT — Device security, EDR, patch management, device trust
Layer 3: NETWORK — Segmentation, firewalls, VPN/ZTNA, DNS security
Layer 4: APPLICATION — SAST/DAST, WAF, API security, input validation
Layer 5: DATA — Encryption, DLP, classification, access control, backup
Layer 6: OPERATIONS — SIEM, SOC, incident response, threat intelligence
```

### NIST Cybersecurity Framework 2.0 (Six Functions)

**GOVERN** (New in 2.0 — The Foundation)
- Board-level cybersecurity oversight
- Risk tolerance defined and communicated
- Supply chain risk management
- Policy framework aligned with business strategy

**IDENTIFY**
- Asset inventory (hardware, software, data, people)
- Risk assessment methodology
- Business environment understanding
- Governance structure documentation

**PROTECT**
- Access control (RBAC, MFA, least privilege)
- Data security (encryption, DLP, backup)
- Security awareness training
- Protective technology (firewalls, WAF, EDR)

**DETECT**
- Continuous monitoring (SIEM, NDR, EDR)
- Anomaly detection (UEBA, AI-driven)
- Security event logging and correlation
- Threat intelligence integration

**RESPOND**
- Incident response planning and execution
- Communication protocols (internal + external)
- Forensic analysis capability
- Mitigation procedures

**RECOVER**
- Recovery planning and execution
- Backup restoration procedures
- Business continuity activation
- Lessons learned integration

### Supply Chain Security (SLSA Framework)

Software supply chain attacks are rising. Implement provenance at every stage:

| SLSA Level | Requirements |
|---|---|
| Level 1 | Documented build process. Provenance exists |
| Level 2 | Hosted build service. Signed provenance |
| Level 3 | Hardened build platform. Non-falsifiable provenance |
| Level 4 | Hermetic, reproducible builds. Two-party review |

Minimum actions:
- Generate and publish SBOMs (Software Bill of Materials) for all releases
- Sign all artifacts (Sigstore/cosign for containers)
- Scan dependencies continuously (Snyk, Dependabot, Renovate)
- Pin dependency versions. Audit transitive dependencies
- Use lockfiles. Verify checksums

---

## 3. Cloud Architecture Patterns

### Well-Architected Review Process

Run a Well-Architected Review (AWS, Azure, or GCP framework) quarterly:

1. Review each pillar against current architecture
2. Identify high-risk findings and improvement opportunities
3. Prioritise by business impact and effort
4. Create action items with owners and deadlines
5. Track remediation progress monthly

### Disaster Recovery Strategies

| Strategy | RPO | RTO | Cost | Use Case |
|---|---|---|---|---|
| Backup & Restore | Hours | Hours | Low | Non-critical workloads |
| Pilot Light | Minutes | 10–30 min | Medium-Low | Databases, core services |
| Warm Standby | Seconds–Minutes | Minutes | Medium | Business-critical apps |
| Multi-Site Active-Active | Near-zero | Near-zero | High | Revenue-critical, global apps |

RPO = Recovery Point Objective (how much data can you lose?)
RTO = Recovery Time Objective (how long until service is restored?)

### Container Orchestration (Kubernetes)

Core concepts every technology leader must understand:

| Concept | Purpose |
|---|---|
| Pod | Smallest deployable unit. One or more containers |
| Deployment | Manages replicas, rolling updates, rollbacks |
| Service | Stable network endpoint for a set of pods |
| Ingress | External access, routing, TLS termination |
| ConfigMap/Secret | Configuration and sensitive data management |
| Namespace | Logical isolation within a cluster |
| Horizontal Pod Autoscaler | Auto-scale based on CPU/memory/custom metrics |

### Serverless Architecture Patterns

When to use serverless (AWS Lambda, Azure Functions, Cloudflare Workers):
- API endpoints with variable traffic
- Event processing (file uploads, queue messages, webhooks)
- Scheduled tasks (cron jobs)
- Data transformation pipelines
- Rapid prototyping and MVPs

When NOT to use serverless:
- Long-running processes (> 15 min on most platforms)
- Consistent, high-throughput workloads (containers are more cost-effective)
- Workloads requiring specific runtime environments or GPU access
- Applications with strict cold-start latency requirements

---

## 4. Data Platform Engineering

### Data Modelling Approaches

**Star Schema (Kimball)**
- Fact tables (events, transactions) surrounded by dimension tables (who, what, when, where)
- Optimised for analytical queries and BI tools
- Best for: data warehouses serving business analysts

**Data Vault 2.0**
- Hubs (business keys) + Links (relationships) + Satellites (descriptive data)
- Highly auditable, historised, scalable
- Best for: enterprise data warehouses with complex, evolving sources

**One Big Table (OBT)**
- Pre-joined, denormalised table for specific analytics use cases
- Fast queries, simple for end users
- Best for: specific BI dashboards, self-service analytics

### dbt (Data Build Tool) Best Practices

dbt has become the standard for data transformation. Key practices:

- **Staging layer** — 1:1 with source tables. Rename, cast, basic cleaning
- **Intermediate layer** — Business logic, joins, aggregations
- **Marts layer** — Final, consumer-ready datasets organised by business domain
- **Tests** — Not-null, unique, accepted-values, relationships. Custom tests for business rules
- **Documentation** — Every model described. Column descriptions for key fields
- **Incremental models** — For large tables. Process only new/changed data
- **Snapshots** — Track slowly changing dimensions (SCD Type 2)

### Data Quality Framework

Implement automated quality checks at every stage:

| Dimension | Check | Example |
|---|---|---|
| Completeness | Missing values | order_id NOT NULL |
| Uniqueness | Duplicate records | COUNT(DISTINCT id) = COUNT(id) |
| Freshness | Data is current | max(updated_at) > now() - interval '1 hour' |
| Accuracy | Values are correct | revenue >= 0, date <= current_date |
| Consistency | Cross-source agreement | CRM count ≈ billing count (within 2%) |
| Validity | Values in expected range | country_code IN ('GB', 'US', 'ZM', ...) |

Tools: Great Expectations, Soda, dbt tests, Monte Carlo, Anomalo

### Real-Time Data Architecture

For real-time use cases (fraud detection, live dashboards, event-driven systems):

```
Sources → Kafka/Kinesis (Event Streaming) → Flink/ksqlDB (Stream Processing) →
  ├── Real-Time Serving (Redis, Elasticsearch)
  ├── Data Lake/Warehouse (Iceberg, Delta Lake) ← for batch + historical
  └── Alerts/Actions (PagerDuty, webhooks, automation)
```

---

## 5. AI/ML Production Playbook

### MLOps Maturity Levels

| Level | Description |
|---|---|
| 0 | Manual. Jupyter notebooks. No pipeline. Data scientist deploys manually |
| 1 | Basic pipeline. Automated training. Manual deployment. Some monitoring |
| 2 | Full CI/CD for ML. Automated training, testing, deployment. Feature store |
| 3 | Advanced. A/B testing, champion/challenger, automated retraining on drift |
| 4 | Autonomous. Self-healing models, automated feature engineering, continuous optimisation |

### Model Selection Framework

| Model Type | Use Case | Tools |
|---|---|---|
| Foundation Models (LLMs) | Text generation, summarisation, Q&A, code | GPT-4, Claude, Gemini, Llama, Mistral |
| Classical ML | Tabular data, prediction, classification | XGBoost, LightGBM, scikit-learn |
| Deep Learning | Computer vision, NLP, speech, complex patterns | PyTorch, TensorFlow |
| Time Series | Forecasting, anomaly detection | Prophet, NeuralProphet, statsmodels |
| Reinforcement Learning | Optimisation, game play, robotics | Stable Baselines, Ray RLlib |
| Embeddings + RAG | Enterprise search, knowledge retrieval | LangChain, LlamaIndex, vector DBs |

### RAG (Retrieval-Augmented Generation) Architecture

The dominant pattern for enterprise AI in 2026:

```
User Query → Embedding Model → Vector Search (Pinecone/Weaviate/pgvector) →
  Top-K Relevant Documents → LLM + Context → Generated Answer + Citations
```

Key implementation details:
- Chunk documents intelligently (semantic chunking > fixed-size)
- Use hybrid search (vector + keyword/BM25) for best recall
- Implement reranking for precision (Cohere Rerank, cross-encoder)
- Cache frequent queries to reduce latency and cost
- Monitor retrieval quality separately from generation quality
- Include source citations in outputs for trust and verification

### Responsible AI Checklist

Before deploying any AI system:
- [ ] Bias testing across protected attributes (gender, race, age, etc.)
- [ ] Explainability assessment (SHAP, LIME, attention maps)
- [ ] Privacy review (PII in training data, model memorisation)
- [ ] Security assessment (prompt injection, data extraction, adversarial attacks)
- [ ] Performance benchmarks on representative test sets
- [ ] Fallback mechanism when model confidence is low
- [ ] Human escalation path for high-stakes decisions
- [ ] Monitoring dashboard for production performance
- [ ] Model card documenting purpose, limitations, and intended use
- [ ] Legal review for regulatory compliance (EU AI Act, etc.)

---

## 6. Automation & DevOps Mastery

### GitOps Workflow

GitOps treats Git as the single source of truth for infrastructure and deployments:

```
Developer commits → Git repo (declarative desired state) → GitOps operator (ArgoCD/Flux) →
  Detects drift → Reconciles cluster state → Matches desired state → Done
```

Benefits: auditable history, rollback = git revert, consistent environments, PR-based changes.

### Chaos Engineering

Proactively test system resilience by intentionally introducing failures:

1. **Define steady state** — What does "healthy" look like? (SLOs, error rates, latency)
2. **Hypothesise** — "If X fails, the system should degrade gracefully to Y"
3. **Inject failure** — Kill pods, simulate network partition, corrupt data, increase latency
4. **Observe** — Did the system behave as expected? Did alerts fire? Did recovery work?
5. **Learn** — Fix weaknesses. Update runbooks. Repeat

Tools: Chaos Monkey (Netflix), Litmus, Gremlin, Chaos Mesh

Start small (one pod, one service) and increase scope as confidence grows.

### SRE Practices

| Practice | Description |
|---|---|
| SLIs | Service Level Indicators — the metrics you measure (latency, error rate, throughput) |
| SLOs | Service Level Objectives — the targets you set (99.9% availability, p99 < 200ms) |
| SLAs | Service Level Agreements — the contractual commitments to customers |
| Error Budgets | Remaining tolerance before SLO is breached. Budget remaining = innovation velocity |
| Toil Reduction | Automate repetitive, manual operational work. Target < 50% time on toil |
| Blameless Post-Mortems | Focus on systems, not people. What failed? How do we prevent it? |

---

## 7. Digital Transformation Execution

### 90-Day Transformation Sprint Template

**Days 1–30: ASSESS**
- Map current state (systems, processes, data, pain points)
- Interview stakeholders across all functions
- Identify quick wins (high impact, low effort)
- Benchmark against industry standards
- Deliverable: Current State Assessment + Opportunity Map

**Days 31–60: DESIGN**
- Define target architecture (not perfect, directional)
- Select 2–3 quick-win projects to demonstrate value
- Build business cases with measurable KPIs
- Identify technology and talent gaps
- Deliverable: Strategic Roadmap + Quick-Win Project Plans

**Days 61–90: DELIVER**
- Execute quick-win projects
- Establish governance cadence (weekly standups, monthly reviews)
- Launch upskilling programme for key roles
- Communicate early results to build momentum
- Deliverable: Working Quick Wins + Governance Framework + Momentum

### Technology Due Diligence Framework

When evaluating technology investments, acquisitions, or vendor selections:

| Category | Questions |
|---|---|
| Architecture | Monolith vs microservices? Tech debt level? Scalability ceiling? |
| Security | Pen test results? Compliance certifications? Incident history? |
| Data | Quality score? Governance maturity? Single source of truth? |
| Team | Key person risk? Skill gaps? Documentation quality? |
| Infrastructure | Cloud-native or legacy? IaC coverage? DR tested? |
| DevOps | DORA metrics? Deployment frequency? Automation level? |
| Cost | Unit economics? Cloud spend trend? Build vs buy decisions? |

---

## 8. Technology Leadership & Communication

### Communicating with the Board

Boards care about: Risk, Revenue, Cost, and Competitive Position.

Translate technology topics:
- "We need Kubernetes" → "We need to reduce deployment time from days to minutes to ship features faster"
- "Our technical debt is high" → "Without investment, our time-to-market will increase 3x in 18 months"
- "We should adopt AI" → "AI can reduce customer service costs by 30% and improve response times by 60%"

### Technology Investment Framing

Always present technology investments as:
1. **The Business Problem** — What pain or opportunity exists?
2. **The Cost of Inaction** — What happens if we do nothing?
3. **The Proposed Solution** — What are we recommending?
4. **The Expected ROI** — What measurable outcomes will we deliver, and when?
5. **The Risk Mitigation** — What could go wrong and how will we handle it?

---

## 9. Vendor Evaluation Framework

| Criterion | Weight | Evaluation Method |
|---|---|---|
| Functionality Fit | 25% | Feature matrix, demo scoring, POC results |
| Security & Compliance | 20% | SOC 2, ISO 27001, pen test results, data residency |
| Integration | 15% | API quality, existing integrations, developer documentation |
| Total Cost of Ownership | 15% | License + implementation + training + maintenance over 3 years |
| Scalability | 10% | Performance benchmarks, customer references at scale |
| Vendor Viability | 10% | Financial health, market position, roadmap alignment |
| Support & SLA | 5% | Response times, escalation path, dedicated account team |

Never evaluate a vendor on a demo alone. Always run a paid proof-of-concept with real data.

---

## 10. Glossary of Key Terms

| Term | Definition |
|---|---|
| ADR | Architecture Decision Record — documented technical decision with context and rationale |
| CI/CD | Continuous Integration / Continuous Deployment — automated build, test, deploy pipeline |
| DORA | DevOps Research and Assessment — four key metrics for software delivery performance |
| EDR | Endpoint Detection & Response — security tool monitoring and responding to endpoint threats |
| FinOps | Cloud financial management discipline uniting engineering, finance, and business |
| GitOps | Infrastructure and deployment management through Git as single source of truth |
| IaC | Infrastructure as Code — managing infrastructure through version-controlled code |
| IDP | Internal Developer Platform — self-service platform engineering for developers |
| KEV | Known Exploited Vulnerability — CISA catalogue of actively exploited vulnerabilities |
| MLOps | Machine Learning Operations — DevOps practices applied to ML model lifecycle |
| NLQ | Natural Language Querying — asking data questions in plain language |
| OKR | Objectives and Key Results — goal-setting framework linking strategy to measurable outcomes |
| RAG | Retrieval-Augmented Generation — combining search with LLMs for grounded AI responses |
| RBAC | Role-Based Access Control — permissions assigned by role, not by individual |
| SBOM | Software Bill of Materials — inventory of all components in a software package |
| SLI/SLO/SLA | Service Level Indicator/Objective/Agreement — reliability measurement and commitment |
| SLSA | Supply-chain Levels for Software Artifacts — framework for supply chain security |
| TOGAF | The Open Group Architecture Framework — enterprise architecture methodology |
| ZTNA | Zero Trust Network Access — secure access model replacing traditional VPN |

---

**The best technology leaders are not the ones who know every tool. They are the ones who
ask the right questions, make decisions with incomplete information, communicate clearly,
and build teams that can execute. Tools change. Principles endure.**
