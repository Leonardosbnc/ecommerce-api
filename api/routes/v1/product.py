from typing import Optional, List
from fastapi import APIRouter, HTTPException, status
from fastapi_pagination import paginate
from sqlmodel import select, column, col

from api.db import ActiveSession
from api.utils.query import paginate
from api.models import Product, Category
from api.serializers.product import (
    BaseMultipleProductsResponse,
    BaseProductResponse,
    CategoryResponse,
)

router = APIRouter()


@router.get("/{sku}", response_model=BaseProductResponse)
async def get_product(sku: str, session: ActiveSession):
    product = session.get(Product, sku)

    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found"
        )

    return {"data": product}


@router.get("/", response_model=BaseMultipleProductsResponse)
async def get_products(
    *,
    page: Optional[int] = 1,
    limit: Optional[int] = 30,
    name: Optional[str] = None,
    session: ActiveSession
):
    filters = {}
    query = select(Product).join(Category)

    if name:
        query = query.where(col(Product.name).icontains(name))
        filters["name"] = name

    paginated_result = paginate(session, query, page, limit)

    return {**paginated_result, "filters": filters}


@router.get("/categories", response_model=List[CategoryResponse])
def get_categories(session: ActiveSession):
    categories = session.exec(select(Category).order_by(Category.name))
    return categories
