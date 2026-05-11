# StockPulse - Commercial Product Roadmap

## Vision

Transform the stock-analysis skill into **StockPulse**, a commercial mobile app for retail investors with AI-powered stock and crypto analysis, portfolio tracking, and personalized alerts.

## Technical Decisions

- **Mobile:** Flutter (iOS + Android cross-platform)
- **Backend:** Python FastAPI on AWS (ECS/Lambda)
- **Database:** PostgreSQL (RDS) + Redis (ElastiCache)
- **Auth:** AWS Cognito or Firebase Auth
- **Monetization:** Freemium + Subscription ($9.99/mo or $79.99/yr)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      MOBILE APP (Flutter)                        │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐           │
│  │Dashboard │ │Portfolio │ │ Analysis │ │ Alerts   │           │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘           │
└─────────────────────────────────────────────────────────────────┘
                              │ HTTPS/REST
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY (AWS)                           │
│                   Rate Limiting, Auth, Caching                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   BACKEND (FastAPI on ECS)                       │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ Auth Service │ │ Analysis API │ │ Portfolio API│            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │ Alerts Svc   │ │ Subscription │ │ User Service │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
└─────────────────────────────────────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  PostgreSQL  │     │    Redis     │     │     S3       │
│   (RDS)      │     │ (ElastiCache)│     │  (Reports)   │
└──────────────┘     └──────────────┘     └──────────────┘

                    BACKGROUND WORKERS (Lambda/ECS)
┌─────────────────────────────────────────────────────────────────┐
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐            │
│  │Price Updater │ │Alert Checker │ │Daily Reports │            │
│  │  (5 min)     │ │  (1 min)     │ │  (Daily)     │            │
│  └──────────────┘ └──────────────┘ └──────────────┘            │
└─────────────────────────────────────────────────────────────────┘
```

---

## Feature Tiers

### Free Tier
- 1 portfolio (max 10 assets)
- Basic stock/crypto analysis
- Daily market summary
- Limited to 5 analyses/day
- Ads displayed

### Premium ($9.99/mo)
- Unlimited portfolios & assets
- Full 8-dimension analysis
- Real-time price alerts
- Push notifications
- Period reports (daily/weekly/monthly)
- No ads
- Priority support

### Pro ($19.99/mo) - Future
- API access
- Custom watchlists
- Advanced screeners
- Export to CSV/PDF
- Portfolio optimization suggestions

---

## Development Phases

### Phase 1: Backend API

**Goal:** Convert Python scripts to production REST API

#### Tasks:
1. **Project Setup**
   - FastAPI project structure
   - Docker containerization
   - CI/CD pipeline (GitHub Actions)
   - AWS infrastructure (Terraform)

2. **Core API Endpoints**
   ```
   POST /auth/register
   POST /auth/login
   POST /auth/refresh

   GET  /analysis/{ticker}
   POST /analysis/batch

   GET  /portfolios
   POST /portfolios
   PUT  /portfolios/{id}
   DELETE /portfolios/{id}

   GET  /portfolios/{id}/assets
   POST /portfolios/{id}/assets
   PUT  /portfolios/{id}/assets/{ticker}
   DELETE /portfolios/{id}/assets/{ticker}

   GET  /portfolios/{id}/performance?period=weekly
   GET  /portfolios/{id}/summary

   GET  /alerts
   POST /alerts
   DELETE /alerts/{id}

   GET  /user/subscription
   POST /user/subscription/upgrade
   ```

3. **Database Schema**
   ```sql
   users (id, email, password_hash, created_at, subscription_tier)
   portfolios (id, user_id, name, created_at, updated_at)
   assets (id, portfolio_id, ticker, asset_type, quantity, cost_basis)
   alerts (id, user_id, ticker, condition, threshold, enabled)
   analysis_cache (ticker, data, expires_at)
   subscriptions (id, user_id, stripe_id, status, expires_at)
   ```

4. **Refactor Existing Code**
   - Extract `analyze_stock.py` into modules:
     - `analysis/earnings.py`
     - `analysis/fundamentals.py`
     - `analysis/sentiment.py`
     - `analysis/crypto.py`
     - `analysis/market_context.py`
   - Add async support throughout
   - Implement proper caching (Redis)
   - Rate limiting per user tier

#### Files to Create:
```
backend/
├── app/
│   ├── main.py              # FastAPI app
│   ├── config.py            # Settings
│   ├── models/              # SQLAlchemy models
│   ├── schemas/             # Pydantic schemas
│   ├── routers/             # API routes
│   │   ├── auth.py
│   │   ├── analysis.py
│   │   ├── portfolios.py
│   │   └── alerts.py
│   ├── services/            # Business logic
│   │   ├── analysis/        # Refactored from analyze_stock.py
│   │   ├── portfolio.py
│   │   └── alerts.py
│   └── workers/             # Background tasks
├── tests/
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

---

### Phase 2: Flutter Mobile App

**Goal:** Build polished cross-platform mobile app

#### Screens:
1. **Onboarding** - Welcome, feature highlights, sign up/login
2. **Dashboard** - Market overview, portfolio summary, alerts
3. **Analysis** - Search ticker, view full analysis, save to portfolio
4. **Portfolio** - List portfolios, asset breakdown, P&L chart
5. **Alerts** - Manage price alerts, notification settings
6. **Settings** - Account, subscription, preferences

#### Key Flutter Packages:
```yaml
dependencies:
  flutter_bloc: ^8.0.0      # State management
  dio: ^5.0.0               # HTTP client
  go_router: ^12.0.0        # Navigation
  fl_chart: ^0.65.0         # Charts
  firebase_messaging: ^14.0.0  # Push notifications
  in_app_purchase: ^3.0.0   # Subscriptions
  shared_preferences: ^2.0.0
  flutter_secure_storage: ^9.0.0
```

#### App Structure:
```
lib/
├── main.dart
├── app/
│   ├── routes.dart
│   └── theme.dart
├── features/
│   ├── auth/
│   │   ├── bloc/
│   │   ├── screens/
│   │   └── widgets/
│   ├── dashboard/
│   ├── analysis/
│   ├── portfolio/
│   ├── alerts/
│   └── settings/
├── core/
│   ├── api/
│   ├── models/
│   └── utils/
└── shared/
    └── widgets/
```

---

### Phase 3: Infrastructure & DevOps

**Goal:** Production-ready cloud infrastructure

#### AWS Services:
- **ECS Fargate** - Backend containers
- **RDS PostgreSQL** - Database
- **ElastiCache Redis** - Caching
- **S3** - Static assets, reports
- **CloudFront** - CDN
- **Cognito** - Authentication
- **SES** - Email notifications
- **SNS** - Push notifications
- **CloudWatch** - Monitoring
- **WAF** - Security

#### Terraform Modules:
```
infrastructure/
├── main.tf
├── variables.tf
├── modules/
│   ├── vpc/
│   ├── ecs/
│   ├── rds/
│   ├── elasticache/
│   └── cognito/
└── environments/
    ├── dev/
    ├── staging/
    └── prod/
```

#### Estimated Monthly Costs (Production):
| Service | Est. Cost |
|---------|-----------|
| ECS Fargate (2 tasks) | $50-100 |
| RDS (db.t3.small) | $30-50 |
| ElastiCache (cache.t3.micro) | $15-25 |
| S3 + CloudFront | $10-20 |
| Other (Cognito, SES, etc.) | $20-30 |
| **Total** | **$125-225/mo** |

---

### Phase 4: Payments & Subscriptions

**Goal:** Integrate Stripe for subscriptions

#### Implementation:
1. Stripe subscription products (Free, Premium, Pro)
2. In-app purchase for iOS/Android
3. Webhook handlers for subscription events
4. Grace period handling
5. Receipt validation

#### Stripe Integration:
```python
# Backend webhook handler
@router.post("/webhooks/stripe")
async def stripe_webhook(request: Request):
    event = stripe.Webhook.construct_event(...)

    if event.type == "customer.subscription.updated":
        update_user_tier(event.data.object)
    elif event.type == "customer.subscription.deleted":
        downgrade_to_free(event.data.object)
```

---

### Phase 5: Push Notifications & Alerts

**Goal:** Real-time price alerts and notifications

#### Alert Types:
- Price above/below threshold
- Percentage change (daily)
- Earnings announcement
- Breaking news (geopolitical)
- Portfolio performance

#### Implementation:
- Firebase Cloud Messaging (FCM)
- Background worker checks alerts every minute
- Rate limit: max 10 alerts/day per free user

---

### Phase 6: Analytics & Monitoring

**Goal:** Track usage, errors, business metrics

#### Tools:
- **Mixpanel/Amplitude** - Product analytics
- **Sentry** - Error tracking
- **CloudWatch** - Infrastructure metrics
- **Custom dashboard** - Business KPIs

#### Key Metrics:
- DAU/MAU
- Conversion rate (free → premium)
- Churn rate
- API response times
- Analysis accuracy feedback

---

## Security Considerations

1. **Authentication**
   - JWT tokens with refresh rotation
   - OAuth2 (Google, Apple Sign-In)
   - 2FA optional for premium users

2. **Data Protection**
   - Encrypt PII at rest (RDS encryption)
   - TLS 1.3 for all API traffic
   - No plaintext passwords

3. **API Security**
   - Rate limiting per tier
   - Input validation (Pydantic)
   - SQL injection prevention (SQLAlchemy ORM)
   - CORS configuration

4. **Compliance**
   - Privacy policy
   - Terms of service
   - GDPR data export/deletion
   - Financial disclaimer (not investment advice)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Yahoo Finance rate limits | High | Implement caching, use paid API fallback |
| App store rejection | Medium | Follow guidelines, proper disclaimers |
| Data accuracy issues | High | Clear disclaimers, data validation |
| Security breach | Critical | Security audit, penetration testing |
| Low conversion rate | Medium | A/B testing, feature gating |

---

## Success Metrics (Year 1)

| Metric | Target |
|--------|--------|
| App downloads | 10,000+ |
| DAU | 1,000+ |
| Premium subscribers | 500+ |
| Monthly revenue | $5,000+ |
| App store rating | 4.5+ stars |
| Churn rate | <5%/month |

---

## Next Steps (Immediate)

1. **Validate idea** - User interviews, landing page
2. **Design** - Figma mockups for key screens
3. **Backend MVP** - Core API endpoints
4. **Flutter prototype** - Basic app with analysis feature
5. **Beta testing** - TestFlight/Google Play beta

---

## Repository Structure (Final)

```
stockpulse/
├── backend/                 # FastAPI backend
│   ├── app/
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── mobile/                  # Flutter app
│   ├── lib/
│   ├── test/
│   ├── ios/
│   ├── android/
│   └── pubspec.yaml
├── infrastructure/          # Terraform
│   ├── modules/
│   └── environments/
├── docs/                    # Documentation
│   ├── api/
│   └── architecture/
└── scripts/                 # Utility scripts
```

---

## Timeline Summary (Planning Only)

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| 1. Backend API | 4-6 weeks | - |
| 2. Flutter App | 6-8 weeks | Phase 1 |
| 3. Infrastructure | 2-3 weeks | Phase 1 |
| 4. Payments | 2 weeks | Phase 2, 3 |
| 5. Notifications | 2 weeks | Phase 2, 3 |
| 6. Analytics | 1 week | Phase 2 |
| **Total** | **17-22 weeks** | |

This is a planning document. No fixed timeline - execute phases as resources allow.

---

**Disclaimer:** This tool is for informational purposes only and does NOT constitute financial advice.
