# kipris-cli

> Korean **patent / trademark / design** search CLI — wraps the official KIPRIS Plus OpenAPI (특허청).

[![ClawHub](https://img.shields.io/badge/ClawHub-kipris--cli-blue)](https://clawhub.ai/s/kipris-cli)

Five subcommands. Returns clean JSONL for AI agents and shell pipelines.

## Install

```bash
clawhub install kipris-cli
# or clone this repo and add bin/ to PATH
```

## Configure

Get a free `KIPRIS_PLUS_KEY` from <https://plus.kipris.or.kr> (월 10,000 calls free).

```bash
export KIPRIS_PLUS_KEY="your-32-char-key"
```

## Use

```bash
# Patent search
kipris-cli patent --word "양자컴퓨팅" --rows 10

# Trademark availability
kipris-cli trademark --word "AURORA" --class 9

# Design search
kipris-cli design --word "smart watch"

# Bibliographic detail
kipris-cli patent-detail --app-no 1020230012345

# All filings by an applicant
kipris-cli applicant --name "삼성전자주식회사" --rows 100
```

Full reference: see [SKILL.md](./SKILL.md).

## Examples

The `examples/` folder ships three end-to-end scripts:

- `competitor-patent-watch.sh` — daily JSONL feed of new patents filed by a competitor (paginated + dedup cursor).
- `brand-availability-check.sh` — TM availability table across NICE classes 9, 35, 42.
- `m-and-a-ip-snapshot.sh` — IP portfolio summary (patents + TMs + designs + top IPC) for a target company.

## Pairs with

- [`opendart-cli`](https://github.com/ChloePark85/opendart-cli) — corporate disclosures (financial side of M&A diligence)
- [`nts-bizno-cli`](https://github.com/ChloePark85/nts-bizno-cli) — KYB business-number lookup (anchor entity name)

## License

MIT-0
