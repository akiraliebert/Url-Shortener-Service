from pydantic import BaseModel, HttpUrl

class URLCreate(BaseModel):
    original_url: HttpUrl


class URLInfo(BaseModel):
    id: int
    short_code: str
    original_url: HttpUrl
    clicks: int

    class Config:
        from_attributes = True  # позволяет строить схему прямо из SQLAlchemy модели