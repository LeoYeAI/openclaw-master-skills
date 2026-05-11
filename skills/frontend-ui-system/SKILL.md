---
name: frontend_ui_system
description: Diseña e implementa interfaces de alta calidad para apps, sitios web y dashboards con enfoque tipo v0.dev: dirección visual clara, design system, jerarquía visual fuerte, componentes reutilizables, mobile-first, consistencia UI y revisión iterativa.
---

# Frontend UI System

## Propósito

Esta skill existe para que el agente diseñe e implemente interfaces de usuario con un nivel visual y estructural mucho más alto que una UI genérica.

El objetivo no es solo producir código funcional. El objetivo es producir una interfaz:

- limpia
- moderna
- coherente
- comercial
- usable
- visualmente jerárquica
- reusable a nivel de componentes
- lista para crecer como producto real

La referencia mental es trabajar más cerca del nivel de criterio de un product designer + frontend engineer, y no como un simple generador de JSX o HTML.

---

# Principio fundamental

**No escribir código hasta tener claridad visual suficiente.**

El diseño no es decoración.  
El diseño es estructura, jerarquía, intención, claridad y sistema.

Cada decisión visual debe tener una razón funcional.

---

# Meta principal

Cuando el usuario pida una app, una web, una landing, un dashboard, una pantalla o una mejora visual, esta skill debe ayudar a producir un resultado que:

- se vea mejor desde la primera iteración
- tenga mejor taste visual por defecto
- evite layouts genéricos o desordenados
- mantenga consistencia entre pantallas
- use un sistema visual claro
- implemente bien el frontend, no solo lo maquille

---

# Cuándo usar esta skill

Usa esta skill cuando el usuario pida cosas como:

- diseñar una app
- rediseñar una pantalla
- mejorar una UI
- hacer una landing page
- construir un dashboard
- crear una web moderna
- hacer una interfaz más premium
- refinar frontend
- hacer una app mobile-first
- mejorar UX/UI
- crear componentes visualmente consistentes
- transformar una interfaz básica en algo más moderno y comercial

También úsala cuando el usuario diga frases vagas como:

- “hazlo más moderno”
- “hazlo más premium”
- “hazlo más limpio”
- “se ve muy básico”
- “quiero que se vea profesional”
- “quiero que parezca producto real”
- “hazlo como una app seria”
- “quiero una UI bonita”

---

# Resultado esperado

Esta skill debe hacer que el agente:

1. piense antes de codificar  
2. proponga dirección visual  
3. documente un mini design system  
4. defina arquitectura de pantallas  
5. implemente con componentes reutilizables  
6. revise jerarquía visual, spacing y consistencia  
7. itere si el resultado sigue viéndose genérico o flojo

---

# FASE 0: diagnóstico inicial

Antes de diseñar o implementar, responder internamente estas preguntas:

## Preguntas base

1. ¿Qué tipo de producto es?
- App móvil
- Web app
- Landing page
- Dashboard
- E-commerce
- SaaS
- Plataforma interna
- Portal
- Sistema administrativo
- Sitio institucional

2. ¿Quién es el usuario objetivo?
- consumidores
- empresas
- profesionales
- jóvenes
- técnicos
- administradores
- clientes finales
- personal operativo

3. ¿Cuál es la acción principal del usuario?
- comprar
- reservar
- registrarse
- explorar
- consultar
- crear contenido
- subir información
- revisar métricas
- gestionar datos
- agendar
- confirmar una acción

4. ¿Qué personalidad debe transmitir el producto?
- premium
- confiable
- moderno
- amigable
- técnico
- corporativo
- juvenil
- sobrio
- innovador
- deportivo
- elegante

5. ¿Cuál es la prioridad del contexto?
- conversión
- claridad
- velocidad
- confianza
- facilidad de uso
- densidad de información
- exploración
- mobile-first
- desktop-first

## Regla
No pasar a implementación sin haber aclarado mentalmente estas cinco cosas.

---

# FASE 1: dirección visual

## Regla obligatoria
Siempre que no exista una dirección visual completamente definida, proponer **2 o 3 estilos visuales distintos** antes de implementar.

## Formato de propuesta visual

Para cada estilo, documentar:

**Estilo [Letra]: "[Nombre conceptual]"**

- Concepto: descripción de 1 línea
- Paleta: color primario + neutrales + acento
- Tipografía: familia y personalidad
- Personalidad: 3 adjetivos
- Fortaleza: por qué funcionaría bien
- Riesgo: qué podría salir mal si se exagera

## Ejemplo de estructura

**Estilo A: "Corporate Trust"**
- Concepto: profesional, serio y confiable
- Paleta: azul marino + grises + blanco + acento sobrio
- Tipografía: Inter
- Personalidad: confiable, corporativo, claro
- Fortaleza: transmite seguridad
- Riesgo: puede sentirse algo genérico

**Estilo B: "Modern Minimal"** ⭐ RECOMENDADO
- Concepto: limpio, contemporáneo y premium
- Paleta: negro suave + blanco + gris neutro + verde lima o azul sobrio
- Tipografía: Geist / Inter / Plus Jakarta Sans
- Personalidad: moderno, premium, tecnológico
- Fortaleza: elegante y muy adaptable
- Riesgo: si se exagera, puede verse vacío

**Estilo C: "Friendly Product"**
- Concepto: accesible y moderno
- Paleta: tonos amigables con neutrales limpios
- Tipografía: Plus Jakarta Sans / Manrope
- Personalidad: accesible, cálido, moderno
- Fortaleza: gran cercanía con el usuario
- Riesgo: puede perder seriedad en ciertos contextos

## Recomendación obligatoria
Marcar uno como **RECOMENDADO** y justificar por qué encaja mejor con el producto, el usuario y la acción principal.

---

# FASE 2: mini design system

Una vez elegida la dirección visual, documentar un mini sistema antes de codificar.

## 2.1 Tokens de color

Definir mínimo estos tokens:

| Token | Uso |
|---|---|
| `primary` | marca, CTA principal, foco |
| `primary-foreground` | texto sobre primary |
| `background` | fondo principal |
| `foreground` | texto principal |
| `card` | fondo de superficies |
| `card-foreground` | texto en cards |
| `muted` | fondos secundarios |
| `muted-foreground` | texto secundario |
| `accent` | badges, highlights, estados activos |
| `accent-foreground` | texto sobre accent |
| `border` | separadores y bordes |
| `destructive` | errores y acciones destructivas |
| `success` | confirmaciones si aplica |
| `warning` | alertas si aplica |

## Reglas de color

- Usar preferentemente **máximo 5 colores dominantes** en la experiencia.
- Tener 1 color primario claro.
- Usar 2 o 3 neutrales máximos.
- Mantener 1 o 2 acentos funcionales.
- Preferir colores sólidos frente a gradientes innecesarios.
- Usar nombres semánticos, no colores directos, cuando se implementen tokens.
- Verificar contraste suficiente.
- El acento debe ayudar a la jerarquía, no competir con todo.

## Evitar
- demasiados colores compitiendo
- acentos por todas partes
- gradientes sin propósito
- colores chillones en exceso
- usar muchos tonos sin sistema

---

## 2.2 Tipografía

Definir:

- familia principal
- pesos usados
- escala base
- line height
- rol de headings, body, caption, labels

## Reglas tipográficas

- Máximo 2 familias tipográficas.
- Tamaño mínimo recomendado para body: 14px.
- Headings con peso 600-700.
- Body con 400-500.
- Mantener line-height cómodo: 1.4 a 1.6.
- Limitar variedad de tamaños.
- La tipografía debe reforzar personalidad y legibilidad.

## Escala sugerida

- 14
- 16
- 18
- 20
- 24
- 30
- 36
- 48

No hace falta usar todos. Solo los necesarios.

---

## 2.3 Espaciado

Definir una unidad base y una escala consistente.

### Recomendación
Unidad base: 4px

Escala común:
- 4
- 8
- 12
- 16
- 20
- 24
- 32
- 40
- 48
- 64
- 80

## Reglas de spacing

- El whitespace es una de las herramientas más importantes.
- Mejor pecar por más aire que por saturación.
- El spacing debe marcar agrupación lógica.
- Elementos relacionados: gaps más cortos.
- Secciones distintas: gaps más amplios.
- Repetir la misma lógica de espaciado entre pantallas.

## Señal de mala UI
Si todo está muy junto, la UI se percibe barata o improvisada.

---

## 2.4 Border radius

Definir radios por nivel.

Sugerencia:
- XS: 6px
- SM: 8px
- MD: 12px
- LG: 16px
- XL: 20px o 24px
- Full: 9999px

## Regla
Usar radios consistentes según tipo de componente.  
No mezclar demasiados radios diferentes sin motivo.

---

## 2.5 Sombras y profundidad

Las sombras deben ser suaves y escasas.

### Niveles sugeridos
- ninguna
- suave
- media
- fuerte solo en casos muy puntuales

## Regla
Preferir una interfaz limpia con elevación moderada antes que una interfaz recargada.

## Evitar
- sombras muy oscuras
- muchas profundidades diferentes
- usar sombra para compensar mala jerarquía

---

# FASE 3: arquitectura de pantallas

Antes de codificar, documentar la estructura general.

## Tabla mínima

| Pantalla | Estructura | CTA principal | Componentes clave |
|---|---|---|---|
| Home | hero / resumen / accesos rápidos | acción principal | cards, hero, quick actions |
| Lista | filtros + listado | click/tap en item | filter bar, item card |
| Detalle | header + contenido + acción | CTA fija o visible | gallery, info, summary |
| Formulario | pasos + campos + submit | confirmar | field, summary, stepper |
| Perfil | datos + acciones + historial | editar/continuar | profile sections |

## Para cada pantalla definir

1. qué ve primero el usuario  
2. qué debe hacer  
3. qué estados necesita  
4. cómo navega desde y hacia ella  
5. qué componentes pueden reutilizarse

## Regla
No tratar pantallas como piezas aisladas.  
Pensar el flujo completo del producto.

---

# FASE 4: reglas visuales estrictas

Estas reglas buscan evitar resultados genéricos o visualmente flojos.

## 4.1 Jerarquía visual

Debe quedar claro:

- qué es lo principal
- qué es secundario
- qué es informativo
- cuál es la acción clave

## Reglas
- Un viewport no debe tener demasiados elementos compitiendo por atención.
- Debe existir un CTA primario claro.
- Los títulos deben diferenciarse claramente del body.
- La información secundaria debe sentirse secundaria.
- El uso del color debe reforzar la jerarquía.

---

## 4.2 Densidad visual

### Regla
Reducir ruido.  
Si hay duda entre agregar o quitar, normalmente conviene quitar.

## Buscar
- aire
- estructura
- ritmo
- bloques legibles
- agrupación lógica

## Evitar
- demasiados iconos
- demasiados badges
- textos compactos
- cards apretadas
- bordes y sombras en exceso
- microdetalles que distraen

---

## 4.3 Consistencia

### Regla crítica
Mismo componente = mismo comportamiento visual y estructural.

## Debe mantenerse consistente:
- radios
- padding interno
- estados
- estilo de botones
- estilo de inputs
- altura de componentes similares
- patrones de card
- chips y badges
- spacing entre bloques
- tono de iconografía

---

## 4.4 Mobile-first

### Proceso obligatorio
1. Pensar primero en 375px aprox.
2. Luego expandir a tablet y desktop.
3. Asegurar CTA claros en móvil.
4. Mantener touch targets cómodos.

## Reglas
- mínimo razonable de touch target: 44x44px
- formularios cómodos para móvil
- sticky bottom CTA si ayuda
- no confiar en hover como interacción principal

---

# FASE 5: reglas de implementación frontend

Esta skill no solo diseña. También debe ayudar a implementar bien.

## 5.1 Filosofía de implementación

Construir primero una base sólida de componentes y layout.  
No escribir una pantalla gigante llena de JSX repetido sin estructura.

## 5.2 Estructura recomendada

Separar cuando sea razonable en:
- `components/ui`
- `components/shared`
- `features/...`
- `pages` o `screens`
- `hooks`
- `lib`
- `types`

No es obligatorio usar exactamente esos nombres, pero sí mantener organización clara.

---

## 5.3 Reutilización

### Regla
Si un patrón se repite 2 o más veces, evaluar extraer componente.

### Extraer especialmente:
- botones
- cards
- headers de sección
- list items
- inputs
- filtros
- barras de acción
- resúmenes
- skeletons
- empty states

---

## 5.4 Props y variantes

Cuando haya componentes reutilizables, preferir variantes claras:
- `variant`
- `size`
- `state`
- `tone`

Ejemplos:
- `variant="default|outline|ghost"`
- `size="sm|md|lg"`

## Regla
No duplicar un mismo componente con diferencias mínimas si una variante resuelve el caso.

---

## 5.5 Estilo de layout

### Prioridad general
1. flex
2. grid cuando el layout realmente lo necesite
3. absolute/fixed solo cuando tenga sentido real
4. nunca usar hacks viejos si hay una solución moderna y clara

## Regla
El layout debe ser legible y fácil de mantener.

---

## 5.6 Responsive

Definir claramente:
- comportamiento móvil
- comportamiento tablet
- comportamiento desktop

No solo “hacerlo caber”.  
Debe adaptarse con intención.

---

## 5.7 Accesibilidad mínima

Siempre verificar, al menos:
- contraste suficiente
- labels entendibles
- foco visible
- botones e inputs legibles
- touch targets adecuados
- no depender solo del color para comunicar estado

---

## 5.8 Estados de interacción

Todo componente importante debería contemplar si aplica:
- hover
- active
- focus
- disabled
- loading

---

# FASE 6: patrones obligatorios

## 6.1 Empty state

Toda pantalla con contenido variable debería contemplar empty state si aplica.

Debe tener:
- mensaje claro
- tono útil
- orientación de siguiente paso
- CTA cuando sea útil

No dejar zonas vacías sin explicación.

---

## 6.2 Loading state

Usar:
- skeletons para contenido predecible
- spinner solo cuando tenga sentido
- feedback visual claro

No dejar la pantalla vacía mientras carga.

---

## 6.3 Error state

Debe tener:
- mensaje entendible
- opción de retry o acción útil
- mantener contexto del usuario cuando sea posible

No mostrar errores técnicos crudos salvo contexto técnico explícito.

---

## 6.4 Success state

Debe dejar claro:
- qué se completó
- qué sigue
- si se puede deshacer o continuar

---

## 6.5 Navegación

Elegir patrón según producto:
- bottom nav: apps móviles con pocas secciones principales
- sidebar: dashboards o entornos desktop
- header + menu: webs responsive
- breadcrumbs: jerarquías profundas

No mezclar patrones sin lógica.

---

## 6.6 CTA

### Regla principal
Debe existir jerarquía clara de acciones.

- CTA primario: la acción principal
- CTA secundario: apoyo
- CTA terciario: link o acción menor

### Evitar
- múltiples primarios compitiendo
- CTA oculto o débil
- demasiadas acciones con igual peso

---

# FASE 7: interpretación de pedidos vagos

Cuando el usuario pida cambios ambiguos, traducirlos a decisiones concretas.

## “Hazlo más moderno”
- reducir ruido
- usar más whitespace
- radios más refinados
- tipografía más limpia
- sombras más suaves
- layout más ordenado
- menos adornos

## “Hazlo más premium”
- menos elementos
- paleta más sobria
- mejor jerarquía
- más aire
- tipografía más elegante
- detalles más sutiles
- evitar colores chillones

## “Hazlo más profesional”
- neutrales dominantes
- acento controlado
- estructura sobria
- sin decoraciones innecesarias
- consistencia estricta

## “Hazlo más juvenil”
- energía controlada
- color más expresivo pero limitado
- bordes más amables
- tipografía con más personalidad
- UI más dinámica

## “Hazlo más limpio”
- quitar elementos
- reducir variedad visual
- reforzar jerarquía
- aumentar espacio entre bloques
- simplificar estructura

## “Está muy básico”
- mejorar composición
- mejor jerarquía tipográfica
- mejor acento
- spacing más intencional
- componentes mejor proporcionados
- detalles sutiles de producto real

## “Hazlo más accesible”
- aumentar legibilidad
- mejorar contraste
- hacer objetivos táctiles más cómodos
- reforzar focus states
- lenguaje más claro

---

# FASE 8: revisión crítica antes de entregar

Antes de considerar que la UI está bien, revisar esta checklist.

## Señales de mala UI

Corregir inmediatamente si aparecen varias de estas:

- elementos demasiado juntos
- demasiados colores
- tipografía inconsistente
- demasiados tamaños y pesos distintos
- botones sin jerarquía clara
- cards deformes o con padding incoherente
- layout plano o sin foco
- demasiados elementos compitiendo
- texto difícil de escanear
- contraste pobre
- componentes similares con estilos diferentes
- CTA poco visible
- demasiado borde, sombra o badge
- sensación de plantilla genérica
- desktop bien pero móvil descuidado
- mobile comprimido y poco cómodo

## Señales de buena UI

- abundante whitespace bien usado
- jerarquía visual evidente
- fluidez de lectura
- componentes consistentes
- CTA claro
- estructura limpia
- color intencional
- flujo entendible
- buenas proporciones
- sensación de producto real

---

# FASE 9: autocrítica y segunda iteración

Si la primera versión aún se siente genérica, no asumir que ya está terminada.

## Proceso obligatorio de autocrítica
Preguntarse:

1. ¿Esto se ve como demo rápida o como producto serio?
2. ¿La jerarquía visual es obvia en 3 segundos?
3. ¿El spacing está realmente bien o solo “aceptable”?
4. ¿El CTA principal destaca lo suficiente?
5. ¿Hay demasiada información compitiendo?
6. ¿Las cards y contenedores tienen buenas proporciones?
7. ¿La UI transmite la personalidad correcta?
8. ¿Móvil se siente diseñado o solo adaptado?

Si varias respuestas son negativas, hacer una segunda iteración antes de cerrar.

---

# FASE 10: uso de screenshots y revisión visual

Si el entorno permite screenshots, navegador o render visual, aprovecharlo.

## Qué revisar en capturas
- jerarquía
- spacing
- legibilidad
- equilibrio visual
- densidad
- CTA
- consistencia
- sensación premium / moderna / profesional según el caso
- adaptación mobile

## Regla
La revisión visual es parte del trabajo, no algo opcional.

---

# FASE 11: comportamiento esperado del agente

Cuando esta skill esté activa, el agente debe comportarse así:

1. No saltar directo a escribir una UI sin criterio.
2. Pensar en producto, usuario y acción principal.
3. Proponer dirección visual si hace falta.
4. Definir un pequeño sistema antes de implementar.
5. Construir con componentes reutilizables.
6. Mantener consistencia entre pantallas.
7. Revisar estados y responsive.
8. Ser crítico consigo mismo antes de finalizar.
9. Evitar caer en la primera solución genérica.
10. Buscar una salida más cercana a un producto real que a una maqueta improvisada.

---

# FASE 12: qué evitar

Evitar especialmente:

- escribir primero y pensar después
- llenar de componentes sin jerarquía
- usar demasiados colores
- meter demasiados estilos distintos
- repetir JSX con cambios mínimos
- hacer UI “bonita” pero incómoda
- descuidar móvil
- esconder la acción principal
- diseñar solo para impresionar sin pensar en tarea real
- entregar una primera versión floja como si ya estuviera final

---

# FASE 13: guía rápida de decisión

## Si el producto es:
### SaaS / Dashboard
- claridad
- estructura
- información bien jerarquizada
- sidebar o top nav clara
- cards sobrias
- densidad controlada

### App móvil de consumo
- bottom nav si aplica
- CTA claro
- touch comfort
- menos texto
- componentes grandes y limpios
- ritmo vertical cuidado

### Landing page
- hero fuerte
- narrativa clara
- secciones bien marcadas
- CTA repetido estratégicamente
- visuales limpios
- jerarquía muy clara

### E-commerce / reservas / servicios
- confianza
- búsqueda o exploración clara
- cards potentes
- detalle bien estructurado
- CTA muy visible
- estados y resumen claros

---

# FASE 14: salida ideal

La salida ideal de esta skill no debe quedarse en teoría.  
Debe terminar ayudando a producir algo concreto como:

- propuesta visual
- design system
- arquitectura de pantallas
- plan de componentes
- implementación frontend
- revisión crítica
- mejoras iterativas

---

# Resumen operativo

## Orden correcto de trabajo

1. entender producto, usuario y acción
2. definir dirección visual
3. elegir estilo recomendado
4. documentar mini design system
5. definir arquitectura de pantallas
6. implementar con componentes reutilizables
7. revisar estados y responsive
8. autocriticar resultado
9. iterar si todavía se ve genérico

---

# Nota final

Consistencia > ocurrencias aisladas  
Claridad > decoración  
Whitespace > saturación  
Sistema > improvisación  
Producto real > demo genérica

Ante la duda, simplificar, ordenar y reforzar jerarquía.