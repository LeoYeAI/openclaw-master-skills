# Security Disclosure: ima-sevio-ai

## Purpose

This document explains endpoint usage, credential flow, and local data behavior for `ima-sevio-ai`.

## Cross-Skill Reads

`ima-sevio-ai` runs standalone and does not require reading any other skill files.
If `ima-knowledge-ai` is installed, those references may be read optionally for guidance only.

## Network Endpoints

| Domain | Used For | Trigger |
|---|---|---|
| `api.imastudio.com` | Product list, task create, task detail polling | All requests |
| `imapi.liveme.com` | Upload-token request for local media inputs | Only when `--input-images` contains local file paths |
| `*.aliyuncs.com` / `*.esxscloud.com` | Presigned binary upload + media CDN delivery | Returned by upload-token API |

For remote media URLs (`http(s)://...`), the script passes URLs directly and does not need upload-token calls.

## Credential Flow

| Credential | Where Sent | Why |
|---|---|---|
| `IMA_API_KEY` | `api.imastudio.com` | Open API auth (`Authorization: Bearer ...`) |
| `IMA_API_KEY` | `imapi.liveme.com` | Upload-token auth for local media uploads |

No API key is sent to presigned upload hosts (`aliyuncs/esxscloud`) during binary upload.

## Model Scope

User-facing model names are restricted to:

- `Ima Sevio 1.0` (mapped to `ima-pro`)
- `Ima Sevio 1.0-Fast` (mapped to `ima-pro-fast`)

Other model aliases are not exposed in this skill.

## Local Data

| Path | Content | Retention |
|---|---|---|
| `~/.openclaw/memory/ima_prefs.json` | Per-user model preference cache | Until manually removed |
| `~/.openclaw/logs/ima_skills/` | Operational logs | Auto-cleaned by script after 7 days |

No API key is written into repository files.
