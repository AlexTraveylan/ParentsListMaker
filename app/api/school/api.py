import logging
from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

from app.api.links.models import (
    SCHOOL_LINK_SERVICE,
    SchoolLink,
    SchoolRelation,
)
from app.api.school.models import SCHOOL_SERVICE, School
from app.api.school.schemas import SchoolSchemaIn, SchoolSchemaMe, SchoolSchemaOut
from app.auth.models import User
from app.auth.token import (
    UserWithInformations,
    get_current_user,
    get_current_user_with_informations,
)
from app.database.unit_of_work import unit_api
from app.exceptions import CannotCreateStillExistsException, RessourceNotFoundException

logger = logging.getLogger(__name__)

school_router = APIRouter(
    tags=["School"],
    prefix="/schools",
)


@school_router.get("/me", status_code=status.HTTP_200_OK)
def get_school_of_user(
    current_user: Annotated[
        UserWithInformations, Depends(get_current_user_with_informations)
    ],
) -> list[SchoolSchemaMe]:
    with unit_api(
        "Tentative de récupération de l'établissement de l'utilisateur"
    ) as session:
        schools = []
        for school_id in current_user.school_ids:
            school = SCHOOL_SERVICE.get_or_none(session, id=school_id)
            if school is None:
                raise RessourceNotFoundException("Établissement non trouvé")

            school_link = SCHOOL_LINK_SERVICE.get_or_none(
                session, school_id=school_id, user_id=current_user.id
            )

            if school_link is None:
                raise RessourceNotFoundException(
                    "Lien entre établissement et utilisateur non trouvé"
                )

            school_with_relation = SchoolSchemaMe(
                id=school.id,
                school_name=school.school_name,
                city=school.city,
                zip_code=school.zip_code,
                country=school.country,
                adress=school.adress,
                school_relation=school_link.school_relation.value,
                code=school.code,
            )

            schools.append(school_with_relation)

    return schools


@school_router.get("/{school_code}", status_code=status.HTTP_200_OK)
def get_school_by_school_code(
    school_code: str = Annotated[str, Path(title="school_code")],
) -> SchoolSchemaOut:
    with unit_api("Tentative de récupération de l'établissement") as session:
        school = SCHOOL_SERVICE.get_or_none(session, code=school_code)
        if school is None:
            raise RessourceNotFoundException("Établissement non trouvé")

        decrypted_school = school.to_decrypted()

    return decrypted_school


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
            code=payload.code,
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


@school_router.get("/join/{school_code}", status_code=status.HTTP_200_OK)
def join_school(
    current_user: Annotated[User, Depends(get_current_user)],
    school_code: Annotated[str, Path(title="school_code")],
) -> SchoolSchemaOut:
    """
    Join a school

    User must be logger in to create a school.
    He must've a link object
    """
    with unit_api("Tentative de rejoindre un établissement") as session:
        school = SCHOOL_SERVICE.get_or_none(session, code=school_code)
        if school is None:
            raise RessourceNotFoundException("Établissement non trouvé")

        user_link = SCHOOL_LINK_SERVICE.get_or_none(
            session, user_id=current_user.id, school_id=school.id
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
