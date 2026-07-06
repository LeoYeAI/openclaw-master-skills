# Customs Declaration Guide

This document covers creating customs declarations for international shipments. A customs declaration is required whenever sender and recipient are in different countries.

---

## Overview: Two-Step Process

International labels require customs documentation before the shipment can be created:

1. **Create customs items** -- one per distinct product in the shipment.
2. **Create the customs declaration** -- references the items and contains certifications.
3. **Attach the declaration** to the shipment via the `customs_declaration` field.

---

## Step 1: Create Customs Items

Call `customs-items-create` once per distinct item type in the shipment.

### Required Fields

| Field | Type | Description |
|---|---|---|
| `description` | string | Plain-language description of the item (e.g., "cotton t-shirt") |
| `quantity` | integer | Number of units |
| `net_weight` | string | Weight per unit (as a string, e.g., "0.5") |
| `mass_unit` | string | One of: `g`, `kg`, `lb`, `oz` |
| `value_amount` | string | Declared monetary value per unit (as a string, e.g., "25.00") |
| `value_currency` | string | ISO 4217 currency code (e.g., `USD`, `EUR`, `GBP`) |
| `origin_country` | string | ISO 3166-1 alpha-2 country code where the item was manufactured (e.g., `US`, `CN`) |

### Optional Fields

| Field | Type | Description |
|---|---|---|
| `tariff_number` | string | HS/HTS harmonized tariff code (6-10 digits). Required by most carriers. Ask the user if not provided. |
| `sku_code` | string | SKU or product code |
| ` eccn_ear99` | string | Export Control Classification Number |
| `metadata` | string | Free-form metadata |

### Example

```json
{
  "description": "Cotton t-shirt, blue, size M",
  "quantity": 3,
  "net_weight": "0.3",
  "mass_unit": "lb",
  "value_amount": "15.00",
  "value_currency": "USD",
  "origin_country": "US",
  "tariff_number": "6109100012"
}
```

### HS / Tariff Codes

HS (Harmonized System) codes classify goods for customs. They are typically 6 digits internationally, extended to 8-10 digits for country-specific tariff schedules (HTS in the US).

**USPS requires 6-digit HS codes on ALL international commercial shipments (as of September 2025). FedEx and DHL strongly recommend them. Shipments without HS codes risk delays or rejection.**

- If the user does not know the HS code, ask them to describe the product. Common codes:
  - Clothing: 6109 (t-shirts), 6110 (sweaters), 6204 (women's suits/trousers)
  - Electronics: 8471 (computers), 8517 (phones), 8528 (monitors)
  - Books: 4901
  - Toys: 9503
  - Cosmetics: 3304
- If unsure, the user should consult their country's tariff schedule or a customs broker.

---

## Step 2: Create the Customs Declaration

Call `customs-declarations-create` with the item object_ids from step 1.

### Required Fields

| Field | Type | Description |
|---|---|---|
| `certify` | boolean | Must be `true`. Certifies the information is accurate. |
| `certify_signer` | string | Full name of the person certifying the declaration. |
| `contents_type` | string | Type of shipment contents. See values below. |
| `non_delivery_option` | string | What to do if the package is undeliverable. See values below. |
| `items` | array | Array of customs item object_ids from step 1. |

### Optional Fields

| Field | Type | Description |
|---|---|---|
| `contents_explanation` | string | Required if `contents_type` is `OTHER`. Free-text explanation. |
| `exporter_reference` | string | Exporter reference number |
| `importer_reference` | string | Importer reference number |
| `invoice` | string | Invoice number |
| `license` | string | Export license number |
| `certificate` | string | Certificate number |
| `notes` | string | Additional notes |
| `eel_pfc` | string | Electronic Export License or Post Office Filing Citation. Values: `NOEEI_30_37_a`, `NOEEI_30_37_h`, `NOEEI_30_36`, `AES_ITN`. **Strongly recommended for US-origin shipments** -- USPS will warn if absent. For shipments to Canada, use `NOEEI_30_36` regardless of value. For non-Canada destinations: shipments under $2,500 use `NOEEI_30_37_a`; shipments over $2,500 require an AES/ITN number. |
| `incoterm` | string | Incoterms trade term (e.g., `DDP`, `DDU`, `DAP`, `FCA`). Some carriers require this to return rates. |
| `b13a_filing_option` | string | Canada B13A filing. Values: `FILED_ELECTRONICALLY`, `SUMMARY_REPORTING`, `NOT_REQUIRED` |
| `metadata` | string | Free-form metadata |

### contents_type Values

| Value | When to Use |
|---|---|
| `MERCHANDISE` | Commercial goods being sold |
| `GIFT` | Gifts with no commercial value |
| `SAMPLE` | Product samples |
| `RETURN_MERCHANDISE` | Returned merchandise |
| `HUMANITARIAN_DONATION` | Humanitarian aid or donations |
| `DOCUMENTS` | Paper documents only |
| `OTHER` | Anything else (must provide `contents_explanation`) |

### non_delivery_option Values

| Value | Meaning |
|---|---|
| `RETURN` | Return the package to sender if undeliverable |
| `ABANDON` | Abandon the package (carrier disposes of it) |

If the user does not specify, ask them. `RETURN` is the safer default for valuable goods.

### Example

```json
{
  "certify": true,
  "certify_signer": "Jane Smith",
  "contents_type": "MERCHANDISE",
  "non_delivery_option": "RETURN",
  "items": [
    "customs_item_abc123",
    "customs_item_def456"
  ],
  "invoice": "INV-2024-0042",
  "eel_pfc": "NOEEI_30_37_a"
}
```

---

### Commercial Invoice

Shippo automatically generates 3 copies of the commercial invoice for international shipments. The invoice URL is returned in the transaction response after label purchase.

---

## Step 3: Attach to Shipment

When calling `shipments-create`, include the `customs_declaration` field set to the object_id returned from step 2:

```json
{
  "address_from": { ... },
  "address_to": { ... },
  "parcels": [ ... ],
  "customs_declaration": "customs_declaration_xyz789"
}
```

---

## Sender Address Requirements for International Shipments

The sender address (`address_from`) must include:
- `email` -- required by carriers for customs processing
- `phone` -- required by carriers for customs processing

If the user's sender address is missing these fields, ask before proceeding.

---

## Batch Processing with Customs

When processing a CSV batch that includes international rows:

1. Identify international rows by comparing `sender_country` and `recipient_country`.
2. For each international row, create customs items from the row data (use `package_description` for the item description, `package_weight` for net_weight, `declared_value` for value_amount).
3. Create a customs declaration per international row.
4. Include the declaration object_id in the batch shipment object's `customs_declaration` field.
5. Ask the user once for shared values: `contents_type`, `non_delivery_option`, and `certify_signer`. Reuse across all international rows unless the CSV provides per-row values.

---

## Common Issues

### Missing HS/Tariff Code
Most carriers require tariff_number for customs clearance. If omitted, the shipment may be delayed or rejected at customs. Always ask the user for this value.

### Value Declaration
Under-declaring item values is illegal and can result in fines or seizure. Ensure `value_amount` reflects the actual market value of the goods.

### EEL/PFC for US Exports
For shipments to Canada, use `NOEEI_30_36` regardless of value. For non-Canada destinations: shipments under $2,500 use `NOEEI_30_37_a` (most common exemption); shipments over $2,500 require an AES/ITN filing -- set `eel_pfc` to the ITN number.

### Restricted and Prohibited Items
The Shippo API does not enforce import/export restrictions. The user is responsible for ensuring their goods are legal to ship to the destination country. If the user mentions shipping batteries, liquids, food, plants, or weapons, advise them to check destination country import regulations.

---

## Decision Trees

### contents_type Selection

Use this logic to determine `contents_type` when the user does not specify:

1. Is the user selling the items? --> `MERCHANDISE`
2. Is it a gift with no commercial value? --> `GIFT`
3. Is it a product sample? --> `SAMPLE`
4. Are the contents paper documents only? --> `DOCUMENTS`
5. Is it a return/exchange of previously purchased goods? --> `RETURN_MERCHANDISE`
6. Is it a charitable/humanitarian donation? --> `HUMANITARIAN_DONATION`
7. None of the above? --> `OTHER` (must also provide `contents_explanation`)

When in doubt, ask the user. `MERCHANDISE` is the most common value.

### Incoterms Selection

Incoterms define who pays duties and taxes. Use this logic:

- **B2C e-commerce (default):** `DDU` (Delivered Duty Unpaid) -- the recipient pays duties/taxes on delivery. This is the standard default.
- **Seller prepays duties/taxes:** `DDP` (Delivered Duty Paid) -- the sender pays all duties and taxes. Not supported by USPS (always DDU). Supported by UPS, FedEx, DHL.
- **FedEx/DHL warehouse or third-party handoff:** `FCA` (Free Carrier) -- seller delivers to a named place (carrier facility). Used for B2B or drop-ship scenarios.
- **DHL Express:** Also supports `DAP` (Delivered at Place), similar to DDU.

If the user does not specify, use `DDU` for B2C shipments. If the user says they want to prepay duties for their customers, use `DDP`.
