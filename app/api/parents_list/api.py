from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, status
from pydantic import BaseModel, Field

from app.api.links.models import (
    LIST_LINK_SERVICE,
    SCHOOL_LINK_SERVICE,
    ListLink,
    SchoolRelation,
    UserOnListStatus,
)
from app.api.parents_list.models import PARENTS_LIST_SERVICE, ParentsList
from app.api.parents_list.schema import ParentsListSchemaIn, ParentsListSchemaOut
from app.api.school.models import SCHOOL_SERVICE
from app.api.user_information.models import USER_INFORMATION_SERVICE
from app.auth.models import USER_SERVICE, User
from app.auth.token import (
    UserWithInformations,
    get_current_user,
    get_current_user_with_informations,
)
from app.database.unit_of_work import unit_api
from app.emailmanager.send_email import (
    html_wrapper_for_join_request_notification,
    send_contact_message,
)
from app.exceptions import (
    RessourceNotFoundException,
    UnauthorizedException,
)

parents_list_router = APIRouter(
    tags=["Parents Lists"],
    prefix="/parents-lists",
)


@parents_list_router.get("/{school_code}", status_code=status.HTTP_200_OK)
def get_parents_lists_by_school_code(
    school_code: str = Annotated[str, Path(title="school_code")],
) -> list[ParentsList]:
    with unit_api(
        "Tentative de récupération de toutes les listes de l'école spécifiée"
    ) as session:
        school = SCHOOL_SERVICE.get_or_none(session, code=school_code)
        if school is None:
            raise RessourceNotFoundException("Établissement non trouvé")

        parents_lists = PARENTS_LIST_SERVICE.get_all_by_school_id(session, school.id)

        session.expunge_all()

    return parents_lists


@parents_list_router.post("/", status_code=status.HTTP_201_CREATED)
def create_parents_list(
    current_user: Annotated[
        UserWithInformations, Depends(get_current_user_with_informations)
    ],
    payload: ParentsListSchemaIn,
) -> ParentsListSchemaOut:
    with unit_api("Tentative de création d'une liste de parents") as session:
        if current_user.email is None or not current_user.is_email_confirmed:
            raise RessourceNotFoundException(
                "Tu ne peux pas créer une liste de parents sans email confirmé"
            )

        school = SCHOOL_SERVICE.get_or_none(session, code=payload.school_code)
        if school is None:
            raise RessourceNotFoundException("Impossible de trouver l'école")

        school_link = SCHOOL_LINK_SERVICE.get_or_none(
            session, school_id=school.id, user_id=current_user.id
        )

        if school_link is None:
            raise RessourceNotFoundException(
                "Lien entre établissement et utilisateur non trouvé"
            )

        if school_link.school_relation == SchoolRelation.DIRECTION:
            raise UnauthorizedException(
                "La direction ne peut pas créer de liste de parents"
            )

        new_parent_list = ParentsList(
            list_name=payload.list_name,
            holder_length=payload.holder_length,
            school_id=school.id,
            creator_id=current_user.id,
        )
        new_parent_list = PARENTS_LIST_SERVICE.create(session, new_parent_list)

        list_link = ListLink(
            status=UserOnListStatus.ACCEPTED,
            position_in_list=1,
            is_admin=True,
            list_id=new_parent_list.id,
            user_id=current_user.id,
        )

        LIST_LINK_SERVICE.create(session, list_link)

        session.expunge(new_parent_list)

    return new_parent_list


class Message(BaseModel):
    message: str = Field(min_length=1, max_length=1000)


@parents_list_router.post("/join/{list_id}", status_code=status.HTTP_200_OK)
def ask_for_join_parents_list(
    current_user: Annotated[
        UserWithInformations, Depends(get_current_user_with_informations)
    ],
    list_id: int = Annotated[int, Path(title="list_id")],
    payload: Message = Annotated[Message, Body(embed=True)],
) -> ListLink:
    with unit_api("Tentative d'ajout d'un membre à une liste de parents") as session:
        list_to_join = PARENTS_LIST_SERVICE.get_or_none(session, id=list_id)
        if list_to_join is None:
            raise RessourceNotFoundException("La liste de parents n'existe pas")

        if list_to_join.id in current_user.parents_list_ids:
            raise RessourceNotFoundException("Tu as déjà rejoint cette liste")

        school = SCHOOL_SERVICE.get_or_none(session, id=list_to_join.school_id)
        if school is None:
            raise RessourceNotFoundException("Impossible de trouver l'école")

        if school.id not in current_user.school_ids:
            raise RessourceNotFoundException("Tu ne fais pas partie de cette école")

        new_list_link = ListLink(
            status=UserOnListStatus.WAITING,
            position_in_list=0,  # 0 means in waiting position
            is_admin=False,
            list_id=list_to_join.id,
            user_id=current_user.id,
        )

        new_list_link_created = LIST_LINK_SERVICE.create(session, new_list_link)

        session.expunge(new_list_link_created)

        creator_user_info = USER_INFORMATION_SERVICE.get_or_none(
            session,
            id=list_to_join.creator_id,
        )
        if creator_user_info is None:
            raise RessourceNotFoundException(
                "Impossible de trouver le créateur de la liste"
            )

        if creator_user_info.email is None or not creator_user_info.is_email_confirmed:
            raise RessourceNotFoundException(
                "Le créateur de la liste n'a pas confirmé son email"
            )

        html = html_wrapper_for_join_request_notification(
            username=current_user.username,
            list_name=list_to_join.list_name,
            message=payload.message,
        )
        send_contact_message(
            f"ParentsListMaker - {current_user.username} a demandé à rejoindre votre liste",
            html,
            to=creator_user_info.email,
        )

    return new_list_link_created


@parents_list_router.delete("/leave/{list_id}", status_code=status.HTTP_204_NO_CONTENT)
def leave_parents_list(
    current_user: Annotated[User, Depends(get_current_user)],
    list_id: int = Annotated[int, Path(title="list_id")],
) -> None:
    with unit_api("Tentative de quitter une liste de parents") as session:
        requested_user_link = LIST_LINK_SERVICE.get_or_none(
            session,
            user_id=current_user.id,
            list_id=list_id,
        )

        parent_list = PARENTS_LIST_SERVICE.get_or_none(session, id=list_id)
        if parent_list is None:
            raise RessourceNotFoundException("La liste de parents n'existe pas")

        if parent_list.creator_id == current_user.id:
            raise RessourceNotFoundException(
                "Tu ne peux pas quitter la liste de parents que tu as créée, contacte un administrateur"
            )

        if requested_user_link is None:
            raise RessourceNotFoundException("Tu n'as pas rejoint cette liste")

        LIST_LINK_SERVICE.delete(session, requested_user_link.id)


@parents_list_router.patch(
    "/accept/{user_id}/{list_id}", status_code=status.HTTP_200_OK
)
def accept_parents_list(
    admin_user: Annotated[
        UserWithInformations, Depends(get_current_user_with_informations)
    ],
    user_id: int = Annotated[int, Path(title="user_id")],
    list_id: int = Annotated[int, Path(title="list_id")],
) -> ListLink:
    with unit_api(f"Tentative d'accepter l'utilisateur {user_id}") as session:
        list_to_join = PARENTS_LIST_SERVICE.get_or_none(session, id=list_id)
        if list_to_join is None:
            raise RessourceNotFoundException("La liste n'existe pas")

        admin_user_list_link = LIST_LINK_SERVICE.get_or_none(
            session,
            user_id=admin_user.id,
            list_id=list_to_join.id,
        )
        if admin_user_list_link is None:
            raise RessourceNotFoundException("Tu n'as pas rejoint cette liste")

        if admin_user_list_link.is_admin is False:
            raise UnauthorizedException("Tu n'est pas admin de cette liste")

        user_to_accept = USER_SERVICE.get_or_none(session, id=user_id)
        if user_to_accept is None:
            raise RessourceNotFoundException("L'utilisateur n'existe pas")

        user_to_accept_list_link = LIST_LINK_SERVICE.get_or_none(
            session,
            user_id=user_to_accept.id,
            list_id=list_to_join.id,
        )
        if user_to_accept_list_link is None:
            raise RessourceNotFoundException(
                "L'utilisateur n'a pas demandé à rejoindre cette liste"
            )

        list_links = LIST_LINK_SERVICE.get_all_list_links_by_list_id(
            session, list_to_join.id
        )

        nb_members = len(
            list(filter(lambda x: x.status == UserOnListStatus.ACCEPTED, list_links))
        )

        new_list_link = LIST_LINK_SERVICE.update(
            session,
            user_to_accept_list_link.id,
            is_admin=False,
            status=UserOnListStatus.ACCEPTED,
            position_in_list=nb_members + 1,
        )

        session.expunge(new_list_link)

    return new_list_link
