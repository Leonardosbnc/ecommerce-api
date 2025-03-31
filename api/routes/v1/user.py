from uuid import UUID
from typing import List
from fastapi import APIRouter, HTTPException, status
from datetime import timedelta

from sqlmodel import select
from api.auth import (
    AuthenticatedUser,
    create_confirm_account_token,
    validate_token,
)
from api.serializers.address import (
    AddressResponse,
    AddressRequest,
    PartialUpdateAddress,
    MultipleAddressResponse,
)
from api.serializers.user import (
    UserResponse,
    UserRequest,
    ConfirmAccountRequest,
)
from api.db import ActiveSession
from api.models import Address, User
from api.services.email import EmailService
from api.config import settings


router = APIRouter()


@router.post(
    "/", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def create_user(data: UserRequest, session: ActiveSession):
    user = User.model_validate(data)

    session.add(user)
    session.commit()
    session.refresh(user)

    if settings.email.enabled is True:
        token_expires = timedelta(minutes=15)
        token = create_confirm_account_token(
            data={"sub": user.username, "fresh": False},
            expires_delta=token_expires,
        )

        EmailService().send_email_confirmation(token, user.email)

    return user


@router.post("/confirm_account", status_code=204)
async def confirm_account(data: ConfirmAccountRequest, session: ActiveSession):
    user = await validate_token(data.token)
    user.confirmed = True

    session.add(user)
    session.commit()


@router.get("/addresses/{id}", response_model=AddressResponse)
async def get_address(
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
async def create_address(
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
