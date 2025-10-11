import string
import random
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.url import URL

# Алфавит base62
BASE62_ALPHABET = string.digits + string.ascii_lowercase + string.ascii_uppercase  # 0-9a-zA-Z
BASE = 62

async def create_short_url(db: AsyncSession, original_url: str) -> URL:
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


def generate_short_code(id_: int, existing_codes: set) -> str:
    """
    Генерирует короткий код по ID с проверкой коллизий.
    existing_codes — это множество уже занятых кодов.
    """
    short_code = encode_base62(id_)

    # Если коллизия — добавляем случайный символ до тех пор, пока код не станет уникальным
    while short_code in existing_codes:
        short_code += random.choice(BASE62_ALPHABET)

    return short_code
