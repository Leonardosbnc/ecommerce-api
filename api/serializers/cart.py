from pydantic import BaseModel, Field, computed_field
from typing import List, Any
from uuid import UUID


class CartItemRequest(BaseModel):
    quantity: int


class CartItemResponse(BaseModel):
    quantity: int
    product_id: str = Field(exclude=True)
    cart_id: UUID = Field(exclude=True)

    @computed_field
    @property
    def _meta(self) -> Any:
        links = {
            "update": {
                "href": f"/v1/carts/{self.cart_id}/items/{self.product_id}",
                "method": "PUT",
            },
            "DELETE": {
                "href": f"/v1/carts/{self.cart_id}/items/{self.product_id}",
                "method": "DELETE",
            },
            "product": {
                "href": f"/v1/products/{self.product_id}",
                "method": "GET",
            },
        }

        return {"_links": links}


class _CartResponse(BaseModel):
    id: UUID
    items: List[CartItemResponse]


class CartResponse(BaseModel):
    data: _CartResponse

    @computed_field
    @property
    def _meta(self) -> Any:
        return {
            "_links": {
                "self": {"href": f"/v1/carts/{self.data.id}", "method": "GET"},
                "add_item": {
                    "href": f"/v1/carts/{self.data.id}/items/:product_sku",
                    "method": "PUT",
                },
            }
        }
