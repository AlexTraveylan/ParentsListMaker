from typing import Annotated

from fastapi import APIRouter, Depends, Path

from app.api.user_information.models import USER_INFORMATION_SERVICE, UserInformation
from app.auth.token import UserWithInformations, get_current_user_with_informations
from app.commun.crypto import encrypt, generate_confirmation_token
from app.database.unit_of_work import unit_api
from app.emailmanager.models import (
    EMAIL_CONFIRMATION_TOKEN_SERVICE,
    EmailConfirmationToken,
)
from app.emailmanager.schema import EmailSchema
from app.exceptions import UnauthorizedException

email_router = APIRouter(
    tags=["Email"],
    prefix="/confirmation-email",
)


@email_router.post("/")
def add_email_to_user(
    current_user: Annotated[
        UserWithInformations, Depends(get_current_user_with_informations)
    ],
    payload: EmailSchema,
) -> EmailConfirmationToken:
    with unit_api("Trying to add email to user") as session:
        existing_user_information = USER_INFORMATION_SERVICE.get_or_none(
            session, user_id=current_user.id
        )

        if existing_user_information is None:
            raise UnauthorizedException("User has no informations")

        USER_INFORMATION_SERVICE.update(
            session,
            existing_user_information.id,
            encrypted_email=encrypt(payload.email),
            is_email_confirmed=False,
        )

        new_email_confirmation = EmailConfirmationToken(
            token=generate_confirmation_token(),
            user_id=current_user.id,
        )

        confirm_email_created = EMAIL_CONFIRMATION_TOKEN_SERVICE.create(
            session, new_email_confirmation
        )

        session.expunge(confirm_email_created)

    return confirm_email_created


@email_router.get("/{token}")
def confirm_email(token: Annotated[str, Path(title="token")]) -> UserInformation:
    with unit_api("Trying to confirm email") as session:
        email_confirmation = EMAIL_CONFIRMATION_TOKEN_SERVICE.get_or_none(
            session, token=token
        )

        if email_confirmation is None:
            raise UnauthorizedException("Token not found")

        if email_confirmation.is_confirmed is True:
            raise UnauthorizedException("Email already confirmed")

        EMAIL_CONFIRMATION_TOKEN_SERVICE.update(
            session, email_confirmation.id, is_confirmed=True
        )

        actual_information = USER_INFORMATION_SERVICE.get_or_none(
            session, user_id=email_confirmation.user_id
        )

        if actual_information is None:
            raise UnauthorizedException("User has no informations")

        user_information = USER_INFORMATION_SERVICE.update(
            session, actual_information.id, is_email_confirmed=True
        )

        session.expunge(user_information)

    return user_information
