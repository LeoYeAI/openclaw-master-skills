---
name: ubtrippin
version: 2.1.0
description: "Lite reference — 5 core operations. Full docs: GET https://www.ubtrippin.xyz/api/v1/docs"
---

# UBTRIPPIN — Quick Reference

Base: `https://www.ubtrippin.xyz` | Auth: `Authorization: Bearer ubt_k1_...`

## 1. List Trips
```
GET /api/v1/trips?status=upcoming
```

## 2. Get Trip Details
```
GET /api/v1/trips/:id
```

## 3. Add Item to Trip
```
POST /api/v1/trips/:id/items
Content-Type: application/json

{ "kind": "flight", "start_date": "2026-04-01", "summary": "AF276 CDG→NRT", "provider": "Air France" }
```
Kinds: `flight`, `hotel`, `car_rental`, `train`, `activity`, `restaurant`, `ticket`, `other`
Required: `kind` + `start_date`. Optional: `end_date`, `start_ts`, `end_ts`, `start_location`, `end_location`, `provider`, `confirmation_code`, `traveler_names`, `details_json`

## 4. Loyalty Lookup
```
GET /api/v1/me/loyalty/lookup?provider_key=delta_skymiles
```

## 5. City Guide
```
GET /api/v1/guides?city=Paris
```

**Full API (60+ endpoints):** `GET https://www.ubtrippin.xyz/api/v1/docs`
