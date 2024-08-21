from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel
from sqlmodel import Session

from app.auth.models import USER_SERVICE, User
from app.commun.crypto import verify_password
from app.commun.decorators import safe_execution
from app.database.unit_of_work import unit
from app.settings import ALGORITHM, SECRET_KEY

CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@safe_execution
def authenticate_user(session: Session, username: str, password: str) -> User | None:
    user = USER_SERVICE.get_or_raise(session, username=username)
    is_auth = verify_password(password, user.hashed_password)

    if is_auth is False:
        return None

    return user


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)

    data.update({"exp": expire})
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")

        if username is None:
            raise CREDENTIALS_EXCEPTION

        token_data = TokenData(username=username)

    except InvalidTokenError:
        raise CREDENTIALS_EXCEPTION

    with unit() as session:
        user = USER_SERVICE.get_or_none(session, username=token_data.username)

    if user is None:
        raise CREDENTIALS_EXCEPTION

    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
):
    return current_user
