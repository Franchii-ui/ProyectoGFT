from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db import get_db
from app.models.user import User
from passlib.hash import bcrypt

router = APIRouter()

@router.post("/login/")
async def login_or_register(
    nombre: str = Form(None),
    apellido: str = Form(None),
    email: str = Form(...),
    password: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()

    if user:
        # User exists, check password
        if not bcrypt.verify(password, user.password_hash):
            raise HTTPException(status_code=401, detail="Contraseña incorrecta")
        return {"message": "Login exitoso", "id": user.id, "username": user.username, "email": user.email}
    else:
        # Register new user
        if not nombre or not apellido:
            raise HTTPException(status_code=400, detail="Faltan nombre o apellido para registro")
        username = f"{nombre} {apellido}"
        password_hash = bcrypt.hash(password)
        new_user = User(username=username, email=email, password_hash=password_hash)
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        return {"message": "Usuario registrado", "id": new_user.id, "username": new_user.username, "email": new_user.email}