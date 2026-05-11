# Tax Token parameters (tokenTaxInfo)

When creating a **Tax-type token**, send a `tokenTaxInfo` object in the create request body. If omitted, a normal token is created. Agent interaction (whether to create a tax token, parameter order) is in [SKILL.md](../SKILL.md) “Create token (full flow)”. This page only lists fields and constraints.

## Field summary

| Parameter | Type | Description | Allowed values / constraint |
|-----------|------|-------------|------------------------------|
| **feeRate** | number | Trading fee rate (%) | **Exactly one of**: `1`, `3`, `5`, `10` |
| **burnRate** | number | Burn share (%) | Custom; see constraints below |
| **divideRate** | number | Dividend share (%) | Custom; see below |
| **liquidityRate** | number | Liquidity share (%) | Custom; see below |
| **recipientRate** | number | Recipient share (%) | Custom; use `0` if not used |
| **recipientAddress** | string | Address that receives allocation | Use `""` if not used |
| **minSharing** | number | Min balance for dividends (ether units) | Must satisfy `d × 10ⁿ`, n≥5, 1≤d≤9 |

## Constraints

1. **feeRate** must be one of **1, 3, 5, 10** (1%, 3%, 5%, 10%).
2. **burnRate + divideRate + liquidityRate + recipientRate = 100** (the four shares must sum to 100).
3. If no recipient: **recipientAddress = ""** and **recipientRate = 0**.
4. **minSharing** examples: `100000` (1×10⁵), `200000`, `500000`, `1000000` (1×10⁶), `9000000`, `10000000` (1×10⁷), i.e. `d × 10ⁿ` with n≥5, 1≤d≤9.

## Examples

**Example 1: 5% fee, 20% burn, 30% dividend, 40% liquidity, 10% recipient**

```json
{
  "tokenTaxInfo": {
    "feeRate": 5,
    "burnRate": 20,
    "divideRate": 30,
    "liquidityRate": 40,
    "recipientRate": 10,
    "recipientAddress": "0x1234567890123456789012345678901234567890",
    "minSharing": 100000
  }
}
```

**Example 2: 3% fee, 100% liquidity, no dividend/burn/recipient**

```json
{
  "tokenTaxInfo": {
    "feeRate": 3,
    "burnRate": 0,
    "divideRate": 0,
    "liquidityRate": 100,
    "recipientRate": 0,
    "recipientAddress": "",
    "minSharing": 100000
  }
}
```

**Example 3: 10% fee, 50% dividend, 50% burn, min share 1×10⁶**

```json
{
  "tokenTaxInfo": {
    "feeRate": 10,
    "burnRate": 50,
    "divideRate": 50,
    "liquidityRate": 0,
    "recipientRate": 0,
    "recipientAddress": "",
    "minSharing": 1000000
  }
}
```

## Use in scripts

- **Option 1 (recommended)**: Write the above `tokenTaxInfo` to a JSON file (can contain only `tokenTaxInfo`) and pass that file path as the last argument to `create-token-api.ts`; the script merges it into the create body.
- **Option 2**: Build tax params via env vars (see “Create token (API)” optional env in SKILL.md).
