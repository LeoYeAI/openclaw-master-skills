# Print-on-Demand API Examples

## Good Example: String Printful IDs + Variants

```bash
curl -X POST https://api.clawver.store/v1/products \
  -H "Authorization: Bearer $CLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name":"AI Studio Tee",
    "type":"print_on_demand",
    "priceInCents":2499,
    "printOnDemand":{
      "printfulProductId":"71",
      "printfulVariantId":"4012",
      "variants":[{"id":"tee-s","name":"Tee / S","printfulVariantId":"4012","priceInCents":2499}]
    }
  }'
```

Why this works: Printful IDs are sent as strings and variants are configured.

## Bad Example: Numeric Printful IDs

```json
{"printOnDemand":{"printfulProductId":71,"printfulVariantId":4012}}
```

Why it fails: integration expects string IDs.

Fix: send `"71"` and `"4012"`.

## Bad Example: Activate POD With Empty Variants

```json
{"status":"active"}
```

Why it fails: POD activation requires a non-empty `printOnDemand.variants` array.

Fix: configure variants first, then activate.

## Good Example: Idempotent POD AI Design Generation

```bash
curl -X POST https://api.clawver.store/v1/products/{productId}/pod-design-generations \
  -H "Authorization: Bearer $CLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Minimal monochrome tiger head logo",
    "placement": "front",
    "variantId": "4012",
    "idempotencyKey": "podgen-1"
  }'
```

Why this works: retries with the same key and payload reuse the same generation task and avoid duplicate credit debits.

## Bad Example: Reusing Idempotency Key With Different Payload

```bash
curl -X POST https://api.clawver.store/v1/products/{productId}/pod-design-generations \
  -H "Authorization: Bearer $CLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Different concept",
    "placement": "back",
    "variantId": "4012",
    "idempotencyKey": "podgen-1"
  }'
```

Why it fails: the same idempotency key cannot be reused for a different request fingerprint.

Fix: use a new idempotency key for materially different prompts/specs.
