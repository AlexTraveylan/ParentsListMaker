from enum import Enum
from typing import Optional

from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field, Session, select

from app.api.school.models import *  # Be sure import School before ListLink
from app.database.model_base import BaseSQLModel
from app.database.repository import Repository


class UserOnListStatus(Enum):
    WAITING = "waiting"
    LEADER = "leader"
    HOLDER = "holder"
    SUBSTITUTE = "substitute"
    REJECTED = "rejected"


class SchoolRelation(Enum):
    DIRECTION = "direction"
    PARENT = "parent"


class ListLink(BaseSQLModel, table=True):
    __tablename__ = "list_links"

    id: Optional[int] = Field(default=None, primary_key=True)
    # List informations None if not linked to a list or Director
    list_id: Optional[int] = Field(
        default=None,
        sa_column=Column(Integer, ForeignKey("parents_lists.id", ondelete="SET NULL")),
    )
    is_admin: Optional[bool] = Field(default=None)
    status: Optional[UserOnListStatus] = Field(default=None)
    # User informations
    user_id: int = Field(
        sa_column=Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    )
    # School informations
    school_relation: SchoolRelation
    school_id: int = Field(
        sa_column=Column(Integer, ForeignKey("schools.id", ondelete="CASCADE"))
    )


class ListLinkService(Repository[ListLink]):
    __model__ = ListLink

    def get_number_of_holders(self, session: Session, list_id: int) -> int:
        nb_holders = session.exec(
            select(ListLink)
            .where(ListLink.list_id == list_id)
            .where(ListLink.status == UserOnListStatus.HOLDER)
        ).all()

        return len(nb_holders) + 1  # the Leader is also a holder

    def get_number_of_substitutes(self, session: Session, list_id: int) -> int:
        nb_substitutes = session.exec(
            select(ListLink)
            .where(ListLink.list_id == list_id)
            .where(ListLink.status == UserOnListStatus.SUBSTITUTE)
        ).all()

        return len(nb_substitutes)

    def get_leader_user_id_of_list(self, session: Session, list_id: int) -> int:
        leader_user_id = session.exec(
            select(ListLink)
            .where(ListLink.list_id == list_id)
            .where(ListLink.status == UserOnListStatus.LEADER)
        ).first()

        return leader_user_id.user_id


LIST_LINK_SERVICE = ListLinkService()
