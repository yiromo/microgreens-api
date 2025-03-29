from fastapi import APIRouter, Request, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from .schemas import *
from typing import List
from database import get_db
from utils.token import get_token
from .services import get_user_service, UserService
from .models import *
from auth.services import AuthService, get_auth_service

router = APIRouter(
    prefix="/users",
    tags=["Users"],
    dependencies=[Depends(get_token)]
)

@router.get("/", response_model=List[UserRead])
async def get_all_users(
    page: int = 1,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    user_service: UserService = Depends(get_user_service),
    auth_service: AuthService = Depends(get_auth_service),
    token: str = Depends(get_token),
):
    """
    ONLY ADMIN AND SUPERADMIN CAN ACCESS THIS ENDPOINT
    """
    current_user = await auth_service.get_current_user(token)
    current_user_type = await user_service.get_user_type(str(current_user.user_type_id))
    
    if current_user_type not in ["admin", "superadmin"]:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    users = await user_service.get_all_users(page, limit)
    user_reads = []
    for user in users:
        user_type = await user_service.get_user_type(str(user.user_type_id))
        user_reads.append(
            UserRead(
                id=str(user.id),
                email=user.email,
                username=user.username,
                is_active=user.is_active,
                is_superuser=user.is_superuser,
                user_type=user_type or "user",
            )
        )
    return user_reads

@router.get("/me", response_model=UserRead)
async def get_me_profile(
    token: str = Depends(get_token),
    auth_service: AuthService = Depends(get_auth_service),
    user_service: UserService = Depends(get_user_service),
):
    current_user: Users = await auth_service.get_current_user(token)
    if not current_user:
        raise HTTPException(status_code=401, detail="User not found")
    
    user_type = await user_service.get_user_type(str(current_user.user_type_id))
    if not user_type:
        raise HTTPException(status_code=404, detail="User type not found")
    
    user = UserRead(
        id=str(current_user.id),
        email=current_user.email,
        username=current_user.username,
        is_superuser=current_user.is_superuser,
        is_active=current_user.is_active,
        user_type=user_type,  
    )
    return user

@router.post("/user-type/", response_model=UserRead)
async def create_user_type(user_type: UserTypeCreate):
    """
    ONLY SUPERADMIN CAN ACCESS THIS ENDPOINT
    """
    pass

@router.get("/user-type/")
async def get_user_type(db: AsyncSession = Depends(get_db)):
    """
    ONLY SUPERADMIN CAN ACCESS THIS ENDPOINT
    """
    pass