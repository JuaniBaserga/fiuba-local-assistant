# PRD v1.1 - Study Planner + Calendar Sync (FIUBA Local Assistant)

## 0. Control del documento
- Version: `1.1`
- Fecha: `2026-04-18`
- Estado: `MVP funcional (Sprint 1-4 implementados, Sprint 5 pendiente)`
- Owner: `fiuba-local-assistant`
- Ultima actualizacion: `2026-04-18`

## 1. Resumen ejecutivo
Este modulo agrega gestion de estudio al asistente local: toma fechas academicas (parciales/finales/entregas), calcula una carga de estudio sugerida por materia, genera bloques diarios/semanales y sincroniza esos bloques con Google Calendar.

El valor principal es operativo: no solo responder dudas, sino convertir cronogramas y fechas reales en un plan accionable y medible.

## 1.1 Estado de avance (2026-04-18)
Implementado:
1. `study init`: crea `study_dates.json` y `study_state.json`.
2. `study plan`: genera sesiones por prioridad y guarda estado.
3. `study export-ics`: exporta calendario importable.
4. `study log`: marca sesiones como completadas.
5. `study report`: genera CSV y graficos SVG de avance.
6. `study sync-gcal`: integra Google Calendar con `--dry-run` y cache de sincronizacion.

Pendiente:
1. Demo end-to-end con 2-3 materias reales.
2. Prueba de sincronizacion Google Calendar en modo real con credenciales del usuario.

## 2. Problema
Situacion actual:
- Las fechas academicas estan en PDFs/mensajes dispersos.
- No existe una planificacion automatica de estudio por prioridad.
- La ejecucion diaria depende de decisiones ad-hoc.

Impacto:
- Sobrecarga en semanas criticas.
- Repasos tardios.
- Dificultad para visualizar avance real por materia.

## 3. Objetivos y no-objetivos
### 3.1 Objetivos MVP
1. Registrar fechas de evaluacion por materia en formato estructurado local.
2. Calcular un plan de horas semanales por materia hasta cada fecha.
3. Generar sesiones concretas de estudio (bloques de calendario).
4. Exportar o sincronizar esas sesiones en Google Calendar.
5. Producir visualizaciones de carga planificada vs ejecutada.

### 3.2 No-objetivos MVP
1. Extraccion perfecta de fechas desde PDF escaneado.
2. Optimizacion matematica avanzada de agenda.
3. Integracion bidireccional completa con todos los calendarios del usuario.
4. App grafica dedicada.

## 4. Usuarios y casos de uso
Usuario primario:
- Estudiante FIUBA con varias materias en paralelo y fechas cercanas.

Casos de uso:
1. Cargar o actualizar fechas de parcial/final por materia.
2. Pedir plan semanal en base a disponibilidad.
3. Sincronizar automaticamente sesiones al calendario.
4. Ver reporte de carga por materia y detectar atrasos.

## 5. Alcance funcional MVP
### 5.1 Ingreso de fechas
Entrada por archivo `study_dates.json` con:
- materia
- tipo_evento (`parcial|final|entrega|otro`)
- fecha
- peso (opcional, default 1.0)

### 5.2 Planificador
Entrada:
- fechas academicas
- horas disponibles por semana
- dificultad por materia (`1-5`)

Salida:
- horas recomendadas por materia/semana
- sesiones propuestas (duracion, fecha, materia, tema opcional)

### 5.3 Sync calendario
Opciones:
1. Export `ICS` (sin OAuth, baseline robusto).
2. Sync Google Calendar (OAuth) como modo API.

### 5.4 Reporte
Genera archivos de salida:
- `study_plan.csv` (sesiones)
- `study_report_weekly.csv` (agregados por semana/materia)
- `study_report_by_materia.csv` (agregados por materia)
- graficos SVG (`study_planned_by_materia.svg`, `study_plan_vs_completed.svg`)

## 6. Requisitos funcionales
1. `RF-01`: Permitir alta/edicion de fechas academicas locales.
2. `RF-02`: Calcular prioridad por materia segun cercania de fechas y peso.
3. `RF-03`: Distribuir horas semanales sin exceder disponibilidad.
4. `RF-04`: Generar sesiones de estudio con duracion configurable.
5. `RF-05`: Exportar sesiones a `ICS`.
6. `RF-06`: Sincronizar sesiones a Google Calendar (si OAuth configurado).
7. `RF-07`: Generar reporte visual de planificacion.

## 7. Requisitos no funcionales
1. Privacidad: datos locales por defecto; sin cloud obligatorio.
2. Auditabilidad: toda sesion debe incluir fuente de regla de planificacion.
3. Robustez: si falla Google Calendar, el plan local y export `ICS` siguen funcionando.
4. Reproducibilidad: misma entrada -> mismo plan (sin aleatoriedad).

## 8. Integracion tecnica con repo actual
Estructura propuesta:
- `src/fiuba_local/study/`
- `src/fiuba_local/study/types.py`
- `src/fiuba_local/study/planner.py`
- `src/fiuba_local/study/io.py`
- `src/fiuba_local/study/calendar_ics.py`
- `src/fiuba_local/study/calendar_google.py` (opcional por feature flag)
- `src/fiuba_local/study/report.py`

CLI:
- `fiuba-local study init`
- `fiuba-local study plan`
- `fiuba-local study export-ics`
- `fiuba-local study log`
- `fiuba-local study sync-gcal`
- `fiuba-local study report`

## 9. Modelo de datos (MVP)
Archivo de estado local (`.fiuba_local/study_state.json`):
- materias
- disponibilidad semanal
- sesiones planificadas
- sesiones completadas
- bloque `gcal` con `synced_session_ids`, `last_sync_at`, `calendar_id` (si aplica)

Archivo de entrada (`.fiuba_local/study_dates.json`):
- lista de eventos academicos versionada por fecha.

## 10. Algoritmo de planificacion (v1)
Prioridad por materia:
- `priority = w_fecha * urgencia + w_peso * peso_evento + w_dificultad * dificultad`
- urgencia basada en dias restantes al evento (mas cerca => mayor puntaje).

Distribucion:
1. Calcular prioridad normalizada por materia.
2. Asignar horas semanales proporcionales a prioridad.
3. Respetar minimo por materia activa y maximo diario configurable.
4. Reservar porcentaje fijo para repaso espaciado.

## 11. Metricas de exito
1. `>= 90%` de semanas con plan generado sin errores.
2. `>= 80%` de sesiones planificadas exportadas correctamente a `ICS`.
3. `>= 70%` de sesiones completadas registradas por usuario en piloto de 2 semanas.
4. Visualizacion clara de carga por materia en cada corrida.

## 12. Riesgos y mitigaciones
Riesgo:
- Fechas incompletas o mal cargadas.
Mitigacion:
- Validaciones de esquema + comando de chequeo.

Riesgo:
- Friccion OAuth en Google Calendar.
Mitigacion:
- Hacer `ICS` como camino principal en MVP.

Riesgo:
- Plan poco realista por sobrecarga.
Mitigacion:
- Limite diario y alerta de saturacion semanal.

## 13. Dependencias
Minimas:
- Python stdlib + modulos actuales del repo.

Opcionales:
- `google-api-python-client`
- `google-auth-oauthlib`
- `pytest` para correr tests unitarios

## 14. Definicion de terminado (MVP)
1. `OK` Usuario carga fechas y disponibilidad.
2. `OK` CLI genera plan semanal reproducible.
3. `OK` CLI exporta calendario (`ICS`) y reporte visual.
4. `PARCIAL` Sync Google Calendar implementado; falta validacion real con credenciales de usuario.
5. `OK` README/documentacion con flujo de uso end-to-end.
