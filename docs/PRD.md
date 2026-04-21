# PRD v3 - Asistente de Estudio FIUBA (Chat-First)

## 0. Control del documento
- Version: `3.1`
- Fecha: `2026-04-18`
- Estado: `Aprobado para implementacion`
- Owner: `Proyecto fiuba-local-assistant`

## 1. Resumen ejecutivo
Este producto resuelve un problema concreto de estudio en FIUBA: material disperso y alto costo para convertir apuntes en respuestas accionables.
La estrategia es `chat-first`: el motor principal es la sesion de chat con el asistente, y la capa local (`fiuba-local-assistant`) funciona como infraestructura de recuperacion y trazabilidad.

Resultado esperado del MVP:
1. Responder preguntas de teoria y procedimiento con fuentes verificables.
2. Resumir unidades en formato util para parcial.
3. Auditar resueltos paso a paso con correcciones claras.

## 2. Problema y oportunidad
Problema actual:
- PDF/guia/resuelto en carpetas sin estructura uniforme.
- Mucho tiempo en busqueda manual.
- Respuestas de modelos locales sin suficiente contexto ni trazabilidad.

Oportunidad:
- Flujo de estudio asistido con fuente local.
- Estandar de respuesta repetible (misma estructura, misma calidad).
- Evidencia medible para entrega academica.

## 3. Objetivos y no-objetivos
### 3.1 Objetivos
1. Mejorar velocidad y calidad de estudio en consultas reales.
2. Mantener privacidad total de fuentes (carpeta local).
3. Garantizar trazabilidad minima por respuesta.
4. Operar con un protocolo estable para `preguntar`, `resumir`, `debatir`.

### 3.2 No-objetivos (MVP)
1. Reemplazar por completo el criterio del estudiante.
2. Autonomia total sin validacion humana.
3. Multiusuario, permisos complejos, sync cloud.
4. App mobile nativa.

## 4. Usuarios y casos de uso
### 4.1 Usuario primario
Estudiante FIUBA (Ing. Industrial) con material local en `~/dev/Facultad`.

### 4.2 Jobs to be done
1. "Cuando estudio una unidad, quiero un resumen para rendir parcial sin leer todo de cero."
2. "Cuando resuelvo un ejercicio, quiero detectar rapido en que paso estoy fallando."
3. "Cuando tengo una duda puntual, quiero respuesta corta, desarrollo y fuente."

## 5. Alcance funcional MVP
### 5.1 Modo `preguntar`
Entrada:
- `materia`
- `pregunta`
- opcional `archivo/tema`

Salida obligatoria:
1. Respuesta corta
2. Desarrollo
3. Chequeo de parcial
4. Fuentes
5. Nivel de confianza (`alta | media | baja`)

### 5.2 Modo `resumir`
Entrada:
- `materia`
- `unidad/tema` o `archivo`

Salida obligatoria:
1. Mapa del tema
2. Conceptos clave
3. Formulas/criterios
4. Errores frecuentes
5. Fuentes
6. Nivel de confianza

### 5.3 Modo `debatir`
Entrada:
- `materia`
- `enunciado`
- `intento del estudiante`

Salida obligatoria:
1. Veredicto rapido (`correcto | parcial | incorrecto`)
2. Error por paso
3. Impacto del error
4. Correccion minima
5. Estrategia alternativa
6. Checklist de examen
7. Fuentes
8. Nivel de confianza

## 6. Requisitos funcionales (RF)
### RF-01 Ingestion incremental
El sistema debe indexar material por materia (`pdf/md/txt`) sin reprocesar archivos sin cambios.

Criterio de aceptacion:
- Si no cambia hash de archivo, no se reindexa.

### RF-02 Recuperacion de contexto
Debe recuperar top-k fragmentos relevantes y aplicar rerank basico.

Criterio de aceptacion:
- Para una consulta con datos existentes, devuelve al menos 1 fuente util.

### RF-03 Trazabilidad
Toda respuesta debe incluir fuentes usadas (archivo + referencia de chunk y, cuando sea posible, pagina/seccion).

Criterio de aceptacion:
- 100% de respuestas en modo productivo incluyen bloque de fuentes.

### RF-04 Contrato de salida
La respuesta debe respetar estructura fija por modo (`preguntar/resumir/debatir`).

Criterio de aceptacion:
- >= 90% de respuestas cumplen plantilla completa.

### RF-05 Manejo de incertidumbre
Si no hay evidencia suficiente, el asistente debe declararlo explicitamente.

Criterio de aceptacion:
- 0 casos de afirmacion fuerte sin fuente en evaluacion controlada.

## 7. Requisitos no funcionales (RNF)
### RNF-01 Privacidad
No se suben archivos de estudio a servicios externos.

### RNF-02 Resiliencia
Archivos corruptos o sin texto no deben romper el flujo general.

### RNF-03 Latencia operativa
Tiempo objetivo por respuesta interactiva: `<= 20s` en consultas normales (excluye modelos locales pesados no cacheados).

### RNF-04 Auditabilidad
Debe existir registro suficiente para explicar por que se respondio algo (fuentes y formato aplicado).

## 8. Arquitectura de solucion (alto nivel)
1. `Chat layer`: interfaz principal con el usuario.
2. `Retrieval layer`: indice local SQLite + FTS5 + rerank simple.
3. `Source layer`: archivos en `~/dev/Facultad`.
4. `Optional local LLM layer`: Ollama para pruebas/autonomia, no obligatorio para el flujo principal.

Principio clave:
- El chat es el orquestador, no un paso accesorio.

## 9. Protocolo operativo
Formato recomendado de entrada:

```text
tipo: preguntar | resumir | debatir
materia: <nombre>
tema/enunciado: <texto>
intento (solo debatir): <texto opcional>
```

Reglas operativas:
1. Primero recuperar evidencia local.
2. Luego sintetizar respuesta.
3. Finalmente reportar fuentes y confianza.

## 10. Metricas de exito
### 10.1 Calidad de respuesta
1. `>= 85%` respuestas con fuente util y verificable.
2. `>= 75%` utilidad percibida (set de 20 preguntas).
3. `>= 70%` deteccion correcta de errores (10 resueltos).

### 10.2 Calidad operativa
1. `>= 90%` cumplimiento de plantilla de salida.
2. `100%` respuestas con bloque de fuentes.

## 11. Evaluacion y metodo de medicion
Dataset de control:
1. 20 preguntas reales (`preguntar/resumir`).
2. 10 casos reales de ejercicios (`debatir`).

Scoring por caso (0-8):
1. Exactitud tecnica
2. Utilidad pedagogica
3. Trazabilidad
4. Claridad

Fuente de verdad de evaluacion:
- `docs/EVAL_SET.md`

## 12. Riesgos y mitigaciones
### Riesgo A: respuestas genericas
Mitigacion:
- Forzar plantilla y bloque de fuentes.
- Penalizar respuestas sin evidencia.

### Riesgo B: fuente insuficiente
Mitigacion:
- Declarar "evidencia insuficiente".
- Solicitar archivo/unidad adicional.

### Riesgo C: PDF dificil de extraer
Mitigacion:
- Fallback de extractor.
- Marcar baja confianza cuando el texto extraido es deficiente.

### Riesgo D: deriva de calidad entre sesiones
Mitigacion:
- Uso estricto de protocolo chat-first.
- Evaluacion semanal contra set fijo.

## 13. Plan de implementacion
### Sprint A (actual): Operacion chat-first
Entregables:
1. PRD v3.
2. Protocolo operativo y plantilla fija.
3. 10 consultas reales de materia piloto.

### Sprint B: Calidad de recuperacion y citas
Entregables:
1. Ajuste top-k/rerank.
2. Citas mas precisas (ideal: pagina/seccion).
3. Manejo formal de baja confianza.

### Sprint C: Debate de resueltos robusto
Entregables:
1. Auditoria por pasos estable.
2. Correccion minima + alternativa + checklist.
3. Validacion con 10 resueltos.

### Sprint D: Entrega academica
Entregables:
1. Evidencia de evaluacion.
2. README final de uso.
3. Demo corta reproducible.

## 14. Definicion de terminado (DoD MVP)
1. Flujo chat-first operativo en materia piloto.
2. Respuestas con formato fijo, fuentes y confianza.
3. Metricas minimas cumplidas en set de evaluacion.
4. Documentacion suficiente para entrega 9216.

## 15. Supuestos y dependencias
1. El usuario mantiene su material en `~/dev/Facultad`.
2. El indice local esta actualizado por materia.
3. El proceso de estudio prioriza chat sobre UI propia.

## 16. Preguntas abiertas
1. Prioridad de materias para escalar despues de `Ind Extractivas`.
2. Nivel de profundidad deseado por tipo de materia.
3. Si conviene agregar modo "entrenamiento oral" para finales.

## 17. Estado de implementacion (snapshot)
Implementado al momento:
1. CLI base: `index`, `ask`, `answer`, `serve`, `stats`.
2. UI localhost con flujo `Preguntar` y motores `Codex/OpenAI/Gemini/Ollama`.
3. Carga de claves por `.env` (`GEMINI_API_KEY`, `GOOGLE_API_KEY`, `OPENAI_API_KEY`).
4. OCR detection:
- Comando `ocr-check` para detectar PDFs candidatos.
- Tab `OCR Check` en la UI con sugerencia de comando `ocrmypdf`.
5. Materias en UI:
- Lista de carpetas reales detectadas desde `~/dev/Facultad`.
- Estado por materia: `indexada` / `sin indexar`.
6. Documentacion operativa:
- `CHAT_PROTOCOL.md`
- `EVAL_SET.md`
- `SPRINT_A_CHECKLIST.md`

Pendiente inmediato:
1. Citas por pagina/seccion (hoy: archivo/chunk).
2. Flujo robusto de `debatir` en UI.
3. Integrar ejecucion OCR desde UI (hoy: deteccion + sugerencia).
