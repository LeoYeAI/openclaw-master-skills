# Gotchas

<!-- This file is loaded when starting unfamiliar tasks or debugging unexpected behavior. -->
<!-- Each entry: what looks right, what's actually wrong, and how to handle it. -->

## Build & Deploy

- [e.g., `pnpm build` silently succeeds even with type errors. Always run `pnpm typecheck` separately.]

## Database

- [e.g., Prisma migrations must be run in order. Never skip a migration even if the schema looks correct.]

## Auth

- [e.g., Session tokens expire after 24h in dev but 7d in prod. Don't assume session persistence in tests.]

## Testing

- [e.g., Integration tests require the dev DB to be running. `docker compose up db` first.]

## Third-Party APIs

- [e.g., Stripe webhook signatures fail in dev unless you run `stripe listen --forward-to localhost:3000/api/webhooks/stripe`.]
