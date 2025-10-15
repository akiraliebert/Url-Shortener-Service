import redis.asyncio as redis
from fastapi import FastAPI, Request

async def init_redis(app: FastAPI, redis_url: str):
    """Создаём подключение и кладём его в app.state"""
    app.state.redis = await redis.from_url(
        redis_url,
        encoding="utf-8",
        decode_responses=True
    )

async def get_redis(request: Request):
    """Достаём клиента из состояния приложения"""
    return request.app.state.redis
