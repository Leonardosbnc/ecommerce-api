import re
from typing import Optional, List
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship
from pydantic import model_validator
from api.security import HashedPassword
from api.utils.models import TimestamppedModel


class User(TimestamppedModel, table=True):
    id: Optional[UUID] = Field(
        primary_key=True, nullable=False, default_factory=uuid4
    )
    email: str = Field(unique=True)
    username: str = Field(unique=True)
    password: HashedPassword
    is_admin: bool = Field(default=False)

    addresses: Optional[List["Address"]] = Relationship(back_populates="user")

    @model_validator(mode="before")
    def validate_and_format_unique_fields(self):
        self.email = self.email.lower().replace(" ", "")
        self.username = self.username.lower().replace(" ", "")

        if not re.fullmatch(
            'r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)', self.email
        ):
            raise ValueError("Email is not valid")

        return self


class Address(TimestamppedModel, table=True):
    id: Optional[UUID] = Field(
        primary_key=True, nullable=False, default_factory=uuid4
    )
    line_1: str
    line_2: Optional[str]
    city: str
    state: str
    country: str
    zip_code: str
    user_id: UUID = Field(foreign_key="user.id")

    user: Optional[User] = Relationship(back_populates="addresses")
