from typing import Optional, Any, List
from uuid import UUID

from pydantic import BaseModel, computed_field, Field
from api.models import Address


class _AddressResponse(BaseModel):
    id: UUID = Field(exclude=True)
    line_1: str
    line_2: Optional[str]
    city: str
    state: str
    country: str
    zip_code: str


class AddressResponse(BaseModel):
    id: UUID = Field(exclude=True)
    data: _AddressResponse

    @computed_field
    @property
    def _meta(self) -> Any:
        links = [
            {
                "self": {"href": f"/address/{self.id}", "method": "GET"},
                "delete": {"href": f"/address/{self.id}", "method": "DELETE"},
                "update": {"href": f"/address/{self.id}", "method": "PATCH"},
            }
        ]

        return {"_links": links}


class MultipleAddressResponse(BaseModel):
    objects: List[Address] = Field(exclude=True)

    @computed_field
    @property
    def data(self) -> List[AddressResponse]:
        return [
            AddressResponse(id=d.id, data=d.model_dump()) for d in self.objects
        ]


class AddressRequest(BaseModel):
    line_1: str
    line_2: Optional[str] = None
    city: str
    state: str
    country: str
    zip_code: str


class PartialUpdateAddress(BaseModel):
    line_1: Optional[str] = None
    line_2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    country: Optional[str] = None
