from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import get_db
from app.models.user import User
from passlib.hash import bcrypt

router = APIRouter()

@router.post("/login/")
async def login(
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if not user or not bcrypt.verify(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    
    return {"message": "Login exitoso", "id": user.id, "username": user.username, "email": user.email}

@router.post("/registro/")
async def register_user(
    nombre: str = Form(...),
    apellido: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user:
        raise HTTPException(status_code=400, detail="El usuario ya existe")
    username = f"{nombre} {apellido}"
    password_hash = bcrypt.hash(password)
    new_user = User(username=username, email=email, password_hash=password_hash)
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {"message": "Usuario registrado", "id": new_user.id, "username": new_user.username, "email": new_user.email}