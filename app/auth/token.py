import datetime
from datetime import timedelta, timezone
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
from app.database.unit_of_work import unit_api
from app.exceptions import UnauthorizedException
from app.settings import ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM, SECRET_KEY

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


def create_access_token(data: dict) -> Token:
    expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.now(timezone.utc) + expires_delta

    data.update({"exp": expire})
    encoded_jwt = jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

    Token(access_token=encoded_jwt, token_type="bearer")


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    with unit_api("Trying to get current user") as session:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str | None = payload.get("sub")

            if username is None:
                raise UnauthorizedException

            token_data = TokenData(username=username)

        except InvalidTokenError:
            raise UnauthorizedException

        user = USER_SERVICE.get_or_none(session, username=token_data.username)

        if user is None:
            raise UnauthorizedException

        session.expunge(user)

    return user
