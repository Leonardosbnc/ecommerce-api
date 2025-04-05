from uuid import UUID
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from api.db import ActiveSession
from api.auth import AuthenticatedUser, OAuthenticatedUser
from api.models import Cart
from api.serializers.cart import CartResponse


router = APIRouter()


@router.get("/{id}", response_model=CartResponse)
def get_cart_items(
    id: UUID, current_user: OAuthenticatedUser, session: ActiveSession
):
    cart = session.get(Cart, id)
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Cart not found"
        )
    if (
        cart.user_id is not None
        and current_user is not None
        and cart.user_id != current_user.id
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Access denied"
        )

    return {"data": cart}


@router.post("/")
def create_cart():
    return
