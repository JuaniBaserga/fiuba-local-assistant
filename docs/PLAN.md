# Plan de Ejecucion v2 (Chat-First)

> Nota 2026-05-04: este plan queda como documento historico. El foco actual esta en
> `docs/PRD.md`; los modos `resumir`, `debatir` y OCR UI quedan como futuras
> iniciativas en `docs/PRD_FUTURE.md`.

## Estado actual
Base tecnica lista:
1. Indexado incremental por materia.
2. Busqueda local en SQLite + FTS5.
3. Consulta asistida con soporte Ollama/OpenAI/Gemini (opcional por motor).
4. UI localhost enfocada en `Preguntar`.
5. Deteccion de OCR por CLI como diagnostico tecnico.

## Sprint A - Operacion chat-first (actual)
Objetivo: estandarizar el flujo de estudio conmigo como motor principal.

Entregables:
1. Protocolo operativo para `preguntar`, `resumir`, `debatir`.
2. Plantilla fija de salida con fuentes.
3. Criterios de calidad minimos por respuesta.
4. Materia piloto: `Ind Extractivas`.

Criterio de cierre:
1. 10 consultas reales contestadas con formato fijo y fuentes trazables.

## Sprint B - Calidad de recuperacion
Objetivo: mejorar precision del contexto recuperado antes de responder.

Entregables:
1. Ajuste de top-k y rerank basico por tokens.
2. Priorizacion de secciones relevantes por tipo de consulta.
3. Mejoras de cita (archivo + chunk y, cuando sea posible, pagina/seccion).
4. Manejo explicito de casos con fuente insuficiente.

Criterio de cierre:
1. >= 85% de respuestas con fuente util y verificable.

## Sprint C - Debate de resueltos
Objetivo: convertir `debatir` en un flujo robusto para practica de examen.

Entregables:
1. Protocolo paso a paso de auditoria de resoluciones.
2. Salida estructurada: veredicto, error, impacto, correccion, alternativa.
3. Checklist de examen por tema.
4. Casos de prueba con resueltos reales.

Criterio de cierre:
1. >= 70% de deteccion correcta de errores en 10 resueltos.

## Sprint D - Evidencia para entrega 9216
Objetivo: empaquetar evidencia reproducible del proyecto.

Entregables:
1. Set de evaluacion documentado (preguntas + resueltos + resultados).
2. README final con flujo de uso y limitaciones.
3. Demo breve del enfoque chat-first con trazabilidad de fuentes.

Criterio de cierre:
1. Material listo para compartir como entregable web/GitHub.
