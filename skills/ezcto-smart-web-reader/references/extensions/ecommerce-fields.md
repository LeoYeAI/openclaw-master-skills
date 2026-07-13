# E-commerce Extension Fields (Enhanced)

When the site is detected as an e-commerce website, extract these additional fields into the `extensions.ecommerce` object.

---

## Additional Extraction Rules

### 1. Products
Extract visible product listings with detailed information:

**Fields per product:**
- `name`: Product name/title
- `price`: Current price (number as string, e.g., "29.99")
- `original_price`: Original price if discounted (for showing savings)
- `currency`: Currency code (USD, EUR, GBP, JPY, etc.)
- `description`: Short product description
- `url`: Link to product page (absolute URL)
- `image`: Main product image URL
- `availability`: "in_stock" / "out_of_stock" / "preorder" / "backorder"
- `rating`: Average rating if displayed (e.g., "4.5")
- `review_count`: Number of reviews
- `sku`: Stock Keeping Unit if available
- `brand`: Product brand if mentioned

**Where to look:**
- Product cards/tiles in listings
- Featured products section
- Schema.org Product markup
- Product detail page content

### 2. Categories
Extract product categories from navigation or filters:

**Sources:**
- Main navigation menu
- Sidebar category list
- Breadcrumb trail
- Filter/facet options

**Format:** Array of category names
```json
"categories": ["Electronics", "Laptops", "Gaming Laptops"]
```

### 3. Payment Methods
Detect supported payment methods from:

**Visual indicators:**
- Payment logo images (Visa, Mastercard, PayPal, etc.)
- "We accept" sections
- Footer payment icons

**Common methods:**
- `credit_card` (if Visa/MC/Amex logos present)
- `paypal`
- `apple_pay`
- `google_pay`
- `amazon_pay`
- `afterpay` / `klarna` (buy now pay later)
- `crypto` (if BTC/ETH logos)
- `bank_transfer`

### 4. Shipping Policy
Extract shipping information from:

**Look for:**
- "Free shipping" offers
- Shipping policy page content
- Estimated delivery times
- Shipping regions/countries

**Example extractions:**
- "Free shipping on orders over $50"
- "2-day shipping available"
- "Ships to US, CA, UK"

### 5. Return Policy
Extract return/refund policy details:

**Look for:**
- Return policy page
- "30-day return" badges
- Money-back guarantee mentions

**Example:**
```json
"return_policy": "30-day return policy with free returns"
```

### 6. Promotions (NEW)
Extract active promotions and discount codes:

**Fields:**
- `code`: Promo code (e.g., "SAVE20")
- `description`: What the promo offers
- `discount_value`: Discount amount or percentage
- `expiry`: Expiration date if mentioned
- `conditions`: Minimum order value, etc.

**Sources:**
- Banner announcements
- Promo code sections
- "Use code XXX at checkout"

### 7. Merchant Info (NEW)
Extract seller/merchant information:

**Fields:**
- `merchant_name`: Store name
- `merchant_rating`: Seller rating if displayed
- `verified`: Whether merchant is verified
- `return_address`: Physical return address

### 8. Product Variants (NEW)
For product detail pages, extract variants:

**Example:**
```json
"product_variants": {
  "colors": ["Black", "Silver", "Rose Gold"],
  "sizes": ["S", "M", "L", "XL"],
  "configurations": ["64GB", "128GB", "256GB"]
}
```

---

## Output Format

```json
{
  "extensions": {
    "ecommerce": {
      "products": [
        {
          "name": "Gaming Laptop RTX 4090",
          "price": "1999.99",
          "original_price": "2499.99",
          "currency": "USD",
          "description": "High-performance gaming laptop with RTX 4090",
          "url": "https://example.com/products/gaming-laptop-rtx4090",
          "image": "https://example.com/images/laptop.jpg",
          "availability": "in_stock",
          "rating": "4.8",
          "review_count": "1,234",
          "sku": "GLAP-4090-001",
          "brand": "TechBrand"
        }
      ],

      "categories": ["Electronics", "Computers", "Gaming Laptops"],

      "payment_methods": [
        "credit_card",
        "paypal",
        "apple_pay",
        "afterpay"
      ],

      "shipping": {
        "policy": "Free shipping on orders over $50",
        "regions": ["US", "CA", "UK", "AU"],
        "estimated_delivery": "2-5 business days"
      },

      "return_policy": "30-day return policy with free returns",

      "promotions": [
        {
          "code": "SAVE20",
          "description": "20% off first order",
          "discount_value": "20%",
          "expiry": "2024-12-31",
          "conditions": "Minimum order $100"
        },
        {
          "code": "FREESHIP",
          "description": "Free shipping on all orders",
          "discount_value": "Free Shipping",
          "expiry": null
        }
      ],

      "merchant_info": {
        "name": "TechStore Official",
        "rating": "4.9/5",
        "verified": true,
        "total_sales": "100K+"
      },

      "product_variants": {
        "colors": ["Black", "Silver"],
        "storage": ["512GB SSD", "1TB SSD"],
        "ram": ["16GB", "32GB"]
      }
    }
  }
}
```

---

## OpenClaw Agent Suggestions (E-commerce-Specific)

```json
{
  "agent_suggestions": {
    "primary_action": {
      "label": "Add to Cart",
      "url": "{{ actions[0].url }}",
      "purpose": "buy",
      "priority": "high"
    },
    "next_actions": [
      {
        "action": "compare_prices",
        "url": "/compare",
        "reason": "Compare with similar products",
        "priority": 1
      },
      {
        "action": "read_reviews",
        "url": "/reviews",
        "reason": "Check customer reviews before purchase",
        "priority": 2
      },
      {
        "action": "check_shipping",
        "url": "/shipping-policy",
        "reason": "Verify shipping options and costs",
        "priority": 3
      }
    ],
    "skills_to_chain": [
      {
        "skill": "price-tracker",
        "input": "{{ extensions.ecommerce.products[0] }}",
        "reason": "Track price history and get alerts on price drops"
      },
      {
        "skill": "review-analyzer",
        "input": "{{ extensions.ecommerce.products[0].url }}",
        "reason": "Analyze customer reviews for sentiment and common issues"
      },
      {
        "skill": "price-comparison",
        "input": "{{ extensions.ecommerce.products[0].name }}",
        "reason": "Find best price across multiple retailers"
      }
    ]
  }
}
```

---

## Validation Rules

- **Price:** Must be a positive number (as string)
- **Currency:** Use ISO 4217 codes (USD, EUR, etc.)
- **Availability:** Must be one of the predefined status values
- **URLs:** Must be absolute URLs (not relative paths)
- **Rating:** Number between 0-5 (as string)

---

## Error Handling

If no products found on an e-commerce site:

```json
{
  "extensions": {
    "ecommerce": {
      "products": [],
      "extraction_confidence": "low",
      "warnings": [
        "E-commerce site detected but no products found on this page",
        "Page might be a category landing page or requires JavaScript"
      ]
    }
  }
}
```
