from enum import Enum
from typing import Optional

from sqlalchemy import Column, ForeignKey, Integer
from sqlmodel import Field

from app.database.model_base import BaseSQLModel
from app.database.repository import Repository


class UserOnListStatus(Enum, str):
    WAITING = "waiting"
    LEADER = "leader"
    HOLDER = "holder"
    SUBSTITUTE = "substitute"
    REJECTED = "rejected"


class ListLink(BaseSQLModel, table=True):
    __tablename__ = "list_links"

    id: Optional[int] = Field(default=None, primary_key=True)
    list_id: int = Field(
        sa_column=Column(Integer, ForeignKey("parents_lists.id", ondelete="CASCADE"))
    )
    user_id: int = Field(
        sa_column=Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    )
    is_admin: bool
    status: UserOnListStatus


class ListLinkService(Repository[ListLink]):
    __model__ = ListLink


LIST_LINK_SERVICE = ListLinkService()
