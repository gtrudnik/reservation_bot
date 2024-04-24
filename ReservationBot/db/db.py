from asyncio import current_task, run
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_scoped_session
from ReservationBot.config import settings


DB = (f"{settings.db_driver}://{settings.postgres_user}:{settings.postgres_password}@{settings.postgres_host}:"
      f"{settings.postgres_port}/{settings.postgres_db}")
engine = create_async_engine(DB, echo=True)
Base = declarative_base()
_async_session_factory = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)  # type: ignore[call-overload]
_async_session = async_scoped_session(_async_session_factory, current_task)


async def get_session() -> AsyncSession:
    """Function for getting AsyncSession"""
    async with _async_session() as session:
        return session
