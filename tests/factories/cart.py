import factory

from api import models
from tests.factories import ProductFactory


class CartFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Cart
        sqlalchemy_session_persistence = "commit"

    user_id = None


class CartItemFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.CartItem
        sqlalchemy_session_persistence = "commit"

    cart_id = None
    product = factory.SubFactory(ProductFactory)
    quantity = 1
