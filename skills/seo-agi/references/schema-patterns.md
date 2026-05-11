# Schema Markup Patterns

JSON-LD schema markup templates for each page type. The skill generates
these at the end of each page as a code block.

## FAQPage (use on any page with an FAQ section)

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "Question text here?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Answer text here."
      }
    }
  ]
}
```

## LocalBusiness (service + location pages)

```json
{
  "@context": "https://schema.org",
  "@type": "LocalBusiness",
  "name": "Business Name",
  "description": "What the business does",
  "url": "https://example.com",
  "address": {
    "@type": "PostalAddress",
    "streetAddress": "123 Main St",
    "addressLocality": "City",
    "addressRegion": "ST",
    "postalCode": "12345",
    "addressCountry": "US"
  },
  "geo": {
    "@type": "GeoCoordinates",
    "latitude": 40.7128,
    "longitude": -74.0060
  },
  "priceRange": "$$"
}
```

## HowTo (guide/tutorial pages)

```json
{
  "@context": "https://schema.org",
  "@type": "HowTo",
  "name": "How to [action]",
  "description": "Brief description",
  "step": [
    {
      "@type": "HowToStep",
      "name": "Step title",
      "text": "Step description"
    }
  ]
}
```

## Product (product/feature pages)

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Product Name",
  "description": "Product description",
  "brand": {
    "@type": "Brand",
    "name": "Brand Name"
  },
  "offers": {
    "@type": "AggregateOffer",
    "lowPrice": "9.99",
    "highPrice": "99.99",
    "priceCurrency": "USD"
  }
}
```

## BreadcrumbList (all pages, especially location hierarchies)

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "https://example.com/"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Category",
      "item": "https://example.com/category/"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "Current Page"
    }
  ]
}
```

## Combination Patterns

Most pages should combine multiple schemas. Common combos:

- **Service page:** LocalBusiness + FAQPage + BreadcrumbList
- **Comparison page:** FAQPage + BreadcrumbList
- **How-to page:** HowTo + FAQPage + BreadcrumbList
- **Location page:** LocalBusiness + FAQPage + BreadcrumbList
- **Product page:** Product + FAQPage + BreadcrumbList

When combining, wrap in an array:

```json
[
  { "@context": "https://schema.org", "@type": "FAQPage", ... },
  { "@context": "https://schema.org", "@type": "BreadcrumbList", ... }
]
```

## Validation

Always validate generated schema at:
- https://search.google.com/test/rich-results
- https://validator.schema.org/
