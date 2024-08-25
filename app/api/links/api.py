from typing import Annotated

from fastapi import APIRouter, Depends, Path, status

from app.api.links.models import LIST_LINK_SERVICE
from app.api.parents_list.models import PARENTS_LIST_SERVICE
from app.auth.token import UserWithInformations, get_current_user_with_informations
from app.database.unit_of_work import unit_api
from app.exceptions import RessourceNotFoundException, UnauthorizedException

links_api = APIRouter(
    tags=["links"],
    prefix="/links",
)


@links_api.patch("/up/{list_id}/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def up_parent_position(
    admin_user: Annotated[
        UserWithInformations, Depends(get_current_user_with_informations)
    ],
    list_id: int = Annotated[int, Path(title="list_id")],
    user_id: int = Annotated[int, Path(title="user_id")],
) -> None:
    with unit_api("Tentative de changer la position d'un membre") as session:
        parent_list = PARENTS_LIST_SERVICE.get_or_none(session, id=list_id)
        if parent_list is None:
            raise RessourceNotFoundException("La liste non trouvée")

        if parent_list.id not in admin_user.parents_list_ids:
            raise UnauthorizedException("Tu n'as pas accès à cette liste")

        admin_user_list_link = LIST_LINK_SERVICE.get_or_none(
            session,
            user_id=admin_user.id,
            list_id=parent_list.id,
        )

        if admin_user_list_link.is_admin is False:
            raise UnauthorizedException("Tu n'es pas admin de cette liste")

        user_to_change_position = LIST_LINK_SERVICE.get_or_none(
            session,
            user_id=user_id,
            list_id=parent_list.id,
        )

        if user_to_change_position is None:
            raise RessourceNotFoundException("L'utilisateur n'existe pas")

        all_list_links = LIST_LINK_SERVICE.get_all_list_links_by_list_id(
            session, parent_list.id
        )

        min_position = 1
        max_position = len(all_list_links)

        if (
            min_position >= user_to_change_position.position_in_list
            or max_position < user_to_change_position.position_in_list
        ):
            raise RessourceNotFoundException("Position invalide")

        parent_to_toogle = LIST_LINK_SERVICE.get_or_none(
            session,
            list_id=parent_list.id,
            position_in_list=user_to_change_position.position_in_list - 1,
        )

        if parent_to_toogle is None:
            raise RessourceNotFoundException("Parent non trouvé")

        LIST_LINK_SERVICE.update(
            session,
            user_to_change_position.id,
            position_in_list=user_to_change_position.position_in_list - 1,
        )

        LIST_LINK_SERVICE.update(
            session,
            parent_to_toogle.id,
            position_in_list=user_to_change_position.position_in_list,
        )


@links_api.patch("/down/{list_id}/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def down_parent_position(
    admin_user: Annotated[
        UserWithInformations, Depends(get_current_user_with_informations)
    ],
    list_id: int = Annotated[int, Path(title="list_id")],
    user_id: int = Annotated[int, Path(title="user_id")],
) -> None:
    with unit_api("Tentative de changer la position d'un membre") as session:
        parent_list = PARENTS_LIST_SERVICE.get_or_none(session, id=list_id)
        if parent_list is None:
            raise RessourceNotFoundException("La liste non trouvée")

        if parent_list.id not in admin_user.parents_list_ids:
            raise UnauthorizedException("Tu n'as pas accès à cette liste")

        admin_user_list_link = LIST_LINK_SERVICE.get_or_none(
            session,
            user_id=admin_user.id,
            list_id=parent_list.id,
        )

        if admin_user_list_link.is_admin is False:
            raise UnauthorizedException("Tu n'es pas admin de cette liste")

        user_to_change_position = LIST_LINK_SERVICE.get_or_none(
            session,
            user_id=user_id,
            list_id=parent_list.id,
        )

        if user_to_change_position is None:
            raise RessourceNotFoundException("L'utilisateur n'existe pas")

        all_list_links = LIST_LINK_SERVICE.get_all_list_links_by_list_id(
            session, parent_list.id
        )

        min_position = 1
        max_position = len(all_list_links)

        if (
            min_position > user_to_change_position.position_in_list
            or max_position <= user_to_change_position.position_in_list
        ):
            raise RessourceNotFoundException("Position invalide")

        parent_to_toogle = LIST_LINK_SERVICE.get_or_none(
            session,
            list_id=parent_list.id,
            position_in_list=user_to_change_position.position_in_list + 1,
        )

        if parent_to_toogle is None:
            raise RessourceNotFoundException("Parent non trouvé")

        LIST_LINK_SERVICE.update(
            session,
            user_to_change_position.id,
            position_in_list=user_to_change_position.position_in_list + 1,
        )

        LIST_LINK_SERVICE.update(
            session,
            parent_to_toogle.id,
            position_in_list=user_to_change_position.position_in_list,
        )
