.PHONY: dev test lint migrate seed

dev:
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	python3 -m pytest

lint:
	python3 -m compileall app tests

migrate:
	alembic upgrade head

seed:
	python3 -m app.db.seed
