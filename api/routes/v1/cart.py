from fastapi import APIRouter, HTTPException, status, Request
from sqlmodel import select, update

from api.db import ActiveSession
from api.auth import OAuthenticatedUser, AuthenticatedUser
from api.models import Cart, CartItem
from api.serializers.cart import CartResponse, CartData


router = APIRouter()


@router.post("/", response_model=CartResponse, status_code=201)
def create_cart(
    current_user: OAuthenticatedUser, session: ActiveSession, request: Request
):
    if current_user is not None:
        user_cart = session.exec(
            select(Cart).where(Cart.user_id == current_user.id)
        ).first()
        if user_cart is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User is already attached to a cart",
            )

    data = CartData(
        user_id=current_user.id if current_user is not None else None,
        origin_ip=request.client.host,
    )
    cart = Cart.model_validate(data)

    session.add(cart)
    session.commit()
    session.refresh(cart)

    return {"data": cart}


@router.get("/current", response_model=CartResponse)
def get_current_cart(
    current_user: OAuthenticatedUser, session: ActiveSession, request: Request
):
    user_cart = None
    if current_user is not None:
        user_cart = session.exec(
            select(Cart).where(Cart.user_id == current_user.id)
        ).first()

        if user_cart is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No cart found"
            )
        return {"data": user_cart}

    ip_cart = session.exec(
        select(Cart).where(Cart.origin_ip == request.client.host)
    ).first()

    if ip_cart is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No cart found"
        )

    return {"data": ip_cart}


@router.post("/sync_ip_to_user", status_code=204)
def sync_ip_cart_to_user(
    current_user: AuthenticatedUser, session: ActiveSession, request: Request
):
    ip_cart = session.exec(
        select(Cart).where(Cart.origin_ip == request.client.host)
    ).first()

    if ip_cart is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No cart found"
        )
    if ip_cart.user_id is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cart is already attached to an user",
        )

    user_cart = session.exec(
        select(Cart).where(Cart.user_id == current_user.id)
    ).first()

    if user_cart is None:
        ip_cart.user_id = current_user.id
        session.commit()
        return

    session.exec(
        update(CartItem)
        .where(CartItem.cart_id == ip_cart.id)
        .values(cart_id=user_cart.id)
    )

    session.delete(ip_cart)
    session.commit()
