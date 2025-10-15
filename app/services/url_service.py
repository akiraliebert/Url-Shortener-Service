import string
import random
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.url import URL
from sqlalchemy import select, update, func

# Алфавит base62
BASE62_ALPHABET = string.digits + string.ascii_lowercase + string.ascii_uppercase  # 0-9a-zA-Z
BASE = 62

async def create_short_url(db: AsyncSession, original_url: str) -> URL:
    existing = await db.execute(select(URL).where(URL.original_url == original_url))
    existing_url = existing.scalar_one_or_none()

    if existing_url:
        return existing_url  # возвращаем уже существующий short_code


    url = URL(original_url=original_url)
    db.add(url)
    await db.flush()  # id уже доступен

    url.short_code = await encode_base62(url.id)
    await db.commit()
    await db.refresh(url)
    return url

async def encode_base62(num: int) -> str:
    """Преобразует целое число в base62 строку."""
    if num == 0:
        return BASE62_ALPHABET[0]

    encoded = []
    while num > 0:
        num, remainder = divmod(num, BASE)
        encoded.append(BASE62_ALPHABET[remainder])
    return ''.join(reversed(encoded))


async def generate_short_code(id_: int, existing_codes: set) -> str:
    """
    Генерирует короткий код по ID с проверкой коллизий.
    existing_codes — это множество уже занятых кодов.
    """
    short_code = encode_base62(id_)

    # Если коллизия — добавляем случайный символ до тех пор, пока код не станет уникальным
    while short_code in existing_codes:
        short_code += random.choice(BASE62_ALPHABET)

    return short_code

async def increment_click_db(db: AsyncSession, short_code: str):
    stmt = (
        update(URL)
        .where(URL.short_code == short_code)
        .values(
            clicks=URL.clicks + 1,
            last_accessed=func.now()
        )
    )
    await db.execute(stmt)
    await db.commit()

async def get_original_url(db: AsyncSession, short_code: str) -> str | None:
    result = await db.execute(select(URL).where(URL.short_code == short_code))
    url_obj = result.scalar_one_or_none()

    if not url_obj:
        return None

    return url_obj.original_url

async def get_url_stats(db: AsyncSession, short_code: str) -> URL | None:
    """Возвращает статистику по короткой ссылке."""
    result = await db.execute(select(URL).where(URL.short_code == short_code))
    url_obj = result.scalar_one_or_none()

    return url_obj

async def delete_url(db: AsyncSession, short_code: str) -> str | None:
    result = await db.execute(select(URL).where(URL.short_code == short_code))
    url_obj = result.scalar_one_or_none()
    if not url_obj:
        return None

    await db.delete(url_obj)
    await db.commit()
    return 'success'
