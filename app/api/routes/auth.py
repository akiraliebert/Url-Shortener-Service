from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.admin import Admin
from app.schemas.admin import AdminCreate, AdminLogin, Token
from app.core.security import get_password_hash, verify_password, create_access_token
from sqlalchemy import select
from datetime import timedelta
from app.core.config import settings

router = APIRouter()

@router.post("/register", response_model=Token)
async def register(admin_data: AdminCreate, db: AsyncSession = Depends(get_db)):
    existing_user = await db.execute(select(Admin).where(Admin.username == admin_data.username))
    if existing_user.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Username already taken")
    
    admin = Admin(
        username=admin_data.username,
        hashed_password=get_password_hash(admin_data.password)
    )
    db.add(admin)
    await db.commit()
    await db.refresh(admin)

    access_token = create_access_token({"sub": admin.username}, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
async def login(admin_data: AdminLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Admin).where(Admin.username == admin_data.username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(admin_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token({"sub": user.username}, timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}
