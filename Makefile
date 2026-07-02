.PHONY: setup dev test test-sqlalchemy migration-smoke verify-light lint api-dev api-test web-dev web-build web-lint

setup:
	npm install
	python3 -m pip install -e apps/api -e services/experiment-engine -e services/bandit-service -e services/uplift-service -e services/mmm-service

dev:
	docker compose up --build

test:
	python3 -m pytest
	npm --workspace apps/web run test

test-sqlalchemy:
	@python3 -c "import sqlalchemy" 2>/dev/null || (echo 'sqlalchemy missing: run python3 -m pip install sqlalchemy alembic "psycopg[binary]"' && exit 1)
	python3 -m pytest -m sqlalchemy -v

migration-smoke:
	docker compose up -d --wait postgres
	CREATIVELIFT_MIGRATION_TEST_DATABASE_URL=postgresql+psycopg://creativelift:creativelift_dev@localhost:5432/creativelift \
		python3 -m pytest apps/api/tests/test_migrations.py -v

verify-light:
	python3 -m compileall -q apps/api services connectors packages/sdk-python
	python3 -m pytest
	npm --workspace apps/web run test

lint:
	python3 -m compileall -q apps/api services connectors packages/sdk-python
	npm --workspace apps/web run lint

api-dev:
	cd apps/api && make dev

api-test:
	cd apps/api && make test

web-dev:
	npm --workspace apps/web run dev

web-build:
	npm --workspace apps/web run build

web-lint:
	npm --workspace apps/web run lint
