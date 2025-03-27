from fastapi import APIRouter

from .auth import router as auth_router
from .v1 import router as v1_router

router = APIRouter()

router.include_router(auth_router, prefix="/auth")
router.include_router(v1_router, prefix="/v1")
