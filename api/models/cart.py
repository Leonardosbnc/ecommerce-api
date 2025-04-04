from uuid import UUID, uuid4
from typing import Optional, TYPE_CHECKING, List

from sqlmodel import Field, Relationship, SQLModel
from api.utils.models import TimestamppedModel


if TYPE_CHECKING:
    from . import User, Product


class Cart(TimestamppedModel, table=True):
    id: Optional[UUID] = Field(primary_key=True, default_factory=uuid4)
    user_id: Optional[UUID] = Field(foreign_key="user.id")

    user: Optional["User"] = Relationship(back_populates="carts")
    items: Optional[List["CartItem"]] = Relationship()


class CartItem(SQLModel, table=True):
    cart_id: UUID = Field(primary_key=True, foreign_key="cart.id")
    product_id: str = Field(primary_key=True, foreign_key="product.sku")
    quantity: int

    product: Optional["Product"] = Relationship()
