from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.list_link.models import LIST_LINK_SERVICE, ListLink
from app.api.school.models import SCHOOL_SERVICE, School
from app.api.school.schemas import SchoolSchemaIn
from app.auth.models import User
from app.auth.token import get_current_user
from app.database.unit_of_work import unit_api
from app.exceptions import CannotCreateStillExistsException

school_router = APIRouter(
    tags=["School"],
    prefix="/schools",
)


@school_router.get("/")
def get_all_schools() -> list[School]:
    with unit_api("Trying to get all schools") as session:
        schools = SCHOOL_SERVICE.get_all(session)
        session.expunge(schools)

    return schools


@school_router.post("/")
def create_school(
    current_user: Annotated[User, Depends(get_current_user)],
    payload: SchoolSchemaIn,
):
    """
    Create a school

    User must be logger in to create a school.
    He must've a link object
    """

    with unit_api("Trying to create school") as session:
        user_link = LIST_LINK_SERVICE.get_or_none(session, user_id=current_user.id)
        if user_link is not None:
            raise CannotCreateStillExistsException("User has no link")

        school = School(
            school_name=payload.school_name,
            city=payload.city,
            zip_code=payload.zip_code,
            country=payload.country,
            adress=payload.adress,
            user_id=current_user.id,
        )

        created_school = SCHOOL_SERVICE.create(session, school)

        list_link = ListLink(
            user_id=current_user.id,
            school_id=created_school.id,
            school_relation=payload.school_relation,
        )

        LIST_LINK_SERVICE.create(session, list_link)

        session.expunge(created_school)

    return created_school
