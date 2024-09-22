from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from schemas import UserCreate, UserLogin
from models import User
from utils import get_password_hash, verify_password, create_access_token
from dependencies import get_db
from datetime import timedelta

router = APIRouter()

from fastapi import Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError


@router.post("/register")
async def register(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Проверяем, существует ли уже пользователь с таким email
    existing_user = await db.execute(select(User).where(User.email == user.email))
    existing_user = existing_user.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User Already Exists!",
        )

    hashed_password = get_password_hash(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password, name=user.name, tag=user.tag)

    try:
        db.add(new_user)
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Не удалось создать пользователя. Возможно, произошла ошибка базы данных.",
        )

    access_token = create_access_token(data={"sub": str(new_user.id)}, expires_delta=timedelta(minutes=30))
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    user_in_db = await db.scalar(select(User).where(User.email == user.email))
    if not user_in_db or not verify_password(user.password, user_in_db.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Incorrect email or password")

    access_token = create_access_token(data={"sub": str(user_in_db.id)}, expires_delta=timedelta(minutes=30))
    return {"access_token": access_token, "token_type": "bearer"}
