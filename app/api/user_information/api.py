from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.user_information.models import USER_INFORMATION_SERVICE, UserInformation
from app.api.user_information.schema import UserInformationSchemaIn
from app.auth.models import User
from app.auth.token import get_current_user
from app.database.unit_of_work import unit_api
from app.exceptions import CannotCreateStillExistsException

user_information_router = APIRouter(
    tags=["User Information"],
    prefix="/user-informations",
)


@user_information_router.post("/", status_code=status.HTTP_201_CREATED)
def read_users_me(
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

        return item
