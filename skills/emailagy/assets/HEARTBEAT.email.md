# Email Heartbeat — Smart Email Agent v3
# Intervalo: 55 minutos (cache-TTL alignment)
# Modelo: SIEMPRE claude-haiku-4-5-20251001

## Check 1 — Correos importantes (cada 55 min)
gog gmail search 'in:inbox is:unread' --max 10 --format minimal --json
→ Aplicar reglas de corp_routing_rules.json (sin IA)
→ Si hay keywords urgente/crítico/emergencia en subject → notificar
→ Si no → HEARTBEAT_OK (silencio total)

## Check 2 — Spam (cada 2h, costo $0.00)
gog gmail search 'in:spam is:unread' --max 50 --format minimal --json
→ Aplicar known_spam_domains.txt → trash directo
→ Sin llamadas IA

## Check 3 — Reporte diario (8am)
→ email-reporter --period day con Haiku
→ Incluir resumen de costos del día

Quiet hours: 23:00–07:00 → HEARTBEAT_OK automático
