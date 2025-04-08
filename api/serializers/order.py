from uuid import UUID
from pydantic import BaseModel, computed_field, Field
from typing import Optional, List, Any


class OrderRequest(BaseModel):
    coupon_code: Optional[str] = None


class OrderData(BaseModel):
    total_amount: int
    total_discounted_amount: int
    discount_percentage: float
    coupon_code: Optional[str] = None
    user_id: UUID


class OrderItemRequest(BaseModel):
    sku: str
    order_id: UUID
    name: str
    header: str
    description: str
    cover_image_key: str | None
    unit_price: int
    quantity: int
    discount_percentage: float
    category_name: str


class OrderItemResponse(BaseModel):
    sku: str
    name: str
    header: str
    description: str
    cover_image_key: Optional[str] = None
    unit_price: int
    quantity: int
    discount_percentage: float
    category_name: str
    order_id: UUID

    @computed_field
    @property
    def _meta(self) -> Any:
        links = {
            "update": {
                "href": f"/v1/orders/{self.order_id}/items/{self.sku}",
                "method": "PUT",
            },
            "delete": {
                "href": f"/v1/orders/{self.order_id}/items/{self.sku}",
                "method": "DELETE",
            },
        }

        return {"_links": links}


class _OrderResponse(BaseModel):
    id: UUID
    order_status: str
    total_amount: int
    total_discounted_amount: int
    discount_percentage: float
    coupon_code: str | None

    items: List[OrderItemResponse]


class OrderResponse(BaseModel):
    data: _OrderResponse

    @computed_field
    @property
    def _meta(self) -> Any:
        links = {
            "self": {"href": f"/v1/orders/{self.data.id}", "method": "GET"},
            "delete": {
                "href": f"/v1/orders/{self.data.id}",
                "method": "DELETE",
            },
            "cancel": {
                "href": f"/v1/orders/{self.data.id}/cancel",
                "method": "POST",
            },
            "add_item": {
                "href": f"/v1/orders/{self.data.id}/items/:product_sku",
                "method": "PUT",
            },
        }

        return {"_links": links}


class MultipleOrderResponse(BaseModel):
    objects: List[_OrderResponse] = Field(exclude=True)
    page: int = Field(exclude=True)
    limit: int = Field(exclude=True)
    total_rows: int = Field(exclude=True)

    @computed_field
    @property
    def data(self) -> List[OrderResponse]:
        return [OrderResponse(data=obj) for obj in self.objects]

    @computed_field
    @property
    def _meta(self) -> Any:
        pagination_data = {
            "page": self.page,
            "limit": self.limit,
            "total_rows": self.total_rows,
        }

        links = {
            "self": {
                "href": f"/v1/orders?page={self.page}&limit={self.limit}",
                "method": "GET",
            },
        }

        if self.page > 1:
            links["previous"] = {
                "href": f"/v1/orders?page={self.page-1}&limit={self.limit}",
                "method": "GET",
            }

        if self.page * self.limit < self.total_rows:
            links["next"] = {
                "href": f"/v1/orders?page={self.page+1}&limit={self.limit}",
                "method": "GET",
            }

        return {**pagination_data, "_links": links}
