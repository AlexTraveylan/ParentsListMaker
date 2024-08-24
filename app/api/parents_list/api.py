from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

from app.api.list_link.models import LIST_LINK_SERVICE, ListLink, UserOnListStatus
from app.api.parents_list.models import PARENTS_LIST_SERVICE, ParentsList
from app.api.parents_list.schema import ParentsListSchema
from app.auth.models import USER_SERVICE, User
from app.auth.token import (
    UserWithInformations,
    get_current_user,
    get_current_user_link,
    get_current_user_with_informations,
)
from app.database.unit_of_work import unit_api
from app.exceptions import (
    RessourceNotFoundException,
    UnauthorizedException,
)

parents_list_router = APIRouter(
    tags=["Parents Lists"],
    prefix="/parents-lists",
)


@parents_list_router.post("/", status_code=status.HTTP_201_CREATED)
def create_parents_list(
    current_user: Annotated[
        UserWithInformations, Depends(get_current_user_with_informations)
    ],
    payload: ParentsListSchema,
) -> ParentsListSchema:
    with unit_api("Tentative de création d'une liste de parents") as session:
        if current_user.email is None:
            raise RessourceNotFoundException(
                "Tu ne peux pas créer une liste de parents sans email confirmé"
            )

        new_parent_list = ParentsList(
            list_name=payload.list_name,
            holder_length=payload.holder_length,
            school_id=payload.school_id,
        )
        new_parent_list = PARENTS_LIST_SERVICE.create(session, new_parent_list)

        existing_link = LIST_LINK_SERVICE.get_or_none(session, user_id=current_user.id)

        if existing_link is None:
            raise RessourceNotFoundException("Tu n'as pas renseigné ton école")

        if existing_link.list_id is not None:
            raise RessourceNotFoundException(
                "Tu ne peux pas créer une liste de parents si tu es déjà membre d'une, quitte la liste d'abord"
            )

        LIST_LINK_SERVICE.update(
            session,
            existing_link.id,
            list_id=new_parent_list.id,
            is_admin=True,
            status=UserOnListStatus.LEADER,
        )

        session.expunge(new_parent_list)

    return new_parent_list


@parents_list_router.get("/join/{list_id}", status_code=status.HTTP_200_OK)
def ask_for_join_parents_list(
    current_user: Annotated[User, Depends(get_current_user)],
    list_id: int = Annotated[int, Path(title="list_id")],
) -> ListLink:
    with unit_api("Tentative d'ajout d'un membre à une liste de parents") as session:
        existing_parents_list = PARENTS_LIST_SERVICE.get_or_none(session, id=list_id)

        if existing_parents_list is None:
            raise RessourceNotFoundException("La liste de parents n'existe pas")

        existing_link = LIST_LINK_SERVICE.get_or_none(session, user_id=current_user.id)

        if existing_link is None:
            raise RessourceNotFoundException("Tu n'as pas rejoint d'école")

        if existing_link.list_id is not None:
            raise RessourceNotFoundException(
                "Tu ne peux pas rejoindre une autre liste de parents, quitte la liste actuelle d'abord"
            )

        updated_link = LIST_LINK_SERVICE.update(
            session,
            existing_link.id,
            list_id=existing_parents_list.id,
            is_admin=False,
            status=UserOnListStatus.WAITING,
        )

        session.expunge(updated_link)

    return updated_link


@parents_list_router.patch("/leave", status_code=status.HTTP_200_OK)
def leave_parents_list(
    user_link: Annotated[ListLink, Depends(get_current_user_link)],
) -> ListLink:
    with unit_api("Tentative de quitter une liste de parents") as session:
        LIST_LINK_SERVICE.update(
            session,
            user_link.id,
            is_admin=None,
            list_id=None,
            status=None,
        )

        session.expunge(user_link)

    return user_link


@parents_list_router.patch("/accept/{user_id}", status_code=status.HTTP_200_OK)
def accept_parents_list(
    request_user_link: Annotated[ListLink, Depends(get_current_user_link)],
    user_id: int = Annotated[int, Path(title="user_id")],
) -> ListLink:
    with unit_api(f"Tentative d'accepter l'utilisateur {user_id}") as session:
        if request_user_link.is_admin is False:
            raise UnauthorizedException(
                "Tu dois être admin de la liste pour cette action"
            )

        user_to_accept = USER_SERVICE.get_or_none(session, id=user_id)
        if user_to_accept is None:
            raise RessourceNotFoundException("L'utilisateur n'existe pas")

        user_to_accept_link = LIST_LINK_SERVICE.get_or_none(session, user_id=user_id)
        if user_to_accept_link is None:
            raise RessourceNotFoundException(
                "L'utilisateur n'a pas demander à rejoindre une liste"
            )

        if user_to_accept_link.list_id != request_user_link.list_id:
            raise UnauthorizedException(
                "L'utilisateur n'a pas demander à rejoindre ta liste"
            )

        if user_to_accept_link.status is not UserOnListStatus.WAITING:
            raise UnauthorizedException("L'utilisateur n'est pas en attente")

        parent_list = PARENTS_LIST_SERVICE.get_or_none(
            session, id=user_to_accept_link.list_id
        )
        if parent_list is None:
            raise RessourceNotFoundException("Ta liste n'existe pas")

        nb_holders = LIST_LINK_SERVICE.get_number_of_holders(
            session, user_to_accept_link.list_id
        )
        nb_substitutes = LIST_LINK_SERVICE.get_number_of_substitutes(
            session, user_to_accept_link.list_id
        )

        if nb_holders + nb_substitutes >= parent_list.holder_length * 2:
            raise RessourceNotFoundException("La liste est pleine")

        if nb_holders >= parent_list.holder_length:
            LIST_LINK_SERVICE.update(
                session,
                user_to_accept_link.id,
                is_admin=False,
                status=UserOnListStatus.HOLDER,
            )
        else:
            LIST_LINK_SERVICE.update(
                session,
                user_to_accept_link.id,
                is_admin=False,
                status=UserOnListStatus.SUBSTITUTE,
            )

        session.expunge(user_to_accept_link)

    return user_to_accept_link


@parents_list_router.patch("/reject/{user_id}", status_code=status.HTTP_200_OK)
def reject_parents_list(
    user_link: Annotated[ListLink, Depends(get_current_user_link)],
    user_id: int = Annotated[int, Path(title="user_id")],
) -> ListLink:
    with unit_api("Tentative de rejeter l'utilisateur {user_id}") as session:
        if user_link.is_admin is False:
            raise UnauthorizedException(
                "Tu dois être admin de la liste pour cette action"
            )

        user_to_reject = USER_SERVICE.get_or_none(session, id=user_id)
        if user_to_reject is None:
            raise RessourceNotFoundException("L'utilisateur n'existe pas")

        user_to_reject_link = LIST_LINK_SERVICE.get_or_none(session, user_id=user_id)
        if user_to_reject_link is None:
            raise RessourceNotFoundException(
                "L'utilisateur n'a pas demandé à rejoindre de liste"
            )

        if user_to_reject_link.list_id != user_link.list_id:
            raise UnauthorizedException(
                "L'utilisateur n'essaie pas de rejoindre ta liste"
            )

        if user_to_reject_link.status is not UserOnListStatus.WAITING:
            raise UnauthorizedException("L'utilisateur n'est pas en attente")

        LIST_LINK_SERVICE.update(
            session,
            user_to_reject_link.id,
            is_admin=None,
            list_id=None,
            status=None,
        )

        session.expunge(user_to_reject_link)

    return user_to_reject_link
