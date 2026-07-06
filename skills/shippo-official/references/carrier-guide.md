# Carrier Guide

Per-carrier nuances, requirements, and gotchas for the major carriers supported by Shippo.

---

## USPS

### Setup
- A **managed USPS account** is available by default on all Shippo accounts. No additional configuration needed.
- Carrier token: `usps`

### Key Details
- **HS codes required** for ALL international commercial shipments as of September 2025. Minimum 6 digits.
- **No DDP support.** USPS always ships DDU (recipient pays duties/taxes). Do not set `incoterm` to `DDP` for USPS.
- **Flat-rate options** available via parcel templates (e.g., `USPS_FlatRateEnvelope`, `USPS_SmallFlatRateBox`, `USPS_MediumFlatRateBox1`, `USPS_LargeFlatRateBox`). When using flat rate, parcel dimensions are ignored -- only weight matters for eligibility.
- **EEL/PFC required** for international shipments. USPS will warn/reject if `eel_pfc` is missing on customs declarations.
- **Tracking number format:** 20-22 digits, or starts with `9` followed by 20+ digits (e.g., `9400111899223100001234`).
- **Max weight:** 70 lbs domestic, 66 lbs international (varies by destination).
- **Signature confirmation:** Available via `extra.signature_confirmation` (`STANDARD`, `ADULT`). Not available on all service levels.

### Common Service Levels
| Token | Name |
|---|---|
| `usps_priority` | Priority Mail |
| `usps_priority_express` | Priority Mail Express |
| `usps_ground_advantage` | Ground Advantage |
| `usps_first` | First-Class Mail |
| `usps_media_mail` | Media Mail |

---

## UPS

### Setup
- **Requires Terms & Conditions acceptance** via the Shippo web app before API use. If the user gets auth errors for UPS, direct them to accept T&C in the Shippo dashboard.
- Carrier token: `ups`

### Key Details
- **Supports DDP** (Delivered Duty Paid). Set `incoterm` to `DDP` on the customs declaration.
- **Signature confirmation options:** `STANDARD`, `ADULT`, `CERTIFIED`, `INDIRECT`
- **Tracking number format:** Starts with `1Z` followed by 16 alphanumeric characters (e.g., `1Z999AA10123456784`).
- **Residential surcharge** applies automatically when the destination is residential. Shippo flags residential addresses during validation.
- **Saturday delivery** available for select services via `extra.saturday_delivery = true`.
- **Max weight:** 150 lbs per package.

### Common Service Levels
| Token | Name |
|---|---|
| `ups_ground` | UPS Ground |
| `ups_next_day_air` | UPS Next Day Air |
| `ups_2nd_day_air` | UPS 2nd Day Air |
| `ups_3_day_select` | UPS 3 Day Select |
| `ups_express` | UPS Worldwide Express |
| `ups_expedited` | UPS Worldwide Expedited |

---

## FedEx

### Setup
- Carrier token: `fedex`
- Requires a FedEx account connected via the Shippo dashboard.

### Key Details
- **Supports DDP** via `duties_payor` field and `incoterm` = `DDP`.
- **FCA incoterm** available for B2B / drop-ship scenarios.
- **Dangerous goods / dry ice** supported via `extra.dangerous_goods` and `extra.dry_ice` fields.
- **Tracking number format:** 12 or 15 digits (e.g., `123456789012` or `123456789012345`).
- **Residential surcharge** applied automatically.
- **Saturday delivery** available via `extra.saturday_delivery = true`.
- **Signature options:** `STANDARD`, `ADULT`, `DIRECT`, `INDIRECT`
- **Max weight:** 150 lbs per package (FedEx Ground), 2200 lbs (FedEx Freight).
- **HS codes** strongly recommended for international shipments.

### Common Service Levels
| Token | Name |
|---|---|
| `fedex_ground` | FedEx Ground |
| `fedex_home_delivery` | FedEx Home Delivery |
| `fedex_2_day` | FedEx 2Day |
| `fedex_express_saver` | FedEx Express Saver |
| `fedex_standard_overnight` | FedEx Standard Overnight |
| `fedex_priority_overnight` | FedEx Priority Overnight |
| `fedex_international_economy` | FedEx International Economy |
| `fedex_international_priority` | FedEx International Priority |

---

## DHL Express

### Setup
- Carrier token: `dhl_express`
- Requires a DHL Express account connected via the Shippo dashboard.

### Key Details
- **DDP and DAP support.** Strong international coverage. DHL is often the best option for international shipments outside North America.
- **HS codes** strongly recommended for all international shipments.
- **Tracking number format:** 10 digits (e.g., `1234567890`).
- **Max weight:** 150 lbs per package.
- **Signature:** Included by default on most service levels.
- **Volumetric weight** (dimensional weight) is calculated using a divisor of 5000 (cm) or 139 (inches), which is more aggressive than domestic carriers.

### Common Service Levels
| Token | Name |
|---|---|
| `dhl_express_worldwide` | DHL Express Worldwide |
| `dhl_express_12_00` | DHL Express 12:00 |
| `dhl_express_09_00` | DHL Express 9:00 |

---

## Surcharges to Watch For

These surcharges are common across carriers and can significantly impact final cost:

| Surcharge | Carriers | Trigger |
|---|---|---|
| **Residential delivery** | UPS, FedEx | Delivering to a residential address |
| **Saturday delivery** | UPS, FedEx | Delivery scheduled for Saturday |
| **Signature confirmation** | All | Requesting signature on delivery |
| **Additional handling** | UPS, FedEx | Packages exceeding certain dimensions or weight thresholds |
| **Address correction** | UPS, FedEx | Carrier corrects an invalid address |
| **Fuel surcharge** | All | Applied automatically, varies by carrier and period |
| **Remote area / extended delivery** | DHL, FedEx | Delivery to remote or rural areas |

---

## Label Size Defaults by Carrier

- **USPS:** 4x6 thermal labels standard
- **UPS:** 4x6 or 4x8
- **FedEx:** 4x6 standard, some services require 4x8
- **DHL Express:** 4x6 standard

When in doubt, use `PDF_4x6` -- it works across all carriers.
