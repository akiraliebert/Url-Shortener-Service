from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from app.services.url_service import create_short_url, get_original_url, increment_click_db, get_url_stats, delete_url
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.url import URLCreate
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.status import HTTP_404_NOT_FOUND, HTTP_422_UNPROCESSABLE_ENTITY
from fastapi.exceptions import RequestValidationError
from app.api.deps import get_current_admin
from app.core.redis_client import get_redis
from app.services.redis_service import cache_url, get_cached_url, reset_cached_url, increment_click_redis, get_stats, reset_stats

router = APIRouter()

@router.post('/shorten')
async def create_short(payload: URLCreate, db: AsyncSession = Depends(get_db), redis = Depends(get_redis)):
    try:
        new_url = await create_short_url(db=db, original_url=str(payload.original_url))
        await cache_url(redis, new_url.short_code, new_url.original_url)
        return {
            "original_url": new_url.original_url,
            "short_code": new_url.short_code,
            "short_url": f"http://localhost:8000/{new_url.short_code}",
        }
    except RequestValidationError as e:
        return JSONResponse(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "error": "Invalid request data",
                "details": e,
            },
        )

@router.get("/{short_code}", response_class=RedirectResponse, status_code=302)
async def redirect_to_original(short_code: str, background_tasks: BackgroundTasks,
                               db: AsyncSession = Depends(get_db), redis = Depends(get_redis)):
    # 1️⃣ Пробуем взять URL из кэша
    original_url = await get_cached_url(redis, short_code)

    # 2️⃣ Если нет в кэше — достаём из БД и кладём в Redis
    if not original_url:
        original_url = await get_original_url(db=db, short_code=short_code)
        if not original_url:
            raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Short URL not found")
        await cache_url(redis, short_code, original_url)

    # 3️⃣ Обновляем статистику (Redis + фоновой апдейт в БД)
    await increment_click_redis(redis, short_code)
    background_tasks.add_task(increment_click_db, db, short_code)

    # 4️⃣ Возвращаем редирект
    return RedirectResponse(url=original_url)


@router.get("/stats/{short_code}")
async def redirect_to_original(short_code: str, db: AsyncSession = Depends(get_db), redis = Depends(get_redis)):
    stats_redis = await get_stats(redis, short_code)
    stats = await get_url_stats(db=db, short_code=short_code)
    if not stats:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Short URL not found")
    return {
        "original_url": stats.original_url,
        "short_code": stats.short_code,
        "clicks": stats_redis['clicks'] if stats_redis else stats.clicks,
        "created_at": stats.created_at,
        "last_accessed": stats_redis['last_accessed'] if stats_redis else stats.last_accessed,
    }

@router.delete("/{short_code}")
async def delete_short_url(
    short_code: str,
    db: AsyncSession = Depends(get_db),
    current_admin: str = Depends(get_current_admin),
    redis = Depends(get_redis)
):
    result = await delete_url(db=db, short_code=short_code)
    if not result:
        raise HTTPException(status_code=404, detail="URL not found")
    await reset_cached_url(redis_client=redis, short_code=short_code)
    await reset_stats(redis_client=redis, short_code=short_code)
    return {"message": f"URL {short_code} deleted by {current_admin}"}

