PYTHON ?= python3

.PHONY: install install-backend install-frontend backend frontend dev init-db load-codebook ingest preprocess start-run analyze export demo test test-backend test-frontend build build-frontend docker-build clean

install: install-backend install-frontend

install-backend:
	$(PYTHON) -m pip install -e ".[test]"

install-frontend:
	npm --prefix web install

backend:
	uvicorn app.api:app --host $${BACKEND_HOST:-127.0.0.1} --port $${BACKEND_PORT:-8000} --reload

frontend:
	npm --prefix web run dev

dev:
	$(MAKE) backend & $(MAKE) frontend

init-db:
	$(PYTHON) -m app.cli.commands init-db

load-codebook:
	$(PYTHON) -m app.cli.commands load-codebook --path app/codebook/examples/codebook.example.yml

ingest:
	$(PYTHON) -m app.cli.commands ingest --path data/raw/demo_conversations.csv --format csv

preprocess:
	$(PYTHON) -m app.cli.commands preprocess --strategy turn

start-run:
	$(PYTHON) -m app.cli.commands start-run --codebook-version 0.1.0 --run-name demo

analyze:
	$(PYTHON) -m app.cli.commands analyze --run-id 1

export:
	$(PYTHON) -m app.cli.commands export --run-id 1 --format markdown --out data/exports/demo_report.md

demo: init-db load-codebook ingest preprocess start-run analyze export

reliability:
	$(PYTHON) -m app.cli.commands reliability --run-id 1

test: test-backend test-frontend

test-backend:
	$(PYTHON) -m pytest

test-frontend:
	npm --prefix web run test

build: build-frontend

build-frontend:
	npm --prefix web run build

docker-build:
	docker compose build

clean:
	rm -f data/thematic_analysis.db data/exports/demo_report.md
