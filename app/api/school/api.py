from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.list_link.models import LIST_LINK_SERVICE
from app.api.school.models import SCHOOL_SERVICE, School
from app.api.school.schemas import SchoolSchemaIn
from app.auth.models import User
from app.auth.token import get_current_user
from app.database.unit_of_work import unit_api
from app.exceptions import RessourceNotFoundException

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


@school_router.get("/{school_id}")
def get_school(school_id: int) -> School:
    with unit_api("Trying to get school") as session:
        school = SCHOOL_SERVICE.get_or_none(session, id=school_id)
        if school is None:
            raise RessourceNotFoundException("School not found")

        session.expunge(school)

    return school


@school_router.post("/")
def create_school(
    current_user: Annotated[User, Depends(get_current_user)],
    payload: SchoolSchemaIn,
):
    """
    Create a school

    User must be logger in to create a school
    He have to be completly registered with informations and a link object
    """

    with unit_api("Trying to create school") as session:
        user_link = LIST_LINK_SERVICE.get_or_none(session, user_id=current_user.id)
        if user_link is None:
            raise RessourceNotFoundException("User has no link")

        school = School(
            school_name=payload.school_name,
            city=payload.city,
            zip_code=payload.zip_code,
            country=payload.country,
            adress=payload.adress,
            user_id=current_user.id,
        )

        created_school = SCHOOL_SERVICE.create(session, school)

        LIST_LINK_SERVICE.update(
            session,
            user_link.id,
            school_id=created_school.id,
            school_relation=payload.school_relation,
        )

        session.expunge(school)
