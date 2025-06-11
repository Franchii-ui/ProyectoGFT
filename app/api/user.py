from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.ext.asyncio import AsyncSession
from app.db import get_db
from app.models.user import User

router = APIRouter()

@router.post("/register/")
async def register_user(
    nombre: str = Form(...),
    apellido: str = Form(...),
    email: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    user = User(username=f"{nombre} {apellido}", email=email)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return {"id": user.id, "username": user.username, "email": user.email}