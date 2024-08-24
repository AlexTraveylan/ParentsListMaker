from pydantic import BaseModel


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
    status: str
    school_relation: str
