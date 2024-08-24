from pydantic import BaseModel

from app.api.list_link.models import SchoolRelation, UserOnListStatus


class LinkListSchemaIn(BaseModel):
    list_id: int
    user_id: int
    school_id: int


class LinkListSchemaOut(BaseModel):
    id: int
    list_id: int
    user_id: int
    school_id: int
    is_admin: bool
    status: UserOnListStatus
    school_relation: SchoolRelation
