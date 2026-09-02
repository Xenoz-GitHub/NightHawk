"""SQLAlchemy database engine and session management."""

from sqlalchemy import create_engine, pool
from sqlalchemy.orm import sessionmaker, declarative_base, scoped_session
from sqlalchemy.exc import SQLAlchemyError

from nighthawk.config.config import get_config
from nighthawk.core.exceptions import DatabaseError

Base = declarative_base()

_engine = None
_session_factory = None


def _make_engine(url: str):
    """Build a SQLAlchemy engine for the given URL (pool only for server DBs)."""
    return create_engine(
        url,
        echo=False,
        poolclass=pool.QueuePool if url.startswith(("postgresql", "postgres")) else pool.NullPool,
        future=True,
    )


def init_database() -> None:
    """Initialize the SQLAlchemy engine and session factory from config."""
    global _engine, _session_factory
    cfg = get_config()
    url = cfg.database_url
    try:
        _engine = _make_engine(url)
        _session_factory = sessionmaker(bind=_engine, expire_on_commit=False)
    except SQLAlchemyError as exc:
        raise DatabaseError(f"Failed to initialize database: {exc}") from exc


def create_all() -> None:
    """Create all tables if they do not exist (dev/bootstrap convenience)."""
    global _engine
    if _engine is None:
        init_database()
    Base.metadata.create_all(_engine)


def reset_engine() -> None:
    """Dispose and forget engine + session factory (used by tests)."""
    global _engine, _session_factory
    if _engine is not None:
        try:
            _engine.dispose()
        except Exception:  # pragma: no cover - dispose is best-effort
            pass
    _engine = None
    _session_factory = None


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
