# `~/Projects/manager` pointers

Read when: you need the “how we do it here” for domains/DNS/redirects.

## Files

- `DOMAINS.md`: mappings + registrar quick map + known exclusions/outstanding NS flips.
- `DNS.md`: Cloudflare onboarding checklist + verification steps.
- `redirect-worker.ts`: Worker implementation (fallback redirect behavior).
- `redirect-worker-mapping.md`: host -> target mapping input.
- `bin/namecheap-set-ns`: Namecheap NS flip helper (env vars in `~/Projects/manager/profile`).
- `bin/cloudflare-ai-bots`: bot management helper (needs token perms).

## Fast navigation

- Find a domain: `rg -n \"\\bexample\\.com\\b\" ~/Projects/manager/DOMAINS.md`
- List scripts: `ls -la ~/Projects/manager/bin`

