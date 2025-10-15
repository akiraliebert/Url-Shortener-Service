import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.main import app
from app.core.database import get_db, Base
from app.core.security import create_access_token
from app.core.redis_client import get_redis

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

engine = create_async_engine(TEST_DATABASE_URL, future=True)
TestingSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


# ======= БАЗА =======
@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ======= FAKE REDIS =======
class FakeRedis:
    def __init__(self):
        self.store = {}
        self.expiry = {}

    async def get(self, key):
        return self.store.get(key)

    async def set(self, key, value, ex=None):
        self.store[key] = value

    async def incr(self, key):
        self.store[key] = str(int(self.store.get(key, "0")) + 1)
        return self.store[key]

    async def hgetall(self, key):
        return self.store.get(key, {})

    async def hset(self, key, *args, **kwargs):
        """Поддерживает hset(key, field, value) и hset(key, mapping={...})"""
        hash_val = self.store.setdefault(key, {})

        if len(args) == 2:  # вариант (key, field, value)
            field, value = args
            hash_val[field] = value
        elif "mapping" in kwargs:
            hash_val.update(kwargs["mapping"])
        else:
            raise TypeError("Invalid arguments for hset()")

        self.store[key] = hash_val
        return True

    async def hincrby(self, key, field, amount=1):
        """Имитация увеличения значения внутри хэша Redis."""
        hash_val = self.store.setdefault(key, {})
        current = int(hash_val.get(field, 0))
        hash_val[field] = current + amount
        self.store[key] = hash_val
        return hash_val[field]

    async def expire(self, key, seconds):
        """Имитация установки TTL."""
        self.expiry[key] = seconds
        return True

    async def delete(self, key):
        self.store.pop(key, None)

    async def close(self):
        pass


@pytest_asyncio.fixture
async def fake_redis():
    redis = FakeRedis()
    yield redis
    await redis.close()


# ======= CLIENT =======
@pytest_asyncio.fixture
async def client(fake_redis):
    async def override_get_db():
        async with TestingSessionLocal() as session:
            yield session

    async def override_get_redis():
        return fake_redis

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_redis] = override_get_redis

    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
def test_token():
    return create_access_token({"sub": "test_user"})
