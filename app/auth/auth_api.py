from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.models import USER_SERVICE
from app.auth.token import (
    Token,
    User,
    authenticate_user,
    create_access_token,
    get_current_active_user,
)
from app.database.unit_of_work import unit
from app.settings import ACCESS_TOKEN_EXPIRE_MINUTES

auth_router = APIRouter(
    prefix="/auth",
    tags=["Authentication"],
)


@auth_router.post("/token")
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    with unit() as session:
        user = authenticate_user(session, form_data.username, form_data.password)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )

        return Token(access_token=access_token, token_type="bearer")


@auth_router.post(
    "/register", response_model=Token, status_code=status.HTTP_201_CREATED
)
def register_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    with unit() as session:
        existing_user = USER_SERVICE.get_or_none(session, username=form_data.username)

    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    # Create new user
    with unit() as session:
        new_user = User(username=form_data.username, password=form_data.password)
        new_user = USER_SERVICE.create(session, new_user)

        # Create and return token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": new_user.username}, expires_delta=access_token_expires
        )
    return Token(access_token=access_token, token_type="bearer")


@auth_router.get("/users/me/", response_model=User)
def read_users_me(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return current_user


@auth_router.get("/users/me/items/")
def read_own_items(
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    return [{"item_id": "Foo", "owner": current_user.username}]
