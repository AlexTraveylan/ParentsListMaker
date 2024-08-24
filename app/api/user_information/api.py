from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.user_information.models import USER_INFORMATION_SERVICE, UserInformation
from app.api.user_information.schema import (
    UserInformationSchemaIn,
    UserInformationSchemaOut,
)
from app.auth.models import User
from app.auth.token import get_current_user
from app.commun.crypto import generate_confirmation_token
from app.database.unit_of_work import unit_api
from app.emailmanager.models import (
    EMAIL_CONFIRMATION_TOKEN_SERVICE,
    EmailConfirmationToken,
)
from app.emailmanager.send_email import (
    html_wrapper_for_confirmation_email_with_token,
    send_contact_message,
)
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

        if item.email is not None:
            token = generate_confirmation_token()
            email_confirmation_token = EmailConfirmationToken(
                token=token,
                user_id=current_user.id,
            )
            EMAIL_CONFIRMATION_TOKEN_SERVICE.create(session, email_confirmation_token)
            html = html_wrapper_for_confirmation_email_with_token(token)
            send_contact_message("Confirmez votre email", html, to=item.email)

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
