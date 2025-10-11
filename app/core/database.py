from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,        # можно True для отладки
    future=True,
    pool_pre_ping=True
)


# 2. Базовый класс моделей
class Base(DeclarativeBase):
    pass


# 3. Фабрика сессий
async_session_maker = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)


# 4. Dependency для FastAPI
async def get_db() -> AsyncSession:
    """Dependency для DI в FastAPI маршрутах."""
    async with async_session_maker() as session:
        yield session
