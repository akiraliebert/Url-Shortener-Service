from fastapi import APIRouter, Depends, HTTPException
from app.services.url_service import create_short_url, get_original_url_and_increment_clicks, get_url_stats, delete_url
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.url import URLCreate
from fastapi.responses import RedirectResponse, JSONResponse
from starlette.status import HTTP_404_NOT_FOUND, HTTP_422_UNPROCESSABLE_ENTITY
from fastapi.exceptions import RequestValidationError
from app.api.deps import get_current_admin

router = APIRouter()

@router.post('/shorten')
async def create_short(payload: URLCreate, db: AsyncSession = Depends(get_db)):
    try:
        new_url = await create_short_url(db=db, original_url=str(payload.original_url))
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
async def redirect_to_original(short_code: str, db: AsyncSession = Depends(get_db)):
    original_url = await get_original_url_and_increment_clicks(db=db, short_code=short_code)
    if not original_url:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Short URL not found")

    return RedirectResponse(url=original_url)


@router.get("/stats/{short_code}")
async def redirect_to_original(short_code: str, db: AsyncSession = Depends(get_db)):
    stats = await get_url_stats(db=db, short_code=short_code)
    if not stats:
        raise HTTPException(status_code=HTTP_404_NOT_FOUND, detail="Short URL not found")

    return {
        "original_url": stats.original_url,
        "short_code": stats.short_code,
        "clicks": stats.clicks,
        "created_at": stats.created_at,
        "last_accessed": stats.last_accessed,
    }

@router.delete("/{short_code}")
async def delete_short_url(
    short_code: str,
    db: AsyncSession = Depends(get_db),
    current_admin: str = Depends(get_current_admin)
):
    result = await delete_url(db=db, short_code=short_code)
    if not result:
        raise HTTPException(status_code=404, detail="URL not found")

    return {"message": f"URL {short_code} deleted by {current_admin}"}

