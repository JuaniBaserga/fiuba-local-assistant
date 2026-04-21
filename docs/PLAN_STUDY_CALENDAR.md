# Plan de ejecucion - Study Planner + Calendar Sync

## Estado actual (2026-04-18)
Resumen por sprint:
1. Sprint 0: `Completado`
2. Sprint 1: `Completado`
3. Sprint 2: `Completado`
4. Sprint 3: `Completado`
5. Sprint 4: `Completado parcial` (implementado + dry-run; falta validacion real con credenciales)
6. Sprint 5: `Pendiente`

Evidencia tecnica generada:
1. Subcomandos `study` disponibles en CLI: `init`, `plan`, `export-ics`, `log`, `report`, `sync-gcal`.
2. Salidas locales verificadas: CSV de plan, CSV de reporte, SVG de visualizacion, archivo ICS.
3. Dry-run de Google Calendar ejecutado sin creacion real de eventos.

## Contexto
Este plan implementa el alcance definido en `docs/PRD_STUDY_CALENDAR.md` sin bloquear el flujo actual de indexado/busqueda/chat.

## Estrategia
Implementacion incremental con valor visible en cada sprint:
1. Primero planificacion local reproducible.
2. Luego salida calendario sin dependencias externas (`ICS`).
3. Despues analitica y visualizacion.
4. Por ultimo integracion Google Calendar (API).

## Sprint 0 - Preparacion (0.5 dia)
Objetivo:
- Definir contratos de datos y comandos CLI.

Entregables:
1. Esquema de `study_dates.json`.
2. Esquema de `study_state.json`.
3. Stub de subcomando `study` en CLI.

Criterio de cierre:
1. `fiuba-local --help` muestra arbol de comandos `study`.

Estado:
1. `Completado` el 2026-04-18.

## Sprint 1 - Planificador local (1-2 dias)
Objetivo:
- Generar plan de horas y sesiones sin APIs externas.

Entregables:
1. Modulo `study/planner.py` con algoritmo v1 de prioridad.
2. Comandos:
- `fiuba-local study init`
- `fiuba-local study plan`
3. Persistencia de sesiones en `study_state.json`.
4. Tests unitarios de reglas de asignacion.

Criterio de cierre:
1. Dados eventos y disponibilidad, genera plan sin exceder horas semanales.

Estado:
1. `Completado` el 2026-04-18.
2. Implementado en `study/planner.py` + `study plan`.

## Sprint 2 - Export calendario (1 dia)
Objetivo:
- Llevar plan a formato consumible por calendario.

Entregables:
1. Modulo `study/calendar_ics.py`.
2. Comando `fiuba-local study export-ics`.
3. Archivo `.ics` valido con sesiones futuras.
4. Test de formato minimo ICS.

Criterio de cierre:
1. El archivo `.ics` se importa en Google Calendar manualmente sin errores.

Estado:
1. `Completado` el 2026-04-18.
2. Implementado en `study/calendar_ics.py` + `study export-ics`.

## Sprint 3 - Reportes y visualizacion (1-2 dias)
Objetivo:
- Medir carga y progreso para presentacion en clase.

Entregables:
1. Modulo `study/report.py`.
2. Comando `fiuba-local study report`.
3. CSV agregados + 2 graficos SVG:
- horas por materia/semana
- planificado vs completado

Criterio de cierre:
1. Reporte generado en una corrida con datos de ejemplo.

Estado:
1. `Completado` el 2026-04-18.
2. Archivos de salida validados en `.fiuba_local/reports/`.

## Sprint 4 - Google Calendar API (1-2 dias)
Objetivo:
- Sincronizacion automatica (opcional) con API oficial.

Entregables:
1. Modulo `study/calendar_google.py`.
2. Comando `fiuba-local study sync-gcal`.
3. Documentacion OAuth paso a paso.
4. Modo `dry-run` para validar sin crear eventos.

Criterio de cierre:
1. Crea eventos en calendario objetivo y evita duplicados por `event_id` local.

Estado:
1. `Completado parcial` el 2026-04-18.
2. Implementado `study sync-gcal` con OAuth, cache `synced_session_ids` y `--dry-run`.
3. Pendiente prueba real de creacion de eventos con credenciales del usuario.

## Sprint 5 - End-to-end demo (0.5-1 dia)
Objetivo:
- Preparar evidencia para clase/entrega.

Entregables:
1. Dataset ejemplo de 2-3 materias.
2. Script de demo reproducible.
3. Capturas/plots para presentacion.

Criterio de cierre:
1. Flujo completo en <= 10 minutos desde cero.

Estado:
1. `Pendiente`.
2. Proximo objetivo: demo con 2-3 materias reales y guion de presentacion.

## Riesgos operativos
1. Datos de entrada inconsistentes.
- Mitigacion: validador de esquema y mensajes de error claros.
2. Sobrecarga de plan por fechas muy cercanas.
- Mitigacion: alerta de saturacion + rebalanceo automatico.
3. OAuth complejo en clase.
- Mitigacion: mostrar primero `ICS`; API como plus.

## Orden de implementacion recomendado
1. Sprint 1
2. Sprint 2
3. Sprint 3
4. Sprint 4
5. Sprint 5

## Definicion de listo para empezar codigo
1. PRD validado.
2. Prioridades de materias iniciales definidas.
3. Disponibilidad semanal inicial acordada.
