from fastapi.testclient import TestClient

from api.security import get_password_hash
from api.auth import create_reset_password_token
from tests.factories import UserFactory


def test_get_token(client: TestClient):
    user = UserFactory.create(password=get_password_hash("Test_password"))
    response = client.post(
        "/auth/token",
        data={"username": user.username, "password": "Test_password"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    response_keys = ["access_token", "refresh_token", "token_type"]
    response_json = response.json()

    assert response.status_code == 200
    for key in response_keys:
        assert key in response_json


def test_bad_login(client: TestClient):
    response = client.post(
        "/auth/token",
        data={"username": "admin", "password": "admin1"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 403


def test_change_password(client: TestClient):
    user = UserFactory.create()
    token = create_reset_password_token({"sub": user.username})
    response = client.post(
        "/auth/change-password",
        json={"token": token, "password": "new_pass123"},
    )

    assert response.status_code == 204
