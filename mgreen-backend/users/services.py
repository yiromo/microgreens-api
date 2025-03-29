from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import UserRead
from typing import List
from database import get_db
from utils.token import get_token
from .models import Users
from sqlalchemy.sql import text
from auth.services import AuthService, get_auth_service

class UserService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_users(self, page: int = 1, limit: int = 10):
        offset = (page - 1) * limit
        result = await self.db.execute(
            text("SELECT * FROM users LIMIT :limit OFFSET :offset"),
            {"limit": limit, "offset": offset},
        )
        users = result.fetchall()
        return [
            Users(
                id=user[0],
                email=user[1],
                username=user[2],
                password=user[3],
                is_active=user[4],
                is_superuser=user[5],
                user_type_id=user[6],
            )
            for user in users
        ]

    async def get_user_type(self, user_type_id: str):
        result = await self.db.execute(
            text("SELECT user_type FROM user_type WHERE id = :user_type_id"),
            {"user_type_id": user_type_id},
        )
        user_type_row = result.fetchone()
        if not user_type_row:
            return None
        return user_type_row[0]  

async def get_user_service(db: AsyncSession = Depends(get_db)):
    return UserService(db)