# shlibrary-seat-booking

Shanghai Library East Branch 3F seat booking skill.

This skill supports:

- browser-assisted login and profile-based auth refresh
- multi-profile auth files
- listing reservations
- checking all-day common availability
- booking seats for one period or the full day
- canceling reservations

## Structure

- `SKILL.md`: skill-facing usage guide
- `scripts/`: CLI entrypoints and implementation
- `references/`: API notes and request/response examples

## Requirements

- Node.js
- Playwright

Install dependencies from this directory:

```bash
npm install playwright
npx playwright install chromium
```

## Auth storage

By default, auth files are stored outside the repository:

- default profile: `~/.config/shlibrary-seat-booking/profiles/default.json`
- named profile: `~/.config/shlibrary-seat-booking/profiles/<profile>.json`

The repository should not contain real auth files or captured tokens.

## Common commands

Run commands from this directory:

```bash
node ./scripts/book_seat.js list --profile user1
node ./scripts/book_seat.js availability --profile user1 --date 2026-03-20 --area 北区 东区
node ./scripts/book_seat.js book --profile user1 --date 2026-03-24 --period 下午 --area 南区 --seat-row 4 --seat-no 5
node ./scripts/book_seat.js cancel --profile user1 --reservation-id 5187335
node ./scripts/login.js --profile user1
```

For full behavior and workflow details, see `SKILL.md`.
