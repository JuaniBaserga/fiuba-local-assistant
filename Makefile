PYTHON ?= python3
PORT ?= 8787

.PHONY: install test run docker-up docker-down

install:
	$(PYTHON) -m pip install -e .

test:
	PYTHONPATH=src $(PYTHON) -m pytest -q

run:
	PYTHONPATH=src $(PYTHON) -m fiuba_local.cli serve --host 127.0.0.1 --port $(PORT)

docker-up:
	docker compose up --build

docker-down:
	docker compose down
