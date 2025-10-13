from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Admin(Base):
    __tablename__ = "admins"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
