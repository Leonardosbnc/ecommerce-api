from .factories import *


def set_factories_session(db):
    for factory in (
        UserFactory,
        AddressFactory,
        CategoryFactory,
        ProductFactory,
        CartFactory,
        CartItemFactory,
    ):
        factory._meta.sqlalchemy_session = db
