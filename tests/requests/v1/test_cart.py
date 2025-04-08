from fastapi.testclient import TestClient
from sqlmodel import select, Session
from uuid import UUID

from tests.providers import CartFactory, CartItemFactory, ProductFactory
from api.models import User


def test_get_cart(auth_client: TestClient, session: Session):
    user = session.exec(
        select(User).where(User.username == "auth_user")
    ).first()
    cart = CartFactory.create(user_id=user.id)

    for _ in range(3):
        CartItemFactory.create(cart_id=cart.id)

    response = auth_client.get("/v1/carts/current")
    data = response.json()

    assert response.status_code == 200
    assert data["data"]["id"] == str(cart.id)
    assert len(data["data"]["items"]) == 3


def test_create_cart(client: TestClient):
    response = client.post("/v1/carts", json={})
    assert response.status_code == 201


def test_sync_cart(
    client: TestClient, auth_client: TestClient, session: Session
):
    res = client.post("/v1/carts", json={})
    cart_id = res.json()["data"]["id"]
    for _ in range(3):
        CartItemFactory.create(cart_id=UUID(cart_id))
    response = auth_client.post("/v1/carts/sync_ip_to_user")
    assert response.status_code == 204


def test_add_cart_item(client: TestClient):
    product = ProductFactory.create()
    client.post("/v1/carts", json={})

    response = client.put(
        f"/v1/carts/items/{product.sku}", json={"quantity": 3}
    )

    assert response.status_code == 200
