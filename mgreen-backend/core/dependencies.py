from sqlalchemy.ext.asyncio import AsyncSession
from database import get_db
from utils.token import get_token
from auth.services import AuthService, get_auth_service
from fastapi import Depends

class CommonDependencies:
    def __init__(
        self,
        db: AsyncSession = Depends(get_db),
        auth_service: AuthService = Depends(get_auth_service),
        token: str = Depends(get_token)
    ):
        self.db = db
        self.auth_service = auth_service
        self.token = token

