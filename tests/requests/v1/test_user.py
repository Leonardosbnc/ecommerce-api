from fastapi.testclient import TestClient

from sqlmodel import select, Session
from tests.factories import AddressFactory
from api.models import User


def test_create_user(client: TestClient):
    response = client.post(
        "/v1/users",
        json={
            "email": "test@email.com",
            "username": "username_test",
            "password": "pass123",
        },
    )

    assert response.status_code == 201


def test_create_address(auth_client: TestClient):
    response = auth_client.post(
        "/v1/users/addresses",
        json={
            "line_1": "Street of Pumpkins, 13",
            "city": "Test City",
            "state": "TS",
            "country": "Brazil",
            "zip_code": "131313",
        },
    )

    assert response.status_code == 201


def test_update_address(auth_client: TestClient, session: Session):
    user = session.exec(
        select(User).where(User.username == "auth_user")
    ).first()
    address = AddressFactory.create(user_id=user.id)

    response = auth_client.patch(
        f"/v1/users/addresses/{address.id}",
        json={
            "line_1": "New Street, 14",
        },
    )

    assert response.status_code == 200


def test_list_addresses(auth_client: TestClient, session: Session):
    user = session.exec(
        select(User).where(User.username == "auth_user")
    ).first()
    for _ in range(4):
        AddressFactory.create(user_id=user.id)

    response = auth_client.get(
        "/v1/users/addresses",
    )

    res_json = response.json()
    assert response.status_code == 200
    assert len(res_json["data"]) == 4


def test_get_address(auth_client: TestClient, session: Session):
    user = session.exec(
        select(User).where(User.username == "auth_user")
    ).first()
    address = AddressFactory.create(user_id=user.id)

    response = auth_client.get(
        f"/v1/users/addresses/{address.id}",
    )
    res_json = response.json()["data"]

    assert response.status_code == 200
    assert res_json["line_1"] == address.line_1
    assert res_json["line_2"] == address.line_2
    assert res_json["city"] == address.city
    assert res_json["state"] == address.state
    assert res_json["country"] == address.country
    assert res_json["zip_code"] == address.zip_code
