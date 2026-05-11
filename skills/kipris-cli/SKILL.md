---
name: kipris-cli
description: Korean patent / trademark / design search via KIPRIS Plus OpenAPI (특허청). Search patents (특허/실용신안), trademarks (상표), and designs (디자인) by keyword, applicant, or application/registration number. Returns clean JSONL for AI agents. Use for prior-art search, competitor IP monitoring, brand-name availability checks, M&A due diligence, and Korean IP analytics. Requires a free KIPRIS_PLUS_KEY from plus.kipris.or.kr.
license: MIT-0
---

# kipris-cli — Korean Patent / Trademark / Design search (KIPRIS Plus)

Five subcommands that wrap the **KIPRIS Plus OpenAPI** (특허청 한국특허정보원) — Korea's authoritative IP database covering ~5M patents, ~6M trademarks, ~1M designs. Every endpoint returns XML; this skill normalizes it to **JSONL** for AI-agent consumption.

> **Why this matters**: Korean IP lookups are otherwise locked behind kipris.or.kr's web UI. AI agents doing prior-art search, M&A target diligence, or brand-name availability checks need clean JSON access. This is the only ClawHub skill covering KIPRIS at the time of publish.

## Quick start

```bash
export KIPRIS_PLUS_KEY="<your-32-char-key>"   # from plus.kipris.or.kr (free, ~1d approval)

# Patent search by keyword
bin/kipris-cli patent --word "양자컴퓨팅" --rows 10

# Trademark availability check
bin/kipris-cli trademark --word "AURORA" --rows 5

# Design search
bin/kipris-cli design --word "smart watch"

# Patent bibliographic detail by application number
bin/kipris-cli patent-detail --app-no 1020230012345

# Search patents by applicant name (개인/법인)
bin/kipris-cli applicant --name "삼성전자주식회사" --rows 20
```

## Subcommands

| Command | Endpoint | Use case |
|---|---|---|
| `patent` | `patUtiModInfoSearchSevice/patUtiModInfoSearch` | Patent + 실용신안 keyword search |
| `trademark` | `TrademarkInfoSearchService/trademarkInfoSearchInfo` | Brand availability + competitor TM watch |
| `design` | `DesignInfoSearchService/designInfoSearchInfo` | Industrial design search |
| `patent-detail` | `patUtiModInfoSearchSevice/patUtiModBibliographicInfoSearch` | Full bibliographic detail by 출원번호 |
| `applicant` | `patUtiModInfoSearchSevice/patUtiModInfoSearchByApplicantName` | All filings by applicant (출원인) |

### Common flags

- `--word "<query>"` — free-text Korean or English (UTF-8)
- `--app-no <13-digit>` — 출원번호 (1020230012345 = 특허, 4020210012345 = 상표, 3020230012345 = 디자인)
- `--rows N` — page size (default 30, max 500)
- `--page N` — 1-indexed page (default 1)
- `--format json|xml|jsonl` — output (default jsonl)
- `--key <KEY>` — override `$KIPRIS_PLUS_KEY`

### Patent-specific filters (subcommand `patent`)

- `--applicant "<name>"` — 출원인명
- `--inventor "<name>"` — 발명자명
- `--ipc "<code>"` — IPC 분류 (e.g. `G06N`)
- `--pat true|false` — include 특허 (default true)
- `--utility true|false` — include 실용신안 (default true)
- `--last-update YYYYMMDD` — 최종변경일 since

### Trademark-specific filters (subcommand `trademark`)

- `--applicant "<name>"`
- `--class "<NICE int>"` — 상품분류 (NICE classification 1-45)
- `--reg-status "registered|pending|rejected|expired"` — 권리상태
- `--start-date YYYYMMDD` / `--end-date YYYYMMDD` — 출원일 range

## Output schema (JSONL)

Each line is one record (patent/TM/design). Common fields normalized across types:

```json
{
  "type": "patent",
  "app_no": "1020230012345",
  "title_ko": "양자 회로 최적화 방법 및 장치",
  "title_en": "Method and apparatus for quantum circuit optimization",
  "applicant": "삼성전자주식회사",
  "inventors": ["홍길동", "김철수"],
  "app_date": "20230101",
  "reg_no": null,
  "reg_date": null,
  "pub_no": "1020240054321",
  "pub_date": "20240715",
  "ipc": ["G06N10/40", "G06F17/14"],
  "abstract": "..."
}
```

Trademarks add `nice_class`, `tm_kind` (문자/도형/입체); designs add `locarno_class`, `parts`.

## Setup — getting a KIPRIS_PLUS_KEY

1. Sign up at <https://plus.kipris.or.kr> (free; corporate or individual).
2. 마이페이지 → API 신청 → 무료 quota (월 10,000건).
3. Approval is typically same-business-day for personal, 2-3 days for corporate.
4. Copy the 32-char `ServiceKey` and `export KIPRIS_PLUS_KEY=...`.

> ⚠️ The legacy `kipris.or.kr` API endpoints have been deprecated since 2024Q4. This skill uses the current `plus.kipris.or.kr/kipo-api/kipi/...` paths.

## Examples

- **`examples/competitor-patent-watch.sh`** — daily JSONL feed of new patents filed by a competitor (paginated + dedup).
- **`examples/brand-availability-check.sh`** — check if a brand name has TM filings in NICE classes 9, 35, 42 (typical SaaS classes).
- **`examples/m-and-a-ip-snapshot.sh`** — given a 사업자등록번호 (via `nts-bizno-cli`) → corporate name → all KIPRIS filings → consolidated CSV. Pairs naturally with `opendart-cli` for full M&A due-diligence chain.

## Related skills

- `opendart-cli` — corporate disclosures (pair for IP-vs-financial due diligence)
- `nts-bizno-cli` — KYB business-number lookup (anchor entity name)
- `juso-address-cli` — registered address resolution
- `kosis-cli` — R&D investment statistics overlay

## Limits

- **Quota**: free tier is 10,000 calls/month. Each `patent --rows 30 --page 1` = 1 call. The skill caches nothing — caller is responsible for pagination throttling.
- **Latency**: typical 200–800ms per call.
- **Rate limit**: 30 req/sec hard cap from KIPRIS Plus. Bulk operations should sleep `0.05s` between calls.

## License

MIT-0. No warranty. Built using only the publicly documented KIPRIS Plus OpenAPI specification.
