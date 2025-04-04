"""Token based auth"""

from datetime import datetime, timedelta, timezone
from typing import Callable, Optional, Union, Annotated
from functools import partial

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import BaseModel
from sqlmodel import Session, select

from api.config import settings
from api.db import engine
from api.models.user import User
from api.security import verify_password

SECRET_KEY = settings.security.secret_key  # pyright: ignore
ALGORITHM = settings.security.algorithm  # pyright: ignore


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


# Models


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class RefreshToken(BaseModel):
    refresh_token: str


class TokenData(BaseModel):
    username: Optional[str] = None


# Functions


def create_jwt_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
    scope: str = "access_token",
) -> str:
    """Creates a JWT Token from provided data"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire, "scope": scope})
    encoded_jwt = jwt.encode(
        to_encode,
        SECRET_KEY,  # pyright: ignore
        algorithm=ALGORITHM,  # pyright: ignore
    )
    return encoded_jwt


create_refresh_token = partial(create_jwt_token, scope="refresh_token")
create_reset_password_token = partial(create_jwt_token, scope="reset_password")
create_confirm_account_token = partial(
    create_jwt_token, scope="confirm_account"
)


def authenticate_user(
    get_user: Callable, username: str, password: str
) -> Union[User, bool]:
    """Authenticate the user"""
    user = get_user(username)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def get_user(username) -> Optional[User]:
    """Get user from database"""
    query = select(User).where(User.username == username)

    with Session(engine) as session:
        return session.exec(query).first()


def get_current_user_or_raise(
    token: str = Depends(oauth2_scheme),
    request: Request = None,
    fresh=False,  # pyright: ignore
    token_scope="access_token",  # pyright: ignore
) -> User:
    """Get current user authenticated"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    if request:
        if authorization := request.headers.get("authorization"):
            try:
                token = authorization.split(" ")[1]
            except IndexError:
                raise credentials_exception

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],  # pyright: ignore
        )
        username: str = payload.get("sub")  # pyright: ignore
        scope: str = payload.get("scope")  # pyright: ignore

        if username is None or scope != token_scope:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    if fresh and (not payload["fresh"] and not user.is_admin):
        raise credentials_exception

    return user


def _try_get_current_user(
    token: str = Depends(oauth2_scheme), request: Request = None
) -> User | None:
    if token is None:
        return None
    try:
        user = get_current_user_or_raise(token, request)
        return user
    except HTTPException:
        return None


# FastAPI dependencies


async def get_current_active_user(
    current_user: User = Depends(get_current_user_or_raise),
) -> User:
    """Wraps the sync get_active_user for sync calls"""
    if current_user.confirmed is not True:
        raise HTTPException(status_code=401, detail="Account not confirmed")

    return current_user


async def try_get_current_active_user(
    current_user: User | None = Depends(_try_get_current_user),
) -> User | None:
    if current_user is not None and current_user.confirmed is not True:
        raise HTTPException(status_code=401, detail="Account not confirmed")

    return current_user


AuthenticatedUser = Annotated[User, Depends(get_current_active_user)]
OAuthenticatedUser = Annotated[
    User, None, Depends(try_get_current_active_user)
]


async def validate_token(
    token: str = Depends(oauth2_scheme), token_scope="access_token"
) -> User:
    """Validates user token"""
    user = get_current_user_or_raise(token=token, token_scope=token_scope)
    return user
