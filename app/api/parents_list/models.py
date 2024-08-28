from typing import Optional

from pydantic import field_validator
from sqlalchemy import Column, ForeignKey, Integer, select
from sqlmodel import Field, Session

from app.commun.validator import validate_string
from app.database.model_base import BaseSQLModel
from app.database.repository import Repository


class ParentsList(BaseSQLModel, table=True):
    __tablename__ = "parents_lists"

    id: Optional[int] = Field(default=None, primary_key=True)
    list_name: str = Field(unique=True)
    holder_length: int = Field(ge=1, le=15)
    school_id: int = Field(
        sa_column=Column(Integer, ForeignKey("schools.id", ondelete="CASCADE"))
    )
    creator_id: int = Field(
        sa_column=Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    )

    @field_validator("list_name")
    def list_name_format(cls, value: str) -> str:
        return validate_string(value)


class ParentsListService(Repository[ParentsList]):
    __model__ = ParentsList

    def get_all_by_school_id(
        self, session: Session, school_id: int
    ) -> list[ParentsList]:
        statement = select(ParentsList).where(ParentsList.school_id == school_id)

        return [item[0] for item in session.exec(statement).all()]


PARENTS_LIST_SERVICE = ParentsListService()
