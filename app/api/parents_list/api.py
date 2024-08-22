from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.api.list_link.models import LIST_LINK_SERVICE, ListLink, UserOnListStatus
from app.api.parents_list.models import PARENTS_LIST_SERVICE, ParentsList
from app.api.parents_list.schema import ParentsListSchema
from app.auth.models import User
from app.auth.token import get_current_user
from app.database.unit_of_work import unit_api
from app.exceptions import CannotCreateStillExistsException, RessourceNotFoundException

parents_list_router = APIRouter(
    tags=["Parents Lists"],
    prefix="/parents-lists",
)


@parents_list_router.post("/", status_code=status.HTTP_201_CREATED)
def create_parents_list(
    current_user: Annotated[User, Depends(get_current_user)],
    parents_list: ParentsListSchema,
) -> ParentsListSchema:
    with unit_api("Trying to create parents list") as session:
        existing_parents_list = PARENTS_LIST_SERVICE.get_or_none(
            session, list_name=parents_list.list_name
        )

        if existing_parents_list is not None:
            raise CannotCreateStillExistsException("Parents list already exists")

        new_parent_list = ParentsList(list_name=parents_list.list_name)

        new_parent_list = PARENTS_LIST_SERVICE.create(session, new_parent_list)

        existing_link = LIST_LINK_SERVICE.get_or_none(session, user_id=current_user.id)

        if existing_link is not None:
            raise CannotCreateStillExistsException(
                "You can't create a parents list if you're already a member of one, leave it first"
            )

        new_link = ListLink(
            list_id=new_parent_list.id,
            user_id=current_user.id,
            is_admin=True,
            status=UserOnListStatus.LEADER,
        )

        LIST_LINK_SERVICE.create(session, new_link)

        session.expunge(new_parent_list)

    return new_parent_list


@parents_list_router.get("/", status_code=status.HTTP_200_OK)
def ask_for_join_parents_list(
    current_user: Annotated[User, Depends(get_current_user)],
    list_name: str,
) -> ListLink:
    with unit_api("Trying to ask for join parents list") as session:
        existing_parents_list = PARENTS_LIST_SERVICE.get_or_none(
            session, list_name=list_name
        )

        if existing_parents_list is None:
            raise RessourceNotFoundException("Parents list doesn't exist")

        existing_link = LIST_LINK_SERVICE.get_or_none(session, user_id=current_user.id)

        if existing_link is None:
            raise CannotCreateStillExistsException(
                "You can't join an other parents list, leaver the current one first"
            )

        new_link = ListLink(
            list_id=existing_parents_list.id,
            user_id=current_user.id,
            is_admin=False,
            status=UserOnListStatus.WAITING,
        )

        LIST_LINK_SERVICE.create(session, new_link)

        session.expunge(new_link)

    return new_link
