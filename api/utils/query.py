from sqlmodel import Session, select, func
from pydantic import BaseModel
from typing import List, Any


class PaginatedResults(BaseModel):
    objects: List[Any]
    page: int
    limit: int
    total_rows: int


def paginate(
    session: Session, query, page: int, limit: int
) -> PaginatedResults:
    offset = (page - 1) * limit
    total_rows = session.exec(
        select(func.count()).select_from(query.subquery())
    ).one()
    objects = session.exec(query.offset(offset).limit(limit)).all()

    return {
        "objects": objects,
        "page": page,
        "limit": limit,
        "total_rows": total_rows,
    }
