from datetime import datetime
from sqlmodel import SQLModel, Field


class TimestamppedModel(SQLModel):
    created_at: datetime = Field(default=datetime.utcnow(), nullable=False)
    updated_at: datetime = Field(
        default_factory=datetime.utcnow, nullable=False
    )
