---
name: smart-email-agent
description: "Inyecta estado de presupuesto, modo activo y learnings pendientes al inicio de sesión"
metadata:
  openclaw:
    emoji: "🧠📬"
    events: ["agent:bootstrap"]
---

# Smart Email Agent — Hook de Bootstrap

Inyecta al inicio de cada sesión:
1. Estado del presupuesto mensual y modo activo (Normal/Ahorro/Emergencia)
2. Modelo permitido según nivel de gasto
3. Learnings pendientes de aplicar

## Habilitar
```bash
openclaw hooks enable smart-email-agent
```
## Setup inicial
```bash
python3 ~/.openclaw/skills/smart-email-agent/scripts/init_orchestrator.py
```
