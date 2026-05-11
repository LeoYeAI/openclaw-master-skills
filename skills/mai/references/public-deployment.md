# Public Deployment Checklist

Mai's public registry includes application-level controls, but production deployment still needs infrastructure and compliance work outside the Python scripts.

## Included In This Package

- API-key authentication with salted hashes.
- Merchant, buyer, and admin authorization checks.
- Per-minute rate limiting by API key or IP.
- Deterministic product risk scoring.
- Admin moderation queue and approve/reject decisions.
- PSP-backed payment custody state machine with a development-only `demo` provider.
- Tests for unauthorized access, role checks, rate limiting, moderation, and payment release authorization.

## Required Before Live Public Launch

- TLS termination and HTTPS-only access.
- Secrets stored outside the registry JSON file.
- Rotatable keys and revocation UI/API.
- Durable database with backups instead of flat-file JSON.
- Structured audit logs retained according to policy.
- Monitoring, alerts, and abuse dashboards.
- Terms, privacy policy, merchant agreement, buyer dispute policy, and prohibited goods policy.
- KYC/KYB and tax handling where required.
- Licensed payment service provider integration for holds, transfers, refunds, chargebacks, and disputes.
- Manual moderation operations and escalation workflow.

## Docker Deployment

Build and run locally:

```bash
docker compose --env-file registry.example.env up --build
```

Create initial keys inside the running container:

```bash
docker compose exec mai-registry python3 scripts/mai_registry.py issue-key --data /data/mai-registry.json --token admin-token --role admin --subject ops-admin
docker compose exec mai-registry python3 scripts/mai_registry.py issue-key --data /data/mai-registry.json --token seller-token --role merchant --subject seller-a --merchant-id seller-a
docker compose exec mai-registry python3 scripts/mai_registry.py issue-key --data /data/mai-registry.json --token buyer-token --role buyer --subject alice --buyer-id alice
```

For public deployment, put the container behind an HTTPS reverse proxy or managed load balancer and restrict access to the registry data volume.

## Payment Boundary

The `demo` payment provider is only a development adapter. A live deployment must replace it with a licensed PSP integration. Mai should record PSP references, webhook evidence, release/refund decisions, and dispute history; Mai should not directly custody buyer funds.
