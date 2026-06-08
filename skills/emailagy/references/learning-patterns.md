# Patrones de Auto-Mejora

## Patrones que eliminan costo IA

**Remitente siempre ignorado** (3+ veces archivado sin leer)
→ Añadir a known_ignore_senders.txt. Auto-archivo, skip IA.

**Dominio corporativo nuevo** (2+ correos clasificados igual)
→ Añadir a corp_routing_rules.json. Routing directo, skip IA.

**Newsletter recurrente** (mismo from + subject normalizado)
→ Marcar leído + archivar automáticamente, sin IA.

## Patrones de costo

**Batches pequeños** (avg < 10 correos/llamada)
→ Activar buffer de 2 min. Ahorro: 60% en llamadas IA.

**Re-análisis de correos ya procesados**
→ Verificar analysis_cache ANTES de llamar a la IA. Ahorro: 100% de re-análisis.

**Rate limit 429 a hora fija** (ej: 9:00-9:30am)
→ Retrasar batch a 9:45am. Backoff: 30s → 60s → 120s.

## Cuándo NO registrar un learning

- Error de red único no repetido
- Clasificación correcta (solo capturar errores)
- Learning idéntico existe en los últimos 7 días
- Impacto estimado < $0.001/mes

## Ciclo de vida

```
pending → (usuario aprueba OR patrón 3x) → applied
applied → (funciona 2+ semanas)          → promoted → archivado
```

Los learnings promoted no aparecen en el resumen de sesión.
Solo visibles cuando el usuario pide el historial completo de mejoras.
