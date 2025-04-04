from fastapi.testclient import TestClient

from tests.providers import ProductFactory


def test_get_product(client: TestClient):
    product = ProductFactory.create(cover_image_key="TEST_KEY")
    response = client.get(f"/v1/products/{product.sku}")
    data = response.json()

    assert response.status_code == 200
    assert data["data"]["sku"] == product.sku
    assert data["data"]["name"] == product.name
    assert data["data"]["description"] == product.description
    assert data["data"]["cover_image_key"] == product.cover_image_key
    assert data["data"]["header"] == product.header
    assert data["data"]["unit_price"] == product.unit_price
    assert data["data"]["discount_percentage"] == product.discount_percentage


def test_list_products(client: TestClient):
    for _ in range(5):
        ProductFactory.create()

    response = client.get("/v1/products")
    data = response.json()

    assert response.status_code == 200
    assert len(data["data"]) == 5
