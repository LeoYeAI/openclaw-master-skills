# Customer context — template

**New here?** Full flow: [SKILL-SETUP.md](SKILL-SETUP.md).

Copy to `team/customers/<customer_id>/CONTEXT.md` and fill in. **Do not commit secrets** — use references to your vault / OpenClaw secrets.

## Identity

- **Customer id (slug):**
- **Display name:**
- **Primary contact (role, channel):**

## Repositories

- **Repo 1** (URL, default branch, main package/app):
- **Repo 2** (if any):

## Documentation

- **Internal wiki / Notion / Confluence:**
- **Runbooks:**
- **Shopware / hosting docs:**

## Shopware (if applicable)

- **Staging admin URL** (path only if needed; no credentials here):
- **Staging storefront URL:**
- **Sales channel / rule sets** relevant to this task:
- **Production:** changes only with explicit approval; document who approved.

## Environments

- **CI:** (link or name)
- **Staging:** how to deploy / verify
- **Secrets:** named entries in _(vault product)_ — e.g. `customer_acme_staging_admin`

## Conventions

- Branch naming:
- PR / review policy:
- Definition of Done (short):

## Tasks (this customer)

Work items for this customer live under **`team/customers/<customer_id>/tasks/<task_id>/`** (same `<customer_id>` as this file). Create that folder when starting a new task; use `SPEC.md`, `HANDOFF.md`, and `QA_NOTES.md` inside it. See [SKILL.md — Extended shared directory layout](../SKILL.md).

## Open decisions / warnings

- Anything the next agent must not assume:
