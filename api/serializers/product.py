from typing import Optional, Any, List, Dict
from pydantic import BaseModel, Field, computed_field

from api.models import Category, Product


class CategoryResponse(BaseModel):
    name: str


class ProductRequest(BaseModel):
    sku: str
    name: str
    header: str
    description: str
    cover_image_key: Optional[str] = None
    unit_price: int
    discount_percentage: Optional[float] = Field(default=0.0)
    category_id: int


class PartialProductRequest(BaseModel):
    sku: Optional[str] = None
    name: Optional[str] = None
    header: Optional[str] = None
    description: Optional[str] = None
    cover_image_key: Optional[str] = None
    unit_price: Optional[int] = None
    discount_percentage: Optional[float] = None
    category_id: Optional[int] = None


class _BaseProductResponse(BaseModel):
    sku: str
    name: str
    header: str
    description: str
    cover_image_key: Optional[str] = None
    unit_price: int
    discount_percentage: float

    category_id: int = Field(exclude=True)
    category: Category = Field(exclude=True)

    @computed_field
    @property
    def category_name(self) -> str:
        return self.category.name


class BaseProductResponse(BaseModel):
    data: _BaseProductResponse

    @computed_field
    @property
    def _meta(self) -> Any:
        links = [
            {
                "self": {
                    "href": f"/v1/products/{self.data.sku}",
                    "method": "GET",
                },
                "category": {
                    "href": f"/v1/categories/{self.data.category_id}",
                    "method": "GET",
                },
            }
        ]

        return {"_links": links}


class AdminProductResponse(BaseProductResponse):
    @computed_field
    @property
    def _meta(self) -> Any:
        links = [
            {
                "self": {"href": f"/v1/products/{self.sku}", "method": "GET"},
                "delete": {
                    "href": f"/v1/products/{self.sku}",
                    "method": "DELETE",
                },
                "update": {
                    "href": f"/v1/products/{self.sku}",
                    "method": "PATCH",
                },
                "category": {
                    "href": f"/v1/categories/{self.category_id}",
                    "method": "GET",
                },
            }
        ]

        return {"_links": links}


class BaseMultipleProductsResponse(BaseModel):
    objects: List[Product] = Field(exclude=True)
    page: int = Field(exclude=True)
    limit: int = Field(exclude=True)
    total_rows: int = Field(exclude=True)
    filters: Dict[str, Any] = Field(exclude=True)

    @computed_field
    @property
    def data(self) -> List[BaseProductResponse]:
        _data = [
            BaseProductResponse(
                data={**obj.model_dump(), "category": obj.category}
            )
            for obj in self.objects
        ]
        return _data

    @computed_field
    @property
    def _meta(self) -> Any:
        pagination_data = {
            "page": self.page,
            "limit": self.limit,
            "total_rows": self.total_rows,
        }

        filter_params = "&".join([f"{k}={v}" for k, v in self.filters.items()])
        links = [
            {
                "self": {
                    "href": f"/v1/products?page={self.page}&limit={self.limit}&{filter_params}",
                    "method": "GET",
                },
            }
        ]
        if self.page > 1:
            links.append(
                {
                    "previous": f"/v1/products?page={self.page-1}&limit={self.limit}&{filter_params}"
                }
            )

        if self.page * self.limit < self.total_rows:
            links.append(
                {
                    "next": f"/v1/products?page={self.page+1}&limit={self.limit}&{filter_params}"
                }
            )

        return {**pagination_data, "_links": links}


class AdminMultipleProductsResponse(BaseMultipleProductsResponse):
    @computed_field
    @property
    def data(self) -> List[AdminProductResponse]:
        _data = [AdminProductResponse({"data": obj}) for obj in self.objects]
        return _data
