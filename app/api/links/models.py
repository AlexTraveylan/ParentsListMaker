from enum import Enum
from typing import Optional

from sqlalchemy import Column, ForeignKey, Integer, select
from sqlmodel import Field, Session

from app.api.school.models import *  # Be sure import School before ListLink
from app.database.model_base import BaseSQLModel
from app.database.repository import Repository


class UserOnListStatus(Enum):
    WAITING = "waiting"
    ACCEPTED = "accepted"


class SchoolRelation(Enum):
    DIRECTION = "direction"
    PARENT = "parent"


class ListLink(BaseSQLModel, table=True):
    __tablename__ = "list_links"

    id: Optional[int] = Field(default=None, primary_key=True)
    status: UserOnListStatus
    position_in_list: int  # 0 means in waiting position
    is_admin: bool = Field(default=False)
    list_id: int = Field(
        default=None,
        sa_column=Column(Integer, ForeignKey("parents_lists.id", ondelete="CASCADE")),
    )
    user_id: int = Field(
        sa_column=Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    )


class ListLinkService(Repository[ListLink]):
    __model__ = ListLink

    def get_all_list_links_by_user_id(
        self, session: Session, user_id: int
    ) -> list[ListLink]:
        statement = select(ListLink).where(ListLink.user_id == user_id)

        return [item[0] for item in session.exec(statement).all()]

    def get_all_list_links_by_list_id(
        self, session: Session, list_id: int
    ) -> list[ListLink]:
        statement = select(ListLink).where(ListLink.list_id == list_id)

        return [item[0] for item in session.exec(statement).all()]


class SchoolLink(BaseSQLModel, table=True):
    __tablename__ = "school_links"

    id: Optional[int] = Field(default=None, primary_key=True)
    school_id: int = Field(
        sa_column=Column(Integer, ForeignKey("schools.id", ondelete="CASCADE"))
    )
    user_id: int = Field(
        sa_column=Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    )
    school_relation: SchoolRelation


class SchoolLinkService(Repository[SchoolLink]):
    __model__ = SchoolLink

    def get_all_school_links_by_user_id(
        self, session: Session, user_id: int
    ) -> list[SchoolLink]:
        statement = select(SchoolLink).where(SchoolLink.user_id == user_id)

        return [item[0] for item in session.exec(statement).all()]


LIST_LINK_SERVICE = ListLinkService()
SCHOOL_LINK_SERVICE = SchoolLinkService()
