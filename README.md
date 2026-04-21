# FIUBA Local Assistant

Asistente de estudio FIUBA para indexar materiales locales y consultar desde CLI o UI web.

## Que trae este repo

- Indexado incremental por materia en SQLite + FTS5.
- Busqueda local de fragmentos relevantes.
- Respuesta con Ollama local o APIs cloud (OpenAI/Gemini).
- UI web local en `http://127.0.0.1:8787`.
- Modulo de planificacion de estudio y exportacion a calendario.

## Requisitos

- Python 3.10+.
- `pip`.
- Opcional: Ollama para modo local.
- Opcional: Docker + Docker Compose.

## Configuracion

1. Copia variables de entorno:

```bash
cp .env.example .env
```

2. Completa solo lo que necesites en `.env`:

- `OPENAI_API_KEY` para motor OpenAI.
- `GEMINI_API_KEY` para motor Gemini.
- `FIUBA_ROOT`, `FIUBA_STATE_DIR`, `FIUBA_DB_PATH` son opcionales.

Defaults si no defines rutas:

- `FIUBA_ROOT=~/dev/Facultad`
- `FIUBA_STATE_DIR=~/.fiuba_local`
- `FIUBA_DB_PATH=~/.fiuba_local/index.db`

## Uso local (sin Docker)

Instalacion editable:

```bash
python3 -m pip install -e .
```

Opcional para extraer mejor texto de PDF:

```bash
python3 -m pip install pypdf
```

Comandos principales:

```bash
# Indexar una materia
PYTHONPATH=src python3 -m fiuba_local.cli index --materia "Ind Extractivas"

# Buscar
PYTHONPATH=src python3 -m fiuba_local.cli ask "balance de masa y energia" --materia "Ind Extractivas" --top-k 5

# Levantar UI web
PYTHONPATH=src python3 -m fiuba_local.cli serve --host 127.0.0.1 --port 8787
```

Tambien puedes usar `make`:

```bash
make install
make test
make run
```

## Uso con Docker

1. Define carpetas en variables de entorno (opcional). Si no lo haces, usa `./Facultad` y `./.fiuba_local` dentro del repo.

```bash
export FIUBA_MATERIAS_DIR=/ruta/a/tu/Facultad
export FIUBA_DATA_DIR=/ruta/a/tu/.fiuba_local
```

2. Levanta el servicio:

```bash
make docker-up
```

3. Abre la UI en:

```text
http://127.0.0.1:8787
```

Nota de Ollama en Docker:

- El compose apunta por defecto a `http://host.docker.internal:11434`.
- En Linux, puede requerir ajustar `OLLAMA_HOST` manualmente.

## Datos que NO se versionan

Este repo ignora por defecto:

- `.env`
- `.venv`
- `.fiuba_local/`
- `Facultad/`
- archivos de cache y binarios locales

## Estructura

```text
fiuba-local-assistant/
├── src/fiuba_local/
├── tests/
├── docs/
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── .env.example
└── pyproject.toml
```

## Publicar en GitHub

```bash
cd /ruta/a/fiuba-local-assistant
git init
git add .
git commit -m "chore: prepare project for sharing (docker + docs)"
```

Luego crea repo remoto y sube:

```bash
git branch -M main
git remote add origin https://github.com/<usuario>/<repo>.git
git push -u origin main
```
