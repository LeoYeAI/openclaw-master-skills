# Cómo Funciona BrainX V5

BrainX es el sistema de memoria persistente de OpenClaw. Usa PostgreSQL + pgvector + OpenAI embeddings para que los agentes recuerden entre sesiones, aprendan de conversaciones pasadas, y compartan conocimiento entre sí — todo automático, sin intervención humana.

---

## 1. Ciclo de Vida de una Memoria

```
Conversación / Archivo .md
        │
        ▼
   ┌─────────┐     ┌──────────┐     ┌──────────┐     ┌───────────┐
   │ Captura  │ ──► │ Embedding│ ──► │ Storage  │ ──► │ Inyección │
   │          │     │ (OpenAI) │     │ (Postgres│     │ (bootstrap│
   │ Scripts  │     │ 1536-dim │     │ +pgvector│     │  de cada  │
   │ o manual │     │ coseno   │     │  )       │     │  agente)  │
   └─────────┘     └──────────┘     └──────────┘     └───────────┘
                                          │
                                          ▼
                                   ┌──────────────┐
                                   │ Curación     │
                                   │ (dedup,      │
                                   │  lifecycle,  │
                                   │  quality)    │
                                   └──────────────┘
```

### Paso a paso:

1. **Captura**: un script extrae información de sesiones de agentes o archivos markdown.
2. **Embedding**: el texto se convierte en un vector de 1536 dimensiones vía `text-embedding-3-small` de OpenAI.
3. **Storage**: el vector + metadata (tipo, tier, importancia, agente, tags) se guarda en `brainx_memories` en PostgreSQL.
4. **Curación**: scripts automáticos deduplicar, puntúan calidad, promueven/degradan, y detectan contradicciones.
5. **Inyección**: cuando un agente inicia sesión, el hook selecciona las memorias más relevantes y las inyecta como contexto.

---

## 2. Tipos de Memoria

| Tipo | Para qué |
|---|---|
| `note` | Información general |
| `decision` | Decisiones tomadas (ej: "usar CDN Cloudflare") |
| `action` | Acciones ejecutadas |
| `learning` | Lecciones aprendidas (ej: "no usar innerHTML sin sanitizar") |
| `fact` | Datos duros extraídos (URLs, puertos, repos, configs) |
| `gotcha` | Trampas/bugs conocidos que otros agentes deben evitar |

### Tiers (prioridad):

| Tier | Significado | Comportamiento |
|---|---|---|
| `hot` | Alta prioridad, acceso frecuente | Se inyecta siempre en bootstrap |
| `warm` | Relevante pero no urgente | Se inyecta si pasa el umbral de importancia |
| `cold` | Baja prioridad / poco acceso | No se inyecta, pero sí aparece en búsquedas |
| `archive` | Histórico | Solo accesible por búsqueda explícita |

La importancia va de 1 a 10. Solo memorias con `importance >= 5` se inyectan por defecto.

---

## 3. Pipeline Automático (Crons)

Estos scripts corren automáticamente y mantienen BrainX vivo:

### Alimentación (captura de memorias nuevas)

| Cron | Script | Qué hace |
|---|---|---|
| Cada 3h (`:00`) | `memory-bridge.js` | Sincroniza archivos `memory/*.md` de cada workspace → vectores en DB |
| Cada 3h (`:30`) | `memory-distiller.js` | Lee session logs de OpenClaw, usa LLM (gpt-4.1-mini) para extraer memorias relevantes |
| Cada 6h (`:15`) | `pattern-detector.js` | Detecta patrones recurrentes en memorias y los registra |
| Cada 6h (`:30`) | `session-snapshot.js` | Captura estado de sesiones activas |

### Curación (mejora de calidad)

| Cron | Script | Qué hace |
|---|---|---|
| Diario 2am | `cross-agent-learning.js` | Propaga gotchas y learnings importantes a todos los agentes |
| Diario 3am | `learning-detail-extractor.js` | Extrae metadata adicional de memorias tipo learning |
| Diario 4am | `trajectory-recorder.js` | Registra paths problema→solución |

### Monitoreo

| Cron | Script | Qué hace |
|---|---|---|
| Cada 30min | `health-check.sh` | Verifica PostgreSQL + pgvector + conteo de memorias |
| Diario 8am | `ops-alerts.sh` | Alertas operacionales |
| Lunes 9am | `weekly-dashboard.sh` | Dashboard semanal de métricas |

### Scripts disponibles (ejecución manual)

| Script | Uso |
|---|---|
| `quality-scorer.js` | Evalúa y puntúa calidad de memorias |
| `dedup-supersede.js` | Elimina duplicados exactos por fingerprint |
| `contradiction-detector.js` | Encuentra memorias que se contradicen |
| `cleanup-low-signal.js` | Degrada memorias muy cortas o de baja señal |
| `context-pack-builder.js` | Genera paquetes de contexto semanales |
| `fact-extractor.js` | Extrae datos duros (URLs, puertos, etc.) con regex |

---

## 4. Inyección en Agentes (Bootstrap)

Cuando un agente inicia sesión, pasa esto:

```
Evento: agent:bootstrap
        │
        ▼
Hook: brainx-auto-inject/handler.js
        │
        ├── 1. Consulta PostgreSQL: top memorias hot+warm con importance >= 5
        │      • Hasta 8 memorias globales (team)
        │      • Hasta 5 memorias propias del agente
        │
        ├── 2. Genera BRAINX_CONTEXT.md en el workspace del agente
        │      (archivo completo con todas las memorias formateadas)
        │
        └── 3. Actualiza MEMORY.md del agente
               (inyecta bloque resumido entre markers BRAINX:START/END)
```

### Archivos generados:

- **`BRAINX_CONTEXT.md`**: contexto completo con memorias detalladas. El agente lo lee si necesita más detalle.
- **Bloque en `MEMORY.md`**: resumen compacto que se carga automáticamente en el system prompt del agente.

### Config actual (`openclaw.json`):

```json
{
  "hooks.internal.entries.brainx-auto-inject": {
    "enabled": true,
    "limit": 5,
    "tier": "hot+warm",
    "minImportance": 5
  }
}
```

---

## 5. Búsqueda y Ranking

Cuando un agente busca memorias (`brainx search` o `brainx inject`):

1. El query se convierte en embedding
2. PostgreSQL calcula similitud coseno contra todas las memorias
3. El score final combina:
   - **Similitud semántica** (base)
   - **Importancia** (+0 a +0.25 según importance/10)
   - **Tier boost**: hot +0.15, warm +0.05, cold -0.05, archive -0.10
4. Se filtran memorias supersedidas (`superseded_by IS NULL`)
5. Se actualiza `access_count` y `last_accessed` de cada resultado

---

## 6. Cross-Agent Learning

Corre diario a las 2am. Hace que el conocimiento fluya entre agentes:

1. Busca memorias tipo `gotcha` y `learning` con alta importancia
2. Las propaga a agentes que no las tienen
3. Respeta el contexto original (no inyecta info irrelevante)

Resultado: si un agente descubre que "innerHTML sin sanitizar causa XSS", todos los demás agentes lo saben en la siguiente sesión.

---

## 7. Estado Actual

### DB:
- **1173 memorias activas** (no supersedidas)
- **557 hot** / **582 warm** / **34 cold**
- **20 agentes** con memorias registradas
- Health checks pasando cada 30 min

### Tablas operativas:
| Tabla | Status |
|---|---|
| `brainx_memories` | ✅ Core, 1173+ registros |
| `brainx_query_log` | ✅ Tracking de queries |
| `brainx_pilot_log` | ✅ Tracking de auto-inject |
| `brainx_context_packs` | ✅ Paquetes de contexto |
| `brainx_patterns` | ✅ Detección de patrones |
| `brainx_session_snapshots` | ⚠️ Schema listo, script en cron |
| `brainx_learning_details` | ⚠️ Schema listo, script en cron |
| `brainx_trajectories` | ⚠️ Schema listo, script en cron |

---

## 8. Uso Rápido (CLI)

```bash
# Verificar salud
brainx health

# Guardar una memoria
brainx add --type decision --content "Usar Cloudflare CDN" --tier hot --importance 9

# Buscar
brainx search --query "CDN" --limit 5

# Obtener contexto para prompt
brainx inject --query "configuración de deploy" --limit 3

# Guardar un fact
brainx fact --content "Puerto nginx: 443" --context mdx-infra
```

---

## 9. Dónde Vive Todo

| Qué | Ruta |
|---|---|
| Skill completa | `~/.openclaw/skills/brainx-v5/` |
| CLI wrapper | `~/.openclaw/skills/brainx-v5/brainx` |
| Hook de inyección | `~/.openclaw/hooks/brainx-auto-inject/handler.js` |
| Config del hook | `openclaw.json → hooks.internal.entries.brainx-auto-inject` |
| Base de datos | PostgreSQL local (`127.0.0.1:5432/brainx_v5`) |
| Logs de cron | `~/.openclaw/skills/brainx-v5/cron/cron-output.log` |
| Schema SQL | `~/.openclaw/skills/brainx-v5/sql/` |
| Variables de entorno | `~/.openclaw/skills/brainx-v5/.env` |
| Docs detallados | `~/.openclaw/skills/brainx-v5/docs/` |
| README completo | `~/.openclaw/skills/brainx-v5/README.md` (107KB) |

---

_Última actualización: 2026-03-08_
