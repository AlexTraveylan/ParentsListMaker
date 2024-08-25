from typing import Annotated

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.models import USER_SERVICE
from app.auth.token import (
    Token,
    User,
    authenticate_user,
    create_access_token,
    get_current_user,
)
from app.database.unit_of_work import unit_api
from app.exceptions import (
    CannotCreateStillExistsException,
    RessourceNotFoundException,
    UnauthorizedException,
)

auth_router = APIRouter(
    tags=["Authentication"],
)


@auth_router.post("/token")
def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    with unit_api("Tentative de connexion") as session:
        user = authenticate_user(session, form_data.username, form_data.password)
        if user is None:
            raise UnauthorizedException("Nom d'utilisateur ou mot de passe incorrect")

        token = create_access_token({"sub": user.username})

    return token


@auth_router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    with unit_api("Tentative de création d'utilisateur") as session:
        existing_user = USER_SERVICE.get_or_none(session, username=form_data.username)

        if existing_user is not None:
            raise CannotCreateStillExistsException("Nom d'utilisateur déjà enregistré")

        new_user = User(username=form_data.username, password=form_data.password)
        new_user = USER_SERVICE.create(session, new_user)

        token = create_access_token({"sub": new_user.username})

    return token


@auth_router.get("/users/me/")
def read_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    return current_user


@auth_router.delete("/users/me/")
def delete_users_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    with unit_api("Tentative de suppression de l'utilisateur") as session:
        is_deleted = USER_SERVICE.delete(session, current_user.id)

        if is_deleted is False:
            raise RessourceNotFoundException("Impossible de supprimer l'utilisateur")

    return None
