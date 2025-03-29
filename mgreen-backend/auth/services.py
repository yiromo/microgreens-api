from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import text
from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from datetime import timedelta
from database import get_db
from users.models import Users, UserTypeEnum
from utils.token import create_access_token, verify_token, get_token
from core.config import settings

class AuthService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def _get_user_by_email(self, email: str) -> Users:
        user_result = await self.db.execute(
            text("SELECT * FROM users WHERE email = :email"),
            {"email": email},
        )
        user = user_result.fetchone()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return Users(
            id=user[0],
            email=user[1],
            username=user[2],
            password=user[3],
            is_active=user[4],
            is_superuser=user[5],
            user_type_id=user[6],
        )
    
    async def _get_user_by_id(self, id: str) -> Users:
        user_result = await self.db.execute(
            text("SELECT * FROM users WHERE id = :id"),
            {"id": id},
        )
        user = user_result.fetchone()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return Users(
            id=user[0],
            email=user[1],
            username=user[2],
            password=user[3],
            is_active=user[4],
            is_superuser=user[5],
            user_type_id=user[6],
        )

    async def authenticate_user(self, email: str, password: str) -> Users:
        user = await self._get_user_by_email(email)
        if not self.pwd_context.verify(password, user.password):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        return user

    async def register_user(self, email: str, username: str, password: str) -> Users:
        existing_user = await self.db.execute(
            text("SELECT email FROM users WHERE email = :email"),
            {"email": email},
        )
        if existing_user.fetchone():
            raise HTTPException(status_code=400, detail="Email already registered")

        user_type_result = await self.db.execute(
            text("SELECT id FROM user_type WHERE user_type = :type"),
            {"type": UserTypeEnum.USER.value},
        )
        user_type = user_type_result.fetchone()
        if not user_type:
            raise HTTPException(status_code=500, detail="User role not found")

        hashed_password = self.pwd_context.hash(password)
        new_user = Users(
            email=email,
            username=username,
            password=hashed_password,
            is_active=True,
            is_superuser=False,
            user_type_id=user_type[0],
        )
        self.db.add(new_user)
        await self.db.commit()
        await self.db.refresh(new_user)
        return new_user

    async def create_tokens(self, user: Users) -> dict:
        access_token = await create_access_token(data={"sub": str(user.id)})
        refresh_token = await create_access_token(
            data={"sub": str(user.id), "type": "refresh"},
            expires_delta=timedelta(days=7),
        )
        return {"access_token": access_token, "refresh_token": refresh_token}

    async def refresh_tokens(self, refresh_token: str) -> dict:
        payload = await verify_token(refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token",
            )
        id = payload.get("sub")
        if not id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
        
        user = await self._get_user_by_id(id)
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        return await self.create_tokens(user)

    async def get_current_user(self, token: str) -> Users:
        payload = await verify_token(token)
        id = payload.get("sub")
        if not id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return await self._get_user_by_id(id)

async def get_auth_service(db: AsyncSession = Depends(get_db)):
    return AuthService(db)

async def get_current_active_user(
    token: str = Depends(get_token),
    auth_service: AuthService = Depends(get_auth_service),
) -> Users:
    user = await auth_service.get_current_user(token)
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

async def get_current_superuser(
    token: str = Depends(get_token),
    auth_service: AuthService = Depends(get_auth_service),
) -> Users:
    user = await auth_service.get_current_user(token)
    if not user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
    return user