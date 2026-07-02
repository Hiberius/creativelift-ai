from pathlib import Path


def test_database_metadata_uses_sqlalchemy_models():
    repo = Path(__file__).resolve().parents[1]
    models_source = (repo / "app" / "db" / "models.py").read_text()
    expected_tables = {
        "organizations",
        "api_keys",
        "brand_packs",
        "claim_evidence",
        "briefs",
        "creative_treatments",
        "experiments",
        "events",
        "connectors",
        "audit_logs",
    }

    for table_name in expected_tables:
        assert f'__tablename__ = "{table_name}"' in models_source


def test_database_runtime_no_longer_uses_sqlmodel_metadata():
    repo = Path(__file__).resolve().parents[1]
    session_source = (repo / "app" / "db" / "session.py").read_text()
    base_source = (repo / "app" / "db" / "base.py").read_text()
    alembic_source = (repo / "alembic" / "env.py").read_text()
    migration_source = (repo / "alembic" / "versions" / "0001_initial_schema.py").read_text()

    assert not (repo / "app" / "models").exists()
    assert "sqlmodel" not in session_source.lower()
    assert "SQLModel" not in alembic_source
    assert "app.models.domain" not in base_source
    assert 'down_revision = None' in migration_source


def test_connector_database_shape_matches_api_schema():
    repo = Path(__file__).resolve().parents[1]
    models_source = (repo / "app" / "db" / "models.py").read_text()
    migration_source = (repo / "alembic" / "versions" / "0001_initial_schema.py").read_text()
    schema_source = (repo / "app" / "schemas" / "domain.py").read_text()

    assert "provider: str" in schema_source
    assert "display_name: str" in schema_source
    assert "provider: Mapped[str]" in models_source
    assert "display_name: Mapped[str]" in models_source
    assert 'sa.Column("provider"' in migration_source
    assert 'sa.Column("display_name"' in migration_source
    assert 'server_default="disconnected"' in migration_source


def test_modular_resource_tables_match_api_schemas():
    repo = Path(__file__).resolve().parents[1]
    models_source = (repo / "app" / "db" / "models.py").read_text()
    migration_source = (repo / "alembic" / "versions" / "0001_initial_schema.py").read_text()
    schema_source = (repo / "app" / "schemas" / "domain.py").read_text()

    for field in ["brief_id", "variables", "response", "input_tokens", "output_tokens"]:
        assert field in schema_source
        assert field in models_source
        assert f'sa.Column("{field}"' in migration_source

    for field in ["date_start", "date_end", "inputs", "outputs"]:
        assert field in schema_source
        assert field in models_source
        assert f'sa.Column("{field}"' in migration_source

    assert "experiment_id: UUID | None" in schema_source
    assert "experiment_id: Mapped[UUID | None]" in models_source
    assert 'sa.Column("experiment_id"' in migration_source
