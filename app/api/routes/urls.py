from fastapi import APIRouter, Depends
from app.services.url_service import create_short_url
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.schemas.url import URLCreate, URLInfo

router = APIRouter()

@router.post('/shorten')
async def create_short(payload: URLCreate, db: AsyncSession = Depends(get_db)):
    new_url = await create_short_url(db=db, original_url=str(payload.original_url))
    return new_url
