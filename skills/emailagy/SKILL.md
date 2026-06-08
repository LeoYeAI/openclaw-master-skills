---
name: smart-email-agent
version: "3.0.0"
description: >
  All-in-one Gmail agent for OpenClaw. Fuses email-reader, email-organizer,
  email-analyzer, email-responder, email-scheduler, and email-reporter into a
  single skill with token-optimizer integration and a self-improvement engine.
  Use this skill for ANYTHING email-related: checking inbox, searching messages,
  organizing labels, classifying/prioritizing, drafting replies, scheduling
  automation, generating reports, or reviewing costs. Triggers on: correo,
  email, inbox, bandeja, spam, draft, borrador, responder, organizar, etiquetar,
  archivar, informe, estadísticas, notificame, automatiza, revisar mensajes,
  prioriza, cuanto cuesta, presupuesto, mejora el agente.
  Requires: gog CLI (primary) or Gmail API Python scripts (fallback).
tags: [email, gmail, gog, inbox, spam, organizer, analyzer, responder, scheduler, reporter, cost, optimization, self-improvement, openclaw]
metadata:
  openclaw:
    emoji: "🧠📬"
    requires:
      bins: [gog]
      env:
        - name: GOG_ACCOUNT
          description: "Dirección Gmail (ej: tu@gmail.com)"
        - name: ANTHROPIC_API_KEY
          description: "Para análisis y borradores con IA"
        - name: EMAIL_BUDGET_USD
          description: "Presupuesto mensual en USD (default: 1.00)"
      env_optional:
        - name: GMAIL_CREDENTIALS_PATH
          description: "Fallback: ruta a credentials.json de Gmail API"
        - name: NOTIFY_CHANNEL
          description: "Canal de notificaciones (telegram/slack/whatsapp)"
        - name: SAFE_BROWSING_API_KEY
          description: "Detección de phishing con Google Safe Browsing"
---

# Smart Email Agent v3 — Gmail All-in-One

Un solo skill que reemplaza los 6 skills del pack original.
Punto de entrada único para toda la gestión de correo.

> **Lazy loading activo:** este skill se carga completo (~500 tokens).
> NO cargues los 6 skills individuales — sería 4.800 tokens desperdiciados.

---

## PARTE 1 — LEER CORREOS (email-reader)

### Herramienta principal: `gog` CLI

```bash
# Verificar prerequisitos
which gog || echo "Instalar: npm i -g gogcli  OR  brew install gogcli"
echo $GOG_ACCOUNT  # debe estar configurado

# Autenticar si es la primera vez
gog auth add $GOG_ACCOUNT
```

### Comandos esenciales

```bash
# No leídos en inbox (acción por defecto cuando el usuario dice "revisa mi correo")
gog gmail search 'in:inbox is:unread' --max 5 --format minimal --json

# Buscar por criterio — usar sintaxis Gmail
gog gmail search 'from:juan@empresa.com newer_than:3d' --max 10 --format minimal --json
gog gmail search 'subject:factura has:attachment' --max 10 --format minimal --json
gog gmail search 'in:spam is:unread' --max 20 --format minimal --json

# Leer correo completo
gog gmail get <message_id> --format full --json

# Leer hilo completo
gog gmail thread <thread_id> --format minimal --json
```

### Operadores de búsqueda Gmail

`from:` `to:` `subject:` `label:` `is:unread` `is:starred`
`has:attachment` `newer_than:Nd` `older_than:Nd`
`in:inbox` `in:sent` `in:spam` `in:trash` `filename:ext`

### Flujo estándar de lectura

1. Verificar `gog` en PATH y `GOG_ACCOUNT` configurado
2. Construir query desde la intención del usuario (preguntar si es ambiguo)
3. Ejecutar con `--format minimal --json --max N`
4. Parsear JSON → presentar lista formateada:

```
📬 5 correos no leídos:
1. De: Juan García <juan@empresa.com> | Asunto: Propuesta Q2 | Hace 2h
   Vista previa: Hola, te mando el resumen de... | ID: msg_abc123
```

5. Ofrecer: leer completo / buscar más / actuar sobre el mensaje

### Reglas de lectura

- SIEMPRE usar `--format minimal --json --max N` (N=5 por defecto)
- Nunca mostrar JSON crudo; nunca leer contenido completo sin pedirlo
- Preservar IDs para acciones de seguimiento
- Sin resultados → confirmar criterios, sugerir términos más amplios
- Solo lectura — enviar/responder requiere la sección RESPONDER (Parte 4)
- No guardar contenido de correos en MEMORY.md salvo que el usuario lo pida

### Errores comunes

| Error | Causa | Solución |
|---|---|---|
| `gog: command not found` | gog no instalado | `npm i -g gogcli` o `brew install gogcli` |
| `GOG_ACCOUNT not set` | Variable no configurada | Pedir al usuario su email Gmail |
| Token expirado | OAuth vencido | `gog auth add <email>` |
| API error 429 | Rate limit | Esperar 60s, reintentar con backoff |

---

## PARTE 2 — ORGANIZAR (email-organizer)

### Jerarquía corporativa Corp/ (azul)

```
Corp/
├── Interno/
│   ├── Management      ← Gerencia, Directores
│   ├── Tech & Ops      ← Desarrollo, Soporte, Operaciones
│   ├── Commercial      ← Ventas, Marketing
│   ├── Admin & HR      ← Jurídica, RRHH, Contabilidad
│   └── Team            ← Resto del equipo @empresa.com
├── Partners & Clientes/
│   └── [empresa]       ← Wolkvox, Masiv, Unisanitas, Nuva, etc.
├── Proveedores/
│   └── [proveedor]     ← Google, Microsoft, AWS, etc.
└── Sistema/
    ├── DMARC
    ├── Notificaciones
    ├── Alertas
    └── No-Reply
```

### Comandos de organización con gog

```bash
# Crear etiqueta
gog gmail label create "Corp/Interno/Tech & Ops"

# Aplicar etiqueta a mensaje
gog gmail label apply <message_id> "Corp/Interno/Management"

# Mover correo (quitar INBOX + aplicar etiqueta)
gog gmail modify <message_id> --add-label "Corp/Partners & Clientes/Wolkvox" --remove-label INBOX

# Archivar (quitar INBOX sin borrar)
gog gmail modify <message_id> --remove-label INBOX

# Mover a spam
gog gmail modify <message_id> --add-label SPAM --remove-label INBOX

# Mover a papelera
gog gmail trash <message_id>

# Operación batch (múltiples IDs)
gog gmail batch-modify --ids id1,id2,id3 --add-label "Corp/Sistema/No-Reply" --remove-label INBOX
```

### Reglas de routing automático

Antes de llamar a la IA, aplicar estas reglas sin costo:

```
from_domain @empresa.com + from_name contiene [Linda, Rafael, Director] → Corp/Interno/Management
from_domain @empresa.com + from_name contiene [Tech, Dev, Soporte]      → Corp/Interno/Tech & Ops
from_domain @empresa.com                                                  → Corp/Interno/Team
from contiene noreply / no-reply / donotreply                            → Corp/Sistema/No-Reply
subject contiene DMARC / SPF / DKIM                                      → Corp/Sistema/DMARC
subject contiene alerta / alert / warning                                → Corp/Sistema/Alertas
```

Guardar y mantener estas reglas en `corp_routing_rules.json`.

### Protocolo de confirmación

NUNCA ejecutar acciones destructivas sin confirmación explícita:

```
⚠️ Pendiente de confirmación:
   → Mover 22 correos a Corp/Sistema/No-Reply
   → Eliminar etiqueta "noreply" (ya vacía)
   Esto NO borra correos, solo reorganiza etiquetas.
   ¿Confirmas? (sí/no)
```

---

## PARTE 3 — ANALIZAR Y CLASIFICAR (email-analyzer)

### Decisión de modelo ANTES de analizar

```
¿Tarea es clasificar / detectar spam / routing?
  → claude-haiku-4-5-20251001   (batch de 10-20 correos, ~$0.00009/correo)

¿Tarea es extraer tareas y fechas de correos importantes?
  → claude-haiku-4-5-20251001   (body[:800], ~$0.00015/correo)

¿El presupuesto está > 80% gastado?
  → forzar haiku para TODO, sin borradores automáticos

¿El presupuesto está > 95% gastado?
  → cero llamadas IA, solo reglas locales
```

**Opus: PROHIBIDO para tareas de email.**
**Sonnet: solo para borradores (ver Parte 4).**

### Pipeline de reducción de tokens (aplicar siempre)

```python
# 1. Pre-filtro sin IA (resolver antes de gastar tokens)
#    - Dominio en corp_routing_rules.json → etiquetar directo
#    - from en known_spam_domains.txt → spam directo
#    - message_id ya en analysis_cache → reutilizar resultado
#    Objetivo: resolver 60-70% a costo $0.00

# 2. Recortar campos al mínimo necesario
CAMPOS = {
    'clasificacion': ['from', 'subject', 'snippet[:100]'],   # ~30 tokens
    'prioridad':     ['from', 'subject', 'body[:400]'],      # ~150 tokens
    'tareas_fechas': ['from', 'subject', 'body[:800]'],      # ~250 tokens
}

# 3. Limpiar texto
def limpiar(texto, limite):
    texto = re.sub(r'<[^>]+>', '', texto)             # quitar HTML
    texto = re.sub(r'https?://\S+', '[URL]', texto)   # comprimir URLs
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto[:limite]

# 4. Batch: NUNCA menos de 10 correos por llamada
#    Esperar hasta tener 10-20 correos pendientes
BATCH_MIN = 10
BATCH_MAX = 20
```

### Prompt de análisis en batch (Haiku)

```
SYSTEM (idéntico siempre — para prompt caching):
Eres un clasificador de correos corporativos.
Analiza cada correo y devuelve SOLO JSON array. Sin texto extra.
Para cada ítem: {"idx":N,"corp_label":"...","categoria":"spam|importante|informativo|sistema|otro",
"prioridad":0-10,"es_spam":bool,"necesita_respuesta":bool,
"tiene_phishing":bool,"tareas":[],"fecha_limite":"ISO o null","razon":"máx 10 palabras"}

USER: Analiza: [JSON array de hasta 20 correos con from+subject+snippet[:100]]
```

### Presentación de resultados

```
🤖 Análisis — 47 correos procesados
⚡ Sin IA (pre-filtro): 31  (66%) → $0.000
🧠 Con Haiku (2 batches): 16     → $0.006

📊 Resultado:
  🔵 Corp/Interno/Management:   2  (prioridad alta)
  🔵 Corp/Partners & Clientes:  8
  🔵 Corp/Sistema/No-Reply:    14
  🗑️  Spam:                    12
  ⚠️  Phishing detectado:        1  → ALERTA
  📋 Con tareas pendientes:      4

Críticos:
  [10/10] linda@empresa.com — "Aprobación contrato urgente"
          Tarea: confirmar antes del viernes
```

---

## PARTE 4 — RESPONDER Y REDACTAR (email-responder)

### Cuándo usar Sonnet vs Haiku para borradores

```
Prioridad >= 8 → claude-sonnet-4-6       (calidad importa)
Prioridad 5-7  → claude-haiku-4-5-20251001  (suficiente, más barato)
Prioridad < 5  → NO generar borrador automático
```

Máximo 3 borradores por sesión cuando presupuesto < 60%.
Máximo 1 borrador por sesión cuando presupuesto 60-80%.
Cero borradores automáticos cuando presupuesto > 80%.

### Flujo de respuesta

```bash
# 1. Leer el hilo completo
gog gmail thread <thread_id> --format minimal --json

# 2. Preparar contexto recortado para la IA
#    Solo: from + subject + body[:600] del último mensaje + resumen del hilo anterior
```

### Prompt de generación de borrador

```
Redacta una respuesta profesional y concisa (máx 150 palabras).
Solo el cuerpo del mensaje, sin asunto ni encabezados.
Tono: profesional pero cercano.
Firma: [NOMBRE_USUARIO]

Hilo: [RESUMEN + ÚLTIMO MENSAJE RECORTADO]
```

### Presentar borrador al usuario

```
✍️ Borrador para: juan@empresa.com
   Re: Propuesta Q2 2026
────────────────────────
Hola Juan,

Gracias por el resumen. Me parece viable la dirección propuesta.
¿Podemos agendar una llamada esta semana?

Saludos,
[Tu nombre]
────────────────────────
[1] Guardar borrador   [2] Editar   [3] Enviar ahora   [4] Descartar
```

### Enviar con gog

```bash
# Guardar como borrador
gog gmail draft create --to "juan@empresa.com" \
  --subject "Re: Propuesta Q2 2026" \
  --body "Hola Juan,..." \
  --reply-to <message_id>

# Enviar borrador guardado
gog gmail draft send <draft_id>

# Enviar directamente (SIEMPRE pedir confirmación antes)
gog gmail send --to "juan@empresa.com" --subject "..." --body "..."
```

### Templates de respuesta rápida

```
acuse_recibo:      "Recibido, te respondo a la brevedad."
confirmar_reunion: "Confirmado para [fecha/hora]. Hasta entonces."
solicitar_info:    "Necesito más información sobre X para proceder."
ausencia:          "Estoy fuera hasta [fecha]. Respondo a mi regreso."
```

### Follow-ups automáticos

```bash
# Buscar correos enviados sin respuesta en últimos 5 días
gog gmail search 'in:sent newer_than:5d' --max 20 --format minimal --json
# Cruzar con INBOX para detectar cuáles no tienen respuesta
```

---

## PARTE 5 — AUTOMATIZAR (email-scheduler)

### Heartbeat optimizado: 55 minutos

**Por qué 55 min:** el caché de Anthropic expira a los 60 minutos.
Con heartbeat de 55 min, el agente mantiene el caché caliente → cada
mensaje paga cache-read en lugar de cache-write (3.75x más barato).

```json
// ~/.openclaw/openclaw.json
{
  "agents": {
    "email-assistant": {
      "heartbeat": { "every": "55m" },
      "model": "anthropic/claude-haiku-4-5-20251001"
    }
  }
}
```

### Cron jobs recomendados

```json
{
  "cron": {
    "jobs": [
      {
        "id": "email-priority-check",
        "schedule": "*/55 * * * *",
        "description": "Revisar correos importantes — modelo Haiku",
        "message": "Revisa inbox no leídos. Si hay prioridad >= 8, notifícame.",
        "model": "anthropic/claude-haiku-4-5-20251001",
        "enabled": true
      },
      {
        "id": "email-spam-cleanup",
        "schedule": "0 8 * * *",
        "description": "Limpieza diaria de spam — solo reglas locales, costo $0",
        "message": "Aplica reglas locales de spam. Sin llamadas IA.",
        "model": "anthropic/claude-haiku-4-5-20251001",
        "enabled": true
      },
      {
        "id": "email-weekly-report",
        "schedule": "0 9 * * MON",
        "description": "Informe semanal",
        "message": "Genera informe semanal de correos con email-reporter.",
        "model": "anthropic/claude-haiku-4-5-20251001",
        "enabled": true
      }
    ]
  }
}
```

**Regla de oro para crons:** SIEMPRE especificar `claude-haiku-4-5-20251001`.
Usar Opus para un cron de 10 tareas/día = $17.70/mes extra innecesario.

### HEARTBEAT.md de correo

```markdown
## Email Heartbeat — Modelo: claude-haiku-4-5-20251001

### Check de correos (cada 55 min)
1. gog gmail search 'in:inbox is:unread' --max 10 --format minimal --json
2. Aplicar reglas locales de corp_routing_rules.json
3. Si hay correo con keywords urgente/crítico/emergencia → notificar
4. Si no hay urgentes → HEARTBEAT_OK (silencio)

### Check de spam (cada 2h, sin IA)
1. gog gmail search 'in:spam is:unread' --max 50 --format minimal --json
2. Aplicar known_spam_domains.txt → mover a trash directo
3. Sin llamadas a IA

Quiet hours: 23:00–07:00 → HEARTBEAT_OK automático
```

### Gmail Push Notifications (tiempo real)

```bash
# Configurar webhook Pub/Sub
python3 scripts/setup_pubsub.py --topic "email-agent-notifications"

# El webhook dispara cuando llega un correo nuevo:
openclaw message "Nuevo correo. Revisa con gog y notifícame si es importante."
```

### Activar automatización completa

```
Usuario: "Activa el agente de correo en modo automático"
Agente:
  1. Verificar: gog auth status
  2. Crear cron jobs recomendados (ver arriba)
  3. Copiar HEARTBEAT.md al workspace
  4. Preguntar: ¿activar Gmail Push para tiempo real?
  5. Confirmar canal de notificaciones (NOTIFY_CHANNEL)
  6. "✅ Agente activado. Reviso cada 55 min. Te aviso si hay algo importante."
```

---

## PARTE 6 — INFORMES Y ESTADÍSTICAS (email-reporter)

### Tipos de informe

```bash
# Resumen del día (al final de sesión — SIEMPRE mostrar)
# Ver sección "Resumen de costos" más abajo

# Estadísticas de spam
gog gmail search 'in:trash newer_than:30d' --max 100 --format minimal --json
# Parsear y agrupar por dominio remitente

# Tareas pendientes en correos
# Consultar analysis_cache donde tareas[] no está vacío y sin respuesta

# Log de prompts IA detectados
cat .learnings/PROMPTS_DETECTADOS.md

# Historial de acciones del agente
cat email_audit.log | tail -50

# Deshacer última acción
gog gmail modify <ids_from_audit_log> --remove-label TRASH --add-label INBOX
```

### Resumen de costos — mostrar al cerrar cada sesión

```
💰 Sesión de hoy
  Correos procesados:    47
  ├─ Sin IA (reglas):    31  (66%) → $0.000
  ├─ Haiku (2 batches):  14       → $0.005
  └─ Sonnet (borradores): 2       → $0.005

  Tokens consumidos: 5.090
  Costo sesión:     $0.010
  Ahorro estimado:  $0.040 (80% vs. sin optimizar)

  Presupuesto mes:  $X.XX gastado / $Y.YY total (N%)
  Proyección mes:   $Z.ZZ
```

---

## PARTE 7 — MOTOR DE AUTO-MEJORA

### Cuándo capturar un aprendizaje

| Evento | Archivo | ID |
|---|---|---|
| Usuario corrige clasificación | `.learnings/LEARNINGS.md` | `LRN-YYYYMMDD-NNN` |
| Costo sesión > 2x el promedio | `.learnings/LEARNINGS.md` | `LRN-YYYYMMDD-NNN` |
| Error de API (rate limit, auth) | `.learnings/ERRORS.md` | `ERR-YYYYMMDD-XXX` |
| Optimización reduce costos >10% | `.learnings/LEARNINGS.md` | `LRN-YYYYMMDD-NNN` |
| Remitente recurrente sin regla | `.learnings/LEARNINGS.md` | `LRN-YYYYMMDD-NNN` |

### Formato

```markdown
## [LRN-YYYYMMDD-NNN] <tipo>
**Logged**: ISO timestamp
**Priority**: low | medium | high
**Status**: pending | applied | promoted
**Area**: cost | classification | routing | api | spam | drafts

### Summary
Una línea con el aprendizaje y su impacto.

### Details
Qué pasó. Qué se asumía vs. qué era verdad.

### Action
Cambio concreto: qué archivo editar, qué valor cambiar.

### Impact
Ahorro estimado: $X/mes | Tokens -N%
---
```

### Ciclo al cerrar sesión

```
1. Revisar .learnings/ con Status=pending
2. ¿Learnings con Impact > $0.01/mes?
   → Proponer: "Aprendí que X. ¿Lo aplico a las reglas?"
   → Si acepta → editar corp_routing_rules.json → Status=applied
3. ¿3+ learnings del mismo dominio/patrón?
   → Promover a regla permanente sin preguntar
   → Status=promoted
4. Reportar: "Apliqué N mejoras. Ahorro estimado: $X/mes"
```

### Efecto compuesto del aprendizaje

```
Mes 1: ~$0.50/mes  (0 reglas)
Mes 2: ~$0.30/mes  (10 reglas aprendidas)
Mes 3: ~$0.18/mes  (25 reglas)
Mes 6: ~$0.10/mes  (60+ reglas)
```

---

## PARTE 8 — CONTROL DE PRESUPUESTO

### Cuatro modos operativos

| % gastado | Modo | Restricciones |
|---|---|---|
| 0–59% | Normal ✅ | Todo habilitado |
| 60–79% | Ahorro leve 🟡 | Avisar. Máx 2 borradores/sesión |
| 80–94% | Ahorro fuerte 🟠 | Solo Haiku. Sin borradores auto. Batch obligatorio ≥20 |
| 95–100% | Emergencia 🔴 | Cero IA. Solo `gog` + reglas locales |

### Diagnósticos con token-optimizer (si está instalado)

```bash
/context list    # qué archivos consumen tokens ahora
/usage full      # tokens + costo por respuesta
/usage cost      # resumen acumulado de sesión
/status          # modelo activo, % contexto

python3 scripts/token_tracker.py check   # estado del budget diario
python3 scripts/model_router.py "analizar correos nuevos"  # qué modelo usar
```

---

## Referencias — leer cuando necesites más detalle

- `references/cost-optimization.md` — Técnicas avanzadas: prompt caching, deduplicación semántica, modo emergencia
- `references/learning-patterns.md` — Patrones de auto-mejora y ciclo de vida de learnings
- `hooks/openclaw-handler.js` — Inyecta estado de presupuesto + modo activo al inicio de sesión
- `scripts/init_orchestrator.py` — Setup inicial: verifica gog, crea budget_tracker, SKILLS_INDEX
- `assets/HEARTBEAT.email.md` — Plantilla lista para copiar al workspace
