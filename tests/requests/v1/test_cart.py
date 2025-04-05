from fastapi.testclient import TestClient
from sqlmodel import select, Session

from tests.providers import CartFactory, CartItemFactory
from api.models import User


def test_get_cart(auth_client: TestClient, session: Session):
    user = session.exec(
        select(User).where(User.username == "auth_user")
    ).first()
    cart = CartFactory(user_id=user.id)

    for _ in range(3):
        CartItemFactory.create(cart_id=cart.id)

    response = auth_client.get(f"/v1/carts/{cart.id}")
    data = response.json()

    assert response.status_code == 200
    assert data["data"]["id"] == str(cart.id)
    assert len(data["data"]["items"]) == 3
