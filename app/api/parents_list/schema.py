from pydantic import BaseModel


class ParentsListSchemaOut(BaseModel):
    list_name: str
    holder_length: int
    school_id: int


class ParentsListSchemaIn(BaseModel):
    list_name: str
    holder_length: int
    school_code: str
