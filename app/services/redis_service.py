from datetime import datetime
from app.core.config import settings

async def cache_url(redis_client, short_code, original_url):
    await redis_client.set(f"url:{short_code}", original_url, ex=settings.REDIS_TTL)


# достать урл из кеша
async def get_cached_url(redis_client, short_code):
    return await redis_client.get(f"url:{short_code}")

async def reset_cached_url(redis_client, short_code):
    await redis_client.delete(f"url:{short_code}")

# получить статистику
async def get_stats(redis_client, short_code):
    stats = await redis_client.hgetall(f"stats:{short_code}")
    if not stats:
        return None
    return stats

# обновить статистику
async def increment_click_redis(redis_client, short_code):
    stats_key = f"stats:{short_code}"
    await redis_client.hincrby(stats_key, "clicks", 1)
    await redis_client.hset(
        stats_key,
        "last_accessed",
        datetime.now().isoformat()
    )
    await redis_client.expire(stats_key, settings.REDIS_TTL)


async def reset_stats(redis_client, short_code: str):
    await redis_client.delete(f"stats:{short_code}")