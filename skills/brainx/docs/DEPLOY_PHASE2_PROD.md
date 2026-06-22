# BrainX V5 Phase 2 - Runbook de despliegue a producción

Este runbook aplica **PII scrub + semantic dedupe + lifecycle automation + eval harness** en producción.

## 0) Pre-checks

- Branch: `feat/brainx-v5-core-without-fallback`
- Commit esperado (fase 2): `91c6a79`
- DB con pgvector activa
- Backup disponible antes de migrar

## 1) Backup (obligatorio)

```bash
cd /home/clawd/.openclaw/skills/brainx-v5
./scripts/backup-brainx.sh
```

Guardar el path del `.sql.gz` generado para rollback.

## 2) Migración SQL (idempotente)

```bash
cd /home/clawd/.openclaw/skills/brainx-v5
psql "$DATABASE_URL" -f sql/migrations/2026-02-24_phase2_governance.sql
```

## 3) Smoke checks DB

```bash
psql "$DATABASE_URL" -c "\d+ brainx_memories"
psql "$DATABASE_URL" -c "\d+ brainx_patterns"
psql "$DATABASE_URL" -c "\d+ brainx_query_log"
```

Checks mínimos:
- `brainx_memories` tiene columnas: `status`, `category`, `pattern_key`, `recurrence_count`, `first_seen`, `last_seen`, `resolved_at`.
- existen tablas `brainx_patterns` y `brainx_query_log`.

## 4) Deploy de código

Desplegar commit con fase 2 (`91c6a79`) en la instancia BrainX activa.

## 5) Config recomendada (env)

```bash
BRAINX_PII_SCRUB_ENABLED=true
BRAINX_PII_SCRUB_REPLACEMENT=[REDACTED]
BRAINX_DEDUPE_SIM_THRESHOLD=0.92
BRAINX_DEDUPE_RECENT_DAYS=30

BRAINX_LIFECYCLE_PROMOTE_MIN_RECURRENCE=3
BRAINX_LIFECYCLE_PROMOTE_DAYS=30
BRAINX_LIFECYCLE_DEGRADE_DAYS=45
BRAINX_LIFECYCLE_LOW_IMPORTANCE_MAX=3
BRAINX_LIFECYCLE_LOW_ACCESS_MAX=1
```

## 6) Smoke funcional (CLI)

```bash
./brainx-v5 health
./brainx-v5 add --type learning --content "Contacto: test@example.com" --context prod-test --category learning --tags pii
./brainx-v5 search --query "contacto" --limit 3
./brainx-v5 metrics --days 7 --json
./brainx-v5 lifecycle-run --dryRun --json
```

Esperado:
- `add` devuelve ok
- contenido sensible redactado si aplica
- `metrics` devuelve estructura JSON con `query_performance`

## 7) Eval de calidad offline (opcional recomendado)

```bash
npm run eval:memory-quality -- --json
```

## 8) Rollback plan

### A) Rollback código
Volver al commit previo (ej: `9f58809`) y redeploy.

### B) Rollback datos
Si hace falta revertir datos completos:
```bash
./scripts/restore-brainx.sh <backup-file.sql.gz>
```

> Nota: evitar drop de columnas en caliente. Preferir rollback por restore de snapshot.

## 9) Criterio de éxito

- 0 errores en `health`
- migración aplicada sin fallos
- `metrics` y `lifecycle-run --dryRun` operativos
- sin incremento anómalo de latencia en `search/inject`
