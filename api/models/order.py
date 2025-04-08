from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship

from api.utils.models import TimestamppedModel
from api.enums import ORDER_STATUS


class Orders(TimestamppedModel, table=True):
    id: Optional[UUID] = Field(primary_key=True, default_factory=uuid4)
    order_status: str = Field(default=ORDER_STATUS.WAITING_PAYMENT)
    total_amount: int
    total_discounted_amount: int
    discount_percentage: float = Field(default=0.0)
    coupon_code: Optional[str] = None
    user_id: UUID = Field(foreign_key="user.id")

    items: Optional[List["OrderItem"]] = Relationship(back_populates="order")


class OrderItem(SQLModel, table=True):
    sku: str = Field(primary_key=True)
    order_id: UUID = Field(primary_key=True, foreign_key="orders.id")

    name: str
    header: str
    description: str
    cover_image_key: Optional[str] = None
    unit_price: int
    quantity: int
    discount_percentage: float = Field(default=0.0)
    category_name: str

    order: Optional["Orders"] = Relationship(back_populates="items")


class Coupon(TimestamppedModel, table=True):
    code: str = Field(primary_key=True)
    expiration: Optional[datetime] = Field(default=None)
    discount_percentage: float
