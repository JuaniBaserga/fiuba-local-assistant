# FIUBA Assistant

Asistente local para estudiar con apuntes propios. Indexa materiales por materia, recupera fragmentos relevantes y responde preguntas con fuentes visibles.

## Foco actual

El producto esta concentrado en una sola experiencia:

1. Descargar o copiar apuntes a una carpeta local.
2. Indexar una materia.
3. Preguntar desde la UI.
4. Revisar respuesta, fuentes y confianza.

Las ideas fuera de foco inmediato, como OCR asistido, Google Drive, debate de
ejercicios y calendario de estudio, estan documentadas en
`docs/prds/06_backlog/README.md`.

## Requisitos

- Python 3.10+.
- `pip`.
- Opcional: API key de Gemini u OpenAI.
- Opcional: Ollama para modo local.

## Quick Start

```bash
cd fiuba-local-assistant
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[pdf]"
cp .env.example .env
```

Edita `.env` si queres usar motores cloud:

```env
GEMINI_API_KEY=...
OPENAI_API_KEY=...
```

Para el setup minimo alcanza con configurar una sola key. Recomendado:

```env
GEMINI_API_KEY=tu_api_key
```

Prepara materiales:

```text
~/dev/Facultad/<Materia>/
```

Ejemplo:

```text
~/dev/Facultad/Ind Extractivas/
```

Indexa una materia:

```bash
.venv/bin/python -m fiuba_local.cli \
  --root ~/dev/Facultad \
  --db ~/.fiuba_local/index.db \
  index --materia "Ind Extractivas"
```

Levanta la UI:

```bash
.venv/bin/python -m fiuba_local.cli \
  --root ~/dev/Facultad \
  --db ~/.fiuba_local/index.db \
  serve --host 127.0.0.1 --port 8787
```

Abri:

```text
http://127.0.0.1:8787
```

## CLI Util

Ver estado del indice:

```bash
.venv/bin/python -m fiuba_local.cli \
  --root ~/dev/Facultad \
  --db ~/.fiuba_local/index.db \
  stats
```

Buscar sin generar respuesta:

```bash
.venv/bin/python -m fiuba_local.cli \
  --root ~/dev/Facultad \
  --db ~/.fiuba_local/index.db \
  ask "balance de masa y energia" --materia "Ind Extractivas" --top-k 5
```

Diagnosticar PDFs con poco texto extraible:

```bash
.venv/bin/python -m fiuba_local.cli \
  --root ~/dev/Facultad \
  ocr-check --materia "Ind Extractivas" --only-needs-ocr
```

## Desarrollo

Instala dependencias de desarrollo:

```bash
.venv/bin/python -m pip install -e ".[dev]"
```

Corre tests:

```bash
make PYTHON=.venv/bin/python test
```

## Docker

Uso opcional:

```bash
export FIUBA_MATERIAS_DIR=/ruta/a/tu/Facultad
export FIUBA_DATA_DIR=/ruta/a/tu/.fiuba_local
make docker-up
```

Luego abrir:

```text
http://127.0.0.1:8787
```

## Datos Locales

No se versionan:

- `.env`
- `.venv/`
- `.fiuba_local/`
- `Facultad/`
- bases SQLite
- caches y binarios locales

## Documentacion

- `docs/README.md`: estado, estrategia, prioridades y cambios recientes.
- `docs/prds/README.md`: registro y ciclo de vida de los PRD.
- `docs/prds/01_respuestas_con_fuentes/PRD.md`: producto actual.
- `docs/prds/02_cerebro_semantico/PRD.md`: experimento de embeddings y mapa semantico.
- `docs/prds/06_backlog/README.md`: oportunidades futuras.
- `docs/reference/EVAL_SET.md`: set de evaluacion.

Regla del proyecto: toda implementacion significativa debe actualizar
`docs/README.md` dentro del mismo cambio.

## Estructura

```text
fiuba-local-assistant/
├── activities/        # Prototipos pedagogicos autocontenidos
├── src/fiuba_local/
├── tests/
├── docs/
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── .env.example
└── pyproject.toml
```

Las actividades independientes y su forma de ejecucion estan catalogadas en
[`activities/README.md`](activities/README.md).
