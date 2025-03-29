from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import TokenRead
from .services import AuthService, get_auth_service
from users.schemas import UserCreate, UserLogin
from database import get_db
from users.models import Users
from utils.token import get_token

router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

@router.post("/login/", response_model=TokenRead)
async def login(
    user: UserLogin,
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.authenticate_user(user.email, user.password)
    tokens = await auth_service.create_tokens(user)
    return tokens

@router.post("/register/", response_model=TokenRead)
async def register(
    user: UserCreate,
    auth_service: AuthService = Depends(get_auth_service),
):
    user = await auth_service.register_user(
        email=user.email, 
        username=user.username,  
        password=user.password,
    )
    tokens = await auth_service.create_tokens(user)
    return tokens

@router.post("/refresh/", response_model=TokenRead)
async def refresh(
    refresh_token: str,
    auth_service: AuthService = Depends(get_auth_service),
):
    tokens = await auth_service.refresh_tokens(refresh_token)
    return tokens

@router.get("/me/", response_model=dict)
async def get_me(
    token: str = Depends(get_token),  
    auth_service: AuthService = Depends(get_auth_service),
):
    current_user: Users = await auth_service.get_current_user(token)  
    return {
        "email": current_user.email,
        "username": current_user.username,
        "is_superuser": current_user.is_superuser,
    }