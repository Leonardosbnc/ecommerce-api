from fastapi.testclient import TestClient
from sqlmodel import Session, select

from api.models import User
from tests.factories import CartFactory, CartItemFactory


def test_create_order(auth_client: TestClient, session: Session):
    user = session.exec(
        select(User).where(User.username == "auth_user")
    ).first()
    cart = CartFactory.create(user_id=user.id)
    for _ in range(3):
        CartItemFactory.create(cart_id=cart.id)

    response = auth_client.post("v1/orders", json={})

    assert response.status_code == 201
