# Four.meme API – Create Token

Base URL: `https://four.meme/meme-api/v1`

## Endpoints (in order)

| Step | Method | Path | Description |
|------|--------|------|-------------|
| 1 | POST | `/private/user/nonce/generate` | Get nonce |
| 2 | POST | `/private/user/login/dex` | Login → access_token |
| 3 | POST | `/private/token/upload` | Upload image → imgUrl |
| 4 | POST | `/private/token/create` | Create → createArg, signature |

## 1. Nonce

- **URL**: `https://four.meme/meme-api/v1/private/user/nonce/generate`
- **Body**: `{ "accountAddress": "<wallet>", "verifyType": "LOGIN", "networkCode": "BSC" }`
- **Response**: `{ "code": "0", "data": "<nonce>" }`

## 2. Login

- **URL**: `https://four.meme/meme-api/v1/private/user/login/dex`
- **Body**: Include `verifyInfo.signature` = sign(`You are sign in Meme {nonce}`) with wallet, `verifyInfo.address`, `verifyInfo.networkCode` ("BSC"), `verifyInfo.verifyType` ("LOGIN"), plus region, langType, walletName, etc.
- **Response**: `{ "code": "0", "data": "<access_token>" }`

## 3. Upload image

- **URL**: `https://four.meme/meme-api/v1/private/token/upload`
- **Headers**: `meme-web-access: <access_token>`, `Content-Type: multipart/form-data`
- **Body**: `file` = image (jpeg/png/gif/bmp/webp)
- **Response**: `{ "code": "0", "data": "<imgUrl>" }`

## 4. Create token

- **URL**: `https://four.meme/meme-api/v1/private/token/create`
- **Headers**: `meme-web-access: <access_token>`, `Content-Type: application/json`
- **Body**: **Required**: **raisedAmount** (raise amount; use 24 or raisedToken.totalBAmount from public config), **raisedToken** (from `GET /public/config`; do not modify). Customizable: name, shortName, desc, imgUrl, launchTime, label, lpTradingFee (0.0025), webUrl, twitterUrl, telegramUrl, preSale, onlyMPC, feePlan, tokenTaxInfo (optional).
- **Response**: `{ "code": "0", "data": { "createArg": "...", "signature": "..." } }`

Then call **TokenManager2.createToken(createArg, sign)** on BSC with these values (as bytes).

## Labels

Meme, AI, Defi, Games, Infra, De-Sci, Social, Depin, Charity, Others.

## tokenTaxInfo (optional; Tax-type token)

Omit to create a normal token; include to create a tax-type token.

- **feeRate**: Trading fee; must be **1, 3, 5, or 10** (1%/3%/5%/10%).
- **burnRate**, **divideRate**, **liquidityRate**, **recipientRate**: All percentages; **sum of the four must be 100**.
- **recipientAddress**: Address that receives the recipient share; use `""` when not used, and **recipientRate = 0**.
- **minSharing**: Min balance to participate in dividends (ether units); must satisfy **minSharing = d×10ⁿ**, n≥5, 1≤d≤9, e.g. 100000, 1000000.

Full field description and examples: [token-tax-info.md](token-tax-info.md).
