from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, status
from pydantic import BaseModel, Field

from app.api.user_information.models import USER_INFORMATION_SERVICE, UserInformation
from app.auth.token import UserWithInformations, get_current_user_with_informations
from app.commun.crypto import encrypt, generate_confirmation_token
from app.database.unit_of_work import unit_api
from app.emailmanager.models import (
    EMAIL_CONFIRMATION_TOKEN_SERVICE,
    EmailConfirmationToken,
)
from app.emailmanager.schema import EmailSchema
from app.emailmanager.send_email import (
    html_wrapper_for_introduction_email,
    send_contact_message,
)
from app.exceptions import RessourceNotFoundException, UnauthorizedException

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


class Message(BaseModel):
    message: str = Field(min_length=1, max_length=1000)


@email_router.post("/contact-user/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def contact_user(
    current_user: Annotated[
        UserWithInformations, Depends(get_current_user_with_informations)
    ],
    user_id: int = Annotated[int, Path(title="user_id")],
    payload: Message = Annotated[Message, Body(embed=True)],
) -> None:
    with unit_api("Tentative de contacter un utilisateur") as session:
        if current_user.email is None or not current_user.is_email_confirmed:
            raise RessourceNotFoundException(
                "Tu ne peux pas contacter un utilisateur sans email confirmé"
            )

        user_info = USER_INFORMATION_SERVICE.get_or_none(session, user_id=user_id)

        if user_info is None:
            raise RessourceNotFoundException("L'utilisateur n'existe pas")

        if user_info.email is None or not user_info.is_email_confirmed:
            raise RessourceNotFoundException(
                "L'utilisateur cible n'a pas confirmé son email"
            )

        html = html_wrapper_for_introduction_email(current_user.email, payload.message)
        send_contact_message(
            subject="ParentsListMaker - Demande de contact",
            html=html,
            to=user_info.email,
        )
