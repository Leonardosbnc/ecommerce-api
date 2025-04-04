import re

from sqlmodel import Field, ARRAY, String, Column, SQLModel, Relationship
from pydantic import model_validator
from typing import List, Optional

from api.utils.models import TimestamppedModel


class Product(TimestamppedModel, table=True):
    sku: str = Field(primary_key=True)
    name: str
    header: str
    description: str
    cover_image_key: Optional[str] = None
    unit_price: int
    discount_percentage: float = Field(default=0.0)
    category_id: int = Field(foreign_key="category.id")

    category: Optional["Category"] = Relationship()
    images: Optional["ProductImage"] = Relationship(back_populates="product")

    @model_validator(mode="before")
    def format_and_validate_sku(self):
        self.sku = self.sku.upper()

        sku_len = len(self.sku)
        if (
            not re.fullmatch(r"^[A-Z0-9]+$", self.sku)
            or sku_len < 3
            or sku_len > 24
        ):
            raise ValueError("Invalid SKU")

        return self


class ProductImage(TimestamppedModel, table=True):
    key: str = Field(primary_key=True)
    product_id: str = Field(foreign_key="product.sku")

    product: Optional["Product"] = Relationship(back_populates="images")


class Category(SQLModel, table=True):
    id: Optional[int] = Field(primary_key=True, nullable=False)
    name: str
