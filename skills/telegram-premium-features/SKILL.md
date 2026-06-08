---
name: telegram-premium-features
description: Complete implementation guide for Telegram/Teamgram premium features and monetization (v2.0.0). Use when building membership systems, payment integration, subscription lifecycle, coupons, analytics, and global payment solutions. Covers ten iterations of optimization from basic implementation to production-ready systems.
version: 2.0.0
---

# Telegram Premium Features Implementation v2.0.0

Complete guide for implementing monetization features in Telegram-compatible backends.

> 📚 **十次版本迭代优化** (v1.0.0 → v2.0.0)
> 
> 本技能经过十次迭代完善，从基础会员系统到全球化支付解决方案的完整知识体系。

## 版本迭代历程

| 版本 | 主题 | 文档 |
|------|------|------|
| v1.0.0 | 基础实现 | 本指南 |
| v1.1.0 | 支付网关对比 | [查看](references/v1.1.0-payment-gateways.md) |
| v1.2.0 | 订阅生命周期 | [查看](references/v1.2.0-lifecycle.md) |
| v1.3.0 | 优惠券促销 | [查看](references/v1.3.0-coupons.md) |
| v1.4.0 | 税务合规 | [查看](references/v1.4.0-tax.md) |
| v1.5.0 | 退款争议 | [查看](references/v1.5.0-refunds.md) |
| v1.6.0 | 推荐奖励 | [查看](references/v1.6.0-referral.md) |
| v1.7.0 | 数据分析 | [查看](references/v1.7.0-analytics.md) |
| v1.8.0 | A/B测试 | [查看](references/v1.8.0-ab-testing.md) |
| v1.9.0 | 国际化 | [查看](references/v1.9.0-i18n.md) |
| v2.0.0 | 完整总结 | [查看](references/v2.0.0-final.md) |

## 快速导航

**基础搭建**: 从 [Membership System](#implementation-membership-system) 开始

**支付集成**: 查看 [v1.1.0支付网关](references/v1.1.0-payment-gateways.md)

**运营优化**: 参考 [v1.3.0优惠券](references/v1.3.0-coupons.md) 和 [v1.7.0数据分析](references/v1.7.0-analytics.md)

**全球化**: 查看 [v1.9.0国际化](references/v1.9.0-i18n.md)

## Overview

This guide covers common premium features for IM platforms:
- Membership/subscription systems
- Usage quotas and limits
- Payment integration
- Feature gating
- Admin analytics

## Core Concepts

### Feature Gating Model

```
┌─────────────────────────────────────────────────────────┐
│                    Feature Check Flow                    │
├─────────────────────────────────────────────────────────┤
│  1. User requests feature (e.g., send large file)       │
│  2. System checks user tier (free/premium)              │
│  3. If premium → allow                                  │
│  4. If free → check quota                               │
│  5. If quota exceeded → show upgrade prompt             │
└─────────────────────────────────────────────────────────┘
```

### User Tiers

| Tier | Features | Price |
|------|----------|-------|
| **Free** | Basic messaging, 100MB file limit, 1 month history | Free |
| **Basic** | 500MB file limit, 6 months history, no ads | $4.99/mo |
| **Premium** | 2GB file limit, unlimited history, priority support | $9.99/mo |
| **Business** | 4GB file limit, unlimited history, custom domains | $19.99/mo |

## Implementation: Membership System

### Database Schema

```sql
-- User subscription status
CREATE TABLE user_subscriptions (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    tier ENUM('free', 'basic', 'premium', 'business') DEFAULT 'free',
    status ENUM('active', 'expired', 'cancelled') DEFAULT 'active',
    started_at BIGINT DEFAULT 0,
    expires_at BIGINT DEFAULT 0,
    auto_renew BOOLEAN DEFAULT FALSE,
    payment_method VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_user_id (user_id),
    INDEX idx_expires (expires_at),
    INDEX idx_status (status)
) ENGINE=InnoDB;

-- Subscription plans
CREATE TABLE subscription_plans (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) NOT NULL,
    tier ENUM('basic', 'premium', 'business') NOT NULL,
    price_monthly DECIMAL(10,2) NOT NULL,
    price_yearly DECIMAL(10,2) NOT NULL,
    features JSON,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Insert default plans
INSERT INTO subscription_plans (name, tier, price_monthly, price_yearly, features) VALUES
('Basic', 'basic', 4.99, 49.99, '{"file_limit": 536870912, "history_months": 6, "ads": false}'),
('Premium', 'premium', 9.99, 99.99, '{"file_limit": 2147483648, "history_months": -1, "priority_support": true}'),
('Business', 'business', 19.99, 199.99, '{"file_limit": 4294967296, "history_months": -1, "custom_domain": true}');
```

### Quota Tracking

```sql
-- User quotas (daily/monthly limits)
CREATE TABLE user_quotas (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    user_id BIGINT NOT NULL,
    quota_type VARCHAR(50) NOT NULL,
    limit_value BIGINT DEFAULT 0,
    used_value BIGINT DEFAULT 0,
    reset_at BIGINT DEFAULT 0,
    UNIQUE KEY uk_user_type (user_id, quota_type)
) ENGINE=InnoDB;

-- Quota types: messages_daily, files_daily, storage_used
```

### Core Implementation

```go
// subscription_manager.go

type SubscriptionManager struct {
    db    *sqlx.DB
    redis *redis.Client
}

// CheckUserTier 检查用户等级
func (m *SubscriptionManager) CheckUserTier(ctx context.Context, userID int64) (Tier, error) {
    // Try cache
    cacheKey := fmt.Sprintf("user:tier:%d", userID)
    cached, err := m.redis.Get(ctx, cacheKey).Result()
    if err == nil {
        return Tier(cached), nil
    }
    
    // Query database
    var sub UserSubscription
    err = m.db.GetContext(ctx, &sub, 
        "SELECT * FROM user_subscriptions WHERE user_id = ?", userID)
    if err == sql.ErrNoRows {
        return TierFree, nil
    }
    if err != nil {
        return TierFree, err
    }
    
    // Check expiration
    if sub.Status == "expired" || (sub.ExpiresAt > 0 && sub.ExpiresAt < time.Now().Unix()) {
        m.ExpireSubscription(ctx, userID)
        return TierFree, nil
    }
    
    // Cache result
    m.redis.Set(ctx, cacheKey, string(sub.Tier), 5*time.Minute)
    
    return Tier(sub.Tier), nil
}

// CheckFeatureAccess 检查功能访问权限
func (m *SubscriptionManager) CheckFeatureAccess(ctx context.Context, userID int64, feature string) (bool, error) {
    tier, err := m.CheckUserTier(ctx, userID)
    if err != nil {
        return false, err
    }
    
    // Feature requirement mapping
    requirements := map[string]Tier{
        "large_files":     TierBasic,
        "unlimited_history": TierPremium,
        "custom_domain":   TierBusiness,
        "priority_support": TierPremium,
    }
    
    requiredTier, exists := requirements[feature]
    if !exists {
        return true, nil // Feature doesn't require tier
    }
    
    return tier >= requiredTier, nil
}

// CheckQuota 检查配额
func (m *SubscriptionManager) CheckQuota(ctx context.Context, userID int64, quotaType string) (bool, int64, error) {
    tier, _ := m.CheckUserTier(ctx, userID)
    
    // Get tier limits
    limits := m.getTierLimits(tier)
    limit := limits[quotaType]
    
    if limit < 0 {
        return true, -1, nil // Unlimited
    }
    
    // Get current usage
    var quota UserQuota
    err := m.db.GetContext(ctx, &quota,
        "SELECT * FROM user_quotas WHERE user_id = ? AND quota_type = ?",
        userID, quotaType)
    
    if err == sql.ErrNoRows {
        // No record yet
        return true, limit, nil
    }
    if err != nil {
        return false, 0, err
    }
    
    // Check if need reset
    if quota.ResetAt < time.Now().Unix() {
        m.resetQuota(ctx, userID, quotaType)
        return true, limit, nil
    }
    
    remaining := limit - quota.UsedValue
    return remaining > 0, remaining, nil
}

// UseQuota 使用配额
func (m *SubscriptionManager) UseQuota(ctx context.Context, userID int64, quotaType string, amount int64) error {
    _, err := m.db.ExecContext(ctx,
        `INSERT INTO user_quotas (user_id, quota_type, used_value, reset_at) 
         VALUES (?, ?, ?, ?)
         ON DUPLICATE KEY UPDATE used_value = used_value + VALUES(used_value)`,
        userID, quotaType, amount, getNextResetTime())
    return err
}

func (m *SubscriptionManager) getTierLimits(tier Tier) map[string]int64 {
    limits := map[Tier]map[string]int64{
        TierFree: {
            "messages_daily": 1000,
            "files_daily":    50,
            "file_size":      100 * 1024 * 1024, // 100MB
            "storage":        1024 * 1024 * 1024, // 1GB
        },
        TierBasic: {
            "messages_daily": 10000,
            "files_daily":    500,
            "file_size":      500 * 1024 * 1024, // 500MB
            "storage":        10 * 1024 * 1024 * 1024, // 10GB
        },
        TierPremium: {
            "messages_daily": -1, // Unlimited
            "files_daily":    -1,
            "file_size":      2 * 1024 * 1024 * 1024, // 2GB
            "storage":        100 * 1024 * 1024 * 1024, // 100GB
        },
    }
    return limits[tier]
}
```

## Implementation: Payment Integration

### Stripe Integration

```go
// stripe_payment.go

import "github.com/stripe/stripe-go/v74"

type StripePayment struct {
    client *stripe.Client
}

func (p *StripePayment) CreateCheckoutSession(ctx context.Context, userID int64, planID int) (string, error) {
    // Get plan details
    plan, err := p.getPlan(ctx, planID)
    if err != nil {
        return "", err
    }
    
    params := &stripe.CheckoutSessionParams{
        CustomerEmail: stripe.String(getUserEmail(userID)),
        LineItems: []*stripe.CheckoutSessionLineItemParams{
            {
                PriceData: &stripe.CheckoutSessionLineItemPriceDataParams{
                    Currency: stripe.String("usd"),
                    ProductData: &stripe.CheckoutSessionLineItemPriceDataProductDataParams{
                        Name: stripe.String(plan.Name),
                    },
                    UnitAmount: stripe.Int64(int64(plan.Price * 100)), // cents
                },
                Quantity: stripe.Int64(1),
            },
        },
        Mode:       stripe.String(string(stripe.CheckoutSessionModeSubscription)),
        SuccessURL: stripe.String(fmt.Sprintf("https://yourapp.com/success?user=%d", userID)),
        CancelURL:  stripe.String("https://yourapp.com/cancel"),
        Metadata: map[string]string{
            "user_id": fmt.Sprintf("%d", userID),
            "plan_id": fmt.Sprintf("%d", planID),
        },
    }
    
    session, err := stripe.CheckoutSession(params)
    if err != nil {
        return "", err
    }
    
    return session.URL, nil
}

func (p *StripePayment) HandleWebhook(payload []byte, sig string) error {
    event, err := stripe.Webhook(payload, sig, webhookSecret)
    if err != nil {
        return err
    }
    
    switch event.Type {
    case "checkout.session.completed":
        var session stripe.CheckoutSession
        err := json.Unmarshal(event.Data.Raw, &session)
        if err != nil {
            return err
        }
        
        userID, _ := strconv.ParseInt(session.Metadata["user_id"], 10, 64)
        planID, _ := strconv.Atoi(session.Metadata["plan_id"])
        
        // Activate subscription
        p.activateSubscription(userID, planID, session.Subscription.ID)
        
    case "invoice.payment_failed":
        // Handle failed payment
        p.handlePaymentFailure(event)
    }
    
    return nil
}
```

### Webhook Handler

```go
// payment_webhook.go

func (s *Server) PaymentWebhook(ctx context.Context, req *PaymentWebhookReq) (*Bool, error) {
    switch req.Provider {
    case "stripe":
        err := s.stripePayment.HandleWebhook(req.Payload, req.Signature)
        if err != nil {
            return BoolFalse, err
        }
    case "alipay":
        err := s.alipayPayment.HandleNotify(req.Payload)
        if err != nil {
            return BoolFalse, err
        }
    }
    
    return BoolTrue, nil
}
```

## Implementation: Feature Gating

### Middleware Pattern

```go
// middleware/premium_middleware.go

func PremiumMiddleware(next HandlerFunc) HandlerFunc {
    return func(ctx context.Context, req Request) (Response, error) {
        userID := getUserIDFromContext(ctx)
        feature := getFeatureFromRequest(req)
        
        // Check access
        hasAccess, err := subscriptionManager.CheckFeatureAccess(ctx, userID, feature)
        if err != nil {
            return nil, err
        }
        
        if !hasAccess {
            return nil, status.Error(codes.PermissionDenied, 
                "This feature requires premium subscription")
        }
        
        // Check quota for usage-based features
        if isQuotaBased(feature) {
            allowed, remaining, err := subscriptionManager.CheckQuota(ctx, userID, feature)
            if err != nil {
                return nil, err
            }
            if !allowed {
                return nil, status.Errorf(codes.ResourceExhausted,
                    "Quota exceeded. Upgrade to get more.")
            }
            // Update context with remaining quota
            ctx = context.WithValue(ctx, "remaining_quota", remaining)
        }
        
        return next(ctx, req)
    }
}
```

### Usage in Handlers

```go
func (s *Server) MessagesSendDocument(ctx context.Context, req *SendDocumentReq) (*Message, error) {
    userID := getUserIDFromContext(ctx)
    fileSize := req.File.Size
    
    // Check file size limit
    tier, _ := s.subManager.CheckUserTier(ctx, userID)
    limits := s.subManager.getTierLimits(tier)
    
    if fileSize > limits["file_size"] {
        return nil, status.Errorf(codes.FailedPrecondition,
            "File too large. Max size for your tier: %d MB", 
            limits["file_size"]/(1024*1024))
    }
    
    // Check and use quota
    allowed, _, err := s.subManager.CheckQuota(ctx, userID, "files_daily")
    if err != nil {
        return nil, err
    }
    if !allowed {
        return nil, status.Errorf(codes.ResourceExhausted,
            "Daily file upload limit reached. Upgrade for unlimited uploads.")
    }
    
    // Use quota
    s.subManager.UseQuota(ctx, userID, "files_daily", 1)
    
    // Process document...
}
```

## Implementation: Admin Dashboard

### Revenue Analytics

```go
// admin/analytics.go

type RevenueAnalytics struct {
    db *sqlx.DB
}

func (a *RevenueAnalytics) GetRevenueReport(ctx context.Context, start, end time.Time) (*RevenueReport, error) {
    query := `
        SELECT 
            DATE(created_at) as date,
            SUM(amount) as revenue,
            COUNT(*) as transactions,
            tier,
            payment_method
        FROM premium_transactions
        WHERE status = 1 
          AND created_at BETWEEN ? AND ?
        GROUP BY DATE(created_at), tier, payment_method
        ORDER BY date DESC
    `
    
    var rows []RevenueRow
    err := a.db.SelectContext(ctx, &rows, query, start, end)
    if err != nil {
        return nil, err
    }
    
    return &RevenueReport{
        Rows:       rows,
        Total:      sumRevenue(rows),
        StartDate:  start,
        EndDate:    end,
    }, nil
}

func (a *RevenueAnalytics) GetUserRetention(ctx context.Context) (*RetentionReport, error) {
    query := `
        SELECT 
            tier,
            COUNT(*) as total_users,
            SUM(CASE WHEN expires_at > NOW() THEN 1 ELSE 0 END) as active_users,
            SUM(CASE WHEN auto_renew = 1 THEN 1 ELSE 0 END) as auto_renew_users
        FROM user_subscriptions
        GROUP BY tier
    `
    
    var rows []RetentionRow
    err := a.db.SelectContext(ctx, &rows, query)
    return &RetentionReport{Rows: rows}, err
}
```

## Client-Side Integration

### Upgrade Prompt UI

```go
// Client receives error and shows upgrade dialog
func handleSendFileError(err error) {
    if status.Code(err) == codes.FailedPrecondition {
        // Show upgrade dialog
        showUpgradeDialog(
            title: "File Too Large",
            message: "Upgrade to Premium to send files up to 2GB",
            plans: getAvailablePlans()
        )
    } else if status.Code(err) == codes.ResourceExhausted {
        // Show quota exceeded dialog
        showUpgradeDialog(
            title: "Daily Limit Reached",
            message: "You've reached your daily upload limit. Upgrade for unlimited uploads.",
            plans: getAvailablePlans()
        )
    }
}
```

## Testing

### Unit Tests

```go
func TestSubscriptionManager(t *testing.T) {
    ctx := context.Background()
    manager := NewSubscriptionManager(testDB, testRedis)
    
    t.Run("CheckUserTier", func(t *testing.T) {
        // Free user
        tier, err := manager.CheckUserTier(ctx, 1)
        assert.NoError(t, err)
        assert.Equal(t, TierFree, tier)
        
        // Premium user
        tier, err = manager.CheckUserTier(ctx, 2)
        assert.NoError(t, err)
        assert.Equal(t, TierPremium, tier)
    })
    
    t.Run("CheckFeatureAccess", func(t *testing.T) {
        // Free user can't access premium feature
        hasAccess, err := manager.CheckFeatureAccess(ctx, 1, "large_files")
        assert.NoError(t, err)
        assert.False(t, hasAccess)
        
        // Premium user can access
        hasAccess, err = manager.CheckFeatureAccess(ctx, 2, "large_files")
        assert.NoError(t, err)
        assert.True(t, hasAccess)
    })
    
    t.Run("CheckQuota", func(t *testing.T) {
        // Free user has limited quota
        allowed, remaining, err := manager.CheckQuota(ctx, 1, "files_daily")
        assert.NoError(t, err)
        assert.True(t, allowed)
        assert.Equal(t, int64(50), remaining)
        
        // Premium user has unlimited
        allowed, remaining, err = manager.CheckQuota(ctx, 2, "files_daily")
        assert.NoError(t, err)
        assert.True(t, allowed)
        assert.Equal(t, int64(-1), remaining) // Unlimited
    })
}
```

## Best Practices

1. **Graceful Degradation**: Free users should still have usable experience
2. **Clear Communication**: Always tell users why a feature is blocked
3. **Easy Upgrade**: One-click upgrade flow
4. **Fair Pricing**: Transparent pricing with clear value proposition
5. **Analytics**: Track conversion rates and user behavior

## References

- [Stripe Documentation](https://stripe.com/docs)
- [PayPal Developer](https://developer.paypal.com/)
- [RevenueCat (mobile subscriptions)](https://www.revenuecat.com/)
