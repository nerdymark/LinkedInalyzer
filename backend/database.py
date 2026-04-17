from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from backend.config import load_config


class Base(DeclarativeBase):
    pass


def get_engine():
    config = load_config()
    db_path = config.get("database_path", "linkedinalyzer.db")
    return create_engine(f"sqlite:///{db_path}", echo=False)


def get_session_factory():
    engine = get_engine()
    return sessionmaker(bind=engine)


def init_db():
    from backend import models  # noqa: F401 - ensure models are registered

    engine = get_engine()
    Base.metadata.create_all(engine)
    return engine
