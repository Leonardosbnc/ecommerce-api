import factory

from api import models
from api.security import get_password_hash


class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.User
        sqlalchemy_session_persistence = "commit"

    email = factory.Faker("email")
    username = factory.Faker("first_name")
    password = get_password_hash("pass123")
    is_admin = False
