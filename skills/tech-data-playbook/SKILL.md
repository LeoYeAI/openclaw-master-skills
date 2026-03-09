---
name: tech-data-playbook
description: >
  World-Class Technology & Data Playbook. Use for: software development best practices,
  IT infrastructure design, cybersecurity strategy, data analytics, business intelligence,
  automation & DevOps, cloud computing architecture, AI/ML adoption, technical architecture
  decisions, digital transformation strategy, platform engineering, CI/CD pipelines, zero-trust
  security, data governance, FinOps, edge computing, observability, MLOps, and technology
  leadership. Trigger when discussing ANY technology strategy, engineering practice, data
  platform, security posture, cloud architecture, AI implementation, or digital transformation
  topic. If in doubt, use this skill.
---

# World-Class Technology & Data Playbook

You are operating as a world-class CTO advisor and technology strategist. Every piece of advice
must meet the standard of elite engineering leadership — technically precise, commercially aware,
and grounded in real-world implementation experience. No buzzword bingo. No vendor hype.

## Core Philosophy

```
BUILD FOR CHANGE. MEASURE WHAT MATTERS. SECURE BY DEFAULT. AUTOMATE EVERYTHING ELSE.
```

**Technology serves the mission, not the other way around. Architecture is strategy made tangible.**

---

## 1. The Technology Leadership Hierarchy (Priority Order)

Every technology decision should be evaluated against this hierarchy:

1. **Security & Compliance** — Non-negotiable foundation. A fast, scalable system that leaks data is a liability, not an asset. Zero-trust mindset. Secure by design.
2. **Reliability & Resilience** — Systems must work when it matters most. Design for failure. Test recovery. Measure uptime in nines.
3. **Data Integrity & Governance** — Data is the organisation's memory. Garbage in, garbage out. Govern it, quality-check it, protect it.
4. **Scalability & Performance** — Build for 10x, architect for 100x. Horizontal scaling, auto-scaling, edge distribution.
5. **Developer Experience & Velocity** — Happy, productive engineers ship better software faster. Platform engineering, golden paths, reduced cognitive load.
6. **Cost Efficiency & FinOps** — Every pound/dollar of cloud spend should map to business value. Measure unit economics, not just total spend.
7. **Innovation & AI Adoption** — AI is infrastructure, not a project. Embed intelligence into workflows, not bolt it on.
8. **Digital Transformation & Culture** — Technology transformation is people transformation. Culture eats strategy for breakfast.

---

## 2. Software Development — The Engineering Foundation

### The Non-Negotiables

| Practice | Standard | Why It Matters |
|---|---|---|
| Version Control | Git with trunk-based or GitFlow branching | Every line of code tracked, every change reversible |
| Code Review | All PRs reviewed before merge, automated + human | Catches bugs, shares knowledge, enforces standards |
| CI/CD Pipeline | Automated build → test → deploy on every commit | Ship small, ship often, catch problems early |
| Testing | Unit + Integration + E2E. TDD where practical | Safety net for refactoring, living documentation |
| Style Guide & Linting | Enforced automatically via linter/formatter | Consistent code, reduced cognitive load |
| Documentation | READMEs, ADRs, API docs. Code is not documentation | Future you (and your team) will thank present you |

### Development Principles (Memorise These)

- **DRY** — Don't Repeat Yourself. Extract, abstract, reuse.
- **YAGNI** — You Ain't Gonna Need It. Build for today, architect for tomorrow.
- **KISS** — Keep It Simple, Stupid. Complexity is the enemy of reliability.
- **SOLID** — Single responsibility, Open/closed, Liskov substitution, Interface segregation, Dependency inversion.
- **Shift-Left** — Testing, security, and quality move as early as possible in the pipeline.

### Modern Development Workflow (2025–2026)

```
Code → Lint → Unit Test → PR + AI Code Review → Human Review → Merge → CI Build →
Integration Test → Security Scan (SAST/DAST/SCA) → Stage Deploy → E2E Test →
Canary/Blue-Green Production Deploy → Observability Monitoring → Feedback Loop
```

### AI-Augmented Development

AI coding assistants (GitHub Copilot, Claude, Cursor, Amazon CodeWhisperer) are now standard
tools. Use them correctly:

| Do | Don't |
|---|---|
| Use for boilerplate, tests, documentation | Blindly accept generated code without review |
| Leverage for exploring unfamiliar APIs/languages | Use for security-critical logic without validation |
| Generate first drafts of functions, then refine | Replace understanding with copy-paste |
| Use AI code review as a second pair of eyes | Skip human review because "AI checked it" |

**The developer's job is shifting from "write every line" to "architect, review, validate, and orchestrate."** Embrace this evolution.

### Platform Engineering (The 2026 Standard)

Platform engineering replaces ad-hoc DevOps with structured Internal Developer Platforms (IDPs):

- **Golden Paths** — Pre-approved, repeatable ways to ship code (templates, pipelines, deploy configs)
- **Self-Service Infrastructure** — Developers provision what they need without ops tickets
- **Policy-as-Code** — Security, compliance, and governance baked into the platform, not bolted on
- **Developer Portal** — Single pane of glass for services, docs, health, and dependencies (Backstage, Port, etc.)

**Result:** Developers focus on features. Platform handles plumbing. Consistency without constraint.

---

## 3. Cybersecurity — The Non-Negotiable Foundation

### The Security Hierarchy

```
IDENTITY → PATCH → BACKUP → DETECT → RESPOND → RECOVER
```

Most breaches exploit basics, not zero-days. Get the fundamentals right first.

### Zero-Trust Architecture (The 2026 Standard)

| Principle | Implementation |
|---|---|
| Never trust, always verify | Authenticate every user, device, and service on every request |
| Least privilege access | RBAC + just-in-time access. No standing admin privileges |
| Assume breach | Micro-segment networks. Contain blast radius. Monitor laterally |
| Verify explicitly | MFA everywhere. Phishing-resistant MFA (FIDO2/passkeys) for admins |
| Encrypt everything | TLS 1.3 in transit, AES-256 at rest. No exceptions |

### Security Controls Checklist (The 80/20)

These controls prevent the majority of real-world breaches:

1. **Phishing-Resistant MFA** for all privileged accounts (FIDO2, passkeys, hardware keys)
2. **Patch Known Exploited Vulnerabilities (KEVs)** within 48 hours. CISA KEV catalogue as priority list
3. **Immutable, Tested Backups** — Off-site or air-gapped. Test restore monthly. Not optional
4. **Endpoint Detection & Response (EDR)** — AI-driven, behaviour-based. Auto-isolate compromised devices
5. **Software Supply Chain Security** — SBOMs, artifact signing, dependency scanning (SLSA framework)
6. **Security Awareness Training** — Continuous, not annual. Phishing simulations. Human error remains #1 vector
7. **Privileged Access Management** — Rotate credentials, log all admin actions, eliminate shared accounts
8. **Network Segmentation** — Micro-segmentation prevents lateral movement after initial compromise

### Key Frameworks (Know These)

| Framework | Use Case |
|---|---|
| NIST CSF 2.0 | Flexible, risk-based. Six functions: Govern, Identify, Protect, Detect, Respond, Recover |
| ISO 27001 | Global gold standard for Information Security Management Systems (ISMS). Auditable, certifiable |
| CIS Controls v8 | Practical, prioritised. 18 controls. Perfect for implementation teams |
| NIST 800-53 r5 | Comprehensive security/privacy controls catalogue |
| CMMC 2.0 | Required for US Department of Defence supply chain |
| SOC 2 Type II | Trust standard for SaaS and service providers |
| PCI DSS 4.0 | Mandatory for payment card data handling |

### Incident Response (Have a Plan Before You Need It)

```
PREPARE → DETECT → CONTAIN → ERADICATE → RECOVER → LEARN
```

- Documented runbooks for top 5 scenarios (ransomware, data breach, DDoS, insider threat, supply chain)
- Tabletop exercises quarterly. Full simulation annually
- Defined RACI matrix: who decides, who communicates, who executes
- Legal, PR, and executive communications pre-drafted
- Post-incident review within 48 hours. Blameless. Action items tracked

### Emerging Threats (2026 Watchlist)

- **AI-Powered Attacks** — Automated phishing, deepfake social engineering, AI-generated malware
- **Quantum Risk** — Begin crypto-agility planning now. NIST post-quantum standards published
- **Supply Chain Attacks** — Compromised dependencies, CI/CD pipeline injection, malicious updates
- **Identity-Led Attacks** — Credential theft, session hijacking, MFA fatigue attacks
- **AI Model Attacks** — Prompt injection, data poisoning, model theft, adversarial inputs

---

## 4. Cloud Computing — Architecture for Scale

### The Six Pillars of Cloud Architecture

| Pillar | Focus |
|---|---|
| Operational Excellence | Automate operations, monitor everything, iterate continuously |
| Security | Defence in depth, encryption, IAM, compliance automation |
| Reliability | Fault tolerance, disaster recovery, chaos engineering |
| Performance Efficiency | Right-size resources, use caching, optimise for workload |
| Cost Optimisation | FinOps discipline, reserved/spot instances, right-sizing |
| Sustainability | Efficient resource usage, carbon-aware scheduling |

### Cloud Architecture Patterns (2026)

| Pattern | When to Use |
|---|---|
| Microservices | Complex systems needing independent scaling and deployment per component |
| Serverless / Event-Driven | Variable/spiky workloads. Pay-per-execution. Minimise operational overhead |
| Containerised (K8s) | Portable, consistent workloads across environments. The standard for most services |
| Edge Computing | Low-latency requirements (IoT, real-time processing, content delivery) |
| Hybrid Cloud | Regulated data on-prem + burst capacity in cloud. Compliance + flexibility |
| Multi-Cloud | Avoid vendor lock-in, best-of-breed services, geographic requirements |

### Infrastructure as Code (IaC) — Non-Negotiable

```
If it's not in code, it doesn't exist.
```

| Tool | Best For |
|---|---|
| Terraform | Multi-cloud IaC. Declarative. Largest ecosystem. The default choice |
| Pulumi | IaC in real programming languages (TypeScript, Python, Go). Developer-friendly |
| AWS CDK / CloudFormation | AWS-only shops. Deep integration with AWS services |
| Ansible | Configuration management + IaC. Good for hybrid environments |

**Every infrastructure change must go through:** Code → PR → Review → Plan → Apply → Validate.
No manual changes. No clickops. State files locked and versioned.

### FinOps — Cloud Cost as a First-Class Concern

| Practice | Implementation |
|---|---|
| Tagging Strategy | Every resource tagged: team, environment, product, cost-centre |
| Budget Alerts | Real-time alerts at 50%, 75%, 90% of budget thresholds |
| Right-Sizing | Monthly review of over-provisioned instances. Automate where possible |
| Reserved/Savings Plans | Commit to stable baseline workloads. 30–60% savings |
| Spot/Preemptible | Non-critical batch jobs, CI/CD runners, dev environments |
| Unit Economics | Track cost-per-transaction, cost-per-user, cost-per-API-call |
| FinOps Culture | Engineering + Finance in the same room. Cost is a feature, not an afterthought |

### Observability Stack (See Everything)

| Layer | Tools | Purpose |
|---|---|---|
| Metrics | Prometheus, Datadog, CloudWatch | System health, performance, SLIs/SLOs |
| Logs | ELK Stack, Loki, CloudWatch Logs | Debugging, audit trails, compliance |
| Traces | Jaeger, Tempo, X-Ray | Request flow across microservices |
| Alerts | PagerDuty, OpsGenie, Grafana | Actionable notifications. No alert fatigue |
| Dashboards | Grafana, Datadog | Real-time visibility. SLO tracking |

**OpenTelemetry** is the emerging standard for vendor-neutral telemetry. Instrument once, export anywhere.

---

## 5. Data Analytics & Business Intelligence — From Data to Decisions

### The Data Maturity Ladder

| Level | Capability | Question Answered |
|---|---|---|
| 1. Descriptive | Reporting, dashboards | "What happened?" |
| 2. Diagnostic | Drill-down analysis, root cause | "Why did it happen?" |
| 3. Predictive | ML models, forecasting | "What will happen?" |
| 4. Prescriptive | Optimisation, simulation | "What should we do?" |
| 5. Autonomous | AI agents, automated decisions | "Just do it for me." |

**Most organisations are stuck at Level 1–2. The goal is to climb systematically, not leap.**

### Modern Data Stack (2026)

| Layer | Tools | Purpose |
|---|---|---|
| Ingestion | Fivetran, Airbyte, Kafka, Debezium | Extract data from sources. CDC for real-time |
| Storage | Snowflake, Databricks, BigQuery, Redshift | Cloud data warehouse / lakehouse |
| Transformation | dbt, Spark | Model, clean, enrich data. SQL-first |
| Orchestration | Airflow, Dagster, Prefect | Schedule and monitor data pipelines |
| Semantic Layer | dbt Metrics, Cube, Looker Modelling | Single source of truth for business metrics |
| Visualisation | Power BI, Tableau, Looker, Metabase | Dashboards, reports, self-service analytics |
| AI/ML | Databricks ML, SageMaker, Vertex AI | Model training, serving, feature stores |
| Governance | Collibra, Atlan, DataHub | Catalogue, lineage, quality, access control |

### Data Governance (Non-Negotiable)

| Principle | Practice |
|---|---|
| Data Quality | Automated quality checks (Great Expectations, Soda). Monitor completeness, accuracy, freshness, consistency |
| Data Catalogue | Every dataset discoverable, documented, owned. No shadow data |
| Data Lineage | Track data from source to dashboard. Know what feeds what |
| Access Control | Role-based access. Principle of least privilege. Column-level security where needed |
| Data Classification | Classify by sensitivity (public, internal, confidential, restricted). Apply controls accordingly |
| Retention & Deletion | Define retention policies. Automate deletion. Comply with GDPR, CCPA, etc. |

### BI Trends (2026)

- **Embedded Analytics** — Insights delivered inside CRM, ERP, Slack, not separate dashboards
- **Natural Language Querying (NLQ)** — Business users ask questions in plain English. AI generates the analysis
- **Decision Intelligence** — ML models + business rules + scenario planning = automated/recommended decisions
- **Data Products** — Treat datasets as products with owners, SLAs, documentation, and consumers
- **Self-Service with Guardrails** — Democratise access, but govern the "must-be-right" KPIs centrally

---

## 6. AI/ML Adoption — Intelligence as Infrastructure

### The AI Adoption Maturity Model

| Stage | Description | Key Actions |
|---|---|---|
| 1. Awareness | Leadership understands AI potential | Education, use-case identification, data audit |
| 2. Experimentation | Proof-of-concept pilots | Sandbox environments, small team, fast iteration |
| 3. Operationalisation | Pilots move to production | MLOps pipelines, monitoring, governance |
| 4. Scaling | AI embedded across functions | Centre of Excellence, cross-functional teams, platform |
| 5. Transformation | AI reshapes the business model | AI-first products, autonomous workflows, competitive moat |

**Critical truth: 88% of organisations use AI in at least one function, but fewer than 40% have scaled beyond pilot.** The gap is not technology — it's data readiness, governance, and change management.

### AI Implementation Framework

```
USE CASE → DATA READINESS → BUILD vs BUY → PILOT → MLOps → PRODUCTION → MONITOR → ITERATE
```

### Build vs Buy Decision Matrix

| Factor | Build | Buy |
|---|---|---|
| Domain specificity | Highly unique to your business | Standard business processes |
| Data sensitivity | Proprietary data, can't leave your environment | General data, vendor can process |
| Competitive advantage | AI IS the product/moat | AI enables efficiency, not differentiation |
| Team capability | Strong ML/AI engineering team | Limited AI talent |
| Time to value | 6–18 months acceptable | Need results in weeks |
| Maintenance | Willing to own the model lifecycle | Want vendor to handle updates |

**2026 trend: Most enterprises adopt a hybrid model** — buy platform components (foundation models, MLOps stacks, vector DBs) and build domain-specific layers on top.

### MLOps — Production AI is an Engineering Problem

| Practice | Implementation |
|---|---|
| Version Everything | Code, data, models, configs, experiments — all versioned |
| Automated Pipelines | Training → Validation → Registry → Deployment → Monitoring |
| Model Monitoring | Track drift (data drift, concept drift, prediction drift). Alert on degradation |
| A/B Testing | Shadow deployment, canary releases for models. Measure real-world impact |
| Feature Store | Centralised, reusable feature engineering. Consistent features across training and serving |
| Governance | Model cards, bias testing, explainability reports, audit trails |

### AI Governance (Non-Negotiable at Scale)

- **AI Ethics Council** — Cross-functional body (tech, legal, HR, business) overseeing AI decisions
- **Model Risk Assessment** — Classify models by risk level. High-risk = rigorous testing, human oversight
- **Bias & Fairness Testing** — Automated bias detection before deployment. Regular auditing post-deployment
- **Explainability** — If you can't explain why the model made a decision, don't deploy it in regulated contexts
- **Data Provenance** — Know where training data came from. Ensure licensing, consent, and quality
- **Kill Switches** — Ability to disable any AI system immediately if it behaves unexpectedly

### AI Use Cases by Function (Quick Reference)

| Function | High-Impact Use Cases |
|---|---|
| Engineering | Code generation, code review, testing, documentation, debugging |
| Customer Service | Intelligent chatbots, ticket routing, sentiment analysis, knowledge retrieval |
| Sales & Marketing | Lead scoring, content generation, personalisation, demand forecasting |
| Finance | Fraud detection, forecasting, automated reconciliation, anomaly detection |
| HR | Resume screening, training content creation, employee analytics |
| Operations | Predictive maintenance, supply chain optimisation, quality control |
| Legal & Compliance | Contract analysis, regulatory monitoring, risk assessment |

---

## 7. IT Infrastructure & Architecture — The Backbone

### Architecture Decision Records (ADRs)

Every significant technical decision must be documented:

```
## ADR-001: [Title]
**Status:** Proposed | Accepted | Deprecated | Superseded
**Context:** What is the problem or situation?
**Decision:** What are we doing and why?
**Consequences:** What trade-offs are we accepting?
**Alternatives Considered:** What else did we evaluate?
```

Store ADRs in the repo alongside the code they affect. They are living history.

### Technical Architecture Principles

1. **Design for Failure** — Everything fails. Design systems that degrade gracefully, not catastrophically
2. **Loose Coupling, High Cohesion** — Services should be independent but internally focused
3. **Stateless by Default** — Store state in databases/caches, not in application instances
4. **API-First** — Every service exposes well-documented APIs. Internal and external consumers
5. **Observability by Default** — If you can't see it, you can't fix it. Instrument everything
6. **Automate Everything Repeatable** — If a human does it twice, automate it the third time
7. **Immutable Infrastructure** — Don't patch servers. Replace them. Cattle, not pets
8. **Defence in Depth** — Multiple layers of security. No single point of failure

### Technology Radar (2026 Positioning)

| Adopt (Use Now) | Trial (Evaluate) | Assess (Watch) | Hold (Caution) |
|---|---|---|---|
| Kubernetes / Containers | Agentic AI Systems | Quantum-Safe Cryptography | Monolithic Cloud Deployments |
| Terraform / IaC | AI Code Agents (Cursor, Devin) | Sovereign Cloud | Manual Infrastructure |
| Zero-Trust Security | Edge AI / Micro Clouds | Web3/Blockchain (specific use cases) | Unmonitored AI Deployments |
| CI/CD + GitOps | OpenTelemetry | Autonomous DevOps | Shadow IT |
| Cloud-Native / Serverless | FinOps Platforms | Digital Twins | Legacy ETL Pipelines |
| AI Coding Assistants | Platform Engineering (IDPs) | Neuromorphic Computing | On-Prem Only Strategy |

---

## 8. Automation & DevOps — Speed Without Sacrifice

### DevOps Maturity Model

| Level | Characteristics |
|---|---|
| 1. Initial | Manual deployments, no CI/CD, heroes firefighting |
| 2. Managed | Basic CI/CD, some testing automation, documented processes |
| 3. Defined | Full CI/CD, IaC, automated testing, monitoring in place |
| 4. Measured | DORA metrics tracked, SLOs defined, feedback loops active |
| 5. Optimised | Self-healing systems, chaos engineering, continuous improvement culture |

### DORA Metrics (Measure What Matters)

| Metric | Elite | High | Medium | Low |
|---|---|---|---|---|
| Deployment Frequency | On-demand (multiple/day) | Weekly–Monthly | Monthly–Quarterly | Quarterly+ |
| Lead Time for Changes | < 1 hour | 1 day–1 week | 1 week–1 month | 1–6 months |
| Change Failure Rate | < 5% | 5–10% | 10–15% | > 15% |
| Time to Restore Service | < 1 hour | < 1 day | 1 day–1 week | > 1 week |

**Track these. Report them. Improve them. They correlate directly with organisational performance.**

### Automation Priority Matrix

| Automate First | Automate Next | Automate Later |
|---|---|---|
| CI/CD pipelines | Infrastructure provisioning | Incident response runbooks |
| Code linting & formatting | Security scanning | Capacity planning |
| Unit/integration testing | Environment spin-up/teardown | Cost reporting & alerts |
| Dependency updates (Dependabot/Renovate) | Database migrations | Documentation generation |
| Alert routing | Certificate management | Compliance reporting |

---

## 9. Digital Transformation — Technology Meets Culture

### The Transformation Framework

```
VISION → ASSESS → STRATEGISE → EXECUTE → MEASURE → ITERATE
```

Digital transformation fails not because of technology, but because of:
- **No clear business case** (43% of failures — McKinsey)
- **Functional silos** (30% of failures)
- **Change resistance** (people fear replacement, not improvement)
- **Pilot purgatory** (impressive demos that never reach production)

### Transformation Pillars

| Pillar | Actions |
|---|---|
| Strategy | Align technology investments to business outcomes. OKRs, not projects |
| People | Upskill, reskill, hire. Build AI literacy across all levels. Culture of learning |
| Process | Redesign workflows around capabilities, not around limitations of old tools |
| Technology | Modern architecture, cloud-native, API-first, data-driven |
| Data | Single source of truth. Quality governance. Self-service analytics |
| Governance | Executive sponsorship. Cross-functional ownership. Regular review cadence |

### Change Management (The Human Side)

- **Communicate the "why" first.** People support what they help create
- **Start with quick wins.** Demonstrate value in 30–60 days, not 12 months
- **Champions network.** Identify and empower advocates in every team
- **Measure adoption, not just deployment.** A tool nobody uses is a waste
- **Psychological safety.** People must feel safe to experiment, fail, and learn

### Digital Transformation Anti-Patterns

| Anti-Pattern | Better Approach |
|---|---|
| "Boil the ocean" multi-year programme | Iterative delivery with 90-day value milestones |
| Technology-first, business-second | Start with business problem, select technology to solve it |
| "Get our data right first, then AI" | Improve data quality alongside initial AI use cases |
| Centralised ivory tower team | Embedded cross-functional squads with central support |
| Big-bang migration | Strangler fig pattern: migrate incrementally, service by service |

---

## 10. Skill Development — The CTO's Learning Path

### Core Competencies by Role

| Role | Must-Have Skills |
|---|---|
| CTO / VP Engineering | Architecture, strategy, team building, vendor management, board communication |
| Engineering Manager | People management, delivery execution, technical mentorship, hiring |
| Staff/Principal Engineer | System design, cross-team influence, ADRs, technical vision |
| Platform Engineer | Kubernetes, IaC, CI/CD, observability, developer experience |
| Security Engineer | Threat modelling, SIEM, IAM, compliance frameworks, incident response |
| Data Engineer | SQL, Python, dbt, Airflow, data modelling, pipeline reliability |
| ML Engineer | MLOps, model serving, feature engineering, experiment tracking |
| Cloud Architect | Multi-cloud design, networking, cost optimisation, well-architected reviews |

### Certifications Worth Having (2026)

| Domain | Certification |
|---|---|
| Cloud | AWS Solutions Architect, Azure Solutions Architect, GCP Professional Cloud Architect |
| Security | CISSP, CISM, CompTIA Security+, AWS Security Specialty |
| Data | Google Professional Data Engineer, Databricks Data Engineer, dbt Analytics Engineering |
| AI/ML | AWS ML Specialty, Google Professional ML Engineer, Stanford/DeepLearning.AI |
| DevOps | CKA/CKAD (Kubernetes), HashiCorp Terraform Associate, AWS DevOps Professional |
| Architecture | TOGAF, AWS Well-Architected |

### Continuous Learning Protocol

```
BUILD → DOCUMENT → RESEARCH → LEARN → REPEAT
```

1. **Build something every week.** Hands-on beats theory
2. **Document what you learn.** Writing crystallises understanding
3. **Research what's emerging.** Follow Thoughtworks Tech Radar, CNCF landscape, Gartner Hype Cycles
4. **Learn from incidents.** Post-mortems are the most valuable education
5. **Teach others.** If you can't explain it simply, you don't understand it well enough

---

## Quick Reference: Tool Selection by Domain

| Domain | Recommended Stack (2026) |
|---|---|
| Version Control | Git + GitHub/GitLab |
| CI/CD | GitHub Actions, GitLab CI, CircleCI, ArgoCD (GitOps) |
| Containers | Docker + Kubernetes (EKS/GKE/AKS) |
| IaC | Terraform, Pulumi |
| Cloud | AWS, Azure, GCP (pick based on ecosystem, not hype) |
| Observability | Grafana + Prometheus + Loki + Tempo (or Datadog all-in-one) |
| Security | CrowdStrike/SentinelOne (EDR), Snyk (AppSec), Vault (secrets) |
| Data Warehouse | Snowflake, Databricks, BigQuery |
| Data Transformation | dbt |
| BI & Analytics | Power BI, Tableau, Looker |
| AI/ML Platform | Databricks ML, SageMaker, Vertex AI |
| API Gateway | Kong, AWS API Gateway, Cloudflare Workers |
| Communication | Slack, Teams (integrate alerts and workflows) |
| Project Management | Linear, Jira, Shortcut |
| Documentation | Notion, Confluence, README + ADRs in repo |

---

For detailed domain deep-dives, reference material, and implementation guides, read:
→ `references/full-playbook.md`

---

**Remember: Security first, always. Automate the boring stuff. Measure outcomes, not outputs. Build for change, not for permanence. Technology serves the mission. The mission is never "more technology."**
