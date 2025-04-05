from fastapi import APIRouter

from .user import router as user_router
from .product import router as product_router
from .cart import router as cart_router

router = APIRouter()


router.include_router(user_router, prefix="/users")
router.include_router(product_router, prefix="/products")
router.include_router(cart_router, prefix="/carts")
