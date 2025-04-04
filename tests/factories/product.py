import factory

from api import models


class CategoryFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Category
        sqlalchemy_session_persistence = "commit"

    name = factory.Faker("first_name")


class ProductFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = models.Product
        sqlalchemy_session_persistence = "commit"

    sku = factory.Sequence(lambda n: "sku{}".format(n))
    name = factory.Sequence(lambda n: "product {}".format(n))
    header = factory.Faker("name")
    description = factory.Faker("text")
    cover_image_key = None
    unit_price = 199
    discount_percentage = 0.0

    category = factory.SubFactory(CategoryFactory)
