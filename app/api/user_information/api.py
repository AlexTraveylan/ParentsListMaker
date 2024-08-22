from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.user_information.models import USER_INFORMATION_SERVICE, UserInformation
from app.api.user_information.schema import (
    UserInformationSchemaIn,
    UserInformationSchemaOut,
)
from app.auth.models import User
from app.auth.token import get_current_user
from app.database.unit_of_work import unit_api
from app.exceptions import CannotCreateStillExistsException, RessourceNotFoundException

user_information_router = APIRouter(
    tags=["User Information"],
    prefix="/user-informations",
)


@user_information_router.post("/", status_code=status.HTTP_201_CREATED)
def create_users_informations(
    current_user: Annotated[User, Depends(get_current_user)],
    user_information: UserInformationSchemaIn,
) -> UserInformation:
    with unit_api("Trying to create user information") as session:
        existing_user_information = USER_INFORMATION_SERVICE.get_or_none(
            session, user_id=current_user.id
        )
        if existing_user_information is not None:
            raise CannotCreateStillExistsException("User already has user information")

        item = UserInformation(
            name=user_information.name,
            first_name=user_information.first_name,
            email=user_information.email,
            user_id=current_user.id,
        )

        item = USER_INFORMATION_SERVICE.create(session, item)

        session.expunge(item)

    return item


@user_information_router.get("/", status_code=status.HTTP_200_OK)
def read_users_informations(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserInformationSchemaOut:
    with unit_api("Trying to read user informations") as session:
        user_informations = USER_INFORMATION_SERVICE.get_or_none(
            session, user_id=current_user.id
        )

        if user_informations is None:
            raise RessourceNotFoundException("User has no user informations")

        session.expunge(user_informations)

    return user_informations.to_decrypted()


@user_information_router.put("/", status_code=status.HTTP_200_OK)
def update_users_informations(
    current_user: Annotated[User, Depends(get_current_user)],
    user_information: UserInformationSchemaIn,
) -> UserInformationSchemaOut:
    with unit_api("Trying to update user informations") as session:
        user_informations = USER_INFORMATION_SERVICE.get_or_none(
            session, user_id=current_user.id
        )

        if user_informations is None:
            raise RessourceNotFoundException("User has no user informations")

        encrypted_informations = UserInformation(
            name=user_information.name,
            first_name=user_information.first_name,
            email=user_information.email,
        )

        new_user_informations = USER_INFORMATION_SERVICE.update(
            session,
            user_informations.id,
            encrypted_name=encrypted_informations.name,
            encrypted_first_name=encrypted_informations.first_name,
            encrypted_email=encrypted_informations.email,
        )

        session.expunge(new_user_informations)

        return new_user_informations.to_decrypted()


@user_information_router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_users_informations(
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    with unit_api("Trying to delete user informations") as session:
        user_informations = USER_INFORMATION_SERVICE.get_or_none(
            session, user_id=current_user.id
        )

        if user_informations is None:
            raise RessourceNotFoundException("User has no user informations")

        USER_INFORMATION_SERVICE.delete(session, user_informations.id)

    return None
