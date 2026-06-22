# FIUBA Local Assistant — estado y dirección

- Ultima actualizacion: `2026-06-22`
- Estado general: `MVP local funcional + discovery semantico`
- Producto activo: `Respuestas con fuentes`
- Discovery activo: `Cerebro semantico`
- Tests: `23 passed`

Este README es la fuente de verdad operativa del proyecto. Resume que existe,
que se esta priorizando y que cambio recientemente. Los detalles estables de
alcance viven en [`prds/`](prds/).

## Regla de mantenimiento

Toda implementación significativa debe actualizar este archivo en el mismo
cambio. Como minimo se debe revisar:

1. `Ultima actualizacion`.
2. `Estado actual`.
3. `Prioridades`.
4. `Cambios recientes`.
5. La cantidad o estado de los tests.

Un cambio esta incompleto si modifica capacidades, comandos, experiencias o
prioridad sin reflejarlo aqui.

## Visión

Convertir materiales de estudio propios en un sistema de conocimiento confiable
que ayude al alumno a comprender, practicar y decidir que hacer despues.

La secuencia estratégica es:

1. **Confianza:** responder usando fuentes propias y verificables.
2. **Comprensión:** conectar teoría, práctica y evaluaciones semánticamente.
3. **Continuidad:** recordar el aprendizaje y recomendar próximas acciones.

No se prioriza personalización compleja antes de medir la calidad de recuperación.

## Estado actual

| Capacidad | Estado | Notas |
|---|---|---|
| Indexado incremental | Funciona | PDF, TXT y Markdown por materia |
| Búsqueda textual | Funciona | SQLite FTS5 |
| Preguntas con fuentes | Funciona | Gemini, OpenAI u Ollama |
| Citas | Parcial | Archivo/chunk; página pendiente en el flujo estable |
| Índice semántico | Experimental | Embeddings locales, páginas y base separada |
| Admin de indexación | Experimental | `/admin` muestra estado FTS/semántico y permite buscar vecinos |
| Diagnóstico OCR | Técnico | Disponible por CLI |
| Actividades de práctica | Funciona | Hub único con Extractivas y Automatización |
| Planner/calendario | Demo UI | Planificador local, export ICS y pantalla `/calendar` |

## Prioridades

### Ahora

1. Evaluar diez preguntas reales de Industrias Extractivas.
2. Comparar recuperación semántica contra el baseline FTS5.
3. Llevar citas por página al flujo estable si el piloto demuestra valor.

### Después

1. Integrar notas Markdown/Obsidian al cerebro semántico.
2. Unificar el modelo de contenido de las actividades pedagógicas.
3. Retomar memoria, agente personalizado o calendarización solo con evidencia de uso.

## Portfolio

| Orden | Iniciativa | Estado | Documento |
|---|---|---|---|
| 01 | Respuestas con fuentes | Activa | [`prds/01_respuestas_con_fuentes/PRD.md`](prds/01_respuestas_con_fuentes/PRD.md) |
| 02 | Cerebro semántico | Discovery | [`prds/02_cerebro_semantico/PRD.md`](prds/02_cerebro_semantico/PRD.md) |
| 03 | Study Vault | Absorbida por 02 | [`prds/03_study_vault/PRD.md`](prds/03_study_vault/PRD.md) |
| 04 | Calendarización | Pausada | [`prds/04_calendarizacion/PRD.md`](prds/04_calendarizacion/PRD.md) |
| 05 | Agente personalizado | Backlog | [`prds/05_agente_personalizado/PRD.md`](prds/05_agente_personalizado/PRD.md) |
| 06 | Oportunidades futuras | Backlog | [`prds/06_backlog/README.md`](prds/06_backlog/README.md) |

Reglas:

- Solo puede haber un producto activo y un discovery simultáneos.
- Todo discovery termina con una decisión: integrar, iterar o archivar.
- Tener código implementado no garantiza que una iniciativa siga priorizada.

## Ejecutar

Aplicación principal:

```bash
cd /Users/juanibaserga/dev/fiuba-local-assistant
.venv/bin/python -m fiuba_local.cli \
  --root /Users/juanibaserga/dev/Facultad \
  --db /Users/juanibaserga/dev/.fiuba_local/index.db \
  serve --host 127.0.0.1 --port 8787
```

Actividades pedagógicas:

```bash
python3 -m http.server 8000 --directory activities
```

Abrir:

- App principal: `http://127.0.0.1:8787`
- Calendario: `http://127.0.0.1:8787/calendar`
- Admin: `http://127.0.0.1:8787/admin`
- Actividades: `http://127.0.0.1:8000`

Tests:

```bash
.venv/bin/python -m pytest -q
```

## Cambios recientes

### 2026-06-22

- Se endureció y refactorizó el planner: límites diarios estrictos, sesiones
  siempre anteriores al objetivo, validación compartida entre CLI y HTTP y
  persistencia JSON atómica.
- Se separaron los comandos CLI y handlers web por dominio, con `StudyService`
  como capa común y pruebas de regresión para entrypoints, estado e ICS.
- Se incorporó un índice semántico experimental con embeddings locales,
  trazabilidad por página y comandos `semantic index`, `semantic search` y
  `semantic stats`.
- Se agregó `/admin` para revisar rutas de índices, métricas FTS/semánticas,
  reindexar el piloto semántico y probar vecinos con fuente, página y extracto.
- Se agregó `/calendar` como pantalla de organización con plan, reporte e
  exportación ICS.
- Se migraron las prácticas de Extractivas y Automatización al repositorio.
- Se creó una página única para cambiar entre ambas actividades.
- El asistente principal se incorporó como pantalla inicial de esa página, para
  reunir preguntas y prácticas en un solo lugar.
- Los PRD se agruparon por iniciativa y prioridad dentro de `docs/prds/`.
- La documentación operativa se consolidó en este README.

### 2026-04-18

- Se implementó la aplicación localhost, el indexado incremental, los motores de
  respuesta, el diagnóstico OCR y el planner/calendario experimental.

## Estructura documental

```text
docs/
├── README.md       fuente de verdad operativa
├── prds/           alcance y decisiones por iniciativa
└── reference/      material auxiliar vigente
```

- Registro y reglas de PRD: [`prds/README.md`](prds/README.md)
- Set de evaluación: [`reference/EVAL_SET.md`](reference/EVAL_SET.md)
