import contextlib
from typing import AsyncIterator, Self

from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import declarative_base

import app.settings as settings

Base = declarative_base()


async def init_db():
    """
    Create all tables that don't already exist
    """
    async with DbSessionManager(settings.DATABASE_URL).connect() as connection:
        await connection.run_sync(Base.metadata.create_all)


class DbSessionManager:
    def __new__(cls, *args, **kwargs) -> Self:
        if not hasattr(cls, "_sessionmanager"):
            cls._sessionmanager = super(DbSessionManager, cls).__new__(cls)
        return cls._sessionmanager

    def __init__(self, host: str) -> None:
        self._engine = create_async_engine(host, echo=True)
        self._sessionmaker = async_sessionmaker(
            bind=self._engine, autocommit=False, autoflush=False
        )

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        """
        Provides an asynchronous context manager for database connections.
        """
        if self._engine is None:
            raise Exception("DbSessionManager is not initialized")
        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """
        Provides an asynchronous context manager for database sessions.
        """
        if self._sessionmaker is None:
            raise Exception("DbSessionManager is not initialized")
        session = self._sessionmaker()
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def close(self) -> None:
        """
        Closes the database engine and cleans up resources.
        """
        if self._engine is None:
            raise Exception("DbSessionManager is not initialized")
        await self._engine.dispose()

        self._engine = None
        self._sessionmaker = None

    def get_engine(self) -> AsyncEngine | None:
        """
        Retrieves the current database engine.
        """
        return self._engine


sessionmanager = DbSessionManager(settings.DATABASE_URL)


async def get_db_session():
    """
    Provides an asynchronous database session.
    """
    async with sessionmanager.session() as session:
        yield session
