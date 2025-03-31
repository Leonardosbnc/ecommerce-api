import os

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, text

os.environ["FORCE_ENV_FOR_DYNACONF"] = "testing"  # noqa

from api.db import engine, get_session
from api.app import app  # type: ignore
from api.security import get_password_hash

from .factories import UserFactory
from .providers import set_factories_session


@pytest.fixture(autouse=True, scope="session", name="db_engine")
def initialize_db(request):
    SQLModel.metadata.create_all(engine)
    request.addfinalizer(remove_db)
    yield engine


@pytest.fixture(autouse=True, scope="function")
def session(db_engine):
    with Session(db_engine) as session:

        def get_session_override():
            return session

        app.dependency_overrides[get_session] = get_session_override

        yield session

        session.rollback()
        for table in reversed(SQLModel.metadata.sorted_tables):
            session.exec(text(f"DELETE FROM {table.name};"))
            session.commit()
        session.close()


@pytest.fixture(scope="function")
def client():
    return TestClient(app)


@pytest.fixture(scope="function")
def auth_client():
    UserFactory.create(
        username="auth_user", password=get_password_hash("pass123")
    )

    client = TestClient(app)
    token = client.post(
        "/auth/token",
        data={"username": "auth_user", "password": "pass123"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    ).json()["access_token"]
    client.headers["Authorization"] = f"Bearer {token}"
    return client


def remove_db():
    try:
        os.remove("testing.db")
    except FileNotFoundError:
        pass


@pytest.fixture(autouse=True)
def set_session_for_factories():
    with Session(engine) as session:
        set_factories_session(session)
