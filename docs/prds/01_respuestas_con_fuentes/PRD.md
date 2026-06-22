# PRD - FIUBA Assistant: Respuestas con fuentes

## 0. Control del documento
- Version: `4.0`
- Fecha: `2026-05-04`
- Ultima actualizacion: `2026-06-22`
- Madurez: `Vigente`
- Estado de iniciativa: `Activa`
- Iniciativa: `I-01`
- Owner: `Proyecto fiuba-local-assistant`

## 1. Resumen ejecutivo
FIUBA Assistant ayuda a estudiar usando apuntes locales. El producto actual se concentra en una sola promesa: responder preguntas con contexto recuperado desde la carpeta de materias y mostrar fuentes verificables.

El foco inmediato no es planificar calendarios, sincronizar Drive, ejecutar OCR desde UI ni cubrir todos los modos pedagogicos. Es hacer excelente el flujo base:

1. Indexar materiales locales.
2. Recuperar fragmentos relevantes.
3. Responder con una estructura clara.
4. Citar fuentes usadas.
5. Declarar incertidumbre cuando el contexto no alcanza.

## 2. Problema
El estudiante tiene PDFs, guias, resumenes y parciales dispersos por materia. Buscar manualmente consume tiempo, y preguntarle a un modelo sin contexto local produce respuestas genericas o dificiles de auditar.

## 3. Objetivos
1. Reducir el tiempo para encontrar una respuesta confiable en apuntes propios.
2. Mejorar la calidad de explicacion para estudiar parcial/final.
3. Mantener trazabilidad minima en cada respuesta.
4. Evitar afirmaciones fuertes cuando no hay evidencia suficiente.
5. Mantener una UI local simple, demo-ready y centrada en preguntar.

## 4. No objetivos actuales
1. Sincronizar carpetas de Google Drive desde la app.
2. Autenticar usuarios o manejar permisos cloud.
3. Ejecutar OCR desde la UI.
4. Productizar debate/resolucion paso a paso como flujo separado.
5. Productizar calendario o planificacion de estudio.
6. Construir app mobile o multiusuario.

Las ideas anteriores no se descartan; quedan registradas en
[`../06_backlog/README.md`](../06_backlog/README.md).

## 5. Usuario primario
Estudiante FIUBA con material local organizado en:

```text
~/dev/Facultad/<Materia>
```

## 6. Flujo principal
1. El usuario descarga o copia materiales a una carpeta de materia.
2. El usuario indexa esa materia desde UI o CLI.
3. El usuario selecciona materia y hace una pregunta.
4. El sistema recupera fragmentos relevantes.
5. El motor configurado genera una respuesta usando solo esos fragmentos.
6. La UI muestra respuesta, modelo usado y fuentes con extractos.

## 7. Requisitos funcionales
### RF-01 Indexado local incremental
El sistema debe indexar archivos `pdf`, `txt` y `md` por materia.

Criterios:
- No reprocesar archivos cuyo hash no cambio.
- Ignorar archivos sin texto util sin romper el proceso.
- Reportar cantidad de archivos actualizados, sin cambios y advertencias.

### RF-02 Listado de materias
La UI debe listar carpetas reales de la raiz de Facultad y marcar estado `indexada` / `sin indexar`.

Criterios:
- `/api/materias` devuelve materias detectadas e indexadas.
- La UI permite refrescar la lista.

### RF-03 Recuperacion de contexto
El sistema debe recuperar top-k chunks relevantes desde SQLite/FTS5 y aplicar rerank basico.

Criterios:
- Si hay material indexado y la pregunta matchea, devuelve al menos una fuente.
- Si no hay contexto, responde error accionable: indexar materia o ajustar consulta.

### RF-04 Respuesta con formato fijo
Toda respuesta productiva debe seguir esta estructura:

1. Respuesta corta
2. Desarrollo
3. Como usarlo en un ejercicio/parcial
4. Fuentes usadas
5. Confianza

Criterios:
- La respuesta cita fuentes con etiquetas `[S1]`, `[S2]`, etc.
- La respuesta declara evidencia insuficiente cuando corresponda.

### RF-05 Motores de respuesta
La UI debe soportar motores disponibles sin exponer complejidad innecesaria:

1. Gemini API
2. OpenAI API
3. Ollama local

Criterios:
- Gemini es el default de UI.
- Modelo/top-k/timeout quedan en ajustes avanzados.
- Errores de API key o conexion se muestran claramente.

## 8. Requisitos no funcionales
### RNF-01 Privacidad local
Los archivos no se suben completos a servicios externos. Solo se envia al motor elegido el contexto recuperado necesario para responder.

### RNF-02 Trazabilidad
Cada respuesta debe incluir fuentes visibles. La precision minima actual es archivo + chunk.

### RNF-03 Simplicidad operativa
La demo debe poder levantarse con un solo comando local y funcionar con materiales ya indexados.

### RNF-04 Resiliencia
PDFs corruptos, escaneados o sin texto no deben romper el indexado completo.

## 9. UI actual
Pantalla unica:

1. Panel lateral:
- Materia
- Estado de indexado
- Boton `Indexar`
- Motor
- Ajustes avanzados

2. Panel principal:
- Pregunta
- Boton `Responder`
- Respuesta
- Fuentes con extractos

## 10. Metricas de exito
1. `100%` de respuestas productivas incluyen fuentes.
2. `>= 85%` de respuestas del set de evaluacion tienen fuente util.
3. `>= 75%` de utilidad percibida en preguntas reales.
4. `0` afirmaciones fuertes sin evidencia en evaluacion manual.
5. Demo local levantable en menos de 2 minutos con indice existente.

## 11. Evaluacion
Dataset recomendado:

1. 20 preguntas reales por materia piloto.
2. 5 preguntas donde el contexto no alcanza.
3. 5 preguntas con documentos parecidos para evaluar si cita la fuente correcta.

Scoring por caso:

1. Exactitud tecnica
2. Utilidad pedagogica
3. Trazabilidad
4. Claridad
5. Manejo de incertidumbre

Referencia: [`../../reference/EVAL_SET.md`](../../reference/EVAL_SET.md).

## 12. Riesgos
### R-01 PDFs sin texto extraible
Mitigacion actual:
- Reportar advertencias de extraccion.
- Mantener comando CLI `ocr-check` como herramienta tecnica, no flujo principal.

### R-02 Respuestas genericas
Mitigacion:
- Prompt estricto.
- Fuentes obligatorias.
- Evaluacion con preguntas reales.

### R-03 Citas poco precisas
Mitigacion actual:
- Archivo + chunk.

Mejora futura:
- Pagina/seccion. Ver [`../06_backlog/README.md`](../06_backlog/README.md).

## 13. Dependencias

1. Material local con texto extraible.
2. Indice SQLite disponible.
3. Al menos un motor de respuesta configurado.
4. Set de evaluacion real para decidir mejoras de recuperacion.

## 14. Definicion de terminado
1. UI enfocada en preguntar y fuentes.
2. Indexado local funcionando por materia.
3. Respuesta con formato fijo y confianza.
4. Fuentes visibles en 100% de respuestas productivas.
5. Tests locales pasan.
6. README explica flujo simple: descargar local, indexar, preguntar.

## 15. Seguimiento

La realidad tecnica, prioridad y proximos pasos se mantienen en
[`../../README.md`](../../README.md).
