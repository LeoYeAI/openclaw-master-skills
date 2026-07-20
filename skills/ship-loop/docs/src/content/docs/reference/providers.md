---
title: Deploy Providers
description: Supported deployment verification providers
---

Ship Loop verifies deployments after pushing code. Each provider checks that the new code is actually live and serving correctly.

## Vercel

```yaml
deploy:
  provider: vercel
  routes: [/, /api/health]
  deploy_header: x-vercel-deployment-url
  timeout: 300
```

Vercel verification:
- Polls each route for HTTP 200
- Checks the `x-vercel-deployment-url` response header to confirm the new deployment is active
- Retries until timeout

## Netlify

```yaml
deploy:
  provider: netlify
  routes: [/, /about]
  timeout: 300
```

Netlify verification:
- Polls each route for HTTP 200
- Checks `x-nf-request-id` header to confirm Netlify is serving the response
- Retries until timeout

## Custom Script

```yaml
deploy:
  provider: custom
  script: ./scripts/verify-deploy.sh
  timeout: 300
```

For custom providers, Ship Loop runs your script with these environment variables:

| Variable | Description |
|----------|-------------|
| `SHIPLOOP_COMMIT` | The commit SHA that was just pushed |
| `SHIPLOOP_SITE` | The site URL from config |

Your script should exit 0 for success, non-zero for failure.

Example custom script:

```bash
#!/bin/bash
# verify-deploy.sh
set -e

echo "Waiting for deployment of $SHIPLOOP_COMMIT..."

for i in {1..30}; do
  response=$(curl -s "$SHIPLOOP_SITE/api/health")
  if echo "$response" | grep -q "$SHIPLOOP_COMMIT"; then
    echo "Deployment verified!"
    exit 0
  fi
  sleep 10
done

echo "Deployment not detected after 5 minutes"
exit 1
```

## Adding a New Provider

See the [Adding a Provider](/ship-loop/guides/adding-a-provider/) guide.

Ship Loop currently has open issues for these providers:
- [AWS Amplify](https://github.com/fernando-fernandez3/ship-loop/issues/1)
- [Cloudflare Pages](https://github.com/fernando-fernandez3/ship-loop/issues/2)
- [Railway](https://github.com/fernando-fernandez3/ship-loop/issues/3)
