from typing import Literal

from pydantic import BaseModel


class SchoolSchemaIn(BaseModel):
    school_name: str
    city: str
    zip_code: str
    country: str
    adress: str
    school_relation: Literal["parent", "direction"]
    code: str


class SchoolSchemaOut(BaseModel):
    id: int
    school_name: str
    city: str
    zip_code: str
    country: str
    adress: str


class SchoolSchemaMe(BaseModel):
    id: int
    school_name: str
    city: str
    zip_code: str
    country: str
    adress: str
    school_relation: Literal["parent", "direction"]
    code: str
