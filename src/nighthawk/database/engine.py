"""SQLAlchemy database engine and session management."""

from sqlalchemy import create_engine, pool
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
from sqlalchemy.exc import SQLAlchemyError

from nighthawk.config.config import get_config
from nighthawk.core.exceptions import DatabaseError

Base = declarative_base()

_engine = None
_session_factory = None


def init_database() -> None:
    """Initialize the SQLAlchemy engine and session factory from config."""
    global _engine, _session_factory
    cfg = get_config()
    url = cfg.database_url
    echo = cfg.db_echo
    pool_size = cfg.db_pool_size
    max_overflow = cfg.db_max_overflow
    try:
        _engine = create_engine(
            url,
            echo=echo,
            poolclass=pool.QueuePool if url.startswith("postgresql") else pool.NullPool,
            pool_size=pool_size,
            max_overflow=max_overflow,
            future=True,
        )
        _session_factory = sessionmaker(bind=_engine, expire_on_commit=False)
    except SQLAlchemyError as exc:
        raise DatabaseError(f"Failed to initialize database: {exc}") from exc


def get_session():
    """Return a new database session."""
    if _session_factory is None:
        init_database()
    return _session_factory()


def get_engine():
    """Return the engine instance."""
    if _engine is None:
        init_database()
    return _engine
