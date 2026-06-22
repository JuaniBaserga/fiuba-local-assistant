# PRD v0.2 - Cerebro y mapa semantico

## 0. Control del documento

- Version: `0.2`
- Fecha: `2026-06-22`
- Ultima actualizacion: `2026-06-22`
- Madurez: `Vigente para discovery`
- Estado de iniciativa: `Discovery`
- Iniciativa: `I-02`
- Owner: `fiuba-local-assistant`
- Corpus piloto: `Ind Extractivas`

## 1. Resumen ejecutivo

Esta iniciativa crea una capa de conocimiento local que combina materiales academicos y notas propias. Obsidian funciona como interfaz humana para escribir, enlazar y mantener el cerebro; FIUBA Assistant extrae, fragmenta, representa con embeddings y permite explorarlo.

El primer producto no sera un chat nuevo. Sera un mapa semantico interactivo de `Ind Extractivas`: fragmentos conceptualmente cercanos apareceran juntos y cada punto permitira volver al documento y pagina de origen.

El mapa es un experimento visible y divertido, pero tambien construye capacidades reutilizables: embeddings incrementales, citas por pagina, colecciones, recuperacion hibrida y soporte futuro para un vault de Obsidian.

Actualizacion `2026-06-22`: ya existe un primer corte funcional del indice semantico experimental. Permite indexar un corpus piloto, buscar vecinos semanticos por CLI y revisar estado/busquedas desde `/admin`. El mapa 2D interactivo sigue pendiente.

## 2. Problema

Hoy existen dos problemas relacionados:

1. Los apuntes estan organizados por carpetas, pero sus relaciones conceptuales permanecen ocultas.
2. Las decisiones, aprendizajes y notas propias no tienen una memoria conectada con las fuentes academicas.

La busqueda actual usa SQLite FTS5 y coincidencia de palabras. Funciona cuando la consulta comparte vocabulario con el texto, pero no representa proximidad semantica ni permite explorar el corpus visualmente.

## 3. Hipotesis

Si representamos fragmentos de buenos PDFs con embeddings y los mostramos en un mapa navegable, entonces el usuario podra:

1. descubrir relaciones entre teoria, practica, resumenes y parciales;
2. encontrar material relevante aunque use palabras diferentes;
3. detectar zonas densas, duplicadas o aisladas del corpus;
4. entender intuitivamente que aportan los embeddings;
5. validar la infraestructura antes de integrarla al flujo principal.

## 4. Objetivos del piloto

1. Construir embeddings locales para un subconjunto de `Ind Extractivas`.
2. Extraer y conservar pagina de origen para cada fragmento.
3. Proyectar los embeddings a dos dimensiones.
4. Mostrar un mapa interactivo con color por tipo de material.
5. Permitir busqueda semantica y resaltado de vecinos.
6. Abrir o identificar claramente PDF, pagina y extracto de cada punto.
7. Mantener el experimento aislado del indice estable.

## 5. No objetivos del piloto

1. Reemplazar la busqueda FTS5 actual.
2. Indexar desde el primer dia las 36 fuentes PDF completas.
3. Crear una base vectorial distribuida o servicio cloud.
4. Enviar apuntes o notas a proveedores externos.
5. Resolver sincronizacion entre dispositivos.
6. Diseñar el vault definitivo antes de aprender del mapa.
7. Productizar un tutor personalizado completo.

## 6. Corpus piloto

La auditoria del `2026-06-22` encontro:

- 36 PDFs;
- 14 DOCX;
- 2 TXT;
- 3 imagenes JPEG;
- ningun PDF marcado como candidato claro a OCR;
- 4 documentos y 418 chunks de la materia presentes en el indice estable, por lo que el indice actual esta incompleto respecto del corpus disponible.

El piloto usara entre 6 y 10 PDFs representativos:

1. teoria;
2. practica;
3. resumenes;
4. parciales o preguntas de examen.

Se evitaran inicialmente compilaciones gigantes y duplicados para que el mapa no quede dominado por una sola fuente.

### Estado del corpus piloto

Al `2026-06-22` se indexo el piloto inicial de `Ind Extractivas`:

- 10 documentos;
- 616 fragmentos;
- 616 embeddings;
- base experimental: `/Users/juanibaserga/dev/.fiuba_local/semantic.db`;
- modelo: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.

La base estable FTS usada por la app principal permanece separada:
`/Users/juanibaserga/dev/.fiuba_local/index.db`.

## 7. Experiencia del usuario

### 7.1 Explorar

El usuario abre el mapa y ve cada fragmento como un punto:

- posicion: proximidad semantica;
- color: teoria, practica, resumen o parcial;
- opacidad o tamano: relevancia o densidad local;
- tooltip: titulo, pagina y extracto breve.

### 7.2 Buscar

El usuario escribe una idea, por ejemplo `separacion por flotacion`. El sistema genera el embedding de la consulta, encuentra vecinos y resalta la region correspondiente.

Estado actual: la busqueda semantica ya funciona por CLI y por `/admin`. La UI devuelve ranking, puntaje, fuente, pagina y extracto. El resaltado sobre mapa queda pendiente de la visualizacion 2D.

### 7.3 Jugar con vecinos

El usuario selecciona un fragmento, intenta anticipar cual sera su vecino semantico mas cercano y luego revela el ranking. Este modo hace visible la calidad y los errores del modelo.

### 7.4 Volver a la fuente

Desde cualquier punto se debe poder identificar el archivo y pagina exactos. Cuando el entorno lo permita, se ofrecera apertura directa del PDF.

## 8. Arquitectura propuesta

```text
Facultad/Ind Extractivas/*.pdf
            |
            v
extraccion por pagina
            |
            v
chunks + metadatos + hash
            |
      +-----+-----+
      |           |
     FTS5     embeddings locales
      |           |
      +-----+-----+
            |
     vecinos + proyeccion 2D
            |
       mapa interactivo
```

Implementacion actual:

```text
CLI /admin
   |
   v
src/fiuba_local/semantic.py
   |
   v
SQLite experimental semantic.db
   |
   +-- documents
   +-- fragments
   +-- embeddings
```

El futuro vault `Cerebro/` entrara por el mismo pipeline como otra coleccion:

```text
collection: facultad | cerebro
area: Ind Extractivas | Desarrollo | ...
type: source | concept | project | decision | experiment
```

## 9. Modelo de datos minimo

### Documento

- `id`
- `path`
- `collection`
- `area`
- `document_type`
- `title`
- `sha256`
- `metadata_json`

### Fragmento

- `id`
- `document_id`
- `chunk_index`
- `page_start`
- `page_end`
- `text`
- `text_hash`

### Embedding

- `chunk_id`
- `model_id`
- `dimensions`
- `vector`
- `created_at`

### Proyeccion

- `chunk_id`
- `projection_id`
- `x`
- `y`

## 10. Requisitos funcionales

### RF-01 Indice experimental

El piloto debe usar una base separada del indice de produccion. Borrar o regenerar el experimento no debe afectar preguntas actuales.

Estado: implementado. El indice semantico usa una SQLite separada (`semantic.db`) y no modifica `index.db`.

### RF-02 Extraccion por pagina

Cada fragmento de PDF debe conservar pagina inicial y final. Los errores de extraccion deben registrarse sin detener el corpus completo.

Estado: implementado para PDFs con `pypdf`. TXT y Markdown se soportan como pagina logica unica para preparar integracion futura con Obsidian.

### RF-03 Embeddings incrementales

El sistema debe reutilizar embeddings cuando no cambien el texto ni el modelo. Un cambio de archivo solo debe recalcular sus fragmentos afectados.

Estado: implementado por hash de archivo y hash de texto. Validacion: reindexar los 10 archivos piloto devolvio `10` sin cambios y `0` embeddings recalculados.

### RF-04 Privacidad local

El modelo de embeddings del piloto debe ejecutarse localmente. Cualquier opcion cloud futura requerira eleccion explicita.

Estado: implementado. La inferencia usa `sentence-transformers` local. La descarga inicial del modelo requiere accion explicita; luego las consultas usan el modelo cacheado.

### RF-05 Visualizacion

El mapa debe soportar zoom, desplazamiento, tooltip, filtros por tipo y seleccion de un punto.

Estado: pendiente. Existe `/admin` como panel operativo, pero no mapa 2D.

### RF-06 Busqueda semantica

Una consulta debe mostrar al menos diez vecinos con puntaje, fuente, pagina y extracto.

Estado: implementado por CLI y `/admin`.

### RF-07 Reproducibilidad

Debe existir un comando documentado para reconstruir embeddings y proyeccion desde cero.

Estado: parcial. Existe comando reproducible para embeddings; falta proyeccion 2D.

```bash
PYTHONPATH=src .venv/bin/python -m fiuba_local.cli \
  --root /Users/juanibaserga/dev/Facultad \
  semantic index \
  --materia "Ind Extractivas" \
  --semantic-db /Users/juanibaserga/dev/.fiuba_local/semantic.db \
  --limit-files 10
```

Busqueda:

```bash
PYTHONPATH=src .venv/bin/python -m fiuba_local.cli \
  semantic search "separacion por flotacion con burbujas" \
  --semantic-db /Users/juanibaserga/dev/.fiuba_local/semantic.db \
  --top-k 10
```

Admin:

```bash
PYTHONPATH=src .venv/bin/python -m fiuba_local.cli \
  --root /Users/juanibaserga/dev/Facultad \
  --db /Users/juanibaserga/dev/.fiuba_local/index.db \
  serve --host 127.0.0.1 --port 8788 \
  --semantic-db /Users/juanibaserga/dev/.fiuba_local/semantic.db
```

Abrir: `http://127.0.0.1:8788/admin`.

## 11. Evaluacion

### Metricas tecnicas

1. 100% de los puntos muestran fuente y pagina.
2. Reindexar sin cambios no recalcula embeddings.
3. El mapa carga de forma util en una maquina local.
4. Ningun contenido sale del equipo durante el piloto.

Estado de evidencia `2026-06-22`:

1. Cumplido para resultados semanticos: fuente, pagina y extracto visibles.
2. Cumplido: reindexado del piloto no recalculo embeddings.
3. Pendiente: no hay mapa 2D todavia.
4. Cumplido para inferencia: embeddings locales. La descarga inicial del modelo fue explicita.

### Metricas de producto

1. El usuario identifica al menos tres relaciones utiles o sorprendentes.
2. En cinco consultas de prueba, al menos cuatro muestran vecinos plausibles.
3. El usuario puede explicar la diferencia entre busqueda textual y semantica despues de usar el mapa.

## 12. Fases

### Fase A - Corpus y pagina

1. Seleccionar 6-10 PDFs.
2. Extraer texto por pagina.
3. Etiquetar tipo de documento.
4. Detectar duplicados evidentes.

Estado: completada para el primer corte operativo, salvo deduplicacion avanzada.

### Fase B - Espacio semantico

1. Elegir un modelo local multilingue.
2. Generar embeddings incrementales.
3. Calcular vecinos.
4. Proyectar a 2D.

Estado: parcialmente completada. Modelo local, embeddings incrementales y vecinos funcionan. Falta proyeccion 2D.

### Fase C - Juguete navegable

1. Construir mapa interactivo.
2. Agregar busqueda y filtros.
3. Agregar modo de vecinos.
4. Registrar hallazgos y fallas.

Estado: iniciada con `/admin`. Busqueda y filtros basicos funcionan; mapa y modo vecinos siguen pendientes.

### Fase D - Decision

1. Comparar busqueda semantica con FTS5.
2. Decidir si integrar recuperacion hibrida en I-01.
3. Crear `Cerebro/` y sumar Markdown/Obsidian si el experimento demuestra valor.

## 13. Riesgos

### El mapa refleja longitud o duplicados, no conceptos

Mitigacion: corpus pequeño, balanceado por tipo y con deduplicacion inicial.

### La proyeccion 2D inventa separaciones visuales

Mitigacion: mostrar tambien vecinos y similitudes originales; tratar el mapa como interfaz exploratoria, no como verdad matematica.

### El modelo local entiende mal español tecnico

Mitigacion: evaluar cinco consultas conocidas y conservar FTS5 como baseline.

### El experimento crece hasta convertirse en otra aplicacion paralela

Mitigacion: criterio de cierre corto y decision explicita al terminar Fase C.

## 14. Definicion de terminado del piloto

1. Existe un comando reproducible para construir el corpus experimental.
2. Entre 6 y 10 PDFs estan representados con pagina trazable.
3. El mapa es navegable y permite buscar.
4. El modo vecinos funciona.
5. Se registraron cinco consultas y tres hallazgos.
6. Hay una decision escrita: integrar, iterar o archivar.

## 15. Preguntas abiertas

1. Que modelo local ofrece el mejor equilibrio entre español tecnico, tamaño y velocidad.
2. Si el punto debe representar pagina, chunk o documento segun el nivel de zoom.
3. Que tecnica de proyeccion produce un mapa estable y comprensible.
4. Si `/admin` alcanza como interfaz de discovery o si el mapa debe vivir como vista separada.
5. Como abrir PDFs en pagina exacta de forma portable.

## 16. Hallazgos iniciales

Consulta: `separacion por flotacion con burbujas`.

Resultados plausibles:

1. `04. 07_Apunte Separaciones-1.pdf`, pagina 23, definicion de flotacion.
2. `04. 07_Apunte Separaciones-1.pdf`, pagina 25, burbujas y factores de flotacion.
3. `04. Clase_Flotacion.pdf`, pagina 7, colectores que unen burbujas y particulas.

Consulta: `trituracion molienda tamaño de particula`.

Resultados plausibles:

1. `02. 06_Apunte Molienda.pdf`, pagina 20.
2. `01. 05_Apunte Trituracion.pdf`, pagina 4.
3. `04. 07_Apunte Separaciones-1.pdf`, pagina 16.

Decision provisional: continuar el discovery hacia comparacion FTS vs semantica y mapa 2D. No integrar todavia en el flujo principal de respuestas.
