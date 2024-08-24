from enum import Enum
from typing import Optional

from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field

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
    # List informations
    list_id: int = Field(
        sa_column=Column(Integer, ForeignKey("parents_lists.id", ondelete="CASCADE"))
    )
    is_admin: bool
    status: UserOnListStatus
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


LIST_LINK_SERVICE = ListLinkService()
