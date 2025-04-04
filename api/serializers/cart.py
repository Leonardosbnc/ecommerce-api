from pydantic import BaseModel, Field, computed_field
from typing import List
from uuid import UUID

from .product import BaseProductResponse
from api.models import Cart


class CartItemRequest(BaseModel):
    quantity: int


class CartItemResponse(BaseModel):
    quantity: int
    product: BaseProductResponse
    cart: Cart = Field(exclude=True)

    @computed_field
    @property
    def _meta(self):
        links = {
            "update": {
                "href": f"/v1/carts/{self.cart.id}/items/{self.product.sku}",
                "method": "PUT",
            },
            "DELETE": {
                "href": f"/v1/carts/{self.cart.id}/items/{self.product.sku}",
                "method": "DELETE",
            },
            "product": {
                "href": f"/v1/products/{self.product.sku}",
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
    def _meta(self):
        return {
            "_links": {
                "self": {"href": f"/v1/carts/{self.data.id}", "method": "GET"},
                "add_item": {
                    "href": f"/v1/carts/{self.data.id}/items/:product_sku",
                    "method": "PUT",
                },
            }
        }
