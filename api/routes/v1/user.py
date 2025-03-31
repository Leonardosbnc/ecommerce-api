from uuid import UUID
from typing import List
from fastapi import APIRouter, HTTPException, status

from sqlmodel import select
from api.auth import AuthenticatedUser
from api.serializers.adress import (
    AddressResponse,
    AddressRequest,
    PartialUpdateAddress,
    MultipleAddressResponse,
)
from api.db import ActiveSession
from api.models import Address

router = APIRouter()


@router.get("/addresses/{id}", response_model=AddressResponse)
async def get_adress(
    id: UUID, current_user: AuthenticatedUser, session: ActiveSession
):
    address = session.get(Address, id)
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Address not found"
        )
    if address.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Permission denied",
        )

    return {"id": address.id, "data": address}


@router.get("/addresses", response_model=MultipleAddressResponse)
async def list_user_addresses(
    current_user: AuthenticatedUser, session: ActiveSession
):
    addresses = session.exec(
        select(Address).where(Address.user_id == current_user.id)
    ).all()
    return {"objects": addresses}


@router.post(
    "/addresses",
    response_model=AddressResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_adress(
    data: AddressRequest,
    current_user: AuthenticatedUser,
    session: ActiveSession,
):
    address = Address.model_validate(
        {**data.model_dump(), "user_id": current_user.id}
    )

    session.add(address)
    session.commit()
    session.refresh(address)

    return {"id": address.id, "data": address}


@router.patch("/addresses/{id}", response_model=AddressResponse)
async def partial_update_address(
    id: UUID,
    data: PartialUpdateAddress,
    session: ActiveSession,
    current_user: AuthenticatedUser,
):
    address = session.get(Address, id)
    if not address:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Address not found"
        )
    if address.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Permission denied",
        )

    patch_data = data.model_dump(exclude_unset=True)
    for key, value in patch_data.items():
        setattr(address, key, value)

    session.commit()
    session.refresh(address)

    return {"id": address.id, "data": address}
