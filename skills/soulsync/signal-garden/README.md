# Signal Garden

> Backend & Frontend for Soulsync Signal System

## Quick Start

```bash
# Install dependencies
npm install

# Run locally
npm run dev
```

Visit `http://localhost:3000`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/signals` | List all signals (paginated) |
| POST | `/api/signals` | Emit a new signal |
| GET | `/api/signals/random` | Get one random signal |
| DELETE | `/api/signals/expired` | Cleanup expired signals |

## Deploy to Vercel

```bash
npm i -g vercel
cd signal-garden
vercel
```

## Tech Stack

- **Framework**: Next.js 14
- **Database**: In-memory (for demo)
- **Hosting**: Vercel (free tier)

## Environment Variables

Not required for demo. In-memory database resets on cold start.

For production, replace `lib/db.ts` with a real database:
- Vercel Postgres
- Upstash Redis
- Cloudflare D1
