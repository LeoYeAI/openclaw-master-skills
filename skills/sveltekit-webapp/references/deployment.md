# Deployment Configuration

## Check Available Targets

Before deploying, verify authentication for your deployment target (Vercel, Cloudflare, Netlify, etc.) and GitHub CLI. The preflight phase handles this automatically — see [cli-commands.md](cli-commands.md#preflight-checks) for the specific verification commands.

## Vercel (Recommended)

### Setup

Add the Vercel adapter using `npx sv add sveltekit-adapter` and select "vercel".

### GitHub Integration (Recommended)

**One-time setup:**
1. Create Vercel project via `vercel link` or the [Vercel dashboard](https://vercel.com/new)
2. Connect your GitHub repo in Vercel: **Settings → Git → Connect Git Repository**
3. Set production branch to `main`

**Benefits:**
- Push to deploy (no CLI needed after setup)
- Automatic preview URLs for branches
- Persistent branch URLs: `[project]-git-dev-[team].vercel.app`
- Preview URLs don't change with each commit

**Deploy:** Push to `main` for production, push to `dev` for a persistent preview URL.

### CLI Deploy (Alternative)

If you prefer CLI deploys over GitHub integration, use `vercel link` to connect, then `vercel` for preview or `vercel --prod` for production.

### svelte.config.js
```javascript
import adapter from '@sveltejs/adapter-vercel';

export default {
  kit: {
    adapter: adapter({
      runtime: 'nodejs22.x'  // or 'edge'
    })
  }
};
```

### Environment Variables
Set environment variables in the Vercel dashboard (Settings → Environment Variables) or via CLI with `vercel env add`.

---

## Cloudflare Pages

### Setup
```bash
npx sv add sveltekit-adapter  # choose: cloudflare, target: pages
```

### svelte.config.js
```javascript
import adapter from '@sveltejs/adapter-cloudflare';

export default {
  kit: {
    adapter: adapter({
      routes: {
        include: ['/*'],
        exclude: ['<all>']
      }
    })
  }
};
```

### Deploy via GitHub
1. Connect repo to Cloudflare Pages dashboard
2. Build command: `npm run build`
3. Output directory: `.svelte-kit/cloudflare`

### Wrangler CLI
Alternatively, install `wrangler` as a dev dependency and deploy with `npx wrangler pages deploy .svelte-kit/cloudflare`.

---

## Netlify

### Setup
```bash
npx sv add sveltekit-adapter  # choose: netlify
```

### svelte.config.js
```javascript
import adapter from '@sveltejs/adapter-netlify';

export default {
  kit: {
    adapter: adapter({
      edge: false,
      split: false
    })
  }
};
```

### netlify.toml
```toml
[build]
  command = "npm run build"
  publish = "build"

[functions]
  node_bundler = "esbuild"
```

### Deploy
Install the Netlify CLI globally, authenticate with `netlify login`, initialize with `netlify init`, then deploy with `netlify deploy --prod`.

---

## Node.js Server

### Setup
```bash
npx sv add sveltekit-adapter  # choose: node
```

### svelte.config.js
```javascript
import adapter from '@sveltejs/adapter-node';

export default {
  kit: {
    adapter: adapter({
      out: 'build',
      precompress: true
    })
  }
};
```

### Run
Build with `npm run build`, then start with `node build/index.js`.

### Environment Variables
Configure `PORT` (default 3000), `HOST` (e.g., 0.0.0.0), and `ORIGIN` (your production domain URL).

### Docker
```dockerfile
FROM node:22-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev
COPY build ./build
EXPOSE 3000
CMD ["node", "build/index.js"]
```

---

## Static Site

### Setup
```bash
npx sv add sveltekit-adapter  # choose: static
```

### svelte.config.js
```javascript
import adapter from '@sveltejs/adapter-static';

export default {
  kit: {
    adapter: adapter({
      pages: 'build',
      assets: 'build',
      fallback: '404.html',  // or 'index.html' for SPA
      precompress: true
    }),
    prerender: {
      entries: ['*']
    }
  }
};
```

### Deploy Anywhere
The `build/` directory can be deployed to any static host:
- GitHub Pages
- Cloudflare Pages
- Netlify
- AWS S3 + CloudFront
- Any web server

---

## CI/CD with GitHub Actions

### Vercel (via GitHub integration) — Recommended
No GitHub Action needed—Vercel auto-deploys on push when connected:
- **Push to `main`** → Production deployment
- **Push to `dev`** → Preview at `[project]-git-dev-[team].vercel.app`
- **Push to any branch** → Preview at `[project]-git-[branch]-[team].vercel.app`

This is the recommended approach. GitHub Actions are only needed for custom CI steps (tests, linting, etc.).

### Manual Deployment Action

`.github/workflows/deploy.yml`:
```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
          cache: 'npm'
      
      - run: npm ci
      - run: npm run build
      - run: npm run test
      
      # Add deployment step based on target
      # Example for Cloudflare Pages:
      - name: Deploy to Cloudflare
        uses: cloudflare/pages-action@v1
        with:
          apiToken: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          accountId: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
          projectName: your-project
          directory: .svelte-kit/cloudflare
```
