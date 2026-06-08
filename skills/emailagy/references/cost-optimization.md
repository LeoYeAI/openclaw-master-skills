# Técnicas de Reducción de Costos

## Batch size — el multiplicador más importante

| Batch | Llamadas/100 correos | Costo relativo |
|---|---|---|
| 1  | 100 | 100% |
| 10 | 10  | 22% |
| 20 | 5   | 15% |

Regla: esperar mínimo 10 correos antes de llamar a la IA.
Buffer: máx 2 minutos de espera para completar el batch.

## Prompt system caching

El system prompt de análisis es siempre el mismo (~300 tokens).
No incluir fecha/hora en el system prompt — invalida el caché.
Anthropic cobra 3.75x más por cache-write vs cache-read.

## Deduplicación por subject normalizado

```python
def normalizar(s):
    s = re.sub(r'^(Re:|Fwd:|RV:)\s*', '', s, flags=re.I)
    s = re.sub(r'\b\d{4,}\b', 'NUM', s)   # números de factura/ticket
    return s.lower().strip()
# Si el subject normalizado ya fue analizado esta semana → reutilizar
```

## Análisis tiered

```
Nivel 0 — Reglas locales ($0.00)         → 60-70% de correos
Nivel 1 — Haiku: from+subject+100chars   → 20-25% de correos
Nivel 2 — Haiku: body[:400]              → correos importantes del N1
Nivel 3 — Sonnet: thread completo        → borradores prio >= 8 únicamente
```

## Cache-TTL heartbeat (55 min)

Anthropic cache TTL = 60 minutos.
Heartbeat cada 55 min = caché siempre caliente = paga cache-read.
Silencio > 60 min = siguiente mensaje paga cache-write (3.75x más caro).

## Modo emergencia (> 95% del presupuesto)

Disponible sin IA: gog para leer/buscar, reglas locales para clasificar,
sqlite para informes, borradores existentes para ver (no generar).
El usuario mantiene 70% de funcionalidad a costo $0.00.

## Proyección de ahorro acumulado

```
Mes 1: $0.50/mes  (0 reglas)
Mes 3: $0.18/mes  (25 reglas aprendidas)
Mes 6: $0.10/mes  (60+ reglas)
```
Cada regla aprendida elimina permanentemente ese costo futuro.
