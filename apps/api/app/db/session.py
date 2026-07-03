from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.db.models import Base
from app.db.tenant import current_organization_id

settings = get_settings()
connect_args = {"check_same_thread": False} if settings.database_url.startswith("sqlite") else {}
engine: Engine = create_engine(settings.database_url, echo=settings.debug, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, class_=Session)

if engine.dialect.name == "postgresql":

    @event.listens_for(engine, "begin")
    def _set_tenant_guc(connection) -> None:
        organization_id = current_organization_id.get()
        if organization_id is not None:
            # SET LOCAL: scoped to this transaction, powers the RLS policies.
            connection.exec_driver_sql(
                "SELECT set_config('app.organization_id', %(org)s, true)",
                {"org": organization_id},
            )


def get_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session


def create_db_and_tables() -> None:
    Base.metadata.create_all(bind=engine)
