import datetime
from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

from api.db import ActiveSession
from api.auth import AuthenticatedUser
from api.serializers.order import (
    OrderResponse,
    OrderRequest,
    OrderItemRequest,
    OrderData,
)
from api.models import Cart, Orders, Coupon, OrderItem

router = APIRouter()


@router.post("/", status_code=201, response_model=OrderResponse)
def create_order(
    data: OrderRequest, current_user: AuthenticatedUser, session: ActiveSession
):
    cart = session.exec(
        select(Cart).where(Cart.user_id == current_user.id)
    ).first()

    if cart is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No cart found for user",
        )

    order_data = {
        **data.model_dump(),
        "user_id": current_user.id,
        "discount_percentage": 0.0,
    }

    if data.coupon_code is not None:
        coupon = session.get(Coupon, data.coupon_code)
        if coupon is not None:
            is_valid = (
                coupon.expiration is None
                or coupon.expiration >= datetime.now()
            )
            if is_valid:
                order_data["coupon_code"] = data.coupon_code
                order_data["discount_percentage"] = coupon.discount_percentage

    total_amount = sum(
        [i.product.discounted_price * i.quantity for i in cart.items]
    )
    order_data["total_amount"] = total_amount
    order_data["total_discounted_amount"] = int(
        (total_amount / 100) * (100 - order_data["discount_percentage"])
    )

    order = Orders.model_validate(OrderData(**order_data))
    session.add(order)
    session.commit()
    session.refresh(order)

    for item in cart.items:
        item_data = {
            **item.model_dump(),
            **item.product.model_dump(),
            "category_name": item.product.category_name,
            "order_id": order.id,
        }
        order_item_data = OrderItemRequest(**item_data)
        order_item = OrderItem.model_validate(order_item_data)
        session.add(order_item)

    session.commit()
    session.refresh(order)

    return {"data": order}
