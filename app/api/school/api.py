import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.links.models import (
    SCHOOL_LINK_SERVICE,
    SchoolLink,
    SchoolRelation,
)
from app.api.school.models import SCHOOL_SERVICE, School
from app.api.school.schemas import SchoolSchemaIn, SchoolSchemaOut
from app.auth.models import User
from app.auth.token import get_current_user
from app.database.unit_of_work import unit_api
from app.exceptions import CannotCreateStillExistsException, RessourceNotFoundException

logger = logging.getLogger(__name__)

school_router = APIRouter(
    tags=["School"],
    prefix="/schools",
)


@school_router.get("/", status_code=status.HTTP_200_OK)
def get_all_schools() -> list[School]:
    with unit_api("Tentative de récupération de tous les établissements") as session:
        schools = SCHOOL_SERVICE.get_all(session)
        session.expunge(schools)

    return schools


@school_router.post("/", status_code=status.HTTP_201_CREATED)
def create_school(
    current_user: Annotated[User, Depends(get_current_user)],
    payload: SchoolSchemaIn,
) -> SchoolSchemaOut:
    """
    Create a school

    User must be logger in to create a school.
    He must've a link object
    """

    with unit_api("Tentative de création d'établissement") as session:
        school = School(
            school_name=payload.school_name,
            city=payload.city,
            zip_code=payload.zip_code,
            country=payload.country,
            adress=payload.adress,
            user_id=current_user.id,
        )

        created_school = SCHOOL_SERVICE.create(session, school)

        school_link = SchoolLink(
            school_id=created_school.id,
            user_id=current_user.id,
            school_relation=payload.school_relation,
        )

        SCHOOL_LINK_SERVICE.create(session, school_link)

        session.expunge(created_school)

    logger.info(
        f"{current_user.username} (id: {current_user.id}) a créé l'établissement {created_school.school_name} (id: {created_school.id})"
    )

    return created_school.to_decrypted()


@school_router.get("/join/{school_id}", status_code=status.HTTP_200_OK)
def join_school(
    current_user: Annotated[User, Depends(get_current_user)],
    school_id: int,
) -> SchoolSchemaOut:
    """
    Join a school

    User must be logger in to create a school.
    He must've a link object
    """
    with unit_api("Tentative de rejoindre un établissement") as session:
        school = SCHOOL_SERVICE.get_or_none(session, id=school_id)
        if school is None:
            raise RessourceNotFoundException("Établissement non trouvé")

        user_link = SCHOOL_LINK_SERVICE.get_or_none(
            session, user_id=current_user.id, school_id=school_id
        )
        if user_link is not None:
            raise CannotCreateStillExistsException("L'utilisateur est déjà membre")

        school_link = SchoolLink(
            school_id=school.id,
            user_id=current_user.id,
            school_relation=SchoolRelation.PARENT,
        )

        SCHOOL_LINK_SERVICE.create(session, school_link)

        session.expunge(school)

    return school.to_decrypted()


@school_router.delete("/leave/{school_id}", status_code=status.HTTP_204_NO_CONTENT)
def leave_school(
    current_user: Annotated[User, Depends(get_current_user)],
    school_id: int,
) -> None:
    with unit_api("Tentative de quitter un établissement") as session:
        school = SCHOOL_SERVICE.get_or_none(session, id=school_id)
        if school is None:
            raise RessourceNotFoundException("Établissement non trouvé")

        school_link = SCHOOL_LINK_SERVICE.get_or_none(
            session, user_id=current_user.id, school_id=school_id
        )
        if school_link is None:
            raise RessourceNotFoundException("L'utilisateur n'est pas membre")

        SCHOOL_LINK_SERVICE.delete(session, school_link.id)
