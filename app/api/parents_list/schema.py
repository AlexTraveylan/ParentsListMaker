from pydantic import BaseModel


class ParentsListSchema(BaseModel):
    list_name: str
    holder_length: int
