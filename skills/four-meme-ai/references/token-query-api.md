# Token query REST API (Four.meme)

Base: `https://four.meme/meme-api/v1`. Requests need `Accept: application/json`; POST needs `Content-Type: application/json`. No login or cookie required.

## 1. Token list (search)

**POST** `/public/token/search`  
Body: JSON object with parameters below.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| pageIndex | integer | No | 1 | Page number |
| pageSize | integer | No | 20 | Result count per page |
| type | string | No | HOT | RankingType: NEW, PROGRESS, VOL, LAST, HOT, CAP, DEX, BURN |
| listType | string | No | NOR | ListType: NOR, NOR_DEX, BIN, USD1, BIN_DEX, USD1_DEX, ADV |
| keyword | string | No | - | Search keyword (fuzzy match) |
| symbol | string | No | - | Quote symbol: BNB, USDT, etc. |
| tag | array[string] | No | - | Tags: Meme, AI, Defi, Games, etc. |
| status | string | No | ALL | PUBLISH, TRADE, or ALL |
| sort | string | No | DESC | DESC or ASC |
| version | string | No | - | V9 (taxFee), V10 (AI); omit for all |

### Parameter usage

**type** – Ranking/list mode:
- `HOT` – Hot ranking (default)
- `NEW` – Newest created
- `PROGRESS` – Fundraise progress
- `VOL` – Total trading volume
- `LAST` – Latest active
- `CAP` – Market cap
- `DEX` – DEX-related
- `BURN` – Burn ranking

**listType** – List category:
- `NOR` – Normal publish list (default; status=PUBLISH)
- `NOR_DEX` – Normal DEX list (status=TRADE)
- `BIN` – Binance publish (BNB_MPC + PUBLISH)
- `USD1` – USD1 publish
- `BIN_DEX` – Binance DEX list
- `USD1_DEX` – USD1 DEX list
- `ADV` – Advanced list

**status** – Token state filter:
- `PUBLISH` – Published, not yet on DEX
- `TRADE` – On DEX, tradable
- `ALL` – No filter

**sort** – Order: `DESC` (default) or `ASC`.

**version** – Token version filter:
- `V9` – taxFee version
- `V10` – AI version
- Omit – All versions

### CLI examples

```bash
# Hot list (default)
fourmeme token-list

# Newest tokens, page 2, 30 per page
fourmeme token-list --type=NEW --sort=DESC --pageIndex=2 --pageSize=30

# Hot + advanced list
fourmeme token-list --type=HOT --listType=ADV

# DEX list (tradable tokens)
fourmeme token-list --listType=NOR_DEX

# Search by keyword
fourmeme token-list --keyword=dog

# Filter by tag (comma-separated)
fourmeme token-list --tag=Meme,AI

# Filter by quote symbol
fourmeme token-list --symbol=BNB

# V9 tokens only
fourmeme token-list --version=V9
```

**Legacy params** (mapped to new):
- `--orderBy=Hot` → type=HOT
- `--orderBy=TimeDesc` → type=NEW, sort=DESC
- `--orderBy=Time` → type=NEW
- `--tokenName=<x>` → keyword=<x>
- `--labels=<x>` → tag=<x>
- `--listedPancake=true` → listType=NOR_DEX

## 2. Token detail and trading info

**GET** `/private/token/get/v2?address=<tokenAddress>`

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| address | string | Yes | Token contract address (0x...) |

**CLI:** `fourmeme token-get <tokenAddress>`

## 3. Rankings (public)

**POST** `/public/token/ranking`  
Body: JSON object with parameters below.

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| type | string | Yes | - | Ranking type (RankingType enum), see table below |
| rankingKind | string | No | - | Ranking dimension (RankingKind) |
| version | string | No | - | Token version; taxFee version is V9 |
| symbol | string | No | - | Filter by quote symbol (e.g. BNB) |
| minCap | number | No | - | Min market cap |
| maxCap | number | No | - | Max market cap |
| minVol | number | No | - | Min trading volume |
| maxVol | number | No | - | Max trading volume |
| minHold | number | No | - | Min holder count |
| maxHold | number | No | - | Max holder count |
| pageSize | integer | No | 20 | Result count per page |

**RankingType (type):**

| Value | Description |
|-------|-------------|
| NEW | Newest created |
| PROGRESS | Fundraise progress |
| VOL_MIN_5 | 5 min trading volume |
| VOL_MIN_30 | 30 min trading volume |
| VOL_HOUR_1 | 1 hour trading volume |
| VOL_HOUR_4 | 4 hours trading volume |
| VOL_DAY_1 | 24 hours trading volume |
| VOL | Total trading volume |
| LAST | Latest active / recently updated |
| HOT | Hot ranking |
| CAP | Market cap ranking |
| DEX | DEX ranking |

### token-rankings parameter usage

**type** (required) – Ranking dimension:
- `NEW` – Newest created
- `PROGRESS` – Fundraise progress
- `VOL_MIN_5`, `VOL_MIN_30` – 5/30 min volume
- `VOL_HOUR_1`, `VOL_HOUR_4` – 1/4 hour volume
- `VOL_DAY_1` – 24h volume
- `VOL` – Total volume
- `LAST` – Latest active
- `HOT` – Hot ranking
- `CAP` – Market cap
- `DEX` – DEX ranking

**Filters** – Optional numeric filters: `minCap`, `maxCap`, `minVol`, `maxVol`, `minHold`, `maxHold`.

### token-rankings CLI examples

```bash
# Hot ranking
fourmeme token-rankings HOT

# 24h volume ranking
fourmeme token-rankings VOL_DAY_1

# Newest tokens
fourmeme token-rankings NEW

# With filters: BNB only, min cap 100
fourmeme token-rankings CAP --symbol=BNB --minCap=100

# V9 tokens, 50 results
fourmeme token-rankings HOT --version=V9 --pageSize=50
```

**Legacy type mapping:** Time→NEW, ProgressDesc→PROGRESS, TradingDesc→VOL_DAY_1, Hot→HOT, Graduated→DEX.
