# Kaipai AI (OpenClaw skill)

Process images and video with **Kaipai AI**: watermark removal and quality restoration. Works inside [OpenClaw](https://github.com/openclaw/openclaw) with a single CLI entrypoint: `scripts/kaipai_ai.py`.

## Capabilities

Calls go to the **Kaipai commercial API** and **consume account quota** (credits) for the configured **MT_AK** tenant. Agents must not tell users the service is free or guess pricing — see [SKILL.md](SKILL.md) (*Billing and user-facing claims*).

| task_name | What it does |
|-----------|----------------|
| `eraser_watermark` | Image watermark removal |
| `videoscreenclear` | Video watermark removal |
| `image_restoration` | Image quality restoration |
| `hdvideoallinone` | Video quality restoration |

## Install

Install the skill folder as your OpenClaw skill (path or marketplace URL your host documents), then restart the gateway if required.

## One-time setup

1. Put **MT_AK** and **MT_SK** in `scripts/.env` (or export them in the environment).
2. Run:

```bash
python3 scripts/kaipai_ai.py preflight
```

Output must be `ok`.

## Dependencies

```bash
python3 scripts/kaipai_ai.py install-deps
```

Uses `scripts/requirements.txt` (e.g. `requests`, OSS client as needed).

## URL inputs (`--input https://...`)

- **Shell:** Quote the full URL so `&` in query strings is not broken (e.g. signed storage URLs).
- **Limits:** Streamed download with **15s connect / 120s read** timeouts and **100MB** max by default (shared with `resolve-input --url`). Override: `MT_AI_URL_CONNECT_TIMEOUT`, `MT_AI_URL_READ_TIMEOUT`, `MT_AI_URL_MAX_BYTES`.
- **Large or slow media:** Use `resolve-input --url …` to save locally, then pass the returned `path` as `--input`.

## Quick examples

**Image watermark removal (blocking):**

```bash
python3 scripts/kaipai_ai.py run-task \
  --task eraser_watermark \
  --input "https://example.com/photo.jpg"
```

**Video task (async worker payload):**

```bash
python3 scripts/kaipai_ai.py spawn-run-task \
  --task hdvideoallinone \
  --input "https://example.com/clip.mp4" \
  --deliver-to "oc_xxx_or_ou_xxx" \
  --deliver-channel feishu
```

Pass the printed `sessions_spawn_args` to OpenClaw `sessions_spawn`. Keep **`runTimeoutSeconds`** at the payload default (**3600**); do not reduce it without accepting timeout risk. Wall time varies. If a host **session/tool wait cap** cuts off before JSON finishes, recover with **`last-task`** / **`history`** / **`query-task`** (see [SKILL.md](SKILL.md) and [docs/errors-and-polling.md](docs/errors-and-polling.md)).

**Two-stage video** (e.g. `videoscreenclear` then `hdvideoallinone`): run **`spawn-run-task` + `sessions_spawn` twice** — one embed per stage, like medeo-video’s one-command-per-spawn. After the first worker finishes, take **`primary_result_url`** from its JSON (or **`last-task`**) and pass it as **`--input`** on the second **`spawn-run-task`**. No extra CLI flags.

**Resume polling by task id:**

```bash
python3 scripts/kaipai_ai.py query-task --task-id "<full_task_id>"
```

**Last run / history (local state under `~/.openclaw/workspace/openclaw-kaipai-ai/`):**

```bash
python3 scripts/kaipai_ai.py last-task
python3 scripts/kaipai_ai.py history
```

**IM attachment → local path for `--input`:**

```bash
python3 scripts/kaipai_ai.py resolve-input --telegram-file-id "AgAC..." --output-dir /tmp
```

See [docs/im-attachments.md](docs/im-attachments.md) and [SKILL.md](SKILL.md) for agents.

## Operators

**One line:** Video tasks → **`spawn-run-task`** (not a blocking **`run-task`** in the main session); if a job was cut off or the user asks for status → **`last-task`** / **`query-task`** — never submit **`run-task`** again for the same **`task_id`**.

**New jobs:** Agents must submit only via **`kaipai_ai.py run-task`** (or the same command inside **`spawn-run-task`**); do not call AIGC/wapi directly and skip **`/skill/consume.json`** — see [SKILL.md](SKILL.md) section **API submission path (MANDATORY)**.

## Docs

- [SKILL.md](SKILL.md) — agent instructions
- [docs/multi-platform.md](docs/multi-platform.md) — delivery (Feishu, Telegram, Discord, …)
- [docs/errors-and-polling.md](docs/errors-and-polling.md) — env vars, polling, failures
- [docs/feishu-send-video.md](docs/feishu-send-video.md) — Feishu native video send

## License

MIT (see repository root if present).
