from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
# from test.router import router as test_router
from auth.router import router as auth_router
from users.router import router as users_router
from plants.router import router as plants_router
from seedbeds.router import router as seedbeds_router
from records.router import router as records_router
from integration.router import router as integration_router

router = APIRouter(
    prefix="/api/v1"
)

# router.include_router(test_router)
router.include_router(auth_router)
router.include_router(users_router)
router.include_router(plants_router)
router.include_router(seedbeds_router)
router.include_router(records_router)
router.include_router(integration_router)
