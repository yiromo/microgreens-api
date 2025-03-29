from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
# from test.router import router as test_router
from auth.router import router as auth_router
from users.router import router as users_router

router = APIRouter(
    prefix="/api/v1"
)

# router.include_router(test_router)
router.include_router(auth_router)
router.include_router(users_router)