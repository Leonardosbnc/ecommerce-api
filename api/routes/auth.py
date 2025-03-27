from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session
from api.config import settings
from api.db import ActiveSession
from api.models import User
from api.security import get_password_hash
from api.services.email import EmailService
from api.serializers.auth import ForgotPassword, ChangePassword
from api.auth import (
    Token,
    RefreshToken,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    create_reset_password_token,
    validate_token,
    get_user,
)


ACCESS_TOKEN_EXPIRE_MINUTES = settings.security.access_token_expire_minutes
REFRESH_TOKEN_EXPIRE_MINUTES = settings.security.refresh_token_expire_minutes
RESET_PASSWORD_TOKEN_EXPIRE_MINUTES = (
    settings.security.reset_password_token_expire_minutes
)

router = APIRouter()


@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    user = authenticate_user(get_user, form_data.username, form_data.password)
    if not user or not isinstance(user, User):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "fresh": True},
        expires_delta=access_token_expires,
    )

    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_refresh_token(
        data={"sub": user.username}, expires_delta=refresh_token_expires
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh_token", response_model=Token)
async def refresh_token(form_data: RefreshToken):
    user = await validate_token(token=form_data.refresh_token)

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username, "fresh": False},
        expires_delta=access_token_expires,
    )

    refresh_token_expires = timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    refresh_token = create_refresh_token(
        data={"sub": user.username}, expires_delta=refresh_token_expires
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/forgot-password", status_code=204)
async def forgot_password(data: ForgotPassword):
    user = get_user(data.username)
    if user is None:
        return

    token_expires = timedelta(minutes=RESET_PASSWORD_TOKEN_EXPIRE_MINUTES)
    token = create_reset_password_token(
        data={"sub": user.username, "fresh": False},
        expires_delta=token_expires,
    )
    EmailService().send_reset_password_email(token, user.email)


@router.post("/change-password", status_code=204)
async def change_password(
    data: ChangePassword, session: Session = ActiveSession
):
    user = await validate_token(token=data.token)
    user.password = get_password_hash(data.password)
    session.add(user)
    session.commit()
