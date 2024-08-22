from typing import Optional

from pydantic import field_validator
from sqlmodel import Field

from app.commun.validator import validate_string
from app.database.model_base import BaseSQLModel
from app.database.repository import Repository


class ParentsList(BaseSQLModel, table=True):
    __tablename__ = "parents_lists"

    id: Optional[int] = Field(default=None, primary_key=True)
    list_name: str = Field(unique=True)
    holder_length: int = Field(ge=1, le=15)

    @field_validator("list_name")
    def list_name_format(cls, value: str) -> str:
        return validate_string(value)


class ParentsListService(Repository[ParentsList]):
    __model__ = ParentsList


PARENTS_LIST_SERVICE = ParentsListService()
