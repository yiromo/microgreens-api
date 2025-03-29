from fastapi import APIRouter
from .routers.plants_router import router as plants_router
from .routers.plants_type_router import router as plants_type_router

router = APIRouter(
    prefix="/microgreen"
)

router.include_router(plants_router)
router.include_router(plants_type_router)