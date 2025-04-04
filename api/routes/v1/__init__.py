from fastapi import APIRouter

from .user import router as user_router
from .product import router as product_router

router = APIRouter()


router.include_router(user_router, prefix="/users")
router.include_router(product_router, prefix="/products")
